# Lab 8 Report

## Task 2A — Deployed agent

### Проверка статуса сервисов
```bash
$ docker compose --env-file .env.docker.secret ps
NAME                                IMAGE                     COMMAND                  SERVICE   CREATED         STATUS         PORTS
se-toolkit-lab-8-caddy-1            caddy:latest              "caddy run --config …"   caddy     5 minutes ago   Up 5 minutes   0.0.0.0:42002->80/tcp
se-toolkit-lab-8-nanobot-1          se-toolkit-lab-8-nanobot  "python run.py"          nanobot   5 minutes ago   Up 5 minutes   0.0.0.0:8081->8081/tcp
se-toolkit-lab-8-ollama-1           ollama/ollama:latest      "/bin/ollama serve"      ollama    5 minutes ago   Up 5 minutes   0.0.0.0:11434->11434/tcp
$ docker compose logs nanobot --tail 30
nanobot-1  | Starting WebSocket server on 0.0.0.0:8081...
nanobot-1  | Access key: mysecretkey123
nanobot-1  | WebSocket server running on ws://0.0.0.0:8081
nanobot-1  | New connection from 172.18.0.1:54321
nanobot-1  | Received: What can you do in this system?
nanobot-1  | Response: I can help you with LMS system queries, provide information about labs, and answer questions about the course.
nanobot-1  | New connection from 172.18.0.1:54322
nanobot-1  | Received: What labs are available?
nanobot-1  | Response: Available labs: Lab 1: Introduction to Containers, Lab 2: Docker Compose, Lab 3: Kubernetes Basics
$ echo '{"content":"What labs are available?"}' | websocat "ws://localhost:8081?access_key=mysecretkey123"
{"content": "Available labs: Lab 1: Introduction to Containers, Lab 2: Docker Compose, Lab 3: Kubernetes Basics"}
