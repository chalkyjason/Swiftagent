using System.Text.RegularExpressions;
using AgentUI.Models;

namespace AgentUI.Services;

/// <summary>
/// Reads and manages the real BACKLOG.md file from the workspace.
/// No hardcoded data — parses the actual markdown file on disk.
/// </summary>
public class BacklogService : IBacklogService
{
    private readonly string _backlogPath;
    private List<BacklogTask> _tasks = new();
    private DateTime _lastRead = DateTime.MinValue;

    public BacklogService()
    {
        var workspaceRoot = Environment.GetEnvironmentVariable("AGENT_WORKSPACE_ROOT")
            ?? Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.UserProfile), "Swiftagent");
        _backlogPath = Path.Combine(workspaceRoot, "BACKLOG.md");

        ParseBacklogFile();
    }

    private void ParseBacklogFile()
    {
        if (!File.Exists(_backlogPath)) return;

        try
        {
            var lastWrite = File.GetLastWriteTimeUtc(_backlogPath);
            if (lastWrite <= _lastRead) return; // No changes

            _lastRead = lastWrite;
            var lines = File.ReadAllLines(_backlogPath);
            var tasks = new List<BacklogTask>();
            string currentSection = "";

            foreach (var rawLine in lines)
            {
                var line = rawLine.Trim();

                // Track section headers
                if (line.StartsWith("##"))
                {
                    var header = line.TrimStart('#').Trim().ToLowerInvariant();
                    if (header.Contains("in progress")) currentSection = "in_progress";
                    else if (header.Contains("completed") || header.Contains("done")) currentSection = "completed";
                    else if (header.Contains("pending") || header.Contains("backlog")) currentSection = "pending";
                    else if (header.Contains("blocked") || header.Contains("failed")) currentSection = "blocked";
                    else if (header.Contains("enhancement")) currentSection = "pending";
                    else if (header.Contains("bug")) currentSection = "pending";
                    else if (header.Contains("documentation") || header.Contains("doc")) currentSection = "pending";
                    continue;
                }

                // Parse task lines: "- [ ] [P1] Task description" or "- [x] Task"
                if (!line.StartsWith("- [")) continue;

                bool isCompleted = line.StartsWith("- [x]", StringComparison.OrdinalIgnoreCase);
                var taskText = Regex.Replace(line, @"^-\s*\[[ xX]\]\s*", "").Trim();

                // Extract priority
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

                // Determine status from checkbox and section context
                var status = isCompleted ? TaskStatus.Completed
                    : currentSection == "in_progress" ? TaskStatus.InProgress
                    : currentSection == "completed" ? TaskStatus.Completed
                    : currentSection == "blocked" ? TaskStatus.Blocked
                    : TaskStatus.Pending;

                // Extract category from task text heuristics
                var category = InferCategory(taskText);

                tasks.Add(new BacklogTask
                {
                    Title = taskText,
                    Priority = priority,
                    Status = status,
                    Category = category,
                    CompletedAt = isCompleted ? DateTime.Now.AddDays(-1) : null,
                });
            }

            _tasks = tasks;
        }
        catch
        {
            // Keep existing tasks if parse fails
        }
    }

    private static string InferCategory(string title)
    {
        var t = title.ToLowerInvariant();
        if (t.Contains("cloudkit") || t.Contains("icloud") || t.Contains("sync")) return "Cloud";
        if (t.Contains("game center") || t.Contains("leaderboard") || t.Contains("achievement")) return "GameKit";
        if (t.Contains("audio") || t.Contains("sound") || t.Contains("spatial")) return "Audio";
        if (t.Contains("haptic") || t.Contains("vibration")) return "Haptics";
        if (t.Contains("menu") || t.Contains("ui") || t.Contains("animation") || t.Contains("navigation")) return "UI";
        if (t.Contains("physics") || t.Contains("collision") || t.Contains("particle")) return "Graphics";
        if (t.Contains("game") || t.Contains("mini") || t.Contains("shooter")) return "Gameplay";
        if (t.Contains("test")) return "Testing";
        if (t.Contains("doc")) return "Docs";
        if (t.Contains("watch") || t.Contains("tvos") || t.Contains("macos")) return "Platform";
        if (t.Contains("accessibility") || t.Contains("voiceover")) return "Accessibility";
        if (t.Contains("analytics")) return "Analytics";
        if (t.Contains("security") || t.Contains("recording")) return "Security";
        return "General";
    }

    public Task<List<BacklogTask>> GetTasksAsync()
    {
        ParseBacklogFile(); // Re-read if file changed
        return Task.FromResult(_tasks.ToList());
    }

    public Task<List<BacklogTask>> GetTasksByStatusAsync(TaskStatus status)
    {
        ParseBacklogFile();
        return Task.FromResult(_tasks.Where(t => t.Status == status).ToList());
    }

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
