import SwiftUI

/// Represents a single item in a game menu.
///
/// MenuItems are data-driven components that can be used to build
/// flexible, reusable menus for different games.
///
/// ## Usage
/// ```swift
/// let playItem = MenuItem(
///     id: "play",
///     title: "Play Game",
///     icon: "play.circle.fill",
///     style: .primary
/// ) {
///     coordinator.startGame()
/// }
/// ```
public struct MenuItem: Identifiable {
    public let id: String
    public let title: String
    public let subtitle: String?
    public let icon: String?
    public let style: MenuItemStyle
    public let isEnabled: Bool
    public let badge: String?
    public let action: () -> Void

    public init(
        id: String,
        title: String,
        subtitle: String? = nil,
        icon: String? = nil,
        style: MenuItemStyle = .standard,
        isEnabled: Bool = true,
        badge: String? = nil,
        action: @escaping () -> Void
    ) {
        self.id = id
        self.title = title
        self.subtitle = subtitle
        self.icon = icon
        self.style = style
        self.isEnabled = isEnabled
        self.badge = badge
        self.action = action
    }
}

/// Visual styles for menu items
public enum MenuItemStyle: Equatable, Sendable {
    /// Primary action button (e.g., "Play")
    case primary

    /// Standard menu option
    case standard

    /// Secondary/less important option
    case secondary

    /// Destructive action (e.g., "Delete Save")
    case destructive

    /// Disabled appearance
    case disabled
}

/// A group of menu items with an optional header
public struct MenuSection: Identifiable {
    public let id: String
    public let header: String?
    public let items: [MenuItem]

    public init(
        id: String = UUID().uuidString,
        header: String? = nil,
        items: [MenuItem]
    ) {
        self.id = id
        self.header = header
        self.items = items
    }
}

/// Factory for creating common menu configurations
public struct MenuBuilder {
    /// Creates a standard main menu configuration
    public static func mainMenu(
        onPlay: @escaping () -> Void,
        onSettings: @escaping () -> Void,
        onLeaderboard: (() -> Void)? = nil,
        onAchievements: (() -> Void)? = nil
    ) -> [MenuItem] {
        var items: [MenuItem] = [
            MenuItem(
                id: "play",
                title: "Play",
                icon: "play.circle.fill",
                style: .primary,
                action: onPlay
            ),
            MenuItem(
                id: "settings",
                title: "Settings",
                icon: "gearshape.fill",
                style: .standard,
                action: onSettings
            )
        ]

        if let onLeaderboard = onLeaderboard {
            items.append(MenuItem(
                id: "leaderboard",
                title: "Leaderboard",
                icon: "trophy.fill",
                style: .standard,
                action: onLeaderboard
            ))
        }

        if let onAchievements = onAchievements {
            items.append(MenuItem(
                id: "achievements",
                title: "Achievements",
                icon: "star.fill",
                style: .standard,
                action: onAchievements
            ))
        }

        return items
    }

    /// Creates a pause menu configuration
    public static func pauseMenu(
        onResume: @escaping () -> Void,
        onSettings: @escaping () -> Void,
        onQuit: @escaping () -> Void
    ) -> [MenuItem] {
        return [
            MenuItem(
                id: "resume",
                title: "Resume",
                icon: "play.fill",
                style: .primary,
                action: onResume
            ),
            MenuItem(
                id: "settings",
                title: "Settings",
                icon: "gearshape.fill",
                style: .standard,
                action: onSettings
            ),
            MenuItem(
                id: "quit",
                title: "Quit to Menu",
                icon: "house.fill",
                style: .destructive,
                action: onQuit
            )
        ]
    }

    /// Creates a game over menu configuration
    public static func gameOverMenu(
        score: Int,
        onPlayAgain: @escaping () -> Void,
        onMainMenu: @escaping () -> Void,
        onShare: (() -> Void)? = nil
    ) -> [MenuItem] {
        var items: [MenuItem] = [
            MenuItem(
                id: "play_again",
                title: "Play Again",
                icon: "arrow.clockwise",
                style: .primary,
                action: onPlayAgain
            ),
            MenuItem(
                id: "main_menu",
                title: "Main Menu",
                icon: "house.fill",
                style: .standard,
                action: onMainMenu
            )
        ]

        if let onShare = onShare {
            items.append(MenuItem(
                id: "share",
                title: "Share Score",
                subtitle: "Score: \(score)",
                icon: "square.and.arrow.up",
                style: .standard,
                action: onShare
            ))
        }

        return items
    }
}
