"""
Model Serving API with Kubernetes Support

This is an enhanced version of the API from Project 01, now with:
- Prometheus metrics for monitoring
- Comprehensive health checks (liveness and readiness)
- Configuration from environment variables and ConfigMaps
- Structured logging
- Graceful shutdown handling

Learning Objectives:
- Understand health check implementations for Kubernetes
- Export Prometheus metrics from Python applications
- Handle configuration in cloud-native applications
- Implement graceful shutdown for zero-downtime deployments
"""

from flask import Flask, request, jsonify, Response
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
import os
import sys
import logging
import signal
import time
from typing import Dict, Any, Optional
import threading

# TODO: Import the model loading module you'll create
# from model import ModelLoader

# ============================================================================
# CONFIGURATION
# ============================================================================

# TODO: Read configuration from environment variables (set by Kubernetes ConfigMap)
# These environment variables are injected by the Kubernetes Deployment manifest
# Reference: kubernetes/configmap.yaml and kubernetes/deployment.yaml

MODEL_NAME: str = ""  # TODO: os.getenv('MODEL_NAME', 'resnet50')
LOG_LEVEL: str = ""   # TODO: os.getenv('LOG_LEVEL', 'INFO')
MAX_BATCH_SIZE: int = 0  # TODO: int(os.getenv('MAX_BATCH_SIZE', '32'))
PORT: int = 0  # TODO: int(os.getenv('PORT', '5000'))

# ============================================================================
# LOGGING SETUP
# ============================================================================

# TODO: Configure structured logging
# Use the LOG_LEVEL from environment variable
# Format: JSON for better parsing in log aggregation systems (future project)
# Include: timestamp, level, message, context

def setup_logging() -> logging.Logger:
    """
    Configure application logging.

    TODO: Implement logging setup:
    1. Create logger instance
    2. Set log level from LOG_LEVEL environment variable
    3. Create handler (StreamHandler for container logs)
    4. Set format: '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    5. Add handler to logger

    Returns:
        logging.Logger: Configured logger instance

    Example:
        logger = logging.getLogger('model-api')
        logger.setLevel(getattr(logging, LOG_LEVEL))
        ...
    """
    # TODO: Implement logging setup
    pass


logger = None  # TODO: setup_logging()

# ============================================================================
# PROMETHEUS METRICS
# ============================================================================

# TODO: Define Prometheus metrics using prometheus_client
# These metrics will be scraped by Prometheus every 30 seconds

# Counter: Monotonically increasing value (requests, errors, predictions)
# Histogram: Distribution of values (latency, inference time)
# Gauge: Value that can go up or down (model loaded status, active connections)

# TODO: Create request counter
# Track total requests with labels: method, endpoint, status_code
request_count = None  # TODO: Counter(...)

# TODO: Create request duration histogram
# Track request latency with labels: method, endpoint
# Buckets: [0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0] (in seconds)
request_duration = None  # TODO: Histogram(...)

# TODO: Create prediction counter
# Track total predictions with labels: model_name, status (success/error)
prediction_count = None  # TODO: Counter(...)

# TODO: Create inference duration histogram
# Track model inference time with labels: model_name
# Buckets: [0.01, 0.05, 0.1, 0.2, 0.5, 1.0] (in seconds)
inference_duration = None  # TODO: Histogram(...)

# TODO: Create model loaded gauge
# Value: 1 if model loaded, 0 if not
# Labels: model_name, version
model_loaded_gauge = None  # TODO: Gauge(...)

# TODO: Create active connections gauge
# Track current number of active requests
active_connections = None  # TODO: Gauge(...)

# ============================================================================
# APPLICATION STATE
# ============================================================================

class ApplicationState:
    """
    Track application state for health checks and graceful shutdown.

    This class maintains state information used by Kubernetes probes:
    - is_ready: False during startup (model loading), True when ready for traffic
    - is_alive: True when application is functioning, False during shutdown
    - model_loaded: True after model successfully loaded
    - shutdown_event: Threading event to coordinate graceful shutdown
    """

    def __init__(self):
        # TODO: Initialize state variables
        self.is_ready: bool = False  # TODO: Set to False initially
        self.is_alive: bool = True   # TODO: Set to True initially
        self.model_loaded: bool = False  # TODO: Set to False initially
        self.shutdown_event = None  # TODO: threading.Event()
        self.model = None  # Will hold loaded model instance

    def mark_ready(self) -> None:
        """Mark application as ready to receive traffic."""
        # TODO: Set is_ready to True and log the event
        pass

    def mark_not_ready(self) -> None:
        """Mark application as not ready (during shutdown)."""
        # TODO: Set is_ready to False and log the event
        pass

    def mark_shutdown(self) -> None:
        """Mark application for shutdown."""
        # TODO: Set is_alive to False, is_ready to False, and trigger shutdown_event
        pass


app_state = None  # TODO: ApplicationState()

# ============================================================================
# FLASK APPLICATION
# ============================================================================

app = Flask(__name__)

# ============================================================================
# MIDDLEWARE
# ============================================================================

@app.before_request
def before_request():
    """
    Middleware executed before each request.

    TODO: Implement:
    1. Increment active_connections gauge
    2. Store request start time (for latency calculation)
    3. Log request details (method, path, client IP)

    Flask's request object is thread-local, safe to attach attributes:
    request.start_time = time.time()
    """
    # TODO: Implement before_request middleware
    pass


@app.after_request
def after_request(response):
    """
    Middleware executed after each request.

    TODO: Implement:
    1. Calculate request duration (time.time() - request.start_time)
    2. Record metrics:
       - request_duration (histogram)
       - request_count (counter) with labels
    3. Decrement active_connections gauge
    4. Log response status and duration

    Args:
        response: Flask Response object

    Returns:
        Response object (must return for Flask)
    """
    # TODO: Implement after_request middleware
    return response


# ============================================================================
# HEALTH CHECK ENDPOINTS
# ============================================================================

@app.route('/health', methods=['GET'])
def health():
    """
    Combined health check endpoint for both liveness and readiness probes.

    Kubernetes will call this endpoint to determine:
    - Liveness: Is the application alive? (Should I restart it?)
    - Readiness: Is the application ready for traffic? (Should I route requests to it?)

    TODO: Implement health check logic:
    1. Check if shutdown is in progress (app_state.is_alive)
    2. Check if model is loaded (app_state.model_loaded)
    3. Return appropriate status code and message

    Return Codes:
    - 200 OK: Healthy and ready
    - 503 Service Unavailable: Not ready (model still loading) or shutting down

    Response Format:
    {
        "status": "healthy" | "unhealthy",
        "model_loaded": true | false,
        "model_name": "resnet50",
        "uptime_seconds": 123.45
    }

    Note: Some implementations separate /health/live and /health/ready endpoints.
    For simplicity, we use one endpoint that serves both purposes.
    """
    # TODO: Implement health check
    # Hint: Check app_state.is_alive and app_state.model_loaded
    # Return 200 if both are True, otherwise 503
    pass


@app.route('/health/live', methods=['GET'])
def liveness():
    """
    Dedicated liveness probe endpoint.

    Returns 200 if application is alive (not deadlocked or crashed).
    Kubernetes will restart the pod if this fails repeatedly.

    TODO: Implement liveness check:
    1. Check app_state.is_alive
    2. Return 200 if alive, 503 if shutting down

    This should be lenient - only fail if truly broken.
    """
    # TODO: Implement liveness check
    pass


@app.route('/health/ready', methods=['GET'])
def readiness():
    """
    Dedicated readiness probe endpoint.

    Returns 200 if application is ready to serve traffic.
    Kubernetes will remove pod from service endpoints if this fails.

    TODO: Implement readiness check:
    1. Check app_state.is_ready and app_state.model_loaded
    2. Optionally: Check dependencies (database, cache, etc.)
    3. Return 200 if ready, 503 if not

    This can be strict - fail if not ready to serve requests properly.
    """
    # TODO: Implement readiness check
    pass


# ============================================================================
# METRICS ENDPOINT
# ============================================================================

@app.route('/metrics', methods=['GET'])
def metrics():
    """
    Prometheus metrics endpoint.

    Exposes metrics in Prometheus format for scraping.
    Prometheus will scrape this endpoint every 30 seconds (configured in ServiceMonitor).

    TODO: Implement metrics endpoint:
    1. Use prometheus_client.generate_latest() to get metrics
    2. Return with correct content type (CONTENT_TYPE_LATEST)

    Example output format:
    # HELP model_api_requests_total Total requests
    # TYPE model_api_requests_total counter
    model_api_requests_total{endpoint="/predict",method="POST",status_code="200"} 42.0

    Returns:
        Response: Metrics in Prometheus text format
    """
    # TODO: Implement metrics endpoint
    # return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)
    pass


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.route('/predict', methods=['POST'])
def predict():
    """
    Model prediction endpoint.

    Accepts JSON input, runs inference, returns predictions.

    TODO: Implement prediction endpoint:
    1. Validate request has JSON content
    2. Extract input data from request.json
    3. Validate input format and size (check MAX_BATCH_SIZE)
    4. Time the inference operation
    5. Call model.predict(input_data)
    6. Record metrics:
       - prediction_count (increment)
       - inference_duration (observe timing)
    7. Return predictions as JSON
    8. Handle errors gracefully (invalid input, inference failure)

    Request Format:
    {
        "instances": [
            [1, 2, 3, ...],
            [4, 5, 6, ...]
        ]
    }

    Response Format:
    {
        "predictions": [
            {"class": "cat", "confidence": 0.95},
            {"class": "dog", "confidence": 0.87}
        ],
        "model_name": "resnet50",
        "inference_time_ms": 45.2
    }

    Error Response:
    {
        "error": "Invalid input format",
        "details": "Expected 'instances' key in JSON"
    }
    """
    # TODO: Implement prediction endpoint

    # Step 1: Validate JSON content
    # if not request.is_json:
    #     return jsonify({"error": "Content-Type must be application/json"}), 400

    # Step 2: Extract input data
    # data = request.get_json()

    # Step 3: Validate input
    # if 'instances' not in data:
    #     return jsonify({"error": "Missing 'instances' in request"}), 400

    # Step 4: Check batch size
    # if len(data['instances']) > MAX_BATCH_SIZE:
    #     return jsonify({"error": f"Batch size exceeds maximum of {MAX_BATCH_SIZE}"}), 400

    # Step 5: Run inference with timing
    # start_time = time.time()
    # try:
    #     predictions = app_state.model.predict(data['instances'])
    #     inference_time = (time.time() - start_time) * 1000  # Convert to ms
    #
    #     # Record metrics
    #     prediction_count.labels(model_name=MODEL_NAME, status='success').inc()
    #     inference_duration.labels(model_name=MODEL_NAME).observe(inference_time / 1000)
    #
    #     return jsonify({
    #         "predictions": predictions,
    #         "model_name": MODEL_NAME,
    #         "inference_time_ms": round(inference_time, 2)
    #     }), 200
    # except Exception as e:
    #     logger.error(f"Prediction failed: {str(e)}")
    #     prediction_count.labels(model_name=MODEL_NAME, status='error').inc()
    #     return jsonify({"error": "Prediction failed", "details": str(e)}), 500

    pass


@app.route('/', methods=['GET'])
def index():
    """
    Root endpoint - API information.

    TODO: Implement index endpoint:
    Return basic API information and available endpoints.

    Response:
    {
        "service": "Model Serving API",
        "version": "2.0",
        "model": "resnet50",
        "endpoints": {
            "predict": "/predict",
            "health": "/health",
            "metrics": "/metrics"
        }
    }
    """
    # TODO: Implement index endpoint
    pass


# ============================================================================
# MODEL LOADING
# ============================================================================

def load_model() -> None:
    """
    Load ML model on application startup.

    This function is called before the application starts accepting traffic.
    It's critical for the readiness probe - application should not be marked
    ready until the model is loaded.

    TODO: Implement model loading:
    1. Log model loading start
    2. Import and initialize ModelLoader (from model.py)
    3. Load model based on MODEL_NAME environment variable
    4. Store model in app_state.model
    5. Update app_state.model_loaded = True
    6. Update model_loaded_gauge metric
    7. Mark application as ready (app_state.mark_ready())
    8. Handle errors (log and exit if model fails to load)

    Example:
        from model import ModelLoader
        loader = ModelLoader(MODEL_NAME)
        app_state.model = loader.load()
        app_state.model_loaded = True
        model_loaded_gauge.labels(model_name=MODEL_NAME, version='1.0').set(1)
        app_state.mark_ready()

    Note: Large models may take 10-30 seconds to load.
    This is why initialDelaySeconds in readiness probe is important.
    """
    # TODO: Implement model loading
    pass


# ============================================================================
# GRACEFUL SHUTDOWN
# ============================================================================

def handle_shutdown(signum, frame):
    """
    Handle shutdown signals for graceful termination.

    Kubernetes sends SIGTERM when terminating a pod:
    1. Pod removed from service endpoints (no new traffic)
    2. SIGTERM sent to container
    3. Grace period (default 30 seconds)
    4. SIGKILL if still running

    TODO: Implement graceful shutdown:
    1. Log shutdown signal received
    2. Mark application as not ready (app_state.mark_not_ready())
    3. Wait briefly for active requests to complete (e.g., 2 seconds)
    4. Mark application for shutdown (app_state.mark_shutdown())
    5. Log shutdown complete
    6. Exit gracefully

    Args:
        signum: Signal number
        frame: Current stack frame

    Example:
        logger.info(f"Received signal {signum}, starting graceful shutdown...")
        app_state.mark_not_ready()
        time.sleep(2)  # Let active requests finish
        app_state.mark_shutdown()
        logger.info("Shutdown complete")
        sys.exit(0)
    """
    # TODO: Implement graceful shutdown handler
    pass


# Register signal handlers
# TODO: Register SIGTERM and SIGINT handlers
# signal.signal(signal.SIGTERM, handle_shutdown)
# signal.signal(signal.SIGINT, handle_shutdown)


# ============================================================================
# APPLICATION STARTUP
# ============================================================================

def initialize_application():
    """
    Initialize application on startup.

    TODO: Implement application initialization:
    1. Log application startup with configuration
    2. Call load_model() to load ML model
    3. Log successful initialization
    4. Handle initialization errors

    This function is called before Flask starts the web server.
    """
    # TODO: Implement application initialization
    pass


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == '__main__':
    """
    Application entry point.

    TODO: Implement main:
    1. Initialize application (load model, setup state)
    2. Start Flask development server

    Configuration:
    - host: '0.0.0.0' (listen on all interfaces, required for container)
    - port: PORT from environment (default 5000)
    - debug: False in production (set from env var)

    Note: For production, use Gunicorn or uWSGI instead of Flask dev server.
    Example Dockerfile CMD:
        gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 60 app:app
    """
    # TODO: Initialize application
    # initialize_application()

    # TODO: Start Flask server
    # app.run(host='0.0.0.0', port=PORT, debug=False)

    pass


# ============================================================================
# LEARNING NOTES
# ============================================================================

"""
Key Concepts for Kubernetes Integration:

1. HEALTH CHECKS
   - Liveness: Is the app alive? (restart if fails)
   - Readiness: Is the app ready for traffic? (remove from endpoints if fails)
   - Best practice: Separate concerns (liveness is lenient, readiness is strict)

2. CONFIGURATION
   - Use environment variables for config (12-factor app principle)
   - Kubernetes ConfigMaps inject env vars into pods
   - Secrets for sensitive data (not ConfigMaps!)

3. OBSERVABILITY
   - Prometheus metrics: Expose at /metrics endpoint
   - Structured logging: JSON format for log aggregation
   - Include context: request IDs, user IDs, trace IDs (future)

4. GRACEFUL SHUTDOWN
   - Handle SIGTERM signal
   - Stop accepting new requests (mark not ready)
   - Complete active requests (grace period)
   - Clean up resources (close connections)
   - Exit cleanly

5. ZERO-DOWNTIME DEPLOYMENTS
   - Readiness probe prevents traffic to new pods until ready
   - Graceful shutdown drains traffic from old pods
   - Rolling update strategy ensures minimum replicas available

6. METRICS BEST PRACTICES
   - Counter: monotonic (requests, errors) - use .inc()
   - Gauge: up/down (current state) - use .set()
   - Histogram: distribution (latency) - use .observe()
   - Label cardinality: Keep low (don't use user IDs as labels!)

7. ERROR HANDLING
   - Return appropriate HTTP status codes
   - Include error details in response (not just "error")
   - Log errors with context
   - Distinguish client errors (4xx) from server errors (5xx)

Next Steps:
- Project 03: Add distributed tracing (OpenTelemetry)
- Project 04: Implement caching layer (Redis)
- Project 05: Multi-model serving with traffic routing
"""
