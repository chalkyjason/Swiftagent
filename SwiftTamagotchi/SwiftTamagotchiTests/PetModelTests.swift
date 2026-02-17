import XCTest
@testable import SwiftTamagotchi

/// Tests for Pet stat logic, state machine, and action methods.
final class PetModelTests: XCTestCase {

    // MARK: - Initialisation

    func testNewPet_HasDefaultName() {
        let pet = Pet()
        XCTAssertEqual(pet.name, "Pixel")
    }

    func testNewPet_StartsAtLevelOne() {
        let pet = Pet()
        XCTAssertEqual(pet.level, 1)
    }

    func testNewPet_StartsHappy() {
        let pet = Pet()
        XCTAssertEqual(pet.state, .happy)
    }

    func testNewPet_StatsAreWithinBounds() {
        let pet = Pet()
        XCTAssertGreaterThan(pet.hunger,    0)
        XCTAssertGreaterThan(pet.happiness, 0)
        XCTAssertGreaterThan(pet.health,    0)
        XCTAssertGreaterThan(pet.energy,    0)
        XCTAssertLessThanOrEqual(pet.hunger,    100)
        XCTAssertLessThanOrEqual(pet.happiness, 100)
        XCTAssertLessThanOrEqual(pet.health,    100)
        XCTAssertLessThanOrEqual(pet.energy,    100)
    }

    // MARK: - Feed

    func testFeed_IncreasesHunger() {
        let pet = Pet()
        pet.hunger = 50
        pet.feed()
        XCTAssertGreaterThan(pet.hunger, 50)
    }

    func testFeed_DoesNotExceed100() {
        let pet = Pet()
        pet.hunger = 90
        pet.feed()
        XCTAssertLessThanOrEqual(pet.hunger, 100)
    }

    func testFeed_DoesNothing_WhenDead() {
        let pet = Pet()
        pet.health = 0
        pet.state = .dead
        let hungerBefore = pet.hunger
        pet.feed()
        XCTAssertEqual(pet.hunger, hungerBefore)
    }

    // MARK: - Play

    func testPlay_IncreasesHappiness() {
        let pet = Pet()
        pet.happiness = 40
        pet.energy = 50
        pet.play()
        XCTAssertGreaterThan(pet.happiness, 40)
    }

    func testPlay_DecreasesEnergy() {
        let pet = Pet()
        pet.energy = 50
        pet.play()
        XCTAssertLessThan(pet.energy, 50)
    }

    func testPlay_DoesNothing_WhenInsufficientEnergy() {
        let pet = Pet()
        let happinessBefore = pet.happiness
        pet.energy = 5   // below the 10-energy threshold
        pet.play()
        XCTAssertEqual(pet.happiness, happinessBefore)
    }

    func testPlay_DoesNothing_WhenDead() {
        let pet = Pet()
        pet.health = 0
        pet.state = .dead
        let happinessBefore = pet.happiness
        pet.play()
        XCTAssertEqual(pet.happiness, happinessBefore)
    }

    // MARK: - Give medicine

    func testGiveMedicine_IncreasesHealth() {
        let pet = Pet()
        pet.health = 50
        pet.giveMedicine()
        XCTAssertGreaterThan(pet.health, 50)
    }

    func testGiveMedicine_DoesNotExceed100() {
        let pet = Pet()
        pet.health = 95
        pet.giveMedicine()
        XCTAssertLessThanOrEqual(pet.health, 100)
    }

    func testGiveMedicine_DecreasesHappiness_BecausePetDoesntLikeIt() {
        let pet = Pet()
        let happinessBefore = pet.happiness
        pet.health = 50
        pet.giveMedicine()
        XCTAssertLessThan(pet.happiness, happinessBefore)
    }

    // MARK: - Sleep

    func testSleep_IncreasesEnergy() {
        let pet = Pet()
        pet.energy = 30
        pet.sleep()
        XCTAssertGreaterThan(pet.energy, 30)
    }

    func testSleep_DoesNotExceed100() {
        let pet = Pet()
        pet.energy = 80
        pet.sleep()
        XCTAssertLessThanOrEqual(pet.energy, 100)
    }

    // MARK: - State machine (updateState)

    func testUpdateState_Dead_WhenHealthIsZero() {
        let pet = Pet()
        pet.health = 0
        pet.updateState()
        XCTAssertEqual(pet.state, .dead)
    }

    func testUpdateState_Sick_WhenHealthIsLow() {
        let pet = Pet()
        pet.health = 20
        pet.hunger = 50
        pet.updateState()
        XCTAssertEqual(pet.state, .sick)
    }

    func testUpdateState_Sick_WhenHungerIsVeryLow() {
        let pet = Pet()
        pet.health = 80
        pet.hunger = 10   // < 20 triggers sick
        pet.updateState()
        XCTAssertEqual(pet.state, .sick)
    }

    func testUpdateState_Sleeping_WhenEnergyIsVeryLow() {
        let pet = Pet()
        pet.health = 80
        pet.hunger = 60
        pet.energy = 10   // < 20 triggers sleeping
        pet.updateState()
        XCTAssertEqual(pet.state, .sleeping)
    }

    func testUpdateState_Sad_WhenHappinessIsLow() {
        let pet = Pet()
        pet.health = 80
        pet.hunger = 60
        pet.energy = 50
        pet.happiness = 20   // < 30 triggers sad
        pet.updateState()
        XCTAssertEqual(pet.state, .sad)
    }

    func testUpdateState_Happy_WhenAllStatsAreGood() {
        let pet = Pet()
        pet.health = 90
        pet.hunger = 80
        pet.happiness = 80
        pet.energy = 70
        pet.updateState()
        XCTAssertEqual(pet.state, .happy)
    }

    // MARK: - Computed visual properties

    func testIsHappy_TrueWhenHappinessAbove60() {
        let pet = Pet()
        pet.happiness = 61
        XCTAssertTrue(pet.isHappy)
    }

    func testIsHappy_FalseWhenHappinessAt60OrBelow() {
        let pet = Pet()
        pet.happiness = 60
        XCTAssertFalse(pet.isHappy)
    }

    func testIsSad_TrueWhenHappinessBelow30() {
        let pet = Pet()
        pet.happiness = 29
        XCTAssertTrue(pet.isSad)
    }

    // MARK: - Codable round-trip

    func testPet_CanBeEncodedAndDecoded() throws {
        let original = Pet(name: "Buddy")
        original.hunger = 42
        original.happiness = 75
        original.health = 60
        original.energy = 55
        original.age = 3
        original.level = 2

        let data = try JSONEncoder().encode(original)
        let decoded = try JSONDecoder().decode(Pet.self, from: data)

        XCTAssertEqual(decoded.name,      original.name)
        XCTAssertEqual(decoded.hunger,    original.hunger)
        XCTAssertEqual(decoded.happiness, original.happiness)
        XCTAssertEqual(decoded.health,    original.health)
        XCTAssertEqual(decoded.energy,    original.energy)
        XCTAssertEqual(decoded.age,       original.age)
        XCTAssertEqual(decoded.level,     original.level)
    }
}
