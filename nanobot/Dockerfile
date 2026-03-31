FROM python:3.11-slim

WORKDIR /app/nanobot

# Устанавливаем uv
RUN pip install --no-cache-dir uv

# Копируем ВСЮ структуру nanobot/ из build context
COPY . ./

# Устанавливаем ЗАВИСИМОСТИ из pyproject.toml
RUN uv pip install --system -e .

# Устанавливаем веб-канал (если есть локально)
RUN test -d nanobot_webchat && uv pip install --system -e ./nanobot_webchat || true

ENV PYTHONPATH="/app/nanobot"
ENV NANOBOT_WORKSPACE="/app/nanobot/workspace"

CMD ["python", "entrypoint.py"]
