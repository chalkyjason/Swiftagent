import XCTest
@testable import CoreUI

final class CoreUITests: XCTestCase {

    // MARK: - MenuItem Tests

    func testMenuItemCreation() {
        var actionCalled = false
        let item = MenuItem(
            id: "test",
            title: "Test Item",
            subtitle: "Test Subtitle",
            icon: "star.fill",
            style: .primary,
            isEnabled: true,
            badge: "NEW",
            action: { actionCalled = true }
        )

        XCTAssertEqual(item.id, "test")
        XCTAssertEqual(item.title, "Test Item")
        XCTAssertEqual(item.subtitle, "Test Subtitle")
        XCTAssertEqual(item.icon, "star.fill")
        XCTAssertEqual(item.style, .primary)
        XCTAssertTrue(item.isEnabled)
        XCTAssertEqual(item.badge, "NEW")

        item.action()
        XCTAssertTrue(actionCalled)
    }

    func testMenuItemStyleEquality() {
        XCTAssertEqual(MenuItemStyle.primary, MenuItemStyle.primary)
        XCTAssertNotEqual(MenuItemStyle.primary, MenuItemStyle.standard)
    }

    func testMenuSectionCreation() {
        let items = [
            MenuItem(id: "1", title: "Item 1", action: {}),
            MenuItem(id: "2", title: "Item 2", action: {})
        ]

        let section = MenuSection(
            id: "section1",
            header: "Test Section",
            items: items
        )

        XCTAssertEqual(section.id, "section1")
        XCTAssertEqual(section.header, "Test Section")
        XCTAssertEqual(section.items.count, 2)
    }

    // MARK: - MenuBuilder Tests

    func testMainMenuBuilder() {
        var playCount = 0
        var settingsCount = 0

        let items = MenuBuilder.mainMenu(
            onPlay: { playCount += 1 },
            onSettings: { settingsCount += 1 }
        )

        XCTAssertGreaterThanOrEqual(items.count, 2)

        // Find and test play item
        if let playItem = items.first(where: { $0.id == "play" }) {
            XCTAssertEqual(playItem.style, .primary)
            playItem.action()
            XCTAssertEqual(playCount, 1)
        } else {
            XCTFail("Play item not found")
        }

        // Find and test settings item
        if let settingsItem = items.first(where: { $0.id == "settings" }) {
            settingsItem.action()
            XCTAssertEqual(settingsCount, 1)
        } else {
            XCTFail("Settings item not found")
        }
    }

    func testPauseMenuBuilder() {
        let items = MenuBuilder.pauseMenu(
            onResume: {},
            onSettings: {},
            onQuit: {}
        )

        XCTAssertEqual(items.count, 3)

        let quitItem = items.first(where: { $0.id == "quit" })
        XCTAssertNotNil(quitItem)
        XCTAssertEqual(quitItem?.style, .destructive)
    }

    func testGameOverMenuBuilder() {
        let items = MenuBuilder.gameOverMenu(
            score: 1000,
            onPlayAgain: {},
            onMainMenu: {},
            onShare: {}
        )

        XCTAssertEqual(items.count, 3)

        let shareItem = items.first(where: { $0.id == "share" })
        XCTAssertNotNil(shareItem)
        XCTAssertTrue(shareItem?.subtitle?.contains("1000") ?? false)
    }

    // MARK: - MenuTheme Tests

    func testDefaultTheme() {
        let theme = MenuTheme.default
        XCTAssertEqual(theme.itemCornerRadius, 12)
        XCTAssertEqual(theme.itemSpacing, 12)
    }

    func testSciFiTheme() {
        let theme = MenuTheme.sciFi
        XCTAssertEqual(theme.itemBorderWidth, 1)
        XCTAssertEqual(theme.itemCornerRadius, 4)
    }

    func testCustomTheme() {
        let theme = MenuTheme(
            backgroundColor: .red,
            itemCornerRadius: 20,
            itemSpacing: 8
        )

        XCTAssertEqual(theme.itemCornerRadius, 20)
        XCTAssertEqual(theme.itemSpacing, 8)
    }

    // MARK: - GameDifficulty Tests

    func testGameDifficultyDisplayNames() {
        XCTAssertEqual(GameDifficulty.easy.displayName, "Easy")
        XCTAssertEqual(GameDifficulty.normal.displayName, "Normal")
        XCTAssertEqual(GameDifficulty.hard.displayName, "Hard")
        XCTAssertEqual(GameDifficulty.expert.displayName, "Expert")
    }

    func testGameDifficultyMultipliers() {
        XCTAssertEqual(GameDifficulty.easy.multiplier, 0.75)
        XCTAssertEqual(GameDifficulty.normal.multiplier, 1.0)
        XCTAssertEqual(GameDifficulty.hard.multiplier, 1.5)
        XCTAssertEqual(GameDifficulty.expert.multiplier, 2.0)
    }

    // MARK: - ColorBlindMode Tests

    func testColorBlindModeDisplayNames() {
        XCTAssertEqual(ColorBlindMode.none.displayName, "None")
        XCTAssertEqual(ColorBlindMode.protanopia.displayName, "Protanopia (Red-Blind)")
        XCTAssertEqual(ColorBlindMode.deuteranopia.displayName, "Deuteranopia (Green-Blind)")
    }

    // MARK: - GameDestination Tests

    func testGameDestinationHashable() {
        let dest1 = GameDestination.gameplay
        let dest2 = GameDestination.gameplay
        let dest3 = GameDestination.settings

        XCTAssertEqual(dest1, dest2)
        XCTAssertNotEqual(dest1, dest3)
    }

    func testGameOverDestination() {
        let dest1 = GameDestination.gameOver(score: 100)
        let dest2 = GameDestination.gameOver(score: 100)
        let dest3 = GameDestination.gameOver(score: 200)

        XCTAssertEqual(dest1, dest2)
        XCTAssertNotEqual(dest1, dest3)
    }

    // MARK: - DefaultGameCoordinator Tests

    @MainActor
    func testCoordinatorInitialState() {
        let coordinator = DefaultGameCoordinator()
        XCTAssertTrue(coordinator.path.isEmpty)
    }

    @MainActor
    func testCoordinatorNavigation() {
        let coordinator = DefaultGameCoordinator()

        coordinator.startGame()
        XCTAssertEqual(coordinator.path.count, 1)

        coordinator.showSettings()
        XCTAssertEqual(coordinator.path.count, 2)

        coordinator.goBack()
        XCTAssertEqual(coordinator.path.count, 1)

        coordinator.popToRoot()
        XCTAssertTrue(coordinator.path.isEmpty)
    }

    @MainActor
    func testCoordinatorShowMenu() {
        let coordinator = DefaultGameCoordinator()

        coordinator.startGame()
        coordinator.showSettings()
        XCTAssertEqual(coordinator.path.count, 2)

        coordinator.showMenu()
        XCTAssertTrue(coordinator.path.isEmpty)
    }

    @MainActor
    func testCoordinatorCallback() {
        let coordinator = DefaultGameCoordinator()
        var lastDestination: GameDestination?

        coordinator.onNavigationChange = { destination in
            lastDestination = destination
        }

        coordinator.startGame()
        XCTAssertEqual(lastDestination, .gameplay)

        coordinator.showSettings()
        XCTAssertEqual(lastDestination, .settings)
    }

    // MARK: - SettingsSection Tests

    func testSettingsSectionAllCases() {
        let allSections = SettingsSection.allCases
        XCTAssertEqual(allSections.count, 5)
        XCTAssertTrue(allSections.contains(.audio))
        XCTAssertTrue(allSections.contains(.gameplay))
        XCTAssertTrue(allSections.contains(.feedback))
        XCTAssertTrue(allSections.contains(.accessibility))
        XCTAssertTrue(allSections.contains(.developer))
    }
}
