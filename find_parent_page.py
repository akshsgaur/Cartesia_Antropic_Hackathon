#!/usr/bin/env python3
"""
Find the correct parent page ID by searching for RepoBuddy pages
"""

import os
from notion_client import Client

async def find_parent_page():
    """Search for RepoBuddy Onboarding Trails page"""
    
    api_key = os.getenv("NOTION_API_KEY")
    if not api_key:
        print("❌ NOTION_API_KEY not found")
        return
    
    client = Client(auth=api_key)
    
    print("🔍 Searching for RepoBuddy Onboarding Trails page...")
    
    # Search for pages with "RepoBuddy" in the title
    search = client.search(query="RepoBuddy", page_size=10)
    
    results = search.get("results", [])
    if not results:
        print("❌ No pages found with 'RepoBuddy' in title")
        print("   Make sure you have a page with that name")
        return
    
    print(f"📄 Found {len(results)} pages:")
    for i, page in enumerate(results, 1):
        page_id = page["id"]
        title = page["properties"]["title"]["title"] if "properties" in page and "title" in page["properties"] else "Untitled"
        created = page.get("created_time", "Unknown")
        
        print(f"   {i}. {title}")
        print(f"      ID: {page_id}")
        print(f"      Created: {created}")
        print()
        
        # Look for the Onboarding Trails page specifically
        if "Onboarding" in title and "Trails" in title:
            print(f"✅ FOUND PARENT PAGE: {title}")
            print(f"   Correct ID: {page_id}")
            print(f"\n📝 Update your .env:")
            print(f"NOTION_PARENT_PAGE_ID={page_id}")
            
            return page_id
    
    print("❌ No 'RepoBuddy Onboarding Trails' page found")
    print("   Please create this page in Notion first")
    return None

if __name__ == "__main__":
    import asyncio
    asyncio.run(find_parent_page())
