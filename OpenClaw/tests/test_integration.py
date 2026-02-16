"""Integration tests for OpenClaw — multi-agent delegation, task lifecycle,
scan mode, and end-to-end agent loop with mocked LLM.
"""

import json
import subprocess
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from OpenClaw.agent import OpenClawAgent
from OpenClaw.config import OpenClawConfig
from OpenClaw.safety import SafetyGuard
from OpenClaw.skills.executor import SkillExecutor


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def workspace(tmp_path):
    """Workspace with a BACKLOG.md ready for tasks."""
    backlog = tmp_path / "BACKLOG.md"
    backlog.write_text(
        "# Task Backlog\n\n"
        "## In Progress\n\n"
        "## Pending\n\n"
        "## Blocked\n\n"
        "## Completed\n"
    )
    return tmp_path


@pytest.fixture
def config(workspace):
    return OpenClawConfig(
        workspace_root=workspace,
        api_key="test-key",
        dry_run=False,
    )


@pytest.fixture
def guard(config):
    return SafetyGuard(config)


@pytest.fixture
def executor(config, guard):
    return SkillExecutor(config, guard)


def _make_config(workspace, **overrides):
    defaults = dict(workspace_root=workspace, api_key="test-key")
    defaults.update(overrides)
    return OpenClawConfig(**defaults)


def _make_text_block(text):
    return SimpleNamespace(type="text", text=text)


def _make_tool_block(name, inputs, tool_id="tool_1"):
    return SimpleNamespace(type="tool_use", name=name, input=inputs, id=tool_id)


def _make_response(content_blocks, stop_reason="end_turn",
                   input_tokens=10, output_tokens=20):
    return SimpleNamespace(
        content=content_blocks,
        stop_reason=stop_reason,
        usage=SimpleNamespace(input_tokens=input_tokens,
                              output_tokens=output_tokens),
    )


# ---------------------------------------------------------------------------
# Task lifecycle: create → list → update
# ---------------------------------------------------------------------------

class TestTaskLifecycle:
    """End-to-end flow through the task management skills."""

    def test_create_list_complete(self, executor, workspace):
        # Create two tasks
        r1 = executor.execute("task_create", {
            "title": "Write unit tests",
            "priority": "P1",
            "category": "Quality",
            "agent": "openclaw",
        })
        assert "OK" in r1

        r2 = executor.execute("task_create", {
            "title": "Add dark mode",
            "priority": "P3",
            "category": "UI",
            "agent": "claude",
        })
        assert "OK" in r2

        # List all tasks
        all_tasks = executor.execute("task_list", {"status_filter": "all"})
        assert "Write unit tests" in all_tasks
        assert "Add dark mode" in all_tasks

        # Filter pending only
        pending = executor.execute("task_list", {"status_filter": "pending"})
        assert "Write unit tests" in pending
        assert "Add dark mode" in pending

        # Complete the first task
        r3 = executor.execute("task_update", {
            "task_title": "Write unit tests",
            "new_status": "completed",
            "notes": "Added 15 new tests",
        })
        assert "OK" in r3

        # Verify completed shows up correctly
        completed = executor.execute("task_list", {"status_filter": "completed"})
        assert "Write unit tests" in completed

        # Verify the other task is still pending
        still_pending = executor.execute("task_list", {"status_filter": "pending"})
        assert "Add dark mode" in still_pending
        assert "Write unit tests" not in still_pending

    def test_create_writes_json_task_file(self, executor, workspace):
        executor.execute("task_create", {
            "title": "Task A", "priority": "P1",
        })
        task_files = list((workspace / ".openclaw_tasks").iterdir())
        assert len(task_files) == 1

        data = json.loads(task_files[0].read_text())
        assert data["title"] == "Task A"
        assert data["priority"] == "P1"
        assert data["status"] == "pending"

    def test_update_nonexistent_task(self, executor, workspace):
        result = executor.execute("task_update", {
            "task_title": "Ghost task",
            "new_status": "completed",
        })
        assert "ERROR" in result


# ---------------------------------------------------------------------------
# Multi-agent delegation
# ---------------------------------------------------------------------------

class TestDelegationIntegration:
    """Tests for Claude CLI and Goose delegation with enabled configs."""

    def test_claude_cli_success(self, workspace):
        config = _make_config(workspace, claude_cli_enabled=True, claude_cli_path="claude")
        guard = SafetyGuard(config)
        executor = SkillExecutor(config, guard)

        mock_result = MagicMock(stdout="Task completed by Claude CLI", stderr="", returncode=0)
        with patch("OpenClaw.skills.executor.subprocess.run", return_value=mock_result), \
             patch("OpenClaw.skills.executor.shutil.which", return_value="/usr/bin/claude"):
            result = executor.execute("agent_delegate", {
                "agent": "claude",
                "task": "Refactor the auth module",
            })
        assert "Task completed by Claude CLI" in result

    def test_claude_cli_not_installed(self, workspace):
        config = _make_config(workspace, claude_cli_enabled=True, claude_cli_path="claude")
        guard = SafetyGuard(config)
        executor = SkillExecutor(config, guard)

        with patch("OpenClaw.skills.executor.shutil.which", return_value=None):
            result = executor.execute("agent_delegate", {
                "agent": "claude",
                "task": "anything",
            })
        assert "ERROR" in result
        assert "not found" in result.lower()

    def test_claude_cli_retries_on_failure(self, workspace):
        config = _make_config(workspace, claude_cli_enabled=True)
        guard = SafetyGuard(config)
        executor = SkillExecutor(config, guard)

        fail = MagicMock(stdout="", stderr="connection error", returncode=1)
        ok = MagicMock(stdout="recovered", stderr="", returncode=0)

        with patch("OpenClaw.skills.executor.subprocess.run", side_effect=[fail, ok]), \
             patch("OpenClaw.skills.executor.time.sleep"), \
             patch("OpenClaw.skills.executor.shutil.which", return_value="/usr/bin/claude"):
            result = executor.execute("agent_delegate", {
                "agent": "claude",
                "task": "retry test",
            })
        assert "recovered" in result

    def test_goose_success(self, workspace):
        config = _make_config(workspace, goose_enabled=True, goose_path="goose")
        guard = SafetyGuard(config)
        executor = SkillExecutor(config, guard)

        mock_result = MagicMock(stdout="Goose completed the task", stderr="", returncode=0)
        with patch("OpenClaw.skills.executor.subprocess.run", return_value=mock_result), \
             patch("OpenClaw.skills.executor.shutil.which", return_value="/usr/bin/goose"):
            result = executor.execute("agent_delegate", {
                "agent": "goose",
                "task": "Generate API docs",
            })
        assert "Goose completed" in result

    def test_goose_not_installed(self, workspace):
        config = _make_config(workspace, goose_enabled=True, goose_path="goose")
        guard = SafetyGuard(config)
        executor = SkillExecutor(config, guard)

        with patch("OpenClaw.skills.executor.shutil.which", return_value=None):
            result = executor.execute("agent_delegate", {
                "agent": "goose",
                "task": "anything",
            })
        assert "ERROR" in result
        assert "not found" in result.lower()

    def test_goose_retries_on_timeout(self, workspace):
        config = _make_config(workspace, goose_enabled=True)
        guard = SafetyGuard(config)
        executor = SkillExecutor(config, guard)

        ok = MagicMock(stdout="finally", stderr="", returncode=0)

        with patch("OpenClaw.skills.executor.subprocess.run",
                   side_effect=[subprocess.TimeoutExpired("cmd", 300), ok]), \
             patch("OpenClaw.skills.executor.time.sleep"), \
             patch("OpenClaw.skills.executor.shutil.which", return_value="/usr/bin/goose"):
            result = executor.execute("agent_delegate", {
                "agent": "goose",
                "task": "slow task",
            })
        assert "finally" in result

    def test_delegate_to_subdirectory(self, workspace):
        config = _make_config(workspace, claude_cli_enabled=True)
        guard = SafetyGuard(config)
        executor = SkillExecutor(config, guard)
        subdir = workspace / "subproject"
        subdir.mkdir()

        mock_result = MagicMock(stdout="done in subdir", stderr="", returncode=0)
        with patch("OpenClaw.skills.executor.subprocess.run", return_value=mock_result), \
             patch("OpenClaw.skills.executor.shutil.which", return_value="/usr/bin/claude"):
            result = executor.execute("agent_delegate", {
                "agent": "claude",
                "task": "build subproject",
                "working_dir": "subproject",
            })
        assert "done in subdir" in result


# ---------------------------------------------------------------------------
# Agent status integration
# ---------------------------------------------------------------------------

class TestAgentStatusIntegration:

    def test_status_with_claude_enabled_and_available(self, workspace):
        config = _make_config(workspace, claude_cli_enabled=True)
        guard = SafetyGuard(config)
        executor = SkillExecutor(config, guard)

        version_result = MagicMock(stdout="1.5.0", stderr="", returncode=0)
        with patch("OpenClaw.skills.executor.subprocess.run", return_value=version_result):
            result = executor.execute("agent_status", {})

        assert "OpenClaw: RUNNING" in result
        assert "Claude CLI: AVAILABLE" in result
        assert "1.5.0" in result

    def test_status_with_goose_enabled_but_missing(self, workspace):
        config = _make_config(workspace, goose_enabled=True)
        guard = SafetyGuard(config)
        executor = SkillExecutor(config, guard)

        fail_result = MagicMock(stdout="", stderr="", returncode=127)
        with patch("OpenClaw.skills.executor.subprocess.run", return_value=fail_result):
            result = executor.execute("agent_status", {})

        assert "Goose: NOT FOUND" in result

    def test_status_with_agent_version_timeout(self, workspace):
        config = _make_config(workspace, claude_cli_enabled=True)
        guard = SafetyGuard(config)
        executor = SkillExecutor(config, guard)

        with patch("OpenClaw.skills.executor.subprocess.run",
                   side_effect=subprocess.TimeoutExpired("cmd", 10)):
            result = executor.execute("agent_status", {})

        assert "Claude CLI: NOT FOUND" in result


# ---------------------------------------------------------------------------
# Scan mode — read-only enforcement
# ---------------------------------------------------------------------------

class TestScanMode:

    def _make_agent(self, workspace):
        config = _make_config(workspace)
        with patch("OpenClaw.agent.signal.signal"):
            agent = OpenClawAgent(config)
        agent.provider = MagicMock()
        return agent

    def test_scan_blocks_write_skills(self, workspace):
        agent = self._make_agent(workspace)

        # Scan mode: agent tries to write a file → should be blocked
        tool_response = _make_response(
            [_make_tool_block("file_write", {"path": "evil.py", "content": "bad"})],
            stop_reason="tool_use",
        )
        text_response = _make_response(
            [_make_text_block("Scan complete.")],
            stop_reason="end_turn",
        )
        agent.provider.create_message.side_effect = [tool_response, text_response]

        with patch.object(agent, "initialize"):
            agent.run(scan_only=True)

        # file_write should have been blocked
        assert not (workspace / "evil.py").exists()

    def test_scan_allows_read_skills(self, workspace):
        agent = self._make_agent(workspace)
        (workspace / "readme.txt").write_text("hello world")

        # Scan mode: agent reads a file → should succeed
        tool_response = _make_response(
            [_make_tool_block("file_read", {"path": "readme.txt"})],
            stop_reason="tool_use",
        )
        text_response = _make_response(
            [_make_text_block("Found readme.")],
            stop_reason="end_turn",
        )
        agent.provider.create_message.side_effect = [tool_response, text_response]

        with patch.object(agent, "initialize"):
            agent.run(scan_only=True)

        # Should have called the provider twice (tool + final)
        assert agent.provider.create_message.call_count == 2

    def test_scan_blocks_shell_exec(self, workspace):
        agent = self._make_agent(workspace)

        tool_response = _make_response(
            [_make_tool_block("shell_exec", {"command": "rm -rf ."})],
            stop_reason="tool_use",
        )
        text_response = _make_response(
            [_make_text_block("Done.")],
            stop_reason="end_turn",
        )
        agent.provider.create_message.side_effect = [tool_response, text_response]

        with patch.object(agent, "initialize"):
            agent.run(scan_only=True)

        # Verify shell_exec was blocked (not executed)
        # The tool result should contain BLOCKED
        tool_result_msg = agent.conversation[2]  # user message with tool_result
        assert tool_result_msg["role"] == "user"
        result_content = tool_result_msg["content"][0]["content"]
        assert "BLOCKED" in result_content

    def test_scan_blocks_git_commit(self, workspace):
        agent = self._make_agent(workspace)

        tool_response = _make_response(
            [_make_tool_block("git_commit", {"files": ["x.py"], "message": "bad"})],
            stop_reason="tool_use",
        )
        text_response = _make_response(
            [_make_text_block("Done.")],
            stop_reason="end_turn",
        )
        agent.provider.create_message.side_effect = [tool_response, text_response]

        with patch.object(agent, "initialize"):
            agent.run(scan_only=True)

        tool_result_msg = agent.conversation[2]
        result_content = tool_result_msg["content"][0]["content"]
        assert "BLOCKED" in result_content
        assert "scan mode" in result_content


# ---------------------------------------------------------------------------
# End-to-end agent loop with mocked LLM
# ---------------------------------------------------------------------------

class TestAgentLoopE2E:

    def _make_agent(self, workspace, **config_kwargs):
        config = _make_config(workspace, **config_kwargs)
        with patch("OpenClaw.agent.signal.signal"):
            agent = OpenClawAgent(config)
        agent.provider = MagicMock()
        return agent

    def test_file_read_write_roundtrip(self, workspace):
        """Agent reads a file, then writes a modified version."""
        agent = self._make_agent(workspace)
        (workspace / "input.txt").write_text("hello")

        # Turn 1: agent reads the file
        read_response = _make_response(
            [_make_tool_block("file_read", {"path": "input.txt"}, "t1")],
            stop_reason="tool_use",
        )
        # Turn 2: agent writes based on what it read
        write_response = _make_response(
            [_make_tool_block("file_write",
                              {"path": "output.txt", "content": "HELLO"},
                              "t2")],
            stop_reason="tool_use",
        )
        # Turn 3: done
        done_response = _make_response(
            [_make_text_block("Uppercased the file.")],
            stop_reason="end_turn",
        )
        agent.provider.create_message.side_effect = [
            read_response, write_response, done_response
        ]

        agent._run_task("Uppercase input.txt and write to output.txt")

        assert (workspace / "output.txt").read_text() == "HELLO"
        assert agent.provider.create_message.call_count == 3

    def test_multi_tool_use_in_single_turn(self, workspace):
        """Agent calls multiple tools in one response."""
        agent = self._make_agent(workspace)
        (workspace / "a.py").write_text("print('a')")
        (workspace / "b.py").write_text("print('b')")

        # Turn 1: agent reads two files at once
        multi_tool_response = _make_response(
            [
                _make_tool_block("file_read", {"path": "a.py"}, "t1"),
                _make_tool_block("file_read", {"path": "b.py"}, "t2"),
            ],
            stop_reason="tool_use",
        )
        done_response = _make_response(
            [_make_text_block("Read both files.")],
            stop_reason="end_turn",
        )
        agent.provider.create_message.side_effect = [multi_tool_response, done_response]

        agent._run_task("Read a.py and b.py")

        # Should have 2 tool results in the user message
        tool_result_msg = agent.conversation[2]
        assert len(tool_result_msg["content"]) == 2
        assert tool_result_msg["content"][0]["tool_use_id"] == "t1"
        assert tool_result_msg["content"][1]["tool_use_id"] == "t2"

    def test_api_error_breaks_loop_gracefully(self, workspace):
        """Agent loop should not crash on LLM API errors."""
        agent = self._make_agent(workspace)
        agent.provider.create_message.side_effect = RuntimeError("API rate limited")

        agent._run_task("do something")

        # Should have stopped after the error, not crashed
        assert len(agent.conversation) == 1  # only the initial user message

    def test_task_execution_respects_shutdown(self, workspace):
        """Setting _shutdown should stop the loop immediately."""
        agent = self._make_agent(workspace)
        agent._shutdown = True

        agent.provider.create_message.return_value = _make_response(
            [_make_text_block("should not reach")],
            stop_reason="end_turn",
        )

        agent._run_task("anything")

        assert agent.provider.create_message.call_count == 0

    def test_continuous_loop_runs_and_stops(self, workspace):
        """Continuous loop runs _run_next_task per iteration."""
        agent = self._make_agent(workspace, max_iterations=3, loop_delay_seconds=0)

        call_count = 0
        def fake_next():
            nonlocal call_count
            call_count += 1

        with patch.object(agent, "initialize"), \
             patch.object(agent, "_run_next_task", side_effect=fake_next), \
             patch.object(agent, "_write_status"):
            agent.run()

        assert call_count == 3
        assert agent.iteration == 3

    def test_error_in_iteration_continues(self, workspace):
        """Errors in one iteration should not stop subsequent iterations."""
        agent = self._make_agent(workspace, max_iterations=3, loop_delay_seconds=0)

        calls = []
        def flaky_next():
            calls.append(1)
            if len(calls) == 2:
                raise RuntimeError("transient failure")

        with patch.object(agent, "initialize"), \
             patch.object(agent, "_run_next_task", side_effect=flaky_next), \
             patch.object(agent, "_write_status"), \
             patch("OpenClaw.agent.time.sleep"):
            agent.run()

        # All 3 iterations should have been attempted
        assert len(calls) == 3


# ---------------------------------------------------------------------------
# Shell exec timeout handling
# ---------------------------------------------------------------------------

class TestShellTimeout:

    def test_shell_exec_timeout_returns_error(self, workspace):
        config = _make_config(workspace)
        guard = SafetyGuard(config)
        executor = SkillExecutor(config, guard)

        with patch("OpenClaw.skills.executor.subprocess.run",
                   side_effect=subprocess.TimeoutExpired("sleep 999", 120)):
            result = executor.execute("shell_exec", {"command": "echo slow"})

        assert "ERROR" in result
        assert "timed out" in result.lower()


# ---------------------------------------------------------------------------
# Path validation edge cases
# ---------------------------------------------------------------------------

class TestPathValidationEdgeCases:

    def test_similar_prefix_directory_blocked(self, tmp_path):
        """Ensure /workspace-evil is not allowed when workspace is /workspace."""
        workspace = tmp_path / "workspace"
        workspace.mkdir()
        evil = tmp_path / "workspace-evil"
        evil.mkdir()

        config = _make_config(workspace)
        guard = SafetyGuard(config)

        assert guard.validate_path(workspace / "file.py") is True
        assert guard.validate_path(evil / "file.py") is False

    def test_symlink_escape_blocked(self, tmp_path):
        """Symlinks that resolve outside workspace should be blocked."""
        workspace = tmp_path / "workspace"
        workspace.mkdir()
        outside = tmp_path / "outside"
        outside.mkdir()
        (outside / "secret.txt").write_text("secret")

        link = workspace / "escape"
        link.symlink_to(outside)

        config = _make_config(workspace)
        guard = SafetyGuard(config)

        # The symlink resolves to outside the workspace
        assert guard.validate_path(link / "secret.txt") is False


# ---------------------------------------------------------------------------
# Git add error handling
# ---------------------------------------------------------------------------

class TestGitAddErrors:

    def test_git_add_failure_stops_commit(self, workspace):
        config = _make_config(workspace)
        guard = SafetyGuard(config)
        executor = SkillExecutor(config, guard)

        add_fail = MagicMock(stdout="", stderr="fatal: not a git repository", returncode=128)
        with patch("OpenClaw.skills.executor.subprocess.run", return_value=add_fail):
            result = executor.execute("git_commit", {
                "files": ["new.py"],
                "message": "add new file",
            })

        assert "GIT ADD FAILED" in result
        assert "new.py" in result
