# Module 005: Docker Containers - Comprehensive Quiz

## Overview

This quiz assesses your understanding of Docker containerization for AI infrastructure, covering all five lectures and exercises from Module 005. The quiz includes multiple choice, true/false, code analysis, and scenario-based questions focusing on Docker fundamentals, Dockerfiles, Docker Compose, networking, volumes, and best practices.

**Time Limit**: 60 minutes
**Total Questions**: 30
**Passing Score**: 75% (23/30 correct)

---

## Section 1: Docker Fundamentals (Questions 1-6)

### Question 1: Containers vs Virtual Machines

**What is the PRIMARY difference between containers and virtual machines?**

A) Containers include a full operating system, VMs don't
B) Containers share the host OS kernel, VMs include their own OS
C) VMs are faster to start than containers
D) Containers require more disk space than VMs

**Answer**: B

**Explanation**: Containers share the host operating system kernel and isolate the application processes, making them lightweight and fast to start. Virtual machines include a full guest operating system, which requires more resources. This makes B correct. Options A and D are backwards (VMs include full OS and use more space), and C is incorrect (containers start much faster than VMs).

---

### Question 2: Docker Architecture

**Which component is responsible for building, running, and distributing Docker containers?**

A) Docker CLI
B) Docker Daemon (dockerd)
C) Docker Registry
D) Container Runtime

**Answer**: B

**Explanation**: The Docker Daemon (dockerd) is the background service that manages Docker objects (images, containers, networks, volumes) and handles building, running, and distributing containers. The Docker CLI (A) is the client interface, Docker Registry (C) stores images, and Container Runtime (D) executes containers but doesn't handle the full lifecycle.

---

### Question 3: Images and Containers

**What is the relationship between Docker images and containers?**

A) An image is a running instance of a container
B) A container is a running instance of an image
C) Images and containers are the same thing
D) Containers are used to build images

**Answer**: B

**Explanation**: A Docker image is a read-only template containing application code, dependencies, and configuration. A container is a running instance created from an image. You can create multiple containers from the same image. Option A reverses the relationship, C is incorrect (they are different), and D is backwards (images are used to create containers, though containers can be committed to create new images).

---

### Question 4: Docker Commands

**What does the command `docker run -d -p 8080:80 nginx` do?**

A) Runs nginx in the foreground on port 8080
B) Runs nginx in the background, mapping host port 8080 to container port 80
C) Runs nginx in debug mode on port 80
D) Downloads nginx image from port 8080

**Answer**: B

**Explanation**: The `-d` flag runs the container in detached mode (background), and `-p 8080:80` maps port 8080 on the host to port 80 in the container. This allows you to access nginx at http://localhost:8080. Option A is incorrect (it runs in background, not foreground), C misinterprets `-d`, and D misunderstands the port mapping syntax.

---

### Question 5: Container Lifecycle

**Which command would you use to view logs from a running container named `ml-api`?**

A) `docker inspect ml-api`
B) `docker logs ml-api`
C) `docker exec ml-api cat /var/log`
D) `docker ps ml-api`

**Answer**: B

**Explanation**: `docker logs <container>` displays the stdout and stderr output from a container, which is the standard way to view container logs. `docker inspect` (A) shows container metadata, `docker exec` (C) would work but is overly complex and assumes logs are in that location, and `docker ps` (D) lists running containers.

---

### Question 6: Image Layers

**True or False: Docker images are composed of read-only layers, and when you create a container, Docker adds a writable layer on top.**

A) True
B) False

**Answer**: A

**Explanation**: This is TRUE. Docker images use a layered filesystem where each instruction in a Dockerfile creates a new read-only layer. When a container is created, Docker adds a thin writable layer (the container layer) on top of the image layers. Any changes made during container runtime are written to this writable layer, while the underlying image layers remain unchanged.

---

## Section 2: Dockerfiles and Building Images (Questions 7-12)

### Question 7: Dockerfile Instructions

**Which Dockerfile instruction is used to specify the command that runs when a container starts?**

A) RUN
B) CMD
C) ENTRYPOINT
D) EXECUTE

**Answer**: B (or C, both are acceptable)

**Explanation**: Both `CMD` and `ENTRYPOINT` specify the command to run when a container starts. `CMD` provides default arguments that can be overridden, while `ENTRYPOINT` configures the container to run as an executable. `RUN` executes commands during image build time (not container start), and `EXECUTE` is not a valid Dockerfile instruction. For this quiz, either B or C is acceptable.

---

### Question 8: Multi-Stage Builds

**What is the PRIMARY benefit of multi-stage Docker builds for ML applications?**

A) Faster container startup times
B) Smaller final image size by excluding build dependencies
C) Better runtime performance
D) Easier debugging

**Answer**: B

**Explanation**: Multi-stage builds allow you to use one stage for building/compiling (with build tools, compilers, dev dependencies) and copy only the necessary artifacts to the final stage. This dramatically reduces image size by excluding build dependencies from the production image. While this may indirectly help startup (A), the primary benefit is size reduction. It doesn't directly improve runtime performance (C) or debugging (D).

---

### Question 9: Layer Caching

**To maximize Docker build cache efficiency, where should you place the `COPY requirements.txt` instruction in a Python ML Dockerfile?**

A) At the very beginning, before any other instructions
B) After `RUN pip install` commands
C) After `FROM` but before installing dependencies with `RUN pip install`
D) At the very end, after all RUN commands

**Answer**: C

**Explanation**: To maximize cache efficiency, copy `requirements.txt` and run `pip install` before copying the application code. This way, the dependency installation layer is cached and only rebuilt when requirements change, not when code changes. Option A would work but isn't after FROM (which must be first), B would install packages before having requirements.txt, and D would cause cache invalidation on every code change.

---

### Question 10: Best Practices

**Which Dockerfile instruction should you use to minimize the number of layers in your image?**

A) Use multiple RUN commands, one per package
B) Chain commands together using `&&` in a single RUN instruction
C) Use multiple COPY commands
D) Use ADD instead of COPY

**Answer**: B

**Explanation**: Chaining commands with `&&` in a single RUN instruction creates one layer instead of multiple layers. For example: `RUN apt-get update && apt-get install -y python3 && apt-get clean` creates one layer. Multiple RUN commands (A) create multiple layers, multiple COPY commands (C) aren't related to RUN layers, and using ADD vs COPY (D) doesn't reduce layers (and COPY is preferred for simple file copying).

---

### Question 11: COPY vs ADD

**When should you use ADD instead of COPY in a Dockerfile?**

A) Always use ADD; it's more powerful
B) When you need to extract tar files automatically or fetch from URLs
C) When copying local files to the image
D) Never use ADD; COPY is always better

**Answer**: B

**Explanation**: `ADD` has additional features like automatic tar extraction and URL fetching, but these features can lead to unexpected behavior. Use `ADD` only when you specifically need these features. For simple file copying (C), use `COPY` as it's more transparent. Options A and D are too absolute.

---

### Question 12: Build Context

**What is the Docker build context, and why does it matter?**

A) The directory containing the Dockerfile
B) The entire directory tree sent to the Docker daemon during build
C) The environment variables available during build
D) The CPU and memory allocated to the build process

**Answer**: B

**Explanation**: The build context is the entire directory tree (typically where you run `docker build`) that gets sent to the Docker daemon. Large build contexts (e.g., containing datasets, models) slow down builds significantly. Use `.dockerignore` to exclude unnecessary files. Option A is partial (it includes that directory and subdirectories), C refers to build args (different concept), and D refers to resource limits (different concept).

---

## Section 3: Docker Compose (Questions 13-18)

### Question 13: Docker Compose Purpose

**What is the PRIMARY purpose of Docker Compose?**

A) To build Docker images faster
B) To define and run multi-container applications
C) To deploy containers to production Kubernetes clusters
D) To compress Docker images

**Answer**: B

**Explanation**: Docker Compose is a tool for defining and running multi-container Docker applications using a YAML file. It's ideal for development environments where you need to run multiple services (e.g., web app, database, cache) together. It doesn't primarily speed up builds (A), isn't designed for production Kubernetes deployments (C), or compress images (D).

---

### Question 14: Docker Compose File Format

**In a `docker-compose.yml` file, what does the `depends_on` key specify?**

A) Which images to download first
B) The startup order and dependencies between services
C) Which services to run on which hosts
D) The version of Docker Compose to use

**Answer**: B

**Explanation**: `depends_on` expresses startup order and dependency relationships between services. For example, a web service might depend on a database service, so Compose will start the database before the web app. It doesn't control download order (A), host placement (C), or Compose version (D - that's the `version` key).

---

### Question 15: Compose Networking

**How do services defined in the same `docker-compose.yml` file communicate with each other?**

A) Using localhost and port numbers
B) Using the service names as hostnames on a shared network
C) They cannot communicate; you must use external networking
D) Using IP addresses assigned by Docker

**Answer**: B

**Explanation**: Docker Compose automatically creates a default network for all services in the compose file. Services can reach each other using the service name as the hostname. For example, a `web` service can connect to a `db` service using `db:5432`. While D is technically true (IP addresses are assigned), B is the correct practice and abstraction.

---

### Question 16: Compose Commands

**Which command starts services defined in `docker-compose.yml` in detached mode?**

A) `docker-compose start -d`
B) `docker-compose run -d`
C) `docker-compose up -d`
D) `docker-compose deploy -d`

**Answer**: C

**Explanation**: `docker-compose up -d` starts all services defined in the compose file in detached mode (background). `docker-compose start` (A) starts existing stopped containers but doesn't accept `-d`, `docker-compose run` (B) runs a one-off command, and `docker-compose deploy` (D) is not a standard command (deploy is for Docker Swarm stacks).

---

### Question 17: Environment Variables

**In Docker Compose, how can you pass environment variables from a `.env` file to your containers?**

A) Docker Compose automatically loads `.env` files in the same directory
B) You must use `docker-compose --env-file .env up`
C) Environment files are not supported in Compose
D) You must manually export variables before running compose

**Answer**: A

**Explanation**: Docker Compose automatically loads a `.env` file from the project directory and makes those variables available for variable substitution in the `docker-compose.yml` file. You can also use `env_file` in the service definition to load environment variables into containers. Option B is incorrect (--env-file is not standard), C is false, and D is unnecessary.

---

### Question 18: Volumes in Compose

**What is the difference between a named volume and a bind mount in Docker Compose?**

A) Named volumes are managed by Docker, bind mounts map host directories
B) Bind mounts are managed by Docker, named volumes map host directories
C) They are the same thing with different names
D) Named volumes are faster than bind mounts

**Answer**: A

**Explanation**: Named volumes are managed by Docker (created in Docker's storage directory) and are portable across environments. Bind mounts map specific host directories/files into containers, giving direct access to host filesystem. Named volumes are preferred for data persistence, while bind mounts are useful for development (e.g., live code reloading).

---

## Section 4: Networking and Volumes (Questions 19-24)

### Question 19: Docker Networks

**Which Docker network driver allows containers to communicate as if they were on the host network?**

A) bridge
B) host
C) overlay
D) none

**Answer**: B

**Explanation**: The `host` network driver removes network isolation between container and host, making the container use the host's network directly. `bridge` (A) is the default isolated network, `overlay` (C) is for multi-host networking (Swarm), and `none` (D) disables networking completely.

---

### Question 20: Port Publishing

**In the port mapping `-p 5000:8080`, which port is on the host machine?**

A) 8080
B) 5000
C) Both ports are on the host
D) Neither; both are container ports

**Answer**: B

**Explanation**: The port mapping syntax is `-p HOST_PORT:CONTAINER_PORT`. So `-p 5000:8080` maps host port 5000 to container port 8080. You would access the service at `localhost:5000`, which forwards to port 8080 inside the container.

---

### Question 21: Data Persistence

**What happens to data stored in a container's filesystem when the container is removed?**

A) Data is automatically backed up to the host
B) Data is lost unless stored in a volume or bind mount
C) Data persists indefinitely on the host
D) Data is transferred to a new container

**Answer**: B

**Explanation**: Container filesystems are ephemeral - when a container is removed, its writable layer (and any data in it) is deleted. To persist data, you must use volumes or bind mounts, which store data outside the container's filesystem. This is critical for databases, ML model checkpoints, and training data.

---

### Question 22: Volume Management

**Which command creates a named volume called `model-data`?**

A) `docker volume create model-data`
B) `docker create volume model-data`
C) `docker volume new model-data`
D) `docker make volume model-data`

**Answer**: A

**Explanation**: `docker volume create <volume-name>` is the correct command to create a named volume. The other options use incorrect syntax or non-existent commands.

---

### Question 23: Network Isolation

**Why would you create a custom Docker network instead of using the default bridge network?**

A) Custom networks are faster
B) Custom networks provide automatic DNS resolution between containers by name
C) Custom networks use less memory
D) The default bridge network doesn't work

**Answer**: B

**Explanation**: Custom bridge networks provide automatic service discovery via DNS - containers can communicate using container names as hostnames. On the default bridge network, you must use `--link` (deprecated) or IP addresses. Performance is similar (A incorrect), memory usage is comparable (C incorrect), and the default bridge works fine (D incorrect).

---

### Question 24: Volume Drivers

**What is a volume driver in Docker?**

A) A software component that manages how and where volume data is stored
B) The CPU driver for containers
C) A network driver for volumes
D) A deprecated feature replaced by bind mounts

**Answer**: A

**Explanation**: Volume drivers are plugins that manage volume storage. The default `local` driver stores data on the host filesystem, but third-party drivers can store data on cloud storage (AWS EBS, Azure Disk), NFS, or distributed storage systems. This is especially useful for ML workflows that need shared storage across multiple hosts.

---

## Section 5: Best Practices and Production (Questions 25-30)

### Question 25: Security - Running as Root

**Why is it a security best practice to avoid running containers as the root user?**

A) Root containers run slower
B) If an attacker escapes the container, they have root access on the host
C) Root users cannot install packages
D) Docker doesn't allow root users

**Answer**: B

**Explanation**: Containers share the host kernel. If a container runs as root and an attacker exploits a vulnerability to escape the container, they gain root access on the host system. Using a non-root user (via `USER` instruction) follows the principle of least privilege. Option A is false (no performance difference), C is backwards (root can install packages), and D is incorrect (Docker allows but discourages root).

---

### Question 26: Image Tagging

**What happens when you push an image without specifying a tag (e.g., `docker push myrepo/myimage`)?**

A) Docker generates a random tag
B) Docker uses the `latest` tag by default
C) The push fails with an error
D) Docker uses the current date as the tag

**Answer**: B

**Explanation**: When no tag is specified, Docker implicitly uses the `latest` tag. This can be dangerous in production because `latest` doesn't mean "most recent" - it's just a convention. Best practice is to use explicit semantic version tags (e.g., `v1.2.3`) for production images.

---

### Question 27: Health Checks

**What is the purpose of a HEALTHCHECK instruction in a Dockerfile?**

A) To check the size of the image
B) To verify the container is functioning correctly by running a command periodically
C) To scan for security vulnerabilities
D) To check network connectivity

**Answer**: B

**Explanation**: `HEALTHCHECK` defines a command that Docker runs periodically to check if the container is healthy. For example: `HEALTHCHECK CMD curl -f http://localhost/health || exit 1`. This allows orchestrators (like Kubernetes) to detect and restart unhealthy containers. It doesn't check image size (A), scan for vulnerabilities (C - that's image scanning), or just check network (D - though health checks often use network).

---

### Question 28: .dockerignore

**What is the purpose of a `.dockerignore` file?**

A) To ignore containers during `docker ps`
B) To exclude files from the build context sent to Docker daemon
C) To hide images from `docker images` list
D) To prevent certain containers from starting

**Answer**: B

**Explanation**: `.dockerignore` works like `.gitignore` - it excludes files and directories from the build context. This is critical for ML projects to exclude large datasets, model checkpoints, and `.git` directories, which speeds up builds and reduces image size. It doesn't affect running containers (A, D) or image listing (C).

---

### Question 29: Container Resource Limits

**Why would you set memory and CPU limits on a container running ML inference?**

A) To make the container run faster
B) To prevent one container from consuming all host resources
C) To increase the container's priority
D) Resource limits are not supported in Docker

**Answer**: B

**Explanation**: Setting resource limits (`--memory`, `--cpus`) prevents a single container from starving other containers or the host system. This is especially important for ML workloads which can be resource-intensive. Limits don't make containers faster (A), don't directly affect priority (C - though CPU shares do), and are definitely supported (D is false).

---

### Question 30: Production Readiness - Scenario

**You're deploying an ML model API to production. Which combination of practices is MOST appropriate?**

A) Run as root, use `latest` tag, no health checks, no resource limits
B) Use non-root user, semantic version tags, add health checks, set resource limits
C) Run in development mode, use bind mounts for models, no logging
D) Use large base image with all tools, commit credentials to Dockerfile

**Answer**: B

**Explanation**: Production best practices include: running as non-root user (security), using semantic version tags instead of `latest` (reproducibility), implementing health checks (reliability), and setting resource limits (stability). Option A violates all best practices, C describes a development setup (not production), and D has security issues (large images, committed credentials).

---

## Scoring Guide

| Score Range | Assessment |
|-------------|------------|
| 27-30 (90-100%) | Excellent - Production Ready |
| 23-26 (75-89%) | Good - Passing Score |
| 18-22 (60-74%) | Fair - Review Key Concepts |
| Below 18 (<60%) | Needs Improvement - Revisit Lectures |

---

## Key Topics Covered

This quiz assessed your understanding of:

1. **Docker Fundamentals**: Containers vs VMs, architecture, images vs containers
2. **Dockerfiles**: Building images, multi-stage builds, layer caching, best practices
3. **Docker Compose**: Multi-container applications, networking, volumes, commands
4. **Networking & Volumes**: Network drivers, port mapping, data persistence, volume management
5. **Production Best Practices**: Security, tagging, health checks, resource limits, .dockerignore

---

## Additional Resources

For topics you found challenging, refer back to:

- **Lecture 01**: Docker Fundamentals (Questions 1-6)
- **Lecture 02**: Dockerfiles Basics (Questions 7-12)
- **Lecture 03**: Docker Compose (Questions 13-18)
- **Lecture 04**: Networking and Volumes (Questions 19-24)
- **Lecture 05**: Best Practices (Questions 25-30)

**Practice Exercises**:
- Exercise 01-07 in the module exercises directory
- Hands-on labs with real ML containerization scenarios

---

**Good luck with your Docker journey in AI infrastructure!**
