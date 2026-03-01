import Foundation

class SaveManager: ObservableObject {
    static let shared = SaveManager()
    private let userDefaults = UserDefaults.standard
    private let petKey = "TamagotchiPet"

    private init() {}

    func savePet(_ pet: Pet) {
        do {
            let encoder = JSONEncoder()
            let data = try encoder.encode(pet)
            userDefaults.set(data, forKey: petKey)
        } catch {
            print("Failed to save pet: \(error)")
        }
    }

    func loadPet() -> Pet? {
        guard let data = userDefaults.data(forKey: petKey) else {
            return nil
        }

        do {
            let decoder = JSONDecoder()
            let pet = try decoder.decode(Pet.self, from: data)
            // Catch up on time that passed while app was closed
            pet.updateStats()
            return pet
        } catch {
            print("Failed to load pet: \(error)")
            return nil
        }
    }

    func deletePet() {
        userDefaults.removeObject(forKey: petKey)
    }
}
