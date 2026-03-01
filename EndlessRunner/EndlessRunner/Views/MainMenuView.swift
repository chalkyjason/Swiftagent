import SwiftUI

struct MainMenuView: View {
    let highScore: Int
    let onStart: () -> Void

    var body: some View {
        VStack(spacing: 30) {
            Spacer()

            Text("PIXEL RUNNER")
                .font(.system(size: 36, weight: .heavy, design: .monospaced))
                .foregroundColor(.white)
                .shadow(color: .black.opacity(0.5), radius: 4, x: 2, y: 2)

            Text("Tap to jump. Avoid obstacles.")
                .font(.system(size: 14, design: .monospaced))
                .foregroundColor(.white.opacity(0.8))

            Spacer()

            Button(action: onStart) {
                Text("START")
                    .font(.system(size: 24, weight: .bold, design: .monospaced))
                    .foregroundColor(.black)
                    .padding(.horizontal, 50)
                    .padding(.vertical, 16)
                    .background(
                        RoundedRectangle(cornerRadius: 8)
                            .fill(.white)
                            .shadow(radius: 4)
                    )
            }

            if highScore > 0 {
                Text("HIGH SCORE: \(highScore)")
                    .font(.system(size: 16, weight: .medium, design: .monospaced))
                    .foregroundColor(.yellow)
            }

            Spacer()
                .frame(height: 60)
        }
    }
}
