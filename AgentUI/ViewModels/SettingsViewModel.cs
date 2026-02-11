using AgentUI.Models;
using AgentUI.Services;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;

namespace AgentUI.ViewModels;

public partial class SettingsViewModel : ObservableObject
{
    private readonly IAgentService _agentService;

    [ObservableProperty] private string _workspaceRoot = string.Empty;
    [ObservableProperty] private double _dailyBudget = 5.00;
    [ObservableProperty] private string _logLevel = "INFO";
    [ObservableProperty] private int _maxFilesPerSession = 100;
    [ObservableProperty] private string _maxFileSize = "1 MB";
    [ObservableProperty] private bool _safeDeleteEnabled = true;
    [ObservableProperty] private bool _sandboxEnabled = true;
    [ObservableProperty] private int _maxContextTokens = 100_000;
    [ObservableProperty] private bool _claudeCliEnabled;
    [ObservableProperty] private bool _gooseEnabled;
    [ObservableProperty] private bool _hasUnsavedChanges;
    [ObservableProperty] private string _statusMessage = string.Empty;

    public List<string> LogLevels { get; } = new() { "DEBUG", "INFO", "WARN", "ERROR" };

    public SettingsViewModel(IAgentService agentService)
    {
        _agentService = agentService;
        LoadConfig();
    }

    private void LoadConfig()
    {
        var config = _agentService.Config;
        WorkspaceRoot = config.WorkspaceRoot;
        DailyBudget = config.DailyBudget;
        LogLevel = config.LogLevel;
        MaxFilesPerSession = config.MaxFilesPerSession;
        MaxFileSize = FormatBytes(config.MaxFileSizeBytes);
        SafeDeleteEnabled = config.SafeDeleteEnabled;
        SandboxEnabled = config.SandboxEnabled;
        MaxContextTokens = config.MaxContextTokens;
        ClaudeCliEnabled = config.ClaudeCliEnabled;
        GooseEnabled = config.GooseEnabled;
        HasUnsavedChanges = false;
    }

    partial void OnDailyBudgetChanged(double value) => HasUnsavedChanges = true;
    partial void OnLogLevelChanged(string value) => HasUnsavedChanges = true;
    partial void OnMaxFilesPerSessionChanged(int value) => HasUnsavedChanges = true;
    partial void OnSafeDeleteEnabledChanged(bool value) => HasUnsavedChanges = true;
    partial void OnSandboxEnabledChanged(bool value) => HasUnsavedChanges = true;
    partial void OnMaxContextTokensChanged(int value) => HasUnsavedChanges = true;
    partial void OnClaudeCliEnabledChanged(bool value) => HasUnsavedChanges = true;
    partial void OnGooseEnabledChanged(bool value) => HasUnsavedChanges = true;

    [RelayCommand]
    private async Task SaveAsync()
    {
        var config = new AgentConfig
        {
            WorkspaceRoot = WorkspaceRoot,
            DailyBudget = DailyBudget,
            LogLevel = LogLevel,
            MaxFilesPerSession = MaxFilesPerSession,
            MaxFileSizeBytes = 1_048_576,
            SafeDeleteEnabled = SafeDeleteEnabled,
            SandboxEnabled = SandboxEnabled,
            MaxContextTokens = MaxContextTokens,
            ClaudeCliEnabled = ClaudeCliEnabled,
            GooseEnabled = GooseEnabled,
        };

        await _agentService.UpdateConfigAsync(config);
        HasUnsavedChanges = false;
        StatusMessage = "Settings saved successfully";

        await Task.Delay(2000);
        StatusMessage = string.Empty;
    }

    [RelayCommand]
    private void Reset()
    {
        LoadConfig();
        StatusMessage = "Settings reset to current values";
    }

    private static string FormatBytes(long bytes) => bytes switch
    {
        >= 1_048_576 => $"{bytes / 1_048_576.0:F0} MB",
        >= 1024 => $"{bytes / 1024.0:F0} KB",
        _ => $"{bytes} B"
    };
}
