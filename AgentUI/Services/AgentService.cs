using System.Text.RegularExpressions;
using AgentUI.Models;

namespace AgentUI.Services;

/// <summary>
/// Service that monitors the OpenClaw agent by reading openclaw.log.
/// No fake seed data — all state comes from real log files on disk.
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
        _logPath = Path.Combine(_workspaceRoot, "openclaw.log");

        Config = new AgentConfig
        {
            WorkspaceRoot = _workspaceRoot,
            DailyBudget = double.TryParse(Environment.GetEnvironmentVariable("AGENT_DAILY_BUDGET"), out var b) ? b : 5.00,
            LogLevel = Environment.GetEnvironmentVariable("AGENT_LOG_LEVEL") ?? "INFO"
        };

        // Start with real empty state
        Status = new AgentStatus
        {
            IsRunning = false,
            CurrentPhase = AgentPhase.Idle,
            DailyBudget = Config.DailyBudget,
            SessionStart = DateTime.Now,
        };

        // Also read the legacy agent.log if it exists
        ReadExistingLog(Path.Combine(_workspaceRoot, "agent.log"));
        ReadExistingLog(_logPath);

        _pollTimer = new Timer(PollAgentState, null, TimeSpan.FromSeconds(2), TimeSpan.FromSeconds(2));
    }

    /// <summary>Read an entire log file for historical entries.</summary>
    private void ReadExistingLog(string path)
    {
        if (!File.Exists(path)) return;

        try
        {
            foreach (var line in File.ReadLines(path))
            {
                var entry = ParseLogLine(line);
                if (entry != null)
                {
                    Logs.Add(entry);
                    ProcessLogEntry(entry);
                }
            }

            // If this is the openclaw log, remember the position for tail-follow
            if (path == _logPath)
                _lastLogPosition = new FileInfo(path).Length;
        }
        catch
        {
            // File may be locked — will pick it up on next poll
        }
    }

    private void PollAgentState(object? state)
    {
        try
        {
            ReadNewLogEntries();
            ReadStatusFile();
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
                ProcessLogEntry(entry);
            }
        }

        _lastLogPosition = fs.Position;
    }

    /// <summary>Extract status, safety events, and cost from a log entry.</summary>
    private void ProcessLogEntry(LogEntry entry)
    {
        var msg = entry.Message;

        // Detect blocked operations -> safety events
        if (msg.Contains("BLOCKED", StringComparison.OrdinalIgnoreCase))
        {
            var ev = new SafetyEvent
            {
                Timestamp = entry.Timestamp,
                EventType = "RUNTIME_BLOCK",
                Details = msg,
                WasBlocked = true
            };
            SafetyEvents.Add(ev);
            SafetyEventOccurred?.Invoke(this, ev);
        }

        // Detect cost lines: "Cost: $0.1234 / $5.00 (12,345 tokens)"
        var costMatch = Regex.Match(msg, @"Cost:\s*\$([0-9.]+)\s*/\s*\$([0-9.]+)\s*\(([0-9,]+)\s*tokens\)");
        if (costMatch.Success)
        {
            if (double.TryParse(costMatch.Groups[1].Value, out var costVal))
                Status.CostToday = costVal;
            if (double.TryParse(costMatch.Groups[2].Value, out var budget))
                Status.DailyBudget = budget;
        }

        // Detect phase changes
        if (msg.Contains("Initialization complete", StringComparison.OrdinalIgnoreCase))
        {
            Status.IsRunning = true;
            Status.CurrentPhase = AgentPhase.Idle;
        }
        else if (msg.Contains("Calling skill:", StringComparison.OrdinalIgnoreCase))
        {
            Status.CurrentPhase = AgentPhase.Act;
        }
        else if (msg.Contains("Task completed", StringComparison.OrdinalIgnoreCase))
        {
            Status.CompletedTasks++;
            Status.CurrentPhase = AgentPhase.Commit;
            Status.RecentActions.Insert(0, $"Completed: {Status.CurrentTask}");
            if (Status.RecentActions.Count > 10) Status.RecentActions.RemoveAt(10);
        }
        else if (msg.Contains("Agent stopped", StringComparison.OrdinalIgnoreCase))
        {
            Status.IsRunning = false;
            Status.CurrentPhase = AgentPhase.Idle;
        }

        // Detect task assignment
        if (msg.Contains("Running single task:", StringComparison.OrdinalIgnoreCase))
        {
            Status.CurrentTask = msg[(msg.IndexOf("Running single task:") + 21)..].Trim();
            Status.CurrentPhase = AgentPhase.Observe;
            Status.TotalTasks++;
        }

        // Track file creation
        if (msg.Contains("Wrote", StringComparison.OrdinalIgnoreCase) && msg.Contains("chars to", StringComparison.OrdinalIgnoreCase))
        {
            Status.FilesCreatedThisSession++;
        }
    }

    private void ReadStatusFile()
    {
        var statusPath = Path.Combine(_workspaceRoot, "openclaw_status.json");
        if (!File.Exists(statusPath)) return;

        try
        {
            var json = File.ReadAllText(statusPath);
            using var doc = System.Text.Json.JsonDocument.Parse(json);
            var root = doc.RootElement;

            if (root.TryGetProperty("phase", out var phase))
            {
                Status.CurrentPhase = phase.GetString()?.ToLowerInvariant() switch
                {
                    "running" => AgentPhase.Act,
                    "initialized" => AgentPhase.Idle,
                    "stopped" => AgentPhase.Idle,
                    "error" => AgentPhase.Idle,
                    _ => Status.CurrentPhase
                };
                Status.IsRunning = phase.GetString() is "running" or "initialized";
            }

            if (root.TryGetProperty("iteration", out var iter))
                Status.CompletedTasks = iter.GetInt32();
            if (root.TryGetProperty("max_iterations", out var maxIter))
                Status.TotalTasks = maxIter.GetInt32();
            if (root.TryGetProperty("files_created", out var fc))
                Status.FilesCreatedThisSession = fc.GetInt32();

            if (root.TryGetProperty("cost", out var cost))
            {
                if (cost.TryGetProperty("cost_today", out var ct))
                    Status.CostToday = ct.GetDouble();
                if (cost.TryGetProperty("daily_budget", out var db))
                    Status.DailyBudget = db.GetDouble();
            }
        }
        catch
        {
            // Will retry next poll
        }
    }

    private static LogEntry? ParseLogLine(string line)
    {
        if (string.IsNullOrWhiteSpace(line)) return null;

        // Format: "2024-01-15 10:30:45,123 - openclaw.agent - INFO - message"
        var parts = line.Split(" - ", 4);
        if (parts.Length < 4) return new LogEntry { Message = line };

        return new LogEntry
        {
            Timestamp = DateTime.TryParse(parts[0].Trim().Split(',')[0], out var ts) ? ts : DateTime.Now,
            Source = parts[1].Trim(),
            Level = parts[2].Trim(),
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
