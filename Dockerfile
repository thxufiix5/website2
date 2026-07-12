FROM python:3.11-slim

# Set workdir
WORKDIR /app

# Prevent Python from writing pyc files and buffer stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy application
COPY . /app

# Default port used by many PaaS providers; Render will set $PORT at runtime
ENV PORT 10000

# Use shell form so $PORT is expanded
CMD gunicorn app:app --bind 0.0.0.0:$PORT --workers 3
