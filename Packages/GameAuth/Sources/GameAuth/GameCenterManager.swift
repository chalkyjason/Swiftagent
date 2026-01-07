import Foundation
import GameKit
import Combine

/// Manages Game Center authentication and player state.
///
/// This singleton handles all Game Center interactions including:
/// - Player authentication
/// - Access to player information
/// - Authentication state observation
///
/// ## Usage
/// ```swift
/// // Get the shared instance
/// let manager = GameCenterManager.shared
///
/// // Observe state changes in SwiftUI
/// @StateObject private var gameCenter = GameCenterManager.shared
///
/// // Authenticate
/// await manager.authenticate()
/// ```
@MainActor
public final class GameCenterManager: ObservableObject {
    // MARK: - Singleton

    /// Shared instance of the Game Center manager
    public static let shared = GameCenterManager()

    // MARK: - Published Properties

    /// Current authentication state
    @Published public private(set) var authenticationState: AuthenticationState = .unauthenticated

    /// The authenticated local player, if available
    @Published public private(set) var localPlayer: GKLocalPlayer?

    /// Whether the user can access Game Center features
    @Published public private(set) var isGameCenterEnabled: Bool = false

    // MARK: - Properties

    /// Delegate for receiving authentication callbacks
    public weak var delegate: AuthenticationDelegate?

    /// View controller to present for authentication (iOS only)
    #if os(iOS) || os(tvOS)
    private var authenticationViewController: UIViewController?
    #endif

    // MARK: - Private Properties

    private var cancellables = Set<AnyCancellable>()

    // MARK: - Initialization

    private init() {
        setupAuthenticationHandler()
    }

    // MARK: - Public Methods

    /// Initiates Game Center authentication.
    ///
    /// This method should be called early in the app lifecycle, typically in
    /// the app's `onAppear` or during launch.
    ///
    /// - Returns: The resulting authentication state
    @discardableResult
    public func authenticate() async -> AuthenticationState {
        authenticationState = .authenticating

        return await withCheckedContinuation { continuation in
            let player = GKLocalPlayer.local

            player.authenticateHandler = { [weak self] viewController, error in
                Task { @MainActor in
                    guard let self = self else {
                        continuation.resume(returning: .unauthenticated)
                        return
                    }

                    let state = self.handleAuthenticationResult(
                        viewController: viewController,
                        error: error
                    )

                    self.updateState(state)
                    continuation.resume(returning: state)
                }
            }
        }
    }

    /// Signs out the current player.
    ///
    /// Note: Game Center doesn't provide a programmatic sign-out.
    /// This method resets the local state but the user must sign out
    /// through the device's Game Center settings.
    public func signOut() {
        authenticationState = .unauthenticated
        localPlayer = nil
        isGameCenterEnabled = false
        delegate?.authenticationStateDidChange(.unauthenticated)
    }

    /// Checks if Game Center is available and the player can authenticate.
    public var canAuthenticate: Bool {
        return GKLocalPlayer.local.isAuthenticated || !GKLocalPlayer.local.isAuthenticated
    }

    /// Gets the authenticated player's alias (display name).
    public var playerAlias: String? {
        return localPlayer?.alias
    }

    /// Gets the authenticated player's Game Center ID.
    public var playerGameCenterID: String? {
        return localPlayer?.gamePlayerID
    }

    // MARK: - Private Methods

    private func setupAuthenticationHandler() {
        // Listen for authentication state changes from the system
        NotificationCenter.default.publisher(for: .GKPlayerAuthenticationDidChangeNotificationName)
            .receive(on: DispatchQueue.main)
            .sink { [weak self] _ in
                Task { @MainActor in
                    self?.checkAuthenticationStatus()
                }
            }
            .store(in: &cancellables)
    }

    private func checkAuthenticationStatus() {
        let player = GKLocalPlayer.local

        if player.isAuthenticated {
            let state = AuthenticationState.authenticated(
                playerID: player.gamePlayerID,
                displayName: player.alias
            )
            updateState(state)
        } else {
            updateState(.unauthenticated)
        }
    }

    private func handleAuthenticationResult(
        viewController: Any?,
        error: Error?
    ) -> AuthenticationState {
        let player = GKLocalPlayer.local

        // Handle errors first
        if let error = error {
            return mapError(error)
        }

        // Check if we need to present a view controller
        #if os(iOS) || os(tvOS)
        if let vc = viewController as? UIViewController {
            authenticationViewController = vc
            delegate?.presentAuthenticationViewController(vc)
            return .authenticating
        }
        #elseif os(macOS)
        if let vc = viewController {
            delegate?.presentAuthenticationViewController(vc)
            return .authenticating
        }
        #endif

        // Check authentication status
        if player.isAuthenticated {
            localPlayer = player
            isGameCenterEnabled = true
            return .authenticated(
                playerID: player.gamePlayerID,
                displayName: player.alias
            )
        }

        return .unauthenticated
    }

    private func mapError(_ error: Error) -> AuthenticationState {
        let nsError = error as NSError

        switch nsError.code {
        case GKError.cancelled.rawValue:
            return .error(.userCancelled)

        case GKError.notSupported.rawValue:
            return .error(.gameCenterNotAvailable)

        case GKError.communicationsFailure.rawValue,
             GKError.connectionTimeout.rawValue:
            return .error(.networkError)

        case GKError.gameUnrecognized.rawValue,
             GKError.notAuthenticated.rawValue:
            return .error(.notSignedIn)

        case GKError.restrictedToAutomatch.rawValue,
             GKError.userDenied.rawValue:
            return .error(.restricted)

        default:
            return .error(.unknown(error.localizedDescription))
        }
    }

    private func updateState(_ state: AuthenticationState) {
        authenticationState = state
        delegate?.authenticationStateDidChange(state)

        switch state {
        case .authenticated:
            isGameCenterEnabled = true
        case .unauthenticated, .error:
            isGameCenterEnabled = false
            localPlayer = nil
        case .authenticating:
            break
        }
    }
}

// MARK: - SwiftUI View Extension

#if canImport(SwiftUI)
import SwiftUI

/// A view that wraps the Game Center authentication view controller.
#if os(iOS) || os(tvOS)
public struct GameCenterAuthenticationView: UIViewControllerRepresentable {
    let viewController: UIViewController

    public init(viewController: UIViewController) {
        self.viewController = viewController
    }

    public func makeUIViewController(context: Context) -> UIViewController {
        return viewController
    }

    public func updateUIViewController(_ uiViewController: UIViewController, context: Context) {}
}
#endif

/// A view modifier that handles Game Center authentication.
public struct GameCenterAuthenticationModifier: ViewModifier {
    @StateObject private var gameCenter = GameCenterManager.shared
    @State private var showingAuthentication = false
    @State private var authViewController: Any?

    public init() {}

    public func body(content: Content) -> some View {
        content
            .task {
                await gameCenter.authenticate()
            }
            .onChange(of: gameCenter.authenticationState) { oldValue, newValue in
                handleStateChange(newValue)
            }
            #if os(iOS) || os(tvOS)
            .sheet(isPresented: $showingAuthentication) {
                if let vc = authViewController as? UIViewController {
                    GameCenterAuthenticationView(viewController: vc)
                }
            }
            #endif
    }

    private func handleStateChange(_ state: AuthenticationState) {
        switch state {
        case .authenticating:
            // Will be handled by delegate if view controller is needed
            break
        default:
            showingAuthentication = false
        }
    }
}

public extension View {
    /// Adds automatic Game Center authentication to the view.
    func withGameCenterAuthentication() -> some View {
        modifier(GameCenterAuthenticationModifier())
    }
}
#endif
