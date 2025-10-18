# Error Handling Guide

This document describes the comprehensive error handling system implemented in the productivity tracker backend.

## Overview

The error handling system provides:
- **User-friendly error messages** - No technical jargon exposed to end users
- **Detailed logging** - Full technical context for debugging
- **Consistent error format** - All errors follow the same JSON structure
- **Proper HTTP status codes** - Semantic status codes for different error types
- **Context tracking** - Additional debugging information in development mode

## Error Response Format

All errors return a consistent JSON structure:

```json
{
  "error": "ERROR_CODE",
  "message": "User-friendly message describing what went wrong",
  "debug_context": {
    "field": "value",
    "additional": "context"
  }
}
```

For validation errors:
```json
{
  "error": "VALIDATION_ERROR",
  "message": "The information provided is invalid. Please check the fields and try again.",
  "details": [
    {
      "field": "email",
      "message": "Please enter a valid email address.",
      "type": "value_error.email"
    }
  ]
}
```

## Custom Exception Classes

### Base Exception

**`AppException`** - Base class for all custom exceptions

```python
from productivity_tracker.core.exceptions import AppException

raise AppException(
    message="Technical message for logging",
    user_message="User-friendly message",
    status_code=400,
    error_code="CUSTOM_ERROR",
    context={"key": "value"}  # Additional debugging info
)
```

### Authentication & Authorization

**`InvalidCredentialsError`** - Wrong username/password
- **Status Code**: 401
- **User Message**: "Invalid email or password. Please check your credentials and try again."

```python
raise InvalidCredentialsError(username="john_doe")
```

**`InactiveUserError`** - Account is inactive
- **Status Code**: 403
- **User Message**: "Your account is inactive. Please contact support."

```python
raise InactiveUserError(user_id=str(user.id))
```

**`InvalidTokenError`** - Token is invalid or expired
- **Status Code**: 401
- **User Message**: "Your session is invalid. Please log in again."

```python
raise InvalidTokenError(reason="Token expired")
```

**`PermissionDeniedError`** - Insufficient permissions
- **Status Code**: 403
- **User Message**: "You don't have permission to perform this action."

```python
raise PermissionDeniedError(permission="admin", resource="users")
```

### Resource Exceptions

**`ResourceNotFoundError`** - Resource doesn't exist
- **Status Code**: 404
- **User Message**: "The {resource} you're looking for doesn't exist."

```python
raise ResourceNotFoundError(resource_type="User", resource_id=str(user_id))
```

**`EmailAlreadyExistsError`** - Email already registered
- **Status Code**: 409
- **User Message**: "An account with this email address already exists. Please use a different email or try logging in."

```python
raise EmailAlreadyExistsError(email="user@example.com")
```

**`UsernameAlreadyExistsError`** - Username already taken
- **Status Code**: 409
- **User Message**: "This username is already taken. Please choose a different username."

```python
raise UsernameAlreadyExistsError(username="john_doe")
```

**`ResourceAlreadyExistsError`** - Generic duplicate resource
- **Status Code**: 409
- **User Message**: "A {resource} with this {field} already exists."

```python
raise ResourceAlreadyExistsError(
    resource_type="Role",
    field="name",
    value="admin"
)
```

### Validation Exceptions

**`ValidationError`** - Input validation failed
- **Status Code**: 422
- **User Message**: "The information provided is invalid."

```python
raise ValidationError(
    message="Password too short",
    user_message="Password must be at least 8 characters.",
    field="password"
)
```

**`PasswordMismatchError`** - Current password incorrect
- **Status Code**: 422
- **User Message**: "The current password you entered is incorrect."

```python
raise PasswordMismatchError()
```

### Business Logic Exceptions

**`BusinessLogicError`** - Custom business rule violation
- **Status Code**: 400
- **User Message**: Custom message

```python
raise BusinessLogicError(
    message="Cannot delete user with active sessions",
    user_message="This user has active sessions and cannot be deleted.",
    context={"active_sessions": 5}
)
```

### Database Exceptions

**`DatabaseError`** - Database operation failed
- **Status Code**: 500
- **User Message**: "We're experiencing technical difficulties. Please try again later."

```python
raise DatabaseError(
    message="Connection timeout",
    original_error=exc
)
```

## Usage in Services

When implementing service methods, use custom exceptions instead of HTTPException:

### Before (Don't Do This)
```python
from fastapi import HTTPException, status

def get_user(self, user_id: UUID) -> User:
    user = self.repository.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"  # Technical message
        )
    return user
```

### After (Do This)
```python
from productivity_tracker.core.exceptions import ResourceNotFoundError

def get_user(self, user_id: UUID) -> User:
    user = self.repository.get_by_id(user_id)
    if not user:
        raise ResourceNotFoundError(
            resource_type="User",
            resource_id=str(user_id)
        )  # Returns: "The user you're looking for doesn't exist."
    return user
```

## Exception Handler Order

Exception handlers are registered in order of specificity (most specific first):

1. `AppException` - Custom application exceptions
2. `HTTPException` - FastAPI HTTP exceptions
3. `RequestValidationError` - Pydantic validation errors
4. `SQLAlchemyError` - Database errors
5. `Exception` - Catch-all for unexpected errors

## Logging Best Practices

The error handlers automatically log errors with appropriate levels:

- **ERROR level** (500+ status): Server errors, database issues
- **WARNING level** (400-499 status): Client errors, validation failures
- **INFO level** (< 400 status): Successful operations

Each log entry includes:
- Full technical error message
- Request path and method
- User context (if authenticated)
- Additional context from exception

## Examples

### Authentication Error Flow

```python
# In service layer
def authenticate_user(self, username: str, password: str) -> User | None:
    user = self.repository.get_by_username(username)
    if not user or not verify_password(password, user.hashed_password):
        return None  # Don't expose which part failed
    return user

# In API layer
user = user_service.authenticate_user(form_data.username, form_data.password)
if not user:
    raise InvalidCredentialsError(username=form_data.username)
```

**Response to user:**
```json
{
  "error": "INVALID_CREDENTIALS",
  "message": "Invalid email or password. Please check your credentials and try again."
}
```

**Log entry:**
```
WARNING: Application error on /api/v1/auth/login: [INVALID_CREDENTIALS] Invalid credentials for user: john_doe | Context: {'username': 'john_doe'}
```

### Registration Error Flow

```python
def create_user(self, user_data: UserCreate) -> User:
    existing_user = self.repository.get_by_email(user_data.email)
    if existing_user:
        raise EmailAlreadyExistsError(str(user_data.email))

    # Create user...
    return created_user
```

**Response to user:**
```json
{
  "error": "EMAIL_ALREADY_EXISTS",
  "message": "An account with this email address already exists. Please use a different email or try logging in."
}
```

### Validation Error (Automatic)

When a request has invalid data:

**Request:**
```json
{
  "email": "invalid-email",
  "password": "abc"
}
```

**Response:**
```json
{
  "error": "VALIDATION_ERROR",
  "message": "The information provided is invalid. Please check the fields and try again.",
  "details": [
    {
      "field": "email",
      "message": "Please enter a valid email address.",
      "type": "value_error.email"
    },
    {
      "field": "password",
      "message": "Password is too short.",
      "type": "value_error.any_str.min_length"
    }
  ]
}
```

## Error Code Reference

| Code | Status | Meaning |
|------|--------|---------|
| `INVALID_CREDENTIALS` | 401 | Wrong username/password |
| `INVALID_TOKEN` | 401 | Token invalid or expired |
| `TOKEN_EXPIRED` | 401 | Session expired |
| `INACTIVE_USER` | 403 | Account inactive |
| `PERMISSION_DENIED` | 403 | Insufficient permissions |
| `RESOURCE_NOT_FOUND` | 404 | Resource doesn't exist |
| `EMAIL_ALREADY_EXISTS` | 409 | Email already registered |
| `USERNAME_ALREADY_EXISTS` | 409 | Username already taken |
| `RESOURCE_ALREADY_EXISTS` | 409 | Generic duplicate |
| `VALIDATION_ERROR` | 422 | Input validation failed |
| `PASSWORD_MISMATCH` | 422 | Current password wrong |
| `BUSINESS_LOGIC_ERROR` | 400 | Business rule violation |
| `DATABASE_ERROR` | 500 | Database issue |
| `INTERNAL_SERVER_ERROR` | 500 | Unexpected error |

## Frontend Integration

Frontend developers should:

1. **Check the `error` code** for programmatic handling
2. **Display the `message`** to users directly (it's already user-friendly)
3. **Use HTTP status codes** for general error categorization

### TypeScript Example

```typescript
interface ErrorResponse {
  error: string;
  message: string;
  details?: Array<{
    field: string;
    message: string;
    type: string;
  }>;
  debug_context?: Record<string, any>;
}

async function handleApiCall() {
  try {
    const response = await fetch('/api/v1/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials)
    });

    if (!response.ok) {
      const error: ErrorResponse = await response.json();

      // Show user-friendly message
      showNotification(error.message, 'error');

      // Handle specific errors
      switch (error.error) {
        case 'INVALID_CREDENTIALS':
          highlightFields(['username', 'password']);
          break;
        case 'INACTIVE_USER':
          redirectToContactSupport();
          break;
        case 'VALIDATION_ERROR':
          if (error.details) {
            error.details.forEach(detail => {
              showFieldError(detail.field, detail.message);
            });
          }
          break;
      }
    }
  } catch (err) {
    showNotification('Network error. Please check your connection.', 'error');
  }
}
```

## Testing Error Handling

Test that your services raise appropriate exceptions:

```python
import pytest
from productivity_tracker.core.exceptions import EmailAlreadyExistsError

def test_create_user_duplicate_email(user_service, sample_user_data):
    # Create first user
    user_service.create_user(sample_user_data)

    # Try to create duplicate
    with pytest.raises(EmailAlreadyExistsError) as exc_info:
        user_service.create_user(sample_user_data)

    assert exc_info.value.status_code == 409
    assert "already exists" in exc_info.value.user_message.lower()
```

## Best Practices

1. ✅ **DO** use specific exception classes
2. ✅ **DO** provide context in exception constructors
3. ✅ **DO** log before raising exceptions in services
4. ✅ **DO** keep user messages simple and actionable
5. ❌ **DON'T** expose technical details in user messages
6. ❌ **DON'T** use HTTPException in service layers
7. ❌ **DON'T** log the same error multiple times
8. ❌ **DON'T** include sensitive data in error messages

## Debug Mode

When `DEBUG=True` in settings:
- Error responses include `debug_context` field
- More detailed stack traces in logs
- CORS allows broader origins

**Never enable DEBUG in production!**
