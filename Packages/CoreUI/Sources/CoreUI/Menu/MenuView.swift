import SwiftUI

/// A data-driven menu view that renders MenuItems with customizable theming.
///
/// MenuView automatically adapts its appearance based on the provided MenuTheme,
/// allowing the same menu logic to look different across games.
///
/// ## Usage
/// ```swift
/// MenuView(
///     title: "My Game",
///     items: menuItems,
///     theme: .sciFi
/// )
/// ```
public struct MenuView: View {
    let title: String?
    let subtitle: String?
    let items: [MenuItem]
    let theme: MenuTheme

    public init(
        title: String? = nil,
        subtitle: String? = nil,
        items: [MenuItem],
        theme: MenuTheme = .default
    ) {
        self.title = title
        self.subtitle = subtitle
        self.items = items
        self.theme = theme
    }

    public var body: some View {
        VStack(spacing: theme.itemSpacing) {
            if let title = title {
                Text(title)
                    .font(theme.titleFont)
                    .foregroundStyle(theme.titleColor)

                if let subtitle = subtitle {
                    Text(subtitle)
                        .font(theme.subtitleFont)
                        .foregroundStyle(theme.subtitleColor)
                }

                Spacer()
                    .frame(height: theme.titleBottomPadding)
            }

            ForEach(items) { item in
                MenuItemView(item: item, theme: theme)
            }
        }
        .padding(theme.contentPadding)
        .background(theme.backgroundColor)
    }
}

/// A view that renders a single menu item.
public struct MenuItemView: View {
    let item: MenuItem
    let theme: MenuTheme
    @State private var isPressed = false

    public init(item: MenuItem, theme: MenuTheme = .default) {
        self.item = item
        self.theme = theme
    }

    public var body: some View {
        Button(action: item.action) {
            HStack(spacing: theme.iconSpacing) {
                if let icon = item.icon {
                    Image(systemName: icon)
                        .font(theme.iconFont)
                        .foregroundStyle(iconColor)
                        .frame(width: theme.iconSize, height: theme.iconSize)
                }

                VStack(alignment: .leading, spacing: 2) {
                    Text(item.title)
                        .font(itemFont)
                        .foregroundStyle(textColor)

                    if let subtitle = item.subtitle {
                        Text(subtitle)
                            .font(theme.itemSubtitleFont)
                            .foregroundStyle(subtitleColor)
                    }
                }

                Spacer()

                if let badge = item.badge {
                    Text(badge)
                        .font(theme.badgeFont)
                        .foregroundStyle(theme.badgeTextColor)
                        .padding(.horizontal, 8)
                        .padding(.vertical, 4)
                        .background(theme.badgeBackgroundColor)
                        .clipShape(Capsule())
                }

                if theme.showChevron && item.style != .primary {
                    Image(systemName: "chevron.right")
                        .font(.caption)
                        .foregroundStyle(theme.chevronColor)
                }
            }
            .padding(theme.itemPadding)
            .background(backgroundForStyle)
            .clipShape(RoundedRectangle(cornerRadius: theme.itemCornerRadius))
            .overlay(
                RoundedRectangle(cornerRadius: theme.itemCornerRadius)
                    .stroke(borderColor, lineWidth: theme.itemBorderWidth)
            )
            .scaleEffect(isPressed ? 0.98 : 1.0)
        }
        .buttonStyle(.plain)
        .disabled(!item.isEnabled)
        .opacity(item.isEnabled ? 1.0 : 0.5)
        .animation(.easeInOut(duration: 0.1), value: isPressed)
        .simultaneousGesture(
            DragGesture(minimumDistance: 0)
                .onChanged { _ in isPressed = true }
                .onEnded { _ in isPressed = false }
        )
    }

    private var itemFont: Font {
        switch item.style {
        case .primary:
            return theme.primaryItemFont
        default:
            return theme.itemFont
        }
    }

    private var textColor: Color {
        switch item.style {
        case .primary:
            return theme.primaryTextColor
        case .standard:
            return theme.itemTextColor
        case .secondary:
            return theme.secondaryTextColor
        case .destructive:
            return theme.destructiveTextColor
        case .disabled:
            return theme.disabledTextColor
        }
    }

    private var iconColor: Color {
        switch item.style {
        case .primary:
            return theme.primaryIconColor
        case .destructive:
            return theme.destructiveTextColor
        default:
            return theme.itemIconColor
        }
    }

    private var subtitleColor: Color {
        return theme.itemSubtitleColor
    }

    private var backgroundForStyle: some ShapeStyle {
        switch item.style {
        case .primary:
            return AnyShapeStyle(theme.primaryBackgroundColor)
        case .destructive:
            return AnyShapeStyle(theme.destructiveBackgroundColor)
        default:
            return AnyShapeStyle(theme.itemBackgroundColor)
        }
    }

    private var borderColor: Color {
        switch item.style {
        case .primary:
            return theme.primaryBorderColor
        default:
            return theme.itemBorderColor
        }
    }
}

/// A sectioned menu view for more complex menu structures.
public struct SectionedMenuView: View {
    let title: String?
    let sections: [MenuSection]
    let theme: MenuTheme

    public init(
        title: String? = nil,
        sections: [MenuSection],
        theme: MenuTheme = .default
    ) {
        self.title = title
        self.sections = sections
        self.theme = theme
    }

    public var body: some View {
        ScrollView {
            VStack(spacing: theme.sectionSpacing) {
                if let title = title {
                    Text(title)
                        .font(theme.titleFont)
                        .foregroundStyle(theme.titleColor)
                        .padding(.bottom, theme.titleBottomPadding)
                }

                ForEach(sections) { section in
                    VStack(alignment: .leading, spacing: theme.itemSpacing) {
                        if let header = section.header {
                            Text(header)
                                .font(theme.sectionHeaderFont)
                                .foregroundStyle(theme.sectionHeaderColor)
                                .padding(.horizontal, theme.contentPadding)
                        }

                        ForEach(section.items) { item in
                            MenuItemView(item: item, theme: theme)
                        }
                    }
                }
            }
            .padding(theme.contentPadding)
        }
        .background(theme.backgroundColor)
    }
}

// MARK: - Preview Helpers

#if DEBUG
struct MenuView_Previews: PreviewProvider {
    static var previews: some View {
        MenuView(
            title: "My Game",
            subtitle: "Version 1.0",
            items: MenuBuilder.mainMenu(
                onPlay: {},
                onSettings: {},
                onLeaderboard: {},
                onAchievements: {}
            ),
            theme: .default
        )
        .previewDisplayName("Default Theme")

        MenuView(
            title: "Space Commander",
            items: MenuBuilder.mainMenu(
                onPlay: {},
                onSettings: {}
            ),
            theme: .sciFi
        )
        .previewDisplayName("Sci-Fi Theme")
    }
}
#endif
