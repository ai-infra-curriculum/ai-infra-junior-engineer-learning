# Exercise 01: PyTorch Model Inference

## Exercise Overview

**Objective**: Load a pre-trained PyTorch image classification model, run inference on real images, and measure performance metrics.

**Difficulty**: Beginner
**Estimated Time**: 2-3 hours
**Prerequisites**: Lecture 02 (PyTorch Basics)

**What You'll Learn**:
- Loading pre-trained models from PyTorch Hub
- Preprocessing images for model input
- Running inference in eval mode
- Measuring inference latency and throughput
- Handling CPU vs GPU execution

---

## Learning Objectives

By the end of this exercise, you will be able to:

✅ Load pre-trained PyTorch models from various sources
✅ Preprocess images to match model requirements
✅ Run inference correctly with `model.eval()` and `torch.no_grad()`
✅ Measure and optimize inference performance
✅ Handle device management (CPU/GPU)
✅ Debug common inference errors

---

## Part 1: Environment Setup

### Step 1.1: Install Dependencies

```bash
# Create virtual environment
python -m venv pytorch_inference_env
source pytorch_inference_env/bin/activate  # On Windows: pytorch_inference_env\Scripts\activate

# Install PyTorch and dependencies
pip install torch torchvision pillow requests
```

### Step 1.2: Verify Installation

```python
# verify_installation.py
import torch
import torchvision

print(f"PyTorch version: {torch.__version__}")
print(f"Torchvision version: {torchvision.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")

if torch.cuda.is_available():
    print(f"CUDA version: {torch.version.cuda}")
    print(f"GPU: {torch.cuda.get_device_name(0)}")
else:
    print("Running on CPU")
```

**Expected Output**:
```
PyTorch version: 2.1.0+cu118
Torchvision version: 0.16.0+cu118
CUDA available: True
CUDA version: 11.8
GPU: NVIDIA Tesla T4
```

### Step 1.3: Download Test Images

```python
# download_images.py
import urllib.request

# Download sample images
images = {
    "dog.jpg": "https://github.com/pytorch/hub/raw/master/images/dog.jpg",
    "cat.jpg": "https://upload.wikimedia.org/wikipedia/commons/4/4d/Cat_November_2010-1a.jpg",
    "car.jpg": "https://upload.wikimedia.org/wikipedia/commons/9/9a/2014_Mazda_3_%28BM%29_2.0_sedan_%282015-08-07%29_01.jpg"
}

for filename, url in images.items():
    print(f"Downloading {filename}...")
    urllib.request.urlretrieve(url, filename)

print("All images downloaded!")
```

✅ **Checkpoint**: You should have Python environment set up and 3 test images downloaded.

---

## Part 2: Loading Pre-trained Models

### Step 2.1: Load ResNet50 from PyTorch Hub

```python
# load_model.py
import torch

# Load pre-trained ResNet50
print("Loading ResNet50...")
model = torch.hub.load('pytorch/vision:v0.10.0', 'resnet50', pretrained=True)

# CRITICAL: Set to evaluation mode
model.eval()

print(f"Model loaded: {model.__class__.__name__}")
print(f"Number of parameters: {sum(p.numel() for p in model.parameters()):,}")
```

**Expected Output**:
```
Loading ResNet50...
Downloading: 100%|██████████| 97.8M/97.8M
Model loaded: ResNet
Number of parameters: 25,557,032
```

### Step 2.2: Understanding Model Architecture

**Task**: Examine the model structure to understand its layers.

```python
# examine_model.py
import torch

model = torch.hub.load('pytorch/vision', 'resnet50', pretrained=True)

# Print model summary
print("Model Architecture:")
print(model)

# Count layers by type
layer_counts = {}
for name, module in model.named_modules():
    layer_type = module.__class__.__name__
    layer_counts[layer_type] = layer_counts.get(layer_type, 0) + 1

print("\nLayer Counts:")
for layer_type, count in sorted(layer_counts.items()):
    print(f"  {layer_type}: {count}")

# Model input requirements
print("\nModel Expectations:")
print("  Input shape: [batch_size, 3, 224, 224]")
print("  Input type: float32 tensor")
print("  Output shape: [batch_size, 1000] (ImageNet classes)")
```

**Questions to Answer** (write your answers):
1. How many convolutional layers does ResNet50 have?
2. What is the expected input shape?
3. How many output classes does the model predict?

✅ **Checkpoint**: Model loaded successfully and you understand its architecture.

---

## Part 3: Image Preprocessing

### Step 3.1: Implement Preprocessing Pipeline

```python
# preprocess.py
import torch
from torchvision import transforms
from PIL import Image

def create_preprocessing_pipeline():
    """Create image preprocessing pipeline for ResNet models"""
    return transforms.Compose([
        transforms.Resize(256),                # Resize shortest side to 256
        transforms.CenterCrop(224),            # Crop center 224x224
        transforms.ToTensor(),                 # Convert to tensor [0, 1]
        transforms.Normalize(                  # Normalize with ImageNet stats
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        ),
    ])

def preprocess_image(image_path: str):
    """Load and preprocess an image"""
    # Load image
    image = Image.open(image_path).convert('RGB')
    print(f"Original image size: {image.size}")

    # Apply preprocessing
    preprocess = create_preprocessing_pipeline()
    tensor = preprocess(image)

    print(f"Preprocessed tensor shape: {tensor.shape}")
    print(f"Tensor dtype: {tensor.dtype}")
    print(f"Tensor range: [{tensor.min():.3f}, {tensor.max():.3f}]")

    # Add batch dimension [C, H, W] -> [1, C, H, W]
    batch = tensor.unsqueeze(0)
    print(f"Batch shape: {batch.shape}")

    return batch

# Test preprocessing
image_tensor = preprocess_image("dog.jpg")
```

**Expected Output**:
```
Original image size: (576, 768)
Preprocessed tensor shape: torch.Size([3, 224, 224])
Tensor dtype: torch.float32
Tensor range: [-2.118, 2.640]
Batch shape: torch.Size([1, 3, 224, 224])
```

### Step 3.2: Understand Preprocessing Steps

**Task**: Answer these questions about preprocessing:

1. **Why resize to 256 then crop to 224?**
   - Hint: Preserves aspect ratio while getting correct size

2. **What do the normalization values mean?**
   - mean=[0.485, 0.456, 0.406]: ImageNet dataset mean for R, G, B
   - std=[0.229, 0.224, 0.225]: ImageNet dataset std for R, G, B

3. **Why is the tensor range negative?**
   - Hint: Normalization formula is (x - mean) / std

✅ **Checkpoint**: You can preprocess images correctly.

---

## Part 4: Running Inference

### Step 4.1: Basic Inference

```python
# inference.py
import torch
from torchvision import transforms
from PIL import Image
import urllib.request

# Load model
model = torch.hub.load('pytorch/vision', 'resnet50', pretrained=True)
model.eval()  # IMPORTANT!

# Load and preprocess image
preprocess = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

image = Image.open("dog.jpg")
input_tensor = preprocess(image)
input_batch = input_tensor.unsqueeze(0)

# Run inference
with torch.no_grad():  # IMPORTANT: Disable gradient computation
    output = model(input_batch)

print(f"Output shape: {output.shape}")  # [1, 1000]
print(f"Output type: {output.dtype}")
print(f"Output sample: {output[0, :5]}")  # First 5 values
```

**Expected Output**:
```
Output shape: torch.Size([1, 1000])
Output type: torch.float32
Output sample: tensor([-1.2345,  0.5678, -0.9123,  1.4567, -0.3456])
```

### Step 4.2: Get Top Predictions

```python
# get_predictions.py
import torch
from torchvision import transforms
from PIL import Image
import urllib.request

# Load ImageNet class labels
labels_url = "https://raw.githubusercontent.com/pytorch/hub/master/imagenet_classes.txt"
urllib.request.urlretrieve(labels_url, "imagenet_classes.txt")

with open("imagenet_classes.txt") as f:
    labels = [line.strip() for line in f.readlines()]

# Load model and image
model = torch.hub.load('pytorch/vision', 'resnet50', pretrained=True)
model.eval()

preprocess = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

image = Image.open("dog.jpg")
input_tensor = preprocess(image)
input_batch = input_tensor.unsqueeze(0)

# Run inference
with torch.no_grad():
    output = model(input_batch)

# Get probabilities
probabilities = torch.nn.functional.softmax(output[0], dim=0)

# Get top 5 predictions
top5_prob, top5_idx = torch.topk(probabilities, 5)

print("Top 5 Predictions:")
for i in range(5):
    class_idx = top5_idx[i].item()
    prob = top5_prob[i].item()
    print(f"  {i+1}. {labels[class_idx]:<30} {prob*100:>6.2f}%")
```

**Expected Output**:
```
Top 5 Predictions:
  1. Samoyed                      89.32%
  2. Pomeranian                    4.02%
  3. white wolf                    3.11%
  4. keeshond                      1.89%
  5. Great Pyrenees                1.42%
```

✅ **Checkpoint**: You can run inference and get meaningful predictions!

---

## Part 5: Performance Measurement

### Step 5.1: Measure Inference Latency

```python
# measure_latency.py
import torch
from torchvision import transforms
from PIL import Image
import time

# Load model
model = torch.hub.load('pytorch/vision', 'resnet50', pretrained=True)
model.eval()

# Prepare input
preprocess = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

image = Image.open("dog.jpg")
input_tensor = preprocess(image).unsqueeze(0)

# Warmup (first run is slower)
print("Warming up...")
with torch.no_grad():
    for _ in range(10):
        _ = model(input_tensor)

# Measure latency
print("\nMeasuring latency...")
iterations = 100
start = time.time()

with torch.no_grad():
    for _ in range(iterations):
        _ = model(input_tensor)

elapsed = time.time() - start
avg_latency_ms = (elapsed / iterations) * 1000

print(f"Average latency: {avg_latency_ms:.2f} ms")
print(f"Throughput: {1000/avg_latency_ms:.2f} images/second")
```

### Step 5.2: Batch Inference Performance

```python
# batch_inference.py
import torch
import time

model = torch.hub.load('pytorch/vision', 'resnet50', pretrained=True)
model.eval()

# Test different batch sizes
batch_sizes = [1, 4, 8, 16, 32]
print(f"{'Batch Size':<12} {'Latency (ms)':<15} {'Throughput (img/s)':<20}")

for batch_size in batch_sizes:
    # Create dummy batch
    dummy_input = torch.rand(batch_size, 3, 224, 224)

    # Warmup
    with torch.no_grad():
        for _ in range(10):
            _ = model(dummy_input)

    # Measure
    iterations = 50
    start = time.time()

    with torch.no_grad():
        for _ in range(iterations):
            _ = model(dummy_input)

    elapsed = time.time() - start
    latency_per_batch = (elapsed / iterations) * 1000
    throughput = (batch_size * iterations) / elapsed

    print(f"{batch_size:<12} {latency_per_batch:<15.2f} {throughput:<20.2f}")
```

**Expected Output (CPU)**:
```
Batch Size   Latency (ms)    Throughput (img/s)
1            45.23           22.11
4            152.34          26.24
8            298.45          26.81
16           589.23          27.15
32           1156.78         27.67
```

✅ **Checkpoint**: You can measure and understand inference performance.

---

## Part 6: GPU Acceleration

### Step 6.1: CPU vs GPU Comparison

```python
# cpu_vs_gpu.py
import torch
import time

# Load model
model = torch.hub.load('pytorch/vision', 'resnet50', pretrained=True)
model.eval()

# Prepare input
dummy_input = torch.rand(1, 3, 224, 224)

def benchmark(model, input_tensor, device, iterations=100):
    """Benchmark inference on specific device"""
    model = model.to(device)
    input_tensor = input_tensor.to(device)

    # Warmup
    with torch.no_grad():
        for _ in range(10):
            _ = model(input_tensor)

    if device.type == 'cuda':
        torch.cuda.synchronize()

    # Measure
    start = time.time()
    with torch.no_grad():
        for _ in range(iterations):
            _ = model(input_tensor)

    if device.type == 'cuda':
        torch.cuda.synchronize()

    elapsed = time.time() - start
    return (elapsed / iterations) * 1000  # ms

# Benchmark CPU
cpu_latency = benchmark(model, dummy_input, torch.device('cpu'))
print(f"CPU latency: {cpu_latency:.2f} ms")

# Benchmark GPU (if available)
if torch.cuda.is_available():
    gpu_latency = benchmark(model, dummy_input, torch.device('cuda'))
    print(f"GPU latency: {gpu_latency:.2f} ms")
    print(f"Speedup: {cpu_latency/gpu_latency:.2f}x")
else:
    print("GPU not available")
```

**Expected Output (with GPU)**:
```
CPU latency: 45.23 ms
GPU latency: 3.45 ms
Speedup: 13.11x
```

✅ **Checkpoint**: You understand CPU vs GPU performance differences.

---

## Part 7: Complete Application

### Step 7.1: Build Image Classifier CLI

```python
# image_classifier.py
import torch
from torchvision import transforms
from PIL import Image
import argparse
import time

class ImageClassifier:
    def __init__(self, model_name='resnet50', device='auto'):
        """Initialize image classifier"""
        print(f"Loading {model_name}...")

        # Determine device
        if device == 'auto':
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        else:
            self.device = torch.device(device)

        print(f"Using device: {self.device}")

        # Load model
        self.model = torch.hub.load('pytorch/vision', model_name, pretrained=True)
        self.model.to(self.device)
        self.model.eval()

        # Load labels
        import urllib.request
        labels_url = "https://raw.githubusercontent.com/pytorch/hub/master/imagenet_classes.txt"
        urllib.request.urlretrieve(labels_url, "imagenet_classes.txt")

        with open("imagenet_classes.txt") as f:
            self.labels = [line.strip() for line in f.readlines()]

        # Preprocessing pipeline
        self.preprocess = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])

        print("Classifier ready!")

    def predict(self, image_path, top_k=5):
        """Predict image class"""
        # Load and preprocess image
        image = Image.open(image_path).convert('RGB')
        input_tensor = self.preprocess(image)
        input_batch = input_tensor.unsqueeze(0).to(self.device)

        # Run inference
        start = time.time()
        with torch.no_grad():
            output = self.model(input_batch)
        inference_time = (time.time() - start) * 1000

        # Get probabilities
        probabilities = torch.nn.functional.softmax(output[0], dim=0)

        # Get top k predictions
        topk_prob, topk_idx = torch.topk(probabilities, top_k)

        results = []
        for i in range(top_k):
            class_idx = topk_idx[i].item()
            prob = topk_prob[i].item()
            results.append({
                'class': self.labels[class_idx],
                'probability': prob,
                'class_id': class_idx
            })

        return results, inference_time

def main():
    parser = argparse.ArgumentParser(description='PyTorch Image Classifier')
    parser.add_argument('image', type=str, help='Path to image file')
    parser.add_argument('--model', type=str, default='resnet50', help='Model name')
    parser.add_argument('--top-k', type=int, default=5, help='Number of top predictions')
    parser.add_argument('--device', type=str, default='auto', help='Device (cpu/cuda/auto)')

    args = parser.parse_args()

    # Create classifier
    classifier = ImageClassifier(model_name=args.model, device=args.device)

    # Run prediction
    print(f"\nClassifying: {args.image}")
    results, inference_time = classifier.predict(args.image, top_k=args.top_k)

    # Print results
    print(f"\nTop {args.top_k} Predictions (inference: {inference_time:.2f}ms):")
    for i, result in enumerate(results):
        print(f"  {i+1}. {result['class']:<30} {result['probability']*100:>6.2f}%")

if __name__ == "__main__":
    main()
```

**Usage**:
```bash
# Classify an image
python image_classifier.py dog.jpg

# Use different model
python image_classifier.py dog.jpg --model resnet18

# Force CPU
python image_classifier.py dog.jpg --device cpu

# Get top 10 predictions
python image_classifier.py dog.jpg --top-k 10
```

✅ **Checkpoint**: You have a complete, working image classifier!

---

## Stretch Goals (Optional Challenges)

### Challenge 1: Multi-Image Batch Processing

**Task**: Modify the classifier to process multiple images in a single batch.

```python
def predict_batch(self, image_paths, top_k=5):
    """Predict classes for multiple images"""
    # TODO: Implement batch prediction
    # Hint: Stack preprocessed images into a single batch
    pass
```

### Challenge 2: Model Comparison

**Task**: Compare different model architectures (ResNet18, ResNet50, MobileNet).

Measure:
- Inference latency
- Accuracy (on same images)
- Model size

### Challenge 3: Error Handling

**Task**: Add proper error handling for:
- Invalid image files
- Out of memory errors
- Missing GPU

---

## Validation and Testing

### Test Your Implementation

```python
# test_classifier.py
import os

def test_classifier():
    """Test image classifier implementation"""
    from image_classifier import ImageClassifier

    # Test initialization
    classifier = ImageClassifier(model_name='resnet18', device='cpu')
    assert classifier.device.type == 'cpu', "Device should be CPU"

    # Test prediction
    results, latency = classifier.predict('dog.jpg', top_k=5)
    assert len(results) == 5, "Should return 5 predictions"
    assert results[0]['probability'] > results[1]['probability'], "Should be sorted by probability"
    assert latency > 0, "Latency should be positive"

    # Test probabilities sum to ~1
    total_prob = sum(r['probability'] for r in results[:5])
    assert 0.95 <= total_prob <= 1.05, f"Top 5 probabilities should sum close to 1, got {total_prob}"

    print("✅ All tests passed!")

if __name__ == "__main__":
    test_classifier()
```

---

## Reflection Questions

Answer these questions to solidify your learning:

1. **Why is `model.eval()` necessary?**
   - Your answer:

2. **What happens if you forget `torch.no_grad()`?**
   - Your answer:

3. **Why do we need to normalize images with ImageNet statistics?**
   - Your answer:

4. **How does batch size affect throughput and latency?**
   - Your answer:

5. **When would you choose CPU over GPU for inference?**
   - Your answer:

---

## Summary

**What You Accomplished**:
✅ Loaded and used pre-trained PyTorch models
✅ Preprocessed images correctly
✅ Ran inference with proper eval mode and no_grad context
✅ Measured inference performance
✅ Compared CPU vs GPU execution
✅ Built a complete image classification application

**Key Skills Gained**:
- Model loading from PyTorch Hub
- Image preprocessing with torchvision.transforms
- Proper inference patterns (eval, no_grad)
- Performance measurement and optimization
- Device management (CPU/GPU)

---

## Next Steps

1. **Complete Exercise 02**: TensorFlow Model Inference
2. **Compare frameworks**: Notice differences between PyTorch and TensorFlow
3. **Experiment**: Try different models and images

---

**Exercise Version**: 1.0
**Last Updated**: October 2025
**Estimated Time**: 2-3 hours
**Difficulty**: Beginner
