---
name: debug-ws
description: Debug WebSocket connection issues between browser and server. Use when the client can't connect, messages aren't flowing, or the UI doesn't update.
user-invocable: true
---

# Debug WebSocket

## When to use
- Browser shows "Disconnected" status
- Messages sent from client aren't received by server
- Server responses don't appear in browser UI
- Audio chunks aren't flowing

## Architecture
- Server: `server/ws_handler.py` — `handle_websocket()` accepts WS at `/ws`
- Client: `client/app.js` — `connect()` opens WS to `ws://host/ws`
- Messages are JSON with a `type` field

## Message flow
```
Client                          Server
  |--- start_session ------------>|
  |<------------ session_info ----|
  |--- audio_in (base64 PCM) --->|  → Cartesia STT
  |<------------ transcript ------|  ← STT result
  |                               |  → Claude (route+plan)
  |                               |  → rg_search
  |                               |  → Claude (synthesize)
  |<------------ response_text ---|
  |<------------ evidence --------|
  |<------------ audio_chunk -----|  ← Cartesia TTS
  |<------------ audio_done ------|
```

## Debugging steps
1. Check browser console for WS errors (`ws.onerror`, `ws.onclose` events)
2. Check server logs for "Client disconnected" or exception traces
3. Verify `send_json()` in ws_handler isn't silently failing
4. For audio issues: check that `audioCtx` sample rates match (16kHz capture, 24kHz playback)
5. For message routing: check `msg_type` matches constants in `models.py`

## Key files
- `server/ws_handler.py` — server-side handler
- `server/models.py` — message type constants (MSG_AUDIO_IN, etc.)
- `client/app.js` — client-side WS logic
- `client/index.html` — UI elements referenced by app.js
