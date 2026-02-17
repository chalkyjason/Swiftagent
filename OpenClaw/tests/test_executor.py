"""Tests for OpenClaw skill executor."""

import json
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from OpenClaw.config import OpenClawConfig
from OpenClaw.safety import SafetyGuard
from OpenClaw.skills.executor import SkillExecutor


@pytest.fixture
def workspace(tmp_path):
    return tmp_path


@pytest.fixture
def config(workspace):
    return OpenClawConfig(
        workspace_root=workspace,
        api_key="test-key",
        dry_run=False,
    )


@pytest.fixture
def dry_config(workspace):
    return OpenClawConfig(
        workspace_root=workspace,
        api_key="test-key",
        dry_run=True,
    )


@pytest.fixture
def guard(config):
    return SafetyGuard(config)


@pytest.fixture
def executor(config, guard):
    return SkillExecutor(config, guard)


@pytest.fixture
def dry_executor(dry_config):
    guard = SafetyGuard(dry_config)
    return SkillExecutor(dry_config, guard)


# ---------------------------------------------------------------------------
# Dispatch
# ---------------------------------------------------------------------------

class TestDispatch:
    def test_unknown_skill_returns_error(self, executor):
        result = executor.execute("nonexistent_skill", {})
        assert "ERROR" in result
        assert "Unknown skill" in result

    def test_all_14_skills_registered(self, executor):
        expected = {
            "shell_exec", "file_read", "file_write", "file_patch", "file_list",
            "git_status", "git_diff", "git_commit",
            "task_create", "task_list", "task_update",
            "search_code", "agent_delegate", "agent_status",
        }
        assert set(executor._dispatch.keys()) == expected


# ---------------------------------------------------------------------------
# File operations
# ---------------------------------------------------------------------------

class TestFileRead:
    def test_read_existing_file(self, executor, workspace):
        f = workspace / "hello.txt"
        f.write_text("hello world")
        result = executor.execute("file_read", {"path": "hello.txt"})
        assert result == "hello world"

    def test_read_nonexistent_file(self, executor):
        result = executor.execute("file_read", {"path": "missing.txt"})
        assert "ERROR" in result
        assert "not found" in result.lower()

    def test_read_outside_sandbox(self, executor):
        result = executor.execute("file_read", {"path": "../../etc/passwd"})
        assert "BLOCKED" in result


class TestFileWrite:
    def test_write_new_file(self, executor, workspace):
        result = executor.execute("file_write", {"path": "new.py", "content": "print('hi')"})
        assert "OK" in result
        assert (workspace / "new.py").read_text() == "print('hi')"

    def test_write_creates_parent_dirs(self, executor, workspace):
        result = executor.execute("file_write", {"path": "sub/dir/file.txt", "content": "nested"})
        assert "OK" in result
        assert (workspace / "sub" / "dir" / "file.txt").read_text() == "nested"

    def test_write_outside_sandbox_blocked(self, executor):
        result = executor.execute("file_write", {"path": "../../evil.py", "content": "bad"})
        assert "BLOCKED" in result

    def test_write_dry_run(self, dry_executor):
        result = dry_executor.execute("file_write", {"path": "test.py", "content": "data"})
        assert "DRY RUN" in result

    def test_write_too_large(self, executor, workspace):
        huge = "x" * (1_048_577)
        result = executor.execute("file_write", {"path": "big.bin", "content": huge})
        assert "BLOCKED" in result


class TestFilePatch:
    def test_patch_replaces_string(self, executor, workspace):
        f = workspace / "code.py"
        f.write_text("def old_name():\n    pass\n")
        result = executor.execute("file_patch", {
            "path": "code.py",
            "old_string": "old_name",
            "new_string": "new_name",
        })
        assert "OK" in result
        assert "new_name" in f.read_text()
        assert "old_name" not in f.read_text()

    def test_patch_string_not_found(self, executor, workspace):
        f = workspace / "code.py"
        f.write_text("hello")
        result = executor.execute("file_patch", {
            "path": "code.py",
            "old_string": "goodbye",
            "new_string": "hi",
        })
        assert "ERROR" in result

    def test_patch_ambiguous_match(self, executor, workspace):
        f = workspace / "code.py"
        f.write_text("foo foo")
        result = executor.execute("file_patch", {
            "path": "code.py",
            "old_string": "foo",
            "new_string": "bar",
        })
        assert "ERROR" in result
        assert "2 times" in result

    def test_patch_dry_run(self, dry_executor, workspace):
        f = workspace / "code.py"
        f.write_text("old")
        result = dry_executor.execute("file_patch", {
            "path": "code.py",
            "old_string": "old",
            "new_string": "new",
        })
        assert "DRY RUN" in result
        assert f.read_text() == "old"  # not modified


class TestFileList:
    def test_list_files(self, executor, workspace):
        (workspace / "a.py").write_text("")
        (workspace / "b.txt").write_text("")
        result = executor.execute("file_list", {"path": "."})
        assert "a.py" in result
        assert "b.txt" in result

    def test_list_with_pattern(self, executor, workspace):
        (workspace / "a.py").write_text("")
        (workspace / "b.txt").write_text("")
        result = executor.execute("file_list", {"path": ".", "pattern": "*.py"})
        assert "a.py" in result
        assert "b.txt" not in result

    def test_list_nonexistent_dir(self, executor):
        result = executor.execute("file_list", {"path": "no_such_dir"})
        assert "ERROR" in result


# ---------------------------------------------------------------------------
# Shell execution
# ---------------------------------------------------------------------------

class TestShellExec:
    def test_allowed_command(self, executor):
        result = executor.execute("shell_exec", {"command": "echo hello"})
        assert "hello" in result

    def test_blocked_command(self, executor):
        result = executor.execute("shell_exec", {"command": "sudo rm -rf /"})
        assert "BLOCKED" in result

    def test_dry_run(self, dry_executor):
        result = dry_executor.execute("shell_exec", {"command": "ls"})
        assert "DRY RUN" in result

    def test_working_dir_outside_sandbox(self, executor):
        result = executor.execute("shell_exec", {
            "command": "ls",
            "working_dir": "../../etc",
        })
        assert "BLOCKED" in result


# ---------------------------------------------------------------------------
# Task management
# ---------------------------------------------------------------------------

class TestTaskCreate:
    def test_create_task_new_backlog(self, executor, workspace):
        result = executor.execute("task_create", {
            "title": "Add tests",
            "priority": "P1",
        })
        assert "OK" in result
        assert (workspace / "BACKLOG.md").exists()
        content = (workspace / "BACKLOG.md").read_text()
        assert "Add tests" in content
        assert "[P1]" in content

    def test_create_task_existing_backlog(self, executor, workspace):
        backlog = workspace / "BACKLOG.md"
        backlog.write_text("# Task Backlog\n\n## Pending\n\n## In Progress\n\n## Completed\n")
        result = executor.execute("task_create", {
            "title": "Fix bug",
            "priority": "P2",
            "category": "Backend",
            "agent": "claude",
        })
        assert "OK" in result
        content = backlog.read_text()
        assert "Fix bug" in content
        assert "[Backend]" in content
        assert "@agent:claude" in content

    def test_create_task_writes_json(self, executor, workspace):
        executor.execute("task_create", {"title": "Test task", "priority": "P3"})
        task_files = list((workspace / ".openclaw_tasks").iterdir())
        assert len(task_files) == 1
        data = json.loads(task_files[0].read_text())
        assert data["title"] == "Test task"
        assert data["priority"] == "P3"
        assert data["status"] == "pending"

    def test_create_task_dry_run(self, dry_executor, workspace):
        result = dry_executor.execute("task_create", {
            "title": "Dry task",
            "priority": "P1",
        })
        assert "DRY RUN" in result


class TestTaskList:
    def test_list_tasks(self, executor, workspace):
        backlog = workspace / "BACKLOG.md"
        backlog.write_text(
            "# Backlog\n\n## Pending\n\n"
            "- [ ] [P1] Fix critical bug\n"
            "- [ ] [P2] Add docs\n\n"
            "## Completed\n\n"
            "- [x] [P3] Setup repo\n"
        )
        result = executor.execute("task_list", {"status_filter": "all"})
        assert "Fix critical bug" in result
        assert "Add docs" in result
        assert "Setup repo" in result

    def test_list_filtered(self, executor, workspace):
        backlog = workspace / "BACKLOG.md"
        backlog.write_text(
            "# Backlog\n\n## Pending\n\n"
            "- [ ] [P1] Pending task\n\n"
            "## Completed\n\n"
            "- [x] Done task\n"
        )
        result = executor.execute("task_list", {"status_filter": "completed"})
        assert "Done task" in result
        assert "Pending task" not in result

    def test_list_no_backlog(self, executor):
        result = executor.execute("task_list", {"status_filter": "all"})
        assert "ERROR" in result


class TestTaskUpdate:
    def test_complete_task(self, executor, workspace):
        backlog = workspace / "BACKLOG.md"
        backlog.write_text("## Pending\n\n- [ ] [P1] Fix bug\n")
        result = executor.execute("task_update", {
            "task_title": "Fix bug",
            "new_status": "completed",
        })
        assert "OK" in result
        assert "- [x]" in backlog.read_text()

    def test_update_task_not_found(self, executor, workspace):
        backlog = workspace / "BACKLOG.md"
        backlog.write_text("## Pending\n\n- [ ] Something else\n")
        result = executor.execute("task_update", {
            "task_title": "Nonexistent",
            "new_status": "completed",
        })
        assert "ERROR" in result

    def test_update_with_notes(self, executor, workspace):
        backlog = workspace / "BACKLOG.md"
        backlog.write_text("## Pending\n\n- [ ] [P1] Fix bug\n")
        executor.execute("task_update", {
            "task_title": "Fix bug",
            "new_status": "completed",
            "notes": "Fixed in commit abc123",
        })
        content = backlog.read_text()
        assert "Fixed in commit abc123" in content


# ---------------------------------------------------------------------------
# Code search
# ---------------------------------------------------------------------------

class TestSearchCode:
    def test_search_finds_pattern(self, executor, workspace):
        (workspace / "app.py").write_text("def hello():\n    print('world')\n")
        result = executor.execute("search_code", {"pattern": "hello"})
        assert "app.py" in result
        assert "hello" in result

    def test_search_regex(self, executor, workspace):
        (workspace / "app.py").write_text("foo123\nbar456\n")
        result = executor.execute("search_code", {"pattern": r"foo\d+"})
        assert "foo123" in result

    def test_search_no_matches(self, executor, workspace):
        (workspace / "app.py").write_text("nothing here")
        result = executor.execute("search_code", {"pattern": "zzzzz"})
        assert "no matches" in result.lower()

    def test_search_invalid_regex(self, executor):
        result = executor.execute("search_code", {"pattern": "[invalid"})
        assert "ERROR" in result

    def test_search_with_file_pattern(self, executor, workspace):
        (workspace / "a.py").write_text("target")
        (workspace / "b.txt").write_text("target")
        result = executor.execute("search_code", {
            "pattern": "target",
            "file_pattern": "*.py",
        })
        assert "a.py" in result
        assert "b.txt" not in result


# ---------------------------------------------------------------------------
# Agent delegation
# ---------------------------------------------------------------------------

class TestAgentDelegate:
    def test_claude_disabled(self, executor):
        result = executor.execute("agent_delegate", {
            "agent": "claude",
            "task": "do something",
        })
        assert "ERROR" in result
        assert "not enabled" in result.lower()

    def test_goose_disabled(self, executor):
        result = executor.execute("agent_delegate", {
            "agent": "goose",
            "task": "do something",
        })
        assert "ERROR" in result
        assert "not enabled" in result.lower()

    def test_unknown_agent(self, executor):
        result = executor.execute("agent_delegate", {
            "agent": "unknown_agent",
            "task": "do something",
        })
        assert "ERROR" in result
        assert "Unknown agent" in result

    def test_working_dir_outside_sandbox(self, executor):
        result = executor.execute("agent_delegate", {
            "agent": "claude",
            "task": "do something",
            "working_dir": "../../etc",
        })
        assert "BLOCKED" in result

    def test_claude_dry_run(self, dry_executor, workspace):
        dry_executor.config.claude_cli_enabled = True
        result = dry_executor.execute("agent_delegate", {
            "agent": "claude",
            "task": "test task",
        })
        assert "DRY RUN" in result

    def test_goose_dry_run(self, dry_executor, workspace):
        dry_executor.config.goose_enabled = True
        result = dry_executor.execute("agent_delegate", {
            "agent": "goose",
            "task": "test task",
        })
        assert "DRY RUN" in result

    def test_aider_disabled(self, executor):
        result = executor.execute("agent_delegate", {
            "agent": "aider",
            "task": "do something",
        })
        assert "ERROR" in result
        assert "not enabled" in result.lower()

    def test_aider_dry_run(self, dry_executor, workspace):
        dry_executor.config.aider_enabled = True
        result = dry_executor.execute("agent_delegate", {
            "agent": "aider",
            "task": "test task",
        })
        assert "DRY RUN" in result

    def test_codex_disabled(self, executor):
        result = executor.execute("agent_delegate", {
            "agent": "codex",
            "task": "do something",
        })
        assert "ERROR" in result
        assert "not enabled" in result.lower()

    def test_codex_dry_run(self, dry_executor, workspace):
        dry_executor.config.codex_enabled = True
        result = dry_executor.execute("agent_delegate", {
            "agent": "codex",
            "task": "test task",
        })
        assert "DRY RUN" in result

    def test_cline_disabled(self, executor):
        result = executor.execute("agent_delegate", {
            "agent": "cline",
            "task": "do something",
        })
        assert "ERROR" in result
        assert "not enabled" in result.lower()

    def test_cline_dry_run(self, dry_executor, workspace):
        dry_executor.config.cline_enabled = True
        result = dry_executor.execute("agent_delegate", {
            "agent": "cline",
            "task": "test task",
        })
        assert "DRY RUN" in result


# ---------------------------------------------------------------------------
# Agent status
# ---------------------------------------------------------------------------

class TestAgentStatus:
    def test_status_shows_openclaw(self, executor):
        result = executor.execute("agent_status", {})
        assert "OpenClaw" in result
        assert "RUNNING" in result

    def test_status_shows_disabled_agents(self, executor):
        result = executor.execute("agent_status", {})
        assert "DISABLED" in result  # both claude and goose disabled by default


# ---------------------------------------------------------------------------
# Subprocess retry logic
# ---------------------------------------------------------------------------

class TestSubprocessRetry:
    def test_retry_succeeds_on_second_attempt(self, executor, workspace):
        fail = MagicMock(stdout="", stderr="oops", returncode=1)
        ok = MagicMock(stdout="done", stderr="", returncode=0)

        with patch("OpenClaw.skills.executor.subprocess.run", side_effect=[fail, ok]), \
             patch("OpenClaw.skills.executor.time.sleep"):
            result = executor._run_subprocess_with_retry(
                "test cmd", workspace, "TestAgent", max_retries=3, base_delay=0,
            )
        assert "done" in result

    def test_retry_exhausts_attempts(self, executor, workspace):
        fail = MagicMock(stdout="", stderr="error", returncode=1)

        with patch("OpenClaw.skills.executor.subprocess.run", return_value=fail), \
             patch("OpenClaw.skills.executor.time.sleep"):
            result = executor._run_subprocess_with_retry(
                "bad cmd", workspace, "TestAgent", max_retries=2, base_delay=0,
            )
        assert "ERROR" in result
        assert "2 attempts" in result

    def test_retry_on_timeout(self, executor, workspace):
        ok = MagicMock(stdout="recovered", stderr="", returncode=0)

        with patch("OpenClaw.skills.executor.subprocess.run",
                   side_effect=[subprocess.TimeoutExpired("cmd", 300), ok]), \
             patch("OpenClaw.skills.executor.time.sleep"):
            result = executor._run_subprocess_with_retry(
                "slow cmd", workspace, "TestAgent", max_retries=2, base_delay=0,
            )
        assert "recovered" in result

    def test_timeout_exhausts_all_retries(self, executor, workspace):
        with patch("OpenClaw.skills.executor.subprocess.run",
                   side_effect=subprocess.TimeoutExpired("cmd", 300)), \
             patch("OpenClaw.skills.executor.time.sleep"):
            result = executor._run_subprocess_with_retry(
                "hangs", workspace, "TestAgent", max_retries=2, base_delay=0,
            )
        assert "ERROR" in result
        assert "timed out" in result

    def test_exponential_backoff_delays(self, executor, workspace):
        fail = MagicMock(stdout="", stderr="err", returncode=1)

        with patch("OpenClaw.skills.executor.subprocess.run", return_value=fail), \
             patch("OpenClaw.skills.executor.time.sleep") as mock_sleep:
            executor._run_subprocess_with_retry(
                "fail cmd", workspace, "TestAgent", max_retries=3, base_delay=2.0,
            )
        # Should sleep with exponential backoff: 2s, 4s
        assert mock_sleep.call_count == 2
        assert mock_sleep.call_args_list[0][0][0] == pytest.approx(2.0)
        assert mock_sleep.call_args_list[1][0][0] == pytest.approx(4.0)
