"""Improvement scanner — analyzes the repo and reports findings.

Can be run standalone or as part of the agent loop to discover
what needs improvement before the agent begins work.
"""

import re
from dataclasses import dataclass, field
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
    """Static analysis scanner for the Swiftagent repo."""

    def __init__(self, config: OpenClawConfig):
        self.config = config
        self.findings: list[Finding] = []

    def scan_all(self) -> list[Finding]:
        """Run all scans and return findings."""
        self.findings = []
        self._scan_todos()
        self._scan_force_unwraps()
        self._scan_empty_catches()
        self._scan_missing_docs()
        self._scan_missing_tests()
        self._scan_backlog()
        return self.findings

    def _swift_files(self) -> list[Path]:
        """Get all Swift source files, excluding hidden dirs."""
        files = []
        for f in self.config.workspace_root.rglob("*.swift"):
            if any(p.startswith(".") for p in f.parts):
                continue
            if "Tests" in f.parts:
                continue
            files.append(f)
        return sorted(files)

    def _test_dirs(self) -> list[Path]:
        """Find test directories in packages."""
        dirs = []
        for pkg in self.config.packages_dir.iterdir():
            if not pkg.is_dir():
                continue
            test_dir = pkg / "Tests"
            dirs.append(test_dir)
        return dirs

    def _scan_todos(self):
        """Find TODO, FIXME, HACK comments in code."""
        pattern = re.compile(r"//\s*(TODO|FIXME|HACK|XXX)[:\s]*(.*)", re.IGNORECASE)
        for f in self._swift_files():
            for i, line in enumerate(f.read_text().split("\n"), 1):
                m = pattern.search(line)
                if m:
                    tag = m.group(1).upper()
                    msg = m.group(2).strip()
                    self.findings.append(Finding(
                        title=f"{tag}: {msg[:60]}",
                        priority="P2" if tag == "TODO" else "P1",
                        category="quality",
                        description=f"{tag} comment at {f.name}:{i}: {msg}",
                        file=str(f.relative_to(self.config.workspace_root)),
                        line=i,
                    ))

    def _scan_force_unwraps(self):
        """Find force unwrap (!) usage outside of tests."""
        pattern = re.compile(r"\w+!\s*[^=]")
        # Heuristic: skip IBOutlet-style patterns and common false positives
        skip = re.compile(r"(IBOutlet|@objc|#if|#endif|import|///|//)")
        for f in self._swift_files():
            for i, line in enumerate(f.read_text().split("\n"), 1):
                if skip.search(line):
                    continue
                if pattern.search(line) and "!" in line:
                    # Avoid false positives from != and negation
                    stripped = line.strip()
                    if stripped.startswith("//") or "!=" in stripped:
                        continue
                    if "!" not in stripped.replace("!=", ""):
                        continue
                    self.findings.append(Finding(
                        title=f"Force unwrap in {f.name}",
                        priority="P2",
                        category="quality",
                        description=f"Potential force unwrap at line {i}: {stripped[:80]}",
                        file=str(f.relative_to(self.config.workspace_root)),
                        line=i,
                    ))

    def _scan_empty_catches(self):
        """Find empty catch blocks."""
        for f in self._swift_files():
            content = f.read_text()
            # Simple heuristic: "catch" followed by empty braces
            for m in re.finditer(r"catch\s*(\w+\s*)?\{[\s]*\}", content):
                line_num = content[:m.start()].count("\n") + 1
                self.findings.append(Finding(
                    title=f"Empty catch block in {f.name}",
                    priority="P2",
                    category="quality",
                    description=f"Empty catch block at line {line_num}. Errors should be logged or handled.",
                    file=str(f.relative_to(self.config.workspace_root)),
                    line=line_num,
                ))

    def _scan_missing_docs(self):
        """Find public declarations without documentation comments."""
        public_decl = re.compile(
            r"^\s*(public\s+)(func|var|let|class|struct|enum|protocol|init)\s+(\w+)"
        )
        for f in self._swift_files():
            lines = f.read_text().split("\n")
            for i, line in enumerate(lines):
                m = public_decl.match(line)
                if not m:
                    continue
                # Check if preceded by a doc comment
                has_doc = False
                for j in range(max(0, i - 3), i):
                    if "///" in lines[j] or "/**" in lines[j]:
                        has_doc = True
                        break
                if not has_doc:
                    name = m.group(3)
                    kind = m.group(2)
                    self.findings.append(Finding(
                        title=f"Missing docs: {kind} {name}",
                        priority="P3",
                        category="docs",
                        description=f"Public {kind} '{name}' in {f.name}:{i+1} has no documentation comment.",
                        file=str(f.relative_to(self.config.workspace_root)),
                        line=i + 1,
                    ))

    def _scan_missing_tests(self):
        """Find packages without test directories or test files."""
        if not self.config.packages_dir.exists():
            return

        for pkg in self.config.packages_dir.iterdir():
            if not pkg.is_dir():
                continue
            test_dir = pkg / "Tests"
            if not test_dir.exists():
                self.findings.append(Finding(
                    title=f"No tests for {pkg.name}",
                    priority="P1",
                    category="testing",
                    description=f"Package {pkg.name} has no Tests/ directory. Add unit tests.",
                    file=str(pkg.relative_to(self.config.workspace_root)),
                ))
            else:
                test_files = list(test_dir.rglob("*.swift"))
                if not test_files:
                    self.findings.append(Finding(
                        title=f"Empty test directory for {pkg.name}",
                        priority="P1",
                        category="testing",
                        description=f"Package {pkg.name}/Tests/ exists but has no .swift test files.",
                        file=str(test_dir.relative_to(self.config.workspace_root)),
                    ))

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
