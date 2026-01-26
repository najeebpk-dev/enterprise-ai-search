# Enterprise AI Search - Docker Image

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY data/ ./data/
COPY setup.py .
COPY README.md .

# Install the package
RUN pip install -e .

# Create a non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Default command
CMD ["python", "-m", "src.query"]

# Build:
#   docker build -t enterprise-ai-search:latest .
#
# Run ingestion:
#   docker run -it --env-file .env enterprise-ai-search:latest python src/ingest.py
#
# Run query:
#   docker run -it --env-file .env enterprise-ai-search:latest python src/query.py
