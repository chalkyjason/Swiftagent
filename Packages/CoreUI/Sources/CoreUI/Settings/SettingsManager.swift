import SwiftUI
import Combine

/// Manages persistent game settings with automatic UserDefaults storage.
///
/// SettingsManager provides a centralized, observable store for common
/// game settings with automatic persistence.
///
/// ## Usage
/// ```swift
/// @StateObject private var settings = SettingsManager.shared
///
/// var body: some View {
///     Slider(value: $settings.masterVolume)
///     Toggle("Haptics", isOn: $settings.hapticsEnabled)
/// }
/// ```
@MainActor
public final class SettingsManager: ObservableObject {
    // MARK: - Singleton

    /// Shared instance of the settings manager
    public static let shared = SettingsManager()

    // MARK: - Keys

    private enum Keys {
        static let masterVolume = "settings.masterVolume"
        static let musicVolume = "settings.musicVolume"
        static let sfxVolume = "settings.sfxVolume"
        static let hapticsEnabled = "settings.hapticsEnabled"
        static let notificationsEnabled = "settings.notificationsEnabled"
        static let soundEnabled = "settings.soundEnabled"
        static let musicEnabled = "settings.musicEnabled"
        static let difficulty = "settings.difficulty"
        static let language = "settings.language"
        static let showFPS = "settings.showFPS"
        static let reducedMotion = "settings.reducedMotion"
        static let colorBlindMode = "settings.colorBlindMode"
        static let tutorialCompleted = "settings.tutorialCompleted"
    }

    // MARK: - Audio Settings

    /// Master volume (0.0 - 1.0)
    @Published public var masterVolume: Double {
        didSet { save(masterVolume, forKey: Keys.masterVolume) }
    }

    /// Music volume (0.0 - 1.0)
    @Published public var musicVolume: Double {
        didSet { save(musicVolume, forKey: Keys.musicVolume) }
    }

    /// Sound effects volume (0.0 - 1.0)
    @Published public var sfxVolume: Double {
        didSet { save(sfxVolume, forKey: Keys.sfxVolume) }
    }

    /// Whether sound is enabled
    @Published public var soundEnabled: Bool {
        didSet { save(soundEnabled, forKey: Keys.soundEnabled) }
    }

    /// Whether music is enabled
    @Published public var musicEnabled: Bool {
        didSet { save(musicEnabled, forKey: Keys.musicEnabled) }
    }

    // MARK: - Feedback Settings

    /// Whether haptic feedback is enabled
    @Published public var hapticsEnabled: Bool {
        didSet { save(hapticsEnabled, forKey: Keys.hapticsEnabled) }
    }

    /// Whether push notifications are enabled
    @Published public var notificationsEnabled: Bool {
        didSet { save(notificationsEnabled, forKey: Keys.notificationsEnabled) }
    }

    // MARK: - Gameplay Settings

    /// Game difficulty level
    @Published public var difficulty: GameDifficulty {
        didSet { save(difficulty.rawValue, forKey: Keys.difficulty) }
    }

    /// Preferred language
    @Published public var language: String {
        didSet { save(language, forKey: Keys.language) }
    }

    // MARK: - Debug/Developer Settings

    /// Whether to show FPS counter
    @Published public var showFPS: Bool {
        didSet { save(showFPS, forKey: Keys.showFPS) }
    }

    // MARK: - Accessibility Settings

    /// Whether to use reduced motion
    @Published public var reducedMotion: Bool {
        didSet { save(reducedMotion, forKey: Keys.reducedMotion) }
    }

    /// Color blind mode setting
    @Published public var colorBlindMode: ColorBlindMode {
        didSet { save(colorBlindMode.rawValue, forKey: Keys.colorBlindMode) }
    }

    // MARK: - Progress Tracking

    /// Whether the tutorial has been completed
    @Published public var tutorialCompleted: Bool {
        didSet { save(tutorialCompleted, forKey: Keys.tutorialCompleted) }
    }

    // MARK: - Computed Properties

    /// Effective music volume (considering master volume)
    public var effectiveMusicVolume: Double {
        return masterVolume * musicVolume * (musicEnabled ? 1.0 : 0.0)
    }

    /// Effective SFX volume (considering master volume)
    public var effectiveSFXVolume: Double {
        return masterVolume * sfxVolume * (soundEnabled ? 1.0 : 0.0)
    }

    // MARK: - Private Properties

    private let defaults: UserDefaults
    private var cancellables = Set<AnyCancellable>()

    // MARK: - Initialization

    private init(defaults: UserDefaults = .standard) {
        self.defaults = defaults

        // Load all settings
        self.masterVolume = defaults.double(forKey: Keys.masterVolume, default: 1.0)
        self.musicVolume = defaults.double(forKey: Keys.musicVolume, default: 0.7)
        self.sfxVolume = defaults.double(forKey: Keys.sfxVolume, default: 1.0)
        self.soundEnabled = defaults.bool(forKey: Keys.soundEnabled, default: true)
        self.musicEnabled = defaults.bool(forKey: Keys.musicEnabled, default: true)
        self.hapticsEnabled = defaults.bool(forKey: Keys.hapticsEnabled, default: true)
        self.notificationsEnabled = defaults.bool(forKey: Keys.notificationsEnabled, default: true)
        self.difficulty = GameDifficulty(rawValue: defaults.string(forKey: Keys.difficulty) ?? "") ?? .normal
        self.language = defaults.string(forKey: Keys.language) ?? Locale.current.language.languageCode?.identifier ?? "en"
        self.showFPS = defaults.bool(forKey: Keys.showFPS, default: false)
        self.reducedMotion = defaults.bool(forKey: Keys.reducedMotion, default: false)
        self.colorBlindMode = ColorBlindMode(rawValue: defaults.string(forKey: Keys.colorBlindMode) ?? "") ?? .none
        self.tutorialCompleted = defaults.bool(forKey: Keys.tutorialCompleted, default: false)
    }

    // MARK: - Public Methods

    /// Resets all settings to their default values
    public func resetToDefaults() {
        masterVolume = 1.0
        musicVolume = 0.7
        sfxVolume = 1.0
        soundEnabled = true
        musicEnabled = true
        hapticsEnabled = true
        notificationsEnabled = true
        difficulty = .normal
        language = Locale.current.language.languageCode?.identifier ?? "en"
        showFPS = false
        reducedMotion = false
        colorBlindMode = .none
        // Note: tutorialCompleted is intentionally NOT reset
    }

    /// Export settings as a dictionary (for backup/sync)
    public func exportSettings() -> [String: Any] {
        return [
            Keys.masterVolume: masterVolume,
            Keys.musicVolume: musicVolume,
            Keys.sfxVolume: sfxVolume,
            Keys.soundEnabled: soundEnabled,
            Keys.musicEnabled: musicEnabled,
            Keys.hapticsEnabled: hapticsEnabled,
            Keys.notificationsEnabled: notificationsEnabled,
            Keys.difficulty: difficulty.rawValue,
            Keys.language: language,
            Keys.showFPS: showFPS,
            Keys.reducedMotion: reducedMotion,
            Keys.colorBlindMode: colorBlindMode.rawValue,
            Keys.tutorialCompleted: tutorialCompleted
        ]
    }

    /// Import settings from a dictionary
    public func importSettings(_ settings: [String: Any]) {
        if let value = settings[Keys.masterVolume] as? Double { masterVolume = value }
        if let value = settings[Keys.musicVolume] as? Double { musicVolume = value }
        if let value = settings[Keys.sfxVolume] as? Double { sfxVolume = value }
        if let value = settings[Keys.soundEnabled] as? Bool { soundEnabled = value }
        if let value = settings[Keys.musicEnabled] as? Bool { musicEnabled = value }
        if let value = settings[Keys.hapticsEnabled] as? Bool { hapticsEnabled = value }
        if let value = settings[Keys.notificationsEnabled] as? Bool { notificationsEnabled = value }
        if let value = settings[Keys.difficulty] as? String { difficulty = GameDifficulty(rawValue: value) ?? .normal }
        if let value = settings[Keys.language] as? String { language = value }
        if let value = settings[Keys.showFPS] as? Bool { showFPS = value }
        if let value = settings[Keys.reducedMotion] as? Bool { reducedMotion = value }
        if let value = settings[Keys.colorBlindMode] as? String { colorBlindMode = ColorBlindMode(rawValue: value) ?? .none }
        if let value = settings[Keys.tutorialCompleted] as? Bool { tutorialCompleted = value }
    }

    // MARK: - Private Methods

    private func save<T>(_ value: T, forKey key: String) {
        defaults.set(value, forKey: key)
    }
}

// MARK: - Supporting Types

/// Game difficulty levels
public enum GameDifficulty: String, CaseIterable, Sendable {
    case easy
    case normal
    case hard
    case expert

    public var displayName: String {
        switch self {
        case .easy: return "Easy"
        case .normal: return "Normal"
        case .hard: return "Hard"
        case .expert: return "Expert"
        }
    }

    public var multiplier: Double {
        switch self {
        case .easy: return 0.75
        case .normal: return 1.0
        case .hard: return 1.5
        case .expert: return 2.0
        }
    }
}

/// Color blind accessibility modes
public enum ColorBlindMode: String, CaseIterable, Sendable {
    case none
    case protanopia      // Red-blind
    case deuteranopia    // Green-blind
    case tritanopia      // Blue-blind
    case achromatopsia   // Complete color blindness

    public var displayName: String {
        switch self {
        case .none: return "None"
        case .protanopia: return "Protanopia (Red-Blind)"
        case .deuteranopia: return "Deuteranopia (Green-Blind)"
        case .tritanopia: return "Tritanopia (Blue-Blind)"
        case .achromatopsia: return "Achromatopsia (Grayscale)"
        }
    }
}

// MARK: - UserDefaults Extension

private extension UserDefaults {
    func double(forKey key: String, default defaultValue: Double) -> Double {
        if object(forKey: key) == nil {
            return defaultValue
        }
        return double(forKey: key)
    }

    func bool(forKey key: String, default defaultValue: Bool) -> Bool {
        if object(forKey: key) == nil {
            return defaultValue
        }
        return bool(forKey: key)
    }
}
