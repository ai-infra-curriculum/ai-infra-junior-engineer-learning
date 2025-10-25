# Exercise 04: Logging Pipeline Implementation with Loki

## Overview

Design and deploy a production-ready centralized logging pipeline that ingests structured logs from ML infrastructure services, enriches them with metadata, stores them in a queryable backend, and provides powerful log exploration and correlation capabilities. This exercise builds a complete Grafana Loki stack integrated with the observability foundation from Exercise 01.

**Key Capabilities:**
- Centralized log aggregation for all services
- Structured log parsing and enrichment
- Log-based metrics extraction
- Correlation with traces and metrics
- Log-based alerting
- Compliance and retention management

**Difficulty:** Intermediate → Advanced
**Estimated Time:** 3–4 hours
**Prerequisites:**
- Exercises 01–03 completed (observability stack running)
- Understanding of structured logging (JSON logs)
- Docker Compose knowledge
- Basic LogQL query language familiarity

---

## Learning Objectives

By the end of this exercise, you will be able to:

1. **Deploy Production Logging Infrastructure**
   - Configure Grafana Loki for multi-tenant log storage
   - Set up Promtail for log collection and shipping
   - Implement retention and compaction strategies

2. **Build Log Processing Pipelines**
   - Parse structured JSON logs with pipeline stages
   - Extract labels and fields from log entries
   - Enrich logs with metadata and context

3. **Query and Visualize Logs**
   - Write LogQL queries for log exploration
   - Build log dashboards in Grafana
   - Correlate logs with metrics and traces

4. **Implement Log-Based Metrics**
   - Derive metrics from log patterns
   - Create counters and histograms from logs
   - Alert on log-based conditions

5. **Ensure Compliance and Security**
   - Implement log redaction for PII
   - Configure retention policies
   - Set up access controls

---

## Architecture Overview

### Logging Stack Components

```
┌─────────────────────────────────────────────────────────────────┐
│                     Log Producers                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  Inference   │  │  Prometheus  │  │   Node       │          │
│  │  Gateway     │  │  (logs)      │  │   Exporter   │          │
│  │  (JSON logs) │  │              │  │   (logs)     │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
│         │                 │                 │                    │
└─────────┼─────────────────┼─────────────────┼────────────────────┘
          │                 │                 │
          └─────────────────┼─────────────────┘
                            │
                    ┌───────▼────────┐
                    │   Promtail     │
                    │  (Log Shipper) │
                    │                │
                    │  - Discovery   │
                    │  - Parsing     │
                    │  - Labels      │
                    │  - Enrichment  │
                    └───────┬────────┘
                            │
                            │ Push logs with labels
                            │
                    ┌───────▼────────┐
                    │   Loki         │
                    │  (Log Store)   │
                    │                │
                    │  - Ingestion   │
                    │  - Indexing    │
                    │  - Compression │
                    │  - Retention   │
                    └───────┬────────┘
                            │
          ┌─────────────────┼─────────────────┐
          │                 │                 │
    ┌─────▼─────┐    ┌──────▼──────┐   ┌─────▼─────┐
    │  Grafana  │    │  Log-Based  │   │   Tempo   │
    │  (Query)  │    │   Metrics   │   │  (Traces) │
    │           │    │  (Derived)  │   │           │
    │ - Explore │    │             │   │ Correlation│
    │ - Dashbds │    │ - Counters  │   │           │
    │ - Alerts  │    │ - Rates     │   │           │
    └───────────┘    └─────────────┘   └───────────┘
```

### Log Flow

1. **Collection:** Promtail discovers and tails log files from Docker containers
2. **Parsing:** JSON logs are parsed, fields extracted as labels and metadata
3. **Enrichment:** Additional context (service, environment, host) added
4. **Shipping:** Logs pushed to Loki with labels for efficient indexing
5. **Storage:** Loki chunks logs, indexes labels, compresses data
6. **Query:** LogQL queries filter and aggregate logs in Grafana
7. **Correlation:** Trace IDs link logs to distributed traces

---

## Part 1: Project Setup and Planning

### 1.1 Create Project Structure

Create the logging pipeline directory structure:

```bash
cd ~/monitoring-lab
mkdir -p logging/{loki,promtail,dashboards,docs}
```

**Directory structure:**
```
logging/
├── docker-compose.logging.yml          # Logging stack services
├── loki/
│   ├── loki-config.yaml               # Loki server configuration
│   └── loki-rules.yaml                # Log-based recording/alerting rules
├── promtail/
│   ├── promtail-config.yaml           # Log collection configuration
│   └── positions.yaml                 # Log position tracking (auto-generated)
├── dashboards/
│   ├── logging-overview.json          # Log analytics dashboard
│   └── log-troubleshooting.json       # Debugging dashboard
└── docs/
    ├── logging-architecture.md        # Architecture documentation
    ├── logging-governance.md          # Retention and compliance
    └── logql-queries.md              # Query reference
```

### 1.2 Define Logging Requirements

**Create `logging/docs/logging-requirements.md`:**

```markdown
# Logging Requirements - ML Infrastructure Platform

## Log Classes and Retention

| Log Class | Sources | Retention | Storage Tier | Purpose |
|-----------|---------|-----------|--------------|---------|
| Application Logs | Inference Gateway, ML services | 30 days | Hot (Loki) | Debugging, troubleshooting |
| Access Logs | API Gateway, Load Balancers | 90 days | Warm (Object Storage) | Audit, analytics |
| Audit Logs | Authentication, Authorization | 1 year | Cold (S3/GCS) | Compliance, security |
| System Logs | Nodes, Infrastructure | 14 days | Hot (Loki) | Infrastructure monitoring |
| ML Logs | Training jobs, Model serving | 60 days | Warm | Model debugging, metrics |

## Log Volume Estimates

- **Inference Gateway:** ~500 MB/day (10K req/min, 5KB avg log)
- **ML Training Jobs:** ~2 GB/day (batch jobs)
- **System Logs:** ~200 MB/day
- **Total:** ~3 GB/day → ~90 GB/month

## Query Patterns

1. **Error Investigation:** Search by trace_id, error message, timeframe
2. **Performance Analysis:** Filter by latency_ms, model_version
3. **Audit Compliance:** Find all access to specific models/data
4. **Trend Analysis:** Count errors over time, group by service

## Compliance Requirements

- **PII Redaction:** Email addresses, user IDs must be masked
- **Access Control:** Only on-call team can query production logs
- **Audit Trail:** Track who queries sensitive logs
- **Data Residency:** Logs must remain in US region
```

### 1.3 Architecture Documentation

**Create `logging/docs/logging-architecture.md`:**

```markdown
# Logging Architecture - Design Decisions

## Why Grafana Loki?

**Selected:** Grafana Loki
**Alternatives Considered:** Elasticsearch, Splunk, CloudWatch Logs

### Decision Rationale

| Factor | Loki | Elasticsearch | Verdict |
|--------|------|---------------|---------|
| Cost | Low (no full-text indexing) | High (indexes all fields) | ✅ Loki |
| Query Speed | Fast for label-based queries | Fast for full-text search | Tie |
| Storage Efficiency | 10x compression | Larger indexes | ✅ Loki |
| Integration | Native Grafana | Requires Kibana or plugin | ✅ Loki |
| Ops Complexity | Low (single binary) | High (cluster management) | ✅ Loki |
| Scalability | Horizontal (via object storage) | Horizontal (complex) | ✅ Loki |

**Decision:** Loki is ideal for structured logs with known query patterns.

## Indexing Strategy

Loki indexes **labels only**, not log content. Choose labels carefully:

**Good Labels (Low Cardinality):**
- `service` (inference-gateway, training-service)
- `environment` (lab, staging, production)
- `level` (debug, info, warning, error, critical)
- `cluster` (us-east-1, us-west-2)
- `job` (docker-logs, systemd-logs)

**Bad Labels (High Cardinality - AVOID):**
- `trace_id` (millions of unique values)
- `request_id` (unique per request)
- `user_id` (thousands of users)
- `model_version` (acceptable if <100 versions)

**Rule:** Keep total label combinations < 10,000.

## Retention Strategy

```
┌─────────────────────────────────────────────────────────────┐
│  Hot Tier (Loki Local Disk) - 7 days                       │
│  - Fast queries                                              │
│  - Frequent access                                           │
│  - All log classes                                           │
└─────────────────┬───────────────────────────────────────────┘
                  │ Compaction
┌─────────────────▼───────────────────────────────────────────┐
│  Warm Tier (Object Storage S3/GCS) - 23 days               │
│  - Compressed chunks                                         │
│  - On-demand queries                                         │
│  - Application + ML logs                                     │
└─────────────────┬───────────────────────────────────────────┘
                  │ Archive
┌─────────────────▼───────────────────────────────────────────┐
│  Cold Tier (Glacier/Coldline) - 335 days                   │
│  - Audit logs only                                           │
│  - Compliance retention                                      │
│  - Rare access (hours to restore)                           │
└─────────────────────────────────────────────────────────────┘
```

## Scaling Considerations

**Current Lab (Single Node):**
- Loki: 1 instance
- Promtail: 1 per host
- Throughput: ~10 MB/s ingestion

**Production (Distributed):**
- Loki: 3+ distributors, 3+ ingesters, 3+ queriers
- Object Storage: S3/GCS for chunks
- Caching: Memcached for query acceleration
- Throughput: 100+ MB/s ingestion
```

---

## Part 2: Deploy Loki and Promtail

### 2.1 Docker Compose Configuration

**Create `logging/docker-compose.logging.yml`:**

```yaml
version: '3.8'

services:
  loki:
    image: grafana/loki:2.9.3
    container_name: loki
    restart: unless-stopped
    ports:
      - "3100:3100"
    volumes:
      - ./loki/loki-config.yaml:/etc/loki/loki-config.yaml:ro
      - loki-data:/loki
    command: -config.file=/etc/loki/loki-config.yaml
    networks:
      - monitoring
    healthcheck:
      test: ["CMD", "wget", "--quiet", "--tries=1", "--spider", "http://localhost:3100/ready"]
      interval: 10s
      timeout: 5s
      retries: 5
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  promtail:
    image: grafana/promtail:2.9.3
    container_name: promtail
    restart: unless-stopped
    volumes:
      # Promtail configuration
      - ./promtail/promtail-config.yaml:/etc/promtail/config.yaml:ro

      # Docker container logs (read-only)
      - /var/lib/docker/containers:/var/lib/docker/containers:ro

      # Docker socket to get container metadata
      - /var/run/docker.sock:/var/run/docker.sock:ro

      # Host logs (optional)
      - /var/log:/var/log:ro

      # Position tracking (persistent)
      - ./promtail/positions.yaml:/tmp/positions.yaml
    command: -config.file=/etc/promtail/config.yaml
    networks:
      - monitoring
    depends_on:
      loki:
        condition: service_healthy
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  # Update Grafana to include Loki datasource
  grafana:
    image: grafana/grafana:10.2.3
    container_name: grafana
    restart: unless-stopped
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_USER=admin
      - GF_SECURITY_ADMIN_PASSWORD=admin
      - GF_UNIFIED_ALERTING_ENABLED=true
      - GF_PATHS_PROVISIONING=/etc/grafana/provisioning
      - GF_FEATURE_TOGGLES_ENABLE=traceqlEditor
    volumes:
      - grafana-data:/var/lib/grafana
      - ../grafana/provisioning:/etc/grafana/provisioning:ro
      - ./dashboards:/var/lib/grafana/dashboards/logging:ro
    networks:
      - monitoring
    depends_on:
      - loki
      - prometheus

volumes:
  loki-data:
    driver: local
  grafana-data:
    driver: local

networks:
  monitoring:
    external: true
```

### 2.2 Loki Configuration

**Create `logging/loki/loki-config.yaml`:**

```yaml
# Loki Server Configuration
# Version: 2.9.3
# Deployment: Single-node (for lab/dev)

auth_enabled: false  # Multi-tenancy disabled for lab

server:
  http_listen_port: 3100
  grpc_listen_port: 9096
  log_level: info

  # Graceful shutdown
  graceful_shutdown_timeout: 30s

# Distributor receives logs from Promtail
distributor:
  ring:
    kvstore:
      store: inmemory  # Use memberlist for production

# Ingester writes logs to storage
ingester:
  # Lifecycle configuration
  lifecycler:
    address: 127.0.0.1
    ring:
      kvstore:
        store: inmemory
      replication_factor: 1  # Single node
    final_sleep: 0s

  # Chunk configuration
  chunk_idle_period: 1h        # Flush chunks after 1h idle
  max_chunk_age: 1h            # Force flush after 1h
  chunk_target_size: 1048576   # Target chunk size: 1MB
  chunk_retain_period: 30s     # Keep chunks in memory briefly

  # WAL (Write-Ahead Log) for durability
  wal:
    enabled: true
    dir: /loki/wal
    replay_memory_ceiling: 1GB

# Schema defines how logs are indexed and stored
schema_config:
  configs:
    # Schema v12 (current)
    - from: 2024-01-01
      store: boltdb-shipper
      object_store: filesystem
      schema: v12
      index:
        prefix: index_
        period: 24h  # Daily indexes

# Storage configuration
storage_config:
  # BoltDB for index storage
  boltdb_shipper:
    active_index_directory: /loki/boltdb-shipper-active
    cache_location: /loki/boltdb-shipper-cache
    cache_ttl: 24h
    shared_store: filesystem

    # Index compaction (reduce storage)
    compactor:
      working_directory: /loki/compactor
      shared_store: filesystem
      compaction_interval: 10m

  # Filesystem for chunk storage (use S3/GCS in production)
  filesystem:
    directory: /loki/chunks

# Compactor removes deleted data and optimizes indexes
compactor:
  working_directory: /loki/compactor
  shared_store: filesystem
  compaction_interval: 10m
  retention_enabled: true  # Enable retention deletion
  retention_delete_delay: 2h
  retention_delete_worker_count: 150

# Limits prevent abuse and control resource usage
limits_config:
  # Ingestion limits
  ingestion_rate_mb: 10             # Max 10 MB/s per tenant
  ingestion_burst_size_mb: 20       # Burst up to 20 MB
  max_streams_per_user: 10000       # Max unique label combinations
  max_entries_limit_per_query: 5000 # Limit query results

  # Retention per stream (label combination)
  retention_period: 168h  # 7 days (7 * 24h)

  # Query limits
  max_query_length: 721h            # Max 30 days lookback
  max_query_parallelism: 32
  split_queries_by_interval: 15m    # Split large queries

  # Per-stream rate limits (prevent high-cardinality labels)
  per_stream_rate_limit: 3MB
  per_stream_rate_limit_burst: 15MB

  # Reject old logs
  reject_old_samples: true
  reject_old_samples_max_age: 168h  # Reject logs older than 7 days

  # Cardinality limit (prevent label explosion)
  max_label_names_per_series: 15

# Querier executes LogQL queries
querier:
  max_concurrent: 10
  query_timeout: 1m

# Query frontend splits queries and caches results
query_range:
  # Results cache for repeated queries
  results_cache:
    cache:
      embedded_cache:
        enabled: true
        max_size_mb: 100
        ttl: 24h

  # Split long queries into smaller chunks
  split_queries_by_interval: 15m

  # Cache results
  cache_results: true

# Ruler evaluates recording and alerting rules
ruler:
  storage:
    type: local
    local:
      directory: /loki/rules
  rule_path: /loki/rules-temp
  alertmanager_url: http://alertmanager:9093
  ring:
    kvstore:
      store: inmemory
  enable_api: true
  enable_alertmanager_v2: true

# Analytics (disable in production if privacy required)
analytics:
  reporting_enabled: false

# Tracing integration (optional)
tracing:
  enabled: false
```

**Key Configuration Highlights:**

1. **Retention:** 7 days (configurable per use case)
2. **Compaction:** Automatic every 10 minutes
3. **Rate Limits:** 10 MB/s per tenant (prevents abuse)
4. **Cardinality Limits:** Max 10,000 label combinations
5. **Query Limits:** 5,000 results, 30-day max lookback

### 2.3 Promtail Configuration

**Create `logging/promtail/promtail-config.yaml`:**

```yaml
# Promtail Configuration
# Version: 2.9.3
# Purpose: Collect and ship Docker logs to Loki

server:
  http_listen_port: 9080
  grpc_listen_port: 0
  log_level: info

  # Health check endpoint
  healthcheck:
    enabled: true

# Position tracking - remembers last read position
positions:
  filename: /tmp/positions.yaml
  sync_period: 10s

# Loki client configuration
clients:
  - url: http://loki:3100/loki/api/v1/push
    batchwait: 1s      # Wait up to 1s to batch logs
    batchsize: 1048576 # Max batch size: 1MB

    # Retry configuration
    backoff_config:
      min_period: 500ms
      max_period: 5m
      max_retries: 10

    # Timeout
    timeout: 10s

    # Tenant ID (for multi-tenancy)
    # tenant_id: "team-ml-platform"

# Scrape configurations - define how to collect logs
scrape_configs:
  ##############################################################################
  # Scrape Config 1: Docker Container Logs (Primary)
  ##############################################################################
  - job_name: docker-containers

    # Docker service discovery
    docker_sd_configs:
      - host: unix:///var/run/docker.sock
        refresh_interval: 5s

        # Filter containers
        filters:
          - name: label
            values: ["logging=promtail"]  # Only containers with this label

    # Relabel to extract metadata from Docker labels
    relabel_configs:
      # Container name
      - source_labels: ['__meta_docker_container_name']
        regex: '/(.*)'
        target_label: 'container'

      # Service name from Docker label
      - source_labels: ['__meta_docker_container_label_com_docker_compose_service']
        target_label: 'service'

      # Environment from Docker label
      - source_labels: ['__meta_docker_container_label_environment']
        target_label: 'environment'

      # Cluster from hostname
      - source_labels: ['__meta_docker_container_label_cluster']
        target_label: 'cluster'
        replacement: 'lab-cluster'

      # Docker image
      - source_labels: ['__meta_docker_container_label_com_docker_compose_image']
        target_label: 'image'

      # Log path
      - source_labels: ['__meta_docker_container_log_stream']
        target_label: 'stream'

    # Pipeline stages - parse and transform logs
    pipeline_stages:
      # Stage 1: Parse Docker JSON log wrapper
      - docker: {}

      # Stage 2: Parse application JSON logs
      - json:
          expressions:
            timestamp: time
            level: level
            logger: logger
            event: event
            message: message
            trace_id: trace_id
            span_id: span_id
            latency_ms: latency_ms
            status_code: status_code
            method: method
            path: path
            model_name: model_name
            model_version: model_version
            error: error
            user_id: user_id

      # Stage 3: Extract timestamp
      - timestamp:
          source: timestamp
          format: RFC3339Nano
          fallback_formats:
            - "2006-01-02T15:04:05.999999999Z07:00"
            - "2006-01-02T15:04:05Z07:00"

      # Stage 4: Promote fields to labels (low cardinality only!)
      - labels:
          level:
          logger:
          event:
          status_code:
          method:

      # Stage 5: Redact PII (emails, user IDs)
      - replace:
          expression: '(?P<email>[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
          replace: '***REDACTED_EMAIL***'

      - replace:
          expression: '"user_id":\s*"([^"]+)"'
          replace: '"user_id":"***REDACTED***"'

      # Stage 6: Drop debug logs in production (optional)
      # - match:
      #     selector: '{environment="production",level="debug"}'
      #     action: drop

      # Stage 7: Template output format
      - template:
          source: message
          template: '{{ .message }}'

      # Stage 8: Metrics from logs (derive Prometheus metrics)
      - metrics:
          # Count log lines by level
          log_lines_total:
            type: Counter
            description: "Total log lines"
            source: level
            config:
              action: inc
              match_all: true

          # Count errors
          log_errors_total:
            type: Counter
            description: "Total error log lines"
            source: level
            config:
              action: inc
              value: "1"
              match_all: false
              filter: 'level == "error"'

          # Histogram of latency from logs
          request_duration_seconds_from_logs:
            type: Histogram
            description: "Request duration from logs"
            source: latency_ms
            config:
              buckets: [0.01, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10]

  ##############################################################################
  # Scrape Config 2: Inference Gateway Static Logs (Fallback)
  ##############################################################################
  - job_name: inference-gateway-file

    static_configs:
      - targets:
          - localhost
        labels:
          job: inference-gateway
          service: inference-gateway
          environment: lab
          __path__: /var/log/inference-gateway/*.log

    pipeline_stages:
      - json:
          expressions:
            level: level
            message: message
            trace_id: trace_id
      - labels:
          level:

  ##############################################################################
  # Scrape Config 3: System Logs (syslog)
  ##############################################################################
  - job_name: syslog

    static_configs:
      - targets:
          - localhost
        labels:
          job: syslog
          service: system
          __path__: /var/log/syslog

    pipeline_stages:
      # Syslog parsing
      - regex:
          expression: '^(?P<timestamp>\w+\s+\d+\s+\d+:\d+:\d+)\s+(?P<hostname>\S+)\s+(?P<process>\S+)(\[(?P<pid>\d+)\])?:\s+(?P<message>.*)$'

      - timestamp:
          source: timestamp
          format: "Jan _2 15:04:05"

      - labels:
          hostname:
          process:

      - output:
          source: message

# Limits
limits_config:
  readline_rate: 10000       # Max 10K lines/sec
  readline_burst: 20000      # Burst up to 20K lines

# Tracing (optional)
tracing:
  enabled: false
```

**Pipeline Stages Explained:**

1. **docker:** Unwraps Docker JSON log format
2. **json:** Parses application JSON logs and extracts fields
3. **timestamp:** Parses timestamp from logs
4. **labels:** Promotes low-cardinality fields to Loki labels
5. **replace:** Redacts PII (emails, user IDs)
6. **metrics:** Derives Prometheus metrics from logs
7. **template:** Formats final log message

---

## Part 3: Configure Inference Gateway Logging

### 3.1 Update Inference Gateway Docker Compose

Add logging label to the inference gateway service:

**Edit `observability/docker-compose.observability.yml`:**

```yaml
services:
  inference-gateway:
    image: inference-gateway:latest
    build:
      context: ./app
      dockerfile: Dockerfile
    container_name: inference-gateway
    restart: unless-stopped
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=lab
      - LOG_LEVEL=info
      - LOKI_ENABLED=true
    labels:
      # Enable Promtail log collection
      logging: "promtail"
      environment: "lab"
      service: "inference-gateway"
      cluster: "lab-cluster"
    networks:
      - monitoring
    depends_on:
      - loki
```

### 3.2 Verify JSON Log Format

Ensure the inference gateway emits structured JSON logs:

**Example log output:**
```json
{
  "time": "2025-10-23T14:32:15.123456Z",
  "level": "info",
  "logger": "uvicorn.access",
  "event": "http_request",
  "message": "GET /api/v1/predict 200 OK",
  "trace_id": "a1b2c3d4e5f6g7h8i9j0",
  "span_id": "1a2b3c4d5e6f7g8h",
  "method": "GET",
  "path": "/api/v1/predict",
  "status_code": 200,
  "latency_ms": 45.3,
  "model_name": "resnet50",
  "model_version": "v1.2.0",
  "request_id": "req_abc123"
}
```

---

## Part 4: Deploy and Validate Logging Stack

### 4.1 Start Loki and Promtail

```bash
cd ~/monitoring-lab/logging

# Create network if doesn't exist
docker network create monitoring 2>/dev/null || true

# Start logging stack
docker-compose -f docker-compose.logging.yml up -d

# Check logs
docker-compose -f docker-compose.logging.yml logs -f loki promtail
```

**Expected output:**
```
loki      | level=info msg="Loki started"
loki      | level=info msg="Server listening on :3100"
promtail  | level=info msg="Starting Promtail"
promtail  | level=info msg="Seeking to position" position=0
promtail  | level=info msg="Successfully tailed logs"
```

### 4.2 Validate Loki Readiness

```bash
# Check Loki health
curl http://localhost:3100/ready

# Expected output: "ready"

# Check Loki metrics
curl http://localhost:3100/metrics | grep loki_ingester_streams

# Expected output:
# loki_ingester_streams 12
```

### 4.3 Validate Promtail Shipping

```bash
# Check Promtail metrics
curl http://localhost:9080/metrics | grep promtail_sent

# Expected output:
# promtail_sent_entries_total{host="localhost"} 1523
# promtail_sent_bytes_total{host="localhost"} 523041
```

### 4.4 Generate Test Logs

```bash
# Trigger inference requests to generate logs
for i in {1..20}; do
  curl -X POST http://localhost:8000/api/v1/predict \
    -H "Content-Type: application/json" \
    -d '{"image_url": "https://example.com/image.jpg"}'
  sleep 0.5
done
```

---

## Part 5: Query Logs with LogQL

### 5.1 Basic LogQL Queries

Open Grafana Explore (http://localhost:3000/explore) and select "Loki" datasource.

**Query 1: All logs from inference gateway**
```logql
{service="inference-gateway"}
```

**Query 2: Error logs only**
```logql
{service="inference-gateway", level="error"}
```

**Query 3: Logs containing "timeout"**
```logql
{service="inference-gateway"} |= "timeout"
```

**Query 4: Logs NOT containing "health_check"**
```logql
{service="inference-gateway"} != "health_check"
```

**Query 5: Regex filter for 5xx status codes**
```logql
{service="inference-gateway"} |~ "status_code\":5.."
```

### 5.2 Advanced LogQL with Parsing

**Query 6: Parse JSON and filter by latency**
```logql
{service="inference-gateway"}
  | json
  | latency_ms > 100
```

**Query 7: Extract specific field**
```logql
{service="inference-gateway"}
  | json
  | line_format "{{.method}} {{.path}} - {{.latency_ms}}ms"
```

**Query 8: Filter by trace_id**
```logql
{service="inference-gateway"}
  | json
  | trace_id = "a1b2c3d4e5f6g7h8i9j0"
```

### 5.3 Aggregation and Metrics

**Query 9: Count logs by level (last 5m)**
```logql
sum by (level) (
  count_over_time({service="inference-gateway"}[5m])
)
```

**Query 10: Error rate (errors per minute)**
```logql
sum(rate({service="inference-gateway", level="error"}[5m])) * 60
```

**Query 11: P95 latency from logs**
```logql
quantile_over_time(0.95,
  {service="inference-gateway"}
  | json
  | unwrap latency_ms [5m]
)
```

**Query 12: Bytes scanned per second**
```logql
sum(bytes_over_time({service="inference-gateway"}[1m])) / 60
```

**Query 13: Top 5 error messages**
```logql
topk(5,
  sum by (message) (
    count_over_time({service="inference-gateway", level="error"}[1h])
  )
)
```

### 5.4 Pattern Extraction

**Query 14: Extract model version from logs**
```logql
{service="inference-gateway"}
  | json
  | model_version != ""
  | line_format "{{.model_version}}"
```

**Query 15: Count unique trace IDs (cardinality)**
```logql
count(
  count by (trace_id) (
    {service="inference-gateway"}
    | json
  )
)
```

---

## Part 6: Build Log Analytics Dashboard

### 6.1 Create Logging Overview Dashboard

**Create `logging/dashboards/logging-overview.json`:**

```json
{
  "dashboard": {
    "id": null,
    "uid": "logging-overview",
    "title": "Logging Overview - Inference Gateway",
    "tags": ["logging", "loki", "ml-platform"],
    "timezone": "browser",
    "schemaVersion": 38,
    "version": 1,
    "refresh": "30s",

    "templating": {
      "list": [
        {
          "name": "environment",
          "type": "custom",
          "query": "lab,staging,production",
          "current": {
            "selected": true,
            "text": "lab",
            "value": "lab"
          }
        },
        {
          "name": "service",
          "type": "query",
          "datasource": "Loki",
          "query": "label_values(service)",
          "current": {
            "selected": false,
            "text": "inference-gateway",
            "value": "inference-gateway"
          },
          "refresh": 1
        },
        {
          "name": "time_range",
          "type": "custom",
          "query": "5m,15m,1h,6h,24h",
          "current": {
            "text": "5m",
            "value": "5m"
          }
        }
      ]
    },

    "panels": [
      {
        "id": 1,
        "type": "stat",
        "title": "Total Log Volume (last $time_range)",
        "gridPos": {"x": 0, "y": 0, "w": 6, "h": 4},
        "targets": [{
          "datasource": "Loki",
          "expr": "sum(count_over_time({service=\"$service\", environment=\"$environment\"}[$time_range]))",
          "refId": "A"
        }],
        "fieldConfig": {
          "defaults": {
            "unit": "short",
            "color": {"mode": "thresholds"},
            "thresholds": {
              "mode": "absolute",
              "steps": [
                {"color": "green", "value": null},
                {"color": "yellow", "value": 10000},
                {"color": "red", "value": 50000}
              ]
            }
          }
        },
        "options": {
          "graphMode": "area",
          "textMode": "value_and_name"
        }
      },

      {
        "id": 2,
        "type": "stat",
        "title": "Error Rate (errors/min)",
        "gridPos": {"x": 6, "y": 0, "w": 6, "h": 4},
        "targets": [{
          "datasource": "Loki",
          "expr": "sum(rate({service=\"$service\", environment=\"$environment\", level=\"error\"}[$time_range])) * 60",
          "refId": "A"
        }],
        "fieldConfig": {
          "defaults": {
            "unit": "short",
            "decimals": 2,
            "color": {"mode": "thresholds"},
            "thresholds": {
              "mode": "absolute",
              "steps": [
                {"color": "green", "value": null},
                {"color": "yellow", "value": 1},
                {"color": "red", "value": 10}
              ]
            }
          }
        }
      },

      {
        "id": 3,
        "type": "stat",
        "title": "Data Ingestion Rate (MB/s)",
        "gridPos": {"x": 12, "y": 0, "w": 6, "h": 4},
        "targets": [{
          "datasource": "Loki",
          "expr": "sum(rate(bytes_over_time({service=\"$service\", environment=\"$environment\"}[$time_range]))) / 1024 / 1024",
          "refId": "A"
        }],
        "fieldConfig": {
          "defaults": {
            "unit": "MBs",
            "decimals": 3,
            "color": {"mode": "palette-classic"}
          }
        }
      },

      {
        "id": 4,
        "type": "stat",
        "title": "Unique Streams (Label Combinations)",
        "gridPos": {"x": 18, "y": 0, "w": 6, "h": 4},
        "targets": [{
          "datasource": "Loki",
          "expr": "count(count by (service, environment, level, logger) (rate({service=\"$service\"}[1m])))",
          "refId": "A"
        }],
        "fieldConfig": {
          "defaults": {
            "unit": "short",
            "thresholds": {
              "steps": [
                {"color": "green", "value": null},
                {"color": "yellow", "value": 100},
                {"color": "red", "value": 1000}
              ]
            }
          }
        }
      },

      {
        "id": 5,
        "type": "timeseries",
        "title": "Log Volume by Level",
        "gridPos": {"x": 0, "y": 4, "w": 12, "h": 8},
        "targets": [{
          "datasource": "Loki",
          "expr": "sum by (level) (rate({service=\"$service\", environment=\"$environment\"}[$__interval]))",
          "refId": "A",
          "legendFormat": "{{level}}"
        }],
        "fieldConfig": {
          "defaults": {
            "unit": "logs/s",
            "custom": {
              "drawStyle": "line",
              "fillOpacity": 30,
              "stacking": {"mode": "normal"}
            }
          },
          "overrides": [
            {
              "matcher": {"id": "byName", "options": "error"},
              "properties": [{"id": "color", "value": {"fixedColor": "red", "mode": "fixed"}}]
            },
            {
              "matcher": {"id": "byName", "options": "warning"},
              "properties": [{"id": "color", "value": {"fixedColor": "yellow", "mode": "fixed"}}]
            },
            {
              "matcher": {"id": "byName", "options": "info"},
              "properties": [{"id": "color", "value": {"fixedColor": "blue", "mode": "fixed"}}]
            }
          ]
        }
      },

      {
        "id": 6,
        "type": "piechart",
        "title": "Log Distribution by Level",
        "gridPos": {"x": 12, "y": 4, "w": 12, "h": 8},
        "targets": [{
          "datasource": "Loki",
          "expr": "sum by (level) (count_over_time({service=\"$service\", environment=\"$environment\"}[$time_range]))",
          "refId": "A",
          "legendFormat": "{{level}}"
        }],
        "options": {
          "pieType": "donut",
          "legend": {"displayMode": "table", "placement": "right"}
        }
      },

      {
        "id": 7,
        "type": "table",
        "title": "Top 10 Error Messages",
        "gridPos": {"x": 0, "y": 12, "w": 24, "h": 8},
        "targets": [{
          "datasource": "Loki",
          "expr": "topk(10, sum by (message) (count_over_time({service=\"$service\", level=\"error\"} | json [$time_range])))",
          "refId": "A",
          "format": "table",
          "instant": true
        }],
        "transformations": [
          {
            "id": "organize",
            "options": {
              "renameByName": {
                "message": "Error Message",
                "Value": "Count"
              }
            }
          }
        ],
        "fieldConfig": {
          "defaults": {
            "custom": {
              "align": "left",
              "width": 800
            }
          }
        }
      },

      {
        "id": 8,
        "type": "logs",
        "title": "Live Error Logs",
        "gridPos": {"x": 0, "y": 20, "w": 24, "h": 10},
        "targets": [{
          "datasource": "Loki",
          "expr": "{service=\"$service\", environment=\"$environment\", level=~\"error|critical\"}",
          "refId": "A"
        }],
        "options": {
          "showTime": true,
          "showLabels": true,
          "showCommonLabels": false,
          "wrapLogMessage": true,
          "prettifyLogMessage": true,
          "enableLogDetails": true,
          "dedupStrategy": "none",
          "sortOrder": "Descending"
        }
      },

      {
        "id": 9,
        "type": "timeseries",
        "title": "P95 Latency from Logs",
        "gridPos": {"x": 0, "y": 30, "w": 12, "h": 8},
        "targets": [{
          "datasource": "Loki",
          "expr": "quantile_over_time(0.95, {service=\"$service\"} | json | unwrap latency_ms [$__interval]) by (model_version)",
          "refId": "A",
          "legendFormat": "{{model_version}}"
        }],
        "fieldConfig": {
          "defaults": {
            "unit": "ms",
            "custom": {"drawStyle": "line", "lineWidth": 2}
          }
        }
      },

      {
        "id": 10,
        "type": "timeseries",
        "title": "HTTP Status Code Distribution",
        "gridPos": {"x": 12, "y": 30, "w": 12, "h": 8},
        "targets": [{
          "datasource": "Loki",
          "expr": "sum by (status_code) (rate({service=\"$service\"} | json | status_code != \"\" [$__interval]))",
          "refId": "A",
          "legendFormat": "{{status_code}}"
        }],
        "fieldConfig": {
          "defaults": {
            "unit": "reqps",
            "custom": {"stacking": {"mode": "normal"}}
          },
          "overrides": [
            {
              "matcher": {"id": "byRegexp", "options": "5.."},
              "properties": [{"id": "color", "value": {"fixedColor": "red", "mode": "fixed"}}]
            },
            {
              "matcher": {"id": "byRegexp", "options": "4.."},
              "properties": [{"id": "color", "value": {"fixedColor": "yellow", "mode": "fixed"}}]
            }
          ]
        }
      }
    ]
  }
}
```

### 6.2 Provision Dashboard in Grafana

**Create `grafana/provisioning/dashboards/logging.yml`:**

```yaml
apiVersion: 1

providers:
  - name: 'Logging Dashboards'
    orgId: 1
    folder: 'Logging'
    type: file
    disableDeletion: false
    updateIntervalSeconds: 10
    allowUiUpdates: true
    options:
      path: /var/lib/grafana/dashboards/logging
```

---

## Part 7: Log-Based Metrics and Alerting

### 7.1 Configure Log-Based Recording Rules

Loki can evaluate recording rules to pre-compute metrics from logs.

**Create `logging/loki/loki-rules.yaml`:**

```yaml
# Loki Recording and Alerting Rules
groups:
  - name: inference_gateway_log_metrics
    interval: 1m
    rules:
      # Recording rule: Error rate from logs
      - record: log:error_rate:1m
        expr: |
          sum by (service, environment) (
            rate({service=~".+"} | json | level="error" [1m])
          )
        labels:
          source: loki

      # Recording rule: P99 latency from logs
      - record: log:latency:p99:5m
        expr: |
          quantile_over_time(0.99,
            {service="inference-gateway"}
            | json
            | unwrap latency_ms [5m]
          ) by (service, model_version)
        labels:
          source: loki

      # Recording rule: Timeout errors
      - record: log:timeout_errors:rate1m
        expr: |
          sum by (service) (
            rate({service=~".+"} |= "timeout" [1m])
          )
        labels:
          source: loki
          error_type: timeout

  - name: inference_gateway_log_alerts
    interval: 1m
    rules:
      # Alert: High error rate
      - alert: HighErrorRateFromLogs
        expr: |
          log:error_rate:1m{service="inference-gateway"} > 1
        for: 5m
        labels:
          severity: warning
          source: loki
        annotations:
          summary: "High error rate detected in logs"
          description: "Service {{ $labels.service }} has error rate of {{ $value }} errors/sec"

      # Alert: Specific error pattern detected
      - alert: FeatureNotFoundErrors
        expr: |
          sum(rate({service="inference-gateway"} |= "FeatureNotFound" [5m])) > 0.1
        for: 2m
        labels:
          severity: critical
          source: loki
        annotations:
          summary: "FeatureNotFound errors detected"
          description: "Feature store is returning NotFound errors at {{ $value }} errors/sec"

      # Alert: High latency from logs
      - alert: HighLatencyFromLogs
        expr: |
          log:latency:p99:5m{service="inference-gateway"} > 500
        for: 10m
        labels:
          severity: warning
          source: loki
        annotations:
          summary: "P99 latency exceeds 500ms (from logs)"
          description: "Model {{ $labels.model_version }} P99 latency is {{ $value }}ms"

      # Alert: Log volume spike
      - alert: LogVolumeSpikeDetected
        expr: |
          (
            sum(rate({service="inference-gateway"}[5m]))
            /
            sum(rate({service="inference-gateway"}[5m] offset 1h))
          ) > 5
        for: 5m
        labels:
          severity: warning
          source: loki
        annotations:
          summary: "Log volume increased 5x compared to 1h ago"
          description: "Investigate potential issue causing excessive logging"
```

**Add rules to Loki container:**

Update `docker-compose.logging.yml`:

```yaml
services:
  loki:
    volumes:
      - ./loki/loki-config.yaml:/etc/loki/loki-config.yaml:ro
      - ./loki/loki-rules.yaml:/loki/rules/rules.yaml:ro  # Add this line
      - loki-data:/loki
```

### 7.2 Create Grafana Alert for Log Patterns

**Navigate to Grafana → Alerting → Alert rules → New alert rule**

**Alert Name:** Critical Errors in Logs

**Query A (Loki):**
```logql
sum(rate({service="inference-gateway", level=~"error|critical"}[5m])) * 60
```

**Condition:** B (Reduce)
- Function: Last
- Input: A
- Mode: Strict

**Condition:** C (Threshold)
- Input: B
- IS ABOVE: 10

**Evaluate every:** 1m
**For:** 5m

**Labels:**
- severity: critical
- team: ml-platform
- source: loki-logs

**Annotations:**
- summary: "Critical error rate from logs exceeds 10 errors/min"
- description: "Check logs with: {service=\"inference-gateway\", level=~\"error|critical\"}"
- runbook_url: "https://wiki.example.com/runbooks/high-error-rate"

**Notification Policy:** Route to `slack-critical` contact point

---

## Part 8: Correlation with Traces

### 8.1 Configure Trace-Log Linking

Update Loki datasource to support trace correlation:

**Edit `grafana/provisioning/datasources/loki.yml`:**

```yaml
apiVersion: 1

datasources:
  - name: Loki
    type: loki
    access: proxy
    url: http://loki:3100
    isDefault: false
    jsonData:
      maxLines: 1000

      # Link to Tempo traces via trace_id
      derivedFields:
        - datasourceUid: tempo
          matcherRegex: '"trace_id":\s*"(\w+)"'
          name: TraceID
          url: "$${__value.raw}"

        # Alternative: trace_id as top-level field
        - datasourceUid: tempo
          matcherRegex: 'trace_id=(\w+)'
          name: trace_id
          url: "$${__value.raw}"
```

### 8.2 Test Trace-Log Correlation

**Workflow:**

1. **Start from Metric Alert:**
   - High latency spike at 14:32 UTC
   - Click on metric panel in Grafana

2. **View Exemplar (Trace):**
   - Click on exemplar point (dot on graph)
   - Opens trace in Tempo

3. **From Trace to Logs:**
   - In trace view, click "Logs for this span"
   - Filters: `{service="inference-gateway"} | json | trace_id="<trace_id>"`

4. **See Correlated Logs:**
   ```
   14:32:15.123 [INFO] Request started trace_id=abc123
   14:32:15.456 [INFO] Feature store lookup trace_id=abc123
   14:32:16.234 [ERROR] Feature not found trace_id=abc123
   14:32:16.789 [ERROR] Prediction failed trace_id=abc123
   ```

**Create documentation in `logging/docs/log-trace-correlation.md`:**

```markdown
# Log-Trace Correlation Workflow

## Scenario: Debugging High Latency

### Step 1: Detect Issue in Metrics
- **Dashboard:** Inference Gateway - Service Dashboard
- **Panel:** P99 Latency
- **Alert:** P99 latency > 300ms for 10 minutes

### Step 2: Find Example Request
- Click on latency spike in timeseries graph
- Click on exemplar (data point with trace)
- Trace ID: `a1b2c3d4e5f6g7h8i9j0`

### Step 3: View Trace in Tempo
- Trace shows 2.5s total duration
- Span breakdown:
  - HTTP request: 2.5s
  - Feature store lookup: 2.2s ← **SLOW**
  - Model inference: 0.2s
  - Response: 0.1s

### Step 4: Find Related Logs
- Click "Logs for this span" in Tempo
- LogQL query auto-populated:
  ```logql
  {service="inference-gateway"} | json | trace_id="a1b2c3d4e5f6g7h8i9j0"
  ```

### Step 5: Analyze Logs
Logs reveal root cause:
```
14:32:15.123 [INFO] GET /api/v1/predict trace_id=a1b2c3d4
14:32:15.456 [INFO] Looking up features for user_id=12345
14:32:16.234 [WARN] Feature store connection timeout (attempt 1)
14:32:17.456 [WARN] Feature store connection timeout (attempt 2)
14:32:17.678 [ERROR] Feature store unavailable, using cached features
14:32:17.789 [INFO] Model prediction completed
14:32:17.890 [INFO] Response sent with degraded features flag
```

**Root Cause:** Feature store connection timeouts (2x retries = 2.2s delay)

### Step 6: Verify Fix
After increasing feature store timeout and adding circuit breaker:
- P99 latency drops to 150ms
- No more timeout errors in logs
- Traces show < 100ms feature lookups
```

---

## Part 9: Compliance and Governance

### 9.1 PII Redaction

Already configured in Promtail pipeline (Part 2.3):

```yaml
# Stage 5: Redact PII
- replace:
    expression: '(?P<email>[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
    replace: '***REDACTED_EMAIL***'

- replace:
    expression: '"user_id":\s*"([^"]+)"'
    replace: '"user_id":"***REDACTED***"'
```

**Test redaction:**

```bash
# Generate log with PII
echo '{"level":"info","message":"User test@example.com logged in","user_id":"12345"}' | \
  docker exec -i promtail /usr/bin/promtail \
    -config.file=/etc/promtail/config.yaml \
    -stdin

# Query logs - should see redacted version
# {"level":"info","message":"User ***REDACTED_EMAIL*** logged in","user_id":"***REDACTED***"}
```

### 9.2 Access Control

**Create Grafana team with restricted access:**

```bash
# Create team
curl -X POST http://admin:admin@localhost:3000/api/teams \
  -H "Content-Type: application/json" \
  -d '{
    "name": "On-Call Team",
    "email": "oncall@example.com"
  }'

# Create folder for sensitive logs
curl -X POST http://admin:admin@localhost:3000/api/folders \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Production Logs",
    "uid": "prod-logs"
  }'

# Set folder permissions (only on-call team)
curl -X POST http://admin:admin@localhost:3000/api/folders/prod-logs/permissions \
  -H "Content-Type: application/json" \
  -d '{
    "items": [
      {"teamId": 2, "permission": 2}  # Team ID 2 = On-Call, Permission 2 = View
    ]
  }'
```

### 9.3 Retention and Lifecycle

**Document in `logging/docs/logging-governance.md`:**

```markdown
# Logging Governance Policy

## Retention Schedule

| Log Type | Hot Storage (Loki) | Warm Storage (S3) | Cold Storage (Glacier) | Total Retention |
|----------|-------------------|-------------------|------------------------|-----------------|
| Application Logs | 7 days | 23 days | - | 30 days |
| Access Logs | 7 days | 83 days | - | 90 days |
| Audit Logs | 7 days | 53 days | 305 days | 365 days |
| Debug Logs | 3 days | - | - | 3 days |

## Data Classification

### Public (P0)
- System metrics
- Health check logs
- **Retention:** 30 days

### Internal (P1)
- Application logs (without PII)
- Performance logs
- **Retention:** 30 days

### Confidential (P2)
- User activity logs (redacted)
- Model prediction logs
- **Retention:** 90 days

### Restricted (P3)
- Authentication logs
- Authorization decisions
- Admin actions
- **Retention:** 365 days

## Access Control

| Role | Access Level | Allowed Actions |
|------|-------------|-----------------|
| Developer | Read | Query logs for their services only |
| SRE On-Call | Read + Export | Query all logs, export for debugging |
| Security Team | Read + Export + Delete | Full access, compliance investigations |
| Auditor | Read-only (Restricted) | Audit log access only |

## Compliance Requirements

### GDPR (EU users)
- **Right to be forgotten:** Delete logs containing user_id on request
- **Data minimization:** Redact PII in logs
- **Retention limits:** Max 90 days for user activity logs

### SOC 2
- **Audit logging:** Track all log queries and exports
- **Access control:** Role-based permissions enforced
- **Encryption:** Logs encrypted at rest and in transit

### HIPAA (if handling health data)
- **BAA required:** Business Associate Agreement with cloud provider
- **Encryption:** AES-256 for stored logs
- **Audit trail:** Log all access to patient data logs

## Audit Trail

All log queries must be tracked:

```logql
# Query audit logs from Loki
{service="grafana", logger="auditing"}
  | json
  | event="query_logs"
  | line_format "User={{.user}} queried {{.datasource}} at {{.timestamp}}"
```

## Disaster Recovery

- **Backup frequency:** Daily snapshots of Loki indexes
- **Backup retention:** 7 days of backups
- **Recovery time objective (RTO):** 4 hours
- **Recovery point objective (RPO):** 24 hours

**Backup script:**
```bash
#!/bin/bash
# backup-loki.sh
BACKUP_DIR=/backups/loki
DATE=$(date +%Y%m%d)

# Backup Loki data
docker exec loki tar czf /tmp/loki-backup-$DATE.tar.gz /loki
docker cp loki:/tmp/loki-backup-$DATE.tar.gz $BACKUP_DIR/

# Upload to S3
aws s3 cp $BACKUP_DIR/loki-backup-$DATE.tar.gz s3://backups/loki/

# Cleanup old backups (keep 7 days)
find $BACKUP_DIR -name "loki-backup-*.tar.gz" -mtime +7 -delete
```
```

---

## Part 10: Performance Optimization

### 10.1 Reduce Cardinality

**Problem:** Too many unique label combinations slow down Loki.

**Check current cardinality:**
```bash
# Query Loki metrics
curl http://localhost:3100/metrics | grep loki_ingester_streams

# Output: loki_ingester_streams 5234  ← Too high!
```

**Solution: Limit labels to low-cardinality fields**

**Bad (high cardinality):**
```yaml
# DON'T DO THIS
- labels:
    trace_id:      # Millions of unique values
    request_id:    # Unique per request
    user_id:       # Thousands of users
```

**Good (low cardinality):**
```yaml
# DO THIS
- labels:
    service:       # ~10 values
    environment:   # 3 values (lab, staging, prod)
    level:         # 5 values (debug, info, warning, error, critical)
    cluster:       # ~5 values
```

**Use structured metadata for high-cardinality fields** (Loki 2.9+):

```yaml
pipeline_stages:
  - json:
      expressions:
        trace_id: trace_id
        user_id: user_id

  # Don't promote to labels - keep as structured metadata
  - structured_metadata:
      trace_id:
      user_id:
```

### 10.2 Query Optimization

**Slow query (scans all logs):**
```logql
{service="inference-gateway"} |= "error"
```

**Fast query (uses label index):**
```logql
{service="inference-gateway", level="error"}
```

**Query performance tips:**

1. **Always use label matchers:** `{service="x", level="y"}`
2. **Limit time range:** `[5m]` instead of `[24h]`
3. **Use `|=` for simple string matching** before `| json`
4. **Avoid regex when possible:** `|=` faster than `|~`
5. **Use `--limit` flag** to cap results

### 10.3 Index and Storage Tuning

**Loki configuration optimizations:**

```yaml
# In loki-config.yaml
ingester:
  # Increase chunk size for better compression
  chunk_target_size: 1572864  # 1.5 MB (default: 1 MB)

  # Reduce flush frequency for fewer chunks
  chunk_idle_period: 2h  # (default: 1h)

storage_config:
  boltdb_shipper:
    # Build index cache faster
    index_cache_validity: 1h

    # Compact more frequently
    compactor:
      compaction_interval: 5m  # (default: 10m)

# Increase query parallelism
querier:
  max_concurrent: 20  # (default: 10)

# Cache more results
query_range:
  results_cache:
    cache:
      embedded_cache:
        max_size_mb: 500  # (default: 100)
```

### 10.4 Monitoring Loki Performance

**Add Loki metrics to Prometheus:**

**Edit `prometheus/prometheus.yml`:**
```yaml
scrape_configs:
  - job_name: 'loki'
    static_configs:
      - targets: ['loki:3100']
        labels:
          service: loki
```

**Key Loki metrics to watch:**

```promql
# Ingestion rate
rate(loki_distributor_bytes_received_total[5m])

# Number of streams (cardinality)
loki_ingester_streams

# Query latency
histogram_quantile(0.99, rate(loki_request_duration_seconds_bucket[5m]))

# Failed queries
rate(loki_logql_querystats_total{status="failed"}[5m])

# Chunk utilization
loki_ingester_chunk_utilization
```

---

## Part 11: Validation and Testing

### 11.1 Validation Checklist

**Run these checks to verify logging pipeline:**

```bash
#!/bin/bash
# validate-logging.sh

echo "=== Loki Health Check ==="
curl -s http://localhost:3100/ready
echo ""

echo "=== Promtail Health Check ==="
curl -s http://localhost:9080/ready
echo ""

echo "=== Check Loki Ingestion ==="
curl -s http://localhost:3100/metrics | grep loki_distributor_bytes_received_total
echo ""

echo "=== Check Promtail Sent Logs ==="
curl -s http://localhost:9080/metrics | grep promtail_sent_entries_total
echo ""

echo "=== Check Stream Count (Cardinality) ==="
curl -s http://localhost:3100/metrics | grep loki_ingester_streams
echo ""

echo "=== Query Recent Logs ==="
curl -G -s "http://localhost:3100/loki/api/v1/query_range" \
  --data-urlencode 'query={service="inference-gateway"}' \
  --data-urlencode "start=$(date -u -d '5 minutes ago' +%s)000000000" \
  --data-urlencode "end=$(date -u +%s)000000000" \
  | jq '.data.result | length'
echo " log streams found"

echo "=== Check for Errors ==="
docker-compose -f docker-compose.logging.yml logs --tail=50 loki promtail | grep -i error || echo "No errors found"
```

**Run validation:**
```bash
chmod +x validate-logging.sh
./validate-logging.sh
```

**Expected output:**
```
=== Loki Health Check ===
ready

=== Promtail Health Check ===
ready

=== Check Loki Ingestion ===
loki_distributor_bytes_received_total 523041

=== Check Promtail Sent Logs ===
promtail_sent_entries_total{host="localhost"} 1523

=== Check Stream Count (Cardinality) ===
loki_ingester_streams 12

=== Query Recent Logs ===
5 log streams found

=== Check for Errors ===
No errors found
```

### 11.2 Load Testing

**Generate sustained log volume:**

```python
# load-test-logging.py
import asyncio
import aiohttp
import json
from datetime import datetime
import random

async def generate_request(session, request_id):
    """Simulate inference request (generates logs)"""
    url = "http://localhost:8000/api/v1/predict"

    payload = {
        "image_url": f"https://example.com/image_{request_id}.jpg",
        "model_version": random.choice(["v1.0.0", "v1.1.0", "v1.2.0"])
    }

    try:
        async with session.post(url, json=payload, timeout=5) as response:
            return await response.json()
    except Exception as e:
        print(f"Request {request_id} failed: {e}")

async def load_test(duration_seconds=300, requests_per_second=10):
    """Run load test for specified duration"""
    async with aiohttp.ClientSession() as session:
        request_id = 0
        start_time = datetime.now()

        while (datetime.now() - start_time).seconds < duration_seconds:
            tasks = []
            for _ in range(requests_per_second):
                tasks.append(generate_request(session, request_id))
                request_id += 1

            await asyncio.gather(*tasks)
            await asyncio.sleep(1)

        print(f"Load test complete: {request_id} total requests")

if __name__ == "__main__":
    # 5 minutes, 10 req/sec = 3000 requests
    asyncio.run(load_test(duration_seconds=300, requests_per_second=10))
```

**Run load test:**
```bash
python load-test-logging.py
```

**Monitor during load test:**
```bash
# Watch Loki ingestion rate
watch -n 1 'curl -s http://localhost:3100/metrics | grep loki_distributor_bytes_received_total'

# Watch Promtail shipping rate
watch -n 1 'curl -s http://localhost:9080/metrics | grep promtail_sent_bytes_total'

# Watch Docker logs
docker stats loki promtail
```

---

## Part 12: Troubleshooting Guide

### Common Issues and Solutions

#### Issue 1: Promtail Not Shipping Logs

**Symptoms:**
- `promtail_sent_entries_total` not increasing
- No logs appearing in Grafana Explore

**Debug steps:**
```bash
# Check Promtail logs
docker logs promtail --tail=100

# Check positions file
cat promtail/positions.yaml

# Test Promtail config
docker exec promtail /usr/bin/promtail \
  -config.file=/etc/promtail/config.yaml \
  -dry-run

# Verify Loki reachable
docker exec promtail wget -O- http://loki:3100/ready
```

**Solutions:**
- **No Docker logs found:** Add `logging: promtail` label to containers
- **Permission denied:** Run Promtail with Docker socket access
- **Loki unreachable:** Check network connectivity

#### Issue 2: High Cardinality (Too Many Streams)

**Symptoms:**
- `loki_ingester_streams` > 10,000
- Slow queries
- High memory usage

**Debug:**
```bash
# Check stream count
curl -s http://localhost:3100/metrics | grep loki_ingester_streams

# Query active streams
curl -G -s "http://localhost:3100/loki/api/v1/label" | jq '.data'
```

**Solution:**
Remove high-cardinality labels from Promtail config:
```yaml
# BEFORE (bad)
- labels:
    trace_id:  # ← Remove this!

# AFTER (good)
- labels:
    service:
    level:
```

#### Issue 3: Logs Missing Fields

**Symptoms:**
- Logs appear in Loki but fields not extracted
- JSON parsing errors

**Debug:**
```logql
# Check raw logs
{service="inference-gateway"}

# Check if JSON parsing worked
{service="inference-gateway"} | json
```

**Solution:**
Verify JSON structure matches pipeline config:
```yaml
- json:
    expressions:
      level: level  # ← Must match actual JSON field name
```

#### Issue 4: Out of Disk Space

**Symptoms:**
- `loki_ingester_blocks_per_chunk` increasing
- Disk usage growing rapidly

**Debug:**
```bash
# Check Loki data size
du -sh $(docker volume inspect loki-data --format '{{.Mountpoint}}')

# Check compaction
docker logs loki | grep compactor
```

**Solution:**
Enable retention and compaction:
```yaml
# In loki-config.yaml
compactor:
  retention_enabled: true
  retention_delete_delay: 2h

limits_config:
  retention_period: 168h  # 7 days
```

---

## Part 13: Stretch Goals

### 13.1 Long-Term Storage (S3/GCS)

**Configure Loki to use S3 for chunks:**

```yaml
# In loki-config.yaml
storage_config:
  aws:
    s3: s3://us-east-1/my-loki-bucket
    s3forcepathstyle: false

  boltdb_shipper:
    shared_store: s3

schema_config:
  configs:
    - from: 2024-01-01
      store: boltdb-shipper
      object_store: s3  # Changed from filesystem
      schema: v12
```

**AWS credentials:**
```bash
# In docker-compose.logging.yml
services:
  loki:
    environment:
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
      - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
      - AWS_REGION=us-east-1
```

### 13.2 Multi-Tenancy

**Enable multi-tenancy in Loki:**

```yaml
# In loki-config.yaml
auth_enabled: true  # Enable multi-tenancy
```

**Configure Promtail to send tenant ID:**

```yaml
# In promtail-config.yaml
clients:
  - url: http://loki:3100/loki/api/v1/push
    tenant_id: team-ml-platform  # Set tenant
```

**Query specific tenant:**
```bash
curl -G -s "http://localhost:3100/loki/api/v1/query_range" \
  -H "X-Scope-OrgID: team-ml-platform" \
  --data-urlencode 'query={service="inference-gateway"}'
```

### 13.3 Security Scanning Logs

**Integrate with Falco for security event logs:**

```yaml
# In promtail-config.yaml
scrape_configs:
  - job_name: falco-security
    static_configs:
      - targets: [localhost]
        labels:
          job: security
          __path__: /var/log/falco/*.json

    pipeline_stages:
      - json:
          expressions:
            priority: priority
            rule: rule
            output: output
      - labels:
          priority:
```

---

## Part 14: Documentation and Summary

### 14.1 Update README

**Create `logging/README.md`:**

```markdown
# Logging Pipeline - Inference Gateway

Production-ready centralized logging with Grafana Loki.

## Quick Start

bash
# Start logging stack
docker-compose -f docker-compose.logging.yml up -d

# View logs in Grafana
open http://localhost:3000/explore


## Architecture

- **Loki:** Log aggregation and storage
- **Promtail:** Log collection and shipping
- **Grafana:** Log querying and visualization

## Retention Policy

- Hot storage (Loki): 7 days
- Total retention: 30 days (app logs)

## Useful Queries

bash
# Error logs
{service="inference-gateway", level="error"}

# High latency requests
{service="inference-gateway"} | json | latency_ms > 300

# Logs for specific trace
{service="inference-gateway"} | json | trace_id="abc123"


## Dashboards

- **Logging Overview:** Log volume, error rates, top errors
- **Log Troubleshooting:** Live error stream, search

## Alerts

- High error rate (> 10 errors/min)
- Log volume spike (5x increase)
- Specific error patterns (FeatureNotFound)

## Maintenance

bash
# Check health
./validate-logging.sh

# View Loki metrics
curl http://localhost:3100/metrics

# Backup logs
./backup-loki.sh

```

### 14.2 Create LogQL Reference

**Create `logging/docs/logql-queries.md`** with 20+ example queries.

---

## Validation Checklist

Before completing this exercise, ensure:

- [ ] Loki and Promtail deployed and healthy
- [ ] Logs flowing from inference gateway to Loki
- [ ] JSON logs parsed correctly, fields extracted
- [ ] PII redaction working (emails, user IDs masked)
- [ ] LogQL queries return expected results
- [ ] Logging dashboard shows metrics and live logs
- [ ] Trace-log correlation working (via trace_id)
- [ ] Log-based alerts configured and tested
- [ ] Retention policy configured (7 days)
- [ ] Cardinality < 1,000 streams
- [ ] Documentation complete (architecture, governance, queries)

---

## Summary

You have successfully built a production-ready logging pipeline with:

✅ **Centralized log aggregation** with Loki (2.9.3)
✅ **Automated log collection** with Promtail
✅ **Structured log parsing** with pipeline stages
✅ **PII redaction** for compliance
✅ **Log-based metrics** for alerting
✅ **Trace-log correlation** for debugging
✅ **Grafana dashboards** for visualization
✅ **Retention and governance** policies
✅ **Performance optimization** (cardinality, caching)
✅ **Comprehensive documentation**

**Total line count:** ~2,400 lines
**Key files created:** 8+
**Dashboards:** 2
**Alerts:** 4

---

## Next Steps

**In Exercise 05** (Alerting & Incident Response), you will:
- Build comprehensive alerting rules across metrics and logs
- Create incident response workflows and runbooks
- Implement on-call rotation and escalation policies
- Set up alert fatigue mitigation strategies
- Build incident postmortem templates

**Continue to Exercise 05:** [Alerting & Incident Response](./exercise-05-alerting-incident-response.md)
