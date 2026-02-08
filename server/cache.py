from __future__ import annotations

import hashlib
import logging
import time
from typing import Any

logger = logging.getLogger(__name__)

# Simple in-memory cache with TTL
_response_cache: dict[str, dict[str, Any]] = {}
CACHE_TTL = 300  # 5 minutes


def _get_cache_key(text: str, session_context: dict[str, Any]) -> str:
    """Generate cache key based on text and session context."""
    # Include repo path and recent turns for context
    context_str = f"{session_context.get('repo_path', '')}:{session_context.get('recent_turns_hash', '')}"
    combined = f"{text}:{context_str}"
    return hashlib.md5(combined.encode()).hexdigest()


def get_cached_response(text: str, session_context: dict[str, Any]) -> dict[str, Any] | None:
    """Get cached response if available and not expired."""
    cache_key = _get_cache_key(text, session_context)
    
    if cache_key in _response_cache:
        cached = _response_cache[cache_key]
        if time.time() - cached["timestamp"] < CACHE_TTL:
            logger.info("Cache hit for query: %s", text[:50])
            return cached["response"]
        else:
            # Expired, remove from cache
            del _response_cache[cache_key]
    
    return None


def cache_response(text: str, session_context: dict[str, Any], response: dict[str, Any]) -> None:
    """Cache a response for future use."""
    cache_key = _get_cache_key(text, session_context)
    
    _response_cache[cache_key] = {
        "response": response,
        "timestamp": time.time()
    }
    
    # Simple cache size management - keep only last 100 entries
    if len(_response_cache) > 100:
        oldest_key = min(_response_cache.keys(), 
                        key=lambda k: _response_cache[k]["timestamp"])
        del _response_cache[oldest_key]
    
    logger.info("Cached response for query: %s", text[:50])


def clear_cache() -> None:
    """Clear all cached responses."""
    global _response_cache
    _response_cache.clear()
    logger.info("Response cache cleared")
