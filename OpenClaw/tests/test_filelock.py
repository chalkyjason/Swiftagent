"""Tests for atomic file I/O utilities."""

import json
from pathlib import Path

import pytest

from OpenClaw.filelock import atomic_write_json, atomic_write_text


class TestAtomicWriteText:
    def test_creates_file(self, tmp_path):
        path = tmp_path / "test.txt"
        atomic_write_text(path, "hello")
        assert path.read_text() == "hello"

    def test_overwrites_existing(self, tmp_path):
        path = tmp_path / "test.txt"
        path.write_text("old")
        atomic_write_text(path, "new")
        assert path.read_text() == "new"

    def test_creates_parent_dirs(self, tmp_path):
        path = tmp_path / "sub" / "dir" / "file.txt"
        atomic_write_text(path, "nested")
        assert path.read_text() == "nested"

    def test_no_temp_files_left(self, tmp_path):
        path = tmp_path / "clean.txt"
        atomic_write_text(path, "data")
        files = list(tmp_path.iterdir())
        assert len(files) == 1
        assert files[0].name == "clean.txt"

    def test_content_is_always_complete(self, tmp_path):
        """Even after multiple rapid writes, file content is always valid."""
        path = tmp_path / "rapid.txt"
        for i in range(20):
            atomic_write_text(path, f"iteration-{i}")
        assert path.read_text() == "iteration-19"


class TestAtomicWriteJson:
    def test_writes_valid_json(self, tmp_path):
        path = tmp_path / "status.json"
        data = {"phase": "running", "cost": 1.23}
        atomic_write_json(path, data)
        loaded = json.loads(path.read_text())
        assert loaded == data

    def test_json_is_indented(self, tmp_path):
        path = tmp_path / "pretty.json"
        atomic_write_json(path, {"key": "value"}, indent=4)
        text = path.read_text()
        assert "    " in text  # 4-space indent

    def test_overwrites_atomically(self, tmp_path):
        path = tmp_path / "status.json"
        atomic_write_json(path, {"v": 1})
        atomic_write_json(path, {"v": 2})
        loaded = json.loads(path.read_text())
        assert loaded["v"] == 2

    def test_handles_list_data(self, tmp_path):
        path = tmp_path / "skills.json"
        data = [{"name": "git_status"}, {"name": "file_read"}]
        atomic_write_json(path, data)
        loaded = json.loads(path.read_text())
        assert len(loaded) == 2
        assert loaded[0]["name"] == "git_status"
