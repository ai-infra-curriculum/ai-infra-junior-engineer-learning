# Lecture 03: Advanced SQL & Query Optimization

## Table of Contents
1. [Introduction](#introduction)
2. [JOINs in Depth](#joins-in-depth)
3. [Subqueries](#subqueries)
4. [Common Table Expressions (CTEs)](#common-table-expressions-ctes)
5. [Aggregations and GROUP BY](#aggregations-and-group-by)
6. [Window Functions](#window-functions)
7. [Query Optimization Fundamentals](#query-optimization-fundamentals)
8. [Indexes and Performance](#indexes-and-performance)
9. [EXPLAIN and Query Plans](#explain-and-query-plans)
10. [Advanced SQL Patterns for ML](#advanced-sql-patterns-for-ml)
11. [Best Practices](#best-practices)
12. [Summary and Key Takeaways](#summary-and-key-takeaways)

## Introduction

Advanced SQL enables you to perform complex data analysis, combine data from multiple sources, and optimize query performance. For ML infrastructure, these skills are essential for analyzing experiment results, computing metrics, and managing large-scale data pipelines efficiently.

### Learning Objectives

By the end of this lecture, you will:
- Master different types of JOINs and when to use each
- Write subqueries and Common Table Expressions (CTEs)
- Use aggregate functions and GROUP BY effectively
- Apply window functions for advanced analytics
- Understand query optimization principles
- Create and use indexes strategically
- Read and interpret query execution plans
- Optimize SQL queries for ML workloads

### Prerequisites
- Lecture 01: Database Fundamentals & SQL Basics
- Lecture 02: Database Design & Normalization
- Proficiency with basic SQL (SELECT, WHERE, INSERT, UPDATE, DELETE)

### Estimated Time
5-6 hours (including hands-on optimization exercises)

## JOINs in Depth

###Schema for Examples

```sql
-- Models table
models:
model_id | name      | framework
---------|-----------|----------
1        | BERT      | PyTorch
2        | ResNet    | TensorFlow
3        | GPT-2     | PyTorch

-- Experiments table
experiments:
exp_id | model_id | accuracy | dataset
-------|----------|----------|--------
101    | 1        | 0.92     | IMDB
102    | 1        | 0.88     | SST-2
103    | 2        | 0.76     | ImageNet
104    | NULL     | 0.85     | CIFAR-10
```

### INNER JOIN

Returns only rows that have matching values in both tables.

```sql
SELECT
    m.name,
    e.accuracy,
    e.dataset
FROM models m
INNER JOIN experiments e ON m.model_id = e.model_id;
```

**Result:**
```
name   | accuracy | dataset
-------|----------|----------
BERT   | 0.92     | IMDB
BERT   | 0.88     | SST-2
ResNet | 0.76     | ImageNet
```

**Note:** GPT-2 (no experiments) and experiment 104 (no model) are excluded.

**When to use:** Most common JOIN type; use when you only want matching records.

### LEFT (OUTER) JOIN

Returns all rows from the left table, with matching rows from the right table (or NULL if no match).

```sql
SELECT
    m.name,
    e.accuracy,
    e.dataset
FROM models m
LEFT JOIN experiments e ON m.model_id = e.model_id;
```

**Result:**
```
name   | accuracy | dataset
-------|----------|----------
BERT   | 0.92     | IMDB
BERT   | 0.88     | SST-2
ResNet | 0.76     | ImageNet
GPT-2  | NULL     | NULL      ← No experiments, but still included
```

**When to use:** Find models without experiments, users without orders, etc.

**Find models with NO experiments:**
```sql
SELECT m.name
FROM models m
LEFT JOIN experiments e ON m.model_id = e.model_id
WHERE e.exp_id IS NULL;

-- Result: GPT-2
```

### RIGHT (OUTER) JOIN

Returns all rows from the right table, with matching rows from the left table (or NULL if no match).

```sql
SELECT
    m.name,
    e.accuracy,
    e.dataset
FROM models m
RIGHT JOIN experiments e ON m.model_id = e.model_id;
```

**Result:**
```
name   | accuracy | dataset
-------|----------|----------
BERT   | 0.92     | IMDB
BERT   | 0.88     | SST-2
ResNet | 0.76     | ImageNet
NULL   | 0.85     | CIFAR-10  ← Experiment without model
```

**Note:** RIGHT JOIN is less common; you can usually rewrite as LEFT JOIN.

### FULL OUTER JOIN

Returns all rows from both tables, with NULLs where there's no match.

```sql
SELECT
    m.name,
    e.accuracy,
    e.dataset
FROM models m
FULL OUTER JOIN experiments e ON m.model_id = e.model_id;
```

**Result:**
```
name   | accuracy | dataset
-------|----------|----------
BERT   | 0.92     | IMDB
BERT   | 0.88     | SST-2
ResNet | 0.76     | ImageNet
GPT-2  | NULL     | NULL      ← Model without experiments
NULL   | 0.85     | CIFAR-10  ← Experiment without model
```

**When to use:** Find orphaned records on both sides.

### CROSS JOIN

Cartesian product: every row from first table paired with every row from second table.

```sql
SELECT m.name, f.framework_name
FROM models m
CROSS JOIN (VALUES ('PyTorch'), ('TensorFlow'), ('JAX')) AS f(framework_name);
```

**Result:** 3 models × 3 frameworks = 9 rows

**When to use:** Generate combinations, create test data.

### SELF JOIN

Join a table to itself.

```sql
-- Find experiments with similar accuracy
SELECT
    e1.exp_id AS exp1,
    e2.exp_id AS exp2,
    e1.accuracy
FROM experiments e1
JOIN experiments e2 ON ABS(e1.accuracy - e2.accuracy) < 0.01
WHERE e1.exp_id < e2.exp_id;  -- Avoid duplicates
```

### Multiple JOINs

```sql
-- Get experiment results with model and user info
SELECT
    u.username,
    m.name AS model_name,
    e.accuracy,
    e.dataset
FROM experiments e
INNER JOIN models m ON e.model_id = m.model_id
INNER JOIN users u ON m.created_by = u.user_id
WHERE e.accuracy > 0.85
ORDER BY e.accuracy DESC;
```

## Subqueries

A query nested inside another query.

### Subquery in WHERE

```sql
-- Find models more accurate than average
SELECT name, accuracy
FROM models
WHERE accuracy > (
    SELECT AVG(accuracy)
    FROM models
    WHERE accuracy IS NOT NULL
);
```

### Subquery with IN

```sql
-- Find models used in experiments
SELECT name
FROM models
WHERE model_id IN (
    SELECT DISTINCT model_id
    FROM experiments
    WHERE model_id IS NOT NULL
);

-- Alternative using JOIN (often faster):
SELECT DISTINCT m.name
FROM models m
INNER JOIN experiments e ON m.model_id = e.model_id;
```

### Subquery in SELECT

```sql
-- Count experiments per model
SELECT
    name,
    (SELECT COUNT(*)
     FROM experiments e
     WHERE e.model_id = m.model_id) AS experiment_count
FROM models m;
```

### Correlated Subquery

Subquery references the outer query.

```sql
-- Find each model's best accuracy
SELECT
    m.name,
    (SELECT MAX(e.accuracy)
     FROM experiments e
     WHERE e.model_id = m.model_id) AS best_accuracy
FROM models m;
```

**Note:** Correlated subqueries can be slow; consider JOINs or window functions instead.

### EXISTS

Check if subquery returns any rows.

```sql
-- Models that have experiments
SELECT name
FROM models m
WHERE EXISTS (
    SELECT 1
    FROM experiments e
    WHERE e.model_id = m.model_id
);

-- Models that have NO experiments
SELECT name
FROM models m
WHERE NOT EXISTS (
    SELECT 1
    FROM experiments e
    WHERE e.model_id = m.model_id
);
```

## Common Table Expressions (CTEs)

CTEs make complex queries more readable by breaking them into named steps.

### Basic CTE

```sql
WITH high_accuracy_experiments AS (
    SELECT model_id, accuracy, dataset
    FROM experiments
    WHERE accuracy > 0.90
)
SELECT
    m.name,
    h.accuracy,
    h.dataset
FROM models m
INNER JOIN high_accuracy_experiments h ON m.model_id = h.model_id;
```

### Multiple CTEs

```sql
WITH
pytorch_models AS (
    SELECT model_id, name
    FROM models
    WHERE framework = 'PyTorch'
),
recent_experiments AS (
    SELECT model_id, accuracy
    FROM experiments
    WHERE created_at > '2024-01-01'
)
SELECT
    p.name,
    AVG(r.accuracy) AS avg_accuracy
FROM pytorch_models p
INNER JOIN recent_experiments r ON p.model_id = r.model_id
GROUP BY p.name;
```

### Recursive CTE

Useful for hierarchical or graph data.

```sql
-- Example: Model lineage (models derived from other models)
WITH RECURSIVE model_lineage AS (
    -- Base case: root models
    SELECT model_id, name, parent_model_id, 1 AS level
    FROM models
    WHERE parent_model_id IS NULL

    UNION ALL

    -- Recursive case: child models
    SELECT m.model_id, m.name, m.parent_model_id, ml.level + 1
    FROM models m
    INNER JOIN model_lineage ml ON m.parent_model_id = ml.model_id
)
SELECT * FROM model_lineage
ORDER BY level, name;
```

## Aggregations and GROUP BY

### Aggregate Functions

```sql
-- Count all experiments
SELECT COUNT(*) FROM experiments;

-- Count non-NULL accuracies
SELECT COUNT(accuracy) FROM experiments;

-- Count distinct models
SELECT COUNT(DISTINCT model_id) FROM experiments;

-- Average accuracy
SELECT AVG(accuracy) FROM experiments;

-- Min and Max accuracy
SELECT MIN(accuracy), MAX(accuracy) FROM experiments;

-- Sum of all accuracies
SELECT SUM(accuracy) FROM experiments;
```

### GROUP BY

```sql
-- Average accuracy per model
SELECT
    model_id,
    AVG(accuracy) AS avg_accuracy,
    COUNT(*) AS experiment_count
FROM experiments
GROUP BY model_id;
```

**Result:**
```
model_id | avg_accuracy | experiment_count
---------|--------------|------------------
1        | 0.90         | 2
2        | 0.76         | 1
NULL     | 0.85         | 1
```

### GROUP BY with JOIN

```sql
-- Average accuracy per model (with model name)
SELECT
    m.name,
    m.framework,
    AVG(e.accuracy) AS avg_accuracy,
    COUNT(e.exp_id) AS experiment_count
FROM models m
LEFT JOIN experiments e ON m.model_id = e.model_id
GROUP BY m.model_id, m.name, m.framework
ORDER BY avg_accuracy DESC NULLS LAST;
```

### HAVING

Filter groups (like WHERE but for aggregated data).

```sql
-- Models with average accuracy > 0.85
SELECT
    model_id,
    AVG(accuracy) AS avg_accuracy
FROM experiments
GROUP BY model_id
HAVING AVG(accuracy) > 0.85;
```

**Note:** WHERE filters rows BEFORE grouping; HAVING filters groups AFTER aggregation.

```sql
-- Find frameworks with more than 1 model and avg accuracy > 0.88
SELECT
    framework,
    COUNT(*) AS model_count,
    AVG(accuracy) AS avg_accuracy
FROM models m
LEFT JOIN experiments e ON m.model_id = e.model_id
WHERE m.created_at > '2024-01-01'  -- Filter rows first
GROUP BY framework
HAVING COUNT(*) > 1                -- Then filter groups
   AND AVG(accuracy) > 0.88;
```

### GROUP BY Multiple Columns

```sql
-- Experiments per model per dataset
SELECT
    model_id,
    dataset,
    COUNT(*) AS experiment_count,
    AVG(accuracy) AS avg_accuracy
FROM experiments
GROUP BY model_id, dataset;
```

## Window Functions

Window functions perform calculations across related rows without collapsing them.

### ROW_NUMBER()

Assign a unique number to each row within a partition.

```sql
-- Number experiments per model
SELECT
    model_id,
    exp_id,
    accuracy,
    ROW_NUMBER() OVER (PARTITION BY model_id ORDER BY accuracy DESC) AS rank_in_model
FROM experiments;
```

**Result:**
```
model_id | exp_id | accuracy | rank_in_model
---------|--------|----------|---------------
1        | 101    | 0.92     | 1
1        | 102    | 0.88     | 2
2        | 103    | 0.76     | 1
```

### RANK() and DENSE_RANK()

```sql
-- RANK: Gaps in ranking for ties
-- DENSE_RANK: No gaps
SELECT
    exp_id,
    accuracy,
    RANK() OVER (ORDER BY accuracy DESC) AS rank,
    DENSE_RANK() OVER (ORDER BY accuracy DESC) AS dense_rank
FROM experiments;
```

**Result:**
```
exp_id | accuracy | rank | dense_rank
-------|----------|------|------------
101    | 0.92     | 1    | 1
102    | 0.88     | 2    | 2
104    | 0.85     | 3    | 3
103    | 0.76     | 4    | 4
```

### NTILE()

Divide rows into N equal buckets.

```sql
-- Divide experiments into quartiles by accuracy
SELECT
    exp_id,
    accuracy,
    NTILE(4) OVER (ORDER BY accuracy) AS quartile
FROM experiments;
```

### LAG() and LEAD()

Access previous/next row values.

```sql
-- Compare each experiment with previous
SELECT
    exp_id,
    accuracy,
    LAG(accuracy) OVER (ORDER BY exp_id) AS prev_accuracy,
    accuracy - LAG(accuracy) OVER (ORDER BY exp_id) AS improvement
FROM experiments;
```

### Aggregate Window Functions

```sql
-- Running average of accuracy
SELECT
    exp_id,
    accuracy,
    AVG(accuracy) OVER (
        ORDER BY exp_id
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS running_avg
FROM experiments;

-- Moving average (last 3 experiments)
SELECT
    exp_id,
    accuracy,
    AVG(accuracy) OVER (
        ORDER BY exp_id
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ) AS moving_avg_3
FROM experiments;
```

### Practical ML Example

```sql
-- Find best experiment per model, with improvement over previous
WITH ranked_experiments AS (
    SELECT
        model_id,
        exp_id,
        accuracy,
        created_at,
        ROW_NUMBER() OVER (PARTITION BY model_id ORDER BY accuracy DESC) AS rank,
        LAG(accuracy) OVER (PARTITION BY model_id ORDER BY created_at) AS prev_accuracy
    FROM experiments
)
SELECT
    model_id,
    exp_id AS best_experiment,
    accuracy AS best_accuracy,
    accuracy - prev_accuracy AS improvement
FROM ranked_experiments
WHERE rank = 1;
```

## Query Optimization Fundamentals

### Understanding Query Execution

SQL queries are executed in this order:

```sql
SELECT column_list          -- 5. Select columns
FROM table                  -- 1. Get data
JOIN other_table ON ...     -- 2. Join tables
WHERE conditions            -- 3. Filter rows
GROUP BY columns            -- 4. Group rows
HAVING group_conditions     -- 4a. Filter groups
ORDER BY columns            -- 6. Sort results
LIMIT n;                    -- 7. Limit results
```

### Optimization Principles

#### 1. Select Only Needed Columns

```sql
-- BAD: Fetches all columns (wasteful)
SELECT * FROM experiments WHERE accuracy > 0.90;

-- GOOD: Only fetch what you need
SELECT exp_id, model_id, accuracy FROM experiments WHERE accuracy > 0.90;
```

#### 2. Filter Early with WHERE

```sql
-- BAD: Joins all data then filters
SELECT m.name, e.accuracy
FROM models m
JOIN experiments e ON m.model_id = e.model_id
WHERE e.accuracy > 0.90;

-- BETTER: Filter before joining (if possible)
SELECT m.name, e.accuracy
FROM models m
JOIN (SELECT * FROM experiments WHERE accuracy > 0.90) e
  ON m.model_id = e.model_id;

-- BEST: Database optimizer usually handles this, but explicit helps
```

#### 3. Use EXISTS Instead of IN for Large Subqueries

```sql
-- CAN BE SLOW: IN with large subquery
SELECT name FROM models
WHERE model_id IN (SELECT model_id FROM experiments);

-- FASTER: EXISTS (stops at first match)
SELECT name FROM models m
WHERE EXISTS (SELECT 1 FROM experiments e WHERE e.model_id = m.model_id);
```

#### 4. Avoid SELECT DISTINCT When Possible

```sql
-- SLOW: DISTINCT requires sorting/deduplication
SELECT DISTINCT model_id FROM experiments;

-- FASTER: Use GROUP BY if aggregating anyway
SELECT model_id, COUNT(*) FROM experiments GROUP BY model_id;
```

#### 5. Limit Results Early

```sql
-- Get top 10 models by accuracy
SELECT name, accuracy
FROM models
WHERE accuracy IS NOT NULL
ORDER BY accuracy DESC
LIMIT 10;  -- Stops after finding 10 results
```

## Indexes and Performance

### What is an Index?

An index is a data structure that speeds up data retrieval at the cost of slower writes and more storage.

**Analogy:** Book index lets you find topics quickly without reading every page.

### Types of Indexes

#### B-Tree Index (Default)

Best for equality and range queries.

```sql
CREATE INDEX idx_experiments_accuracy ON experiments(accuracy);

-- Now this is fast:
SELECT * FROM experiments WHERE accuracy > 0.90;
SELECT * FROM experiments WHERE accuracy BETWEEN 0.85 AND 0.95;
```

#### Hash Index

Best for equality queries only.

```sql
CREATE INDEX idx_models_name_hash ON models USING HASH (name);

-- Fast:
SELECT * FROM models WHERE name = 'BERT';

-- Won't use index (hash doesn't support ranges):
SELECT * FROM models WHERE name LIKE 'BERT%';
```

#### Composite Index

Index on multiple columns.

```sql
CREATE INDEX idx_exp_model_accuracy ON experiments(model_id, accuracy);

-- Uses index:
SELECT * FROM experiments WHERE model_id = 1 AND accuracy > 0.90;
SELECT * FROM experiments WHERE model_id = 1;  -- Uses first column

-- Won't use index efficiently:
SELECT * FROM experiments WHERE accuracy > 0.90;  -- Skips first column
```

**Order matters:** Put most selective column first.

#### Unique Index

Enforces uniqueness and speeds up lookups.

```sql
CREATE UNIQUE INDEX idx_models_name_unique ON models(name);

-- Prevents duplicates AND makes lookups fast
```

### When to Index

**Index these:**
- Primary keys (automatically indexed)
- Foreign keys
- Columns in WHERE clauses
- Columns in JOIN conditions
- Columns in ORDER BY
- Columns in GROUP BY

**Don't over-index:**
```sql
-- BAD: Index every column
CREATE INDEX idx1 ON experiments(exp_id);        -- Already primary key
CREATE INDEX idx2 ON experiments(model_id);      -- Maybe useful
CREATE INDEX idx3 ON experiments(accuracy);      -- Maybe useful
CREATE INDEX idx4 ON experiments(loss);          -- Probably not needed
CREATE INDEX idx5 ON experiments(created_at);    -- Depends on queries
CREATE INDEX idx6 ON experiments(batch_size);    -- Probably not needed
```

**Each index:**
- ✅ Speeds up reads
- ❌ Slows down writes (INSERT, UPDATE, DELETE)
- ❌ Takes up storage

### Monitoring Index Usage

```sql
-- PostgreSQL: Check unused indexes
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan AS index_scans,
    idx_tup_read AS tuples_read,
    idx_tup_fetch AS tuples_fetched
FROM pg_stat_user_indexes
WHERE idx_scan = 0
  AND indexname NOT LIKE '%_pkey';  -- Exclude primary keys

-- Drop unused indexes
DROP INDEX idx_rarely_used;
```

## EXPLAIN and Query Plans

### Using EXPLAIN

```sql
-- See query execution plan
EXPLAIN SELECT * FROM experiments WHERE accuracy > 0.90;

-- Include actual execution statistics
EXPLAIN ANALYZE SELECT * FROM experiments WHERE accuracy > 0.90;
```

### Reading EXPLAIN Output

**Example:**
```
QUERY PLAN
--------------------------------------------------------------
Seq Scan on experiments  (cost=0.00..35.50 rows=5 width=40)
  Filter: (accuracy > 0.90)
```

**Components:**
- **Seq Scan**: Sequential scan (reads whole table)
- **cost=0.00..35.50**: Estimated cost (startup..total)
- **rows=5**: Estimated rows returned
- **width=40**: Estimated bytes per row

### With Index

```sql
CREATE INDEX idx_experiments_accuracy ON experiments(accuracy);

EXPLAIN SELECT * FROM experiments WHERE accuracy > 0.90;
```

**Output:**
```
Index Scan using idx_experiments_accuracy on experiments
  (cost=0.15..8.17 rows=5 width=40)
  Index Cond: (accuracy > 0.90)
```

**Index Scan** instead of **Seq Scan** = faster!

### Common Plan Nodes

- **Seq Scan**: Full table scan (slow for large tables)
- **Index Scan**: Uses index (fast)
- **Index Only Scan**: Gets data from index without accessing table (fastest)
- **Bitmap Index Scan**: Scans index, then fetches rows (medium)
- **Hash Join**: Joins using hash table
- **Merge Join**: Joins sorted data
- **Nested Loop**: For each row in first table, scan second table

### Optimization Based on EXPLAIN

```sql
-- Slow query
EXPLAIN ANALYZE
SELECT m.name, AVG(e.accuracy)
FROM models m
JOIN experiments e ON m.model_id = e.model_id
WHERE e.created_at > '2024-01-01'
GROUP BY m.name;

-- If you see Seq Scan on experiments, add index:
CREATE INDEX idx_experiments_created_at ON experiments(created_at);

-- If you see slow join, ensure foreign key is indexed:
CREATE INDEX idx_experiments_model_id ON experiments(model_id);
```

## Advanced SQL Patterns for ML

### Pattern 1: Pivot Table (Metrics by Model)

```sql
-- Pivot metrics from rows to columns
SELECT
    model_id,
    MAX(CASE WHEN metric_name = 'accuracy' THEN metric_value END) AS accuracy,
    MAX(CASE WHEN metric_name = 'precision' THEN metric_value END) AS precision,
    MAX(CASE WHEN metric_name = 'recall' THEN metric_value END) AS recall,
    MAX(CASE WHEN metric_name = 'f1_score' THEN metric_value END) AS f1_score
FROM experiment_metrics
GROUP BY model_id;
```

### Pattern 2: Cohort Analysis

```sql
-- Analyze model performance by training month
SELECT
    DATE_TRUNC('month', created_at) AS training_month,
    framework,
    COUNT(*) AS models_trained,
    AVG(accuracy) AS avg_accuracy,
    MAX(accuracy) AS best_accuracy
FROM models
WHERE created_at >= '2024-01-01'
GROUP BY training_month, framework
ORDER BY training_month, framework;
```

### Pattern 3: Percentile Analysis

```sql
-- Find 95th percentile inference latency
SELECT
    model_id,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY latency_ms) AS p95_latency
FROM predictions
GROUP BY model_id;
```

### Pattern 4: Time Series Aggregation

```sql
-- Daily prediction counts with 7-day moving average
SELECT
    DATE(created_at) AS date,
    COUNT(*) AS predictions_count,
    AVG(COUNT(*)) OVER (
        ORDER BY DATE(created_at)
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) AS moving_avg_7d
FROM predictions
GROUP BY DATE(created_at)
ORDER BY date;
```

### Pattern 5: Finding Outliers

```sql
-- Find experiments with anomalous results (> 2 std devs from mean)
WITH stats AS (
    SELECT
        AVG(accuracy) AS mean_accuracy,
        STDDEV(accuracy) AS stddev_accuracy
    FROM experiments
)
SELECT e.exp_id, e.accuracy, e.model_id
FROM experiments e, stats s
WHERE ABS(e.accuracy - s.mean_accuracy) > 2 * s.stddev_accuracy;
```

## Best Practices

### 1. Write Readable Queries

```sql
-- GOOD: Clear, formatted
SELECT
    m.name,
    m.framework,
    COUNT(e.exp_id) AS experiment_count,
    AVG(e.accuracy) AS avg_accuracy
FROM models m
LEFT JOIN experiments e ON m.model_id = e.model_id
WHERE m.created_at > '2024-01-01'
GROUP BY m.model_id, m.name, m.framework
HAVING COUNT(e.exp_id) > 0
ORDER BY avg_accuracy DESC
LIMIT 10;

-- BAD: Unreadable
select m.name,m.framework,count(e.exp_id),avg(e.accuracy) from models m left join experiments e on m.model_id=e.model_id where m.created_at>'2024-01-01' group by m.model_id,m.name,m.framework having count(e.exp_id)>0 order by avg_accuracy desc limit 10;
```

### 2. Use CTEs for Complex Queries

```sql
-- Instead of nested subqueries, use CTEs
WITH recent_models AS (
    SELECT * FROM models WHERE created_at > '2024-01-01'
),
high_accuracy_experiments AS (
    SELECT * FROM experiments WHERE accuracy > 0.90
)
SELECT
    m.name,
    COUNT(e.exp_id) AS successful_experiments
FROM recent_models m
JOIN high_accuracy_experiments e ON m.model_id = e.model_id
GROUP BY m.name;
```

### 3. Test Queries on Sample Data

```sql
-- Test on small subset first
SELECT * FROM large_table WHERE ... LIMIT 100;

-- Then remove LIMIT for full query
```

### 4. Monitor Query Performance

```sql
-- PostgreSQL: Find slow queries
SELECT
    query,
    calls,
    total_time,
    mean_time,
    max_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;
```

### 5. Regular Maintenance

```sql
-- PostgreSQL: Update statistics for better query plans
ANALYZE experiments;

-- Rebuild indexes if fragmented
REINDEX TABLE experiments;

-- Clean up deleted rows
VACUUM experiments;
```

## Summary and Key Takeaways

### Core SQL Techniques

1. **JOINs**: Combine data from multiple tables (INNER, LEFT, RIGHT, FULL OUTER)
2. **Subqueries**: Nested queries for complex filtering
3. **CTEs**: Named query blocks for readability
4. **GROUP BY**: Aggregate data by categories
5. **Window Functions**: Advanced analytics without collapsing rows

### Optimization Principles

1. **Select specific columns**, not `*`
2. **Filter early** with WHERE
3. **Index strategically** (foreign keys, WHERE columns, JOIN columns)
4. **Avoid over-indexing** (each index has cost)
5. **Use EXPLAIN** to understand query plans
6. **Monitor performance** and optimize slow queries

### Advanced Patterns

- **Pivoting**: Transform rows to columns
- **Percentiles**: Statistical analysis
- **Moving Averages**: Time series analysis
- **Outlier Detection**: Find anomalies
- **Cohort Analysis**: Group by time periods

### ML-Specific Applications

- Compare experiment results across models
- Track model performance over time
- Analyze prediction patterns
- Compute aggregate metrics
- Monitor inference latency
- Find best hyperparameters

### Next Steps

In the next lecture, we'll cover:
- Object-Relational Mapping (ORMs)
- SQLAlchemy for Python
- Database migrations
- Connection pooling
- Transaction management
- Integration patterns for ML applications

---

**Estimated Study Time:** 5-6 hours
**Hands-on Practice:** Complete Exercise 03: Advanced SQL Queries
**Assessment:** Quiz covers JOINs, aggregations, window functions, and optimization
