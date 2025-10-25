# Lecture 04: Advanced API Patterns and Production Strategies

## Table of Contents
1. [Introduction](#introduction)
2. [API Versioning Strategies](#api-versioning-strategies)
3. [GraphQL for ML APIs](#graphql-for-ml-apis)
4. [gRPC for High-Performance APIs](#grpc-for-high-performance-apis)
5. [Rate Limiting and Throttling](#rate-limiting-and-throttling)
6. [Caching Strategies](#caching-strategies)
7. [API Gateways](#api-gateways)
8. [Async and Background Tasks](#async-and-background-tasks)
9. [Webhooks and Event-Driven APIs](#webhooks-and-event-driven-apis)
10. [API Monitoring and Observability](#api-monitoring-and-observability)
11. [Summary and Key Takeaways](#summary-and-key-takeaways)

## Introduction

As ML APIs grow in complexity and scale, basic REST patterns may not be sufficient. You'll need advanced techniques to handle:
- **Breaking changes** without disrupting existing clients
- **High-throughput** inference workloads (100k+ requests/sec)
- **Complex queries** across multiple models or data sources
- **Long-running** training or batch processing jobs
- **Real-time updates** when models are retrained

This lecture covers advanced API patterns and production strategies specifically for AI infrastructure.

### Learning Objectives

By the end of this lecture, you will:
- Implement API versioning to manage breaking changes
- Understand when to use GraphQL vs REST vs gRPC
- Build high-performance gRPC services for ML inference
- Implement rate limiting to protect API resources
- Design effective caching strategies for ML predictions
- Use API gateways for routing and management
- Handle long-running tasks with async patterns
- Monitor APIs with proper observability

### Prerequisites
- Lectures 01-03 in this module (REST, FastAPI, Authentication)
- Understanding of HTTP and APIs
- Basic Python and FastAPI knowledge

**Duration**: 90 minutes
**Difficulty**: Intermediate to Advanced

---

## 1. API Versioning Strategies

### Why Version APIs?

```
Scenario: You need to change your ML model output format

Old Response:
{
  "prediction": "cat",
  "confidence": 0.95
}

New Response (incompatible):
{
  "predictions": [
    {"label": "cat", "score": 0.95},
    {"label": "dog", "score": 0.03}
  ],
  "model_version": "v2.0"
}

❌ If you deploy this without versioning:
   - Existing clients break immediately
   - Mobile apps crash
   - Dashboards show errors
   - Users complain

✅ With versioning:
   - /v1/predict → old format (still works)
   - /v2/predict → new format (opt-in)
   - Gradual migration over months
```

### Versioning Strategies

#### 1. URL Path Versioning (Recommended)

```python
from fastapi import FastAPI, APIRouter

app = FastAPI()

# V1 API
v1_router = APIRouter(prefix="/v1")

@v1_router.post("/predict")
async def predict_v1(input_data: dict):
    return {"prediction": "cat", "confidence": 0.95}

# V2 API
v2_router = APIRouter(prefix="/v2")

@v2_router.post("/predict")
async def predict_v2(input_data: dict):
    return {
        "predictions": [
            {"label": "cat", "score": 0.95},
            {"label": "dog", "score": 0.03}
        ],
        "model_version": "v2.0"
    }

app.include_router(v1_router)
app.include_router(v2_router)

# Both endpoints available:
# POST /v1/predict
# POST /v2/predict
```

**Pros**: Clear, simple, widely understood
**Cons**: Duplicates URL structure

#### 2. Header Versioning

```python
from fastapi import FastAPI, Header, HTTPException

app = FastAPI()

@app.post("/predict")
async def predict(
    input_data: dict,
    api_version: str = Header(default="v1", alias="API-Version")
):
    if api_version == "v1":
        return {"prediction": "cat", "confidence": 0.95}
    elif api_version == "v2":
        return {
            "predictions": [{"label": "cat", "score": 0.95}],
            "model_version": "v2.0"
        }
    else:
        raise HTTPException(400, f"Unsupported API version: {api_version}")

# Usage:
# curl -H "API-Version: v2" POST /predict
```

**Pros**: Clean URLs, more flexible
**Cons**: Not visible in URL, harder to discover

#### 3. Query Parameter Versioning

```python
@app.post("/predict")
async def predict(input_data: dict, version: str = "v1"):
    if version == "v1":
        return old_format()
    elif version == "v2":
        return new_format()
```

**Usage**: `POST /predict?version=v2`

**Pros**: Simple, compatible with caching
**Cons**: Pollutes query params, easy to forget

### Versioning Best Practices

1. **Use Semantic Versioning**
   - `v1`, `v2`, `v3` for major versions
   - `/v1.1/` for minor updates (non-breaking)

2. **Deprecate gradually**
   ```python
   @v1_router.post("/predict", deprecated=True)
   async def predict_v1(input_data: dict):
       """
       Deprecated: Use /v2/predict instead.
       This endpoint will be removed on 2024-12-31.
       """
       # Add deprecation header
       response.headers["X-API-Deprecated"] = "true"
       response.headers["X-API-Sunset-Date"] = "2024-12-31"
       return old_format()
   ```

3. **Maintain old versions for 6-12 months**
4. **Document migration guides**
5. **Alert clients about deprecation**

---

## 2. GraphQL for ML APIs

### GraphQL vs REST

**REST Problems for ML:**
```
# Scenario: Get user recommendations

# REST: Multiple requests (N+1 problem)
GET /user/123                    # User info
GET /user/123/preferences        # User preferences
GET /models/recommend?user=123   # Recommendations
GET /models/123/metadata         # Model metadata

# 4 requests, overfetching data

# GraphQL: Single request
query {
  user(id: 123) {
    name
    preferences { categories }
    recommendations(limit: 10) {
      item_id
      score
      model { name, version }
    }
  }
}
```

### When to Use GraphQL for ML

✅ **Good for:**
- Complex, nested data queries
- Dashboards with flexible data needs
- Mobile apps (reduce bandwidth)
- Batch predictions across multiple models

❌ **Not good for:**
- High-throughput, simple inference (REST/gRPC better)
- Real-time streaming (WebSockets/gRPC streaming better)

### GraphQL Example with Strawberry (FastAPI)

```python
from fastapi import FastAPI
import strawberry
from strawberry.fastapi import GraphQLRouter

# Define types
@strawberry.type
class Prediction:
    label: str
    score: float

@strawberry.type
class Model:
    name: str
    version: str

@strawberry.type
class ModelPrediction:
    model: Model
    predictions: list[Prediction]

# Define queries
@strawberry.type
class Query:
    @strawberry.field
    async def predict(self, input_data: str) -> ModelPrediction:
        # Run inference
        predictions = await run_model(input_data)
        return ModelPrediction(
            model=Model(name="bert-classifier", version="v1.0"),
            predictions=[
                Prediction(label="positive", score=0.95),
                Prediction(label="negative", score=0.05)
            ]
        )

    @strawberry.field
    async def batch_predict(
        self, inputs: list[str], models: list[str]
    ) -> list[ModelPrediction]:
        # Run predictions across multiple models
        results = []
        for model_name in models:
            model_predictions = await run_model_batch(model_name, inputs)
            results.append(model_predictions)
        return results

# Create schema
schema = strawberry.Schema(query=Query)

# Add to FastAPI
app = FastAPI()
graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")

# Query:
# {
#   predict(inputData: "This is great!") {
#     model { name version }
#     predictions { label score }
#   }
# }
```

---

## 3. gRPC for High-Performance APIs

### Why gRPC for ML Inference?

```
Performance Comparison:
┌──────────────────────────────────────┐
│  Metric       │ REST  │ gRPC  │ Δ    │
│──────────────────────────────────────│
│  Latency      │ 50ms  │ 10ms  │ 5x ↓ │
│  Throughput   │ 10k/s │ 100k/s│ 10x ↑│
│  Bandwidth    │ 1MB/s │ 0.2MB │ 5x ↓ │
│  CPU usage    │ 40%   │ 15%   │ 2.7x↓│
└──────────────────────────────────────┘

Why?
- Binary protocol (Protobuf) vs JSON
- HTTP/2 multiplexing vs HTTP/1.1
- Code generation vs manual serialization
- Built-in streaming
```

### When to Use gRPC

✅ **Use gRPC for:**
- Microservice-to-microservice communication
- High-throughput ML inference (>1000 req/s)
- Streaming predictions (video, audio)
- Model serving backends (TensorFlow Serving, TorchServe)

❌ **Don't use gRPC for:**
- Public-facing APIs (browser support limited)
- Simple CRUD operations
- When clients can't use Protobuf

### gRPC Example for ML Inference

**1. Define protocol buffer (`.proto` file):**

```protobuf
// inference.proto
syntax = "proto3";

package ml_inference;

service InferenceService {
  // Single prediction
  rpc Predict(PredictRequest) returns (PredictResponse);

  // Batch prediction
  rpc BatchPredict(BatchPredictRequest) returns (BatchPredictResponse);

  // Streaming predictions
  rpc StreamPredict(stream PredictRequest) returns (stream PredictResponse);
}

message PredictRequest {
  string model_name = 1;
  repeated float features = 2;
  map<string, string> metadata = 3;
}

message Prediction {
  string label = 1;
  float score = 2;
}

message PredictResponse {
  repeated Prediction predictions = 1;
  string model_version = 2;
  float latency_ms = 3;
}

message BatchPredictRequest {
  string model_name = 1;
  repeated PredictRequest requests = 2;
}

message BatchPredictResponse {
  repeated PredictResponse responses = 1;
}
```

**2. Generate Python code:**

```bash
python -m grpc_tools.protoc \
  -I. \
  --python_out=. \
  --grpc_python_out=. \
  inference.proto
```

**3. Implement server:**

```python
import grpc
from concurrent import futures
import inference_pb2
import inference_pb2_grpc
import numpy as np

class InferenceService(inference_pb2_grpc.InferenceServiceServicer):
    def __init__(self):
        # Load model
        self.model = load_model("bert-classifier")

    def Predict(self, request, context):
        # Run inference
        features = np.array(request.features)
        predictions = self.model.predict(features)

        # Build response
        response = inference_pb2.PredictResponse(
            model_version="v1.0",
            latency_ms=12.5
        )

        for label, score in predictions:
            pred = response.predictions.add()
            pred.label = label
            pred.score = score

        return response

    def StreamPredict(self, request_iterator, context):
        # Stream predictions
        for request in request_iterator:
            response = self.Predict(request, context)
            yield response

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    inference_pb2_grpc.add_InferenceServiceServicer_to_server(
        InferenceService(), server
    )
    server.add_insecure_port('[::]:50051')
    server.start()
    print("gRPC server started on port 50051")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
```

**4. Implement client:**

```python
import grpc
import inference_pb2
import inference_pb2_grpc

def run_inference():
    channel = grpc.insecure_channel('localhost:50051')
    stub = inference_pb2_grpc.InferenceServiceStub(channel)

    request = inference_pb2.PredictRequest(
        model_name="bert-classifier",
        features=[0.1, 0.2, 0.3, 0.4]
    )

    response = stub.Predict(request)
    print(f"Predictions: {response.predictions}")
    print(f"Latency: {response.latency_ms}ms")
```

---

## 4. Rate Limiting and Throttling

### Why Rate Limit ML APIs?

```
Scenario: Public ML API without rate limits

User sends 1,000,000 requests/min
↓
GPU resources exhausted
↓
API down for everyone
↓
$10,000 cloud bill
```

### Rate Limiting Strategies

#### 1. Fixed Window

```python
from fastapi import FastAPI, Request, HTTPException
from collections import defaultdict
import time

app = FastAPI()

# Storage: {user_id: [(timestamp, count)]}
request_counts = defaultdict(list)

RATE_LIMIT = 100  # requests per minute
WINDOW = 60  # seconds

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    user_id = request.headers.get("X-User-ID", "anonymous")
    current_time = time.time()

    # Clean old requests
    request_counts[user_id] = [
        (ts, count) for ts, count in request_counts[user_id]
        if current_time - ts < WINDOW
    ]

    # Count requests in current window
    total_requests = sum(count for _, count in request_counts[user_id])

    if total_requests >= RATE_LIMIT:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Max {RATE_LIMIT} requests per minute."
        )

    # Record request
    request_counts[user_id].append((current_time, 1))

    response = await call_next(request)
    response.headers["X-RateLimit-Limit"] = str(RATE_LIMIT)
    response.headers["X-RateLimit-Remaining"] = str(RATE_LIMIT - total_requests - 1)
    return response
```

#### 2. Token Bucket (Recommended)

Better handling of bursts:

```python
import time
from fastapi import FastAPI, Request, HTTPException

class TokenBucket:
    def __init__(self, rate: int, capacity: int):
        self.rate = rate  # tokens per second
        self.capacity = capacity  # max tokens
        self.tokens = capacity
        self.last_update = time.time()

    def consume(self, tokens: int = 1) -> bool:
        current_time = time.time()
        # Refill tokens
        elapsed = current_time - self.last_update
        self.tokens = min(
            self.capacity,
            self.tokens + elapsed * self.rate
        )
        self.last_update = current_time

        # Check if enough tokens
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False

# Per-user buckets
buckets = {}

@app.middleware("http")
async def token_bucket_middleware(request: Request, call_next):
    user_id = request.headers.get("X-User-ID", "anonymous")

    if user_id not in buckets:
        # 10 requests/sec, burst up to 50
        buckets[user_id] = TokenBucket(rate=10, capacity=50)

    if not buckets[user_id].consume():
        raise HTTPException(429, "Rate limit exceeded")

    return await call_next(request)
```

#### 3. Redis-Based Rate Limiting (Production)

```python
import aioredis
from fastapi import FastAPI, Request, HTTPException

app = FastAPI()
redis = None

@app.on_event("startup")
async def startup():
    global redis
    redis = await aioredis.from_url("redis://localhost")

@app.middleware("http")
async def redis_rate_limit(request: Request, call_next):
    user_id = request.headers.get("X-User-ID", "anonymous")
    key = f"rate_limit:{user_id}"

    # Increment counter
    current = await redis.incr(key)

    # Set expiry on first request
    if current == 1:
        await redis.expire(key, 60)  # 60 second window

    # Check limit
    if current > 100:
        raise HTTPException(429, "Rate limit exceeded")

    return await call_next(request)
```

### Cost-Based Rate Limiting

Different endpoints have different costs:

```python
COST_PER_ENDPOINT = {
    "/predict/small-model": 1,      # 1 token
    "/predict/large-model": 10,     # 10 tokens
    "/batch-predict": 50,           # 50 tokens
}

@app.middleware("http")
async def cost_based_rate_limit(request: Request, call_next):
    user_id = request.headers.get("X-User-ID")
    endpoint = request.url.path

    cost = COST_PER_ENDPOINT.get(endpoint, 1)

    if not buckets[user_id].consume(cost):
        raise HTTPException(429, f"Insufficient quota (cost: {cost} tokens)")

    return await call_next(request)
```

---

## 5. Caching Strategies

### Why Cache ML Predictions?

```
Scenario: Image classification API

Same image uploaded multiple times
├── User 1 uploads cat.jpg → Prediction: "cat" (100ms)
├── User 2 uploads cat.jpg → Prediction: "cat" (100ms) ← Wasted!
└── User 3 uploads cat.jpg → Prediction: "cat" (100ms) ← Wasted!

With caching:
├── User 1 uploads cat.jpg → Prediction: "cat" (100ms, cache MISS)
├── User 2 uploads cat.jpg → Prediction: "cat" (2ms, cache HIT) ✓
└── User 3 uploads cat.jpg → Prediction: "cat" (2ms, cache HIT) ✓

Savings: 98ms × 2 = 196ms saved, 2× less GPU usage
```

### Caching Strategies

#### 1. In-Memory Cache (LRU)

```python
from functools import lru_cache
import hashlib
import json

@lru_cache(maxsize=1000)
def predict_cached(input_hash: str):
    # This function is cached
    return run_model(input_hash)

@app.post("/predict")
async def predict(input_data: dict):
    # Hash input for cache key
    input_json = json.dumps(input_data, sort_keys=True)
    input_hash = hashlib.md5(input_json.encode()).hexdigest()

    # Try cache
    result = predict_cached(input_hash)
    return result
```

#### 2. Redis Cache

```python
import aioredis
import json
import hashlib

redis = await aioredis.from_url("redis://localhost")

async def get_cached_prediction(input_data: dict):
    # Create cache key
    input_json = json.dumps(input_data, sort_keys=True)
    cache_key = f"pred:{hashlib.md5(input_json.encode()).hexdigest()}"

    # Try cache
    cached = await redis.get(cache_key)
    if cached:
        return json.loads(cached)

    # Cache miss - run inference
    result = await run_model(input_data)

    # Store in cache (TTL: 1 hour)
    await redis.setex(cache_key, 3600, json.dumps(result))

    return result

@app.post("/predict")
async def predict(input_data: dict):
    return await get_cached_prediction(input_data)
```

### Cache Invalidation

```python
# Invalidate cache when model updates
@app.post("/admin/update-model")
async def update_model(model_version: str):
    # Deploy new model
    deploy_model(model_version)

    # Clear prediction cache
    await redis.flushdb()  # Or use pattern: redis.delete("pred:*")

    return {"status": "Model updated, cache cleared"}
```

---

## 6. API Gateways

### What is an API Gateway?

```
Without Gateway:
Client → ML API 1
Client → ML API 2
Client → ML API 3
(Each client implements: auth, rate limiting, logging, retry)

With Gateway:
Client → Gateway → ML API 1
                 → ML API 2
                 → ML API 3
(Gateway handles: auth, rate limiting, logging, routing)
```

### Popular API Gateways

- **Kong** - Open source, plugin-based
- **AWS API Gateway** - Managed, serverless
- **NGINX** - High performance, flexible
- **Traefik** - Kubernetes-native
- **Envoy** - Service mesh

### Kong Example for ML APIs

```yaml
# kong.yml
services:
  - name: ml-inference-service
    url: http://ml-api:8000
    routes:
      - name: predict-route
        paths:
          - /predict
    plugins:
      - name: key-auth
      - name: rate-limiting
        config:
          minute: 100
          hour: 1000
      - name: request-transformer
        config:
          add:
            headers:
              - X-Gateway: Kong
      - name: prometheus
```

```bash
# Apply configuration
curl -X POST http://localhost:8001/config \
  --data @kong.yml
```

---

## 7. Async and Background Tasks

### Long-Running ML Tasks

```python
from fastapi import FastAPI, BackgroundTasks
from celery import Celery
import uuid

app = FastAPI()
celery_app = Celery('tasks', broker='redis://localhost:6379')

# In-memory job storage (use Redis in production)
jobs = {}

@celery_app.task
def train_model_task(job_id: str, config: dict):
    jobs[job_id] = {"status": "running"}
    try:
        # Train model (takes hours)
        model = train_model(config)
        save_model(model)
        jobs[job_id] = {"status": "completed", "model_path": "models/model.pt"}
    except Exception as e:
        jobs[job_id] = {"status": "failed", "error": str(e)}

@app.post("/train")
async def start_training(config: dict):
    job_id = str(uuid.uuid4())
    train_model_task.delay(job_id, config)
    return {
        "job_id": job_id,
        "status": "queued",
        "status_url": f"/jobs/{job_id}"
    }

@app.get("/jobs/{job_id}")
async def get_job_status(job_id: str):
    if job_id not in jobs:
        return {"error": "Job not found"}
    return jobs[job_id]
```

---

## 8. Summary and Key Takeaways

### Core Concepts

1. **API Versioning** prevents breaking changes
   - Use URL path versioning (`/v1/`, `/v2/`)
   - Deprecate gradually with sunset dates
   - Maintain old versions for 6-12 months

2. **Choose the right protocol**
   - REST: Public APIs, simple CRUD
   - GraphQL: Complex queries, flexible clients
   - gRPC: High-performance, microservices

3. **Rate limiting** protects resources
   - Use token bucket algorithm
   - Implement cost-based limits for ML
   - Store state in Redis for production

4. **Caching** saves compute
   - Cache predictions by input hash
   - Use Redis for distributed caching
   - Invalidate on model updates

5. **API Gateways** centralize cross-cutting concerns
   - Authentication, rate limiting, logging
   - Reduces client complexity
   - Simplifies monitoring

6. **Async tasks** handle long-running jobs
   - Use Celery or similar task queue
   - Return job ID immediately
   - Provide status endpoint

### Practical Skills Gained

✅ Version APIs to manage breaking changes
✅ Implement high-performance gRPC services
✅ Add rate limiting to protect ML resources
✅ Cache predictions to reduce latency and cost
✅ Use API gateways for centralized management
✅ Handle long-running training jobs asynchronously

### Next Steps

- **Practice**: Add versioning to an existing API
- **Experiment**: Compare REST vs gRPC performance
- **Implement**: Add Redis-based rate limiting
- **Deploy**: Set up Kong gateway for an ML API

### Additional Resources

- [API Versioning Best Practices](https://www.troyhunt.com/your-api-versioning-is-wrong-which-is/)
- [GraphQL Official Docs](https://graphql.org/)
- [gRPC Python Quickstart](https://grpc.io/docs/languages/python/quickstart/)
- [Kong API Gateway](https://konghq.com/)
- [FastAPI Background Tasks](https://fastapi.tiangolo.com/tutorial/background-tasks/)

---

**Congratulations!** You now understand advanced API patterns and production strategies for building scalable, high-performance ML APIs.

**Next Lecture**: Module 008 - Databases & SQL
