# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8002 \
    PYTHONPATH=/app:/app/src

# Set the working directory
WORKDIR /app

# Install git and other dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the project files
COPY . .

# Create an empty __init__.py in the src directory if it doesn't exist
RUN touch src/__init__.py

# For debugging: Print directory structure and key files
RUN find /app -type f -name "*.py" | grep -E 'agent|graph' | sort && \
    ls -la /app && \
    ls -la /app/src && \
    ls -la /app/src/agent

# Try installing the agent package in development mode
RUN pip install -e . || echo "Development install failed, continuing anyway"

# Create symlinks to help with imports
RUN ln -sf /app/src/agent /app/agent

# Create a user with lower privileges
RUN adduser --disabled-password --gecos "" appuser
# Ensure appuser has access to required directories
RUN chown -R appuser:appuser /app
USER appuser

# Expose the port the app runs on
EXPOSE 8002

# Run the initialization script before starting the server
CMD python docker_init.py && uvicorn main:app --host 0.0.0.0 --port 8002 