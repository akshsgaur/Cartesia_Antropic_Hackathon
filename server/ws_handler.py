from __future__ import annotations

import asyncio
import json
import logging
import uuid
from typing import Any

from fastapi import WebSocket, WebSocketDisconnect

from config import REPO_PATH, NOTION_CURRICULUM_PAGE_ID
from models import (
    MSG_AUDIO_IN, MSG_MODE_SWITCH, MSG_START_SESSION, MSG_STOP_SESSION,
    MSG_TRANSCRIPT, MSG_RESPONSE_TEXT, MSG_AUDIO_CHUNK, MSG_AUDIO_DONE,
    MSG_EVIDENCE, MSG_SESSION_INFO, MSG_MODE_CHANGED, MSG_CURRICULUM,
    MSG_ERROR, MSG_QUEST, MSG_QUEST_RESULT,
    SessionState,
)

logger = logging.getLogger(__name__)


async def send_json(ws: WebSocket, msg_type: str, data: dict[str, Any] | None = None) -> None:
    payload: dict[str, Any] = {"type": msg_type}
    if data:
        payload.update(data)
    await ws.send_json(payload)


async def handle_websocket(ws: WebSocket) -> None:
    await ws.accept()
    session = SessionState(session_id=str(uuid.uuid4()))
    stt_client = None
    tts_client = None
    notion_flush_task: asyncio.Task | None = None

    # Lazy imports to avoid circular deps at module level
    from cartesia_stt import CartesiaSTT
    from cartesia_tts import CartesiaTTS
    from orchestrator.chat import handle_chat_turn
    from orchestrator.dm import handle_dm_turn, start_quest
    from repo.scan import scan_repo
    from notion.read_curriculum import load_curriculum
    from notion.write_trail import TrailWriter

    trail_writer = TrailWriter()

    GOODBYE_PHRASES = {"goodbye", "good bye", "bye bye", "bye", "end session", "stop session", "i'm done", "im done"}

    async def on_final_transcript(text: str) -> None:
        """Called when STT delivers a final transcript."""
        if not text.strip():
            return

        logger.info(">>> FINAL TRANSCRIPT: %s", text)

        # Check for goodbye / end-session phrases
        lowered = text.strip().lower().rstrip(".!?,")
        if lowered in GOODBYE_PHRASES:
            session.add_turn("user", text)
            if tts_client:
                await tts_client.speak("Goodbye! Great session. Check your Onboarding Trail in Notion for a summary.", ws, session)
            await trail_writer.flush()
            await send_json(ws, "session_ended", {})
            return

        session.add_turn("user", text)

        try:
            if session.mode == "practice" and session.current_quest:
                result = await handle_dm_turn(session, text)
                if result:
                    await send_json(ws, MSG_QUEST_RESULT, {
                        "quest_id": result.quest_id,
                        "grade": result.grade,
                        "score": result.score,
                        "feedback": result.feedback,
                        "evidence": result.evidence.to_dict(),
                    })
                    if tts_client:
                        await tts_client.speak(result.feedback, ws, session)
                    if session.current_quest:
                        await trail_writer.append_quest_result(
                            session.trail_page_id,
                            session.current_quest,
                            text,
                            result,
                        )
                    if result.grade == "pass":
                        await asyncio.sleep(1.5)
                        await _start_next_quest()
            else:
                logger.info(">>> Running natural conversation flow...")
                response = await handle_chat_turn(session, text)
                
                if response:
                    conversation_stage = response.get("conversation_stage", "complete")
                    voice_answer = response.get("voice_answer", "")
                    
                    if conversation_stage == "complete":
                        # Simple question - immediate complete response
                        await send_json(ws, MSG_RESPONSE_TEXT, {
                            "voice_answer": voice_answer,
                            "detailed_answer": response.get("detailed_answer", ""),
                        })
                        logger.info(">>> Sent complete response")
                        
                        if tts_client:
                            logger.info(">>> Starting TTS: %s", voice_answer[:80])
                            await tts_client.speak(voice_answer, ws, session)
                        
                        evidence = response.get("evidence")
                        if evidence:
                            await send_json(ws, MSG_EVIDENCE, {"evidence": evidence.to_dict()})
                    
                    elif conversation_stage == "thinking":
                        # Complex question - immediate acknowledgment + background processing
                        await send_json(ws, MSG_RESPONSE_TEXT, {
                            "voice_answer": voice_answer,
                            "detailed_answer": "",  # Empty for now
                        })
                        logger.info(">>> Sent immediate acknowledgment")
                        
                        # Start TTS immediately with acknowledgment
                        if tts_client:
                            logger.info(">>> Starting acknowledgment TTS: %s", voice_answer[:80])
                            await tts_client.speak(voice_answer, ws, session)
                        
                        # Wait for background processing
                        processing_task = response.get("processing_task")
                        if processing_task:
                            try:
                                result = await asyncio.wait_for(processing_task, timeout=10.0)
                                
                                # Send thinking filler
                                thinking_filler = result.get("thinking_filler", "Let me check...")
                                if tts_client:
                                    await tts_client.speak(thinking_filler, ws, session)
                                
                                # Small pause for natural rhythm
                                await asyncio.sleep(0.5)
                                
                                # Send final response
                                transition = result.get("transition", "Here's what I found:")
                                detailed_answer = result.get("detailed_answer", "")
                                evidence = result.get("evidence")
                                
                                full_response = f"{transition} {detailed_answer}"
                                
                                await send_json(ws, MSG_RESPONSE_TEXT, {
                                    "voice_answer": voice_answer,  # Keep original acknowledgment
                                    "detailed_answer": full_response,
                                })
                                logger.info(">>> Sent final detailed response")
                                
                                if evidence:
                                    await send_json(ws, MSG_EVIDENCE, {"evidence": evidence.to_dict()})
                                
                                # Speak the detailed answer
                                if tts_client:
                                    logger.info(">>> Starting detailed TTS: %s", full_response[:80])
                                    await tts_client.speak(full_response, ws, session)
                                
                            except asyncio.TimeoutError:
                                logger.warning("Background processing timed out")
                                fallback = "I'm still looking into that, but I can tell you this is an interesting question!"
                                await send_json(ws, MSG_RESPONSE_TEXT, {
                                    "voice_answer": voice_answer,
                                    "detailed_answer": fallback,
                                })
                                if tts_client:
                                    await tts_client.speak(fallback, ws, session)
                    
                    # Log to Notion (non-blocking)
                    await trail_writer.append_chat_turn(
                        session.trail_page_id,
                        text,
                        response.get("detailed_answer", ""),
                        response.get("evidence"),
                    )
                    session.add_turn("assistant", response.get("detailed_answer", ""))
        except Exception as e:
            logger.error(">>> on_final_transcript ERROR: %s", e, exc_info=True)

    async def _start_next_quest() -> None:
        quest = await start_quest(session)
        if quest:
            session.current_quest = quest
            await send_json(ws, MSG_QUEST, {
                "id": quest.id,
                "title": quest.title,
                "description": quest.description,
                "difficulty": quest.difficulty,
            })
            if tts_client:
                await tts_client.speak(
                    f"Quest: {quest.title}. {quest.description}", ws, session
                )

    try:
        while True:
            try:
                raw = await ws.receive_text()
            except Exception as e:
                logger.info("WebSocket receive error: %s", e)
                break
                
            try:
                msg = json.loads(raw)
            except json.JSONDecodeError:
                await send_json(ws, MSG_ERROR, {"message": "Invalid JSON"})
                continue

            msg_type = msg.get("type", "")

            if msg_type == MSG_START_SESSION:
                repo_path = msg.get("repo_path", REPO_PATH)
                curriculum_page_id = msg.get("curriculum_page_id", NOTION_CURRICULUM_PAGE_ID)
                session.repo_path = repo_path

                # --- Run all startup tasks in parallel ---
                stt_client = CartesiaSTT(on_transcript=on_final_transcript)
                tts_client = CartesiaTTS()
                repo_name = repo_path.rstrip("/").split("/")[-1] if repo_path else "unknown"

                async def _scan():
                    try:
                        session.repo_scan = await scan_repo(repo_path)
                    except Exception as e:
                        logger.error("Repo scan failed: %s", e)

                async def _curriculum():
                    if not curriculum_page_id:
                        return
                    try:
                        session.curriculum = await load_curriculum(curriculum_page_id)
                    except Exception as e:
                        logger.warning("Curriculum load failed: %s", e)

                async def _trail():
                    try:
                        page_id, page_url = await trail_writer.create_trail_page(repo_name)
                        session.trail_page_id = page_id
                        session.trail_page_url = page_url
                    except Exception as e:
                        logger.warning("Trail page creation failed: %s", e)

                async def _stt():
                    try:
                        await stt_client.connect()
                    except Exception as e:
                        logger.error("STT connect failed: %s", e)
                        await send_json(ws, MSG_ERROR, {"message": f"STT connect failed: {e}"})

                async def _tts():
                    try:
                        await tts_client.connect()
                    except Exception as e:
                        logger.error("TTS connect failed: %s", e)
                        await send_json(ws, MSG_ERROR, {"message": f"TTS connect failed: {e}"})

                await asyncio.gather(_scan(), _trail(), _stt(), _tts())

                # Start Notion flush loop
                notion_flush_task = asyncio.create_task(trail_writer.flush_loop())

                # Send session info immediately so the UI unlocks
                await send_json(ws, MSG_SESSION_INFO, {
                    "session_id": session.session_id,
                    "repo_path": session.repo_path,
                    "trail_url": session.trail_page_url,
                    "repo_summary": session.repo_scan.summary() if session.repo_scan else "",
                    "mode": session.mode,
                })

                # Curriculum loads in background — send it when ready
                await _curriculum()
                if session.curriculum:
                    await send_json(ws, MSG_CURRICULUM, {
                        "curriculum": session.curriculum.to_dict()
                    })

            elif msg_type == MSG_AUDIO_IN:
                audio_b64 = msg.get("audio", "")
                if stt_client and audio_b64:
                    # Don't feed audio to STT while TTS is playing — prevents
                    # the mic from picking up speaker output and cancelling TTS.
                    if session.is_speaking:
                        continue
                    await stt_client.send_audio(audio_b64)
                    transcript_event = stt_client.get_latest_event()
                    if transcript_event:
                        await send_json(ws, MSG_TRANSCRIPT, transcript_event)
                elif not stt_client and audio_b64:
                    # User is trying to speak before session start - send helpful message
                    logger.warning(">>> audio_in received but stt_client is None! Session not started.")
                    await send_json(ws, MSG_ERROR, {
                        "message": "Please start a session first by entering a repository path and clicking 'Start Session'"
                    })
                elif not audio_b64:
                    logger.debug(">>> audio_in received but no audio data")
                else:
                    logger.warning(">>> audio_in received but stt_client is None!")

            elif msg_type == MSG_MODE_SWITCH:
                new_mode = msg.get("mode", "chat")
                session.mode = new_mode
                await send_json(ws, MSG_MODE_CHANGED, {"mode": new_mode})
                if new_mode == "practice":
                    await _start_next_quest()

            elif msg_type == MSG_STOP_SESSION:
                # Flush remaining Notion writes
                await trail_writer.flush()
                break

    except WebSocketDisconnect:
        logger.info("Client disconnected: %s", session.session_id)
    except Exception as e:
        logger.error("WebSocket error: %s", e, exc_info=True)
    finally:
        if stt_client:
            await stt_client.close()
        if tts_client:
            await tts_client.close()
        if notion_flush_task:
            notion_flush_task.cancel()
        await trail_writer.flush()
        logger.info("Session ended: %s", session.session_id)
