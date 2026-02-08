---
name: add-ws-message
description: Add a new WebSocket message type to the protocol. Use when adding new client-server communication.
user-invocable: true
---

# Add WebSocket Message Type

## When to use
- Adding a new feature that requires client-server communication
- Need to send a new type of data from server to browser or vice versa

## Steps

### 1. Define the message constant in `server/models.py`
```python
# Client → Server
MSG_MY_NEW_ACTION = "my_new_action"

# Server → Client
MSG_MY_NEW_EVENT = "my_new_event"
```

### 2. Handle it in `server/ws_handler.py`
For client→server messages, add an `elif` in the message routing loop:
```python
elif msg_type == MSG_MY_NEW_ACTION:
    # handle it
    await send_json(ws, MSG_MY_NEW_EVENT, {"key": "value"})
```

### 3. Handle it in `client/app.js`
For server→client messages, add a case in `handleMessage()`:
```javascript
case 'my_new_event':
    handleMyNewEvent(msg);
    break;
```

To send from client:
```javascript
send('my_new_action', { key: 'value' });
```

## Conventions
- Message type strings use `snake_case`
- Constants in models.py use `MSG_UPPER_SNAKE_CASE`
- All messages are JSON with a `type` field
- Use `send_json(ws, type, data)` helper on the server side

## Key files
- `server/models.py` — message type constants
- `server/ws_handler.py` — server-side routing
- `client/app.js` — client-side routing
