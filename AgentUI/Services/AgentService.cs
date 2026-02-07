using AgentUI.Models;

namespace AgentUI.Services;

/// <summary>
/// Service that monitors and controls the Python agent process.
/// Reads agent.log and checkpoint files to track state.
/// </summary>
public class AgentService : IAgentService
{
    private readonly Timer _pollTimer;
    private readonly string _workspaceRoot;
    private readonly string _logPath;
    private long _lastLogPosition;

    public AgentStatus Status { get; private set; } = new();
    public AgentConfig Config { get; private set; } = new();
    public List<LogEntry> Logs { get; private set; } = new();
    public List<SafetyEvent> SafetyEvents { get; private set; } = new();
    public List<CostEntry> CostHistory { get; private set; } = new();

    public event EventHandler<AgentStatus>? StatusChanged;
    public event EventHandler<LogEntry>? LogReceived;
    public event EventHandler<SafetyEvent>? SafetyEventOccurred;

    public AgentService()
    {
        _workspaceRoot = Environment.GetEnvironmentVariable("AGENT_WORKSPACE_ROOT")
            ?? Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.UserProfile), "Swiftagent");
        _logPath = Path.Combine(_workspaceRoot, "agent.log");

        Config = new AgentConfig
        {
            WorkspaceRoot = _workspaceRoot,
            DailyBudget = double.TryParse(Environment.GetEnvironmentVariable("AGENT_DAILY_BUDGET"), out var b) ? b : 5.00,
            LogLevel = Environment.GetEnvironmentVariable("AGENT_LOG_LEVEL") ?? "INFO"
        };

        _pollTimer = new Timer(PollAgentState, null, TimeSpan.Zero, TimeSpan.FromSeconds(2));
        SeedDemoData();
    }

    private void SeedDemoData()
    {
        Status = new AgentStatus
        {
            IsRunning = true,
            CurrentPhase = AgentPhase.Orient,
            CurrentTask = "Implement CloudKit sync for game saves",
            CompletedTasks = 7,
            TotalTasks = 22,
            CostToday = 1.37,
            DailyBudget = 5.00,
            FilesCreatedThisSession = 12,
            SessionStart = DateTime.Now.AddHours(-2.5),
            RecentActions = new List<string>
            {
                "Completed: Add haptic feedback patterns",
                "Completed: Create base game scene class",
                "Completed: Implement sound manager",
                "Started: CloudKit sync for game saves",
                "Fetched context from vector store (3 relevant chunks)"
            }
        };

        Logs = new List<LogEntry>
        {
            new() { Timestamp = DateTime.Now.AddMinutes(-45), Level = "INFO", Message = "Agent started — OODA loop initialized", Source = "game_agent" },
            new() { Timestamp = DateTime.Now.AddMinutes(-44), Level = "INFO", Message = "OBSERVE: Fetched task [P1] CloudKit sync from BACKLOG.md", Source = "game_agent" },
            new() { Timestamp = DateTime.Now.AddMinutes(-43), Level = "INFO", Message = "ORIENT: Querying vector store for CloudKit patterns", Source = "context_manager" },
            new() { Timestamp = DateTime.Now.AddMinutes(-42), Level = "INFO", Message = "Retrieved 3 relevant context chunks (1,847 tokens)", Source = "context_manager" },
            new() { Timestamp = DateTime.Now.AddMinutes(-40), Level = "INFO", Message = "DECIDE: Planning implementation — 4 files to create/modify", Source = "game_agent" },
            new() { Timestamp = DateTime.Now.AddMinutes(-38), Level = "WARN", Message = "Token usage approaching 80% of context window", Source = "context_manager" },
            new() { Timestamp = DateTime.Now.AddMinutes(-35), Level = "INFO", Message = "ACT: Creating CloudKitSyncManager.swift", Source = "game_agent" },
            new() { Timestamp = DateTime.Now.AddMinutes(-30), Level = "INFO", Message = "ACT: Modifying GameAuth/Package.swift — adding CloudKit dependency", Source = "game_agent" },
            new() { Timestamp = DateTime.Now.AddMinutes(-25), Level = "INFO", Message = "VERIFY: Running swift build...", Source = "game_agent" },
            new() { Timestamp = DateTime.Now.AddMinutes(-23), Level = "ERROR", Message = "Build failed: Missing import CloudKit in CloudKitSyncManager.swift", Source = "game_agent" },
            new() { Timestamp = DateTime.Now.AddMinutes(-22), Level = "INFO", Message = "ACT: Fixing missing import statement", Source = "game_agent" },
            new() { Timestamp = DateTime.Now.AddMinutes(-20), Level = "INFO", Message = "VERIFY: Running swift build... SUCCESS", Source = "game_agent" },
            new() { Timestamp = DateTime.Now.AddMinutes(-18), Level = "INFO", Message = "VERIFY: Running swift test... 14/14 passed", Source = "game_agent" },
            new() { Timestamp = DateTime.Now.AddMinutes(-15), Level = "INFO", Message = "COMMIT: Changes committed — 'Add CloudKit sync manager'", Source = "game_agent" },
            new() { Timestamp = DateTime.Now.AddMinutes(-10), Level = "INFO", Message = "Cost update: $0.23 for this task cycle (total today: $1.37)", Source = "game_agent" },
        };

        SafetyEvents = new List<SafetyEvent>
        {
            new() { Timestamp = DateTime.Now.AddHours(-2), EventType = "PATH_VALIDATION", Details = "Blocked access to /etc/passwd — outside workspace", WasBlocked = true },
            new() { Timestamp = DateTime.Now.AddHours(-1.5), EventType = "COMMAND_FILTER", Details = "Blocked 'rm -rf /' — dangerous command pattern", WasBlocked = true },
            new() { Timestamp = DateTime.Now.AddHours(-1), EventType = "FILE_SIZE_CHECK", Details = "Allowed 45KB file creation (limit: 1MB)", WasBlocked = false },
            new() { Timestamp = DateTime.Now.AddMinutes(-30), EventType = "SAFE_DELETE", Details = "Moved old test file to .trash instead of deleting", WasBlocked = false },
        };

        CostHistory = new List<CostEntry>
        {
            new() { Timestamp = DateTime.Now.AddHours(-2.5), Amount = 0.18, Operation = "Task: Add haptic feedback", TokensUsed = 12_400 },
            new() { Timestamp = DateTime.Now.AddHours(-2), Amount = 0.31, Operation = "Task: Create base game scene", TokensUsed = 22_100 },
            new() { Timestamp = DateTime.Now.AddHours(-1.5), Amount = 0.24, Operation = "Task: Implement sound manager", TokensUsed = 16_800 },
            new() { Timestamp = DateTime.Now.AddHours(-1), Amount = 0.41, Operation = "Task: Physics collision system", TokensUsed = 28_900 },
            new() { Timestamp = DateTime.Now.AddMinutes(-30), Amount = 0.23, Operation = "Task: CloudKit sync manager", TokensUsed = 15_600 },
        };
    }

    private void PollAgentState(object? state)
    {
        try
        {
            ReadNewLogEntries();
            ReadCheckpointState();
            StatusChanged?.Invoke(this, Status);
        }
        catch
        {
            // Silently continue polling
        }
    }

    private void ReadNewLogEntries()
    {
        if (!File.Exists(_logPath)) return;

        using var fs = new FileStream(_logPath, FileMode.Open, FileAccess.Read, FileShare.ReadWrite);
        if (fs.Length <= _lastLogPosition) return;

        fs.Seek(_lastLogPosition, SeekOrigin.Begin);
        using var reader = new StreamReader(fs);

        while (reader.ReadLine() is { } line)
        {
            var entry = ParseLogLine(line);
            if (entry != null)
            {
                Logs.Add(entry);
                LogReceived?.Invoke(this, entry);

                if (entry.Message.Contains("BLOCKED", StringComparison.OrdinalIgnoreCase))
                {
                    var safetyEvent = new SafetyEvent
                    {
                        Timestamp = entry.Timestamp,
                        EventType = "RUNTIME_BLOCK",
                        Details = entry.Message,
                        WasBlocked = true
                    };
                    SafetyEvents.Add(safetyEvent);
                    SafetyEventOccurred?.Invoke(this, safetyEvent);
                }
            }
        }

        _lastLogPosition = fs.Position;
    }

    private void ReadCheckpointState()
    {
        var checkpointPath = Path.Combine(_workspaceRoot, ".agent_checkpoint.json");
        if (!File.Exists(checkpointPath)) return;
        // Future: parse checkpoint JSON to update agent status
    }

    private static LogEntry? ParseLogLine(string line)
    {
        if (string.IsNullOrWhiteSpace(line)) return null;

        // Expected format: "2024-01-15 10:30:45 - module - LEVEL - message"
        var parts = line.Split(" - ", 4);
        if (parts.Length < 4) return new LogEntry { Message = line };

        var level = parts[2].Trim();
        return new LogEntry
        {
            Timestamp = DateTime.TryParse(parts[0].Trim(), out var ts) ? ts : DateTime.Now,
            Source = parts[1].Trim(),
            Level = level,
            Message = parts[3].Trim()
        };
    }

    public Task StartAgentAsync()
    {
        Status.IsRunning = true;
        Status.SessionStart = DateTime.Now;
        StatusChanged?.Invoke(this, Status);
        return Task.CompletedTask;
    }

    public Task StopAgentAsync()
    {
        Status.IsRunning = false;
        Status.CurrentPhase = AgentPhase.Idle;
        StatusChanged?.Invoke(this, Status);
        return Task.CompletedTask;
    }

    public Task<AgentStatus> GetStatusAsync() => Task.FromResult(Status);

    public Task UpdateConfigAsync(AgentConfig config)
    {
        Config = config;
        return Task.CompletedTask;
    }

    public Task<List<LogEntry>> GetLogsAsync(int count = 100)
    {
        return Task.FromResult(Logs.TakeLast(count).ToList());
    }
}
