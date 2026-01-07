/// GameAuth - Game Center Authentication Package
///
/// A reusable Swift package for handling Game Center authentication
/// in iOS, macOS, and tvOS games.
///
/// ## Overview
///
/// GameAuth provides a simple, SwiftUI-friendly interface for Game Center
/// authentication. It handles the complexity of the GameKit authentication
/// flow and provides observable state for reactive UI updates.
///
/// ## Quick Start
///
/// 1. Import the package:
/// ```swift
/// import GameAuth
/// ```
///
/// 2. Add authentication to your root view:
/// ```swift
/// @main
/// struct MyGameApp: App {
///     var body: some Scene {
///         WindowGroup {
///             ContentView()
///                 .withGameCenterAuthentication()
///         }
///     }
/// }
/// ```
///
/// 3. Observe authentication state:
/// ```swift
/// struct ContentView: View {
///     @StateObject private var gameCenter = GameCenterManager.shared
///
///     var body: some View {
///         Group {
///             switch gameCenter.authenticationState {
///             case .authenticated(_, let name):
///                 Text("Welcome, \(name)!")
///             case .authenticating:
///                 ProgressView("Signing in...")
///             case .unauthenticated:
///                 Button("Sign In") {
///                     Task { await gameCenter.authenticate() }
///                 }
///             case .error(let error):
///                 Text(error.localizedDescription)
///             }
///         }
///     }
/// }
/// ```
///
/// ## Features
///
/// - **SwiftUI Integration**: Observable state with `@Published` properties
/// - **Async/Await Support**: Modern concurrency for authentication
/// - **Error Handling**: Detailed error types with user-friendly messages
/// - **Multi-Platform**: Supports iOS, macOS, and tvOS
/// - **View Modifier**: Simple `.withGameCenterAuthentication()` modifier

// Re-export all public types
@_exported import Foundation
@_exported import GameKit

// Package version
public let gameAuthVersion = "1.0.0"
