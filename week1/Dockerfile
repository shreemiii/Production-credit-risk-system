
# Credit-risk scoring service
# Build: docker build -t credit-risk-api .
# Run: docker run -p 8080:8080 -v "$PWD/models:/app/models" credit-risk-api

FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080

WORKDIR /app

# Install pinned API dependencies
COPY requirements-api.txt .
RUN pip install --no-cache-dir -r requirements-api.txt

# Copy only the API code
COPY api/ api/

# Run as a non-root user
RUN useradd --create-home appuser
USER appuser

# Start FastAPI using the Cloud Run port
CMD ["sh", "-c", "exec uvicorn api.main:app --host 0.0.0.0 --port ${PORT}"]
