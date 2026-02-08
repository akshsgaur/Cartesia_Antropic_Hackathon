---
name: add-quest
description: Add a new quest template for Practice mode. Use when you want to add new code exploration challenges.
user-invocable: true
---

# Add Quest Template

## When to use
- Adding new types of code exploration quests
- Expanding the Practice mode with new challenges

## Architecture
Quest templates live in `server/orchestrator/quest_templates.py` as a list of dicts with `id` and `template` keys. Claude specializes each template for the specific repo at runtime via `QUEST_GENERATOR_PROMPT`.

## Current templates (10)
1. `http_entrypoint` — Find server start
2. `config_loader` — Find config/env loading
3. `database_connection` — Find DB connection
4. `auth_middleware` — Find auth middleware
5. `request_trace` — Trace a request flow
6. `error_handling` — Find error handling
7. `test_setup` — Find test config
8. `data_model` — Find schema/model definitions
9. `background_job` — Find workers/cron
10. `build_deploy` — Find build/deploy config

## Adding a new template
1. Add an entry to `QUEST_TEMPLATES` in `server/orchestrator/quest_templates.py`:
   ```python
   {
       "id": "unique_snake_case_id",
       "template": "Human-readable description of what to find/do",
   }
   ```
2. The `id` must be unique — it's used to track completed quests in `SessionState.completed_quests`
3. The `template` text is passed to Claude's `QUEST_GENERATOR_PROMPT` which specializes it for the target repo

## Difficulty system
- Level 1: Claude adds file_hints, very specific instructions
- Level 2: Moderate hints
- Level 3: Minimal hints, tests deeper understanding
- Auto-adjusts: 2 consecutive passes → level up, 2 fails → level down

## Key files
- `server/orchestrator/quest_templates.py` — template definitions
- `server/orchestrator/dm.py` — `start_quest()` and `handle_dm_turn()`
- `server/orchestrator/prompts.py` — `QUEST_GENERATOR_PROMPT`, `QUEST_GRADER_PROMPT`
- `server/models.py` — `Quest`, `QuestResult` dataclasses
