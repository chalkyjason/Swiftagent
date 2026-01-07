import SwiftUI

/// Defines the visual appearance of menus.
///
/// MenuTheme allows complete customization of menu appearance,
/// enabling the same menu logic to render differently for various games.
///
/// ## Built-in Themes
/// - `.default`: Clean, modern appearance
/// - `.sciFi`: Futuristic blue/cyan theme
/// - `.fantasy`: Warm, parchment-like appearance
/// - `.retro`: Pixel-art inspired theme
///
/// ## Custom Themes
/// ```swift
/// let customTheme = MenuTheme(
///     backgroundColor: .purple,
///     itemBackgroundColor: .purple.opacity(0.3),
///     titleFont: .custom("Papyrus", size: 32),
///     // ... other customizations
/// )
/// ```
public struct MenuTheme: Sendable {
    // MARK: - Background

    /// Background color for the entire menu
    public var backgroundColor: Color

    // MARK: - Title

    public var titleFont: Font
    public var titleColor: Color
    public var subtitleFont: Font
    public var subtitleColor: Color
    public var titleBottomPadding: CGFloat

    // MARK: - Item Styling

    public var itemFont: Font
    public var primaryItemFont: Font
    public var itemSubtitleFont: Font
    public var itemTextColor: Color
    public var primaryTextColor: Color
    public var secondaryTextColor: Color
    public var destructiveTextColor: Color
    public var disabledTextColor: Color
    public var itemSubtitleColor: Color

    public var itemBackgroundColor: Color
    public var primaryBackgroundColor: Color
    public var destructiveBackgroundColor: Color

    public var itemBorderColor: Color
    public var primaryBorderColor: Color
    public var itemBorderWidth: CGFloat
    public var itemCornerRadius: CGFloat

    // MARK: - Icons

    public var iconFont: Font
    public var iconSize: CGFloat
    public var iconSpacing: CGFloat
    public var itemIconColor: Color
    public var primaryIconColor: Color

    // MARK: - Badges

    public var badgeFont: Font
    public var badgeTextColor: Color
    public var badgeBackgroundColor: Color

    // MARK: - Chevrons

    public var showChevron: Bool
    public var chevronColor: Color

    // MARK: - Layout

    public var contentPadding: CGFloat
    public var itemPadding: EdgeInsets
    public var itemSpacing: CGFloat
    public var sectionSpacing: CGFloat
    public var sectionHeaderFont: Font
    public var sectionHeaderColor: Color

    // MARK: - Initialization

    public init(
        backgroundColor: Color = Color(.systemBackground),
        titleFont: Font = .largeTitle.bold(),
        titleColor: Color = .primary,
        subtitleFont: Font = .subheadline,
        subtitleColor: Color = .secondary,
        titleBottomPadding: CGFloat = 32,
        itemFont: Font = .headline,
        primaryItemFont: Font = .headline.bold(),
        itemSubtitleFont: Font = .caption,
        itemTextColor: Color = .primary,
        primaryTextColor: Color = .white,
        secondaryTextColor: Color = .secondary,
        destructiveTextColor: Color = .red,
        disabledTextColor: Color = .gray,
        itemSubtitleColor: Color = .secondary,
        itemBackgroundColor: Color = Color(.secondarySystemBackground),
        primaryBackgroundColor: Color = .blue,
        destructiveBackgroundColor: Color = Color.red.opacity(0.1),
        itemBorderColor: Color = .clear,
        primaryBorderColor: Color = .clear,
        itemBorderWidth: CGFloat = 0,
        itemCornerRadius: CGFloat = 12,
        iconFont: Font = .title3,
        iconSize: CGFloat = 24,
        iconSpacing: CGFloat = 12,
        itemIconColor: Color = .blue,
        primaryIconColor: Color = .white,
        badgeFont: Font = .caption.bold(),
        badgeTextColor: Color = .white,
        badgeBackgroundColor: Color = .red,
        showChevron: Bool = false,
        chevronColor: Color = .secondary,
        contentPadding: CGFloat = 20,
        itemPadding: EdgeInsets = EdgeInsets(top: 16, leading: 16, bottom: 16, trailing: 16),
        itemSpacing: CGFloat = 12,
        sectionSpacing: CGFloat = 24,
        sectionHeaderFont: Font = .footnote.bold(),
        sectionHeaderColor: Color = .secondary
    ) {
        self.backgroundColor = backgroundColor
        self.titleFont = titleFont
        self.titleColor = titleColor
        self.subtitleFont = subtitleFont
        self.subtitleColor = subtitleColor
        self.titleBottomPadding = titleBottomPadding
        self.itemFont = itemFont
        self.primaryItemFont = primaryItemFont
        self.itemSubtitleFont = itemSubtitleFont
        self.itemTextColor = itemTextColor
        self.primaryTextColor = primaryTextColor
        self.secondaryTextColor = secondaryTextColor
        self.destructiveTextColor = destructiveTextColor
        self.disabledTextColor = disabledTextColor
        self.itemSubtitleColor = itemSubtitleColor
        self.itemBackgroundColor = itemBackgroundColor
        self.primaryBackgroundColor = primaryBackgroundColor
        self.destructiveBackgroundColor = destructiveBackgroundColor
        self.itemBorderColor = itemBorderColor
        self.primaryBorderColor = primaryBorderColor
        self.itemBorderWidth = itemBorderWidth
        self.itemCornerRadius = itemCornerRadius
        self.iconFont = iconFont
        self.iconSize = iconSize
        self.iconSpacing = iconSpacing
        self.itemIconColor = itemIconColor
        self.primaryIconColor = primaryIconColor
        self.badgeFont = badgeFont
        self.badgeTextColor = badgeTextColor
        self.badgeBackgroundColor = badgeBackgroundColor
        self.showChevron = showChevron
        self.chevronColor = chevronColor
        self.contentPadding = contentPadding
        self.itemPadding = itemPadding
        self.itemSpacing = itemSpacing
        self.sectionSpacing = sectionSpacing
        self.sectionHeaderFont = sectionHeaderFont
        self.sectionHeaderColor = sectionHeaderColor
    }
}

// MARK: - Built-in Themes

public extension MenuTheme {
    /// Default clean theme
    static let `default` = MenuTheme()

    /// Sci-fi/futuristic theme with cyan accents
    static let sciFi = MenuTheme(
        backgroundColor: Color(red: 0.05, green: 0.05, blue: 0.15),
        titleFont: .system(size: 36, weight: .black, design: .rounded),
        titleColor: Color.cyan,
        subtitleColor: Color.cyan.opacity(0.7),
        itemFont: .system(size: 16, weight: .medium, design: .monospaced),
        primaryItemFont: .system(size: 18, weight: .bold, design: .monospaced),
        itemTextColor: Color.cyan.opacity(0.9),
        primaryTextColor: Color.black,
        secondaryTextColor: Color.cyan.opacity(0.6),
        destructiveTextColor: Color.red,
        itemBackgroundColor: Color.cyan.opacity(0.1),
        primaryBackgroundColor: Color.cyan,
        destructiveBackgroundColor: Color.red.opacity(0.2),
        itemBorderColor: Color.cyan.opacity(0.3),
        primaryBorderColor: Color.cyan,
        itemBorderWidth: 1,
        itemCornerRadius: 4,
        itemIconColor: Color.cyan,
        primaryIconColor: Color.black,
        badgeBackgroundColor: Color.orange,
        contentPadding: 24,
        itemPadding: EdgeInsets(top: 14, leading: 20, bottom: 14, trailing: 20)
    )

    /// Fantasy/medieval theme
    static let fantasy = MenuTheme(
        backgroundColor: Color(red: 0.95, green: 0.9, blue: 0.8),
        titleFont: .system(size: 34, weight: .bold, design: .serif),
        titleColor: Color(red: 0.4, green: 0.2, blue: 0.1),
        subtitleColor: Color(red: 0.5, green: 0.35, blue: 0.2),
        itemFont: .system(size: 17, weight: .medium, design: .serif),
        primaryItemFont: .system(size: 19, weight: .bold, design: .serif),
        itemTextColor: Color(red: 0.3, green: 0.2, blue: 0.1),
        primaryTextColor: Color(red: 0.95, green: 0.9, blue: 0.8),
        destructiveTextColor: Color(red: 0.6, green: 0.1, blue: 0.1),
        itemBackgroundColor: Color(red: 0.85, green: 0.75, blue: 0.6),
        primaryBackgroundColor: Color(red: 0.5, green: 0.3, blue: 0.15),
        destructiveBackgroundColor: Color(red: 0.6, green: 0.1, blue: 0.1).opacity(0.2),
        itemBorderColor: Color(red: 0.6, green: 0.45, blue: 0.3),
        primaryBorderColor: Color(red: 0.3, green: 0.2, blue: 0.1),
        itemBorderWidth: 2,
        itemCornerRadius: 8,
        itemIconColor: Color(red: 0.5, green: 0.35, blue: 0.2),
        primaryIconColor: Color(red: 0.95, green: 0.85, blue: 0.7),
        contentPadding: 28,
        itemSpacing: 14
    )

    /// Retro/pixel art theme
    static let retro = MenuTheme(
        backgroundColor: Color(red: 0.1, green: 0.1, blue: 0.1),
        titleFont: .system(size: 28, weight: .black),
        titleColor: Color.green,
        subtitleColor: Color.green.opacity(0.7),
        itemFont: .system(size: 16, weight: .bold),
        primaryItemFont: .system(size: 18, weight: .black),
        itemTextColor: Color.green,
        primaryTextColor: Color.black,
        destructiveTextColor: Color.red,
        itemBackgroundColor: Color.green.opacity(0.15),
        primaryBackgroundColor: Color.green,
        itemBorderColor: Color.green,
        primaryBorderColor: Color.green,
        itemBorderWidth: 3,
        itemCornerRadius: 0,
        itemIconColor: Color.green,
        primaryIconColor: Color.black,
        badgeBackgroundColor: Color.yellow,
        badgeTextColor: Color.black,
        itemPadding: EdgeInsets(top: 12, leading: 16, bottom: 12, trailing: 16),
        itemSpacing: 8
    )

    /// Minimalist dark theme
    static let dark = MenuTheme(
        backgroundColor: Color.black,
        titleFont: .system(size: 32, weight: .thin),
        titleColor: Color.white,
        subtitleColor: Color.white.opacity(0.5),
        itemFont: .system(size: 17, weight: .light),
        primaryItemFont: .system(size: 17, weight: .medium),
        itemTextColor: Color.white.opacity(0.9),
        primaryTextColor: Color.black,
        destructiveTextColor: Color.red,
        itemBackgroundColor: Color.white.opacity(0.05),
        primaryBackgroundColor: Color.white,
        itemBorderColor: Color.white.opacity(0.1),
        itemBorderWidth: 1,
        itemCornerRadius: 16,
        itemIconColor: Color.white.opacity(0.7),
        primaryIconColor: Color.black,
        itemSpacing: 16
    )
}
