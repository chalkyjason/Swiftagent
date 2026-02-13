import SwiftUI

struct PetView: View {
    @ObservedObject var pet: Pet
    @State private var animationOffset: CGFloat = 0
    
    let petSize: CGFloat = 120
    let pixelSize: CGFloat = 8
    
    var body: some View {
        ZStack {
            // Pet Body (Oval shape with pixelated effect)
            PetBodyView(pet: pet, size: petSize)
                .offset(y: animationOffset)
            
            // Eyes
            HStack(spacing: 20) {
                PetEyeView(color: pet.eyeColor, isSleeping: pet.state == .sleeping)
                PetEyeView(color: pet.eyeColor, isSleeping: pet.state == .sleeping)
            }
            .offset(y: animationOffset - 15)
            
            // Mouth
            PetMouthView(isHappy: pet.isHappy, isSad: pet.isSad)
                .offset(y: animationOffset + 15)
        }
        .onAppear {
            startAnimation()
        }
        .animation(.easeInOut(duration: 2).repeatForever(autoreverses: true), value: animationOffset)
    }
    
    private func startAnimation() {
        animationOffset = pet.state == .sleeping ? 0 : 5
    }
}

struct PetBodyView: View {
    let pet: Pet
    let size: CGFloat
    
    var body: some View {
        // Create pixelated oval shape
        ZStack {
            // Main body
            Ellipse()
                .fill(pet.petColor)
                .frame(width: size, height: size * 1.2)
                .overlay(
                    // Pixelated effect overlay
                    LazyVGrid(columns: Array(repeating: GridItem(.fixed(8), spacing: 0), count: Int(size/8))) {
                        ForEach(0..<Int((size * 1.2) / 8), id: .self) { row in
                            ForEach(0..<Int(size/8), id: .self) { col in
                                Rectangle()
                                    .fill(pet.petColor.opacity(pixelatedOpacity(row: row, col: col)))
                                    .frame(width: 8, height: 8)
                            }
                        }
                    }
                )
            
            // State-specific overlays
            if pet.state == .eating {
                Text("🍎")
                    .font(.title)
                    .offset(x: 30, y: -10)
            } else if pet.state == .playing {
                Text("⚽")
                    .font(.title2)
                    .offset(x: -30, y: 10)
            }
        }
    }
    
    private func pixelatedOpacity(row: Int, col: Int) -> Double {
        // Create oval shape with pixelated effect
        let centerX = size / 16
        let centerY = (size * 1.2) / 16
        let x = Double(col) - centerX
        let y = Double(row) - centerY
        let distance = sqrt(x*x + y*y)
        
        return distance <= centerX * 0.8 ? 1.0 : 0.0
    }
}

struct PetEyeView: View {
    let color: Color
    let isSleeping: Bool
    
    var body: some View {
        if isSleeping {
            // Sleeping eyes (horizontal lines)
            Rectangle()
                .fill(color)
                .frame(width: 12, height: 2)
        } else {
            // Regular eyes
            Rectangle()
                .fill(color)
                .frame(width: 8, height: 8)
        }
    }
}

struct PetMouthView: View {
    let isHappy: Bool
    let isSad: Bool
    
    var body: some View {
        if isHappy {
            // Happy mouth (smile)
            Arc(startAngle: .degrees(0), endAngle: .degrees(180), clockwise: false)
                .stroke(Color.black, lineWidth: 3)
                .frame(width: 20, height: 10)
        } else if isSad {
            // Sad mouth (frown)
            Arc(startAngle: .degrees(180), endAngle: .degrees(360), clockwise: false)
                .stroke(Color.black, lineWidth: 3)
                .frame(width: 20, height: 10)
        } else {
            // Neutral mouth
            Rectangle()
                .fill(Color.black)
                .frame(width: 16, height: 2)
        }
    }
}

struct Arc: Shape {
    var startAngle: Angle
    var endAngle: Angle
    var clockwise: Bool
    
    func path(in rect: CGRect) -> Path {
        var path = Path()
        path.addArc(center: CGPoint(x: rect.midX, y: rect.midY),
                   radius: rect.width / 2,
                   startAngle: startAngle,
                   endAngle: endAngle,
                   clockwise: clockwise)
        return path
    }
}
