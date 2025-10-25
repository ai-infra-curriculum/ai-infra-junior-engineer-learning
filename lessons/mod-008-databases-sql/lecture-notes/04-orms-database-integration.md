# Lecture 04: ORMs and Database Integration

## Table of Contents
1. [Introduction](#introduction)
2. [What is an ORM?](#what-is-an-orm)
3. [Introduction to SQLAlchemy](#introduction-to-sqlalchemy)
4. [Setting Up SQLAlchemy](#setting-up-sqlalchemy)
5. [Defining Models](#defining-models)
6. [CRUD Operations with ORM](#crud-operations-with-orm)
7. [Querying with SQLAlchemy](#querying-with-sqlalchemy)
8. [Relationships in SQLAlchemy](#relationships-in-sqlalchemy)
9. [Migrations with Alembic](#migrations-with-alembic)
10. [Connection Pooling](#connection-pooling)
11. [Transaction Management](#transaction-management)
12. [ORM Patterns for ML Applications](#orm-patterns-for-ml-applications)
13. [Best Practices](#best-practices)
14. [Summary and Key Takeaways](#summary-and-key-takeaways)

## Introduction

Object-Relational Mapping (ORM) bridges the gap between object-oriented programming and relational databases. Instead of writing raw SQL, you work with Python objects that automatically map to database tables. This makes development faster, safer, and more maintainable—especially critical for ML infrastructure applications.

### Learning Objectives

By the end of this lecture, you will:
- Understand what ORMs are and their advantages
- Set up and configure SQLAlchemy
- Define database models as Python classes
- Perform CRUD operations using ORM
- Write complex queries with SQLAlchemy
- Implement relationships between models
- Manage database migrations with Alembic
- Use connection pooling and transactions
- Apply ORM patterns to ML applications

### Prerequisites
- Lectures 01-03 (SQL fundamentals and advanced concepts)
- Python programming proficiency
- Understanding of classes and objects in Python

### Estimated Time
4-5 hours (including hands-on ORM practice)

## What is an ORM?

### Definition

An **Object-Relational Mapper (ORM)** is a library that:
- Maps database tables to Python classes
- Maps table rows to Python objects
- Maps columns to object attributes
- Converts between SQL and Python automatically

### Without ORM (Raw SQL)

```python
import sqlite3

# Manual SQL with string formatting (error-prone!)
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Insert
model_name = "BERT-base"
framework = "PyTorch"
cursor.execute(
    "INSERT INTO models (name, framework) VALUES (?, ?)",
    (model_name, framework)
)

# Query
cursor.execute("SELECT * FROM models WHERE framework = ?", (framework,))
rows = cursor.fetchall()

# Manual object creation
models = []
for row in rows:
    model = {
        'id': row[0],
        'name': row[1],
        'framework': row[2]
    }
    models.append(model)

conn.commit()
conn.close()
```

**Problems:**
- SQL strings are error-prone
- No type checking
- Manual object construction
- SQL injection risks
- Database-specific SQL

### With ORM (SQLAlchemy)

```python
from sqlalchemy.orm import Session
from models import Model

# Object-oriented approach
with Session(engine) as session:
    # Create
    model = Model(name="BERT-base", framework="PyTorch")
    session.add(model)
    session.commit()

    # Query
    pytorch_models = session.query(Model).filter_by(framework="PyTorch").all()

    # Access as objects
    for model in pytorch_models:
        print(f"{model.name} ({model.framework})")
```

**Benefits:**
- Pythonic code
- Type safety
- Automatic SQL generation
- SQL injection protection
- Database independence

### Advantages of ORMs

1. **Productivity**: Write less code
2. **Maintainability**: Easier to read and modify
3. **Type Safety**: Catch errors at development time
4. **Security**: Protection against SQL injection
5. **Portability**: Switch databases easily
6. **Abstraction**: Don't need to be SQL expert
7. **Validation**: Built-in data validation

### Disadvantages of ORMs

1. **Learning Curve**: Need to learn ORM API
2. **Performance**: Can be slower than raw SQL for complex queries
3. **Abstraction Leaks**: Sometimes need to drop to raw SQL
4. **Overhead**: Extra layer between code and database
5. **N+1 Queries**: Easy to accidentally create performance problems

## Introduction to SQLAlchemy

### What is SQLAlchemy?

**SQLAlchemy** is the most popular Python ORM, consisting of:

1. **Core**: SQL generation and execution
2. **ORM**: Object-relational mapping
3. **Engine**: Database connection management
4. **Session**: Transaction and query management

### SQLAlchemy Architecture

```
┌─────────────────────────────────────┐
│  Your Python Application            │
├─────────────────────────────────────┤
│  SQLAlchemy ORM Layer               │
│  (Models, Queries, Sessions)        │
├─────────────────────────────────────┤
│  SQLAlchemy Core                    │
│  (SQL Expression Language)          │
├─────────────────────────────────────┤
│  Engine (Connection Pool)           │
├─────────────────────────────────────┤
│  DBAPI (psycopg2, sqlite3, etc.)   │
├─────────────────────────────────────┤
│  Database (PostgreSQL, MySQL, etc.) │
└─────────────────────────────────────┘
```

### Supported Databases

- PostgreSQL (recommended for production)
- MySQL/MariaDB
- SQLite (great for development)
- Oracle
- Microsoft SQL Server

## Setting Up SQLAlchemy

### Installation

```bash
# Install SQLAlchemy
pip install sqlalchemy

# Database drivers
pip install psycopg2-binary  # PostgreSQL
pip install pymysql          # MySQL
# SQLite support is built-in
```

### Creating Database Engine

```python
from sqlalchemy import create_engine

# SQLite (file-based)
engine = create_engine('sqlite:///ml_database.db', echo=True)

# PostgreSQL
engine = create_engine(
    'postgresql://username:password@localhost:5432/ml_database',
    echo=True  # Log all SQL (for development)
)

# MySQL
engine = create_engine(
    'mysql+pymysql://username:password@localhost:3306/ml_database',
    echo=True
)
```

**Connection String Format:**
```
dialect+driver://username:password@host:port/database
```

### Creating Session Factory

```python
from sqlalchemy.orm import sessionmaker

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Use session
session = SessionLocal()
try:
    # Database operations
    pass
finally:
    session.close()

# Or use context manager (recommended)
with SessionLocal() as session:
    # Database operations
    pass  # Automatically closes
```

## Defining Models

### Basic Model

```python
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

# Base class for all models
Base = declarative_base()

class Model(Base):
    __tablename__ = 'models'

    # Columns
    model_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    framework = Column(String(50), nullable=False)
    version = Column(String(20), default='1.0.0')
    accuracy = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Model(name='{self.name}', framework='{self.framework}')>"
```

### Common Column Types

```python
from sqlalchemy import (
    Integer, BigInteger, SmallInteger,
    String, Text,
    Float, Numeric,
    Boolean,
    Date, DateTime, Time,
    JSON, ARRAY
)

class Example(Base):
    __tablename__ = 'examples'

    id = Column(Integer, primary_key=True)

    # Integers
    count = Column(Integer)
    big_number = Column(BigInteger)

    # Strings
    name = Column(String(100))       # VARCHAR(100)
    description = Column(Text)       # Unlimited text

    # Numbers
    accuracy = Column(Float)         # Floating point
    price = Column(Numeric(10, 2))   # Decimal: 12345678.90

    # Boolean
    is_active = Column(Boolean, default=True)

    # Dates
    created_date = Column(Date)
    created_at = Column(DateTime)
    created_time = Column(Time)

    # JSON (PostgreSQL)
    metadata_json = Column(JSON)

    # Array (PostgreSQL)
    tags = Column(ARRAY(String))
```

### Column Constraints

```python
from sqlalchemy import CheckConstraint

class Model(Base):
    __tablename__ = 'models'

    model_id = Column(Integer, primary_key=True)

    # NOT NULL
    name = Column(String(100), nullable=False)

    # UNIQUE
    email = Column(String(255), unique=True)

    # DEFAULT
    status = Column(String(20), default='training')

    # CHECK constraint
    accuracy = Column(
        Float,
        CheckConstraint('accuracy >= 0 AND accuracy <= 1', name='accuracy_range')
    )

    # Index
    framework = Column(String(50), index=True)
```

### Creating Tables

```python
# Create all tables
Base.metadata.create_all(engine)

# Create specific table
Model.__table__.create(engine)

# Drop all tables
Base.metadata.drop_all(engine)
```

## CRUD Operations with ORM

### Create (INSERT)

```python
from models import Model
from sqlalchemy.orm import Session

with Session(engine) as session:
    # Create single object
    model = Model(
        name="BERT-base",
        framework="PyTorch",
        accuracy=0.92
    )
    session.add(model)
    session.commit()

    # Access auto-generated ID
    print(f"Created model with ID: {model.model_id}")

    # Create multiple objects
    models = [
        Model(name="ResNet-50", framework="TensorFlow", accuracy=0.88),
        Model(name="GPT-2", framework="PyTorch", accuracy=0.95),
    ]
    session.add_all(models)
    session.commit()
```

### Read (SELECT)

```python
with Session(engine) as session:
    # Get all
    all_models = session.query(Model).all()

    # Get by primary key
    model = session.query(Model).get(1)  # ID = 1

    # Get first
    first_model = session.query(Model).first()

    # Filter
    pytorch_models = session.query(Model).filter_by(framework="PyTorch").all()

    # Complex filter
    accurate_models = session.query(Model).filter(Model.accuracy > 0.90).all()

    # Count
    model_count = session.query(Model).count()
```

### Update

```python
with Session(engine) as session:
    # Get and modify
    model = session.query(Model).filter_by(name="BERT-base").first()
    model.accuracy = 0.93
    model.version = "2.0.0"
    session.commit()

    # Bulk update
    session.query(Model).filter_by(framework="PyTorch").update({
        "status": "deployed"
    })
    session.commit()
```

### Delete

```python
with Session(engine) as session:
    # Delete specific object
    model = session.query(Model).filter_by(name="BERT-base").first()
    session.delete(model)
    session.commit()

    # Bulk delete
    session.query(Model).filter_by(status="archived").delete()
    session.commit()
```

## Querying with SQLAlchemy

### Basic Queries

```python
# All records
models = session.query(Model).all()

# Specific columns
names = session.query(Model.name, Model.framework).all()
# Returns list of tuples: [('BERT', 'PyTorch'), ...]

# One result
model = session.query(Model).filter_by(name="BERT").one()  # Raises if 0 or >1
model = session.query(Model).filter_by(name="BERT").one_or_none()  # None if not found
```

### Filtering

```python
# filter_by: Simple equality
models = session.query(Model).filter_by(framework="PyTorch").all()

# filter: Complex conditions
models = session.query(Model).filter(Model.accuracy > 0.90).all()

# Multiple filters (AND)
models = session.query(Model).filter(
    Model.framework == "PyTorch",
    Model.accuracy > 0.90
).all()

# OR condition
from sqlalchemy import or_
models = session.query(Model).filter(
    or_(
        Model.framework == "PyTorch",
        Model.framework == "TensorFlow"
    )
).all()

# IN operator
from sqlalchemy import in_
models = session.query(Model).filter(
    Model.framework.in_(['PyTorch', 'TensorFlow'])
).all()

# LIKE
models = session.query(Model).filter(Model.name.like('%BERT%')).all()

# BETWEEN
models = session.query(Model).filter(Model.accuracy.between(0.85, 0.95)).all()

# IS NULL
models = session.query(Model).filter(Model.accuracy.is_(None)).all()
```

### Ordering and Limiting

```python
# Order by
models = session.query(Model).order_by(Model.accuracy.desc()).all()

# Multiple order
models = session.query(Model).order_by(Model.framework, Model.accuracy.desc()).all()

# Limit
top_5 = session.query(Model).order_by(Model.accuracy.desc()).limit(5).all()

# Offset (pagination)
page_2 = session.query(Model).limit(10).offset(10).all()
```

### Aggregations

```python
from sqlalchemy import func

# Count
count = session.query(func.count(Model.model_id)).scalar()

# Average
avg_accuracy = session.query(func.avg(Model.accuracy)).scalar()

# Min and Max
min_acc = session.query(func.min(Model.accuracy)).scalar()
max_acc = session.query(func.max(Model.accuracy)).scalar()

# Group by
results = session.query(
    Model.framework,
    func.count(Model.model_id).label('count'),
    func.avg(Model.accuracy).label('avg_accuracy')
).group_by(Model.framework).all()

# Having
results = session.query(
    Model.framework,
    func.count(Model.model_id).label('count')
).group_by(Model.framework).having(func.count(Model.model_id) > 1).all()
```

## Relationships in SQLAlchemy

### One-to-Many Relationship

```python
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

class Model(Base):
    __tablename__ = 'models'

    model_id = Column(Integer, primary_key=True)
    name = Column(String(100))

    # Relationship (one model has many experiments)
    experiments = relationship("Experiment", back_populates="model")

class Experiment(Base):
    __tablename__ = 'experiments'

    experiment_id = Column(Integer, primary_key=True)
    model_id = Column(Integer, ForeignKey('models.model_id'))
    accuracy = Column(Float)

    # Relationship (many experiments belong to one model)
    model = relationship("Model", back_populates="experiments")
```

**Usage:**
```python
with Session(engine) as session:
    # Create model with experiments
    model = Model(name="BERT")
    exp1 = Experiment(accuracy=0.92)
    exp2 = Experiment(accuracy=0.93)

    model.experiments.append(exp1)
    model.experiments.append(exp2)

    session.add(model)
    session.commit()

    # Access experiments
    model = session.query(Model).filter_by(name="BERT").first()
    for exp in model.experiments:
        print(f"Experiment {exp.experiment_id}: {exp.accuracy}")

    # Access model from experiment
    exp = session.query(Experiment).first()
    print(f"Model: {exp.model.name}")
```

### Many-to-Many Relationship

```python
# Association table
model_tags = Table(
    'model_tags',
    Base.metadata,
    Column('model_id', Integer, ForeignKey('models.model_id')),
    Column('tag_id', Integer, ForeignKey('tags.tag_id'))
)

class Model(Base):
    __tablename__ = 'models'

    model_id = Column(Integer, primary_key=True)
    name = Column(String(100))

    # Many-to-many
    tags = relationship("Tag", secondary=model_tags, back_populates="models")

class Tag(Base):
    __tablename__ = 'tags'

    tag_id = Column(Integer, primary_key=True)
    tag_name = Column(String(50))

    # Many-to-many
    models = relationship("Model", secondary=model_tags, back_populates="tags")
```

**Usage:**
```python
with Session(engine) as session:
    # Create model and tags
    model = Model(name="BERT")
    tag1 = Tag(tag_name="NLP")
    tag2 = Tag(tag_name="Transformer")

    model.tags.extend([tag1, tag2])

    session.add(model)
    session.commit()

    # Query models by tag
    nlp_models = session.query(Model).join(Model.tags).filter(Tag.tag_name == "NLP").all()
```

### Eager Loading (Avoid N+1 Queries)

```python
from sqlalchemy.orm import joinedload, selectinload

# Without eager loading (N+1 problem):
models = session.query(Model).all()
for model in models:  # 1 query
    for exp in model.experiments:  # N queries (one per model)
        print(exp.accuracy)

# With joinedload (uses JOIN):
models = session.query(Model).options(joinedload(Model.experiments)).all()
for model in models:  # 1 query total
    for exp in model.experiments:
        print(exp.accuracy)

# With selectinload (uses separate SELECT IN):
models = session.query(Model).options(selectinload(Model.experiments)).all()
```

## Migrations with Alembic

### What is Alembic?

**Alembic** is a database migration tool for SQLAlchemy that:
- Tracks schema changes over time
- Allows upgrading/downgrading database schema
- Works with version control

### Setup Alembic

```bash
# Install
pip install alembic

# Initialize
alembic init alembic

# Creates:
# alembic/
# ├── env.py
# ├── script.py.mako
# └── versions/
# alembic.ini
```

### Configure Alembic

**alembic.ini:**
```ini
# Set database URL
sqlalchemy.url = postgresql://user:password@localhost/ml_database
```

**alembic/env.py:**
```python
# Import your models
from models import Base
target_metadata = Base.metadata
```

### Creating Migrations

```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "create models table"

# Manual migration
alembic revision -m "add accuracy column"
```

**Generated migration:**
```python
# alembic/versions/001_create_models_table.py
def upgrade():
    op.create_table(
        'models',
        sa.Column('model_id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('framework', sa.String(50))
    )

def downgrade():
    op.drop_table('models')
```

### Running Migrations

```bash
# Upgrade to latest
alembic upgrade head

# Upgrade to specific version
alembic upgrade abc123

# Downgrade one version
alembic downgrade -1

# Show current version
alembic current

# Show migration history
alembic history
```

## Connection Pooling

### What is Connection Pooling?

Reusing database connections instead of creating new ones for each query.

**Benefits:**
- Faster (no connection overhead)
- Less resource usage
- Handle more concurrent requests

### Configuring Pool

```python
from sqlalchemy import create_engine

engine = create_engine(
    'postgresql://user:password@localhost/ml_database',
    pool_size=5,        # Keep 5 connections open
    max_overflow=10,    # Allow 10 additional connections if needed
    pool_timeout=30,    # Wait 30s for available connection
    pool_recycle=3600,  # Recycle connections after 1 hour
)
```

### Pool Types

```python
# QueuePool (default for most databases)
from sqlalchemy.pool import QueuePool
engine = create_engine(..., poolclass=QueuePool)

# NullPool (no pooling, new connection each time)
from sqlalchemy.pool import NullPool
engine = create_engine(..., poolclass=NullPool)

# StaticPool (single connection, SQLite)
from sqlalchemy.pool import StaticPool
engine = create_engine('sqlite://', poolclass=StaticPool)
```

## Transaction Management

### Basic Transaction

```python
with Session(engine) as session:
    try:
        # Multiple operations in one transaction
        model1 = Model(name="BERT", framework="PyTorch")
        model2 = Model(name="GPT-2", framework="PyTorch")

        session.add(model1)
        session.add(model2)

        session.commit()  # Both saved or both fail
    except Exception as e:
        session.rollback()  # Undo all changes
        raise e
```

### Explicit Transactions

```python
with Session(engine) as session:
    with session.begin():  # Explicit transaction
        model = Model(name="BERT")
        session.add(model)
        # Automatically commits if no exception
        # Automatically rolls back if exception
```

### Nested Transactions (Savepoints)

```python
with Session(engine) as session:
    with session.begin():
        model = Model(name="BERT")
        session.add(model)

        with session.begin_nested():  # Savepoint
            exp = Experiment(model_id=1, accuracy=0.92)
            session.add(exp)
            # Can roll back to this point if needed

        session.commit()
```

## ORM Patterns for ML Applications

### Pattern 1: Model Registry

```python
class MLModel(Base):
    __tablename__ = 'ml_models'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True)
    framework = Column(String(50))
    model_path = Column(String(255))
    accuracy = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String(20), default='training')

    versions = relationship("ModelVersion", back_populates="model")
    experiments = relationship("Experiment", back_populates="model")

class ModelVersion(Base):
    __tablename__ = 'model_versions'

    id = Column(Integer, primary_key=True)
    model_id = Column(Integer, ForeignKey('ml_models.id'))
    version = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow)

    model = relationship("MLModel", back_populates="versions")

# Usage
def register_model(session, name, framework, model_path):
    model = MLModel(
        name=name,
        framework=framework,
        model_path=model_path,
        status='ready'
    )
    session.add(model)
    session.commit()
    return model

def get_latest_model(session, name):
    return session.query(MLModel).filter_by(
        name=name,
        status='deployed'
    ).order_by(MLModel.created_at.desc()).first()
```

### Pattern 2: Experiment Tracking

```python
class Experiment(Base):
    __tablename__ = 'experiments'

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    model_id = Column(Integer, ForeignKey('ml_models.id'))
    dataset = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)

    model = relationship("MLModel", back_populates="experiments")
    hyperparameters = relationship("Hyperparameter", back_populates="experiment")
    metrics = relationship("Metric", back_populates="experiment")

class Hyperparameter(Base):
    __tablename__ = 'hyperparameters'

    id = Column(Integer, primary_key=True)
    experiment_id = Column(Integer, ForeignKey('experiments.id'))
    name = Column(String(50))
    value = Column(String(100))

    experiment = relationship("Experiment", back_populates="hyperparameters")

class Metric(Base):
    __tablename__ = 'metrics'

    id = Column(Integer, primary_key=True)
    experiment_id = Column(Integer, ForeignKey('experiments.id'))
    name = Column(String(50))
    value = Column(Float)
    epoch = Column(Integer)

    experiment = relationship("Experiment", back_populates="metrics")

# Usage
def log_experiment(session, model_id, dataset, hyperparams, metrics):
    exp = Experiment(model_id=model_id, dataset=dataset)

    for name, value in hyperparams.items():
        hp = Hyperparameter(name=name, value=str(value))
        exp.hyperparameters.append(hp)

    for name, value in metrics.items():
        m = Metric(name=name, value=value)
        exp.metrics.append(m)

    session.add(exp)
    session.commit()
    return exp
```

### Pattern 3: Repository Pattern

```python
class ModelRepository:
    def __init__(self, session):
        self.session = session

    def get_by_id(self, model_id):
        return self.session.query(MLModel).get(model_id)

    def get_by_name(self, name):
        return self.session.query(MLModel).filter_by(name=name).first()

    def get_all(self, framework=None, status=None):
        query = self.session.query(MLModel)
        if framework:
            query = query.filter_by(framework=framework)
        if status:
            query = query.filter_by(status=status)
        return query.all()

    def create(self, model):
        self.session.add(model)
        self.session.commit()
        return model

    def update(self, model):
        self.session.commit()
        return model

    def delete(self, model):
        self.session.delete(model)
        self.session.commit()

# Usage
with Session(engine) as session:
    repo = ModelRepository(session)

    # Create
    model = MLModel(name="BERT", framework="PyTorch")
    repo.create(model)

    # Get
    model = repo.get_by_name("BERT")

    # Update
    model.accuracy = 0.95
    repo.update(model)

    # Delete
    repo.delete(model)
```

## Best Practices

### 1. Use Context Managers

```python
# GOOD
with Session(engine) as session:
    model = session.query(Model).first()
    # Session automatically closed

# AVOID
session = Session(engine)
model = session.query(Model).first()
session.close()  # Easy to forget!
```

### 2. Use Transactions

```python
# GOOD
with Session(engine) as session:
    try:
        model = Model(name="BERT")
        session.add(model)
        session.commit()
    except:
        session.rollback()
        raise

# BETTER
with Session(engine) as session:
    with session.begin():
        model = Model(name="BERT")
        session.add(model)
        # Auto-commit or rollback
```

### 3. Avoid N+1 Queries

```python
# BAD (N+1 queries)
models = session.query(Model).all()
for model in models:
    for exp in model.experiments:  # Query per model!
        print(exp.accuracy)

# GOOD (2 queries)
models = session.query(Model).options(selectinload(Model.experiments)).all()
for model in models:
    for exp in model.experiments:
        print(exp.accuracy)
```

### 4. Use Bulk Operations

```python
# SLOW
for i in range(1000):
    model = Model(name=f"model_{i}")
    session.add(model)
    session.commit()  # 1000 commits!

# FAST
models = [Model(name=f"model_{i}") for i in range(1000)]
session.bulk_save_objects(models)
session.commit()  # 1 commit
```

### 5. Close Sessions

```python
# Always close sessions
with Session(engine) as session:
    # Do work
    pass  # Auto-closes

# For long-running apps, use scoped sessions
from sqlalchemy.orm import scoped_session

SessionLocal = scoped_session(sessionmaker(bind=engine))

# Access session
session = SessionLocal()
# Work with session
SessionLocal.remove()  # Close session
```

## Summary and Key Takeaways

### What We Learned

1. **ORMs** map objects to database tables automatically
2. **SQLAlchemy** is the standard Python ORM
3. **Models** are Python classes that represent tables
4. **Sessions** manage transactions and queries
5. **Relationships** connect models (1:1, 1:N, M:N)
6. **Migrations** track schema changes with Alembic
7. **Pooling** reuses connections for performance
8. **Transactions** ensure data integrity

### ORM vs Raw SQL

| Aspect | ORM | Raw SQL |
|--------|-----|---------|
| Productivity | High | Medium |
| Type Safety | Yes | No |
| Readability | High | Medium |
| Performance | Good | Best |
| Complexity | Medium | Low |
| Portability | High | Low |

**Rule of thumb:** Use ORM for 90% of operations, raw SQL for complex/performance-critical queries.

### When to Use Each

**Use ORM when:**
- CRUD operations
- Standard queries
- Type safety is important
- Database portability matters

**Use raw SQL when:**
- Complex aggregations
- Bulk operations
- Performance-critical queries
- Database-specific features needed

### Next Steps

You now have all the database knowledge needed for ML infrastructure:
- SQL basics and advanced queries
- Database design and normalization
- Query optimization
- ORM integration

**Practice by building:**
- Model registry application
- Experiment tracking system
- Prediction logging service
- Dataset management tool

---

**Estimated Study Time:** 4-5 hours
**Hands-on Practice:** Complete Exercise 04: SQLAlchemy ORM
**Final Assessment:** Module quiz covers all 4 lectures
