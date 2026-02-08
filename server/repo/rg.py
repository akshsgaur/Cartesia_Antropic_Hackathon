from __future__ import annotations

import asyncio
import json
import logging

from models import RgMatch

logger = logging.getLogger(__name__)


async def rg_search(
    pattern: str,
    repo_path: str,
    max_results: int = 20,
    file_glob: str | None = None,
) -> list[RgMatch]:
    """Run ripgrep and return structured matches."""
    cmd = ["rg", "--json", "-m", str(max_results), "--max-filesize", "1M"]
    if file_glob:
        cmd.extend(["-g", file_glob])
    cmd.extend([pattern, repo_path])

    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=10)
    except asyncio.TimeoutError:
        logger.warning("rg timed out for pattern: %s", pattern)
        return []
    except FileNotFoundError:
        logger.error("ripgrep (rg) not found on PATH")
        return []

    matches: list[RgMatch] = []
    for line in stdout.decode("utf-8", errors="replace").splitlines():
        try:
            data = json.loads(line)
        except json.JSONDecodeError:
            continue

        if data.get("type") != "match":
            continue

        match_data = data.get("data", {})
        path_data = match_data.get("path", {})
        path = path_data.get("text", "")

        # Make path relative to repo_path
        if path.startswith(repo_path):
            path = path[len(repo_path):].lstrip("/")

        line_number = match_data.get("line_number", 0)

        lines = match_data.get("lines", {})
        line_text = lines.get("text", "").strip()

        matches.append(RgMatch(
            path=path,
            line_number=line_number,
            line_text=line_text,
        ))

        if len(matches) >= max_results:
            break

    return matches
