import os
from dotenv import load_dotenv

load_dotenv()

CARTESIA_API_KEY = os.environ.get("CARTESIA_API_KEY", "").strip()
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "").strip()
NOTION_API_KEY = os.environ.get("NOTION_API_KEY", "").strip()
NOTION_PARENT_PAGE_ID = os.environ.get("NOTION_PARENT_PAGE_ID", "").strip()
NOTION_CURRICULUM_PAGE_ID = os.environ.get("NOTION_CURRICULUM_PAGE_ID", "").strip()
REPO_PATH = os.environ.get("REPO_PATH", "").strip()
CARTESIA_VOICE_ID = os.environ.get("CARTESIA_VOICE_ID", "f114a467-c40a-4db8-964d-aaba89cd08fa").strip()
PORT = int(os.environ.get("PORT", "3000").strip())
