#!/usr/bin/env python3
"""
Test script for Goose integration functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from goose_integration import EnhancedSwiftGameAgent, GooseLLMRequest, FileGitManager
import json

def test_file_operations():
    """Test file operations"""
    print("🧪 Testing file operations...")
    
    file_manager = FileGitManager("./SwiftTamagotchi")
    
    # Test reading a file
    readme_content = file_manager.read_file_safe("README.md")
    if readme_content:
        print(f"✅ Successfully read README.md ({len(readme_content)} chars)")
    else:
        print("❌ Failed to read README.md")
    
    # Test git status
    git_status = file_manager.git_status()
    print(f"✅ Git status: {git_status}")

def test_llm_interface():
    """Test LLM interface (simulation)"""
    print("\n🧪 Testing LLM interface...")
    
    agent = EnhancedSwiftGameAgent("./SwiftTamagotchi")
    
    # Test basic LLM request
    request = GooseLLMRequest(
        prompt="Analyze this Swift project structure",
        task_type="analysis",
        context="Test context"
    )
    
    response = agent.llm.query_llm(request)
    print(f"✅ LLM Response: {response.response}")
    print(f"✅ Suggestions: {response.suggestions}")

def test_enhanced_analysis():
    """Test enhanced analysis functionality"""
    print("\n🧪 Testing enhanced analysis...")
    
    try:
        agent = EnhancedSwiftGameAgent("./SwiftTamagotchi")
        analysis = agent.analyze_with_llm_assistance()
        print(f"✅ Analysis completed successfully")
        print(f"   - Swift files: {len(analysis['swift_files'])}")
        print(f"   - Git status keys: {list(analysis['git_status'].keys())}")
    except Exception as e:
        print(f"❌ Analysis failed: {e}")

if __name__ == "__main__":
    print("🚀 Testing Goose Integration Components")
    print("=" * 50)
    
    test_file_operations()
    test_llm_interface() 
    test_enhanced_analysis()
    
    print("\n✅ Integration tests completed!")
