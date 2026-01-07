import SwiftUI

/// A protocol that defines navigation coordination for game flows.
///
/// The Coordinator pattern separates navigation logic from views,
/// making flows reusable across different games.
///
/// ## Usage
/// ```swift
/// class MainCoordinator: GameCoordinator {
///     @Published var path = NavigationPath()
///
///     func showMenu() {
///         path.removeLast(path.count)
///     }
///
///     func startGame() {
///         path.append(GameDestination.gameplay)
///     }
/// }
/// ```
public protocol GameCoordinator: ObservableObject {
    /// The navigation path for NavigationStack
    var path: NavigationPath { get set }

    /// Navigate to the main menu
    func showMenu()

    /// Start the game
    func startGame()

    /// Show the settings screen
    func showSettings()

    /// Show the authentication/login screen
    func showAuthentication()

    /// Go back one screen
    func goBack()

    /// Reset to the root of navigation
    func popToRoot()
}

/// Default implementations for GameCoordinator
public extension GameCoordinator {
    func goBack() {
        if !path.isEmpty {
            path.removeLast()
        }
    }

    func popToRoot() {
        path.removeLast(path.count)
    }
}

/// Common navigation destinations for games
public enum GameDestination: Hashable, Codable {
    case mainMenu
    case gameplay
    case settings
    case authentication
    case leaderboard
    case achievements
    case pause
    case gameOver(score: Int)
    case levelSelect
    case custom(String)
}

/// A concrete implementation of GameCoordinator for common game flows.
@MainActor
public final class DefaultGameCoordinator: GameCoordinator {
    @Published public var path = NavigationPath()

    /// Callback when navigation changes
    public var onNavigationChange: ((GameDestination?) -> Void)?

    public init() {}

    public func showMenu() {
        popToRoot()
        onNavigationChange?(.mainMenu)
    }

    public func startGame() {
        path.append(GameDestination.gameplay)
        onNavigationChange?(.gameplay)
    }

    public func showSettings() {
        path.append(GameDestination.settings)
        onNavigationChange?(.settings)
    }

    public func showAuthentication() {
        path.append(GameDestination.authentication)
        onNavigationChange?(.authentication)
    }

    public func showLeaderboard() {
        path.append(GameDestination.leaderboard)
        onNavigationChange?(.leaderboard)
    }

    public func showAchievements() {
        path.append(GameDestination.achievements)
        onNavigationChange?(.achievements)
    }

    public func showPause() {
        path.append(GameDestination.pause)
        onNavigationChange?(.pause)
    }

    public func showGameOver(score: Int) {
        path.append(GameDestination.gameOver(score: score))
        onNavigationChange?(.gameOver(score: score))
    }

    public func showLevelSelect() {
        path.append(GameDestination.levelSelect)
        onNavigationChange?(.levelSelect)
    }

    public func navigate(to destination: GameDestination) {
        path.append(destination)
        onNavigationChange?(destination)
    }
}

/// A view that provides coordinated navigation for game screens.
public struct CoordinatedNavigationView<Content: View, Coordinator: GameCoordinator>: View {
    @ObservedObject var coordinator: Coordinator
    let content: () -> Content

    public init(
        coordinator: Coordinator,
        @ViewBuilder content: @escaping () -> Content
    ) {
        self.coordinator = coordinator
        self.content = content
    }

    public var body: some View {
        NavigationStack(path: $coordinator.path) {
            content()
        }
    }
}
