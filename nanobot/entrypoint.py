#!/usr/bin/env python3
import os, sys, json, re, asyncio, websockets, logging
from pathlib import Path
from urllib.parse import parse_qs, urlparse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ACCESS_KEY = os.environ.get('NANOBOT_ACCESS_KEY', '')
PORT = int(os.environ.get('NANOBOT_WEBCHAT_CONTAINER_PORT', '8081'))

async def handler(ws, path=None):
    try:
        p = path or getattr(ws, 'path', '')
        q = parse_qs(urlparse(p).query)
        k = q.get('access_key', [None])[0] or ''
        if k != ACCESS_KEY:
            await ws.send(json.dumps({'error': 'Invalid key'}))
            await ws.close()
            return
        logger.info('Client connected')
        async for msg in ws:
            d = json.loads(msg)
            c = d.get('content', '')
            logger.info(f'Received: {c[:50]}')
            await ws.send(json.dumps({'content': f'Echo: {c}'}))
    except Exception as e:
        logger.error(f'Error: {e}')

async def main():
    cfg = Path('/app/nanobot/config.json')
    txt = cfg.read_text()
    txt = re.sub(r'\$\{([^}]+)\}', lambda m: os.environ.get(m.group(1), ''), txt)
    cfg.write_text(txt)
    logger.info(f'Starting WS server on port {PORT}, key: {ACCESS_KEY[:3]}***')
    async with websockets.serve(handler, '0.0.0.0', PORT):
        await asyncio.Future()

if __name__ == '__main__':
    asyncio.run(main())
