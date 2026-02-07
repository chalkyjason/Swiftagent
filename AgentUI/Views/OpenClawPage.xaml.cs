using AgentUI.ViewModels;

namespace AgentUI.Views;

public partial class OpenClawPage : ContentPage
{
    public OpenClawPage(OpenClawViewModel viewModel)
    {
        InitializeComponent();
        BindingContext = viewModel;
    }
}
