"""Tests for OpenClaw agent — CostTracker, status writing, and task loop."""

import json
import signal
from datetime import date
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from OpenClaw.config import OpenClawConfig
from OpenClaw.agent import CostTracker, OpenClawAgent, _setup_logging


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_config(workspace: Path) -> OpenClawConfig:
    return OpenClawConfig(
        workspace_root=workspace,
        api_key="test-key",
        daily_budget=5.0,
    )


def _make_text_block(text: str):
    return SimpleNamespace(type="text", text=text)


def _make_tool_block(name: str, inputs: dict, tool_id: str = "tool_1"):
    return SimpleNamespace(type="tool_use", name=name, input=inputs, id=tool_id)


def _make_response(content_blocks, stop_reason="end_turn", input_tokens=10, output_tokens=20):
    return SimpleNamespace(
        content=content_blocks,
        stop_reason=stop_reason,
        usage=SimpleNamespace(input_tokens=input_tokens, output_tokens=output_tokens),
    )


# ---------------------------------------------------------------------------
# CostTracker
# ---------------------------------------------------------------------------

class TestCostTracker:
    def test_initial_state(self, tmp_path):
        config = _make_config(tmp_path)
        tracker = CostTracker(5.0, config)
        assert tracker.cost_today == 0.0
        assert tracker.budget_remaining == 5.0
        assert tracker.over_budget is False

    def test_record_usage(self, tmp_path):
        config = _make_config(tmp_path)
        tracker = CostTracker(5.0, config)
        tracker.record_usage(1_000_000, 0)
        # 1M input tokens * $3/MTok = $3.00
        assert tracker.cost_today == pytest.approx(3.0)
        assert tracker.budget_remaining == pytest.approx(2.0)

    def test_output_tokens_cost(self, tmp_path):
        config = _make_config(tmp_path)
        tracker = CostTracker(5.0, config)
        tracker.record_usage(0, 100_000)
        # 100k output tokens * $15/MTok = $1.50
        assert tracker.cost_today == pytest.approx(1.5)

    def test_over_budget(self, tmp_path):
        config = _make_config(tmp_path)
        tracker = CostTracker(1.0, config)
        tracker.record_usage(0, 100_000)  # $1.50 > $1.00 budget
        assert tracker.over_budget is True
        assert tracker.budget_remaining == 0.0

    def test_day_rollover_resets(self, tmp_path):
        config = _make_config(tmp_path)
        tracker = CostTracker(5.0, config)
        tracker.record_usage(1_000_000, 0)
        assert tracker.cost_today == pytest.approx(3.0)

        # Simulate day change
        tracker.today = date(2020, 1, 1)
        assert tracker.cost_today == 0.0
        assert tracker.input_tokens == 0
        assert tracker.output_tokens == 0

    def test_to_dict(self, tmp_path):
        config = _make_config(tmp_path)
        tracker = CostTracker(5.0, config)
        tracker.record_usage(100, 200)
        d = tracker.to_dict()
        assert "cost_today" in d
        assert d["daily_budget"] == 5.0
        assert d["input_tokens"] == 100
        assert d["output_tokens"] == 200
        assert d["total_tokens"] == 300


# ---------------------------------------------------------------------------
# OpenClawAgent — initialization and status
# ---------------------------------------------------------------------------

class TestAgentInit:
    def test_agent_creates_with_defaults(self, tmp_path):
        config = _make_config(tmp_path)
        with patch("OpenClaw.agent.signal.signal"):
            agent = OpenClawAgent(config)
        assert agent.config is config
        assert agent.iteration == 0
        assert agent._shutdown is False

    def test_write_status_creates_json(self, tmp_path):
        config = _make_config(tmp_path)
        with patch("OpenClaw.agent.signal.signal"):
            agent = OpenClawAgent(config)
        agent._write_status(phase="testing", current_task="test task")

        status = json.loads(config.status_path.read_text())
        assert status["phase"] == "testing"
        assert status["current_task"] == "test task"
        assert status["model"] == config.model
        assert "cost" in status
        assert "agents" in status

    def test_write_status_atomic(self, tmp_path):
        """Status file should always be valid JSON (atomic write)."""
        config = _make_config(tmp_path)
        with patch("OpenClaw.agent.signal.signal"):
            agent = OpenClawAgent(config)

        # Write multiple times rapidly
        for phase in ["idle", "running", "error", "stopped"]:
            agent._write_status(phase=phase)

        # Final file should be valid JSON
        status = json.loads(config.status_path.read_text())
        assert status["phase"] == "stopped"

    def test_signal_handler_sets_shutdown(self, tmp_path):
        config = _make_config(tmp_path)
        with patch("OpenClaw.agent.signal.signal"):
            agent = OpenClawAgent(config)
        agent._handle_signal(signal.SIGINT, None)
        assert agent._shutdown is True


# ---------------------------------------------------------------------------
# OpenClawAgent — task execution loop with mocked API
# ---------------------------------------------------------------------------

class TestRunTask:
    def _setup_agent(self, tmp_path):
        config = _make_config(tmp_path)
        with patch("OpenClaw.agent.signal.signal"):
            agent = OpenClawAgent(config)
        agent.client = MagicMock()
        return agent

    def test_simple_text_response(self, tmp_path):
        agent = self._setup_agent(tmp_path)
        agent.client.messages.create.return_value = _make_response(
            [_make_text_block("Done!")],
            stop_reason="end_turn",
        )

        agent._run_task("say hello")

        assert agent.client.messages.create.call_count == 1
        assert len(agent.conversation) == 2  # user + assistant

    def test_tool_use_then_text(self, tmp_path):
        agent = self._setup_agent(tmp_path)

        # First call: agent uses a tool
        tool_response = _make_response(
            [_make_tool_block("git_status", {})],
            stop_reason="tool_use",
        )
        # Second call: agent gives final text
        text_response = _make_response(
            [_make_text_block("All done.")],
            stop_reason="end_turn",
        )
        agent.client.messages.create.side_effect = [tool_response, text_response]

        agent._run_task("check git status")

        assert agent.client.messages.create.call_count == 2
        # conversation: user, assistant(tool), user(tool_result), assistant(text)
        assert len(agent.conversation) == 4

    def test_budget_stops_loop(self, tmp_path):
        config = _make_config(tmp_path)
        config.daily_budget = 0.001  # very small budget
        with patch("OpenClaw.agent.signal.signal"):
            agent = OpenClawAgent(config)
        agent.client = MagicMock()

        # Response that costs tokens
        agent.client.messages.create.return_value = _make_response(
            [_make_tool_block("git_status", {})],
            stop_reason="tool_use",
            input_tokens=1_000_000,  # $3 — way over $0.001
            output_tokens=0,
        )

        agent._run_task("do something expensive")

        # Should stop after first turn due to budget
        assert agent.client.messages.create.call_count == 1
        assert agent.cost.over_budget is True

    def test_shutdown_stops_loop(self, tmp_path):
        agent = self._setup_agent(tmp_path)
        agent._shutdown = True
        agent.client.messages.create.return_value = _make_response(
            [_make_tool_block("git_status", {})],
            stop_reason="tool_use",
        )

        agent._run_task("anything")

        # Should not even call the API since shutdown is set before first iteration
        assert agent.client.messages.create.call_count == 0


# ---------------------------------------------------------------------------
# OpenClawAgent — main run loop
# ---------------------------------------------------------------------------

class TestRunLoop:
    def test_run_single_task(self, tmp_path):
        config = _make_config(tmp_path)
        with patch("OpenClaw.agent.signal.signal"):
            agent = OpenClawAgent(config)

        with patch.object(agent, "initialize"), \
             patch.object(agent, "_run_task") as mock_run:
            agent.run(task="test task")
            mock_run.assert_called_once_with("test task")

    def test_run_scan_only(self, tmp_path):
        config = _make_config(tmp_path)
        with patch("OpenClaw.agent.signal.signal"):
            agent = OpenClawAgent(config)

        with patch.object(agent, "initialize"), \
             patch.object(agent, "_run_scan") as mock_scan:
            agent.run(scan_only=True)
            mock_scan.assert_called_once()

    def test_continuous_loop_respects_max_iterations(self, tmp_path):
        config = _make_config(tmp_path)
        config.max_iterations = 2
        config.loop_delay_seconds = 0
        with patch("OpenClaw.agent.signal.signal"):
            agent = OpenClawAgent(config)

        call_count = 0

        def fake_run_next():
            nonlocal call_count
            call_count += 1

        with patch.object(agent, "initialize"), \
             patch.object(agent, "_run_next_task", side_effect=fake_run_next), \
             patch.object(agent, "_write_status"):
            agent.run()

        assert call_count == 2
        assert agent.iteration == 2

    def test_continuous_loop_handles_errors(self, tmp_path):
        config = _make_config(tmp_path)
        config.max_iterations = 2
        config.loop_delay_seconds = 0
        with patch("OpenClaw.agent.signal.signal"):
            agent = OpenClawAgent(config)

        with patch.object(agent, "initialize"), \
             patch.object(agent, "_run_next_task", side_effect=RuntimeError("boom")), \
             patch.object(agent, "_write_status"), \
             patch("OpenClaw.agent.time.sleep"):
            # Should not raise — errors are caught
            agent.run()

        assert agent.iteration == 2


# ---------------------------------------------------------------------------
# Setup logging
# ---------------------------------------------------------------------------

class TestSetupLogging:
    def test_creates_log_file(self, tmp_path):
        config = _make_config(tmp_path)
        _setup_logging(config)
        assert config.log_path.exists()
