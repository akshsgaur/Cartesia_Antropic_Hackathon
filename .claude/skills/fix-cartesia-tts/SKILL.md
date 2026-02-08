---
name: fix-cartesia-tts
description: Fix the Cartesia TTS WebSocket client. Use when TTS connection fails, no audio is produced, or barge-in doesn't work.
user-invocable: true
---

# Fix Cartesia TTS

## When to use
- No audio playback in the browser
- TTS WebSocket connection fails
- Barge-in (interrupting TTS when user speaks) doesn't work

## Architecture
- `server/cartesia_tts.py` connects to `wss://api.cartesia.ai/tts/websocket?api_key=KEY&cartesia_version=2024-06-10`
- Sends JSON requests with: context_id, model_id (sonic-3), transcript, voice (mode=id, id=VOICE_ID), output_format (raw pcm_s16le 24kHz)
- Receives chunks with base64 audio data, forwards to browser via WS `audio_chunk` messages
- Barge-in: when STT fires during TTS playback, send `{"context_id": "...", "cancel": true}` to TTS WS

## Key files
- `server/cartesia_tts.py` — TTS client class
- `server/ws_handler.py` — barge-in logic in `MSG_AUDIO_IN` handler
- `client/app.js` — `playNext()` function for PCM playback at 24kHz

## Audio format
Output is PCM s16le at 24000 Hz. The browser converts Int16 → Float32 and plays via Web Audio API AudioBuffer at sampleRate 24000.

## Verification
Start the server, open browser, speak — you should hear a response. Check browser console for `audio_chunk` messages.
