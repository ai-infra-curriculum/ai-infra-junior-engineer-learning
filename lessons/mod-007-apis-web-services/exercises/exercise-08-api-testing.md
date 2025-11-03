# Exercise 08: Comprehensive API Testing

## Overview

**Estimated Time**: 3-4 hours
**Difficulty**: Intermediate to Advanced
**Prerequisites**:
- Completed Exercises 01-07
- Lecture 03: Authentication, Testing, and Deployment
- Understanding of testing principles (unit, integration, load)
- Familiarity with pytest

## Learning Objectives

By completing this exercise, you will:
1. Write unit tests for API endpoints with pytest
2. Implement integration tests for full request/response cycles
3. Create contract tests for API schemas
4. Perform load testing with Locust
5. Set up CI/CD for automated testing
6. Measure and improve test coverage
7. Apply testing best practices for production APIs

## Scenario

Your team's ML serving API is growing rapidly. You now have:
- 12 endpoints across 3 modules (auth, predictions, admin)
- 5 different teams consuming the API
- 50,000 requests/day with plans to scale 10x
- Critical SLA: 99.9% uptime, <100ms p95 latency

**Current Problem**: The API has minimal tests. Recent deployments broke backward compatibility, causing production incidents.

**Your Mission**: Build a comprehensive test suite that:
- Catches bugs before production
- Validates API contracts
- Ensures performance meets SLAs
- Runs automatically in CI/CD
- Provides confidence for rapid deployment

---

## Part 1: Unit Testing with pytest

### Task 1.1: Set Up Testing Environment

**File**: `conftest.py`

```python
"""Pytest configuration and shared fixtures."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import jwt
from datetime import datetime, timedelta

from app import app, get_db, SECRET_KEY, ALGORITHM
from database import Base
from models import User, Model

# Test database (in-memory SQLite)
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db():
    """Create test database for each test."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db):
    """Create test client with overridden database."""
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def test_user(db):
    """Create a test user in database."""
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password="$2b$12$hashedpassword",  # Pre-hashed
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture
def auth_token(test_user):
    """Generate valid JWT token for test user."""
    payload = {
        "sub": test_user.username,
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token

@pytest.fixture
def auth_headers(auth_token):
    """Generate authorization headers."""
    return {"Authorization": f"Bearer {auth_token}"}

@pytest.fixture
def test_model(db):
    """Create a test ML model record."""
    model = Model(
        name="test-model-v1",
        version="1.0.0",
        model_type="random_forest",
        input_features=10,
        created_at=datetime.utcnow()
    )
    db.add(model)
    db.commit()
    db.refresh(model)
    return model
```

### Task 1.2: Test Authentication Endpoints

**File**: `test_auth.py`

```python
"""Unit tests for authentication endpoints."""

import pytest
from datetime import datetime, timedelta
import jwt

from app import SECRET_KEY, ALGORITHM

class TestLogin:
    """Tests for login endpoint."""

    def test_login_success(self, client, test_user):
        """Test successful login with valid credentials."""
        response = client.post(
            "/auth/login",
            json={
                "username": "testuser",
                "password": "testpassword123"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

        # Verify token is valid
        token = data["access_token"]
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert payload["sub"] == "testuser"

    def test_login_invalid_username(self, client):
        """Test login with non-existent username."""
        response = client.post(
            "/auth/login",
            json={
                "username": "nonexistent",
                "password": "password123"
            }
        )

        assert response.status_code == 401
        assert "error" in response.json()

    def test_login_invalid_password(self, client, test_user):
        """Test login with incorrect password."""
        response = client.post(
            "/auth/login",
            json={
                "username": "testuser",
                "password": "wrongpassword"
            }
        )

        assert response.status_code == 401

    def test_login_missing_fields(self, client):
        """Test login with missing required fields."""
        # Missing password
        response = client.post(
            "/auth/login",
            json={"username": "testuser"}
        )
        assert response.status_code == 422  # Validation error

        # Missing username
        response = client.post(
            "/auth/login",
            json={"password": "password123"}
        )
        assert response.status_code == 422

    @pytest.mark.parametrize("username,password,expected_status", [
        ("", "password123", 422),  # Empty username
        ("a", "password123", 422),  # Too short username
        ("testuser", "123", 422),  # Too short password
        ("test@user", "password123", 422),  # Invalid characters
    ])
    def test_login_validation(self, client, username, password, expected_status):
        """Test input validation for various invalid inputs."""
        response = client.post(
            "/auth/login",
            json={"username": username, "password": password}
        )
        assert response.status_code == expected_status

class TestTokenValidation:
    """Tests for token validation."""

    def test_access_protected_endpoint_with_valid_token(self, client, auth_headers):
        """Test accessing protected endpoint with valid token."""
        response = client.get("/users/me", headers=auth_headers)
        assert response.status_code == 200

    def test_access_protected_endpoint_without_token(self, client):
        """Test accessing protected endpoint without token."""
        response = client.get("/users/me")
        assert response.status_code == 401

    def test_access_protected_endpoint_with_expired_token(self, client, test_user):
        """Test accessing protected endpoint with expired token."""
        # Create expired token
        payload = {
            "sub": test_user.username,
            "exp": datetime.utcnow() - timedelta(hours=1)  # Expired 1 hour ago
        }
        expired_token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

        response = client.get(
            "/users/me",
            headers={"Authorization": f"Bearer {expired_token}"}
        )
        assert response.status_code == 401
        assert "expired" in response.json()["detail"].lower()

    def test_access_protected_endpoint_with_invalid_token(self, client):
        """Test accessing protected endpoint with malformed token."""
        response = client.get(
            "/users/me",
            headers={"Authorization": "Bearer invalid.token.here"}
        )
        assert response.status_code == 401
```

### Task 1.3: Test Prediction Endpoints

**File**: `test_predictions.py`

```python
"""Unit tests for prediction endpoints."""

import pytest
import numpy as np
from unittest.mock import patch, MagicMock

class TestSinglePrediction:
    """Tests for single prediction endpoint."""

    def test_predict_success(self, client, auth_headers, test_model):
        """Test successful prediction."""
        features = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]

        # Mock model.predict to avoid loading actual model
        with patch('app.model') as mock_model:
            mock_model.predict.return_value = np.array([0.85])

            response = client.post(
                "/predict",
                json={"features": features},
                headers=auth_headers
            )

        assert response.status_code == 200
        data = response.json()
        assert "prediction" in data
        assert isinstance(data["prediction"], float)
        assert data["model_version"] == test_model.version

    def test_predict_invalid_feature_count(self, client, auth_headers):
        """Test prediction with wrong number of features."""
        features = [1.0, 2.0, 3.0]  # Only 3 features, need 10

        response = client.post(
            "/predict",
            json={"features": features},
            headers=auth_headers
        )

        assert response.status_code == 422  # Validation error
        assert "10" in str(response.json())  # Error mentions required count

    def test_predict_invalid_feature_types(self, client, auth_headers):
        """Test prediction with non-numeric features."""
        features = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j"]

        response = client.post(
            "/predict",
            json={"features": features},
            headers=auth_headers
        )

        assert response.status_code == 422

    def test_predict_missing_features(self, client, auth_headers):
        """Test prediction without features field."""
        response = client.post(
            "/predict",
            json={},
            headers=auth_headers
        )

        assert response.status_code == 422

    def test_predict_caching(self, client, auth_headers):
        """Test that repeated predictions are cached."""
        features = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]

        with patch('app.model') as mock_model:
            mock_model.predict.return_value = np.array([0.85])

            # First request
            response1 = client.post(
                "/predict",
                json={"features": features},
                headers=auth_headers
            )
            assert response1.json()["cached"] == False

            # Second request (should be cached)
            response2 = client.post(
                "/predict",
                json={"features": features},
                headers=auth_headers
            )
            assert response2.json()["cached"] == True

            # Model should only be called once
            assert mock_model.predict.call_count == 1

    def test_predict_unauthorized(self, client):
        """Test prediction without authentication."""
        features = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]

        response = client.post(
            "/predict",
            json={"features": features}
        )

        assert response.status_code == 401

class TestBatchPrediction:
    """Tests for batch prediction endpoint."""

    def test_batch_predict_success(self, client, auth_headers):
        """Test successful batch prediction."""
        samples = [
            [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0],
            [2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0],
        ]

        with patch('app.model') as mock_model:
            mock_model.predict.return_value = np.array([0.85, 0.92])

            response = client.post(
                "/batch-predict",
                json={"samples": samples},
                headers=auth_headers
            )

        assert response.status_code == 200
        data = response.json()
        assert len(data["predictions"]) == 2
        assert data["count"] == 2

    def test_batch_predict_exceeds_max_samples(self, client, auth_headers):
        """Test batch prediction with too many samples."""
        samples = [[float(i)] * 10 for i in range(101)]  # 101 samples, max is 100

        response = client.post(
            "/batch-predict",
            json={"samples": samples},
            headers=auth_headers
        )

        assert response.status_code == 422

    @pytest.mark.parametrize("invalid_samples", [
        [],  # Empty list
        [[1.0, 2.0]],  # Wrong feature count
        [[]],  # Empty sample
        "not a list",  # Wrong type
    ])
    def test_batch_predict_validation(self, client, auth_headers, invalid_samples):
        """Test batch prediction input validation."""
        response = client.post(
            "/batch-predict",
            json={"samples": invalid_samples},
            headers=auth_headers
        )

        assert response.status_code == 422

# TODO: Add tests for:
# - Model loading errors
# - Prediction errors/exceptions
# - Response time under load
# - Memory usage with large batches
```

### Task 1.4: Test Coverage Analysis

**File**: `pytest.ini`

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    --verbose
    --cov=app
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=80
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
    unit: marks tests as unit tests
```

**TODO**: Run tests and achieve 80%+ coverage:

```bash
# Run all tests with coverage
pytest

# Run only unit tests
pytest -m unit

# Generate HTML coverage report
pytest --cov-report=html
open htmlcov/index.html

# TODO: Record your coverage results:
# Total coverage: ___%
# Missing coverage in: ___
```

---

## Part 2: Integration Testing

### Task 2.1: End-to-End Workflow Tests

**File**: `test_integration.py`

```python
"""Integration tests for complete workflows."""

import pytest

@pytest.mark.integration
class TestCompleteAuthFlow:
    """Test complete authentication workflow."""

    def test_register_login_access_flow(self, client):
        """Test user registration → login → access protected resource."""
        # Step 1: Register new user
        response = client.post(
            "/auth/register",
            json={
                "username": "newuser",
                "email": "new@example.com",
                "password": "securepassword123"
            }
        )
        assert response.status_code == 201

        # Step 2: Login with new account
        response = client.post(
            "/auth/login",
            json={
                "username": "newuser",
                "password": "securepassword123"
            }
        )
        assert response.status_code == 200
        token = response.json()["access_token"]

        # Step 3: Access protected resource
        response = client.get(
            "/users/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        assert response.json()["username"] == "newuser"

@pytest.mark.integration
class TestMLPipelineFlow:
    """Test complete ML prediction pipeline."""

    def test_full_prediction_pipeline(self, client, auth_headers, test_model):
        """Test: login → upload model → predict → get history."""
        # Step 1: Check model info
        response = client.get("/models", headers=auth_headers)
        assert response.status_code == 200
        models = response.json()
        assert len(models) >= 1

        # Step 2: Make prediction
        features = [1.0] * 10
        with patch('app.model') as mock_model:
            mock_model.predict.return_value = np.array([0.85])

            response = client.post(
                "/predict",
                json={"features": features},
                headers=auth_headers
            )
        assert response.status_code == 200
        prediction_id = response.json().get("id")

        # Step 3: Get prediction history
        response = client.get("/predictions/history", headers=auth_headers)
        assert response.status_code == 200
        history = response.json()
        assert len(history) >= 1

        # Step 4: Get specific prediction
        if prediction_id:
            response = client.get(
                f"/predictions/{prediction_id}",
                headers=auth_headers
            )
            assert response.status_code == 200

    def test_batch_prediction_with_feedback(self, client, auth_headers):
        """Test batch prediction with feedback loop."""
        # Step 1: Batch predict
        samples = [[float(i)] * 10 for i in range(5)]

        with patch('app.model') as mock_model:
            mock_model.predict.return_value = np.array([0.1, 0.3, 0.5, 0.7, 0.9])

            response = client.post(
                "/batch-predict",
                json={"samples": samples},
                headers=auth_headers
            )

        assert response.status_code == 200
        predictions = response.json()["predictions"]

        # Step 2: Submit feedback on predictions
        for i, pred in enumerate(predictions):
            response = client.post(
                "/feedback",
                json={
                    "prediction_value": pred,
                    "actual_value": pred + 0.1,  # Simulated ground truth
                    "feedback_score": 5
                },
                headers=auth_headers
            )
            # TODO: Add assertion

@pytest.mark.integration
class TestErrorRecovery:
    """Test error handling and recovery."""

    def test_database_connection_error_recovery(self, client, auth_headers):
        """Test API behavior when database is unavailable."""
        # TODO: Mock database error and verify graceful degradation
        pass

    def test_model_loading_error_fallback(self, client, auth_headers):
        """Test fallback behavior when model fails to load."""
        # TODO: Simulate model loading error and verify fallback
        pass
```

### Task 2.2: Database Integration Tests

**File**: `test_database.py`

```python
"""Integration tests for database operations."""

import pytest
from sqlalchemy.exc import IntegrityError

@pytest.mark.integration
class TestDatabaseConstraints:
    """Test database integrity constraints."""

    def test_unique_username_constraint(self, db):
        """Test that duplicate usernames are rejected."""
        from database import User

        # Create first user
        user1 = User(username="testuser", email="test1@example.com")
        db.add(user1)
        db.commit()

        # Try to create duplicate username
        user2 = User(username="testuser", email="test2@example.com")
        db.add(user2)

        with pytest.raises(IntegrityError):
            db.commit()

    def test_cascade_delete(self, db, test_user):
        """Test that deleting user cascades to related records."""
        from database import Prediction

        # Create predictions for user
        for i in range(5):
            pred = Prediction(user_id=test_user.id, value=float(i))
            db.add(pred)
        db.commit()

        # Delete user
        db.delete(test_user)
        db.commit()

        # Verify predictions are also deleted
        remaining = db.query(Prediction).filter(
            Prediction.user_id == test_user.id
        ).count()
        assert remaining == 0

@pytest.mark.integration
class TestDatabaseTransactions:
    """Test transaction handling."""

    def test_transaction_rollback_on_error(self, db):
        """Test that errors roll back transactions."""
        from database import User

        initial_count = db.query(User).count()

        try:
            # Create user
            user = User(username="testuser", email="test@example.com")
            db.add(user)

            # Cause an error
            raise ValueError("Simulated error")

        except ValueError:
            db.rollback()

        # Verify no user was created
        final_count = db.query(User).count()
        assert final_count == initial_count
```

---

## Part 3: Contract Testing

### Task 3.1: OpenAPI Schema Validation

**File**: `test_contracts.py`

```python
"""Contract tests using OpenAPI schema."""

import pytest
from openapi_spec_validator import validate_spec
from openapi_spec_validator.readers import read_from_filename
import json

class TestOpenAPISchema:
    """Validate API conforms to OpenAPI spec."""

    def test_openapi_spec_is_valid(self, client):
        """Test that generated OpenAPI spec is valid."""
        response = client.get("/openapi.json")
        assert response.status_code == 200

        spec = response.json()

        # Validate spec structure
        assert "openapi" in spec
        assert "info" in spec
        assert "paths" in spec

        # Validate spec is valid OpenAPI 3.0
        try:
            validate_spec(spec)
        except Exception as e:
            pytest.fail(f"OpenAPI spec validation failed: {e}")

    def test_all_endpoints_documented(self, client):
        """Test that all endpoints are in OpenAPI spec."""
        response = client.get("/openapi.json")
        spec = response.json()
        paths = spec["paths"]

        # Expected endpoints
        expected = [
            "/auth/login",
            "/predict",
            "/batch-predict",
            "/models",
            "/health"
        ]

        for endpoint in expected:
            assert endpoint in paths, f"Endpoint {endpoint} not documented"

    def test_response_matches_schema(self, client, auth_headers):
        """Test that actual responses match declared schema."""
        # Get OpenAPI schema for /predict endpoint
        response = client.get("/openapi.json")
        spec = response.json()
        predict_schema = spec["paths"]["/predict"]["post"]["responses"]["200"]

        # Make actual request
        with patch('app.model') as mock_model:
            mock_model.predict.return_value = np.array([0.85])

            response = client.post(
                "/predict",
                json={"features": [1.0] * 10},
                headers=auth_headers
            )

        # Validate response matches schema
        # TODO: Implement schema validation using jsonschema library
        from jsonschema import validate as validate_json

        response_data = response.json()
        # validate_json(response_data, predict_schema["content"]["application/json"]["schema"])

class TestBackwardCompatibility:
    """Test API backward compatibility."""

    def test_response_contains_required_fields(self, client, auth_headers):
        """Test that responses always include required fields."""
        with patch('app.model') as mock_model:
            mock_model.predict.return_value = np.array([0.85])

            response = client.post(
                "/predict",
                json={"features": [1.0] * 10},
                headers=auth_headers
            )

        data = response.json()

        # Required fields that must never be removed
        required_fields = ["prediction", "model_version"]
        for field in required_fields:
            assert field in data, f"Required field '{field}' missing"

    def test_optional_fields_dont_break_clients(self, client, auth_headers):
        """Test that adding new optional fields doesn't break existing clients."""
        # Simulate old client that only expects certain fields
        expected_fields = {"prediction", "model_version"}

        with patch('app.model') as mock_model:
            mock_model.predict.return_value = np.array([0.85])

            response = client.post(
                "/predict",
                json={"features": [1.0] * 10},
                headers=auth_headers
            )

        data = response.json()
        actual_fields = set(data.keys())

        # All expected fields should be present
        assert expected_fields.issubset(actual_fields)

        # Additional fields are OK (backward compatible)
        extra_fields = actual_fields - expected_fields
        print(f"Extra fields (backward compatible): {extra_fields}")
```

---

## Part 4: Load Testing

### Task 4.1: Create Locust Load Test

**File**: `locustfile.py`

```python
"""Load testing scenarios with Locust."""

from locust import HttpUser, task, between, events
import random

class MLAPIUser(HttpUser):
    """Simulate users making prediction requests."""

    wait_time = between(1, 3)  # Wait 1-3 seconds between requests
    token = None

    def on_start(self):
        """Login and get token when user starts."""
        response = self.client.post(
            "/auth/login",
            json={"username": "testuser", "password": "testpassword123"}
        )

        if response.status_code == 200:
            self.token = response.json()["access_token"]

    @task(10)  # Weight: 10 (most common)
    def predict_single(self):
        """Make single prediction request."""
        if not self.token:
            return

        features = [random.random() for _ in range(10)]

        with self.client.post(
            "/predict",
            json={"features": features},
            headers={"Authorization": f"Bearer {self.token}"},
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if "prediction" in data:
                    response.success()
                else:
                    response.failure("Missing prediction field")
            else:
                response.failure(f"Got status {response.status_code}")

    @task(3)  # Weight: 3 (less common)
    def predict_batch(self):
        """Make batch prediction request."""
        if not self.token:
            return

        batch_size = random.randint(5, 20)
        samples = [[random.random() for _ in range(10)] for _ in range(batch_size)]

        with self.client.post(
            "/batch-predict",
            json={"samples": samples},
            headers={"Authorization": f"Bearer {self.token}"},
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if len(data["predictions"]) == batch_size:
                    response.success()
                else:
                    response.failure("Prediction count mismatch")
            else:
                response.failure(f"Got status {response.status_code}")

    @task(1)  # Weight: 1 (rare)
    def get_model_info(self):
        """Get model information."""
        with self.client.get("/models", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Got status {response.status_code}")

@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Called when test starts."""
    print("Load test starting...")

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Called when test stops - print summary."""
    print(f"\nLoad test completed!")
    print(f"Total requests: {environment.stats.total.num_requests}")
    print(f"Total failures: {environment.stats.total.num_failures}")
    print(f"Average response time: {environment.stats.total.avg_response_time:.2f}ms")
    print(f"P95 response time: {environment.stats.total.get_response_time_percentile(0.95):.2f}ms")
```

**TODO**: Run load tests and record results:

```bash
# Start API
uvicorn app:app --host 0.0.0.0 --port 8000

# Run Locust
locust -f locustfile.py --host http://localhost:8000

# Open browser: http://localhost:8089
# Configure:
#   - Number of users: 100
#   - Spawn rate: 10 users/second
#   - Run time: 5 minutes

# Record results:
# - RPS: ___
# - P95 latency: ___ ms
# - P99 latency: ___ ms
# - Failure rate: ___%
# - Meets SLA (<100ms p95)?: Yes/No
```

### Task 4.2: Stress Testing

**File**: `stress_test.py`

```python
"""Stress tests to find breaking points."""

import pytest
import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import statistics

@pytest.mark.slow
def test_concurrent_requests_stress():
    """Test API under high concurrency."""
    url = "http://localhost:8000"

    # Get token
    response = requests.post(
        f"{url}/auth/login",
        json={"username": "testuser", "password": "testpassword123"}
    )
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Stress test parameters
    num_requests = 1000
    max_workers = 100

    latencies = []
    errors = 0

    def make_request(i):
        try:
            start = time.time()
            response = requests.post(
                f"{url}/predict",
                json={"features": [float(i % 10)] * 10},
                headers=headers,
                timeout=5
            )
            latency = time.time() - start

            if response.status_code == 200:
                return ("success", latency)
            else:
                return ("error", latency)
        except Exception as e:
            return ("exception", 0)

    # Execute stress test
    print(f"\n🔥 Stress test: {num_requests} requests, {max_workers} concurrent")
    start_time = time.time()

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(make_request, i) for i in range(num_requests)]

        for future in as_completed(futures):
            status, latency = future.result()
            if status == "success":
                latencies.append(latency)
            else:
                errors += 1

    total_time = time.time() - start_time

    # Results
    print(f"\n📊 Results:")
    print(f"   Total time: {total_time:.2f}s")
    print(f"   Throughput: {num_requests / total_time:.2f} req/sec")
    print(f"   Successful: {len(latencies)}")
    print(f"   Errors: {errors}")
    print(f"   Error rate: {errors/num_requests*100:.2f}%")

    if latencies:
        print(f"   Avg latency: {statistics.mean(latencies)*1000:.2f}ms")
        print(f"   P50 latency: {statistics.median(latencies)*1000:.2f}ms")
        sorted_latencies = sorted(latencies)
        print(f"   P95 latency: {sorted_latencies[int(0.95*len(sorted_latencies))]*1000:.2f}ms")
        print(f"   P99 latency: {sorted_latencies[int(0.99*len(sorted_latencies))]*1000:.2f}ms")

    # Assertions
    assert errors / num_requests < 0.01, "Error rate > 1%"
    assert statistics.median(latencies) < 0.5, "P50 latency > 500ms"

@pytest.mark.slow
def test_sustained_load():
    """Test API under sustained load for 5 minutes."""
    # TODO: Implement sustained load test
    # Run moderate load for extended period
    # Monitor memory usage, check for leaks
    # Verify performance doesn't degrade over time
    pass
```

---

## Part 5: CI/CD Integration

### Task 5.1: GitHub Actions Workflow

**File**: `.github/workflows/test.yml`

```yaml
name: API Testing Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  unit-tests:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          cache: 'pip'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt

      - name: Run unit tests
        run: |
          pytest tests/test_*.py -m "not slow and not integration" \
            --cov=app \
            --cov-report=xml \
            --cov-report=term

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
          fail_ci_if_error: true

  integration-tests:
    runs-on: ubuntu-latest
    needs: unit-tests

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt

      - name: Run integration tests
        run: |
          pytest tests/test_*.py -m integration

  contract-tests:
    runs-on: ubuntu-latest
    needs: unit-tests

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt

      - name: Run contract tests
        run: |
          pytest tests/test_contracts.py -v

      - name: Upload OpenAPI spec
        uses: actions/upload-artifact@v3
        with:
          name: openapi-spec
          path: openapi.json

  load-tests:
    runs-on: ubuntu-latest
    needs: [unit-tests, integration-tests]
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install locust

      - name: Start API
        run: |
          uvicorn app:app --host 0.0.0.0 --port 8000 &
          sleep 5

      - name: Run load tests
        run: |
          locust -f locustfile.py \
            --host http://localhost:8000 \
            --users 50 \
            --spawn-rate 5 \
            --run-time 2m \
            --headless \
            --only-summary

      - name: Check performance SLA
        run: |
          # TODO: Parse Locust output and verify P95 < 100ms
          python check_sla.py locust_stats.json
```

### Task 5.2: Pre-commit Hooks

**File**: `.pre-commit-config.yaml`

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files

  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
        language_version: python3.11

  - repo: https://github.com/PyCQA/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        args: ['--max-line-length=88']

  - repo: local
    hooks:
      - id: pytest-quick
        name: pytest-quick
        entry: pytest -m "not slow" --tb=short
        language: system
        pass_filenames: false
        always_run: true
```

---

## Deliverables

### Test Suite Documentation

```markdown
# API Test Suite Documentation

## Coverage Summary
- Unit tests: ___ tests
- Integration tests: ___ tests
- Contract tests: ___ tests
- Load tests: ___ scenarios
- Total coverage: ___%

## Running Tests

### All tests
\`\`\`bash
pytest
\`\`\`

### Specific test types
\`\`\`bash
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests
pytest -m "not slow"    # Skip slow tests
\`\`\`

### With coverage
\`\`\`bash
pytest --cov=app --cov-report=html
\`\`\`

### Load testing
\`\`\`bash
locust -f locustfile.py --host http://localhost:8000
\`\`\`

## Test Results
- All tests passing: ✅/❌
- Coverage goal met (80%+): ✅/❌
- Performance SLA met (<100ms p95): ✅/❌
- Contract tests passing: ✅/❌
```

---

## Success Criteria

- [ ] Unit test coverage ≥ 80%
- [ ] All integration tests pass
- [ ] Contract tests validate OpenAPI spec
- [ ] Load tests confirm API meets SLA (<100ms p95)
- [ ] CI/CD pipeline runs tests automatically
- [ ] Pre-commit hooks prevent bad commits
- [ ] Documentation complete

---

## Bonus Challenges

### Challenge 1: Chaos Testing

Simulate failures:
- Kill API process mid-request
- Corrupt database
- Overload CPU/memory

### Challenge 2: Security Testing

Add security tests:
- SQL injection attempts
- XSS attempts
- JWT token tampering
- Rate limit bypassing

### Challenge 3: Performance Profiling

Use `py-spy` to profile:
```bash
py-spy record -o profile.svg -- python -m pytest
```

---

## References

- **pytest documentation**: https://docs.pytest.org/
- **FastAPI testing**: https://fastapi.tiangolo.com/tutorial/testing/
- **Locust documentation**: https://docs.locust.io/
- **OpenAPI validation**: https://github.com/p1c2u/openapi-spec-validator

---

**Estimated Completion Time**: 3-4 hours

**Next Module**: Module 008 - Databases & SQL
