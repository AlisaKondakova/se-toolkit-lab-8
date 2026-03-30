FROM python:3.11-slim

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY run.py /app/run.py

RUN pip install websockets httpx

EXPOSE 8081

CMD ["python", "run.py"]
