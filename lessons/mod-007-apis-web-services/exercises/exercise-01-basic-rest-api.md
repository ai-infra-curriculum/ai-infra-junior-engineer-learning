# Exercise 01: Build a Basic REST API

## Overview

In this exercise, you'll build a basic REST API for managing ML models metadata using FastAPI. This exercise reinforces the fundamental concepts of REST architecture, HTTP methods, status codes, and FastAPI basics.

**Difficulty:** Beginner
**Estimated Time:** 2-3 hours
**Prerequisites:**
- Lecture 01: API Fundamentals & REST
- Lecture 02: FastAPI Framework
- Python 3.7+ installed
- Basic Python knowledge

## Learning Objectives

By completing this exercise, you will:
- Set up a FastAPI project from scratch
- Implement CRUD operations following REST principles
- Use proper HTTP methods and status codes
- Define Pydantic models for request/response validation
- Handle errors gracefully
- Test your API using interactive documentation
- Understand RESTful resource design

## Scenario

You're building a simple model registry API that allows users to:
- List all registered ML models
- Get details about a specific model
- Register a new model
- Update model information
- Delete a model
- Search/filter models by framework or status

## Project Setup

### 1. Create Project Directory

```bash
mkdir ml-model-registry
cd ml-model-registry
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install fastapi uvicorn pydantic
pip install pytest httpx  # For testing
```

### 4. Create Project Structure

```
ml-model-registry/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── models.py
│   └── database.py
├── tests/
│   ├── __init__.py
│   └── test_api.py
├── requirements.txt
└── README.md
```

## Part 1: Define Data Models

**File: app/models.py**

Create Pydantic models to represent your data:

```python
from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime
from enum import Enum

# TODO: Define ModelFramework enum
# Hint: Should include pytorch, tensorflow, sklearn, xgboost

# TODO: Define ModelStatus enum
# Hint: Should include training, ready, deployed, archived

# TODO: Create Model class (BaseModel)
# Required fields:
#   - id: str (unique identifier)
#   - name: str (model name)
#   - framework: ModelFramework
#   - version: str (semantic version, default "1.0.0")
#   - status: ModelStatus (default "ready")
#   - created_at: datetime
#   - updated_at: datetime
# Optional fields:
#   - description: Optional[str]
#   - accuracy: Optional[float] (range 0-1)
#   - tags: List[str] (default empty list)
#   - model_size_mb: Optional[float]

# TODO: Create ModelCreate class (BaseModel)
# This is what users send when creating a model
# Should NOT include: id, created_at, updated_at (server generates these)

# TODO: Create ModelUpdate class (BaseModel)
# All fields should be optional (for partial updates)
# Should NOT include: id, created_at (these can't be changed)

# TODO: Add Config class with example for documentation
```

**What You'll Learn:**
- How to use Pydantic for data validation
- Difference between request and response models
- Using Enums for constrained values
- Field validation with constraints

## Part 2: Implement In-Memory Database

**File: app/database.py**

Implement a simple in-memory database (Python dictionary):

```python
from typing import Dict, List, Optional
from app.models import Model
from datetime import datetime
import uuid

# TODO: Create a global dictionary to store models
# Key: model_id (str)
# Value: Model object

class ModelDB:
    """In-memory database for models"""

    def __init__(self):
        # TODO: Initialize empty models dictionary
        pass

    def create_model(self, model_data: dict) -> Model:
        """Create a new model"""
        # TODO: Generate unique ID using uuid.uuid4()
        # TODO: Add created_at and updated_at timestamps
        # TODO: Create Model object
        # TODO: Store in dictionary
        # TODO: Return the created model
        pass

    def get_model(self, model_id: str) -> Optional[Model]:
        """Get a model by ID"""
        # TODO: Return model if exists, None otherwise
        pass

    def get_all_models(self,
                       skip: int = 0,
                       limit: int = 100,
                       framework: Optional[str] = None,
                       status: Optional[str] = None) -> List[Model]:
        """Get all models with optional filtering"""
        # TODO: Get all models from dictionary
        # TODO: Filter by framework if provided
        # TODO: Filter by status if provided
        # TODO: Apply pagination (skip, limit)
        # TODO: Return list of models
        pass

    def update_model(self, model_id: str, update_data: dict) -> Optional[Model]:
        """Update a model"""
        # TODO: Check if model exists
        # TODO: Update fields that are provided
        # TODO: Update updated_at timestamp
        # TODO: Return updated model
        pass

    def delete_model(self, model_id: str) -> bool:
        """Delete a model"""
        # TODO: Check if model exists
        # TODO: Delete from dictionary
        # TODO: Return True if deleted, False if not found
        pass

    def model_exists(self, model_id: str) -> bool:
        """Check if model exists"""
        # TODO: Return True if model_id in dictionary
        pass

# Create global database instance
db = ModelDB()
```

**What You'll Learn:**
- CRUD operations implementation
- Data filtering and pagination
- Handling optional parameters

## Part 3: Create API Endpoints

**File: app/main.py**

Implement the REST API endpoints:

```python
from fastapi import FastAPI, HTTPException, status, Query
from typing import List, Optional
from app.models import Model, ModelCreate, ModelUpdate
from app.database import db

# TODO: Create FastAPI app instance with title and version
app = FastAPI(
    title="ML Model Registry API",
    version="1.0.0",
    description="API for managing ML model metadata"
)

# TODO: Implement GET / endpoint
# Return welcome message and API info
@app.get("/")
def root():
    pass

# TODO: Implement GET /health endpoint
# Return health status of the API
@app.get("/health")
def health_check():
    pass

# TODO: Implement GET /api/v1/models endpoint
# Parameters: skip (default 0), limit (default 100), framework (optional), status (optional)
# Return: List of models
# Response model: List[Model]
@app.get("/api/v1/models", response_model=List[Model])
def list_models(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    framework: Optional[str] = Query(None, description="Filter by framework"),
    status: Optional[str] = Query(None, description="Filter by status")
):
    # TODO: Call db.get_all_models() with parameters
    # TODO: Return results
    pass

# TODO: Implement POST /api/v1/models endpoint
# Body: ModelCreate
# Return: Created model with 201 status
# Response model: Model
@app.post("/api/v1/models", response_model=Model, status_code=status.HTTP_201_CREATED)
def create_model(model: ModelCreate):
    # TODO: Call db.create_model() with model data
    # TODO: Return created model
    pass

# TODO: Implement GET /api/v1/models/{model_id} endpoint
# Return: Model details
# Response model: Model
# Errors: 404 if not found
@app.get("/api/v1/models/{model_id}", response_model=Model)
def get_model(model_id: str):
    # TODO: Call db.get_model()
    # TODO: If not found, raise HTTPException with 404
    # TODO: Return model
    pass

# TODO: Implement PUT /api/v1/models/{model_id} endpoint
# Body: ModelUpdate
# Return: Updated model
# Response model: Model
# Errors: 404 if not found
@app.put("/api/v1/models/{model_id}", response_model=Model)
def update_model(model_id: str, model_update: ModelUpdate):
    # TODO: Check if model exists using db.model_exists()
    # TODO: If not found, raise HTTPException with 404
    # TODO: Call db.update_model() with non-null fields from model_update
    # TODO: Return updated model
    pass

# TODO: Implement DELETE /api/v1/models/{model_id} endpoint
# Return: 204 No Content on success
# Errors: 404 if not found
@app.delete("/api/v1/models/{model_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_model(model_id: str):
    # TODO: Call db.delete_model()
    # TODO: If not found, raise HTTPException with 404
    # TODO: Return None (204 has no response body)
    pass

# TODO: Implement GET /api/v1/models/search endpoint
# Query parameter: q (search term)
# Search in model name, description, and tags
@app.get("/api/v1/models/search", response_model=List[Model])
def search_models(q: str = Query(..., min_length=1, description="Search query")):
    # TODO: Get all models
    # TODO: Filter models where q appears in name, description, or tags
    # TODO: Return matching models
    pass
```

**What You'll Learn:**
- Defining path operations with proper HTTP methods
- Using path parameters and query parameters
- Request body validation with Pydantic
- Setting proper status codes
- Error handling with HTTPException
- Response model specification

## Part 4: Run and Test Your API

### 1. Run the Server

```bash
uvicorn app.main:app --reload
```

Expected output:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using watchfiles
```

### 2. Access Interactive Documentation

Open browser and go to:
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

### 3. Test Endpoints Using Swagger UI

**Create a Model:**
```json
POST /api/v1/models
{
  "name": "BERT Sentiment Classifier",
  "framework": "pytorch",
  "description": "Fine-tuned BERT for sentiment analysis",
  "version": "1.0.0",
  "accuracy": 0.94,
  "tags": ["nlp", "sentiment", "transformer"],
  "model_size_mb": 438.5
}
```

**List Models:**
```
GET /api/v1/models
GET /api/v1/models?framework=pytorch
GET /api/v1/models?status=ready&limit=10
```

**Get Specific Model:**
```
GET /api/v1/models/{model_id}
```

**Update Model:**
```json
PUT /api/v1/models/{model_id}
{
  "status": "deployed",
  "accuracy": 0.95
}
```

**Delete Model:**
```
DELETE /api/v1/models/{model_id}
```

**Search Models:**
```
GET /api/v1/models/search?q=bert
```

### 4. Test with curl

```bash
# Create model
curl -X POST "http://localhost:8000/api/v1/models" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "GPT-2 Text Generator",
    "framework": "pytorch",
    "version": "1.0.0",
    "tags": ["nlp", "generation"]
  }'

# List models
curl "http://localhost:8000/api/v1/models"

# Get specific model
curl "http://localhost:8000/api/v1/models/{model_id}"

# Update model
curl -X PUT "http://localhost:8000/api/v1/models/{model_id}" \
  -H "Content-Type: application/json" \
  -d '{"status": "deployed"}'

# Delete model
curl -X DELETE "http://localhost:8000/api/v1/models/{model_id}"
```

## Part 5: Write Tests

**File: tests/test_api.py**

```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root():
    """Test root endpoint"""
    # TODO: Make GET request to /
    # TODO: Assert status code is 200
    # TODO: Assert response contains expected message
    pass

def test_health_check():
    """Test health endpoint"""
    # TODO: Make GET request to /health
    # TODO: Assert status code is 200
    # TODO: Assert status is healthy
    pass

def test_create_model():
    """Test creating a model"""
    model_data = {
        "name": "Test Model",
        "framework": "pytorch",
        "version": "1.0.0",
        "tags": ["test"]
    }

    # TODO: Make POST request to /api/v1/models
    # TODO: Assert status code is 201
    # TODO: Assert response contains id
    # TODO: Assert name matches
    pass

def test_get_model():
    """Test getting a specific model"""
    # TODO: First create a model
    # TODO: Extract model_id from response
    # TODO: Make GET request to /api/v1/models/{model_id}
    # TODO: Assert status code is 200
    # TODO: Assert model data matches
    pass

def test_get_nonexistent_model():
    """Test getting a model that doesn't exist"""
    # TODO: Make GET request with invalid ID
    # TODO: Assert status code is 404
    pass

def test_list_models():
    """Test listing models"""
    # TODO: Create 2-3 models
    # TODO: Make GET request to /api/v1/models
    # TODO: Assert status code is 200
    # TODO: Assert response is a list
    # TODO: Assert list contains created models
    pass

def test_update_model():
    """Test updating a model"""
    # TODO: Create a model
    # TODO: Update the model with new data
    # TODO: Assert status code is 200
    # TODO: Assert updated_at changed
    # TODO: Assert new values are reflected
    pass

def test_delete_model():
    """Test deleting a model"""
    # TODO: Create a model
    # TODO: Delete the model
    # TODO: Assert status code is 204
    # TODO: Try to get the model again
    # TODO: Assert it returns 404
    pass

def test_filter_by_framework():
    """Test filtering models by framework"""
    # TODO: Create models with different frameworks
    # TODO: Filter by framework
    # TODO: Assert only matching models are returned
    pass

def test_search_models():
    """Test search functionality"""
    # TODO: Create models with specific names/tags
    # TODO: Search for a term
    # TODO: Assert matching models are returned
    pass
```

**Run tests:**
```bash
pytest tests/test_api.py -v
```

## Challenges and Extensions

### Challenge 1: Add Pagination Metadata

Enhance the list endpoint to return pagination metadata:

```json
{
  "items": [...],
  "total": 100,
  "page": 1,
  "size": 10,
  "pages": 10
}
```

### Challenge 2: Add Sorting

Allow sorting by different fields:
```
GET /api/v1/models?sort_by=created_at&order=desc
```

### Challenge 3: Add Model Statistics Endpoint

```
GET /api/v1/models/stats
{
  "total_models": 42,
  "by_framework": {
    "pytorch": 20,
    "tensorflow": 15,
    "sklearn": 7
  },
  "by_status": {
    "ready": 30,
    "deployed": 10,
    "archived": 2
  }
}
```

### Challenge 4: Add Validation

- Model names must be unique
- Version must follow semantic versioning (X.Y.Z)
- Tags should be lowercase with no spaces
- Accuracy must be between 0 and 1

### Challenge 5: Add Batch Operations

```python
POST /api/v1/models/batch
{
  "models": [
    {...},
    {...}
  ]
}
```

## Common Issues and Solutions

### Issue 1: Import Errors

**Problem:** `ModuleNotFoundError: No module named 'app'`

**Solution:**
- Make sure you're in the project root directory
- Run with: `uvicorn app.main:app --reload`
- Or add `__init__.py` files to make directories into packages

### Issue 2: Pydantic Validation Errors

**Problem:** `ValidationError` when creating models

**Solution:**
- Check that all required fields are provided
- Ensure data types match (e.g., accuracy as float, not string)
- Use `.dict()` or `.model_dump()` to convert Pydantic models to dicts

### Issue 3: 422 Unprocessable Entity

**Problem:** API returns 422 when sending requests

**Solution:**
- Check request body matches the expected Pydantic model
- Ensure JSON is valid
- Check that enum values are correct

## Deliverables

By the end of this exercise, you should have:

1. ✅ Working FastAPI application with CRUD endpoints
2. ✅ Pydantic models for request/response validation
3. ✅ In-memory database implementation
4. ✅ Proper HTTP status codes for all responses
5. ✅ Error handling for invalid requests
6. ✅ Interactive API documentation (Swagger UI)
7. ✅ Test suite with 90%+ coverage
8. ✅ README with setup and usage instructions

## Submission Checklist

- [ ] All endpoints implemented and working
- [ ] All tests passing (`pytest`)
- [ ] Interactive documentation accessible at `/docs`
- [ ] Code follows Python style guidelines (use `black` for formatting)
- [ ] No hardcoded values (use environment variables or config)
- [ ] README.md with:
  - [ ] Setup instructions
  - [ ] API endpoint documentation
  - [ ] Example requests and responses
  - [ ] How to run tests

## Key Takeaways

After completing this exercise, you should understand:

1. **REST Principles:** Resource-based URLs, HTTP methods, status codes
2. **FastAPI Basics:** Path operations, Pydantic models, automatic validation
3. **CRUD Operations:** Create, Read, Update, Delete patterns
4. **Error Handling:** Proper HTTP exceptions and status codes
5. **API Testing:** Using TestClient for automated testing
6. **Documentation:** Auto-generated interactive docs

## Next Steps

- Exercise 02: Build a model serving API with actual ML models
- Exercise 03: Add JWT authentication to your API
- Exercise 04: Deploy your API to production

---

**Estimated Completion Time:** 2-3 hours
**Difficulty:** Beginner
**Focus:** REST API fundamentals, FastAPI basics, CRUD operations
