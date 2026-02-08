using AgentUI.ViewModels;

namespace AgentUI.Views;

public partial class SafetyPage : ContentPage
{
    public SafetyPage(SafetyViewModel viewModel)
    {
        InitializeComponent();
        BindingContext = viewModel;
    }
}
