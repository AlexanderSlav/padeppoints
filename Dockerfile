FROM python:3.11-slim AS base

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends git curl && \
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

# Production image
FROM base AS production
COPY . .

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

USER appuser

# Use gunicorn with uvicorn workers for production
CMD ["gunicorn", "app.main:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "--timeout", "120", "--forwarded-allow-ips", "*"]