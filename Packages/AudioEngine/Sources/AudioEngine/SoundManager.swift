import AVFoundation
import Combine

/// Manages sound effect and music playback for games.
///
/// SoundManager provides a simple API for playing audio with
/// support for volume control, looping, and preloading.
///
/// ## Usage
/// ```swift
/// // Play a sound effect
/// SoundManager.shared.playSound("explosion")
///
/// // Play background music
/// SoundManager.shared.playMusic("background_theme", loop: true)
///
/// // Preload sounds for instant playback
/// SoundManager.shared.preloadSounds(["jump", "coin", "hit"])
/// ```
@MainActor
public final class SoundManager: ObservableObject {
    // MARK: - Singleton

    /// Shared instance of the sound manager
    public static let shared = SoundManager()

    // MARK: - Published Properties

    /// Master volume (0.0 - 1.0)
    @Published public var masterVolume: Float = 1.0 {
        didSet { updateVolumes() }
    }

    /// Sound effects volume (0.0 - 1.0)
    @Published public var sfxVolume: Float = 1.0 {
        didSet { updateVolumes() }
    }

    /// Music volume (0.0 - 1.0)
    @Published public var musicVolume: Float = 0.7 {
        didSet { updateVolumes() }
    }

    /// Whether sound effects are enabled
    @Published public var isSfxEnabled: Bool = true

    /// Whether music is enabled
    @Published public var isMusicEnabled: Bool = true {
        didSet {
            if isMusicEnabled {
                musicPlayer?.play()
            } else {
                musicPlayer?.pause()
            }
        }
    }

    /// Currently playing music track name
    @Published public private(set) var currentMusicTrack: String?

    // MARK: - Private Properties

    private var soundPlayers: [String: [AVAudioPlayer]] = [:]
    private var musicPlayer: AVAudioPlayer?
    private var preloadedSounds: [String: AVAudioPlayer] = [:]

    private let maxConcurrentSounds = 10

    // MARK: - Initialization

    private init() {
        setupAudioSession()
    }

    private func setupAudioSession() {
        #if os(iOS) || os(tvOS)
        do {
            try AVAudioSession.sharedInstance().setCategory(
                .ambient,
                mode: .default,
                options: [.mixWithOthers]
            )
            try AVAudioSession.sharedInstance().setActive(true)
        } catch {
            print("Failed to setup audio session: \(error)")
        }
        #endif
    }

    // MARK: - Sound Effects

    /// Plays a sound effect
    /// - Parameters:
    ///   - name: The name of the sound file (without extension)
    ///   - volume: Volume override (0.0 - 1.0), uses sfxVolume if nil
    ///   - rate: Playback rate (0.5 - 2.0)
    ///   - pan: Stereo pan (-1.0 left to 1.0 right)
    @discardableResult
    public func playSound(
        _ name: String,
        volume: Float? = nil,
        rate: Float = 1.0,
        pan: Float = 0.0
    ) -> Bool {
        guard isSfxEnabled else { return false }

        // Try to use preloaded sound first
        if let preloaded = preloadedSounds[name] {
            let player = createPlayer(from: preloaded)
            return playSoundPlayer(player, name: name, volume: volume, rate: rate, pan: pan)
        }

        // Load and play
        guard let player = loadSound(name) else {
            print("Sound not found: \(name)")
            return false
        }

        return playSoundPlayer(player, name: name, volume: volume, rate: rate, pan: pan)
    }

    private func playSoundPlayer(
        _ player: AVAudioPlayer?,
        name: String,
        volume: Float?,
        rate: Float,
        pan: Float
    ) -> Bool {
        guard let player = player else { return false }

        let effectiveVolume = (volume ?? sfxVolume) * masterVolume
        player.volume = effectiveVolume
        player.enableRate = true
        player.rate = rate
        player.pan = pan
        player.numberOfLoops = 0

        // Manage concurrent sounds
        cleanupFinishedSounds(for: name)

        var players = soundPlayers[name] ?? []
        if players.count >= maxConcurrentSounds {
            players.first?.stop()
            players.removeFirst()
        }
        players.append(player)
        soundPlayers[name] = players

        return player.play()
    }

    /// Stops all instances of a sound effect
    public func stopSound(_ name: String) {
        soundPlayers[name]?.forEach { $0.stop() }
        soundPlayers[name]?.removeAll()
    }

    /// Stops all sound effects
    public func stopAllSounds() {
        soundPlayers.values.flatMap { $0 }.forEach { $0.stop() }
        soundPlayers.removeAll()
    }

    // MARK: - Music

    /// Plays background music
    /// - Parameters:
    ///   - name: The name of the music file (without extension)
    ///   - loop: Whether to loop the music
    ///   - fadeIn: Duration of fade-in effect (0 for instant)
    public func playMusic(_ name: String, loop: Bool = true, fadeIn: TimeInterval = 0) {
        guard isMusicEnabled else {
            currentMusicTrack = name
            return
        }

        // Stop current music
        if musicPlayer?.isPlaying == true {
            stopMusic(fadeOut: 0.3)
        }

        guard let player = loadSound(name) else {
            print("Music not found: \(name)")
            return
        }

        musicPlayer = player
        currentMusicTrack = name

        let targetVolume = musicVolume * masterVolume
        player.numberOfLoops = loop ? -1 : 0

        if fadeIn > 0 {
            player.volume = 0
            player.play()
            fadeVolume(player: player, to: targetVolume, duration: fadeIn)
        } else {
            player.volume = targetVolume
            player.play()
        }
    }

    /// Stops the background music
    /// - Parameter fadeOut: Duration of fade-out effect (0 for instant)
    public func stopMusic(fadeOut: TimeInterval = 0) {
        guard let player = musicPlayer else { return }

        if fadeOut > 0 {
            fadeVolume(player: player, to: 0, duration: fadeOut) {
                player.stop()
            }
        } else {
            player.stop()
        }

        currentMusicTrack = nil
    }

    /// Pauses the background music
    public func pauseMusic() {
        musicPlayer?.pause()
    }

    /// Resumes the background music
    public func resumeMusic() {
        guard isMusicEnabled else { return }
        musicPlayer?.play()
    }

    // MARK: - Preloading

    /// Preloads sounds for instant playback
    /// - Parameter names: Array of sound file names
    public func preloadSounds(_ names: [String]) {
        for name in names {
            if let player = loadSound(name) {
                player.prepareToPlay()
                preloadedSounds[name] = player
            }
        }
    }

    /// Clears preloaded sounds to free memory
    public func clearPreloadedSounds() {
        preloadedSounds.removeAll()
    }

    // MARK: - Private Helpers

    private func loadSound(_ name: String) -> AVAudioPlayer? {
        // Try common audio formats
        let extensions = ["mp3", "wav", "m4a", "aac", "caf"]

        for ext in extensions {
            if let url = Bundle.main.url(forResource: name, withExtension: ext) {
                do {
                    let player = try AVAudioPlayer(contentsOf: url)
                    player.prepareToPlay()
                    return player
                } catch {
                    print("Error loading sound \(name).\(ext): \(error)")
                }
            }
        }

        return nil
    }

    private func createPlayer(from template: AVAudioPlayer) -> AVAudioPlayer? {
        guard let url = template.url else { return nil }
        return try? AVAudioPlayer(contentsOf: url)
    }

    private func updateVolumes() {
        let effectiveMusicVolume = musicVolume * masterVolume
        musicPlayer?.volume = effectiveMusicVolume

        let effectiveSfxVolume = sfxVolume * masterVolume
        soundPlayers.values.flatMap { $0 }.forEach { $0.volume = effectiveSfxVolume }
    }

    private func cleanupFinishedSounds(for name: String) {
        soundPlayers[name]?.removeAll { !$0.isPlaying }
    }

    private func fadeVolume(
        player: AVAudioPlayer,
        to volume: Float,
        duration: TimeInterval,
        completion: (() -> Void)? = nil
    ) {
        let steps = 20
        let stepDuration = duration / Double(steps)
        let volumeStep = (volume - player.volume) / Float(steps)

        var currentStep = 0
        Timer.scheduledTimer(withTimeInterval: stepDuration, repeats: true) { timer in
            currentStep += 1
            player.volume += volumeStep

            if currentStep >= steps {
                timer.invalidate()
                player.volume = volume
                completion?()
            }
        }
    }
}

// MARK: - Convenience Extensions

public extension SoundManager {
    /// Plays a UI feedback sound (e.g., button tap)
    func playUISound(_ type: UISound) {
        playSound(type.rawValue, volume: 0.5)
    }

    /// Common UI sound types
    enum UISound: String {
        case tap = "ui_tap"
        case success = "ui_success"
        case error = "ui_error"
        case swoosh = "ui_swoosh"
        case coin = "coin"
        case powerUp = "power_up"
    }
}
