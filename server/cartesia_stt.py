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
    "?model=ink-whisper"
    "&language=en"
    "&encoding=pcm_s16le"
    "&sample_rate=16000"
)

STT_HEADERS = {
    "X-API-Key": CARTESIA_API_KEY,
    "Cartesia-Version": "2025-04-16",
}


PING_INTERVAL = 60  # seconds — keeps the connection alive (Cartesia timeout is 180s)


class CartesiaSTT:
    def __init__(self, on_transcript: Callable[[str], Awaitable[None]]) -> None:
        self._on_transcript = on_transcript
        self._ws: ClientConnection | None = None
        self._receive_task: asyncio.Task | None = None
        self._ping_task: asyncio.Task | None = None
        self._latest_event: dict[str, Any] | None = None
        self._closed = False

    async def connect(self) -> None:
        self._ws = await websockets.connect(
            STT_URL,
            additional_headers=STT_HEADERS,
        )
        self._receive_task = asyncio.create_task(self._receive_loop())
        self._ping_task = asyncio.create_task(self._keepalive())
        logger.info("Cartesia STT connected")

    async def _keepalive(self) -> None:
        """Send periodic WebSocket pings to prevent idle timeout."""
        while not self._closed:
            await asyncio.sleep(PING_INTERVAL)
            if self._ws and self._ws.close_code is None:
                try:
                    await self._ws.ping()
                except Exception:
                    pass

    async def _reconnect(self) -> None:
        """Reconnect the STT WebSocket after timeout or disconnect."""
        if self._closed:
            return
        try:
            self._ws = await websockets.connect(
                STT_URL,
                additional_headers=STT_HEADERS,
            )
            logger.info("Cartesia STT reconnected")
        except Exception as e:
            logger.error("STT reconnect failed: %s", e)
            self._ws = None

    async def _receive_loop(self) -> None:
        """Receive transcripts, auto-reconnect on disconnect/timeout."""
        while not self._closed:
            if not self._ws:
                await asyncio.sleep(1)
                await self._reconnect()
                continue
            try:
                async for raw in self._ws:
                    try:
                        msg = json.loads(raw)
                    except (json.JSONDecodeError, TypeError):
                        continue

                    msg_type = msg.get("type", "")

                    if msg_type == "transcript":
                        text = msg.get("text", "") or msg.get("transcript", "")
                        is_final = msg.get("is_final", False)
                        self._latest_event = {
                            "text": text,
                            "is_final": is_final,
                        }

                        if is_final and text.strip():
                            asyncio.create_task(self._on_transcript(text.strip()))

                    elif msg_type == "done":
                        logger.info("STT session done, will reconnect")
                        break

            except websockets.ConnectionClosed:
                logger.info("STT WebSocket closed, will reconnect")
            except Exception as e:
                logger.error("STT receive error: %s", e, exc_info=True)

            # Connection lost or session done — reconnect
            self._ws = None
            if not self._closed:
                await asyncio.sleep(0.5)
                await self._reconnect()

    async def send_audio(self, audio_b64: str) -> None:
        """Send base64-encoded PCM audio to Cartesia STT as raw binary."""
        if not self._ws:
            await self._reconnect()
        if not self._ws:
            return
        try:
            audio_bytes = base64.b64decode(audio_b64)
            await self._ws.send(audio_bytes)
        except websockets.ConnectionClosed:
            logger.warning("STT send failed (closed), reconnecting")
            self._ws = None
            await self._reconnect()
        except Exception as e:
            logger.error("STT send error: %s", e)

    def get_latest_event(self) -> dict[str, Any] | None:
        """Return and clear the latest transcript event."""
        event = self._latest_event
        self._latest_event = None
        return event

    async def close(self) -> None:
        self._closed = True
        if self._receive_task:
            self._receive_task.cancel()
        if self._ping_task:
            self._ping_task.cancel()
        if self._ws:
            try:
                await self._ws.send("done")
            except Exception:
                pass
            await self._ws.close()
        logger.info("STT closed")
