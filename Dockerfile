FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libopencv-dev \
    python3-opencv \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Environment variables for cloud deployment
ENV OLLAMA_API_URL="http://localhost:11434"
ENV HF_API_TOKEN=""
ENV USE_HF_FALLBACK="true"
ENV MODEL_PATH="models/weights2_fridge_vision.pt"
ENV CONFIDENCE_THRESHOLD="0.5"
ENV HOST="0.0.0.0"
ENV PORT="8000"

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Run application
CMD ["python", "run_server.py"]
