# AgriSmart AI - Production Multi-Architecture Dockerfile
# SIH-2026 Problem Statement 1
FROM python:3.11-slim

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000 \
    HOST=0.0.0.0 \
    ENVIRONMENT=production

# Install system dependencies (curl for container healthcheck, libgomp1 for PyTorch CPU)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Upgrade pip and install PyTorch CPU wheels + application dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY app/ app/
COPY model/ model/
COPY report/ report/
COPY predict.py .
COPY supabase_schema.sql .
COPY start.sh .

# Create isolated upload storage and ensure write permissions
RUN mkdir -p app/isolated_uploads && \
    chmod +x start.sh

# Expose HTTP port
EXPOSE 8000

# Docker Healthcheck targeting production /health endpoint
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Launch AgriSmart AI via production start script
CMD ["./start.sh"]
