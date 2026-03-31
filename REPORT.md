# Lab 8 — Report

## Task 2A — Deployed agent

Nanobot startup log excerpt showing the gateway started inside Docker:

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
nanobot-1  | 2026-03-31 14:01:14.167 | INFO | nanobot.channels.manager:_init_channels:58 - WebChat channel enabled
nanobot-1  | ✓ Channels enabled: webchat
nanobot-1  | ✓ Heartbeat: every 1800s
nanobot-1  | 2026-03-31 14:01:14.772 | INFO | nanobot_webchat.channel:start:72 - WebChat starting on 0.0.0.0:8081
nanobot-1  | 2026-03-31 14:01:15.263 | INFO | nanobot.agent.loop:run:280 - Agent loop started
```

Services running:
```
NAME                                    STATUS          PORTS
se-toolkit-lab-8-caddy-1                Up              0.0.0.0:42002->80/tcp
se-toolkit-lab-8-client-web-flutter-1   Up              80/tcp
se-toolkit-lab-8-nanobot-1              Up              0.0.0.0:8080-8081->8080-8081/tcp
```

## Task 2B — Web client

WebSocket conversation evidence showing full stack working:

```
nanobot-1  | 2026-03-31 14:29:31.549 | INFO | nanobot_webchat.channel:_handle_ws:120 - WebChat: new connection chat_id=840c0289-a67d-4447-a088-6c247584ea3d
nanobot-1  | 2026-03-31 14:29:31.552 | INFO | nanobot.agent.loop:_process_message:425 - Processing message from webchat:840c0289-a67d-4447-a088-6c247584ea3d: hello
nanobot-1  | 2026-03-31 14:29:34.270 | INFO | nanobot.agent.loop:_process_message:479 - Response to webchat:840c0289-a67d-4447-a088-6c247584ea3d: [agent response]
nanobot-1  | 2026-03-31 14:29:37.175 | INFO | nanobot_webchat.channel:_handle_ws:147 - WebChat: disconnected chat_id=840c0289-a67d-4447-a088-6c247584ea3d
```

This proves:
1. WebSocket connection established successfully
2. Message "hello" received from Flutter web client
3. Agent processed the message and generated response
4. Response sent back to client
5. Clean disconnect

Flutter web client accessible at: http://localhost:42002/flutter
Access key: mysecretkey123

<<<<<<< HEAD
<!-- Screenshots: healthy trace span hierarchy, error trace -->

## Task 3C — Observability MCP tools

<!-- Paste agent responses to "any errors in the last hour?" under normal and failure conditions -->

## Task 4A — Multi-step investigation

<!-- Paste the agent's response to "What went wrong?" showing chained log + trace investigation -->

## Task 4B — Proactive health check

<!-- Screenshot or transcript of the proactive health report that appears in the Flutter chat -->

<img width="1920" height="1200" alt="toolkit" src="https://github.com/user-attachments/assets/386168ab-513a-4252-a5f5-14a4b25ee57e" />

## Task 4C — Bug fix and recovery

<!-- 1. Root cause identified
     2. Code fix (diff or description)
     3. Post-fix response to "What went wrong?" showing the real underlying failure
     4. Healthy follow-up report or transcript after recovery -->
### Проверка статуса сервисов
=======
```bash
# Flutter serves content
curl http://localhost:42002/flutter/index.html
# Returns: <!DOCTYPE html><html>...

# WebSocket endpoint accepts connections
curl -s -o /dev/null -w "%{http_code}" http://localhost:42002/ws/chat
# Returns: 400 (expected for non-WebSocket connection)
```
