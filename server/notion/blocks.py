"""Notion block builder helpers."""
from __future__ import annotations

from typing import Any


def heading_2(text: str) -> dict[str, Any]:
    return {
        "object": "block",
        "type": "heading_2",
        "heading_2": {
            "rich_text": [{"type": "text", "text": {"content": text}}]
        },
    }


def heading_3(text: str) -> dict[str, Any]:
    return {
        "object": "block",
        "type": "heading_3",
        "heading_3": {
            "rich_text": [{"type": "text", "text": {"content": text}}]
        },
    }


def paragraph(text: str) -> dict[str, Any]:
    # Notion limits rich_text content to 2000 chars
    text = text[:2000]
    return {
        "object": "block",
        "type": "paragraph",
        "paragraph": {
            "rich_text": [{"type": "text", "text": {"content": text}}]
        },
    }


def code_block(text: str, language: str = "plain text") -> dict[str, Any]:
    text = text[:2000]
    return {
        "object": "block",
        "type": "code",
        "code": {
            "rich_text": [{"type": "text", "text": {"content": text}}],
            "language": language,
        },
    }


def toggle(title: str, children: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    block: dict[str, Any] = {
        "object": "block",
        "type": "toggle",
        "toggle": {
            "rich_text": [{"type": "text", "text": {"content": title[:2000]}}],
        },
    }
    if children:
        block["toggle"]["children"] = children
    return block


def bulleted_list_item(text: str) -> dict[str, Any]:
    text = text[:2000]
    return {
        "object": "block",
        "type": "bulleted_list_item",
        "bulleted_list_item": {
            "rich_text": [{"type": "text", "text": {"content": text}}]
        },
    }


def divider() -> dict[str, Any]:
    return {
        "object": "block",
        "type": "divider",
        "divider": {},
    }
