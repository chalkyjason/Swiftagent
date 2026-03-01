import Foundation

class ScoreManager {
    static let shared = ScoreManager()
    private let highScoreKey = "EndlessRunnerHighScore"
    private let defaults = UserDefaults.standard

    private init() {}

    var highScore: Int {
        get { defaults.integer(forKey: highScoreKey) }
        set { defaults.set(newValue, forKey: highScoreKey) }
    }

    func submitScore(_ score: Int) -> Bool {
        if score > highScore {
            highScore = score
            return true
        }
        return false
    }

    func resetHighScore() {
        defaults.removeObject(forKey: highScoreKey)
    }
}
