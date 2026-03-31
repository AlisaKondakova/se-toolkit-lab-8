FROM python:3.11-slim
WORKDIR /app/nanobot
RUN pip install --no-cache-dir websockets
COPY config.json ./
COPY entrypoint.py ./
CMD ["python", "entrypoint.py"]
