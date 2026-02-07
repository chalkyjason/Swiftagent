using AgentUI.Models;

namespace AgentUI.Services;

public interface IAgentService
{
    AgentStatus Status { get; }
    AgentConfig Config { get; }
    List<LogEntry> Logs { get; }
    List<SafetyEvent> SafetyEvents { get; }
    List<CostEntry> CostHistory { get; }

    event EventHandler<AgentStatus>? StatusChanged;
    event EventHandler<LogEntry>? LogReceived;
    event EventHandler<SafetyEvent>? SafetyEventOccurred;

    Task StartAgentAsync();
    Task StopAgentAsync();
    Task<AgentStatus> GetStatusAsync();
    Task UpdateConfigAsync(AgentConfig config);
    Task<List<LogEntry>> GetLogsAsync(int count = 100);
}
