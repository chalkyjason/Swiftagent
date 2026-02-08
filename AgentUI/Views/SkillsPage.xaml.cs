using AgentUI.ViewModels;

namespace AgentUI.Views;

public partial class SkillsPage : ContentPage
{
    public SkillsPage(SkillsViewModel viewModel)
    {
        InitializeComponent();
        BindingContext = viewModel;
    }
}
