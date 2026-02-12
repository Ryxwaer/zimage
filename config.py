"""
Configuration module for Z-Image Turbo application.
Uses pydantic-settings to load from .env file.
"""

import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables / .env file."""

    # ── Model Settings ──────────────────────────────────────────────
    MODEL_REPO_ID: str = "Tongyi-MAI/Z-Image-Turbo"
    MODEL_CACHE_DIR: str = "/models"
    MODEL_DTYPE: str = "bfloat16"  # bfloat16 or float32

    # ── Generation Defaults ─────────────────────────────────────────
    DEFAULT_WIDTH: int = 512
    DEFAULT_HEIGHT: int = 512
    DEFAULT_STEPS: int = 9  # Results in 8 DiT forwards for Turbo
    DEFAULT_GUIDANCE_SCALE: float = 0.0  # Must be 0 for Turbo models

    # ── CPU Optimization ────────────────────────────────────────────
    NUM_THREADS: int = 0  # 0 = auto-detect (all cores)

    # ── Server Settings ─────────────────────────────────────────────
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    MCP_PATH: str = "/mcp"

    # ── Storage ─────────────────────────────────────────────────────
    OUTPUT_DIR: str = "generated"
    MAX_HISTORY: int = 10  # Max images to keep in carousel

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
    }


# Singleton settings instance
SETTINGS = Settings()

# Ensure output directory exists
os.makedirs(SETTINGS.OUTPUT_DIR, exist_ok=True)
