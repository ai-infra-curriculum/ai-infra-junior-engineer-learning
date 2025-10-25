# Project 01: Detailed Requirements Specification

**Project:** Simple Model API Deployment
**Role:** Junior AI Infrastructure Engineer
**Version:** 1.0

---

## Table of Contents

1. [Functional Requirements](#functional-requirements)
2. [Non-Functional Requirements](#non-functional-requirements)
3. [API Specifications](#api-specifications)
4. [Data Models](#data-models)
5. [Error Handling](#error-handling)
6. [Security Requirements](#security-requirements)
7. [Performance Requirements](#performance-requirements)
8. [Assessment Rubric](#assessment-rubric)

---

## Functional Requirements

### FR-1: Model Loading and Inference

#### FR-1.1: Model Selection and Loading
**Description:** The application must load a pre-trained image classification model on startup.

**Supported Models:**
- ResNet-50 (recommended for beginners)
- MobileNetV2 (alternative, lighter model)

**Requirements:**
- Model must be loaded during application initialization
- Model weights should be downloaded automatically if not present
- Loading errors must be caught and logged
- Model must be set to evaluation mode (no training)

**Acceptance Criteria:**
- [ ] Model loads successfully within 30 seconds on startup
- [ ] Application fails gracefully with clear error if model loading fails
- [ ] Model is cached and not reloaded on each request
- [ ] Loading progress is logged at INFO level

#### FR-1.2: Image Upload Handling
**Description:** Accept image uploads via HTTP POST requests.

**Requirements:**
- Support multipart/form-data file uploads
- Accept common image formats: JPEG, PNG, BMP, GIF
- Validate file is an actual image (not just by extension)
- Enforce maximum file size limit (10MB)

**Acceptance Criteria:**
- [ ] Endpoint accepts multipart/form-data with 'file' field
- [ ] Rejects non-image files with HTTP 400
- [ ] Rejects files > 10MB with HTTP 413
- [ ] Handles corrupted images gracefully with HTTP 400

#### FR-1.3: Image Preprocessing
**Description:** Preprocess uploaded images according to model requirements.

**Requirements:**
- Convert images to RGB format (handle grayscale and RGBA)
- Resize images to 224x224 pixels
- Apply ImageNet normalization (mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
- Convert to tensor format compatible with the ML framework

**Acceptance Criteria:**
- [ ] All images converted to RGB successfully
- [ ] Images resized maintaining aspect ratio (center crop)
- [ ] Normalization applied correctly
- [ ] Preprocessing completes in < 50ms for typical images

#### FR-1.4: Prediction Generation
**Description:** Generate top-K predictions with class names and confidence scores.

**Requirements:**
- Return top-5 predictions by default
- Include class name/label for each prediction
- Include confidence score (probability) for each prediction
- Apply softmax to convert logits to probabilities
- Map class indices to human-readable labels (ImageNet classes)

**Acceptance Criteria:**
- [ ] Returns exactly 5 predictions (unless top_k parameter specified)
- [ ] Predictions sorted by confidence (highest first)
- [ ] Confidence scores sum to approximately 1.0 (within 0.01)
- [ ] Class labels are human-readable (e.g., "golden retriever", not "n02099601")

#### FR-1.5: Error Handling for Model Operations
**Description:** Handle model-related errors gracefully.

**Requirements:**
- Catch out-of-memory errors during inference
- Handle model file corruption or missing weights
- Detect incompatible input shapes
- Handle framework-specific errors (PyTorch/TensorFlow)

**Acceptance Criteria:**
- [ ] OOM errors return HTTP 503 with retry-after header
- [ ] Missing model weights trigger automatic download or fail gracefully
- [ ] Invalid input shapes return HTTP 400 with descriptive message
- [ ] All model errors logged at ERROR level with stack traces

---

### FR-2: REST API Implementation

#### FR-2.1: /predict Endpoint
**Description:** Primary endpoint for single-image inference.

**Specification:**
```
POST /predict
Content-Type: multipart/form-data

Request Body:
- file: image file (required)
- top_k: number of predictions to return (optional, default=5)

Response (200 OK):
{
  "success": true,
  "predictions": [
    {
      "class": "golden_retriever",
      "confidence": 0.89,
      "rank": 1
    },
    ...
  ],
  "latency_ms": 234,
  "timestamp": "2025-10-18T10:30:45Z"
}

Error Response (4xx/5xx):
{
  "success": false,
  "error": {
    "code": "INVALID_IMAGE_FORMAT",
    "message": "Uploaded file is not a valid image",
    "correlation_id": "req-12345678"
  }
}
```

**Acceptance Criteria:**
- [ ] Endpoint accessible at POST /predict
- [ ] Accepts multipart/form-data requests
- [ ] Returns JSON response
- [ ] Includes latency measurement
- [ ] Logs each request with correlation ID

#### FR-2.2: /health Endpoint
**Description:** Health check endpoint for monitoring and load balancers.

**Specification:**
```
GET /health

Response (200 OK):
{
  "status": "healthy",
  "model_loaded": true,
  "model_name": "resnet50",
  "uptime_seconds": 3600,
  "timestamp": "2025-10-18T10:30:45Z"
}

Response (503 Service Unavailable):
{
  "status": "unhealthy",
  "model_loaded": false,
  "reason": "Model failed to load",
  "timestamp": "2025-10-18T10:30:45Z"
}
```

**Acceptance Criteria:**
- [ ] Responds in < 100ms
- [ ] Returns 200 when application is healthy
- [ ] Returns 503 when model not loaded or critical error
- [ ] No authentication required
- [ ] Can be called frequently (monitoring)

#### FR-2.3: /info Endpoint
**Description:** Provides model and API metadata.

**Specification:**
```
GET /info

Response (200 OK):
{
  "model": {
    "name": "resnet50",
    "framework": "pytorch",
    "version": "2.0.0",
    "input_shape": [224, 224, 3],
    "output_classes": 1000
  },
  "api": {
    "version": "1.0.0",
    "endpoints": ["/predict", "/health", "/info"]
  },
  "limits": {
    "max_file_size_mb": 10,
    "max_image_dimension": 4096,
    "timeout_seconds": 30
  }
}
```

**Acceptance Criteria:**
- [ ] Returns complete metadata
- [ ] Information is accurate and up-to-date
- [ ] No authentication required
- [ ] Useful for API discovery

#### FR-2.4: Request Validation
**Description:** Validate all incoming requests before processing.

**Requirements:**
- Check Content-Type header for /predict
- Validate file field exists in multipart form
- Verify file is not empty
- Check file size before reading into memory
- Validate top_k parameter if provided (1-10 range)

**Acceptance Criteria:**
- [ ] Missing file field returns HTTP 400
- [ ] Empty files return HTTP 400
- [ ] Invalid Content-Type returns HTTP 415
- [ ] Invalid top_k returns HTTP 400 with explanation

#### FR-2.5: Response Format
**Description:** Consistent JSON response format across all endpoints.

**Requirements:**
- Use JSON as default content type
- Include success/error indicator
- Include timestamp in all responses
- Use snake_case for field names
- Pretty-print in development, minified in production

**Acceptance Criteria:**
- [ ] All responses are valid JSON
- [ ] Content-Type header set to application/json
- [ ] Consistent field naming convention
- [ ] Timestamps in ISO 8601 format

---

### FR-3: Error Handling

#### FR-3.1: Structured Error Responses
**Description:** Return structured, informative error responses.

**Error Response Format:**
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "correlation_id": "req-xxxxxxxx",
    "timestamp": "2025-10-18T10:30:45Z",
    "details": {}  // Optional additional context
  }
}
```

**Error Codes:**
- `INVALID_IMAGE_FORMAT` - File is not a valid image
- `FILE_TOO_LARGE` - File exceeds size limit
- `MISSING_FILE` - No file in request
- `MODEL_ERROR` - Model inference failed
- `OUT_OF_MEMORY` - Insufficient memory for operation
- `TIMEOUT` - Request processing exceeded timeout
- `INTERNAL_ERROR` - Unexpected server error

**Acceptance Criteria:**
- [ ] All errors use this format
- [ ] Error codes are consistent and documented
- [ ] Messages are clear and actionable
- [ ] Correlation IDs enable request tracking

#### FR-3.2: Out-of-Memory Handling
**Description:** Gracefully handle OOM conditions.

**Requirements:**
- Catch memory errors during model loading
- Catch memory errors during inference
- Return HTTP 503 with Retry-After header
- Log OOM events for capacity planning
- Attempt to recover (clear caches, etc.)

**Acceptance Criteria:**
- [ ] OOM during inference doesn't crash application
- [ ] Returns HTTP 503 with appropriate message
- [ ] Retry-After header suggests reasonable delay (60s)
- [ ] Application continues to serve requests after recovery

#### FR-3.3: Invalid Input Handling
**Description:** Handle all forms of invalid input.

**Invalid Input Types:**
- Corrupted image files
- Non-image files (PDFs, text files, etc.)
- Images with unsupported formats
- Extremely large images (> 10000x10000)
- Empty files
- Wrong Content-Type

**Acceptance Criteria:**
- [ ] Each invalid input type has specific error code
- [ ] No crashes or exceptions reach the user
- [ ] Error messages help users correct the issue
- [ ] All invalid inputs logged at WARNING level

#### FR-3.4: Request Timeout Handling
**Description:** Enforce maximum request processing time.

**Requirements:**
- Maximum 30 seconds per request
- Timeout applies to entire request lifecycle
- Return HTTP 504 on timeout
- Cancel ongoing inference on timeout
- Log timeout events

**Acceptance Criteria:**
- [ ] Requests exceeding 30s return HTTP 504
- [ ] Timeout message is clear
- [ ] Resources cleaned up on timeout
- [ ] Timeout doesn't affect other requests

---

## Non-Functional Requirements

### NFR-1: Performance

#### NFR-1.1: Latency Requirements
- **P50 (median):** < 300ms for 224x224 images on CPU
- **P95:** < 500ms for 224x224 images on CPU
- **P99:** < 1000ms for 224x224 images on CPU
- **Health check:** < 100ms

**Measurement:** Latency measured from request received to response sent, excluding network time.

#### NFR-1.2: Throughput
- Minimum 10 concurrent requests supported
- Recommended: 20-30 concurrent requests on t3.medium (AWS) or equivalent
- No degradation in P95 latency under normal load

#### NFR-1.3: Resource Usage
- **Memory:** < 2GB under normal load (single worker)
- **CPU:** Efficient use, no CPU-bound loops
- **Startup Time:** < 30 seconds from container start to ready
- **Shutdown Time:** Graceful shutdown within 10 seconds

#### NFR-1.4: Scalability
- Application must be stateless (no local state)
- Support horizontal scaling (multiple instances)
- No file system dependencies (except model weights)
- Thread-safe or process-safe

---

### NFR-2: Reliability

#### NFR-2.1: Availability
- **Target:** 99% uptime under normal conditions
- **Recovery:** Automatic restart on crash (via container orchestration)
- **Graceful Degradation:** Continue serving requests during high load (with increased latency)

#### NFR-2.2: Error Rates
- **Target:** < 1% error rate under normal conditions
- **Transient Errors:** Retry-able errors should return appropriate status codes
- **Permanent Errors:** Clear error messages for unrecoverable errors

#### NFR-2.3: Data Integrity
- All uploaded images processed correctly
- No data corruption during preprocessing
- Predictions deterministic for same input (with eval mode)

---

### NFR-3: Security

#### NFR-3.1: Input Validation
- Validate all user inputs
- Prevent path traversal attacks
- Prevent code injection via filenames
- Sanitize error messages (no sensitive data)

#### NFR-3.2: File Upload Security
- Maximum file size enforced (10MB)
- Verify file content matches declared type
- No execution of uploaded files
- Files not persisted to disk (memory only)

#### NFR-3.3: Rate Limiting (Optional)
- Recommended: 100 requests per minute per IP
- Return HTTP 429 when limit exceeded
- Include Retry-After header

#### NFR-3.4: Logging Security
- No sensitive data in logs
- Log all authentication attempts (if auth added)
- Correlation IDs for request tracking
- Log rotation to prevent disk fill

---

### NFR-4: Maintainability

#### NFR-4.1: Code Quality
- Follow PEP 8 style guide (Python)
- Type hints on all function signatures
- Docstrings (Google style) on all public functions
- Maximum function length: 50 lines
- Maximum file length: 500 lines

#### NFR-4.2: Configuration Management
- All configuration via environment variables or config file
- No hardcoded values (ports, URLs, paths, etc.)
- Default values for optional configurations
- Configuration validation on startup

#### NFR-4.3: Logging
- Structured logging (JSON format recommended)
- Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Include timestamp, level, message, correlation_id
- Log aggregation-friendly format

#### NFR-4.4: Testing
- Unit test coverage > 80%
- Integration tests for all endpoints
- Test error paths, not just happy paths
- Performance tests for latency validation

---

## API Specifications

### Request Headers

**Required:**
- `Content-Type: multipart/form-data` (for /predict)

**Optional:**
- `X-Request-ID: <uuid>` - Client-provided correlation ID
- `Accept: application/json` - Response format (JSON only supported)

### Response Headers

**Always Included:**
- `Content-Type: application/json`
- `X-Correlation-ID: <uuid>` - Request tracking ID
- `X-Response-Time: <ms>` - Processing time in milliseconds

**Conditional:**
- `Retry-After: <seconds>` - For 503 and 429 responses
- `Cache-Control: no-cache` - For /predict endpoint

---

## Data Models

### Prediction Object
```python
from typing import TypedDict

class Prediction(TypedDict):
    class_name: str        # Human-readable class name
    confidence: float      # Probability score (0.0 to 1.0)
    rank: int             # Rank in top-K (1-based)
```

### Error Object
```python
from typing import TypedDict, Optional

class Error(TypedDict):
    code: str                    # Error code
    message: str                 # Human-readable message
    correlation_id: str          # Request tracking ID
    timestamp: str              # ISO 8601 timestamp
    details: Optional[dict]      # Additional context (optional)
```

### Model Info
```python
from typing import TypedDict, List

class ModelInfo(TypedDict):
    name: str                    # Model name
    framework: str               # ML framework (pytorch/tensorflow)
    version: str                 # Framework version
    input_shape: List[int]       # Expected input shape [H, W, C]
    output_classes: int          # Number of output classes
```

---

## Error Handling

### HTTP Status Codes

| Code | Meaning | Usage |
|------|---------|-------|
| 200 | OK | Successful prediction or info request |
| 400 | Bad Request | Invalid input, malformed request |
| 413 | Payload Too Large | File exceeds size limit |
| 415 | Unsupported Media Type | Wrong Content-Type |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Unexpected application error |
| 503 | Service Unavailable | Model not loaded, OOM, overload |
| 504 | Gateway Timeout | Request processing timeout |

### Error Code Mapping

```python
ERROR_CODES = {
    "INVALID_IMAGE_FORMAT": 400,
    "FILE_TOO_LARGE": 413,
    "MISSING_FILE": 400,
    "INVALID_PARAMETER": 400,
    "MODEL_ERROR": 500,
    "OUT_OF_MEMORY": 503,
    "TIMEOUT": 504,
    "RATE_LIMIT_EXCEEDED": 429,
    "INTERNAL_ERROR": 500,
}
```

---

## Security Requirements

### Input Validation Rules

1. **File Size:** Maximum 10MB (10,485,760 bytes)
2. **File Types:** JPEG, PNG, BMP, GIF (validated by content, not extension)
3. **Image Dimensions:** Maximum 10,000 x 10,000 pixels
4. **Filename:** Sanitize to prevent path traversal
5. **Top-K Parameter:** Integer between 1 and 10

### Security Headers

Include these headers in all responses:
```
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
```

---

## Performance Requirements

### Latency Targets by Percentile

| Percentile | Target (CPU) | Measurement Method |
|------------|--------------|-------------------|
| P50 | < 300ms | Server-side timing |
| P95 | < 500ms | Server-side timing |
| P99 | < 1000ms | Server-side timing |
| P99.9 | < 2000ms | Server-side timing |

### Resource Limits

| Resource | Limit | Monitoring |
|----------|-------|-----------|
| Memory | 2GB | Container metrics |
| CPU | 2 cores (burst) | Container metrics |
| Disk I/O | Minimal | Logs only |
| Network | 10 Mbps | Cloud monitoring |

---

## Assessment Rubric

### Code Quality (25 points)

| Criteria | Points | Description |
|----------|--------|-------------|
| Code Organization | 5 | Well-structured modules, clear separation of concerns |
| Code Style | 5 | PEP 8 compliant, consistent formatting |
| Documentation | 5 | Comprehensive docstrings and comments |
| Error Handling | 5 | Robust error handling, all cases covered |
| Testing | 5 | >80% coverage, all scenarios tested |

### Functionality (30 points)

| Criteria | Points | Description |
|----------|--------|-------------|
| API Endpoints | 6 | All endpoints work correctly |
| Model Inference | 6 | Accurate predictions, optimal performance |
| Input Validation | 6 | Comprehensive validation, all edge cases |
| Error Responses | 6 | Clear, structured error messages |
| Performance | 6 | Meets all performance targets |

### Containerization (15 points)

| Criteria | Points | Description |
|----------|--------|-------------|
| Dockerfile | 5 | Optimized, multi-stage, minimal size |
| Image Size | 5 | < 2GB, efficient layering |
| Build Process | 5 | Efficient caching, fast builds |

### Deployment (20 points)

| Criteria | Points | Description |
|----------|--------|-------------|
| Cloud Setup | 5 | Correct cloud configuration, best practices |
| Accessibility | 5 | Public URL, stable, fast |
| Monitoring | 5 | Comprehensive logging and monitoring |
| Security | 5 | Excellent security practices |

### Documentation (10 points)

| Criteria | Points | Description |
|----------|--------|-------------|
| README | 5 | Comprehensive, clear, professional |
| API Docs | 5 | Complete spec with examples |

**Total: 100 points**
**Passing Score: 70 points**

---

## Appendix: Example Requests

### cURL Examples

```bash
# Health check
curl -X GET http://localhost:5000/health

# Get model info
curl -X GET http://localhost:5000/info

# Make prediction
curl -X POST \
  -F "file=@dog.jpg" \
  http://localhost:5000/predict

# Make prediction with custom top_k
curl -X POST \
  -F "file=@dog.jpg" \
  -F "top_k=10" \
  http://localhost:5000/predict
```

### Python Example

```python
import requests

# Health check
response = requests.get('http://localhost:5000/health')
print(response.json())

# Make prediction
with open('dog.jpg', 'rb') as f:
    files = {'file': f}
    response = requests.post('http://localhost:5000/predict', files=files)
    print(response.json())
```

---

**Document Version:** 1.0
**Last Updated:** October 2025
**Maintained by:** AI Infrastructure Curriculum Team
