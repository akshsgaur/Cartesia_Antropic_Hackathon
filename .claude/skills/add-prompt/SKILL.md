---
name: add-prompt
description: Add or modify a Claude prompt template. Use when adding new AI capabilities or tuning existing prompt behavior.
user-invocable: true
---

# Add/Modify Claude Prompt

## When to use
- Adding a new Claude-powered feature (new prompt template)
- Tuning an existing prompt for better results
- Changing JSON output format from a prompt

## Architecture
All prompts live in `server/orchestrator/prompts.py`. Each is a Python format string with `{placeholders}`.

Current prompts:
1. `CURRICULUM_EXTRACTOR_PROMPT` — Notion page → curriculum JSON
2. `ROUTER_PLANNER_PROMPT` — user text → intent + rg patterns + candidate files
3. `SYNTHESIZER_PROMPT` — evidence + question → voice_answer + detailed_answer + glossary
4. `QUEST_GENERATOR_PROMPT` — template → specialized quest JSON
5. `QUEST_GRADER_PROMPT` — answer + evidence → grade + feedback
6. `CHAT_GREETING_PROMPT` — simple greeting response

## Conventions
- All prompts MUST instruct Claude to return **only valid JSON** (no markdown wrapping unless fenced)
- The JSON parsing in callers handles both raw JSON and ` ```json ``` ` fenced blocks
- Keep voice_answer fields to <=2 sentences (for TTS)
- Use `{{` and `}}` for literal braces in f-strings (Python format string escaping)

## Adding a new prompt
1. Define the template in `orchestrator/prompts.py`
2. Call it via `anthropic_client.call_claude(prompt, max_tokens=N)`
3. Parse JSON response with the standard pattern:
   ```python
   if "```json" in result:
       json_str = result.split("```json")[1].split("```")[0]
   ```
4. Wire it into the appropriate pipeline (chat.py, dm.py, or a new module)

## Key files
- `server/orchestrator/prompts.py` — all templates
- `server/anthropic_client.py` — `call_claude()` function
- `server/orchestrator/chat.py` — chat pipeline (uses router + synthesizer)
- `server/orchestrator/dm.py` — DM pipeline (uses quest gen + grader)
