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
        => throw new NotImplementedException();
}

public class BoolToRunningTextConverter : IValueConverter
{
    public object? Convert(object? value, Type targetType, object? parameter, CultureInfo culture)
        => value is true ? "Running" : "Stopped";

    public object? ConvertBack(object? value, Type targetType, object? parameter, CultureInfo culture)
        => throw new NotImplementedException();
}

public class BoolToRunningColorConverter : IValueConverter
{
    public object? Convert(object? value, Type targetType, object? parameter, CultureInfo culture)
        => value is true ? Color.FromArgb("#00e676") : Color.FromArgb("#ff1744");

    public object? ConvertBack(object? value, Type targetType, object? parameter, CultureInfo culture)
        => throw new NotImplementedException();
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
        => throw new NotImplementedException();
}

public class StatusToColorConverter : IValueConverter
{
    public object? Convert(object? value, Type targetType, object? parameter, CultureInfo culture)
    {
        if (value is not TaskStatus status) return Colors.Grey;
        return status switch
        {
            TaskStatus.Completed => Color.FromArgb("#00e676"),
            TaskStatus.InProgress => Color.FromArgb("#00d4ff"),
            TaskStatus.Pending => Color.FromArgb("#6c757d"),
            TaskStatus.Blocked => Color.FromArgb("#ff1744"),
            _ => Colors.Grey
        };
    }

    public object? ConvertBack(object? value, Type targetType, object? parameter, CultureInfo culture)
        => throw new NotImplementedException();
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
        => throw new NotImplementedException();
}

public class BoolToBlockedColorConverter : IValueConverter
{
    public object? Convert(object? value, Type targetType, object? parameter, CultureInfo culture)
        => value is true ? Color.FromArgb("#ff1744") : Color.FromArgb("#00e676");

    public object? ConvertBack(object? value, Type targetType, object? parameter, CultureInfo culture)
        => throw new NotImplementedException();
}

public class BoolToBlockedTextConverter : IValueConverter
{
    public object? Convert(object? value, Type targetType, object? parameter, CultureInfo culture)
        => value is true ? "BLOCKED" : "ALLOWED";

    public object? ConvertBack(object? value, Type targetType, object? parameter, CultureInfo culture)
        => throw new NotImplementedException();
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
        => throw new NotImplementedException();
}
