# Redis Session Management - Quick Start

## What Was Implemented

Redis-based session management has been integrated with cookie-based authentication to provide:

1. **Session Storage**: All login sessions are stored in Redis with automatic expiration
2. **Session Validation**: Every authenticated request validates against Redis
3. **Session Control**: Users can view and manage their active sessions
4. **Immediate Revocation**: Logout invalidates sessions instantly

## Files Modified/Created

### New Files
- `productivity_tracker/core/redis_client.py` - Redis client for session operations
- `productivity_tracker/api/sessions.py` - Session management endpoints
- `docs/REDIS_SESSION_MANAGEMENT.md` - Complete documentation

### Modified Files
- `productivity_tracker/core/security.py` - Added JTI to access tokens
- `productivity_tracker/core/dependencies.py` - Added Redis session validation
- `productivity_tracker/api/auth.py` - Integrated Redis with login/logout/refresh
- `productivity_tracker/api/setup.py` - Added sessions router
- `productivity_tracker/main.py` - Added Redis lifecycle management

## Quick Test

### 1. Start the application

```bash
docker-compose up --build
```

### 2. Test Login (Creates Redis Session)

```bash
curl -X POST http://localhost:3456/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "your_username", "password": "your_password"}' \
  -c cookies.txt
```

### 3. Check Session Info

```bash
curl -X GET http://localhost:3456/api/v1/auth/sessions \
  -b cookies.txt
```

Expected response:
```json
{
  "active_sessions": 1,
  "redis_available": true
}
```

### 4. Verify Session in Redis

```bash
docker exec -it productivity_redis redis-cli
> KEYS session:*
> GET session:{jti-from-above}
```

### 5. Test Logout (Deletes Redis Session)

```bash
curl -X POST http://localhost:3456/api/v1/auth/logout \
  -b cookies.txt
```

### 6. Verify Session Deleted

```bash
docker exec -it productivity_redis redis-cli
> KEYS session:*
```

Should show no sessions for that user.

### 7. Test Logout from All Devices

Login multiple times (different browsers/devices), then:

```bash
curl -X POST http://localhost:3456/api/v1/auth/logout-all \
  -b cookies.txt
```

Expected response:
```json
{
  "message": "Successfully logged out from all sessions",
  "sessions_deleted": 3
}
```

## Endpoints Added

### GET `/api/v1/auth/sessions`
- **Auth Required**: Yes
- **Returns**: Active session count and Redis status

### POST `/api/v1/auth/logout-all`
- **Auth Required**: Yes
- **Returns**: Number of sessions deleted

## Configuration

Add to your `.env` file (already in docker-compose):

```bash
REDIS_URL=redis://redis:6379/0
```

## Architecture Flow

### Login
1. User credentials validated ✓
2. JWT created with unique `jti` ✓
3. Session stored in Redis: `session:{jti}` → `{user_id, metadata}` ✓
4. Cookie set with JWT ✓

### Every Request
1. Cookie JWT extracted ✓
2. JWT decoded and validated ✓
3. Session checked in Redis using `jti` ✓
4. If session exists → Authenticated ✓
5. If session missing → 401 Unauthorized ✓

### Logout
1. Extract `jti` from JWT ✓
2. Delete `session:{jti}` from Redis ✓
3. Clear cookie ✓

### Refresh Token
1. Validate refresh token ✓
2. Generate new JWT with new `jti` ✓
3. Create new session in Redis ✓
4. Set new cookie ✓

## Benefits

✅ **Instant Revocation**: Logout immediately invalidates all tokens
✅ **Multi-Device Control**: See and manage sessions across devices
✅ **Security**: Stolen tokens can be revoked
✅ **Audit Trail**: Track session metadata (login time, IP, etc.)
✅ **Graceful Degradation**: Falls back to JWT-only if Redis unavailable

## Next Steps

1. **Add session metadata**: Store IP address, user agent, login time
2. **Session limits**: Limit concurrent sessions per user
3. **Admin controls**: Let admins view/manage user sessions
4. **Activity tracking**: Track last activity time, extend sessions
5. **Security alerts**: Detect suspicious login patterns

## Monitoring

Check Redis status:
```bash
docker exec -it productivity_redis redis-cli INFO
```

Count active sessions:
```bash
docker exec -it productivity_redis redis-cli --scan --pattern "session:*" | wc -l
```

View all session keys:
```bash
docker exec -it productivity_redis redis-cli KEYS "session:*"
```

## Troubleshooting

**Q: Sessions not being created?**
A: Check Redis connection in logs. Ensure REDIS_URL is set correctly.

**Q: Authentication still works without Redis?**
A: Yes! The system gracefully degrades to JWT-only validation.

**Q: How to clear all sessions?**
A:
```bash
docker exec -it productivity_redis redis-cli FLUSHDB
```

**Q: Sessions disappearing?**
A: Check TTL matches ACCESS_TOKEN_EXPIRE_MINUTES. Sessions auto-expire.

## Testing Commands

```bash
# Check Redis is running
docker ps | grep redis

# View Redis logs
docker logs productivity_redis

# Monitor Redis operations
docker exec -it productivity_redis redis-cli MONITOR

# Check memory usage
docker exec -it productivity_redis redis-cli INFO memory
```
