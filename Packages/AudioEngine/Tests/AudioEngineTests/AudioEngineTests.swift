import XCTest
@testable import AudioEngine

final class AudioEngineTests: XCTestCase {

    // MARK: - SoundManager Tests

    @MainActor
    func testSoundManagerSingleton() {
        let manager1 = SoundManager.shared
        let manager2 = SoundManager.shared

        XCTAssertTrue(manager1 === manager2)
    }

    @MainActor
    func testSoundManagerDefaultValues() {
        let manager = SoundManager.shared

        XCTAssertEqual(manager.masterVolume, 1.0)
        XCTAssertEqual(manager.sfxVolume, 1.0)
        XCTAssertEqual(manager.musicVolume, 0.7)
        XCTAssertTrue(manager.isSfxEnabled)
        XCTAssertTrue(manager.isMusicEnabled)
    }

    @MainActor
    func testSoundManagerVolumeSettings() {
        let manager = SoundManager.shared

        manager.masterVolume = 0.5
        XCTAssertEqual(manager.masterVolume, 0.5)

        manager.sfxVolume = 0.8
        XCTAssertEqual(manager.sfxVolume, 0.8)

        manager.musicVolume = 0.3
        XCTAssertEqual(manager.musicVolume, 0.3)

        // Reset for other tests
        manager.masterVolume = 1.0
        manager.sfxVolume = 1.0
        manager.musicVolume = 0.7
    }

    @MainActor
    func testSoundManagerDisabledSound() {
        let manager = SoundManager.shared

        manager.isSfxEnabled = false
        let result = manager.playSound("nonexistent_sound")
        XCTAssertFalse(result)

        manager.isSfxEnabled = true
    }

    @MainActor
    func testSoundManagerCurrentMusicTrack() {
        let manager = SoundManager.shared

        XCTAssertNil(manager.currentMusicTrack)
    }

    // MARK: - HapticFeedback Tests

    @MainActor
    func testHapticFeedbackSingleton() {
        let feedback1 = HapticFeedback.shared
        let feedback2 = HapticFeedback.shared

        XCTAssertTrue(feedback1 === feedback2)
    }

    @MainActor
    func testHapticFeedbackDefaultValues() {
        let feedback = HapticFeedback.shared

        XCTAssertTrue(feedback.isEnabled)
        XCTAssertEqual(feedback.intensity, 1.0)
    }

    @MainActor
    func testHapticFeedbackEnableDisable() {
        let feedback = HapticFeedback.shared

        feedback.isEnabled = false
        XCTAssertFalse(feedback.isEnabled)

        feedback.isEnabled = true
        XCTAssertTrue(feedback.isEnabled)
    }

    @MainActor
    func testHapticFeedbackIntensity() {
        let feedback = HapticFeedback.shared

        feedback.intensity = 0.5
        XCTAssertEqual(feedback.intensity, 0.5)

        feedback.intensity = 1.0
    }

    // MARK: - Impact Style Tests

    func testImpactStyleValues() {
        // Ensure all cases are available
        let styles: [ImpactStyle] = [.light, .medium, .heavy, .soft, .rigid]
        XCTAssertEqual(styles.count, 5)
    }

    // MARK: - Notification Type Tests

    func testNotificationTypeValues() {
        let types: [NotificationType] = [.success, .warning, .error]
        XCTAssertEqual(types.count, 3)
    }

    // MARK: - Haptic Event Tests

    func testHapticEventCreation() {
        let impactEvent = HapticEvent.impact(.medium)
        let waitEvent = HapticEvent.wait(0.1)
        let notificationEvent = HapticEvent.notification(.success)
        let selectionEvent = HapticEvent.selection
        let continuousEvent = HapticEvent.continuous(intensity: 0.5, sharpness: 0.5, duration: 0.2)

        // Just verify they can be created (no crashes)
        _ = [impactEvent, waitEvent, notificationEvent, selectionEvent, continuousEvent]
    }

    // MARK: - UI Sound Tests

    func testUISoundRawValues() {
        XCTAssertEqual(SoundManager.UISound.tap.rawValue, "ui_tap")
        XCTAssertEqual(SoundManager.UISound.success.rawValue, "ui_success")
        XCTAssertEqual(SoundManager.UISound.error.rawValue, "ui_error")
        XCTAssertEqual(SoundManager.UISound.swoosh.rawValue, "ui_swoosh")
        XCTAssertEqual(SoundManager.UISound.coin.rawValue, "coin")
        XCTAssertEqual(SoundManager.UISound.powerUp.rawValue, "power_up")
    }
}
