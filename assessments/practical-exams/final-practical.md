# Final Practical Exam

## Overview

**Purpose**: Comprehensive assessment of all Junior AI Infrastructure Engineer competencies

**Duration**: 4 hours

**Prerequisites**: Completed all modules (1-4) and all projects (1-5)

**Passing Score**: 80/100 points

**Format**: Build a complete end-to-end ML infrastructure system

**Environment**: Your local development machine with Docker, Kubernetes (kind/minikube), and GitHub account

---

## Exam Instructions

### Before You Begin

1. **Environment setup**:
   ```bash
   mkdir final-exam
   cd final-exam
   git init
   git remote add origin [your-github-repo-url]
   ```

2. **Required tools**:
   - Python 3.9+
   - Docker and Docker Compose
   - Kubernetes (kind, minikube, or Docker Desktop with K8s)
   - kubectl configured
   - GitHub account
   - Git

3. **Time allocation**:
   - Setup and planning: 30 minutes
   - Core implementation: 150 minutes
   - Testing and debugging: 60 minutes
   - Documentation: 30 minutes
   - Final review: 30 minutes

4. **Submission requirements**:
   - GitHub repository with all code
   - Comprehensive README
   - Architecture documentation
   - Working deployment
   - CI/CD pipeline

### Exam Rules

- This is an **open-book** exam
- You may use official documentation
- No copying from other students
- No AI-generated complete solutions
- All work must be your own implementation
- Git commits should show your development process

---

## Project Requirements

### Scenario

**Company**: TechStartup AI
**Role**: Junior AI Infrastructure Engineer
**Task**: Build a production-ready ML model serving platform

Your team needs a platform to deploy and monitor multiple ML models. You've been tasked with creating a proof-of-concept system that demonstrates:
- Model serving capabilities
- Monitoring and observability
- Data persistence
- Scalability via Kubernetes
- Automated deployment via CI/CD

---

## Part 1: Core Application (35 points)

### Requirements

Build a multi-model serving platform with the following capabilities:

#### 1.1 Model Server Application (15 points)

**Features**:
- Serve at least 2 different ML models (e.g., sentiment analysis, text summarization)
- RESTful API with proper versioning (v1)
- Request/response validation
- Async processing for long-running predictions
- Model switching/selection via API

**Required Endpoints**:

```python
# Health and Status
GET /health
GET /api/v1/models  # List available models

# Predictions
POST /api/v1/predict
{
  "model": "sentiment-analysis",
  "text": "input text here",
  "version": "1.0.0"
}

# Response:
{
  "prediction_id": "uuid",
  "model": "sentiment-analysis",
  "result": {...},
  "confidence": 0.95,
  "processing_time_ms": 234
}

# History
GET /api/v1/predictions/{prediction_id}
GET /api/v1/predictions?model=sentiment-analysis&limit=10
```

**Evaluation Criteria**:
- [ ] All endpoints functional (6 points)
- [ ] Proper error handling with HTTP status codes (3 points)
- [ ] Input validation and sanitization (2 points)
- [ ] Clean, maintainable code structure (4 points)

#### 1.2 Database Layer (10 points)

**Requirements**:
- PostgreSQL database for storing predictions
- Schema includes: predictions, models, model_versions tables
- Database migrations (Alembic or similar)
- Connection pooling
- Proper indexing on frequently queried columns

**Schema Design**:

```sql
-- Models registry
CREATE TABLE models (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Model versions
CREATE TABLE model_versions (
    id SERIAL PRIMARY KEY,
    model_id INTEGER REFERENCES models(id),
    version VARCHAR(20) NOT NULL,
    artifact_path VARCHAR(255),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(model_id, version)
);

-- Predictions log
CREATE TABLE predictions (
    id UUID PRIMARY KEY,
    model_version_id INTEGER REFERENCES model_versions(id),
    input_data JSONB NOT NULL,
    output_data JSONB NOT NULL,
    confidence FLOAT,
    processing_time_ms INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Add appropriate indexes
```

**Evaluation Criteria**:
- [ ] Schema properly designed and normalized (4 points)
- [ ] Migrations work correctly (2 points)
- [ ] Efficient queries with indexes (2 points)
- [ ] Database initialization automated (2 points)

#### 1.3 Monitoring and Observability (10 points)

**Requirements**:
- Structured logging with appropriate log levels
- Prometheus metrics exposed
- Custom business metrics tracked
- Grafana dashboard (exported as JSON)

**Required Metrics**:
- Request count by endpoint and model
- Request latency (histogram)
- Error rate
- Model prediction confidence distribution
- Active models count
- Database connection pool status

**Evaluation Criteria**:
- [ ] Comprehensive logging implementation (3 points)
- [ ] Prometheus metrics properly exposed (3 points)
- [ ] Meaningful custom metrics (2 points)
- [ ] Grafana dashboard functional and useful (2 points)

---

## Part 2: Containerization and Orchestration (30 points)

### 2.1 Docker Implementation (15 points)

**Requirements**:
- Multi-stage Dockerfile for optimization
- Docker Compose for local development
- All services properly networked
- Health checks configured
- Environment-based configuration

**Docker Compose Services**:
- `api`: Your model serving application
- `postgres`: Database with persistence
- `prometheus`: Metrics collection
- `grafana`: Visualization (with provisioned dashboard)

**Evaluation Criteria**:
- [ ] Optimized Dockerfile (<1GB image) (4 points)
- [ ] Docker Compose properly configured (5 points)
- [ ] All services start and communicate (4 points)
- [ ] Proper use of volumes and networks (2 points)

### 2.2 Kubernetes Deployment (15 points)

**Requirements**:
- Kubernetes manifests for all components
- ConfigMaps for configuration
- Secrets for sensitive data
- Services and Ingress/NodePort
- Horizontal Pod Autoscaler (HPA)
- Resource limits and requests defined

**Required K8s Resources**:
```
k8s/
├── namespace.yaml
├── configmap.yaml
├── secret.yaml (template only, not actual secrets)
├── deployment-api.yaml
├── deployment-postgres.yaml
├── service-api.yaml
├── service-postgres.yaml
├── hpa.yaml
└── README.md
```

**Evaluation Criteria**:
- [ ] All manifests are valid and apply successfully (5 points)
- [ ] Application accessible in cluster (4 points)
- [ ] ConfigMaps and Secrets used properly (3 points)
- [ ] HPA configured and functional (3 points)

---

## Part 3: CI/CD Pipeline (20 points)

### Requirements

**GitHub Actions Workflow**:
- Triggered on push to main and pull requests
- Run linting and code quality checks
- Run unit and integration tests
- Build and push Docker image to registry
- Deploy to staging environment (can be simulated)

**Pipeline Stages**:

```yaml
# .github/workflows/ci-cd.yml
stages:
  - lint
  - test
  - build
  - deploy
```

**Required Checks**:
- Black/Flake8 for Python linting
- Pytest for unit tests
- Coverage report (minimum 60%)
- Docker image security scan (optional but bonus)
- Kubernetes manifest validation

**Evaluation Criteria**:
- [ ] Pipeline triggers correctly (3 points)
- [ ] All tests pass (5 points)
- [ ] Docker build and push works (5 points)
- [ ] Code quality checks implemented (4 points)
- [ ] Deployment automation (3 points)

---

## Part 4: Documentation and Best Practices (15 points)

### 4.1 Documentation (10 points)

**Required Documentation**:

1. **README.md** (4 points):
   - Project overview and purpose
   - Architecture diagram
   - Prerequisites
   - Quick start guide
   - API documentation
   - Troubleshooting section

2. **ARCHITECTURE.md** (3 points):
   - System architecture overview
   - Component descriptions
   - Data flow diagrams
   - Technology stack rationale
   - Scaling considerations

3. **DEPLOYMENT.md** (3 points):
   - Local development setup
   - Docker Compose deployment
   - Kubernetes deployment
   - Environment variables
   - Configuration options

**Evaluation Criteria**:
- [ ] README is comprehensive and clear (4 points)
- [ ] Architecture is well-documented (3 points)
- [ ] Deployment guide is detailed (3 points)

### 4.2 Code Quality and Best Practices (5 points)

**Requirements**:
- PEP 8 compliant code
- Type hints throughout
- Docstrings for functions/classes
- No hardcoded credentials
- Proper .gitignore
- Environment variables via .env
- Error handling throughout
- Security best practices followed

**Evaluation Criteria**:
- [ ] Code style and formatting (2 points)
- [ ] Documentation and comments (1 point)
- [ ] Security practices (1 point)
- [ ] Configuration management (1 point)

---

## Bonus Features (up to +15 points)

Implement any of these for additional credit:

- [ ] **Redis caching layer** (+3 points)
- [ ] **API rate limiting** (+2 points)
- [ ] **JWT authentication** (+3 points)
- [ ] **API request validation with Pydantic** (+2 points)
- [ ] **Async endpoint for long-running tasks** (+3 points)
- [ ] **Model A/B testing endpoint** (+4 points)
- [ ] **Helm chart for K8s deployment** (+5 points)
- [ ] **Load testing results and report** (+3 points)
- [ ] **Security scanning in CI/CD** (+2 points)

---

## Project Structure

Your final project should follow this structure:

```
final-exam/
├── .github/
│   └── workflows/
│       └── ci-cd.yml
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   └── sentiment.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   └── schemas.py
│   ├── database/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   └── connection.py
│   └── utils/
│       ├── __init__.py
│       ├── logging.py
│       └── metrics.py
├── tests/
│   ├── __init__.py
│   ├── test_api.py
│   ├── test_models.py
│   └── test_database.py
├── migrations/
│   └── (Alembic migrations)
├── k8s/
│   └── (Kubernetes manifests)
├── monitoring/
│   ├── prometheus.yml
│   └── grafana-dashboard.json
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── docs/
│   ├── ARCHITECTURE.md
│   └── DEPLOYMENT.md
├── scripts/
│   ├── setup.sh
│   └── deploy.sh
├── .env.example
├── .gitignore
├── requirements.txt
├── README.md
└── pyproject.toml (for Black, etc.)
```

---

## Testing Requirements

### Unit Tests

Create tests for:
- Model loading and prediction
- API endpoint responses
- Database operations
- Input validation

### Integration Tests

Test:
- End-to-end API flow
- Database persistence
- Multi-service interaction

### Minimum Coverage

- Overall: 60%
- Critical paths: 80%

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-cov pytest-asyncio

# Run tests with coverage
pytest --cov=src --cov-report=html

# View coverage report
open htmlcov/index.html
```

---

## Deployment Verification

### Docker Compose Verification

```bash
# Build and start all services
docker-compose up -d

# Check all services are healthy
docker-compose ps

# Test the API
curl http://localhost:8000/health
curl -X POST http://localhost:8000/api/v1/predict \
  -H "Content-Type: application/json" \
  -d '{"model": "sentiment-analysis", "text": "This is great!", "version": "1.0.0"}'

# Check Prometheus
curl http://localhost:9090

# Check Grafana
open http://localhost:3000
```

### Kubernetes Verification

```bash
# Apply all manifests
kubectl apply -f k8s/

# Check deployments
kubectl get deployments
kubectl get pods
kubectl get services

# Port forward to access
kubectl port-forward svc/api-service 8000:8000

# Test the API
curl http://localhost:8000/health

# Check logs
kubectl logs -l app=api
```

---

## Submission Checklist

Before submitting, verify:

### Functionality
- [ ] All API endpoints work correctly
- [ ] Docker Compose starts all services
- [ ] Kubernetes deployment succeeds
- [ ] CI/CD pipeline passes
- [ ] Tests achieve minimum coverage

### Code Quality
- [ ] Code follows PEP 8
- [ ] Type hints present
- [ ] No hardcoded secrets
- [ ] Error handling comprehensive
- [ ] Logging implemented

### Documentation
- [ ] README is complete
- [ ] Architecture documented
- [ ] Deployment guide included
- [ ] API endpoints documented
- [ ] Troubleshooting section present

### Repository
- [ ] Meaningful commit messages
- [ ] .gitignore properly configured
- [ ] .env.example provided
- [ ] No sensitive data committed

---

## Submission Instructions

1. **Commit your final code**:
   ```bash
   git add .
   git commit -m "Final exam submission"
   git push origin main
   ```

2. **Create a release**:
   ```bash
   git tag -a v1.0.0 -m "Final exam submission"
   git push origin v1.0.0
   ```

3. **Create SUBMISSION.md**:
   ```markdown
   # Final Exam Submission

   **Student**: [Your Name]
   **Date**: [Date]
   **GitHub Repository**: [URL]
   **Commit SHA**: [Full SHA]

   ## Time Breakdown
   - Planning: X hours
   - Implementation: X hours
   - Testing: X hours
   - Documentation: X hours
   - Total: X hours

   ## Self-Assessment
   Part 1 (Core Application): __ / 35
   Part 2 (Containerization): __ / 30
   Part 3 (CI/CD): __ / 20
   Part 4 (Documentation): __ / 15
   Bonus: __ / 15

   Total: __ / 100

   ## Challenges Faced
   1. [Challenge and how you solved it]
   2. [Challenge and how you solved it]

   ## What I Learned
   [Reflection on the exam]

   ## Additional Notes
   [Any important information for the reviewer]
   ```

4. **Submit your GitHub repository URL** via your learning platform

---

## Grading Rubric

| Component | Points | Weight | Your Score |
|-----------|--------|--------|------------|
| **Part 1: Core Application** | | | |
| - Model Server | 15 | 15% | |
| - Database Layer | 10 | 10% | |
| - Monitoring | 10 | 10% | |
| **Part 2: Container & K8s** | | | |
| - Docker | 15 | 15% | |
| - Kubernetes | 15 | 15% | |
| **Part 3: CI/CD** | 20 | 20% | |
| **Part 4: Documentation** | 15 | 15% | |
| **Subtotal** | **100** | **100%** | |
| **Bonus** | +15 | +15% | |
| **Total** | **115** | **115%** | |

### Pass/Fail Criteria

- **90-100+**: Exceptional - Exceeds all expectations
- **80-89**: Excellent - Fully competent, ready for next level
- **70-79**: Good - Competent with minor gaps
- **60-69**: Adequate - Basic competency, review recommended
- **<60**: Insufficient - Significant gaps, retake required

**Minimum to pass**: 80/100

---

## Common Issues and Tips

### Performance Tips
- Use connection pooling for database
- Implement caching where appropriate
- Optimize Docker image size
- Use async processing for heavy tasks

### Debugging Tips
- Check logs: `docker-compose logs -f [service]`
- Test incrementally as you build
- Use `kubectl describe` for K8s issues
- Verify environment variables are set

### Time Management
- Start with core functionality
- Get Docker working first
- Then move to Kubernetes
- Leave CI/CD and bonuses for later
- Budget time for documentation

### Security Reminders
- Never commit secrets
- Use environment variables
- Run containers as non-root
- Validate all inputs
- Use HTTPS in production (document only)

---

## After the Exam

### If You Pass (80%+)
Congratulations! You've demonstrated competency as a Junior AI Infrastructure Engineer.

**Next steps**:
1. Review feedback
2. Add this project to your portfolio
3. Continue to intermediate level
4. Share your work (GitHub, LinkedIn)

### If Additional Work Needed (<80%)
Don't be discouraged! Use this as a learning opportunity.

**Action plan**:
1. Review detailed feedback
2. Identify specific weak areas
3. Revisit relevant modules
4. Practice specific skills
5. Retake after 2 weeks

---

## Resources

### Documentation
- [Flask](https://flask.palletsprojects.com/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Docker](https://docs.docker.com/)
- [Kubernetes](https://kubernetes.io/docs/)
- [Prometheus](https://prometheus.io/docs/)
- [GitHub Actions](https://docs.github.com/en/actions)

### Tools
- [Docker Desktop](https://www.docker.com/products/docker-desktop)
- [kubectl Cheat Sheet](https://kubernetes.io/docs/reference/kubectl/cheatsheet/)
- [kind](https://kind.sigs.k8s.io/) or [minikube](https://minikube.sigs.k8s.io/)

---

## Questions During the Exam

If you encounter issues:
1. **Technical problems**: Document in SUBMISSION.md
2. **Ambiguous requirements**: Make reasonable assumptions and document them
3. **Time constraints**: Prioritize core requirements over bonuses

---

## Academic Integrity

This exam tests your individual competency:
- Use official documentation freely
- Don't copy from other students
- Don't use AI to generate complete solutions
- Show your work through Git commits
- Document any external code snippets used

**Violation of academic integrity will result in a failing grade.**

---

## Final Checklist

Before submitting, ensure:

- [ ] Application runs successfully with Docker Compose
- [ ] Application deploys to Kubernetes
- [ ] All tests pass
- [ ] CI/CD pipeline succeeds
- [ ] README is comprehensive
- [ ] No secrets in repository
- [ ] Git history shows your development process
- [ ] SUBMISSION.md completed
- [ ] Repository is public or shared with instructors

---

**Good luck!** This exam represents everything you've learned. Take your time, be methodical, and demonstrate your skills. You've got this!

---

## Evaluation Timeline

- **Submission deadline**: [As assigned]
- **Initial review**: Within 5 business days
- **Feedback provided**: Within 7 business days
- **Retake available**: 2 weeks after feedback

---

**Remember**: This is a comprehensive test of practical skills. Focus on making things work first, then optimize and polish. Quality over quantity, but completeness matters for passing.
