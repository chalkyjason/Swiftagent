import Foundation

#if os(iOS)
import UIKit
import CoreHaptics
#endif

/// Manages haptic feedback for games.
///
/// HapticFeedback provides a simple API for triggering various
/// haptic patterns on supported devices.
///
/// ## Usage
/// ```swift
/// // Simple feedback
/// HapticFeedback.shared.impact(.medium)
///
/// // Game events
/// HapticFeedback.shared.notification(.success)
///
/// // Custom patterns
/// HapticFeedback.shared.playPattern([
///     .impact(.light),
///     .wait(0.1),
///     .impact(.heavy)
/// ])
/// ```
@MainActor
public final class HapticFeedback: ObservableObject {
    // MARK: - Singleton

    /// Shared instance of the haptic feedback manager
    public static let shared = HapticFeedback()

    // MARK: - Published Properties

    /// Whether haptic feedback is enabled
    @Published public var isEnabled: Bool = true

    /// Intensity multiplier (0.0 - 1.0)
    @Published public var intensity: Float = 1.0

    // MARK: - Private Properties

    #if os(iOS)
    private var impactGeneratorLight: UIImpactFeedbackGenerator?
    private var impactGeneratorMedium: UIImpactFeedbackGenerator?
    private var impactGeneratorHeavy: UIImpactFeedbackGenerator?
    private var impactGeneratorSoft: UIImpactFeedbackGenerator?
    private var impactGeneratorRigid: UIImpactFeedbackGenerator?
    private var notificationGenerator: UINotificationFeedbackGenerator?
    private var selectionGenerator: UISelectionFeedbackGenerator?

    private var hapticEngine: CHHapticEngine?
    private var supportsHaptics: Bool = false
    #endif

    // MARK: - Initialization

    private init() {
        #if os(iOS)
        setupGenerators()
        setupHapticEngine()
        #endif
    }

    #if os(iOS)
    private func setupGenerators() {
        impactGeneratorLight = UIImpactFeedbackGenerator(style: .light)
        impactGeneratorMedium = UIImpactFeedbackGenerator(style: .medium)
        impactGeneratorHeavy = UIImpactFeedbackGenerator(style: .heavy)
        impactGeneratorSoft = UIImpactFeedbackGenerator(style: .soft)
        impactGeneratorRigid = UIImpactFeedbackGenerator(style: .rigid)
        notificationGenerator = UINotificationFeedbackGenerator()
        selectionGenerator = UISelectionFeedbackGenerator()

        // Prepare generators for faster response
        impactGeneratorLight?.prepare()
        impactGeneratorMedium?.prepare()
        impactGeneratorHeavy?.prepare()
        notificationGenerator?.prepare()
        selectionGenerator?.prepare()
    }

    private func setupHapticEngine() {
        supportsHaptics = CHHapticEngine.capabilitiesForHardware().supportsHaptics

        guard supportsHaptics else { return }

        do {
            hapticEngine = try CHHapticEngine()
            hapticEngine?.playsHapticsOnly = true

            // Handle engine reset
            hapticEngine?.resetHandler = { [weak self] in
                do {
                    try self?.hapticEngine?.start()
                } catch {
                    print("Failed to restart haptic engine: \(error)")
                }
            }

            // Handle engine stop
            hapticEngine?.stoppedHandler = { reason in
                print("Haptic engine stopped: \(reason)")
            }

            try hapticEngine?.start()
        } catch {
            print("Failed to create haptic engine: \(error)")
        }
    }
    #endif

    // MARK: - Public Methods

    /// Triggers an impact haptic
    public func impact(_ style: ImpactStyle, intensity: CGFloat? = nil) {
        guard isEnabled else { return }

        #if os(iOS)
        let effectiveIntensity = intensity ?? CGFloat(self.intensity)

        switch style {
        case .light:
            impactGeneratorLight?.impactOccurred(intensity: effectiveIntensity)
        case .medium:
            impactGeneratorMedium?.impactOccurred(intensity: effectiveIntensity)
        case .heavy:
            impactGeneratorHeavy?.impactOccurred(intensity: effectiveIntensity)
        case .soft:
            impactGeneratorSoft?.impactOccurred(intensity: effectiveIntensity)
        case .rigid:
            impactGeneratorRigid?.impactOccurred(intensity: effectiveIntensity)
        }
        #endif
    }

    /// Triggers a notification haptic
    public func notification(_ type: NotificationType) {
        guard isEnabled else { return }

        #if os(iOS)
        switch type {
        case .success:
            notificationGenerator?.notificationOccurred(.success)
        case .warning:
            notificationGenerator?.notificationOccurred(.warning)
        case .error:
            notificationGenerator?.notificationOccurred(.error)
        }
        #endif
    }

    /// Triggers a selection haptic (light tap)
    public func selection() {
        guard isEnabled else { return }

        #if os(iOS)
        selectionGenerator?.selectionChanged()
        #endif
    }

    /// Plays a custom haptic pattern
    public func playPattern(_ pattern: [HapticEvent]) {
        guard isEnabled else { return }

        #if os(iOS)
        guard supportsHaptics, let engine = hapticEngine else {
            // Fallback to basic haptics
            playPatternFallback(pattern)
            return
        }

        do {
            let events = pattern.compactMap { $0.toCHHapticEvent() }
            let pattern = try CHHapticPattern(events: events, parameters: [])
            let player = try engine.makePlayer(with: pattern)
            try player.start(atTime: CHHapticTimeImmediate)
        } catch {
            print("Failed to play haptic pattern: \(error)")
            playPatternFallback(pattern)
        }
        #endif
    }

    #if os(iOS)
    private func playPatternFallback(_ pattern: [HapticEvent]) {
        var delay: TimeInterval = 0

        for event in pattern {
            switch event {
            case .impact(let style):
                DispatchQueue.main.asyncAfter(deadline: .now() + delay) { [weak self] in
                    self?.impact(style)
                }
            case .notification(let type):
                DispatchQueue.main.asyncAfter(deadline: .now() + delay) { [weak self] in
                    self?.notification(type)
                }
            case .selection:
                DispatchQueue.main.asyncAfter(deadline: .now() + delay) { [weak self] in
                    self?.selection()
                }
            case .wait(let duration):
                delay += duration
            case .continuous:
                // Not supported in fallback
                break
            }
        }
    }
    #endif

    /// Prepares the haptic generators for lower latency
    public func prepare() {
        #if os(iOS)
        impactGeneratorLight?.prepare()
        impactGeneratorMedium?.prepare()
        impactGeneratorHeavy?.prepare()
        notificationGenerator?.prepare()
        selectionGenerator?.prepare()
        #endif
    }

    // MARK: - Convenience Methods

    /// Quick tap feedback for buttons
    public func tap() {
        impact(.light)
    }

    /// Feedback for successful actions
    public func success() {
        notification(.success)
    }

    /// Feedback for errors
    public func error() {
        notification(.error)
    }

    /// Feedback for collisions (medium impact)
    public func collision() {
        impact(.medium)
    }

    /// Feedback for explosions (heavy impact)
    public func explosion() {
        impact(.heavy)
    }

    /// Feedback for collecting items
    public func collect() {
        playPattern([
            .impact(.light),
            .wait(0.05),
            .impact(.soft)
        ])
    }

    /// Feedback for power-ups
    public func powerUp() {
        playPattern([
            .impact(.soft),
            .wait(0.1),
            .impact(.medium),
            .wait(0.1),
            .impact(.heavy)
        ])
    }

    /// Feedback for damage taken
    public func damage() {
        playPattern([
            .impact(.rigid),
            .wait(0.05),
            .impact(.heavy)
        ])
    }
}

// MARK: - Types

/// Impact feedback styles
public enum ImpactStyle: Sendable {
    case light
    case medium
    case heavy
    case soft
    case rigid
}

/// Notification feedback types
public enum NotificationType: Sendable {
    case success
    case warning
    case error
}

/// Events for custom haptic patterns
public enum HapticEvent: Sendable {
    case impact(ImpactStyle)
    case notification(NotificationType)
    case selection
    case wait(TimeInterval)
    case continuous(intensity: Float, sharpness: Float, duration: TimeInterval)

    #if os(iOS)
    func toCHHapticEvent() -> CHHapticEvent? {
        switch self {
        case .impact(let style):
            let intensity: Float
            let sharpness: Float

            switch style {
            case .light:
                intensity = 0.3
                sharpness = 0.5
            case .medium:
                intensity = 0.5
                sharpness = 0.5
            case .heavy:
                intensity = 1.0
                sharpness = 0.5
            case .soft:
                intensity = 0.5
                sharpness = 0.0
            case .rigid:
                intensity = 0.5
                sharpness = 1.0
            }

            return CHHapticEvent(
                eventType: .hapticTransient,
                parameters: [
                    CHHapticEventParameter(parameterID: .hapticIntensity, value: intensity),
                    CHHapticEventParameter(parameterID: .hapticSharpness, value: sharpness)
                ],
                relativeTime: 0
            )

        case .continuous(let intensity, let sharpness, let duration):
            return CHHapticEvent(
                eventType: .hapticContinuous,
                parameters: [
                    CHHapticEventParameter(parameterID: .hapticIntensity, value: intensity),
                    CHHapticEventParameter(parameterID: .hapticSharpness, value: sharpness)
                ],
                relativeTime: 0,
                duration: duration
            )

        case .notification, .selection, .wait:
            return nil
        }
    }
    #endif
}
