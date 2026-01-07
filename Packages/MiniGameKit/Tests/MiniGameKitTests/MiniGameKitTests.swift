import XCTest
@testable import MiniGameKit

final class MiniGameKitTests: XCTestCase {

    // MARK: - GameState Tests

    func testGameStatePlayable() {
        XCTAssertFalse(GameState.ready.isPlayable)
        XCTAssertTrue(GameState.playing.isPlayable)
        XCTAssertFalse(GameState.paused.isPlayable)
        XCTAssertFalse(GameState.gameOver(score: 100).isPlayable)
        XCTAssertTrue(GameState.countdown(3).isPlayable)
    }

    func testGameStateAcceptsInput() {
        XCTAssertFalse(GameState.ready.acceptsInput)
        XCTAssertTrue(GameState.playing.acceptsInput)
        XCTAssertFalse(GameState.paused.acceptsInput)
        XCTAssertFalse(GameState.gameOver(score: 100).acceptsInput)
        XCTAssertFalse(GameState.countdown(3).acceptsInput)
    }

    func testGameStateEquality() {
        XCTAssertEqual(GameState.ready, GameState.ready)
        XCTAssertEqual(GameState.playing, GameState.playing)
        XCTAssertEqual(GameState.gameOver(score: 100), GameState.gameOver(score: 100))
        XCTAssertNotEqual(GameState.gameOver(score: 100), GameState.gameOver(score: 200))
        XCTAssertEqual(GameState.countdown(3), GameState.countdown(3))
        XCTAssertNotEqual(GameState.countdown(3), GameState.countdown(2))
    }

    // MARK: - GameResult Tests

    func testGameResultCreation() {
        let result = GameResult(
            score: 1000,
            duration: 120.5,
            achievementsUnlocked: ["first_win", "high_scorer"],
            isHighScore: true
        )

        XCTAssertEqual(result.score, 1000)
        XCTAssertEqual(result.duration, 120.5)
        XCTAssertEqual(result.achievementsUnlocked.count, 2)
        XCTAssertTrue(result.isHighScore)
    }

    func testGameResultDefaults() {
        let result = GameResult(score: 500, duration: 60)

        XCTAssertEqual(result.score, 500)
        XCTAssertEqual(result.duration, 60)
        XCTAssertTrue(result.achievementsUnlocked.isEmpty)
        XCTAssertFalse(result.isHighScore)
    }

    // MARK: - GameLoop Tests

    @MainActor
    func testGameLoopInitialState() {
        let loop = GameLoop()

        XCTAssertEqual(loop.state, .ready)
        XCTAssertEqual(loop.score, 0)
        XCTAssertEqual(loop.elapsedTime, 0)
        XCTAssertFalse(loop.isRunning)
    }

    @MainActor
    func testGameLoopTargetFPS() {
        let loop30 = GameLoop(targetFPS: 30)
        let loop60 = GameLoop(targetFPS: 60)

        XCTAssertEqual(loop30.targetFPS, 30)
        XCTAssertEqual(loop60.targetFPS, 60)
    }

    @MainActor
    func testGameLoopScoring() {
        let loop = GameLoop()

        loop.addScore(100)
        XCTAssertEqual(loop.score, 100)

        loop.addScore(50)
        XCTAssertEqual(loop.score, 150)

        loop.setScore(200)
        XCTAssertEqual(loop.score, 200)
    }

    @MainActor
    func testGameLoopHighScore() {
        let loop = GameLoop()

        loop.setScore(100)
        loop.stop()
        XCTAssertEqual(loop.highScore, 100)

        loop.reset()
        loop.setScore(50)
        loop.stop()
        XCTAssertEqual(loop.highScore, 100) // High score should remain

        loop.reset()
        loop.setScore(150)
        loop.stop()
        XCTAssertEqual(loop.highScore, 150) // New high score
    }

    @MainActor
    func testGameLoopReset() {
        let loop = GameLoop()

        loop.setScore(500)
        loop.reset()

        XCTAssertEqual(loop.state, .ready)
        XCTAssertEqual(loop.score, 0)
        XCTAssertEqual(loop.elapsedTime, 0)
    }

    // MARK: - GameTimer Tests

    @MainActor
    func testGameTimerCountUp() {
        let timer = GameTimer(mode: .countUp)

        XCTAssertEqual(timer.timeRemaining, 0)
        XCTAssertFalse(timer.isExpired)
    }

    @MainActor
    func testGameTimerCountDown() {
        let timer = GameTimer(mode: .countDown(from: 60))

        XCTAssertEqual(timer.timeRemaining, 60)
        XCTAssertFalse(timer.isExpired)
    }

    @MainActor
    func testGameTimerFormat() {
        let timer = GameTimer(mode: .countDown(from: 125.5))

        // 125.5 seconds = 2 minutes, 5.5 seconds
        XCTAssertTrue(timer.formattedTime.contains("02:05"))
    }

    @MainActor
    func testGameTimerReset() {
        let timer = GameTimer(mode: .countDown(from: 30))

        // Simulate some time passing (in a real test you'd use expectations)
        timer.reset()

        XCTAssertEqual(timer.timeRemaining, 30)
        XCTAssertFalse(timer.isExpired)
    }

    // MARK: - GameLifecycleObserver Tests

    @MainActor
    func testLifecycleObserverInitialState() {
        let observer = GameLifecycleObserver()

        XCTAssertFalse(observer.shouldPause)
        XCTAssertTrue(observer.isInForeground)
    }

    @MainActor
    func testLifecycleObserverScenePhaseUpdate() {
        let observer = GameLifecycleObserver()

        observer.update(scenePhase: .background)
        XCTAssertTrue(observer.shouldPause)
        XCTAssertFalse(observer.isInForeground)

        observer.acknowledgeResume()
        XCTAssertFalse(observer.shouldPause)
    }
}

// MARK: - Mock MiniGame for Testing

struct MockMiniGame: MiniGame {
    let id = UUID()
    let title: String
    let iconName: String

    var startCalled = false
    var pauseCalled = false
    var resumeCalled = false
    var endCalled = false
    var endScore: Int?

    init(title: String = "Mock Game", iconName: String = "gamecontroller") {
        self.title = title
        self.iconName = iconName
    }

    @MainActor
    func makeGameView() -> AnyView {
        AnyView(Text("Mock Game View"))
    }

    func onStart() {
        // Would set startCalled = true in a mutable version
    }

    func onPause() {
        // Would set pauseCalled = true
    }

    func onResume() {
        // Would set resumeCalled = true
    }

    func onEnd(score: Int) {
        // Would set endCalled = true, endScore = score
    }
}

final class MiniGameProtocolTests: XCTestCase {

    func testMiniGameDefaultValues() {
        let game = MockMiniGame()

        XCTAssertEqual(game.description, "")
        XCTAssertEqual(game.difficulty, 1)
        XCTAssertEqual(game.estimatedDuration, 60)
    }

    func testMiniGameCustomValues() {
        let game = MockMiniGame(title: "Custom Game", iconName: "star")

        XCTAssertEqual(game.title, "Custom Game")
        XCTAssertEqual(game.iconName, "star")
    }
}
