import Foundation

enum PetState: String, CaseIterable, Codable {
    case happy = "happy"
    case sad = "sad"
    case sleeping = "sleeping"
    case eating = "eating"
    case playing = "playing"
    case sick = "sick"
    case dead = "dead"
    
    var displayName: String {
        return rawValue.capitalized
    }
    
    var emoji: String {
        switch self {
        case .happy: return "😊"
        case .sad: return "😢"
        case .sleeping: return "😴"
        case .eating: return "🍽️"
        case .playing: return "🎮"
        case .sick: return "🤒"
        case .dead: return "💀"
        }
    }
}
