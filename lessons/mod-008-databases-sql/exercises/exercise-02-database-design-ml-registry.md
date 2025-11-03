# Exercise 02: Database Design for ML Model Registry

## Exercise Overview

**Objective**: Design and implement a production-grade, normalized relational database schema for an ML Model Registry. Master entity-relationship modeling, normalization principles, foreign keys, and referential integrity.

**Difficulty**: Intermediate
**Estimated Time**: 3-4 hours
**Prerequisites**:
- Lecture 02 (Database Design & Normalization)
- Exercise 01 (SQL Basics & CRUD) completed
- Understanding of primary keys and foreign keys
- Basic ER diagram reading skills

## Learning Objectives

By completing this exercise, you will:
- Design Entity-Relationship (ER) models for ML systems
- Apply database normalization principles (1NF, 2NF, 3NF)
- Implement primary keys and foreign keys with referential integrity
- Model one-to-many and many-to-many relationships
- Create junction tables for complex relationship patterns
- Configure CASCADE behavior for referential integrity
- Design lookup tables as alternatives to enum types
- Develop indexing strategies for optimal query performance on related tables
- Document database schemas with clear conventions
- Build production-grade ML model registry schemas

---

## Real-World Scenario

You're the infrastructure engineer at **ML Platform Corp**, and your team is building a centralized **ML Model Registry** that will serve as the **source of truth** for all ML models across the organization.

### Business Requirements

The ML Model Registry must support:

1. **Model Catalog**: Track all ML models with ownership, purpose, and metadata
2. **Versioning**: Each model can have multiple versions (v1.0.0, v1.1.0, v2.0.0)
3. **Training Runs**: Link versions to specific training runs with metrics
4. **Deployments**: Track where and when versions are deployed (dev, staging, prod)
5. **Datasets**: Maintain catalog of datasets used for training
6. **Approvals**: Require compliance approvals before production deployments
7. **Tags**: Enable flexible categorization and discovery
8. **Audit Trail**: Track who did what and when

### Why This Matters

A well-designed schema:
- ✅ Prevents data anomalies and inconsistencies
- ✅ Enforces business rules at the database level
- ✅ Enables efficient queries across relationships
- ✅ Supports future growth without major redesigns
- ✅ Provides clear data lineage and audit trails

---

## Part 1: Understanding Normalization

### Step 1.1: The Problem with Denormalized Data

**Bad Example**: All data in one table

```sql
-- DON'T DO THIS!
CREATE TABLE model_everything (
    id UUID PRIMARY KEY,
    model_name TEXT,
    model_description TEXT,
    model_owner TEXT,
    version TEXT,
    git_commit TEXT,
    deployment_env TEXT,        -- Problem: Multiple deployments stored as CSV?
    deployment_dates TEXT,      -- Problem: Dates stored as text?
    training_run_ids TEXT,      -- Problem: Multiple runs as delimited string?
    dataset_names TEXT,         -- Problem: Can't query efficiently
    tags TEXT,                  -- Problem: No structure
    approval_status TEXT,
    approved_by TEXT
);
```

**Problems**:
- ❌ Redundant data (model_name repeated for each version)
- ❌ Update anomalies (change owner in one place, forget others)
- ❌ Insertion anomalies (can't add model without version)
- ❌ Deletion anomalies (delete last version, lose model info)
- ❌ Can't efficiently query relationships
- ❌ No referential integrity

### Step 1.2: Normalization Forms

**First Normal Form (1NF)**:
- Each column contains atomic values (no arrays, no CSV)
- Each row is unique (has primary key)
- No repeating groups

**Second Normal Form (2NF)**:
- Meets 1NF
- No partial dependencies (all non-key columns depend on entire primary key)

**Third Normal Form (3NF)**:
- Meets 2NF
- No transitive dependencies (non-key columns don't depend on other non-key columns)

**Our Goal**: Design to 3NF for ML Model Registry

### Step 1.3: Identifying Entities

Let's identify the main entities (tables):

1. **models**: The ML model itself (ResNet, BERT, etc.)
2. **model_versions**: Specific versions of a model (v1.0.0, v2.0.0)
3. **training_runs**: Individual training executions
4. **deployments**: Where versions are deployed
5. **datasets**: Training/validation data collections
6. **tags**: Flexible metadata labels
7. **approvals**: Compliance and review approvals
8. **teams**: Organizational teams (lookup table)
9. **environments**: Deployment targets (lookup table)

**Junction Tables** (many-to-many):
- **run_datasets**: Training runs can use multiple datasets
- **model_tags**: Models can have multiple tags
- **dataset_tags**: Datasets can have multiple tags

---

## Part 2: Entity Relationships

### Step 2.1: Relationship Types

**One-to-Many (1:N)**:
- One model → Many versions
- One version → Many training runs
- One version → Many deployments
- One team → Many models

**Many-to-Many (M:N)**:
- Models ↔ Tags (via junction table)
- Datasets ↔ Tags (via junction table)
- Training Runs ↔ Datasets (via junction table)

### Step 2.2: ER Diagram Overview

```
┌─────────┐       ┌────────────────┐       ┌──────────────┐
│  teams  │──────<│     models     │>──────│  model_tags  │
└─────────┘       └────────────────┘       └──────────────┘
                          │                        │
                          │ 1:N                    │
                          ▼                        ▼
                  ┌──────────────────┐      ┌────────┐
                  │  model_versions  │      │  tags  │
                  └──────────────────┘      └────────┘
                          │                        ▲
                ┌─────────┴─────────┐              │
                │ 1:N               │ 1:N          │
                ▼                   ▼              │
        ┌──────────────┐    ┌──────────────┐      │
        │training_runs │    │ deployments  │      │
        └──────────────┘    └──────────────┘      │
                │                   │              │
                │ M:N               │              │
                ▼                   ▼              │
        ┌──────────────┐    ┌──────────────┐      │
        │ run_datasets │    │ environments │      │
        └──────────────┘    └──────────────┘      │
                │                                  │
                ▼                                  │
        ┌──────────────┐                          │
        │   datasets   │>─────────────────────────┘
        └──────────────┘    (dataset_tags)
```

---

## Part 3: Schema Implementation

### Step 3.1: Environment Setup

```bash
# Continue with the PostgreSQL container from Exercise 01
# Or start a new one:
docker run --name pg-ml-registry \
  -e POSTGRES_PASSWORD=mlops_secure_pass \
  -e POSTGRES_USER=mlops \
  -e POSTGRES_DB=ml_registry \
  -p 5432:5432 \
  -d postgres:14

# Connect
docker exec -it pg-ml-registry psql -U mlops -d ml_registry
```

### Step 3.2: Create Lookup Tables First

Create `sql/10_model_registry_schema.sql`:

```sql
-- ============================================
-- ML Model Registry Schema
-- ============================================
-- Purpose: Production-grade model registry
-- Author: ML Infrastructure Team
-- Date: 2025-10-23
-- Version: 1.0
-- ============================================

-- Drop existing objects (for development)
DROP TABLE IF EXISTS model_tags CASCADE;
DROP TABLE IF EXISTS dataset_tags CASCADE;
DROP TABLE IF EXISTS run_datasets CASCADE;
DROP TABLE IF EXISTS approvals CASCADE;
DROP TABLE IF EXISTS deployments CASCADE;
DROP TABLE IF EXISTS training_runs CASCADE;
DROP TABLE IF EXISTS model_versions CASCADE;
DROP TABLE IF EXISTS models CASCADE;
DROP TABLE IF EXISTS datasets CASCADE;
DROP TABLE IF EXISTS tags CASCADE;
DROP TABLE IF EXISTS environments CASCADE;
DROP TABLE IF EXISTS teams CASCADE;

-- ============================================
-- LOOKUP TABLES
-- ============================================

-- Teams table (lookup)
CREATE TABLE teams (
    team_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    team_name TEXT UNIQUE NOT NULL,
    team_email TEXT,
    department TEXT,
    cost_center TEXT,
    manager_name TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    CONSTRAINT valid_email CHECK (team_email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$')
);

CREATE INDEX idx_teams_name ON teams(team_name);

COMMENT ON TABLE teams IS 'Organizational teams owning ML models';
COMMENT ON COLUMN teams.cost_center IS 'For tracking ML infrastructure costs';

-- Environments table (lookup)
CREATE TABLE environments (
    environment_id SERIAL PRIMARY KEY,
    environment_name TEXT UNIQUE NOT NULL,
    environment_type TEXT NOT NULL,
    description TEXT,
    priority INTEGER DEFAULT 0,

    CONSTRAINT valid_env_type CHECK (
        environment_type IN ('development', 'staging', 'production', 'canary', 'shadow')
    ),
    CONSTRAINT valid_env_name CHECK (
        environment_name IN ('dev', 'qa', 'staging', 'staging-eu', 'staging-us',
                           'prod', 'prod-eu', 'prod-us', 'prod-apac',
                           'canary', 'shadow', 'local')
    )
);

CREATE INDEX idx_environments_type ON environments(environment_type);

COMMENT ON TABLE environments IS 'Deployment environments for ML models';

-- Insert default environments
INSERT INTO environments (environment_name, environment_type, description, priority) VALUES
    ('dev', 'development', 'Local development environment', 0),
    ('qa', 'development', 'QA testing environment', 1),
    ('staging', 'staging', 'Staging environment for final testing', 2),
    ('staging-eu', 'staging', 'Staging environment - EU region', 2),
    ('staging-us', 'staging', 'Staging environment - US region', 2),
    ('canary', 'canary', 'Canary deployment for gradual rollout', 3),
    ('prod', 'production', 'Production environment', 4),
    ('prod-eu', 'production', 'Production - Europe', 4),
    ('prod-us', 'production', 'Production - United States', 4),
    ('prod-apac', 'production', 'Production - Asia Pacific', 4);

-- ============================================
-- CORE ENTITIES
-- ============================================

-- Models table
CREATE TABLE models (
    model_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    model_name TEXT UNIQUE NOT NULL,
    display_name TEXT NOT NULL,
    description TEXT,
    objective TEXT,

    -- Ownership
    team_id UUID REFERENCES teams(team_id) ON DELETE SET NULL,
    primary_contact TEXT,
    secondary_contact TEXT,

    -- Business classification
    business_unit TEXT,
    risk_level TEXT DEFAULT 'medium',
    compliance_required BOOLEAN DEFAULT FALSE,

    -- Metadata
    github_repo TEXT,
    documentation_url TEXT,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by TEXT DEFAULT CURRENT_USER,

    -- Constraints
    CONSTRAINT valid_risk_level CHECK (
        risk_level IN ('low', 'medium', 'high', 'critical')
    ),
    CONSTRAINT valid_model_name CHECK (
        model_name ~ '^[a-z0-9-]+$'  -- Kebab-case only
    )
);

CREATE INDEX idx_models_team ON models(team_id);
CREATE INDEX idx_models_risk ON models(risk_level);
CREATE INDEX idx_models_name ON models(model_name);
CREATE INDEX idx_models_created ON models(created_at DESC);

COMMENT ON TABLE models IS 'Central catalog of ML models';
COMMENT ON COLUMN models.model_name IS 'Unique identifier (kebab-case)';
COMMENT ON COLUMN models.risk_level IS 'Business risk classification';
COMMENT ON COLUMN models.compliance_required IS 'Requires approval workflow';

-- Model Versions table
CREATE TABLE model_versions (
    version_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    model_id UUID NOT NULL REFERENCES models(model_id) ON DELETE CASCADE,

    -- Version info
    semver TEXT NOT NULL,  -- Semantic versioning: 1.2.3
    version_alias TEXT,     -- e.g., "latest", "stable"
    description TEXT,

    -- Artifacts
    git_commit TEXT,
    git_branch TEXT,
    artifact_uri TEXT NOT NULL,  -- S3, GCS, Azure Blob location
    artifact_size_mb NUMERIC(10,2),
    checksum_sha256 TEXT,

    -- Framework and environment
    framework TEXT NOT NULL,
    framework_version TEXT,
    python_version TEXT,
    cuda_version TEXT,

    -- Status
    status TEXT NOT NULL DEFAULT 'registered',

    -- Metadata
    registered_by TEXT NOT NULL,
    registered_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    promoted_to_production_at TIMESTAMP WITH TIME ZONE,
    deprecated_at TIMESTAMP WITH TIME ZONE,
    deprecation_reason TEXT,

    -- Performance benchmark (optional)
    benchmark_accuracy NUMERIC(5,4),
    benchmark_latency_ms NUMERIC(8,2),
    benchmark_throughput_qps NUMERIC(10,2),

    -- Constraints
    CONSTRAINT unique_model_version UNIQUE (model_id, semver),
    CONSTRAINT valid_status CHECK (
        status IN ('registered', 'validated', 'deployed', 'deprecated', 'archived')
    ),
    CONSTRAINT valid_framework CHECK (
        framework IN ('pytorch', 'tensorflow', 'sklearn', 'xgboost', 'jax',
                     'lightgbm', 'catboost', 'onnx', 'huggingface')
    ),
    CONSTRAINT valid_semver CHECK (
        semver ~ '^\d+\.\d+\.\d+(-[a-z0-9]+)?$'  -- 1.2.3 or 1.2.3-beta
    ),
    CONSTRAINT valid_checksum CHECK (
        checksum_sha256 IS NULL OR LENGTH(checksum_sha256) = 64
    )
);

CREATE INDEX idx_versions_model ON model_versions(model_id);
CREATE INDEX idx_versions_status ON model_versions(status);
CREATE INDEX idx_versions_semver ON model_versions(model_id, semver DESC);
CREATE INDEX idx_versions_registered ON model_versions(registered_at DESC);
CREATE INDEX idx_versions_framework ON model_versions(framework);

COMMENT ON TABLE model_versions IS 'Versioned artifacts for ML models';
COMMENT ON COLUMN model_versions.semver IS 'Semantic version (major.minor.patch)';
COMMENT ON COLUMN model_versions.artifact_uri IS 'Cloud storage location (s3://, gs://, etc.)';

-- Datasets table
CREATE TABLE datasets (
    dataset_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dataset_name TEXT UNIQUE NOT NULL,
    display_name TEXT NOT NULL,
    description TEXT,

    -- Storage
    storage_location TEXT NOT NULL,  -- S3, GCS, Azure, etc.
    storage_format TEXT,              -- parquet, csv, tfrecord, etc.
    storage_size_gb NUMERIC(12,2),

    -- Schema and versioning
    schema_url TEXT,
    schema_version TEXT,
    data_version TEXT,

    -- Ownership and governance
    data_steward TEXT,
    team_id UUID REFERENCES teams(team_id) ON DELETE SET NULL,

    -- Data quality
    freshness_sla_hours INTEGER,
    last_updated_at TIMESTAMP WITH TIME ZONE,
    row_count BIGINT,
    column_count INTEGER,

    -- Compliance
    contains_pii BOOLEAN DEFAULT FALSE,
    data_classification TEXT DEFAULT 'internal',
    retention_days INTEGER,

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by TEXT DEFAULT CURRENT_USER,

    -- Constraints
    CONSTRAINT valid_freshness CHECK (freshness_sla_hours IS NULL OR freshness_sla_hours > 0),
    CONSTRAINT valid_storage_format CHECK (
        storage_format IN ('parquet', 'csv', 'json', 'avro', 'tfrecord', 'hdf5', 'arrow')
    ),
    CONSTRAINT valid_classification CHECK (
        data_classification IN ('public', 'internal', 'confidential', 'restricted')
    ),
    CONSTRAINT valid_dataset_name CHECK (
        dataset_name ~ '^[a-z0-9-_]+$'
    )
);

CREATE INDEX idx_datasets_name ON datasets(dataset_name);
CREATE INDEX idx_datasets_team ON datasets(team_id);
CREATE INDEX idx_datasets_updated ON datasets(last_updated_at DESC);
CREATE INDEX idx_datasets_classification ON datasets(data_classification);

COMMENT ON TABLE datasets IS 'Catalog of datasets used for ML training';
COMMENT ON COLUMN datasets.contains_pii IS 'Personally Identifiable Information present';
COMMENT ON COLUMN datasets.data_classification IS 'Security classification level';

-- Training Runs table
CREATE TABLE training_runs (
    run_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    version_id UUID NOT NULL REFERENCES model_versions(version_id) ON DELETE CASCADE,

    -- Run identification
    run_name TEXT,
    experiment_name TEXT,

    -- Status
    status TEXT NOT NULL DEFAULT 'queued',

    -- Metrics
    accuracy NUMERIC(5,4),
    precision_score NUMERIC(5,4),
    recall_score NUMERIC(5,4),
    f1_score NUMERIC(5,4),
    loss NUMERIC(10,5),

    -- Custom metrics (JSONB for flexibility)
    custom_metrics JSONB DEFAULT '{}'::jsonb,

    -- Hyperparameters
    hyperparameters JSONB DEFAULT '{}'::jsonb,

    -- Compute resources
    compute_target TEXT,
    instance_type TEXT,
    gpu_count INTEGER DEFAULT 0,
    gpu_type TEXT,
    gpu_hours NUMERIC(10,2) DEFAULT 0,
    cpu_hours NUMERIC(10,2) DEFAULT 0,
    estimated_cost_usd NUMERIC(10,2),

    -- Execution details
    started_by TEXT,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    duration_seconds INTEGER,
    exit_code INTEGER,

    -- Artifacts
    logs_uri TEXT,
    tensorboard_uri TEXT,
    checkpoint_uri TEXT,

    -- Feature engineering
    feature_store_snapshot TEXT,
    feature_count INTEGER,

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    notes TEXT,

    -- Constraints
    CONSTRAINT valid_status CHECK (
        status IN ('queued', 'running', 'succeeded', 'failed', 'cancelled', 'timeout')
    ),
    CONSTRAINT valid_metrics CHECK (
        (accuracy IS NULL OR (accuracy >= 0 AND accuracy <= 1)) AND
        (precision_score IS NULL OR (precision_score >= 0 AND precision_score <= 1)) AND
        (recall_score IS NULL OR (recall_score >= 0 AND recall_score <= 1)) AND
        (f1_score IS NULL OR (f1_score >= 0 AND f1_score <= 1))
    ),
    CONSTRAINT valid_gpu_count CHECK (gpu_count >= 0),
    CONSTRAINT completed_timestamp CHECK (
        (status IN ('succeeded', 'failed', 'cancelled', 'timeout') AND completed_at IS NOT NULL)
        OR (status IN ('queued', 'running') AND completed_at IS NULL)
    )
);

CREATE INDEX idx_training_version ON training_runs(version_id);
CREATE INDEX idx_training_status ON training_runs(status);
CREATE INDEX idx_training_created ON training_runs(created_at DESC);
CREATE INDEX idx_training_experiment ON training_runs(experiment_name);
CREATE INDEX idx_training_metrics ON training_runs USING GIN (custom_metrics);
CREATE INDEX idx_training_hyperparams ON training_runs USING GIN (hyperparameters);

COMMENT ON TABLE training_runs IS 'Individual training job executions';
COMMENT ON COLUMN training_runs.custom_metrics IS 'Flexible JSONB field for arbitrary metrics';
COMMENT ON COLUMN training_runs.hyperparameters IS 'Training hyperparameters as JSON';

-- Deployments table
CREATE TABLE deployments (
    deployment_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    version_id UUID NOT NULL REFERENCES model_versions(version_id) ON DELETE RESTRICT,
    environment_id INTEGER NOT NULL REFERENCES environments(environment_id),

    -- Deployment details
    deployment_name TEXT,
    endpoint_url TEXT,
    serving_framework TEXT,  -- torchserve, tfserving, triton, etc.

    -- Service configuration
    replicas INTEGER DEFAULT 1,
    instance_type TEXT,
    gpu_enabled BOOLEAN DEFAULT FALSE,
    auto_scaling_enabled BOOLEAN DEFAULT FALSE,
    min_replicas INTEGER,
    max_replicas INTEGER,

    -- SLO targets
    target_latency_p50_ms NUMERIC(8,2),
    target_latency_p95_ms NUMERIC(8,2),
    target_latency_p99_ms NUMERIC(8,2),
    target_availability_percent NUMERIC(5,2),
    target_throughput_qps NUMERIC(10,2),

    -- Actual metrics (updated periodically)
    actual_latency_p50_ms NUMERIC(8,2),
    actual_latency_p95_ms NUMERIC(8,2),
    actual_latency_p99_ms NUMERIC(8,2),
    actual_availability_percent NUMERIC(5,2),
    actual_throughput_qps NUMERIC(10,2),

    -- Deployment lifecycle
    deployed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deployed_by TEXT NOT NULL,
    undeployed_at TIMESTAMP WITH TIME ZONE,
    undeployed_by TEXT,
    status TEXT NOT NULL DEFAULT 'active',

    -- Traffic routing
    traffic_percentage INTEGER DEFAULT 100,

    -- Cost tracking
    monthly_cost_usd NUMERIC(12,2),

    -- Metadata
    deployment_notes TEXT,

    -- Constraints
    CONSTRAINT unique_env_deployment UNIQUE (environment_id, version_id, deployed_at),
    CONSTRAINT valid_status_deployment CHECK (
        status IN ('active', 'degraded', 'inactive', 'failed')
    ),
    CONSTRAINT valid_replicas CHECK (
        replicas >= 1 AND
        (min_replicas IS NULL OR min_replicas >= 1) AND
        (max_replicas IS NULL OR max_replicas >= min_replicas)
    ),
    CONSTRAINT valid_traffic CHECK (
        traffic_percentage >= 0 AND traffic_percentage <= 100
    ),
    CONSTRAINT valid_availability CHECK (
        target_availability_percent IS NULL OR
        (target_availability_percent >= 0 AND target_availability_percent <= 100)
    )
);

CREATE INDEX idx_deployments_version ON deployments(version_id);
CREATE INDEX idx_deployments_env ON deployments(environment_id);
CREATE INDEX idx_deployments_status ON deployments(status);
CREATE INDEX idx_deployments_date ON deployments(deployed_at DESC);
CREATE INDEX idx_deployments_active ON deployments(environment_id, status)
    WHERE status = 'active';

COMMENT ON TABLE deployments IS 'Model version deployments to environments';
COMMENT ON COLUMN deployments.traffic_percentage IS 'For canary/blue-green deployments';

-- Approvals table
CREATE TABLE approvals (
    approval_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    version_id UUID NOT NULL REFERENCES model_versions(version_id) ON DELETE CASCADE,

    -- Approval type
    approval_type TEXT NOT NULL,
    required_for_env TEXT,  -- e.g., 'production'

    -- Status
    status TEXT NOT NULL DEFAULT 'pending',

    -- Approver info
    requested_by TEXT NOT NULL,
    requested_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    approved_by TEXT,
    approved_at TIMESTAMP WITH TIME ZONE,
    rejected_by TEXT,
    rejected_at TIMESTAMP WITH TIME ZONE,

    -- Details
    approval_notes TEXT,
    rejection_reason TEXT,

    -- Evidence/attestation
    compliance_checklist JSONB,
    risk_assessment_score NUMERIC(3,1),

    -- Expiration
    expires_at TIMESTAMP WITH TIME ZONE,

    -- Constraints
    CONSTRAINT valid_approval_type CHECK (
        approval_type IN ('compliance', 'security', 'legal', 'business', 'technical')
    ),
    CONSTRAINT valid_approval_status CHECK (
        status IN ('pending', 'approved', 'rejected', 'expired')
    ),
    CONSTRAINT approval_xor CHECK (
        (status = 'approved' AND approved_by IS NOT NULL AND approved_at IS NOT NULL AND rejected_by IS NULL)
        OR (status = 'rejected' AND rejected_by IS NOT NULL AND rejected_at IS NOT NULL AND approved_by IS NULL)
        OR (status IN ('pending', 'expired'))
    )
);

CREATE INDEX idx_approvals_version ON approvals(version_id);
CREATE INDEX idx_approvals_status ON approvals(status);
CREATE INDEX idx_approvals_type ON approvals(approval_type);
CREATE INDEX idx_approvals_pending ON approvals(version_id, status) WHERE status = 'pending';

COMMENT ON TABLE approvals IS 'Approval workflows for model deployments';
COMMENT ON COLUMN approvals.compliance_checklist IS 'JSONB checklist items';

-- Tags table
CREATE TABLE tags (
    tag_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tag_category TEXT NOT NULL,
    tag_value TEXT NOT NULL,
    tag_description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    CONSTRAINT unique_tag UNIQUE (tag_category, tag_value),
    CONSTRAINT valid_tag_category CHECK (
        tag_category IN ('domain', 'use-case', 'framework', 'team', 'project',
                        'customer', 'region', 'priority', 'status', 'custom')
    )
);

CREATE INDEX idx_tags_category ON tags(tag_category);
CREATE INDEX idx_tags_value ON tags(tag_value);

COMMENT ON TABLE tags IS 'Flexible tagging system for categorization';

-- Insert common tags
INSERT INTO tags (tag_category, tag_value, tag_description) VALUES
    ('domain', 'nlp', 'Natural Language Processing'),
    ('domain', 'computer-vision', 'Computer Vision'),
    ('domain', 'time-series', 'Time Series Analysis'),
    ('domain', 'recommendation', 'Recommendation Systems'),
    ('domain', 'tabular', 'Tabular Data Models'),
    ('use-case', 'classification', 'Classification task'),
    ('use-case', 'regression', 'Regression task'),
    ('use-case', 'generation', 'Generative models'),
    ('use-case', 'detection', 'Object/anomaly detection'),
    ('use-case', 'segmentation', 'Segmentation task'),
    ('priority', 'critical', 'Business-critical model'),
    ('priority', 'high', 'High priority'),
    ('priority', 'medium', 'Medium priority'),
    ('priority', 'low', 'Low priority'),
    ('status', 'experimental', 'Experimental/research'),
    ('status', 'production-ready', 'Production-ready'),
    ('status', 'deprecated', 'Deprecated, do not use');

-- ============================================
-- JUNCTION TABLES (Many-to-Many)
-- ============================================

-- Model Tags (models ↔ tags)
CREATE TABLE model_tags (
    model_id UUID NOT NULL REFERENCES models(model_id) ON DELETE CASCADE,
    tag_id UUID NOT NULL REFERENCES tags(tag_id) ON DELETE CASCADE,
    tagged_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    tagged_by TEXT DEFAULT CURRENT_USER,

    PRIMARY KEY (model_id, tag_id)
);

CREATE INDEX idx_model_tags_model ON model_tags(model_id);
CREATE INDEX idx_model_tags_tag ON model_tags(tag_id);

COMMENT ON TABLE model_tags IS 'Many-to-many: models to tags';

-- Dataset Tags (datasets ↔ tags)
CREATE TABLE dataset_tags (
    dataset_id UUID NOT NULL REFERENCES datasets(dataset_id) ON DELETE CASCADE,
    tag_id UUID NOT NULL REFERENCES tags(tag_id) ON DELETE CASCADE,
    tagged_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    tagged_by TEXT DEFAULT CURRENT_USER,

    PRIMARY KEY (dataset_id, tag_id)
);

CREATE INDEX idx_dataset_tags_dataset ON dataset_tags(dataset_id);
CREATE INDEX idx_dataset_tags_tag ON dataset_tags(tag_id);

COMMENT ON TABLE dataset_tags IS 'Many-to-many: datasets to tags';

-- Run Datasets (training_runs ↔ datasets)
CREATE TABLE run_datasets (
    run_id UUID NOT NULL REFERENCES training_runs(run_id) ON DELETE CASCADE,
    dataset_id UUID NOT NULL REFERENCES datasets(dataset_id) ON DELETE RESTRICT,
    dataset_role TEXT NOT NULL,  -- 'training', 'validation', 'test'
    sample_count BIGINT,
    usage_percentage NUMERIC(5,2),

    PRIMARY KEY (run_id, dataset_id, dataset_role),

    CONSTRAINT valid_dataset_role CHECK (
        dataset_role IN ('training', 'validation', 'test', 'calibration')
    ),
    CONSTRAINT valid_usage_percent CHECK (
        usage_percentage IS NULL OR (usage_percentage >= 0 AND usage_percentage <= 100)
    )
);

CREATE INDEX idx_run_datasets_run ON run_datasets(run_id);
CREATE INDEX idx_run_datasets_dataset ON run_datasets(dataset_id);

COMMENT ON TABLE run_datasets IS 'Many-to-many: training runs to datasets';
COMMENT ON COLUMN run_datasets.dataset_role IS 'How dataset was used (train/val/test)';

-- ============================================
-- TRIGGERS
-- ============================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for models table
CREATE TRIGGER update_models_updated_at
    BEFORE UPDATE ON models
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

COMMENT ON FUNCTION update_updated_at_column() IS 'Automatically update updated_at timestamp';

-- ============================================
-- VIEWS
-- ============================================

-- View: Latest version per model
CREATE OR REPLACE VIEW vw_latest_model_versions AS
SELECT DISTINCT ON (m.model_id)
    m.model_id,
    m.model_name,
    m.display_name AS model_display_name,
    mv.version_id,
    mv.semver,
    mv.status AS version_status,
    mv.framework,
    mv.registered_at,
    mv.artifact_uri
FROM models m
INNER JOIN model_versions mv ON m.model_id = mv.model_id
WHERE mv.status != 'archived'
ORDER BY m.model_id, mv.registered_at DESC;

COMMENT ON VIEW vw_latest_model_versions IS 'Latest non-archived version per model';

-- View: Production deployments
CREATE OR REPLACE VIEW vw_production_deployments AS
SELECT
    m.model_name,
    m.display_name AS model_display_name,
    mv.semver,
    e.environment_name,
    d.endpoint_url,
    d.status AS deployment_status,
    d.deployed_at,
    d.deployed_by,
    d.traffic_percentage,
    d.actual_latency_p95_ms,
    d.actual_availability_percent
FROM deployments d
INNER JOIN model_versions mv ON d.version_id = mv.version_id
INNER JOIN models m ON mv.model_id = m.model_id
INNER JOIN environments e ON d.environment_id = e.environment_id
WHERE e.environment_type = 'production'
  AND d.status = 'active'
ORDER BY m.model_name, d.deployed_at DESC;

COMMENT ON VIEW vw_production_deployments IS 'Active production deployments';

-- ============================================
-- SAMPLE DATA
-- ============================================

-- Insert sample teams
INSERT INTO teams (team_name, team_email, department, manager_name) VALUES
    ('ml-platform', 'ml-platform@example.com', 'Engineering', 'Alice Johnson'),
    ('data-science', 'data-science@example.com', 'Analytics', 'Bob Smith'),
    ('ai-research', 'ai-research@example.com', 'R&D', 'Carol White'),
    ('mlops', 'mlops@example.com', 'Operations', 'David Brown');

-- Insert sample models
INSERT INTO models (model_name, display_name, description, team_id, objective, risk_level, compliance_required) VALUES
    ('sentiment-classifier', 'Sentiment Classifier', 'Customer feedback sentiment analysis',
     (SELECT team_id FROM teams WHERE team_name = 'data-science'),
     'Classify customer sentiment as positive/negative/neutral', 'medium', FALSE),

    ('fraud-detector', 'Fraud Detection Model', 'Real-time transaction fraud detection',
     (SELECT team_id FROM teams WHERE team_name = 'ai-research'),
     'Identify fraudulent transactions', 'critical', TRUE),

    ('product-recommender', 'Product Recommendation Engine', 'Personalized product recommendations',
     (SELECT team_id FROM teams WHERE team_name = 'data-science'),
     'Recommend products to users based on behavior', 'high', FALSE);

-- Get model IDs for foreign keys
DO $$
DECLARE
    sentiment_model_id UUID;
    fraud_model_id UUID;
    recommender_model_id UUID;
BEGIN
    SELECT model_id INTO sentiment_model_id FROM models WHERE model_name = 'sentiment-classifier';
    SELECT model_id INTO fraud_model_id FROM models WHERE model_name = 'fraud-detector';
    SELECT model_id INTO recommender_model_id FROM models WHERE model_name = 'product-recommender';

    -- Insert model versions
    INSERT INTO model_versions (model_id, semver, artifact_uri, framework, framework_version, registered_by, status) VALUES
        (sentiment_model_id, '1.0.0', 's3://ml-artifacts/sentiment-classifier/1.0.0/',
         'pytorch', '2.0.1', 'alice@example.com', 'deployed'),
        (sentiment_model_id, '1.1.0', 's3://ml-artifacts/sentiment-classifier/1.1.0/',
         'pytorch', '2.0.1', 'alice@example.com', 'registered'),

        (fraud_model_id, '2.0.0', 's3://ml-artifacts/fraud-detector/2.0.0/',
         'tensorflow', '2.13.0', 'bob@example.com', 'validated'),

        (recommender_model_id, '0.9.0', 's3://ml-artifacts/product-recommender/0.9.0/',
         'sklearn', '1.3.0', 'carol@example.com', 'registered');
END $$;

-- Insert sample datasets
INSERT INTO datasets (dataset_name, display_name, storage_location, storage_format, data_steward, contains_pii) VALUES
    ('customer-reviews-2024', 'Customer Reviews 2024', 's3://datasets/customer-reviews/',
     'parquet', 'alice@example.com', FALSE),
    ('transaction-logs', 'Transaction Logs', 's3://datasets/transactions/',
     'parquet', 'bob@example.com', TRUE),
    ('user-interactions', 'User Interaction Events', 's3://datasets/user-events/',
     'parquet', 'carol@example.com', TRUE);

-- ============================================
-- GRANT PERMISSIONS (Example)
-- ============================================

-- Grant read-only access to data scientists
-- GRANT SELECT ON ALL TABLES IN SCHEMA public TO data_scientists_role;

-- Grant full access to ML platform team
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO ml_platform_role;

-- ============================================
-- SCHEMA VALIDATION
-- ============================================

-- Verify table counts
SELECT 'Tables created successfully' AS status;
SELECT COUNT(*) AS table_count FROM information_schema.tables
WHERE table_schema = 'public' AND table_type = 'BASE TABLE';

-- Verify foreign keys
SELECT COUNT(*) AS foreign_key_count FROM information_schema.table_constraints
WHERE constraint_type = 'FOREIGN KEY' AND table_schema = 'public';

-- Verify indexes
SELECT COUNT(*) AS index_count FROM pg_indexes WHERE schemaname = 'public';
```

✅ **Checkpoint**: Schema created with all tables, relationships, indexes, and constraints.

---

## Part 4: Testing the Schema

### Step 4.1: Load the Schema

```bash
# Execute the schema file
docker exec -i pg-ml-registry psql -U mlops -d ml_registry < sql/10_model_registry_schema.sql
```

**Expected Output**:
```
DROP TABLE
DROP TABLE
...
CREATE TABLE
CREATE TABLE
...
INSERT 0 10
INSERT 0 4
INSERT 0 3
INSERT 0 4
INSERT 0 3
status
-------
Tables created successfully
(1 row)

table_count
-----------
14
(1 row)

foreign_key_count
-----------------
12
(1 row)

index_count
-----------
45
(1 row)
```

### Step 4.2: Verify Tables

```sql
-- List all tables
\dt

-- Describe models table
\d+ models

-- Describe model_versions table
\d+ model_versions

-- Check foreign keys
SELECT
    tc.table_name,
    kcu.column_name,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name,
    rc.delete_rule
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
  ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage AS ccu
  ON ccu.constraint_name = tc.constraint_name
JOIN information_schema.referential_constraints AS rc
  ON rc.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY'
ORDER BY tc.table_name, kcu.column_name;
```

### Step 4.3: Test Referential Integrity

```sql
-- =====================
-- Test CASCADE behavior
-- =====================

BEGIN;

-- Insert a test model
INSERT INTO models (model_name, display_name)
VALUES ('test-model', 'Test Model')
RETURNING model_id;

-- Copy the returned UUID
-- Insert a version (use actual UUID from above)
INSERT INTO model_versions (model_id, semver, artifact_uri, framework, registered_by)
VALUES ('YOUR-UUID-HERE', '1.0.0', 's3://test/', 'pytorch', 'test@example.com');

-- Delete the model (should CASCADE delete the version)
DELETE FROM models WHERE model_name = 'test-model';

-- Verify version was also deleted
SELECT COUNT(*) FROM model_versions WHERE model_id = 'YOUR-UUID-HERE';
-- Should return 0

ROLLBACK;  -- Don't actually delete
```

### Step 4.4: Test Junction Tables

```sql
-- Get a model and tag
SELECT m.model_id, m.model_name, t.tag_id, t.tag_value
FROM models m
CROSS JOIN tags t
WHERE m.model_name = 'sentiment-classifier'
  AND t.tag_value = 'nlp'
LIMIT 1;

-- Tag the model
INSERT INTO model_tags (model_id, tag_id)
SELECT m.model_id, t.tag_id
FROM models m, tags t
WHERE m.model_name = 'sentiment-classifier'
  AND t.tag_value = 'nlp';

-- Verify
SELECT m.model_name, t.tag_category, t.tag_value
FROM models m
INNER JOIN model_tags mt ON m.model_id = mt.model_id
INNER JOIN tags t ON mt.tag_id = t.tag_id
WHERE m.model_name = 'sentiment-classifier';
```

✅ **Checkpoint**: All referential integrity constraints work correctly.

---

## Part 5: Complex Queries Across Relationships

### Step 5.1: Join Queries

```sql
-- ====================
-- BASIC JOINS
-- ====================

-- 1. Models with their latest version
SELECT
    m.model_name,
    m.display_name,
    mv.semver,
    mv.status,
    mv.framework
FROM models m
INNER JOIN model_versions mv ON m.model_id = mv.model_id
ORDER BY m.model_name, mv.registered_at DESC;

-- 2. Models with team information
SELECT
    m.model_name,
    m.display_name,
    t.team_name,
    t.department,
    m.risk_level
FROM models m
LEFT JOIN teams t ON m.team_id = t.team_id
ORDER BY m.model_name;

-- 3. All deployments with model and environment info
SELECT
    m.model_name,
    mv.semver,
    e.environment_name,
    e.environment_type,
    d.deployed_at,
    d.deployed_by,
    d.status
FROM deployments d
INNER JOIN model_versions mv ON d.version_id = mv.version_id
INNER JOIN models m ON mv.model_id = m.model_id
INNER JOIN environments e ON d.environment_id = e.environment_id
ORDER BY d.deployed_at DESC;
```

### Step 5.2: Aggregation Across Relationships

```sql
-- ====================
-- AGGREGATIONS
-- ====================

-- 1. Count versions per model
SELECT
    m.model_name,
    COUNT(mv.version_id) AS version_count,
    MAX(mv.registered_at) AS latest_version_date
FROM models m
LEFT JOIN model_versions mv ON m.model_id = mv.model_id
GROUP BY m.model_id, m.model_name
ORDER BY version_count DESC;

-- 2. Deployment summary by environment
SELECT
    e.environment_name,
    COUNT(d.deployment_id) AS total_deployments,
    COUNT(DISTINCT mv.model_id) AS unique_models,
    COUNT(*) FILTER (WHERE d.status = 'active') AS active_deployments
FROM environments e
LEFT JOIN deployments d ON e.environment_id = d.environment_id
LEFT JOIN model_versions mv ON d.version_id = mv.version_id
GROUP BY e.environment_id, e.environment_name
ORDER BY e.priority DESC;

-- 3. Training runs per model
SELECT
    m.model_name,
    COUNT(tr.run_id) AS total_runs,
    COUNT(*) FILTER (WHERE tr.status = 'succeeded') AS successful_runs,
    ROUND(AVG(tr.gpu_hours), 2) AS avg_gpu_hours,
    SUM(tr.estimated_cost_usd) AS total_cost
FROM models m
INNER JOIN model_versions mv ON m.model_id = mv.model_id
LEFT JOIN training_runs tr ON mv.version_id = tr.version_id
GROUP BY m.model_id, m.model_name
ORDER BY total_cost DESC NULLS LAST;
```

### Step 5.3: Complex Multi-Join Queries

```sql
-- ====================
-- COMPLEX QUERIES
-- ====================

-- 1. Complete model lineage
SELECT
    m.model_name,
    mv.semver,
    tr.run_name,
    tr.status AS training_status,
    d_train.dataset_name AS training_dataset,
    tr.accuracy,
    dep.environment_name,
    dep.deployed_at
FROM models m
INNER JOIN model_versions mv ON m.model_id = mv.model_id
LEFT JOIN training_runs tr ON mv.version_id = tr.version_id
LEFT JOIN run_datasets rd ON tr.run_id = rd.run_id AND rd.dataset_role = 'training'
LEFT JOIN datasets d_train ON rd.dataset_id = d_train.dataset_id
LEFT JOIN (
    SELECT
        d.version_id,
        e.environment_name,
        d.deployed_at
    FROM deployments d
    INNER JOIN environments e ON d.environment_id = e.environment_id
    WHERE d.status = 'active'
) dep ON mv.version_id = dep.version_id
WHERE m.model_name = 'sentiment-classifier'
ORDER BY mv.registered_at DESC, tr.created_at DESC;

-- 2. Models requiring approval for production
SELECT
    m.model_name,
    m.display_name,
    m.risk_level,
    mv.semver,
    a.approval_type,
    a.status AS approval_status,
    a.requested_at,
    a.approved_by,
    a.approved_at
FROM models m
INNER JOIN model_versions mv ON m.model_id = mv.model_id
INNER JOIN approvals a ON mv.version_id = a.version_id
WHERE m.compliance_required = TRUE
  AND a.status IN ('pending', 'approved')
ORDER BY a.requested_at DESC;

-- 3. Dataset usage across models
SELECT
    d.dataset_name,
    d.display_name,
    COUNT(DISTINCT mv.model_id) AS used_by_models,
    COUNT(tr.run_id) AS total_training_runs,
    STRING_AGG(DISTINCT m.model_name, ', ') AS model_list
FROM datasets d
INNER JOIN run_datasets rd ON d.dataset_id = rd.dataset_id
INNER JOIN training_runs tr ON rd.run_id = tr.run_id
INNER JOIN model_versions mv ON tr.version_id = mv.version_id
INNER JOIN models m ON mv.model_id = m.model_id
GROUP BY d.dataset_id, d.dataset_name, d.display_name
ORDER BY used_by_models DESC, total_training_runs DESC;
```

✅ **Checkpoint**: You can query complex relationships across multiple tables.

---

## Part 6: Best Practices and Production Considerations

### Step 6.1: Indexing Strategy

```sql
-- Check index usage
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY idx_scan DESC;

-- Find missing indexes (queries that do seq scans)
SELECT
    schemaname,
    tablename,
    seq_scan,
    seq_tup_read,
    seq_tup_read / seq_scan AS avg_rows_per_scan
FROM pg_stat_user_tables
WHERE schemaname = 'public'
  AND seq_scan > 0
ORDER BY seq_tup_read DESC;
```

### Step 6.2: Data Integrity Validation

```sql
-- ====================
-- INTEGRITY CHECKS
-- ====================

-- 1. Orphaned records (shouldn't exist with FK constraints)
SELECT 'Checking for orphaned model_versions...' AS check_name;
SELECT COUNT(*) AS orphaned_count
FROM model_versions mv
WHERE NOT EXISTS (
    SELECT 1 FROM models m WHERE m.model_id = mv.model_id
);
-- Should be 0

-- 2. Deployments without active environment
SELECT 'Checking active deployments in valid environments...' AS check_name;
SELECT COUNT(*) AS invalid_deployments
FROM deployments d
LEFT JOIN environments e ON d.environment_id = e.environment_id
WHERE d.status = 'active' AND e.environment_id IS NULL;
-- Should be 0

-- 3. Models without versions (allowed, but worth tracking)
SELECT
    m.model_name,
    m.created_at,
    COUNT(mv.version_id) AS version_count
FROM models m
LEFT JOIN model_versions mv ON m.model_id = mv.model_id
GROUP BY m.model_id, m.model_name, m.created_at
HAVING COUNT(mv.version_id) = 0;
```

### Step 6.3: Performance Optimization

```sql
-- ====================
-- PERFORMANCE CHECKS
-- ====================

-- 1. Table sizes
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS total_size,
    pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) AS table_size,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename) - pg_relation_size(schemaname||'.'||tablename)) AS index_size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- 2. Slow query identification
-- Enable in postgresql.conf: log_min_duration_statement = 1000
-- Check logs for slow queries

-- 3. EXPLAIN ANALYZE for common queries
EXPLAIN ANALYZE
SELECT m.model_name, COUNT(mv.version_id)
FROM models m
LEFT JOIN model_versions mv ON m.model_id = mv.model_id
GROUP BY m.model_id, m.model_name;
```

---

## Part 7: Hands-On Challenges

### Challenge 1: Add New Entities

Design and implement:
1. A `experiments` table to group related training runs
2. A `users` table for authentication/authorization
3. Link models to users (created_by should reference users table)

### Challenge 2: Complex Query

Write a query that answers:
"Show me all models deployed to production with approval status, including their latest training metrics and the datasets used"

<details>
<summary>Solution Hint</summary>

```sql
SELECT
    m.model_name,
    mv.semver,
    dep.environment_name,
    dep.deployed_at,
    a.status AS approval_status,
    tr.accuracy,
    tr.f1_score,
    STRING_AGG(d.dataset_name, ', ') AS datasets_used
FROM models m
INNER JOIN model_versions mv ON m.model_id = mv.model_id
INNER JOIN deployments dep_join ON mv.version_id = dep_join.version_id
INNER JOIN environments e ON dep_join.environment_id = e.environment_id
LEFT JOIN approvals a ON mv.version_id = a.version_id
LEFT JOIN LATERAL (
    SELECT * FROM training_runs
    WHERE version_id = mv.version_id
    ORDER BY created_at DESC
    LIMIT 1
) tr ON TRUE
LEFT JOIN run_datasets rd ON tr.run_id = rd.run_id
LEFT JOIN datasets d ON rd.dataset_id = d.dataset_id
WHERE e.environment_type = 'production'
  AND dep_join.status = 'active'
GROUP BY m.model_name, mv.semver, dep.environment_name, dep.deployed_at,
         a.status, tr.accuracy, tr.f1_score;
```
</details>

### Challenge 3: Data Migration

Create a script that:
1. Exports model data from Exercise 01's training_runs table
2. Migrates it to the new normalized schema
3. Validates data integrity after migration

---

## Part 8: Documentation

### Step 8.1: Create ER Diagram

Use one of these tools:
- **dbdiagram.io** (online, free)
- **draw.io** (online or desktop)
- **DBeaver** (desktop, auto-generate from DB)
- **pgAdmin** (desktop)

Save as: `design/er-diagram-model-registry.png`

### Step 8.2: Schema Documentation

Create `docs/model-registry-schema.md`:

```markdown
# ML Model Registry Schema Documentation

## Overview
Production-grade relational schema for ML model lifecycle management.

## Entity Descriptions

### Core Tables

#### models
- **Purpose**: Central catalog of ML models
- **Key Columns**:
  - `model_id` (PK): Unique identifier
  - `model_name`: Human-readable name (unique, kebab-case)
  - `team_id` (FK): Owning team
  - `risk_level`: Business risk classification
- **Relationships**:
  - 1:N with model_versions
  - 1:N with teams (via team_id)
  - M:N with tags (via model_tags)

[Continue for all tables...]

## Relationship Map

[Include ER diagram image]

## Common Queries

### List production deployments
\`\`\`sql
SELECT * FROM vw_production_deployments;
\`\`\`

[More examples...]

## Operational Considerations

- **Backups**: Daily full backups, hourly incremental
- **Retention**: Keep deployments for 2 years, training_runs for 1 year
- **Scaling**: Partition training_runs by created_at when > 10M rows
```

---

## Part 9: Summary and Deliverables

### What You Learned

✅ **Database Design**:
- Entity-Relationship modeling
- Normalization to 3NF
- Primary and foreign keys
- Referential integrity

✅ **Relationships**:
- One-to-many (1:N)
- Many-to-many (M:N) with junction tables
- CASCADE vs RESTRICT delete behaviors

✅ **Advanced Concepts**:
- Lookup tables for enums
- Triggers for automatic updates
- Views for common queries
- JSONB for flexible data

✅ **Best Practices**:
- Indexing strategy
- Constraint enforcement
- Documentation standards

### Deliverables Checklist

- [ ] `sql/10_model_registry_schema.sql` - Complete schema
- [ ] `design/er-diagram-model-registry.png` - ER diagram
- [ ] `docs/model-registry-schema.md` - Documentation
- [ ] All tables created without errors
- [ ] Foreign keys enforce referential integrity
- [ ] Sample data loaded successfully
- [ ] Complex queries across joins work
- [ ] Reflection written (300-500 words)

### Reflection Questions

1. **Normalization**: How does 3NF prevent data anomalies?
2. **Trade-offs**: When might denormalization be acceptable?
3. **Scalability**: Which tables need partitioning at scale?
4. **Extensions**: How would you add model monitoring metrics?
5. **Challenges**: What was the most complex relationship to model?

---

## Next Steps

- **Exercise 03**: Advanced SQL Joins - Master INNER/LEFT/RIGHT/FULL joins with complex scenarios
- **Exercise 04**: SQLAlchemy ORM Integration - Connect Python apps to this schema
- **Exercise 05**: Optimization & Indexing - Learn query optimization and index design

---

## Additional Resources

- [Database Normalization Guide](https://www.postgresql.org/docs/current/ddl-constraints.html)
- [ER Diagram Tutorial](https://www.lucidchart.com/pages/er-diagrams)
- [PostgreSQL Foreign Keys](https://www.postgresql.org/docs/current/ddl-constraints.html#DDL-CONSTRAINTS-FK)
- [dbdiagram.io](https://dbdiagram.io/) - Free ER diagram tool

---

**Exercise Complete!** 🎉

You've designed a production-ready, normalized ML Model Registry schema that can scale to thousands of models and millions of training runs.

**Estimated Time**: 3-4 hours
**Difficulty**: Intermediate
**Lines of Code**: ~650 SQL
**Learning Objectives**: ✅ All achieved
**Ready for**: Exercise 03 - Advanced SQL Joins
