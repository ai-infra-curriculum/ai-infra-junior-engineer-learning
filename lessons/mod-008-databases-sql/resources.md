# Module 008 — Databases & SQL Resources

## Official documentation

- **PostgreSQL documentation** — [postgresql.org/docs](https://www.postgresql.org/docs/). The most-loved relational database; the docs are the best reference.
- **SQLite documentation** — [sqlite.org/docs.html](https://www.sqlite.org/docs.html). The standard for local development + tests.
- **MySQL documentation** — [dev.mysql.com/doc](https://dev.mysql.com/doc/). Still very common in legacy systems.
- **MongoDB documentation** — [mongodb.com/docs](https://www.mongodb.com/docs/). The standard document store.
- **Redis documentation** — [redis.io/docs](https://redis.io/docs/). In-memory key-value + data structure store.

## Books

- **SQL Cookbook (2nd ed.)** by Anthony Molinaro and Robert de Graaf. Recipe-based; lookup-friendly.
- **The Art of PostgreSQL** by Dimitri Fontaine. Modern PostgreSQL idioms.
- **Designing Data-Intensive Applications** by Martin Kleppmann. The single best book on data systems. Required reading.
- **Database Internals** by Alex Petrov. Deeper dive into how databases work.

## Interactive learning

- **SQLZoo** — [sqlzoo.net](https://sqlzoo.net/). Interactive SQL tutorials.
- **Mode SQL Tutorial** — [mode.com/sql-tutorial](https://mode.com/sql-tutorial/). Practical, analytics-focused.
- **PostgreSQL Tutorial** — [postgresqltutorial.com](https://www.postgresqltutorial.com/). Free tutorials covering basic to advanced.

## ML-specific data tools

- **DuckDB documentation** — [duckdb.org/docs](https://duckdb.org/docs/). Embedded analytical database. Increasingly used for fast local data exploration in ML.
- **ClickHouse documentation** — [clickhouse.com/docs](https://clickhouse.com/docs). Column-store for analytical workloads at scale.
- **Snowflake documentation** — [docs.snowflake.com](https://docs.snowflake.com/). The most-used cloud data warehouse.
- **BigQuery documentation** — [cloud.google.com/bigquery/docs](https://cloud.google.com/bigquery/docs). GCP's data warehouse.

## ORMs and database libraries (Python)

- **SQLAlchemy** — [docs.sqlalchemy.org](https://docs.sqlalchemy.org/). The standard Python ORM + Core. Read both layers.
- **psycopg** — [www.psycopg.org/psycopg3](https://www.psycopg.org/psycopg3/docs/). PostgreSQL driver. v3 is async-native.
- **asyncpg** — [magicstack.github.io/asyncpg](https://magicstack.github.io/asyncpg/). Fast async PostgreSQL driver.
- **alembic** — [alembic.sqlalchemy.org](https://alembic.sqlalchemy.org/). SQLAlchemy's migration tool.
- **DBOS** — [dbos.dev](https://www.dbos.dev/). Newer, durable execution backed by Postgres.

## SQL style + performance

- **Use The Index, Luke!** — [use-the-index-luke.com](https://use-the-index-luke.com/). The best free reference on database indexes and query performance.
- **SQL Style Guide** — [sqlstyle.guide](https://www.sqlstyle.guide/). Consistent conventions.
- **EXPLAIN ANALYZE walkthroughs** — practice reading query plans in PostgreSQL.

## Vector databases (ML-specific)

- **pgvector** — [github.com/pgvector/pgvector](https://github.com/pgvector/pgvector). Postgres extension for vector search. Often the right answer.
- **Chroma** — [docs.trychroma.com](https://docs.trychroma.com/). Lightweight vector DB.
- **Pinecone** — [docs.pinecone.io](https://docs.pinecone.io/). Managed vector DB.
- **Weaviate / Qdrant / Milvus** — alternative vector stores.

## Common mistakes

- N+1 queries (loading related rows in a loop).
- Storing JSON blobs and then querying inside them (use proper relations instead, or use JSONB with indexes).
- No indexes on foreign keys.
- Trusting user input in SQL strings (SQL injection).
- ORM all-the-way-down without ever looking at the generated SQL.

## Cross-references in this curriculum

- Module 001 (Python) for database client code.
- Engineer track's `mod-105-data-pipelines` for production data pipelines.
- ML Platform track for feature stores (a specialized DB pattern).
