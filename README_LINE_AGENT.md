# RepoBuddy - Voice-Native Code Onboarding with Cartesia Line Platform

## 🎯 Overview

RepoBuddy helps engineers explore unfamiliar codebases through natural voice conversation. This version uses the **Cartesia Line Platform** for professional-grade audio handling with built-in VAD, turn-taking, and barge-in capabilities.

## 🏗️ Architecture

```
Browser
├── Calls API WebSocket → Cartesia Line Platform (audio I/O, turn-taking)
│     ↓
│   Our Line Agent (on Cartesia cloud)
│     ├── Claude (LlmAgent) — conversation reasoning
│     └── Custom tools → HTTP calls to our server (via ngrok)
│     
└── Our FastAPI Server WebSocket (evidence, curriculum, quests, session state)
      ├── Repo Brain (ripgrep, file reads)
      ├── Notion API (curriculum, trail)
      └── Pushes structured data to client
```

## 🚀 Quick Start

### Prerequisites
- **Cartesia API Key** - Get from [Cartesia Console](https://console.cartesia.ai)
- **Anthropic API Key** - Get from [Anthropic Console](https://console.anthropic.com)
- **ngrok** - For exposing local server to Cartesia Line agent
- **Python 3.11+** and **ripgrep** (`brew install ripgrep`)

### Automated Setup
```bash
# Clone and navigate
git clone https://github.com/akshsgaur/Cartesia_Antropic_Hackathon.git
cd Cartesia_Antropic_Hackathon

# Set environment variables
export CARTESIA_API_KEY=your_cartesia_key
export ANTHROPIC_API_KEY=your_anthropic_key

# Run automated setup
./setup_line_agent.sh
```

### Manual Setup

#### 1. Install Dependencies
```bash
# Install Cartesia CLI
curl -fsSL https://cartesia.sh | sh

# Install Line SDK
cd server && pip install cartesia-line && cd ..

# Install server dependencies
cd server && pip install -r requirements.txt && cd ..
```

#### 2. Set up ngrok Tunnel
```bash
# Start ngrok (in background)
ngrok http 3000 &

# Get your ngrok URL
export NGROK_URL=$(curl -s http://127.0.0.1:4040/api/tunnels | grep -o 'https://[^"]*\.ngrok\.io')
```

#### 3. Deploy Line Agent
```bash
cd line_agent

# Set environment
export CARTESIA_API_KEY=your_key
export ANTHROPIC_API_KEY=your_key  
export SERVER_URL=$NGROK_URL

# Deploy to Cartesia
cartesia deploy

# Get agent ID
cartesia agents ls
```

#### 4. Start Local Server
```bash
cd server
python main.py
```

#### 5. Use RepoBuddy
1. Open `https://localhost:3000` in browser
2. Enter repository path and click "Start Session"
3. Click microphone button and speak naturally!
4. Enjoy voice-powered code exploration 🎉

## 📁 Project Structure

```
├── server/                    # FastAPI backend
│   ├── api_routes.py         # HTTP endpoints for Line agent tools
│   ├── main.py              # FastAPI app with API router
│   ├── ws_handler.py         # Simplified data WebSocket handler
│   ├── cartesia_tts.py       # Legacy TTS (kept for reference)
│   └── ...                 # Other existing modules
├── line_agent/               # Cartesia Line agent
│   ├── main.py              # VoiceAgentApp with Claude integration
│   ├── tools.py             # Custom HTTP tools (loopback to our server)
│   ├── cartesia.toml        # Deployment configuration
│   └── pyproject.toml       # Dependencies
├── client/
│   ├── app_calls_api.js      # New client with Calls API support
│   ├── app.js               # Original client (fallback)
│   └── index.html           # Updated to use Calls API
└── setup_line_agent.sh       # Automated setup script
```

## 🔧 API Endpoints

The server exposes HTTP endpoints that the Line agent calls:

- `POST /api/search` - Ripgrep search with patterns
- `POST /api/read_file` - Read file snippets
- `GET /api/repo_scan` - Get repository scan summary
- `POST /api/notion/log` - Log chat turns to Notion trail
- `GET /api/curriculum` - Get parsed curriculum
- `POST /api/token` - Proxy to Cartesia access-token API
- `POST /api/analyze` - Deep code analysis with evidence

## 🎤 Voice Features

### Natural Conversation
- **Voice Activity Detection** - Automatic speech detection
- **Turn-taking** - Natural back-and-forth conversation
- **Barge-in** - Interrupt TTS by speaking
- **Echo Cancellation** - Prevents audio feedback loops

### Audio Pipeline
- **Input**: PCM 16kHz, mono (from browser microphone)
- **Output**: PCM 24kHz, mono (to browser speakers)
- **Codecs**: Raw PCM for low latency
- **Transport**: WebSocket via Cartesia Calls API

## 🧠 Claude Integration

### Two-Tier Architecture
- **Fast Model** (`claude-haiku-4-5-20251001`) - Responsive conversation
- **Background Tools** - Deep analysis with evidence collection
- **Context Management** - Repository + curriculum in system prompt

### Custom Tools
- `search_code` - Ripgrep search across codebase
- `read_file` - Read specific files and snippets
- `get_repo_info` - Repository scan and summary
- `deep_analysis` - Complex question analysis (background)

## 📚 Notion Integration

- **Curriculum Loading** - Parse Notion pages into structured learning paths
- **Trail Logging** - Automatic session logging to Notion pages
- **Progress Tracking** - Quest completion and skill development
- **Rich Content** - Code blocks, toggles, and structured data

## 🔍 Code Search

### Evidence Collection
- **Multi-pattern Search** - Ripgrep with optimized patterns
- **File Scoping** - Target specific files for faster results
- **Snippet Extraction** - Contextual code snippets
- **Framework Detection** - Automatic tech stack identification

### Search Optimization
- **Cached Results** - Avoid repeated expensive operations
- **Pattern Generation** - Claude generates optimal ripgrep patterns
- **Result Ranking** - Relevance scoring and prioritization

## 🛠️ Development

### Local Development
```bash
# Start server (HTTP for development)
cd server
python main.py

# Or with HTTPS (for microphone testing)
python main.py  # Uses self-signed certs
```

### Line Agent Development
```bash
cd line_agent

# Test locally
cartesia dev

# Deploy to staging
cartesia deploy --env staging
```

### Debugging
- **Server Logs**: Check console for FastAPI logs
- **Line Agent Logs**: Cartesia console shows agent execution
- **Browser DevTools**: Network tab shows WebSocket traffic
- **ngrok Dashboard**: Monitor tunnel status and requests

## 🔒 Security

- **HTTPS Required** - Microphone access needs secure context
- **API Keys** - Stored in environment variables only
- **ngrok Tunnel** - Temporary public URL for agent access
- **Self-signed Certs** - Generated locally for development

## 🚀 Deployment

### Production Deployment
1. **Domain Setup** - Configure custom domain for HTTPS
2. **Environment Variables** - Set all required keys
3. **Agent Deployment** - `cartesia deploy --env production`
4. **Server Hosting** - Deploy FastAPI app (AWS, GCP, etc.)
5. **DNS Configuration** - Point domain to server
6. **SSL Certificate** - Use Let's Encrypt or similar

### Environment Variables
```bash
CARTESIA_API_KEY=your_cartesia_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
NOTION_API_KEY=your_notion_api_key
NOTION_PARENT_PAGE_ID=your_notion_parent_page
NOTION_CURRICULUM_PAGE_ID=your_curriculum_page
REPO_PATH=/path/to/repo
PORT=3000
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push branch: `git push origin feature/amazing-feature`
5. Open Pull Request

## 📄 License

MIT License - see LICENSE file for details.

## 🙏 Acknowledgments

- **Cartesia** - Voice AI platform and Line SDK
- **Anthropic** - Claude language models
- **FastAPI** - Modern Python web framework
- **Notion** - Productivity and documentation platform

---

🎉 **Happy voice coding with RepoBuddy!** 🎉
