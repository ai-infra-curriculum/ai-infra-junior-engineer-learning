# Module 005: Docker and Containers

## Module Overview

Containerization has revolutionized how we build, ship, and run applications, especially in AI/ML infrastructure. This module provides comprehensive training in Docker, the leading containerization platform, teaching you to package applications with their dependencies, manage container lifecycles, and orchestrate multi-container applications.

You'll learn container fundamentals, Docker architecture, best practices for creating efficient container images, and how to use Docker Compose for multi-container applications. These skills are essential for modern infrastructure engineering, enabling consistent environments across development, testing, and production.

By the end of this module, you'll be confident containerizing applications, building optimized images, managing container networks and storage, and using containers in AI/ML workflows.

## Learning Objectives

By completing this module, you will be able to:

1. **Understand containerization concepts** and how containers differ from virtual machines
2. **Install and configure Docker** across different platforms
3. **Work with Docker images** including pulling, building, and publishing
4. **Create Dockerfiles** following best practices for efficiency and security
5. **Manage container lifecycle** including running, stopping, and monitoring containers
6. **Configure container networking** for communication between containers and external systems
7. **Manage persistent data** using volumes and bind mounts
8. **Use Docker Compose** to define and run multi-container applications
9. **Optimize images** for size, security, and build performance
10. **Apply containers to AI/ML workflows** including model serving and training

## Prerequisites

- Completion of Module 002 (Linux Essentials) required
- Completion of Module 003 (Git Version Control) recommended
- Completion of Module 001 (Python Fundamentals) recommended
- Comfort with command-line interfaces
- Basic understanding of networking concepts

**Recommended Setup:**
- Docker Desktop (Windows/Mac) or Docker Engine (Linux) version 20.10+
- At least 8GB RAM (16GB recommended for AI/ML containers)
- 50GB+ available disk space
- Terminal access
- Text editor or IDE

## Time Commitment

- **Total Estimated Time:** 40-50 hours
- **Lectures & Reading:** 15-18 hours
- **Hands-on Exercises:** 20-25 hours
- **Projects:** 5-7 hours

**Recommended Pace:**
- Part-time (5-10 hrs/week): 4-6 weeks
- Full-time (20-30 hrs/week): 2-3 weeks

Container mastery requires hands-on practice. Expect to spend time experimenting, troubleshooting, and building real-world scenarios.

## Module Structure

### Week 1: Docker Fundamentals
- **Topics:** Container concepts, Docker architecture, basic commands
- **Key Skills:** pull, run, ps, logs, stop, rm
- **Practice:** Running containers, basic lifecycle management

### Week 2: Building Images
- **Topics:** Dockerfiles, image layers, build optimization
- **Key Skills:** build, tag, push, Dockerfile syntax
- **Practice:** Creating custom images, multi-stage builds

### Week 3: Networking and Storage
- **Topics:** Container networking, volumes, bind mounts
- **Key Skills:** network commands, volume management, data persistence
- **Practice:** Multi-container communication, data management

### Week 4: Docker Compose and Advanced Topics
- **Topics:** Docker Compose, security, optimization, AI/ML use cases
- **Key Skills:** docker-compose.yml, best practices, production considerations
- **Practice:** Multi-container applications, ML model serving

## Detailed Topic Breakdown

### 1. Introduction to Containers (5-6 hours)

#### 1.1 Containerization Fundamentals
- What are containers?
- History of containerization (chroot, LXC, Docker)
- Containers vs virtual machines
- Benefits of containerization
- Use cases in AI/ML infrastructure
- Container ecosystem overview

#### 1.2 Docker Architecture
- Docker Engine components
- Client-server architecture
- containerd and runc
- Docker daemon
- Docker CLI
- Docker registries (Docker Hub, private registries)
- Image and container relationship

#### 1.3 Installing Docker
- Installation on Linux
- Docker Desktop for Windows/Mac
- Post-installation configuration
- Running Docker without sudo (Linux)
- Verifying installation
- Docker version management
- Resource allocation and limits

#### 1.4 Container Images and Registries
- Understanding images and layers
- Image naming and tagging conventions
- Docker Hub and public registries
- Official vs community images
- Base images (Alpine, Ubuntu, Python)
- Image security considerations
- Registry authentication

### 2. Working with Docker Containers (7-9 hours)

#### 2.1 Running Containers
- Basic `docker run` command
- Interactive vs detached mode
- Container naming
- Port mapping and publishing
- Environment variables
- Resource constraints (CPU, memory)
- Container restart policies

#### 2.2 Managing Container Lifecycle
- Listing containers (`docker ps`)
- Starting and stopping containers
- Pausing and unpausing
- Restarting containers
- Removing containers
- Container logs
- Executing commands in running containers

#### 2.3 Container Inspection and Debugging
- Inspecting containers
- Viewing logs
- Attaching to containers
- Copying files to/from containers
- Container stats and monitoring
- Debugging container issues
- Common troubleshooting scenarios

#### 2.4 Working with Images
- Pulling images from registries
- Searching for images
- Listing local images
- Removing images
- Image history and layers
- Tagging images
- Saving and loading images

### 3. Building Docker Images (9-11 hours)

#### 3.1 Dockerfile Basics
- Dockerfile syntax and structure
- FROM instruction (base images)
- RUN instruction (commands during build)
- COPY and ADD instructions
- WORKDIR instruction
- ENV instruction (environment variables)
- EXPOSE instruction (ports)
- CMD vs ENTRYPOINT
- Understanding build context

#### 3.2 Image Layers and Caching
- How Docker layers work
- Layer caching mechanism
- Optimizing layer order
- Invalidating cache
- BuildKit and cache management
- Layer size considerations
- .dockerignore file

#### 3.3 Multi-Stage Builds
- Why multi-stage builds?
- Syntax and structure
- Naming build stages
- Copying artifacts between stages
- Use cases (compile languages, minimize size)
- Multi-stage for AI/ML applications
- Build targets

#### 3.4 Building Efficient Images
- Minimizing image size
- Choosing appropriate base images
- Alpine Linux advantages
- Combining RUN commands
- Removing unnecessary files
- Security scanning
- Best practices for production images

#### 3.5 Building Images for Python/AI Applications
- Python base images
- Installing dependencies efficiently
- Requirements.txt in Docker
- Poetry and Pipenv in containers
- CUDA and GPU support
- ML framework images (PyTorch, TensorFlow)
- Model packaging in images

#### 3.6 Publishing Images
- Pushing to Docker Hub
- Private registry setup
- Authentication and authorization
- Image versioning strategies
- Automated builds
- CI/CD integration
- Image signing and trust

### 4. Container Networking (6-8 hours)

#### 4.1 Docker Networking Fundamentals
- Default networking behavior
- Network types (bridge, host, none)
- Understanding bridge networks
- Container DNS
- Port mapping deep dive
- Network isolation
- Inspecting networks

#### 4.2 User-Defined Networks
- Creating custom networks
- Connecting containers to networks
- Network aliases
- Multi-network containers
- Network drivers
- Overlay networks (Swarm preview)
- Service discovery

#### 4.3 Container Communication
- Container-to-container communication
- Using container names as hostnames
- Linking containers (legacy)
- Environment variables for configuration
- Service discovery patterns
- Load balancing basics
- Network security

#### 4.4 Advanced Networking
- Host networking mode
- macvlan and ipvlan
- Network troubleshooting
- Network performance
- Exposing services externally
- Reverse proxy patterns (nginx)
- Network policies

### 5. Container Storage and Data Persistence (5-7 hours)

#### 5.1 Understanding Container Storage
- Container filesystem layers
- Ephemeral vs persistent data
- Storage drivers
- Union filesystems
- Copy-on-write mechanism
- Storage performance considerations

#### 5.2 Docker Volumes
- Creating and managing volumes
- Named volumes vs anonymous volumes
- Volume drivers
- Listing and inspecting volumes
- Removing unused volumes
- Volume backup and restore
- Volume performance

#### 5.3 Bind Mounts
- What are bind mounts?
- When to use bind mounts
- Read-only mounts
- Bind mounts for development
- Security considerations
- Host path concerns
- Permissions issues

#### 5.4 tmpfs Mounts
- In-memory storage
- Use cases for tmpfs
- Performance benefits
- Size limitations
- Sensitive data handling

#### 5.5 Data Management Patterns
- Database containers and persistence
- Backup strategies
- Data volume containers (legacy)
- Volume sharing between containers
- Data initialization
- Migration strategies
- Managing large datasets (ML training data)

### 6. Docker Compose (7-9 hours)

#### 6.1 Introduction to Docker Compose
- Why Docker Compose?
- Compose vs individual docker run commands
- Installing Docker Compose
- Compose file format and versions
- docker-compose.yml structure
- Common use cases
- Compose CLI overview

#### 6.2 Defining Services
- Service configuration
- Image vs build
- Environment variables
- Port mapping
- Volume mounting
- Networks in Compose
- Dependencies and startup order

#### 6.3 Compose Commands
- Starting services (`up`)
- Stopping and removing (`down`)
- Viewing logs
- Executing commands
- Scaling services
- Building images
- Service status and management

#### 6.4 Multi-Container Applications
- Web application with database
- Application with message queue
- Microservices architecture
- Service dependencies
- Health checks
- Restart policies
- Resource limits

#### 6.5 Development Workflows
- Compose for development environments
- Hot reloading and bind mounts
- Override files (docker-compose.override.yml)
- Multiple Compose files
- Environment-specific configurations
- Development vs production configs
- Testing with Compose

#### 6.6 Compose for AI/ML Applications
- ML training pipeline with Compose
- Model serving architecture
- Jupyter notebook environment
- ML workflow orchestration
- GPU access in Compose
- Distributed training setup
- MLflow with Compose

### 7. Docker Best Practices and Security (4-5 hours)

#### 7.1 Dockerfile Best Practices
- Official Docker best practices
- Minimizing layers
- Ordering instructions efficiently
- Using specific base image versions
- Non-root users
- Health checks
- Labels and metadata

#### 7.2 Security Considerations
- Running as non-root
- Scanning for vulnerabilities
- Secrets management
- Minimizing attack surface
- Read-only filesystems
- Security scanning tools
- AppArmor and SELinux

#### 7.3 Production Readiness
- Health checks and monitoring
- Logging best practices
- Resource limits
- Restart policies
- Graceful shutdown
- Configuration management
- Twelve-factor app principles

#### 7.4 Image Optimization
- Layer caching strategies
- Multi-stage build patterns
- Minimizing image size
- Build arguments
- Squashing layers (when appropriate)
- Image tagging strategies
- Registry cleanup

#### 7.5 Performance Tuning
- Storage driver selection
- Network performance
- Resource allocation
- Build performance
- Registry caching
- Image pulling strategies
- Monitoring container performance

## Lecture Outline

> **Status Update (2025-10-29):** All 7 comprehensive lecture notes are now complete and available! Each lecture includes detailed coverage of containerization concepts with practical ML infrastructure examples.

This module includes **7 lectures** and **8 exercises** covering Docker and container fundamentals:

### Lecture 1: Introduction to Containers and Docker (90 min)
- Containerization concepts
- Containers vs VMs
- Docker architecture
- Installation and setup
- First container
- **Lab:** Running your first containers

### Lecture 2: Working with Containers (90 min)
- Container lifecycle
- Basic Docker commands
- Managing containers
- Container inspection
- Logs and debugging
- **Lab:** Container management exercises

### Lecture 3: Building Docker Images (120 min)
- Dockerfile fundamentals
- Image layers and caching
- Building images
- Best practices
- .dockerignore
- **Lab:** Creating custom images

### Lecture 4: Multi-Stage Builds and Optimization (90 min)
- Multi-stage build concept
- Image size optimization
- Security considerations
- Building Python applications
- **Lab:** Optimized application images

### Lecture 5: Container Networking (90 min)
- Networking fundamentals
- Network types
- Container communication
- Port mapping
- User-defined networks
- **Lab:** Multi-container networking

### Lecture 6: Data Persistence (90 min)
- Storage options
- Volumes vs bind mounts
- Data management patterns
- Backup and restore
- Performance considerations
- **Lab:** Persistent data scenarios

### Lecture 7: Docker Compose (120 min)
- Compose fundamentals
- docker-compose.yml syntax
- Multi-container applications
- Service orchestration
- Development workflows
- **Lab:** Complete application stack

### Lecture 8: Containers for AI/ML (90 min)
- ML container considerations
- GPU support
- Model serving containers
- Training pipelines
- Jupyter environments
- Production ML with containers
- **Lab:** Containerized ML application

## Hands-On Exercises

> **Status Update (2025-10-29):** All 8 comprehensive exercises are now complete! Each exercise includes step-by-step instructions with ML infrastructure scenarios and validation checkpoints.

This module includes **8 exercises** organized into progressive skill development:

### Exercise Categories

#### Basic Container Operations (8 exercises)
1. Running and managing containers
2. Working with logs and debugging
3. Port mapping and networking
4. Environment variables
5. Resource limits
6. Container inspection
7. Image management
8. Registry operations

#### Building Images (8 exercises)
9. Basic Dockerfile creation
10. Layer optimization
11. Multi-stage builds
12. Python application containerization
13. Web application with dependencies
14. Optimizing image size
15. Security scanning
16. Publishing to registry

#### Networking and Storage (8 exercises)
17. Custom networks
18. Container communication
19. Volume management
20. Bind mount scenarios
21. Multi-container networking
22. Database persistence
23. Backup and restore
24. Performance testing

#### Docker Compose (8 exercises)
25. Basic Compose application
26. Web app with database
27. Microservices architecture
28. Development environment
29. Production configuration
30. ML training pipeline
31. Model serving stack
32. Complete ML workflow

## Assessment and Evaluation

### Knowledge Checks
- Quiz after each major section (7 quizzes total)
- Dockerfile syntax questions
- Networking scenario analysis
- Troubleshooting exercises
- Best practices evaluation

### Practical Assessments
- **Container Operations:** Execute complete container lifecycle management
- **Image Building:** Create optimized, production-ready images
- **Networking:** Configure multi-container communication
- **Compose:** Deploy complete application stacks
- **ML Application:** Containerize and deploy ML model

### Competency Criteria
To complete this module successfully, you should be able to:
- Run and manage Docker containers confidently
- Write efficient Dockerfiles following best practices
- Build optimized images with multi-stage builds
- Configure container networking for various scenarios
- Manage persistent data using volumes
- Use Docker Compose for multi-container applications
- Apply security best practices
- Containerize Python/ML applications
- Troubleshoot common container issues
- Deploy containerized applications

### Capstone Project
**Containerized ML Application:**
Build a complete ML application demonstrating:
- Optimized Docker images
- Model serving container
- Training pipeline container
- Data persistence
- Container networking
- Docker Compose orchestration
- Production best practices
- Documentation

## Resources and References

> **Note:** See `resources/recommended-reading.md` for a comprehensive list of learning materials, books, and online resources.

### Essential Resources
- Official Docker documentation
- Docker Hub
- Play with Docker (browser-based playground)
- Docker CLI reference

### Recommended Books
- "Docker Deep Dive" by Nigel Poulton
- "Docker in Action" by Jeff Nickoloff
- "Docker: Up & Running" by Karl Matthias and Sean Kane

### Online Learning
- Docker's official tutorials
- Docker Labs (hands-on tutorials)
- Katacoda Docker scenarios
- Docker Mastery course

### Tools
- Docker Desktop
- Docker Extensions
- Dive (image layer analysis)
- Hadolint (Dockerfile linter)
- Trivy (security scanner)

## Getting Started

### Step 1: Install Docker
1. Download Docker Desktop (Windows/Mac) or Docker Engine (Linux)
2. Complete installation
3. Verify with `docker version`
4. Run hello-world container
5. Allocate adequate resources

### Step 2: Familiarize with CLI
1. Practice basic commands
2. Explore Docker Hub
3. Pull sample images
4. Run containers interactively
5. View logs and inspect containers

### Step 3: Begin with Lecture 1
- Read container fundamentals
- Understand Docker architecture
- Complete first container lab
- Experiment with commands

### Step 4: Build Progressively
- Work through exercises sequentially
- Create Dockerfiles
- Experiment with networking
- Practice with Compose
- Build real applications

## Tips for Success

1. **Practice Regularly:** Use Docker for personal projects
2. **Read Dockerfiles:** Study images on Docker Hub
3. **Experiment Safely:** Containers are disposable; try things out
4. **Optimize Early:** Practice efficient Dockerfile writing from the start
5. **Understand Layers:** Visualize how layers work
6. **Use .dockerignore:** Keep build contexts clean
7. **Version Everything:** Tag images appropriately
8. **Monitor Resources:** Watch disk space and running containers
9. **Security First:** Never commit secrets, run as non-root
10. **Document:** Comment Dockerfiles and Compose files

## Next Steps

After completing this module, you'll be ready to:
- **Module 006:** Basic ML Concepts (containerize ML models)
- **Module 009:** Monitoring Basics (monitor containerized services)
- **Module 010:** Cloud Platforms (run containers in cloud)
- **Later:** Kubernetes and container orchestration

## Development Status

**Current Status:** Template phase - comprehensive structure in place

**Available Now:**
- Complete module structure
- Detailed topic breakdown
- Lecture outline
- Exercise framework

**In Development:**
- Full lecture notes with examples
- Step-by-step exercises
- Dockerfile templates
- Compose file examples
- ML-specific scenarios
- Video demonstrations

**Planned Updates:**
- Kubernetes preview
- Advanced networking
- Production deployment patterns
- CI/CD integration
- GPU container setup

## Feedback and Contributions

Contributions and feedback welcome. Help improve this module by:
- Reporting issues
- Suggesting improvements
- Sharing Dockerfile examples
- Contributing exercises

---

**Module Maintainer:** AI Infrastructure Curriculum Team
**Contact:** ai-infra-curriculum@joshua-ferguson.com
**Last Updated:** 2025-10-18
**Version:** 1.0.0-template
