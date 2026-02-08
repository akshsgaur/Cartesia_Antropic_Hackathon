#!/usr/bin/env python3
"""
Test Notion connection and verify page IDs
"""

import os
import asyncio
from notion_client import Client

async def test_notion_connection():
    """Test Notion API connection and page access"""
    
    api_key = os.getenv("NOTION_API_KEY")
    parent_page_id = os.getenv("NOTION_PARENT_PAGE_ID")
    curriculum_page_id = os.getenv("NOTION_CURRICULUM_PAGE_ID")
    
    if not api_key:
        print("❌ NOTION_API_KEY not found")
        return
    
    print("🔑 Testing Notion API connection...")
    print(f"API Key: {api_key[:20]}...")
    print(f"Parent Page ID: {parent_page_id}")
    print(f"Curriculum Page ID: {curriculum_page_id}")
    
    client = Client(auth=api_key)
    
    try:
        # Test 1: Try to retrieve parent page
        print(f"\n📄 Testing parent page access...")
        try:
            parent_page = client.pages.retrieve(page_id=parent_page_id)
            print(f"✅ Parent page found: {parent_page['properties']['title']['title']}")
        except Exception as e:
            print(f"❌ Parent page error: {e}")
            print("   This page might not exist or isn't shared with integration")
        
        # Test 2: Try to retrieve curriculum page
        print(f"\n📚 Testing curriculum page access...")
        try:
            curriculum_page = client.pages.retrieve(page_id=curriculum_page_id)
            print(f"✅ Curriculum page found: {curriculum_page['properties']['title']['title']}")
        except Exception as e:
            print(f"❌ Curriculum page error: {e}")
            print("   This page might not exist or isn't shared with integration")
        
        # Test 3: List accessible pages
        print(f"\n📋 Listing first 5 accessible pages...")
        search = client.search(query="", page_size=5)
        for i, page in enumerate(search.get("results", []), 1):
            page_id = page["id"]
            title = page["properties"]["title"]["title"] if "properties" in page and "title" in page["properties"] else "Untitled"
            print(f"   {i}. {title} (ID: {page_id[:20]}...)")
        
        # Test 4: Try to create a test page
        print(f"\n🧪 Testing page creation...")
        try:
            test_page = client.pages.create(
                parent={"database_id": parent_page_id},
                properties={"title": {"title": "RepoBuddy Test Page"}}
            )
            print(f"✅ Test page created: {test_page['id']}")
            
            # Clean up - delete test page
            client.pages.update(page_id=test_page["id"], archived=True)
            print("✅ Test page cleaned up")
        except Exception as e:
            print(f"❌ Page creation error: {e}")
        
    except Exception as e:
        print(f"❌ Connection error: {e}")
        print("   Check your API key and permissions")

if __name__ == "__main__":
    asyncio.run(test_notion_connection())
