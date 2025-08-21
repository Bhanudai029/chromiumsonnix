# Use a Python base image suitable for Playwright
FROM python:3.9-slim-bullseye

# Set environment variables for Playwright
ENV PIP_NO_CACHE_DIR=1 \
    PYTHONUNBUFFERED=1 \
    PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

# Install necessary system dependencies for Playwright Chromium
# This list is comprehensive and covers most common missing libraries.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxrandr2 \
    libxdamage1 \
    libgbm1 \
    libasound2 \
    libpangocairo-1.0-0 \
    libpango-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libgtk-3-0 \
    libx11-xcb1 \
    libx11-6 \
    libxext6 \
    libxfixes3 \
    libxrender1 \
    libxshmfence1 \
    libxinerama1 \
    libxcursor1 \
    libxi6 \
    libxss1 \
    # Clean up apt cache to keep image size down
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements.txt and install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Install Playwright browsers into the specified path
RUN playwright install chromium

# Remove FFMPEG to save space and potentially memory, as it's often not needed for basic headless operations
RUN rm -rf /ms-playwright/ffmpeg*

# Copy the rest of your application code
COPY . .

# Expose the port (Render will use this)
EXPOSE $PORT

# Command to run the Flask application with Gunicorn
CMD gunicorn app:app --bind 0.0.0.0:$PORT --workers 1
