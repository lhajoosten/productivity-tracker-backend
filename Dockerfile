FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# System deps only for building wheels (remove if not needed)
RUN apt-get update && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps into a virtualenv for reuse
COPY requirements.txt ./
RUN python -m venv /opt/venv \
    && . /opt/venv/bin/activate \
    && pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

WORKDIR /app

# Copy the virtualenv from the builder
COPY --from=builder /opt/venv /opt/venv

# Copy application code
COPY . .

# Run as non-root
RUN useradd -r -u 10001 appuser
USER 10001

EXPOSE 8000

# Adjust the module path if your app entrypoint differs
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
