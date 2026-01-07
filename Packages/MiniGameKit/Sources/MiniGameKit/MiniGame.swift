import SwiftUI

/// A protocol that defines a reusable mini-game component.
///
/// Conforming to this protocol allows any game to be treated as a
/// "black box" that can be plugged into any host application.
///
/// ## Usage
/// ```swift
/// struct FlappyClone: MiniGame {
///     let id = UUID()
///     let title = "Flappy Clone"
///     let iconName = "bird"
///
///     func makeGameView() -> AnyView {
///         AnyView(FlappyGameView())
///     }
///
///     func onStart() { print("Game started") }
///     func onPause() { AudioEngine.shared.pauseMusic() }
///     func onResume() { AudioEngine.shared.resumeMusic() }
///     func onEnd(score: Int) { GameCenter.submitScore(score) }
/// }
/// ```
public protocol MiniGame: Identifiable {
    /// Unique identifier for this game instance
    var id: UUID { get }

    /// Display title for the game
    var title: String { get }

    /// SF Symbol name or custom asset name for the icon
    var iconName: String { get }

    /// Optional description of the game
    var description: String { get }

    /// Difficulty rating (1-5)
    var difficulty: Int { get }

    /// Estimated play time in seconds
    var estimatedDuration: TimeInterval { get }

    /// Creates the game view
    @MainActor
    func makeGameView() -> AnyView

    /// Called when the game starts
    func onStart()

    /// Called when the game is paused
    func onPause()

    /// Called when the game resumes from pause
    func onResume()

    /// Called when the game ends
    /// - Parameter score: The final score achieved
    func onEnd(score: Int)

    /// Called to reset the game to initial state
    func onReset()
}

// MARK: - Default Implementations

public extension MiniGame {
    var description: String { "" }
    var difficulty: Int { 1 }
    var estimatedDuration: TimeInterval { 60 }

    func onStart() {}
    func onPause() {}
    func onResume() {}
    func onEnd(score: Int) {}
    func onReset() {}
}

/// Represents the current state of a mini-game
public enum GameState: Equatable, Sendable {
    /// Game is ready to start
    case ready

    /// Game is counting down to start
    case countdown(Int)

    /// Game is actively being played
    case playing

    /// Game is paused
    case paused

    /// Game is over
    case gameOver(score: Int)

    /// Game ended with an error
    case error(String)

    /// Whether the game is in a playable state
    public var isPlayable: Bool {
        switch self {
        case .playing, .countdown:
            return true
        default:
            return false
        }
    }

    /// Whether user input should be accepted
    public var acceptsInput: Bool {
        switch self {
        case .playing:
            return true
        default:
            return false
        }
    }
}

/// A result type for completed games
public struct GameResult: Sendable {
    public let score: Int
    public let duration: TimeInterval
    public let achievementsUnlocked: [String]
    public let isHighScore: Bool

    public init(
        score: Int,
        duration: TimeInterval,
        achievementsUnlocked: [String] = [],
        isHighScore: Bool = false
    ) {
        self.score = score
        self.duration = duration
        self.achievementsUnlocked = achievementsUnlocked
        self.isHighScore = isHighScore
    }
}

/// Protocol for objects that manage game state
public protocol GameStateManager: AnyObject {
    var state: GameState { get set }
    var score: Int { get set }
    var highScore: Int { get }

    func start()
    func pause()
    func resume()
    func end()
    func reset()
}
