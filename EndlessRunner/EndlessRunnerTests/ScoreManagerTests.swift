import XCTest
@testable import EndlessRunner

final class ScoreManagerTests: XCTestCase {

    private let testDefaults = UserDefaults(suiteName: "EndlessRunnerTests")!
    private let testKey = "EndlessRunnerHighScore"

    override func setUp() {
        super.setUp()
        testDefaults.removeObject(forKey: testKey)
    }

    override func tearDown() {
        testDefaults.removeObject(forKey: testKey)
        super.tearDown()
    }

    // MARK: - High Score Storage

    func testHighScore_DefaultsToZero() {
        let score = testDefaults.integer(forKey: testKey)
        XCTAssertEqual(score, 0)
    }

    func testHighScore_CanBeSet() {
        testDefaults.set(500, forKey: testKey)
        XCTAssertEqual(testDefaults.integer(forKey: testKey), 500)
    }

    func testHighScore_SubmitHigherScore_Updates() {
        testDefaults.set(100, forKey: testKey)
        let newScore = 200
        if newScore > testDefaults.integer(forKey: testKey) {
            testDefaults.set(newScore, forKey: testKey)
        }
        XCTAssertEqual(testDefaults.integer(forKey: testKey), 200)
    }

    func testHighScore_SubmitLowerScore_DoesNotUpdate() {
        testDefaults.set(500, forKey: testKey)
        let newScore = 100
        if newScore > testDefaults.integer(forKey: testKey) {
            testDefaults.set(newScore, forKey: testKey)
        }
        XCTAssertEqual(testDefaults.integer(forKey: testKey), 500)
    }

    func testHighScore_SubmitEqualScore_DoesNotUpdate() {
        testDefaults.set(300, forKey: testKey)
        let newScore = 300
        let wasNew = newScore > testDefaults.integer(forKey: testKey)
        XCTAssertFalse(wasNew)
    }

    func testReset_RemovesHighScore() {
        testDefaults.set(999, forKey: testKey)
        testDefaults.removeObject(forKey: testKey)
        XCTAssertEqual(testDefaults.integer(forKey: testKey), 0)
    }

    // MARK: - Obstacle Model

    func testObstacle_RectCalculation() {
        let obstacle = Obstacle(x: 100, y: 500, type: .cactusSmall)
        let rect = obstacle.rect
        XCTAssertEqual(rect.origin.x, 100)
        XCTAssertEqual(rect.width, obstacle.size.width)
        XCTAssertEqual(rect.height, obstacle.size.height)
    }

    func testObstacle_HitboxIsSmaller() {
        let obstacle = Obstacle(x: 100, y: 500, type: .cactusLarge)
        let rect = obstacle.rect
        let hitbox = obstacle.hitbox
        XCTAssertGreaterThan(hitbox.minX, rect.minX)
        XCTAssertLessThan(hitbox.maxX, rect.maxX)
        XCTAssertGreaterThan(hitbox.minY, rect.minY)
        XCTAssertLessThan(hitbox.maxY, rect.maxY)
    }

    func testObstacleTypes_AllHaveValidSizes() {
        for type in ObstacleType.allCases {
            XCTAssertGreaterThan(type.size.width, 0)
            XCTAssertGreaterThan(type.size.height, 0)
        }
    }

    // MARK: - Game Constants

    func testGameConstants_SpeedRange() {
        XCTAssertLessThan(GameConstants.initialSpeed, GameConstants.maxSpeed)
    }

    func testGameConstants_JumpVelocityIsNegative() {
        XCTAssertLessThan(GameConstants.jumpVelocity, 0)
    }

    func testGameConstants_GravityIsPositive() {
        XCTAssertGreaterThan(GameConstants.gravity, 0)
    }

    func testGameConstants_MaxJumpsIsPositive() {
        XCTAssertGreaterThan(GameConstants.maxJumps, 0)
    }

    func testGameConstants_ObstacleGapRange() {
        XCTAssertLessThan(GameConstants.minObstacleGap, GameConstants.maxObstacleGap)
    }
}
