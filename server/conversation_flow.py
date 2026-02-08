"""
Natural conversation flow with immediate acknowledgments and thinking fillers.
Makes RepoBuddy feel like talking to a friend rather than a robot.
"""

import random
import logging
from typing import Any

logger = logging.getLogger(__name__)

# Immediate acknowledgments (under 1 second)
IMMEDIATE_RESPONSES = [
    "Hmm, that's a good question.",
    "Let me think about that for a second.",
    "Interesting! Let me look into that.",
    "Good point! One moment while I check.",
    "Ah, let me see what I can find.",
    "That's a great question! Give me a moment.",
    "Let me explore the codebase for that.",
    "Hmm, I should check the files for this.",
]

# Thinking fillers while processing (2-3 seconds)
THINKING_FILLERS = [
    "Okay, I'm looking through the code now...",
    "Let me check the repository structure...",
    "I'm searching through the files...",
    "Let me examine what we have here...",
    "Okay, I'm finding the relevant code...",
    "Let me look into the implementation...",
]

# Transition phrases when ready with answer
READY_TRANSITIONS = [
    "Okay, here's what I found:",
    "Based on what I'm seeing:",
    "Alright, so here's the deal:",
    "Okay, so from the codebase:",
    "Great! So what I can tell you is:",
    "Perfect! Here's what I discovered:",
]

# Quick acknowledgments for simple questions
QUICK_RESPONSES = {
    "greeting": [
        "Hey there! I'm RepoBuddy, nice to meet you!",
        "Hi! Ready to explore this codebase together?",
        "Hello! I'm here to help you understand this project.",
    ],
    "what_is_this": [
        "This is RepoBuddy! It's a voice-powered code exploration tool.",
        "You're looking at RepoBuddy - your friendly code exploration companion!",
        "This is the RepoBuddy repository - it helps engineers understand codebases.",
    ],
    "features": [
        "Let me tell you about the features! I can see several key ones...",
        "Great question! This project has some awesome features...",
        "Oh yeah! Let me walk you through the main features...",
    ],
}

def get_immediate_acknowledgment(user_text: str, intent: str = "") -> str:
    """Get an immediate acknowledgment to start the conversation naturally."""
    # Check for quick responses first
    lowered = user_text.lower().strip()
    
    if any(word in lowered for word in ["hello", "hi", "hey", "greetings"]):
        return random.choice(QUICK_RESPONSES["greeting"])
    
    if any(word in lowered for word in ["what is this", "what is this repository", "what am i looking at"]):
        return random.choice(QUICK_RESPONSES["what_is_this"])
    
    if any(word in lowered for word in ["features", "what can it do", "what does it do"]):
        return random.choice(QUICK_RESPONSES["features"])
    
    # Default acknowledgment
    return random.choice(IMMEDIATE_RESPONSES)

def get_thinking_filler() -> str:
    """Get a thinking filler to play while processing."""
    return random.choice(THINKING_FILLERS)

def get_ready_transition() -> str:
    """Get a transition phrase when ready with the answer."""
    return random.choice(READY_TRANSITIONS)

def classify_question_type(user_text: str) -> str:
    """Quick classification for immediate responses."""
    lowered = user_text.lower().strip()
    
    if any(word in lowered for word in ["hello", "hi", "hey", "greetings"]):
        return "greeting"
    
    if any(word in lowered for word in ["what is this", "what is this repository", "what am i looking at", "what is"]):
        return "what_is_this"
    
    if any(word in lowered for word in ["features", "what can it do", "what does it do", "tell me about"]):
        return "features"
    
    if any(word in lowered for word in ["how", "how does", "how do"]):
        return "how_question"
    
    if any(word in lowered for word in ["where", "where is", "where can"]):
        return "where_question"
    
    return "general"
