"""
Goose LLM Integration Module
Provides interface for Swift Game Agent to access Goose LLM capabilities
"""

import json
import subprocess
import requests
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

@dataclass
class GooseLLMRequest:
    """Request structure for Goose LLM operations"""
    prompt: str
    context: Optional[str] = None
    task_type: str = "general"  # general, code_review, code_generation, analysis
    files_context: Optional[List[str]] = None

@dataclass
class GooseLLMResponse:
    """Response structure from Goose LLM"""
    response: str
    suggestions: List[str]
    code_snippets: List[str]
    next_actions: List[str]

class GooseLLMInterface:
    """Interface to communicate with Goose LLM for enhanced agent capabilities"""
    
    def __init__(self, workspace_path: str):
        self.workspace_path = workspace_path
        self.session_context = []
        
    def query_llm(self, request: GooseLLMRequest) -> GooseLLMResponse:
        """Send request to Goose LLM and get structured response"""
        
        # Build context-aware prompt
        full_prompt = self._build_contextual_prompt(request)
        
        # For now, this would integrate with Goose through IPC or API
        # In practice, this could use Goose's tool execution capabilities
        
        # Simulate structured response (in real implementation, this would call Goose)
        return GooseLLMResponse(
            response=f"LLM response for: {request.prompt}",
            suggestions=[
                "Add comprehensive error handling",
                "Implement MVVM pattern more consistently",
                "Add unit tests for core functionality"
            ],
            code_snippets=[
                "// Swift code example would be generated here"
            ],
            next_actions=[
                "Review current architecture",
                "Implement suggested improvements",
                "Test changes thoroughly"
            ]
        )
    
    def _build_contextual_prompt(self, request: GooseLLMRequest) -> str:
        """Build a context-aware prompt for Goose"""
        
        context_parts = []
        
        # Add file context if provided
        if request.files_context:
            context_parts.append("=== FILE CONTEXT ===")
            for file_path in request.files_context:
                if os.path.exists(file_path):
                    with open(file_path, 'r') as f:
                        content = f.read()
                        context_parts.append(f"File: {file_path}")
                        context_parts.append(content)
        
        # Add session context
        if self.session_context:
            context_parts.append("=== SESSION CONTEXT ===")
            context_parts.extend(self.session_context[-5:])  # Last 5 interactions
        
        # Add general context
        if request.context:
            context_parts.append("=== ADDITIONAL CONTEXT ===")
            context_parts.append(request.context)
        
        # Build final prompt
        full_prompt = "\n\n".join(context_parts)
        full_prompt += f"\n\n=== TASK ({request.task_type.upper()}) ===\n"
        full_prompt += request.prompt
        
        return full_prompt
    
    def add_to_context(self, interaction: str):
        """Add interaction to session context"""
        self.session_context.append(interaction)
        
        # Keep only last 10 interactions to manage memory
        if len(self.session_context) > 10:
            self.session_context = self.session_context[-10:]

class FileGitManager:
    """Enhanced file and git operations with safety checks"""
    
    def __init__(self, workspace_path: str):
        self.workspace_path = workspace_path
        self.safe_extensions = {'.swift', '.py', '.json', '.md', '.txt', '.yml', '.yaml', '.toml'}
        
    def read_file_safe(self, file_path: str) -> Optional[str]:
        """Safely read file with validation"""
        full_path = os.path.join(self.workspace_path, file_path)
        
        # Safety checks
        if not self._is_safe_path(full_path):
            raise ValueError(f"Unsafe file path: {file_path}")
        
        if not os.path.exists(full_path):
            return None
            
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return None
    
    def write_file_safe(self, file_path: str, content: str, backup: bool = True) -> bool:
        """Safely write file with backup option"""
        full_path = os.path.join(self.workspace_path, file_path)
        
        # Safety checks
        if not self._is_safe_path(full_path):
            raise ValueError(f"Unsafe file path: {file_path}")
        
        try:
            # Create backup if file exists
            if backup and os.path.exists(full_path):
                backup_path = f"{full_path}.backup"
                with open(full_path, 'r') as original:
                    with open(backup_path, 'w') as backup_file:
                        backup_file.write(original.read())
            
            # Write new content
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return True
            
        except Exception as e:
            print(f"Error writing {file_path}: {e}")
            return False
    
    def _is_safe_path(self, path: str) -> bool:
        """Check if path is safe to operate on"""
        
        # Must be within workspace
        if not os.path.abspath(path).startswith(os.path.abspath(self.workspace_path)):
            return False
        
        # Check file extension
        _, ext = os.path.splitext(path)
        if ext.lower() not in self.safe_extensions:
            return False
        
        # Prevent access to hidden/system files
        if any(part.startswith('.') for part in path.split('/') if part not in {'.', '..'}):
            # Allow specific known safe hidden files
            safe_hidden = {'.gitignore', '.gitattributes', '.swiftlint.yml'}
            filename = os.path.basename(path)
            if filename not in safe_hidden:
                return False
        
        return True
    
    def git_status(self) -> Dict[str, Any]:
        """Get git repository status"""
        try:
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                cwd=self.workspace_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            # Parse git status output
            status = {
                'modified': [],
                'added': [],
                'deleted': [],
                'untracked': []
            }
            
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue
                    
                status_code = line[:2]
                file_path = line[3:]
                
                if status_code[0] == 'M':
                    status['modified'].append(file_path)
                elif status_code[0] == 'A':
                    status['added'].append(file_path)
                elif status_code[0] == 'D':
                    status['deleted'].append(file_path)
                elif status_code == '??':
                    status['untracked'].append(file_path)
            
            return status
            
        except subprocess.CalledProcessError as e:
            print(f"Git status error: {e}")
            return {'error': str(e)}
    
    def git_add_and_commit(self, files: List[str], message: str) -> bool:
        """Add files and commit with message"""
        try:
            # Add files
            for file_path in files:
                full_path = os.path.join(self.workspace_path, file_path)
                if self._is_safe_path(full_path):
                    subprocess.run(
                        ['git', 'add', file_path],
                        cwd=self.workspace_path,
                        check=True
                    )
            
            # Commit
            subprocess.run(
                ['git', 'commit', '-m', message],
                cwd=self.workspace_path,
                check=True
            )
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"Git commit error: {e}")
            return False
    
    def get_file_diff(self, file_path: str) -> Optional[str]:
        """Get git diff for a specific file"""
        try:
            result = subprocess.run(
                ['git', 'diff', 'HEAD', file_path],
                cwd=self.workspace_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            return result.stdout if result.stdout else None
            
        except subprocess.CalledProcessError as e:
            print(f"Git diff error: {e}")
            return None

class EnhancedSwiftGameAgent:
    """Enhanced Swift Game Agent with Goose LLM and Git integration"""
    
    def __init__(self, project_path: str = "./SwiftTamagotchi"):
        self.project_path = project_path
        self.llm = GooseLLMInterface(project_path)
        self.file_manager = FileGitManager(project_path)
        self.analysis_cache = {}
        
    def analyze_with_llm_assistance(self) -> Dict[str, Any]:
        """Perform analysis with LLM assistance"""
        
        # Get current project state
        git_status = self.file_manager.git_status()
        
        # Find all Swift files
        swift_files = []
        for root, dirs, files in os.walk(self.project_path):
            for file in files:
                if file.endswith('.swift'):
                    rel_path = os.path.relpath(os.path.join(root, file), self.project_path)
                    swift_files.append(rel_path)
        
        # Request LLM analysis
        request = GooseLLMRequest(
            prompt=f"""
            Analyze this Swift iOS game project for improvement opportunities.
            
            Current state:
            - Found {len(swift_files)} Swift files
            - Git status: {git_status}
            
            Please provide:
            1. Code quality assessment
            2. Architecture recommendations
            3. Feature suggestions
            4. Performance optimization opportunities
            5. Prioritized implementation plan
            """,
            task_type="analysis",
            files_context=swift_files[:5],  # Limit to first 5 files for context
            context="Swift iOS Tamagotchi game development project"
        )
        
        llm_response = self.llm.query_llm(request)
        
        return {
            'swift_files': swift_files,
            'git_status': git_status,
            'llm_analysis': llm_response,
            'timestamp': datetime.now().isoformat()
        }
    
    def implement_improvement_with_llm(self, improvement_title: str) -> Dict[str, Any]:
        """Implement improvement with LLM code generation assistance"""
        
        request = GooseLLMRequest(
            prompt=f"""
            Generate Swift code implementation for: {improvement_title}
            
            Requirements:
            - Follow iOS best practices
            - Use SwiftUI and modern Swift patterns
            - Include error handling
            - Add appropriate documentation
            - Ensure compatibility with existing codebase
            
            Please provide:
            1. Complete Swift code implementation
            2. Integration instructions
            3. Testing recommendations
            4. Files that need to be modified
            """,
            task_type="code_generation",
            context="Swift iOS Tamagotchi game - focusing on maintainable, modern code"
        )
        
        llm_response = self.llm.query_llm(request)
        
        # Here you would parse the LLM response and actually implement the changes
        # For now, return the structured response
        
        return {
            'improvement': improvement_title,
            'implementation': llm_response,
            'status': 'generated',
            'next_steps': llm_response.next_actions
        }
    
    def review_changes_with_llm(self, files_changed: List[str]) -> Dict[str, Any]:
        """Review changes with LLM assistance"""
        
        # Get diffs for changed files
        diffs = {}
        for file_path in files_changed:
            diff = self.file_manager.get_file_diff(file_path)
            if diff:
                diffs[file_path] = diff
        
        request = GooseLLMRequest(
            prompt=f"""
            Review these code changes for quality, correctness, and best practices:
            
            Files changed: {', '.join(files_changed)}
            
            Please assess:
            1. Code quality and style
            2. Potential bugs or issues
            3. Performance implications
            4. Testing coverage needs
            5. Documentation requirements
            
            Provide specific recommendations for improvement.
            """,
            task_type="code_review",
            context=f"Code diffs: {json.dumps(diffs, indent=2)}"
        )
        
        llm_response = self.llm.query_llm(request)
        
        return {
            'files_reviewed': files_changed,
            'diffs': diffs,
            'review': llm_response,
            'recommendations': llm_response.suggestions
        }
