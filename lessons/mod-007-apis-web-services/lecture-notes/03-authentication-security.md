# Lecture 03: Authentication & Security for APIs

## Table of Contents
1. [Introduction](#introduction)
2. [Security Fundamentals](#security-fundamentals)
3. [Authentication vs Authorization](#authentication-vs-authorization)
4. [API Key Authentication](#api-key-authentication)
5. [JWT (JSON Web Tokens)](#jwt-json-web-tokens)
6. [OAuth2 and OpenID Connect](#oauth2-and-openid-connect)
7. [Implementing Authentication in FastAPI](#implementing-authentication-in-fastapi)
8. [Password Security](#password-security)
9. [HTTPS and Transport Security](#https-and-transport-security)
10. [CORS (Cross-Origin Resource Sharing)](#cors-cross-origin-resource-sharing)
11. [Rate Limiting and Throttling](#rate-limiting-and-throttling)
12. [Input Validation and Sanitization](#input-validation-and-sanitization)
13. [Security Headers](#security-headers)
14. [Security for ML APIs](#security-for-ml-apis)
15. [Best Practices and Checklists](#best-practices-and-checklists)
16. [Summary and Key Takeaways](#summary-and-key-takeaways)

## Introduction

Security is not optional—it's a fundamental requirement for any production API. A single security vulnerability can lead to data breaches, unauthorized access, service disruption, or worse. This is especially critical for ML APIs, which often handle sensitive data and expensive computational resources.

This lecture covers essential security concepts and practical implementation strategies for building secure APIs.

### Learning Objectives

By the end of this lecture, you will:
- Understand the difference between authentication and authorization
- Implement various authentication methods (API keys, JWT, OAuth2)
- Secure passwords using proper hashing techniques
- Configure HTTPS and transport layer security
- Implement CORS policies correctly
- Add rate limiting to prevent abuse
- Validate and sanitize user inputs
- Apply security headers
- Understand ML-specific security concerns
- Follow security best practices

### Prerequisites
- Module 007 - Lecture 01: API Fundamentals
- Module 007 - Lecture 02: FastAPI Framework
- Basic understanding of cryptography concepts
- HTTP protocol knowledge

### Estimated Time
4-5 hours (including hands-on implementation)

## Security Fundamentals

### The CIA Triad

The foundation of information security:

1. **Confidentiality**: Data is accessible only to authorized users
   - Encryption (data at rest and in transit)
   - Access controls
   - Authentication

2. **Integrity**: Data is accurate and hasn't been tampered with
   - Checksums and hashes
   - Digital signatures
   - Validation

3. **Availability**: Systems are accessible when needed
   - Load balancing
   - DDoS protection
   - Rate limiting

### Principle of Least Privilege

Grant only the minimum permissions necessary:

```python
# Bad: Give admin access to everyone
user_permissions = "admin"

# Good: Granular permissions
user_permissions = {
    "read_models": True,
    "create_models": False,
    "delete_models": False,
    "predict": True
}
```

### Defense in Depth

Multiple layers of security:

```
┌─────────────────────────────┐
│ Application Layer           │ ← Input validation
├─────────────────────────────┤
│ Authentication Layer        │ ← JWT/OAuth2
├─────────────────────────────┤
│ Network Layer               │ ← Firewall, VPN
├─────────────────────────────┤
│ Transport Layer             │ ← HTTPS/TLS
├─────────────────────────────┤
│ Infrastructure Layer        │ ← Security groups
└─────────────────────────────┘
```

### Security by Design

Build security in from the start, not as an afterthought:

- Use secure frameworks (FastAPI, Django)
- Follow security guidelines (OWASP Top 10)
- Regular security audits
- Automated security testing
- Keep dependencies updated

## Authentication vs Authorization

These terms are often confused, but they serve different purposes:

### Authentication

**"Who are you?"**

Verifying the identity of a user or system.

```python
# User provides credentials
username = "alice"
password = "secret123"

# System verifies identity
if verify_credentials(username, password):
    # User is authenticated
    issue_token(username)
```

**Methods:**
- Username/password
- API keys
- Tokens (JWT)
- Certificates
- Biometrics

### Authorization

**"What can you do?"**

Determining what an authenticated user is allowed to do.

```python
# User is authenticated as "alice"
user = get_current_user()  # alice

# Check authorization
if user.has_permission("delete_models"):
    delete_model(model_id)
else:
    raise PermissionDeniedError()
```

**Methods:**
- Role-Based Access Control (RBAC)
- Attribute-Based Access Control (ABAC)
- Access Control Lists (ACL)

### Example Flow

```python
from fastapi import FastAPI, Depends, HTTPException
from typing import Optional

app = FastAPI()

# Authentication: Verify who they are
def authenticate_user(api_key: str) -> Optional[User]:
    user = db.get_user_by_api_key(api_key)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return user

# Authorization: Check what they can do
def authorize_action(user: User, action: str) -> bool:
    return action in user.permissions

@app.delete("/models/{model_id}")
def delete_model(
    model_id: str,
    user: User = Depends(authenticate_user)
):
    # Authorization check
    if not authorize_action(user, "delete_models"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    # Perform action
    db.delete_model(model_id)
    return {"message": "Model deleted"}
```

**Key Differences:**

| Aspect | Authentication | Authorization |
|--------|---------------|---------------|
| Question | Who are you? | What can you do? |
| Process | Verify identity | Check permissions |
| Status Code | 401 Unauthorized | 403 Forbidden |
| Order | First | Second (after auth) |
| Example | Login with password | Access admin panel |

## API Key Authentication

The simplest form of authentication for APIs.

### What is an API Key?

A unique identifier used to authenticate requests:

```
API-Key: sk_live_51H8K2jLkJ...
```

### Advantages

- Simple to implement
- Easy for users to understand
- No session management needed
- Stateless

### Disadvantages

- If leaked, anyone can use it
- No built-in expiration
- Hard to rotate safely
- Limited information about the user

### Implementation

**Generate API Keys:**

```python
import secrets
import hashlib

def generate_api_key() -> str:
    """Generate a secure random API key"""
    return secrets.token_urlsafe(32)

def hash_api_key(api_key: str) -> str:
    """Hash API key for storage"""
    return hashlib.sha256(api_key.encode()).hexdigest()

# Usage
api_key = generate_api_key()
print(f"API Key: {api_key}")
# Store hash in database
hashed = hash_api_key(api_key)
```

**Verify API Keys:**

```python
from fastapi import FastAPI, HTTPException, Security
from fastapi.security import APIKeyHeader

app = FastAPI()

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

# Simulated database
API_KEYS = {
    "hashed_key_1": {"username": "alice", "permissions": ["read", "write"]},
    "hashed_key_2": {"username": "bob", "permissions": ["read"]}
}

def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key is None:
        raise HTTPException(status_code=401, detail="API key missing")

    hashed = hash_api_key(api_key)
    if hashed not in API_KEYS:
        raise HTTPException(status_code=401, detail="Invalid API key")

    return API_KEYS[hashed]

@app.get("/protected")
def protected_route(user_info: dict = Depends(verify_api_key)):
    return {"message": f"Hello {user_info['username']}"}
```

**Using API Keys (Client Side):**

```python
import requests

headers = {"X-API-Key": "your-api-key-here"}
response = requests.get("http://api.example.com/protected", headers=headers)
```

### Best Practices

1. **Use HTTPS**: API keys in plain HTTP can be intercepted
2. **Hash keys**: Store hashed versions in database
3. **Prefix keys**: Use prefixes to identify key types (`sk_live_`, `pk_test_`)
4. **Rotation**: Provide mechanism to rotate keys
5. **Scopes**: Limit key permissions
6. **Monitoring**: Log API key usage and detect abuse
7. **Rate limiting**: Prevent brute force attacks

## JWT (JSON Web Tokens)

JWT is a compact, URL-safe means of representing claims between two parties.

### What is JWT?

A JWT consists of three parts:
```
header.payload.signature
```

Example:
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

**Parts:**

1. **Header**: Algorithm and token type
   ```json
   {
     "alg": "HS256",
     "typ": "JWT"
   }
   ```

2. **Payload**: Claims (data)
   ```json
   {
     "sub": "1234567890",
     "name": "Alice Smith",
     "role": "admin",
     "exp": 1634567890
   }
   ```

3. **Signature**: Verifies integrity
   ```
   HMACSHA256(
     base64UrlEncode(header) + "." +
     base64UrlEncode(payload),
     secret
   )
   ```

### Advantages

- **Stateless**: No server-side session storage
- **Compact**: Easily transmitted in URLs, headers
- **Self-contained**: Contains all user information
- **Secure**: Cryptographically signed
- **Scalable**: Works across multiple servers

### Disadvantages

- **Cannot revoke**: Valid until expiration
- **Size**: Larger than simple API keys
- **Secret management**: Must protect signing key

### Standard Claims

- **iss** (issuer): Who created the token
- **sub** (subject): User ID
- **aud** (audience): Who token is intended for
- **exp** (expiration): When token expires
- **iat** (issued at): When token was created
- **nbf** (not before): Token not valid before this time

### Implementation with FastAPI

**Install dependencies:**
```bash
pip install python-jose[cryptography]
pip install passlib[bcrypt]
pip install python-multipart
```

**Create JWT utilities:**

```python
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext

# Configuration
SECRET_KEY = "your-secret-key-keep-it-secret"  # Use environment variable!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token"""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> dict:
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )
```

**Login endpoint:**

```python
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class Token(BaseModel):
    access_token: str
    token_type: str

class User(BaseModel):
    username: str
    email: str
    disabled: bool = False

# Simulated user database
fake_users_db = {
    "alice": {
        "username": "alice",
        "email": "alice@example.com",
        "hashed_password": "$2b$12$...",  # bcrypt hash
        "disabled": False
    }
}

def authenticate_user(username: str, password: str):
    """Verify username and password"""
    user = fake_users_db.get(username)
    if not user:
        return False
    if not pwd_context.verify(password, user["hashed_password"]):
        return False
    return user

@app.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login and get access token"""
    user = authenticate_user(form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Create token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]},
        expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}
```

**Protected endpoints:**

```python
async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Get current user from token"""
    payload = verify_token(token)
    username: str = payload.get("sub")

    if username is None:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = fake_users_db.get(username)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")

    return User(**user)

@app.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """Get current user profile"""
    return current_user

@app.get("/protected")
async def protected_route(current_user: User = Depends(get_current_user)):
    return {"message": f"Hello {current_user.username}"}
```

**Client usage:**

```python
import requests

# 1. Login to get token
response = requests.post(
    "http://localhost:8000/token",
    data={"username": "alice", "password": "secret"}
)
token = response.json()["access_token"]

# 2. Use token for authenticated requests
headers = {"Authorization": f"Bearer {token}"}
response = requests.get("http://localhost:8000/users/me", headers=headers)
print(response.json())
```

### Refresh Tokens

Access tokens should be short-lived. Use refresh tokens for long-term access:

```python
def create_refresh_token(data: dict):
    """Create long-lived refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=7)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@app.post("/token/refresh")
async def refresh_access_token(refresh_token: str):
    """Get new access token using refresh token"""
    payload = verify_token(refresh_token)

    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    # Create new access token
    access_token = create_access_token(data={"sub": payload.get("sub")})
    return {"access_token": access_token, "token_type": "bearer"}
```

## OAuth2 and OpenID Connect

### OAuth2 Overview

OAuth2 is an authorization framework that enables third-party applications to obtain limited access to a service.

**Use Cases:**
- "Login with Google"
- "Login with GitHub"
- Third-party app access

**Roles:**
1. **Resource Owner**: User
2. **Client**: Application requesting access
3. **Authorization Server**: Issues tokens
4. **Resource Server**: Hosts protected resources

**Flow:**

```
┌──────────┐                               ┌─────────────┐
│  Client  │                               │   Resource  │
│          │                               │    Owner    │
└────┬─────┘                               └──────┬──────┘
     │                                             │
     │  1. Authorization Request                   │
     │────────────────────────────────────────────>│
     │                                             │
     │  2. Authorization Grant                     │
     │<────────────────────────────────────────────│
     │                                             │
     │  3. Authorization Grant                     │
     │────────────────────────────>┌──────────────┴───┐
     │                             │  Authorization   │
     │  4. Access Token            │     Server       │
     │<────────────────────────────┤                  │
     │                             └──────────────────┘
     │  5. Access Token            ┌──────────────────┐
     │────────────────────────────>│   Resource       │
     │                             │    Server        │
     │  6. Protected Resource      │                  │
     │<────────────────────────────┤                  │
     │                             └──────────────────┘
```

### FastAPI OAuth2 Implementation

```python
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2AuthorizationCodeBearer

app = FastAPI()

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl="https://provider.com/oauth/authorize",
    tokenUrl="https://provider.com/oauth/token"
)

@app.get("/protected")
async def protected_route(token: str = Depends(oauth2_scheme)):
    # Verify token with provider
    user_info = verify_with_provider(token)
    return {"user": user_info}
```

### OpenID Connect

Extension of OAuth2 for authentication:

```python
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config

config = Config('.env')
oauth = OAuth(config)

oauth.register(
    name='google',
    client_id=config('GOOGLE_CLIENT_ID'),
    client_secret=config('GOOGLE_CLIENT_SECRET'),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

@app.get('/login/google')
async def login_google(request: Request):
    redirect_uri = request.url_for('auth_google')
    return await oauth.google.authorize_redirect(request, redirect_uri)

@app.get('/auth/google')
async def auth_google(request: Request):
    token = await oauth.google.authorize_access_token(request)
    user = await oauth.google.parse_id_token(request, token)
    return {"user": user}
```

## Password Security

### Never Store Plain Text Passwords

**Bad:**
```python
users = {
    "alice": {"password": "secret123"}  # NEVER DO THIS!
}
```

**Good:**
```python
users = {
    "alice": {"password_hash": "$2b$12$KIX..."}  # Hashed password
}
```

### Hashing vs Encryption

| Aspect | Hashing | Encryption |
|--------|---------|------------|
| Reversible | No | Yes |
| Purpose | Verify integrity | Protect data |
| Use Case | Passwords | Sensitive data |
| Algorithms | bcrypt, argon2 | AES, RSA |

### Using bcrypt

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Hash password
password = "user_password_123"
hashed = pwd_context.hash(password)
print(hashed)
# $2b$12$KIXl.W9T8qI9GqN3z2GKsOzp8qjZ6q...

# Verify password
is_correct = pwd_context.verify("user_password_123", hashed)
print(is_correct)  # True

is_correct = pwd_context.verify("wrong_password", hashed)
print(is_correct)  # False
```

### Password Requirements

```python
from pydantic import BaseModel, validator
import re

class UserCreate(BaseModel):
    username: str
    password: str

    @validator("password")
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain digit")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("Password must contain special character")
        return v
```

### Secure Password Reset

```python
import secrets
from datetime import datetime, timedelta

def create_password_reset_token(email: str) -> str:
    """Create secure password reset token"""
    token = secrets.token_urlsafe(32)

    # Store token with expiration
    reset_tokens[token] = {
        "email": email,
        "expires": datetime.utcnow() + timedelta(hours=1)
    }

    return token

@app.post("/password-reset/request")
async def request_password_reset(email: str):
    """Request password reset"""
    user = get_user_by_email(email)
    if not user:
        # Don't reveal if user exists
        return {"message": "If email exists, reset link will be sent"}

    token = create_password_reset_token(email)
    send_reset_email(email, token)

    return {"message": "If email exists, reset link will be sent"}

@app.post("/password-reset/confirm")
async def confirm_password_reset(token: str, new_password: str):
    """Reset password using token"""
    if token not in reset_tokens:
        raise HTTPException(status_code=400, detail="Invalid token")

    reset_info = reset_tokens[token]

    if datetime.utcnow() > reset_info["expires"]:
        raise HTTPException(status_code=400, detail="Token expired")

    # Update password
    update_user_password(reset_info["email"], new_password)

    # Invalidate token
    del reset_tokens[token]

    return {"message": "Password reset successful"}
```

## HTTPS and Transport Security

### Why HTTPS?

Without HTTPS:
- Passwords sent in plain text
- API keys visible to attackers
- Data can be modified in transit
- No server authentication

With HTTPS:
- Encrypted communication
- Data integrity
- Server authentication
- Client trust

### TLS/SSL Certificates

**Development (self-signed):**
```bash
# Generate self-signed certificate
openssl req -x509 -newkey rsa:4096 -nodes \
  -out cert.pem -keyout key.pem -days 365
```

**Production:**
Use Let's Encrypt (free) or commercial CA.

### Running FastAPI with HTTPS

```python
# Using uvicorn with SSL
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=443,
        ssl_keyfile="./key.pem",
        ssl_certfile="./cert.pem"
    )
```

Or via command line:
```bash
uvicorn main:app --ssl-keyfile=./key.pem --ssl-certfile=./cert.pem
```

### Force HTTPS

```python
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse

app = FastAPI()

@app.middleware("http")
async def force_https(request: Request, call_next):
    if request.url.scheme != "https" and not request.url.hostname in ["localhost", "127.0.0.1"]:
        url = request.url.replace(scheme="https")
        return RedirectResponse(url, status_code=301)
    return await call_next(request)
```

### Security Headers

```python
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware

# Enforce HTTPS
app.add_middleware(HTTPSRedirectMiddleware)

# Limit allowed hosts
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["example.com", "*.example.com"]
)
```

## CORS (Cross-Origin Resource Sharing)

### What is CORS?

Security feature that restricts which origins can access your API.

**Scenario:**
- Your API: `https://api.example.com`
- Frontend: `https://app.example.com`
- Different origin (different subdomain)

Without CORS configuration, the browser blocks the request.

### CORS Headers

```http
Access-Control-Allow-Origin: https://app.example.com
Access-Control-Allow-Methods: GET, POST, PUT, DELETE
Access-Control-Allow-Headers: Content-Type, Authorization
Access-Control-Max-Age: 3600
```

### Implementing CORS in FastAPI

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://app.example.com",
        "https://dashboard.example.com"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", "Authorization"],
)
```

### Development Configuration

```python
# WARNING: Only for development!
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Production Configuration

```python
import os

# Load allowed origins from environment
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-API-Key"],
    max_age=3600,
)
```

## Rate Limiting and Throttling

### Why Rate Limiting?

- Prevent abuse and DoS attacks
- Ensure fair resource allocation
- Protect infrastructure from overload
- Monetization (tier-based limits)

### Strategies

1. **Fixed Window**: X requests per time window
2. **Sliding Window**: More precise than fixed
3. **Token Bucket**: Allows bursts
4. **Leaky Bucket**: Smooths traffic

### Implementation with SlowAPI

```bash
pip install slowapi
```

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import FastAPI, Request

app = FastAPI()

# Initialize limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Apply rate limit to endpoint
@app.post("/predict")
@limiter.limit("10/minute")
async def predict(request: Request, input_data: PredictionInput):
    return {"prediction": "result"}

# Different limits for different endpoints
@app.get("/expensive-operation")
@limiter.limit("2/minute")
async def expensive_operation(request: Request):
    return {"status": "processing"}

# Multiple limits
@app.get("/api/data")
@limiter.limit("100/hour")
@limiter.limit("1000/day")
async def get_data(request: Request):
    return {"data": []}
```

### User-Based Rate Limiting

```python
def get_user_id(request: Request) -> str:
    """Extract user ID from request"""
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if token:
        payload = verify_token(token)
        return payload.get("sub", "anonymous")
    return "anonymous"

limiter = Limiter(key_func=get_user_id)

@app.post("/predict")
@limiter.limit("100/minute")  # Per user, not per IP
async def predict(request: Request, input_data: PredictionInput):
    return {"prediction": "result"}
```

### Custom Rate Limits Based on User Tier

```python
from functools import wraps

def get_user_rate_limit(user: User) -> str:
    """Get rate limit based on user tier"""
    limits = {
        "free": "10/minute",
        "pro": "100/minute",
        "enterprise": "1000/minute"
    }
    return limits.get(user.tier, "10/minute")

@app.post("/predict")
async def predict(
    request: Request,
    input_data: PredictionInput,
    current_user: User = Depends(get_current_user)
):
    # Apply custom limit
    limit = get_user_rate_limit(current_user)
    # Use custom limiter logic
    return {"prediction": "result"}
```

### Rate Limit Headers

Include rate limit information in responses:

```python
from fastapi import Response

@app.get("/api/data")
async def get_data(response: Response):
    # Add rate limit headers
    response.headers["X-RateLimit-Limit"] = "100"
    response.headers["X-RateLimit-Remaining"] = "95"
    response.headers["X-RateLimit-Reset"] = "1634567890"

    return {"data": []}
```

## Input Validation and Sanitization

### SQL Injection Prevention

**Bad (vulnerable):**
```python
# NEVER DO THIS!
query = f"SELECT * FROM users WHERE username = '{username}'"
db.execute(query)
```

**Good (parameterized queries):**
```python
query = "SELECT * FROM users WHERE username = ?"
db.execute(query, (username,))
```

### XSS (Cross-Site Scripting) Prevention

```python
from markupsafe import escape

@app.post("/comments")
async def create_comment(comment: str):
    # Escape HTML
    safe_comment = escape(comment)
    db.save_comment(safe_comment)
    return {"comment": safe_comment}
```

### Command Injection Prevention

```python
import subprocess
import shlex

# Bad
filename = user_input
subprocess.run(f"cat {filename}", shell=True)  # DANGEROUS!

# Good
filename = shlex.quote(user_input)
subprocess.run(["cat", filename])  # Safe
```

### Path Traversal Prevention

```python
from pathlib import Path

@app.get("/files/{filename}")
async def get_file(filename: str):
    # Prevent path traversal
    base_dir = Path("/safe/directory")
    file_path = (base_dir / filename).resolve()

    # Ensure file is within base directory
    if not file_path.is_relative_to(base_dir):
        raise HTTPException(status_code=400, detail="Invalid file path")

    return FileResponse(file_path)
```

### Pydantic Validation

```python
from pydantic import BaseModel, validator, constr, conint
from typing import List

class ModelConfig(BaseModel):
    name: constr(min_length=1, max_length=100, regex="^[a-zA-Z0-9-_]+$")
    batch_size: conint(ge=1, le=128)
    tags: List[constr(max_length=50)]

    @validator("tags")
    def validate_tags(cls, v):
        if len(v) > 10:
            raise ValueError("Maximum 10 tags allowed")
        return v
```

## Security Headers

### Important Security Headers

```python
from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)

        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"

        # XSS protection
        response.headers["X-Content-Type-Options"] = "nosniff"

        # Control referrer information
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Content Security Policy
        response.headers["Content-Security-Policy"] = "default-src 'self'"

        # Strict Transport Security (HTTPS only)
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        # Permissions Policy
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=()"

        return response

app = FastAPI()
app.add_middleware(SecurityHeadersMiddleware)
```

## Security for ML APIs

### Model Security

**1. Model File Protection:**
```python
import os
from pathlib import Path

MODEL_DIR = Path("/secure/models")

def load_model(model_id: str):
    # Validate model ID
    if not model_id.isalnum():
        raise ValueError("Invalid model ID")

    model_path = MODEL_DIR / f"{model_id}.pkl"

    # Check file exists and is within allowed directory
    if not model_path.is_file() or not model_path.is_relative_to(MODEL_DIR):
        raise FileNotFoundError("Model not found")

    # Set restrictive permissions (owner read/write only)
    os.chmod(model_path, 0o600)

    return pickle.load(open(model_path, "rb"))
```

**2. Input Validation for ML Models:**
```python
from pydantic import BaseModel, validator
import numpy as np

class ImagePredictionInput(BaseModel):
    image_data: str  # Base64 encoded
    max_size_mb: int = 10

    @validator("image_data")
    def validate_image(cls, v):
        import base64

        try:
            decoded = base64.b64decode(v)
        except Exception:
            raise ValueError("Invalid base64 encoding")

        # Check size
        size_mb = len(decoded) / (1024 * 1024)
        if size_mb > cls.max_size_mb:
            raise ValueError(f"Image too large: {size_mb:.2f}MB > {cls.max_size_mb}MB")

        return v
```

**3. Resource Limits:**
```python
from contextlib import contextmanager
import signal

@contextmanager
def time_limit(seconds: int):
    """Context manager to limit execution time"""
    def signal_handler(signum, frame):
        raise TimeoutError("Prediction timed out")

    signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)

@app.post("/predict")
async def predict(input_data: PredictionInput):
    try:
        with time_limit(5):  # 5 second timeout
            prediction = model.predict(input_data.features)
            return {"prediction": prediction}
    except TimeoutError:
        raise HTTPException(status_code=504, detail="Prediction timeout")
```

**4. Adversarial Input Detection:**
```python
def detect_adversarial_input(input_data: np.ndarray) -> bool:
    """Basic adversarial input detection"""
    # Check for extreme values
    if np.any(np.abs(input_data) > 1000):
        return True

    # Check for NaN or Inf
    if np.any(~np.isfinite(input_data)):
        return True

    return False

@app.post("/predict")
async def predict(input_data: PredictionInput):
    features = np.array(input_data.features)

    if detect_adversarial_input(features):
        raise HTTPException(status_code=400, detail="Invalid input detected")

    return model.predict(features)
```

### Data Privacy

**1. PII Protection:**
```python
import re

def mask_pii(text: str) -> str:
    """Mask personally identifiable information"""
    # Email
    text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', text)

    # Phone
    text = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[PHONE]', text)

    # SSN
    text = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '[SSN]', text)

    return text

@app.post("/analyze")
async def analyze_text(text: str):
    # Mask PII before logging or processing
    safe_text = mask_pii(text)
    logger.info(f"Processing: {safe_text}")

    return {"result": "processed"}
```

**2. Audit Logging:**
```python
import logging
from datetime import datetime

audit_logger = logging.getLogger("audit")

@app.post("/predict")
async def predict(
    input_data: PredictionInput,
    current_user: User = Depends(get_current_user)
):
    # Log access
    audit_logger.info({
        "timestamp": datetime.utcnow().isoformat(),
        "user": current_user.username,
        "action": "prediction",
        "model": "bert-base",
        "ip": request.client.host
    })

    return model.predict(input_data.features)
```

## Best Practices and Checklists

### Security Checklist

**Authentication & Authorization:**
- [ ] Use HTTPS for all endpoints
- [ ] Implement proper authentication (JWT, OAuth2)
- [ ] Hash passwords with bcrypt or argon2
- [ ] Implement role-based access control
- [ ] Use API keys for service-to-service communication
- [ ] Implement token expiration and refresh

**Input Validation:**
- [ ] Validate all inputs with Pydantic
- [ ] Sanitize user inputs
- [ ] Implement file upload restrictions
- [ ] Check for SQL injection vulnerabilities
- [ ] Prevent command injection
- [ ] Protect against path traversal

**Rate Limiting:**
- [ ] Implement rate limiting per user/IP
- [ ] Set appropriate limits for each endpoint
- [ ] Return rate limit headers
- [ ] Handle rate limit exceeded gracefully

**Headers & CORS:**
- [ ] Configure CORS properly
- [ ] Set security headers
- [ ] Implement CSP policy
- [ ] Use HSTS for HTTPS enforcement

**Monitoring & Logging:**
- [ ] Log authentication attempts
- [ ] Log authorization failures
- [ ] Monitor for suspicious activity
- [ ] Set up alerts for security events
- [ ] Implement audit logging

**Dependencies:**
- [ ] Keep dependencies updated
- [ ] Scan for vulnerabilities
- [ ] Use verified packages only
- [ ] Pin dependency versions

**ML-Specific:**
- [ ] Validate model inputs
- [ ] Implement resource limits
- [ ] Protect model files
- [ ] Handle adversarial inputs
- [ ] Mask PII in logs

## Summary and Key Takeaways

### Core Concepts

1. **Authentication vs Authorization**
   - Authentication: Who are you?
   - Authorization: What can you do?

2. **Authentication Methods**
   - API Keys: Simple, stateless
   - JWT: Self-contained tokens
   - OAuth2: Third-party access

3. **Security Fundamentals**
   - HTTPS everywhere
   - Hash passwords, never store plain text
   - Validate all inputs
   - Implement rate limiting
   - Set security headers

4. **ML-Specific Security**
   - Validate model inputs
   - Protect model files
   - Implement timeouts
   - Mask PII data
   - Audit logging

### Implementation Priorities

1. **Must Have (P0):**
   - HTTPS/TLS
   - Authentication
   - Input validation
   - Password hashing

2. **Should Have (P1):**
   - Rate limiting
   - Security headers
   - CORS configuration
   - Audit logging

3. **Nice to Have (P2):**
   - OAuth2 integration
   - Advanced monitoring
   - Anomaly detection

### Next Steps

- Complete Exercise 02: Implement authentication system
- Review OWASP Top 10 API Security Risks
- Practice implementing security features
- Learn about security testing and penetration testing

### Resources

- [OWASP API Security Top 10](https://owasp.org/www-project-api-security/)
- [FastAPI Security Documentation](https://fastapi.tiangolo.com/tutorial/security/)
- [JWT.io](https://jwt.io/)
- [OAuth 2.0 Simplified](https://www.oauth.com/)

---

**Estimated Study Time**: 4-5 hours
**Hands-on Practice**: Complete Exercise 02: Authentication & Security
**Assessment**: Quiz covers authentication, authorization, and security best practices
