import SwiftUI
import Combine

/// Observes app lifecycle events and manages game pause state automatically.
///
/// This observer listens to `scenePhase` changes and automatically pauses
/// games when the app goes to the background.
///
/// ## Usage
/// ```swift
/// @StateObject private var lifecycle = GameLifecycleObserver()
///
/// var body: some View {
///     GameView()
///         .onChange(of: lifecycle.shouldPause) { _, shouldPause in
///             if shouldPause { gameLoop.pause() }
///         }
/// }
/// ```
@MainActor
public final class GameLifecycleObserver: ObservableObject {
    /// Whether the game should be paused
    @Published public private(set) var shouldPause: Bool = false

    /// Whether the app is currently in foreground
    @Published public private(set) var isInForeground: Bool = true

    /// The current scene phase
    @Published public private(set) var scenePhase: ScenePhase = .active

    /// Callback when pause state changes
    public var onPauseStateChanged: ((Bool) -> Void)?

    /// Callback when app enters background
    public var onEnterBackground: (() -> Void)?

    /// Callback when app enters foreground
    public var onEnterForeground: (() -> Void)?

    private var cancellables = Set<AnyCancellable>()

    public init() {
        setupNotifications()
    }

    private func setupNotifications() {
        // App will resign active (going to background)
        NotificationCenter.default.publisher(for: UIApplication.willResignActiveNotification)
            .receive(on: DispatchQueue.main)
            .sink { [weak self] _ in
                self?.handleResignActive()
            }
            .store(in: &cancellables)

        // App did become active (coming to foreground)
        NotificationCenter.default.publisher(for: UIApplication.didBecomeActiveNotification)
            .receive(on: DispatchQueue.main)
            .sink { [weak self] _ in
                self?.handleBecomeActive()
            }
            .store(in: &cancellables)

        // App will enter foreground (before becoming active)
        NotificationCenter.default.publisher(for: UIApplication.willEnterForegroundNotification)
            .receive(on: DispatchQueue.main)
            .sink { [weak self] _ in
                self?.isInForeground = true
            }
            .store(in: &cancellables)

        // App did enter background
        NotificationCenter.default.publisher(for: UIApplication.didEnterBackgroundNotification)
            .receive(on: DispatchQueue.main)
            .sink { [weak self] _ in
                self?.isInForeground = false
            }
            .store(in: &cancellables)
    }

    private func handleResignActive() {
        shouldPause = true
        scenePhase = .inactive
        onPauseStateChanged?(true)
        onEnterBackground?()
    }

    private func handleBecomeActive() {
        scenePhase = .active
        onEnterForeground?()
        // Note: We don't automatically resume - let the user decide
    }

    /// Call this to acknowledge the resume (clears the shouldPause flag)
    public func acknowledgeResume() {
        shouldPause = false
        onPauseStateChanged?(false)
    }

    /// Updates from SwiftUI's scenePhase environment
    public func update(scenePhase: ScenePhase) {
        let oldPhase = self.scenePhase
        self.scenePhase = scenePhase

        if oldPhase == .active && scenePhase != .active {
            shouldPause = true
            onPauseStateChanged?(true)
        }

        isInForeground = scenePhase == .active
    }
}

/// A view modifier that automatically pauses games on lifecycle events
public struct AutoPauseModifier: ViewModifier {
    @Environment(\.scenePhase) private var scenePhase
    @StateObject private var lifecycle = GameLifecycleObserver()

    let onPause: () -> Void
    let onResume: (() -> Void)?

    public init(onPause: @escaping () -> Void, onResume: (() -> Void)? = nil) {
        self.onPause = onPause
        self.onResume = onResume
    }

    public func body(content: Content) -> some View {
        content
            .onChange(of: scenePhase) { oldPhase, newPhase in
                lifecycle.update(scenePhase: newPhase)

                if newPhase != .active {
                    onPause()
                }
            }
            .environmentObject(lifecycle)
    }
}

public extension View {
    /// Adds automatic pause behavior when app goes to background
    func autoPause(onPause: @escaping () -> Void, onResume: (() -> Void)? = nil) -> some View {
        modifier(AutoPauseModifier(onPause: onPause, onResume: onResume))
    }
}

// MARK: - Pause Overlay

/// A reusable pause overlay view with resume and quit options
public struct PauseOverlay<Background: View>: View {
    let isPresented: Bool
    let onResume: () -> Void
    let onQuit: () -> Void
    let onSettings: (() -> Void)?
    let background: () -> Background

    public init(
        isPresented: Bool,
        onResume: @escaping () -> Void,
        onQuit: @escaping () -> Void,
        onSettings: (() -> Void)? = nil,
        @ViewBuilder background: @escaping () -> Background = { Color.black.opacity(0.7) }
    ) {
        self.isPresented = isPresented
        self.onResume = onResume
        self.onQuit = onQuit
        self.onSettings = onSettings
        self.background = background
    }

    public var body: some View {
        if isPresented {
            ZStack {
                background()
                    .ignoresSafeArea()

                VStack(spacing: 24) {
                    Text("PAUSED")
                        .font(.system(size: 48, weight: .black))
                        .foregroundStyle(.white)

                    VStack(spacing: 16) {
                        PauseButton(title: "Resume", icon: "play.fill", style: .primary) {
                            onResume()
                        }

                        if let onSettings = onSettings {
                            PauseButton(title: "Settings", icon: "gearshape.fill", style: .secondary) {
                                onSettings()
                            }
                        }

                        PauseButton(title: "Quit", icon: "house.fill", style: .destructive) {
                            onQuit()
                        }
                    }
                }
            }
            .transition(.opacity)
        }
    }
}

/// A styled button for the pause menu
public struct PauseButton: View {
    enum Style {
        case primary, secondary, destructive
    }

    let title: String
    let icon: String
    let style: Style
    let action: () -> Void

    public init(title: String, icon: String, style: Style, action: @escaping () -> Void) {
        self.title = title
        self.icon = icon
        self.style = style
        self.action = action
    }

    public var body: some View {
        Button(action: action) {
            HStack {
                Image(systemName: icon)
                Text(title)
            }
            .font(.headline)
            .foregroundStyle(textColor)
            .frame(minWidth: 200)
            .padding(.vertical, 16)
            .padding(.horizontal, 32)
            .background(backgroundColor)
            .clipShape(RoundedRectangle(cornerRadius: 12))
        }
    }

    private var textColor: Color {
        switch style {
        case .primary: return .black
        case .secondary: return .white
        case .destructive: return .white
        }
    }

    private var backgroundColor: Color {
        switch style {
        case .primary: return .white
        case .secondary: return .white.opacity(0.2)
        case .destructive: return .red.opacity(0.8)
        }
    }
}

// MARK: - Game Over Overlay

/// A reusable game over overlay
public struct GameOverOverlay: View {
    let score: Int
    let highScore: Int
    let onPlayAgain: () -> Void
    let onMainMenu: () -> Void
    let onShare: (() -> Void)?

    public init(
        score: Int,
        highScore: Int,
        onPlayAgain: @escaping () -> Void,
        onMainMenu: @escaping () -> Void,
        onShare: (() -> Void)? = nil
    ) {
        self.score = score
        self.highScore = highScore
        self.onPlayAgain = onPlayAgain
        self.onMainMenu = onMainMenu
        self.onShare = onShare
    }

    public var body: some View {
        ZStack {
            Color.black.opacity(0.8)
                .ignoresSafeArea()

            VStack(spacing: 32) {
                Text("GAME OVER")
                    .font(.system(size: 40, weight: .black))
                    .foregroundStyle(.white)

                VStack(spacing: 8) {
                    Text("Score")
                        .font(.headline)
                        .foregroundStyle(.white.opacity(0.7))

                    Text("\(score)")
                        .font(.system(size: 64, weight: .bold, design: .rounded))
                        .foregroundStyle(.white)

                    if score >= highScore && score > 0 {
                        Text("NEW HIGH SCORE!")
                            .font(.headline)
                            .foregroundStyle(.yellow)
                    } else {
                        Text("Best: \(highScore)")
                            .font(.subheadline)
                            .foregroundStyle(.white.opacity(0.5))
                    }
                }

                VStack(spacing: 16) {
                    PauseButton(title: "Play Again", icon: "arrow.clockwise", style: .primary) {
                        onPlayAgain()
                    }

                    if let onShare = onShare {
                        PauseButton(title: "Share", icon: "square.and.arrow.up", style: .secondary) {
                            onShare()
                        }
                    }

                    PauseButton(title: "Main Menu", icon: "house.fill", style: .secondary) {
                        onMainMenu()
                    }
                }
            }
        }
        .transition(.opacity)
    }
}
