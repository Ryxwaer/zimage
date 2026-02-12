# ── Stage 1: Build Vue Frontend ──────────────────────────────────
FROM node:20-slim AS frontend-build

WORKDIR /build

COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install

COPY frontend/ ./
RUN npm run build


# ── Stage 2: Python Backend ──────────────────────────────────────
FROM python:3.11-slim AS runtime

WORKDIR /app

# System dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libgl1 \
        libglib2.0-0t64 \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY main.py config.py mcp_server.py ./
COPY services/ ./services/
COPY routers/ ./routers/

# Copy built frontend from stage 1
COPY --from=frontend-build /static ./static/

# Create output directory
RUN mkdir -p /app/generated /models

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=120s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/status')" || exit 1

# Run the application
CMD ["uvicorn", "main:APP", "--host", "0.0.0.0", "--port", "8000"]
