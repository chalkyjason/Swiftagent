import SwiftUI
import Combine

/// A reusable game loop that manages timing and state for mini-games.
///
/// GameLoop provides:
/// - Fixed timestep updates for consistent physics
/// - Delta time for smooth rendering
/// - Automatic pause/resume handling
/// - Frame rate limiting
///
/// ## Usage
/// ```swift
/// @StateObject private var gameLoop = GameLoop(targetFPS: 60)
///
/// var body: some View {
///     Canvas { context, size in
///         // Render using gameLoop.deltaTime
///     }
///     .onReceive(gameLoop.$tick) { _ in
///         updateGame(deltaTime: gameLoop.deltaTime)
///     }
/// }
/// ```
@MainActor
public final class GameLoop: ObservableObject {
    // MARK: - Published Properties

    /// Increments on each frame, useful for triggering view updates
    @Published public private(set) var tick: UInt64 = 0

    /// Current game state
    @Published public var state: GameState = .ready {
        didSet { handleStateChange(from: oldValue, to: state) }
    }

    /// Current score
    @Published public var score: Int = 0

    /// Time elapsed since game started (excluding pauses)
    @Published public private(set) var elapsedTime: TimeInterval = 0

    // MARK: - Public Properties

    /// Time since the last frame (for smooth rendering)
    public private(set) var deltaTime: TimeInterval = 0

    /// Target frames per second
    public let targetFPS: Int

    /// Fixed timestep for physics updates (seconds)
    public let fixedTimestep: TimeInterval

    /// High score for this session
    public private(set) var highScore: Int = 0

    /// Whether the game loop is running
    public var isRunning: Bool {
        displayLink != nil && state == .playing
    }

    // MARK: - Callbacks

    /// Called each frame with the delta time
    public var onUpdate: ((TimeInterval) -> Void)?

    /// Called at fixed intervals for physics
    public var onFixedUpdate: ((TimeInterval) -> Void)?

    /// Called when state changes
    public var onStateChange: ((GameState, GameState) -> Void)?

    // MARK: - Private Properties

    private var displayLink: CADisplayLink?
    private var lastFrameTime: CFTimeInterval = 0
    private var accumulator: TimeInterval = 0
    private var pauseTime: CFTimeInterval = 0
    private var cancellables = Set<AnyCancellable>()

    // MARK: - Initialization

    public init(targetFPS: Int = 60, fixedTimestep: TimeInterval = 1.0 / 60.0) {
        self.targetFPS = targetFPS
        self.fixedTimestep = fixedTimestep
        setupScenePhaseObserver()
    }

    deinit {
        stop()
    }

    // MARK: - Public Methods

    /// Starts the game loop
    public func start() {
        guard state != .playing else { return }

        state = .playing
        score = 0
        elapsedTime = 0
        accumulator = 0

        startDisplayLink()
    }

    /// Starts with a countdown
    public func startWithCountdown(from count: Int = 3) {
        guard state == .ready || state == .gameOver(score: score) else { return }

        state = .countdown(count)
        performCountdown(from: count)
    }

    /// Pauses the game loop
    public func pause() {
        guard state == .playing else { return }
        pauseTime = CACurrentMediaTime()
        state = .paused
    }

    /// Resumes the game loop
    public func resume() {
        guard state == .paused else { return }
        let pauseDuration = CACurrentMediaTime() - pauseTime
        lastFrameTime += pauseDuration
        state = .playing
    }

    /// Stops the game loop and records the score
    public func stop() {
        stopDisplayLink()

        if score > highScore {
            highScore = score
        }

        if case .playing = state {
            state = .gameOver(score: score)
        }
    }

    /// Resets the game loop to initial state
    public func reset() {
        stop()
        score = 0
        elapsedTime = 0
        tick = 0
        state = .ready
    }

    /// Adds points to the score
    public func addScore(_ points: Int) {
        score += points
    }

    /// Sets the score directly
    public func setScore(_ newScore: Int) {
        score = newScore
    }

    // MARK: - Private Methods

    private func setupScenePhaseObserver() {
        // Observe app lifecycle for automatic pause/resume
        NotificationCenter.default.publisher(for: UIApplication.willResignActiveNotification)
            .sink { [weak self] _ in
                self?.pause()
            }
            .store(in: &cancellables)

        NotificationCenter.default.publisher(for: UIApplication.didBecomeActiveNotification)
            .sink { [weak self] _ in
                // Don't auto-resume, let user decide
            }
            .store(in: &cancellables)
    }

    private func startDisplayLink() {
        stopDisplayLink()

        lastFrameTime = CACurrentMediaTime()

        let link = CADisplayLink(target: self, selector: #selector(frame))
        link.preferredFrameRateRange = CAFrameRateRange(
            minimum: Float(targetFPS / 2),
            maximum: Float(targetFPS),
            preferred: Float(targetFPS)
        )
        link.add(to: .main, forMode: .common)
        displayLink = link
    }

    private func stopDisplayLink() {
        displayLink?.invalidate()
        displayLink = nil
    }

    @objc private func frame(_ displayLink: CADisplayLink) {
        guard state == .playing else { return }

        let currentTime = displayLink.timestamp
        deltaTime = min(currentTime - lastFrameTime, 0.1) // Cap at 100ms to prevent spiral of death
        lastFrameTime = currentTime
        elapsedTime += deltaTime

        // Fixed timestep accumulator for physics
        accumulator += deltaTime

        while accumulator >= fixedTimestep {
            onFixedUpdate?(fixedTimestep)
            accumulator -= fixedTimestep
        }

        // Variable timestep for rendering
        onUpdate?(deltaTime)

        tick += 1
    }

    private func performCountdown(from count: Int) {
        guard count > 0 else {
            start()
            return
        }

        state = .countdown(count)

        DispatchQueue.main.asyncAfter(deadline: .now() + 1.0) { [weak self] in
            self?.performCountdown(from: count - 1)
        }
    }

    private func handleStateChange(from oldState: GameState, to newState: GameState) {
        onStateChange?(oldState, newState)

        switch newState {
        case .playing:
            if displayLink == nil {
                startDisplayLink()
            }
        case .paused, .gameOver, .ready, .error:
            break
        case .countdown:
            break
        }
    }
}

// MARK: - GameStateManager Conformance

extension GameLoop: GameStateManager {
    public func end() {
        stop()
    }
}

// MARK: - Game Timer

/// A simple countdown or count-up timer for games
@MainActor
public final class GameTimer: ObservableObject {
    public enum Mode {
        case countUp
        case countDown(from: TimeInterval)
    }

    @Published public private(set) var timeRemaining: TimeInterval
    @Published public private(set) var isExpired: Bool = false

    public let mode: Mode
    public var onExpired: (() -> Void)?

    private var timer: Timer?
    private let startTime: TimeInterval

    public init(mode: Mode) {
        self.mode = mode
        switch mode {
        case .countUp:
            self.timeRemaining = 0
            self.startTime = 0
        case .countDown(let time):
            self.timeRemaining = time
            self.startTime = time
        }
    }

    public func start() {
        timer?.invalidate()
        timer = Timer.scheduledTimer(withTimeInterval: 0.1, repeats: true) { [weak self] _ in
            Task { @MainActor in
                self?.tick()
            }
        }
    }

    public func pause() {
        timer?.invalidate()
        timer = nil
    }

    public func reset() {
        timer?.invalidate()
        timer = nil
        isExpired = false
        switch mode {
        case .countUp:
            timeRemaining = 0
        case .countDown(let time):
            timeRemaining = time
        }
    }

    private func tick() {
        switch mode {
        case .countUp:
            timeRemaining += 0.1
        case .countDown:
            timeRemaining -= 0.1
            if timeRemaining <= 0 {
                timeRemaining = 0
                isExpired = true
                timer?.invalidate()
                timer = nil
                onExpired?()
            }
        }
    }

    /// Formatted time string (MM:SS or MM:SS.S)
    public var formattedTime: String {
        let minutes = Int(timeRemaining) / 60
        let seconds = Int(timeRemaining) % 60
        let tenths = Int((timeRemaining * 10).truncatingRemainder(dividingBy: 10))

        if case .countDown = mode {
            return String(format: "%02d:%02d.%d", minutes, seconds, tenths)
        }
        return String(format: "%02d:%02d", minutes, seconds)
    }
}
