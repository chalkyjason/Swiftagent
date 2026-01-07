// swift-tools-version: 5.9
// The swift-tools-version declares the minimum version of Swift required to build this package.

import PackageDescription

let package = Package(
    name: "PhysicsUtils",
    platforms: [
        .iOS(.v16),
        .macOS(.v13),
        .tvOS(.v16)
    ],
    products: [
        .library(
            name: "PhysicsUtils",
            targets: ["PhysicsUtils"]
        ),
    ],
    dependencies: [],
    targets: [
        .target(
            name: "PhysicsUtils",
            dependencies: [],
            path: "Sources/PhysicsUtils"
        ),
        .testTarget(
            name: "PhysicsUtilsTests",
            dependencies: ["PhysicsUtils"],
            path: "Tests/PhysicsUtilsTests"
        ),
    ]
)
