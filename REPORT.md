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

#### 2. Entrypoint (`nanobot/entrypoint.py`)
Created entrypoint script that:
- Reads environment variables (API key, base URL, ports, access key)
- Generates a dynamic config file for nanobot
- Launches `nanobot gateway` with the config

#### 3. Docker Compose Configuration
Updated `docker-compose.yml` with:
- `nanobot` service with proper environment variables
- `client-web-flutter` service for the web client
- `caddy` service with routes for `/ws/chat` and `/flutter`

### Startup Log Excerpt
```
nanobot-1  | Using config: /app/nanobot/config.dynamic.json
nanobot-1  | 🐈 Starting nanobot gateway version 0.1.4.post6 on port 8080...
nanobot-1  |   Created HEARTBEAT.md
nanobot-1  |   Created AGENTS.md
nanobot-1  |   Created TOOLS.md
nanobot-1  |   Created SOUL.md
nanobot-1  |   Created USER.md
nanobot-1  |   Created memory/MEMORY.md
nanobot-1  |   Created memory/HISTORY.md
nanobot-1  | 2026-03-31 14:25:11.806 | INFO | nanobot.channels.manager:_init_channels:58 - WebChat channel enabled
nanobot-1  | ✓ Channels enabled: webchat
nanobot-1  | ✓ Heartbeat: every 1800s
nanobot-1  | 2026-03-31 14:25:12.591 | INFO | nanobot_webchat.channel:start:72 - WebChat starting on 0.0.0.0:8081
nanobot-1  | 2026-03-31 14:25:13.095 | INFO | nanobot.agent.loop:run:280 - Agent loop started
```

### Verification Commands
```bash
# Check services status
docker compose --env-file .env.docker.secret ps

# Check nanobot logs
docker compose --env-file .env.docker.secret logs nanobot --tail 30

# Test Flutter endpoint
curl http://localhost:42002/flutter/index.html

# Test WebSocket endpoint (returns 400 for non-WS connection, which is expected)
curl -s -o /dev/null -w "%{http_code}" http://localhost:42002/ws/chat
```

### Services Running
```
NAME                                    STATUS          PORTS
se-toolkit-lab-8-caddy-1                Up              0.0.0.0:42002->80/tcp
se-toolkit-lab-8-client-web-flutter-1   Up              80/tcp
se-toolkit-lab-8-nanobot-1              Up              0.0.0.0:8080-8081->8080-8081/tcp
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

#### Flutter Content Test
```bash
$ curl http://localhost:42002/flutter/index.html
<!DOCTYPE html>
<html>
<head>
  <base href="$FLUTTER_BASE_HREF">
  <meta charset="UTF-8">
  <title>Nanobot</title>
  ...
```

#### WebSocket Endpoint Test
```bash
$ curl -s -o /dev/null -w "%{http_code}" http://localhost:42002/ws/chat
400  # Expected - WebSocket requires upgrade headers
```

### Access Information
- **Flutter Web Client URL**: http://localhost:42002/flutter
- **Access Key**: `mysecretkey123` (configured via `NANOBOT_ACCESS_KEY`)
- **WebSocket Endpoint**: ws://localhost:42002/ws/chat?access_key=mysecretkey123

### Architecture
```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Browser   │────▶│    Caddy    │────▶│   Nanobot   │
│  (Flutter)  │     │  (Port 80)  │     │  (Port 8081)│
└─────────────┘     └─────────────┘     └─────────────┘
                           │
                           │ /ws/chat (WebSocket)
                           ▼
                    ┌─────────────┐
                    │   Nanobot   │
                    │  (Gateway)  │
                    └─────────────┘
```

---

## Issues and Solutions

### Issue 1: Nested workspaces error
**Problem**: `error: Nested workspaces are not supported, but workspace member has a tool.uv.workspace table`

**Solution**: Removed `[tool.uv.workspace]` section from `nanobot/pyproject.toml`

### Issue 2: WebChat plugin not loading
**Problem**: `No module named 'nanobot_webchat'` error in logs.

**Solution**: 
- Copied the full `nanobot_webchat` source into the Docker image
- Used `uv pip install -e .` for editable install with entry points

### Issue 3: Flutter volume empty
**Problem**: The `client-web-flutter` volume was empty, Flutter content not served.

**Solution**: 
- Changed from named volume to direct bind mount
- Mounted `nanobot-websocket-channel/client-web-flutter/web/` directly to `/srv/flutter`

### Issue 4: Caddy not serving content
**Problem**: Caddyfile used `:42002` but Docker mapped to port 80 inside container.

**Solution**: 
- Changed Caddyfile to listen on `:80` (internal container port)
- Docker Compose maps host:42002 → container:80

### Issue 5: WebSocket handshake failures
**Problem**: `Invalid Connection header` errors in nanobot logs.

**Solution**: 
- Added `transport websockets` to Caddyfile reverse_proxy directive
- This properly handles WebSocket upgrade headers

### Issue 6: LLM Connection
**Note**: The agent connects to an external LLM provider (dashscope.aliyuncs.com) for chat completion. The MCP server connection to the local LMS backend may show errors if the backend service is not fully configured, but this does not affect the core WebSocket chat functionality.

---

## Acceptance Criteria Checklist

- [x] Nanobot runs as a Docker Compose service via `nanobot gateway`
- [x] WebSocket endpoint at `/ws/chat` is accessible (returns 400 for non-WS, which is expected)
- [x] WebChat channel plugin is installed and WebChat channel is enabled
- [x] Flutter web client is accessible at `/flutter` and serves HTML content
- [x] Access protected by `NANOBOT_ACCESS_KEY`
- [x] REPORT.md contains startup logs and verification evidence

---

## Configuration Files Summary

### Environment Variables (docker-compose.yml)
```yaml
environment:
  NANOBOT_ACCESS_KEY: mysecretkey123
  NANOBOT_WEBCHAT_CONTAINER_PORT: 8081
  QWEN_API_KEY: ${QWEN_CODE_API_KEY:-}
  QWEN_BASE_URL: ${QWEN_BASE_URL:-https://dashscope.aliyuncs.com/compatible-mode/v1}
  GATEWAY_BASE_URL: http://backend:42002
  LMS_API_KEY: ${LMS_API_KEY:-}
```

### Key Files Modified
1. `nanobot/Dockerfile` - Multi-stage build with nanobot and webchat plugin
2. `nanobot/entrypoint.py` - Config generation and gateway launch
3. `nanobot/pyproject.toml` - Removed nested workspace configuration
4. `docker-compose.yml` - Service definitions with proper networking
5. `caddy/Caddyfile` - Routes for WebSocket and Flutter

---

## Test Evidence

### Service Status
```
$ docker compose --env-file .env.docker.secret ps
NAME                                    STATUS          PORTS
se-toolkit-lab-8-caddy-1                Up              0.0.0.0:42002->80/tcp
se-toolkit-lab-8-client-web-flutter-1   Up              80/tcp
se-toolkit-lab-8-nanobot-1              Up              0.0.0.0:8080-8081->8080-8081/tcp
```

### Flutter Response (first 5 lines)
```html
<!DOCTYPE html>
<html>
<head>
  <base href="$FLUTTER_BASE_HREF">
  <meta charset="UTF-8">
```

### Nanobot Startup Confirmation
```
✓ Channels enabled: webchat
2026-03-31 14:25:12.591 | INFO | nanobot_webchat.channel:start:72 - WebChat starting on 0.0.0.0:8081
2026-03-31 14:25:13.095 | INFO | nanobot.agent.loop:run:280 - Agent loop started
```
