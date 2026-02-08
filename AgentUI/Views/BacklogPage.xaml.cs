using AgentUI.ViewModels;

namespace AgentUI.Views;

public partial class BacklogPage : ContentPage
{
    public BacklogPage(BacklogViewModel viewModel)
    {
        InitializeComponent();
        BindingContext = viewModel;
    }
}
