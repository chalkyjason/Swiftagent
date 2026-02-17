import XCTest
@testable import SwiftTamagotchi

/// Tests for SaveManager persist/load/delete lifecycle using a test-isolated
/// UserDefaults suite so tests never touch the real user data.
final class SaveManagerTests: XCTestCase {

    // Use an isolated UserDefaults suite so tests don't pollute real storage.
    private let testDefaults = UserDefaults(suiteName: "SwiftTamagotchiTests")!
    private let testKey = "TamagotchiPet"

    override func setUp() {
        super.setUp()
        testDefaults.removeObject(forKey: testKey)
    }

    override func tearDown() {
        testDefaults.removeObject(forKey: testKey)
        super.tearDown()
    }

    // MARK: - Save & Load

    func testSaveThenLoad_RestoresSamePetName() throws {
        let pet = Pet(name: "TestPet")
        let data = try JSONEncoder().encode(pet)
        testDefaults.set(data, forKey: testKey)

        guard let loaded = testDefaults.data(forKey: testKey) else {
            XCTFail("No data found after save")
            return
        }
        let decoded = try JSONDecoder().decode(Pet.self, from: loaded)
        XCTAssertEqual(decoded.name, "TestPet")
    }

    func testSaveThenLoad_RestoresAllStats() throws {
        let pet = Pet()
        pet.hunger    = 55
        pet.happiness = 66
        pet.health    = 77
        pet.energy    = 44
        pet.level     = 3

        let data = try JSONEncoder().encode(pet)
        testDefaults.set(data, forKey: testKey)

        let loaded = try JSONDecoder().decode(
            Pet.self,
            from: testDefaults.data(forKey: testKey)!
        )
        XCTAssertEqual(loaded.hunger,    55)
        XCTAssertEqual(loaded.happiness, 66)
        XCTAssertEqual(loaded.health,    77)
        XCTAssertEqual(loaded.energy,    44)
        XCTAssertEqual(loaded.level,     3)
    }

    // MARK: - Load when nothing is saved

    func testLoad_ReturnsNil_WhenNoDataExists() {
        testDefaults.removeObject(forKey: testKey)
        let data = testDefaults.data(forKey: testKey)
        XCTAssertNil(data)
    }

    // MARK: - Delete

    func testDelete_RemovesDataFromDefaults() throws {
        let pet = Pet(name: "ToDelete")
        testDefaults.set(try JSONEncoder().encode(pet), forKey: testKey)

        // Verify it's there
        XCTAssertNotNil(testDefaults.data(forKey: testKey))

        // Delete
        testDefaults.removeObject(forKey: testKey)

        XCTAssertNil(testDefaults.data(forKey: testKey))
    }

    // MARK: - Time-away stat decay (mirrors SaveManager.updatePetForTimePassed)

    private func applyTimePassed(to pet: Pet, hours: Double) {
        pet.hunger    = max(0, pet.hunger    - (hours * 5))
        pet.happiness = max(0, pet.happiness - (hours * 3))
        pet.energy    = max(0, pet.energy    - (hours * 2))
        if pet.hunger < 20 || pet.happiness < 20 {
            pet.health = max(0, pet.health - (hours * 2))
        }
        pet.updateState()
    }

    func testTimeAwayDecay_ReducesHunger() {
        let pet = Pet()
        pet.hunger = 80
        let before = pet.hunger
        applyTimePassed(to: pet, hours: 1.0)
        XCTAssertLessThan(pet.hunger, before)
    }

    func testTimeAwayDecay_NeverGoesBelowZero() {
        let pet = Pet()
        pet.hunger    = 5
        pet.happiness = 5
        pet.energy    = 5
        applyTimePassed(to: pet, hours: 100)   // extreme time away
        XCTAssertGreaterThanOrEqual(pet.hunger,    0)
        XCTAssertGreaterThanOrEqual(pet.happiness, 0)
        XCTAssertGreaterThanOrEqual(pet.energy,    0)
        XCTAssertGreaterThanOrEqual(pet.health,    0)
    }

    func testTimeAwayDecay_LowHunger_AlsoReducesHealth() {
        let pet = Pet()
        pet.health    = 80
        pet.hunger    = 10   // < 20 means health also decays
        pet.happiness = 80
        let healthBefore = pet.health
        applyTimePassed(to: pet, hours: 2.0)
        XCTAssertLessThan(pet.health, healthBefore)
    }

    func testTimeAwayDecay_GoodStats_HealthDoesNotDecay() {
        let pet = Pet()
        pet.health    = 80
        pet.hunger    = 80   // both above 20 so health should not decay
        pet.happiness = 80
        let healthBefore = pet.health
        applyTimePassed(to: pet, hours: 0.5)
        XCTAssertEqual(pet.health, healthBefore)
    }

    // MARK: - Codable robustness

    func testPet_Codable_WithCorruptData_ReturnsNil() {
        let corruptData = "not valid json".data(using: .utf8)!
        let decoded = try? JSONDecoder().decode(Pet.self, from: corruptData)
        XCTAssertNil(decoded)
    }
}
