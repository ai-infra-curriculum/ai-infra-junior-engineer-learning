# Exercise 04: SQLAlchemy ORM Integration

## Overview

Bridge your database design with a Python application using SQLAlchemy ORM. You will model the ML registry domain, implement query patterns, and expose a service layer ready for FastAPI integration. This exercise transforms the SQL schema from Exercise 02 into a production-ready Python package with ORM models, repositories, migrations, and comprehensive testing.

**Difficulty:** Intermediate → Advanced
**Estimated Time:** 3-4 hours
**Prerequisites:**
- Prior exercises completed (schema design + advanced SQL)
- Lecture 04 (ORMs & Database Integration)
- Python 3.9+, virtual environment basics
- Familiarity with type hints and modern Python patterns

## Learning Objectives

By the end of this exercise, you will be able to:

1. **Map relational tables to SQLAlchemy ORM models** with proper relationships and constraints
2. **Configure sessions and connection pooling** for production database access
3. **Implement repository patterns** that encapsulate CRUD and complex queries
4. **Manage schema migrations** using Alembic for database evolution
5. **Write comprehensive tests** for database interactions with fixtures and factories
6. **Apply production patterns** including connection pooling, error handling, and logging
7. **Integrate with FastAPI** for building RESTful APIs backed by databases

## Scenario

Your ML infrastructure team needs a reusable Python package `ml_registry_db` that other services can import. This package will provide:

- **ORM models** mirroring the normalized schema from Exercise 02
- **Repository layer** with functions like `get_latest_deployment(model_name)` and `record_training_run(...)`
- **Migration management** using Alembic for schema evolution
- **CLI tools** to bootstrap database with seed data
- **Test suite** validating mappings and business logic
- **FastAPI integration** demonstrating real-world API usage

This package will become the foundation for your ML model registry service, enabling teams to track models, versions, deployments, and training runs programmatically.

---

## Part 1: Project Scaffolding and Setup

### Step 1.1: Create Project Structure

Create the following directory structure:

```bash
mkdir -p ml-registry-db/{src/ml_registry_db,alembic/versions,scripts,tests}
cd ml-registry-db
```

Complete project layout:

```
ml-registry-db/
├── pyproject.toml              # Poetry dependency management
├── README.md                   # Documentation
├── .env.example                # Environment variable template
├── .gitignore                  # Git ignore rules
├── src/
│   └── ml_registry_db/
│       ├── __init__.py         # Package initialization
│       ├── config.py           # Configuration management
│       ├── db.py               # Database session and engine
│       ├── models.py           # SQLAlchemy ORM models
│       ├── repositories.py     # Repository pattern implementations
│       ├── schemas.py          # Pydantic models for validation
│       └── cli.py              # Command-line interface
├── alembic/                    # Database migrations
│   ├── env.py                  # Alembic environment config
│   ├── script.py.mako          # Migration template
│   ├── alembic.ini             # Alembic configuration
│   └── versions/               # Migration version files
├── scripts/
│   ├── seed_data.py            # Populate database with test data
│   ├── create_tables.py        # Initialize database schema
│   └── reset_db.py             # Drop and recreate database
└── tests/
    ├── __init__.py
    ├── conftest.py             # Pytest fixtures
    ├── factories.py            # Factory Boy test data generators
    ├── test_models.py          # ORM model tests
    ├── test_repositories.py    # Repository function tests
    └── test_integration.py     # End-to-end integration tests
```

### Step 1.2: Initialize Poetry Project

Create `pyproject.toml`:

```toml
[tool.poetry]
name = "ml-registry-db"
version = "0.1.0"
description = "ML Model Registry Database Package with SQLAlchemy ORM"
authors = ["Your Name <you@example.com>"]
readme = "README.md"
packages = [{include = "ml_registry_db", from = "src"}]

[tool.poetry.dependencies]
python = "^3.9"
SQLAlchemy = "^2.0"
alembic = "^1.12"
psycopg2-binary = "^2.9"
pydantic = "^2.5"
pydantic-settings = "^2.1"
python-dotenv = "^1.0"
typer = "^0.9"
rich = "^13.7"           # Pretty console output

[tool.poetry.group.dev.dependencies]
pytest = "^7.4"
pytest-asyncio = "^0.23"
pytest-cov = "^4.1"
factory-boy = "^3.3"
faker = "^21.0"
black = "^23.12"
ruff = "^0.1"
mypy = "^1.7"
sqlalchemy-stubs = "^0.4"

[tool.poetry.scripts]
ml-registry = "ml_registry_db.cli:app"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"

[tool.black]
line-length = 100
target-version = ['py39', 'py310', 'py311']

[tool.ruff]
line-length = 100
select = ["E", "F", "W", "I", "N", "UP"]

[tool.mypy]
python_version = "3.9"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
plugins = ["pydantic.mypy", "sqlalchemy.ext.mypy.plugin"]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_functions = ["test_*"]
addopts = "-v --cov=ml_registry_db --cov-report=term-missing"
```

### Step 1.3: Environment Configuration

Create `.env.example`:

```bash
# Database Configuration
DATABASE_URL=postgresql://ml_user:ml_password@localhost:5432/ml_registry
TEST_DATABASE_URL=postgresql://ml_user:ml_password@localhost:5432/ml_registry_test

# Database Connection Pool Settings
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=3600

# Application Settings
ENVIRONMENT=development
LOG_LEVEL=INFO
DEBUG=true

# Optional: Async database support
ASYNC_DATABASE_URL=postgresql+asyncpg://ml_user:ml_password@localhost:5432/ml_registry
```

Copy to `.env` and customize:

```bash
cp .env.example .env
# Edit .env with your actual credentials
```

### Step 1.4: Install Dependencies

```bash
# Install Poetry if not already installed
curl -sSL https://install.python-poetry.org | python3 -

# Install project dependencies
poetry install

# Activate virtual environment
poetry shell
```

### Step 1.5: Create `.gitignore`

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
.venv/
.poetry/

# Environment variables
.env
.env.local

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Testing
.coverage
.pytest_cache/
htmlcov/

# Database
*.db
*.sqlite

# Alembic
alembic/versions/*.pyc

# OS
.DS_Store
Thumbs.db
```

### Checkpoint 1

✅ Verify your setup:

```bash
poetry --version
poetry show  # List installed dependencies
ls -la src/ml_registry_db/  # Confirm package structure
cat .env  # Check environment variables (don't commit this!)
```

---

## Part 2: Configuration Management

### Step 2.1: Create Configuration Module

Create `src/ml_registry_db/config.py`:

```python
"""
Configuration management using Pydantic Settings.
Loads from environment variables and .env files.
"""
from functools import lru_cache
from typing import Optional

from pydantic import Field, PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Database settings
    database_url: PostgresDsn = Field(
        ...,
        description="PostgreSQL database URL",
        examples=["postgresql://user:pass@localhost/db"],
    )

    test_database_url: Optional[PostgresDsn] = Field(
        None,
        description="Test database URL (defaults to database_url with _test suffix)",
    )

    # Connection pool settings
    db_pool_size: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Number of connections to keep in the pool",
    )

    db_max_overflow: int = Field(
        default=10,
        ge=0,
        le=50,
        description="Maximum overflow connections beyond pool_size",
    )

    db_pool_timeout: int = Field(
        default=30,
        ge=1,
        le=300,
        description="Seconds to wait before timing out on connection checkout",
    )

    db_pool_recycle: int = Field(
        default=3600,
        ge=300,
        description="Seconds after which to recycle connections",
    )

    db_echo: bool = Field(
        default=False,
        description="Echo SQL statements to stdout (for debugging)",
    )

    # Application settings
    environment: str = Field(
        default="development",
        pattern="^(development|staging|production|test)$",
    )

    log_level: str = Field(
        default="INFO",
        pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$",
    )

    debug: bool = Field(default=False)

    @field_validator("test_database_url", mode="before")
    @classmethod
    def build_test_url(cls, v: Optional[str], info) -> Optional[str]:
        """Auto-generate test database URL if not provided."""
        if v is not None:
            return v

        # Get the main database URL from validation data
        db_url = info.data.get("database_url")
        if db_url:
            # Replace database name with _test suffix
            return str(db_url).rsplit("/", 1)[0] + "/ml_registry_test"
        return None

    @property
    def is_development(self) -> bool:
        return self.environment == "development"

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @property
    def is_test(self) -> bool:
        return self.environment == "test"


@lru_cache()
def get_settings() -> Settings:
    """
    Create cached settings instance.
    Use lru_cache to avoid re-reading environment on every call.
    """
    return Settings()


# Convenience access
settings = get_settings()


# Usage example:
if __name__ == "__main__":
    from rich import print as rprint

    rprint("[bold]Current Settings:[/bold]")
    rprint(f"Database URL: {settings.database_url}")
    rprint(f"Environment: {settings.environment}")
    rprint(f"Pool Size: {settings.db_pool_size}")
    rprint(f"Max Overflow: {settings.db_max_overflow}")
```

### Key Configuration Patterns

**Why use Pydantic Settings?**

1. **Type Safety**: Automatic validation and type conversion
2. **Documentation**: Built-in field descriptions and examples
3. **Defaults**: Sensible defaults with override capability
4. **Validation**: Constraints (ge, le, pattern) ensure valid config
5. **12-Factor App**: Environment variable support for cloud deployments

**Security Best Practices:**

- ✅ Never commit `.env` files to version control
- ✅ Use different credentials for dev/staging/prod
- ✅ Rotate database passwords regularly
- ✅ Use IAM authentication in cloud environments (AWS RDS IAM, GCP Cloud SQL)
- ✅ Encrypt DATABASE_URL in CI/CD secrets

---

## Part 3: Database Session and Engine Configuration

### Step 3.1: Create Database Module

Create `src/ml_registry_db/db.py`:

```python
"""
Database engine, session factory, and connection management.
Provides context managers for session lifecycle.
"""
import logging
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine, event, pool
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker, declarative_base

from .config import settings

logger = logging.getLogger(__name__)

# Declarative base for ORM models
Base = declarative_base()


def create_db_engine(url: str = None, echo: bool = None) -> Engine:
    """
    Create SQLAlchemy engine with connection pooling.

    Args:
        url: Database URL (defaults to settings.database_url)
        echo: Echo SQL to stdout (defaults to settings.db_echo)

    Returns:
        Configured SQLAlchemy engine

    Connection Pool Configuration:
    - pool_size: Number of persistent connections
    - max_overflow: Additional connections under load
    - pool_timeout: Seconds to wait for available connection
    - pool_recycle: Seconds before recycling connections (prevents stale connections)
    - pool_pre_ping: Test connections before checkout (detect dropped connections)
    """
    db_url = url or str(settings.database_url)
    sql_echo = echo if echo is not None else settings.db_echo

    engine = create_engine(
        db_url,
        echo=sql_echo,
        pool_size=settings.db_pool_size,
        max_overflow=settings.db_max_overflow,
        pool_timeout=settings.db_pool_timeout,
        pool_recycle=settings.db_pool_recycle,
        pool_pre_ping=True,  # Verify connection health before use
        # Use QueuePool for multi-threaded applications
        poolclass=pool.QueuePool,
    )

    # Register event listeners for connection lifecycle
    @event.listens_for(engine, "connect")
    def receive_connect(dbapi_conn, connection_record):
        """Log new database connections."""
        logger.debug(f"New database connection established: {id(dbapi_conn)}")

    @event.listens_for(engine, "checkout")
    def receive_checkout(dbapi_conn, connection_record, connection_proxy):
        """Log connection checkouts from pool."""
        logger.debug(f"Connection checked out from pool: {id(dbapi_conn)}")

    return engine


# Global engine instance (singleton pattern)
_engine: Engine = None


def get_engine() -> Engine:
    """Get or create the global engine instance."""
    global _engine
    if _engine is None:
        _engine = create_db_engine()
        logger.info("Database engine initialized")
    return _engine


# Session factory
SessionLocal = sessionmaker(
    bind=None,  # Will be bound dynamically
    autocommit=False,  # Require explicit commit
    autoflush=False,   # Don't auto-flush on query (more explicit control)
    expire_on_commit=True,  # Expire objects after commit (fetch fresh data)
)


def get_session_factory() -> sessionmaker:
    """Get session factory bound to the global engine."""
    SessionLocal.configure(bind=get_engine())
    return SessionLocal


@contextmanager
def get_session() -> Generator[Session, None, None]:
    """
    Context manager for database sessions.
    Automatically handles commit/rollback and cleanup.

    Usage:
        with get_session() as session:
            model = session.query(Model).first()
            session.commit()

    Benefits:
    - Automatic rollback on exceptions
    - Guaranteed session cleanup
    - Exception propagation
    """
    session = get_session_factory()()
    try:
        yield session
        session.commit()  # Commit if no exceptions
    except Exception as e:
        session.rollback()  # Rollback on any exception
        logger.error(f"Session rollback due to exception: {e}")
        raise  # Re-raise exception after rollback
    finally:
        session.close()  # Always close session


def get_db() -> Generator[Session, None, None]:
    """
    Dependency injection helper for FastAPI.

    Usage:
        @app.get("/models")
        def list_models(db: Session = Depends(get_db)):
            return db.query(Model).all()
    """
    session = get_session_factory()()
    try:
        yield session
    finally:
        session.close()


def init_db(engine: Engine = None) -> None:
    """
    Initialize database schema (create all tables).

    Args:
        engine: SQLAlchemy engine (defaults to global engine)

    Note: In production, use Alembic migrations instead of create_all().
    This function is primarily for development and testing.
    """
    from . import models  # Import to register models with Base

    db_engine = engine or get_engine()
    Base.metadata.create_all(bind=db_engine)
    logger.info("Database schema initialized")


def drop_db(engine: Engine = None) -> None:
    """
    Drop all database tables.

    WARNING: This is destructive! Use only in development/testing.
    """
    from . import models

    db_engine = engine or get_engine()
    Base.metadata.drop_all(bind=db_engine)
    logger.warning("Database schema dropped")


def reset_db(engine: Engine = None) -> None:
    """Drop and recreate all tables."""
    drop_db(engine)
    init_db(engine)
    logger.info("Database reset complete")


# Connection pool statistics
def get_pool_status() -> dict:
    """
    Get current connection pool statistics.
    Useful for monitoring and debugging.
    """
    engine = get_engine()
    pool_obj = engine.pool

    return {
        "pool_size": pool_obj.size(),
        "checked_in": pool_obj.checkedin(),
        "checked_out": pool_obj.checkedout(),
        "overflow": pool_obj.overflow(),
        "total_connections": pool_obj.size() + pool_obj.overflow(),
    }


# Example usage
if __name__ == "__main__":
    import sys

    logging.basicConfig(level=logging.DEBUG)

    print("Testing database connection...")

    try:
        engine = get_engine()
        print(f"✅ Engine created: {engine}")

        # Test connection
        with engine.connect() as conn:
            result = conn.execute("SELECT version()")
            version = result.scalar()
            print(f"✅ PostgreSQL version: {version}")

        # Test session
        with get_session() as session:
            result = session.execute("SELECT current_database()")
            db_name = result.scalar()
            print(f"✅ Connected to database: {db_name}")

        # Pool stats
        stats = get_pool_status()
        print(f"✅ Pool status: {stats}")

    except Exception as e:
        print(f"❌ Connection failed: {e}")
        sys.exit(1)
```

### Understanding Connection Pooling

**Why Connection Pooling?**

Creating database connections is expensive (TCP handshake, authentication, etc.). Connection pooling maintains a pool of reusable connections.

**Key Parameters:**

- **pool_size=5**: Keep 5 persistent connections open
- **max_overflow=10**: Allow up to 10 additional temporary connections under load (total: 15)
- **pool_timeout=30**: Wait 30 seconds for available connection before raising error
- **pool_recycle=3600**: Close and replace connections after 1 hour (prevents stale connections)
- **pool_pre_ping=True**: Test connection health before use (detect dropped connections)

**Production Considerations:**

```python
# Development (verbose logging)
engine = create_engine(url, echo=True, pool_size=5)

# Production (connection pooling optimized)
engine = create_engine(
    url,
    echo=False,
    pool_size=20,           # More connections for high traffic
    max_overflow=40,
    pool_recycle=1800,      # Recycle more frequently
    pool_pre_ping=True,
)
```

### Checkpoint 2

Test your database connection:

```bash
# Ensure PostgreSQL is running (from Exercise 01)
docker ps  # Check ml-registry-postgres container

# Test connection
python -m ml_registry_db.db

# Expected output:
# ✅ Engine created: Engine(postgresql://...)
# ✅ PostgreSQL version: PostgreSQL 14.x
# ✅ Connected to database: ml_registry
# ✅ Pool status: {'pool_size': 5, ...}
```

---

## Part 4: ORM Models with Relationships

### Step 4.1: Create ORM Models

Create `src/ml_registry_db/models.py`:

```python
"""
SQLAlchemy ORM models for ML Model Registry.
Maps to the normalized schema from Exercise 02.
"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    Enum as SQLEnum,
    Float,
    ForeignKey,
    Index,
    Integer,
    JSON,
    Numeric,
    String,
    Table,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from .db import Base

# ============================================================================
# Enums for type safety
# ============================================================================

import enum


class FrameworkEnum(str, enum.Enum):
    """Supported ML frameworks."""
    PYTORCH = "pytorch"
    TENSORFLOW = "tensorflow"
    SKLEARN = "sklearn"
    XGBOOST = "xgboost"
    JAX = "jax"
    MXNET = "mxnet"


class RunStatusEnum(str, enum.Enum):
    """Training run status."""
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class DeploymentStatusEnum(str, enum.Enum):
    """Deployment status."""
    PENDING = "pending"
    ACTIVE = "active"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"
    DECOMMISSIONED = "decommissioned"


class ApprovalStatusEnum(str, enum.Enum):
    """Approval workflow status."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    REVOKED = "revoked"


# ============================================================================
# Junction Tables (Many-to-Many Relationships)
# ============================================================================

model_tags = Table(
    "model_tags",
    Base.metadata,
    Column("model_id", PGUUID(as_uuid=True), ForeignKey("models.model_id", ondelete="CASCADE")),
    Column("tag_id", Integer, ForeignKey("tags.tag_id", ondelete="CASCADE")),
    Column("tagged_at", DateTime(timezone=True), server_default=func.now()),
    UniqueConstraint("model_id", "tag_id", name="unique_model_tag"),
)

dataset_tags = Table(
    "dataset_tags",
    Base.metadata,
    Column("dataset_id", PGUUID(as_uuid=True), ForeignKey("datasets.dataset_id", ondelete="CASCADE")),
    Column("tag_id", Integer, ForeignKey("tags.tag_id", ondelete="CASCADE")),
    Column("tagged_at", DateTime(timezone=True), server_default=func.now()),
    UniqueConstraint("dataset_id", "tag_id", name="unique_dataset_tag"),
)

run_datasets = Table(
    "run_datasets",
    Base.metadata,
    Column("run_id", PGUUID(as_uuid=True), ForeignKey("training_runs.run_id", ondelete="CASCADE")),
    Column("dataset_id", PGUUID(as_uuid=True), ForeignKey("datasets.dataset_id", ondelete="CASCADE")),
    Column("split_type", String(20), nullable=False),  # train, validation, test
    Column("linked_at", DateTime(timezone=True), server_default=func.now()),
    CheckConstraint("split_type IN ('train', 'validation', 'test')", name="valid_split_type"),
)


# ============================================================================
# Mixin Classes for Common Patterns
# ============================================================================

class TimestampMixin:
    """Mixin for created_at and updated_at timestamps."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class UUIDPrimaryKeyMixin:
    """Mixin for UUID primary key."""

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )


# ============================================================================
# Core Models
# ============================================================================

class Team(Base):
    """Teams that own models."""

    __tablename__ = "teams"

    team_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    team_name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    team_email: Mapped[str] = mapped_column(String(255), nullable=False)
    team_slack_channel: Mapped[Optional[str]] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    models: Mapped[List["Model"]] = relationship("Model", back_populates="team")

    def __repr__(self) -> str:
        return f"<Team(id={self.team_id}, name='{self.team_name}')>"


class Environment(Base):
    """Deployment environments (dev, staging, production)."""

    __tablename__ = "environments"

    environment_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    environment_name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)

    # Relationships
    deployments: Mapped[List["Deployment"]] = relationship("Deployment", back_populates="environment")

    __table_args__ = (
        CheckConstraint(
            "environment_name IN ('development', 'staging', 'production', 'canary', 'shadow')",
            name="valid_environment",
        ),
    )

    def __repr__(self) -> str:
        return f"<Environment(id={self.environment_id}, name='{self.environment_name}')>"


class Model(Base, TimestampMixin):
    """Top-level model entity."""

    __tablename__ = "models"

    model_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    model_name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    team_id: Mapped[int] = mapped_column(Integer, ForeignKey("teams.team_id", ondelete="SET NULL"))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    team: Mapped["Team"] = relationship("Team", back_populates="models")
    versions: Mapped[List["ModelVersion"]] = relationship(
        "ModelVersion",
        back_populates="model",
        cascade="all, delete-orphan",
        order_by="ModelVersion.registered_at.desc()",
    )
    tags: Mapped[List["Tag"]] = relationship("Tag", secondary=model_tags, back_populates="models")

    def __repr__(self) -> str:
        return f"<Model(id={self.model_id}, name='{self.model_name}', versions={len(self.versions)})>"


class ModelVersion(Base, TimestampMixin):
    """Versions of a model (semantic versioning)."""

    __tablename__ = "model_versions"

    version_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    model_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("models.model_id", ondelete="CASCADE"),
        nullable=False,
    )
    semver: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g., "1.2.3"
    artifact_uri: Mapped[str] = mapped_column(String(500), nullable=False)
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)
    registered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    registered_by: Mapped[Optional[str]] = mapped_column(String(255))

    # Relationships
    model: Mapped["Model"] = relationship("Model", back_populates="versions")
    deployments: Mapped[List["Deployment"]] = relationship(
        "Deployment",
        back_populates="version",
        cascade="all, delete-orphan",
    )
    approvals: Mapped[List["Approval"]] = relationship(
        "Approval",
        back_populates="version",
        cascade="all, delete-orphan",
    )
    training_runs: Mapped[List["TrainingRun"]] = relationship(
        "TrainingRun",
        back_populates="model_version",
    )

    __table_args__ = (
        UniqueConstraint("model_id", "semver", name="unique_model_version"),
        Index("idx_model_versions_registered_at", "registered_at"),
    )

    def __repr__(self) -> str:
        return f"<ModelVersion(id={self.version_id}, model={self.model_id}, semver='{self.semver}')>"


class TrainingRun(Base, TimestampMixin):
    """Training run records with hyperparameters and metrics."""

    __tablename__ = "training_runs"

    run_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    model_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    framework: Mapped[str] = mapped_column(
        SQLEnum(FrameworkEnum, name="framework_enum", create_type=False),
        nullable=False,
    )
    experiment_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    run_name: Mapped[Optional[str]] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(
        SQLEnum(RunStatusEnum, name="run_status_enum", create_type=False),
        nullable=False,
        default=RunStatusEnum.QUEUED,
        index=True,
    )

    # Metrics
    accuracy: Mapped[Optional[float]] = mapped_column(Numeric(5, 4))
    loss: Mapped[Optional[float]] = mapped_column(Numeric(8, 5))
    f1_score: Mapped[Optional[float]] = mapped_column(Numeric(5, 4))
    precision: Mapped[Optional[float]] = mapped_column(Numeric(5, 4))
    recall: Mapped[Optional[float]] = mapped_column(Numeric(5, 4))

    # Hyperparameters and metadata
    hyperparameters: Mapped[dict] = mapped_column(JSONB, default=dict)
    metrics: Mapped[dict] = mapped_column(JSONB, default=dict)
    tags_json: Mapped[dict] = mapped_column("tags", JSONB, default=dict)

    # Execution details
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    duration_seconds: Mapped[Optional[int]] = mapped_column(Integer)
    git_commit_hash: Mapped[Optional[str]] = mapped_column(String(40))
    run_by: Mapped[Optional[str]] = mapped_column(String(255))
    artifact_uri: Mapped[Optional[str]] = mapped_column(String(500))

    # Foreign keys
    version_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("model_versions.version_id", ondelete="SET NULL"),
    )

    # Relationships
    model_version: Mapped[Optional["ModelVersion"]] = relationship("ModelVersion", back_populates="training_runs")
    datasets: Mapped[List["Dataset"]] = relationship("Dataset", secondary=run_datasets, back_populates="training_runs")

    __table_args__ = (
        Index("idx_training_runs_experiment_status", "experiment_name", "status"),
        Index("idx_training_runs_started_at", "started_at"),
        CheckConstraint("accuracy IS NULL OR (accuracy >= 0 AND accuracy <= 1)", name="valid_accuracy"),
        CheckConstraint("loss IS NULL OR loss >= 0", name="valid_loss"),
    )

    def __repr__(self) -> str:
        return f"<TrainingRun(id={self.run_id}, model='{self.model_name}', status='{self.status}')>"


class Deployment(Base, TimestampMixin):
    """Model deployments to specific environments."""

    __tablename__ = "deployments"

    deployment_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    version_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("model_versions.version_id", ondelete="RESTRICT"),
        nullable=False,
    )
    environment_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("environments.environment_id", ondelete="RESTRICT"),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        SQLEnum(DeploymentStatusEnum, name="deployment_status_enum", create_type=False),
        nullable=False,
        default=DeploymentStatusEnum.PENDING,
    )
    deployed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    deployed_by: Mapped[str] = mapped_column(String(255), nullable=False)
    endpoint_url: Mapped[Optional[str]] = mapped_column(String(500))
    replicas: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    cpu_limit: Mapped[Optional[str]] = mapped_column(String(20))
    memory_limit: Mapped[Optional[str]] = mapped_column(String(20))
    gpu_count: Mapped[int] = mapped_column(Integer, default=0)
    config: Mapped[dict] = mapped_column(JSONB, default=dict)
    rollback_version_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True))

    # Relationships
    version: Mapped["ModelVersion"] = relationship("ModelVersion", back_populates="deployments")
    environment: Mapped["Environment"] = relationship("Environment", back_populates="deployments")

    __table_args__ = (
        Index("idx_deployments_environment_status", "environment_id", "status"),
        Index("idx_deployments_deployed_at", "deployed_at"),
        CheckConstraint("replicas >= 0", name="valid_replicas"),
        CheckConstraint("gpu_count >= 0", name="valid_gpu_count"),
    )

    def __repr__(self) -> str:
        return f"<Deployment(id={self.deployment_id}, version={self.version_id}, env={self.environment_id})>"


class Dataset(Base, TimestampMixin):
    """Datasets used for training."""

    __tablename__ = "datasets"

    dataset_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    dataset_name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    storage_uri: Mapped[str] = mapped_column(String(500), nullable=False)
    size_bytes: Mapped[Optional[int]] = mapped_column(Integer)
    row_count: Mapped[Optional[int]] = mapped_column(Integer)
    schema_: Mapped[dict] = mapped_column("schema", JSONB, default=dict)
    checksum: Mapped[Optional[str]] = mapped_column(String(64))  # SHA-256

    # Relationships
    training_runs: Mapped[List["TrainingRun"]] = relationship(
        "TrainingRun",
        secondary=run_datasets,
        back_populates="datasets",
    )
    tags: Mapped[List["Tag"]] = relationship("Tag", secondary=dataset_tags, back_populates="datasets")

    def __repr__(self) -> str:
        return f"<Dataset(id={self.dataset_id}, name='{self.dataset_name}')>"


class Approval(Base):
    """Approval workflow for model versions."""

    __tablename__ = "approvals"

    approval_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    version_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("model_versions.version_id", ondelete="CASCADE"),
        nullable=False,
    )
    approver: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(
        SQLEnum(ApprovalStatusEnum, name="approval_status_enum", create_type=False),
        nullable=False,
        default=ApprovalStatusEnum.PENDING,
    )
    comments: Mapped[Optional[str]] = mapped_column(Text)
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    version: Mapped["ModelVersion"] = relationship("ModelVersion", back_populates="approvals")

    __table_args__ = (
        Index("idx_approvals_status", "status"),
    )

    def __repr__(self) -> str:
        return f"<Approval(id={self.approval_id}, version={self.version_id}, status='{self.status}')>"


class Tag(Base):
    """Tags for categorization (many-to-many with models and datasets)."""

    __tablename__ = "tags"

    tag_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tag_name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    category: Mapped[Optional[str]] = mapped_column(String(50))  # e.g., "framework", "domain", "team"
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    models: Mapped[List["Model"]] = relationship("Model", secondary=model_tags, back_populates="tags")
    datasets: Mapped[List["Dataset"]] = relationship("Dataset", secondary=dataset_tags, back_populates="tags")

    def __repr__(self) -> str:
        return f"<Tag(id={self.tag_id}, name='{self.tag_name}', category='{self.category}')>"
```

### Understanding SQLAlchemy 2.0 Patterns

**Key Features Used:**

1. **Mapped[Type] Annotations**: Type hints for better IDE support and mypy checking
2. **mapped_column()**: New SQLAlchemy 2.0 API replacing Column()
3. **relationship()**: Define ORM relationships (one-to-many, many-to-many)
4. **Mixins**: Reusable patterns (TimestampMixin) for DRY code
5. **Enums**: Type-safe status fields
6. **JSONB**: PostgreSQL-specific JSON storage with indexing support
7. **Cascade Rules**: Control deletion behavior (CASCADE, RESTRICT, SET NULL)
8. **Indexes**: Optimize query performance

**Relationship Patterns:**

```python
# One-to-Many (Model has many ModelVersions)
class Model(Base):
    versions: Mapped[List["ModelVersion"]] = relationship(
        "ModelVersion",
        back_populates="model",
        cascade="all, delete-orphan",  # Delete versions when model deleted
    )

class ModelVersion(Base):
    model: Mapped["Model"] = relationship("Model", back_populates="versions")

# Many-to-Many (Models have many Tags through model_tags junction table)
model_tags = Table("model_tags", Base.metadata, ...)

class Model(Base):
    tags: Mapped[List["Tag"]] = relationship("Tag", secondary=model_tags)
```

### Checkpoint 3

Test your models:

```bash
# Create test script
cat > test_models.py << 'EOF'
from ml_registry_db.models import Model, ModelVersion, TrainingRun
from ml_registry_db.db import get_engine, Base

engine = get_engine()
Base.metadata.create_all(engine)
print("✅ All tables created successfully!")

# Show tables
from sqlalchemy import inspect
inspector = inspect(engine)
tables = inspector.get_table_names()
print(f"✅ Tables: {tables}")
EOF

python test_models.py
```

---

## Part 5: Pydantic Schemas for API Validation

### Step 5.1: Create Pydantic Schemas

Create `src/ml_registry_db/schemas.py`:

```python
"""
Pydantic models for request/response validation.
Used for FastAPI integration and data validation.
"""
from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


# ============================================================================
# Base Schemas
# ============================================================================

class BaseSchema(BaseModel):
    """Base schema with ORM mode enabled."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


# ============================================================================
# Team Schemas
# ============================================================================

class TeamBase(BaseSchema):
    team_name: str = Field(..., max_length=100, examples=["ml-platform-team"])
    team_email: str = Field(..., max_length=255, examples=["ml-team@company.com"])
    team_slack_channel: Optional[str] = Field(None, max_length=100, examples=["#ml-platform"])


class TeamCreate(TeamBase):
    """Schema for creating a new team."""
    pass


class TeamRead(TeamBase):
    """Schema for reading team data."""
    team_id: int
    created_at: datetime


# ============================================================================
# Model Schemas
# ============================================================================

class ModelBase(BaseSchema):
    model_name: str = Field(..., max_length=255, examples=["fraud-detection-v1"])
    description: Optional[str] = Field(None, examples=["Fraud detection model using XGBoost"])
    team_id: Optional[int] = None
    is_active: bool = True


class ModelCreate(ModelBase):
    """Schema for registering a new model."""
    pass


class ModelUpdate(BaseSchema):
    """Schema for updating model metadata."""
    description: Optional[str] = None
    team_id: Optional[int] = None
    is_active: Optional[bool] = None


class ModelRead(ModelBase):
    """Schema for reading model data."""
    model_id: UUID
    created_at: datetime
    updated_at: datetime


class ModelWithVersions(ModelRead):
    """Model with nested versions."""
    versions: List["ModelVersionRead"] = []


# ============================================================================
# Model Version Schemas
# ============================================================================

class ModelVersionBase(BaseSchema):
    semver: str = Field(..., pattern=r"^\d+\.\d+\.\d+$", examples=["1.0.0", "2.1.3"])
    artifact_uri: str = Field(..., max_length=500, examples=["s3://models/fraud-detection/v1.0.0"])
    metadata_: Dict = Field(default_factory=dict, alias="metadata")
    registered_by: Optional[str] = Field(None, max_length=255, examples=["alice@company.com"])


class ModelVersionCreate(ModelVersionBase):
    """Schema for registering a new model version."""
    model_id: UUID


class ModelVersionRead(ModelVersionBase):
    """Schema for reading model version data."""
    version_id: UUID
    model_id: UUID
    registered_at: datetime
    created_at: datetime
    updated_at: datetime


# ============================================================================
# Training Run Schemas
# ============================================================================

class TrainingRunBase(BaseSchema):
    model_name: str = Field(..., max_length=255)
    framework: str = Field(..., pattern="^(pytorch|tensorflow|sklearn|xgboost|jax|mxnet)$")
    experiment_name: str = Field(..., max_length=255)
    run_name: Optional[str] = Field(None, max_length=255)
    hyperparameters: Dict = Field(default_factory=dict)
    tags_json: Dict = Field(default_factory=dict, alias="tags")
    git_commit_hash: Optional[str] = Field(None, pattern=r"^[a-f0-9]{40}$")
    run_by: Optional[str] = None


class TrainingRunCreate(TrainingRunBase):
    """Schema for creating a training run."""
    pass


class TrainingRunUpdate(BaseSchema):
    """Schema for updating a training run (typically status and metrics)."""
    status: Optional[str] = Field(
        None,
        pattern="^(queued|running|succeeded|failed|cancelled|timeout)$",
    )
    accuracy: Optional[float] = Field(None, ge=0, le=1)
    loss: Optional[float] = Field(None, ge=0)
    f1_score: Optional[float] = Field(None, ge=0, le=1)
    precision: Optional[float] = Field(None, ge=0, le=1)
    recall: Optional[float] = Field(None, ge=0, le=1)
    metrics: Optional[Dict] = None
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    duration_seconds: Optional[int] = Field(None, ge=0)
    artifact_uri: Optional[str] = None
    version_id: Optional[UUID] = None


class TrainingRunRead(TrainingRunBase):
    """Schema for reading training run data."""
    run_id: UUID
    status: str
    accuracy: Optional[float] = None
    loss: Optional[float] = None
    f1_score: Optional[float] = None
    precision: Optional[float] = None
    recall: Optional[float] = None
    metrics: Dict
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    artifact_uri: Optional[str] = None
    version_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime


# ============================================================================
# Deployment Schemas
# ============================================================================

class DeploymentBase(BaseSchema):
    version_id: UUID
    environment_id: int
    deployed_by: str = Field(..., max_length=255)
    endpoint_url: Optional[str] = Field(None, max_length=500)
    replicas: int = Field(default=1, ge=0)
    cpu_limit: Optional[str] = Field(None, max_length=20, examples=["500m", "2"])
    memory_limit: Optional[str] = Field(None, max_length=20, examples=["1Gi", "512Mi"])
    gpu_count: int = Field(default=0, ge=0)
    config: Dict = Field(default_factory=dict)


class DeploymentCreate(DeploymentBase):
    """Schema for creating a deployment."""
    pass


class DeploymentUpdate(BaseSchema):
    """Schema for updating deployment status."""
    status: Optional[str] = Field(
        None,
        pattern="^(pending|active|failed|rolled_back|decommissioned)$",
    )
    replicas: Optional[int] = Field(None, ge=0)
    rollback_version_id: Optional[UUID] = None


class DeploymentRead(DeploymentBase):
    """Schema for reading deployment data."""
    deployment_id: UUID
    status: str
    deployed_at: datetime
    rollback_version_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime


# ============================================================================
# Dataset Schemas
# ============================================================================

class DatasetBase(BaseSchema):
    dataset_name: str = Field(..., max_length=255)
    description: Optional[str] = None
    storage_uri: str = Field(..., max_length=500, examples=["s3://datasets/fraud-training-2024"])
    size_bytes: Optional[int] = Field(None, ge=0)
    row_count: Optional[int] = Field(None, ge=0)
    schema_: Dict = Field(default_factory=dict, alias="schema")
    checksum: Optional[str] = Field(None, pattern=r"^[a-f0-9]{64}$")  # SHA-256


class DatasetCreate(DatasetBase):
    """Schema for registering a dataset."""
    pass


class DatasetRead(DatasetBase):
    """Schema for reading dataset data."""
    dataset_id: UUID
    created_at: datetime
    updated_at: datetime


# ============================================================================
# Approval Schemas
# ============================================================================

class ApprovalBase(BaseSchema):
    version_id: UUID
    approver: str = Field(..., max_length=255)
    comments: Optional[str] = None


class ApprovalCreate(ApprovalBase):
    """Schema for submitting an approval."""
    pass


class ApprovalUpdate(BaseSchema):
    """Schema for updating approval status."""
    status: str = Field(..., pattern="^(pending|approved|rejected|revoked)$")
    comments: Optional[str] = None


class ApprovalRead(ApprovalBase):
    """Schema for reading approval data."""
    approval_id: UUID
    status: str
    approved_at: Optional[datetime] = None
    created_at: datetime


# ============================================================================
# Tag Schemas
# ============================================================================

class TagBase(BaseSchema):
    tag_name: str = Field(..., max_length=100, examples=["production", "experimental"])
    category: Optional[str] = Field(None, max_length=50, examples=["environment", "team"])


class TagCreate(TagBase):
    """Schema for creating a tag."""
    pass


class TagRead(TagBase):
    """Schema for reading tag data."""
    tag_id: int
    created_at: datetime


# Update forward references for nested models
ModelWithVersions.model_rebuild()
```

### Why Pydantic?

**Benefits:**

1. **Automatic Validation**: Type checking, field constraints, pattern matching
2. **Serialization**: Automatic JSON encoding/decoding
3. **Documentation**: OpenAPI schema generation for FastAPI
4. **Type Safety**: Full mypy and IDE support
5. **ORM Integration**: `from_attributes=True` converts SQLAlchemy models to Pydantic

**Usage Example:**

```python
from ml_registry_db.schemas import ModelCreate, ModelRead
from ml_registry_db.models import Model

# Request validation
model_data = ModelCreate(
    model_name="fraud-detection",
    description="XGBoost fraud model",
    team_id=1,
)

# Create ORM model
orm_model = Model(**model_data.model_dump())

# Response serialization
response = ModelRead.model_validate(orm_model)
print(response.model_dump_json())
```

---

## Part 6: Repository Pattern Implementation

### Step 6.1: Create Repository Layer

Create `src/ml_registry_db/repositories.py`:

```python
"""
Repository layer for database operations.
Encapsulates CRUD logic and complex queries.
"""
import logging
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, func, and_, or_, desc
from sqlalchemy.orm import Session, selectinload, joinedload
from sqlalchemy.exc import IntegrityError

from . import models, schemas

logger = logging.getLogger(__name__)


# ============================================================================
# Custom Exceptions
# ============================================================================

class RepositoryException(Exception):
    """Base exception for repository operations."""
    pass


class NotFoundError(RepositoryException):
    """Resource not found."""
    pass


class DuplicateError(RepositoryException):
    """Duplicate resource (unique constraint violation)."""
    pass


class ValidationError(RepositoryException):
    """Invalid data or business logic violation."""
    pass


# ============================================================================
# Team Repository
# ============================================================================

def create_team(session: Session, data: schemas.TeamCreate) -> models.Team:
    """Create a new team."""
    try:
        team = models.Team(**data.model_dump())
        session.add(team)
        session.flush()  # Get team_id without committing
        logger.info(f"Team created: {team.team_name}")
        return team
    except IntegrityError as e:
        raise DuplicateError(f"Team '{data.team_name}' already exists") from e


def get_team(session: Session, team_id: int) -> Optional[models.Team]:
    """Get team by ID."""
    return session.get(models.Team, team_id)


def list_teams(session: Session, limit: int = 100) -> List[models.Team]:
    """List all teams."""
    stmt = select(models.Team).limit(limit)
    return list(session.scalars(stmt))


# ============================================================================
# Model Repository
# ============================================================================

def register_model(session: Session, data: schemas.ModelCreate) -> models.Model:
    """
    Register a new ML model.

    Raises:
        DuplicateError: If model with same name already exists
        ValidationError: If team_id is invalid
    """
    # Validate team exists if provided
    if data.team_id:
        team = session.get(models.Team, data.team_id)
        if not team:
            raise ValidationError(f"Team {data.team_id} not found")

    try:
        model = models.Model(**data.model_dump())
        session.add(model)
        session.flush()
        logger.info(f"Model registered: {model.model_name} ({model.model_id})")
        return model
    except IntegrityError as e:
        raise DuplicateError(f"Model '{data.model_name}' already exists") from e


def get_model(session: Session, model_id: UUID) -> Optional[models.Model]:
    """Get model by ID with eager-loaded versions."""
    stmt = (
        select(models.Model)
        .where(models.Model.model_id == model_id)
        .options(selectinload(models.Model.versions))
    )
    return session.scalar(stmt)


def get_model_by_name(session: Session, model_name: str) -> Optional[models.Model]:
    """Get model by name with eager-loaded versions."""
    stmt = (
        select(models.Model)
        .where(models.Model.model_name == model_name)
        .options(selectinload(models.Model.versions))
    )
    return session.scalar(stmt)


def list_models(
    session: Session,
    *,
    team_id: Optional[int] = None,
    is_active: Optional[bool] = None,
    limit: int = 50,
    offset: int = 0,
) -> List[models.Model]:
    """
    List models with optional filtering.

    Args:
        session: Database session
        team_id: Filter by team ID
        is_active: Filter by active status
        limit: Maximum results to return
        offset: Number of results to skip (pagination)
    """
    stmt = select(models.Model).options(selectinload(models.Model.versions))

    if team_id is not None:
        stmt = stmt.where(models.Model.team_id == team_id)
    if is_active is not None:
        stmt = stmt.where(models.Model.is_active == is_active)

    stmt = stmt.order_by(desc(models.Model.created_at)).limit(limit).offset(offset)

    return list(session.scalars(stmt))


def update_model(
    session: Session,
    model_id: UUID,
    data: schemas.ModelUpdate,
) -> models.Model:
    """Update model metadata."""
    model = get_model(session, model_id)
    if not model:
        raise NotFoundError(f"Model {model_id} not found")

    # Update only provided fields
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(model, field, value)

    session.flush()
    logger.info(f"Model updated: {model.model_name}")
    return model


def delete_model(session: Session, model_id: UUID) -> None:
    """
    Delete model and all related versions (cascade).

    WARNING: This is destructive!
    """
    model = get_model(session, model_id)
    if not model:
        raise NotFoundError(f"Model {model_id} not found")

    session.delete(model)
    session.flush()
    logger.warning(f"Model deleted: {model.model_name} ({model_id})")


# ============================================================================
# Model Version Repository
# ============================================================================

def add_model_version(
    session: Session,
    data: schemas.ModelVersionCreate,
) -> models.ModelVersion:
    """
    Register a new model version.

    Raises:
        NotFoundError: If parent model doesn't exist
        DuplicateError: If version already exists for this model
    """
    # Validate parent model exists
    model = get_model(session, data.model_id)
    if not model:
        raise NotFoundError(f"Model {data.model_id} not found")

    try:
        version = models.ModelVersion(**data.model_dump())
        session.add(version)
        session.flush()
        logger.info(f"Version registered: {model.model_name} v{version.semver}")
        return version
    except IntegrityError as e:
        raise DuplicateError(
            f"Version {data.semver} already exists for model {data.model_id}"
        ) from e


def get_model_version(session: Session, version_id: UUID) -> Optional[models.ModelVersion]:
    """Get model version by ID."""
    stmt = (
        select(models.ModelVersion)
        .where(models.ModelVersion.version_id == version_id)
        .options(
            joinedload(models.ModelVersion.model),
            selectinload(models.ModelVersion.deployments),
        )
    )
    return session.scalar(stmt)


def get_latest_model_version(session: Session, model_name: str) -> Optional[models.ModelVersion]:
    """Get the most recent version of a model."""
    stmt = (
        select(models.ModelVersion)
        .join(models.Model)
        .where(models.Model.model_name == model_name)
        .order_by(desc(models.ModelVersion.registered_at))
        .limit(1)
    )
    return session.scalar(stmt)


def list_model_versions(
    session: Session,
    model_id: UUID,
    limit: int = 20,
) -> List[models.ModelVersion]:
    """List all versions for a model."""
    stmt = (
        select(models.ModelVersion)
        .where(models.ModelVersion.model_id == model_id)
        .order_by(desc(models.ModelVersion.registered_at))
        .limit(limit)
    )
    return list(session.scalars(stmt))


# ============================================================================
# Training Run Repository
# ============================================================================

def record_training_run(
    session: Session,
    data: schemas.TrainingRunCreate,
) -> models.TrainingRun:
    """Record a new training run."""
    run = models.TrainingRun(**data.model_dump())
    session.add(run)
    session.flush()
    logger.info(f"Training run recorded: {run.run_id} ({run.model_name})")
    return run


def get_training_run(session: Session, run_id: UUID) -> Optional[models.TrainingRun]:
    """Get training run by ID."""
    return session.get(models.TrainingRun, run_id)


def update_training_run(
    session: Session,
    run_id: UUID,
    data: schemas.TrainingRunUpdate,
) -> models.TrainingRun:
    """
    Update training run (typically status and metrics).
    """
    run = get_training_run(session, run_id)
    if not run:
        raise NotFoundError(f"Training run {run_id} not found")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(run, field, value)

    session.flush()
    logger.info(f"Training run updated: {run_id} (status={run.status})")
    return run


def list_training_runs(
    session: Session,
    *,
    model_name: Optional[str] = None,
    experiment_name: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
) -> List[models.TrainingRun]:
    """List training runs with optional filtering."""
    stmt = select(models.TrainingRun)

    if model_name:
        stmt = stmt.where(models.TrainingRun.model_name == model_name)
    if experiment_name:
        stmt = stmt.where(models.TrainingRun.experiment_name == experiment_name)
    if status:
        stmt = stmt.where(models.TrainingRun.status == status)

    stmt = stmt.order_by(desc(models.TrainingRun.created_at)).limit(limit).offset(offset)

    return list(session.scalars(stmt))


def get_best_training_run(
    session: Session,
    model_name: str,
    metric: str = "accuracy",
    maximize: bool = True,
) -> Optional[models.TrainingRun]:
    """
    Get best training run for a model based on metric.

    Args:
        session: Database session
        model_name: Model name
        metric: Metric name (accuracy, loss, f1_score, etc.)
        maximize: True to get highest value, False for lowest
    """
    # Only consider successful runs
    stmt = (
        select(models.TrainingRun)
        .where(
            and_(
                models.TrainingRun.model_name == model_name,
                models.TrainingRun.status == "succeeded",
            )
        )
    )

    # Order by metric (ascending or descending)
    metric_col = getattr(models.TrainingRun, metric, None)
    if not metric_col:
        raise ValidationError(f"Invalid metric: {metric}")

    if maximize:
        stmt = stmt.order_by(desc(metric_col))
    else:
        stmt = stmt.order_by(metric_col)

    stmt = stmt.limit(1)

    return session.scalar(stmt)


# ============================================================================
# Deployment Repository
# ============================================================================

def create_deployment(
    session: Session,
    data: schemas.DeploymentCreate,
) -> models.Deployment:
    """
    Create a new deployment.

    Raises:
        NotFoundError: If version or environment doesn't exist
    """
    # Validate version exists
    version = get_model_version(session, data.version_id)
    if not version:
        raise NotFoundError(f"Model version {data.version_id} not found")

    # Validate environment exists
    env = session.get(models.Environment, data.environment_id)
    if not env:
        raise NotFoundError(f"Environment {data.environment_id} not found")

    deployment = models.Deployment(**data.model_dump())
    session.add(deployment)
    session.flush()
    logger.info(f"Deployment created: {deployment.deployment_id} to {env.environment_name}")
    return deployment


def get_deployment(session: Session, deployment_id: UUID) -> Optional[models.Deployment]:
    """Get deployment by ID."""
    stmt = (
        select(models.Deployment)
        .where(models.Deployment.deployment_id == deployment_id)
        .options(
            joinedload(models.Deployment.version).joinedload(models.ModelVersion.model),
            joinedload(models.Deployment.environment),
        )
    )
    return session.scalar(stmt)


def update_deployment(
    session: Session,
    deployment_id: UUID,
    data: schemas.DeploymentUpdate,
) -> models.Deployment:
    """Update deployment (typically status)."""
    deployment = get_deployment(session, deployment_id)
    if not deployment:
        raise NotFoundError(f"Deployment {deployment_id} not found")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(deployment, field, value)

    session.flush()
    logger.info(f"Deployment updated: {deployment_id} (status={deployment.status})")
    return deployment


def get_latest_deployment(
    session: Session,
    model_name: str,
    environment_name: str = "production",
) -> Optional[models.Deployment]:
    """
    Get latest active deployment for a model in an environment.
    """
    stmt = (
        select(models.Deployment)
        .join(models.ModelVersion)
        .join(models.Model)
        .join(models.Environment)
        .where(
            and_(
                models.Model.model_name == model_name,
                models.Environment.environment_name == environment_name,
                models.Deployment.status == "active",
            )
        )
        .order_by(desc(models.Deployment.deployed_at))
        .limit(1)
    )
    return session.scalar(stmt)


def list_deployments(
    session: Session,
    *,
    model_name: Optional[str] = None,
    environment_id: Optional[int] = None,
    status: Optional[str] = None,
    limit: int = 50,
) -> List[models.Deployment]:
    """List deployments with optional filtering."""
    stmt = (
        select(models.Deployment)
        .options(
            joinedload(models.Deployment.version).joinedload(models.ModelVersion.model),
            joinedload(models.Deployment.environment),
        )
    )

    if model_name:
        stmt = stmt.join(models.ModelVersion).join(models.Model).where(
            models.Model.model_name == model_name
        )
    if environment_id:
        stmt = stmt.where(models.Deployment.environment_id == environment_id)
    if status:
        stmt = stmt.where(models.Deployment.status == status)

    stmt = stmt.order_by(desc(models.Deployment.deployed_at)).limit(limit)

    return list(session.scalars(stmt))


# ============================================================================
# Dataset Repository
# ============================================================================

def register_dataset(session: Session, data: schemas.DatasetCreate) -> models.Dataset:
    """Register a new dataset."""
    try:
        dataset = models.Dataset(**data.model_dump())
        session.add(dataset)
        session.flush()
        logger.info(f"Dataset registered: {dataset.dataset_name}")
        return dataset
    except IntegrityError as e:
        raise DuplicateError(f"Dataset '{data.dataset_name}' already exists") from e


def get_dataset(session: Session, dataset_id: UUID) -> Optional[models.Dataset]:
    """Get dataset by ID."""
    return session.get(models.Dataset, dataset_id)


def get_dataset_by_name(session: Session, dataset_name: str) -> Optional[models.Dataset]:
    """Get dataset by name."""
    stmt = select(models.Dataset).where(models.Dataset.dataset_name == dataset_name)
    return session.scalar(stmt)


def list_datasets(session: Session, limit: int = 50) -> List[models.Dataset]:
    """List all datasets."""
    stmt = select(models.Dataset).order_by(desc(models.Dataset.created_at)).limit(limit)
    return list(session.scalars(stmt))


# ============================================================================
# Approval Repository
# ============================================================================

def create_approval(session: Session, data: schemas.ApprovalCreate) -> models.Approval:
    """Submit approval request for a model version."""
    # Validate version exists
    version = get_model_version(session, data.version_id)
    if not version:
        raise NotFoundError(f"Model version {data.version_id} not found")

    approval = models.Approval(**data.model_dump())
    session.add(approval)
    session.flush()
    logger.info(f"Approval created: {approval.approval_id} for version {data.version_id}")
    return approval


def update_approval(
    session: Session,
    approval_id: UUID,
    data: schemas.ApprovalUpdate,
) -> models.Approval:
    """Update approval status."""
    approval = session.get(models.Approval, approval_id)
    if not approval:
        raise NotFoundError(f"Approval {approval_id} not found")

    # Set approved_at timestamp if transitioning to approved
    if data.status == "approved" and approval.status != "approved":
        approval.approved_at = datetime.utcnow()

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(approval, field, value)

    session.flush()
    logger.info(f"Approval updated: {approval_id} (status={approval.status})")
    return approval


def list_approvals(
    session: Session,
    version_id: UUID,
) -> List[models.Approval]:
    """List all approvals for a model version."""
    stmt = (
        select(models.Approval)
        .where(models.Approval.version_id == version_id)
        .order_by(desc(models.Approval.created_at))
    )
    return list(session.scalars(stmt))


# ============================================================================
# Tag Repository
# ============================================================================

def create_tag(session: Session, data: schemas.TagCreate) -> models.Tag:
    """Create a new tag."""
    try:
        tag = models.Tag(**data.model_dump())
        session.add(tag)
        session.flush()
        logger.info(f"Tag created: {tag.tag_name}")
        return tag
    except IntegrityError as e:
        raise DuplicateError(f"Tag '{data.tag_name}' already exists") from e


def get_tag_by_name(session: Session, tag_name: str) -> Optional[models.Tag]:
    """Get tag by name."""
    stmt = select(models.Tag).where(models.Tag.tag_name == tag_name)
    return session.scalar(stmt)


def list_tags(session: Session, category: Optional[str] = None) -> List[models.Tag]:
    """List tags, optionally filtered by category."""
    stmt = select(models.Tag)
    if category:
        stmt = stmt.where(models.Tag.category == category)
    return list(session.scalars(stmt))


def add_tag_to_model(session: Session, model_id: UUID, tag_name: str) -> None:
    """Add tag to model (creates tag if it doesn't exist)."""
    model = get_model(session, model_id)
    if not model:
        raise NotFoundError(f"Model {model_id} not found")

    tag = get_tag_by_name(session, tag_name)
    if not tag:
        tag = create_tag(session, schemas.TagCreate(tag_name=tag_name))

    if tag not in model.tags:
        model.tags.append(tag)
        session.flush()
        logger.info(f"Tag '{tag_name}' added to model {model.model_name}")


def remove_tag_from_model(session: Session, model_id: UUID, tag_name: str) -> None:
    """Remove tag from model."""
    model = get_model(session, model_id)
    if not model:
        raise NotFoundError(f"Model {model_id} not found")

    tag = get_tag_by_name(session, tag_name)
    if tag and tag in model.tags:
        model.tags.remove(tag)
        session.flush()
        logger.info(f"Tag '{tag_name}' removed from model {model.model_name}")
```

### Repository Pattern Benefits

**Why use repositories?**

1. **Separation of Concerns**: Business logic separated from database access
2. **Testability**: Easy to mock repositories in unit tests
3. **Reusability**: Common queries encapsulated in functions
4. **Consistency**: Standardized error handling and logging
5. **Maintainability**: Changes to queries in one place

**Key Patterns:**

- **Eager Loading**: Use `selectinload()` and `joinedload()` to avoid N+1 queries
- **Custom Exceptions**: Clear error types (NotFoundError, DuplicateError, ValidationError)
- **Filtering**: Optional parameters for flexible queries
- **Pagination**: limit/offset for large result sets
- **Transaction Management**: flush() within functions, commit() in calling code

### Checkpoint 4

Test repositories:

```bash
cat > test_repos.py << 'EOF'
from ml_registry_db.db import get_session, reset_db
from ml_registry_db import repositories, schemas

# Reset database
reset_db()

with get_session() as session:
    # Create team
    team = repositories.create_team(
        session,
        schemas.TeamCreate(
            team_name="ml-platform",
            team_email="ml@company.com",
        ),
    )
    print(f"✅ Team created: {team}")

    # Register model
    model = repositories.register_model(
        session,
        schemas.ModelCreate(
            model_name="fraud-detection",
            description="XGBoost fraud detection",
            team_id=team.team_id,
        ),
    )
    print(f"✅ Model registered: {model}")

    # Add version
    version = repositories.add_model_version(
        session,
        schemas.ModelVersionCreate(
            model_id=model.model_id,
            semver="1.0.0",
            artifact_uri="s3://models/fraud-v1",
        ),
    )
    print(f"✅ Version added: {version}")

print("✅ All repository operations successful!")
EOF

python test_repos.py
```

---

## Part 7: Alembic Database Migrations

### Step 7.1: Initialize Alembic

```bash
# Initialize Alembic in the project
alembic init alembic

# This creates:
# alembic/
# ├── env.py
# ├── script.py.mako
# ├── versions/
# └── alembic.ini (in project root)
```

### Step 7.2: Configure Alembic

Edit `alembic/env.py` to import your models and use your database URL:

```python
"""Alembic environment configuration."""
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context

# Import your models' metadata
from ml_registry_db.db import Base
from ml_registry_db.config import settings
import ml_registry_db.models  # Important: registers models with Base

# this is the Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set target metadata for autogenerate support
target_metadata = Base.metadata

# Override sqlalchemy.url from settings
config.set_main_option("sqlalchemy.url", str(settings.database_url))


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

### Step 7.3: Create Initial Migration

```bash
# Generate initial migration from models
alembic revision --autogenerate -m "create initial schema"

# This creates a file like:
# alembic/versions/abc123_create_initial_schema.py

# Review the migration file, then apply it:
alembic upgrade head

# Check migration status:
alembic current

# Expected output:
# abc123 (head)
```

### Step 7.4: Common Migration Commands

```bash
# Create a new migration
alembic revision --autogenerate -m "add new column"

# Apply all pending migrations
alembic upgrade head

# Rollback last migration
alembic downgrade -1

# Show migration history
alembic history --verbose

# Rollback to specific version
alembic downgrade abc123

# Show current version
alembic current

# Generate SQL without applying (dry run)
alembic upgrade head --sql

# Stamp database with version (without running migrations)
alembic stamp head
```

### Schema Evolution Example

Let's say you want to add a `priority` field to training runs:

1. **Modify model**:

```python
# In models.py, add to TrainingRun:
priority: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
```

2. **Generate migration**:

```bash
alembic revision --autogenerate -m "add priority to training runs"
```

3. **Review generated migration**:

```python
# alembic/versions/def456_add_priority_to_training_runs.py

def upgrade() -> None:
    op.add_column('training_runs',
        sa.Column('priority', sa.Integer(), nullable=False, server_default='5')
    )

def downgrade() -> None:
    op.drop_column('training_runs', 'priority')
```

4. **Apply migration**:

```bash
alembic upgrade head
```

### Production Migration Workflow

**Best Practices:**

1. **Review Generated Migrations**: Always check autogenerated migrations
2. **Test Migrations**: Test on staging before production
3. **Backup Data**: Always backup before production migrations
4. **Downgrade Path**: Ensure `downgrade()` functions work
5. **Data Migrations**: Separate schema and data migrations
6. **Zero-Downtime**: Use techniques like:
   - Add new column with default
   - Backfill data
   - Switch application code
   - Remove old column in next release

---

## Part 8: Testing with Pytest

### Step 8.1: Create Test Fixtures

Create `tests/conftest.py`:

```python
"""Pytest configuration and fixtures."""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from ml_registry_db.db import Base
from ml_registry_db.config import settings


@pytest.fixture(scope="session")
def test_engine():
    """Create test database engine."""
    # Use test database URL
    test_url = str(settings.test_database_url)
    engine = create_engine(test_url, echo=False)

    # Create all tables
    Base.metadata.create_all(engine)

    yield engine

    # Cleanup: drop all tables after tests
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture(scope="function")
def session(test_engine):
    """
    Create a new database session for each test.
    Uses a transaction that is rolled back after the test.
    """
    connection = test_engine.connect()
    transaction = connection.begin()

    SessionLocal = sessionmaker(bind=connection)
    session = SessionLocal()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def sample_team(session: Session):
    """Create a sample team for testing."""
    from ml_registry_db import models

    team = models.Team(
        team_name="test-team",
        team_email="test@company.com",
    )
    session.add(team)
    session.commit()
    session.refresh(team)
    return team


@pytest.fixture
def sample_model(session: Session, sample_team):
    """Create a sample model for testing."""
    from ml_registry_db import models

    model = models.Model(
        model_name="test-model",
        description="Test ML model",
        team_id=sample_team.team_id,
    )
    session.add(model)
    session.commit()
    session.refresh(model)
    return model


@pytest.fixture
def sample_model_version(session: Session, sample_model):
    """Create a sample model version for testing."""
    from ml_registry_db import models

    version = models.ModelVersion(
        model_id=sample_model.model_id,
        semver="1.0.0",
        artifact_uri="s3://test/model-v1",
        metadata_={"framework": "pytorch"},
    )
    session.add(version)
    session.commit()
    session.refresh(version)
    return version


@pytest.fixture
def sample_environment(session: Session):
    """Create a sample environment for testing."""
    from ml_registry_db import models

    env = models.Environment(
        environment_name="production",
        description="Production environment",
    )
    session.add(env)
    session.commit()
    session.refresh(env)
    return env
```

### Step 8.2: Create Model Tests

Create `tests/test_models.py`:

```python
"""Tests for ORM models."""
import pytest
from sqlalchemy.exc import IntegrityError

from ml_registry_db import models


def test_create_team(session):
    """Test creating a team."""
    team = models.Team(
        team_name="ml-team",
        team_email="ml@company.com",
        team_slack_channel="#ml-platform",
    )
    session.add(team)
    session.commit()

    assert team.team_id is not None
    assert team.team_name == "ml-team"
    assert team.created_at is not None


def test_create_model_with_team(session, sample_team):
    """Test creating a model linked to a team."""
    model = models.Model(
        model_name="fraud-detection",
        description="Fraud detection model",
        team_id=sample_team.team_id,
    )
    session.add(model)
    session.commit()

    assert model.model_id is not None
    assert model.team.team_name == sample_team.team_name


def test_model_version_relationship(session, sample_model):
    """Test one-to-many relationship between Model and ModelVersion."""
    # Create two versions
    v1 = models.ModelVersion(
        model_id=sample_model.model_id,
        semver="1.0.0",
        artifact_uri="s3://models/v1",
    )
    v2 = models.ModelVersion(
        model_id=sample_model.model_id,
        semver="1.1.0",
        artifact_uri="s3://models/v1.1",
    )
    session.add_all([v1, v2])
    session.commit()

    # Refresh model to load versions
    session.refresh(sample_model)

    assert len(sample_model.versions) == 2
    assert sample_model.versions[0].model_id == sample_model.model_id


def test_duplicate_model_name_fails(session):
    """Test that duplicate model names are rejected."""
    model1 = models.Model(model_name="duplicate-test")
    model2 = models.Model(model_name="duplicate-test")

    session.add(model1)
    session.commit()

    session.add(model2)
    with pytest.raises(IntegrityError):
        session.commit()


def test_cascade_delete_model_versions(session, sample_model):
    """Test that deleting a model cascades to versions."""
    # Create version
    version = models.ModelVersion(
        model_id=sample_model.model_id,
        semver="1.0.0",
        artifact_uri="s3://test",
    )
    session.add(version)
    session.commit()

    version_id = version.version_id

    # Delete model
    session.delete(sample_model)
    session.commit()

    # Version should be deleted too
    deleted_version = session.get(models.ModelVersion, version_id)
    assert deleted_version is None


def test_training_run_creation(session):
    """Test creating a training run with metrics."""
    run = models.TrainingRun(
        model_name="test-model",
        framework=models.FrameworkEnum.PYTORCH,
        experiment_name="exp-001",
        status=models.RunStatusEnum.SUCCEEDED,
        accuracy=0.95,
        loss=0.12,
        hyperparameters={"lr": 0.001, "batch_size": 32},
    )
    session.add(run)
    session.commit()

    assert run.run_id is not None
    assert run.accuracy == 0.95
    assert run.hyperparameters["lr"] == 0.001


def test_deployment_foreign_key_constraint(session, sample_model_version, sample_environment):
    """Test that deployment requires valid version and environment."""
    deployment = models.Deployment(
        version_id=sample_model_version.version_id,
        environment_id=sample_environment.environment_id,
        deployed_by="alice@company.com",
        replicas=3,
    )
    session.add(deployment)
    session.commit()

    assert deployment.deployment_id is not None
    assert deployment.version.version_id == sample_model_version.version_id


def test_many_to_many_model_tags(session, sample_model):
    """Test many-to-many relationship between models and tags."""
    tag1 = models.Tag(tag_name="production", category="environment")
    tag2 = models.Tag(tag_name="critical", category="priority")

    session.add_all([tag1, tag2])
    session.commit()

    # Add tags to model
    sample_model.tags.append(tag1)
    sample_model.tags.append(tag2)
    session.commit()

    # Refresh and verify
    session.refresh(sample_model)
    assert len(sample_model.tags) == 2
    assert tag1 in sample_model.tags
```

### Step 8.3: Create Repository Tests

Create `tests/test_repositories.py`:

```python
"""Tests for repository layer."""
import pytest

from ml_registry_db import repositories, schemas


def test_register_model(session, sample_team):
    """Test registering a new model."""
    data = schemas.ModelCreate(
        model_name="new-model",
        description="Test model",
        team_id=sample_team.team_id,
    )

    model = repositories.register_model(session, data)
    session.commit()

    assert model.model_id is not None
    assert model.model_name == "new-model"


def test_register_duplicate_model_fails(session):
    """Test that registering duplicate model raises DuplicateError."""
    data = schemas.ModelCreate(model_name="duplicate-model")

    repositories.register_model(session, data)
    session.commit()

    with pytest.raises(repositories.DuplicateError):
        repositories.register_model(session, data)
        session.commit()


def test_get_model_by_name(session, sample_model):
    """Test retrieving model by name."""
    model = repositories.get_model_by_name(session, sample_model.model_name)

    assert model is not None
    assert model.model_id == sample_model.model_id


def test_list_models_with_filters(session, sample_team):
    """Test listing models with team filter."""
    # Create models for different teams
    data1 = schemas.ModelCreate(model_name="team1-model", team_id=sample_team.team_id)
    data2 = schemas.ModelCreate(model_name="team2-model")

    repositories.register_model(session, data1)
    repositories.register_model(session, data2)
    session.commit()

    # Filter by team
    team_models = repositories.list_models(session, team_id=sample_team.team_id)

    assert len(team_models) >= 1
    assert all(m.team_id == sample_team.team_id for m in team_models)


def test_add_model_version(session, sample_model):
    """Test adding a version to a model."""
    data = schemas.ModelVersionCreate(
        model_id=sample_model.model_id,
        semver="2.0.0",
        artifact_uri="s3://models/v2",
    )

    version = repositories.add_model_version(session, data)
    session.commit()

    assert version.version_id is not None
    assert version.semver == "2.0.0"


def test_get_latest_model_version(session, sample_model):
    """Test retrieving the latest version of a model."""
    # Create multiple versions
    for i in range(3):
        data = schemas.ModelVersionCreate(
            model_id=sample_model.model_id,
            semver=f"1.{i}.0",
            artifact_uri=f"s3://models/v1.{i}",
        )
        repositories.add_model_version(session, data)
    session.commit()

    latest = repositories.get_latest_model_version(session, sample_model.model_name)

    assert latest is not None
    assert latest.semver == "1.2.0"  # Last version created


def test_record_training_run(session):
    """Test recording a training run."""
    data = schemas.TrainingRunCreate(
        model_name="test-model",
        framework="pytorch",
        experiment_name="exp-001",
        hyperparameters={"lr": 0.001},
    )

    run = repositories.record_training_run(session, data)
    session.commit()

    assert run.run_id is not None
    assert run.status == "queued"


def test_update_training_run_status(session):
    """Test updating training run with results."""
    # Create run
    data = schemas.TrainingRunCreate(
        model_name="test-model",
        framework="pytorch",
        experiment_name="exp-001",
    )
    run = repositories.record_training_run(session, data)
    session.commit()

    # Update with results
    update_data = schemas.TrainingRunUpdate(
        status="succeeded",
        accuracy=0.92,
        loss=0.15,
    )
    updated_run = repositories.update_training_run(session, run.run_id, update_data)
    session.commit()

    assert updated_run.status == "succeeded"
    assert updated_run.accuracy == 0.92


def test_get_best_training_run(session):
    """Test finding best training run by metric."""
    # Create multiple runs with different accuracies
    for i, acc in enumerate([0.85, 0.92, 0.88]):
        data = schemas.TrainingRunCreate(
            model_name="test-model",
            framework="pytorch",
            experiment_name="exp-001",
            run_name=f"run-{i}",
        )
        run = repositories.record_training_run(session, data)

        # Update with results
        update = schemas.TrainingRunUpdate(status="succeeded", accuracy=acc)
        repositories.update_training_run(session, run.run_id, update)
    session.commit()

    best = repositories.get_best_training_run(session, "test-model", metric="accuracy")

    assert best is not None
    assert best.accuracy == 0.92


def test_create_deployment(session, sample_model_version, sample_environment):
    """Test creating a deployment."""
    data = schemas.DeploymentCreate(
        version_id=sample_model_version.version_id,
        environment_id=sample_environment.environment_id,
        deployed_by="alice@company.com",
        replicas=2,
    )

    deployment = repositories.create_deployment(session, data)
    session.commit()

    assert deployment.deployment_id is not None
    assert deployment.replicas == 2


def test_get_latest_deployment(session, sample_model, sample_model_version, sample_environment):
    """Test retrieving latest active deployment."""
    # Create deployment
    data = schemas.DeploymentCreate(
        version_id=sample_model_version.version_id,
        environment_id=sample_environment.environment_id,
        deployed_by="alice@company.com",
    )
    deployment = repositories.create_deployment(session, data)

    # Mark as active
    update = schemas.DeploymentUpdate(status="active")
    repositories.update_deployment(session, deployment.deployment_id, update)
    session.commit()

    latest = repositories.get_latest_deployment(
        session,
        sample_model.model_name,
        sample_environment.environment_name,
    )

    assert latest is not None
    assert latest.deployment_id == deployment.deployment_id


def test_add_tag_to_model(session, sample_model):
    """Test adding tags to models."""
    repositories.add_tag_to_model(session, sample_model.model_id, "production")
    repositories.add_tag_to_model(session, sample_model.model_id, "critical")
    session.commit()

    session.refresh(sample_model)

    tag_names = [tag.tag_name for tag in sample_model.tags]
    assert "production" in tag_names
    assert "critical" in tag_names
```

### Step 8.4: Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=ml_registry_db --cov-report=html

# Run specific test file
pytest tests/test_repositories.py

# Run specific test
pytest tests/test_models.py::test_create_team

# Run with verbose output
pytest -v

# Expected output:
# tests/test_models.py::test_create_team PASSED
# tests/test_models.py::test_create_model_with_team PASSED
# ...
# ========== 25 passed in 2.45s ==========
```

---

## Part 9: CLI Tools

### Step 9.1: Create CLI Module

Create `src/ml_registry_db/cli.py`:

```python
"""Command-line interface for ml-registry-db."""
import logging
from typing import Optional

import typer
from rich import print as rprint
from rich.console import Console
from rich.table import Table

from . import repositories, schemas
from .db import get_session, init_db, drop_db, get_pool_status

app = typer.Typer(help="ML Registry Database CLI")
console = Console()


@app.command()
def init():
    """Initialize database schema (create all tables)."""
    try:
        init_db()
        rprint("[green]✅ Database schema initialized successfully[/green]")
    except Exception as e:
        rprint(f"[red]❌ Error initializing database: {e}[/red]")
        raise typer.Exit(code=1)


@app.command()
def drop():
    """Drop all database tables (WARNING: destructive!)."""
    confirm = typer.confirm("Are you sure you want to drop all tables?")
    if not confirm:
        rprint("[yellow]Operation cancelled[/yellow]")
        return

    try:
        drop_db()
        rprint("[yellow]⚠️  All tables dropped[/yellow]")
    except Exception as e:
        rprint(f"[red]❌ Error dropping tables: {e}[/red]")
        raise typer.Exit(code=1)


@app.command()
def pool_status():
    """Show connection pool statistics."""
    try:
        stats = get_pool_status()

        table = Table(title="Connection Pool Status")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")

        for key, value in stats.items():
            table.add_row(key.replace("_", " ").title(), str(value))

        console.print(table)
    except Exception as e:
        rprint(f"[red]❌ Error getting pool status: {e}[/red]")


@app.command()
def register_model(
    name: str = typer.Argument(..., help="Model name"),
    description: str = typer.Option(None, help="Model description"),
    team_id: Optional[int] = typer.Option(None, help="Team ID"),
):
    """Register a new ML model."""
    try:
        with get_session() as session:
            data = schemas.ModelCreate(
                model_name=name,
                description=description,
                team_id=team_id,
            )
            model = repositories.register_model(session, data)

            rprint(f"[green]✅ Model registered: {model.model_name}[/green]")
            rprint(f"   Model ID: {model.model_id}")
    except repositories.DuplicateError:
        rprint(f"[red]❌ Model '{name}' already exists[/red]")
        raise typer.Exit(code=1)
    except Exception as e:
        rprint(f"[red]❌ Error: {e}[/red]")
        raise typer.Exit(code=1)


@app.command()
def list_models(
    team_id: Optional[int] = typer.Option(None, help="Filter by team ID"),
    limit: int = typer.Option(20, help="Maximum results"),
):
    """List registered models."""
    try:
        with get_session() as session:
            models = repositories.list_models(
                session,
                team_id=team_id,
                limit=limit,
            )

            if not models:
                rprint("[yellow]No models found[/yellow]")
                return

            table = Table(title=f"Models ({len(models)} found)")
            table.add_column("Model Name", style="cyan")
            table.add_column("Team", style="green")
            table.add_column("Versions", style="yellow")
            table.add_column("Active", style="magenta")

            for model in models:
                table.add_row(
                    model.model_name,
                    model.team.team_name if model.team else "N/A",
                    str(len(model.versions)),
                    "✓" if model.is_active else "✗",
                )

            console.print(table)
    except Exception as e:
        rprint(f"[red]❌ Error: {e}[/red]")
        raise typer.Exit(code=1)


@app.command()
def seed_data():
    """Populate database with sample data for testing."""
    try:
        with get_session() as session:
            # Create teams
            team1 = repositories.create_team(
                session,
                schemas.TeamCreate(
                    team_name="ml-platform",
                    team_email="ml-platform@company.com",
                ),
            )

            team2 = repositories.create_team(
                session,
                schemas.TeamCreate(
                    team_name="data-science",
                    team_email="ds@company.com",
                ),
            )

            # Create models
            fraud_model = repositories.register_model(
                session,
                schemas.ModelCreate(
                    model_name="fraud-detection",
                    description="XGBoost fraud detection model",
                    team_id=team1.team_id,
                ),
            )

            churn_model = repositories.register_model(
                session,
                schemas.ModelCreate(
                    model_name="churn-prediction",
                    description="Customer churn prediction",
                    team_id=team2.team_id,
                ),
            )

            # Add versions
            fraud_v1 = repositories.add_model_version(
                session,
                schemas.ModelVersionCreate(
                    model_id=fraud_model.model_id,
                    semver="1.0.0",
                    artifact_uri="s3://models/fraud/v1.0.0",
                ),
            )

            churn_v1 = repositories.add_model_version(
                session,
                schemas.ModelVersionCreate(
                    model_id=churn_model.model_id,
                    semver="1.0.0",
                    artifact_uri="s3://models/churn/v1.0.0",
                ),
            )

            # Record training runs
            repositories.record_training_run(
                session,
                schemas.TrainingRunCreate(
                    model_name="fraud-detection",
                    framework="xgboost",
                    experiment_name="fraud-exp-001",
                    hyperparameters={"max_depth": 6, "learning_rate": 0.1},
                ),
            )

            rprint("[green]✅ Sample data created successfully[/green]")
            rprint(f"   Teams: 2")
            rprint(f"   Models: 2")
            rprint(f"   Versions: 2")
            rprint(f"   Training runs: 1")

    except Exception as e:
        rprint(f"[red]❌ Error seeding data: {e}[/red]")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
```

### Step 9.2: Use CLI

```bash
# Initialize database
ml-registry init

# Seed with sample data
ml-registry seed-data

# List models
ml-registry list-models

# Register new model
ml-registry register-model "recommendation-engine" \
    --description "Collaborative filtering recommender" \
    --team-id 1

# Show connection pool status
ml-registry pool-status
```

---

## Part 10: FastAPI Integration Example

Create `scripts/fastapi_example.py`:

```python
"""
Example FastAPI application using ml-registry-db.
Demonstrates RESTful API endpoints backed by the database.
"""
from typing import List
from uuid import UUID

from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ml_registry_db import repositories, schemas
from ml_registry_db.db import get_db

app = FastAPI(
    title="ML Model Registry API",
    description="RESTful API for ML model management",
    version="1.0.0",
)


# ============================================================================
# Model Endpoints
# ============================================================================

@app.post("/models", response_model=schemas.ModelRead, status_code=status.HTTP_201_CREATED)
def create_model(
    model_data: schemas.ModelCreate,
    db: Session = Depends(get_db),
):
    """Register a new ML model."""
    try:
        model = repositories.register_model(db, model_data)
        db.commit()
        return model
    except repositories.DuplicateError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except repositories.ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@app.get("/models", response_model=List[schemas.ModelRead])
def list_models(
    team_id: int = None,
    is_active: bool = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    """List all models with optional filtering."""
    models = repositories.list_models(
        db,
        team_id=team_id,
        is_active=is_active,
        limit=limit,
        offset=offset,
    )
    return models


@app.get("/models/{model_id}", response_model=schemas.ModelWithVersions)
def get_model(model_id: UUID, db: Session = Depends(get_db)):
    """Get model by ID with all versions."""
    model = repositories.get_model(db, model_id)
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    return model


@app.patch("/models/{model_id}", response_model=schemas.ModelRead)
def update_model(
    model_id: UUID,
    model_data: schemas.ModelUpdate,
    db: Session = Depends(get_db),
):
    """Update model metadata."""
    try:
        model = repositories.update_model(db, model_id, model_data)
        db.commit()
        return model
    except repositories.NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ============================================================================
# Model Version Endpoints
# ============================================================================

@app.post("/versions", response_model=schemas.ModelVersionRead, status_code=201)
def create_model_version(
    version_data: schemas.ModelVersionCreate,
    db: Session = Depends(get_db),
):
    """Register a new model version."""
    try:
        version = repositories.add_model_version(db, version_data)
        db.commit()
        return version
    except repositories.NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except repositories.DuplicateError as e:
        raise HTTPException(status_code=409, detail=str(e))


@app.get("/models/{model_name}/latest", response_model=schemas.ModelVersionRead)
def get_latest_version(model_name: str, db: Session = Depends(get_db)):
    """Get the latest version of a model."""
    version = repositories.get_latest_model_version(db, model_name)
    if not version:
        raise HTTPException(status_code=404, detail="Model not found or has no versions")
    return version


# ============================================================================
# Training Run Endpoints
# ============================================================================

@app.post("/training-runs", response_model=schemas.TrainingRunRead, status_code=201)
def create_training_run(
    run_data: schemas.TrainingRunCreate,
    db: Session = Depends(get_db),
):
    """Record a new training run."""
    run = repositories.record_training_run(db, run_data)
    db.commit()
    return run


@app.patch("/training-runs/{run_id}", response_model=schemas.TrainingRunRead)
def update_training_run(
    run_id: UUID,
    run_data: schemas.TrainingRunUpdate,
    db: Session = Depends(get_db),
):
    """Update training run with results."""
    try:
        run = repositories.update_training_run(db, run_id, run_data)
        db.commit()
        return run
    except repositories.NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/training-runs", response_model=List[schemas.TrainingRunRead])
def list_training_runs(
    model_name: str = None,
    experiment_name: str = None,
    status: str = None,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    """List training runs with optional filtering."""
    runs = repositories.list_training_runs(
        db,
        model_name=model_name,
        experiment_name=experiment_name,
        status=status,
        limit=limit,
    )
    return runs


# ============================================================================
# Deployment Endpoints
# ============================================================================

@app.post("/deployments", response_model=schemas.DeploymentRead, status_code=201)
def create_deployment(
    deployment_data: schemas.DeploymentCreate,
    db: Session = Depends(get_db),
):
    """Create a new deployment."""
    try:
        deployment = repositories.create_deployment(db, deployment_data)
        db.commit()
        return deployment
    except repositories.NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/deployments/latest", response_model=schemas.DeploymentRead)
def get_latest_deployment(
    model_name: str,
    environment: str = "production",
    db: Session = Depends(get_db),
):
    """Get latest active deployment for a model."""
    deployment = repositories.get_latest_deployment(db, model_name, environment)
    if not deployment:
        raise HTTPException(status_code=404, detail="No active deployment found")
    return deployment


# ============================================================================
# Health Check
# ============================================================================

@app.get("/health")
def health_check():
    """Health check endpoint."""
    from ml_registry_db.db import get_pool_status

    pool_stats = get_pool_status()

    return {
        "status": "healthy",
        "database": "connected",
        "pool": pool_stats,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

Run the API:

```bash
# Install FastAPI and Uvicorn
poetry add fastapi uvicorn

# Run the server
python scripts/fastapi_example.py

# Test endpoints
curl http://localhost:8000/health
curl http://localhost:8000/models

# Access API docs
open http://localhost:8000/docs
```

---

## Part 11: Production Considerations

### Connection Pooling Best Practices

**Development:**

```python
engine = create_engine(
    url,
    pool_size=5,          # Small pool for local dev
    max_overflow=5,
    echo=True,            # Log SQL for debugging
)
```

**Production:**

```python
engine = create_engine(
    url,
    pool_size=20,         # Larger pool for traffic
    max_overflow=40,      # Handle traffic spikes
    pool_recycle=1800,    # Recycle connections every 30 min
    pool_pre_ping=True,   # Check connection health
    echo=False,           # Disable SQL logging
)
```

### Monitoring and Logging

Add instrumentation:

```python
import logging
from sqlalchemy import event

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ml_registry_db")

@event.listens_for(Engine, "before_cursor_execute")
def log_query(conn, cursor, statement, parameters, context, executemany):
    """Log slow queries."""
    import time
    context._query_start_time = time.time()

@event.listens_for(Engine, "after_cursor_execute")
def log_query_duration(conn, cursor, statement, parameters, context, executemany):
    """Log query duration."""
    duration = time.time() - context._query_start_time
    if duration > 1.0:  # Log queries taking > 1 second
        logger.warning(f"Slow query ({duration:.2f}s): {statement[:100]}...")
```

### Security Best Practices

1. **Use environment variables** for credentials
2. **Rotate passwords** regularly
3. **Use IAM authentication** in cloud (AWS RDS IAM, GCP Cloud SQL)
4. **Enable SSL/TLS** for database connections:

```python
engine = create_engine(
    url,
    connect_args={
        "sslmode": "require",
        "sslcert": "/path/to/client-cert.pem",
        "sslkey": "/path/to/client-key.pem",
        "sslrootcert": "/path/to/ca-cert.pem",
    },
)
```

5. **Use least privilege** database users
6. **Audit logging** for sensitive operations
7. **Input validation** with Pydantic schemas

---

## Part 12: Hands-on Challenges

### Challenge 1: Implement Async Support

Add async SQLAlchemy support using `asyncpg`:

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

async_engine = create_async_engine(
    "postgresql+asyncpg://user:pass@localhost/db",
    echo=False,
)

async def async_list_models():
    async with AsyncSession(async_engine) as session:
        result = await session.execute(select(Model))
        return result.scalars().all()
```

**Tasks:**
- Create async versions of repository functions
- Update FastAPI endpoints to use async/await
- Benchmark performance difference

### Challenge 2: Implement Caching Layer

Add Redis caching for frequently accessed data:

```python
import redis
from functools import wraps

cache = redis.Redis(host='localhost', port=6379, decode_responses=True)

def cached(expire=300):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = f"{func.__name__}:{args}:{kwargs}"
            cached_result = cache.get(key)

            if cached_result:
                return json.loads(cached_result)

            result = func(*args, **kwargs)
            cache.setex(key, expire, json.dumps(result))
            return result
        return wrapper
    return decorator

@cached(expire=600)
def get_model_cached(session, model_id):
    return repositories.get_model(session, model_id)
```

**Tasks:**
- Add caching to read-heavy repository functions
- Implement cache invalidation on writes
- Monitor cache hit rates

### Challenge 3: Add Full-Text Search

Implement full-text search for models and datasets:

```python
from sqlalchemy import func

# Add tsvector column to Model
class Model(Base):
    search_vector = mapped_column(
        TSVector,
        Computed(
            "to_tsvector('english', coalesce(model_name,'') || ' ' || coalesce(description,''))",
            persisted=True,
        ),
    )

# Search function
def search_models(session: Session, query: str) -> List[Model]:
    return session.query(Model).filter(
        Model.search_vector.op("@@")(func.plainto_tsquery("english", query))
    ).all()
```

**Tasks:**
- Add full-text search indexes
- Implement ranking by relevance
- Support multi-language search

### Solutions

<details>
<summary>Click to reveal solutions</summary>

**Challenge 1 Solution**: See `examples/async_repositories.py` (implement async versions of key functions)

**Challenge 2 Solution**: See `examples/redis_caching.py` (implement caching with invalidation)

**Challenge 3 Solution**: See `examples/fulltext_search.py` (implement PostgreSQL FTS)

</details>

---

## Part 13: Troubleshooting Guide

### Common Issues

**1. Connection Refused**

```
sqlalchemy.exc.OperationalError: could not connect to server: Connection refused
```

**Solution:**
- Verify PostgreSQL is running: `docker ps`
- Check connection string in `.env`
- Test connection: `psql -h localhost -U ml_user -d ml_registry`

**2. Pool Timeout**

```
sqlalchemy.exc.TimeoutError: QueuePool limit of size 5 overflow 10 reached
```

**Solution:**
- Increase `pool_size` and `max_overflow`
- Check for connection leaks (unclosed sessions)
- Use context managers (`with get_session()`) to ensure cleanup

**3. Migration Conflicts**

```
alembic.util.exc.CommandError: Can't locate revision identified by 'abc123'
```

**Solution:**
- Check `alembic_version` table: `SELECT * FROM alembic_version;`
- Stamp database with current version: `alembic stamp head`
- Reset migrations if needed: `alembic downgrade base && alembic upgrade head`

**4. Foreign Key Constraint Violations**

```
sqlalchemy.exc.IntegrityError: foreign key constraint "fk_version" violated
```

**Solution:**
- Ensure parent records exist before creating child records
- Use `try/except` to catch `IntegrityError`
- Check cascade rules (`ON DELETE CASCADE` vs `RESTRICT`)

**5. N+1 Query Problem**

**Symptom**: Many queries executed for related objects

**Solution:**
- Use eager loading:
  ```python
  stmt = select(Model).options(selectinload(Model.versions))
  ```
- Use `joinedload()` for single-object relationships
- Monitor SQL with `echo=True` during development

---

## Part 14: Summary and Next Steps

### What You've Learned

✅ **SQLAlchemy ORM**: Mapping tables to Python classes with relationships
✅ **Session Management**: Connection pooling, context managers, transaction handling
✅ **Repository Pattern**: Encapsulating database logic in reusable functions
✅ **Pydantic Integration**: Type-safe validation for API requests/responses
✅ **Alembic Migrations**: Managing schema evolution over time
✅ **Testing**: Comprehensive test suite with fixtures and factories
✅ **Production Patterns**: Connection pooling, error handling, logging, security
✅ **FastAPI Integration**: Building RESTful APIs backed by databases

### Key Takeaways

1. **ORM Abstraction**: SQLAlchemy provides powerful abstractions while allowing raw SQL when needed
2. **Relationships**: Properly configured relationships (one-to-many, many-to-many) simplify data access
3. **Testing**: Transactional tests ensure isolation and repeatability
4. **Migrations**: Alembic enables safe schema evolution in production
5. **Production Readiness**: Connection pooling, monitoring, and error handling are critical

### Project Deliverables

✅ Fully functional Python package: `ml-registry-db`
✅ ORM models for all 9 tables from Exercise 02
✅ Repository layer with 20+ functions
✅ Pydantic schemas for validation
✅ Alembic migration setup
✅ Test suite with 25+ tests
✅ CLI tools for database management
✅ FastAPI integration example
✅ Production-ready configuration

### Next Steps

**Exercise 05**: Database Optimization & Indexing
- Query performance analysis
- Index strategies (B-tree, GIN, partial indexes)
- Query optimization techniques
- Monitoring and observability

**Beyond This Module**:
- **Module 009**: Monitoring & Logging - Instrument database operations
- **Module 010**: Cloud Platforms - Deploy to AWS RDS or GCP Cloud SQL
- **Projects**: Build complete ML platforms using this database package

### Production Checklist

Before deploying to production:

- [ ] Environment variables configured for prod database
- [ ] Connection pooling tuned for expected traffic
- [ ] SSL/TLS enabled for database connections
- [ ] Alembic migrations tested on staging
- [ ] Test coverage ≥ 80%
- [ ] Logging and monitoring instrumented
- [ ] Error handling for all edge cases
- [ ] Database backups configured
- [ ] Disaster recovery plan documented
- [ ] Security audit completed (credentials, IAM, encryption)

### Resources

**SQLAlchemy Documentation**:
- Official Docs: https://docs.sqlalchemy.org/
- ORM Tutorial: https://docs.sqlalchemy.org/en/20/tutorial/
- Relationships Guide: https://docs.sqlalchemy.org/en/20/orm/relationships.html

**Alembic Documentation**:
- https://alembic.sqlalchemy.org/

**Pydantic Documentation**:
- https://docs.pydantic.dev/

**FastAPI + SQLAlchemy**:
- https://fastapi.tiangolo.com/tutorial/sql-databases/

**PostgreSQL**:
- psycopg2: https://www.psycopg.org/
- asyncpg: https://github.com/MagicStack/asyncpg

---

## Congratulations!

You've completed Exercise 04 and built a production-ready Python package for managing ML model metadata with SQLAlchemy ORM. You now have:

- A reusable database package that can be imported into any Python application
- Complete understanding of ORM patterns, relationships, and query optimization
- Testing infrastructure for validating database interactions
- Migration management for schema evolution
- Real-world integration with FastAPI for building APIs

**You're now ready for Exercise 05: Database Optimization & Indexing!**

---

**Exercise 04 Complete** | Next: [Exercise 05: Optimization & Indexing](./exercise-05-optimization-indexing.md)
