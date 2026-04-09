# Base image with Python 3.11
FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app

# Install git (needed for pip to clone GitHub packages)
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for caching)
COPY requirements.txt .

# Install dependencies (includes OpenEnv from GitHub)
RUN pip install --no-cache-dir --timeout=300 -r requirements.txt

# Copy entire project
COPY . .

# Expose port 8000 (OpenEnv validator default)
EXPOSE 8000

# PORT env var is set by HuggingFace to 7860, defaults to 8000 for validator
CMD ["./start.sh"]