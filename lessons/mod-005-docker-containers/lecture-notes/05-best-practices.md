# Lecture 05: Docker Best Practices and Production Readiness

## Learning Objectives

By the end of this lecture, you will be able to:

- Apply Dockerfile best practices for efficiency and security
- Optimize Docker images for size and performance
- Implement security hardening measures
- Configure containers for production environments
- Set up health checks and monitoring
- Manage secrets securely
- Apply the Twelve-Factor App principles
- Troubleshoot common production issues

**Duration**: 90-120 minutes
**Difficulty**: Intermediate to Advanced
**Prerequisites**: Lectures 01-04 (All previous Docker lectures)

---

## 1. Dockerfile Best Practices

### Use Specific Base Image Tags

```dockerfile
# ❌ Bad: Unpredictable
FROM python:latest

# ✅ Good: Specific version
FROM python:3.11.6-slim

# ✅ Even better: With digest
FROM python:3.11.6-slim@sha256:abc123...
```

**Why?**
- `latest` changes over time → builds not reproducible
- Specific versions ensure consistency
- Digests guarantee exact image

### Minimize Layer Count

```dockerfile
# ❌ Bad: Many layers
FROM ubuntu:22.04
RUN apt-get update
RUN apt-get install -y python3
RUN apt-get install -y python3-pip
RUN apt-get install -y curl
RUN apt-get clean

# ✅ Good: Combined into one layer
FROM ubuntu:22.04
RUN apt-get update && \
    apt-get install -y \
        python3 \
        python3-pip \
        curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
```

### Optimize Layer Caching

```dockerfile
# ❌ Bad: Cache invalidated frequently
FROM python:3.11-slim
COPY . /app                          # Changes often
RUN pip install -r /app/requirements.txt

# ✅ Good: Dependencies cached
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .              # Copy deps first
RUN pip install --no-cache-dir -r requirements.txt
COPY . .                             # Copy code last
```

### Use Multi-Stage Builds

```dockerfile
# Build stage
FROM python:3.11 AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.11-slim
WORKDIR /app

# Copy only installed packages
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

COPY . .
CMD ["python", "app.py"]

# Result: Much smaller image!
```

### Use .dockerignore

```
# .dockerignore
**/__pycache__
**/*.pyc
**/*.pyo
**/*.pyd
.Python
env/
venv/
.git/
.gitignore
.dockerignore
.env
.vscode/
.idea/
*.md
LICENSE
.pytest_cache/
.coverage
htmlcov/
dist/
build/
*.egg-info/
node_modules/
*.log
```

### Run as Non-Root User

```dockerfile
# ❌ Bad: Runs as root (security risk)
FROM python:3.11-slim
COPY . /app
CMD ["python", "app.py"]

# ✅ Good: Non-root user
FROM python:3.11-slim

# Create user
RUN groupadd -r appuser && \
    useradd -r -g appuser appuser

WORKDIR /app
COPY --chown=appuser:appuser . .

# Switch to non-root user
USER appuser

CMD ["python", "app.py"]
```

### Add Health Checks

```dockerfile
FROM nginx:alpine

COPY nginx.conf /etc/nginx/nginx.conf
COPY html /usr/share/nginx/html

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost/health || exit 1

EXPOSE 80
```

---

## 2. Image Optimization

### Choosing the Right Base Image

```dockerfile
# Full image: 1.2 GB
FROM python:3.11

# Slim image: 200 MB (recommended)
FROM python:3.11-slim

# Alpine image: 50 MB (smallest)
FROM python:3.11-alpine
```

**Trade-offs**:
```
Full (python:3.11)
├─ Pros: Everything included, compatible
└─ Cons: Very large (1.2GB)

Slim (python:3.11-slim)
├─ Pros: Good balance, most packages work
└─ Cons: Some dev tools missing

Alpine (python:3.11-alpine)
├─ Pros: Smallest size (50MB)
└─ Cons: Different libc (musl), compatibility issues
```

### Remove Build Dependencies

```dockerfile
FROM python:3.11-slim

# Install build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        gcc && \
    # Install Python packages
    pip install --no-cache-dir numpy pandas && \
    # Remove build dependencies
    apt-get purge -y --auto-remove \
        build-essential \
        gcc && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
```

### Minimize Installed Packages

```dockerfile
# ❌ Bad: Installs recommended packages
RUN apt-get install -y curl

# ✅ Good: Only essential packages
RUN apt-get install -y --no-install-recommends curl
```

### Clean Up in Same Layer

```dockerfile
# ❌ Bad: Files in separate layers still count
RUN apt-get update
RUN apt-get install -y package
RUN apt-get clean  # Doesn't reduce previous layers!

# ✅ Good: Clean up in same RUN
RUN apt-get update && \
    apt-get install -y package && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
```

### Use pip Flags

```dockerfile
# ❌ Bad: Downloads cache, huge layers
RUN pip install flask

# ✅ Good: No cache
RUN pip install --no-cache-dir flask

# ✅ Even better: No compile
RUN pip install --no-cache-dir --no-compile flask
```

---

## 3. Security Best Practices

### Scan Images for Vulnerabilities

```bash
# Use Docker Scout (built-in)
docker scout cve myimage:latest

# Use Trivy
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
    aquasec/trivy image myimage:latest

# Use Snyk
snyk container test myimage:latest
```

### Don't Include Secrets

```dockerfile
# ❌ BAD: Secret in image
ENV API_KEY=sk_live_abc123...

# ❌ BAD: Secret in layer
COPY .env /app/.env

# ✅ Good: Use build secrets (BuildKit)
RUN --mount=type=secret,id=api_key \
    API_KEY=$(cat /run/secrets/api_key) python build.py
```

**Pass secrets at runtime**:
```bash
# Environment variable
docker run -e API_KEY=$API_KEY myapp

# Docker secret (Swarm)
docker secret create api_key api_key.txt
docker service create --secret api_key myapp

# Volume mount
docker run -v $(pwd)/.env:/app/.env:ro myapp
```

### Use Read-Only Filesystem

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .

# Make filesystem read-only
# Writable tmpfs for /tmp
CMD ["python", "app.py"]
```

```bash
docker run --read-only --tmpfs /tmp myapp
```

### Limit Container Capabilities

```bash
# Drop all capabilities
docker run --cap-drop ALL myapp

# Add only required capabilities
docker run --cap-drop ALL --cap-add NET_BIND_SERVICE myapp
```

### Use Security Options

```dockerfile
# Dockerfile
FROM python:3.11-slim
RUN apt-get update && apt-get install -y --no-install-recommends apparmor

# Add security labels
LABEL security.apparmor="docker-default"
```

```bash
# Run with security options
docker run \
    --security-opt=no-new-privileges:true \
    --security-opt apparmor=docker-default \
    myapp
```

---

## 4. Production Configuration

### Resource Limits

```yaml
# docker-compose.yml
services:
  web:
    image: myapp
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 512M
        reservations:
          cpus: '0.5'
          memory: 256M
```

```bash
# Docker run
docker run -d \
    --cpus="1.0" \
    --memory="512m" \
    --memory-reservation="256m" \
    myapp
```

### Restart Policies

```yaml
services:
  web:
    image: myapp
    restart: unless-stopped
    # Options:
    # - no: Never restart
    # - always: Always restart
    # - on-failure: Restart on non-zero exit
    # - unless-stopped: Restart unless manually stopped
```

### Health Checks

```yaml
services:
  web:
    image: myapp
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

**Health check script**:
```python
# health.py
from flask import Flask, jsonify
import psutil

app = Flask(__name__)

@app.route('/health')
def health():
    # Check dependencies
    try:
        # Database check
        db.ping()

        # Memory check
        memory = psutil.virtual_memory()
        if memory.percent > 90:
            return jsonify({"status": "unhealthy", "reason": "high memory"}), 503

        return jsonify({"status": "healthy"}), 200
    except Exception as e:
        return jsonify({"status": "unhealthy", "reason": str(e)}), 503
```

### Logging Configuration

```dockerfile
FROM python:3.11-slim

# Log to stdout/stderr (Docker best practice)
ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY . .

CMD ["python", "app.py"]
```

```python
# app.py
import logging
import sys

# Configure logging to stdout
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)

logger = logging.getLogger(__name__)
logger.info("Application started")
```

```bash
# View logs
docker logs -f myapp

# With timestamps
docker logs -f --timestamps myapp

# JSON logging driver
docker run --log-driver=json-file --log-opt max-size=10m --log-opt max-file=3 myapp
```

---

## 5. Twelve-Factor App Principles

### I. Codebase

```bash
# One codebase, many deployments
git clone repo
docker build -t myapp:dev .
docker build -t myapp:staging .
docker build -t myapp:prod .
```

### II. Dependencies

```dockerfile
# Explicitly declare dependencies
FROM python:3.11-slim
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
```

### III. Config

```yaml
# Store config in environment
services:
  web:
    image: myapp
    environment:
      DATABASE_URL: ${DATABASE_URL}
      SECRET_KEY: ${SECRET_KEY}
      DEBUG: ${DEBUG}
```

### IV. Backing Services

```yaml
# Treat backing services as attached resources
services:
  web:
    environment:
      DATABASE_URL: postgresql://db:5432/mydb
      REDIS_URL: redis://redis:6379
      S3_BUCKET: ${S3_BUCKET}
```

### V. Build, Release, Run

```bash
# Build
docker build -t myapp:$(git rev-parse --short HEAD) .

# Release
docker tag myapp:abc123 myapp:1.0.0
docker push myapp:1.0.0

# Run
docker run myapp:1.0.0
```

### VI. Processes

```dockerfile
# Stateless processes
FROM python:3.11-slim
# Don't store session data in container
# Use Redis/database instead
```

### VII. Port Binding

```dockerfile
# Export services via port binding
EXPOSE 8000
CMD ["python", "app.py"]  # Binds to 0.0.0.0:8000
```

### VIII. Concurrency

```yaml
# Scale via process model
services:
  web:
    image: myapp
    deploy:
      replicas: 5  # Horizontal scaling
```

### IX. Disposability

```python
# Fast startup and graceful shutdown
import signal
import sys

def signal_handler(sig, frame):
    print('Graceful shutdown...')
    # Clean up resources
    db.close()
    sys.exit(0)

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)
```

### X. Dev/Prod Parity

```yaml
# Same containers in dev and production
services:
  web:
    image: myapp:${VERSION}  # Same image
    environment:
      ENV: ${ENVIRONMENT}     # Different config
```

### XI. Logs

```python
# Treat logs as event streams
import logging
logging.basicConfig(stream=sys.stdout)  # To stdout
```

### XII. Admin Processes

```bash
# Run admin tasks as one-off processes
docker run --rm myapp python manage.py migrate
docker run --rm myapp python manage.py createsuperuser
```

---

## 6. Monitoring and Observability

### Container Metrics

```bash
# View resource usage
docker stats

# Specific container
docker stats myapp

# Export metrics
docker run -d -p 9323:9323 \
    -v /var/run/docker.sock:/var/run/docker.sock \
    google/cadvisor:latest
```

### Application Metrics

```python
# app.py - Expose Prometheus metrics
from flask import Flask
from prometheus_client import Counter, Histogram, generate_latest

app = Flask(__name__)

request_count = Counter('http_requests_total', 'Total HTTP requests')
request_duration = Histogram('http_request_duration_seconds', 'HTTP request duration')

@app.route('/metrics')
def metrics():
    return generate_latest()

@app.route('/')
@request_duration.time()
def index():
    request_count.inc()
    return "Hello!"
```

### Structured Logging

```python
import json
import logging

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            'timestamp': self.formatTime(record),
            'level': record.levelname,
            'message': record.getMessage(),
            'logger': record.name,
            'path': record.pathname,
            'line': record.lineno
        }
        return json.dumps(log_data)

handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())
logger = logging.getLogger()
logger.addHandler(handler)
logger.setLevel(logging.INFO)

logger.info("Application started", extra={'version': '1.0.0'})
```

---

## 7. CI/CD Best Practices

### Build Pipeline

```yaml
# .github/workflows/docker.yml
name: Docker Build

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2

      - name: Build and push
        uses: docker/build-push-action@v4
        with:
          context: .
          push: true
          tags: |
            myapp:latest
            myapp:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

### Multi-Platform Builds

```bash
# Build for multiple architectures
docker buildx build \
    --platform linux/amd64,linux/arm64 \
    -t myapp:latest \
    --push \
    .
```

### Image Signing

```bash
# Sign image with Docker Content Trust
export DOCKER_CONTENT_TRUST=1
docker push myapp:latest

# Verify signature
docker pull myapp:latest  # Fails if not signed
```

---

## 8. Common Production Issues

### Issue 1: Container Keeps Restarting

**Diagnosis**:
```bash
# Check logs
docker logs myapp

# Check exit code
docker inspect myapp | grep ExitCode

# Check events
docker events --filter container=myapp
```

**Common causes**:
- Application crashes
- Missing environment variables
- Health check failures
- Resource limits

### Issue 2: High Memory Usage

**Diagnosis**:
```bash
# Check memory usage
docker stats myapp

# Inspect container
docker exec myapp ps aux --sort=-%mem | head
```

**Solutions**:
```yaml
services:
  web:
    deploy:
      resources:
        limits:
          memory: 1G
    environment:
      # For Java apps
      JAVA_OPTS: "-Xmx512m"
      # For Node apps
      NODE_OPTIONS: "--max-old-space-size=512"
```

### Issue 3: Slow Image Builds

**Solutions**:
```dockerfile
# Use BuildKit
# DOCKER_BUILDKIT=1 docker build .

# Cache dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .

# Use build cache
docker build --cache-from myapp:latest .

# Parallel builds
RUN apt-get update && apt-get install -y \
    package1 package2 package3
```

### Issue 4: Network Connectivity

**Diagnosis**:
```bash
# Test connectivity
docker exec myapp ping google.com

# Check DNS
docker exec myapp nslookup db

# Inspect network
docker network inspect myapp_network
```

---

## 9. Production Checklist

### Pre-Deployment

- [ ] Image uses specific version tags, not `:latest`
- [ ] Multi-stage build to minimize size
- [ ] Runs as non-root user
- [ ] Security scan completed (no critical vulnerabilities)
- [ ] Health check implemented
- [ ] Resource limits configured
- [ ] Logging to stdout/stderr
- [ ] Secrets passed via environment or volumes
- [ ] .dockerignore file configured
- [ ] Documentation updated

### Dockerfile Review

- [ ] Uses official or verified base images
- [ ] Minimal number of layers
- [ ] Dependencies installed first (caching)
- [ ] Cleanup in same RUN command
- [ ] No secrets in image
- [ ] Labels for metadata
- [ ] EXPOSE for documentation
- [ ] CMD or ENTRYPOINT defined

### Compose File Review

- [ ] Version specified
- [ ] Health checks defined
- [ ] Restart policies configured
- [ ] Resource limits set
- [ ] Volumes for persistent data
- [ ] Networks properly segmented
- [ ] Environment variables documented
- [ ] Dependencies correctly specified

### Runtime Configuration

- [ ] Monitoring configured
- [ ] Log aggregation set up
- [ ] Backup strategy for volumes
- [ ] Rollback procedure documented
- [ ] Scaling strategy defined
- [ ] Update procedure documented

---

## Key Takeaways

✅ **Use specific image tags** for reproducibility
✅ **Multi-stage builds** reduce image size
✅ **Run as non-root user** for security
✅ **Add health checks** for reliability
✅ **Log to stdout** for container best practices
✅ **Set resource limits** to prevent resource exhaustion
✅ **Scan images** for vulnerabilities
✅ **Use .dockerignore** to minimize build context
✅ **Follow 12-factor principles** for cloud-native apps
✅ **Implement graceful shutdown** for zero-downtime deployments

---

## Quick Reference

### Dockerfile Template (Production-Ready)

```dockerfile
# Use specific version
FROM python:3.11.6-slim

# Metadata
LABEL maintainer="team@example.com" \
      version="1.0.0" \
      description="Production app"

# Create non-root user
RUN groupadd -r appuser && \
    useradd -r -g appuser appuser

# Install dependencies
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY --chown=appuser:appuser . .

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=3s \
    CMD python health_check.py || exit 1

# Expose port
EXPOSE 8000

# Run application
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "app:app"]
```

### Compose Template (Production-Ready)

```yaml
version: '3.8'

services:
  web:
    image: myapp:1.0.0
    restart: unless-stopped
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: ${DATABASE_URL}
    env_file:
      - .env
    volumes:
      - app-data:/app/data
    networks:
      - frontend
      - backend
    depends_on:
      db:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 3s
      retries: 3
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 512M
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  db:
    image: postgres:15
    restart: unless-stopped
    environment:
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - db-data:/var/lib/postgresql/data
    networks:
      - backend
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  app-data:
  db-data:

networks:
  frontend:
  backend:
    internal: true
```

---

## Congratulations!

You've completed the Docker lecture series! You now have the knowledge to:

- ✅ Build efficient Docker images
- ✅ Create multi-container applications
- ✅ Configure networking and storage
- ✅ Apply production best practices
- ✅ Secure your containers
- ✅ Monitor and troubleshoot

### Next Steps

1. **Practice**: Build real applications
2. **Exercises**: Complete module hands-on exercises
3. **Projects**: Containerize your own applications
4. **Advanced**: Learn Kubernetes for orchestration

---

**Lecture Version**: 1.0
**Last Updated**: October 2025
**Estimated Time**: 90-120 minutes
**Difficulty**: Intermediate to Advanced
