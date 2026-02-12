"""
REST API routes for image generation, image listing, status, and config.
"""

import asyncio
import os
from functools import partial
from typing import Optional

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from config import SETTINGS
from services.image_generator import generate_image, list_images
from services.model_manager import MODEL_MANAGER


ROUTER = APIRouter(prefix="/api", tags=["api"])

# Only allow one generation at a time – CPU can't parallelise inference
_GENERATION_LOCK = asyncio.Lock()


# ── Request / Response Models ────────────────────────────────────


class GenerateRequest(BaseModel):
    """Request body for image generation."""
    prompt: str = Field(..., min_length=1, max_length=2000, description="Text prompt")
    width: int = Field(0, ge=0, le=2048, description="Image width (0 = default)")
    height: int = Field(0, ge=0, le=2048, description="Image height (0 = default)")
    steps: int = Field(0, ge=0, le=100, description="Inference steps (0 = default)")
    seed: int = Field(-1, ge=-1, description="Random seed (-1 = random)")


class GenerateResponse(BaseModel):
    """Response from image generation."""
    filename: str
    url: str
    prompt: str
    width: int
    height: int
    steps: int
    seed: int
    guidance_scale: float
    generation_time_seconds: float
    timestamp: str
    model: str


class StatusResponse(BaseModel):
    """Model status response."""
    is_loaded: bool
    is_loading: bool
    error: Optional[str] = None
    model_repo: str
    dtype: str


class ConfigResponse(BaseModel):
    """Public configuration for the frontend."""
    mcp_path: str
    default_width: int
    default_height: int
    default_steps: int
    max_history: int
    model_repo: str


# ── Endpoints ────────────────────────────────────────────────────


@ROUTER.post("/generate", response_model=GenerateResponse)
async def api_generate(request: GenerateRequest):
    """Generate an image from a text prompt.
    Runs inference in a thread pool so the event loop stays responsive.
    """
    if not MODEL_MANAGER.is_loaded:
        raise HTTPException(
            status_code=503,
            detail="Model is not loaded yet. Please wait.",
        )

    if _GENERATION_LOCK.locked():
        raise HTTPException(
            status_code=429,
            detail="Another image is currently being generated. Please wait.",
        )

    async with _GENERATION_LOCK:
        try:
            LOOP = asyncio.get_running_loop()
            RESULT = await LOOP.run_in_executor(
                None,
                partial(
                    generate_image,
                    prompt=request.prompt,
                    width=request.width,
                    height=request.height,
                    steps=request.steps,
                    seed=request.seed,
                ),
            )
            RESULT["url"] = f"/api/images/{RESULT['filename']}"
            return GenerateResponse(**RESULT)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


@ROUTER.get("/images")
async def api_list_images(limit: Optional[int] = None):
    """List recent generated images."""
    return list_images(limit=limit)


@ROUTER.get("/images/{filename}")
async def api_get_image(filename: str):
    """Serve a specific generated image file."""
    # Sanitize filename to prevent path traversal
    SAFE_NAME = os.path.basename(filename)
    FILEPATH = os.path.join(SETTINGS.OUTPUT_DIR, SAFE_NAME)

    if not os.path.isfile(FILEPATH):
        raise HTTPException(status_code=404, detail="Image not found")

    return FileResponse(FILEPATH, media_type="image/png")


@ROUTER.get("/status", response_model=StatusResponse)
async def api_status():
    """Get current model status."""
    return MODEL_MANAGER.get_status()


@ROUTER.get("/config", response_model=ConfigResponse)
async def api_config():
    """Get public configuration for the frontend."""
    return ConfigResponse(
        mcp_path=SETTINGS.MCP_PATH,
        default_width=SETTINGS.DEFAULT_WIDTH,
        default_height=SETTINGS.DEFAULT_HEIGHT,
        default_steps=SETTINGS.DEFAULT_STEPS,
        max_history=SETTINGS.MAX_HISTORY,
        model_repo=SETTINGS.MODEL_REPO_ID,
    )
