from __future__ import annotations

import json
import logging
from typing import Any

from notion.client import get_notion_client
from anthropic_client import call_claude
from orchestrator.prompts import CURRICULUM_EXTRACTOR_PROMPT
from models import Curriculum, CurriculumModule, CurriculumMilestone

logger = logging.getLogger(__name__)


def _blocks_to_text(blocks: list[dict[str, Any]], indent: int = 0) -> str:
    """Convert Notion blocks to markdown-like text."""
    lines: list[str] = []
    prefix = "  " * indent

    for block in blocks:
        btype = block.get("type", "")
        text = _extract_rich_text(block.get(btype, {}))

        if btype.startswith("heading_"):
            level = int(btype[-1])
            lines.append(f"{'#' * level} {text}")
        elif btype == "paragraph":
            lines.append(f"{prefix}{text}")
        elif btype == "bulleted_list_item":
            lines.append(f"{prefix}- {text}")
        elif btype == "numbered_list_item":
            lines.append(f"{prefix}1. {text}")
        elif btype == "to_do":
            checked = block.get(btype, {}).get("checked", False)
            mark = "x" if checked else " "
            lines.append(f"{prefix}- [{mark}] {text}")
        elif btype == "toggle":
            lines.append(f"{prefix}> {text}")
        elif btype == "code":
            lang = block.get(btype, {}).get("language", "")
            lines.append(f"{prefix}```{lang}\n{text}\n```")
        elif btype == "divider":
            lines.append("---")
        elif btype == "callout":
            emoji = block.get(btype, {}).get("icon", {}).get("emoji", "")
            lines.append(f"{prefix}{emoji} {text}")
        elif text:
            lines.append(f"{prefix}{text}")

        # Handle children
        if block.get("has_children"):
            children = block.get("children", [])
            if children:
                lines.append(_blocks_to_text(children, indent + 1))

    return "\n".join(lines)


def _extract_rich_text(block_data: dict[str, Any]) -> str:
    """Extract plain text from Notion rich_text array."""
    parts: list[str] = []
    for rt in block_data.get("rich_text", []):
        parts.append(rt.get("plain_text", ""))
    return "".join(parts)


async def _fetch_all_blocks(page_id: str) -> list[dict[str, Any]]:
    """Fetch all blocks from a Notion page, including children."""
    client = get_notion_client()
    if not client:
        return []

    blocks: list[dict[str, Any]] = []
    cursor = None

    while True:
        kwargs: dict[str, Any] = {"block_id": page_id}
        if cursor:
            kwargs["start_cursor"] = cursor
        response = client.blocks.children.list(**kwargs)
        results = response.get("results", [])
        blocks.extend(results)

        # Fetch children for blocks that have them
        for block in results:
            if block.get("has_children"):
                children = await _fetch_all_blocks(block["id"])
                block["children"] = children

        if not response.get("has_more"):
            break
        cursor = response.get("next_cursor")

    return blocks


async def load_curriculum(page_id: str) -> Curriculum | None:
    """Read a Notion page and extract curriculum structure via Claude."""
    if not page_id:
        return None

    try:
        blocks = await _fetch_all_blocks(page_id)
        if not blocks:
            logger.warning("No blocks found in curriculum page %s", page_id)
            return None

        markdown_text = _blocks_to_text(blocks)
        if not markdown_text.strip():
            return None

        # Use Claude to extract structured curriculum
        prompt = CURRICULUM_EXTRACTOR_PROMPT.format(page_content=markdown_text)
        result = await call_claude(prompt, max_tokens=2000)

        # Parse JSON from response
        # Try to find JSON in the response
        json_str = result
        if "```json" in result:
            json_str = result.split("```json")[1].split("```")[0]
        elif "```" in result:
            json_str = result.split("```")[1].split("```")[0]

        data = json.loads(json_str.strip())

        return Curriculum(
            title=data.get("title", "Untitled Curriculum"),
            goals=data.get("goals", []),
            modules=[
                CurriculumModule(
                    name=m.get("name", ""),
                    topics=m.get("topics", []),
                    key_files=m.get("key_files", []),
                )
                for m in data.get("modules", [])
            ],
            milestones=[
                CurriculumMilestone(
                    description=ms.get("description", ""),
                    day_target=ms.get("day_target", 1),
                )
                for ms in data.get("milestones", [])
            ],
        )
    except Exception as e:
        logger.error("Failed to load curriculum: %s", e, exc_info=True)
        return None
