# Lecture 04: Asynchronous Programming in Python

## Table of Contents
1. [Introduction](#introduction)
2. [Understanding Async/Await](#understanding-asyncawait)
3. [Running Multiple Tasks Concurrently](#running-multiple-tasks-concurrently)
4. [Async with HTTP Requests](#async-with-http-requests)
5. [Error Handling in Async Code](#error-handling-in-async-code)
6. [Async Context Managers](#async-context-managers)
7. [Async Generators](#async-generators)
8. [Common Async Patterns for AI Infrastructure](#common-async-patterns-for-ai-infrastructure)
9. [Summary](#summary)

---

## Introduction

This lecture covers asynchronous programming in Python, a critical skill for building efficient AI infrastructure systems that handle multiple concurrent operations.

### Why Asynchronous Programming Matters

**In AI Infrastructure**:
- **Handle Multiple API Requests**: Serve predictions for multiple clients simultaneously
- **Concurrent Model Operations**: Check health of multiple model endpoints at once
- **Efficient I/O Operations**: Download datasets or upload models without blocking
- **Scalable Services**: Build systems that can handle high throughput

**Asynchronous programming** allows you to write concurrent code that can handle multiple operations without blocking. This is crucial for I/O-bound operations like:
- Making HTTP API calls
- Reading/writing to databases
- File I/O operations
- Network communication

### Learning Objectives

By the end of this lecture, you will:
- Understand when and why to use async programming
- Write async functions using `async`/`await` syntax
- Run multiple tasks concurrently with `asyncio.gather()`
- Handle errors in async code
- Implement async context managers and generators
- Apply async patterns to AI infrastructure scenarios

This lecture prepares you for **Exercise 06: Async Programming**, where you'll build a concurrent model monitoring system.

---

## Understanding Async/Await

### When to Use Async

✅ **Use Async For**:
- I/O-bound operations (network calls, file operations, database queries)
- Handling many concurrent connections (web servers, API gateways)
- Long-running operations that wait on external systems

❌ **Don't Use Async For**:
- CPU-bound operations (use multiprocessing instead)
- Simple scripts without concurrent operations
- Code that doesn't involve waiting

### Basic Async Syntax

```python
import asyncio

# Define an async function with 'async def'
async def fetch_data(url: str) -> dict:
    """Async function to fetch data from URL"""
    await asyncio.sleep(1)  # Simulate network delay
    return {"url": url, "data": "sample data"}

# Run async function
async def main():
    result = await fetch_data("https://api.example.com/data")
    print(result)

# Execute the async code
if __name__ == "__main__":
    asyncio.run(main())
```

**Key Concepts**:
- `async def`: Defines a coroutine function
- `await`: Pauses execution until the awaited operation completes
- `asyncio.run()`: Entry point for running async code

---

## Running Multiple Tasks Concurrently

The power of async is running multiple operations at once:

```python
import asyncio
from typing import List

async def fetch_model_metadata(model_id: str) -> dict:
    """Fetch metadata for a single model"""
    await asyncio.sleep(0.5)  # Simulate API call
    return {
        "model_id": model_id,
        "version": "1.0",
        "accuracy": 0.95
    }

async def fetch_all_models(model_ids: List[str]) -> List[dict]:
    """Fetch metadata for multiple models concurrently"""
    # Create tasks for all models
    tasks = [fetch_model_metadata(mid) for mid in model_ids]

    # Run all tasks concurrently
    results = await asyncio.gather(*tasks)
    return results

async def main():
    model_ids = [f"model-{i}" for i in range(5)]

    # Sequential execution (slow)
    print("Sequential execution:")
    import time
    start = time.time()
    results = []
    for mid in model_ids:
        result = await fetch_model_metadata(mid)
        results.append(result)
    print(f"Time: {time.time() - start:.2f}s")  # ~2.5 seconds

    # Concurrent execution (fast)
    print("\nConcurrent execution:")
    start = time.time()
    results = await fetch_all_models(model_ids)
    print(f"Time: {time.time() - start:.2f}s")  # ~0.5 seconds

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Async with HTTP Requests

Using `httpx` for async HTTP calls:

```python
import asyncio
import httpx
from typing import List, Dict

async def check_model_health(endpoint: str) -> Dict[str, str]:
    """Check if a model serving endpoint is healthy"""
    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            response = await client.get(f"{endpoint}/health")
            return {
                "endpoint": endpoint,
                "status": "healthy" if response.status_code == 200 else "unhealthy",
                "response_time": response.elapsed.total_seconds()
            }
        except Exception as e:
            return {
                "endpoint": endpoint,
                "status": "error",
                "error": str(e)
            }

async def monitor_models(endpoints: List[str]) -> List[Dict]:
    """Monitor multiple model endpoints concurrently"""
    tasks = [check_model_health(ep) for ep in endpoints]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return results

# Usage
async def main():
    endpoints = [
        "http://model1.example.com",
        "http://model2.example.com",
        "http://model3.example.com"
    ]

    health_status = await monitor_models(endpoints)
    for status in health_status:
        print(f"{status['endpoint']}: {status['status']}")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Error Handling in Async Code

```python
import asyncio
from typing import Optional

async def fetch_with_retry(url: str, max_retries: int = 3) -> Optional[dict]:
    """Fetch data with retry logic"""
    for attempt in range(max_retries):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=10.0)
                response.raise_for_status()
                return response.json()
        except httpx.TimeoutException:
            print(f"Timeout on attempt {attempt + 1}")
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
        except httpx.HTTPError as e:
            print(f"HTTP error: {e}")
            return None

    return None  # All retries failed
```

---

## Async Context Managers

```python
import asyncio
from typing import AsyncGenerator

class AsyncModelClient:
    """Async client for ML model serving"""

    async def __aenter__(self):
        """Setup when entering context"""
        self.client = httpx.AsyncClient()
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Cleanup when exiting context"""
        await self.disconnect()
        await self.client.aclose()

    async def connect(self):
        """Establish connection"""
        await asyncio.sleep(0.1)  # Simulate connection
        print("Connected to model server")

    async def disconnect(self):
        """Close connection"""
        await asyncio.sleep(0.1)
        print("Disconnected from model server")

    async def predict(self, data: dict) -> dict:
        """Make prediction"""
        response = await self.client.post(
            "http://model.example.com/predict",
            json=data
        )
        return response.json()

# Usage
async def main():
    async with AsyncModelClient() as client:
        result = await client.predict({"features": [1, 2, 3]})
        print(result)
```

---

## Async Generators

```python
import asyncio
from typing import AsyncGenerator

async def stream_training_logs(job_id: str) -> AsyncGenerator[str, None]:
    """Stream training logs asynchronously"""
    for i in range(10):
        await asyncio.sleep(0.5)
        yield f"[{job_id}] Epoch {i+1}/10 - loss: {1.0/(i+1):.4f}"

async def monitor_training():
    """Monitor training job logs"""
    async for log_line in stream_training_logs("job-123"):
        print(log_line)

if __name__ == "__main__":
    asyncio.run(monitor_training())
```

---

## Common Async Patterns for AI Infrastructure

### Pattern 1: Concurrent Model Deployment

```python
import asyncio
from typing import List

async def deploy_model(model_id: str, environment: str) -> dict:
    """Deploy a single model"""
    print(f"Deploying {model_id} to {environment}...")
    await asyncio.sleep(2)  # Simulate deployment time
    return {
        "model_id": model_id,
        "environment": environment,
        "status": "deployed"
    }

async def deploy_multiple_models(
    models: List[str],
    environment: str
) -> List[dict]:
    """Deploy multiple models concurrently"""
    tasks = [deploy_model(mid, environment) for mid in models]
    return await asyncio.gather(*tasks)
```

### Pattern 2: Async Data Pipeline

```python
import asyncio
from typing import List, Dict

async def fetch_training_data(source: str) -> List[Dict]:
    """Fetch training data from source"""
    await asyncio.sleep(1)
    return [{"id": i, "features": [i]*10} for i in range(100)]

async def preprocess_batch(batch: List[Dict]) -> List[Dict]:
    """Preprocess a batch of data"""
    await asyncio.sleep(0.5)
    return [{"id": item["id"], "processed": True} for item in batch]

async def save_to_storage(data: List[Dict]) -> None:
    """Save processed data to storage"""
    await asyncio.sleep(0.3)
    print(f"Saved {len(data)} records")

async def data_pipeline():
    """Execute data pipeline with async operations"""
    # Fetch data
    raw_data = await fetch_training_data("s3://bucket/data")

    # Preprocess in batches concurrently
    batch_size = 25
    batches = [raw_data[i:i+batch_size] for i in range(0, len(raw_data), batch_size)]
    processed_batches = await asyncio.gather(*[preprocess_batch(b) for b in batches])

    # Flatten results
    processed_data = [item for batch in processed_batches for item in batch]

    # Save
    await save_to_storage(processed_data)
```

---

## Summary

### Key Takeaways

#### Async Programming
- Use `async`/`await` for I/O-bound concurrent operations
- `asyncio.gather()` runs multiple tasks concurrently
- Async is essential for efficient API calls and database queries
- Always use `asyncio.run()` as the entry point
- Handle errors with try/except in async functions
- Use `httpx` for async HTTP requests
- Implement async context managers for resource management
- Use async generators for streaming data

### Best Practices for AI Infrastructure

1. **Write Async Code For**:
   - Model serving APIs (multiple concurrent requests)
   - Batch inference with multiple model calls
   - Health check monitoring across services
   - Data pipeline operations
   - Concurrent model deployments

2. **Performance Considerations**:
   - Async excels at I/O-bound operations
   - Use multiprocessing for CPU-bound tasks
   - Monitor concurrency limits to avoid overwhelming systems
   - Implement proper timeout and retry logic

3. **Error Handling**:
   - Always wrap async operations in try/except
   - Use `return_exceptions=True` in `asyncio.gather()` to handle partial failures
   - Implement exponential backoff for retries
   - Log errors with proper context

### Next Steps

- **Complete Exercise 06: Async Programming** - Build a concurrent model monitoring system
- **Continue to Lecture 05: Testing and Code Quality** - Learn to test async code and maintain quality standards
- Practice async patterns with real HTTP APIs
- Experiment with `asyncio` debugging tools

### Additional Resources

- [asyncio Documentation](https://docs.python.org/3/library/asyncio.html)
- [Real Python: Async IO](https://realpython.com/async-io-python/)
- [HTTPX Documentation](https://www.python-httpx.org/)
- [AsyncIO Cheat Sheet](https://github.com/crazyguitar/pysheeet/blob/master/docs/notes/python-asyncio.rst)

---

**Lecture Version**: 1.0
**Last Updated**: October 2025
**Estimated Duration**: 6-8 hours

**Ready to continue?** Move on to `lecture-notes/05-testing-code-quality.md`
