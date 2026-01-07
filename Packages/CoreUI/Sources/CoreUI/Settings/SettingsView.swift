import SwiftUI

/// A drop-in settings view that automatically generates UI from SettingsManager.
///
/// SettingsView creates appropriate controls (sliders, toggles, pickers)
/// based on the setting types, with full persistence handled automatically.
///
/// ## Usage
/// ```swift
/// NavigationStack {
///     SettingsView()
/// }
/// ```
///
/// ## Customization
/// ```swift
/// SettingsView(
///     sections: [.audio, .gameplay, .accessibility],
///     theme: .dark
/// )
/// ```
public struct SettingsView: View {
    @StateObject private var settings = SettingsManager.shared

    let sections: [SettingsSection]
    let theme: SettingsTheme
    let onDismiss: (() -> Void)?

    public init(
        sections: [SettingsSection] = SettingsSection.allCases,
        theme: SettingsTheme = .default,
        onDismiss: (() -> Void)? = nil
    ) {
        self.sections = sections
        self.theme = theme
        self.onDismiss = onDismiss
    }

    public var body: some View {
        Form {
            ForEach(sections, id: \.self) { section in
                sectionView(for: section)
            }

            Section {
                Button(role: .destructive) {
                    settings.resetToDefaults()
                } label: {
                    Label("Reset to Defaults", systemImage: "arrow.counterclockwise")
                }
            }
        }
        .navigationTitle("Settings")
        #if os(iOS)
        .navigationBarTitleDisplayMode(.large)
        #endif
        .toolbar {
            if let onDismiss = onDismiss {
                ToolbarItem(placement: .confirmationAction) {
                    Button("Done", action: onDismiss)
                }
            }
        }
    }

    @ViewBuilder
    private func sectionView(for section: SettingsSection) -> some View {
        switch section {
        case .audio:
            audioSection
        case .gameplay:
            gameplaySection
        case .feedback:
            feedbackSection
        case .accessibility:
            accessibilitySection
        case .developer:
            developerSection
        }
    }

    private var audioSection: some View {
        Section("Audio") {
            VolumeSlider(
                value: $settings.masterVolume,
                label: "Master Volume",
                icon: "speaker.wave.3.fill"
            )

            Toggle(isOn: $settings.musicEnabled) {
                Label("Music", systemImage: "music.note")
            }

            if settings.musicEnabled {
                VolumeSlider(
                    value: $settings.musicVolume,
                    label: "Music Volume",
                    icon: "music.note.list"
                )
            }

            Toggle(isOn: $settings.soundEnabled) {
                Label("Sound Effects", systemImage: "speaker.fill")
            }

            if settings.soundEnabled {
                VolumeSlider(
                    value: $settings.sfxVolume,
                    label: "SFX Volume",
                    icon: "waveform"
                )
            }
        }
    }

    private var gameplaySection: some View {
        Section("Gameplay") {
            Picker(selection: $settings.difficulty) {
                ForEach(GameDifficulty.allCases, id: \.self) { difficulty in
                    Text(difficulty.displayName).tag(difficulty)
                }
            } label: {
                Label("Difficulty", systemImage: "slider.horizontal.3")
            }

            Picker(selection: $settings.language) {
                Text("English").tag("en")
                Text("Spanish").tag("es")
                Text("French").tag("fr")
                Text("German").tag("de")
                Text("Japanese").tag("ja")
                Text("Chinese").tag("zh")
            } label: {
                Label("Language", systemImage: "globe")
            }
        }
    }

    private var feedbackSection: some View {
        Section("Feedback") {
            Toggle(isOn: $settings.hapticsEnabled) {
                Label("Haptic Feedback", systemImage: "hand.tap.fill")
            }

            Toggle(isOn: $settings.notificationsEnabled) {
                Label("Notifications", systemImage: "bell.fill")
            }
        }
    }

    private var accessibilitySection: some View {
        Section("Accessibility") {
            Toggle(isOn: $settings.reducedMotion) {
                Label("Reduced Motion", systemImage: "figure.walk.motion")
            }

            Picker(selection: $settings.colorBlindMode) {
                ForEach(ColorBlindMode.allCases, id: \.self) { mode in
                    Text(mode.displayName).tag(mode)
                }
            } label: {
                Label("Color Blind Mode", systemImage: "eye")
            }
        }
    }

    private var developerSection: some View {
        Section("Developer") {
            Toggle(isOn: $settings.showFPS) {
                Label("Show FPS Counter", systemImage: "speedometer")
            }

            Button {
                settings.tutorialCompleted = false
            } label: {
                Label("Reset Tutorial", systemImage: "book.closed")
            }
        }
    }
}

/// A themed volume slider control
public struct VolumeSlider: View {
    @Binding var value: Double
    let label: String
    let icon: String

    public init(value: Binding<Double>, label: String, icon: String) {
        self._value = value
        self.label = label
        self.icon = icon
    }

    public var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Label(label, systemImage: icon)
                .font(.subheadline)

            HStack {
                Image(systemName: iconForVolume(0))
                    .foregroundStyle(.secondary)

                Slider(value: $value, in: 0...1, step: 0.05)

                Image(systemName: iconForVolume(value))
                    .foregroundStyle(.secondary)
            }
        }
        .padding(.vertical, 4)
    }

    private func iconForVolume(_ volume: Double) -> String {
        switch volume {
        case 0:
            return "speaker.slash.fill"
        case 0..<0.33:
            return "speaker.fill"
        case 0.33..<0.66:
            return "speaker.wave.1.fill"
        case 0.66..<1.0:
            return "speaker.wave.2.fill"
        default:
            return "speaker.wave.3.fill"
        }
    }
}

/// Sections available in the settings view
public enum SettingsSection: String, CaseIterable {
    case audio
    case gameplay
    case feedback
    case accessibility
    case developer
}

/// Theme configuration for settings view
public struct SettingsTheme {
    public var accentColor: Color
    public var backgroundColor: Color

    public static let `default` = SettingsTheme(
        accentColor: .blue,
        backgroundColor: Color(.systemGroupedBackground)
    )

    public static let dark = SettingsTheme(
        accentColor: .cyan,
        backgroundColor: .black
    )

    public init(accentColor: Color, backgroundColor: Color) {
        self.accentColor = accentColor
        self.backgroundColor = backgroundColor
    }
}

// MARK: - Compact Settings View

/// A more compact settings view for in-game overlays
public struct CompactSettingsView: View {
    @StateObject private var settings = SettingsManager.shared

    public init() {}

    public var body: some View {
        VStack(spacing: 16) {
            // Audio quick controls
            HStack(spacing: 20) {
                Button {
                    settings.musicEnabled.toggle()
                } label: {
                    Image(systemName: settings.musicEnabled ? "music.note" : "music.note.slash")
                        .font(.title2)
                }

                Button {
                    settings.soundEnabled.toggle()
                } label: {
                    Image(systemName: settings.soundEnabled ? "speaker.wave.2.fill" : "speaker.slash.fill")
                        .font(.title2)
                }

                Button {
                    settings.hapticsEnabled.toggle()
                } label: {
                    Image(systemName: settings.hapticsEnabled ? "hand.tap.fill" : "hand.raised.slash.fill")
                        .font(.title2)
                }
            }

            // Volume slider
            HStack {
                Image(systemName: "speaker.fill")
                Slider(value: $settings.masterVolume)
                Image(systemName: "speaker.wave.3.fill")
            }
            .padding(.horizontal)
        }
        .padding()
        .background(.regularMaterial)
        .clipShape(RoundedRectangle(cornerRadius: 16))
    }
}

#if DEBUG
struct SettingsView_Previews: PreviewProvider {
    static var previews: some View {
        NavigationStack {
            SettingsView()
        }

        CompactSettingsView()
            .padding()
            .previewDisplayName("Compact")
    }
}
#endif
