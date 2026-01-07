/// AudioEngine - Sound Effects, Music, and Haptic Feedback
///
/// A Swift package for managing audio and haptic feedback in games.
///
/// ## Overview
///
/// AudioEngine provides:
/// 1. **SoundManager**: Play and manage sound effects and music
/// 2. **HapticFeedback**: Trigger haptic feedback patterns
///
/// ## Quick Start
///
/// ### Sound Effects
/// ```swift
/// // Play a sound
/// SoundManager.shared.playSound("explosion")
///
/// // Play with options
/// SoundManager.shared.playSound("laser", volume: 0.8, rate: 1.2, pan: -0.5)
///
/// // Preload sounds for instant playback
/// SoundManager.shared.preloadSounds(["jump", "coin", "hit"])
/// ```
///
/// ### Background Music
/// ```swift
/// // Play music with fade-in
/// SoundManager.shared.playMusic("level_theme", loop: true, fadeIn: 2.0)
///
/// // Control music
/// SoundManager.shared.pauseMusic()
/// SoundManager.shared.resumeMusic()
/// SoundManager.shared.stopMusic(fadeOut: 1.0)
/// ```
///
/// ### Volume Control
/// ```swift
/// // Master volume affects everything
/// SoundManager.shared.masterVolume = 0.8
///
/// // Individual control
/// SoundManager.shared.sfxVolume = 1.0
/// SoundManager.shared.musicVolume = 0.5
///
/// // Enable/disable
/// SoundManager.shared.isSfxEnabled = true
/// SoundManager.shared.isMusicEnabled = false
/// ```
///
/// ### Haptic Feedback
/// ```swift
/// // Simple feedback
/// HapticFeedback.shared.impact(.medium)
/// HapticFeedback.shared.notification(.success)
///
/// // Game-specific patterns
/// HapticFeedback.shared.explosion()
/// HapticFeedback.shared.collect()
/// HapticFeedback.shared.damage()
///
/// // Custom patterns
/// HapticFeedback.shared.playPattern([
///     .impact(.light),
///     .wait(0.1),
///     .impact(.heavy)
/// ])
/// ```
///
/// ## Integration with Settings
/// ```swift
/// // Sync with SettingsManager
/// $settings.masterVolume
///     .sink { SoundManager.shared.masterVolume = Float($0) }
///
/// $settings.hapticsEnabled
///     .sink { HapticFeedback.shared.isEnabled = $0 }
/// ```
///
/// ## Features
///
/// - **AVFoundation Based**: Uses native iOS/macOS audio
/// - **Preloading**: Load sounds in advance for zero-latency playback
/// - **Core Haptics**: Advanced haptic patterns on supported devices
/// - **Observable**: SwiftUI-ready with `@Published` properties

@_exported import AVFoundation

// Package version
public let audioEngineVersion = "1.0.0"
