# Exercise 05: GPU Basics - Accelerating ML Inference

**Difficulty**: Beginner-Intermediate
**Duration**: 2-3 hours
**Prerequisites**: Python fundamentals, Exercise 01-04 completed

**Note**: This exercise can be completed without a physical GPU using cloud resources or CPU-only mode for learning concepts.

## Learning Objectives

By the end of this exercise, you will:

1. Understand why GPUs accelerate ML workloads
2. Check for GPU availability and capabilities
3. Move models and data between CPU and GPU
4. Compare CPU vs GPU inference performance
5. Understand GPU memory management basics
6. Troubleshoot common GPU-related issues

## What You'll Build

A performance comparison tool that:
- Detects available hardware (CPU/GPU)
- Runs the same model on both CPU and GPU
- Measures and compares performance
- Generates a performance report

## Background: Why GPUs for ML?

### CPU vs GPU Architecture

**CPU (Central Processing Unit)**:
- Few cores (4-64 typically)
- High clock speed
- Complex instruction sets
- Good for sequential tasks

**GPU (Graphics Processing Unit)**:
- Thousands of cores (2000-10000+)
- Lower clock speed per core
- Optimized for parallel operations
- Excellent for matrix math (ML's foundation)

### Why ML Benefits from GPUs

Machine learning is fundamentally about matrix multiplications:

```
Input (1000 values) × Weights (1000×1000 matrix) = Output (1000 values)
```

**On CPU**: Multiply row by column sequentially
**On GPU**: Multiply thousands of elements simultaneously

**Speedup Example**:
- Training ResNet-50: CPU ~2 weeks, GPU ~1 day
- LLM inference: CPU ~1 token/s, GPU ~50 tokens/s

## Part 1: GPU Detection and Setup

### Step 1: Install CUDA-Enabled PyTorch

First, check if you have NVIDIA GPU:

```bash
# Linux/Mac
nvidia-smi

# If command not found, you don't have NVIDIA GPU or drivers
```

**If you have NVIDIA GPU**:

```bash
# Install PyTorch with CUDA support
pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

**If you DON'T have GPU** (we can still learn concepts):

```bash
# Install CPU-only PyTorch
pip3 install torch torchvision
```

Install other dependencies:

```bash
pip install transformers psutil
```

### Step 2: Check GPU Availability

Create `check_gpu.py`:

```python
import torch
import sys

print("=" * 60)
print("GPU Detection and Information")
print("=" * 60)

# Check CUDA availability
cuda_available = torch.cuda.is_available()
print(f"\nCUDA Available: {cuda_available}")

if cuda_available:
    # GPU information
    gpu_count = torch.cuda.device_count()
    print(f"Number of GPUs: {gpu_count}")

    for i in range(gpu_count):
        print(f"\n--- GPU {i} ---")
        print(f"Name: {torch.cuda.get_device_name(i)}")
        print(f"Compute Capability: {torch.cuda.get_device_capability(i)}")

        # Memory information
        total_memory = torch.cuda.get_device_properties(i).total_memory
        print(f"Total Memory: {total_memory / 1024**3:.2f} GB")

        # Current memory usage
        allocated = torch.cuda.memory_allocated(i) / 1024**3
        reserved = torch.cuda.memory_reserved(i) / 1024**3
        print(f"Currently Allocated: {allocated:.2f} GB")
        print(f"Currently Reserved: {reserved:.2f} GB")

    # CUDA version
    print(f"\nCUDA Version: {torch.version.cuda}")
    print(f"cuDNN Version: {torch.backends.cudnn.version()}")
    print(f"cuDNN Enabled: {torch.backends.cudnn.enabled}")

else:
    print("\nNo CUDA-capable GPU detected.")
    print("This is fine for learning! We can still run everything on CPU.")
    print("\nTo use GPU in the future:")
    print("1. Get a machine with NVIDIA GPU")
    print("2. Install NVIDIA drivers")
    print("3. Install CUDA toolkit")
    print("4. Install PyTorch with CUDA support")

# PyTorch configuration
print("\n" + "=" * 60)
print("PyTorch Configuration")
print("=" * 60)
print(f"PyTorch Version: {torch.__version__}")
print(f"Python Version: {sys.version.split()[0]}")

# Test tensor creation on different devices
print("\n" + "=" * 60)
print("Device Testing")
print("=" * 60)

# CPU tensor
cpu_tensor = torch.randn(1000, 1000)
print(f"✓ CPU tensor created: {cpu_tensor.shape}")
print(f"  Device: {cpu_tensor.device}")

# GPU tensor (if available)
if cuda_available:
    gpu_tensor = torch.randn(1000, 1000, device='cuda')
    print(f"✓ GPU tensor created: {gpu_tensor.shape}")
    print(f"  Device: {gpu_tensor.device}")
else:
    print("⚠ GPU tensors not available (CPU only mode)")
```

Run it:

```bash
python check_gpu.py
```

**Example output with GPU**:
```
============================================================
GPU Detection and Information
============================================================

CUDA Available: True
Number of GPUs: 1

--- GPU 0 ---
Name: NVIDIA GeForce RTX 3060
Compute Capability: (8, 6)
Total Memory: 12.00 GB
Currently Allocated: 0.00 GB
Currently Reserved: 0.00 GB

CUDA Version: 11.8
cuDNN Version: 8700
cuDNN Enabled: True

============================================================
PyTorch Configuration
============================================================
PyTorch Version: 2.0.0
Python Version: 3.10.12

============================================================
Device Testing
============================================================
✓ CPU tensor created: torch.Size([1000, 1000])
  Device: cpu
✓ GPU tensor created: torch.Size([1000, 1000])
  Device: cuda:0
```

## Part 2: Moving Data Between CPU and GPU

### Step 3: Device Management Basics

Create `device_management.py`:

```python
import torch
import time

print("Device Management Basics")
print("=" * 60)

# Determine device
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Using device: {device}\n")

# Create tensor on CPU
print("1. Creating tensor on CPU")
cpu_tensor = torch.randn(1000, 1000)
print(f"   Shape: {cpu_tensor.shape}")
print(f"   Device: {cpu_tensor.device}")
print(f"   Memory: {cpu_tensor.element_size() * cpu_tensor.nelement() / 1024**2:.2f} MB")

if torch.cuda.is_available():
    print("\n2. Moving tensor to GPU")
    start = time.time()
    gpu_tensor = cpu_tensor.to('cuda')  # or cpu_tensor.cuda()
    transfer_time = time.time() - start

    print(f"   Device: {gpu_tensor.device}")
    print(f"   Transfer time: {transfer_time*1000:.2f} ms")

    print("\n3. Moving tensor back to CPU")
    start = time.time()
    cpu_tensor_back = gpu_tensor.to('cpu')  # or gpu_tensor.cpu()
    transfer_time = time.time() - start

    print(f"   Device: {cpu_tensor_back.device}")
    print(f"   Transfer time: {transfer_time*1000:.2f} ms")

    # Check memory usage
    print("\n4. GPU Memory Usage")
    allocated = torch.cuda.memory_allocated() / 1024**2
    reserved = torch.cuda.memory_reserved() / 1024**2
    print(f"   Allocated: {allocated:.2f} MB")
    print(f"   Reserved: {reserved:.2f} MB")

    # Clean up GPU memory
    print("\n5. Cleaning up GPU memory")
    del gpu_tensor
    torch.cuda.empty_cache()

    allocated = torch.cuda.memory_allocated() / 1024**2
    print(f"   Allocated after cleanup: {allocated:.2f} MB")

else:
    print("\n⚠ GPU not available - skipping GPU operations")

print("\n" + "=" * 60)
print("Best Practices:")
print("=" * 60)
print("1. Move model to device ONCE at startup")
print("2. Move input data to same device as model")
print("3. Move output back to CPU if needed for further processing")
print("4. Clean up GPU memory when done with large tensors")
```

## Part 3: CPU vs GPU Performance Comparison

### Step 4: Benchmark Matrix Operations

Create `benchmark_operations.py`:

```python
import torch
import time

def benchmark_matmul(size, device, iterations=100):
    """Benchmark matrix multiplication on device"""
    # Create random matrices
    a = torch.randn(size, size, device=device)
    b = torch.randn(size, size, device=device)

    # Warmup (important for GPU!)
    for _ in range(10):
        _ = torch.matmul(a, b)

    # Synchronize GPU before timing
    if device.type == 'cuda':
        torch.cuda.synchronize()

    # Benchmark
    start = time.time()
    for _ in range(iterations):
        c = torch.matmul(a, b)

    # Synchronize again (GPU operations are async)
    if device.type == 'cuda':
        torch.cuda.synchronize()

    elapsed = time.time() - start
    avg_time = elapsed / iterations

    return avg_time * 1000  # Convert to milliseconds

# Run benchmarks
print("=" * 60)
print("Matrix Multiplication Benchmark")
print("=" * 60)

sizes = [100, 500, 1000, 2000]

for size in sizes:
    print(f"\nMatrix size: {size}x{size}")

    # CPU benchmark
    cpu_time = benchmark_matmul(size, torch.device('cpu'))
    print(f"  CPU: {cpu_time:.2f} ms")

    # GPU benchmark (if available)
    if torch.cuda.is_available():
        gpu_time = benchmark_matmul(size, torch.device('cuda'))
        speedup = cpu_time / gpu_time
        print(f"  GPU: {gpu_time:.2f} ms")
        print(f"  Speedup: {speedup:.1f}x faster")
    else:
        print("  GPU: Not available")

# Summary
print("\n" + "=" * 60)
print("Key Observations:")
print("=" * 60)
print("1. GPU is slower for small matrices (overhead costs)")
print("2. GPU advantage grows with matrix size")
print("3. For ML, most operations are large enough to benefit from GPU")
```

**Expected output**:
```
Matrix Multiplication Benchmark
============================================================

Matrix size: 100x100
  CPU: 0.12 ms
  GPU: 0.25 ms
  Speedup: 0.5x faster  ← GPU slower for tiny matrices!

Matrix size: 500x500
  CPU: 8.45 ms
  GPU: 0.85 ms
  Speedup: 9.9x faster

Matrix size: 1000x1000
  CPU: 42.33 ms
  GPU: 1.87 ms
  Speedup: 22.6x faster

Matrix size: 2000x2000
  CPU: 421.56 ms
  GPU: 5.34 ms
  Speedup: 78.9x faster  ← Massive speedup!
```

### Step 5: Model Inference Comparison

Create `inference_benchmark.py`:

```python
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import time
import psutil

def get_memory_usage():
    """Get current process memory in MB"""
    process = psutil.Process()
    return process.memory_info().rss / 1024 / 1024

def benchmark_model(model_name, device, num_runs=10):
    """Benchmark model inference on specified device"""
    print(f"\n{'=' * 60}")
    print(f"Testing on {device}")
    print(f"{'=' * 60}")

    # Memory before loading
    mem_before = get_memory_usage()

    # Load model and tokenizer
    print("Loading model...")
    start = time.time()

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)
    model = model.to(device)

    load_time = time.time() - start

    # Memory after loading
    mem_after = get_memory_usage()
    model_memory = mem_after - mem_before

    print(f"✓ Model loaded in {load_time:.2f}s")
    print(f"  Memory usage: {model_memory:.2f} MB")

    # GPU memory if applicable
    if device.type == 'cuda':
        gpu_memory = torch.cuda.memory_allocated() / 1024 / 1024
        print(f"  GPU memory: {gpu_memory:.2f} MB")

    # Prepare input
    prompt = "Machine learning infrastructure requires"
    inputs = tokenizer(prompt, return_tensors="pt")
    inputs = {k: v.to(device) for k, v in inputs.items()}

    # Warmup
    print("Warming up...")
    with torch.no_grad():
        for _ in range(3):
            _ = model.generate(**inputs, max_length=50)

    # Benchmark
    print(f"Running {num_runs} inference iterations...")
    inference_times = []

    for i in range(num_runs):
        # Synchronize if GPU
        if device.type == 'cuda':
            torch.cuda.synchronize()

        start = time.time()

        with torch.no_grad():
            outputs = model.generate(**inputs, max_length=50)

        # Synchronize if GPU
        if device.type == 'cuda':
            torch.cuda.synchronize()

        elapsed = time.time() - start
        inference_times.append(elapsed)

        if i == 0:  # Show first output
            generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
            print(f"\nSample output:\n{generated_text}\n")

    # Statistics
    avg_time = sum(inference_times) / len(inference_times)
    min_time = min(inference_times)
    max_time = max(inference_times)

    print(f"Inference Statistics:")
    print(f"  Average: {avg_time:.3f}s")
    print(f"  Min: {min_time:.3f}s")
    print(f"  Max: {max_time:.3f}s")
    print(f"  Tokens/second: ~{50/avg_time:.1f}")

    # Cleanup
    del model
    if device.type == 'cuda':
        torch.cuda.empty_cache()

    return {
        'device': str(device),
        'load_time': load_time,
        'memory_mb': model_memory,
        'avg_inference_time': avg_time,
        'tokens_per_sec': 50/avg_time
    }

# Main benchmark
model_name = "gpt2"  # Small model for testing

print("=" * 60)
print(f"Model Inference Benchmark: {model_name}")
print("=" * 60)

results = []

# CPU benchmark
cpu_result = benchmark_model(model_name, torch.device('cpu'))
results.append(cpu_result)

# GPU benchmark (if available)
if torch.cuda.is_available():
    gpu_result = benchmark_model(model_name, torch.device('cuda'))
    results.append(gpu_result)

    # Comparison
    print(f"\n{'=' * 60}")
    print("Comparison Summary")
    print(f"{'=' * 60}")

    speedup = cpu_result['avg_inference_time'] / gpu_result['avg_inference_time']
    print(f"\nInference Speedup: {speedup:.1f}x faster on GPU")
    print(f"CPU: {cpu_result['avg_inference_time']:.3f}s per inference")
    print(f"GPU: {gpu_result['avg_inference_time']:.3f}s per inference")

    print(f"\nThroughput:")
    print(f"CPU: {cpu_result['tokens_per_sec']:.1f} tokens/s")
    print(f"GPU: {gpu_result['tokens_per_sec']:.1f} tokens/s")

else:
    print("\n⚠ No GPU available for comparison")
```

## Part 4: GPU Memory Management

### Step 6: Understanding GPU Memory

Create `gpu_memory_management.py`:

```python
import torch

if not torch.cuda.is_available():
    print("GPU not available - skipping this exercise")
    exit(0)

def print_gpu_memory(label=""):
    """Print current GPU memory usage"""
    allocated = torch.cuda.memory_allocated() / 1024**2
    reserved = torch.cuda.memory_reserved() / 1024**2
    total = torch.cuda.get_device_properties(0).total_memory / 1024**2

    if label:
        print(f"\n{label}")
    print(f"  Allocated: {allocated:.2f} MB")
    print(f"  Reserved: {reserved:.2f} MB")
    print(f"  Total Available: {total:.2f} MB")
    print(f"  Free: {total - allocated:.2f} MB")

print("GPU Memory Management")
print("=" * 60)

# Initial state
print_gpu_memory("Initial state:")

# Allocate tensor
print("\nAllocating 1000x1000 tensor...")
tensor1 = torch.randn(1000, 1000, device='cuda')
print_gpu_memory("After allocation:")

# Allocate more
print("\nAllocating another 2000x2000 tensor...")
tensor2 = torch.randn(2000, 2000, device='cuda')
print_gpu_memory("After second allocation:")

# Delete tensor
print("\nDeleting first tensor...")
del tensor1
print_gpu_memory("After deletion (memory still reserved):")

# Empty cache
print("\nEmptying cache...")
torch.cuda.empty_cache()
print_gpu_memory("After emptying cache:")

# Out of memory example (be careful!)
print("\n" + "=" * 60)
print("Handling Out of Memory")
print("=" * 60)

try:
    # Try to allocate huge tensor
    print("\nTrying to allocate massive tensor...")
    huge_tensor = torch.randn(50000, 50000, device='cuda')
except RuntimeError as e:
    print(f"✗ Out of Memory Error:")
    print(f"  {str(e)}")
    print("\n  This is expected! GPU memory is limited.")
    print("  In production, you would:")
    print("  - Use smaller batch sizes")
    print("  - Use gradient checkpointing")
    print("  - Use model parallelism")
    print("  - Use mixed precision (FP16)")

# Cleanup
del tensor2
torch.cuda.empty_cache()
print_gpu_memory("\nAfter cleanup:")
```

## Part 5: Building a Device-Agnostic API

### Step 7: Smart Device Selection

Create `smart_device_api.py`:

```python
from flask import Flask, request, jsonify
from transformers import pipeline
import torch
import time

app = Flask(__name__)

# Smart device selection
device = 0 if torch.cuda.is_available() else -1  # 0 = GPU, -1 = CPU
device_name = "GPU" if device == 0 else "CPU"

print(f"Loading model on {device_name}...")
generator = pipeline('text-generation', model='gpt2', device=device)
print(f"✓ Model ready on {device_name}!")

@app.route('/info', methods=['GET'])
def info():
    """Get system information"""
    info_data = {
        "device": device_name,
        "cuda_available": torch.cuda.is_available(),
        "model": "gpt2"
    }

    if torch.cuda.is_available():
        info_data.update({
            "gpu_name": torch.cuda.get_device_name(0),
            "gpu_memory_total_gb": torch.cuda.get_device_properties(0).total_memory / 1024**3,
            "gpu_memory_allocated_gb": torch.cuda.memory_allocated() / 1024**3
        })

    return jsonify(info_data)

@app.route('/generate', methods=['POST'])
def generate():
    """Generate text with performance metrics"""
    data = request.get_json()
    prompt = data.get('prompt', '')

    if not prompt:
        return jsonify({"error": "Prompt required"}), 400

    # Measure inference time
    start = time.time()

    result = generator(
        prompt,
        max_length=data.get('max_length', 50),
        temperature=data.get('temperature', 0.7),
        num_return_sequences=1
    )

    inference_time = time.time() - start

    # Calculate tokens/second (approximate)
    tokens_generated = len(result[0]['generated_text'].split())
    tokens_per_sec = tokens_generated / inference_time

    response = {
        "prompt": prompt,
        "generated_text": result[0]['generated_text'],
        "device": device_name,
        "inference_time_seconds": round(inference_time, 3),
        "tokens_per_second": round(tokens_per_sec, 1)
    }

    if torch.cuda.is_available():
        response["gpu_memory_used_gb"] = torch.cuda.memory_allocated() / 1024**3

    return jsonify(response)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

Test it:

```bash
python smart_device_api.py

# In another terminal:
curl http://localhost:5000/info

curl -X POST http://localhost:5000/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "GPUs accelerate machine learning by", "max_length": 60}'
```

## Challenges

### Challenge 1: Mixed Precision Training

Research and implement FP16 (half precision) inference. Compare performance and memory usage to FP32.

### Challenge 2: Batch Processing

Modify the API to:
- Accept multiple prompts in one request
- Process them as a batch on GPU
- Compare batched vs individual inference performance

### Challenge 3: GPU Utilization Monitoring

Add real-time GPU utilization tracking:
- Use `nvidia-smi` or `py3nvml` library
- Log GPU temperature, utilization %
- Alert if utilization drops below threshold

### Challenge 4: Multi-GPU Support

If you have access to multi-GPU system:
- Implement model parallelism
- Or data parallelism
- Compare performance

## Key Takeaways

1. **GPUs massively accelerate ML**: 10-100x speedup common
2. **Not all operations benefit equally**: Small operations have overhead
3. **Memory is limited**: GPU memory is precious, manage carefully
4. **Device placement matters**: Keep model and data on same device
5. **Synchronization is critical**: GPU operations are async
6. **Warmup is important**: First run is always slower
7. **Batch size affects utilization**: Larger batches use GPU better

## Infrastructure Considerations

### When to Use GPU vs CPU

**Use GPU for**:
- Training (almost always)
- Real-time inference with latency requirements
- High-throughput inference
- Large batch processing
- Large models (> 100M parameters)

**CPU is fine for**:
- Small models
- Low request volume
- Cost-sensitive deployments
- Development/testing
- Batch inference where latency doesn't matter

### GPU Cost Optimization

Cloud GPU pricing (approximate):
- **T4** (16GB): $0.35/hour
- **A10G** (24GB): $1.00/hour
- **A100** (40GB): $3.00-4.00/hour

**Optimization strategies**:
1. Use spot instances for training (60-90% discount)
2. Batch requests for inference
3. Use smaller/quantized models
4. Auto-scale based on demand
5. Use CPU for dev/test, GPU for production

## Next Steps

1. **Learn GPU optimization**:
   - Model quantization (INT8, INT4)
   - Flash Attention
   - Kernel fusion

2. **Explore distributed training**:
   - DataParallel
   - DistributedDataParallel
   - DeepSpeed, FSDP

3. **Study inference optimization**:
   - TensorRT
   - ONNX Runtime
   - vLLM, TGI

4. **Monitor production GPUs**:
   - NVML/nvidia-smi
   - DCGM (Data Center GPU Manager)
   - Grafana dashboards

## Resources

- [PyTorch CUDA Semantics](https://pytorch.org/docs/stable/notes/cuda.html)
- [NVIDIA Developer Resources](https://developer.nvidia.com/)
- [GPU Performance Guide](https://pytorch.org/tutorials/recipes/recipes/tuning_guide.html)

---

**Congratulations!** You now understand GPU fundamentals for ML infrastructure. You can make informed decisions about when and how to use GPUs in production systems.
