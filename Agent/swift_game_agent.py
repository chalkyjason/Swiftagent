#!/usr/bin/env python3
"""
Swift Game Development Agent
Specialized agent for improving and enhancing Swift iOS games
"""

import json
import os
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class ImprovementType(Enum):
    FEATURE_ADDITION = "feature_addition"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"
    UI_ENHANCEMENT = "ui_enhancement"
    CODE_REFACTORING = "code_refactoring"
    BUG_FIX = "bug_fix"
    ACCESSIBILITY = "accessibility"
    TESTING = "testing"
    DOCUMENTATION = "documentation"

@dataclass
class GameImprovement:
    improvement_type: ImprovementType
    title: str
    description: str
    priority: int  # 1-10 (10 being highest)
    estimated_time: str
    files_affected: List[str]
    implementation_notes: str
    swift_code: Optional[str] = None

class SwiftGameAgent:
    def __init__(self, project_path: str = "./SwiftTamagotchi"):
        self.project_path = project_path
        self.game_files = {}
        self.current_features = []
        self.improvement_backlog = []
        self.performance_metrics = {}
        
    def analyze_game_structure(self) -> Dict:
        """Analyze the current game structure and identify improvement opportunities"""
        print("🔍 Analyzing Swift Tamagotchi game structure...")
        
        analysis = {
            "files_analyzed": 0,
            "lines_of_code": 0,
            "swift_files": [],
            "architecture_patterns": [],
            "potential_improvements": [],
            "code_quality_score": 0
        }
        
        # Scan for Swift files
        for root, dirs, files in os.walk(self.project_path):
            for file in files:
                if file.endswith('.swift'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r') as f:
                            content = f.read()
                            analysis["swift_files"].append(file)
                            analysis["lines_of_code"] += len(content.splitlines())
                            analysis["files_analyzed"] += 1
                            
                            # Store for later analysis
                            self.game_files[file] = content
                    except Exception as e:
                        print(f"⚠️ Could not read {file}: {e}")
        
        # Analyze architecture patterns
        analysis["architecture_patterns"] = self._detect_architecture_patterns()
        
        # Calculate code quality score
        analysis["code_quality_score"] = self._calculate_code_quality()
        
        # Generate improvement suggestions
        analysis["potential_improvements"] = self._generate_initial_improvements()
        
        print(f"✅ Analysis complete: {analysis['files_analyzed']} files, {analysis['lines_of_code']} lines of code")
        return analysis
    
    def _detect_architecture_patterns(self) -> List[str]:
        """Detect architecture patterns used in the codebase"""
        patterns = []
        
        # Check for MVVM
        if any("@ObservableObject" in content or "ObservableObject" in content for content in self.game_files.values()):
            patterns.append("MVVM (Model-View-ViewModel)")
        
        # Check for SwiftUI
        if any("import SwiftUI" in content for content in self.game_files.values()):
            patterns.append("SwiftUI Declarative UI")
        
        # Check for Combine
        if any("import Combine" in content for content in self.game_files.values()):
            patterns.append("Combine Reactive Programming")
        
        return patterns
    
    def _calculate_code_quality(self) -> float:
        """Calculate a code quality score based on various metrics"""
        score = 0.0
        total_files = len(self.game_files)
        
        if total_files == 0:
            return 0.0
        
        for filename, content in self.game_files.items():
            file_score = 0.0
            lines = content.splitlines()
            
            # Check for documentation
            if any(line.strip().startswith("///") or line.strip().startswith("/**") for line in lines):
                file_score += 2.0
            
            # Check for proper error handling
            if "do {" in content and "catch" in content:
                file_score += 1.5
            
            # Check for good naming conventions
            if re.search(r'func [a-z][a-zA-Z]*\(', content):
                file_score += 1.0
            
            # Check for MARK comments (organization)
            if "// MARK:" in content:
                file_score += 1.0
            
            # Penalty for very long files
            if len(lines) > 500:
                file_score -= 1.0
            
            score += file_score
        
        return min(10.0, score / total_files)
    
    def _generate_initial_improvements(self) -> List[GameImprovement]:
        """Generate initial improvement suggestions based on analysis"""
        improvements = []
        
        # Feature enhancements
        improvements.extend([
            GameImprovement(
                improvement_type=ImprovementType.FEATURE_ADDITION,
                title="Sound Effects System",
                description="Add sound effects for pet actions (feed, play, sleep) and background music",
                priority=8,
                estimated_time="4-6 hours",
                files_affected=["PetModel.swift", "ContentView.swift", "MenuView.swift"],
                implementation_notes="Use AVAudioPlayer for sound effects, add sound toggle in settings"
            ),
            
            GameImprovement(
                improvement_type=ImprovementType.FEATURE_ADDITION,
                title="Haptic Feedback",
                description="Add haptic feedback for user interactions and pet state changes",
                priority=6,
                estimated_time="2-3 hours",
                files_affected=["MenuView.swift", "PetModel.swift"],
                implementation_notes="Use UIImpactFeedbackGenerator for different interaction types"
            ),
            
            GameImprovement(
                improvement_type=ImprovementType.FEATURE_ADDITION,
                title="Multiple Pet Types",
                description="Allow users to choose from different pet types (cat, dog, dragon, etc.)",
                priority=9,
                estimated_time="8-12 hours",
                files_affected=["PetModel.swift", "PetView.swift", "SaveManager.swift"],
                implementation_notes="Create PetType enum, modify rendering system, add selection screen"
            ),
            
            GameImprovement(
                improvement_type=ImprovementType.FEATURE_ADDITION,
                title="Achievement System",
                description="Add achievements for reaching milestones (pet age, stat levels, actions)",
                priority=7,
                estimated_time="6-8 hours",
                files_affected=["GameLogic.swift", "PetModel.swift", "New: AchievementManager.swift"],
                implementation_notes="Create achievement tracking, notifications, and display system"
            ),
            
            GameImprovement(
                improvement_type=ImprovementType.FEATURE_ADDITION,
                title="iOS Widget Support",
                description="Create iOS home screen widget showing pet status",
                priority=8,
                estimated_time="10-15 hours",
                files_affected=["New: TamagotchiWidget.swift", "SaveManager.swift"],
                implementation_notes="Use WidgetKit framework, shared data container, timeline updates"
            )
        ])
        
        # UI/UX improvements
        improvements.extend([
            GameImprovement(
                improvement_type=ImprovementType.UI_ENHANCEMENT,
                title="Advanced Animations",
                description="Add more sophisticated pet animations and transitions",
                priority=6,
                estimated_time="5-7 hours",
                files_affected=["PetView.swift", "ContentView.swift"],
                implementation_notes="Use advanced SwiftUI animations, spring effects, particle systems"
            ),
            
            GameImprovement(
                improvement_type=ImprovementType.UI_ENHANCEMENT,
                title="Dark Mode Support",
                description="Add proper dark mode support with custom color schemes",
                priority=5,
                estimated_time="3-4 hours",
                files_affected=["All View files"],
                implementation_notes="Create custom color sets, test in both light and dark modes"
            ),
            
            GameImprovement(
                improvement_type=ImprovementType.UI_ENHANCEMENT,
                title="Settings Screen",
                description="Add comprehensive settings screen for game customization",
                priority=6,
                estimated_time="4-6 hours",
                files_affected=["New: SettingsView.swift", "GameLogic.swift"],
                implementation_notes="Include notification settings, sound toggles, pet naming, reset options"
            )
        ])
        
        # Performance optimizations
        improvements.extend([
            GameImprovement(
                improvement_type=ImprovementType.PERFORMANCE_OPTIMIZATION,
                title="Optimize Pet Rendering",
                description="Improve pet rendering performance for smoother animations",
                priority=5,
                estimated_time="3-4 hours",
                files_affected=["PetView.swift"],
                implementation_notes="Use efficient drawing techniques, reduce unnecessary redraws"
            ),
            
            GameImprovement(
                improvement_type=ImprovementType.PERFORMANCE_OPTIMIZATION,
                title="Memory Management",
                description="Optimize memory usage and prevent potential leaks",
                priority=7,
                estimated_time="4-5 hours",
                files_affected=["GameLogic.swift", "SaveManager.swift"],
                implementation_notes="Review timer management, weak references, proper cleanup"
            )
        ])
        
        # Testing and quality
        improvements.extend([
            GameImprovement(
                improvement_type=ImprovementType.TESTING,
                title="Unit Tests",
                description="Add comprehensive unit tests for game logic",
                priority=6,
                estimated_time="8-10 hours",
                files_affected=["New: TamagotchiTests.swift"],
                implementation_notes="Test pet stat calculations, save/load, state transitions"
            ),
            
            GameImprovement(
                improvement_type=ImprovementType.ACCESSIBILITY,
                title="Accessibility Improvements",
                description="Add VoiceOver support and accessibility labels",
                priority=5,
                estimated_time="3-4 hours",
                files_affected=["All View files"],
                implementation_notes="Add accessibility labels, hints, and proper navigation"
            )
        ])
        
        return sorted(improvements, key=lambda x: x.priority, reverse=True)
    
    def generate_improvement_plan(self, focus_area: str = "all") -> Dict:
        """Generate a prioritized improvement plan"""
        print(f"📋 Generating improvement plan (focus: {focus_area})...")
        
        all_improvements = self._generate_initial_improvements()
        
        # Filter by focus area if specified
        if focus_area != "all":
            focus_types = {
                "features": [ImprovementType.FEATURE_ADDITION],
                "ui": [ImprovementType.UI_ENHANCEMENT],
                "performance": [ImprovementType.PERFORMANCE_OPTIMIZATION],
                "quality": [ImprovementType.TESTING, ImprovementType.BUG_FIX, ImprovementType.CODE_REFACTORING]
            }
            
            if focus_area in focus_types:
                all_improvements = [imp for imp in all_improvements if imp.improvement_type in focus_types[focus_area]]
        
        plan = {
            "total_improvements": len(all_improvements),
            "focus_area": focus_area,
            "high_priority": [imp for imp in all_improvements if imp.priority >= 8],
            "medium_priority": [imp for imp in all_improvements if 5 <= imp.priority < 8],
            "low_priority": [imp for imp in all_improvements if imp.priority < 5],
            "estimated_total_time": self._calculate_total_time(all_improvements),
            "recommended_order": self._recommend_implementation_order(all_improvements)
        }
        
        return plan
    
    def _calculate_total_time(self, improvements: List[GameImprovement]) -> str:
        """Calculate total estimated time for improvements"""
        total_hours = 0
        
        for improvement in improvements:
            time_str = improvement.estimated_time
            # Parse time estimates (e.g., "4-6 hours", "2-3 hours")
            numbers = re.findall(r'\d+', time_str)
            if numbers:
                # Take the average of the range
                if len(numbers) >= 2:
                    avg_hours = (int(numbers[0]) + int(numbers[1])) / 2
                else:
                    avg_hours = int(numbers[0])
                total_hours += avg_hours
        
        if total_hours < 24:
            return f"{total_hours:.1f} hours"
        else:
            days = total_hours / 8  # Assuming 8 hour work days
            return f"{days:.1f} days ({total_hours:.1f} hours)"
    
    def _recommend_implementation_order(self, improvements: List[GameImprovement]) -> List[str]:
        """Recommend the order of implementation based on priority and dependencies"""
        # Sort by priority first, then by logical dependencies
        priority_order = sorted(improvements, key=lambda x: x.priority, reverse=True)
        
        # Logical implementation order
        recommended_order = []
        
        # Start with foundation improvements
        for imp in priority_order:
            if imp.improvement_type == ImprovementType.CODE_REFACTORING:
                recommended_order.append(imp.title)
        
        # Then core features
        for imp in priority_order:
            if imp.improvement_type == ImprovementType.FEATURE_ADDITION and imp.priority >= 8:
                recommended_order.append(imp.title)
        
        # UI enhancements
        for imp in priority_order:
            if imp.improvement_type == ImprovementType.UI_ENHANCEMENT:
                recommended_order.append(imp.title)
        
        # Performance and remaining features
        for imp in priority_order:
            if imp.title not in recommended_order:
                recommended_order.append(imp.title)
        
        return recommended_order
    
    def implement_improvement(self, improvement_title: str) -> Dict:
        """Implement a specific improvement with code generation"""
        print(f"🛠️ Implementing: {improvement_title}")
        
        # Find the improvement
        all_improvements = self._generate_initial_improvements()
        improvement = next((imp for imp in all_improvements if imp.title == improvement_title), None)
        
        if not improvement:
            return {"error": f"Improvement '{improvement_title}' not found"}
        
        # Generate implementation code based on improvement type
        implementation = {
            "improvement": improvement,
            "generated_code": {},
            "instructions": [],
            "tests": [],
            "documentation": ""
        }
        
        # Generate specific implementations
        if improvement.title == "Sound Effects System":
            implementation = self._implement_sound_system()
        elif improvement.title == "Haptic Feedback":
            implementation = self._implement_haptic_feedback()
        elif improvement.title == "Multiple Pet Types":
            implementation = self._implement_multiple_pet_types()
        elif improvement.title == "Achievement System":
            implementation = self._implement_achievement_system()
        elif improvement.title == "iOS Widget Support":
            implementation = self._implement_widget_support()
        elif improvement.title == "Settings Screen":
            implementation = self._implement_settings_screen()
        else:
            implementation["instructions"] = [f"Manual implementation required for: {improvement_title}"]
        
        return implementation
    
    def _implement_sound_system(self) -> Dict:
        """Generate code for sound effects system"""
        return {
            "generated_code": {
                "SoundManager.swift": """import AVFoundation

class SoundManager: ObservableObject {
    static let shared = SoundManager()
    
    private var audioPlayers: [String: AVAudioPlayer] = [:]
    @Published var soundEnabled = true
    
    private init() {
        setupAudioSession()
    }
    
    private func setupAudioSession() {
        do {
            try AVAudioSession.sharedInstance().setCategory(.ambient, mode: .default)
            try AVAudioSession.sharedInstance().setActive(true)
        } catch {
            print("Failed to set up audio session: \(error)")
        }
    }
    
    func playSound(_ soundName: String) {
        guard soundEnabled else { return }
        
        if let player = audioPlayers[soundName] {
            player.stop()
            player.currentTime = 0
            player.play()
        } else {
            loadAndPlaySound(soundName)
        }
    }
    
    private func loadAndPlaySound(_ soundName: String) {
        guard let path = Bundle.main.path(forResource: soundName, ofType: "mp3") else {
            print("Sound file not found: \(soundName).mp3")
            return
        }
        
        let url = URL(fileURLWithPath: path)
        
        do {
            let player = try AVAudioPlayer(contentsOf: url)
            player.prepareToPlay()
            audioPlayers[soundName] = player
            player.play()
        } catch {
            print("Failed to play sound: \(error)")
        }
    }
}
""",
                "Modified PetModel.swift": """// Add to Pet class actions:

func feed() {
    guard state != .dead else { return }
    
    if hunger < 100 {
        hunger = min(100, hunger + 25)
        happiness = min(100, happiness + 5)
        state = .eating
        
        // Add sound effect
        SoundManager.shared.playSound("feed")
        
        DispatchQueue.main.asyncAfter(deadline: .now() + 2) {
            self.updateState()
        }
    }
}

func play() {
    guard state != .dead else { return }
    
    if energy > 10 {
        happiness = min(100, happiness + 20)
        energy = max(0, energy - 15)
        state = .playing
        
        // Add sound effect
        SoundManager.shared.playSound("play")
        
        DispatchQueue.main.asyncAfter(deadline: .now() + 2) {
            self.updateState()
        }
    }
}
"""
            },
            "instructions": [
                "1. Add SoundManager.swift to your project",
                "2. Add sound files (feed.mp3, play.mp3, sleep.mp3, medicine.mp3) to your bundle",
                "3. Update PetModel.swift with sound calls",
                "4. Add sound toggle in settings"
            ],
            "assets_needed": [
                "feed.mp3 - feeding sound effect",
                "play.mp3 - playing sound effect", 
                "sleep.mp3 - sleeping sound effect",
                "medicine.mp3 - medicine sound effect"
            ]
        }
    
    def _implement_haptic_feedback(self) -> Dict:
        """Generate code for haptic feedback system"""
        return {
            "generated_code": {
                "HapticManager.swift": """import UIKit

class HapticManager {
    static let shared = HapticManager()
    
    private init() {}
    
    func impact(_ style: UIImpactFeedbackGenerator.FeedbackStyle) {
        let impactFeedback = UIImpactFeedbackGenerator(style: style)
        impactFeedback.impactOccurred()
    }
    
    func notification(_ type: UINotificationFeedbackGenerator.FeedbackType) {
        let notificationFeedback = UINotificationFeedbackGenerator()
        notificationFeedback.notificationOccurred(type)
    }
    
    func selection() {
        let selectionFeedback = UISelectionFeedbackGenerator()
        selectionFeedback.selectionChanged()
    }
}
""",
                "Modified MenuButton": """struct MenuButton: View {
    let icon: String
    let title: String
    let color: Color
    let disabled: Bool
    let action: () -> Void
    
    var body: some View {
        Button(action: {
            // Add haptic feedback
            HapticManager.shared.impact(.medium)
            action()
        }) {
            // ... existing button code
        }
    }
}
"""
            }
        }
    
    def _implement_multiple_pet_types(self) -> Dict:
        """Generate code for multiple pet types system"""
        return {
            "generated_code": {
                "PetType.swift": """import SwiftUI

enum PetType: String, CaseIterable, Codable {
    case cat = "cat"
    case dog = "dog"
    case dragon = "dragon"
    case bunny = "bunny"
    
    var displayName: String {
        return rawValue.capitalized
    }
    
    var emoji: String {
        switch self {
        case .cat: return "🐱"
        case .dog: return "🐶"
        case .dragon: return "🐉"
        case .bunny: return "🐰"
        }
    }
    
    var baseColor: Color {
        switch self {
        case .cat: return .orange
        case .dog: return .brown
        case .dragon: return .purple
        case .bunny: return .pink
        }
    }
    
    var statBonus: (hunger: Double, happiness: Double, health: Double, energy: Double) {
        switch self {
        case .cat: return (hunger: 5, happiness: 10, health: 0, energy: 5)
        case .dog: return (hunger: 10, happiness: 15, health: 5, energy: 10)
        case .dragon: return (hunger: 0, happiness: 5, health: 15, energy: 0)
        case .bunny: return (hunger: 15, happiness: 5, health: 0, energy: 15)
        }
    }
}
""",
                "PetSelectionView.swift": """import SwiftUI

struct PetSelectionView: View {
    @Binding var selectedPetType: PetType?
    @Environment(\.presentationMode) var presentationMode
    
    let columns = Array(repeating: GridItem(.flexible()), count: 2)
    
    var body: some View {
        NavigationView {
            VStack(spacing: 20) {
                Text("Choose Your Pet!")
                    .font(.title)
                    .fontWeight(.bold)
                
                Text("Each pet type has unique traits and bonuses")
                    .font(.caption)
                    .foregroundColor(.secondary)
                    .multilineTextAlignment(.center)
                
                LazyVGrid(columns: columns, spacing: 20) {
                    ForEach(PetType.allCases, id: \.self) { petType in
                        PetTypeCard(petType: petType) {
                            selectedPetType = petType
                            presentationMode.wrappedValue.dismiss()
                        }
                    }
                }
                .padding()
                
                Spacer()
            }
            .navigationTitle("Pet Selection")
            .navigationBarItems(trailing: 
                Button("Cancel") {
                    presentationMode.wrappedValue.dismiss()
                }
            )
        }
    }
}

struct PetTypeCard: View {
    let petType: PetType
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            VStack(spacing: 10) {
                Text(petType.emoji)
                    .font(.system(size: 60))
                
                Text(petType.displayName)
                    .font(.headline)
                    .foregroundColor(.primary)
                
                VStack(alignment: .leading, spacing: 4) {
                    BonusRow(icon: "🍎", value: petType.statBonus.hunger)
                    BonusRow(icon: "😊", value: petType.statBonus.happiness)
                    BonusRow(icon: "❤️", value: petType.statBonus.health)
                    BonusRow(icon: "⚡", value: petType.statBonus.energy)
                }
                .font(.caption)
            }
            .padding()
            .background(
                RoundedRectangle(cornerRadius: 12)
                    .fill(petType.baseColor.opacity(0.2))
                    .overlay(
                        RoundedRectangle(cornerRadius: 12)
                            .stroke(petType.baseColor, lineWidth: 2)
                    )
            )
        }
    }
}

struct BonusRow: View {
    let icon: String
    let value: Double
    
    var body: some View {
        HStack {
            Text(icon)
            Text("+\(Int(value))")
                .fontWeight(.medium)
        }
    }
}
"""
            },
            "instructions": [
                "1. Add PetType.swift to your Models folder",
                "2. Add PetSelectionView.swift to your Views folder", 
                "3. Update Pet model to include petType property",
                "4. Modify PetView to use pet type colors and emojis",
                "5. Add pet selection screen to onboarding flow"
            ]
        }
    
    def _implement_achievement_system(self) -> Dict:
        """Generate code for achievement system"""
        return {
            "instructions": [
                "Achievement system implementation requires:",
                "1. Create Achievement model with title, description, condition",
                "2. Add AchievementManager to track progress",
                "3. Integrate achievement checking with pet actions",
                "4. Create achievement display UI"
            ]
        }
    
    def _implement_widget_support(self) -> Dict:
        """Generate code for iOS widget support"""
        return {
            "instructions": [
                "iOS Widget implementation requires:",
                "1. Add WidgetKit extension to project",
                "2. Create shared data container",
                "3. Implement widget timeline provider",
                "4. Design widget UI with pet status"
            ]
        }
    
    def _implement_settings_screen(self) -> Dict:
        """Generate code for settings screen"""
        return {
            "instructions": [
                "Settings screen implementation includes:",
                "1. Create SettingsView with SwiftUI",
                "2. Add sound toggle, notification settings",
                "3. Pet naming functionality",
                "4. Reset options and data management"
            ]
        }
    
    def generate_status_report(self) -> Dict:
        """Generate a comprehensive status report of the game"""
        print("📊 Generating game status report...")
        
        analysis = self.analyze_game_structure()
        improvement_plan = self.generate_improvement_plan()
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "game_analysis": analysis,
            "improvement_recommendations": improvement_plan,
            "next_actions": self._generate_next_actions(improvement_plan),
            "code_health": {
                "quality_score": analysis["code_quality_score"],
                "lines_of_code": analysis["lines_of_code"],
                "files_count": analysis["files_analyzed"],
                "architecture_score": self._rate_architecture()
            }
        }
        
        return report
    
    def _generate_next_actions(self, improvement_plan: Dict) -> List[str]:
        """Generate recommended next actions"""
        actions = []
        
        if improvement_plan["high_priority"]:
            top_improvement = improvement_plan["high_priority"][0]
            actions.append(f"🚀 Start with: {top_improvement.title}")
            actions.append(f"📝 Estimated time: {top_improvement.estimated_time}")
        
        actions.extend([
            "🧪 Set up unit testing framework",
            "📱 Test on multiple iOS versions",
            "🎨 Review UI/UX with users",
            "⚡ Profile app performance"
        ])
        
        return actions
    
    def _rate_architecture(self) -> float:
        """Rate the current architecture quality"""
        score = 5.0  # Base score
        
        # Check for good patterns
        if "MVVM" in self._detect_architecture_patterns():
            score += 1.5
        if "SwiftUI" in str(self._detect_architecture_patterns()):
            score += 1.0
        if "Combine" in str(self._detect_architecture_patterns()):
            score += 0.5
        
        return min(10.0, score)

def main():
    """Main function to run the Swift Game Agent"""
    print("🎮 Swift Game Development Agent")
    print("=" * 50)
    
    agent = SwiftGameAgent()
    
    # Run analysis
    analysis = agent.analyze_game_structure()
    print(f"\n📊 Code Quality Score: {analysis['code_quality_score']:.1f}/10")
    print(f"📁 Architecture: {', '.join(analysis['architecture_patterns'])}")
    
    # Generate improvement plan
    plan = agent.generate_improvement_plan()
    print(f"\n🎯 Found {plan['total_improvements']} improvement opportunities")
    print(f"⏱️  Total estimated time: {plan['estimated_total_time']}")
    
    # Show top recommendations
    print("\n🔥 Top Priority Improvements:")
    for i, improvement in enumerate(plan['high_priority'][:3], 1):
        print(f"  {i}. {improvement.title} (Priority: {improvement.priority})")
        print(f"     ⏰ {improvement.estimated_time}")
        print(f"     📝 {improvement.description}")
        print()
    
    # Generate full report
    report = agent.generate_status_report()
    
    return report

if __name__ == "__main__":
    report = main()
    
    # Save report
    with open("swift_game_improvement_report.json", "w") as f:
        json.dump(report, f, indent=2, default=str)
    
    print("✅ Report saved to: swift_game_improvement_report.json")
