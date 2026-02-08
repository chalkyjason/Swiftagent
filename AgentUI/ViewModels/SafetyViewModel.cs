using System.Collections.ObjectModel;
using AgentUI.Models;
using AgentUI.Services;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;

namespace AgentUI.ViewModels;

public partial class SafetyViewModel : ObservableObject
{
    private readonly IAgentService _agentService;

    [ObservableProperty] private double _costToday;
    [ObservableProperty] private double _dailyBudget = 5.00;
    [ObservableProperty] private double _budgetUsagePercent;
    [ObservableProperty] private string _budgetText = "$0.00 / $5.00";
    [ObservableProperty] private int _totalTokensUsed;
    [ObservableProperty] private int _blockedEvents;
    [ObservableProperty] private int _allowedEvents;
    [ObservableProperty] private string _costTrend = "stable";

    public ObservableCollection<SafetyEvent> SafetyEvents { get; } = new();
    public ObservableCollection<CostEntry> CostEntries { get; } = new();

    public SafetyViewModel(IAgentService agentService)
    {
        _agentService = agentService;
        _agentService.SafetyEventOccurred += OnSafetyEvent;
        LoadData();
    }

    private void OnSafetyEvent(object? sender, SafetyEvent e)
    {
        MainThread.BeginInvokeOnMainThread(() =>
        {
            SafetyEvents.Insert(0, e);
            UpdateCounts();
        });
    }

    [RelayCommand]
    private void Refresh() => LoadData();

    private void LoadData()
    {
        SafetyEvents.Clear();
        foreach (var ev in _agentService.SafetyEvents.OrderByDescending(e => e.Timestamp))
            SafetyEvents.Add(ev);

        CostEntries.Clear();
        foreach (var entry in _agentService.CostHistory.OrderByDescending(e => e.Timestamp))
            CostEntries.Add(entry);

        var status = _agentService.Status;
        CostToday = status.CostToday;
        DailyBudget = status.DailyBudget;
        BudgetUsagePercent = DailyBudget > 0 ? CostToday / DailyBudget : 0;
        BudgetText = $"${CostToday:F2} / ${DailyBudget:F2}";
        TotalTokensUsed = _agentService.CostHistory.Sum(c => c.TokensUsed);

        UpdateCounts();
    }

    private void UpdateCounts()
    {
        BlockedEvents = SafetyEvents.Count(e => e.WasBlocked);
        AllowedEvents = SafetyEvents.Count(e => !e.WasBlocked);
    }
}
