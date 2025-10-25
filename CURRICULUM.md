# Junior AI Infrastructure Engineer - Detailed Curriculum

**Version:** 1.0.0
**Last Updated:** October 2025
**Total Duration:** 440 hours (11 weeks full-time, 22 weeks part-time)
**Difficulty Level:** Beginner to Intermediate
**Prerequisites:** Basic Python programming, command-line familiarity

---

## Table of Contents

- [Overview](#overview)
- [Learning Objectives](#learning-objectives)
- [Prerequisites](#prerequisites)
- [Module Breakdown](#module-breakdown)
- [Project Breakdown](#project-breakdown)
- [Assessment Strategy](#assessment-strategy)
- [Time Commitment](#time-commitment)
- [Career Outcomes](#career-outcomes)

---

## Overview

This curriculum is designed to transform beginners into job-ready Junior AI Infrastructure Engineers through a combination of theoretical modules and hands-on projects. The learning path is carefully scaffolded, starting with foundational concepts and progressively building to production-grade ML systems.

### Curriculum Philosophy

- **Hands-on first:** 66% of time spent on projects
- **Industry-aligned:** Skills match real job requirements
- **Portfolio-focused:** Every project is showcase-worthy
- **Progressive:** Each module/project builds on previous ones
- **Comprehensive:** Covers full ML infrastructure lifecycle

### Learning Approach

1. **Module Study:** Learn concepts through lectures and exercises
2. **Immediate Practice:** Apply concepts in guided exercises
3. **Knowledge Checks:** Quiz yourself on key concepts
4. **Project Application:** Use skills in real-world projects
5. **Assessment:** Self-assess and iterate

---

## Learning Objectives

### By the end of this curriculum, you will be able to:

#### Technical Skills

**ML Deployment:**
- Load and serve machine learning models via REST APIs
- Implement model versioning and A/B testing
- Optimize model serving for performance and cost
- Handle common ML serving challenges (batch processing, streaming)

**Containerization & Orchestration:**
- Containerize Python applications with Docker
- Build multi-stage Docker images for production
- Deploy applications to Kubernetes clusters
- Configure auto-scaling, load balancing, and health checks
- Manage Kubernetes resources with Helm charts

**MLOps Fundamentals:**
- Build end-to-end ML pipelines with Airflow/Prefect
- Track experiments systematically with MLflow
- Version datasets and models with DVC
- Implement data validation and quality checks
- Manage model lifecycle from training to retirement

**Monitoring & Observability:**
- Deploy Prometheus and Grafana for metrics
- Instrument applications with custom metrics
- Set up log aggregation with ELK Stack
- Configure alerts and on-call rotations
- Monitor ML-specific metrics (drift, accuracy, latency)

**Cloud Infrastructure:**
- Deploy to AWS, GCP, or Azure
- Manage cloud resources and costs
- Implement security best practices
- Use managed services (RDS, S3, etc.)
- Design for high availability

**CI/CD & Automation:**
- Build CI/CD pipelines with GitHub Actions
- Automate testing and deployment
- Implement infrastructure as code
- Manage secrets and environment configuration
- Handle rollbacks and disaster recovery

#### Professional Skills

- **Problem-solving:** Debug production issues systematically
- **Documentation:** Write clear technical documentation
- **Communication:** Explain technical concepts to non-technical stakeholders
- **Collaboration:** Work effectively in cross-functional teams
- **Time management:** Estimate tasks and meet deadlines

---

## Prerequisites

### Required Knowledge

**Python Programming:**
- Variables, data types, control flow
- Functions and modules
- Object-oriented programming basics
- File I/O and error handling
- Basic libraries (os, sys, json, requests)

**Command Line:**
- Navigate file system (cd, ls, pwd)
- File operations (cp, mv, rm, mkdir)
- Text manipulation (cat, grep, less)
- Process management (ps, kill, top)

**Basic Networking:**
- HTTP/HTTPS basics
- IP addresses and ports
- DNS fundamentals

### Recommended (Not Required)

- Prior experience with Git
- Familiarity with Linux/Unix systems
- Basic SQL knowledge
- Understanding of client-server architecture

### Assessment Quiz

Before starting, take the [Prerequisites Assessment Quiz](assessments/quizzes/prerequisites-quiz.md) to gauge your readiness.

**Passing score:** 70%
**If you score below 70%:** Review recommended preparatory materials

---

## Module Breakdown

### Module 001: Python Fundamentals for Infrastructure

**Duration:** 15 hours
**Difficulty:** Beginner
**Prerequisites:** None

#### Topics Covered

1. **Python Environment Setup** (2 hours)
   - Virtual environments (venv, conda)
   - Package management (pip, requirements.txt)
   - IDE setup and configuration

2. **Advanced Python for Infrastructure** (6 hours)
   - Type hints and mypy
   - Logging best practices
   - Configuration management
   - Error handling patterns
   - Working with APIs (requests library)

3. **Python for DevOps** (4 hours)
   - Subprocess management
   - File system operations
   - JSON/YAML parsing
   - Command-line arguments (argparse)

4. **Testing & Quality** (3 hours)
   - Unit testing with pytest
   - Code formatting (black, isort)
   - Linting (pylint, flake8)
   - Pre-commit hooks

#### Learning Outcomes

- Set up professional Python development environment
- Write production-quality Python code
- Implement proper logging and error handling
- Test and validate code before deployment

#### Resources

- [Lecture Notes](lessons/mod-001-python-fundamentals/lecture-notes/)
- [Exercises](lessons/mod-001-python-fundamentals/exercises/)
- [Quiz](lessons/mod-001-python-fundamentals/quizzes/)

---

### Module 002: Linux Essentials

**Duration:** 15 hours
**Difficulty:** Beginner
**Prerequisites:** None

#### Topics Covered

1. **Linux Fundamentals** (4 hours)
   - File system hierarchy
   - Users, groups, and permissions
   - Process management
   - System resources (CPU, memory, disk)

2. **Shell Scripting** (5 hours)
   - Bash basics
   - Variables and conditionals
   - Loops and functions
   - Script debugging

3. **System Administration** (4 hours)
   - Package management (apt, yum)
   - Service management (systemd)
   - Log management
   - Cron jobs and scheduling

4. **Networking Basics** (2 hours)
   - Network configuration (ifconfig, ip)
   - Firewall basics (iptables, ufw)
   - SSH and key management
   - Network troubleshooting (ping, netstat, curl)

#### Learning Outcomes

- Navigate and manage Linux systems confidently
- Write shell scripts for automation
- Troubleshoot common system issues
- Secure Linux servers

---

### Module 003: Git & Version Control

**Duration:** 10 hours
**Difficulty:** Beginner
**Prerequisites:** Command-line familiarity

#### Topics Covered

1. **Git Fundamentals** (3 hours)
   - Repository initialization
   - Commits and history
   - Branches and merging
   - Remote repositories

2. **Collaboration Workflows** (3 hours)
   - Pull requests and code review
   - Merge strategies
   - Conflict resolution
   - Git hooks

3. **Advanced Git** (2 hours)
   - Rebasing and cherry-picking
   - Stashing and cleaning
   - Bisect for debugging
   - Submodules

4. **GitHub Workflows** (2 hours)
   - Issue tracking
   - Project management
   - GitHub Actions basics
   - Documentation (README, CONTRIBUTING)

#### Learning Outcomes

- Use Git for version control professionally
- Collaborate on code with team members
- Implement Git-based workflows
- Leverage GitHub for project management

---

### Module 004: ML Basics (PyTorch/TensorFlow)

**Duration:** 20 hours
**Difficulty:** Beginner
**Prerequisites:** Python fundamentals

#### Topics Covered

1. **Machine Learning Overview** (4 hours)
   - Supervised vs unsupervised learning
   - Training, validation, testing
   - Common ML workflows
   - Model evaluation metrics

2. **PyTorch Basics** (6 hours)
   - Tensors and operations
   - Building neural networks
   - Training loops
   - Saving and loading models

3. **TensorFlow/Keras Basics** (6 hours)
   - TensorFlow fundamentals
   - Keras API
   - Model training and evaluation
   - Model serialization

4. **Model Deployment Preparation** (4 hours)
   - Model formats (ONNX, TorchScript, SavedModel)
   - Model optimization basics
   - Input/output handling
   - Model versioning

#### Learning Outcomes

- Understand ML model lifecycle
- Work with PyTorch and TensorFlow models
- Prepare models for deployment
- Convert between model formats

---

### Module 005: Docker & Containerization

**Duration:** 15 hours
**Difficulty:** Beginner
**Prerequisites:** Linux essentials

#### Topics Covered

1. **Docker Fundamentals** (4 hours)
   - Container vs VM
   - Docker architecture
   - Images and containers
   - Docker Hub and registries

2. **Dockerfile Best Practices** (5 hours)
   - Layer caching
   - Multi-stage builds
   - Security considerations
   - Image optimization

3. **Docker Compose** (3 hours)
   - Service definition
   - Networking
   - Volumes and persistence
   - Environment configuration

4. **Container Operations** (3 hours)
   - Container networking
   - Volume management
   - Resource limits
   - Logging and debugging

#### Learning Outcomes

- Containerize Python ML applications
- Write production-ready Dockerfiles
- Orchestrate multi-container applications
- Debug containerized applications

---

### Module 006: Kubernetes Introduction

**Duration:** 20 hours
**Difficulty:** Beginner+
**Prerequisites:** Docker fundamentals

#### Topics Covered

1. **Kubernetes Architecture** (4 hours)
   - Control plane and nodes
   - Pods, services, deployments
   - ConfigMaps and Secrets
   - Namespaces

2. **Deploying Applications** (6 hours)
   - Writing manifests (YAML)
   - Deployments and StatefulSets
   - Services and ingress
   - Persistent volumes

3. **Helm Package Manager** (5 hours)
   - Helm charts basics
   - Chart templates
   - Values and configuration
   - Chart deployment

4. **Kubernetes Operations** (5 hours)
   - kubectl basics
   - Debugging pods
   - Log aggregation
   - Resource monitoring
   - Auto-scaling (HPA)

#### Learning Outcomes

- Deploy applications to Kubernetes
- Write Kubernetes manifests
- Use Helm for package management
- Troubleshoot Kubernetes deployments

---

### Module 007: APIs & Web Services

**Duration:** 15 hours
**Difficulty:** Beginner
**Prerequisites:** Python fundamentals

#### Topics Covered

1. **REST API Fundamentals** (3 hours)
   - HTTP methods and status codes
   - API design principles
   - Authentication and authorization
   - Rate limiting

2. **FastAPI Framework** (6 hours)
   - Building REST APIs
   - Request/response models (Pydantic)
   - Dependency injection
   - Async operations
   - API documentation (OpenAPI)

3. **Flask Framework** (3 hours)
   - Flask basics
   - Routing and views
   - Request handling
   - Flask extensions

4. **API Testing** (3 hours)
   - Unit testing APIs (pytest)
   - Integration testing
   - Load testing (locust)
   - API documentation

#### Learning Outcomes

- Build production-grade REST APIs
- Implement authentication and authorization
- Test and document APIs
- Choose appropriate frameworks

---

### Module 008: Databases & SQL

**Duration:** 15 hours
**Difficulty:** Beginner
**Prerequisites:** Python fundamentals

#### Topics Covered

1. **SQL Fundamentals** (5 hours)
   - SELECT queries
   - Joins and aggregations
   - Indexes and optimization
   - Transactions

2. **PostgreSQL** (5 hours)
   - Installation and setup
   - Database design
   - Performance tuning
   - Backup and recovery

3. **NoSQL Basics** (3 hours)
   - Document databases (MongoDB)
   - Key-value stores (Redis)
   - Use cases for NoSQL

4. **Python Database Integration** (2 hours)
   - SQLAlchemy ORM
   - Connection pooling
   - Migration tools (Alembic)
   - Database testing

#### Learning Outcomes

- Design and query relational databases
- Choose appropriate database technologies
- Integrate databases with Python applications
- Implement database best practices

---

### Module 009: Monitoring & Logging Basics

**Duration:** 15 hours
**Difficulty:** Beginner+
**Prerequisites:** Docker, Kubernetes

#### Topics Covered

1. **Monitoring Fundamentals** (3 hours)
   - Metrics, logs, and traces
   - SLIs, SLOs, and SLAs
   - Monitoring strategies
   - Alert design

2. **Prometheus** (5 hours)
   - Architecture and components
   - Metrics collection
   - PromQL basics
   - Recording and alerting rules

3. **Grafana** (4 hours)
   - Dashboard creation
   - Visualization types
   - Variables and templating
   - Alert integration

4. **Logging Best Practices** (3 hours)
   - Structured logging
   - Log levels and formatting
   - Centralized logging
   - Log analysis

#### Learning Outcomes

- Implement monitoring for applications
- Create operational dashboards
- Set up alerting rules
- Analyze logs effectively

---

### Module 010: Cloud Platforms (AWS/GCP/Azure)

**Duration:** 20 hours
**Difficulty:** Beginner+
**Prerequisites:** Docker, basic networking

#### Topics Covered

1. **Cloud Fundamentals** (4 hours)
   - Cloud service models (IaaS, PaaS, SaaS)
   - Regions and availability zones
   - Identity and access management
   - Cost management

2. **Compute Services** (5 hours)
   - Virtual machines (EC2, Compute Engine, VMs)
   - Container services (ECS, GKE, AKS)
   - Serverless (Lambda, Cloud Functions, Functions)

3. **Storage and Databases** (5 hours)
   - Object storage (S3, Cloud Storage, Blob)
   - Managed databases (RDS, Cloud SQL, Azure SQL)
   - Caching (ElastiCache, Memorystore, Redis Cache)

4. **Networking and Security** (6 hours)
   - VPC and subnets
   - Load balancers
   - Security groups and firewalls
   - Secrets management
   - SSL/TLS certificates

#### Learning Outcomes

- Deploy applications to cloud platforms
- Choose appropriate cloud services
- Implement cloud security best practices
- Manage cloud costs

---

## Project Breakdown

### Project 01: Simple Model API Deployment

**Duration:** 60 hours
**Difficulty:** Beginner
**Prerequisites:** Modules 001-005

#### Overview

Build and deploy a REST API that serves machine learning predictions using Flask or FastAPI, containerize it with Docker, and deploy to a cloud platform.

#### Key Deliverables

- REST API with /predict endpoint
- Model loading and inference code
- Dockerfile and docker-compose.yml
- Basic monitoring and logging
- Cloud deployment (AWS/GCP/Azure)
- README with API documentation

#### Technologies

- Flask/FastAPI, PyTorch/TensorFlow, Docker, AWS/GCP/Azure, PostgreSQL

#### Assessment Weight

**Total:** 100 points
- Code Quality: 25 points
- Functionality: 30 points
- Deployment: 20 points
- Documentation: 15 points
- Performance: 10 points

[Full Project Details →](projects/project-01-simple-model-api/)

---

### Project 02: Kubernetes Model Serving

**Duration:** 80 hours
**Difficulty:** Beginner+
**Prerequisites:** Project 01, Module 006

#### Overview

Deploy your ML model API to Kubernetes with auto-scaling, load balancing, monitoring, and zero-downtime updates.

#### Key Deliverables

- Kubernetes manifests (Deployment, Service, Ingress)
- Helm chart
- Horizontal Pod Autoscaler configuration
- Prometheus metrics integration
- Grafana dashboard
- Load testing results

#### Technologies

- Kubernetes, Helm, Prometheus, Grafana, NGINX Ingress

#### Assessment Weight

**Total:** 100 points
- Infrastructure: 30 points
- Functionality: 25 points
- Monitoring: 20 points
- Documentation: 15 points
- Scalability: 10 points

[Full Project Details →](projects/project-02-kubernetes-serving/)

---

### Project 03: ML Pipeline with Experiment Tracking

**Duration:** 100 hours
**Difficulty:** Intermediate
**Prerequisites:** Projects 01-02, Modules 007-008

#### Overview

Build an end-to-end ML pipeline with data ingestion, preprocessing, training, evaluation, and deployment, using MLflow for experiment tracking and DVC for versioning.

#### Key Deliverables

- Airflow/Prefect DAGs for pipeline orchestration
- MLflow tracking and model registry
- DVC for data and model versioning
- Data validation with Great Expectations
- PostgreSQL for metadata storage
- Automated retraining pipeline

#### Technologies

- MLflow, Airflow/Prefect, DVC, Great Expectations, PostgreSQL, Docker, Kubernetes

#### Assessment Weight

**Total:** 100 points
- Pipeline Design: 25 points
- Experiment Tracking: 20 points
- Data Versioning: 15 points
- Code Quality: 20 points
- Documentation: 20 points

[Full Project Details →](projects/project-03-ml-pipeline-tracking/)

---

### Project 04: Monitoring & Alerting System

**Duration:** 80 hours
**Difficulty:** Intermediate
**Prerequisites:** Projects 01-03, Module 009

#### Overview

Deploy a comprehensive monitoring and alerting system for your ML infrastructure using Prometheus, Grafana, and ELK Stack.

#### Key Deliverables

- Prometheus deployment with custom metrics
- Grafana dashboards for ML metrics
- ELK Stack for log aggregation
- Alertmanager configuration
- PagerDuty/Slack integration
- Runbooks for common alerts

#### Technologies

- Prometheus, Grafana, Elasticsearch, Logstash, Kibana, Alertmanager, PagerDuty

#### Assessment Weight

**Total:** 100 points
- Metrics Collection: 25 points
- Dashboard Quality: 25 points
- Alerting: 20 points
- Log Management: 20 points
- Documentation: 10 points

[Full Project Details →](projects/project-04-monitoring-alerting/)

---

### Project 05: Production-Ready ML System (Capstone)

**Duration:** 120 hours
**Difficulty:** Intermediate+
**Prerequisites:** All previous projects and modules

#### Overview

Integrate all previous projects into a complete, production-ready ML system with CI/CD, security, high availability, and disaster recovery.

#### Key Deliverables

- End-to-end ML system architecture
- GitHub Actions CI/CD pipeline
- Infrastructure as Code (Terraform basics)
- Security implementation (HTTPS, secrets management)
- Multi-environment setup (dev, staging, prod)
- Disaster recovery plan
- Complete documentation
- Demo video presentation

#### Technologies

- All technologies from previous projects + GitHub Actions, Terraform, cert-manager, Vault, Velero

#### Assessment Weight

**Total:** 100 points
- System Integration: 30 points
- CI/CD: 20 points
- Security: 20 points
- Documentation: 20 points
- Presentation: 10 points

[Full Project Details →](projects/project-05-production-ml-capstone/)

---

## Assessment Strategy

### Continuous Assessment

- **Module Quizzes:** 10 quizzes (10 points each)
- **Project Assessments:** 5 projects (100 points each)
- **Total Possible:** 600 points

### Passing Criteria

- **Overall:** 70% (420/600 points)
- **Each Project:** 70/100 points minimum
- **Module Quizzes:** 7/10 points average

### Grading Scale

| Grade | Points | Percentage |
|-------|--------|------------|
| A (Excellent) | 540-600 | 90-100% |
| B (Good) | 480-539 | 80-89% |
| C (Satisfactory) | 420-479 | 70-79% |
| F (Not Passing) | <420 | <70% |

### Self-Assessment

Each project includes:
- **Detailed rubric** with scoring criteria
- **Self-assessment checklist** to verify completion
- **Peer review guidelines** for study groups
- **Example solutions** (in solutions repository)

---

## Time Commitment

### Full-Time Study (40 hours/week)

**Total Duration:** 11 weeks

- **Weeks 1-3:** Modules (10 modules × 15 hours avg ÷ 40 hours/week)
- **Weeks 4-11:** Projects (440 hours ÷ 40 hours/week)

### Part-Time Study (20 hours/week)

**Total Duration:** 22 weeks

- **Weeks 1-7:** Modules
- **Weeks 8-22:** Projects

### Flexible/Self-Paced

Complete at your own pace. Typical timelines:
- **Aggressive:** 8-10 weeks (50+ hours/week)
- **Moderate:** 16-20 weeks (20-25 hours/week)
- **Relaxed:** 6-12 months (10-15 hours/week)

---

## Career Outcomes

### Job Titles You'll Qualify For

- Junior ML Infrastructure Engineer
- Junior MLOps Engineer
- DevOps Engineer (ML focus)
- Cloud Infrastructure Engineer (entry-level)
- ML Platform Engineer (junior)

### Expected Salary Range (US, 2025)

- **Entry-level:** $67,000 - $95,000
- **With 1-2 years exp:** $80,000 - $110,000
- **Tech hubs (SF, NYC, Seattle):** +20-40% premium

### Next Steps After Completion

1. **Job Search:** Apply for Junior ML Infrastructure roles
2. **Portfolio:** Showcase capstone project to employers
3. **Continue Learning:** Advance to Level 1 (AI Infrastructure Engineer)
4. **Specialize:** Choose specialized track (MLOps, Security, Platform, Performance)
5. **Contribute:** Contribute to open-source ML infrastructure projects

---

**Ready to begin?** Start with [Module 001: Python Fundamentals](lessons/mod-001-python-fundamentals/)

**Questions?** See [FAQ](community/FAQ.md) or open an issue

---

**Last Updated:** October 2025
**Maintained By:** AI Infrastructure Curriculum Team
**Contact:** ai-infra-curriculum@joshua-ferguson.com
