import SwiftUI

struct GameOverView: View {
    let score: Int
    let highScore: Int
    let isNewHighScore: Bool
    let onRestart: () -> Void
    let onMenu: () -> Void

    var body: some View {
        VStack(spacing: 20) {
            Text("GAME OVER")
                .font(.system(size: 32, weight: .heavy, design: .monospaced))
                .foregroundColor(.white)

            if isNewHighScore {
                Text("NEW HIGH SCORE!")
                    .font(.system(size: 18, weight: .bold, design: .monospaced))
                    .foregroundColor(.yellow)
            }

            VStack(spacing: 8) {
                Text("SCORE: \(score)")
                    .font(.system(size: 22, weight: .bold, design: .monospaced))
                    .foregroundColor(.white)

                Text("BEST: \(highScore)")
                    .font(.system(size: 16, design: .monospaced))
                    .foregroundColor(.white.opacity(0.7))
            }

            HStack(spacing: 20) {
                Button(action: onRestart) {
                    Text("RETRY")
                        .font(.system(size: 18, weight: .bold, design: .monospaced))
                        .foregroundColor(.black)
                        .padding(.horizontal, 30)
                        .padding(.vertical, 12)
                        .background(
                            RoundedRectangle(cornerRadius: 8)
                                .fill(.white)
                        )
                }

                Button(action: onMenu) {
                    Text("MENU")
                        .font(.system(size: 18, weight: .bold, design: .monospaced))
                        .foregroundColor(.white)
                        .padding(.horizontal, 30)
                        .padding(.vertical, 12)
                        .background(
                            RoundedRectangle(cornerRadius: 8)
                                .stroke(.white, lineWidth: 2)
                        )
                }
            }
        }
        .padding(30)
        .background(
            RoundedRectangle(cornerRadius: 16)
                .fill(.black.opacity(0.75))
        )
    }
}
