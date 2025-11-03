# Exercise 07: Flask to FastAPI Migration

## Overview

**Estimated Time**: 3-4 hours
**Difficulty**: Intermediate
**Prerequisites**:
- Completed Exercises 01-06
- Lecture 02: FastAPI Fundamentals
- Understanding of Flask framework basics
- Knowledge of async/await concepts

## Learning Objectives

By completing this exercise, you will:
1. Understand architectural differences between Flask and FastAPI
2. Migrate an existing Flask ML serving API to FastAPI
3. Preserve functionality while modernizing the codebase
4. Implement Pydantic models for request/response validation
5. Leverage FastAPI's automatic OpenAPI documentation
6. Compare performance characteristics between frameworks
7. Apply best practices for async API development

## Scenario

Your ML infrastructure team has been running a Flask-based model serving API for 2 years. The API works but has several pain points:

**Current Issues**:
- Manual request validation with lots of if/else checks
- No automatic API documentation
- Synchronous request handling limits throughput
- Difficult to add new endpoints without breaking changes
- Type hints exist but aren't enforced at runtime

**Goals**:
- Migrate to FastAPI for better performance
- Add automatic validation with Pydantic
- Implement async endpoints where beneficial
- Generate automatic OpenAPI/Swagger docs
- Maintain backward compatibility during migration

---

## Part 1: Understanding the Flask Application

### Task 1.1: Analyze Existing Flask API

Here's the existing Flask ML serving API:

**File**: `flask_app.py`

```python
"""Flask-based ML model serving API."""

from flask import Flask, request, jsonify
from functools import wraps
import time
import jwt
import pickle
import numpy as np
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'

# Load ML model
with open('model.pkl', 'rb') as f:
    model = pickle.load(f)

# Simple in-memory cache
prediction_cache = {}

# Authentication decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')

        if not token:
            return jsonify({'error': 'Token is missing'}), 401

        try:
            token = token.replace('Bearer ', '')
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        except:
            return jsonify({'error': 'Token is invalid'}), 401

        return f(*args, **kwargs)

    return decorated

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/predict', methods=['POST'])
@token_required
def predict():
    """Make predictions on input features."""
    try:
        # Get request data
        data = request.get_json()

        # Validate input
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        if 'features' not in data:
            return jsonify({'error': 'Missing features field'}), 400

        features = data['features']

        if not isinstance(features, list):
            return jsonify({'error': 'Features must be a list'}), 400

        if len(features) != 10:
            return jsonify({'error': 'Expected 10 features'}), 400

        # Check cache
        feature_key = str(features)
        if feature_key in prediction_cache:
            return jsonify({
                'prediction': prediction_cache[feature_key],
                'cached': True
            })

        # Make prediction
        features_array = np.array([features])
        prediction = model.predict(features_array)[0]

        # Cache result
        prediction_cache[feature_key] = float(prediction)

        return jsonify({
            'prediction': float(prediction),
            'cached': False,
            'model_version': '1.0'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/batch-predict', methods=['POST'])
@token_required
def batch_predict():
    """Make predictions on multiple samples."""
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': 'No data provided'}), 400

        if 'samples' not in data:
            return jsonify({'error': 'Missing samples field'}), 400

        samples = data['samples']

        if not isinstance(samples, list):
            return jsonify({'error': 'Samples must be a list'}), 400

        if len(samples) > 100:
            return jsonify({'error': 'Maximum 100 samples allowed'}), 400

        # Validate each sample
        for i, sample in enumerate(samples):
            if not isinstance(sample, list):
                return jsonify({'error': f'Sample {i} must be a list'}), 400
            if len(sample) != 10:
                return jsonify({'error': f'Sample {i} must have 10 features'}), 400

        # Make predictions
        features_array = np.array(samples)
        predictions = model.predict(features_array)

        return jsonify({
            'predictions': [float(p) for p in predictions],
            'count': len(predictions),
            'model_version': '1.0'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/model-info', methods=['GET'])
def model_info():
    """Get information about the model."""
    return jsonify({
        'version': '1.0',
        'input_features': 10,
        'model_type': 'random_forest',
        'training_date': '2024-01-15'
    })

@app.route('/login', methods=['POST'])
def login():
    """Generate authentication token."""
    data = request.get_json()

    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'error': 'Missing credentials'}), 400

    # Simplified auth (in production, validate against database)
    if data['username'] == 'admin' and data['password'] == 'password':
        token = jwt.encode({
            'user': data['username'],
            'exp': datetime.utcnow() + timedelta(hours=24)
        }, app.config['SECRET_KEY'], algorithm="HS256")

        return jsonify({'token': token})

    return jsonify({'error': 'Invalid credentials'}), 401

if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

**TODO**: Review this code and identify:

1. **Manual validation patterns** (list 5 examples):
   ```
   1. Checking if data exists: if not data
   2.
   3.
   4.
   5.
   ```

2. **Synchronous operations** that could benefit from async:
   ```
   1. Model prediction (I/O bound for large models)
   2.
   3.
   ```

3. **Missing features** that FastAPI would provide:
   ```
   1. Automatic API documentation
   2.
   3.
   ```

---

## Part 2: Implementing FastAPI Version

### Task 2.1: Create Pydantic Models

**File**: `models.py`

```python
"""Pydantic models for request/response validation."""

from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime

class HealthResponse(BaseModel):
    """Health check response model."""
    status: str
    timestamp: datetime

class PredictionRequest(BaseModel):
    """Single prediction request model."""
    features: List[float] = Field(
        ...,
        min_items=10,
        max_items=10,
        description="List of 10 numerical features"
    )

    @validator('features')
    def validate_features(cls, v):
        """Ensure all features are valid numbers."""
        for i, feature in enumerate(v):
            if not isinstance(feature, (int, float)):
                raise ValueError(f'Feature {i} must be a number')
            if feature < -1000 or feature > 1000:
                raise ValueError(f'Feature {i} out of valid range [-1000, 1000]')
        return v

    class Config:
        schema_extra = {
            "example": {
                "features": [1.2, 3.4, 5.6, 7.8, 9.0, 2.3, 4.5, 6.7, 8.9, 0.1]
            }
        }

class PredictionResponse(BaseModel):
    """Single prediction response model."""
    prediction: float
    cached: bool = False
    model_version: str

class BatchPredictionRequest(BaseModel):
    """Batch prediction request model."""
    samples: List[List[float]] = Field(
        ...,
        max_items=100,
        description="List of feature vectors (max 100 samples)"
    )

    # TODO: Add validator to ensure each sample has 10 features

    class Config:
        schema_extra = {
            "example": {
                "samples": [
                    [1.2, 3.4, 5.6, 7.8, 9.0, 2.3, 4.5, 6.7, 8.9, 0.1],
                    [2.1, 4.3, 6.5, 8.7, 0.9, 3.2, 5.4, 7.6, 9.8, 1.0]
                ]
            }
        }

class BatchPredictionResponse(BaseModel):
    """Batch prediction response model."""
    predictions: List[float]
    count: int
    model_version: str

class ModelInfo(BaseModel):
    """Model information response."""
    version: str
    input_features: int
    model_type: str
    training_date: str

class LoginRequest(BaseModel):
    """Login credentials."""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)

class LoginResponse(BaseModel):
    """Login response with token."""
    token: str

class ErrorResponse(BaseModel):
    """Standard error response."""
    error: str
    detail: Optional[str] = None
```

**TODO**: Complete the batch prediction validator:

```python
@validator('samples')
def validate_samples(cls, v):
    """Validate each sample has correct number of features."""
    # TODO: Implement validation
    # Hint: Check that each sample is a list of 10 floats
    pass
```

### Task 2.2: Migrate to FastAPI

**File**: `fastapi_app.py`

```python
"""FastAPI-based ML model serving API."""

from fastapi import FastAPI, Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import pickle
import numpy as np
import jwt
from datetime import datetime, timedelta
from models import (
    HealthResponse,
    PredictionRequest,
    PredictionResponse,
    BatchPredictionRequest,
    BatchPredictionResponse,
    ModelInfo,
    LoginRequest,
    LoginResponse,
    ErrorResponse
)

app = FastAPI(
    title="ML Model Serving API",
    description="FastAPI-based machine learning model serving",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuration
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"

# Security
security = HTTPBearer()

# Load ML model
with open('model.pkl', 'rb') as f:
    model = pickle.load(f)

# In-memory cache
prediction_cache = {}

# Dependency: Verify JWT token
async def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """Verify and decode JWT token."""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.

    Returns the current status and timestamp.
    """
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow()
    )

@app.post(
    "/predict",
    response_model=PredictionResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"}
    }
)
async def predict(
    request: PredictionRequest,
    user: dict = Depends(verify_token)
):
    """
    Make a prediction on input features.

    - **features**: List of 10 numerical features

    Returns prediction value and whether result was cached.
    """
    try:
        # Check cache
        feature_key = str(request.features)
        if feature_key in prediction_cache:
            return PredictionResponse(
                prediction=prediction_cache[feature_key],
                cached=True,
                model_version="1.0"
            )

        # Make prediction
        features_array = np.array([request.features])
        prediction = model.predict(features_array)[0]

        # Cache result
        prediction_cache[feature_key] = float(prediction)

        return PredictionResponse(
            prediction=float(prediction),
            cached=False,
            model_version="1.0"
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.post(
    "/batch-predict",
    response_model=BatchPredictionResponse,
    responses={
        401: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
async def batch_predict(
    request: BatchPredictionRequest,
    user: dict = Depends(verify_token)
):
    """
    Make predictions on multiple samples.

    - **samples**: List of feature vectors (max 100)

    Returns list of predictions.
    """
    try:
        # Make predictions
        features_array = np.array(request.samples)
        predictions = model.predict(features_array)

        return BatchPredictionResponse(
            predictions=[float(p) for p in predictions],
            count=len(predictions),
            model_version="1.0"
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.get("/model-info", response_model=ModelInfo)
async def model_info():
    """
    Get information about the deployed model.

    Returns model version, type, and metadata.
    """
    return ModelInfo(
        version="1.0",
        input_features=10,
        model_type="random_forest",
        training_date="2024-01-15"
    )

@app.post("/login", response_model=LoginResponse)
async def login(credentials: LoginRequest):
    """
    Authenticate and receive JWT token.

    - **username**: User username
    - **password**: User password

    Returns JWT token valid for 24 hours.
    """
    # Simplified auth (in production, validate against database)
    if credentials.username == "admin" and credentials.password == "password":
        token = jwt.encode(
            {
                "user": credentials.username,
                "exp": datetime.utcnow() + timedelta(hours=24)
            },
            SECRET_KEY,
            algorithm=ALGORITHM
        )

        return LoginResponse(token=token)

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

**TODO**: Compare the two implementations and document differences:

| Aspect | Flask | FastAPI | Winner |
|--------|-------|---------|--------|
| Lines of code | ~150 | ~140 | FastAPI |
| Request validation | Manual if/else | Pydantic automatic | ? |
| Documentation | Manual/Swagger extension | Automatic OpenAPI | ? |
| Type safety | Optional hints | Enforced at runtime | ? |
| Async support | Limited (Flask 2.0+) | Native | ? |
| Error handling | Try/except + jsonify | HTTPException | ? |

---

## Part 3: Advanced FastAPI Features

### Task 3.1: Add Background Tasks

Add a background task to log predictions asynchronously:

```python
from fastapi import BackgroundTasks

def log_prediction(features: List[float], prediction: float, user: str):
    """Log prediction to file (runs in background)."""
    with open('predictions.log', 'a') as f:
        timestamp = datetime.utcnow().isoformat()
        f.write(f"{timestamp},{user},{features},{prediction}\n")

@app.post("/predict")
async def predict(
    request: PredictionRequest,
    background_tasks: BackgroundTasks,
    user: dict = Depends(verify_token)
):
    """Make prediction with background logging."""
    # ... prediction logic ...

    # Add background task (doesn't block response)
    background_tasks.add_task(
        log_prediction,
        request.features,
        prediction,
        user['user']
    )

    return PredictionResponse(...)
```

**TODO**: Add similar background task for batch predictions.

### Task 3.2: Implement Async Model Loading

If your model loading is I/O intensive:

```python
import asyncio

# Global model variable
model = None

@app.on_event("startup")
async def load_model():
    """Load model asynchronously on startup."""
    global model

    # Simulate async model loading from remote storage
    await asyncio.sleep(0.1)  # Placeholder for actual I/O

    with open('model.pkl', 'rb') as f:
        model = pickle.load(f)

    print("✅ Model loaded successfully")

@app.on_event("shutdown")
async def cleanup():
    """Cleanup on shutdown."""
    # Clear cache, close connections, etc.
    prediction_cache.clear()
    print("✅ Cleanup completed")
```

### Task 3.3: Add Request/Response Middleware

Add middleware for request timing:

```python
from fastapi import Request
import time

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time to response headers."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response
```

**TODO**: Add middleware for:
1. Request ID tracking
2. CORS headers
3. Rate limiting (basic implementation)

---

## Part 4: Testing Both APIs

### Task 4.1: Create Test Client

**File**: `test_comparison.py`

```python
"""Compare Flask and FastAPI performance."""

import requests
import time
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configuration
FLASK_URL = "http://localhost:5000"
FASTAPI_URL = "http://localhost:8000"
NUM_REQUESTS = 1000
CONCURRENCY = 10

def get_token(base_url: str) -> str:
    """Get authentication token."""
    response = requests.post(
        f"{base_url}/login",
        json={"username": "admin", "password": "password"}
    )
    return response.json()['token']

def make_prediction(base_url: str, token: str, features: list) -> float:
    """Make a single prediction request."""
    start = time.time()

    response = requests.post(
        f"{base_url}/predict",
        json={"features": features},
        headers={"Authorization": f"Bearer {token}"}
    )

    elapsed = time.time() - start

    if response.status_code != 200:
        raise Exception(f"Request failed: {response.text}")

    return elapsed

def benchmark_api(base_url: str, name: str):
    """Benchmark API performance."""
    print(f"\n{'='*50}")
    print(f"Benchmarking {name}")
    print(f"{'='*50}")

    # Get token
    token = get_token(base_url)

    # Test features
    features = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]

    # Sequential requests
    print(f"\n1. Sequential requests ({NUM_REQUESTS} requests)...")
    latencies = []

    start_time = time.time()
    for _ in range(NUM_REQUESTS):
        latency = make_prediction(base_url, token, features)
        latencies.append(latency)
    total_time = time.time() - start_time

    print(f"   Total time: {total_time:.2f}s")
    print(f"   Requests/sec: {NUM_REQUESTS / total_time:.2f}")
    print(f"   Avg latency: {statistics.mean(latencies)*1000:.2f}ms")
    print(f"   P50 latency: {statistics.median(latencies)*1000:.2f}ms")
    print(f"   P95 latency: {sorted(latencies)[int(0.95*len(latencies))]*1000:.2f}ms")
    print(f"   P99 latency: {sorted(latencies)[int(0.99*len(latencies))]*1000:.2f}ms")

    # Concurrent requests
    print(f"\n2. Concurrent requests ({NUM_REQUESTS} requests, {CONCURRENCY} concurrent)...")
    latencies = []

    start_time = time.time()
    with ThreadPoolExecutor(max_workers=CONCURRENCY) as executor:
        futures = [
            executor.submit(make_prediction, base_url, token, features)
            for _ in range(NUM_REQUESTS)
        ]

        for future in as_completed(futures):
            latencies.append(future.result())

    total_time = time.time() - start_time

    print(f"   Total time: {total_time:.2f}s")
    print(f"   Requests/sec: {NUM_REQUESTS / total_time:.2f}")
    print(f"   Avg latency: {statistics.mean(latencies)*1000:.2f}ms")
    print(f"   P50 latency: {statistics.median(latencies)*1000:.2f}ms")
    print(f"   P95 latency: {sorted(latencies)[int(0.95*len(latencies))]*1000:.2f}ms")
    print(f"   P99 latency: {sorted(latencies)[int(0.99*len(latencies))]*1000:.2f}ms")

if __name__ == "__main__":
    # TODO: Start Flask app on port 5000
    # TODO: Start FastAPI app on port 8000

    benchmark_api(FLASK_URL, "Flask")
    benchmark_api(FASTAPI_URL, "FastAPI")

    print(f"\n{'='*50}")
    print("Benchmark complete!")
    print(f"{'='*50}")
```

**TODO**: Run this benchmark and record results:

```
Flask Results:
- Sequential: ___ req/sec, P95: ___ ms
- Concurrent: ___ req/sec, P95: ___ ms

FastAPI Results:
- Sequential: ___ req/sec, P95: ___ ms
- Concurrent: ___ req/sec, P95: ___ ms

Winner: ___________
Improvement: ____%
```

### Task 4.2: Validate Backward Compatibility

Ensure FastAPI API is backward compatible:

```python
"""Test backward compatibility."""

def test_endpoint_compatibility():
    """Verify FastAPI has same endpoints as Flask."""
    flask_endpoints = ["/health", "/predict", "/batch-predict", "/model-info", "/login"]

    for endpoint in flask_endpoints:
        # TODO: Test that endpoint exists and returns correct status
        pass

def test_request_format_compatibility():
    """Verify request/response format unchanged."""
    # TODO: Send Flask-format request to FastAPI
    # TODO: Verify response matches Flask format
    pass

def test_error_handling_compatibility():
    """Verify error responses match."""
    # TODO: Send invalid requests
    # TODO: Verify error format matches Flask
    pass
```

---

## Part 5: Deployment Comparison

### Task 5.1: Dockerize Both Applications

**Flask Dockerfile**:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements-flask.txt .
RUN pip install --no-cache-dir -r requirements-flask.txt

COPY flask_app.py model.pkl ./

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "flask_app:app"]
```

**FastAPI Dockerfile**:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements-fastapi.txt .
RUN pip install --no-cache-dir -r requirements-fastapi.txt

COPY fastapi_app.py models.py model.pkl ./

CMD ["uvicorn", "fastapi_app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

**TODO**: Compare deployment characteristics:

| Characteristic | Flask + Gunicorn | FastAPI + Uvicorn |
|----------------|------------------|-------------------|
| Base image size | ___ MB | ___ MB |
| Startup time | ___ s | ___ s |
| Memory usage (idle) | ___ MB | ___ MB |
| Memory usage (load) | ___ MB | ___ MB |
| Workers | 4 | 4 |
| Worker model | Process-based | Event loop-based |

### Task 5.2: Create docker-compose for Side-by-Side Comparison

**File**: `docker-compose.yml`

```yaml
version: '3.8'

services:
  flask-api:
    build:
      context: .
      dockerfile: Dockerfile.flask
    ports:
      - "5000:5000"
    environment:
      - PYTHONUNBUFFERED=1
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  fastapi-api:
    build:
      context: .
      dockerfile: Dockerfile.fastapi
    ports:
      - "8000:8000"
    environment:
      - PYTHONUNBUFFERED=1
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Optional: Load testing service
  locust:
    image: locustio/locust
    ports:
      - "8089:8089"
    volumes:
      - ./locustfile.py:/mnt/locust/locustfile.py
    command: -f /mnt/locust/locustfile.py --host=http://flask-api:5000
```

---

## Deliverables

### Document 1: Migration Checklist

```markdown
# Flask to FastAPI Migration Checklist

## Pre-Migration
- [ ] Document all Flask endpoints
- [ ] Create test suite for existing API
- [ ] Benchmark current performance
- [ ] Review authentication mechanism

## Migration
- [ ] Create Pydantic models
- [ ] Migrate endpoints one-by-one
- [ ] Implement authentication
- [ ] Add automatic documentation
- [ ] Create async endpoints where beneficial

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Performance benchmarks meet targets
- [ ] Backward compatibility verified

## Deployment
- [ ] Create Dockerfile
- [ ] Update CI/CD pipeline
- [ ] Deploy to staging
- [ ] Run smoke tests
- [ ] Monitor metrics
- [ ] Gradual rollout to production
```

### Document 2: Performance Comparison Report

Record your findings:

```markdown
# Flask vs FastAPI Performance Comparison

## Throughput
- Flask: ___ req/sec
- FastAPI: ___ req/sec
- Improvement: ___%

## Latency
- Flask P95: ___ ms
- FastAPI P95: ___ ms
- Improvement: ___%

## Code Quality
- Lines of code: Flask ___ vs FastAPI ___
- Type safety: ___
- Documentation: ___

## Recommendation
Based on testing, we recommend ___ because:
1. Reason 1
2. Reason 2
3. Reason 3
```

### Document 3: Updated API Documentation

FastAPI generates this automatically! Access at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

## Success Criteria

- [ ] FastAPI version implements all Flask endpoints
- [ ] Pydantic models validate all inputs
- [ ] Authentication works identically
- [ ] Performance metrics improve or match Flask
- [ ] Automatic API documentation available
- [ ] Backward compatibility maintained
- [ ] Docker deployment successful
- [ ] Comprehensive testing completed

---

## Troubleshooting

### Issue: "Pydantic validation too strict"

If valid requests are rejected:
```python
# Make fields optional or adjust constraints
features: List[float] = Field(..., min_items=1, max_items=20)  # More flexible
```

### Issue: "Async doesn't improve performance"

Async helps for I/O-bound operations, not CPU-bound:
- ✅ Good: Database queries, HTTP requests, file I/O
- ❌ Not helpful: Model inference (CPU/GPU bound)

### Issue: "Token authentication broken"

Check Bearer scheme:
```python
# Flask: token from header directly
token = request.headers.get('Authorization').replace('Bearer ', '')

# FastAPI: HTTPBearer handles this
credentials: HTTPAuthorizationCredentials = Depends(security)
token = credentials.credentials  # Already without 'Bearer '
```

---

## Bonus Challenges

### Challenge 1: Implement Rate Limiting

Use `slowapi` for rate limiting:

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/predict")
@limiter.limit("100/minute")
async def predict(...):
    pass
```

### Challenge 2: Add WebSocket Support

Add real-time prediction streaming:

```python
from fastapi import WebSocket

@app.websocket("/ws/predict")
async def websocket_predict(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_json()
        # Make prediction
        prediction = # ...
        await websocket.send_json({"prediction": prediction})
```

### Challenge 3: Implement GraphQL API

Use Strawberry GraphQL with FastAPI:

```python
import strawberry
from strawberry.fastapi import GraphQLRouter

@strawberry.type
class Prediction:
    value: float
    confidence: float

@strawberry.type
class Query:
    @strawberry.field
    def predict(self, features: List[float]) -> Prediction:
        # Make prediction
        pass

schema = strawberry.Schema(query=Query)
graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")
```

---

## References

- **Lecture 02**: FastAPI Fundamentals
- **Exercise 01-06**: FastAPI basics, authentication, production deployment
- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **Pydantic Documentation**: https://docs.pydantic.dev/
- **Flask Documentation**: https://flask.palletsprojects.com/
- **Migration Guide**: https://fastapi.tiangolo.com/alternatives/

---

## Reflection Questions

1. When would you choose Flask over FastAPI?
2. How does Pydantic validation compare to manual validation?
3. What are the trade-offs of async endpoints?
4. How does automatic documentation improve API development?
5. What migration strategy minimizes risk?
6. How do you ensure backward compatibility during migration?

---

**Estimated Completion Time**: 3-4 hours

**Next Exercise**: Exercise 08 - Comprehensive API Testing
