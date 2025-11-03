# Exercise 07: NoSQL Databases for Machine Learning

## Overview
Explore NoSQL database systems (MongoDB, Redis) and evaluate when to use them versus traditional SQL databases for ML infrastructure. Build a hybrid system that leverages the strengths of both SQL and NoSQL databases for different aspects of an ML platform.

**Duration:** 3-4 hours
**Difficulty:** Intermediate

## Learning Objectives
By completing this exercise, you will:
- Understand the trade-offs between SQL and NoSQL databases
- Work with document databases (MongoDB) for flexible ML metadata
- Use key-value stores (Redis) for high-performance caching and feature serving
- Design hybrid architectures that combine SQL and NoSQL
- Implement data migration strategies between database types
- Choose appropriate database technologies for specific ML use cases

## Prerequisites
- Docker and Docker Compose installed
- Python 3.8+
- Understanding of SQL basics from previous exercises
- Familiarity with JSON data structures

## Scenario
You're building an **ML Platform** that needs to handle diverse data types:
- **Model metadata** with varying schemas (different frameworks have different configs)
- **Real-time feature serving** requiring <10ms latency
- **Experiment tracking** with flexible, nested parameters
- **Structured training data** requiring complex queries and joins

No single database type handles all these requirements optimally. You'll build a hybrid system using:
- **PostgreSQL** for structured data requiring transactions and complex queries
- **MongoDB** for flexible, document-based ML metadata
- **Redis** for high-speed caching and feature stores

## Tasks

### Task 1: Environment Setup with Docker Compose

**TODO 1.1:** Create Docker Compose configuration for multi-database setup

```yaml
# docker-compose.yml
version: '3.8'

services:
  postgres:
    image: postgres:15
    container_name: ml-postgres
    environment:
      POSTGRES_USER: mluser
      POSTGRES_PASSWORD: mlpass123
      POSTGRES_DB: ml_platform
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U mluser"]
      interval: 10s
      timeout: 5s
      retries: 5

  mongodb:
    image: mongo:7
    container_name: ml-mongodb
    environment:
      MONGO_INITDB_ROOT_USERNAME: mluser
      MONGO_INITDB_ROOT_PASSWORD: mlpass123
      MONGO_INITDB_DATABASE: ml_metadata
    ports:
      - "27017:27017"
    volumes:
      - mongo_data:/data/db
    healthcheck:
      test: ["CMD", "mongosh", "--eval", "db.adminCommand('ping')"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: ml-redis
    command: redis-server --requirepass mlpass123 --maxmemory 256mb --maxmemory-policy allkeys-lru
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "-a", "mlpass123", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
  mongo_data:
  redis_data:
```

**TODO 1.2:** Start the multi-database environment

```bash
# Start all databases
docker-compose up -d

# TODO: Verify all services are healthy
docker-compose ps

# Expected output: All services showing "healthy" status
```

**TODO 1.3:** Install Python database clients

```bash
# TODO: Create requirements.txt
cat > requirements.txt << EOF
psycopg2-binary>=2.9.0
sqlalchemy>=2.0.0
pymongo>=4.5.0
redis>=5.0.0
numpy>=1.24.0
pandas>=2.0.0
pydantic>=2.0.0
EOF

# Install dependencies
pip install -r requirements.txt
```

### Task 2: PostgreSQL for Structured ML Data

**TODO 2.1:** Create schema for structured training datasets

```python
# postgres_setup.py
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

PG_URL = "postgresql://mluser:mlpass123@localhost:5432/ml_platform"
engine = create_engine(PG_URL)

def setup_postgres_schema():
    """Create tables for structured ML platform data."""
    with engine.connect() as conn:
        # TODO: Create datasets table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS datasets (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) UNIQUE NOT NULL,
                description TEXT,
                total_rows INTEGER,
                total_features INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by VARCHAR(100)
            )
        """))

        # TODO: Create training_runs table (structured data)
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS training_runs (
                id SERIAL PRIMARY KEY,
                dataset_id INTEGER REFERENCES datasets(id),
                model_name VARCHAR(255),
                framework VARCHAR(50),
                status VARCHAR(20) DEFAULT 'running',
                accuracy FLOAT,
                loss FLOAT,
                training_time_seconds INTEGER,
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP
            )
        """))

        # TODO: Create indexes for common queries
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_training_runs_status
            ON training_runs(status)
        """))

        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_training_runs_model
            ON training_runs(model_name)
        """))

        conn.commit()
        print("✓ PostgreSQL schema created")

# TODO: Insert sample data
def insert_sample_data():
    with engine.connect() as conn:
        conn.execute(text("""
            INSERT INTO datasets (name, description, total_rows, total_features, created_by)
            VALUES
                ('fraud-train-v1', 'Credit card fraud detection dataset', 284807, 30, 'alice'),
                ('recommendation-train-v2', 'User-item interaction dataset', 10000000, 50, 'bob')
            ON CONFLICT (name) DO NOTHING
        """))

        conn.execute(text("""
            INSERT INTO training_runs (dataset_id, model_name, framework, status, accuracy, loss, training_time_seconds)
            VALUES
                (1, 'fraud-detector-v1', 'pytorch', 'completed', 0.9845, 0.042, 3600),
                (1, 'fraud-detector-v2', 'tensorflow', 'completed', 0.9821, 0.051, 4200),
                (2, 'recommender-model', 'pytorch', 'running', NULL, NULL, NULL)
        """))

        conn.commit()
        print("✓ Sample data inserted")

if __name__ == "__main__":
    setup_postgres_schema()
    insert_sample_data()
```

**TODO 2.2:** Implement complex analytical queries

```python
# postgres_queries.py
from postgres_setup import engine
from sqlalchemy import text

def get_top_models_by_accuracy(top_n: int = 5):
    """
    SQL excels at aggregations and complex filtering.
    Get top N models by accuracy across all datasets.
    """
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT
                tr.model_name,
                d.name as dataset_name,
                tr.framework,
                tr.accuracy,
                tr.training_time_seconds,
                ROUND(tr.accuracy / (tr.training_time_seconds / 3600.0), 4) as accuracy_per_hour
            FROM training_runs tr
            JOIN datasets d ON tr.dataset_id = d.id
            WHERE tr.status = 'completed'
            ORDER BY tr.accuracy DESC
            LIMIT :top_n
        """), {"top_n": top_n})

        print(f"\n=== Top {top_n} Models by Accuracy ===")
        for row in result:
            print(f"  {row[0]:<30} | {row[1]:<25} | {row[2]:<12} | Acc: {row[3]:.4f} | Time: {row[4]}s | Acc/hr: {row[5]}")

def get_framework_comparison():
    """
    Aggregation query: Compare frameworks by average performance.
    """
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT
                framework,
                COUNT(*) as total_runs,
                ROUND(AVG(accuracy)::numeric, 4) as avg_accuracy,
                ROUND(AVG(training_time_seconds)::numeric, 2) as avg_training_time
            FROM training_runs
            WHERE status = 'completed'
            GROUP BY framework
            ORDER BY avg_accuracy DESC
        """))

        print("\n=== Framework Performance Comparison ===")
        for row in result:
            print(f"  {row[0]:<15} | Runs: {row[1]} | Avg Accuracy: {row[2]} | Avg Time: {row[3]}s")

# TODO: Run queries
if __name__ == "__main__":
    get_top_models_by_accuracy()
    get_framework_comparison()
```

### Task 3: MongoDB for Flexible ML Metadata

**TODO 3.1:** Set up MongoDB connection and collections

```python
# mongodb_setup.py
from pymongo import MongoClient
from datetime import datetime
import json

MONGO_URL = "mongodb://mluser:mlpass123@localhost:27017/"
client = MongoClient(MONGO_URL)
db = client.ml_metadata

def setup_mongodb_collections():
    """
    Document databases excel at flexible schemas.
    Different model types can have completely different metadata structures.
    """
    # TODO: Create collections with validation
    try:
        db.create_collection("model_configs", validator={
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["model_id", "model_name", "framework"],
                "properties": {
                    "model_id": {"bsonType": "string"},
                    "model_name": {"bsonType": "string"},
                    "framework": {"bsonType": "string"},
                    "config": {"bsonType": "object"}  # Flexible nested config
                }
            }
        })
        print("✓ Created model_configs collection")
    except Exception as e:
        print(f"Collection already exists or error: {e}")

    try:
        db.create_collection("experiments")
        print("✓ Created experiments collection")
    except:
        pass

    # TODO: Create indexes
    db.model_configs.create_index("model_id", unique=True)
    db.model_configs.create_index("framework")
    db.experiments.create_index([("model_id", 1), ("experiment_date", -1)])

    print("✓ MongoDB collections configured")

def insert_flexible_model_configs():
    """
    Demonstrate MongoDB's schema flexibility:
    Each model can have completely different configuration structures.
    """
    # TODO: PyTorch model config
    pytorch_config = {
        "model_id": "fraud-detector-v1",
        "model_name": "Fraud Detector CNN",
        "framework": "pytorch",
        "created_at": datetime.utcnow(),
        "config": {
            "architecture": {
                "layers": [
                    {"type": "conv2d", "filters": 32, "kernel_size": 3},
                    {"type": "maxpool", "pool_size": 2},
                    {"type": "dense", "units": 128, "activation": "relu"},
                    {"type": "dense", "units": 1, "activation": "sigmoid"}
                ]
            },
            "training": {
                "optimizer": "adam",
                "learning_rate": 0.001,
                "batch_size": 32,
                "epochs": 50
            },
            "data_preprocessing": {
                "normalization": "minmax",
                "augmentation": ["rotation", "flip"]
            }
        },
        "metrics": {
            "accuracy": 0.9845,
            "precision": 0.9712,
            "recall": 0.9834
        }
    }

    # TODO: Transformer model config (completely different structure)
    transformer_config = {
        "model_id": "sentiment-analyzer-v2",
        "model_name": "BERT Sentiment Classifier",
        "framework": "huggingface",
        "created_at": datetime.utcnow(),
        "config": {
            "base_model": "bert-base-uncased",
            "tokenizer": {
                "max_length": 512,
                "padding": "max_length",
                "truncation": True
            },
            "fine_tuning": {
                "learning_rate": 2e-5,
                "warmup_steps": 500,
                "weight_decay": 0.01,
                "num_train_epochs": 3
            },
            "task": "text-classification",
            "num_labels": 3
        },
        "metrics": {
            "accuracy": 0.9234,
            "f1_macro": 0.9187
        },
        "deployment": {
            "quantization": "int8",
            "onnx_export": True,
            "serving_framework": "triton"
        }
    }

    # TODO: XGBoost model config (yet another structure)
    xgboost_config = {
        "model_id": "churn-predictor-v3",
        "model_name": "Customer Churn XGBoost",
        "framework": "xgboost",
        "created_at": datetime.utcnow(),
        "config": {
            "booster": "gbtree",
            "objective": "binary:logistic",
            "eval_metric": "auc",
            "max_depth": 6,
            "learning_rate": 0.3,
            "n_estimators": 100,
            "feature_importance_type": "gain"
        },
        "feature_engineering": {
            "categorical_encoding": "target_encoding",
            "missing_value_strategy": "median_imputation",
            "feature_selection": {
                "method": "recursive_feature_elimination",
                "n_features": 50
            }
        },
        "metrics": {
            "auc_roc": 0.8934,
            "accuracy": 0.8456,
            "precision": 0.8234,
            "recall": 0.8678
        }
    }

    # TODO: Insert all configs
    db.model_configs.insert_many([pytorch_config, transformer_config, xgboost_config])
    print("✓ Inserted flexible model configs (3 different schemas)")

if __name__ == "__main__":
    setup_mongodb_collections()
    insert_flexible_model_configs()
```

**TODO 3.2:** Query and manipulate document data

```python
# mongodb_queries.py
from mongodb_setup import db
from pprint import pprint

def find_models_by_framework(framework: str):
    """MongoDB excels at querying nested documents."""
    print(f"\n=== Models using {framework} ===")
    models = db.model_configs.find({"framework": framework})

    for model in models:
        print(f"\n  Model: {model['model_name']}")
        print(f"  ID: {model['model_id']}")
        print(f"  Config keys: {list(model['config'].keys())}")

def find_high_accuracy_models(min_accuracy: float = 0.90):
    """Query nested fields with dot notation."""
    print(f"\n=== Models with accuracy >= {min_accuracy} ===")

    # TODO: Query nested metrics.accuracy field
    models = db.model_configs.find({
        "metrics.accuracy": {"$gte": min_accuracy}
    }).sort("metrics.accuracy", -1)

    for model in models:
        acc = model['metrics'].get('accuracy', 'N/A')
        print(f"  {model['model_name']:<40} | Accuracy: {acc}")

def update_model_with_new_metrics(model_id: str, new_metrics: dict):
    """
    MongoDB's flexible schema allows adding new fields without schema migration.
    Try adding this to a SQL table without ALTER TABLE!
    """
    result = db.model_configs.update_one(
        {"model_id": model_id},
        {
            "$set": {
                "metrics.inference_latency_ms": new_metrics.get("latency"),
                "metrics.model_size_mb": new_metrics.get("size"),
                "updated_at": datetime.utcnow()
            }
        }
    )

    print(f"\n✓ Updated {model_id} with new metrics: {new_metrics}")
    print(f"  Matched: {result.matched_count}, Modified: {result.modified_count}")

def aggregate_metrics_by_framework():
    """MongoDB aggregation pipeline for complex analysis."""
    print("\n=== Average Accuracy by Framework ===")

    # TODO: Use aggregation pipeline
    pipeline = [
        {
            "$group": {
                "_id": "$framework",
                "avg_accuracy": {"$avg": "$metrics.accuracy"},
                "count": {"$sum": 1}
            }
        },
        {
            "$sort": {"avg_accuracy": -1}
        }
    ]

    results = db.model_configs.aggregate(pipeline)

    for result in results:
        print(f"  {result['_id']:<15} | Avg Accuracy: {result['avg_accuracy']:.4f} | Count: {result['count']}")

# TODO: Run queries
if __name__ == "__main__":
    from datetime import datetime
    from mongodb_setup import setup_mongodb_collections, insert_flexible_model_configs

    find_models_by_framework("pytorch")
    find_high_accuracy_models()
    update_model_with_new_metrics("fraud-detector-v1", {"latency": 15.3, "size": 245.6})
    aggregate_metrics_by_framework()
```

### Task 4: Redis for High-Speed Caching and Feature Serving

**TODO 4.1:** Set up Redis connection and basic operations

```python
# redis_setup.py
import redis
import json
import time
import numpy as np

REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_PASSWORD = "mlpass123"

# TODO: Create Redis client
redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    password=REDIS_PASSWORD,
    decode_responses=True  # Automatically decode bytes to strings
)

def test_redis_connection():
    """Verify Redis is accessible."""
    try:
        redis_client.ping()
        print("✓ Redis connection successful")
        return True
    except Exception as e:
        print(f"✗ Redis connection failed: {e}")
        return False

# TODO: Cache model predictions
def cache_prediction(user_id: str, features: list, prediction: float, ttl: int = 300):
    """
    Cache prediction results with TTL (time-to-live).
    Redis excels at high-speed reads/writes with automatic expiration.
    """
    cache_key = f"prediction:{user_id}"

    # TODO: Store as JSON with expiration
    data = {
        "user_id": user_id,
        "features": features,
        "prediction": prediction,
        "cached_at": time.time()
    }

    redis_client.setex(
        cache_key,
        ttl,  # Expires after ttl seconds
        json.dumps(data)
    )

    print(f"✓ Cached prediction for {user_id} (TTL: {ttl}s)")

def get_cached_prediction(user_id: str):
    """Retrieve cached prediction if available."""
    cache_key = f"prediction:{user_id}"

    # TODO: Try to get from cache
    cached = redis_client.get(cache_key)

    if cached:
        data = json.loads(cached)
        age = time.time() - data['cached_at']
        print(f"✓ Cache HIT for {user_id} (age: {age:.1f}s)")
        return data['prediction']
    else:
        print(f"✗ Cache MISS for {user_id}")
        return None

if __name__ == "__main__":
    test_redis_connection()

    # Test caching
    cache_prediction("user_123", [0.5, 0.3, 0.8], 0.92, ttl=10)
    pred = get_cached_prediction("user_123")
    print(f"  Prediction: {pred}")

    # Wait for expiration
    print("\nWaiting 11 seconds for cache to expire...")
    time.sleep(11)
    pred = get_cached_prediction("user_123")
```

**TODO 4.2:** Implement feature store with Redis

```python
# feature_store.py
import redis
import numpy as np
import json
import time

from redis_setup import redis_client

def store_user_features(user_id: str, features: dict):
    """
    Store user features in Redis Hash.
    Hashes are perfect for storing related key-value pairs.
    """
    feature_key = f"features:user:{user_id}"

    # TODO: Use Redis hash for structured features
    redis_client.hset(feature_key, mapping=features)
    redis_client.expire(feature_key, 3600)  # Expire after 1 hour

    print(f"✓ Stored features for {user_id}: {list(features.keys())}")

def get_user_features(user_id: str):
    """Retrieve all features for a user."""
    feature_key = f"features:user:{user_id}"

    # TODO: Get all hash fields
    features = redis_client.hgetall(feature_key)

    if features:
        print(f"✓ Retrieved {len(features)} features for {user_id}")
        return {k: float(v) for k, v in features.items()}
    else:
        print(f"✗ No features found for {user_id}")
        return None

def batch_get_features(user_ids: list):
    """
    Efficiently retrieve features for multiple users using pipeline.
    Pipelines batch commands to reduce round-trip latency.
    """
    pipe = redis_client.pipeline()

    # TODO: Queue all reads in pipeline
    for user_id in user_ids:
        feature_key = f"features:user:{user_id}"
        pipe.hgetall(feature_key)

    # Execute all commands at once
    start = time.time()
    results = pipe.execute()
    duration = time.time() - start

    print(f"✓ Retrieved features for {len(user_ids)} users in {duration*1000:.2f}ms")

    # Convert results
    features_dict = {}
    for user_id, features in zip(user_ids, results):
        if features:
            features_dict[user_id] = {k: float(v) for k, v in features.items()}

    return features_dict

def implement_leaderboard():
    """
    Redis Sorted Sets are perfect for leaderboards and rankings.
    """
    leaderboard_key = "leaderboard:model_accuracy"

    # TODO: Add models to sorted set (score = accuracy)
    models = {
        "fraud-detector-v1": 0.9845,
        "fraud-detector-v2": 0.9821,
        "sentiment-analyzer-v2": 0.9234,
        "churn-predictor-v3": 0.8934
    }

    for model, accuracy in models.items():
        redis_client.zadd(leaderboard_key, {model: accuracy})

    print("\n=== Model Accuracy Leaderboard (Top 3) ===")

    # TODO: Get top 3 models by accuracy
    top_models = redis_client.zrevrange(leaderboard_key, 0, 2, withscores=True)

    for rank, (model, accuracy) in enumerate(top_models, 1):
        print(f"  {rank}. {model:<30} | Accuracy: {accuracy:.4f}")

    # TODO: Get rank of specific model
    rank = redis_client.zrevrank("leaderboard:model_accuracy", "churn-predictor-v3")
    print(f"\nchurn-predictor-v3 rank: {rank + 1}")

# TODO: Run feature store operations
if __name__ == "__main__":
    # Store features
    store_user_features("user_001", {
        "age": "35",
        "account_balance": "5000.50",
        "days_since_signup": "120",
        "num_transactions": "45"
    })

    store_user_features("user_002", {
        "age": "28",
        "account_balance": "12000.00",
        "days_since_signup": "365",
        "num_transactions": "120"
    })

    # Retrieve single user
    features = get_user_features("user_001")
    print(f"  Features: {features}\n")

    # Batch retrieval
    batch_features = batch_get_features(["user_001", "user_002", "user_003"])

    # Leaderboard
    implement_leaderboard()
```

**TODO 4.3:** Benchmark Redis vs PostgreSQL for reads

```python
# benchmark_reads.py
import time
from postgres_setup import engine
from sqlalchemy import text
from redis_setup import redis_client
import json

def benchmark_sql_read(num_queries: int = 1000):
    """Benchmark PostgreSQL for simple key-value reads."""
    # Pre-populate some data
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS kv_store (
                key VARCHAR(255) PRIMARY KEY,
                value TEXT
            )
        """))
        conn.execute(text("TRUNCATE kv_store"))

        # Insert test data
        for i in range(100):
            conn.execute(
                text("INSERT INTO kv_store (key, value) VALUES (:k, :v)"),
                {"k": f"key_{i}", "v": json.dumps({"data": f"value_{i}"})}
            )
        conn.commit()

    # Benchmark reads
    start = time.time()
    with engine.connect() as conn:
        for i in range(num_queries):
            key = f"key_{i % 100}"
            result = conn.execute(
                text("SELECT value FROM kv_store WHERE key = :k"),
                {"k": key}
            )
            _ = result.fetchone()

    duration = time.time() - start
    qps = num_queries / duration

    print(f"PostgreSQL: {num_queries} reads in {duration:.2f}s ({qps:.0f} QPS)")
    return duration

def benchmark_redis_read(num_queries: int = 1000):
    """Benchmark Redis for simple key-value reads."""
    # Pre-populate
    for i in range(100):
        redis_client.set(f"key_{i}", json.dumps({"data": f"value_{i}"}))

    # Benchmark reads
    start = time.time()
    for i in range(num_queries):
        key = f"key_{i % 100}"
        _ = redis_client.get(key)

    duration = time.time() - start
    qps = num_queries / duration

    print(f"Redis:      {num_queries} reads in {duration:.2f}s ({qps:.0f} QPS)")
    return duration

# TODO: Run benchmark
if __name__ == "__main__":
    print("=== Read Performance Comparison ===\n")

    pg_time = benchmark_sql_read(1000)
    redis_time = benchmark_redis_read(1000)

    speedup = pg_time / redis_time
    print(f"\nRedis is {speedup:.1f}x faster for simple key-value reads")

    print("\n✓ Use Redis for:")
    print("  - High-frequency reads (caching, feature serving)")
    print("  - Session management")
    print("  - Real-time leaderboards")
    print("  - Rate limiting\n")

    print("✓ Use PostgreSQL for:")
    print("  - Complex queries with JOINs")
    print("  - Transactions requiring ACID guarantees")
    print("  - Data requiring long-term persistence")
    print("  - Analytical queries with aggregations")
```

### Task 5: Hybrid Architecture - Combining SQL and NoSQL

**TODO 5.1:** Design a hybrid ML platform

```python
# hybrid_platform.py
from postgres_setup import engine
from sqlalchemy import text
from mongodb_setup import db
from redis_setup import redis_client
import json
import time

class MLPlatformHybrid:
    """
    Hybrid architecture leveraging strengths of each database:
    - PostgreSQL: Structured training run data, datasets
    - MongoDB: Flexible model configurations
    - Redis: High-speed feature caching and predictions
    """

    def register_training_run(self, dataset_name: str, model_config: dict):
        """
        1. Store structured training metadata in PostgreSQL
        2. Store flexible model config in MongoDB
        3. Link them with a common model_id
        """
        model_id = f"{model_config['model_name']}-{int(time.time())}"

        # TODO: Insert into PostgreSQL
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT id FROM datasets WHERE name = :name"),
                {"name": dataset_name}
            )
            dataset_id = result.fetchone()[0]

            conn.execute(text("""
                INSERT INTO training_runs
                (dataset_id, model_name, framework, status)
                VALUES (:did, :model_id, :fw, 'running')
            """), {
                "did": dataset_id,
                "model_id": model_id,
                "fw": model_config['framework']
            })
            conn.commit()

        # TODO: Insert flexible config into MongoDB
        mongo_doc = {
            "model_id": model_id,
            "model_name": model_config['model_name'],
            "framework": model_config['framework'],
            "config": model_config.get('hyperparameters', {}),
            "created_at": time.time()
        }
        db.model_configs.insert_one(mongo_doc)

        print(f"✓ Registered training run: {model_id}")
        print(f"  - PostgreSQL: Training run metadata")
        print(f"  - MongoDB: Full model configuration")

        return model_id

    def get_model_info(self, model_id: str):
        """
        Fetch comprehensive model info from multiple databases.
        """
        info = {}

        # TODO: Get structured data from PostgreSQL
        with engine.connect() as conn:
            result = conn.execute(
                text("""
                    SELECT tr.status, tr.accuracy, tr.loss, tr.training_time_seconds, d.name
                    FROM training_runs tr
                    JOIN datasets d ON tr.dataset_id = d.id
                    WHERE tr.model_name = :model_id
                """),
                {"model_id": model_id}
            )
            row = result.fetchone()

            if row:
                info['postgres'] = {
                    "status": row[0],
                    "accuracy": row[1],
                    "loss": row[2],
                    "training_time": row[3],
                    "dataset": row[4]
                }

        # TODO: Get flexible config from MongoDB
        mongo_doc = db.model_configs.find_one({"model_id": model_id})
        if mongo_doc:
            info['mongodb'] = {
                "framework": mongo_doc['framework'],
                "config": mongo_doc.get('config', {}),
                "created_at": mongo_doc.get('created_at')
            }

        return info

    def serve_prediction_with_cache(self, user_id: str, features: list):
        """
        Prediction serving with Redis cache:
        1. Check Redis cache for recent prediction
        2. If miss, compute prediction and cache it
        """
        cache_key = f"prediction:{user_id}"

        # TODO: Try cache first
        cached = redis_client.get(cache_key)
        if cached:
            print(f"✓ Cache HIT for {user_id}")
            return json.loads(cached)

        # Cache miss - compute prediction
        print(f"✗ Cache MISS for {user_id} - computing prediction...")
        time.sleep(0.1)  # Simulate model inference

        prediction = {
            "user_id": user_id,
            "prediction": 0.85,  # Mock prediction
            "features": features,
            "timestamp": time.time()
        }

        # TODO: Cache for 5 minutes
        redis_client.setex(cache_key, 300, json.dumps(prediction))

        return prediction

# TODO: Test hybrid platform
if __name__ == "__main__":
    platform = MLPlatformHybrid()

    # Register a new training run
    model_config = {
        "model_name": "fraud-detector",
        "framework": "pytorch",
        "hyperparameters": {
            "learning_rate": 0.001,
            "batch_size": 64,
            "epochs": 20,
            "layers": [128, 64, 32]
        }
    }

    model_id = platform.register_training_run("fraud-train-v1", model_config)

    # Retrieve info from multiple databases
    print("\n=== Model Information (Hybrid Query) ===")
    info = platform.get_model_info(model_id)
    print(f"PostgreSQL data: {info.get('postgres')}")
    print(f"MongoDB data: {info.get('mongodb')}")

    # Prediction serving with cache
    print("\n=== Prediction Serving ===")
    pred1 = platform.serve_prediction_with_cache("user_999", [0.1, 0.2, 0.3])
    pred2 = platform.serve_prediction_with_cache("user_999", [0.1, 0.2, 0.3])  # Should hit cache
```

### Task 6: Data Migration Strategies

**TODO 6.1:** Migrate data from PostgreSQL to MongoDB

```python
# migration_sql_to_mongo.py
from postgres_setup import engine
from mongodb_setup import db
from sqlalchemy import text
from datetime import datetime

def migrate_training_runs_to_mongo():
    """
    Scenario: Need to add flexible metadata to training runs.
    Migrate structured data from PostgreSQL to MongoDB for flexibility.
    """
    # TODO: Fetch all training runs from PostgreSQL
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT
                tr.id,
                tr.model_name,
                tr.framework,
                tr.status,
                tr.accuracy,
                tr.loss,
                tr.training_time_seconds,
                d.name as dataset_name
            FROM training_runs tr
            JOIN datasets d ON tr.dataset_id = d.id
        """))

        training_runs = []
        for row in result:
            # TODO: Convert to MongoDB document format
            doc = {
                "postgres_id": row[0],
                "model_name": row[1],
                "framework": row[2],
                "status": row[3],
                "metrics": {
                    "accuracy": row[4],
                    "loss": row[5]
                },
                "training_time_seconds": row[6],
                "dataset": row[7],
                "migrated_at": datetime.utcnow(),
                # Can now add flexible fields easily
                "tags": [],
                "custom_metadata": {}
            }
            training_runs.append(doc)

    # TODO: Insert into MongoDB
    if training_runs:
        db.training_runs_migrated.insert_many(training_runs)
        print(f"✓ Migrated {len(training_runs)} training runs to MongoDB")

    # Verify migration
    count = db.training_runs_migrated.count_documents({})
    print(f"  MongoDB training_runs_migrated count: {count}")

# TODO: Run migration
if __name__ == "__main__":
    migrate_training_runs_to_mongo()
```

**TODO 6.2:** Implement dual-write strategy for gradual migration

```python
# dual_write_strategy.py
from postgres_setup import engine
from mongodb_setup import db
from sqlalchemy import text
from datetime import datetime

def create_training_run_dual_write(model_name: str, framework: str, dataset_id: int):
    """
    Dual-write pattern: Write to both databases during migration period.
    Allows gradual cutover from PostgreSQL to MongoDB.
    """
    try:
        # TODO: Write to PostgreSQL (primary for now)
        with engine.connect() as conn:
            result = conn.execute(text("""
                INSERT INTO training_runs (dataset_id, model_name, framework, status)
                VALUES (:did, :model, :fw, 'running')
                RETURNING id
            """), {"did": dataset_id, "model": model_name, "fw": framework})

            pg_id = result.fetchone()[0]
            conn.commit()
            print(f"✓ Written to PostgreSQL (id: {pg_id})")

        # TODO: Write to MongoDB (shadow write)
        mongo_doc = {
            "postgres_id": pg_id,
            "model_name": model_name,
            "framework": framework,
            "status": "running",
            "created_at": datetime.utcnow()
        }
        result = db.training_runs_migrated.insert_one(mongo_doc)
        print(f"✓ Written to MongoDB (id: {result.inserted_id})")

        return pg_id

    except Exception as e:
        print(f"✗ Dual-write failed: {e}")
        # TODO: Implement rollback or compensation logic
        raise

# TODO: Test dual-write
if __name__ == "__main__":
    create_training_run_dual_write("test-dual-write-model", "tensorflow", 1)
```

### Task 7: Decision Matrix and Use Case Evaluation

**TODO 7.1:** Create decision matrix for database selection

```python
# decision_matrix.py
import pandas as pd

def create_decision_matrix():
    """
    Decision matrix for choosing between SQL, MongoDB, and Redis
    for different ML platform use cases.
    """
    data = {
        "Use Case": [
            "Training run metadata",
            "Model hyperparameters",
            "Real-time predictions",
            "User features for serving",
            "Dataset lineage",
            "Experiment metrics",
            "Model artifact metadata",
            "API request caching",
            "Session management",
            "Complex analytical queries"
        ],
        "Best Choice": [
            "PostgreSQL",
            "MongoDB",
            "Redis",
            "Redis",
            "PostgreSQL",
            "PostgreSQL",
            "MongoDB",
            "Redis",
            "Redis",
            "PostgreSQL"
        ],
        "Reasoning": [
            "Structured data, needs JOINs with datasets",
            "Flexible schema, different frameworks have different params",
            "Sub-10ms latency required, high throughput",
            "Fast reads, TTL for stale features",
            "Complex relationships, FOREIGN KEY constraints",
            "Aggregations, time-series queries",
            "Varies by framework, flexible schema",
            "Automatic expiration, extremely fast reads",
            "Fast reads/writes, automatic cleanup",
            "SQL excels at aggregations, filtering, JOINs"
        ]
    }

    df = pd.DataFrame(data)
    print("\n=== ML Platform Database Decision Matrix ===\n")
    print(df.to_string(index=False))

    # Summary
    print("\n=== Summary ===")
    print(f"PostgreSQL: {(df['Best Choice'] == 'PostgreSQL').sum()} use cases")
    print(f"MongoDB:    {(df['Best Choice'] == 'MongoDB').sum()} use cases")
    print(f"Redis:      {(df['Best Choice'] == 'Redis').sum()} use cases")

# TODO: Run decision matrix
if __name__ == "__main__":
    create_decision_matrix()
```

**TODO 7.2:** Document trade-offs

```python
# database_tradeoffs.py

def print_tradeoffs():
    """Document key trade-offs for each database type."""

    tradeoffs = {
        "PostgreSQL (SQL)": {
            "Strengths": [
                "ACID transactions guarantee data consistency",
                "Complex queries with JOINs, aggregations, window functions",
                "Strong schema enforcement prevents data corruption",
                "Mature ecosystem and tooling",
                "Excellent for analytical workloads"
            ],
            "Weaknesses": [
                "Schema changes require migrations (ALTER TABLE)",
                "Vertical scaling limits for very high throughput",
                "Higher latency than Redis for simple key-value lookups",
                "Not ideal for rapidly evolving data structures"
            ],
            "Best For": [
                "Core business data requiring consistency",
                "Complex analytical queries",
                "Data with clear relationships (users, orders, etc.)"
            ]
        },
        "MongoDB (Document NoSQL)": {
            "Strengths": [
                "Flexible schema allows rapid iteration",
                "Nested documents reduce need for JOINs",
                "Horizontal scaling with sharding",
                "Excels at storing varied data structures",
                "Native JSON support"
            ],
            "Weaknesses": [
                "Weaker consistency guarantees (eventual consistency)",
                "No FOREIGN KEY constraints (manual enforcement)",
                "Can lead to data duplication",
                "Complex queries less efficient than SQL",
                "Aggregation pipeline has learning curve"
            ],
            "Best For": [
                "Rapidly evolving schemas (ML experiments)",
                "Hierarchical data (model configs, metadata)",
                "Catalog systems with varied item types"
            ]
        },
        "Redis (Key-Value NoSQL)": {
            "Strengths": [
                "Extremely fast (in-memory, <1ms latency)",
                "Built-in TTL for automatic expiration",
                "Rich data structures (sets, sorted sets, hashes)",
                "Pub/sub for real-time messaging",
                "Perfect for caching layer"
            ],
            "Weaknesses": [
                "Data limited by RAM (expensive at scale)",
                "No complex queries (no JOINs, aggregations)",
                "Persistence is optional (data loss risk)",
                "Not suitable for primary data storage",
                "Simple data structures only"
            ],
            "Best For": [
                "Caching layer (predictions, API responses)",
                "Session management and rate limiting",
                "Real-time leaderboards and counters",
                "Feature stores for ML serving"
            ]
        }
    }

    for db_type, info in tradeoffs.items():
        print(f"\n{'='*60}")
        print(f"{db_type}")
        print('='*60)

        print("\n✓ Strengths:")
        for strength in info["Strengths"]:
            print(f"  - {strength}")

        print("\n✗ Weaknesses:")
        for weakness in info["Weaknesses"]:
            print(f"  - {weakness}")

        print("\n→ Best For:")
        for use_case in info["Best For"]:
            print(f"  - {use_case}")

# TODO: Print tradeoffs
if __name__ == "__main__":
    print_tradeoffs()
```

## Deliverables

Submit a repository with:

1. **Docker Configuration**
   - `docker-compose.yml` for multi-database environment
   - Scripts to initialize all databases

2. **Python Modules**
   - `postgres_setup.py` and `postgres_queries.py`
   - `mongodb_setup.py` and `mongodb_queries.py`
   - `redis_setup.py` and `feature_store.py`
   - `benchmark_reads.py` - Performance comparison
   - `hybrid_platform.py` - Unified ML platform
   - `migration_sql_to_mongo.py` - Data migration examples
   - `decision_matrix.py` and `database_tradeoffs.py`

3. **Analysis Document** (`ANALYSIS.md`)
   - Decision matrix for database selection
   - Performance benchmark results (Redis vs PostgreSQL)
   - Trade-off analysis for each database type
   - Hybrid architecture diagram
   - Migration strategy recommendations

4. **README**
   - Setup instructions for multi-database environment
   - How to run each script
   - Key learnings about SQL vs NoSQL

## Success Criteria

- [ ] All three databases running and accessible via Docker Compose
- [ ] PostgreSQL queries demonstrate complex JOINs and aggregations
- [ ] MongoDB demonstrates flexible schema with varied document structures
- [ ] Redis caching shows measurable performance improvement
- [ ] Feature store implemented with Redis hashes and pipelines
- [ ] Benchmark shows Redis >5x faster than PostgreSQL for key-value reads
- [ ] Hybrid platform successfully uses all three databases
- [ ] Decision matrix clearly documents when to use each database
- [ ] Data migration scripts work correctly
- [ ] Code includes proper connection management and error handling

## Bonus Challenges

1. **Distributed Transactions**: Implement saga pattern for operations spanning multiple databases
2. **MongoDB Sharding**: Set up sharded MongoDB cluster for horizontal scaling demonstration
3. **Redis Cluster**: Configure Redis cluster for high availability
4. **Change Data Capture (CDC)**: Stream PostgreSQL changes to MongoDB using Debezium
5. **Graph Database**: Add Neo4j to track model lineage and data provenance
6. **Time-Series Database**: Add InfluxDB for high-frequency metrics storage

## Resources

- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [MongoDB Manual](https://www.mongodb.com/docs/manual/)
- [Redis Documentation](https://redis.io/documentation)
- [Choosing the Right Database](https://www.prisma.io/dataguide/intro/comparing-database-types)
- [CAP Theorem](https://en.wikipedia.org/wiki/CAP_theorem)

## Evaluation Rubric

| Criteria | Points |
|----------|--------|
| Multi-database environment setup | 10 |
| PostgreSQL complex queries (JOINs, aggregations) | 15 |
| MongoDB flexible schema implementation | 15 |
| Redis caching and feature store | 15 |
| Performance benchmarks with analysis | 15 |
| Hybrid architecture implementation | 15 |
| Decision matrix and trade-off analysis | 10 |
| Code quality and documentation | 5 |

**Total: 100 points**
