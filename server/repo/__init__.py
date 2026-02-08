"""
Enhanced Code Retrieval Module

This module provides advanced code search capabilities beyond simple ripgrep:
- Intent-aware query classification
- Multi-pattern generation for different languages
- Semantic understanding of code structure
- Relationship mapping between components
- Intelligent caching for performance

Usage:
    from repo.enhanced_search import search_code
    
    result = await search_code("where is the login function", "/path/to/repo")
    print(f"Found {len(result.matches)} matches in {result.search_time_ms}ms")
"""

from .enhanced_search import (
    SearchIntent,
    SearchQuery, 
    SearchResult,
    search_code,
    enhanced_searcher
)

from .rg import rg_search
from .file import open_snippet, open_around_match, file_exists
from .evidence import collect_evidence
from .scan import scan_repo

__all__ = [
    # Enhanced search
    "SearchIntent",
    "SearchQuery", 
    "SearchResult",
    "search_code",
    "enhanced_searcher",
    
    # Original functionality
    "rg_search",
    "open_snippet", 
    "open_around_match",
    "file_exists",
    "collect_evidence",
    "scan_repo"
]