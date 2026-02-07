using System.Collections.ObjectModel;
using AgentUI.Models;
using AgentUI.Services;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;

namespace AgentUI.ViewModels;

public partial class OpenClawViewModel : ObservableObject
{
    private readonly IOpenClawService _openClawService;

    // Connection status
    [ObservableProperty] private bool _isConnected;
    [ObservableProperty] private string _connectionState = "Disconnected";
    [ObservableProperty] private Color _connectionColor = Colors.Grey;
    [ObservableProperty] private string _agentName = string.Empty;
    [ObservableProperty] private string _selectedModel = string.Empty;
    [ObservableProperty] private string _version = string.Empty;
    [ObservableProperty] private string _uptime = "--";
    [ObservableProperty] private string _platform = "Local";
    [ObservableProperty] private int _activeSkills;
    [ObservableProperty] private int _totalSkills;
    [ObservableProperty] private string _tokensUsed = "0";
    [ObservableProperty] private bool _safetyScannerEnabled;

    // Chat
    [ObservableProperty] private string _messageText = string.Empty;
    [ObservableProperty] private string _activeConversationTitle = "No active conversation";
    [ObservableProperty] private bool _hasActiveConversation;

    public ObservableCollection<ChatMessage> Messages { get; } = new();
    public ObservableCollection<OpenClawConversation> Conversations { get; } = new();

    public OpenClawViewModel(IOpenClawService openClawService)
    {
        _openClawService = openClawService;
        _openClawService.StatusChanged += OnStatusChanged;
        _openClawService.MessageReceived += OnMessageReceived;
        _ = RefreshAsync();
    }

    private void OnStatusChanged(object? sender, OpenClawStatus status) =>
        MainThread.BeginInvokeOnMainThread(() => UpdateFromStatus(status));

    private void OnMessageReceived(object? sender, ChatMessage msg) =>
        MainThread.BeginInvokeOnMainThread(() => Messages.Add(msg));

    [RelayCommand]
    private async Task RefreshAsync()
    {
        var status = await _openClawService.GetStatusAsync();
        UpdateFromStatus(status);

        var conversations = await _openClawService.GetConversationsAsync();
        Conversations.Clear();
        foreach (var c in conversations)
            Conversations.Add(c);

        LoadActiveConversation();
    }

    [RelayCommand]
    private async Task ToggleConnectionAsync()
    {
        if (IsConnected)
            await _openClawService.DisconnectAsync();
        else
            await _openClawService.ConnectAsync();

        await RefreshAsync();
    }

    [RelayCommand]
    private async Task SendMessageAsync()
    {
        if (string.IsNullOrWhiteSpace(MessageText)) return;

        var convo = _openClawService.ActiveConversation;
        if (convo == null)
        {
            convo = await _openClawService.StartConversationAsync("New Task");
            LoadActiveConversation();
        }

        var text = MessageText;
        MessageText = string.Empty;
        await _openClawService.SendMessageAsync(convo.Id, text);
    }

    [RelayCommand]
    private async Task NewConversationAsync()
    {
        await _openClawService.StartConversationAsync($"Task {DateTime.Now:HH:mm}");
        await RefreshAsync();
    }

    [RelayCommand]
    private void SelectConversation(OpenClawConversation conversation)
    {
        foreach (var c in Conversations)
            c.IsActive = c.Id == conversation.Id;

        Messages.Clear();
        foreach (var msg in conversation.Messages)
            Messages.Add(msg);

        ActiveConversationTitle = conversation.Title;
        HasActiveConversation = true;
    }

    private void LoadActiveConversation()
    {
        var active = _openClawService.ActiveConversation;
        if (active != null)
        {
            Messages.Clear();
            foreach (var msg in active.Messages)
                Messages.Add(msg);

            ActiveConversationTitle = active.Title;
            HasActiveConversation = true;
        }
    }

    private void UpdateFromStatus(OpenClawStatus status)
    {
        IsConnected = status.ConnectionState == OpenClawConnectionState.Connected;
        ConnectionState = status.ConnectionState.ToString();
        ConnectionColor = status.ConnectionState switch
        {
            OpenClawConnectionState.Connected => Color.FromArgb("#00e676"),
            OpenClawConnectionState.Connecting => Color.FromArgb("#ffea00"),
            OpenClawConnectionState.Error => Color.FromArgb("#ff1744"),
            _ => Color.FromArgb("#6c757d")
        };
        AgentName = status.AgentName;
        SelectedModel = status.SelectedModel;
        Version = status.Version;
        Platform = status.Platform;
        ActiveSkills = status.ActiveSkillsCount;
        TotalSkills = status.TotalSkillsCount;
        TokensUsed = $"{status.TokensUsedToday:N0}";
        SafetyScannerEnabled = status.SafetyScannerEnabled;
        Uptime = status.Uptime.HasValue
            ? $"{status.Uptime.Value.Hours}h {status.Uptime.Value.Minutes}m"
            : "--";
    }
}
