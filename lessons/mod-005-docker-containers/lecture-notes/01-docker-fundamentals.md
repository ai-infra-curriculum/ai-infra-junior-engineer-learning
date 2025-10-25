# Lecture 01: Docker Fundamentals

## Learning Objectives

By the end of this lecture, you will be able to:

- Understand what containers are and why they matter
- Explain how containers differ from virtual machines
- Understand Docker architecture and its components
- Install Docker on your system
- Run your first containers
- Use basic Docker commands confidently
- Understand the relationship between images and containers

**Duration**: 90 minutes
**Difficulty**: Beginner
**Prerequisites**: Module 002 (Linux Essentials)

---

## 1. Introduction to Containerization

### What Are Containers?

**Containers** are lightweight, standalone packages that contain everything needed to run a piece of software: code, runtime, system tools, libraries, and settings.

**Analogy**: Think of containers like shipping containers:
- Standardized format
- Portable across different systems
- Isolated from other containers
- Can be stacked and managed easily

```
Traditional Deployment:
┌─────────────────────────┐
│   Physical Server       │
│  ┌──────────────────┐  │
│  │  App A + Deps    │  │
│  │  App B + Deps    │  │  ← Dependencies conflict!
│  │  App C + Deps    │  │     Hard to manage!
│  └──────────────────┘  │
└─────────────────────────┘

Container Deployment:
┌─────────────────────────┐
│   Physical Server       │
│  ┌────┐ ┌────┐ ┌────┐  │
│  │App │ │App │ │App │  │
│  │ A  │ │ B  │ │ C  │  │  ← Isolated!
│  │+Dep│ │+Dep│ │+Dep│  │     Portable!
│  └────┘ └────┘ └────┘  │
└─────────────────────────┘
```

### Why Containers Matter

**For Infrastructure Engineers:**

1. **Consistency**: "Works on my machine" → "Works everywhere"
2. **Portability**: Move between dev, test, and production seamlessly
3. **Efficiency**: Faster startup than VMs, better resource utilization
4. **Isolation**: Applications don't interfere with each other
5. **Scalability**: Easy to replicate and scale horizontally
6. **Version Control**: Images can be versioned like code

**For AI/ML Infrastructure:**

- Package models with exact dependencies
- Consistent training environments
- Easy model serving deployment
- GPU resource management
- Reproducible research environments

---

## 2. Containers vs Virtual Machines

### Architecture Comparison

```
Virtual Machines:
┌─────────────────────────────────┐
│        Physical Server          │
│  ┌──────────────────────────┐  │
│  │      Hypervisor          │  │
│  └──────────────────────────┘  │
│  ┌────┐  ┌────┐  ┌────┐       │
│  │VM1 │  │VM2 │  │VM3 │       │
│  │OS  │  │OS  │  │OS  │       │  ← Each VM has full OS!
│  │App │  │App │  │App │       │     Heavy!
│  └────┘  └────┘  └────┘       │
└─────────────────────────────────┘

Containers:
┌─────────────────────────────────┐
│        Physical Server          │
│  ┌──────────────────────────┐  │
│  │        Host OS           │  │
│  └──────────────────────────┘  │
│  ┌──────────────────────────┐  │
│  │    Container Runtime     │  │
│  └──────────────────────────┘  │
│  ┌────┐  ┌────┐  ┌────┐       │
│  │C1  │  │C2  │  │C3  │       │  ← Share host OS kernel!
│  │App │  │App │  │App │       │     Lightweight!
│  └────┘  └────┘  └────┘       │
└─────────────────────────────────┘
```

### Comparison Table

| Aspect | Virtual Machines | Containers |
|--------|------------------|------------|
| **Startup Time** | Minutes | Seconds |
| **Size** | GBs | MBs |
| **Performance** | Slower (overhead) | Near-native |
| **Isolation** | Complete (hardware-level) | Process-level |
| **OS** | Each VM has full OS | Share host OS kernel |
| **Portability** | Limited | Highly portable |
| **Resource Usage** | Heavy | Lightweight |
| **Use Case** | Strong isolation needs | Microservices, CI/CD |

### When to Use What?

**Use VMs when:**
- Need different operating systems
- Require complete isolation (security)
- Running legacy applications
- Need hardware-level features

**Use Containers when:**
- Building microservices
- CI/CD pipelines
- Development environments
- Cloud-native applications
- ML model serving

**Best Practice**: Often use both! VMs for isolation, containers within VMs for efficiency.

---

## 3. Docker Architecture

### Overview

Docker uses a **client-server architecture**:

```
┌─────────────────────────────────────────────────┐
│                Docker Client                    │
│              (docker command)                   │
└────────────────────┬────────────────────────────┘
                     │ REST API
                     ↓
┌─────────────────────────────────────────────────┐
│              Docker Daemon                      │
│               (dockerd)                         │
│  ┌────────────────────────────────────────┐   │
│  │     Container Management               │   │
│  ├────────────────────────────────────────┤   │
│  │     Image Management                   │   │
│  ├────────────────────────────────────────┤   │
│  │     Volume Management                  │   │
│  ├────────────────────────────────────────┤   │
│  │     Network Management                 │   │
│  └────────────────────────────────────────┘   │
│                     │                          │
│                     ↓                          │
│              containerd                        │
│                     │                          │
│                     ↓                          │
│                  runc                          │
└─────────────────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────┐
│              Containers                         │
│    [Container 1] [Container 2] [Container 3]   │
└─────────────────────────────────────────────────┘
```

### Key Components

**1. Docker Client (`docker` CLI)**
- Command-line interface you use
- Sends commands to Docker daemon
- Examples: `docker run`, `docker build`, `docker ps`

**2. Docker Daemon (`dockerd`)**
- Background service managing containers
- Listens for Docker API requests
- Manages images, containers, networks, volumes
- Can communicate with other daemons

**3. containerd**
- Industry-standard container runtime
- Manages container lifecycle
- Image transfer and storage
- Started/stopped by Docker daemon

**4. runc**
- Low-level container runtime
- Actually creates and runs containers
- OCI (Open Container Initiative) compliant

**5. Docker Registry**
- Stores Docker images
- Docker Hub: public registry
- Private registries for enterprise

### How It All Works Together

```
$ docker run nginx

1. Client: Sends 'run nginx' to daemon
2. Daemon: Checks if nginx image exists locally
3. Daemon: If not, pulls from registry (Docker Hub)
4. containerd: Unpacks image layers
5. runc: Creates container from image
6. Container: nginx starts running!
```

---

## 4. Installing Docker

### Installation on Linux (Ubuntu/Debian)

```bash
# Update package index
sudo apt-get update

# Install prerequisites
sudo apt-get install \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# Add Docker's official GPG key
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Set up repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker Engine
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Verify installation
sudo docker run hello-world
```

### Post-Installation: Run Docker without `sudo`

```bash
# Create docker group (usually exists)
sudo groupadd docker

# Add your user to docker group
sudo usermod -aG docker $USER

# Apply group membership (or log out/in)
newgrp docker

# Verify
docker run hello-world  # No sudo needed!
```

### Installation on Mac/Windows

**Docker Desktop** (recommended for development):

1. Download from https://www.docker.com/products/docker-desktop
2. Run installer
3. Start Docker Desktop
4. Verify in terminal: `docker --version`

**What's Included:**
- Docker Engine
- Docker CLI
- Docker Compose
- Kubernetes (optional)
- Dashboard UI

### Verification

```bash
# Check version
docker --version
# Output: Docker version 24.0.6, build ed223bc

# Check detailed info
docker version

# Check Docker system info
docker info

# Run test container
docker run hello-world
```

**Expected Output from hello-world**:
```
Hello from Docker!
This message shows that your installation appears to be working correctly.

To generate this message, Docker took the following steps:
 1. The Docker client contacted the Docker daemon.
 2. The Docker daemon pulled the "hello-world" image from the Docker Hub.
 3. The Docker daemon created a new container from that image which runs the
    executable that produces the output you are currently reading.
 4. The Docker daemon streamed that output to the Docker client, which sent it
    to your terminal.
```

---

## 5. Understanding Images and Containers

### The Image-Container Relationship

**Image** = Blueprint (class in OOP)
**Container** = Running instance (object in OOP)

```
Image (nginx:latest)
      │
      ├──→ Container 1 (web-server-1)
      ├──→ Container 2 (web-server-2)
      └──→ Container 3 (web-server-3)

One image, multiple containers!
```

### What is a Docker Image?

**Image**: Read-only template with instructions for creating a container.

**Key Concepts:**
- Made up of layers
- Each layer represents a filesystem change
- Layers are cached and reusable
- Images are immutable

```
Image Layers (example):
┌─────────────────────┐
│  App Code Layer     │  ← Top layer
├─────────────────────┤
│  pip install deps   │
├─────────────────────┤
│  Python 3.11        │
├─────────────────────┤
│  Ubuntu Base        │  ← Bottom layer
└─────────────────────┘
```

### What is a Container?

**Container**: Runnable instance of an image.

**Key Concepts:**
- Has writable layer on top of image
- Can be started, stopped, moved, deleted
- Isolated from other containers
- Can connect to networks, attach storage

```
Container = Image + Writable Layer + Runtime Config

┌─────────────────────┐
│  Writable Layer     │  ← Container's changes
├─────────────────────┤
│  Image Layers       │  ← Read-only
└─────────────────────┘
```

---

## 6. Your First Containers

### Running a Simple Container

```bash
# Run nginx web server
docker run nginx

# What happened:
# 1. Downloaded nginx image (if not present)
# 2. Created container from image
# 3. Started nginx process
# 4. Attached to container output (logs)

# Stop with Ctrl+C
```

### Running in Detached Mode

```bash
# Run in background (-d = detached)
docker run -d nginx

# Output: container ID
# a1b2c3d4e5f6...

# Container runs in background!
```

### Naming Containers

```bash
# Give container a name
docker run -d --name my-nginx nginx

# Easier to reference by name than ID
```

### Port Mapping

```bash
# Map container port to host port
docker run -d -p 8080:80 nginx

# Format: -p host_port:container_port
# Access nginx at http://localhost:8080

# Open browser and visit http://localhost:8080
# You should see "Welcome to nginx!"
```

### Interactive Containers

```bash
# Run Ubuntu interactively
docker run -it ubuntu bash

# -i: Keep STDIN open (interactive)
# -t: Allocate pseudo-TTY (terminal)

# You're now inside the container!
root@a1b2c3d4e5f6:/# ls
root@a1b2c3d4e5f6:/# whoami
# root

root@a1b2c3d4e5f6:/# exit  # Exit container
```

### Environment Variables

```bash
# Pass environment variables
docker run -d -e MY_VAR=hello -e DB_HOST=localhost nginx

# Multiple variables with multiple -e flags
```

---

## 7. Basic Docker Commands

### Managing Containers

```bash
# List running containers
docker ps

# List all containers (including stopped)
docker ps -a

# Stop a container
docker stop my-nginx

# Start a stopped container
docker start my-nginx

# Restart a container
docker restart my-nginx

# Remove a container
docker rm my-nginx

# Force remove running container
docker rm -f my-nginx

# Remove all stopped containers
docker container prune
```

### Viewing Container Details

```bash
# View container logs
docker logs my-nginx

# Follow logs (like tail -f)
docker logs -f my-nginx

# Last 100 lines
docker logs --tail 100 my-nginx

# Inspect container
docker inspect my-nginx

# View container stats (CPU, memory)
docker stats my-nginx
```

### Executing Commands in Containers

```bash
# Execute command in running container
docker exec my-nginx ls /etc

# Interactive shell
docker exec -it my-nginx bash

# Now you're inside the running container!
```

### Managing Images

```bash
# List images
docker images

# Pull image from registry
docker pull python:3.11

# Remove image
docker rmi nginx

# Remove unused images
docker image prune

# View image history (layers)
docker history nginx
```

---

## 8. Practical Examples

### Example 1: Simple Web Server

```bash
# Run nginx on port 8080
docker run -d -p 8080:80 --name webserver nginx

# Verify it's running
docker ps

# Check logs
docker logs webserver

# Access in browser: http://localhost:8080

# Stop and remove
docker stop webserver
docker rm webserver
```

### Example 2: Python Application

```bash
# Run Python REPL
docker run -it python:3.11 python

>>> print("Hello from Docker!")
>>> exit()

# Run Python script
echo 'print("Hello from Docker!")' > hello.py
docker run -v $(pwd):/app python:3.11 python /app/hello.py
```

### Example 3: Database Container

```bash
# Run PostgreSQL
docker run -d \
  --name postgres-db \
  -e POSTGRES_PASSWORD=mysecretpassword \
  -p 5432:5432 \
  postgres:15

# Check it's running
docker logs postgres-db

# Connect with psql
docker exec -it postgres-db psql -U postgres

# Cleanup
docker stop postgres-db
docker rm postgres-db
```

### Example 4: Development Environment

```bash
# Run Jupyter notebook
docker run -d \
  --name jupyter \
  -p 8888:8888 \
  -v $(pwd):/home/jovyan/work \
  jupyter/scipy-notebook

# Get access token
docker logs jupyter | grep token

# Access at http://localhost:8888 with token
```

---

## 9. Common Issues and Troubleshooting

### Issue 1: "Cannot connect to Docker daemon"

**Error**: `Cannot connect to the Docker daemon. Is the docker daemon running?`

**Solutions**:
```bash
# Check if Docker is running
sudo systemctl status docker

# Start Docker
sudo systemctl start docker

# Check if user is in docker group
groups $USER

# If not, add user to docker group (see section 4)
```

### Issue 2: Port Already in Use

**Error**: `Bind for 0.0.0.0:8080 failed: port is already allocated`

**Solutions**:
```bash
# Find what's using the port
sudo lsof -i :8080

# Use different host port
docker run -p 8081:80 nginx

# Or stop the conflicting service
```

### Issue 3: Container Exits Immediately

**Problem**: Container starts and stops right away

**Diagnosis**:
```bash
# Check exit code
docker ps -a

# View logs
docker logs <container-name>

# Run interactively to debug
docker run -it <image> sh
```

### Issue 4: Out of Disk Space

**Error**: `no space left on device`

**Solutions**:
```bash
# Check Docker disk usage
docker system df

# Clean up unused resources
docker system prune

# Remove all unused containers, networks, images
docker system prune -a

# Remove specific items
docker container prune  # Remove stopped containers
docker image prune      # Remove dangling images
docker volume prune     # Remove unused volumes
```

---

## 10. Best Practices (Fundamentals)

### 1. Always Name Your Containers

```bash
# Bad
docker run -d nginx

# Good
docker run -d --name my-webserver nginx
```

### 2. Use Specific Image Tags

```bash
# Bad (uses 'latest', unpredictable)
docker run nginx

# Good (specific version)
docker run nginx:1.25.3
```

### 3. Clean Up Regularly

```bash
# Remove stopped containers
docker container prune

# Remove unused images
docker image prune

# Full cleanup (be careful!)
docker system prune -a
```

### 4. Check Logs for Debugging

```bash
# Always check logs first
docker logs <container-name>

# For live troubleshooting
docker logs -f <container-name>
```

### 5. Use `docker exec` for Inspection

```bash
# Don't create new containers to debug
# Use exec on running container
docker exec -it <container-name> bash
```

---

## Key Takeaways

✅ **Containers** are lightweight, isolated application packages
✅ **Containers ≠ VMs**: Containers share host OS, much lighter
✅ **Docker** is a platform for building and running containers
✅ **Images** are blueprints, **containers** are running instances
✅ **Docker uses client-server architecture** with daemon
✅ **Basic workflow**: pull image → run container → manage lifecycle
✅ **Port mapping** connects container to host network
✅ **docker ps** shows running containers
✅ **docker logs** shows container output
✅ **docker exec** runs commands in running containers

---

## Quick Reference

### Essential Commands

```bash
# Run container
docker run [OPTIONS] IMAGE [COMMAND]

# List containers
docker ps [-a]

# Stop container
docker stop CONTAINER

# Remove container
docker rm CONTAINER

# View logs
docker logs CONTAINER

# Execute command
docker exec [OPTIONS] CONTAINER COMMAND

# List images
docker images

# Pull image
docker pull IMAGE[:TAG]

# Remove image
docker rmi IMAGE
```

### Common Options

```
-d         Detached mode (background)
-it        Interactive with terminal
-p         Port mapping (host:container)
-e         Environment variable
--name     Name the container
-v         Volume mount
--rm       Remove container when it exits
```

---

## What's Next?

In the next lecture, we'll dive deeper into:
- **Dockerfile basics**: Building your own images
- **Image layers**: Understanding how images are constructed
- **Building images**: Creating custom images for your applications
- **Image optimization**: Making images smaller and faster

**Practice Before Next Lecture**:
1. Run at least 5 different containers
2. Practice start/stop/remove
3. Use `docker exec` to explore running containers
4. Try port mapping with different applications

Continue to `lecture-notes/02-dockerfiles-basics.md`

---

**Lecture Version**: 1.0
**Last Updated**: October 2025
**Estimated Time**: 90 minutes
**Difficulty**: Beginner
