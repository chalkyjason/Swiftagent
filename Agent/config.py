"""
Configuration for the Autonomous Game Development Agent.

This module contains all configuration settings for the agent including
workspace paths, safety policies, cost limits, and model settings.
"""

import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum


class ModelTier(Enum):
    """Model tiers for cost optimization."""
    HAIKU = "claude-3-haiku-20240307"
    SONNET = "claude-sonnet-4-20250514"
    OPUS = "claude-opus-4-20250514"


@dataclass
class WorkspaceConfig:
    """Configuration for the agent workspace."""
    root_path: Path = field(default_factory=lambda: Path.cwd().parent if Path.cwd().name == "Agent" else Path.cwd())
    packages_dir: str = "Packages"
    apps_dir: str = "Apps"
    checkpoint_dir: str = ".agent_checkpoints"
    trash_dir: str = ".agent_trash"

    def __post_init__(self):
        self.root_path = Path(self.root_path)
        self.packages_path = self.root_path / self.packages_dir
        self.apps_path = self.root_path / self.apps_dir
        self.checkpoint_path = self.root_path / self.checkpoint_dir
        self.trash_path = self.root_path / self.trash_dir


@dataclass
class SafetyConfig:
    """Safety and sandboxing configuration."""
    # Commands that are completely blocked
    blocked_commands: List[str] = field(default_factory=lambda: [
        "sudo", "chmod", "chown", "rm -rf /", "rm -rf ~",
        "mkfs", "dd", "format", "> /dev/", "shutdown", "reboot",
        "kill -9 1", "killall", "pkill -9"
    ])

    # Commands that require path validation
    restricted_commands: List[str] = field(default_factory=lambda: [
        "rm", "mv", "cp"
    ])

    # Allowed commands for full execution
    allowed_commands: List[str] = field(default_factory=lambda: [
        "swift", "xcodebuild", "git", "ls", "cat", "head", "tail",
        "grep", "find", "mkdir", "touch", "echo", "cd", "pwd",
        "xcrun", "simctl", "pod", "carthage", "mint"
    ])

    # Maximum file size the agent can create (in bytes)
    max_file_size: int = 1_000_000  # 1MB

    # Maximum number of files the agent can create per session
    max_files_per_session: int = 100


@dataclass
class CostConfig:
    """Cost management configuration."""
    daily_budget_usd: float = 5.0
    warning_threshold: float = 0.8  # Warn at 80% of budget

    # Token costs (approximate, in USD per 1M tokens)
    input_cost_per_million: float = 3.0
    output_cost_per_million: float = 15.0

    # Use cheaper model for these task types
    haiku_task_types: List[str] = field(default_factory=lambda: [
        "write_tests", "add_comments", "format_code", "simple_refactor"
    ])


@dataclass
class ContextConfig:
    """Context management configuration."""
    max_context_tokens: int = 200_000
    safety_threshold: float = 0.8  # Trigger summarization at 80%
    summarization_ratio: float = 0.5  # Summarize oldest 50%

    # Vector database settings
    vector_db_path: str = ".vector_db"
    embedding_model: str = "all-MiniLM-L6-v2"
    chunk_size: int = 500
    chunk_overlap: int = 50


@dataclass
class AgentConfig:
    """Main agent configuration."""
    workspace: WorkspaceConfig = field(default_factory=WorkspaceConfig)
    safety: SafetyConfig = field(default_factory=SafetyConfig)
    cost: CostConfig = field(default_factory=CostConfig)
    context: ContextConfig = field(default_factory=ContextConfig)

    # Model settings
    default_model: ModelTier = ModelTier.SONNET
    fallback_model: ModelTier = ModelTier.HAIKU

    # Loop settings
    loop_delay_seconds: float = 1.0
    max_retries: int = 3
    retry_backoff_base: float = 2.0

    # Logging
    log_level: str = "INFO"
    log_file: str = "agent.log"

    @classmethod
    def from_env(cls) -> "AgentConfig":
        """Create configuration from environment variables."""
        config = cls()

        if workspace_root := os.environ.get("AGENT_WORKSPACE_ROOT"):
            config.workspace.root_path = Path(workspace_root)
            config.workspace.__post_init__()

        if daily_budget := os.environ.get("AGENT_DAILY_BUDGET"):
            config.cost.daily_budget_usd = float(daily_budget)

        if log_level := os.environ.get("AGENT_LOG_LEVEL"):
            config.log_level = log_level

        return config


# Global configuration instance
_config: Optional[AgentConfig] = None


def get_config() -> AgentConfig:
    """Get the global configuration instance."""
    global _config
    if _config is None:
        _config = AgentConfig.from_env()
    return _config


def set_config(config: AgentConfig) -> None:
    """Set the global configuration instance."""
    global _config
    _config = config
