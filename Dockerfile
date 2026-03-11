# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set environment variables to avoid issues during installation
ENV PYTHONUNBUFFERED=1
ENV PIP_DEFAULT_TIMEOUT=100
ENV PIP_TIMEOUT=100
ENV PIP_RETRIES=5

# Set working directory
WORKDIR /app

# Install system dependencies that might be needed
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    gfortran \
    musl-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements_docker.txt .

# Install dependencies with increased timeout and retries
RUN pip install --no-cache-dir --default-timeout=100 --retries 5 -r requirements_docker.txt

# Copy the rest of the application
COPY . .

# Expose the port for the FastAPI application
EXPOSE 8000

# Set environment variables
ENV PYTHONPATH=/app

# Command to run the application
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]