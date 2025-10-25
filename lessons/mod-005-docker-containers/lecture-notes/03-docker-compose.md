# Lecture 03: Docker Compose

## Learning Objectives

By the end of this lecture, you will be able to:

- Understand what Docker Compose is and when to use it
- Write docker-compose.yml files
- Define multi-container applications
- Manage service dependencies and networking
- Use environment variables and volumes in Compose
- Run and manage multi-container applications
- Use Compose for development workflows
- Build ML application stacks with Compose

**Duration**: 120 minutes
**Difficulty**: Intermediate
**Prerequisites**: Lectures 01-02 (Docker Fundamentals, Dockerfiles)

---

## 1. Introduction to Docker Compose

### What is Docker Compose?

**Docker Compose** is a tool for defining and running multi-container Docker applications using a YAML configuration file.

**Without Compose** (manual, error-prone):
```bash
# Start database
docker run -d --name db -e POSTGRES_PASSWORD=secret postgres:15

# Create network
docker network create myapp-network

# Connect database to network
docker network connect myapp-network db

# Build and run web app
docker build -t myapp .
docker run -d --name web -p 8000:8000 --network myapp-network \
  -e DATABASE_URL=postgresql://db:5432 myapp

# Start redis cache
docker run -d --name redis --network myapp-network redis:7

# If anything fails... manual cleanup nightmare!
```

**With Compose** (declarative, simple):
```yaml
# docker-compose.yml
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_PASSWORD: secret

  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://db:5432
    depends_on:
      - db

  redis:
    image: redis:7
```

```bash
# Start everything
docker-compose up

# Stop everything
docker-compose down
```

### Why Use Docker Compose?

✅ **Simplicity**: One command to start entire stack
✅ **Declarative**: Define desired state, not steps
✅ **Reproducible**: Same environment every time
✅ **Version Control**: Store compose file in Git
✅ **Development**: Quick local environment setup
✅ **Testing**: Spin up test environments easily

### When to Use Docker Compose

**Perfect for:**
- 🎯 Local development environments
- 🎯 Testing and CI/CD
- 🎯 Small production deployments (single host)
- 🎯 Prototyping microservices

**Not ideal for:**
- ❌ Large-scale production (use Kubernetes)
- ❌ Multi-host deployments (use Swarm/K8s)
- ❌ Complex orchestration needs

---

## 2. Docker Compose File Structure

### Basic Structure

```yaml
version: '3.8'  # Compose file format version

services:       # Define containers
  service1:
    # Service configuration

  service2:
    # Service configuration

networks:       # Optional: custom networks
  mynetwork:

volumes:        # Optional: named volumes
  myvolume:
```

### Version Numbers

```yaml
# Modern (recommended)
version: '3.8'

# Older versions
version: '3.7'
version: '3.6'
version: '2'

# Version determines available features
# Use '3.8' or later for latest features
```

### Service Definition

```yaml
services:
  webapp:
    image: nginx:latest           # Use existing image
    # OR
    build: ./webapp               # Build from Dockerfile

    container_name: my-webapp     # Optional: custom name

    ports:                        # Port mapping
      - "8080:80"

    environment:                  # Environment variables
      ENV_VAR: value

    volumes:                      # Volume mounts
      - ./data:/data

    networks:                     # Networks
      - frontend

    depends_on:                   # Dependencies
      - database

    restart: unless-stopped       # Restart policy
```

---

## 3. Defining Services

### Using Existing Images

```yaml
services:
  # PostgreSQL database
  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: myuser
      POSTGRES_PASSWORD: mypassword
      POSTGRES_DB: mydb
    volumes:
      - postgres_data:/var/lib/postgresql/data

  # Redis cache
  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

### Building from Dockerfile

```yaml
services:
  web:
    build:
      context: ./webapp           # Directory with Dockerfile
      dockerfile: Dockerfile      # Dockerfile name (optional)
      args:                       # Build arguments
        VERSION: "1.0"
    image: myapp:latest           # Tag built image
```

**Advanced build options**:
```yaml
services:
  web:
    build:
      context: .
      dockerfile: Dockerfile.prod
      args:
        BUILD_ENV: production
      target: production          # Multi-stage build target
      cache_from:
        - myapp:latest
```

### Port Mapping

```yaml
services:
  web:
    image: nginx
    ports:
      # Short syntax
      - "8080:80"                 # host:container
      - "443:443"

      # Long syntax
      - target: 80                # Container port
        published: 8080           # Host port
        protocol: tcp
        mode: host
```

### Environment Variables

**Method 1: Direct definition**:
```yaml
services:
  web:
    environment:
      DEBUG: "true"
      DATABASE_URL: "postgresql://db:5432/mydb"
      API_KEY: "secret-key"
```

**Method 2: Environment file**:
```yaml
# docker-compose.yml
services:
  web:
    env_file:
      - .env
      - .env.production
```

```bash
# .env
DEBUG=true
DATABASE_URL=postgresql://db:5432/mydb
API_KEY=secret-key
```

**Method 3: Shell environment**:
```yaml
services:
  web:
    environment:
      API_KEY: ${API_KEY}         # Use $API_KEY from shell
```

---

## 4. Networking in Compose

### Default Networking

Docker Compose automatically creates a network:

```yaml
services:
  web:
    image: nginx

  api:
    image: myapi
```

**Result**:
- Network created: `myapp_default`
- Services can reach each other by service name
- `web` can access `api` at hostname `api`

### Service Discovery

```yaml
services:
  web:
    image: nginx
    # Can connect to: http://api:8000

  api:
    image: python:3.11
    # Can connect to: http://db:5432

  db:
    image: postgres:15
```

**Automatic DNS resolution**:
- Service name = hostname
- `ping api` works from `web` container
- `ping db` works from `api` container

### Custom Networks

```yaml
services:
  frontend:
    image: nginx
    networks:
      - frontend_net

  backend:
    image: myapi
    networks:
      - frontend_net
      - backend_net

  database:
    image: postgres
    networks:
      - backend_net

networks:
  frontend_net:
    driver: bridge
  backend_net:
    driver: bridge
```

**Network isolation**:
```
frontend ←→ backend ←→ database
(frontend_net)   (backend_net)

frontend CANNOT reach database directly!
```

---

## 5. Volumes and Data Persistence

### Named Volumes

```yaml
services:
  db:
    image: postgres:15
    volumes:
      - db_data:/var/lib/postgresql/data

volumes:
  db_data:                        # Named volume
```

**Docker manages the volume location**:
```bash
docker volume ls
# DRIVER    VOLUME NAME
# local     myapp_db_data
```

### Bind Mounts

```yaml
services:
  web:
    image: nginx
    volumes:
      # Bind mount (absolute or relative path)
      - ./html:/usr/share/nginx/html
      - ./nginx.conf:/etc/nginx/nginx.conf:ro  # Read-only
```

**Use cases**:
- ✅ Development: Live code reloading
- ✅ Configuration files
- ⚠️ Production: Use named volumes instead

### Volume Syntax

```yaml
services:
  app:
    volumes:
      # Short syntax
      - /host/path:/container/path
      - named_volume:/container/path

      # Long syntax
      - type: bind
        source: ./local/path
        target: /container/path
        read_only: true

      - type: volume
        source: named_volume
        target: /container/path
        volume:
          nocopy: true

volumes:
  named_volume:
```

---

## 6. Service Dependencies

### depends_on

```yaml
services:
  web:
    image: myapp
    depends_on:
      - db
      - redis

  db:
    image: postgres:15

  redis:
    image: redis:7
```

**What depends_on does**:
- ✅ Controls startup order: db → redis → web
- ❌ Does NOT wait for service to be "ready"

### Health Checks

```yaml
services:
  db:
    image: postgres:15
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  web:
    image: myapp
    depends_on:
      db:
        condition: service_healthy    # Wait for health check
```

**Health check conditions**:
- `service_started`: Just started (default)
- `service_healthy`: Health check passed
- `service_completed_successfully`: For one-off tasks

### Init Containers Pattern

```yaml
services:
  db-init:
    image: postgres:15
    command: |
      psql -c "CREATE DATABASE mydb;"
    depends_on:
      - db
    restart: "no"                     # Run once

  web:
    image: myapp
    depends_on:
      db-init:
        condition: service_completed_successfully
```

---

## 7. Complete Application Examples

### Example 1: Web App with Database

```yaml
version: '3.8'

services:
  # PostgreSQL database
  db:
    image: postgres:15
    environment:
      POSTGRES_USER: appuser
      POSTGRES_PASSWORD: apppass
      POSTGRES_DB: appdb
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U appuser"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Flask web application
  web:
    build: ./webapp
    ports:
      - "5000:5000"
    environment:
      DATABASE_URL: postgresql://appuser:apppass@db:5432/appdb
      FLASK_ENV: development
    volumes:
      - ./webapp:/app              # Live reload
    depends_on:
      db:
        condition: service_healthy
    restart: unless-stopped

volumes:
  postgres_data:
```

### Example 2: Microservices Architecture

```yaml
version: '3.8'

services:
  # Frontend
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      API_URL: http://api:8000
    depends_on:
      - api

  # API Gateway
  api:
    build: ./api
    ports:
      - "8000:8000"
    environment:
      AUTH_SERVICE_URL: http://auth:8001
      USER_SERVICE_URL: http://users:8002
    depends_on:
      - auth
      - users
      - redis

  # Auth Service
  auth:
    build: ./services/auth
    environment:
      JWT_SECRET: ${JWT_SECRET}
      DB_URL: postgresql://db:5432/auth
    depends_on:
      - db

  # User Service
  users:
    build: ./services/users
    environment:
      DB_URL: postgresql://db:5432/users
    depends_on:
      - db

  # Shared Database
  db:
    image: postgres:15
    environment:
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - db_data:/var/lib/postgresql/data

  # Redis Cache
  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

volumes:
  db_data:
  redis_data:
```

### Example 3: ML Model Serving

```yaml
version: '3.8'

services:
  # Model API
  model-api:
    build: ./model-serving
    ports:
      - "8080:8080"
    environment:
      MODEL_PATH: /models/model.pt
      REDIS_URL: redis://redis:6379
    volumes:
      - ./models:/models:ro         # Read-only model files
    depends_on:
      - redis
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]    # GPU support

  # Redis for caching predictions
  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

  # Monitoring
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus

  # Visualization
  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      GF_SECURITY_ADMIN_PASSWORD: ${GRAFANA_PASSWORD}
    volumes:
      - grafana_data:/var/lib/grafana
    depends_on:
      - prometheus

volumes:
  redis_data:
  prometheus_data:
  grafana_data:
```

---

## 8. Docker Compose Commands

### Starting Services

```bash
# Start all services in foreground
docker-compose up

# Start in background (detached)
docker-compose up -d

# Start specific services
docker-compose up web db

# Rebuild images before starting
docker-compose up --build

# Force recreate containers
docker-compose up --force-recreate

# Scale services
docker-compose up --scale web=3
```

### Stopping Services

```bash
# Stop services (containers remain)
docker-compose stop

# Stop specific service
docker-compose stop web

# Stop and remove containers
docker-compose down

# Remove volumes too
docker-compose down -v

# Remove images too
docker-compose down --rmi all
```

### Viewing Status

```bash
# List running services
docker-compose ps

# View logs
docker-compose logs

# Follow logs
docker-compose logs -f

# Logs for specific service
docker-compose logs -f web

# Last 100 lines
docker-compose logs --tail=100

# View resource usage
docker-compose top
```

### Executing Commands

```bash
# Run command in service
docker-compose exec web bash

# Run one-off command
docker-compose run web python manage.py migrate

# Without starting dependencies
docker-compose run --no-deps web python manage.py test
```

### Building and Managing

```bash
# Build/rebuild services
docker-compose build

# Build specific service
docker-compose build web

# Build without cache
docker-compose build --no-cache

# Pull images
docker-compose pull

# Push images
docker-compose push

# Validate compose file
docker-compose config

# View config with variables resolved
docker-compose config --resolve-image-digests
```

---

## 9. Development Workflows

### Development Compose File

```yaml
# docker-compose.yml (base)
version: '3.8'

services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      DATABASE_URL: postgresql://db:5432/appdb
```

```yaml
# docker-compose.override.yml (auto-loaded in dev)
version: '3.8'

services:
  web:
    volumes:
      - ./src:/app/src              # Live reload
    environment:
      DEBUG: "true"
      FLASK_ENV: development
    command: flask run --reload     # Auto-reload on changes
```

**Usage**:
```bash
# Automatically uses both files
docker-compose up

# Equivalent to:
docker-compose -f docker-compose.yml -f docker-compose.override.yml up
```

### Production Compose File

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  web:
    image: myapp:1.0.0              # Use built image
    environment:
      FLASK_ENV: production
    restart: always
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
```

**Usage**:
```bash
# Use production config
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Hot Reloading for Development

```yaml
services:
  # Python/Flask
  flask-app:
    build: .
    volumes:
      - ./app:/app                  # Sync code
    environment:
      FLASK_DEBUG: "1"
    command: flask run --reload --host=0.0.0.0

  # Node.js
  node-app:
    build: .
    volumes:
      - ./src:/app/src
      - /app/node_modules           # Don't override node_modules
    environment:
      NODE_ENV: development
    command: npm run dev
```

---

## 10. Best Practices

### 1. Use Environment Variables

```yaml
# docker-compose.yml
services:
  web:
    environment:
      SECRET_KEY: ${SECRET_KEY}
      DB_PASSWORD: ${DB_PASSWORD}
```

```bash
# .env
SECRET_KEY=your-secret-key
DB_PASSWORD=secure-password
```

**Never commit secrets to Git!**

### 2. Health Checks

```yaml
services:
  api:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

### 3. Resource Limits

```yaml
services:
  web:
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
```

### 4. Restart Policies

```yaml
services:
  web:
    restart: unless-stopped        # Recommended for production
    # Options: no, always, on-failure, unless-stopped
```

### 5. Named Volumes

```yaml
# Good: Named volumes
volumes:
  postgres_data:

# Avoid: Anonymous volumes
# volumes:
#   - /var/lib/postgresql/data
```

### 6. Network Segmentation

```yaml
services:
  frontend:
    networks:
      - public

  backend:
    networks:
      - public
      - private

  database:
    networks:
      - private           # Not exposed to frontend

networks:
  public:
  private:
    internal: true        # No external access
```

### 7. Version Control

```bash
# Commit to Git
git add docker-compose.yml
git add docker-compose.override.yml.example  # Template, not actual override
git add .env.example                          # Template, not actual .env

# .gitignore
docker-compose.override.yml
.env
```

---

## 11. Troubleshooting

### Common Issues

**Issue 1: Port already in use**
```bash
# Error: port is already allocated

# Find what's using the port
sudo lsof -i :8080

# Change port in compose file
ports:
  - "8081:8080"  # Use different host port
```

**Issue 2: Service not starting**
```bash
# Check logs
docker-compose logs service-name

# Check service status
docker-compose ps

# Inspect container
docker-compose exec service-name bash
```

**Issue 3: Network connectivity**
```bash
# Test connectivity between services
docker-compose exec web ping db

# Check networks
docker network ls
docker network inspect myapp_default
```

**Issue 4: Volume permissions**
```bash
# Fix permissions
docker-compose exec web chown -R appuser:appuser /app/data

# Or in Dockerfile
RUN chown -R appuser:appuser /app
USER appuser
```

### Debugging Commands

```bash
# Validate compose file
docker-compose config

# View resolved config
docker-compose config --services

# Check environment variables
docker-compose config --environment

# Remove everything and start fresh
docker-compose down -v --remove-orphans
docker-compose up --build --force-recreate
```

---

## Key Takeaways

✅ **Docker Compose** manages multi-container applications
✅ **docker-compose.yml** defines services declaratively
✅ **Services** can reference each other by name (DNS)
✅ **depends_on** controls startup order
✅ **volumes** provide data persistence
✅ **networks** enable service isolation
✅ **override files** customize for different environments
✅ **docker-compose up/down** manages lifecycle
✅ **Perfect for development**, okay for small production
✅ **Use Kubernetes** for large-scale production

---

## Quick Reference

### Essential Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Execute command
docker-compose exec service bash

# Rebuild
docker-compose up --build

# Scale service
docker-compose up --scale web=3
```

### Compose File Template

```yaml
version: '3.8'

services:
  app:
    build: .
    image: myapp:latest
    container_name: myapp
    ports:
      - "8000:8000"
    environment:
      ENV_VAR: value
    env_file:
      - .env
    volumes:
      - app_data:/data
    networks:
      - app_network
    depends_on:
      - db
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 5s
      retries: 3

  db:
    image: postgres:15
    volumes:
      - db_data:/var/lib/postgresql/data
    networks:
      - app_network

volumes:
  app_data:
  db_data:

networks:
  app_network:
    driver: bridge
```

---

## What's Next?

In the next lecture, we'll explore:
- **Docker Networking**: Deep dive into network types
- **Docker Volumes**: Advanced data management
- **Storage drivers** and performance
- **Network troubleshooting**

Continue to `lecture-notes/04-networking-volumes.md`

---

**Lecture Version**: 1.0
**Last Updated**: October 2025
**Estimated Time**: 120 minutes
**Difficulty**: Intermediate
