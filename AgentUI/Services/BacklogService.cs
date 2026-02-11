using System.Text.Json;
using System.Text.RegularExpressions;
using AgentUI.Models;

namespace AgentUI.Services;

/// <summary>
/// Reads and manages the real BACKLOG.md file from the workspace.
/// Supports creating, updating, and deleting tasks with write-through to disk.
/// </summary>
public class BacklogService : IBacklogService
{
    private readonly string _backlogPath;
    private readonly string _tasksDir;
    private List<BacklogTask> _tasks = new();
    private DateTime _lastRead = DateTime.MinValue;

    public BacklogService()
    {
        var workspaceRoot = Environment.GetEnvironmentVariable("AGENT_WORKSPACE_ROOT")
            ?? Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.UserProfile), "Swiftagent");
        _backlogPath = Path.Combine(workspaceRoot, "BACKLOG.md");
        _tasksDir = Path.Combine(workspaceRoot, ".openclaw_tasks");

        Directory.CreateDirectory(_tasksDir);
        ParseBacklogFile();
    }

    private void ParseBacklogFile()
    {
        if (!File.Exists(_backlogPath)) return;

        try
        {
            var lastWrite = File.GetLastWriteTimeUtc(_backlogPath);
            if (lastWrite <= _lastRead) return;

            _lastRead = lastWrite;
            var lines = File.ReadAllLines(_backlogPath);
            var tasks = new List<BacklogTask>();
            string currentSection = "";

            foreach (var rawLine in lines)
            {
                var line = rawLine.Trim();

                if (line.StartsWith("##"))
                {
                    var header = line.TrimStart('#').Trim().ToLowerInvariant();
                    if (header.Contains("in progress")) currentSection = "in_progress";
                    else if (header.Contains("completed") || header.Contains("done")) currentSection = "completed";
                    else if (header.Contains("pending") || header.Contains("backlog")) currentSection = "pending";
                    else if (header.Contains("blocked") || header.Contains("failed")) currentSection = "blocked";
                    continue;
                }

                if (!line.StartsWith("- [")) continue;

                bool isCompleted = line.StartsWith("- [x]", StringComparison.OrdinalIgnoreCase);
                var taskText = Regex.Replace(line, @"^-\s*\[[ xX]\]\s*", "").Trim();

                var priority = TaskPriority.P2;
                var priorityMatch = Regex.Match(taskText, @"\[P([123])\]");
                if (priorityMatch.Success)
                {
                    priority = priorityMatch.Groups[1].Value switch
                    {
                        "1" => TaskPriority.P1,
                        "3" => TaskPriority.P3,
                        _ => TaskPriority.P2
                    };
                    taskText = taskText.Replace(priorityMatch.Value, "").Trim();
                }

                // Extract agent tag
                var agentMatch = Regex.Match(taskText, @"@agent:(\w+)");
                var assignedAgent = agentMatch.Success ? agentMatch.Groups[1].Value : "";
                if (agentMatch.Success)
                    taskText = taskText.Replace(agentMatch.Value, "").Trim();

                // Extract category tag
                var catMatch = Regex.Match(taskText, @"\[([^\]]+)\]");
                var category = catMatch.Success ? catMatch.Groups[1].Value : InferCategory(taskText);
                if (catMatch.Success)
                    taskText = taskText.Replace(catMatch.Value, "").Trim();

                var status = isCompleted ? BacklogTaskStatus.Completed
                    : currentSection == "in_progress" ? BacklogTaskStatus.InProgress
                    : currentSection == "completed" ? BacklogTaskStatus.Completed
                    : currentSection == "blocked" ? BacklogTaskStatus.Blocked
                    : BacklogTaskStatus.Pending;

                tasks.Add(new BacklogTask
                {
                    Title = taskText,
                    Priority = priority,
                    Status = status,
                    Category = category,
                    AssignedAgent = assignedAgent,
                    CompletedAt = isCompleted ? DateTime.Now.AddDays(-1) : null,
                });
            }

            _tasks = tasks;
        }
        catch
        {
            // File may be locked or malformed — keep existing tasks
        }
    }

    private static string InferCategory(string text)
    {
        var lower = text.ToLowerInvariant();
        if (lower.Contains("api") || lower.Contains("backend") || lower.Contains("server")) return "Backend";
        if (lower.Contains("ui") || lower.Contains("frontend") || lower.Contains("page")) return "Frontend";
        if (lower.Contains("test")) return "Testing";
        if (lower.Contains("doc")) return "Docs";
        if (lower.Contains("deploy") || lower.Contains("ci") || lower.Contains("docker")) return "DevOps";
        if (lower.Contains("bug") || lower.Contains("fix")) return "Bug Fix";
        if (lower.Contains("refactor")) return "Refactor";
        return "General";
    }

    public Task<List<BacklogTask>> GetTasksAsync()
    {
        ParseBacklogFile();
        return Task.FromResult(_tasks.ToList());
    }

    public Task<List<BacklogTask>> GetTasksByStatusAsync(BacklogTaskStatus status)
        => Task.FromResult(_tasks.Where(t => t.Status == status).ToList());

    public Task AddTaskAsync(BacklogTask task)
    {
        _tasks.Add(task);
        WriteTaskToBacklog(task);
        WriteTaskJson(task);
        return Task.CompletedTask;
    }

    public Task UpdateTaskAsync(BacklogTask task)
    {
        var idx = _tasks.FindIndex(t => t.Id == task.Id);
        if (idx >= 0)
        {
            _tasks[idx] = task;
            RewriteBacklog();
        }
        return Task.CompletedTask;
    }

    public Task DeleteTaskAsync(string taskId)
    {
        _tasks.RemoveAll(t => t.Id == taskId);
        RewriteBacklog();
        return Task.CompletedTask;
    }

    private void WriteTaskToBacklog(BacklogTask task)
    {
        try
        {
            var content = File.Exists(_backlogPath)
                ? File.ReadAllText(_backlogPath)
                : "# Task Backlog\n\n## Pending\n\n## In Progress\n\n## Completed\n";

            var agentTag = !string.IsNullOrEmpty(task.AssignedAgent) ? $" @agent:{task.AssignedAgent}" : "";
            var catTag = !string.IsNullOrEmpty(task.Category) ? $" [{task.Category}]" : "";
            var taskLine = $"- [ ] [{task.Priority}]{catTag} {task.Title}{agentTag}";

            if (content.Contains("## Pending"))
                content = content.Replace("## Pending", $"## Pending\n\n{taskLine}");
            else
                content += $"\n## Pending\n\n{taskLine}\n";

            File.WriteAllText(_backlogPath, content);
            _lastRead = DateTime.UtcNow;
        }
        catch
        {
            // File may be locked
        }
    }

    private void WriteTaskJson(BacklogTask task)
    {
        try
        {
            var taskFile = Path.Combine(_tasksDir, $"{task.Id}.json");
            var json = JsonSerializer.Serialize(new
            {
                id = task.Id,
                title = task.Title,
                description = task.Description,
                priority = task.Priority.ToString(),
                category = task.Category,
                agent = task.AssignedAgent,
                status = task.Status.ToString().ToLowerInvariant(),
                created_at = task.CreatedAt.ToString("O"),
            }, new JsonSerializerOptions { WriteIndented = true });
            File.WriteAllText(taskFile, json);
        }
        catch
        {
            // Non-critical
        }
    }

    private void RewriteBacklog()
    {
        try
        {
            var sb = new System.Text.StringBuilder();
            sb.AppendLine("# Task Backlog\n");

            void WriteSection(string header, BacklogTaskStatus status)
            {
                sb.AppendLine($"## {header}\n");
                foreach (var t in _tasks.Where(t => t.Status == status).OrderBy(t => t.Priority))
                {
                    var check = t.Status == BacklogTaskStatus.Completed ? "x" : " ";
                    var agentTag = !string.IsNullOrEmpty(t.AssignedAgent) ? $" @agent:{t.AssignedAgent}" : "";
                    var catTag = !string.IsNullOrEmpty(t.Category) ? $" [{t.Category}]" : "";
                    sb.AppendLine($"- [{check}] [{t.Priority}]{catTag} {t.Title}{agentTag}");
                }
                sb.AppendLine();
            }

            WriteSection("In Progress", BacklogTaskStatus.InProgress);
            WriteSection("Pending", BacklogTaskStatus.Pending);
            WriteSection("Blocked", BacklogTaskStatus.Blocked);
            WriteSection("Completed", BacklogTaskStatus.Completed);

            File.WriteAllText(_backlogPath, sb.ToString());
            _lastRead = DateTime.UtcNow;
        }
        catch
        {
            // File may be locked
        }
    }
}
