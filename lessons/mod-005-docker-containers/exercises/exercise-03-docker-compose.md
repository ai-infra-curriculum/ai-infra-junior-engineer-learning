# Exercise 03: Docker Compose Applications

## Exercise Overview

**Objective**: Master Docker Compose for orchestrating multi-container applications, including databases, web services, caching layers, and ML inference services.

**Difficulty**: Intermediate
**Estimated Time**: 3-4 hours
**Prerequisites**:
- Exercise 01 (Container Operations)
- Exercise 02 (Building Custom Images)
- Lecture 03 (Docker Compose)

## Learning Objectives

By completing this exercise, you will:
- Write docker-compose.yml files for multi-container applications
- Design service architectures with proper dependency management
- Configure environment variables and secrets for different environments
- Implement volume strategies for data persistence across services
- Set up custom networks for service isolation and discovery
- Scale services horizontally using replica configuration
- Deploy production-ready stacks with health checks and restart policies
- Build ML serving infrastructure with databases, caching, and monitoring
- Manage container lifecycle using Compose commands (up, down, logs, ps)
- Debug multi-container applications using Compose tools

---

## Part 1: Your First Compose Application

### Step 1.1: Simple Web + Database Stack

```bash
# Create project directory
mkdir -p ~/docker-exercises/compose-basics
cd ~/docker-exercises/compose-basics

# Create a simple Flask app
cat > app.py << 'EOF'
from flask import Flask, jsonify
import psycopg2
import os

app = Flask(__name__)

def get_db_connection():
    return psycopg2.connect(
        host=os.environ.get('DB_HOST', 'db'),
        database=os.environ.get('DB_NAME', 'myapp'),
        user=os.environ.get('DB_USER', 'postgres'),
        password=os.environ.get('DB_PASSWORD', 'postgres')
    )

@app.route('/')
def home():
    return jsonify({'message': 'Hello from Docker Compose!'})

@app.route('/db-test')
def db_test():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT version();')
        version = cur.fetchone()[0]
        cur.close()
        conn.close()
        return jsonify({'status': 'connected', 'db_version': version})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
EOF

# Create requirements
cat > requirements.txt << 'EOF'
flask==3.0.0
psycopg2-binary==2.9.9
EOF

# Create Dockerfile
cat > Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

CMD ["python", "app.py"]
EOF
```

### Step 1.2: Create docker-compose.yml

```yaml
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      - DB_HOST=db
      - DB_NAME=myapp
      - DB_USER=postgres
      - DB_PASSWORD=postgres
    depends_on:
      - db

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=myapp
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
EOF
```

### Step 1.3: Run Your First Compose Stack

```bash
# Start all services
docker compose up

# In another terminal, test the application
curl http://localhost:5000
curl http://localhost:5000/db-test

# View logs
docker compose logs
docker compose logs web
docker compose logs db

# Stop with Ctrl+C, then remove
docker compose down

# Run in detached mode
docker compose up -d

# Check status
docker compose ps

# View logs in follow mode
docker compose logs -f

# Stop and remove everything including volumes
docker compose down -v
```

**Questions**:
1. What happens if you start the web service before the database?
2. How does the web service resolve the hostname "db"?
3. What happens to the data when you run `docker compose down`?
4. What about with `docker compose down -v`?

✅ **Checkpoint**: You can run a multi-container application with Docker Compose.

---

## Part 2: Service Dependencies and Health Checks

### Step 2.1: Improve Startup Order

```yaml
cat > docker-compose-v2.yml << 'EOF'
version: '3.8'

services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      - DB_HOST=db
      - DB_NAME=myapp
      - DB_USER=postgres
      - DB_PASSWORD=postgres
    depends_on:
      db:
        condition: service_healthy
    restart: on-failure

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=myapp
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
EOF
```

```bash
# Run with health checks
docker compose -f docker-compose-v2.yml up

# Watch services become healthy
docker compose -f docker-compose-v2.yml ps
```

### Step 2.2: Add Initialization Script

```bash
# Create init script for database
mkdir -p init-scripts

cat > init-scripts/01-create-tables.sql << 'EOF'
CREATE TABLE IF NOT EXISTS visits (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(50)
);

CREATE INDEX idx_timestamp ON visits(timestamp);

INSERT INTO visits (ip_address) VALUES ('127.0.0.1');
EOF
```

```yaml
cat > docker-compose-v3.yml << 'EOF'
version: '3.8'

services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      - DB_HOST=db
      - DB_NAME=myapp
      - DB_USER=postgres
      - DB_PASSWORD=postgres
    depends_on:
      db:
        condition: service_healthy

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=myapp
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init-scripts:/docker-entrypoint-initdb.d
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
EOF
```

```bash
# Start with init scripts
docker compose -f docker-compose-v3.yml up -d

# Verify table was created
docker compose -f docker-compose-v3.yml exec db \
  psql -U postgres -d myapp -c "SELECT * FROM visits;"
```

✅ **Checkpoint**: You can manage service dependencies and initialization.

---

## Part 3: Environment Configuration

### Step 3.1: Using .env Files

```bash
# Create environment file
cat > .env << 'EOF'
# Database Configuration
POSTGRES_DB=myapp
POSTGRES_USER=appuser
POSTGRES_PASSWORD=securepassword123

# Application Configuration
FLASK_ENV=development
DEBUG=true
SECRET_KEY=dev-secret-key

# Ports
WEB_PORT=5000
DB_PORT=5432
EOF

# Create .env.production
cat > .env.production << 'EOF'
POSTGRES_DB=myapp_prod
POSTGRES_USER=produser
POSTGRES_PASSWORD=super-secure-production-password

FLASK_ENV=production
DEBUG=false
SECRET_KEY=production-secret-key-change-me

WEB_PORT=8000
DB_PORT=5432
EOF
```

### Step 3.2: Use Variables in Compose

```yaml
cat > docker-compose-env.yml << 'EOF'
version: '3.8'

services:
  web:
    build: .
    ports:
      - "${WEB_PORT:-5000}:5000"
    environment:
      - DB_HOST=db
      - DB_NAME=${POSTGRES_DB}
      - DB_USER=${POSTGRES_USER}
      - DB_PASSWORD=${POSTGRES_PASSWORD}
      - FLASK_ENV=${FLASK_ENV:-development}
      - DEBUG=${DEBUG:-false}
      - SECRET_KEY=${SECRET_KEY}
    depends_on:
      db:
        condition: service_healthy

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=${POSTGRES_DB}
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    ports:
      - "${DB_PORT:-5432}:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
EOF
```

```bash
# Run with default .env
docker compose -f docker-compose-env.yml up -d

# Run with production env
docker compose -f docker-compose-env.yml --env-file .env.production up -d

# Check which variables are used
docker compose -f docker-compose-env.yml config
```

### Step 3.3: Environment-Specific Overrides

```yaml
# Create base configuration
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  web:
    build: .
    environment:
      - DB_HOST=db
    depends_on:
      db:
        condition: service_healthy

  db:
    image: postgres:15
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
EOF

# Create development override
cat > docker-compose.override.yml << 'EOF'
version: '3.8'

services:
  web:
    ports:
      - "5000:5000"
    volumes:
      - .:/app  # Mount code for hot reload
    environment:
      - FLASK_ENV=development
      - DEBUG=true

  db:
    ports:
      - "5432:5432"  # Expose DB in development
EOF

# Create production override
cat > docker-compose.prod.yml << 'EOF'
version: '3.8'

services:
  web:
    ports:
      - "8000:5000"
    environment:
      - FLASK_ENV=production
      - DEBUG=false
    restart: always
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '0.5'
          memory: 512M

  db:
    restart: always
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
EOF
```

```bash
# Development (uses base + override automatically)
docker compose up -d

# Production (explicit override)
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

✅ **Checkpoint**: You can manage environment-specific configurations.

---

## Part 4: Adding More Services

### Step 4.1: Complete Web Stack (Web + DB + Redis + Nginx)

```bash
# Create new project
mkdir -p ~/docker-exercises/full-stack
cd ~/docker-exercises/full-stack

# Create Flask app with Redis caching
cat > app.py << 'EOF'
from flask import Flask, jsonify
import redis
import psycopg2
import os
import time

app = Flask(__name__)

# Redis connection
cache = redis.Redis(
    host=os.environ.get('REDIS_HOST', 'redis'),
    port=6379,
    decode_responses=True
)

# Database connection
def get_db():
    return psycopg2.connect(
        host=os.environ.get('DB_HOST', 'db'),
        database=os.environ.get('DB_NAME', 'myapp'),
        user=os.environ.get('DB_USER', 'postgres'),
        password=os.environ.get('DB_PASSWORD', 'postgres')
    )

@app.route('/health')
def health():
    return jsonify({'status': 'healthy'})

@app.route('/')
def home():
    # Increment page views in Redis
    cache.incr('page_views')
    views = cache.get('page_views')
    return jsonify({
        'message': 'Hello from Full Stack!',
        'page_views': views
    })

@app.route('/slow')
def slow_endpoint():
    # Check cache first
    cached = cache.get('slow_result')
    if cached:
        return jsonify({'result': cached, 'cached': True})

    # Simulate slow operation
    time.sleep(3)
    result = "Computed expensive result"

    # Cache for 60 seconds
    cache.setex('slow_result', 60, result)

    return jsonify({'result': result, 'cached': False})

@app.route('/stats')
def stats():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT COUNT(*) FROM visits;')
    visit_count = cur.fetchone()[0]
    cur.close()
    conn.close()

    return jsonify({
        'db_visits': visit_count,
        'cache_views': cache.get('page_views')
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
EOF

# Requirements
cat > requirements.txt << 'EOF'
flask==3.0.0
redis==5.0.1
psycopg2-binary==2.9.9
EOF

# Dockerfile
cat > Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

HEALTHCHECK --interval=30s --timeout=3s \
  CMD python -c "import requests; requests.get('http://localhost:5000/health')" || exit 1

CMD ["python", "app.py"]
EOF

# Nginx configuration
mkdir -p nginx

cat > nginx/nginx.conf << 'EOF'
upstream web_backend {
    server web:5000;
}

server {
    listen 80;
    server_name localhost;

    location / {
        proxy_pass http://web_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /health {
        access_log off;
        proxy_pass http://web_backend;
    }
}
EOF
```

### Step 4.2: Complete Docker Compose

```yaml
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/conf.d/default.conf
    depends_on:
      web:
        condition: service_healthy
    restart: always

  web:
    build: .
    environment:
      - DB_HOST=db
      - DB_NAME=myapp
      - DB_USER=postgres
      - DB_PASSWORD=postgres
      - REDIS_HOST=redis
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: always

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=myapp
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init-scripts:/docker-entrypoint-initdb.d
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5

volumes:
  postgres_data:
  redis_data:
EOF
```

```bash
# Create init script
mkdir -p init-scripts
cat > init-scripts/01-init.sql << 'EOF'
CREATE TABLE visits (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
INSERT INTO visits (timestamp) VALUES (NOW());
EOF

# Start the full stack
docker compose up -d

# Wait for services to be healthy
sleep 15

# Test the application
curl http://localhost/
curl http://localhost/stats
curl http://localhost/slow  # First call - slow
curl http://localhost/slow  # Second call - cached!

# Check logs
docker compose logs -f web

# Check all services
docker compose ps
```

✅ **Checkpoint**: You can orchestrate a complete web stack with multiple services.

---

## Part 5: ML Inference Stack

### Step 5.1: ML Model Serving with Supporting Services

```bash
# Create ML project
mkdir -p ~/docker-exercises/ml-stack
cd ~/docker-exercises/ml-stack

# Create model serving app
cat > serve.py << 'EOF'
from flask import Flask, request, jsonify
import torch
import torchvision.models as models
import torchvision.transforms as transforms
from PIL import Image
import io
import redis
import json
import hashlib
import psycopg2
import os
from datetime import datetime

app = Flask(__name__)

# Load model
print("Loading model...")
model = models.resnet18(pretrained=True)
model.eval()
print("Model loaded!")

# Redis for caching
cache = redis.Redis(host=os.environ.get('REDIS_HOST', 'redis'), decode_responses=True)

# Database for logging
def get_db():
    return psycopg2.connect(
        host=os.environ.get('DB_HOST', 'db'),
        database=os.environ.get('DB_NAME', 'mlapp'),
        user=os.environ.get('DB_USER', 'postgres'),
        password=os.environ.get('DB_PASSWORD', 'postgres')
    )

# Image preprocessing
transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'model': 'resnet18'})

@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    img_bytes = file.read()

    # Create hash for caching
    img_hash = hashlib.md5(img_bytes).hexdigest()

    # Check cache
    cached_result = cache.get(f'prediction:{img_hash}')
    if cached_result:
        cache.incr('cache_hits')
        return jsonify({
            'predictions': json.loads(cached_result),
            'cached': True,
            'image_hash': img_hash
        })

    # Process image
    img = Image.open(io.BytesIO(img_bytes)).convert('RGB')
    img_tensor = transform(img).unsqueeze(0)

    # Predict
    with torch.no_grad():
        output = model(img_tensor)
        probabilities = torch.nn.functional.softmax(output[0], dim=0)
        top5_prob, top5_catid = torch.topk(probabilities, 5)

    results = []
    for i in range(5):
        results.append({
            'class_id': top5_catid[i].item(),
            'probability': float(top5_prob[i].item())
        })

    # Cache result
    cache.setex(f'prediction:{img_hash}', 3600, json.dumps(results))
    cache.incr('cache_misses')

    # Log to database
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            'INSERT INTO predictions (image_hash, top_class, confidence) VALUES (%s, %s, %s)',
            (img_hash, results[0]['class_id'], results[0]['probability'])
        )
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"DB logging error: {e}")

    return jsonify({
        'predictions': results,
        'cached': False,
        'image_hash': img_hash
    })

@app.route('/metrics')
def metrics():
    cache_hits = int(cache.get('cache_hits') or 0)
    cache_misses = int(cache.get('cache_misses') or 0)
    total = cache_hits + cache_misses
    hit_rate = (cache_hits / total * 100) if total > 0 else 0

    # Get prediction count from DB
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute('SELECT COUNT(*) FROM predictions')
        total_predictions = cur.fetchone()[0]
        cur.close()
        conn.close()
    except:
        total_predictions = 0

    return jsonify({
        'cache_hits': cache_hits,
        'cache_misses': cache_misses,
        'cache_hit_rate': f"{hit_rate:.2f}%",
        'total_predictions': total_predictions
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
EOF

# Requirements
cat > requirements.txt << 'EOF'
flask==3.0.0
torch==2.1.0
torchvision==0.16.0
pillow==10.1.0
redis==5.0.1
psycopg2-binary==2.9.9
gunicorn==21.2.0
EOF

# Dockerfile
cat > Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends libgomp1 && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY serve.py .

HEALTHCHECK --interval=30s --timeout=5s --start-period=60s \
  CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "--timeout", "120", "serve:app"]
EOF
```

### Step 5.2: ML Stack Docker Compose

```yaml
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  ml-api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DB_HOST=db
      - DB_NAME=mlapp
      - DB_USER=postgres
      - DB_PASSWORD=postgres
      - REDIS_HOST=redis
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: always
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=mlapp
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init-db:/docker-entrypoint-initdb.d
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    command: redis-server --maxmemory 256mb --maxmemory-policy allkeys-lru
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5

  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'

volumes:
  postgres_data:
  redis_data:
  prometheus_data:
EOF
```

```bash
# Create database init script
mkdir -p init-db
cat > init-db/01-schema.sql << 'EOF'
CREATE TABLE predictions (
    id SERIAL PRIMARY KEY,
    image_hash VARCHAR(32) NOT NULL,
    top_class INTEGER,
    confidence REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_image_hash ON predictions(image_hash);
CREATE INDEX idx_created_at ON predictions(created_at);
EOF

# Create Prometheus config
cat > prometheus.yml << 'EOF'
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'ml-api'
    static_configs:
      - targets: ['ml-api:8000']
EOF

# Start ML stack
docker compose up -d

# Wait for services
sleep 30

# Test health
curl http://localhost:8000/health

# Test metrics
curl http://localhost:8000/metrics
```

✅ **Checkpoint**: You can deploy an ML inference stack with caching and monitoring.

---

## Part 6: Scaling Services

### Step 6.1: Scale Web Service

```bash
# Scale web service to 3 replicas
docker compose up -d --scale web=3

# Check all instances
docker compose ps

# Test load distribution
for i in {1..10}; do
  curl http://localhost/
done

# View logs from all replicas
docker compose logs web

# Scale down
docker compose up -d --scale web=1
```

### Step 6.2: Load Balancing with Nginx

```bash
# Create project with load balancing
mkdir -p ~/docker-exercises/load-balance
cd ~/docker-exercises/load-balance

# Create simple app that shows hostname
cat > app.py << 'EOF'
from flask import Flask, jsonify
import socket
import os

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        'hostname': socket.gethostname(),
        'message': 'Hello from instance'
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
EOF

cat > requirements.txt << 'EOF'
flask==3.0.0
EOF

cat > Dockerfile << 'EOF'
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
CMD ["python", "app.py"]
EOF

# Nginx config with load balancing
mkdir -p nginx
cat > nginx/nginx.conf << 'EOF'
upstream web_backend {
    # Load balancing configuration
    least_conn;  # Use least connections algorithm

    server web:5000 max_fails=3 fail_timeout=30s;
}

server {
    listen 80;

    location / {
        proxy_pass http://web_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
EOF

cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/conf.d/default.conf
    depends_on:
      - web

  web:
    build: .
    deploy:
      replicas: 3
EOF
```

```bash
# Start with 3 replicas
docker compose up -d

# Test load balancing (see different hostnames)
for i in {1..10}; do
  curl http://localhost/ | grep hostname
  sleep 0.5
done
```

✅ **Checkpoint**: You can scale services and configure load balancing.

---

## Part 7: Named Networks and Isolation

### Step 7.1: Multi-Network Architecture

```yaml
cat > docker-compose-networks.yml << 'EOF'
version: '3.8'

services:
  # Frontend network
  nginx:
    image: nginx:alpine
    networks:
      - frontend
    ports:
      - "80:80"

  # Both networks
  api:
    build: .
    networks:
      - frontend
      - backend
    environment:
      - DB_HOST=db
      - CACHE_HOST=cache

  # Backend network only
  db:
    image: postgres:15
    networks:
      - backend
    environment:
      - POSTGRES_PASSWORD=postgres

  cache:
    image: redis:7-alpine
    networks:
      - backend

networks:
  frontend:
    driver: bridge
  backend:
    driver: bridge
    internal: true  # No external access
EOF
```

```bash
# Start with network isolation
docker compose -f docker-compose-networks.yml up -d

# Verify nginx can't access db directly
docker compose -f docker-compose-networks.yml exec nginx ping db
# Should fail - different networks!

# But api can access both
docker compose -f docker-compose-networks.yml exec api ping nginx
docker compose -f docker-compose-networks.yml exec api ping db
```

### Step 7.2: Custom Network Configuration

```yaml
cat > docker-compose-custom-net.yml << 'EOF'
version: '3.8'

services:
  web:
    image: nginx
    networks:
      app_net:
        ipv4_address: 172.25.0.10

  api:
    build: .
    networks:
      app_net:
        ipv4_address: 172.25.0.11

  db:
    image: postgres:15
    networks:
      app_net:
        ipv4_address: 172.25.0.12
    environment:
      - POSTGRES_PASSWORD=postgres

networks:
  app_net:
    driver: bridge
    ipam:
      config:
        - subnet: 172.25.0.0/16
          gateway: 172.25.0.1
EOF
```

✅ **Checkpoint**: You can configure network isolation and custom networks.

---

## Part 8: Volume Management Patterns

### Step 8.1: Named Volumes vs Bind Mounts

```yaml
cat > docker-compose-volumes.yml << 'EOF'
version: '3.8'

services:
  web:
    build: .
    volumes:
      # Bind mount for development (hot reload)
      - ./app:/app
      # Named volume for dependencies
      - node_modules:/app/node_modules
      # tmpfs for temporary files
      - type: tmpfs
        target: /tmp

  db:
    image: postgres:15
    volumes:
      # Named volume for persistence
      - db_data:/var/lib/postgresql/data
      # Bind mount for backups
      - ./backups:/backups
    environment:
      - POSTGRES_PASSWORD=postgres

  logs:
    image: busybox
    volumes:
      # Shared volume between services
      - app_logs:/logs
    command: tail -f /logs/app.log

volumes:
  node_modules:
  db_data:
  app_logs:
EOF
```

### Step 8.2: Backup and Restore

```bash
# Backup volume data
docker compose -f docker-compose-volumes.yml exec db \
  pg_dump -U postgres mydb > ./backups/backup-$(date +%Y%m%d).sql

# Or backup entire volume
docker run --rm \
  -v full-stack_postgres_data:/data \
  -v $(pwd)/backups:/backup \
  alpine tar czf /backup/postgres-data.tar.gz -C /data .

# Restore from backup
docker run --rm \
  -v full-stack_postgres_data:/data \
  -v $(pwd)/backups:/backup \
  alpine tar xzf /backup/postgres-data.tar.gz -C /data
```

✅ **Checkpoint**: You can manage volumes for different use cases.

---

## Part 9: Production Best Practices

### Step 9.1: Production-Ready Compose File

```yaml
cat > docker-compose.prod.yml << 'EOF'
version: '3.8'

services:
  web:
    build:
      context: .
      dockerfile: Dockerfile.prod
    restart: always
    environment:
      - ENVIRONMENT=production
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
    networks:
      - app_network

  db:
    image: postgres:15
    restart: always
    environment:
      - POSTGRES_PASSWORD_FILE=/run/secrets/db_password
    secrets:
      - db_password
    volumes:
      - db_data:/var/lib/postgresql/data
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - app_network

secrets:
  db_password:
    file: ./secrets/db_password.txt

volumes:
  db_data:
    driver: local

networks:
  app_network:
    driver: bridge
EOF
```

### Step 9.2: Health Checks and Monitoring

```yaml
cat > docker-compose-monitoring.yml << 'EOF'
version: '3.8'

services:
  app:
    build: .
    healthcheck:
      test: ["CMD-SHELL", "curl -f http://localhost:5000/health || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  prometheus:
    image: prom/prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana
    volumes:
      - grafana_data:/var/lib/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin

volumes:
  prometheus_data:
  grafana_data:
EOF
```

✅ **Checkpoint**: You can create production-ready Compose configurations.

---

## Part 10: Debugging and Troubleshooting

### Step 10.1: Common Issues

```bash
# View service logs
docker compose logs service_name

# Follow logs in real-time
docker compose logs -f --tail=100

# Check service status
docker compose ps

# Inspect service details
docker compose exec service_name env
docker compose exec service_name ps aux

# Restart specific service
docker compose restart service_name

# Rebuild and restart
docker compose up -d --build service_name

# Validate compose file
docker compose config

# View resolved configuration
docker compose config --resolve-image-digests
```

### Step 10.2: Debugging Techniques

```bash
# Start services one by one
docker compose up db
docker compose up db redis
docker compose up  # All services

# Run command in service
docker compose exec web bash
docker compose exec db psql -U postgres

# Check network connectivity
docker compose exec web ping db
docker compose exec web nc -zv db 5432

# View resource usage
docker stats

# Inspect volumes
docker volume ls
docker volume inspect project_volume_name
```

✅ **Checkpoint**: You can debug and troubleshoot Compose applications.

---

## Practical Challenges

### Challenge 1: Complete E-commerce Stack

**Requirements**:
- Frontend (Nginx)
- API (Python/Flask)
- Database (PostgreSQL)
- Cache (Redis)
- Message Queue (RabbitMQ)
- Worker service
- All with proper health checks
- Environment-based configuration

### Challenge 2: ML Pipeline

**Requirements**:
- Model training service (scheduled)
- Model serving API
- Feature store (PostgreSQL)
- Model registry
- Monitoring (Prometheus + Grafana)
- Proper volume management for models

### Challenge 3: Microservices Architecture

**Requirements**:
- User service
- Product service
- Order service
- API Gateway
- Service mesh
- Separate networks for frontend/backend
- Shared logging volume

---

## Summary

**What You Accomplished**:
✅ Created multi-container applications with Docker Compose
✅ Managed service dependencies and startup order
✅ Configured environment variables and secrets
✅ Built complete web stacks (web + db + cache + proxy)
✅ Deployed ML inference services with supporting infrastructure
✅ Scaled services and configured load balancing
✅ Implemented network isolation
✅ Managed volumes for different use cases
✅ Applied production best practices
✅ Debugged and troubleshooted compose applications

**Key Compose Features Mastered**:
- Service definitions and dependencies
- Health checks and restart policies
- Environment configuration and secrets
- Volume management (named, bind mounts, tmpfs)
- Network isolation and custom networks
- Scaling and resource limits
- Logging configuration
- Production deployment patterns

---

## Next Steps

**Continue Learning**:
- **Exercise 04**: Advanced Networking Scenarios
- **Exercise 05**: Volume Management and Data Persistence
- **Exercise 06**: Production Deployment Strategies
- **Exercise 07**: Complete ML Application Containerization

---

**Exercise Version**: 1.0
**Last Updated**: October 2025
**Estimated Time**: 3-4 hours
**Difficulty**: Intermediate
