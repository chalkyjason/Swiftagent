// swift-tools-version: 5.9
// The swift-tools-version declares the minimum version of Swift required to build this package.

import PackageDescription

let package = Package(
    name: "MiniGameKit",
    platforms: [
        .iOS(.v16),
        .macOS(.v13),
        .tvOS(.v16)
    ],
    products: [
        .library(
            name: "MiniGameKit",
            targets: ["MiniGameKit"]
        ),
    ],
    dependencies: [],
    targets: [
        .target(
            name: "MiniGameKit",
            dependencies: [],
            path: "Sources/MiniGameKit"
        ),
        .testTarget(
            name: "MiniGameKitTests",
            dependencies: ["MiniGameKit"],
            path: "Tests/MiniGameKitTests"
        ),
    ]
)
