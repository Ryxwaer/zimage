# Z-Image Turbo

Text-to-image generation using [Z-Image-Turbo](https://huggingface.co/Tongyi-MAI/Z-Image-Turbo) (6B parameters), optimized for CPU-only inference. Includes a minimal web UI and an MCP server for agent integration.

**Live demo:** [https://zimage.ryxwaer.com/](https://zimage.ryxwaer.com/)

---

## Features

### Image Generation
- Generate images from text prompts using Z-Image-Turbo
- CPU-optimized inference with `bfloat16` on AMD Ryzen AI 9 HX 470 (64 GB RAM)
- Resolution presets: 512×512, 768×768, 1024×1024, 768×512, 512×768
- Adjustable inference steps (default 9)
- Seed control for reproducible results
- Concurrency guard — one generation at a time (429 for concurrent requests)

### Web Interface
- Vue 3 + Tailwind CSS v4
- Dark theme with animated gradient background
- Enter to generate (Shift+Enter for newlines)
- Collapsible settings panel
- Image carousel with mouse-wheel horizontal scroll
- Full-size image modal viewer with metadata
- MCP connection config with click-to-copy

### MCP Server
- Streamable HTTP transport at `/mcp`
- `generate_image` tool (params: prompt, width, height, seed, steps)
- Compatible with Cursor, Claude Desktop, and other MCP clients
- DNS rebinding protection disabled for reverse proxy compatibility

### Deployment
- Multi-stage Docker build (Node 20 + Python 3.11)
- Nginx Proxy Manager network integration
- Persistent volumes for model cache and generated images
- Health check with 120s start period for model loading
- Auto-downloads model from HuggingFace on first run

---

## Quick Start

```bash
# Clone and start
git clone <repo-url> && cd zimage
cp .env.example .env   # adjust if needed
docker compose up -d --build
```

The app will be available at `http://localhost:8100`. The model downloads automatically on first startup (~12 GB).

## Configuration

All settings are configurable via environment variables or `.env` file. See [`.env.example`](.env.example) for available options.

| Variable | Default | Description |
|----------|---------|-------------|
| `MODEL_REPO_ID` | `Tongyi-MAI/Z-Image-Turbo` | HuggingFace model repo |
| `MODEL_CACHE_DIR` | `/models` | Model cache path |
| `MODEL_DTYPE` | `bfloat16` | Inference dtype |
| `DEFAULT_WIDTH` | `512` | Default image width |
| `DEFAULT_HEIGHT` | `512` | Default image height |
| `DEFAULT_STEPS` | `9` | Default inference steps |
| `NUM_THREADS` | `0` | CPU threads (0 = all cores) |
| `OUTPUT_DIR` | `generated` | Generated images path |
| `MAX_HISTORY` | `50` | Max images in carousel |
| `MCP_PATH` | `/mcp` | MCP endpoint path |

## MCP Connection

Add to your MCP client config:

```json
{
  "mcpServers": {
    "z-image": {
      "url": "https://zimage.ryxwaer.com/mcp"
    }
  }
}
```

## Architecture

```
FastAPI (main.py)
├── /api/*          REST API (generate, images, status, config)
├── /mcp            MCP Streamable HTTP server
├── /               Vue SPA (static)
└── /assets         Vite-built JS/CSS
```

- **Backend:** FastAPI + uvicorn (single worker, singleton model)
- **Frontend:** Vue 3 + Vite + Tailwind CSS v4
- **Model:** diffusers ZImagePipeline, bfloat16, CPU
- **Inference:** Thread-pool executor keeps event loop responsive

## License

MIT
