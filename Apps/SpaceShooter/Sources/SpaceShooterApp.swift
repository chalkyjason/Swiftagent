/// SpaceShooter - A Sample Game Using All Reusable Packages
///
/// This app demonstrates how to integrate all the game development
/// packages into a complete iOS game.
///
/// ## Packages Used
/// - **GameAuth**: Game Center authentication
/// - **CoreUI**: Navigation, menus, and settings
/// - **MiniGameKit**: Game loop and state management
/// - **PhysicsUtils**: SpriteKit helpers and vector math
/// - **AudioEngine**: Sound effects, music, and haptics

import SwiftUI
import GameAuth
import CoreUI
import MiniGameKit
import PhysicsUtils
import AudioEngine

// MARK: - App Entry Point

@main
struct SpaceShooterApp: App {
    @StateObject private var coordinator = DefaultGameCoordinator()
    @StateObject private var gameCenter = GameCenterManager.shared
    @StateObject private var settings = SettingsManager.shared

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(coordinator)
                .environmentObject(settings)
                .withGameCenterAuthentication()
                .onAppear {
                    setupAudio()
                }
        }
    }

    private func setupAudio() {
        // Sync audio settings
        SoundManager.shared.masterVolume = Float(settings.masterVolume)
        SoundManager.shared.musicVolume = Float(settings.musicVolume)
        SoundManager.shared.sfxVolume = Float(settings.sfxVolume)
        SoundManager.shared.isMusicEnabled = settings.musicEnabled
        SoundManager.shared.isSfxEnabled = settings.soundEnabled

        // Sync haptics
        HapticFeedback.shared.isEnabled = settings.hapticsEnabled
    }
}

// MARK: - Main Content View

struct ContentView: View {
    @EnvironmentObject var coordinator: DefaultGameCoordinator

    var body: some View {
        CoordinatedNavigationView(coordinator: coordinator) {
            MainMenuScreen()
                .navigationDestination(for: GameDestination.self) { destination in
                    destinationView(for: destination)
                }
        }
    }

    @ViewBuilder
    private func destinationView(for destination: GameDestination) -> some View {
        switch destination {
        case .gameplay:
            GameplayScreen()
        case .settings:
            SettingsScreen()
        case .gameOver(let score):
            GameOverScreen(score: score)
        case .leaderboard:
            LeaderboardScreen()
        case .pause:
            PauseScreen()
        default:
            Text("Unknown destination")
        }
    }
}

// MARK: - Main Menu Screen

struct MainMenuScreen: View {
    @EnvironmentObject var coordinator: DefaultGameCoordinator
    @StateObject private var gameCenter = GameCenterManager.shared

    var body: some View {
        ZStack {
            // Animated background would go here
            Color.black.ignoresSafeArea()

            VStack(spacing: 0) {
                // Title
                Text("SPACE SHOOTER")
                    .font(.system(size: 36, weight: .black, design: .rounded))
                    .foregroundStyle(
                        LinearGradient(
                            colors: [.cyan, .blue],
                            startPoint: .top,
                            endPoint: .bottom
                        )
                    )
                    .padding(.top, 60)

                // Player info
                if let displayName = gameCenter.authenticationState.displayName {
                    Text("Welcome, \(displayName)!")
                        .font(.subheadline)
                        .foregroundStyle(.cyan.opacity(0.7))
                        .padding(.top, 8)
                }

                Spacer()

                // Menu
                MenuView(
                    items: menuItems,
                    theme: .sciFi
                )

                Spacer()

                // Version
                Text("v1.0.0")
                    .font(.caption)
                    .foregroundStyle(.white.opacity(0.3))
                    .padding(.bottom, 20)
            }
        }
    }

    private var menuItems: [MenuItem] {
        MenuBuilder.mainMenu(
            onPlay: {
                HapticFeedback.shared.impact(.medium)
                coordinator.startGame()
            },
            onSettings: {
                HapticFeedback.shared.tap()
                coordinator.showSettings()
            },
            onLeaderboard: gameCenter.isGameCenterEnabled ? {
                HapticFeedback.shared.tap()
                coordinator.showLeaderboard()
            } : nil
        )
    }
}

// MARK: - Gameplay Screen

struct GameplayScreen: View {
    @EnvironmentObject var coordinator: DefaultGameCoordinator
    @StateObject private var gameLoop = GameLoop(targetFPS: 60)
    @State private var playerPosition = CGPoint(x: 0.5, y: 0.2)

    var body: some View {
        GeometryReader { geometry in
            ZStack {
                // Game background
                Color.black.ignoresSafeArea()

                // Stars (simplified)
                ForEach(0..<50, id: \.self) { i in
                    Circle()
                        .fill(.white.opacity(Double.random(in: 0.3...1.0)))
                        .frame(width: CGFloat.random(in: 1...3))
                        .position(
                            x: CGFloat.random(in: 0...geometry.size.width),
                            y: CGFloat.random(in: 0...geometry.size.height)
                        )
                }

                // Player ship (simplified)
                Image(systemName: "arrowtriangle.up.fill")
                    .font(.system(size: 40))
                    .foregroundStyle(.cyan)
                    .position(
                        x: playerPosition.x * geometry.size.width,
                        y: geometry.size.height - (playerPosition.y * geometry.size.height)
                    )

                // HUD
                VStack {
                    HStack {
                        // Score
                        Text("Score: \(gameLoop.score)")
                            .font(.headline.monospaced())
                            .foregroundStyle(.white)

                        Spacer()

                        // Pause button
                        Button {
                            gameLoop.pause()
                            coordinator.showPause()
                        } label: {
                            Image(systemName: "pause.fill")
                                .font(.title2)
                                .foregroundStyle(.white)
                        }
                    }
                    .padding()

                    Spacer()
                }

                // Pause overlay
                if gameLoop.state == .paused {
                    PauseOverlay(
                        isPresented: true,
                        onResume: {
                            gameLoop.resume()
                            coordinator.goBack()
                        },
                        onQuit: {
                            gameLoop.stop()
                            coordinator.showMenu()
                        }
                    )
                }

                // Game over overlay
                if case .gameOver(let score) = gameLoop.state {
                    GameOverOverlay(
                        score: score,
                        highScore: gameLoop.highScore,
                        onPlayAgain: {
                            gameLoop.reset()
                            gameLoop.start()
                        },
                        onMainMenu: {
                            coordinator.showMenu()
                        }
                    )
                }
            }
            .gesture(
                DragGesture()
                    .onChanged { value in
                        let newX = value.location.x / geometry.size.width
                        playerPosition.x = min(max(newX, 0.1), 0.9)
                    }
            )
            .onTapGesture {
                // Fire weapon
                HapticFeedback.shared.impact(.light)
                gameLoop.addScore(10)
            }
        }
        .navigationBarHidden(true)
        .onAppear {
            gameLoop.start()
            gameLoop.onUpdate = { deltaTime in
                // Game update logic would go here
            }
        }
        .autoPause(onPause: {
            gameLoop.pause()
        })
    }
}

// MARK: - Settings Screen

struct SettingsScreen: View {
    @Environment(\.dismiss) private var dismiss

    var body: some View {
        SettingsView(onDismiss: {
            dismiss()
        })
    }
}

// MARK: - Game Over Screen

struct GameOverScreen: View {
    let score: Int
    @EnvironmentObject var coordinator: DefaultGameCoordinator

    var body: some View {
        ZStack {
            Color.black.ignoresSafeArea()

            VStack(spacing: 32) {
                Text("GAME OVER")
                    .font(.system(size: 48, weight: .black))
                    .foregroundStyle(.red)

                Text("Score: \(score)")
                    .font(.system(size: 36, weight: .bold, design: .rounded))
                    .foregroundStyle(.white)

                VStack(spacing: 16) {
                    Button {
                        coordinator.startGame()
                    } label: {
                        Text("Play Again")
                            .font(.headline)
                            .frame(maxWidth: .infinity)
                            .padding()
                            .background(.cyan)
                            .foregroundStyle(.black)
                            .clipShape(RoundedRectangle(cornerRadius: 12))
                    }

                    Button {
                        coordinator.showMenu()
                    } label: {
                        Text("Main Menu")
                            .font(.headline)
                            .frame(maxWidth: .infinity)
                            .padding()
                            .background(.white.opacity(0.2))
                            .foregroundStyle(.white)
                            .clipShape(RoundedRectangle(cornerRadius: 12))
                    }
                }
                .padding(.horizontal, 40)
            }
        }
        .navigationBarHidden(true)
    }
}

// MARK: - Leaderboard Screen

struct LeaderboardScreen: View {
    @Environment(\.dismiss) private var dismiss

    var body: some View {
        ZStack {
            Color.black.ignoresSafeArea()

            VStack {
                Text("Leaderboard")
                    .font(.largeTitle.bold())
                    .foregroundStyle(.white)

                Text("Game Center integration would show here")
                    .foregroundStyle(.white.opacity(0.7))

                Button("Done") {
                    dismiss()
                }
                .padding()
            }
        }
    }
}

// MARK: - Pause Screen

struct PauseScreen: View {
    @EnvironmentObject var coordinator: DefaultGameCoordinator

    var body: some View {
        // The pause overlay is handled in GameplayScreen
        // This is just a placeholder for navigation
        Color.clear
    }
}
