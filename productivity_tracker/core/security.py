"""Security utilities for password hashing and JWT tokens."""

from datetime import datetime, timedelta

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from productivity_tracker.core.settings import settings

# Initialize Argon2 password hasher
ph = PasswordHasher()


def hash_password(password: str) -> str:
    """Hash a password using Argon2."""
    return str(ph.hash(password))


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash using Argon2."""
    try:
        ph.verify(hashed_password, plain_password)
        # Check if rehash is needed (if parameters changed)
        if ph.check_needs_rehash(hashed_password):
            # In production, you should update the password hash in the database
            pass
        return True
    except VerifyMismatchError:
        return False


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    to_encode.update({"type": "access"})  # nosec

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire, "type": "access"})  # nosec
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return str(encoded_jwt)


def create_refresh_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Create a JWT refresh token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return str(encoded_jwt)


def decode_token(token: str) -> dict | None:
    """Decode and verify a JWT token."""
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return dict(payload) if payload else None
    except jwt.ExpiredSignatureError:
        return None
    except jwt.JWTError:
        return None
