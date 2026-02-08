using AgentUI.ViewModels;

namespace AgentUI.Views;

public partial class ConsolePage : ContentPage
{
    public ConsolePage(ConsoleViewModel viewModel)
    {
        InitializeComponent();
        BindingContext = viewModel;
    }
}
