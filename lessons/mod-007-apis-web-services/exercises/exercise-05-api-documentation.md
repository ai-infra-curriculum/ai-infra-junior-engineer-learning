# Exercise 05: API Documentation and OpenAPI

## Overview

Create comprehensive API documentation using OpenAPI/Swagger, customize the auto-generated docs, add examples, and learn best practices for documenting ML APIs. Good documentation is essential for API adoption and maintenance.

**Difficulty:** Beginner-Intermediate
**Estimated Time:** 1-2 hours
**Prerequisites:**
- Exercise 01-02 completed
- Understanding of REST principles
- Lecture 01-02

## Learning Objectives

By completing this exercise, you will:
- Customize FastAPI's auto-generated documentation
- Add detailed descriptions and examples to endpoints
- Document request/response models thoroughly
- Add authentication documentation
- Create custom API documentation pages
- Export OpenAPI schema for client generation

## Scenario

Your ML API needs professional documentation for:
- Internal developers integrating the API
- External partners using your models
- Client SDK generation
- API testing and validation

## Part 1: Enhanced Endpoint Documentation

**File: app/main.py** (enhance existing endpoints)

```python
from fastapi import FastAPI, status
from pydantic import BaseModel, Field
from typing import List, Optional

app = FastAPI(
    title="ML Model API",
    description="""
    # ML Model Serving API

    This API provides machine learning model inference capabilities with the following features:

    * **Authentication**: JWT-based authentication
    * **Rate Limiting**: Tiered limits based on subscription
    * **Models**: Multiple pre-trained models available
    * **Real-time**: Low-latency predictions
    * **Batch Processing**: Process multiple inputs efficiently

    ## Getting Started

    1. Obtain API credentials
    2. Authenticate to get access token
    3. Make prediction requests

    ## Rate Limits

    - Free tier: 10 requests/minute
    - Pro tier: 100 requests/minute
    - Enterprise: Custom limits

    For support, contact: support@example.com
    """,
    version="1.0.0",
    terms_of_service="https://example.com/terms",
    contact={
        "name": "API Support",
        "url": "https://example.com/support",
        "email": "support@example.com"
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT"
    }
)

# TODO: Add detailed endpoint documentation
@app.post(
    "/api/v1/predict",
    response_model=PredictionOutput,
    status_code=status.HTTP_200_OK,
    summary="Make a prediction",
    description="""
    Make a prediction using the sentiment analysis model.

    This endpoint analyzes text and returns sentiment classification
    with confidence scores.

    **Processing Time:** < 100ms for single predictions

    **Example Use Cases:**
    - Customer review analysis
    - Social media sentiment tracking
    - Product feedback classification
    """,
    response_description="Prediction result with confidence score",
    tags=["Predictions"],
    responses={
        200: {
            "description": "Successful prediction",
            "content": {
                "application/json": {
                    "example": {
                        "text": "This product is amazing!",
                        "prediction": "positive",
                        "confidence": 0.95,
                        "timestamp": "2024-10-18T14:30:00Z"
                    }
                }
            }
        },
        401: {
            "description": "Authentication failed",
            "content": {
                "application/json": {
                    "example": {"detail": "Invalid or expired token"}
                }
            }
        },
        422: {
            "description": "Validation error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "loc": ["body", "text"],
                                "msg": "field required",
                                "type": "value_error.missing"
                            }
                        ]
                    }
                }
            }
        },
        429: {
            "description": "Rate limit exceeded",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Too many requests",
                        "retry_after": 60
                    }
                }
            }
        }
    }
)
async def predict(
    input_data: PredictionInput,
    current_user: User = Depends(get_current_active_user)
):
    """
    Make a sentiment prediction on the provided text.

    Args:
        input_data: Text input for sentiment analysis

    Returns:
        Prediction result with sentiment label and confidence

    Raises:
        HTTPException: If model is not loaded or prediction fails
    """
    # Implementation
    pass
```

## Part 2: Enhanced Pydantic Models

**File: app/models.py**

```python
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum

class SentimentLabel(str, Enum):
    """Sentiment classification labels"""
    positive = "positive"
    negative = "negative"
    neutral = "neutral"

class PredictionInput(BaseModel):
    """
    Input data for sentiment prediction.

    The model accepts text up to 5000 characters and performs
    sentiment analysis.
    """

    text: str = Field(
        ...,
        title="Input Text",
        description="Text to analyze for sentiment (1-5000 characters)",
        min_length=1,
        max_length=5000,
        example="This product exceeded my expectations! Highly recommend."
    )

    language: Optional[str] = Field(
        "en",
        title="Language Code",
        description="ISO 639-1 language code (e.g., 'en', 'es', 'fr')",
        regex="^[a-z]{2}$",
        example="en"
    )

    return_probabilities: bool = Field(
        False,
        title="Return Probabilities",
        description="Include probability scores for all classes",
        example=True
    )

    class Config:
        schema_extra = {
            "example": {
                "text": "This movie was absolutely fantastic! Great acting and plot.",
                "language": "en",
                "return_probabilities": True
            }
        }

class PredictionOutput(BaseModel):
    """
    Prediction result from sentiment analysis.

    Contains the predicted sentiment, confidence score, and optional
    probability distribution across all classes.
    """

    text: str = Field(
        ...,
        title="Original Text",
        description="The input text that was analyzed"
    )

    prediction: SentimentLabel = Field(
        ...,
        title="Predicted Sentiment",
        description="The predicted sentiment label"
    )

    confidence: float = Field(
        ...,
        title="Confidence Score",
        description="Model confidence in prediction (0.0-1.0)",
        ge=0.0,
        le=1.0,
        example=0.95
    )

    probabilities: Optional[dict] = Field(
        None,
        title="Class Probabilities",
        description="Probability distribution across all classes",
        example={
            "positive": 0.95,
            "negative": 0.03,
            "neutral": 0.02
        }
    )

    model_version: str = Field(
        ...,
        title="Model Version",
        description="Version of the model used for prediction",
        example="1.0.0"
    )

    processing_time_ms: Optional[int] = Field(
        None,
        title="Processing Time",
        description="Time taken to process prediction in milliseconds",
        example=45
    )

    timestamp: datetime = Field(
        ...,
        title="Timestamp",
        description="ISO 8601 timestamp of prediction",
        example="2024-10-18T14:30:00.000Z"
    )

    class Config:
        schema_extra = {
            "example": {
                "text": "This movie was absolutely fantastic!",
                "prediction": "positive",
                "confidence": 0.95,
                "probabilities": {
                    "positive": 0.95,
                    "negative": 0.03,
                    "neutral": 0.02
                },
                "model_version": "1.0.0",
                "processing_time_ms": 45,
                "timestamp": "2024-10-18T14:30:00.000Z"
            }
        }

class BatchPredictionInput(BaseModel):
    """Input for batch predictions"""

    texts: List[str] = Field(
        ...,
        title="Text List",
        description="List of texts to analyze (max 100)",
        min_items=1,
        max_items=100,
        example=[
            "Great product!",
            "Very disappointed.",
            "It's okay, nothing special."
        ]
    )

    @validator('texts')
    def validate_texts(cls, v):
        """Ensure each text is not empty"""
        for text in v:
            if not text.strip():
                raise ValueError("Text cannot be empty")
        return v

    class Config:
        schema_extra = {
            "example": {
                "texts": [
                    "This movie was amazing! Loved it.",
                    "Waste of time, very boring.",
                    "It was okay, nothing special.",
                    "Excellent performance by the actors."
                ]
            }
        }
```

## Part 3: Tag Organization

**File: app/main.py** (organize with tags)

```python
from fastapi import FastAPI

# TODO: Define tag metadata
tags_metadata = [
    {
        "name": "Authentication",
        "description": "Operations for user authentication and authorization",
    },
    {
        "name": "Predictions",
        "description": "Model inference endpoints for sentiment analysis",
        "externalDocs": {
            "description": "Model documentation",
            "url": "https://docs.example.com/models/sentiment"
        }
    },
    {
        "name": "Models",
        "description": "Model management and information",
    },
    {
        "name": "Jobs",
        "description": "Asynchronous job management for batch processing",
    },
    {
        "name": "Health",
        "description": "Health check and monitoring endpoints",
    }
]

app = FastAPI(
    title="ML Model API",
    openapi_tags=tags_metadata
)

# Apply tags to endpoints
@app.post("/token", tags=["Authentication"])
async def login():
    pass

@app.post("/api/v1/predict", tags=["Predictions"])
async def predict():
    pass

@app.get("/api/v1/models", tags=["Models"])
async def list_models():
    pass

@app.get("/health", tags=["Health"])
async def health_check():
    pass
```

## Part 4: Custom Documentation Pages

**File: app/main.py** (add custom docs)

```python
from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.openapi.utils import get_openapi

app = FastAPI(docs_url=None, redoc_url=None)  # Disable default docs

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    """Custom Swagger UI with custom styling"""
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} - Documentation",
        swagger_favicon_url="https://fastapi.tiangolo.com/img/favicon.png"
    )

@app.get("/redoc", include_in_schema=False)
async def redoc_html():
    """Custom ReDoc documentation"""
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} - ReDoc",
        redoc_favicon_url="https://fastapi.tiangolo.com/img/favicon.png"
    )

def custom_openapi():
    """Customize OpenAPI schema"""
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="ML Model Serving API",
        version="1.0.0",
        description="Production ML API with authentication and rate limiting",
        routes=app.routes,
    )

    # TODO: Add custom schema properties
    openapi_schema["info"]["x-logo"] = {
        "url": "https://example.com/logo.png"
    }

    # TODO: Add security schemes
    openapi_schema["components"]["securitySchemes"] = {
        "Bearer": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Enter your JWT token"
        }
    }

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
```

## Part 5: Code Examples in Documentation

**File: app/docs_examples.py**

```python
"""
Code examples for API documentation
"""

# Python example
python_example = """
import requests

# 1. Authenticate
response = requests.post(
    'https://api.example.com/token',
    data={'username': 'your_username', 'password': 'your_password'}
)
token = response.json()['access_token']

# 2. Make prediction
headers = {'Authorization': f'Bearer {token}'}
response = requests.post(
    'https://api.example.com/api/v1/predict',
    headers=headers,
    json={'text': 'This product is amazing!'}
)
result = response.json()
print(f"Sentiment: {result['prediction']}, Confidence: {result['confidence']}")
"""

# cURL example
curl_example = """
# 1. Authenticate
curl -X POST "https://api.example.com/token" \\
  -H "Content-Type: application/x-www-form-urlencoded" \\
  -d "username=your_username&password=your_password"

# 2. Make prediction
curl -X POST "https://api.example.com/api/v1/predict" \\
  -H "Authorization: Bearer YOUR_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{"text": "This product is amazing!"}'
"""

# JavaScript example
javascript_example = """
// 1. Authenticate
const authResponse = await fetch('https://api.example.com/token', {
  method: 'POST',
  headers: {'Content-Type': 'application/x-www-form-urlencoded'},
  body: new URLSearchParams({
    username: 'your_username',
    password: 'your_password'
  })
});
const { access_token } = await authResponse.json();

// 2. Make prediction
const predResponse = await fetch('https://api.example.com/api/v1/predict', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${access_token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    text: 'This product is amazing!'
  })
});
const result = await predResponse.json();
console.log(`Sentiment: ${result.prediction}, Confidence: ${result.confidence}`);
"""
```

## Part 6: Export OpenAPI Schema

**File: scripts/export_openapi.py**

```python
"""
Export OpenAPI schema for client generation
"""
import json
import yaml
from app.main import app

# Export as JSON
def export_json():
    """Export OpenAPI schema as JSON"""
    with open('openapi.json', 'w') as f:
        json.dump(app.openapi(), f, indent=2)
    print("OpenAPI schema exported to openapi.json")

# Export as YAML
def export_yaml():
    """Export OpenAPI schema as YAML"""
    with open('openapi.yaml', 'w') as f:
        yaml.dump(app.openapi(), f, sort_keys=False)
    print("OpenAPI schema exported to openapi.yaml")

if __name__ == "__main__":
    export_json()
    export_yaml()
```

**Run export:**
```bash
python scripts/export_openapi.py
```

## Part 7: Generate Client SDKs

### Using OpenAPI Generator

```bash
# Install OpenAPI Generator
npm install -g @openapitools/openapi-generator-cli

# Generate Python client
openapi-generator-cli generate \
  -i openapi.json \
  -g python \
  -o clients/python-client

# Generate JavaScript client
openapi-generator-cli generate \
  -i openapi.json \
  -g javascript \
  -o clients/js-client

# Generate Java client
openapi-generator-cli generate \
  -i openapi.json \
  -g java \
  -o clients/java-client
```

### Test Generated Client

```python
# Using auto-generated Python client
from generated_client import ApiClient, PredictionsApi
from generated_client.models import PredictionInput

# Configure client
client = ApiClient(configuration)
client.configuration.access_token = 'your_jwt_token'

# Make prediction
api = PredictionsApi(client)
result = api.predict(PredictionInput(text="This is great!"))
print(result.prediction)
```

## Part 8: Documentation Testing

**File: tests/test_documentation.py**

```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_openapi_schema():
    """Test OpenAPI schema is generated"""
    response = client.get("/openapi.json")
    assert response.status_code == 200

    schema = response.json()
    assert "openapi" in schema
    assert schema["info"]["title"] == "ML Model API"
    assert "paths" in schema
    assert "components" in schema

def test_swagger_docs_accessible():
    """Test Swagger UI is accessible"""
    response = client.get("/docs")
    assert response.status_code == 200
    assert "swagger" in response.text.lower()

def test_redoc_accessible():
    """Test ReDoc is accessible"""
    response = client.get("/redoc")
    assert response.status_code == 200

def test_all_endpoints_documented():
    """Test all endpoints have descriptions"""
    schema = client.get("/openapi.json").json()

    for path, methods in schema["paths"].items():
        for method, details in methods.items():
            # Skip non-HTTP methods
            if method not in ["get", "post", "put", "delete", "patch"]:
                continue

            assert "summary" in details or "description" in details, \
                f"Endpoint {method.upper()} {path} missing documentation"

def test_models_have_examples():
    """Test that models have examples in schema"""
    schema = client.get("/openapi.json").json()

    if "components" in schema and "schemas" in schema["components"]:
        for model_name, model_schema in schema["components"]["schemas"].items():
            # Check if example exists
            has_example = (
                "example" in model_schema or
                ("properties" in model_schema and
                 any("example" in prop for prop in model_schema["properties"].values()))
            )
            print(f"{model_name}: has_example={has_example}")

def test_security_scheme_documented():
    """Test security scheme is documented"""
    schema = client.get("/openapi.json").json()

    assert "components" in schema
    assert "securitySchemes" in schema["components"]
    assert "Bearer" in schema["components"]["securitySchemes"]
```

## Deliverables

- ✅ Comprehensive endpoint documentation
- ✅ Enhanced Pydantic models with examples
- ✅ Organized tags and sections
- ✅ Custom documentation pages
- ✅ Exported OpenAPI schema (JSON/YAML)
- ✅ Generated client SDKs
- ✅ Documentation tests

## Best Practices Checklist

- [ ] Every endpoint has a clear summary
- [ ] Every endpoint has a detailed description
- [ ] Every parameter has a description
- [ ] All models have examples
- [ ] Response codes are documented
- [ ] Error responses are documented
- [ ] Authentication is documented
- [ ] Rate limits are documented
- [ ] Code examples are provided
- [ ] Changelog is maintained

## Key Takeaways

1. **Auto-Generation:** FastAPI automatically generates OpenAPI docs
2. **Customization:** Extensive customization through Pydantic and decorators
3. **Examples:** Examples make APIs much easier to use
4. **Client Generation:** OpenAPI schema enables automatic client generation
5. **Testing:** Documentation should be tested like code

## Next Steps

- Learn about API versioning strategies
- Implement changelog tracking
- Create interactive tutorials
- Set up documentation site (Docusaurus, MkDocs)

---

**Estimated Time:** 1-2 hours
**Difficulty:** Beginner-Intermediate
**Focus:** API documentation, OpenAPI, examples, client generation
