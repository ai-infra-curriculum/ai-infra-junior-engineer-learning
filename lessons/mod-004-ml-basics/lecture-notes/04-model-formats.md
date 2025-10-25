# Lecture 04: Model Formats and Deployment Preparation

## Learning Objectives

By the end of this lecture, you will be able to:

- Understand ONNX (Open Neural Network Exchange) format and its benefits
- Convert PyTorch models to ONNX format
- Convert TensorFlow models to ONNX format
- Run inference with ONNX Runtime
- Choose appropriate model formats for different deployment scenarios
- Apply model optimization techniques (quantization, pruning)
- Package models for production deployment
- Understand model versioning and management strategies

**Duration**: 6-8 hours
**Difficulty**: Intermediate
**Prerequisites**: Lectures 01-03 (ML Overview, PyTorch, TensorFlow)

---

## 1. Introduction to ONNX

### What is ONNX?

**ONNX** (Open Neural Network Exchange) is an open format to represent machine learning models. It enables interoperability between different ML frameworks.

**Key Concept**: Train in any framework, deploy anywhere.

```
PyTorch Model  ─┐
                ├──→ ONNX Format ──→ ONNX Runtime ──→ Production
TensorFlow Model ─┘
```

### Why ONNX Matters for Infrastructure

**Problem Without ONNX**:
```
Data Scientists use PyTorch
  ↓
Infrastructure team only supports TensorFlow Serving
  ↓
Manual rewrite or complex workarounds needed
```

**Solution With ONNX**:
```
Data Scientists use any framework
  ↓
Convert to ONNX
  ↓
Deploy with ONNX Runtime (framework-agnostic)
```

### ONNX Benefits

| Benefit | Description | Impact |
|---------|-------------|--------|
| **Interoperability** | Framework-independent | No vendor lock-in |
| **Performance** | Optimized runtime | Faster inference |
| **Portability** | Works across platforms | Edge to cloud |
| **Standardization** | Common format | Easier tooling |
| **Optimization** | Built-in optimizations | Better resource usage |

### ONNX Ecosystem

```
┌─────────────────────────────────────────────────┐
│                   ONNX Format                   │
└─────────────────────────────────────────────────┘
         ↑                              ↓
    ┌────────┐                    ┌──────────┐
    │ Export │                    │  Deploy  │
    └────────┘                    └──────────┘
         ↑                              ↓
┌────────────────────┐          ┌──────────────────┐
│  PyTorch           │          │ ONNX Runtime     │
│  TensorFlow        │          │ - Python         │
│  scikit-learn      │          │ - C++            │
│  Keras             │          │ - JavaScript     │
│  MXNet             │          │ - Java           │
└────────────────────┘          │ - C#             │
                                └──────────────────┘
```

---

## 2. Converting PyTorch Models to ONNX

### Basic Conversion

```python
import torch
import torch.onnx

# Load PyTorch model
model = torch.hub.load('pytorch/vision', 'resnet18', pretrained=True)
model.eval()

# Create dummy input (must match model's expected input)
dummy_input = torch.randn(1, 3, 224, 224)

# Export to ONNX
torch.onnx.export(
    model,                      # Model to export
    dummy_input,                # Example input
    "resnet18.onnx",           # Output file path
    export_params=True,         # Store trained parameter weights
    opset_version=13,          # ONNX version
    do_constant_folding=True,   # Optimize constant folding
    input_names=['input'],      # Model input names
    output_names=['output'],    # Model output names
    dynamic_axes={              # Variable length axes
        'input': {0: 'batch_size'},
        'output': {0: 'batch_size'}
    }
)

print("Model exported to resnet18.onnx")
```

### Understanding Export Parameters

```python
torch.onnx.export(
    model,
    dummy_input,
    "model.onnx",

    # Export parameters
    export_params=True,         # Include weights (always True for inference)

    # ONNX version (opset)
    opset_version=13,          # 11-15 commonly supported, 13 recommended

    # Optimizations
    do_constant_folding=True,   # Fold constants at export time

    # Input/output configuration
    input_names=['images'],
    output_names=['predictions'],

    # Dynamic shapes (important for production!)
    dynamic_axes={
        'images': {0: 'batch_size'},      # Batch dimension is dynamic
        'predictions': {0: 'batch_size'}
    },

    # Verbosity
    verbose=False,              # Set True for debugging

    # Training mode
    training=torch.onnx.TrainingMode.EVAL  # Always EVAL for inference models
)
```

### Advanced: Converting Custom Models

```python
import torch
import torch.nn as nn

# Define custom model
class CustomModel(nn.Module):
    def __init__(self):
        super(CustomModel, self).__init__()
        self.conv1 = nn.Conv2d(3, 64, kernel_size=3, padding=1)
        self.relu = nn.ReLU()
        self.pool = nn.MaxPool2d(2, 2)
        self.fc = nn.Linear(64 * 112 * 112, 10)

    def forward(self, x):
        x = self.conv1(x)
        x = self.relu(x)
        x = self.pool(x)
        x = x.view(x.size(0), -1)
        x = self.fc(x)
        return x

# Create and export
model = CustomModel()
model.eval()

dummy_input = torch.randn(1, 3, 224, 224)

torch.onnx.export(
    model,
    dummy_input,
    "custom_model.onnx",
    export_params=True,
    opset_version=13,
    input_names=['input'],
    output_names=['output'],
    dynamic_axes={'input': {0: 'batch_size'}, 'output': {0: 'batch_size'}}
)

print("Custom model exported successfully")
```

### Verifying ONNX Export

```python
import onnx

# Load ONNX model
onnx_model = onnx.load("resnet18.onnx")

# Check that the model is well-formed
onnx.checker.check_model(onnx_model)

# Print model graph info
print("Model Inputs:")
for input in onnx_model.graph.input:
    print(f"  Name: {input.name}")
    print(f"  Shape: {[d.dim_value if d.dim_value > 0 else 'dynamic' for d in input.type.tensor_type.shape.dim]}")

print("\nModel Outputs:")
for output in onnx_model.graph.output:
    print(f"  Name: {output.name}")
    print(f"  Shape: {[d.dim_value if d.dim_value > 0 else 'dynamic' for d in output.type.tensor_type.shape.dim]}")

# Get model metadata
print(f"\nONNX Opset Version: {onnx_model.opset_import[0].version}")
print(f"Producer: {onnx_model.producer_name}")
```

---

## 3. Converting TensorFlow Models to ONNX

### Using tf2onnx

```bash
# Install tf2onnx
pip install tf2onnx
```

```python
import tensorflow as tf
import tf2onnx
import onnx

# Load TensorFlow model
model = tf.keras.applications.MobileNetV2(weights='imagenet')

# Get input signature
spec = (tf.TensorSpec((None, 224, 224, 3), tf.float32, name="input"),)

# Convert to ONNX
model_proto, _ = tf2onnx.convert.from_keras(
    model,
    input_signature=spec,
    opset=13,
    output_path="mobilenet_v2.onnx"
)

print("Model converted to ONNX")
```

### Converting from SavedModel

```python
import tf2onnx

# Convert SavedModel to ONNX
# This is the most reliable method for TensorFlow
!python -m tf2onnx.convert \
    --saved-model tensorflow_model/ \
    --output model.onnx \
    --opset 13

# Or in Python
model_proto, external_tensor_storage = tf2onnx.convert.from_saved_model(
    'tensorflow_model/',
    output_path='model.onnx',
    opset=13
)
```

### Handling Custom TensorFlow Operations

```python
import tensorflow as tf
import tf2onnx

# Some TensorFlow ops may not have ONNX equivalents
# Check supported ops: https://github.com/onnx/tensorflow-onnx/blob/master/support_status.md

# If conversion fails, try:
model_proto, _ = tf2onnx.convert.from_keras(
    model,
    input_signature=spec,
    opset=13,
    output_path="model.onnx",
    # Custom op handlers if needed
    custom_ops={
        'CustomOp': custom_op_handler
    }
)
```

---

## 4. Running Inference with ONNX Runtime

### Installation

```bash
# CPU version
pip install onnxruntime

# GPU version
pip install onnxruntime-gpu
```

### Basic Inference

```python
import onnxruntime as ort
import numpy as np

# Load ONNX model
session = ort.InferenceSession("resnet18.onnx")

# Get model metadata
input_name = session.get_inputs()[0].name
output_name = session.get_outputs()[0].name

print(f"Input name: {input_name}")
print(f"Input shape: {session.get_inputs()[0].shape}")
print(f"Input type: {session.get_inputs()[0].type}")

# Prepare input
input_data = np.random.randn(1, 3, 224, 224).astype(np.float32)

# Run inference
outputs = session.run([output_name], {input_name: input_data})

# Get results
predictions = outputs[0]
print(f"Output shape: {predictions.shape}")
```

### Production Inference Class

```python
import onnxruntime as ort
import numpy as np
from typing import Dict, List

class ONNXModel:
    def __init__(self, model_path: str, providers: List[str] = None):
        """
        Initialize ONNX model

        Args:
            model_path: Path to ONNX model file
            providers: Execution providers (e.g., ['CUDAExecutionProvider', 'CPUExecutionProvider'])
        """
        if providers is None:
            # Use GPU if available, otherwise CPU
            providers = ['CUDAExecutionProvider', 'CPUExecutionProvider'] if ort.get_device() == 'GPU' else ['CPUExecutionProvider']

        self.session = ort.InferenceSession(model_path, providers=providers)

        # Store input/output metadata
        self.input_name = self.session.get_inputs()[0].name
        self.output_name = self.session.get_outputs()[0].name
        self.input_shape = self.session.get_inputs()[0].shape

        print(f"Model loaded with {providers}")
        print(f"Input: {self.input_name} {self.input_shape}")
        print(f"Output: {self.output_name}")

    def predict(self, input_data: np.ndarray) -> np.ndarray:
        """Run inference on input data"""
        # Ensure correct dtype
        if input_data.dtype != np.float32:
            input_data = input_data.astype(np.float32)

        # Run inference
        outputs = self.session.run(
            [self.output_name],
            {self.input_name: input_data}
        )

        return outputs[0]

    def predict_batch(self, batch: List[np.ndarray]) -> np.ndarray:
        """Run inference on batch of inputs"""
        # Stack inputs
        batch_array = np.stack(batch)
        return self.predict(batch_array)

# Usage
model = ONNXModel("resnet18.onnx")
input_data = np.random.randn(1, 3, 224, 224).astype(np.float32)
output = model.predict(input_data)
print(f"Prediction shape: {output.shape}")
```

### Performance Comparison

```python
import torch
import onnxruntime as ort
import numpy as np
import time

# Load PyTorch model
torch_model = torch.hub.load('pytorch/vision', 'resnet18', pretrained=True)
torch_model.eval()

# Load ONNX model
onnx_session = ort.InferenceSession("resnet18.onnx")

# Prepare input
input_data = np.random.randn(1, 3, 224, 224).astype(np.float32)
torch_input = torch.from_numpy(input_data)

# Benchmark PyTorch
iterations = 100
start = time.time()
with torch.no_grad():
    for _ in range(iterations):
        _ = torch_model(torch_input)
pytorch_time = (time.time() - start) / iterations

# Benchmark ONNX Runtime
start = time.time()
for _ in range(iterations):
    _ = onnx_session.run(None, {"input": input_data})
onnx_time = (time.time() - start) / iterations

print(f"PyTorch inference time: {pytorch_time*1000:.2f} ms")
print(f"ONNX Runtime inference time: {onnx_time*1000:.2f} ms")
print(f"Speedup: {pytorch_time/onnx_time:.2f}x")
```

**Typical Results (CPU)**:
```
PyTorch inference time: 45.23 ms
ONNX Runtime inference time: 32.18 ms
Speedup: 1.41x
```

---

## 5. Model Optimization Techniques

### Quantization: Reducing Model Size

**What is Quantization?**
Converting model weights from float32 (32 bits) to int8 (8 bits), reducing size by ~4x.

```python
import torch

# Load model
model = torch.hub.load('pytorch/vision', 'resnet18', pretrained=True)
model.eval()

# Dynamic quantization (easiest, CPU only)
quantized_model = torch.quantization.quantize_dynamic(
    model,
    {torch.nn.Linear, torch.nn.Conv2d},
    dtype=torch.qint8
)

# Save quantized model
torch.save(quantized_model.state_dict(), "resnet18_quantized.pth")

# Compare sizes
import os
original_size = os.path.getsize("resnet18.pth") / (1024 ** 2)
quantized_size = os.path.getsize("resnet18_quantized.pth") / (1024 ** 2)

print(f"Original size: {original_size:.2f} MB")
print(f"Quantized size: {quantized_size:.2f} MB")
print(f"Size reduction: {(1 - quantized_size/original_size)*100:.1f}%")
```

### ONNX Quantization

```python
from onnxruntime.quantization import quantize_dynamic, QuantType

# Quantize ONNX model
quantize_dynamic(
    model_input="resnet18.onnx",
    model_output="resnet18_quantized.onnx",
    weight_type=QuantType.QUInt8  # or QInt8
)

print("Model quantized successfully")

# Compare sizes
import os
original = os.path.getsize("resnet18.onnx") / (1024 ** 2)
quantized = os.path.getsize("resnet18_quantized.onnx") / (1024 ** 2)

print(f"Original: {original:.2f} MB")
print(f"Quantized: {quantized:.2f} MB")
print(f"Reduction: {(1 - quantized/original)*100:.1f}%")
```

### Model Pruning (Removing Unnecessary Weights)

```python
import torch
import torch.nn.utils.prune as prune

# Load model
model = torch.hub.load('pytorch/vision', 'resnet18', pretrained=True)

# Prune 30% of weights in conv layers
for name, module in model.named_modules():
    if isinstance(module, torch.nn.Conv2d):
        prune.l1_unstructured(module, name='weight', amount=0.3)

# Make pruning permanent
for name, module in model.named_modules():
    if isinstance(module, torch.nn.Conv2d):
        prune.remove(module, 'weight')

print("Model pruned (30% of conv weights removed)")

# Accuracy will be lower - may need fine-tuning
```

### Knowledge Distillation (Advanced)

**Concept**: Train a smaller "student" model to mimic a larger "teacher" model.

```python
# Pseudocode - requires training
# 1. Load large teacher model
teacher = load_large_model()

# 2. Create smaller student model
student = create_small_model()

# 3. Train student to match teacher's outputs
for data, labels in dataloader:
    teacher_predictions = teacher(data)
    student_predictions = student(data)

    # Loss combines matching teacher and ground truth
    loss = distillation_loss(student_predictions, teacher_predictions, labels)
    loss.backward()
    optimizer.step()

# Result: Smaller, faster model with similar accuracy
```

---

## 6. Choosing the Right Model Format

### Decision Matrix

```
                                        ┌─────────────┐
                                        │  Deployment │
                                        │   Target    │
                                        └──────┬──────┘
                                               │
                    ┌──────────────────────────┼──────────────────────────┐
                    │                          │                          │
             ┌──────▼──────┐          ┌────────▼────────┐        ┌───────▼──────┐
             │   Server    │          │  Mobile/Edge    │        │   Browser    │
             └──────┬──────┘          └────────┬────────┘        └───────┬──────┘
                    │                          │                          │
        ┌───────────┼───────────┐              │                          │
        │           │           │              │                          │
   ┌────▼───┐  ┌───▼────┐  ┌───▼────┐   ┌─────▼─────┐            ┌──────▼──────┐
   │PyTorch │  │TensorFlow│ │  ONNX  │   │  TFLite   │            │TensorFlow.js│
   │TorchSrv│  │ Serving │  │ Runtime│   │  ONNX     │            │   ONNX.js   │
   └────────┘  └─────────┘  └────────┘   └───────────┘            └─────────────┘
```

### Format Selection Guide

| Scenario | Recommended Format | Reason |
|----------|-------------------|---------|
| **PyTorch native serving** | PyTorch + TorchServe | Native support, no conversion |
| **TensorFlow native serving** | SavedModel + TF Serving | Mature production tools |
| **Framework-agnostic** | ONNX + ONNX Runtime | Best interoperability |
| **Mobile (iOS/Android)** | TFLite or ONNX | Optimized for mobile |
| **Edge devices** | TFLite or ONNX | Small size, fast inference |
| **Browser** | TensorFlow.js or ONNX.js | JavaScript runtime |
| **Multi-framework support** | ONNX | Single serving infrastructure |
| **Maximum performance** | Native format + optimizations | Framework-specific optimizations |

### Production Recommendations

**Scenario 1: Single Framework Organization**
```
If data scientists use only PyTorch or only TensorFlow:
→ Use native format and serving tools
→ No need for ONNX conversion
→ Simpler infrastructure
```

**Scenario 2: Multi-Framework Organization**
```
If data scientists use both PyTorch and TensorFlow:
→ Standardize on ONNX for deployment
→ Convert all models to ONNX
→ Use ONNX Runtime for serving
→ Single serving infrastructure
```

**Scenario 3: Hybrid Approach**
```
For maximum flexibility:
→ Support both native and ONNX formats
→ Use native when possible (better performance)
→ Use ONNX for framework-agnostic deployments
→ Build infrastructure to handle both
```

---

## 7. Model Packaging for Production

### Creating a Model Package

```python
# model_package.py
import json
from pathlib import Path
import shutil
from datetime import datetime

class ModelPackage:
    """Package model with metadata for production deployment"""

    def __init__(self, name: str, version: str):
        self.name = name
        self.version = version
        self.package_dir = Path(f"{name}_v{version}")

    def create(self, model_path: str, metadata: dict):
        """Create model package"""
        # Create directory structure
        self.package_dir.mkdir(exist_ok=True)
        (self.package_dir / "model").mkdir(exist_ok=True)
        (self.package_dir / "metadata").mkdir(exist_ok=True)

        # Copy model files
        if Path(model_path).is_file():
            shutil.copy(model_path, self.package_dir / "model" / Path(model_path).name)
        else:
            shutil.copytree(model_path, self.package_dir / "model" / Path(model_path).name)

        # Create metadata
        full_metadata = {
            'name': self.name,
            'version': self.version,
            'created_at': datetime.now().isoformat(),
            'model_file': Path(model_path).name,
            **metadata
        }

        # Save metadata
        with open(self.package_dir / "metadata" / "model.json", 'w') as f:
            json.dump(full_metadata, f, indent=2)

        # Create requirements.txt
        self._create_requirements(metadata.get('framework', 'pytorch'))

        # Create README
        self._create_readme(full_metadata)

        print(f"Model package created: {self.package_dir}")

    def _create_requirements(self, framework: str):
        """Create requirements.txt"""
        requirements = {
            'pytorch': ['torch>=2.0.0', 'torchvision>=0.15.0'],
            'tensorflow': ['tensorflow>=2.13.0'],
            'onnx': ['onnxruntime>=1.15.0', 'onnx>=1.14.0']
        }

        with open(self.package_dir / "requirements.txt", 'w') as f:
            f.write('\n'.join(requirements.get(framework, [])))

    def _create_readme(self, metadata: dict):
        """Create README.md"""
        readme = f"""# {metadata['name']} v{metadata['version']}

## Model Information

- **Model**: {metadata['name']}
- **Version**: {metadata['version']}
- **Created**: {metadata['created_at']}
- **Framework**: {metadata.get('framework', 'N/A')}
- **Task**: {metadata.get('task', 'N/A')}

## Usage

```python
# Load model
from model_loader import load_model
model = load_model('model/{metadata['model_file']}')

# Run inference
output = model.predict(input_data)
```

## Metadata

```json
{json.dumps(metadata, indent=2)}
```
"""
        with open(self.package_dir / "README.md", 'w') as f:
            f.write(readme)

# Usage
packager = ModelPackage("resnet18", "1.0.0")
packager.create(
    "resnet18.onnx",
    metadata={
        'framework': 'onnx',
        'task': 'image_classification',
        'input_shape': [1, 3, 224, 224],
        'output_shape': [1, 1000],
        'accuracy': 0.697,
        'training_dataset': 'ImageNet',
        'author': 'Infrastructure Team'
    }
)
```

### Docker Image for Model Serving

```dockerfile
# Dockerfile
FROM python:3.11-slim

# Install dependencies
RUN pip install onnxruntime fastapi uvicorn numpy pillow

# Create app directory
WORKDIR /app

# Copy model
COPY resnet18.onnx /app/model.onnx

# Copy serving code
COPY serve.py /app/

# Expose port
EXPOSE 8000

# Run server
CMD ["python", "serve.py"]
```

```python
# serve.py
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import onnxruntime as ort
import numpy as np
from PIL import Image
import io

app = FastAPI()

# Load model at startup
session = ort.InferenceSession("model.onnx")
input_name = session.get_inputs()[0].name

def preprocess_image(image_bytes):
    """Preprocess image for model"""
    image = Image.open(io.BytesIO(image_bytes))
    image = image.resize((224, 224))
    image_array = np.array(image).astype(np.float32) / 255.0
    image_array = np.transpose(image_array, (2, 0, 1))  # HWC -> CHW
    image_array = np.expand_dims(image_array, axis=0)   # Add batch dim
    return image_array

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    # Read image
    image_bytes = await file.read()

    # Preprocess
    input_data = preprocess_image(image_bytes)

    # Run inference
    outputs = session.run(None, {input_name: input_data})

    # Get top prediction
    predictions = outputs[0][0]
    top_idx = int(np.argmax(predictions))
    confidence = float(predictions[top_idx])

    return JSONResponse({
        "prediction": top_idx,
        "confidence": confidence
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

---

## 8. Model Versioning and Management

### Versioning Strategy

```python
# model_version.py
from typing import Dict
from pathlib import Path
import json

class ModelVersionManager:
    """Manage model versions"""

    def __init__(self, base_path: str = "./models"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(exist_ok=True)

    def register_model(self, name: str, version: str, model_path: str, metadata: Dict):
        """Register a new model version"""
        # Create version directory
        version_dir = self.base_path / name / version
        version_dir.mkdir(parents=True, exist_ok=True)

        # Copy model
        import shutil
        shutil.copy(model_path, version_dir / "model.onnx")

        # Save metadata
        with open(version_dir / "metadata.json", 'w') as f:
            json.dump(metadata, f, indent=2)

        print(f"Registered {name} v{version}")

    def list_versions(self, name: str):
        """List all versions of a model"""
        model_dir = self.base_path / name
        if not model_dir.exists():
            return []

        versions = []
        for version_dir in sorted(model_dir.iterdir()):
            if version_dir.is_dir():
                metadata_file = version_dir / "metadata.json"
                if metadata_file.exists():
                    with open(metadata_file) as f:
                        metadata = json.load(f)
                    versions.append({
                        'version': version_dir.name,
                        'metadata': metadata
                    })

        return versions

    def get_latest_version(self, name: str):
        """Get the latest version of a model"""
        versions = self.list_versions(name)
        if not versions:
            return None

        # Assuming semantic versioning (e.g., 1.0.0, 1.1.0, 2.0.0)
        latest = sorted(versions, key=lambda x: x['version'], reverse=True)[0]
        return latest

# Usage
manager = ModelVersionManager()

# Register model v1
manager.register_model(
    "resnet18",
    "1.0.0",
    "resnet18_v1.onnx",
    {'accuracy': 0.695, 'size_mb': 44.7}
)

# Register model v2 (improved)
manager.register_model(
    "resnet18",
    "1.1.0",
    "resnet18_v2.onnx",
    {'accuracy': 0.705, 'size_mb': 42.3}
)

# List versions
versions = manager.list_versions("resnet18")
for v in versions:
    print(f"Version {v['version']}: accuracy={v['metadata']['accuracy']}")

# Get latest
latest = manager.get_latest_version("resnet18")
print(f"Latest version: {latest['version']}")
```

### A/B Testing Infrastructure

```python
import random
from typing import Dict

class ABTestRouter:
    """Route requests to different model versions for A/B testing"""

    def __init__(self):
        self.models: Dict[str, Dict] = {}

    def register_variant(self, variant_name: str, model_path: str, traffic_percentage: float):
        """Register a model variant for A/B testing"""
        self.models[variant_name] = {
            'model_path': model_path,
            'traffic': traffic_percentage,
            'requests': 0,
            'total_latency': 0.0
        }

    def route_request(self):
        """Route request to a variant based on traffic split"""
        # Simple random routing based on traffic percentages
        rand = random.random() * 100
        cumulative = 0

        for variant_name, config in self.models.items():
            cumulative += config['traffic']
            if rand <= cumulative:
                return variant_name

        # Fallback to first variant
        return list(self.models.keys())[0]

    def log_metrics(self, variant_name: str, latency: float):
        """Log metrics for analysis"""
        self.models[variant_name]['requests'] += 1
        self.models[variant_name]['total_latency'] += latency

    def get_stats(self):
        """Get performance statistics"""
        stats = {}
        for variant, config in self.models.items():
            avg_latency = (config['total_latency'] / config['requests']
                          if config['requests'] > 0 else 0)
            stats[variant] = {
                'requests': config['requests'],
                'avg_latency_ms': avg_latency * 1000,
                'traffic_allocation': config['traffic']
            }
        return stats

# Usage
router = ABTestRouter()
router.register_variant("model_v1", "resnet18_v1.onnx", traffic_percentage=50)
router.register_variant("model_v2", "resnet18_v2.onnx", traffic_percentage=50)

# Simulate requests
for _ in range(1000):
    variant = router.route_request()
    # ... run inference ...
    latency = 0.05  # Example latency
    router.log_metrics(variant, latency)

# Check stats
stats = router.get_stats()
print("A/B Test Results:")
for variant, metrics in stats.items():
    print(f"{variant}: {metrics['requests']} requests, {metrics['avg_latency_ms']:.2f}ms avg")
```

---

## Key Takeaways

### For Infrastructure Engineers

1. **ONNX enables interoperability**: Train anywhere, deploy anywhere
2. **Multiple formats exist**: Choose based on deployment target
3. **Optimization is important**: Quantization can reduce size by 4x
4. **Version management matters**: Always version your models
5. **Package models properly**: Include metadata and documentation
6. **A/B testing is essential**: Compare model versions in production
7. **ONNX Runtime is fast**: Often faster than native frameworks

### Production Checklist

- [ ] Model exported to appropriate format (ONNX, SavedModel, etc.)
- [ ] Model validated (accuracy matches original)
- [ ] Optimizations applied (quantization if appropriate)
- [ ] Model packaged with metadata
- [ ] Version number assigned
- [ ] Docker image built and tested
- [ ] Serving endpoint implemented
- [ ] Health checks configured
- [ ] Monitoring and logging added
- [ ] Documentation complete

---

## Quick Reference

### ONNX Conversion

```python
# PyTorch → ONNX
torch.onnx.export(model, dummy_input, "model.onnx", opset_version=13)

# TensorFlow → ONNX
python -m tf2onnx.convert --saved-model model/ --output model.onnx

# ONNX Inference
import onnxruntime as ort
session = ort.InferenceSession("model.onnx")
outputs = session.run(None, {input_name: input_data})
```

### Format Comparison

| Format | Best For | Size | Speed |
|--------|----------|------|-------|
| PyTorch (pth) | PyTorch development | Medium | Fast |
| TensorFlow (SavedModel) | TensorFlow Serving | Large | Fast |
| ONNX | Cross-framework | Medium | Very Fast |
| TFLite | Mobile/Edge | Small | Very Fast |

---

## What's Next?

You've completed all lectures in Module 004! Now it's time to:

1. **Complete the exercises**: Practice converting and deploying models
2. **Take the quiz**: Test your understanding
3. **Build a project**: Create an end-to-end model serving system

Continue to `exercises/exercise-01-pytorch-inference.md`

---

**Lecture Version**: 1.0
**Last Updated**: October 2025
**Estimated Completion Time**: 6-8 hours
**Difficulty**: Intermediate
