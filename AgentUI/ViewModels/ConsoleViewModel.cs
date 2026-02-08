using System.Collections.ObjectModel;
using AgentUI.Models;
using AgentUI.Services;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;

namespace AgentUI.ViewModels;

public partial class ConsoleViewModel : ObservableObject
{
    private readonly IAgentService _agentService;

    [ObservableProperty] private string _selectedLevel = "All";
    [ObservableProperty] private bool _autoScroll = true;
    [ObservableProperty] private int _totalEntries;
    [ObservableProperty] private int _errorCount;
    [ObservableProperty] private int _warnCount;

    public ObservableCollection<LogEntry> Logs { get; } = new();
    public ObservableCollection<LogEntry> FilteredLogs { get; } = new();

    public ConsoleViewModel(IAgentService agentService)
    {
        _agentService = agentService;
        _agentService.LogReceived += OnLogReceived;
        _ = LoadLogsAsync();
    }

    private void OnLogReceived(object? sender, LogEntry entry)
    {
        MainThread.BeginInvokeOnMainThread(() =>
        {
            Logs.Add(entry);
            if (MatchesFilter(entry))
                FilteredLogs.Add(entry);

            UpdateCounts();
        });
    }

    [RelayCommand]
    private async Task LoadLogsAsync()
    {
        var logs = await _agentService.GetLogsAsync(200);
        Logs.Clear();
        foreach (var log in logs)
            Logs.Add(log);

        UpdateCounts();
        ApplyFilter();
    }

    [RelayCommand]
    private void FilterByLevel(string level)
    {
        SelectedLevel = level;
        ApplyFilter();
    }

    [RelayCommand]
    private void ClearLogs()
    {
        Logs.Clear();
        FilteredLogs.Clear();
        UpdateCounts();
    }

    private void ApplyFilter()
    {
        FilteredLogs.Clear();
        foreach (var log in Logs.Where(MatchesFilter))
            FilteredLogs.Add(log);
    }

    private bool MatchesFilter(LogEntry entry) =>
        SelectedLevel == "All" || entry.Level.Equals(SelectedLevel, StringComparison.OrdinalIgnoreCase);

    private void UpdateCounts()
    {
        TotalEntries = Logs.Count;
        ErrorCount = Logs.Count(l => l.Level == "ERROR");
        WarnCount = Logs.Count(l => l.Level is "WARN" or "WARNING");
    }
}
