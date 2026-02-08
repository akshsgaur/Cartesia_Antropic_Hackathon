from __future__ import annotations

import json
import logging
from typing import Any

import asyncio

from anthropic_client import call_claude, parse_json_response
from orchestrator.router import route_and_plan
from orchestrator.prompts import SYNTHESIZER_PROMPT, CHAT_GREETING_PROMPT
from repo.evidence import collect_evidence
from models import SessionState, EvidencePack
from cache import get_cached_response, cache_response
from conversation_flow import (
    get_immediate_acknowledgment, 
    get_thinking_filler, 
    get_ready_transition,
    classify_question_type
)

logger = logging.getLogger(__name__)


async def handle_chat_turn(session: SessionState, user_text: str) -> dict[str, Any] | None:
    """
    Natural conversation flow with immediate acknowledgments:
    1. Instant acknowledgment (under 1 second)
    2. Thinking filler while processing
    3. Ready transition + actual answer
    """
    try:
        logger.info("Chat turn started for: %s", user_text[:50])
        
        # Step 0: Check cache first for instant responses
        session_context = {
            "repo_path": session.repo_path,
            "recent_turns_hash": str(hash(str(session.recent_turns()[-3:])))
        }
        
        cached_response = get_cached_response(user_text, session_context)
        if cached_response:
            logger.info("Returning cached response for: %s", user_text[:50])
            return cached_response

        # Step 1: Get immediate acknowledgment (instant!)
        question_type = classify_question_type(user_text)
        immediate_response = get_immediate_acknowledgment(user_text, question_type)
        
        # For simple questions, return immediate response without processing
        if question_type in ["greeting", "what_is_this", "features"]:
            response = {
                "voice_answer": immediate_response,
                "detailed_answer": immediate_response,
                "evidence": EvidencePack(),
                "glossary_updates": {},
                "conversation_stage": "complete"
            }
            cache_response(user_text, session_context, response)
            return response

        # Step 2: Start processing in background
        processing_task = asyncio.create_task(
            _process_question_with_evidence(session, user_text)
        )
        
        # Step 3: Return immediate acknowledgment + thinking filler
        response = {
            "voice_answer": immediate_response,
            "detailed_answer": "",  # Will be updated
            "evidence": EvidencePack(),
            "glossary_updates": {},
            "conversation_stage": "thinking",
            "processing_task": processing_task
        }
        
        return response

    except Exception as e:
        logger.error("Chat pipeline error: %s", e, exc_info=True)
        return {
            "voice_answer": "Oh, sorry about that! Let me try again.",
            "detailed_answer": f"Error: {e}",
            "evidence": EvidencePack(),
            "glossary_updates": {},
        }


async def _process_question_with_evidence(session: SessionState, user_text: str) -> dict[str, Any]:
    """Process the question in background with evidence collection."""
    logger.info("Starting background processing for: %s", user_text[:50])
    try:
        # Route and plan
        logger.info("Calling route_and_plan...")
        plan = await route_and_plan(session, user_text)
        logger.info("Route and plan complete: intent=%s", plan.get("intent"))
        
        # Quick evidence collection (limited for speed)
        evidence_task = asyncio.create_task(_collect_evidence_background(
            session.repo_path, plan["rg_patterns"], plan["candidate_files"]
        ))
        
        # Generate thinking filler
        thinking_filler = get_thinking_filler()
        
        # Wait for evidence (with timeout)
        evidence = EvidencePack()
        try:
            evidence = await asyncio.wait_for(evidence_task, timeout=3.0)  # 3 second timeout
        except asyncio.TimeoutError:
            logger.warning("Evidence collection timed out, proceeding without evidence")
        
        # Generate detailed answer
        logger.info("Generating detailed answer...")
        detailed_answer = await _generate_detailed_answer(
            session, user_text, plan, evidence
        )
        logger.info("Detailed answer generated: %s...", detailed_answer[:100])
        
        # Get ready transition
        transition = get_ready_transition()
        
        logger.info("Background processing complete, returning result")
        return {
            "thinking_filler": thinking_filler,
            "transition": transition,
            "detailed_answer": detailed_answer,
            "evidence": evidence,
            "conversation_stage": "ready"
        }
        
    except Exception as e:
        logger.error("Background processing error: %s", e, exc_info=True)
        return {
            "thinking_filler": "Let me try a different approach...",
            "transition": "Here's what I can tell you:",
            "detailed_answer": f"I encountered an issue: {e}",
            "evidence": EvidencePack(),
            "conversation_stage": "ready"
        }


async def _handle_simple_chat(session: SessionState, user_text: str) -> dict[str, Any]:
    """Handle greetings and off-topic messages — uses Haiku for speed."""
    repo_name = session.repo_path.rstrip("/").split("/")[-1] if session.repo_path else "unknown"

    prompt = CHAT_GREETING_PROMPT.format(
        user_text=user_text,
        repo_name=repo_name,
        mode=session.mode,
    )

    try:
        result = await call_claude(prompt, max_tokens=800, model="claude-haiku-4-5-20251001")
        logger.info("Router received Claude response: %s...", result[:100])
        data = parse_json_response(result)
        logger.info("Router parsed response: intent=%s", data.get("intent"))
        return {
            "voice_answer": data.get("voice_answer", "Hey there!"),
            "detailed_answer": data.get("detailed_answer", ""),
            "evidence": EvidencePack(),
            "glossary_updates": {},
        }
    except Exception as e:
        logger.error("Simple chat error: %s", e)
        return {
            "voice_answer": "Hey! I'm here to help you explore this codebase. Ask me anything!",
            "detailed_answer": "Ready to help with code exploration.",
            "evidence": EvidencePack(),
            "glossary_updates": {},
        }


async def _collect_evidence_background(
    repo_path: str, 
    rg_patterns: list[str], 
    candidate_files: list[str] | None = None
) -> EvidencePack:
    """Collect evidence in background with optimized search limits."""
    if not repo_path or (not rg_patterns and not candidate_files):
        return EvidencePack()
    
    # Limit evidence collection for speed
    return await collect_evidence(
        repo_path=repo_path,
        rg_patterns=rg_patterns[:3],  # Limit to 3 patterns max
        candidate_files=candidate_files[:2] if candidate_files else None,  # Limit to 2 files max
        max_snippets=3,  # Reduce from 5 to 3 snippets
    )


async def _generate_voice_answer(
    session: SessionState, 
    user_text: str, 
    plan: dict[str, Any]
) -> str:
    """Generate quick voice answer with minimal context for immediate response."""
    # Use Haiku for speed with minimal context but include repo awareness
    repo_name = session.repo_path.rstrip("/").split("/")[-1] if session.repo_path else "this repository"
    
    prompt = f"""Based on the user's question about {repo_name}, provide a brief, helpful voice answer (max 2 sentences).

Question: {user_text}
Intent: {plan.get('intent', 'unknown')}
Repository: {repo_name}

Be helpful and specific to the context. If asking about features, describe what you see. If asking what this is, identify it clearly."""

    try:
        result = await call_claude(
            prompt, 
            max_tokens=100,  # Very short response
            model="claude-haiku-4-5-20251001"
        )
        return result.strip()
    except Exception as e:
        logger.error("Voice answer generation error: %s", e)
        return f"I'm exploring {repo_name} to help answer that."


async def _generate_detailed_answer(
    session: SessionState,
    user_text: str,
    plan: dict[str, Any],
    evidence: EvidencePack
) -> str:
    """Generate detailed answer with full evidence context."""
    curriculum_text = ""
    if session.curriculum:
        curriculum_text = json.dumps(session.curriculum.to_dict(), indent=2)

    recent = "\n".join(
        f"{t['role']}: {t['content'][:200]}" for t in session.recent_turns()
    )

    prompt = SYNTHESIZER_PROMPT.format(
        curriculum=curriculum_text or "(no curriculum)",
        question=user_text,
        evidence=evidence.to_prompt_text(),
        recent_turns=recent or "(start of conversation)",
    )

    try:
        result = await call_claude(prompt, max_tokens=1000)  # Reduced from 1500
        data = parse_json_response(result)
        
        glossary_updates = data.get("glossary_updates", {})
        if glossary_updates and isinstance(glossary_updates, dict):
            session.glossary.update(glossary_updates)
            
        return data.get("detailed_answer", "")
    except Exception as e:
        logger.error("Detailed answer generation error: %s", e)
        return f"I encountered an issue: {e}"
