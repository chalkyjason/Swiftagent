namespace AgentUI.Models;

public enum OpenClawConnectionState
{
    Disconnected,
    Connecting,
    Connected,
    Error
}

public enum SkillSafetyRating
{
    Verified,
    Community,
    Unreviewed,
    Flagged
}

public enum ChatRole
{
    User,
    Assistant,
    System,
    Skill
}

public class OpenClawStatus
{
    public OpenClawConnectionState ConnectionState { get; set; } = OpenClawConnectionState.Disconnected;
    public string AgentName { get; set; } = "OpenClaw";
    public string SelectedModel { get; set; } = string.Empty;
    public string Version { get; set; } = "2.0.0";
    public int ActiveSkillsCount { get; set; }
    public int TotalSkillsCount { get; set; }
    public int ConversationCount { get; set; }
    public int PendingTasks { get; set; }
    public DateTime? ConnectedSince { get; set; }
    public TimeSpan? Uptime => ConnectedSince.HasValue ? DateTime.Now - ConnectedSince.Value : null;
    public string Platform { get; set; } = string.Empty;
    public int TokensUsedToday { get; set; }
    public bool SafetyScannerEnabled { get; set; }

    // Multi-agent statuses: key = agent name, value = status string
    public Dictionary<string, string> AgentStatuses { get; set; } = new();
}

public class OpenClawSkill
{
    public string Id { get; set; } = Guid.NewGuid().ToString("N")[..8];
    public string Name { get; set; } = string.Empty;
    public string Description { get; set; } = string.Empty;
    public string Category { get; set; } = string.Empty;
    public string Author { get; set; } = string.Empty;
    public string Version { get; set; } = "2.0.0";
    public SkillSafetyRating SafetyRating { get; set; } = SkillSafetyRating.Unreviewed;
    public bool IsEnabled { get; set; }
    public bool IsWhitelisted { get; set; }
    public int UsageCount { get; set; }
    public DateTime InstalledAt { get; set; } = DateTime.Now;
    public List<string> RequiredPermissions { get; set; } = new();
}

public class ChatMessage
{
    public string Id { get; set; } = Guid.NewGuid().ToString("N")[..8];
    public ChatRole Role { get; set; }
    public string Content { get; set; } = string.Empty;
    public DateTime Timestamp { get; set; } = DateTime.Now;
    public string? SkillName { get; set; }
    public bool IsStreaming { get; set; }
}

public class OpenClawConversation
{
    public string Id { get; set; } = Guid.NewGuid().ToString("N")[..8];
    public string Title { get; set; } = string.Empty;
    public DateTime CreatedAt { get; set; } = DateTime.Now;
    public DateTime LastMessageAt { get; set; } = DateTime.Now;
    public int MessageCount { get; set; }
    public List<ChatMessage> Messages { get; set; } = new();
    public bool IsActive { get; set; }
}

public class OpenClawConfig
{
    public string Host { get; set; } = "localhost";
    public int Port { get; set; } = 3142;
    public string SelectedModel { get; set; } = "claude-sonnet-4-5-20250929";
    public List<string> AvailableModels { get; set; } = new()
    {
        "claude-sonnet-4-5-20250929",
        "claude-opus-4-6",
        "claude-haiku-4-5-20251001",
    };
    public bool SafetyScannerEnabled { get; set; } = true;
    public bool WhitelistOnlyMode { get; set; } = true;
    public string MessagingPlatform { get; set; } = string.Empty;
    public List<string> AvailablePlatforms { get; set; } = new();
    public bool ClaudeCliEnabled { get; set; }
    public bool GooseEnabled { get; set; }
    public bool AiderEnabled { get; set; }
    public bool CodexEnabled { get; set; }
    public bool ClineEnabled { get; set; }
}
