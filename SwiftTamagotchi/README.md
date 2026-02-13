# Swift Tamagotchi Game for iPhone 📱

A native iOS conversion of the Python Pygame Tamagotchi game, built with SwiftUI.

## 🎮 Features

- **Virtual Pet Simulation**: Complete care system with hunger, happiness, health, and energy stats
- **Real-time Progression**: Pet continues to age and stats change even when app is closed
- **Native iOS Design**: Beautiful SwiftUI interface optimized for iPhone
- **Persistent Save System**: Automatic saving using UserDefaults
- **Interactive Touch Controls**: Intuitive tap-based menu system
- **Pet Evolution**: Level up system based on pet age
- **State Management**: Different visual states (happy, sad, sick, sleeping, eating, playing, dead)
- **Pixel Art Style**: Adapted retro aesthetic for iOS

## 📋 Requirements

- iOS 15.0+
- Xcode 13.0+
- Swift 5.0+

## 🚀 Installation

1. Open Terminal and navigate to the SwiftTamagotchi directory
2. Open the project in Xcode:
   ```bash
   open SwiftTamagotchi.xcodeproj
   ```
3. Select your target device or simulator
4. Build and run (⌘+R)

## 🎯 How to Play

### Controls
- **Tap** any action button in the menu to interact with your pet
- **Stats button** shows detailed information about your pet
- **Save button** manually saves your progress (game auto-saves every 5 minutes)

### Actions
- **🍎 Feed**: Increases hunger and slightly boosts happiness
- **🎮 Play**: Greatly increases happiness but uses energy
- **💊 Medicine**: Restores health (pet won't like it much)
- **😴 Sleep**: Restores energy
- **📊 Stats**: View detailed pet statistics
- **💾 Save**: Manually save your progress

## 🐾 Pet Care Tips

- Keep all stats above 20 to maintain pet health
- A happy pet is a healthy pet - play regularly!
- Don't let your pet get too tired before playing
- Your pet ages in real-time, even when the app is closed
- The game auto-saves when you close the app

## 🎨 Pet States

Your pet will show different colors and emotions based on its condition:

- **😊 Happy** (Green): All stats are good
- **😢 Sad** (Blue): Happiness is low  
- **🤒 Sick** (Purple): Health is low or other stats are critically low
- **😴 Sleeping** (Gray): Energy is very low
- **🍽️ Eating** (Orange): Just been fed
- **🎮 Playing** (Yellow): Just played with
- **💀 Dead** (Red): Health reached zero (game over)

## 🏗️ Project Structure

```
SwiftTamagotchi/
├── SwiftTamagotchi/
│   ├── TamagotchiApp.swift          # Main app entry point
│   ├── Models/
│   │   ├── PetStates.swift          # Pet state enum
│   │   └── PetModel.swift           # Pet data model
│   ├── Views/
│   │   ├── ContentView.swift        # Main game view
│   │   ├── PetView.swift           # Pet visual representation
│   │   ├── StatsView.swift         # Statistics display
│   │   └── MenuView.swift          # Action menu
│   ├── ViewModels/
│   │   └── GameLogic.swift         # Game logic and state management
│   ├── Managers/
│   │   └── SaveManager.swift       # Save/load functionality
│   └── Info.plist                  # App configuration
└── README.md
```

## 🔧 Technical Implementation

### Architecture
- **MVVM Pattern**: Clean separation of concerns
- **ObservableObject**: Reactive UI updates
- **Combine Framework**: For reactive programming
- **SwiftUI**: Native iOS user interface
- **UserDefaults**: Persistent data storage

### Key Classes
- **Pet**: Main pet model with stats and behaviors
- **GameLogic**: Manages game state and timers
- **SaveManager**: Handles data persistence
- **PetView**: Custom SwiftUI pet renderer

### Features
- **Real-time Updates**: Timer-based stat progression
- **App Lifecycle Management**: Proper pause/resume handling  
- **Automatic Saving**: Periodic and app lifecycle saves
- **State Animations**: Smooth visual transitions
- **Touch Interactions**: Native iOS gesture handling

## 🎊 What's New from Python Version

### ✅ iOS Adaptations
- Native SwiftUI interface
- Touch-optimized controls
- iOS app lifecycle integration
- UserDefaults persistence
- Portrait orientation focus
- iOS-style animations

### 🆕 Enhanced Features
- Detailed stats view with descriptions
- Visual feedback for actions
- Better state management
- Improved error handling
- Native iOS notifications

## 🐛 Troubleshooting

### Common Issues
1. **Build Errors**: Make sure you're using Xcode 13+ and iOS 15+ deployment target
2. **Save Issues**: Check app permissions and device storage
3. **Performance**: Close other apps if experiencing lag

### Reset Pet
Use the menu button (⋯) in the top right and select "New Pet" to start over.

## 🔄 From Python to Swift

This iOS version maintains all core functionality from the original Python/Pygame version:

| Python Feature | Swift Implementation |
|---|---|
| Pygame graphics | SwiftUI custom views |
| JSON save files | UserDefaults persistence |
| Keyboard controls | Touch interactions |
| Pixel art rendering | Custom SwiftUI shapes |
| Game loop | Timer-based updates |
| Menu system | Native iOS navigation |

## 📱 Future Enhancements

- [ ] Sound effects and music
- [ ] Multiple pet types
- [ ] Achievement system  
- [ ] Widget support
- [ ] iCloud sync
- [ ] Apple Watch companion
- [ ] Share pet stats

---

Enjoy taking care of your pixelated companion on iOS! 🎮📱
