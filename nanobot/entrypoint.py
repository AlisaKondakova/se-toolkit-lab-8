import json
import os
import sys

def main():
    config_path = "/app/nanobot/config.json"
    resolved_path = "/app/nanobot/config.resolved.json"
    
    if not os.path.exists(config_path):
        print(f"ERROR: config.json not found at {config_path}")
        sys.exit(1)

    with open(config_path, "r") as f:
        config = json.load(f)

    # Resolve LLM provider settings from env vars
    qwen_api_key = os.environ.get("QWEN_API_KEY")
    qwen_base_url = os.environ.get("QWEN_BASE_URL")
    
    if "providers" in config and "openai" in config["providers"]:
        if qwen_api_key:
            config["providers"]["openai"]["apiKey"] = qwen_api_key
        if qwen_base_url:
            config["providers"]["openai"]["apiBase"] = qwen_base_url

    # Resolve WebSocket channel settings
    webchat_port = int(os.environ.get("NANOBOT_WEBCHAT_CONTAINER_PORT", "8081"))
    access_key = os.environ.get("NANOBOT_ACCESS_KEY")
    
    if "channels" in config and "webchat" in config["channels"]:
        config["channels"]["webchat"]["port"] = webchat_port
        if access_key:
            config["channels"]["webchat"]["access_key"] = access_key

    # Resolve MCP server settings
    gateway_base_url = os.environ.get("GATEWAY_BASE_URL")
    lms_api_key = os.environ.get("LMS_API_KEY")
    
    if "tools" in config and "mcpServers" in config["tools"]:
        for server_name, server_config in config["tools"]["mcpServers"].items():
            if "env" in server_config:
                if gateway_base_url and "GATEWAY_BASE_URL" in server_config["env"]:
                    server_config["env"]["GATEWAY_BASE_URL"] = gateway_base_url
                if lms_api_key and "LMS_API_KEY" in server_config["env"]:
                    server_config["env"]["LMS_API_KEY"] = lms_api_key

    with open(resolved_path, "w") as f:
        json.dump(config, f, indent=2)

    # Also copy to ~/.nanobot/config.json for compatibility
    home_config_dir = os.path.expanduser("~/.nanobot")
    os.makedirs(home_config_dir, exist_ok=True)
    home_config_path = os.path.join(home_config_dir, "config.json")
    with open(home_config_path, "w") as f:
        json.dump(config, f, indent=2)

    print(f"--- CONFIG RESOLVED ---")
    print(f"--- LLM Base URL: {qwen_base_url} ---")
    print(f"--- LLM API Key set: {bool(qwen_api_key)} ---")
    print(f"--- WebChat Port: {webchat_port} ---")
    print(f"--- Config written to: {resolved_path} ---")
    print(f"--- STARTING GATEWAY ---")
    sys.stdout.flush()

    os.execvp("nanobot", ["nanobot", "gateway", "--config", resolved_path, "--workspace", "/app/nanobot/workspace"])

if __name__ == "__main__":
    main()
