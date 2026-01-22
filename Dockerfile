# Pin to Bookworm for stable package names
FROM python:3.11-slim-bookworm

WORKDIR /app

# Install system dependencies for WeasyPrint, MediaPipe, and Playwright/Chromium
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
    # Playwright/Chromium dependencies
    libnss3 \
    libnspr4 \
    libasound2 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libcairo2 \
    libpangoft2-1.0-0 \
    libx11-xcb1 \
    libxcb-dri3-0 \
    libxshmfence1 \
    libxext6 \
    libx11-6 \
    # Fonts
    fonts-liberation \
    fonts-noto-color-emoji \
    # Utilities
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Set Playwright browsers path to a location accessible by all users
ENV PLAYWRIGHT_BROWSERS_PATH=/app/.playwright

# Install Playwright Chromium browser
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
