import Foundation
import SwiftUI

class Pet: ObservableObject, Codable {
    @Published var name: String
    @Published var hunger: Double
    @Published var happiness: Double
    @Published var health: Double
    @Published var energy: Double
    @Published var age: Int
    @Published var level: Int
    @Published var state: PetState
    @Published var lastUpdate: Date
    @Published var birthTime: Date
    
    // Animation properties
    @Published var animationOffset: CGFloat = 0
    @Published var animationFrame: Int = 0
    
    enum CodingKeys: String, CodingKey {
        case name, hunger, happiness, health, energy, age, level, state, lastUpdate, birthTime
    }
    
    init(name: String = "Pixel") {
        self.name = name
        self.hunger = 80.0
        self.happiness = 80.0
        self.health = 90.0
        self.energy = 70.0
        self.age = 0
        self.level = 1
        self.state = .happy
        self.lastUpdate = Date()
        self.birthTime = Date()
    }
    
    required init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        name = try container.decode(String.self, forKey: .name)
        hunger = try container.decode(Double.self, forKey: .hunger)
        happiness = try container.decode(Double.self, forKey: .happiness)
        health = try container.decode(Double.self, forKey: .health)
        energy = try container.decode(Double.self, forKey: .energy)
        age = try container.decode(Int.self, forKey: .age)
        level = try container.decode(Int.self, forKey: .level)
        state = try container.decode(PetState.self, forKey: .state)
        lastUpdate = try container.decode(Date.self, forKey: .lastUpdate)
        birthTime = try container.decode(Date.self, forKey: .birthTime)
    }
    
    func encode(to encoder: Encoder) throws {
        var container = encoder.container(keyedBy: CodingKeys.self)
        try container.encode(name, forKey: .name)
        try container.encode(hunger, forKey: .hunger)
        try container.encode(happiness, forKey: .happiness)
        try container.encode(health, forKey: .health)
        try container.encode(energy, forKey: .energy)
        try container.encode(age, forKey: .age)
        try container.encode(level, forKey: .level)
        try container.encode(state, forKey: .state)
        try container.encode(lastUpdate, forKey: .lastUpdate)
        try container.encode(birthTime, forKey: .birthTime)
    }
    
    // MARK: - Stat Management
    
    func updateStats() {
        let currentTime = Date()
        let timePassed = currentTime.timeIntervalSince(lastUpdate)
        
        // Update stats based on time passed (in minutes)
        let minutesPassed = timePassed / 60.0
        
        if minutesPassed >= 1.0 {
            hunger = max(0, hunger - minutesPassed)
            happiness = max(0, happiness - (minutesPassed * 0.5))
            energy = max(0, energy - (minutesPassed * 0.3))
            
            // Health decreases if other stats are low
            if hunger < 20 || happiness < 20 {
                health = max(0, health - minutesPassed)
            } else if health < 100 {
                health = min(100, health + (minutesPassed * 0.1))
            }
            
            // Update age and level
            let hoursAlive = currentTime.timeIntervalSince(birthTime) / 3600.0
            age = Int(hoursAlive)
            level = min(10, age / 24 + 1) // Level up every day
            
            lastUpdate = currentTime
            updateState()
        }
    }
    
    func updateState() {
        if health <= 0 {
            state = .dead
        } else if health < 30 || hunger < 20 {
            state = .sick
        } else if energy < 20 {
            state = .sleeping
        } else if happiness < 30 {
            state = .sad
        } else {
            state = .happy
        }
    }
    
    // MARK: - Actions
    
    func feed() {
        guard state != .dead else { return }
        
        if hunger < 100 {
            hunger = min(100, hunger + 25)
            happiness = min(100, happiness + 5)
            state = .eating
            
            // Reset state after a delay
            DispatchQueue.main.asyncAfter(deadline: .now() + 2) {
                self.updateState()
            }
        }
    }
    
    func play() {
        guard state != .dead else { return }
        
        if energy > 10 {
            happiness = min(100, happiness + 20)
            energy = max(0, energy - 15)
            state = .playing
            
            // Reset state after a delay
            DispatchQueue.main.asyncAfter(deadline: .now() + 2) {
                self.updateState()
            }
        }
    }
    
    func giveMedicine() {
        guard state != .dead else { return }
        
        if health < 100 {
            health = min(100, health + 30)
            happiness = max(0, happiness - 5) // Pet doesn't like medicine
            updateState()
        }
    }
    
    func sleep() {
        guard state != .dead else { return }
        
        energy = min(100, energy + 40)
        state = .sleeping
        
        // Reset state after a delay
        DispatchQueue.main.asyncAfter(deadline: .now() + 3) {
            self.updateState()
        }
    }
    
    // MARK: - Visual Properties
    
    var petColor: Color {
        switch state {
        case .happy:
            return .green
        case .sad:
            return .blue
        case .sick:
            return .purple
        case .sleeping:
            return .gray
        case .dead:
            return .red
        case .eating:
            return .orange
        case .playing:
            return .yellow
        }
    }
    
    var eyeColor: Color {
        switch state {
        case .sleeping:
            return .gray
        case .dead:
            return .red
        default:
            return .black
        }
    }
    
    var isHappy: Bool {
        return happiness > 60
    }
    
    var isSad: Bool {
        return happiness < 30
    }
}
