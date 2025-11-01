# Productivity Tracker Backend

[![CI/CD Pipeline](https://github.com/lhajoosten/productivity-tracker-backend/actions/workflows/ci-pipeline.yml/badge.svg)](https://github.com/lhajoosten/productivity-tracker-backend/actions/workflows/ci-pipeline.yml)
[![codecov](https://codecov.io/gh/lhajoosten/productivity-tracker-backend/branch/master/graph/badge.svg)](https://codecov.io/gh/lhajoosten/productivity-tracker-backend)
[![Python Version](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.199-009688.svg?logo=fastapi)](https://fastapi.tiangolo.com)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Poetry](https://img.shields.io/endpoint?url=https://python-poetry.org/badge/v0.json)](https://python-poetry.org/)
[![Pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)

A production-grade FastAPI backend for comprehensive productivity tracking with enterprise-level authentication, authorization, and RBAC (Role-Based Access Control).

## 🎯 Vision

The Productivity Tracker is designed to evolve from a foundational RBAC system into a full-featured, AI-powered productivity platform. Our roadmap follows a logical progression:

**Phase 1 (v1.0-1.6):** Security, validation, and core productivity tracking
**Phase 2 (v2.0-2.3):** Enterprise features, performance, and observability
**Phase 3 (v3.0+):** AI integration, accessibility, and platform extensibility

Each version builds upon the previous with **no breaking changes within major versions**, ensuring stability while continuously improving quality, security, scalability, and user experience.

📖 **See our complete vision:** [Version Roadmap](docs/versioning/VERSION_ROADMAP.md)

## 📋 Current Status

**🎯 Version:** 1.0.0-beta - **Foundation Release**

**Release Name:** Foundation - First Beta
**Release Date:** January 2025
**API Version:** v1

**✅ Implemented Features:**
- ✅ JWT-based authentication with Argon2 password hashing
- ✅ Complete RBAC system (users, roles, permissions)
- ✅ Organization, department, and team management
- ✅ Comprehensive API documentation (OpenAPI/Swagger)
- ✅ Production-grade error handling and logging
- ✅ Database migrations with Alembic
- ✅ Health check endpoints
- ✅ API versioning infrastructure

**🔜 Next Release:** v1.1.0 - Security & Validation Enhancement (Q1 2026)
- Rate limiting and account lockout
- Enhanced password policies
- Audit logging system
- Increased test coverage (85%+)

## 📊 Code Coverage

[![codecov](https://codecov.io/gh/lhajoosten/productivity-tracker-backend/branch/master/graph/badge.svg)](https://codecov.io/gh/lhajoosten/productivity-tracker-backend)

Current coverage: ![coverage](https://codecov.io/gh/lhajoosten/productivity-tracker-backend/branch/master/graphs/sunburst.svg)

## 🚀 Features

### ✅ Core Features (v1.0 - Available Now)

- **Authentication & Authorization**
  - JWT-based authentication with access and refresh tokens
  - Cookie-based session management
  - Password hashing with Argon2
  - Role-Based Access Control (RBAC)
  - Permission management system

- **Organization Management**
  - Multi-organization support
  - Department hierarchy management
  - Team creation and member management
  - User assignment to organizations/departments/teams

- **API Features**
  - RESTful API design with versioning support
  - Automatic OpenAPI/Swagger documentation
  - Request/response validation with Pydantic
  - **User-friendly error handling with proper context**
  - Request logging with user tracking
  - Consistent error response format

- **Database**
  - PostgreSQL with SQLAlchemy ORM
  - Alembic migrations
  - Soft delete support
  - Repository pattern for data access

- **Security**
  - Security headers middleware
  - CORS configuration
  - Input validation
  - SQL injection protection
  - Secret detection in pre-commit hooks

- **Code Quality**
  - Pre-commit hooks with multiple checks
  - Black code formatting
  - Ruff linting
  - mypy type checking
  - Bandit security scanning
  - Comprehensive test coverage

### 🗺️ Product Roadmap

Our product evolution follows a strategic, logical progression from core functionality to enterprise-grade features and beyond. Each version is carefully designed to build upon the previous while maintaining backward compatibility within major versions.

**📖 Complete Roadmap:** See [docs/VERSION_ROADMAP.md](docs/versioning/VERSION_ROADMAP.md) for detailed version planning

#### Quick Overview

**v1.0.0-beta (Current)** - Foundation ✅
- Core RBAC, authentication, organization management

**v1.1.0** (Q1 2026) - Security & Validation Enhancement
- Rate limiting, audit logging, enhanced security

**v1.2.0** (Q2 2026) - Productivity Tracking Core
- Time tracking, task management, projects

**v1.3.0** (Q3 2026) - Analytics & Reporting
- Dashboards, reports, performance metrics

**v1.4.0** (Q4 2026) - Collaboration & Communication
- Comments, notifications, file attachments

**v1.5.0** (Q1 2027) - Performance & Scalability
- Caching, bulk operations, database optimization

**v1.6.0** (Q2 2027) - Integration & Extensibility
- Webhooks, third-party integrations, plugin framework

**v2.0.0** (Q3 2027) - Enterprise Features
- Multi-region, SSO/SAML, GDPR compliance, enhanced security

**v2.1.0** (Q4 2027) - AI & Machine Learning
- AI-powered productivity insights, automation, predictions

**v2.2.0** (Q1 2028) - Accessibility & Internationalization
- Multi-language, WCAG compliance, global reach

**v2.3.0** (Q2 2028) - Advanced Quality & Observability
- Distributed tracing, 95%+ test coverage, SRE practices

**v3.0.0** (Future) - Platform Evolution
- Low-code workflows, marketplace, next-gen features

### 📐 Our Approach to Quality

We prioritize production-grade quality across all dimensions:

- **🔐 Security:** Continuous security improvements, regular audits, OWASP compliance
- **📊 Quality:** Increasing test coverage (80% → 95%), automated quality checks
- **⚡ Performance:** Optimized response times, caching, scalability features
- **🌍 Accessibility:** WCAG compliance, internationalization, inclusive design
- **🤝 Collaboration:** Team features, real-time updates, communication tools
- **🔍 Observability:** Logging, monitoring, tracing, alerting
- **📈 Scalability:** Multi-region support, performance optimization, load handling

**Quality Gates:** Each release must pass strict criteria for code quality, security, performance, and documentation before deployment.

**Versioning Strategy:** We follow [Semantic Versioning 2.0.0](https://semver.org/) - see [docs/VERSIONING_STRATEGY.md](docs/versioning/VERSIONING_STRATEGY.md)

## 📋 Requirements

- Python 3.12+
- PostgreSQL 14+
- Poetry (Python package manager)

## 🛠️ Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd productivity-tracker-backend
```

### 2. Install dependencies and set up pre-commit hooks

```bash
make setup
```

Or manually:

```bash
poetry install
poetry run pre-commit install
```

### 3. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` and update the values:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/productivity_tracker
SECRET_KEY=your-secret-key-here
DEBUG=True
```

### 4. Run database migrations

```bash
make upgrade
```

Or:

```bash
poetry run alembic upgrade head
```

### 5. Create a superuser (optional)

```bash
poetry run prd_tracker create-super-user
```

### 6. Seed RBAC data (optional but recommended)

```bash
poetry run python productivity_tracker/scripts/seed_rbac.py
```

This creates default roles (admin, user, viewer) and permissions.

## 🏃 Running the Application

### Development server

```bash
make run
```

Or:

```bash
poetry run uvicorn productivity_tracker.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:

- **API**: <http://localhost:8500>
- **Swagger UI**: <http://localhost:8500/docs>
- **ReDoc**: <http://localhost:8500/redoc>

### 🔄 API Versioning

The API uses semantic versioning with the following structure:
- **Current Version:** v1.0 (Production Ready)
- **API Base Path:** `/api/v1.0/` or `/api/v1/` (major version alias)
- **Feature Flags:** Controlled via version-specific feature toggles

**Version Status:**
- ✅ **v1.0** - Active (Core RBAC, Organizations, Teams, Departments)
- 🚧 **v1.1** - In Development (Audit Logging, Bulk Operations, Search)
- 📋 **v1.2** - Planned (Advanced Permissions, Notifications)
- 🔮 **v2.0** - Future (Projects, Tasks, Time Tracking)

## 🧪 Testing

```bash
# Run tests
make test

# Run tests with coverage report
make test-cov
```

## 📖 Documentation

Comprehensive guides are available in the `docs/` folder:

- **[Error Handling Guide](docs/ERROR_HANDLING.md)** - Learn about the error handling system, custom exceptions, and user-friendly error messages
- **[RBAC Guide](docs/RBAC_HANDLING.md)** - Complete guide to Role-Based Access Control, permissions, and security best practices

### Key Concepts

#### Error Handling
All errors return consistent, user-friendly messages without exposing technical details:
```json
{
  "error": "INVALID_CREDENTIALS",
  "message": "Invalid email or password. Please check your credentials and try again."
}
```

See the [Error Handling Guide](docs/ERROR_HANDLING.md) for complete documentation.

#### Role-Based Access Control (RBAC)
Fine-grained access control through a Users → Roles → Permissions model:
- Users can have multiple roles
- Roles contain multiple permissions
- Permissions follow the format `resource:action` (e.g., `users:delete`)

See the [RBAC Guide](docs/RBAC_HANDLING.md) for complete documentation.

## 📝 Development

### Available Make Commands

```bash
make help              # Show all available commands
make dev-install       # Install all dependencies including dev tools
make format            # Format code with Black and isort
make lint              # Run linters (Ruff, mypy, bandit)
make test              # Run tests
make test-cov          # Run tests with coverage
make run               # Run development server
make migrate           # Create a new migration
make upgrade           # Apply migrations
make downgrade         # Rollback last migration
make clean             # Clean cache files
make pre-commit        # Run pre-commit hooks on all files
make check             # Run lint + test
```

### Code Style

This project uses:

- **Black** for code formatting
- **isort** for import sorting
- **Ruff** for linting
- **mypy** for type checking

Format your code before committing:

```bash
make format
```

### Pre-commit Hooks

Pre-commit hooks automatically run on `git commit` to:

- Format code with Black
- Sort imports with isort
- Lint with Ruff
- Check types with mypy
- Scan for security issues with Bandit
- Detect secrets
- Check YAML/JSON syntax
- Remove trailing whitespace

Run hooks manually:

```bash
make pre-commit
```

## 🗄️ Database Migrations

### Create a new migration

```bash
make migrate
# Or with message:
poetry run alembic revision --autogenerate -m "your migration message"
```

### Apply migrations

```bash
make upgrade
```

### Rollback

```bash
make downgrade
```

## 📚 API Documentation

### 🔐 Authentication Endpoints

- `POST /auth/register` - Register a new user
- `POST /auth/login` - Login and receive access token
- `POST /auth/logout` - Logout and clear token
- `POST /auth/refresh` - Refresh access token
- `GET /auth/me` - Get current user info
- `PUT /auth/me` - Update current user
- `PUT /auth/me/password` - Change password

### 👥 User Management (Admin only)

- `GET /auth/users` - List all users
- `GET /auth/users/{user_id}` - Get user by ID
- `PUT /auth/users/{user_id}` - Update user
- `DELETE /auth/users/{user_id}` - Delete user
- `POST /auth/users/{user_id}/activate` - Activate user
- `POST /auth/users/{user_id}/deactivate` - Deactivate user
- `POST /auth/users/{user_id}/roles` - Assign roles to user

### 🏢 Organization Management

- `POST /organizations` - Create organization
- `GET /organizations` - List all organizations
- `GET /organizations/{org_id}` - Get organization by ID
- `GET /organizations/current` - Get current user's organization
- `PUT /organizations/{org_id}` - Update organization
- `DELETE /organizations/{org_id}` - Delete organization
- `POST /organizations/{org_id}/members/{user_id}` - Add member to organization
- `DELETE /organizations/{org_id}/members/{user_id}` - Remove member from organization
- `GET /organizations/{org_id}/members` - Get organization members

### 🏬 Department Management

- `POST /departments` - Create department
- `GET /departments` - List all departments
- `GET /departments/{dept_id}` - Get department by ID
- `GET /departments/organization/{org_id}` - Get departments by organization
- `PUT /departments/{dept_id}` - Update department
- `DELETE /departments/{dept_id}` - Delete department

### 👨‍👩‍👧‍👦 Team Management

- `POST /teams` - Create team
- `GET /teams` - List all teams
- `GET /teams/{team_id}` - Get team by ID
- `GET /teams/department/{dept_id}` - Get teams by department
- `PUT /teams/{team_id}` - Update team
- `DELETE /teams/{team_id}` - Delete team
- `POST /teams/{team_id}/members` - Add member to team
- `DELETE /teams/{team_id}/members` - Remove member from team
- `GET /teams/{team_id}/members` - Get team members

### 🎭 Role Management (Admin only)

- `POST /roles/` - Create role
- `GET /roles/` - List all roles
- `GET /roles/{role_id}` - Get role by ID
- `GET /roles/name/{role_name}` - Get role by name
- `PUT /roles/{role_id}` - Update role
- `DELETE /roles/{role_id}` - Delete role
- `POST /roles/{role_id}/permissions` - Assign permissions to role
- `DELETE /roles/{role_id}/permissions/{permission_id}` - Remove permission from role

### 🔑 Permission Management (Admin only)

- `POST /permissions/` - Create permission
- `GET /permissions/` - List all permissions
- `GET /permissions/{permission_id}` - Get permission by ID
- `PUT /permissions/{permission_id}` - Update permission
- `DELETE /permissions/{permission_id}` - Delete permission

### 🏥 System Health

- `GET /health` - Health check endpoint

## 📈 API Overview

The API currently provides **75+ endpoints** across **8 main modules**:

| Module | Endpoints | Description |
|--------|-----------|-------------|
| **Authentication** | 14 | User registration, login, profile management |
| **Organizations** | 8 | Multi-org support, member management |
| **Departments** | 6 | Department hierarchy within organizations |
| **Teams** | 7 | Team creation, member assignment |
| **Roles** | 8 | Role-based access control |
| **Permissions** | 5 | Granular permission management |
| **Admin** | 3 | Administrative utilities |
| **Health** | 1 | System monitoring |

**Total Coverage:**
- ✅ **Complete CRUD** operations for all entities
- ✅ **Relationship management** between entities
- ✅ **Soft delete** support across all models
- ✅ **Pagination** on all list endpoints
- ✅ **Filtering** by parent entities (org → dept → team)
- ✅ **Member counting** and statistics

## 🏗️ Project Structure

```text
productivity-tracker-backend/
├── productivity_tracker/
│   ├── api/                    # API routes
│   │   ├── auth.py            # Authentication endpoints
│   │   ├── organizations.py   # Organization management
│   │   ├── departments.py     # Department management
│   │   ├── teams.py           # Team management
│   │   ├── roles.py           # Role management
│   │   ├── permissions.py     # Permission management
│   │   ├── admin.py           # Admin utilities
│   │   ├── setup.py           # API setup
│   │   └── health.py          # Health check
│   ├── core/                   # Core functionality
│   │   ├── database.py        # Database connection
│   │   ├── security.py        # Security utilities
│   │   ├── dependencies.py    # FastAPI dependencies
│   │   ├── middleware.py      # Custom middleware
│   │   ├── settings.py        # Configuration
│   │   ├── exceptions.py      # Custom exceptions
│   │   ├── exception_filter.py # Global exception handling
│   │   ├── logging_config.py  # Logging setup
│   │   └── setup.py           # Core setup
│   ├── database/
│   │   └── entities/          # SQLAlchemy models
│   │       ├── base.py        # Base entity
│   │       ├── user.py        # User model
│   │       ├── role.py        # Role & Permission models
│   │       ├── organization.py # Organization model
│   │       ├── department.py  # Department model
│   │       └── team.py        # Team model
│   ├── models/                 # Pydantic schemas
│   │   ├── auth.py            # Auth-related schemas
│   │   └── organization.py    # Organization schemas
│   ├── repositories/           # Data access layer
│   │   ├── base.py            # Base repository
│   │   ├── user_repository.py
│   │   ├── role_repository.py
│   │   ├── permission_repository.py
│   │   ├── organization_repository.py
│   │   ├── department_repository.py
│   │   └── team_repository.py
│   ├── services/               # Business logic
│   │   ├── user_service.py
│   │   ├── role_service.py
│   │   ├── permission_service.py
│   │   ├── organization_service.py
│   │   ├── department_service.py
│   │   └── team_service.py
│   ├── versioning/             # API versioning
│   │   ├── versioning.py      # Version definitions
│   │   ├── utils.py           # Versioning utilities
│   │   └── version.py         # Version helpers
│   ├── scripts/                # Utility scripts
│   │   ├── create_super_user.py
│   │   └── seed_rbac.py
│   ├── cli.py                  # CLI commands
│   └── main.py                 # FastAPI application
├── migrations/                  # Alembic migrations
├── tests/                       # Test files
├── logs/                        # Application logs
├── .env.example                 # Environment template
├── .pre-commit-config.yaml     # Pre-commit configuration
├── pyproject.toml              # Project dependencies & config
├── Makefile                     # Development commands
└── README.md
```

## 🔐 Security

- Passwords are hashed using Argon2
- JWT tokens for stateless authentication
- HTTP-only cookies for token storage
- CORS configuration for cross-origin requests
- Security headers middleware
- Input validation with Pydantic
- SQL injection protection via SQLAlchemy ORM
- Secret detection in pre-commit hooks

## 📊 Logging

Logs are written to:

- **Console**: Colored output for development
- **logs/app.log**: All application logs (rotating, 10MB max)
- **logs/error.log**: Error logs only (daily rotation, 30 days)

Log format includes:

- Timestamp
- Log level
- Module name
- Request method and path
- User information (if authenticated)
- Response status and duration

## 🤝 Contributing

1. Create a feature branch
2. Make your changes
3. Run `make check` to ensure all tests pass
4. Commit your changes (pre-commit hooks will run automatically)
5. Push and create a pull request

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE.md) file for details.
