# AGENTS.md — RepoBuddy

## Project Summary
RepoBuddy is a voice-native onboarding companion. Browser clients connect via WebSocket to a Python/FastAPI backend that orchestrates Cartesia STT/TTS, Anthropic Claude, ripgrep-based code search, and Notion read/write to guide engineers through unfamiliar codebases by voice.

## Repository Layout

```
server/                         — Python backend (run from this dir)
  main.py                       — FastAPI entry point, static file mount, /ws endpoint
  config.py                     — Env var loading (python-dotenv)
  models.py                     — Shared dataclasses, WS message-type constants
  ws_handler.py                 — WebSocket handler, session lifecycle, message dispatch
  anthropic_client.py           — Async Claude wrapper (call_claude function)
  cartesia_stt.py               — Cartesia STT WebSocket client (ink-whisper model)
  cartesia_stt_old.py           — Previous STT implementation (backup)
  cartesia_tts.py               — Cartesia TTS WebSocket client (sonic-3) + barge-in
  notion/
    client.py                   — Notion SDK singleton
    read_curriculum.py          — Fetch Notion page → Curriculum dataclass via Claude
    write_trail.py              — TrailWriter: create page, batch-append blocks
    blocks.py                   — Notion block builder helpers (heading, paragraph, toggle, code)
  repo/
    __init__.py                 — Re-exports all repo modules + enhanced_search
    scan.py                     — scan_repo: file tree, extensions, framework probes
    rg.py                       — rg_search: async ripgrep subprocess → list[RgMatch]
    file.py                     — open_snippet, open_around_match, file_exists
    evidence.py                 — collect_evidence: run rg + open snippets → EvidencePack
    enhanced_search.py          — Multi-layer search: intent classify, pattern gen, cache
  orchestrator/
    router.py                   — Route+plan (1 Claude call): intent + rg patterns + files
    chat.py                     — Chat pipeline: route → search → synthesize → TTS → Notion
    dm.py                       — DM pipeline: quest gen → present → grade → adjust difficulty
    prompts.py                  — All 6 Claude prompt templates
    quest_templates.py          — 10 generic code exploration quest templates
client/                         — Vanilla HTML/JS/CSS (no build step)
  index.html                    — Single-page app shell
  app.js                        — Mic capture (PCM 16kHz), WS client, audio playback (24kHz)
  style.css                     — Dark theme, 3-column layout
```

## Critical Conventions

### Module Naming
- Shared types live in `server/models.py` — **never** use `types.py` (shadows stdlib).
- All modules import shared types from `models`.

### WebSocket Protocol
Client→Server: `audio_in` (base64 PCM), `mode_switch`, `start_session`, `stop_session`
Server→Client: `transcript`, `response_text`, `audio_chunk`, `audio_done`, `evidence`, `quest`, `quest_result`, `session_info`, `mode_changed`, `curriculum`, `error`

### Audio Formats
- STT input: PCM s16le, 16 kHz, mono
- TTS output: PCM s16le, 24 kHz, mono

### Claude Prompt Patterns
All prompts in `orchestrator/prompts.py` return JSON. Parsing handles both raw JSON and ` ```json ` fenced blocks. There are 6 prompts:
1. `CURRICULUM_EXTRACTOR_PROMPT` — Notion markdown → curriculum JSON
2. `ROUTER_PLANNER_PROMPT` — user text → intent + search plan
3. `SYNTHESIZER_PROMPT` — evidence + question → voice_answer + detailed_answer
4. `QUEST_GENERATOR_PROMPT` — template → specialized quest
5. `QUEST_GRADER_PROMPT` — answer + evidence → grade + feedback
6. `CHAT_GREETING_PROMPT` — simple chat (no code search)

### Error Handling
- Every external call (Cartesia, Claude, Notion, rg) is wrapped in try/except.
- Errors surface to client via `error` WS message.
- Notion writes are fire-and-forget async — never block voice.
- If Notion keys are missing, all Notion calls silently no-op.

### Session State
`SessionState` dataclass in `models.py`. In-memory only, one per WebSocket connection. Holds: mode, repo_scan, curriculum, conversation_history, quest state, glossary, TTS context.

### Lazy Imports
`ws_handler.py` does lazy imports inside `handle_websocket()` to break circular dependency chains between ws_handler ↔ orchestrator ↔ repo modules.

## Environment
- Python 3.11+ required
- `rg` (ripgrep) must be on PATH
- All secrets in `server/.env` (gitignored). Template: `server/.env.example`
- Run: `cd server && pip install -r requirements.txt && python main.py`

## Current Known Issues
1. **Missing cartesia_stt.py** — The original was renamed to `cartesia_stt_old.py` but `ws_handler.py:39` still imports `from cartesia_stt import CartesiaSTT`. This must be resolved before the server can start.
2. **Cartesia API protocol** — The STT/TTS WebSocket protocol may need updates for the latest Cartesia API version. Check Cartesia docs.
3. **enhanced_search.py RelationshipMapper** — Currently a placeholder; no real AST parsing.

## Testing
- `server/test_enhanced_search.py` — Enhanced search tests
- `server/test_without_notion.py` — Pipeline tests without Notion dependency
- No test framework configured yet (pytest recommended)

## Dependencies
See `server/requirements.txt`: fastapi, uvicorn, websockets, anthropic, notion-client, python-dotenv
