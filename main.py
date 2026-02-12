"""
Z-Image Turbo – FastAPI application entrypoint.
Serves the Vue SPA, REST API, and MCP HTTP server.
"""

import asyncio
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from termcolor import colored

from config import SETTINGS
from routers.api import ROUTER as API_ROUTER
from mcp_server import MCP
from services.model_manager import MODEL_MANAGER


# ── Lifespan: load model + MCP session manager on startup ────────


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load the model in a background thread and start MCP session manager."""
    print(colored("=" * 60, "cyan"))
    print(colored("  Z-Image Turbo Server Starting", "cyan", attrs=["bold"]))
    print(colored("=" * 60, "cyan"))

    # Load model in background thread to not block startup
    LOOP = asyncio.get_running_loop()
    LOOP.run_in_executor(None, MODEL_MANAGER.load_model)

    print(colored(
        f"[Startup] Model loading in background: {SETTINGS.MODEL_REPO_ID}",
        "yellow",
    ))
    print(colored(
        f"[Startup] MCP server at: {SETTINGS.MCP_PATH}",
        "cyan",
    ))

    # Start MCP session manager (required for Streamable HTTP transport)
    async with MCP.session_manager.run():
        yield

    print(colored("[Shutdown] Server shutting down.", "yellow"))


# ── FastAPI App ──────────────────────────────────────────────────

APP = FastAPI(
    title="Z-Image Turbo",
    description="Image generation with Z-Image-Turbo model",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS – allow cross-origin for MCP agent connections
APP.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# ── Mount API Routes ─────────────────────────────────────────────

APP.include_router(API_ROUTER)

# ── Mount MCP Server ─────────────────────────────────────────────
# Build the Starlette sub-app (this also lazily creates session_manager)
MCP_APP = MCP.streamable_http_app()
# Mount the sub-app – FastAPI strips the prefix, so the internal route is "/"
APP.mount(SETTINGS.MCP_PATH, MCP_APP)

# ── Serve Static Frontend ───────────────────────────────────────

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
ASSETS_DIR = os.path.join(STATIC_DIR, "assets")
os.makedirs(STATIC_DIR, exist_ok=True)


@APP.get("/")
async def serve_index():
    """Serve the Vue SPA index.html."""
    INDEX_PATH = os.path.join(STATIC_DIR, "index.html")
    if os.path.isfile(INDEX_PATH):
        return FileResponse(INDEX_PATH)
    return {"message": "Z-Image Turbo API. Frontend not built yet."}


# Mount Vite-built assets at /assets (JS, CSS bundles)
if os.path.isdir(ASSETS_DIR):
    APP.mount("/assets", StaticFiles(directory=ASSETS_DIR), name="static-assets")


# ── Run with Uvicorn ─────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:APP",
        host=SETTINGS.HOST,
        port=SETTINGS.PORT,
        reload=False,
    )
