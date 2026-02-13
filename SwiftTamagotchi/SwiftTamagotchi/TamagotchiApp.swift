import SwiftUI

@main
struct TamagotchiApp: App {
    let saveManager = SaveManager.shared
    
    var body: some Scene {
        WindowGroup {
            ContentView()
        }
    }
}
