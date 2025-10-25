# Exercise 03: Rate Limiting and CORS Configuration

## Overview

Enhance your API with production-ready features including rate limiting to prevent abuse, CORS configuration for web applications, and security headers. Learn how to protect your ML API from overuse while allowing legitimate cross-origin requests.

**Difficulty:** Intermediate
**Estimated Time:** 2-3 hours
**Prerequisites:**
- Exercise 01 and 02 completed
- Lecture 03: Authentication & Security
- Understanding of HTTP headers

## Learning Objectives

By completing this exercise, you will:
- Implement rate limiting to prevent API abuse
- Configure CORS for cross-origin requests
- Add security headers
- Create tiered rate limits based on user roles
- Monitor and log rate limit violations
- Handle rate limit errors gracefully

## Scenario

Your ML API is getting popular, and you need to:
- Prevent abuse by limiting request rates
- Allow your frontend application to make requests (different domain)
- Implement different rate limits for free vs premium users
- Add security headers for production deployment

## Project Setup

### Install Dependencies

```bash
pip install slowapi
pip install redis  # Optional: for distributed rate limiting
```

## Part 1: Basic Rate Limiting

**File: app/rate_limiter.py**

```python
from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import Request
from typing import Callable

# TODO: Create basic limiter
# limiter = Limiter(key_func=get_remote_address)

# TODO: Create custom key function that uses user ID from JWT
def get_user_identifier(request: Request) -> str:
    """
    Get user identifier for rate limiting.
    Uses user ID from JWT if authenticated, otherwise IP address.
    """
    # TODO: Check if Authorization header exists
    # TODO: If exists, extract user ID from JWT
    # TODO: Otherwise, return IP address
    # Hint: Use get_remote_address(request) for IP
    pass

# TODO: Create limiter with custom key function
# user_limiter = Limiter(key_func=get_user_identifier)
```

## Part 2: Apply Rate Limits to Endpoints

**File: app/main.py** (update)

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from fastapi import FastAPI, Request

from app.rate_limiter import limiter, user_limiter

app = FastAPI(title="ML API with Rate Limiting")

# TODO: Configure rate limiting
# app.state.limiter = limiter
# app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
# app.add_middleware(SlowAPIMiddleware)

@app.get("/")
@limiter.limit("100/minute")
async def root(request: Request):
    """Root endpoint with rate limit"""
    # TODO: Return welcome message
    pass

@app.post("/api/v1/predict")
@limiter.limit("10/minute")  # Limit expensive ML predictions
async def predict(
    request: Request,
    input_data: PredictionInput,
    current_user: User = Depends(get_current_active_user)
):
    """Prediction endpoint with rate limit"""
    # TODO: Make prediction
    # TODO: Return result
    pass

@app.post("/api/v1/predict/batch")
@limiter.limit("2/minute")  # Stricter limit for batch operations
async def predict_batch(
    request: Request,
    input_data: BatchPredictionInput,
    current_user: User = Depends(get_current_active_user)
):
    """Batch prediction with strict rate limit"""
    # TODO: Process batch
    # TODO: Return results
    pass

# TODO: Add endpoint without rate limit (health check)
@app.get("/health")
async def health_check():
    """Health check - no rate limit"""
    pass
```

## Part 3: Tiered Rate Limiting

**File: app/models.py** (update)

```python
from enum import Enum

class UserTier(str, Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"

class User(BaseModel):
    username: str
    email: str
    tier: UserTier = UserTier.FREE
    disabled: bool = False
```

**File: app/rate_limiter.py** (update)

```python
from app.auth import get_current_user
from app.models import UserTier
from fastapi import Depends

# TODO: Define rate limits per tier
RATE_LIMITS = {
    UserTier.FREE: "10/minute",
    UserTier.PRO: "100/minute",
    UserTier.ENTERPRISE: "1000/minute"
}

def get_rate_limit_for_user(user: User) -> str:
    """Get rate limit based on user tier"""
    # TODO: Return rate limit from RATE_LIMITS dict
    pass

# TODO: Create dynamic rate limiter
class DynamicRateLimiter:
    """Rate limiter that adjusts based on user tier"""

    def __init__(self):
        self.limiters = {
            tier: Limiter(key_func=get_user_identifier)
            for tier in UserTier
        }

    async def check_rate_limit(
        self,
        request: Request,
        user: User
    ):
        """Check rate limit for user based on their tier"""
        # TODO: Get appropriate limiter for user tier
        # TODO: Check rate limit
        # TODO: Raise RateLimitExceeded if exceeded
        pass
```

## Part 4: CORS Configuration

**File: app/main.py** (update)

```python
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# TODO: Configure CORS
# Determine allowed origins based on environment
import os

if os.getenv("ENVIRONMENT") == "production":
    # TODO: Set specific allowed origins for production
    allowed_origins = [
        "https://your-frontend.com",
        "https://app.your-frontend.com"
    ]
else:
    # TODO: Allow all origins in development (use cautiously!)
    allowed_origins = ["*"]

# TODO: Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
    max_age=3600,
)
```

## Part 5: Security Headers Middleware

**File: app/security.py**

```python
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses"""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # TODO: Add security headers
        # X-Frame-Options: Prevent clickjacking
        # response.headers["X-Frame-Options"] = "DENY"

        # X-Content-Type-Options: Prevent MIME sniffing
        # response.headers["X-Content-Type-Options"] = "nosniff"

        # X-XSS-Protection: Enable XSS filter
        # response.headers["X-XSS-Protection"] = "1; mode=block"

        # Referrer-Policy: Control referrer information
        # response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Content-Security-Policy: Restrict resource loading
        # response.headers["Content-Security-Policy"] = "default-src 'self'"

        # Strict-Transport-Security: Force HTTPS (only if using HTTPS)
        # if request.url.scheme == "https":
        #     response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        return response
```

**Apply middleware in main.py:**

```python
from app.security import SecurityHeadersMiddleware

app.add_middleware(SecurityHeadersMiddleware)
```

## Part 6: Rate Limit Information Headers

**File: app/rate_limiter.py** (update)

```python
from fastapi import Response

def add_rate_limit_headers(
    response: Response,
    limit: int,
    remaining: int,
    reset_time: int
):
    """Add rate limit information to response headers"""
    # TODO: Add X-RateLimit-Limit header
    # response.headers["X-RateLimit-Limit"] = str(limit)

    # TODO: Add X-RateLimit-Remaining header
    # response.headers["X-RateLimit-Remaining"] = str(remaining)

    # TODO: Add X-RateLimit-Reset header (Unix timestamp)
    # response.headers["X-RateLimit-Reset"] = str(reset_time)

    pass
```

## Part 7: Custom Rate Limit Error Response

**File: app/main.py** (update)

```python
from fastapi import Request, status
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
import time

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """Custom handler for rate limit exceeded errors"""

    # TODO: Calculate retry after time
    # retry_after = 60  # seconds

    # TODO: Create custom error response
    response = JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={
            "error": "Rate limit exceeded",
            "message": "Too many requests. Please try again later.",
            "retry_after": 60,
            "documentation": "https://docs.your-api.com/rate-limits"
        }
    )

    # TODO: Add Retry-After header
    # response.headers["Retry-After"] = str(retry_after)

    return response
```

## Part 8: Testing CORS and Rate Limiting

**File: tests/test_rate_limit.py**

```python
from fastapi.testclient import TestClient
from app.main import app
import time

client = TestClient(app)

def test_rate_limit_enforced():
    """Test that rate limit is enforced"""
    # TODO: Get auth token
    # TODO: Make requests up to the limit
    # TODO: Verify all succeed (status 200)
    # TODO: Make one more request
    # TODO: Verify it fails with 429
    pass

def test_rate_limit_headers():
    """Test that rate limit headers are present"""
    # TODO: Make a request
    # TODO: Check for X-RateLimit-Limit header
    # TODO: Check for X-RateLimit-Remaining header
    # TODO: Verify headers have correct values
    pass

def test_rate_limit_resets():
    """Test that rate limit resets after time window"""
    # TODO: Exhaust rate limit
    # TODO: Wait for reset period
    # TODO: Verify requests work again
    pass

def test_different_limits_per_tier():
    """Test that different user tiers have different limits"""
    # TODO: Login as free user
    # TODO: Make 10 requests (free tier limit)
    # TODO: Verify 11th request fails

    # TODO: Login as pro user
    # TODO: Make 100 requests (pro tier limit)
    # TODO: Verify all succeed
    pass

def test_cors_headers():
    """Test that CORS headers are present"""
    # TODO: Make OPTIONS request
    # TODO: Check for Access-Control-Allow-Origin
    # TODO: Check for Access-Control-Allow-Methods
    # TODO: Check for Access-Control-Allow-Headers
    pass

def test_security_headers():
    """Test that security headers are present"""
    # TODO: Make any request
    # TODO: Check for X-Frame-Options
    # TODO: Check for X-Content-Type-Options
    # TODO: Check for X-XSS-Protection
    # TODO: Check for Content-Security-Policy
    pass

def test_rate_limit_error_format():
    """Test rate limit error response format"""
    # TODO: Exhaust rate limit
    # TODO: Make request that exceeds limit
    # TODO: Verify response has error message
    # TODO: Verify response has retry_after
    # TODO: Check Retry-After header
    pass
```

## Part 9: Frontend CORS Testing

Create a simple HTML file to test CORS:

**File: test_cors.html**

```html
<!DOCTYPE html>
<html>
<head>
    <title>CORS Test</title>
</head>
<body>
    <h1>API CORS Test</h1>
    <button onclick="testAPI()">Test API</button>
    <div id="result"></div>

    <script>
        async function testAPI() {
            const resultDiv = document.getElementById('result');

            try {
                // TODO: Make fetch request to your API
                const response = await fetch('http://localhost:8000/api/v1/predict', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': 'Bearer YOUR_TOKEN'
                    },
                    body: JSON.stringify({
                        text: 'This is a test'
                    })
                });

                if (response.ok) {
                    const data = await response.json();
                    resultDiv.innerHTML = `<p style="color: green">Success! Prediction: ${data.prediction}</p>`;
                } else {
                    resultDiv.innerHTML = `<p style="color: red">Error: ${response.status}</p>`;
                }
            } catch (error) {
                resultDiv.innerHTML = `<p style="color: red">CORS Error: ${error.message}</p>`;
            }
        }
    </script>
</body>
</html>
```

**Test CORS:**
1. Open the HTML file in browser
2. Click "Test API" button
3. Check browser console for CORS errors
4. Verify response is received

## Part 10: Monitoring Rate Limit Usage

**File: app/monitoring.py**

```python
from collections import defaultdict
from datetime import datetime
from typing import Dict

class RateLimitMonitor:
    """Monitor and log rate limit violations"""

    def __init__(self):
        self.violations = defaultdict(list)
        self.requests_by_user = defaultdict(int)

    def log_violation(self, user_id: str, endpoint: str):
        """Log a rate limit violation"""
        # TODO: Add violation to list
        # self.violations[user_id].append({
        #     "endpoint": endpoint,
        #     "timestamp": datetime.utcnow()
        # })
        pass

    def increment_request_count(self, user_id: str):
        """Increment request count for user"""
        # TODO: Increment counter
        pass

    def get_user_violations(self, user_id: str) -> list:
        """Get violations for a specific user"""
        # TODO: Return violations list
        pass

    def get_top_users(self, limit: int = 10) -> Dict:
        """Get top users by request count"""
        # TODO: Sort users by request count
        # TODO: Return top N users
        pass

# Global monitor instance
monitor = RateLimitMonitor()
```

## Challenges and Extensions

### Challenge 1: Redis-Based Rate Limiting

Implement distributed rate limiting with Redis:

```python
from slowapi.middleware import SlowAPIMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
import redis

redis_client = redis.Redis(host='localhost', port=6379, db=0)

limiter = Limiter(
    key_func=get_remote_address,
    storage_uri="redis://localhost:6379"
)
```

### Challenge 2: Dynamic Rate Limit Adjustment

Adjust rate limits based on API load:

```python
def get_dynamic_rate_limit() -> str:
    cpu_usage = get_cpu_usage()
    if cpu_usage > 80:
        return "5/minute"  # Reduce limit under high load
    elif cpu_usage > 50:
        return "20/minute"
    else:
        return "50/minute"
```

### Challenge 3: Rate Limit Bypass for Trusted IPs

Allow unlimited requests from trusted IPs:

```python
TRUSTED_IPS = ["10.0.0.1", "192.168.1.1"]

def should_check_rate_limit(request: Request) -> bool:
    client_ip = request.client.host
    return client_ip not in TRUSTED_IPS
```

### Challenge 4: Rate Limit Dashboard

Create an endpoint to view rate limit statistics:

```python
@app.get("/admin/rate-limits/stats")
async def get_rate_limit_stats(
    admin_user: User = Depends(require_admin)
):
    return {
        "total_requests": monitor.get_total_requests(),
        "violations": monitor.get_total_violations(),
        "top_users": monitor.get_top_users(10)
    }
```

### Challenge 5: Custom CORS Per Endpoint

Different CORS policies for different endpoints:

```python
from fastapi.middleware.cors import CORSMiddleware

# Stricter CORS for admin endpoints
admin_cors = CORSMiddleware(
    app=app,
    allow_origins=["https://admin.example.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
)

# Permissive CORS for public endpoints
public_cors = CORSMiddleware(
    app=app,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET"],
)
```

## Common Issues and Solutions

### Issue 1: CORS Preflight Requests Failing

**Problem:** OPTIONS requests return 405

**Solution:**
- Ensure CORS middleware is added before routes
- Add OPTIONS to allowed_methods
- Check that wildcard (*) is used cautiously

### Issue 2: Rate Limit Not Working

**Problem:** Rate limit not enforced

**Solution:**
- Verify SlowAPIMiddleware is added
- Check that @limiter.limit() decorator is applied
- Ensure limiter is added to app.state

### Issue 3: Rate Limit Headers Missing

**Problem:** X-RateLimit headers not in response

**Solution:**
- Manually add headers in endpoint
- Use custom rate limiter that adds headers
- Check middleware order

## Deliverables

- ✅ Rate limiting implemented
- ✅ CORS configured correctly
- ✅ Security headers added
- ✅ Tiered rate limits based on user roles
- ✅ Custom error responses for rate limits
- ✅ Tests for all security features
- ✅ Documentation of rate limits

## Key Takeaways

1. **Rate Limiting:** Essential for preventing abuse and ensuring fair usage
2. **CORS:** Required for web applications on different domains
3. **Security Headers:** Add multiple layers of protection
4. **Tiered Access:** Different limits for different user tiers
5. **Monitoring:** Track violations and usage patterns

## Next Steps

- Exercise 04: Background tasks and async operations
- Exercise 05: Deploy API with Docker and NGINX
- Learn about API gateway patterns

---

**Estimated Time:** 2-3 hours
**Difficulty:** Intermediate
**Focus:** Rate limiting, CORS, security headers, production hardening
