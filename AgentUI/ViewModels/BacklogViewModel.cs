using System.Collections.ObjectModel;
using AgentUI.Models;
using AgentUI.Services;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;

namespace AgentUI.ViewModels;

public partial class BacklogViewModel : ObservableObject
{
    private readonly IBacklogService _backlogService;

    [ObservableProperty] private string _selectedFilter = "All";
    [ObservableProperty] private int _totalCount;
    [ObservableProperty] private int _completedCount;
    [ObservableProperty] private int _inProgressCount;
    [ObservableProperty] private int _pendingCount;

    public ObservableCollection<BacklogTask> Tasks { get; } = new();
    public ObservableCollection<BacklogTask> FilteredTasks { get; } = new();

    public BacklogViewModel(IBacklogService backlogService)
    {
        _backlogService = backlogService;
        _ = LoadTasksAsync();
    }

    [RelayCommand]
    private async Task LoadTasksAsync()
    {
        var tasks = await _backlogService.GetTasksAsync();
        Tasks.Clear();
        foreach (var task in tasks)
            Tasks.Add(task);

        TotalCount = tasks.Count;
        CompletedCount = tasks.Count(t => t.Status == BacklogTaskStatus.Completed);
        InProgressCount = tasks.Count(t => t.Status == BacklogTaskStatus.InProgress);
        PendingCount = tasks.Count(t => t.Status == BacklogTaskStatus.Pending);

        ApplyFilter();
    }

    [RelayCommand]
    private void Filter(string filter)
    {
        SelectedFilter = filter;
        ApplyFilter();
    }

    private void ApplyFilter()
    {
        FilteredTasks.Clear();
        var filtered = SelectedFilter switch
        {
            "In Progress" => Tasks.Where(t => t.Status == BacklogTaskStatus.InProgress),
            "Pending" => Tasks.Where(t => t.Status == BacklogTaskStatus.Pending),
            "Completed" => Tasks.Where(t => t.Status == BacklogTaskStatus.Completed),
            "P1" => Tasks.Where(t => t.Priority == TaskPriority.P1),
            "P2" => Tasks.Where(t => t.Priority == TaskPriority.P2),
            "P3" => Tasks.Where(t => t.Priority == TaskPriority.P3),
            _ => Tasks.AsEnumerable()
        };

        foreach (var task in filtered.OrderBy(t => t.Status).ThenBy(t => t.Priority))
            FilteredTasks.Add(task);
    }
}
