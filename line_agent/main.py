from __future__ import annotations

import os
import logging
from typing import Annotated

import httpx
from line.voice_agent_app import VoiceAgentApp, AgentEnv, CallRequest
from line.llm_agent import LlmAgent, LlmConfig, end_call
from tools import search_code, read_file, get_repo_info, deep_analysis

logger = logging.getLogger(__name__)

# Get server URL from environment (set by Cartesia)
SERVER_URL = os.getenv("SERVER_URL", "http://localhost:3000")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

if not ANTHROPIC_API_KEY:
    raise ValueError("ANTHROPIC_API_KEY environment variable is required")

SYSTEM_PROMPT = """You are RepoBuddy, a voice-native onboarding companion that helps engineers explore unfamiliar codebases through natural conversation.

Your role:
- Guide users through understanding new codebases
- Answer questions about code structure, patterns, and implementation
- Provide clear, concise explanations suitable for voice delivery
- Use the search and file reading tools to investigate code

Guidelines:
- Keep voice responses conversational and under 2 sentences when possible
- Use search_code to find relevant code patterns
- Use read_file to examine specific files in detail
- Use deep_analysis for complex questions that require comprehensive investigation
- Be helpful, patient, and encouraging

Current repository context will be provided by the tools.
"""

async def get_agent(env: AgentEnv, call_request: CallRequest) -> LlmAgent:
    """Create and configure the RepoBuddy agent."""
    
    # Get repo context from metadata (passed by client via start event)
    repo_url = call_request.metadata.get("server_url", SERVER_URL)
    
    logger.info(f"Starting RepoBuddy agent with server URL: {repo_url}")
    
    return LlmAgent(
        model="anthropic/claude-haiku-4-5-20251001",
        api_key=ANTHROPIC_API_KEY,
        tools=[search_code, read_file, get_repo_info, deep_analysis, end_call],
        config=LlmConfig(
            system_prompt=SYSTEM_PROMPT,
            introduction="Hey! I'm RepoBuddy. I'm here to help you explore and understand this codebase. What would you like to know?",
            temperature=0.7,
        ),
    )

# Create the voice agent app
app = VoiceAgentApp(get_agent=get_agent)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
