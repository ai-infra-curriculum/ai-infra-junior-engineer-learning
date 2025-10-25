# Exercise 02: TensorFlow Model Inference

## Exercise Overview

**Objective**: Load pre-trained TensorFlow/Keras models, run inference on images, measure performance, and explore TensorFlow Serving basics.

**Difficulty**: Beginner
**Estimated Time**: 2-3 hours
**Prerequisites**: Lecture 03 (TensorFlow Basics)

**What You'll Learn**:
- Loading pre-trained models from keras.applications
- Preprocessing images for TensorFlow models
- Running inference with TensorFlow/Keras APIs
- Measuring inference latency and throughput
- Introduction to TensorFlow Serving
- SavedModel format and model export

---

## Learning Objectives

By the end of this exercise, you will be able to:

✅ Load pre-trained Keras models from keras.applications
✅ Preprocess images using TensorFlow preprocessing functions
✅ Run inference using both Keras and TensorFlow APIs
✅ Measure and optimize TensorFlow inference performance
✅ Export models in SavedModel format
✅ Understand TensorFlow Serving fundamentals
✅ Compare TensorFlow and PyTorch inference patterns

---

## Part 1: Environment Setup

### Step 1.1: Install Dependencies

```bash
# Create virtual environment
python -m venv tensorflow_inference_env
source tensorflow_inference_env/bin/activate  # On Windows: tensorflow_inference_env\Scripts\activate

# Install TensorFlow and dependencies
pip install tensorflow pillow requests numpy matplotlib
```

**Note**: TensorFlow 2.x includes Keras by default, so no separate Keras installation is needed.

### Step 1.2: Verify Installation

```python
# verify_installation.py
import tensorflow as tf
import numpy as np

print(f"TensorFlow version: {tf.__version__}")
print(f"Keras version: {tf.keras.__version__}")
print(f"Numpy version: {np.__version__}")

# Check for GPU
gpus = tf.config.list_physical_devices('GPU')
if gpus:
    print(f"GPU available: {len(gpus)} device(s)")
    for gpu in gpus:
        print(f"  - {gpu.name}")
else:
    print("Running on CPU")

# Check GPU memory configuration
if gpus:
    try:
        # Prevent TensorFlow from allocating all GPU memory
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
        print("GPU memory growth enabled")
    except RuntimeError as e:
        print(f"Memory growth setting error: {e}")
```

**Expected Output**:
```
TensorFlow version: 2.15.0
Keras version: 2.15.0
Numpy version: 1.24.3
GPU available: 1 device(s)
  - /physical_device:GPU:0
GPU memory growth enabled
```

### Step 1.3: Download Test Images

```python
# download_images.py
import urllib.request
import os

# Create images directory
os.makedirs("test_images", exist_ok=True)

# Download sample images
images = {
    "elephant.jpg": "https://upload.wikimedia.org/wikipedia/commons/3/37/African_Bush_Elephant.jpg",
    "tiger.jpg": "https://upload.wikimedia.org/wikipedia/commons/5/56/Tiger.50.jpg",
    "airplane.jpg": "https://upload.wikimedia.org/wikipedia/commons/2/2d/Boeing_777-31H_Air_China_B-2086.jpg"
}

for filename, url in images.items():
    filepath = os.path.join("test_images", filename)
    print(f"Downloading {filename}...")
    try:
        urllib.request.urlretrieve(url, filepath)
        print(f"  ✓ Saved to {filepath}")
    except Exception as e:
        print(f"  ✗ Error: {e}")

print("\nAll images downloaded!")
print(f"Images location: {os.path.abspath('test_images')}")
```

✅ **Checkpoint**: You should have TensorFlow environment set up and 3 test images downloaded.

---

## Part 2: Loading Pre-trained Models

### Step 2.1: Load MobileNetV2 from keras.applications

```python
# load_model.py
import tensorflow as tf
from tensorflow import keras

# Load pre-trained MobileNetV2
print("Loading MobileNetV2...")
model = keras.applications.MobileNetV2(
    weights='imagenet',  # Use pre-trained ImageNet weights
    include_top=True,    # Include classification head
    input_shape=(224, 224, 3)
)

print(f"Model loaded: {model.name}")
print(f"Input shape: {model.input_shape}")
print(f"Output shape: {model.output_shape}")

# Count parameters
trainable_params = sum([tf.size(w).numpy() for w in model.trainable_weights])
total_params = sum([tf.size(w).numpy() for w in model.weights])

print(f"Trainable parameters: {trainable_params:,}")
print(f"Total parameters: {total_params:,}")
```

**Expected Output**:
```
Downloading data from https://storage.googleapis.com/tensorflow/keras-applications/mobilenet_v2/mobilenet_v2_weights_tf_dim_ordering_tf_kernels_1.0_224.h5
14536120/14536120 [==============================] - 2s 0us/step
Model loaded: mobilenetv2_1.00_224
Input shape: (None, 224, 224, 3)
Output shape: (None, 1000)
Trainable parameters: 3,538,984
Total parameters: 3,538,984
```

### Step 2.2: Understanding Model Architecture

**Task**: Examine the model structure to understand its layers.

```python
# examine_model.py
import tensorflow as tf
from tensorflow import keras

model = keras.applications.MobileNetV2(weights='imagenet')

# Print model summary
print("Model Architecture Summary:")
model.summary()

print("\n" + "="*60)

# Count layers by type
layer_counts = {}
for layer in model.layers:
    layer_type = layer.__class__.__name__
    layer_counts[layer_type] = layer_counts.get(layer_type, 0) + 1

print("\nLayer Counts:")
for layer_type, count in sorted(layer_counts.items()):
    print(f"  {layer_type}: {count}")

# Model input/output information
print("\nModel Expectations:")
print(f"  Input shape: {model.input_shape}")
print(f"  Input dtype: {model.input.dtype}")
print(f"  Output shape: {model.output_shape}")
print(f"  Output classes: 1000 (ImageNet)")
print(f"  Expected input range: [0, 255] or [0, 1] depending on preprocessing")

# Get first and last few layers
print("\nFirst 5 layers:")
for i, layer in enumerate(model.layers[:5]):
    print(f"  {i+1}. {layer.name} ({layer.__class__.__name__})")

print("\nLast 5 layers:")
for i, layer in enumerate(model.layers[-5:]):
    print(f"  {len(model.layers)-5+i+1}. {layer.name} ({layer.__class__.__name__})")
```

**Questions to Answer** (write your answers):
1. How many total layers does MobileNetV2 have?
2. What is the expected input shape?
3. What types of layers are used in MobileNetV2?
4. How does this compare to ResNet50 in PyTorch?

✅ **Checkpoint**: Model loaded successfully and you understand its architecture.

---

## Part 3: Image Preprocessing

### Step 3.1: Implement Preprocessing Pipeline

```python
# preprocess.py
import tensorflow as tf
from tensorflow import keras
import numpy as np
from PIL import Image

def load_and_preprocess_image(image_path, target_size=(224, 224)):
    """
    Load and preprocess an image for MobileNetV2.

    Args:
        image_path: Path to image file
        target_size: Target image size (height, width)

    Returns:
        preprocessed_image: Preprocessed image tensor ready for model
    """
    # Method 1: Using keras.preprocessing (simpler)
    print(f"Loading image: {image_path}")

    # Load image
    img = keras.preprocessing.image.load_img(
        image_path,
        target_size=target_size
    )
    print(f"Original image size: {img.size}")

    # Convert to array
    img_array = keras.preprocessing.image.img_to_array(img)
    print(f"Image array shape: {img_array.shape}")
    print(f"Array dtype: {img_array.dtype}")
    print(f"Value range: [{img_array.min():.1f}, {img_array.max():.1f}]")

    # Add batch dimension: (224, 224, 3) -> (1, 224, 224, 3)
    img_batch = np.expand_dims(img_array, axis=0)
    print(f"Batch shape: {img_batch.shape}")

    # Apply model-specific preprocessing
    preprocessed = keras.applications.mobilenet_v2.preprocess_input(img_batch)
    print(f"After preprocessing range: [{preprocessed.min():.3f}, {preprocessed.max():.3f}]")

    return preprocessed

# Test preprocessing
preprocessed_image = load_and_preprocess_image("test_images/elephant.jpg")
```

**Expected Output**:
```
Loading image: test_images/elephant.jpg
Original image size: (224, 224)
Image array shape: (224, 224, 3)
Array dtype: float32
Value range: [0.0, 255.0]
Batch shape: (1, 224, 224, 3)
After preprocessing range: [-1.000, 1.000]
```

### Step 3.2: Alternative Preprocessing with TensorFlow APIs

```python
# preprocess_tf.py
import tensorflow as tf

def preprocess_with_tf(image_path, target_size=(224, 224)):
    """
    Preprocess image using pure TensorFlow APIs (more flexible).

    This approach is more suitable for production pipelines
    and TensorFlow Serving.
    """
    # Read image file
    image_raw = tf.io.read_file(image_path)

    # Decode image (automatically detects format)
    image = tf.image.decode_image(image_raw, channels=3)

    # Ensure shape is set (needed for some operations)
    image.set_shape([None, None, 3])

    print(f"Original shape: {image.shape}")
    print(f"Original dtype: {image.dtype}")

    # Resize image
    image = tf.image.resize(image, target_size)
    print(f"Resized shape: {image.shape}")

    # Convert to float32 if needed
    image = tf.cast(image, tf.float32)

    # Add batch dimension
    image = tf.expand_dims(image, 0)
    print(f"Batch shape: {image.shape}")

    # MobileNetV2 preprocessing: scale to [-1, 1]
    image = tf.keras.applications.mobilenet_v2.preprocess_input(image)
    print(f"Preprocessed range: [{tf.reduce_min(image):.3f}, {tf.reduce_max(image):.3f}]")

    return image

# Test TensorFlow preprocessing
tf_preprocessed = preprocess_with_tf("test_images/elephant.jpg")
```

### Step 3.3: Understand Preprocessing Differences

**Task**: Answer these questions about TensorFlow preprocessing:

1. **What does `preprocess_input` do for MobileNetV2?**
   - Hint: It scales pixel values from [0, 255] to [-1, 1]

2. **Why does TensorFlow use channels-last format (H, W, C)?**
   - Hint: Compare with PyTorch's channels-first (C, H, W)

3. **When would you use pure TensorFlow APIs vs Keras utilities?**
   - Hint: Consider deployment scenarios like TensorFlow Serving

✅ **Checkpoint**: You can preprocess images using multiple methods.

---

## Part 4: Running Inference

### Step 4.1: Basic Inference with Keras

```python
# inference.py
import tensorflow as tf
from tensorflow import keras
import numpy as np

# Load model
print("Loading model...")
model = keras.applications.MobileNetV2(weights='imagenet')

# Load and preprocess image
image_path = "test_images/elephant.jpg"
img = keras.preprocessing.image.load_img(image_path, target_size=(224, 224))
img_array = keras.preprocessing.image.img_to_array(img)
img_batch = np.expand_dims(img_array, axis=0)
preprocessed = keras.applications.mobilenet_v2.preprocess_input(img_batch)

print(f"Input shape: {preprocessed.shape}")
print(f"Input dtype: {preprocessed.dtype}")

# Run inference (Keras API - high level)
print("\nRunning inference...")
predictions = model.predict(preprocessed, verbose=0)

print(f"Output shape: {predictions.shape}")
print(f"Output dtype: {predictions.dtype}")
print(f"Output sample (first 5 values): {predictions[0, :5]}")
print(f"Predictions sum to: {predictions.sum():.6f}")  # Should be ~1 after softmax
```

**Expected Output**:
```
Loading model...
Input shape: (1, 224, 224, 3)
Input dtype: float32

Running inference...
Output shape: (1, 1000)
Output dtype: float32
Output sample (first 5 values): [1.234e-05 3.456e-06 2.345e-04 1.123e-05 4.567e-07]
Predictions sum to: 1.000000
```

### Step 4.2: Get Top Predictions with Labels

```python
# get_predictions.py
import tensorflow as tf
from tensorflow import keras
import numpy as np
import json
import urllib.request

# Download ImageNet class labels
print("Downloading ImageNet labels...")
labels_url = "https://storage.googleapis.com/download.tensorflow.org/data/imagenet_class_index.json"
urllib.request.urlretrieve(labels_url, "imagenet_class_index.json")

# Load labels
with open("imagenet_class_index.json") as f:
    class_idx = json.load(f)
    # Convert to list of class names
    labels = [class_idx[str(i)][1] for i in range(len(class_idx))]

print(f"Loaded {len(labels)} class labels")

# Load model
model = keras.applications.MobileNetV2(weights='imagenet')

# Load and preprocess image
image_path = "test_images/elephant.jpg"
img = keras.preprocessing.image.load_img(image_path, target_size=(224, 224))
img_array = keras.preprocessing.image.img_to_array(img)
img_batch = np.expand_dims(img_array, axis=0)
preprocessed = keras.applications.mobilenet_v2.preprocess_input(img_batch)

# Run inference
predictions = model.predict(preprocessed, verbose=0)

# Decode predictions (TensorFlow/Keras provides a helper for this)
decoded_predictions = keras.applications.mobilenet_v2.decode_predictions(
    predictions,
    top=5
)

# Display results
print(f"\nClassifying: {image_path}")
print("Top 5 Predictions:")
for i, (imagenet_id, class_name, probability) in enumerate(decoded_predictions[0]):
    print(f"  {i+1}. {class_name:<30} {probability*100:>6.2f}% (ID: {imagenet_id})")
```

**Expected Output**:
```
Downloading ImageNet labels...
Loaded 1000 class labels

Classifying: test_images/elephant.jpg
Top 5 Predictions:
  1. African_elephant            92.45% (ID: n02504458)
  2. tusker                      6.32% (ID: n02504013)
  3. Indian_elephant             1.12% (ID: n02504013)
  4. triceratops                 0.08% (ID: n01704323)
  5. ram                         0.02% (ID: n02412080)
```

### Step 4.3: Inference with TensorFlow's Functional API

```python
# inference_functional.py
import tensorflow as tf
from tensorflow import keras
import numpy as np

# Load model
model = keras.applications.MobileNetV2(weights='imagenet')

# Create a preprocessing + inference function
@tf.function  # This decorator compiles the function to a graph for better performance
def predict_image(image_path):
    """
    Complete preprocessing + inference pipeline using tf.function.
    This is closer to how TensorFlow Serving works.
    """
    # Read and preprocess
    image_raw = tf.io.read_file(image_path)
    image = tf.image.decode_image(image_raw, channels=3)
    image.set_shape([None, None, 3])
    image = tf.image.resize(image, [224, 224])
    image = tf.cast(image, tf.float32)
    image = tf.expand_dims(image, 0)
    image = keras.applications.mobilenet_v2.preprocess_input(image)

    # Run inference
    predictions = model(image, training=False)

    return predictions

# Test the function
print("Running tf.function inference...")
predictions = predict_image("test_images/elephant.jpg")
print(f"Predictions shape: {predictions.shape}")
print(f"Top prediction probability: {tf.reduce_max(predictions).numpy():.4f}")

# Get top 5 classes
top5_idx = tf.argsort(predictions[0], direction='DESCENDING')[:5]
top5_probs = tf.gather(predictions[0], top5_idx)

print("\nTop 5 class indices and probabilities:")
for idx, prob in zip(top5_idx.numpy(), top5_probs.numpy()):
    print(f"  Class {idx}: {prob:.4f}")
```

**Why use `@tf.function`?**
- Compiles Python code to TensorFlow graph
- Much faster for repeated calls
- Essential for production deployments
- Similar to TorchScript in PyTorch

✅ **Checkpoint**: You can run inference using multiple TensorFlow APIs!

---

## Part 5: Performance Measurement

### Step 5.1: Measure Inference Latency

```python
# measure_latency.py
import tensorflow as tf
from tensorflow import keras
import numpy as np
import time

# Load model
print("Loading model...")
model = keras.applications.MobileNetV2(weights='imagenet')

# Prepare test input
dummy_input = np.random.rand(1, 224, 224, 3).astype(np.float32)
dummy_input = keras.applications.mobilenet_v2.preprocess_input(dummy_input)

# Warmup (first few runs are slower due to TensorFlow graph compilation)
print("Warming up (this takes a moment)...")
for _ in range(20):
    _ = model.predict(dummy_input, verbose=0)

print("Warmup complete!")

# Measure latency
print("\nMeasuring inference latency...")
iterations = 100

start = time.time()
for _ in range(iterations):
    _ = model.predict(dummy_input, verbose=0)
elapsed = time.time() - start

avg_latency_ms = (elapsed / iterations) * 1000
throughput = iterations / elapsed

print(f"Average latency: {avg_latency_ms:.2f} ms")
print(f"Throughput: {throughput:.2f} images/second")
```

### Step 5.2: Optimized Inference with tf.function

```python
# measure_latency_optimized.py
import tensorflow as tf
from tensorflow import keras
import numpy as np
import time

# Load model
model = keras.applications.MobileNetV2(weights='imagenet')

# Create optimized inference function
@tf.function
def predict_optimized(inputs):
    return model(inputs, training=False)

# Prepare test input
dummy_input = tf.random.normal([1, 224, 224, 3])
dummy_input = keras.applications.mobilenet_v2.preprocess_input(dummy_input)

# Warmup
print("Warming up with @tf.function...")
for _ in range(20):
    _ = predict_optimized(dummy_input)

# Measure latency
iterations = 100
start = time.time()
for _ in range(iterations):
    _ = predict_optimized(dummy_input)
elapsed = time.time() - start

avg_latency_ms = (elapsed / iterations) * 1000
throughput = iterations / elapsed

print(f"Optimized average latency: {avg_latency_ms:.2f} ms")
print(f"Optimized throughput: {throughput:.2f} images/second")
print("\nNote: @tf.function should be significantly faster!")
```

### Step 5.3: Batch Inference Performance

```python
# batch_inference.py
import tensorflow as tf
from tensorflow import keras
import numpy as np
import time

# Load model
model = keras.applications.MobileNetV2(weights='imagenet')

# Create optimized inference function
@tf.function
def predict_batch(inputs):
    return model(inputs, training=False)

# Test different batch sizes
batch_sizes = [1, 4, 8, 16, 32]
print(f"{'Batch Size':<12} {'Latency/Batch (ms)':<20} {'Latency/Image (ms)':<20} {'Throughput (img/s)':<20}")
print("=" * 72)

for batch_size in batch_sizes:
    # Create dummy batch
    dummy_input = tf.random.normal([batch_size, 224, 224, 3])
    dummy_input = keras.applications.mobilenet_v2.preprocess_input(dummy_input)

    # Warmup
    for _ in range(10):
        _ = predict_batch(dummy_input)

    # Measure
    iterations = 50
    start = time.time()

    for _ in range(iterations):
        _ = predict_batch(dummy_input)

    elapsed = time.time() - start
    latency_per_batch = (elapsed / iterations) * 1000
    latency_per_image = latency_per_batch / batch_size
    throughput = (batch_size * iterations) / elapsed

    print(f"{batch_size:<12} {latency_per_batch:<20.2f} {latency_per_image:<20.2f} {throughput:<20.2f}")
```

**Expected Output (CPU)**:
```
Batch Size   Latency/Batch (ms)   Latency/Image (ms)   Throughput (img/s)
========================================================================
1            35.23                35.23                28.39
4            98.45                24.61                40.63
8            182.34               22.79                43.88
16           348.12               21.76                45.96
32           672.89               21.03                47.55
```

**Key Observation**: Larger batches improve throughput but increase per-batch latency.

✅ **Checkpoint**: You can measure and optimize TensorFlow inference performance.

---

## Part 6: SavedModel Format and TensorFlow Serving Basics

### Step 6.1: Export Model in SavedModel Format

```python
# export_savedmodel.py
import tensorflow as tf
from tensorflow import keras
import os

# Load model
print("Loading model...")
model = keras.applications.MobileNetV2(weights='imagenet')

# Define the export path
export_path = "saved_models/mobilenetv2/1"
os.makedirs(export_path, exist_ok=True)

# Save in SavedModel format
print(f"Saving model to {export_path}...")
model.save(export_path, save_format='tf')

print("Model saved successfully!")

# Verify the saved model structure
print("\nSavedModel directory structure:")
for root, dirs, files in os.walk("saved_models"):
    level = root.replace("saved_models", '').count(os.sep)
    indent = ' ' * 2 * level
    print(f"{indent}{os.path.basename(root)}/")
    subindent = ' ' * 2 * (level + 1)
    for file in files:
        print(f"{subindent}{file}")
```

**Expected Output**:
```
Loading model...
Saving model to saved_models/mobilenetv2/1...
INFO:tensorflow:Assets written to: saved_models/mobilenetv2/1/assets
Model saved successfully!

SavedModel directory structure:
saved_models/
  mobilenetv2/
    1/
      assets/
      variables/
        variables.data-00000-of-00001
        variables.index
      saved_model.pb
      keras_metadata.pb
```

### Step 6.2: Load and Use SavedModel

```python
# load_savedmodel.py
import tensorflow as tf
import numpy as np
from tensorflow import keras

# Load the SavedModel
print("Loading SavedModel...")
loaded_model = tf.keras.models.load_model("saved_models/mobilenetv2/1")

print(f"Model loaded: {loaded_model.name}")
print(f"Input shape: {loaded_model.input_shape}")
print(f"Output shape: {loaded_model.output_shape}")

# Test inference with loaded model
dummy_input = np.random.rand(1, 224, 224, 3).astype(np.float32)
dummy_input = keras.applications.mobilenet_v2.preprocess_input(dummy_input)

print("\nRunning inference with loaded model...")
predictions = loaded_model.predict(dummy_input, verbose=0)
print(f"Predictions shape: {predictions.shape}")
print(f"Predictions sum: {predictions.sum():.6f}")

print("\n✓ SavedModel works correctly!")
```

### Step 6.3: Inspect SavedModel with CLI

```python
# inspect_savedmodel.py
import subprocess
import os

# Use TensorFlow's saved_model_cli to inspect the model
export_path = "saved_models/mobilenetv2/1"

print("Inspecting SavedModel with saved_model_cli...")
print("=" * 60)

# Show all signatures
result = subprocess.run(
    ['saved_model_cli', 'show', '--dir', export_path, '--all'],
    capture_output=True,
    text=True
)

print(result.stdout)

print("\n" + "=" * 60)
print("Key Information:")
print("- signature_def: The model's input/output interface")
print("- serving_default: Default signature for TensorFlow Serving")
print("- inputs: Expected input tensors (name, shape, dtype)")
print("- outputs: Output tensors")
```

**Alternative: Python API Inspection**

```python
# inspect_savedmodel_python.py
import tensorflow as tf

# Load SavedModel
loaded = tf.saved_model.load("saved_models/mobilenetv2/1")

print("Available signatures:")
print(list(loaded.signatures.keys()))

# Get the default serving signature
serving_fn = loaded.signatures['serving_default']

print("\nServing signature details:")
print(f"Inputs: {serving_fn.structured_input_signature}")
print(f"Outputs: {serving_fn.structured_outputs}")
```

### Step 6.4: Introduction to TensorFlow Serving

**Conceptual Overview** (No Docker required for this exercise)

TensorFlow Serving is a production-grade model serving system. Key concepts:

**SavedModel Structure for Serving**:
```
saved_models/
└── mobilenetv2/          # Model name
    ├── 1/                # Version number
    │   ├── saved_model.pb
    │   ├── variables/
    │   └── assets/
    └── 2/                # New version (for A/B testing, rollbacks)
        ├── saved_model.pb
        ├── variables/
        └── assets/
```

**How TensorFlow Serving Works**:
1. Monitors a directory for model versions
2. Loads the latest version automatically
3. Serves predictions via REST API or gRPC
4. Supports batching, model versioning, and hot-swapping

**Example REST API request** (conceptual):
```bash
# If TensorFlow Serving was running on localhost:8501
curl -X POST http://localhost:8501/v1/models/mobilenetv2:predict \
  -H "Content-Type: application/json" \
  -d '{
    "instances": [
      {
        "input_1": [[[0.5, 0.5, 0.5], ...]]  # 224x224x3 image
      }
    ]
  }'
```

**Infrastructure Engineer Perspective**:
- SavedModel is the deployment format (like ONNX or TorchScript)
- Version management is built into the directory structure
- REST API makes it language-agnostic (any client can use it)
- Can scale horizontally (multiple TensorFlow Serving instances)
- Integrates with Kubernetes, Docker, load balancers

✅ **Checkpoint**: You understand SavedModel format and TensorFlow Serving concepts.

---

## Part 7: Complete Application

### Step 7.1: Build Image Classifier CLI

```python
# image_classifier.py
import tensorflow as tf
from tensorflow import keras
import numpy as np
import argparse
import time
import os
import json

class TensorFlowImageClassifier:
    """Production-ready TensorFlow image classifier"""

    def __init__(self, model_name='MobileNetV2', use_saved_model=False, model_path=None):
        """
        Initialize classifier.

        Args:
            model_name: Name of keras.applications model
            use_saved_model: If True, load from SavedModel path
            model_path: Path to SavedModel (required if use_saved_model=True)
        """
        print(f"Initializing classifier...")

        # Load model
        if use_saved_model:
            if not model_path:
                raise ValueError("model_path required when use_saved_model=True")
            print(f"Loading SavedModel from {model_path}...")
            self.model = keras.models.load_model(model_path)
        else:
            print(f"Loading {model_name} from keras.applications...")
            model_class = getattr(keras.applications, model_name)
            self.model = model_class(weights='imagenet')

        # Get preprocessing function
        if use_saved_model:
            # Assume MobileNetV2 preprocessing for saved models
            self.preprocess_fn = keras.applications.mobilenet_v2.preprocess_input
        else:
            preprocess_module = getattr(
                keras.applications,
                model_name.lower()
            )
            self.preprocess_fn = preprocess_module.preprocess_input

        # Load ImageNet labels
        self._load_labels()

        # Create optimized inference function
        @tf.function
        def predict_fn(inputs):
            return self.model(inputs, training=False)

        self.predict_fn = predict_fn

        # Warmup
        print("Warming up model...")
        dummy_input = tf.random.normal([1, 224, 224, 3])
        for _ in range(5):
            _ = self.predict_fn(dummy_input)

        print("Classifier ready!\n")

    def _load_labels(self):
        """Load ImageNet class labels"""
        labels_path = "imagenet_class_index.json"

        if not os.path.exists(labels_path):
            print("Downloading ImageNet labels...")
            import urllib.request
            url = "https://storage.googleapis.com/download.tensorflow.org/data/imagenet_class_index.json"
            urllib.request.urlretrieve(url, labels_path)

        with open(labels_path) as f:
            class_idx = json.load(f)
            self.labels = [class_idx[str(i)][1] for i in range(len(class_idx))]

    def predict(self, image_path, top_k=5):
        """
        Predict image class.

        Args:
            image_path: Path to image file
            top_k: Number of top predictions to return

        Returns:
            results: List of dicts with 'class', 'probability', 'class_id'
            inference_time_ms: Inference time in milliseconds
        """
        # Load and preprocess image
        img = keras.preprocessing.image.load_img(image_path, target_size=(224, 224))
        img_array = keras.preprocessing.image.img_to_array(img)
        img_batch = np.expand_dims(img_array, axis=0)
        preprocessed = self.preprocess_fn(img_batch)

        # Convert to tensor
        input_tensor = tf.convert_to_tensor(preprocessed, dtype=tf.float32)

        # Run inference with timing
        start = time.time()
        predictions = self.predict_fn(input_tensor)
        inference_time_ms = (time.time() - start) * 1000

        # Get top k predictions
        top_k_idx = tf.argsort(predictions[0], direction='DESCENDING')[:top_k]
        top_k_probs = tf.gather(predictions[0], top_k_idx)

        # Format results
        results = []
        for idx, prob in zip(top_k_idx.numpy(), top_k_probs.numpy()):
            results.append({
                'class': self.labels[idx],
                'probability': float(prob),
                'class_id': int(idx)
            })

        return results, inference_time_ms

def main():
    parser = argparse.ArgumentParser(description='TensorFlow Image Classifier')
    parser.add_argument('image', type=str, help='Path to image file')
    parser.add_argument('--model', type=str, default='MobileNetV2',
                       help='Model name from keras.applications')
    parser.add_argument('--top-k', type=int, default=5,
                       help='Number of top predictions')
    parser.add_argument('--saved-model', type=str, default=None,
                       help='Path to SavedModel (optional)')

    args = parser.parse_args()

    # Create classifier
    use_saved = args.saved_model is not None
    classifier = TensorFlowImageClassifier(
        model_name=args.model,
        use_saved_model=use_saved,
        model_path=args.saved_model
    )

    # Run prediction
    print(f"Classifying: {args.image}")
    print("=" * 60)
    results, inference_time = classifier.predict(args.image, top_k=args.top_k)

    # Print results
    print(f"\nTop {args.top_k} Predictions (inference: {inference_time:.2f}ms):")
    for i, result in enumerate(results):
        print(f"  {i+1}. {result['class']:<30} {result['probability']*100:>6.2f}%")
    print()

if __name__ == "__main__":
    main()
```

**Usage Examples**:
```bash
# Basic usage
python image_classifier.py test_images/elephant.jpg

# Different model
python image_classifier.py test_images/tiger.jpg --model ResNet50

# Use SavedModel
python image_classifier.py test_images/airplane.jpg --saved-model saved_models/mobilenetv2/1

# Get top 10 predictions
python image_classifier.py test_images/elephant.jpg --top-k 10
```

✅ **Checkpoint**: You have a complete, production-ready image classifier!

---

## Part 8: PyTorch vs TensorFlow Comparison

### Key Differences Summary

| Aspect | PyTorch | TensorFlow/Keras |
|--------|---------|------------------|
| **Image Format** | Channels-first (C, H, W) | Channels-last (H, W, C) |
| **Model Loading** | `torch.hub.load()` | `keras.applications.ModelName()` |
| **Eval Mode** | `model.eval()` required | Not required (but use `training=False`) |
| **No Gradient** | `with torch.no_grad():` | Not required for inference |
| **Preprocessing** | Manual transforms pipeline | Model-specific `preprocess_input()` |
| **Batch Dimension** | `unsqueeze(0)` | `np.expand_dims(axis=0)` |
| **Optimization** | TorchScript | `@tf.function` |
| **Serving** | TorchServe | TensorFlow Serving |
| **Export Format** | .pt, .pth, TorchScript | SavedModel (.pb) |

### Step 8.1: Side-by-Side Comparison

```python
# framework_comparison.py
import time
import numpy as np

# TensorFlow
import tensorflow as tf
from tensorflow import keras

# PyTorch (if available)
try:
    import torch
    from torchvision import transforms, models
    PYTORCH_AVAILABLE = True
except ImportError:
    PYTORCH_AVAILABLE = False
    print("PyTorch not available, skipping comparison")

def benchmark_tensorflow():
    """Benchmark TensorFlow inference"""
    model = keras.applications.MobileNetV2(weights='imagenet')

    @tf.function
    def predict(x):
        return model(x, training=False)

    dummy_input = tf.random.normal([1, 224, 224, 3])

    # Warmup
    for _ in range(10):
        _ = predict(dummy_input)

    # Measure
    iterations = 100
    start = time.time()
    for _ in range(iterations):
        _ = predict(dummy_input)
    elapsed = time.time() - start

    return (elapsed / iterations) * 1000

def benchmark_pytorch():
    """Benchmark PyTorch inference"""
    if not PYTORCH_AVAILABLE:
        return None

    device = torch.device('cpu')
    model = models.mobilenet_v2(pretrained=True)
    model.to(device)
    model.eval()

    dummy_input = torch.rand(1, 3, 224, 224).to(device)

    # Warmup
    with torch.no_grad():
        for _ in range(10):
            _ = model(dummy_input)

    # Measure
    iterations = 100
    start = time.time()
    with torch.no_grad():
        for _ in range(iterations):
            _ = model(dummy_input)
    elapsed = time.time() - start

    return (elapsed / iterations) * 1000

# Run benchmarks
print("Benchmarking MobileNetV2 on CPU...")
print("=" * 60)

tf_latency = benchmark_tensorflow()
print(f"TensorFlow latency: {tf_latency:.2f} ms")

if PYTORCH_AVAILABLE:
    pt_latency = benchmark_pytorch()
    print(f"PyTorch latency:    {pt_latency:.2f} ms")

    if pt_latency < tf_latency:
        speedup = tf_latency / pt_latency
        print(f"\nPyTorch is {speedup:.2f}x faster")
    else:
        speedup = pt_latency / tf_latency
        print(f"\nTensorFlow is {speedup:.2f}x faster")
else:
    print("PyTorch not available for comparison")
```

---

## Stretch Goals (Optional Challenges)

### Challenge 1: Multi-Model Comparison

**Task**: Create a script that compares multiple Keras models on the same image.

```python
def compare_models(image_path, models_to_test):
    """
    Compare multiple models on same image.

    Args:
        image_path: Path to image
        models_to_test: List of model names from keras.applications

    Returns:
        Comparison results
    """
    # TODO: Implement multi-model comparison
    # Hint: Test MobileNetV2, ResNet50, EfficientNetB0
    # Compare: latency, top-1 prediction, confidence
    pass
```

### Challenge 2: TensorFlow Serving with Docker

**Task**: Deploy your SavedModel with TensorFlow Serving using Docker.

```bash
# Pull TensorFlow Serving image
docker pull tensorflow/serving

# Run TensorFlow Serving
docker run -p 8501:8501 \
  --mount type=bind,source=/path/to/saved_models/mobilenetv2,target=/models/mobilenetv2 \
  -e MODEL_NAME=mobilenetv2 \
  -t tensorflow/serving

# Test with curl
curl -X POST http://localhost:8501/v1/models/mobilenetv2:predict \
  -H "Content-Type: application/json" \
  -d @request.json
```

### Challenge 3: Mixed Precision Inference

**Task**: Implement mixed precision (FP16) inference for faster GPU performance.

```python
# Enable mixed precision
from tensorflow.keras import mixed_precision
policy = mixed_precision.Policy('mixed_float16')
mixed_precision.set_global_policy(policy)

# TODO: Test performance improvement on GPU
```

---

## Validation and Testing

### Test Your Implementation

```python
# test_classifier.py
import os
import tensorflow as tf

def test_tensorflow_classifier():
    """Test TensorFlow classifier implementation"""
    from image_classifier import TensorFlowImageClassifier

    # Test initialization
    classifier = TensorFlowImageClassifier(model_name='MobileNetV2')
    assert classifier.model is not None, "Model should be loaded"
    assert len(classifier.labels) == 1000, "Should have 1000 ImageNet labels"

    # Test prediction
    test_image = "test_images/elephant.jpg"
    if os.path.exists(test_image):
        results, latency = classifier.predict(test_image, top_k=5)

        assert len(results) == 5, "Should return 5 predictions"
        assert results[0]['probability'] >= results[1]['probability'], "Should be sorted"
        assert latency > 0, "Latency should be positive"

        # Check probability range
        for result in results:
            assert 0 <= result['probability'] <= 1, "Probabilities should be in [0, 1]"

        print("✅ All tests passed!")
    else:
        print(f"⚠ Test image not found: {test_image}")

if __name__ == "__main__":
    test_tensorflow_classifier()
```

---

## Reflection Questions

Answer these questions to solidify your learning:

1. **How does TensorFlow's channels-last format differ from PyTorch's channels-first?**
   - Your answer:

2. **What is the purpose of `@tf.function` and how does it improve performance?**
   - Your answer:

3. **Why is SavedModel format important for production deployments?**
   - Your answer:

4. **What are the key differences between TensorFlow Serving and TorchServe?**
   - Your answer:

5. **When would you choose TensorFlow over PyTorch for inference?**
   - Your answer:

---

## Summary

**What You Accomplished**:
✅ Loaded and used pre-trained Keras models
✅ Preprocessed images using TensorFlow APIs
✅ Ran inference with Keras and TensorFlow functional APIs
✅ Measured and optimized inference performance with `@tf.function`
✅ Exported models in SavedModel format
✅ Understood TensorFlow Serving fundamentals
✅ Built a complete, production-ready image classifier
✅ Compared TensorFlow and PyTorch approaches

**Key Skills Gained**:
- Model loading from keras.applications
- Image preprocessing with TensorFlow/Keras utilities
- SavedModel export and inspection
- Performance optimization with `@tf.function`
- TensorFlow Serving concepts
- Framework comparison (TensorFlow vs PyTorch)

**Infrastructure Engineer Takeaways**:
- SavedModel is TensorFlow's deployment format (language-agnostic)
- TensorFlow Serving provides production-ready model serving
- Version management is built into the directory structure
- `@tf.function` compiles to graphs for better performance
- TensorFlow integrates well with cloud platforms (GCP, AWS, Azure)

---

## Next Steps

1. **Complete Both Exercises**: Compare your PyTorch and TensorFlow implementations
2. **Try TensorFlow Serving**: Deploy a model with Docker (optional)
3. **Experiment**: Test different keras.applications models
4. **Move to Projects**: Apply these concepts in the module projects

---

**Exercise Version**: 1.0
**Last Updated**: October 2025
**Estimated Time**: 2-3 hours
**Difficulty**: Beginner
