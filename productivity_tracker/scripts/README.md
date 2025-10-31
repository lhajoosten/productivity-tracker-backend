# Development Scripts

This directory contains utility scripts for setting up and managing the development environment.

## Available Scripts

### 1. `create_super_user.py`
Creates a superuser account interactively.

**Usage:**
```bash
python -m productivity_tracker.scripts.create_super_user
```

**Interactive prompts:**
- Username (3-50 chars, alphanumeric + underscore)
- Email
- Password (minimum 8 characters)

**Example:**
```bash
python -m productivity_tracker.scripts.create_super_user

# Follow the prompts:
Username: johndoe
Email: john@example.com
Password: ********
Confirm password: ********
```

---

### 2. `seed_rbac.py`
Seeds the database with roles and permissions for Role-Based Access Control (RBAC).

**Usage:**
```bash
python -m productivity_tracker.scripts.seed_rbac
```

**What it creates:**
- **Permissions:** CRUD permissions for users, tasks, projects, organizations, departments, teams
- **Roles:**
  - `admin` - Full access to all resources
  - `organization_manager` - Manage organizations, departments, and teams
  - `department_manager` - Manage departments and teams
  - `team_lead` - Lead teams, manage team members and tasks
  - `user` - Create and manage own tasks and projects
  - `viewer` - Read-only access

**Note:** Also creates a default admin user (username: `admin`, password: `admin123`). Change this password immediately!

---

### 3. `seed_test_data.py`
Seeds the database with comprehensive test data for development and testing.

**Usage:**
```bash
python -m productivity_tracker.scripts.seed_test_data <superuser_id>
```

**Arguments:**
- `<superuser_id>`: UUID of an existing superuser account

**Example:**
```bash
python -m productivity_tracker.scripts.seed_test_data "ad9c3024-8c65-4ec9-a2d8-0347f8106f0d"
```

**What it creates:**

#### Organizations
- **TechCorp Industries** - Technology solutions provider
- **Innovate Solutions** - AI/ML startup

#### Departments
- TechCorp:
  - Engineering
  - Product Management
  - Sales & Marketing
- Innovate:
  - Research & Development
  - Operations

#### Teams
- Backend Team (Engineering)
- Frontend Team (Engineering)
- Product Strategy (Product Management)
- AI Research (R&D)

#### Users (18 test users)
All users have password: `password123`

**Organization Managers:**
- alice_smith@techcorp.com
- bob_johnson@innovate.com

**Department Managers:**
- carol_williams@techcorp.com
- david_brown@techcorp.com
- emily_davis@innovate.com

**Team Leads:**
- frank_miller@techcorp.com (Backend Team)
- grace_wilson@techcorp.com (Frontend Team)
- henry_moore@techcorp.com (Product Strategy)
- iris_taylor@innovate.com (AI Research)

**Regular Users:**
- jack_anderson@techcorp.com
- kate_thomas@techcorp.com
- liam_jackson@techcorp.com
- mia_white@techcorp.com
- noah_harris@innovate.com
- olivia_martin@innovate.com

**Viewers:**
- peter_garcia@techcorp.com
- quinn_rodriguez@innovate.com

**Admin:**
- rachel_admin@techcorp.com

---

### 4. `setup_dev_env.py` ⭐ **Recommended**
All-in-one script that runs both `seed_rbac.py` and `seed_test_data.py` in sequence.

**Usage:**
```bash
python -m productivity_tracker.scripts.setup_dev_env <superuser_id>
```

**Arguments:**
- `<superuser_id>`: UUID of an existing superuser account

**Example:**
```bash
python -m productivity_tracker.scripts.setup_dev_env "ad9c3024-8c65-4ec9-a2d8-0347f8106f0d"
```

**What it does:**
1. Seeds RBAC roles and permissions
2. Seeds test data (organizations, departments, teams, users)

This is the easiest way to get started with a fully populated development environment!

---

## Quick Start Guide

### First Time Setup

1. **Create a superuser:**
   ```bash
   python -m productivity_tracker.scripts.create_super_user
   ```

2. **Setup development environment:**
   ```bash
   python -m productivity_tracker.scripts.setup_dev_env "<your-superuser-id>"
   ```

That's it! Your development database is now fully populated with realistic test data.

### Alternative: Step-by-Step Setup

If you prefer to run scripts individually:

1. **Create a superuser:**
   ```bash
   python -m productivity_tracker.scripts.create_super_user
   ```

2. **Seed RBAC:**
   ```bash
   python -m productivity_tracker.scripts.seed_rbac
   ```

3. **Seed test data:**
   ```bash
   python -m productivity_tracker.scripts.seed_test_data "<your-superuser-id>"
   ```

---

## Testing Scenarios

With the seeded test data, you can test various scenarios:

### 1. Organization Management
- Login as `alice_smith` (organization_manager)
- Manage TechCorp Industries
- View/edit departments and teams

### 2. Department Management
- Login as `carol_williams` (department_manager)
- Manage Engineering department
- Create/manage teams

### 3. Team Leadership
- Login as `frank_miller` (team_lead)
- Manage Backend Team
- Add/remove team members
- Assign tasks

### 4. Regular User Workflow
- Login as `jack_anderson` (user)
- Create and manage tasks
- View team and organization info

### 5. Viewer Access
- Login as `peter_garcia` (viewer)
- Read-only access to verify permissions

### 6. Admin Operations
- Login as `rachel_admin` (admin)
- Full access to all resources

---

## Notes

- **Default Password:** All test users have password `password123`
- **Idempotent:** Scripts can be run multiple times safely (they skip existing records)
- **Security:** Remember to change default passwords in production!
- **Database:** Ensure your database is running and accessible before running scripts

---

## Troubleshooting

### "No roles found" error
Run `seed_rbac.py` before `seed_test_data.py`:
```bash
python -m productivity_tracker.scripts.seed_rbac
```

### "Superuser not found" error
Make sure you're using the correct superuser UUID:
```bash
# Get your superuser ID from the API or database
python -m productivity_tracker.scripts.seed_test_data "correct-uuid-here"
```

### Database connection errors
Check your database connection settings in `.env` or config files.

---

## Development Workflow

After initial setup, you typically only need to:

1. **Reset database** (when needed):
   ```bash
   # Drop and recreate database
   # Then run migrations
   alembic upgrade head
   ```

2. **Re-seed data**:
   ```bash
   python -m productivity_tracker.scripts.setup_dev_env "<superuser-id>"
   ```

This gives you a fresh, consistent development environment!
