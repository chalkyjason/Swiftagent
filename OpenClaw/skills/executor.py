"""Skill executor — runs tool calls returned by the Claude API.

General-purpose executor with multi-agent delegation and task management.
"""

import json
import logging
import re
import shutil
import subprocess
import time
from datetime import datetime
from pathlib import Path

from ..config import OpenClawConfig
from ..safety import SafetyGuard

logger = logging.getLogger("openclaw.executor")


class SkillExecutor:
    """Dispatches and executes skill (tool) calls from the agent."""

    def __init__(self, config: OpenClawConfig, safety: SafetyGuard):
        self.config = config
        self.safety = safety
        self._dispatch = {
            "shell_exec": self._shell_exec,
            "file_read": self._file_read,
            "file_write": self._file_write,
            "file_patch": self._file_patch,
            "file_list": self._file_list,
            "git_status": self._git_status,
            "git_diff": self._git_diff,
            "git_commit": self._git_commit,
            "task_create": self._task_create,
            "task_list": self._task_list,
            "task_update": self._task_update,
            "search_code": self._search_code,
            "agent_delegate": self._agent_delegate,
            "agent_status": self._agent_status,
        }

    def execute(self, skill_name: str, inputs: dict) -> str:
        """Execute a skill by name. Returns the result string."""
        handler = self._dispatch.get(skill_name)
        if not handler:
            return f"ERROR: Unknown skill '{skill_name}'"
        try:
            result = handler(inputs)
            logger.info(f"Skill {skill_name} executed successfully")
            return result
        except Exception as e:
            logger.error(f"Skill {skill_name} failed: {e}")
            return f"ERROR: {e}"

    # -- Shell --

    def _shell_exec(self, inputs: dict) -> str:
        command = inputs["command"]
        allowed, reason = self.safety.validate_command(command)
        if not allowed:
            return f"BLOCKED: {reason}"

        working_dir = self.config.workspace_root
        if "working_dir" in inputs and inputs["working_dir"]:
            working_dir = self.config.workspace_root / inputs["working_dir"]
            if not self.safety.validate_path(working_dir):
                return "BLOCKED: Working directory outside sandbox"

        if self.config.dry_run:
            return f"[DRY RUN] Would execute: {command}"

        try:
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True,
                cwd=str(working_dir), timeout=120
            )
        except subprocess.TimeoutExpired:
            return "ERROR: Command timed out after 120 seconds"

        output = result.stdout
        if result.stderr:
            output += f"\nSTDERR:\n{result.stderr}"
        if result.returncode != 0:
            output += f"\nExit code: {result.returncode}"
        return output.strip() or "(no output)"

    # -- File operations --

    def _file_read(self, inputs: dict) -> str:
        path = self.config.workspace_root / inputs["path"]
        if not self.safety.validate_path(path):
            return f"BLOCKED: Path outside sandbox: {inputs['path']}"
        if not path.exists():
            return f"ERROR: File not found: {inputs['path']}"
        try:
            return path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return f"ERROR: Cannot read binary file: {inputs['path']}"

    def _file_write(self, inputs: dict) -> str:
        path = self.config.workspace_root / inputs["path"]
        content = inputs["content"]
        allowed, reason = self.safety.validate_file_write(path, content)
        if not allowed:
            return f"BLOCKED: {reason}"
        if self.config.dry_run:
            return f"[DRY RUN] Would write {len(content)} chars to {inputs['path']}"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        self.safety.record_file_created()
        logger.info(f"Wrote {len(content)} chars to {inputs['path']}")
        return f"OK: Written {len(content)} chars to {inputs['path']}"

    def _file_patch(self, inputs: dict) -> str:
        path = self.config.workspace_root / inputs["path"]
        if not self.safety.validate_path(path):
            return "BLOCKED: Path outside sandbox"
        if not path.exists():
            return f"ERROR: File not found: {inputs['path']}"
        content = path.read_text(encoding="utf-8")
        old_string = inputs["old_string"]
        new_string = inputs["new_string"]
        if old_string not in content:
            return f"ERROR: old_string not found in {inputs['path']}"
        count = content.count(old_string)
        if count > 1:
            return f"ERROR: old_string found {count} times — must be unique"
        if self.config.dry_run:
            return f"[DRY RUN] Would patch {inputs['path']}"
        new_content = content.replace(old_string, new_string, 1)
        path.write_text(new_content, encoding="utf-8")
        logger.info(f"Patched {inputs['path']}")
        return f"OK: Patched {inputs['path']}"

    def _file_list(self, inputs: dict) -> str:
        base = self.config.workspace_root / inputs.get("path", ".")
        if not self.safety.validate_path(base):
            return "BLOCKED: Path outside sandbox"
        if not base.exists():
            return f"ERROR: Directory not found: {inputs.get('path', '.')}"
        pattern = inputs.get("pattern", "*")
        matches = sorted(str(p.relative_to(self.config.workspace_root))
                         for p in base.rglob(pattern)
                         if not any(part.startswith(".") for part in p.parts))
        return "\n".join(matches[:200]) or "(no matches)"

    # -- Git --

    def _git_status(self, _inputs: dict) -> str:
        result = subprocess.run(
            "git status --short", shell=True, capture_output=True, text=True,
            cwd=str(self.config.workspace_root)
        )
        return result.stdout.strip() or "(working tree clean)"

    def _git_diff(self, inputs: dict) -> str:
        cmd = "git diff"
        if "path" in inputs and inputs["path"]:
            path = self.config.workspace_root / inputs["path"]
            if not self.safety.validate_path(path):
                return "BLOCKED: Path outside sandbox"
            cmd += f" -- {inputs['path']}"
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True,
            cwd=str(self.config.workspace_root)
        )
        diff = result.stdout.strip()
        if len(diff) > 10000:
            diff = diff[:10000] + "\n\n... (truncated)"
        return diff or "(no changes)"

    def _git_commit(self, inputs: dict) -> str:
        files = inputs["files"]
        message = inputs["message"]
        for f in files:
            full = self.config.workspace_root / f
            if not self.safety.validate_path(full):
                return f"BLOCKED: File outside sandbox: {f}"
        if self.config.dry_run:
            return f"[DRY RUN] Would commit {len(files)} files: {message}"
        for f in files:
            add_result = subprocess.run(
                ["git", "add", "--", f], capture_output=True, text=True,
                cwd=str(self.config.workspace_root)
            )
            if add_result.returncode != 0:
                return f"GIT ADD FAILED for {f}:\n{add_result.stderr.strip()}"
        result = subprocess.run(
            ["git", "commit", "-m", message],
            capture_output=True, text=True,
            cwd=str(self.config.workspace_root)
        )
        if result.returncode != 0:
            return f"COMMIT FAILED:\n{result.stderr}"
        return f"COMMITTED: {message}\n{result.stdout.strip()}"

    # -- Task management --

    def _task_create(self, inputs: dict) -> str:
        title = inputs["title"]
        priority = inputs.get("priority", "P2")
        description = inputs.get("description", "")
        category = inputs.get("category", "General")
        agent = inputs.get("agent", "any")

        backlog = self.config.backlog_path
        if not backlog.exists():
            backlog.write_text("# Task Backlog\n\n## Pending\n\n## In Progress\n\n## Completed\n", encoding="utf-8")

        content = backlog.read_text(encoding="utf-8")

        # Build the task line
        agent_tag = f" @agent:{agent}" if agent != "any" else ""
        cat_tag = f" [{category}]" if category else ""
        task_line = f"- [ ] [{priority}]{cat_tag} {title}{agent_tag}"
        if description:
            task_line += f"\n  > {description}"

        # Insert into Pending section
        if "## Pending" in content:
            content = content.replace("## Pending", f"## Pending\n\n{task_line}", 1)
        else:
            content += f"\n## Pending\n\n{task_line}\n"

        if self.config.dry_run:
            return f"[DRY RUN] Would create task: {title}"

        backlog.write_text(content, encoding="utf-8")
        logger.info(f"Created task: {title} [{priority}]")

        # Write task detail to tasks dir
        task_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        task_file = self.config.tasks_dir / f"{task_id}.json"
        task_data = {
            "id": task_id,
            "title": title,
            "description": description,
            "priority": priority,
            "category": category,
            "agent": agent,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
        }
        task_file.write_text(json.dumps(task_data, indent=2), encoding="utf-8")

        return f"OK: Created task '{title}' [{priority}] assigned to {agent}"

    def _task_list(self, inputs: dict) -> str:
        status_filter = inputs.get("status_filter", "all")

        if not self.config.backlog_path.exists():
            return "ERROR: BACKLOG.md not found"

        content = self.config.backlog_path.read_text(encoding="utf-8")
        lines = content.split("\n")
        tasks = []
        current_section = ""

        for line in lines:
            stripped = line.strip()
            if stripped.startswith("##"):
                header = stripped.lstrip("#").strip().lower()
                if "in progress" in header:
                    current_section = "in_progress"
                elif "completed" in header or "done" in header:
                    current_section = "completed"
                elif "blocked" in header:
                    current_section = "blocked"
                elif "pending" in header:
                    current_section = "pending"
                continue

            if not stripped.startswith("- ["):
                continue

            is_done = stripped.startswith("- [x]")
            status = "completed" if is_done else current_section or "pending"

            if status_filter != "all" and status != status_filter:
                continue

            task_text = re.sub(r"^-\s*\[[ xX]\]\s*", "", stripped).strip()
            tasks.append(f"[{status.upper()}] {task_text}")

        return "\n".join(tasks) if tasks else "(no tasks found)"

    def _task_update(self, inputs: dict) -> str:
        if not self.config.backlog_path.exists():
            return "ERROR: BACKLOG.md not found"

        task_title = inputs["task_title"]
        new_status = inputs["new_status"]
        notes = inputs.get("notes", "")

        content = self.config.backlog_path.read_text(encoding="utf-8")
        lines = content.split("\n")
        updated = False

        for i, line in enumerate(lines):
            if task_title.lower() in line.lower():
                if new_status == "completed":
                    lines[i] = line.replace("- [ ]", "- [x]")
                elif new_status == "pending":
                    lines[i] = line.replace("- [x]", "- [ ]")
                if notes:
                    lines.insert(i + 1, f"  > Note: {notes}")
                updated = True
                break

        if not updated:
            return f"ERROR: Task not found: {task_title}"

        if self.config.dry_run:
            return f"[DRY RUN] Would update task to {new_status}"

        self.config.backlog_path.write_text("\n".join(lines), encoding="utf-8")
        logger.info(f"Updated task '{task_title}' -> {new_status}")
        return f"OK: Updated task to {new_status}"

    # -- Code search --

    def _search_code(self, inputs: dict) -> str:
        pattern = inputs["pattern"]
        file_pattern = inputs.get("file_pattern", "*")
        search_path = self.config.workspace_root / inputs.get("path", ".")

        if not self.safety.validate_path(search_path):
            return "BLOCKED: Path outside sandbox"

        results = []
        try:
            regex = re.compile(pattern, re.IGNORECASE)
        except re.error as e:
            return f"ERROR: Invalid regex: {e}"

        for filepath in search_path.rglob(file_pattern):
            if any(part.startswith(".") for part in filepath.parts):
                continue
            try:
                content = filepath.read_text(encoding="utf-8")
                for line_num, line in enumerate(content.split("\n"), 1):
                    if regex.search(line):
                        rel = filepath.relative_to(self.config.workspace_root)
                        results.append(f"{rel}:{line_num}: {line.strip()}")
            except (UnicodeDecodeError, PermissionError):
                continue

        if len(results) > 100:
            results = results[:100]
            results.append("... (truncated to 100 results)")

        return "\n".join(results) or "(no matches)"

    # -- Multi-agent delegation --

    def _agent_delegate(self, inputs: dict) -> str:
        agent = inputs["agent"]
        task = inputs["task"]
        working_dir = self.config.workspace_root / inputs.get("working_dir", ".")

        if not self.safety.validate_path(working_dir):
            return "BLOCKED: Working directory outside sandbox"

        if agent == "claude":
            if not self.config.claude_cli_enabled:
                return "ERROR: Claude CLI not enabled. Set CLAUDE_CLI_ENABLED=true"
            return self._run_claude_cli(task, working_dir)
        elif agent == "goose":
            if not self.config.goose_enabled:
                return "ERROR: Goose not enabled. Set GOOSE_ENABLED=true"
            return self._run_goose(task, working_dir)
        else:
            return f"ERROR: Unknown agent: {agent}"

    def _run_subprocess_with_retry(
        self, cmd: str, working_dir: Path, agent_name: str,
        max_retries: int = 3, base_delay: float = 2.0,
    ) -> str:
        """Run a subprocess command with exponential backoff retry on failure.

        Retries on non-zero exit codes and timeouts. Does NOT retry on
        FileNotFoundError (the binary is missing — retrying won't help).
        """
        last_error = ""
        for attempt in range(max_retries):
            try:
                result = subprocess.run(
                    cmd, shell=True, capture_output=True, text=True,
                    cwd=str(working_dir), timeout=300,
                )
                output = result.stdout.strip()
                if result.stderr:
                    output += f"\nSTDERR: {result.stderr.strip()}"

                if result.returncode == 0:
                    logger.info(f"{agent_name} completed: {output[:200]}...")
                    return output or f"(no output from {agent_name})"

                last_error = f"Exit code: {result.returncode}\n{output}"
                logger.warning(
                    f"{agent_name} attempt {attempt + 1}/{max_retries} failed: "
                    f"exit code {result.returncode}"
                )
            except subprocess.TimeoutExpired:
                last_error = f"{agent_name} timed out after 300s"
                logger.warning(
                    f"{agent_name} attempt {attempt + 1}/{max_retries} timed out"
                )

            if attempt < max_retries - 1:
                delay = base_delay * (2 ** attempt)
                logger.info(f"Retrying {agent_name} in {delay:.0f}s...")
                time.sleep(delay)

        return f"ERROR: {agent_name} failed after {max_retries} attempts. Last error: {last_error}"

    def _run_claude_cli(self, task: str, working_dir: Path) -> str:
        """Run a task via Claude Code CLI with retry."""
        logger.info(f"Delegating to Claude CLI: {task[:80]}...")

        if self.config.dry_run:
            return f"[DRY RUN] Would delegate to Claude CLI: {task}"

        if not shutil.which(self.config.claude_cli_path):
            return (
                f"ERROR: Claude CLI not found at '{self.config.claude_cli_path}'. "
                "Install with: npm install -g @anthropic-ai/claude-code"
            )

        cmd = f'{self.config.claude_cli_path} --print "{task}"'
        return self._run_subprocess_with_retry(cmd, working_dir, "Claude CLI")

    def _run_goose(self, task: str, working_dir: Path) -> str:
        """Run a task via Goose agent with retry."""
        logger.info(f"Delegating to Goose: {task[:80]}...")

        if self.config.dry_run:
            return f"[DRY RUN] Would delegate to Goose: {task}"

        if not shutil.which(self.config.goose_path):
            return (
                f"ERROR: Goose not found at '{self.config.goose_path}'. "
                "Install from: https://github.com/block/goose"
            )

        cmd = f'{self.config.goose_path} run "{task}"'
        return self._run_subprocess_with_retry(cmd, working_dir, "Goose")

    def _agent_status(self, _inputs: dict) -> str:
        """Check status of all configured agents."""
        statuses = []

        # OpenClaw (always available if we're running)
        statuses.append("OpenClaw: RUNNING (this agent)")

        # Claude CLI
        if self.config.claude_cli_enabled:
            try:
                result = subprocess.run(
                    f"{self.config.claude_cli_path} --version",
                    shell=True, capture_output=True, text=True, timeout=10
                )
                if result.returncode == 0:
                    version = result.stdout.strip()
                    statuses.append(f"Claude CLI: AVAILABLE ({version})")
                else:
                    statuses.append("Claude CLI: NOT FOUND (install: npm install -g @anthropic-ai/claude-code)")
            except (subprocess.TimeoutExpired, FileNotFoundError):
                statuses.append("Claude CLI: NOT FOUND")
        else:
            statuses.append("Claude CLI: DISABLED (set CLAUDE_CLI_ENABLED=true)")

        # Goose
        if self.config.goose_enabled:
            try:
                result = subprocess.run(
                    f"{self.config.goose_path} version",
                    shell=True, capture_output=True, text=True, timeout=10
                )
                if result.returncode == 0:
                    version = result.stdout.strip()
                    statuses.append(f"Goose: AVAILABLE ({version})")
                else:
                    statuses.append("Goose: NOT FOUND (install from https://github.com/block/goose)")
            except (subprocess.TimeoutExpired, FileNotFoundError):
                statuses.append("Goose: NOT FOUND")
        else:
            statuses.append("Goose: DISABLED (set GOOSE_ENABLED=true)")

        return "\n".join(statuses)
