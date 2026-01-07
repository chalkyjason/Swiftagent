import Foundation

/// Represents the current authentication state of the user.
public enum AuthenticationState: Equatable, Sendable {
    /// User is currently authenticated with Game Center
    case authenticated(playerID: String, displayName: String)

    /// Authentication is in progress
    case authenticating

    /// User is not authenticated
    case unauthenticated

    /// Authentication failed with an error
    case error(AuthenticationError)

    /// Whether the user is currently authenticated
    public var isAuthenticated: Bool {
        if case .authenticated = self {
            return true
        }
        return false
    }

    /// The display name if authenticated, nil otherwise
    public var displayName: String? {
        if case .authenticated(_, let name) = self {
            return name
        }
        return nil
    }

    /// The player ID if authenticated, nil otherwise
    public var playerID: String? {
        if case .authenticated(let id, _) = self {
            return id
        }
        return nil
    }
}

/// Errors that can occur during Game Center authentication
public enum AuthenticationError: Error, Equatable, Sendable {
    /// Game Center is not available on this device
    case gameCenterNotAvailable

    /// User cancelled the authentication
    case userCancelled

    /// Network error occurred
    case networkError

    /// Unknown error occurred
    case unknown(String)

    /// Authentication is restricted (e.g., parental controls)
    case restricted

    /// User is not signed into Game Center on the device
    case notSignedIn

    public var localizedDescription: String {
        switch self {
        case .gameCenterNotAvailable:
            return "Game Center is not available on this device."
        case .userCancelled:
            return "Authentication was cancelled."
        case .networkError:
            return "A network error occurred. Please check your connection."
        case .unknown(let message):
            return "An error occurred: \(message)"
        case .restricted:
            return "Game Center access is restricted on this device."
        case .notSignedIn:
            return "Please sign in to Game Center in Settings."
        }
    }
}

/// Delegate protocol for receiving authentication state changes
public protocol AuthenticationDelegate: AnyObject {
    /// Called when authentication state changes
    func authenticationStateDidChange(_ state: AuthenticationState)

    /// Called when a view controller needs to be presented for authentication
    func presentAuthenticationViewController(_ viewController: Any)
}
