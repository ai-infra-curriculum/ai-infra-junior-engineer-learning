# Module 008: Databases and SQL

## Module Overview

Databases are fundamental to AI/ML infrastructure, storing training data, model metadata, application state, and results. This module provides comprehensive training in relational databases with PostgreSQL, SQL query language, database design, and integration with Python applications.

You'll learn database fundamentals, SQL from basics to advanced queries, schema design, indexing, transactions, and how to work with databases in Python using SQLAlchemy. You'll also get an introduction to NoSQL databases and when to use them for AI/ML workloads.

By the end of this module, you'll be confident designing database schemas, writing efficient SQL queries, optimizing database performance, and integrating databases into Python applications and ML pipelines.

## Learning Objectives

By completing this module, you will be able to:

1. **Understand relational database concepts** and ACID properties
2. **Write SQL queries** from basic SELECT to complex JOINs and subqueries
3. **Design database schemas** with proper normalization and relationships
4. **Use PostgreSQL** effectively including advanced features
5. **Work with databases in Python** using SQLAlchemy ORM
6. **Optimize query performance** using indexes and query planning
7. **Understand transactions** and concurrency control
8. **Implement database migrations** and version control for schemas
9. **Explore NoSQL databases** and understand when to use them
10. **Apply databases to ML workflows** for storing features, models, and results

## Prerequisites

- Completion of Module 001 (Python Fundamentals) required
- Completion of Module 004 (Python for Infrastructure) recommended
- Completion of Module 002 (Linux Essentials) recommended
- Basic understanding of data structures
- Comfort with command-line interfaces

**Recommended Setup:**
- PostgreSQL 14+ installed locally or via Docker
- Python 3.9+ with virtual environment
- Database client (pgAdmin, DBeaver, or psql command-line)
- Text editor or IDE with SQL support
- Docker (optional, for database containers)

## Time Commitment

- **Total Estimated Time:** 40-50 hours
- **Lectures & Reading:** 15-18 hours
- **Hands-on Exercises:** 20-25 hours
- **Projects:** 5-7 hours

**Recommended Pace:**
- Part-time (5-10 hrs/week): 4-6 weeks
- Full-time (20-30 hrs/week): 2-3 weeks

Database skills develop through practice. Expect to spend time designing schemas, writing queries, and optimizing performance.

## Module Structure

### Week 1: SQL Fundamentals
- **Topics:** Database concepts, basic SQL, data types, simple queries
- **Key Skills:** SELECT, WHERE, INSERT, UPDATE, DELETE, basic filtering
- **Practice:** Writing basic queries, data manipulation

### Week 2: Advanced SQL
- **Topics:** JOINs, subqueries, aggregations, window functions
- **Key Skills:** Complex queries, grouping, advanced filtering
- **Practice:** Multi-table queries, analytical queries

### Week 3: Database Design and Python Integration
- **Topics:** Schema design, normalization, SQLAlchemy, migrations
- **Key Skills:** ERD design, ORM usage, database version control
- **Practice:** Designing schemas, Python database applications

### Week 4: Performance and NoSQL
- **Topics:** Indexing, query optimization, transactions, NoSQL introduction
- **Key Skills:** Performance tuning, EXPLAIN analysis, NoSQL basics
- **Practice:** Optimization exercises, exploring NoSQL databases

## Detailed Topic Breakdown

### 1. Database Fundamentals (5-6 hours)

#### 1.1 Introduction to Databases
- What are databases?
- Database management systems (DBMS)
- Relational vs non-relational databases
- Database use cases in AI/ML
- ACID properties (Atomicity, Consistency, Isolation, Durability)
- CAP theorem overview
- Database architecture

#### 1.2 Relational Database Concepts
- Tables, rows, and columns
- Primary keys and foreign keys
- Relationships (one-to-one, one-to-many, many-to-many)
- Constraints and data integrity
- Referential integrity
- Normalization overview
- Schema design principles

#### 1.3 PostgreSQL Introduction
- Why PostgreSQL?
- PostgreSQL vs MySQL vs SQLite
- Installation and setup
- psql command-line tool
- PostgreSQL architecture
- Configuration basics
- User and permission management

#### 1.4 Database Tools
- psql command-line client
- pgAdmin (GUI client)
- DBeaver (universal database tool)
- SQL editors and IDEs
- Database version control tools
- Backup and restore tools
- Monitoring tools

### 2. SQL Basics (7-9 hours)

#### 2.1 Data Types
- Numeric types (INTEGER, DECIMAL, FLOAT)
- String types (VARCHAR, TEXT, CHAR)
- Date and time types
- Boolean type
- JSON and JSONB
- Arrays
- Custom types
- Type casting

#### 2.2 Creating and Managing Tables
- CREATE TABLE syntax
- Column definitions
- Primary keys
- Foreign keys
- Constraints (NOT NULL, UNIQUE, CHECK)
- Default values
- ALTER TABLE operations
- DROP TABLE

#### 2.3 Basic Queries (SELECT)
- SELECT statement structure
- Selecting specific columns
- Selecting all columns (*)
- DISTINCT keyword
- Column aliases (AS)
- Limiting results (LIMIT)
- Ordering results (ORDER BY)
- Basic WHERE clause

#### 2.4 Filtering Data
- WHERE clause conditions
- Comparison operators (=, !=, <, >, <=, >=)
- Logical operators (AND, OR, NOT)
- IN operator
- BETWEEN operator
- LIKE and pattern matching
- NULL handling (IS NULL, IS NOT NULL)
- CASE expressions

#### 2.5 Data Manipulation (INSERT, UPDATE, DELETE)
- INSERT single row
- INSERT multiple rows
- INSERT with SELECT
- UPDATE statements
- UPDATE with conditions
- DELETE statements
- DELETE with conditions
- TRUNCATE vs DELETE
- RETURNING clause

### 3. Advanced SQL (8-10 hours)

#### 3.1 Joins
- Understanding joins
- INNER JOIN
- LEFT JOIN (LEFT OUTER JOIN)
- RIGHT JOIN (RIGHT OUTER JOIN)
- FULL OUTER JOIN
- CROSS JOIN
- Self joins
- Multiple joins
- Join conditions and performance

#### 3.2 Subqueries
- What are subqueries?
- Subqueries in WHERE clause
- Subqueries in SELECT clause
- Subqueries in FROM clause
- Correlated subqueries
- EXISTS and NOT EXISTS
- IN and NOT IN with subqueries
- Subquery performance considerations

#### 3.3 Aggregate Functions
- COUNT, SUM, AVG
- MIN and MAX
- GROUP BY clause
- HAVING clause
- Grouping by multiple columns
- Aggregating with DISTINCT
- Aggregate functions with JOINs
- Statistical aggregates

#### 3.4 Window Functions
- Introduction to window functions
- OVER clause
- PARTITION BY
- ORDER BY in window functions
- ROW_NUMBER, RANK, DENSE_RANK
- LAG and LEAD
- Running totals and moving averages
- Window frame specifications
- Practical use cases

#### 3.5 Set Operations
- UNION and UNION ALL
- INTERSECT
- EXCEPT
- Combining queries
- Set operation rules
- Performance considerations

#### 3.6 Common Table Expressions (CTEs)
- WITH clause
- Simple CTEs
- Multiple CTEs
- Recursive CTEs
- CTE vs subqueries
- Use cases for CTEs
- CTE best practices

#### 3.7 Advanced PostgreSQL Features
- JSON and JSONB operations
- Array operations
- Full-text search
- Pattern matching with regular expressions
- Date and time functions
- String functions
- Mathematical functions
- Conditional expressions

### 4. Database Design (6-8 hours)

#### 4.1 Schema Design Principles
- Entity-Relationship modeling
- Identifying entities and attributes
- Defining relationships
- Cardinality and optionality
- ERD notation and tools
- Translating ERDs to tables
- Design patterns

#### 4.2 Normalization
- What is normalization?
- First Normal Form (1NF)
- Second Normal Form (2NF)
- Third Normal Form (3NF)
- Boyce-Codd Normal Form (BCNF)
- Denormalization (when and why)
- Normal forms in practice
- Trade-offs

#### 4.3 Indexes
- What are indexes?
- B-tree indexes (default)
- Hash indexes
- GiST and GIN indexes
- Creating indexes
- Composite indexes
- Unique indexes
- Partial indexes
- Index maintenance
- When to use indexes
- Index performance impact

#### 4.4 Constraints and Data Integrity
- Primary key constraints
- Foreign key constraints
- Unique constraints
- Check constraints
- Not null constraints
- Constraint naming conventions
- Deferred constraints
- Constraint validation

#### 4.5 Views
- Creating views
- Materialized views
- View benefits
- Updateable views
- View performance
- Using views for security
- View maintenance

### 5. Python and Database Integration (7-9 hours)

#### 5.1 Python Database Drivers
- psycopg2 (PostgreSQL driver)
- Database connections
- Executing queries
- Parameterized queries
- Fetching results
- Connection pooling
- Error handling
- Context managers

#### 5.2 SQLAlchemy Core
- Introduction to SQLAlchemy
- Core vs ORM
- Engine and connections
- Metadata and Table objects
- SQL expression language
- Executing statements
- Result sets
- Transactions

#### 5.3 SQLAlchemy ORM
- Object-Relational Mapping concepts
- Defining models
- Declarative base
- Column types
- Relationships (one-to-many, many-to-many)
- Querying with ORM
- Session management
- Lazy loading vs eager loading

#### 5.4 CRUD Operations with SQLAlchemy
- Creating records
- Reading records (queries)
- Updating records
- Deleting records
- Bulk operations
- Query filtering
- Ordering and pagination
- Aggregations

#### 5.5 Database Migrations
- Why migrations?
- Alembic introduction
- Creating migrations
- Applying migrations
- Rollback strategies
- Migration best practices
- Team collaboration with migrations
- Production migration strategies

#### 5.6 Database Connection Management
- Connection pooling
- Connection lifecycle
- Connection strings
- Environment-based configuration
- Connection error handling
- Connection testing
- Performance tuning
- Cloud database connections

### 6. Performance and Optimization (5-7 hours)

#### 6.1 Query Performance
- EXPLAIN and EXPLAIN ANALYZE
- Reading query plans
- Sequential scans vs index scans
- Join algorithms
- Query optimization strategies
- Query rewriting
- Avoiding N+1 queries
- Caching strategies

#### 6.2 Indexing Strategy
- Identifying slow queries
- Choosing columns to index
- Composite index design
- Index coverage
- Index maintenance overhead
- Monitoring index usage
- Removing unused indexes
- Index bloat

#### 6.3 Transactions and Concurrency
- Transaction basics (BEGIN, COMMIT, ROLLBACK)
- ACID properties in practice
- Isolation levels
- Concurrency issues (dirty reads, lost updates)
- Locking mechanisms
- Deadlocks and prevention
- Transaction best practices
- Long-running transactions

#### 6.4 Database Maintenance
- VACUUM and ANALYZE
- Database statistics
- Table bloat management
- Backup strategies
- Point-in-time recovery
- Replication basics
- Monitoring database health
- Performance tuning parameters

### 7. NoSQL Databases (4-5 hours)

#### 7.1 NoSQL Introduction
- What is NoSQL?
- NoSQL vs SQL
- NoSQL categories (document, key-value, graph, columnar)
- CAP theorem revisited
- Eventual consistency
- Use cases for NoSQL
- Polyglot persistence

#### 7.2 Document Databases (MongoDB)
- Document model
- Collections and documents
- CRUD operations in MongoDB
- Querying documents
- Indexes in MongoDB
- Aggregation pipelines
- Schema design for documents
- When to use MongoDB

#### 7.3 Key-Value Stores (Redis)
- Key-value model
- Redis data types
- Redis commands
- Use cases (caching, sessions, queues)
- Redis persistence
- Redis in Python
- Performance characteristics
- Redis vs Memcached

#### 7.4 NoSQL for AI/ML
- Storing unstructured data
- Feature stores
- Time-series data (InfluxDB, TimescaleDB)
- Vector databases for embeddings
- Graph databases for relationships
- Choosing the right database
- Hybrid approaches

### 8. Databases in ML Workflows (3-4 hours)

#### 8.1 Training Data Storage
- Storing raw data
- Feature engineering results
- Data versioning
- Large dataset handling
- Data quality checks
- Data lineage tracking
- Partitioning strategies

#### 8.2 Model Metadata Storage
- Model registry databases
- Experiment tracking
- Hyperparameter storage
- Model versioning
- Performance metrics
- Model lineage
- Metadata querying

#### 8.3 Inference Results Storage
- Prediction logging
- Real-time vs batch storage
- Time-series prediction data
- Result aggregation
- Query patterns for analysis
- Data retention policies
- GDPR compliance

#### 8.4 ML Pipeline Databases
- Pipeline orchestration metadata
- Job status and logging
- Dependency tracking
- Scheduler databases
- Monitoring and alerting data
- Audit trails

## Lecture Outline

> **Status Update (2025-10-29):** All 5 comprehensive lecture notes are now complete and available! Each lecture includes SQL examples and database design patterns for ML infrastructure.

This module includes **5 lectures** and **7 exercises** covering databases and SQL:

### Lecture 1: Database Fundamentals (90 min)
- Database concepts
- Relational model
- PostgreSQL introduction
- Installation and setup
- First database and table
- **Lab:** PostgreSQL environment setup

### Lecture 2: SQL Basics (90 min)
- SELECT queries
- Filtering with WHERE
- Data types
- INSERT, UPDATE, DELETE
- Basic data manipulation
- **Lab:** Basic SQL operations

### Lecture 3: Advanced SQL Queries (120 min)
- JOINs deep dive
- Subqueries
- Aggregate functions
- GROUP BY and HAVING
- Window functions
- **Lab:** Complex query challenges

### Lecture 4: Database Design (90 min)
- Schema design principles
- Normalization
- ERD modeling
- Relationships and constraints
- Design patterns
- **Lab:** Designing a database schema

### Lecture 5: Indexes and Performance (90 min)
- Understanding indexes
- Query optimization
- EXPLAIN plans
- Performance tuning
- Best practices
- **Lab:** Query optimization exercises

### Lecture 6: Python and SQLAlchemy (120 min)
- psycopg2 basics
- SQLAlchemy Core
- SQLAlchemy ORM
- Database migrations
- Python database patterns
- **Lab:** Python database application

### Lecture 7: Transactions and Concurrency (90 min)
- Transaction fundamentals
- Isolation levels
- Locking and concurrency
- Deadlock handling
- Best practices
- **Lab:** Transaction scenarios

### Lecture 8: NoSQL and ML Databases (90 min)
- NoSQL overview
- MongoDB and Redis
- Databases for ML workflows
- Choosing the right database
- Polyglot persistence
- **Lab:** NoSQL hands-on

## Hands-On Exercises

> **Status Update (2025-10-29):** All 7 comprehensive exercises are now complete! Each exercise includes SQL challenges and ML database scenarios with complete solutions.

This module includes **7 exercises** organized by skill level:

### Exercise Categories

#### SQL Basics (2 exercises)
1. Creating tables and schemas
2. Basic SELECT queries
3. Filtering and sorting
4. Data manipulation (INSERT, UPDATE, DELETE)
5. Working with NULL values
6. Date and time operations
7. String manipulation
8. CASE expressions
9. Subqueries basics
10. Basic aggregations

#### Advanced SQL (10 exercises)
11. INNER and OUTER joins
12. Self-joins
13. Complex subqueries
14. Window functions
15. CTEs (Common Table Expressions)
16. Recursive queries
17. Set operations
18. JSON operations
19. Advanced aggregations
20. Query optimization challenges

#### Database Design (5 exercises)
21. ERD design exercise
22. Normalization practice
23. Schema implementation
24. Constraint design
25. Index strategy

#### Python Integration (8 exercises)
26. psycopg2 basics
27. SQLAlchemy Core queries
28. ORM model definition
29. CRUD with ORM
30. Relationships in ORM
31. Database migrations with Alembic
32. Connection pooling
33. Complete Python database app

#### Performance (4 exercises)
34. Query performance analysis
35. Index optimization
36. Transaction management
37. Concurrency scenarios

#### NoSQL (3 exercises)
38. MongoDB operations
39. Redis caching
40. NoSQL use case selection

### Exercise 06: Transaction Isolation and Concurrency Control
**Difficulty**: Intermediate to Advanced
**Duration**: 3-4 hours
**File**: `exercises/exercise-06-transactions-concurrency.md`

Build ML model registry with proper transaction handling:
- Understand and demonstrate ACID properties
- Test different transaction isolation levels (READ COMMITTED, REPEATABLE READ, SERIALIZABLE)
- Implement pessimistic locking (SELECT FOR UPDATE)
- Implement optimistic locking with version numbers
- Handle deadlock scenarios and prevention strategies
- Design concurrent-safe operations for ML metadata

### Exercise 07: NoSQL Databases for Machine Learning
**Difficulty**: Intermediate
**Duration**: 3-4 hours
**File**: `exercises/exercise-07-nosql-ml.md`

Implement hybrid architecture using SQL and NoSQL:
- Use PostgreSQL for structured training data and transactions
- Use MongoDB for flexible, document-based ML metadata
- Implement Redis for high-speed feature caching and serving
- Compare storage costs and performance across clouds
- Design data migration strategies between database types
- Create decision matrix for database selection by use case

## Assessment and Evaluation

### Knowledge Checks
- Quiz after each major section
- SQL syntax comprehension
- Database design principles
- Performance concepts
- NoSQL understanding

### Practical Assessments
- **SQL Proficiency:** Write 20+ queries of varying complexity
- **Schema Design:** Design normalized database for application
- **Python Integration:** Build application with database backend
- **Performance:** Optimize slow queries using indexes
- **ML Database:** Design database for ML workflow

### Competency Criteria
To complete this module successfully, you should be able to:
- Write complex SQL queries independently
- Design normalized database schemas
- Use PostgreSQL effectively
- Integrate databases with Python applications
- Optimize query performance
- Manage transactions and concurrency
- Choose appropriate database types
- Apply databases to ML workflows
- Troubleshoot database issues
- Implement database migrations

### Capstone Project
**ML Experiment Tracking Database:**
Design and implement complete database system for:
- Experiment metadata storage
- Model versioning
- Training metrics
- Hyperparameter tracking
- Result querying and analysis
- Python API for interaction
- Performance optimization
- Migration management
- Complete documentation

## Resources and References

> **Note:** See `resources/recommended-reading.md` for a comprehensive list of learning materials, books, and online resources.

### Essential Resources
- PostgreSQL documentation
- SQLAlchemy documentation
- SQL Tutorial (W3Schools, SQLBolt)
- PostgreSQL exercises

### Recommended Books
- "SQL Cookbook" by Anthony Molinaro
- "PostgreSQL: Up and Running" by Regina Obe
- "Learning SQL" by Alan Beaulieu
- "Database Design for Mere Mortals" by Michael Hernandez

### Online Learning
- Mode SQL Tutorial
- SQLZoo
- PostgreSQL Tutorial
- SQLAlchemy tutorials
- LeetCode database problems

### Tools
- pgAdmin
- DBeaver
- DataGrip
- psql
- TablePlus

## Getting Started

### Step 1: Install PostgreSQL
1. Install PostgreSQL locally or via Docker
2. Verify installation
3. Create test database
4. Install GUI client
5. Test connection

### Step 2: Set Up Python Environment
1. Install psycopg2 and SQLAlchemy
2. Create virtual environment
3. Test Python database connection
4. Install Alembic for migrations

### Step 3: Begin with Lecture 1
- Learn database fundamentals
- Set up PostgreSQL
- Create first tables
- Execute basic queries

### Step 4: Practice Regularly
- Complete SQL exercises
- Design practice schemas
- Build Python applications
- Optimize queries
- Work on projects

## Tips for Success

1. **Practice SQL Daily:** Regular practice builds query fluency
2. **Visualize Schemas:** Draw ERDs before implementing
3. **Use EXPLAIN:** Always check query plans for slow queries
4. **Start Normalized:** Design normalized schemas first
5. **Learn from Examples:** Study schemas of popular applications
6. **Use Migrations:** Always version control schema changes
7. **Test Transactions:** Practice isolation levels and locking
8. **Monitor Performance:** Use database monitoring tools
9. **Read Documentation:** PostgreSQL docs are comprehensive
10. **Build Projects:** Apply skills to real applications

## Next Steps

After completing this module, you'll be ready to:
- **Module 009:** Monitoring Basics (monitor databases)
- **Module 010:** Cloud Platforms (managed databases)
- Advanced topics: Database administration, replication, sharding

## Development Status

**Current Status:** Template phase - comprehensive structure in place

**Available Now:**
- Complete module structure
- Detailed topic breakdown
- Lecture outline
- Exercise framework

**In Development:**
- Full lecture notes
- SQL exercise sets
- Schema design examples
- Python integration tutorials
- Performance tuning guides
- ML database patterns

**Planned Updates:**
- Advanced PostgreSQL features
- Database administration
- Replication and HA
- Sharding strategies
- Time-series databases
- Vector databases

## Feedback and Contributions

Help improve this module:
- Report issues
- Share schema designs
- Contribute exercises
- Suggest resources

---

**Module Maintainer:** AI Infrastructure Curriculum Team
**Contact:** ai-infra-curriculum@joshua-ferguson.com
**Last Updated:** 2025-10-18
**Version:** 1.0.0-template
