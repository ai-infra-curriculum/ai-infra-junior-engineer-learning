# Exercise 06: Transaction Isolation and Concurrency Control

## Overview
Build an ML model registry with proper transaction handling, test different isolation levels, implement locking strategies, and handle concurrent operations safely. This exercise demonstrates how to manage database consistency when multiple users or services access and modify ML metadata simultaneously.

**Duration:** 3-4 hours
**Difficulty:** Intermediate

## Learning Objectives
By completing this exercise, you will:
- Understand ACID properties and their importance in ML systems
- Implement and test different transaction isolation levels
- Apply optimistic and pessimistic locking strategies
- Identify and resolve deadlock scenarios
- Design concurrent-safe operations for ML metadata
- Handle race conditions in model versioning

## Prerequisites
- PostgreSQL or MySQL installed locally or via Docker
- Python 3.8+
- SQLAlchemy 2.0+
- Understanding of SQL basics and Python

## Scenario
You're building a centralized **ML Model Registry** where multiple data scientists and CI/CD pipelines register, update, and query model metadata concurrently. The system must handle:
- Multiple teams registering models with auto-incrementing version numbers
- Concurrent updates to experiment metrics
- Race conditions when promoting models to production
- Consistency when reading model lineage across related tables

Without proper concurrency control, you risk:
- Duplicate version numbers
- Lost updates (one user's changes overwritten)
- Inconsistent reads (reading partial updates)
- Deadlocks (two processes blocking each other)

## Tasks

### Task 1: Database Setup and Schema Design

**TODO 1.1:** Start a PostgreSQL container with Docker

```bash
docker run -d \
  --name ml-registry-db \
  -e POSTGRES_PASSWORD=mlregistry123 \
  -e POSTGRES_USER=mluser \
  -e POSTGRES_DB=model_registry \
  -p 5432:5432 \
  postgres:15

# TODO: Verify connection
psql -h localhost -U mluser -d model_registry
```

**TODO 1.2:** Create the schema for the model registry

```sql
-- models table
CREATE TABLE models (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100),
    UNIQUE(name)
);

-- model_versions table
CREATE TABLE model_versions (
    id SERIAL PRIMARY KEY,
    model_id INTEGER REFERENCES models(id) ON DELETE CASCADE,
    version INTEGER NOT NULL,
    framework VARCHAR(50),
    artifact_uri TEXT,
    stage VARCHAR(20) DEFAULT 'staging', -- staging, production, archived
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(model_id, version)
);

-- experiments table
CREATE TABLE experiments (
    id SERIAL PRIMARY KEY,
    model_version_id INTEGER REFERENCES model_versions(id) ON DELETE CASCADE,
    metric_name VARCHAR(100),
    metric_value FLOAT,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- model_metadata table (for optimistic locking demo)
CREATE TABLE model_metadata (
    model_version_id INTEGER PRIMARY KEY REFERENCES model_versions(id) ON DELETE CASCADE,
    tags JSONB,
    parameters JSONB,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    version_lock INTEGER DEFAULT 0  -- For optimistic locking
);

-- Insert sample data
INSERT INTO models (name, description, created_by) VALUES
    ('fraud-detector', 'Credit card fraud detection model', 'alice'),
    ('recommender-v2', 'Product recommendation engine', 'bob');

-- TODO: Add indexes for performance
CREATE INDEX idx_model_versions_stage ON model_versions(stage);
CREATE INDEX idx_experiments_model_version ON experiments(model_version_id);
```

**TODO 1.3:** Create Python connection module

```python
# db_connection.py
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager

DATABASE_URL = "postgresql://mluser:mlregistry123@localhost:5432/model_registry"

engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    echo=True  # Set to False in production
)

SessionLocal = sessionmaker(bind=engine)

@contextmanager
def get_db_session():
    """Context manager for database sessions."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

# TODO: Implement connection pool monitoring
def get_pool_status():
    """Return current connection pool statistics."""
    pool = engine.pool
    return {
        "size": pool.size(),
        "checked_in": pool.checkedin(),
        "checked_out": pool.checkedout(),
        "overflow": pool.overflow()
    }
```

### Task 2: Understanding ACID Properties

**TODO 2.1:** Create a test to demonstrate Atomicity

```python
# test_acid_atomicity.py
from db_connection import get_db_session
from sqlalchemy import text

def register_model_with_version_atomically(model_name: str, version: int):
    """
    Atomicity: Either both model and version are created, or neither.
    If version creation fails, model creation should rollback.
    """
    with get_db_session() as session:
        # TODO: Insert model
        result = session.execute(
            text("INSERT INTO models (name, created_by) VALUES (:name, 'system') RETURNING id"),
            {"name": model_name}
        )
        model_id = result.fetchone()[0]
        print(f"Created model {model_name} with ID {model_id}")

        # TODO: Intentionally cause error on version insert (test atomicity)
        # This will fail if version already exists, causing rollback
        session.execute(
            text("INSERT INTO model_versions (model_id, version, framework) VALUES (:mid, :ver, 'pytorch')"),
            {"mid": model_id, "ver": version}
        )
        print(f"Created version {version} for model {model_id}")

# Test atomicity
if __name__ == "__main__":
    try:
        # First call succeeds
        register_model_with_version_atomically("test-model-1", 1)
        print("✓ Transaction 1 committed successfully\n")
    except Exception as e:
        print(f"✗ Transaction 1 failed: {e}\n")

    try:
        # Second call with same version should fail and rollback model creation too
        register_model_with_version_atomically("test-model-2", 1)
        print("✓ Transaction 2 committed successfully\n")
    except Exception as e:
        print(f"✗ Transaction 2 failed and rolled back: {e}\n")

    # TODO: Verify that test-model-2 was NOT created
    with get_db_session() as session:
        result = session.execute(text("SELECT name FROM models WHERE name = 'test-model-2'"))
        if result.fetchone():
            print("✗ Atomicity violated: model exists despite error")
        else:
            print("✓ Atomicity preserved: model was rolled back")
```

**TODO 2.2:** Demonstrate Consistency with constraints

```python
# test_acid_consistency.py
from db_connection import get_db_session
from sqlalchemy import text

def test_referential_integrity():
    """
    Consistency: Database constraints prevent invalid states.
    Cannot create model_version without valid model_id.
    """
    with get_db_session() as session:
        try:
            # TODO: Try to insert version with non-existent model_id
            session.execute(
                text("INSERT INTO model_versions (model_id, version) VALUES (9999, 1)")
            )
            print("✗ Consistency violated: orphaned version created")
        except Exception as e:
            print(f"✓ Consistency enforced: {e}")
            session.rollback()

def test_unique_constraint():
    """Cannot have duplicate (model_id, version) pairs."""
    model_id = 1  # Assume exists
    with get_db_session() as session:
        try:
            # TODO: Insert version 1
            session.execute(
                text("INSERT INTO model_versions (model_id, version, framework) VALUES (:mid, 1, 'pytorch')"),
                {"mid": model_id}
            )
            # TODO: Try to insert duplicate version
            session.execute(
                text("INSERT INTO model_versions (model_id, version, framework) VALUES (:mid, 1, 'tensorflow')"),
                {"mid": model_id}
            )
            print("✗ Uniqueness constraint violated")
        except Exception as e:
            print(f"✓ Uniqueness enforced: {e}")
            session.rollback()

if __name__ == "__main__":
    test_referential_integrity()
    test_unique_constraint()
```

### Task 3: Transaction Isolation Levels

**TODO 3.1:** Demonstrate READ UNCOMMITTED (dirty reads)

```python
# test_isolation_levels.py
import time
import threading
from db_connection import get_db_session, engine
from sqlalchemy import text

def dirty_read_demo():
    """
    READ UNCOMMITTED: Can read uncommitted changes from other transactions.
    Note: PostgreSQL doesn't support READ UNCOMMITTED; it behaves like READ COMMITTED.
    MySQL/MariaDB support this level.
    """
    def writer():
        with get_db_session() as session:
            # Set isolation level
            session.execute(text("SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED"))
            session.execute(text("UPDATE models SET description = 'TEMP UPDATE' WHERE id = 1"))
            print("Writer: Updated description (not committed)")
            time.sleep(3)
            print("Writer: Rolling back...")
            session.rollback()

    def reader():
        time.sleep(1)  # Let writer start first
        with get_db_session() as session:
            # TODO: Set isolation level
            session.execute(text("SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED"))
            result = session.execute(text("SELECT description FROM models WHERE id = 1"))
            desc = result.fetchone()[0]
            print(f"Reader: Read description = '{desc}' (may be uncommitted)")

    # TODO: Run writer and reader concurrently
    t1 = threading.Thread(target=writer)
    t2 = threading.Thread(target=reader)
    t1.start()
    t2.start()
    t1.join()
    t2.join()

# TODO: Implement this function
dirty_read_demo()
```

**TODO 3.2:** Demonstrate READ COMMITTED (prevents dirty reads)

```python
def read_committed_demo():
    """
    READ COMMITTED: Only see committed changes. Most common default.
    """
    def writer():
        with get_db_session() as session:
            session.execute(text("SET TRANSACTION ISOLATION LEVEL READ COMMITTED"))
            session.execute(text("UPDATE models SET description = 'TEMP' WHERE id = 1"))
            print("Writer: Updated (not committed)")
            time.sleep(3)
            session.commit()
            print("Writer: Committed")

    def reader():
        time.sleep(1)
        with get_db_session() as session:
            session.execute(text("SET TRANSACTION ISOLATION LEVEL READ COMMITTED"))
            result = session.execute(text("SELECT description FROM models WHERE id = 1"))
            desc = result.fetchone()[0]
            print(f"Reader: First read = '{desc}' (should be original)")

            # TODO: Read again after writer commits
            time.sleep(3)
            result = session.execute(text("SELECT description FROM models WHERE id = 1"))
            desc = result.fetchone()[0]
            print(f"Reader: Second read = '{desc}' (should be updated)")

    t1 = threading.Thread(target=writer)
    t2 = threading.Thread(target=reader)
    t1.start()
    t2.start()
    t1.join()
    t2.join()

# TODO: Run and observe the difference from READ UNCOMMITTED
read_committed_demo()
```

**TODO 3.3:** Demonstrate REPEATABLE READ (prevents non-repeatable reads)

```python
def repeatable_read_demo():
    """
    REPEATABLE READ: Sees snapshot of database at transaction start.
    Prevents non-repeatable reads within same transaction.
    """
    def writer():
        time.sleep(2)
        with get_db_session() as session:
            session.execute(text("UPDATE model_versions SET stage = 'production' WHERE id = 1"))
            session.commit()
            print("Writer: Updated stage to production")

    def reader():
        with get_db_session() as session:
            # TODO: Set isolation level
            session.execute(text("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ"))

            result = session.execute(text("SELECT stage FROM model_versions WHERE id = 1"))
            stage1 = result.fetchone()[0]
            print(f"Reader: First read = '{stage1}'")

            time.sleep(4)  # Wait for writer to commit

            # TODO: Read again - should see SAME value as first read
            result = session.execute(text("SELECT stage FROM model_versions WHERE id = 1"))
            stage2 = result.fetchone()[0]
            print(f"Reader: Second read = '{stage2}' (should match first)")

            session.commit()

    t1 = threading.Thread(target=reader)
    t2 = threading.Thread(target=writer)
    t1.start()
    t2.start()
    t1.join()
    t2.join()

# TODO: Run and observe consistent reads
repeatable_read_demo()
```

**TODO 3.4:** Demonstrate SERIALIZABLE (strictest isolation)

```python
def serializable_demo():
    """
    SERIALIZABLE: Prevents all anomalies including phantom reads.
    Transactions execute as if they ran one after another.
    """
    def count_production_models():
        with get_db_session() as session:
            session.execute(text("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE"))

            # TODO: Count production models
            result = session.execute(
                text("SELECT COUNT(*) FROM model_versions WHERE stage = 'production'")
            )
            count1 = result.fetchone()[0]
            print(f"Counter: First count = {count1}")

            time.sleep(3)

            # TODO: Count again
            result = session.execute(
                text("SELECT COUNT(*) FROM model_versions WHERE stage = 'production'")
            )
            count2 = result.fetchone()[0]
            print(f"Counter: Second count = {count2} (should match first)")

            session.commit()

    def insert_production_model():
        time.sleep(1)
        try:
            with get_db_session() as session:
                session.execute(text("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE"))
                session.execute(
                    text("INSERT INTO model_versions (model_id, version, stage) VALUES (1, 999, 'production')")
                )
                session.commit()
                print("Inserter: Added production model")
        except Exception as e:
            print(f"Inserter: Serialization conflict - {e}")

    t1 = threading.Thread(target=count_production_models)
    t2 = threading.Thread(target=insert_production_model)
    t1.start()
    t2.start()
    t1.join()
    t2.join()

# TODO: Run and observe serialization conflicts
serializable_demo()
```

### Task 4: Pessimistic Locking (SELECT FOR UPDATE)

**TODO 4.1:** Implement safe version number generation with row-level locks

```python
# model_registry.py
from db_connection import get_db_session
from sqlalchemy import text
import time

def register_new_model_version_safe(model_id: int, framework: str, artifact_uri: str):
    """
    Use SELECT FOR UPDATE to lock the row and safely generate next version number.
    Prevents race condition where two processes read same max version.
    """
    with get_db_session() as session:
        # TODO: Lock the model row
        session.execute(
            text("SELECT id FROM models WHERE id = :mid FOR UPDATE"),
            {"mid": model_id}
        )
        print(f"[{threading.current_thread().name}] Acquired lock on model {model_id}")

        # TODO: Get current max version
        result = session.execute(
            text("SELECT COALESCE(MAX(version), 0) FROM model_versions WHERE model_id = :mid"),
            {"mid": model_id}
        )
        max_version = result.fetchone()[0]
        next_version = max_version + 1
        print(f"[{threading.current_thread().name}] Current max version: {max_version}, next: {next_version}")

        # Simulate processing time
        time.sleep(1)

        # TODO: Insert new version
        session.execute(
            text("""
                INSERT INTO model_versions (model_id, version, framework, artifact_uri)
                VALUES (:mid, :ver, :fw, :uri)
            """),
            {"mid": model_id, "ver": next_version, "fw": framework, "uri": artifact_uri}
        )
        print(f"[{threading.current_thread().name}] Created version {next_version}")
        session.commit()
        return next_version

# TODO: Test concurrent version creation
def test_concurrent_version_creation():
    """Multiple threads trying to create versions for same model."""
    import threading

    def create_version(i):
        try:
            version = register_new_model_version_safe(
                model_id=1,
                framework="pytorch",
                artifact_uri=f"s3://models/fraud-detector/v{i}.pt"
            )
            print(f"Thread {i}: Successfully created version {version}")
        except Exception as e:
            print(f"Thread {i}: Error - {e}")

    threads = [threading.Thread(target=create_version, args=(i,), name=f"Thread-{i}") for i in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # TODO: Verify no duplicate versions created
    with get_db_session() as session:
        result = session.execute(
            text("SELECT version FROM model_versions WHERE model_id = 1 ORDER BY version")
        )
        versions = [row[0] for row in result.fetchall()]
        print(f"\nFinal versions: {versions}")

        if len(versions) == len(set(versions)):
            print("✓ No duplicate versions - pessimistic locking worked")
        else:
            print("✗ Duplicate versions detected")

if __name__ == "__main__":
    test_concurrent_version_creation()
```

**TODO 4.2:** Implement safe model promotion with FOR UPDATE

```python
def promote_to_production_safe(model_id: int, target_version: int):
    """
    Safely promote a model version to production:
    1. Demote current production version to staging
    2. Promote target version to production
    Use locks to prevent concurrent promotions.
    """
    with get_db_session() as session:
        # TODO: Lock all versions of this model
        session.execute(
            text("SELECT id FROM model_versions WHERE model_id = :mid FOR UPDATE"),
            {"mid": model_id}
        )
        print(f"Acquired locks for model {model_id}")

        # TODO: Find current production version
        result = session.execute(
            text("SELECT id, version FROM model_versions WHERE model_id = :mid AND stage = 'production'"),
            {"mid": model_id}
        )
        current_prod = result.fetchone()

        if current_prod:
            # TODO: Demote current production
            session.execute(
                text("UPDATE model_versions SET stage = 'staging' WHERE id = :id"),
                {"id": current_prod[0]}
            )
            print(f"Demoted version {current_prod[1]} to staging")

        # TODO: Promote target version
        result = session.execute(
            text("UPDATE model_versions SET stage = 'production' WHERE model_id = :mid AND version = :ver"),
            {"mid": model_id, "ver": target_version}
        )

        if result.rowcount == 0:
            raise ValueError(f"Version {target_version} not found")

        print(f"Promoted version {target_version} to production")
        session.commit()

# TODO: Test concurrent promotions
def test_concurrent_promotions():
    import threading

    def promote(version):
        try:
            promote_to_production_safe(model_id=1, target_version=version)
        except Exception as e:
            print(f"Promotion to v{version} failed: {e}")

    # Try to promote v2 and v3 concurrently
    t1 = threading.Thread(target=promote, args=(2,))
    t2 = threading.Thread(target=promote, args=(3,))
    t1.start()
    t2.start()
    t1.join()
    t2.join()

    # TODO: Verify only one version is in production
    with get_db_session() as session:
        result = session.execute(
            text("SELECT version FROM model_versions WHERE model_id = 1 AND stage = 'production'")
        )
        prod_versions = [row[0] for row in result.fetchall()]
        print(f"\nProduction versions: {prod_versions}")

        if len(prod_versions) == 1:
            print("✓ Only one production version - promotion was safe")
        else:
            print("✗ Multiple production versions - race condition occurred")
```

### Task 5: Optimistic Locking with Version Numbers

**TODO 5.1:** Implement optimistic locking for metadata updates

```python
# optimistic_locking.py
from db_connection import get_db_session
from sqlalchemy import text
import json

def update_model_metadata_optimistic(model_version_id: int, new_tags: dict, new_params: dict):
    """
    Update metadata using optimistic locking (version_lock field).
    Only succeeds if version_lock hasn't changed since we read it.
    """
    with get_db_session() as session:
        # TODO: Read current metadata and version_lock
        result = session.execute(
            text("SELECT tags, parameters, version_lock FROM model_metadata WHERE model_version_id = :mvid"),
            {"mvid": model_version_id}
        )
        row = result.fetchone()

        if not row:
            # TODO: Insert if doesn't exist
            session.execute(
                text("""
                    INSERT INTO model_metadata (model_version_id, tags, parameters, version_lock)
                    VALUES (:mvid, :tags, :params, 0)
                """),
                {"mvid": model_version_id, "tags": json.dumps(new_tags), "params": json.dumps(new_params)}
            )
            print(f"Created metadata for version {model_version_id}")
            session.commit()
            return

        current_lock = row[2]
        print(f"Current version_lock: {current_lock}")

        # Simulate processing time
        import time
        time.sleep(1)

        # TODO: Update only if version_lock hasn't changed
        result = session.execute(
            text("""
                UPDATE model_metadata
                SET tags = :tags,
                    parameters = :params,
                    version_lock = :new_lock,
                    updated_at = CURRENT_TIMESTAMP
                WHERE model_version_id = :mvid AND version_lock = :old_lock
            """),
            {
                "mvid": model_version_id,
                "tags": json.dumps(new_tags),
                "params": json.dumps(new_params),
                "old_lock": current_lock,
                "new_lock": current_lock + 1
            }
        )

        if result.rowcount == 0:
            # Someone else updated it first
            raise Exception(f"Optimistic lock failed: metadata was modified by another process")

        print(f"Updated metadata (new version_lock: {current_lock + 1})")
        session.commit()

# TODO: Test concurrent updates with optimistic locking
def test_optimistic_locking():
    import threading

    # First, create a model version with metadata
    model_version_id = 1
    with get_db_session() as session:
        session.execute(
            text("INSERT INTO model_metadata (model_version_id, tags, parameters) VALUES (:mvid, '{}', '{}') ON CONFLICT DO NOTHING"),
            {"mvid": model_version_id}
        )
        session.commit()

    def update_tags(thread_id):
        try:
            new_tags = {"updated_by": f"thread_{thread_id}", "timestamp": str(time.time())}
            new_params = {"learning_rate": 0.001 * thread_id}
            update_model_metadata_optimistic(model_version_id, new_tags, new_params)
            print(f"Thread {thread_id}: Update succeeded")
        except Exception as e:
            print(f"Thread {thread_id}: Update failed - {e}")

    # TODO: Run concurrent updates
    threads = [threading.Thread(target=update_tags, args=(i,)) for i in range(3)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # Check final state
    with get_db_session() as session:
        result = session.execute(
            text("SELECT tags, version_lock FROM model_metadata WHERE model_version_id = :mvid"),
            {"mvid": model_version_id}
        )
        row = result.fetchone()
        print(f"\nFinal state: tags={row[0]}, version_lock={row[1]}")
        print("Expected: 2 updates failed, 1 succeeded, version_lock=1")

if __name__ == "__main__":
    test_optimistic_locking()
```

**TODO 5.2:** Compare optimistic vs pessimistic locking performance

```python
# locking_comparison.py
import time
import threading
from model_registry import register_new_model_version_safe
from optimistic_locking import update_model_metadata_optimistic

def benchmark_pessimistic():
    """Benchmark pessimistic locking (SELECT FOR UPDATE)."""
    start = time.time()
    threads = [
        threading.Thread(target=register_new_model_version_safe, args=(1, "pytorch", f"s3://test/{i}"))
        for i in range(10)
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    duration = time.time() - start
    print(f"Pessimistic locking: {duration:.2f}s for 10 operations")
    return duration

def benchmark_optimistic():
    """Benchmark optimistic locking with retries."""
    def update_with_retry(thread_id):
        max_retries = 5
        for attempt in range(max_retries):
            try:
                update_model_metadata_optimistic(
                    1,
                    {"thread": thread_id, "attempt": attempt},
                    {"value": thread_id}
                )
                return
            except Exception:
                time.sleep(0.01 * (2 ** attempt))  # Exponential backoff
        print(f"Thread {thread_id}: All retries exhausted")

    start = time.time()
    threads = [threading.Thread(target=update_with_retry, args=(i,)) for i in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    duration = time.time() - start
    print(f"Optimistic locking: {duration:.2f}s for 10 operations")
    return duration

# TODO: Run benchmark and analyze results
if __name__ == "__main__":
    print("=== Locking Strategy Comparison ===\n")
    print("Pessimistic (SELECT FOR UPDATE):")
    print("- Pros: Guaranteed success, no retries needed")
    print("- Cons: Holds locks longer, blocks other transactions\n")

    pess_time = benchmark_pessimistic()

    print("\nOptimistic (Version Numbers):")
    print("- Pros: No locks, better concurrency for low-conflict scenarios")
    print("- Cons: Requires retry logic, wastes work on conflicts\n")

    opt_time = benchmark_optimistic()

    print(f"\nPerformance comparison: Optimistic was {pess_time/opt_time:.2f}x {'faster' if opt_time < pess_time else 'slower'}")
    print("\nRecommendation:")
    print("- Use pessimistic locking for high-contention writes (e.g., version number generation)")
    print("- Use optimistic locking for low-contention updates (e.g., metadata edits)")
```

### Task 6: Deadlock Detection and Prevention

**TODO 6.1:** Create a deadlock scenario

```python
# deadlock_demo.py
import threading
import time
from db_connection import get_db_session
from sqlalchemy import text

def create_deadlock_scenario():
    """
    Deadlock scenario:
    - Thread A locks model 1, then tries to lock model 2
    - Thread B locks model 2, then tries to lock model 1
    Both threads wait for each other => DEADLOCK
    """
    def thread_a():
        try:
            with get_db_session() as session:
                # TODO: Lock model 1
                print("Thread A: Locking model 1...")
                session.execute(text("SELECT * FROM models WHERE id = 1 FOR UPDATE"))
                print("Thread A: Acquired lock on model 1")

                time.sleep(2)  # Give thread B time to lock model 2

                # TODO: Try to lock model 2 (will wait for thread B)
                print("Thread A: Trying to lock model 2...")
                session.execute(text("SELECT * FROM models WHERE id = 2 FOR UPDATE"))
                print("Thread A: Acquired lock on model 2")

                session.commit()
                print("Thread A: SUCCESS")
        except Exception as e:
            print(f"Thread A: DEADLOCK DETECTED - {e}")

    def thread_b():
        try:
            time.sleep(1)  # Let thread A go first
            with get_db_session() as session:
                # TODO: Lock model 2
                print("Thread B: Locking model 2...")
                session.execute(text("SELECT * FROM models WHERE id = 2 FOR UPDATE"))
                print("Thread B: Acquired lock on model 2")

                time.sleep(2)

                # TODO: Try to lock model 1 (will wait for thread A)
                print("Thread B: Trying to lock model 1...")
                session.execute(text("SELECT * FROM models WHERE id = 1 FOR UPDATE"))
                print("Thread B: Acquired lock on model 1")

                session.commit()
                print("Thread B: SUCCESS")
        except Exception as e:
            print(f"Thread B: DEADLOCK DETECTED - {e}")

    # TODO: Run both threads
    ta = threading.Thread(target=thread_a)
    tb = threading.Thread(target=thread_b)
    ta.start()
    tb.start()
    ta.join()
    tb.join()

    print("\nPostgreSQL will detect the deadlock and abort one transaction.")

# TODO: Run the deadlock demo
create_deadlock_scenario()
```

**TODO 6.2:** Prevent deadlocks with lock ordering

```python
def prevent_deadlock_with_ordering():
    """
    Prevention: Always acquire locks in the same order (by ID).
    Both threads lock model 1 first, then model 2.
    """
    def thread_safe(thread_name, model_ids):
        try:
            # TODO: Sort model IDs to ensure consistent lock order
            sorted_ids = sorted(model_ids)

            with get_db_session() as session:
                for model_id in sorted_ids:
                    print(f"{thread_name}: Locking model {model_id}...")
                    session.execute(
                        text(f"SELECT * FROM models WHERE id = {model_id} FOR UPDATE")
                    )
                    print(f"{thread_name}: Acquired lock on model {model_id}")
                    time.sleep(1)

                session.commit()
                print(f"{thread_name}: SUCCESS - no deadlock")
        except Exception as e:
            print(f"{thread_name}: ERROR - {e}")

    # TODO: Run threads that would deadlock without ordering
    ta = threading.Thread(target=thread_safe, args=("Thread A", [1, 2]))
    tb = threading.Thread(target=thread_safe, args=("Thread B", [2, 1]))  # Note: reverse order as input
    ta.start()
    tb.start()
    ta.join()
    tb.join()

    print("\nWith lock ordering: Both threads lock in order 1->2, no deadlock occurs.")

# TODO: Run the prevention demo
prevent_deadlock_with_ordering()
```

**TODO 6.3:** Implement deadlock retry logic

```python
def operation_with_deadlock_retry(max_retries=3):
    """
    If a deadlock is detected, retry the entire transaction.
    """
    for attempt in range(max_retries):
        try:
            with get_db_session() as session:
                # TODO: Perform operations that might deadlock
                session.execute(text("SELECT * FROM models WHERE id = 1 FOR UPDATE"))
                time.sleep(1)
                session.execute(text("SELECT * FROM models WHERE id = 2 FOR UPDATE"))
                session.commit()
                print(f"Attempt {attempt + 1}: SUCCESS")
                return
        except Exception as e:
            if "deadlock" in str(e).lower():
                print(f"Attempt {attempt + 1}: Deadlock detected, retrying...")
                time.sleep(0.1 * (2 ** attempt))  # Exponential backoff
            else:
                raise

    raise Exception("Max retries exceeded due to deadlocks")

# TODO: Test retry logic
operation_with_deadlock_retry()
```

### Task 7: Real-World ML Registry Operations

**TODO 7.1:** Implement batch experiment logging with proper isolation

```python
# ml_registry_operations.py
from db_connection import get_db_session
from sqlalchemy import text

def log_experiments_batch(model_version_id: int, metrics: list):
    """
    Log multiple experiment metrics atomically.
    Use appropriate isolation level for this write-heavy operation.
    """
    with get_db_session() as session:
        # TODO: Set isolation level (READ COMMITTED is sufficient for inserts)
        session.execute(text("SET TRANSACTION ISOLATION LEVEL READ COMMITTED"))

        # TODO: Insert all metrics in one transaction
        for metric in metrics:
            session.execute(
                text("""
                    INSERT INTO experiments (model_version_id, metric_name, metric_value)
                    VALUES (:mvid, :name, :value)
                """),
                {"mvid": model_version_id, "name": metric["name"], "value": metric["value"]}
            )

        session.commit()
        print(f"Logged {len(metrics)} metrics for version {model_version_id}")

# TODO: Test concurrent metric logging
def test_concurrent_metric_logging():
    import threading

    def log_metrics(thread_id):
        metrics = [
            {"name": "accuracy", "value": 0.9 + thread_id * 0.01},
            {"name": "precision", "value": 0.85 + thread_id * 0.01},
            {"name": "recall", "value": 0.88 + thread_id * 0.01}
        ]
        log_experiments_batch(model_version_id=1, metrics=metrics)

    threads = [threading.Thread(target=log_metrics, args=(i,)) for i in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # TODO: Verify all metrics were logged
    with get_db_session() as session:
        result = session.execute(
            text("SELECT COUNT(*) FROM experiments WHERE model_version_id = 1")
        )
        count = result.fetchone()[0]
        print(f"Total metrics logged: {count} (expected: 15)")

if __name__ == "__main__":
    test_concurrent_metric_logging()
```

**TODO 7.2:** Implement safe model comparison query

```python
def compare_models_consistent(model_ids: list):
    """
    Compare metrics across multiple models.
    Use REPEATABLE READ to ensure consistent snapshot.
    """
    with get_db_session() as session:
        # TODO: Set isolation to get consistent snapshot
        session.execute(text("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ"))

        results = {}
        for model_id in model_ids:
            # TODO: Get latest version for each model
            result = session.execute(
                text("""
                    SELECT mv.id, mv.version
                    FROM model_versions mv
                    WHERE mv.model_id = :mid
                    ORDER BY mv.version DESC
                    LIMIT 1
                """),
                {"mid": model_id}
            )
            version_row = result.fetchone()

            if not version_row:
                continue

            version_id = version_row[0]

            # TODO: Get average metrics
            result = session.execute(
                text("""
                    SELECT metric_name, AVG(metric_value) as avg_value
                    FROM experiments
                    WHERE model_version_id = :vid
                    GROUP BY metric_name
                """),
                {"vid": version_id}
            )

            results[model_id] = {row[0]: row[1] for row in result.fetchall()}

        session.commit()
        return results

# TODO: Test model comparison
if __name__ == "__main__":
    comparison = compare_models_consistent([1, 2])
    print("Model Comparison:")
    for model_id, metrics in comparison.items():
        print(f"  Model {model_id}: {metrics}")
```

## Deliverables

Submit a repository with:

1. **SQL Schema** (`schema.sql`)
   - Complete table definitions
   - Indexes for performance
   - Sample data inserts

2. **Python Modules**
   - `db_connection.py` - Connection management
   - `test_acid_*.py` - ACID property demonstrations
   - `test_isolation_levels.py` - All 4 isolation level tests
   - `model_registry.py` - Pessimistic locking implementations
   - `optimistic_locking.py` - Optimistic locking with version numbers
   - `deadlock_demo.py` - Deadlock scenarios and prevention
   - `ml_registry_operations.py` - Real-world ML registry operations
   - `locking_comparison.py` - Performance benchmarks

3. **Test Results** (`RESULTS.md`)
   - Output from each test scenario
   - Screenshots or logs showing:
     - Isolation level behavior differences
     - Successful prevention of race conditions
     - Deadlock detection and recovery
     - Performance comparison of locking strategies
   - Analysis of when to use each isolation level and locking strategy

4. **Architecture Document** (`ARCHITECTURE.md`)
   - Diagram of the model registry schema
   - Decision matrix: When to use which isolation level
   - Decision matrix: When to use optimistic vs pessimistic locking
   - Concurrency patterns for ML systems
   - Best practices for avoiding deadlocks

## Success Criteria

- [ ] All ACID properties correctly demonstrated
- [ ] All 4 isolation levels tested with clear output showing differences
- [ ] Pessimistic locking prevents race conditions in version generation
- [ ] Optimistic locking correctly detects concurrent modifications
- [ ] Deadlock scenario created and prevention strategies implemented
- [ ] Performance benchmark shows measurable differences between strategies
- [ ] No duplicate model versions created under concurrent load
- [ ] All transactions are properly committed or rolled back
- [ ] Code includes proper error handling and logging
- [ ] Architecture document clearly explains trade-offs

## Bonus Challenges

1. **Distributed Locking**: Implement Redis-based distributed locks for cross-database coordination
2. **Connection Pool Tuning**: Test different pool sizes and measure impact on deadlock frequency
3. **Monitoring**: Add metrics for:
   - Transaction duration by isolation level
   - Lock wait times
   - Deadlock frequency
   - Retry counts for optimistic locking
4. **Saga Pattern**: Implement a saga for multi-step model deployment workflow with compensation
5. **Read Replicas**: Extend the system to use read replicas for query load, with eventual consistency handling

## Resources

- [PostgreSQL Transaction Isolation](https://www.postgresql.org/docs/current/transaction-iso.html)
- [SQLAlchemy Session Documentation](https://docs.sqlalchemy.org/en/20/orm/session.html)
- [Database Concurrency Control](https://use-the-index-luke.com/sql/transaction-isolation)
- [Designing Data-Intensive Applications](https://dataintensive.net/) - Chapter 7: Transactions

## Evaluation Rubric

| Criteria | Points |
|----------|--------|
| ACID demonstrations correct and clear | 15 |
| All isolation levels tested with proper analysis | 20 |
| Pessimistic locking correctly implemented | 15 |
| Optimistic locking with retry logic | 15 |
| Deadlock prevention strategies | 15 |
| Performance benchmarks and analysis | 10 |
| Code quality (error handling, logging, structure) | 10 |

**Total: 100 points**
