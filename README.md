# Productivity Tracker Backend

A production-ready FastAPI backend for tracking productivity metrics with
comprehensive authentication, authorization, and RBAC (Role-Based Access
Control).

## 🚀 Features

- **Authentication & Authorization**
  - JWT-based authentication with access and refresh tokens
  - Cookie-based session management
  - Password hashing with Argon2
  - Role-Based Access Control (RBAC)
  - Permission management system

- **API Features**
  - RESTful API design
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

### Authentication Endpoints

- `POST /auth/register` - Register a new user
- `POST /auth/login` - Login and receive access token
- `POST /auth/logout` - Logout and clear token
- `POST /auth/refresh` - Refresh access token
- `GET /auth/me` - Get current user info
- `PUT /auth/me` - Update current user
- `PUT /auth/me/password` - Change password

### User Management (Admin only)

- `GET /auth/users` - List all users
- `GET /auth/users/{user_id}` - Get user by ID
- `PUT /auth/users/{user_id}` - Update user
- `DELETE /auth/users/{user_id}` - Delete user
- `POST /auth/users/{user_id}/activate` - Activate user
- `POST /auth/users/{user_id}/deactivate` - Deactivate user
- `POST /auth/users/{user_id}/roles` - Assign roles to user

### Role Management (Admin only)

- `POST /roles/` - Create role
- `GET /roles/` - List all roles
- `GET /roles/{role_id}` - Get role by ID
- `PUT /roles/{role_id}` - Update role
- `DELETE /roles/{role_id}` - Delete role
- `POST /roles/{role_id}/permissions` - Assign permissions to role

### Permission Management (Admin only)

- `POST /permissions/` - Create permission
- `GET /permissions/` - List all permissions
- `GET /permissions/{permission_id}` - Get permission by ID
- `PUT /permissions/{permission_id}` - Update permission
- `DELETE /permissions/{permission_id}` - Delete permission

## 🏗️ Project Structure

```text
productivity-tracker-backend/
├── productivity_tracker/
│   ├── api/                    # API routes
│   │   ├── auth.py            # Authentication endpoints
│   │   ├── roles.py           # Role management
│   │   ├── permissions.py     # Permission management
│   │   └── health.py          # Health check
│   ├── core/                   # Core functionality
│   │   ├── database.py        # Database connection
│   │   ├── security.py        # Security utilities
│   │   ├── dependencies.py    # FastAPI dependencies
│   │   ├── middleware.py      # Custom middleware
│   │   ├── settings.py        # Configuration
│   │   └── logging_config.py  # Logging setup
│   ├── database/
│   │   └── entities/          # SQLAlchemy models
│   │       ├── base.py        # Base entity
│   │       ├── user.py        # User model
│   │       └── role.py        # Role & Permission models
│   ├── models/                 # Pydantic schemas
│   │   └── auth.py            # Auth-related schemas
│   ├── repositories/           # Data access layer
│   │   ├── base.py            # Base repository
│   │   ├── user_repository.py
│   │   ├── role_repository.py
│   │   └── permission_repository.py
│   ├── services/               # Business logic
│   │   ├── user_service.py
│   │   ├── role_service.py
│   │   └── permission_service.py
│   ├── scripts/                # Utility scripts
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
