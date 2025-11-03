# Exercise 07: PromQL and Recording Rules for ML Infrastructure

## Overview
Master Prometheus Query Language (PromQL) and implement recording rules to optimize query performance for ML infrastructure monitoring. Learn to write efficient queries, pre-compute complex metrics, and design alert rules that catch issues before they impact users.

**Duration:** 3-4 hours
**Difficulty:** Intermediate to Advanced

## Learning Objectives
By completing this exercise, you will:
- Write effective PromQL queries for ML metrics
- Use rate(), increase(), histogram_quantile() for time-series analysis
- Implement recording rules to pre-compute expensive queries
- Design alert rules with proper thresholds and inhibition
- Optimize Prometheus performance with aggregation
- Monitor ML-specific metrics (inference latency, prediction accuracy, model drift)
- Troubleshoot query performance issues

## Prerequisites
- Prometheus installed (see Exercise 01)
- Basic understanding of time-series data
- Kubernetes cluster with metrics (or Docker Compose setup)
- Grafana for visualization (optional but recommended)

## Scenario
You're monitoring an **ML Platform** with multiple model serving APIs. Each model exposes custom metrics:
- `model_prediction_duration_seconds` - Histogram of inference latency
- `model_predictions_total` - Counter of predictions made
- `model_prediction_errors_total` - Counter of prediction errors
- `model_cache_hits_total` / `model_cache_misses_total` - Cache performance
- `model_input_features_count` - Gauge of feature vector size
- `model_memory_usage_bytes` - Gauge of model memory footprint

Users complain about:
- "Slow responses during peak hours"
- "Occasional prediction errors"
- "Dashboard queries timing out"

You'll use PromQL to analyze these metrics, create recording rules for efficiency, and set up alerts for proactive monitoring.

## Tasks

### Task 1: PromQL Fundamentals

**TODO 1.1:** Understanding metric types and instant queries

```promql
# TODO: Instant vector - current value of all metrics matching selector
model_predictions_total

# Filter by labels
model_predictions_total{model="fraud-detector"}

# Multiple label selectors
model_predictions_total{model="fraud-detector", version="v2"}

# Label matching operators
model_predictions_total{model=~"fraud.*"}  # Regex match
model_predictions_total{environment!="dev"}  # Not equal

# Range vector - time series over last 5 minutes
model_predictions_total[5m]

# Offset modifier - query data from 1 hour ago
model_predictions_total offset 1h
```

**TODO 1.2:** Rate and increase functions for counters

```promql
# TODO: Calculate requests per second (rate over 5 min)
rate(model_predictions_total[5m])

# Per-second rate for specific model
rate(model_predictions_total{model="fraud-detector"}[5m])

# Total increase over time period
increase(model_predictions_total[1h])

# Compare to 1 hour ago
increase(model_predictions_total[1h])
  /
increase(model_predictions_total[1h] offset 1h)

# Error rate
rate(model_prediction_errors_total[5m])
  /
rate(model_predictions_total[5m])

# TODO: Practice query
# Calculate the number of predictions in the last hour for each model
# Answer: sum by (model) (increase(model_predictions_total[1h]))
```

**TODO 1.3:** Aggregation operators

```promql
# TODO: Sum across all models
sum(rate(model_predictions_total[5m]))

# Sum by model name (group by model label)
sum by (model) (rate(model_predictions_total[5m]))

# Sum without certain labels (remove namespace label)
sum without (namespace) (rate(model_predictions_total[5m]))

# Average latency across all models
avg(model_prediction_duration_seconds_sum / model_prediction_duration_seconds_count)

# Max memory usage among all models
max(model_memory_usage_bytes)

# Min, max, avg, stddev, count
min by (model) (model_prediction_duration_seconds)
max by (model) (model_prediction_duration_seconds)
avg by (model) (model_prediction_duration_seconds)
stddev by (model) (model_prediction_duration_seconds)
count by (model) (model_predictions_total)

# TODO: Practice query
# Find the model with the highest error rate
# Answer: topk(1, rate(model_prediction_errors_total[5m]) / rate(model_predictions_total[5m]))
```

### Task 2: Advanced PromQL for ML Metrics

**TODO 2.1:** Histogram queries for latency percentiles

```promql
# TODO: Calculate 95th percentile latency
histogram_quantile(0.95,
  sum by (le, model) (
    rate(model_prediction_duration_seconds_bucket[5m])
  )
)

# 50th percentile (median)
histogram_quantile(0.50,
  rate(model_prediction_duration_seconds_bucket[5m])
)

# 99th percentile
histogram_quantile(0.99,
  rate(model_prediction_duration_seconds_bucket[5m])
)

# Multiple percentiles in single panel (for Grafana)
histogram_quantile(0.50, sum(rate(model_prediction_duration_seconds_bucket[5m])) by (le))
or
histogram_quantile(0.95, sum(rate(model_prediction_duration_seconds_bucket[5m])) by (le))
or
histogram_quantile(0.99, sum(rate(model_prediction_duration_seconds_bucket[5m])) by (le))

# Average latency (more efficient than histogram_quantile)
rate(model_prediction_duration_seconds_sum[5m])
  /
rate(model_prediction_duration_seconds_count[5m])
```

**TODO 2.2:** Cache hit ratio and efficiency metrics

```promql
# TODO: Cache hit rate
sum(rate(model_cache_hits_total[5m]))
  /
(
  sum(rate(model_cache_hits_total[5m]))
  +
  sum(rate(model_cache_misses_total[5m]))
)

# Per-model cache hit rate
sum by (model) (rate(model_cache_hits_total[5m]))
  /
sum by (model) (
  rate(model_cache_hits_total[5m]) + rate(model_cache_misses_total[5m])
)

# Identify models with low cache hit rate (< 80%)
(
  sum by (model) (rate(model_cache_hits_total[5m]))
  /
  sum by (model) (
    rate(model_cache_hits_total[5m]) + rate(model_cache_misses_total[5m])
  )
) < 0.8
```

**TODO 2.3:** Request rate patterns and anomaly detection

```promql
# TODO: Hour-over-hour comparison
rate(model_predictions_total[5m])
  /
rate(model_predictions_total[5m] offset 1h)

# Day-over-day comparison (same time yesterday)
rate(model_predictions_total[5m])
  /
rate(model_predictions_total[5m] offset 24h)

# Detect sudden drops (> 50% decrease)
(
  rate(model_predictions_total[5m])
  /
  rate(model_predictions_total[5m] offset 5m)
) < 0.5

# Moving average over last hour
avg_over_time(rate(model_predictions_total[5m])[1h:5m])

# Predict next value (linear regression)
predict_linear(model_predictions_total[1h], 3600)
```

**TODO 2.4:** Resource utilization correlation

```promql
# TODO: Predictions per CPU core
rate(model_predictions_total[5m])
  /
container_cpu_usage_seconds_total

# Memory efficiency (predictions per GB of memory)
rate(model_predictions_total[5m])
  /
(container_memory_usage_bytes / 1024 / 1024 / 1024)

# Identify memory leaks (memory growing over time)
deriv(container_memory_usage_bytes[1h]) > 0

# Correlation between request rate and latency
rate(model_predictions_total[5m])
  and on (model)
histogram_quantile(0.95,
  rate(model_prediction_duration_seconds_bucket[5m])
)
```

### Task 3: Recording Rules for Performance

**TODO 3.1:** Create recording rules file

```yaml
# prometheus-recording-rules.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-recording-rules
  namespace: monitoring
data:
  recording_rules.yml: |
    groups:
    - name: ml_model_serving_rules
      interval: 30s
      rules:

      # Pre-compute request rate per model
      - record: model:predictions:rate5m
        expr: sum by (model, version) (rate(model_predictions_total[5m]))

      # Pre-compute error rate per model
      - record: model:errors:rate5m
        expr: sum by (model, version) (rate(model_prediction_errors_total[5m]))

      # Pre-compute error ratio (percentage)
      - record: model:error_ratio:rate5m
        expr: |
          model:errors:rate5m
            /
          model:predictions:rate5m

      # Pre-compute p50, p95, p99 latencies
      - record: model:latency:p50
        expr: |
          histogram_quantile(0.50,
            sum by (le, model) (
              rate(model_prediction_duration_seconds_bucket[5m])
            )
          )

      - record: model:latency:p95
        expr: |
          histogram_quantile(0.95,
            sum by (le, model) (
              rate(model_prediction_duration_seconds_bucket[5m])
            )
          )

      - record: model:latency:p99
        expr: |
          histogram_quantile(0.99,
            sum by (le, model) (
              rate(model_prediction_duration_seconds_bucket[5m])
            )
          )

      # Average latency (more efficient)
      - record: model:latency:mean
        expr: |
          sum by (model) (rate(model_prediction_duration_seconds_sum[5m]))
            /
          sum by (model) (rate(model_prediction_duration_seconds_count[5m]))

      # Cache hit ratio
      - record: model:cache:hit_ratio
        expr: |
          sum by (model) (rate(model_cache_hits_total[5m]))
            /
          sum by (model) (
            rate(model_cache_hits_total[5m])
            +
            rate(model_cache_misses_total[5m])
          )

      # Total predictions across all models (aggregated)
      - record: platform:predictions:rate5m
        expr: sum(model:predictions:rate5m)

      # Total error rate across platform
      - record: platform:errors:rate5m
        expr: sum(model:errors:rate5m)

      # Platform-wide error ratio
      - record: platform:error_ratio:rate5m
        expr: platform:errors:rate5m / platform:predictions:rate5m

    # Resource efficiency rules
    - name: ml_resource_efficiency_rules
      interval: 60s
      rules:

      # Predictions per CPU second
      - record: model:efficiency:predictions_per_cpu
        expr: |
          model:predictions:rate5m
            /
          sum by (model) (rate(container_cpu_usage_seconds_total[5m]))

      # Predictions per GB of memory
      - record: model:efficiency:predictions_per_gb_memory
        expr: |
          model:predictions:rate5m
            /
          (
            sum by (model) (container_memory_usage_bytes)
            / 1024 / 1024 / 1024
          )

      # Memory usage trend (bytes per hour)
      - record: model:memory:growth_rate_1h
        expr: deriv(container_memory_usage_bytes{container="model-server"}[1h])

    # Business-level KPIs
    - name: ml_business_rules
      interval: 60s
      rules:

      # Daily prediction volume
      - record: model:predictions:daily
        expr: sum by (model) (increase(model_predictions_total[24h]))

      # Cost per 1000 predictions (assuming $0.10 per CPU-hour)
      - record: model:cost:per_1k_predictions
        expr: |
          (
            sum by (model) (rate(container_cpu_usage_seconds_total[5m]))
            * 0.10 / 3600
          )
            /
          (model:predictions:rate5m / 1000)
```

```bash
# TODO: Apply recording rules
kubectl apply -f prometheus-recording-rules.yaml

# Update Prometheus to load recording rules
kubectl edit configmap prometheus-server -n monitoring
# Add:
#   rule_files:
#     - /etc/prometheus/recording_rules.yml

# Reload Prometheus configuration
kubectl rollout restart deployment prometheus-server -n monitoring

# Wait for Prometheus to restart
kubectl wait --for=condition=available deployment/prometheus-server -n monitoring --timeout=120s

# TODO: Verify recording rules are loaded
# Open Prometheus UI and go to Status > Rules
kubectl port-forward -n monitoring svc/prometheus-server 9090:80
# Navigate to http://localhost:9090/rules
```

**TODO 3.2:** Query recording rules (much faster than raw queries)

```promql
# TODO: Use pre-computed metrics instead of raw queries

# Before (expensive):
sum by (model) (rate(model_predictions_total[5m]))

# After (cheap, using recording rule):
model:predictions:rate5m

# Before (very expensive, histogram query):
histogram_quantile(0.95,
  sum by (le, model) (
    rate(model_prediction_duration_seconds_bucket[5m])
  )
)

# After (instant lookup):
model:latency:p95

# Complex dashboard query (instant):
platform:predictions:rate5m
# vs dozens of raw queries
```

**TODO 3.3:** Measure query performance improvement

```bash
# TODO: Benchmark query performance
cat > benchmark_queries.sh << 'EOF'
#!/bin/bash
# Benchmark PromQL query performance

PROM_URL="http://localhost:9090"

echo "=== PromQL Query Performance Benchmark ==="

# Test 1: Raw query
echo -e "\n[Test 1] Raw query (no recording rule):"
time curl -s "$PROM_URL/api/v1/query" \
  --data-urlencode 'query=sum by (model) (rate(model_predictions_total[5m]))' \
  > /dev/null

# Test 2: Recording rule query
echo -e "\n[Test 2] Recording rule query:"
time curl -s "$PROM_URL/api/v1/query" \
  --data-urlencode 'query=model:predictions:rate5m' \
  > /dev/null

# Test 3: Complex histogram query (raw)
echo -e "\n[Test 3] Complex histogram query (raw):"
time curl -s "$PROM_URL/api/v1/query" \
  --data-urlencode 'query=histogram_quantile(0.95, sum by (le, model) (rate(model_prediction_duration_seconds_bucket[5m])))' \
  > /dev/null

# Test 4: Pre-computed percentile
echo -e "\n[Test 4] Pre-computed percentile:"
time curl -s "$PROM_URL/api/v1/query" \
  --data-urlencode 'query=model:latency:p95' \
  > /dev/null

echo -e "\n=== Benchmark Complete ==="
echo "Recording rules should be 5-10x faster for complex queries"
EOF

chmod +x benchmark_queries.sh

# TODO: Run benchmark
# ./benchmark_queries.sh
```

### Task 4: Alert Rules with Proper Thresholds

**TODO 4.1:** Create alert rules for ML platform

```yaml
# prometheus-alert-rules.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-alert-rules
  namespace: monitoring
data:
  alert_rules.yml: |
    groups:
    - name: ml_model_alerts
      interval: 30s
      rules:

      # High error rate alert
      - alert: ModelHighErrorRate
        expr: model:error_ratio:rate5m > 0.05  # > 5% errors
        for: 5m
        labels:
          severity: warning
          component: model-serving
        annotations:
          summary: "High error rate for model {{ $labels.model }}"
          description: "Model {{ $labels.model }} has error rate of {{ $value | humanizePercentage }} (threshold: 5%)"
          dashboard: "http://grafana/d/model-health?var-model={{ $labels.model }}"

      # Critical error rate
      - alert: ModelCriticalErrorRate
        expr: model:error_ratio:rate5m > 0.20  # > 20% errors
        for: 2m
        labels:
          severity: critical
          component: model-serving
          page: "true"  # Page on-call engineer
        annotations:
          summary: "CRITICAL: Model {{ $labels.model }} failing"
          description: "Model {{ $labels.model }} has error rate of {{ $value | humanizePercentage }}. Immediate action required!"
          runbook: "https://wiki/runbooks/model-high-errors"

      # High latency alert (p95 > 500ms)
      - alert: ModelHighLatency
        expr: model:latency:p95 > 0.5
        for: 10m
        labels:
          severity: warning
          component: model-serving
        annotations:
          summary: "High latency for model {{ $labels.model }}"
          description: "Model {{ $labels.model }} p95 latency is {{ $value | humanizeDuration }}"

      # Request rate dropped significantly
      - alert: ModelLowTraffic
        expr: |
          (
            model:predictions:rate5m
              /
            (model:predictions:rate5m offset 1h)
          ) < 0.5
          and
          model:predictions:rate5m offset 1h > 10  # Only if was previously active
        for: 15m
        labels:
          severity: warning
          component: model-serving
        annotations:
          summary: "Traffic dropped for model {{ $labels.model }}"
          description: "Model {{ $labels.model }} traffic is 50% lower than 1 hour ago"

      # No predictions (model down)
      - alert: ModelNoPredictions
        expr: model:predictions:rate5m == 0
        for: 5m
        labels:
          severity: critical
          component: model-serving
          page: "true"
        annotations:
          summary: "Model {{ $labels.model }} is not serving predictions"
          description: "No predictions from model {{ $labels.model }} for 5 minutes"

      # Low cache hit rate
      - alert: ModelLowCacheHitRate
        expr: model:cache:hit_ratio < 0.70  # < 70% cache hits
        for: 30m
        labels:
          severity: info
          component: model-serving
        annotations:
          summary: "Low cache hit rate for model {{ $labels.model }}"
          description: "Cache hit rate is {{ $value | humanizePercentage }} (target: >80%)"

      # Memory leak detection
      - alert: ModelMemoryLeak
        expr: model:memory:growth_rate_1h > 100 * 1024 * 1024  # Growing > 100 MB/hr
        for: 2h
        labels:
          severity: warning
          component: model-serving
        annotations:
          summary: "Possible memory leak in model {{ $labels.model }}"
          description: "Memory growing at {{ $value | humanize }}B/hr"

    # Platform-wide alerts
    - name: ml_platform_alerts
      interval: 60s
      rules:

      # Overall platform error rate
      - alert: PlatformHighErrorRate
        expr: platform:error_ratio:rate5m > 0.10
        for: 5m
        labels:
          severity: critical
          component: platform
        annotations:
          summary: "ML Platform experiencing high error rate"
          description: "Platform-wide error rate is {{ $value | humanizePercentage }}"

      # Total request rate anomaly
      - alert: PlatformTrafficAnomaly
        expr: |
          abs(
            platform:predictions:rate5m
              -
            avg_over_time(platform:predictions:rate5m[1h])
          ) > (2 * stddev_over_time(platform:predictions:rate5m[1h]))
        for: 10m
        labels:
          severity: warning
          component: platform
        annotations:
          summary: "ML Platform traffic anomaly detected"
          description: "Current traffic {{ $value }} deviates significantly from normal"

    # SLA/SLO alerts
    - name: ml_slo_alerts
      interval: 60s
      rules:

      # SLO: 99.9% availability (error budget)
      - alert: SLOErrorBudgetBurn
        expr: |
          (
            1 - (
              sum(model:predictions:rate5m) - sum(model:errors:rate5m)
            ) / sum(model:predictions:rate5m)
          ) > 0.001  # > 0.1% error rate burns into error budget
        for: 1h
        labels:
          severity: warning
          component: slo
        annotations:
          summary: "Burning through error budget"
          description: "Current error rate {{ $value | humanizePercentage }} exceeds SLO target (99.9%)"

      # Latency SLO: p95 < 200ms
      - alert: SLOLatencyViolation
        expr: |
          histogram_quantile(0.95,
            sum(rate(model_prediction_duration_seconds_bucket[5m])) by (le)
          ) > 0.2
        for: 30m
        labels:
          severity: warning
          component: slo
        annotations:
          summary: "Latency SLO violation"
          description: "P95 latency {{ $value | humanizeDuration }} exceeds SLO target (200ms)"
```

```bash
# TODO: Apply alert rules
kubectl apply -f prometheus-alert-rules.yaml

# Reload Prometheus
kubectl rollout restart deployment prometheus-server -n monitoring

# Verify alerts are loaded
# Open Prometheus UI -> Alerts
kubectl port-forward -n monitoring svc/prometheus-server 9090:80
# Navigate to http://localhost:9090/alerts
```

**TODO 4.2:** Alert inhibition and routing

```yaml
# alertmanager-config.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: alertmanager-config
  namespace: monitoring
data:
  alertmanager.yml: |
    global:
      resolve_timeout: 5m

    # Inhibition rules: suppress less severe alerts when more severe fire
    inhibit_rules:
    # Don't alert about high errors if model is completely down
    - source_match:
        alertname: 'ModelNoPredictions'
      target_match_re:
        alertname: 'ModelHighErrorRate|ModelHighLatency'
      equal:
        - model

    # Don't alert about warning-level errors when critical-level fires
    - source_match:
        severity: 'critical'
      target_match:
        severity: 'warning'
      equal:
        - model
        - component

    # Route alerts to different receivers
    route:
      receiver: 'default'
      group_by: ['alertname', 'model']
      group_wait: 30s
      group_interval: 5m
      repeat_interval: 12h

      routes:
      # Page for critical alerts
      - match:
          severity: critical
        receiver: 'pagerduty'
        continue: true

      # Slack for warnings
      - match:
          severity: warning
        receiver: 'slack-warnings'

      # Email for info alerts
      - match:
          severity: info
        receiver: 'email'

    receivers:
    - name: 'default'
      webhook_configs:
      - url: 'http://alertmanager-webhook/alerts'

    - name: 'pagerduty'
      pagerduty_configs:
      - service_key: '<pagerduty-integration-key>'

    - name: 'slack-warnings'
      slack_configs:
      - api_url: '<slack-webhook-url>'
        channel: '#ml-platform-alerts'
        title: 'ML Platform Alert'
        text: '{{ range .Alerts }}{{ .Annotations.description }}{{ end }}'

    - name: 'email'
      email_configs:
      - to: 'ml-team@company.com'
        from: 'alerts@company.com'
        smarthost: 'smtp.company.com:587'
```

### Task 5: Query Optimization Techniques

**TODO 5.1:** Identify and fix slow queries

```promql
# TODO: Anti-pattern 1 - Querying without rate() on counters
# ❌ Wrong:
sum(model_predictions_total)

# ✅ Correct:
sum(rate(model_predictions_total[5m]))

# TODO: Anti-pattern 2 - Too many labels in grouping
# ❌ Wrong (groups by every label):
sum by (model, version, namespace, pod, node, cluster) (
  rate(model_predictions_total[5m])
)

# ✅ Correct (only necessary labels):
sum by (model) (rate(model_predictions_total[5m]))

# TODO: Anti-pattern 3 - Short range vectors for rate()
# ❌ Wrong (too short, spiky results):
rate(model_predictions_total[30s])

# ✅ Correct (4x scrape interval minimum):
rate(model_predictions_total[5m])  # if scrape interval is 30s

# TODO: Anti-pattern 4 - Complex subqueries without recording rules
# ❌ Wrong (calculated every time):
histogram_quantile(0.95,
  sum by (le, model) (
    rate(model_prediction_duration_seconds_bucket[5m])
  )
)
  /
avg(model:predictions:rate5m)

# ✅ Correct (use pre-computed values):
model:latency:p95 / platform:predictions:rate5m

# TODO: Anti-pattern 5 - Large time ranges without recording rules
# ❌ Wrong (30 days of raw data):
rate(model_predictions_total[30d])

# ✅ Correct (use downsampled data or recording rules):
# Use recording rule: model:predictions:daily
avg_over_time(model:predictions:daily[30d])
```

**TODO 5.2:** Cardinality management

```bash
# TODO: Check metric cardinality
cat > check_cardinality.sh << 'EOF'
#!/bin/bash
# Check Prometheus metric cardinality

PROM_URL="http://localhost:9090"

echo "=== Metric Cardinality Analysis ==="

# Total number of time series
echo -e "\n[1] Total time series:"
curl -s "$PROM_URL/api/v1/query" \
  --data-urlencode 'query=count({__name__=~".+"})' \
  | jq -r '.data.result[0].value[1]'

# Top metrics by cardinality
echo -e "\n[2] Top 10 metrics by cardinality:"
curl -s "$PROM_URL/api/v1/label/__name__/values" \
  | jq -r '.data[]' \
  | while read metric; do
      count=$(curl -s "$PROM_URL/api/v1/query" \
        --data-urlencode "query=count($metric)" \
        | jq -r '.data.result[0].value[1] // 0')
      echo "$count $metric"
  done \
  | sort -rn \
  | head -n 10

# Cardinality by job
echo -e "\n[3] Cardinality by job:"
curl -s "$PROM_URL/api/v1/query" \
  --data-urlencode 'query=count by (job) ({__name__=~".+"})' \
  | jq -r '.data.result[] | "\(.metric.job): \(.value[1])"'

echo -e "\n=== Analysis Complete ==="
EOF

chmod +x check_cardinality.sh

# TODO: Run cardinality check
# ./check_cardinality.sh
```

**TODO 5.3:** Reduce cardinality with relabeling

```yaml
# prometheus-relabeling.yaml
scrape_configs:
- job_name: 'model-serving'
  kubernetes_sd_configs:
  - role: pod

  # Drop unnecessary labels to reduce cardinality
  metric_relabel_configs:
  # Drop pod UID (unique per pod, high cardinality)
  - source_labels: [__meta_kubernetes_pod_uid]
    action: drop

  # Drop container ID (unique, high cardinality)
  - source_labels: [container_id]
    action: drop

  # Normalize version labels (v1.0.1 -> v1)
  - source_labels: [version]
    regex: '(v\d+)\.\d+\.\d+'
    target_label: version
    replacement: '$1'

  # Drop low-value metrics
  - source_labels: [__name__]
    regex: '(go_.*|process_.*|promhttp_.*)'
    action: drop

  # Keep only essential labels
  - regex: '__.*|pod_template_hash|controller_revision_hash'
    action: labeldrop
```

## Deliverables

Submit a repository with:

1. **PromQL Query Library** (`PROMQL_QUERIES.md`)
   - Collection of useful queries for ML monitoring
   - Explanations of each query
   - Performance notes

2. **Recording Rules Configuration**
   - `recording_rules.yml` - Production-ready recording rules
   - Documentation explaining each rule
   - Calculation of storage savings

3. **Alert Rules Configuration**
   - `alert_rules.yml` - Comprehensive alerts
   - Alert runbook (what to do when each alert fires)
   - Threshold justifications

4. **Performance Analysis** (`PERFORMANCE_ANALYSIS.md`)
   - Query benchmarks (before/after recording rules)
   - Cardinality analysis results
   - Optimization recommendations

5. **Scripts**
   - `benchmark_queries.sh` - Query performance testing
   - `check_cardinality.sh` - Cardinality analysis
   - Alert testing scripts

## Success Criteria

- [ ] Understand and can write PromQL queries for counters, gauges, histograms
- [ ] Recording rules deployed and reducing query latency by >5x
- [ ] Alert rules firing correctly with proper thresholds
- [ ] Alert inhibition prevents notification spam
- [ ] Query performance benchmarks show measurable improvement
- [ ] Cardinality under control (<100k time series)
- [ ] Can troubleshoot slow queries and optimize them
- [ ] Documentation includes runbooks for alerts
- [ ] Grafana dashboards use recording rules instead of raw queries

## Bonus Challenges

1. **Multi-Burn-Rate Alerts**: Implement Google SRE multi-window alerting for SLOs
2. **Anomaly Detection**: Use `predict_linear()` to detect anomalous trends
3. **Custom Exporters**: Write a Python exporter for custom ML metrics
4. **Federation**: Set up Prometheus federation for multi-cluster monitoring
5. **Long-term Storage**: Configure Thanos or Cortex for long-term metrics storage
6. **Alert Testing**: Create automated tests for alert rules using promtool

## Resources

- [PromQL Basics](https://prometheus.io/docs/prometheus/latest/querying/basics/)
- [Recording Rules](https://prometheus.io/docs/prometheus/latest/configuration/recording_rules/)
- [Alerting Rules](https://prometheus.io/docs/prometheus/latest/configuration/alerting_rules/)
- [PromQL Cheat Sheet](https://promlabs.com/promql-cheat-sheet/)
- [Robust Perception Blog](https://www.robustperception.io/blog/)

## Evaluation Rubric

| Criteria | Points |
|----------|--------|
| PromQL query fundamentals | 15 |
| Advanced queries (histograms, aggregations) | 20 |
| Recording rules implementation | 20 |
| Alert rules with proper thresholds | 20 |
| Query optimization and performance | 15 |
| Documentation and runbooks | 10 |

**Total: 100 points**
