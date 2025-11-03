# Lecture 02: Prometheus Metrics Pipeline for AI Infrastructure

## Lecture Overview
Prometheus has become the de facto standard for metrics collection in cloud-native environments. This lecture explains how to design, deploy, and operate a Prometheus-based metrics stack tailored to AI infrastructure workloads. You will learn the Prometheus data model, configuration patterns, exporter ecosystem, PromQL query design, and strategies for scaling the pipeline in production.

**Estimated Reading Time:** 75–90 minutes
**Hands-on Companion Lab:** Exercise 02 – Prometheus Setup & Exporters
**Prerequisite Knowledge:** Lecture 01 (observability foundations), Docker basics, familiarity with Linux services.

### Learning Objectives

By the end of this lecture, you will:
- Understand Prometheus architecture and core components
- Configure Prometheus for AI infrastructure monitoring
- Implement service discovery patterns for Kubernetes environments
- Write PromQL queries to extract meaningful metrics
- Deploy and configure exporters for ML workloads
- Apply relabeling strategies to optimize metric collection
- Design Prometheus deployments for production scalability

---

## 1. Prometheus Architecture Deep Dive

### 1.1 Core Components
- **Prometheus Server:** Scrapes targets, stores time-series data, runs PromQL queries, triggers alerts.
- **Exporters:** Processes that expose metrics over HTTP in the Prometheus exposition format.
- **Pushgateway:** Buffer for ephemeral/short-lived jobs (use sparingly).
- **Alertmanager:** Manages alert routing, deduplication, and notification.
- **Service Discovery:** Mechanism for discovering scrape targets (Kubernetes API, Consul, file-based, EC2, etc.).

### 1.2 Pull vs Push Model
- Prometheus **pulls** metrics from targets on a configured interval, simplifying auth and lifecycle management.
- Pushgateway acts as a bridge for batch jobs that cannot be scraped. Avoid using it for long-lived services.

### 1.3 Data Flow
1. Target exposes metrics via HTTP endpoint (default `/metrics`).
2. Prometheus scrapes the endpoint at a configured interval (`scrape_interval`).
3. Samples stored in a custom time-series database (TSDB) with retention policy (default 15 days).
4. Recording rules aggregate/transform metrics into new series.
5. PromQL queries fetch data for dashboards, alerts, and automation.

### 1.4 Storage Internals
- TSDB organizes data in 2-hour blocks (~128 MB each).
- Samples stored as chunks; uses write-ahead log (WAL) for durability.
- Compaction merges blocks and applies retention policy.
- High cardinality (many unique combination of metric name + labels) inflates memory usage and query time.

---

## 2. Installing and Configuring Prometheus

### 2.1 Quickstart with Docker Compose
Create a minimal stack for local experimentation:
```yaml
# docker-compose.prometheus.yml
version: "3.8"

services:
  prometheus:
    image: prom/prometheus:v2.51.0
    container_name: prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus-data:/prometheus
    command:
      - "--config.file=/etc/prometheus/prometheus.yml"
      - "--storage.tsdb.retention.time=15d"
      - "--web.enable-lifecycle"

volumes:
  prometheus-data:
```
Run `docker compose -f docker-compose.prometheus.yml up -d`.

### 2.2 Configuration File Anatomy (`prometheus.yml`)
```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 30s
  scrape_timeout: 10s

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'node_exporter'
    static_configs:
      - targets: ['node-exporter:9100']
```

**Key sections:**
- `global`: defaults for scrape frequency and rule evaluation.
- `scrape_configs`: list of jobs to scrape.
- `static_configs`: static target lists; in production use service discovery (e.g., Kubernetes).
- `relabel_configs`: modify labels or drop targets at scrape time.

### 2.3 Service Discovery Patterns
- **Kubernetes:** Use `kubernetes_sd_configs` to discover pods, services, or endpoints. Apply relabeling to select desired targets.
- **Files:** `file_sd_configs` reads JSON/YAML files listing targets; integrate with deployment tooling.
- **Cloud Providers:** Use EC2, Azure, or GCE discovery to auto-register instances.

**Example: Kubernetes Pod Scrape**
```yaml
scrape_configs:
  - job_name: 'kubernetes-pods'
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
        action: keep
        regex: true
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
        target_label: __metrics_path__
        regex: (.+)
      - source_labels: [__address__, __meta_kubernetes_pod_annotation_prometheus_io_port]
        action: replace
        regex: (.+):(?:\d+);(\d+)
        replacement: ${1}:${2}
        target_label: __address__
```

---

## 3. Exporters for AI Infrastructure

### 3.1 Common Exporters
- **Node Exporter:** Host-level metrics (CPU, memory, disk). Essential baseline.
- **cAdvisor / kube-state-metrics:** Container and Kubernetes metrics.
- **Blackbox Exporter:** Synthetic probe of HTTP/HTTPS/TCP endpoints.
- **DCGM Exporter:** NVIDIA GPU metrics (SM utilization, temperature, ECC errors).
- **Prometheus Python Client:** Instrument custom applications and pipelines.
- **Kafka Exporter, Redis Exporter, Postgres Exporter:** Observe platform dependencies.

### 3.2 Custom Exporter Design
When off-the-shelf exporters are insufficient:
1. Use Prometheus client libraries (Python, Go, Java, Rust).
2. Expose `/metrics` endpoint with relevant metric families (counters, gauges, histograms, summaries).
3. Ensure thread/process safety in metric registration.
4. Limit cardinality (avoid per-request labels).
5. Provide health endpoint and integration tests.

**Python Example:**
```python
from prometheus_client import start_http_server, Gauge
import random
import time

GPU_MEM_UTIL = Gauge(
    "gpu_memory_utilization",
    "Percentage of GPU memory used",
    ["gpu_id", "model_name"]
)

def collect_metrics():
    while True:
        for gpu in range(4):
            GPU_MEM_UTIL.labels(gpu_id=gpu, model_name="vision-transformer").set(random.uniform(20, 90))
        time.sleep(10)

if __name__ == "__main__":
    start_http_server(8000)
    collect_metrics()
```

### 3.3 Exporter Configuration Best Practices
- Run exporters as sidecars for per-pod metrics or DaemonSets for node-level metrics.
- Use TLS/Basic auth for scraping endpoints over untrusted networks.
- Monitor exporter health (uptime, scrape failures).
- Document version compatibility (e.g., DCGM exporter + driver versions).

---

## 4. PromQL Essentials

### 4.1 Data Model Recap
- Metrics identified by **metric name** + set of **label key/value pairs**.
- **Sample:** (`metric_name{label1="value1", ...}`, timestamp, value).
- Vector types: instant vector (samples at single time), range vector (samples over duration).

### 4.2 Querying Basics
- Instant query: `http_requests_total{job="api", status="500"}`
- Range query: `rate(http_requests_total{job="api"}[5m])`
- Aggregation: `sum(rate(http_requests_total[5m])) by (status)`
- Filtering with regex: `{pod=~"ml-inference-.*"}`

### 4.3 Functions You Must Know
- `rate()` / `irate()` – per-second rate for counters.
- `increase()` – total increase over range (useful for counts).
- `avg_over_time()`, `max_over_time()` – detect trends.
- `histogram_quantile()` – compute quantiles from histogram buckets.
- `sum by(...)`, `avg without(...)` – grouping modifiers.
- `label_replace()` – manipulate labels on the fly.

### 4.4 Example Queries for AI Workloads
**GPU Utilization:**
```promql
avg by (cluster, gpu) (DCGM_FI_DEV_GPU_UTIL)
```

**Batch Inference Throughput:**
```promql
rate(ai_infra_batch_predictions_total{job="batch-runner"}[10m])
```

**Error Budget Burn Rate (SLO 99% latency < 300 ms):**
```promql
(1 - sum(rate(ai_infra_inference_latency_seconds_bucket{le="0.3"}[1m])) /
     sum(rate(ai_infra_inference_latency_seconds_count[1m])))
    / (1 - 0.99)
```

**Data Pipeline Backlog:**
```promql
max by (pipeline) (ai_infra_pipeline_queue_length{pipeline=~"feature-.*"})
```

### 4.5 Recording Rules
- Pre-compute expensive queries or standardize SLO calculations.
- Store rules in `rules/*.yml` and reference via `rule_files` in `prometheus.yml`.

Example:
```yaml
groups:
  - name: inference_slo.rules
    interval: 30s
    rules:
      - record: slo:inference_latency:ratio
        expr: |
          sum(rate(ai_infra_inference_latency_seconds_bucket{le="0.3"}[5m])) /
          sum(rate(ai_infra_inference_latency_seconds_count[5m]))
      - record: slo:inference_latency:burn_rate
        expr: (1 - slo:inference_latency:ratio) / (1 - 0.99)
```

Benefits:
- Reduces dashboard load times.
- Ensures consistent calculations across dashboards, alerts.

---

## 5. Alerting with Prometheus and Alertmanager

### 5.1 Alerting Rules
Define alerting expressions using PromQL.

```yaml
groups:
  - name: inference_alerts.rules
    rules:
      - alert: InferenceLatencyHigh
        expr: slo:inference_latency:burn_rate{cluster="prod"} > 2
        for: 10m
        labels:
          severity: page
        annotations:
          summary: "Inference latency SLO burn rate high in {{ $labels.cluster }}"
          description: "Burn rate {{ $value }} exceeds threshold. Check runbook go/inference-latency."
```

### 5.2 Alertmanager Configuration
- Handles deduplication, grouping, routing to receivers (PagerDuty, Slack, email).
```yaml
route:
  receiver: pagerduty-prod
  group_by: ['alertname', 'cluster']
  routes:
    - matchers:
        severity = 'page'
      receiver: pagerduty-prod
    - matchers:
        severity = 'ticket'
      receiver: jira-triage

receivers:
  - name: pagerduty-prod
    pagerduty_configs:
      - routing_key: ${PAGERDUTY_KEY}
```

### 5.3 Alert Hygiene
- Add `for` clause to avoid transient spikes.
- Include links to Grafana dashboards, runbooks, and trace search.
- Test alerts in staging using simulated metrics or test environment.
- Regularly review alert noise; remove or tune false positives.

---

## 6. Scaling Prometheus

### 6.1 Federation
- Lower-tier Prometheus servers scrape workloads in specific regions/clusters.
- Top-level Prometheus federates aggregated metrics (sums, averages).
- Useful for multi-region, multi-team setups.

### 6.2 Sharding & Horizontal Scaling
- Use **Prometheus Operator** or **Cortex/Mimir/Thanos** for horizontal scalability, long-term storage, and high availability.
- **Thanos** adds object-storage backed historical data + query layer across multiple Prometheus instances.
- **Cortex/Mimir** is fully distributed TSDB supporting massive scale.

### 6.3 HA Setup Considerations
- Run Prometheus in pairs (active-active) scraping the same targets; dedup queries in Thanos.
- Ensure Alertmanager runs as a cluster of at least three replicas for consensus.
- Store persistent data on SSD-backed disks; plan backup strategy.

### 6.4 Retention and Storage Management
- Configure `--storage.tsdb.retention.size` or `--storage.tsdb.retention.time`.
- Offload long-term metrics to remote storage (Thanos, Cortex, VictoriaMetrics).
- Monitor cardinality: use `prometheus_tsdb_head_series` and `prometheus_tsdb_head_memory_allocations_bytes`.

---

## 7. Security and Multi-Tenancy

### 7.1 Securing Prometheus
- Restrict access to `/` and `/api` endpoints via reverse proxy, mutual TLS, or OAuth proxy.
- Use RBAC when running in Kubernetes; limit permissions.
- Scrubbing secrets: avoid embedding credentials in labels; use environment variables or secret mounts.

### 7.2 Multi-Tenant Considerations
- Namespaces/label conventions per team (e.g., `team="ml-platform"`).
- Quotas via rate limits on remote write or query concurrency.
- Governance: implement retention policies per team, cost attribution dashboards.

---

## 8. Operational Best Practices

### 8.1 Runbooks
- Document restart procedure, alert triage steps, common query references.
- Provide `kubectl` commands or systemctl instructions for restart.
- Maintain GitOps repository for Prometheus configuration and dashboard JSON.

### 8.2 Observability of Prometheus Itself
- Scrape Prometheus metrics:
  - `prometheus_tsdb_head_samples_appended_total`
  - `prometheus_engine_query_duration_seconds`
  - `prometheus_notifications_dropped_total`
- Set alerts for high scrape failure ratios, query latency, disk usage.

### 8.3 Testing Configuration
- Validate configuration changes with `promtool check config prometheus.yml`.
- Test rules: `promtool test rules rules/*.yml`.
- Use `--web.enable-lifecycle` for safe hot-reloads (`curl -X POST http://localhost:9090/-/reload`).

### 8.4 Change Management
- Store configs and rules in Git.
- Enforce code review and automated linting (Promtool, promql lints).
- Provide staging Prometheus environment mirroring production load.

---

## 9. Prometheus for ML-Specific Metrics

### 9.1 Instrumenting Training Pipelines
- Expose metrics from training jobs: epoch durations, loss, learning rate.
- Use sidecar exporters or embed metrics in training script.
- In distributed training (Horovod, Ray, PyTorch DDP), aggregate metrics centrally.

### 9.2 Monitoring Feature Stores
- Track feature freshness, ingestion latency, row counts per feature table.
- Monitor data quality check counts (success vs failure).

### 9.3 Inference Services
- Capture request latency with histograms (e.g., `inference_latency_seconds`).
- Include labels for model version, model type, region.
- Monitor CPU/GPU utilization, queue length, concurrency.
- Integrate drift detectors by exposing metrics such as PSI (population stability index).

### 9.4 Cost and Efficiency Metrics
- Export cost per request, GPU hours per job, energy consumption.
- Combine with Grafana dashboards for FinOps visibility.

---

## 10. Troubleshooting & Common Pitfalls

### 10.1 High Cardinality
- Avoid labels with unbounded values (user IDs, request IDs).
- Use cardinality analysis tools (`prometheus_tsdb_cardinality`).
- Consider dropping labels via relabeling.

### 10.2 Scrape Failures
- Inspect `up` metric (`up == 0` indicates failure).
- Check network connectivity, TLS certificate expirations.
- Watch for exporter resource starvation; add health probes.

### 10.3 Query Performance
- Use `avg_over_time` or recording rules for long-term calculations.
- Limit `offset` usage; ensure queries span rational windows.
- Monitor Prometheus CPU usage; heavy queries can overload server.

### 10.4 Time Synchronization
- Ensure NTP is enabled across servers; out-of-sync clocks break correlations.

---

## 11. Hands-On Checklist
- [ ] Deploy Prometheus via Docker Compose or Kubernetes manifest.
- [ ] Configure scrape jobs for node exporter, custom service, and application instrumentation.
- [ ] Create recording rule for inference latency SLO.
- [ ] Write promtool unit tests for rules you create.
- [ ] Trigger a sample alert and verify it routes correctly through Alertmanager.
- [ ] Document pipeline architecture with diagram ∕ ascii in README.

---

## 12. Knowledge Check
1. Explain the Prometheus data model and why label cardinality matters.
2. Differentiate between `rate`, `irate`, and `increase` with concrete use cases.
3. Design a PromQL query that surfaces top 5 models by GPU consumption over a 1-hour window.
4. Outline the steps to scrape Prometheus metrics from a Kubernetes pod.
5. Describe two approaches for scaling Prometheus to manage 1 million active series.

---

## 13. Additional Resources
- Prometheus Docs: https://prometheus.io/docs/introduction/overview/
- Robust Perception blog (Julius Volz, Brian Brazil) – deep dives into Prometheus usage.
- “Monitoring Distributed Systems” (Cloud Native Patterns series).
- Thanos and Cortex documentation for horizontally scalable Prometheus.
- NVIDIA DCGM exporter documentation for GPU monitoring.
- PromQL tutorials by Grafana Labs.

---

## 14. Summary
- Prometheus offers a flexible pull-based metrics pipeline ideal for cloud-native AI infrastructure.
- Exporters and service discovery extend coverage across infrastructure, platform, and ML workloads.
- PromQL enables powerful analytics—recording rules and alerting turn those insights into action.
- Scaling strategies (federation, Thanos, Mimir) support large-scale deployments.
- Integrating ML-specific metrics expands observability beyond traditional infrastructure signals.

Next, Lecture 03 will layer Grafana on top of Prometheus to build meaningful dashboards and alert workflows for your AI platform.
