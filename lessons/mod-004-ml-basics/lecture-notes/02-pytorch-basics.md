# Lecture 02: PyTorch Basics for Infrastructure Engineers

## Learning Objectives

By the end of this lecture, you will be able to:

- Understand PyTorch architecture and its role in ML infrastructure
- Work with PyTorch tensors and manage CPU/GPU devices
- Load pre-trained PyTorch models from various sources
- Run inference with PyTorch models in production scenarios
- Understand PyTorch model serialization formats
- Identify and resolve common PyTorch deployment issues
- Estimate resource requirements for PyTorch models

**Duration**: 8-10 hours
**Difficulty**: Beginner to Intermediate
**Prerequisites**: Module 001 (Python), Lecture 01 (ML Overview)

---

## 1. Introduction to PyTorch

### What is PyTorch?

PyTorch is an open-source machine learning framework developed by Meta (Facebook) AI Research. For infrastructure engineers, PyTorch is important because:

**Industry Adoption**:
- Used by major companies: Meta, Tesla, Microsoft, OpenAI
- Powers products like GPT models, Tesla Autopilot, and Meta's recommendation systems
- Strong in research and increasingly in production

**Infrastructure Perspective**:
- **Dynamic computation graphs**: Models are Python code, easier to debug
- **Python-native**: Integrates naturally with Python infrastructure
- **GPU acceleration**: Optimized for NVIDIA CUDA
- **Production-ready**: TorchServe for model serving
- **Large ecosystem**: HuggingFace Transformers, PyTorch Lightning, etc.

### PyTorch vs Other Frameworks

| Feature | PyTorch | TensorFlow | ONNX |
|---------|---------|------------|------|
| **Graph Type** | Dynamic (eager) | Static (graph mode) | Static |
| **Debugging** | Python debugger works | More difficult | Not applicable |
| **Production Tools** | TorchServe | TF Serving | ONNX Runtime |
| **Mobile Support** | PyTorch Mobile | TFLite | ONNX Runtime Mobile |
| **Ecosystem** | Research-focused | Production-focused | Interoperability |
| **Learning Curve** | Pythonic, easier | Steeper | Model format only |

**For Infrastructure**:
- PyTorch: Easier to debug, common in research orgs
- TensorFlow: More mature serving tools, enterprise adoption
- ONNX: Framework-independent deployment

---

## 2. PyTorch Installation and Environment

### Installation Options

```bash
# CPU-only (lightweight, works everywhere)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# GPU-enabled (requires NVIDIA GPU with CUDA)
# Check CUDA version first
nvidia-smi  # Look for "CUDA Version: XX.X"

# CUDA 11.8
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# CUDA 12.1
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### Verifying Installation

```python
import torch

# Check PyTorch version
print(f"PyTorch version: {torch.__version__}")

# Check CUDA availability
print(f"CUDA available: {torch.cuda.is_available()}")

# If CUDA is available
if torch.cuda.is_available():
    print(f"CUDA version: {torch.version.cuda}")
    print(f"Number of GPUs: {torch.cuda.device_count()}")
    print(f"GPU name: {torch.cuda.get_device_name(0)}")

# Check CPU capabilities
print(f"Number of CPU threads: {torch.get_num_threads()}")
```

**Expected Output (with GPU)**:
```
PyTorch version: 2.1.0+cu118
CUDA available: True
CUDA version: 11.8
Number of GPUs: 1
GPU name: NVIDIA Tesla T4
Number of CPU threads: 8
```

### Infrastructure Considerations

**Docker Images**:
```dockerfile
# Official PyTorch images
FROM pytorch/pytorch:2.1.0-cuda11.8-cudnn8-runtime

# Or build your own
FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04
RUN pip install torch==2.1.0 torchvision==0.16.0 --index-url https://download.pytorch.org/whl/cu118
```

**Dependencies**:
- **torch**: Core library (~800MB for CPU, ~2GB for GPU)
- **torchvision**: Computer vision models and utilities
- **torchaudio**: Audio processing (optional for most infrastructure work)
- **CUDA toolkit**: Required for GPU support (already in nvidia/cuda images)

---

## 3. PyTorch Tensors: The Foundation

### What Are Tensors?

Tensors are multi-dimensional arrays—the fundamental data structure in PyTorch. Think of them as NumPy arrays with GPU acceleration and automatic differentiation.

```python
import torch
import numpy as np

# Creating tensors
t1 = torch.tensor([1, 2, 3, 4])                # From Python list
t2 = torch.from_numpy(np.array([1, 2, 3, 4]))  # From NumPy
t3 = torch.zeros(2, 3)                          # 2x3 matrix of zeros
t4 = torch.ones(3, 4)                           # 3x4 matrix of ones
t5 = torch.rand(2, 3)                           # Random values [0, 1)
t6 = torch.randn(2, 3)                          # Random normal distribution

print(f"t1: {t1}")
print(f"t3 shape: {t3.shape}")
print(f"t5:\n{t5}")
```

**Output**:
```
t1: tensor([1, 2, 3, 4])
t3 shape: torch.Size([2, 3])
t5:
tensor([[0.3745, 0.9507, 0.7320],
        [0.5987, 0.1560, 0.1560]])
```

### Tensor Dimensions and Shapes

```python
# Common tensor shapes in ML
scalar = torch.tensor(42)                      # 0D: single value
vector = torch.tensor([1, 2, 3])               # 1D: [3]
matrix = torch.tensor([[1, 2], [3, 4]])        # 2D: [2, 2]
image = torch.rand(3, 224, 224)                # 3D: [C, H, W]
batch_images = torch.rand(32, 3, 224, 224)     # 4D: [N, C, H, W]

print(f"Image shape: {image.shape}")           # torch.Size([3, 224, 224])
print(f"Batch shape: {batch_images.shape}")    # torch.Size([32, 3, 224, 224])

# Shape conventions:
# N = batch size
# C = channels (3 for RGB, 1 for grayscale)
# H = height
# W = width
```

### Data Types (dtype)

```python
# Common data types
t_float32 = torch.tensor([1.0, 2.0], dtype=torch.float32)  # Default for models
t_float16 = torch.tensor([1.0, 2.0], dtype=torch.float16)  # Half precision (faster)
t_int64 = torch.tensor([1, 2], dtype=torch.int64)          # Default for integers
t_bool = torch.tensor([True, False], dtype=torch.bool)     # Boolean

print(f"float32 dtype: {t_float32.dtype}")
print(f"Memory: float32={t_float32.element_size()} bytes, float16={t_float16.element_size()} bytes")
```

**Infrastructure Impact**:
- **float32**: Standard precision, 4 bytes per value
- **float16**: Half precision, 2 bytes per value, 2x memory savings, faster on modern GPUs
- **int8**: Quantized models, 1 byte per value, 4x savings vs float32

---

## 4. Device Management: CPU vs GPU

### Understanding Devices

```python
import torch

# Check available devices
cpu_device = torch.device('cpu')
cuda_device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

print(f"Using device: {cuda_device}")

# Create tensors on specific devices
t_cpu = torch.rand(3, 3, device='cpu')
t_gpu = torch.rand(3, 3, device='cuda') if torch.cuda.is_available() else torch.rand(3, 3)

print(f"t_cpu device: {t_cpu.device}")
print(f"t_gpu device: {t_gpu.device}")

# Move tensors between devices
t_moved = t_cpu.to('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Moved tensor device: {t_moved.device}")
```

### Performance Comparison

```python
import time

size = 5000

# CPU computation
t_cpu = torch.rand(size, size)
start = time.time()
result_cpu = torch.matmul(t_cpu, t_cpu)
cpu_time = time.time() - start
print(f"CPU time: {cpu_time:.4f} seconds")

# GPU computation (if available)
if torch.cuda.is_available():
    t_gpu = torch.rand(size, size, device='cuda')

    # Warm-up (first run is slower)
    _ = torch.matmul(t_gpu, t_gpu)
    torch.cuda.synchronize()

    # Actual benchmark
    start = time.time()
    result_gpu = torch.matmul(t_gpu, t_gpu)
    torch.cuda.synchronize()  # Wait for GPU to finish
    gpu_time = time.time() - start

    print(f"GPU time: {gpu_time:.4f} seconds")
    print(f"Speedup: {cpu_time/gpu_time:.2f}x")
```

**Typical Results**:
```
CPU time: 2.3456 seconds
GPU time: 0.0234 seconds
Speedup: 100.24x
```

### Infrastructure Best Practices

```python
# Pattern 1: Detect device once, use everywhere
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Pattern 2: Move model and data to same device
model = MyModel().to(device)
data = data.to(device)
output = model(data)

# Pattern 3: Clear GPU memory when done
if torch.cuda.is_available():
    torch.cuda.empty_cache()

# Pattern 4: Monitor GPU memory
if torch.cuda.is_available():
    print(f"Memory allocated: {torch.cuda.memory_allocated() / 1024**3:.2f} GB")
    print(f"Memory reserved: {torch.cuda.memory_reserved() / 1024**3:.2f} GB")
```

**Common Error**:
```python
# This will fail!
model = MyModel().to('cuda')
data = torch.rand(1, 3, 224, 224)  # On CPU by default
output = model(data)  # RuntimeError: Expected all tensors to be on the same device
```

**Fix**:
```python
model = MyModel().to('cuda')
data = torch.rand(1, 3, 224, 224).to('cuda')  # Move to GPU
output = model(data)  # Works!
```

---

## 5. Loading Pre-trained Models

### From PyTorch Hub

```python
import torch

# Load a pre-trained ResNet50 model
model = torch.hub.load('pytorch/vision:v0.10.0', 'resnet50', pretrained=True)
model.eval()  # Set to evaluation mode (important!)

print(f"Model type: {type(model)}")
print(f"Number of parameters: {sum(p.numel() for p in model.parameters()):,}")
```

**Output**:
```
Model type: <class 'torchvision.models.resnet.ResNet'>
Number of parameters: 25,557,032
```

### From HuggingFace

```python
# First install transformers
# pip install transformers

from transformers import AutoModel, AutoTokenizer

# Load BERT model and tokenizer
model_name = "bert-base-uncased"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)

print(f"Model: {model.__class__.__name__}")
print(f"Vocab size: {tokenizer.vocab_size}")
```

### From Local Files

```python
import torch

# Save a model (you would do this after training)
model = torch.hub.load('pytorch/vision', 'resnet18', pretrained=True)
torch.save(model.state_dict(), 'resnet18_weights.pth')
torch.save(model, 'resnet18_full.pth')

# Load from state_dict (recommended)
model_new = torch.hub.load('pytorch/vision', 'resnet18', pretrained=False)
model_new.load_state_dict(torch.load('resnet18_weights.pth'))
model_new.eval()

# Load full model
model_full = torch.load('resnet18_full.pth')
model_full.eval()

print("Models loaded successfully!")
```

### Infrastructure Considerations

**Model Storage**:
```bash
# Models are cached by default
ls ~/.cache/torch/hub/checkpoints/
# resnet50-0676ba61.pth (97.8 MB)
# resnet18-5c106cde.pth (44.7 MB)

# HuggingFace cache
ls ~/.cache/huggingface/hub/
# models--bert-base-uncased/ (440 MB)
```

**Best Practices**:
```python
import os
from pathlib import Path

# Set custom cache directory (useful in containers)
os.environ['TORCH_HOME'] = '/data/models/torch'
os.environ['HF_HOME'] = '/data/models/huggingface'

# Pre-download models during Docker build
# This avoids download delays during inference
model = torch.hub.load('pytorch/vision', 'resnet50', pretrained=True)
```

---

## 6. Running Inference with PyTorch

### Image Classification Example

```python
import torch
from torchvision import transforms
from PIL import Image
import urllib.request

# Load model
model = torch.hub.load('pytorch/vision', 'resnet50', pretrained=True)
model.eval()

# Load and preprocess image
url = "https://github.com/pytorch/hub/raw/master/images/dog.jpg"
urllib.request.urlretrieve(url, "dog.jpg")
image = Image.open("dog.jpg")

# Define preprocessing pipeline
preprocess = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

# Preprocess and add batch dimension
input_tensor = preprocess(image)
input_batch = input_tensor.unsqueeze(0)  # Add batch dimension: [3, 224, 224] -> [1, 3, 224, 224]

# Run inference
with torch.no_grad():  # Disable gradient computation (faster, less memory)
    output = model(input_batch)

# Get prediction
probabilities = torch.nn.functional.softmax(output[0], dim=0)
top5_prob, top5_catid = torch.topk(probabilities, 5)

# Load ImageNet labels
labels_url = "https://raw.githubusercontent.com/pytorch/hub/master/imagenet_classes.txt"
urllib.request.urlretrieve(labels_url, "imagenet_classes.txt")
with open("imagenet_classes.txt") as f:
    labels = [line.strip() for line in f.readlines()]

# Print results
print("\nTop 5 predictions:")
for i in range(5):
    print(f"{labels[top5_catid[i]]}: {top5_prob[i].item():.4f}")
```

**Output**:
```
Top 5 predictions:
Samoyed: 0.8932
Arctic fox: 0.0402
white wolf: 0.0311
Pomeranian: 0.0189
Great Pyrenees: 0.0142
```

### Batch Inference

```python
import torch
import time

model = torch.hub.load('pytorch/vision', 'resnet50', pretrained=True)
model.eval()

# Single sample inference
single_input = torch.rand(1, 3, 224, 224)
start = time.time()
with torch.no_grad():
    _ = model(single_input)
single_time = time.time() - start
print(f"Single sample: {single_time:.4f} seconds")

# Batch inference
batch_sizes = [1, 8, 16, 32, 64]
for batch_size in batch_sizes:
    batch_input = torch.rand(batch_size, 3, 224, 224)
    start = time.time()
    with torch.no_grad():
        _ = model(batch_input)
    batch_time = time.time() - start
    throughput = batch_size / batch_time
    print(f"Batch {batch_size:2d}: {batch_time:.4f}s ({throughput:.2f} samples/sec)")
```

**Typical Output (GPU)**:
```
Single sample: 0.0123 seconds
Batch  1: 0.0125s (80.00 samples/sec)
Batch  8: 0.0234s (341.88 samples/sec)
Batch 16: 0.0398s (402.01 samples/sec)
Batch 32: 0.0756s (423.28 samples/sec)
Batch 64: 0.1489s (429.82 samples/sec)
```

**Key Insights**:
- Batching significantly improves throughput
- GPU utilization increases with larger batches
- Diminishing returns after certain batch size (memory constraints)

---

## 7. Model Serialization and Loading

### Two Serialization Methods

**Method 1: Save State Dict (Recommended)**:
```python
# Save
model = torch.hub.load('pytorch/vision', 'resnet18', pretrained=True)
torch.save(model.state_dict(), 'model_weights.pth')

# Load
model = torch.hub.load('pytorch/vision', 'resnet18', pretrained=False)
model.load_state_dict(torch.load('model_weights.pth'))
model.eval()
```

**Method 2: Save Entire Model**:
```python
# Save
torch.save(model, 'model_full.pth')

# Load
model = torch.load('model_full.pth')
model.eval()
```

### Comparison

| Aspect | State Dict | Full Model |
|--------|-----------|------------|
| **File Size** | Smaller (weights only) | Larger (weights + architecture) |
| **Portability** | Requires model class definition | Self-contained |
| **Flexibility** | Can modify architecture | Architecture frozen |
| **Best For** | Production deployment | Quick experiments |
| **Recommendation** | ✅ Use this | ❌ Avoid in production |

### Production Serialization Pattern

```python
import torch
from pathlib import Path

class ModelSerializer:
    @staticmethod
    def save_model(model, path: str, metadata: dict = None):
        """Save model with metadata for production"""
        save_dict = {
            'model_state_dict': model.state_dict(),
            'model_class': model.__class__.__name__,
            'pytorch_version': torch.__version__,
        }
        if metadata:
            save_dict['metadata'] = metadata

        torch.save(save_dict, path)
        print(f"Model saved to {path}")

    @staticmethod
    def load_model(model, path: str):
        """Load model and validate metadata"""
        checkpoint = torch.load(path)

        # Validate PyTorch version
        saved_version = checkpoint.get('pytorch_version', 'unknown')
        current_version = torch.__version__
        if saved_version != current_version:
            print(f"Warning: Model saved with PyTorch {saved_version}, loading with {current_version}")

        # Load weights
        model.load_state_dict(checkpoint['model_state_dict'])
        model.eval()

        # Return metadata if exists
        return checkpoint.get('metadata', {})

# Usage
model = torch.hub.load('pytorch/vision', 'resnet18', pretrained=True)

# Save with metadata
metadata = {
    'training_date': '2025-10-18',
    'accuracy': 0.95,
    'dataset': 'ImageNet',
}
ModelSerializer.save_model(model, 'production_model.pth', metadata)

# Load
model_new = torch.hub.load('pytorch/vision', 'resnet18', pretrained=False)
metadata = ModelSerializer.load_model(model_new, 'production_model.pth')
print(f"Loaded model with metadata: {metadata}")
```

---

## 8. TorchServe: Production Model Serving

### What is TorchServe?

TorchServe is PyTorch's official model serving framework for production deployments.

**Features**:
- RESTful and gRPC APIs
- Multi-model serving
- Model versioning
- Auto-scaling
- Metrics and logging
- A/B testing support

### Installing TorchServe

```bash
pip install torchserve torch-model-archiver torch-workflow-archiver
```

### Creating a Model Archive

```python
# handler.py - Custom inference logic
import torch
from torchvision import transforms
from ts.torch_handler.base_handler import BaseHandler
from PIL import Image
import io

class ImageClassifierHandler(BaseHandler):
    def __init__(self):
        super(ImageClassifierHandler, self).__init__()
        self.transform = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406],
                              std=[0.229, 0.224, 0.225]),
        ])

    def preprocess(self, data):
        images = []
        for row in data:
            image = Image.open(io.BytesIO(row.get("data") or row.get("body")))
            image = self.transform(image)
            images.append(image)
        return torch.stack(images)

    def postprocess(self, data):
        return data.argmax(dim=1).tolist()
```

```bash
# Create model archive
torch-model-archiver \
    --model-name resnet50 \
    --version 1.0 \
    --model-file model.py \
    --serialized-file resnet50_weights.pth \
    --handler handler.py \
    --export-path model-store

# Start TorchServe
torchserve --start --model-store model-store --models resnet50=resnet50.mar

# Test inference
curl -X POST http://localhost:8080/predictions/resnet50 -T image.jpg
```

### TorchServe in Docker

```dockerfile
FROM pytorch/torchserve:latest

# Copy model archive
COPY resnet50.mar /home/model-server/model-store/

# Expose ports
EXPOSE 8080 8081 8082

# Start TorchServe with model
CMD ["torchserve", \
     "--start", \
     "--model-store", "/home/model-server/model-store", \
     "--models", "resnet50=resnet50.mar"]
```

---

## 9. Common Issues and Troubleshooting

### Issue 1: CUDA Out of Memory

**Error**:
```
RuntimeError: CUDA out of memory. Tried to allocate 1024.00 MiB
```

**Solutions**:
```python
# 1. Reduce batch size
batch_size = 8  # Instead of 32

# 2. Use gradient checkpointing (during training)
# For inference, ensure torch.no_grad()
with torch.no_grad():
    output = model(input)

# 3. Clear cache between batches
torch.cuda.empty_cache()

# 4. Use mixed precision (float16 instead of float32)
with torch.cuda.amp.autocast():
    output = model(input)

# 5. Monitor memory usage
print(f"Allocated: {torch.cuda.memory_allocated() / 1024**3:.2f} GB")
print(f"Reserved: {torch.cuda.memory_reserved() / 1024**3:.2f} GB")
```

### Issue 2: Model on Wrong Device

**Error**:
```
RuntimeError: Expected all tensors to be on the same device, but found at least two devices, cuda:0 and cpu!
```

**Solution**:
```python
# Ensure model and input are on same device
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = model.to(device)
input_tensor = input_tensor.to(device)
output = model(input_tensor)
```

### Issue 3: Model in Training Mode

**Problem**: Model gives different outputs each time (due to dropout/batchnorm)

**Solution**:
```python
# Always set model to eval mode for inference
model.eval()

# Use no_grad context
with torch.no_grad():
    output = model(input)
```

### Issue 4: Input Shape Mismatch

**Error**:
```
RuntimeError: shape '[32, 3, 224, 224]' is invalid for input of size 150528
```

**Solution**:
```python
# Check expected input shape
print(f"Input shape: {input_tensor.shape}")  # torch.Size([224, 224, 3])

# Reorder dimensions: HWC -> CHW
input_tensor = input_tensor.permute(2, 0, 1)  # Now [3, 224, 224]

# Add batch dimension
input_tensor = input_tensor.unsqueeze(0)  # Now [1, 3, 224, 224]
```

### Issue 5: Version Mismatch

**Error**:
```
RuntimeError: version_ <= kMaxSupportedFileFormatVersion INTERNAL ASSERT FAILED
```

**Solution**:
```python
# Save with specific protocol version for compatibility
torch.save(model.state_dict(), 'model.pth', _use_new_zipfile_serialization=False)

# Or update PyTorch version to match saved model version
```

---

## 10. Resource Estimation and Optimization

### Model Size and Memory

```python
import torch

def estimate_model_size(model):
    """Estimate model size in memory"""
    param_size = 0
    buffer_size = 0

    for param in model.parameters():
        param_size += param.nelement() * param.element_size()

    for buffer in model.buffers():
        buffer_size += buffer.nelement() * buffer.element_size()

    size_mb = (param_size + buffer_size) / 1024**2
    return size_mb

model = torch.hub.load('pytorch/vision', 'resnet50', pretrained=True)
print(f"Model size: {estimate_model_size(model):.2f} MB")
```

### Inference Performance Benchmarking

```python
import torch
import time

def benchmark_inference(model, input_shape, batch_sizes=[1, 8, 16, 32], warmup=10, iterations=100):
    """Benchmark model inference performance"""
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = model.to(device).eval()

    results = []
    for batch_size in batch_sizes:
        # Create dummy input
        dummy_input = torch.rand(batch_size, *input_shape).to(device)

        # Warmup
        with torch.no_grad():
            for _ in range(warmup):
                _ = model(dummy_input)

        # Benchmark
        start = time.time()
        with torch.no_grad():
            for _ in range(iterations):
                _ = model(dummy_input)

        if torch.cuda.is_available():
            torch.cuda.synchronize()

        elapsed = time.time() - start
        throughput = (batch_size * iterations) / elapsed
        latency = (elapsed / iterations) * 1000  # ms

        results.append({
            'batch_size': batch_size,
            'throughput': throughput,
            'latency_per_batch': latency,
            'latency_per_sample': latency / batch_size,
        })

    return results

# Usage
model = torch.hub.load('pytorch/vision', 'resnet50', pretrained=True)
results = benchmark_inference(model, input_shape=(3, 224, 224))

print("\nBenchmark Results:")
print(f"{'Batch Size':<12} {'Throughput':<15} {'Latency/Batch':<15} {'Latency/Sample':<15}")
for r in results:
    print(f"{r['batch_size']:<12} {r['throughput']:<15.2f} {r['latency_per_batch']:<15.2f} {r['latency_per_sample']:<15.2f}")
```

### Optimization Techniques

**1. Mixed Precision Inference**:
```python
# Use float16 instead of float32
model = model.half()  # Convert model to float16
input = input.half()  # Convert input to float16

# Or use automatic mixed precision
with torch.cuda.amp.autocast():
    output = model(input)
```

**2. TorchScript Compilation**:
```python
# Trace model for faster inference
example_input = torch.rand(1, 3, 224, 224)
traced_model = torch.jit.trace(model, example_input)
traced_model.save('model_traced.pt')

# Load and use
model = torch.jit.load('model_traced.pt')
output = model(input)
```

**3. Quantization**:
```python
# Dynamic quantization (easiest, CPU only)
quantized_model = torch.quantization.quantize_dynamic(
    model, {torch.nn.Linear}, dtype=torch.qint8
)

# Reduces model size by ~4x, faster on CPU
```

---

## Key Takeaways

### For Infrastructure Engineers

1. **PyTorch is Python-native**: Easy to debug, integrates naturally
2. **Device management is critical**: Always match model and input devices
3. **Batch inference improves throughput**: Balance latency and throughput
4. **Use torch.no_grad() for inference**: Saves memory and computation
5. **TorchServe for production**: Don't build your own serving framework
6. **Model serialization matters**: Use state_dict for flexibility
7. **Monitor GPU memory**: OOM errors are common, use empty_cache()
8. **Version compatibility**: PyTorch versions must match for loading models

### Production Checklist

Before deploying PyTorch models:

- [ ] Model set to `.eval()` mode
- [ ] All inference in `torch.no_grad()` context
- [ ] Input preprocessing defined and tested
- [ ] Output postprocessing defined and tested
- [ ] Device management (CPU/GPU) handled correctly
- [ ] Error handling for OOM and device errors
- [ ] Model versioning and metadata saved
- [ ] Performance benchmarked (latency/throughput)
- [ ] Memory requirements estimated
- [ ] TorchServe or custom serving tested

---

## Quick Reference

### Essential Commands

```python
# Installation check
import torch
print(torch.__version__)
print(torch.cuda.is_available())

# Device management
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = model.to(device)
tensor = tensor.to(device)

# Load model
model = torch.hub.load('repo', 'model_name', pretrained=True)
model.eval()

# Inference
with torch.no_grad():
    output = model(input)

# Memory management
torch.cuda.empty_cache()
print(torch.cuda.memory_allocated())
```

### Common Model Sources

- **PyTorch Hub**: `torch.hub.load('pytorch/vision', 'resnet50')`
- **HuggingFace**: `AutoModel.from_pretrained('bert-base-uncased')`
- **Torchvision**: `torchvision.models.resnet50(pretrained=True)`
- **Custom**: `torch.load('model.pth')`

---

## What's Next?

In the next lecture, we'll cover:
- **TensorFlow Basics**: Compare with PyTorch
- **TensorFlow Serving**: Production serving framework
- **Model format differences**: SavedModel vs state_dict

Continue to `lecture-notes/03-tensorflow-basics.md`

---

**Lecture Version**: 1.0
**Last Updated**: October 2025
**Estimated Completion Time**: 8-10 hours
**Difficulty**: Beginner to Intermediate
