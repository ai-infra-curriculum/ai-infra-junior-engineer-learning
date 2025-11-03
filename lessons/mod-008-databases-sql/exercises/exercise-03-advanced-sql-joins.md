# Exercise 03: Advanced SQL Joins & Analytical Queries

## Exercise Overview

**Objective**: Master advanced SQL query patterns including all join types, window functions, CTEs, and complex aggregations. Write production-ready analytical queries for ML infrastructure dashboards and reports.

**Difficulty**: Intermediate → Advanced
**Estimated Time**: 3-4 hours
**Prerequisites**:
- Exercise 01 (SQL Basics & CRUD) completed
- Exercise 02 (Database Design) completed with schema loaded
- Lecture 03 (Advanced SQL & Query Optimization)
- Understanding of set theory (INNER vs OUTER joins)

## Learning Objectives

By completing this exercise, you will:
- Master all JOIN types (INNER, LEFT, RIGHT, FULL OUTER, CROSS, SELF)
- Implement window functions (ROW_NUMBER, RANK, LAG, LEAD, SUM OVER)
- Write Common Table Expressions (CTEs) for complex multi-step queries
- Construct subqueries (correlated and non-correlated)
- Apply conditional aggregations using FILTER and CASE WHEN
- Use LATERAL joins for advanced query scenarios
- Analyze query performance with EXPLAIN and EXPLAIN ANALYZE
- Create materialized views for caching expensive analytical queries
- Build production-ready analytical queries for ML infrastructure dashboards
- Optimize query performance for large datasets

---

## Real-World Scenario

You're the **Senior ML Infrastructure Engineer** tasked with building analytics that power:

1. **Executive Dashboard**: Model deployment health, success rates, costs
2. **Compliance Reports**: Approval workflows, audit trails, SLA tracking
3. **Operations Metrics**: Resource utilization, failure analysis, performance trends
4. **Data Science Insights**: Model performance comparisons, dataset usage patterns

These queries will be used by:
- **Executives**: Monthly business reviews
- **Compliance Team**: Regulatory audits
- **MLOps Team**: Daily standups and incident response
- **Data Scientists**: Model selection and optimization

---

## Part 1: Understanding JOINs

### Step 1.1: JOIN Types Overview

**Visual Reference**:
```
Table A (models)     Table B (model_versions)
┌─────────┐         ┌─────────┐
│ A only  │         │ B only  │
│    ┌────┼─────────┼────┐    │
│    │ A∩B│         │ A∩B│    │
│    └────┼─────────┼────┘    │
└─────────┘         └─────────┘

INNER JOIN:  A ∩ B  (intersection only)
LEFT JOIN:   A       (all A + matching B)
RIGHT JOIN:       B  (all B + matching A)
FULL OUTER:  A ∪ B  (everything from both)
CROSS JOIN:  A × B  (cartesian product)
```

### Step 1.2: Setup Sample Data

Let's ensure we have comprehensive test data:

```sql
-- ============================================
-- Additional Sample Data for Exercise 03
-- ============================================
-- File: sql/20_sample_data_advanced.sql

-- Add more model versions
DO $$
DECLARE
    model_id_var UUID;
BEGIN
    -- Get sentiment classifier model ID
    SELECT model_id INTO model_id_var
    FROM models WHERE model_name = 'sentiment-classifier';

    INSERT INTO model_versions (model_id, semver, artifact_uri, framework, registered_by, status) VALUES
        (model_id_var, '1.2.0', 's3://ml-artifacts/sentiment-classifier/1.2.0/', 'pytorch', 'alice@example.com', 'registered'),
        (model_id_var, '1.3.0', 's3://ml-artifacts/sentiment-classifier/1.3.0/', 'pytorch', 'alice@example.com', 'validated'),
        (model_id_var, '2.0.0', 's3://ml-artifacts/sentiment-classifier/2.0.0/', 'pytorch', 'bob@example.com', 'deployed');
END $$;

-- Add training runs
INSERT INTO training_runs (version_id, run_name, status, accuracy, precision_score, recall_score, f1_score, gpu_hours, created_at)
SELECT
    mv.version_id,
    'run-' || mv.semver,
    CASE WHEN RANDOM() < 0.8 THEN 'succeeded' ELSE 'failed' END,
    0.8 + RANDOM() * 0.15,
    0.75 + RANDOM() * 0.2,
    0.75 + RANDOM() * 0.2,
    0.75 + RANDOM() * 0.2,
    RANDOM() * 20,
    NOW() - (RANDOM() * INTERVAL '30 days')
FROM model_versions mv
WHERE mv.framework = 'pytorch'
LIMIT 10;

-- Add deployments
INSERT INTO deployments (version_id, environment_id, deployed_by, status, deployed_at)
SELECT
    mv.version_id,
    e.environment_id,
    'ops@example.com',
    'active',
    NOW() - (RANDOM() * INTERVAL '60 days')
FROM model_versions mv
CROSS JOIN environments e
WHERE e.environment_name IN ('staging', 'prod')
  AND mv.status = 'deployed'
LIMIT 5;

-- Verify data
SELECT 'Data loaded' AS status;
SELECT COUNT(*) AS total_models FROM models;
SELECT COUNT(*) AS total_versions FROM model_versions;
SELECT COUNT(*) AS total_runs FROM training_runs;
SELECT COUNT(*) AS total_deployments FROM deployments;
```

✅ **Checkpoint**: Sample data loaded with models, versions, runs, and deployments.

---

## Part 2: INNER JOIN - The Foundation

### Step 2.1: Basic INNER JOIN

```sql
-- ==========================================
-- INNER JOIN EXAMPLES
-- ==========================================

-- Query 1: Models with their versions (INNER JOIN)
-- Returns only models that HAVE versions
SELECT
    m.model_name,
    m.display_name,
    mv.semver,
    mv.status AS version_status,
    mv.registered_at
FROM models m
INNER JOIN model_versions mv ON m.model_id = mv.model_id
ORDER BY m.model_name, mv.semver DESC;

-- Output:
-- model_name            | display_name          | semver | version_status | registered_at
-- fraud-detector        | Fraud Detection Model | 2.0.0  | validated      | 2025-10-20
-- sentiment-classifier  | Sentiment Classifier  | 2.0.0  | deployed       | 2025-10-22
-- sentiment-classifier  | Sentiment Classifier  | 1.3.0  | validated      | 2025-10-21
-- ... (only models WITH versions appear)
```

**Key Point**: INNER JOIN excludes models without versions!

### Step 2.2: Multi-Table INNER JOIN

```sql
-- Query 2: Complete model lineage (models → versions → training runs)
SELECT
    m.model_name,
    mv.semver,
    tr.run_name,
    tr.status AS run_status,
    tr.accuracy,
    tr.gpu_hours,
    tr.created_at
FROM models m
INNER JOIN model_versions mv ON m.model_id = mv.model_id
INNER JOIN training_runs tr ON mv.version_id = tr.version_id
WHERE tr.status = 'succeeded'
ORDER BY m.model_name, mv.semver DESC, tr.accuracy DESC;

-- This shows: Only models that have versions that have training runs
```

### Step 2.3: INNER JOIN with Aggregation

```sql
-- Query 3: Count training runs per model
SELECT
    m.model_name,
    m.display_name,
    COUNT(tr.run_id) AS total_runs,
    COUNT(*) FILTER (WHERE tr.status = 'succeeded') AS successful_runs,
    ROUND(AVG(tr.accuracy), 4) AS avg_accuracy,
    SUM(tr.gpu_hours) AS total_gpu_hours
FROM models m
INNER JOIN model_versions mv ON m.model_id = mv.model_id
INNER JOIN training_runs tr ON mv.version_id = tr.version_id
GROUP BY m.model_id, m.model_name, m.display_name
HAVING COUNT(tr.run_id) > 0
ORDER BY total_gpu_hours DESC;
```

✅ **Checkpoint**: You understand INNER JOIN returns only matching rows from both tables.

---

## Part 3: LEFT JOIN - Include All from Left Table

### Step 3.1: Basic LEFT JOIN

```sql
-- ==========================================
-- LEFT JOIN (LEFT OUTER JOIN) EXAMPLES
-- ==========================================

-- Query 4: ALL models with their versions (if any)
-- Returns models even if they have NO versions
SELECT
    m.model_name,
    m.display_name,
    m.created_at,
    mv.semver,
    mv.status AS version_status
FROM models m
LEFT JOIN model_versions mv ON m.model_id = mv.model_id
ORDER BY m.model_name, mv.semver DESC NULLS LAST;

-- Output includes:
-- model_name          | display_name        | semver | version_status
-- fraud-detector      | Fraud Detection     | 2.0.0  | validated
-- new-model-no-vers   | New Model           | NULL   | NULL
-- sentiment-class...  | Sentiment Class...  | 2.0.0  | deployed
-- ... (ALL models appear, even those without versions)
```

**Key Point**: LEFT JOIN keeps ALL rows from left table (models), adding NULL for missing matches!

### Step 3.2: Finding Missing Relationships

```sql
-- Query 5: Find models WITHOUT any versions (quality check)
SELECT
    m.model_name,
    m.display_name,
    m.created_at,
    m.created_by,
    COUNT(mv.version_id) AS version_count
FROM models m
LEFT JOIN model_versions mv ON m.model_id = mv.model_id
GROUP BY m.model_id, m.model_name, m.display_name, m.created_at, m.created_by
HAVING COUNT(mv.version_id) = 0
ORDER BY m.created_at DESC;

-- Useful for finding:
-- - Abandoned models
-- - Models in registration process
-- - Data quality issues
```

### Step 3.3: LEFT JOIN with COALESCE

```sql
-- Query 6: All models with version count (0 if none)
SELECT
    m.model_name,
    m.display_name,
    m.risk_level,
    COALESCE(COUNT(mv.version_id), 0) AS version_count,
    COALESCE(MAX(mv.registered_at), m.created_at) AS last_activity
FROM models m
LEFT JOIN model_versions mv ON m.model_id = mv.model_id
GROUP BY m.model_id, m.model_name, m.display_name, m.risk_level, m.created_at
ORDER BY version_count DESC, last_activity DESC;
```

### Step 3.4: Multi-Level LEFT JOINs

```sql
-- Query 7: Complete model info even if versions/runs don't exist
SELECT
    m.model_name,
    m.display_name,
    t.team_name,
    mv.semver,
    tr.run_name,
    tr.accuracy,
    d.dataset_name
FROM models m
LEFT JOIN teams t ON m.team_id = t.team_id
LEFT JOIN model_versions mv ON m.model_id = mv.model_id
LEFT JOIN training_runs tr ON mv.version_id = tr.version_id
LEFT JOIN run_datasets rd ON tr.run_id = rd.run_id
LEFT JOIN datasets d ON rd.dataset_id = d.dataset_id
WHERE m.model_name = 'sentiment-classifier'
ORDER BY mv.semver DESC NULLS LAST, tr.created_at DESC NULLS LAST;

-- Shows complete lineage even if some parts are missing
```

✅ **Checkpoint**: You understand LEFT JOIN preserves all left table rows with NULL for missing matches.

---

## Part 4: RIGHT JOIN and FULL OUTER JOIN

### Step 4.1: RIGHT JOIN (Rarely Used)

```sql
-- ==========================================
-- RIGHT JOIN EXAMPLES
-- ==========================================

-- Query 8: All versions with their models (if model exists)
-- RIGHT JOIN is the opposite of LEFT JOIN
SELECT
    m.model_name,
    m.display_name,
    mv.semver,
    mv.status,
    mv.registered_at
FROM models m
RIGHT JOIN model_versions mv ON m.model_id = mv.model_id
ORDER BY mv.registered_at DESC;

-- Equivalent to:
SELECT
    m.model_name,
    m.display_name,
    mv.semver,
    mv.status,
    mv.registered_at
FROM model_versions mv
LEFT JOIN models m ON mv.model_id = m.model_id
ORDER BY mv.registered_at DESC;
```

**Best Practice**: Most developers prefer LEFT JOIN and reorder tables instead of using RIGHT JOIN.

### Step 4.2: FULL OUTER JOIN

```sql
-- ==========================================
-- FULL OUTER JOIN EXAMPLES
-- ==========================================

-- Query 9: All models AND all tags (whether linked or not)
SELECT
    m.model_name,
    t.tag_category,
    t.tag_value,
    CASE
        WHEN m.model_id IS NULL THEN 'Unused tag'
        WHEN t.tag_id IS NULL THEN 'Untagged model'
        ELSE 'Tagged'
    END AS relationship_status
FROM models m
FULL OUTER JOIN model_tags mt ON m.model_id = mt.model_id
FULL OUTER JOIN tags t ON mt.tag_id = t.tag_id
ORDER BY relationship_status, m.model_name NULLS LAST;

-- Useful for finding:
-- - Unused tags (no models)
-- - Untagged models
-- - Complete inventory
```

### Step 4.3: Practical FULL OUTER JOIN

```sql
-- Query 10: Reconcile expected vs actual deployments
WITH expected_deployments AS (
    SELECT
        mv.version_id,
        e.environment_id,
        mv.semver,
        e.environment_name
    FROM model_versions mv
    CROSS JOIN environments e
    WHERE mv.status = 'deployed'
      AND e.environment_type IN ('staging', 'production')
),
actual_deployments AS (
    SELECT
        version_id,
        environment_id,
        deployed_at,
        status
    FROM deployments
    WHERE status = 'active'
)
SELECT
    ex.semver,
    ex.environment_name,
    CASE
        WHEN act.version_id IS NULL THEN 'MISSING - Expected but not deployed'
        WHEN ex.version_id IS NULL THEN 'EXTRA - Deployed but not expected'
        ELSE 'OK - Deployed as expected'
    END AS deployment_status,
    act.deployed_at,
    act.status
FROM expected_deployments ex
FULL OUTER JOIN actual_deployments act
    ON ex.version_id = act.version_id
    AND ex.environment_id = act.environment_id
ORDER BY deployment_status, ex.semver;
```

✅ **Checkpoint**: You understand FULL OUTER JOIN returns all rows from both tables.

---

## Part 5: CROSS JOIN and SELF JOIN

### Step 5.1: CROSS JOIN (Cartesian Product)

```sql
-- ==========================================
-- CROSS JOIN EXAMPLES
-- ==========================================

-- Query 11: All possible model-environment combinations
SELECT
    m.model_name,
    e.environment_name,
    e.environment_type
FROM models m
CROSS JOIN environments e
WHERE e.environment_type IN ('staging', 'production')
ORDER BY m.model_name, e.priority;

-- Useful for:
-- - Generating all possible combinations
-- - Creating deployment matrices
-- - Test case generation
```

### Step 5.2: CROSS JOIN with Filter

```sql
-- Query 12: Identify missing deployments
SELECT
    m.model_name,
    mv.semver,
    e.environment_name,
    'Missing deployment' AS status
FROM models m
CROSS JOIN model_versions mv
CROSS JOIN environments e
WHERE mv.model_id = m.model_id
  AND mv.status = 'deployed'
  AND e.environment_name = 'prod'
  AND NOT EXISTS (
      SELECT 1
      FROM deployments d
      WHERE d.version_id = mv.version_id
        AND d.environment_id = e.environment_id
        AND d.status = 'active'
  )
ORDER BY m.model_name, mv.semver;
```

### Step 5.3: SELF JOIN

```sql
-- ==========================================
-- SELF JOIN EXAMPLES
-- ==========================================

-- Query 13: Compare model versions (current vs previous)
SELECT
    m.model_name,
    curr.semver AS current_version,
    curr.registered_at AS current_registered,
    prev.semver AS previous_version,
    prev.registered_at AS previous_registered,
    EXTRACT(DAYS FROM (curr.registered_at - prev.registered_at)) AS days_between
FROM models m
INNER JOIN model_versions curr ON m.model_id = curr.model_id
LEFT JOIN model_versions prev ON m.model_id = prev.model_id
    AND prev.registered_at < curr.registered_at
    AND NOT EXISTS (
        SELECT 1 FROM model_versions mid
        WHERE mid.model_id = m.model_id
          AND mid.registered_at > prev.registered_at
          AND mid.registered_at < curr.registered_at
    )
WHERE m.model_name = 'sentiment-classifier'
ORDER BY curr.registered_at DESC;

-- Shows: Each version with its immediate predecessor
```

### Step 5.4: Find Duplicates with SELF JOIN

```sql
-- Query 14: Find potential duplicate models (similar names)
SELECT DISTINCT
    m1.model_name AS model_1,
    m2.model_name AS model_2,
    m1.objective AS objective_1,
    m2.objective AS objective_2
FROM models m1
INNER JOIN models m2 ON m1.model_id < m2.model_id  -- Avoid duplicate pairs
WHERE SIMILARITY(m1.model_name, m2.model_name) > 0.6  -- PostgreSQL pg_trgm extension
   OR m1.objective = m2.objective;

-- Helps identify:
-- - Duplicate registrations
-- - Similar models that should be merged
-- - Naming convention violations
```

✅ **Checkpoint**: You understand CROSS JOIN (all combinations) and SELF JOIN (table joins itself).

---

## Part 6: Window Functions

### Step 6.1: ROW_NUMBER and RANK

```sql
-- ==========================================
-- WINDOW FUNCTIONS
-- ==========================================

-- Query 15: Rank models by accuracy within each framework
SELECT
    m.model_name,
    mv.framework,
    tr.accuracy,
    ROW_NUMBER() OVER (PARTITION BY mv.framework ORDER BY tr.accuracy DESC) AS row_num,
    RANK() OVER (PARTITION BY mv.framework ORDER BY tr.accuracy DESC) AS rank,
    DENSE_RANK() OVER (PARTITION BY mv.framework ORDER BY tr.accuracy DESC) AS dense_rank
FROM models m
INNER JOIN model_versions mv ON m.model_id = mv.model_id
INNER JOIN training_runs tr ON mv.version_id = tr.version_id
WHERE tr.status = 'succeeded'
  AND tr.accuracy IS NOT NULL
ORDER BY mv.framework, tr.accuracy DESC;

-- ROW_NUMBER: 1, 2, 3, 4 (always unique)
-- RANK:       1, 2, 2, 4 (ties share rank, skip next)
-- DENSE_RANK: 1, 2, 2, 3 (ties share rank, don't skip)
```

### Step 6.2: Get Latest Record per Group

```sql
-- Query 16: Latest deployment per model (most common pattern!)
SELECT
    model_name,
    semver,
    environment_name,
    deployed_at,
    deployed_by,
    status
FROM (
    SELECT
        m.model_name,
        mv.semver,
        e.environment_name,
        d.deployed_at,
        d.deployed_by,
        d.status,
        ROW_NUMBER() OVER (
            PARTITION BY m.model_id, e.environment_id
            ORDER BY d.deployed_at DESC
        ) AS rn
    FROM models m
    INNER JOIN model_versions mv ON m.model_id = mv.model_id
    INNER JOIN deployments d ON mv.version_id = d.version_id
    INNER JOIN environments e ON d.environment_id = e.environment_id
) ranked
WHERE rn = 1
ORDER BY model_name, environment_name;

-- Gets most recent deployment for each model in each environment
```

### Step 6.3: LAG and LEAD

```sql
-- Query 17: Compare accuracy with previous training run
SELECT
    m.model_name,
    mv.semver,
    tr.run_name,
    tr.accuracy AS current_accuracy,
    LAG(tr.accuracy) OVER (
        PARTITION BY m.model_id
        ORDER BY tr.created_at
    ) AS previous_accuracy,
    tr.accuracy - LAG(tr.accuracy) OVER (
        PARTITION BY m.model_id
        ORDER BY tr.created_at
    ) AS accuracy_delta,
    CASE
        WHEN tr.accuracy > LAG(tr.accuracy) OVER (PARTITION BY m.model_id ORDER BY tr.created_at)
        THEN '↑ Improved'
        WHEN tr.accuracy < LAG(tr.accuracy) OVER (PARTITION BY m.model_id ORDER BY tr.created_at)
        THEN '↓ Degraded'
        ELSE '→ Same'
    END AS trend
FROM models m
INNER JOIN model_versions mv ON m.model_id = mv.model_id
INNER JOIN training_runs tr ON mv.version_id = tr.version_id
WHERE tr.status = 'succeeded'
  AND tr.accuracy IS NOT NULL
ORDER BY m.model_name, tr.created_at;

-- LAG: Access previous row in window
-- LEAD: Access next row in window
```

### Step 6.4: Running Totals and Moving Averages

```sql
-- Query 18: Running total of GPU hours per model
SELECT
    m.model_name,
    tr.created_at::DATE AS run_date,
    tr.gpu_hours,
    SUM(tr.gpu_hours) OVER (
        PARTITION BY m.model_id
        ORDER BY tr.created_at
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS cumulative_gpu_hours,
    AVG(tr.gpu_hours) OVER (
        PARTITION BY m.model_id
        ORDER BY tr.created_at
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) AS moving_avg_7_runs
FROM models m
INNER JOIN model_versions mv ON m.model_id = mv.model_id
INNER JOIN training_runs tr ON mv.version_id = tr.version_id
WHERE tr.status = 'succeeded'
ORDER BY m.model_name, tr.created_at;

-- ROWS BETWEEN: Define the window frame
-- UNBOUNDED PRECEDING: From start
-- N PRECEDING: Last N rows
-- CURRENT ROW: Up to current
```

### Step 6.5: NTILE for Percentiles

```sql
-- Query 19: Quartile analysis of model accuracy
SELECT
    m.model_name,
    tr.accuracy,
    NTILE(4) OVER (ORDER BY tr.accuracy) AS accuracy_quartile,
    PERCENT_RANK() OVER (ORDER BY tr.accuracy) AS percentile_rank,
    CASE
        WHEN NTILE(4) OVER (ORDER BY tr.accuracy) = 4 THEN 'Top 25%'
        WHEN NTILE(4) OVER (ORDER BY tr.accuracy) = 3 THEN 'Above Average'
        WHEN NTILE(4) OVER (ORDER BY tr.accuracy) = 2 THEN 'Below Average'
        ELSE 'Bottom 25%'
    END AS performance_category
FROM models m
INNER JOIN model_versions mv ON m.model_id = mv.model_id
INNER JOIN training_runs tr ON mv.version_id = tr.version_id
WHERE tr.status = 'succeeded'
  AND tr.accuracy IS NOT NULL
ORDER BY tr.accuracy DESC;

-- NTILE(N): Divide into N equal buckets
-- PERCENT_RANK(): Percentile (0.0 to 1.0)
```

✅ **Checkpoint**: You can use window functions for ranking, comparisons, and running calculations.

---

## Part 7: Common Table Expressions (CTEs)

### Step 7.1: Simple CTE

```sql
-- ==========================================
-- COMMON TABLE EXPRESSIONS (WITH clause)
-- ==========================================

-- Query 20: Multi-step analysis with CTEs
WITH production_models AS (
    -- Step 1: Find models in production
    SELECT DISTINCT
        m.model_id,
        m.model_name,
        m.risk_level
    FROM models m
    INNER JOIN model_versions mv ON m.model_id = mv.model_id
    INNER JOIN deployments d ON mv.version_id = d.version_id
    INNER JOIN environments e ON d.environment_id = e.environment_id
    WHERE e.environment_type = 'production'
      AND d.status = 'active'
),
model_metrics AS (
    -- Step 2: Calculate metrics for those models
    SELECT
        pm.model_id,
        pm.model_name,
        COUNT(tr.run_id) AS total_runs,
        AVG(tr.accuracy) AS avg_accuracy,
        MAX(tr.accuracy) AS best_accuracy,
        SUM(tr.gpu_hours) AS total_gpu_cost
    FROM production_models pm
    INNER JOIN model_versions mv ON pm.model_id = mv.model_id
    LEFT JOIN training_runs tr ON mv.version_id = tr.version_id
    WHERE tr.status = 'succeeded'
    GROUP BY pm.model_id, pm.model_name
)
-- Step 3: Final output with derived fields
SELECT
    mm.model_name,
    mm.total_runs,
    ROUND(mm.avg_accuracy::numeric, 4) AS avg_accuracy,
    ROUND(mm.best_accuracy::numeric, 4) AS best_accuracy,
    mm.total_gpu_cost,
    CASE
        WHEN mm.total_runs < 10 THEN 'Undertested'
        WHEN mm.avg_accuracy < 0.85 THEN 'Needs improvement'
        ELSE 'Healthy'
    END AS health_status
FROM model_metrics mm
ORDER BY mm.total_gpu_cost DESC;

-- CTEs make complex queries readable!
```

### Step 7.2: Multiple CTEs with JOINs

```sql
-- Query 21: Deployment readiness report
WITH latest_versions AS (
    SELECT DISTINCT ON (m.model_id)
        m.model_id,
        m.model_name,
        m.compliance_required,
        mv.version_id,
        mv.semver,
        mv.status
    FROM models m
    INNER JOIN model_versions mv ON m.model_id = mv.model_id
    ORDER BY m.model_id, mv.registered_at DESC
),
approval_status AS (
    SELECT
        lv.model_id,
        lv.version_id,
        COUNT(*) FILTER (WHERE a.status = 'approved') AS approvals_granted,
        COUNT(*) FILTER (WHERE a.status = 'pending') AS approvals_pending,
        COUNT(*) FILTER (WHERE a.status = 'rejected') AS approvals_rejected
    FROM latest_versions lv
    LEFT JOIN approvals a ON lv.version_id = a.version_id
    GROUP BY lv.model_id, lv.version_id
),
deployment_status AS (
    SELECT
        lv.model_id,
        COUNT(*) FILTER (WHERE d.status = 'active' AND e.environment_type = 'production') AS prod_deployments
    FROM latest_versions lv
    LEFT JOIN deployments d ON lv.version_id = d.version_id
    LEFT JOIN environments e ON d.environment_id = e.environment_id
    GROUP BY lv.model_id
)
SELECT
    lv.model_name,
    lv.semver,
    lv.status AS version_status,
    lv.compliance_required,
    COALESCE(ast.approvals_granted, 0) AS approvals_granted,
    COALESCE(ast.approvals_pending, 0) AS approvals_pending,
    COALESCE(dst.prod_deployments, 0) AS prod_deployments,
    CASE
        WHEN lv.compliance_required AND COALESCE(ast.approvals_granted, 0) = 0
            THEN '⚠️ Blocked - Needs approval'
        WHEN COALESCE(ast.approvals_rejected, 0) > 0
            THEN '❌ Blocked - Approval rejected'
        WHEN lv.status != 'validated'
            THEN '⏳ Not ready - Needs validation'
        WHEN COALESCE(dst.prod_deployments, 0) > 0
            THEN '✅ Deployed to production'
        ELSE '✅ Ready for deployment'
    END AS readiness_status
FROM latest_versions lv
LEFT JOIN approval_status ast ON lv.model_id = ast.model_id
LEFT JOIN deployment_status dst ON lv.model_id = dst.model_id
ORDER BY readiness_status, lv.model_name;
```

### Step 7.3: Recursive CTE (Advanced)

```sql
-- Query 22: Model version history tree (if versions reference parent versions)
-- Note: This requires a parent_version_id column in model_versions

-- First, let's imagine we have version lineage
-- ALTER TABLE model_versions ADD COLUMN parent_version_id UUID REFERENCES model_versions(version_id);

-- Recursive CTE example:
WITH RECURSIVE version_lineage AS (
    -- Base case: root versions (no parent)
    SELECT
        version_id,
        model_id,
        semver,
        parent_version_id,
        1 AS depth,
        semver::TEXT AS lineage_path
    FROM model_versions
    WHERE parent_version_id IS NULL

    UNION ALL

    -- Recursive case: child versions
    SELECT
        mv.version_id,
        mv.model_id,
        mv.semver,
        mv.parent_version_id,
        vl.depth + 1,
        vl.lineage_path || ' → ' || mv.semver
    FROM model_versions mv
    INNER JOIN version_lineage vl ON mv.parent_version_id = vl.version_id
    WHERE vl.depth < 10  -- Prevent infinite recursion
)
SELECT
    m.model_name,
    vl.semver,
    vl.depth,
    vl.lineage_path
FROM version_lineage vl
INNER JOIN models m ON vl.model_id = m.model_id
ORDER BY m.model_name, vl.depth, vl.semver;

-- Recursive CTEs are powerful for hierarchical data!
```

✅ **Checkpoint**: You can use CTEs to break complex queries into readable steps.

---

## Part 8: Subqueries

### Step 8.1: Subquery in WHERE Clause

```sql
-- ==========================================
-- SUBQUERIES
-- ==========================================

-- Query 23: Models with above-average accuracy
SELECT
    m.model_name,
    AVG(tr.accuracy) AS avg_accuracy
FROM models m
INNER JOIN model_versions mv ON m.model_id = mv.model_id
INNER JOIN training_runs tr ON mv.version_id = tr.version_id
WHERE tr.status = 'succeeded'
  AND tr.accuracy IS NOT NULL
GROUP BY m.model_id, m.model_name
HAVING AVG(tr.accuracy) > (
    -- Subquery: calculate global average
    SELECT AVG(accuracy)
    FROM training_runs
    WHERE status = 'succeeded'
      AND accuracy IS NOT NULL
)
ORDER BY avg_accuracy DESC;
```

### Step 8.2: Correlated Subquery

```sql
-- Query 24: Models with their best training run
SELECT
    m.model_name,
    m.display_name,
    (
        SELECT MAX(tr.accuracy)
        FROM model_versions mv
        INNER JOIN training_runs tr ON mv.version_id = tr.version_id
        WHERE mv.model_id = m.model_id
          AND tr.status = 'succeeded'
    ) AS best_accuracy,
    (
        SELECT COUNT(*)
        FROM model_versions mv
        WHERE mv.model_id = m.model_id
    ) AS version_count
FROM models m
ORDER BY best_accuracy DESC NULLS LAST;

-- Correlated: subquery references outer query (m.model_id)
```

### Step 8.3: EXISTS and NOT EXISTS

```sql
-- Query 25: Models with at least one failed training run
SELECT
    m.model_name,
    m.display_name,
    m.risk_level
FROM models m
WHERE EXISTS (
    SELECT 1
    FROM model_versions mv
    INNER JOIN training_runs tr ON mv.version_id = tr.version_id
    WHERE mv.model_id = m.model_id
      AND tr.status = 'failed'
)
ORDER BY m.risk_level DESC, m.model_name;

-- Query 26: Models with NO successful deployments
SELECT
    m.model_name,
    m.display_name,
    m.created_at
FROM models m
WHERE NOT EXISTS (
    SELECT 1
    FROM model_versions mv
    INNER JOIN deployments d ON mv.version_id = d.version_id
    WHERE mv.model_id = m.model_id
      AND d.status = 'active'
)
ORDER BY m.created_at;

-- EXISTS is more efficient than COUNT(*) > 0
```

### Step 8.4: Subquery in FROM (Derived Table)

```sql
-- Query 27: Ranking models by multiple metrics
SELECT
    metrics.model_name,
    metrics.avg_accuracy,
    metrics.total_runs,
    metrics.total_cost,
    NTILE(3) OVER (ORDER BY metrics.avg_accuracy DESC) AS accuracy_tier,
    NTILE(3) OVER (ORDER BY metrics.total_cost ASC) AS cost_efficiency_tier
FROM (
    SELECT
        m.model_name,
        AVG(tr.accuracy) AS avg_accuracy,
        COUNT(tr.run_id) AS total_runs,
        SUM(tr.gpu_hours) * 2.5 AS total_cost  -- $2.50/GPU hour
    FROM models m
    INNER JOIN model_versions mv ON m.model_id = mv.model_id
    INNER JOIN training_runs tr ON mv.version_id = tr.version_id
    WHERE tr.status = 'succeeded'
    GROUP BY m.model_id, m.model_name
    HAVING COUNT(tr.run_id) >= 3
) AS metrics
ORDER BY metrics.avg_accuracy DESC;
```

✅ **Checkpoint**: You can use subqueries in WHERE, SELECT, FROM, and with EXISTS.

---

## Part 9: LATERAL Joins (Advanced)

### Step 9.1: LATERAL with Function Call

```sql
-- ==========================================
-- LATERAL JOINS
-- ==========================================

-- Query 28: Top 3 training runs per model
SELECT
    m.model_name,
    top_runs.run_name,
    top_runs.accuracy,
    top_runs.created_at
FROM models m
CROSS JOIN LATERAL (
    SELECT
        tr.run_name,
        tr.accuracy,
        tr.created_at
    FROM model_versions mv
    INNER JOIN training_runs tr ON mv.version_id = tr.version_id
    WHERE mv.model_id = m.model_id
      AND tr.status = 'succeeded'
      AND tr.accuracy IS NOT NULL
    ORDER BY tr.accuracy DESC
    LIMIT 3
) AS top_runs
ORDER BY m.model_name, top_runs.accuracy DESC;

-- LATERAL allows subquery to reference outer query
-- Similar to correlated subquery but returns multiple rows
```

### Step 9.2: LATERAL for Latest Record Pattern

```sql
-- Query 29: Models with their latest deployment (using LATERAL)
SELECT
    m.model_name,
    m.display_name,
    latest_deploy.environment_name,
    latest_deploy.deployed_at,
    latest_deploy.status
FROM models m
CROSS JOIN LATERAL (
    SELECT
        e.environment_name,
        d.deployed_at,
        d.status
    FROM model_versions mv
    INNER JOIN deployments d ON mv.version_id = d.version_id
    INNER JOIN environments e ON d.environment_id = e.environment_id
    WHERE mv.model_id = m.model_id
      AND e.environment_type = 'production'
    ORDER BY d.deployed_at DESC
    LIMIT 1
) AS latest_deploy
ORDER BY m.model_name;
```

✅ **Checkpoint**: You understand LATERAL joins for row-level subqueries.

---

## Part 10: Performance Analysis with EXPLAIN

### Step 10.1: Understanding EXPLAIN

```sql
-- ==========================================
-- QUERY PERFORMANCE ANALYSIS
-- ==========================================

-- Query 30: Basic EXPLAIN
EXPLAIN
SELECT m.model_name, COUNT(mv.version_id)
FROM models m
LEFT JOIN model_versions mv ON m.model_id = mv.model_id
GROUP BY m.model_id, m.model_name;

-- Output shows:
-- HashAggregate  (cost=X..Y rows=Z width=W)
--   Group Key: m.model_id, m.model_name
--   ->  Hash Left Join  (cost=X..Y rows=Z width=W)
--         Hash Cond: (mv.model_id = m.model_id)
--         ->  Seq Scan on model_versions mv  (cost=X..Y rows=Z width=W)
--         ->  Hash  (cost=X..Y rows=Z width=W)
--               ->  Seq Scan on models m  (cost=X..Y rows=Z width=W)
```

### Step 10.2: EXPLAIN ANALYZE (Actual Execution)

```sql
-- Query 31: EXPLAIN ANALYZE for actual runtime
EXPLAIN ANALYZE
SELECT
    m.model_name,
    COUNT(tr.run_id) AS total_runs,
    AVG(tr.accuracy) AS avg_accuracy
FROM models m
INNER JOIN model_versions mv ON m.model_id = mv.model_id
INNER JOIN training_runs tr ON mv.version_id = tr.version_id
WHERE tr.status = 'succeeded'
GROUP BY m.model_id, m.model_name
ORDER BY avg_accuracy DESC;

-- Output includes:
-- Actual time: X..Y ms
-- Rows: Z (actual) vs Z (estimated)
-- Loops: N

-- Look for:
-- - Seq Scan (table scan) - might need index
-- - Index Scan - using index
-- - Hash Join - good for large datasets
-- - Nested Loop - good for small datasets
-- - Sort - might be expensive
```

### Step 10.3: Performance Comparison

```sql
-- Query 32: Compare indexed vs non-indexed query

-- Without index on training_runs.status
EXPLAIN ANALYZE
SELECT * FROM training_runs WHERE status = 'failed';
-- Shows: Seq Scan on training_runs

-- Create index
CREATE INDEX idx_training_runs_status_temp ON training_runs(status);

-- With index
EXPLAIN ANALYZE
SELECT * FROM training_runs WHERE status = 'failed';
-- Shows: Index Scan using idx_training_runs_status_temp

-- Check performance difference
\timing on
SELECT COUNT(*) FROM training_runs WHERE status = 'failed';
-- Time: X ms (with index)

-- Drop temporary index
DROP INDEX idx_training_runs_status_temp;

-- Time: Y ms (without index)
```

✅ **Checkpoint**: You can use EXPLAIN ANALYZE to understand query performance.

---

## Part 11: Materialized Views

### Step 11.1: Create Materialized View

```sql
-- ==========================================
-- MATERIALIZED VIEWS
-- ==========================================

-- Query 33: Create materialized view for expensive query
CREATE MATERIALIZED VIEW mv_model_health_summary AS
SELECT
    m.model_id,
    m.model_name,
    m.display_name,
    m.risk_level,
    COUNT(DISTINCT mv.version_id) AS total_versions,
    COUNT(DISTINCT tr.run_id) AS total_runs,
    COUNT(DISTINCT tr.run_id) FILTER (WHERE tr.status = 'succeeded') AS successful_runs,
    ROUND(AVG(tr.accuracy) FILTER (WHERE tr.status = 'succeeded')::numeric, 4) AS avg_accuracy,
    SUM(tr.gpu_hours) AS total_gpu_hours,
    MAX(tr.created_at) AS last_run_date,
    COUNT(DISTINCT d.deployment_id) FILTER (
        WHERE d.status = 'active'
    ) AS active_deployments
FROM models m
LEFT JOIN model_versions mv ON m.model_id = mv.model_id
LEFT JOIN training_runs tr ON mv.version_id = tr.version_id
LEFT JOIN deployments d ON mv.version_id = d.version_id
GROUP BY m.model_id, m.model_name, m.display_name, m.risk_level;

-- Create index on materialized view
CREATE INDEX idx_mv_model_health_model_name ON mv_model_health_summary(model_name);

-- Query the materialized view (fast!)
SELECT * FROM mv_model_health_summary
WHERE risk_level = 'critical'
ORDER BY avg_accuracy DESC NULLS LAST;
```

### Step 11.2: Refresh Materialized View

```sql
-- Refresh materialized view (updates data)
REFRESH MATERIALIZED VIEW mv_model_health_summary;

-- Refresh without blocking reads (PostgreSQL 9.4+)
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_model_health_summary;

-- Check when last refreshed
SELECT
    schemaname,
    matviewname,
    matviewowner,
    ispopulated,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||matviewname)) AS size
FROM pg_matviews
WHERE matviewname = 'mv_model_health_summary';
```

### Step 11.3: Automatic Refresh Strategy

```sql
-- Create function to refresh materialized views
CREATE OR REPLACE FUNCTION refresh_model_health_summary()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_model_health_summary;
END;
$$ LANGUAGE plpgsql;

-- Schedule with pg_cron (requires pg_cron extension)
-- SELECT cron.schedule('refresh-model-health', '0 */6 * * *', 'SELECT refresh_model_health_summary()');
-- Runs every 6 hours

-- Or call manually from application
-- SELECT refresh_model_health_summary();
```

✅ **Checkpoint**: You can create materialized views to cache expensive queries.

---

## Part 12: Hands-On Challenges

### Challenge 1: Executive Dashboard Query

Write a query that provides:
- Model name
- Total versions
- Latest version
- Production deployment status (Yes/No)
- Average accuracy of all successful runs
- Total GPU cost (hours * $2.50)
- Health status (Healthy/Warning/Critical based on accuracy and deployment)

<details>
<summary>Solution</summary>

```sql
WITH latest_versions AS (
    SELECT DISTINCT ON (model_id)
        model_id,
        semver AS latest_version
    FROM model_versions
    ORDER BY model_id, registered_at DESC
),
prod_status AS (
    SELECT DISTINCT
        mv.model_id,
        TRUE AS has_prod_deployment
    FROM model_versions mv
    INNER JOIN deployments d ON mv.version_id = d.version_id
    INNER JOIN environments e ON d.environment_id = e.environment_id
    WHERE e.environment_type = 'production' AND d.status = 'active'
)
SELECT
    m.model_name,
    COUNT(DISTINCT mv.version_id) AS total_versions,
    lv.latest_version,
    COALESCE(ps.has_prod_deployment, FALSE) AS in_production,
    ROUND(AVG(tr.accuracy) FILTER (WHERE tr.status = 'succeeded')::numeric, 4) AS avg_accuracy,
    ROUND((SUM(tr.gpu_hours) * 2.50)::numeric, 2) AS total_cost_usd,
    CASE
        WHEN AVG(tr.accuracy) FILTER (WHERE tr.status = 'succeeded') >= 0.90 AND ps.has_prod_deployment THEN 'Healthy'
        WHEN AVG(tr.accuracy) FILTER (WHERE tr.status = 'succeeded') >= 0.80 THEN 'Warning'
        ELSE 'Critical'
    END AS health_status
FROM models m
LEFT JOIN model_versions mv ON m.model_id = mv.model_id
LEFT JOIN training_runs tr ON mv.version_id = tr.version_id
LEFT JOIN latest_versions lv ON m.model_id = lv.model_id
LEFT JOIN prod_status ps ON m.model_id = ps.model_id
GROUP BY m.model_id, m.model_name, lv.latest_version, ps.has_prod_deployment
ORDER BY health_status DESC, avg_accuracy DESC NULLS LAST;
```
</details>

### Challenge 2: Compliance Audit Report

Write a query showing:
- All production deployments
- Associated approvals (approval type, approver, date)
- Models missing required approvals
- SLA compliance (deployment within 5 days of approval)

### Challenge 3: Resource Optimization Query

Identify:
- Models with low utilization (< 5 runs in last 30 days)
- Models with high cost but low accuracy (GPU hours > 50, accuracy < 0.80)
- Recommended actions (deprecate, optimize, retrain)

---

## Part 13: Summary and Deliverables

### What You Learned

✅ **JOIN Types**:
- INNER JOIN (intersection)
- LEFT/RIGHT JOIN (preserve one side)
- FULL OUTER JOIN (union)
- CROSS JOIN (cartesian product)
- SELF JOIN (compare rows in same table)

✅ **Window Functions**:
- ROW_NUMBER, RANK, DENSE_RANK
- LAG, LEAD (compare with previous/next)
- Running totals with SUM OVER
- Moving averages with window frames
- NTILE for percentiles

✅ **Advanced Patterns**:
- CTEs for readable multi-step queries
- Subqueries (correlated and non-correlated)
- EXISTS for efficient existence checks
- LATERAL joins for row-level subqueries

✅ **Performance**:
- EXPLAIN and EXPLAIN ANALYZE
- Index usage analysis
- Materialized views for caching

### Deliverables Checklist

- [ ] `sql/30_advanced_queries.sql` - All example queries
- [ ] At least 3 complex analytical queries for dashboards
- [ ] EXPLAIN ANALYZE output for 3+ queries
- [ ] 1 materialized view created
- [ ] Documentation of performance findings
- [ ] Reflection written (300-500 words)

### Reflection Questions

1. **Complexity**: Which join type was most challenging and why?
2. **Window Functions**: How do they simplify problems vs subqueries?
3. **Performance**: What was your biggest performance insight?
4. **Production**: How would you monitor these queries in production?
5. **Testing**: How would you test these queries in CI/CD?

---

## Next Steps

- **Exercise 04**: SQLAlchemy ORM Integration - Connect Python applications to this schema
- **Exercise 05**: Optimization & Indexing - Deep dive into query performance

---

## Additional Resources

- [PostgreSQL Window Functions](https://www.postgresql.org/docs/current/tutorial-window.html)
- [Understanding EXPLAIN](https://www.postgresql.org/docs/current/using-explain.html)
- [SQL Joins Visualized](https://joins.spathon.com/)
- [PostgreSQL Performance Tips](https://wiki.postgresql.org/wiki/Performance_Optimization)

---

**Exercise Complete!** 🎉

You've mastered advanced SQL joins and analytical queries. You can now write complex production queries for ML infrastructure dashboards and reports.

**Estimated Time**: 3-4 hours
**Difficulty**: Intermediate → Advanced
**Lines of Code**: ~200 SQL queries
**Learning Objectives**: ✅ All achieved
**Ready for**: Exercise 04 - SQLAlchemy ORM Integration
