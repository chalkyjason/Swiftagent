import XCTest
@testable import GameAuth

final class GameAuthTests: XCTestCase {

    // MARK: - AuthenticationState Tests

    func testAuthenticatedStateProperties() {
        let state = AuthenticationState.authenticated(
            playerID: "test_player_123",
            displayName: "TestPlayer"
        )

        XCTAssertTrue(state.isAuthenticated)
        XCTAssertEqual(state.playerID, "test_player_123")
        XCTAssertEqual(state.displayName, "TestPlayer")
    }

    func testUnauthenticatedStateProperties() {
        let state = AuthenticationState.unauthenticated

        XCTAssertFalse(state.isAuthenticated)
        XCTAssertNil(state.playerID)
        XCTAssertNil(state.displayName)
    }

    func testAuthenticatingStateProperties() {
        let state = AuthenticationState.authenticating

        XCTAssertFalse(state.isAuthenticated)
        XCTAssertNil(state.playerID)
        XCTAssertNil(state.displayName)
    }

    func testErrorStateProperties() {
        let state = AuthenticationState.error(.networkError)

        XCTAssertFalse(state.isAuthenticated)
        XCTAssertNil(state.playerID)
        XCTAssertNil(state.displayName)
    }

    func testAuthenticationStateEquality() {
        let state1 = AuthenticationState.authenticated(playerID: "123", displayName: "Player")
        let state2 = AuthenticationState.authenticated(playerID: "123", displayName: "Player")
        let state3 = AuthenticationState.authenticated(playerID: "456", displayName: "Other")

        XCTAssertEqual(state1, state2)
        XCTAssertNotEqual(state1, state3)

        XCTAssertEqual(AuthenticationState.unauthenticated, AuthenticationState.unauthenticated)
        XCTAssertEqual(AuthenticationState.authenticating, AuthenticationState.authenticating)
    }

    // MARK: - AuthenticationError Tests

    func testAuthenticationErrorDescriptions() {
        let errors: [(AuthenticationError, String)] = [
            (.gameCenterNotAvailable, "Game Center is not available on this device."),
            (.userCancelled, "Authentication was cancelled."),
            (.networkError, "A network error occurred. Please check your connection."),
            (.restricted, "Game Center access is restricted on this device."),
            (.notSignedIn, "Please sign in to Game Center in Settings."),
            (.unknown("Test error"), "An error occurred: Test error")
        ]

        for (error, expectedDescription) in errors {
            XCTAssertEqual(error.localizedDescription, expectedDescription)
        }
    }

    func testAuthenticationErrorEquality() {
        XCTAssertEqual(AuthenticationError.networkError, AuthenticationError.networkError)
        XCTAssertEqual(AuthenticationError.unknown("test"), AuthenticationError.unknown("test"))
        XCTAssertNotEqual(AuthenticationError.unknown("test1"), AuthenticationError.unknown("test2"))
        XCTAssertNotEqual(AuthenticationError.networkError, AuthenticationError.userCancelled)
    }

    // MARK: - GameCenterManager Tests

    @MainActor
    func testManagerInitialState() {
        let manager = GameCenterManager.shared

        // Initial state should be unauthenticated
        XCTAssertEqual(manager.authenticationState, .unauthenticated)
        XCTAssertFalse(manager.isGameCenterEnabled)
        XCTAssertNil(manager.localPlayer)
    }

    @MainActor
    func testCanAuthenticate() {
        let manager = GameCenterManager.shared

        // Should always be able to attempt authentication
        XCTAssertTrue(manager.canAuthenticate)
    }

    @MainActor
    func testPlayerPropertiesWhenUnauthenticated() {
        let manager = GameCenterManager.shared

        XCTAssertNil(manager.playerAlias)
        XCTAssertNil(manager.playerGameCenterID)
    }

    @MainActor
    func testSignOut() {
        let manager = GameCenterManager.shared

        manager.signOut()

        XCTAssertEqual(manager.authenticationState, .unauthenticated)
        XCTAssertFalse(manager.isGameCenterEnabled)
        XCTAssertNil(manager.localPlayer)
    }
}

// MARK: - Mock Delegate for Testing

final class MockAuthenticationDelegate: AuthenticationDelegate {
    var stateChanges: [AuthenticationState] = []
    var presentedViewControllers: [Any] = []

    func authenticationStateDidChange(_ state: AuthenticationState) {
        stateChanges.append(state)
    }

    func presentAuthenticationViewController(_ viewController: Any) {
        presentedViewControllers.append(viewController)
    }
}
