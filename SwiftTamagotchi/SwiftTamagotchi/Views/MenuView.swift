import SwiftUI

struct MenuView: View {
    @ObservedObject var pet: Pet
    @State private var showingStats = false
    let onSave: () -> Void
    
    let columns = Array(repeating: GridItem(.flexible(), spacing: 10), count: 3)
    
    var body: some View {
        VStack(spacing: 15) {
            Text("Actions")
                .font(.headline)
                .foregroundColor(.white)
            
            LazyVGrid(columns: columns, spacing: 10) {
                MenuButton(
                    icon: "🍎",
                    title: "Feed",
                    color: .red,
                    disabled: pet.state == .dead || pet.hunger >= 100
                ) {
                    pet.feed()
                }
                
                MenuButton(
                    icon: "🎮",
                    title: "Play",
                    color: .yellow,
                    disabled: pet.state == .dead || pet.energy < 10
                ) {
                    pet.play()
                }
                
                MenuButton(
                    icon: "💊",
                    title: "Medicine",
                    color: .purple,
                    disabled: pet.state == .dead || pet.health >= 100
                ) {
                    pet.giveMedicine()
                }
                
                MenuButton(
                    icon: "😴",
                    title: "Sleep",
                    color: .blue,
                    disabled: pet.state == .dead || pet.energy >= 100
                ) {
                    pet.sleep()
                }
                
                MenuButton(
                    icon: "📊",
                    title: "Stats",
                    color: .green,
                    disabled: false
                ) {
                    showingStats = true
                }
                
                MenuButton(
                    icon: "💾",
                    title: "Save",
                    color: .orange,
                    disabled: false
                ) {
                    onSave()
                }
            }
        }
        .padding()
        .background(
            RoundedRectangle(cornerRadius: 12)
                .fill(Color.black.opacity(0.7))
        )
        .sheet(isPresented: $showingStats) {
            DetailedStatsView(pet: pet)
        }
    }
}

struct MenuButton: View {
    let icon: String
    let title: String
    let color: Color
    let disabled: Bool
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            VStack(spacing: 4) {
                Text(icon)
                    .font(.title2)
                Text(title)
                    .font(.caption)
                    .fontWeight(.medium)
            }
            .frame(maxWidth: .infinity, maxHeight: .infinity)
            .aspectRatio(1, contentMode: .fit)
            .background(
                RoundedRectangle(cornerRadius: 8)
                    .fill(disabled ? Color.gray.opacity(0.3) : color.opacity(0.8))
            )
            .foregroundColor(disabled ? .gray : .white)
        }
        .disabled(disabled)
        .scaleEffect(disabled ? 0.9 : 1.0)
        .animation(.easeInOut(duration: 0.2), value: disabled)
    }
}
