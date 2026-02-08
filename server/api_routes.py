"""HTTP API endpoints for Line agent tool calls (via ngrok)."""
from __future__ import annotations

import json
import logging
from typing import Any

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

import config
from repo.rg import rg_search
from repo.file import open_snippet, open_around_match
from repo.scan import scan_repo
from repo.evidence import collect_evidence
from notion.write_trail import TrailWriter
from notion.read_curriculum import load_curriculum
from anthropic_client import call_claude, parse_json_response
from orchestrator.prompts import SYNTHESIZER_PROMPT

logger = logging.getLogger(__name__)

api_router = APIRouter(prefix="/api", tags=["api"])

# Shared state — set once on session start, reused across requests
_repo_path: str = config.REPO_PATH or ""
_repo_scan_cache: dict[str, Any] | None = None
_trail_writer = TrailWriter()


def set_repo_path(path: str) -> None:
    global _repo_path, _repo_scan_cache
    _repo_path = path
    _repo_scan_cache = None  # invalidate cache


def get_repo_path() -> str:
    return _repo_path


# ---------- Request / Response models ----------

class SearchRequest(BaseModel):
    pattern: str
    max_results: int = 20
    file_glob: str | None = None


class ReadFileRequest(BaseModel):
    path: str
    start: int = 1
    end: int = 50


class NotionLogRequest(BaseModel):
    page_id: str
    user_text: str
    assistant_text: str


class AnalyzeRequest(BaseModel):
    question: str
    rg_patterns: list[str] = []
    candidate_files: list[str] = []
    curriculum_json: str = ""
    recent_turns: str = ""


# ---------- Endpoints ----------

@api_router.post("/search")
async def search_code(req: SearchRequest):
    """Ripgrep search — returns matches."""
    repo = get_repo_path()
    if not repo:
        raise HTTPException(status_code=400, detail="No repo path configured")

    matches = await rg_search(
        pattern=req.pattern,
        repo_path=repo,
        max_results=req.max_results,
        file_glob=req.file_glob,
    )
    return {
        "matches": [
            {"path": m.path, "line_number": m.line_number, "line_text": m.line_text}
            for m in matches
        ]
    }


@api_router.post("/read_file")
async def read_file(req: ReadFileRequest):
    """Read a file snippet — returns content."""
    repo = get_repo_path()
    if not repo:
        raise HTTPException(status_code=400, detail="No repo path configured")

    snippet = open_snippet(repo, req.path, req.start, req.end)
    if snippet is None:
        raise HTTPException(status_code=404, detail=f"File not found: {req.path}")

    return {
        "path": snippet.path,
        "start": snippet.start,
        "end": snippet.end,
        "text": snippet.text,
    }


@api_router.get("/repo_scan")
async def get_repo_scan():
    """Return cached repo scan summary."""
    global _repo_scan_cache

    repo = get_repo_path()
    if not repo:
        raise HTTPException(status_code=400, detail="No repo path configured")

    if _repo_scan_cache is None:
        scan = await scan_repo(repo)
        _repo_scan_cache = {
            "tree": scan.tree,
            "extensions": scan.extensions,
            "frameworks": scan.frameworks,
            "languages": scan.languages,
            "total_files": scan.total_files,
            "summary": scan.summary(),
        }

    return _repo_scan_cache


@api_router.post("/notion/log")
async def notion_log(req: NotionLogRequest):
    """Log a chat turn to Notion trail."""
    try:
        await _trail_writer.append_chat_turn(
            req.page_id, req.user_text, req.assistant_text
        )
        await _trail_writer.flush()
        return {"status": "ok"}
    except Exception as e:
        logger.error("Notion log error: %s", e)
        return {"status": "error", "detail": str(e)}


@api_router.get("/curriculum")
async def get_curriculum(page_id: str = ""):
    """Return parsed curriculum JSON."""
    pid = page_id or config.NOTION_CURRICULUM_PAGE_ID
    if not pid:
        return {"curriculum": None}

    curriculum = await load_curriculum(pid)
    if curriculum is None:
        return {"curriculum": None}

    return {"curriculum": curriculum.to_dict()}


@api_router.get("/token")
async def get_calls_token():
    """Return Cartesia agent info for Calls API."""
    if not config.CARTESIA_API_KEY:
        raise HTTPException(status_code=500, detail="CARTESIA_API_KEY not set")
    
    # For development, return the deployed agent ID
    # The client will use this to connect directly to the deployed agent
    return {
        "agent_id": "agent_aFXBG3ULr9CUndb4zHr6dv",
        "endpoint": f"wss://api.cartesia.ai/agents/stream/agent_aFXBG3ULr9CUndb4zHr6dv"
    }


@api_router.post("/analyze")
async def analyze_question(req: AnalyzeRequest):
    """Deep analysis: collect evidence + synthesize answer via Claude Sonnet."""
    repo = get_repo_path()
    if not repo:
        raise HTTPException(status_code=400, detail="No repo path configured")

    # Collect evidence
    evidence = await collect_evidence(
        repo_path=repo,
        rg_patterns=req.rg_patterns[:3],
        candidate_files=req.candidate_files[:3] if req.candidate_files else None,
        max_snippets=5,
    )

    # Synthesize answer
    prompt = SYNTHESIZER_PROMPT.format(
        curriculum=req.curriculum_json or "(no curriculum)",
        question=req.question,
        evidence=evidence.to_prompt_text(),
        recent_turns=req.recent_turns or "(start of conversation)",
    )

    try:
        result = await call_claude(prompt, max_tokens=1000)
        data = parse_json_response(result)
        return {
            "voice_answer": data.get("voice_answer", ""),
            "detailed_answer": data.get("detailed_answer", ""),
            "evidence": evidence.to_dict(),
        }
    except Exception as e:
        logger.error("Analyze error: %s", e)
        return {
            "voice_answer": "I had trouble analyzing that.",
            "detailed_answer": str(e),
            "evidence": evidence.to_dict(),
        }
