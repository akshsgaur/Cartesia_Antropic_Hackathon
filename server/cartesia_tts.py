from __future__ import annotations

import asyncio
import json
import logging
import uuid
from typing import Any

import websockets
from websockets.asyncio.client import ClientConnection
from fastapi import WebSocket, WebSocketDisconnect
from uvicorn.protocols.utils import ClientDisconnected

from config import CARTESIA_API_KEY, CARTESIA_VOICE_ID
from models import MSG_AUDIO_CHUNK, MSG_AUDIO_DONE, SessionState

logger = logging.getLogger(__name__)

TTS_URL = (
    f"wss://api.cartesia.ai/tts/websocket"
    f"?api_key={CARTESIA_API_KEY}"
    f"&cartesia_version=2024-06-10"
)

PING_INTERVAL = 60  # seconds — keeps the connection alive (Cartesia timeout is 180s)


class CartesiaTTS:
    def __init__(self) -> None:
        self._ws: ClientConnection | None = None
        self._closed = False
        self._ping_task: asyncio.Task | None = None

    async def connect(self) -> None:
        self._ws = await websockets.connect(TTS_URL)
        self._ping_task = asyncio.create_task(self._keepalive())
        logger.info("Cartesia TTS connected")

    async def _keepalive(self) -> None:
        """Send periodic WebSocket pings to prevent idle timeout."""
        while not self._closed:
            await asyncio.sleep(PING_INTERVAL)
            if self._ws and self._ws.close_code is None:
                try:
                    await self._ws.ping()
                except Exception:
                    pass

    async def _ensure_connected(self) -> bool:
        """Reconnect if the WebSocket is dead. Returns True if connected."""
        if self._closed:
            return False
        if self._ws:
            try:
                if self._ws.close_code is not None:
                    self._ws = None
            except Exception:
                self._ws = None
        if not self._ws:
            try:
                self._ws = await websockets.connect(TTS_URL)
                logger.info("Cartesia TTS reconnected")
            except Exception as e:
                logger.error("TTS reconnect failed: %s", e)
                return False
        return True

    async def speak(self, text: str, client_ws: WebSocket, session: SessionState) -> None:
        """Send text to TTS and stream audio chunks back to the client."""
        if not text.strip():
            return

        if not await self._ensure_connected():
            return

        context_id = str(uuid.uuid4())
        session.tts_context_id = context_id
        session.is_speaking = True

        request = {
            "context_id": context_id,
            "model_id": "sonic-3",
            "transcript": text,
            "voice": {
                "mode": "id",
                "id": CARTESIA_VOICE_ID,
            },
            "output_format": {
                "container": "raw",
                "encoding": "pcm_s16le",
                "sample_rate": 24000,
            },
        }

        try:
            logger.info("TTS sending request: %s", json.dumps(request)[:200])
            await self._ws.send(json.dumps(request))
            logger.info("TTS request sent, waiting for response...")

            chunk_count = 0
            while session.is_speaking:
                try:
                    raw = await asyncio.wait_for(self._ws.recv(), timeout=10.0)
                except asyncio.TimeoutError:
                    logger.warning("TTS recv timeout after %d chunks", chunk_count)
                    break

                try:
                    msg = json.loads(raw)
                except (json.JSONDecodeError, TypeError):
                    continue

                if msg.get("context_id") != context_id:
                    continue

                if msg.get("type") == "chunk" and "data" in msg:
                    chunk_count += 1
                    try:
                        await client_ws.send_json({
                            "type": MSG_AUDIO_CHUNK,
                            "audio": msg["data"],
                        })
                    except (WebSocketDisconnect, ClientDisconnected):
                        logger.warning("Client disconnected during TTS, stopping audio stream")
                        break
                elif msg.get("type") == "error":
                    logger.error("TTS error response: %s", msg)
                    break

                if msg.get("done", False):
                    logger.info("TTS done, sent %d chunks", chunk_count)
                    break

        except websockets.ConnectionClosed:
            logger.warning("TTS connection closed during speak, will reconnect next call")
            self._ws = None
        except Exception as e:
            logger.error("TTS speak error: %s", e, exc_info=True)
            self._ws = None
        finally:
            session.is_speaking = False
            session.tts_context_id = ""
            try:
                await client_ws.send_json({"type": MSG_AUDIO_DONE, "interrupted": False})
            except (WebSocketDisconnect, ClientDisconnected, Exception):
                logger.debug("Client disconnected before audio_done message")

    async def cancel(self, session: SessionState) -> None:
        """Cancel current TTS playback (barge-in)."""
        if not session.tts_context_id:
            return

        session.is_speaking = False
        cancel_msg = {
            "context_id": session.tts_context_id,
            "cancel": True,
        }
        if self._ws:
            try:
                await self._ws.send(json.dumps(cancel_msg))
            except websockets.ConnectionClosed:
                logger.warning("TTS cancel failed (connection closed)")
                self._ws = None
            except Exception as e:
                logger.error("TTS cancel error: %s", e)
        session.tts_context_id = ""

    async def close(self) -> None:
        self._closed = True
        if self._ping_task:
            self._ping_task.cancel()
        if self._ws:
            await self._ws.close()
        logger.info("TTS closed")
