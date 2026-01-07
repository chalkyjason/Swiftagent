// swift-tools-version: 5.9
// The swift-tools-version declares the minimum version of Swift required to build this package.

import PackageDescription

let package = Package(
    name: "GameAuth",
    platforms: [
        .iOS(.v16),
        .macOS(.v13),
        .tvOS(.v16)
    ],
    products: [
        .library(
            name: "GameAuth",
            targets: ["GameAuth"]
        ),
    ],
    dependencies: [],
    targets: [
        .target(
            name: "GameAuth",
            dependencies: [],
            path: "Sources/GameAuth"
        ),
        .testTarget(
            name: "GameAuthTests",
            dependencies: ["GameAuth"],
            path: "Tests/GameAuthTests"
        ),
    ]
)
