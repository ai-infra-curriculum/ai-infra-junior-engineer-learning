"""
Model API Application

This module implements the REST API for model inference using Flask.

Choose Flask OR FastAPI - both implementations are shown below.
Flask is recommended for beginners.

Author: AI Infrastructure Curriculum
License: MIT
"""

import io
import time
import uuid
import logging
from typing import Dict, Tuple, Optional
from PIL import Image

# TODO: Choose your framework - uncomment ONE of these:
# from flask import Flask, request, jsonify, Response
# from fastapi import FastAPI, File, UploadFile, HTTPException
# from fastapi.responses import JSONResponse

# TODO: Import your modules after implementing them
# from config import Config
# from model_loader import ModelLoader

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# =========================================================================
# FLASK IMPLEMENTATION
# =========================================================================

"""
TODO: Implement Flask application
Uncomment and complete the code below if using Flask.

# Initialize Flask app
app = Flask(__name__)

# TODO: Initialize configuration
# config = Config()

# TODO: Initialize model loader
# model_loader = None  # Will be loaded in init_model()


def init_model():
    '''
    Initialize and load ML model.

    TODO: Implement model initialization
    - Create ModelLoader instance
    - Load model
    - Handle errors gracefully
    - This is called once at startup
    '''
    global model_loader
    # TODO: Implement model loading
    # try:
    #     logger.info("Initializing model...")
    #     model_loader = ModelLoader(
    #         model_name=config.MODEL_NAME,
    #         device=config.DEVICE
    #     )
    #     model_loader.load()
    #     logger.info("Model initialized successfully")
    # except Exception as e:
    #     logger.error(f"Failed to initialize model: {e}")
    #     raise
    pass


@app.route('/health', methods=['GET'])
def health():
    '''
    Health check endpoint.

    TODO: Implement health check
    - Check if model is loaded
    - Return healthy status if model loaded
    - Return unhealthy (503) if model not loaded
    - Include model name and uptime

    Returns:
        JSON response with health status
    '''
    # TODO: Implement health check
    # is_healthy = model_loader is not None and model_loader.model is not None
    #
    # if is_healthy:
    #     return jsonify({
    #         'status': 'healthy',
    #         'model_loaded': True,
    #         'model_name': model_loader.model_name
    #     }), 200
    # else:
    #     return jsonify({
    #         'status': 'unhealthy',
    #         'model_loaded': False,
    #         'reason': 'Model not loaded'
    #     }), 503
    pass


@app.route('/info', methods=['GET'])
def info():
    '''
    Model information endpoint.

    TODO: Implement info endpoint
    - Return model metadata
    - Include API version
    - Include supported endpoints
    - Include limits (file size, timeout, etc.)

    Returns:
        JSON response with model and API info
    '''
    # TODO: Implement info endpoint
    # if model_loader is None:
    #     return jsonify({'error': 'Model not loaded'}), 503
    #
    # model_info = model_loader.get_model_info()
    #
    # return jsonify({
    #     'model': model_info,
    #     'api': {
    #         'version': config.API_VERSION,
    #         'endpoints': ['/predict', '/health', '/info']
    #     },
    #     'limits': {
    #         'max_file_size_mb': config.MAX_FILE_SIZE / (1024 * 1024),
    #         'max_image_dimension': config.MAX_IMAGE_DIMENSION,
    #         'timeout_seconds': config.REQUEST_TIMEOUT
    #     }
    # }), 200
    pass


@app.route('/predict', methods=['POST'])
def predict():
    '''
    Prediction endpoint.

    TODO: Implement prediction endpoint
    1. Generate correlation ID for request tracking
    2. Validate request has file
    3. Validate file size
    4. Load and validate image
    5. Get top_k parameter (optional)
    6. Call model_loader.predict()
    7. Measure latency
    8. Format response
    9. Log request
    10. Handle all errors gracefully

    Returns:
        JSON response with predictions or error
    '''
    correlation_id = generate_correlation_id()
    start_time = time.time()

    # TODO: Implement prediction logic
    # try:
    #     # 1. Validate request has file
    #     if 'file' not in request.files:
    #         return format_error_response(
    #             'MISSING_FILE',
    #             'No file provided in request',
    #             correlation_id
    #         ), 400
    #
    #     file = request.files['file']
    #
    #     # 2. Check file has name
    #     if file.filename == '':
    #         return format_error_response(
    #             'EMPTY_FILENAME',
    #             'Empty filename',
    #             correlation_id
    #         ), 400
    #
    #     # 3. Check file size
    #     file.seek(0, 2)  # Seek to end
    #     file_size = file.tell()
    #     file.seek(0)  # Reset to beginning
    #
    #     if file_size > config.MAX_FILE_SIZE:
    #         return format_error_response(
    #             'FILE_TOO_LARGE',
    #             f'File size {file_size} exceeds limit {config.MAX_FILE_SIZE}',
    #             correlation_id
    #         ), 413
    #
    #     # 4. Load image
    #     try:
    #         file_bytes = file.read()
    #         image = Image.open(io.BytesIO(file_bytes))
    #     except Exception as e:
    #         return format_error_response(
    #             'INVALID_IMAGE_FORMAT',
    #             f'Could not load image: {str(e)}',
    #             correlation_id
    #         ), 400
    #
    #     # 5. Validate image
    #     is_valid, error_msg = model_loader.validate_image(image)
    #     if not is_valid:
    #         return format_error_response(
    #             'INVALID_IMAGE',
    #             error_msg,
    #             correlation_id
    #         ), 400
    #
    #     # 6. Get top_k parameter
    #     top_k = request.form.get('top_k', config.DEFAULT_TOP_K)
    #     try:
    #         top_k = int(top_k)
    #         if top_k < 1 or top_k > config.MAX_TOP_K:
    #             return format_error_response(
    #                 'INVALID_PARAMETER',
    #                 f'top_k must be between 1 and {config.MAX_TOP_K}',
    #                 correlation_id
    #             ), 400
    #     except ValueError:
    #         return format_error_response(
    #             'INVALID_PARAMETER',
    #             'top_k must be an integer',
    #             correlation_id
    #         ), 400
    #
    #     # 7. Generate predictions
    #     predictions = model_loader.predict(image, top_k=top_k)
    #
    #     # 8. Calculate latency
    #     latency_ms = (time.time() - start_time) * 1000
    #
    #     # 9. Log request
    #     logger.info(f"Prediction successful: correlation_id={correlation_id}, "
    #                f"latency={latency_ms:.2f}ms, top_class={predictions[0]['class']}")
    #
    #     # 10. Return response
    #     return format_success_response(predictions, latency_ms, correlation_id), 200
    #
    # except Exception as e:
    #     logger.error(f"Prediction error: {e}", exc_info=True)
    #     return format_error_response(
    #         'INTERNAL_ERROR',
    #         'Internal server error',
    #         correlation_id
    #     ), 500
    pass


# =========================================================================
# Error Handlers
# =========================================================================

@app.errorhandler(404)
def not_found(error):
    '''Handle 404 errors.'''
    # TODO: Implement 404 handler
    # return jsonify({
    #     'success': False,
    #     'error': {
    #         'code': 'NOT_FOUND',
    #         'message': 'Endpoint not found'
    #     }
    # }), 404
    pass


@app.errorhandler(405)
def method_not_allowed(error):
    '''Handle 405 errors.'''
    # TODO: Implement 405 handler
    pass


@app.errorhandler(500)
def internal_error(error):
    '''Handle 500 errors.'''
    # TODO: Implement 500 handler
    pass


# =========================================================================
# Helper Functions
# =========================================================================

def generate_correlation_id() -> str:
    '''
    Generate unique correlation ID for request tracking.

    TODO: Implement correlation ID generation
    - Use UUID for uniqueness
    - Format as 'req-<8-char-hex>'
    - Used for tracing requests in logs

    Returns:
        Correlation ID string

    Example:
        >>> generate_correlation_id()
        'req-a1b2c3d4'
    '''
    # TODO: Implement
    # return f"req-{uuid.uuid4().hex[:8]}"
    pass


def format_success_response(predictions: list,
                           latency_ms: float,
                           correlation_id: str) -> dict:
    '''
    Format successful prediction response.

    TODO: Implement success response formatting
    - Include success=True
    - Include predictions list
    - Include latency
    - Include correlation_id
    - Include timestamp

    Args:
        predictions: List of prediction dictionaries
        latency_ms: Request latency in milliseconds
        correlation_id: Request correlation ID

    Returns:
        Formatted response dictionary
    '''
    # TODO: Implement
    # from datetime import datetime
    # return {
    #     'success': True,
    #     'predictions': predictions,
    #     'latency_ms': round(latency_ms, 2),
    #     'correlation_id': correlation_id,
    #     'timestamp': datetime.utcnow().isoformat() + 'Z'
    # }
    pass


def format_error_response(error_code: str,
                         message: str,
                         correlation_id: str,
                         details: Optional[dict] = None) -> dict:
    '''
    Format error response.

    TODO: Implement error response formatting
    - Include success=False
    - Include error object with code, message
    - Include correlation_id for tracking
    - Include timestamp
    - Optionally include details

    Args:
        error_code: Error code (e.g., 'INVALID_IMAGE')
        message: Human-readable error message
        correlation_id: Request correlation ID
        details: Optional additional details

    Returns:
        Formatted error response dictionary
    '''
    # TODO: Implement
    # from datetime import datetime
    # error_response = {
    #     'success': False,
    #     'error': {
    #         'code': error_code,
    #         'message': message,
    #         'correlation_id': correlation_id,
    #         'timestamp': datetime.utcnow().isoformat() + 'Z'
    #     }
    # }
    # if details:
    #     error_response['error']['details'] = details
    # return error_response
    pass


def validate_image_file(file) -> Tuple[bool, Optional[str]]:
    '''
    Validate uploaded file is a valid image.

    TODO: Implement file validation
    - Check file is not None
    - Check file has content
    - Try to open with PIL
    - Return (is_valid, error_message)

    Args:
        file: Flask file object

    Returns:
        Tuple of (is_valid, error_message)
    '''
    # TODO: Implement validation
    pass


# =========================================================================
# Application Startup
# =========================================================================

if __name__ == '__main__':
    '''
    Run Flask application.

    TODO: Implement application startup
    - Initialize model
    - Start Flask server
    - Use config for host and port
    '''
    # TODO: Implement startup
    # try:
    #     # Initialize model
    #     init_model()
    #
    #     # Start server
    #     logger.info(f"Starting server on {config.HOST}:{config.PORT}")
    #     app.run(
    #         host=config.HOST,
    #         port=config.PORT,
    #         debug=config.DEBUG
    #     )
    # except Exception as e:
    #     logger.error(f"Failed to start server: {e}")
    #     exit(1)
    pass
"""


# =========================================================================
# FASTAPI IMPLEMENTATION (ALTERNATIVE)
# =========================================================================

"""
TODO: Implement FastAPI application (OPTIONAL - only if you prefer FastAPI)
FastAPI provides automatic API documentation and better async support.
Uncomment and complete the code below if using FastAPI.

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List

# Initialize FastAPI app
app = FastAPI(
    title="Model Inference API",
    description="REST API for image classification",
    version="1.0.0"
)

# TODO: Initialize configuration and model
# config = Config()
# model_loader = None


# Response models
class PredictionResponse(BaseModel):
    '''Prediction response model.'''
    class_name: str
    confidence: float
    rank: int


class PredictionsResponse(BaseModel):
    '''Full predictions response.'''
    success: bool
    predictions: List[PredictionResponse]
    latency_ms: float
    correlation_id: str
    timestamp: str


class ErrorResponse(BaseModel):
    '''Error response model.'''
    success: bool
    error: dict


@app.on_event("startup")
async def startup_event():
    '''
    Initialize model on startup.

    TODO: Implement startup logic
    - Load model
    - Log successful startup
    '''
    # global model_loader
    # logger.info("Initializing model...")
    # model_loader = ModelLoader(
    #     model_name=config.MODEL_NAME,
    #     device=config.DEVICE
    # )
    # model_loader.load()
    # logger.info("Model loaded successfully")
    pass


@app.get("/health")
async def health():
    '''
    Health check endpoint.

    TODO: Implement health check
    '''
    # TODO: Implement
    pass


@app.get("/info")
async def info():
    '''
    Model info endpoint.

    TODO: Implement info endpoint
    '''
    # TODO: Implement
    pass


@app.post("/predict", response_model=PredictionsResponse)
async def predict(file: UploadFile = File(...), top_k: int = 5):
    '''
    Prediction endpoint.

    TODO: Implement prediction
    - Validate file
    - Load image
    - Generate predictions
    - Return formatted response
    '''
    # TODO: Implement
    pass


if __name__ == "__main__":
    '''Run FastAPI application with uvicorn.'''
    import uvicorn

    # TODO: Start server
    # uvicorn.run(
    #     app,
    #     host=config.HOST,
    #     port=config.PORT,
    #     log_level=config.LOG_LEVEL.lower()
    # )
    pass
"""


# =========================================================================
# Testing During Development
# =========================================================================

"""
TODO: Test your implementation

Flask testing:
$ python app.py

FastAPI testing:
$ uvicorn app:app --reload

Then in another terminal:
$ curl http://localhost:5000/health
$ curl http://localhost:5000/info
$ curl -X POST -F "file=@test_image.jpg" http://localhost:5000/predict

Or use Postman for easier testing.
"""
