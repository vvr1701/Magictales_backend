FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for WeasyPrint, MediaPipe, and base packages
# Note: Using Debian bookworm package names
RUN apt-get update && apt-get install -y --no-install-recommends \
    # WeasyPrint dependencies
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf-2.0-0 \
    libffi-dev \
    shared-mime-info \
    # OpenCV/MediaPipe dependencies
    libgl1 \
    libglib2.0-0 \
    # Utilities
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first (needed for playwright install-deps)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright system dependencies (Chromium browser deps)
# This uses apt-get internally, so must run as root
RUN playwright install-deps chromium

# Set Playwright browsers path to a location accessible by all users
ENV PLAYWRIGHT_BROWSERS_PATH=/app/.playwright

# Install Playwright browsers to the shared location
RUN playwright install chromium

# Copy application
COPY . .

# Create non-root user and set ownership of app directory (including playwright browsers)
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
