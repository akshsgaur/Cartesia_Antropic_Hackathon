from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any


# --- WebSocket message types ---

# Client → Server
MSG_AUDIO_IN = "audio_in"
MSG_MODE_SWITCH = "mode_switch"
MSG_START_SESSION = "start_session"
MSG_STOP_SESSION = "stop_session"

# Server → Client
MSG_TRANSCRIPT = "transcript"
MSG_RESPONSE_TEXT = "response_text"
MSG_AUDIO_CHUNK = "audio_chunk"
MSG_AUDIO_DONE = "audio_done"
MSG_EVIDENCE = "evidence"
MSG_QUEST = "quest"
MSG_QUEST_RESULT = "quest_result"
MSG_SESSION_INFO = "session_info"
MSG_MODE_CHANGED = "mode_changed"
MSG_CURRICULUM = "curriculum"
MSG_ERROR = "error"


# --- Repo types ---

@dataclass
class RgMatch:
    path: str
    line_number: int
    line_text: str


@dataclass
class FileSnippet:
    path: str
    start: int
    end: int
    text: str


@dataclass
class EvidencePack:
    matches: list[RgMatch] = field(default_factory=list)
    snippets: list[FileSnippet] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "matches": [
                {"path": m.path, "line_number": m.line_number, "line_text": m.line_text}
                for m in self.matches
            ],
            "snippets": [
                {"path": s.path, "start": s.start, "end": s.end, "text": s.text}
                for s in self.snippets
            ],
            "notes": self.notes,
        }

    def to_prompt_text(self) -> str:
        parts: list[str] = []
        for s in self.snippets:
            parts.append(f"--- {s.path} (lines {s.start}-{s.end}) ---\n{s.text}")
        for m in self.matches:
            parts.append(f"{m.path}:{m.line_number}: {m.line_text}")
        if self.notes:
            parts.append("Notes: " + "; ".join(self.notes))
        return "\n\n".join(parts) if parts else "(no evidence found)"


@dataclass
class RepoScan:
    tree: str
    extensions: dict[str, int]
    frameworks: list[str]
    languages: list[str]
    total_files: int

    def summary(self) -> str:
        langs = ", ".join(self.languages) if self.languages else "unknown"
        fws = ", ".join(self.frameworks) if self.frameworks else "none detected"
        top_ext = sorted(self.extensions.items(), key=lambda x: -x[1])[:8]
        ext_str = ", ".join(f"{e}({c})" for e, c in top_ext)
        return (
            f"Languages: {langs}\nFrameworks: {fws}\n"
            f"Files: {self.total_files}\nTop extensions: {ext_str}"
        )


# --- Curriculum types ---

@dataclass
class CurriculumModule:
    name: str
    topics: list[str]
    key_files: list[str]


@dataclass
class CurriculumMilestone:
    description: str
    day_target: int


@dataclass
class Curriculum:
    title: str
    goals: list[str]
    modules: list[CurriculumModule]
    milestones: list[CurriculumMilestone]

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "goals": self.goals,
            "modules": [
                {"name": m.name, "topics": m.topics, "key_files": m.key_files}
                for m in self.modules
            ],
            "milestones": [
                {"description": ms.description, "day_target": ms.day_target}
                for ms in self.milestones
            ],
        }


# --- Quest types ---

@dataclass
class Quest:
    id: str
    title: str
    description: str
    difficulty: int  # 1-3
    rg_patterns: list[str]
    keywords: list[str]
    file_hints: list[str]
    expected_findings: list[str]


@dataclass
class QuestResult:
    quest_id: str
    grade: str  # "pass", "partial", "fail"
    score: int  # 0-100
    feedback: str
    evidence: EvidencePack


# --- Session state ---

@dataclass
class SessionState:
    session_id: str
    mode: str = "chat"  # "chat" or "practice"
    repo_path: str = ""
    repo_scan: RepoScan | None = None
    curriculum: Curriculum | None = None
    trail_page_id: str = ""
    trail_page_url: str = ""
    conversation_history: list[dict[str, str]] = field(default_factory=list)
    completed_quests: list[str] = field(default_factory=list)
    current_quest: Quest | None = None
    quest_level: int = 1
    consecutive_passes: int = 0
    consecutive_fails: int = 0
    glossary: dict[str, str] = field(default_factory=dict)
    is_speaking: bool = False
    tts_context_id: str = ""

    def add_turn(self, role: str, content: str) -> None:
        self.conversation_history.append({"role": role, "content": content})

    def recent_turns(self, n: int = 3) -> list[dict[str, str]]:
        return self.conversation_history[-n * 2:] if self.conversation_history else []
