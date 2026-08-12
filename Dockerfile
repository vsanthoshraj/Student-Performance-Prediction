# Stage 1: Build virtualenv & dependencies
FROM python:3.10-slim AS builder

WORKDIR /build

# Set environment variables for build
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Install build dependencies required for compiling C extensions (if needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy and install dependencies in virtual environment (layer caching)
COPY backend/requirements.txt .
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime image
FROM python:3.10-slim AS runner

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=5000 \
    PATH="/opt/venv/bin:$PATH"

# Create non-root user and group for security
RUN groupadd -g 10001 appgroup && \
    useradd -u 10001 -g appgroup -s /bin/sh -d /app appuser

WORKDIR /app

# Copy virtualenv from builder stage
COPY --from=builder /opt/venv /opt/venv

# Copy application files (leveraging .dockerignore)
COPY --chown=appuser:appgroup . /app

# Ensure runtime directories exist with correct permissions
RUN mkdir -p /app/backend/uploads /app/backend/data && \
    chown -R appuser:appgroup /app

# Switch to non-root user
USER appuser

# Expose server port
EXPOSE 5000

# Health check using Python standard library
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/login').read()"

# Run application with Gunicorn WSGI server
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "run:app"]


