# Quick Fix Guide for RepoBuddy

## 🚨 Current Issues

### 1. Notion Page Access (404 Errors)
**Problem**: Page IDs not found or pages not shared with integration
**Solution**: 
1. Open Notion workspace
2. Verify pages exist:
   - "RepoBuddy Onboarding Trails"
   - "Engineering Onboarding Curriculum"
3. Share pages with your "RepoBuddy Onboarding" integration
4. Get correct page IDs from URLs

### 2. Cartesia WebSocket (HTTP 400)
**Problem**: WebSocket connection rejected
**Solution**: This might resolve itself when Notion is fixed

## 🔧 Quick Fix Steps

### Step 1: Fix Notion Pages
1. Go to https://www.notion.so
2. Find/create your two pages
3. For each page:
   - Click "Share" (top right)
   - "Invite" → Select "RepoBuddy Onboarding" integration
   - Give "Full access"
4. Copy page URLs and extract IDs (32 chars before ?)

### Step 2: Update .env
Replace the page IDs with correct ones:
```bash
NOTION_PARENT_PAGE_ID=<correct_parent_id>
NOTION_CURRICULUM_PAGE_ID=<correct_curriculum_id>
```

### Step 3: Restart Server
```bash
cd server
/Users/akshitgaur/miniconda3/bin/python main.py
```

### Step 4: Test Minimal Version
If Notion issues persist, you can test RepoBuddy without Notion:
1. Comment out Notion calls in code
2. Test voice interaction and code search
3. Add Notion back after fixing

## 🎯 What Should Work
- ✅ Voice recognition (Cartesia STT)
- ✅ Code search (enhanced retrieval)
- ✅ Voice response (Blake's voice)
- ❓ Notion logging (needs page access)

## 🧪 Test Without Notion (Temporary)
Uncomment these lines in relevant files to skip Notion:
```python
# notion.write_trail(session_data)  # Comment out
# curriculum_data = await load_curriculum()  # Comment out
```

This lets you test the core voice functionality while fixing Notion setup.
