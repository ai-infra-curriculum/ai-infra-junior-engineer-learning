# Prometheus + PromQL Cheat Sheet

Quick reference for Prometheus scrape configs and PromQL queries. Assumes you've completed Module 009.

## Mental Model

- Prometheus **scrapes** HTTP `/metrics` endpoints at a fixed interval.
- Each scrape yields **time-series samples**: `metric_name{label="value", ...} value @ timestamp`.
- PromQL is a query language over those time-series.
- Alertmanager handles routing, deduping, and silencing.

## Metric Types

| Type | When to use | Example |
|---|---|---|
| **Counter** | Monotonically increasing (resets to 0 on restart). Use `rate()` to query. | `http_requests_total` |
| **Gauge** | Goes up and down (current value). | `cpu_usage_seconds`, `memory_bytes` |
| **Histogram** | Distribution. Yields `_bucket`, `_sum`, `_count`. Use `histogram_quantile()`. | `http_request_duration_seconds` |
| **Summary** | Pre-computed quantiles. Cannot aggregate across instances. Prefer histogram. | `request_latency_seconds{quantile="0.95"}` |

## Instrumenting (Python)

```python
from prometheus_client import Counter, Gauge, Histogram, start_http_server

REQUESTS = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status"],
)
INFLIGHT = Gauge("inflight_requests", "Inflight requests")
LATENCY = Histogram(
    "http_request_duration_seconds",
    "Request latency",
    ["path"],
    buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0),
)

start_http_server(8000)  # serves /metrics

INFLIGHT.inc()
with LATENCY.labels(path="/predict").time():
    ...
REQUESTS.labels(method="POST", path="/predict", status="200").inc()
INFLIGHT.dec()
```

## Scrape Config (prometheus.yml)

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    cluster: ml-prod
    region: us-west-2

scrape_configs:
  - job_name: model-api
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
        action: keep
        regex: "true"
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
        action: replace
        target_label: __metrics_path__
        regex: (.+)
      - source_labels: [__address__, __meta_kubernetes_pod_annotation_prometheus_io_port]
        action: replace
        regex: ([^:]+)(?::\d+)?;(\d+)
        replacement: $1:$2
        target_label: __address__
      - source_labels: [__meta_kubernetes_namespace]
        target_label: namespace
      - source_labels: [__meta_kubernetes_pod_label_app_kubernetes_io_name]
        target_label: service

rule_files:
  - /etc/prometheus/rules/*.yml

alerting:
  alertmanagers:
    - static_configs:
        - targets: [alertmanager:9093]
```

## PromQL — Selectors

```promql
# Latest value of a metric across all series
http_requests_total

# Single label match
http_requests_total{status="200"}

# Multiple labels, regex
http_requests_total{status=~"2..", method!="OPTIONS"}

# Negative match
http_requests_total{status!~"2.."}

# Range vector: last 5 minutes of samples
http_requests_total[5m]

# Offset (time-shift)
http_requests_total offset 1h
```

## PromQL — Rates and Increases

```promql
# Per-second rate over the last 5 minutes (works on counters)
rate(http_requests_total[5m])

# irate: instantaneous rate, uses last two samples — for graphs of bursty signals
irate(http_requests_total[5m])

# Increase (raw delta) over 1 hour
increase(http_requests_total[1h])

# Resets-handled correctly automatically.
```

**Rule of thumb:** if you `sum()` a counter, you almost always meant `sum(rate(...))`.

## PromQL — Aggregation

```promql
# Total RPS across all instances
sum(rate(http_requests_total[5m]))

# Group by label
sum by (status) (rate(http_requests_total[5m]))
sum by (path, status) (rate(http_requests_total[5m]))

# Topk
topk(5, sum by (path) (rate(http_requests_total[5m])))

# Average across instances
avg(rate(node_cpu_seconds_total[2m]))

# Standard deviation
stddev(rate(http_request_duration_seconds_sum[5m]))
```

## PromQL — Histogram Quantiles

```promql
# p95 latency
histogram_quantile(0.95,
    sum by (le) (rate(http_request_duration_seconds_bucket[5m]))
)

# p95 by path
histogram_quantile(0.95,
    sum by (path, le) (rate(http_request_duration_seconds_bucket[5m]))
)
```

Always wrap the bucket sum with `sum by (..., le)` BEFORE `histogram_quantile`.

## PromQL — Common Patterns

```promql
# Error rate (%)
100 * sum(rate(http_requests_total{status=~"5.."}[5m]))
    /
sum(rate(http_requests_total[5m]))

# Saturation: pods near CPU limit
sum by (pod) (
    rate(container_cpu_usage_seconds_total[2m])
) / sum by (pod) (
    kube_pod_container_resource_limits{resource="cpu"}
)

# Time-to-restart (last 24h)
changes(kube_pod_container_status_restarts_total[24h])

# Pod up?
up{job="model-api"}

# Service "available" replicas vs desired
kube_deployment_status_replicas_available{deployment="model-api"}
  /
kube_deployment_spec_replicas{deployment="model-api"}

# Filter by threshold (used as alert expression)
sum(rate(http_requests_total{status=~"5.."}[5m]))
  /
sum(rate(http_requests_total[5m])) > 0.05
```

## Recording Rules

Pre-compute expensive expressions for dashboards:

```yaml
groups:
  - name: model-api-recording
    interval: 30s
    rules:
      - record: model_api:request_rate:rate5m
        expr: sum by (status) (rate(http_requests_total{job="model-api"}[5m]))

      - record: model_api:latency_p95:5m
        expr: histogram_quantile(0.95,
              sum by (le) (rate(http_request_duration_seconds_bucket{job="model-api"}[5m])))
```

## Alerting Rules

```yaml
groups:
  - name: model-api-alerts
    rules:
      - alert: HighErrorRate
        expr: |
          sum(rate(http_requests_total{job="model-api",status=~"5.."}[5m]))
          /
          sum(rate(http_requests_total{job="model-api"}[5m]))
          > 0.05
        for: 5m
        labels:
          severity: critical
          service: model-api
        annotations:
          summary: "5xx error rate > 5%"
          description: "Error rate is {{ $value | humanizePercentage }} for 5 minutes."
          runbook_url: "https://runbooks/model-api/high-error-rate"
          dashboard_url: "https://grafana/d/model-api"
```

Key fields:
- `expr` — the PromQL that must be true to fire.
- `for` — how long the expression must be true before alerting (de-noising).
- `labels` — used by Alertmanager for routing.
- `annotations` — human-readable, supports template variables.

## Common Gotchas

- **Counters reset on restart.** Use `rate()` / `increase()` which handle resets, not raw differences.
- **`rate()` requires at least 2 samples in range.** If your scrape interval is 30s, `rate(...[30s])` may return nothing — use `[1m]` or longer.
- **Histogram quantiles aren't linearly interpolated.** They estimate via bucket boundaries; quantile accuracy depends on bucket layout. Choose buckets near your SLO.
- **Summary metrics can't be aggregated** across instances. Use histograms for anything you want to aggregate.
- **High-cardinality labels** (user_id, request_id) blow up Prometheus. Never label by per-user fields.
- **Labels are time-series identifiers.** Adding/removing a label creates new series and confuses dashboards.

## Useful Tools

| Tool | Purpose |
|---|---|
| `promtool` | Validate config, lint rules, run queries |
| `promtool check rules /etc/prometheus/rules/*.yml` | CI gate |
| `promtool check config prometheus.yml` | CI gate |
| `prometheus-flask-exporter`, `prometheus-fastapi-instrumentator` | Auto-instrument Python web apps |
| `node_exporter`, `kube-state-metrics` | Standard infra exporters |
| `cardinality` query: `sum(scrape_series_added)` | Find runaway cardinality |

## See Also

- PromQL docs: https://prometheus.io/docs/prometheus/latest/querying/basics/
- Best-practice labels: https://prometheus.io/docs/practices/naming/
- Alertmanager routing: https://prometheus.io/docs/alerting/latest/configuration/
