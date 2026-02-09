using AgentUI.Models;

namespace AgentUI.Services;

/// <summary>
/// Reads and manages the BACKLOG.md file used by the agent.
/// </summary>
public class BacklogService : IBacklogService
{
    private readonly List<BacklogTask> _tasks;

    public BacklogService()
    {
        _tasks = SeedFromBacklog();
    }

    private static List<BacklogTask> SeedFromBacklog()
    {
        return new List<BacklogTask>
        {
            // In Progress
            new() { Title = "CloudKit sync for save games", Priority = TaskPriority.P1, Status = BacklogTaskStatus.InProgress, Category = "Cloud" },
            new() { Title = "Leaderboard UI with SwiftUI", Priority = TaskPriority.P1, Status = BacklogTaskStatus.InProgress, Category = "UI" },

            // Pending High Priority
            new() { Title = "iCloud save game persistence", Priority = TaskPriority.P1, Status = BacklogTaskStatus.Pending, Category = "Cloud" },
            new() { Title = "Game Center leaderboard submission", Priority = TaskPriority.P1, Status = BacklogTaskStatus.Pending, Category = "GameKit" },
            new() { Title = "Achievement system integration", Priority = TaskPriority.P1, Status = BacklogTaskStatus.Pending, Category = "GameKit" },

            // Pending Medium Priority
            new() { Title = "Additional mini-games (Puzzle, Runner)", Priority = TaskPriority.P2, Status = BacklogTaskStatus.Pending, Category = "Gameplay" },
            new() { Title = "Particle effects system", Priority = TaskPriority.P2, Status = BacklogTaskStatus.Pending, Category = "Graphics" },
            new() { Title = "Spatial audio support", Priority = TaskPriority.P2, Status = BacklogTaskStatus.Pending, Category = "Audio" },
            new() { Title = "Advanced haptic patterns", Priority = TaskPriority.P2, Status = BacklogTaskStatus.Pending, Category = "Haptics" },
            new() { Title = "Menu transition animations", Priority = TaskPriority.P2, Status = BacklogTaskStatus.Pending, Category = "UI" },

            // Pending Low Priority
            new() { Title = "watchOS companion app", Priority = TaskPriority.P3, Status = BacklogTaskStatus.Pending, Category = "Platform" },
            new() { Title = "tvOS remote input support", Priority = TaskPriority.P3, Status = BacklogTaskStatus.Pending, Category = "Platform" },
            new() { Title = "Accessibility VoiceOver support", Priority = TaskPriority.P3, Status = BacklogTaskStatus.Pending, Category = "Accessibility" },
            new() { Title = "Analytics event tracking", Priority = TaskPriority.P3, Status = BacklogTaskStatus.Pending, Category = "Analytics" },
            new() { Title = "Screen recording prevention", Priority = TaskPriority.P3, Status = BacklogTaskStatus.Pending, Category = "Security" },

            // Completed
            new() { Title = "Game Center authentication", Priority = TaskPriority.P1, Status = BacklogTaskStatus.Completed, Category = "GameKit", CompletedAt = DateTime.Now.AddDays(-5) },
            new() { Title = "Core navigation system", Priority = TaskPriority.P1, Status = BacklogTaskStatus.Completed, Category = "UI", CompletedAt = DateTime.Now.AddDays(-4) },
            new() { Title = "Game loop with fixed timestep", Priority = TaskPriority.P1, Status = BacklogTaskStatus.Completed, Category = "Engine", CompletedAt = DateTime.Now.AddDays(-4) },
            new() { Title = "Base game scene (SpriteKit)", Priority = TaskPriority.P1, Status = BacklogTaskStatus.Completed, Category = "Engine", CompletedAt = DateTime.Now.AddDays(-3) },
            new() { Title = "Sound manager with AVFoundation", Priority = TaskPriority.P1, Status = BacklogTaskStatus.Completed, Category = "Audio", CompletedAt = DateTime.Now.AddDays(-2) },
            new() { Title = "Haptic feedback engine", Priority = TaskPriority.P2, Status = BacklogTaskStatus.Completed, Category = "Haptics", CompletedAt = DateTime.Now.AddDays(-2) },
            new() { Title = "SpaceShooter sample app", Priority = TaskPriority.P1, Status = BacklogTaskStatus.Completed, Category = "App", CompletedAt = DateTime.Now.AddDays(-1) },
        };
    }

    public Task<List<BacklogTask>> GetTasksAsync() => Task.FromResult(_tasks.ToList());

    public Task<List<BacklogTask>> GetTasksByStatusAsync(BacklogTaskStatus status)
        => Task.FromResult(_tasks.Where(t => t.Status == status).ToList());

    public Task AddTaskAsync(BacklogTask task)
    {
        _tasks.Add(task);
        return Task.CompletedTask;
    }

    public Task UpdateTaskAsync(BacklogTask task)
    {
        var idx = _tasks.FindIndex(t => t.Id == task.Id);
        if (idx >= 0) _tasks[idx] = task;
        return Task.CompletedTask;
    }

    public Task DeleteTaskAsync(string taskId)
    {
        _tasks.RemoveAll(t => t.Id == taskId);
        return Task.CompletedTask;
    }
}
