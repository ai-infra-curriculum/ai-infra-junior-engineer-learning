# Exercise 04: Docker Networking Scenarios

## Exercise Overview

**Objective**: Master Docker networking concepts including network drivers, service discovery, DNS resolution, network isolation, and advanced networking patterns for ML infrastructure.

**Difficulty**: Intermediate to Advanced
**Estimated Time**: 3-4 hours
**Prerequisites**:
- Exercise 01-03 (Container Operations, Images, Compose)
- Lecture 04 (Networking & Volumes)

## Learning Objectives

By completing this exercise, you will:
- Compare Docker network drivers (bridge, host, overlay, macvlan) and their use cases
- Configure DNS-based service discovery for container communication
- Implement network isolation strategies for security boundaries
- Create custom bridge networks with specific IP ranges
- Enable container-to-container communication within networks
- Configure external connectivity and port mappings
- Design load balancing patterns for distributed ML inference
- Set up multi-host networking for distributed systems
- Troubleshoot network issues using Docker and system tools
- Apply networking best practices for ML infrastructure

---

## Part 1: Understanding Network Drivers

### Step 1.1: Bridge Network (Default)

```bash
# Create project directory
mkdir -p ~/docker-exercises/networking
cd ~/docker-exercises/networking

# Inspect default bridge network
docker network ls
docker network inspect bridge

# Run container on default bridge
docker run -d --name web1 nginx
docker run -d --name web2 nginx

# Check their IPs
docker inspect web1 --format='{{.NetworkSettings.IPAddress}}'
docker inspect web2 --format='{{.NetworkSettings.IPAddress}}'

# Try DNS resolution (will fail on default bridge!)
docker exec web1 ping web2
# Error: ping: web2: Name or service not known

# Containers can ping by IP though
WEB2_IP=$(docker inspect web2 --format='{{.NetworkSettings.IPAddress}}')
docker exec web1 ping -c 3 $WEB2_IP

# Cleanup
docker rm -f web1 web2
```

**Key Insight**: Default bridge network doesn't support automatic DNS resolution!

### Step 1.2: Custom Bridge Network

```bash
# Create custom bridge network
docker network create my-network

# Inspect it
docker network inspect my-network

# Run containers on custom network
docker run -d --name web1 --network my-network nginx
docker run -d --name web2 --network my-network nginx

# Now DNS works!
docker exec web1 ping -c 3 web2
docker exec web2 ping -c 3 web1

# Success! Custom bridges provide automatic DNS resolution
```

### Step 1.3: Host Network

```bash
# Run container with host network
docker run -d --name web-host --network host nginx

# Container uses host's network stack directly
# No port mapping needed - nginx accessible on port 80

# Check (if port 80 is available)
curl http://localhost:80

# View network settings
docker inspect web-host --format='{{.NetworkSettings.Networks}}'

# Cleanup
docker rm -f web-host
```

**Use Cases**:
- High-performance networking (no NAT overhead)
- Network monitoring tools
- When you need host's network interfaces

**Limitations**:
- No network isolation
- Can't run multiple containers on same port
- Less portable

### Step 1.4: None Network

```bash
# Container with no network
docker run -d --name isolated --network none alpine sleep 3600

# Verify no network interfaces (except loopback)
docker exec isolated ip addr show

# Only sees 'lo' (loopback)

# Cleanup
docker rm -f isolated
```

**Use Cases**:
- Maximum network isolation
- Testing scenarios
- Security-sensitive workloads

✅ **Checkpoint**: You understand different Docker network drivers.

---

## Part 2: Service Discovery and DNS

### Step 2.1: Basic Service Discovery

```bash
# Create network
docker network create app-net

# Run database
docker run -d \
  --name postgres-db \
  --network app-net \
  -e POSTGRES_PASSWORD=secret \
  postgres:15

# Run application that connects to 'postgres-db'
cat > app.py << 'EOF'
import psycopg2
import sys

try:
    # Connect using service name 'postgres-db'
    conn = psycopg2.connect(
        host='postgres-db',
        database='postgres',
        user='postgres',
        password='secret'
    )
    print("✓ Successfully connected to database!")
    print(f"Database: {conn.get_dsn_parameters()['host']}")
    conn.close()
except Exception as e:
    print(f"✗ Connection failed: {e}")
    sys.exit(1)
EOF

cat > Dockerfile << 'EOF'
FROM python:3.11-slim
RUN pip install psycopg2-binary
COPY app.py .
CMD ["python", "app.py"]
EOF

docker build -t db-client .

# Run client - it finds DB by name!
docker run --rm --network app-net db-client
```

### Step 2.2: DNS Round-Robin

```bash
# Create multiple containers with same network alias
docker network create lb-net

# Run 3 web servers with alias 'web'
docker run -d --name web1 --network lb-net --network-alias web nginx
docker run -d --name web2 --network lb-net --network-alias web nginx
docker run -d --name web3 --network lb-net --network-alias web nginx

# Create test client
docker run -it --rm --network lb-net alpine sh

# Inside container, try multiple DNS lookups:
# nslookup web
# wget -qO- http://web
# Multiple requests will round-robin across containers
```

### Step 2.3: Service Discovery in Compose

```yaml
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  api:
    build: .
    environment:
      # Can reference other services by name
      - DB_HOST=database
      - CACHE_HOST=redis-cache
      - QUEUE_HOST=message-queue
    depends_on:
      - database
      - redis-cache
      - message-queue

  database:
    image: postgres:15
    environment:
      - POSTGRES_PASSWORD=secret

  redis-cache:
    image: redis:7-alpine

  message-queue:
    image: rabbitmq:3-alpine
EOF
```

**How It Works**:
- Compose creates a default network
- Each service gets a DNS entry matching its service name
- Services can resolve each other by name
- Multiple replicas get round-robin DNS

✅ **Checkpoint**: You understand Docker DNS and service discovery.

---

## Part 3: Network Isolation Patterns

### Step 3.1: Frontend-Backend Separation

```bash
mkdir -p ~/docker-exercises/network-isolation
cd ~/docker-exercises/network-isolation

# Create simple API
cat > api.py << 'EOF'
from flask import Flask, jsonify
import psycopg2
import os

app = Flask(__name__)

@app.route('/data')
def get_data():
    conn = psycopg2.connect(
        host='db',
        database='app',
        user='postgres',
        password=os.environ['DB_PASSWORD']
    )
    cur = conn.cursor()
    cur.execute('SELECT version();')
    version = cur.fetchone()[0]
    return jsonify({'db_version': version})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
EOF

cat > requirements.txt << 'EOF'
flask==3.0.0
psycopg2-binary==2.9.9
EOF

cat > Dockerfile << 'EOF'
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY api.py .
CMD ["python", "api.py"]
EOF
```

```yaml
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  # Public-facing (frontend network only)
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    networks:
      - frontend
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf

  # API layer (both networks)
  api:
    build: .
    networks:
      - frontend
      - backend
    environment:
      - DB_PASSWORD=secret

  # Database (backend network only - isolated!)
  db:
    image: postgres:15
    networks:
      - backend
    environment:
      - POSTGRES_DB=app
      - POSTGRES_PASSWORD=secret

networks:
  frontend:
    driver: bridge
  backend:
    driver: bridge
    internal: true  # No external internet access
EOF
```

```bash
# Start services
docker compose up -d

# Verify isolation
# Nginx CAN reach API
docker compose exec nginx nc -zv api 5000

# Nginx CANNOT reach DB directly (different network)
docker compose exec nginx nc -zv db 5432
# Should fail!

# API CAN reach DB (on backend network)
docker compose exec api nc -zv db 5432

# DB cannot reach internet (internal network)
docker compose exec db ping -c 1 8.8.8.8
# Should fail!
```

**Security Benefits**:
- Database not exposed to frontend
- Backend network has no internet access
- API acts as controlled gateway
- Minimizes attack surface

### Step 3.2: Multi-Tier Isolation

```yaml
cat > docker-compose-3tier.yml << 'EOF'
version: '3.8'

services:
  # Tier 1: Public DMZ
  load-balancer:
    image: nginx:alpine
    ports:
      - "443:443"
    networks:
      - dmz

  # Tier 2: Application Layer
  web-app:
    build: .
    networks:
      - dmz
      - app-tier
    depends_on:
      - api

  api:
    build: ./api
    networks:
      - app-tier
      - data-tier

  # Tier 3: Data Layer
  database:
    image: postgres:15
    networks:
      - data-tier
    environment:
      - POSTGRES_PASSWORD=secret

  cache:
    image: redis:7-alpine
    networks:
      - data-tier

networks:
  dmz:
    driver: bridge
  app-tier:
    driver: bridge
    internal: true
  data-tier:
    driver: bridge
    internal: true
EOF
```

**Network Diagram**:
```
Internet → DMZ → App Tier → Data Tier
           ↓      ↓          ↓
          LB     Web/API    DB/Cache
```

✅ **Checkpoint**: You can implement network isolation for security.

---

## Part 4: Custom Network Configuration

### Step 4.1: Custom Subnet and IP Ranges

```bash
# Create network with custom subnet
docker network create \
  --driver bridge \
  --subnet 172.25.0.0/16 \
  --gateway 172.25.0.1 \
  --ip-range 172.25.5.0/24 \
  custom-net

# Assign specific IPs to containers
docker run -d \
  --name web \
  --network custom-net \
  --ip 172.25.5.10 \
  nginx

docker run -d \
  --name api \
  --network custom-net \
  --ip 172.25.5.11 \
  nginx

# Verify IPs
docker inspect web --format='{{.NetworkSettings.Networks.custom_net.IPAddress}}'
docker inspect api --format='{{.NetworkSettings.Networks.custom_net.IPAddress}}'
```

### Step 4.2: Multiple Networks per Container

```bash
# Create two networks
docker network create net-a
docker network create net-b

# Run container on net-a
docker run -d --name app --network net-a nginx

# Connect to net-b as well
docker network connect net-b app

# Now container has IPs on both networks
docker inspect app --format='{{json .NetworkSettings.Networks}}' | python -m json.tool

# Container can reach services on either network!
```

### Step 4.3: Network Aliases

```bash
docker network create multi-alias

# Run container with multiple aliases
docker run -d \
  --name web \
  --network multi-alias \
  --network-alias webserver \
  --network-alias api \
  --network-alias frontend \
  nginx

# All these DNS names resolve to same container:
docker run --rm --network multi-alias alpine nslookup webserver
docker run --rm --network multi-alias alpine nslookup api
docker run --rm --network multi-alias alpine nslookup frontend
```

✅ **Checkpoint**: You can configure advanced network settings.

---

## Part 5: Container Communication Patterns

### Step 5.1: Request-Response Pattern

```bash
mkdir -p ~/docker-exercises/communication
cd ~/docker-exercises/communication

# Service A (client)
cat > client.py << 'EOF'
import requests
import time

while True:
    try:
        response = requests.get('http://server:5000/data')
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
    time.sleep(5)
EOF

# Service B (server)
cat > server.py << 'EOF'
from flask import Flask, jsonify
import random

app = Flask(__name__)

@app.route('/data')
def data():
    return jsonify({
        'value': random.randint(1, 100),
        'timestamp': 'now'
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
EOF
```

```yaml
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  client:
    image: python:3.11-slim
    command: sh -c "pip install requests && python /app/client.py"
    volumes:
      - ./client.py:/app/client.py
    depends_on:
      - server

  server:
    image: python:3.11-slim
    command: sh -c "pip install flask && python /app/server.py"
    volumes:
      - ./server.py:/app/server.py
EOF
```

### Step 5.2: Publish-Subscribe Pattern

```bash
# Publisher
cat > publisher.py << 'EOF'
import redis
import time
import json

r = redis.Redis(host='redis', decode_responses=True)

counter = 0
while True:
    message = {'id': counter, 'data': f'Message {counter}'}
    r.publish('events', json.dumps(message))
    print(f"Published: {message}")
    counter += 1
    time.sleep(2)
EOF

# Subscriber
cat > subscriber.py << 'EOF'
import redis
import json

r = redis.Redis(host='redis', decode_responses=True)
pubsub = r.pubsub()
pubsub.subscribe('events')

print("Waiting for messages...")
for message in pubsub.listen():
    if message['type'] == 'message':
        data = json.loads(message['data'])
        print(f"Received: {data}")
EOF
```

```yaml
cat > docker-compose-pubsub.yml << 'EOF'
version: '3.8'

services:
  redis:
    image: redis:7-alpine

  publisher:
    image: python:3.11-slim
    command: sh -c "pip install redis && python /app/publisher.py"
    volumes:
      - ./publisher.py:/app/publisher.py
    depends_on:
      - redis

  subscriber1:
    image: python:3.11-slim
    command: sh -c "pip install redis && python /app/subscriber.py"
    volumes:
      - ./subscriber.py:/app/subscriber.py
    depends_on:
      - redis

  subscriber2:
    image: python:3.11-slim
    command: sh -c "pip install redis && python /app/subscriber.py"
    volumes:
      - ./subscriber.py:/app/subscriber.py
    depends_on:
      - redis
EOF
```

```bash
docker compose -f docker-compose-pubsub.yml up
```

### Step 5.3: Service Mesh Pattern (Envoy Proxy)

```yaml
cat > docker-compose-mesh.yml << 'EOF'
version: '3.8'

services:
  # Service with sidecar proxy
  app:
    build: .
    networks:
      - mesh

  # Envoy sidecar
  envoy-proxy:
    image: envoyproxy/envoy:v1.28-latest
    volumes:
      - ./envoy.yaml:/etc/envoy/envoy.yaml
    networks:
      - mesh
    command: /usr/local/bin/envoy -c /etc/envoy/envoy.yaml

  # Another service
  api:
    build: ./api
    networks:
      - mesh

  # Its sidecar
  envoy-api:
    image: envoyproxy/envoy:v1.28-latest
    volumes:
      - ./envoy-api.yaml:/etc/envoy/envoy.yaml
    networks:
      - mesh

networks:
  mesh:
    driver: bridge
EOF
```

✅ **Checkpoint**: You understand container communication patterns.

---

## Part 6: Load Balancing and High Availability

### Step 6.1: Nginx Load Balancer

```bash
mkdir -p ~/docker-exercises/load-balancing
cd ~/docker-exercises/load-balancing

# Backend application
cat > app.py << 'EOF'
from flask import Flask, jsonify
import socket
import os

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        'server': socket.gethostname(),
        'ip': socket.gethostbyname(socket.gethostname())
    })

@app.route('/health')
def health():
    return jsonify({'status': 'healthy'})

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
RUN pip install -r requirements.txt
COPY app.py .
CMD ["python", "app.py"]
EOF

# Nginx config with load balancing
mkdir -p nginx
cat > nginx/nginx.conf << 'EOF'
upstream backend {
    least_conn;  # Load balancing algorithm

    # Health check configuration
    server backend1:5000 max_fails=3 fail_timeout=30s;
    server backend2:5000 max_fails=3 fail_timeout=30s;
    server backend3:5000 max_fails=3 fail_timeout=30s;
}

server {
    listen 80;

    location / {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

        # Retry on failure
        proxy_next_upstream error timeout http_502 http_503 http_504;
    }

    location /health {
        access_log off;
        proxy_pass http://backend/health;
    }
}
EOF
```

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
      - backend1
      - backend2
      - backend3
    networks:
      - loadbalancer

  backend1:
    build: .
    networks:
      - loadbalancer

  backend2:
    build: .
    networks:
      - loadbalancer

  backend3:
    build: .
    networks:
      - loadbalancer

networks:
  loadbalancer:
    driver: bridge
EOF
```

```bash
# Start the stack
docker compose up -d

# Test load balancing - see different servers
for i in {1..10}; do
  curl -s http://localhost/ | grep server
  sleep 0.5
done

# Simulate failure
docker compose stop backend2

# Requests still work (distributed to healthy backends)
for i in {1..5}; do
  curl -s http://localhost/ | grep server
done

# Bring it back
docker compose start backend2
```

### Step 6.2: HAProxy Load Balancer

```bash
# HAProxy configuration
cat > haproxy.cfg << 'EOF'
global
    log stdout format raw local0
    maxconn 4096

defaults
    log     global
    mode    http
    option  httplog
    option  dontlognull
    timeout connect 5000ms
    timeout client  50000ms
    timeout server  50000ms

frontend http_front
    bind *:80
    default_backend http_back

backend http_back
    balance roundrobin
    option httpchk GET /health
    http-check expect status 200

    server backend1 backend1:5000 check
    server backend2 backend2:5000 check
    server backend3 backend3:5000 check

listen stats
    bind *:8080
    stats enable
    stats uri /stats
    stats refresh 10s
EOF
```

```yaml
cat > docker-compose-haproxy.yml << 'EOF'
version: '3.8'

services:
  haproxy:
    image: haproxy:2.8-alpine
    ports:
      - "80:80"
      - "8080:8080"  # Stats page
    volumes:
      - ./haproxy.cfg:/usr/local/etc/haproxy/haproxy.cfg
    depends_on:
      - backend1
      - backend2
      - backend3

  backend1:
    build: .

  backend2:
    build: .

  backend3:
    build: .
EOF
```

```bash
# Start with HAProxy
docker compose -f docker-compose-haproxy.yml up -d

# Test
for i in {1..10}; do curl -s http://localhost/ | grep server; done

# View stats
open http://localhost:8080/stats
```

✅ **Checkpoint**: You can configure load balancing with health checks.

---

## Part 7: External Connectivity

### Step 7.1: Port Publishing Modes

```bash
# Bind to all interfaces
docker run -d -p 8080:80 --name web-all nginx

# Bind to specific interface (localhost only)
docker run -d -p 127.0.0.1:8081:80 --name web-local nginx

# Random port assignment
docker run -d -p 80 --name web-random nginx
docker port web-random

# Multiple port mappings
docker run -d \
  -p 8082:80 \
  -p 8443:443 \
  --name web-multi \
  nginx

# Check published ports
docker port web-multi
```

### Step 7.2: Exposing Services

```yaml
cat > docker-compose-expose.yml << 'EOF'
version: '3.8'

services:
  # Exposed externally
  web:
    image: nginx
    ports:
      - "8080:80"  # host:container

  # Not exposed externally (only internal)
  api:
    image: nginx
    expose:
      - "80"  # Visible to other services, not host

  # Internal service
  db:
    image: postgres:15
    environment:
      - POSTGRES_PASSWORD=secret
    # No ports or expose - completely internal
EOF
```

### Step 7.3: Host Network Access

```bash
# Container accessing host services
docker run --rm \
  --add-host host.docker.internal:host-gateway \
  alpine ping -c 3 host.docker.internal

# Useful for accessing host's services from container
```

✅ **Checkpoint**: You understand external connectivity patterns.

---

## Part 8: Network Debugging and Troubleshooting

### Step 8.1: Network Inspection Tools

```bash
# List all networks
docker network ls

# Inspect network details
docker network inspect bridge

# See which containers are on a network
docker network inspect my-network \
  --format='{{range .Containers}}{{.Name}} {{end}}'

# Container's network settings
docker inspect container-name \
  --format='{{json .NetworkSettings}}' | python -m json.tool
```

### Step 8.2: Connectivity Testing

```bash
# Create test network
docker network create test-net

# Run test containers
docker run -d --name server --network test-net nginx
docker run -d --name client --network test-net alpine sleep 3600

# Test DNS resolution
docker exec client nslookup server

# Test connectivity
docker exec client ping -c 3 server

# Test port connectivity
docker exec client nc -zv server 80

# HTTP test
docker exec client wget -qO- http://server

# Install debugging tools
docker exec client apk add --no-cache curl tcpdump bind-tools

# Advanced debugging
docker exec client tcpdump -i eth0 -n
```

### Step 8.3: Common Issues and Solutions

```bash
# Issue 1: DNS not working
# Solution: Use custom bridge network (not default bridge)

# Issue 2: Can't connect to container
# Check if on same network
docker inspect container1 --format='{{json .NetworkSettings.Networks}}'
docker inspect container2 --format='{{json .NetworkSettings.Networks}}'

# Issue 3: Port already in use
# Check what's using the port
docker ps -a
netstat -tlnp | grep :8080

# Issue 4: Network cleanup
docker network prune

# Issue 5: Container can't reach internet
# Check Docker daemon DNS settings
cat /etc/docker/daemon.json
# Add: {"dns": ["8.8.8.8", "8.8.4.4"]}
```

### Step 8.4: Network Monitoring

```bash
# Real-time network stats
docker stats

# Network traffic with tcpdump
docker run --rm --net=host \
  nicolaka/netshoot \
  tcpdump -i any port 80

# Network diagnostic container
docker run -it --rm \
  --network container:target-container \
  nicolaka/netshoot

# Inside netshoot, you have:
# - ping, nslookup, dig
# - curl, wget
# - tcpdump, iperf
# - netstat, ss
```

✅ **Checkpoint**: You can debug and troubleshoot network issues.

---

## Part 9: ML Infrastructure Networking

### Step 9.1: Distributed Training Network

```yaml
cat > docker-compose-training.yml << 'EOF'
version: '3.8'

services:
  # Master node
  master:
    image: pytorch/pytorch:2.0.1-cuda11.7-cudnn8-runtime
    command: python train.py --role master --rank 0
    volumes:
      - ./train.py:/workspace/train.py
      - model-data:/models
    networks:
      training-net:
        aliases:
          - master-node
    environment:
      - MASTER_ADDR=master-node
      - MASTER_PORT=29500
      - WORLD_SIZE=3

  # Worker nodes
  worker1:
    image: pytorch/pytorch:2.0.1-cuda11.7-cudnn8-runtime
    command: python train.py --role worker --rank 1
    volumes:
      - ./train.py:/workspace/train.py
      - model-data:/models
    networks:
      - training-net
    environment:
      - MASTER_ADDR=master-node
      - MASTER_PORT=29500
      - WORLD_SIZE=3
    depends_on:
      - master

  worker2:
    image: pytorch/pytorch:2.0.1-cuda11.7-cudnn8-runtime
    command: python train.py --role worker --rank 2
    volumes:
      - ./train.py:/workspace/train.py
      - model-data:/models
    networks:
      - training-net
    environment:
      - MASTER_ADDR=master-node
      - MASTER_PORT=29500
      - WORLD_SIZE=3
    depends_on:
      - master

networks:
  training-net:
    driver: bridge
    ipam:
      config:
        - subnet: 172.28.0.0/16

volumes:
  model-data:
EOF
```

### Step 9.2: Model Serving with A/B Testing

```yaml
cat > docker-compose-ab-testing.yml << 'EOF'
version: '3.8'

services:
  # Load balancer with A/B routing
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx-ab.conf:/etc/nginx/conf.d/default.conf
    networks:
      - serving-net

  # Model version A (80% traffic)
  model-v1:
    build:
      context: .
      args:
        MODEL_VERSION: v1
    deploy:
      replicas: 4
    networks:
      serving-net:
        aliases:
          - model-a

  # Model version B (20% traffic)
  model-v2:
    build:
      context: .
      args:
        MODEL_VERSION: v2
    deploy:
      replicas: 1
    networks:
      serving-net:
        aliases:
          - model-b

  # Metrics collection
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    networks:
      - serving-net

networks:
  serving-net:
    driver: bridge
EOF
```

**Nginx A/B Config**:
```nginx
# nginx-ab.conf
split_clients "${remote_addr}" $backend {
    80%     model-a;
    20%     model-b;
}

upstream model-a {
    server model-v1:8000;
}

upstream model-b {
    server model-v2:8000;
}

server {
    listen 80;
    location / {
        proxy_pass http://$backend;
    }
}
```

### Step 9.3: Feature Store Architecture

```yaml
cat > docker-compose-features.yml << 'EOF'
version: '3.8'

services:
  # Online feature serving
  feature-server:
    build: ./feature-server
    networks:
      - online-tier
      - cache-tier
    depends_on:
      - redis
      - postgres

  # Fast cache layer
  redis:
    image: redis:7-alpine
    networks:
      - cache-tier

  # Feature database
  postgres:
    image: postgres:15
    networks:
      - cache-tier
      - storage-tier
    volumes:
      - features-db:/var/lib/postgresql/data

  # Offline feature computation
  spark-master:
    image: bitnami/spark:3.4
    networks:
      - storage-tier
      - compute-tier
    environment:
      - SPARK_MODE=master

  spark-worker:
    image: bitnami/spark:3.4
    networks:
      - compute-tier
    environment:
      - SPARK_MODE=worker
      - SPARK_MASTER_URL=spark://spark-master:7077
    deploy:
      replicas: 2

networks:
  online-tier:     # API access
  cache-tier:      # Fast feature access
  storage-tier:    # Persistent storage
  compute-tier:    # Batch processing

volumes:
  features-db:
EOF
```

✅ **Checkpoint**: You can design ML infrastructure networks.

---

## Part 10: Production Networking Patterns

### Step 10.1: Zero-Downtime Deployments

```yaml
cat > docker-compose-rolling.yml << 'EOF'
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx-rolling.conf:/etc/nginx/conf.d/default.conf
    depends_on:
      - app-blue
      - app-green

  # Blue deployment (current)
  app-blue:
    build: .
    environment:
      - VERSION=blue
    networks:
      - app-net
    deploy:
      replicas: 3

  # Green deployment (new version)
  app-green:
    build: .
    environment:
      - VERSION=green
    networks:
      - app-net
    deploy:
      replicas: 3

networks:
  app-net:
EOF
```

### Step 10.2: Circuit Breaker Pattern

```python
# circuit_breaker.py
cat > circuit_breaker.py << 'EOF'
import requests
import time
from enum import Enum

class CircuitState(Enum):
    CLOSED = 1   # Normal operation
    OPEN = 2     # Failures detected, blocking requests
    HALF_OPEN = 3  # Testing if service recovered

class CircuitBreaker:
    def __init__(self, failure_threshold=5, timeout=60):
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.state = CircuitState.CLOSED
        self.last_failure_time = None

    def call(self, url):
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time > self.timeout:
                self.state = CircuitState.HALF_OPEN
            else:
                raise Exception("Circuit breaker is OPEN")

        try:
            response = requests.get(url, timeout=2)
            response.raise_for_status()

            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.CLOSED
                self.failure_count = 0

            return response

        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()

            if self.failure_count >= self.failure_threshold:
                self.state = CircuitState.OPEN

            raise e

# Usage
breaker = CircuitBreaker()
try:
    response = breaker.call('http://api:5000/data')
except Exception as e:
    print(f"Service unavailable: {e}")
EOF
```

### Step 10.3: Service Mesh with Istio (Conceptual)

```yaml
# Istio would handle:
# - Service-to-service encryption (mTLS)
# - Traffic management (routing, retries, timeouts)
# - Observability (metrics, logs, traces)
# - Circuit breaking and fault injection

# Example service with Istio sidecar pattern
cat > docker-compose-sidecar.yml << 'EOF'
version: '3.8'

services:
  app:
    build: .
    networks:
      - mesh

  # Envoy sidecar proxy
  envoy:
    image: envoyproxy/envoy:v1.28-latest
    volumes:
      - ./envoy-config.yaml:/etc/envoy/envoy.yaml
    networks:
      - mesh
    # All traffic goes through Envoy

networks:
  mesh:
EOF
```

✅ **Checkpoint**: You understand production networking patterns.

---

## Practical Challenges

### Challenge 1: Secure Multi-Tier Application

**Requirements**:
- 3-tier architecture (web, api, database)
- Network isolation between tiers
- Only necessary connections allowed
- No database internet access
- Load balancing on API tier

### Challenge 2: Microservices Communication

**Requirements**:
- 5 microservices
- Service discovery
- One service accessible publicly
- Internal service mesh
- Health checks and circuit breakers

### Challenge 3: ML Pipeline Network

**Requirements**:
- Training cluster (master + workers)
- Feature store (online + offline)
- Model serving (A/B testing)
- Monitoring and logging
- Proper network segmentation

---

## Summary

**What You Accomplished**:
✅ Mastered Docker network drivers (bridge, host, overlay, none)
✅ Implemented service discovery and DNS resolution
✅ Created network isolation for security
✅ Configured custom networks with specific IP ranges
✅ Implemented load balancing with health checks
✅ Debugged network connectivity issues
✅ Designed ML infrastructure networks
✅ Applied production networking patterns

**Key Networking Concepts**:
- Bridge networks and DNS
- Network isolation and security
- Load balancing algorithms
- Service discovery patterns
- Circuit breakers and resilience
- Network troubleshooting
- Production-ready architectures

---

## Next Steps

**Continue Learning**:
- **Exercise 05**: Volume Management and Data Persistence
- **Exercise 06**: Production Deployment Strategies
- **Exercise 07**: Complete ML Application Containerization

---

**Exercise Version**: 1.0
**Last Updated**: October 2025
**Estimated Time**: 3-4 hours
**Difficulty**: Intermediate to Advanced
