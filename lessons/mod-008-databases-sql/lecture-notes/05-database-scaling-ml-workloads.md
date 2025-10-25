# Lecture 05: Database Scaling and Performance for ML Workloads

## Table of Contents
1. [Introduction](#introduction)
2. [Database Scaling Fundamentals](#database-scaling-fundamentals)
3. [Read Replicas and Replication](#read-replicas-and-replication)
4. [Database Sharding](#database-sharding)
5. [Caching Strategies](#caching-strategies)
6. [NoSQL Databases for ML](#nosql-databases-for-ml)
7. [Time-Series Databases](#time-series-databases)
8. [Vector Databases for ML](#vector-databases-for-ml)
9. [Database Performance Optimization](#database-performance-optimization)
10. [Summary and Key Takeaways](#summary-and-key-takeaways)

## Introduction

ML applications generate massive amounts of data: training datasets, model metadata, predictions, metrics, logs, and embeddings. As your ML platform scales from hundreds to millions of predictions per day, your database becomes a bottleneck.

This lecture covers database scaling strategies, performance optimization, and specialized databases for ML workloads.

### Learning Objectives

By the end of this lecture, you will:
- Understand vertical vs horizontal scaling trade-offs
- Implement read replicas for scaling read-heavy workloads
- Design sharding strategies for horizontal scaling
- Use caching to reduce database load
- Choose appropriate NoSQL databases for ML data
- Work with time-series databases for metrics
- Use vector databases for similarity search
- Optimize database performance for ML workloads

### Prerequisites
- Lectures 01-04 (SQL fundamentals, query optimization, ORMs)
- Understanding of ML workflows (training, inference, metrics)
- Basic knowledge of caching concepts

**Duration**: 90 minutes
**Difficulty**: Intermediate to Advanced

---

## 1. Database Scaling Fundamentals

### Vertical vs Horizontal Scaling

```
Vertical Scaling (Scale Up):
┌─────────────────────────────┐
│  Bigger Database Server     │
│  ├── 4 CPUs  → 32 CPUs     │
│  ├── 16GB RAM → 256GB RAM  │
│  └── 1TB SSD → 10TB SSD    │
└─────────────────────────────┘

Pros: Simple, no code changes
Cons: Expensive, hardware limits, single point of failure

Horizontal Scaling (Scale Out):
┌──────────┐ ┌──────────┐ ┌──────────┐
│ DB Node 1│ │ DB Node 2│ │ DB Node 3│
│ 4 CPUs   │ │ 4 CPUs   │ │ 4 CPUs   │
│ 16GB RAM │ │ 16GB RAM │ │ 16GB RAM │
└──────────┘ └──────────┘ └──────────┘

Pros: Cost-effective, unlimited scaling, high availability
Cons: Complex, code changes needed, data consistency challenges
```

### ML Database Workload Characteristics

```
Typical ML Database Access Patterns:

Training Phase:
├── Read: HEAVY (read datasets, features)
├── Write: MEDIUM (save checkpoints, metrics)
└── Query Pattern: Batch reads, sequential scans

Inference Phase:
├── Read: HEAVY (load features for prediction)
├── Write: HEAVY (store predictions, logs)
└── Query Pattern: Point queries, high QPS

Metrics/Monitoring:
├── Read: HEAVY (dashboards, alerts)
├── Write: HEAVY (time-series metrics)
└── Query Pattern: Time-range queries, aggregations

Solution: Different databases for different workloads!
```

---

## 2. Read Replicas and Replication

### Master-Replica Architecture

```
┌──────────────────────────────────────┐
│        Master (Primary)              │
│     Handles ALL writes               │
│  ├── INSERT predictions              │
│  ├── UPDATE model metadata           │
│  └── DELETE old experiments          │
└────────────┬─────────────────────────┘
             │ Replication
      ┌──────┴──────┬──────────┐
      │             │          │
┌─────▼─────┐ ┌────▼──────┐ ┌─▼──────────┐
│ Replica 1 │ │ Replica 2 │ │ Replica 3  │
│ Read-only │ │ Read-only │ │ Read-only  │
│ Dashboard │ │ Analytics │ │ ML Training│
└───────────┘ └───────────┘ └────────────┘
```

### Setting Up Read Replicas (PostgreSQL)

**On Master:**

```sql
-- Enable replication in postgresql.conf
wal_level = replica
max_wal_senders = 3
wal_keep_size = 1GB

-- Create replication user
CREATE USER replicator REPLICATION LOGIN PASSWORD 'secure_password';
```

**On Replica:**

```bash
# Stop replica
sudo systemctl stop postgresql

# Remove old data
rm -rf /var/lib/postgresql/14/main

# Copy data from master
pg_basebackup -h master-host -D /var/lib/postgresql/14/main \
  -U replicator -v -P -W -R

# Start replica
sudo systemctl start postgresql
```

**Application Code with Read Replicas:**

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import random

# Master for writes
master_engine = create_engine('postgresql://user:pass@master-db:5432/mldb')
MasterSession = sessionmaker(bind=master_engine)

# Replicas for reads
replica_engines = [
    create_engine('postgresql://user:pass@replica1-db:5432/mldb'),
    create_engine('postgresql://user:pass@replica2-db:5432/mldb'),
    create_engine('postgresql://user:pass@replica3-db:5432/mldb')
]
ReplicaSession = sessionmaker(bind=random.choice(replica_engines))

def save_prediction(prediction_data):
    """Write to master"""
    session = MasterSession()
    try:
        prediction = Prediction(**prediction_data)
        session.add(prediction)
        session.commit()
    finally:
        session.close()

def get_model_metadata(model_id):
    """Read from replica"""
    session = ReplicaSession()
    try:
        return session.query(Model).filter_by(id=model_id).first()
    finally:
        session.close()
```

### Replication Lag

**Problem**: Replicas may be behind master (seconds to minutes)

```python
# Check replication lag (PostgreSQL)
import psycopg2

conn = psycopg2.connect("dbname=mldb host=replica1")
cursor = conn.cursor()

cursor.execute("""
    SELECT
        pg_last_wal_receive_lsn() AS receive,
        pg_last_wal_replay_lsn() AS replay,
        pg_last_wal_receive_lsn() - pg_last_wal_replay_lsn() AS lag_bytes
""")

lag = cursor.fetchone()
print(f"Replication lag: {lag[2]} bytes")

# If lag > threshold, warn user
if lag[2] > 1000000:  # 1MB lag
    print("WARNING: Replica is significantly behind master")
```

---

## 3. Database Sharding

### What is Sharding?

**Sharding** = Horizontal partitioning across multiple databases

```
Single Database (100M rows):
┌────────────────────────────────┐
│  Predictions Table             │
│  ├── User 1 predictions        │
│  ├── User 2 predictions        │
│  ├── ...                       │
│  └── User 1M predictions       │
│  (Slow queries, single server) │
└────────────────────────────────┘

Sharded (4 shards, 25M rows each):
┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
│ Shard 0  │ │ Shard 1  │ │ Shard 2  │ │ Shard 3  │
│ Users    │ │ Users    │ │ Users    │ │ Users    │
│ 0-249K   │ │ 250-499K │ │ 500-749K │ │ 750K-1M  │
└──────────┘ └──────────┘ └──────────┘ └──────────┘
```

### Sharding Strategies

#### 1. Hash-Based Sharding

```python
import hashlib

NUM_SHARDS = 4

def get_shard(user_id):
    """Determine shard based on user ID hash"""
    hash_value = int(hashlib.md5(str(user_id).encode()).hexdigest(), 16)
    shard_id = hash_value % NUM_SHARDS
    return shard_id

# Example
user_id = 12345
shard = get_shard(user_id)
print(f"User {user_id} → Shard {shard}")
# User 12345 → Shard 2
```

**Database connections per shard:**

```python
from sqlalchemy import create_engine

shard_engines = {
    0: create_engine('postgresql://user:pass@shard0-db:5432/mldb'),
    1: create_engine('postgresql://user:pass@shard1-db:5432/mldb'),
    2: create_engine('postgresql://user:pass@shard2-db:5432/mldb'),
    3: create_engine('postgresql://user:pass@shard3-db:5432/mldb')
}

def get_engine_for_user(user_id):
    shard_id = get_shard(user_id)
    return shard_engines[shard_id]

# Save prediction to correct shard
def save_prediction(user_id, prediction_data):
    engine = get_engine_for_user(user_id)
    with engine.connect() as conn:
        conn.execute(
            "INSERT INTO predictions (user_id, result, timestamp) VALUES (%s, %s, %s)",
            (user_id, prediction_data['result'], prediction_data['timestamp'])
        )
```

#### 2. Range-Based Sharding

```python
# Shard by user_id ranges
def get_shard_by_range(user_id):
    if user_id < 250000:
        return 0
    elif user_id < 500000:
        return 1
    elif user_id < 750000:
        return 2
    else:
        return 3
```

**Pros**: Easy to add new users to new shards
**Cons**: Uneven distribution if user growth is non-linear

#### 3. Geographic Sharding

```python
# Shard by geographic region
SHARD_BY_REGION = {
    'us-east': 0,
    'us-west': 1,
    'eu': 2,
    'asia': 3
}

def get_shard_by_region(region):
    return SHARD_BY_REGION.get(region, 0)
```

**Use case**: Data residency requirements, low latency

### Cross-Shard Queries

**Problem**: Queries that span multiple shards

```python
# Get predictions for all users (across all shards)
def get_all_predictions_last_hour():
    results = []

    # Query each shard
    for shard_id, engine in shard_engines.items():
        with engine.connect() as conn:
            shard_results = conn.execute("""
                SELECT * FROM predictions
                WHERE timestamp > NOW() - INTERVAL '1 hour'
            """).fetchall()
            results.extend(shard_results)

    return results

# Aggregate across shards
def get_total_predictions_count():
    total = 0
    for shard_id, engine in shard_engines.items():
        with engine.connect() as conn:
            count = conn.execute("SELECT COUNT(*) FROM predictions").scalar()
            total += count
    return total
```

**Performance tip**: Use async queries to parallelize:

```python
import asyncio
import asyncpg

async def get_count_from_shard(shard_config):
    conn = await asyncpg.connect(**shard_config)
    count = await conn.fetchval("SELECT COUNT(*) FROM predictions")
    await conn.close()
    return count

async def get_total_count_parallel():
    tasks = [get_count_from_shard(cfg) for cfg in shard_configs]
    counts = await asyncio.gather(*tasks)
    return sum(counts)

# 4x faster than sequential
total = asyncio.run(get_total_count_parallel())
```

---

## 4. Caching Strategies

### Why Cache for ML?

```
Without Cache:
Every prediction request → Database query → 50ms latency

With Cache:
First request → Database → Cache → 50ms
Subsequent requests → Cache → 2ms (25x faster!)
```

### Redis for ML Caching

```python
import redis
import json
import hashlib

redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)

def get_user_features(user_id):
    """Get user features with caching"""
    cache_key = f"user_features:{user_id}"

    # Try cache first
    cached = redis_client.get(cache_key)
    if cached:
        return json.loads(cached)

    # Cache miss - query database
    features = db.query(f"SELECT * FROM user_features WHERE user_id = {user_id}")

    # Store in cache (TTL: 1 hour)
    redis_client.setex(cache_key, 3600, json.dumps(features))

    return features
```

### Cache Invalidation

```python
def update_user_features(user_id, new_features):
    """Update features and invalidate cache"""
    # Update database
    db.execute(
        "UPDATE user_features SET features = %s WHERE user_id = %s",
        (json.dumps(new_features), user_id)
    )

    # Invalidate cache
    cache_key = f"user_features:{user_id}"
    redis_client.delete(cache_key)
```

### Caching Model Metadata

```python
def get_model_config(model_id):
    """Cache model configurations"""
    cache_key = f"model_config:{model_id}"

    cached = redis_client.get(cache_key)
    if cached:
        return json.loads(cached)

    # Load from DB
    config = db.query(f"SELECT config FROM models WHERE id = {model_id}")

    # Cache for 24 hours (models change infrequently)
    redis_client.setex(cache_key, 86400, json.dumps(config))

    return config
```

---

## 5. NoSQL Databases for ML

### When to Use NoSQL

```
Use SQL for:
✓ Structured data (tabular)
✓ Complex joins
✓ ACID transactions
✓ Business-critical data

Use NoSQL for:
✓ Unstructured/semi-structured data
✓ Massive scale (billions of records)
✓ High write throughput
✓ Flexible schema
```

### MongoDB for ML Metadata

```python
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['ml_platform']

# Store experiment metadata
experiments = db['experiments']

experiment = {
    'experiment_id': 'exp_12345',
    'model_type': 'bert-classifier',
    'hyperparameters': {
        'learning_rate': 0.001,
        'batch_size': 32,
        'epochs': 10
    },
    'metrics': {
        'accuracy': 0.95,
        'f1_score': 0.94
    },
    'artifacts': {
        'model_path': 's3://models/exp_12345/model.pt',
        'config_path': 's3://models/exp_12345/config.yaml'
    },
    'created_at': '2024-01-15T10:30:00Z',
    'status': 'completed'
}

experiments.insert_one(experiment)

# Query experiments
best_experiments = experiments.find(
    {'metrics.accuracy': {'$gte': 0.90}}
).sort('metrics.accuracy', -1).limit(10)

for exp in best_experiments:
    print(f"{exp['experiment_id']}: {exp['metrics']['accuracy']}")
```

---

## 6. Time-Series Databases

### InfluxDB for ML Metrics

```python
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

client = InfluxDBClient(url="http://localhost:8086", token="my-token", org="ml-org")
write_api = client.write_api(write_options=SYNCHRONOUS)

# Write metrics
def log_inference_metrics(model_name, latency_ms, batch_size):
    point = Point("inference_metrics") \
        .tag("model", model_name) \
        .field("latency_ms", latency_ms) \
        .field("batch_size", batch_size)

    write_api.write(bucket="ml-metrics", record=point)

# Query metrics
query_api = client.query_api()

query = '''
from(bucket: "ml-metrics")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "inference_metrics")
  |> filter(fn: (r) => r.model == "bert-classifier")
  |> mean()
'''

tables = query_api.query(query)
for table in tables:
    for record in table.records:
        print(f"Average latency: {record.get_value()} ms")
```

---

## 7. Vector Databases for ML

### Pinecone for Similarity Search

```python
import pinecone

pinecone.init(api_key="your-api-key", environment="us-west1-gcp")

# Create index
pinecone.create_index("ml-embeddings", dimension=768, metric="cosine")

index = pinecone.Index("ml-embeddings")

# Store embeddings
embeddings = [
    ("doc1", [0.1, 0.2, ...], {"text": "ML infrastructure"}),
    ("doc2", [0.3, 0.4, ...], {"text": "Model serving"}),
]

index.upsert(vectors=embeddings)

# Similarity search
query_embedding = [0.15, 0.25, ...]
results = index.query(query_embedding, top_k=10, include_metadata=True)

for match in results['matches']:
    print(f"ID: {match['id']}, Score: {match['score']}, Text: {match['metadata']['text']}")
```

---

## 8. Database Performance Optimization

### Query Optimization Checklist

```sql
-- 1. Add indexes on frequently queried columns
CREATE INDEX idx_predictions_user_timestamp
ON predictions (user_id, timestamp DESC);

-- 2. Use EXPLAIN to analyze query plans
EXPLAIN ANALYZE
SELECT * FROM predictions
WHERE user_id = 12345 AND timestamp > NOW() - INTERVAL '1 hour';

-- 3. Avoid SELECT * (only select needed columns)
SELECT id, result, timestamp FROM predictions WHERE user_id = 12345;

-- 4. Use connection pooling (SQLAlchemy)
engine = create_engine(
    'postgresql://user:pass@db:5432/mldb',
    pool_size=20,
    max_overflow=40,
    pool_pre_ping=True
)
```

---

## 9. Summary and Key Takeaways

### Core Concepts

1. **Scaling strategies** for ML workloads
   - Read replicas: 3-10x read throughput
   - Sharding: Unlimited horizontal scaling
   - Vertical scaling: Simple but limited

2. **Caching** reduces database load
   - Redis for hot data (user features, model configs)
   - 10-50x latency reduction
   - Implement cache invalidation

3. **NoSQL** for unstructured ML data
   - MongoDB: Experiment metadata
   - InfluxDB: Time-series metrics
   - Pinecone: Vector similarity search

4. **Performance optimization** is critical
   - Index frequently queried columns
   - Use EXPLAIN to analyze queries
   - Connection pooling for efficiency

### Practical Skills Gained

✅ Set up read replicas for scaling reads
✅ Implement database sharding strategies
✅ Use Redis caching to reduce latency
✅ Choose appropriate NoSQL databases
✅ Work with time-series and vector databases
✅ Optimize database performance

### Next Steps

- **Practice**: Set up read replicas in PostgreSQL
- **Experiment**: Implement Redis caching for an ML API
- **Explore**: Try InfluxDB for tracking model metrics
- **Challenge**: Design a sharding strategy for 100M users

### Additional Resources

- [PostgreSQL Replication](https://www.postgresql.org/docs/current/high-availability.html)
- [Database Sharding Explained](https://www.mongodb.com/basics/sharding)
- [Redis Documentation](https://redis.io/documentation)
- [InfluxDB for ML Metrics](https://www.influxdata.com/)
- [Pinecone Vector Database](https://www.pinecone.io/)

---

**Congratulations!** You now understand how to scale databases for ML workloads, from read replicas and sharding to specialized NoSQL databases for different ML data types.

**Module Complete!**
