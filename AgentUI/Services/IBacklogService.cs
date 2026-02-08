using AgentUI.Models;

namespace AgentUI.Services;

public interface IBacklogService
{
    Task<List<BacklogTask>> GetTasksAsync();
    Task<List<BacklogTask>> GetTasksByStatusAsync(TaskStatus status);
    Task AddTaskAsync(BacklogTask task);
    Task UpdateTaskAsync(BacklogTask task);
    Task DeleteTaskAsync(string taskId);
}
