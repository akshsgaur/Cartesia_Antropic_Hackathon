"""
Enhanced Code Retrieval System
Multi-layered search with ripgrep + semantic understanding
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import time
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

from models import RgMatch, FileSnippet
from repo.rg import rg_search
from repo.file import open_snippet

logger = logging.getLogger(__name__)


class SearchIntent(Enum):
    DEFINITION = "definition"
    USAGE = "usage"
    IMPLEMENTATION = "implementation"
    RELATIONSHIP = "relationship"
    PATTERN = "pattern"
    ERROR = "error"


@dataclass
class SearchQuery:
    text: str
    intent: Optional[SearchIntent] = None
    language: Optional[str] = None
    file_types: Optional[List[str]] = None
    context: Optional[Dict[str, Any]] = None


@dataclass
class SearchResult:
    matches: List[RgMatch]
    snippets: List[FileSnippet]
    relationships: List[Dict[str, Any]]
    confidence: float
    search_time_ms: float
    strategy_used: str


class QueryClassifier:
    """Classify user queries for optimal search strategy"""
    
    INTENT_PATTERNS = {
        SearchIntent.DEFINITION: [
            "where is", "find definition", "locate", "defined in"
        ],
        SearchIntent.USAGE: [
            "how is used", "where used", "usage", "calls"
        ],
        SearchIntent.IMPLEMENTATION: [
            "how does", "implementation", "works", "code"
        ],
        SearchIntent.RELATIONSHIP: [
            "relates to", "connects to", "depends on", "imports"
        ],
        SearchIntent.PATTERN: [
            "like", "similar to", "pattern", "example"
        ],
        SearchIntent.ERROR: [
            "error in", "bug", "issue", "problem", "fix"
        ]
    }
    
    def classify(self, query: str) -> SearchIntent:
        """Classify query intent based on patterns"""
        query_lower = query.lower()
        
        for intent, patterns in self.INTENT_PATTERNS.items():
            if any(pattern in query_lower for pattern in patterns):
                return intent
        
        return SearchIntent.IMPLEMENTATION  # Default


class PatternGenerator:
    """Generate search patterns for different languages and intents"""
    
    LANGUAGE_PATTERNS = {
        "python": {
            SearchIntent.DEFINITION: [
                r"def\s+{term}\s*\(",
                r"class\s+{term}\s*\(",
                r"{term}\s*=\s*",
                r"import\s+{term}",
                r"from\s+.*import\s+{term}"
            ],
            SearchIntent.USAGE: [
                r"{term}\s*\(",
                r"\.{term}\s*\(",
                r"{term}\.",
                r"\[{term}\]"
            ],
            SearchIntent.IMPLEMENTATION: [
                r"{term}",
                r"{term}.*",
                r".*{term}.*"
            ]
        },
        "javascript": {
            SearchIntent.DEFINITION: [
                r"function\s+{term}\s*\(",
                r"const\s+{term}\s*=",
                r"class\s+{term}",
                r"var\s+{term}\s*=",
                r"let\s+{term}\s*="
            ],
            SearchIntent.USAGE: [
                r"{term}\s*\(",
                r"\.{term}\s*\(",
                r"{term}\.",
                r"{term}\["
            ],
            SearchIntent.IMPLEMENTATION: [
                r"{term}",
                r"{term}.*",
                r".*{term}.*"
            ]
        },
        "typescript": {
            SearchIntent.DEFINITION: [
                r"function\s+{term}\s*\(",
                r"const\s+{term}\s*=",
                r"class\s+{term}",
                r"interface\s+{term}",
                r"type\s+{term}\s*="
            ],
            SearchIntent.USAGE: [
                r"{term}\s*\(",
                r"\.{term}\s*\(",
                r"{term}\.",
                r"{term}<"
            ],
            SearchIntent.IMPLEMENTATION: [
                r"{term}",
                r"{term}.*",
                r".*{term}.*"
            ]
        }
    }
    
    def generate_patterns(self, query: SearchQuery) -> List[str]:
        """Generate search patterns based on intent and language"""
        patterns = []
        
        # Extract search term (remove question words)
        term = self._extract_term(query.text)
        
        if not term:
            return [query.text]  # Fallback to original query
        
        # Get language-specific patterns
        lang_patterns = self.LANGUAGE_PATTERNS.get(query.language, {})
        intent_patterns = lang_patterns.get(query.intent, [])
        
        # Generate patterns
        for pattern_template in intent_patterns:
            patterns.append(pattern_template.format(term=term))
        
        # Add fallback patterns
        if not patterns:
            patterns.extend([
                rf"\b{term}\b",
                rf"{term}",
                rf".*{term}.*"
            ])
        
        return patterns
    
    def _extract_term(self, query: str) -> str:
        """Extract the main search term from query"""
        # Remove common question words and patterns
        stop_words = {
            "where", "is", "the", "a", "an", "and", "or", "but", "in", "on", "at",
            "to", "for", "of", "with", "by", "how", "does", "do", "can", "could",
            "would", "should", "find", "locate", "search", "look", "show", "tell"
        }
        
        words = query.lower().split()
        filtered = [w for w in words if w not in stop_words and len(w) > 1]
        
        # Return the most significant word (usually last)
        return filtered[-1] if filtered else ""


class MultiLevelCache:
    """Hierarchical caching system"""
    
    def __init__(self):
        self.l1_memory: Dict[str, Tuple[Any, float]] = {}  # (result, timestamp)
        self.l2_disk: Dict[str, Any] = {}  # Persistent cache
        self.cache_ttl = 300  # 5 minutes
    
    def _get_cache_key(self, query: SearchQuery) -> str:
        """Generate cache key for query"""
        key_data = {
            "text": query.text,
            "intent": query.intent.value if query.intent else None,
            "language": query.language,
            "file_types": query.file_types
        }
        return hashlib.md5(json.dumps(key_data, sort_keys=True).encode()).hexdigest()
    
    async def get(self, query: SearchQuery) -> Optional[SearchResult]:
        """Get cached result"""
        key = self._get_cache_key(query)
        current_time = time.time()
        
        # Check L1 cache
        if key in self.l1_memory:
            result, timestamp = self.l1_memory[key]
            if current_time - timestamp < self.cache_ttl:
                return result
            else:
                del self.l1_memory[key]
        
        # Check L2 cache (simplified - in production use disk storage)
        if key in self.l2_disk:
            result = self.l2_disk[key]
            # Promote to L1
            self.l1_memory[key] = (result, current_time)
            return result
        
        return None
    
    async def set(self, query: SearchQuery, result: SearchResult) -> None:
        """Cache result"""
        key = self._get_cache_key(query)
        current_time = time.time()
        
        # Store in both levels
        self.l1_memory[key] = (result, current_time)
        self.l2_disk[key] = result
        
        # Cleanup old entries (simple LRU)
        if len(self.l1_memory) > 100:
            oldest_key = min(self.l1_memory.keys(), 
                           key=lambda k: self.l1_memory[k][1])
            del self.l1_memory[oldest_key]


class RelationshipMapper:
    """Map relationships between code components"""
    
    def __init__(self):
        self.import_graph: Dict[str, Set[str]] = {}
        self.call_graph: Dict[str, Set[str]] = {}
        self.dependency_graph: Dict[str, Set[str]] = {}
    
    async def build_relationships(self, repo_path: str) -> None:
        """Build relationship graphs for the repository"""
        logger.info("Building relationship graphs...")
        
        # This is a simplified implementation
        # In production, use AST parsing for accurate results
        
        # Find imports and build dependency graph
        import_patterns = [
            r"import\s+(\w+)",
            r"from\s+(\w+)\s+import",
            r"require\s*\(['\"]([^'\"]+)['\"]",
            r"#include\s*[<\"]([^>\"]+)[>\"]"
        ]
        
        # Build call graph (simplified)
        call_patterns = [
            r"(\w+)\s*\(",
            r"\.(\w+)\s*\("
        ]
        
        # For now, create placeholder relationships
        # In production, implement full AST parsing
        logger.info("Relationship graphs built (simplified implementation)")
    
    async def find_related(self, symbol: str) -> List[Dict[str, Any]]:
        """Find symbols related to the given symbol"""
        relationships = []
        
        # Check imports
        if symbol in self.import_graph:
            for imported in self.import_graph[symbol]:
                relationships.append({
                    "type": "import",
                    "target": imported,
                    "description": f"{symbol} imports {imported}"
                })
        
        # Check function calls
        if symbol in self.call_graph:
            for called in self.call_graph[symbol]:
                relationships.append({
                    "type": "calls",
                    "target": called,
                    "description": f"{symbol} calls {called}"
                })
        
        return relationships


class EnhancedSearcher:
    """Enhanced multi-layered search system"""
    
    def __init__(self):
        self.classifier = QueryClassifier()
        self.pattern_generator = PatternGenerator()
        self.cache = MultiLevelCache()
        self.relationship_mapper = RelationshipMapper()
        self._repo_path: Optional[str] = None
    
    async def initialize(self, repo_path: str) -> None:
        """Initialize the searcher with repository path"""
        self._repo_path = repo_path
        await self.relationship_mapper.build_relationships(repo_path)
        logger.info(f"Enhanced searcher initialized for {repo_path}")
    
    async def search(self, query_text: str, **kwargs) -> SearchResult:
        """Main search interface"""
        start_time = time.time()
        
        # Build query object
        query = SearchQuery(
            text=query_text,
            intent=kwargs.get("intent"),
            language=kwargs.get("language"),
            file_types=kwargs.get("file_types"),
            context=kwargs.get("context", {})
        )
        
        # Check cache first
        cached_result = await self.cache.get(query)
        if cached_result:
            logger.debug(f"Cache hit for query: {query_text}")
            return cached_result
        
        # Classify intent if not provided
        if not query.intent:
            query.intent = self.classifier.classify(query.text)
        
        # Detect language if not provided
        if not query.language:
            query.language = self._detect_language(query.file_types)
        
        # Execute search strategy
        result = await self._execute_search_strategy(query)
        
        # Calculate search time
        result.search_time_ms = (time.time() - start_time) * 1000
        
        # Cache result
        await self.cache.set(query, result)
        
        return result
    
    async def _execute_search_strategy(self, query: SearchQuery) -> SearchResult:
        """Execute the appropriate search strategy"""
        
        if query.intent == SearchIntent.DEFINITION:
            return await self._definition_search(query)
        elif query.intent == SearchIntent.USAGE:
            return await self._usage_search(query)
        elif query.intent == SearchIntent.RELATIONSHIP:
            return await self._relationship_search(query)
        else:
            return await self._general_search(query)
    
    async def _definition_search(self, query: SearchQuery) -> SearchResult:
        """Search for definitions of functions, classes, etc."""
        patterns = self.pattern_generator.generate_patterns(query)
        
        all_matches = []
        for pattern in patterns:
            matches = await rg_search(pattern, self._repo_path, max_results=10)
            all_matches.extend(matches)
        
        # Rank by definition likelihood
        ranked_matches = self._rank_definitions(all_matches, query)
        
        # Get snippets for top matches
        snippets = []
        for match in ranked_matches[:5]:
            snippet = open_snippet(self._repo_path, match.path, 
                                 max(1, match.line_number - 5),
                                 match.line_number + 5)
            if snippet:
                snippets.append(snippet)
        
        return SearchResult(
            matches=ranked_matches,
            snippets=snippets,
            relationships=[],
            confidence=0.8,
            search_time_ms=0,  # Will be set by caller
            strategy_used="definition_search"
        )
    
    async def _usage_search(self, query: SearchQuery) -> SearchResult:
        """Search for usage of functions, classes, etc."""
        patterns = self.pattern_generator.generate_patterns(query)
        
        all_matches = []
        for pattern in patterns:
            matches = await rg_search(pattern, self._repo_path, max_results=15)
            all_matches.extend(matches)
        
        # Filter out definitions, keep usages
        usage_matches = self._filter_usages(all_matches, query)
        
        # Get snippets for top matches
        snippets = []
        for match in usage_matches[:5]:
            snippet = open_snippet(self._repo_path, match.path,
                                 max(1, match.line_number - 3),
                                 match.line_number + 3)
            if snippet:
                snippets.append(snippet)
        
        return SearchResult(
            matches=usage_matches,
            snippets=snippets,
            relationships=[],
            confidence=0.7,
            search_time_ms=0,
            strategy_used="usage_search"
        )
    
    async def _relationship_search(self, query: SearchQuery) -> SearchResult:
        """Search for relationships between components"""
        # First find the symbol
        definition_result = await self._definition_search(query)
        
        # Then find relationships
        relationships = []
        if definition_result.matches:
            symbol = self.pattern_generator._extract_term(query.text)
            relationships = await self.relationship_mapper.find_related(symbol)
        
        return SearchResult(
            matches=definition_result.matches,
            snippets=definition_result.snippets,
            relationships=relationships,
            confidence=0.6,
            search_time_ms=0,
            strategy_used="relationship_search"
        )
    
    async def _general_search(self, query: SearchQuery) -> SearchResult:
        """General purpose search"""
        # Use original text as pattern
        matches = await rg_search(query.text, self._repo_path, max_results=20)
        
        # Get snippets for top matches
        snippets = []
        for match in matches[:5]:
            snippet = open_snippet(self._repo_path, match.path,
                                 max(1, match.line_number - 5),
                                 match.line_number + 5)
            if snippet:
                snippets.append(snippet)
        
        return SearchResult(
            matches=matches,
            snippets=snippets,
            relationships=[],
            confidence=0.5,
            search_time_ms=0,
            strategy_used="general_search"
        )
    
    def _detect_language(self, file_types: Optional[List[str]]) -> Optional[str]:
        """Detect programming language from file types"""
        if not file_types:
            return None
        
        language_map = {
            "py": "python",
            "js": "javascript",
            "ts": "typescript",
            "jsx": "javascript",
            "tsx": "typescript",
            "go": "go",
            "rs": "rust",
            "java": "java",
            "rb": "ruby",
            "php": "php",
            "c": "c",
            "cpp": "cpp",
            "cs": "csharp"
        }
        
        for ft in file_types:
            if ft in language_map:
                return language_map[ft]
        
        return None
    
    def _rank_definitions(self, matches: List[RgMatch], query: SearchQuery) -> List[RgMatch]:
        """Rank matches by likelihood of being definitions"""
        scored_matches = []
        
        for match in matches:
            score = 0.0
            
            line_text = match.line_text.lower()
            
            # Definition patterns
            if any(pattern in line_text for pattern in ["def ", "class ", "function ", "interface "]):
                score += 0.5
            
            # Assignment patterns
            if "=" in line_text and not line_text.strip().startswith("#"):
                score += 0.3
            
            # Import patterns
            if any(pattern in line_text for pattern in ["import ", "from ", "require "]):
                score += 0.4
            
            # Exact term match
            term = self.pattern_generator._extract_term(query.text)
            if term and term.lower() in line_text:
                score += 0.2
            
            scored_matches.append((match, score))
        
        # Sort by score (descending)
        scored_matches.sort(key=lambda x: x[1], reverse=True)
        
        return [match for match, _ in scored_matches]
    
    def _filter_usages(self, matches: List[RgMatch], query: SearchQuery) -> List[RgMatch]:
        """Filter matches to keep only usages, not definitions"""
        usages = []
        term = self.pattern_generator._extract_term(query.text)
        
        for match in matches:
            line_text = match.line_text.lower()
            
            # Skip obvious definitions
            if any(pattern in line_text for pattern in ["def ", "class ", "function ", "interface "]):
                # But include if it's a different symbol
                if term and term.lower() not in line_text:
                    usages.append(match)
                continue
            
            # Include function calls and references
            if term and term.lower() in line_text:
                usages.append(match)
        
        return usages


# Global instance
enhanced_searcher = EnhancedSearcher()


async def search_code(query: str, repo_path: str, **kwargs) -> SearchResult:
    """Main interface for enhanced code search"""
    await enhanced_searcher.initialize(repo_path)
    return await enhanced_searcher.search(query, **kwargs)
