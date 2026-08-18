FROM python:3.11-slim

# Copy uv binary directly from official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

# Enable bytecode compilation and set environment path
ENV UV_COMPILE_BYTECODE=1
ENV PATH="/app/.venv/bin:$PATH"

# Copy dependency definition files first for optimal layer caching
COPY pyproject.toml uv.lock* ./

# Install dependencies into /app/.venv without installing project root yet
RUN uv sync --frozen --no-dev --no-install-project

# Copy remaining application source code
COPY . .

# Sync the application itself
RUN uv sync --frozen --no-dev

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]