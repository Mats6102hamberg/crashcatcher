FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    procps \
    net-tools \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy watchdog script
COPY watchdog.py .

# Create logs directory
RUN mkdir -p /app/logs

# Create non-root user
RUN useradd --create-home --shell /bin/bash watchdog && chown -R watchdog:watchdog /app
USER watchdog

# Health check
HEALTHCHECK --interval=60s --timeout=30s --start-period=10s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health', timeout=5)" || exit 1

# Run the watchdog
CMD ["python", "watchdog.py"]
