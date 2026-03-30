#!/usr/bin/env python3
import json
import os
import sys
from pathlib import Path

def main():
    config_path = Path('/app/nanobot/config.json')
    resolved_path = Path('/app/nanobot/config.resolved.json')
    
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    # Inject environment variables
    if 'providers' in config and 'ollama' in config['providers']:
        config['providers']['ollama']['apiBase'] = os.environ.get('OLLAMA_HOST', 'http://ollama:11434')
    
    if 'channels' in config and 'webchat' in config['channels']:
        config['channels']['webchat']['host'] = os.environ.get('WEBCHAT_HOST', '0.0.0.0')
        config['channels']['webchat']['port'] = int(os.environ.get('WEBCHAT_PORT', '8081'))
        config['channels']['webchat']['access_key'] = os.environ.get('NANOBOT_ACCESS_KEY', 'mysecretkey123')
    
    if 'gateway' in config:
        config['gateway']['host'] = os.environ.get('GATEWAY_HOST', '0.0.0.0')
        config['gateway']['port'] = int(os.environ.get('GATEWAY_PORT', '8080'))
    
    with open(resolved_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"Starting nanobot gateway with config: {resolved_path}")
    sys.stdout.flush()
    
    os.environ['PYTHONPATH'] = '/app/nanobot:' + os.environ.get('PYTHONPATH', '')
    
    os.execvp("nanobot", ["nanobot", "gateway", "--config", str(resolved_path), "--workspace", "/app/nanobot/workspace"])

if __name__ == "__main__":
    main()
