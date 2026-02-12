"""Tests for OpenClaw configuration."""

import os
from pathlib import Path

import pytest

from OpenClaw.config import OpenClawConfig


@pytest.fixture
def workspace(tmp_path):
    return tmp_path


class TestConfigDefaults:
    def test_default_model(self):
        cfg = OpenClawConfig()
        assert "claude" in cfg.model

    def test_default_budget(self):
        cfg = OpenClawConfig()
        assert cfg.daily_budget == 5.0

    def test_default_safety_settings(self):
        cfg = OpenClawConfig()
        assert cfg.sandbox_enabled is True
        assert cfg.safe_delete is True
        assert cfg.whitelist_only is True

    def test_max_file_size(self):
        cfg = OpenClawConfig()
        assert cfg.max_file_size_bytes == 1_048_576

    def test_max_files_per_session(self):
        cfg = OpenClawConfig()
        assert cfg.max_files_per_session == 100

    def test_default_iterations(self):
        cfg = OpenClawConfig()
        assert cfg.max_iterations == 20
        assert cfg.max_retries_per_task == 3


class TestConfigPaths:
    def test_backlog_path(self, workspace):
        cfg = OpenClawConfig(workspace_root=workspace)
        assert cfg.backlog_path == workspace / "BACKLOG.md"

    def test_log_path(self, workspace):
        cfg = OpenClawConfig(workspace_root=workspace)
        assert cfg.log_path == workspace / "openclaw.log"

    def test_checkpoint_dir(self, workspace):
        cfg = OpenClawConfig(workspace_root=workspace)
        assert cfg.checkpoint_dir == workspace / ".openclaw_checkpoints"

    def test_trash_dir(self, workspace):
        cfg = OpenClawConfig(workspace_root=workspace)
        assert cfg.trash_dir == workspace / ".openclaw_trash"

    def test_tasks_dir(self, workspace):
        cfg = OpenClawConfig(workspace_root=workspace)
        assert cfg.tasks_dir == workspace / ".openclaw_tasks"

    def test_status_path(self, workspace):
        cfg = OpenClawConfig(workspace_root=workspace)
        assert cfg.status_path == workspace / "openclaw_status.json"

    def test_skills_path(self, workspace):
        cfg = OpenClawConfig(workspace_root=workspace)
        assert cfg.skills_path == workspace / "openclaw_skills.json"


class TestConfigValidation:
    def test_missing_api_key(self, workspace):
        cfg = OpenClawConfig(workspace_root=workspace, api_key="")
        errors = cfg.validate()
        assert any("ANTHROPIC_API_KEY" in e for e in errors)

    def test_nonexistent_workspace(self):
        cfg = OpenClawConfig(
            workspace_root=Path("/nonexistent/path/that/does/not/exist"),
            api_key="test-key",
        )
        errors = cfg.validate()
        assert any("does not exist" in e for e in errors)

    def test_negative_budget(self, workspace):
        cfg = OpenClawConfig(
            workspace_root=workspace,
            api_key="test-key",
            daily_budget=-1.0,
        )
        errors = cfg.validate()
        assert any("budget" in e.lower() for e in errors)

    def test_zero_budget(self, workspace):
        cfg = OpenClawConfig(
            workspace_root=workspace,
            api_key="test-key",
            daily_budget=0.0,
        )
        errors = cfg.validate()
        assert any("budget" in e.lower() for e in errors)

    def test_valid_config(self, workspace):
        cfg = OpenClawConfig(
            workspace_root=workspace,
            api_key="test-key",
            daily_budget=5.0,
        )
        errors = cfg.validate()
        assert errors == []

    def test_multiple_errors(self):
        cfg = OpenClawConfig(
            workspace_root=Path("/nonexistent"),
            api_key="",
            daily_budget=-1.0,
        )
        errors = cfg.validate()
        assert len(errors) >= 2  # at least api_key + workspace


class TestConfigCosts:
    def test_input_token_cost(self):
        cfg = OpenClawConfig()
        assert cfg.cost_per_input_token == pytest.approx(3.0 / 1_000_000)

    def test_output_token_cost(self):
        cfg = OpenClawConfig()
        assert cfg.cost_per_output_token == pytest.approx(15.0 / 1_000_000)
