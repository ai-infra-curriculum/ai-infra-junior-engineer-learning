# Lecture 06: NoSQL Basics

## Table of Contents
1. [Introduction](#introduction)
2. [What Is NoSQL?](#what-is-nosql)
3. [NoSQL Categories](#nosql-categories)
4. [When to Use NoSQL Instead of SQL](#when-to-use-nosql-instead-of-sql)
5. [MongoDB: Document Database](#mongodb-document-database)
6. [Redis: Key-Value and Data Structures](#redis-key-value-and-data-structures)
7. [Vector Databases for ML](#vector-databases-for-ml)
8. [Consistency, Availability, and the CAP Theorem](#consistency-availability-and-the-cap-theorem)
9. [Polyglot Persistence in ML Systems](#polyglot-persistence-in-ml-systems)
10. [Operational Concerns](#operational-concerns)
11. [Summary and Key Takeaways](#summary-and-key-takeaways)

## Introduction

Relational databases are the right answer for many problems but not all problems. NoSQL ("Not Only SQL") databases trade some of the constraints of the relational model — fixed schema, ACID transactions, joins — for properties relational databases struggle with: horizontal scale, flexible documents, sub-millisecond key lookups, and specialized data types like vectors and time series.

In an ML infrastructure team, you will routinely encounter:
- **Redis** as a feature store cache, a session store, and a job queue.
- **MongoDB** as a flexible store for experiment metadata, model artifacts catalog, or user-event logs.
- A **vector database** (Pinecone, Weaviate, Qdrant, pgvector) for embedding similarity search.

This lecture grounds you in the two NoSQL systems you are most likely to meet day one — MongoDB and Redis — and introduces vector databases as the emerging third leg of ML persistence. It is not a deep dive into either; that is the domain of dedicated database training. The goal is competent use, accurate decision-making, and the language to talk to specialists.

### Learning Objectives

By the end of this lecture, you will:
- Distinguish the major NoSQL categories and when each is appropriate
- Read and write MongoDB documents from Python using PyMongo
- Use Redis for caching, queues, and rate limiting from Python
- Understand the CAP theorem at a working level
- Choose NoSQL vs SQL for an ML infrastructure problem with clear reasoning
- Operate a NoSQL service safely (auth, backups, monitoring)

### Prerequisites
- Module 008 Lectures 01–05 (SQL fundamentals, ORMs, scaling)
- Python fundamentals
- Comfort with JSON

### Estimated Time
3 hours (including hands-on exercises)

---

## What Is NoSQL?

NoSQL is a loose umbrella term for databases that do not use the relational model. The "Not Only SQL" expansion was retrofitted to soften the original meaning and emphasize that NoSQL systems can complement, not just replace, relational stores.

Common traits across NoSQL systems:

1. **Schema-flexible.** You can add a new field to a document without an `ALTER TABLE`.
2. **Horizontally scalable.** Designed from the start to shard across many nodes.
3. **Single-purpose data models.** Each NoSQL category solves one shape of problem well rather than all problems adequately.
4. **Relaxed transactional guarantees.** Most NoSQL systems give up some ACID properties (especially across documents/shards) for performance and scale.
5. **Document, key, or graph access patterns.** Lookups by primary key are extremely fast; ad-hoc joins are not the strength.

NoSQL is **not** a magic upgrade over PostgreSQL. Modern PostgreSQL handles JSON documents, full-text search, time-series workloads, and even vectors (via `pgvector`) competently. If your workload is small to medium and you don't have a clear constraint that PostgreSQL fails to meet, stay relational.

---

## NoSQL Categories

| Category | Examples | Sweet spot |
|---|---|---|
| **Key-value** | Redis, DynamoDB, etcd, Memcached | Sub-millisecond lookups by exact key; caching; counters; queues |
| **Document** | MongoDB, Couchbase, Firestore | Nested, semi-structured records where the schema evolves; per-document access |
| **Column-family** | Cassandra, HBase, ScyllaDB | Massive write throughput at scale; time-series with high cardinality |
| **Graph** | Neo4j, ArangoDB, JanusGraph | Many-hop relationship queries; recommendation graphs; fraud rings |
| **Time-series** | InfluxDB, TimescaleDB, Prometheus | High-throughput append-only metrics with time-based queries |
| **Vector** | Pinecone, Weaviate, Qdrant, Milvus, pgvector | Approximate nearest-neighbor search over learned embeddings |

You will most often work with the **key-value** and **document** categories; vector databases are the rising star in ML.

---

## When to Use NoSQL Instead of SQL

NoSQL is the right choice when one or more of the following is clearly true:

1. **The access pattern is dominantly point-lookup by key.** A relational table can do this, but a key-value store does it cheaper and faster.
2. **Records are nested and the shape varies.** A blog post with comments and tags fits more naturally in one document than three joined tables. ML experiment metadata is a typical example: each run logs a different set of metrics and parameters.
3. **You need sub-millisecond latency at scale.** Redis serves millions of operations per second per node from RAM.
4. **The workload is write-heavy and append-only with predictable partition keys.** Cassandra and DynamoDB shine here.
5. **You need horizontal scale and can model around eventual consistency.** A relational primary won't scale linearly past a certain point; a sharded NoSQL store will.
6. **The query is fundamentally a similarity search over vectors.** No relational engine without `pgvector` (or similar) will do this efficiently.

Stay with SQL when:

- You need **joins** across many entities.
- You need **strong transactional guarantees** across rows (financial ledgers, inventory).
- The data is highly structured and rarely changes shape.
- The team is small and one boring relational database covers everything.

---

## MongoDB: Document Database

MongoDB stores **BSON** (binary-encoded JSON) documents in **collections** which live in **databases**. Documents in a collection do not have to share a schema, though in practice you should enforce one via application code or MongoDB's optional schema validation.

### Core Concepts

| MongoDB | Relational analog |
|---|---|
| Database | Database |
| Collection | Table |
| Document | Row |
| Field | Column |
| _id | Primary key |
| Index | Index |

Each document is uniquely identified by `_id`, which defaults to a 12-byte `ObjectId`.

### Python Quickstart: PyMongo

```python
from pymongo import MongoClient, ASCENDING
from datetime import datetime

client = MongoClient("mongodb://localhost:27017", appname="ml-platform")
db = client["mlops"]
runs = db["experiment_runs"]

# Insert a document
run_doc = {
    "experiment": "fraud-detector",
    "model_version": "v3",
    "started_at": datetime.utcnow(),
    "params": {"learning_rate": 0.01, "batch_size": 64},
    "metrics": {"auc": 0.91, "f1": 0.84},
    "tags": ["baseline", "team-payments"],
}
result = runs.insert_one(run_doc)
print(result.inserted_id)

# Query
recent_baselines = list(
    runs.find(
        {"experiment": "fraud-detector", "tags": "baseline"},
        {"_id": 0, "model_version": 1, "metrics.auc": 1},
    ).sort("started_at", -1).limit(10)
)

# Update
runs.update_one(
    {"_id": result.inserted_id},
    {"$set": {"metrics.recall": 0.78}},
)

# Index for the dominant query pattern
runs.create_index([("experiment", ASCENDING), ("started_at", -1)])
```

### Query Operators

Common operators:

- Equality, comparison: `{"value": {"$gt": 0.9}}`, `{"$in": [...]}`, `{"$ne": ...}`
- Logical: `{"$and": [...]}`, `{"$or": [...]}`, `{"$not": ...}`
- Array: `{"tags": {"$all": ["a", "b"]}}`, `{"$size": 3}`
- Existence: `{"deprecated": {"$exists": False}}`
- Pattern: `{"name": {"$regex": "^prod-"}}`

### The Aggregation Pipeline

MongoDB's aggregation framework is the analog of SQL `GROUP BY` and beyond. It is a sequence of stages applied to documents.

```python
pipeline = [
    {"$match": {"experiment": "fraud-detector"}},
    {"$group": {
        "_id": "$model_version",
        "best_auc": {"$max": "$metrics.auc"},
        "runs":    {"$sum": 1},
    }},
    {"$sort": {"best_auc": -1}},
]

for row in runs.aggregate(pipeline):
    print(row)
```

### Indexing — The One Operational Skill That Matters

The default behavior for an unindexed query is a **collection scan**, which scales linearly with the collection. Always:

1. Profile your real query patterns.
2. Create a compound index that matches the query shape (equality fields first, range/sort fields last — the "ESR rule").
3. Use `explain("executionStats")` to confirm the index is used.

```python
runs.create_index([
    ("experiment", ASCENDING),
    ("tags",       ASCENDING),
    ("started_at", -1),
])

print(runs.find({"experiment": "x"}).explain("executionStats")["executionStats"])
```

### Schema Validation

MongoDB is schema-flexible by default but you can enforce a JSON Schema on a collection:

```javascript
db.runCommand({
  collMod: "experiment_runs",
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["experiment", "model_version", "started_at"],
      properties: {
        experiment:    { bsonType: "string" },
        model_version: { bsonType: "string" },
        started_at:    { bsonType: "date" },
        metrics:       { bsonType: "object" },
      }
    }
  },
  validationLevel: "moderate"
})
```

In practice, validation via a Pydantic model in your application is usually more flexible and easier to evolve than DB-side validation.

### Transactions

MongoDB supports multi-document transactions on replica sets and sharded clusters. They work but have higher overhead than single-document atomic operations. Prefer to model data so that a logical transaction maps to a single document update; reach for transactions only when crossing documents is unavoidable.

---

## Redis: Key-Value and Data Structures

Redis is an in-memory data store. It can persist to disk, but its sweet spot is "small to medium, hot data, latency-critical." It also includes built-in data structures — lists, sets, sorted sets, hashes, streams — which let it stand in for many specialized systems.

### Where Redis Shows Up in ML

1. **Feature-store cache.** Online inference looks up features by entity id; Redis returns them in microseconds.
2. **Result cache.** Identical prediction requests (idempotent, deterministic models) can be cached.
3. **Job queue.** Celery, RQ, and Dramatiq use Redis as the message broker for batch inference and training jobs.
4. **Rate limiting.** Token-bucket counters in Redis protect prediction endpoints from runaway clients.
5. **Distributed locks.** Coordinate "only one trainer at a time" semantics across replicas.
6. **Real-time leaderboards / counters.** Sorted sets keep model latency rankings or A/B group counters.

### Python Quickstart: redis-py

```python
import redis, json, time

r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

# Strings
r.set("model:current", "v3.2.1")
print(r.get("model:current"))               # "v3.2.1"

# TTL: cache a feature vector for 60 seconds
r.set("features:user:42", json.dumps([0.1, 0.4, 0.7]), ex=60)

# Hashes — store related fields together
r.hset("user:42", mapping={"age": 35, "tier": "gold", "country": "US"})
print(r.hgetall("user:42"))

# Lists — simple FIFO queues
r.lpush("inference:queue", json.dumps({"req_id": "abc", "features": [1, 2, 3]}))
job = r.brpop("inference:queue", timeout=5)  # blocking pop

# Sets — unique membership
r.sadd("seen:request_ids", "abc", "def")
print(r.sismember("seen:request_ids", "abc"))

# Sorted sets — ranking
r.zadd("model:latency_p95", {"m1": 12.3, "m2": 9.1, "m3": 15.4})
print(r.zrange("model:latency_p95", 0, -1, withscores=True))

# Atomic counter — useful for rate limiting
count = r.incr("rate:user:42")
if count == 1:
    r.expire("rate:user:42", 60)  # reset window after 60s
if count > 100:
    raise RuntimeError("rate limit exceeded")
```

### Patterns Worth Knowing

**Cache-aside.**

```python
def get_features(user_id: str) -> list[float]:
    key = f"features:{user_id}"
    cached = r.get(key)
    if cached:
        return json.loads(cached)

    features = feature_store.fetch(user_id)        # slow
    r.set(key, json.dumps(features), ex=300)        # 5 min TTL
    return features
```

**Pipelining** to batch operations and cut round-trips:

```python
pipe = r.pipeline()
for uid in user_ids:
    pipe.get(f"features:{uid}")
results = pipe.execute()
```

**Pub/Sub** for cross-service notifications:

```python
# producer
r.publish("model.deployed", json.dumps({"version": "v3.2.1"}))

# consumer
sub = r.pubsub()
sub.subscribe("model.deployed")
for msg in sub.listen():
    if msg["type"] == "message":
        handle(json.loads(msg["data"]))
```

**Streams** for durable, replayable event logs (Redis 5+) — a small-scale Kafka substitute.

### Operational Realities

- **Memory is the constraint.** Plan capacity carefully. Use `maxmemory-policy allkeys-lru` to evict cold keys when full.
- **Persistence has trade-offs.** RDB snapshots are cheap but can lose seconds of writes; AOF gives durability at a write-amplification cost.
- **Single-threaded command execution.** Long-running commands (`KEYS *` on a big DB, large `LRANGE`) block the whole server. Use `SCAN` and avoid unbounded scans.
- **Cluster mode** shards keys across nodes by hash slot. Use hash tags (`{tag}`) when you need atomic multi-key ops on the same shard.

---

## Vector Databases for ML

Vector databases are a NoSQL category that has emerged with the rise of embedding-based ML — recommendation, semantic search, RAG (retrieval-augmented generation).

### The Problem

You have N million item embeddings (dense float vectors of dimension D, often 384 or 768 or 1536). At query time, given a new embedding, you need the top-k most similar vectors by cosine similarity or L2 distance. Doing this naively is O(N·D) per query and does not scale.

### The Tools

Approximate Nearest Neighbor (ANN) algorithms — HNSW, IVF, ScaNN — trade a small amount of recall for vastly better query latency. Vector databases package these algorithms with persistence, replication, metadata filtering, and a client API.

| Option | When to consider |
|---|---|
| **pgvector** | You already run PostgreSQL and your dataset is small to medium (< ~10M vectors). |
| **Qdrant**, **Weaviate**, **Milvus** | Self-hosted, larger scale, more advanced filtering and quantization. |
| **Pinecone** | Fully managed; pay-per-use; very simple API. |
| **Vespa**, **OpenSearch k-NN** | If you already run them for full-text search. |

### Minimal Example: Qdrant

```python
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct

client = QdrantClient(host="localhost", port=6333)

client.recreate_collection(
    collection_name="products",
    vectors_config=VectorParams(size=384, distance=Distance.COSINE),
)

client.upsert(
    collection_name="products",
    points=[
        PointStruct(id=1, vector=[...384 floats...], payload={"category": "shoes"}),
        PointStruct(id=2, vector=[...], payload={"category": "shirts"}),
    ],
)

hits = client.search(
    collection_name="products",
    query_vector=[...384 floats...],
    limit=5,
    query_filter={"must": [{"key": "category", "match": {"value": "shoes"}}]},
)
```

Vector databases will appear repeatedly in later modules (RAG-style applications, embedding pipelines). Treat this as an introduction.

---

## Consistency, Availability, and the CAP Theorem

The CAP theorem states that in the presence of a **network partition**, a distributed system must choose between **consistency** (every read sees the latest write) and **availability** (every request receives a response). Many NoSQL systems lean toward availability and accept eventual consistency.

In practice:

- **PostgreSQL primary** → strongly consistent; loses availability if the primary partitions.
- **MongoDB** → tunable: by default reads from the primary are consistent; reads from secondaries can be stale.
- **Cassandra / DynamoDB** → tunable per query (`ONE`, `QUORUM`, `ALL`); typically run with eventual consistency for throughput.
- **Redis** → single-node is strongly consistent; clustered with replication can be eventually consistent across replicas.

The right question is rarely "is this database consistent?" It is **"what consistency does my workload require?"** Model serving latency cache → eventual is fine. Bank balance → strong. Feature lookup → "as fresh as we can afford."

---

## Polyglot Persistence in ML Systems

Mature ML platforms typically use several databases together:

```
              ┌────────────────────────────────────────────┐
              │                                            │
   ┌──────────┴──────────┐                  ┌──────────────┴──────────────┐
   │  PostgreSQL          │                  │  Redis                       │
   │  user / billing      │                  │  online features,            │
   │  source-of-truth     │                  │  rate limiting, cache        │
   └──────────┬──────────┘                  └──────────────┬──────────────┘
              │                                            │
   ┌──────────┴──────────┐                  ┌──────────────┴──────────────┐
   │  MongoDB             │                  │  Vector DB (Qdrant/pgvector)│
   │  experiment metadata │                  │  embedding similarity        │
   │  model artifact catalog                 │  for RAG / recsys           │
   └──────────────────────┘                  └──────────────────────────────┘
              │
   ┌──────────┴──────────┐
   │  S3 / GCS / Blob     │
   │  model files, raw    │
   │  data, large logs    │
   └──────────────────────┘
```

This is **polyglot persistence**: pick the right store per access pattern. The cost is operational complexity and data-consistency coordination across stores. The benefit is workloads that no single database can serve well.

---

## Operational Concerns

Whatever NoSQL system you adopt, the operational checklist is largely the same:

1. **Authentication and authorization.** Default deployments often leave auth off. Always enable it before exposing the service. Use TLS in transit.
2. **Network exposure.** Never bind Redis or MongoDB to a public interface without a firewall and auth. They have been historical sources of internet-wide data breaches.
3. **Backups.** RDB/AOF for Redis, mongodump or filesystem snapshots for MongoDB, point-in-time restore where the service offers it. Test restores quarterly.
4. **Replication.** Run a replica set / cluster for high availability. Validate failover by killing the primary in staging.
5. **Monitoring.** Memory used, ops/sec, latency p50/p99, replication lag, hit ratio for caches.
6. **Resource limits.** Apply Kubernetes resource requests and limits. Memory-bound services that overshoot RAM get OOM-killed and lose the in-memory state.
7. **Capacity planning.** Key-count × average size for Redis; document count × average size + indexes for MongoDB; vectors × dimension × bytes/element for vector DBs.

---

## Summary and Key Takeaways

- **NoSQL is a family, not a database.** Pick the category — key-value, document, column-family, graph, time-series, vector — that fits the workload.
- **Don't reach for NoSQL by default.** Modern PostgreSQL handles JSON, time-series, and even vectors well at small-to-medium scale.
- **Reach for Redis** when you need a cache, a queue, a rate limiter, or microsecond key lookups.
- **Reach for MongoDB** when records are deeply nested and the schema varies per record, and your queries are mostly per-document.
- **Reach for a vector database** when the query is "give me the top-k most similar embeddings."
- **The CAP theorem** is the working framework for thinking about consistency vs availability — tune to your workload, not the database default.
- **Polyglot persistence** is the norm in ML platforms: SQL for source-of-truth, Redis for hot data, MongoDB for flexible metadata, object storage for artifacts, vector DB for similarity.
- **Operate carefully:** auth, TLS, backups, replication, monitoring, capacity. Treat NoSQL stores with the same discipline as relational ones.

The exercises for this module include a hands-on Redis caching exercise and a MongoDB experiment-tracker mini-project, where you will apply the patterns introduced here.
