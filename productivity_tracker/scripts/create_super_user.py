"""Script to create a superuser interactively from the terminal."""

import re
import sys
from getpass import getpass

from sqlalchemy.exc import IntegrityError

from productivity_tracker.core.security import hash_password
from productivity_tracker.database import SessionLocal
from productivity_tracker.database.entities import User


def validate_email(email: str) -> bool:
    """Basic email validation."""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None


def validate_username(username: str) -> bool:
    """Username validation (3-50 chars, alphanumeric and underscores)."""
    if len(username) < 3 or len(username) > 50:
        return False
    pattern = r"^[a-zA-Z0-9_]+$"
    return re.match(pattern, username) is not None


def validate_password(password: str) -> bool:
    """Password validation (minimum 8 characters)."""
    return len(password) >= 8


def create_super_user():
    """Create a new superuser interactively."""
    print("\n" + "=" * 60)
    print("CREATE SUPERUSER")
    print("=" * 60 + "\n")

    db = SessionLocal()
    try:
        # Get username
        while True:
            username = input("Username (3-50 chars, alphanumeric + underscore): ").strip()
            if not username:
                print("❌ Username cannot be empty.")
                continue
            if not validate_username(username):
                print(
                    "❌ Invalid username. Must be 3-50 characters, alphanumeric and underscores only."
                )
                continue

            # Check if username exists
            existing = db.query(User).filter(User.username == username).first()
            if existing:
                print(f"❌ Username '{username}' already exists.")
                continue
            break

        # Get email
        while True:
            email = input("Email: ").strip()
            if not email:
                print("❌ Email cannot be empty.")
                continue
            if not validate_email(email):
                print("❌ Invalid email format.")
                continue

            # Check if email exists
            existing = db.query(User).filter(User.email == email).first()
            if existing:
                print(f"❌ Email '{email}' already exists.")
                continue
            break

        # Get password
        while True:
            password = getpass("Password (minimum 8 characters): ")
            if not password:
                print("❌ Password cannot be empty.")
                continue
            if not validate_password(password):
                print("❌ Password must be at least 8 characters long.")
                continue

            password_confirm = getpass("Confirm password: ")
            if password != password_confirm:
                print("❌ Passwords do not match.")
                continue
            break

        # Create superuser
        print("\n" + "-" * 60)
        print("Creating superuser...")

        superuser = User(
            username=username,
            email=email,
            hashed_password=hash_password(password),
            is_active=True,
            is_superuser=True,
            role_id=None,  # Superusers don't need a role
        )

        db.add(superuser)
        db.commit()
        db.refresh(superuser)

        print("✅ Superuser created successfully!")
        print("-" * 60)
        print(f"ID:           {superuser.id}")
        print(f"Username:     {superuser.username}")
        print(f"Email:        {superuser.email}")
        print(f"Is Active:    {superuser.is_active}")
        print(f"Is Superuser: {superuser.is_superuser}")
        print(f"Created At:   {superuser.created_at}")
        print("-" * 60 + "\n")

        return 0

    except IntegrityError as e:
        db.rollback()
        print(f"\n❌ Database error: {e}")
        print("The user might already exist or there's a constraint violation.")
        return 1
    except KeyboardInterrupt:
        print("\n\n❌ Cancelled by user.")
        return 130
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error creating superuser: {e}")
        import traceback

        traceback.print_exc()
        return 1
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(create_super_user())
