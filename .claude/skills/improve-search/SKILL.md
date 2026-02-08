---
name: improve-search
description: Improve code search quality — tune ripgrep patterns, enhance evidence collection, or improve the enhanced search system. Use when search results are irrelevant or missing.
user-invocable: true
---

# Improve Code Search

## When to use
- Search results don't match what the user asked about
- Evidence panel shows irrelevant or empty results
- rg_patterns from the router aren't finding the right code

## Architecture — Two search paths

### Path 1: Router-driven (used in chat pipeline)
1. `orchestrator/router.py` — Claude generates 1-3 rg_patterns + candidate_files
2. `repo/evidence.py` → `collect_evidence()` — runs rg_search for each pattern, opens snippets
3. Results go to synthesizer as EvidencePack

### Path 2: Enhanced search (standalone)
1. `repo/enhanced_search.py` — `EnhancedSearcher` class
2. `QueryClassifier` — classifies intent (definition, usage, implementation, relationship, pattern, error)
3. `PatternGenerator` — generates language-specific rg patterns
4. `MultiLevelCache` — caches results for 5 minutes
5. `RelationshipMapper` — placeholder for dependency graph (not yet implemented)

## Tuning search quality

### Router prompts (`orchestrator/prompts.py`)
The `ROUTER_PLANNER_PROMPT` tells Claude to generate rg patterns. Tune it by:
- Adding examples of good patterns for the target language
- Being more specific about what to search for
- Adjusting the number of patterns (currently 1-3)

### Evidence collection (`repo/evidence.py`)
- `max_snippets` parameter controls how many file snippets are opened (default 5)
- `open_around_match` uses a `radius` of 10 lines by default
- To show more context, increase the radius

### ripgrep wrapper (`repo/rg.py`)
- `max_results` default is 20 matches
- `file_glob` can filter by extension (e.g., `"*.py"`)
- Timeout is 10 seconds

## Key files
- `server/repo/rg.py` — ripgrep wrapper
- `server/repo/evidence.py` — evidence collector
- `server/repo/enhanced_search.py` — enhanced multi-layer search
- `server/orchestrator/router.py` — Claude-driven search planning
- `server/orchestrator/prompts.py` — ROUTER_PLANNER_PROMPT
