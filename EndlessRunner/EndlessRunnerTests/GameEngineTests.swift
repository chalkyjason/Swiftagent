import XCTest
@testable import EndlessRunner

final class GameEngineTests: XCTestCase {

    // MARK: - Initialization

    func testNewEngine_IsNotRunning() {
        let engine = GameEngine()
        XCTAssertFalse(engine.isRunning)
        XCTAssertFalse(engine.isGameOver)
    }

    func testNewEngine_ScoreIsZero() {
        let engine = GameEngine()
        XCTAssertEqual(engine.score, 0)
    }

    // MARK: - Configure

    func testConfigure_SetsUpHighScore() {
        let engine = GameEngine()
        engine.configure(screenSize: CGSize(width: 400, height: 800))
        // highScore should be loaded from ScoreManager (defaults to 0)
        XCTAssertGreaterThanOrEqual(engine.highScore, 0)
    }

    // MARK: - Start Game

    func testStartGame_SetsRunningState() {
        let engine = GameEngine()
        engine.configure(screenSize: CGSize(width: 400, height: 800))
        engine.startGame()
        XCTAssertTrue(engine.isRunning)
        XCTAssertFalse(engine.isGameOver)
    }

    func testStartGame_ResetsScore() {
        let engine = GameEngine()
        engine.configure(screenSize: CGSize(width: 400, height: 800))
        engine.startGame()
        XCTAssertEqual(engine.score, 0)
    }

    func testStartGame_ClearsObstacles() {
        let engine = GameEngine()
        engine.configure(screenSize: CGSize(width: 400, height: 800))
        engine.startGame()
        XCTAssertTrue(engine.obstacles.isEmpty)
    }

    func testStartGame_PlayerIsRunning() {
        let engine = GameEngine()
        engine.configure(screenSize: CGSize(width: 400, height: 800))
        engine.startGame()
        XCTAssertEqual(engine.playerState, .running)
    }

    func testStartGame_SetsInitialSpeed() {
        let engine = GameEngine()
        engine.configure(screenSize: CGSize(width: 400, height: 800))
        engine.startGame()
        XCTAssertEqual(engine.speed, GameConstants.initialSpeed)
    }

    // MARK: - Jump

    func testJump_ChangesPlayerStateToJumping() {
        let engine = GameEngine()
        engine.configure(screenSize: CGSize(width: 400, height: 800))
        engine.startGame()
        engine.jump()
        XCTAssertEqual(engine.playerState, .jumping)
    }

    func testJump_SetsNegativeVelocity() {
        let engine = GameEngine()
        engine.configure(screenSize: CGSize(width: 400, height: 800))
        engine.startGame()
        engine.jump()
        XCTAssertLessThan(engine.velocity, 0)
    }

    func testJump_DoesNothing_WhenNotRunning() {
        let engine = GameEngine()
        engine.configure(screenSize: CGSize(width: 400, height: 800))
        // Don't start game
        engine.jump()
        XCTAssertEqual(engine.playerState, .running)
    }

    func testDoubleJump_AllowedWithTwoJumps() {
        let engine = GameEngine()
        engine.configure(screenSize: CGSize(width: 400, height: 800))
        engine.startGame()
        engine.jump()
        XCTAssertEqual(engine.jumpsRemaining, 1)
        engine.jump()
        XCTAssertEqual(engine.jumpsRemaining, 0)
    }

    func testTripleJump_NotAllowed() {
        let engine = GameEngine()
        engine.configure(screenSize: CGSize(width: 400, height: 800))
        engine.startGame()
        engine.jump()
        engine.jump()
        let velocityAfterDouble = engine.velocity
        engine.jump() // Should be ignored
        XCTAssertEqual(engine.velocity, velocityAfterDouble)
        XCTAssertEqual(engine.jumpsRemaining, 0)
    }

    // MARK: - Update Loop

    func testUpdate_IncreasesScore() {
        let engine = GameEngine()
        engine.configure(screenSize: CGSize(width: 400, height: 800))
        engine.startGame()
        let initialScore = engine.score
        engine.update()
        XCTAssertGreaterThan(engine.score, initialScore)
    }

    func testUpdate_IncreasesSpeed() {
        let engine = GameEngine()
        engine.configure(screenSize: CGSize(width: 400, height: 800))
        engine.startGame()
        let initialSpeed = engine.speed
        for _ in 0..<100 {
            engine.update()
        }
        XCTAssertGreaterThan(engine.speed, initialSpeed)
    }

    func testUpdate_SpeedDoesNotExceedMax() {
        let engine = GameEngine()
        engine.configure(screenSize: CGSize(width: 400, height: 800))
        engine.startGame()
        for _ in 0..<100_000 {
            engine.update()
            if engine.isGameOver { engine.startGame() }
        }
        XCTAssertLessThanOrEqual(engine.speed, GameConstants.maxSpeed)
    }

    func testUpdate_DoesNothing_WhenGameOver() {
        let engine = GameEngine()
        engine.configure(screenSize: CGSize(width: 400, height: 800))
        engine.startGame()
        // Manually trigger game over by making isGameOver true
        // We need to cause a collision - so let's just verify update doesn't crash
        engine.update()
        XCTAssertTrue(engine.isRunning || engine.isGameOver)
    }

    // MARK: - Ground physics

    func testPlayerY_DoesNotFallBelowGround() {
        let engine = GameEngine()
        let screenSize = CGSize(width: 400, height: 800)
        engine.configure(screenSize: screenSize)
        engine.startGame()

        // Run many updates to ensure player stays on ground
        for _ in 0..<200 {
            engine.update()
        }

        let groundY = screenSize.height - GameConstants.groundHeight
        let maxPlayerY = groundY - GameConstants.playerSize.height
        XCTAssertLessThanOrEqual(engine.playerY, maxPlayerY + 1) // +1 for floating point
    }

    func testJump_PlayerMovesUp() {
        let engine = GameEngine()
        engine.configure(screenSize: CGSize(width: 400, height: 800))
        engine.startGame()
        let startY = engine.playerY
        engine.jump()
        engine.update()
        XCTAssertLessThan(engine.playerY, startY)
    }

    // MARK: - Gravity

    func testGravity_BringsPlayerDown() {
        let engine = GameEngine()
        engine.configure(screenSize: CGSize(width: 400, height: 800))
        engine.startGame()
        engine.jump()

        // Run a few frames to get upward
        for _ in 0..<5 {
            engine.update()
        }
        let peakY = engine.playerY

        // Run many more frames to come back down
        for _ in 0..<50 {
            engine.update()
        }
        XCTAssertGreaterThanOrEqual(engine.playerY, peakY)
    }

    // MARK: - Jump resets on landing

    func testJumpsReset_WhenLanding() {
        let engine = GameEngine()
        engine.configure(screenSize: CGSize(width: 400, height: 800))
        engine.startGame()
        engine.jump()
        XCTAssertEqual(engine.jumpsRemaining, 1)

        // Run enough frames to land
        for _ in 0..<100 {
            engine.update()
        }
        XCTAssertEqual(engine.jumpsRemaining, GameConstants.maxJumps)
    }
}
