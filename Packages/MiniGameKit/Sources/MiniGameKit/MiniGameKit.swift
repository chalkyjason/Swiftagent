/// MiniGameKit - Reusable Game Loop and State Management
///
/// A Swift package providing the core infrastructure for building
/// mini-games on iOS, macOS, and tvOS.
///
/// ## Overview
///
/// MiniGameKit provides:
/// 1. **MiniGame Protocol**: A standard interface for pluggable games
/// 2. **GameLoop**: Fixed and variable timestep update loops
/// 3. **GameLifecycle**: Automatic pause/resume on app state changes
/// 4. **UI Components**: Pause overlays, game over screens
///
/// ## Quick Start
///
/// ### Creating a Mini-Game
/// ```swift
/// struct TapGame: MiniGame {
///     let id = UUID()
///     let title = "Tap Challenge"
///     let iconName = "hand.tap.fill"
///
///     @MainActor
///     func makeGameView() -> AnyView {
///         AnyView(TapGameView())
///     }
/// }
/// ```
///
/// ### Using the Game Loop
/// ```swift
/// struct TapGameView: View {
///     @StateObject private var gameLoop = GameLoop(targetFPS: 60)
///
///     var body: some View {
///         ZStack {
///             // Game content
///
///             PauseOverlay(
///                 isPresented: gameLoop.state == .paused,
///                 onResume: { gameLoop.resume() },
///                 onQuit: { gameLoop.stop() }
///             )
///         }
///         .onAppear { gameLoop.start() }
///         .autoPause(onPause: { gameLoop.pause() })
///     }
/// }
/// ```
///
/// ### Game State Management
/// ```swift
/// // Check state
/// switch gameLoop.state {
/// case .ready:
///     // Show start button
/// case .playing:
///     // Game is active
/// case .paused:
///     // Show pause menu
/// case .gameOver(let score):
///     // Show results
/// }
///
/// // Update score
/// gameLoop.addScore(100)
/// ```
///
/// ## Features
///
/// - **Protocol-Oriented**: Plug any game into any host app
/// - **Fixed Timestep**: Consistent physics simulation
/// - **Auto-Pause**: Automatic lifecycle handling
/// - **Reusable UI**: Pre-built pause and game over overlays

// Re-export SwiftUI for convenience
@_exported import SwiftUI

// Package version
public let miniGameKitVersion = "1.0.0"
