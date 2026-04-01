# Multi-stage build for nanobot
# Stage 1: Build with uv
FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim AS builder

WORKDIR /app

# Copy the webchat plugin source from the submodule
COPY nanobot-websocket-channel/pyproject.toml ./nanobot-websocket-channel/pyproject.toml
COPY nanobot-websocket-channel/nanobot_webchat ./nanobot-websocket-channel/nanobot_webchat

WORKDIR /app/nanobot-websocket-channel

# Install nanobot-websocket-channel plugin (this also installs nanobot-ai dependency)
RUN uv pip install --system -e .

# Install MCP servers
WORKDIR /app/nanobot/mcp
COPY nanobot/mcp/pyproject.toml ./
COPY nanobot/mcp/mcp_lms ./mcp_lms
RUN uv pip install --system -e .

WORKDIR /app
COPY mcp/observability_server.py ./mcp/observability_server.py

# Install observability as a module
RUN uv pip install --system -e ./mcp 2>/dev/null || true

# Stage 2: Runtime
FROM python:3.11-slim

WORKDIR /app/nanobot

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy nanobot project files
COPY nanobot/config.json ./
COPY nanobot/entrypoint.py ./
COPY nanobot/pyproject.toml ./

# Copy MCP servers source (for cwd-based execution)
COPY nanobot/mcp ./mcp

# Copy workspace
COPY nanobot/workspace ./workspace

# Copy the webchat plugin source for runtime
COPY nanobot-websocket-channel/nanobot_webchat /app/nanobot-websocket-channel/nanobot_webchat

# Copy observability server
COPY mcp/observability_server.py /app/mcp/observability_server.py

# Set PYTHONPATH to include the webchat plugin and mcp
ENV PYTHONPATH="/app/nanobot-websocket-channel:/app/mcp:${PYTHONPATH}"

CMD ["python", "entrypoint.py"]
