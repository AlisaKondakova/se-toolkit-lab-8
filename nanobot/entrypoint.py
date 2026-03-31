#!/usr/bin/env python3
"""
Entrypoint for nanobot Docker container.
Creates config.json from environment variables and launches nanobot gateway.
"""
import os
import json

def main():
    workspace_path = "/app/nanobot/workspace"
    config_path = "/app/nanobot/config.dynamic.json"
    
    # Get environment variables
    api_key = os.environ.get("QWEN_API_KEY", "")
    base_url = os.environ.get("QWEN_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
    gateway_port = int(os.environ.get("NANOBOT_GATEWAY_CONTAINER_PORT", "8080"))
    webchat_port = int(os.environ.get("NANOBOT_WEBCHAT_CONTAINER_PORT", "8081"))
    access_key = os.environ.get("NANOBOT_ACCESS_KEY", "mysecretkey123")
    gateway_base_url = os.environ.get("GATEWAY_BASE_URL", "http://backend:42002")
    lms_api_key = os.environ.get("LMS_API_KEY", "")
    
    # Create config for nanobot (matching schema)
    config = {
        "providers": {
            "dashscope": {
                "apiKey": api_key,
                "apiBase": base_url
            }
        },
        "gateway": {
            "host": "0.0.0.0",
            "port": gateway_port
        },
        "channels": {
            "webchat": {
                "enabled": True,
                "host": "0.0.0.0",
                "port": webchat_port,
                "access_key": access_key
            }
        },
        "tools": {
            "mcpServers": {
                "lms": {
                    "type": "sse",
                    "url": gateway_base_url,
                    "headers": {
                        "Authorization": f"Bearer {lms_api_key}"
                    }
                }
            }
        },
        "agents": {
            "defaults": {
                "provider": "dashscope",
                "model": "qwen-coder"
            }
        }
    }
    
    # Write config
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)
    
    print(f"Starting nanobot gateway")
    print(f"  - API Key: {api_key[:3]}***" if api_key else "  - API Key: (empty)")
    print(f"  - Base URL: {base_url}")
    print(f"  - Gateway Port: {gateway_port}")
    print(f"  - Webchat Port: {webchat_port}")
    print(f"  - Gateway Base URL: {gateway_base_url}")
    
    # Launch nanobot gateway with config
    os.execvp("nanobot", ["nanobot", "gateway", "--config", config_path, "--workspace", workspace_path, "--port", str(gateway_port)])

if __name__ == "__main__":
    main()
