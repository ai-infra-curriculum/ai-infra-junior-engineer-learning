# Project 01: System Architecture

**Project:** Simple Model API Deployment
**Role:** Junior AI Infrastructure Engineer
**Version:** 1.0

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture Diagram](#architecture-diagram)
3. [Component Design](#component-design)
4. [Data Flow](#data-flow)
5. [Technology Stack](#technology-stack)
6. [Deployment Architecture](#deployment-architecture)
7. [Design Decisions](#design-decisions)
8. [Scalability Considerations](#scalability-considerations)

---

## System Overview

This project implements a simple REST API for serving predictions from a pre-trained image classification model. The system follows a stateless, containerized microservice architecture pattern that is commonly used in production ML systems.

### Key Characteristics

- **Stateless:** No server-side session state, enabling horizontal scaling
- **Containerized:** Docker packaging for consistent deployment across environments
- **Synchronous:** Request-response pattern with blocking inference
- **Single-model:** Serves one model version at a time (no A/B testing yet)
- **CPU-optimized:** Designed for CPU inference (GPU support in later projects)

### Design Philosophy

This architecture prioritizes:
1. **Simplicity:** Easy to understand and debug for beginners
2. **Reliability:** Graceful error handling and recovery
3. **Observability:** Comprehensive logging for troubleshooting
4. **Maintainability:** Clear separation of concerns, modular design

---

## Architecture Diagram

### High-Level Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                        Cloud Platform                         │
│                   (AWS / GCP / Azure)                         │
│                                                                │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Virtual Machine Instance                 │   │
│  │                (t3.medium or equivalent)              │   │
│  │                                                        │   │
│  │  ┌──────────────────────────────────────────────┐   │   │
│  │  │           Docker Container                    │   │   │
│  │  │                                                │   │   │
│  │  │  ┌──────────────────────────────────────┐   │   │   │
│  │  │  │      Flask/FastAPI Application       │   │   │   │
│  │  │  │                                        │   │   │   │
│  │  │  │  ┌─────────────┐  ┌──────────────┐  │   │   │   │
│  │  │  │  │  API Layer  │  │ Model Manager│  │   │   │   │
│  │  │  │  │             │  │              │  │   │   │   │
│  │  │  │  │ /predict    │◄─┤ load_model() │  │   │   │   │
│  │  │  │  │ /health     │  │ predict()    │  │   │   │   │
│  │  │  │  │ /info       │  │ preprocess() │  │   │   │   │
│  │  │  │  └─────────────┘  └──────────────┘  │   │   │   │
│  │  │  │                                        │   │   │   │
│  │  │  │  ┌─────────────┐  ┌──────────────┐  │   │   │   │
│  │  │  │  │   Config    │  │   Logging    │  │   │   │   │
│  │  │  │  │  Manager    │  │   Handler    │  │   │   │   │
│  │  │  │  └─────────────┘  └──────────────┘  │   │   │   │
│  │  │  │                                        │   │   │   │
│  │  │  └──────────────────────────────────────┘   │   │   │
│  │  │                                                │   │   │
│  │  │  Port Mapping: 5000:5000                     │   │   │
│  │  └──────────────────────────────────────────────┘   │   │
│  │                                                        │   │
│  │  Security Group / Firewall:                           │   │
│  │  - Port 5000 (HTTP)                                   │   │
│  │  - Port 22 (SSH - admin only)                         │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                                │
│  Public IP: X.X.X.X                                           │
└──────────────────────────────────────────────────────────────┘
                              ▲
                              │
                              │ HTTP Requests
                              │
                    ┌─────────┴──────────┐
                    │                    │
                ┌───┴────┐         ┌────┴─────┐
                │ Client │         │ Postman  │
                │Browser │         │  /cURL   │
                └────────┘         └──────────┘
```

### Component Architecture

```
┌────────────────────────────────────────────────────────────┐
│                   Application Layer                         │
├────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────────────────────────────────────────────┐   │
│  │                 app.py (Main Application)           │   │
│  │                                                      │   │
│  │  ┌──────────────────────────────────────────────┐  │   │
│  │  │          API Route Handlers                   │  │   │
│  │  │                                                │  │   │
│  │  │  @app.route('/predict')                       │  │   │
│  │  │  @app.route('/health')                        │  │   │
│  │  │  @app.route('/info')                          │  │   │
│  │  └──────────────────────────────────────────────┘  │   │
│  │                        │                             │   │
│  │                        ▼                             │   │
│  │  ┌──────────────────────────────────────────────┐  │   │
│  │  │         Request Processing Pipeline           │  │   │
│  │  │                                                │  │   │
│  │  │  1. Request Validation                        │  │   │
│  │  │  2. File Upload Handling                      │  │   │
│  │  │  3. Image Preprocessing                       │  │   │
│  │  │  4. Model Inference                           │  │   │
│  │  │  5. Response Formatting                       │  │   │
│  │  │  6. Error Handling                            │  │   │
│  │  │  7. Logging                                   │  │   │
│  │  └──────────────────────────────────────────────┘  │   │
│  └────────────────────────────────────────────────────┘   │
│                                                              │
├────────────────────────────────────────────────────────────┤
│                  Business Logic Layer                       │
├────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────┐      ┌──────────────────────────┐   │
│  │  model_loader.py │      │      config.py           │   │
│  │                  │      │                          │   │
│  │  ModelLoader     │      │  Configuration           │   │
│  │  ├─ __init__()   │      │  ├─ MODEL_NAME           │   │
│  │  ├─ load()       │      │  ├─ MODEL_PATH           │   │
│  │  ├─ predict()    │      │  ├─ HOST / PORT          │   │
│  │  ├─ preprocess() │      │  ├─ LOG_LEVEL            │   │
│  │  └─ get_labels() │      │  └─ MAX_FILE_SIZE        │   │
│  └──────────────────┘      └──────────────────────────┘   │
│                                                              │
├────────────────────────────────────────────────────────────┤
│                    Infrastructure Layer                     │
├────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │   Logging    │  │  Error       │  │   Health     │    │
│  │   System     │  │  Handler     │  │   Monitor    │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
│                                                              │
└────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────┐
│                      ML Framework Layer                     │
│                   (PyTorch / TensorFlow)                    │
└────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────┐
│                     Operating System                        │
│                    (Linux Container)                        │
└────────────────────────────────────────────────────────────┘
```

---

## Component Design

### 1. API Layer (app.py)

**Responsibility:** HTTP request/response handling, routing, API contract enforcement

**Key Components:**
- Flask/FastAPI application instance
- Route handlers for each endpoint
- Request validation middleware
- Response formatting utilities
- Error handling middleware

**Design Pattern:** MVC (Model-View-Controller) - API layer acts as the Controller

**Interface:**
```python
class ModelAPI:
    """Main API application class"""

    def __init__(self, model_loader: ModelLoader, config: Config):
        """Initialize API with dependencies"""

    def predict(self, request) -> Response:
        """Handle /predict endpoint"""

    def health(self) -> Response:
        """Handle /health endpoint"""

    def info(self) -> Response:
        """Handle /info endpoint"""
```

### 2. Model Manager (model_loader.py)

**Responsibility:** ML model lifecycle management, inference execution

**Key Components:**
- Model loading from pretrained weights
- Image preprocessing pipeline
- Inference execution
- Result post-processing
- Class label mapping

**Design Pattern:** Singleton - One model instance per application

**Interface:**
```python
class ModelLoader:
    """Manages ML model lifecycle"""

    def __init__(self, model_name: str, device: str = "cpu"):
        """Initialize with model configuration"""

    def load_model(self) -> None:
        """Load model weights and initialize"""

    def preprocess(self, image: PIL.Image) -> torch.Tensor:
        """Preprocess image for inference"""

    def predict(self, image: PIL.Image, top_k: int = 5) -> List[Prediction]:
        """Generate predictions for image"""

    def get_model_info(self) -> ModelInfo:
        """Return model metadata"""
```

### 3. Configuration Manager (config.py)

**Responsibility:** Application configuration management, environment variable handling

**Key Components:**
- Environment variable loading
- Configuration validation
- Default value management
- Type conversions

**Design Pattern:** Configuration Object

**Interface:**
```python
class Config:
    """Application configuration"""

    # Model settings
    MODEL_NAME: str
    MODEL_PATH: str
    DEVICE: str  # "cpu" or "cuda"

    # API settings
    HOST: str
    PORT: int
    DEBUG: bool

    # Limits
    MAX_FILE_SIZE: int
    REQUEST_TIMEOUT: int

    # Logging
    LOG_LEVEL: str
    LOG_FORMAT: str
```

### 4. Logging System

**Responsibility:** Structured logging, request tracking, error reporting

**Key Components:**
- Logger configuration
- Correlation ID generation
- Structured log formatting (JSON)
- Log level management

**Design Pattern:** Decorator pattern for request logging

---

## Data Flow

### Prediction Request Flow

```
┌─────────┐
│ Client  │
└────┬────┘
     │
     │ 1. POST /predict (multipart/form-data)
     │    - file: image bytes
     │    - top_k: 5 (optional)
     ▼
┌────────────────┐
│  API Gateway   │ (Flask/FastAPI)
│  (Route)       │
└────┬───────────┘
     │
     │ 2. Route to predict() handler
     ▼
┌────────────────┐
│ Request        │
│ Validation     │ - Check Content-Type
│                │ - Validate file exists
│                │ - Check file size
└────┬───────────┘
     │
     │ 3. Valid request
     ▼
┌────────────────┐
│ File Upload    │
│ Handler        │ - Read file bytes
│                │ - Parse multipart data
└────┬───────────┘
     │
     │ 4. Image bytes
     ▼
┌────────────────┐
│ Image          │
│ Loader         │ - Load with PIL
│                │ - Convert to RGB
│                │ - Validate format
└────┬───────────┘
     │
     │ 5. PIL.Image object
     ▼
┌────────────────┐
│ Model          │
│ Preprocessor   │ - Resize to 224x224
│                │ - Normalize
│                │ - Convert to tensor
└────┬───────────┘
     │
     │ 6. torch.Tensor [1, 3, 224, 224]
     ▼
┌────────────────┐
│ ML Model       │
│ (ResNet-50)    │ - Forward pass
│                │ - Generate logits
└────┬───────────┘
     │
     │ 7. Output tensor [1, 1000]
     ▼
┌────────────────┐
│ Post-          │
│ Processor      │ - Apply softmax
│                │ - Get top-K
│                │ - Map to labels
└────┬───────────┘
     │
     │ 8. List[Prediction]
     ▼
┌────────────────┐
│ Response       │
│ Formatter      │ - Format JSON
│                │ - Add metadata
│                │ - Add timestamps
└────┬───────────┘
     │
     │ 9. JSON response
     ▼
┌────────────────┐
│ Logging        │ - Log request
│                │ - Record latency
│                │ - Track errors
└────┬───────────┘
     │
     │ 10. HTTP 200 OK
     ▼
┌─────────┐
│ Client  │ - Receives predictions
└─────────┘
```

### Error Handling Flow

```
     [Any Stage]
          │
          │ Exception occurs
          ▼
     ┌────────────┐
     │ Try/Catch  │
     │ Block      │
     └────┬───────┘
          │
          ├─── ValueError ────────► HTTP 400 (Bad Request)
          │
          ├─── MemoryError ───────► HTTP 503 (Service Unavailable)
          │
          ├─── TimeoutError ──────► HTTP 504 (Gateway Timeout)
          │
          ├─── FileNotFoundError ─► HTTP 400 (Bad Request)
          │
          └─── Exception ─────────► HTTP 500 (Internal Server Error)
                    │
                    ▼
          ┌──────────────────┐
          │ Error Handler    │
          │ - Format error   │
          │ - Generate ID    │
          │ - Log error      │
          └────┬─────────────┘
               │
               ▼
          [Error Response]
```

---

## Technology Stack

### Programming Language
- **Python 3.11+**
  - Justification: Excellent ML ecosystem, readability, productivity
  - Alternatives considered: Go (lack of ML libraries), Java (verbosity)

### Web Framework
- **Flask 3.0+** or **FastAPI 0.100+**
  - Flask: Simpler, more traditional, extensive documentation
  - FastAPI: Modern, async support, automatic API docs, type validation
  - Recommendation for beginners: Flask (less complexity)

### ML Framework
- **PyTorch 2.0+** or **TensorFlow 2.13+**
  - PyTorch: More intuitive, better debugging, research-friendly
  - TensorFlow: Production-ready, broader ecosystem, TF Serving integration
  - Recommendation: PyTorch (easier learning curve)

### Image Processing
- **Pillow (PIL Fork)**
  - Industry standard for Python image processing
  - Alternative: OpenCV (overkill for this use case)

### Configuration
- **python-dotenv**
  - Load environment variables from .env files
  - Alternative: Manual os.environ (less convenient)

### Testing
- **pytest**
  - Modern, feature-rich testing framework
  - Alternative: unittest (more verbose)

### Containerization
- **Docker 24.0+**
  - Industry standard for containerization
  - Base image: python:3.11-slim (smaller, faster)

---

## Deployment Architecture

### Container Architecture

```
┌─────────────────────────────────────────────────┐
│           Docker Container                       │
│                                                   │
│  ┌────────────────────────────────────────┐    │
│  │  Python 3.11 Runtime Environment       │    │
│  ├────────────────────────────────────────┤    │
│  │  System Dependencies:                  │    │
│  │  - libgomp1 (OpenMP for PyTorch)       │    │
│  │  - ca-certificates                     │    │
│  └────────────────────────────────────────┘    │
│                                                   │
│  ┌────────────────────────────────────────┐    │
│  │  Python Dependencies:                  │    │
│  │  - flask / fastapi                     │    │
│  │  - torch / torchvision                 │    │
│  │  - pillow                              │    │
│  │  - python-dotenv                       │    │
│  └────────────────────────────────────────┘    │
│                                                   │
│  ┌────────────────────────────────────────┐    │
│  │  Application Code:                     │    │
│  │  /app/                                 │    │
│  │  ├── src/                              │    │
│  │  │   ├── app.py                        │    │
│  │  │   ├── model_loader.py               │    │
│  │  │   └── config.py                     │    │
│  │  └── .env                              │    │
│  └────────────────────────────────────────┘    │
│                                                   │
│  ┌────────────────────────────────────────┐    │
│  │  Cached Model Weights:                 │    │
│  │  ~/.cache/torch/hub/                   │    │
│  │  └── checkpoints/                      │    │
│  │      └── resnet50.pth (97MB)           │    │
│  └────────────────────────────────────────┘    │
│                                                   │
│  Exposed Ports: 5000                             │
│  Health Check: GET /health (every 30s)          │
└─────────────────────────────────────────────────┘
```

### Cloud Deployment (AWS Example)

```
┌──────────────────────────────────────────────────────┐
│                     AWS Cloud                         │
│                                                        │
│  ┌────────────────────────────────────────────────┐ │
│  │              VPC (Virtual Private Cloud)        │ │
│  │                                                  │ │
│  │  ┌────────────────────────────────────────┐   │ │
│  │  │         Public Subnet                   │   │ │
│  │  │                                          │   │ │
│  │  │  ┌──────────────────────────────────┐  │   │ │
│  │  │  │     EC2 Instance (t3.medium)     │  │   │ │
│  │  │  │     - 2 vCPUs                    │  │   │ │
│  │  │  │     - 4GB RAM                    │  │   │ │
│  │  │  │     - Ubuntu 22.04 LTS           │  │   │ │
│  │  │  │     - Docker Engine              │  │   │ │
│  │  │  │                                   │  │   │ │
│  │  │  │  ┌──────────────────────────┐   │  │   │ │
│  │  │  │  │  Model API Container     │   │  │   │ │
│  │  │  │  │  (Port 5000)             │   │  │   │ │
│  │  │  │  └──────────────────────────┘   │  │   │ │
│  │  │  │                                   │  │   │ │
│  │  │  │  Public IP: 52.x.x.x             │  │   │ │
│  │  │  └──────────────────────────────────┘  │   │ │
│  │  │                                          │   │ │
│  │  └────────────────────────────────────────┘   │ │
│  │                                                  │ │
│  │  ┌────────────────────────────────────────┐   │ │
│  │  │        Security Group                   │   │ │
│  │  │  - Inbound: Port 5000 (0.0.0.0/0)      │   │ │
│  │  │  - Inbound: Port 22 (Admin IP only)    │   │ │
│  │  │  - Outbound: All traffic               │   │ │
│  │  └────────────────────────────────────────┘   │ │
│  └────────────────────────────────────────────────┘ │
│                                                        │
│  ┌────────────────────────────────────────────────┐ │
│  │           CloudWatch Logs                       │ │
│  │  - Container stdout/stderr                      │ │
│  │  - Application logs                             │ │
│  └────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────┘
```

---

## Design Decisions

### 1. Synchronous vs Asynchronous

**Decision:** Synchronous (blocking) request handling

**Rationale:**
- Simpler implementation for beginners
- ML inference is CPU-bound (not I/O-bound)
- Fewer concurrency issues
- Easier debugging

**Trade-offs:**
- Lower throughput under high concurrency
- Request queuing can cause timeouts
- Not optimal for long-running requests

**Future Consideration:** Move to async (FastAPI) in later projects

### 2. Model Loading Strategy

**Decision:** Load model once at startup, keep in memory

**Rationale:**
- Faster inference (no loading overhead per request)
- Simpler code (no caching logic needed)
- Acceptable memory footprint (<500MB for ResNet-50)

**Trade-offs:**
- Higher memory usage
- Slower startup time (20-30 seconds)
- No model hot-swapping

**Alternative Considered:** Lazy loading (load on first request) - rejected due to poor first-request latency

### 3. Single Model vs Multi-Model

**Decision:** Single model per instance

**Rationale:**
- Simpler deployment and management
- Predictable resource usage
- Easier monitoring and debugging

**Trade-offs:**
- Cannot A/B test models
- Requires redeployment for model updates

**Future Path:** Multi-model serving in advanced projects

### 4. CPU vs GPU

**Decision:** CPU-only for this project

**Rationale:**
- Lower cost (no GPU instances)
- Simpler setup (no CUDA configuration)
- Sufficient performance for learning (<1s latency)

**Trade-offs:**
- Higher latency (300-500ms vs 50-100ms on GPU)
- Lower throughput

**Future Path:** GPU optimization in later projects

### 5. Image Storage

**Decision:** In-memory only (no disk persistence)

**Rationale:**
- Faster processing
- No disk I/O overhead
- Simpler cleanup (automatic garbage collection)
- Reduced security risk

**Trade-offs:**
- Cannot replay requests
- No audit trail of inputs

### 6. Logging Strategy

**Decision:** Structured logging to stdout/stderr

**Rationale:**
- Compatible with container orchestration
- Easy integration with cloud logging (CloudWatch, Stackdriver)
- No file system dependencies

**Format:** JSON for structured logging, text for development

---

## Scalability Considerations

### Horizontal Scaling

The application is designed to scale horizontally:

```
                  ┌──────────────┐
                  │ Load Balancer│
                  └──────┬───────┘
                         │
           ┌─────────────┼─────────────┐
           │             │             │
           ▼             ▼             ▼
      ┌────────┐    ┌────────┐    ┌────────┐
      │ API    │    │ API    │    │ API    │
      │ Instance│   │ Instance│   │ Instance│
      │   #1   │    │   #2   │    │   #3   │
      └────────┘    └────────┘    └────────┘
```

**Scaling Characteristics:**
- Stateless design (no shared state between instances)
- Independent model loading per instance
- No database dependencies
- Session-less authentication (if added)

**Limitations:**
- No shared cache (each instance loads model independently)
- Startup time scales linearly (all instances load model)
- Total memory = memory_per_instance × num_instances

### Vertical Scaling

For higher throughput on a single instance:

**Options:**
1. **More CPU cores:** Run multiple worker processes (Gunicorn/Uvicorn)
2. **More memory:** Support larger batch sizes or bigger models
3. **Add GPU:** 10-20x inference speedup

**Recommendation:** Start with 2 vCPUs, 4GB RAM (t3.medium equivalent)

### Performance Optimization Paths

**Phase 1 (Current):**
- Single worker, CPU inference
- Target: 10 requests/second

**Phase 2 (Future):**
- Multi-worker deployment (4-8 workers)
- Target: 40-80 requests/second

**Phase 3 (Future):**
- GPU inference
- Target: 200-400 requests/second

**Phase 4 (Future):**
- Model optimization (TensorRT, ONNX)
- Target: 500-1000 requests/second

---

## Security Architecture

### Defense in Depth

```
┌─────────────────────────────────────────────┐
│         Layer 1: Network Security           │
│  - Security Groups / Firewall Rules         │
│  - Rate Limiting (optional)                 │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│     Layer 2: Application Input Validation   │
│  - File type validation                     │
│  - File size limits                         │
│  - Content-Type checking                    │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│     Layer 3: Request Processing             │
│  - Timeout enforcement                      │
│  - Memory limits                            │
│  - No file system persistence               │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│        Layer 4: Error Handling              │
│  - No sensitive data in errors              │
│  - Sanitized error messages                 │
│  - Correlation ID tracking                  │
└─────────────────────────────────────────────┘
```

---

## Monitoring and Observability

### Logging Levels

```python
# INFO: Normal operations
"Request received: correlation_id=abc123"
"Prediction completed: latency=234ms"

# WARNING: Unusual but recoverable
"File size near limit: 9.8MB"
"Request took longer than expected: 950ms"

# ERROR: Request failed
"Invalid image format: correlation_id=abc123"
"Out of memory during inference"

# CRITICAL: System failure
"Model failed to load on startup"
"Health check failing"
```

### Metrics to Track

**Request Metrics:**
- Request count (per endpoint)
- Latency (P50, P95, P99)
- Error rate (4xx, 5xx)
- Request size distribution

**Resource Metrics:**
- CPU usage (%)
- Memory usage (MB)
- Memory utilization (%)
- Disk I/O (minimal)

**Application Metrics:**
- Model load time
- Inference time
- Preprocessing time
- Queue depth (if async)

---

## Future Enhancements

This architecture provides a foundation for future improvements:

1. **Batch Inference:** Accept multiple images per request
2. **Async Processing:** Use FastAPI + async for better concurrency
3. **GPU Support:** Add CUDA support for faster inference
4. **Model Versioning:** Support multiple model versions simultaneously
5. **Caching:** Add result caching for repeated requests
6. **Authentication:** Add API key or JWT authentication
7. **Rate Limiting:** Add per-client rate limiting
8. **Metrics Export:** Export Prometheus metrics
9. **Health Checks:** Advanced health checks (model accuracy testing)
10. **Blue-Green Deployment:** Zero-downtime model updates

---

**Document Version:** 1.0
**Last Updated:** October 2025
**Maintained by:** AI Infrastructure Curriculum Team
