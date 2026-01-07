// swift-tools-version: 5.9
// Sample game app demonstrating package integration

import PackageDescription

let package = Package(
    name: "SpaceShooter",
    platforms: [
        .iOS(.v16),
        .macOS(.v13)
    ],
    products: [
        .executable(
            name: "SpaceShooter",
            targets: ["SpaceShooter"]
        ),
    ],
    dependencies: [
        .package(path: "../../Packages/GameAuth"),
        .package(path: "../../Packages/CoreUI"),
        .package(path: "../../Packages/MiniGameKit"),
        .package(path: "../../Packages/PhysicsUtils"),
        .package(path: "../../Packages/AudioEngine"),
    ],
    targets: [
        .executableTarget(
            name: "SpaceShooter",
            dependencies: [
                "GameAuth",
                "CoreUI",
                "MiniGameKit",
                "PhysicsUtils",
                "AudioEngine"
            ],
            path: "Sources"
        ),
    ]
)
