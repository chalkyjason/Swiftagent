import SwiftUI

struct GameView: View {
    @StateObject private var engine = GameEngine()
    @State private var showMenu = true

    var body: some View {
        GeometryReader { geometry in
            ZStack {
                // Game canvas - always rendered for background
                TimelineView(.animation(minimumInterval: 1.0 / 60.0)) { timeline in
                    GameCanvasView(engine: engine, screenSize: geometry.size)
                        .onChange(of: timeline.date) { _, _ in
                            if engine.isRunning {
                                engine.update()
                            }
                        }
                }

                // HUD (score display during gameplay)
                if engine.isRunning && !engine.isGameOver {
                    VStack {
                        HStack {
                            Spacer()
                            VStack(alignment: .trailing, spacing: 4) {
                                Text("\(engine.score)")
                                    .font(.system(size: 24, weight: .bold, design: .monospaced))
                                    .foregroundColor(.white)
                                    .shadow(color: .black.opacity(0.5), radius: 2)

                                if engine.highScore > 0 {
                                    Text("HI \(engine.highScore)")
                                        .font(.system(size: 14, design: .monospaced))
                                        .foregroundColor(.white.opacity(0.6))
                                }
                            }
                            .padding()
                        }
                        Spacer()
                    }
                }

                // Menu overlay
                if showMenu && !engine.isRunning {
                    Color.black.opacity(0.4)
                        .ignoresSafeArea()

                    MainMenuView(highScore: engine.highScore) {
                        engine.configure(screenSize: geometry.size)
                        engine.startGame()
                        showMenu = false
                    }
                }

                // Game over overlay
                if engine.isGameOver {
                    Color.black.opacity(0.3)
                        .ignoresSafeArea()

                    GameOverView(
                        score: engine.score,
                        highScore: engine.highScore,
                        isNewHighScore: engine.isNewHighScore,
                        onRestart: {
                            engine.startGame()
                        },
                        onMenu: {
                            showMenu = true
                        }
                    )
                }
            }
            .onAppear {
                engine.configure(screenSize: geometry.size)
            }
            .onTapGesture {
                if engine.isRunning && !engine.isGameOver {
                    engine.jump()
                }
            }
        }
        .ignoresSafeArea()
    }
}

#Preview {
    GameView()
}
