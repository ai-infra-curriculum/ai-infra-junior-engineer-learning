# Exercise 04: Background Tasks and Async Operations

## Overview

Learn to implement asynchronous operations and background tasks in FastAPI to handle long-running ML operations efficiently. Understand how to process tasks without blocking API responses and implement job queues for model training and batch processing.

**Difficulty:** Intermediate-Advanced
**Estimated Time:** 2-3 hours
**Prerequisites:**
- Exercise 01-03 completed
- Lecture 02: FastAPI Framework
- Basic understanding of async/await in Python

## Learning Objectives

By completing this exercise, you will:
- Implement FastAPI BackgroundTasks for simple async operations
- Create long-running job tracking system
- Use async/await for I/O-bound operations
- Implement task queues for ML operations
- Handle job status polling
- Stream results with Server-Sent Events (SSE)

## Scenario

Your ML API needs to handle operations that take time:
- Model training (minutes to hours)
- Large batch predictions
- Data preprocessing pipelines
- Model evaluation

Users shouldn't wait for responses. Instead, submit jobs and poll for status.

## Project Setup

### Install Dependencies

```bash
pip install aiofiles
pip install sse-starlette  # For Server-Sent Events
```

## Part 1: Simple Background Tasks

**File: app/background.py**

```python
from fastapi import BackgroundTasks
import time
import logging

logger = logging.getLogger(__name__)

def log_prediction(user_id: str, text: str, prediction: str):
    """Log prediction to file (runs in background)"""
    # TODO: Open log file in append mode
    # TODO: Write log entry with timestamp, user, input, prediction
    # TODO: Simulate some processing time
    pass

def send_notification(email: str, message: str):
    """Send email notification (simulated)"""
    # TODO: Simulate sending email
    # TODO: Log notification sent
    # time.sleep(1)  # Simulate email sending
    pass

def update_user_stats(user_id: str):
    """Update user request statistics"""
    # TODO: Increment user's request count
    # TODO: Update last_request_time
    pass
```

**File: app/main.py** (update)

```python
from fastapi import BackgroundTasks

@app.post("/api/v1/predict")
async def predict(
    input_data: PredictionInput,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user)
):
    """Prediction with background logging"""

    # Make prediction (fast)
    result = ml_service.predict(input_data.text)

    # TODO: Add background tasks (don't block response)
    # background_tasks.add_task(log_prediction, current_user.username, input_data.text, result["prediction"])
    # background_tasks.add_task(update_user_stats, current_user.username)

    # Return immediately
    return result
```

## Part 2: Job Queue System

**File: app/jobs.py**

```python
from enum import Enum
from typing import Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel
import uuid
import asyncio

class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class Job(BaseModel):
    job_id: str
    job_type: str
    status: JobStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    progress: float = 0.0  # 0-100
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    user_id: str

class JobQueue:
    """Simple in-memory job queue"""

    def __init__(self):
        self.jobs: Dict[str, Job] = {}
        self.active_jobs = set()

    def create_job(self, job_type: str, user_id: str) -> str:
        """Create a new job"""
        # TODO: Generate job_id using uuid
        # TODO: Create Job object with status=PENDING
        # TODO: Store in self.jobs
        # TODO: Return job_id
        pass

    def get_job(self, job_id: str) -> Optional[Job]:
        """Get job by ID"""
        # TODO: Return job from self.jobs if exists
        pass

    def update_job_status(self, job_id: str, status: JobStatus, **kwargs):
        """Update job status and other fields"""
        # TODO: Get job
        # TODO: Update status
        # TODO: Update other fields (started_at, completed_at, etc.)
        # TODO: If completed/failed, remove from active_jobs
        pass

    def update_progress(self, job_id: str, progress: float):
        """Update job progress"""
        # TODO: Get job
        # TODO: Update progress (clamp to 0-100)
        pass

    def set_result(self, job_id: str, result: Dict[str, Any]):
        """Set job result"""
        # TODO: Get job
        # TODO: Set result
        # TODO: Set status to COMPLETED
        # TODO: Set completed_at
        pass

    def set_error(self, job_id: str, error: str):
        """Set job error"""
        # TODO: Get job
        # TODO: Set error
        # TODO: Set status to FAILED
        # TODO: Set completed_at
        pass

    def get_user_jobs(self, user_id: str) -> list[Job]:
        """Get all jobs for a user"""
        # TODO: Filter jobs by user_id
        # TODO: Return sorted by created_at (newest first)
        pass

# Global job queue
job_queue = JobQueue()
```

## Part 3: Long-Running Task: Batch Prediction

**File: app/tasks.py**

```python
import asyncio
from app.jobs import job_queue, JobStatus
from app.ml_service import ml_service
import logging

logger = logging.getLogger(__name__)

async def process_batch_prediction(
    job_id: str,
    texts: list[str],
    user_id: str
):
    """Process batch prediction as background job"""
    try:
        # TODO: Update job status to RUNNING
        # job_queue.update_job_status(job_id, JobStatus.RUNNING, started_at=datetime.utcnow())

        # TODO: Process in batches of 10
        batch_size = 10
        results = []

        for i in range(0, len(texts), batch_size):
            # TODO: Get batch
            batch = texts[i:i+batch_size]

            # TODO: Process batch (simulate with sleep)
            # await asyncio.sleep(1)  # Simulate processing
            batch_results = [ml_service.predict(text) for text in batch]
            results.extend(batch_results)

            # TODO: Update progress
            progress = ((i + len(batch)) / len(texts)) * 100
            job_queue.update_progress(job_id, progress)

        # TODO: Set result
        job_queue.set_result(job_id, {
            "predictions": results,
            "total": len(results)
        })

        logger.info(f"Batch job {job_id} completed successfully")

    except Exception as e:
        # TODO: Set error
        logger.error(f"Batch job {job_id} failed: {e}")
        job_queue.set_error(job_id, str(e))

async def process_model_training(
    job_id: str,
    training_data: dict,
    user_id: str
):
    """Simulate model training as background job"""
    try:
        # TODO: Update status to RUNNING
        job_queue.update_job_status(job_id, JobStatus.RUNNING, started_at=datetime.utcnow())

        # TODO: Simulate training epochs
        epochs = 10
        for epoch in range(epochs):
            # Simulate epoch processing
            await asyncio.sleep(2)

            # Update progress
            progress = ((epoch + 1) / epochs) * 100
            job_queue.update_progress(job_id, progress)

        # TODO: Set result
        job_queue.set_result(job_id, {
            "model_id": f"model_{job_id[:8]}",
            "accuracy": 0.95,
            "epochs": epochs
        })

    except Exception as e:
        job_queue.set_error(job_id, str(e))
```

## Part 4: Job API Endpoints

**File: app/main.py** (update)

```python
from app.jobs import job_queue, Job, JobStatus
from app.tasks import process_batch_prediction, process_model_training
import asyncio

@app.post("/api/v1/jobs/batch-predict", response_model=dict)
async def create_batch_prediction_job(
    texts: list[str],
    current_user: User = Depends(get_current_active_user)
):
    """Create a batch prediction job"""

    # TODO: Validate input (max 1000 texts)
    if len(texts) > 1000:
        raise HTTPException(status_code=400, detail="Maximum 1000 texts allowed")

    # TODO: Create job
    job_id = job_queue.create_job("batch_predict", current_user.username)

    # TODO: Start background task
    asyncio.create_task(process_batch_prediction(job_id, texts, current_user.username))

    # TODO: Return job info
    return {
        "job_id": job_id,
        "status": "pending",
        "message": "Job created successfully",
        "poll_url": f"/api/v1/jobs/{job_id}"
    }

@app.post("/api/v1/jobs/train-model", response_model=dict)
async def create_training_job(
    training_data: dict,
    current_user: User = Depends(get_current_active_user)
):
    """Create a model training job"""

    # TODO: Create job
    job_id = job_queue.create_job("train_model", current_user.username)

    # TODO: Start background task
    asyncio.create_task(process_model_training(job_id, training_data, current_user.username))

    # TODO: Return job info
    return {
        "job_id": job_id,
        "status": "pending",
        "message": "Training job created",
        "poll_url": f"/api/v1/jobs/{job_id}"
    }

@app.get("/api/v1/jobs/{job_id}", response_model=Job)
async def get_job_status(
    job_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get job status"""

    # TODO: Get job from queue
    job = job_queue.get_job(job_id)

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # TODO: Verify job belongs to user
    if job.user_id != current_user.username:
        raise HTTPException(status_code=403, detail="Not authorized")

    return job

@app.get("/api/v1/jobs", response_model=list[Job])
async def list_user_jobs(
    current_user: User = Depends(get_current_active_user)
):
    """List all jobs for current user"""
    # TODO: Get user's jobs
    jobs = job_queue.get_user_jobs(current_user.username)
    return jobs

@app.delete("/api/v1/jobs/{job_id}")
async def cancel_job(
    job_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Cancel a job"""

    job = job_queue.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.user_id != current_user.username:
        raise HTTPException(status_code=403, detail="Not authorized")

    # TODO: Only allow cancelling pending/running jobs
    if job.status in [JobStatus.PENDING, JobStatus.RUNNING]:
        job_queue.update_job_status(job_id, JobStatus.CANCELLED)
        return {"message": "Job cancelled"}
    else:
        raise HTTPException(status_code=400, detail="Cannot cancel completed job")
```

## Part 5: Server-Sent Events for Real-Time Updates

**File: app/streaming.py**

```python
from sse_starlette.sse import EventSourceResponse
from fastapi import Request
import asyncio
import json

async def job_status_stream(job_id: str, request: Request):
    """Stream job status updates using SSE"""

    async def event_generator():
        last_status = None
        last_progress = None

        while True:
            # Check if client disconnected
            if await request.is_disconnected():
                break

            # Get current job status
            job = job_queue.get_job(job_id)
            if not job:
                yield {
                    "event": "error",
                    "data": json.dumps({"error": "Job not found"})
                }
                break

            # Send update if status or progress changed
            if job.status != last_status or job.progress != last_progress:
                yield {
                    "event": "update",
                    "data": json.dumps({
                        "status": job.status,
                        "progress": job.progress,
                        "job_id": job_id
                    })
                }
                last_status = job.status
                last_progress = job.progress

            # Stop streaming if job is finished
            if job.status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED]:
                yield {
                    "event": "complete",
                    "data": json.dumps({
                        "status": job.status,
                        "result": job.result,
                        "error": job.error
                    })
                }
                break

            # Wait before next update
            await asyncio.sleep(1)

    return EventSourceResponse(event_generator())
```

**Add endpoint in main.py:**

```python
from app.streaming import job_status_stream

@app.get("/api/v1/jobs/{job_id}/stream")
async def stream_job_status(
    job_id: str,
    request: Request,
    current_user: User = Depends(get_current_active_user)
):
    """Stream job status updates via SSE"""

    job = job_queue.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.user_id != current_user.username:
        raise HTTPException(status_code=403, detail="Not authorized")

    return await job_status_stream(job_id, request)
```

## Part 6: Async File Operations

**File: app/file_ops.py**

```python
import aiofiles
import asyncio
from typing import List

async def save_results_async(filename: str, data: dict):
    """Save results to file asynchronously"""
    # TODO: Use aiofiles to write JSON
    # async with aiofiles.open(filename, 'w') as f:
    #     await f.write(json.dumps(data, indent=2))
    pass

async def read_large_file_async(filename: str) -> List[str]:
    """Read large file line by line asynchronously"""
    lines = []
    # TODO: Use aiofiles to read file
    # async with aiofiles.open(filename, 'r') as f:
    #     async for line in f:
    #         lines.append(line.strip())
    return lines

async def process_file_batch(filenames: List[str]) -> List[dict]:
    """Process multiple files concurrently"""
    # TODO: Create tasks for each file
    # tasks = [read_large_file_async(f) for f in filenames]

    # TODO: Gather results
    # results = await asyncio.gather(*tasks)

    return results
```

## Part 7: Testing Async Operations

**File: tests/test_jobs.py**

```python
from fastapi.testclient import TestClient
from app.main import app
import time

client = TestClient(app)

def get_token():
    """Helper to get auth token"""
    response = client.post("/token", data={"username": "alice", "password": "secret123"})
    return response.json()["access_token"]

def test_create_batch_job():
    """Test creating batch prediction job"""
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}

    # TODO: Create batch job
    response = client.post(
        "/api/v1/jobs/batch-predict",
        json={"texts": ["test1", "test2", "test3"]},
        headers=headers
    )

    # TODO: Assert status 200
    # TODO: Assert job_id in response
    # TODO: Assert poll_url in response
    pass

def test_get_job_status():
    """Test getting job status"""
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}

    # TODO: Create job
    create_response = client.post(
        "/api/v1/jobs/batch-predict",
        json={"texts": ["test"]},
        headers=headers
    )
    job_id = create_response.json()["job_id"]

    # TODO: Get job status
    response = client.get(f"/api/v1/jobs/{job_id}", headers=headers)

    # TODO: Assert status 200
    # TODO: Assert job_id matches
    # TODO: Assert status is pending or running
    pass

def test_job_completion():
    """Test job completes successfully"""
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}

    # TODO: Create job with small batch
    response = client.post(
        "/api/v1/jobs/batch-predict",
        json={"texts": ["test1", "test2"]},
        headers=headers
    )
    job_id = response.json()["job_id"]

    # TODO: Poll until completion (max 30 seconds)
    max_attempts = 30
    for _ in range(max_attempts):
        status_response = client.get(f"/api/v1/jobs/{job_id}", headers=headers)
        job = status_response.json()

        if job["status"] == "completed":
            # TODO: Assert result is present
            # TODO: Assert predictions array has 2 items
            break

        time.sleep(1)
    else:
        assert False, "Job did not complete in time"

def test_list_user_jobs():
    """Test listing user's jobs"""
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}

    # TODO: Create 2 jobs
    for i in range(2):
        client.post(
            "/api/v1/jobs/batch-predict",
            json={"texts": [f"test{i}"]},
            headers=headers
        )

    # TODO: List jobs
    response = client.get("/api/v1/jobs", headers=headers)

    # TODO: Assert status 200
    # TODO: Assert at least 2 jobs returned
    pass

def test_cancel_job():
    """Test cancelling a job"""
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}

    # TODO: Create long-running job
    response = client.post(
        "/api/v1/jobs/train-model",
        json={"data": "test"},
        headers=headers
    )
    job_id = response.json()["job_id"]

    # TODO: Cancel job
    cancel_response = client.delete(f"/api/v1/jobs/{job_id}", headers=headers)

    # TODO: Assert status 200
    # TODO: Verify job status is cancelled
    pass
```

## Challenges and Extensions

### Challenge 1: Job Persistence

Store jobs in database instead of memory:

```python
# Use SQLAlchemy or MongoDB
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Store jobs in database for persistence across restarts
```

### Challenge 2: Job Priority Queue

Implement priority-based job processing:

```python
import heapq

class PriorityJobQueue:
    def __init__(self):
        self.queue = []

    def add_job(self, job: Job, priority: int):
        heapq.heappush(self.queue, (priority, job))

    def get_next_job(self):
        if self.queue:
            return heapq.heappop(self.queue)[1]
        return None
```

### Challenge 3: Celery Integration

Use Celery for production job queues:

```bash
pip install celery redis
```

```python
from celery import Celery

celery_app = Celery('tasks', broker='redis://localhost:6379')

@celery_app.task
def process_batch(texts: list):
    # Process batch
    return results
```

### Challenge 4: WebSocket Updates

Use WebSockets instead of SSE for bidirectional communication:

```python
from fastapi import WebSocket

@app.websocket("/ws/jobs/{job_id}")
async def websocket_job_updates(websocket: WebSocket, job_id: str):
    await websocket.accept()
    # Send updates via WebSocket
```

## Key Takeaways

1. **BackgroundTasks:** Simple async operations that don't block responses
2. **Job Queues:** Track long-running operations with status polling
3. **Async/Await:** Efficient handling of I/O-bound operations
4. **SSE:** Real-time updates without polling overhead
5. **Progress Tracking:** Keep users informed of job status

## Next Steps

- Exercise 05: Deploy API with Docker
- Learn about Celery and RabbitMQ for production queues
- Implement WebSocket for real-time bidirectional communication

---

**Estimated Time:** 2-3 hours
**Difficulty:** Intermediate-Advanced
**Focus:** Async operations, background tasks, job queues, streaming
