# Module 007: APIs and Web Services

## Module Overview

APIs (Application Programming Interfaces) and web services are the backbone of modern distributed systems and AI/ML infrastructure. This module provides comprehensive training in designing, building, testing, and consuming RESTful APIs using Python frameworks like FastAPI and Flask.

You'll learn API design principles, HTTP fundamentals, authentication mechanisms, and how to build production-ready APIs for serving machine learning models. These skills are essential for exposing ML models as services, integrating AI capabilities into applications, and building scalable infrastructure.

By the end of this module, you'll be confident building robust APIs, implementing authentication, testing endpoints thoroughly, and deploying API services in containerized environments.

## Learning Objectives

By completing this module, you will be able to:

1. **Understand HTTP protocol** and RESTful API principles
2. **Design effective APIs** following REST conventions and best practices
3. **Build APIs with FastAPI** leveraging modern Python features
4. **Build APIs with Flask** for lightweight applications
5. **Implement authentication** including JWT, OAuth, and API keys
6. **Handle data validation** using Pydantic and request validation
7. **Test APIs thoroughly** using pytest and automated testing tools
8. **Document APIs** with OpenAPI/Swagger specifications
9. **Deploy APIs** in containerized environments
10. **Build ML model serving APIs** for inference and predictions

## Prerequisites

- Completion of Module 001 (Python Fundamentals) required
- Completion of Module 004 (Python for Infrastructure) recommended
- Completion of Module 005 (Docker and Containers) recommended
- Completion of Module 003 (Git Version Control) recommended
- Understanding of HTTP basics
- Familiarity with command line and terminal

**Recommended Setup:**
- Python 3.9+ installed
- Virtual environment tool (venv or conda)
- Postman or similar API testing tool
- Docker (for deployment exercises)
- Text editor or IDE with Python support
- cURL or HTTPie for command-line testing

## Time Commitment

- **Total Estimated Time:** 35-45 hours
- **Lectures & Reading:** 12-15 hours
- **Hands-on Exercises:** 18-22 hours
- **Projects:** 5-8 hours

**Recommended Pace:**
- Part-time (5-10 hrs/week): 4-5 weeks
- Full-time (20-30 hrs/week): 2 weeks

API development requires practice building, testing, and refining endpoints. Expect to iterate and experiment frequently.

## Module Structure

### Week 1: HTTP and REST Fundamentals
- **Topics:** HTTP protocol, REST principles, API design
- **Key Skills:** HTTP methods, status codes, REST conventions
- **Practice:** Designing APIs, analyzing existing APIs

### Week 2: Building APIs with FastAPI
- **Topics:** FastAPI framework, path operations, request/response handling
- **Key Skills:** FastAPI routing, Pydantic models, validation
- **Practice:** Building CRUD APIs, data validation

### Week 3: Authentication and Advanced Features
- **Topics:** Authentication mechanisms, middleware, error handling
- **Key Skills:** JWT authentication, dependency injection, testing
- **Practice:** Secured APIs, comprehensive testing

### Week 4: Deployment and ML Model Serving
- **Topics:** API deployment, performance, ML model APIs
- **Key Skills:** Containerization, monitoring, model serving
- **Practice:** Production deployment, ML inference API

## Detailed Topic Breakdown

### 1. HTTP and REST Fundamentals (5-6 hours)

#### 1.1 HTTP Protocol Basics
- Client-server architecture
- Request-response cycle
- HTTP methods (GET, POST, PUT, DELETE, PATCH)
- HTTP status codes (2xx, 3xx, 4xx, 5xx)
- HTTP headers (common headers and their purposes)
- Request and response structure
- Content types and serialization (JSON, XML)

#### 1.2 RESTful API Principles
- What is REST?
- REST constraints (stateless, client-server, cacheable)
- Resources and URI design
- CRUD operations mapping to HTTP methods
- Resource naming conventions
- REST maturity model (Richardson)
- REST vs GraphQL vs gRPC

#### 1.3 API Design Best Practices
- Resource-oriented design
- URI structure and hierarchy
- Versioning strategies (/v1/, /v2/)
- Query parameters vs path parameters
- Pagination strategies
- Filtering and sorting
- Error response design
- HATEOAS concepts

#### 1.4 API Documentation
- Importance of documentation
- OpenAPI specification (Swagger)
- API documentation standards
- Interactive documentation
- Code examples and SDKs
- Changelog and versioning
- Developer experience considerations

### 2. Introduction to FastAPI (7-9 hours)

#### 2.1 FastAPI Fundamentals
- Why FastAPI?
- FastAPI vs Flask comparison
- Installation and setup
- First FastAPI application
- Automatic interactive documentation
- Type hints and modern Python
- ASGI vs WSGI
- Performance characteristics

#### 2.2 Path Operations
- Defining routes and endpoints
- HTTP method decorators
- Path parameters
- Query parameters
- Request body
- Response models
- Status codes
- Tags and metadata

#### 2.3 Pydantic Models
- Data validation with Pydantic
- Creating models
- Field validation
- Complex data types
- Nested models
- Model configuration
- Custom validators
- JSON Schema generation

#### 2.4 Request Handling
- Reading request data
- Form data
- File uploads
- Headers
- Cookies
- Request object access
- Multiple request sources
- Data validation and conversion

#### 2.5 Response Handling
- Response models
- Response status codes
- Custom response types
- JSON responses
- File responses
- Streaming responses
- Response headers
- Response validation

#### 2.6 Path Operations Configuration
- Response model configuration
- Status codes and responses
- Tags and groups
- Summary and description
- Deprecation
- Operation ID
- Response examples
- OpenAPI metadata

### 3. Building Complete APIs (6-8 hours)

#### 3.1 CRUD Operations
- Create endpoints (POST)
- Read endpoints (GET)
- Update endpoints (PUT, PATCH)
- Delete endpoints (DELETE)
- RESTful URL patterns
- Database integration (SQLAlchemy)
- Error handling
- Input validation

#### 3.2 Dependency Injection
- FastAPI dependency system
- Creating dependencies
- Reusable dependencies
- Nested dependencies
- Class-based dependencies
- Dependency scope
- Testing with dependencies
- Common dependency patterns

#### 3.3 Database Integration
- SQLAlchemy basics
- Defining models
- Database sessions
- CRUD operations with database
- Async database operations
- Connection pooling
- Migrations (Alembic)
- Transaction management

#### 3.4 Error Handling
- HTTP exceptions
- Custom exception handlers
- Validation errors
- Status codes for errors
- Error response format
- Logging errors
- User-friendly error messages
- Exception middleware

#### 3.5 Background Tasks
- Running background tasks
- Use cases (emails, processing)
- Task queues (Celery preview)
- Async task handling
- Progress tracking
- Error handling in background tasks
- Background task best practices

### 4. Flask Web Framework (5-6 hours)

#### 4.1 Flask Fundamentals
- Flask philosophy
- Installation and setup
- Application structure
- First Flask application
- Development server
- Debug mode
- Application context
- Request context

#### 4.2 Routing and Views
- Route definitions
- URL building
- HTTP methods
- Variable rules
- URL converters
- Redirects and errors
- View decorators
- Blueprint for modular applications

#### 4.3 Request and Response
- Request object
- Response object
- JSON responses (jsonify)
- File uploads
- Cookies and sessions
- Custom response types
- Error handlers
- Before/after request hooks

#### 4.4 Flask Extensions
- Flask-RESTful for APIs
- Flask-CORS
- Flask-SQLAlchemy
- Flask-Migrate
- Flask-JWT-Extended
- Flask-Marshmallow
- Extension ecosystem
- Configuration management

#### 4.5 Flask vs FastAPI
- Performance comparison
- Use case differences
- Ecosystem maturity
- Learning curve
- Type safety
- Documentation generation
- When to choose each
- Migration strategies

### 5. Authentication and Authorization (6-8 hours)

#### 5.1 Authentication Basics
- Authentication vs authorization
- Stateless authentication
- Token-based authentication
- Session-based authentication
- API keys
- OAuth 2.0 overview
- Authentication flows
- Security considerations

#### 5.2 JWT Authentication
- What is JWT?
- JWT structure (header, payload, signature)
- Creating JWTs
- Validating JWTs
- Token expiration
- Refresh tokens
- Token storage
- Security best practices

#### 5.3 Implementing Authentication in FastAPI
- User model and database
- Password hashing (bcrypt)
- Login endpoint
- Token generation
- Protected routes
- Dependency injection for auth
- Current user dependency
- Role-based access control

#### 5.4 OAuth 2.0 Integration
- OAuth 2.0 flows
- Authorization code flow
- Implicit flow
- Client credentials flow
- Third-party authentication
- Social login (Google, GitHub)
- OAuth libraries (Authlib)
- Security considerations

#### 5.5 API Keys and Rate Limiting
- API key generation
- API key validation
- Rate limiting strategies
- Rate limiting implementation
- Throttling
- Quota management
- API key best practices
- DDoS protection basics

### 6. Testing APIs (5-7 hours)

#### 6.1 Testing Fundamentals
- Why test APIs?
- Types of API tests
- Testing pyramid
- Test-driven development (TDD)
- Testing tools overview
- pytest for API testing
- Test organization
- Test data management

#### 6.2 Unit Testing API Endpoints
- Testing with TestClient (FastAPI)
- Testing Flask applications
- Mocking dependencies
- Database testing strategies
- Fixture usage
- Parametrized tests
- Testing error cases
- Code coverage

#### 6.3 Integration Testing
- Testing complete workflows
- Database integration tests
- Testing authentication
- Testing file uploads
- Testing external APIs
- Test databases
- Transaction rollback
- Test performance

#### 6.4 API Testing Tools
- Postman for manual testing
- Thunder Client (VS Code)
- HTTPie for CLI testing
- Newman for automated Postman tests
- Pytest plugins
- API testing frameworks
- Load testing (Locust preview)
- Contract testing

#### 6.5 Test Automation
- Continuous integration
- GitHub Actions for API testing
- Pre-commit hooks
- Test coverage reporting
- Automated testing workflows
- Test environments
- Testing best practices
- Maintaining test suites

### 7. Production and Deployment (5-7 hours)

#### 7.1 Production Considerations
- ASGI servers (Uvicorn, Gunicorn)
- Worker processes and threads
- Reverse proxy (Nginx)
- HTTPS and SSL/TLS
- Environment configuration
- Secrets management
- Logging and monitoring
- Health checks

#### 7.2 Containerizing APIs
- Dockerfile for FastAPI
- Dockerfile for Flask
- Multi-stage builds
- Docker Compose for development
- Environment variables in containers
- Container networking
- Volume management
- Container security

#### 7.3 API Performance
- Async programming benefits
- Database query optimization
- Caching strategies (Redis)
- Connection pooling
- Response compression
- CDN for static assets
- Profiling API performance
- Performance monitoring

#### 7.4 API Monitoring and Logging
- Structured logging
- Log aggregation
- Error tracking (Sentry)
- Performance monitoring (New Relic, Datadog)
- Metrics and dashboards
- Alerting
- Distributed tracing
- APM (Application Performance Monitoring)

#### 7.5 API Security
- HTTPS enforcement
- CORS configuration
- Input validation
- SQL injection prevention
- XSS protection
- CSRF protection
- Security headers
- Dependency scanning
- Security best practices

### 8. ML Model Serving APIs (4-5 hours)

#### 8.1 Serving Models via API
- Why serve models as APIs?
- Model loading strategies
- Inference endpoint design
- Request/response formats
- Batch vs real-time inference
- Model versioning in APIs
- A/B testing setup
- Model metadata endpoints

#### 8.2 Building ML APIs with FastAPI
- Loading ML models (scikit-learn, PyTorch)
- Preprocessing in API
- Prediction endpoints
- Input validation for ML
- Output formatting
- Error handling for ML errors
- Model health checks
- Example implementations

#### 8.3 Performance Optimization
- Model caching
- Batch prediction optimization
- Async inference
- GPU utilization
- Model quantization
- Response time optimization
- Scaling strategies
- Load testing ML APIs

#### 8.4 ML API Best Practices
- Versioning ML APIs
- Model registry integration
- Feature validation
- Monitoring predictions
- Handling edge cases
- Explainability endpoints
- Model retraining triggers
- Production ML patterns

## Lecture Outline

> **Status Update (2025-10-29):** All 4 comprehensive lecture notes are now complete and available! Each lecture includes practical API development examples for ML infrastructure.

This module includes **4 lectures** and **8 exercises** covering API development:

### Lecture 1: HTTP and REST Fundamentals (90 min)
- HTTP protocol overview
- REST principles
- API design best practices
- Status codes and methods
- Resource-oriented design
- **Lab:** Analyzing and designing APIs

### Lecture 2: FastAPI Basics (90 min)
- Introduction to FastAPI
- First API application
- Path operations
- Query and path parameters
- Automatic documentation
- **Lab:** Building basic FastAPI endpoints

### Lecture 3: Request and Response Handling (90 min)
- Pydantic models
- Data validation
- Request body handling
- Response models
- Status codes
- **Lab:** CRUD API with validation

### Lecture 4: Database Integration (90 min)
- SQLAlchemy with FastAPI
- Database models
- CRUD operations
- Dependency injection
- Error handling
- **Lab:** API with database backend

### Lecture 5: Authentication and Security (120 min)
- Authentication concepts
- JWT implementation
- Password hashing
- Protected routes
- OAuth 2.0 overview
- **Lab:** Secured API with authentication

### Lecture 6: Flask Web Framework (90 min)
- Flask fundamentals
- Routing and views
- Flask-RESTful
- Flask vs FastAPI
- When to use each
- **Lab:** Building API with Flask

### Lecture 7: Testing and Quality Assurance (90 min)
- API testing strategies
- pytest for APIs
- Test client usage
- Integration testing
- CI/CD for APIs
- **Lab:** Comprehensive test suite

### Lecture 8: ML Model Serving (120 min)
- Model serving architecture
- Building ML APIs
- Performance optimization
- Deployment strategies
- Monitoring and maintenance
- **Lab:** Complete ML inference API

## Hands-On Exercises

> **Status Update (2025-10-29):** All 8 comprehensive exercises are now complete! Each exercise includes detailed instructions with ML API examples and complete solutions.

This module includes **8 exercises** building practical API development skills:

### Exercise Categories

#### HTTP and REST (2 exercises)
1. HTTP method and status code practice
2. API design challenge
3. Analyzing existing APIs
4. REST principles application
5. URI design patterns

#### FastAPI Basics (8 exercises)
6. First FastAPI application
7. Path and query parameters
8. Pydantic models and validation
9. Request body handling
10. Response models
11. CRUD operations
12. Error handling
13. Dependency injection

#### Authentication (5 exercises)
14. Password hashing implementation
15. JWT token generation
16. Protected endpoint creation
17. User authentication system
18. Role-based access control

#### Testing (5 exercises)
19. Unit testing endpoints
20. Integration test suite
21. Testing authentication
22. Mocking dependencies
23. CI/CD test automation

#### Deployment (5 exercises)
24. Containerizing FastAPI app
25. Production configuration
26. Health check endpoints
27. Logging implementation
28. Performance optimization

#### ML Model Serving (4 exercises)
29. Loading and serving model
30. Prediction endpoint
31. Batch prediction API
32. Complete ML service

### Exercise 07: Flask to FastAPI Migration
**Difficulty**: Intermediate
**Duration**: 3-4 hours
**File**: `exercises/exercise-07-flask-fastapi-migration.md`

Migrate a Flask ML API to FastAPI and compare performance:
- Convert Flask routes to FastAPI endpoints
- Implement Pydantic models for request/response validation
- Add async endpoints for improved concurrency
- Migrate authentication mechanisms
- Performance benchmarking and comparison
- Deploy both versions for A/B testing

### Exercise 08: Comprehensive API Testing
**Difficulty**: Intermediate to Advanced
**Duration**: 3-4 hours
**File**: `exercises/exercise-08-api-testing.md`

Build comprehensive test suite for ML APIs:
- Unit testing with pytest (fixtures, mocking, parametrized tests)
- Integration testing for complete workflows
- Contract testing with OpenAPI schema validation
- Load testing with Locust (concurrent users, sustained load)
- CI/CD integration with GitHub Actions
- Coverage requirements and performance SLAs

## Assessment and Evaluation

### Knowledge Checks
- **2 comprehensive quizzes** covering all module content
  - Quiz 1: HTTP, REST, and FastAPI Fundamentals (Lectures 1-2)
  - Quiz 2: Authentication, Testing, and ML APIs (Lectures 3-4)
- HTTP and REST concepts
- Framework comparisons
- Security principles
- Best practices evaluation

### Practical Assessments
- **Basic API:** Build CRUD API with validation
- **Authenticated API:** Implement complete authentication
- **Tested API:** Achieve >80% test coverage
- **ML API:** Deploy model serving endpoint
- **Production API:** Containerized, documented, monitored

### Competency Criteria
To complete this module successfully, you should be able to:
- Design RESTful APIs following best practices
- Build APIs using FastAPI and Flask
- Implement authentication and authorization
- Write comprehensive API tests
- Handle errors appropriately
- Document APIs effectively
- Deploy APIs in containers
- Serve ML models via API
- Monitor and maintain production APIs
- Optimize API performance

### Capstone Project
**ML Model Serving API:**
Build a production-ready ML API featuring:
- Model inference endpoints
- JWT authentication
- Request validation
- Comprehensive testing
- Docker containerization
- API documentation
- Monitoring and logging
- Performance optimization
- Complete deployment guide

## Resources and References

> **Note:** See `resources/recommended-reading.md` for a comprehensive list of learning materials, books, and online resources.

### Essential Resources
- FastAPI documentation
- Flask documentation
- REST API Tutorial
- HTTP specification

### Recommended Books
- "RESTful Web APIs" by Leonard Richardson
- "Flask Web Development" by Miguel Grinberg
- "Building Microservices" by Sam Newman

### Online Learning
- FastAPI tutorial
- Real Python API tutorials
- Test-Driven Development with Python
- REST API design course

### Tools
- Postman
- Thunder Client
- HTTPie
- Swagger Editor
- JWT.io
- Python requests library

## Getting Started

### Step 1: Set Up Environment
1. Install Python 3.9+
2. Create virtual environment
3. Install FastAPI and dependencies
4. Install testing tools
5. Install Postman or similar

### Step 2: Review Prerequisites
- Python fundamentals
- HTTP basics
- Command line comfort
- Docker knowledge (for deployment)

### Step 3: Begin with Lecture 1
- Learn HTTP and REST
- Design first API
- Complete initial exercises

### Step 4: Build Progressively
- Start with simple endpoints
- Add complexity gradually
- Test thoroughly
- Deploy to containers
- Build ML serving API

## Tips for Success

1. **Test Everything:** Write tests as you build
2. **Document Early:** Use OpenAPI documentation from start
3. **Security First:** Never skip authentication in production
4. **Validate Input:** Always validate and sanitize input
5. **Handle Errors:** Provide clear error messages
6. **Version APIs:** Plan for versioning from the beginning
7. **Monitor Performance:** Track response times
8. **Use Type Hints:** Leverage Python type hints
9. **Follow Standards:** Stick to REST conventions
10. **Read Documentation:** FastAPI docs are excellent

## Next Steps

After completing this module, you'll be ready to:
- **Module 009:** Monitoring Basics (monitor your APIs)
- **Module 010:** Cloud Platforms (deploy APIs to cloud)
- Advanced topics: Microservices, API gateways, service mesh

## Development Status

**Current Status:** Template phase - comprehensive structure in place

**Available Now:**
- Complete module structure
- Detailed topic breakdown
- Lecture outline
- Exercise framework

**In Development:**
- Full lecture notes
- Step-by-step exercises
- Code examples
- ML serving examples
- Testing templates
- Deployment guides

**Planned Updates:**
- GraphQL introduction
- gRPC basics
- Microservices patterns
- Service mesh concepts
- Advanced authentication

## Feedback and Contributions

Help improve this module by:
- Reporting issues
- Suggesting improvements
- Contributing examples
- Sharing best practices

---

**Module Maintainer:** AI Infrastructure Curriculum Team
**Contact:** ai-infra-curriculum@joshua-ferguson.com
**Last Updated:** 2025-10-18
**Version:** 1.0.0-template
