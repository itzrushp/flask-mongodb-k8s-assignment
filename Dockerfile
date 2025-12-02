# Use official Python runtime as base image<a></a>
FROM python:3.10-slim

# Why Python 3.10?<a></a>
# - Stable, widely-supported version<a></a>
# - Sufficient for Flask applications<a></a>
# - Good balance of features and stability<a></a>
# Set working directory in container<a></a>
WORKDIR /app

# Copy requirements first (Docker caching optimization)<a></a>
# This layer is cached if requirements.txt doesn't change<a></a>
COPY requirements.txt .

# Install Python dependencies<a></a>
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code<a></a>
# This layer is rebuilt if code changes (more frequent)<a></a>
COPY app.py .

# Expose port that Flask runs on<a></a>
EXPOSE 5000

# Health check for Docker<a></a>
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
CMD python -c "import requests; requests.get('http://localhost:5000/health')"

# Default command to run the application<a></a>
CMD ["python", "app.py"]