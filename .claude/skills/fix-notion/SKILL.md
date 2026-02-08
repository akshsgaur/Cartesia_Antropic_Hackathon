---
name: fix-notion
description: Fix Notion integration issues — trail page creation, curriculum reading, or block appending. Use when Notion operations fail or return empty results.
user-invocable: true
---

# Fix Notion Integration

## When to use
- Trail page not created on session start
- Curriculum page returns empty/null
- Chat turns or quest results not appearing in Notion
- Notion API errors in server logs

## Architecture
- `server/notion/client.py` — singleton `get_notion_client()`, returns None if no API key
- `server/notion/read_curriculum.py` — `load_curriculum(page_id)`: fetch blocks → markdown → Claude → Curriculum dataclass
- `server/notion/write_trail.py` — `TrailWriter`: async queue + flush loop (every 3s)
- `server/notion/blocks.py` — helpers: `heading_2`, `paragraph`, `toggle`, `code_block`, `divider`, `bulleted_list_item`

## Key design decisions
- All Notion operations are **optional** — if `NOTION_API_KEY` is empty, everything no-ops
- Writes are **batched** — queued in memory, flushed every 3 seconds or on session end
- Notion limits: 100 blocks per API call, 2000 chars per rich_text content
- Trail page structure: "Chat Log" section, "Practice Log" section, "Glossary" section

## Common issues
1. **"Notion API key not set"** — Check `server/.env` has `NOTION_API_KEY=ntn_...`
2. **"Could not find page"** — Ensure `NOTION_PARENT_PAGE_ID` is a valid page ID the integration can access. The integration must be shared with that page in Notion.
3. **Empty curriculum** — The curriculum page might have no blocks, or the page ID might be wrong. Check logs for "No blocks found".
4. **Blocks not appearing** — The flush loop might not be running. Check that `notion_flush_task` is created in `ws_handler.py`.

## Environment variables
- `NOTION_API_KEY` — Integration token (starts with `ntn_`)
- `NOTION_PARENT_PAGE_ID` — Page ID (32 hex chars, no dashes) where trail pages are created as children
- `NOTION_CURRICULUM_PAGE_ID` — Page ID of the manager's curriculum page

## Key files
- `server/notion/client.py`
- `server/notion/read_curriculum.py`
- `server/notion/write_trail.py`
- `server/notion/blocks.py`
- `server/config.py` — env var loading
