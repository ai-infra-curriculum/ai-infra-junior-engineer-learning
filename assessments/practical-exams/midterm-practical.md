# Midterm Practical Exam

## Overview

**Purpose**: Assess hands-on competency in Docker containerization, basic model deployment, and troubleshooting

**Duration**: 3 hours

**Prerequisites**: Completed Modules 1-2 and Projects 1-2

**Passing Score**: 75/100 points

**Format**: Hands-on coding and deployment tasks

**Environment**: Your local development machine with Docker installed

---

## Exam Instructions

### Before You Begin

1. **Setup your workspace**:
   ```bash
   mkdir midterm-exam
   cd midterm-exam
   git init
   ```

2. **Required tools**:
   - Python 3.9+
   - Docker and Docker Compose
   - Text editor/IDE
   - Git

3. **Time management**:
   - Task 1: 45 minutes
   - Task 2: 60 minutes
   - Task 3: 45 minutes
   - Review/testing: 30 minutes

4. **Submission requirements**:
   - All code in a Git repository
   - README.md with setup instructions
   - Working Docker containers
   - Documentation of any issues encountered

### General Rules

- You may use official documentation
- No collaboration with others
- No pre-built solutions
- All code must be your own work
- Save your work frequently

---

## Task 1: Containerize a Machine Learning Model (30 points)

### Scenario

You've been provided with a Python script that loads a pre-trained sentiment analysis model. Your task is to containerize this application and expose it via a REST API.

### Provided Code

**model_server.py** (you need to create this based on requirements):

```python
# TODO: Import necessary libraries (Flask/FastAPI, transformers, etc.)

# TODO: Load a pre-trained sentiment analysis model
# Suggestion: Use transformers library with a small model like
# "distilbert-base-uncased-finetuned-sst-2-english"

# TODO: Create API endpoint POST /predict
# Input: {"text": "some text to analyze"}
# Output: {"sentiment": "POSITIVE/NEGATIVE", "score": 0.95}

# TODO: Create health check endpoint GET /health

# TODO: Run the server on port 8000
```

### Requirements

1. **Application** (12 points):
   - [ ] Implement the model server with all TODOs completed
   - [ ] POST /predict endpoint accepts text and returns sentiment
   - [ ] GET /health endpoint returns service status
   - [ ] Proper error handling for invalid inputs
   - [ ] Model loads successfully on startup

2. **Dockerfile** (10 points):
   - [ ] Uses appropriate base image (Python 3.9+)
   - [ ] Installs all dependencies
   - [ ] Copies application code
   - [ ] Exposes correct port (8000)
   - [ ] Runs as non-root user
   - [ ] Image size < 2GB

3. **Documentation** (5 points):
   - [ ] README with build instructions
   - [ ] How to run the container
   - [ ] Example API requests
   - [ ] Known limitations

4. **Testing** (3 points):
   - [ ] Successfully builds without errors
   - [ ] Container runs and stays healthy
   - [ ] API responds to requests correctly

### Deliverables

```
task1/
├── model_server.py
├── requirements.txt
├── Dockerfile
├── .dockerignore
└── README.md
```

### Evaluation Criteria

| Criterion | Points | Your Score |
|-----------|--------|------------|
| Working API endpoints | 6 | |
| Error handling | 3 | |
| Model loads correctly | 3 | |
| Dockerfile best practices | 6 | |
| Image optimization | 4 | |
| Documentation quality | 5 | |
| Successfully runs | 3 | |
| **Total** | **30** | |

---

## Task 2: Multi-Container Application with Monitoring (40 points)

### Scenario

Extend your Task 1 application to include a PostgreSQL database for logging predictions and Prometheus for monitoring. Use Docker Compose to orchestrate all services.

### Requirements

1. **Enhanced Application** (15 points):
   - [ ] Modified model_server.py to log predictions to PostgreSQL
   - [ ] Database schema with predictions table (id, text, sentiment, score, timestamp)
   - [ ] New endpoint GET /predictions to retrieve history
   - [ ] Prometheus metrics exposed at /metrics
   - [ ] Track: request count, request duration, prediction distribution

2. **Docker Compose Configuration** (15 points):
   - [ ] Service: model-server (your application)
   - [ ] Service: postgres (with volume for persistence)
   - [ ] Service: prometheus (with config file)
   - [ ] Proper networking between services
   - [ ] Environment variables for configuration
   - [ ] Health checks for all services

3. **Database Integration** (5 points):
   - [ ] Connection to PostgreSQL works
   - [ ] Predictions saved successfully
   - [ ] Retrieval endpoint works
   - [ ] Proper error handling for DB issues

4. **Monitoring Setup** (5 points):
   - [ ] Prometheus scrapes metrics
   - [ ] Custom metrics visible in Prometheus UI
   - [ ] Prometheus accessible at localhost:9090

### Deliverables

```
task2/
├── model_server.py (updated)
├── requirements.txt (updated)
├── Dockerfile (updated)
├── docker-compose.yml
├── prometheus.yml
├── init-db.sql (optional)
├── .env.example
└── README.md
```

### Database Schema

Create a table with this structure:

```sql
CREATE TABLE predictions (
    id SERIAL PRIMARY KEY,
    text TEXT NOT NULL,
    sentiment VARCHAR(20) NOT NULL,
    confidence FLOAT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Prometheus Configuration Template

```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'model-server'
    static_configs:
      - targets: ['model-server:8000']
```

### Example API Interactions

**Make a prediction**:
```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "This is amazing!"}'
```

**Get prediction history**:
```bash
curl http://localhost:8000/predictions?limit=10
```

**Check metrics**:
```bash
curl http://localhost:8000/metrics
```

### Evaluation Criteria

| Criterion | Points | Your Score |
|-----------|--------|------------|
| Database integration works | 8 | |
| Predictions stored correctly | 4 | |
| History endpoint functional | 3 | |
| Docker Compose configuration | 10 | |
| Service networking | 5 | |
| Prometheus metrics exposed | 3 | |
| Metrics are meaningful | 2 | |
| All services start successfully | 5 | |
| **Total** | **40** | |

---

## Task 3: Troubleshooting and Documentation (30 points)

### Scenario

You've inherited a broken Docker application. Your task is to identify and fix the issues, then document the problems and solutions.

### Provided Files

You'll be given (create these intentionally broken):

**broken_app.py**:
```python
from flask import Flask, request, jsonify
import os

app = Flask(__name__)

# TODO: Fix issue - missing database connection
DATABASE_URL = os.getenv("DATABASE_URL")

@app.route('/api/data', methods=['GET'])
def get_data():
    # TODO: Fix issue - improper error handling
    data = fetch_from_database()
    return jsonify(data)

@app.route('/api/data', methods=['POST'])
def post_data():
    # TODO: Fix issue - no input validation
    content = request.json
    save_to_database(content)
    return jsonify({"status": "success"})

# TODO: Fix issue - functions not implemented
def fetch_from_database():
    pass

def save_to_database(data):
    pass

if __name__ == '__main__':
    # TODO: Fix issue - running as root, binding to wrong port
    app.run(host='0.0.0.0', port=5000)
```

**Broken Dockerfile**:
```dockerfile
# TODO: Fix issue - using outdated base image
FROM python:2.7

# TODO: Fix issue - not setting working directory
COPY . .

# TODO: Fix issue - installing unnecessary packages
RUN pip install flask requests numpy pandas scikit-learn tensorflow

# TODO: Fix issue - exposing wrong port
EXPOSE 8080

# TODO: Fix issue - running as root
CMD ["python", "broken_app.py"]
```

**Broken docker-compose.yml**:
```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      # TODO: Fix issue - port mapping mismatch
      - "5000:8080"
    environment:
      # TODO: Fix issue - exposing sensitive data
      - DATABASE_URL=postgresql://admin:password123@db:5432/mydb
    # TODO: Fix issue - missing dependency

  # TODO: Fix issue - database service not defined
```

### Your Tasks

1. **Identify Issues** (10 points):
   - [ ] List all problems found in the code
   - [ ] Categorize by severity (Critical, High, Medium, Low)
   - [ ] Explain why each is a problem

2. **Fix All Issues** (15 points):
   - [ ] Correct the Python application
   - [ ] Fix the Dockerfile
   - [ ] Fix the docker-compose.yml
   - [ ] Add proper error handling
   - [ ] Implement missing functions (can be stubs)
   - [ ] Add input validation

3. **Documentation** (5 points):
   - [ ] Create ISSUES.md listing all problems
   - [ ] Create FIXES.md explaining all corrections
   - [ ] Update README.md with proper setup instructions

### Expected Issues to Find and Fix

You should identify at least these issues:

**Code Issues**:
- Missing database connection implementation
- No error handling in endpoints
- No input validation
- Missing function implementations
- Security concerns (exposed credentials)

**Dockerfile Issues**:
- Outdated Python version
- No working directory set
- Excessive package installations
- Wrong port exposed
- Running as root user
- Missing .dockerignore

**Docker Compose Issues**:
- Port mapping mismatch
- Hardcoded credentials (should use secrets/env file)
- Missing database service
- No health checks
- Missing depends_on

### Deliverables

```
task3/
├── broken_app.py (fixed)
├── requirements.txt
├── Dockerfile (fixed)
├── docker-compose.yml (fixed)
├── .dockerignore
├── .env.example
├── ISSUES.md
├── FIXES.md
└── README.md
```

### ISSUES.md Template

```markdown
# Issues Found

## Critical Issues
1. **Issue**: Description
   - **Location**: File and line number
   - **Impact**: Why this is critical
   - **Fix**: How to resolve

## High Priority Issues
...

## Medium Priority Issues
...

## Low Priority Issues
...
```

### FIXES.md Template

```markdown
# Fixes Applied

## Issue 1: [Title]
- **Original Code**: ```[problematic code]```
- **Fixed Code**: ```[corrected code]```
- **Explanation**: Why this fix works
- **Testing**: How to verify the fix

## Issue 2: [Title]
...
```

### Evaluation Criteria

| Criterion | Points | Your Score |
|-----------|--------|------------|
| Identified critical issues | 5 | |
| Identified all issues | 5 | |
| Fixed application code | 5 | |
| Fixed Dockerfile | 5 | |
| Fixed docker-compose.yml | 5 | |
| Documentation quality | 3 | |
| Testing verification | 2 | |
| **Total** | **30** | |

---

## Submission Guidelines

### What to Submit

1. **Git repository** with all three tasks:
   ```
   midterm-exam/
   ├── task1/
   ├── task2/
   ├── task3/
   └── EXAM_SUMMARY.md
   ```

2. **EXAM_SUMMARY.md** containing:
   - Time spent on each task
   - Challenges encountered
   - How you resolved issues
   - Self-assessment scores
   - Resources consulted

### How to Submit

1. **Create final commit**:
   ```bash
   git add .
   git commit -m "Midterm exam submission"
   ```

2. **Verify all works**:
   - [ ] All Docker images build successfully
   - [ ] All containers run without errors
   - [ ] All API endpoints respond correctly
   - [ ] Documentation is complete

3. **Export your work**:
   ```bash
   git archive --format=zip HEAD > midterm-exam-submission.zip
   ```

4. **Submit via your learning platform** or as instructed

---

## Grading Rubric Summary

| Section | Points | Your Score |
|---------|--------|------------|
| Task 1: Containerized Model | 30 | |
| Task 2: Multi-Container App | 40 | |
| Task 3: Troubleshooting | 30 | |
| **Total** | **100** | |

### Score Interpretation

- **90-100**: Exceptional - Advanced understanding
- **75-89**: Proficient - Ready to proceed
- **60-74**: Adequate - Review recommended
- **<60**: Needs improvement - Retake after review

---

## Time Management Tips

### First Hour
- Read all requirements completely
- Set up your workspace
- Start with Task 1 (most straightforward)

### Second Hour
- Complete Task 1
- Begin Task 2
- Test as you go

### Third Hour
- Complete Task 2
- Tackle Task 3 (troubleshooting)
- Document findings

### Final 30 Minutes
- Review all deliverables
- Test everything works
- Write EXAM_SUMMARY.md
- Commit and prepare submission

---

## Resources Allowed

### Permitted
- Official Python documentation
- Docker documentation
- Flask/FastAPI documentation
- PostgreSQL documentation
- Prometheus documentation
- Stack Overflow (for syntax reference)
- Your own notes from completed modules

### Not Permitted
- Copying complete solutions
- AI assistance for entire implementations
- Collaboration with other students
- Pre-built project templates

---

## Common Pitfalls to Avoid

1. **Not reading requirements carefully** - Make sure you understand what's asked
2. **Spending too long on one task** - Move on if stuck, come back later
3. **Not testing incrementally** - Test each component as you build
4. **Poor time management** - Watch the clock, allocate time wisely
5. **Incomplete documentation** - Don't skip the README files
6. **Not handling errors** - Always include try-catch blocks
7. **Hardcoding values** - Use environment variables
8. **Running as root** - Always create a non-root user in Docker

---

## After the Exam

### If You Pass (75%+)
1. Review any weak areas
2. Continue to Module 3
3. Keep your solutions as reference
4. Help others in study groups

### If You Don't Pass (<75%)
1. Review the grading feedback
2. Identify specific gaps
3. Revisit relevant lessons
4. Practice weak areas
5. Retake after 1 week

---

## Study Recommendations

Before taking this exam, make sure you can:
- [ ] Write a Dockerfile from scratch
- [ ] Create a Flask/FastAPI application
- [ ] Use Docker Compose with multiple services
- [ ] Connect to PostgreSQL from Python
- [ ] Expose Prometheus metrics
- [ ] Debug container issues
- [ ] Read and write technical documentation

---

## Questions or Issues

If you encounter technical difficulties during the exam:
1. Document the issue thoroughly
2. Include it in your EXAM_SUMMARY.md
3. Show your troubleshooting steps
4. Attempt workarounds

Technical issues won't count against you if properly documented.

---

**Good luck!** Remember: This exam tests practical skills you'll use daily as a Junior AI Infrastructure Engineer. Take your time, test thoroughly, and document well.
