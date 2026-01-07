import Foundation
import CoreGraphics

// MARK: - CGPoint Extensions

public extension CGPoint {
    /// Creates a point from an angle and length
    init(angle: CGFloat, length: CGFloat) {
        self.init(x: cos(angle) * length, y: sin(angle) * length)
    }

    /// The length (magnitude) of the vector
    var length: CGFloat {
        sqrt(x * x + y * y)
    }

    /// The squared length (avoids sqrt for performance)
    var lengthSquared: CGFloat {
        x * x + y * y
    }

    /// The angle of the vector in radians
    var angle: CGFloat {
        atan2(y, x)
    }

    /// Returns a normalized (unit length) version of the vector
    var normalized: CGPoint {
        let len = length
        return len > 0 ? self / len : .zero
    }

    /// Returns the vector rotated by the given angle in radians
    func rotated(by angle: CGFloat) -> CGPoint {
        CGPoint(
            x: x * cos(angle) - y * sin(angle),
            y: x * sin(angle) + y * cos(angle)
        )
    }

    /// Returns the distance to another point
    func distance(to point: CGPoint) -> CGFloat {
        (self - point).length
    }

    /// Returns the squared distance to another point (faster than distance)
    func distanceSquared(to point: CGPoint) -> CGFloat {
        (self - point).lengthSquared
    }

    /// Dot product with another vector
    func dot(_ other: CGPoint) -> CGFloat {
        x * other.x + y * other.y
    }

    /// Cross product (z-component of 3D cross product)
    func cross(_ other: CGPoint) -> CGFloat {
        x * other.y - y * other.x
    }

    /// Linearly interpolates between this point and another
    func lerp(to: CGPoint, t: CGFloat) -> CGPoint {
        CGPoint(
            x: x + (to.x - x) * t,
            y: y + (to.y - y) * t
        )
    }

    /// Clamps the vector to a maximum length
    func clamped(to maxLength: CGFloat) -> CGPoint {
        let len = length
        if len > maxLength {
            return self * (maxLength / len)
        }
        return self
    }

    /// Returns perpendicular vector (rotated 90 degrees counterclockwise)
    var perpendicular: CGPoint {
        CGPoint(x: -y, y: x)
    }

    /// Returns the reflection of this vector off a surface with the given normal
    func reflected(normal: CGPoint) -> CGPoint {
        self - normal * (2 * self.dot(normal))
    }
}

// MARK: - CGPoint Operators

public extension CGPoint {
    static func + (lhs: CGPoint, rhs: CGPoint) -> CGPoint {
        CGPoint(x: lhs.x + rhs.x, y: lhs.y + rhs.y)
    }

    static func - (lhs: CGPoint, rhs: CGPoint) -> CGPoint {
        CGPoint(x: lhs.x - rhs.x, y: lhs.y - rhs.y)
    }

    static func * (lhs: CGPoint, rhs: CGFloat) -> CGPoint {
        CGPoint(x: lhs.x * rhs, y: lhs.y * rhs)
    }

    static func * (lhs: CGFloat, rhs: CGPoint) -> CGPoint {
        CGPoint(x: lhs * rhs.x, y: lhs * rhs.y)
    }

    static func / (lhs: CGPoint, rhs: CGFloat) -> CGPoint {
        CGPoint(x: lhs.x / rhs, y: lhs.y / rhs)
    }

    static func += (lhs: inout CGPoint, rhs: CGPoint) {
        lhs = lhs + rhs
    }

    static func -= (lhs: inout CGPoint, rhs: CGPoint) {
        lhs = lhs - rhs
    }

    static func *= (lhs: inout CGPoint, rhs: CGFloat) {
        lhs = lhs * rhs
    }

    static func /= (lhs: inout CGPoint, rhs: CGFloat) {
        lhs = lhs / rhs
    }

    static prefix func - (point: CGPoint) -> CGPoint {
        CGPoint(x: -point.x, y: -point.y)
    }
}

// MARK: - CGVector Extensions

public extension CGVector {
    /// Creates a vector from an angle and length
    init(angle: CGFloat, length: CGFloat) {
        self.init(dx: cos(angle) * length, dy: sin(angle) * length)
    }

    /// Converts to CGPoint
    var point: CGPoint {
        CGPoint(x: dx, y: dy)
    }

    /// The length (magnitude) of the vector
    var length: CGFloat {
        sqrt(dx * dx + dy * dy)
    }

    /// The squared length
    var lengthSquared: CGFloat {
        dx * dx + dy * dy
    }

    /// The angle in radians
    var angle: CGFloat {
        atan2(dy, dx)
    }

    /// Returns a normalized version
    var normalized: CGVector {
        let len = length
        return len > 0 ? CGVector(dx: dx / len, dy: dy / len) : .zero
    }
}

// MARK: - CGSize Extensions

public extension CGSize {
    /// Center point of the size (width/2, height/2)
    var center: CGPoint {
        CGPoint(x: width / 2, y: height / 2)
    }

    /// Diagonal length
    var diagonal: CGFloat {
        sqrt(width * width + height * height)
    }

    /// Aspect ratio (width / height)
    var aspectRatio: CGFloat {
        height != 0 ? width / height : 0
    }

    /// Returns a size scaled uniformly
    func scaled(by factor: CGFloat) -> CGSize {
        CGSize(width: width * factor, height: height * factor)
    }

    /// Returns a size that fits within the given size while maintaining aspect ratio
    func aspectFit(in container: CGSize) -> CGSize {
        let widthRatio = container.width / width
        let heightRatio = container.height / height
        let ratio = min(widthRatio, heightRatio)
        return scaled(by: ratio)
    }

    /// Returns a size that fills the given size while maintaining aspect ratio
    func aspectFill(in container: CGSize) -> CGSize {
        let widthRatio = container.width / width
        let heightRatio = container.height / height
        let ratio = max(widthRatio, heightRatio)
        return scaled(by: ratio)
    }
}

// MARK: - CGRect Extensions

public extension CGRect {
    /// Center point of the rectangle
    var center: CGPoint {
        CGPoint(x: midX, y: midY)
    }

    /// Creates a rect centered at a point with the given size
    init(center: CGPoint, size: CGSize) {
        self.init(
            x: center.x - size.width / 2,
            y: center.y - size.height / 2,
            width: size.width,
            height: size.height
        )
    }

    /// Top-left corner
    var topLeft: CGPoint {
        CGPoint(x: minX, y: maxY)
    }

    /// Top-right corner
    var topRight: CGPoint {
        CGPoint(x: maxX, y: maxY)
    }

    /// Bottom-left corner
    var bottomLeft: CGPoint {
        CGPoint(x: minX, y: minY)
    }

    /// Bottom-right corner
    var bottomRight: CGPoint {
        CGPoint(x: maxX, y: minY)
    }

    /// Returns a random point within the rectangle
    func randomPoint() -> CGPoint {
        CGPoint(
            x: CGFloat.random(in: minX...maxX),
            y: CGFloat.random(in: minY...maxY)
        )
    }

    /// Checks if a point is inside the rect with a margin
    func contains(_ point: CGPoint, margin: CGFloat) -> Bool {
        insetBy(dx: -margin, dy: -margin).contains(point)
    }
}

// MARK: - Angle Utilities

/// Utility functions for working with angles
public struct Angle {
    /// Converts degrees to radians
    public static func degreesToRadians(_ degrees: CGFloat) -> CGFloat {
        degrees * .pi / 180
    }

    /// Converts radians to degrees
    public static func radiansToDegrees(_ radians: CGFloat) -> CGFloat {
        radians * 180 / .pi
    }

    /// Normalizes an angle to the range [-π, π]
    public static func normalize(_ angle: CGFloat) -> CGFloat {
        var result = angle.truncatingRemainder(dividingBy: 2 * .pi)
        if result > .pi {
            result -= 2 * .pi
        } else if result < -.pi {
            result += 2 * .pi
        }
        return result
    }

    /// Returns the shortest angular distance between two angles
    public static func shortestDistance(from: CGFloat, to: CGFloat) -> CGFloat {
        normalize(to - from)
    }

    /// Linearly interpolates between two angles (taking the short path)
    public static func lerp(from: CGFloat, to: CGFloat, t: CGFloat) -> CGFloat {
        from + shortestDistance(from: from, to: to) * t
    }
}

// MARK: - Random Utilities

public extension CGFloat {
    /// Returns a random value between two values
    static func random(between min: CGFloat, and max: CGFloat) -> CGFloat {
        CGFloat.random(in: min...max)
    }
}

public extension CGPoint {
    /// Returns a random point within a rectangle
    static func random(in rect: CGRect) -> CGPoint {
        rect.randomPoint()
    }

    /// Returns a random point on a circle
    static func randomOnCircle(center: CGPoint = .zero, radius: CGFloat) -> CGPoint {
        let angle = CGFloat.random(in: 0...(2 * .pi))
        return CGPoint(
            x: center.x + cos(angle) * radius,
            y: center.y + sin(angle) * radius
        )
    }

    /// Returns a random point inside a circle
    static func randomInCircle(center: CGPoint = .zero, radius: CGFloat) -> CGPoint {
        let r = radius * sqrt(CGFloat.random(in: 0...1))
        let angle = CGFloat.random(in: 0...(2 * .pi))
        return CGPoint(
            x: center.x + cos(angle) * r,
            y: center.y + sin(angle) * r
        )
    }
}
