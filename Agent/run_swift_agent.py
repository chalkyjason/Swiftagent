#!/usr/bin/env python3
"""
Swift Game Agent Launcher
Interactive launcher for the Swift Game Development Agent
"""

import sys
import os
import json
from swift_game_agent import SwiftGameAgent, ImprovementType

def print_banner():
    print("🎮" * 20)
    print("🚀 SWIFT GAME DEVELOPMENT AGENT 🚀")
    print("🎮" * 20)
    print("Specialized agent for improving your Swift Tamagotchi game")
    print()

def show_menu():
    print("📋 Available Actions:")
    print("1. 🔍 Analyze current game")
    print("2. 📊 Generate improvement plan")
    print("3. 🛠️  Implement specific improvement")
    print("4. 📈 Generate status report")
    print("5. 🎯 Focus on specific area")
    print("6. 💡 Get quick recommendations")
    print("7. 🚪 Exit")
    print()

def analyze_game(agent):
    print("🔍 ANALYZING SWIFT TAMAGOTCHI GAME")
    print("-" * 40)
    
    analysis = agent.analyze_game_structure()
    
    print(f"📁 Files analyzed: {analysis['files_analyzed']}")
    print(f"📝 Lines of code: {analysis['lines_of_code']:,}")
    print(f"🏗️  Architecture: {', '.join(analysis['architecture_patterns'])}")
    print(f"⭐ Code quality: {analysis['code_quality_score']:.1f}/10")
    print()
    
    if analysis['potential_improvements']:
        print("💡 Top improvement opportunities:")
        for i, imp in enumerate(analysis['potential_improvements'][:3], 1):
            print(f"  {i}. {imp.title} (Priority: {imp.priority})")
    
    return analysis

def generate_improvement_plan(agent):
    print("📋 GENERATING IMPROVEMENT PLAN")
    print("-" * 40)
    
    focus_areas = ["all", "features", "ui", "performance", "quality"]
    print("Focus areas:", ", ".join(focus_areas))
    focus = input("Enter focus area (default: all): ").strip() or "all"
    
    plan = agent.generate_improvement_plan(focus)
    
    print(f"\n🎯 Found {plan['total_improvements']} improvements")
    print(f"⏱️  Estimated time: {plan['estimated_total_time']}")
    print()
    
    print("🔥 HIGH PRIORITY:")
    for imp in plan['high_priority']:
        print(f"  • {imp.title} (⏰ {imp.estimated_time})")
    
    print("\n📋 MEDIUM PRIORITY:")
    for imp in plan['medium_priority'][:3]:
        print(f"  • {imp.title} (⏰ {imp.estimated_time})")
    
    if plan['low_priority']:
        print(f"\n📝 {len(plan['low_priority'])} lower priority items available")
    
    print("\n📶 RECOMMENDED ORDER:")
    for i, title in enumerate(plan['recommended_order'][:5], 1):
        print(f"  {i}. {title}")
    
    return plan

def implement_improvement(agent):
    print("🛠️  IMPLEMENT IMPROVEMENT")
    print("-" * 40)
    
    # Get available improvements
    all_improvements = agent._generate_initial_improvements()
    
    print("Available improvements:")
    for i, imp in enumerate(all_improvements[:10], 1):
        print(f"  {i}. {imp.title}")
    
    try:
        choice = int(input("\nEnter improvement number: ")) - 1
        if 0 <= choice < len(all_improvements):
            improvement = all_improvements[choice]
            result = agent.implement_improvement(improvement.title)
            
            print(f"\n🎯 Implementing: {improvement.title}")
            print(f"📝 Description: {improvement.description}")
            print(f"⏰ Estimated time: {improvement.estimated_time}")
            print()
            
            if "generated_code" in result and result["generated_code"]:
                print("📄 Generated code files:")
                for filename in result["generated_code"].keys():
                    print(f"  • {filename}")
            
            if "instructions" in result:
                print("\n📋 Implementation steps:")
                for step in result["instructions"]:
                    print(f"  {step}")
            
            return result
        else:
            print("❌ Invalid choice")
    except (ValueError, IndexError):
        print("❌ Invalid input")

def focus_area_analysis(agent):
    print("🎯 FOCUSED AREA ANALYSIS")
    print("-" * 40)
    
    areas = {
        "1": ("features", "New game features and content"),
        "2": ("ui", "User interface and experience"),
        "3": ("performance", "Performance and optimization"),
        "4": ("quality", "Code quality and testing")
    }
    
    print("Focus areas:")
    for key, (area, desc) in areas.items():
        print(f"  {key}. {area.upper()}: {desc}")
    
    choice = input("\nSelect focus area (1-4): ").strip()
    
    if choice in areas:
        area, desc = areas[choice]
        print(f"\n🔍 Focusing on: {desc}")
        
        plan = agent.generate_improvement_plan(area)
        
        print(f"\n📊 {area.upper()} IMPROVEMENTS ({plan['total_improvements']} found):")
        
        all_items = plan['high_priority'] + plan['medium_priority'] + plan['low_priority']
        for imp in all_items:
            print(f"\n📌 {imp.title}")
            print(f"   Priority: {imp.priority}/10")
            print(f"   Time: {imp.estimated_time}")
            print(f"   Description: {imp.description}")
    else:
        print("❌ Invalid choice")

def quick_recommendations(agent):
    print("💡 QUICK RECOMMENDATIONS")
    print("-" * 40)
    
    # Get top 5 high-priority improvements
    improvements = agent._generate_initial_improvements()
    top_5 = sorted(improvements, key=lambda x: x.priority, reverse=True)[:5]
    
    print("🚀 TOP 5 RECOMMENDATIONS:")
    for i, imp in enumerate(top_5, 1):
        print(f"\n{i}. {imp.title}")
        print(f"   🎯 Priority: {imp.priority}/10")
        print(f"   ⏰ Time: {imp.estimated_time}")
        print(f"   💡 {imp.description}")
        print(f"   📁 Files: {', '.join(imp.files_affected[:2])}{'...' if len(imp.files_affected) > 2 else ''}")

def generate_status_report(agent):
    print("📊 GENERATING STATUS REPORT")
    print("-" * 40)
    
    report = agent.generate_status_report()
    
    print("📈 GAME STATUS REPORT")
    print(f"Generated: {report['timestamp']}")
    print()
    
    print("🏗️  CODE HEALTH:")
    health = report['code_health']
    print(f"  Quality Score: {health['quality_score']:.1f}/10")
    print(f"  Architecture: {health['architecture_score']:.1f}/10")
    print(f"  Files: {health['files_count']}")
    print(f"  Lines of Code: {health['lines_of_code']:,}")
    print()
    
    print("🎯 NEXT ACTIONS:")
    for action in report['next_actions']:
        print(f"  {action}")
    
    # Save report
    filename = f"swift_game_report_{report['timestamp'][:10]}.json"
    with open(filename, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    print(f"\n💾 Report saved: {filename}")

def main():
    print_banner()
    
    # Initialize agent
    agent = SwiftGameAgent()
    
    while True:
        show_menu()
        choice = input("Select action (1-7): ").strip()
        
        print("\n" + "="*50)
        
        try:
            if choice == "1":
                analyze_game(agent)
            elif choice == "2":
                generate_improvement_plan(agent)
            elif choice == "3":
                implement_improvement(agent)
            elif choice == "4":
                generate_status_report(agent)
            elif choice == "5":
                focus_area_analysis(agent)
            elif choice == "6":
                quick_recommendations(agent)
            elif choice == "7":
                print("👋 Thanks for using Swift Game Agent!")
                break
            else:
                print("❌ Invalid choice. Please select 1-7.")
        
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("\n" + "="*50)
        input("Press Enter to continue...")
        print()

if __name__ == "__main__":
    main()
