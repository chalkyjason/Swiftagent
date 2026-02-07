using System.Collections.ObjectModel;
using AgentUI.Models;
using AgentUI.Services;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;

namespace AgentUI.ViewModels;

public partial class SkillsViewModel : ObservableObject
{
    private readonly IOpenClawService _openClawService;

    [ObservableProperty] private string _selectedFilter = "All";
    [ObservableProperty] private int _totalCount;
    [ObservableProperty] private int _enabledCount;
    [ObservableProperty] private int _verifiedCount;
    [ObservableProperty] private int _flaggedCount;
    [ObservableProperty] private bool _whitelistOnlyMode;

    public ObservableCollection<OpenClawSkill> Skills { get; } = new();
    public ObservableCollection<OpenClawSkill> FilteredSkills { get; } = new();

    public SkillsViewModel(IOpenClawService openClawService)
    {
        _openClawService = openClawService;
        WhitelistOnlyMode = openClawService.Config.WhitelistOnlyMode;
        _ = LoadSkillsAsync();
    }

    [RelayCommand]
    private async Task LoadSkillsAsync()
    {
        var skills = await _openClawService.GetSkillsAsync();
        Skills.Clear();
        foreach (var skill in skills)
            Skills.Add(skill);

        UpdateCounts();
        ApplyFilter();
    }

    [RelayCommand]
    private void Filter(string filter)
    {
        SelectedFilter = filter;
        ApplyFilter();
    }

    [RelayCommand]
    private async Task ToggleSkillAsync(OpenClawSkill skill)
    {
        await _openClawService.ToggleSkillAsync(skill.Id, !skill.IsEnabled);
        await LoadSkillsAsync();
    }

    [RelayCommand]
    private async Task ToggleWhitelistAsync(OpenClawSkill skill)
    {
        await _openClawService.SetSkillWhitelistAsync(skill.Id, !skill.IsWhitelisted);
        await LoadSkillsAsync();
    }

    private void ApplyFilter()
    {
        FilteredSkills.Clear();
        var filtered = SelectedFilter switch
        {
            "Enabled" => Skills.Where(s => s.IsEnabled),
            "Disabled" => Skills.Where(s => !s.IsEnabled),
            "Verified" => Skills.Where(s => s.SafetyRating == SkillSafetyRating.Verified),
            "Community" => Skills.Where(s => s.SafetyRating == SkillSafetyRating.Community),
            "Flagged" => Skills.Where(s => s.SafetyRating == SkillSafetyRating.Flagged),
            "Whitelisted" => Skills.Where(s => s.IsWhitelisted),
            _ => Skills.AsEnumerable()
        };

        foreach (var skill in filtered.OrderBy(s => s.SafetyRating).ThenBy(s => s.Name))
            FilteredSkills.Add(skill);
    }

    private void UpdateCounts()
    {
        TotalCount = Skills.Count;
        EnabledCount = Skills.Count(s => s.IsEnabled);
        VerifiedCount = Skills.Count(s => s.SafetyRating == SkillSafetyRating.Verified);
        FlaggedCount = Skills.Count(s => s.SafetyRating == SkillSafetyRating.Flagged);
    }
}
