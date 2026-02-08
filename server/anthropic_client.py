from __future__ import annotations

import json
import logging
import re
from typing import Any

import anthropic

from config import ANTHROPIC_API_KEY

logger = logging.getLogger(__name__)

_client: anthropic.AsyncAnthropic | None = None


def _get_client() -> anthropic.AsyncAnthropic:
    global _client
    if _client is None:
        _client = anthropic.AsyncAnthropic(api_key=ANTHROPIC_API_KEY)
    return _client


async def call_claude(
    prompt: str,
    system: str = "",
    max_tokens: int = 1500,
    model: str = "claude-sonnet-4-5-20250929",
) -> str:
    """Single Claude API call. Returns the text response."""
    client = _get_client()

    messages = [{"role": "user", "content": prompt}]

    kwargs: dict = {
        "model": model,
        "max_tokens": max_tokens,
        "messages": messages,
    }
    if system:
        kwargs["system"] = system

    try:
        response = await client.messages.create(**kwargs)
        text = ""
        for block in response.content:
            if hasattr(block, "text"):
                text += block.text
        return text
    except Exception as e:
        logger.error("Claude API error: %s", e, exc_info=True)
        raise


def parse_json_response(text: str) -> dict[str, Any]:
    """Robustly parse JSON from Claude's response, handling common issues."""
    # Extract JSON from fenced code blocks
    json_str = text
    if "```json" in text:
        json_str = text.split("```json")[1].split("```")[0]
    elif "```" in text:
        json_str = text.split("```")[1].split("```")[0]
    json_str = json_str.strip()

    # Try strict parse first
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        pass

    # Try fixing truncated JSON by closing open braces/brackets
    try:
        fixed = json_str
        open_braces = fixed.count("{") - fixed.count("}")
        open_brackets = fixed.count("[") - fixed.count("]")
        # If inside a string, close it
        if fixed.count('"') % 2 == 1:
            fixed += '"'
        fixed += "]" * open_brackets
        fixed += "}" * open_braces
        return json.loads(fixed)
    except json.JSONDecodeError:
        pass

    # Fallback: extract known fields with regex
    logger.warning("JSON parse failed, using regex fallback. Raw: %s", text[:500])
    result: dict[str, Any] = {}

    for field in ("voice_answer", "detailed_answer", "intent", "grade", "feedback", "title", "description"):
        match = re.search(rf'"{field}"\s*:\s*"((?:[^"\\]|\\.)*)"', text, re.DOTALL)
        if match:
            result[field] = match.group(1).replace('\\"', '"').replace("\\n", "\n")

    # Extract numeric fields
    for field in ("score",):
        match = re.search(rf'"{field}"\s*:\s*(\d+)', text)
        if match:
            result[field] = int(match.group(1))

    # Extract arrays
    for field in ("rg_patterns", "candidate_files", "keywords", "file_hints", "expected_findings", "goals"):
        match = re.search(rf'"{field}"\s*:\s*\[(.*?)\]', text, re.DOTALL)
        if match:
            items = re.findall(r'"((?:[^"\\]|\\.)*)"', match.group(1))
            result[field] = items

    # Extract objects
    for field in ("glossary_updates",):
        match = re.search(rf'"{field}"\s*:\s*\{{(.*?)\}}', text, re.DOTALL)
        if match:
            pairs = re.findall(r'"([^"]+)"\s*:\s*"((?:[^"\\]|\\.)*)"', match.group(1))
            result[field] = dict(pairs)

    if not result:
        raise ValueError(f"Could not parse any JSON from response: {text[:300]}")

    return result
