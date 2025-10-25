# Exercise 03: Model Format Conversion with ONNX

## Exercise Overview

**Objective**: Convert PyTorch and TensorFlow models to ONNX format, run inference with ONNX Runtime, and compare performance between native frameworks and ONNX.

**Difficulty**: Beginner-Intermediate
**Estimated Time**: 3-4 hours
**Prerequisites**: Lectures 02 (PyTorch Basics) and 03 (TensorFlow Basics), Exercise 01

**What You'll Learn**:
- Converting PyTorch models to ONNX format
- Converting TensorFlow models to ONNX format
- Running inference with ONNX Runtime
- Validating model conversions for accuracy
- Comparing performance across frameworks
- Understanding when and why to use ONNX

---

## Learning Objectives

By the end of this exercise, you will be able to:

✅ Export PyTorch models to ONNX using `torch.onnx.export()`
✅ Convert TensorFlow models to ONNX using `tf2onnx`
✅ Run inference with ONNX Runtime
✅ Validate converted models for numerical accuracy
✅ Measure and compare performance across formats
✅ Understand ONNX's role in AI infrastructure
✅ Make informed decisions about when to use ONNX

---

## Background: Why ONNX Matters for Infrastructure Engineers

### What is ONNX?

**ONNX (Open Neural Network Exchange)** is an open standard format for representing machine learning models. Think of it as a "universal translator" for ML models.

### Why Infrastructure Engineers Care About ONNX

1. **Framework Independence**: Deploy models without framework dependencies
2. **Optimization**: ONNX Runtime provides hardware-specific optimizations
3. **Interoperability**: Train in PyTorch, deploy with TensorFlow Serving, or vice versa
4. **Performance**: Often faster than native frameworks, especially for inference
5. **Deployment Flexibility**: One model format for multiple deployment targets
6. **Reduced Dependencies**: Smaller deployment footprint without full training frameworks

### Real-World Use Cases

- **Edge Deployment**: Reduce model size and dependency footprint for IoT devices
- **Multi-Framework Teams**: Standardize deployment regardless of training framework
- **Performance Optimization**: Leverage ONNX Runtime's optimized execution
- **Cloud Cost Reduction**: Faster inference = lower compute costs
- **Cross-Platform**: Same model runs on Windows, Linux, ARM, mobile, web

---

## Part 1: Environment Setup

### Step 1.1: Install Dependencies

```bash
# Create virtual environment
python -m venv onnx_env
source onnx_env/bin/activate  # On Windows: onnx_env\Scripts\activate

# Install PyTorch and TensorFlow
pip install torch torchvision
pip install tensorflow

# Install ONNX tools
pip install onnx onnxruntime
pip install tf2onnx
pip install onnxconverter-common

# Install utilities
pip install pillow numpy matplotlib
```

### Step 1.2: Verify Installation

```python
# verify_installation.py
import torch
import tensorflow as tf
import onnx
import onnxruntime as ort
import tf2onnx

print("=== Framework Versions ===")
print(f"PyTorch: {torch.__version__}")
print(f"TensorFlow: {tf.__version__}")
print(f"ONNX: {onnx.__version__}")
print(f"ONNX Runtime: {ort.__version__}")
print(f"tf2onnx: {tf2onnx.__version__}")

print("\n=== Device Information ===")
print(f"PyTorch CUDA available: {torch.cuda.is_available()}")
print(f"TensorFlow GPUs: {len(tf.config.list_physical_devices('GPU'))}")
print(f"ONNX Runtime providers: {ort.get_available_providers()}")
```

**Expected Output**:
```
=== Framework Versions ===
PyTorch: 2.1.0
TensorFlow: 2.14.0
ONNX: 1.15.0
ONNX Runtime: 1.16.3
tf2onnx: 1.15.1

=== Device Information ===
PyTorch CUDA available: True
TensorFlow GPUs: 1
ONNX Runtime providers: ['CUDAExecutionProvider', 'CPUExecutionProvider']
```

### Step 1.3: Download Test Resources

```python
# download_resources.py
import urllib.request
import os

# Create directories
os.makedirs("models", exist_ok=True)
os.makedirs("test_images", exist_ok=True)

# Download test image
image_url = "https://github.com/pytorch/hub/raw/master/images/dog.jpg"
urllib.request.urlretrieve(image_url, "test_images/dog.jpg")

# Download ImageNet labels
labels_url = "https://raw.githubusercontent.com/pytorch/hub/master/imagenet_classes.txt"
urllib.request.urlretrieve(labels_url, "imagenet_classes.txt")

print("✅ Resources downloaded!")
print("  - test_images/dog.jpg")
print("  - imagenet_classes.txt")
print("  - models/ directory created")
```

✅ **Checkpoint**: Environment set up with all necessary tools installed.

---

## Part 2: Converting PyTorch Models to ONNX

### Step 2.1: Export Simple PyTorch Model

```python
# pytorch_to_onnx_basic.py
import torch
import torch.nn as nn
import onnx

# Define a simple model
class SimpleNet(nn.Module):
    def __init__(self):
        super(SimpleNet, self).__init__()
        self.fc1 = nn.Linear(10, 20)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(20, 5)

    def forward(self, x):
        x = self.fc1(x)
        x = self.relu(x)
        x = self.fc2(x)
        return x

# Create model instance
model = SimpleNet()
model.eval()

# Create dummy input matching expected input shape
dummy_input = torch.randn(1, 10)

# Export to ONNX
onnx_path = "models/simple_net.onnx"
torch.onnx.export(
    model,                          # Model being exported
    dummy_input,                    # Example input for tracing
    onnx_path,                      # Where to save ONNX file
    export_params=True,             # Store trained parameters
    opset_version=14,               # ONNX version
    do_constant_folding=True,       # Optimize constants
    input_names=['input'],          # Input tensor names
    output_names=['output'],        # Output tensor names
    dynamic_axes={                  # Variable dimensions
        'input': {0: 'batch_size'},
        'output': {0: 'batch_size'}
    }
)

print(f"✅ Model exported to {onnx_path}")

# Verify the ONNX model
onnx_model = onnx.load(onnx_path)
onnx.checker.check_model(onnx_model)
print("✅ ONNX model is valid!")

# Print model information
print(f"\nModel info:")
print(f"  Inputs: {[inp.name for inp in onnx_model.graph.input]}")
print(f"  Outputs: {[out.name for out in onnx_model.graph.output]}")
print(f"  Operators: {len(onnx_model.graph.node)}")
```

**Expected Output**:
```
✅ Model exported to models/simple_net.onnx
✅ ONNX model is valid!

Model info:
  Inputs: ['input']
  Outputs: ['output']
  Operators: 3
```

### Step 2.2: Understanding Export Parameters

Let's understand each parameter in `torch.onnx.export()`:

```python
# export_parameters_explained.py
import torch
import torch.nn as nn

model = nn.Sequential(
    nn.Linear(10, 20),
    nn.ReLU(),
    nn.Linear(20, 5)
)
model.eval()

dummy_input = torch.randn(1, 10)

torch.onnx.export(
    model,
    dummy_input,
    "models/explained.onnx",

    # export_params=True: Include trained weights in ONNX file
    # Set to False if you only want the model structure
    export_params=True,

    # opset_version: ONNX operator set version
    # Higher versions support more operations but may have less support
    # Version 14+ is recommended for modern models
    opset_version=14,

    # do_constant_folding=True: Optimize constant expressions at export time
    # Example: 2*3 becomes 6 directly in the graph
    do_constant_folding=True,

    # input_names/output_names: Human-readable names for tensors
    # Crucial for identifying inputs/outputs when loading the model
    input_names=['features'],
    output_names=['predictions'],

    # dynamic_axes: Allow variable dimensions
    # Dimension 0 (batch_size) can vary at runtime
    dynamic_axes={
        'features': {0: 'batch_size'},
        'predictions': {0: 'batch_size'}
    },

    # verbose=True: Print detailed export information (useful for debugging)
    verbose=False
)

print("✅ Model exported with all parameters explained!")
```

### Step 2.3: Export ResNet50 to ONNX

Now let's export a real pre-trained model:

```python
# pytorch_resnet_to_onnx.py
import torch
import torchvision.models as models
import onnx
import os

print("Loading ResNet50...")
model = models.resnet50(pretrained=True)
model.eval()

# Create example input (ImageNet size)
batch_size = 1
dummy_input = torch.randn(batch_size, 3, 224, 224)

# Export to ONNX
onnx_path = "models/resnet50.onnx"
print(f"Exporting to {onnx_path}...")

torch.onnx.export(
    model,
    dummy_input,
    onnx_path,
    export_params=True,
    opset_version=14,
    do_constant_folding=True,
    input_names=['input'],
    output_names=['output'],
    dynamic_axes={
        'input': {0: 'batch_size'},
        'output': {0: 'batch_size'}
    }
)

print("✅ Export complete!")

# Verify ONNX model
print("\nVerifying ONNX model...")
onnx_model = onnx.load(onnx_path)
onnx.checker.check_model(onnx_model)
print("✅ ONNX model is valid!")

# Model statistics
file_size_mb = os.path.getsize(onnx_path) / (1024 * 1024)
print(f"\nModel Statistics:")
print(f"  File size: {file_size_mb:.2f} MB")
print(f"  Graph nodes: {len(onnx_model.graph.node)}")
print(f"  Inputs: {[i.name for i in onnx_model.graph.input]}")
print(f"  Outputs: {[o.name for o in onnx_model.graph.output]}")
```

**Expected Output**:
```
Loading ResNet50...
Exporting to models/resnet50.onnx...
✅ Export complete!

Verifying ONNX model...
✅ ONNX model is valid!

Model Statistics:
  File size: 97.53 MB
  Graph nodes: 176
  Inputs: ['input']
  Outputs: ['output']
```

✅ **Checkpoint**: You can export PyTorch models to ONNX format.

---

## Part 3: Converting TensorFlow Models to ONNX

### Step 3.1: Export Keras Model to ONNX

```python
# tensorflow_to_onnx_basic.py
import tensorflow as tf
import tf2onnx
import onnx

# Create a simple Keras model
model = tf.keras.Sequential([
    tf.keras.layers.Input(shape=(10,)),
    tf.keras.layers.Dense(20, activation='relu'),
    tf.keras.layers.Dense(5, activation='softmax')
])

print("Model created:")
model.summary()

# Convert to ONNX
# Method 1: Direct conversion from Keras model
onnx_path = "models/keras_model.onnx"

spec = (tf.TensorSpec((None, 10), tf.float32, name="input"),)
model_proto, _ = tf2onnx.convert.from_keras(
    model,
    input_signature=spec,
    opset=14,
    output_path=onnx_path
)

print(f"\n✅ Model exported to {onnx_path}")

# Verify ONNX model
onnx_model = onnx.load(onnx_path)
onnx.checker.check_model(onnx_model)
print("✅ ONNX model is valid!")
```

### Step 3.2: Export TensorFlow SavedModel to ONNX

```python
# tensorflow_savedmodel_to_onnx.py
import tensorflow as tf
import tf2onnx
import onnx
import tempfile
import os

print("Loading MobileNetV2...")
model = tf.keras.applications.MobileNetV2(
    weights='imagenet',
    input_shape=(224, 224, 3)
)

# Save as TensorFlow SavedModel first
saved_model_dir = "models/mobilenet_saved"
print(f"Saving to {saved_model_dir}...")
model.save(saved_model_dir)

# Convert SavedModel to ONNX
onnx_path = "models/mobilenet_v2.onnx"
print(f"Converting to ONNX: {onnx_path}...")

os.system(f"python -m tf2onnx.convert \
    --saved-model {saved_model_dir} \
    --output {onnx_path} \
    --opset 14")

print("\n✅ Conversion complete!")

# Verify
onnx_model = onnx.load(onnx_path)
onnx.checker.check_model(onnx_model)
print("✅ ONNX model is valid!")

# Model info
file_size_mb = os.path.getsize(onnx_path) / (1024 * 1024)
print(f"\nModel Statistics:")
print(f"  File size: {file_size_mb:.2f} MB")
print(f"  Graph nodes: {len(onnx_model.graph.node)}")
```

### Step 3.3: Alternative Conversion Method

```python
# tensorflow_to_onnx_alternative.py
import tensorflow as tf
import tf2onnx
import numpy as np

# Load model
model = tf.keras.applications.MobileNetV2(
    weights='imagenet',
    input_shape=(224, 224, 3)
)

# Method 2: Convert using concrete function
onnx_path = "models/mobilenet_v2_alt.onnx"

# Get concrete function
concrete_func = tf.function(lambda x: model(x))
concrete_func = concrete_func.get_concrete_function(
    tf.TensorSpec(model.inputs[0].shape, model.inputs[0].dtype)
)

# Convert to ONNX
model_proto, _ = tf2onnx.convert.from_function(
    concrete_func,
    input_signature=[tf.TensorSpec([None, 224, 224, 3], tf.float32, name="input")],
    opset=14,
    output_path=onnx_path
)

print(f"✅ Model exported to {onnx_path}")
```

✅ **Checkpoint**: You can convert both PyTorch and TensorFlow models to ONNX.

---

## Part 4: Running Inference with ONNX Runtime

### Step 4.1: Basic ONNX Runtime Inference

```python
# onnx_runtime_basic.py
import onnxruntime as ort
import numpy as np

# Load ONNX model
print("Loading ONNX model...")
onnx_path = "models/simple_net.onnx"
session = ort.InferenceSession(onnx_path)

# Get model metadata
print("\n=== Model Information ===")
print(f"Inputs:")
for input_meta in session.get_inputs():
    print(f"  Name: {input_meta.name}")
    print(f"  Shape: {input_meta.shape}")
    print(f"  Type: {input_meta.type}")

print(f"\nOutputs:")
for output_meta in session.get_outputs():
    print(f"  Name: {output_meta.name}")
    print(f"  Shape: {output_meta.shape}")
    print(f"  Type: {output_meta.type}")

# Prepare input
input_name = session.get_inputs()[0].name
input_data = np.random.randn(1, 10).astype(np.float32)

# Run inference
print("\n=== Running Inference ===")
outputs = session.run(None, {input_name: input_data})

print(f"Output shape: {outputs[0].shape}")
print(f"Output values: {outputs[0]}")
```

**Expected Output**:
```
Loading ONNX model...

=== Model Information ===
Inputs:
  Name: input
  Shape: ['batch_size', 10]
  Type: tensor(float)

Outputs:
  Name: output
  Shape: ['batch_size', 5]
  Type: tensor(float)

=== Running Inference ===
Output shape: (1, 5)
Output values: [[-0.123  0.456 -0.789  0.234 -0.567]]
```

### Step 4.2: ResNet50 Inference with ONNX Runtime

```python
# onnx_resnet_inference.py
import onnxruntime as ort
import numpy as np
from PIL import Image
import urllib.request

# Load ImageNet labels
labels_url = "https://raw.githubusercontent.com/pytorch/hub/master/imagenet_classes.txt"
urllib.request.urlretrieve(labels_url, "imagenet_classes.txt")
with open("imagenet_classes.txt") as f:
    labels = [line.strip() for line in f.readlines()]

# Load ONNX model
print("Loading ONNX ResNet50...")
session = ort.InferenceSession("models/resnet50.onnx")

# Get input name
input_name = session.get_inputs()[0].name
output_name = session.get_outputs()[0].name

print(f"Input name: {input_name}")
print(f"Output name: {output_name}")

# Load and preprocess image
def preprocess_image(image_path):
    """Preprocess image for ResNet50"""
    from PIL import Image
    import numpy as np

    # Load image
    image = Image.open(image_path).convert('RGB')

    # Resize and center crop
    image = image.resize((256, 256))
    left = (256 - 224) / 2
    top = (256 - 224) / 2
    right = left + 224
    bottom = top + 224
    image = image.crop((left, top, right, bottom))

    # Convert to array and normalize
    img_array = np.array(image).astype(np.float32) / 255.0

    # Normalize with ImageNet stats
    mean = np.array([0.485, 0.456, 0.406])
    std = np.array([0.229, 0.224, 0.225])
    img_array = (img_array - mean) / std

    # Transpose to CHW format and add batch dimension
    img_array = img_array.transpose(2, 0, 1)
    img_array = np.expand_dims(img_array, axis=0)

    return img_array

# Preprocess image
image_path = "test_images/dog.jpg"
print(f"\nPreprocessing {image_path}...")
input_data = preprocess_image(image_path)
print(f"Input shape: {input_data.shape}")
print(f"Input dtype: {input_data.dtype}")

# Run inference
print("\nRunning inference...")
outputs = session.run([output_name], {input_name: input_data})
predictions = outputs[0][0]

# Get top 5 predictions
top5_indices = np.argsort(predictions)[-5:][::-1]

# Apply softmax to get probabilities
exp_predictions = np.exp(predictions - np.max(predictions))
probabilities = exp_predictions / exp_predictions.sum()

print("\nTop 5 Predictions:")
for i, idx in enumerate(top5_indices):
    print(f"  {i+1}. {labels[idx]:<30} {probabilities[idx]*100:>6.2f}%")
```

**Expected Output**:
```
Loading ONNX ResNet50...
Input name: input
Output name: output

Preprocessing test_images/dog.jpg...
Input shape: (1, 3, 224, 224)
Input dtype: float32

Running inference...

Top 5 Predictions:
  1. Samoyed                      87.34%
  2. Pomeranian                    5.23%
  3. white wolf                    3.45%
  4. keeshond                      2.11%
  5. Great Pyrenees                1.34%
```

### Step 4.3: Choosing Execution Providers

ONNX Runtime supports multiple execution providers for hardware acceleration:

```python
# onnx_execution_providers.py
import onnxruntime as ort
import numpy as np

# List available providers
print("Available execution providers:")
for provider in ort.get_available_providers():
    print(f"  - {provider}")

# Create sessions with different providers
onnx_path = "models/resnet50.onnx"

# CPU Provider
print("\n=== CPU Execution Provider ===")
cpu_session = ort.InferenceSession(
    onnx_path,
    providers=['CPUExecutionProvider']
)
print(f"Using: {cpu_session.get_providers()}")

# CUDA Provider (if available)
if 'CUDAExecutionProvider' in ort.get_available_providers():
    print("\n=== CUDA Execution Provider ===")
    cuda_session = ort.InferenceSession(
        onnx_path,
        providers=['CUDAExecutionProvider', 'CPUExecutionProvider']
    )
    print(f"Using: {cuda_session.get_providers()}")
else:
    print("\n⚠️  CUDA not available")

# Other providers (if available)
# - TensorrtExecutionProvider: NVIDIA TensorRT
# - OpenVINOExecutionProvider: Intel OpenVINO
# - CoreMLExecutionProvider: Apple CoreML
# - DmlExecutionProvider: DirectML (Windows)
```

✅ **Checkpoint**: You can run inference with ONNX Runtime on converted models.

---

## Part 5: Model Validation

### Step 5.1: Validate PyTorch to ONNX Conversion

```python
# validate_pytorch_onnx.py
import torch
import torch.nn as nn
import onnxruntime as ort
import numpy as np

# Load PyTorch model
print("Loading PyTorch ResNet50...")
pytorch_model = torch.hub.load('pytorch/vision', 'resnet50', pretrained=True)
pytorch_model.eval()

# Load ONNX model
print("Loading ONNX ResNet50...")
onnx_session = ort.InferenceSession("models/resnet50.onnx")

# Create test input
batch_size = 1
test_input = torch.randn(batch_size, 3, 224, 224)
print(f"\nTest input shape: {test_input.shape}")

# PyTorch inference
print("\nRunning PyTorch inference...")
with torch.no_grad():
    pytorch_output = pytorch_model(test_input)
pytorch_result = pytorch_output.numpy()

# ONNX inference
print("Running ONNX inference...")
input_name = onnx_session.get_inputs()[0].name
onnx_result = onnx_session.run(None, {input_name: test_input.numpy()})[0]

# Compare outputs
print("\n=== Validation Results ===")
print(f"PyTorch output shape: {pytorch_result.shape}")
print(f"ONNX output shape: {onnx_result.shape}")

# Calculate differences
absolute_diff = np.abs(pytorch_result - onnx_result)
max_diff = np.max(absolute_diff)
mean_diff = np.mean(absolute_diff)
relative_diff = np.mean(np.abs(pytorch_result - onnx_result) / (np.abs(pytorch_result) + 1e-8))

print(f"\nNumerical Comparison:")
print(f"  Max absolute difference: {max_diff:.6f}")
print(f"  Mean absolute difference: {mean_diff:.6f}")
print(f"  Mean relative difference: {relative_diff:.6f}")

# Check if outputs are close
tolerance = 1e-5
if np.allclose(pytorch_result, onnx_result, rtol=tolerance, atol=tolerance):
    print(f"\n✅ PASS: Outputs match within tolerance ({tolerance})")
else:
    print(f"\n❌ FAIL: Outputs differ beyond tolerance ({tolerance})")

# Compare top predictions
pytorch_top5 = np.argsort(pytorch_result[0])[-5:][::-1]
onnx_top5 = np.argsort(onnx_result[0])[-5:][::-1]

print(f"\nTop 5 Class Predictions:")
print(f"  PyTorch: {pytorch_top5}")
print(f"  ONNX:    {onnx_top5}")

if np.array_equal(pytorch_top5, onnx_top5):
    print("  ✅ Top 5 predictions match!")
else:
    print("  ⚠️  Top 5 predictions differ")
```

**Expected Output**:
```
Loading PyTorch ResNet50...
Loading ONNX ResNet50...

Test input shape: torch.Size([1, 3, 224, 224])

Running PyTorch inference...
Running ONNX inference...

=== Validation Results ===
PyTorch output shape: (1, 1000)
ONNX output shape: (1, 1000)

Numerical Comparison:
  Max absolute difference: 0.000012
  Mean absolute difference: 0.000003
  Mean relative difference: 0.000001

✅ PASS: Outputs match within tolerance (1e-05)

Top 5 Class Predictions:
  PyTorch: [259 261 260 262 263]
  ONNX:    [259 261 260 262 263]
  ✅ Top 5 predictions match!
```

### Step 5.2: Comprehensive Validation Suite

```python
# validation_suite.py
import torch
import onnxruntime as ort
import numpy as np
from typing import Dict, Tuple

class ModelValidator:
    """Validate ONNX model against PyTorch original"""

    def __init__(self, pytorch_model: torch.nn.Module, onnx_path: str):
        self.pytorch_model = pytorch_model
        self.pytorch_model.eval()
        self.onnx_session = ort.InferenceSession(onnx_path)
        self.input_name = self.onnx_session.get_inputs()[0].name

    def validate(self, test_inputs: list, tolerance: float = 1e-5) -> Dict:
        """Run validation on multiple test inputs"""
        results = {
            'passed': 0,
            'failed': 0,
            'max_diff': 0.0,
            'mean_diff': 0.0,
            'details': []
        }

        print(f"Running validation on {len(test_inputs)} test cases...")

        for i, test_input in enumerate(test_inputs):
            # PyTorch inference
            with torch.no_grad():
                pytorch_output = self.pytorch_model(test_input).numpy()

            # ONNX inference
            onnx_output = self.onnx_session.run(
                None,
                {self.input_name: test_input.numpy()}
            )[0]

            # Calculate differences
            abs_diff = np.abs(pytorch_output - onnx_output)
            max_diff = np.max(abs_diff)
            mean_diff = np.mean(abs_diff)

            # Update results
            results['max_diff'] = max(results['max_diff'], max_diff)
            results['mean_diff'] += mean_diff

            # Check if passed
            passed = np.allclose(pytorch_output, onnx_output, rtol=tolerance, atol=tolerance)
            if passed:
                results['passed'] += 1
                status = '✅'
            else:
                results['failed'] += 1
                status = '❌'

            results['details'].append({
                'test_case': i,
                'max_diff': max_diff,
                'mean_diff': mean_diff,
                'passed': passed
            })

            print(f"  Test {i+1}: {status} (max_diff: {max_diff:.6f})")

        results['mean_diff'] /= len(test_inputs)
        return results

# Example usage
print("Loading models...")
pytorch_model = torch.hub.load('pytorch/vision', 'resnet18', pretrained=True)
pytorch_model.eval()

# Export to ONNX
torch.onnx.export(
    pytorch_model,
    torch.randn(1, 3, 224, 224),
    "models/resnet18.onnx",
    export_params=True,
    opset_version=14,
    input_names=['input'],
    output_names=['output']
)

# Create validator
validator = ModelValidator(pytorch_model, "models/resnet18.onnx")

# Generate test inputs with different characteristics
test_inputs = [
    torch.randn(1, 3, 224, 224),           # Random normal
    torch.zeros(1, 3, 224, 224),           # All zeros
    torch.ones(1, 3, 224, 224),            # All ones
    torch.randn(1, 3, 224, 224) * 0.1,     # Small values
    torch.randn(1, 3, 224, 224) * 10,      # Large values
]

# Run validation
results = validator.validate(test_inputs, tolerance=1e-5)

# Print summary
print("\n=== Validation Summary ===")
print(f"Total tests: {len(test_inputs)}")
print(f"Passed: {results['passed']}")
print(f"Failed: {results['failed']}")
print(f"Max difference: {results['max_diff']:.6f}")
print(f"Mean difference: {results['mean_diff']:.6f}")

if results['failed'] == 0:
    print("\n✅ All validation tests passed!")
else:
    print(f"\n⚠️  {results['failed']} tests failed")
```

✅ **Checkpoint**: You can validate ONNX models for numerical accuracy.

---

## Part 6: Performance Comparison

### Step 6.1: Latency Comparison

```python
# performance_comparison.py
import torch
import onnxruntime as ort
import numpy as np
import time
from typing import Dict

def benchmark_pytorch(model, input_tensor, iterations=100, warmup=10):
    """Benchmark PyTorch model"""
    model.eval()

    # Warmup
    with torch.no_grad():
        for _ in range(warmup):
            _ = model(input_tensor)

    # Measure
    start = time.time()
    with torch.no_grad():
        for _ in range(iterations):
            _ = model(input_tensor)
    elapsed = time.time() - start

    return (elapsed / iterations) * 1000  # ms

def benchmark_onnx(session, input_name, input_data, iterations=100, warmup=10):
    """Benchmark ONNX Runtime"""

    # Warmup
    for _ in range(warmup):
        _ = session.run(None, {input_name: input_data})

    # Measure
    start = time.time()
    for _ in range(iterations):
        _ = session.run(None, {input_name: input_data})
    elapsed = time.time() - start

    return (elapsed / iterations) * 1000  # ms

# Load models
print("Loading models...")
pytorch_model = torch.hub.load('pytorch/vision', 'resnet50', pretrained=True)
pytorch_model.eval()

onnx_session = ort.InferenceSession("models/resnet50.onnx")
input_name = onnx_session.get_inputs()[0].name

# Test different batch sizes
batch_sizes = [1, 4, 8, 16]
print("\n=== Performance Comparison (CPU) ===")
print(f"{'Batch Size':<12} {'PyTorch (ms)':<15} {'ONNX (ms)':<15} {'Speedup':<10}")
print("-" * 55)

for batch_size in batch_sizes:
    # Prepare inputs
    pytorch_input = torch.randn(batch_size, 3, 224, 224)
    onnx_input = pytorch_input.numpy()

    # Benchmark
    pytorch_time = benchmark_pytorch(pytorch_model, pytorch_input, iterations=50)
    onnx_time = benchmark_onnx(onnx_session, input_name, onnx_input, iterations=50)

    speedup = pytorch_time / onnx_time

    print(f"{batch_size:<12} {pytorch_time:<15.2f} {onnx_time:<15.2f} {speedup:<10.2f}x")
```

**Expected Output (CPU)**:
```
Loading models...

=== Performance Comparison (CPU) ===
Batch Size   PyTorch (ms)    ONNX (ms)       Speedup
-------------------------------------------------------
1            45.23           32.18           1.41x
4            167.89          118.45          1.42x
8            329.34          228.91          1.44x
16           645.78          447.23          1.44x
```

### Step 6.2: Comprehensive Performance Suite

```python
# performance_suite.py
import torch
import onnxruntime as ort
import numpy as np
import time
import psutil
import os

class PerformanceBenchmark:
    """Comprehensive performance benchmarking"""

    def __init__(self):
        self.results = {}

    def measure_latency(self, func, iterations=100, warmup=10):
        """Measure average latency"""
        # Warmup
        for _ in range(warmup):
            func()

        # Measure
        latencies = []
        for _ in range(iterations):
            start = time.perf_counter()
            func()
            elapsed = time.perf_counter() - start
            latencies.append(elapsed * 1000)  # ms

        return {
            'mean': np.mean(latencies),
            'std': np.std(latencies),
            'min': np.min(latencies),
            'max': np.max(latencies),
            'p50': np.percentile(latencies, 50),
            'p95': np.percentile(latencies, 95),
            'p99': np.percentile(latencies, 99)
        }

    def measure_throughput(self, func, duration_sec=5):
        """Measure throughput (iterations per second)"""
        count = 0
        start = time.time()

        while time.time() - start < duration_sec:
            func()
            count += 1

        elapsed = time.time() - start
        return count / elapsed

    def measure_memory(self, func):
        """Measure memory usage"""
        process = psutil.Process(os.getpid())

        # Initial memory
        mem_before = process.memory_info().rss / 1024 / 1024  # MB

        # Run function
        func()

        # Final memory
        mem_after = process.memory_info().rss / 1024 / 1024  # MB

        return {
            'before_mb': mem_before,
            'after_mb': mem_after,
            'delta_mb': mem_after - mem_before
        }

    def benchmark_model(self, name, inference_func):
        """Run complete benchmark suite"""
        print(f"\n{'='*50}")
        print(f"Benchmarking: {name}")
        print(f"{'='*50}")

        # Latency
        print("\n📊 Latency Statistics:")
        latency_stats = self.measure_latency(inference_func, iterations=100)
        for key, value in latency_stats.items():
            print(f"  {key:>6}: {value:>8.3f} ms")

        # Throughput
        print("\n🚀 Throughput:")
        throughput = self.measure_throughput(inference_func, duration_sec=3)
        print(f"  {throughput:.2f} inferences/second")

        # Memory
        print("\n💾 Memory Usage:")
        memory_stats = self.measure_memory(inference_func)
        print(f"  Before: {memory_stats['before_mb']:.2f} MB")
        print(f"  After:  {memory_stats['after_mb']:.2f} MB")
        print(f"  Delta:  {memory_stats['delta_mb']:.2f} MB")

        self.results[name] = {
            'latency': latency_stats,
            'throughput': throughput,
            'memory': memory_stats
        }

    def print_comparison(self):
        """Print comparison between all benchmarked models"""
        print(f"\n\n{'='*70}")
        print("PERFORMANCE COMPARISON SUMMARY")
        print(f"{'='*70}")

        if len(self.results) < 2:
            print("Need at least 2 models to compare")
            return

        models = list(self.results.keys())
        baseline = models[0]
        comparison = models[1]

        baseline_latency = self.results[baseline]['latency']['mean']
        comparison_latency = self.results[comparison]['latency']['mean']
        latency_speedup = baseline_latency / comparison_latency

        baseline_throughput = self.results[baseline]['throughput']
        comparison_throughput = self.results[comparison]['throughput']
        throughput_improvement = comparison_throughput / baseline_throughput

        print(f"\n📊 {comparison} vs {baseline}:")
        print(f"  Latency:    {latency_speedup:>6.2f}x {'faster' if latency_speedup > 1 else 'slower'}")
        print(f"  Throughput: {throughput_improvement:>6.2f}x {'higher' if throughput_improvement > 1 else 'lower'}")

# Example usage
print("Setting up benchmark...")

# Load PyTorch model
pytorch_model = torch.hub.load('pytorch/vision', 'mobilenet_v2', pretrained=True)
pytorch_model.eval()
pytorch_input = torch.randn(1, 3, 224, 224)

# Load ONNX model
onnx_session = ort.InferenceSession("models/mobilenet_v2.onnx")
input_name = onnx_session.get_inputs()[0].name
onnx_input = pytorch_input.numpy()

# Create benchmark
benchmark = PerformanceBenchmark()

# Benchmark PyTorch
pytorch_func = lambda: pytorch_model(pytorch_input)
benchmark.benchmark_model("PyTorch MobileNetV2", pytorch_func)

# Benchmark ONNX
onnx_func = lambda: onnx_session.run(None, {input_name: onnx_input})
benchmark.benchmark_model("ONNX MobileNetV2", onnx_func)

# Print comparison
benchmark.print_comparison()
```

**Expected Output**:
```
==================================================
Benchmarking: PyTorch MobileNetV2
==================================================

📊 Latency Statistics:
    mean:   18.234 ms
     std:    1.456 ms
     min:   16.123 ms
     max:   23.456 ms
     p50:   18.012 ms
     p95:   20.567 ms
     p99:   22.345 ms

🚀 Throughput:
  54.32 inferences/second

💾 Memory Usage:
  Before: 245.67 MB
  After:  245.89 MB
  Delta:  0.22 MB

==================================================
Benchmarking: ONNX MobileNetV2
==================================================

📊 Latency Statistics:
    mean:   12.456 ms
     std:    0.987 ms
     min:   11.234 ms
     max:   15.678 ms
     p50:   12.345 ms
     p95:   13.456 ms
     p99:   14.234 ms

🚀 Throughput:
  79.87 inferences/second

💾 Memory Usage:
  Before: 245.89 MB
  After:  246.01 MB
  Delta:  0.12 MB

======================================================================
PERFORMANCE COMPARISON SUMMARY
======================================================================

📊 ONNX MobileNetV2 vs PyTorch MobileNetV2:
  Latency:      1.46x faster
  Throughput:   1.47x higher
```

✅ **Checkpoint**: You can comprehensively measure and compare performance.

---

## Part 7: Production-Ready Conversion Script

### Step 7.1: Complete Conversion Tool

```python
# model_converter.py
"""
Production-ready model conversion tool
Converts PyTorch and TensorFlow models to ONNX with validation
"""

import torch
import onnx
import onnxruntime as ort
import numpy as np
import argparse
import os
from typing import Optional, Tuple
import json

class ModelConverter:
    """Convert and validate models to ONNX format"""

    def __init__(self, validate: bool = True, verbose: bool = True):
        self.validate = validate
        self.verbose = verbose
        self.conversion_report = {}

    def log(self, message: str):
        """Print message if verbose"""
        if self.verbose:
            print(message)

    def convert_pytorch(
        self,
        model: torch.nn.Module,
        dummy_input: torch.Tensor,
        output_path: str,
        input_names: list = ['input'],
        output_names: list = ['output'],
        dynamic_axes: Optional[dict] = None,
        opset_version: int = 14
    ) -> bool:
        """Convert PyTorch model to ONNX"""

        self.log(f"\n{'='*60}")
        self.log("Converting PyTorch Model to ONNX")
        self.log(f"{'='*60}")

        try:
            # Ensure model is in eval mode
            model.eval()

            # Default dynamic axes for batch size
            if dynamic_axes is None:
                dynamic_axes = {
                    input_names[0]: {0: 'batch_size'},
                    output_names[0]: {0: 'batch_size'}
                }

            # Export to ONNX
            self.log(f"\n📤 Exporting to {output_path}...")
            torch.onnx.export(
                model,
                dummy_input,
                output_path,
                export_params=True,
                opset_version=opset_version,
                do_constant_folding=True,
                input_names=input_names,
                output_names=output_names,
                dynamic_axes=dynamic_axes,
                verbose=False
            )

            # Verify ONNX model
            self.log("✅ Checking ONNX model validity...")
            onnx_model = onnx.load(output_path)
            onnx.checker.check_model(onnx_model)
            self.log("✅ ONNX model is valid!")

            # Store model info
            file_size = os.path.getsize(output_path) / (1024 * 1024)
            self.conversion_report['output_path'] = output_path
            self.conversion_report['file_size_mb'] = round(file_size, 2)
            self.conversion_report['opset_version'] = opset_version

            self.log(f"\n📊 Model Statistics:")
            self.log(f"  File size: {file_size:.2f} MB")
            self.log(f"  Opset version: {opset_version}")
            self.log(f"  Graph nodes: {len(onnx_model.graph.node)}")

            # Validate if requested
            if self.validate:
                self.log("\n🔍 Validating conversion accuracy...")
                validation_passed = self._validate_pytorch_conversion(
                    model, output_path, dummy_input
                )
                self.conversion_report['validation_passed'] = validation_passed

                if validation_passed:
                    self.log("✅ Validation passed!")
                else:
                    self.log("⚠️  Validation failed - outputs differ significantly")
                    return False

            self.log("\n✅ Conversion successful!")
            return True

        except Exception as e:
            self.log(f"\n❌ Conversion failed: {str(e)}")
            self.conversion_report['error'] = str(e)
            return False

    def _validate_pytorch_conversion(
        self,
        pytorch_model: torch.nn.Module,
        onnx_path: str,
        test_input: torch.Tensor,
        tolerance: float = 1e-5
    ) -> bool:
        """Validate PyTorch to ONNX conversion"""

        # PyTorch inference
        with torch.no_grad():
            pytorch_output = pytorch_model(test_input).numpy()

        # ONNX inference
        onnx_session = ort.InferenceSession(onnx_path)
        input_name = onnx_session.get_inputs()[0].name
        onnx_output = onnx_session.run(None, {input_name: test_input.numpy()})[0]

        # Compare
        abs_diff = np.abs(pytorch_output - onnx_output)
        max_diff = np.max(abs_diff)
        mean_diff = np.mean(abs_diff)

        self.log(f"  Max difference: {max_diff:.6f}")
        self.log(f"  Mean difference: {mean_diff:.6f}")

        self.conversion_report['max_difference'] = float(max_diff)
        self.conversion_report['mean_difference'] = float(mean_diff)

        return np.allclose(pytorch_output, onnx_output, rtol=tolerance, atol=tolerance)

    def save_report(self, output_path: str = "conversion_report.json"):
        """Save conversion report to JSON"""
        with open(output_path, 'w') as f:
            json.dump(self.conversion_report, f, indent=2)
        self.log(f"\n📄 Report saved to {output_path}")

def main():
    parser = argparse.ArgumentParser(description='Convert models to ONNX format')
    parser.add_argument('--model', type=str, default='resnet18',
                       help='PyTorch model name')
    parser.add_argument('--output', type=str, default='models/converted_model.onnx',
                       help='Output ONNX path')
    parser.add_argument('--no-validate', action='store_true',
                       help='Skip validation')
    parser.add_argument('--opset', type=int, default=14,
                       help='ONNX opset version')

    args = parser.parse_args()

    # Load PyTorch model
    print(f"Loading PyTorch model: {args.model}")
    model = torch.hub.load('pytorch/vision', args.model, pretrained=True)
    model.eval()

    # Create dummy input
    dummy_input = torch.randn(1, 3, 224, 224)

    # Create converter
    converter = ModelConverter(validate=not args.no_validate)

    # Convert model
    success = converter.convert_pytorch(
        model=model,
        dummy_input=dummy_input,
        output_path=args.output,
        opset_version=args.opset
    )

    # Save report
    if success:
        converter.save_report()

    return 0 if success else 1

if __name__ == "__main__":
    exit(main())
```

**Usage**:
```bash
# Convert ResNet18
python model_converter.py --model resnet18 --output models/resnet18.onnx

# Convert MobileNetV2 without validation
python model_converter.py --model mobilenet_v2 --output models/mobilenet.onnx --no-validate

# Convert with specific opset version
python model_converter.py --model efficientnet_b0 --opset 15
```

✅ **Checkpoint**: You have a production-ready conversion tool!

---

## Part 8: Real-World Application

### Step 8.1: Complete Inference Comparison Tool

```python
# inference_comparison_app.py
"""
Compare inference across PyTorch, TensorFlow, and ONNX
"""

import torch
import onnxruntime as ort
import numpy as np
from PIL import Image
import time
import argparse
from typing import Dict, List

class MultiFrameworkInference:
    """Run inference across multiple frameworks"""

    def __init__(self, image_path: str):
        self.image_path = image_path
        self.image = None
        self.labels = None
        self._load_labels()

    def _load_labels(self):
        """Load ImageNet labels"""
        import urllib.request
        url = "https://raw.githubusercontent.com/pytorch/hub/master/imagenet_classes.txt"
        urllib.request.urlretrieve(url, "imagenet_classes.txt")
        with open("imagenet_classes.txt") as f:
            self.labels = [line.strip() for line in f.readlines()]

    def preprocess_pytorch(self) -> torch.Tensor:
        """Preprocess for PyTorch"""
        from torchvision import transforms

        transform = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])

        image = Image.open(self.image_path).convert('RGB')
        return transform(image).unsqueeze(0)

    def preprocess_onnx(self) -> np.ndarray:
        """Preprocess for ONNX"""
        image = Image.open(self.image_path).convert('RGB')
        image = image.resize((256, 256))

        # Center crop
        left = (256 - 224) / 2
        top = (256 - 224) / 2
        image = image.crop((left, top, left + 224, top + 224))

        # Normalize
        img_array = np.array(image).astype(np.float32) / 255.0
        mean = np.array([0.485, 0.456, 0.406])
        std = np.array([0.229, 0.224, 0.225])
        img_array = (img_array - mean) / std

        # CHW format
        img_array = img_array.transpose(2, 0, 1)
        return np.expand_dims(img_array, axis=0)

    def run_pytorch(self, model_name: str = 'resnet18') -> Dict:
        """Run PyTorch inference"""
        print(f"\n{'='*50}")
        print(f"PyTorch Inference ({model_name})")
        print(f"{'='*50}")

        # Load model
        print("Loading model...")
        model = torch.hub.load('pytorch/vision', model_name, pretrained=True)
        model.eval()

        # Preprocess
        input_tensor = self.preprocess_pytorch()

        # Warmup
        with torch.no_grad():
            for _ in range(10):
                _ = model(input_tensor)

        # Measure inference
        start = time.perf_counter()
        with torch.no_grad():
            output = model(input_tensor)
        latency_ms = (time.perf_counter() - start) * 1000

        # Get predictions
        probabilities = torch.nn.functional.softmax(output[0], dim=0)
        top5_prob, top5_idx = torch.topk(probabilities, 5)

        results = {
            'framework': 'PyTorch',
            'model': model_name,
            'latency_ms': latency_ms,
            'predictions': [
                {
                    'class': self.labels[idx.item()],
                    'probability': prob.item()
                }
                for prob, idx in zip(top5_prob, top5_idx)
            ]
        }

        self._print_results(results)
        return results

    def run_onnx(self, onnx_path: str) -> Dict:
        """Run ONNX Runtime inference"""
        print(f"\n{'='*50}")
        print(f"ONNX Runtime Inference")
        print(f"{'='*50}")

        # Load model
        print(f"Loading model from {onnx_path}...")
        session = ort.InferenceSession(onnx_path)
        input_name = session.get_inputs()[0].name

        # Preprocess
        input_data = self.preprocess_onnx()

        # Warmup
        for _ in range(10):
            _ = session.run(None, {input_name: input_data})

        # Measure inference
        start = time.perf_counter()
        output = session.run(None, {input_name: input_data})[0]
        latency_ms = (time.perf_counter() - start) * 1000

        # Get predictions
        exp_output = np.exp(output[0] - np.max(output[0]))
        probabilities = exp_output / exp_output.sum()
        top5_idx = np.argsort(probabilities)[-5:][::-1]

        results = {
            'framework': 'ONNX Runtime',
            'model': os.path.basename(onnx_path),
            'latency_ms': latency_ms,
            'predictions': [
                {
                    'class': self.labels[idx],
                    'probability': float(probabilities[idx])
                }
                for idx in top5_idx
            ]
        }

        self._print_results(results)
        return results

    def _print_results(self, results: Dict):
        """Print inference results"""
        print(f"\n⏱️  Inference time: {results['latency_ms']:.2f} ms")
        print(f"\n🎯 Top 5 Predictions:")
        for i, pred in enumerate(results['predictions']):
            print(f"  {i+1}. {pred['class']:<30} {pred['probability']*100:>6.2f}%")

    def compare(self, results: List[Dict]):
        """Compare results across frameworks"""
        print(f"\n\n{'='*70}")
        print("COMPARISON SUMMARY")
        print(f"{'='*70}")

        print(f"\n{'Framework':<20} {'Model':<25} {'Latency (ms)':<15}")
        print("-" * 60)

        for result in results:
            print(f"{result['framework']:<20} {result['model']:<25} {result['latency_ms']:<15.2f}")

        # Find fastest
        fastest = min(results, key=lambda x: x['latency_ms'])
        print(f"\n🏆 Fastest: {fastest['framework']} ({fastest['latency_ms']:.2f} ms)")

        # Compare predictions
        print(f"\n🎯 Top Prediction Comparison:")
        for result in results:
            top_pred = result['predictions'][0]
            print(f"  {result['framework']:<20} {top_pred['class']:<30} {top_pred['probability']*100:>6.2f}%")

def main():
    parser = argparse.ArgumentParser(description='Compare inference across frameworks')
    parser.add_argument('image', type=str, help='Image path')
    parser.add_argument('--pytorch-model', type=str, default='resnet18',
                       help='PyTorch model name')
    parser.add_argument('--onnx-model', type=str, default='models/resnet18.onnx',
                       help='ONNX model path')

    args = parser.parse_args()

    # Create inference engine
    engine = MultiFrameworkInference(args.image)

    # Run inference on both frameworks
    results = []

    # PyTorch
    pytorch_result = engine.run_pytorch(args.pytorch_model)
    results.append(pytorch_result)

    # ONNX
    if os.path.exists(args.onnx_model):
        onnx_result = engine.run_onnx(args.onnx_model)
        results.append(onnx_result)
    else:
        print(f"\n⚠️  ONNX model not found: {args.onnx_model}")
        print("Convert PyTorch model first using model_converter.py")

    # Compare
    if len(results) > 1:
        engine.compare(results)

if __name__ == "__main__":
    main()
```

**Usage**:
```bash
# Compare PyTorch and ONNX inference
python inference_comparison_app.py test_images/dog.jpg \
    --pytorch-model resnet18 \
    --onnx-model models/resnet18.onnx
```

✅ **Final Checkpoint**: You have a complete multi-framework inference system!

---

## Stretch Goals (Optional Challenges)

### Challenge 1: Optimize ONNX Model

**Task**: Apply optimization techniques to reduce model size and improve speed.

```python
# Hint: Use onnxruntime.transformers.optimizer
from onnxruntime.transformers import optimizer

optimized_model = optimizer.optimize_model(
    "models/resnet50.onnx",
    model_type='bert',  # or appropriate type
    num_heads=0,
    hidden_size=0
)
```

### Challenge 2: Quantization

**Task**: Convert model to INT8 quantization for faster inference.

```python
# Hint: Use dynamic quantization
import onnxruntime as ort
from onnxruntime.quantization import quantize_dynamic, QuantType

quantize_dynamic(
    "models/resnet50.onnx",
    "models/resnet50_quant.onnx",
    weight_type=QuantType.QUInt8
)
```

### Challenge 3: Custom Operators

**Task**: Handle models with custom PyTorch operators in ONNX conversion.

Research:
- How to register custom ONNX operators
- Symbolic function definition
- Operator compatibility across versions

---

## Validation and Testing

### Test Your Knowledge

```python
# test_conversions.py
"""Test your conversion implementations"""

def test_conversion_validity():
    """Test that converted models are valid ONNX"""
    import onnx

    onnx_files = [
        "models/resnet50.onnx",
        "models/mobilenet_v2.onnx"
    ]

    for onnx_file in onnx_files:
        if os.path.exists(onnx_file):
            model = onnx.load(onnx_file)
            onnx.checker.check_model(model)
            print(f"✅ {onnx_file} is valid")
        else:
            print(f"⚠️  {onnx_file} not found")

def test_numerical_accuracy():
    """Test that ONNX outputs match PyTorch"""
    # Your implementation here
    pass

def test_performance_improvement():
    """Test that ONNX is faster than PyTorch"""
    # Your implementation here
    pass

if __name__ == "__main__":
    test_conversion_validity()
    test_numerical_accuracy()
    test_performance_improvement()
```

---

## Reflection Questions

Answer these questions to solidify your learning:

1. **What are the main benefits of using ONNX in production?**
   - Your answer:

2. **When would you NOT use ONNX (stick with native framework)?**
   - Your answer:

3. **Why is model validation important after conversion?**
   - Your answer:

4. **How does ONNX Runtime achieve better performance than native frameworks?**
   - Your answer:

5. **What are the trade-offs between different opset versions?**
   - Your answer:

6. **In what scenarios would you use dynamic_axes?**
   - Your answer:

7. **How would you debug a model that converts but gives wrong outputs?**
   - Your answer:

---

## Summary

**What You Accomplished**:
✅ Converted PyTorch models to ONNX format
✅ Converted TensorFlow models to ONNX format
✅ Ran inference with ONNX Runtime
✅ Validated converted models for accuracy
✅ Measured performance across frameworks
✅ Built production-ready conversion tools
✅ Understood ONNX's role in ML infrastructure

**Key Skills Gained**:
- Model format conversion (PyTorch → ONNX)
- Model format conversion (TensorFlow → ONNX)
- ONNX Runtime inference
- Numerical validation techniques
- Performance benchmarking
- Multi-framework deployment strategies

**Infrastructure Engineer Takeaways**:
- **Deployment Flexibility**: ONNX enables framework-agnostic deployment
- **Performance**: ONNX Runtime often outperforms native frameworks for inference
- **Optimization**: Standard format enables hardware-specific optimizations
- **Interoperability**: Train in one framework, deploy in another
- **Cost Savings**: Faster inference reduces cloud compute costs

---

## Next Steps

1. **Explore ONNX Runtime Optimizations**: Learn about graph optimizations, quantization, and pruning
2. **Try Different Models**: Convert various architectures (transformers, GANs, etc.)
3. **Production Deployment**: Use ONNX models in serving frameworks (TorchServe, TensorFlow Serving, Triton)
4. **Hardware Acceleration**: Experiment with TensorRT, OpenVINO, CoreML execution providers
5. **Complete Project 02**: Deploy ONNX model as a REST API

---

## Additional Resources

### Documentation
- [ONNX Official Documentation](https://onnx.ai/onnx/)
- [ONNX Runtime Documentation](https://onnxruntime.ai/)
- [PyTorch ONNX Export](https://pytorch.org/docs/stable/onnx.html)
- [TF2ONNX Documentation](https://github.com/onnx/tensorflow-onnx)

### Tutorials
- ONNX Runtime Performance Tuning Guide
- Model Optimization Best Practices
- Quantization and Pruning Techniques

### Tools
- Netron (visualize ONNX models)
- ONNX Optimizer
- ONNX Runtime Tools

---

**Exercise Version**: 1.0
**Last Updated**: October 2025
**Estimated Time**: 3-4 hours
**Difficulty**: Beginner-Intermediate
