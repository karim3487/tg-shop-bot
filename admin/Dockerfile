# Stage 1: Build
FROM python:3.12-slim AS builder

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    uv sync --frozen --no-install-project --no-dev

# Stage 2: Final
FROM python:3.12-slim

# Install tini and gosu
RUN apt-get update && apt-get install -y --no-install-recommends tini gosu && \
    rm -rf /var/lib/apt/lists/*

# Add non-root user
RUN groupadd -r appgroup && useradd -r -g appgroup -m appuser

WORKDIR /app

# Copy virtual environment and uv from builder
COPY --from=builder /app/.venv /app/.venv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy application code
COPY . .

# Setup permissions
RUN mkdir -p /app/logs /app/staticfiles && \
    chown -R appuser:appgroup /app && \
    chmod +x /app/docker-entrypoint.sh

# Environment setup
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

ENTRYPOINT ["/usr/bin/tini", "--", "/app/docker-entrypoint.sh"]
