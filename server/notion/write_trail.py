from __future__ import annotations

import asyncio
import logging
from datetime import datetime
from typing import Any

from notion.client import get_notion_client
from notion.blocks import heading_2, heading_3, paragraph, code_block, toggle, divider, bulleted_list_item
from models import EvidencePack, Quest, QuestResult

logger = logging.getLogger(__name__)


class TrailWriter:
    def __init__(self) -> None:
        self._queue: list[tuple[str, list[dict[str, Any]]]] = []
        self._lock = asyncio.Lock()

    async def create_trail_page(self, repo_name: str) -> tuple[str, str]:
        """Create a new trail page under the parent page. Returns (page_id, url)."""
        client = get_notion_client()
        if not client:
            return ("", "")

        from config import NOTION_PARENT_PAGE_ID
        if not NOTION_PARENT_PAGE_ID:
            return ("", "")

        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        title = f"Onboarding Trail — {repo_name} — {now}"

        try:
            page = client.pages.create(
                parent={"page_id": NOTION_PARENT_PAGE_ID},
                properties={
                    "title": {
                        "title": [
                            {
                                "type": "text", 
                                "text": {"content": title}
                            }
                        ]
                    }
                },
                children=[
                    heading_2("Chat Log"),
                    paragraph("Conversation history from RepoBuddy sessions."),
                    divider(),
                    heading_2("Practice Log"),
                    paragraph("Quest results and code exploration challenges."),
                    divider(),
                    heading_2("Glossary"),
                    paragraph("Terms and concepts discovered during onboarding."),
                ],
            )
            page_id = page["id"]
            page_url = page.get("url", "")
            logger.info("Created trail page: %s", page_url)
            return (page_id, page_url)
        except Exception as e:
            logger.error("Failed to create trail page: %s", e)
            return ("", "")

    async def append_chat_turn(
        self,
        page_id: str,
        user_text: str,
        assistant_text: str,
        evidence: EvidencePack | None = None,
    ) -> None:
        if not page_id:
            return

        children: list[dict[str, Any]] = [
            paragraph(f"User: {user_text}"),
            paragraph(f"Assistant: {assistant_text}"),
        ]
        if evidence and evidence.snippets:
            for s in evidence.snippets[:3]:
                children.append(code_block(
                    f"// {s.path} (lines {s.start}-{s.end})\n{s.text}",
                ))

        block = toggle(
            f"Q: {user_text[:80]}{'...' if len(user_text) > 80 else ''}",
            children,
        )
        self._enqueue(page_id, [block])

    async def append_quest_result(
        self,
        page_id: str,
        quest: Quest,
        user_answer: str,
        result: QuestResult,
    ) -> None:
        if not page_id:
            return

        children: list[dict[str, Any]] = [
            paragraph(f"Quest: {quest.description}"),
            paragraph(f"Answer: {user_answer}"),
            paragraph(f"Grade: {result.grade} ({result.score}/100)"),
            paragraph(f"Feedback: {result.feedback}"),
        ]
        if result.evidence and result.evidence.snippets:
            for s in result.evidence.snippets[:2]:
                children.append(code_block(
                    f"// {s.path} (lines {s.start}-{s.end})\n{s.text}",
                ))

        block = toggle(
            f"{'✅' if result.grade == 'pass' else '⚠️' if result.grade == 'partial' else '❌'} {quest.title}",
            children,
        )
        self._enqueue(page_id, [block])

    async def append_glossary(self, page_id: str, glossary: dict[str, str]) -> None:
        if not page_id or not glossary:
            return
        blocks = [bulleted_list_item(f"**{k}**: {v}") for k, v in glossary.items()]
        self._enqueue(page_id, blocks)

    def _enqueue(self, page_id: str, blocks: list[dict[str, Any]]) -> None:
        self._queue.append((page_id, blocks))

    async def flush(self) -> None:
        async with self._lock:
            if not self._queue:
                return
            client = get_notion_client()
            if not client:
                self._queue.clear()
                return

            # Group by page_id
            by_page: dict[str, list[dict[str, Any]]] = {}
            for page_id, blocks in self._queue:
                by_page.setdefault(page_id, []).extend(blocks)
            self._queue.clear()

            for page_id, blocks in by_page.items():
                try:
                    # Notion limits to 100 blocks per request
                    for i in range(0, len(blocks), 100):
                        chunk = blocks[i:i+100]
                        client.blocks.children.append(
                            block_id=page_id,
                            children=chunk,
                        )
                except Exception as e:
                    logger.error("Notion flush error for %s: %s", page_id, e)

    async def flush_loop(self) -> None:
        """Background task that flushes every 3 seconds."""
        try:
            while True:
                await asyncio.sleep(3)
                await self.flush()
        except asyncio.CancelledError:
            await self.flush()
