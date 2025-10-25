# Lecture 03: TensorFlow Basics for Infrastructure Engineers

## Learning Objectives

By the end of this lecture, you will be able to:

- Understand TensorFlow/Keras architecture and ecosystem
- Work with TensorFlow model formats (SavedModel, H5, TFLite)
- Load pre-trained TensorFlow models from various sources
- Run inference with TensorFlow models in production
- Deploy models using TensorFlow Serving
- Compare TensorFlow and PyTorch from infrastructure perspective
- Troubleshoot common TensorFlow deployment issues

**Duration**: 8-10 hours
**Difficulty**: Beginner to Intermediate
**Prerequisites**: Module 001 (Python), Lecture 01 (ML Overview), Lecture 02 (PyTorch Basics)

---

## 1. Introduction to TensorFlow

### What is TensorFlow?

TensorFlow is an open-source machine learning framework developed by Google. It's one of the most mature and production-ready ML frameworks available.

**Industry Adoption**:
- Used by: Google, Airbnb, Uber, Twitter, Dropbox
- Powers: Google Search, Gmail, Google Photos, YouTube recommendations
- Strong in: Production deployments, mobile/edge ML, enterprise environments

**Infrastructure Perspective**:
- **Static computation graphs**: More optimization opportunities
- **TensorFlow Serving**: Battle-tested production serving
- **TensorFlow Lite**: Mobile and edge deployment
- **TensorFlow.js**: Browser-based ML
- **TPU support**: Google's custom ML accelerators
- **Enterprise features**: Better multi-language support (Python, C++, Java, Go)

### TensorFlow and Keras

**Keras** is the high-level API for TensorFlow (built-in since TF 2.0):
```python
# Old way (TensorFlow 1.x)
import tensorflow as tf
import keras

# Modern way (TensorFlow 2.x)
import tensorflow as tf
# Keras is built-in
from tensorflow import keras
```

**For Infrastructure**: Always use `tensorflow.keras`, not standalone Keras.

---

## 2. TensorFlow Installation and Environment

### Installation Options

```bash
# CPU-only version (lightweight)
pip install tensorflow

# GPU-enabled version (same package, detects GPU automatically)
pip install tensorflow[and-cuda]

# Or specific version
pip install tensorflow==2.14.0

# Verify installation
python -c "import tensorflow as tf; print(tf.__version__); print(tf.config.list_physical_devices('GPU'))"
```

### Verifying Installation

```python
import tensorflow as tf

# Check TensorFlow version
print(f"TensorFlow version: {tf.__version__}")

# Check GPU availability
gpus = tf.config.list_physical_devices('GPU')
print(f"GPUs available: {len(gpus)}")

if gpus:
    for gpu in gpus:
        print(f"  {gpu.name}: {gpu.device_type}")

    # Get GPU details
    gpu_details = tf.config.experimental.get_device_details(gpus[0])
    print(f"GPU compute capability: {gpu_details.get('compute_capability')}")

# Check CPU capabilities
print(f"Built with CUDA: {tf.test.is_built_with_cuda()}")
print(f"GPU support: {tf.test.is_gpu_available()}")
```

**Expected Output (with GPU)**:
```
TensorFlow version: 2.14.0
GPUs available: 1
  /physical_device:GPU:0: GPU
GPU compute capability: (8, 0)
Built with CUDA: True
GPU support: True
```

### Infrastructure Considerations

**Docker Images**:
```dockerfile
# Official TensorFlow images
FROM tensorflow/tensorflow:2.14.0-gpu

# Or CPU-only
FROM tensorflow/tensorflow:2.14.0

# Custom build
FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04
RUN pip install tensorflow==2.14.0
```

**Dependencies**:
- **tensorflow**: Core library (~500MB)
- **tensorboard**: Visualization tool (included)
- **tensorflow-datasets**: Common datasets (optional)
- **tensorflow-hub**: Pre-trained models (optional)

---

## 3. TensorFlow Model Formats

TensorFlow supports multiple model formats, each with different use cases:

### Format 1: SavedModel (Recommended for Production)

**What it is**: Complete TensorFlow program including weights and computation graph.

```python
import tensorflow as tf

# Create a simple model
model = tf.keras.Sequential([
    tf.keras.layers.Dense(128, activation='relu', input_shape=(784,)),
    tf.keras.layers.Dense(10, activation='softmax')
])

# Save as SavedModel (directory-based format)
model.save('my_model/')

# Directory structure:
# my_model/
#   ├── saved_model.pb          # The computation graph
#   ├── variables/
#   │   ├── variables.data-*    # Weight values
#   │   └── variables.index     # Weight index
#   └── assets/                 # Additional files (optional)

# Load SavedModel
loaded_model = tf.keras.models.load_model('my_model/')
```

**Characteristics**:
- ✅ **Production-ready**: Works with TensorFlow Serving
- ✅ **Language-independent**: Can load in C++, Java, Go
- ✅ **Complete**: Includes graph and weights
- ✅ **Versioned**: Supports model versioning
- ❌ **Larger size**: More files than H5

### Format 2: HDF5 (.h5 or .keras)

**What it is**: Single file containing architecture and weights.

```python
# Save as H5
model.save('my_model.h5')

# Or use .keras extension (recommended in TF 2.x)
model.save('my_model.keras')

# Load H5
loaded_model = tf.keras.models.load_model('my_model.h5')
```

**Characteristics**:
- ✅ **Single file**: Easy to manage
- ✅ **Compact**: Smaller than SavedModel
- ✅ **Keras-only**: Works only with Keras models
- ❌ **Not for TF Serving**: Cannot use with TensorFlow Serving
- ❌ **Python-only**: Harder to load in other languages

### Format 3: TensorFlow Lite (.tflite)

**What it is**: Optimized format for mobile and edge devices.

```python
# Convert to TFLite
converter = tf.lite.TFLiteConverter.from_keras_model(model)
tflite_model = converter.convert()

# Save
with open('model.tflite', 'wb') as f:
    f.write(tflite_model)

# Load and run inference
interpreter = tf.lite.Interpreter(model_path='model.tflite')
interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# Run inference
interpreter.set_tensor(input_details[0]['index'], input_data)
interpreter.invoke()
output = interpreter.get_tensor(output_details[0]['index'])
```

**Characteristics**:
- ✅ **Optimized**: Smaller size, faster inference
- ✅ **Mobile-ready**: Android, iOS support
- ✅ **Edge devices**: Raspberry Pi, microcontrollers
- ❌ **Limited ops**: Not all TensorFlow ops supported
- ❌ **Conversion needed**: Extra step in deployment

### Format Comparison

| Format | Size | Speed | TF Serving | Mobile | Use Case |
|--------|------|-------|------------|--------|----------|
| **SavedModel** | Large | Fast | ✅ Yes | ❌ No | Production servers |
| **H5/Keras** | Medium | Fast | ❌ No | ❌ No | Development, experiments |
| **TFLite** | Small | Very Fast | ❌ No | ✅ Yes | Mobile, edge devices |

**Infrastructure Decision Tree**:
```
Are you deploying to mobile/edge?
├─ Yes → Use TFLite
└─ No → Are you using TensorFlow Serving?
    ├─ Yes → Use SavedModel
    └─ No → Use SavedModel (future-proof) or H5 (convenience)
```

---

## 4. Loading Pre-trained Models

### From TensorFlow Hub

```python
import tensorflow as tf
import tensorflow_hub as hub

# Load a pre-trained model
model = tf.keras.Sequential([
    hub.KerasLayer("https://tfhub.dev/google/imagenet/mobilenet_v2_100_224/classification/5")
])

# Build model (initialize weights)
model.build([None, 224, 224, 3])

print(f"Model inputs: {model.inputs}")
print(f"Model outputs: {model.outputs}")
```

### From Keras Applications

```python
from tensorflow.keras.applications import ResNet50, VGG16, MobileNetV2

# Load pre-trained ResNet50
model = ResNet50(weights='imagenet')

print(f"Model name: {model.name}")
print(f"Number of layers: {len(model.layers)}")
print(f"Number of parameters: {model.count_params():,}")
```

**Output**:
```
Model name: resnet50
Number of layers: 175
Number of parameters: 25,636,712
```

### From HuggingFace (via transformers)

```python
from transformers import TFAutoModel, AutoTokenizer

# Load BERT model (TensorFlow version)
model_name = "bert-base-uncased"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = TFAutoModel.from_pretrained(model_name)

print(f"Model type: {type(model)}")
print(f"Model parameters: {model.num_parameters():,}")
```

### From Local Files

```python
import tensorflow as tf

# Load SavedModel
model = tf.keras.models.load_model('my_model/')

# Load H5
model = tf.keras.models.load_model('my_model.h5')

# Load weights only (requires model architecture)
model = ResNet50(weights=None)  # Architecture without weights
model.load_weights('resnet50_weights.h5')

print("Model loaded successfully!")
```

### Infrastructure Best Practices

```python
import os
import tensorflow as tf

# Set custom model cache directory
os.environ['TFHUB_CACHE_DIR'] = '/data/models/tfhub'

# Pre-download models during container build
model = tf.keras.applications.ResNet50(weights='imagenet')
model.save('/data/models/resnet50/')

# In production, load from local path
model = tf.keras.models.load_model('/data/models/resnet50/')
```

---

## 5. Running Inference with TensorFlow

### Image Classification Example

```python
import tensorflow as tf
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.resnet50 import preprocess_input, decode_predictions
import numpy as np
import urllib.request

# Load pre-trained model
model = ResNet50(weights='imagenet')

# Download and load image
url = "https://storage.googleapis.com/download.tensorflow.org/example_images/grace_hopper.jpg"
urllib.request.urlretrieve(url, "grace_hopper.jpg")
img = image.load_img("grace_hopper.jpg", target_size=(224, 224))

# Preprocess image
img_array = image.img_to_array(img)
img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension
img_array = preprocess_input(img_array)

print(f"Input shape: {img_array.shape}")  # (1, 224, 224, 3)

# Run inference
predictions = model.predict(img_array)

# Decode predictions
decoded = decode_predictions(predictions, top=5)[0]

print("\nTop 5 predictions:")
for i, (imagenet_id, label, score) in enumerate(decoded):
    print(f"{i+1}. {label}: {score:.4f}")
```

**Output**:
```
Input shape: (1, 224, 224, 3)

Top 5 predictions:
1. military_uniform: 0.8324
2. suit: 0.0514
3. mortarboard: 0.0349
4. Windsor_tie: 0.0142
5. bow_tie: 0.0123
```

### Batch Inference

```python
import tensorflow as tf
import numpy as np
import time

# Load model
model = tf.keras.applications.ResNet50(weights='imagenet')

# Benchmark different batch sizes
batch_sizes = [1, 8, 16, 32, 64]
input_shape = (224, 224, 3)

print(f"{'Batch Size':<12} {'Time (s)':<12} {'Throughput (samples/s)':<25} {'Latency/Sample (ms)':<20}")

for batch_size in batch_sizes:
    # Create dummy input
    dummy_input = np.random.rand(batch_size, *input_shape).astype(np.float32)

    # Warmup
    _ = model.predict(dummy_input, verbose=0)

    # Benchmark
    start = time.time()
    _ = model.predict(dummy_input, verbose=0)
    elapsed = time.time() - start

    throughput = batch_size / elapsed
    latency_per_sample = (elapsed / batch_size) * 1000

    print(f"{batch_size:<12} {elapsed:<12.4f} {throughput:<25.2f} {latency_per_sample:<20.2f}")
```

**Typical Output (GPU)**:
```
Batch Size   Time (s)     Throughput (samples/s)    Latency/Sample (ms)
1            0.0234       42.74                     23.40
8            0.0456       175.44                    5.70
16           0.0789       202.79                    4.93
32           0.1456       219.78                    4.55
64           0.2845       224.96                    4.45
```

### Production Inference Pattern

```python
import tensorflow as tf
import numpy as np

class ImageClassifier:
    def __init__(self, model_path: str):
        """Initialize classifier with model"""
        self.model = tf.keras.models.load_model(model_path)
        self.model.compile()  # Optimize for inference

    def preprocess(self, image_data: np.ndarray) -> np.ndarray:
        """Preprocess input image"""
        # Resize to model input size
        image_data = tf.image.resize(image_data, [224, 224])
        # Normalize
        image_data = tf.keras.applications.resnet50.preprocess_input(image_data)
        return image_data

    def predict(self, images: np.ndarray) -> np.ndarray:
        """Run inference on batch of images"""
        # Preprocess
        processed = self.preprocess(images)

        # Predict
        predictions = self.model.predict(processed, verbose=0)

        return predictions

    def predict_single(self, image: np.ndarray) -> np.ndarray:
        """Run inference on single image"""
        # Add batch dimension
        image_batch = np.expand_dims(image, axis=0)
        predictions = self.predict(image_batch)
        return predictions[0]

# Usage
classifier = ImageClassifier('resnet50_model/')
dummy_image = np.random.rand(224, 224, 3).astype(np.float32)
result = classifier.predict_single(dummy_image)
print(f"Prediction shape: {result.shape}")
```

---

## 6. TensorFlow Serving: Production Deployment

### What is TensorFlow Serving?

TensorFlow Serving is a flexible, high-performance serving system for machine learning models, designed for production environments.

**Features**:
- **REST and gRPC APIs**: Multiple protocol support
- **Model versioning**: Serve multiple versions simultaneously
- **Hot-swapping**: Update models without downtime
- **Batching**: Automatic request batching
- **Monitoring**: Built-in metrics
- **Multi-model serving**: Serve multiple models in one instance

### Installing TensorFlow Serving

```bash
# Option 1: Docker (recommended)
docker pull tensorflow/serving

# Option 2: APT (Ubuntu/Debian)
echo "deb [arch=amd64] http://storage.googleapis.com/tensorflow-serving-apt stable tensorflow-model-server tensorflow-model-server-universal" | sudo tee /etc/apt/sources.list.d/tensorflow-serving.list
curl https://storage.googleapis.com/tensorflow-serving-apt/tensorflow-serving.release.pub.gpg | sudo apt-key add -
sudo apt update && sudo apt install tensorflow-model-server
```

### Preparing Model for Serving

```python
import tensorflow as tf

# Load or create model
model = tf.keras.applications.MobileNetV2(weights='imagenet')

# Save in TensorFlow Serving format
model_version = 1
export_path = f'./serving_models/mobilenet/{model_version}'
model.save(export_path)

print(f"Model saved to {export_path}")

# Directory structure:
# serving_models/
#   └── mobilenet/
#       └── 1/              # Version number
#           ├── saved_model.pb
#           └── variables/
```

### Running TensorFlow Serving

```bash
# Using Docker
docker run -p 8501:8501 \
  --mount type=bind,source=$(pwd)/serving_models/mobilenet,target=/models/mobilenet \
  -e MODEL_NAME=mobilenet \
  tensorflow/serving

# Server will start and expose:
# - REST API on port 8501
# - gRPC API on port 8500 (default)
```

### Making Inference Requests

**REST API**:
```python
import requests
import json
import numpy as np

# Prepare input data
data = np.random.rand(1, 224, 224, 3).tolist()

# Create request payload
payload = {
    "instances": data
}

# Send request
url = "http://localhost:8501/v1/models/mobilenet:predict"
response = requests.post(url, json=payload)

# Parse response
predictions = response.json()["predictions"]
print(f"Predictions shape: {np.array(predictions).shape}")
```

**gRPC API** (faster):
```python
import grpc
import numpy as np
from tensorflow_serving.apis import predict_pb2
from tensorflow_serving.apis import prediction_service_pb2_grpc
import tensorflow as tf

# Create gRPC channel
channel = grpc.insecure_channel('localhost:8500')
stub = prediction_service_pb2_grpc.PredictionServiceStub(channel)

# Prepare request
request = predict_pb2.PredictRequest()
request.model_spec.name = 'mobilenet'
request.model_spec.signature_name = 'serving_default'

# Add input data
input_data = np.random.rand(1, 224, 224, 3).astype(np.float32)
request.inputs['input_1'].CopyFrom(
    tf.make_tensor_proto(input_data, shape=input_data.shape)
)

# Get response
result = stub.Predict(request, 10.0)  # 10 second timeout
print(f"Result: {result}")
```

### TensorFlow Serving Configuration

```bash
# Model config file (models.config)
cat > models.config <<EOF
model_config_list {
  config {
    name: 'mobilenet'
    base_path: '/models/mobilenet'
    model_platform: 'tensorflow'
    model_version_policy {
      specific {
        versions: 1
        versions: 2
      }
    }
  }
  config {
    name: 'resnet'
    base_path: '/models/resnet'
    model_platform: 'tensorflow'
  }
}
EOF

# Run with config
docker run -p 8501:8501 \
  --mount type=bind,source=$(pwd)/serving_models,target=/models \
  --mount type=bind,source=$(pwd)/models.config,target=/config/models.config \
  tensorflow/serving \
  --model_config_file=/config/models.config
```

### Production Docker Setup

```dockerfile
# Dockerfile for TensorFlow Serving with custom models
FROM tensorflow/serving:latest

# Copy models
COPY serving_models/ /models/

# Copy config
COPY models.config /config/models.config

# Expose ports
EXPOSE 8500 8501

# Set environment variables
ENV MODEL_NAME=mobilenet

# Start TensorFlow Serving
CMD ["tensorflow_model_server", \
     "--model_config_file=/config/models.config", \
     "--rest_api_port=8501", \
     "--allow_version_labels_for_unavailable_models=true"]
```

---

## 7. TensorFlow vs PyTorch Comparison

### From Infrastructure Perspective

| Aspect | TensorFlow | PyTorch |
|--------|------------|---------|
| **Production Serving** | TensorFlow Serving (mature) | TorchServe (newer) |
| **Model Format** | SavedModel (directory) | State Dict / Full Model (file) |
| **Mobile Deployment** | TFLite (very mature) | PyTorch Mobile (growing) |
| **Multi-language** | C++, Java, Go, JavaScript | Primarily Python, C++ |
| **Cloud Integration** | Strong (Google Cloud) | Growing |
| **Enterprise Adoption** | Higher (older, more stable) | Growing rapidly |
| **Debugging** | Harder (static graphs) | Easier (dynamic graphs) |
| **Learning Curve** | Steeper | Gentler |
| **Community** | Large, enterprise-focused | Large, research-focused |

### Code Comparison

**PyTorch**:
```python
import torch

# Load model
model = torch.hub.load('pytorch/vision', 'resnet50', pretrained=True)
model.eval()

# Inference
with torch.no_grad():
    output = model(input_tensor)
```

**TensorFlow**:
```python
import tensorflow as tf

# Load model
model = tf.keras.applications.ResNet50(weights='imagenet')

# Inference (no special context needed)
output = model.predict(input_array)
```

### When to Choose Which?

**Choose TensorFlow if**:
- ✅ Need mature production serving (TensorFlow Serving)
- ✅ Deploying to mobile/edge devices extensively
- ✅ Enterprise environment with multi-language requirements
- ✅ Using Google Cloud Platform heavily
- ✅ Need battle-tested production tools

**Choose PyTorch if**:
- ✅ Research-oriented organization
- ✅ Need easier debugging during development
- ✅ Team prefers Pythonic, intuitive APIs
- ✅ Deploying primarily to servers (not mobile)
- ✅ Using HuggingFace ecosystem heavily

**Use Both**:
- Convert models to ONNX for framework-independent deployment
- Use whichever framework the data science team prefers
- Build infrastructure that supports both

---

## 8. Common Issues and Troubleshooting

### Issue 1: GPU Not Detected

**Problem**: TensorFlow not using GPU despite having one.

**Diagnostics**:
```python
import tensorflow as tf

# Check GPU
print(tf.config.list_physical_devices('GPU'))

# Enable logging
tf.debugging.set_log_device_placement(True)

# Test GPU computation
with tf.device('/GPU:0'):
    a = tf.constant([[1.0, 2.0], [3.0, 4.0]])
    b = tf.constant([[5.0, 6.0], [7.0, 8.0]])
    c = tf.matmul(a, b)
    print(c)
```

**Solutions**:
```bash
# 1. Check CUDA installation
nvidia-smi

# 2. Reinstall TensorFlow with GPU support
pip uninstall tensorflow
pip install tensorflow[and-cuda]

# 3. Check CUDA and cuDNN versions match TensorFlow requirements
# TensorFlow 2.14 requires CUDA 11.8 and cuDNN 8.7
```

### Issue 2: Model Loading Errors

**Error**:
```
ValueError: Unable to load model. Unable to restore object of class _tf_keras_metric
```

**Solution**:
```python
# Use custom_objects when loading
import tensorflow as tf

# Define custom objects if needed
custom_objects = {'CustomMetric': CustomMetric}

# Load with custom objects
model = tf.keras.models.load_model('model.h5', custom_objects=custom_objects)

# Or use compile=False to skip metric loading
model = tf.keras.models.load_model('model.h5', compile=False)
```

### Issue 3: Input Shape Mismatch

**Error**:
```
ValueError: Input 0 of layer "resnet50" is incompatible with the layer: expected shape=(None, 224, 224, 3), found shape=(None, 3, 224, 224)
```

**Problem**: TensorFlow uses channels-last (NHWC), PyTorch uses channels-first (NCHW).

**Solution**:
```python
import numpy as np

# PyTorch format: [N, C, H, W]
pytorch_format = np.random.rand(1, 3, 224, 224)

# Convert to TensorFlow format: [N, H, W, C]
tensorflow_format = np.transpose(pytorch_format, (0, 2, 3, 1))

print(f"PyTorch shape: {pytorch_format.shape}")      # (1, 3, 224, 224)
print(f"TensorFlow shape: {tensorflow_format.shape}") # (1, 224, 224, 3)

# Use TensorFlow format
output = model.predict(tensorflow_format)
```

### Issue 4: Out of Memory

**Error**:
```
ResourceExhaustedError: OOM when allocating tensor
```

**Solutions**:
```python
import tensorflow as tf

# 1. Enable memory growth (don't allocate all GPU memory at once)
gpus = tf.config.list_physical_devices('GPU')
if gpus:
    for gpu in gpus:
        tf.config.experimental.set_memory_growth(gpu, True)

# 2. Set memory limit
if gpus:
    tf.config.set_logical_device_configuration(
        gpus[0],
        [tf.config.LogicalDeviceConfiguration(memory_limit=4096)]  # 4GB
    )

# 3. Reduce batch size
batch_size = 8  # Instead of 32

# 4. Use mixed precision
tf.keras.mixed_precision.set_global_policy('mixed_float16')
```

### Issue 5: TensorFlow Serving Connection Issues

**Error**:
```
requests.exceptions.ConnectionError: HTTPConnectionPool
```

**Diagnostics**:
```bash
# Check if TensorFlow Serving is running
curl http://localhost:8501/v1/models/mobilenet

# Should return model metadata
```

**Solutions**:
```python
import requests
import time

def wait_for_server(url, timeout=60):
    """Wait for TensorFlow Serving to be ready"""
    start = time.time()
    while time.time() - start < timeout:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                print("Server is ready!")
                return True
        except requests.exceptions.ConnectionError:
            time.sleep(1)
    return False

# Wait for server
server_url = "http://localhost:8501/v1/models/mobilenet"
if wait_for_server(server_url):
    # Make inference request
    pass
```

---

## 9. Performance Optimization

### Mixed Precision Training and Inference

```python
import tensorflow as tf

# Enable mixed precision
policy = tf.keras.mixed_precision.Policy('mixed_float16')
tf.keras.mixed_precision.set_global_policy(policy)

# Load model
model = tf.keras.applications.ResNet50(weights='imagenet')

# Model will automatically use float16 for computations
# and float32 for numerical stability where needed

print(f"Compute dtype: {policy.compute_dtype}")  # float16
print(f"Variable dtype: {policy.variable_dtype}")  # float32
```

**Benefits**:
- ~2x faster inference on modern GPUs
- ~50% less memory usage
- Minimal accuracy loss

### TensorFlow Lite Conversion with Optimization

```python
import tensorflow as tf

# Load model
model = tf.keras.applications.MobileNetV2(weights='imagenet')

# Create converter
converter = tf.lite.TFLiteConverter.from_keras_model(model)

# Enable optimizations
converter.optimizations = [tf.lite.Optimize.DEFAULT]

# Optional: Quantize to int8 for even smaller models
def representative_dataset():
    for _ in range(100):
        data = np.random.rand(1, 224, 224, 3).astype(np.float32)
        yield [data]

converter.representative_dataset = representative_dataset
converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]
converter.inference_input_type = tf.uint8
converter.inference_output_type = tf.uint8

# Convert
tflite_model = converter.convert()

# Save
with open('mobilenet_quantized.tflite', 'wb') as f:
    f.write(tflite_model)

print(f"Original model size: {model.count_params() * 4 / 1024 / 1024:.2f} MB")
print(f"TFLite model size: {len(tflite_model) / 1024 / 1024:.2f} MB")
```

### Model Compilation for XLA

```python
import tensorflow as tf

# Load model
model = tf.keras.applications.ResNet50(weights='imagenet')

# Compile with XLA
model.compile(
    optimizer='adam',
    loss='categorical_crossentropy',
    jit_compile=True  # Enable XLA compilation
)

# Inference will be faster after initial compilation
```

---

## 10. Resource Estimation

### Model Size Calculation

```python
import tensorflow as tf

def get_model_size(model):
    """Calculate model size in MB"""
    total_params = model.count_params()
    # Assuming float32 (4 bytes per parameter)
    size_mb = (total_params * 4) / (1024 ** 2)
    return size_mb

model = tf.keras.applications.ResNet50(weights='imagenet')
print(f"Model size: {get_model_size(model):.2f} MB")
print(f"Total parameters: {model.count_params():,}")
```

### Memory Requirements

```python
import tensorflow as tf
import numpy as np

def estimate_memory(model, batch_size, input_shape):
    """Estimate memory requirements for inference"""
    # Model size
    model_size = get_model_size(model)

    # Input size
    input_size = np.prod(input_shape) * batch_size * 4 / (1024 ** 2)  # MB

    # Rough estimate: 2-3x model size for activations
    activation_size = model_size * 2.5

    total_mb = model_size + input_size + activation_size
    return {
        'model_mb': model_size,
        'input_mb': input_size,
        'activation_mb': activation_size,
        'total_mb': total_mb,
        'recommended_gpu_gb': total_mb / 1024 * 1.5  # 50% buffer
    }

model = tf.keras.applications.ResNet50(weights='imagenet')
memory = estimate_memory(model, batch_size=32, input_shape=(224, 224, 3))

print("Memory Estimates:")
for key, value in memory.items():
    print(f"  {key}: {value:.2f}")
```

---

## Key Takeaways

### For Infrastructure Engineers

1. **SavedModel is production format**: Use for TensorFlow Serving deployments
2. **TensorFlow Serving is mature**: Battle-tested for production
3. **Channels-last format**: TensorFlow uses [N, H, W, C], not [N, C, H, W]
4. **Multiple model formats**: Choose based on deployment target
5. **Mixed precision is powerful**: Easy 2x speedup with minimal changes
6. **Memory growth is important**: Enable to avoid OOM errors
7. **REST API is convenient**: gRPC is faster for high-throughput
8. **Model versioning built-in**: TF Serving supports A/B testing naturally

### Production Checklist

Before deploying TensorFlow models:

- [ ] Model saved in appropriate format (SavedModel for servers)
- [ ] Model tested with expected input shapes
- [ ] TensorFlow Serving configuration tested
- [ ] Model versioning strategy defined
- [ ] Memory requirements estimated
- [ ] GPU memory growth enabled (if applicable)
- [ ] Health check endpoint implemented
- [ ] Monitoring and logging configured
- [ ] Input preprocessing validated
- [ ] Output postprocessing validated

---

## Quick Reference

### Essential Commands

```python
# Installation check
import tensorflow as tf
print(tf.__version__)
print(tf.config.list_physical_devices('GPU'))

# Load model
model = tf.keras.models.load_model('model/')
model = tf.keras.applications.ResNet50(weights='imagenet')

# Inference
predictions = model.predict(input_array)

# Enable GPU memory growth
gpus = tf.config.list_physical_devices('GPU')
for gpu in gpus:
    tf.config.experimental.set_memory_growth(gpu, True)
```

### TensorFlow Serving

```bash
# Run TensorFlow Serving
docker run -p 8501:8501 \
  --mount type=bind,source=/path/to/model,target=/models/mymodel \
  -e MODEL_NAME=mymodel \
  tensorflow/serving

# Test REST API
curl -X POST http://localhost:8501/v1/models/mymodel:predict \
  -d '{"instances": [[1.0, 2.0, 3.0]]}'
```

---

## What's Next?

In the next lecture, we'll cover:
- **ONNX format**: Framework-independent deployment
- **Model conversion**: PyTorch ↔ TensorFlow ↔ ONNX
- **Optimization techniques**: Quantization, pruning, distillation

Continue to `lecture-notes/04-model-formats.md`

---

**Lecture Version**: 1.0
**Last Updated**: October 2025
**Estimated Completion Time**: 8-10 hours
**Difficulty**: Beginner to Intermediate
