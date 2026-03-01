import SwiftUI

struct GameCanvasView: View {
    @ObservedObject var engine: GameEngine
    let screenSize: CGSize

    private var groundY: CGFloat {
        screenSize.height - GameConstants.groundHeight
    }

    var body: some View {
        Canvas { context, size in
            drawSky(context: context, size: size)
            drawClouds(context: context, size: size)
            drawGround(context: context, size: size)
            drawObstacles(context: context)
            drawPlayer(context: context)
        }
    }

    // MARK: - Drawing

    private func drawSky(context: GraphicsContext, size: CGSize) {
        let skyGradient = Gradient(colors: [
            Color(red: 0.53, green: 0.81, blue: 0.98),
            Color(red: 0.75, green: 0.90, blue: 1.0)
        ])
        let skyRect = CGRect(x: 0, y: 0, width: size.width, height: groundY)
        context.fill(
            Path(skyRect),
            with: .linearGradient(skyGradient, startPoint: .zero, endPoint: CGPoint(x: 0, y: groundY))
        )
    }

    private func drawClouds(context: GraphicsContext, size: CGSize) {
        let cloudPositions: [(x: CGFloat, y: CGFloat, scale: CGFloat)] = [
            (100, 60, 1.0),
            (300, 40, 0.7),
            (500, 80, 0.8),
            (700, 50, 0.6),
        ]

        for cloud in cloudPositions {
            let offset = (engine.groundOffset * 0.3).truncatingRemainder(dividingBy: size.width + 200)
            let x = (cloud.x + offset).truncatingRemainder(dividingBy: size.width + 100)

            var ctx = context
            ctx.opacity = 0.8
            let cloudRect = CGRect(
                x: x, y: cloud.y,
                width: 60 * cloud.scale, height: 20 * cloud.scale
            )
            ctx.fill(Path(ellipseIn: cloudRect), with: .color(.white))

            let cloudRect2 = CGRect(
                x: x + 20 * cloud.scale, y: cloud.y - 10 * cloud.scale,
                width: 40 * cloud.scale, height: 25 * cloud.scale
            )
            ctx.fill(Path(ellipseIn: cloudRect2), with: .color(.white))
        }
    }

    private func drawGround(context: GraphicsContext, size: CGSize) {
        // Main ground
        let groundRect = CGRect(x: 0, y: groundY, width: size.width, height: GameConstants.groundHeight)
        context.fill(Path(groundRect), with: .color(Color(red: 0.55, green: 0.36, blue: 0.24)))

        // Ground top line
        let topLine = CGRect(x: 0, y: groundY, width: size.width, height: 3)
        context.fill(Path(topLine), with: .color(Color(red: 0.40, green: 0.26, blue: 0.17)))

        // Scrolling ground texture (pixel dashes)
        let dashWidth: CGFloat = 20
        let dashHeight: CGFloat = 2
        let dashY = groundY + 15
        var dashX = engine.groundOffset
        while dashX < size.width + dashWidth {
            let rect = CGRect(x: dashX, y: dashY, width: dashWidth, height: dashHeight)
            context.fill(Path(rect), with: .color(Color(red: 0.45, green: 0.30, blue: 0.20)))
            dashX += 40
        }

        let dashY2 = groundY + 35
        var dashX2 = engine.groundOffset + 20
        while dashX2 < size.width + dashWidth {
            let rect = CGRect(x: dashX2, y: dashY2, width: dashWidth * 0.6, height: dashHeight)
            context.fill(Path(rect), with: .color(Color(red: 0.45, green: 0.30, blue: 0.20)))
            dashX2 += 40
        }
    }

    private func drawObstacles(context: GraphicsContext) {
        for obstacle in engine.obstacles {
            switch obstacle.type {
            case .cactusSmall:
                drawCactus(context: context, obstacle: obstacle, isLarge: false)
            case .cactusLarge:
                drawCactus(context: context, obstacle: obstacle, isLarge: true)
            case .rock:
                drawRock(context: context, obstacle: obstacle)
            case .doubleRock:
                drawDoubleRock(context: context, obstacle: obstacle)
            }
        }
    }

    private func drawCactus(context: GraphicsContext, obstacle: Obstacle, isLarge: Bool) {
        let rect = obstacle.rect
        let green = Color(red: 0.2, green: 0.6, blue: 0.2)
        let darkGreen = Color(red: 0.15, green: 0.45, blue: 0.15)

        // Main trunk
        let trunkWidth = rect.width * 0.4
        let trunkRect = CGRect(
            x: rect.midX - trunkWidth / 2,
            y: rect.minY,
            width: trunkWidth,
            height: rect.height
        )
        context.fill(Path(trunkRect), with: .color(green))

        // Arms
        if isLarge {
            let armHeight = rect.height * 0.25
            // Left arm
            let leftArmH = CGRect(
                x: rect.minX,
                y: rect.minY + rect.height * 0.3,
                width: rect.width * 0.3,
                height: trunkWidth * 0.7
            )
            context.fill(Path(leftArmH), with: .color(green))
            let leftArmV = CGRect(
                x: rect.minX,
                y: rect.minY + rect.height * 0.3 - armHeight,
                width: trunkWidth * 0.7,
                height: armHeight
            )
            context.fill(Path(leftArmV), with: .color(green))

            // Right arm
            let rightArmH = CGRect(
                x: rect.midX + trunkWidth / 2 - rect.width * 0.05,
                y: rect.minY + rect.height * 0.5,
                width: rect.width * 0.3,
                height: trunkWidth * 0.7
            )
            context.fill(Path(rightArmH), with: .color(green))
            let rightArmV = CGRect(
                x: rect.maxX - trunkWidth * 0.7,
                y: rect.minY + rect.height * 0.5 - armHeight * 0.7,
                width: trunkWidth * 0.7,
                height: armHeight * 0.7
            )
            context.fill(Path(rightArmV), with: .color(green))
        }

        // Detail lines
        let lineRect = CGRect(
            x: rect.midX - 1,
            y: rect.minY + 4,
            width: 2,
            height: rect.height - 8
        )
        context.fill(Path(lineRect), with: .color(darkGreen))
    }

    private func drawRock(context: GraphicsContext, obstacle: Obstacle) {
        let rect = obstacle.rect
        let gray = Color(red: 0.5, green: 0.5, blue: 0.5)
        let darkGray = Color(red: 0.35, green: 0.35, blue: 0.35)

        // Rock body as a rounded trapezoid approximation
        var path = Path()
        path.move(to: CGPoint(x: rect.minX + 5, y: rect.maxY))
        path.addLine(to: CGPoint(x: rect.minX, y: rect.maxY - rect.height * 0.6))
        path.addLine(to: CGPoint(x: rect.minX + rect.width * 0.3, y: rect.minY))
        path.addLine(to: CGPoint(x: rect.maxX - rect.width * 0.2, y: rect.minY + 3))
        path.addLine(to: CGPoint(x: rect.maxX, y: rect.maxY - rect.height * 0.4))
        path.addLine(to: CGPoint(x: rect.maxX - 3, y: rect.maxY))
        path.closeSubpath()
        context.fill(path, with: .color(gray))

        // Highlight
        let highlight = CGRect(
            x: rect.minX + rect.width * 0.3,
            y: rect.minY + 5,
            width: rect.width * 0.2,
            height: 3
        )
        context.fill(Path(highlight), with: .color(.white.opacity(0.3)))

        // Shadow line
        let shadowLine = CGRect(
            x: rect.minX + 4,
            y: rect.maxY - 4,
            width: rect.width - 8,
            height: 2
        )
        context.fill(Path(shadowLine), with: .color(darkGray))
    }

    private func drawDoubleRock(context: GraphicsContext, obstacle: Obstacle) {
        let rect = obstacle.rect

        // First rock (slightly left and lower)
        let rock1 = Obstacle(
            x: obstacle.x,
            y: obstacle.y,
            type: .rock
        )
        drawRock(context: context, obstacle: rock1)

        // Second rock overlapping (slightly right and higher)
        let smallRect = CGRect(
            x: rect.minX + rect.width * 0.4,
            y: rect.minY - 5,
            width: rect.width * 0.5,
            height: rect.height * 0.7
        )
        let gray = Color(red: 0.55, green: 0.55, blue: 0.55)
        var path = Path()
        path.move(to: CGPoint(x: smallRect.minX + 3, y: smallRect.maxY))
        path.addLine(to: CGPoint(x: smallRect.minX, y: smallRect.midY))
        path.addLine(to: CGPoint(x: smallRect.midX, y: smallRect.minY))
        path.addLine(to: CGPoint(x: smallRect.maxX, y: smallRect.midY))
        path.addLine(to: CGPoint(x: smallRect.maxX - 2, y: smallRect.maxY))
        path.closeSubpath()
        context.fill(path, with: .color(gray))
    }

    private func drawPlayer(context: GraphicsContext) {
        let x = GameConstants.playerX
        let y = engine.playerY
        let w = GameConstants.playerSize.width
        let h = GameConstants.playerSize.height

        switch engine.playerState {
        case .running:
            drawRunningPlayer(context: context, x: x, y: y, w: w, h: h)
        case .jumping, .falling:
            drawJumpingPlayer(context: context, x: x, y: y, w: w, h: h)
        case .dead:
            drawDeadPlayer(context: context, x: x, y: y, w: w, h: h)
        }
    }

    private func drawRunningPlayer(context: GraphicsContext, x: CGFloat, y: CGFloat, w: CGFloat, h: CGFloat) {
        let bodyColor = Color(red: 0.2, green: 0.5, blue: 0.9)
        let skinColor = Color(red: 1.0, green: 0.85, blue: 0.7)

        // Body
        let bodyRect = CGRect(x: x + 5, y: y + 15, width: w - 10, height: h * 0.45)
        context.fill(Path(bodyRect), with: .color(bodyColor))

        // Head
        let headRect = CGRect(x: x + 8, y: y, width: w - 16, height: 18)
        context.fill(Path(headRect), with: .color(skinColor))

        // Eyes
        let eyeRect = CGRect(x: x + 22, y: y + 5, width: 4, height: 4)
        context.fill(Path(eyeRect), with: .color(.black))

        // Legs (animated based on ground offset)
        let legPhase = abs(engine.groundOffset.truncatingRemainder(dividingBy: 20)) > 10
        let legY = y + h * 0.6
        let legHeight = h * 0.4

        if legPhase {
            // Left leg forward, right leg back
            let leftLeg = CGRect(x: x + 12, y: legY, width: 7, height: legHeight)
            context.fill(Path(leftLeg), with: .color(bodyColor.opacity(0.8)))
            let rightLeg = CGRect(x: x + 20, y: legY, width: 7, height: legHeight - 5)
            context.fill(Path(rightLeg), with: .color(bodyColor.opacity(0.8)))
        } else {
            let leftLeg = CGRect(x: x + 12, y: legY, width: 7, height: legHeight - 5)
            context.fill(Path(leftLeg), with: .color(bodyColor.opacity(0.8)))
            let rightLeg = CGRect(x: x + 20, y: legY, width: 7, height: legHeight)
            context.fill(Path(rightLeg), with: .color(bodyColor.opacity(0.8)))
        }
    }

    private func drawJumpingPlayer(context: GraphicsContext, x: CGFloat, y: CGFloat, w: CGFloat, h: CGFloat) {
        let bodyColor = Color(red: 0.2, green: 0.5, blue: 0.9)
        let skinColor = Color(red: 1.0, green: 0.85, blue: 0.7)

        // Body
        let bodyRect = CGRect(x: x + 5, y: y + 15, width: w - 10, height: h * 0.45)
        context.fill(Path(bodyRect), with: .color(bodyColor))

        // Head
        let headRect = CGRect(x: x + 8, y: y, width: w - 16, height: 18)
        context.fill(Path(headRect), with: .color(skinColor))

        // Eyes
        let eyeRect = CGRect(x: x + 22, y: y + 5, width: 4, height: 4)
        context.fill(Path(eyeRect), with: .color(.black))

        // Legs tucked
        let legY = y + h * 0.6
        let leftLeg = CGRect(x: x + 10, y: legY, width: 8, height: h * 0.3)
        context.fill(Path(leftLeg), with: .color(bodyColor.opacity(0.8)))
        let rightLeg = CGRect(x: x + 22, y: legY, width: 8, height: h * 0.3)
        context.fill(Path(rightLeg), with: .color(bodyColor.opacity(0.8)))
    }

    private func drawDeadPlayer(context: GraphicsContext, x: CGFloat, y: CGFloat, w: CGFloat, h: CGFloat) {
        let bodyColor = Color(red: 0.6, green: 0.3, blue: 0.3)
        let skinColor = Color(red: 0.9, green: 0.75, blue: 0.65)

        // Body (tilted effect - just draw slightly rotated rectangles)
        let bodyRect = CGRect(x: x + 3, y: y + 15, width: w - 6, height: h * 0.45)
        context.fill(Path(bodyRect), with: .color(bodyColor))

        // Head
        let headRect = CGRect(x: x + 8, y: y + 2, width: w - 16, height: 18)
        context.fill(Path(headRect), with: .color(skinColor))

        // X eyes
        let eyeX = x + 20
        let eyeY = y + 7
        var xPath = Path()
        xPath.move(to: CGPoint(x: eyeX, y: eyeY))
        xPath.addLine(to: CGPoint(x: eyeX + 6, y: eyeY + 6))
        xPath.move(to: CGPoint(x: eyeX + 6, y: eyeY))
        xPath.addLine(to: CGPoint(x: eyeX, y: eyeY + 6))
        context.stroke(xPath, with: .color(.red), lineWidth: 2)

        // Legs collapsed
        let legY = y + h * 0.6
        let leftLeg = CGRect(x: x + 8, y: legY, width: 10, height: h * 0.25)
        context.fill(Path(leftLeg), with: .color(bodyColor.opacity(0.7)))
        let rightLeg = CGRect(x: x + 22, y: legY, width: 10, height: h * 0.25)
        context.fill(Path(rightLeg), with: .color(bodyColor.opacity(0.7)))
    }
}
