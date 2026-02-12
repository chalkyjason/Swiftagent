"""Atomic file I/O utilities for safe IPC between OpenClaw and the MAUI UI.

Prevents partial reads by writing to a temp file and atomically renaming.
"""

import json
import logging
import os
import tempfile
from pathlib import Path

logger = logging.getLogger("openclaw.filelock")


def atomic_write_json(path: Path, data: dict, indent: int = 2) -> None:
    """Write JSON to a file atomically using temp-file + rename.

    This ensures the MAUI UI never reads a half-written status file.
    On POSIX, os.replace is atomic. On Windows, it's as close as we get.
    """
    content = json.dumps(data, indent=indent)
    atomic_write_text(path, content)


def atomic_write_text(path: Path, content: str) -> None:
    """Write text to a file atomically using temp-file + rename."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(
        dir=str(path.parent),
        prefix=f".{path.name}.",
        suffix=".tmp",
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(content)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, str(path))
    except BaseException:
        # Clean up the temp file on any error
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise
