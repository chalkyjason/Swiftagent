import Foundation
import SwiftUI

class GameEngine: ObservableObject {
    // MARK: - Published State

    @Published var playerY: CGFloat = 0
    @Published var playerState: PlayerState = .running
    @Published var obstacles: [Obstacle] = []
    @Published var score: Int = 0
    @Published var highScore: Int = 0
    @Published var isRunning: Bool = false
    @Published var isGameOver: Bool = false
    @Published var groundOffset: CGFloat = 0
    @Published var isNewHighScore: Bool = false

    // MARK: - Internal State

    private(set) var velocity: CGFloat = 0
    private(set) var jumpsRemaining: Int = GameConstants.maxJumps
    private(set) var speed: CGFloat = GameConstants.initialSpeed
    private(set) var distanceTraveled: CGFloat = 0
    private var nextObstacleDistance: CGFloat = 300
    private var screenWidth: CGFloat = 0
    private var screenHeight: CGFloat = 0
    private var groundY: CGFloat = 0

    private let scoreManager = ScoreManager.shared

    // MARK: - Setup

    func configure(screenSize: CGSize) {
        screenWidth = screenSize.width
        screenHeight = screenSize.height
        groundY = screenHeight - GameConstants.groundHeight
        highScore = scoreManager.highScore
    }

    func startGame() {
        playerY = groundY - GameConstants.playerSize.height
        velocity = 0
        jumpsRemaining = GameConstants.maxJumps
        speed = GameConstants.initialSpeed
        score = 0
        distanceTraveled = 0
        nextObstacleDistance = 300
        obstacles = []
        groundOffset = 0
        isGameOver = false
        isNewHighScore = false
        playerState = .running
        isRunning = true
    }

    // MARK: - Input

    func jump() {
        guard isRunning, !isGameOver else { return }
        guard jumpsRemaining > 0 else { return }

        velocity = GameConstants.jumpVelocity
        jumpsRemaining -= 1
        playerState = .jumping
    }

    // MARK: - Game Loop

    func update() {
        guard isRunning, !isGameOver else { return }

        updatePlayer()
        updateObstacles()
        updateScore()
        updateSpeed()
        updateGround()
        checkCollisions()
    }

    private func updatePlayer() {
        velocity = min(velocity + GameConstants.gravity, GameConstants.maxFallSpeed)
        playerY += velocity

        let floorY = groundY - GameConstants.playerSize.height
        if playerY >= floorY {
            playerY = floorY
            velocity = 0
            jumpsRemaining = GameConstants.maxJumps
            if playerState != .dead {
                playerState = .running
            }
        } else if velocity > 0 {
            playerState = .falling
        }
    }

    private func updateObstacles() {
        // Move existing obstacles
        for i in obstacles.indices {
            obstacles[i].x -= speed
        }

        // Remove off-screen obstacles
        obstacles.removeAll { $0.x + $0.size.width < 0 }

        // Spawn new obstacles
        distanceTraveled += speed
        if distanceTraveled >= nextObstacleDistance {
            spawnObstacle()
            let gap = CGFloat.random(in: GameConstants.minObstacleGap...GameConstants.maxObstacleGap)
            nextObstacleDistance = distanceTraveled + gap
        }
    }

    private func spawnObstacle() {
        let type = ObstacleType.allCases.randomElement() ?? .cactusSmall
        let obstacle = Obstacle(
            x: screenWidth + 50,
            y: groundY,
            type: type
        )
        obstacles.append(obstacle)
    }

    private func updateScore() {
        score += GameConstants.pointsPerFrame
    }

    private func updateSpeed() {
        if speed < GameConstants.maxSpeed {
            speed += GameConstants.speedIncreaseRate
        }
    }

    private func updateGround() {
        groundOffset -= speed
        if groundOffset <= -40 {
            groundOffset += 40
        }
    }

    private func checkCollisions() {
        let playerRect = CGRect(
            x: GameConstants.playerX,
            y: playerY,
            width: GameConstants.playerSize.width,
            height: GameConstants.playerSize.height
        ).insetBy(dx: 6, dy: 4)

        for obstacle in obstacles {
            if playerRect.intersects(obstacle.hitbox) {
                gameOver()
                return
            }
        }
    }

    private func gameOver() {
        isRunning = false
        isGameOver = true
        playerState = .dead
        isNewHighScore = scoreManager.submitScore(score)
        highScore = scoreManager.highScore
    }
}
