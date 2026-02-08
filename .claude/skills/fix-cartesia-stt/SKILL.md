---
name: fix-cartesia-stt
description: Fix the Cartesia STT WebSocket client to work with the latest API. Use when STT connection fails or transcription doesn't work.
user-invocable: true
---

# Fix Cartesia STT

## When to use
- Server crashes on `from cartesia_stt import CartesiaSTT`
- STT WebSocket connection fails
- No transcripts are received from Cartesia

## Steps

1. Check if `server/cartesia_stt.py` exists. If not, it may have been renamed to `cartesia_stt_old.py`.
2. Read the Cartesia STT WebSocket docs to verify the correct URL, model name, and message format.
3. The STT WebSocket URL pattern is: `wss://api.cartesia.ai/stt/websocket?model=ink-whisper&language=en&encoding=pcm_s16le&sample_rate=16000&api_key=KEY`
4. Audio is sent as raw binary frames (not JSON). Transcripts come back as JSON: `{"type": "transcript", "transcript": "...", "is_final": true/false}`
5. Ensure `ws_handler.py` imports from the correct module name.

## Key files
- `server/cartesia_stt.py` (or `server/cartesia_stt_old.py`)
- `server/ws_handler.py` (line ~39: `from cartesia_stt import CartesiaSTT`)
- `server/config.py` (CARTESIA_API_KEY)

## Verification
```bash
cd server && python -c "from cartesia_stt import CartesiaSTT; print('import OK')"
```
