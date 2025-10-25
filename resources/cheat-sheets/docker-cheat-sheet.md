# Docker Cheat Sheet

Quick reference guide for essential Docker commands and concepts.

---

## Table of Contents

- [Basic Commands](#basic-commands)
- [Image Management](#image-management)
- [Container Management](#container-management)
- [Dockerfile Syntax](#dockerfile-syntax)
- [Docker Compose](#docker-compose)
- [Networking](#networking)
- [Volumes](#volumes)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)

---

## Basic Commands

### Version and Info
```bash
# Check Docker version
docker --version
docker version  # detailed version info

# Display system-wide information
docker info

# Get help
docker --help
docker <command> --help
```

### Images
```bash
# List images
docker images
docker image ls

# Pull an image
docker pull <image>:<tag>
docker pull python:3.9

# Remove an image
docker rmi <image-id>
docker image rm <image-id>

# Remove unused images
docker image prune
docker image prune -a  # remove all unused images
```

### Containers
```bash
# List running containers
docker ps
docker container ls

# List all containers (including stopped)
docker ps -a
docker container ls -a

# Run a container
docker run <image>
docker run -d <image>  # detached mode
docker run -it <image> bash  # interactive with bash

# Stop a container
docker stop <container-id>

# Start a stopped container
docker start <container-id>

# Remove a container
docker rm <container-id>

# Remove all stopped containers
docker container prune
```

---

## Image Management

### Building Images
```bash
# Build from Dockerfile in current directory
docker build -t <image-name>:<tag> .

# Build with specific Dockerfile
docker build -f Dockerfile.prod -t myapp:prod .

# Build with build arguments
docker build --build-arg VERSION=1.0 -t myapp:1.0 .

# Build with no cache
docker build --no-cache -t myapp:latest .
```

### Tagging Images
```bash
# Tag an image
docker tag <image-id> <repository>:<tag>
docker tag myapp:latest myuser/myapp:v1.0

# Push to registry
docker push myuser/myapp:v1.0

# Pull specific tag
docker pull myuser/myapp:v1.0
```

### Inspecting Images
```bash
# Display detailed information
docker inspect <image-id>

# View image history
docker history <image-id>

# Check image size
docker images --format "{{.Repository}}:{{.Tag}} - {{.Size}}"
```

---

## Container Management

### Running Containers

#### Basic Run
```bash
# Run container with name
docker run --name my-container nginx

# Run with port mapping
docker run -p 8080:80 nginx

# Run with environment variables
docker run -e "ENV=production" -e "DEBUG=false" myapp

# Run with volume mount
docker run -v /host/path:/container/path myapp

# Run with resource limits
docker run --memory="256m" --cpus="1.0" myapp
```

#### Advanced Options
```bash
# Run with restart policy
docker run --restart=always nginx
docker run --restart=on-failure:3 myapp  # restart max 3 times

# Run with custom network
docker run --network my-network myapp

# Run as specific user
docker run --user 1000:1000 myapp

# Run with working directory
docker run -w /app myapp

# Run with custom hostname
docker run --hostname my-host myapp
```

### Container Operations
```bash
# Execute command in running container
docker exec <container-id> <command>
docker exec -it <container-id> bash  # interactive bash

# View logs
docker logs <container-id>
docker logs -f <container-id>  # follow logs
docker logs --tail 100 <container-id>  # last 100 lines

# View container processes
docker top <container-id>

# View container resource usage
docker stats
docker stats <container-id>

# Copy files to/from container
docker cp <container-id>:/path/in/container /local/path
docker cp /local/path <container-id>:/path/in/container

# Inspect container
docker inspect <container-id>
```

### Container Lifecycle
```bash
# Stop container gracefully (SIGTERM then SIGKILL)
docker stop <container-id>

# Force stop (SIGKILL immediately)
docker kill <container-id>

# Pause container
docker pause <container-id>

# Unpause container
docker unpause <container-id>

# Restart container
docker restart <container-id>

# Rename container
docker rename <old-name> <new-name>
```

---

## Dockerfile Syntax

### Basic Structure
```dockerfile
# Base image
FROM python:3.9-slim

# Metadata
LABEL maintainer="you@example.com"
LABEL version="1.0"

# Set working directory
WORKDIR /app

# Copy files
COPY requirements.txt .
COPY . .

# Run commands
RUN apt-get update && apt-get install -y \
    package1 \
    package2 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    ENVIRONMENT=production

# Expose port
EXPOSE 8000

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser /app
USER appuser

# Define entrypoint and command
ENTRYPOINT ["python"]
CMD ["app.py"]
```

### Multi-Stage Builds
```dockerfile
# Build stage
FROM python:3.9 AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.9-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .
ENV PATH=/root/.local/bin:$PATH
CMD ["python", "app.py"]
```

### Common Instructions
```dockerfile
# ARG - Build-time variables
ARG VERSION=1.0
ARG BUILD_DATE

# ENV - Environment variables
ENV APP_HOME=/app \
    PORT=8000

# VOLUME - Mount point
VOLUME ["/data"]

# HEALTHCHECK
HEALTHCHECK --interval=30s --timeout=3s \
  CMD curl -f http://localhost:8000/health || exit 1

# ONBUILD - Trigger for child images
ONBUILD COPY . /app
```

---

## Docker Compose

### Basic Commands
```bash
# Start services
docker-compose up
docker-compose up -d  # detached mode

# Start specific services
docker-compose up service1 service2

# Stop services
docker-compose stop

# Stop and remove containers, networks
docker-compose down

# Stop and remove everything including volumes
docker-compose down -v

# View logs
docker-compose logs
docker-compose logs -f  # follow
docker-compose logs service1  # specific service

# List services
docker-compose ps

# Execute command in service
docker-compose exec service1 bash

# Build or rebuild services
docker-compose build
docker-compose build --no-cache

# Pull service images
docker-compose pull

# Validate docker-compose.yml
docker-compose config
```

### docker-compose.yml Structure
```yaml
version: '3.8'

services:
  web:
    build:
      context: .
      dockerfile: Dockerfile
      args:
        VERSION: "1.0"
    image: myapp:latest
    container_name: my-web-app
    ports:
      - "8000:8000"
    environment:
      - DEBUG=false
      - DATABASE_URL=postgresql://db:5432/mydb
    env_file:
      - .env
    volumes:
      - ./src:/app/src
      - app-data:/app/data
    networks:
      - app-network
    depends_on:
      - db
      - redis
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    command: python app.py

  db:
    image: postgres:13
    container_name: my-postgres
    environment:
      POSTGRES_DB: mydb
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    volumes:
      - postgres-data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    networks:
      - app-network
    ports:
      - "5432:5432"

  redis:
    image: redis:alpine
    networks:
      - app-network

volumes:
  app-data:
  postgres-data:

networks:
  app-network:
    driver: bridge
```

---

## Networking

### Network Commands
```bash
# List networks
docker network ls

# Create network
docker network create my-network
docker network create --driver bridge my-bridge

# Inspect network
docker network inspect my-network

# Connect container to network
docker network connect my-network <container-id>

# Disconnect container from network
docker network disconnect my-network <container-id>

# Remove network
docker network rm my-network

# Remove unused networks
docker network prune
```

### Network Drivers
- **bridge**: Default, isolated network on a single host
- **host**: Remove network isolation, use host's network
- **overlay**: Multi-host networking (Swarm)
- **macvlan**: Assign MAC address to container
- **none**: Disable networking

### DNS Resolution
```bash
# Containers can reach each other by name on custom networks
docker run --network my-network --name web nginx
docker run --network my-network alpine ping web
```

---

## Volumes

### Volume Commands
```bash
# List volumes
docker volume ls

# Create volume
docker volume create my-volume

# Inspect volume
docker volume inspect my-volume

# Remove volume
docker volume rm my-volume

# Remove unused volumes
docker volume prune
```

### Volume Types

#### Named Volumes
```bash
docker run -v my-volume:/data alpine
docker-compose:
  volumes:
    - my-volume:/data
```

#### Bind Mounts
```bash
docker run -v /host/path:/container/path alpine
docker-compose:
  volumes:
    - ./local:/app
```

#### Anonymous Volumes
```bash
docker run -v /data alpine
```

---

## Troubleshooting

### Debugging Containers

#### Container Won't Start
```bash
# Check logs
docker logs <container-id>

# Inspect container configuration
docker inspect <container-id>

# Try running interactively
docker run -it <image> bash

# Check if port is already in use
netstat -tulpn | grep <port>
```

#### Container Exits Immediately
```bash
# Check exit code
docker ps -a
docker inspect <container-id> | grep ExitCode

# Common exit codes:
# 0 - Success
# 1 - Application error
# 137 - SIGKILL (killed by system)
# 139 - Segmentation fault
# 143 - SIGTERM (graceful shutdown)
```

#### Network Issues
```bash
# Check container networking
docker exec <container-id> ping google.com
docker exec <container-id> nslookup google.com

# Check exposed ports
docker port <container-id>

# Inspect network
docker network inspect <network-name>
```

#### Performance Issues
```bash
# Check resource usage
docker stats <container-id>

# Check disk usage
docker system df

# Check logs size
docker inspect -f '{{.LogPath}}' <container-id>
# then: ls -lh /path/to/log
```

### Common Issues

**Issue**: "Permission denied"
```bash
# Solution 1: Run as root (not recommended)
docker run --user root <image>

# Solution 2: Fix ownership in Dockerfile
RUN chown -R appuser:appuser /app
USER appuser
```

**Issue**: "Cannot connect to Docker daemon"
```bash
# Solution: Start Docker service
sudo systemctl start docker

# Or add user to docker group
sudo usermod -aG docker $USER
# Log out and back in
```

**Issue**: "No space left on device"
```bash
# Clean up
docker system prune -a --volumes
```

---

## Best Practices

### Dockerfile Best Practices

1. **Use specific base image tags**
   ```dockerfile
   # Good
   FROM python:3.9-slim

   # Avoid
   FROM python:latest
   ```

2. **Minimize layers**
   ```dockerfile
   # Good
   RUN apt-get update && apt-get install -y \
       package1 \
       package2 \
       && rm -rf /var/lib/apt/lists/*

   # Avoid
   RUN apt-get update
   RUN apt-get install -y package1
   RUN apt-get install -y package2
   ```

3. **Order instructions by change frequency**
   ```dockerfile
   # Rarely changes
   FROM python:3.9-slim
   RUN apt-get update && apt-get install -y gcc

   # Sometimes changes
   COPY requirements.txt .
   RUN pip install -r requirements.txt

   # Frequently changes
   COPY . .
   ```

4. **Use .dockerignore**
   ```
   .git
   .env
   __pycache__
   *.pyc
   node_modules
   .venv
   ```

5. **Don't run as root**
   ```dockerfile
   RUN useradd -m -u 1000 appuser
   USER appuser
   ```

6. **Use COPY instead of ADD**
   ```dockerfile
   # Preferred
   COPY requirements.txt .

   # Only for tar extraction or URLs
   ADD archive.tar.gz /app
   ```

### Container Best Practices

1. **One process per container**
2. **Use environment variables for configuration**
3. **Implement health checks**
4. **Use restart policies appropriately**
5. **Tag images with semantic versioning**
6. **Keep containers ephemeral**
7. **Don't store data in containers (use volumes)**

### Security Best Practices

1. **Scan images for vulnerabilities**
   ```bash
   docker scan <image>
   ```

2. **Don't include secrets in images**
3. **Use secrets management**
4. **Keep base images updated**
5. **Limit container capabilities**
   ```bash
   docker run --cap-drop ALL --cap-add NET_BIND_SERVICE myapp
   ```

---

## Quick Reference

### Most Used Commands
```bash
# Build and run
docker build -t myapp .
docker run -d -p 8000:8000 --name myapp-container myapp

# View and debug
docker ps
docker logs -f myapp-container
docker exec -it myapp-container bash

# Clean up
docker stop myapp-container
docker rm myapp-container
docker rmi myapp
docker system prune -a
```

### Resource Limits
```bash
# Memory limit
docker run -m 512m myapp

# CPU limit
docker run --cpus="1.5" myapp

# Both
docker run -m 512m --cpus="1.5" myapp
```

### Docker Compose Quick Start
```bash
# Start everything
docker-compose up -d

# View logs
docker-compose logs -f

# Rebuild and restart
docker-compose up -d --build

# Stop everything
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

---

## Useful Aliases

Add these to your `~/.bashrc` or `~/.zshrc`:

```bash
# Docker
alias d='docker'
alias dps='docker ps'
alias dpsa='docker ps -a'
alias di='docker images'
alias dex='docker exec -it'
alias dlogs='docker logs -f'
alias dstop='docker stop $(docker ps -q)'
alias drm='docker rm $(docker ps -aq)'
alias drmi='docker rmi $(docker images -q)'

# Docker Compose
alias dc='docker-compose'
alias dcu='docker-compose up -d'
alias dcd='docker-compose down'
alias dcl='docker-compose logs -f'
alias dce='docker-compose exec'
alias dcb='docker-compose build'

# Cleanup
alias docker-clean='docker system prune -a --volumes'
```

---

## Additional Resources

- [Official Docker Documentation](https://docs.docker.com/)
- [Docker Hub](https://hub.docker.com/)
- [Play with Docker](https://labs.play-with-docker.com/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)

---

**Print this cheat sheet and keep it handy!**
