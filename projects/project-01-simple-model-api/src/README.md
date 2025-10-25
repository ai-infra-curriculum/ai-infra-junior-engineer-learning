# Source Code Implementation Guide

**Project:** Simple Model API Deployment
**Directory:** `src/`

---

## Overview

This directory contains the core application code for the Model API. The code is organized into three main modules:

1. **`config.py`** - Configuration management and environment variables
2. **`model_loader.py`** - ML model loading, preprocessing, and inference
3. **`app.py`** - REST API implementation with Flask/FastAPI

---

## Implementation Order

Follow this order to build the application:

### 1. Start with Configuration (`config.py`)
- Simplest module, no dependencies
- Defines all configuration values
- Sets up environment variable loading
- Estimated time: 1-2 hours

### 2. Implement Model Loader (`model_loader.py`)
- Core ML functionality
- Depends only on ML framework (PyTorch/TensorFlow)
- Can be tested independently
- Estimated time: 4-6 hours

### 3. Build the API (`app.py`)
- Ties everything together
- Depends on config and model_loader
- Implements REST endpoints
- Estimated time: 6-8 hours

---

## Code Structure

```
src/
├── README.md              # This file
├── app.py                 # Main application (STUB)
├── model_loader.py        # Model management (STUB)
└── config.py              # Configuration (STUB)
```

---

## Module Descriptions

### `config.py` - Configuration Management

**Purpose:** Centralize all configuration values and environment variables

**What to Implement:**
- Environment variable loading with defaults
- Configuration validation
- Type conversions (string to int, bool, etc.)
- Configuration class or dictionary

**Key Configuration Values:**
```python
# Model Configuration
MODEL_NAME: str = "resnet50"  # or "mobilenet_v2"
MODEL_PATH: str = "~/.cache/torch/hub"
DEVICE: str = "cpu"  # or "cuda"

# API Configuration
HOST: str = "0.0.0.0"
PORT: int = 5000
DEBUG: bool = False

# Limits
MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
REQUEST_TIMEOUT: int = 30  # seconds

# Logging
LOG_LEVEL: str = "INFO"
LOG_FORMAT: str = "json"  # or "text"
```

**Testing:**
```python
# Test that config loads correctly
from config import Config

config = Config()
assert config.MODEL_NAME in ["resnet50", "mobilenet_v2"]
assert config.PORT > 0
assert config.MAX_FILE_SIZE > 0
```

---

### `model_loader.py` - Model Management

**Purpose:** Handle all ML model operations (loading, preprocessing, inference)

**What to Implement:**

#### 1. Model Loading
```python
def load_model(model_name: str, device: str) -> torch.nn.Module:
    """
    Load pre-trained model from torchvision.

    TODO:
    - Import appropriate model from torchvision.models
    - Load with pretrained=True
    - Move model to specified device
    - Set model to eval() mode
    - Return model instance
    """
```

#### 2. Image Preprocessing
```python
def preprocess_image(image: PIL.Image) -> torch.Tensor:
    """
    Preprocess image for model inference.

    TODO:
    - Convert image to RGB (handle grayscale, RGBA)
    - Resize to 224x224
    - Convert to tensor
    - Normalize with ImageNet stats
    - Add batch dimension
    - Return preprocessed tensor
    """
```

#### 3. Inference
```python
def predict(model: torch.nn.Module,
           image_tensor: torch.Tensor,
           top_k: int = 5) -> List[Dict]:
    """
    Generate predictions from model.

    TODO:
    - Disable gradient computation (torch.no_grad())
    - Run forward pass
    - Apply softmax to get probabilities
    - Get top-K predictions
    - Map indices to class labels
    - Format as list of dicts
    - Return predictions
    """
```

#### 4. Class Label Loading
```python
def load_imagenet_labels() -> Dict[int, str]:
    """
    Load ImageNet class labels.

    TODO:
    - Download or load ImageNet labels
    - Parse into dictionary {index: label}
    - Handle missing label file
    - Return label mapping
    """
```

**Model Loader Class Structure:**
```python
class ModelLoader:
    """Manages ML model lifecycle and inference."""

    def __init__(self, model_name: str = "resnet50", device: str = "cpu"):
        """Initialize ModelLoader with configuration."""

    def load(self) -> None:
        """Load model weights and prepare for inference."""

    def preprocess(self, image: PIL.Image) -> torch.Tensor:
        """Preprocess image for model input."""

    def predict(self, image: PIL.Image, top_k: int = 5) -> List[Dict]:
        """Generate top-K predictions for image."""

    def get_model_info(self) -> Dict:
        """Return model metadata."""
```

**Testing:**
```python
# Test model loading
loader = ModelLoader(model_name="resnet50")
loader.load()
assert loader.model is not None

# Test preprocessing
from PIL import Image
test_image = Image.open("test.jpg")
tensor = loader.preprocess(test_image)
assert tensor.shape == (1, 3, 224, 224)

# Test prediction
predictions = loader.predict(test_image)
assert len(predictions) == 5
assert all(0 <= p['confidence'] <= 1 for p in predictions)
```

---

### `app.py` - REST API Implementation

**Purpose:** Implement HTTP API endpoints and request handling

**What to Implement:**

#### 1. Application Setup
```python
# Flask example
from flask import Flask, request, jsonify
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize model loader
model_loader = ModelLoader()
model_loader.load()
```

#### 2. Health Check Endpoint
```python
@app.route('/health', methods=['GET'])
def health():
    """
    Health check endpoint.

    TODO:
    - Check if model is loaded
    - Return status: "healthy" or "unhealthy"
    - Include model name
    - Return 200 if healthy, 503 if not
    """
```

#### 3. Info Endpoint
```python
@app.route('/info', methods=['GET'])
def info():
    """
    Model information endpoint.

    TODO:
    - Get model metadata from model_loader
    - Include API version
    - Include supported endpoints
    - Include limits (file size, timeout)
    - Return as JSON
    """
```

#### 4. Predict Endpoint
```python
@app.route('/predict', methods=['POST'])
def predict():
    """
    Prediction endpoint.

    TODO:
    - Validate request has file
    - Check Content-Type
    - Validate file size
    - Load image with PIL
    - Handle image loading errors
    - Call model_loader.predict()
    - Format response with predictions
    - Add latency measurement
    - Log request with correlation ID
    - Handle all errors gracefully
    - Return JSON response
    """
```

#### 5. Error Handling
```python
@app.errorhandler(400)
def bad_request(error):
    """Handle 400 errors."""

@app.errorhandler(413)
def payload_too_large(error):
    """Handle file too large errors."""

@app.errorhandler(500)
def internal_error(error):
    """Handle internal server errors."""
```

#### 6. Request Validation
```python
def validate_image_file(file) -> Tuple[bool, Optional[str]]:
    """
    Validate uploaded image file.

    TODO:
    - Check file is not None
    - Validate file size
    - Attempt to open with PIL
    - Verify it's actually an image
    - Return (is_valid, error_message)
    """
```

#### 7. Response Formatting
```python
def format_success_response(predictions: List[Dict],
                          latency_ms: float) -> Dict:
    """Format successful prediction response."""

def format_error_response(error_code: str,
                         message: str,
                         correlation_id: str) -> Dict:
    """Format error response."""
```

#### 8. Correlation ID Generation
```python
import uuid

def generate_correlation_id() -> str:
    """Generate unique correlation ID for request tracking."""
    return f"req-{uuid.uuid4().hex[:8]}"
```

**Flask vs FastAPI:**

This guide shows Flask examples, but you can also use FastAPI:

```python
# FastAPI example
from fastapi import FastAPI, File, UploadFile, HTTPException
from typing import List

app = FastAPI()

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/predict")
async def predict(file: UploadFile = File(...), top_k: int = 5):
    # Implementation here
    pass
```

**Choose one framework and stick with it throughout the project.**

---

## Implementation Guidelines

### Code Style

Follow PEP 8 style guide:
- 4 spaces for indentation (no tabs)
- Maximum line length: 88 characters (Black formatter)
- Two blank lines between top-level functions/classes
- One blank line between methods
- Lowercase with underscores for functions/variables
- CamelCase for class names

### Type Hints

Add type hints to all functions:
```python
from typing import List, Dict, Tuple, Optional
from PIL import Image
import torch

def predict(image: Image.Image, top_k: int = 5) -> List[Dict[str, any]]:
    """Generate predictions with type safety."""
    pass
```

### Docstrings

Use Google-style docstrings:
```python
def preprocess_image(image: Image.Image) -> torch.Tensor:
    """
    Preprocess image for model inference.

    Converts image to RGB, resizes to 224x224, normalizes with ImageNet
    statistics, and converts to PyTorch tensor.

    Args:
        image: PIL Image object to preprocess

    Returns:
        Preprocessed image tensor with shape (1, 3, 224, 224)

    Raises:
        ValueError: If image cannot be converted to RGB

    Example:
        >>> from PIL import Image
        >>> img = Image.open('dog.jpg')
        >>> tensor = preprocess_image(img)
        >>> tensor.shape
        torch.Size([1, 3, 224, 224])
    """
    pass
```

### Error Handling

Always handle errors gracefully:
```python
try:
    image = Image.open(file_bytes)
    image = image.convert('RGB')
except Exception as e:
    logger.error(f"Failed to load image: {e}")
    return {"error": "Invalid image file"}, 400
```

### Logging

Log at appropriate levels:
```python
logger.debug("Preprocessing image")       # Detailed debugging info
logger.info("Model loaded successfully")  # Normal operations
logger.warning("File size near limit")    # Unusual but recoverable
logger.error("Invalid image format")      # Request failed
logger.critical("Model failed to load")   # System failure
```

---

## Testing Your Implementation

### Unit Tests

Test each module independently:

```python
# tests/test_config.py
def test_config_defaults():
    config = Config()
    assert config.MODEL_NAME == "resnet50"
    assert config.PORT == 5000

# tests/test_model_loader.py
def test_model_loads():
    loader = ModelLoader()
    loader.load()
    assert loader.model is not None

def test_prediction():
    loader = ModelLoader()
    loader.load()
    image = Image.open('test_image.jpg')
    predictions = loader.predict(image)
    assert len(predictions) == 5

# tests/test_app.py
def test_health_endpoint(client):
    response = client.get('/health')
    assert response.status_code == 200

def test_predict_endpoint(client):
    with open('test_image.jpg', 'rb') as f:
        response = client.post('/predict',
                              data={'file': f})
    assert response.status_code == 200
```

### Manual Testing

Test with cURL:
```bash
# Health check
curl http://localhost:5000/health

# Model info
curl http://localhost:5000/info

# Prediction
curl -X POST \
  -F "file=@dog.jpg" \
  http://localhost:5000/predict
```

---

## Common Pitfalls

### 1. Model Not in Eval Mode
```python
# WRONG
model = models.resnet50(pretrained=True)

# CORRECT
model = models.resnet50(pretrained=True)
model.eval()  # Disable dropout and batch normalization
```

### 2. Incorrect Tensor Dimensions
```python
# WRONG - Missing batch dimension
tensor = transform(image)  # Shape: (3, 224, 224)
output = model(tensor)     # ERROR!

# CORRECT - Add batch dimension
tensor = transform(image).unsqueeze(0)  # Shape: (1, 3, 224, 224)
output = model(tensor)  # Works!
```

### 3. Forgetting torch.no_grad()
```python
# WRONG - Wastes memory tracking gradients
output = model(tensor)

# CORRECT - Disable gradient computation
with torch.no_grad():
    output = model(tensor)
```

### 4. Not Converting Image to RGB
```python
# WRONG - May be grayscale or RGBA
image = Image.open(file)

# CORRECT - Ensure RGB
image = Image.open(file).convert('RGB')
```

### 5. Hardcoded Values
```python
# WRONG
PORT = 5000
MODEL_NAME = "resnet50"

# CORRECT
from config import Config
config = Config()
PORT = config.PORT
MODEL_NAME = config.MODEL_NAME
```

---

## Performance Tips

### 1. Load Model Once
```python
# WRONG - Loads model on every request (very slow!)
@app.route('/predict', methods=['POST'])
def predict():
    model = load_model()  # DON'T DO THIS

# CORRECT - Load once at startup
model_loader = ModelLoader()
model_loader.load()  # Once during initialization

@app.route('/predict', methods=['POST'])
def predict():
    predictions = model_loader.predict(image)  # Fast
```

### 2. Measure Latency
```python
import time

start_time = time.time()
predictions = model_loader.predict(image)
latency_ms = (time.time() - start_time) * 1000
logger.info(f"Prediction latency: {latency_ms:.2f}ms")
```

### 3. Efficient Image Loading
```python
# Load directly from bytes (no disk I/O)
import io
from PIL import Image

file_bytes = request.files['file'].read()
image = Image.open(io.BytesIO(file_bytes))
```

---

## Next Steps

1. **Implement config.py** - Start with configuration
2. **Implement model_loader.py** - Build core ML functionality
3. **Test model_loader independently** - Ensure it works before API
4. **Implement app.py** - Build the REST API
5. **Test locally** - Run the server and test with cURL/Postman
6. **Write unit tests** - Ensure code quality
7. **Containerize** - Move to Docker phase

---

## Getting Help

- Read the TODO comments in each stub file carefully
- Reference the architecture.md for system design
- Check official documentation (Flask, PyTorch, etc.)
- Test each component before moving to the next
- Use print statements liberally during development
- Ask for help in office hours if stuck

---

**Good luck with your implementation!**

**Document Version:** 1.0
**Last Updated:** October 2025
