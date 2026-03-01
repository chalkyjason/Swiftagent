import SwiftUI

struct ContentView: View {
    @StateObject private var gameLogic = GameLogic()
    @State private var showingResetAlert = false

    var body: some View {
        ZStack {
            LinearGradient(
                colors: [
                    Color.blue.opacity(0.3),
                    Color.purple.opacity(0.2),
                    Color.pink.opacity(0.1)
                ],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
            .ignoresSafeArea()

            VStack(spacing: 20) {
                VStack(spacing: 8) {
                    Text("🎮 Pixelated Tamagotchi")
                        .font(.title)
                        .fontWeight(.bold)
                        .foregroundColor(.primary)

                    Text("Take care of your virtual pet!")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
                .padding(.top)

                Spacer()

                VStack(spacing: 15) {
                    PetView(pet: gameLogic.pet)
                        .frame(height: 200)
                        .padding()
                        .background(
                            RoundedRectangle(cornerRadius: 20)
                                .fill(.ultraThinMaterial)
                                .shadow(radius: 10)
                        )

                    if gameLogic.pet.state == .dead {
                        DeathScreenView(onRestart: {
                            gameLogic.resetPet()
                        })
                    }
                }

                Spacer()

                StatsView(pet: gameLogic.pet)
                    .padding(.horizontal)

                Spacer()

                MenuView(pet: gameLogic.pet) {
                    gameLogic.savePet()
                }
                .padding(.horizontal)
                .padding(.bottom, 20)
            }

            if gameLogic.showMessage {
                VStack {
                    Spacer()

                    Text(gameLogic.gameMessage)
                        .font(.headline)
                        .foregroundColor(.white)
                        .padding()
                        .background(
                            RoundedRectangle(cornerRadius: 10)
                                .fill(Color.black.opacity(0.8))
                        )
                        .transition(.scale.combined(with: .opacity))

                    Spacer()
                        .frame(height: 100)
                }
                .animation(.spring(), value: gameLogic.showMessage)
            }
        }
        .toolbar(.hidden, for: .navigationBar)
        .toolbar {
            ToolbarItem(placement: .confirmationAction) {
                Menu {
                    Button("New Pet") {
                        showingResetAlert = true
                    }

                    Button("Save Game") {
                        gameLogic.savePet()
                    }
                } label: {
                    Image(systemName: "ellipsis.circle")
                        .font(.title2)
                }
            }
        }
        .alert("Create New Pet?", isPresented: $showingResetAlert) {
            Button("Cancel", role: .cancel) { }
            Button("Create New Pet", role: .destructive) {
                gameLogic.resetPet()
            }
        } message: {
            Text("This will delete your current pet and create a new one. This action cannot be undone.")
        }
        #if canImport(UIKit)
        .onReceive(NotificationCenter.default.publisher(for: UIApplication.willResignActiveNotification)) { _ in
            gameLogic.pauseGame()
        }
        .onReceive(NotificationCenter.default.publisher(for: UIApplication.didBecomeActiveNotification)) { _ in
            gameLogic.resumeGame()
        }
        #endif
    }
}

struct DeathScreenView: View {
    let onRestart: () -> Void

    var body: some View {
        VStack(spacing: 20) {
            Text("💀")
                .font(.system(size: 60))

            Text("Your pet has passed away...")
                .font(.title2)
                .fontWeight(.bold)
                .foregroundColor(.primary)
                .multilineTextAlignment(.center)

            Text("Don't worry! You can create a new pet and try again.")
                .font(.body)
                .foregroundColor(.secondary)
                .multilineTextAlignment(.center)

            Button("Create New Pet") {
                onRestart()
            }
            .font(.headline)
            .foregroundColor(.white)
            .padding()
            .background(
                RoundedRectangle(cornerRadius: 10)
                    .fill(Color.blue)
            )
        }
        .padding()
        .background(
            RoundedRectangle(cornerRadius: 20)
                .fill(.ultraThinMaterial)
        )
        .padding()
    }
}

#Preview {
    ContentView()
}
