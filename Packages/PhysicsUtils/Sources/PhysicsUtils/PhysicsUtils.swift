/// PhysicsUtils - SpriteKit Physics and Math Utilities
///
/// A Swift package providing common utilities for SpriteKit-based games.
///
/// ## Overview
///
/// PhysicsUtils provides:
/// 1. **Vector Math**: CGPoint/CGVector extensions for game math
/// 2. **Collision Categories**: Type-safe physics category management
/// 3. **BaseGameScene**: Pre-built SKScene with common functionality
///
/// ## Quick Start
///
/// ### Vector Math
/// ```swift
/// let velocity = CGPoint(angle: .pi / 4, length: 100)
/// let normalized = velocity.normalized
/// let distance = point1.distance(to: point2)
/// let reflection = velocity.reflected(normal: surfaceNormal)
/// ```
///
/// ### Collision Categories
/// ```swift
/// extension CollisionCategory {
///     static let player = CollisionCategory(rawValue: 1 << 0)
///     static let enemy = CollisionCategory(rawValue: 1 << 1)
/// }
///
/// playerNode.physicsBody?.configure(
///     category: .player,
///     collidesWith: [.enemy, .wall],
///     contactsWith: [.enemy, .collectible]
/// )
/// ```
///
/// ### BaseGameScene
/// ```swift
/// class MyScene: BaseGameScene {
///     override func update(deltaTime: TimeInterval) {
///         // Called every frame with proper delta time
///         player.position += velocity * deltaTime
///     }
///
///     override func handleTap(at location: CGPoint) {
///         // Unified input handling for iOS and macOS
///         shoot(toward: location)
///     }
///
///     override func handleContact(_ contact: SKPhysicsContact, began: Bool) {
///         // Physics collision handling
///         if let enemy = contact.node(for: .enemy) {
///             enemy.removeFromParent()
///         }
///     }
/// }
/// ```
///
/// ## Features
///
/// - **Cross-Platform**: iOS, macOS, tvOS support
/// - **Performance**: Optimized vector operations
/// - **Type Safety**: Collision categories prevent bit mask errors
/// - **SwiftUI Ready**: SpriteKitView for easy SwiftUI integration

@_exported import SpriteKit
@_exported import CoreGraphics

// Package version
public let physicsUtilsVersion = "1.0.0"
