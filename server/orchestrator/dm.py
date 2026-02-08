from __future__ import annotations

import json
import logging

from anthropic_client import call_claude, parse_json_response
from orchestrator.prompts import QUEST_GENERATOR_PROMPT, QUEST_GRADER_PROMPT
from orchestrator.quest_templates import QUEST_TEMPLATES
from repo.evidence import collect_evidence
from models import SessionState, Quest, QuestResult, EvidencePack

logger = logging.getLogger(__name__)


async def start_quest(session: SessionState) -> Quest | None:
    """Generate the next quest for the engineer."""
    available = [t for t in QUEST_TEMPLATES if t["id"] not in session.completed_quests]
    if not available:
        session.completed_quests.clear()
        available = QUEST_TEMPLATES

    template = available[0]

    curriculum_text = ""
    if session.curriculum:
        curriculum_text = json.dumps(session.curriculum.to_dict(), indent=2)

    repo_scan_text = session.repo_scan.summary() if session.repo_scan else "(no scan)"

    prompt = QUEST_GENERATOR_PROMPT.format(
        curriculum=curriculum_text or "(no curriculum)",
        repo_scan=repo_scan_text,
        completed_quests=", ".join(session.completed_quests) or "none",
        template=template["template"],
        difficulty=session.quest_level,
    )

    try:
        result = await call_claude(prompt, max_tokens=800)
        data = parse_json_response(result)

        quest = Quest(
            id=template["id"],
            title=data.get("title", template["template"][:50]),
            description=data.get("description", template["template"]),
            difficulty=session.quest_level,
            rg_patterns=data.get("rg_patterns", []),
            keywords=data.get("keywords", []),
            file_hints=data.get("file_hints", []),
            expected_findings=data.get("expected_findings", []),
        )
        return quest

    except Exception as e:
        logger.error("Quest generation failed: %s", e)
        return Quest(
            id=template["id"],
            title=template["template"][:60],
            description=template["template"],
            difficulty=session.quest_level,
            rg_patterns=[],
            keywords=[],
            file_hints=[],
            expected_findings=[],
        )


async def handle_dm_turn(session: SessionState, user_answer: str) -> QuestResult | None:
    """Grade the user's answer to the current quest."""
    quest = session.current_quest
    if not quest:
        return None

    answer_words = [w for w in user_answer.split() if len(w) > 3]
    search_patterns = quest.rg_patterns + answer_words[:2]

    evidence = EvidencePack()
    if session.repo_path and search_patterns:
        evidence = await collect_evidence(
            repo_path=session.repo_path,
            rg_patterns=search_patterns,
            candidate_files=quest.file_hints,
        )

    prompt = QUEST_GRADER_PROMPT.format(
        quest_title=quest.title,
        quest_description=quest.description,
        expected_findings=", ".join(quest.expected_findings),
        user_answer=user_answer,
        evidence=evidence.to_prompt_text(),
    )

    try:
        result_text = await call_claude(prompt, max_tokens=500)
        data = parse_json_response(result_text)
        grade = data.get("grade", "fail")
        score = data.get("score", 0)
        feedback = data.get("feedback", "Keep exploring!")

    except Exception as e:
        logger.error("Quest grading failed: %s", e)
        grade = "partial"
        score = 50
        feedback = "I had trouble grading that. Let's move on to the next quest!"

    result = QuestResult(
        quest_id=quest.id,
        grade=grade,
        score=score,
        feedback=feedback,
        evidence=evidence,
    )

    # Update difficulty tracking
    if grade == "pass":
        session.consecutive_passes += 1
        session.consecutive_fails = 0
        session.completed_quests.append(quest.id)
        if session.consecutive_passes >= 2 and session.quest_level < 3:
            session.quest_level += 1
            session.consecutive_passes = 0
    elif grade == "fail":
        session.consecutive_fails += 1
        session.consecutive_passes = 0
        if session.consecutive_fails >= 2 and session.quest_level > 1:
            session.quest_level -= 1
            session.consecutive_fails = 0

    session.current_quest = None
    return result
