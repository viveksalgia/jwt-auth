# Use Python 3.11 slim base image for smaller size and security
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=100

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Install system dependencies required for Python packages
RUN apt-get update && apt-get install -y \
    libmariadb-dev \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install MySQL client
RUN apt-get update \
    && apt-get install -y mariadb-client-compat

# Set working directory
WORKDIR /app

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Change the directory owner to appuser
RUN chown -R appuser:appuser /app

# Ensure entrypoint is executable
RUN chmod +x /app/scripts/entrypoint.sh

# Switch to non-root user
USER appuser

# Expose port 8080 for FastAPI
EXPOSE 8080

# Entrypoint runs migrations then starts uvicorn
CMD ["/app/scripts/entrypoint.sh"]