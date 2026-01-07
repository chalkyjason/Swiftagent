# Agent Backlog

This file is used by the autonomous agent to track and manage tasks.
Tasks are organized by priority and status.

## In Progress

- [ ] [P1] Add CloudKit sync support to GameAuth package
- [ ] [P2] Implement leaderboard and achievements UI in CoreUI

## Pending

### High Priority
- [ ] [P1] Add iCloud save game support to persistence layer
- [ ] [P1] Implement Game Center leaderboard submission
- [ ] [P1] Add achievement tracking and display

### Medium Priority
- [ ] [P2] Create TapGame mini-game using MiniGameKit
- [ ] [P2] Add particle effects helper to PhysicsUtils
- [ ] [P2] Implement spatial audio in AudioEngine
- [ ] [P2] Add vibration patterns for iOS 17+ custom haptics
- [ ] [P2] Create AnimatedMenuBackground component for CoreUI

### Low Priority
- [ ] [P3] Add watchOS support to GameAuth
- [ ] [P3] Create tvOS-optimized menu navigation
- [ ] [P3] Add accessibility voiceover support to menus
- [ ] [P3] Implement analytics event tracking abstraction
- [ ] [P3] Add screenshot/screen recording prevention utility

### Enhancements
- [ ] Add SwiftData support alongside UserDefaults in SettingsManager
- [ ] Create onboarding/tutorial flow components
- [ ] Implement in-app purchase abstraction layer
- [ ] Add localization helpers for game strings
- [ ] Create shader helpers for visual effects

### Bug Fixes
- [ ] Investigate potential memory leak in sound preloading
- [ ] Fix GameLoop delta time calculation on first frame

### Documentation
- [ ] Add DocC documentation to all packages
- [ ] Create video tutorials for package integration
- [ ] Add more code examples to README files

## Completed

- [x] Create package directory structure
- [x] Implement GameAuth package with Game Center support
- [x] Implement CoreUI package with navigation and menus
- [x] Implement MiniGameKit package with game loop
- [x] Implement PhysicsUtils package with SpriteKit helpers
- [x] Implement AudioEngine package with sound and haptics
- [x] Create SpaceShooter sample app

---

## Agent Instructions

When processing this backlog:

1. **Priority Order**: Process tasks marked `[P1]` first, then `[P2]`, then `[P3]`
2. **Context Gathering**: Before starting a task, query the vector store for related code
3. **Testing**: Write tests alongside implementation
4. **Documentation**: Update README for any new features
5. **Commits**: Make atomic commits with clear messages

### Task Status Legend
- `[ ]` - Pending
- `[x]` - Completed
- Priority: `[P1]` High, `[P2]` Medium, `[P3]` Low

### Adding New Tasks
To add a task, append it to the appropriate section:
```markdown
- [ ] [P2] Description of the new task
```
