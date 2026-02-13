import Foundation
import Combine

class GameLogic: ObservableObject {
    @Published var pet: Pet
    @Published var gameMessage: String = ""
    @Published var showMessage: Bool = false
    
    private var gameTimer: Timer?
    private var saveTimer: Timer?
    private let saveManager = SaveManager.shared
    
    init() {
        // Try to load existing pet, or create new one
        if let savedPet = saveManager.loadPet() {
            self.pet = savedPet
        } else {
            self.pet = Pet()
            saveManager.savePet(pet)
        }
        
        startGameTimers()
    }
    
    deinit {
        stopGameTimers()
    }
    
    // MARK: - Game Timers
    
    private func startGameTimers() {
        // Update pet stats every minute
        gameTimer = Timer.scheduledTimer(withTimeInterval: 60.0, repeats: true) { _ in
            self.pet.updateStats()
        }
        
        // Auto-save every 5 minutes
        saveTimer = Timer.scheduledTimer(withTimeInterval: 300.0, repeats: true) { _ in
            self.savePet()
        }
    }
    
    private func stopGameTimers() {
        gameTimer?.invalidate()
        saveTimer?.invalidate()
    }
    
    // MARK: - Game Actions
    
    func savePet() {
        saveManager.savePet(pet)
        showGameMessage("Game saved!")
    }
    
    func resetPet() {
        saveManager.deletePet()
        pet = Pet()
        saveManager.savePet(pet)
        showGameMessage("New pet created!")
    }
    
    func showGameMessage(_ message: String) {
        gameMessage = message
        showMessage = true
        
        DispatchQueue.main.asyncAfter(deadline: .now() + 2) {
            self.showMessage = false
        }
    }
    
    // MARK: - App Lifecycle
    
    func pauseGame() {
        stopGameTimers()
        savePet()
    }
    
    func resumeGame() {
        pet.updateStats()
        startGameTimers()
    }
}
