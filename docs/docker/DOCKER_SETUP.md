# Docker Setup Guide

## Overview

The project uses Docker Compose to orchestrate multiple services for local development:
- **app** - FastAPI application (Python 3.12)
- **postgres** - PostgreSQL 16 database
- **redis** - Redis cache
- **minio** - S3-compatible object storage
- **pgadmin** - PostgreSQL admin UI
- **redis-commander** - Redis admin UI

## Quick Start

### 1. Copy Environment File
```bash
cp .env.example .env
```

Edit `.env` with your settings (especially change passwords in production).

### 2. Start All Services
```bash
make db-up
# or
docker compose up -d
```

### 3. Run Migrations
```bash
make upgrade
# or
poetry run alembic upgrade head
```

### 4. Seed RBAC Data
```bash
make seed-rbac
```

### 5. Start Development Server
```bash
make run
# or
poetry run uvicorn productivity_tracker.main:app --reload
```

## Service URLs

| Service | URL | Credentials |
|---------|-----|-------------|
| API | http://localhost:8000 | - |
| API Docs | http://localhost:8000/docs | - |
| PostgreSQL | localhost:5432 | See `.env` |
| PgAdmin | http://localhost:5050 | See `.env` |
| MinIO Console | http://localhost:9001 | See `.env` |
| MinIO API | http://localhost:9000 | See `.env` |
| Redis | localhost:6379 | No password |
| Redis Commander | http://localhost:8081 | - |

## Makefile Commands

### Database Management
```bash
make db-up          # Start database
make db-down        # Stop database
make db-restart     # Restart database
make db-clean       # Stop and remove volumes (deletes data!)
make db-reset       # Clean + start + migrate
make db-logs        # View database logs
```

### Development Workflow
```bash
make dev-setup      # Complete setup (db + migrations + rbac)
make dev-reset      # Reset development database
make run            # Start dev server
```

### Migrations
```bash
make migrate        # Create new migration (prompts for message)
make upgrade        # Run migrations
make downgrade      # Rollback last migration
```

### Testing
```bash
make test-db-up     # Start test database
make test-db-down   # Stop test database
make test-db-clean  # Clean test database
make test-ci-full   # Run full test suite with coverage
```

## Docker Compose Files

### docker-compose.yml (Development)
Main development environment with all services.

**Services:**
- `app` - FastAPI on port 8000 with hot reload
- `postgres` - PostgreSQL on port 5432
- `redis` - Redis on port 6379
- `minio` - MinIO on ports 9000 (API) and 9001 (console)
- `pgadmin` - PgAdmin on port 5050
- `redis-commander` - Redis UI on port 8081

### docker-compose.test.yml (Testing)
Isolated test database to avoid conflicts with development data.

**Services:**
- `test-db` - PostgreSQL on port 5433

## Dockerfile

Multi-stage build for optimized production images:

**Builder Stage:**
- Installs Poetry and dependencies
- Creates virtual environment
- Production dependencies only

**Runtime Stage:**
- Minimal Python 3.12 slim image
- Copies only virtual environment and application code
- Runs as non-root user
- Health check enabled
- Exposes port 8500

## Environment Variables

### Required Variables
See `.env.example` for full list. Key variables:

```bash
# Database
POSTGRES_USER=lhajoosten
POSTGRES_PASSWORD=your_password
POSTGRES_DB=productivity_db
DATABASE_URL=postgresql://lhajoosten:your_password@localhost:5432/productivity_db

# Application
SECRET_KEY=your-secret-key-change-in-production
ENVIRONMENT=development

# MinIO
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioadmin

# PgAdmin
PGADMIN_DEFAULT_EMAIL=admin@admin.com
PGADMIN_DEFAULT_PASSWORD=admin
```

## Volume Management

### Development Volumes
```bash
docker volume ls | grep productivity
```

Volumes:
- `productivity-tracker-backend_postgres_data` - Database data
- `productivity-tracker-backend_minio_data` - Object storage
- `productivity-tracker-backend_redis_data` - Redis persistence
- `productivity-tracker-backend_pgadmin_data` - PgAdmin settings

### Clean Up Volumes
```bash
# Warning: Deletes ALL data!
make db-clean

# Manual cleanup
docker compose down -v
```

## Networking

All services run on the `productivity-network` bridge network, allowing:
- Service-to-service communication by container name
- Isolated from other Docker projects
- DNS resolution (e.g., `postgres:5432` from app container)

## Development Tips

### Hot Reload
The app container mounts source code as volumes for hot reload:
```yaml
volumes:
  - ./productivity_tracker:/app/productivity_tracker:cached
  - ./migrations:/app/migrations:cached
```

Changes to Python files automatically restart the server.

### Connect to Database from Host
```bash
# Using psql
psql postgresql://lhajoosten:your_password@localhost:5432/productivity_db

# Using PgAdmin
# Navigate to http://localhost:5050
# Add server: postgres (from container) or localhost:5432 (from host)
```

### View Logs
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f app
docker compose logs -f postgres

# Using make
make db-logs
```

### Execute Commands in Container
```bash
# Shell access
docker compose exec app bash

# Run Alembic migration
docker compose exec app alembic upgrade head

# Run Python script
docker compose exec app python -m productivity_tracker.scripts.seed_rbac
```

## Production Deployment

### Build Production Image
```bash
docker build -t productivity-tracker:latest .
```

### Environment Overrides
In production, override with environment-specific values:
```bash
docker run -e DATABASE_URL=postgresql://... \
           -e SECRET_KEY=... \
           -e ENVIRONMENT=production \
           -p 8500:8500 \
           productivity-tracker:latest
```

### Health Check
The Dockerfile includes a health check:
```dockerfile
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8500/health')"
```

Verify health:
```bash
docker inspect --format='{{.State.Health.Status}}' <container_id>
```

## Troubleshooting

### Port Already in Use
```bash
# Find process using port
lsof -i :5432
sudo lsof -i :5432

# Kill process or change port in docker-compose.yml
```

### Database Connection Issues
```bash
# Check if postgres is healthy
docker compose ps

# View postgres logs
docker compose logs postgres

# Verify environment variables
docker compose exec app env | grep DATABASE
```

### Permission Issues
```bash
# Fix ownership of volumes
sudo chown -R $USER:$USER ./

# Reset volumes
make db-clean
make db-up
```

### Container Won't Start
```bash
# Check logs
docker compose logs app

# Rebuild image
docker compose build --no-cache app
docker compose up -d app
```

### Migration Issues
```bash
# Check current revision
docker compose exec app alembic current

# View migration history
docker compose exec app alembic history

# Downgrade if needed
docker compose exec app alembic downgrade -1
```

## Testing Database

The test database runs on a separate port (5433) to avoid conflicts:

```bash
# Start test database
make test-db-up

# Run tests
TESTING=1 TEST_DATABASE_URL=postgresql://test_user:test_password@localhost:5433/test_productivity_tracker \
poetry run pytest

# Clean up
make test-db-clean
```

## Complete Setup Example

Starting from scratch:

```bash
# 1. Clone repository
cd productivity-tracker-backend

# 2. Copy environment file
cp .env.example .env

# 3. Edit .env with your settings
nano .env

# 4. Install dependencies
poetry install

# 5. Start all services
make dev-setup
# This runs: db-up + upgrade + seed-rbac

# 6. Create superuser
make create-superuser

# 7. Start development server
make run

# 8. Visit http://localhost:8000/docs
```

## Useful One-Liners

```bash
# Restart everything
docker compose restart

# Remove all containers and volumes
docker compose down -v && docker compose up -d

# View all running containers
docker compose ps

# Stop everything
docker compose down

# Follow all logs
docker compose logs -f

# Rebuild and restart app only
docker compose up -d --build app
```

## Security Notes

1. **Change default passwords** in `.env` for production
2. **Use secrets management** (not .env files) in production
3. **Limit exposed ports** - only expose what's needed
4. **Use non-root user** (already configured in Dockerfile)
5. **Update base images** regularly
6. **Scan images** for vulnerabilities

## See Also

- [Makefile](../../Makefile) - All available commands
- [.env.example](../../.env.example) - Environment variables template
- [docker-compose.yml](../../docker-compose.yml) - Development services
- [Dockerfile](../../Dockerfile) - Application image
