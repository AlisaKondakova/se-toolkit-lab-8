# Multi-stage build for nanobot
# Stage 1: Build with uv
FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim AS builder

WORKDIR /app

# Copy webchat plugin (full package for installation)
COPY nanobot-websocket-channel/pyproject.toml ./nanobot-websocket-channel/pyproject.toml
COPY nanobot-websocket-channel/nanobot_webchat ./nanobot-websocket-channel/nanobot_webchat

WORKDIR /app/nanobot-websocket-channel

# Install nanobot-websocket-channel plugin (this also installs nanobot-ai dependency)
RUN uv pip install --system -e .

# Stage 2: Runtime
FROM python:3.11-slim

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy the webchat plugin source (for editable install to work)
COPY nanobot-websocket-channel/nanobot_webchat ./nanobot-websocket-channel/nanobot_webchat
COPY nanobot-websocket-channel/pyproject.toml ./nanobot-websocket-channel/pyproject.toml

WORKDIR /app/nanobot

# Copy entrypoint script
COPY nanobot/entrypoint.py ./

CMD ["python", "entrypoint.py"]
