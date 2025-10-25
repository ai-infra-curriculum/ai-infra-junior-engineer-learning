# Exercise 04: LLM Basics - Running Your First Language Model

**Difficulty**: Beginner
**Duration**: 2-3 hours
**Prerequisites**: Python fundamentals, basic ML concepts

## Learning Objectives

By the end of this exercise, you will:

1. Understand what Large Language Models (LLMs) are
2. Run inference with a pre-trained LLM using Hugging Face Transformers
3. Understand LLM inputs (prompts) and outputs (generated text)
4. Recognize LLM resource requirements and constraints
5. Deploy a simple LLM API endpoint

## What You'll Build

A simple text generation API that:
- Loads a small pre-trained language model
- Accepts text prompts via HTTP endpoint
- Generates responses using the LLM
- Returns generated text to the user

## Background: What are LLMs?

### What is a Large Language Model?

A Large Language Model (LLM) is a type of neural network trained on massive amounts of text data to understand and generate human-like text. Examples include:
- GPT (OpenAI)
- LLaMA (Meta)
- BERT (Google)
- T5, Flan-T5 (Google)

###  Why LLMs Matter for Infrastructure Engineers

As an infrastructure engineer, you won't be training LLMs (that's expensive and specialized), but you WILL be:
- **Deploying** LLMs for applications
- **Serving** LLM inference at scale
- **Optimizing** LLM performance and cost
- **Managing** model versions and updates
- **Monitoring** LLM resource usage

### Key Concepts

**1. Prompt**: Input text given to the LLM
```
Prompt: "Explain Kubernetes in one sentence:"
```

**2. Generation**: Output text produced by the LLM
```
Generated: "Kubernetes is an open-source container orchestration platform that automates deployment, scaling, and management of containerized applications."
```

**3. Tokens**: Text units the model processes (roughly words/sub-words)
```
"Hello world" → ["Hello", " world"] → 2 tokens
```

**4. Context Window**: Maximum tokens the model can process at once
```
Small models: 512-1024 tokens
Larger models: 4096-32768+ tokens
```

## Part 1: Environment Setup

### Step 1: Install Dependencies

Create a new project directory:

```bash
mkdir llm-basics-exercise
cd llm-basics-exercise
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

Install required packages:

```bash
pip install transformers torch flask requests
```

**Package breakdown**:
- `transformers`: Hugging Face library for LLMs
- `torch`: PyTorch (backend for transformers)
- `flask`: Web framework for API
- `requests`: HTTP client for testing

### Step 2: Verify Installation

Create `test_install.py`:

```python
import torch
from transformers import pipeline

print(f"PyTorch version: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")

# Test a simple pipeline (will download model on first run)
print("Testing Transformers...")
generator = pipeline('text-generation', model='gpt2', max_length=30)
result = generator("Hello, I am", max_length=20, num_return_sequences=1)
print(result[0]['generated_text'])
print("✓ Installation successful!")
```

Run it:

```bash
python test_install.py
```

**Expected output**:
```
PyTorch version: 2.0.0
CUDA available: False
Testing Transformers...
Downloading model...
Hello, I am a software engineer based in San Francisco...
✓ Installation successful!
```

## Part 2: Understanding LLM Inference

### Step 3: Basic Text Generation

Create `basic_generation.py`:

```python
from transformers import pipeline

# Initialize the model (happens once, then cached)
print("Loading model...")
generator = pipeline(
    'text-generation',
    model='gpt2',           # Small 124M parameter model
    device=-1                # Use CPU (-1), or 0 for GPU
)
print("Model loaded!")

# Generate text
prompt = "Machine learning is"
print(f"\nPrompt: {prompt}")

results = generator(
    prompt,
    max_length=50,          # Maximum total tokens
    num_return_sequences=3, # Generate 3 variations
    temperature=0.7,        # Randomness (0=deterministic, 1=creative)
    top_k=50                # Consider top 50 tokens each step
)

# Display results
for i, result in enumerate(results, 1):
    print(f"\nGeneration {i}:")
    print(result['generated_text'])
```

Run it:

```bash
python basic_generation.py
```

**What's happening?**
1. Model loads from Hugging Face Hub (downloads first time)
2. Prompt is converted to tokens
3. Model generates tokens one by one
4. Tokens are converted back to text
5. Multiple variations created due to randomness

### Step 4: Understanding Parameters

Create `parameter_exploration.py`:

```python
from transformers import pipeline

generator = pipeline('text-generation', model='gpt2', device=-1)

prompt = "The future of AI is"

print("=" * 60)
print("Experiment 1: Temperature Effect")
print("=" * 60)

# Low temperature (deterministic)
result = generator(prompt, max_length=30, temperature=0.1, num_return_sequences=1)
print(f"\nTemperature=0.1 (deterministic):\n{result[0]['generated_text']}")

# High temperature (creative)
result = generator(prompt, max_length=30, temperature=1.5, num_return_sequences=1)
print(f"\nTemperature=1.5 (creative):\n{result[0]['generated_text']}")

print("\n" + "=" * 60)
print("Experiment 2: Max Length Effect")
print("=" * 60)

# Short generation
result = generator(prompt, max_length=20, temperature=0.7, num_return_sequences=1)
print(f"\nMax length=20:\n{result[0]['generated_text']}")

# Longer generation
result = generator(prompt, max_length=80, temperature=0.7, num_return_sequences=1)
print(f"\nMax length=80:\n{result[0]['generated_text']}")
```

**Key parameters explained**:
- **temperature**: Controls randomness (0.0-2.0)
  - Low (0.1-0.5): Predictable, focused
  - Medium (0.7-1.0): Balanced
  - High (1.0-2.0): Creative, diverse
- **max_length**: Total tokens (prompt + generation)
- **top_k**: Consider only top K probable next tokens
- **top_p**: Nucleus sampling (probability threshold)

## Part 3: Building an LLM API

### Step 5: Create Flask API

Create `llm_api.py`:

```python
from flask import Flask, request, jsonify
from transformers import pipeline
import time

app = Flask(__name__)

# Load model once at startup
print("Loading LLM model...")
generator = pipeline(
    'text-generation',
    model='gpt2',
    device=-1  # CPU
)
print("Model ready!")

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "model": "gpt2"
    })

@app.route('/generate', methods=['POST'])
def generate():
    """Text generation endpoint"""
    try:
        # Get request data
        data = request.get_json()
        prompt = data.get('prompt', '')
        max_length = data.get('max_length', 50)
        temperature = data.get('temperature', 0.7)

        # Validation
        if not prompt:
            return jsonify({"error": "Prompt is required"}), 400

        if max_length > 200:
            return jsonify({"error": "max_length cannot exceed 200"}), 400

        # Generate
        start_time = time.time()
        result = generator(
            prompt,
            max_length=max_length,
            temperature=temperature,
            num_return_sequences=1
        )
        inference_time = time.time() - start_time

        # Return response
        return jsonify({
            "prompt": prompt,
            "generated_text": result[0]['generated_text'],
            "inference_time_seconds": round(inference_time, 2),
            "parameters": {
                "max_length": max_length,
                "temperature": temperature
            }
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
```

### Step 6: Test the API

**Terminal 1** - Start the server:

```bash
python llm_api.py
```

**Terminal 2** - Test with curl:

```bash
# Health check
curl http://localhost:5000/health

# Simple generation
curl -X POST http://localhost:5000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Kubernetes is a",
    "max_length": 50,
    "temperature": 0.7
  }'

# More creative
curl -X POST http://localhost:5000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "The best way to deploy machine learning models is",
    "max_length": 100,
    "temperature": 1.0
  }'
```

Create `test_api.py` for Python testing:

```python
import requests
import json

API_URL = "http://localhost:5000"

def test_generation(prompt, max_length=50, temperature=0.7):
    response = requests.post(
        f"{API_URL}/generate",
        json={
            "prompt": prompt,
            "max_length": max_length,
            "temperature": temperature
        }
    )

    if response.status_code == 200:
        data = response.json()
        print(f"\nPrompt: {data['prompt']}")
        print(f"Generated: {data['generated_text']}")
        print(f"Inference time: {data['inference_time_seconds']}s")
    else:
        print(f"Error: {response.json()}")

if __name__ == '__main__':
    # Test cases
    test_generation("Docker containers are")
    test_generation("Machine learning infrastructure requires", max_length=80)
    test_generation("The future of AI is", temperature=1.2)
```

## Part 4: Resource Monitoring

### Step 7: Monitor Resource Usage

Create `monitor_resources.py`:

```python
import psutil
import time
from transformers import pipeline

def get_memory_usage():
    """Get current memory usage in MB"""
    process = psutil.Process()
    return process.memory_info().rss / 1024 / 1024

print("=" * 60)
print("LLM Resource Monitoring")
print("=" * 60)

# Before loading model
mem_before = get_memory_usage()
print(f"\nMemory before loading model: {mem_before:.2f} MB")

# Load model
print("Loading model...")
start_time = time.time()
generator = pipeline('text-generation', model='gpt2', device=-1)
load_time = time.time() - start_time

mem_after = get_memory_usage()
print(f"Memory after loading model: {mem_after:.2f} MB")
print(f"Model memory usage: {mem_after - mem_before:.2f} MB")
print(f"Load time: {load_time:.2f} seconds")

# Run inference
print("\nRunning inference...")
prompt = "Machine learning is"
start_time = time.time()

result = generator(prompt, max_length=50, num_return_sequences=1)

inference_time = time.time() - start_time
mem_during = get_memory_usage()

print(f"Inference time: {inference_time:.2f} seconds")
print(f"Memory during inference: {mem_during:.2f} MB")
print(f"\nGenerated text:\n{result[0]['generated_text']}")

# Resource summary
print("\n" + "=" * 60)
print("Resource Summary")
print("=" * 60)
print(f"Total memory used: {mem_during:.2f} MB")
print(f"Model load time: {load_time:.2f}s")
print(f"Inference time: {inference_time:.2f}s")
print(f"Tokens per second: ~{50/inference_time:.1f}")
```

**Expected output**:
```
LLM Resource Monitoring
============================================================

Memory before loading model: 45.23 MB
Loading model...
Memory after loading model: 550.67 MB
Model memory usage: 505.44 MB
Load time: 2.34 seconds

Running inference...
Inference time: 1.23 seconds
Memory during inference: 562.11 MB

Resource Summary
============================================================
Total memory used: 562.11 MB
Model load time: 2.34s
Inference time: 1.23s
Tokens per second: ~40.7
```

## Part 5: Comparison with Different Models

### Step 8: Compare Model Sizes

Create `compare_models.py`:

```python
import time
from transformers import pipeline
import psutil

def test_model(model_name):
    """Test a model and return metrics"""
    print(f"\n{'=' * 60}")
    print(f"Testing: {model_name}")
    print(f"{'=' * 60}")

    # Memory before
    process = psutil.Process()
    mem_before = process.memory_info().rss / 1024 / 1024

    # Load model
    start = time.time()
    try:
        generator = pipeline('text-generation', model=model_name, device=-1)
        load_time = time.time() - start

        # Memory after
        mem_after = process.memory_info().rss / 1024 / 1024
        model_memory = mem_after - mem_before

        # Run inference
        start = time.time()
        result = generator("Hello, I am", max_length=50, num_return_sequences=1)
        inference_time = time.time() - start

        print(f"✓ Model loaded successfully")
        print(f"  Load time: {load_time:.2f}s")
        print(f"  Memory usage: {model_memory:.2f} MB")
        print(f"  Inference time: {inference_time:.2f}s")
        print(f"  Output: {result[0]['generated_text'][:80]}...")

        return {
            "model": model_name,
            "load_time": load_time,
            "memory_mb": model_memory,
            "inference_time": inference_time,
            "success": True
        }
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return {"model": model_name, "success": False, "error": str(e)}

# Test different sized models
models = [
    "gpt2",              # 124M parameters (~500MB)
    "distilgpt2",        # 82M parameters (~350MB)
    "gpt2-medium",       # 355M parameters (~1.5GB) - may be slow on CPU
]

results = []
for model in models:
    results.append(test_model(model))
    time.sleep(2)  # Cool down between tests

# Summary
print(f"\n{'=' * 60}")
print("Model Comparison Summary")
print(f"{'=' * 60}")

for result in results:
    if result['success']:
        print(f"\n{result['model']}:")
        print(f"  Memory: {result['memory_mb']:.2f} MB")
        print(f"  Load: {result['load_time']:.2f}s")
        print(f"  Inference: {result['inference_time']:.2f}s")
```

## Challenges

### Challenge 1: Add Temperature Control to API

Modify `llm_api.py` to:
- Validate temperature is between 0.0 and 2.0
- Return error if invalid
- Document the parameter in the API response

### Challenge 2: Implement Streaming Responses

Research and implement token-by-token streaming instead of waiting for full completion.

Hint: Look into `TextIteratorStreamer` from transformers.

### Challenge 3: Multi-Model Support

Extend the API to:
- Support multiple models (gpt2, distilgpt2)
- Add `/models` endpoint listing available models
- Add `model` parameter to `/generate` endpoint
- Load models on-demand (lazy loading)

### Challenge 4: Add Caching

Implement a simple cache:
- If same prompt + parameters requested, return cached result
- Set cache expiration (e.g., 5 minutes)
- Add `/cache/clear` endpoint

## Infrastructure Considerations

### Resource Requirements

| Model | Parameters | Memory | CPU Inference | GPU Inference |
|-------|-----------|--------|---------------|---------------|
| distilgpt2 | 82M | ~350 MB | ~2-3 tokens/s | ~50-100 tokens/s |
| gpt2 | 124M | ~500 MB | ~1-2 tokens/s | ~30-50 tokens/s |
| gpt2-medium | 355M | ~1.5 GB | ~0.5-1 tokens/s | ~20-30 tokens/s |
| gpt2-large | 774M | ~3 GB | ~0.2-0.5 tokens/s | ~10-20 tokens/s |

### Production Deployment Checklist

- [ ] Model loaded before serving requests (not per-request)
- [ ] Health check endpoint implemented
- [ ] Request timeout configured
- [ ] Max request length validated
- [ ] Error handling for OOM (Out of Memory)
- [ ] Metrics collected (latency, throughput)
- [ ] Logging for debugging
- [ ] Rate limiting implemented
- [ ] Resource monitoring (CPU, memory, GPU)

## Key Takeaways

1. **LLMs are resource-intensive**: Even small models use hundreds of MB
2. **Inference is slow on CPU**: GPUs recommended for production
3. **Model loading is expensive**: Do it once at startup, not per-request
4. **Prompts matter**: Different prompts yield different results
5. **Parameters affect output**: Temperature, max_length, top_k/top_p
6. **Context windows are limited**: Can't process infinite text
7. **Token-based pricing**: Cloud LLM APIs charge per token

## Next Steps

After completing this exercise:

1. **Explore larger models** (requires more resources):
   - Flan-T5 (better instruction following)
   - LLaMA-2 (requires approval from Meta)
   - Mistral-7B (excellent open-source option)

2. **Learn optimization techniques**:
   - Quantization (reduce model size)
   - Batching (process multiple requests together)
   - GPU deployment
   - Model quantization (4-bit, 8-bit)

3. **Study production LLM serving**:
   - vLLM (high-throughput serving)
   - TGI (Hugging Face Text Generation Inference)
   - TensorRT-LLM (NVIDIA optimized)

4. **Explore prompt engineering**:
   - System prompts
   - Few-shot learning
   - Chain-of-thought prompting

## Resources

- [Hugging Face Transformers Docs](https://huggingface.co/docs/transformers)
- [GPT-2 Model Card](https://huggingface.co/gpt2)
- [LLM Inference Optimization](https://huggingface.co/docs/transformers/llm_tutorial)
- [vLLM Documentation](https://vllm.readthedocs.io/)

---

**Congratulations!** You've deployed your first LLM! You now understand the basics of running language models and the infrastructure requirements for serving them.
