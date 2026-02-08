import logging
import shutil
from pathlib import Path

from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

import config
from ws_handler import handle_websocket

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(title="RepoBuddy")

# Serve client files
CLIENT_DIR = Path(__file__).resolve().parent.parent / "client"
app.mount("/static", StaticFiles(directory=str(CLIENT_DIR)), name="static")


@app.get("/")
async def index():
    return FileResponse(str(CLIENT_DIR / "index.html"))


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await handle_websocket(ws)


@app.on_event("startup")
async def startup():
    # Check for ripgrep
    if not shutil.which("rg"):
        logger.warning(
            "ripgrep (rg) not found on PATH. Install it:\n"
            "  macOS: brew install ripgrep\n"
            "  Ubuntu: sudo apt install ripgrep\n"
            "  Other: https://github.com/BurntSushi/ripgrep#installation"
        )

    if not config.CARTESIA_API_KEY:
        logger.warning("CARTESIA_API_KEY not set")
    if not config.ANTHROPIC_API_KEY:
        logger.warning("ANTHROPIC_API_KEY not set")
    if not config.REPO_PATH:
        logger.warning("REPO_PATH not set — you can pass it in start_session")

    logger.info("RepoBuddy starting on port %d", config.PORT)


if __name__ == "__main__":
    import uvicorn
    
    # Generate self-signed certificate for HTTPS (required for microphone access)
    try:
        logger.info("Running HTTPS on port %d - microphone access enabled", config.PORT)
        uvicorn.run(
            "main:app", 
            host="0.0.0.0", 
            port=config.PORT, 
            reload=True,
            ssl_keyfile="server.key",
            ssl_certfile="server.crt"
        )
    except FileNotFoundError:
        logger.warning("SSL certificates not found. Run: openssl req -x509 -newkey rsa:4096 -keyout server.key -out server.crt -days 365 -nodes")
        logger.info("Falling back to HTTP - microphone may not work")
        uvicorn.run("main:app", host="0.0.0.0", port=config.PORT, reload=True)
    except Exception as e:
        logger.error("SSL setup failed: %s", e)
        logger.info("Falling back to HTTP - microphone may not work")
        uvicorn.run("main:app", host="0.0.0.0", port=config.PORT, reload=True)
