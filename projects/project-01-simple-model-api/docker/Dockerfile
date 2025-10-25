# Dockerfile for Model API
#
# This Dockerfile creates a container image for the model inference API.
# It uses multi-stage builds to optimize image size and build time.
#
# Author: AI Infrastructure Curriculum
# License: MIT

# TODO: Implement Dockerfile
# This is a STUB file with comprehensive instructions.
# Follow the TODOs below to complete the implementation.

# =========================================================================
# Stage 1: Base Image Selection
# =========================================================================

# TODO: Choose base image
# Recommended: python:3.11-slim-bookworm
# - slim: Smaller image size (~100MB vs 900MB for full)
# - bookworm: Debian 12 (latest stable)
# - Alternatives: python:3.11-alpine (smallest but harder to use with ML libs)
#
# FROM python:3.11-slim-bookworm


# =========================================================================
# Stage 2: System Dependencies
# =========================================================================

# TODO: Set working directory
# Recommended: /app
# WORKDIR /app

# TODO: Install system dependencies
# Required for PyTorch and image processing:
# - libgomp1: OpenMP library (required by PyTorch)
# - libglib2.0-0: GLib library (required by PIL/Pillow)
# - ca-certificates: SSL certificates
# - curl: For health checks
#
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     libgomp1 \
#     libglib2.0-0 \
#     ca-certificates \
#     curl \
#     && rm -rf /var/lib/apt/lists/*
#
# Note: Clean apt cache to reduce image size


# =========================================================================
# Stage 3: Python Dependencies
# =========================================================================

# TODO: Copy requirements file first (for better caching)
# Docker caches layers - if requirements.txt doesn't change,
# pip install won't run again
#
# COPY requirements.txt .

# TODO: Install Python dependencies
# - Use --no-cache-dir to reduce image size
# - Consider using specific versions for reproducibility
#
# RUN pip install --no-cache-dir -r requirements.txt

# TODO: Pre-download model weights (OPTIONAL but recommended)
# This downloads model weights during build time instead of first run
# Speeds up container startup and makes it predictable
#
# RUN python -c "import torchvision.models as models; \
#                models.resnet50(pretrained=True)"
#
# Note: This adds ~100MB to image but saves 20-30s on startup


# =========================================================================
# Stage 4: Application Code
# =========================================================================

# TODO: Copy application source code
# Copy src/ directory containing all Python files
#
# COPY src/ ./src/

# TODO: Copy any additional files needed
# - Configuration files
# - Label files
# - etc.
#
# COPY .env.example .env


# =========================================================================
# Stage 5: Configuration
# =========================================================================

# TODO: Set environment variables
# These provide defaults that can be overridden at runtime
#
# ENV MODEL_NAME=resnet50 \
#     DEVICE=cpu \
#     HOST=0.0.0.0 \
#     PORT=5000 \
#     LOG_LEVEL=INFO \
#     PYTHONUNBUFFERED=1

# Note: PYTHONUNBUFFERED=1 ensures logs appear in real-time


# TODO: Expose port
# Document which port the application listens on
#
# EXPOSE 5000


# =========================================================================
# Stage 6: Health Check
# =========================================================================

# TODO: Configure health check
# Docker will periodically check if the container is healthy
#
# HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
#     CMD curl -f http://localhost:5000/health || exit 1
#
# Parameters:
# - interval: How often to check (every 30 seconds)
# - timeout: Max time for check to complete (5 seconds)
# - start-period: Grace period before first check (30s for model loading)
# - retries: Number of failures before marking unhealthy (3)


# =========================================================================
# Stage 7: User Configuration (OPTIONAL but recommended for security)
# =========================================================================

# TODO: Create non-root user (OPTIONAL)
# Running as non-root is a security best practice
#
# RUN useradd -m -u 1000 apiuser && \
#     chown -R apiuser:apiuser /app
#
# USER apiuser


# =========================================================================
# Stage 8: Entrypoint
# =========================================================================

# TODO: Define entrypoint
# This is the command that runs when the container starts
#
# For Flask:
# CMD ["python", "src/app.py"]
#
# For production with Gunicorn:
# CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "src.app:app"]
#
# For FastAPI with Uvicorn:
# CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "5000"]


# =========================================================================
# Advanced Optimizations (OPTIONAL)
# =========================================================================

# TODO: Multi-stage build for smaller image (ADVANCED)
# Use separate stages for building and running
#
# # Build stage
# FROM python:3.11 as builder
# WORKDIR /app
# COPY requirements.txt .
# RUN pip install --user --no-cache-dir -r requirements.txt
#
# # Runtime stage
# FROM python:3.11-slim
# WORKDIR /app
# COPY --from=builder /root/.local /root/.local
# COPY src/ ./src/
# ENV PATH=/root/.local/bin:$PATH
# CMD ["python", "src/app.py"]


# TODO: Use .dockerignore to exclude unnecessary files
# Create a .dockerignore file in the project root with:
# __pycache__
# *.pyc
# *.pyo
# *.pyd
# .Python
# env/
# venv/
# .git/
# .gitignore
# *.md
# tests/
# .pytest_cache/


# =========================================================================
# Build Instructions
# =========================================================================

# TODO: Build the Docker image
# Run from project root directory:
#
# docker build -f docker/Dockerfile -t model-api:v1.0 .
#
# Parameters:
# -f docker/Dockerfile : Specify Dockerfile location
# -t model-api:v1.0    : Tag the image with name and version
# .                    : Build context (project root)


# =========================================================================
# Run Instructions
# =========================================================================

# TODO: Run the container
#
# Basic run:
# docker run -p 5000:5000 model-api:v1.0
#
# With environment variables:
# docker run -p 5000:5000 \
#   -e MODEL_NAME=resnet50 \
#   -e LOG_LEVEL=DEBUG \
#   model-api:v1.0
#
# With volume mount (for development):
# docker run -p 5000:5000 \
#   -v $(pwd)/src:/app/src \
#   model-api:v1.0
#
# In detached mode (background):
# docker run -d -p 5000:5000 --name model-api model-api:v1.0


# =========================================================================
# Image Size Optimization Tips
# =========================================================================

# Tips to reduce image size:
# 1. Use python:3.11-slim instead of python:3.11
# 2. Clean apt cache after installing packages
# 3. Use --no-cache-dir with pip
# 4. Use multi-stage builds
# 5. Don't include test files or documentation
# 6. Combine RUN commands to reduce layers
# 7. Order commands from least to most frequently changing
#
# Target image size: < 2GB
# Typical sizes:
# - python:3.11: ~900MB base
# - python:3.11-slim: ~120MB base
# - + PyTorch: ~500MB
# - + Model weights: ~100MB
# - + Your code: <10MB
# Total: ~730MB - 1.5GB


# =========================================================================
# Troubleshooting
# =========================================================================

# Common issues:
#
# 1. "No module named 'torch'"
#    - Make sure requirements.txt is copied and installed
#
# 2. "Cannot connect to Docker daemon"
#    - Start Docker Desktop or Docker service
#
# 3. "ModuleNotFoundError: No module named 'src'"
#    - Run from project root directory
#    - Check WORKDIR is set correctly
#
# 4. Health check always failing
#    - Check application is listening on 0.0.0.0, not 127.0.0.1
#    - Ensure port 5000 is exposed
#    - Wait for model to load (30s start-period)
#
# 5. Image too large
#    - Use slim base image
#    - Clean apt cache
#    - Use .dockerignore


# =========================================================================
# Example Complete Dockerfile
# =========================================================================

# Uncomment and modify the example below:

# FROM python:3.11-slim-bookworm
#
# WORKDIR /app
#
# # Install system dependencies
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     libgomp1 \
#     libglib2.0-0 \
#     ca-certificates \
#     curl \
#     && rm -rf /var/lib/apt/lists/*
#
# # Install Python dependencies
# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt
#
# # Pre-download model (optional)
# RUN python -c "import torchvision.models as models; models.resnet50(pretrained=True)"
#
# # Copy application code
# COPY src/ ./src/
# COPY .env.example .env
#
# # Set environment variables
# ENV MODEL_NAME=resnet50 \
#     DEVICE=cpu \
#     HOST=0.0.0.0 \
#     PORT=5000 \
#     LOG_LEVEL=INFO \
#     PYTHONUNBUFFERED=1
#
# # Expose port
# EXPOSE 5000
#
# # Health check
# HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
#     CMD curl -f http://localhost:5000/health || exit 1
#
# # Run application
# CMD ["python", "src/app.py"]
