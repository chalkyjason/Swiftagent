"""
Checkpoint Manager for the Autonomous Game Development Agent.

This module handles persistence and state recovery, enabling the agent
to resume work after interruptions (crashes, reboots, API failures).
"""

import json
import pickle
import hashlib
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict, field
from enum import Enum

from config import get_config


logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """Status of a task in the backlog."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


@dataclass
class TaskCheckpoint:
    """Checkpoint data for a single task."""
    task_id: str
    description: str
    status: TaskStatus
    priority: int = 0
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    error_message: Optional[str] = None
    attempts: int = 0
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConversationCheckpoint:
    """Checkpoint for conversation history with the LLM."""
    messages: List[Dict[str, str]]
    summary: Optional[str] = None
    token_count: int = 0


@dataclass
class AgentCheckpoint:
    """Complete checkpoint of agent state."""
    checkpoint_id: str
    created_at: str
    current_task: Optional[str]
    task_queue: List[TaskCheckpoint]
    conversation: ConversationCheckpoint
    workspace_state: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)


class CheckpointManager:
    """
    Manages agent state persistence and recovery.

    This class provides:
    - Automatic state saving after each successful action
    - Recovery from crashes/interruptions
    - Multiple checkpoint slots for rollback
    - Conversation history compression
    """

    def __init__(self, checkpoint_dir: Optional[Path] = None, max_checkpoints: int = 10):
        config = get_config()
        self.checkpoint_dir = checkpoint_dir or config.workspace.checkpoint_path
        self.max_checkpoints = max_checkpoints
        self.current_checkpoint: Optional[AgentCheckpoint] = None
        self._ensure_directory()

    def _ensure_directory(self) -> None:
        """Ensure checkpoint directory exists."""
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)

    def _generate_checkpoint_id(self) -> str:
        """Generate a unique checkpoint ID."""
        timestamp = datetime.now().isoformat()
        hash_input = f"{timestamp}-{id(self)}"
        return hashlib.sha256(hash_input.encode()).hexdigest()[:16]

    def _get_checkpoint_path(self, checkpoint_id: str) -> Path:
        """Get the file path for a checkpoint."""
        return self.checkpoint_dir / f"checkpoint_{checkpoint_id}.json"

    def _get_latest_checkpoint_path(self) -> Path:
        """Get the path to the latest checkpoint pointer."""
        return self.checkpoint_dir / "latest.txt"

    def _cleanup_old_checkpoints(self) -> None:
        """Remove old checkpoints beyond the max limit."""
        checkpoints = sorted(
            self.checkpoint_dir.glob("checkpoint_*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )

        for old_checkpoint in checkpoints[self.max_checkpoints:]:
            try:
                old_checkpoint.unlink()
                logger.info(f"Removed old checkpoint: {old_checkpoint}")
            except Exception as e:
                logger.warning(f"Failed to remove checkpoint {old_checkpoint}: {e}")

    def save(self, checkpoint: AgentCheckpoint) -> str:
        """
        Save an agent checkpoint.

        Args:
            checkpoint: The checkpoint to save

        Returns:
            The checkpoint ID
        """
        checkpoint_path = self._get_checkpoint_path(checkpoint.checkpoint_id)

        # Convert to serializable format
        data = self._serialize_checkpoint(checkpoint)

        try:
            with open(checkpoint_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)

            # Update latest pointer
            with open(self._get_latest_checkpoint_path(), 'w') as f:
                f.write(checkpoint.checkpoint_id)

            self.current_checkpoint = checkpoint
            self._cleanup_old_checkpoints()

            logger.info(f"Saved checkpoint: {checkpoint.checkpoint_id}")
            return checkpoint.checkpoint_id

        except Exception as e:
            logger.error(f"Failed to save checkpoint: {e}")
            raise

    def load(self, checkpoint_id: Optional[str] = None) -> Optional[AgentCheckpoint]:
        """
        Load a checkpoint.

        Args:
            checkpoint_id: Specific checkpoint to load, or None for latest

        Returns:
            The loaded checkpoint, or None if not found
        """
        if checkpoint_id is None:
            checkpoint_id = self._get_latest_checkpoint_id()
            if checkpoint_id is None:
                return None

        checkpoint_path = self._get_checkpoint_path(checkpoint_id)

        if not checkpoint_path.exists():
            logger.warning(f"Checkpoint not found: {checkpoint_id}")
            return None

        try:
            with open(checkpoint_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            checkpoint = self._deserialize_checkpoint(data)
            self.current_checkpoint = checkpoint

            logger.info(f"Loaded checkpoint: {checkpoint_id}")
            return checkpoint

        except Exception as e:
            logger.error(f"Failed to load checkpoint: {e}")
            return None

    def _get_latest_checkpoint_id(self) -> Optional[str]:
        """Get the ID of the latest checkpoint."""
        latest_path = self._get_latest_checkpoint_path()
        if latest_path.exists():
            return latest_path.read_text().strip()
        return None

    def _serialize_checkpoint(self, checkpoint: AgentCheckpoint) -> Dict[str, Any]:
        """Convert checkpoint to serializable dictionary."""
        data = {
            "checkpoint_id": checkpoint.checkpoint_id,
            "created_at": checkpoint.created_at,
            "current_task": checkpoint.current_task,
            "task_queue": [
                {
                    "task_id": t.task_id,
                    "description": t.description,
                    "status": t.status.value,
                    "priority": t.priority,
                    "started_at": t.started_at,
                    "completed_at": t.completed_at,
                    "error_message": t.error_message,
                    "attempts": t.attempts,
                    "context": t.context
                }
                for t in checkpoint.task_queue
            ],
            "conversation": {
                "messages": checkpoint.conversation.messages,
                "summary": checkpoint.conversation.summary,
                "token_count": checkpoint.conversation.token_count
            },
            "workspace_state": checkpoint.workspace_state,
            "metadata": checkpoint.metadata
        }
        return data

    def _deserialize_checkpoint(self, data: Dict[str, Any]) -> AgentCheckpoint:
        """Convert dictionary back to checkpoint object."""
        task_queue = [
            TaskCheckpoint(
                task_id=t["task_id"],
                description=t["description"],
                status=TaskStatus(t["status"]),
                priority=t.get("priority", 0),
                started_at=t.get("started_at"),
                completed_at=t.get("completed_at"),
                error_message=t.get("error_message"),
                attempts=t.get("attempts", 0),
                context=t.get("context", {})
            )
            for t in data.get("task_queue", [])
        ]

        conversation = ConversationCheckpoint(
            messages=data.get("conversation", {}).get("messages", []),
            summary=data.get("conversation", {}).get("summary"),
            token_count=data.get("conversation", {}).get("token_count", 0)
        )

        return AgentCheckpoint(
            checkpoint_id=data["checkpoint_id"],
            created_at=data["created_at"],
            current_task=data.get("current_task"),
            task_queue=task_queue,
            conversation=conversation,
            workspace_state=data.get("workspace_state", {}),
            metadata=data.get("metadata", {})
        )

    def create_checkpoint(
        self,
        current_task: Optional[str],
        task_queue: List[TaskCheckpoint],
        messages: List[Dict[str, str]],
        workspace_state: Optional[Dict[str, Any]] = None,
        summary: Optional[str] = None
    ) -> AgentCheckpoint:
        """
        Create a new checkpoint from current state.

        Args:
            current_task: ID of the task being worked on
            task_queue: List of all tasks
            messages: Conversation history
            workspace_state: Additional workspace state
            summary: Summary of older conversation

        Returns:
            The created checkpoint
        """
        checkpoint = AgentCheckpoint(
            checkpoint_id=self._generate_checkpoint_id(),
            created_at=datetime.now().isoformat(),
            current_task=current_task,
            task_queue=task_queue,
            conversation=ConversationCheckpoint(
                messages=messages,
                summary=summary,
                token_count=self._estimate_tokens(messages)
            ),
            workspace_state=workspace_state or {},
            metadata={"version": "1.0"}
        )

        return checkpoint

    def _estimate_tokens(self, messages: List[Dict[str, str]]) -> int:
        """Estimate token count for messages."""
        # Rough estimation: ~4 characters per token
        total_chars = sum(len(m.get("content", "")) for m in messages)
        return total_chars // 4

    def list_checkpoints(self) -> List[Dict[str, Any]]:
        """List all available checkpoints."""
        checkpoints = []
        for cp_file in self.checkpoint_dir.glob("checkpoint_*.json"):
            try:
                with open(cp_file, 'r') as f:
                    data = json.load(f)
                checkpoints.append({
                    "checkpoint_id": data["checkpoint_id"],
                    "created_at": data["created_at"],
                    "current_task": data.get("current_task"),
                    "task_count": len(data.get("task_queue", []))
                })
            except Exception as e:
                logger.warning(f"Could not read checkpoint {cp_file}: {e}")

        return sorted(checkpoints, key=lambda x: x["created_at"], reverse=True)

    def delete_checkpoint(self, checkpoint_id: str) -> bool:
        """Delete a specific checkpoint."""
        checkpoint_path = self._get_checkpoint_path(checkpoint_id)
        if checkpoint_path.exists():
            checkpoint_path.unlink()
            logger.info(f"Deleted checkpoint: {checkpoint_id}")
            return True
        return False


class BacklogManager:
    """
    Manages the task backlog file (BACKLOG.md).

    Parses and updates the markdown-based task list that
    drives the agent's work queue.
    """

    def __init__(self, backlog_path: Optional[Path] = None):
        config = get_config()
        self.backlog_path = backlog_path or (config.workspace.root_path / "BACKLOG.md")

    def parse_backlog(self) -> List[TaskCheckpoint]:
        """Parse the BACKLOG.md file into tasks."""
        if not self.backlog_path.exists():
            return []

        tasks = []
        content = self.backlog_path.read_text()

        for line in content.split('\n'):
            line = line.strip()
            if not line:
                continue

            # Parse checkbox format: - [ ] task or - [x] task
            if line.startswith('- [ ]') or line.startswith('- [x]'):
                is_completed = line.startswith('- [x]')
                description = line[5:].strip()

                # Check for priority marker [P1], [P2], etc.
                priority = 0
                if description.startswith('[P'):
                    try:
                        priority_end = description.index(']')
                        priority = int(description[2:priority_end])
                        description = description[priority_end + 1:].strip()
                    except (ValueError, IndexError):
                        pass

                task_id = hashlib.md5(description.encode()).hexdigest()[:8]
                tasks.append(TaskCheckpoint(
                    task_id=task_id,
                    description=description,
                    status=TaskStatus.COMPLETED if is_completed else TaskStatus.PENDING,
                    priority=priority
                ))

        # Sort by priority (higher first) then by order in file
        tasks.sort(key=lambda t: (-t.priority, tasks.index(t)))
        return tasks

    def update_backlog(self, tasks: List[TaskCheckpoint]) -> None:
        """Update the BACKLOG.md file with current task states."""
        lines = ["# Agent Backlog\n", "\n"]

        # Group by status
        pending = [t for t in tasks if t.status == TaskStatus.PENDING]
        in_progress = [t for t in tasks if t.status == TaskStatus.IN_PROGRESS]
        completed = [t for t in tasks if t.status == TaskStatus.COMPLETED]
        failed = [t for t in tasks if t.status in (TaskStatus.FAILED, TaskStatus.BLOCKED)]

        if in_progress:
            lines.append("## In Progress\n")
            for task in in_progress:
                priority = f"[P{task.priority}] " if task.priority > 0 else ""
                lines.append(f"- [ ] {priority}{task.description}\n")
            lines.append("\n")

        if pending:
            lines.append("## Pending\n")
            for task in pending:
                priority = f"[P{task.priority}] " if task.priority > 0 else ""
                lines.append(f"- [ ] {priority}{task.description}\n")
            lines.append("\n")

        if failed:
            lines.append("## Blocked/Failed\n")
            for task in failed:
                error = f" (Error: {task.error_message})" if task.error_message else ""
                lines.append(f"- [ ] {task.description}{error}\n")
            lines.append("\n")

        if completed:
            lines.append("## Completed\n")
            for task in completed:
                lines.append(f"- [x] {task.description}\n")
            lines.append("\n")

        self.backlog_path.write_text("".join(lines))
        logger.info(f"Updated backlog: {len(pending)} pending, {len(completed)} completed")

    def add_task(self, description: str, priority: int = 0) -> TaskCheckpoint:
        """Add a new task to the backlog."""
        tasks = self.parse_backlog()
        task_id = hashlib.md5(description.encode()).hexdigest()[:8]

        new_task = TaskCheckpoint(
            task_id=task_id,
            description=description,
            status=TaskStatus.PENDING,
            priority=priority
        )

        tasks.append(new_task)
        self.update_backlog(tasks)
        return new_task

    def mark_task_complete(self, task_id: str) -> bool:
        """Mark a task as completed."""
        tasks = self.parse_backlog()
        for task in tasks:
            if task.task_id == task_id:
                task.status = TaskStatus.COMPLETED
                task.completed_at = datetime.now().isoformat()
                self.update_backlog(tasks)
                return True
        return False

    def get_next_task(self) -> Optional[TaskCheckpoint]:
        """Get the next pending task to work on."""
        tasks = self.parse_backlog()
        pending = [t for t in tasks if t.status == TaskStatus.PENDING]
        if pending:
            return pending[0]  # Already sorted by priority
        return None
