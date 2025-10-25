# Lecture 01: API Fundamentals & REST

## Table of Contents
1. [Introduction](#introduction)
2. [What is an API?](#what-is-an-api)
3. [Types of APIs](#types-of-apis)
4. [REST Architecture](#rest-architecture)
5. [HTTP Protocol Fundamentals](#http-protocol-fundamentals)
6. [RESTful API Design Principles](#restful-api-design-principles)
7. [API Request and Response Structure](#api-request-and-response-structure)
8. [Status Codes and Error Handling](#status-codes-and-error-handling)
9. [API Versioning Strategies](#api-versioning-strategies)
10. [APIs in AI/ML Infrastructure](#apis-in-aiml-infrastructure)
11. [Best Practices](#best-practices)
12. [Summary and Key Takeaways](#summary-and-key-takeaways)

## Introduction

Application Programming Interfaces (APIs) are the backbone of modern software architecture, enabling different systems, services, and applications to communicate with each other. In AI/ML infrastructure, APIs play a critical role in model serving, data pipeline orchestration, and integration with various tools and platforms.

Understanding how APIs work—particularly RESTful APIs—is essential for building, deploying, and maintaining AI infrastructure. This lecture provides a comprehensive foundation in API concepts, the REST architectural style, and practical design patterns you'll use throughout your career.

### Learning Objectives

By the end of this lecture, you will:
- Understand what APIs are and why they're fundamental to modern software
- Distinguish between different types of APIs and when to use each
- Master the REST architectural principles and constraints
- Comprehend HTTP protocol fundamentals (methods, headers, status codes)
- Design RESTful APIs following best practices
- Handle errors and implement proper status code responses
- Apply API design principles to AI/ML use cases
- Understand API versioning strategies

### Prerequisites
- Module 001: Python Fundamentals
- Module 002: Linux & Command Line
- Basic understanding of client-server architecture
- Familiarity with JSON data format

### Estimated Time
4-5 hours (including hands-on examples)

## What is an API?

### Definition

An **Application Programming Interface (API)** is a contract or interface that defines how software components should interact. It specifies:
- What operations are available
- What inputs each operation requires
- What outputs each operation returns
- What errors might occur

Think of an API as a menu in a restaurant:
- The menu lists what you can order (available operations)
- Each item has a description (documentation)
- You make a request (place an order)
- The kitchen processes it (backend logic)
- You receive a response (your food or an error message if they're out of stock)

### Why APIs Matter

APIs enable:

1. **Separation of Concerns**: Frontend and backend can be developed independently
2. **Reusability**: One API can serve multiple clients (web, mobile, IoT devices)
3. **Scalability**: Services can scale independently
4. **Integration**: Different systems can work together
5. **Abstraction**: Hide complex implementation details behind simple interfaces

### Real-World Example: ML Model Serving

When you deploy a machine learning model, you expose it through an API:

```python
# Client makes a request
POST /api/v1/predict
{
  "features": [1.2, 3.4, 5.6, 7.8]
}

# Server responds with prediction
{
  "prediction": "class_A",
  "confidence": 0.92,
  "latency_ms": 45
}
```

The client doesn't need to know:
- What ML framework you're using (PyTorch, TensorFlow)
- How the model was trained
- Where the model weights are stored
- How preprocessing is done

The API abstracts all these details behind a simple interface.

## Types of APIs

### 1. Web APIs

APIs accessible over HTTP/HTTPS, used for communication between clients and servers over the internet.

**Types of Web APIs:**

#### a) REST (Representational State Transfer)
- Uses HTTP methods (GET, POST, PUT, DELETE)
- Stateless client-server communication
- Resource-based URLs
- Most popular for public APIs

**Example:**
```
GET https://api.example.com/models/bert-base
POST https://api.example.com/predictions
```

#### b) GraphQL
- Query language for APIs
- Client specifies exactly what data it needs
- Single endpoint for all operations
- Reduces over-fetching and under-fetching

**Example:**
```graphql
query {
  model(id: "bert-base") {
    name
    version
    metrics {
      accuracy
      f1Score
    }
  }
}
```

#### c) SOAP (Simple Object Access Protocol)
- XML-based protocol
- Strict standards and contracts (WSDL)
- Common in enterprise and legacy systems
- More overhead than REST

#### d) gRPC
- High-performance RPC framework
- Uses Protocol Buffers for serialization
- Bidirectional streaming
- Ideal for microservices communication

**Example:**
```protobuf
service PredictionService {
  rpc Predict(PredictRequest) returns (PredictResponse);
}
```

### 2. Library/Framework APIs

Interfaces provided by programming libraries and frameworks:

```python
# TensorFlow API
model = tf.keras.Sequential([
    tf.keras.layers.Dense(128, activation='relu'),
    tf.keras.layers.Dense(10, activation='softmax')
])

# PyTorch API
model = nn.Sequential(
    nn.Linear(784, 128),
    nn.ReLU(),
    nn.Linear(128, 10)
)
```

### 3. Operating System APIs

Interfaces for interacting with the OS:

```python
import os
import subprocess

# OS API for file operations
files = os.listdir('/data/models')

# OS API for process management
result = subprocess.run(['nvidia-smi'], capture_output=True)
```

### 4. Hardware APIs

Interfaces for hardware interaction:

```python
import torch

# CUDA API (abstracted through PyTorch)
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model.to(device)
```

### Focus: Web APIs and REST

For the remainder of this lecture, we'll focus on **RESTful Web APIs**, as they are the most common type you'll work with in AI/ML infrastructure.

## REST Architecture

### What is REST?

REST (Representational State Transfer) is an **architectural style**, not a protocol or standard. It was introduced by Roy Fielding in his 2000 doctoral dissertation and has become the dominant approach for building web APIs.

### REST Constraints

A truly RESTful API must adhere to six constraints:

#### 1. Client-Server Architecture

The client and server are **separate** concerns:
- **Client**: Handles user interface and user experience
- **Server**: Handles data storage and business logic

**Benefits:**
- Independent evolution of client and server
- Better scalability
- Simpler components

```
┌─────────┐                    ┌─────────┐
│ Client  │ ←─── HTTP ────→ │ Server  │
│ (React) │                    │ (Python)│
└─────────┘                    └─────────┘
```

#### 2. Stateless

Each request from client to server must contain **all information** needed to understand and process the request. The server doesn't store client context between requests.

**Stateless Example (Good):**
```
GET /api/users/123
Authorization: Bearer eyJhbGciOiJ...
```
Every request includes authentication token.

**Stateful Example (Bad):**
```
POST /api/login
{ "username": "alice", "password": "***" }

# Server stores session
# Later request doesn't include auth info
GET /api/users/123
```

**Benefits of Statelessness:**
- Easier to scale horizontally (any server can handle any request)
- Simpler server implementation
- Better reliability (no session state to lose)
- Improved visibility for monitoring

#### 3. Cacheable

Responses must define themselves as **cacheable or non-cacheable** to prevent clients from reusing stale data.

```http
HTTP/1.1 200 OK
Cache-Control: max-age=3600
ETag: "33a64df551425fcc55e4d42a148795d9f25f89d4"

{
  "model_name": "bert-base",
  "version": "1.0.0"
}
```

**Benefits:**
- Reduced latency
- Reduced server load
- Improved user experience

#### 4. Uniform Interface

A consistent, standardized interface between client and server. This is the fundamental constraint that distinguishes REST from other architectures.

**Four sub-constraints:**

**a) Resource Identification**
Each resource has a unique identifier (URI):
```
/api/models/bert-base
/api/datasets/imagenet
/api/jobs/training-job-123
```

**b) Resource Manipulation Through Representations**
Clients manipulate resources through representations (usually JSON):
```json
{
  "id": "bert-base",
  "name": "BERT Base Model",
  "parameters": 110000000,
  "status": "ready"
}
```

**c) Self-Descriptive Messages**
Each message includes enough information to describe how to process it:
```http
POST /api/predictions HTTP/1.1
Content-Type: application/json
Accept: application/json

{"features": [1.2, 3.4, 5.6]}
```

**d) Hypermedia as the Engine of Application State (HATEOAS)**
Responses include links to related resources:
```json
{
  "id": "bert-base",
  "name": "BERT Base Model",
  "_links": {
    "self": "/api/models/bert-base",
    "predict": "/api/models/bert-base/predict",
    "metrics": "/api/models/bert-base/metrics"
  }
}
```

#### 5. Layered System

The architecture can be composed of hierarchical layers, with each layer only aware of the immediate layer with which it interacts.

```
┌──────────────┐
│  Client      │
├──────────────┤
│  Load Balancer│
├──────────────┤
│  API Gateway │
├──────────────┤
│  Auth Service│
├──────────────┤
│  API Server  │
├──────────────┤
│  Database    │
└──────────────┘
```

Client doesn't know (or care) about the layers in between.

**Benefits:**
- Improved security (intermediary layers can enforce policies)
- Load balancing and caching at different layers
- Encapsulation of legacy services

#### 6. Code on Demand (Optional)

Servers can temporarily extend client functionality by transferring executable code (e.g., JavaScript).

This is the only optional constraint and is rarely used in REST APIs.

### Resources: The Foundation of REST

In REST, everything is a **resource**. A resource is any information that can be named:
- A document or image
- A database record
- A collection of other resources
- A non-virtual object (e.g., a person)

**Resource Examples in ML Infrastructure:**
- Models: `/api/models/bert-base`
- Datasets: `/api/datasets/imagenet`
- Training jobs: `/api/jobs/training-job-123`
- Predictions: `/api/predictions/pred-456`
- Experiments: `/api/experiments/exp-789`

**Resource Naming Conventions:**
- Use **nouns**, not verbs: `/users` not `/getUsers`
- Use **plural** forms: `/models` not `/model`
- Use **hierarchy** for relationships: `/models/bert-base/versions/1.0.0`
- Use **hyphens** for readability: `/training-jobs` not `/trainingJobs`
- Use **lowercase**: `/api/models` not `/API/Models`

## HTTP Protocol Fundamentals

REST APIs are built on top of HTTP (Hypertext Transfer Protocol). Understanding HTTP is essential for designing and consuming REST APIs.

### HTTP Request Structure

An HTTP request consists of:

```http
POST /api/v1/predictions HTTP/1.1
Host: ml-api.example.com
Content-Type: application/json
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Accept: application/json
User-Agent: Python-Requests/2.28.1

{
  "model_id": "bert-base",
  "input_text": "This is a test sentence.",
  "max_length": 512
}
```

**Components:**
1. **Request Line**: Method, URI, HTTP version
2. **Headers**: Metadata about the request
3. **Body**: Data being sent (optional, not used in GET)

### HTTP Methods (Verbs)

HTTP methods define the **action** to be performed on a resource.

#### GET - Retrieve a Resource

**Purpose**: Fetch data without modifying it

**Properties:**
- Safe (doesn't modify server state)
- Idempotent (multiple identical requests have the same effect as one)
- Cacheable

**Examples:**
```http
GET /api/models                    # List all models
GET /api/models/bert-base         # Get specific model
GET /api/models?status=ready      # Filter models
GET /api/models/bert-base/metrics # Get model metrics
```

**Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "id": "bert-base",
  "name": "BERT Base Model",
  "status": "ready",
  "created_at": "2024-10-01T10:00:00Z"
}
```

#### POST - Create a New Resource

**Purpose**: Create a new resource or trigger an action

**Properties:**
- Not safe (modifies server state)
- Not idempotent (multiple requests create multiple resources)
- Not cacheable

**Examples:**
```http
POST /api/models                  # Create new model
POST /api/predictions             # Request prediction
POST /api/jobs/training           # Start training job
```

**Request:**
```http
POST /api/models HTTP/1.1
Content-Type: application/json

{
  "name": "Custom BERT Model",
  "base_model": "bert-base",
  "task": "sentiment-analysis"
}
```

**Response:**
```http
HTTP/1.1 201 Created
Location: /api/models/custom-bert-123
Content-Type: application/json

{
  "id": "custom-bert-123",
  "name": "Custom BERT Model",
  "status": "initializing",
  "created_at": "2024-10-18T14:30:00Z"
}
```

#### PUT - Update/Replace a Resource

**Purpose**: Update an existing resource or create it if it doesn't exist (at a specific URI)

**Properties:**
- Not safe
- **Idempotent** (multiple identical requests have the same effect)
- Not cacheable

**Examples:**
```http
PUT /api/models/bert-base         # Replace entire model config
PUT /api/models/bert-base/config  # Replace model configuration
```

**Request:**
```http
PUT /api/models/bert-base/config HTTP/1.1
Content-Type: application/json

{
  "max_sequence_length": 512,
  "batch_size": 32,
  "learning_rate": 0.001
}
```

**Key Point**: PUT replaces the **entire** resource. If you omit a field, it may be deleted or set to default.

#### PATCH - Partial Update

**Purpose**: Apply partial modifications to a resource

**Properties:**
- Not safe
- Can be idempotent (depends on implementation)
- Not cacheable

**Examples:**
```http
PATCH /api/models/bert-base       # Update specific fields
```

**Request:**
```http
PATCH /api/models/bert-base HTTP/1.1
Content-Type: application/json

{
  "status": "archived"
}
```

Only the `status` field is updated; other fields remain unchanged.

#### DELETE - Remove a Resource

**Purpose**: Delete a resource

**Properties:**
- Not safe
- **Idempotent** (deleting multiple times has same effect as once)
- Not cacheable

**Examples:**
```http
DELETE /api/models/bert-base
DELETE /api/jobs/training-job-123
```

**Response:**
```http
HTTP/1.1 204 No Content
```

#### Other Methods

**HEAD**: Same as GET but returns only headers (no body)
```http
HEAD /api/models/bert-base  # Check if resource exists
```

**OPTIONS**: Describe communication options for the resource
```http
OPTIONS /api/models
# Response includes Allow header with supported methods
```

### HTTP Headers

Headers provide metadata about the request or response.

#### Common Request Headers

```http
# Content negotiation
Accept: application/json
Accept-Language: en-US
Accept-Encoding: gzip, deflate

# Authentication
Authorization: Bearer <token>
Authorization: Basic <base64-credentials>

# Content type
Content-Type: application/json
Content-Length: 1234

# Client information
User-Agent: Mozilla/5.0 ...
Referer: https://example.com/page

# Custom headers (use X- prefix or domain-specific prefix)
X-Request-ID: abc-123-def-456
X-API-Version: 2.0
```

#### Common Response Headers

```http
# Caching
Cache-Control: max-age=3600, must-revalidate
ETag: "33a64df551425fcc55e4d42a148795d9f25f89d4"
Expires: Wed, 21 Oct 2024 07:28:00 GMT

# Content information
Content-Type: application/json; charset=utf-8
Content-Length: 1234
Content-Encoding: gzip

# CORS (Cross-Origin Resource Sharing)
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET, POST, PUT, DELETE

# Rate limiting
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1634567890

# Location of created resource
Location: /api/models/new-model-123
```

## RESTful API Design Principles

### 1. Use Nouns for Resources, Not Verbs

**Good:**
```
GET    /api/models              # Get all models
POST   /api/models              # Create model
GET    /api/models/bert-base    # Get specific model
PUT    /api/models/bert-base    # Update model
DELETE /api/models/bert-base    # Delete model
```

**Bad:**
```
GET  /api/getAllModels
POST /api/createModel
GET  /api/getModel/bert-base
POST /api/updateModel/bert-base
POST /api/deleteModel/bert-base
```

The HTTP method already indicates the action. The URL should identify the resource.

### 2. Use Plural Nouns for Collections

**Good:**
```
/api/models
/api/datasets
/api/training-jobs
```

**Bad:**
```
/api/model
/api/dataset
/api/training-job
```

Consistency: whether you're getting one or many, you're still accessing the "models" collection.

### 3. Use Hierarchies to Show Relationships

```
GET /api/models/bert-base/versions           # All versions of a model
GET /api/models/bert-base/versions/1.0.0     # Specific version
GET /api/datasets/imagenet/splits/train      # Training split
GET /api/experiments/exp-123/runs/run-456    # Specific run
```

### 4. Use Query Parameters for Filtering, Sorting, and Pagination

**Filtering:**
```
GET /api/models?status=ready
GET /api/models?type=transformer&status=ready
GET /api/models?created_after=2024-01-01
```

**Sorting:**
```
GET /api/models?sort=created_at
GET /api/models?sort=-created_at          # Descending
GET /api/models?sort=name,created_at      # Multiple fields
```

**Pagination:**
```
GET /api/models?page=2&per_page=20
GET /api/models?offset=40&limit=20
GET /api/models?cursor=eyJpZCI6MTIzfQ==    # Cursor-based
```

**Full Query Search:**
```
GET /api/models?q=bert+sentiment
```

### 5. Return Appropriate Status Codes

Don't return 200 OK for everything! Use semantic status codes.

### 6. Provide Meaningful Error Messages

**Bad:**
```json
{
  "error": "Bad request"
}
```

**Good:**
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid model configuration",
    "details": [
      {
        "field": "batch_size",
        "issue": "must be a positive integer",
        "provided": -5
      }
    ],
    "documentation_url": "https://docs.example.com/api/models#validation"
  }
}
```

### 7. Version Your API

APIs evolve over time. Versioning prevents breaking existing clients.

**URL Versioning:**
```
/api/v1/models
/api/v2/models
```

**Header Versioning:**
```http
GET /api/models
Accept: application/vnd.example.v2+json
```

**Query Parameter Versioning:**
```
/api/models?version=2
```

## API Request and Response Structure

### Request Structure

A well-formed API request includes:

```http
POST /api/v1/predictions HTTP/1.1
Host: ml-api.example.com
Content-Type: application/json
Authorization: Bearer eyJ...
X-Request-ID: 550e8400-e29b-41d4-a716-446655440000

{
  "model_id": "sentiment-bert-v2",
  "inputs": {
    "text": "This product exceeded my expectations!",
    "language": "en"
  },
  "parameters": {
    "max_length": 512,
    "return_probabilities": true
  }
}
```

### Response Structure

A well-formed API response includes:

```http
HTTP/1.1 200 OK
Content-Type: application/json
X-Request-ID: 550e8400-e29b-41d4-a716-446655440000
X-RateLimit-Remaining: 4999
Cache-Control: no-cache

{
  "data": {
    "prediction": "positive",
    "confidence": 0.94,
    "probabilities": {
      "positive": 0.94,
      "neutral": 0.04,
      "negative": 0.02
    },
    "processing_time_ms": 23
  },
  "metadata": {
    "model_version": "2.1.0",
    "timestamp": "2024-10-18T14:30:00Z",
    "request_id": "550e8400-e29b-41d4-a716-446655440000"
  }
}
```

### Response Envelopes

**With Envelope (Consistent Structure):**
```json
{
  "status": "success",
  "data": { ... },
  "metadata": { ... }
}
```

**Without Envelope (Direct Data):**
```json
{
  "id": "model-123",
  "name": "BERT Model"
}
```

Both approaches are valid. Choose one and be consistent.

## Status Codes and Error Handling

### HTTP Status Code Categories

HTTP status codes are three-digit numbers grouped into five categories:

#### 1xx - Informational
Rarely used in REST APIs.
- `100 Continue`: Server received headers, client can proceed with body

#### 2xx - Success

- **200 OK**: Request succeeded (general success)
  ```http
  GET /api/models/bert-base
  → 200 OK
  ```

- **201 Created**: New resource created successfully
  ```http
  POST /api/models
  → 201 Created
  Location: /api/models/new-model-123
  ```

- **202 Accepted**: Request accepted for processing (async)
  ```http
  POST /api/jobs/training
  → 202 Accepted
  Location: /api/jobs/training-job-456
  ```

- **204 No Content**: Success, no body to return
  ```http
  DELETE /api/models/bert-base
  → 204 No Content
  ```

#### 3xx - Redirection

- **301 Moved Permanently**: Resource permanently moved
  ```http
  GET /api/old-endpoint
  → 301 Moved Permanently
  Location: /api/new-endpoint
  ```

- **304 Not Modified**: Resource hasn't changed (caching)
  ```http
  GET /api/models/bert-base
  If-None-Match: "abc123"
  → 304 Not Modified
  ```

#### 4xx - Client Errors

- **400 Bad Request**: Malformed request or invalid data
  ```json
  {
    "error": "Invalid JSON syntax in request body"
  }
  ```

- **401 Unauthorized**: Authentication required or failed
  ```json
  {
    "error": "Missing or invalid authentication token"
  }
  ```

- **403 Forbidden**: Authenticated but not authorized
  ```json
  {
    "error": "You don't have permission to delete this model"
  }
  ```

- **404 Not Found**: Resource doesn't exist
  ```json
  {
    "error": "Model 'bert-base' not found"
  }
  ```

- **405 Method Not Allowed**: HTTP method not supported
  ```http
  DELETE /api/models/read-only-model
  → 405 Method Not Allowed
  Allow: GET, HEAD
  ```

- **409 Conflict**: Request conflicts with server state
  ```json
  {
    "error": "Model with name 'bert-base' already exists"
  }
  ```

- **422 Unprocessable Entity**: Syntactically correct but semantically invalid
  ```json
  {
    "error": "batch_size must be between 1 and 128",
    "provided": 200
  }
  ```

- **429 Too Many Requests**: Rate limit exceeded
  ```http
  → 429 Too Many Requests
  Retry-After: 60
  X-RateLimit-Reset: 1634567890
  ```

#### 5xx - Server Errors

- **500 Internal Server Error**: Unexpected server error
  ```json
  {
    "error": "An unexpected error occurred. Please try again later.",
    "request_id": "550e8400-e29b-41d4-a716-446655440000"
  }
  ```

- **502 Bad Gateway**: Invalid response from upstream server
- **503 Service Unavailable**: Server temporarily unavailable
  ```http
  → 503 Service Unavailable
  Retry-After: 120
  ```

- **504 Gateway Timeout**: Upstream server timeout

### Error Response Structure

A good error response includes:

```json
{
  "error": {
    "code": "MODEL_NOT_FOUND",
    "message": "The requested model does not exist",
    "details": {
      "model_id": "non-existent-model",
      "available_models": ["/api/models"]
    },
    "request_id": "550e8400-e29b-41d4-a716-446655440000",
    "timestamp": "2024-10-18T14:30:00Z",
    "documentation": "https://docs.example.com/errors#model-not-found"
  }
}
```

**Key elements:**
1. **Machine-readable code**: For programmatic error handling
2. **Human-readable message**: For developers debugging
3. **Details**: Context-specific information
4. **Request ID**: For tracing and support
5. **Documentation link**: Help users resolve the issue

## API Versioning Strategies

As your API evolves, you need a strategy to introduce changes without breaking existing clients.

### 1. URL Path Versioning

**Pros:**
- Clear and explicit
- Easy to route requests
- Simple for clients to specify version

**Cons:**
- Can lead to URL proliferation
- Breaks REST principle of stable resource identifiers

```
https://api.example.com/v1/models
https://api.example.com/v2/models
```

### 2. Query Parameter Versioning

```
https://api.example.com/models?version=2
```

**Pros:**
- Keeps URL structure clean
- Optional (can default to latest)

**Cons:**
- Easy to forget
- Can be cached incorrectly

### 3. Header Versioning

```http
GET /api/models
Accept: application/vnd.example.v2+json
```

Or custom header:
```http
GET /api/models
X-API-Version: 2
```

**Pros:**
- Clean URLs
- Follows HTTP content negotiation pattern

**Cons:**
- Less visible (not in URL)
- Harder to test in browser

### 4. Content Negotiation

```http
GET /api/models
Accept: application/vnd.example.model.v2+json
```

**Pros:**
- True REST approach
- Fine-grained versioning per resource

**Cons:**
- Complex to implement
- Less intuitive for clients

### Best Practices for Versioning

1. **Start with v1** from day one
2. **Only major changes** warrant a new version
3. **Support old versions** for a reasonable period (deprecation policy)
4. **Communicate changes** clearly through:
   - Changelog
   - Deprecation warnings in responses
   - Documentation
5. **Sunset headers** to indicate version retirement:
   ```http
   Sunset: Sat, 31 Dec 2024 23:59:59 GMT
   Deprecation: true
   Link: <https://api.example.com/v2/models>; rel="successor-version"
   ```

## APIs in AI/ML Infrastructure

### Common Use Cases

#### 1. Model Serving/Inference APIs

Expose trained models for predictions:

```python
POST /api/v1/models/bert-sentiment/predict
{
  "text": "This movie was amazing!",
  "return_confidence": true
}

Response:
{
  "sentiment": "positive",
  "confidence": 0.98,
  "latency_ms": 45
}
```

#### 2. Model Management APIs

Manage model lifecycle:

```python
# List models
GET /api/v1/models

# Register new model
POST /api/v1/models
{
  "name": "custom-bert",
  "framework": "pytorch",
  "model_url": "s3://models/custom-bert.pt"
}

# Update model metadata
PATCH /api/v1/models/custom-bert
{
  "status": "production",
  "tags": ["nlp", "sentiment-analysis"]
}

# Delete model
DELETE /api/v1/models/custom-bert
```

#### 3. Training Job APIs

Submit and monitor training jobs:

```python
# Start training
POST /api/v1/training-jobs
{
  "model_type": "bert",
  "dataset": "imdb-sentiment",
  "config": {
    "epochs": 10,
    "batch_size": 32,
    "learning_rate": 0.001
  }
}

# Check status
GET /api/v1/training-jobs/job-123

# Get metrics
GET /api/v1/training-jobs/job-123/metrics
```

#### 4. Data Pipeline APIs

Orchestrate data processing:

```python
# Trigger pipeline
POST /api/v1/pipelines/data-preprocessing/run
{
  "input_dataset": "raw-data-v2",
  "transformations": ["clean", "tokenize", "normalize"]
}

# Monitor pipeline
GET /api/v1/pipelines/run-456/status
```

#### 5. Experiment Tracking APIs

Track ML experiments:

```python
# Create experiment
POST /api/v1/experiments
{
  "name": "bert-hyperparameter-tuning",
  "description": "Testing different learning rates"
}

# Log metrics
POST /api/v1/experiments/exp-123/metrics
{
  "accuracy": 0.92,
  "loss": 0.15,
  "epoch": 5
}

# Log parameters
POST /api/v1/experiments/exp-123/params
{
  "learning_rate": 0.001,
  "batch_size": 32
}
```

### Design Considerations for ML APIs

1. **Batch Predictions**: Support both single and batch inference
   ```python
   POST /api/v1/predict
   {
     "inputs": [
       {"text": "Sample 1"},
       {"text": "Sample 2"},
       {"text": "Sample 3"}
     ]
   }
   ```

2. **Asynchronous Processing**: Long-running tasks should be async
   ```python
   POST /api/v1/training-jobs
   → 202 Accepted
   Location: /api/v1/training-jobs/job-123

   # Client polls for status
   GET /api/v1/training-jobs/job-123
   {
     "status": "running",
     "progress": 0.45
   }
   ```

3. **Streaming Responses**: For real-time or large outputs
   ```python
   GET /api/v1/logs/training-job-123
   # Server-Sent Events or WebSocket stream
   ```

4. **Model Versioning**: Support multiple model versions
   ```python
   POST /api/v1/models/bert-sentiment/v1.0.0/predict
   POST /api/v1/models/bert-sentiment/v2.0.0/predict
   ```

5. **Health Checks**: Essential for deployment
   ```python
   GET /health
   {
     "status": "healthy",
     "model_loaded": true,
     "gpu_available": true,
     "latency_p95_ms": 120
   }
   ```

## Best Practices

### 1. Documentation

- **OpenAPI/Swagger**: Use standard documentation formats
- **Examples**: Provide request/response examples
- **Error Codes**: Document all possible errors
- **Rate Limits**: Clearly state limits and policies

### 2. Security

- **HTTPS Only**: Encrypt all API traffic
- **Authentication**: Require authentication for all non-public endpoints
- **Authorization**: Implement fine-grained permissions
- **Rate Limiting**: Prevent abuse
- **Input Validation**: Validate all inputs thoroughly
- **API Keys**: Rotate keys regularly

### 3. Performance

- **Caching**: Use HTTP caching headers appropriately
- **Compression**: Enable gzip/brotli compression
- **Pagination**: Always paginate large collections
- **Async Operations**: Use async for long-running tasks
- **Connection Pooling**: Reuse connections

### 4. Monitoring & Observability

- **Logging**: Log all requests with request IDs
- **Metrics**: Track latency, throughput, error rates
- **Tracing**: Implement distributed tracing
- **Alerting**: Set up alerts for anomalies

### 5. Backward Compatibility

- **Additive Changes**: Add new fields, don't remove old ones
- **Deprecation Warnings**: Warn before removing features
- **Version Support**: Maintain old versions for transition period

## Summary and Key Takeaways

### Core Concepts

1. **APIs are contracts** that define how systems interact
2. **REST is an architectural style** based on six constraints
3. **Resources are nouns** identified by URIs
4. **HTTP methods are verbs** that define actions on resources
5. **Status codes communicate outcomes** semantically

### RESTful Principles

- **Stateless**: Each request is independent
- **Cacheable**: Responses define cacheability
- **Uniform Interface**: Consistent resource interactions
- **Layered System**: Abstraction through layers

### Design Best Practices

- Use **plural nouns** for resource collections
- Use **hierarchies** for relationships
- Use **query parameters** for filtering and sorting
- Return **appropriate status codes**
- Provide **meaningful error messages**
- **Version your API** from the start

### ML-Specific Considerations

- Support **batch and streaming** inference
- Implement **asynchronous** operations for training
- Expose **model versioning** through the API
- Include **health check** endpoints
- Design for **high throughput** and **low latency**

### Next Steps

In the next lecture, we'll dive deep into **FastAPI**, a modern Python framework for building high-performance REST APIs. You'll learn how to implement the principles covered here using FastAPI's features like automatic documentation, request validation, and async support.

### Further Reading

- [REST dissertation by Roy Fielding](https://www.ics.uci.edu/~fielding/pubs/dissertation/rest_arch_style.htm)
- [HTTP/1.1 Specification (RFC 7231)](https://tools.ietf.org/html/rfc7231)
- [OpenAPI Specification](https://swagger.io/specification/)
- [RESTful API Design Best Practices](https://restfulapi.net/)

---

**Estimated Study Time**: 4-5 hours
**Hands-on Practice**: Complete Exercise 01 to build your first REST API
**Assessment**: Quiz 01 covers all concepts from this lecture
