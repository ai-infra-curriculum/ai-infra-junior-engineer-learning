# Exercise 01: Docker Container Operations

## Overview

Master fundamental Docker container operations including running, managing, and debugging containers.

**Difficulty**: Beginner
**Estimated Time**: 2-3 hours

## Learning Objectives

By completing this exercise, you will:
- Execute Docker containers in interactive and detached modes
- Manage container lifecycle (start, stop, restart, remove)
- Inspect container logs and debug running containers
- Configure port mapping for container networking
- Set environment variables for containerized applications
- Apply resource constraints (CPU, memory) to containers
- Use docker inspect to examine container configuration

## Prerequisites

- Lecture 01 (Docker Fundamentals) completed
- Docker installed and running
- Basic command-line proficiency

---

## Part 1: Environment Setup

### Step 1.1: Verify Docker Installation

```bash
# Check Docker version
docker --version

# Check Docker info
docker info

# Test with hello-world
docker run hello-world
```

**Expected Output**:
```
Docker version 24.0.6, build ed223bc
...
Hello from Docker!
```

✅ **Checkpoint**: Docker is installed and running.

---

## Part 2: Running Containers

### Step 2.1: Run Your First Container

```bash
# Run nginx in foreground
docker run nginx

# Press Ctrl+C to stop

# What happened?
# 1. Downloaded nginx image (if not present)
# 2. Created container from image
# 3. Started nginx process
# 4. Attached to container output
```

### Step 2.2: Detached Mode

```bash
# Run in background (-d = detached)
docker run -d nginx

# Output: Container ID
# abc123def456...

# Container is running in background!
```

### Step 2.3: Naming Containers

```bash
# Give container a friendly name
docker run -d --name my-nginx nginx

# Verify it's running
docker ps

# Output shows your named container
```

**Questions**:
1. Why is naming containers useful?
2. What happens if you try to create another container with the same name?

✅ **Checkpoint**: You can run containers in detached mode with custom names.

---

## Part 3: Managing Container Lifecycle

### Step 3.1: List Containers

```bash
# List running containers
docker ps

# List all containers (including stopped)
docker ps -a

# List with custom format
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

### Step 3.2: Stop and Start Containers

```bash
# Stop a running container
docker stop my-nginx

# Verify it's stopped
docker ps -a

# Start it again
docker start my-nginx

# Restart container
docker restart my-nginx
```

### Step 3.3: Pause and Unpause

```bash
# Pause container (freezes processes)
docker pause my-nginx

# Check status
docker ps

# Unpause
docker unpause my-nginx
```

### Step 3.4: Remove Containers

```bash
# Stop container first
docker stop my-nginx

# Remove container
docker rm my-nginx

# Remove running container (force)
docker rm -f my-nginx

# Run container that auto-removes when stopped
docker run -d --rm --name temp-nginx nginx
docker stop temp-nginx
docker ps -a  # Container is gone!
```

**Task**: Create a script that manages nginx lifecycle

```bash
#!/bin/bash
# lifecycle.sh

echo "Starting nginx..."
docker run -d --name web nginx

echo "Waiting 5 seconds..."
sleep 5

echo "Stopping nginx..."
docker stop web

echo "Removing nginx..."
docker rm web

echo "Done!"
```

✅ **Checkpoint**: You can manage container lifecycle (start, stop, remove).

---

## Part 4: Port Mapping

### Step 4.1: Expose Container Ports

```bash
# Map host port 8080 to container port 80
docker run -d -p 8080:80 --name web nginx

# Test in browser or with curl
curl http://localhost:8080

# You should see nginx welcome page!
```

### Step 4.2: Multiple Port Mappings

```bash
# Map multiple ports
docker run -d \
  -p 8080:80 \
  -p 8443:443 \
  --name web-secure \
  nginx

# Check port mappings
docker port web-secure
```

### Step 4.3: Random Port Assignment

```bash
# Let Docker assign random host port
docker run -d -P --name web-random nginx

# Find assigned port
docker port web-random

# Output: 80/tcp -> 0.0.0.0:32768
```

### Step 4.4: Bind to Specific Interface

```bash
# Only accessible from localhost
docker run -d -p 127.0.0.1:8080:80 --name web-local nginx

# Accessible from any interface
docker run -d -p 0.0.0.0:8080:80 --name web-public nginx
```

**Challenge**: Run 3 nginx containers on ports 8081, 8082, 8083

```bash
# Your code here
docker run -d -p 8081:80 --name web1 nginx
docker run -d -p 8082:80 --name web2 nginx
docker run -d -p 8083:80 --name web3 nginx

# Verify all running
docker ps

# Test all ports
curl http://localhost:8081
curl http://localhost:8082
curl http://localhost:8083
```

✅ **Checkpoint**: You can map container ports to host.

---

## Part 5: Environment Variables

### Step 5.1: Pass Environment Variables

```bash
# Single variable
docker run -d -e MY_VAR=hello --name env-test alpine sleep 3600

# Verify
docker exec env-test env | grep MY_VAR
# MY_VAR=hello

# Multiple variables
docker run -d \
  -e DB_HOST=localhost \
  -e DB_PORT=5432 \
  -e DB_NAME=mydb \
  --name app-with-env \
  alpine sleep 3600
```

### Step 5.2: Use Environment File

```bash
# Create .env file
cat > app.env << EOF
DB_HOST=postgres
DB_PORT=5432
DB_USER=appuser
DB_PASSWORD=secret123
DEBUG=true
EOF

# Run with env file
docker run -d --env-file app.env --name app-env alpine sleep 3600

# Verify
docker exec app-env env
```

### Step 5.3: Real Example - PostgreSQL

```bash
# Run PostgreSQL with environment variables
docker run -d \
  --name postgres-db \
  -e POSTGRES_USER=myuser \
  -e POSTGRES_PASSWORD=mypassword \
  -e POSTGRES_DB=mydb \
  -p 5432:5432 \
  postgres:15

# Check logs
docker logs postgres-db

# Connect to database
docker exec -it postgres-db psql -U myuser -d mydb

# Inside psql:
# \l  - list databases
# \q  - quit
```

✅ **Checkpoint**: You can configure containers with environment variables.

---

## Part 6: Viewing Logs

### Step 6.1: Basic Logging

```bash
# View logs
docker logs web

# Follow logs (like tail -f)
docker logs -f web

# Last 50 lines
docker logs --tail 50 web

# Logs since specific time
docker logs --since 10m web  # Last 10 minutes

# With timestamps
docker logs -f --timestamps web
```

### Step 6.2: Generate Some Logs

```bash
# Generate traffic to nginx
for i in {1..10}; do
  curl http://localhost:8080
done

# View access logs
docker logs web
```

### Step 6.3: Log Driver Configuration

```bash
# Run with JSON log driver (default)
docker run -d \
  --log-driver json-file \
  --log-opt max-size=10m \
  --log-opt max-file=3 \
  --name web-logs \
  nginx

# Run with no logs (for performance)
docker run -d --log-driver none --name no-logs nginx
```

✅ **Checkpoint**: You can view and manage container logs.

---

## Part 7: Executing Commands in Containers

### Step 7.1: Basic Exec

```bash
# Execute single command
docker exec web ls /usr/share/nginx/html

# Run interactive shell
docker exec -it web bash

# Inside container:
ls
pwd
whoami
exit
```

### Step 7.2: Execute as Different User

```bash
# Execute as root (default)
docker exec -u root web whoami

# Execute as www-data
docker exec -u www-data web whoami
```

### Step 7.3: Practical Examples

```bash
# Check nginx configuration
docker exec web nginx -t

# View nginx process
docker exec web ps aux

# Check disk usage
docker exec web df -h

# Install tools and use them
docker exec web apt-get update
docker exec web apt-get install -y curl
docker exec web curl localhost
```

**Challenge**: Create a Python container and execute Python commands

```bash
# Run Python container
docker run -d --name python-app python:3.11 sleep 3600

# Execute Python commands
docker exec python-app python --version
docker exec python-app pip list
docker exec -it python-app python

# In Python REPL:
# >>> print("Hello from Docker!")
# >>> exit()
```

✅ **Checkpoint**: You can execute commands inside running containers.

---

## Part 8: Inspecting Containers

### Step 8.1: Container Inspection

```bash
# Get all details
docker inspect web

# Get specific fields
docker inspect web --format='{{.State.Status}}'
docker inspect web --format='{{.NetworkSettings.IPAddress}}'
docker inspect web --format='{{json .Config.Env}}'
```

### Step 8.2: Resource Usage

```bash
# Real-time stats
docker stats

# Single container
docker stats web

# No streaming (one shot)
docker stats --no-stream
```

### Step 8.3: Process Information

```bash
# View processes in container
docker top web

# With custom format
docker top web aux
```

### Step 8.4: File System Changes

```bash
# See file changes in container
docker diff web

# Legend:
# A - Added
# D - Deleted
# C - Changed
```

✅ **Checkpoint**: You can inspect container details and resource usage.

---

## Part 9: Resource Constraints

### Step 9.1: Memory Limits

```bash
# Limit memory to 512MB
docker run -d --memory="512m" --name limited-mem nginx

# Memory with swap limit
docker run -d \
  --memory="512m" \
  --memory-swap="1g" \
  --name mem-with-swap \
  nginx

# Verify limits
docker stats limited-mem --no-stream
```

### Step 9.2: CPU Limits

```bash
# Limit to 1 CPU
docker run -d --cpus="1.0" --name limited-cpu nginx

# CPU shares (relative weight)
docker run -d --cpu-shares=512 --name low-priority nginx
docker run -d --cpu-shares=1024 --name high-priority nginx
```

### Step 9.3: Test Resource Limits

```bash
# Run container that will consume memory
docker run -d \
  --memory="100m" \
  --name stress-test \
  progrium/stress --vm 1 --vm-bytes 150M

# Watch what happens
docker logs stress-test
docker stats stress-test

# Container should be killed due to OOM
```

✅ **Checkpoint**: You can set and monitor resource limits.

---

## Part 10: Interactive Containers

### Step 10.1: Interactive Mode

```bash
# Run Ubuntu interactively
docker run -it ubuntu bash

# Inside container:
apt-get update
apt-get install -y curl
curl https://api.github.com
exit
```

### Step 10.2: Attach to Running Container

```bash
# Run container
docker run -d --name myapp alpine sh -c "while true; do echo Hello; sleep 2; done"

# Attach to see output
docker attach myapp

# Detach: Ctrl+P, Ctrl+Q (keeps container running)
# Or Ctrl+C (stops container)
```

### Step 10.3: Copy Files

```bash
# Create test file
echo "Hello from host" > test.txt

# Copy to container
docker cp test.txt web:/tmp/

# Verify
docker exec web cat /tmp/test.txt

# Copy from container
docker exec web sh -c "echo 'From container' > /tmp/from-container.txt"
docker cp web:/tmp/from-container.txt .
cat from-container.txt
```

✅ **Checkpoint**: You can work with containers interactively.

---

## Part 11: Cleanup and Maintenance

### Step 11.1: Remove Stopped Containers

```bash
# Remove all stopped containers
docker container prune

# Confirm: y
```

### Step 11.2: Remove All Containers

```bash
# Stop all running containers
docker stop $(docker ps -q)

# Remove all containers
docker rm $(docker ps -a -q)
```

### Step 11.3: System Cleanup

```bash
# View disk usage
docker system df

# Detailed view
docker system df -v

# Clean up everything unused
docker system prune

# Including volumes
docker system prune -a --volumes
```

✅ **Checkpoint**: You can clean up Docker resources.

---

## Part 12: Practical Application

### Challenge: Web Application Stack

**Task**: Set up a complete web application environment

```bash
# 1. Run PostgreSQL database
docker run -d \
  --name db \
  -e POSTGRES_PASSWORD=secret \
  -e POSTGRES_DB=appdb \
  postgres:15

# 2. Run Redis cache
docker run -d \
  --name cache \
  redis:7-alpine

# 3. Wait for services to start
sleep 5

# 4. Check all running
docker ps

# 5. Test database
docker exec db psql -U postgres -d appdb -c "SELECT version();"

# 6. Test Redis
docker exec cache redis-cli ping

# 7. View logs
docker logs db
docker logs cache

# 8. Check resource usage
docker stats --no-stream

# 9. Cleanup
docker stop db cache
docker rm db cache
```

### Challenge: Debug a Failing Container

```bash
# Run container that fails
docker run -d --name failing-app nginx:nonexistent

# What went wrong? Debug it:
# 1. Check status
docker ps -a

# 2. View logs
docker logs failing-app

# 3. Inspect
docker inspect failing-app

# 4. Fix and rerun
docker rm failing-app
docker run -d --name working-app nginx:latest
```

---

## Validation and Testing

### Test Your Knowledge

Create a bash script that:
1. Runs 3 nginx containers on different ports
2. Generates traffic to each
3. Views logs from all containers
4. Checks resource usage
5. Stops and removes all containers

```bash
#!/bin/bash
# solution.sh

# Your implementation here
echo "Starting containers..."
docker run -d -p 8081:80 --name web1 nginx
docker run -d -p 8082:80 --name web2 nginx
docker run -d -p 8083:80 --name web3 nginx

echo "Waiting for startup..."
sleep 3

echo "Generating traffic..."
for i in {1..5}; do
  curl -s http://localhost:8081 > /dev/null
  curl -s http://localhost:8082 > /dev/null
  curl -s http://localhost:8083 > /dev/null
done

echo "Viewing logs..."
docker logs --tail 5 web1
docker logs --tail 5 web2
docker logs --tail 5 web3

echo "Resource usage..."
docker stats --no-stream web1 web2 web3

echo "Cleanup..."
docker stop web1 web2 web3
docker rm web1 web2 web3

echo "Done!"
```

---

## Reflection Questions

1. **What's the difference between `docker stop` and `docker kill`?**
   - Your answer:

2. **When would you use `--rm` flag?**
   - Your answer:

3. **How do you troubleshoot a container that exits immediately?**
   - Your answer:

4. **What's the difference between `docker run` and `docker exec`?**
   - Your answer:

5. **Why is it important to limit container resources?**
   - Your answer:

---

## Summary

**What You Accomplished**:
✅ Ran containers in multiple modes
✅ Managed container lifecycle
✅ Configured port mapping
✅ Used environment variables
✅ Viewed and analyzed logs
✅ Executed commands in containers
✅ Set resource limits
✅ Inspected container details
✅ Cleaned up resources

**Key Commands Mastered**:
- `docker run` - Create and start containers
- `docker ps` - List containers
- `docker logs` - View container logs
- `docker exec` - Execute commands
- `docker stop/start/restart` - Manage lifecycle
- `docker rm` - Remove containers
- `docker stats` - Monitor resources
- `docker inspect` - View details

---

## Next Steps

**Practice More**:
1. Run different types of applications (databases, web servers, etc.)
2. Experiment with different resource limits
3. Practice debugging failing containers
4. Create more complex multi-container setups

**Continue Learning**:
- **Exercise 02**: Building Custom Images
- **Exercise 03**: Docker Compose Applications

---

**Exercise Version**: 1.0
**Last Updated**: October 2025
**Estimated Time**: 2-3 hours
**Difficulty**: Beginner
