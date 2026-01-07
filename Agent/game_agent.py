#!/usr/bin/env python3
"""
Autonomous Game Development Agent

This is the main entry point for the continuous game development agent.
It implements the OODA loop (Observe, Orient, Decide, Act) for autonomous
software engineering of iOS game components.

Usage:
    python game_agent.py [--config CONFIG_PATH] [--resume] [--single-task]
"""

import os
import sys
import time
import signal
import asyncio
import logging
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from enum import Enum

from config import get_config, AgentConfig, ModelTier
from safety_wrapper import SafetyWrapper, SafetyPolicy
from checkpoint_manager import (
    CheckpointManager, BacklogManager, TaskCheckpoint,
    TaskStatus, AgentCheckpoint
)
from context_manager import ContextManager, TokenCounter


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('agent.log')
    ]
)
logger = logging.getLogger(__name__)


class AgentState(Enum):
    """Current state of the agent."""
    INITIALIZING = "initializing"
    IDLE = "idle"
    WORKING = "working"
    VERIFYING = "verifying"
    COMMITTING = "committing"
    ERROR_RECOVERY = "error_recovery"
    PAUSED = "paused"
    SHUTDOWN = "shutdown"


@dataclass
class CostTracker:
    """Tracks API usage costs."""
    daily_input_tokens: int = 0
    daily_output_tokens: int = 0
    last_reset: datetime = None

    def __post_init__(self):
        if self.last_reset is None:
            self.last_reset = datetime.now()

    def add_usage(self, input_tokens: int, output_tokens: int) -> None:
        """Record token usage."""
        # Reset if new day
        if datetime.now().date() > self.last_reset.date():
            self.daily_input_tokens = 0
            self.daily_output_tokens = 0
            self.last_reset = datetime.now()

        self.daily_input_tokens += input_tokens
        self.daily_output_tokens += output_tokens

    def get_daily_cost(self, config: AgentConfig) -> float:
        """Calculate daily cost in USD."""
        input_cost = (self.daily_input_tokens / 1_000_000) * config.cost.input_cost_per_million
        output_cost = (self.daily_output_tokens / 1_000_000) * config.cost.output_cost_per_million
        return input_cost + output_cost

    def is_over_budget(self, config: AgentConfig) -> bool:
        """Check if daily budget exceeded."""
        return self.get_daily_cost(config) >= config.cost.daily_budget_usd


class GameDevelopmentAgent:
    """
    The main autonomous game development agent.

    This agent continuously processes tasks from the backlog,
    implementing Swift packages for iOS game development.
    """

    def __init__(self, config: Optional[AgentConfig] = None):
        self.config = config or get_config()
        self.state = AgentState.INITIALIZING
        self.safety = SafetyWrapper()
        self.safety_policy = SafetyPolicy()
        self.checkpoint_mgr = CheckpointManager()
        self.backlog_mgr = BacklogManager()
        self.context_mgr = ContextManager()
        self.cost_tracker = CostTracker()

        self.current_task: Optional[TaskCheckpoint] = None
        self._shutdown_requested = False
        self._setup_signal_handlers()

        # System prompt for the LLM
        self.system_prompt = self._build_system_prompt()
        self.context_mgr.set_system_prompt(self.system_prompt)

    def _setup_signal_handlers(self) -> None:
        """Setup graceful shutdown handlers."""
        signal.signal(signal.SIGINT, self._handle_shutdown)
        signal.signal(signal.SIGTERM, self._handle_shutdown)

    def _handle_shutdown(self, signum, frame) -> None:
        """Handle shutdown signals gracefully."""
        logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        self._shutdown_requested = True
        self.state = AgentState.SHUTDOWN

    def _build_system_prompt(self) -> str:
        """Build the system prompt for the LLM."""
        return """You are an expert iOS game development architect. Your role is to build
reusable Swift packages for game development using Swift Package Manager (SPM).

## Core Principles
1. **Modularity First**: Never write code in the App target if it can be a reusable Package.
2. **Protocol-Oriented**: Prefer Protocols and Value Types (Structs) over Class inheritance.
3. **Safety Critical**: Always verify your changes by running `swift test`.
4. **Documentation**: Write clear documentation for every public API.

## Architecture Guidelines
- Use the Coordinator pattern for navigation
- Implement data-driven UI components
- Follow MVVM architecture for SwiftUI views
- Use dependency injection for testability

## Package Structure
Each package should have:
- A clear public API exposed through exports
- Unit tests for all public functionality
- A README.md explaining usage
- Example code demonstrating integration

## Code Style
- Use Swift 5.9+ features appropriately
- Follow Apple's Swift API Design Guidelines
- Use async/await for asynchronous operations
- Leverage SwiftUI and Combine where appropriate

## Testing Requirements
- Write tests before or alongside implementation
- Ensure all public APIs have test coverage
- Use XCTest framework
- Mock external dependencies

When you complete a task:
1. Run `swift build` to verify compilation
2. Run `swift test` to verify tests pass
3. Update the BACKLOG.md to mark the task complete
4. Commit changes with a descriptive message

If you encounter errors, analyze them carefully and fix them before proceeding."""

    async def initialize(self) -> None:
        """Initialize the agent, potentially resuming from checkpoint."""
        logger.info("Initializing Game Development Agent...")

        # Try to load existing checkpoint
        checkpoint = self.checkpoint_mgr.load()
        if checkpoint:
            logger.info(f"Resuming from checkpoint: {checkpoint.checkpoint_id}")
            self._restore_from_checkpoint(checkpoint)
        else:
            logger.info("Starting fresh session")

        # Ensure workspace directories exist
        self._ensure_workspace()

        # Index existing code for RAG
        await self._index_codebase()

        self.state = AgentState.IDLE
        logger.info("Agent initialization complete")

    def _restore_from_checkpoint(self, checkpoint: AgentCheckpoint) -> None:
        """Restore agent state from checkpoint."""
        # Restore task state
        if checkpoint.current_task:
            tasks = self.backlog_mgr.parse_backlog()
            for task in tasks:
                if task.task_id == checkpoint.current_task:
                    self.current_task = task
                    break

        # Restore context
        self.context_mgr.restore_state({
            "messages": [{"role": m["role"], "content": m["content"]}
                         for m in checkpoint.conversation.messages],
            "summary": checkpoint.conversation.summary
        })

    def _ensure_workspace(self) -> None:
        """Ensure all workspace directories exist."""
        workspace = self.config.workspace
        workspace.root_path.mkdir(parents=True, exist_ok=True)
        workspace.packages_path.mkdir(parents=True, exist_ok=True)
        workspace.apps_path.mkdir(parents=True, exist_ok=True)
        workspace.checkpoint_path.mkdir(parents=True, exist_ok=True)
        workspace.trash_path.mkdir(parents=True, exist_ok=True)

    async def _index_codebase(self) -> None:
        """Index the codebase for RAG."""
        logger.info("Indexing codebase for retrieval...")
        packages_path = self.config.workspace.packages_path

        for swift_file in packages_path.rglob("*.swift"):
            self.context_mgr.vector_store.index_swift_file(swift_file)

        logger.info("Codebase indexing complete")

    async def run(self) -> None:
        """Main agent loop."""
        await self.initialize()

        logger.info("Starting main agent loop...")

        while not self._shutdown_requested:
            try:
                # Check budget
                if self.cost_tracker.is_over_budget(self.config):
                    logger.warning("Daily budget exceeded, pausing until tomorrow")
                    self.state = AgentState.PAUSED
                    await self._wait_until_budget_reset()
                    continue

                # Execute one iteration of the OODA loop
                await self._ooda_iteration()

                # Save checkpoint after successful iteration
                await self._save_checkpoint()

                # Brief pause between iterations
                await asyncio.sleep(self.config.loop_delay_seconds)

            except Exception as e:
                logger.error(f"Error in main loop: {e}", exc_info=True)
                self.state = AgentState.ERROR_RECOVERY
                await self._handle_error(e)

        logger.info("Agent shutdown complete")

    async def _ooda_iteration(self) -> None:
        """Execute one iteration of the OODA loop."""
        # Phase 1: OBSERVE - Get the next task
        self.state = AgentState.IDLE
        task = await self._observe()

        if task is None:
            logger.info("No pending tasks, waiting...")
            await asyncio.sleep(10)
            return

        # Phase 2: ORIENT - Gather context
        self.current_task = task
        self.state = AgentState.WORKING
        context = await self._orient(task)

        # Phase 3: DECIDE - Plan the approach
        plan = await self._decide(task, context)

        # Phase 4: ACT - Execute the plan
        success = await self._act(task, plan)

        # Phase 5: VERIFY - Check the work
        self.state = AgentState.VERIFYING
        verified = await self._verify(task)

        # Phase 6: COMMIT - Save and record
        if verified:
            self.state = AgentState.COMMITTING
            await self._commit(task)
        else:
            # Self-correction loop
            await self._self_correct(task)

    async def _observe(self) -> Optional[TaskCheckpoint]:
        """Observe phase: Get the next task from backlog."""
        task = self.backlog_mgr.get_next_task()
        if task:
            logger.info(f"Next task: {task.description}")
            task.status = TaskStatus.IN_PROGRESS
            task.started_at = datetime.now().isoformat()
            task.attempts += 1
        return task

    async def _orient(self, task: TaskCheckpoint) -> Dict[str, Any]:
        """Orient phase: Gather context for the task."""
        context = {
            "task": task.description,
            "relevant_code": "",
            "dependencies": [],
            "existing_patterns": []
        }

        # Query vector store for relevant code
        relevant = self.context_mgr.get_relevant_context(task.description)
        context["relevant_code"] = relevant

        # Check Package.swift files for dependencies
        packages_path = self.config.workspace.packages_path
        for package_dir in packages_path.iterdir():
            if package_dir.is_dir():
                manifest = package_dir / "Package.swift"
                if manifest.exists():
                    context["dependencies"].append(package_dir.name)

        return context

    async def _decide(self, task: TaskCheckpoint, context: Dict[str, Any]) -> str:
        """Decide phase: Plan the approach."""
        # Build a prompt for planning
        planning_prompt = f"""
Task: {task.description}

Existing packages: {', '.join(context['dependencies']) if context['dependencies'] else 'None'}

Relevant code context:
{context['relevant_code'][:2000] if context['relevant_code'] else 'No existing code found.'}

Please create a detailed implementation plan for this task. Include:
1. Which package this belongs to (new or existing)
2. The public API design
3. Key implementation details
4. Test cases to write
"""
        # In production, this would call the LLM API
        # For now, return a placeholder plan
        return f"Plan for: {task.description}"

    async def _act(self, task: TaskCheckpoint, plan: str) -> bool:
        """Act phase: Execute the implementation."""
        logger.info(f"Executing task: {task.description}")

        # This is where the actual LLM interaction and code generation happens
        # In production, this would:
        # 1. Call the Claude API with the plan
        # 2. Parse the response for file operations
        # 3. Execute file writes through the safety wrapper
        # 4. Run builds and tests

        # Placeholder implementation
        try:
            # Simulate work
            await asyncio.sleep(1)
            return True
        except Exception as e:
            logger.error(f"Error during act phase: {e}")
            return False

    async def _verify(self, task: TaskCheckpoint) -> bool:
        """Verify phase: Check the work."""
        logger.info(f"Verifying task: {task.description}")

        # Run swift build
        build_result = await self._run_swift_command("build")
        if not build_result:
            logger.warning("Build failed")
            return False

        # Run swift test
        test_result = await self._run_swift_command("test")
        if not test_result:
            logger.warning("Tests failed")
            return False

        return True

    async def _run_swift_command(self, command: str) -> bool:
        """Run a swift command safely."""
        full_command = f"swift {command}"

        # Validate command
        result = self.safety_policy.can_execute_command(full_command)
        if not result:
            logger.warning(f"Command blocked by safety policy: {full_command}")
            return False

        # In production, this would actually execute the command
        # using subprocess with proper error handling
        return True

    async def _commit(self, task: TaskCheckpoint) -> None:
        """Commit phase: Save and record the completed work."""
        logger.info(f"Committing task: {task.description}")

        # Mark task as complete
        task.status = TaskStatus.COMPLETED
        task.completed_at = datetime.now().isoformat()

        # Update backlog
        tasks = self.backlog_mgr.parse_backlog()
        for i, t in enumerate(tasks):
            if t.task_id == task.task_id:
                tasks[i] = task
                break
        self.backlog_mgr.update_backlog(tasks)

        # Git commit (if git is available)
        await self._git_commit(f"Complete: {task.description}")

        self.current_task = None

    async def _git_commit(self, message: str) -> bool:
        """Create a git commit with the given message."""
        # In production, this would execute git commands
        logger.info(f"Git commit: {message}")
        return True

    async def _self_correct(self, task: TaskCheckpoint) -> None:
        """Self-correction loop for failed verification."""
        logger.info(f"Entering self-correction for: {task.description}")

        max_correction_attempts = 3
        for attempt in range(max_correction_attempts):
            logger.info(f"Correction attempt {attempt + 1}/{max_correction_attempts}")

            # Re-run the act phase with error context
            # In production, this would include the error messages in the prompt

            # Try verification again
            if await self._verify(task):
                logger.info("Self-correction successful")
                await self._commit(task)
                return

        # Mark as failed if all attempts exhausted
        logger.warning(f"Task failed after {max_correction_attempts} correction attempts")
        task.status = TaskStatus.FAILED
        task.error_message = "Failed verification after multiple attempts"

        # Update backlog
        tasks = self.backlog_mgr.parse_backlog()
        for i, t in enumerate(tasks):
            if t.task_id == task.task_id:
                tasks[i] = task
                break
        self.backlog_mgr.update_backlog(tasks)

    async def _save_checkpoint(self) -> None:
        """Save current state to checkpoint."""
        tasks = self.backlog_mgr.parse_backlog()

        checkpoint = self.checkpoint_mgr.create_checkpoint(
            current_task=self.current_task.task_id if self.current_task else None,
            task_queue=tasks,
            messages=self.context_mgr.get_context_for_api(),
            workspace_state={
                "state": self.state.value,
                "cost": {
                    "daily_input": self.cost_tracker.daily_input_tokens,
                    "daily_output": self.cost_tracker.daily_output_tokens
                }
            },
            summary=self.context_mgr.summary
        )

        self.checkpoint_mgr.save(checkpoint)

    async def _handle_error(self, error: Exception) -> None:
        """Handle errors in the main loop."""
        logger.error(f"Handling error: {error}")

        # Save checkpoint before potential crash
        try:
            await self._save_checkpoint()
        except:
            pass

        # Exponential backoff retry
        retry_delay = self.config.retry_backoff_base
        for attempt in range(self.config.max_retries):
            logger.info(f"Retry attempt {attempt + 1}/{self.config.max_retries} after {retry_delay}s")
            await asyncio.sleep(retry_delay)
            retry_delay *= 2

            try:
                # Try to recover
                self.state = AgentState.IDLE
                return
            except Exception as e:
                logger.error(f"Recovery attempt failed: {e}")

        logger.critical("Max retries exceeded, entering shutdown")
        self._shutdown_requested = True

    async def _wait_until_budget_reset(self) -> None:
        """Wait until the daily budget resets."""
        now = datetime.now()
        tomorrow = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        wait_seconds = (tomorrow - now).total_seconds()
        logger.info(f"Waiting {wait_seconds:.0f} seconds until budget reset")
        await asyncio.sleep(wait_seconds)
        self.cost_tracker.last_reset = datetime.now()


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Autonomous Game Development Agent")
    parser.add_argument("--config", help="Path to config file")
    parser.add_argument("--resume", action="store_true", help="Resume from checkpoint")
    parser.add_argument("--single-task", action="store_true", help="Run only one task")
    args = parser.parse_args()

    agent = GameDevelopmentAgent()

    if args.single_task:
        await agent.initialize()
        await agent._ooda_iteration()
    else:
        await agent.run()


if __name__ == "__main__":
    asyncio.run(main())
