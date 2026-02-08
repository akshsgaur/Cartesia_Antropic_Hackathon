from __future__ import annotations

import os
import logging
from typing import Annotated

import httpx
from line.tools import loopback_tool

# Get server URL from environment
SERVER_URL = os.getenv("SERVER_URL", "http://localhost:3000")

logger = logging.getLogger(__name__)

@loopback_tool
async def search_code(ctx: any, query: Annotated[str, "Search pattern"]) -> str:
    """Search codebase using ripgrep."""
    try:
        resp = await httpx.post(
            f"{SERVER_URL}/api/search", 
            json={"pattern": query, "max_results": 20},
            timeout=10.0
        )
        resp.raise_for_status()
        data = resp.json()
        
        if data.get("matches"):
            results = [f"• {m['path']}:{m['line_number']} - {m['line_text']}" 
                      for m in data["matches"][:10]]
            return f"Found {len(data['matches'])} matches:\n" + "\n".join(results)
        else:
            return "No matches found"
            
    except Exception as e:
        logger.error(f"Search error: {e}")
        return f"Search failed: {e}"

@loopback_tool
async def read_file(ctx: any, path: Annotated[str, "File path"], 
                  start: Annotated[int, "Start line"] = 1, 
                  end: Annotated[int, "End line"] = 50) -> str:
    """Read a file from the repository."""
    try:
        resp = await httpx.post(
            f"{SERVER_URL}/api/read_file",
            json={"path": path, "start": start, "end": end},
            timeout=10.0
        )
        resp.raise_for_status()
        data = resp.json()
        
        return f"File: {data['path']} (lines {data['start']}-{data['end']}):\n{data['text']}"
        
    except Exception as e:
        logger.error(f"Read file error: {e}")
        return f"Failed to read file: {e}"

@loopback_tool
async def get_repo_info(ctx: any) -> str:
    """Get repository scan information."""
    try:
        resp = await httpx.get(
            f"{SERVER_URL}/api/repo_scan",
            timeout=10.0
        )
        resp.raise_for_status()
        data = resp.json()
        
        if data.get("scan"):
            scan = data["scan"]
            info = [
                f"Repository Summary:",
                f"• Total files: {scan.get('total_files', 0)}",
                f"• Languages: {', '.join(scan.get('languages', []))}",
                f"• Frameworks detected: {', '.join(scan.get('frameworks', []))}",
                f"• File extensions: {', '.join(scan.get('extensions', []))}"
            ]
            return "\n".join(info)
        else:
            return "No repository scan available"
            
    except Exception as e:
        logger.error(f"Repo info error: {e}")
        return f"Failed to get repository info: {e}"

@loopback_tool(is_background=True)
async def deep_analysis(ctx: any, question: Annotated[str, "Complex question"]) -> str:
    """Deep code analysis for complex questions. Runs in background."""
    try:
        # First yield a thinking message
        yield "Let me dig into the code for that..."
        
        # Call our server's analyze endpoint
        resp = await httpx.post(
            f"{SERVER_URL}/api/analyze",
            json={"question": question},
            timeout=30.0
        )
        resp.raise_for_status()
        data = resp.json()
        
        # Return the analysis result
        voice_answer = data.get("voice_answer", "")
        detailed_answer = data.get("detailed_answer", "")
        
        if voice_answer:
            yield voice_answer
        if detailed_answer and detailed_answer != voice_answer:
            yield f"\n\nDetails: {detailed_answer}"
            
    except Exception as e:
        logger.error(f"Deep analysis error: {e}")
        yield f"I had trouble analyzing that question: {e}"
