# Exercise 02: ML Model Serving API with Authentication

## Overview

Build a production-ready ML model serving API that loads actual machine learning models and makes predictions. This exercise adds JWT authentication, proper model loading, and inference capabilities to your REST API skills.

**Difficulty:** Intermediate
**Estimated Time:** 3-4 hours
**Prerequisites:**
- Exercise 01 completed
- Lecture 02: FastAPI Framework
- Lecture 03: Authentication & Security
- Basic understanding of scikit-learn or PyTorch

## Learning Objectives

By completing this exercise, you will:
- Load and serve real ML models
- Implement JWT-based authentication
- Create secure prediction endpoints
- Handle model inference efficiently
- Implement proper error handling for ML operations
- Use dependency injection for model loading
- Write tests for authenticated endpoints

## Scenario

You're building an API that serves a pre-trained sentiment analysis model. The API should:
- Authenticate users with JWT tokens
- Load the ML model once at startup
- Provide prediction endpoints (single and batch)
- Track prediction statistics
- Handle errors gracefully

## Project Setup

### 1. Install Additional Dependencies

```bash
pip install python-jose[cryptography]
pip install passlib[bcrypt]
pip install python-multipart
pip install scikit-learn
pip install numpy
```

### 2. Project Structure

```
ml-serving-api/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── auth.py
│   ├── models.py
│   ├── ml_service.py
│   └── config.py
├── models/
│   └── sentiment_model.pkl
├── tests/
│   ├── __init__.py
│   └── test_api.py
├── scripts/
│   └── train_model.py
├── requirements.txt
└── .env
```

## Part 1: Train a Simple Model

First, create a simple sentiment analysis model for testing.

**File: scripts/train_model.py**

```python
"""
Train a simple sentiment analysis model for the API
"""
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
import pickle
import os

# TODO: Create training data
# Sample positive and negative movie reviews
positive_reviews = [
    "This movie was amazing! I loved every minute.",
    "Excellent film with great acting and plot.",
    "One of the best movies I've seen this year.",
    "Fantastic! Highly recommend this movie.",
    "Brilliant performances and wonderful story.",
]

negative_reviews = [
    "Terrible movie, waste of time.",
    "Very disappointing and boring.",
    "Poor acting and weak storyline.",
    "I didn't enjoy this film at all.",
    "One of the worst movies I've ever watched.",
]

# TODO: Combine reviews and create labels
# X = positive_reviews + negative_reviews
# y = ['positive'] * len(positive_reviews) + ['negative'] * len(negative_reviews)

# TODO: Create pipeline with TfidfVectorizer and MultinomialNB
# pipeline = Pipeline([...])

# TODO: Train the model
# pipeline.fit(X, y)

# TODO: Test the model
# test_texts = ["This was great!", "Really bad movie"]
# predictions = pipeline.predict(test_texts)
# print(predictions)

# TODO: Save model to file
# os.makedirs('models', exist_ok=True)
# with open('models/sentiment_model.pkl', 'wb') as f:
#     pickle.dump(pipeline, f)

print("Model trained and saved successfully!")
```

**Run the training script:**
```bash
python scripts/train_model.py
```

## Part 2: Configuration Management

**File: app/config.py**

```python
from pydantic import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Application settings"""

    # TODO: Define settings
    # app_name: str = "ML Serving API"
    # secret_key: str (for JWT signing)
    # algorithm: str = "HS256"
    # access_token_expire_minutes: int = 30
    # model_path: str = "models/sentiment_model.pkl"

    class Config:
        env_file = ".env"

settings = Settings()
```

**File: .env**

```bash
SECRET_KEY=your-secret-key-change-this-in-production
```

## Part 3: Implement Authentication

**File: app/auth.py**

```python
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from app.config import settings

# TODO: Initialize password context
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# TODO: Initialize OAuth2 scheme
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class User(BaseModel):
    username: str
    email: str
    disabled: bool = False

class UserInDB(User):
    hashed_password: str

# TODO: Mock user database
# In production, use real database
fake_users_db = {
    "alice": {
        "username": "alice",
        "email": "alice@example.com",
        "hashed_password": "$2b$12$...",  # Hash of "secret123"
        "disabled": False,
    }
}

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    # TODO: Use pwd_context.verify()
    pass

def get_password_hash(password: str) -> str:
    """Hash a password"""
    # TODO: Use pwd_context.hash()
    pass

def get_user(username: str) -> Optional[UserInDB]:
    """Get user from database"""
    # TODO: Look up user in fake_users_db
    # TODO: Return UserInDB if found, None otherwise
    pass

def authenticate_user(username: str, password: str) -> Optional[UserInDB]:
    """Authenticate a user"""
    # TODO: Get user from database
    # TODO: Verify password
    # TODO: Return user if authenticated, None otherwise
    pass

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    # TODO: Copy data
    # TODO: Add expiration time
    # TODO: Encode JWT with secret key
    # TODO: Return encoded token
    pass

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Get current user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # TODO: Decode JWT token
    # TODO: Extract username from payload
    # TODO: Get user from database
    # TODO: Raise exception if invalid
    # TODO: Return user
    pass

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Ensure user is active"""
    # TODO: Check if user is disabled
    # TODO: Raise exception if disabled
    # TODO: Return user
    pass
```

## Part 4: Create ML Service

**File: app/ml_service.py**

```python
import pickle
import numpy as np
from typing import List, Dict
from datetime import datetime
from app.config import settings

class MLModelService:
    """Service for loading and running ML model"""

    def __init__(self):
        self.model = None
        self.model_loaded = False
        self.prediction_count = 0
        self.model_info = {
            "name": "Sentiment Analysis Model",
            "version": "1.0.0",
            "framework": "scikit-learn"
        }

    def load_model(self):
        """Load ML model from file"""
        # TODO: Open model file
        # TODO: Load model with pickle
        # TODO: Set model_loaded to True
        # TODO: Handle errors (file not found, corrupt file, etc.)
        pass

    def predict(self, text: str) -> Dict:
        """Make prediction on single text"""
        # TODO: Check if model is loaded
        # TODO: Make prediction
        # TODO: Get prediction probabilities if available
        # TODO: Increment prediction_count
        # TODO: Return result dictionary with:
        #   - prediction: str
        #   - confidence: float (optional)
        #   - timestamp: datetime
        pass

    def predict_batch(self, texts: List[str]) -> List[Dict]:
        """Make predictions on batch of texts"""
        # TODO: Check if model is loaded
        # TODO: Make batch prediction
        # TODO: Return list of results
        pass

    def get_stats(self) -> Dict:
        """Get model statistics"""
        # TODO: Return dictionary with:
        #   - model_loaded: bool
        #   - total_predictions: int
        #   - model_info: dict
        pass

# Create global instance
ml_service = MLModelService()
```

## Part 5: Define API Models

**File: app/models.py**

```python
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class PredictionInput(BaseModel):
    """Input for single prediction"""
    text: str = Field(..., min_length=1, max_length=5000)

    class Config:
        schema_extra = {
            "example": {
                "text": "This movie was absolutely fantastic!"
            }
        }

class PredictionOutput(BaseModel):
    """Output for single prediction"""
    # TODO: Define fields:
    # - text: str (original input)
    # - prediction: str (positive/negative)
    # - confidence: Optional[float]
    # - timestamp: datetime
    # - model_version: str
    pass

class BatchPredictionInput(BaseModel):
    """Input for batch prediction"""
    # TODO: Define field:
    # - texts: List[str] with validation (max 100 items)
    pass

class BatchPredictionOutput(BaseModel):
    """Output for batch prediction"""
    # TODO: Define fields:
    # - results: List[PredictionOutput]
    # - total_count: int
    # - processing_time_ms: float
    pass

class ModelStats(BaseModel):
    """Model statistics"""
    # TODO: Define fields:
    # - model_loaded: bool
    # - total_predictions: int
    # - model_name: str
    # - model_version: str
    # - framework: str
    pass
```

## Part 6: Create API Endpoints

**File: app/main.py**

```python
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from typing import List
import time

from app.config import settings
from app.auth import (
    authenticate_user, create_access_token,
    get_current_active_user, Token, User
)
from app.models import (
    PredictionInput, PredictionOutput,
    BatchPredictionInput, BatchPredictionOutput,
    ModelStats
)
from app.ml_service import ml_service

# TODO: Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="ML Model Serving API with Authentication"
)

@app.on_event("startup")
async def startup_event():
    """Load ML model on startup"""
    # TODO: Load model using ml_service.load_model()
    # TODO: Log success/failure
    pass

@app.get("/")
def root():
    """Root endpoint"""
    # TODO: Return welcome message and API info
    pass

@app.get("/health")
def health_check():
    """Health check endpoint"""
    # TODO: Return health status and model loaded status
    pass

@app.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login endpoint to get JWT token"""
    # TODO: Authenticate user
    # TODO: If authentication fails, raise 401 HTTPException
    # TODO: Create access token with expiration
    # TODO: Return token
    pass

@app.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """Get current user profile"""
    # TODO: Return current user
    pass

@app.post("/api/v1/predict", response_model=PredictionOutput)
async def predict(
    input_data: PredictionInput,
    current_user: User = Depends(get_current_active_user)
):
    """Make single prediction (authenticated)"""
    # TODO: Call ml_service.predict()
    # TODO: Handle errors (model not loaded, prediction failed)
    # TODO: Return prediction result
    pass

@app.post("/api/v1/predict/batch", response_model=BatchPredictionOutput)
async def predict_batch(
    input_data: BatchPredictionInput,
    current_user: User = Depends(get_current_active_user)
):
    """Make batch predictions (authenticated)"""
    # TODO: Record start time
    # TODO: Call ml_service.predict_batch()
    # TODO: Calculate processing time
    # TODO: Return batch results with timing
    pass

@app.get("/api/v1/model/stats", response_model=ModelStats)
async def get_model_stats(current_user: User = Depends(get_current_active_user)):
    """Get model statistics (authenticated)"""
    # TODO: Call ml_service.get_stats()
    # TODO: Return stats
    pass
```

## Part 7: Write Tests

**File: tests/test_api.py**

```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def get_auth_token() -> str:
    """Helper: Get authentication token"""
    # TODO: Login with test credentials
    # TODO: Extract and return access token
    pass

def test_root():
    """Test root endpoint"""
    # TODO: Make GET request to /
    # TODO: Assert status 200
    pass

def test_health_check():
    """Test health endpoint"""
    # TODO: Make GET request to /health
    # TODO: Assert status 200
    # TODO: Assert model_loaded is True
    pass

def test_login_success():
    """Test successful login"""
    # TODO: POST to /token with valid credentials
    # TODO: Assert status 200
    # TODO: Assert access_token in response
    # TODO: Assert token_type is "bearer"
    pass

def test_login_failure():
    """Test failed login"""
    # TODO: POST to /token with invalid credentials
    # TODO: Assert status 401
    pass

def test_predict_without_auth():
    """Test prediction without authentication"""
    # TODO: POST to /api/v1/predict without token
    # TODO: Assert status 401
    pass

def test_predict_with_auth():
    """Test prediction with authentication"""
    # TODO: Get auth token
    # TODO: POST to /api/v1/predict with token
    # TODO: Assert status 200
    # TODO: Assert prediction is "positive" or "negative"
    pass

def test_predict_positive_sentiment():
    """Test positive sentiment prediction"""
    # TODO: Get auth token
    # TODO: Predict with positive text
    # TODO: Assert prediction is "positive"
    pass

def test_predict_negative_sentiment():
    """Test negative sentiment prediction"""
    # TODO: Get auth token
    # TODO: Predict with negative text
    # TODO: Assert prediction is "negative"
    pass

def test_batch_predict():
    """Test batch prediction"""
    # TODO: Get auth token
    # TODO: POST to /api/v1/predict/batch with multiple texts
    # TODO: Assert status 200
    # TODO: Assert correct number of results
    # TODO: Assert processing_time_ms is present
    pass

def test_model_stats():
    """Test model statistics"""
    # TODO: Get auth token
    # TODO: GET /api/v1/model/stats
    # TODO: Assert status 200
    # TODO: Assert model_loaded is True
    # TODO: Assert total_predictions >= 0
    pass

def test_get_current_user():
    """Test getting current user profile"""
    # TODO: Get auth token
    # TODO: GET /users/me
    # TODO: Assert status 200
    # TODO: Assert username matches
    pass
```

## Part 8: Run and Test

### 1. Train the Model

```bash
python scripts/train_model.py
```

### 2. Run the API

```bash
uvicorn app.main:app --reload
```

### 3. Test Authentication Flow

**Get Token:**
```bash
curl -X POST "http://localhost:8000/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=alice&password=secret123"
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Make Prediction:**
```bash
curl -X POST "http://localhost:8000/api/v1/predict" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"text": "This movie was absolutely fantastic!"}'
```

**Batch Prediction:**
```bash
curl -X POST "http://localhost:8000/api/v1/predict/batch" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "texts": [
      "Great movie!",
      "Terrible film.",
      "Amazing experience!"
    ]
  }'
```

### 4. Run Tests

```bash
pytest tests/ -v
```

## Challenges and Extensions

### Challenge 1: User Registration

Add endpoint to register new users:
```python
@app.post("/register")
async def register_user(username: str, password: str, email: str):
    # Validate input
    # Hash password
    # Store user
    # Return success message
    pass
```

### Challenge 2: Model Versioning

Support multiple model versions:
```python
@app.post("/api/v1/predict")
async def predict(
    input_data: PredictionInput,
    model_version: str = "1.0.0",
    current_user: User = Depends(get_current_active_user)
):
    # Load specific model version
    # Make prediction
    pass
```

### Challenge 3: Prediction History

Store prediction history for analytics:
```python
class PredictionHistory:
    def __init__(self):
        self.history = []

    def add(self, user: str, input: str, prediction: str):
        self.history.append({
            "user": user,
            "input": input,
            "prediction": prediction,
            "timestamp": datetime.utcnow()
        })

@app.get("/api/v1/predictions/history")
async def get_prediction_history(
    current_user: User = Depends(get_current_active_user)
):
    # Return user's prediction history
    pass
```

### Challenge 4: Model Metrics

Add endpoint for model performance metrics:
```python
@app.get("/api/v1/model/metrics")
async def get_model_metrics():
    return {
        "accuracy": 0.92,
        "precision": 0.90,
        "recall": 0.94,
        "f1_score": 0.92
    }
```

### Challenge 5: Async Predictions

Use async/await for better performance:
```python
@app.post("/api/v1/predict")
async def predict_async(
    input_data: PredictionInput,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user)
):
    # Make prediction asynchronously
    # Log to database in background
    pass
```

## Common Issues and Solutions

### Issue 1: Model Not Loading

**Problem:** Model file not found or corrupt

**Solution:**
- Check model path in config
- Verify model file exists: `ls -l models/`
- Re-run training script

### Issue 2: JWT Token Errors

**Problem:** "Could not validate credentials"

**Solution:**
- Check SECRET_KEY in .env
- Verify token is passed in Authorization header
- Check token hasn't expired

### Issue 3: Authentication Always Fails

**Problem:** Password verification fails

**Solution:**
- Generate proper password hash:
  ```python
  from passlib.context import CryptContext
  pwd_context = CryptContext(schemes=["bcrypt"])
  print(pwd_context.hash("secret123"))
  ```
- Update hash in fake_users_db

## Deliverables

- ✅ Working ML model serving API
- ✅ JWT authentication implementation
- ✅ Single and batch prediction endpoints
- ✅ Model statistics tracking
- ✅ Comprehensive test suite
- ✅ Documentation and usage examples

## Key Takeaways

1. **Authentication:** JWT tokens for stateless authentication
2. **Model Loading:** Load models once at startup for efficiency
3. **Dependency Injection:** Use for model and user management
4. **Error Handling:** Graceful degradation when model fails
5. **Testing:** Test both authenticated and unauthenticated scenarios

## Next Steps

- Exercise 03: Add rate limiting and advanced security
- Exercise 04: Deploy API with Docker
- Exercise 05: Add monitoring and logging

---

**Estimated Time:** 3-4 hours
**Difficulty:** Intermediate
**Focus:** ML model serving, JWT authentication, production patterns
