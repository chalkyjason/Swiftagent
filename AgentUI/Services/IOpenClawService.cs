using AgentUI.Models;

namespace AgentUI.Services;

public interface IOpenClawService
{
    OpenClawStatus Status { get; }
    OpenClawConfig Config { get; }
    List<OpenClawSkill> Skills { get; }
    List<OpenClawConversation> Conversations { get; }
    OpenClawConversation? ActiveConversation { get; }

    event EventHandler<OpenClawStatus>? StatusChanged;
    event EventHandler<ChatMessage>? MessageReceived;

    Task ConnectAsync();
    Task DisconnectAsync();
    Task<OpenClawStatus> GetStatusAsync();
    Task UpdateConfigAsync(OpenClawConfig config);

    Task<List<OpenClawSkill>> GetSkillsAsync();
    Task ToggleSkillAsync(string skillId, bool enabled);
    Task SetSkillWhitelistAsync(string skillId, bool whitelisted);

    Task<OpenClawConversation> StartConversationAsync(string title);
    Task<ChatMessage> SendMessageAsync(string conversationId, string message);
    Task<List<OpenClawConversation>> GetConversationsAsync();
}
