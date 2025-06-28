// swift-tools-version: 5.9
// The swift-tools-version declares the minimum version of Swift required to build this package.

import PackageDescription

let package = Package(
    name: "APUSHGraderCore",
    platforms: [
        .iOS(.v16),
        .macOS(.v13)
    ],
    products: [
        .library(
            name: "APUSHGraderCore",
            targets: ["APUSHGraderCore"]),
        .executable(
            name: "TestRunner",
            targets: ["TestRunner"]),
    ],
    targets: [
        .target(
            name: "APUSHGraderCore",
            dependencies: []),
        .executableTarget(
            name: "TestRunner",
            dependencies: ["APUSHGraderCore"]),
    ]
)