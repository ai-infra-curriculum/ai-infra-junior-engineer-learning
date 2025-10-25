# Lecture 02: Database Design & Normalization

## Table of Contents
1. [Introduction](#introduction)
2. [Database Design Principles](#database-design-principles)
3. [Entity-Relationship (ER) Modeling](#entity-relationship-er-modeling)
4. [Types of Relationships](#types-of-relationships)
5. [From ER Diagram to Tables](#from-er-diagram-to-tables)
6. [Data Normalization](#data-normalization)
7. [First Normal Form (1NF)](#first-normal-form-1nf)
8. [Second Normal Form (2NF)](#second-normal-form-2nf)
9. [Third Normal Form (3NF)](#third-normal-form-3nf)
10. [Boyce-Codd Normal Form (BCNF)](#boyce-codd-normal-form-bcnf)
11. [Denormalization](#denormalization)
12. [Designing ML Database Schemas](#designing-ml-database-schemas)
13. [Schema Migration Strategies](#schema-migration-strategies)
14. [Best Practices](#best-practices)
15. [Summary and Key Takeaways](#summary-and-key-takeaways)

## Introduction

Good database design is crucial for building scalable, maintainable, and efficient applications. Poor design leads to data redundancy, inconsistencies, and performance problems. This lecture teaches you the principles and techniques for designing robust database schemas, with a focus on normalization and ML use cases.

### Learning Objectives

By the end of this lecture, you will:
- Understand database design principles
- Create Entity-Relationship diagrams
- Identify and implement different relationship types
- Apply normalization forms (1NF through BCNF)
- Know when to denormalize for performance
- Design database schemas for ML systems
- Plan and execute schema migrations

### Prerequisites
- Lecture 01: Database Fundamentals & SQL Basics
- Understanding of relational database concepts
- Basic SQL knowledge (CREATE, SELECT, etc.)

### Estimated Time
4-5 hours (including design exercises)

## Database Design Principles

### 1. Data Integrity

Ensure data is accurate and consistent:

**Example of Poor Integrity:**
```
Users table:
user_id | email             | email_verified
--------|-------------------|---------------
1       | alice@example.com | true
1       | bob@example.com   | false  ← Same user_id, different email!
```

**Good Integrity:**
```sql
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY,           -- Unique
    email VARCHAR(255) NOT NULL UNIQUE,    -- Must exist, must be unique
    email_verified BOOLEAN DEFAULT FALSE
);
```

### 2. Minimize Redundancy

Don't store the same data in multiple places:

**Bad (Redundant):**
```
experiments table:
exp_id | model_name | model_framework | model_version | accuracy
-------|------------|-----------------|---------------|----------
1      | BERT-base  | PyTorch         | 1.0.0         | 0.92
2      | BERT-base  | PyTorch         | 1.0.0         | 0.93
3      | BERT-base  | PyTorch         | 1.0.0         | 0.94
       ↑ Repeated model info in every experiment
```

**Good (Normalized):**
```
models table:
model_id | name      | framework | version
---------|-----------|-----------|--------
1        | BERT-base | PyTorch   | 1.0.0

experiments table:
exp_id | model_id | accuracy
-------|----------|----------
1      | 1        | 0.92
2      | 1        | 0.93
3      | 1        | 0.94
       ↑ Reference to model, no duplication
```

### 3. Logical Organization

Group related data together:

```sql
-- GOOD: Related data in one table
CREATE TABLE user_profiles (
    user_id INTEGER PRIMARY KEY,
    username VARCHAR(50),
    email VARCHAR(255),
    full_name VARCHAR(100),
    created_at TIMESTAMP
);

-- AVOID: Splitting unnecessarily
CREATE TABLE usernames (user_id INT, username VARCHAR(50));
CREATE TABLE emails (user_id INT, email VARCHAR(255));
CREATE TABLE names (user_id INT, full_name VARCHAR(100));
```

### 4. Scalability

Design for growth:

```sql
-- Use appropriate data types
CREATE TABLE predictions (
    prediction_id BIGINT PRIMARY KEY,  -- Handles billions of records
    model_id INTEGER,
    confidence DECIMAL(5,4),           -- Precise numbers
    created_at TIMESTAMP
);

-- Add indexes for performance
CREATE INDEX idx_predictions_model_id ON predictions(model_id);
CREATE INDEX idx_predictions_created_at ON predictions(created_at);
```

### 5. Flexibility

Design for future changes:

```sql
-- Flexible: Use separate table for tags
CREATE TABLE model_tags (
    tag_id INTEGER PRIMARY KEY,
    model_id INTEGER,
    tag_name VARCHAR(50),
    FOREIGN KEY (model_id) REFERENCES models(model_id)
);
-- Easy to add/remove tags without changing schema

-- Inflexible: Store as comma-separated string
CREATE TABLE models (
    model_id INTEGER PRIMARY KEY,
    tags VARCHAR(255)  -- 'nlp,transformer,bert'
    -- Hard to query, maintain, and modify
);
```

## Entity-Relationship (ER) Modeling

### What is an ER Diagram?

An **Entity-Relationship diagram** visually represents the structure of a database:
- **Entities**: Things we want to store (tables)
- **Attributes**: Properties of entities (columns)
- **Relationships**: How entities connect

### ER Diagram Components

**Entities (Rectangles):**
```
┌─────────────┐
│   Models    │  ← Entity
└─────────────┘
```

**Attributes (Ovals):**
```
    ┌──────────┐
    │model_name│  ← Attribute
    └────┬─────┘
         │
    ┌────┴────┐
    │ Models  │
    └─────────┘
```

**Primary Key (Underlined):**
```
model_id (underlined) = primary key
```

**Relationships (Diamonds):**
```
┌─────────┐       ┌──────────┐       ┌────────────┐
│ Models  │───────│  trains  │───────│Experiments │
└─────────┘       └──────────┘       └────────────┘
```

### Example: ML Model Registry ER Diagram

```
                  1                     N
┌─────────┐              ┌──────────────┐
│ Models  │──────────────│ Experiments  │
└─────────┘   has many   └──────────────┘
│                         │
│ model_id (PK)           │ experiment_id (PK)
│ name                    │ model_id (FK)
│ framework               │ accuracy
│ version                 │ created_at
│ created_at              │
│                         │
│         1               │        N
│         │               │        │
│         └───────────────┴────────┘
│                 runs
│
│              1
│              │
│              │
│         ┌────┴──────┐
│         │           │
│    ┌────┴────┐  ┌──┴──────────┐
│    │ Users   │  │ Predictions │
│    └─────────┘  └─────────────┘
│    │            │
│    │user_id(PK) │ prediction_id (PK)
│    │username    │ model_id (FK)
│    │email       │ input_data
│                 │ prediction
│                 │ created_at
└─────────────────┘
      created by
```

### Cardinality Notations

**One-to-One (1:1)**
```
User ────── Profile
  1            1
```

**One-to-Many (1:N)**
```
Model ────── Experiments
  1              N
```

**Many-to-Many (M:N)**
```
Models ────── Tags
  M              N
```

## Types of Relationships

### 1. One-to-One (1:1)

One entity relates to exactly one other entity.

**Example: User and User Profile**

```sql
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE
);

CREATE TABLE user_profiles (
    profile_id INTEGER PRIMARY KEY,
    user_id INTEGER UNIQUE NOT NULL,  -- UNIQUE makes it 1:1
    bio TEXT,
    avatar_url VARCHAR(255),
    preferences JSON,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
```

**When to use:**
- Separate sensitive data (e.g., billing info)
- Optional extended information
- Large binary data (photos, documents)

### 2. One-to-Many (1:N)

One entity relates to many other entities.

**Example: Model has Many Experiments**

```sql
CREATE TABLE models (
    model_id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

CREATE TABLE experiments (
    experiment_id INTEGER PRIMARY KEY,
    model_id INTEGER NOT NULL,  -- Many experiments → one model
    accuracy DECIMAL(5,4),
    created_at TIMESTAMP,
    FOREIGN KEY (model_id) REFERENCES models(model_id)
);
```

**Visual:**
```
Model (id=1, name='BERT')
    ├─ Experiment (id=101, model_id=1, accuracy=0.92)
    ├─ Experiment (id=102, model_id=1, accuracy=0.93)
    └─ Experiment (id=103, model_id=1, accuracy=0.94)
```

**When to use:**
- Parent-child relationships
- Most common relationship type
- Examples: User→Orders, Model→Predictions, Dataset→Samples

### 3. Many-to-Many (M:N)

Many entities relate to many other entities.

**Example: Models and Tags**

**Problem:** Can't directly represent M:N in relational databases.

**Solution:** Use a **junction table** (also called: bridge table, linking table, associative table)

```sql
CREATE TABLE models (
    model_id INTEGER PRIMARY KEY,
    name VARCHAR(100)
);

CREATE TABLE tags (
    tag_id INTEGER PRIMARY KEY,
    tag_name VARCHAR(50) UNIQUE
);

-- Junction table
CREATE TABLE model_tags (
    model_id INTEGER,
    tag_id INTEGER,
    PRIMARY KEY (model_id, tag_id),  -- Composite key
    FOREIGN KEY (model_id) REFERENCES models(model_id),
    FOREIGN KEY (tag_id) REFERENCES tags(tag_id)
);
```

**Visual:**
```
Models:                      Tags:
1: BERT                      A: NLP
2: ResNet                    B: Vision
3: GPT-2                     C: Transformer

model_tags (junction):
model_id | tag_id
---------|--------
1        | A       ← BERT has tag NLP
1        | C       ← BERT has tag Transformer
2        | B       ← ResNet has tag Vision
3        | A       ← GPT-2 has tag NLP
3        | C       ← GPT-2 has tag Transformer
```

**Query example:**
```sql
-- Get all tags for BERT
SELECT t.tag_name
FROM tags t
JOIN model_tags mt ON t.tag_id = mt.tag_id
JOIN models m ON mt.model_id = m.model_id
WHERE m.name = 'BERT';

-- Result: NLP, Transformer
```

**When to use:**
- Students↔Courses
- Products↔Categories
- Models↔Tags
- Users↔Roles

## From ER Diagram to Tables

### Step 1: Each Entity → Table

```
Entity: Model
Attributes: model_id, name, framework

→

CREATE TABLE models (
    model_id INTEGER PRIMARY KEY,
    name VARCHAR(100),
    framework VARCHAR(50)
);
```

### Step 2: One-to-Many → Foreign Key

```
Model (1) → (N) Experiments

→

CREATE TABLE experiments (
    experiment_id INTEGER PRIMARY KEY,
    model_id INTEGER,  -- Foreign key
    accuracy DECIMAL(5,4),
    FOREIGN KEY (model_id) REFERENCES models(model_id)
);
```

### Step 3: Many-to-Many → Junction Table

```
Models (M) ↔ (N) Tags

→

CREATE TABLE model_tags (
    model_id INTEGER,
    tag_id INTEGER,
    PRIMARY KEY (model_id, tag_id),
    FOREIGN KEY (model_id) REFERENCES models(model_id),
    FOREIGN KEY (tag_id) REFERENCES tags(tag_id)
);
```

### Complete Example: ML Platform Schema

```sql
-- Users
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Models (1:N with Experiments, M:N with Tags)
CREATE TABLE models (
    model_id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    framework VARCHAR(50),
    created_by INTEGER,  -- FK to users
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(user_id)
);

-- Experiments (N:1 with Models)
CREATE TABLE experiments (
    experiment_id INTEGER PRIMARY KEY,
    model_id INTEGER NOT NULL,
    accuracy DECIMAL(5,4),
    loss DECIMAL(10,6),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (model_id) REFERENCES models(model_id)
);

-- Tags
CREATE TABLE tags (
    tag_id INTEGER PRIMARY KEY,
    tag_name VARCHAR(50) UNIQUE NOT NULL
);

-- Model-Tags junction (M:N)
CREATE TABLE model_tags (
    model_id INTEGER,
    tag_id INTEGER,
    PRIMARY KEY (model_id, tag_id),
    FOREIGN KEY (model_id) REFERENCES models(model_id),
    FOREIGN KEY (tag_id) REFERENCES tags(tag_id)
);
```

## Data Normalization

### What is Normalization?

**Normalization** is the process of organizing data to:
1. Eliminate redundancy
2. Ensure data dependencies make sense
3. Reduce anomalies during INSERT, UPDATE, DELETE

### Why Normalize?

**Problems with Unnormalized Data:**

```
experiments_bad table:
┌────┬───────────┬──────────┬───────────┬──────────┬─────────────┐
│ id │model_name │ framework│ dataset   │ accuracy │ model_author│
├────┼───────────┼──────────┼───────────┼──────────┼─────────────┤
│ 1  │BERT-base  │ PyTorch  │ IMDB      │ 0.92     │ Alice       │
│ 2  │BERT-base  │ PyTorch  │ SST-2     │ 0.88     │ Alice       │
│ 3  │ResNet-50  │TensorFlow│ ImageNet  │ 0.76     │ Bob         │
└────┴───────────┴──────────┴───────────┴──────────┴─────────────┘
```

**Issues:**

1. **Update Anomaly**: Change BERT's framework requires updating multiple rows
2. **Insertion Anomaly**: Can't add a model without an experiment
3. **Deletion Anomaly**: Deleting all ResNet experiments loses model info
4. **Space Waste**: Duplicate data (BERT-base repeated)

### Normalization Forms Overview

- **1NF**: Atomic values, no repeating groups
- **2NF**: 1NF + no partial dependencies
- **3NF**: 2NF + no transitive dependencies
- **BCNF**: Stricter version of 3NF

## First Normal Form (1NF)

### Rules

1. Each column contains atomic (indivisible) values
2. Each column contains values of the same type
3. Each column has a unique name
4. Order doesn't matter

### Violations

**Violation 1: Non-atomic values**

```sql
-- ❌ VIOLATES 1NF (tags is a list)
CREATE TABLE models_bad (
    model_id INTEGER,
    name VARCHAR(100),
    tags VARCHAR(255)  -- 'nlp,transformer,bert'
);
```

**Fix:**
```sql
-- ✓ 1NF Compliant
CREATE TABLE models (
    model_id INTEGER PRIMARY KEY,
    name VARCHAR(100)
);

CREATE TABLE model_tags (
    model_id INTEGER,
    tag VARCHAR(50),
    PRIMARY KEY (model_id, tag)
);
```

**Violation 2: Repeating groups**

```sql
-- ❌ VIOLATES 1NF (repeating columns)
CREATE TABLE experiments_bad (
    model_id INTEGER,
    metric1_name VARCHAR(50),
    metric1_value DECIMAL(5,4),
    metric2_name VARCHAR(50),
    metric2_value DECIMAL(5,4),
    metric3_name VARCHAR(50),
    metric3_value DECIMAL(5,4)
);
```

**Fix:**
```sql
-- ✓ 1NF Compliant
CREATE TABLE experiment_metrics (
    experiment_id INTEGER,
    metric_name VARCHAR(50),
    metric_value DECIMAL(5,4),
    PRIMARY KEY (experiment_id, metric_name)
);
```

### 1NF Example

**Before 1NF:**
```
┌────────┬───────────────┬─────────────────────┐
│model_id│ name          │ frameworks          │
├────────┼───────────────┼─────────────────────┤
│ 1      │ BERT          │ PyTorch,TensorFlow  │  ← Not atomic
│ 2      │ ResNet        │ TensorFlow          │
└────────┴───────────────┴─────────────────────┘
```

**After 1NF:**
```
models:
┌────────┬───────────┐
│model_id│ name      │
├────────┼───────────┤
│ 1      │ BERT      │
│ 2      │ ResNet    │
└────────┴───────────┘

model_frameworks:
┌────────┬────────────┐
│model_id│ framework  │
├────────┼────────────┤
│ 1      │ PyTorch    │
│ 1      │TensorFlow  │
│ 2      │TensorFlow  │
└────────┴────────────┘
```

## Second Normal Form (2NF)

### Rules

1. Must be in 1NF
2. No **partial dependencies** on composite keys

### What is Partial Dependency?

When a non-key attribute depends on only part of a composite primary key.

### Example Violation

```sql
-- Composite key: (experiment_id, dataset_id)
CREATE TABLE experiment_datasets_bad (
    experiment_id INTEGER,
    dataset_id INTEGER,
    dataset_name VARCHAR(100),  -- ❌ Depends only on dataset_id
    dataset_size INTEGER,       -- ❌ Depends only on dataset_id
    accuracy DECIMAL(5,4),      -- ✓ Depends on both
    PRIMARY KEY (experiment_id, dataset_id)
);
```

**Problem:** `dataset_name` and `dataset_size` depend only on `dataset_id`, not on the full key.

### Fix: Separate Tables

```sql
-- ✓ 2NF Compliant

-- Datasets (dataset attributes separate)
CREATE TABLE datasets (
    dataset_id INTEGER PRIMARY KEY,
    dataset_name VARCHAR(100),
    dataset_size INTEGER
);

-- Experiment-Dataset relationship
CREATE TABLE experiment_datasets (
    experiment_id INTEGER,
    dataset_id INTEGER,
    accuracy DECIMAL(5,4),  -- Depends on both keys
    PRIMARY KEY (experiment_id, dataset_id),
    FOREIGN KEY (dataset_id) REFERENCES datasets(dataset_id)
);
```

### 2NF Example

**Before 2NF:**
```
experiment_results (composite key: experiment_id, metric_name):
┌──────────────┬─────────────┬──────────────┬─────────┐
│experiment_id │ metric_name │ metric_type  │ value   │
├──────────────┼─────────────┼──────────────┼─────────┤
│ 1            │ accuracy    │ performance  │ 0.92    │
│ 1            │ f1_score    │ performance  │ 0.88    │
│ 2            │ accuracy    │ performance  │ 0.90    │
└──────────────┴─────────────┴──────────────┴─────────┘
               ↑ metric_type depends only on metric_name (partial dependency)
```

**After 2NF:**
```
metrics:
┌─────────────┬──────────────┐
│ metric_name │ metric_type  │
├─────────────┼──────────────┤
│ accuracy    │ performance  │
│ f1_score    │ performance  │
│ loss        │ training     │
└─────────────┴──────────────┘

experiment_results:
┌──────────────┬─────────────┬─────────┐
│experiment_id │ metric_name │ value   │
├──────────────┼─────────────┼─────────┤
│ 1            │ accuracy    │ 0.92    │
│ 1            │ f1_score    │ 0.88    │
│ 2            │ accuracy    │ 0.90    │
└──────────────┴─────────────┴─────────┘
```

## Third Normal Form (3NF)

### Rules

1. Must be in 2NF
2. No **transitive dependencies**

### What is Transitive Dependency?

When a non-key attribute depends on another non-key attribute.

```
A → B → C  (A determines B, B determines C)
Therefore: A → C transitively
```

### Example Violation

```sql
-- ❌ Violates 3NF
CREATE TABLE models_bad (
    model_id INTEGER PRIMARY KEY,
    name VARCHAR(100),
    framework VARCHAR(50),
    framework_creator VARCHAR(100),  -- ❌ Depends on framework, not model_id
    framework_year INTEGER           -- ❌ Depends on framework, not model_id
);

-- Transitive dependency:
-- model_id → framework → framework_creator
```

**Problem:** If we change PyTorch's creator, we must update all PyTorch models.

### Fix: Separate Framework Info

```sql
-- ✓ 3NF Compliant

CREATE TABLE frameworks (
    framework_name VARCHAR(50) PRIMARY KEY,
    creator VARCHAR(100),
    release_year INTEGER
);

CREATE TABLE models (
    model_id INTEGER PRIMARY KEY,
    name VARCHAR(100),
    framework VARCHAR(50),
    FOREIGN KEY (framework) REFERENCES frameworks(framework_name)
);
```

### 3NF Example

**Before 3NF:**
```
experiments:
┌────────────┬──────────┬────────────┬─────────────────┬─────────────┐
│experiment_id│ model_id │ model_name │ model_framework │ accuracy    │
├────────────┼──────────┼────────────┼─────────────────┼─────────────┤
│ 1          │ 10       │ BERT-base  │ PyTorch         │ 0.92        │
│ 2          │ 10       │ BERT-base  │ PyTorch         │ 0.93        │
└────────────┴──────────┴────────────┴─────────────────┴─────────────┘
            ↑ experiment_id → model_id → model_name (transitive)
```

**After 3NF:**
```
models:
┌──────────┬────────────┬─────────────────┐
│ model_id │ model_name │ model_framework │
├──────────┼────────────┼─────────────────┤
│ 10       │ BERT-base  │ PyTorch         │
└──────────┴────────────┴─────────────────┘

experiments:
┌────────────┬──────────┬──────────┐
│experiment_id│ model_id │ accuracy │
├────────────┼──────────┼──────────┤
│ 1          │ 10       │ 0.92     │
│ 2          │ 10       │ 0.93     │
└────────────┴──────────┴──────────┘
```

## Boyce-Codd Normal Form (BCNF)

### Rules

1. Must be in 3NF
2. For every functional dependency X → Y, X must be a superkey

**Simplified:** Every determinant must be a candidate key.

### Example (Rare Edge Case)

```sql
-- Student-Course-Instructor
-- Rules:
-- - Each student takes one course from one instructor
-- - Each instructor teaches only one course
-- - Multiple instructors can teach the same course

CREATE TABLE enrollment (
    student_id INTEGER,
    course VARCHAR(50),
    instructor VARCHAR(50),
    PRIMARY KEY (student_id, course),
    -- Functional dependency: instructor → course
    -- But instructor is not a superkey
    -- VIOLATES BCNF
);
```

**Fix:**
```sql
-- Split into two tables
CREATE TABLE instructors (
    instructor VARCHAR(50) PRIMARY KEY,
    course VARCHAR(50)
);

CREATE TABLE enrollment (
    student_id INTEGER,
    instructor VARCHAR(50),
    PRIMARY KEY (student_id, instructor),
    FOREIGN KEY (instructor) REFERENCES instructors(instructor)
);
```

**Note:** BCNF is rarely needed in practice. 3NF is usually sufficient.

## Denormalization

### What is Denormalization?

Intentionally introducing redundancy to improve read performance.

### When to Denormalize?

1. **Read-heavy workloads**: More reads than writes
2. **Performance critical**: Response time matters more than storage
3. **Complex joins**: Queries join many tables
4. **Reporting/Analytics**: Pre-computed aggregates

### Example: Prediction Logging

**Normalized (3NF):**
```sql
-- Fast writes, slow reads
CREATE TABLE predictions (
    prediction_id BIGINT PRIMARY KEY,
    model_id INTEGER,
    user_id INTEGER,
    prediction TEXT,
    created_at TIMESTAMP,
    FOREIGN KEY (model_id) REFERENCES models(model_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Query requires joins
SELECT p.prediction, m.name, u.username
FROM predictions p
JOIN models m ON p.model_id = m.model_id
JOIN users u ON p.user_id = u.user_id
WHERE p.created_at > '2024-10-01';
```

**Denormalized (for reads):**
```sql
-- Duplicate model_name and username for faster queries
CREATE TABLE predictions_denorm (
    prediction_id BIGINT PRIMARY KEY,
    model_id INTEGER,
    model_name VARCHAR(100),     -- ← Redundant (from models table)
    user_id INTEGER,
    username VARCHAR(50),        -- ← Redundant (from users table)
    prediction TEXT,
    created_at TIMESTAMP
);

-- No joins needed!
SELECT prediction, model_name, username
FROM predictions_denorm
WHERE created_at > '2024-10-01';
```

**Tradeoffs:**
- ✅ **Faster reads** (no joins)
- ✅ **Simpler queries**
- ❌ **More storage** (duplicate data)
- ❌ **Update complexity** (must update multiple places)
- ❌ **Data inconsistency risk**

### Materialized Views (Better Alternative)

```sql
-- PostgreSQL materialized view
CREATE MATERIALIZED VIEW prediction_summary AS
SELECT
    p.prediction_id,
    p.prediction,
    m.name AS model_name,
    u.username,
    p.created_at
FROM predictions p
JOIN models m ON p.model_id = m.model_id
JOIN users u ON p.user_id = u.user_id;

-- Refresh periodically
REFRESH MATERIALIZED VIEW prediction_summary;

-- Query is fast
SELECT * FROM prediction_summary
WHERE created_at > '2024-10-01';
```

**Benefits:**
- Original tables stay normalized
- View is denormalized for performance
- Automatic updates (can be scheduled)

## Designing ML Database Schemas

### Use Case 1: ML Model Registry

```sql
-- Core tables
CREATE TABLE models (
    model_id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    framework VARCHAR(50),
    architecture VARCHAR(100),
    created_by INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) CHECK (status IN ('training', 'ready', 'deployed', 'archived')),
    FOREIGN KEY (created_by) REFERENCES users(user_id)
);

CREATE TABLE model_versions (
    version_id SERIAL PRIMARY KEY,
    model_id INTEGER NOT NULL,
    version_number VARCHAR(20) NOT NULL,
    model_path VARCHAR(255),
    accuracy DECIMAL(5,4),
    precision_score DECIMAL(5,4),
    recall_score DECIMAL(5,4),
    f1_score DECIMAL(5,4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (model_id) REFERENCES models(model_id),
    UNIQUE (model_id, version_number)
);

CREATE TABLE model_metrics (
    metric_id SERIAL PRIMARY KEY,
    version_id INTEGER NOT NULL,
    metric_name VARCHAR(50),
    metric_value DECIMAL(10,6),
    FOREIGN KEY (version_id) REFERENCES model_versions(version_id)
);
```

### Use Case 2: Experiment Tracking

```sql
CREATE TABLE experiments (
    experiment_id SERIAL PRIMARY KEY,
    experiment_name VARCHAR(100),
    model_id INTEGER,
    dataset_id INTEGER,
    created_by INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    status VARCHAR(20),
    FOREIGN KEY (model_id) REFERENCES models(model_id),
    FOREIGN KEY (created_by) REFERENCES users(user_id)
);

CREATE TABLE experiment_hyperparameters (
    experiment_id INTEGER,
    param_name VARCHAR(50),
    param_value TEXT,
    PRIMARY KEY (experiment_id, param_name),
    FOREIGN KEY (experiment_id) REFERENCES experiments(experiment_id)
);

CREATE TABLE experiment_results (
    result_id SERIAL PRIMARY KEY,
    experiment_id INTEGER,
    epoch INTEGER,
    metric_name VARCHAR(50),
    metric_value DECIMAL(10,6),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (experiment_id) REFERENCES experiments(experiment_id)
);
```

### Use Case 3: Dataset Management

```sql
CREATE TABLE datasets (
    dataset_id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    dataset_type VARCHAR(50),  -- 'training', 'validation', 'test'
    size_bytes BIGINT,
    num_samples INTEGER,
    storage_path VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE dataset_splits (
    split_id SERIAL PRIMARY KEY,
    dataset_id INTEGER,
    split_name VARCHAR(20),  -- 'train', 'val', 'test'
    split_percentage DECIMAL(5,2),
    num_samples INTEGER,
    FOREIGN KEY (dataset_id) REFERENCES datasets(dataset_id)
);

CREATE TABLE dataset_features (
    feature_id SERIAL PRIMARY KEY,
    dataset_id INTEGER,
    feature_name VARCHAR(100),
    data_type VARCHAR(50),
    is_nullable BOOLEAN,
    FOREIGN KEY (dataset_id) REFERENCES datasets(dataset_id)
);
```

## Schema Migration Strategies

### 1. Version Control Your Schema

```sql
-- migrations/001_create_models_table.sql
CREATE TABLE models (
    model_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

-- migrations/002_add_framework_column.sql
ALTER TABLE models
ADD COLUMN framework VARCHAR(50);

-- migrations/003_add_accuracy_column.sql
ALTER TABLE models
ADD COLUMN accuracy DECIMAL(5,4);
```

### 2. Use Migration Tools

**Alembic (Python):**
```python
# alembic/versions/001_create_models.py
def upgrade():
    op.create_table(
        'models',
        sa.Column('model_id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(100), nullable=False)
    )

def downgrade():
    op.drop_table('models')
```

**Flyway (Java):**
```sql
-- V1__create_models_table.sql
CREATE TABLE models (
    model_id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);
```

### 3. Safe Migration Practices

```sql
-- ❌ DANGEROUS: Can't roll back
ALTER TABLE models DROP COLUMN old_column;

-- ✓ SAFER: Multi-step migration
-- Step 1: Add new column
ALTER TABLE models ADD COLUMN new_column VARCHAR(100);

-- Step 2: Migrate data
UPDATE models SET new_column = old_column;

-- Step 3: (Later) Drop old column
-- ALTER TABLE models DROP COLUMN old_column;
```

### 4. Zero-Downtime Migrations

```sql
-- Add column with default (instant in most databases)
ALTER TABLE models
ADD COLUMN status VARCHAR(20) DEFAULT 'active';

-- Create index concurrently (PostgreSQL)
CREATE INDEX CONCURRENTLY idx_models_status ON models(status);

-- Add foreign key with NOT VALID (PostgreSQL)
ALTER TABLE experiments
ADD CONSTRAINT fk_model
FOREIGN KEY (model_id) REFERENCES models(model_id)
NOT VALID;

-- Validate later (can be done during low traffic)
ALTER TABLE experiments
VALIDATE CONSTRAINT fk_model;
```

## Best Practices

### 1. Name Things Clearly

```sql
-- GOOD
CREATE TABLE models (...);
CREATE TABLE model_versions (...);
CREATE TABLE experiment_results (...);

-- AVOID
CREATE TABLE tbl1 (...);
CREATE TABLE data (...);
CREATE TABLE temp_stuff (...);
```

### 2. Use Appropriate Data Types

```sql
-- GOOD
model_id BIGINT           -- Can handle billions of records
accuracy DECIMAL(5,4)     -- Precise: 0.9234
created_at TIMESTAMP      -- Date and time
is_active BOOLEAN         -- True/False

-- AVOID
model_id VARCHAR(50)      -- Waste of space, slower
accuracy VARCHAR(10)      -- Can't do math operations
created_at VARCHAR(50)    -- Can't do date operations
is_active VARCHAR(5)      -- 'true' vs TRUE vs 1 confusion
```

### 3. Document Your Schema

```sql
-- Add comments
COMMENT ON TABLE models IS 'Registry of all ML models';
COMMENT ON COLUMN models.accuracy IS 'Model accuracy on test set (0-1)';

-- Or in migration files
-- Migration: Add model versioning
-- Purpose: Track multiple versions of the same model
-- Author: Alice
-- Date: 2024-10-18
```

### 4. Plan for Auditing

```sql
CREATE TABLE models (
    model_id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    created_by INTEGER,           -- Who created?
    created_at TIMESTAMP,         -- When created?
    updated_by INTEGER,           -- Who last updated?
    updated_at TIMESTAMP,         -- When last updated?
    deleted_at TIMESTAMP          -- Soft delete (NULL = not deleted)
);
```

### 5. Index Strategic Columns

```sql
-- Index foreign keys
CREATE INDEX idx_experiments_model_id ON experiments(model_id);

-- Index frequently queried columns
CREATE INDEX idx_models_framework ON models(framework);
CREATE INDEX idx_predictions_created_at ON predictions(created_at);

-- Composite index for common query pattern
CREATE INDEX idx_models_status_accuracy ON models(status, accuracy);
```

## Summary and Key Takeaways

### Core Concepts

1. **ER Diagrams** visually represent database structure
2. **Relationships** connect entities (1:1, 1:N, M:N)
3. **Normalization** reduces redundancy and anomalies
4. **Denormalization** trades redundancy for performance

### Normalization Forms

| Form | Rule | Purpose |
|------|------|---------|
| 1NF  | Atomic values | No repeating groups |
| 2NF  | No partial dependencies | Depends on full key |
| 3NF  | No transitive dependencies | Non-keys don't depend on non-keys |
| BCNF | Determinants are keys | Stricter 3NF |

### Design Principles

1. **Start normalized** (3NF)
2. **Denormalize only when needed** (with evidence)
3. **Use foreign keys** for referential integrity
4. **Index strategically** for query performance
5. **Version control** your schema
6. **Plan migrations** carefully

### ML-Specific Patterns

- **Model Registry**: Models + Versions + Metrics
- **Experiment Tracking**: Experiments + Hyperparameters + Results
- **Dataset Management**: Datasets + Splits + Features
- **Prediction Logging**: Predictions + Models + Users

### Next Steps

In the next lecture, we'll cover:
- Advanced SQL queries (JOINs, subqueries, CTEs)
- Aggregations and GROUP BY
- Window functions
- Query optimization techniques
- Indexing strategies
- Query execution plans

---

**Estimated Study Time:** 4-5 hours
**Hands-on Practice:** Complete Exercise 02: Database Design
**Assessment:** Quiz questions cover ER diagrams and normalization
