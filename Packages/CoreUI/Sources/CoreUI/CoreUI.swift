/// CoreUI - Game UI Components Package
///
/// A comprehensive Swift package providing reusable UI components
/// for iOS, macOS, and tvOS games.
///
/// ## Overview
///
/// CoreUI provides three main systems:
/// 1. **Navigation Coordination**: The Coordinator pattern for game flows
/// 2. **Data-Driven Menus**: Flexible, themeable menu components
/// 3. **Settings Management**: Automatic persistence and UI generation
///
/// ## Quick Start
///
/// ### Navigation
/// ```swift
/// @StateObject private var coordinator = DefaultGameCoordinator()
///
/// var body: some View {
///     CoordinatedNavigationView(coordinator: coordinator) {
///         MainMenuView()
///     }
///     .environmentObject(coordinator)
/// }
/// ```
///
/// ### Menus
/// ```swift
/// let items = MenuBuilder.mainMenu(
///     onPlay: { coordinator.startGame() },
///     onSettings: { coordinator.showSettings() }
/// )
///
/// MenuView(title: "My Game", items: items, theme: .sciFi)
/// ```
///
/// ### Settings
/// ```swift
/// NavigationStack {
///     SettingsView()
/// }
/// // That's it! Persistence is automatic.
/// ```
///
/// ## Features
///
/// - **SwiftUI Native**: Built entirely with SwiftUI
/// - **Themeable**: Multiple built-in themes, fully customizable
/// - **Observable**: All managers are `@Observable` for reactive updates
/// - **Accessible**: Built-in accessibility support
/// - **Multi-Platform**: iOS, macOS, tvOS support

// Re-export all public types
@_exported import SwiftUI

// Package version
public let coreUIVersion = "1.0.0"
