# Exercise 01: SQL Fundamentals & CRUD Operations

## Exercise Overview

**Objective**: Master fundamental SQL operations by building a production-ready ML training metadata database. Learn to create schemas, insert data, and perform CRUD operations that power real ML infrastructure platforms.

**Difficulty**: Beginner
**Estimated Time**: 3-4 hours
**Prerequisites**:
- Lecture 01 (Database Fundamentals & SQL Basics)
- PostgreSQL installed locally or running via Docker
- Comfort with terminal and text editor
- Module 005 (Docker) for containerized PostgreSQL setup

## Learning Objectives

By completing this exercise, you will:
- Initialize and manage PostgreSQL databases for ML applications
- Design table schemas with appropriate constraints and data types
- Implement primary keys, foreign keys, and unique constraints
- Apply CHECK constraints for data validation rules
- Utilize JSONB data type for flexible metadata storage
- Handle timestamps and timezone conversions properly
- Execute INSERT, SELECT, UPDATE, DELETE operations (CRUD)
- Write filtering, sorting, and aggregation queries
- Understand transaction basics and ACID properties
- Follow SQL best practices for ML infrastructure

---

## Real-World Scenario

You're building the **ML Training Registry** for your organization's AI infrastructure platform. The platform runs hundreds of training jobs daily across multiple compute targets (Kubernetes, AWS Batch, Vertex AI), and your team needs a reliable way to:

- Track all training runs with metadata (model, framework, dataset, metrics)
- Monitor job status and troubleshoot failures
- Analyze resource utilization (GPU hours, cost)
- Audit experiments for compliance
- Provide data for dashboards and reporting

Your database will serve as the **source of truth** for:
- Data scientists querying training history
- Platform engineers monitoring infrastructure
- ML Ops teams tracking deployments
- Finance teams calculating costs
- Compliance teams auditing experiments

---

## Part 1: Environment Setup

### Step 1.1: Start PostgreSQL Container

We'll use Docker to ensure a consistent environment across all students.

```bash
# Create a directory for this exercise
mkdir -p ~/ml-training-registry
cd ~/ml-training-registry

# Create directories for SQL files
mkdir -p sql

# Start PostgreSQL 14 container
docker run --name pg-ml-training \
  -e POSTGRES_PASSWORD=mlops_secure_pass \
  -e POSTGRES_USER=mlops \
  -e POSTGRES_DB=ml_infra \
  -p 5432:5432 \
  -d postgres:14

# Wait a few seconds for PostgreSQL to start
sleep 5

# Verify container is running
docker ps | grep pg-ml-training
```

**Expected Output**:
```
CONTAINER ID   IMAGE         COMMAND                  STATUS         PORTS
abc123def456   postgres:14   "docker-entrypoint.s…"   Up 10 seconds  0.0.0.0:5432->5432/tcp
```

**Troubleshooting**:
- If port 5432 is already in use: `docker run ... -p 5433:5432` (change host port)
- If container fails to start: `docker logs pg-ml-training`
- To stop: `docker stop pg-ml-training`
- To remove: `docker rm pg-ml-training`

### Step 1.2: Connect to PostgreSQL

```bash
# Method 1: Using psql in Docker container
docker exec -it pg-ml-training psql -U mlops -d ml_infra

# Method 2: Using psql on host (if installed)
psql -h localhost -U mlops -d ml_infra
# Password: mlops_secure_pass

# Method 3: Connection string format
psql "postgresql://mlops:mlops_secure_pass@localhost:5432/ml_infra"
```

**Inside psql**, you should see:
```
psql (14.x)
Type "help" for help.

ml_infra=#
```

### Step 1.3: Essential psql Commands

```sql
-- List all databases
\l

-- List all tables in current database
\dt

-- Describe table structure
\d training_runs

-- Show current database and user
\conninfo

-- Enable query timing (helpful for performance)
\timing on

-- Execute SQL from file
\i sql/01_create_training_runs.sql

-- Quit psql
\q

-- Toggle expanded display (useful for wide results)
\x

-- Get help
\?

-- Clear screen
\! clear
```

✅ **Checkpoint**: You should be connected to the `ml_infra` database and able to run `\l` to list databases.

---

## Part 2: Understanding the Schema

### Step 2.1: Schema Design Principles

Before writing SQL, let's understand what makes a good ML training runs table:

**Key Requirements**:
1. **Unique Identification**: Every training run needs a unique ID
2. **Metadata**: Model name, framework, experiment name
3. **Status Tracking**: Queue → Running → Succeeded/Failed/Cancelled
4. **Metrics**: Accuracy, loss, other performance metrics
5. **Resource Tracking**: GPU hours, compute target, cost
6. **Flexibility**: Store arbitrary hyperparameters (learning rate, batch size, etc.)
7. **Timestamps**: Track when runs started and completed
8. **Auditability**: Notes and comments for debugging

**Data Types We'll Use**:
- `UUID`: Universally unique identifier (better than auto-increment for distributed systems)
- `TEXT`: Variable-length strings (model names, notes)
- `NUMERIC(p,s)`: Precise decimal numbers (accuracy, loss, GPU hours)
- `JSONB`: Binary JSON (flexible parameter storage)
- `TIMESTAMP WITH TIME ZONE`: Timezone-aware timestamps
- `CHECK`: Constraints to enforce data validity

### Step 2.2: Why These Choices?

| Choice | Reason |
|--------|--------|
| UUID primary key | Works across distributed systems, no collisions |
| TEXT for names | Flexible, no length limits, PostgreSQL optimized |
| NUMERIC for metrics | Exact precision (float can cause rounding errors) |
| JSONB for parameters | Flexible schema, queryable, binary format (fast) |
| TIMESTAMPTZ | Handles different timezones (AWS us-east-1 vs GCP europe-west1) |
| CHECK constraints | Enforce data quality at database level |

---

## Part 3: Create the Training Runs Table

### Step 3.1: Basic Table Creation

Create the file `sql/01_create_training_runs.sql`:

```sql
-- ============================================
-- ML Training Runs Table Schema
-- ============================================
-- Purpose: Track all ML model training jobs
-- Author: ML Infrastructure Team
-- Date: 2025-10-23
-- ============================================

-- Drop table if exists (for development/testing)
-- WARNING: This deletes all data!
DROP TABLE IF EXISTS training_runs CASCADE;

-- Create the training_runs table
CREATE TABLE training_runs (
    -- Primary key: UUID for distributed system compatibility
    run_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Model identification
    model_name TEXT NOT NULL,
    framework TEXT NOT NULL,
    experiment_name TEXT NOT NULL,

    -- Status tracking
    status TEXT NOT NULL DEFAULT 'queued',

    -- Metrics (NULL if not applicable or not yet computed)
    accuracy NUMERIC(5,4),        -- Example: 0.9234 (4 decimal places)
    loss NUMERIC(8,5),             -- Example: 123.45678
    precision_score NUMERIC(5,4),
    recall_score NUMERIC(5,4),
    f1_score NUMERIC(5,4),

    -- Data and compute configuration
    dataset TEXT NOT NULL,
    compute_target TEXT NOT NULL,
    gpu_hours NUMERIC(8,2) DEFAULT 0,
    cpu_hours NUMERIC(8,2) DEFAULT 0,

    -- Flexible parameter storage (JSON)
    parameters JSONB DEFAULT '{}'::jsonb,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,

    -- Notes and metadata
    notes TEXT,
    created_by TEXT DEFAULT CURRENT_USER,

    -- Data validation constraints
    CONSTRAINT valid_framework CHECK (
        framework IN ('pytorch', 'tensorflow', 'sklearn', 'xgboost', 'jax', 'mxnet')
    ),

    CONSTRAINT valid_status CHECK (
        status IN ('queued', 'running', 'succeeded', 'failed', 'cancelled', 'timeout')
    ),

    CONSTRAINT valid_accuracy CHECK (
        accuracy IS NULL OR (accuracy >= 0 AND accuracy <= 1)
    ),

    CONSTRAINT valid_precision CHECK (
        precision_score IS NULL OR (precision_score >= 0 AND precision_score <= 1)
    ),

    CONSTRAINT valid_recall CHECK (
        recall_score IS NULL OR (recall_score >= 0 AND recall_score <= 1)
    ),

    CONSTRAINT valid_f1 CHECK (
        f1_score IS NULL OR (f1_score >= 0 AND f1_score <= 1)
    ),

    CONSTRAINT valid_gpu_hours CHECK (gpu_hours >= 0),
    CONSTRAINT valid_cpu_hours CHECK (cpu_hours >= 0),

    -- Completed runs must have completed_at timestamp
    CONSTRAINT completed_timestamp CHECK (
        (status IN ('succeeded', 'failed', 'cancelled', 'timeout') AND completed_at IS NOT NULL)
        OR
        (status IN ('queued', 'running') AND completed_at IS NULL)
    ),

    -- Started runs must have started_at timestamp
    CONSTRAINT started_timestamp CHECK (
        (status IN ('running', 'succeeded', 'failed', 'cancelled', 'timeout') AND started_at IS NOT NULL)
        OR
        (status = 'queued' AND started_at IS NULL)
    ),

    -- Logical time ordering
    CONSTRAINT time_order CHECK (
        (started_at IS NULL OR started_at >= created_at) AND
        (completed_at IS NULL OR completed_at >= created_at)
    ),

    -- Prevent duplicate runs on same day
    CONSTRAINT unique_daily_run UNIQUE (
        model_name, experiment_name, dataset, DATE(created_at)
    )
);

-- Create indexes for common queries
CREATE INDEX idx_training_runs_status ON training_runs(status);
CREATE INDEX idx_training_runs_created_at ON training_runs(created_at DESC);
CREATE INDEX idx_training_runs_model_name ON training_runs(model_name);
CREATE INDEX idx_training_runs_framework ON training_runs(framework);
CREATE INDEX idx_training_runs_compute_target ON training_runs(compute_target);

-- Index for JSONB queries (parameters)
CREATE INDEX idx_training_runs_parameters ON training_runs USING GIN (parameters);

-- Composite index for filtering active jobs
CREATE INDEX idx_training_runs_active ON training_runs(status, created_at DESC)
    WHERE status IN ('queued', 'running');

-- Comment the table
COMMENT ON TABLE training_runs IS 'Tracks all ML model training jobs across the platform';
COMMENT ON COLUMN training_runs.run_id IS 'Unique identifier for each training run';
COMMENT ON COLUMN training_runs.parameters IS 'JSONB field storing hyperparameters and configuration';
COMMENT ON COLUMN training_runs.gpu_hours IS 'Total GPU compute hours consumed';
```

### Step 3.2: Load the Schema

```bash
# Execute the SQL file
docker exec -i pg-ml-training psql -U mlops -d ml_infra < sql/01_create_training_runs.sql

# Or from within psql:
# \i sql/01_create_training_runs.sql
```

**Expected Output**:
```
DROP TABLE
CREATE TABLE
CREATE INDEX
CREATE INDEX
CREATE INDEX
CREATE INDEX
CREATE INDEX
CREATE INDEX
CREATE INDEX
COMMENT
COMMENT
COMMENT
COMMENT
```

### Step 3.3: Verify the Table

```sql
-- Describe the table structure
\d training_runs

-- Check constraints
SELECT conname, pg_get_constraintdef(oid)
FROM pg_constraint
WHERE conrelid = 'training_runs'::regclass;

-- Check indexes
\di training_runs*

-- Check table size (should be empty)
SELECT pg_size_pretty(pg_total_relation_size('training_runs'));
```

**Expected Output for `\d training_runs`**:
```
                              Table "public.training_runs"
      Column       |           Type           | Collation | Nullable |    Default
-------------------+--------------------------+-----------+----------+----------------
 run_id            | uuid                     |           | not null | gen_random_uuid()
 model_name        | text                     |           | not null |
 framework         | text                     |           | not null |
 experiment_name   | text                     |           | not null |
 status            | text                     |           | not null | 'queued'::text
 accuracy          | numeric(5,4)             |           |          |
 ...
Indexes:
    "training_runs_pkey" PRIMARY KEY, btree (run_id)
    "unique_daily_run" UNIQUE CONSTRAINT, btree (model_name, experiment_name, dataset, ...
    ...
```

✅ **Checkpoint**: Table created successfully with all constraints and indexes.

---

## Part 4: Insert Seed Data (CREATE Operations)

### Step 4.1: Understanding INSERT Syntax

```sql
-- Basic INSERT syntax
INSERT INTO table_name (column1, column2, ...)
VALUES (value1, value2, ...);

-- Insert multiple rows
INSERT INTO table_name (column1, column2, ...)
VALUES
    (value1a, value2a, ...),
    (value1b, value2b, ...),
    (value1c, value2c, ...);

-- Insert with RETURNING (get inserted data back)
INSERT INTO table_name (column1, column2, ...)
VALUES (value1, value2, ...)
RETURNING *;  -- or RETURNING column1, column2
```

### Step 4.2: Create Seed Data File

Create `sql/02_seed_training_runs.sql`:

```sql
-- ============================================
-- ML Training Runs Seed Data
-- ============================================
-- Purpose: Insert realistic training run data
-- Date: 2025-10-23
-- ============================================

-- Insert 20 training runs with realistic data
INSERT INTO training_runs (
    model_name, framework, experiment_name, status,
    accuracy, loss, precision_score, recall_score, f1_score,
    dataset, compute_target, gpu_hours, cpu_hours,
    parameters, created_at, started_at, completed_at, notes
) VALUES

-- Successful runs
(
    'resnet50-classification',
    'pytorch',
    'exp-baseline-2025-q1',
    'succeeded',
    0.9234,
    0.2876,
    0.9156,
    0.9312,
    0.9233,
    'imagenet-1k',
    'k8s-gpu-a100',
    24.5,
    2.1,
    '{"learning_rate": 0.001, "batch_size": 64, "optimizer": "adam", "epochs": 30, "augmentation": true}',
    NOW() - INTERVAL '5 days',
    NOW() - INTERVAL '5 days' + INTERVAL '10 minutes',
    NOW() - INTERVAL '4 days 1 hour',
    'Baseline model achieved target accuracy. Ready for deployment.'
),

(
    'bert-sentiment-analysis',
    'tensorflow',
    'exp-bert-base-v1',
    'succeeded',
    0.8923,
    0.3245,
    0.8856,
    0.8991,
    0.8923,
    'imdb-reviews',
    'aws-sagemaker-p3',
    16.2,
    1.5,
    '{"learning_rate": 0.00005, "batch_size": 32, "max_length": 512, "model_checkpoint": "bert-base-uncased"}',
    NOW() - INTERVAL '7 days',
    NOW() - INTERVAL '7 days' + INTERVAL '5 minutes',
    NOW() - INTERVAL '6 days 8 hours',
    'BERT fine-tuning completed. F1 score meets SLA requirements.'
),

(
    'recommendation-collaborative-filter',
    'sklearn',
    'exp-svd-baseline',
    'succeeded',
    NULL,  -- Not applicable for recommendation systems
    0.1234,
    NULL,
    NULL,
    NULL,
    'movielens-25m',
    'on-premise-cpu',
    0.0,
    45.6,
    '{"algorithm": "SVD", "n_factors": 100, "n_epochs": 20, "lr_all": 0.005, "reg_all": 0.02}',
    NOW() - INTERVAL '3 days',
    NOW() - INTERVAL '3 days' + INTERVAL '2 minutes',
    NOW() - INTERVAL '2 days 20 hours',
    'SVD baseline for comparison. RMSE: 0.1234'
),

(
    'object-detection-yolo',
    'pytorch',
    'exp-yolo-v8-coco',
    'succeeded',
    0.7845,  -- mAP@0.5
    1.2345,
    0.7623,
    0.8012,
    0.7812,
    'coco-2017',
    'gcp-vertex-ai-v100',
    32.4,
    3.2,
    '{"model": "yolov8l", "img_size": 640, "batch_size": 16, "epochs": 50, "iou_threshold": 0.5}',
    NOW() - INTERVAL '10 days',
    NOW() - INTERVAL '10 days' + INTERVAL '15 minutes',
    NOW() - INTERVAL '8 days 12 hours',
    'YOLOv8 training complete. mAP@0.5: 0.7845. Deployed to production.'
),

(
    'timeseries-lstm-forecast',
    'tensorflow',
    'exp-lstm-multistep-v2',
    'succeeded',
    NULL,
    0.0456,  -- MAE
    NULL,
    NULL,
    NULL,
    'energy-consumption-hourly',
    'aws-batch-gpu',
    8.7,
    0.9,
    '{"layers": [128, 64, 32], "dropout": 0.2, "sequence_length": 168, "forecast_horizon": 24}',
    NOW() - INTERVAL '2 days',
    NOW() - INTERVAL '2 days' + INTERVAL '3 minutes',
    NOW() - INTERVAL '1 day 14 hours',
    'LSTM forecast model. MAE improved by 12% vs baseline.'
),

-- Failed runs
(
    'gan-image-generation',
    'pytorch',
    'exp-stylegan3-highres',
    'failed',
    NULL,
    NULL,
    NULL,
    NULL,
    NULL,
    'ffhq-512x512',
    'k8s-gpu-a100',
    12.3,
    1.1,
    '{"resolution": 512, "batch_size": 8, "g_lr": 0.0025, "d_lr": 0.0025}',
    NOW() - INTERVAL '1 day',
    NOW() - INTERVAL '1 day' + INTERVAL '8 minutes',
    NOW() - INTERVAL '1 day' + INTERVAL '12 hours 20 minutes',
    'Training failed: OOM error. Discriminator loss exploded at iteration 45000. Need to reduce batch size.'
),

(
    'nlp-transformer-translation',
    'jax',
    'exp-t5-en-fr',
    'failed',
    NULL,
    NULL,
    NULL,
    NULL,
    NULL,
    'wmt14-en-fr',
    'gcp-tpu-v3',
    0.0,  -- TPU, not GPU
    156.3,
    '{"model": "t5-base", "max_source_length": 128, "max_target_length": 128, "batch_size": 64}',
    NOW() - INTERVAL '4 days',
    NOW() - INTERVAL '4 days' + INTERVAL '20 minutes',
    NOW() - INTERVAL '3 days 18 hours',
    'JAX/Flax training failed: TPU out of memory. Reduce batch size from 64 to 32.'
),

(
    'anomaly-detection-autoencoder',
    'tensorflow',
    'exp-vae-network-intrusion',
    'failed',
    NULL,
    NULL,
    NULL,
    NULL,
    NULL,
    'kdd-cup-99',
    'on-premise-gpu',
    3.2,
    0.4,
    '{"latent_dim": 16, "encoder_layers": [128, 64], "decoder_layers": [64, 128]}',
    NOW() - INTERVAL '6 days',
    NOW() - INTERVAL '6 days' + INTERVAL '5 minutes',
    NOW() - INTERVAL '6 days' + INTERVAL '3 hours 12 minutes',
    'Training diverged. Loss became NaN after epoch 12. Investigating data preprocessing.'
),

-- Running jobs
(
    'llm-fine-tune-mistral',
    'pytorch',
    'exp-mistral-7b-instruct',
    'running',
    NULL,
    NULL,
    NULL,
    NULL,
    NULL,
    'custom-instruction-dataset',
    'aws-p4d-24xlarge',
    48.5,  -- Expensive!
    4.2,
    '{"model": "mistral-7b-v0.1", "lora_r": 16, "lora_alpha": 32, "batch_size": 4, "gradient_accumulation": 8}',
    NOW() - INTERVAL '6 hours',
    NOW() - INTERVAL '5 hours 55 minutes',
    NULL,
    NULL
),

(
    'multimodal-clip-training',
    'pytorch',
    'exp-clip-vit-b32',
    'running',
    NULL,
    NULL,
    NULL,
    NULL,
    NULL,
    'laion-400m-subset',
    'k8s-gpu-a100-cluster',
    156.2,
    12.3,
    '{"vision_model": "vit-b-32", "text_model": "bert-base", "batch_size": 256, "num_gpus": 8}',
    NOW() - INTERVAL '2 days 4 hours',
    NOW() - INTERVAL '2 days 3 hours 50 minutes',
    NULL,
    NULL
),

-- Queued jobs
(
    'speech-recognition-whisper',
    'pytorch',
    'exp-whisper-large-v3',
    'queued',
    NULL,
    NULL,
    NULL,
    NULL,
    NULL,
    'librispeech-960h',
    'gcp-vertex-ai-a100',
    0.0,
    0.0,
    '{"model": "whisper-large-v3", "batch_size": 16, "gradient_checkpointing": true}',
    NOW() - INTERVAL '30 minutes',
    NULL,
    NULL,
    NULL
),

(
    'reinforcement-learning-ppo',
    'pytorch',
    'exp-ppo-atari-breakout',
    'queued',
    NULL,
    NULL,
    NULL,
    NULL,
    NULL,
    'atari-breakout',
    'on-premise-gpu',
    0.0,
    0.0,
    '{"algorithm": "ppo", "num_envs": 16, "num_steps": 128, "num_epochs": 4, "clip_range": 0.2}',
    NOW() - INTERVAL '15 minutes',
    NULL,
    NULL,
    NULL
),

-- Cancelled jobs
(
    'graph-neural-network',
    'pytorch',
    'exp-gnn-molecular-properties',
    'cancelled',
    NULL,
    NULL,
    NULL,
    NULL,
    NULL,
    'qm9-molecules',
    'aws-batch-cpu',
    0.0,
    12.3,
    '{"model": "gcn", "hidden_dim": 128, "num_layers": 4, "pooling": "mean"}',
    NOW() - INTERVAL '8 days',
    NOW() - INTERVAL '8 days' + INTERVAL '10 minutes',
    NOW() - INTERVAL '8 days' + INTERVAL '2 hours 5 minutes',
    'Cancelled by user. Dataset preprocessing issues discovered. Will retry with corrected data.'
),

-- Timeout
(
    'neural-architecture-search',
    'tensorflow',
    'exp-nas-efficient-net',
    'timeout',
    NULL,
    NULL,
    NULL,
    NULL,
    NULL,
    'cifar-100',
    'gcp-tpu-v4',
    0.0,
    456.7,
    '{"search_space": "efficientnet", "num_trials": 1000, "time_budget_hours": 48}',
    NOW() - INTERVAL '12 days',
    NOW() - INTERVAL '12 days' + INTERVAL '30 minutes',
    NOW() - INTERVAL '10 days',
    'Exceeded 48-hour time budget. Architecture search incomplete. Consider resuming from checkpoint.'
),

-- More successful runs for variety
(
    'tabular-xgboost-classification',
    'xgboost',
    'exp-xgb-fraud-detection',
    'succeeded',
    0.9567,
    0.1234,
    0.9423,
    0.9689,
    0.9554,
    'credit-card-fraud',
    'aws-batch-cpu',
    0.0,
    8.9,
    '{"max_depth": 6, "learning_rate": 0.1, "n_estimators": 200, "objective": "binary:logistic"}',
    NOW() - INTERVAL '1 day',
    NOW() - INTERVAL '1 day' + INTERVAL '2 minutes',
    NOW() - INTERVAL '1 day' + INTERVAL '8 hours 45 minutes',
    'XGBoost fraud detection. Precision: 0.9423, Recall: 0.9689. Deployed to prod.'
),

(
    'semantic-segmentation-unet',
    'pytorch',
    'exp-unet-medical-imaging',
    'succeeded',
    0.8834,  -- Dice coefficient
    0.2145,
    0.8756,
    0.8912,
    0.8833,
    'medical-ct-scans',
    'k8s-gpu-v100',
    18.9,
    1.8,
    '{"architecture": "unet", "encoder": "resnet34", "num_classes": 3, "loss": "dice_ce"}',
    NOW() - INTERVAL '9 days',
    NOW() - INTERVAL '9 days' + INTERVAL '12 minutes',
    NOW() - INTERVAL '8 days 6 hours',
    'U-Net segmentation for medical imaging. Dice: 0.8834. Clinical validation pending.'
),

(
    'time-series-prophet-forecast',
    'sklearn',
    'exp-prophet-sales-forecast',
    'succeeded',
    NULL,
    0.0892,  -- MAPE
    NULL,
    NULL,
    NULL,
    'retail-sales-monthly',
    'on-premise-cpu',
    0.0,
    2.3,
    '{"seasonality_mode": "multiplicative", "yearly_seasonality": true, "weekly_seasonality": false}',
    NOW() - INTERVAL '5 days',
    NOW() - INTERVAL '5 days' + INTERVAL '1 minute',
    NOW() - INTERVAL '5 days' + INTERVAL '2 hours 15 minutes',
    'Prophet forecast model. MAPE: 8.92%. Used for quarterly planning.'
),

(
    'bert-question-answering',
    'tensorflow',
    'exp-squad-v2-distilbert',
    'succeeded',
    0.8145,  -- F1 score
    1.0234,
    0.8012,
    0.8289,
    0.8145,
    'squad-v2',
    'gcp-vertex-ai-t4',
    12.4,
    1.2,
    '{"model": "distilbert-base-uncased", "max_seq_length": 384, "doc_stride": 128, "batch_size": 12}',
    NOW() - INTERVAL '11 days',
    NOW() - INTERVAL '11 days' + INTERVAL '8 minutes',
    NOW() - INTERVAL '10 days 14 hours',
    'DistilBERT QA model. F1: 0.8145. 40% faster than BERT-base with minimal accuracy loss.'
),

(
    'image-super-resolution-esrgan',
    'pytorch',
    'exp-esrgan-4x-upscale',
    'succeeded',
    NULL,
    NULL,
    NULL,
    NULL,
    NULL,
    'div2k-flickr2k',
    'k8s-gpu-a100',
    28.6,
    2.4,
    '{"scale_factor": 4, "generator_lr": 0.0001, "discriminator_lr": 0.0001, "perceptual_loss_weight": 1.0}',
    NOW() - INTERVAL '6 days',
    NOW() - INTERVAL '6 days' + INTERVAL '18 minutes',
    NOW() - INTERVAL '5 days 4 hours',
    'ESRGAN 4x super-resolution. PSNR: 28.45 dB, SSIM: 0.8234. Visual quality excellent.'
),

(
    'audio-classification-vgg',
    'tensorflow',
    'exp-audio-vgg-urban-sounds',
    'succeeded',
    0.9123,
    0.2567,
    0.9045,
    0.9201,
    0.9122,
    'urbansound8k',
    'aws-sagemaker-ml-p2',
    6.8,
    0.7,
    '{"model": "vggish", "sample_rate": 16000, "n_mels": 128, "hop_length": 512}',
    NOW() - INTERVAL '3 days',
    NOW() - INTERVAL '3 days' + INTERVAL '4 minutes',
    NOW() - INTERVAL '2 days 18 hours',
    'Audio classification using VGGish. Accuracy: 0.9123 on UrbanSound8K test set.'
);

-- Verify inserts
SELECT COUNT(*) AS total_runs FROM training_runs;
SELECT status, COUNT(*) AS count FROM training_runs GROUP BY status ORDER BY count DESC;
```

### Step 4.3: Load Seed Data

```bash
# Execute seed data
docker exec -i pg-ml-training psql -U mlops -d ml_infra < sql/02_seed_training_runs.sql
```

**Expected Output**:
```
INSERT 0 20
 total_runs
------------
         20
(1 row)

  status   | count
-----------+-------
 succeeded |    12
 failed    |     3
 running   |     2
 queued    |     2
 cancelled |     1
 timeout   |     1
(6 rows)
```

### Step 4.4: Verify Data

```sql
-- View first 5 runs
SELECT run_id, model_name, framework, status, accuracy, gpu_hours
FROM training_runs
ORDER BY created_at DESC
LIMIT 5;

-- Check data types and values
SELECT
    model_name,
    framework,
    status,
    ROUND(gpu_hours::numeric, 2) as gpu_hours,
    parameters->>'learning_rate' as learning_rate,
    parameters->>'batch_size' as batch_size
FROM training_runs
WHERE framework = 'pytorch'
LIMIT 5;
```

✅ **Checkpoint**: 20 training runs inserted successfully with realistic data.

---

## Part 5: Read Operations (SELECT Queries)

### Step 5.1: Basic SELECT Queries

Create `sql/03_crud_operations.sql`:

```sql
-- ============================================
-- CRUD Operations Examples
-- ============================================

-- ====================
-- READ (SELECT) QUERIES
-- ====================

-- 1. Select all columns (avoid in production!)
SELECT * FROM training_runs LIMIT 3;

-- 2. Select specific columns
SELECT run_id, model_name, framework, status, created_at
FROM training_runs
LIMIT 5;

-- 3. Filter with WHERE
SELECT model_name, status, accuracy
FROM training_runs
WHERE status = 'succeeded';

-- 4. Multiple conditions with AND
SELECT model_name, framework, accuracy, gpu_hours
FROM training_runs
WHERE status = 'succeeded'
  AND framework = 'pytorch'
  AND accuracy > 0.9;

-- 5. Multiple conditions with OR
SELECT model_name, status, notes
FROM training_runs
WHERE status = 'failed' OR status = 'timeout';

-- 6. IN operator
SELECT model_name, framework, status
FROM training_runs
WHERE framework IN ('pytorch', 'tensorflow');

-- 7. BETWEEN for ranges
SELECT model_name, gpu_hours, created_at
FROM training_runs
WHERE gpu_hours BETWEEN 10 AND 30;

-- 8. LIKE for pattern matching
SELECT model_name, dataset
FROM training_runs
WHERE model_name LIKE '%bert%';

-- 9. IS NULL / IS NOT NULL
SELECT model_name, status, accuracy
FROM training_runs
WHERE accuracy IS NULL;

SELECT model_name, status, accuracy
FROM training_runs
WHERE accuracy IS NOT NULL;

-- 10. ORDER BY
SELECT model_name, accuracy, gpu_hours
FROM training_runs
WHERE status = 'succeeded'
ORDER BY accuracy DESC
LIMIT 10;

-- 11. ORDER BY multiple columns
SELECT model_name, framework, accuracy
FROM training_runs
ORDER BY framework ASC, accuracy DESC NULLS LAST;
```

### Step 5.2: Aggregate Functions

```sql
-- ====================
-- AGGREGATE QUERIES
-- ====================

-- Count total runs
SELECT COUNT(*) AS total_runs FROM training_runs;

-- Count non-null accuracies
SELECT COUNT(accuracy) AS runs_with_accuracy FROM training_runs;

-- Average accuracy
SELECT ROUND(AVG(accuracy)::numeric, 4) AS avg_accuracy
FROM training_runs
WHERE accuracy IS NOT NULL;

-- Min, Max, Sum
SELECT
    MIN(gpu_hours) AS min_gpu,
    MAX(gpu_hours) AS max_gpu,
    ROUND(SUM(gpu_hours)::numeric, 2) AS total_gpu_hours,
    ROUND(AVG(gpu_hours)::numeric, 2) AS avg_gpu_hours
FROM training_runs;

-- Standard deviation
SELECT
    ROUND(STDDEV(accuracy)::numeric, 4) AS stddev_accuracy
FROM training_runs
WHERE accuracy IS NOT NULL;
```

### Step 5.3: GROUP BY Queries

```sql
-- ====================
-- GROUP BY QUERIES
-- ====================

-- Runs by status
SELECT status, COUNT(*) AS count
FROM training_runs
GROUP BY status
ORDER BY count DESC;

-- Runs by framework
SELECT framework, COUNT(*) AS count
FROM training_runs
GROUP BY framework
ORDER BY count DESC;

-- Average accuracy by framework
SELECT
    framework,
    COUNT(*) AS total_runs,
    COUNT(accuracy) AS runs_with_accuracy,
    ROUND(AVG(accuracy)::numeric, 4) AS avg_accuracy
FROM training_runs
GROUP BY framework
ORDER BY avg_accuracy DESC NULLS LAST;

-- GPU usage by compute target
SELECT
    compute_target,
    COUNT(*) AS runs,
    ROUND(SUM(gpu_hours)::numeric, 2) AS total_gpu_hours,
    ROUND(AVG(gpu_hours)::numeric, 2) AS avg_gpu_hours
FROM training_runs
GROUP BY compute_target
ORDER BY total_gpu_hours DESC;

-- HAVING clause (filter groups)
SELECT
    framework,
    COUNT(*) AS runs
FROM training_runs
GROUP BY framework
HAVING COUNT(*) >= 3
ORDER BY runs DESC;

-- Complex grouping
SELECT
    framework,
    status,
    COUNT(*) AS count,
    ROUND(AVG(gpu_hours)::numeric, 2) AS avg_gpu_hours
FROM training_runs
GROUP BY framework, status
ORDER BY framework, status;
```

### Step 5.4: JSONB Queries

```sql
-- ====================
-- JSONB QUERIES
-- ====================

-- Access JSON field
SELECT
    model_name,
    parameters->>'learning_rate' AS learning_rate,
    parameters->>'batch_size' AS batch_size
FROM training_runs
WHERE parameters ? 'learning_rate'  -- Check if key exists
LIMIT 5;

-- Filter by JSON value
SELECT model_name, parameters
FROM training_runs
WHERE parameters->>'optimizer' = 'adam';

-- Convert JSON value to number for comparison
SELECT model_name, parameters->>'batch_size' AS batch_size
FROM training_runs
WHERE (parameters->>'batch_size')::int >= 32;

-- Check if JSON contains key
SELECT model_name, parameters
FROM training_runs
WHERE parameters ? 'lora_r';  -- LoRA fine-tuning

-- JSON array operations
SELECT
    model_name,
    parameters->'encoder_layers' AS encoder_layers
FROM training_runs
WHERE parameters ? 'encoder_layers';
```

### Step 5.5: Date/Time Queries

```sql
-- ====================
-- DATE/TIME QUERIES
-- ====================

-- Runs in last 7 days
SELECT model_name, status, created_at
FROM training_runs
WHERE created_at > NOW() - INTERVAL '7 days';

-- Runs today
SELECT model_name, status, created_at
FROM training_runs
WHERE DATE(created_at) = CURRENT_DATE;

-- Runs this week
SELECT model_name, status, created_at
FROM training_runs
WHERE created_at > DATE_TRUNC('week', NOW());

-- Calculate duration (for completed runs)
SELECT
    model_name,
    status,
    started_at,
    completed_at,
    completed_at - started_at AS duration
FROM training_runs
WHERE completed_at IS NOT NULL
ORDER BY duration DESC;

-- Extract parts of timestamp
SELECT
    model_name,
    EXTRACT(YEAR FROM created_at) AS year,
    EXTRACT(MONTH FROM created_at) AS month,
    EXTRACT(DAY FROM created_at) AS day,
    TO_CHAR(created_at, 'YYYY-MM-DD HH24:MI:SS') AS formatted_date
FROM training_runs
LIMIT 5;

-- Age function
SELECT
    model_name,
    created_at,
    AGE(NOW(), created_at) AS age
FROM training_runs
ORDER BY age ASC
LIMIT 5;
```

### Step 5.6: Practical Queries for ML Infrastructure

```sql
-- ====================
-- PRACTICAL ML QUERIES
-- ====================

-- Query 1: Active jobs (running or queued)
SELECT
    run_id,
    model_name,
    framework,
    status,
    created_at,
    AGE(NOW(), created_at) AS wait_time
FROM training_runs
WHERE status IN ('queued', 'running')
ORDER BY created_at ASC;

-- Query 2: Recent failures (last 7 days) with notes
SELECT
    model_name,
    framework,
    dataset,
    created_at,
    completed_at,
    completed_at - started_at AS duration,
    notes
FROM training_runs
WHERE status = 'failed'
  AND created_at > NOW() - INTERVAL '7 days'
ORDER BY created_at DESC;

-- Query 3: Top 10 most accurate models
SELECT
    model_name,
    framework,
    dataset,
    accuracy,
    precision_score,
    recall_score,
    f1_score,
    gpu_hours
FROM training_runs
WHERE status = 'succeeded'
  AND accuracy IS NOT NULL
ORDER BY accuracy DESC
LIMIT 10;

-- Query 4: Resource utilization by compute target
SELECT
    compute_target,
    COUNT(*) AS total_runs,
    COUNT(*) FILTER (WHERE status = 'succeeded') AS successful_runs,
    COUNT(*) FILTER (WHERE status = 'failed') AS failed_runs,
    ROUND(SUM(gpu_hours)::numeric, 2) AS total_gpu_hours,
    ROUND(AVG(gpu_hours)::numeric, 2) AS avg_gpu_hours_per_run,
    ROUND(100.0 * COUNT(*) FILTER (WHERE status = 'succeeded') / COUNT(*), 2) AS success_rate
FROM training_runs
GROUP BY compute_target
ORDER BY total_gpu_hours DESC;

-- Query 5: High GPU usage runs (potential cost issues)
SELECT
    run_id,
    model_name,
    framework,
    compute_target,
    gpu_hours,
    completed_at - started_at AS duration,
    parameters->>'batch_size' AS batch_size,
    notes
FROM training_runs
WHERE gpu_hours > 20
   OR parameters->>'accelerator' = 'a100'
ORDER BY gpu_hours DESC;

-- Query 6: Models that need review (low accuracy or NULL)
SELECT
    run_id,
    model_name,
    framework,
    status,
    COALESCE(accuracy, 0.0) AS accuracy,
    created_at,
    notes
FROM training_runs
WHERE (accuracy IS NULL OR accuracy < 0.7)
  AND status = 'succeeded'
ORDER BY accuracy ASC NULLS FIRST;

-- Query 7: Framework performance comparison
SELECT
    framework,
    COUNT(*) AS total_runs,
    ROUND(AVG(accuracy) FILTER (WHERE accuracy IS NOT NULL)::numeric, 4) AS avg_accuracy,
    ROUND(AVG(gpu_hours)::numeric, 2) AS avg_gpu_hours,
    ROUND(AVG(EXTRACT(EPOCH FROM (completed_at - started_at)) / 3600) FILTER (WHERE completed_at IS NOT NULL)::numeric, 2) AS avg_duration_hours
FROM training_runs
GROUP BY framework
ORDER BY avg_accuracy DESC NULLS LAST;

-- Query 8: Daily training activity
SELECT
    DATE(created_at) AS date,
    COUNT(*) AS runs_started,
    COUNT(*) FILTER (WHERE status = 'succeeded') AS succeeded,
    COUNT(*) FILTER (WHERE status = 'failed') AS failed,
    ROUND(SUM(gpu_hours)::numeric, 2) AS total_gpu_hours
FROM training_runs
WHERE created_at > NOW() - INTERVAL '30 days'
GROUP BY DATE(created_at)
ORDER BY date DESC;

-- Query 9: Long-running jobs (potential hangs)
SELECT
    run_id,
    model_name,
    framework,
    status,
    started_at,
    AGE(NOW(), started_at) AS running_time,
    compute_target
FROM training_runs
WHERE status = 'running'
  AND started_at < NOW() - INTERVAL '24 hours'
ORDER BY started_at ASC;

-- Query 10: Model experiment history
SELECT
    experiment_name,
    COUNT(*) AS total_attempts,
    COUNT(*) FILTER (WHERE status = 'succeeded') AS succeeded,
    MAX(accuracy) AS best_accuracy,
    AVG(accuracy) FILTER (WHERE accuracy IS NOT NULL) AS avg_accuracy,
    SUM(gpu_hours) AS total_gpu_hours
FROM training_runs
WHERE model_name LIKE '%bert%'
GROUP BY experiment_name
ORDER BY best_accuracy DESC NULLS LAST;
```

✅ **Checkpoint**: You can run complex SELECT queries with filtering, aggregation, and JSONB operations.

---

## Part 6: Update Operations

### Step 6.1: Basic UPDATE Syntax

```sql
-- ====================
-- UPDATE OPERATIONS
-- ====================

-- Basic UPDATE syntax
-- UPDATE table_name
-- SET column1 = value1, column2 = value2, ...
-- WHERE condition;

-- IMPORTANT: Always use WHERE clause to avoid updating all rows!
```

### Step 6.2: Practical UPDATE Examples

```sql
-- Update 1: Start a queued job
UPDATE training_runs
SET
    status = 'running',
    started_at = NOW(),
    notes = 'Job picked up by scheduler at ' || NOW()
WHERE status = 'queued'
  AND model_name = 'speech-recognition-whisper'
RETURNING run_id, model_name, status, started_at;

-- Update 2: Complete a successful run
UPDATE training_runs
SET
    status = 'succeeded',
    completed_at = NOW(),
    accuracy = 0.9456,
    loss = 0.1892,
    precision_score = 0.9423,
    recall_score = 0.9489,
    f1_score = 0.9456,
    gpu_hours = gpu_hours + 18.5,  -- Add final GPU usage
    notes = 'Training completed successfully. Model deployed to production.'
WHERE status = 'running'
  AND model_name = 'llm-fine-tune-mistral'
RETURNING run_id, model_name, status, accuracy, completed_at;

-- Update 3: Mark a running job as failed
UPDATE training_runs
SET
    status = 'failed',
    completed_at = NOW(),
    notes = 'Out of memory error. Killed by scheduler.'
WHERE status = 'running'
  AND model_name = 'multimodal-clip-training'
RETURNING run_id, model_name, status, notes;

-- Update 4: Update JSON parameters
UPDATE training_runs
SET
    parameters = parameters || '{"tuned": true, "final_lr": 0.00001}'::jsonb
WHERE model_name = 'bert-sentiment-analysis'
  AND status = 'succeeded'
RETURNING model_name, parameters;

-- Update 5: Bulk update - add created_by for older runs
UPDATE training_runs
SET created_by = 'legacy_system'
WHERE created_by = 'mlops'
  AND created_at < NOW() - INTERVAL '10 days'
RETURNING COUNT(*);

-- Update 6: Conditional update based on calculation
UPDATE training_runs
SET
    f1_score = 2.0 * (precision_score * recall_score) / (precision_score + recall_score)
WHERE precision_score IS NOT NULL
  AND recall_score IS NOT NULL
  AND f1_score IS NULL
RETURNING model_name, precision_score, recall_score, f1_score;

-- Update 7: Increment values
UPDATE training_runs
SET gpu_hours = gpu_hours + 2.5
WHERE status = 'running'
  AND model_name = 'multimodal-clip-training'
RETURNING model_name, gpu_hours;
```

### Step 6.3: Safe UPDATE Practices

```sql
-- ====================
-- SAFE UPDATE PRACTICES
-- ====================

-- Always use transactions for important updates
BEGIN;

-- Preview what will be updated
SELECT run_id, model_name, status, accuracy
FROM training_runs
WHERE status = 'queued'
  AND created_at < NOW() - INTERVAL '1 hour';

-- Perform the update
UPDATE training_runs
SET status = 'cancelled',
    completed_at = NOW(),
    notes = 'Cancelled: queued for over 1 hour without starting'
WHERE status = 'queued'
  AND created_at < NOW() - INTERVAL '1 hour';

-- Verify the update
SELECT run_id, model_name, status, completed_at, notes
FROM training_runs
WHERE status = 'cancelled'
  AND completed_at > NOW() - INTERVAL '1 minute';

-- If satisfied, commit. Otherwise, rollback.
COMMIT;
-- ROLLBACK;
```

✅ **Checkpoint**: You can safely update records with WHERE clauses and transactions.

---

## Part 7: Delete Operations

### Step 7.1: Basic DELETE Syntax

```sql
-- ====================
-- DELETE OPERATIONS
-- ====================

-- Basic DELETE syntax
-- DELETE FROM table_name
-- WHERE condition;

-- WARNING: DELETE without WHERE removes ALL rows!
-- Always use WHERE clause!
```

### Step 7.2: Practical DELETE Examples

```sql
-- Delete 1: Remove old test runs
BEGIN;

-- Count before delete
SELECT COUNT(*) AS before_count
FROM training_runs
WHERE notes ILIKE '%test%'
  AND created_at < NOW() - INTERVAL '120 days';

-- Perform delete
DELETE FROM training_runs
WHERE notes ILIKE '%test%'
  AND created_at < NOW() - INTERVAL '120 days'
  AND status = 'failed'
RETURNING run_id, model_name, created_at;

-- Count after delete
SELECT COUNT(*) AS after_count
FROM training_runs;

COMMIT;

-- Delete 2: Remove cancelled runs older than 90 days
BEGIN;

SELECT COUNT(*) FROM training_runs WHERE status = 'cancelled' AND created_at < NOW() - INTERVAL '90 days';

DELETE FROM training_runs
WHERE status = 'cancelled'
  AND created_at < NOW() - INTERVAL '90 days';

COMMIT;

-- Delete 3: Remove specific run by ID
DELETE FROM training_runs
WHERE run_id = '00000000-0000-0000-0000-000000000000'  -- Replace with actual UUID
RETURNING *;

-- Delete 4: Cascade delete (if we had foreign keys)
-- This would delete related records in other tables
-- We'll cover this in Exercise 02
```

### Step 7.3: DELETE vs TRUNCATE

```sql
-- DELETE: Removes specific rows, can use WHERE, slower, can rollback
DELETE FROM training_runs WHERE status = 'failed';

-- TRUNCATE: Removes ALL rows, faster, resets sequences, cannot rollback easily
-- Use with extreme caution!
TRUNCATE TABLE training_runs;  -- DON'T RUN THIS NOW!

-- TRUNCATE with CASCADE (drops dependent data)
-- TRUNCATE TABLE training_runs CASCADE;  -- DANGEROUS!
```

✅ **Checkpoint**: You understand DELETE operations and safety practices.

---

## Part 8: Transactions and Data Integrity

### Step 8.1: Understanding Transactions

```sql
-- ====================
-- TRANSACTIONS
-- ====================

-- Transaction: Multiple operations as a single unit
-- Either ALL succeed or ALL fail (atomicity)

-- Basic transaction
BEGIN;
    INSERT INTO training_runs (...) VALUES (...);
    UPDATE training_runs SET ... WHERE ...;
    DELETE FROM training_runs WHERE ...;
COMMIT;  -- Make changes permanent

-- Rollback example
BEGIN;
    UPDATE training_runs SET status = 'failed' WHERE run_id = '...';
    -- Oops, made a mistake!
ROLLBACK;  -- Undo all changes since BEGIN
```

### Step 8.2: Practical Transaction Example

```sql
-- ====================
-- PRACTICAL TRANSACTION
-- ====================

-- Scenario: Move a job from queued -> running -> succeeded

BEGIN;

-- Step 1: Verify job is queued
SELECT run_id, model_name, status
FROM training_runs
WHERE model_name = 'reinforcement-learning-ppo'
  AND status = 'queued';

-- Step 2: Start the job
UPDATE training_runs
SET
    status = 'running',
    started_at = NOW(),
    notes = 'Started by scheduler'
WHERE model_name = 'reinforcement-learning-ppo'
  AND status = 'queued';

-- Step 3: Simulate job completion (in real life, this would be minutes/hours later)
-- For demo purposes only:
UPDATE training_runs
SET
    status = 'succeeded',
    completed_at = NOW(),
    accuracy = 0.8234,
    loss = 0.4567,
    gpu_hours = 15.6,
    notes = 'PPO training completed. Breakout score: 450 average.'
WHERE model_name = 'reinforcement-learning-ppo'
  AND status = 'running';

-- Step 4: Verify final state
SELECT run_id, model_name, status, accuracy, gpu_hours, started_at, completed_at
FROM training_runs
WHERE model_name = 'reinforcement-learning-ppo';

-- If everything looks good:
COMMIT;

-- If something went wrong:
-- ROLLBACK;
```

### Step 8.3: Transaction Isolation

```sql
-- PostgreSQL default isolation level: READ COMMITTED
SHOW transaction_isolation;

-- Set isolation level (for advanced use cases)
BEGIN TRANSACTION ISOLATION LEVEL SERIALIZABLE;
    -- Your queries here
COMMIT;
```

✅ **Checkpoint**: You understand transactions and can use BEGIN/COMMIT/ROLLBACK.

---

## Part 9: Advanced Topics

### Step 9.1: Subqueries

```sql
-- ====================
-- SUBQUERIES
-- ====================

-- Subquery in WHERE clause
SELECT model_name, accuracy
FROM training_runs
WHERE accuracy > (
    SELECT AVG(accuracy)
    FROM training_runs
    WHERE accuracy IS NOT NULL
);

-- Subquery in FROM clause (derived table)
SELECT
    framework,
    avg_accuracy
FROM (
    SELECT
        framework,
        ROUND(AVG(accuracy)::numeric, 4) AS avg_accuracy
    FROM training_runs
    WHERE accuracy IS NOT NULL
    GROUP BY framework
) AS framework_stats
WHERE avg_accuracy > 0.85;

-- Correlated subquery
SELECT
    t1.model_name,
    t1.accuracy,
    (
        SELECT COUNT(*)
        FROM training_runs t2
        WHERE t2.model_name = t1.model_name
    ) AS total_experiments
FROM training_runs t1
WHERE t1.status = 'succeeded';
```

### Step 9.2: Common Table Expressions (CTEs)

```sql
-- ====================
-- CTEs (WITH clause)
-- ====================

-- CTE for better readability
WITH successful_runs AS (
    SELECT *
    FROM training_runs
    WHERE status = 'succeeded'
      AND accuracy IS NOT NULL
),
framework_stats AS (
    SELECT
        framework,
        COUNT(*) AS runs,
        ROUND(AVG(accuracy)::numeric, 4) AS avg_accuracy
    FROM successful_runs
    GROUP BY framework
)
SELECT *
FROM framework_stats
WHERE avg_accuracy > 0.85
ORDER BY avg_accuracy DESC;

-- Multiple CTEs
WITH
pytorch_runs AS (
    SELECT * FROM training_runs WHERE framework = 'pytorch'
),
tensorflow_runs AS (
    SELECT * FROM training_runs WHERE framework = 'tensorflow'
)
SELECT
    'PyTorch' AS framework,
    COUNT(*) AS runs,
    ROUND(AVG(accuracy)::numeric, 4) AS avg_accuracy
FROM pytorch_runs
WHERE accuracy IS NOT NULL

UNION ALL

SELECT
    'TensorFlow' AS framework,
    COUNT(*) AS runs,
    ROUND(AVG(accuracy)::numeric, 4) AS avg_accuracy
FROM tensorflow_runs
WHERE accuracy IS NOT NULL;
```

### Step 9.3: Window Functions

```sql
-- ====================
-- WINDOW FUNCTIONS
-- ====================

-- Rank models by accuracy within each framework
SELECT
    model_name,
    framework,
    accuracy,
    RANK() OVER (PARTITION BY framework ORDER BY accuracy DESC NULLS LAST) AS rank_in_framework
FROM training_runs
WHERE status = 'succeeded'
  AND accuracy IS NOT NULL;

-- Running total of GPU hours
SELECT
    model_name,
    created_at,
    gpu_hours,
    SUM(gpu_hours) OVER (ORDER BY created_at) AS cumulative_gpu_hours
FROM training_runs
ORDER BY created_at;

-- Row number
SELECT
    ROW_NUMBER() OVER (ORDER BY accuracy DESC NULLS LAST) AS rank,
    model_name,
    accuracy,
    f1_score
FROM training_runs
WHERE status = 'succeeded';
```

### Step 9.4: CASE Statements

```sql
-- ====================
-- CASE STATEMENTS
-- ====================

-- Categorize models by accuracy
SELECT
    model_name,
    accuracy,
    CASE
        WHEN accuracy >= 0.95 THEN 'Excellent'
        WHEN accuracy >= 0.90 THEN 'Good'
        WHEN accuracy >= 0.80 THEN 'Fair'
        WHEN accuracy < 0.80 THEN 'Poor'
        ELSE 'Unknown'
    END AS performance_category
FROM training_runs
WHERE accuracy IS NOT NULL
ORDER BY accuracy DESC;

-- Categorize GPU usage
SELECT
    model_name,
    gpu_hours,
    CASE
        WHEN gpu_hours = 0 THEN 'CPU Only'
        WHEN gpu_hours < 10 THEN 'Light GPU Usage'
        WHEN gpu_hours < 50 THEN 'Moderate GPU Usage'
        ELSE 'Heavy GPU Usage'
    END AS gpu_category,
    CASE
        WHEN gpu_hours > 30 THEN '$$$ High Cost'
        WHEN gpu_hours > 10 THEN '$$ Medium Cost'
        ELSE '$ Low Cost'
    END AS cost_estimate
FROM training_runs
WHERE gpu_hours > 0
ORDER BY gpu_hours DESC;
```

---

## Part 10: Data Import/Export

### Step 10.1: Export to CSV

```sql
-- ====================
-- EXPORT TO CSV
-- ====================

-- Export all successful runs to CSV
\copy (SELECT model_name, framework, accuracy, gpu_hours, created_at FROM training_runs WHERE status = 'succeeded') TO '/tmp/successful_runs.csv' WITH CSV HEADER;

-- Export with custom delimiter
\copy (SELECT * FROM training_runs) TO '/tmp/all_runs.tsv' WITH (FORMAT csv, DELIMITER E'\t', HEADER);
```

### Step 10.2: Import from CSV

```bash
# Create a CSV file first
cat > /tmp/new_runs.csv << 'EOF'
model_name,framework,experiment_name,status,dataset,compute_target,parameters
test-model-1,pytorch,test-exp-1,queued,test-data,k8s-cpu,"{}"
test-model-2,tensorflow,test-exp-2,queued,test-data,k8s-cpu,"{}"
EOF
```

```sql
-- Import from CSV (from within psql)
\copy training_runs(model_name, framework, experiment_name, status, dataset, compute_target, parameters) FROM '/tmp/new_runs.csv' WITH CSV HEADER;
```

---

## Part 11: Performance and Optimization Preview

### Step 11.1: EXPLAIN ANALYZE

```sql
-- ====================
-- QUERY PERFORMANCE
-- ====================

-- See query execution plan
EXPLAIN SELECT * FROM training_runs WHERE gpu_hours > 20;

-- See actual execution time
EXPLAIN ANALYZE SELECT * FROM training_runs WHERE gpu_hours > 20;

-- Compare with and without index
EXPLAIN ANALYZE SELECT * FROM training_runs WHERE status = 'succeeded';
-- Should use idx_training_runs_status index
```

### Step 11.2: Table Statistics

```sql
-- Table size
SELECT pg_size_pretty(pg_total_relation_size('training_runs'));

-- Row count
SELECT COUNT(*) FROM training_runs;

-- Index usage
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan AS index_scans,
    idx_tup_read AS tuples_read,
    idx_tup_fetch AS tuples_fetched
FROM pg_stat_user_indexes
WHERE tablename = 'training_runs';
```

---

## Part 12: Cleanup and Best Practices

### Step 12.1: Data Retention Policy

```sql
-- ====================
-- DATA RETENTION
-- ====================

-- Create a data retention function (preview for later modules)
-- Delete old test/failed runs
BEGIN;

SELECT COUNT(*) FROM training_runs
WHERE (status = 'failed' AND created_at < NOW() - INTERVAL '90 days')
   OR (notes ILIKE '%test%' AND created_at < NOW() - INTERVAL '30 days');

DELETE FROM training_runs
WHERE (status = 'failed' AND created_at < NOW() - INTERVAL '90 days')
   OR (notes ILIKE '%test%' AND created_at < NOW() - INTERVAL '30 days');

COMMIT;
```

### Step 12.2: SQL Best Practices Summary

**DO**:
- ✅ Always use `WHERE` clause with UPDATE/DELETE
- ✅ Use transactions for multi-step operations
- ✅ Test queries with `SELECT` before `UPDATE`/`DELETE`
- ✅ Use `LIMIT` when exploring large tables
- ✅ Add indexes on frequently queried columns
- ✅ Use specific column names instead of `SELECT *`
- ✅ Use `EXPLAIN ANALYZE` to check query performance
- ✅ Use constraints to enforce data quality

**DON'T**:
- ❌ Never `UPDATE`/`DELETE` without `WHERE` (unless intentional)
- ❌ Don't use `SELECT *` in production code
- ❌ Don't store sensitive data in plain text
- ❌ Don't forget to backup before major operations
- ❌ Don't use `TRUNCATE` without understanding consequences

---

## Part 13: Hands-On Challenges

### Challenge 1: Data Analysis

Write queries to answer these questions:

1. What is the success rate for each framework?
2. Which compute target has the highest average GPU hours?
3. Find all models that ran longer than 1 day
4. Calculate the total cost if GPU hours cost $2.50/hour
5. Find experiments with multiple attempts

<details>
<summary>Solution Hints</summary>

```sql
-- 1. Success rate
SELECT
    framework,
    COUNT(*) FILTER (WHERE status = 'succeeded') * 100.0 / COUNT(*) AS success_rate
FROM training_runs
GROUP BY framework;

-- 2. Highest GPU usage
SELECT compute_target, AVG(gpu_hours)
FROM training_runs
GROUP BY compute_target
ORDER BY AVG(gpu_hours) DESC
LIMIT 1;

-- 3. Long runs
SELECT *
FROM training_runs
WHERE (completed_at - started_at) > INTERVAL '1 day';

-- 4. Total cost
SELECT SUM(gpu_hours) * 2.50 AS total_cost FROM training_runs;

-- 5. Multiple attempts
SELECT experiment_name, COUNT(*)
FROM training_runs
GROUP BY experiment_name
HAVING COUNT(*) > 1;
```
</details>

### Challenge 2: Data Manipulation

1. Insert a new training run for your favorite ML model
2. Update it from queued → running → succeeded
3. Calculate and update the F1 score from precision/recall
4. Export the final result to CSV

### Challenge 3: Cleanup

1. Find all runs older than 30 days with status 'queued'
2. Update them to 'cancelled' with appropriate notes
3. Delete any test runs (notes contain 'test')

---

## Part 14: Deliverables and Self-Assessment

### Deliverables

Submit the following in your repository:

```
ml-training-registry/
├── sql/
│   ├── 01_create_training_runs.sql
│   ├── 02_seed_training_runs.sql
│   ├── 03_crud_operations.sql
│   └── 04_analysis_queries.sql
├── screenshots/
│   ├── table_structure.png
│   ├── seed_data_verification.png
│   └── query_results.png
└── REFLECTION.md
```

### Reflection Questions

Write a 300-500 word reflection answering:

1. **Understanding**: Explain the purpose of each constraint you added
2. **Comparison**: What's the difference between DELETE and TRUNCATE?
3. **Integration**: How would you expose this data to downstream services (APIs, dashboards)?
4. **Design**: What improvements would you make to the schema?
5. **Challenges**: What was the most challenging part of this exercise?
6. **Production**: What additional features would a production ML registry need?

### Self-Assessment Checklist

- [ ] I can create tables with appropriate data types
- [ ] I understand PRIMARY KEY, UNIQUE, and CHECK constraints
- [ ] I can write SELECT queries with filtering and sorting
- [ ] I can use aggregate functions (COUNT, AVG, SUM, etc.)
- [ ] I can use GROUP BY and HAVING
- [ ] I can query JSONB data
- [ ] I can perform INSERT, UPDATE, DELETE operations
- [ ] I understand transactions (BEGIN/COMMIT/ROLLBACK)
- [ ] I can write safe UPDATE/DELETE queries with WHERE
- [ ] I can use EXPLAIN ANALYZE to check query performance
- [ ] I understand the difference between DELETE and TRUNCATE
- [ ] I can import/export data using \copy

---

## Summary and Key Takeaways

### What You Learned

✅ **Schema Design**:
- Table creation with appropriate data types
- Constraints (PRIMARY KEY, UNIQUE, CHECK, NOT NULL)
- Default values and generated columns
- JSONB for flexible metadata storage

✅ **CRUD Operations**:
- **CREATE**: INSERT data with single and bulk operations
- **READ**: SELECT queries with filtering, sorting, aggregation
- **UPDATE**: Modify records safely with WHERE clauses
- **DELETE**: Remove records with proper safety measures

✅ **Advanced SQL**:
- JSONB queries for flexible data
- Date/time operations and intervals
- Aggregate functions and GROUP BY
- Window functions (preview)
- Common Table Expressions (preview)

✅ **Best Practices**:
- Always use WHERE with UPDATE/DELETE
- Use transactions for multi-step operations
- Test with SELECT before UPDATE/DELETE
- Use indexes for performance
- Enforce data quality with constraints

### Next Steps

- **Exercise 02**: Database Design for ML Model Registry - Learn normalization, foreign keys, and multi-table relationships
- **Exercise 03**: Advanced SQL Joins - Master INNER JOIN, LEFT JOIN, and complex queries
- **Exercise 04**: SQLAlchemy ORM Integration - Connect Python applications to PostgreSQL
- **Exercise 05**: Optimization & Indexing - Learn to optimize queries and design indexes

---

## Additional Resources

- [PostgreSQL Official Documentation](https://www.postgresql.org/docs/)
- [PostgreSQL Tutorial](https://www.postgresqltutorial.com/)
- [SQL Style Guide](https://www.sqlstyle.guide/)
- [JSONB Performance Tips](https://www.postgresql.org/docs/current/datatype-json.html)
- [Explain Analyze Visualization](https://explain.depesz.com/)

---

**Exercise Complete!** 🎉

You now have a solid foundation in SQL fundamentals and CRUD operations for ML infrastructure. You've built a production-ready training registry that can track hundreds of experiments with rich metadata.

**Estimated Time Spent**: 3-4 hours
**Difficulty**: Beginner → Intermediate
**Learning Objectives Achieved**: ✅ All objectives met
**Ready for**: Exercise 02 - Database Design for ML Model Registry
