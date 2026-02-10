using AgentUI.Models;

namespace AgentUI.Services;

public interface IBacklogService
{
    Task<List<BacklogTask>> GetTasksAsync();
    Task<List<BacklogTask>> GetTasksByStatusAsync(BacklogTaskStatus status);
    Task AddTaskAsync(BacklogTask task);
    Task UpdateTaskAsync(BacklogTask task);
    Task DeleteTaskAsync(string taskId);
}
