from __future__ import annotations

import json
import logging
from typing import Any

from anthropic_client import call_claude, parse_json_response
from orchestrator.prompts import ROUTER_PLANNER_PROMPT
from models import SessionState

logger = logging.getLogger(__name__)


async def route_and_plan(session: SessionState, user_text: str) -> dict[str, Any]:
    """Classify intent and generate search plan. Returns parsed JSON."""
    curriculum_text = ""
    if session.curriculum:
        curriculum_text = json.dumps(session.curriculum.to_dict(), indent=2)

    repo_scan_text = session.repo_scan.summary() if session.repo_scan else "(no scan)"

    recent = "\n".join(
        f"{t['role']}: {t['content'][:200]}" for t in session.recent_turns()
    )

    prompt = ROUTER_PLANNER_PROMPT.format(
        curriculum=curriculum_text or "(no curriculum loaded)",
        repo_scan=repo_scan_text,
        recent_turns=recent or "(start of conversation)",
        user_text=user_text,
    )

    try:
        result = await call_claude(prompt, max_tokens=800, model="claude-haiku-4-5-20251001")
        data = parse_json_response(result)
        return {
            "intent": data.get("intent", "code_question"),
            "rg_patterns": data.get("rg_patterns", []),
            "candidate_files": data.get("candidate_files", []),
            "search_notes": data.get("search_notes", ""),
        }
    except Exception as e:
        logger.error("Router failed: %s", e)
        return {
            "intent": "code_question",
            "rg_patterns": [user_text.split()[-1]] if user_text.split() else [],
            "candidate_files": [],
            "search_notes": "Router failed, using fallback",
        }
