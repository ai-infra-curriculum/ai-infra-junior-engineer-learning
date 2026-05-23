# Lecture 05: Flask Framework

## Table of Contents
1. [Introduction](#introduction)
2. [What is Flask?](#what-is-flask)
3. [Flask vs FastAPI: When to Choose Which](#flask-vs-fastapi-when-to-choose-which)
4. [Installation and Project Layout](#installation-and-project-layout)
5. [Your First Flask Application](#your-first-flask-application)
6. [Routing and View Functions](#routing-and-view-functions)
7. [Request Handling](#request-handling)
8. [Response Construction](#response-construction)
9. [Application Factory Pattern and Blueprints](#application-factory-pattern-and-blueprints)
10. [Configuration Management](#configuration-management)
11. [Error Handling](#error-handling)
12. [Middleware and Hooks](#middleware-and-hooks)
13. [Flask Extensions](#flask-extensions)
14. [Building a Flask ML API](#building-a-flask-ml-api)
15. [Production Deployment](#production-deployment)
16. [Testing Flask Applications](#testing-flask-applications)
17. [Best Practices](#best-practices)
18. [Summary and Key Takeaways](#summary-and-key-takeaways)

## Introduction

Flask is a lightweight, mature Python web framework that has powered production APIs for over a decade. While newer frameworks like FastAPI have captured attention in the ML community, Flask remains widely used in legacy systems, internal tooling, and any context where a simple, unopinionated, battle-tested framework is preferred.

This lecture teaches Flask from the ground up, focused on the patterns you will actually encounter when deploying ML models behind Flask endpoints. By the end, you will be able to read existing Flask codebases, write new endpoints competently, and make an informed choice between Flask and FastAPI for new projects.

### Learning Objectives

By the end of this lecture, you will:
- Understand Flask's design philosophy and how it differs from FastAPI
- Set up a Flask project with the application factory pattern
- Define routes, view functions, and handle HTTP verbs correctly
- Parse request bodies, query strings, headers, and uploaded files
- Construct JSON, HTML, and streaming responses
- Organize larger applications using Blueprints
- Manage configuration safely across environments
- Handle errors with custom error pages and JSON error responses
- Use common extensions: Flask-RESTful, Flask-SQLAlchemy, Flask-CORS, Flask-Smorest
- Build a complete ML inference endpoint in Flask
- Deploy Flask behind Gunicorn or uWSGI
- Test Flask applications with pytest

### Prerequisites
- Module 001: Python Fundamentals
- Module 007 - Lecture 01: API Fundamentals & REST
- Module 007 - Lecture 02: FastAPI Framework (for comparison)
- Basic understanding of WSGI

### Estimated Time
3 hours (including hands-on coding)

---

## What is Flask?

Flask is a **WSGI microframework** for Python created by Armin Ronacher in 2010. The term "microframework" describes its philosophy: Flask provides the minimum needed to build a web application — routing, request/response objects, templating via Jinja2, and a development server — and leaves everything else (database access, authentication, form validation) to extensions or your own code.

### Key Characteristics

1. **Minimal core, large ecosystem.** Flask itself is small (a few thousand lines). Functionality is added through well-curated extensions like Flask-SQLAlchemy, Flask-Login, Flask-Smorest.
2. **WSGI-based.** Flask follows the Python Web Server Gateway Interface standard (PEP 3333), making it compatible with any WSGI server: Gunicorn, uWSGI, mod_wsgi, Waitress.
3. **Synchronous by default.** Each request is handled by a worker thread or process. Flask 2.0+ supports `async def` view functions but does not run on an event loop the way FastAPI does.
4. **Unopinionated.** Flask does not prescribe a project structure, ORM, or template engine. You assemble the stack you want.
5. **Mature and stable.** With over a decade of production use, the framework's API is unlikely to surprise you and documentation is abundant.

### Why Flask Still Matters in ML Infrastructure

- **Legacy systems.** Many production ML services predate FastAPI and run on Flask. Familiarity is non-negotiable when working on existing platforms.
- **Lightweight internal tools.** A simple admin endpoint, a model health checker, or a one-off batch trigger is often easier in Flask than in any heavier framework.
- **Operator familiarity.** Operations teams who have run Flask + Gunicorn for years have well-developed runbooks, alerting, and tuning knowledge.
- **WSGI ecosystem.** Tools like New Relic, Datadog APM, and many WAFs have first-class WSGI middleware support.
- **Stable patterns.** When you don't need async I/O or auto-generated docs, Flask's simplicity reduces cognitive overhead.

---

## Flask vs FastAPI: When to Choose Which

| Aspect | Flask | FastAPI |
|---|---|---|
| Style | WSGI, synchronous | ASGI, async-native |
| Speed | Adequate; bounded by sync I/O | Higher throughput for I/O-bound workloads |
| Type hints | Optional, not enforced | Required for routing/validation |
| Data validation | Manual or extensions (marshmallow, pydantic) | Built-in via Pydantic |
| Auto-docs | Via extensions (Flask-Smorest, apispec) | Built-in OpenAPI + Swagger UI |
| Async I/O | Limited (Flask 2.0+, but worker-bound) | First-class |
| Maturity | Very mature (since 2010) | Mature (since 2018), growing fast |
| Learning curve | Gentle | Slightly steeper (Pydantic, async) |
| Best fit | Internal tools, legacy services, simple APIs | High-concurrency ML serving, modern greenfield APIs |

### Decision Guide

**Choose Flask when:**
- You're working on an existing Flask codebase.
- Your endpoints are CPU-bound (model inference) rather than I/O-bound — async gives no benefit.
- The team is already deeply experienced with Flask + Gunicorn ops.
- You need a tiny, single-file service.

**Choose FastAPI when:**
- You're building a new high-traffic ML serving layer.
- Your workload is I/O-bound (database calls, calls to other services, streaming).
- You want auto-generated docs without configuring an extension.
- You want stricter input validation by default.

For model inference specifically, the difference is often modest: model latency dominates framework overhead. Pick the one the team will maintain best.

---

## Installation and Project Layout

```bash
# Recommended: create a virtual environment first
python -m venv .venv
source .venv/bin/activate

pip install flask
```

Minimal project structure for a small service:

```
myapi/
├── app.py
├── requirements.txt
└── tests/
    └── test_app.py
```

For anything that will outlive a prototype, use the application factory pattern (covered below):

```
myapi/
├── app/
│   ├── __init__.py          # create_app() factory
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── health.py
│   │   └── predict.py
│   ├── models/              # SQLAlchemy models, NOT ML models
│   ├── ml/
│   │   ├── loader.py
│   │   └── inference.py
│   ├── schemas.py           # marshmallow/pydantic
│   └── config.py
├── tests/
├── wsgi.py                  # Gunicorn entrypoint
└── requirements.txt
```

---

## Your First Flask Application

```python
# app.py
from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/")
def index():
    return jsonify(message="Hello, Flask")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
```

Run it:

```bash
python app.py
# or
flask --app app run --debug
```

Visit `http://localhost:8000/`.

### What's Happening

- `Flask(__name__)` creates the application object. The `__name__` argument tells Flask where to look for templates and static files.
- `@app.route("/")` is a decorator that registers `index` as the view function for the path `/`.
- `jsonify` converts a Python dict to a JSON response with `Content-Type: application/json`.
- `app.run(...)` starts the **development server only.** Never use it in production.

---

## Routing and View Functions

### HTTP Methods

By default, a route accepts only `GET`. Use the `methods` argument for others:

```python
@app.route("/predict", methods=["POST"])
def predict():
    ...

@app.route("/model/<model_id>", methods=["GET", "DELETE"])
def model(model_id):
    ...
```

You can also use the convenience decorators added in Flask 2.0:

```python
@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/predict")
def predict():
    ...
```

### URL Variables and Converters

```python
@app.get("/users/<int:user_id>")
def user(user_id: int):
    return {"id": user_id}

@app.get("/files/<path:filepath>")
def file(filepath: str):
    # 'path' converter allows slashes
    return {"path": filepath}
```

Built-in converters: `string` (default), `int`, `float`, `path`, `uuid`. Custom converters can be registered on `app.url_map.converters`.

### url_for() — Build URLs, Don't Hardcode

```python
from flask import url_for

@app.get("/")
def index():
    return {"predict_url": url_for("predict", _external=True)}
```

`url_for` looks up routes by view function name, so renaming a URL doesn't break links elsewhere.

---

## Request Handling

The request-bound `request` object exposes everything about the incoming request.

```python
from flask import request

@app.post("/predict")
def predict():
    # JSON body
    payload = request.get_json(silent=True) or {}

    # Query parameters: /predict?model=resnet50
    model_name = request.args.get("model", "default")

    # Headers
    auth = request.headers.get("Authorization")

    # Path
    path = request.path  # "/predict"

    # Form data
    # value = request.form["field_name"]

    # Uploaded file (multipart/form-data)
    # f = request.files["file"]
    # f.save("/tmp/upload.bin")

    return {"model": model_name, "received": payload}
```

### Parsing and Validating JSON

Raw `request.get_json()` returns whatever the client sent. You should validate. Two common approaches:

**Approach 1: Manual validation**

```python
@app.post("/predict")
def predict():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return {"error": "JSON object required"}, 400

    features = payload.get("features")
    if not isinstance(features, list) or len(features) != 10:
        return {"error": "features must be a list of length 10"}, 400

    return {"prediction": run_model(features)}
```

**Approach 2: marshmallow schema**

```python
from marshmallow import Schema, fields, ValidationError

class PredictRequest(Schema):
    features = fields.List(fields.Float(), required=True)
    model_version = fields.String(load_default="latest")

schema = PredictRequest()

@app.post("/predict")
def predict():
    try:
        data = schema.load(request.get_json() or {})
    except ValidationError as err:
        return {"errors": err.messages}, 400

    return {"prediction": run_model(data["features"], data["model_version"])}
```

For projects already using Pydantic, the `flask-pydantic` extension provides similar ergonomics.

---

## Response Construction

A view function can return:

```python
# Tuple: (body, status, headers)
return {"ok": True}, 201, {"X-Request-Id": "abc"}

# Dict — auto-converted to JSON (Flask 1.1+)
return {"ok": True}

# Flask Response object for full control
from flask import make_response
resp = make_response({"ok": True}, 200)
resp.headers["X-Request-Id"] = "abc"
return resp

# Streaming response (e.g., large inference batches)
from flask import Response
def generate():
    yield "["
    for i, result in enumerate(stream_predictions()):
        if i > 0: yield ","
        yield json.dumps(result)
    yield "]"
return Response(generate(), mimetype="application/json")
```

### Standard Status Codes

| Code | Use |
|---|---|
| 200 | Success with body |
| 201 | Resource created (POST to a collection) |
| 202 | Accepted, processing async |
| 204 | Success, no body |
| 400 | Bad client request (validation) |
| 401 | Unauthenticated |
| 403 | Authenticated but forbidden |
| 404 | Resource not found |
| 422 | Semantically invalid request |
| 500 | Server error |
| 503 | Temporarily unavailable (e.g., model not loaded) |

---

## Application Factory Pattern and Blueprints

For anything larger than a single file, organize with a factory and blueprints.

### Factory

```python
# app/__init__.py
from flask import Flask
from .config import load_config
from .routes.health import bp as health_bp
from .routes.predict import bp as predict_bp

def create_app(config_name: str = "default") -> Flask:
    app = Flask(__name__)
    app.config.update(load_config(config_name))

    app.register_blueprint(health_bp)
    app.register_blueprint(predict_bp, url_prefix="/v1")

    return app
```

### Blueprint

```python
# app/routes/predict.py
from flask import Blueprint, request, current_app

bp = Blueprint("predict", __name__)

@bp.post("/predict")
def predict():
    model = current_app.config["MODEL"]
    payload = request.get_json() or {}
    return {"prediction": model.predict(payload["features"])}
```

### WSGI Entry Point

```python
# wsgi.py
from app import create_app
app = create_app("production")
```

Run with Gunicorn:

```bash
gunicorn --workers 4 --bind 0.0.0.0:8000 wsgi:app
```

Benefits:
- Multiple app instances for tests with different configs.
- Clear separation of concerns by feature area.
- Easier to mount sub-apps and reuse routes.

---

## Configuration Management

Never hardcode secrets. Flask supports several config loading patterns.

```python
# Environment variables
app.config["MODEL_PATH"] = os.environ["MODEL_PATH"]
app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]

# From a Python class
class ProductionConfig:
    DEBUG = False
    MODEL_PATH = os.environ["MODEL_PATH"]
    LOG_LEVEL = "INFO"

app.config.from_object(ProductionConfig)

# From an env-prefixed loader (Flask 2.1+)
app.config.from_prefixed_env(prefix="MYAPI")
# MYAPI_MODEL_PATH=/models/v1 → app.config["MODEL_PATH"]
```

For production, prefer environment variables managed by your orchestrator (Kubernetes secrets, AWS Secrets Manager). Never commit a `.env` with real secrets.

---

## Error Handling

### Custom Error Pages and JSON Errors

```python
from werkzeug.exceptions import HTTPException

@app.errorhandler(HTTPException)
def handle_http_error(err):
    return {
        "error": err.name,
        "detail": err.description,
        "status": err.code,
    }, err.code

@app.errorhandler(Exception)
def handle_unexpected(err):
    app.logger.exception("Unhandled error")
    return {"error": "internal_server_error"}, 500
```

### Aborting Early

```python
from flask import abort

@app.get("/models/<model_id>")
def get_model(model_id):
    model = registry.find(model_id)
    if model is None:
        abort(404, description=f"Model '{model_id}' not found")
    return model.to_dict()
```

---

## Middleware and Hooks

Flask calls these "request hooks":

```python
@app.before_request
def log_request():
    app.logger.info("%s %s", request.method, request.path)

@app.after_request
def add_request_id(response):
    response.headers["X-Request-Id"] = request.headers.get("X-Request-Id", uuid.uuid4().hex)
    return response

@app.teardown_request
def cleanup(exc):
    # Always runs, even on exception. Close DB sessions here.
    pass
```

For true WSGI middleware (e.g., Prometheus instrumentation), wrap `app.wsgi_app`:

```python
from werkzeug.middleware.proxy_fix import ProxyFix
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1)
```

---

## Flask Extensions

The Flask ecosystem includes many high-quality extensions. The ones you'll meet most often in ML infrastructure:

| Extension | Purpose |
|---|---|
| **Flask-SQLAlchemy** | ORM integration for relational databases |
| **Flask-Migrate** | Alembic-backed schema migrations |
| **Flask-Smorest** | OpenAPI generation + marshmallow integration (closest analog to FastAPI's auto-docs) |
| **Flask-RESTful** | Class-based resource routing (older, still common) |
| **Flask-CORS** | Cross-origin request handling |
| **Flask-Login** | Session-based user authentication |
| **Flask-JWT-Extended** | JWT-based authentication |
| **Flask-Limiter** | Rate limiting |
| **prometheus-flask-exporter** | `/metrics` endpoint for Prometheus scraping |

### Example: Flask-Smorest for Auto-Generated Docs

```python
from flask import Flask
from flask_smorest import Api, Blueprint
from marshmallow import Schema, fields

app = Flask(__name__)
app.config["API_TITLE"] = "Model API"
app.config["API_VERSION"] = "v1"
app.config["OPENAPI_VERSION"] = "3.0.3"
app.config["OPENAPI_URL_PREFIX"] = "/"
app.config["OPENAPI_SWAGGER_UI_PATH"] = "/docs"
app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"

api = Api(app)
blp = Blueprint("predict", "predict", url_prefix="/v1")

class PredictIn(Schema):
    features = fields.List(fields.Float(), required=True)

class PredictOut(Schema):
    prediction = fields.Float()

@blp.route("/predict", methods=["POST"])
@blp.arguments(PredictIn)
@blp.response(200, PredictOut)
def predict(payload):
    return {"prediction": sum(payload["features"]) / len(payload["features"])}

api.register_blueprint(blp)
```

Visit `/docs` and you'll have a Swagger UI comparable to FastAPI's.

### Example: Prometheus Metrics

```python
from prometheus_flask_exporter import PrometheusMetrics

metrics = PrometheusMetrics(app)
metrics.info("app_info", "Model API", version="1.0.0")
```

This exposes `/metrics` with request counts, latencies, and exception counters — ready for Prometheus to scrape.

---

## Building a Flask ML API

A realistic minimal ML serving endpoint:

```python
# app/ml/loader.py
import joblib
from threading import Lock

_lock = Lock()
_model = None

def get_model(model_path: str):
    global _model
    with _lock:
        if _model is None:
            _model = joblib.load(model_path)
        return _model
```

```python
# app/routes/predict.py
from flask import Blueprint, request, current_app, abort
from marshmallow import Schema, fields, ValidationError
import time

from ..ml.loader import get_model

bp = Blueprint("predict", __name__)

class PredictRequest(Schema):
    features = fields.List(fields.Float(), required=True)

schema = PredictRequest()

@bp.post("/predict")
def predict():
    try:
        data = schema.load(request.get_json() or {})
    except ValidationError as err:
        return {"errors": err.messages}, 400

    if len(data["features"]) != current_app.config["FEATURE_COUNT"]:
        abort(400, description="wrong feature count")

    model = get_model(current_app.config["MODEL_PATH"])

    start = time.perf_counter()
    pred = model.predict([data["features"]])[0]
    elapsed_ms = (time.perf_counter() - start) * 1000

    return {
        "prediction": float(pred),
        "latency_ms": round(elapsed_ms, 2),
    }
```

```python
# app/__init__.py
from flask import Flask
from prometheus_flask_exporter import PrometheusMetrics

def create_app(config):
    app = Flask(__name__)
    app.config.update(config)

    from .routes.predict import bp as predict_bp
    app.register_blueprint(predict_bp, url_prefix="/v1")

    PrometheusMetrics(app)

    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app
```

### Important Considerations for ML in Flask

1. **Model loading.** Load the model once at startup or lazily on first request, behind a lock. Never reload per request.
2. **Worker model.** Each Gunicorn worker is a separate Python process with its own model copy. Plan memory accordingly.
3. **GIL and CPU work.** Inference is usually CPU-bound, which means the GIL serializes work within a worker. For higher throughput, increase worker count rather than threads.
4. **Cold start.** First request after process start pays the model-load cost. Use a readiness probe that warms the model before traffic arrives.
5. **Batch endpoints.** For high throughput, accept a batch of inputs per request instead of one prediction per request.

---

## Production Deployment

The Flask development server is not for production. Use a WSGI server like Gunicorn:

```bash
gunicorn \
  --workers 4 \
  --threads 2 \
  --bind 0.0.0.0:8000 \
  --timeout 60 \
  --access-logfile - \
  --error-logfile - \
  wsgi:app
```

### Worker Tuning

- **Workers**: Start at `(2 × CPU cores) + 1` for I/O-bound workloads. For CPU-bound ML inference, use `CPU cores`, sometimes fewer.
- **Threads**: Useful for I/O-bound work; less so for CPU-bound inference due to the GIL.
- **Timeout**: Set above your p99 inference latency; below your load balancer's request timeout.

### Behind a Reverse Proxy

Run NGINX or a cloud load balancer in front of Gunicorn for TLS termination, static asset serving, and connection pooling. Tell Flask to trust forwarded headers using `werkzeug.middleware.proxy_fix.ProxyFix`.

### Containerizing

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

ENV PYTHONUNBUFFERED=1
EXPOSE 8000

CMD ["gunicorn", "--workers", "4", "--bind", "0.0.0.0:8000", "wsgi:app"]
```

---

## Testing Flask Applications

Flask provides a test client that runs your app in-process — no real network:

```python
# tests/test_predict.py
import pytest
from app import create_app

@pytest.fixture
def client():
    app = create_app({"TESTING": True, "MODEL_PATH": "tests/fixtures/model.joblib", "FEATURE_COUNT": 4})
    with app.test_client() as c:
        yield c

def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.get_json() == {"status": "ok"}

def test_predict_happy_path(client):
    r = client.post("/v1/predict", json={"features": [1.0, 2.0, 3.0, 4.0]})
    assert r.status_code == 200
    body = r.get_json()
    assert "prediction" in body
    assert isinstance(body["prediction"], float)

def test_predict_validation(client):
    r = client.post("/v1/predict", json={"features": "not a list"})
    assert r.status_code == 400
```

Run with `pytest`. For load testing, use Locust (covered in `04-api-testing.md` exercises).

---

## Best Practices

1. **Use the application factory.** Avoid module-level state that depends on environment.
2. **Keep view functions thin.** Push business logic into separate modules.
3. **Validate input.** Reject bad requests at the boundary with 400, never let bad data hit your model.
4. **Return structured errors.** A consistent JSON error shape (`{"error": "...", "detail": "..."}`) is easier to consume.
5. **Log structured.** Use `app.logger` with JSON formatting in production.
6. **Instrument everything.** Add Prometheus metrics, distributed tracing, and structured request logs from day one.
7. **Never run the dev server in production.** Always use Gunicorn or uWSGI.
8. **Pin dependencies.** Use `requirements.txt` with explicit versions, generated by `pip-compile` or `poetry export`.
9. **Health and readiness endpoints.** `/health` is always 200 if the process is up. `/ready` is 200 only when the model is loaded and dependencies are reachable.
10. **Graceful shutdown.** Gunicorn handles `SIGTERM`. Make sure long-running predictions finish or are cancelled cleanly.

---

## Summary and Key Takeaways

- Flask is a synchronous WSGI microframework — minimal core, extensions for everything else.
- Choose Flask for simple services, legacy systems, and CPU-bound ML inference where async gives no benefit.
- Use the application factory + blueprints for anything past a prototype.
- Validate input with marshmallow, pydantic, or manual checks. Don't trust JSON payloads.
- For auto-generated docs comparable to FastAPI, use **Flask-Smorest**.
- Load ML models once per worker; never reload per request.
- Deploy with Gunicorn behind NGINX or a cloud load balancer. Never use the development server in production.
- Test with `app.test_client()` — fast, in-process, no network.
- Instrument with `prometheus-flask-exporter` and structured logs from the start.

In the next module you will containerize this same Flask service and deploy it to Kubernetes alongside the FastAPI variant, allowing direct comparison of operations characteristics.
