// swift-tools-version: 5.9
// The swift-tools-version declares the minimum version of Swift required to build this package.

import PackageDescription

let package = Package(
    name: "AudioEngine",
    platforms: [
        .iOS(.v16),
        .macOS(.v13),
        .tvOS(.v16)
    ],
    products: [
        .library(
            name: "AudioEngine",
            targets: ["AudioEngine"]
        ),
    ],
    dependencies: [],
    targets: [
        .target(
            name: "AudioEngine",
            dependencies: [],
            path: "Sources/AudioEngine"
        ),
        .testTarget(
            name: "AudioEngineTests",
            dependencies: ["AudioEngine"],
            path: "Tests/AudioEngineTests"
        ),
    ]
)
