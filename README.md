# Swiftagent - Autonomous Game Development Infrastructure

A comprehensive framework for building reusable iOS/macOS game components using Swift Package Manager, with a cross-platform .NET MAUI control panel and autonomous AI agents (OpenClaw + legacy Agent).

## Architecture Overview

```
/Swiftagent
├── /AgentUI                  # .NET MAUI cross-platform control panel
│   ├── /Platforms
│   │   ├── /MacCatalyst     # macOS (Mac Catalyst) support
│   │   ├── /Windows         # Windows 10+ support
│   │   ├── /iOS             # iOS 16+ support
│   │   └── /Android         # Android 5.0+ support
│   ├── /Services            # Agent monitoring, backlog, OpenClaw services
│   ├── /ViewModels          # MVVM view models (Dashboard, Backlog, Console, etc.)
│   ├── /Views               # XAML pages (Dashboard, OpenClaw, Skills, etc.)
│   └── /Models              # Data models (AgentState, OpenClawModels)
│
├── /OpenClaw                 # Python-based autonomous improvement agent
│   ├── agent.py             # Main OODA improvement loop
│   ├── config.py            # Configuration management
│   ├── safety.py            # Sandboxing and safety guards
│   ├── scanner.py           # Code quality scanner
│   ├── /skills              # Tool definitions and executor
│   └── /prompts             # System prompts
│
├── /Agent                    # Legacy Python agent infrastructure
│   ├── game_agent.py        # Main agent loop (OODA pattern)
│   ├── config.py            # Configuration management
│   ├── safety_wrapper.py    # Sandboxing and safety policies
│   ├── checkpoint_manager.py # State persistence and recovery
│   └── context_manager.py   # RAG and context optimization
│
├── /Apps                     # Concrete game implementations
│   └── /SpaceShooter        # Sample game demonstrating all packages
│
├── /Packages                 # Reusable Swift packages
│   ├── /GameAuth            # Game Center authentication
│   ├── /CoreUI              # Navigation, menus, settings
│   ├── /MiniGameKit         # Game loop and state management
│   ├── /PhysicsUtils        # SpriteKit helpers and vector math
│   └── /AudioEngine         # Sound effects, music, and haptics
│
└── BACKLOG.md               # Agent task queue
```

## Packages

### GameAuth
Game Center authentication and player identity management.

```swift
import GameAuth

// Automatic authentication on app launch
ContentView()
    .withGameCenterAuthentication()

// Manual authentication
await GameCenterManager.shared.authenticate()

// Check authentication state
switch GameCenterManager.shared.authenticationState {
case .authenticated(let playerID, let displayName):
    print("Welcome, \(displayName)!")
case .unauthenticated:
    print("Please sign in")
case .error(let error):
    print(error.localizedDescription)
}
```

### CoreUI
Navigation coordination, data-driven menus, and settings management.

```swift
import CoreUI

// Navigation with Coordinator pattern
@StateObject private var coordinator = DefaultGameCoordinator()

CoordinatedNavigationView(coordinator: coordinator) {
    MainMenuView()
}

// Data-driven menus
let items = MenuBuilder.mainMenu(
    onPlay: { coordinator.startGame() },
    onSettings: { coordinator.showSettings() }
)
MenuView(title: "My Game", items: items, theme: .sciFi)

// Drop-in settings view
SettingsView()  // Full persistence handled automatically
```

**Built-in Themes:**
- `.default` - Clean, modern appearance
- `.sciFi` - Futuristic cyan/blue theme
- `.fantasy` - Warm, parchment-like appearance
- `.retro` - Pixel-art inspired
- `.dark` - Minimalist dark theme

### MiniGameKit
Game loop, state management, and lifecycle handling.

```swift
import MiniGameKit

// Game loop with fixed timestep
@StateObject private var gameLoop = GameLoop(targetFPS: 60)

// Handle updates
gameLoop.onUpdate = { deltaTime in
    player.position += velocity * deltaTime
}

// State management
gameLoop.start()
gameLoop.pause()
gameLoop.resume()
gameLoop.stop()

// Score tracking
gameLoop.addScore(100)

// Auto-pause on app background
MyGameView()
    .autoPause(onPause: { gameLoop.pause() })

// Reusable pause overlay
PauseOverlay(
    isPresented: gameLoop.state == .paused,
    onResume: { gameLoop.resume() },
    onQuit: { coordinator.showMenu() }
)
```

### PhysicsUtils
SpriteKit helpers, collision categories, and vector math.

```swift
import PhysicsUtils

// Vector math extensions
let velocity = CGPoint(angle: .pi / 4, length: 100)
let normalized = velocity.normalized
let distance = point1.distance(to: point2)
let reflection = velocity.reflected(normal: surfaceNormal)
let midpoint = point1.lerp(to: point2, t: 0.5)

// Type-safe collision categories
extension CollisionCategory {
    static let player = CollisionCategory(rawValue: 1 << 0)
    static let enemy = CollisionCategory(rawValue: 1 << 1)
}

playerNode.physicsBody?.configure(
    category: .player,
    collidesWith: [.enemy, .wall],
    contactsWith: [.enemy, .collectible]
)

// BaseGameScene with built-in delta time
class MyScene: BaseGameScene {
    override func update(deltaTime: TimeInterval) {
        // Called every frame with proper delta time
    }

    override func handleTap(at location: CGPoint) {
        // Unified input for iOS and macOS
    }

    override func handleContact(_ contact: SKPhysicsContact, began: Bool) {
        // Physics contact handling
    }
}
```

### AudioEngine
Sound effects, background music, and haptic feedback.

```swift
import AudioEngine

// Sound effects
SoundManager.shared.playSound("explosion")
SoundManager.shared.playSound("laser", volume: 0.8, rate: 1.2, pan: -0.5)

// Preload for instant playback
SoundManager.shared.preloadSounds(["jump", "coin", "hit"])

// Background music
SoundManager.shared.playMusic("level_theme", loop: true, fadeIn: 2.0)
SoundManager.shared.pauseMusic()
SoundManager.shared.stopMusic(fadeOut: 1.0)

// Volume control
SoundManager.shared.masterVolume = 0.8
SoundManager.shared.musicVolume = 0.5
SoundManager.shared.sfxVolume = 1.0

// Haptic feedback
HapticFeedback.shared.impact(.medium)
HapticFeedback.shared.notification(.success)

// Game-specific patterns
HapticFeedback.shared.explosion()
HapticFeedback.shared.collect()
HapticFeedback.shared.damage()

// Custom patterns
HapticFeedback.shared.playPattern([
    .impact(.light),
    .wait(0.1),
    .impact(.heavy)
])
```

## Creating a New Game

1. Create a new app directory:
```bash
mkdir -p Apps/MyGame/Sources
```

2. Create `Package.swift`:
```swift
// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "MyGame",
    platforms: [.iOS(.v16)],
    dependencies: [
        .package(path: "../../Packages/GameAuth"),
        .package(path: "../../Packages/CoreUI"),
        .package(path: "../../Packages/MiniGameKit"),
        .package(path: "../../Packages/PhysicsUtils"),
        .package(path: "../../Packages/AudioEngine"),
    ],
    targets: [
        .executableTarget(
            name: "MyGame",
            dependencies: ["GameAuth", "CoreUI", "MiniGameKit", "PhysicsUtils", "AudioEngine"]
        ),
    ]
)
```

3. Create your app entry point in `Sources/MyGameApp.swift`

## AgentUI - Cross-Platform Control Panel (.NET MAUI)

A .NET MAUI app for monitoring and controlling the autonomous agents. Runs on Mac, Windows, iOS, and Android.

### Supported Platforms

| Platform | Status | Min Version |
|----------|--------|-------------|
| macOS (Mac Catalyst) | Supported | macOS 16.0+ |
| Windows | Supported | Windows 10 (17763+) |
| iOS | Supported | iOS 16.0+ |
| Android | Supported | API 21 (5.0+) |

### Pages

- **Dashboard** - Agent status overview, iteration tracking, cost monitoring
- **OpenClaw** - Chat interface and configuration for the OpenClaw agent
- **Skills** - Browse, enable/disable, and manage agent skills
- **Backlog** - View and manage the task backlog
- **Console** - Live agent log output
- **Safety & Cost** - Safety events, blocked commands, budget tracking
- **Settings** - Agent configuration (workspace path, model, budget, etc.)

### Prerequisites (Mac)

1. Install [.NET 8 SDK](https://dotnet.microsoft.com/download/dotnet/8.0)
2. Install the MAUI workload:
   ```bash
   sudo dotnet workload install maui
   ```
3. Xcode 15+ must be installed (for Mac Catalyst builds)

### Running on Mac

```bash
cd AgentUI

# Restore dependencies
dotnet restore

# Build and run on Mac (via Mac Catalyst)
dotnet build -f net8.0-maccatalyst
dotnet run -f net8.0-maccatalyst
```

### Running on Windows

```powershell
cd AgentUI

# Restore dependencies
dotnet restore

# Build and run on Windows
dotnet build -f net8.0-windows10.0.19041.0
dotnet run -f net8.0-windows10.0.19041.0
```

## OpenClaw - Autonomous Improvement Agent

The `/OpenClaw` directory contains a Python-based autonomous agent powered by Claude that iterates on the codebase using an OODA (Observe, Orient, Decide, Act) loop.

### Features

- Processes tasks from `BACKLOG.md` by priority
- 13 built-in skills: file read/write/patch, shell exec, swift build/test, git operations, code search
- Safety sandbox: path confinement, command blocklist, file size limits, safe deletion
- Code quality scanner: finds TODOs, force unwraps, empty catches, missing tests
- Daily cost budget enforcement

### Running OpenClaw

```bash
# Set your Anthropic API key
export ANTHROPIC_API_KEY=sk-ant-...

# Install dependencies
pip install -r OpenClaw/requirements.txt

# Run the agent
python -m OpenClaw

# With options
python -m OpenClaw --model claude-opus-4-6 --budget 10.0 --max-iterations 5
```

## Legacy Agent

The `/Agent` directory contains the original Python-based autonomous agent with RAG support.

### Running the Legacy Agent

```bash
cd Agent
pip install -r requirements.txt
python game_agent.py
```

### Agent Configuration

Configure via environment variables:
```bash
export AGENT_WORKSPACE_ROOT=/path/to/workspace
export AGENT_DAILY_BUDGET=5.0
export AGENT_LOG_LEVEL=INFO
```

### Safety Features (both agents)

- **Sandboxing**: Agent confined to workspace directory
- **Command filtering**: Dangerous commands blocked
- **Safe deletion**: Files moved to trash, not deleted
- **Budget caps**: Daily spending limits
- **Checkpointing**: State recovery after crashes

## Requirements

| Component | Requirements |
|-----------|-------------|
| Swift Packages | Swift 5.9+, Xcode 15+, iOS 16+ / macOS 13+ / tvOS 16+ |
| AgentUI (MAUI) | .NET 8 SDK, MAUI workload, Xcode 15+ (Mac) or VS 2022 (Windows) |
| OpenClaw Agent | Python 3.10+, Anthropic API key |
| Legacy Agent | Python 3.10+ |

## Building Swift Packages

```bash
# Build all packages
swift build

# Run tests
swift test

# Build specific package
cd Packages/GameAuth
swift build
```

## License

MIT License - See LICENSE file for details.

## Contributing

Contributions are welcome! Please read the contributing guidelines before submitting PRs.

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

---

*Built with the Claude Agent SDK for autonomous software development*
