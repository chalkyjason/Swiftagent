"""
Safety Wrapper for the Autonomous Game Development Agent.

This module implements sandboxing and safety policies to ensure the agent
operates safely within defined boundaries. It intercepts and validates
all file system operations and shell commands before execution.
"""

import os
import re
import shutil
import logging
from pathlib import Path
from typing import Optional, Tuple, List
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

from config import get_config, SafetyConfig, WorkspaceConfig


logger = logging.getLogger(__name__)


class SafetyViolation(Exception):
    """Raised when a safety policy is violated."""
    pass


class ActionType(Enum):
    """Types of actions the agent can perform."""
    READ_FILE = "read_file"
    WRITE_FILE = "write_file"
    DELETE_FILE = "delete_file"
    EXECUTE_COMMAND = "execute_command"
    CREATE_DIRECTORY = "create_directory"


@dataclass
class SafetyCheckResult:
    """Result of a safety check."""
    allowed: bool
    reason: str
    modified_action: Optional[str] = None


class SafetyWrapper:
    """
    Safety wrapper that validates and sanitizes all agent actions.

    This class enforces:
    - Path sandboxing (agent cannot access files outside workspace)
    - Command filtering (dangerous commands are blocked)
    - Safe deletion (files moved to trash instead of permanent delete)
    - File size limits
    - Operation logging for audit trails
    """

    def __init__(self, workspace_config: Optional[WorkspaceConfig] = None,
                 safety_config: Optional[SafetyConfig] = None):
        config = get_config()
        self.workspace = workspace_config or config.workspace
        self.safety = safety_config or config.safety
        self.files_created_this_session = 0
        self._ensure_directories()

    def _ensure_directories(self) -> None:
        """Ensure required directories exist."""
        self.workspace.root_path.mkdir(parents=True, exist_ok=True)
        self.workspace.checkpoint_path.mkdir(parents=True, exist_ok=True)
        self.workspace.trash_path.mkdir(parents=True, exist_ok=True)

    def _normalize_path(self, path: str) -> Path:
        """Normalize and resolve a path."""
        p = Path(path).expanduser()
        if not p.is_absolute():
            p = self.workspace.root_path / p
        return p.resolve()

    def _is_within_sandbox(self, path: Path) -> bool:
        """Check if a path is within the allowed sandbox."""
        try:
            path.relative_to(self.workspace.root_path)
            return True
        except ValueError:
            return False

    def validate_path(self, path: str, action: ActionType) -> SafetyCheckResult:
        """
        Validate a file path for the given action.

        Args:
            path: The file path to validate
            action: The type of action being performed

        Returns:
            SafetyCheckResult indicating if the action is allowed
        """
        normalized = self._normalize_path(path)

        # Check sandbox boundary
        if not self._is_within_sandbox(normalized):
            return SafetyCheckResult(
                allowed=False,
                reason=f"Path '{path}' is outside the allowed workspace: {self.workspace.root_path}"
            )

        # Check for path traversal attempts
        if ".." in str(path):
            return SafetyCheckResult(
                allowed=False,
                reason=f"Path traversal detected in: {path}"
            )

        # Additional checks for write operations
        if action == ActionType.WRITE_FILE:
            if self.files_created_this_session >= self.safety.max_files_per_session:
                return SafetyCheckResult(
                    allowed=False,
                    reason=f"Maximum file creation limit ({self.safety.max_files_per_session}) reached"
                )

        return SafetyCheckResult(
            allowed=True,
            reason="Path validation passed",
            modified_action=str(normalized)
        )

    def validate_command(self, command: str) -> SafetyCheckResult:
        """
        Validate a shell command for safety.

        Args:
            command: The shell command to validate

        Returns:
            SafetyCheckResult indicating if the command is allowed
        """
        command_lower = command.lower().strip()

        # Check for blocked commands
        for blocked in self.safety.blocked_commands:
            if blocked.lower() in command_lower:
                return SafetyCheckResult(
                    allowed=False,
                    reason=f"Blocked command detected: {blocked}"
                )

        # Check for dangerous patterns
        dangerous_patterns = [
            r">\s*/dev/",  # Writing to device files
            r"\|\s*sh\b",  # Piping to shell
            r"\|\s*bash\b",
            r"`.*`",  # Command substitution that could be dangerous
            r"\$\(.*rm.*\)",  # Command substitution with rm
        ]

        for pattern in dangerous_patterns:
            if re.search(pattern, command):
                return SafetyCheckResult(
                    allowed=False,
                    reason=f"Dangerous command pattern detected: {pattern}"
                )

        # Check restricted commands need path validation
        for restricted in self.safety.restricted_commands:
            if command_lower.startswith(restricted):
                # Extract paths and validate them
                paths = self._extract_paths_from_command(command)
                for path in paths:
                    result = self.validate_path(path, ActionType.DELETE_FILE if restricted == "rm" else ActionType.WRITE_FILE)
                    if not result.allowed:
                        return result

        return SafetyCheckResult(
            allowed=True,
            reason="Command validation passed"
        )

    def _extract_paths_from_command(self, command: str) -> List[str]:
        """Extract file paths from a command string."""
        # Simple path extraction - split by spaces and filter
        parts = command.split()
        paths = []
        skip_next = False

        for part in parts[1:]:  # Skip the command itself
            if skip_next:
                skip_next = False
                continue
            if part.startswith("-"):
                # Skip flags, but check if next arg is a flag value
                if part in ["-o", "-f", "-d", "-t"]:
                    skip_next = True
                continue
            # Assume anything else might be a path
            if part and not part.startswith("-"):
                paths.append(part)

        return paths

    def safe_read(self, path: str) -> Tuple[bool, str]:
        """
        Safely read a file within the sandbox.

        Args:
            path: Path to the file to read

        Returns:
            Tuple of (success, content_or_error)
        """
        result = self.validate_path(path, ActionType.READ_FILE)
        if not result.allowed:
            return False, result.reason

        try:
            normalized = self._normalize_path(path)
            with open(normalized, 'r', encoding='utf-8') as f:
                content = f.read()
            logger.info(f"Successfully read file: {normalized}")
            return True, content
        except Exception as e:
            return False, str(e)

    def safe_write(self, path: str, content: str) -> Tuple[bool, str]:
        """
        Safely write to a file within the sandbox.

        Args:
            path: Path to the file to write
            content: Content to write

        Returns:
            Tuple of (success, message)
        """
        result = self.validate_path(path, ActionType.WRITE_FILE)
        if not result.allowed:
            return False, result.reason

        # Check file size
        if len(content.encode('utf-8')) > self.safety.max_file_size:
            return False, f"Content exceeds maximum file size of {self.safety.max_file_size} bytes"

        try:
            normalized = self._normalize_path(path)
            # Ensure parent directory exists
            normalized.parent.mkdir(parents=True, exist_ok=True)

            with open(normalized, 'w', encoding='utf-8') as f:
                f.write(content)

            self.files_created_this_session += 1
            logger.info(f"Successfully wrote file: {normalized}")
            return True, f"File written: {normalized}"
        except Exception as e:
            return False, str(e)

    def safe_delete(self, path: str) -> Tuple[bool, str]:
        """
        Safely delete a file by moving it to trash.

        Args:
            path: Path to the file to delete

        Returns:
            Tuple of (success, message)
        """
        result = self.validate_path(path, ActionType.DELETE_FILE)
        if not result.allowed:
            return False, result.reason

        try:
            normalized = self._normalize_path(path)
            if not normalized.exists():
                return False, f"File does not exist: {normalized}"

            # Move to trash with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            trash_name = f"{normalized.stem}_{timestamp}{normalized.suffix}"
            trash_path = self.workspace.trash_path / trash_name

            shutil.move(str(normalized), str(trash_path))
            logger.info(f"Moved file to trash: {normalized} -> {trash_path}")
            return True, f"File moved to trash: {trash_path}"
        except Exception as e:
            return False, str(e)

    def safe_execute(self, command: str) -> SafetyCheckResult:
        """
        Validate a command for safe execution.

        This method only validates - actual execution should be done
        by the caller after validation passes.

        Args:
            command: The command to validate

        Returns:
            SafetyCheckResult indicating if execution is allowed
        """
        return self.validate_command(command)

    def reset_session(self) -> None:
        """Reset session-specific counters."""
        self.files_created_this_session = 0
        logger.info("Session counters reset")

    def get_audit_log(self) -> List[str]:
        """Get the audit log for this session."""
        # In a production system, this would return actual logged operations
        return []


class SafetyPolicy:
    """
    High-level safety policy manager.

    Provides a simplified interface for common safety operations
    and policy enforcement.
    """

    def __init__(self):
        self.wrapper = SafetyWrapper()

    def can_access_path(self, path: str) -> bool:
        """Check if a path can be accessed."""
        result = self.wrapper.validate_path(path, ActionType.READ_FILE)
        return result.allowed

    def can_execute_command(self, command: str) -> bool:
        """Check if a command can be executed."""
        result = self.wrapper.validate_command(command)
        return result.allowed

    def sanitize_command(self, command: str) -> Optional[str]:
        """
        Sanitize a command, returning None if it cannot be made safe.

        Args:
            command: The command to sanitize

        Returns:
            Sanitized command or None if not possible
        """
        result = self.wrapper.validate_command(command)
        if result.allowed:
            return command
        return None

    def get_allowed_commands(self) -> List[str]:
        """Get list of allowed command prefixes."""
        return self.wrapper.safety.allowed_commands.copy()
