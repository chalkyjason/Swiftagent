using System.Globalization;
using AgentUI.Models;

namespace AgentUI.Converters;

public class PhaseToColorConverter : IValueConverter
{
    public object? Convert(object? value, Type targetType, object? parameter, CultureInfo culture)
    {
        if (value is not AgentPhase phase) return Colors.Grey;
        return phase switch
        {
            AgentPhase.Observe => Color.FromArgb("#00d4ff"),
            AgentPhase.Orient => Color.FromArgb("#d500f9"),
            AgentPhase.Decide => Color.FromArgb("#ffea00"),
            AgentPhase.Act => Color.FromArgb("#00e676"),
            AgentPhase.Verify => Color.FromArgb("#ff9100"),
            AgentPhase.Commit => Color.FromArgb("#00e676"),
            _ => Color.FromArgb("#6c757d")
        };
    }

    public object? ConvertBack(object? value, Type targetType, object? parameter, CultureInfo culture)
        => null;
}

public class BoolToRunningTextConverter : IValueConverter
{
    public object? Convert(object? value, Type targetType, object? parameter, CultureInfo culture)
        => value is true ? "Running" : "Stopped";

    public object? ConvertBack(object? value, Type targetType, object? parameter, CultureInfo culture)
        => null;
}

public class BoolToRunningColorConverter : IValueConverter
{
    public object? Convert(object? value, Type targetType, object? parameter, CultureInfo culture)
        => value is true ? Color.FromArgb("#00e676") : Color.FromArgb("#ff1744");

    public object? ConvertBack(object? value, Type targetType, object? parameter, CultureInfo culture)
        => null;
}

public class PriorityToColorConverter : IValueConverter
{
    public object? Convert(object? value, Type targetType, object? parameter, CultureInfo culture)
    {
        if (value is not TaskPriority priority) return Colors.Grey;
        return priority switch
        {
            TaskPriority.P1 => Color.FromArgb("#ff1744"),
            TaskPriority.P2 => Color.FromArgb("#ff9100"),
            TaskPriority.P3 => Color.FromArgb("#00d4ff"),
            _ => Colors.Grey
        };
    }

    public object? ConvertBack(object? value, Type targetType, object? parameter, CultureInfo culture)
        => null;
}

public class StatusToColorConverter : IValueConverter
{
    public object? Convert(object? value, Type targetType, object? parameter, CultureInfo culture)
    {
        if (value is not BacklogTaskStatus status) return Colors.Grey;
        return status switch
        {
            BacklogTaskStatus.Completed => Color.FromArgb("#00e676"),
            BacklogTaskStatus.InProgress => Color.FromArgb("#00d4ff"),
            BacklogTaskStatus.Pending => Color.FromArgb("#6c757d"),
            BacklogTaskStatus.Blocked => Color.FromArgb("#ff1744"),
            _ => Colors.Grey
        };
    }

    public object? ConvertBack(object? value, Type targetType, object? parameter, CultureInfo culture)
        => null;
}

public class LogLevelToColorConverter : IValueConverter
{
    public object? Convert(object? value, Type targetType, object? parameter, CultureInfo culture)
    {
        if (value is not string level) return Colors.Grey;
        return level.ToUpperInvariant() switch
        {
            "ERROR" => Color.FromArgb("#ff1744"),
            "WARN" or "WARNING" => Color.FromArgb("#ff9100"),
            "INFO" => Color.FromArgb("#00d4ff"),
            "DEBUG" => Color.FromArgb("#6c757d"),
            _ => Color.FromArgb("#b0b0b0")
        };
    }

    public object? ConvertBack(object? value, Type targetType, object? parameter, CultureInfo culture)
        => null;
}

public class BoolToBlockedColorConverter : IValueConverter
{
    public object? Convert(object? value, Type targetType, object? parameter, CultureInfo culture)
        => value is true ? Color.FromArgb("#ff1744") : Color.FromArgb("#00e676");

    public object? ConvertBack(object? value, Type targetType, object? parameter, CultureInfo culture)
        => null;
}

public class BoolToBlockedTextConverter : IValueConverter
{
    public object? Convert(object? value, Type targetType, object? parameter, CultureInfo culture)
        => value is true ? "BLOCKED" : "ALLOWED";

    public object? ConvertBack(object? value, Type targetType, object? parameter, CultureInfo culture)
        => null;
}

public class InverseBoolConverter : IValueConverter
{
    public object? Convert(object? value, Type targetType, object? parameter, CultureInfo culture)
        => value is bool b ? !b : value;

    public object? ConvertBack(object? value, Type targetType, object? parameter, CultureInfo culture)
        => value is bool b ? !b : value;
}

public class DoubleToPercentConverter : IValueConverter
{
    public object? Convert(object? value, Type targetType, object? parameter, CultureInfo culture)
        => value is double d ? $"{d:P0}" : "0%";

    public object? ConvertBack(object? value, Type targetType, object? parameter, CultureInfo culture)
        => null;
}

public class SafetyRatingToColorConverter : IValueConverter
{
    public object? Convert(object? value, Type targetType, object? parameter, CultureInfo culture)
    {
        if (value is not SkillSafetyRating rating) return Colors.Grey;
        return rating switch
        {
            SkillSafetyRating.Verified => Color.FromArgb("#00e676"),
            SkillSafetyRating.Community => Color.FromArgb("#00d4ff"),
            SkillSafetyRating.Unreviewed => Color.FromArgb("#ff9100"),
            SkillSafetyRating.Flagged => Color.FromArgb("#ff1744"),
            _ => Colors.Grey
        };
    }

    public object? ConvertBack(object? value, Type targetType, object? parameter, CultureInfo culture)
        => null;
}

public class ChatRoleToColorConverter : IValueConverter
{
    public object? Convert(object? value, Type targetType, object? parameter, CultureInfo culture)
    {
        if (value is not ChatRole role) return Colors.Grey;
        return role switch
        {
            ChatRole.User => Color.FromArgb("#00d4ff"),
            ChatRole.Assistant => Color.FromArgb("#00e676"),
            ChatRole.Skill => Color.FromArgb("#d500f9"),
            ChatRole.System => Color.FromArgb("#6c757d"),
            _ => Colors.Grey
        };
    }

    public object? ConvertBack(object? value, Type targetType, object? parameter, CultureInfo culture)
        => null;
}

public class ChatRoleToAlignmentConverter : IValueConverter
{
    public object? Convert(object? value, Type targetType, object? parameter, CultureInfo culture)
        => value is ChatRole.User ? LayoutOptions.End : LayoutOptions.Start;

    public object? ConvertBack(object? value, Type targetType, object? parameter, CultureInfo culture)
        => null;
}

public class ChatRoleToBgColorConverter : IValueConverter
{
    public object? Convert(object? value, Type targetType, object? parameter, CultureInfo culture)
    {
        if (value is not ChatRole role) return Color.FromArgb("#1a1a3e");
        return role switch
        {
            ChatRole.User => Color.FromArgb("#0f3460"),
            ChatRole.Assistant => Color.FromArgb("#1a2e1a"),
            ChatRole.Skill => Color.FromArgb("#2a1a3e"),
            _ => Color.FromArgb("#1a1a3e")
        };
    }

    public object? ConvertBack(object? value, Type targetType, object? parameter, CultureInfo culture)
        => null;
}

public class ChatRoleToLabelConverter : IValueConverter
{
    public object? Convert(object? value, Type targetType, object? parameter, CultureInfo culture)
    {
        if (value is not ChatRole role) return "?";
        return role switch
        {
            ChatRole.User => "YOU",
            ChatRole.Assistant => "OPENCLAW",
            ChatRole.Skill => "SKILL",
            ChatRole.System => "SYSTEM",
            _ => "?"
        };
    }

    public object? ConvertBack(object? value, Type targetType, object? parameter, CultureInfo culture)
        => null;
}

public class BoolToConnectedTextConverter : IValueConverter
{
    public object? Convert(object? value, Type targetType, object? parameter, CultureInfo culture)
        => value is true ? "Connected" : "Disconnected";

    public object? ConvertBack(object? value, Type targetType, object? parameter, CultureInfo culture)
        => null;
}
