"""Skill executor — runs tool calls returned by the Claude API.

Each skill function receives validated input and returns a string result.
All file/command operations pass through the SafetyGuard.
"""

import fnmatch
import logging
import re
import subprocess
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
            "swift_build": self._swift_build,
            "swift_test": self._swift_test,
            "git_status": self._git_status,
            "git_diff": self._git_diff,
            "git_commit": self._git_commit,
            "backlog_read": self._backlog_read,
            "backlog_update_task": self._backlog_update_task,
            "search_code": self._search_code,
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

    # ── Shell ────────────────────────────────────────────────────

    def _shell_exec(self, inputs: dict) -> str:
        command = inputs["command"]
        allowed, reason = self.safety.validate_command(command)
        if not allowed:
            return f"BLOCKED: {reason}"

        working_dir = self.config.workspace_root
        if "working_dir" in inputs and inputs["working_dir"]:
            working_dir = self.config.workspace_root / inputs["working_dir"]
            if not self.safety.validate_path(working_dir):
                return f"BLOCKED: Working directory outside sandbox"

        if self.config.dry_run:
            return f"[DRY RUN] Would execute: {command}"

        result = subprocess.run(
            command, shell=True, capture_output=True, text=True,
            cwd=str(working_dir), timeout=120
        )
        output = result.stdout
        if result.stderr:
            output += f"\nSTDERR:\n{result.stderr}"
        if result.returncode != 0:
            output += f"\nExit code: {result.returncode}"
        return output.strip() or "(no output)"

    # ── File operations ──────────────────────────────────────────

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
            return f"BLOCKED: Path outside sandbox"
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
            return f"BLOCKED: Path outside sandbox"
        if not base.exists():
            return f"ERROR: Directory not found: {inputs.get('path', '.')}"

        pattern = inputs.get("pattern", "*")
        matches = sorted(str(p.relative_to(self.config.workspace_root))
                         for p in base.rglob(pattern)
                         if not any(part.startswith(".") for part in p.parts))
        return "\n".join(matches[:200]) or "(no matches)"

    # ── Swift build/test ─────────────────────────────────────────

    def _swift_build(self, inputs: dict) -> str:
        pkg_path = self.config.workspace_root / inputs["package_path"]
        if not self.safety.validate_path(pkg_path):
            return "BLOCKED: Package path outside sandbox"

        cmd = f"swift build --package-path {pkg_path}"
        if self.config.dry_run:
            return f"[DRY RUN] Would run: {cmd}"

        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True,
            cwd=str(self.config.workspace_root), timeout=300
        )
        output = result.stdout + "\n" + result.stderr
        status = "BUILD SUCCEEDED" if result.returncode == 0 else "BUILD FAILED"
        return f"{status}\n\n{output.strip()}"

    def _swift_test(self, inputs: dict) -> str:
        pkg_path = self.config.workspace_root / inputs["package_path"]
        if not self.safety.validate_path(pkg_path):
            return "BLOCKED: Package path outside sandbox"

        cmd = f"swift test --package-path {pkg_path}"
        if self.config.dry_run:
            return f"[DRY RUN] Would run: {cmd}"

        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True,
            cwd=str(self.config.workspace_root), timeout=300
        )
        output = result.stdout + "\n" + result.stderr
        status = "TESTS PASSED" if result.returncode == 0 else "TESTS FAILED"
        return f"{status}\n\n{output.strip()}"

    # ── Git ──────────────────────────────────────────────────────

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

        # Validate all paths
        for f in files:
            full = self.config.workspace_root / f
            if not self.safety.validate_path(full):
                return f"BLOCKED: File outside sandbox: {f}"

        if self.config.dry_run:
            return f"[DRY RUN] Would commit {len(files)} files: {message}"

        # Stage files
        for f in files:
            subprocess.run(
                f"git add {f}", shell=True,
                cwd=str(self.config.workspace_root)
            )

        # Commit
        result = subprocess.run(
            ["git", "commit", "-m", message],
            capture_output=True, text=True,
            cwd=str(self.config.workspace_root)
        )
        if result.returncode != 0:
            return f"COMMIT FAILED:\n{result.stderr}"
        return f"COMMITTED: {message}\n{result.stdout.strip()}"

    # ── Backlog ──────────────────────────────────────────────────

    def _backlog_read(self, _inputs: dict) -> str:
        if not self.config.backlog_path.exists():
            return "ERROR: BACKLOG.md not found"
        return self.config.backlog_path.read_text(encoding="utf-8")

    def _backlog_update_task(self, inputs: dict) -> str:
        if not self.config.backlog_path.exists():
            return "ERROR: BACKLOG.md not found"

        task_desc = inputs["task_description"]
        new_status = inputs["new_status"]

        content = self.config.backlog_path.read_text(encoding="utf-8")
        lines = content.split("\n")
        updated = False

        for i, line in enumerate(lines):
            if task_desc.lower() in line.lower():
                if new_status == "completed":
                    lines[i] = line.replace("- [ ]", "- [x]")
                elif new_status == "pending":
                    lines[i] = line.replace("- [x]", "- [ ]")
                updated = True
                break

        if not updated:
            return f"ERROR: Task not found: {task_desc}"

        if self.config.dry_run:
            return f"[DRY RUN] Would update task to {new_status}"

        self.config.backlog_path.write_text("\n".join(lines), encoding="utf-8")
        return f"OK: Updated task to {new_status}"

    # ── Code search ──────────────────────────────────────────────

    def _search_code(self, inputs: dict) -> str:
        pattern = inputs["pattern"]
        file_pattern = inputs.get("file_pattern", "*.swift")
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
