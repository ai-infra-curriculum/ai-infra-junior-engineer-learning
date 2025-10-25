# Lecture 01: Database Fundamentals & SQL Basics

## Table of Contents
1. [Introduction](#introduction)
2. [What is a Database?](#what-is-a-database)
3. [Types of Databases](#types-of-databases)
4. [Relational Database Concepts](#relational-database-concepts)
5. [Introduction to SQL](#introduction-to-sql)
6. [Setting Up Your Database Environment](#setting-up-your-database-environment)
7. [Creating Databases and Tables](#creating-databases-and-tables)
8. [Basic SQL Queries (SELECT)](#basic-sql-queries-select)
9. [Filtering Data (WHERE)](#filtering-data-where)
10. [Sorting and Limiting Results](#sorting-and-limiting-results)
11. [Inserting Data](#inserting-data)
12. [Updating Data](#updating-data)
13. [Deleting Data](#deleting-data)
14. [Databases in ML Infrastructure](#databases-in-ml-infrastructure)
15. [Best Practices](#best-practices)
16. [Summary and Key Takeaways](#summary-and-key-takeaways)

## Introduction

Databases are the backbone of modern applications, storing and managing the data that powers everything from web applications to machine learning systems. For AI/ML infrastructure, databases play a critical role in storing training data, model metadata, experiment results, and production metrics.

This lecture introduces you to database fundamentals and SQL (Structured Query Language), the standard language for interacting with relational databases.

### Learning Objectives

By the end of this lecture, you will:
- Understand what databases are and why they're essential
- Distinguish between different types of databases
- Comprehend relational database concepts (tables, rows, columns, keys)
- Write basic SQL queries to retrieve data
- Filter, sort, and limit query results
- Insert, update, and delete data
- Apply database concepts to ML infrastructure scenarios
- Follow SQL best practices

### Prerequisites
- Basic programming knowledge (Python recommended)
- Command-line proficiency
- Understanding of data structures (arrays, dictionaries)

### Estimated Time
4-5 hours (including hands-on practice)

## What is a Database?

### Definition

A **database** is an organized collection of structured data stored electronically. Databases are designed to:
- Store large amounts of data efficiently
- Retrieve data quickly
- Maintain data integrity and consistency
- Support concurrent access by multiple users
- Provide data security and backup capabilities

### Why Use Databases?

**Without databases:**
```python
# Storing data in files (problematic!)
import json

# Save data
with open('models.json', 'w') as f:
    json.dump({"model1": {...}, "model2": {...}}, f)

# Problems:
# - No concurrent access control
# - Difficult to query efficiently
# - No data integrity guarantees
# - Hard to scale
# - No transaction support
```

**With databases:**
```sql
-- Efficient, scalable, concurrent access
SELECT * FROM models WHERE accuracy > 0.9;
-- Instant results from millions of records!
```

### Key Advantages of Databases

1. **Data Integrity**: Enforce rules and constraints
2. **Concurrency**: Multiple users can access simultaneously
3. **Scalability**: Handle growing data volumes
4. **Performance**: Optimized for fast queries
5. **Security**: Access control and authentication
6. **ACID Properties**: Atomicity, Consistency, Isolation, Durability
7. **Backup & Recovery**: Data protection mechanisms

## Types of Databases

### 1. Relational Databases (SQL)

Store data in structured tables with predefined schemas.

**Examples:**
- PostgreSQL (open-source, powerful)
- MySQL/MariaDB (popular, web-friendly)
- SQLite (lightweight, file-based)
- Oracle (enterprise)
- Microsoft SQL Server (enterprise)

**Characteristics:**
- Structured data with schemas
- ACID transactions
- SQL query language
- Relationships via foreign keys
- Strong consistency

**Use Cases:**
- Financial systems
- E-commerce
- User management
- ML experiment tracking
- Model metadata storage

### 2. NoSQL Databases

Store data in flexible, non-tabular formats.

**Types:**

**a) Document Databases**
- MongoDB, CouchDB
- Store JSON-like documents
- Flexible schema

```json
{
  "model_id": "bert-v1",
  "metrics": {
    "accuracy": 0.92,
    "f1": 0.89
  },
  "tags": ["nlp", "transformer"]
}
```

**b) Key-Value Stores**
- Redis, DynamoDB
- Simple key-value pairs
- Extremely fast

```
model:bert-v1 → {"accuracy": 0.92}
```

**c) Column-Family Stores**
- Cassandra, HBase
- Optimized for large-scale data

**d) Graph Databases**
- Neo4j, Amazon Neptune
- Store relationships and connections

**Use Cases:**
- Caching (Redis)
- Real-time analytics
- Unstructured data
- Horizontal scaling
- Feature stores in ML

### 3. Comparison: SQL vs NoSQL

| Aspect | SQL (Relational) | NoSQL |
|--------|------------------|-------|
| Schema | Fixed, predefined | Flexible, dynamic |
| Scalability | Vertical (scale up) | Horizontal (scale out) |
| Transactions | ACID guarantees | Eventual consistency |
| Queries | Powerful SQL | Varies by type |
| Data Structure | Tables, rows, columns | Documents, key-value, etc. |
| Best For | Structured data, complex queries | Unstructured data, high volume |
| ML Use Cases | Metadata, experiments | Features, embeddings, logs |

### When to Use Each?

**Use SQL when:**
- Data has a clear structure
- Need complex queries and joins
- ACID transactions are critical
- Data integrity is paramount
- Examples: Model registry, experiment tracking

**Use NoSQL when:**
- Schema changes frequently
- Need massive horizontal scaling
- Handling unstructured data
- Speed over consistency
- Examples: Feature caching, log storage, embeddings

## Relational Database Concepts

### Tables

Tables are the fundamental structure in relational databases. Think of them as spreadsheets.

```
models table:
┌────────┬─────────────┬───────────┬──────────┐
│ id     │ name        │ framework │ accuracy │
├────────┼─────────────┼───────────┼──────────┤
│ 1      │ BERT-base   │ PyTorch   │ 0.92     │
│ 2      │ ResNet-50   │ TensorFlow│ 0.88     │
│ 3      │ GPT-2       │ PyTorch   │ 0.95     │
└────────┴─────────────┴───────────┴──────────┘
```

**Components:**
- **Table name**: `models`
- **Columns**: `id`, `name`, `framework`, `accuracy`
- **Rows**: Each row is a record (3 rows above)

### Columns (Fields)

Columns define the attributes of the data.

```sql
Column Name | Data Type    | Constraints
------------|--------------|-------------
id          | INTEGER      | PRIMARY KEY
name        | VARCHAR(100) | NOT NULL
framework   | VARCHAR(50)  | NOT NULL
accuracy    | DECIMAL(5,4) | CHECK (accuracy >= 0 AND accuracy <= 1)
created_at  | TIMESTAMP    | DEFAULT CURRENT_TIMESTAMP
```

### Rows (Records)

Each row represents a single entity or record.

```sql
-- One row (one model)
(1, 'BERT-base', 'PyTorch', 0.92, '2024-01-15 10:30:00')
```

### Primary Keys

A **primary key** uniquely identifies each row in a table.

```sql
CREATE TABLE models (
    id INTEGER PRIMARY KEY,  -- Unique identifier
    name VARCHAR(100)
);
```

**Properties:**
- Must be unique for each row
- Cannot be NULL
- Only one primary key per table
- Often auto-incrementing

### Foreign Keys

A **foreign key** creates a relationship between tables.

```sql
CREATE TABLE experiments (
    experiment_id INTEGER PRIMARY KEY,
    model_id INTEGER,
    accuracy DECIMAL(5,4),
    FOREIGN KEY (model_id) REFERENCES models(id)
);
```

This links experiments to models:
```
models table:           experiments table:
┌────┬──────────┐      ┌──────────────┬──────────┬──────────┐
│ id │ name     │      │ experiment_id│ model_id │ accuracy │
├────┼──────────┤      ├──────────────┼──────────┼──────────┤
│ 1  │ BERT     │ ←────┤ 101          │ 1        │ 0.92     │
│ 2  │ ResNet   │ ←────┤ 102          │ 2        │ 0.88     │
└────┴──────────┘      │ 103          │ 1        │ 0.93     │
                       └──────────────┴──────────┴──────────┘
```

### Data Types

Common SQL data types:

**Numeric:**
```sql
INTEGER         -- Whole numbers: 1, 42, -10
BIGINT          -- Large integers: 9223372036854775807
DECIMAL(10,2)   -- Fixed precision: 123.45
FLOAT           -- Floating point: 3.14159
```

**Text:**
```sql
CHAR(10)        -- Fixed length: 'BERT      ' (padded)
VARCHAR(100)    -- Variable length: 'BERT-base'
TEXT            -- Unlimited text
```

**Date/Time:**
```sql
DATE            -- Date only: '2024-10-18'
TIME            -- Time only: '14:30:00'
TIMESTAMP       -- Date and time: '2024-10-18 14:30:00'
```

**Boolean:**
```sql
BOOLEAN         -- TRUE or FALSE
```

**Other:**
```sql
JSON            -- JSON data (PostgreSQL)
ARRAY           -- Arrays (PostgreSQL)
BLOB            -- Binary data (images, files)
```

## Introduction to SQL

### What is SQL?

**SQL (Structured Query Language)** is the standard language for interacting with relational databases.

**SQL Categories:**

1. **DDL (Data Definition Language)**: Define structure
   - `CREATE`, `ALTER`, `DROP`

2. **DML (Data Manipulation Language)**: Manipulate data
   - `SELECT`, `INSERT`, `UPDATE`, `DELETE`

3. **DCL (Data Control Language)**: Control access
   - `GRANT`, `REVOKE`

4. **TCL (Transaction Control Language)**: Manage transactions
   - `COMMIT`, `ROLLBACK`

### SQL Syntax Conventions

```sql
-- SQL keywords are typically UPPERCASE (convention)
SELECT * FROM models;

-- But lowercase works too
select * from models;

-- Statements end with semicolon
SELECT name FROM models;

-- Comments
-- Single line comment
/* Multi-line
   comment */
```

**Best Practices:**
- Use UPPERCASE for SQL keywords
- Use lowercase for table/column names
- Indent for readability
- End statements with semicolons

## Setting Up Your Database Environment

### Option 1: SQLite (Recommended for Learning)

SQLite is file-based and requires no server setup.

```bash
# Install (usually pre-installed on Linux/Mac)
sudo apt-get install sqlite3  # Ubuntu/Debian

# Create database
sqlite3 ml_database.db

# You'll see:
# SQLite version 3.x.x
# sqlite>
```

### Option 2: PostgreSQL (Production-Grade)

```bash
# Install PostgreSQL
sudo apt-get install postgresql postgresql-contrib

# Start service
sudo systemctl start postgresql

# Access PostgreSQL
sudo -u postgres psql

# Create database
CREATE DATABASE ml_database;

# Connect to database
\c ml_database
```

### Option 3: Docker (Portable)

```bash
# Run PostgreSQL in Docker
docker run --name postgres-ml \
  -e POSTGRES_PASSWORD=mypassword \
  -e POSTGRES_DB=ml_database \
  -p 5432:5432 \
  -d postgres:14

# Connect
docker exec -it postgres-ml psql -U postgres -d ml_database
```

### Python Database Connection

```python
# SQLite
import sqlite3
conn = sqlite3.connect('ml_database.db')
cursor = conn.cursor()

# PostgreSQL (requires psycopg2)
import psycopg2
conn = psycopg2.connect(
    host="localhost",
    database="ml_database",
    user="postgres",
    password="mypassword"
)
cursor = conn.cursor()
```

## Creating Databases and Tables

### Create Database

```sql
-- PostgreSQL/MySQL
CREATE DATABASE ml_database;

-- Use database
USE ml_database;  -- MySQL
\c ml_database    -- PostgreSQL
```

### Create Table

```sql
CREATE TABLE models (
    id INTEGER PRIMARY KEY AUTOINCREMENT,  -- SQLite
    -- id SERIAL PRIMARY KEY,               -- PostgreSQL
    name VARCHAR(100) NOT NULL,
    framework VARCHAR(50) NOT NULL,
    version VARCHAR(20) DEFAULT '1.0.0',
    accuracy DECIMAL(5, 4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Constraints:**
- `PRIMARY KEY`: Unique identifier
- `NOT NULL`: Value required
- `DEFAULT`: Default value if not specified
- `UNIQUE`: All values must be unique
- `CHECK`: Custom validation

### Example: ML Model Registry

```sql
-- Models table
CREATE TABLE models (
    model_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL UNIQUE,
    framework VARCHAR(50) NOT NULL,
    model_type VARCHAR(50),
    version VARCHAR(20) DEFAULT '1.0.0',
    accuracy DECIMAL(5, 4),
    f1_score DECIMAL(5, 4),
    precision_score DECIMAL(5, 4),
    recall_score DECIMAL(5, 4),
    model_path VARCHAR(255),
    created_by VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'training',
    CHECK (accuracy >= 0 AND accuracy <= 1),
    CHECK (status IN ('training', 'ready', 'deployed', 'archived'))
);

-- Experiments table
CREATE TABLE experiments (
    experiment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    model_id INTEGER NOT NULL,
    experiment_name VARCHAR(100),
    dataset_name VARCHAR(100),
    batch_size INTEGER,
    learning_rate DECIMAL(10, 8),
    epochs INTEGER,
    accuracy DECIMAL(5, 4),
    loss DECIMAL(10, 6),
    training_time_seconds INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (model_id) REFERENCES models(model_id)
);

-- Predictions table (for logging)
CREATE TABLE predictions (
    prediction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    model_id INTEGER NOT NULL,
    input_data TEXT,
    prediction TEXT,
    confidence DECIMAL(5, 4),
    latency_ms INTEGER,
    user_id VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (model_id) REFERENCES models(model_id)
);
```

### View Table Structure

```sql
-- SQLite
.schema models

-- PostgreSQL
\d models

-- MySQL
DESCRIBE models;

-- Standard SQL
SHOW COLUMNS FROM models;
```

## Basic SQL Queries (SELECT)

### Select All Columns

```sql
-- Get all data from models table
SELECT * FROM models;
```

**Output:**
```
model_id | name      | framework | accuracy | created_at
---------|-----------|-----------|----------|-------------------
1        | BERT-base | PyTorch   | 0.92     | 2024-10-18 10:00:00
2        | ResNet-50 | TensorFlow| 0.88     | 2024-10-18 11:00:00
3        | GPT-2     | PyTorch   | 0.95     | 2024-10-18 12:00:00
```

### Select Specific Columns

```sql
-- Get only name and accuracy
SELECT name, accuracy FROM models;
```

**Output:**
```
name      | accuracy
----------|----------
BERT-base | 0.92
ResNet-50 | 0.88
GPT-2     | 0.95
```

### Column Aliases

```sql
-- Rename columns in output
SELECT
    name AS model_name,
    accuracy AS model_accuracy,
    framework AS ml_framework
FROM models;
```

**Output:**
```
model_name | model_accuracy | ml_framework
-----------|----------------|-------------
BERT-base  | 0.92           | PyTorch
ResNet-50  | 0.88           | TensorFlow
```

### Expressions in SELECT

```sql
-- Calculate accuracy percentage
SELECT
    name,
    accuracy,
    accuracy * 100 AS accuracy_percent
FROM models;
```

**Output:**
```
name      | accuracy | accuracy_percent
----------|----------|------------------
BERT-base | 0.92     | 92.0
ResNet-50 | 0.88     | 88.0
```

### DISTINCT Values

```sql
-- Get unique frameworks
SELECT DISTINCT framework FROM models;
```

**Output:**
```
framework
-----------
PyTorch
TensorFlow
```

## Filtering Data (WHERE)

### Basic WHERE Clause

```sql
-- Get models with accuracy > 0.90
SELECT * FROM models
WHERE accuracy > 0.90;
```

### Comparison Operators

```sql
-- Equal to
SELECT * FROM models WHERE framework = 'PyTorch';

-- Not equal to
SELECT * FROM models WHERE framework != 'TensorFlow';
SELECT * FROM models WHERE framework <> 'TensorFlow';  -- Alternative

-- Greater than
SELECT * FROM models WHERE accuracy > 0.90;

-- Greater than or equal to
SELECT * FROM models WHERE accuracy >= 0.90;

-- Less than
SELECT * FROM models WHERE accuracy < 0.90;

-- Less than or equal to
SELECT * FROM models WHERE accuracy <= 0.90;
```

### Logical Operators

**AND:**
```sql
-- Models that are PyTorch AND accuracy > 0.90
SELECT * FROM models
WHERE framework = 'PyTorch' AND accuracy > 0.90;
```

**OR:**
```sql
-- Models that are PyTorch OR TensorFlow
SELECT * FROM models
WHERE framework = 'PyTorch' OR framework = 'TensorFlow';
```

**NOT:**
```sql
-- Models that are NOT PyTorch
SELECT * FROM models
WHERE NOT framework = 'PyTorch';
```

**Combining:**
```sql
-- Complex condition
SELECT * FROM models
WHERE (framework = 'PyTorch' OR framework = 'TensorFlow')
  AND accuracy > 0.85
  AND status = 'deployed';
```

### IN Operator

```sql
-- Models in specific frameworks
SELECT * FROM models
WHERE framework IN ('PyTorch', 'TensorFlow', 'JAX');

-- Equivalent to:
SELECT * FROM models
WHERE framework = 'PyTorch'
   OR framework = 'TensorFlow'
   OR framework = 'JAX';
```

### BETWEEN Operator

```sql
-- Models with accuracy between 0.85 and 0.95
SELECT * FROM models
WHERE accuracy BETWEEN 0.85 AND 0.95;

-- Equivalent to:
SELECT * FROM models
WHERE accuracy >= 0.85 AND accuracy <= 0.95;
```

### LIKE Pattern Matching

```sql
-- Models with names starting with 'BERT'
SELECT * FROM models WHERE name LIKE 'BERT%';

-- Models with names ending with 'Net'
SELECT * FROM models WHERE name LIKE '%Net';

-- Models with names containing 'GPT'
SELECT * FROM models WHERE name LIKE '%GPT%';

-- _ matches single character
SELECT * FROM models WHERE name LIKE 'GPT-_';  -- GPT-2, GPT-3
```

**Wildcards:**
- `%`: Matches any sequence of characters
- `_`: Matches exactly one character

### NULL Handling

```sql
-- Find models without accuracy scores
SELECT * FROM models WHERE accuracy IS NULL;

-- Find models with accuracy scores
SELECT * FROM models WHERE accuracy IS NOT NULL;

-- Note: Use IS NULL, not = NULL
-- This is WRONG:
SELECT * FROM models WHERE accuracy = NULL;  -- Returns nothing!
```

## Sorting and Limiting Results

### ORDER BY

```sql
-- Sort by accuracy (ascending - lowest first)
SELECT * FROM models ORDER BY accuracy;

-- Sort by accuracy (descending - highest first)
SELECT * FROM models ORDER BY accuracy DESC;

-- Sort by multiple columns
SELECT * FROM models
ORDER BY framework ASC, accuracy DESC;
-- First sort by framework alphabetically,
-- then by accuracy (high to low) within each framework
```

### LIMIT

```sql
-- Get top 5 most accurate models
SELECT * FROM models
ORDER BY accuracy DESC
LIMIT 5;

-- Get models 11-20 (pagination)
SELECT * FROM models
ORDER BY created_at DESC
LIMIT 10 OFFSET 10;
-- Skip first 10, return next 10
```

### Combining WHERE, ORDER BY, LIMIT

```sql
-- Top 3 PyTorch models by accuracy
SELECT name, framework, accuracy
FROM models
WHERE framework = 'PyTorch'
ORDER BY accuracy DESC
LIMIT 3;
```

## Inserting Data

### Insert Single Row

```sql
INSERT INTO models (name, framework, accuracy, status)
VALUES ('BERT-large', 'PyTorch', 0.94, 'ready');
```

### Insert Multiple Rows

```sql
INSERT INTO models (name, framework, accuracy, status)
VALUES
    ('ResNet-101', 'TensorFlow', 0.89, 'ready'),
    ('ViT-base', 'PyTorch', 0.91, 'ready'),
    ('EfficientNet-B0', 'TensorFlow', 0.87, 'training');
```

### Insert with Default Values

```sql
-- Use defaults for version, created_at, status
INSERT INTO models (name, framework, accuracy)
VALUES ('MobileNet-v2', 'TensorFlow', 0.85);
-- version will be '1.0.0', status will be 'training'
-- created_at will be current timestamp
```

### Insert from SELECT

```sql
-- Copy data from another table
INSERT INTO models_backup
SELECT * FROM models WHERE status = 'archived';
```

## Updating Data

### Update Single Column

```sql
-- Update model status
UPDATE models
SET status = 'deployed'
WHERE model_id = 1;
```

### Update Multiple Columns

```sql
-- Update model after retraining
UPDATE models
SET
    accuracy = 0.96,
    version = '2.0.0',
    updated_at = CURRENT_TIMESTAMP
WHERE model_id = 1;
```

### Update with Conditions

```sql
-- Archive old models
UPDATE models
SET status = 'archived'
WHERE created_at < '2024-01-01' AND status != 'deployed';
```

### Update All Rows (DANGEROUS!)

```sql
-- This updates ALL rows!
UPDATE models SET status = 'archived';

-- Always use WHERE unless you really want to update everything
```

## Deleting Data

### Delete Specific Rows

```sql
-- Delete a specific model
DELETE FROM models WHERE model_id = 5;
```

### Delete with Conditions

```sql
-- Delete archived models from 2023
DELETE FROM models
WHERE status = 'archived'
  AND created_at < '2024-01-01';
```

### Delete All Rows (VERY DANGEROUS!)

```sql
-- This deletes ALL rows!
DELETE FROM models;

-- Better: Use WHERE clause
DELETE FROM models WHERE 1=0;  -- Deletes nothing (safe test)
```

### TRUNCATE (Faster Alternative)

```sql
-- Remove all rows quickly (resets auto-increment)
TRUNCATE TABLE models;
-- Warning: Cannot be rolled back in some databases!
```

## Databases in ML Infrastructure

### Use Case 1: Model Registry

```sql
-- Track all trained models
CREATE TABLE model_registry (
    model_id INTEGER PRIMARY KEY,
    name VARCHAR(100),
    framework VARCHAR(50),
    architecture VARCHAR(100),
    dataset VARCHAR(100),
    accuracy DECIMAL(5,4),
    training_date TIMESTAMP,
    model_path VARCHAR(255),
    status VARCHAR(20)
);

-- Query: Find best models
SELECT name, accuracy, framework
FROM model_registry
WHERE accuracy > 0.90 AND status = 'production'
ORDER BY accuracy DESC
LIMIT 10;
```

### Use Case 2: Experiment Tracking

```sql
-- Log all training experiments
CREATE TABLE experiments (
    experiment_id INTEGER PRIMARY KEY,
    model_name VARCHAR(100),
    hyperparameters TEXT,  -- JSON string
    accuracy DECIMAL(5,4),
    loss DECIMAL(10,6),
    training_time_seconds INTEGER,
    created_at TIMESTAMP
);

-- Query: Find best hyperparameters
SELECT hyperparameters, accuracy
FROM experiments
WHERE model_name = 'BERT-classifier'
ORDER BY accuracy DESC
LIMIT 1;
```

### Use Case 3: Prediction Logging

```sql
-- Log all predictions for monitoring
CREATE TABLE prediction_logs (
    log_id INTEGER PRIMARY KEY,
    model_id INTEGER,
    input_hash VARCHAR(64),
    prediction TEXT,
    confidence DECIMAL(5,4),
    latency_ms INTEGER,
    timestamp TIMESTAMP,
    user_id VARCHAR(50)
);

-- Query: Monitor model performance
SELECT
    DATE(timestamp) as date,
    AVG(confidence) as avg_confidence,
    AVG(latency_ms) as avg_latency,
    COUNT(*) as prediction_count
FROM prediction_logs
WHERE model_id = 1
  AND timestamp >= DATE('now', '-7 days')
GROUP BY DATE(timestamp);
```

## Best Practices

### 1. Always Use WHERE with UPDATE/DELETE

```sql
-- BAD: Accidentally updates all rows!
UPDATE models SET status = 'archived';

-- GOOD: Updates specific rows
UPDATE models SET status = 'archived'
WHERE model_id = 5;
```

### 2. Use Transactions for Multiple Operations

```sql
BEGIN TRANSACTION;

UPDATE models SET status = 'deployed' WHERE model_id = 1;
INSERT INTO deployment_log (model_id, deployed_at) VALUES (1, CURRENT_TIMESTAMP);

COMMIT;  -- Or ROLLBACK if something fails
```

### 3. Index Important Columns

```sql
-- Create index for faster queries
CREATE INDEX idx_models_framework ON models(framework);
CREATE INDEX idx_models_accuracy ON models(accuracy);

-- Now queries on these columns are much faster
SELECT * FROM models WHERE framework = 'PyTorch';
```

### 4. Use Meaningful Names

```sql
-- BAD
CREATE TABLE t1 (c1 INT, c2 VARCHAR(50));

-- GOOD
CREATE TABLE models (
    model_id INTEGER,
    model_name VARCHAR(50)
);
```

### 5. Validate Data with Constraints

```sql
CREATE TABLE models (
    model_id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    accuracy DECIMAL(5,4) CHECK (accuracy >= 0 AND accuracy <= 1),
    status VARCHAR(20) CHECK (status IN ('training', 'ready', 'deployed'))
);
```

### 6. Regular Backups

```bash
# SQLite backup
sqlite3 ml_database.db ".backup backup.db"

# PostgreSQL backup
pg_dump ml_database > backup.sql
```

## Summary and Key Takeaways

### Core Concepts

1. **Databases** organize and store structured data efficiently
2. **SQL** is the standard language for relational databases
3. **Tables** consist of rows (records) and columns (fields)
4. **Primary keys** uniquely identify rows
5. **Foreign keys** create relationships between tables

### Essential SQL Commands

**Data Retrieval:**
- `SELECT`: Retrieve data
- `WHERE`: Filter rows
- `ORDER BY`: Sort results
- `LIMIT`: Restrict number of results

**Data Modification:**
- `INSERT`: Add new rows
- `UPDATE`: Modify existing rows
- `DELETE`: Remove rows

**Data Definition:**
- `CREATE TABLE`: Define new table
- `ALTER TABLE`: Modify table structure
- `DROP TABLE`: Delete table

### Best Practices

1. Always use `WHERE` with `UPDATE` and `DELETE`
2. Use transactions for related operations
3. Create indexes on frequently queried columns
4. Validate data with constraints
5. Use meaningful names for tables and columns
6. Back up your databases regularly

### ML-Specific Insights

Databases are essential for:
- Model registry and versioning
- Experiment tracking and comparison
- Prediction logging and monitoring
- Dataset metadata management
- Performance metrics storage

### Next Steps

In the next lecture, we'll cover:
- Database design principles
- Normalization (1NF, 2NF, 3NF)
- Relationships (one-to-many, many-to-many)
- Entity-Relationship diagrams
- Schema design for ML systems

### Practice Exercises

1. Create a database for tracking your ML experiments
2. Write queries to find your best-performing models
3. Design a schema for prediction logging
4. Practice filtering with complex WHERE clauses

---

**Estimated Study Time:** 4-5 hours
**Hands-on Practice:** Complete Exercise 01: SQL Basics
**Assessment:** Quiz 01 covers database fundamentals and basic SQL
