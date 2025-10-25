# Lecture 02: FastAPI Framework

## Table of Contents
1. [Introduction](#introduction)
2. [What is FastAPI?](#what-is-fastapi)
3. [FastAPI Installation and Setup](#fastapi-installation-and-setup)
4. [Your First FastAPI Application](#your-first-fastapi-application)
5. [Path Operations and Routing](#path-operations-and-routing)
6. [Request and Response Models](#request-and-response-models)
7. [Path Parameters and Query Parameters](#path-parameters-and-query-parameters)
8. [Request Body and Validation](#request-body-and-validation)
9. [Response Models and Status Codes](#response-models-and-status-codes)
10. [Dependency Injection](#dependency-injection)
11. [Error Handling and Custom Exceptions](#error-handling-and-custom-exceptions)
12. [Background Tasks](#background-tasks)
13. [Building ML APIs with FastAPI](#building-ml-apis-with-fastapi)
14. [Testing FastAPI Applications](#testing-fastapi-applications)
15. [Best Practices](#best-practices)
16. [Summary and Key Takeaways](#summary-and-key-takeaways)

## Introduction

FastAPI is a modern, high-performance web framework for building APIs with Python 3.7+ based on standard Python type hints. It has quickly become one of the most popular frameworks for building production-grade APIs, especially in the machine learning and data science communities.

This lecture will guide you through FastAPI's core concepts and features, teaching you how to build robust, performant APIs for AI/ML applications.

### Learning Objectives

By the end of this lecture, you will:
- Understand what makes FastAPI unique and why it's ideal for ML applications
- Set up a FastAPI development environment
- Create path operations using various HTTP methods
- Define request and response models with automatic validation
- Implement path parameters, query parameters, and request bodies
- Use Pydantic for data validation and serialization
- Implement dependency injection for cleaner code
- Handle errors gracefully with custom exceptions
- Build async endpoints for improved performance
- Create a complete ML model serving API
- Test FastAPI applications effectively

### Prerequisites
- Module 001: Python Fundamentals
- Module 007 - Lecture 01: API Fundamentals & REST
- Understanding of Python type hints
- Basic async/await concepts (helpful but not required)

### Estimated Time
4-5 hours (including hands-on coding)

## What is FastAPI?

### Overview

**FastAPI** is a modern, fast (high-performance) web framework for building APIs with Python 3.7+ based on standard Python type hints. Created by Sebastián Ramírez in 2018, it has rapidly gained adoption due to its performance, developer experience, and automatic documentation generation.

### Key Features

1. **Fast**: Very high performance, on par with NodeJS and Go (thanks to Starlette and Pydantic)
2. **Fast to code**: Increase development speed by 200-300%
3. **Fewer bugs**: Reduce about 40% of human-induced errors
4. **Intuitive**: Great editor support with auto-completion everywhere
5. **Easy**: Designed to be easy to use and learn
6. **Short**: Minimize code duplication
7. **Robust**: Get production-ready code with automatic interactive documentation
8. **Standards-based**: Based on OpenAPI and JSON Schema

### Why FastAPI for ML Infrastructure?

1. **Performance**: Critical for low-latency model inference
2. **Async Support**: Handle multiple concurrent prediction requests efficiently
3. **Automatic Validation**: Validate input data before feeding to models
4. **Type Safety**: Catch errors during development, not production
5. **Automatic Documentation**: Interactive API docs out-of-the-box
6. **Easy Integration**: Works well with ML frameworks (PyTorch, TensorFlow, sklearn)
7. **Modern Python**: Uses latest Python features (type hints, async/await)

### FastAPI vs. Flask

| Feature | FastAPI | Flask |
|---------|---------|-------|
| Performance | Very High (async) | Moderate (sync) |
| Type Hints | Built-in, required | Optional, via extensions |
| Validation | Automatic (Pydantic) | Manual or via extensions |
| Documentation | Auto-generated | Manual or via extensions |
| Async Support | Native | Via extensions |
| Learning Curve | Moderate | Low |
| Best For | Production APIs, ML serving | Prototypes, simple apps |

## FastAPI Installation and Setup

### Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install FastAPI and ASGI server
pip install fastapi
pip install "uvicorn[standard]"

# For development
pip install "fastapi[all]"  # Includes all optional dependencies
```

**What gets installed:**
- `fastapi`: The FastAPI framework
- `uvicorn`: ASGI server to run the application
- `pydantic`: Data validation using Python type hints
- `starlette`: Web framework used by FastAPI

### Project Structure

For a simple ML API:

```
ml-api/
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI application
│   ├── models.py         # Pydantic models
│   ├── routers/          # API routes
│   │   ├── __init__.py
│   │   ├── predictions.py
│   │   └── health.py
│   ├── services/         # Business logic
│   │   ├── __init__.py
│   │   └── ml_model.py
│   └── dependencies.py   # Shared dependencies
├── tests/
│   ├── __init__.py
│   └── test_api.py
├── models/               # ML model files
│   └── model.pkl
├── requirements.txt
├── .env
└── README.md
```

## Your First FastAPI Application

### Hello World

Create `main.py`:

```python
from fastapi import FastAPI

# Create FastAPI instance
app = FastAPI()

# Define a path operation
@app.get("/")
def read_root():
    return {"message": "Hello World"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
```

### Running the Application

```bash
# Run with uvicorn
uvicorn main:app --reload

# Options:
# --reload: Auto-reload on code changes (development only)
# --host 0.0.0.0: Make accessible from any IP
# --port 8000: Specify port (default: 8000)
# --workers 4: Number of worker processes (production)
```

Output:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using watchfiles
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Testing Your API

**Using curl:**
```bash
curl http://localhost:8000/
# {"message":"Hello World"}

curl http://localhost:8000/health
# {"status":"healthy"}
```

**Using Python requests:**
```python
import requests

response = requests.get("http://localhost:8000/")
print(response.json())
# {'message': 'Hello World'}
```

### Interactive Documentation

FastAPI automatically generates interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

You can test your API directly from the browser using these interfaces!

### OpenAPI Schema

FastAPI generates an OpenAPI schema automatically:

```bash
curl http://localhost:8000/openapi.json
```

This schema can be used for:
- Client code generation
- API testing tools
- Third-party integrations
- Documentation

## Path Operations and Routing

### HTTP Methods

FastAPI provides decorators for all HTTP methods:

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/items")
def read_items():
    return {"message": "Get all items"}

@app.post("/items")
def create_item():
    return {"message": "Create item"}

@app.put("/items/{item_id}")
def update_item(item_id: int):
    return {"message": f"Update item {item_id}"}

@app.patch("/items/{item_id}")
def partial_update_item(item_id: int):
    return {"message": f"Partial update item {item_id}"}

@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    return {"message": f"Delete item {item_id}"}

@app.head("/items")
def items_head():
    return None  # Only returns headers

@app.options("/items")
def items_options():
    return {"methods": ["GET", "POST"]}
```

### Path Operation Configuration

Add metadata to your endpoints:

```python
@app.get(
    "/models/{model_id}",
    summary="Get model details",
    description="Retrieve detailed information about a specific model",
    response_description="Model information including metadata and status",
    tags=["Models"],
    deprecated=False
)
def get_model(model_id: str):
    return {"model_id": model_id, "status": "ready"}
```

### Tags for Organization

Group related endpoints:

```python
@app.get("/models", tags=["Models"])
def list_models():
    return {"models": []}

@app.post("/models", tags=["Models"])
def create_model():
    return {"model_id": "new-model"}

@app.get("/datasets", tags=["Datasets"])
def list_datasets():
    return {"datasets": []}

@app.post("/predictions", tags=["Inference"])
def predict():
    return {"prediction": 0.95}
```

Tags create sections in the auto-generated documentation.

### Routers for Modularity

For larger applications, use `APIRouter`:

**routers/models.py:**
```python
from fastapi import APIRouter

router = APIRouter(
    prefix="/api/v1/models",
    tags=["Models"],
    responses={404: {"description": "Not found"}}
)

@router.get("/")
def list_models():
    return {"models": []}

@router.get("/{model_id}")
def get_model(model_id: str):
    return {"model_id": model_id}

@router.post("/")
def create_model():
    return {"model_id": "new-model"}
```

**main.py:**
```python
from fastapi import FastAPI
from routers import models

app = FastAPI()

# Include router
app.include_router(models.router)
```

Now your endpoints are available at:
- `GET /api/v1/models/`
- `GET /api/v1/models/{model_id}`
- `POST /api/v1/models/`

## Request and Response Models

### Pydantic Models

FastAPI uses **Pydantic** for data validation and serialization. Pydantic models are Python classes that define the shape of data.

```python
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class Model(BaseModel):
    id: str
    name: str
    version: str = "1.0.0"
    framework: str = Field(..., description="ML framework (pytorch, tensorflow, etc.)")
    created_at: datetime
    tags: List[str] = []
    accuracy: Optional[float] = None

    class Config:
        # Example for documentation
        schema_extra = {
            "example": {
                "id": "bert-base",
                "name": "BERT Base Model",
                "version": "1.0.0",
                "framework": "pytorch",
                "created_at": "2024-10-18T14:30:00Z",
                "tags": ["nlp", "transformer"],
                "accuracy": 0.92
            }
        }
```

### Field Validation

```python
from pydantic import BaseModel, Field, validator
from typing import Literal

class TrainingConfig(BaseModel):
    batch_size: int = Field(gt=0, le=128, description="Batch size (1-128)")
    learning_rate: float = Field(gt=0, le=1, description="Learning rate (0-1)")
    epochs: int = Field(ge=1, le=1000, description="Number of epochs")
    optimizer: Literal["adam", "sgd", "rmsprop"] = "adam"

    @validator("learning_rate")
    def validate_lr(cls, v):
        if v > 0.1:
            raise ValueError("Learning rate above 0.1 is usually too high")
        return v

    @validator("batch_size")
    def validate_batch_size(cls, v):
        # Must be power of 2
        if v & (v - 1) != 0:
            raise ValueError("Batch size should be power of 2 for optimal performance")
        return v
```

### Using Models in Path Operations

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class PredictionRequest(BaseModel):
    text: str
    max_length: int = 512

class PredictionResponse(BaseModel):
    prediction: str
    confidence: float
    processing_time_ms: int

@app.post("/predict", response_model=PredictionResponse)
def predict(request: PredictionRequest):
    # FastAPI automatically:
    # 1. Validates request body against PredictionRequest
    # 2. Converts JSON to PredictionRequest object
    # 3. Validates response against PredictionResponse
    # 4. Converts PredictionResponse to JSON

    return PredictionResponse(
        prediction="positive",
        confidence=0.95,
        processing_time_ms=45
    )
```

## Path Parameters and Query Parameters

### Path Parameters

```python
@app.get("/models/{model_id}")
def get_model(model_id: str):
    return {"model_id": model_id}

# With type validation
@app.get("/models/{model_id}/versions/{version_num}")
def get_model_version(model_id: str, version_num: int):
    return {"model_id": model_id, "version": version_num}

# With Enum for limited values
from enum import Enum

class ModelFramework(str, Enum):
    pytorch = "pytorch"
    tensorflow = "tensorflow"
    sklearn = "sklearn"

@app.get("/models/framework/{framework}")
def get_models_by_framework(framework: ModelFramework):
    return {"framework": framework, "models": []}
```

### Query Parameters

```python
from typing import Optional, List

# Optional query parameter
@app.get("/models")
def list_models(skip: int = 0, limit: int = 10):
    # GET /models?skip=0&limit=10
    return {"skip": skip, "limit": limit}

# Required query parameter (no default value)
@app.get("/search")
def search_models(q: str):
    # GET /search?q=bert
    # GET /search  → 422 Error (missing required parameter)
    return {"query": q}

# Optional with None default
@app.get("/models")
def list_models(status: Optional[str] = None):
    # GET /models
    # GET /models?status=ready
    if status:
        return {"filter": status}
    return {"message": "All models"}

# Multiple values (List)
@app.get("/models")
def list_models(tags: List[str] = []):
    # GET /models?tags=nlp&tags=transformer
    return {"tags": tags}

# Boolean query parameters
@app.get("/models")
def list_models(include_archived: bool = False):
    # GET /models?include_archived=true
    # GET /models?include_archived=1
    # GET /models?include_archived=yes
    # All convert to True
    return {"include_archived": include_archived}
```

### Combining Path and Query Parameters

```python
@app.get("/models/{model_id}")
def get_model(
    model_id: str,
    include_metrics: bool = False,
    version: Optional[str] = None
):
    # GET /models/bert-base
    # GET /models/bert-base?include_metrics=true
    # GET /models/bert-base?include_metrics=true&version=2.0.0

    result = {"model_id": model_id}
    if include_metrics:
        result["metrics"] = {"accuracy": 0.92}
    if version:
        result["version"] = version
    return result
```

## Request Body and Validation

### Simple Request Body

```python
from pydantic import BaseModel

class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None

@app.post("/items")
def create_item(item: Item):
    # FastAPI validates the request body
    total = item.price + (item.tax or 0)
    return {"item": item, "total": total}
```

### Nested Models

```python
class DatasetInfo(BaseModel):
    name: str
    size: int
    path: str

class TrainingJobConfig(BaseModel):
    model_type: str
    dataset: DatasetInfo
    batch_size: int
    epochs: int

@app.post("/training-jobs")
def create_training_job(config: TrainingJobConfig):
    return {
        "status": "created",
        "model": config.model_type,
        "dataset": config.dataset.name
    }

# Request body:
# {
#   "model_type": "bert",
#   "dataset": {
#     "name": "imdb",
#     "size": 50000,
#     "path": "/data/imdb"
#   },
#   "batch_size": 32,
#   "epochs": 10
# }
```

### Lists and Dictionaries

```python
from typing import List, Dict

class BatchPredictionRequest(BaseModel):
    inputs: List[str]
    model_id: str

@app.post("/batch-predict")
def batch_predict(request: BatchPredictionRequest):
    predictions = [f"pred_{i}" for i in range(len(request.inputs))]
    return {"predictions": predictions}

# Request:
# {
#   "model_id": "bert-base",
#   "inputs": ["text 1", "text 2", "text 3"]
# }

class FlexibleConfig(BaseModel):
    parameters: Dict[str, float]

@app.post("/configure")
def configure(config: FlexibleConfig):
    return config

# Request:
# {
#   "parameters": {
#     "learning_rate": 0.001,
#     "dropout": 0.1,
#     "temperature": 0.7
#   }
# }
```

### Advanced Validation

```python
from pydantic import BaseModel, Field, validator, root_validator

class PredictionInput(BaseModel):
    text: str = Field(..., min_length=1, max_length=10000)
    language: str = Field("en", regex="^[a-z]{2}$")  # Two-letter language code
    confidence_threshold: float = Field(0.5, ge=0.0, le=1.0)

    @validator("text")
    def text_must_not_be_only_whitespace(cls, v):
        if not v.strip():
            raise ValueError("Text cannot be only whitespace")
        return v.strip()

    @root_validator
    def check_language_compatibility(cls, values):
        text = values.get("text")
        language = values.get("language")

        # Example: Check if text matches language
        # In practice, you'd use language detection library

        return values

@app.post("/predict")
def predict(input_data: PredictionInput):
    return {"status": "validated", "text_length": len(input_data.text)}
```

## Response Models and Status Codes

### Response Model

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class ModelResponse(BaseModel):
    id: str
    name: str
    status: str

@app.get("/models/{model_id}", response_model=ModelResponse)
def get_model(model_id: str):
    # Even if you return extra fields, only ModelResponse fields will be in response
    return {
        "id": model_id,
        "name": "BERT Model",
        "status": "ready",
        "internal_field": "won't be shown"  # Filtered out
    }
```

### Excluding Fields

```python
class UserInDB(BaseModel):
    username: str
    email: str
    full_name: str
    hashed_password: str  # Sensitive!

class UserOut(BaseModel):
    username: str
    email: str
    full_name: str

@app.get("/users/{user_id}", response_model=UserOut)
def get_user(user_id: str):
    # Fetch from database
    user_in_db = {
        "username": "alice",
        "email": "alice@example.com",
        "full_name": "Alice Smith",
        "hashed_password": "$2b$12$..."
    }
    # hashed_password won't be in response
    return user_in_db
```

### Response Status Codes

```python
from fastapi import FastAPI, status

app = FastAPI()

@app.post("/models", status_code=status.HTTP_201_CREATED)
def create_model():
    return {"id": "new-model"}

@app.delete("/models/{model_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_model(model_id: str):
    # 204 responses don't return a body
    return None

@app.get("/models/{model_id}", status_code=status.HTTP_200_OK)
def get_model(model_id: str):
    return {"id": model_id}
```

### Multiple Response Models

```python
from typing import Union
from fastapi import Response

class SuccessResponse(BaseModel):
    data: dict
    message: str

class ErrorResponse(BaseModel):
    error: str
    details: str

@app.get(
    "/models/{model_id}",
    responses={
        200: {"model": SuccessResponse, "description": "Model found"},
        404: {"model": ErrorResponse, "description": "Model not found"}
    }
)
def get_model(model_id: str, response: Response):
    if model_id == "unknown":
        response.status_code = 404
        return ErrorResponse(error="Not Found", details=f"Model {model_id} doesn't exist")

    return SuccessResponse(data={"id": model_id}, message="Success")
```

## Dependency Injection

Dependency Injection is a powerful FastAPI feature that allows you to:
- Share logic across endpoints
- Manage database connections
- Handle authentication
- Validate permissions
- Reduce code duplication

### Basic Dependency

```python
from fastapi import Depends

def get_current_user(token: str):
    # In reality, decode and validate token
    if token == "valid-token":
        return {"username": "alice"}
    raise HTTPException(status_code=401, detail="Invalid token")

@app.get("/protected")
def protected_route(user: dict = Depends(get_current_user)):
    return {"message": f"Hello {user['username']}"}
```

### Database Connection Dependency

```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/models")
def list_models(db: Session = Depends(get_db)):
    models = db.query(ModelTable).all()
    return models
```

### Layered Dependencies

```python
from fastapi import Header, HTTPException

def verify_token(x_token: str = Header(...)):
    if x_token != "secret-token":
        raise HTTPException(status_code=401, detail="Invalid token")
    return x_token

def get_current_user(token: str = Depends(verify_token)):
    # Token is already verified
    return {"username": "alice", "token": token}

def get_admin_user(user: dict = Depends(get_current_user)):
    if user["username"] != "admin":
        raise HTTPException(status_code=403, detail="Not an admin")
    return user

@app.get("/admin/dashboard")
def admin_dashboard(admin: dict = Depends(get_admin_user)):
    # Only admins can access
    return {"message": f"Welcome admin {admin['username']}"}
```

### Class-Based Dependencies

```python
from typing import Optional

class CommonQueryParams:
    def __init__(self, skip: int = 0, limit: int = 10, q: Optional[str] = None):
        self.skip = skip
        self.limit = limit
        self.q = q

@app.get("/items")
def list_items(commons: CommonQueryParams = Depends()):
    return {"skip": commons.skip, "limit": commons.limit, "q": commons.q}

# Usage:
# GET /items?skip=10&limit=20&q=search
```

### ML Model Loading Dependency

```python
import pickle
from typing import Optional

# Global model cache
_model_cache = {}

def get_ml_model(model_id: str):
    """Dependency to load and cache ML models"""
    if model_id not in _model_cache:
        # Load model (expensive operation)
        with open(f"models/{model_id}.pkl", "rb") as f:
            _model_cache[model_id] = pickle.load(f)
    return _model_cache[model_id]

@app.post("/predict/{model_id}")
def predict(
    model_id: str,
    input_data: PredictionInput,
    model = Depends(get_ml_model)
):
    # Model is already loaded and cached
    prediction = model.predict([input_data.features])
    return {"prediction": prediction[0]}
```

## Error Handling and Custom Exceptions

### HTTPException

```python
from fastapi import HTTPException, status

@app.get("/models/{model_id}")
def get_model(model_id: str):
    # Simulate database lookup
    if model_id not in ["bert-base", "gpt-2"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Model '{model_id}' not found",
            headers={"X-Error": "Model-Not-Found"}
        )

    return {"model_id": model_id, "status": "ready"}
```

### Custom Exception Classes

```python
class ModelNotFoundError(Exception):
    def __init__(self, model_id: str):
        self.model_id = model_id

class InvalidModelError(Exception):
    def __init__(self, model_id: str, reason: str):
        self.model_id = model_id
        self.reason = reason

# Exception handlers
from fastapi import Request
from fastapi.responses import JSONResponse

@app.exception_handler(ModelNotFoundError)
async def model_not_found_handler(request: Request, exc: ModelNotFoundError):
    return JSONResponse(
        status_code=404,
        content={
            "error": "Model not found",
            "model_id": exc.model_id,
            "suggestion": "Check /api/models for available models"
        }
    )

@app.exception_handler(InvalidModelError)
async def invalid_model_handler(request: Request, exc: InvalidModelError):
    return JSONResponse(
        status_code=422,
        content={
            "error": "Invalid model",
            "model_id": exc.model_id,
            "reason": exc.reason
        }
    )

# Using custom exceptions
@app.get("/models/{model_id}")
def get_model(model_id: str):
    if model_id == "unknown":
        raise ModelNotFoundError(model_id)
    if model_id == "corrupted":
        raise InvalidModelError(model_id, "Model file is corrupted")
    return {"model_id": model_id}
```

### Global Exception Handler

```python
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # Log the exception
    logger.error(f"Unhandled exception: {exc}", exc_info=True)

    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred",
            "request_id": str(uuid.uuid4())
        }
    )
```

## Background Tasks

For operations that don't need to block the response:

```python
from fastapi import BackgroundTasks

def log_prediction(model_id: str, input_data: dict, prediction: dict):
    """Log prediction to database or file"""
    # Simulate logging
    with open("predictions.log", "a") as f:
        f.write(f"{model_id}: {input_data} -> {prediction}\n")

@app.post("/predict")
def predict(
    input_data: PredictionInput,
    background_tasks: BackgroundTasks
):
    # Make prediction
    prediction = {"result": "positive", "confidence": 0.95}

    # Add task to run after response is sent
    background_tasks.add_task(
        log_prediction,
        model_id="bert-base",
        input_data=input_data.dict(),
        prediction=prediction
    )

    # Return immediately
    return prediction
```

### Multiple Background Tasks

```python
def send_notification(email: str, message: str):
    # Send email notification
    pass

def update_metrics(model_id: str):
    # Update prediction count
    pass

@app.post("/predict")
def predict(
    input_data: PredictionInput,
    background_tasks: BackgroundTasks
):
    prediction = {"result": "positive"}

    background_tasks.add_task(log_prediction, "bert", input_data, prediction)
    background_tasks.add_task(send_notification, "admin@example.com", "Prediction made")
    background_tasks.add_task(update_metrics, "bert-base")

    return prediction
```

## Building ML APIs with FastAPI

### Complete Model Serving Example

```python
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Optional
import pickle
import numpy as np
from datetime import datetime

app = FastAPI(title="ML Model API", version="1.0.0")

# Models
class PredictionInput(BaseModel):
    features: List[float] = Field(..., min_items=4, max_items=4)

    class Config:
        schema_extra = {
            "example": {
                "features": [5.1, 3.5, 1.4, 0.2]
            }
        }

class PredictionOutput(BaseModel):
    prediction: str
    confidence: float
    probabilities: dict
    model_version: str
    timestamp: datetime

class ModelInfo(BaseModel):
    name: str
    version: str
    framework: str
    features: int
    classes: List[str]
    accuracy: float

# Global model storage
_models = {}

# Startup event to load models
@app.on_event("startup")
async def load_models():
    """Load ML models on application startup"""
    try:
        with open("models/iris_classifier.pkl", "rb") as f:
            _models["iris"] = pickle.load(f)
        print("Models loaded successfully")
    except Exception as e:
        print(f"Error loading models: {e}")

# Dependency to get model
def get_model():
    if "iris" not in _models:
        raise HTTPException(status_code=503, detail="Model not loaded")
    return _models["iris"]

# Health check
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "models_loaded": len(_models),
        "timestamp": datetime.utcnow()
    }

# Model info
@app.get("/models/iris", response_model=ModelInfo)
def get_model_info():
    return ModelInfo(
        name="Iris Classifier",
        version="1.0.0",
        framework="scikit-learn",
        features=4,
        classes=["setosa", "versicolor", "virginica"],
        accuracy=0.96
    )

# Prediction endpoint
@app.post("/predict", response_model=PredictionOutput)
def predict(
    input_data: PredictionInput,
    model = Depends(get_model)
):
    try:
        # Prepare input
        features = np.array([input_data.features])

        # Make prediction
        prediction = model.predict(features)[0]
        probabilities = model.predict_proba(features)[0]

        # Get class names
        classes = ["setosa", "versicolor", "virginica"]

        return PredictionOutput(
            prediction=classes[prediction],
            confidence=float(max(probabilities)),
            probabilities={cls: float(prob) for cls, prob in zip(classes, probabilities)},
            model_version="1.0.0",
            timestamp=datetime.utcnow()
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(e)}"
        )

# Batch prediction
@app.post("/batch-predict")
def batch_predict(
    inputs: List[PredictionInput],
    model = Depends(get_model)
):
    results = []
    for input_data in inputs:
        features = np.array([input_data.features])
        prediction = model.predict(features)[0]
        results.append({
            "features": input_data.features,
            "prediction": ["setosa", "versicolor", "virginica"][prediction]
        })

    return {"predictions": results, "count": len(results)}
```

## Testing FastAPI Applications

### Using TestClient

```python
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}

def test_create_item():
    response = client.post(
        "/items",
        json={"name": "Test Item", "price": 10.0}
    )
    assert response.status_code == 200
    assert "item" in response.json()

def test_invalid_item():
    response = client.post(
        "/items",
        json={"name": "Test", "price": "invalid"}  # Wrong type
    )
    assert response.status_code == 422  # Validation error

def test_prediction():
    response = client.post(
        "/predict",
        json={"features": [5.1, 3.5, 1.4, 0.2]}
    )
    assert response.status_code == 200
    data = response.json()
    assert "prediction" in data
    assert "confidence" in data
```

### Pytest Fixtures

```python
import pytest
from fastapi.testclient import TestClient

@pytest.fixture
def client():
    from main import app
    return TestClient(app)

@pytest.fixture
def auth_headers():
    return {"Authorization": "Bearer test-token"}

def test_protected_endpoint(client, auth_headers):
    response = client.get("/protected", headers=auth_headers)
    assert response.status_code == 200
```

## Best Practices

### 1. Project Structure

Use routers to organize code:
```
app/
├── main.py
├── routers/
│   ├── models.py
│   ├── predictions.py
│   └── health.py
├── models/
│   ├── schemas.py
│   └── ml_models.py
├── services/
│   ├── model_service.py
│   └── prediction_service.py
└── dependencies.py
```

### 2. Configuration Management

```python
from pydantic import BaseSettings

class Settings(BaseSettings):
    app_name: str = "ML API"
    model_path: str = "/models"
    max_batch_size: int = 100
    redis_url: str = "redis://localhost"

    class Config:
        env_file = ".env"

settings = Settings()
```

### 3. Logging

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.post("/predict")
def predict(input_data: PredictionInput):
    logger.info(f"Prediction request received: {input_data}")
    try:
        result = model.predict(input_data.features)
        logger.info(f"Prediction successful: {result}")
        return result
    except Exception as e:
        logger.error(f"Prediction failed: {e}", exc_info=True)
        raise
```

### 4. CORS Configuration

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 5. Request Validation

Always validate inputs:
```python
class PredictionInput(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000)

    @validator("text")
    def validate_text(cls, v):
        if not v.strip():
            raise ValueError("Text cannot be empty")
        return v.strip()
```

### 6. Async Endpoints

For I/O-bound operations:
```python
import aiofiles

@app.get("/logs")
async def get_logs():
    async with aiofiles.open("app.log", mode="r") as f:
        content = await f.read()
    return {"logs": content}
```

### 7. Rate Limiting

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/predict")
@limiter.limit("10/minute")
def predict(request: Request, input_data: PredictionInput):
    return {"prediction": "result"}
```

## Summary and Key Takeaways

### What We Learned

1. **FastAPI Basics**
   - High-performance async framework
   - Automatic validation and documentation
   - Type hints for development speed and safety

2. **Core Features**
   - Path operations with HTTP methods
   - Pydantic models for request/response validation
   - Path and query parameters with type checking
   - Dependency injection for clean code architecture

3. **Advanced Topics**
   - Error handling with custom exceptions
   - Background tasks for async operations
   - Model serving with proper structure
   - Testing with TestClient

4. **ML-Specific Patterns**
   - Model loading and caching
   - Batch prediction endpoints
   - Health checks and monitoring
   - Proper error handling for production

### Next Steps

In the next lecture, we'll cover **Authentication & Security**, including:
- API key authentication
- JWT tokens
- OAuth2
- Rate limiting
- Input sanitization
- HTTPS and security headers

### Practice Exercise

Build a complete model serving API:
1. Load a scikit-learn model
2. Create prediction endpoints
3. Add health checks
4. Implement error handling
5. Write tests
6. Add documentation

---

**Estimated Study Time**: 4-5 hours
**Hands-on Practice**: Complete Exercise 01 and 02
**Assessment**: Quiz will cover FastAPI concepts and practical implementation
