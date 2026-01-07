import XCTest
@testable import PhysicsUtils

final class PhysicsUtilsTests: XCTestCase {

    // MARK: - CGPoint Vector Math Tests

    func testPointLength() {
        let point = CGPoint(x: 3, y: 4)
        XCTAssertEqual(point.length, 5, accuracy: 0.0001)
    }

    func testPointLengthSquared() {
        let point = CGPoint(x: 3, y: 4)
        XCTAssertEqual(point.lengthSquared, 25, accuracy: 0.0001)
    }

    func testPointNormalized() {
        let point = CGPoint(x: 3, y: 4)
        let normalized = point.normalized

        XCTAssertEqual(normalized.length, 1, accuracy: 0.0001)
        XCTAssertEqual(normalized.x, 0.6, accuracy: 0.0001)
        XCTAssertEqual(normalized.y, 0.8, accuracy: 0.0001)
    }

    func testPointZeroNormalized() {
        let zero = CGPoint.zero
        let normalized = zero.normalized

        XCTAssertEqual(normalized, .zero)
    }

    func testPointFromAngle() {
        let point = CGPoint(angle: 0, length: 1)
        XCTAssertEqual(point.x, 1, accuracy: 0.0001)
        XCTAssertEqual(point.y, 0, accuracy: 0.0001)

        let point90 = CGPoint(angle: .pi / 2, length: 1)
        XCTAssertEqual(point90.x, 0, accuracy: 0.0001)
        XCTAssertEqual(point90.y, 1, accuracy: 0.0001)
    }

    func testPointAngle() {
        let right = CGPoint(x: 1, y: 0)
        XCTAssertEqual(right.angle, 0, accuracy: 0.0001)

        let up = CGPoint(x: 0, y: 1)
        XCTAssertEqual(up.angle, .pi / 2, accuracy: 0.0001)
    }

    func testPointDistance() {
        let a = CGPoint(x: 0, y: 0)
        let b = CGPoint(x: 3, y: 4)

        XCTAssertEqual(a.distance(to: b), 5, accuracy: 0.0001)
    }

    func testPointDot() {
        let a = CGPoint(x: 1, y: 0)
        let b = CGPoint(x: 0, y: 1)

        XCTAssertEqual(a.dot(b), 0, accuracy: 0.0001) // Perpendicular

        let c = CGPoint(x: 1, y: 1)
        let d = CGPoint(x: 1, y: 1)
        XCTAssertEqual(c.dot(d), 2, accuracy: 0.0001) // Same direction
    }

    func testPointCross() {
        let a = CGPoint(x: 1, y: 0)
        let b = CGPoint(x: 0, y: 1)

        XCTAssertEqual(a.cross(b), 1, accuracy: 0.0001)
        XCTAssertEqual(b.cross(a), -1, accuracy: 0.0001)
    }

    func testPointLerp() {
        let a = CGPoint(x: 0, y: 0)
        let b = CGPoint(x: 10, y: 10)

        let mid = a.lerp(to: b, t: 0.5)
        XCTAssertEqual(mid.x, 5, accuracy: 0.0001)
        XCTAssertEqual(mid.y, 5, accuracy: 0.0001)

        let quarter = a.lerp(to: b, t: 0.25)
        XCTAssertEqual(quarter.x, 2.5, accuracy: 0.0001)
        XCTAssertEqual(quarter.y, 2.5, accuracy: 0.0001)
    }

    func testPointClamped() {
        let point = CGPoint(x: 6, y: 8) // length = 10
        let clamped = point.clamped(to: 5)

        XCTAssertEqual(clamped.length, 5, accuracy: 0.0001)
    }

    func testPointPerpendicular() {
        let point = CGPoint(x: 1, y: 0)
        let perp = point.perpendicular

        XCTAssertEqual(perp.x, 0, accuracy: 0.0001)
        XCTAssertEqual(perp.y, 1, accuracy: 0.0001)
        XCTAssertEqual(point.dot(perp), 0, accuracy: 0.0001) // Should be perpendicular
    }

    func testPointRotated() {
        let point = CGPoint(x: 1, y: 0)
        let rotated = point.rotated(by: .pi / 2)

        XCTAssertEqual(rotated.x, 0, accuracy: 0.0001)
        XCTAssertEqual(rotated.y, 1, accuracy: 0.0001)
    }

    // MARK: - CGPoint Operators Tests

    func testPointAddition() {
        let a = CGPoint(x: 1, y: 2)
        let b = CGPoint(x: 3, y: 4)

        let sum = a + b
        XCTAssertEqual(sum.x, 4)
        XCTAssertEqual(sum.y, 6)
    }

    func testPointSubtraction() {
        let a = CGPoint(x: 5, y: 6)
        let b = CGPoint(x: 2, y: 3)

        let diff = a - b
        XCTAssertEqual(diff.x, 3)
        XCTAssertEqual(diff.y, 3)
    }

    func testPointScalarMultiplication() {
        let point = CGPoint(x: 2, y: 3)

        let scaled1 = point * 2
        XCTAssertEqual(scaled1.x, 4)
        XCTAssertEqual(scaled1.y, 6)

        let scaled2 = 3 * point
        XCTAssertEqual(scaled2.x, 6)
        XCTAssertEqual(scaled2.y, 9)
    }

    func testPointScalarDivision() {
        let point = CGPoint(x: 6, y: 8)
        let divided = point / 2

        XCTAssertEqual(divided.x, 3)
        XCTAssertEqual(divided.y, 4)
    }

    func testPointNegation() {
        let point = CGPoint(x: 3, y: -4)
        let negated = -point

        XCTAssertEqual(negated.x, -3)
        XCTAssertEqual(negated.y, 4)
    }

    // MARK: - CGSize Tests

    func testSizeCenter() {
        let size = CGSize(width: 100, height: 50)
        let center = size.center

        XCTAssertEqual(center.x, 50)
        XCTAssertEqual(center.y, 25)
    }

    func testSizeDiagonal() {
        let size = CGSize(width: 3, height: 4)
        XCTAssertEqual(size.diagonal, 5, accuracy: 0.0001)
    }

    func testSizeAspectRatio() {
        let wideSize = CGSize(width: 16, height: 9)
        XCTAssertEqual(wideSize.aspectRatio, 16.0 / 9.0, accuracy: 0.0001)

        let zeroHeight = CGSize(width: 100, height: 0)
        XCTAssertEqual(zeroHeight.aspectRatio, 0)
    }

    func testSizeAspectFit() {
        let size = CGSize(width: 200, height: 100)
        let container = CGSize(width: 100, height: 100)
        let fitted = size.aspectFit(in: container)

        XCTAssertEqual(fitted.width, 100, accuracy: 0.0001)
        XCTAssertEqual(fitted.height, 50, accuracy: 0.0001)
    }

    // MARK: - CGRect Tests

    func testRectCenter() {
        let rect = CGRect(x: 0, y: 0, width: 100, height: 50)
        let center = rect.center

        XCTAssertEqual(center.x, 50)
        XCTAssertEqual(center.y, 25)
    }

    func testRectInitFromCenter() {
        let center = CGPoint(x: 50, y: 50)
        let size = CGSize(width: 20, height: 10)
        let rect = CGRect(center: center, size: size)

        XCTAssertEqual(rect.minX, 40)
        XCTAssertEqual(rect.minY, 45)
        XCTAssertEqual(rect.center, center)
    }

    // MARK: - Angle Tests

    func testDegreesToRadians() {
        XCTAssertEqual(Angle.degreesToRadians(180), .pi, accuracy: 0.0001)
        XCTAssertEqual(Angle.degreesToRadians(90), .pi / 2, accuracy: 0.0001)
    }

    func testRadiansToDegrees() {
        XCTAssertEqual(Angle.radiansToDegrees(.pi), 180, accuracy: 0.0001)
        XCTAssertEqual(Angle.radiansToDegrees(.pi / 2), 90, accuracy: 0.0001)
    }

    func testAngleNormalize() {
        XCTAssertEqual(Angle.normalize(3 * .pi), -.pi, accuracy: 0.0001)
        XCTAssertEqual(Angle.normalize(-3 * .pi), .pi, accuracy: 0.0001)
    }

    // MARK: - CollisionCategory Tests

    func testCollisionCategoryBit() {
        let cat0 = CollisionCategory.bit(0)
        XCTAssertEqual(cat0.rawValue, 1)

        let cat3 = CollisionCategory.bit(3)
        XCTAssertEqual(cat3.rawValue, 8)
    }

    func testCollisionCategoryUnion() {
        let combined: CollisionCategory = [.player, .enemy]
        XCTAssertTrue(combined.contains(.player))
        XCTAssertTrue(combined.contains(.enemy))
        XCTAssertFalse(combined.contains(.wall))
    }

    func testCollisionPresets() {
        let playerPreset = CollisionPresets.player()
        XCTAssertEqual(playerPreset.category, .player)
        XCTAssertTrue(playerPreset.collision.contains(.wall))
        XCTAssertTrue(playerPreset.contact.contains(.enemy))
    }
}
