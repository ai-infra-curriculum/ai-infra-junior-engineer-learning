# Project 01: Simple Model API Deployment

**Role:** Junior AI Infrastructure Engineer (Entry Level)
**Duration:** 60 hours (1-2 weeks full-time, 2-3 weeks part-time)
**Complexity:** Beginner
**Prerequisites:** Basic Python knowledge, familiarity with command line

---

## Project Overview

Welcome to your first AI Infrastructure project! In this project, you'll build and deploy a REST API that serves predictions from a pre-trained machine learning model. This is a foundational skill that every AI Infrastructure Engineer must master.

### What You'll Build

You'll create a production-ready API that:
- Loads a pre-trained image classification model (ResNet-50 or MobileNetV2)
- Accepts image uploads via HTTP requests
- Returns predictions with confidence scores
- Runs in a Docker container
- Deploys to a cloud platform (AWS, GCP, or Azure)
- Includes monitoring and logging

### Real-World Context

Data scientists train models locally on their laptops or in notebooks. Your job as an infrastructure engineer is to take those model files and make them available to users through a scalable, reliable API. This project simulates that exact scenario - you're the bridge between ML research and production deployment.

---

## Learning Objectives

By completing this project, you will:

1. **Understand ML Model Deployment** - Learn how to load and serve predictions from pre-trained models
2. **Build REST APIs** - Design and implement HTTP APIs using Flask or FastAPI
3. **Containerize Applications** - Package your application with Docker for consistent deployment
4. **Deploy to Cloud** - Get hands-on experience with cloud platforms (EC2, GCE, or Azure VMs)
5. **Implement Monitoring** - Add health checks, logging, and basic observability
6. **Write Documentation** - Create clear, comprehensive deployment documentation
7. **Apply Best Practices** - Learn industry standards for error handling, validation, and security

---

## Technology Stack

### Core Technologies
- **Python 3.11+** - Primary programming language
- **Flask 3.0+ or FastAPI 0.100+** - Web framework for REST API
- **PyTorch 2.0+ or TensorFlow 2.13+** - ML framework for model inference
- **Pillow (PIL)** - Image processing library
- **Docker 24.0+** - Containerization platform
- **Cloud Platform** - AWS EC2, GCP Compute Engine, or Azure VM

### Recommended Tools
- **VS Code** with Python extension for development
- **Postman or cURL** for API testing
- **Git/GitHub** for version control
- **Docker Desktop** for local container testing

---

## Project Requirements

### Functional Requirements

#### FR-1: Model Loading and Inference
- Load a pre-trained image classification model on startup
- Accept image uploads via HTTP POST
- Preprocess images according to model requirements
- Return top-5 predictions with class names and confidence scores
- Handle model loading errors gracefully

**Acceptance Criteria:**
- Model loads successfully on application startup
- Inference latency < 500ms for 224x224 images (CPU)
- Returns properly formatted JSON response
- Handles invalid image formats with HTTP 400 error

#### FR-2: REST API Implementation
- **`/predict`** endpoint for single-image inference
- **`/health`** endpoint for health checks
- **`/info`** endpoint returning model metadata
- Support multipart/form-data for image upload
- Request validation (file size limits, format checks)

**Acceptance Criteria:**
- All 3 endpoints respond correctly
- API follows RESTful conventions
- Request/response format documented
- Returns appropriate HTTP status codes

#### FR-3: Error Handling
- Structured error responses with error codes
- Handle out-of-memory errors gracefully
- Validate image inputs (corrupted, wrong format, too large)
- Implement request timeout handling (30 seconds max)

**Acceptance Criteria:**
- All error cases tested and handled
- No crashes on invalid input
- Clear error messages returned to users

### Non-Functional Requirements

#### NFR-1: Performance
- P99 latency < 1 second for predictions
- Support minimum 10 concurrent requests
- Memory usage < 2GB under normal load
- Startup time < 30 seconds

#### NFR-2: Reliability
- 99% uptime under normal conditions
- Graceful degradation when resources constrained
- Health check endpoint responds in < 100ms

#### NFR-3: Security
- Input validation to prevent injection attacks
- File size limits to prevent DOS (max 10MB per image)
- No execution of arbitrary code from uploaded files
- Basic rate limiting (optional: 100 requests/minute per IP)

#### NFR-4: Maintainability
- Code follows PEP 8 style guide
- Functions have docstrings
- Configuration externalized (not hardcoded)
- Logging at appropriate levels (INFO, WARNING, ERROR)

---

## Project Structure

```
project-01-simple-model-api/
├── README.md                      # This file
├── requirements.md                # Detailed requirements specification
├── architecture.md                # System architecture and design
├── src/
│   ├── README.md                  # Code structure guide
│   ├── app.py                     # Main Flask/FastAPI application (STUB)
│   ├── model_loader.py            # Model loading logic (STUB)
│   └── config.py                  # Configuration management (STUB)
├── tests/
│   ├── test_app.py                # API endpoint tests (STUB)
│   └── test_model.py              # Model functionality tests (STUB)
├── docker/
│   ├── Dockerfile                 # Container definition (STUB)
│   └── docker-compose.yml         # Local development setup
└── .env.example                   # Environment variable template
```

---

## Getting Started

### Prerequisites

Before starting this project, ensure you have:

1. **Python 3.11 or higher** installed
2. **Docker Desktop** installed and running
3. **Git** for version control
4. **A cloud account** (AWS Free Tier, GCP Free Trial, or Azure Free Account)
5. **Basic Python knowledge** (functions, classes, imports)
6. **Command line familiarity** (navigating directories, running commands)

### Setup Instructions

1. **Read All Documentation First**
   ```bash
   # Start with these files in order:
   # 1. README.md (this file) - Overview and setup
   # 2. requirements.md - Detailed requirements
   # 3. architecture.md - System design and architecture
   # 4. src/README.md - Code implementation guide
   ```

2. **Set Up Your Development Environment**
   ```bash
   # Create project directory
   mkdir model-api-deployment
   cd model-api-deployment

   # Create Python virtual environment
   python3.11 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

   # Install dependencies (you'll create this file)
   pip install flask torch torchvision pillow python-dotenv pytest
   ```

3. **Review the Code Stubs**
   - Navigate to `src/` directory
   - Read through all stub files
   - Each stub contains comprehensive TODO comments explaining what to implement
   - Type hints are provided to guide your implementation

4. **Implement the Application**
   - Start with `src/config.py` - configuration management
   - Then `src/model_loader.py` - model loading and inference
   - Finally `src/app.py` - REST API implementation
   - Write tests as you go in `tests/` directory

5. **Test Locally**
   ```bash
   # Run the application
   python src/app.py

   # In another terminal, test the endpoints
   curl http://localhost:5000/health
   curl http://localhost:5000/info
   curl -X POST -F "file=@test_image.jpg" http://localhost:5000/predict

   # Run tests
   pytest tests/
   ```

6. **Containerize**
   ```bash
   # Build Docker image
   docker build -f docker/Dockerfile -t model-api:v1.0 .

   # Run container
   docker run -p 5000:5000 model-api:v1.0

   # Or use Docker Compose
   docker-compose -f docker/docker-compose.yml up
   ```

7. **Deploy to Cloud**
   - Follow the deployment guide in `docs/DEPLOYMENT.md` (you'll create this)
   - Choose one cloud platform: AWS, GCP, or Azure
   - Set up security groups/firewall rules
   - Deploy your containerized application
   - Test the public endpoint

---

## Implementation Phases

### Phase 1: Local Development (20 hours)
- Set up development environment
- Implement model loading logic
- Build REST API with Flask/FastAPI
- Add error handling and validation
- Test locally with sample images
- Write basic documentation

### Phase 2: Containerization (15 hours)
- Create Dockerfile with optimizations
- Build and test Docker image
- Optimize image size (target < 2GB)
- Create docker-compose.yml for local development
- Test container locally

### Phase 3: Cloud Deployment (20 hours)
- Set up cloud account and permissions
- Provision VM instance (EC2/GCE/Azure)
- Install Docker on VM
- Deploy containerized application
- Configure security and networking
- Set up basic monitoring and logging

### Phase 4: Testing & Validation (5 hours)
- Functional testing of all endpoints
- Performance testing (latency, concurrency)
- Load testing with multiple requests
- Security validation
- Documentation review and updates

---

## Deliverables

Upon completion, you should have:

### 1. Source Code Repository
- [ ] Complete Python application with all features
- [ ] Unit tests with >80% coverage
- [ ] Dockerfile and docker-compose.yml
- [ ] Configuration files and examples
- [ ] .gitignore and requirements.txt

### 2. Documentation
- [ ] Comprehensive README with setup instructions
- [ ] API documentation (endpoints, request/response formats)
- [ ] Deployment guide with step-by-step instructions
- [ ] Architecture diagram
- [ ] Troubleshooting guide

### 3. Deployed Application
- [ ] Working API deployed to cloud platform
- [ ] Accessible via public URL
- [ ] Health checks passing
- [ ] Logs visible in cloud console
- [ ] 99% uptime during testing period

### 4. Demo
- [ ] 5-minute demo video or live demonstration
- [ ] Shows working API with sample predictions
- [ ] Explains architecture and key decisions
- [ ] Discusses challenges and learnings

---

## Assessment Criteria

Your project will be evaluated on:

- **Code Quality (25%)** - Organization, style, documentation, error handling, testing
- **Functionality (30%)** - API endpoints, model inference, validation, error responses, performance
- **Containerization (15%)** - Dockerfile quality, image size, build process
- **Deployment (20%)** - Cloud setup, accessibility, monitoring, security
- **Documentation (10%)** - README, API docs, deployment guide, architecture

**Passing Score:** 70/100 points

See `requirements.md` for the detailed rubric.

---

## Common Pitfalls to Avoid

1. **Hardcoding values** - Use environment variables for configuration
2. **No error handling** - Every endpoint should handle errors gracefully
3. **Large Docker images** - Optimize with multi-stage builds and slim base images
4. **Insecure deployment** - Always configure security groups/firewalls properly
5. **No logging** - Logging is essential for debugging production issues
6. **Memory leaks** - Clean up resources after each request
7. **Testing only happy paths** - Test error cases and edge cases thoroughly

---

## Time Management Tips

- **Don't rush Phase 1** - A solid local implementation saves debugging time later
- **Budget extra time for Docker** - Container debugging can be slow
- **Expect deployment failures** - Plan for 2-3 iterations to get cloud deployment right
- **Document as you go** - Don't leave documentation until the end
- **Keep a buffer** - Reserve 10-15 hours for unexpected issues

---

## Resources

### Official Documentation
- [Flask Documentation](https://flask.palletsprojects.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [PyTorch Documentation](https://pytorch.org/docs/)
- [Docker Documentation](https://docs.docker.com/)
- [AWS EC2 Documentation](https://docs.aws.amazon.com/ec2/)

### Tutorials
- Building ML APIs with Flask
- Docker for Machine Learning
- Deploying to AWS EC2

### Tools
- [Postman](https://www.postman.com/) - API testing
- [Docker Desktop](https://www.docker.com/products/docker-desktop) - Local containers
- [VS Code](https://code.visualstudio.com/) - Code editor

---

## Getting Help

- **Office Hours** - Attend weekly office hours for guidance
- **Discussion Forum** - Ask questions and help peers
- **Documentation** - Read the docs thoroughly before asking
- **Debugging** - Use print statements and logging liberally
- **Stack Overflow** - Search for similar problems (but don't copy code)

---

## Next Steps

After completing this project:

1. **Add to Portfolio** - Create a GitHub repository with a detailed README
2. **Write a Blog Post** - Document your experience and learnings
3. **Update Resume** - Add ML API deployment to your skills and projects
4. **Iterate** - Consider adding features like batch prediction, model versioning, or GPU acceleration
5. **Move to Project 2** - The next project builds on this foundation with Kubernetes

---

## Evaluation Checklist

Before submission, verify:

**Code Quality**
- [ ] Code follows PEP 8 style guide
- [ ] All functions have docstrings
- [ ] Type hints on all functions
- [ ] No hardcoded values
- [ ] Error handling implemented
- [ ] Unit tests written (>80% coverage)

**Functionality**
- [ ] `/health` endpoint works
- [ ] `/info` endpoint works
- [ ] `/predict` endpoint works
- [ ] Returns top-5 predictions
- [ ] Handles invalid inputs
- [ ] Meets performance targets

**Containerization**
- [ ] Dockerfile builds successfully
- [ ] Image size < 2GB
- [ ] Container runs without errors
- [ ] Health check configured

**Deployment**
- [ ] Deployed to cloud platform
- [ ] Accessible via public URL
- [ ] Security properly configured
- [ ] Logs visible

**Documentation**
- [ ] README complete
- [ ] API documentation complete
- [ ] Deployment guide complete
- [ ] Architecture diagram included

---

**Good luck! Remember: Start simple, test often, and ask for help when stuck.**

**Project Version:** 1.0
**Last Updated:** October 2025
**Maintained by:** AI Infrastructure Curriculum Team (ai-infra-curriculum@joshua-ferguson.com)
