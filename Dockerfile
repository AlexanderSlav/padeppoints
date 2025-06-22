FROM python:3.11-slim AS base

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends git && \
    rm -rf /var/lib/apt/lists/*

# Base dependencies layer
COPY requirements.txt .
RUN pip install -r requirements.txt

# Development image
FROM base AS dev
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Test image
FROM base AS test
RUN pip install pytest pytest-asyncio pytest-cov httpx
COPY . .
CMD ["sh", "-c", "sleep 10 && pytest -vvv --asyncio-mode=auto -s"] 