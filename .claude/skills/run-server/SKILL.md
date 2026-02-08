---
name: run-server
description: Start the RepoBuddy server and verify it works. Use for startup issues, import errors, or dependency problems.
user-invocable: true
---

# Run Server

## Quick start
```bash
cd server
pip install -r requirements.txt
cp .env.example .env  # then fill in API keys
python main.py
```
Opens on http://localhost:3000 (or whatever PORT is set to).

## Prerequisites
- Python 3.11+
- `rg` (ripgrep) on PATH: `brew install ripgrep` / `apt install ripgrep`
- All env vars in `server/.env`

## Common startup errors

### `ModuleNotFoundError: No module named 'X'`
Run `pip install -r server/requirements.txt`. If using a venv, make sure it's activated.

### `ImportError: cannot import name 'CartesiaSTT' from 'cartesia_stt'`
`cartesia_stt.py` may be missing (renamed to `cartesia_stt_old.py`). Either:
- Rename it back: `mv server/cartesia_stt_old.py server/cartesia_stt.py`
- Or create a new `cartesia_stt.py` with the correct Cartesia API protocol

### `ripgrep (rg) not found on PATH`
This is a warning, not fatal. Install ripgrep for code search to work.

### `CARTESIA_API_KEY not set` / `ANTHROPIC_API_KEY not set`
Fill in `server/.env` with your API keys.

## Verification checklist
1. Server starts without import errors
2. http://localhost:3000 loads the UI
3. Browser console shows WebSocket connected
4. Clicking "Start Session" with a valid repo path shows repo info in sidebar
5. Holding mic button captures audio (check browser console)

## Key files
- `server/main.py` — entry point
- `server/config.py` — env vars
- `server/requirements.txt` — dependencies
- `server/.env` — secrets (gitignored)
