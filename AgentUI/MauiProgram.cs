using AgentUI.Services;
using AgentUI.ViewModels;
using AgentUI.Views;
using CommunityToolkit.Maui;
using Microsoft.Extensions.Logging;

namespace AgentUI;

public static class MauiProgram
{
    public static MauiApp CreateMauiApp()
    {
        var builder = MauiApp.CreateBuilder();
        builder
            .UseMauiApp<App>()
            .UseMauiCommunityToolkit()
            .ConfigureFonts(fonts =>
            {
                fonts.AddFont("OpenSans-Regular.ttf", "OpenSansRegular");
                fonts.AddFont("OpenSans-Semibold.ttf", "OpenSansSemibold");
            });

        // Services
        builder.Services.AddSingleton<IAgentService, AgentService>();
        builder.Services.AddSingleton<IBacklogService, BacklogService>();

        // ViewModels
        builder.Services.AddSingleton<DashboardViewModel>();
        builder.Services.AddSingleton<BacklogViewModel>();
        builder.Services.AddSingleton<ConsoleViewModel>();
        builder.Services.AddSingleton<SettingsViewModel>();
        builder.Services.AddSingleton<SafetyViewModel>();

        // Views
        builder.Services.AddSingleton<DashboardPage>();
        builder.Services.AddSingleton<BacklogPage>();
        builder.Services.AddSingleton<ConsolePage>();
        builder.Services.AddSingleton<SettingsPage>();
        builder.Services.AddSingleton<SafetyPage>();

#if DEBUG
        builder.Logging.AddDebug();
#endif

        return builder.Build();
    }
}
