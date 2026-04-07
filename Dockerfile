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

# Expose port 7860 (required for HuggingFace Spaces)
EXPOSE 7860

# Run the server
CMD ["uvicorn", "traffic_env.server.app:app", "--host", "0.0.0.0", "--port", "7860"]