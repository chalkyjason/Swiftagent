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
            print("Pet saved successfully!")
        } catch {
            print("Failed to save pet: \(error)")
        }
    }
    
    func loadPet() -> Pet? {
        guard let data = userDefaults.data(forKey: petKey) else {
            print("No saved pet found, creating new one")
            return nil
        }
        
        do {
            let decoder = JSONDecoder()
            let pet = try decoder.decode(Pet.self, from: data)
            
            // Update stats for time passed while app was closed
            let timePassed = Date().timeIntervalSince(pet.lastUpdate)
            updatePetForTimePassed(pet, timePassed: timePassed)
            
            print("Pet loaded successfully!")
            return pet
        } catch {
            print("Failed to load pet: \(error)")
            return nil
        }
    }
    
    private func updatePetForTimePassed(_ pet: Pet, timePassed: TimeInterval) {
        let hoursPassedAway = timePassed / 3600.0
        
        // Decrease stats based on time away
        pet.hunger = max(0, pet.hunger - (hoursPassedAway * 5))
        pet.happiness = max(0, pet.happiness - (hoursPassedAway * 3))
        pet.energy = max(0, pet.energy - (hoursPassedAway * 2))
        
        // Health decreases if other stats are low
        if pet.hunger < 20 || pet.happiness < 20 {
            pet.health = max(0, pet.health - (hoursPassedAway * 2))
        }
        
        pet.updateState()
    }
    
    func deletePet() {
        userDefaults.removeObject(forKey: petKey)
        print("Pet data deleted")
    }
}
