using AgentUI.Models;

namespace AgentUI.Tests.ViewModels;

/// <summary>
/// Unit tests for DashboardViewModel presentation logic.
///
/// DashboardViewModel uses MAUI's Color and MainThread types which require the
/// MAUI runtime. The tests here cover the pure .NET derivation logic that is
/// mirrored directly from UpdateFromStatus and UpdateFromOpenClawStatus. For
/// full integration coverage, run the MAUI test runner on a simulator/device.
/// </summary>
public class DashboardViewModelTests
{
    // -------------------------------------------------------------------------
    // Task progress calculation (mirrors UpdateFromStatus)
    // -------------------------------------------------------------------------

    private static double ComputeTaskProgress(int completed, int total) =>
        total > 0 ? (double)completed / total : 0;

    [Theory]
    [InlineData(0,  0,  0.0)]
    [InlineData(0,  5,  0.0)]
    [InlineData(3,  5,  0.6)]
    [InlineData(5,  5,  1.0)]
    [InlineData(10, 4,  2.5)] // over-complete edge case
    public void TaskProgress_CalculatesCorrectly(int completed, int total, double expected)
    {
        var result = ComputeTaskProgress(completed, total);
        Assert.Equal(expected, result, precision: 10);
    }

    // -------------------------------------------------------------------------
    // Budget usage calculation (mirrors UpdateFromStatus)
    // -------------------------------------------------------------------------

    private static double ComputeBudgetUsage(double costToday, double dailyBudget) =>
        dailyBudget > 0 ? costToday / dailyBudget : 0;

    [Theory]
    [InlineData(0.0,  5.0,  0.0)]
    [InlineData(2.5,  5.0,  0.5)]
    [InlineData(5.0,  5.0,  1.0)]
    [InlineData(6.0,  5.0,  1.2)] // over-budget
    [InlineData(1.0,  0.0,  0.0)] // zero budget guard
    public void BudgetUsage_CalculatesCorrectly(double cost, double budget, double expected)
    {
        var result = ComputeBudgetUsage(cost, budget);
        Assert.Equal(expected, result, precision: 10);
    }

    // -------------------------------------------------------------------------
    // Current task display (mirrors UpdateFromStatus null-guard)
    // -------------------------------------------------------------------------

    private static string FormatCurrentTask(string? raw) =>
        string.IsNullOrEmpty(raw) ? "No active task" : raw;

    [Theory]
    [InlineData(null,            "No active task")]
    [InlineData("",              "No active task")]
    [InlineData("Fix auth bug",  "Fix auth bug")]
    public void CurrentTask_DisplayText_IsCorrect(string? raw, string expected)
    {
        Assert.Equal(expected, FormatCurrentTask(raw));
    }

    // -------------------------------------------------------------------------
    // Uptime formatting (mirrors UpdateFromStatus)
    // -------------------------------------------------------------------------

    private static string FormatUptime(TimeSpan uptime) =>
        $"{(int)uptime.TotalHours}h {uptime.Minutes}m";

    [Theory]
    [InlineData(0,  0,  "0h 0m")]
    [InlineData(1,  30, "1h 30m")]
    [InlineData(25, 15, "25h 15m")]
    public void Uptime_FormatString_IsCorrect(int hours, int minutes, string expected)
    {
        var uptime = TimeSpan.FromHours(hours) + TimeSpan.FromMinutes(minutes);
        Assert.Equal(expected, FormatUptime(uptime));
    }

    // -------------------------------------------------------------------------
    // Files display (mirrors UpdateFromStatus)
    // -------------------------------------------------------------------------

    private static string FormatFilesText(int created, int max) => $"{created} / {max}";

    [Theory]
    [InlineData(0,   100, "0 / 100")]
    [InlineData(42,  100, "42 / 100")]
    [InlineData(100, 100, "100 / 100")]
    public void FilesText_FormatString_IsCorrect(int created, int max, string expected)
    {
        Assert.Equal(expected, FormatFilesText(created, max));
    }

    // -------------------------------------------------------------------------
    // OpenClaw: connection state — model field (no MAUI Color needed)
    // -------------------------------------------------------------------------

    [Fact]
    public void OpenClawStatus_Connected_IsDetectedCorrectly()
    {
        var status = new OpenClawStatus
        {
            ConnectionState = OpenClawConnectionState.Connected,
            SelectedModel = "llama3.1:8b",
        };
        Assert.True(status.ConnectionState == OpenClawConnectionState.Connected);
        Assert.Equal("llama3.1:8b", status.SelectedModel);
    }

    [Fact]
    public void OpenClawStatus_Disconnected_HasNoUptime()
    {
        var status = new OpenClawStatus { ConnectionState = OpenClawConnectionState.Disconnected };
        Assert.Null(status.Uptime);
    }

    [Fact]
    public void OpenClawStatus_Connected_HasPositiveUptime()
    {
        var status = new OpenClawStatus
        {
            ConnectionState = OpenClawConnectionState.Connected,
            ConnectedSince = DateTime.Now.AddMinutes(-30),
        };
        Assert.NotNull(status.Uptime);
        Assert.True(status.Uptime!.Value.TotalSeconds > 0);
    }

    // -------------------------------------------------------------------------
    // AgentStatus model
    // -------------------------------------------------------------------------

    [Fact]
    public void AgentStatus_UptimeProperty_IsComputedFromSessionStart()
    {
        var start = DateTime.Now.AddHours(-2);
        var status = new AgentStatus { SessionStart = start };
        Assert.True(status.Uptime.TotalHours >= 2.0);
    }

    [Fact]
    public void AgentStatus_DefaultBudget_Is5Dollars()
    {
        var status = new AgentStatus();
        Assert.Equal(5.00, status.DailyBudget);
    }
}
