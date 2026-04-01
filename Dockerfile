# Base image with Python 3.11
FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app

# Install git (needed for pip to clone GitHub packages)
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy entire project
COPY . .

# Install OpenEnv from local clone
RUN pip install --no-cache-dir -e OpenEnv/

# Expose port 8000
EXPOSE 8000

# Run the server
CMD ["uvicorn", "traffic_env.server.app:app", "--host", "0.0.0.0", "--port", "8000"]