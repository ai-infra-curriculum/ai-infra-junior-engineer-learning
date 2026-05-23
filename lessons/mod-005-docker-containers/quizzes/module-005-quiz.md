# Module 005: Docker & Containerization - Comprehensive Quiz

## Quiz Overview

**Total Questions**: 50
**Passing Score**: 80% (40/50 correct)
**Time Limit**: 90 minutes
**Question Types**: Multiple choice, true/false, scenario-based

**Topics Covered**:
- Docker fundamentals
- Dockerfiles and image building
- Docker Compose
- Networking
- Volumes and data persistence
- Production deployment
- ML containerization
- Security and best practices

---

## Section 1: Docker Fundamentals (10 questions)

### Question 1
What is the primary difference between a Docker image and a Docker container?

A) An image is a running instance, a container is a template
B) An image is a template, a container is a running instance
C) They are the same thing
D) Images are for development, containers are for production

**Answer**: B

---

### Question 2
Which command would you use to run a container in detached mode with port 8080 on the host mapped to port 80 in the container?

A) `docker run -p 8080:80 nginx`
B) `docker run -d -p 80:8080 nginx`
C) `docker run -d -p 8080:80 nginx`
D) `docker run --detach --port 8080:80 nginx`

**Answer**: C

---

### Question 3
What happens to data inside a container when the container is removed?

A) Data is automatically backed up
B) Data persists on the host
C) Data is lost unless stored in a volume
D) Data is moved to a new container

**Answer**: C

---

### Question 4
Which command shows only the running containers?

A) `docker ps -a`
B) `docker ps`
C) `docker containers ls --all`
D) `docker list running`

**Answer**: B

---

### Question 5
What is the purpose of `docker exec`?

A) Execute a command inside a running container
B) Start a stopped container
C) Create a new container
D) Export container filesystem

**Answer**: A

---

### Question 6
How do you remove all stopped containers?

A) `docker rm --all`
B) `docker container prune`
C) `docker clean containers`
D) `docker delete stopped`

**Answer**: B

---

### Question 7
What does the `-it` flag combination do in `docker run -it ubuntu bash`?

A) Interactive + TTY allocation
B) Image + Tag specification
C) Install + Test mode
D) Internal + Temporary

**Answer**: A

---

### Question 8
Which Docker command shows resource usage statistics for containers?

A) `docker info`
B) `docker stats`
C) `docker top`
D) `docker inspect`

**Answer**: B

---

### Question 9
What is the default network driver for Docker containers?

A) host
B) none
C) bridge
D) overlay

**Answer**: C

---

### Question 10
True or False: By default, containers on the default bridge network can resolve each other by container name.

A) True
B) False

**Answer**: B (False - requires custom bridge network for DNS)

---

## Section 2: Dockerfiles & Image Building (10 questions)

### Question 11
Which Dockerfile instruction sets the working directory for subsequent commands?

A) `CD`
B) `WORKDIR`
C) `DIR`
D) `SETDIR`

**Answer**: B

---

### Question 12
What's the difference between `COPY` and `ADD` in a Dockerfile?

A) No difference
B) `ADD` can extract tar files and download URLs
C) `COPY` is faster
D) `ADD` only works with local files

**Answer**: B

---

### Question 13
In a multi-stage Dockerfile, how do you copy files from a previous stage named "builder"?

A) `COPY builder:/app /app`
B) `COPY --from=builder /app /app`
C) `COPY --stage=builder /app /app`
D) `FROM builder COPY /app /app`

**Answer**: B

---

### Question 14
Which instruction creates a new layer in a Docker image?

A) `ENV`
B) `EXPOSE`
C) `RUN`
D) `CMD`

**Answer**: C

---

### Question 15
What's the best practice for installing packages in a Dockerfile?

A) `RUN apt-get update && apt-get install -y package && rm -rf /var/lib/apt/lists/*`
B) `RUN apt-get update` then `RUN apt-get install -y package`
C) `RUN apt-get install -y package`
D) Install packages after container starts

**Answer**: A

---

### Question 16
What's the difference between `CMD` and `ENTRYPOINT`?

A) No difference
B) `CMD` can be overridden easily, `ENTRYPOINT` defines the executable
C) `CMD` is for development, `ENTRYPOINT` for production
D) `ENTRYPOINT` is deprecated

**Answer**: B

---

### Question 17
What does `.dockerignore` do?

A) Ignores errors during build
B) Excludes files from build context
C) Prevents container from starting
D) Hides sensitive data

**Answer**: B

---

### Question 18
Which is the most optimized base image for production Python applications?

A) `python:3.11`
B) `python:3.11-slim`
C) `python:3.11-alpine`
D) `ubuntu:latest` with Python installed

**Answer**: B (slim is generally better than alpine for Python due to compatibility)

---

### Question 19
What's the purpose of `ARG` in a Dockerfile?

A) Define environment variables
B) Define build-time variables
C) Pass arguments to CMD
D) Configure arguments for ENTRYPOINT

**Answer**: B

---

### Question 20
True or False: Layer caching speeds up builds by reusing unchanged layers.

A) True
B) False

**Answer**: A

---

## Section 3: Docker Compose (8 questions)

### Question 21
What file format does Docker Compose use?

A) JSON
B) YAML
C) XML
D) TOML

**Answer**: B

---

### Question 22
How do you start all services defined in `docker-compose.yml` in detached mode?

A) `docker-compose start -d`
B) `docker-compose up --detach`
C) `docker-compose run -d`
D) `docker-compose deploy`

**Answer**: B

---

### Question 23
In Docker Compose, how does service A wait for service B to be healthy before starting?

```yaml
services:
  A:
    depends_on:
      ?
```

A) `B: required`
B) `B: wait`
C) `B: { condition: service_healthy }`
D) `B: true`

**Answer**: C

---

### Question 24
How do you scale a service to 3 replicas in Docker Compose?

A) `docker-compose scale service=3`
B) `docker-compose up --scale service=3`
C) `docker-compose replicas service 3`
D) Modify `docker-compose.yml` and set `replicas: 3`

**Answer**: B

---

### Question 25
Which Docker Compose command removes containers, networks, and volumes?

A) `docker-compose down`
B) `docker-compose down -v`
C) `docker-compose clean`
D) `docker-compose remove --all`

**Answer**: B

---

### Question 26
How do you reference environment variables from a `.env` file in `docker-compose.yml`?

A) `$ENV_VAR`
B) `${ENV_VAR}`
C) `{ENV_VAR}`
D) `@ENV_VAR`

**Answer**: B

---

### Question 27
What's the purpose of `networks` in Docker Compose?

A) Configure internet access
B) Define custom networks for service isolation
C) Set up VPN connections
D) Configure DNS servers

**Answer**: B

---

### Question 28
True or False: Docker Compose creates a default network for all services.

A) True
B) False

**Answer**: A

---

## Section 4: Networking (8 questions)

### Question 29
Which network driver provides automatic DNS resolution between containers?

A) Default bridge
B) Custom bridge
C) host
D) none

**Answer**: B

---

### Question 30
What does the `host` network mode do?

A) Creates isolated network
B) Container uses host's network stack directly
C) Provides internet access
D) Enables IPv6

**Answer**: B

---

### Question 31
How do you create a custom Docker network?

A) `docker network new mynetwork`
B) `docker network create mynetwork`
C) `docker create network mynetwork`
D) `docker network add mynetwork`

**Answer**: B

---

### Question 32
In Docker Compose, services can reach each other using:

A) IP addresses only
B) Service names as hostnames
C) Container IDs
D) MAC addresses

**Answer**: B

---

### Question 33
Which port mapping makes a service accessible only on localhost?

A) `-p 8080:80`
B) `-p 0.0.0.0:8080:80`
C) `-p 127.0.0.1:8080:80`
D) `-p localhost:8080:80`

**Answer**: C

---

### Question 34
What's the purpose of network aliases in Docker?

A) Rename networks
B) Provide alternative hostnames for containers
C) Configure IP addresses
D) Set up network bridges

**Answer**: B

---

### Question 35
How do you inspect a Docker network named "mynet"?

A) `docker network show mynet`
B) `docker network inspect mynet`
C) `docker inspect network mynet`
D) `docker network info mynet`

**Answer**: B

---

### Question 36
True or False: Containers on the same custom bridge network can communicate without port publishing.

A) True
B) False

**Answer**: A

---

## Section 5: Volumes & Data Persistence (6 questions)

### Question 37
What are the three types of Docker volumes/mounts?

A) Named, anonymous, temporary
B) Named volumes, bind mounts, tmpfs
C) Persistent, ephemeral, cached
D) Local, remote, distributed

**Answer**: B

---

### Question 38
Which mount type stores data in host memory (RAM)?

A) Named volume
B) Bind mount
C) tmpfs mount
D) cached mount

**Answer**: C

---

### Question 39
How do you create a named volume?

A) `docker volume new mydata`
B) `docker volume create mydata`
C) `docker create volume mydata`
D) `docker volume add mydata`

**Answer**: B

---

### Question 40
What's the recommended way to backup a Docker volume?

A) Copy from `/var/lib/docker/volumes/`
B) Use `docker volume backup`
C) Run container with volume mounted and create tar archive
D) Use `docker cp` on the volume

**Answer**: C

---

### Question 41
In which scenario would you use a bind mount instead of a named volume?

A) Database storage
B) Development with hot-reload
C) Production data
D) Shared data between containers

**Answer**: B

---

### Question 42
True or False: Named volumes persist after containers are removed.

A) True
B) False

**Answer**: A

---

## Section 6: Production & Security (8 questions)

### Question 43
Which is a security best practice for production containers?

A) Run as root user
B) Use `latest` tag
C) Run as non-root user
D) Disable health checks

**Answer**: C

---

### Question 44
What does the `--read-only` flag do?

A) Opens files in read-only mode
B) Makes root filesystem read-only
C) Prevents log writing
D) Disables network access

**Answer**: B

---

### Question 45
Which deployment strategy allows testing new version with small traffic percentage?

A) Blue-green
B) Rolling update
C) Canary deployment
D) Recreate

**Answer**: C

---

### Question 46
What's the purpose of `HEALTHCHECK` in a Dockerfile?

A) Check if image is healthy
B) Monitor container health
C) Validate Dockerfile syntax
D) Check disk space

**Answer**: B

---

### Question 47
How do you limit a container to use maximum 512MB of memory?

A) `docker run --memory 512M myapp`
B) `docker run --mem-limit 512 myapp`
C) `docker run --max-memory 512MB myapp`
D) `docker run -m 512M myapp`

**Answer**: D (or A, both are correct - D is shorter form)

---

### Question 48
What's the recommended logging driver option for production?

A) `none`
B) `json-file` with rotation
C) `console`
D) Unlimited `json-file`

**Answer**: B

---

### Question 49
Which tool scans Docker images for vulnerabilities?

A) docker lint
B) docker check
C) Trivy or Docker Scout
D) docker scan (deprecated)

**Answer**: C

---

### Question 50
True or False: Multi-stage builds help reduce final image size.

A) True
B) False

**Answer**: A

---

## Answer Key

### Section 1: Fundamentals
1. B  2. C  3. C  4. B  5. A  6. B  7. A  8. B  9. C  10. B

### Section 2: Dockerfiles
11. B  12. B  13. B  14. C  15. A  16. B  17. B  18. B  19. B  20. A

### Section 3: Compose
21. B  22. B  23. C  24. B  25. B  26. B  27. B  28. A

### Section 4: Networking
29. B  30. B  31. B  32. B  33. C  34. B  35. B  36. A

### Section 5: Volumes
37. B  38. C  39. B  40. C  41. B  42. A

### Section 6: Production
43. C  44. B  45. C  46. B  47. D  48. B  49. C  50. A

---

## Scoring Guide

- **45-50 correct (90-100%)**: Excellent! You have mastered Docker.
- **40-44 correct (80-88%)**: Good! You passed. Review missed topics.
- **35-39 correct (70-78%)**: Close! Review material and retake.
- **Below 35 (<70%)**: Review all lectures and exercises before retaking.

---

## Topics to Review by Score

**If you scored below 80%**, review these topics based on your weakest sections:

- **Section 1**: Review Lecture 01 (Docker Fundamentals), Exercise 01
- **Section 2**: Review Lecture 02 (Dockerfiles), Exercise 02
- **Section 3**: Review Lecture 03 (Docker Compose), Exercise 03
- **Section 4**: Review Lecture 04 (Networking), Exercise 04
- **Section 5**: Review Lecture 04 (Volumes), Exercise 05
- **Section 6**: Review Lecture 05 (Best Practices), Exercise 06

---

**Quiz Version**: 1.0
**Last Updated**: October 2025
**Time to Complete**: 90 minutes
**Passing Score**: 80% (40/50)
