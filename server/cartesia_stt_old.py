from __future__ import annotations

import asyncio
import base64
import json
import logging
from typing import Any, Callable, Awaitable

import websockets
from websockets.asyncio.client import ClientConnection

from config import CARTESIA_API_KEY

logger = logging.getLogger(__name__)

STT_URL = (
    "wss://api.cartesia.ai/stt/websocket"
    "?model=sonic-3"
    "&language=en"
    "&encoding=pcm_s16le"
    "&sample_rate=16000"
    f"&api_key={CARTESIA_API_KEY}"
    "&cartesia_version=2025-04-16"
)


class CartesiaSTT:
    def __init__(self, on_transcript: Callable[[str], Awaitable[None]]) -> None:
        self._on_transcript = on_transcript
        self._ws: ClientConnection | None = None
        self._receive_task: asyncio.Task | None = None
        self._latest_event: dict[str, Any] | None = None

    async def connect(self) -> None:
        try:
            # Connect with proper subprotocols
            self._ws = await websockets.connect(
                STT_URL,
                subprotocols=["json", "binary"]
            )
            self._receive_task = asyncio.create_task(self._receive_loop())
            logger.info("Cartesia STT connected")
        
        # Send initial context message
        init_message = {
            "model_id": "sonic-3",
            "context_id": "happy-monkeys-fly",
            "output_format": {
                "container": "raw",
                "encoding": "pcm_s16le", 
                "sample_rate": 16000
            }
        }
        await self._ws.send(json.dumps(init_message))

    async def _receive_loop(self) -> None:
        if not self._ws:
            return
        try:
            async for raw in self._ws:
                try:
                    msg = json.loads(raw)
                except (json.JSONDecodeError, TypeError):
                    continue

                msg_type = msg.get("type", "")

                if msg_type == "transcript":
                    text = msg.get("transcript", "")
                    is_final = msg.get("is_final", False)
                    self._latest_event = {
                        "text": text,
                        "is_final": is_final,
                    }

                    if is_final and text.strip():
                        asyncio.create_task(self._on_transcript(text.strip()))

        except websockets.ConnectionClosed:
            logger.info("STT WebSocket closed")
        except Exception as e:
            logger.error("STT receive error: %s", e, exc_info=True)

    async def send_audio(self, audio_b64: str) -> None:
        """Send base64-encoded PCM audio to Cartesia STT."""
        if not self._ws:
            return
        try:
            # Create proper WebSocket message for Cartesia STT
            audio_bytes = base64.b64decode(audio_b64)
            
            # Send as JSON message with audio data
            message = {
                "model_id": "sonic-3",
                "transcript": "Hello, world! I'm generating audio on Cartesia!",
                "voice": {
                    "mode": "id", 
                    "id": "a167e0f3-df7e-4d52-a9c3-f949145efdab"
                },
                "language": "en",
                "context_id": "happy-monkeys-fly",
                "output_format": {
                    "container": "raw",
                    "encoding": "pcm_s16le",
                    "sample_rate": 16000
                },
                "add_timestamps": True,
                "continue": False
            }
            
            await self._ws.send(json.dumps(message))
        except Exception as e:
            logger.error("STT send error: %s", e)

    def get_latest_event(self) -> dict[str, Any] | None:
        """Return and clear the latest transcript event."""
        event = self._latest_event
        self._latest_event = None
        return event

    async def close(self) -> None:
        if self._receive_task:
            self._receive_task.cancel()
        if self._ws:
            # Send proper close message
            close_message = {
                "type": "done",
                "done": True,
                "flush_id": 1
            }
            await self._ws.send(json.dumps(close_message))
            await self._ws.close()
        logger.info("STT closed")
