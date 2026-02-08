using System.Collections.ObjectModel;
using AgentUI.Models;
using AgentUI.Services;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;

namespace AgentUI.ViewModels;

public partial class DashboardViewModel : ObservableObject
{
    private readonly IAgentService _agentService;
    private readonly IOpenClawService _openClawService;

    [ObservableProperty] private bool _isRunning;
    [ObservableProperty] private string _currentPhase = "Idle";
    [ObservableProperty] private Color _phaseColor = Colors.Grey;
    [ObservableProperty] private string _currentTask = "No active task";
    [ObservableProperty] private int _completedTasks;
    [ObservableProperty] private int _totalTasks;
    [ObservableProperty] private double _taskProgress;
    [ObservableProperty] private string _costToday = "$0.00";
    [ObservableProperty] private double _budgetUsage;
    [ObservableProperty] private string _budgetText = "$0.00 / $5.00";
    [ObservableProperty] private string _uptime = "0h 0m";
    [ObservableProperty] private int _filesCreated;
    [ObservableProperty] private string _filesText = "0 / 100";

    [ObservableProperty] private bool _isObserveActive;
    [ObservableProperty] private bool _isOrientActive;
    [ObservableProperty] private bool _isDecideActive;
    [ObservableProperty] private bool _isActActive;
    [ObservableProperty] private bool _isVerifyActive;
    [ObservableProperty] private bool _isCommitActive;

    // OpenClaw status
    [ObservableProperty] private bool _isOpenClawConnected;
    [ObservableProperty] private Color _openClawConnectionColor = Colors.Grey;
    [ObservableProperty] private string _openClawModel = "--";
    [ObservableProperty] private string _openClawSkills = "0/0";
    [ObservableProperty] private string _openClawTokens = "0";
    [ObservableProperty] private string _openClawVersion = "--";

    public ObservableCollection<string> RecentActions { get; } = new();

    public DashboardViewModel(IAgentService agentService, IOpenClawService openClawService)
    {
        _agentService = agentService;
        _openClawService = openClawService;
        _agentService.StatusChanged += OnStatusChanged;
        _openClawService.StatusChanged += OnOpenClawStatusChanged;
        _ = RefreshAsync();
    }

    private void OnStatusChanged(object? sender, AgentStatus status) =>
        MainThread.BeginInvokeOnMainThread(() => UpdateFromStatus(status));

    private void OnOpenClawStatusChanged(object? sender, OpenClawStatus status) =>
        MainThread.BeginInvokeOnMainThread(() => UpdateFromOpenClawStatus(status));

    [RelayCommand]
    private async Task RefreshAsync()
    {
        var status = await _agentService.GetStatusAsync();
        UpdateFromStatus(status);

        var clawStatus = await _openClawService.GetStatusAsync();
        UpdateFromOpenClawStatus(clawStatus);
    }

    [RelayCommand]
    private async Task ToggleAgentAsync()
    {
        if (IsRunning)
            await _agentService.StopAgentAsync();
        else
            await _agentService.StartAgentAsync();

        await RefreshAsync();
    }

    private void UpdateFromStatus(AgentStatus status)
    {
        IsRunning = status.IsRunning;
        CurrentPhase = status.CurrentPhase.ToString().ToUpperInvariant();
        CurrentTask = string.IsNullOrEmpty(status.CurrentTask) ? "No active task" : status.CurrentTask;
        CompletedTasks = status.CompletedTasks;
        TotalTasks = status.TotalTasks;
        TaskProgress = status.TotalTasks > 0 ? (double)status.CompletedTasks / status.TotalTasks : 0;
        CostToday = $"${status.CostToday:F2}";
        BudgetUsage = status.DailyBudget > 0 ? status.CostToday / status.DailyBudget : 0;
        BudgetText = $"${status.CostToday:F2} / ${status.DailyBudget:F2}";
        Uptime = $"{status.Uptime.Hours}h {status.Uptime.Minutes}m";
        FilesCreated = status.FilesCreatedThisSession;
        FilesText = $"{status.FilesCreatedThisSession} / {status.MaxFilesPerSession}";

        PhaseColor = status.CurrentPhase switch
        {
            AgentPhase.Observe => Color.FromArgb("#00d4ff"),
            AgentPhase.Orient => Color.FromArgb("#d500f9"),
            AgentPhase.Decide => Color.FromArgb("#ffea00"),
            AgentPhase.Act => Color.FromArgb("#00e676"),
            AgentPhase.Verify => Color.FromArgb("#ff9100"),
            AgentPhase.Commit => Color.FromArgb("#00e676"),
            _ => Color.FromArgb("#6c757d")
        };

        IsObserveActive = status.CurrentPhase == AgentPhase.Observe;
        IsOrientActive = status.CurrentPhase == AgentPhase.Orient;
        IsDecideActive = status.CurrentPhase == AgentPhase.Decide;
        IsActActive = status.CurrentPhase == AgentPhase.Act;
        IsVerifyActive = status.CurrentPhase == AgentPhase.Verify;
        IsCommitActive = status.CurrentPhase == AgentPhase.Commit;

        RecentActions.Clear();
        foreach (var action in status.RecentActions)
            RecentActions.Add(action);
    }

    private void UpdateFromOpenClawStatus(OpenClawStatus status)
    {
        IsOpenClawConnected = status.ConnectionState == OpenClawConnectionState.Connected;
        OpenClawConnectionColor = status.ConnectionState switch
        {
            OpenClawConnectionState.Connected => Color.FromArgb("#00e676"),
            OpenClawConnectionState.Connecting => Color.FromArgb("#ffea00"),
            OpenClawConnectionState.Error => Color.FromArgb("#ff1744"),
            _ => Color.FromArgb("#6c757d")
        };
        OpenClawModel = status.SelectedModel;
        OpenClawSkills = $"{status.ActiveSkillsCount}/{status.TotalSkillsCount}";
        OpenClawTokens = $"{status.TokensUsedToday:N0}";
        OpenClawVersion = status.Version;
    }
}
