FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies and Poetry
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && curl -sSL https://install.python-poetry.org | python3 - \
    && ln -s /root/.local/bin/poetry /usr/local/bin/poetry

# Configure Poetry to not create virtual environments (use system Python)
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_CACHE_DIR=/tmp/poetry_cache

# Copy Poetry files
COPY pyproject.toml poetry.lock* ./

# Install dependencies using Poetry (directly to system Python)
RUN poetry install --no-root --only main && rm -rf $POETRY_CACHE_DIR

# Copy application code
COPY . .

# Install project
RUN poetry install --only-root

# Set Python path
ENV PYTHONPATH="/app:$PYTHONPATH"

# Expose port
EXPOSE 8500

# Default command - use uvicorn directly since it's installed in system Python
CMD ["uvicorn", "productivity_tracker.main:app", "--host", "0.0.0.0", "--port", "8500", "--reload"]
