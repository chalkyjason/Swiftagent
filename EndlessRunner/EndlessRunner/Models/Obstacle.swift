import Foundation
import CoreGraphics

struct Obstacle: Identifiable {
    let id = UUID()
    var x: CGFloat
    let y: CGFloat
    let type: ObstacleType
    var scored: Bool = false

    var size: CGSize { type.size }

    var rect: CGRect {
        CGRect(
            x: x,
            y: y - size.height,
            width: size.width,
            height: size.height
        )
    }

    /// Slightly inset hitbox for forgiving collision
    var hitbox: CGRect {
        rect.insetBy(dx: 4, dy: 4)
    }
}
