from __future__ import annotations

import os
import logging
from pathlib import Path

from models import FileSnippet

logger = logging.getLogger(__name__)


def file_exists(repo_path: str, file_path: str) -> bool:
    full_path = os.path.join(repo_path, file_path)
    return os.path.isfile(full_path)


def open_snippet(repo_path: str, file_path: str, start: int, end: int) -> FileSnippet | None:
    """Read lines [start, end] from a file (1-indexed)."""
    full_path = os.path.join(repo_path, file_path)
    if not os.path.isfile(full_path):
        return None

    try:
        with open(full_path, "r", errors="replace") as f:
            lines = f.readlines()

        start = max(1, start)
        end = min(len(lines), end)
        text = "".join(lines[start - 1:end])

        return FileSnippet(
            path=file_path,
            start=start,
            end=end,
            text=text,
        )
    except Exception as e:
        logger.error("Failed to read %s: %s", full_path, e)
        return None


def open_around_match(repo_path: str, file_path: str, line: int, radius: int = 10) -> FileSnippet | None:
    """Read a snippet centered around a specific line."""
    start = max(1, line - radius)
    end = line + radius
    return open_snippet(repo_path, file_path, start, end)
