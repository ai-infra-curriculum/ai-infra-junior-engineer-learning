"""
Prometheus Metrics Instrumentation for ML API

This module provides comprehensive metrics instrumentation for the ML inference API,
including application metrics, infrastructure metrics, and ML-specific metrics.

Learning Objectives:
- Understand different Prometheus metric types (Counter, Gauge, Histogram, Summary)
- Learn how to instrument web applications with metrics
- Implement middleware for automatic request tracking
- Export metrics in Prometheus format
- Track ML-specific metrics (predictions, latency, confidence)

Reference:
- Prometheus Python Client: https://github.com/prometheus/client_python
- Prometheus Best Practices: https://prometheus.io/docs/practices/naming/
"""

from prometheus_client import Counter, Histogram, Gauge, Info, Summary
from prometheus_client import CollectorRegistry, generate_latest
from flask import Flask, Response, request, g
import time
import logging
from typing import Dict, Optional, Callable
import functools

# TODO: Import psutil for system metrics (CPU, memory, disk)
# Hint: pip install psutil
# import psutil

logger = logging.getLogger(__name__)


# =============================================================================
# Metric Registry
# =============================================================================

# TODO: Create a custom registry for all metrics
# Hint: registry = CollectorRegistry()
# Why custom registry? Allows you to control which metrics are exposed,
# useful for testing and multi-app deployments


# =============================================================================
# Application Info Metrics
# =============================================================================

# TODO: Create an Info metric for application metadata
# This provides static information about your application
#
# Example:
# app_info = Info(
#     'app_info',
#     'Application information',
#     registry=registry
# )
#
# Then set the info:
# app_info.info({
#     'version': '1.0.0',
#     'environment': 'production',
#     'service': 'ml-api',
#     'model_version': 'resnet50-v1'
# })


# =============================================================================
# HTTP Request Metrics
# =============================================================================

# TODO: Create a Counter for total HTTP requests
# Counter: A metric that only increases (never decreases or resets)
# Use for: Total requests, total errors, total predictions
#
# Syntax:
# http_requests_total = Counter(
#     'http_requests_total',
#     'Total HTTP requests',
#     ['method', 'endpoint', 'status'],  # Labels for dimensions
#     registry=registry
# )
#
# Labels best practices:
# - Use labels for dimensions (method, endpoint, status)
# - Keep cardinality low (avoid user IDs, request IDs as labels)
# - Use consistent label names across metrics


# TODO: Create a Histogram for HTTP request duration
# Histogram: Samples observations and counts them in configurable buckets
# Use for: Request duration, response size, inference latency
#
# Syntax:
# http_request_duration_seconds = Histogram(
#     'http_request_duration_seconds',
#     'HTTP request duration in seconds',
#     ['method', 'endpoint'],
#     buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
#     registry=registry
# )
#
# Bucket selection tips:
# - Start with powers of 2 or 10
# - Cover expected range (0.01s to 10s for API requests)
# - Add buckets at important thresholds (SLA boundaries)
# - Too many buckets = high cardinality, too few = imprecise percentiles


# TODO: Create a Histogram for HTTP request size (bytes)
# Track the size of incoming requests
# Useful for: Identifying large payloads, optimizing data transfer
#
# Buckets suggestion: [100, 1000, 10000, 100000, 1000000, 10000000]


# TODO: Create a Histogram for HTTP response size (bytes)
# Track the size of outgoing responses


# TODO: Create a Counter for HTTP requests in flight
# Actually, use a Gauge for this since it goes up and down
# http_requests_in_flight = Gauge(
#     'http_requests_in_flight',
#     'Current number of HTTP requests being processed',
#     registry=registry
# )


# =============================================================================
# ML Model Metrics
# =============================================================================

# TODO: Create a Counter for total model predictions
# Track predictions by model name and predicted class
#
# model_predictions_total = Counter(
#     'model_predictions_total',
#     'Total number of model predictions',
#     ['model_name', 'prediction_class'],
#     registry=registry
# )


# TODO: Create a Histogram for model inference duration
# Critical metric for ML systems - how long does inference take?
#
# Buckets suggestion for inference: [0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0]
# (1ms to 1 second range)


# TODO: Create a Histogram for model prediction confidence
# Track the distribution of confidence scores
# Helps identify when model is uncertain
#
# Buckets suggestion: [0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.99, 1.0]


# TODO: Create a Gauge for current model accuracy
# Updated periodically (daily) with ground truth feedback
#
# model_accuracy = Gauge(
#     'model_accuracy',
#     'Current model accuracy (0-1)',
#     ['model_name'],
#     registry=registry
# )


# TODO: Create a Counter for model prediction errors
# Track when predictions fail (exceptions, timeouts, etc.)


# =============================================================================
# Data Quality Metrics
# =============================================================================

# TODO: Create a Gauge for data drift score
# Measures distribution shift in input data
#
# data_drift_score = Gauge(
#     'data_drift_score',
#     'Data drift score (0-1, higher = more drift)',
#     ['feature_name'],
#     registry=registry
# )


# TODO: Create a Counter for missing features in requests
# Track data quality issues
#
# missing_features_total = Counter(
#     'missing_features_total',
#     'Total requests with missing features',
#     ['feature_name'],
#     registry=registry
# )


# TODO: Create a Counter for invalid requests
# Track malformed requests, schema violations, etc.


# =============================================================================
# Infrastructure Metrics
# =============================================================================

# TODO: Create a Gauge for memory usage in bytes
# Use psutil to get current memory usage
#
# memory_usage_bytes = Gauge(
#     'process_memory_usage_bytes',
#     'Current memory usage in bytes',
#     registry=registry
# )


# TODO: Create a Gauge for CPU usage percentage
# cpu_usage_percent = Gauge(
#     'process_cpu_usage_percent',
#     'Current CPU usage percentage',
#     registry=registry
# )


# TODO: Create a Gauge for active database connections (if using DB)


# =============================================================================
# Business Metrics
# =============================================================================

# TODO: Create a Counter for revenue-impacting predictions
# If your ML system has business value, track it!
#
# Example:
# business_predictions_total = Counter(
#     'business_predictions_total',
#     'Total predictions for paying customers',
#     ['customer_tier'],
#     registry=registry
# )


# =============================================================================
# Metrics Middleware for Flask
# =============================================================================

class MetricsMiddleware:
    """
    Flask middleware to automatically track HTTP request metrics.

    This middleware:
    1. Tracks request count, duration, size for all endpoints
    2. Records response status codes
    3. Handles errors gracefully
    4. Provides helper methods for ML-specific metrics

    Usage:
        app = Flask(__name__)
        metrics = MetricsMiddleware(app)

        @app.route('/predict', methods=['POST'])
        def predict():
            # Your prediction code
            result = model.predict(data)

            # Track prediction metrics
            metrics.track_prediction(
                model_name='resnet50',
                prediction_class='cat',
                confidence=0.95,
                inference_time=0.045
            )

            return jsonify({'prediction': result})
    """

    def __init__(self, app: Flask):
        """
        Initialize metrics middleware.

        Args:
            app: Flask application instance
        """
        self.app = app
        self.setup_middleware()

    def setup_middleware(self):
        """Set up before and after request handlers."""

        # TODO: Implement before_request handler
        # This runs before each request
        #
        # Tasks:
        # 1. Record start time: g.start_time = time.time()
        # 2. Increment in-flight requests gauge
        # 3. Record request size
        #
        # Hint: Use @self.app.before_request decorator
        # Example:
        # @self.app.before_request
        # def before_request():
        #     g.start_time = time.time()
        #     http_requests_in_flight.inc()
        #     # Get request size
        #     request_size = len(request.get_data())
        #     http_request_size_bytes.labels(
        #         method=request.method,
        #         endpoint=request.endpoint or 'unknown'
        #     ).observe(request_size)

        pass  # Remove this after implementing

        # TODO: Implement after_request handler
        # This runs after each request (even if it failed)
        #
        # Tasks:
        # 1. Calculate request duration
        # 2. Record duration in histogram
        # 3. Increment request counter with status code
        # 4. Record response size
        # 5. Decrement in-flight requests gauge
        #
        # Hint: Use @self.app.after_request decorator
        # Example:
        # @self.app.after_request
        # def after_request(response):
        #     # Calculate duration
        #     if hasattr(g, 'start_time'):
        #         duration = time.time() - g.start_time
        #
        #         # Record duration
        #         http_request_duration_seconds.labels(
        #             method=request.method,
        #             endpoint=request.endpoint or 'unknown'
        #         ).observe(duration)
        #
        #         # Record request count with status
        #         http_requests_total.labels(
        #             method=request.method,
        #             endpoint=request.endpoint or 'unknown',
        #             status=response.status_code
        #         ).inc()
        #
        #         # Decrement in-flight
        #         http_requests_in_flight.dec()
        #
        #     return response

        pass  # Remove this after implementing

        # TODO: Implement teardown_request handler for error cases
        # This runs even if the request raised an exception
        # Ensures in-flight gauge is always decremented
        #
        # @self.app.teardown_request
        # def teardown_request(exception=None):
        #     if exception:
        #         http_requests_in_flight.dec()

    def track_prediction(
        self,
        model_name: str,
        prediction_class: str,
        confidence: float,
        inference_time: float
    ):
        """
        Track ML prediction metrics.

        Args:
            model_name: Name of the model (e.g., 'resnet50')
            prediction_class: Predicted class (e.g., 'cat', 'dog')
            confidence: Prediction confidence score (0-1)
            inference_time: Inference duration in seconds
        """
        # TODO: Implement prediction tracking
        # 1. Increment predictions counter
        # 2. Record inference duration
        # 3. Record confidence score
        #
        # Example:
        # model_predictions_total.labels(
        #     model_name=model_name,
        #     prediction_class=prediction_class
        # ).inc()
        #
        # model_inference_duration_seconds.labels(
        #     model_name=model_name
        # ).observe(inference_time)
        #
        # model_prediction_confidence.labels(
        #     model_name=model_name
        # ).observe(confidence)

        pass  # Remove this after implementing

    def track_data_quality(
        self,
        missing_features: Dict[str, int],
        drift_scores: Optional[Dict[str, float]] = None
    ):
        """
        Track data quality metrics.

        Args:
            missing_features: Dict of {feature_name: count} for missing features
            drift_scores: Dict of {feature_name: drift_score} for detected drift
        """
        # TODO: Implement data quality tracking
        # 1. Update missing features counters
        # 2. Update drift score gauges (if provided)
        #
        # Example:
        # for feature_name, count in missing_features.items():
        #     missing_features_total.labels(
        #         feature_name=feature_name
        #     ).inc(count)
        #
        # if drift_scores:
        #     for feature_name, score in drift_scores.items():
        #         data_drift_score.labels(
        #             feature_name=feature_name
        #         ).set(score)

        pass  # Remove this after implementing

    def update_model_accuracy(self, model_name: str, accuracy: float):
        """
        Update model accuracy gauge.

        Args:
            model_name: Name of the model
            accuracy: Current accuracy (0-1)
        """
        # TODO: Update model accuracy gauge
        # model_accuracy.labels(model_name=model_name).set(accuracy)

        pass  # Remove this after implementing


# =============================================================================
# System Metrics Collector
# =============================================================================

class SystemMetricsCollector:
    """
    Collect system-level metrics using psutil.

    Run this in a background thread to periodically update system metrics.
    """

    def __init__(self, interval: int = 15):
        """
        Initialize system metrics collector.

        Args:
            interval: Collection interval in seconds
        """
        self.interval = interval

    def collect_once(self):
        """Collect system metrics once."""
        # TODO: Collect and update system metrics
        #
        # 1. Memory usage:
        #    import psutil
        #    process = psutil.Process()
        #    memory_info = process.memory_info()
        #    memory_usage_bytes.set(memory_info.rss)
        #
        # 2. CPU usage:
        #    cpu_percent = process.cpu_percent(interval=1)
        #    cpu_usage_percent.set(cpu_percent)
        #
        # 3. (Optional) Disk I/O, network I/O, etc.

        pass  # Remove this after implementing

    def start_background_collection(self):
        """Start collecting metrics in a background thread."""
        # TODO: Implement background collection
        #
        # Hint: Use threading.Thread with daemon=True
        #
        # import threading
        #
        # def _collect_loop():
        #     while True:
        #         try:
        #             self.collect_once()
        #         except Exception as e:
        #             logger.error(f"Error collecting system metrics: {e}")
        #         time.sleep(self.interval)
        #
        # thread = threading.Thread(target=_collect_loop, daemon=True)
        # thread.start()
        # logger.info(f"Started system metrics collection (interval={self.interval}s)")

        pass  # Remove this after implementing


# =============================================================================
# Metrics Endpoint
# =============================================================================

def metrics_endpoint() -> Response:
    """
    Expose metrics in Prometheus format.

    This endpoint is scraped by Prometheus to collect metrics.

    Returns:
        Flask Response with metrics in Prometheus text format
    """
    # TODO: Generate and return metrics
    #
    # Use prometheus_client.generate_latest() to export all metrics
    # in Prometheus text format
    #
    # Example:
    # return Response(
    #     generate_latest(registry),
    #     mimetype='text/plain; version=0.0.4; charset=utf-8'
    # )

    pass  # Remove this after implementing


# =============================================================================
# Decorator for Timing Functions
# =============================================================================

def timed(metric_name: str = None, labels: Dict[str, str] = None):
    """
    Decorator to time function execution and record in a metric.

    Usage:
        @timed(metric_name='function_duration_seconds', labels={'function': 'load_model'})
        def load_model():
            # Model loading code
            pass

    Args:
        metric_name: Name of the histogram metric to record duration
        labels: Labels to apply to the metric
    """
    # TODO: Implement timing decorator
    #
    # This is an advanced pattern for tracking arbitrary function durations
    #
    # Hint: Use functools.wraps to preserve function metadata
    #
    # def decorator(func: Callable) -> Callable:
    #     @functools.wraps(func)
    #     def wrapper(*args, **kwargs):
    #         start_time = time.time()
    #         try:
    #             result = func(*args, **kwargs)
    #             return result
    #         finally:
    #             duration = time.time() - start_time
    #             # Record duration in metric
    #             # You'll need to create/get the appropriate metric
    #             logger.debug(f"{func.__name__} took {duration:.4f}s")
    #     return wrapper
    # return decorator

    def decorator(func: Callable) -> Callable:
        return func  # Placeholder
    return decorator


# =============================================================================
# Example Usage
# =============================================================================

if __name__ == "__main__":
    # TODO: Create a sample Flask app with metrics
    #
    # from flask import Flask, jsonify
    #
    # app = Flask(__name__)
    # metrics = MetricsMiddleware(app)
    #
    # @app.route('/metrics')
    # def metrics():
    #     return metrics_endpoint()
    #
    # @app.route('/predict', methods=['POST'])
    # def predict():
    #     # Simulate prediction
    #     import random
    #     time.sleep(random.uniform(0.01, 0.1))  # Simulate inference
    #
    #     prediction_class = random.choice(['cat', 'dog', 'bird'])
    #     confidence = random.uniform(0.7, 0.99)
    #     inference_time = random.uniform(0.01, 0.1)
    #
    #     metrics.track_prediction(
    #         model_name='resnet50',
    #         prediction_class=prediction_class,
    #         confidence=confidence,
    #         inference_time=inference_time
    #     )
    #
    #     return jsonify({
    #         'prediction': prediction_class,
    #         'confidence': confidence
    #     })
    #
    # @app.route('/health')
    # def health():
    #     return jsonify({'status': 'healthy'})
    #
    # # Start system metrics collection
    # collector = SystemMetricsCollector(interval=15)
    # collector.start_background_collection()
    #
    # # Run app
    # app.run(host='0.0.0.0', port=5000)

    print("Implement the example Flask app above to test your metrics!")
    print("\nSteps to test:")
    print("1. Implement all TODOs in this file")
    print("2. Run this file: python instrumentation.py")
    print("3. Make requests: curl -X POST http://localhost:5000/predict")
    print("4. Check metrics: curl http://localhost:5000/metrics")
    print("5. Look for your custom metrics in the output!")
