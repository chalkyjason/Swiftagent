using AgentUI.Models;

namespace AgentUI.Services;

/// <summary>
/// Service that connects to and manages the local OpenClaw agent instance.
/// Monitors openclaw.log for real-time status and feeds logs into the UI.
/// Launch the agent via: python -m OpenClaw [--dry-run] [--scan-only] [--task "..."]
/// </summary>
public class OpenClawService : IOpenClawService
{
    private readonly Timer _pollTimer;
    private readonly string _workspaceRoot;
    private readonly string _logPath;
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
        SeedDemoData();
        _pollTimer = new Timer(PollStatus, null, TimeSpan.FromSeconds(5), TimeSpan.FromSeconds(3));
    }

    private void SeedDemoData()
    {
        Status = new OpenClawStatus
        {
            ConnectionState = OpenClawConnectionState.Connected,
            AgentName = "Swiftagent-Claw",
            SelectedModel = "claude-opus-4-6",
            Version = "v2026.2.6",
            ActiveSkillsCount = 8,
            TotalSkillsCount = 14,
            ConversationCount = 3,
            PendingTasks = 2,
            ConnectedSince = DateTime.Now.AddHours(-1.5),
            Platform = "Local",
            TokensUsedToday = 48_200,
            SafetyScannerEnabled = true
        };

        Skills = new List<OpenClawSkill>
        {
            // Shell & File Skills
            new() { Name = "shell_exec", Description = "Execute shell commands in a sandboxed environment", Category = "System", Author = "openclaw-core", Version = "2.1.0", SafetyRating = SkillSafetyRating.Verified, IsEnabled = true, IsWhitelisted = true, UsageCount = 47, RequiredPermissions = new() { "shell.execute", "process.spawn" } },
            new() { Name = "file_manager", Description = "Read, write, and manage files within the workspace", Category = "System", Author = "openclaw-core", Version = "2.0.3", SafetyRating = SkillSafetyRating.Verified, IsEnabled = true, IsWhitelisted = true, UsageCount = 83, RequiredPermissions = new() { "fs.read", "fs.write" } },
            new() { Name = "git_ops", Description = "Git operations: commit, branch, diff, log", Category = "Development", Author = "openclaw-core", Version = "1.4.0", SafetyRating = SkillSafetyRating.Verified, IsEnabled = true, IsWhitelisted = true, UsageCount = 29, RequiredPermissions = new() { "shell.execute", "fs.read" } },
            new() { Name = "swift_build", Description = "Build and test Swift packages via swift CLI", Category = "Development", Author = "swiftagent", Version = "1.0.0", SafetyRating = SkillSafetyRating.Community, IsEnabled = true, IsWhitelisted = true, UsageCount = 34, RequiredPermissions = new() { "shell.execute" } },
            new() { Name = "web_search", Description = "Search the web for documentation and solutions", Category = "Research", Author = "openclaw-core", Version = "1.2.0", SafetyRating = SkillSafetyRating.Verified, IsEnabled = true, IsWhitelisted = true, UsageCount = 21, RequiredPermissions = new() { "net.http" } },
            new() { Name = "web_scrape", Description = "Fetch and parse web page content", Category = "Research", Author = "openclaw-core", Version = "1.1.0", SafetyRating = SkillSafetyRating.Verified, IsEnabled = true, IsWhitelisted = true, UsageCount = 12, RequiredPermissions = new() { "net.http" } },
            new() { Name = "code_analysis", Description = "Static analysis of Swift/Python source code", Category = "Development", Author = "openclaw-core", Version = "1.3.0", SafetyRating = SkillSafetyRating.Verified, IsEnabled = true, IsWhitelisted = true, UsageCount = 15, RequiredPermissions = new() { "fs.read" } },
            new() { Name = "backlog_sync", Description = "Parse and update BACKLOG.md task file", Category = "Project", Author = "swiftagent", Version = "1.0.0", SafetyRating = SkillSafetyRating.Community, IsEnabled = true, IsWhitelisted = true, UsageCount = 18, RequiredPermissions = new() { "fs.read", "fs.write" } },

            // Disabled / Not whitelisted
            new() { Name = "docker_ops", Description = "Manage Docker containers and images", Category = "System", Author = "community-contrib", Version = "0.9.2", SafetyRating = SkillSafetyRating.Community, IsEnabled = false, IsWhitelisted = false, UsageCount = 0, RequiredPermissions = new() { "shell.execute", "docker.api" } },
            new() { Name = "db_query", Description = "Execute SQL queries against local databases", Category = "Data", Author = "community-contrib", Version = "0.8.1", SafetyRating = SkillSafetyRating.Unreviewed, IsEnabled = false, IsWhitelisted = false, UsageCount = 0, RequiredPermissions = new() { "db.connect", "db.query" } },
            new() { Name = "email_send", Description = "Send emails via SMTP", Category = "Communication", Author = "community-contrib", Version = "1.0.0", SafetyRating = SkillSafetyRating.Unreviewed, IsEnabled = false, IsWhitelisted = false, UsageCount = 0, RequiredPermissions = new() { "net.smtp" } },
            new() { Name = "screenshot", Description = "Capture screen and window screenshots", Category = "System", Author = "community-contrib", Version = "0.7.0", SafetyRating = SkillSafetyRating.Flagged, IsEnabled = false, IsWhitelisted = false, UsageCount = 0, RequiredPermissions = new() { "screen.capture" } },
            new() { Name = "crypto_wallet", Description = "Interact with cryptocurrency wallets", Category = "Finance", Author = "unknown", Version = "0.2.0", SafetyRating = SkillSafetyRating.Flagged, IsEnabled = false, IsWhitelisted = false, UsageCount = 0, RequiredPermissions = new() { "net.http", "fs.read", "fs.write" } },
            new() { Name = "clipboard_access", Description = "Read and write system clipboard", Category = "System", Author = "community-contrib", Version = "0.5.0", SafetyRating = SkillSafetyRating.Unreviewed, IsEnabled = false, IsWhitelisted = false, UsageCount = 0, RequiredPermissions = new() { "clipboard.read", "clipboard.write" } },
        };

        var activeConvo = new OpenClawConversation
        {
            Title = "CloudKit Sync Implementation",
            CreatedAt = DateTime.Now.AddHours(-1),
            LastMessageAt = DateTime.Now.AddMinutes(-5),
            MessageCount = 8,
            IsActive = true,
            Messages = new List<ChatMessage>
            {
                new() { Role = ChatRole.User, Content = "Implement CloudKit sync for game saves in the GameAuth package. It should support saving and loading game state to iCloud.", Timestamp = DateTime.Now.AddMinutes(-60) },
                new() { Role = ChatRole.Assistant, Content = "I'll implement CloudKit sync for game saves. Let me start by analyzing the existing GameAuth package structure and then create a CloudKitSyncManager.\n\nFirst, let me check the current package layout.", Timestamp = DateTime.Now.AddMinutes(-59) },
                new() { Role = ChatRole.Skill, Content = "Executed: file_manager.list_directory(\"Packages/GameAuth/Sources\")\n\nFound 3 files:\n- GameCenterManager.swift\n- AuthenticationState.swift\n- PlayerProfile.swift", Timestamp = DateTime.Now.AddMinutes(-58), SkillName = "file_manager" },
                new() { Role = ChatRole.Assistant, Content = "Good. I can see the existing structure. I'll create a new `CloudKitSyncManager.swift` file that integrates with the existing authentication flow. Let me also search for CloudKit best practices.", Timestamp = DateTime.Now.AddMinutes(-57) },
                new() { Role = ChatRole.Skill, Content = "Executed: web_search.query(\"CloudKit CKRecord game save Swift async await 2026\")\n\nFound 5 relevant results about CloudKit game save patterns.", Timestamp = DateTime.Now.AddMinutes(-55), SkillName = "web_search" },
                new() { Role = ChatRole.Assistant, Content = "Based on the research, I'll implement the sync manager using CKRecord with async/await. Here's my plan:\n\n1. Create `CloudKitSyncManager.swift` with save/load/delete operations\n2. Define a `GameSaveRecord` model for CKRecord mapping\n3. Add conflict resolution with last-writer-wins strategy\n4. Update Package.swift to include CloudKit framework\n\nLet me start creating the files.", Timestamp = DateTime.Now.AddMinutes(-52) },
                new() { Role = ChatRole.Skill, Content = "Executed: file_manager.write(\"Packages/GameAuth/Sources/CloudKitSyncManager.swift\")\n\nCreated CloudKitSyncManager.swift (127 lines)\n\nExecuted: swift_build.run(\"Packages/GameAuth\")\n\nBuild succeeded. 0 warnings.", Timestamp = DateTime.Now.AddMinutes(-40), SkillName = "swift_build" },
                new() { Role = ChatRole.Assistant, Content = "CloudKit sync manager has been implemented and builds successfully. The implementation includes:\n\n- `CloudKitSyncManager`: Main actor-isolated singleton\n- `save(gameState:)`: Saves game state to iCloud\n- `load(recordId:)`: Loads game state from iCloud\n- `delete(recordId:)`: Removes a save from iCloud\n- `syncAll()`: Fetches all saves and resolves conflicts\n\nWould you like me to add unit tests or proceed to the next backlog task?", Timestamp = DateTime.Now.AddMinutes(-38) },
            }
        };

        Conversations = new List<OpenClawConversation>
        {
            activeConvo,
            new() { Title = "SpriteKit Physics Setup", CreatedAt = DateTime.Now.AddHours(-4), LastMessageAt = DateTime.Now.AddHours(-3), MessageCount = 12, IsActive = false },
            new() { Title = "Audio Engine Architecture", CreatedAt = DateTime.Now.AddDays(-1), LastMessageAt = DateTime.Now.AddDays(-1).AddHours(2), MessageCount = 6, IsActive = false },
        };

        ActiveConversation = activeConvo;
    }

    private void PollStatus(object? state)
    {
        try
        {
            ReadOpenClawLog();

            // Check if the agent process is running
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

    private void ReadOpenClawLog()
    {
        if (!File.Exists(_logPath)) return;

        using var fs = new FileStream(_logPath, FileMode.Open, FileAccess.Read, FileShare.ReadWrite);
        if (fs.Length <= _lastLogPosition) return;

        fs.Seek(_lastLogPosition, SeekOrigin.Begin);
        using var reader = new StreamReader(fs);

        while (reader.ReadLine() is { } line)
        {
            // Parse log lines and update token counts / status
            if (line.Contains("tokens)", StringComparison.OrdinalIgnoreCase))
            {
                // Extract token usage from cost log lines
                var match = System.Text.RegularExpressions.Regex.Match(
                    line, @"(\d[\d,]+)\s+tokens");
                if (match.Success && int.TryParse(
                    match.Groups[1].Value.Replace(",", ""), out var tokens))
                {
                    Status.TokensUsedToday = tokens;
                }
            }

            if (line.Contains("Calling skill:", StringComparison.OrdinalIgnoreCase))
            {
                // Feed skill calls into the active conversation
                var msg = new ChatMessage
                {
                    Role = ChatRole.Skill,
                    Content = line,
                    Timestamp = DateTime.Now
                };
                ActiveConversation?.Messages.Add(msg);
                MessageReceived?.Invoke(this, msg);
            }
        }

        _lastLogPosition = fs.Position;
    }

    public Task ConnectAsync()
    {
        // Launch the OpenClaw agent process
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
        }
        catch
        {
            Status.ConnectionState = OpenClawConnectionState.Error;
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

    public Task<OpenClawStatus> GetStatusAsync() => Task.FromResult(Status);

    public Task UpdateConfigAsync(OpenClawConfig config)
    {
        Config = config;
        Status.SelectedModel = config.SelectedModel;
        Status.SafetyScannerEnabled = config.SafetyScannerEnabled;
        Status.Platform = config.MessagingPlatform;
        return Task.CompletedTask;
    }

    public Task<List<OpenClawSkill>> GetSkillsAsync() => Task.FromResult(Skills.ToList());

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
        if (ActiveConversation != null)
            ActiveConversation.IsActive = false;
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

        // Simulate assistant response
        var response = new ChatMessage
        {
            Role = ChatRole.Assistant,
            Content = $"Acknowledged. I'll work on: \"{message}\"\n\nLet me analyze the codebase and determine the best approach.",
            Timestamp = DateTime.Now.AddSeconds(1)
        };
        convo.Messages.Add(response);
        convo.MessageCount++;
        MessageReceived?.Invoke(this, response);

        return Task.FromResult(response);
    }

    public Task<List<OpenClawConversation>> GetConversationsAsync()
        => Task.FromResult(Conversations.ToList());
}
