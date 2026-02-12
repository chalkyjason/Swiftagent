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
    [ObservableProperty] private int _blockedCount;

    // Task creation form
    [ObservableProperty] private string _newTaskTitle = string.Empty;
    [ObservableProperty] private string _newTaskDescription = string.Empty;
    [ObservableProperty] private string _newTaskPriority = "P2";
    [ObservableProperty] private string _newTaskCategory = "General";
    [ObservableProperty] private string _newTaskAgent = "any";
    [ObservableProperty] private bool _isFormVisible;
    [ObservableProperty] private string _statusMessage = string.Empty;

    public ObservableCollection<BacklogTask> Tasks { get; } = new();
    public ObservableCollection<BacklogTask> FilteredTasks { get; } = new();

    public List<string> Priorities { get; } = new() { "P1", "P2", "P3" };
    public List<string> Categories { get; } = new()
    {
        "General", "Backend", "Frontend", "DevOps", "Testing", "Docs", "Bug Fix", "Refactor", "Research"
    };
    public List<string> Agents { get; } = new() { "any", "openclaw", "claude", "goose" };

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
        BlockedCount = tasks.Count(t => t.Status == BacklogTaskStatus.Blocked);

        ApplyFilter();
    }

    [RelayCommand]
    private void Filter(string filter)
    {
        SelectedFilter = filter;
        ApplyFilter();
    }

    [RelayCommand]
    private void ToggleForm()
    {
        IsFormVisible = !IsFormVisible;
        if (!IsFormVisible) ClearForm();
    }

    [RelayCommand]
    private async Task CreateTaskAsync()
    {
        if (string.IsNullOrWhiteSpace(NewTaskTitle))
        {
            StatusMessage = "Title is required";
            return;
        }

        var priority = NewTaskPriority switch
        {
            "P1" => TaskPriority.P1,
            "P3" => TaskPriority.P3,
            _ => TaskPriority.P2
        };

        var task = new BacklogTask
        {
            Title = NewTaskTitle.Trim(),
            Description = NewTaskDescription.Trim(),
            Priority = priority,
            Category = NewTaskCategory,
            AssignedAgent = NewTaskAgent,
            Status = BacklogTaskStatus.Pending,
        };

        await _backlogService.AddTaskAsync(task);
        ClearForm();
        IsFormVisible = false;
        StatusMessage = $"Task '{task.Title}' created";
        await LoadTasksAsync();

        // Clear status message after 3 seconds
        _ = Task.Delay(3000).ContinueWith(_ =>
            MainThread.BeginInvokeOnMainThread(() => StatusMessage = string.Empty));
    }

    [RelayCommand]
    private async Task DeleteTaskAsync(BacklogTask task)
    {
        if (task == null) return;
        await _backlogService.DeleteTaskAsync(task.Id);
        await LoadTasksAsync();
    }

    private void ClearForm()
    {
        NewTaskTitle = string.Empty;
        NewTaskDescription = string.Empty;
        NewTaskPriority = "P2";
        NewTaskCategory = "General";
        NewTaskAgent = "any";
    }

    private void ApplyFilter()
    {
        FilteredTasks.Clear();
        var filtered = SelectedFilter switch
        {
            "In Progress" => Tasks.Where(t => t.Status == BacklogTaskStatus.InProgress),
            "Pending" => Tasks.Where(t => t.Status == BacklogTaskStatus.Pending),
            "Completed" => Tasks.Where(t => t.Status == BacklogTaskStatus.Completed),
            "Blocked" => Tasks.Where(t => t.Status == BacklogTaskStatus.Blocked),
            "P1" => Tasks.Where(t => t.Priority == TaskPriority.P1),
            "P2" => Tasks.Where(t => t.Priority == TaskPriority.P2),
            "P3" => Tasks.Where(t => t.Priority == TaskPriority.P3),
            _ => Tasks.AsEnumerable()
        };

        foreach (var task in filtered.OrderBy(t => t.Status).ThenBy(t => t.Priority))
            FilteredTasks.Add(task);
    }
}
