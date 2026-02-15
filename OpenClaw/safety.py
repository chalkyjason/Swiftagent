"""Safety guardrails for the OpenClaw agent.

Enforces sandboxing, command filtering, and file operation limits.
"""

import logging
import re
import shutil
from datetime import datetime
from pathlib import Path

from .config import OpenClawConfig

logger = logging.getLogger("openclaw.safety")

# Commands that are always blocked
BLOCKED_COMMANDS = frozenset({
    "sudo", "chmod", "chown", "mkfs", "dd", "format",
    "shutdown", "reboot", "systemctl", "launchctl",
})

# Patterns that are always blocked
BLOCKED_PATTERNS = [
    re.compile(r"rm\s+(-rf?|-fr?)\s+(/|~)"),   # rm -rf / or ~
    re.compile(r">\s*/dev/"),                     # write to device files
    re.compile(r"kill\s+-9\s+1\b"),               # kill init
    re.compile(r"killall|pkill\s+-9"),             # mass kill
    re.compile(r"\|\s*(sh|bash|zsh)\b"),           # pipe to shell
    re.compile(r"`[^`]*`"),                        # command substitution via backtick
    re.compile(r"\$\(.*rm.*\)"),                   # command subst with rm
]

# Commands allowed for execution (general-purpose)
ALLOWED_PREFIXES = [
    "git status", "git diff", "git log", "git add", "git commit",
    "git branch", "git checkout", "git stash", "git push", "git pull",
    "ls", "cat", "head", "tail", "grep", "find", "wc",
    "mkdir", "touch", "echo", "cp", "mv",
    "python", "pip", "python3", "pip3",
    "node", "npm", "npx", "yarn", "pnpm",
    "cargo", "rustc",
    "go ", "go build", "go test", "go run",
    "make", "cmake",
    "docker", "docker-compose",
    "curl", "wget",
    "jq", "yq",
    "goose",
    "claude",
    "aider",
    "codex",
    "cline",
]


class SafetyGuard:
    """Validates and enforces safety constraints on agent operations."""

    def __init__(self, config: OpenClawConfig):
        self.config = config
        self.files_created = 0
        self.blocked_count = 0
        self._ensure_dirs()

    def _ensure_dirs(self):
        self.config.trash_dir.mkdir(parents=True, exist_ok=True)
        self.config.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.config.tasks_dir.mkdir(parents=True, exist_ok=True)

    def validate_path(self, path: str | Path) -> bool:
        """Check that a path is within the workspace sandbox."""
        try:
            resolved = Path(path).resolve()
            workspace = self.config.workspace_root.resolve()
            return str(resolved).startswith(str(workspace))
        except (ValueError, OSError):
            return False

    def validate_command(self, command: str) -> tuple[bool, str]:
        """Validate a shell command. Returns (allowed, reason)."""
        cmd_stripped = command.strip()
        first_word = cmd_stripped.split()[0] if cmd_stripped else ""

        if first_word in BLOCKED_COMMANDS:
            self.blocked_count += 1
            reason = f"Blocked command: {first_word}"
            logger.warning(reason)
            return False, reason

        for pattern in BLOCKED_PATTERNS:
            if pattern.search(cmd_stripped):
                self.blocked_count += 1
                reason = f"Blocked pattern: {pattern.pattern}"
                logger.warning(reason)
                return False, reason

        if not any(cmd_stripped.startswith(p) for p in ALLOWED_PREFIXES):
            self.blocked_count += 1
            reason = f"Command not in allowlist: {first_word}"
            logger.warning(reason)
            return False, reason

        return True, "OK"

    def validate_file_write(self, path: str | Path, content: str) -> tuple[bool, str]:
        """Validate a file write operation."""
        if not self.validate_path(path):
            return False, f"Path outside sandbox: {path}"
        size = len(content.encode("utf-8"))
        if size > self.config.max_file_size_bytes:
            return False, f"File too large: {size} bytes (max {self.config.max_file_size_bytes})"
        if self.files_created >= self.config.max_files_per_session:
            return False, f"File creation limit reached: {self.config.max_files_per_session}"
        return True, "OK"

    def record_file_created(self):
        self.files_created += 1

    def safe_delete(self, path: str | Path) -> bool:
        """Move a file to trash instead of deleting permanently."""
        path = Path(path)
        if not self.validate_path(path):
            logger.warning(f"Cannot delete file outside sandbox: {path}")
            return False
        if not path.exists():
            return True
        if self.config.safe_delete:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            trash_path = self.config.trash_dir / f"{path.name}.{ts}"
            shutil.move(str(path), str(trash_path))
            logger.info(f"Moved to trash: {path} -> {trash_path}")
        else:
            path.unlink()
            logger.info(f"Deleted: {path}")
        return True
