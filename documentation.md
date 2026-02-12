# Z-Image Turbo – Documentation

## Architecture Overview

FastAPI backend serving a Vue 3 SPA, with Z-Image-Turbo model for CPU-based image generation and an MCP HTTP server for agent access.

## Backend Modules

### `config.py` – Settings
- **Class**: `Settings(BaseSettings)` – Pydantic settings from `.env`
- **Instance**: `SETTINGS` – singleton config object
- Key settings: `MODEL_REPO_ID`, `MODEL_CACHE_DIR`, `MODEL_DTYPE`, `PUBLIC_URL`

### `services/model_manager.py` – Model Lifecycle
- **Class**: `ModelManager` – thread-safe singleton for pipeline management
- **Instance**: `MODEL_MANAGER`
- Methods: `load_model()`, `get_status()`
- Properties: `pipeline`, `is_loaded`, `is_loading`, `error`

### `services/image_generator.py` – Image Generation
- **Function**: `generate_image(prompt, width, height, steps, seed)` – returns metadata dict
- **Function**: `list_images(limit)` – lists recent images from `generated/` directory
- Saves PNG images with JSON metadata sidecars

### `routers/api.py` – REST API
- `POST /api/generate` – generate image from prompt
- `GET /api/images` – list recent images
- `GET /api/images/{filename}` – serve image file
- `GET /api/status` – model status
- `GET /api/config` – public config for frontend

### `mcp_server.py` – MCP Server
- **Instance**: `MCP` (FastMCP)
- **Tool**: `generate_image` – create image from text
- **Tool**: `get_model_status` – check model state
- Mounted at `/mcp` on FastAPI app

### `main.py` – Application Entry
- FastAPI app with lifespan (background model loading)
- CORS middleware, API router, MCP mount, static file serving

## Frontend Components

### `App.vue` – Root layout with background animation blobs
### `PromptInput.vue` – Textarea + generate button with timer
### `SettingsPanel.vue` – Collapsible resolution/steps/seed controls
### `ImageCarousel.vue` – Horizontal scrollable gallery
### `ImageModal.vue` – Full-screen image overlay with metadata
### `McpConnect.vue` – MCP endpoint URL and config JSON with copy buttons

## API Schemas

### GenerateRequest
```json
{
  "prompt": "string",
  "width": 512,
  "height": 512,
  "steps": 9,
  "seed": -1
}
```

### GenerateResponse
```json
{
  "filename": "string",
  "url": "string",
  "prompt": "string",
  "width": 512,
  "height": 512,
  "steps": 9,
  "seed": 12345,
  "guidance_scale": 0.0,
  "generation_time_seconds": 45.2,
  "timestamp": "2026-02-12T10:00:00Z",
  "model": "Tongyi-MAI/Z-Image-Turbo"
}
```

## Docker Deployment

### Build & Run
```bash
docker compose up -d --build
```

### Environment Variables
See `.env.example` for all configuration options.

### Volumes
- `zimage_models` – HuggingFace model cache
- `zimage_output` – generated images

### Networks
Connects to `nginx-proxy-manager_default` for reverse proxy access.
