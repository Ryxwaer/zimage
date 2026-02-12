"""
Model Manager: handles auto-download and loading of the Z-Image-Turbo pipeline.
Singleton pattern ensures the model is loaded once and reused across requests.
"""

import os
import torch
from threading import Lock
from typing import Optional

from termcolor import colored

from config import SETTINGS


class ModelManager:
    """Manages the Z-Image-Turbo pipeline lifecycle."""

    def __init__(self) -> None:
        self._pipeline = None
        self._lock = Lock()
        self._is_loading = False
        self._is_loaded = False
        self._error: Optional[str] = None

    @property
    def is_loaded(self) -> bool:
        return self._is_loaded

    @property
    def is_loading(self) -> bool:
        return self._is_loading

    @property
    def error(self) -> Optional[str]:
        return self._error

    @property
    def pipeline(self):
        if not self._is_loaded:
            raise RuntimeError("Model not loaded. Call load_model() first.")
        return self._pipeline

    def _configure_cpu(self) -> None:
        """Configure PyTorch for optimal CPU inference."""
        NUM_THREADS = SETTINGS.NUM_THREADS
        if NUM_THREADS <= 0:
            NUM_THREADS = os.cpu_count() or 4
        torch.set_num_threads(NUM_THREADS)
        torch.set_num_interop_threads(max(1, NUM_THREADS // 2))
        print(colored(
            f"[ModelManager] CPU threads: {NUM_THREADS} "
            f"(interop: {max(1, NUM_THREADS // 2)})",
            "cyan",
        ))

    def _resolve_dtype(self) -> torch.dtype:
        """Resolve the configured dtype string to a torch.dtype."""
        DTYPE_MAP = {
            "bfloat16": torch.bfloat16,
            "float16": torch.float16,
            "float32": torch.float32,
        }
        DTYPE = DTYPE_MAP.get(SETTINGS.MODEL_DTYPE, torch.bfloat16)
        print(colored(f"[ModelManager] Using dtype: {SETTINGS.MODEL_DTYPE}", "cyan"))
        return DTYPE

    def load_model(self) -> None:
        """
        Load the Z-Image-Turbo pipeline.
        Downloads the model from HuggingFace if not cached locally.
        Thread-safe: only one load can happen at a time.
        """
        with self._lock:
            if self._is_loaded or self._is_loading:
                return

            self._is_loading = True
            self._error = None

        try:
            self._configure_cpu()
            DTYPE = self._resolve_dtype()

            print(colored(
                f"[ModelManager] Loading model: {SETTINGS.MODEL_REPO_ID}",
                "yellow",
            ))
            print(colored(
                f"[ModelManager] Cache directory: {SETTINGS.MODEL_CACHE_DIR}",
                "yellow",
            ))

            # Import diffusers here to avoid slow import at module level
            from diffusers import ZImagePipeline

            # This will auto-download from HuggingFace if not cached
            PIPELINE = ZImagePipeline.from_pretrained(
                SETTINGS.MODEL_REPO_ID,
                torch_dtype=DTYPE,
                cache_dir=SETTINGS.MODEL_CACHE_DIR,
                low_cpu_mem_usage=True,
            )

            # Keep on CPU
            PIPELINE.to("cpu")

            print(colored(
                "[ModelManager] Model loaded successfully on CPU",
                "green", attrs=["bold"],
            ))

            with self._lock:
                self._pipeline = PIPELINE
                self._is_loaded = True
                self._is_loading = False

        except Exception as e:
            ERROR_MSG = f"Failed to load model: {e}"
            print(colored(f"[ModelManager] {ERROR_MSG}", "red", attrs=["bold"]))
            with self._lock:
                self._is_loading = False
                self._error = ERROR_MSG
            raise

    def get_status(self) -> dict:
        """Return current model status as a dictionary."""
        return {
            "is_loaded": self._is_loaded,
            "is_loading": self._is_loading,
            "error": self._error,
            "model_repo": SETTINGS.MODEL_REPO_ID,
            "dtype": SETTINGS.MODEL_DTYPE,
        }


# Singleton instance
MODEL_MANAGER = ModelManager()
