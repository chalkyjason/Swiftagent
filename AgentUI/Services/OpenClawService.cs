using System.Text.Json;
using System.Text.RegularExpressions;
using AgentUI.Models;

namespace AgentUI.Services;

/// <summary>
/// Service that connects to and manages the local OpenClaw agent instance.
/// Reads openclaw_status.json, openclaw_skills.json, and openclaw.log from
/// the workspace — all written by the real Python agent.
///
/// Launch the agent: python -m OpenClaw [--dry-run] [--scan-only] [--task "..."]
/// </summary>
public class OpenClawService : IOpenClawService
{
    private readonly Timer _pollTimer;
    private readonly string _workspaceRoot;
    private readonly string _logPath;
    private readonly string _statusPath;
    private readonly string _skillsPath;
    private long _lastLogPosition;
    private System.Diagnostics.Process? _agentProcess;

    public OpenClawStatus Status { get; private set; } = new();
    public OpenClawConfig Config { get; private set; } = new();
    public List<OpenClawSkill> Skills { get; private set; } = new();
    public List<OpenClawConversation> Conversations { get; private set; } = new();
    public OpenClawConversation? ActiveConversation { get; private set; }

    public event EventHandler<OpenClawStatus>? StatusChanged;
    public event EventHandler<ChatMessage>? MessageReceived;

    public OpenClawService()
    {
        _workspaceRoot = Environment.GetEnvironmentVariable("AGENT_WORKSPACE_ROOT")
            ?? Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.UserProfile), "Swiftagent");
        _logPath = Path.Combine(_workspaceRoot, "openclaw.log");
        _statusPath = Path.Combine(_workspaceRoot, "openclaw_status.json");
        _skillsPath = Path.Combine(_workspaceRoot, "openclaw_skills.json");

        // Start with real defaults — no fake data
        Status = new OpenClawStatus
        {
            ConnectionState = OpenClawConnectionState.Disconnected,
            AgentName = "Swiftagent-Claw",
            SelectedModel = "claude-sonnet-4-5-20250929",
            Version = "1.0.0",
            Platform = "Local",
            SafetyScannerEnabled = true,
        };

        // Try to load real state from disk immediately
        LoadStatusFromDisk();
        LoadSkillsFromDisk();

        _pollTimer = new Timer(PollStatus, null, TimeSpan.FromSeconds(2), TimeSpan.FromSeconds(3));
    }

    // ── Polling ─────────────────────────────────────────────────

    private void PollStatus(object? state)
    {
        try
        {
            LoadStatusFromDisk();
            ReadOpenClawLog();

            // Check if agent process is alive
            if (_agentProcess is { HasExited: false })
            {
                Status.ConnectionState = OpenClawConnectionState.Connected;
            }
            else if (_agentProcess is { HasExited: true })
            {
                Status.ConnectionState = OpenClawConnectionState.Disconnected;
                _agentProcess = null;
            }

            StatusChanged?.Invoke(this, Status);
        }
        catch
        {
            // Continue polling
        }
    }

    private void LoadStatusFromDisk()
    {
        if (!File.Exists(_statusPath)) return;

        try
        {
            var json = File.ReadAllText(_statusPath);
            using var doc = JsonDocument.Parse(json);
            var root = doc.RootElement;

            if (root.TryGetProperty("connection_state", out var cs))
            {
                Status.ConnectionState = cs.GetString() switch
                {
                    "connected" => OpenClawConnectionState.Connected,
                    "connecting" => OpenClawConnectionState.Connecting,
                    "error" => OpenClawConnectionState.Error,
                    _ => OpenClawConnectionState.Disconnected
                };
            }

            if (root.TryGetProperty("model", out var m))
                Status.SelectedModel = m.GetString() ?? Status.SelectedModel;
            if (root.TryGetProperty("version", out var v))
                Status.Version = v.GetString() ?? Status.Version;
            if (root.TryGetProperty("active_skills_count", out var asc))
                Status.ActiveSkillsCount = asc.GetInt32();
            if (root.TryGetProperty("total_skills_count", out var tsc))
                Status.TotalSkillsCount = tsc.GetInt32();
            if (root.TryGetProperty("safety_scanner", out var ss))
                Status.SafetyScannerEnabled = ss.GetBoolean();

            if (root.TryGetProperty("cost", out var cost))
            {
                if (cost.TryGetProperty("total_tokens", out var tt))
                    Status.TokensUsedToday = tt.GetInt32();
            }
        }
        catch
        {
            // Corrupted or partially written — skip this cycle
        }
    }

    private void LoadSkillsFromDisk()
    {
        if (!File.Exists(_skillsPath)) return;

        try
        {
            var json = File.ReadAllText(_skillsPath);
            using var doc = JsonDocument.Parse(json);
            var arr = doc.RootElement;

            Skills.Clear();
            foreach (var skill in arr.EnumerateArray())
            {
                var name = skill.GetProperty("name").GetString() ?? "";
                var desc = skill.TryGetProperty("description", out var d) ? d.GetString() ?? "" : "";

                Skills.Add(new OpenClawSkill
                {
                    Name = name,
                    Description = desc,
                    Category = CategorizeSkill(name),
                    Author = "openclaw",
                    Version = "1.0.0",
                    SafetyRating = RateSkillSafety(name),
                    IsEnabled = true,
                    IsWhitelisted = true,
                });
            }

            Status.ActiveSkillsCount = Skills.Count(s => s.IsEnabled);
            Status.TotalSkillsCount = Skills.Count;
        }
        catch
        {
            // Will retry on next poll
        }
    }

    private static string CategorizeSkill(string name) => name switch
    {
        "shell_exec" => "System",
        "file_read" or "file_write" or "file_patch" or "file_list" => "Files",
        "swift_build" or "swift_test" or "search_code" => "Development",
        "git_status" or "git_diff" or "git_commit" => "Git",
        "backlog_read" or "backlog_update_task" => "Project",
        _ => "Other"
    };

    private static SkillSafetyRating RateSkillSafety(string name) => name switch
    {
        "shell_exec" or "git_commit" or "file_write" or "file_patch" => SkillSafetyRating.Community,
        _ => SkillSafetyRating.Verified
    };

    private void ReadOpenClawLog()
    {
        if (!File.Exists(_logPath)) return;

        using var fs = new FileStream(_logPath, FileMode.Open, FileAccess.Read, FileShare.ReadWrite);
        if (fs.Length <= _lastLogPosition) return;

        fs.Seek(_lastLogPosition, SeekOrigin.Begin);
        using var reader = new StreamReader(fs);

        while (reader.ReadLine() is { } line)
        {
            // Extract token counts from cost log lines
            if (line.Contains("tokens)", StringComparison.OrdinalIgnoreCase))
            {
                var match = Regex.Match(line, @"(\d[\d,]+)\s+tokens");
                if (match.Success && int.TryParse(
                    match.Groups[1].Value.Replace(",", ""), out var tokens))
                {
                    Status.TokensUsedToday = tokens;
                }
            }

            // Feed agent text and skill calls into the active conversation
            if (ActiveConversation != null)
            {
                ChatMessage? msg = null;

                if (line.Contains("Calling skill:", StringComparison.OrdinalIgnoreCase))
                {
                    var skillMatch = Regex.Match(line, @"Calling skill:\s*(\w+)");
                    msg = new ChatMessage
                    {
                        Role = ChatRole.Skill,
                        Content = line[(line.IndexOf("Calling skill:") + 15)..].Trim(),
                        SkillName = skillMatch.Success ? skillMatch.Groups[1].Value : null,
                        Timestamp = DateTime.Now
                    };
                }
                else if (line.Contains("Agent:", StringComparison.OrdinalIgnoreCase))
                {
                    msg = new ChatMessage
                    {
                        Role = ChatRole.Assistant,
                        Content = line[(line.IndexOf("Agent:") + 7)..].Trim(),
                        Timestamp = DateTime.Now
                    };
                }

                if (msg != null)
                {
                    ActiveConversation.Messages.Add(msg);
                    ActiveConversation.MessageCount++;
                    ActiveConversation.LastMessageAt = DateTime.Now;
                    MessageReceived?.Invoke(this, msg);
                }
            }
        }

        _lastLogPosition = fs.Position;
    }

    // ── Connect / Disconnect (launches real Python agent) ───────

    public Task ConnectAsync()
    {
        var startInfo = new System.Diagnostics.ProcessStartInfo
        {
            FileName = "python",
            Arguments = "-m OpenClaw",
            WorkingDirectory = _workspaceRoot,
            UseShellExecute = false,
            RedirectStandardOutput = true,
            RedirectStandardError = true,
            CreateNoWindow = true,
        };

        try
        {
            _agentProcess = System.Diagnostics.Process.Start(startInfo);
            Status.ConnectionState = OpenClawConnectionState.Connected;
            Status.ConnectedSince = DateTime.Now;

            // Start a conversation to track this session
            var convo = new OpenClawConversation
            {
                Title = $"Session {DateTime.Now:yyyy-MM-dd HH:mm}",
                IsActive = true
            };
            if (ActiveConversation != null) ActiveConversation.IsActive = false;
            Conversations.Insert(0, convo);
            ActiveConversation = convo;
            Status.ConversationCount = Conversations.Count;
        }
        catch (Exception ex)
        {
            Status.ConnectionState = OpenClawConnectionState.Error;
            // Surface the error so the user knows what went wrong
            var errConvo = new OpenClawConversation { Title = "Connection Error", IsActive = true };
            errConvo.Messages.Add(new ChatMessage
            {
                Role = ChatRole.System,
                Content = $"Failed to start agent: {ex.Message}\n\n"
                    + "Make sure Python and the anthropic package are installed:\n"
                    + "  pip install anthropic\n"
                    + "  export ANTHROPIC_API_KEY=sk-...\n"
                    + "  python -m OpenClaw"
            });
            Conversations.Insert(0, errConvo);
            ActiveConversation = errConvo;
        }

        StatusChanged?.Invoke(this, Status);
        return Task.CompletedTask;
    }

    public Task DisconnectAsync()
    {
        if (_agentProcess is { HasExited: false })
        {
            _agentProcess.Kill(entireProcessTree: true);
            _agentProcess = null;
        }

        Status.ConnectionState = OpenClawConnectionState.Disconnected;
        Status.ConnectedSince = null;
        StatusChanged?.Invoke(this, Status);
        return Task.CompletedTask;
    }

    // ── Remaining interface methods ─────────────────────────────

    public Task<OpenClawStatus> GetStatusAsync() => Task.FromResult(Status);

    public Task UpdateConfigAsync(OpenClawConfig config)
    {
        Config = config;
        Status.SelectedModel = config.SelectedModel;
        Status.SafetyScannerEnabled = config.SafetyScannerEnabled;
        Status.Platform = config.MessagingPlatform;
        return Task.CompletedTask;
    }

    public Task<List<OpenClawSkill>> GetSkillsAsync()
    {
        LoadSkillsFromDisk();  // Refresh from disk
        return Task.FromResult(Skills.ToList());
    }

    public Task ToggleSkillAsync(string skillId, bool enabled)
    {
        var skill = Skills.FirstOrDefault(s => s.Id == skillId);
        if (skill != null)
        {
            skill.IsEnabled = enabled;
            Status.ActiveSkillsCount = Skills.Count(s => s.IsEnabled);
            StatusChanged?.Invoke(this, Status);
        }
        return Task.CompletedTask;
    }

    public Task SetSkillWhitelistAsync(string skillId, bool whitelisted)
    {
        var skill = Skills.FirstOrDefault(s => s.Id == skillId);
        if (skill != null)
        {
            skill.IsWhitelisted = whitelisted;
            if (!whitelisted) skill.IsEnabled = false;
        }
        return Task.CompletedTask;
    }

    public Task<OpenClawConversation> StartConversationAsync(string title)
    {
        var convo = new OpenClawConversation { Title = title, IsActive = true };
        if (ActiveConversation != null) ActiveConversation.IsActive = false;
        Conversations.Insert(0, convo);
        ActiveConversation = convo;
        Status.ConversationCount = Conversations.Count;
        return Task.FromResult(convo);
    }

    public Task<ChatMessage> SendMessageAsync(string conversationId, string message)
    {
        var convo = Conversations.FirstOrDefault(c => c.Id == conversationId);
        if (convo == null) return Task.FromResult(new ChatMessage());

        var userMsg = new ChatMessage { Role = ChatRole.User, Content = message };
        convo.Messages.Add(userMsg);
        convo.MessageCount++;
        convo.LastMessageAt = DateTime.Now;
        MessageReceived?.Invoke(this, userMsg);

        // When connected to a running agent, the response will come through
        // the log polling. When disconnected, tell the user.
        if (Status.ConnectionState != OpenClawConnectionState.Connected)
        {
            var hint = new ChatMessage
            {
                Role = ChatRole.System,
                Content = "Agent is not running. Press Connect to start the OpenClaw agent.",
                Timestamp = DateTime.Now
            };
            convo.Messages.Add(hint);
            convo.MessageCount++;
            MessageReceived?.Invoke(this, hint);
            return Task.FromResult(hint);
        }

        return Task.FromResult(userMsg);
    }

    public Task<List<OpenClawConversation>> GetConversationsAsync()
        => Task.FromResult(Conversations.ToList());
}
