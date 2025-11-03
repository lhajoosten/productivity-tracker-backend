# Redis Session Management

## Overview

The Productivity Tracker Backend implements Redis-based session management for cookie-based authentication. This provides enhanced security and control over user sessions, allowing for features like session invalidation, logout from all devices, and session tracking.

## Architecture

### Components

1. **RedisClient** (`productivity_tracker/core/redis_client.py`)
   - Handles all Redis operations for session management
   - Manages session lifecycle (create, read, delete)
   - Provides user session tracking capabilities

2. **JWT with Session ID** (`productivity_tracker/core/security.py`)
   - Access tokens include a unique `jti` (JWT ID) claim
   - The `jti` serves as the session identifier in Redis

3. **Session Validation** (`productivity_tracker/core/dependencies.py`)
   - All authenticated requests validate the session against Redis
   - Invalid or expired sessions result in authentication failure

4. **Session Endpoints** (`productivity_tracker/api/sessions.py`)
   - `/auth/sessions` - Get active session count
   - `/auth/logout-all` - Invalidate all user sessions

## How It Works

### 1. Login Flow

When a user logs in:

1. User credentials are validated
2. An access token is created with a unique `jti` (session ID)
3. A session is created in Redis with:
   - Key: `session:{jti}`
   - Value: JSON with `user_id` and metadata
   - TTL: Matches `ACCESS_TOKEN_EXPIRE_MINUTES`
4. The access token is set as an HTTP-only cookie

```python
# Example session data in Redis
{
    "user_id": "123e4567-e89b-12d3-a456-426614174000",
    "metadata": {
        "username": "john.doe",
        "login_time": "..."
    }
}
```

### 2. Authentication Flow

On every authenticated request:

1. Access token is extracted from cookie
2. JWT is decoded and validated
3. If `jti` exists, session is validated in Redis
4. If session doesn't exist → Authentication fails
5. If session exists → User is authenticated

### 3. Logout Flow

When a user logs out:

1. The `jti` is extracted from the access token
2. The session is deleted from Redis
3. The cookie is cleared
4. All subsequent requests with that token fail authentication

### 4. Token Refresh Flow

When refreshing an access token:

1. A new access token with a new `jti` is created
2. A new session is created in Redis
3. The old session remains valid until its TTL expires (graceful transition)

## Configuration

### Environment Variables

```bash
# Redis connection
REDIS_URL=redis://localhost:6379/0

# Session TTL (in minutes, used for access tokens)
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Settings

The Redis configuration is optional. If Redis is not available:
- Sessions are not stored
- Authentication still works via JWT validation
- Session-specific features are disabled

## Features

### 1. Session Tracking

Get the number of active sessions for the current user:

```bash
GET /api/v1/auth/sessions
```

Response:
```json
{
    "active_sessions": 3,
    "redis_available": true
}
```

### 2. Logout from All Devices

Invalidate all active sessions for the current user:

```bash
POST /api/v1/auth/logout-all
```

Response:
```json
{
    "message": "Successfully logged out from all sessions",
    "sessions_deleted": 3
}
```

### 3. Session Invalidation

Sessions are automatically invalidated when:
- The access token expires (TTL)
- User logs out
- User logs out from all devices
- Session is manually deleted from Redis

## Security Benefits

1. **Token Revocation**: Unlike pure JWT, tokens can be revoked by deleting the session
2. **Session Control**: Users can see and manage their active sessions
3. **Force Logout**: Admins or users can invalidate all sessions
4. **Stolen Token Mitigation**: Stolen tokens can be invalidated immediately
5. **Audit Trail**: Session metadata can track login times, devices, etc.

## Redis Data Structure

### Session Key Pattern

```
session:{jti}
```

Example:
```
session:550e8400-e29b-41d4-a716-446655440000
```

### Session Value

```json
{
    "user_id": "123e4567-e89b-12d3-a456-426614174000",
    "metadata": {
        "username": "john.doe",
        "login_time": "2025-11-03T10:30:00",
        "ip_address": "192.168.1.1",
        "user_agent": "Mozilla/5.0..."
    }
}
```

## API Endpoints

### Modified Endpoints

#### POST `/api/v1/auth/login`
- Creates a session in Redis
- Returns access token with embedded `jti`

#### POST `/api/v1/auth/logout`
- Deletes the session from Redis
- Clears the cookie

#### POST `/api/v1/auth/refresh`
- Creates a new session with new `jti`
- Old session remains valid until TTL expires

### New Endpoints

#### GET `/api/v1/auth/sessions`
- **Authentication**: Required
- **Returns**: Active session count and Redis availability

#### POST `/api/v1/auth/logout-all`
- **Authentication**: Required
- **Returns**: Number of sessions deleted

## Error Handling

### Session Not Found

If a session doesn't exist in Redis (but JWT is valid):

```json
{
    "detail": {
        "error": "InvalidToken",
        "message": "Session expired or invalid"
    }
}
```

### Redis Unavailable

If Redis is not available:
- Authentication falls back to JWT-only validation
- Session endpoints return appropriate status
- No errors are raised (graceful degradation)

## Monitoring

### Redis Health Check

Check Redis connectivity:

```python
from productivity_tracker.core.redis_client import get_redis_client

redis_client = get_redis_client()
if redis_client.is_connected:
    print("Redis is connected")
else:
    print("Redis is not available")
```

### Session Metrics

Track session metrics:
- Total active sessions per user
- Session creation/deletion rates
- Average session duration

## Docker Setup

Redis is included in `docker-compose.yml`:

```yaml
redis:
  image: redis:7-alpine
  container_name: productivity_redis
  ports:
    - "6379:6379"
  volumes:
    - redis_data:/data
  command: redis-server --appendonly yes
  healthcheck:
    test: ["CMD", "redis-cli", "ping"]
    interval: 10s
    timeout: 5s
    retries: 5
```

## Development vs Production

### Development
- Redis runs in Docker
- Sessions persist across restarts (with AOF)
- Lower security requirements

### Production
- Use managed Redis service (AWS ElastiCache, Redis Cloud, etc.)
- Enable Redis AUTH
- Use TLS for Redis connections
- Set appropriate memory limits
- Configure eviction policies
- Enable Redis persistence (RDB + AOF)

## Best Practices

1. **Session TTL**: Keep it short (15-30 minutes) for security
2. **Refresh Tokens**: Use longer-lived refresh tokens for UX
3. **Session Metadata**: Store minimal data in sessions
4. **Cleanup**: Redis TTL handles automatic cleanup
5. **Monitoring**: Track Redis memory usage and connection pool
6. **Failover**: Implement graceful degradation if Redis is down

## Future Enhancements

- [ ] Store device/browser information in session metadata
- [ ] Add IP address tracking and validation
- [ ] Implement concurrent session limits per user
- [ ] Add session activity timestamps
- [ ] Implement suspicious activity detection
- [ ] Add admin endpoints to view/manage user sessions
- [ ] Support for Redis Cluster for high availability
- [ ] Session fingerprinting for enhanced security

## Testing

### Unit Tests

Test Redis client operations:

```python
def test_create_session():
    redis_client = get_redis_client()
    success = redis_client.create_session(
        session_id="test-jti",
        user_id=UUID("..."),
        ttl_seconds=300
    )
    assert success

def test_session_validation():
    # Create session
    # Validate it exists
    # Delete it
    # Validate it's gone
```

### Integration Tests

Test authentication flow with Redis:

```python
def test_login_creates_session():
    # Login
    # Verify session exists in Redis
    # Verify token contains jti

def test_logout_deletes_session():
    # Login
    # Logout
    # Verify session deleted from Redis
```

## Troubleshooting

### Sessions not persisting

Check Redis connection:
```bash
docker exec -it productivity_redis redis-cli ping
```

### Too many sessions

Check active sessions:
```bash
docker exec -it productivity_redis redis-cli --scan --pattern "session:*" | wc -l
```

### Clear all sessions

```bash
docker exec -it productivity_redis redis-cli FLUSHDB
```

## References

- [JWT Best Practices](https://tools.ietf.org/html/rfc8725)
- [Redis Session Store Pattern](https://redis.io/docs/manual/patterns/distributed-locks/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
