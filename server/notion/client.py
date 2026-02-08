from __future__ import annotations

import logging
from notion_client import Client

from config import NOTION_API_KEY

logger = logging.getLogger(__name__)

_client: Client | None = None


def get_notion_client() -> Client | None:
    global _client
    if not NOTION_API_KEY:
        logger.warning("NOTION_API_KEY not set — Notion features disabled")
        return None
    if _client is None:
        _client = Client(auth=NOTION_API_KEY)
    return _client
