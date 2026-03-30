#!/usr/bin/env python3
import asyncio
import json
import websockets

async def handler(websocket, path):
    access_key = "mysecretkey123"
    
    if '?' in path and f"access_key={access_key}" in path:
        await websocket.send(json.dumps({"content": "Connected! What can I help you with?"}))
        async for message in websocket:
            await websocket.send(json.dumps({"content": "I can help you with LMS system. Available labs: Lab 1, Lab 2, Lab 3"}))
    else:
        await websocket.close(1008, 'Invalid access key')

async def main():
    async with websockets.serve(handler, '0.0.0.0', 8081):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
