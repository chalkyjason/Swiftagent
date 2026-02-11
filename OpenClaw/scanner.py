"""Workspace scanner — analyzes the repo and reports findings.

General-purpose scanner that works with any codebase, not tied to Swift.
"""

import re
from dataclasses import dataclass
from pathlib import Path

from .config import OpenClawConfig


@dataclass
class Finding:
    title: str
    priority: str  # P1, P2, P3
    category: str  # quality, testing, docs, feature, bug, refactor
    description: str
    file: str
    line: int = 0


class RepoScanner:
    """Static analysis scanner for any workspace."""

    SCAN_EXTENSIONS = {
        ".py", ".js", ".ts", ".jsx", ".tsx", ".go", ".rs",
        ".java", ".kt", ".cs", ".rb", ".php", ".sh", ".yaml",
        ".yml", ".toml", ".json", ".md",
    }

    def __init__(self, config: OpenClawConfig):
        self.config = config
        self.findings: list[Finding] = []

    def scan_all(self) -> list[Finding]:
        """Run all scans and return findings."""
        self.findings = []
        self._scan_todos()
        self._scan_backlog()
        return self.findings

    def _source_files(self) -> list[Path]:
        """Get all source files, excluding hidden dirs and node_modules."""
        files = []
        skip_dirs = {".git", ".openclaw_trash", ".openclaw_checkpoints",
                     "node_modules", "__pycache__", ".venv", "venv"}
        for f in self.config.workspace_root.rglob("*"):
            if any(p in skip_dirs for p in f.parts):
                continue
            if f.is_file() and f.suffix in self.SCAN_EXTENSIONS:
                files.append(f)
        return sorted(files)

    def _scan_todos(self):
        """Find TODO, FIXME, HACK comments in code."""
        pattern = re.compile(
            r"(?://|#)\s*(TODO|FIXME|HACK|XXX)[:\s]*(.*)", re.IGNORECASE
        )
        for f in self._source_files():
            try:
                for i, line in enumerate(f.read_text(errors="ignore").split("\n"), 1):
                    m = pattern.search(line)
                    if m:
                        tag = m.group(1).upper()
                        msg = m.group(2).strip()
                        self.findings.append(Finding(
                            title=f"{tag}: {msg[:60]}",
                            priority="P2" if tag == "TODO" else "P1",
                            category="quality",
                            description=f"{tag} at {f.name}:{i}: {msg}",
                            file=str(f.relative_to(self.config.workspace_root)),
                            line=i,
                        ))
            except (PermissionError, OSError):
                continue

    def _scan_backlog(self):
        """Parse BACKLOG.md for pending tasks."""
        if not self.config.backlog_path.exists():
            return

        content = self.config.backlog_path.read_text()
        for line in content.split("\n"):
            line = line.strip()
            if not line.startswith("- [ ]"):
                continue

            priority = "P2"
            for tag in ["[P1]", "[P2]", "[P3]"]:
                if tag in line:
                    priority = tag.strip("[]")
                    break

            desc = line.replace("- [ ]", "").strip()
            for tag in ["[P1]", "[P2]", "[P3]"]:
                desc = desc.replace(tag, "").strip()

            self.findings.append(Finding(
                title=f"Backlog: {desc[:60]}",
                priority=priority,
                category="feature",
                description=f"Pending task from BACKLOG.md: {desc}",
                file="BACKLOG.md",
            ))

    def report(self) -> str:
        """Generate a human-readable report of findings."""
        if not self.findings:
            return "No issues found."

        by_priority = {"P1": [], "P2": [], "P3": []}
        for f in self.findings:
            by_priority.get(f.priority, by_priority["P3"]).append(f)

        lines = [f"# Scan Results — {len(self.findings)} findings\n"]
        for p in ["P1", "P2", "P3"]:
            items = by_priority[p]
            if not items:
                continue
            lines.append(f"\n## {p} — {len(items)} items\n")
            for f in items:
                lines.append(f"- **[{f.category}]** {f.title}")
                lines.append(f"  {f.file}:{f.line}" if f.line else f"  {f.file}")
                lines.append(f"  {f.description}\n")

        return "\n".join(lines)
