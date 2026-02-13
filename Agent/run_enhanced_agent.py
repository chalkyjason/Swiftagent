#!/usr/bin/env python3
"""
Enhanced Swift Game Agent Runner with Goose LLM Integration
Connects your existing agent with Goose for LLM capabilities and enhanced file/git operations
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from goose_integration import EnhancedSwiftGameAgent, GooseLLMRequest
from swift_game_agent import SwiftGameAgent
import json
from datetime import datetime

class SwiftAgentGooseRunner:
    """Main runner that combines your existing agent with Goose integration"""
    
    def __init__(self):
        self.enhanced_agent = EnhancedSwiftGameAgent("./SwiftTamagotchi")
        self.classic_agent = SwiftGameAgent("./SwiftTamagotchi")
        
    def show_menu(self):
        """Display enhanced menu with Goose integration options"""
        print("\n" + "="*60)
        print("🤖 Enhanced Swift Game Agent with Goose LLM Integration")
        print("="*60)
        print("1. 🔍 Analyze with LLM Assistance")
        print("2. 🛠️  Implement Improvement with LLM")
        print("3. 📊 Generate Status Report")
        print("4. 🔄 Review Changes with LLM")
        print("5. 📝 Git Status and Operations")
        print("6. 💡 Ask Goose LLM Anything")
        print("7. 🎯 Classic Agent Mode")
        print("0. 🚪 Exit")
        print("="*60)
        
    def run_analysis_with_llm(self):
        """Run enhanced analysis with LLM assistance"""
        print("\n🔍 Running analysis with Goose LLM assistance...")
        
        try:
            analysis = self.enhanced_agent.analyze_with_llm_assistance()
            
            print(f"\n✅ Analysis Complete!")
            print(f"📁 Found {len(analysis['swift_files'])} Swift files")
            print(f"📊 Git Status: {analysis['git_status']}")
            print(f"\n🤖 LLM Analysis:")
            print(f"Response: {analysis['llm_analysis'].response}")
            print(f"\n💡 Suggestions:")
            for i, suggestion in enumerate(analysis['llm_analysis'].suggestions, 1):
                print(f"  {i}. {suggestion}")
                
            print(f"\n🎯 Next Actions:")
            for i, action in enumerate(analysis['llm_analysis'].next_actions, 1):
                print(f"  {i}. {action}")
                
            # Save analysis to file
            with open('./Agent/latest_analysis.json', 'w') as f:
                json.dump(analysis, f, indent=2, default=str)
            print("\n💾 Analysis saved to ./Agent/latest_analysis.json")
            
        except Exception as e:
            print(f"❌ Analysis failed: {e}")
    
    def implement_with_llm(self):
        """Implement improvement with LLM assistance"""
        print("\n🛠️ Implement improvement with Goose LLM...")
        
        improvement = input("Enter improvement to implement: ").strip()
        if not improvement:
            print("❌ No improvement specified")
            return
        
        try:
            result = self.enhanced_agent.implement_improvement_with_llm(improvement)
            
            print(f"\n✅ Implementation Generated!")
            print(f"🎯 Improvement: {result['improvement']}")
            print(f"📝 Implementation: {result['implementation'].response}")
            
            if result['implementation'].code_snippets:
                print(f"\n💻 Code Snippets:")
                for i, snippet in enumerate(result['implementation'].code_snippets, 1):
                    print(f"\n--- Snippet {i} ---")
                    print(snippet)
            
            print(f"\n🎯 Next Steps:")
            for i, step in enumerate(result['next_steps'], 1):
                print(f"  {i}. {step}")
                
        except Exception as e:
            print(f"❌ Implementation failed: {e}")
    
    def generate_status_report(self):
        """Generate comprehensive status report"""
        print("\n📊 Generating status report...")
        
        try:
            # Get git status
            git_status = self.enhanced_agent.file_manager.git_status()
            
            # Get project overview
            swift_files = []
            total_lines = 0
            
            for root, dirs, files in os.walk(self.enhanced_agent.project_path):
                for file in files:
                    if file.endswith('.swift'):
                        file_path = os.path.join(root, file)
                        swift_files.append(os.path.relpath(file_path, self.enhanced_agent.project_path))
                        
                        # Count lines
                        try:
                            with open(file_path, 'r') as f:
                                total_lines += len(f.readlines())
                        except:
                            pass
            
            print("\n" + "="*50)
            print("📊 Swift Tamagotchi Game Status Report")
            print("="*50)
            print(f"📁 Swift Files: {len(swift_files)}")
            print(f"📝 Total Lines of Code: {total_lines}")
            print(f"📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            print(f"\n🔄 Git Status:")
            if 'error' in git_status:
                print(f"  ❌ Git Error: {git_status['error']}")
            else:
                print(f"  📝 Modified: {len(git_status['modified'])} files")
                print(f"  ➕ Added: {len(git_status['added'])} files")
                print(f"  ➖ Deleted: {len(git_status['deleted'])} files")
                print(f"  ❓ Untracked: {len(git_status['untracked'])} files")
                
                if git_status['modified']:
                    print(f"  Modified files: {', '.join(git_status['modified'])}")
            
            print(f"\n📁 Swift Files:")
            for i, file in enumerate(swift_files[:10], 1):  # Show first 10
                print(f"  {i}. {file}")
            if len(swift_files) > 10:
                print(f"  ... and {len(swift_files) - 10} more files")
                
        except Exception as e:
            print(f"❌ Status report failed: {e}")
    
    def review_changes_with_llm(self):
        """Review recent changes with LLM"""
        print("\n🔄 Reviewing changes with Goose LLM...")
        
        try:
            git_status = self.enhanced_agent.file_manager.git_status()
            
            if 'error' in git_status:
                print(f"❌ Git error: {git_status['error']}")
                return
            
            changed_files = git_status['modified'] + git_status['added']
            
            if not changed_files:
                print("✅ No changes to review")
                return
            
            review = self.enhanced_agent.review_changes_with_llm(changed_files)
            
            print(f"\n✅ Review Complete!")
            print(f"📁 Files Reviewed: {', '.join(review['files_reviewed'])}")
            print(f"\n🤖 Review: {review['review'].response}")
            print(f"\n💡 Recommendations:")
            for i, rec in enumerate(review['recommendations'], 1):
                print(f"  {i}. {rec}")
                
        except Exception as e:
            print(f"❌ Review failed: {e}")
    
    def git_operations(self):
        """Git operations menu"""
        print("\n🔄 Git Operations")
        print("1. Show Status")
        print("2. Add and Commit Changes")
        print("3. View File Diff")
        print("0. Back to Main Menu")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == "1":
            git_status = self.enhanced_agent.file_manager.git_status()
            print(f"\nGit Status: {json.dumps(git_status, indent=2)}")
            
        elif choice == "2":
            files = input("Enter files to add (space-separated): ").strip().split()
            message = input("Commit message: ").strip()
            
            if files and message:
                success = self.enhanced_agent.file_manager.git_add_and_commit(files, message)
                print("✅ Committed successfully!" if success else "❌ Commit failed")
            else:
                print("❌ Files and message required")
                
        elif choice == "3":
            file_path = input("Enter file path for diff: ").strip()
            if file_path:
                diff = self.enhanced_agent.file_manager.get_file_diff(file_path)
                print(f"\nDiff for {file_path}:")
                print(diff if diff else "No changes")
    
    def ask_llm_anything(self):
        """Direct LLM query interface"""
        print("\n💡 Ask Goose LLM Anything")
        
        question = input("Your question: ").strip()
        if not question:
            print("❌ No question provided")
            return
        
        try:
            request = GooseLLMRequest(
                prompt=question,
                task_type="general",
                context="Swift iOS game development context"
            )
            
            response = self.enhanced_agent.llm.query_llm(request)
            
            print(f"\n🤖 Goose Response:")
            print(response.response)
            
            if response.suggestions:
                print(f"\n💡 Suggestions:")
                for i, suggestion in enumerate(response.suggestions, 1):
                    print(f"  {i}. {suggestion}")
                    
        except Exception as e:
            print(f"❌ Query failed: {e}")
    
    def run_classic_agent(self):
        """Run the original agent functionality"""
        print("\n🎯 Classic Agent Mode")
        print("Running original swift_game_agent functionality...")
        
        try:
            # This would call your existing agent methods
            analysis = self.classic_agent.analyze_game_structure()
            print(f"Classic analysis: {analysis}")
        except Exception as e:
            print(f"❌ Classic agent failed: {e}")
    
    def run(self):
        """Main application loop"""
        while True:
            try:
                self.show_menu()
                choice = input("\nSelect option: ").strip()
                
                if choice == "0":
                    print("👋 Goodbye!")
                    break
                elif choice == "1":
                    self.run_analysis_with_llm()
                elif choice == "2":
                    self.implement_with_llm()
                elif choice == "3":
                    self.generate_status_report()
                elif choice == "4":
                    self.review_changes_with_llm()
                elif choice == "5":
                    self.git_operations()
                elif choice == "6":
                    self.ask_llm_anything()
                elif choice == "7":
                    self.run_classic_agent()
                else:
                    print("❌ Invalid option")
                    
                input("\nPress Enter to continue...")
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                input("\nPress Enter to continue...")

if __name__ == "__main__":
    runner = SwiftAgentGooseRunner()
    runner.run()
