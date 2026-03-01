import Foundation
import CoreGraphics

enum GameConstants {
    // Player
    static let playerSize = CGSize(width: 40, height: 50)
    static let playerX: CGFloat = 80
    static let jumpVelocity: CGFloat = -14
    static let gravity: CGFloat = 0.6
    static let maxFallSpeed: CGFloat = 15
    static let maxJumps = 2

    // Ground
    static let groundHeight: CGFloat = 60

    // Obstacles
    static let minObstacleGap: CGFloat = 250
    static let maxObstacleGap: CGFloat = 400
    static let obstacleWidth: CGFloat = 30
    static let minObstacleHeight: CGFloat = 30
    static let maxObstacleHeight: CGFloat = 70

    // Game speed
    static let initialSpeed: CGFloat = 5
    static let maxSpeed: CGFloat = 14
    static let speedIncreaseRate: CGFloat = 0.002

    // Scoring
    static let pointsPerFrame: Int = 1
    static let milestone: Int = 500
}

enum PlayerState: String {
    case running
    case jumping
    case falling
    case dead
}

enum ObstacleType: CaseIterable {
    case cactusSmall
    case cactusLarge
    case rock
    case doubleRock

    var size: CGSize {
        switch self {
        case .cactusSmall:
            return CGSize(width: 25, height: 40)
        case .cactusLarge:
            return CGSize(width: 30, height: 60)
        case .rock:
            return CGSize(width: 35, height: 30)
        case .doubleRock:
            return CGSize(width: 50, height: 35)
        }
    }
}
