import SpriteKit

/// A type-safe wrapper for physics collision categories.
///
/// CollisionCategory provides a clean way to define and manage
/// physics collision masks without manual bit manipulation.
///
/// ## Usage
/// ```swift
/// // Define categories
/// extension CollisionCategory {
///     static let player = CollisionCategory(rawValue: 1 << 0)
///     static let enemy = CollisionCategory(rawValue: 1 << 1)
///     static let projectile = CollisionCategory(rawValue: 1 << 2)
///     static let wall = CollisionCategory(rawValue: 1 << 3)
/// }
///
/// // Configure a node
/// playerNode.physicsBody?.configure(
///     category: .player,
///     collidesWith: [.enemy, .wall],
///     contactsWith: [.enemy, .projectile]
/// )
/// ```
public struct CollisionCategory: OptionSet, Sendable {
    public let rawValue: UInt32

    public init(rawValue: UInt32) {
        self.rawValue = rawValue
    }

    // MARK: - Common Categories

    /// No collision category
    public static let none = CollisionCategory([])

    /// All collision categories
    public static let all = CollisionCategory(rawValue: .max)

    // MARK: - Predefined Game Categories

    /// Category for player-controlled objects
    public static let player = CollisionCategory(rawValue: 1 << 0)

    /// Category for enemy objects
    public static let enemy = CollisionCategory(rawValue: 1 << 1)

    /// Category for projectiles
    public static let projectile = CollisionCategory(rawValue: 1 << 2)

    /// Category for walls/boundaries
    public static let wall = CollisionCategory(rawValue: 1 << 3)

    /// Category for ground/platforms
    public static let ground = CollisionCategory(rawValue: 1 << 4)

    /// Category for collectible items
    public static let collectible = CollisionCategory(rawValue: 1 << 5)

    /// Category for triggers/sensors
    public static let trigger = CollisionCategory(rawValue: 1 << 6)

    /// Category for hazards
    public static let hazard = CollisionCategory(rawValue: 1 << 7)

    // MARK: - Utility Methods

    /// Creates a category from a bit index (0-31)
    public static func bit(_ index: Int) -> CollisionCategory {
        precondition(index >= 0 && index < 32, "Bit index must be 0-31")
        return CollisionCategory(rawValue: 1 << index)
    }
}

// MARK: - SKPhysicsBody Extensions

public extension SKPhysicsBody {
    /// Configures collision properties using type-safe categories
    func configure(
        category: CollisionCategory,
        collidesWith: CollisionCategory = .none,
        contactsWith: CollisionCategory = .none
    ) {
        categoryBitMask = category.rawValue
        collisionBitMask = collidesWith.rawValue
        contactTestBitMask = contactsWith.rawValue
    }

    /// Sets the category bit mask using type-safe categories
    func setCategory(_ category: CollisionCategory) {
        categoryBitMask = category.rawValue
    }

    /// Adds collision categories
    func addCollision(with categories: CollisionCategory) {
        collisionBitMask |= categories.rawValue
    }

    /// Removes collision categories
    func removeCollision(with categories: CollisionCategory) {
        collisionBitMask &= ~categories.rawValue
    }

    /// Adds contact test categories
    func addContact(with categories: CollisionCategory) {
        contactTestBitMask |= categories.rawValue
    }

    /// Removes contact test categories
    func removeContact(with categories: CollisionCategory) {
        contactTestBitMask &= ~categories.rawValue
    }

    /// Checks if this body's category intersects with the given categories
    func isInCategory(_ categories: CollisionCategory) -> Bool {
        categoryBitMask & categories.rawValue != 0
    }

    /// Checks if this body collides with the given categories
    func collidesWith(_ categories: CollisionCategory) -> Bool {
        collisionBitMask & categories.rawValue != 0
    }

    /// Checks if this body contacts with the given categories
    func contactsWith(_ categories: CollisionCategory) -> Bool {
        contactTestBitMask & categories.rawValue != 0
    }
}

// MARK: - SKPhysicsContact Extensions

public extension SKPhysicsContact {
    /// Checks if the contact involves a specific category
    func involves(_ category: CollisionCategory) -> Bool {
        (bodyA.categoryBitMask | bodyB.categoryBitMask) & category.rawValue != 0
    }

    /// Returns the body matching the given category, if any
    func body(for category: CollisionCategory) -> SKPhysicsBody? {
        if bodyA.categoryBitMask & category.rawValue != 0 {
            return bodyA
        }
        if bodyB.categoryBitMask & category.rawValue != 0 {
            return bodyB
        }
        return nil
    }

    /// Returns the other body (not matching the given category)
    func otherBody(than category: CollisionCategory) -> SKPhysicsBody? {
        if bodyA.categoryBitMask & category.rawValue != 0 {
            return bodyB
        }
        if bodyB.categoryBitMask & category.rawValue != 0 {
            return bodyA
        }
        return nil
    }

    /// Returns the node for a specific category
    func node(for category: CollisionCategory) -> SKNode? {
        body(for: category)?.node
    }

    /// Returns the other node (not matching the given category)
    func otherNode(than category: CollisionCategory) -> SKNode? {
        otherBody(than: category)?.node
    }
}

// MARK: - Collision Configuration Presets

/// Pre-built collision configurations for common game object types
public struct CollisionPresets {
    /// Standard player configuration
    public static func player() -> (category: CollisionCategory, collision: CollisionCategory, contact: CollisionCategory) {
        (
            category: .player,
            collision: [.wall, .ground, .enemy],
            contact: [.enemy, .collectible, .hazard, .trigger]
        )
    }

    /// Standard enemy configuration
    public static func enemy() -> (category: CollisionCategory, collision: CollisionCategory, contact: CollisionCategory) {
        (
            category: .enemy,
            collision: [.wall, .ground, .player],
            contact: [.player, .projectile]
        )
    }

    /// Standard projectile configuration
    public static func projectile() -> (category: CollisionCategory, collision: CollisionCategory, contact: CollisionCategory) {
        (
            category: .projectile,
            collision: .wall,
            contact: [.enemy, .wall]
        )
    }

    /// Standard wall/boundary configuration
    public static func wall() -> (category: CollisionCategory, collision: CollisionCategory, contact: CollisionCategory) {
        (
            category: .wall,
            collision: .none,
            contact: .none
        )
    }

    /// Standard collectible configuration
    public static func collectible() -> (category: CollisionCategory, collision: CollisionCategory, contact: CollisionCategory) {
        (
            category: .collectible,
            collision: .none,
            contact: .player
        )
    }

    /// Standard trigger/sensor configuration
    public static func trigger() -> (category: CollisionCategory, collision: CollisionCategory, contact: CollisionCategory) {
        (
            category: .trigger,
            collision: .none,
            contact: .player
        )
    }
}
