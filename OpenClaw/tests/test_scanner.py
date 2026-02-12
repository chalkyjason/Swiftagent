"""Tests for OpenClaw workspace scanner."""

from pathlib import Path

import pytest

from OpenClaw.config import OpenClawConfig
from OpenClaw.scanner import Finding, RepoScanner


@pytest.fixture
def workspace(tmp_path):
    return tmp_path


@pytest.fixture
def config(workspace):
    return OpenClawConfig(
        workspace_root=workspace,
        api_key="test-key",
    )


@pytest.fixture
def scanner(config):
    return RepoScanner(config)


# ---------------------------------------------------------------------------
# TODO/FIXME scanning
# ---------------------------------------------------------------------------

class TestTodoScanning:
    def test_finds_todo(self, scanner, workspace):
        (workspace / "app.py").write_text("# TODO: add tests\n")
        findings = scanner.scan_all()
        assert len(findings) == 1
        assert "TODO" in findings[0].title
        assert findings[0].priority == "P2"

    def test_finds_fixme(self, scanner, workspace):
        (workspace / "app.py").write_text("# FIXME: broken logic\n")
        findings = scanner.scan_all()
        assert len(findings) == 1
        assert "FIXME" in findings[0].title
        assert findings[0].priority == "P1"

    def test_finds_hack(self, scanner, workspace):
        (workspace / "app.py").write_text("# HACK: workaround\n")
        findings = scanner.scan_all()
        assert len(findings) == 1
        assert "HACK" in findings[0].title
        assert findings[0].priority == "P1"

    def test_finds_slash_comment(self, scanner, workspace):
        (workspace / "app.js").write_text("// TODO: fix later\n")
        findings = scanner.scan_all()
        assert len(findings) == 1

    def test_case_insensitive(self, scanner, workspace):
        (workspace / "app.py").write_text("# todo: lowercase\n")
        findings = scanner.scan_all()
        assert len(findings) == 1

    def test_multiple_todos_in_file(self, scanner, workspace):
        (workspace / "app.py").write_text(
            "# TODO: first\n"
            "code()\n"
            "# FIXME: second\n"
        )
        findings = scanner.scan_all()
        assert len(findings) == 2

    def test_skips_hidden_dirs(self, scanner, workspace):
        hidden = workspace / ".git" / "hooks"
        hidden.mkdir(parents=True)
        (hidden / "pre-commit.py").write_text("# TODO: test\n")
        findings = scanner.scan_all()
        assert len(findings) == 0

    def test_skips_node_modules(self, scanner, workspace):
        nm = workspace / "node_modules" / "pkg"
        nm.mkdir(parents=True)
        (nm / "index.js").write_text("// TODO: test\n")
        findings = scanner.scan_all()
        assert len(findings) == 0

    def test_skips_pycache(self, scanner, workspace):
        pc = workspace / "__pycache__"
        pc.mkdir()
        (pc / "mod.py").write_text("# TODO: test\n")
        findings = scanner.scan_all()
        assert len(findings) == 0


# ---------------------------------------------------------------------------
# Backlog scanning
# ---------------------------------------------------------------------------

class TestBacklogScanning:
    def test_finds_pending_tasks(self, scanner, workspace):
        backlog = workspace / "BACKLOG.md"
        backlog.write_text(
            "# Backlog\n\n"
            "- [ ] [P1] Critical fix\n"
            "- [ ] [P2] Add feature\n"
            "- [x] Done task\n"
        )
        findings = scanner.scan_all()
        assert len(findings) == 2  # only pending
        titles = [f.title for f in findings]
        assert any("Critical fix" in t for t in titles)
        assert any("Add feature" in t for t in titles)

    def test_priority_extraction(self, scanner, workspace):
        backlog = workspace / "BACKLOG.md"
        backlog.write_text("- [ ] [P1] High priority\n")
        findings = scanner.scan_all()
        assert findings[0].priority == "P1"

    def test_default_priority(self, scanner, workspace):
        backlog = workspace / "BACKLOG.md"
        backlog.write_text("- [ ] No priority tag\n")
        findings = scanner.scan_all()
        assert findings[0].priority == "P2"

    def test_no_backlog_file(self, scanner):
        findings = scanner.scan_all()
        assert len(findings) == 0

    def test_empty_backlog(self, scanner, workspace):
        backlog = workspace / "BACKLOG.md"
        backlog.write_text("# Backlog\n\nNothing here.\n")
        findings = scanner.scan_all()
        assert len(findings) == 0


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

class TestReport:
    def test_empty_report(self, scanner):
        scanner.findings = []
        report = scanner.report()
        assert "No issues found" in report

    def test_report_with_findings(self, scanner):
        scanner.findings = [
            Finding("Bug", "P1", "quality", "Description", "file.py", 10),
            Finding("Docs", "P3", "docs", "Missing docs", "README.md"),
        ]
        report = scanner.report()
        assert "2 findings" in report
        assert "P1" in report
        assert "P3" in report
        assert "Bug" in report
        assert "Docs" in report

    def test_report_groups_by_priority(self, scanner):
        scanner.findings = [
            Finding("Low", "P3", "quality", "desc", "a.py"),
            Finding("High", "P1", "quality", "desc", "b.py"),
        ]
        report = scanner.report()
        p1_pos = report.index("P1")
        p3_pos = report.index("P3")
        assert p1_pos < p3_pos  # P1 comes before P3


# ---------------------------------------------------------------------------
# Source file filtering
# ---------------------------------------------------------------------------

class TestSourceFiles:
    def test_includes_python_files(self, scanner, workspace):
        (workspace / "app.py").write_text("")
        files = scanner._source_files()
        assert any(f.name == "app.py" for f in files)

    def test_includes_javascript(self, scanner, workspace):
        (workspace / "app.js").write_text("")
        files = scanner._source_files()
        assert any(f.name == "app.js" for f in files)

    def test_excludes_unsupported_extensions(self, scanner, workspace):
        (workspace / "image.png").write_text("")
        files = scanner._source_files()
        assert not any(f.name == "image.png" for f in files)

    def test_excludes_venv(self, scanner, workspace):
        venv = workspace / "venv" / "lib"
        venv.mkdir(parents=True)
        (venv / "site.py").write_text("")
        files = scanner._source_files()
        assert len(files) == 0
