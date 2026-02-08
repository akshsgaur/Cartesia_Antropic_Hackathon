# Notion Integration Setup Guide

## 📋 **Quick Setup Checklist**

- [ ] Create Notion integration token
- [ ] Create Parent Page for onboarding trails  
- [ ] Create Curriculum Page with learning content
- [ ] Get Page IDs from URLs
- [ ] Update .env file with IDs
- [ ] Test integration

---

## 🔑 **Step 1: Create Notion Integration**

1. **Go to Notion Developers**: https://www.notion.so/my-integrations
2. **Create New Integration**:
   - Click "New integration"
   - Give it a name: "RepoBuddy Onboarding"
   - Select your workspace
   - Set permissions: Read content, Write content, Update content
   - Copy the **Integration Token** (starts with `secret_`)

3. **Add to .env**:
```bash
NOTION_API_KEY=secret_your_integration_token_here
```

## 📄 **Step 2: Create Notion Pages**

### **Parent Page (for tracking)**
1. Create page: "RepoBuddy Onboarding Trails"
2. Set as database or regular page
3. This will automatically store:
   - Session logs
   - Progress tracking
   - Milestone achievements
   - Quest completion records

### **Curriculum Page (for content)**
1. Create page: "Engineering Onboarding Curriculum"  
2. Copy content from `ONBOARDING_GUIDE.md`
3. Structure with:
   - Weekly sections
   - Learning objectives
   - Milestone checkboxes
   - Progress tracking tables

## 🔍 **Step 3: Get Page IDs**

### **From URL Method (Easiest)**
1. Open each Notion page
2. Copy the URL from browser
3. Extract the ID (32-character string after last `/`)

**Example**:
```
URL: https://www.notion.so/workspace/RepoBuddy-Onboarding-Trails-a1b2c3d4e5f67890a1b2c3d4e5f67890
ID:  a1b2c3d4e5f67890a1b2c3d4e5f67890
```

### **Update .env File**:
```bash
NOTION_PARENT_PAGE_ID=a1b2c3d4e5f67890a1b2c3d4e5f67890
NOTION_CURRICULUM_PAGE_ID=b2c3d4e5f67890a1b2c3d4e5f67890a1
```

## 🧪 **Step 4: Test Integration**

### **Test Script** (optional):
```python
# test_notion.py
from notion_client import Client
import os

notion = Client(auth=os.getenv("NOTION_API_KEY"))

# Test parent page access
parent_page = notion.pages.retrieve(os.getenv("NOTION_PARENT_PAGE_ID"))
print(f"Parent page: {parent_page['properties']['title']}")

# Test curriculum page access  
curriculum_page = notion.pages.retrieve(os.getenv("NOTION_CURRICULUM_PAGE_ID"))
print(f"Curriculum page: {curriculum_page['properties']['title']}")
```

### **Run Test**:
```bash
cd server
python test_notion.py
```

## ✅ **Integration Verification**

Once configured, RepoBuddy will:

1. **Read Curriculum**: Automatically load learning objectives from curriculum page
2. **Track Progress**: Update progress on curriculum page
3. **Log Sessions**: Create detailed session logs in parent page
4. **Monitor Milestones**: Track and celebrate milestone achievements

## 🚨 **Troubleshooting**

### **Common Issues**:

**"Unauthorized" Error**:
- Check NOTION_API_KEY is correct
- Ensure integration has proper permissions
- Verify integration is added to workspace

**"Page not found" Error**:
- Verify Page IDs are correct (32 characters, no dashes)
- Ensure pages are shared with integration
- Check pages are in correct workspace

**"Permission denied" Error**:
- Integration needs "Write content" permission
- Share pages with your integration
- Check workspace access settings

### **Debug Commands**:
```bash
# Check environment variables
echo $NOTION_API_KEY
echo $NOTION_PARENT_PAGE_ID
echo $NOTION_CURRICULUM_PAGE_ID

# Test API connection
curl -X POST "https://api.notion.com/v1/pages" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Content-Type: application/json"
```

---

## 📚 **Additional Resources**

- [Notion API Documentation](https://developers.notion.com/docs)
- [RepoBuddy AGENTS.md](./AGENTS.md) - For skill details
- [ONBOARDING_GUIDE.md](./ONBOARDING_GUIDE.md) - Complete curriculum

Once set up, RepoBuddy will automatically track onboarding progress and create persistent learning trails in Notion!
