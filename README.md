# RepoBuddy

Voice-native onboarding companion that reads a manager's Notion curriculum, guides engineers through a local codebase via voice conversation with evidence-backed answers, and logs an "Onboarding Trail" back to Notion.

**Sponsor alignment:** Cartesia (voice), Anthropic (reasoning), Notion (curriculum + persistence).

## Features

- **Voice-first interaction** — Talk to RepoBuddy about any codebase using your microphone
- **Evidence-backed answers** — Every response cites specific files and line numbers from the repo
- **Curriculum-aware** — Reads a manager's Notion page to guide onboarding priorities
- **Practice mode** — Code exploration quests with adaptive difficulty
- **Onboarding Trail** — Full conversation + quest log persisted to Notion

## Architecture

```
Browser (mic/audio) ←→ WebSocket ←→ FastAPI Server
                                        ├── Cartesia STT (ink-whisper)
                                        ├── Cartesia TTS (sonic-3)
                                        ├── Claude (routing + synthesis)
                                        ├── Repo Brain (ripgrep + file reads)
                                        └── Notion (read curriculum / write trail)
```

## Prerequisites

- **Python 3.11+**
- **ripgrep** (`rg`) — required for codebase search
  - macOS: `brew install ripgrep`
  - Ubuntu: `sudo apt install ripgrep`
  - Other: https://github.com/BurntSushi/ripgrep#installation

## Setup

1. **Clone and install dependencies:**
   ```bash
   cd server
   pip install -r requirements.txt
   ```

2. **Configure environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

   | Variable | Required | Description |
   |----------|----------|-------------|
   | `CARTESIA_API_KEY` | Yes | Cartesia API key for STT/TTS |
   | `ANTHROPIC_API_KEY` | Yes | Anthropic API key for Claude |
   | `NOTION_API_KEY` | No | Notion integration token |
   | `NOTION_PARENT_PAGE_ID` | No | Page under which trail pages are created |
   | `NOTION_CURRICULUM_PAGE_ID` | No | Manager's curriculum page ID |
   | `REPO_PATH` | No | Default repo path (can also be set in UI) |
   | `CARTESIA_VOICE_ID` | No | Cartesia voice UUID |
   | `PORT` | No | Server port (default: 3000) |

3. **Run the server:**
   ```bash
   cd server
   python main.py
   ```

4. **Open the app:**
   Navigate to http://localhost:3000

## Quick Demo (3 minutes)

1. Start the server and open http://localhost:3000
2. Enter a repo path (e.g., `/path/to/your/project`) and click **Start Session**
3. Hold the microphone button and ask: *"Where does the server start?"*
4. See the transcript, hear the voice response, and view code evidence in the right panel
5. Toggle to **Practice** mode — a code exploration quest will be presented
6. Answer by voice — get graded with feedback
7. If Notion is configured, click the trail link to see the full log

## How It Works

### Chat Mode (2 Claude calls per turn)
1. **Router + Planner**: Classifies intent, generates ripgrep patterns and candidate files
2. **Execute**: Runs ripgrep searches, opens file snippets around matches
3. **Synthesizer**: Produces a voice-friendly answer + detailed markdown with citations
4. Stream voice answer to TTS, send evidence to UI, queue Notion log

### Practice Mode
- 10 quest templates covering common codebase exploration tasks
- Claude specializes each template for the specific repo
- Adaptive difficulty: 2 passes = level up, 2 fails = level down
- Grading with encouraging feedback

## Tech Stack

- **Backend**: Python, FastAPI, WebSockets
- **Voice**: Cartesia STT (ink-whisper) + TTS (sonic-3)
- **Reasoning**: Anthropic Claude
- **Persistence**: Notion API
- **Search**: ripgrep
- **Frontend**: Vanilla HTML/JS/CSS (no build step)
