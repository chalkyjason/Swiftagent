namespace AgentUI.Models;

public enum AgentPhase
{
    Idle,
    Observe,
    Orient,
    Decide,
    Act,
    Verify,
    Commit
}

public enum TaskPriority
{
    P1,
    P2,
    P3
}

public enum BacklogTaskStatus
{
    Pending,
    InProgress,
    Completed,
    Blocked
}

public class AgentStatus
{
    public AgentPhase CurrentPhase { get; set; } = AgentPhase.Idle;
    public bool IsRunning { get; set; }
    public string CurrentTask { get; set; } = string.Empty;
    public int CompletedTasks { get; set; }
    public int TotalTasks { get; set; }
    public double CostToday { get; set; }
    public double DailyBudget { get; set; } = 5.00;
    public int FilesCreatedThisSession { get; set; }
    public int MaxFilesPerSession { get; set; } = 100;
    public DateTime SessionStart { get; set; } = DateTime.Now;
    public TimeSpan Uptime => DateTime.Now - SessionStart;
    public List<string> RecentActions { get; set; } = new();

    // Multi-agent status
    public Dictionary<string, string> AgentStatuses { get; set; } = new();
}

public class BacklogTask
{
    public string Id { get; set; } = Guid.NewGuid().ToString("N")[..8];
    public string Title { get; set; } = string.Empty;
    public string Description { get; set; } = string.Empty;
    public TaskPriority Priority { get; set; } = TaskPriority.P2;
    public BacklogTaskStatus Status { get; set; } = BacklogTaskStatus.Pending;
    public string Category { get; set; } = string.Empty;
    public string AssignedAgent { get; set; } = string.Empty;
    public DateTime CreatedAt { get; set; } = DateTime.Now;
    public DateTime? CompletedAt { get; set; }
}

public class LogEntry
{
    public DateTime Timestamp { get; set; } = DateTime.Now;
    public string Level { get; set; } = "INFO";
    public string Message { get; set; } = string.Empty;
    public string Source { get; set; } = string.Empty;
}

public class SafetyEvent
{
    public DateTime Timestamp { get; set; } = DateTime.Now;
    public string EventType { get; set; } = string.Empty;
    public string Details { get; set; } = string.Empty;
    public bool WasBlocked { get; set; }
}

public class CostEntry
{
    public DateTime Timestamp { get; set; } = DateTime.Now;
    public double Amount { get; set; }
    public string Operation { get; set; } = string.Empty;
    public int TokensUsed { get; set; }
}

public class AgentConfig
{
    public string WorkspaceRoot { get; set; } = string.Empty;
    public double DailyBudget { get; set; } = 5.00;
    public string LogLevel { get; set; } = "INFO";
    public int MaxFilesPerSession { get; set; } = 100;
    public long MaxFileSizeBytes { get; set; } = 1_048_576;
    public bool SafeDeleteEnabled { get; set; } = true;
    public bool SandboxEnabled { get; set; } = true;
    public int MaxContextTokens { get; set; } = 100_000;
    public bool ClaudeCliEnabled { get; set; }
    public bool GooseEnabled { get; set; }
    public bool AiderEnabled { get; set; }
    public bool CodexEnabled { get; set; }
    public bool ClineEnabled { get; set; }
}
