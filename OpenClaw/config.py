"""OpenClaw agent configuration — general-purpose multi-agent task runner."""

import os
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class OpenClawConfig:
    """Central configuration for the OpenClaw agent."""

    # Workspace
    workspace_root: Path = field(default_factory=lambda: Path(
        os.getenv("OPENCLAW_WORKSPACE",
                   str(Path(__file__).resolve().parent.parent))
    ))

    # LLM provider: "anthropic" or "local" (Ollama / OpenAI-compatible)
    provider: str = os.getenv("OPENCLAW_PROVIDER", "anthropic")
    model: str = os.getenv("OPENCLAW_MODEL", "claude-sonnet-4-5-20250929")
    api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    max_tokens: int = 8192
    temperature: float = 0.0

    # Local LLM settings (used when provider == "local")
    local_api_base: str = os.getenv("OPENCLAW_LOCAL_API_BASE", "http://localhost:11434/v1")
    local_api_key: str = os.getenv("OPENCLAW_LOCAL_API_KEY", "ollama")

    # Budget
    daily_budget: float = float(os.getenv("OPENCLAW_BUDGET", "5.00"))
    cost_per_input_token: float = 3.0 / 1_000_000   # $3/MTok (Sonnet)
    cost_per_output_token: float = 15.0 / 1_000_000  # $15/MTok (Sonnet)

    # Safety
    sandbox_enabled: bool = True
    max_file_size_bytes: int = 1_048_576  # 1 MB
    max_files_per_session: int = 100
    safe_delete: bool = True
    whitelist_only: bool = True

    # Agent behaviour
    max_iterations: int = 20
    max_retries_per_task: int = 3
    loop_delay_seconds: float = 1.0
    dry_run: bool = os.getenv("OPENCLAW_DRY_RUN", "false").lower() == "true"
    log_level: str = os.getenv("OPENCLAW_LOG_LEVEL", "INFO")

    # Multi-agent settings
    goose_enabled: bool = os.getenv("GOOSE_ENABLED", "false").lower() == "true"
    goose_path: str = os.getenv("GOOSE_PATH", "goose")
    claude_cli_enabled: bool = os.getenv("CLAUDE_CLI_ENABLED", "false").lower() == "true"
    claude_cli_path: str = os.getenv("CLAUDE_CLI_PATH", "claude")

    # Paths (derived)
    @property
    def backlog_path(self) -> Path:
        return self.workspace_root / "BACKLOG.md"

    @property
    def log_path(self) -> Path:
        return self.workspace_root / "openclaw.log"

    @property
    def checkpoint_dir(self) -> Path:
        return self.workspace_root / ".openclaw_checkpoints"

    @property
    def trash_dir(self) -> Path:
        return self.workspace_root / ".openclaw_trash"

    @property
    def tasks_dir(self) -> Path:
        return self.workspace_root / ".openclaw_tasks"

    @property
    def status_path(self) -> Path:
        return self.workspace_root / "openclaw_status.json"

    @property
    def skills_path(self) -> Path:
        return self.workspace_root / "openclaw_skills.json"

    def validate(self) -> list[str]:
        """Return list of config errors, empty if valid."""
        errors = []
        if self.provider == "anthropic" and not self.api_key:
            errors.append("ANTHROPIC_API_KEY is not set")
        if self.provider == "local" and not self.local_api_base:
            errors.append("OPENCLAW_LOCAL_API_BASE is not set")
        if self.provider not in ("anthropic", "local"):
            errors.append(f"Unknown provider: {self.provider} (use 'anthropic' or 'local')")
        if not self.workspace_root.exists():
            errors.append(f"Workspace root does not exist: {self.workspace_root}")
        if self.daily_budget <= 0:
            errors.append("Daily budget must be positive")
        return errors
