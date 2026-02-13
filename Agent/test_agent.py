#!/usr/bin/env python3
"""
Quick test script for Swift Game Development Agent
"""

from swift_game_agent import SwiftGameAgent, ImprovementType

def test_agent():
    print("🧪 Testing Swift Game Development Agent")
    print("=" * 50)
    
    # Initialize agent
    agent = SwiftGameAgent()
    
    # Test analysis
    print("\n1. 🔍 Testing Game Analysis...")
    analysis = agent.analyze_game_structure()
    
    print(f"   ✅ Files analyzed: {analysis['files_analyzed']}")
    print(f"   ✅ Lines of code: {analysis['lines_of_code']:,}")
    print(f"   ✅ Quality score: {analysis['code_quality_score']:.1f}/10")
    
    # Test improvement plan
    print("\n2. 📋 Testing Improvement Plan...")
    plan = agent.generate_improvement_plan()
    
    print(f"   ✅ Total improvements: {plan['total_improvements']}")
    print(f"   ✅ High priority: {len(plan['high_priority'])}")
    print(f"   ✅ Estimated time: {plan['estimated_total_time']}")
    
    # Test focused analysis
    print("\n3. 🎯 Testing Focused Analysis...")
    feature_plan = agent.generate_improvement_plan("features")
    
    print(f"   ✅ Feature improvements: {feature_plan['total_improvements']}")
    
    # Test implementation
    print("\n4. 🛠️ Testing Implementation Generation...")
    if plan['high_priority']:
        top_improvement = plan['high_priority'][0]
        result = agent.implement_improvement(top_improvement.title)
        
        if "generated_code" in result and result["generated_code"]:
            print(f"   ✅ Generated code for: {top_improvement.title}")
            print(f"   ✅ Files created: {len(result['generated_code'])}")
        else:
            print(f"   ℹ️ Manual implementation for: {top_improvement.title}")
    
    # Test status report
    print("\n5. 📊 Testing Status Report...")
    report = agent.generate_status_report()
    
    print(f"   ✅ Report generated: {report['timestamp']}")
    print(f"   ✅ Code health score: {report['code_health']['quality_score']:.1f}/10")
    print(f"   ✅ Next actions: {len(report['next_actions'])}")
    
    print("\n🎉 All tests completed successfully!")
    
    # Show quick recommendations
    print("\n💡 Quick Recommendations:")
    improvements = agent._generate_initial_improvements()
    top_3 = sorted(improvements, key=lambda x: x.priority, reverse=True)[:3]
    
    for i, imp in enumerate(top_3, 1):
        print(f"   {i}. {imp.title} (Priority: {imp.priority})")
        print(f"      ⏰ {imp.estimated_time}")
        print(f"      📝 {imp.description}")
        print()

if __name__ == "__main__":
    test_agent()
