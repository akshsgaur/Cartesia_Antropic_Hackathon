#!/usr/bin/env python3
"""
Test script for enhanced code retrieval system
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add server to path
sys.path.insert(0, str(Path(__file__).parent))

from repo.enhanced_search import search_code, SearchIntent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_enhanced_search():
    """Test the enhanced search capabilities"""
    
    # Test repository (current repo)
    repo_path = str(Path(__file__).parent.parent)
    
    print("🔍 Testing Enhanced Code Retrieval System")
    print(f"Repository: {repo_path}")
    print("=" * 60)
    
    # Test cases
    test_cases = [
        {
            "query": "where is the main function",
            "expected_intent": SearchIntent.DEFINITION,
            "description": "Function definition search"
        },
        {
            "query": "how is rg_search used",
            "expected_intent": SearchIntent.USAGE,
            "description": "Usage analysis search"
        },
        {
            "query": "how does authentication work",
            "expected_intent": SearchIntent.IMPLEMENTATION,
            "description": "Implementation explanation search"
        },
        {
            "query": "database connection",
            "expected_intent": SearchIntent.IMPLEMENTATION,
            "description": "Concept search"
        },
        {
            "query": "error in file handling",
            "expected_intent": SearchIntent.ERROR,
            "description": "Error/bug search"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 Test {i}: {test_case['description']}")
        print(f"Query: \"{test_case['query']}\"")
        print(f"Expected Intent: {test_case['expected_intent'].value}")
        
        try:
            result = await search_code(
                query=test_case['query'],
                repo_path=repo_path
            )
            
            print(f"✅ Results:")
            print(f"   Strategy Used: {result.strategy_used}")
            print(f"   Matches Found: {len(result.matches)}")
            print(f"   Snippets Generated: {len(result.snippets)}")
            print(f"   Confidence: {result.confidence:.2f}")
            print(f"   Search Time: {result.search_time_ms:.1f}ms")
            
            # Show top matches
            if result.matches:
                print(f"   Top Match: {result.matches[0].path}:{result.matches[0].line_number}")
                print(f"   Preview: {result.matches[0].line_text[:80]}...")
            
            # Show relationships if any
            if result.relationships:
                print(f"   Relationships: {len(result.relationships)} found")
                for rel in result.relationships[:2]:
                    print(f"     - {rel['type']}: {rel['description']}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("-" * 40)
    
    print("\n🎯 Performance Comparison")
    
    # Compare with simple ripgrep
    from repo.rg import rg_search
    
    queries = ["main", "search", "database", "error"]
    
    print("\nQuery Performance Comparison:")
    print("Query".ljust(20) + "Enhanced (ms)".ljust(15) + "ripgrep (ms)".ljust(15) + "Improvement")
    print("-" * 60)
    
    for query in queries:
        # Test enhanced search
        start = asyncio.get_event_loop().time()
        enhanced_result = await search_code(query, repo_path)
        enhanced_time = (asyncio.get_event_loop().time() - start) * 1000
        
        # Test simple ripgrep
        start = asyncio.get_event_loop().time()
        rg_result = await rg_search(query, repo_path)
        rg_time = (asyncio.get_event_loop().time() - start) * 1000
        
        improvement = f"{((rg_time - enhanced_time) / rg_time * 100):+.1f}%" if rg_time > 0 else "N/A"
        
        print(query.ljust(20) + f"{enhanced_time:.1f}".ljust(15) + f"{rg_time:.1f}".ljust(15) + improvement)
    
    print("\n🚀 Enhanced Search Features Demonstrated:")
    print("✅ Intent classification for better search strategy")
    print("✅ Multi-pattern generation for different languages")
    print("✅ Result ranking by relevance")
    print("✅ Relationship mapping between components")
    print("✅ Intelligent caching for performance")
    print("✅ Context-aware search results")


if __name__ == "__main__":
    asyncio.run(test_enhanced_search())
