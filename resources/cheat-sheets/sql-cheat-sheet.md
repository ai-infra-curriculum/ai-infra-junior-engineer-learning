# SQL Cheat Sheet — PostgreSQL Focus

Quick reference for SQL syntax and PostgreSQL-specific features. Assumes you've completed Module 008.

## Reading Data

```sql
-- Basics
SELECT * FROM users;
SELECT id, email, created_at FROM users WHERE created_at > NOW() - INTERVAL '7 days';

-- DISTINCT
SELECT DISTINCT country FROM users;

-- Sorting + paging
SELECT id, email FROM users
ORDER BY created_at DESC
LIMIT 50 OFFSET 100;

-- IN / BETWEEN / LIKE / ILIKE / IS NULL
SELECT * FROM events WHERE event_type IN ('signup', 'purchase');
SELECT * FROM events WHERE amount BETWEEN 10 AND 100;
SELECT * FROM users WHERE email LIKE '%@example.com';
SELECT * FROM users WHERE name ILIKE 'jo%';        -- case-insensitive
SELECT * FROM users WHERE deleted_at IS NULL;
```

## Aggregates

```sql
SELECT
    country,
    COUNT(*)            AS user_count,
    COUNT(DISTINCT email) AS unique_emails,
    AVG(age)::numeric(10,2) AS avg_age,
    MIN(created_at)     AS earliest,
    MAX(created_at)     AS latest
FROM users
GROUP BY country
HAVING COUNT(*) > 100
ORDER BY user_count DESC;
```

## Joins

```sql
-- INNER
SELECT u.id, u.email, o.total
FROM users u
JOIN orders o ON o.user_id = u.id;

-- LEFT (users without orders included)
SELECT u.id, u.email, COALESCE(SUM(o.total), 0) AS lifetime_value
FROM users u
LEFT JOIN orders o ON o.user_id = u.id
GROUP BY u.id, u.email;

-- Self-join
SELECT a.id, b.id AS referrer_id
FROM users a
JOIN users b ON a.referrer_id = b.id;

-- Anti-join (users with no orders)
SELECT u.*
FROM users u
LEFT JOIN orders o ON o.user_id = u.id
WHERE o.id IS NULL;
-- or, often clearer:
SELECT *
FROM users u
WHERE NOT EXISTS (SELECT 1 FROM orders WHERE user_id = u.id);
```

## CTEs (WITH)

```sql
WITH recent_orders AS (
    SELECT user_id, SUM(total) AS spend
    FROM orders
    WHERE created_at > NOW() - INTERVAL '30 days'
    GROUP BY user_id
),
high_value AS (
    SELECT user_id FROM recent_orders WHERE spend > 1000
)
SELECT u.id, u.email, ro.spend
FROM users u
JOIN high_value hv ON hv.user_id = u.id
JOIN recent_orders ro ON ro.user_id = u.id;
```

## Window Functions

```sql
-- Running total per user
SELECT
    user_id, created_at, total,
    SUM(total) OVER (PARTITION BY user_id ORDER BY created_at) AS running_total
FROM orders;

-- Rank within partition
SELECT
    user_id, total,
    ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY total DESC) AS rn,
    RANK()       OVER (PARTITION BY user_id ORDER BY total DESC) AS rk,
    DENSE_RANK() OVER (PARTITION BY user_id ORDER BY total DESC) AS dr
FROM orders;

-- Lag/Lead
SELECT
    created_at, total,
    LAG(total)  OVER (ORDER BY created_at) AS prev_total,
    LEAD(total) OVER (ORDER BY created_at) AS next_total
FROM orders;
```

## Writing Data

```sql
-- INSERT
INSERT INTO users (email, name) VALUES ('a@b.com', 'A');

-- Multi-row
INSERT INTO users (email, name) VALUES
    ('a@b.com', 'A'),
    ('c@d.com', 'C');

-- INSERT … ON CONFLICT (upsert)
INSERT INTO users (id, email)
VALUES (1, 'new@example.com')
ON CONFLICT (id)
DO UPDATE SET email = EXCLUDED.email, updated_at = NOW();

-- UPDATE
UPDATE users SET name = 'X' WHERE id = 1;
UPDATE users u
SET total_orders = subq.cnt
FROM (SELECT user_id, COUNT(*) AS cnt FROM orders GROUP BY user_id) subq
WHERE u.id = subq.user_id;

-- DELETE
DELETE FROM users WHERE deleted_at < NOW() - INTERVAL '90 days';

-- RETURNING — useful for getting back inserted ids
INSERT INTO orders (user_id, total) VALUES (1, 50)
RETURNING id, created_at;
```

## DDL

```sql
CREATE TABLE users (
    id           BIGSERIAL PRIMARY KEY,
    email        TEXT NOT NULL UNIQUE,
    name         TEXT,
    age          INT CHECK (age >= 0),
    metadata     JSONB DEFAULT '{}'::jsonb,
    created_at   TIMESTAMPTZ DEFAULT NOW(),
    updated_at   TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_users_email_lower ON users (LOWER(email));
CREATE INDEX idx_orders_user_created ON orders (user_id, created_at DESC);
CREATE INDEX idx_users_metadata ON users USING GIN (metadata);

ALTER TABLE users ADD COLUMN tier TEXT NOT NULL DEFAULT 'free';
ALTER TABLE users DROP COLUMN unused_col;
ALTER TABLE users RENAME COLUMN old_name TO new_name;

DROP TABLE IF EXISTS old_users;
```

## Indexes — Rules of Thumb

| Pattern | Index |
|---|---|
| Equality on a column | B-tree (default) |
| Range or sort | B-tree (column order: equality → range → sort) |
| Full-text search | GIN with `tsvector` |
| JSONB containment | GIN |
| Geographic | GiST or BRIN |
| Sequential time-series | BRIN |

Cover frequently-paired columns with a single compound index, not one per column. Always run `EXPLAIN ANALYZE` to confirm the planner uses your index.

## PostgreSQL JSONB

```sql
-- Get a field
SELECT metadata->'name' FROM users;          -- jsonb
SELECT metadata->>'name' FROM users;         -- text

-- Path
SELECT metadata#>'{address,city}' FROM users;

-- Contains
SELECT * FROM users WHERE metadata @> '{"tier": "gold"}';

-- Key exists
SELECT * FROM users WHERE metadata ? 'phone';

-- Update specific field
UPDATE users SET metadata = jsonb_set(metadata, '{tier}', '"gold"');
```

## Transactions

```sql
BEGIN;
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
UPDATE accounts SET balance = balance + 100 WHERE id = 2;
COMMIT;
-- or ROLLBACK;

-- Savepoints
BEGIN;
INSERT INTO ...;
SAVEPOINT sp1;
INSERT INTO ...;
ROLLBACK TO SAVEPOINT sp1;
COMMIT;
```

Isolation levels: `READ COMMITTED` (default), `REPEATABLE READ`, `SERIALIZABLE`. Use serializable when correctness matters and you can retry on conflict.

## EXPLAIN

```sql
EXPLAIN SELECT ...;                  -- plan
EXPLAIN ANALYZE SELECT ...;          -- plan + actual timings
EXPLAIN (ANALYZE, BUFFERS) SELECT ...;
EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) SELECT ...;
```

Look for:
- `Seq Scan` on big tables → missing index.
- Estimated vs actual row counts diverging → bad stats, run `ANALYZE`.
- Sort operations spilling to disk → `work_mem` too low for the query.

## Performance Patterns

```sql
-- Pagination by keyset (much faster than OFFSET on large tables)
SELECT * FROM events
WHERE created_at < $1                -- last seen timestamp
ORDER BY created_at DESC
LIMIT 50;

-- Count estimate without scanning
SELECT reltuples::bigint AS approx_count
FROM pg_class
WHERE relname = 'events';

-- Top-N per group via DISTINCT ON
SELECT DISTINCT ON (user_id) user_id, created_at, total
FROM orders
ORDER BY user_id, created_at DESC;
```

## Useful psql

```bash
psql "postgres://user:pass@host:5432/db"

\l               # list databases
\dt              # list tables
\d users         # describe table
\di              # list indexes
\du              # list roles/users
\x               # toggle expanded display
\timing          # show query times
\copy users TO 'users.csv' CSV HEADER
\copy events FROM 'events.csv' CSV HEADER
\watch 5         # re-run last query every 5s
```

## Common Gotchas

- **`NULL` is not equal to anything.** `NULL = NULL` is `NULL`, not `TRUE`. Use `IS NULL`.
- **`COUNT(*)` vs `COUNT(col)`.** `COUNT(col)` ignores nulls.
- **String comparison is case-sensitive** in PostgreSQL by default. Use `LOWER()` or `ILIKE`.
- **Timezones.** Prefer `TIMESTAMPTZ` over `TIMESTAMP`. Internally stored as UTC.
- **Implicit casts** can defeat indexes. `WHERE int_column = '5'` may or may not use the index; cast explicitly.
- **OR is often slower than UNION ALL.** Sometimes splitting `WHERE a OR b` into two queries joined by `UNION ALL` lets the planner use indexes on each.

## See Also

- `EXPLAIN` documentation: https://www.postgresql.org/docs/current/using-explain.html
- pgAdmin, DBeaver, DataGrip for GUI clients
- pg_stat_statements extension for query profiling in production
