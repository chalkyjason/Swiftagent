import SwiftUI

struct StatsView: View {
    @ObservedObject var pet: Pet

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            HStack {
                Text("\(pet.name)")
                    .font(.title2)
                    .fontWeight(.bold)
                Spacer()
                Text("Lv.\(pet.level)")
                    .font(.title3)
                    .foregroundColor(.secondary)
            }

            HStack {
                Text("Age: \(pet.age)h")
                    .font(.caption)
                    .foregroundColor(.secondary)
                Spacer()
                HStack {
                    Text(pet.state.emoji)
                    Text(pet.state.displayName)
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            }

            StatBarView(name: "Hunger", value: pet.hunger, color: .red, icon: "🍎")
            StatBarView(name: "Happiness", value: pet.happiness, color: .yellow, icon: "😊")
            StatBarView(name: "Health", value: pet.health, color: .green, icon: "❤️")
            StatBarView(name: "Energy", value: pet.energy, color: .blue, icon: "⚡")
        }
        .padding()
        .background(Color.gray.opacity(0.1))
        .cornerRadius(12)
    }
}

struct StatBarView: View {
    let name: String
    let value: Double
    let color: Color
    let icon: String

    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            HStack {
                Text(icon)
                    .font(.caption)
                Text(name)
                    .font(.caption)
                    .fontWeight(.medium)
                Spacer()
                Text("\(Int(value))")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }

            GeometryReader { geometry in
                ZStack(alignment: .leading) {
                    Rectangle()
                        .fill(Color.gray.opacity(0.3))
                        .frame(height: 8)
                        .cornerRadius(4)

                    Rectangle()
                        .fill(color)
                        .frame(width: geometry.size.width * CGFloat(value / 100.0), height: 8)
                        .cornerRadius(4)
                        .animation(.easeInOut(duration: 0.5), value: value)
                }
            }
            .frame(height: 8)
        }
    }
}

struct DetailedStatsView: View {
    @ObservedObject var pet: Pet
    @Environment(\.dismiss) private var dismiss

    var body: some View {
        NavigationView {
            ScrollView {
                VStack(spacing: 20) {
                    PetView(pet: pet)
                        .frame(height: 200)

                    VStack(alignment: .leading, spacing: 15) {
                        Text("Detailed Statistics")
                            .font(.title2)
                            .fontWeight(.bold)

                        DetailedStatRow(icon: "🍎", name: "Hunger", value: pet.hunger, description: getHungerDescription())
                        DetailedStatRow(icon: "😊", name: "Happiness", value: pet.happiness, description: getHappinessDescription())
                        DetailedStatRow(icon: "❤️", name: "Health", value: pet.health, description: getHealthDescription())
                        DetailedStatRow(icon: "⚡", name: "Energy", value: pet.energy, description: getEnergyDescription())

                        Divider()

                        VStack(alignment: .leading, spacing: 8) {
                            Text("Pet Information")
                                .font(.headline)

                            HStack {
                                Text("Name:")
                                Spacer()
                                Text(pet.name)
                                    .fontWeight(.medium)
                            }

                            HStack {
                                Text("Age:")
                                Spacer()
                                Text("\(pet.age) hours")
                                    .fontWeight(.medium)
                            }

                            HStack {
                                Text("Level:")
                                Spacer()
                                Text("\(pet.level)")
                                    .fontWeight(.medium)
                            }

                            HStack {
                                Text("Status:")
                                Spacer()
                                HStack {
                                    Text(pet.state.emoji)
                                    Text(pet.state.displayName)
                                        .fontWeight(.medium)
                                }
                            }

                            HStack {
                                Text("Born:")
                                Spacer()
                                Text(formatDate(pet.birthTime))
                                    .fontWeight(.medium)
                                    .font(.caption)
                            }
                        }
                    }
                    .padding()
                }
            }
            .navigationTitle("Pet Stats")
            .toolbar {
                ToolbarItem(placement: .confirmationAction) {
                    Button("Done") {
                        dismiss()
                    }
                }
            }
        }
    }

    private func getHungerDescription() -> String {
        switch pet.hunger {
        case 80...100: return "Very full and satisfied"
        case 60..<80: return "Content and well-fed"
        case 40..<60: return "Getting a bit hungry"
        case 20..<40: return "Quite hungry, needs food"
        case 0..<20: return "Starving! Feed immediately!"
        default: return "Unknown"
        }
    }

    private func getHappinessDescription() -> String {
        switch pet.happiness {
        case 80...100: return "Extremely happy and playful"
        case 60..<80: return "Happy and content"
        case 40..<60: return "Neutral mood"
        case 20..<40: return "Feeling down, needs attention"
        case 0..<20: return "Very sad, play with me!"
        default: return "Unknown"
        }
    }

    private func getHealthDescription() -> String {
        switch pet.health {
        case 80...100: return "Perfect health"
        case 60..<80: return "Good health"
        case 40..<60: return "Fair health"
        case 20..<40: return "Poor health, needs medicine"
        case 0..<20: return "Critical condition!"
        default: return "Unknown"
        }
    }

    private func getEnergyDescription() -> String {
        switch pet.energy {
        case 80...100: return "Full of energy"
        case 60..<80: return "Energetic"
        case 40..<60: return "Moderate energy"
        case 20..<40: return "Getting tired"
        case 0..<20: return "Exhausted, needs sleep"
        default: return "Unknown"
        }
    }

    private func formatDate(_ date: Date) -> String {
        let formatter = DateFormatter()
        formatter.dateStyle = .short
        formatter.timeStyle = .short
        return formatter.string(from: date)
    }
}

struct DetailedStatRow: View {
    let icon: String
    let name: String
    let value: Double
    let description: String

    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            HStack {
                Text(icon)
                Text(name)
                    .fontWeight(.medium)
                Spacer()
                Text("\(Int(value))/100")
                    .foregroundColor(.secondary)
            }

            Text(description)
                .font(.caption)
                .foregroundColor(.secondary)
                .padding(.leading, 20)
        }
    }
}
