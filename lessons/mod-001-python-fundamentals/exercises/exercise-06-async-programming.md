# Exercise 06: Async Programming for Concurrent ML Operations

## Overview

This exercise teaches you how to use Python's asyncio for concurrent operations in ML workflows. You'll learn to handle multiple tasks simultaneously, improve I/O-bound operation performance, and build efficient ML pipelines that can process data concurrently.

## Learning Objectives

By completing this exercise, you will:
- Understand async/await syntax and coroutines
- Write asynchronous functions for I/O-bound tasks
- Use asyncio.gather() for concurrent execution
- Implement async file operations and API calls
- Build async data loaders and preprocessors
- Handle errors in async code
- Understand when to use async vs threading vs multiprocessing
- Monitor and optimize async ML workflows

## Prerequisites

- Completed Exercises 01-05
- Understanding of synchronous vs asynchronous execution
- Basic knowledge of concurrent programming concepts

## Time Required

- Estimated: 90-120 minutes
- Difficulty: Intermediate to Advanced

## Part 1: Async Basics

### Step 1: Understanding Coroutines

```python
# Create a script: async_basics.py

import asyncio
import time
from typing import List

async def download_model(model_name: str) -> dict:
    """Simulate async model download"""
    print(f"Starting download: {model_name}")
    await asyncio.sleep(2)  # Simulate network delay
    print(f"Completed download: {model_name}")
    return {"name": model_name, "size": 100, "status": "downloaded"}

async def load_dataset(dataset_name: str) -> dict:
    """Simulate async dataset loading"""
    print(f"Loading dataset: {dataset_name}")
    await asyncio.sleep(1)  # Simulate I/O
    print(f"Loaded dataset: {dataset_name}")
    return {"name": dataset_name, "samples": 1000}

async def preprocess_data(data: dict) -> dict:
    """Simulate async preprocessing"""
    print(f"Preprocessing: {data['name']}")
    await asyncio.sleep(1.5)
    print(f"Preprocessed: {data['name']}")
    return {**data, "preprocessed": True}

# Sequential vs Concurrent execution
async def sequential_execution():
    """Execute tasks sequentially"""
    print("=== Sequential Execution ===")
    start = time.time()

    model = await download_model("resnet50")
    data = await load_dataset("imagenet")
    processed = await preprocess_data(data)

    elapsed = time.time() - start
    print(f"Sequential time: {elapsed:.2f}s\n")

async def concurrent_execution():
    """Execute tasks concurrently"""
    print("=== Concurrent Execution ===")
    start = time.time()

    # Run tasks concurrently
    model_task = download_model("resnet50")
    data_task = load_dataset("imagenet")

    model, data = await asyncio.gather(model_task, data_task)
    processed = await preprocess_data(data)

    elapsed = time.time() - start
    print(f"Concurrent time: {elapsed:.2f}s\n")

# Example usage
if __name__ == "__main__":
    # Run sequential
    asyncio.run(sequential_execution())

    # Run concurrent
    asyncio.run(concurrent_execution())
```

### Step 2: Async with Multiple Tasks

```python
# Create a script: async_multiple.py

import asyncio
import random
from typing import List, Dict

async def process_sample(sample_id: int) -> dict:
    """Process a single sample asynchronously"""
    # Simulate variable processing time
    delay = random.uniform(0.1, 0.5)
    await asyncio.sleep(delay)

    return {
        "sample_id": sample_id,
        "processed": True,
        "time": delay
    }

async def process_batch_async(batch: List[int]) -> List[dict]:
    """Process entire batch concurrently"""
    tasks = [process_sample(sample_id) for sample_id in batch]
    results = await asyncio.gather(*tasks)
    return results

async def download_multiple_models(model_names: List[str]) -> Dict[str, dict]:
    """Download multiple models concurrently"""
    async def download(name: str) -> tuple:
        await asyncio.sleep(random.uniform(0.5, 2.0))
        return name, {"name": name, "downloaded": True}

    tasks = [download(name) for name in model_names]
    results = await asyncio.gather(*tasks)

    return dict(results)

# Example usage
async def main():
    print("=== Processing Batch Async ===")
    batch = list(range(10))

    start = asyncio.get_event_loop().time()
    results = await process_batch_async(batch)
    elapsed = asyncio.get_event_loop().time() - start

    print(f"Processed {len(results)} samples in {elapsed:.2f}s")
    print(f"Average time per sample: {elapsed/len(results):.2f}s\n")

    print("=== Downloading Multiple Models ===")
    models = ["resnet50", "vgg16", "mobilenet", "efficientnet"]

    start = asyncio.get_event_loop().time()
    downloaded = await download_multiple_models(models)
    elapsed = asyncio.get_event_loop().time() - start

    print(f"Downloaded {len(downloaded)} models in {elapsed:.2f}s")
    print(f"Models: {list(downloaded.keys())}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Part 2: Async File Operations

### Step 3: Async File I/O

```python
# Create a script: async_file_io.py

import asyncio
import aiofiles
from pathlib import Path
from typing import List, Dict

async def read_file_async(filepath: str) -> str:
    """Read file asynchronously"""
    async with aiofiles.open(filepath, 'r') as f:
        content = await f.read()
    return content

async def write_file_async(filepath: str, content: str) -> None:
    """Write file asynchronously"""
    async with aiofiles.open(filepath, 'w') as f:
        await f.write(content)

async def read_multiple_files(filepaths: List[str]) -> Dict[str, str]:
    """Read multiple files concurrently"""
    async def read_one(path: str) -> tuple:
        content = await read_file_async(path)
        return path, content

    tasks = [read_one(path) for path in filepaths]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Filter out exceptions
    successful = {}
    for result in results:
        if isinstance(result, tuple):
            path, content = result
            successful[path] = content

    return successful

async def process_csv_async(filepath: str) -> List[Dict]:
    """Process CSV file asynchronously"""
    import csv

    async with aiofiles.open(filepath, 'r') as f:
        content = await f.read()

    # Parse CSV
    lines = content.strip().split('\n')
    if not lines:
        return []

    import io
    reader = csv.DictReader(io.StringIO(content))
    return list(reader)

async def save_predictions_async(filepath: str,
                                 predictions: List[Dict]) -> None:
    """Save predictions asynchronously"""
    import csv
    import io

    # Convert to CSV string
    if not predictions:
        return

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=predictions[0].keys())
    writer.writeheader()
    writer.writerows(predictions)

    # Write asynchronously
    async with aiofiles.open(filepath, 'w') as f:
        await f.write(output.getvalue())

# Example usage
async def main():
    # Create sample files
    print("=== Creating Sample Files ===")
    for i in range(5):
        await write_file_async(f"data_{i}.txt", f"Content of file {i}\n" * 10)
    print("✓ Created 5 sample files\n")

    # Read multiple files
    print("=== Reading Multiple Files ===")
    filepaths = [f"data_{i}.txt" for i in range(5)]

    start = asyncio.get_event_loop().time()
    contents = await read_multiple_files(filepaths)
    elapsed = asyncio.get_event_loop().time() - start

    print(f"Read {len(contents)} files in {elapsed:.2f}s")

    # Save predictions
    predictions = [
        {"sample_id": i, "prediction": 0.9, "label": 1}
        for i in range(100)
    ]

    await save_predictions_async("predictions.csv", predictions)
    print("✓ Saved predictions")

if __name__ == "__main__":
    asyncio.run(main())
```

## Part 3: Async API Calls

### Step 4: Concurrent API Requests

```python
# Create a script: async_api_calls.py

import asyncio
import aiohttp
from typing import List, Dict, Optional

async def fetch_model_metadata(session: aiohttp.ClientSession,
                               model_id: str) -> Dict:
    """Fetch model metadata from API"""
    url = f"https://api.example.com/models/{model_id}"

    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
            if response.status == 200:
                data = await response.json()
                return {"model_id": model_id, "data": data, "success": True}
            else:
                return {"model_id": model_id, "error": f"Status {response.status}", "success": False}
    except asyncio.TimeoutError:
        return {"model_id": model_id, "error": "Timeout", "success": False}
    except Exception as e:
        return {"model_id": model_id, "error": str(e), "success": False}

async def fetch_multiple_models(model_ids: List[str]) -> List[Dict]:
    """Fetch metadata for multiple models concurrently"""
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_model_metadata(session, model_id) for model_id in model_ids]
        results = await asyncio.gather(*tasks)
        return results

async def batch_inference_api(samples: List[Dict],
                              api_url: str,
                              batch_size: int = 10) -> List[Dict]:
    """Send samples to inference API in batches"""
    async def send_batch(session: aiohttp.ClientSession, batch: List[Dict]) -> Dict:
        try:
            async with session.post(api_url, json={"samples": batch}) as response:
                return await response.json()
        except Exception as e:
            return {"error": str(e), "success": False}

    # Split into batches
    batches = [samples[i:i+batch_size] for i in range(0, len(samples), batch_size)]

    async with aiohttp.ClientSession() as session:
        tasks = [send_batch(session, batch) for batch in batches]
        results = await asyncio.gather(*tasks)
        return results

# Example usage (with mock server)
async def main():
    print("=== Async API Calls (Mock) ===")

    # Simulate API calls
    model_ids = [f"model_{i}" for i in range(10)]

    print(f"Fetching metadata for {len(model_ids)} models...")

    # Note: This would fail with real API, but demonstrates the pattern
    # Uncomment when you have a real API endpoint
    # results = await fetch_multiple_models(model_ids)
    # successful = [r for r in results if r.get("success")]
    # print(f"Successfully fetched: {len(successful)}/{len(model_ids)}")

    print("✓ API call pattern demonstrated")

if __name__ == "__main__":
    asyncio.run(main())
```

## Part 4: Async Data Pipeline

### Step 5: Building an Async ML Pipeline

```python
# Create a script: async_ml_pipeline.py

import asyncio
from typing import List, Dict, Optional
from dataclasses import dataclass
import time

@dataclass
class Sample:
    """Data sample"""
    id: int
    data: List[float]
    processed: bool = False
    predicted: bool = False

class AsyncMLPipeline:
    """Asynchronous ML pipeline"""

    def __init__(self, batch_size: int = 32):
        self.batch_size = batch_size

    async def load_data(self, num_samples: int) -> List[Sample]:
        """Load data asynchronously"""
        print(f"Loading {num_samples} samples...")
        await asyncio.sleep(0.5)  # Simulate I/O

        samples = [
            Sample(id=i, data=[float(i) * 0.1] * 10)
            for i in range(num_samples)
        ]

        print(f"✓ Loaded {len(samples)} samples")
        return samples

    async def preprocess_sample(self, sample: Sample) -> Sample:
        """Preprocess single sample"""
        await asyncio.sleep(0.01)  # Simulate processing
        sample.processed = True
        return sample

    async def preprocess_batch(self, samples: List[Sample]) -> List[Sample]:
        """Preprocess batch of samples concurrently"""
        tasks = [self.preprocess_sample(s) for s in samples]
        return await asyncio.gather(*tasks)

    async def predict_sample(self, sample: Sample) -> Sample:
        """Run inference on single sample"""
        await asyncio.sleep(0.02)  # Simulate inference
        sample.predicted = True
        return sample

    async def predict_batch(self, samples: List[Sample]) -> List[Sample]:
        """Run inference on batch concurrently"""
        tasks = [self.predict_sample(s) for s in samples]
        return await asyncio.gather(*tasks)

    async def run_pipeline(self, num_samples: int) -> Dict[str, any]:
        """Run complete async pipeline"""
        start_time = time.time()

        # Load data
        samples = await self.load_data(num_samples)

        # Preprocess in batches
        print(f"Preprocessing {len(samples)} samples...")
        batches = [samples[i:i+self.batch_size]
                  for i in range(0, len(samples), self.batch_size)]

        preprocessed = []
        for batch in batches:
            batch_result = await self.preprocess_batch(batch)
            preprocessed.extend(batch_result)

        print(f"✓ Preprocessed {len(preprocessed)} samples")

        # Predict in batches
        print(f"Running inference on {len(preprocessed)} samples...")
        predicted = []
        for batch in [preprocessed[i:i+self.batch_size]
                     for i in range(0, len(preprocessed), self.batch_size)]:
            batch_result = await self.predict_batch(batch)
            predicted.extend(batch_result)

        print(f"✓ Predicted {len(predicted)} samples")

        elapsed = time.time() - start_time

        return {
            "total_samples": len(predicted),
            "time_elapsed": elapsed,
            "samples_per_second": len(predicted) / elapsed
        }

# Example usage
async def main():
    print("=== Async ML Pipeline ===\n")

    pipeline = AsyncMLPipeline(batch_size=32)
    results = await pipeline.run_pipeline(num_samples=200)

    print(f"\n=== Results ===")
    print(f"Total samples: {results['total_samples']}")
    print(f"Time elapsed: {results['time_elapsed']:.2f}s")
    print(f"Throughput: {results['samples_per_second']:.1f} samples/sec")

if __name__ == "__main__":
    asyncio.run(main())
```

## Part 5: Error Handling in Async Code

### Step 6: Async Exception Handling

```python
# Create a script: async_error_handling.py

import asyncio
from typing import List, Dict, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def risky_operation(task_id: int, failure_rate: float = 0.3) -> Dict:
    """Operation that might fail"""
    import random

    await asyncio.sleep(0.1)

    if random.random() < failure_rate:
        raise ValueError(f"Task {task_id} failed")

    return {"task_id": task_id, "result": "success"}

async def safe_risky_operation(task_id: int) -> Dict:
    """Wrap risky operation with error handling"""
    try:
        result = await risky_operation(task_id)
        return result
    except ValueError as e:
        logger.warning(f"Task {task_id} failed: {e}")
        return {"task_id": task_id, "result": "failed", "error": str(e)}
    except Exception as e:
        logger.error(f"Unexpected error in task {task_id}: {e}")
        return {"task_id": task_id, "result": "error", "error": str(e)}

async def run_tasks_with_error_handling(num_tasks: int) -> Dict[str, int]:
    """Run multiple tasks with error handling"""
    tasks = [safe_risky_operation(i) for i in range(num_tasks)]
    results = await asyncio.gather(*tasks)

    # Count outcomes
    successful = sum(1 for r in results if r["result"] == "success")
    failed = sum(1 for r in results if r["result"] == "failed")
    errors = sum(1 for r in results if r["result"] == "error")

    return {
        "total": num_tasks,
        "successful": successful,
        "failed": failed,
        "errors": errors
    }

async def retry_async(func, *args, max_retries: int = 3, **kwargs):
    """Retry async function on failure"""
    for attempt in range(max_retries):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            logger.warning(f"Attempt {attempt + 1} failed, retrying...")
            await asyncio.sleep(0.5 * (attempt + 1))

# Example usage
async def main():
    print("=== Async Error Handling ===\n")

    stats = await run_tasks_with_error_handling(20)

    print(f"Results:")
    print(f"  Total: {stats['total']}")
    print(f"  Successful: {stats['successful']}")
    print(f"  Failed: {stats['failed']}")
    print(f"  Errors: {stats['errors']}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Part 6: When to Use Async

### Step 7: Async vs Threading vs Multiprocessing

```python
# Create a script: concurrency_comparison.py

import asyncio
import time
import threading
import multiprocessing
from typing import List

def cpu_bound_task(n: int) -> int:
    """CPU-intensive task"""
    result = sum(i * i for i in range(n))
    return result

def io_bound_task(duration: float) -> str:
    """I/O-bound task (simulated)"""
    time.sleep(duration)
    return "completed"

async def io_bound_task_async(duration: float) -> str:
    """Async I/O-bound task"""
    await asyncio.sleep(duration)
    return "completed"

# Synchronous baseline
def sync_io_tasks(num_tasks: int):
    """Run I/O tasks synchronously"""
    start = time.time()

    for _ in range(num_tasks):
        io_bound_task(0.1)

    return time.time() - start

# Async version
async def async_io_tasks(num_tasks: int):
    """Run I/O tasks asynchronously"""
    start = time.time()

    tasks = [io_bound_task_async(0.1) for _ in range(num_tasks)]
    await asyncio.gather(*tasks)

    return time.time() - start

# Threading version
def threaded_io_tasks(num_tasks: int):
    """Run I/O tasks with threading"""
    start = time.time()

    threads = []
    for _ in range(num_tasks):
        thread = threading.Thread(target=io_bound_task, args=(0.1,))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    return time.time() - start

def compare_approaches():
    """Compare different concurrency approaches"""
    num_tasks = 10

    print("=== I/O-Bound Task Comparison ===")
    print(f"Number of tasks: {num_tasks}\n")

    # Synchronous
    sync_time = sync_io_tasks(num_tasks)
    print(f"Synchronous: {sync_time:.2f}s")

    # Async
    async_time = asyncio.run(async_io_tasks(num_tasks))
    print(f"Async: {async_time:.2f}s")

    # Threading
    threaded_time = threaded_io_tasks(num_tasks)
    print(f"Threading: {threaded_time:.2f}s\n")

    print(f"Async speedup: {sync_time/async_time:.1f}x")
    print(f"Threading speedup: {sync_time/threaded_time:.1f}x")

if __name__ == "__main__":
    compare_approaches()

    print("\n=== Guidelines ===")
    print("Use Async for:")
    print("  - I/O-bound tasks (file, network, database)")
    print("  - Many concurrent operations")
    print("  - API calls and web scraping")
    print("\nUse Threading for:")
    print("  - I/O-bound tasks in sync code")
    print("  - Moderate concurrency")
    print("\nUse Multiprocessing for:")
    print("  - CPU-bound tasks")
    print("  - Parallel computation")
    print("  - Training multiple models")
```

## Validation

```python
# Create a script: validate_async.py

async def validate_async_basics():
    """Validate async basics"""
    async def test_func():
        await asyncio.sleep(0.1)
        return "success"

    result = await test_func()
    assert result == "success", "Async function failed"
    print("✓ Async basics work")

async def validate_gather():
    """Validate asyncio.gather()"""
    async def task(n):
        await asyncio.sleep(0.1)
        return n * 2

    results = await asyncio.gather(task(1), task(2), task(3))
    assert results == [2, 4, 6], "Gather failed"
    print("✓ asyncio.gather() works")

async def validate_error_handling():
    """Validate async error handling"""
    async def failing_task():
        raise ValueError("Test error")

    try:
        await failing_task()
        assert False, "Should have raised error"
    except ValueError:
        print("✓ Async error handling works")

async def main():
    print("=== Async Validation ===\n")
    await validate_async_basics()
    await validate_gather()
    await validate_error_handling()
    print("\n✓ All validations passed!")

if __name__ == "__main__":
    asyncio.run(main())
```

## Reflection Questions

1. When should you use async vs threading?
2. How does asyncio improve I/O-bound task performance?
3. What are the limitations of async programming?
4. How do you debug async code?
5. When is multiprocessing better than async?
6. How do you handle errors in concurrent tasks?
7. What monitoring is needed for async ML pipelines?

## Next Steps

- **Exercise 07**: Testing async code with pytest-asyncio
- **Module 002**: Linux Essentials
- **Project 01**: Build a complete async ML pipeline

## Additional Resources

- Asyncio Documentation: https://docs.python.org/3/library/asyncio.html
- Real Python Async Guide: https://realpython.com/async-io-python/
- aiohttp: https://docs.aiohttp.org/
- aiofiles: https://github.com/Tinche/aiofiles

---

**Congratulations!** You've mastered async programming for concurrent ML operations. You can now build efficient, high-performance ML pipelines that handle multiple tasks simultaneously.
