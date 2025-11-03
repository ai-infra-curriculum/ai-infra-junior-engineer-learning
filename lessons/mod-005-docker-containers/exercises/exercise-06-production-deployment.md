# Exercise 06: Production Deployment Strategies

## Exercise Overview

**Objective**: Master production-ready Docker deployment patterns including security hardening, resource management, monitoring, logging, high availability, and CI/CD integration.

**Difficulty**: Advanced
**Estimated Time**: 4-5 hours
**Prerequisites**:
- Exercise 01-05 (All previous Docker exercises)
- All Docker lectures

## Learning Objectives

By completing this exercise, you will:
- Implement production security best practices (non-root users, read-only filesystems)
- Configure resource limits and quotas for CPU and memory
- Design health checks and monitoring strategies for containerized applications
- Establish logging architectures with centralized log aggregation
- Build high availability patterns with container orchestration
- Deploy using blue-green and canary deployment strategies
- Integrate Docker workflows into CI/CD pipelines
- Manage secrets securely using Docker secrets and environment variables
- Execute multi-stage deployments across environments (dev, staging, prod)
- Implement rollback strategies and disaster recovery procedures

---

## Part 1: Security Hardening

### Step 1.1: Non-Root User Pattern

```dockerfile
# Create production-secure Dockerfile
mkdir -p ~/docker-exercises/production
cd ~/docker-exercises/production

cat > Dockerfile.secure << 'EOF'
FROM python:3.11-slim

# Create non-root user
RUN groupadd -r appuser && \
    useradd -r -g appuser -u 1000 -m -s /bin/bash appuser

# Set working directory
WORKDIR /app

# Install dependencies as root
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files with correct ownership
COPY --chown=appuser:appuser . .

# Switch to non-root user
USER appuser

# Run application
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app"]
EOF
```

### Step 1.2: Minimal Attack Surface

```dockerfile
cat > Dockerfile.minimal << 'EOF'
# Multi-stage build
FROM python:3.11 AS builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Minimal runtime
FROM python:3.11-slim

# Install only runtime dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser -u 1000 appuser

WORKDIR /app

# Copy only necessary files
COPY --from=builder /root/.local /home/appuser/.local
COPY --chown=appuser:appuser app.py .

USER appuser

ENV PATH=/home/appuser/.local/bin:$PATH

CMD ["python", "app.py"]
EOF
```

### Step 1.3: Security Scanning

```bash
# Create simple app for testing
cat > app.py << 'EOF'
from flask import Flask
app = Flask(__name__)

@app.route('/health')
def health():
    return {'status': 'healthy'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
EOF

cat > requirements.txt << 'EOF'
flask==3.0.0
gunicorn==21.2.0
EOF

# Build image
docker build -f Dockerfile.secure -t myapp:secure .

# Scan for vulnerabilities (using Docker Scout or Trivy)
# docker scout cves myapp:secure

# Or use Trivy
# docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
#   aquasec/trivy image myapp:secure
```

### Step 1.4: Read-Only Root Filesystem

```yaml
cat > docker-compose-readonly.yml << 'EOF'
version: '3.8'

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile.secure
    read_only: true  # Root filesystem is read-only
    tmpfs:
      - /tmp  # Writable temporary directory
      - /var/run
    volumes:
      - app-data:/app/data  # Writable data directory
    security_opt:
      - no-new-privileges:true  # Prevent privilege escalation
    cap_drop:
      - ALL  # Drop all capabilities
    cap_add:
      - NET_BIND_SERVICE  # Only add necessary capabilities

volumes:
  app-data:
EOF
```

✅ **Checkpoint**: You can implement security hardening for containers.

---

## Part 2: Resource Management

### Step 2.1: CPU and Memory Limits

```yaml
cat > docker-compose-resources.yml << 'EOF'
version: '3.8'

services:
  web:
    image: nginx
    deploy:
      resources:
        limits:
          cpus: '0.5'  # Max 50% of one CPU
          memory: 512M  # Max 512MB RAM
        reservations:
          cpus: '0.25'  # Guaranteed 25% CPU
          memory: 256M  # Guaranteed 256MB RAM
    restart: always

  api:
    build: .
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
      replicas: 3

  db:
    image: postgres:15
    environment:
      - POSTGRES_PASSWORD=secret
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '1.0'
          memory: 1G
    volumes:
      - db-data:/var/lib/postgresql/data

volumes:
  db-data:
EOF
```

### Step 2.2: Testing Resource Limits

```bash
# Start with resource limits
docker compose -f docker-compose-resources.yml up -d

# Monitor resource usage
docker stats

# Test memory limit
docker run -d \
  --name memory-test \
  --memory="100m" \
  --memory-swap="100m" \
  progrium/stress \
  --vm 1 --vm-bytes 150M

# Container should be killed (OOM)
docker logs memory-test
docker ps -a | grep memory-test

# Test CPU limit
docker run -d \
  --name cpu-test \
  --cpus="0.5" \
  progrium/stress \
  --cpu 2

# Check CPU usage (should not exceed 50%)
docker stats cpu-test

# Cleanup
docker rm -f memory-test cpu-test
docker compose -f docker-compose-resources.yml down
```

### Step 2.3: Disk I/O Limits

```bash
# Limit disk I/O
docker run -d \
  --name io-test \
  --device-read-bps /dev/sda:1mb \
  --device-write-bps /dev/sda:1mb \
  alpine sh -c "while true; do dd if=/dev/zero of=/tmp/test bs=1M count=10; done"

# Monitor I/O
docker stats io-test

# Cleanup
docker rm -f io-test
```

✅ **Checkpoint**: You can configure and enforce resource limits.

---

## Part 3: Health Checks and Monitoring

### Step 3.1: Comprehensive Health Checks

```dockerfile
cat > Dockerfile.health << 'EOF'
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install requests  # For health check

COPY app.py health_check.py ./

# Comprehensive health check
HEALTHCHECK --interval=30s \
            --timeout=10s \
            --start-period=40s \
            --retries=3 \
  CMD python health_check.py || exit 1

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "app:app"]
EOF

cat > health_check.py << 'EOF'
#!/usr/bin/env python3
import sys
import requests
import psutil

def check_app_health():
    """Check if application is responding"""
    try:
        r = requests.get('http://localhost:8000/health', timeout=5)
        return r.status_code == 200
    except:
        return False

def check_system_health():
    """Check system resources"""
    # Check CPU usage
    cpu = psutil.cpu_percent(interval=1)
    if cpu > 90:
        print(f"High CPU usage: {cpu}%")
        return False

    # Check memory usage
    memory = psutil.virtual_memory()
    if memory.percent > 90:
        print(f"High memory usage: {memory.percent}%")
        return False

    # Check disk usage
    disk = psutil.disk_usage('/')
    if disk.percent > 90:
        print(f"High disk usage: {disk.percent}%")
        return False

    return True

if __name__ == '__main__':
    app_healthy = check_app_health()
    system_healthy = check_system_health()

    if app_healthy and system_healthy:
        print("Health check passed")
        sys.exit(0)
    else:
        print("Health check failed")
        sys.exit(1)
EOF
```

### Step 3.2: Docker Compose Health Checks

```yaml
cat > docker-compose-health.yml << 'EOF'
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      - POSTGRES_PASSWORD=secret
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 10s
    volumes:
      - db-data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5

  api:
    build:
      context: .
      dockerfile: Dockerfile.health
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "python", "health_check.py"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    restart: on-failure:3

volumes:
  db-data:
EOF
```

### Step 3.3: Monitoring with Prometheus

```yaml
cat > docker-compose-monitoring.yml << 'EOF'
version: '3.8'

services:
  # Application with metrics endpoint
  app:
    build: .
    ports:
      - "8000:8000"
    labels:
      prometheus.scrape: "true"
      prometheus.port: "8000"
      prometheus.path: "/metrics"

  # Prometheus
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/usr/share/prometheus/console_libraries'
      - '--web.console.templates=/usr/share/prometheus/consoles'

  # Grafana
  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    volumes:
      - grafana-data:/var/lib/grafana
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
      - GF_USERS_ALLOW_SIGN_UP=false
    depends_on:
      - prometheus

  # Node exporter for system metrics
  node-exporter:
    image: prom/node-exporter:latest
    ports:
      - "9100:9100"
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
    command:
      - '--path.procfs=/host/proc'
      - '--path.sysfs=/host/sys'
      - '--collector.filesystem.mount-points-exclude=^/(sys|proc|dev|host|etc)($$|/)'

volumes:
  prometheus-data:
  grafana-data:
EOF

cat > prometheus.yml << 'EOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'app'
    static_configs:
      - targets: ['app:8000']

  - job_name: 'node'
    static_configs:
      - targets: ['node-exporter:9100']
EOF
```

✅ **Checkpoint**: You can implement health checks and monitoring.

---

## Part 4: Logging Strategies

### Step 4.1: Centralized Logging

```yaml
cat > docker-compose-logging.yml << 'EOF'
version: '3.8'

services:
  # Application
  app:
    build: .
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
        labels: "app,environment"
    labels:
      app: "myapp"
      environment: "production"

  # Elasticsearch
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.10.0
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
    volumes:
      - es-data:/usr/share/elasticsearch/data
    ports:
      - "9200:9200"

  # Logstash
  logstash:
    image: docker.elastic.co/logstash/logstash:8.10.0
    volumes:
      - ./logstash.conf:/usr/share/logstash/pipeline/logstash.conf
    depends_on:
      - elasticsearch

  # Kibana
  kibana:
    image: docker.elastic.co/kibana/kibana:8.10.0
    ports:
      - "5601:5601"
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
    depends_on:
      - elasticsearch

  # Filebeat for log collection
  filebeat:
    image: docker.elastic.co/beats/filebeat:8.10.0
    user: root
    volumes:
      - ./filebeat.yml:/usr/share/filebeat/filebeat.yml:ro
      - /var/lib/docker/containers:/var/lib/docker/containers:ro
      - /var/run/docker.sock:/var/run/docker.sock:ro
    command: filebeat -e -strict.perms=false
    depends_on:
      - elasticsearch

volumes:
  es-data:
EOF
```

### Step 4.2: Structured Logging

```python
cat > logging_app.py << 'EOF'
import logging
import json
from datetime import datetime
from flask import Flask, request

app = Flask(__name__)

# Structured logging
class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_obj = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        if hasattr(record, 'request_id'):
            log_obj['request_id'] = record.request_id
        if hasattr(record, 'user_id'):
            log_obj['user_id'] = record.user_id
        return json.dumps(log_obj)

handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger = logging.getLogger()
logger.addHandler(handler)
logger.setLevel(logging.INFO)

@app.route('/api/<path:path>')
def api(path):
    logger.info('API request', extra={
        'request_id': request.headers.get('X-Request-ID'),
        'path': path,
        'method': request.method,
        'ip': request.remote_addr
    })
    return {'status': 'ok'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
EOF
```

### Step 4.3: Log Aggregation Pattern

```yaml
cat > docker-compose-fluentd.yml << 'EOF'
version: '3.8'

services:
  app:
    build: .
    logging:
      driver: "fluentd"
      options:
        fluentd-address: localhost:24224
        tag: "app.{{.Name}}"

  fluentd:
    image: fluent/fluentd:latest
    ports:
      - "24224:24224"
      - "24224:24224/udp"
    volumes:
      - ./fluentd.conf:/fluentd/etc/fluent.conf
      - fluentd-data:/fluentd/log

volumes:
  fluentd-data:
EOF
```

✅ **Checkpoint**: You can implement production logging strategies.

---

## Part 5: High Availability Patterns

### Step 5.1: Replica Management

```yaml
cat > docker-compose-ha.yml << 'EOF'
version: '3.8'

services:
  # Load balancer
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx-lb.conf:/etc/nginx/nginx.conf
    depends_on:
      - app

  # Application with multiple replicas
  app:
    build: .
    deploy:
      replicas: 3
      update_config:
        parallelism: 1  # Update one at a time
        delay: 10s
        failure_action: rollback
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
        window: 120s
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Database with replication
  db-primary:
    image: postgres:15
    environment:
      - POSTGRES_PASSWORD=secret
      - POSTGRES_REPLICATION_MODE=master
      - POSTGRES_REPLICATION_USER=replicator
      - POSTGRES_REPLICATION_PASSWORD=replicator_password
    volumes:
      - db-primary-data:/var/lib/postgresql/data

  db-replica:
    image: postgres:15
    environment:
      - POSTGRES_PASSWORD=secret
      - POSTGRES_MASTER_SERVICE_HOST=db-primary
      - POSTGRES_REPLICATION_MODE=slave
      - POSTGRES_REPLICATION_USER=replicator
      - POSTGRES_REPLICATION_PASSWORD=replicator_password
    volumes:
      - db-replica-data:/var/lib/postgresql/data
    depends_on:
      - db-primary

volumes:
  db-primary-data:
  db-replica-data:
EOF
```

### Step 5.2: Automatic Failover

```yaml
cat > docker-compose-failover.yml << 'EOF'
version: '3.8'

services:
  app:
    build: .
    deploy:
      replicas: 3
      placement:
        max_replicas_per_node: 1  # Spread across nodes
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 10s
      timeout: 5s
      retries: 3
      start_period: 40s
    restart: always

  # Redis with Sentinel for automatic failover
  redis-master:
    image: redis:7-alpine
    command: redis-server --appendonly yes

  redis-replica:
    image: redis:7-alpine
    command: redis-server --appendonly yes --slaveof redis-master 6379
    deploy:
      replicas: 2
    depends_on:
      - redis-master

  redis-sentinel:
    image: redis:7-alpine
    command: >
      redis-sentinel
      --sentinel monitor mymaster redis-master 6379 2
      --sentinel down-after-milliseconds mymaster 5000
      --sentinel parallel-syncs mymaster 1
      --sentinel failover-timeout mymaster 10000
    deploy:
      replicas: 3
    depends_on:
      - redis-master
EOF
```

✅ **Checkpoint**: You can implement high availability patterns.

---

## Part 6: Deployment Strategies

### Step 6.1: Blue-Green Deployment

```yaml
cat > docker-compose-bluegreen.yml << 'EOF'
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx-bluegreen.conf:/etc/nginx/nginx.conf
    environment:
      - ACTIVE_ENV=${ACTIVE_ENV:-blue}

  # Blue environment (current production)
  app-blue:
    build:
      context: .
      args:
        VERSION: blue
    environment:
      - VERSION=blue
    deploy:
      replicas: 3

  # Green environment (new version)
  app-green:
    build:
      context: .
      args:
        VERSION: green
    environment:
      - VERSION=green
    deploy:
      replicas: 3
EOF

# Nginx configuration for blue-green
cat > nginx-bluegreen.conf << 'EOF'
events {
    worker_connections 1024;
}

http {
    upstream blue {
        server app-blue:8000;
    }

    upstream green {
        server app-green:8000;
    }

    # Switch between blue and green
    map $http_upgrade $backend {
        default blue;  # Change to 'green' to switch
    }

    server {
        listen 80;

        location / {
            proxy_pass http://$backend;
            proxy_set_header Host $host;
        }
    }
}
EOF
```

```bash
# Deploy blue (current)
ACTIVE_ENV=blue docker compose -f docker-compose-bluegreen.yml up -d app-blue

# Deploy green (new version) alongside blue
docker compose -f docker-compose-bluegreen.yml up -d app-green

# Test green environment
curl -H "Host: green.example.com" http://localhost/

# Switch traffic to green (update nginx config)
# Then reload nginx
docker compose -f docker-compose-bluegreen.yml exec nginx nginx -s reload

# If successful, remove blue
# If failed, switch back to blue
```

### Step 6.2: Canary Deployment

```yaml
cat > docker-compose-canary.yml << 'EOF'
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx-canary.conf:/etc/nginx/nginx.conf

  # Stable version (90% traffic)
  app-stable:
    build:
      context: .
      args:
        VERSION: stable
    deploy:
      replicas: 9
    environment:
      - VERSION=stable

  # Canary version (10% traffic)
  app-canary:
    build:
      context: .
      args:
        VERSION: canary
    deploy:
      replicas: 1
    environment:
      - VERSION=canary
EOF

cat > nginx-canary.conf << 'EOF'
events {
    worker_connections 1024;
}

http {
    upstream backend {
        # 90% to stable
        server app-stable:8000 weight=9;
        # 10% to canary
        server app-canary:8000 weight=1;
    }

    server {
        listen 80;

        location / {
            proxy_pass http://backend;
            proxy_set_header Host $host;

            # Add header to identify version
            add_header X-App-Version $upstream_addr;
        }
    }
}
EOF
```

### Step 6.3: Rolling Updates

```yaml
cat > docker-compose-rolling.yml << 'EOF'
version: '3.8'

services:
  app:
    build: .
    deploy:
      replicas: 6
      update_config:
        parallelism: 2  # Update 2 at a time
        delay: 10s  # Wait 10s between batches
        failure_action: rollback  # Rollback on failure
        monitor: 30s  # Monitor for 30s
        max_failure_ratio: 0.3  # Rollback if >30% fail
        order: start-first  # Start new before stopping old
      rollback_config:
        parallelism: 2
        delay: 5s
        failure_action: pause
        monitor: 30s
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 10s
      timeout: 5s
      retries: 3
EOF
```

```bash
# Initial deployment
docker compose -f docker-compose-rolling.yml up -d

# Update to new version
docker compose -f docker-compose-rolling.yml build
docker compose -f docker-compose-rolling.yml up -d --no-deps --build app

# Monitor rolling update
watch docker compose -f docker-compose-rolling.yml ps
```

✅ **Checkpoint**: You can implement various deployment strategies.

---

## Part 7: Secret Management

### Step 7.1: Docker Secrets

```bash
# Create secrets
echo "db_password_secret" | docker secret create db_password -
echo "api_key_secret" | docker secret create api_key -

# List secrets
docker secret ls

# Use in Docker Compose
cat > docker-compose-secrets.yml << 'EOF'
version: '3.8'

services:
  app:
    image: myapp
    secrets:
      - db_password
      - api_key
    environment:
      - DB_PASSWORD_FILE=/run/secrets/db_password
      - API_KEY_FILE=/run/secrets/api_key

  db:
    image: postgres:15
    secrets:
      - db_password
    environment:
      - POSTGRES_PASSWORD_FILE=/run/secrets/db_password

secrets:
  db_password:
    external: true
  api_key:
    external: true
EOF
```

### Step 7.2: Environment-Specific Secrets

```yaml
cat > docker-compose-env-secrets.yml << 'EOF'
version: '3.8'

services:
  app:
    build: .
    secrets:
      - source: db_password
        target: /run/secrets/db_password
        mode: 0400  # Read-only for owner
    environment:
      - ENVIRONMENT=${ENVIRONMENT:-production}

secrets:
  db_password:
    file: ./secrets/${ENVIRONMENT}/db_password.txt
EOF
```

```bash
# Create secrets directory structure
mkdir -p secrets/development secrets/production

echo "dev_password" > secrets/development/db_password.txt
echo "prod_password" > secrets/production/db_password.txt

# Run with different environments
ENVIRONMENT=development docker compose -f docker-compose-env-secrets.yml up -d
ENVIRONMENT=production docker compose -f docker-compose-env-secrets.yml up -d
```

### Step 7.3: Vault Integration (Conceptual)

```python
# app_with_vault.py
cat > app_with_vault.py << 'EOF'
import hvac
import os
from flask import Flask

app = Flask(__name__)

# Initialize Vault client
vault_client = hvac.Client(
    url=os.environ.get('VAULT_ADDR', 'http://vault:8200'),
    token=os.environ.get('VAULT_TOKEN')
)

# Read secrets from Vault
def get_secret(path):
    try:
        secret = vault_client.secrets.kv.v2.read_secret_version(path=path)
        return secret['data']['data']
    except Exception as e:
        print(f"Error reading secret: {e}")
        return None

# Use secrets
db_credentials = get_secret('database/credentials')
api_keys = get_secret('api/keys')

@app.route('/health')
def health():
    return {'status': 'healthy'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
EOF
```

✅ **Checkpoint**: You can manage secrets securely.

---

## Part 8: CI/CD Integration

### Step 8.1: GitHub Actions Workflow

```yaml
# .github/workflows/docker-deploy.yml
cat > docker-deploy.yml << 'EOF'
name: Docker Build and Deploy

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  build:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2

      - name: Log in to registry
        uses: docker/login-action@v2
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v4
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=ref,event=branch
            type=ref,event=pr
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}
            type=sha

      - name: Build and push
        uses: docker/build-push-action@v4
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=registry,ref=${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:buildcache
          cache-to: type=registry,ref=${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:buildcache,mode=max

      - name: Run security scan
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ steps.meta.outputs.version }}
          format: 'sarif'
          output: 'trivy-results.sarif'

      - name: Upload scan results
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: 'trivy-results.sarif'

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'

    steps:
      - name: Deploy to production
        run: |
          # SSH to server and update containers
          # docker-compose pull
          # docker-compose up -d
          echo "Deploy step would go here"
EOF
```

### Step 8.2: GitLab CI/CD

```yaml
# .gitlab-ci.yml
cat > gitlab-ci.yml << 'EOF'
stages:
  - build
  - test
  - deploy

variables:
  DOCKER_DRIVER: overlay2
  IMAGE_TAG: $CI_REGISTRY_IMAGE:$CI_COMMIT_REF_SLUG

build:
  stage: build
  image: docker:latest
  services:
    - docker:dind
  before_script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
  script:
    - docker build -t $IMAGE_TAG .
    - docker push $IMAGE_TAG

test:
  stage: test
  image: $IMAGE_TAG
  script:
    - python -m pytest tests/

deploy_production:
  stage: deploy
  only:
    - main
  script:
    - docker-compose pull
    - docker-compose up -d
  environment:
    name: production
    url: https://app.example.com
EOF
```

### Step 8.3: Automated Testing

```bash
# create test script
cat > test-deployment.sh << 'EOF'
#!/bin/bash

set -e

echo "Starting deployment tests..."

# Build image
docker build -t myapp:test .

# Start services
docker compose -f docker-compose.test.yml up -d

# Wait for services to be healthy
echo "Waiting for services..."
timeout 60 sh -c 'until docker compose -f docker-compose.test.yml ps | grep -q healthy; do sleep 2; done'

# Run integration tests
docker compose -f docker-compose.test.yml exec -T app pytest tests/integration/

# Run smoke tests
curl -f http://localhost:8000/health || exit 1
curl -f http://localhost:8000/api/status || exit 1

# Cleanup
docker compose -f docker-compose.test.yml down -v

echo "All tests passed!"
EOF

chmod +x test-deployment.sh
```

✅ **Checkpoint**: You can integrate Docker with CI/CD pipelines.

---

## Part 9: Complete Production Stack

### Step 9.1: Full Production Configuration

```yaml
cat > docker-compose.production.yml << 'EOF'
version: '3.8'

services:
  # Reverse proxy
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/prod.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
      - nginx-cache:/var/cache/nginx
    depends_on:
      - app
    restart: always
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  # Application
  app:
    build:
      context: .
      dockerfile: Dockerfile.prod
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
      update_config:
        parallelism: 1
        delay: 10s
        failure_action: rollback
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
    secrets:
      - db_password
      - api_key
    environment:
      - ENVIRONMENT=production
      - DB_HOST=db
      - REDIS_HOST=redis
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    read_only: true
    tmpfs:
      - /tmp
    security_opt:
      - no-new-privileges:true
    cap_drop:
      - ALL
    cap_add:
      - NET_BIND_SERVICE
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  # Database
  db:
    image: postgres:15
    secrets:
      - db_password
    environment:
      - POSTGRES_PASSWORD_FILE=/run/secrets/db_password
    volumes:
      - db-data:/var/lib/postgresql/data
      - ./backups:/backups
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: always
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  # Cache
  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes --maxmemory 256mb --maxmemory-policy allkeys-lru
    volumes:
      - redis-data:/data
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5
    restart: always

  # Monitoring
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus-data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.retention.time=30d'
    restart: always

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    volumes:
      - grafana-data:/var/lib/grafana
      - ./grafana/dashboards:/etc/grafana/provisioning/dashboards
    environment:
      - GF_SECURITY_ADMIN_PASSWORD_FILE=/run/secrets/grafana_password
      - GF_USERS_ALLOW_SIGN_UP=false
    secrets:
      - grafana_password
    depends_on:
      - prometheus
    restart: always

volumes:
  db-data:
    driver: local
  redis-data:
    driver: local
  prometheus-data:
    driver: local
  grafana-data:
    driver: local
  nginx-cache:
    driver: local

secrets:
  db_password:
    file: ./secrets/prod/db_password.txt
  api_key:
    file: ./secrets/prod/api_key.txt
  grafana_password:
    file: ./secrets/prod/grafana_password.txt

networks:
  default:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
EOF
```

✅ **Checkpoint**: You can deploy a complete production stack.

---

## Summary

**What You Accomplished**:
✅ Implemented security hardening
✅ Configured resource limits
✅ Set up health checks and monitoring
✅ Implemented centralized logging
✅ Built high availability patterns
✅ Mastered deployment strategies
✅ Managed secrets securely
✅ Integrated with CI/CD
✅ Deployed complete production stacks

**Production Checklist**:
- [x] Non-root users
- [x] Read-only filesystems
- [x] Resource limits
- [x] Health checks
- [x] Logging configured
- [x] Monitoring enabled
- [x] Secrets management
- [x] High availability
- [x] Automated deployments
- [x] Rollback strategy

---

## Next Steps

**Continue Learning**:
- **Exercise 07**: Complete ML Application Containerization
- **Module Quiz**: Test your Docker knowledge

---

**Exercise Version**: 1.0
**Last Updated**: October 2025
**Estimated Time**: 4-5 hours
**Difficulty**: Advanced
