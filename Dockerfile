# Use official Python runtime as base image
FROM python:3.10-slim

# Why Python 3.10?
# - Stable, widely-supported version
# - Sufficient for Flask applications
# - Good balance of features and stability
# Set working directory in container
WORKDIR /app

# Copy requirements first (Docker caching optimization)
# This layer is cached if requirements.txt doesn't change
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
# This layer is rebuilt if code changes (more frequent)
COPY app.py .

# Expose port that Flask runs on
EXPOSE 5000

# Health check for Docker
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
CMD python -c "import requests; requests.get('http://localhost:5000/health')"

# Default command to run the application
CMD ["python", "app.py"]