# HTTPS Setup for Docker/Docker Compose

## Overview

This guide covers setting up HTTPS for the Productivity Tracker backend running in Docker. Two approaches are provided:

1. **Nginx Reverse Proxy with SSL** (Recommended) ✅ **Implemented**
2. **Direct Uvicorn with SSL** (Alternative)

## Approach 1: Nginx Reverse Proxy (Recommended)

### Architecture

```
Client (HTTPS:443) → Nginx (SSL Termination) → FastAPI App (HTTP:3456)
```

### Benefits
- ✅ Production-ready setup
- ✅ Better performance with static files
- ✅ Easy to add load balancing
- ✅ Centralized SSL certificate management
- ✅ HTTP to HTTPS redirect
- ✅ Security headers
- ✅ Rate limiting capability
- ✅ WebSocket support

### Files Created/Modified

1. **`nginx/nginx.conf`** - Nginx configuration with SSL
2. **`nginx/Dockerfile`** - Nginx Docker image
3. **`docker-compose.yml`** - Added nginx service
4. **`Dockerfile`** - Updated to work behind proxy

### How It Works

1. Nginx listens on ports 80 (HTTP) and 443 (HTTPS)
2. HTTP requests are redirected to HTTPS
3. HTTPS requests are proxied to the FastAPI app on port 3456
4. SSL certificates are mounted from `./certs` directory
5. App is not exposed directly to the host

### Configuration

#### SSL Certificates Location
```
certs/
  ├── api.localhost.pem          # SSL certificate
  └── api.localhost-key.pem      # Private key
```

#### Nginx Configuration Highlights
```nginx
# SSL on port 443
listen 443 ssl http2;
ssl_certificate /etc/nginx/certs/api.localhost.pem;
ssl_certificate_key /etc/nginx/certs/api.localhost-key.pem;

# Proxy to app
location / {
    proxy_pass http://app:3456;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-Proto $scheme;
    # ... more headers
}
```

### Usage

#### Start Services
```bash
docker-compose up --build
```

#### Access the API
- **HTTPS**: https://api.localhost (port 443)
- **HTTP**: http://api.localhost (redirects to HTTPS)
- **Docs**: https://api.localhost/api/v1/docs

#### Test HTTPS
```bash
# Test HTTPS connection
curl -k https://api.localhost/health

# Test with full SSL verification (if you trust the cert)
curl --cacert certs/api.localhost.pem https://api.localhost/health

# Test redirect from HTTP to HTTPS
curl -I http://api.localhost/health
```

### Logs

#### View Nginx Logs
```bash
# Access logs
docker exec productivity_nginx tail -f /var/log/nginx/api.access.log

# Error logs
docker exec productivity_nginx tail -f /var/log/nginx/api.error.log

# Or use docker logs
docker logs -f productivity_nginx
```

#### View App Logs
```bash
docker logs -f productivity_app
```

### Certificate Management

#### Using Self-Signed Certificates (Development)

If you need to regenerate your certificates:

```bash
# Generate new self-signed certificate
openssl req -x509 -newkey rsa:4096 -nodes \
  -keyout certs/api.localhost-key.pem \
  -out certs/api.localhost.pem \
  -days 365 \
  -subj "/CN=api.localhost"

# Or with more details
openssl req -x509 -newkey rsa:4096 -nodes \
  -keyout certs/api.localhost-key.pem \
  -out certs/api.localhost.pem \
  -days 365 \
  -subj "/C=US/ST=State/L=City/O=Organization/CN=api.localhost" \
  -addext "subjectAltName=DNS:api.localhost,DNS:localhost,DNS:*.localhost"
```

#### Using Let's Encrypt (Production)

For production, use Let's Encrypt with certbot:

```bash
# Install certbot
apt-get update && apt-get install certbot

# Get certificate (requires domain pointing to your server)
certbot certonly --standalone -d yourdomain.com

# Certificates will be in:
# /etc/letsencrypt/live/yourdomain.com/fullchain.pem
# /etc/letsencrypt/live/yourdomain.com/privkey.pem

# Update nginx.conf to point to these
```

#### Trust Self-Signed Certificate (Local Development)

**On macOS:**
```bash
# Add to keychain
sudo security add-trusted-cert -d -r trustRoot -k /Library/Keychains/System.keychain certs/api.localhost.pem
```

**On Windows:**
```powershell
# Import certificate
Import-Certificate -FilePath "certs\api.localhost.pem" -CertStoreLocation Cert:\LocalMachine\Root
```

**On Linux:**
```bash
# Copy to trusted certificates
sudo cp certs/api.localhost.pem /usr/local/share/ca-certificates/api.localhost.crt
sudo update-ca-certificates
```

### Nginx Configuration Options

#### Enable Rate Limiting

Add to `nginx/nginx.conf`:

```nginx
# In http context (before server block)
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;

# In location block
location /api/ {
    limit_req zone=api_limit burst=20 nodelay;
    proxy_pass http://app:3456;
    # ... other settings
}
```

#### Enable CORS Headers

Add to `nginx/nginx.conf` in location block:

```nginx
location / {
    # CORS headers
    add_header Access-Control-Allow-Origin $http_origin always;
    add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS" always;
    add_header Access-Control-Allow-Headers "Authorization, Content-Type" always;
    add_header Access-Control-Allow-Credentials true always;

    if ($request_method = OPTIONS) {
        return 204;
    }

    proxy_pass http://app:3456;
    # ... other settings
}
```

#### Enable Gzip Compression

Add to `nginx/nginx.conf`:

```nginx
# Gzip compression
gzip on;
gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
gzip_min_length 1000;
gzip_comp_level 6;
```

### Ports

| Service | HTTP | HTTPS | Purpose |
|---------|------|-------|---------|
| Nginx | 80 | 443 | Reverse proxy with SSL |
| App | - | - | Internal only (3456) |
| Postgres | 5432 | - | Database |
| Redis | 6379 | - | Cache/Sessions |
| MinIO | 9000 | - | Object storage |
| PgAdmin | 5050 | - | Database admin |

### Troubleshooting

#### Certificate Errors
```bash
# Check certificate details
openssl x509 -in certs/api.localhost.pem -text -noout

# Check certificate and key match
openssl x509 -noout -modulus -in certs/api.localhost.pem | openssl md5
openssl rsa -noout -modulus -in certs/api.localhost-key.pem | openssl md5
# Both should output the same hash
```

#### Nginx Won't Start
```bash
# Test nginx configuration
docker exec productivity_nginx nginx -t

# Check logs
docker logs productivity_nginx

# Common issues:
# - Certificate files not found (check volume mount)
# - Port 80/443 already in use
# - Syntax errors in nginx.conf
```

#### SSL Handshake Errors
```bash
# Test SSL connection
openssl s_client -connect api.localhost:443 -servername api.localhost

# Check cipher compatibility
nmap --script ssl-enum-ciphers -p 443 api.localhost
```

#### Connection Refused
```bash
# Check if nginx is running
docker ps | grep nginx

# Check if app is accessible from nginx
docker exec productivity_nginx curl http://app:3456/health

# Check network connectivity
docker exec productivity_nginx ping app
```

---

## Approach 2: Direct Uvicorn with SSL (Alternative)

### When to Use
- Simple development setup
- No need for reverse proxy features
- Testing SSL directly with Python

### Configuration

Create `docker-compose.ssl.yml`:

```yaml
version: '3.8'

services:
  app:
    build:
      context: ..
      dockerfile: Dockerfile
    container_name: productivity_app
    volumes:
      - ./productivity_tracker:/app/productivity_tracker:cached
      - ./migrations:/app/migrations:cached
      - ./certs:/app/certs:ro  # Mount certificates
    ports:
      - "443:3456"  # Expose HTTPS port
    command: >
      uvicorn productivity_tracker.main:app
      --host 0.0.0.0
      --port 3456
      --ssl-keyfile /app/certs/api.localhost-key.pem
      --ssl-certfile /app/certs/api.localhost.pem
      --reload
    # ... rest of config same as docker-compose.yml
```

### Usage

```bash
# Start with direct SSL
docker-compose -f docker-compose.ssl.yml up --build

# Access at
curl -k https://localhost:443/health
```

### Limitations
- ❌ No automatic HTTP to HTTPS redirect
- ❌ No reverse proxy benefits
- ❌ Harder to add load balancing
- ❌ No centralized SSL management
- ✅ Simpler setup
- ✅ Good for development/testing

---

## Production Deployment

### Using Cloud Providers

#### AWS (with ALB/ELB)
- Use Application Load Balancer for SSL termination
- Store certificates in AWS Certificate Manager
- Point ALB to ECS/EKS containers

#### Google Cloud (with Load Balancer)
- Use Google Cloud Load Balancer for SSL
- Manage certificates with Google-managed certificates
- Deploy to Cloud Run or GKE

#### Azure (with Application Gateway)
- Use Application Gateway for SSL termination
- Store certificates in Key Vault
- Deploy to Container Instances or AKS

### Using Traefik (Alternative to Nginx)

```yaml
# docker-compose.traefik.yml
services:
  traefik:
    image: traefik:v2.10
    command:
      - "--providers.docker=true"
      - "--entrypoints.web.address=:80"
      - "--entrypoints.websecure.address=:443"
      - "--certificatesresolvers.le.acme.email=your-email@example.com"
      - "--certificatesresolvers.le.acme.storage=/letsencrypt/acme.json"
      - "--certificatesresolvers.le.acme.httpchallenge.entrypoint=web"
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - traefik-certificates:/letsencrypt
    networks:
      - productivity-network

  app:
    # ... your app config
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.app.rule=Host(`api.yourdomain.com`)"
      - "traefik.http.routers.app.entrypoints=websecure"
      - "traefik.http.routers.app.tls.certresolver=le"
```

### Security Best Practices

1. **Use Strong SSL Configuration**
   - TLS 1.2+ only
   - Strong cipher suites
   - HSTS headers

2. **Certificate Management**
   - Rotate certificates regularly
   - Use Let's Encrypt for auto-renewal
   - Store private keys securely

3. **Monitoring**
   - Monitor certificate expiration
   - Log SSL handshake failures
   - Track SSL/TLS versions used

4. **Rate Limiting**
   - Implement at nginx level
   - Protect against DDoS
   - API throttling

5. **Security Headers**
   - HSTS
   - X-Frame-Options
   - X-Content-Type-Options
   - CSP headers

---

## Summary

✅ **Implemented**: Nginx reverse proxy with SSL termination
✅ **Certificates**: Mounted from `./certs` directory
✅ **HTTP Redirect**: Automatic redirect to HTTPS
✅ **Security Headers**: Added security headers
✅ **Logging**: Nginx access and error logs
✅ **Production Ready**: Scalable architecture

### Quick Start

```bash
# Start with HTTPS
docker-compose up --build

# Access API
curl -k https://api.localhost/api/v1/docs

# View logs
docker logs -f productivity_nginx
docker logs -f productivity_app
```

### Next Steps

1. **Trust the certificate** on your local machine (see above)
2. **Update your frontend** to use `https://api.localhost` instead of `http://`
3. **Configure CORS** if needed for your frontend domain
4. **Add rate limiting** for production
5. **Set up certificate auto-renewal** for production with Let's Encrypt
