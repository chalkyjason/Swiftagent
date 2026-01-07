// swift-tools-version: 5.9
// The swift-tools-version declares the minimum version of Swift required to build this package.

import PackageDescription

let package = Package(
    name: "CoreUI",
    platforms: [
        .iOS(.v16),
        .macOS(.v13),
        .tvOS(.v16)
    ],
    products: [
        .library(
            name: "CoreUI",
            targets: ["CoreUI"]
        ),
    ],
    dependencies: [],
    targets: [
        .target(
            name: "CoreUI",
            dependencies: [],
            path: "Sources/CoreUI"
        ),
        .testTarget(
            name: "CoreUITests",
            dependencies: ["CoreUI"],
            path: "Tests/CoreUITests"
        ),
    ]
)
