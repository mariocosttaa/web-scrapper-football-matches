# ============================================================================
# Dockerfile - Web Scraper
# ============================================================================
# Since docker-compose.yml mounts the entire directory as a volume,
# we only need to:
# 1. Install dependencies
# 2. Install Playwright browsers
# 3. Create output directories
# Code files are mounted from host, so no need to COPY them!
# ============================================================================

# Step 1: Use official Playwright Python image as base
FROM mcr.microsoft.com/playwright/python:v1.48.0-noble

# Step 2: Set working directory
WORKDIR /app

# Step 3: Set environment variables for unbuffered output (see logs immediately)
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Step 4: Copy only requirements.txt (needed for pip install)
# This is the ONLY file we copy - everything else comes from volume mount
COPY requirements.txt .

# Step 5: Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Step 6: Install Playwright browsers
RUN playwright install chromium && \
    playwright install-deps chromium

# Step 7: Create output directories and database directory (persistent, even if volume mount fails)
RUN mkdir -p /app/outputs/step-1 \
             /app/outputs/step-2 \
             /app/outputs/step-3 \
             /app/db

# Step 8: Set default command
# Code is mounted from host via docker-compose.yml volume
CMD ["python", "-u", "main.py"]
