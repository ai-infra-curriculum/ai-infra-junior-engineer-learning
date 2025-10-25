# Exercise 01: Observability Foundations Lab

## Overview

Kick off Module 009 by instrumenting a production-ready FastAPI inference service with comprehensive observability: metrics, logs, and traces. You will define SLIs/SLOs, implement structured logging, expose Prometheus metrics, capture OpenTelemetry traces, and establish observability best practices that serve as the foundation for the entire monitoring stack.

**Difficulty:** Beginner → Intermediate
**Estimated Time:** 3–4 hours
**Prerequisites:**
- Completion of Lecture 01 (Observability Fundamentals)
- Familiarity with Python (Module 001) and FastAPI basics (Module 007)
- Docker and Docker Compose (Module 005)
- Basic understanding of Prometheus and OpenTelemetry concepts

## Learning Objectives

By finishing this lab you will be able to:

1. Design and document practical SLIs and SLOs for a microservice
2. Instrument a FastAPI application with Prometheus metrics (counters, histograms, gauges, summaries)
3. Implement structured JSON logging with correlation metadata and trace context
4. Integrate OpenTelemetry tracing with automatic and manual instrumentation
5. Propagate trace context through logs for unified observability
6. Implement the Four Golden Signals (latency, traffic, errors, saturation)
7. Create observability readiness assessments for production services
8. Apply cardinality best practices to avoid metric explosions
9. Implement health check endpoints for monitoring systems
10. Document observability architecture and SLO commitments

## Scenario

The `inference-gateway` service is a critical microservice that exposes a `/predict` endpoint wrapping a PyTorch ResNet-50 image classification model. Product leadership has set aggressive reliability targets (99.5% availability, P99 latency < 300ms) before wider rollout to production traffic.

As the junior AI infrastructure engineer, you're tasked with implementing comprehensive observability foundations so the platform team can:
- Monitor SLO compliance in real-time
- Detect and debug production incidents quickly
- Understand model performance and resource utilization
- Integrate this service into the broader monitoring stack (Prometheus, Grafana, Loki)

This exercise builds the observability foundation that will be extended in subsequent exercises with Prometheus, Grafana, centralized logging, and alerting.

---

## Part 1: Environment Setup and Docker Configuration

### Step 1.1: Create Project Structure

Create a new directory for the inference gateway service with a complete project structure:

```bash
mkdir -p inference-gateway
cd inference-gateway

# Create directory structure
mkdir -p app/{api,core,instrumentation,models}
mkdir -p tests/{unit,integration}
mkdir -p docs
mkdir -p config
mkdir -p scripts

# Create initial files
touch app/__init__.py
touch app/api/__init__.py
touch app/core/__init__.py
touch app/instrumentation/__init__.py
touch app/models/__init__.py
touch tests/__init__.py
touch README.md
touch .env.example
touch .dockerignore
touch docker-compose.yml
```

**Expected Structure:**
```
inference-gateway/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes.py           # API endpoints
│   │   └── dependencies.py     # Dependency injection
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py           # Configuration management
│   │   └── exceptions.py       # Custom exceptions
│   ├── instrumentation/
│   │   ├── __init__.py
│   │   ├── metrics.py          # Prometheus metrics
│   │   ├── logging.py          # Structured logging
│   │   └── tracing.py          # OpenTelemetry tracing
│   └── models/
│       ├── __init__.py
│       └── inference.py        # Model inference logic
├── tests/
│   ├── __init__.py
│   ├── unit/
│   └── integration/
├── docs/
│   ├── slo.md
│   ├── observability-readiness.md
│   └── architecture.md
├── config/
│   └── prometheus.yml          # Local Prometheus config
├── scripts/
│   ├── setup.sh
│   └── load_test.sh
├── requirements.txt
├── requirements-dev.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── .dockerignore
├── pytest.ini
└── README.md
```

### Step 1.2: Define Dependencies

Create `requirements.txt` with production dependencies:

```txt
# requirements.txt
# FastAPI and web server
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
pydantic-settings==2.1.0

# Observability - Metrics
prometheus-client==0.19.0

# Observability - Logging
structlog==23.2.0
python-json-logger==2.0.7

# Observability - Tracing
opentelemetry-api==1.21.0
opentelemetry-sdk==1.21.0
opentelemetry-instrumentation-fastapi==0.42b0
opentelemetry-instrumentation-logging==0.42b0
opentelemetry-exporter-otlp==1.21.0
opentelemetry-exporter-otlp-proto-http==1.21.0

# ML Libraries (for model inference)
torch==2.1.1
torchvision==0.16.1
Pillow==10.1.0
numpy==1.26.2

# Utilities
python-multipart==0.0.6
httpx==0.25.2
tenacity==8.2.3
```

Create `requirements-dev.txt` for development and testing:

```txt
# requirements-dev.txt
-r requirements.txt

# Testing
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
pytest-mock==3.12.0
httpx==0.25.2

# Code Quality
black==23.12.1
ruff==0.1.8
mypy==1.7.1

# Load Testing
locust==2.19.1
```

### Step 1.3: Create Dockerfile

Create a production-ready multi-stage `Dockerfile`:

```dockerfile
# Dockerfile
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Create app user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# ============================================
# Development stage
# ============================================
FROM base as development

# Install development dependencies
COPY requirements-dev.txt .
RUN pip install --no-cache-dir -r requirements-dev.txt

# Copy application code
COPY . .

# Change ownership
RUN chown -R appuser:appuser /app

USER appuser

# Expose ports
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/healthz || exit 1

# Run with auto-reload for development
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# ============================================
# Production stage
# ============================================
FROM base as production

# Install production dependencies only
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/

# Download and cache model weights (optional - remove if too large)
# RUN python -c "import torchvision.models as models; models.resnet50(pretrained=True)"

# Change ownership
RUN chown -R appuser:appuser /app

USER appuser

# Expose ports
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/healthz || exit 1

# Run with production settings
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### Step 1.4: Create Docker Compose Configuration

Create `docker-compose.yml` for local development with observability stack:

```yaml
# docker-compose.yml
version: '3.9'

services:
  # Inference Gateway Service
  inference-gateway:
    build:
      context: .
      dockerfile: Dockerfile
      target: development
    container_name: inference-gateway
    ports:
      - "8000:8000"
      - "8001:8001"  # Optional: admin/debug port
    environment:
      - LOG_LEVEL=INFO
      - ENVIRONMENT=development
      - SERVICE_NAME=inference-gateway
      - SERVICE_VERSION=1.0.0
      - OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4318
      - OTEL_SERVICE_NAME=inference-gateway
      - OTEL_TRACES_EXPORTER=otlp
      - OTEL_METRICS_EXPORTER=none
      - OTEL_LOGS_EXPORTER=none
    volumes:
      - ./app:/app/app
      - ./tests:/app/tests
      - ./docs:/app/docs
    depends_on:
      - otel-collector
    networks:
      - observability
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/healthz"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  # OpenTelemetry Collector (for trace collection)
  otel-collector:
    image: otel/opentelemetry-collector:0.91.0
    container_name: otel-collector
    command: ["--config=/etc/otel-collector-config.yml"]
    volumes:
      - ./config/otel-collector-config.yml:/etc/otel-collector-config.yml
    ports:
      - "4317:4317"   # OTLP gRPC receiver
      - "4318:4318"   # OTLP HTTP receiver
      - "13133:13133" # health_check extension
    networks:
      - observability

  # Jaeger (for trace visualization - optional for this exercise)
  jaeger:
    image: jaegertracing/all-in-one:1.52
    container_name: jaeger
    ports:
      - "16686:16686"  # Jaeger UI
      - "14268:14268"  # Jaeger collector HTTP
    environment:
      - COLLECTOR_OTLP_ENABLED=true
    networks:
      - observability

  # Prometheus (for metrics - will be expanded in Exercise 02)
  prometheus:
    image: prom/prometheus:v2.48.1
    container_name: prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/usr/share/prometheus/console_libraries'
      - '--web.console.templates=/usr/share/prometheus/consoles'
      - '--web.enable-lifecycle'
    volumes:
      - ./config/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
    ports:
      - "9090:9090"
    networks:
      - observability

networks:
  observability:
    driver: bridge

volumes:
  prometheus-data:
```

### Step 1.5: Create OpenTelemetry Collector Configuration

Create `config/otel-collector-config.yml`:

```yaml
# config/otel-collector-config.yml
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317
      http:
        endpoint: 0.0.0.0:4318

processors:
  batch:
    timeout: 10s
    send_batch_size: 1024

  # Add resource attributes
  resource:
    attributes:
      - key: environment
        value: development
        action: upsert

exporters:
  # Export to Jaeger for visualization
  otlp/jaeger:
    endpoint: jaeger:4317
    tls:
      insecure: true

  # Console exporter for debugging
  logging:
    loglevel: info

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [batch, resource]
      exporters: [otlp/jaeger, logging]

  extensions: [health_check]

extensions:
  health_check:
    endpoint: 0.0.0.0:13133
```

### Step 1.6: Create Prometheus Configuration

Create `config/prometheus.yml`:

```yaml
# config/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    cluster: 'dev'
    environment: 'development'

scrape_configs:
  # Scrape the inference gateway service
  - job_name: 'inference-gateway'
    static_configs:
      - targets: ['inference-gateway:8000']
        labels:
          service: 'inference-gateway'
          team: 'ml-platform'

  # Scrape Prometheus itself
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']
```

### Step 1.7: Create Environment Configuration

Create `.env.example`:

```bash
# .env.example
# Application Settings
SERVICE_NAME=inference-gateway
SERVICE_VERSION=1.0.0
ENVIRONMENT=development
LOG_LEVEL=INFO

# Server Configuration
HOST=0.0.0.0
PORT=8000
WORKERS=4

# Model Configuration
MODEL_NAME=resnet50
MODEL_DEVICE=cpu
MODEL_BATCH_SIZE=1

# OpenTelemetry Configuration
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318
OTEL_SERVICE_NAME=inference-gateway
OTEL_TRACES_EXPORTER=otlp
OTEL_METRICS_EXPORTER=none
OTEL_LOGS_EXPORTER=none

# Prometheus Configuration
METRICS_PORT=8000
METRICS_PATH=/metrics

# SLO Targets (for documentation/reference)
SLO_AVAILABILITY_TARGET=99.5
SLO_P99_LATENCY_MS=300
SLO_ERROR_RATE_MAX=0.5
```

Copy to `.env`:
```bash
cp .env.example .env
```

**✅ Checkpoint:** Verify directory structure and configuration files are created correctly.

---

## Part 2: Configuration Management with Pydantic Settings

### Step 2.1: Create Configuration Module

Create `app/core/config.py`:

```python
# app/core/config.py
"""
Configuration management using Pydantic Settings.
Loads configuration from environment variables with validation.
"""
from typing import Literal
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application Settings
    service_name: str = Field(default="inference-gateway", description="Service name")
    service_version: str = Field(default="1.0.0", description="Service version")
    environment: Literal["development", "staging", "production"] = Field(
        default="development", description="Deployment environment"
    )
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO", description="Logging level"
    )

    # Server Configuration
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, ge=1024, le=65535, description="Server port")
    workers: int = Field(default=4, ge=1, le=16, description="Number of workers")

    # Model Configuration
    model_name: str = Field(default="resnet50", description="Model architecture")
    model_device: Literal["cpu", "cuda", "mps"] = Field(
        default="cpu", description="Device for model inference"
    )
    model_batch_size: int = Field(
        default=1, ge=1, le=128, description="Inference batch size"
    )

    # OpenTelemetry Configuration
    otel_exporter_otlp_endpoint: str = Field(
        default="http://localhost:4318", description="OTLP endpoint"
    )
    otel_service_name: str = Field(
        default="inference-gateway", description="OTEL service name"
    )
    otel_traces_exporter: str = Field(
        default="otlp", description="Trace exporter type"
    )

    # Metrics Configuration
    metrics_port: int = Field(
        default=8000, ge=1024, le=65535, description="Metrics port"
    )
    metrics_path: str = Field(default="/metrics", description="Metrics endpoint path")

    # SLO Targets (for reference)
    slo_availability_target: float = Field(
        default=99.5, ge=0.0, le=100.0, description="Availability SLO target (%)"
    )
    slo_p99_latency_ms: int = Field(
        default=300, ge=1, description="P99 latency SLO target (ms)"
    )
    slo_error_rate_max: float = Field(
        default=0.5, ge=0.0, le=100.0, description="Max error rate SLO (%)"
    )

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment == "development"


# Global settings instance
settings = Settings()
```

**Key Features:**
- Type-safe configuration with Pydantic validation
- Environment variable loading
- Sensible defaults
- Production/development checks
- SLO targets for documentation

### Step 2.2: Create Custom Exceptions

Create `app/core/exceptions.py`:

```python
# app/core/exceptions.py
"""Custom exceptions for the inference gateway service."""


class InferenceGatewayException(Exception):
    """Base exception for all service-specific errors."""

    def __init__(self, message: str, error_code: str = "UNKNOWN_ERROR"):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class ModelNotLoadedError(InferenceGatewayException):
    """Raised when model is not loaded or initialization failed."""

    def __init__(self, message: str = "Model not loaded"):
        super().__init__(message, error_code="MODEL_NOT_LOADED")


class InferenceError(InferenceGatewayException):
    """Raised when inference fails."""

    def __init__(self, message: str = "Inference failed"):
        super().__init__(message, error_code="INFERENCE_ERROR")


class InvalidInputError(InferenceGatewayException):
    """Raised when input validation fails."""

    def __init__(self, message: str = "Invalid input"):
        super().__init__(message, error_code="INVALID_INPUT")


class ServiceUnavailableError(InferenceGatewayException):
    """Raised when service is temporarily unavailable."""

    def __init__(self, message: str = "Service temporarily unavailable"):
        super().__init__(message, error_code="SERVICE_UNAVAILABLE")
```

**✅ Checkpoint:** Configuration module loads correctly with environment variables.

---

## Part 3: Implement Structured Logging with Trace Context

### Step 3.1: Create Logging Module

Create `app/instrumentation/logging.py`:

```python
# app/instrumentation/logging.py
"""
Structured logging configuration with OpenTelemetry trace context.
Outputs JSON logs with correlation IDs for unified observability.
"""
import logging
import sys
from typing import Any

import structlog
from opentelemetry import trace
from pythonjsonlogger import jsonlogger

from app.core.config import settings


def add_trace_context(
    logger: logging.Logger, method_name: str, event_dict: dict[str, Any]
) -> dict[str, Any]:
    """
    Add OpenTelemetry trace context to log entries.

    Adds trace_id and span_id to every log for correlation with traces.
    """
    span = trace.get_current_span()
    if span and span.get_span_context().is_valid:
        span_context = span.get_span_context()
        event_dict["trace_id"] = format(span_context.trace_id, "032x")
        event_dict["span_id"] = format(span_context.span_id, "016x")
        event_dict["trace_flags"] = span_context.trace_flags
    return event_dict


def add_service_context(
    logger: logging.Logger, method_name: str, event_dict: dict[str, Any]
) -> dict[str, Any]:
    """Add service metadata to all log entries."""
    event_dict["service"] = settings.service_name
    event_dict["version"] = settings.service_version
    event_dict["environment"] = settings.environment
    return event_dict


def configure_logging() -> None:
    """
    Configure structured logging with JSON output and trace context.

    Sets up structlog with:
    - JSON formatting for machine readability
    - OpenTelemetry trace context injection
    - Service metadata (name, version, environment)
    - Timestamp and log level
    - Consistent field naming
    """
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.log_level),
    )

    # Configure structlog
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            add_service_context,
            add_trace_context,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.BoundLogger:
    """
    Get a logger instance for the specified module.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Configured structlog logger
    """
    return structlog.get_logger(name)


# Initialize logging on module import
configure_logging()
```

**Key Features:**
- Automatic trace context injection (trace_id, span_id)
- Service metadata on every log
- JSON output for log aggregation
- ISO timestamps with UTC
- Structured fields for filtering

**Example Log Output:**
```json
{
  "event": "request_completed",
  "timestamp": "2025-10-23T10:15:30.123456Z",
  "level": "info",
  "logger": "app.api.routes",
  "service": "inference-gateway",
  "version": "1.0.0",
  "environment": "development",
  "trace_id": "5f3a2b1c0d9e8f7a6b5c4d3e2f1a0b9c",
  "span_id": "1a2b3c4d5e6f7a8b",
  "method": "POST",
  "path": "/predict",
  "status_code": 200,
  "latency_ms": 145.67,
  "model_version": "resnet50-v1"
}
```

**✅ Checkpoint:** Import the logging module and verify JSON output:

```python
from app.instrumentation.logging import get_logger

logger = get_logger(__name__)
logger.info("test_log", foo="bar", count=42)
```

---

## Part 4: Implement Prometheus Metrics

### Step 4.1: Create Metrics Module

Create `app/instrumentation/metrics.py`:

```python
# app/instrumentation/metrics.py
"""
Prometheus metrics instrumentation for the inference gateway.

Implements the Four Golden Signals:
- Latency: Request duration histograms
- Traffic: Request rate counters
- Errors: Error rate counters
- Saturation: Queue depth and resource usage gauges
"""
from typing import Callable
import time
from functools import wraps

from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    Summary,
    Info,
    CollectorRegistry,
    REGISTRY,
)

from app.core.config import settings


# ============================================
# Metric Definitions
# ============================================

# Traffic: Request counters
http_requests_total = Counter(
    name="http_requests_total",
    documentation="Total HTTP requests by method, endpoint, and status",
    labelnames=["method", "endpoint", "status_code"],
    registry=REGISTRY,
)

inference_requests_total = Counter(
    name="inference_requests_total",
    documentation="Total inference requests by model, version, and status",
    labelnames=["model_name", "model_version", "status"],
    registry=REGISTRY,
)

# Latency: Request duration histograms
http_request_duration_seconds = Histogram(
    name="http_request_duration_seconds",
    documentation="HTTP request duration in seconds",
    labelnames=["method", "endpoint"],
    buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
    registry=REGISTRY,
)

inference_duration_seconds = Histogram(
    name="inference_duration_seconds",
    documentation="Model inference duration in seconds",
    labelnames=["model_name", "model_version"],
    buckets=[0.01, 0.025, 0.05, 0.1, 0.15, 0.2, 0.3, 0.5, 0.75, 1.0, 2.0],
    registry=REGISTRY,
)

inference_preprocessing_duration_seconds = Histogram(
    name="inference_preprocessing_duration_seconds",
    documentation="Input preprocessing duration in seconds",
    labelnames=["model_name"],
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5],
    registry=REGISTRY,
)

inference_postprocessing_duration_seconds = Histogram(
    name="inference_postprocessing_duration_seconds",
    documentation="Output postprocessing duration in seconds",
    labelnames=["model_name"],
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5],
    registry=REGISTRY,
)

# Errors: Error counters
http_errors_total = Counter(
    name="http_errors_total",
    documentation="Total HTTP errors by method, endpoint, and error type",
    labelnames=["method", "endpoint", "error_type"],
    registry=REGISTRY,
)

inference_errors_total = Counter(
    name="inference_errors_total",
    documentation="Total inference errors by model, version, and error type",
    labelnames=["model_name", "model_version", "error_type"],
    registry=REGISTRY,
)

# Saturation: Queue depth and resource usage
inference_queue_depth = Gauge(
    name="inference_queue_depth",
    documentation="Current number of requests in inference queue",
    registry=REGISTRY,
)

model_memory_bytes = Gauge(
    name="model_memory_bytes",
    documentation="Model memory usage in bytes",
    labelnames=["model_name"],
    registry=REGISTRY,
)

# ML-Specific Metrics
inference_batch_size = Histogram(
    name="inference_batch_size",
    documentation="Inference batch size distribution",
    labelnames=["model_name"],
    buckets=[1, 2, 4, 8, 16, 32, 64, 128],
    registry=REGISTRY,
)

inference_confidence_score = Histogram(
    name="inference_confidence_score",
    documentation="Model confidence score distribution",
    labelnames=["model_name", "predicted_class"],
    buckets=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.99, 1.0],
    registry=REGISTRY,
)

model_predictions_total = Counter(
    name="model_predictions_total",
    documentation="Total model predictions by class",
    labelnames=["model_name", "predicted_class"],
    registry=REGISTRY,
)

# Application Info
app_info = Info(
    name="app",
    documentation="Application information",
    registry=REGISTRY,
)

# Initialize app info
app_info.info(
    {
        "service": settings.service_name,
        "version": settings.service_version,
        "environment": settings.environment,
    }
)


# ============================================
# Metric Utilities
# ============================================

class MetricsMiddleware:
    """
    Middleware to automatically track HTTP request metrics.

    Records:
    - Request count by method, endpoint, status
    - Request duration by method, endpoint
    - Error count by method, endpoint, error type
    """

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        method = scope["method"]
        path = scope["path"]

        # Skip metrics endpoint to avoid recursion
        if path == "/metrics":
            await self.app(scope, receive, send)
            return

        start_time = time.perf_counter()
        status_code = 500  # Default to error

        async def send_wrapper(message):
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        except Exception as e:
            http_errors_total.labels(
                method=method, endpoint=path, error_type=type(e).__name__
            ).inc()
            raise
        finally:
            duration = time.perf_counter() - start_time

            # Record metrics
            http_requests_total.labels(
                method=method, endpoint=path, status_code=status_code
            ).inc()

            http_request_duration_seconds.labels(method=method, endpoint=path).observe(
                duration
            )


def track_inference_time(model_name: str, model_version: str) -> Callable:
    """
    Decorator to track inference duration and count.

    Usage:
        @track_inference_time("resnet50", "v1")
        async def run_inference(input_data):
            ...
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            status = "success"

            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                status = "failure"
                inference_errors_total.labels(
                    model_name=model_name,
                    model_version=model_version,
                    error_type=type(e).__name__,
                ).inc()
                raise
            finally:
                duration = time.perf_counter() - start_time
                inference_duration_seconds.labels(
                    model_name=model_name, model_version=model_version
                ).observe(duration)

                inference_requests_total.labels(
                    model_name=model_name, model_version=model_version, status=status
                ).inc()

        return wrapper

    return decorator


# ============================================
# Metric Helpers
# ============================================

def record_preprocessing_time(model_name: str, duration: float) -> None:
    """Record preprocessing duration."""
    inference_preprocessing_duration_seconds.labels(model_name=model_name).observe(
        duration
    )


def record_postprocessing_time(model_name: str, duration: float) -> None:
    """Record postprocessing duration."""
    inference_postprocessing_duration_seconds.labels(model_name=model_name).observe(
        duration
    )


def record_prediction(
    model_name: str, predicted_class: str, confidence: float
) -> None:
    """Record model prediction and confidence."""
    model_predictions_total.labels(
        model_name=model_name, predicted_class=predicted_class
    ).inc()

    inference_confidence_score.labels(
        model_name=model_name, predicted_class=predicted_class
    ).observe(confidence)


def set_queue_depth(depth: int) -> None:
    """Set current inference queue depth."""
    inference_queue_depth.set(depth)


def set_model_memory(model_name: str, memory_bytes: int) -> None:
    """Set model memory usage in bytes."""
    model_memory_bytes.labels(model_name=model_name).set(memory_bytes)
```

**Key Features:**
- **Four Golden Signals**: Latency, Traffic, Errors, Saturation
- **HTTP metrics**: Request count, duration, errors
- **Inference metrics**: Duration, preprocessing, postprocessing
- **ML-specific metrics**: Confidence scores, predictions by class, batch sizes
- **Automatic tracking**: Decorator and middleware patterns
- **Cardinality control**: Limited label values to prevent metric explosion

**Histogram Bucket Design:**
- HTTP requests: 5ms to 10s (web service latency range)
- Inference: 10ms to 2s (model execution range)
- Preprocessing/postprocessing: 1ms to 500ms (data transformation range)

**✅ Checkpoint:** Metrics are defined and can be imported without errors.

---

## Part 5: Implement OpenTelemetry Tracing

### Step 5.1: Create Tracing Module

Create `app/instrumentation/tracing.py`:

```python
# app/instrumentation/tracing.py
"""
OpenTelemetry tracing configuration for distributed tracing.

Provides:
- Automatic instrumentation for FastAPI
- Manual span creation for custom operations
- Trace context propagation
- OTLP export to collector
"""
import logging
from typing import Optional

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.resources import Resource, SERVICE_NAME, SERVICE_VERSION
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor

from app.core.config import settings

logger = logging.getLogger(__name__)


def configure_tracing() -> None:
    """
    Configure OpenTelemetry tracing with OTLP export.

    Sets up:
    - Resource attributes (service name, version)
    - Trace provider
    - OTLP exporter (or console exporter for development)
    - Batch span processor
    """
    # Create resource with service information
    resource = Resource.create(
        {
            SERVICE_NAME: settings.otel_service_name,
            SERVICE_VERSION: settings.service_version,
            "deployment.environment": settings.environment,
        }
    )

    # Create tracer provider
    provider = TracerProvider(resource=resource)

    # Configure span processor and exporter
    if settings.environment == "development":
        # Use console exporter for local development
        console_exporter = ConsoleSpanExporter()
        provider.add_span_processor(BatchSpanProcessor(console_exporter))
        logger.info("Tracing configured with ConsoleSpanExporter")

    try:
        # Try to use OTLP exporter
        otlp_exporter = OTLPSpanExporter(
            endpoint=f"{settings.otel_exporter_otlp_endpoint}/v1/traces"
        )
        provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
        logger.info(
            f"Tracing configured with OTLPSpanExporter: {settings.otel_exporter_otlp_endpoint}"
        )
    except Exception as e:
        logger.warning(f"Failed to configure OTLP exporter: {e}")
        # Fallback to console exporter
        console_exporter = ConsoleSpanExporter()
        provider.add_span_processor(BatchSpanProcessor(console_exporter))

    # Set global tracer provider
    trace.set_tracer_provider(provider)

    # Instrument logging to add trace context
    LoggingInstrumentor().instrument(set_logging_format=False)

    logger.info("OpenTelemetry tracing configured successfully")


def instrument_fastapi(app) -> None:
    """
    Instrument FastAPI application with automatic tracing.

    Args:
        app: FastAPI application instance
    """
    FastAPIInstrumentor.instrument_app(app)
    logger.info("FastAPI instrumented with OpenTelemetry")


def get_tracer(name: str) -> trace.Tracer:
    """
    Get a tracer instance for manual span creation.

    Args:
        name: Tracer name (typically module name)

    Returns:
        OpenTelemetry tracer
    """
    return trace.get_tracer(name)


def get_current_trace_id() -> Optional[str]:
    """
    Get current trace ID as hex string.

    Returns:
        Trace ID or None if no active span
    """
    span = trace.get_current_span()
    if span and span.get_span_context().is_valid:
        return format(span.get_span_context().trace_id, "032x")
    return None


def get_current_span_id() -> Optional[str]:
    """
    Get current span ID as hex string.

    Returns:
        Span ID or None if no active span
    """
    span = trace.get_current_span()
    if span and span.get_span_context().is_valid:
        return format(span.get_span_context().span_id, "016x")
    return None
```

**Key Features:**
- Automatic FastAPI instrumentation
- OTLP export to collector
- Console export for development
- Trace context helpers
- Resource attributes (service, version, environment)

**✅ Checkpoint:** Tracing module imports without errors.

---

## Part 6: Implement Model Inference

### Step 6.1: Create Inference Module

Create `app/models/inference.py`:

```python
# app/models/inference.py
"""
Model inference logic with observability instrumentation.

Implements:
- Model loading and initialization
- Input preprocessing
- Inference execution
- Output postprocessing
- Comprehensive metrics tracking
"""
import time
from typing import List, Dict, Any
import io

import torch
import torchvision.transforms as transforms
import torchvision.models as models
from PIL import Image
import numpy as np

from opentelemetry import trace

from app.core.config import settings
from app.core.exceptions import ModelNotLoadedError, InferenceError, InvalidInputError
from app.instrumentation.logging import get_logger
from app.instrumentation import metrics

logger = get_logger(__name__)
tracer = trace.get_tracer(__name__)

# ImageNet class labels (abbreviated for this exercise)
# In production, load from a complete file
IMAGENET_CLASSES = [
    "tench", "goldfish", "great_white_shark", "tiger_shark", "hammerhead",
    # ... (1000 classes total)
]


class ModelInferenceService:
    """
    Singleton service for model inference with observability.

    Handles model lifecycle, preprocessing, inference, and postprocessing
    with comprehensive instrumentation.
    """

    def __init__(self):
        self.model: Optional[torch.nn.Module] = None
        self.device: torch.device = torch.device(settings.model_device)
        self.model_name = settings.model_name
        self.model_version = "v1.0"
        self.transform = self._create_transform()
        self._is_loaded = False

    def _create_transform(self) -> transforms.Compose:
        """Create image preprocessing transform pipeline."""
        return transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]
            ),
        ])

    @tracer.start_as_current_span("load_model")
    def load_model(self) -> None:
        """
        Load model weights and move to device.

        Raises:
            ModelNotLoadedError: If model loading fails
        """
        if self._is_loaded:
            logger.info("Model already loaded", model_name=self.model_name)
            return

        try:
            logger.info(
                "Loading model", model_name=self.model_name, device=str(self.device)
            )

            # Load pretrained ResNet-50
            if self.model_name == "resnet50":
                self.model = models.resnet50(pretrained=True)
            else:
                raise ModelNotLoadedError(f"Unknown model: {self.model_name}")

            # Move to device and set to eval mode
            self.model.to(self.device)
            self.model.eval()

            self._is_loaded = True

            # Record model memory usage (approximate)
            param_size = sum(p.numel() * p.element_size() for p in self.model.parameters())
            buffer_size = sum(b.numel() * b.element_size() for b in self.model.buffers())
            total_memory = param_size + buffer_size

            metrics.set_model_memory(self.model_name, total_memory)

            logger.info(
                "Model loaded successfully",
                model_name=self.model_name,
                device=str(self.device),
                memory_bytes=total_memory,
            )

        except Exception as e:
            logger.error(
                "Model loading failed", model_name=self.model_name, error=str(e)
            )
            raise ModelNotLoadedError(f"Failed to load model: {e}") from e

    @tracer.start_as_current_span("preprocess_image")
    def preprocess_image(self, image_bytes: bytes) -> torch.Tensor:
        """
        Preprocess image bytes to model input tensor.

        Args:
            image_bytes: Raw image bytes

        Returns:
            Preprocessed tensor ready for inference

        Raises:
            InvalidInputError: If image is invalid
        """
        start_time = time.perf_counter()

        try:
            # Load image from bytes
            image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

            # Apply transformations
            tensor = self.transform(image)

            # Add batch dimension
            tensor = tensor.unsqueeze(0)

            # Move to device
            tensor = tensor.to(self.device)

            duration = time.perf_counter() - start_time
            metrics.record_preprocessing_time(self.model_name, duration)

            logger.debug(
                "Image preprocessed",
                model_name=self.model_name,
                duration_ms=duration * 1000,
                tensor_shape=list(tensor.shape),
            )

            return tensor

        except Exception as e:
            logger.error("Preprocessing failed", error=str(e))
            raise InvalidInputError(f"Failed to preprocess image: {e}") from e

    @tracer.start_as_current_span("run_inference")
    @metrics.track_inference_time("resnet50", "v1.0")
    async def predict(self, image_bytes: bytes) -> Dict[str, Any]:
        """
        Run inference on image and return top predictions.

        Args:
            image_bytes: Raw image bytes

        Returns:
            Dictionary with predictions and metadata

        Raises:
            ModelNotLoadedError: If model not loaded
            InferenceError: If inference fails
        """
        if not self._is_loaded:
            raise ModelNotLoadedError("Model not loaded. Call load_model() first.")

        with tracer.start_as_current_span("inference_pipeline") as span:
            try:
                # Preprocess
                input_tensor = self.preprocess_image(image_bytes)

                # Inference
                start_time = time.perf_counter()

                with torch.no_grad():
                    outputs = self.model(input_tensor)

                inference_duration = time.perf_counter() - start_time

                span.set_attribute("inference.duration_ms", inference_duration * 1000)
                span.set_attribute("inference.model_name", self.model_name)

                # Postprocessing
                postprocess_start = time.perf_counter()

                probabilities = torch.nn.functional.softmax(outputs[0], dim=0)
                top5_prob, top5_idx = torch.topk(probabilities, 5)

                predictions = []
                for i in range(5):
                    class_idx = top5_idx[i].item()
                    confidence = top5_prob[i].item()

                    # Use placeholder class name (in production, load full ImageNet labels)
                    class_name = IMAGENET_CLASSES[class_idx] if class_idx < len(IMAGENET_CLASSES) else f"class_{class_idx}"

                    predictions.append({
                        "class": class_name,
                        "class_id": class_idx,
                        "confidence": round(confidence, 4),
                    })

                    # Record prediction metrics
                    if i == 0:  # Only record top prediction to control cardinality
                        metrics.record_prediction(
                            self.model_name, class_name, confidence
                        )

                postprocess_duration = time.perf_counter() - postprocess_start
                metrics.record_postprocessing_time(self.model_name, postprocess_duration)

                # Record batch size
                metrics.inference_batch_size.labels(model_name=self.model_name).observe(
                    input_tensor.shape[0]
                )

                logger.info(
                    "Inference completed",
                    model_name=self.model_name,
                    top_prediction=predictions[0]["class"],
                    top_confidence=predictions[0]["confidence"],
                    inference_duration_ms=inference_duration * 1000,
                )

                return {
                    "predictions": predictions,
                    "model_name": self.model_name,
                    "model_version": self.model_version,
                    "inference_duration_ms": round(inference_duration * 1000, 2),
                }

            except (ModelNotLoadedError, InvalidInputError):
                raise
            except Exception as e:
                logger.error("Inference failed", model_name=self.model_name, error=str(e))
                raise InferenceError(f"Inference failed: {e}") from e


# Global singleton instance
model_service = ModelInferenceService()
```

**Key Features:**
- Model lifecycle management
- Comprehensive error handling
- Distributed tracing with spans
- Metrics for preprocessing, inference, postprocessing
- ML-specific metrics (confidence, predictions by class)
- Memory tracking

**✅ Checkpoint:** Inference module imports correctly.

---

## Part 7: Create FastAPI Application and Routes

### Step 7.1: Create API Dependencies

Create `app/api/dependencies.py`:

```python
# app/api/dependencies.py
"""FastAPI dependencies for dependency injection."""
from typing import Generator

from app.models.inference import model_service, ModelInferenceService


def get_model_service() -> Generator[ModelInferenceService, None, None]:
    """Dependency to get model service instance."""
    yield model_service
```

### Step 7.2: Create API Routes

Create `app/api/routes.py`:

```python
# app/api/routes.py
"""API route handlers for the inference gateway."""
from typing import Dict, Any

from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, status
from opentelemetry import trace

from app.models.inference import ModelInferenceService
from app.api.dependencies import get_model_service
from app.core.exceptions import (
    ModelNotLoadedError,
    InferenceError,
    InvalidInputError,
)
from app.instrumentation.logging import get_logger
from app.instrumentation import metrics

logger = get_logger(__name__)
tracer = trace.get_tracer(__name__)

router = APIRouter()


@router.get("/healthz", status_code=status.HTTP_200_OK, tags=["health"])
async def health_check() -> Dict[str, str]:
    """
    Health check endpoint for liveness probe.

    Returns:
        Status message
    """
    return {"status": "healthy"}


@router.get("/readyz", status_code=status.HTTP_200_OK, tags=["health"])
async def readiness_check(
    model_service: ModelInferenceService = Depends(get_model_service),
) -> Dict[str, Any]:
    """
    Readiness check endpoint for readiness probe.

    Verifies model is loaded and ready to serve requests.

    Returns:
        Status message with model info

    Raises:
        HTTPException: If model not ready
    """
    if not model_service._is_loaded:
        logger.warning("Readiness check failed: model not loaded")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model not loaded",
        )

    return {
        "status": "ready",
        "model_name": model_service.model_name,
        "model_version": model_service.model_version,
        "device": str(model_service.device),
    }


@router.post("/predict", status_code=status.HTTP_200_OK, tags=["inference"])
async def predict(
    file: UploadFile = File(..., description="Image file to classify"),
    model_service: ModelInferenceService = Depends(get_model_service),
) -> Dict[str, Any]:
    """
    Run inference on uploaded image.

    Args:
        file: Uploaded image file
        model_service: Injected model service

    Returns:
        Prediction results with top-5 classes and confidences

    Raises:
        HTTPException: If inference fails
    """
    with tracer.start_as_current_span("predict_endpoint") as span:
        try:
            # Read image bytes
            image_bytes = await file.read()

            span.set_attribute("file.name", file.filename or "unknown")
            span.set_attribute("file.size_bytes", len(image_bytes))

            # Run inference
            result = await model_service.predict(image_bytes)

            logger.info(
                "Prediction successful",
                filename=file.filename,
                top_prediction=result["predictions"][0]["class"],
                confidence=result["predictions"][0]["confidence"],
            )

            return result

        except ModelNotLoadedError as e:
            logger.error("Model not loaded", error=str(e))
            metrics.http_errors_total.labels(
                method="POST", endpoint="/predict", error_type="ModelNotLoadedError"
            ).inc()
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e)
            )

        except InvalidInputError as e:
            logger.error("Invalid input", error=str(e), filename=file.filename)
            metrics.http_errors_total.labels(
                method="POST", endpoint="/predict", error_type="InvalidInputError"
            ).inc()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

        except InferenceError as e:
            logger.error("Inference failed", error=str(e))
            metrics.http_errors_total.labels(
                method="POST", endpoint="/predict", error_type="InferenceError"
            ).inc()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
            )

        except Exception as e:
            logger.error("Unexpected error", error=str(e), error_type=type(e).__name__)
            metrics.http_errors_total.labels(
                method="POST", endpoint="/predict", error_type="UnexpectedError"
            ).inc()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error",
            )
```

**Key Features:**
- Health and readiness checks
- File upload handling
- Comprehensive error handling
- Metrics tracking
- Distributed tracing
- Structured logging

### Step 7.3: Create Main Application

Create `app/main.py`:

```python
# app/main.py
"""
FastAPI application entry point with observability instrumentation.

Configures:
- FastAPI application
- Prometheus metrics endpoint
- OpenTelemetry tracing
- Structured logging
- Error handlers
- CORS middleware
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app

from app.core.config import settings
from app.core.exceptions import InferenceGatewayException
from app.api.routes import router
from app.models.inference import model_service
from app.instrumentation.logging import get_logger
from app.instrumentation.tracing import configure_tracing, instrument_fastapi
from app.instrumentation.metrics import MetricsMiddleware

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.

    Startup:
    - Configure tracing
    - Load ML model

    Shutdown:
    - Cleanup resources
    """
    # Startup
    logger.info(
        "Starting application",
        service=settings.service_name,
        version=settings.service_version,
        environment=settings.environment,
    )

    # Configure OpenTelemetry tracing
    configure_tracing()

    # Load model
    try:
        model_service.load_model()
        logger.info("Model loaded successfully")
    except Exception as e:
        logger.error("Failed to load model during startup", error=str(e))
        # Continue startup even if model loading fails
        # Readiness check will catch this

    yield

    # Shutdown
    logger.info("Shutting down application")


# Create FastAPI application
app = FastAPI(
    title="Inference Gateway",
    description="ML model inference service with comprehensive observability",
    version=settings.service_version,
    lifespan=lifespan,
    docs_url="/docs" if settings.is_development else None,
    redoc_url="/redoc" if settings.is_development else None,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.is_development else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add metrics middleware
app.add_middleware(MetricsMiddleware)

# Instrument with OpenTelemetry
instrument_fastapi(app)

# Include API routes
app.include_router(router)

# Mount Prometheus metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


# Exception handlers
@app.exception_handler(InferenceGatewayException)
async def inference_gateway_exception_handler(
    request: Request, exc: InferenceGatewayException
) -> JSONResponse:
    """Handle custom application exceptions."""
    logger.error(
        "Application exception",
        error_code=exc.error_code,
        error_message=exc.message,
        path=request.url.path,
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": exc.error_code, "message": exc.message},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions."""
    logger.error(
        "Unhandled exception",
        error_type=type(exc).__name__,
        error_message=str(exc),
        path=request.url.path,
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "INTERNAL_SERVER_ERROR", "message": "Internal server error"},
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.is_development,
        log_level=settings.log_level.lower(),
    )
```

**Key Features:**
- Lifespan handlers for startup/shutdown
- Prometheus metrics mounted at `/metrics`
- OpenTelemetry instrumentation
- CORS middleware
- Exception handlers
- Conditional API docs (dev only)

**✅ Checkpoint:** Application starts successfully:

```bash
# Start with Docker Compose
docker-compose up --build

# Or run locally
python -m app.main
```

Verify endpoints:
- http://localhost:8000/docs (Swagger UI)
- http://localhost:8000/healthz (Health check)
- http://localhost:8000/readyz (Readiness check)
- http://localhost:8000/metrics (Prometheus metrics)

---

## Part 8: Define SLIs and SLOs

Create `docs/slo.md`:

```markdown
# Service Level Objectives (SLOs)

## Overview

This document defines the Service Level Indicators (SLIs) and Service Level Objectives (SLOs) for the `inference-gateway` service.

**Service**: inference-gateway
**Owner**: ML Platform Team
**Last Updated**: 2025-10-23
**Review Cycle**: Quarterly

---

## SLO Summary

| SLI | Objective | Measurement Window | Error Budget |
|-----|-----------|-------------------|--------------|
| Availability | 99.5% | 28-day rolling | 0.5% (~3.6 hours/month) |
| P99 Latency | < 300ms | 28-day rolling | - |
| Error Rate | < 0.5% | 28-day rolling | 0.5% of requests |
| Throughput | Support 100 req/s | 1-minute average | - |

---

## Detailed SLIs

### 1. Availability

**Definition**: Percentage of successful HTTP requests (status 200-399) over total requests.

**Metric**: `sum(rate(http_requests_total{status_code!~"5.."}[28d])) / sum(rate(http_requests_total[28d])) * 100`

**Target**: 99.5%

**Measurement Window**: 28-day rolling window

**Error Budget**: 0.5% downtime = ~3.6 hours per month = ~0.86 hours per week

**Alerting**:
- **Warning**: Error budget burn rate > 2x (0.86h remaining for week)
- **Critical**: Error budget burn rate > 5x (immediate page)

**Rationale**: Product requirements mandate 99.5% availability for production traffic. This allows for ~3.6 hours of downtime per month for maintenance, incidents, and deployments.

---

### 2. Request Latency (P99)

**Definition**: 99th percentile of successful request duration for `/predict` endpoint.

**Metric**: `histogram_quantile(0.99, rate(http_request_duration_seconds_bucket{endpoint="/predict"}[28d]))`

**Target**: < 300ms

**Measurement Window**: 28-day rolling window

**Alerting**:
- **Warning**: P99 latency > 300ms for 5 minutes
- **Critical**: P99 latency > 500ms for 5 minutes

**Rationale**: User experience research shows 300ms is the threshold for "instant" response. Exceeding this degrades user satisfaction scores.

---

### 3. Error Rate

**Definition**: Percentage of failed requests (status 500-599) over total requests.

**Metric**: `sum(rate(http_requests_total{status_code=~"5.."}[28d])) / sum(rate(http_requests_total[28d])) * 100`

**Target**: < 0.5%

**Measurement Window**: 28-day rolling window

**Error Budget**: 0.5% of requests = ~432 errors per 100,000 requests

**Alerting**:
- **Warning**: Error rate > 0.5% for 5 minutes
- **Critical**: Error rate > 1% for 5 minutes

**Rationale**: Internal service reliability targets require < 1% error rate. We target 0.5% to maintain buffer for unexpected failures.

---

### 4. Throughput Capacity

**Definition**: Sustained requests per second the service can handle while meeting latency/error SLOs.

**Metric**: `rate(http_requests_total{endpoint="/predict"}[1m])`

**Target**: Support 100 req/s sustained load

**Measurement Window**: 1-minute average

**Alerting**:
- **Warning**: Request rate > 80 req/s (approaching capacity)
- **Critical**: Request rate > 100 req/s with P99 latency > 300ms (capacity exceeded)

**Rationale**: Current traffic projections estimate 50 req/s peak load. Target 100 req/s provides 2x headroom for growth.

---

## ML-Specific SLIs

### 5. Model Inference Latency (P95)

**Definition**: 95th percentile of model inference duration (excluding pre/post-processing).

**Metric**: `histogram_quantile(0.95, rate(inference_duration_seconds_bucket{model_name="resnet50"}[28d]))`

**Target**: < 150ms

**Measurement Window**: 28-day rolling window

**Alerting**:
- **Warning**: P95 inference latency > 150ms for 10 minutes
- **Critical**: P95 inference latency > 200ms for 5 minutes

**Rationale**: Inference latency directly impacts overall request latency. 150ms inference allows ~100ms for network/processing overhead to stay under 300ms total.

---

### 6. Model Confidence Coverage

**Definition**: Percentage of predictions with confidence > 0.7 (high confidence).

**Metric**: `sum(rate(inference_confidence_score_bucket{le="1.0"}[28d])) - sum(rate(inference_confidence_score_bucket{le="0.7"}[28d])) / sum(rate(inference_confidence_score_count[28d])) * 100`

**Target**: > 80%

**Measurement Window**: 28-day rolling window

**Alerting**:
- **Warning**: High confidence rate < 80% for 1 hour
- **Critical**: High confidence rate < 70% for 30 minutes

**Rationale**: Low confidence predictions indicate potential model drift, data quality issues, or distribution shift. Monitoring this helps detect degradation early.

---

## Error Budget Policy

### Error Budget Remaining

**Formula**: `(1 - (actual_availability / target_availability)) * measurement_window`

**Example**: For 99.5% target over 28 days:
- Error budget = 0.5% of 28 days = ~3.6 hours
- If actual availability is 99.7%, budget remaining = 1.44 hours
- If actual availability is 99.3%, budget exceeded by 1.44 hours

### Policy Actions

| Budget Remaining | Action |
|------------------|--------|
| > 75% | Business as usual - Continue feature development |
| 50-75% | Caution - Review recent changes, increase monitoring |
| 25-50% | Slow down - Pause non-critical deployments, focus on reliability |
| < 25% | Freeze - Stop all feature deployments, focus only on reliability improvements |
| Exhausted | Incident - Declare incident, all hands on deck for recovery |

### Budget Burn Rate Alerts

**1-hour burn rate**: If we continue at current error rate, how much budget consumed in 1 hour?

**Alert Thresholds**:
- 🟡 Warning: 2x normal burn rate for 15 minutes
- 🔴 Critical: 5x normal burn rate for 5 minutes

---

## Monitoring and Dashboards

### Primary Dashboard

**Grafana Dashboard**: `inference-gateway-slo-overview`

**Panels**:
1. SLO Compliance Status (current vs target)
2. Error Budget Remaining (gauge + timeseries)
3. Availability (28-day rolling)
4. P99 Latency (timeseries)
5. Error Rate (timeseries)
6. Throughput (req/s)
7. ML Metrics (inference latency, confidence distribution)

### Alerts

All SLO alerts route to:
- **Warning**: #ml-platform-alerts Slack channel
- **Critical**: PagerDuty → On-call engineer

---

## Review and Iteration

### Review Schedule

- **Weekly**: Error budget status review in team sync
- **Monthly**: SLO compliance report to stakeholders
- **Quarterly**: SLO definition review and adjustment

### Adjustment Triggers

Re-evaluate SLOs if:
- Consistent overperformance (> 99.9% for 3 months)
- Consistent underperformance (< 99% for 2 months)
- Product requirements change
- User feedback indicates unmet expectations
- Business priorities shift

---

## References

- [Google SRE Book - SLIs, SLOs, SLAs](https://sre.google/sre-book/service-level-objectives/)
- [Prometheus Queries for SLO Monitoring](https://prometheus.io/docs/prometheus/latest/querying/examples/)
- Internal: [ML Platform SLO Standards](https://wiki.internal/ml-platform-slos)
```

**✅ Checkpoint:** SLO document is created and accessible.

---

## Part 9: Create Observability Readiness Assessment

Create `docs/observability-readiness.md`:

```markdown
# Observability Readiness Assessment

**Service**: inference-gateway
**Assessment Date**: 2025-10-23
**Assessor**: Junior AI Infrastructure Engineer
**Status**: ✅ Ready for Production Monitoring Integration

---

## Executive Summary

The `inference-gateway` service has achieved **comprehensive observability coverage** across metrics, logs, and traces. All critical signals are instrumented and ready for integration with the broader monitoring stack (Prometheus, Grafana, Loki, Jaeger).

**Overall Readiness**: 95% (19/20 criteria met)

---

## Assessment Criteria

### 1. Metrics (Prometheus)

| Criterion | Status | Notes |
|-----------|--------|-------|
| ✅ Service exposes `/metrics` endpoint | Complete | Prometheus exposition format |
| ✅ Four Golden Signals instrumented | Complete | Latency, Traffic, Errors, Saturation |
| ✅ HTTP request metrics | Complete | Counter + histogram by method, endpoint, status |
| ✅ Application-specific metrics | Complete | Inference latency, confidence, predictions |
| ✅ Resource usage metrics | Complete | Model memory, queue depth |
| ✅ Histogram buckets appropriate | Complete | Aligned with SLO targets |
| ✅ Cardinality control | Complete | Limited label values, no unbounded dimensions |
| ✅ Metric naming conventions | Complete | Follows Prometheus best practices |

**Metrics Coverage**: 100% (8/8)

**Available Metrics**:
- `http_requests_total`
- `http_request_duration_seconds`
- `http_errors_total`
- `inference_requests_total`
- `inference_duration_seconds`
- `inference_confidence_score`
- `model_predictions_total`
- `inference_queue_depth`
- `model_memory_bytes`

---

### 2. Logging (Structured JSON)

| Criterion | Status | Notes |
|-----------|--------|-------|
| ✅ Structured JSON logging | Complete | All logs output as JSON |
| ✅ Consistent log schema | Complete | Timestamp, level, event, service, trace_id |
| ✅ Trace context in logs | Complete | trace_id and span_id automatically injected |
| ✅ Service metadata | Complete | Service name, version, environment |
| ✅ Request correlation | Complete | Request ID and trace ID for correlation |
| ✅ Appropriate log levels | Complete | DEBUG, INFO, WARNING, ERROR used correctly |
| ⚠️ Log aggregation integration | Pending | Loki/Elasticsearch integration in Exercise 04 |
| ✅ PII/sensitive data redaction | Complete | No credentials or PII in logs |

**Logging Coverage**: 87.5% (7/8) - Aggregation pending

**Sample Log Entry**:
```json
{
  "event": "inference_completed",
  "timestamp": "2025-10-23T10:15:30.123456Z",
  "level": "info",
  "service": "inference-gateway",
  "version": "1.0.0",
  "environment": "development",
  "trace_id": "5f3a2b1c0d9e8f7a6b5c4d3e2f1a0b9c",
  "span_id": "1a2b3c4d5e6f7a8b",
  "model_name": "resnet50",
  "top_prediction": "golden_retriever",
  "confidence": 0.9876,
  "inference_duration_ms": 145.67
}
```

---

### 3. Tracing (OpenTelemetry)

| Criterion | Status | Notes |
|-----------|--------|-------|
| ✅ OpenTelemetry SDK configured | Complete | OTLP exporter to collector |
| ✅ Automatic HTTP instrumentation | Complete | FastAPI auto-instrumentation |
| ✅ Custom span creation | Complete | Manual spans for preprocessing, inference, postprocessing |
| ✅ Span attributes | Complete | Model name, latency, file size |
| ✅ Trace context propagation | Complete | Trace ID propagates to logs |
| ✅ Trace sampling | Complete | Default sampling (100% for dev) |
| ✅ OTLP collector integration | Complete | Exports to Jaeger via collector |

**Tracing Coverage**: 100% (7/7)

**Instrumented Spans**:
- `predict_endpoint` - Overall request span
- `load_model` - Model loading
- `preprocess_image` - Image preprocessing
- `run_inference` - Model inference execution
- `inference_pipeline` - Full inference flow

---

### 4. Health Checks

| Criterion | Status | Notes |
|-----------|--------|-------|
| ✅ Liveness probe endpoint | Complete | GET /healthz |
| ✅ Readiness probe endpoint | Complete | GET /readyz (checks model loaded) |
| ✅ Startup probe (if needed) | N/A | Not needed for this service |

**Health Check Coverage**: 100% (2/2)

---

### 5. SLO Definition

| Criterion | Status | Notes |
|-----------|--------|-------|
| ✅ SLIs defined | Complete | Availability, latency, error rate, throughput |
| ✅ SLOs documented | Complete | See docs/slo.md |
| ✅ Error budgets calculated | Complete | 0.5% downtime = 3.6 hours/month |
| ✅ Alerting rules defined | Complete | Warning and critical thresholds |

**SLO Coverage**: 100% (4/4)

---

## Readiness Summary

| Category | Criteria Met | Percentage | Status |
|----------|--------------|------------|--------|
| Metrics | 8/8 | 100% | ✅ Ready |
| Logging | 7/8 | 87.5% | ⚠️ Pending aggregation |
| Tracing | 7/7 | 100% | ✅ Ready |
| Health Checks | 2/2 | 100% | ✅ Ready |
| SLOs | 4/4 | 100% | ✅ Ready |
| **Overall** | **28/29** | **96.6%** | ✅ **Production Ready** |

---

## Gap Analysis

### 1. Log Aggregation Integration (Exercise 04)

**Status**: ⚠️ Pending
**Priority**: High
**Plan**: Integrate with Loki/Elasticsearch in Exercise 04 (Logging Pipeline)
**Timeline**: Next exercise

**Actions**:
- [ ] Configure Loki as log aggregation backend
- [ ] Set up log shipping (Promtail or Fluent Bit)
- [ ] Create retention policies
- [ ] Build log exploration dashboards in Grafana

---

## Production Deployment Checklist

Before deploying to production:

- [ ] Configure production OTLP collector endpoint
- [ ] Set up Prometheus scrape targets
- [ ] Create Grafana dashboards for SLO monitoring
- [ ] Configure alerting rules in Prometheus/Alertmanager
- [ ] Set up PagerDuty integration
- [ ] Configure log retention policies
- [ ] Review and adjust trace sampling rate (100% → 1-10%)
- [ ] Load test with realistic traffic patterns
- [ ] Validate SLO queries return expected results
- [ ] Document runbooks for common alerts

---

## Recommendations

### Immediate

1. **Load Testing**: Run locust load test to validate SLO targets under realistic traffic
2. **Dashboard Creation**: Build Grafana dashboard based on SLO definitions
3. **Alert Tuning**: Deploy alerting rules and tune thresholds to reduce noise

### Short-Term (Next Sprint)

1. **Log Aggregation**: Complete Loki integration (Exercise 04)
2. **Distributed Tracing**: Instrument downstream dependencies (if any)
3. **Cost Optimization**: Review trace sampling rate for production

### Long-Term (Next Quarter)

1. **Anomaly Detection**: Implement ML-based anomaly detection on metrics
2. **Continuous Profiling**: Add CPU/memory profiling for performance optimization
3. **Chaos Engineering**: Inject faults to validate observability during incidents

---

## References

- [OpenTelemetry Best Practices](https://opentelemetry.io/docs/concepts/signals/)
- [Prometheus Metric Types](https://prometheus.io/docs/concepts/metric_types/)
- [Structured Logging with structlog](https://www.structlog.org/en/stable/)
- Internal: [ML Platform Observability Standards](https://wiki.internal/observability)

---

**Assessment Complete**: ✅
**Next Review**: After Exercise 02 (Prometheus Stack)
```

**✅ Checkpoint:** Observability readiness document is complete.

---

## Part 10: Testing and Validation

### Step 10.1: Create Test Script

Create `scripts/load_test.sh`:

```bash
#!/bin/bash
# scripts/load_test.sh
# Simple load test script using curl

set -e

SERVICE_URL="http://localhost:8000"
IMAGE_FILE="sample_image.jpg"  # You need to provide a sample image

echo "=== Load Test: Inference Gateway ==="
echo "Service: $SERVICE_URL"
echo "Requests: 50"
echo ""

# Download a sample image if not exists
if [ ! -f "$IMAGE_FILE" ]; then
    echo "Downloading sample image..."
    curl -o "$IMAGE_FILE" "https://upload.wikimedia.org/wikipedia/commons/3/3a/Cat03.jpg"
fi

echo "Running 50 requests..."

for i in {1..50}; do
    echo -n "Request $i/50... "

    response=$(curl -s -w "%{http_code}" -X POST \
        -F "file=@$IMAGE_FILE" \
        "$SERVICE_URL/predict")

    status_code="${response: -3}"

    if [ "$status_code" = "200" ]; then
        echo "✓ Success"
    else
        echo "✗ Failed (HTTP $status_code)"
    fi

    sleep 0.1
done

echo ""
echo "Load test complete!"
echo "Check metrics at: $SERVICE_URL/metrics"
echo "Check traces at: http://localhost:16686 (Jaeger UI)"
```

Make executable:
```bash
chmod +x scripts/load_test.sh
```

### Step 10.2: Run Load Test

```bash
# Start services
docker-compose up -d

# Wait for services to be ready
sleep 10

# Run load test
./scripts/load_test.sh
```

### Step 10.3: Verify Observability

**1. Check Prometheus Metrics:**
```bash
curl http://localhost:8000/metrics | grep inference
```

Expected output (sample):
```
# HELP inference_requests_total Total inference requests by model, version, and status
# TYPE inference_requests_total counter
inference_requests_total{model_name="resnet50",model_version="v1.0",status="success"} 50.0

# HELP inference_duration_seconds Model inference duration in seconds
# TYPE inference_duration_seconds histogram
inference_duration_seconds_bucket{le="0.01",model_name="resnet50",model_version="v1.0"} 0.0
inference_duration_seconds_bucket{le="0.1",model_name="resnet50",model_version="v1.0"} 35.0
inference_duration_seconds_bucket{le="0.5",model_name="resnet50",model_version="v1.0"} 50.0
inference_duration_seconds_count{model_name="resnet50",model_version="v1.0"} 50.0
inference_duration_seconds_sum{model_name="resnet50",model_version="v1.0"} 6.785
```

**2. Check Structured Logs:**
```bash
docker-compose logs inference-gateway | tail -20
```

Expected JSON logs with trace context.

**3. Check Traces in Jaeger:**

Open http://localhost:16686 in browser:
- Select "inference-gateway" service
- Click "Find Traces"
- Inspect individual spans

**✅ Checkpoint:** All observability signals (metrics, logs, traces) are working correctly.

---

## Part 11: Create Architecture Documentation

Create `docs/architecture.md`:

```markdown
# Inference Gateway - Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Inference Gateway                         │
│                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   FastAPI    │───▶│   Metrics    │───▶│  Prometheus  │  │
│  │  Application │    │ (prometheus  │    │              │  │
│  │              │    │  -client)    │    │              │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│         │                                                    │
│         │                                                    │
│         ▼                                                    │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   Logging    │───▶│  Trace CTX   │───▶│     Loki     │  │
│  │ (structlog)  │    │  Injection   │    │  (planned)   │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│         │                                                    │
│         │                                                    │
│         ▼                                                    │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   Tracing    │───▶│OTLP Collector│───▶│    Jaeger    │  │
│  │(OpenTelemetry)    │              │    │              │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│         │                                                    │
│         │                                                    │
│         ▼                                                    │
│  ┌──────────────┐                                           │
│  │ Model Inference                                          │
│  │  (PyTorch)   │                                           │
│  └──────────────┘                                           │
└─────────────────────────────────────────────────────────────┘
```

## Component Descriptions

### FastAPI Application (`app/main.py`)
- HTTP server for inference requests
- Middleware for metrics and tracing
- Exception handlers
- Lifespan management

### Metrics (`app/instrumentation/metrics.py`)
- Prometheus client library
- Four Golden Signals implementation
- ML-specific metrics
- Middleware for automatic tracking

### Logging (`app/instrumentation/logging.py`)
- Structured JSON logs
- Trace context injection
- Service metadata
- ISO timestamps

### Tracing (`app/instrumentation/tracing.py`)
- OpenTelemetry SDK
- FastAPI auto-instrumentation
- Manual span creation
- OTLP export

### Model Inference (`app/models/inference.py`)
- PyTorch model loading
- Preprocessing pipeline
- Inference execution
- Postprocessing
- Comprehensive instrumentation

## Data Flow

### Request Path

1. **Client** → HTTP POST /predict (image file)
2. **FastAPI** → MetricsMiddleware (start timer)
3. **FastAPI** → OpenTelemetry (create span)
4. **Route Handler** → Dependency injection (model service)
5. **Model Service** → Preprocess image (with span)
6. **Model Service** → Run inference (with span)
7. **Model Service** → Postprocess results (with span)
8. **Route Handler** → Return response
9. **MetricsMiddleware** → Record metrics
10. **OpenTelemetry** → Export trace to collector
11. **Logging** → Emit structured log with trace context

### Observability Data Flow

**Metrics**:
- Generated by prometheus-client
- Exposed at GET /metrics
- Scraped by Prometheus every 15s

**Logs**:
- Generated by structlog
- Output to stdout as JSON
- (Future) Shipped to Loki by Promtail

**Traces**:
- Generated by OpenTelemetry SDK
- Exported via OTLP HTTP to collector
- Forwarded to Jaeger for visualization

## Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| Web Framework | FastAPI | 0.104.1 |
| HTTP Server | Uvicorn | 0.24.0 |
| ML Framework | PyTorch | 2.1.1 |
| Metrics | prometheus-client | 0.19.0 |
| Logging | structlog | 23.2.0 |
| Tracing | OpenTelemetry | 1.21.0 |
| Configuration | Pydantic Settings | 2.1.0 |

## Deployment Architecture

### Development (Docker Compose)

```yaml
services:
  - inference-gateway (port 8000)
  - otel-collector (port 4318)
  - jaeger (port 16686)
  - prometheus (port 9090)
```

### Production (Kubernetes) - Planned

```
┌─────────────────────────────────────────┐
│            Ingress Controller            │
└─────────────────┬───────────────────────┘
                  │
        ┌─────────▼─────────┐
        │  Service (LB)     │
        └─────────┬─────────┘
                  │
     ┌────────────┼────────────┐
     │            │            │
┌────▼────┐  ┌────▼────┐  ┌────▼────┐
│  Pod 1  │  │  Pod 2  │  │  Pod 3  │
│ Gateway │  │ Gateway │  │ Gateway │
└─────────┘  └─────────┘  └─────────┘
     │            │            │
     └────────────┼────────────┘
                  │
     ┌────────────┼────────────┐
     │            │            │
┌────▼────┐  ┌────▼────┐  ┌────▼────┐
│Prometheus│ │   Loki  │  │ Jaeger  │
└─────────┘  └─────────┘  └─────────┘
```
```

**✅ Checkpoint:** Architecture documentation is complete.

---

## Part 12: Optional Enhancements

### Enhancement 1: Unit Tests

Create `tests/unit/test_metrics.py`:

```python
# tests/unit/test_metrics.py
"""Unit tests for metrics instrumentation."""
import pytest
from prometheus_client import REGISTRY

from app.instrumentation import metrics


def test_metrics_exist():
    """Verify all expected metrics are registered."""
    metric_names = [
        "http_requests_total",
        "inference_requests_total",
        "http_request_duration_seconds",
        "inference_duration_seconds",
        "inference_errors_total",
    ]

    for name in metric_names:
        assert name in REGISTRY._names_to_collectors, f"Metric {name} not registered"


def test_record_prediction():
    """Test recording predictions updates counters."""
    model_name = "test_model"
    predicted_class = "test_class"
    confidence = 0.95

    # Record prediction
    metrics.record_prediction(model_name, predicted_class, confidence)

    # Verify counter incremented (check via registry)
    # In real tests, use prometheus_client test utilities
    assert True  # Placeholder
```

Create `tests/unit/test_config.py`:

```python
# tests/unit/test_config.py
"""Unit tests for configuration."""
import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_settings_defaults():
    """Verify default settings load correctly."""
    settings = Settings()

    assert settings.service_name == "inference-gateway"
    assert settings.environment in ["development", "staging", "production"]
    assert settings.port >= 1024


def test_settings_validation():
    """Verify settings validation works."""
    with pytest.raises(ValidationError):
        Settings(port=99999)  # Port out of range
```

### Enhancement 2: Integration Tests

Create `tests/integration/test_api.py`:

```python
# tests/integration/test_api.py
"""Integration tests for API endpoints."""
import pytest
from httpx import AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_health_check():
    """Test health check endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/healthz")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


@pytest.mark.asyncio
async def test_readiness_check():
    """Test readiness check endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/readyz")

    # May be 503 if model not loaded, or 200 if loaded
    assert response.status_code in [200, 503]


@pytest.mark.asyncio
async def test_metrics_endpoint():
    """Test Prometheus metrics endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/metrics")

    assert response.status_code == 200
    assert "http_requests_total" in response.text
```

Run tests:
```bash
pytest tests/ -v --cov=app
```

### Enhancement 3: Locust Load Test

Create `tests/load/locustfile.py`:

```python
# tests/load/locustfile.py
"""Locust load test for inference gateway."""
from locust import HttpUser, task, between
import random


class InferenceGatewayUser(HttpUser):
    """Simulated user for load testing."""

    wait_time = between(0.5, 2)

    def on_start(self):
        """Load test image on start."""
        with open("sample_image.jpg", "rb") as f:
            self.image_bytes = f.read()

    @task(10)
    def predict(self):
        """Run prediction request."""
        files = {"file": ("test.jpg", self.image_bytes, "image/jpeg")}
        with self.client.post("/predict", files=files, catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Got status {response.status_code}")

    @task(1)
    def health_check(self):
        """Health check request."""
        self.client.get("/healthz")

    @task(1)
    def readiness_check(self):
        """Readiness check request."""
        self.client.get("/readyz")
```

Run Locust:
```bash
locust -f tests/load/locustfile.py --host=http://localhost:8000
```

Access UI at http://localhost:8089

---

## Part 13: Update README

Create final `README.md`:

```markdown
# Inference Gateway

Production-ready ML model inference service with comprehensive observability (metrics, logs, traces).

## Overview

The Inference Gateway exposes a ResNet-50 image classification model via a FastAPI HTTP API. It implements enterprise-grade observability patterns including:

- **Metrics**: Prometheus metrics (Four Golden Signals + ML-specific metrics)
- **Logging**: Structured JSON logs with trace context
- **Tracing**: OpenTelemetry distributed tracing
- **SLOs**: Defined Service Level Objectives with error budgets
- **Health Checks**: Kubernetes-compatible liveness/readiness probes

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)

### Start with Docker Compose

```bash
# Clone repository
git clone <repository-url>
cd inference-gateway

# Start all services
docker-compose up --build

# In another terminal, run load test
./scripts/load_test.sh
```

### Access Observability Stack

- **Inference API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Prometheus Metrics**: http://localhost:8000/metrics
- **Prometheus UI**: http://localhost:9090
- **Jaeger UI**: http://localhost:16686

### Local Development

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements-dev.txt

# Run application
python -m app.main

# Run tests
pytest tests/ -v

# Run with auto-reload
uvicorn app.main:app --reload
```

## API Endpoints

### Health Checks

- `GET /healthz` - Liveness probe
- `GET /readyz` - Readiness probe (checks model loaded)

### Inference

- `POST /predict` - Run image classification
  - **Request**: Multipart form with image file
  - **Response**: JSON with top-5 predictions and confidence scores

### Observability

- `GET /metrics` - Prometheus metrics endpoint
- `GET /docs` - Interactive API documentation (dev only)

## Example Request

```bash
curl -X POST http://localhost:8000/predict \
  -F "file=@sample_image.jpg"
```

Response:
```json
{
  "predictions": [
    {"class": "golden_retriever", "class_id": 207, "confidence": 0.9876},
    {"class": "labrador_retriever", "class_id": 208, "confidence": 0.0089},
    {"class": "tennis_ball", "class_id": 852, "confidence": 0.0023},
    {"class": "kite", "class_id": 131, "confidence": 0.0009},
    {"class": "lakeside", "class_id": 975, "confidence": 0.0003}
  ],
  "model_name": "resnet50",
  "model_version": "v1.0",
  "inference_duration_ms": 145.67
}
```

## Observability

### Metrics

**Four Golden Signals**:
- **Latency**: `http_request_duration_seconds`, `inference_duration_seconds`
- **Traffic**: `http_requests_total`, `inference_requests_total`
- **Errors**: `http_errors_total`, `inference_errors_total`
- **Saturation**: `inference_queue_depth`, `model_memory_bytes`

**ML-Specific**:
- `inference_confidence_score` - Model confidence distribution
- `model_predictions_total` - Predictions by class
- `inference_batch_size` - Batch size distribution

### Logs

Structured JSON logs with trace context:

```json
{
  "event": "inference_completed",
  "timestamp": "2025-10-23T10:15:30.123456Z",
  "level": "info",
  "service": "inference-gateway",
  "version": "1.0.0",
  "trace_id": "5f3a2b1c0d9e8f7a6b5c4d3e2f1a0b9c",
  "span_id": "1a2b3c4d5e6f7a8b",
  "model_name": "resnet50",
  "top_prediction": "golden_retriever",
  "confidence": 0.9876
}
```

### Traces

OpenTelemetry traces exported to Jaeger via OTLP collector. View at http://localhost:16686

## SLO Targets

- **Availability**: 99.5% (error budget: 3.6 hours/month)
- **P99 Latency**: < 300ms
- **Error Rate**: < 0.5%
- **Throughput**: Support 100 req/s sustained

See [`docs/slo.md`](docs/slo.md) for detailed SLO definitions.

## Architecture

See [`docs/architecture.md`](docs/architecture.md) for architecture overview.

## Project Structure

```
inference-gateway/
├── app/
│   ├── main.py                  # FastAPI application
│   ├── api/
│   │   ├── routes.py            # API endpoints
│   │   └── dependencies.py      # Dependency injection
│   ├── core/
│   │   ├── config.py            # Configuration
│   │   └── exceptions.py        # Custom exceptions
│   ├── instrumentation/
│   │   ├── metrics.py           # Prometheus metrics
│   │   ├── logging.py           # Structured logging
│   │   └── tracing.py           # OpenTelemetry tracing
│   └── models/
│       └── inference.py         # Model inference logic
├── docs/
│   ├── slo.md                   # SLO definitions
│   ├── architecture.md          # Architecture documentation
│   └── observability-readiness.md
├── tests/
│   ├── unit/                    # Unit tests
│   ├── integration/             # Integration tests
│   └── load/                    # Load tests (Locust)
├── config/
│   ├── prometheus.yml           # Prometheus config
│   └── otel-collector-config.yml
├── docker-compose.yml
├── Dockerfile
└── README.md
```

## Testing

```bash
# Run unit and integration tests
pytest tests/ -v --cov=app

# Run load test
./scripts/load_test.sh

# Run Locust load test
locust -f tests/load/locustfile.py --host=http://localhost:8000
```

## Configuration

Configuration via environment variables (see `.env.example`):

```bash
SERVICE_NAME=inference-gateway
SERVICE_VERSION=1.0.0
ENVIRONMENT=development
LOG_LEVEL=INFO
MODEL_NAME=resnet50
MODEL_DEVICE=cpu
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318
```

## Deployment

### Docker

```bash
docker build -t inference-gateway:latest .
docker run -p 8000:8000 inference-gateway:latest
```

### Kubernetes (planned for Module 010)

```bash
kubectl apply -f k8s/
```

## Observability Status

✅ **Production Ready**

See [`docs/observability-readiness.md`](docs/observability-readiness.md) for detailed assessment.

## License

MIT

## Contributing

See `CONTRIBUTING.md` (to be created)

## Contact

ML Platform Team - ml-platform@example.com
```

**✅ Checkpoint:** README is comprehensive and professional.

---

## Part 14: Summary and Reflection

### Summary

Congratulations! You've successfully built a production-ready inference gateway service with comprehensive observability instrumentation:

**What You Built**:
1. ✅ FastAPI inference service with ResNet-50 model
2. ✅ Prometheus metrics (Four Golden Signals + ML-specific)
3. ✅ Structured JSON logging with trace context
4. ✅ OpenTelemetry distributed tracing
5. ✅ Health check endpoints (liveness/readiness)
6. ✅ Comprehensive error handling
7. ✅ SLO definitions with error budgets
8. ✅ Observability readiness assessment
9. ✅ Docker Compose development environment
10. ✅ Documentation (SLOs, architecture, README)

**Skills Gained**:
- Designing SLIs and SLOs for microservices
- Implementing the Four Golden Signals
- Instrumenting ML models with observability
- Structured logging best practices
- OpenTelemetry tracing patterns
- Prometheus metric design
- Cardinality control for metrics
- Health check patterns for Kubernetes
- Production-ready error handling

### Deliverables Checklist

- ✅ Instrumented FastAPI service with metrics/logging/tracing
- ✅ `docs/slo.md` with comprehensive SLO definitions
- ✅ `docs/observability-readiness.md` with readiness assessment
- ✅ `docs/architecture.md` with system architecture
- ✅ Updated `README.md` documenting observability setup
- ✅ Docker Compose stack with OTLP collector, Jaeger, Prometheus
- ✅ Load test script demonstrating functionality
- ✅ All code properly structured and documented

---

## Reflection Questions

1. **Which SLI/SLOs were hardest to define and why?**
   - Consider: ML-specific SLIs (confidence coverage), measurement windows, error budgets
   - Reflect on trade-offs between strictness and achievability

2. **How would you automate the observability readiness assessment for new services?**
   - Think about: Automated checks, CI/CD integration, standardization
   - Consider: Checklist automation, policy-as-code, service catalogs

3. **What additional signals (metrics/logs) would you capture if this service handled real customer traffic?**
   - Consider: User-facing metrics, business metrics, cost tracking
   - Think about: Privacy implications, data retention, compliance

4. **How does structured logging improve cross-team collaboration during incidents?**
   - Reflect on: Correlation across services, queryability, standardization
   - Consider: On-call experience, mean time to recovery (MTTR)

5. **What are the risks of high-cardinality metrics, and how did you mitigate them?**
   - Consider: Label design, aggregation strategies, sampling
   - Think about: Cost implications, query performance, storage

6. **How would you adjust trace sampling for production to balance cost and visibility?**
   - Consider: Head-based vs tail-based sampling, error sampling, importance scoring
   - Think about: Cost-benefit analysis, retention policies

---

## Next Steps

**In Exercise 02** (Prometheus Stack), you will:
- Set up a complete Prometheus monitoring stack
- Create recording and alerting rules
- Build a comprehensive service discovery setup
- Implement alert manager with routing and silencing
- Create synthetic monitors for availability testing

**Continue to:** [Exercise 02: Prometheus Monitoring Stack](exercise-02-prometheus-stack.md)

---

**Exercise 01 Complete!** 🎉

You've built a solid observability foundation that will serve as the base for the rest of Module 009.
