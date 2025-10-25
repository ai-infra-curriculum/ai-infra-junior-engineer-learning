# Exercise 06: Building a Production-Ready ML API

## Overview

This comprehensive exercise guides you through building a complete production-ready ML API with FastAPI, implementing proper authentication, rate limiting, caching, monitoring, error handling, and deployment. You'll create an end-to-end inference API that follows industry best practices.

## Learning Objectives

By completing this exercise, you will:
- Build a complete ML inference API with FastAPI
- Implement JWT authentication and API key validation
- Add rate limiting to prevent abuse
- Implement caching for frequently requested predictions
- Set up comprehensive monitoring and logging
- Handle errors gracefully with proper status codes
- Create API documentation with OpenAPI/Swagger
- Deploy the API with proper CI/CD
- Load test and optimize performance

## Prerequisites

- Completed exercises 01-05 in this module
- All API lectures (REST, FastAPI, Authentication, Advanced Patterns)
- Python FastAPI knowledge
- Basic understanding of ML inference

## Time Required

- Estimated: 150-180 minutes
- Difficulty: Advanced

---

## Part 1: Project Setup

### Task 1.1: Create Project Structure

```bash
mkdir ml-inference-api
cd ml-inference-api

# Create directory structure
mkdir -p app/{api,core,models,schemas,services}
mkdir -p tests
mkdir -p scripts
mkdir -p deployment/{docker,kubernetes}

# Create files
touch app/__init__.py
touch app/main.py
touch app/api/__init__.py
touch app/core/{config.py,security.py,logging_config.py}
touch app/models/__init__.py
touch app/schemas/{request.py,response.py}
touch app/services/{inference.py,cache.py}
touch requirements.txt
touch .env.example
touch Dockerfile
touch docker-compose.yml
```

### Task 1.2: Install Dependencies

**requirements.txt:**
```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
pydantic-settings==2.1.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
redis==5.0.1
prometheus-client==0.19.0
slowapi==0.1.9
onnxruntime==1.16.3
numpy==1.24.3
httpx==0.25.2
pytest==7.4.3
pytest-asyncio==0.21.1
```

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

---

## Part 2: Configuration and Security

### Task 2.1: Environment Configuration

**app/core/config.py:**
```python
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # App settings
    APP_NAME: str = "ML Inference API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    API_KEY_HEADER: str = "X-API-Key"

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    CACHE_TTL: int = 3600  # 1 hour

    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000

    # Model
    MODEL_PATH: str = "models/model.onnx"

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
```

**.env.example:**
```bash
SECRET_KEY=your-secret-key-change-this-in-production
REDIS_HOST=localhost
REDIS_PORT=6379
MODEL_PATH=models/model.onnx
DEBUG=False
```

### Task 2.2: Security Implementation

**app/core/security.py:**
```python
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader, HTTPBearer, HTTPAuthorizationCredentials
from app.core.config import get_settings

settings = get_settings()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# API Key authentication
api_key_header = APIKeyHeader(name=settings.API_KEY_HEADER, auto_error=False)

# JWT Bearer authentication
security = HTTPBearer()

# Valid API keys (in production, store in database)
VALID_API_KEYS = {
    "dev-key-123": {"user": "developer", "tier": "premium"},
    "test-key-456": {"user": "tester", "tier": "free"}
}

def verify_api_key(api_key: str = Security(api_key_header)):
    """Validate API key"""
    if not api_key or api_key not in VALID_API_KEYS:
        raise HTTPException(
            status_code=403,
            detail="Invalid or missing API key"
        )
    return VALID_API_KEYS[api_key]

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    """Verify JWT token"""
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials"
        )
```

---

## Part 3: Core Services

### Task 3.1: Inference Service

**app/services/inference.py:**
```python
import onnxruntime as ort
import numpy as np
from typing import List
import logging
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class InferenceService:
    def __init__(self):
        self.session = None
        self.model_loaded = False

    def load_model(self):
        """Load ONNX model"""
        try:
            self.session = ort.InferenceSession(settings.MODEL_PATH)
            self.model_loaded = True
            logger.info(f"Model loaded from {settings.MODEL_PATH}")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise

    def predict(self, features: List[float]) -> float:
        """Run inference"""
        if not self.model_loaded:
            raise RuntimeError("Model not loaded")

        try:
            # Prepare input
            input_data = np.array([features], dtype=np.float32)

            # Run inference
            outputs = self.session.run(None, {"input": input_data})
            prediction = float(outputs[0][0])

            return prediction

        except Exception as e:
            logger.error(f"Inference error: {e}")
            raise

# Global inference service
inference_service = InferenceService()
```

### Task 3.2: Caching Service

**app/services/cache.py:**
```python
import redis
import json
import hashlib
from typing import Optional
from app.core.config import get_settings

settings = get_settings()

class CacheService:
    def __init__(self):
        self.redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            decode_responses=True
        )

    def _generate_key(self, features: list) -> str:
        """Generate cache key from features"""
        features_str = json.dumps(features, sort_keys=True)
        return f"prediction:{hashlib.md5(features_str.encode()).hexdigest()}"

    def get(self, features: list) -> Optional[float]:
        """Get cached prediction"""
        key = self._generate_key(features)
        cached = self.redis_client.get(key)
        return float(cached) if cached else None

    def set(self, features: list, prediction: float):
        """Cache prediction"""
        key = self._generate_key(features)
        self.redis_client.setex(key, settings.CACHE_TTL, str(prediction))

    def clear(self):
        """Clear all cached predictions"""
        keys = self.redis_client.keys("prediction:*")
        if keys:
            self.redis_client.delete(*keys)

cache_service = CacheService()
```

---

## Part 4: API Schemas

### Task 4.1: Request/Response Models

**app/schemas/request.py:**
```python
from pydantic import BaseModel, Field
from typing import List

class PredictionRequest(BaseModel):
    features: List[float] = Field(
        ...,
        description="Input features for prediction",
        min_items=1,
        max_items=100
    )

    class Config:
        json_schema_extra = {
            "example": {
                "features": [1.0, 2.0, 3.0, 4.0, 5.0]
            }
        }

class BatchPredictionRequest(BaseModel):
    requests: List[PredictionRequest] = Field(
        ...,
        max_items=100
    )
```

**app/schemas/response.py:**
```python
from pydantic import BaseModel
from typing import List, Optional

class PredictionResponse(BaseModel):
    prediction: float
    latency_ms: float
    cached: bool = False
    model_version: str = "1.0.0"

class BatchPredictionResponse(BaseModel):
    predictions: List[PredictionResponse]
    total_latency_ms: float

class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    version: str

class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
```

---

## Part 5: API Endpoints

### Task 5.1: Main Application

**app/main.py:**
```python
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from prometheus_client import Counter, Histogram, generate_latest
import time
import logging

from app.core.config import get_settings
from app.core.security import verify_api_key
from app.services.inference import inference_service
from app.services.cache import cache_service
from app.schemas.request import PredictionRequest, BatchPredictionRequest
from app.schemas.response import (
    PredictionResponse,
    BatchPredictionResponse,
    HealthResponse,
    ErrorResponse
)

# Initialize settings
settings = get_settings()

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Production ML Inference API",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add rate limiter to app
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prometheus metrics
PREDICTION_COUNT = Counter('predictions_total', 'Total predictions')
PREDICTION_LATENCY = Histogram('prediction_latency_seconds', 'Prediction latency')
CACHE_HITS = Counter('cache_hits_total', 'Total cache hits')
CACHE_MISSES = Counter('cache_misses_total', 'Total cache misses')
ERROR_COUNT = Counter('errors_total', 'Total errors', ['error_type'])

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_event():
    """Load model on startup"""
    logger.info("Starting ML Inference API...")
    inference_service.load_model()
    logger.info("Model loaded successfully")

@app.get("/", tags=["Root"])
async def root():
    """API root endpoint"""
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "endpoints": {
            "/health": "Health check",
            "/predict": "Single prediction (requires API key)",
            "/batch-predict": "Batch predictions (requires API key)",
            "/metrics": "Prometheus metrics",
            "/docs": "API documentation"
        }
    }

@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        model_loaded=inference_service.model_loaded,
        version=settings.APP_VERSION
    )

@app.post(
    "/predict",
    response_model=PredictionResponse,
    tags=["Predictions"],
    dependencies=[Depends(verify_api_key)]
)
@limiter.limit(f"{settings.RATE_LIMIT_PER_MINUTE}/minute")
async def predict(request: Request, pred_request: PredictionRequest):
    """Make a prediction"""
    start_time = time.time()

    try:
        # Check cache first
        cached_result = cache_service.get(pred_request.features)

        if cached_result is not None:
            CACHE_HITS.inc()
            latency = (time.time() - start_time) * 1000

            return PredictionResponse(
                prediction=cached_result,
                latency_ms=latency,
                cached=True
            )

        # Cache miss - run inference
        CACHE_MISSES.inc()
        prediction = inference_service.predict(pred_request.features)

        # Cache result
        cache_service.set(pred_request.features, prediction)

        # Metrics
        latency = (time.time() - start_time) * 1000
        PREDICTION_COUNT.inc()
        PREDICTION_LATENCY.observe(time.time() - start_time)

        return PredictionResponse(
            prediction=prediction,
            latency_ms=latency,
            cached=False
        )

    except Exception as e:
        ERROR_COUNT.labels(error_type=type(e).__name__).inc()
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post(
    "/batch-predict",
    response_model=BatchPredictionResponse,
    tags=["Predictions"],
    dependencies=[Depends(verify_api_key)]
)
@limiter.limit(f"{settings.RATE_LIMIT_PER_MINUTE}/minute")
async def batch_predict(request: Request, batch_request: BatchPredictionRequest):
    """Make batch predictions"""
    start_time = time.time()

    try:
        predictions = []

        for pred_req in batch_request.requests:
            pred_start = time.time()
            prediction = inference_service.predict(pred_req.features)
            pred_latency = (time.time() - pred_start) * 1000

            predictions.append(PredictionResponse(
                prediction=prediction,
                latency_ms=pred_latency,
                cached=False
            ))

            PREDICTION_COUNT.inc()

        total_latency = (time.time() - start_time) * 1000

        return BatchPredictionResponse(
            predictions=predictions,
            total_latency_ms=total_latency
        )

    except Exception as e:
        ERROR_COUNT.labels(error_type=type(e).__name__).inc()
        logger.error(f"Batch prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics", tags=["Monitoring"])
async def metrics():
    """Prometheus metrics endpoint"""
    return JSONResponse(content=generate_latest().decode(), media_type="text/plain")

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    ERROR_COUNT.labels(error_type="unhandled").inc()
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

---

## Part 6: Testing

### Task 6.1: Unit Tests

**tests/test_api.py:**
```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "service" in response.json()

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_predict_no_api_key():
    response = client.post(
        "/predict",
        json={"features": [1.0, 2.0, 3.0]}
    )
    assert response.status_code == 403

def test_predict_with_api_key():
    response = client.post(
        "/predict",
        json={"features": [1.0, 2.0, 3.0]},
        headers={"X-API-Key": "dev-key-123"}
    )
    assert response.status_code == 200
    assert "prediction" in response.json()
    assert "latency_ms" in response.json()

def test_batch_predict():
    response = client.post(
        "/batch-predict",
        json={
            "requests": [
                {"features": [1.0, 2.0]},
                {"features": [3.0, 4.0]}
            ]
        },
        headers={"X-API-Key": "dev-key-123"}
    )
    assert response.status_code == 200
    assert len(response.json()["predictions"]) == 2

# Run tests
# pytest tests/test_api.py -v
```

---

## Part 7: Deployment

### Task 7.1: Docker Deployment

**Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY app/ ./app/
COPY models/ ./models/

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s \
    CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - REDIS_HOST=redis
      - SECRET_KEY=dev-secret-key-change-in-prod
    depends_on:
      - redis
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    restart: unless-stopped

  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    restart: unless-stopped
```

---

## Deliverables

Submit the following:

1. **Complete API Code**:
   - FastAPI application with all endpoints
   - Authentication and authorization
   - Rate limiting and caching
   - Error handling

2. **Tests**:
   - Unit tests for all endpoints
   - Integration tests
   - Performance tests

3. **Documentation**:
   - API documentation (auto-generated with FastAPI)
   - Deployment guide
   - Usage examples

4. **Evidence**:
   - Screenshots of Swagger UI
   - Load test results
   - Prometheus metrics dashboard

---

## Challenge Questions

1. **Security**: How would you prevent API key leakage in logs?

2. **Scaling**: How do you handle 100,000 requests/second?

3. **Monitoring**: What alerts would you set up for production?

4. **Versioning**: How do you deploy API v2 without breaking v1 clients?

5. **Cost**: How do you optimize costs for an API with 1B requests/month?

---

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [API Security Best Practices](https://owasp.org/www-project-api-security/)
- [Rate Limiting Patterns](https://cloud.google.com/architecture/rate-limiting-strategies)
- [Prometheus Metrics](https://prometheus.io/docs/practices/naming/)

---

**Congratulations!** You've built a production-ready ML API with authentication, caching, monitoring, and proper error handling.
