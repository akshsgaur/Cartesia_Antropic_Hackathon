"""
Natural conversation flow with immediate acknowledgments and thinking fillers.
Makes RepoBuddy feel like talking to a friend rather than a robot.
"""

import random
import re
import logging
from typing import Any

logger = logging.getLogger(__name__)


def _matches_phrase(text: str, phrases: list[str]) -> bool:
    """Check if text matches any phrase using word boundaries (not substring)."""
    lowered = text.lower().strip().rstrip(".!?,")
    for phrase in phrases:
        # Use word boundary regex to avoid false matches like "hi" in "this"
        if re.search(r'\b' + re.escape(phrase) + r'\b', lowered):
            return True
    return False


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
}

# Greeting patterns — only match standalone greetings, not words containing them
GREETING_PATTERNS = ["hello", "hey there", "greetings"]
# "hi" and "hey" only match at the START of the sentence to avoid false positives
GREETING_START_PATTERNS = ["hi", "hey"]


def get_immediate_acknowledgment(user_text: str, intent: str = "") -> str:
    """Get an immediate acknowledgment to start the conversation naturally."""
    if intent == "greeting":
        return random.choice(QUICK_RESPONSES["greeting"])
    return random.choice(IMMEDIATE_RESPONSES)


def get_thinking_filler() -> str:
    """Get a thinking filler to play while processing."""
    return random.choice(THINKING_FILLERS)


def get_ready_transition() -> str:
    """Get a transition phrase when ready with the answer."""
    return random.choice(READY_TRANSITIONS)


def classify_question_type(user_text: str) -> str:
    """Quick classification for immediate responses.

    Only 'greeting' triggers a canned response — everything else goes to Claude.
    """
    lowered = user_text.lower().strip().rstrip(".!?,")

    # Check for standalone greetings (whole message is basically just a greeting)
    # Only short messages (under 5 words) can be greetings
    words = lowered.split()
    if len(words) <= 4:
        if _matches_phrase(lowered, GREETING_PATTERNS):
            return "greeting"
        # "hi" and "hey" only match at the very start
        if words and words[0] in GREETING_START_PATTERNS:
            return "greeting"

    return "general"
