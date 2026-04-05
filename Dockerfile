# Use a slim Python base image
FROM python:3.12-slim

# Install uv by copying the binary from the official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set the working directory
WORKDIR /app

# Enable bytecode compilation for faster startup
ENV UV_COMPILE_BYTECODE=1

# Copy only the dependency files first (for better Docker caching)
COPY pyproject.toml uv.lock ./

# Install dependencies into the system environment (no need for venv inside Docker)
RUN uv sync --frozen --no-install-project --no-dev

# Copy the rest of your application code
COPY . .

# Run your Flask app
CMD ["uv", "run", "run.py"]