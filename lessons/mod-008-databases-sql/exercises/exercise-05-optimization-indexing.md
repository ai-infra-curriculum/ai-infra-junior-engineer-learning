# Exercise 05: Database Optimization & Indexing

## Overview

Optimize the performance of your ML registry database by profiling queries, introducing indexes, and tuning configuration. You will also establish baseline monitoring dashboards so you can spot regressions early. This exercise transforms you from a database user into a performance engineer, capable of diagnosing bottlenecks and implementing targeted optimizations for production ML infrastructure.

**Difficulty:** Intermediate → Advanced
**Estimated Time:** 3-4 hours
**Prerequisites:**
- Exercises 01–04 completed (schema, advanced SQL, ORM integration)
- Lecture 04 (ORMs & Database Integration)
- Comfort with interpreting `EXPLAIN ANALYZE` output
- Basic understanding of database architecture (pages, buffers, WAL)

## Learning Objectives

By the end of this exercise, you will be able to:

1. **Profile database performance** using PostgreSQL diagnostic tools (pg_stat_statements, EXPLAIN ANALYZE)
2. **Identify query bottlenecks** through execution plan analysis and metrics
3. **Design index strategies** for different query patterns (B-tree, Hash, BRIN, GIN, partial indexes)
4. **Measure performance improvements** with before/after comparisons
5. **Implement maintenance procedures** (VACUUM, ANALYZE, REINDEX)
6. **Configure monitoring** for production database health
7. **Optimize query patterns** in application code and ORM usage
8. **Apply production best practices** for database performance management

## Scenario

Your ML model registry has been running smoothly for 3 months, but recent growth has caused performance issues:

- **Dashboard queries** taking 5-10 seconds to load (previously <500ms)
- **Training run ingestion** experiencing occasional timeouts
- **Deployment status checks** causing API slowdowns during peak hours
- **Database CPU usage** spiking to 80-90% during business hours

As the infrastructure engineer on call, you must:
1. Profile the workload to identify slow queries
2. Apply targeted optimizations (indexes, query rewrites)
3. Establish monitoring to prevent future regressions
4. Document a repeatable performance tuning process

Management expects:
- ✅ 80% reduction in P99 query latency
- ✅ Dashboard load times < 1 second
- ✅ Zero query timeouts during peak hours
- ✅ Automated monitoring and alerting

---

## Part 1: Database Performance Profiling

### Step 1.1: Enable Query Statistics

PostgreSQL provides `pg_stat_statements` for tracking query performance. Enable it:

```sql
-- Connect to your database
psql -h localhost -U ml_user -d ml_registry

-- Enable the extension
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- Verify it's working
SELECT * FROM pg_stat_statements LIMIT 5;
```

**Expected Output:**
```
 userid | dbid  | queryid  |         query          | calls | total_time | mean_time
--------+-------+----------+------------------------+-------+------------+-----------
  16384 | 16385 | 12345678 | SELECT * FROM models   |   142 |    1250.34 |      8.80
```

### Step 1.2: Configure PostgreSQL for Performance Tracking

Edit `postgresql.conf` (or set via Docker environment):

```conf
# Track statement execution statistics
shared_preload_libraries = 'pg_stat_statements'
pg_stat_statements.track = all
pg_stat_statements.max = 10000

# Enable detailed query logging for slow queries
log_min_duration_statement = 1000  # Log queries > 1 second
log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h '
log_statement = 'ddl'

# Enable auto-explain for queries > 500ms
session_preload_libraries = 'auto_explain'
auto_explain.log_min_duration = 500
auto_explain.log_analyze = true
auto_explain.log_buffers = true
auto_explain.log_timing = true
auto_explain.log_format = 'json'

# Improve statistics accuracy
default_statistics_target = 100  # Default is 100, increase for complex queries
```

**Restart PostgreSQL** to apply changes:

```bash
docker restart ml-registry-postgres
```

### Step 1.3: Generate Realistic Workload

Create a workload simulation script to generate realistic query patterns:

Create `scripts/generate_workload.py`:

```python
"""
Generate realistic workload for ML model registry.
Simulates dashboard queries, training run ingestion, and deployment checks.
"""
import time
import random
from datetime import datetime, timedelta
from uuid import uuid4

import psycopg2
from psycopg2.extras import execute_values

# Database connection
conn = psycopg2.connect(
    host="localhost",
    port=5432,
    dbname="ml_registry",
    user="ml_user",
    password="ml_password"
)

def simulate_dashboard_query():
    """Simulate slow dashboard query - latest deployments with model info."""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT
                m.model_name,
                mv.semver,
                d.environment_id,
                d.status,
                d.deployed_at,
                d.deployed_by
            FROM deployments d
            INNER JOIN model_versions mv ON d.version_id = mv.version_id
            INNER JOIN models m ON mv.model_id = m.model_id
            WHERE d.deployed_at > NOW() - INTERVAL '30 days'
            ORDER BY d.deployed_at DESC
            LIMIT 50;
        """)
        results = cur.fetchall()
        return len(results)

def simulate_training_runs_query():
    """Simulate training runs query by experiment."""
    with conn.cursor() as cur:
        experiment_name = random.choice([
            "fraud-exp-001", "churn-exp-002", "recommender-exp-003"
        ])
        cur.execute("""
            SELECT
                run_id,
                model_name,
                status,
                accuracy,
                created_at
            FROM training_runs
            WHERE experiment_name = %s
              AND created_at > NOW() - INTERVAL '7 days'
            ORDER BY accuracy DESC NULLS LAST
            LIMIT 20;
        """, (experiment_name,))
        results = cur.fetchall()
        return len(results)

def simulate_model_stats_query():
    """Simulate aggregate stats query across all models."""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT
                m.model_name,
                COUNT(DISTINCT mv.version_id) as version_count,
                COUNT(DISTINCT tr.run_id) as training_runs,
                COUNT(DISTINCT d.deployment_id) as deployments,
                MAX(tr.accuracy) as best_accuracy
            FROM models m
            LEFT JOIN model_versions mv ON m.model_id = mv.model_id
            LEFT JOIN training_runs tr ON tr.version_id = mv.version_id
            LEFT JOIN deployments d ON d.version_id = mv.version_id
            WHERE m.is_active = true
            GROUP BY m.model_id, m.model_name
            ORDER BY deployments DESC;
        """)
        results = cur.fetchall()
        return len(results)

def simulate_deployment_status_check():
    """Simulate deployment status check for specific environment."""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT
                m.model_name,
                mv.semver,
                d.status,
                d.replicas,
                d.deployed_at
            FROM deployments d
            INNER JOIN model_versions mv ON d.version_id = mv.version_id
            INNER JOIN models m ON mv.model_id = m.model_id
            WHERE d.environment_id = 1
              AND d.status = 'active'
            ORDER BY d.deployed_at DESC;
        """)
        results = cur.fetchall()
        return len(results)

def run_workload(duration_seconds=60, queries_per_second=10):
    """
    Run mixed workload for specified duration.

    Args:
        duration_seconds: How long to run workload
        queries_per_second: Target QPS
    """
    query_functions = [
        simulate_dashboard_query,
        simulate_training_runs_query,
        simulate_model_stats_query,
        simulate_deployment_status_check,
    ]

    start_time = time.time()
    query_count = 0

    print(f"Running workload for {duration_seconds}s at {queries_per_second} QPS...")

    while time.time() - start_time < duration_seconds:
        # Random query selection
        query_func = random.choice(query_functions)

        try:
            start = time.time()
            rows = query_func()
            duration = (time.time() - start) * 1000  # ms

            query_count += 1

            if duration > 100:  # Log slow queries
                print(f"  ⚠️  {query_func.__name__}: {duration:.1f}ms ({rows} rows)")

        except Exception as e:
            print(f"  ❌ Error in {query_func.__name__}: {e}")

        # Rate limiting
        time.sleep(1.0 / queries_per_second)

    elapsed = time.time() - start_time
    print(f"\nWorkload complete:")
    print(f"  Total queries: {query_count}")
    print(f"  Duration: {elapsed:.1f}s")
    print(f"  Actual QPS: {query_count / elapsed:.1f}")

if __name__ == "__main__":
    import sys

    duration = int(sys.argv[1]) if len(sys.argv) > 1 else 60
    qps = int(sys.argv[2]) if len(sys.argv) > 2 else 10

    try:
        run_workload(duration, qps)
    finally:
        conn.close()
```

**Run the workload:**

```bash
python scripts/generate_workload.py 60 10  # 60 seconds, 10 QPS
```

### Step 1.4: Capture Baseline Performance Metrics

Query `pg_stat_statements` to identify slow queries:

```sql
-- Top 10 slowest queries by total time
SELECT
    query,
    calls,
    total_exec_time / 1000 as total_time_sec,
    mean_exec_time as avg_time_ms,
    max_exec_time as max_time_ms,
    stddev_exec_time as stddev_ms,
    rows,
    100.0 * shared_blks_hit / NULLIF(shared_blks_hit + shared_blks_read, 0) AS cache_hit_ratio
FROM pg_stat_statements
WHERE query NOT LIKE '%pg_stat_statements%'
ORDER BY total_exec_time DESC
LIMIT 10;
```

**Example Output:**

```
 query                           | calls | total_time_sec | avg_time_ms | max_time_ms | cache_hit_ratio
---------------------------------+-------+----------------+-------------+-------------+-----------------
 SELECT m.model_name, mv.semver… |   245 |          35.67 |      145.58 |     1250.34 |           45.23
 SELECT run_id, model_name…      |   892 |          28.45 |       31.90 |      456.78 |           78.92
 SELECT m.model_name, COUNT…     |   156 |          22.34 |      143.21 |      890.12 |           38.45
```

**Key Metrics to Track:**

1. **total_time_sec**: Total time spent in this query (high = priority target)
2. **avg_time_ms**: Average execution time per call
3. **max_time_ms**: Worst-case latency (P100)
4. **cache_hit_ratio**: % of data found in memory vs disk (low = I/O bottleneck)
5. **calls**: How often the query runs (high + slow = critical)

### Step 1.5: Analyze Execution Plans with EXPLAIN

For each slow query, capture detailed execution plan:

```sql
EXPLAIN (ANALYZE, BUFFERS, VERBOSE, TIMING)
SELECT
    m.model_name,
    mv.semver,
    d.environment_id,
    d.status,
    d.deployed_at
FROM deployments d
INNER JOIN model_versions mv ON d.version_id = mv.version_id
INNER JOIN models m ON mv.model_id = m.model_id
WHERE d.deployed_at > NOW() - INTERVAL '30 days'
ORDER BY d.deployed_at DESC
LIMIT 50;
```

**Example Execution Plan (Before Optimization):**

```
Limit  (cost=1245.67..1246.05 rows=50 width=120) (actual time=145.234..145.567 rows=50 loops=1)
  Buffers: shared hit=2456 read=3421
  ->  Sort  (cost=1245.67..1256.78 rows=4450 width=120) (actual time=145.231..145.298 rows=50 loops=1)
        Sort Key: d.deployed_at DESC
        Sort Method: top-N heapsort  Memory: 35kB
        Buffers: shared hit=2456 read=3421
        ->  Hash Join  (cost=234.56..1134.89 rows=4450 width=120) (actual time=12.345..139.876 rows=4450 loops=1)
              Hash Cond: (mv.model_id = m.model_id)
              Buffers: shared hit=2456 read=3421
              ->  Hash Join  (cost=123.45..987.65 rows=4450 width=88) (actual time=5.678..125.432 rows=4450 loops=1)
                    Hash Cond: (d.version_id = mv.version_id)
                    Buffers: shared hit=1234 read=3421
                    ->  Seq Scan on deployments d  (cost=0.00..845.67 rows=4450 width=56) (actual time=0.023..112.345 rows=4450 loops=1)
                          Filter: (deployed_at > (now() - '30 days'::interval))
                          Rows Removed by Filter: 15678
                          Buffers: shared hit=567 read=3421
                    ->  Hash  (cost=98.76..98.76 rows=1975 width=32) (actual time=5.432..5.433 rows=1975 loops=1)
                          Buckets: 2048  Batches: 1  Memory Usage: 125kB
                          Buffers: shared hit=667
                          ->  Seq Scan on model_versions mv  (cost=0.00..98.76 rows=1975 width=32) (actual time=0.012..3.456 rows=1975 loops=1)
                                Buffers: shared hit=667
              ->  Hash  (cost=87.65..87.65 rows=1876 width=40) (actual time=6.543..6.544 rows=1876 loops=1)
                    Buckets: 2048  Batches: 1  Memory Usage: 145kB
                    Buffers: shared hit=555
                    ->  Seq Scan on models m  (cost=0.00..87.65 rows=1876 width=40) (actual time=0.015..4.234 rows=1876 loops=1)
                          Buffers: shared hit=555
Planning Time: 1.234 ms
Execution Time: 145.678 ms
```

**Key Findings from Execution Plan:**

1. **Seq Scan on deployments** (112ms): Full table scan filtering 15,678 rows → **needs index on deployed_at**
2. **Low cache hit ratio** (2,456 hit / 5,877 total = 42%): Data not in memory → **I/O bottleneck**
3. **Hash joins**: Efficient, but input data comes from slow sequential scans
4. **No index usage**: Query doesn't benefit from any existing indexes

### Step 1.6: Document Baseline Performance

Create `docs/performance-baseline.md`:

```markdown
# Performance Baseline Report

**Date**: 2025-10-23
**Database**: ml_registry (PostgreSQL 14.x)
**Workload**: 60 seconds @ 10 QPS mixed queries

---

## Executive Summary

- **Slowest Query**: Dashboard deployments view (145ms avg, 1,250ms max)
- **Primary Bottleneck**: Sequential scans on `deployments` table (no index on `deployed_at`)
- **Cache Hit Ratio**: 45% (target: >90%)
- **Total Queries Analyzed**: 4

---

## Query 1: Latest Deployments Dashboard

**Query**:
```sql
SELECT m.model_name, mv.semver, d.status, d.deployed_at
FROM deployments d
INNER JOIN model_versions mv ON d.version_id = mv.version_id
INNER JOIN models m ON mv.model_id = m.model_id
WHERE d.deployed_at > NOW() - INTERVAL '30 days'
ORDER BY d.deployed_at DESC
LIMIT 50;
```

**Metrics**:
- Calls: 245
- Total Time: 35.67 seconds
- Avg Time: 145.58 ms
- Max Time: 1,250.34 ms
- Rows Scanned: 20,128 (deployments table)
- Rows Returned: 50
- Cache Hit Ratio: 45.23%

**Execution Plan Summary**:
- Sequential scan on `deployments` (112ms)
- Hash joins on `model_versions` and `models` (33ms)
- Sort and limit (0.5ms)

**Bottleneck**: Seq Scan filtering by `deployed_at`

**Recommendation**: Add B-tree index on `deployments(deployed_at DESC)`

---

## Query 2: Training Runs by Experiment

**Query**:
```sql
SELECT run_id, model_name, status, accuracy, created_at
FROM training_runs
WHERE experiment_name = $1
  AND created_at > NOW() - INTERVAL '7 days'
ORDER BY accuracy DESC NULLS LAST
LIMIT 20;
```

**Metrics**:
- Calls: 892
- Total Time: 28.45 seconds
- Avg Time: 31.90 ms
- Max Time: 456.78 ms
- Rows Scanned: 45,670
- Rows Returned: 20
- Cache Hit Ratio: 78.92%

**Bottleneck**: Seq Scan filtering by `experiment_name` and `created_at`

**Recommendation**: Composite index on `training_runs(experiment_name, created_at DESC)`

---

## Query 3: Model Statistics Aggregation

**Query**:
```sql
SELECT
    m.model_name,
    COUNT(DISTINCT mv.version_id) as version_count,
    COUNT(DISTINCT tr.run_id) as training_runs,
    MAX(tr.accuracy) as best_accuracy
FROM models m
LEFT JOIN model_versions mv ON m.model_id = mv.model_id
LEFT JOIN training_runs tr ON tr.version_id = mv.version_id
WHERE m.is_active = true
GROUP BY m.model_id, m.model_name
ORDER BY version_count DESC;
```

**Metrics**:
- Calls: 156
- Total Time: 22.34 seconds
- Avg Time: 143.21 ms
- Max Time: 890.12 ms
- Rows Scanned: 67,890
- Rows Returned: 42
- Cache Hit Ratio: 38.45%

**Bottleneck**: Multiple joins with sequential scans on `training_runs`

**Recommendation**: Index on `training_runs(version_id)` for join optimization

---

## Query 4: Active Deployments by Environment

**Query**:
```sql
SELECT m.model_name, mv.semver, d.status, d.deployed_at
FROM deployments d
INNER JOIN model_versions mv ON d.version_id = mv.version_id
INNER JOIN models m ON mv.model_id = m.model_id
WHERE d.environment_id = 1 AND d.status = 'active'
ORDER BY d.deployed_at DESC;
```

**Metrics**:
- Calls: 421
- Total Time: 18.92 seconds
- Avg Time: 44.94 ms
- Max Time: 234.56 ms
- Rows Scanned: 20,128
- Rows Returned: 12
- Cache Hit Ratio: 56.78%

**Bottleneck**: Seq Scan filtering by `environment_id` and `status`

**Recommendation**: Partial index on active production deployments

---

## Summary of Optimization Targets

| Query | Avg Time (Before) | Target Time | Priority | Index Strategy |
|-------|-------------------|-------------|----------|----------------|
| Q1: Deployments Dashboard | 145ms | <30ms | HIGH | B-tree on deployed_at |
| Q2: Training Runs by Exp | 32ms | <10ms | MEDIUM | Composite (experiment, created_at) |
| Q3: Model Stats | 143ms | <50ms | HIGH | Foreign key indexes |
| Q4: Active Deployments | 45ms | <15ms | MEDIUM | Partial index (env + status) |

**Total Expected Improvement**: 75-85% reduction in query latency
```

### Checkpoint 1

✅ Verify your profiling setup:

```bash
# Check pg_stat_statements is enabled
psql -h localhost -U ml_user -d ml_registry -c "SELECT COUNT(*) FROM pg_stat_statements;"

# Verify baseline document exists
ls -la docs/performance-baseline.md

# Review captured slow queries
grep "Avg Time" docs/performance-baseline.md
```

---

## Part 2: Index Strategy and Implementation

### Step 2.1: Understanding PostgreSQL Index Types

**Index Types and Use Cases:**

| Index Type | Use Case | Example | Performance Characteristics |
|------------|----------|---------|----------------------------|
| **B-tree** (default) | Equality, range queries, sorting | `created_at`, `status`, foreign keys | Best general-purpose, balanced read/write |
| **Hash** | Equality only (=) | `uuid` lookups | Faster than B-tree for equality, no range support |
| **GIN** (Generalized Inverted Index) | JSONB, arrays, full-text search | `metadata @> '{"framework": "pytorch"}'` | Large index size, slower writes, fast reads |
| **GiST** (Generalized Search Tree) | Geometric data, ranges | PostGIS, `tsrange` overlap | Lossy, requires recheck |
| **BRIN** (Block Range Index) | Large tables with natural ordering | Time-series `created_at` on append-only table | Tiny index size, fast writes, moderate reads |
| **Partial** | Subset of rows | `WHERE status = 'active'` | Small index, very fast for filtered queries |
| **Expression** | Function results | `LOWER(email)` | Index computed values |

### Step 2.2: Identify Index Candidates

Use this decision tree:

```
Query has WHERE/JOIN clause?
├─ YES: What columns are filtered/joined?
│  ├─ Single column + range/sort → B-tree
│  ├─ Multiple columns → Composite B-tree (order matters!)
│  ├─ JSONB queries → GIN
│  ├─ Equality only on UUID/hash → Hash
│  └─ Time-series on large table → BRIN
└─ NO: Query does aggregation?
   └─ YES: Index columns used in GROUP BY/ORDER BY
```

**Analyze Each Slow Query:**

**Query 1 Analysis**: Latest Deployments Dashboard

```sql
WHERE d.deployed_at > NOW() - INTERVAL '30 days'  -- Range filter
ORDER BY d.deployed_at DESC                       -- Sorting
```

**Decision**: B-tree index on `deployments(deployed_at DESC)`
- **Why DESC?**: Matches ORDER BY direction, enables index-only scan
- **Why B-tree?**: Range queries (>) and sorting

---

**Query 2 Analysis**: Training Runs by Experiment

```sql
WHERE experiment_name = $1                -- Equality filter
  AND created_at > NOW() - INTERVAL '7 days'  -- Range filter
ORDER BY accuracy DESC NULLS LAST
```

**Decision**: Composite index on `training_runs(experiment_name, created_at DESC, accuracy DESC)`
- **Column order**: Most selective first (experiment_name), then range filter
- **Include accuracy**: Supports ORDER BY, enables covering index

---

**Query 3 Analysis**: Model Statistics

```sql
LEFT JOIN training_runs tr ON tr.version_id = mv.version_id  -- Foreign key join
```

**Decision**: B-tree index on `training_runs(version_id)`
- **Why?**: Foreign key joins are common, this enables nested loop joins
- **Note**: This should have been created with the foreign key constraint!

---

**Query 4 Analysis**: Active Deployments

```sql
WHERE d.environment_id = 1 AND d.status = 'active'  -- Filters on subset
```

**Decision**: Partial index on `deployments(version_id, deployed_at DESC) WHERE environment_id = 1 AND status = 'active'`
- **Why partial?**: Only ~5% of deployments match filter
- **Benefit**: Smaller index, faster updates on non-production deployments

### Step 2.3: Calculate Index Selectivity

Before creating indexes, estimate their effectiveness:

```sql
-- Check column selectivity (lower = more selective = better index)
SELECT
    'deployed_at' as column_name,
    COUNT(DISTINCT deployed_at)::float / COUNT(*)::float as selectivity,
    COUNT(*) as total_rows
FROM deployments
UNION ALL
SELECT
    'status',
    COUNT(DISTINCT status)::float / COUNT(*)::float,
    COUNT(*)
FROM deployments
UNION ALL
SELECT
    'environment_id',
    COUNT(DISTINCT environment_id)::float / COUNT(*)::float,
    COUNT(*)
FROM deployments;
```

**Example Output:**

```
 column_name    | selectivity | total_rows
----------------+-------------+------------
 deployed_at    |       0.956 |      20128  ← High selectivity, good for index
 status         |       0.032 |      20128  ← Low selectivity (only 5 statuses)
 environment_id |       0.015 |      20128  ← Low selectivity (only 3 environments)
```

**Interpretation:**
- **High selectivity (>0.8)**: Excellent index candidate
- **Medium selectivity (0.3-0.8)**: Good for composite indexes or partial indexes
- **Low selectivity (<0.3)**: Use only in composite indexes or with partial index

### Step 2.4: Create Index Strategy Document

Create `docs/index-strategy.md`:

```markdown
# Index Strategy for ML Model Registry

## Indexing Principles

1. **Index Foreign Keys**: Enable efficient joins
2. **Index WHERE Clauses**: Columns frequently filtered
3. **Index ORDER BY**: Support sorting without in-memory sort
4. **Composite Indexes**: Column order = selectivity (high → low)
5. **Covering Indexes**: Include columns to enable index-only scans
6. **Partial Indexes**: Filter to subset when possible
7. **Monitor Size**: Each index adds write overhead and storage

---

## Proposed Indexes

### Priority 1: Foreign Key Indexes (Missing!)

These should have been created automatically but weren't:

| Table | Column | Type | Rationale |
|-------|--------|------|-----------|
| `model_versions` | `model_id` | B-tree | FK join to models |
| `training_runs` | `version_id` | B-tree | FK join to model_versions |
| `deployments` | `version_id` | B-tree | FK join to model_versions |
| `deployments` | `environment_id` | B-tree | FK join to environments |
| `approvals` | `version_id` | B-tree | FK join to model_versions |

**Impact**: Enable nested loop joins instead of hash joins (10-50x faster for small result sets)

---

### Priority 2: Time-Range Query Indexes

| Table | Index Definition | Type | Use Case |
|-------|------------------|------|----------|
| `deployments` | `(deployed_at DESC)` | B-tree | Dashboard queries filtering recent deployments |
| `training_runs` | `(created_at DESC)` | B-tree | Recent training runs, time-series analytics |
| `training_runs` | `(started_at)` | BRIN | Large table, append-only pattern |
| `model_versions` | `(registered_at DESC)` | B-tree | Latest version queries |

**Impact**: Eliminate sequential scans on time-range filters (100x+ faster)

---

### Priority 3: Composite Indexes for Common Query Patterns

| Table | Index Definition | Covering Columns | Query Pattern |
|-------|------------------|------------------|---------------|
| `training_runs` | `(experiment_name, created_at DESC)` | `accuracy, status` | Experiment dashboard |
| `training_runs` | `(model_name, status)` | `accuracy, created_at` | Model success rate |
| `deployments` | `(environment_id, status, deployed_at DESC)` | `version_id` | Active deployments by env |

**Impact**: Support multiple filters + sort in single index scan

---

### Priority 4: Partial Indexes for Hot Queries

| Table | Index Definition | Filter Condition | Size Reduction |
|-------|------------------|------------------|----------------|
| `deployments` | `(version_id, deployed_at DESC)` | `WHERE environment_id = 1 AND status = 'active'` | 95% smaller |
| `training_runs` | `(model_name, created_at DESC)` | `WHERE status = 'succeeded'` | 80% smaller |
| `approvals` | `(version_id, approved_at DESC)` | `WHERE status = 'approved'` | 70% smaller |

**Impact**: Dramatically smaller indexes, faster updates, targeted queries

---

### Priority 5: JSONB Indexes for Metadata Queries

| Table | Index Definition | Type | Query Pattern |
|-------|------------------|------|---------------|
| `training_runs` | `USING GIN (hyperparameters)` | GIN | Search by hyperparameter values |
| `training_runs` | `USING GIN (metrics)` | GIN | Find runs with specific metrics |
| `model_versions` | `USING GIN (metadata_)` | GIN | Search model metadata |

**Impact**: Enable fast JSONB queries (`@>`, `?`, `?&` operators)

---

## Index Size Estimates

| Index Category | Count | Estimated Size | Write Overhead |
|----------------|-------|----------------|----------------|
| Foreign Keys | 5 | ~50 MB | +5% write time |
| Time-Range | 4 | ~80 MB | +8% write time |
| Composite | 3 | ~120 MB | +12% write time |
| Partial | 3 | ~30 MB | +2% write time (filtered) |
| JSONB | 3 | ~200 MB | +20% write time |
| **Total** | **18** | **~480 MB** | **+47% write overhead** |

**Trade-off Analysis**: 480 MB additional storage and ~50% slower writes for 10-100x faster reads

**Recommendation**: Implement Priority 1-3 immediately, evaluate Priority 4-5 based on workload

---

## Maintenance Plan

- **REINDEX**: Monthly for heavily updated indexes
- **VACUUM ANALYZE**: Weekly or after bulk operations
- **Monitor Bloat**: Index bloat > 50% requires REINDEX
- **Track Unused Indexes**: Remove if `idx_scan = 0` after 30 days
```

### Step 2.5: Implement Indexes (DDL Script)

Create `sql/50_indexes.sql`:

```sql
-- =============================================================================
-- ML Model Registry - Performance Indexes
-- =============================================================================
-- This script creates indexes to optimize query performance.
-- All indexes use CONCURRENTLY to avoid blocking production writes.
--
-- Estimated execution time: 5-15 minutes (depending on data volume)
-- =============================================================================

-- Enable timing
\timing on

-- Show progress
\echo '================================'
\echo 'Creating Performance Indexes'
\echo '================================'

-- =============================================================================
-- Priority 1: Foreign Key Indexes (Critical)
-- =============================================================================

\echo '\n[1/18] Creating index on model_versions(model_id)...'
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_model_versions_model_id
    ON model_versions (model_id);

\echo '[2/18] Creating index on training_runs(version_id)...'
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_training_runs_version_id
    ON training_runs (version_id);

\echo '[3/18] Creating index on deployments(version_id)...'
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_deployments_version_id
    ON deployments (version_id);

\echo '[4/18] Creating index on deployments(environment_id)...'
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_deployments_environment_id
    ON deployments (environment_id);

\echo '[5/18] Creating index on approvals(version_id)...'
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_approvals_version_id
    ON approvals (version_id);

-- =============================================================================
-- Priority 2: Time-Range Query Indexes
-- =============================================================================

\echo '[6/18] Creating index on deployments(deployed_at DESC)...'
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_deployments_deployed_at_desc
    ON deployments (deployed_at DESC);

\echo '[7/18] Creating index on training_runs(created_at DESC)...'
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_training_runs_created_at_desc
    ON training_runs (created_at DESC);

\echo '[8/18] Creating BRIN index on training_runs(started_at)...'
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_training_runs_started_at_brin
    ON training_runs USING BRIN (started_at)
    WITH (pages_per_range = 128);  -- Tune based on table size

\echo '[9/18] Creating index on model_versions(registered_at DESC)...'
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_model_versions_registered_at_desc
    ON model_versions (registered_at DESC);

-- =============================================================================
-- Priority 3: Composite Indexes for Common Queries
-- =============================================================================

\echo '[10/18] Creating composite index on training_runs(experiment_name, created_at)...'
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_training_runs_exp_created
    ON training_runs (experiment_name, created_at DESC)
    INCLUDE (accuracy, status);  -- Covering index for SELECT fields

\echo '[11/18] Creating composite index on training_runs(model_name, status)...'
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_training_runs_model_status
    ON training_runs (model_name, status)
    INCLUDE (accuracy, created_at);

\echo '[12/18] Creating composite index on deployments(environment, status, deployed_at)...'
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_deployments_env_status_deployed
    ON deployments (environment_id, status, deployed_at DESC)
    INCLUDE (version_id);

-- =============================================================================
-- Priority 4: Partial Indexes for Hot Queries
-- =============================================================================

\echo '[13/18] Creating partial index on active production deployments...'
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_deployments_prod_active
    ON deployments (version_id, deployed_at DESC)
    WHERE environment_id = 1 AND status = 'active';

\echo '[14/18] Creating partial index on successful training runs...'
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_training_runs_succeeded
    ON training_runs (model_name, created_at DESC)
    INCLUDE (accuracy, run_id)
    WHERE status = 'succeeded';

\echo '[15/18] Creating partial index on approved versions...'
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_approvals_approved
    ON approvals (version_id, approved_at DESC)
    WHERE status = 'approved';

-- =============================================================================
-- Priority 5: JSONB Indexes for Metadata Queries
-- =============================================================================

\echo '[16/18] Creating GIN index on training_runs.hyperparameters...'
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_training_runs_hyperparameters_gin
    ON training_runs USING GIN (hyperparameters jsonb_path_ops);

\echo '[17/18] Creating GIN index on training_runs.metrics...'
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_training_runs_metrics_gin
    ON training_runs USING GIN (metrics jsonb_path_ops);

\echo '[18/18] Creating GIN index on model_versions.metadata_...'
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_model_versions_metadata_gin
    ON model_versions USING GIN (metadata_ jsonb_path_ops);

-- =============================================================================
-- Verify Index Creation
-- =============================================================================

\echo '\n================================'
\echo 'Verifying Indexes'
\echo '================================'

SELECT
    schemaname,
    tablename,
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) as index_size
FROM pg_indexes
LEFT JOIN pg_class ON pg_class.relname = indexname
WHERE schemaname = 'public'
  AND indexname LIKE 'idx_%'
ORDER BY tablename, indexname;

-- =============================================================================
-- Analyze Tables to Update Statistics
-- =============================================================================

\echo '\n================================'
\echo 'Updating Table Statistics'
\echo '================================'

ANALYZE VERBOSE models;
ANALYZE VERBOSE model_versions;
ANALYZE VERBOSE training_runs;
ANALYZE VERBOSE deployments;
ANALYZE VERBOSE approvals;

\echo '\n================================'
\echo 'Index Creation Complete!'
\echo '================================'
```

**Execute the script:**

```bash
# Apply indexes (this will take 5-15 minutes)
psql -h localhost -U ml_user -d ml_registry -f sql/50_indexes.sql

# Monitor progress in another terminal
watch -n 2 "psql -h localhost -U ml_user -d ml_registry -c \"
    SELECT
        now() - query_start AS duration,
        state,
        query
    FROM pg_stat_activity
    WHERE query LIKE '%CREATE INDEX%' AND state != 'idle';
\""
```

### Step 2.6: Verify Index Usage

After creating indexes, verify they're being used:

```sql
-- Check index sizes
SELECT
    schemaname,
    tablename,
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) as size,
    idx_scan as scans,
    idx_tup_read as tuples_read,
    idx_tup_fetch as tuples_fetched
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY pg_relation_size(indexrelid) DESC;
```

**Re-run slow query with EXPLAIN:**

```sql
EXPLAIN (ANALYZE, BUFFERS, VERBOSE)
SELECT
    m.model_name,
    mv.semver,
    d.status,
    d.deployed_at
FROM deployments d
INNER JOIN model_versions mv ON d.version_id = mv.version_id
INNER JOIN models m ON mv.model_id = m.model_id
WHERE d.deployed_at > NOW() - INTERVAL '30 days'
ORDER BY d.deployed_at DESC
LIMIT 50;
```

**Expected Plan (After Optimization):**

```
Limit  (cost=45.67..46.05 rows=50 width=120) (actual time=8.234..8.567 rows=50 loops=1)
  Buffers: shared hit=156 read=12
  ->  Nested Loop  (cost=1.23..89.45 rows=4450 width=120) (actual time=0.345..8.123 rows=50 loops=1)
        Buffers: shared hit=156 read=12
        ->  Nested Loop  (cost=0.82..45.67 rows=4450 width=88) (actual time=0.234..5.678 rows=50 loops=1)
              Buffers: shared hit=98 read=12
              ->  Index Scan Backward using idx_deployments_deployed_at_desc on deployments d
                  (cost=0.42..23.45 rows=4450 width=56) (actual time=0.123..2.345 rows=50 loops=1)
                    Index Cond: (deployed_at > (now() - '30 days'::interval))
                    Buffers: shared hit=12 read=4
              ->  Index Scan using model_versions_pkey on model_versions mv
                  (cost=0.40..0.48 rows=1 width=32) (actual time=0.034..0.035 rows=1 loops=50)
                    Index Cond: (version_id = d.version_id)
                    Buffers: shared hit=86 read=8
        ->  Index Scan using models_pkey on models m
              (cost=0.41..0.49 rows=1 width=40) (actual time=0.023..0.024 rows=1 loops=50)
              Index Cond: (model_id = mv.model_id)
              Buffers: shared hit=58
Planning Time: 0.876 ms
Execution Time: 8.678 ms
```

**Improvements:**
- ✅ **Execution time**: 145ms → 8.7ms (16x faster!)
- ✅ **Index scans** instead of sequential scans
- ✅ **Nested loops** instead of hash joins (better for LIMIT queries)
- ✅ **Buffer usage**: 5,877 blocks → 168 blocks (35x less I/O)
- ✅ **Backward index scan** leverages DESC index

### Checkpoint 2

✅ Verify indexes are working:

```bash
# Check all indexes were created
psql -h localhost -U ml_user -d ml_registry -c "
    SELECT COUNT(*) as total_indexes
    FROM pg_indexes
    WHERE schemaname = 'public' AND indexname LIKE 'idx_%';
"

# Verify index usage
psql -h localhost -U ml_user -d ml_registry -c "
    SELECT tablename, indexname, idx_scan
    FROM pg_stat_user_indexes
    WHERE schemaname = 'public'
    ORDER BY idx_scan DESC
    LIMIT 10;
"
```

---

## Part 3: Performance Measurement and Validation

### Step 3.1: Re-run Workload After Optimization

```bash
# Clear pg_stat_statements to get fresh metrics
psql -h localhost -U ml_user -d ml_registry -c "SELECT pg_stat_statements_reset();"

# Run workload again
python scripts/generate_workload.py 60 10

# Capture new metrics
psql -h localhost -U ml_user -d ml_registry -c "
    SELECT
        LEFT(query, 80) as query_preview,
        calls,
        ROUND(mean_exec_time::numeric, 2) as avg_ms,
        ROUND(max_exec_time::numeric, 2) as max_ms,
        ROUND(100.0 * shared_blks_hit / NULLIF(shared_blks_hit + shared_blks_read, 0), 1) AS cache_hit_pct
    FROM pg_stat_statements
    WHERE query NOT LIKE '%pg_stat%'
    ORDER BY mean_exec_time DESC
    LIMIT 10;
"
```

### Step 3.2: Create Before/After Comparison

Create `docs/performance-results.md`:

```markdown
# Performance Optimization Results

**Optimization Date**: 2025-10-23
**Method**: Index implementation (18 indexes created)
**Test Duration**: 60 seconds @ 10 QPS

---

## Summary of Improvements

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| **Avg Query Latency (P50)** | 145ms | 12ms | **92% faster** |
| **Max Query Latency (P99)** | 1,250ms | 45ms | **96% faster** |
| **Cache Hit Ratio** | 45% | 94% | **+49 percentage points** |
| **Queries >1s** | 18 (7.3%) | 0 (0%) | **100% eliminated** |
| **Total Query Time** | 35.67s | 2.89s | **92% reduction** |
| **Database CPU Usage** | 78% | 23% | **-55 percentage points** |

---

## Per-Query Improvements

### Query 1: Latest Deployments Dashboard

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Avg Time | 145.58ms | 8.67ms | **94% faster** |
| Max Time | 1,250.34ms | 23.45ms | **98% faster** |
| Cache Hit | 45.23% | 95.67% | +50.44pp |
| Execution Plan | Seq Scan → Sort | Index Scan (backwards) | ✅ |

**Index Used**: `idx_deployments_deployed_at_desc`

---

### Query 2: Training Runs by Experiment

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Avg Time | 31.90ms | 5.12ms | **84% faster** |
| Max Time | 456.78ms | 18.90ms | **96% faster** |
| Cache Hit | 78.92% | 97.34% | +18.42pp |
| Execution Plan | Seq Scan → Filter | Index Scan | ✅ |

**Index Used**: `idx_training_runs_exp_created` (composite + covering)

---

### Query 3: Model Statistics Aggregation

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Avg Time | 143.21ms | 18.34ms | **87% faster** |
| Max Time | 890.12ms | 67.89ms | **92% faster** |
| Cache Hit | 38.45% | 91.23% | +52.78pp |
| Execution Plan | Hash Join | Nested Loop (indexed) | ✅ |

**Indexes Used**: `idx_training_runs_version_id`, `idx_model_versions_model_id`

---

### Query 4: Active Deployments by Environment

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Avg Time | 44.94ms | 2.34ms | **95% faster** |
| Max Time | 234.56ms | 8.12ms | **97% faster** |
| Cache Hit | 56.78% | 98.45% | +41.67pp |
| Execution Plan | Seq Scan → Filter | Partial Index Scan | ✅ |

**Index Used**: `idx_deployments_prod_active` (partial index)

---

## Index Effectiveness Analysis

| Index | Size | Scans | Tuples Read | Effectiveness |
|-------|------|-------|-------------|---------------|
| `idx_deployments_deployed_at_desc` | 8.2 MB | 245 | 12,250 | ⭐⭐⭐⭐⭐ High |
| `idx_training_runs_exp_created` | 15.4 MB | 892 | 17,840 | ⭐⭐⭐⭐⭐ High |
| `idx_training_runs_version_id` | 12.1 MB | 1,248 | 67,890 | ⭐⭐⭐⭐⭐ High |
| `idx_deployments_prod_active` | 0.9 MB | 421 | 5,052 | ⭐⭐⭐⭐⭐ High (partial) |
| `idx_model_versions_model_id` | 6.7 MB | 2,134 | 89,234 | ⭐⭐⭐⭐⭐ High |
| `idx_training_runs_hyperparameters_gin` | 45.2 MB | 0 | 0 | ⚠️ Unused (consider dropping) |
| `idx_training_runs_metrics_gin` | 38.9 MB | 0 | 0 | ⚠️ Unused (consider dropping) |

---

## Cost-Benefit Analysis

**Benefits**:
- 92% average query latency reduction
- Zero query timeouts
- 94% cache hit ratio (near optimal)
- 55% reduction in CPU usage
- Enabled scaling to 10x current traffic

**Costs**:
- 478 MB additional storage (index size)
- ~47% increase in INSERT/UPDATE time (measured)
- ~8 minutes for index creation (one-time)
- Ongoing maintenance (REINDEX monthly)

**Recommendation**: **Massive win**. Trade-off heavily favors indexes for read-heavy ML registry workload.

---

## Lessons Learned

1. **Foreign key indexes are critical**: Biggest wins came from indexing FK columns
2. **Composite indexes beat multiple single-column indexes**: Query planner uses one well-designed composite index vs multiple separate indexes
3. **Partial indexes are underused**: 95% size reduction for hot queries
4. **JSONB indexes are expensive**: Only create if you have queries using them
5. **Measure, don't guess**: EXPLAIN ANALYZE revealed actual bottlenecks

---

## Next Steps

1. ✅ Monitor index usage for 7 days
2. ✅ Drop unused JSONB indexes (`idx_training_runs_hyperparameters_gin`, `idx_training_runs_metrics_gin`)
3. ✅ Set up automated alerts for slow queries (>100ms)
4. ✅ Schedule monthly REINDEX for high-churn tables
5. ✅ Document index maintenance in runbook
```

### Step 3.3: Identify Unused Indexes

After running for a week, check for unused indexes:

```sql
-- Find indexes that have never been scanned
SELECT
    schemaname,
    tablename,
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) as size,
    idx_scan as scans,
    idx_tup_read as tuples_read
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
  AND idx_scan = 0
  AND indexname LIKE 'idx_%'
ORDER BY pg_relation_size(indexrelid) DESC;
```

**Drop unused indexes:**

```sql
-- If confirmed unused after 30 days
DROP INDEX CONCURRENTLY IF EXISTS idx_training_runs_hyperparameters_gin;
DROP INDEX CONCURRENTLY IF EXISTS idx_training_runs_metrics_gin;
```

### Checkpoint 3

✅ Validate performance improvements:

```bash
# Compare before/after metrics
diff docs/performance-baseline.md docs/performance-results.md

# Check for unused indexes
psql -h localhost -U ml_user -d ml_registry -c "
    SELECT COUNT(*) as unused_indexes
    FROM pg_stat_user_indexes
    WHERE idx_scan = 0 AND indexname LIKE 'idx_%';
"

# Verify cache hit ratio improved
psql -h localhost -U ml_user -d ml_registry -c "
    SELECT
        ROUND(100.0 * sum(blks_hit) / NULLIF(sum(blks_hit + blks_read), 0), 2) AS cache_hit_ratio
    FROM pg_stat_database
    WHERE datname = 'ml_registry';
"
```

---

## Part 4: Database Maintenance and Monitoring

### Step 4.1: Understanding VACUUM and ANALYZE

**PostgreSQL Maintenance Concepts:**

1. **VACUUM**: Reclaims space from dead tuples (deleted/updated rows)
   - **VACUUM**: Mark space as reusable (non-blocking)
   - **VACUUM FULL**: Rewrite table to compact space (blocks writes, use sparingly)
   - **Autovacuum**: Automatic background vacuum process

2. **ANALYZE**: Update table statistics for query planner
   - Tracks data distribution for optimization decisions
   - Should run after bulk inserts/updates
   - Automatically runs with autovacuum

3. **REINDEX**: Rebuild bloated indexes
   - Fixes index bloat from many updates
   - Use `REINDEX CONCURRENTLY` (PostgreSQL 12+) to avoid blocking

### Step 4.2: Manual Maintenance Operations

Create `scripts/maintenance.sql`:

```sql
-- =============================================================================
-- Database Maintenance Script
-- Run weekly or after bulk operations
-- =============================================================================

\timing on
\echo '================================'
\echo 'Running Database Maintenance'
\echo '================================'

-- =============================================================================
-- Step 1: Vacuum with Statistics Update
-- =============================================================================

\echo '\n[1/4] VACUUM ANALYZE: models...'
VACUUM (VERBOSE, ANALYZE, SKIP_LOCKED) models;

\echo '[2/4] VACUUM ANALYZE: model_versions...'
VACUUM (VERBOSE, ANALYZE, SKIP_LOCKED) model_versions;

\echo '[3/4] VACUUM ANALYZE: training_runs...'
VACUUM (VERBOSE, ANALYZE, SKIP_LOCKED) training_runs;

\echo '[4/4] VACUUM ANALYZE: deployments...'
VACUUM (VERBOSE, ANALYZE, SKIP_LOCKED) deployments;

-- =============================================================================
-- Step 2: Check for Bloat
-- =============================================================================

\echo '\n================================'
\echo 'Checking Table Bloat'
\echo '================================'

SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS total_size,
    pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) AS table_size,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename) - pg_relation_size(schemaname||'.'||tablename)) AS index_size,
    ROUND(100 * (pg_total_relation_size(schemaname||'.'||tablename) - pg_relation_size(schemaname||'.'||tablename))::numeric / NULLIF(pg_total_relation_size(schemaname||'.'||tablename), 0), 2) AS index_ratio
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- =============================================================================
-- Step 3: Check for Index Bloat (requires pgstattuple extension)
-- =============================================================================

CREATE EXTENSION IF NOT EXISTS pgstattuple;

\echo '\n================================'
\echo 'Checking Index Bloat'
\echo '================================'

SELECT
    schemaname,
    tablename,
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) AS index_size,
    ROUND((pgstatindex(indexrelid)).avg_leaf_density, 2) AS leaf_density,
    CASE
        WHEN (pgstatindex(indexrelid)).avg_leaf_density < 70 THEN 'High Bloat - Consider REINDEX'
        WHEN (pgstatindex(indexrelid)).avg_leaf_density < 85 THEN 'Moderate Bloat'
        ELSE 'Healthy'
    END AS status
FROM pg_indexes
JOIN pg_class ON pg_class.relname = indexname
WHERE schemaname = 'public'
  AND indexname LIKE 'idx_%'
  AND pg_relation_size(indexrelid) > 1024 * 1024  -- Only check indexes > 1MB
ORDER BY (pgstatindex(indexrelid)).avg_leaf_density ASC;

-- =============================================================================
-- Step 4: Update Extended Statistics (for multi-column correlations)
-- =============================================================================

\echo '\n================================'
\echo 'Creating Extended Statistics'
\echo '================================'

-- Create extended statistics for correlated columns
CREATE STATISTICS IF NOT EXISTS training_runs_exp_created_stats (dependencies)
    ON experiment_name, created_at
    FROM training_runs;

CREATE STATISTICS IF NOT EXISTS deployments_env_status_stats (dependencies)
    ON environment_id, status
    FROM deployments;

-- Update statistics
ANALYZE training_runs;
ANALYZE deployments;

\echo '\n================================'
\echo 'Maintenance Complete!'
\echo '================================'
```

**Execute maintenance:**

```bash
psql -h localhost -U ml_user -d ml_registry -f scripts/maintenance.sql
```

### Step 4.3: Configure Autovacuum

Edit `postgresql.conf`:

```conf
# Autovacuum Configuration (aggressive for high-write workload)
autovacuum = on
autovacuum_max_workers = 4  # Number of parallel workers
autovacuum_naptime = 30s    # Check interval (default 1min)

# Trigger vacuum when 20% of table is dead tuples OR 10,000 rows
autovacuum_vacuum_scale_factor = 0.2
autovacuum_vacuum_threshold = 10000

# Trigger analyze when 10% of table changes OR 5,000 rows
autovacuum_analyze_scale_factor = 0.1
autovacuum_analyze_threshold = 5000

# Per-table overrides for high-churn tables
# ALTER TABLE training_runs SET (autovacuum_vacuum_scale_factor = 0.1);
# ALTER TABLE deployments SET (autovacuum_vacuum_scale_factor = 0.1);
```

**Monitor autovacuum activity:**

```sql
-- Check last autovacuum/analyze times
SELECT
    schemaname,
    relname,
    last_vacuum,
    last_autovacuum,
    last_analyze,
    last_autoanalyze,
    n_tup_ins as inserts,
    n_tup_upd as updates,
    n_tup_del as deletes,
    n_dead_tup as dead_tuples
FROM pg_stat_user_tables
WHERE schemaname = 'public'
ORDER BY n_dead_tup DESC;
```

### Step 4.4: Set Up Monitoring with Prometheus

Create `docker-compose.monitoring.yml`:

```yaml
version: '3.8'

services:
  postgres-exporter:
    image: prometheuscommunity/postgres-exporter:latest
    container_name: postgres-exporter
    environment:
      DATA_SOURCE_NAME: "postgresql://ml_user:ml_password@ml-registry-postgres:5432/ml_registry?sslmode=disable"
      PG_EXPORTER_EXTEND_QUERY_PATH: "/etc/postgres_exporter/queries.yaml"
    ports:
      - "9187:9187"
    volumes:
      - ./monitoring/postgres_queries.yaml:/etc/postgres_exporter/queries.yaml:ro
    networks:
      - ml-registry-network

  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus-data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.retention.time=30d'
    networks:
      - ml-registry-network

  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
      - GF_USERS_ALLOW_SIGN_UP=false
    volumes:
      - grafana-data:/var/lib/grafana
      - ./monitoring/grafana-dashboards:/etc/grafana/provisioning/dashboards:ro
      - ./monitoring/grafana-datasources.yml:/etc/grafana/provisioning/datasources/datasources.yml:ro
    networks:
      - ml-registry-network

volumes:
  prometheus-data:
  grafana-data:

networks:
  ml-registry-network:
    external: true
```

Create `monitoring/postgres_queries.yaml`:

```yaml
# Custom PostgreSQL metrics for ML model registry

pg_database_size:
  query: "SELECT pg_database_size(current_database()) as bytes"
  metrics:
    - bytes:
        usage: "GAUGE"
        description: "Database size in bytes"

pg_slow_queries:
  query: |
    SELECT COUNT(*) as count
    FROM pg_stat_statements
    WHERE mean_exec_time > 100
  metrics:
    - count:
        usage: "GAUGE"
        description: "Number of queries with avg execution time > 100ms"

pg_cache_hit_ratio:
  query: |
    SELECT
      ROUND(100.0 * sum(blks_hit) / NULLIF(sum(blks_hit + blks_read), 0), 2) AS ratio
    FROM pg_stat_database
    WHERE datname = current_database()
  metrics:
    - ratio:
        usage: "GAUGE"
        description: "Cache hit ratio percentage"

pg_table_sizes:
  query: |
    SELECT
      schemaname || '.' || tablename as table_name,
      pg_total_relation_size(schemaname||'.'||tablename) as bytes
    FROM pg_tables
    WHERE schemaname = 'public'
  metrics:
    - table_name:
        usage: "LABEL"
        description: "Table name"
    - bytes:
        usage: "GAUGE"
        description: "Total table size including indexes"

pg_index_usage:
  query: |
    SELECT
      schemaname || '.' || indexname as index_name,
      idx_scan as scans,
      pg_relation_size(indexrelid) as bytes
    FROM pg_stat_user_indexes
    WHERE schemaname = 'public'
  metrics:
    - index_name:
        usage: "LABEL"
        description: "Index name"
    - scans:
        usage: "COUNTER"
        description: "Number of index scans"
    - bytes:
        usage: "GAUGE"
        description: "Index size in bytes"

pg_deadlocks:
  query: "SELECT deadlocks as count FROM pg_stat_database WHERE datname = current_database()"
  metrics:
    - count:
        usage: "COUNTER"
        description: "Number of deadlocks detected"

pg_connections:
  query: |
    SELECT
      state,
      COUNT(*) as count
    FROM pg_stat_activity
    WHERE datname = current_database()
    GROUP BY state
  metrics:
    - state:
        usage: "LABEL"
        description: "Connection state"
    - count:
        usage: "GAUGE"
        description: "Number of connections in this state"
```

Create `monitoring/prometheus.yml`:

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']
        labels:
          environment: 'development'
          database: 'ml_registry'
```

**Start monitoring stack:**

```bash
docker-compose -f docker-compose.monitoring.yml up -d

# Access Grafana
open http://localhost:3000  # admin/admin

# Access Prometheus
open http://localhost:9090
```

### Step 4.5: Create Grafana Dashboard

Create `monitoring/grafana-dashboards/postgres-performance.json`:

```json
{
  "dashboard": {
    "title": "ML Registry Database Performance",
    "panels": [
      {
        "title": "Query Latency (P50, P95, P99)",
        "targets": [
          {
            "expr": "histogram_quantile(0.50, rate(pg_stat_statements_exec_time_bucket[5m]))",
            "legendFormat": "P50"
          },
          {
            "expr": "histogram_quantile(0.95, rate(pg_stat_statements_exec_time_bucket[5m]))",
            "legendFormat": "P95"
          },
          {
            "expr": "histogram_quantile(0.99, rate(pg_stat_statements_exec_time_bucket[5m]))",
            "legendFormat": "P99"
          }
        ]
      },
      {
        "title": "Cache Hit Ratio",
        "targets": [
          {
            "expr": "pg_cache_hit_ratio",
            "legendFormat": "Cache Hit %"
          }
        ],
        "thresholds": [
          {"value": 90, "color": "green"},
          {"value": 80, "color": "yellow"},
          {"value": 0, "color": "red"}
        ]
      },
      {
        "title": "Slow Queries (>100ms)",
        "targets": [
          {
            "expr": "pg_slow_queries",
            "legendFormat": "Slow Queries"
          }
        ]
      },
      {
        "title": "Database Size",
        "targets": [
          {
            "expr": "pg_database_size_bytes",
            "legendFormat": "Database Size"
          }
        ]
      },
      {
        "title": "Active Connections",
        "targets": [
          {
            "expr": "sum(pg_connections{state='active'})",
            "legendFormat": "Active"
          },
          {
            "expr": "sum(pg_connections{state='idle'})",
            "legendFormat": "Idle"
          }
        ]
      },
      {
        "title": "Deadlocks",
        "targets": [
          {
            "expr": "rate(pg_deadlocks[5m])",
            "legendFormat": "Deadlocks/sec"
          }
        ]
      }
    ]
  }
}
```

### Step 4.6: Configure Alerting Rules

Create `monitoring/alert-rules.yml`:

```yaml
groups:
  - name: postgres_alerts
    interval: 30s
    rules:
      - alert: HighQueryLatency
        expr: histogram_quantile(0.99, rate(pg_stat_statements_exec_time_bucket[5m])) > 1000
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "P99 query latency above 1 second"
          description: "Database queries are slow (P99: {{ $value }}ms)"

      - alert: LowCacheHitRatio
        expr: pg_cache_hit_ratio < 85
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Cache hit ratio below 85%"
          description: "Too many disk reads (cache hit: {{ $value }}%)"

      - alert: HighConnectionCount
        expr: sum(pg_connections) > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High number of database connections"
          description: "Connection count: {{ $value }} (limit: 100)"

      - alert: DeadlocksDetected
        expr: rate(pg_deadlocks[5m]) > 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Database deadlocks detected"
          description: "Deadlock rate: {{ $value }}/sec"

      - alert: AutovacuumNotRunning
        expr: time() - pg_stat_user_tables_last_autovacuum > 86400
        for: 1h
        labels:
          severity: warning
        annotations:
          summary: "Autovacuum hasn't run in 24 hours"
          description: "Table {{ $labels.table }} needs vacuuming"
```

### Checkpoint 4

✅ Verify maintenance and monitoring:

```bash
# Check autovacuum is running
psql -h localhost -U ml_user -d ml_registry -c "
    SELECT COUNT(*) as autovacuum_workers
    FROM pg_stat_activity
    WHERE query LIKE '%autovacuum%';
"

# Verify Prometheus is scraping metrics
curl -s http://localhost:9090/api/v1/query?query=pg_cache_hit_ratio | jq '.data.result[0].value[1]'

# Check Grafana dashboard is accessible
curl -s http://localhost:3000/api/health | jq '.'
```

---

## Part 5: Advanced Optimization Techniques

### Step 5.1: Query Rewriting for Performance

**Common Performance Anti-Patterns:**

**❌ Bad: OR conditions with different columns**

```sql
-- Forces sequential scan
SELECT * FROM training_runs
WHERE model_name = 'fraud-detection' OR experiment_name = 'exp-001';
```

**✅ Good: Use UNION for OR conditions**

```sql
-- Can use indexes
SELECT * FROM training_runs WHERE model_name = 'fraud-detection'
UNION
SELECT * FROM training_runs WHERE experiment_name = 'exp-001';
```

---

**❌ Bad: NOT IN subquery**

```sql
-- Slow for large subqueries
SELECT * FROM models
WHERE model_id NOT IN (SELECT model_id FROM model_versions);
```

**✅ Good: Use LEFT JOIN with NULL check**

```sql
-- Much faster
SELECT m.*
FROM models m
LEFT JOIN model_versions mv ON m.model_id = mv.model_id
WHERE mv.model_id IS NULL;
```

---

**❌ Bad: SELECT * with OFFSET for pagination**

```sql
-- Scans all preceding rows
SELECT * FROM training_runs
ORDER BY created_at DESC
LIMIT 20 OFFSET 10000;  -- Slow for high offsets
```

**✅ Good: Keyset pagination**

```sql
-- Uses index, constant time
SELECT * FROM training_runs
WHERE created_at < '2024-01-15 10:00:00'
ORDER BY created_at DESC
LIMIT 20;
```

---

**❌ Bad: Function calls in WHERE clause**

```sql
-- Prevents index usage
SELECT * FROM training_runs
WHERE DATE(created_at) = '2024-01-15';
```

**✅ Good: Range query**

```sql
-- Uses index on created_at
SELECT * FROM training_runs
WHERE created_at >= '2024-01-15' AND created_at < '2024-01-16';
```

### Step 5.2: Partitioning for Large Tables

For tables > 10M rows or > 50GB, consider partitioning:

```sql
-- Create partitioned table for training_runs
CREATE TABLE training_runs_partitioned (
    run_id UUID PRIMARY KEY,
    model_name TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    -- ... other columns
) PARTITION BY RANGE (created_at);

-- Create monthly partitions
CREATE TABLE training_runs_2024_01 PARTITION OF training_runs_partitioned
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

CREATE TABLE training_runs_2024_02 PARTITION OF training_runs_partitioned
    FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');

-- Create index on each partition (automatically inherited)
CREATE INDEX ON training_runs_partitioned (created_at DESC);
CREATE INDEX ON training_runs_partitioned (experiment_name, created_at DESC);

-- Automatic partition management (PostgreSQL 13+)
CREATE OR REPLACE FUNCTION create_monthly_partitions()
RETURNS void AS $$
DECLARE
    start_date DATE;
    end_date DATE;
    partition_name TEXT;
BEGIN
    -- Create partitions for next 3 months
    FOR i IN 0..2 LOOP
        start_date := DATE_TRUNC('month', NOW() + (i || ' months')::INTERVAL);
        end_date := start_date + INTERVAL '1 month';
        partition_name := 'training_runs_' || TO_CHAR(start_date, 'YYYY_MM');

        IF NOT EXISTS (SELECT 1 FROM pg_tables WHERE tablename = partition_name) THEN
            EXECUTE format(
                'CREATE TABLE %I PARTITION OF training_runs_partitioned FOR VALUES FROM (%L) TO (%L)',
                partition_name, start_date, end_date
            );
            RAISE NOTICE 'Created partition: %', partition_name;
        END IF;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- Schedule with pg_cron or external scheduler
SELECT create_monthly_partitions();
```

**Benefits of Partitioning:**
- ✅ Queries with time filters only scan relevant partitions (partition pruning)
- ✅ Easier maintenance (drop old partitions instead of DELETE)
- ✅ Parallel query execution across partitions
- ✅ Smaller indexes per partition

### Step 5.3: Connection Pooling with PgBouncer

For applications with many short-lived connections, add connection pooling:

Create `docker-compose.pgbouncer.yml`:

```yaml
version: '3.8'

services:
  pgbouncer:
    image: edoburu/pgbouncer:latest
    container_name: pgbouncer
    environment:
      DATABASE_URL: "postgresql://ml_user:ml_password@ml-registry-postgres:5432/ml_registry"
      POOL_MODE: transaction  # or session, statement
      MAX_CLIENT_CONN: 1000
      DEFAULT_POOL_SIZE: 25
      RESERVE_POOL_SIZE: 5
      RESERVE_POOL_TIMEOUT: 3
      SERVER_IDLE_TIMEOUT: 600
      MAX_DB_CONNECTIONS: 100
    ports:
      - "6432:6432"
    networks:
      - ml-registry-network

networks:
  ml-registry-network:
    external: true
```

**Update application connection string:**

```python
# Before: Direct PostgreSQL connection
DATABASE_URL = "postgresql://ml_user:ml_password@localhost:5432/ml_registry"

# After: Through PgBouncer
DATABASE_URL = "postgresql://ml_user:ml_password@localhost:6432/ml_registry"
```

**Benefits:**
- ✅ Reduce connection overhead (connection creation is expensive)
- ✅ Handle connection spikes without exhausting database connections
- ✅ Support > 1000 application connections with only 100 database connections

### Step 5.4: Read Replicas for Scaling Reads

For read-heavy workloads, set up streaming replication:

```yaml
# docker-compose.replicas.yml
version: '3.8'

services:
  postgres-primary:
    image: postgres:14
    environment:
      POSTGRES_USER: ml_user
      POSTGRES_PASSWORD: ml_password
      POSTGRES_DB: ml_registry
      POSTGRES_INITDB_ARGS: "-c wal_level=replica -c max_wal_senders=3"
    volumes:
      - postgres-primary-data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  postgres-replica:
    image: postgres:14
    environment:
      PGUSER: replicator
      PGPASSWORD: replicator_password
    command: |
      bash -c "
      until pg_basebackup -h postgres-primary -D /var/lib/postgresql/data -U replicator -v -P --wal-method=stream; do
        echo 'Waiting for primary to be ready...'
        sleep 5
      done
      echo 'standby_mode = on' > /var/lib/postgresql/data/recovery.conf
      echo 'primary_conninfo = \"host=postgres-primary port=5432 user=replicator password=replicator_password\"' >> /var/lib/postgresql/data/recovery.conf
      postgres
      "
    volumes:
      - postgres-replica-data:/var/lib/postgresql/data
    ports:
      - "5433:5432"
    depends_on:
      - postgres-primary

volumes:
  postgres-primary-data:
  postgres-replica-data:
```

**Application Configuration:**

```python
# Write to primary
PRIMARY_DB_URL = "postgresql://ml_user:ml_password@localhost:5432/ml_registry"

# Read from replica
REPLICA_DB_URL = "postgresql://ml_user:ml_password@localhost:5433/ml_registry"

# SQLAlchemy configuration
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

primary_engine = create_engine(PRIMARY_DB_URL)
replica_engine = create_engine(REPLICA_DB_URL)

# Use replica for read-only queries
ReadSession = sessionmaker(bind=replica_engine)

def get_models_readonly():
    with ReadSession() as session:
        return session.query(Model).all()
```

### Checkpoint 5

✅ Verify advanced optimizations:

```bash
# Check if partitioning is enabled (if implemented)
psql -h localhost -U ml_user -d ml_registry -c "
    SELECT tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename))
    FROM pg_tables
    WHERE schemaname = 'public' AND tablename LIKE '%_partition_%'
    ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
"

# Test PgBouncer connection (if running)
psql -h localhost -p 6432 -U ml_user -d ml_registry -c "SELECT 1;"

# Check replication lag (if replicas configured)
psql -h localhost -U ml_user -d ml_registry -c "
    SELECT client_addr, state, sync_state,
           pg_wal_lsn_diff(pg_current_wal_lsn(), sent_lsn) AS lag_bytes
    FROM pg_stat_replication;
"
```

---

## Part 6: Production Runbook and Documentation

### Step 6.1: Create Performance Tuning Runbook

Create `docs/runbook-performance-tuning.md`:

```markdown
# Database Performance Tuning Runbook

## Quick Reference

| Issue | Symptom | Action | Priority |
|-------|---------|--------|----------|
| Slow queries | P99 > 500ms | Run EXPLAIN ANALYZE, check indexes | 🔴 HIGH |
| Low cache hit ratio | < 90% | Increase `shared_buffers`, check query patterns | 🟡 MEDIUM |
| High connections | > 80% of max | Add PgBouncer, check connection leaks | 🔴 HIGH |
| Table bloat | > 50% | Run VACUUM FULL during maintenance window | 🟡 MEDIUM |
| Index bloat | Leaf density < 70% | REINDEX CONCURRENTLY | 🟠 LOW |
| Deadlocks | > 0/hour | Review transaction logic, add retries | 🔴 HIGH |

---

## Procedure 1: Investigate Slow Query

**Trigger**: Alert fires for query latency > 500ms

**Steps**:

1. **Identify slow queries:**
   ```sql
   SELECT query, calls, mean_exec_time, max_exec_time
   FROM pg_stat_statements
   WHERE mean_exec_time > 100
   ORDER BY mean_exec_time DESC
   LIMIT 10;
   ```

2. **Capture execution plan:**
   ```sql
   EXPLAIN (ANALYZE, BUFFERS, VERBOSE) <slow_query>;
   ```

3. **Check for missing indexes:**
   - Look for "Seq Scan" on large tables
   - Check "rows" vs "actual rows" mismatch (stale statistics)
   - Verify indexes exist on WHERE/JOIN columns

4. **Apply fix:**
   - **If missing index**: `CREATE INDEX CONCURRENTLY ...`
   - **If stale stats**: `ANALYZE <table>;`
   - **If bad query**: Rewrite using techniques from Part 5

5. **Verify improvement:**
   - Re-run EXPLAIN ANALYZE
   - Monitor metrics for 24 hours
   - Document in `docs/performance-improvements.md`

**Rollback Plan**: `DROP INDEX CONCURRENTLY IF EXISTS <index_name>;`

---

## Procedure 2: Handle Table Bloat

**Trigger**: Table size increased by > 2x without corresponding data growth

**Steps**:

1. **Check bloat:**
   ```sql
   SELECT
       tablename,
       pg_size_pretty(pg_total_relation_size(tablename)) as size,
       n_dead_tup,
       ROUND(100 * n_dead_tup::numeric / NULLIF(n_live_tup + n_dead_tup, 0), 2) as dead_pct
   FROM pg_stat_user_tables
   WHERE schemaname = 'public'
   ORDER BY n_dead_tup DESC;
   ```

2. **If dead_pct > 20%**, run VACUUM:
   ```sql
   VACUUM (VERBOSE, ANALYZE) training_runs;
   ```

3. **If bloat persists**, schedule VACUUM FULL (requires maintenance window):
   ```sql
   -- ⚠️ Locks table for writes
   VACUUM FULL training_runs;
   ```

4. **Tune autovacuum** to prevent recurrence:
   ```sql
   ALTER TABLE training_runs SET (
       autovacuum_vacuum_scale_factor = 0.1,
       autovacuum_vacuum_threshold = 5000
   );
   ```

---

## Procedure 3: Emergency Performance Triage

**Trigger**: Database CPU > 90%, queries timing out

**Immediate Actions (within 5 minutes)**:

1. **Identify blocking queries:**
   ```sql
   SELECT pid, query, state, wait_event_type, wait_event
   FROM pg_stat_activity
   WHERE state != 'idle'
   ORDER BY query_start;
   ```

2. **Kill long-running queries** (if safe):
   ```sql
   SELECT pg_terminate_backend(pid)
   FROM pg_stat_activity
   WHERE state = 'active'
     AND query_start < NOW() - INTERVAL '5 minutes'
     AND query NOT LIKE '%pg_stat_activity%';
   ```

3. **Check for lock contention:**
   ```sql
   SELECT
       blocked_locks.pid AS blocked_pid,
       blocked_activity.query AS blocked_query,
       blocking_locks.pid AS blocking_pid,
       blocking_activity.query AS blocking_query
   FROM pg_catalog.pg_locks blocked_locks
   JOIN pg_catalog.pg_stat_activity blocked_activity ON blocked_activity.pid = blocked_locks.pid
   JOIN pg_catalog.pg_locks blocking_locks ON blocking_locks.locktype = blocked_locks.locktype
   JOIN pg_catalog.pg_stat_activity blocking_activity ON blocking_activity.pid = blocking_locks.pid
   WHERE NOT blocked_locks.granted;
   ```

4. **Enable query logging** temporarily:
   ```sql
   ALTER SYSTEM SET log_min_duration_statement = 0;  -- Log all queries
   SELECT pg_reload_conf();
   ```

5. **Escalate** to DBA if issue persists after 15 minutes

**Follow-up Actions (within 24 hours)**:

- Review slow query log
- Update indexes based on patterns
- Consider adding read replicas
- Document incident in postmortem

---

## Procedure 4: Monthly Maintenance

**Schedule**: First Sunday of each month, 2 AM UTC

**Checklist**:

- [ ] Run `scripts/maintenance.sql`
- [ ] Check for unused indexes (`idx_scan = 0`)
- [ ] REINDEX bloated indexes (leaf_density < 70%)
- [ ] Review pg_stat_statements for new slow queries
- [ ] Update `docs/performance-baseline.md` with current metrics
- [ ] Verify backup restoration (restore to test database)
- [ ] Review alert threshold (adjust based on traffic changes)

**Estimated Duration**: 30-60 minutes

---

## Emergency Contacts

- **Primary DBA**: dba@company.com (Pager: +1-XXX-XXX-XXXX)
- **Backup DBA**: backup-dba@company.com
- **Escalation**: #database-oncall Slack channel

---

## References

- [PostgreSQL Documentation: Performance Tips](https://www.postgresql.org/docs/current/performance-tips.html)
- [pgAnalyze: Index Advisor](https://pganalyze.com/)
- [Postgres EXPLAIN Visualizer](https://explain.depesz.com/)
```

### Step 6.2: Document Optimization History

Create `docs/performance-improvements.md`:

```markdown
# Performance Optimization History

## 2025-10-23: Initial Index Creation

**Problem**: Dashboard queries timing out (P99 > 1,000ms)

**Root Cause**: Missing indexes on foreign keys and time-range filters

**Solution**: Created 18 indexes covering:
- Foreign key columns (5 indexes)
- Time-range queries (4 indexes)
- Composite indexes (3 indexes)
- Partial indexes (3 indexes)
- JSONB indexes (3 indexes)

**Results**:
- 92% reduction in average query latency
- 96% reduction in P99 latency
- Cache hit ratio improved from 45% to 94%
- Zero query timeouts

**Metrics**: See `docs/performance-results.md`

**Indexes Created**: See `sql/50_indexes.sql`

---

## Future Optimization Candidates

1. **Partition training_runs table** (Priority: MEDIUM)
   - Rationale: Table approaching 10M rows
   - Expected benefit: 50% faster time-range queries
   - Estimated effort: 4 hours (migration script + testing)

2. **Add read replica** (Priority: HIGH if traffic > 100 QPS)
   - Rationale: Read-heavy workload (95% reads)
   - Expected benefit: 2x read capacity
   - Estimated effort: 8 hours (setup + application changes)

3. **Implement PgBouncer** (Priority: LOW currently)
   - Rationale: Connection count stable (< 50)
   - Revisit when: Connections > 80

4. **JSONB index optimization** (Priority: LOW)
   - Current status: JSONB indexes unused
   - Action: Monitor for 30 days, drop if still unused
```

### Checkpoint 6

✅ Verify runbook completeness:

```bash
# Check all documentation exists
ls -la docs/runbook-performance-tuning.md
ls -la docs/performance-improvements.md
ls -la docs/index-strategy.md

# Verify maintenance script exists
ls -la scripts/maintenance.sql

# Test maintenance script (dry run)
psql -h localhost -U ml_user -d ml_registry -f scripts/maintenance.sql --dry-run
```

---

## Part 7: Hands-on Challenges

### Challenge 1: Optimize a Complex Analytical Query

**Problem**: The following query is slow (avg 850ms):

```sql
SELECT
    m.model_name,
    COUNT(DISTINCT d.deployment_id) as total_deployments,
    COUNT(DISTINCT d.deployment_id) FILTER (WHERE d.status = 'active') as active_deployments,
    MAX(d.deployed_at) as last_deployment,
    AVG(tr.accuracy) FILTER (WHERE tr.status = 'succeeded') as avg_accuracy,
    COUNT(DISTINCT tr.run_id) as total_runs
FROM models m
LEFT JOIN model_versions mv ON m.model_id = mv.model_id
LEFT JOIN deployments d ON mv.version_id = d.version_id
LEFT JOIN training_runs tr ON mv.version_id = tr.version_id
WHERE m.created_at > NOW() - INTERVAL '90 days'
GROUP BY m.model_id, m.model_name
HAVING COUNT(DISTINCT d.deployment_id) > 0
ORDER BY total_deployments DESC;
```

**Tasks**:
1. Run EXPLAIN ANALYZE and identify bottlenecks
2. Create necessary indexes
3. Consider query rewrite (CTEs, subqueries, materialized view)
4. Measure before/after improvement
5. Document your solution

**Target**: < 100ms execution time

<details>
<summary>Click for Solution Hints</summary>

**Hints**:
- Consider filtering early (WHERE before JOIN)
- Use window functions instead of multiple aggregations
- Create covering index on (created_at, model_id) for models table
- Consider materialized view refreshed hourly

</details>

---

### Challenge 2: Design Partitioning Strategy

**Problem**: `training_runs` table has 50M rows and growing by 100K/day

**Tasks**:
1. Design monthly partitioning strategy
2. Write migration script to convert existing table to partitioned table
3. Create function to auto-create future partitions
4. Test partition pruning with EXPLAIN
5. Document retention policy (keep 12 months, archive older)

**Deliverable**: `sql/60_partition_training_runs.sql`

---

### Challenge 3: Implement Query Result Caching

**Problem**: Dashboard stats query runs 1000x/hour but data changes only every 5 minutes

**Tasks**:
1. Create materialized view for dashboard stats
2. Set up refresh job (pg_cron or application-level)
3. Modify application to query materialized view
4. Measure cache hit rate
5. Compare performance vs direct query

**Target**: 99% cache hit rate, <5ms query time

---

## Part 8: Summary and Next Steps

### What You've Learned

✅ **Database profiling** with pg_stat_statements and EXPLAIN ANALYZE
✅ **Index strategy design** for different query patterns
✅ **Performance measurement** with before/after metrics
✅ **Maintenance procedures** (VACUUM, ANALYZE, REINDEX)
✅ **Monitoring setup** with Prometheus and Grafana
✅ **Production runbooks** for performance issues
✅ **Advanced techniques** (partitioning, connection pooling, replication)

### Key Takeaways

1. **Measure before optimizing**: Use EXPLAIN ANALYZE to find actual bottlenecks
2. **Indexes are powerful but not free**: 50% write overhead for 10-100x read speedup
3. **Foreign key indexes are critical**: Always index FK columns
4. **Composite indexes beat multiple single-column indexes**: Column order matters
5. **Partial indexes are underused**: Target hot queries with filtered indexes
6. **Monitoring prevents regressions**: Set up alerts before performance degrades
7. **Maintenance is essential**: VACUUM, ANALYZE, and REINDEX keep database healthy

### Performance Achievements

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Avg Query Latency | 145ms | 12ms | **92% faster** |
| P99 Latency | 1,250ms | 45ms | **96% faster** |
| Cache Hit Ratio | 45% | 94% | **+49pp** |
| Slow Queries (>1s) | 7.3% | 0% | **100% eliminated** |
| Database CPU | 78% | 23% | **-55pp** |

### Production Readiness Checklist

Before deploying to production:

- [ ] All indexes created with `CONCURRENTLY`
- [ ] EXPLAIN ANALYZE confirms index usage
- [ ] Before/after metrics documented
- [ ] Monitoring dashboard configured
- [ ] Alert rules configured and tested
- [ ] Runbook documented and reviewed
- [ ] Maintenance schedule established
- [ ] Backup/restore tested
- [ ] Performance regression tests added to CI/CD
- [ ] Team trained on troubleshooting procedures

### Next Steps

**Module 009: Monitoring & Logging Basics**
- Instrument database queries in application code
- Set up distributed tracing (OpenTelemetry)
- Create custom metrics for business KPIs
- Implement log aggregation (ELK, Loki)

**Module 010: Cloud Platforms**
- Deploy to managed PostgreSQL (AWS RDS, GCP Cloud SQL)
- Configure automated backups and point-in-time recovery
- Set up cross-region replication
- Optimize costs (reserved instances, storage tiers)

**Real-World Projects**:
- Build complete ML platform with optimized database backend
- Implement auto-scaling based on query load
- Create multi-tenant database architecture

### Resources

**Books**:
- "PostgreSQL 14 Internals" by Egor Rogov
- "The Art of PostgreSQL" by Dimitri Fontaine

**Tools**:
- [pgAnalyze](https://pganalyze.com/) - Query performance monitoring
- [pghero](https://github.com/ankane/pghero) - Database health dashboard
- [pgBadger](https://github.com/darold/pgbadger) - Log analyzer
- [EXPLAIN Visualizer](https://explain.depesz.com/) - Visual query plans

**Documentation**:
- [PostgreSQL Performance Tips](https://www.postgresql.org/docs/current/performance-tips.html)
- [Index Types](https://www.postgresql.org/docs/current/indexes-types.html)
- [EXPLAIN Documentation](https://www.postgresql.org/docs/current/sql-explain.html)

---

## Congratulations!

You've completed Exercise 05 and mastered database performance optimization! You now have:

- Production-ready indexing strategy
- Comprehensive monitoring setup
- Performance runbook for operations
- Before/after metrics proving 92% improvement
- Advanced techniques for scaling beyond current workload

**You're ready to manage production ML infrastructure databases!**

---

**Exercise 05 Complete** | [Return to Module 008 Overview](../README.md) | Next: [Module 009: Monitoring & Logging](../../mod-009-monitoring-logging/README.md)
