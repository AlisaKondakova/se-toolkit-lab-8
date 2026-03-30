#!/usr/bin/env python3
import asyncio
import json
import os
import httpx
import websockets

async def chat_with_ollama(message):
    """Отправляем запрос в Ollama"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://ollama:11434/api/generate",
            json={
                "model": "qwen2.5-coder:7b",
                "prompt": message,
                "stream": False
            },
            timeout=60.0
        )
        data = response.json()
        return data.get("response", "No response")

async def handler(websocket, path):
    """Обработчик WebSocket соединений"""
    # Проверяем access key
    access_key = os.environ.get('NANOBOT_ACCESS_KEY', 'mysecretkey123')
    
    # Получаем access_key из query string
    if '?' in path:
        params = {}
        for p in path.split('?')[1].split('&'):
            if '=' in p:
                key, val = p.split('=', 1)
                params[key] = val
        if params.get('access_key') != access_key:
            await websocket.close(1008, 'Invalid access key')
            return
    else:
        await websocket.close(1008, 'No access key provided')
        return
    
    print(f"New connection from {websocket.remote_address}")
    await websocket.send(json.dumps({"content": "Connected! Ask me anything."}))
    
    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                user_message = data.get('content', '')
                print(f"Received: {user_message}")
                
                # Получаем ответ от Ollama
                response = await chat_with_ollama(user_message)
                print(f"Response: {response[:100]}...")
                
                await websocket.send(json.dumps({"content": response}))
            except Exception as e:
                print(f"Error: {e}")
                await websocket.send(json.dumps({"error": str(e)}))
    except websockets.exceptions.ConnectionClosed:
        print("Connection closed")

async def main():
    print("Starting WebSocket server on port 8081...")
    print(f"Access key: {os.environ.get('NANOBOT_ACCESS_KEY', 'mysecretkey123')}")
    
    async with websockets.serve(handler, '0.0.0.0', 8081):
        print("WebSocket server running on ws://0.0.0.0:8081")
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
