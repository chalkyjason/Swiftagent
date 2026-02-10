"""OpenClaw Agent — autonomous improvement agent for Swiftagent.

Connects to the Claude API, uses skills (tools) to read/write/build code,
and iterates through tasks from BACKLOG.md or a scan of the repo.
"""

import json
import logging
import signal
import sys
import time
from datetime import datetime, date
from pathlib import Path

import anthropic

from .config import OpenClawConfig
from .prompts import SYSTEM_PROMPT, SCAN_PROMPT
from .safety import SafetyGuard
from .skills import get_skill_schemas
from .skills.executor import SkillExecutor

logger = logging.getLogger("openclaw.agent")


class CostTracker:
    """Tracks API costs against a daily budget."""

    def __init__(self, daily_budget: float, config: OpenClawConfig):
        self.daily_budget = daily_budget
        self.config = config
        self.today = date.today()
        self.input_tokens = 0
        self.output_tokens = 0

    @property
    def cost_today(self) -> float:
        if date.today() != self.today:
            self.today = date.today()
            self.input_tokens = 0
            self.output_tokens = 0
        return (
            self.input_tokens * self.config.cost_per_input_token +
            self.output_tokens * self.config.cost_per_output_token
        )

    @property
    def budget_remaining(self) -> float:
        return max(0, self.daily_budget - self.cost_today)

    @property
    def over_budget(self) -> bool:
        return self.cost_today >= self.daily_budget

    def record_usage(self, input_tokens: int, output_tokens: int):
        self.input_tokens += input_tokens
        self.output_tokens += output_tokens
        logger.info(
            f"Cost: ${self.cost_today:.4f} / ${self.daily_budget:.2f} "
            f"({self.input_tokens + self.output_tokens:,} tokens)"
        )

    def to_dict(self) -> dict:
        return {
            "cost_today": round(self.cost_today, 4),
            "daily_budget": self.daily_budget,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "total_tokens": self.input_tokens + self.output_tokens,
        }


class OpenClawAgent:
    """Main agent that runs improvement tasks against the repository."""

    def __init__(self, config: OpenClawConfig | None = None):
        self.config = config or OpenClawConfig()
        self.safety = SafetyGuard(self.config)
        self.executor = SkillExecutor(self.config, self.safety)
        self.cost = CostTracker(self.config.daily_budget, self.config)
        self.client: anthropic.Anthropic | None = None
        self.conversation: list[dict] = []
        self.iteration = 0
        self._shutdown = False

        signal.signal(signal.SIGINT, self._handle_signal)
        signal.signal(signal.SIGTERM, self._handle_signal)

    def _handle_signal(self, signum, frame):
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        self._shutdown = True

    # ── Initialization ───────────────────────────────────────────

    def _write_status(self, current_task: str = "", phase: str = "idle"):
        """Write status.json for the MAUI UI to read."""
        status = {
            "connection_state": "connected",
            "agent_name": "Swiftagent-Claw",
            "model": self.config.model,
            "version": "1.0.0",
            "phase": phase,
            "current_task": current_task,
            "iteration": self.iteration,
            "max_iterations": self.config.max_iterations,
            "dry_run": self.config.dry_run,
            "safety_scanner": self.config.sandbox_enabled,
            "files_created": self.safety.files_created,
            "blocked_count": self.safety.blocked_count,
            "cost": self.cost.to_dict(),
            "skills": [s["name"] for s in get_skill_schemas()],
            "active_skills_count": len(get_skill_schemas()),
            "total_skills_count": len(get_skill_schemas()),
            "timestamp": datetime.now().isoformat(),
        }
        status_path = self.config.workspace_root / "openclaw_status.json"
        status_path.write_text(json.dumps(status, indent=2))

    def initialize(self):
        """Set up the agent: validate config, init API client."""
        _setup_logging(self.config)
        logger.info("OpenClaw agent initializing...")

        errors = self.config.validate()
        if errors:
            for e in errors:
                logger.error(f"Config error: {e}")
            sys.exit(1)

        self.client = anthropic.Anthropic(api_key=self.config.api_key)
        logger.info(f"Model: {self.config.model}")
        logger.info(f"Workspace: {self.config.workspace_root}")
        logger.info(f"Budget: ${self.config.daily_budget:.2f}/day")
        logger.info(f"Dry run: {self.config.dry_run}")
        logger.info("Initialization complete.")

        # Write skills.json so the MAUI UI can discover available skills
        skills_path = self.config.workspace_root / "openclaw_skills.json"
        skills_path.write_text(json.dumps(get_skill_schemas(), indent=2))

        self._write_status(phase="initialized")

    # ── Main loop ────────────────────────────────────────────────

    def run(self, task: str | None = None, scan_only: bool = False):
        """Run the agent loop.

        Args:
            task: If provided, run only this single task then stop.
            scan_only: If True, scan for improvements but don't modify code.
        """
        self.initialize()

        if scan_only:
            self._run_scan()
            return

        if task:
            logger.info(f"Running single task: {task}")
            self._run_task(task)
            return

        # Continuous improvement loop
        logger.info("Starting continuous improvement loop...")
        while not self._shutdown and self.iteration < self.config.max_iterations:
            if self.cost.over_budget:
                logger.warning(
                    f"Daily budget exhausted (${self.cost.cost_today:.2f}). "
                    "Stopping until tomorrow."
                )
                break

            self.iteration += 1
            logger.info(f"\n{'='*60}")
            logger.info(f"Iteration {self.iteration}/{self.config.max_iterations}")
            logger.info(f"{'='*60}")

            try:
                self._write_status(phase="running")
                self._run_next_task()
                self._write_status(phase="idle")
            except Exception as e:
                logger.error(f"Iteration failed: {e}", exc_info=True)
                self._write_status(phase="error", current_task=str(e))
                time.sleep(5)

            time.sleep(self.config.loop_delay_seconds)

        self._write_status(phase="stopped")
        logger.info(
            f"Agent stopped. Iterations: {self.iteration}, "
            f"Cost: ${self.cost.cost_today:.4f}"
        )

    # ── Task execution ───────────────────────────────────────────

    def _run_next_task(self):
        """Pick and execute the next task from BACKLOG.md."""
        # Ask the agent to read the backlog and decide what to work on
        self.conversation = []
        self._run_task(
            "Read BACKLOG.md using the backlog_read skill. Pick the highest "
            "priority pending task that is NOT already in progress. Then "
            "implement it fully: read relevant code, make changes, build, "
            "test, and commit. Update BACKLOG.md when done."
        )

    def _run_task(self, task: str):
        """Execute a single task via agentic tool-use loop."""
        self.conversation = [{"role": "user", "content": task}]
        tools = get_skill_schemas()

        for turn in range(50):  # max turns per task
            if self._shutdown or self.cost.over_budget:
                break

            response = self.client.messages.create(
                model=self.config.model,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                system=SYSTEM_PROMPT,
                tools=tools,
                messages=self.conversation,
            )

            # Track cost
            self.cost.record_usage(
                response.usage.input_tokens,
                response.usage.output_tokens,
            )

            # Process response content blocks
            assistant_content = []
            tool_results = []
            has_tool_use = False

            for block in response.content:
                if block.type == "text":
                    logger.info(f"Agent: {block.text[:200]}...")
                    assistant_content.append(block)
                elif block.type == "tool_use":
                    has_tool_use = True
                    assistant_content.append(block)
                    logger.info(f"Calling skill: {block.name}({json.dumps(block.input)[:100]}...)")

                    result = self.executor.execute(block.name, block.input)
                    logger.info(f"Skill result: {result[:200]}...")

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result,
                    })

            # Add assistant message
            self.conversation.append({
                "role": "assistant",
                "content": assistant_content,
            })

            # If there were tool uses, add results and continue
            if has_tool_use:
                self.conversation.append({
                    "role": "user",
                    "content": tool_results,
                })
                continue

            # No tool use = agent is done with this task
            if response.stop_reason == "end_turn":
                logger.info("Task completed.")
                break

        logger.info(f"Task finished after {turn + 1} turns")

    # ── Scan mode ────────────────────────────────────────────────

    def _run_scan(self):
        """Scan the repo for improvements without modifying anything."""
        logger.info("Running improvement scan (read-only)...")

        # First, gather repo structure
        structure = self.executor.execute("file_list", {
            "path": ".", "pattern": "**/*.swift"
        })

        scan_message = (
            f"Here is the repository file structure:\n\n"
            f"```\n{structure}\n```\n\n"
            f"{SCAN_PROMPT}\n\n"
            "Use the file_read and search_code skills to inspect the code, "
            "then output your findings."
        )

        self.conversation = [{"role": "user", "content": scan_message}]
        tools = get_skill_schemas()

        for turn in range(30):
            if self._shutdown or self.cost.over_budget:
                break

            response = self.client.messages.create(
                model=self.config.model,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                system=SYSTEM_PROMPT,
                tools=tools,
                messages=self.conversation,
            )

            self.cost.record_usage(
                response.usage.input_tokens,
                response.usage.output_tokens,
            )

            assistant_content = []
            tool_results = []
            has_tool_use = False

            for block in response.content:
                if block.type == "text":
                    print(block.text)
                    assistant_content.append(block)
                elif block.type == "tool_use":
                    has_tool_use = True
                    assistant_content.append(block)
                    # Only allow read-only skills in scan mode
                    if block.name in ("file_read", "file_list", "search_code",
                                      "backlog_read", "git_status", "git_diff"):
                        result = self.executor.execute(block.name, block.input)
                    else:
                        result = f"BLOCKED: Skill '{block.name}' not allowed in scan mode"
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result,
                    })

            self.conversation.append({"role": "assistant", "content": assistant_content})

            if has_tool_use:
                self.conversation.append({"role": "user", "content": tool_results})
                continue

            if response.stop_reason == "end_turn":
                break

        logger.info(f"Scan complete. Cost: ${self.cost.cost_today:.4f}")


def _setup_logging(config: OpenClawConfig):
    """Configure logging to file and console."""
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    level = getattr(logging, config.log_level.upper(), logging.INFO)

    # File handler
    file_handler = logging.FileHandler(config.log_path, mode="a")
    file_handler.setFormatter(logging.Formatter(log_format))

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(
        "%(asctime)s %(levelname)-5s %(message)s", datefmt="%H:%M:%S"
    ))

    root = logging.getLogger("openclaw")
    root.setLevel(level)
    root.addHandler(file_handler)
    root.addHandler(console_handler)
