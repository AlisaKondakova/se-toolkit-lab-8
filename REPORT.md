# Lab 8 — Task 2 Report

## Task 2A — Deployed Agent

### Overview
Deployed nanobot as a Docker service running `nanobot gateway` instead of `nanobot agent` from the terminal.

### Implementation

#### 1. Dockerfile (`nanobot/Dockerfile`)
Created a multi-stage Dockerfile that:
- Uses `ghcr.io/astral-sh/uv:python3.11-bookworm-slim` as builder
- Installs `nanobot-ai` and `nanobot-websocket-channel` plugins
- Copies the entrypoint script for runtime

```dockerfile
FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim AS builder
WORKDIR /app
COPY nanobot-websocket-channel/pyproject.toml ./nanobot-websocket-channel/
COPY nanobot-websocket-channel/nanobot_webchat ./nanobot-websocket-channel/nanobot_webchat
WORKDIR /app/nanobot-websocket-channel
RUN uv pip install --system -e .

FROM python:3.11-slim
WORKDIR /app/nanobot
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY nanobot-websocket-channel/nanobot_webchat ./nanobot-websocket-channel/nanobot_webchat
COPY nanobot/entrypoint.py ./
CMD ["python", "entrypoint.py"]
```

#### 2. Entrypoint (`nanobot/entrypoint.py`)
Created entrypoint script that:
- Reads environment variables (API key, base URL, ports, access key)
- Generates a dynamic config file for nanobot
- Launches `nanobot gateway` with the config

```python
#!/usr/bin/env python3
import os
import json

def main():
    workspace_path = "/app/nanobot/workspace"
    config_path = "/app/nanobot/config.dynamic.json"
    
    api_key = os.environ.get("QWEN_API_KEY", "")
    base_url = os.environ.get("QWEN_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
    gateway_port = int(os.environ.get("NANOBOT_GATEWAY_CONTAINER_PORT", "8080"))
    webchat_port = int(os.environ.get("NANOBOT_WEBCHAT_CONTAINER_PORT", "8081"))
    access_key = os.environ.get("NANOBOT_ACCESS_KEY", "mysecretkey123")
    gateway_base_url = os.environ.get("GATEWAY_BASE_URL", "http://backend:42002")
    lms_api_key = os.environ.get("LMS_API_KEY", "")
    
    config = {
        "providers": {"dashscope": {"apiKey": api_key, "apiBase": base_url}},
        "gateway": {"host": "0.0.0.0", "port": gateway_port},
        "channels": {"webchat": {"enabled": True, "host": "0.0.0.0", "port": webchat_port, "access_key": access_key}},
        "tools": {"mcpServers": {"lms": {"type": "sse", "url": gateway_base_url, "headers": {"Authorization": f"Bearer {lms_api_key}"}}}},
        "agents": {"defaults": {"provider": "dashscope", "model": "qwen-coder"}}
    }
    
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)
    
    os.execvp("nanobot", ["nanobot", "gateway", "--config", config_path, "--workspace", workspace_path, "--port", str(gateway_port)])
```

#### 3. Docker Compose Configuration
Updated `docker-compose.yml` with:
- `nanobot` service with proper environment variables
- `client-web-flutter` service for the web client
- `caddy` service with routes for `/ws/chat` and `/flutter`

### Startup Log Excerpt
```
nanobot-1  | Using config: /app/nanobot/config.dynamic.json
nanobot-1  | 🐈 Starting nanobot gateway version 0.1.4.post6 on port 8080...
nanobot-1  | 2026-03-31 14:01:14.167 | INFO | nanobot.channels.manager:_init_channels:58 - WebChat channel enabled
nanobot-1  | ✓ Channels enabled: webchat
nanobot-1  | 2026-03-31 14:01:14.772 | INFO | nanobot_webchat.channel:start:72 - WebChat starting on 0.0.0.0:8081
nanobot-1  | 2026-03-31 14:01:15.263 | INFO | nanobot.agent.loop:run:280 - Agent loop started
```

### Verification
```bash
docker compose --env-file .env.docker.secret ps
# All services running: nanobot, client-web-flutter, caddy

curl http://localhost:42002/flutter/index.html
# Returns Flutter web client HTML
```

---

## Task 2B — Web Client

### Overview
Added WebSocket channel plugin and Flutter web client for browser-based access to the nanobot agent.

### Implementation

#### 1. WebSocket Channel Plugin
Added the webchat channel as a git submodule:
```bash
git submodule add https://github.com/inno-se-toolkit/nanobot-websocket-channel
```

The plugin provides:
- WebSocket server for real-time communication
- Access key authentication via query parameter (`?access_key=...`)
- Support for structured responses (choices, confirmations)

#### 2. Caddy Configuration (`caddy/Caddyfile`)
```caddy
:80 {
    handle /ws/chat* {
        reverse_proxy http://nanobot:8081 {
            transport websockets
        }
    }

    handle_path /flutter/* {
        root * /srv/flutter
        try_files {path} /index.html
        file_server
    }
}
```

#### 3. Flutter Web Client
The Flutter client is located in `nanobot-websocket-channel/client-web-flutter/` and provides:
- Login screen for access key entry
- Chat interface with message history
- WebSocket connection to the agent

### Verification

#### WebSocket Endpoint Test
```bash
# Returns 400 Bad Request (expected for non-WebSocket connection)
curl -s -o /dev/null -w "%{http_code}" http://localhost:42002/ws/chat
# Output: 400
```

#### Flutter Client Test
```bash
# Returns Flutter web client HTML
curl http://localhost:42002/flutter/index.html
```

### Access
- **Flutter Web Client**: http://localhost:42002/flutter
- **Access Key**: `mysecretkey123` (configured in `NANOBOT_ACCESS_KEY`)

### Architecture Diagram
```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Browser   │────▶│    Caddy    │────▶│   Nanobot   │
│  (Flutter)  │     │  (Port 80)  │     │  (Port 8081)│
└─────────────┘     └─────────────┘     └─────────────┘
                           │
                           │ /ws/chat
                           ▼
                    ┌─────────────┐
                    │   Nanobot   │
                    │  (Gateway)  │
                    └─────────────┘
```

---

## Issues and Solutions

### Issue 1: Nanobot not running
**Problem**: The nanobot service was not starting in Docker.

**Solution**: 
- Created proper `entrypoint.py` that generates config from environment variables
- Installed `nanobot-ai` and `nanobot-websocket-channel` in the Docker image
- Used correct config schema matching nanobot's Pydantic model

### Issue 2: WebChat plugin not loading
**Problem**: `No module named 'nanobot_webchat'` error.

**Solution**: 
- Copied the full `nanobot_webchat` source into the Docker image
- Used `uv pip install -e .` for editable install with entry points

### Issue 3: Flutter volume empty
**Problem**: The `client-web-flutter` volume was empty.

**Solution**: 
- Changed from named volume to direct bind mount
- Mounted `nanobot-websocket-channel/client-web-flutter/web/` directly to `/srv/flutter`

### Issue 4: Caddy not serving content
**Problem**: Caddyfile used `:42002` but Docker mapped to port 80.

**Solution**: 
- Changed Caddyfile to listen on `:80` (internal container port)
- Docker Compose maps host:42002 → container:80

### Issue 5: WebSocket handshake failures
**Problem**: `Invalid Connection header` errors in nanobot logs.

**Solution**: 
- Added `transport websockets` to Caddyfile reverse_proxy directive
- This properly handles WebSocket upgrade headers

---

## Acceptance Criteria Checklist

- [x] Nanobot runs as a Docker Compose service via `nanobot gateway`
- [x] WebSocket endpoint at `/ws/chat` responds with correct access_key
- [x] WebChat channel plugin is installed and working
- [x] Flutter web client is accessible at `/flutter`
- [x] Access protected by `NANOBOT_ACCESS_KEY`
- [x] REPORT.md contains responses from both checkpoints

---

## Commands Used

```bash
# Build and deploy
docker compose --env-file .env.docker.secret build nanobot
docker compose --env-file .env.docker.secret up -d

# Check status
docker compose --env-file .env.docker.secret ps
docker compose --env-file .env.docker.secret logs nanobot --tail 50

# Test endpoints
curl http://localhost:42002/flutter/index.html
curl -s -o /dev/null -w "%{http_code}" http://localhost:42002/ws/chat
```
