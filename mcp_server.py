"""
MCP HTTP Server: exposes image generation as an MCP tool.
Mounted on FastAPI at /mcp using Streamable HTTP transport.
Agents (Cursor, Claude, etc.) can connect to generate images programmatically.
"""

from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings

from services.image_generator import generate_image as _generate
from services.model_manager import MODEL_MANAGER


# Disable DNS rebinding protection — app is behind a reverse proxy
TRANSPORT_SECURITY = TransportSecuritySettings(
    enable_dns_rebinding_protection=False,
)

# Create the MCP server instance
# streamable_http_path="/" because FastAPI mount at /mcp strips the prefix
MCP = FastMCP(
    name="Z-Image Generator",
    instructions=(
        "Z-Image Generator MCP server. "
        "Use the generate_image tool to create images from text prompts. "
        "It is good for generating small profile pictures at 512x512 "
        "but also capable of highly realistic 1024x1024 images. "
        "You should specify a style with each prompt (e.g. photo, illustration, painting). "
        "The model runs on CPU so generation may take 30-120 seconds."
    ),
    streamable_http_path="/",
    transport_security=TRANSPORT_SECURITY,
)


@MCP.tool()
async def generate_image(
    prompt: str,
    width: int = 512,
    height: int = 512,
    seed: int = -1,
    steps: int = 0,
) -> str:
    """
    Generate an image from a text prompt using Z-Image-Turbo.

    Args:
        prompt: A detailed text description of the image to generate.
        width: Image width in pixels. Recommended: 512 or 1024.
        height: Image height in pixels. Recommended: 512 or 1024.
        seed: Random seed for reproducibility. Use -1 for random.
        steps: Number of inference steps. Use 0 for default (9).

    Returns:
        JSON string with the generation result including the image URL.
    """
    import asyncio
    import json
    from functools import partial

    if not MODEL_MANAGER.is_loaded:
        return json.dumps({"error": "Model is not loaded yet. Please wait."})

    try:
        LOOP = asyncio.get_running_loop()
        RESULT = await LOOP.run_in_executor(
            None,
            partial(
                _generate,
                prompt=prompt,
                width=width,
                height=height,
                steps=steps,
                seed=seed,
            ),
        )
        RESULT["url"] = f"/api/images/{RESULT['filename']}"
        return json.dumps(RESULT, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})
