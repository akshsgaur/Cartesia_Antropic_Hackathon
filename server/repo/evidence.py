from __future__ import annotations

import logging
from typing import Any

from models import EvidencePack, RgMatch
from repo.rg import rg_search
from repo.file import open_around_match

logger = logging.getLogger(__name__)


async def collect_evidence(
    repo_path: str,
    rg_patterns: list[str],
    candidate_files: list[str] | None = None,
    max_snippets: int = 5,
) -> EvidencePack:
    """Run rg searches and open snippets for top hits."""
    pack = EvidencePack()
    seen_files: set[str] = set()

    # Run rg searches
    for pattern in rg_patterns:
        matches = await rg_search(pattern, repo_path)
        pack.matches.extend(matches)

        # Open snippets for top unique file hits
        for m in matches:
            if m.path in seen_files:
                continue
            if len(pack.snippets) >= max_snippets:
                break
            seen_files.add(m.path)
            snippet = open_around_match(repo_path, m.path, m.line_number)
            if snippet:
                pack.snippets.append(snippet)

    # Open candidate files if provided
    if candidate_files:
        for fpath in candidate_files:
            if fpath in seen_files:
                continue
            if len(pack.snippets) >= max_snippets:
                break
            seen_files.add(fpath)
            snippet = open_around_match(repo_path, fpath, 1, radius=25)
            if snippet:
                pack.snippets.append(snippet)

    return pack
