# Exercise 05: Alerting & Incident Response Runbook for AI Infrastructure

## Overview
Combine metrics, logs, and tracing to implement a robust alerting pipeline and incident response workflow for the inference platform. You will configure Alertmanager/Grafana alert routing, develop runbooks, simulate incidents (latency spike, data drift, logging outages), and conduct a mini post-incident review to solidify operational readiness.

**Difficulty:** Advanced
**Estimated Time:** 3–4 hours
**Prerequisites:**
- Exercises 01–04 completed
- Lecture 04 (Logging, Alerting, ML Monitoring)
- Alertmanager or Grafana OnCall available
- Access to collaboration tooling (Slack/Teams) for notifications

## Learning Objectives
By completing this exercise you will:
1. Implement alert routing policies aligned with SLOs and team structure.
2. Configure multi-window burn rate alerts and log-based alerts in Prometheus/Grafana.
3. Simulate incidents and execute runbooks using observability tools.
4. Produce an incident timeline and post-incident review capturing lessons learned.
5. Establish continuous improvement backlog for observability and on-call processes.
6. Build production-ready alerting infrastructure for ML systems.
7. Develop incident response muscle memory through realistic simulations.

## What You'll Build

By the end of this exercise, you'll have:

- **Complete Alerting Stack**: Alertmanager with multi-channel routing (PagerDuty, Slack, Email)
- **Production Alert Rules**: SLO-based multi-window burn rate alerts, error budgets, drift detection
- **Professional Runbooks**: 5+ detailed runbooks following Google SRE best practices
- **Incident Simulation Framework**: Scripts to trigger realistic incidents
- **Post-Incident Review Process**: Templates and completed examples
- **Continuous Improvement System**: Backlog tracking and metrics

This builds directly on the observability foundation from Exercises 01-04, completing your production-ready ML monitoring stack.

## Part 1: Alert Routing Architecture

### 1.1 Directory Structure Setup

Create the following directory structure for alerting and incident management:

```bash
mkdir -p alerting/{config,rules,runbooks,incidents,docs}
cd alerting/

# Create subdirectories
mkdir -p config/{alertmanager,grafana}
mkdir -p rules/{prometheus,grafana}
mkdir -p runbooks/{inference,platform,ml-operations}
mkdir -p incidents/{2025-01,templates}
mkdir -p docs/policies
```

### 1.2 Alerting Policy Design

Create `docs/policies/alerting-policy.md`:

```markdown
# AI Infrastructure Alerting Policy

## Alert Severity Levels

### Critical (Page)
- **Impact**: Service degradation or complete outage affecting users
- **Examples**:
  - SLO burn rate exceeding error budget rapidly (multi-window alert)
  - Inference service completely down (100% error rate)
  - Data pipeline failure preventing model updates
- **Response Time**: 5 minutes
- **Notification**: PagerDuty (immediate page)
- **Escalation**: Automatic after 10 minutes if not acknowledged
- **On-Call Required**: Yes

### High (Urgent)
- **Impact**: Potential service degradation, error budget consumption
- **Examples**:
  - Elevated error rate (5-10%)
  - Latency degradation (P95 > 200ms but < SLO breach)
  - Model drift detected (PSI > 0.2)
  - Infrastructure alerts (high CPU, disk space warnings)
- **Response Time**: 15 minutes during business hours
- **Notification**: Slack #ai-infra-urgent + Email
- **On-Call Required**: During business hours

### Medium (Warning)
- **Impact**: Early warning signals, capacity planning
- **Examples**:
  - Moderate error rate increase (2-5%)
  - Feature store cache miss rate elevated
  - Log volume spike
  - Prometheus scrape failures
- **Response Time**: 1 hour
- **Notification**: Slack #ai-infra-alerts
- **On-Call Required**: No

### Low (Info)
- **Impact**: Informational, no immediate action required
- **Examples**:
  - Scheduled maintenance notifications
  - Deployment notifications
  - Capacity planning metrics
- **Response Time**: Best effort
- **Notification**: Slack #ai-infra-info
- **On-Call Required**: No

## Escalation Chain

### Primary On-Call
- **Response Time**: 5 minutes for critical, 15 minutes for high
- **Responsibilities**:
  - Acknowledge alerts
  - Execute runbooks
  - Escalate if unable to resolve within 30 minutes

### Secondary On-Call
- **Escalation Trigger**: 10 minutes no acknowledgment, or primary requests backup
- **Responsibilities**:
  - Support primary on-call
  - Take over if primary unavailable

### Incident Commander (Manager/Tech Lead)
- **Escalation Trigger**: Incident duration > 1 hour or multi-service impact
- **Responsibilities**:
  - Coordinate response across teams
  - External communication
  - Post-incident review facilitation

### Subject Matter Experts
- **ML Engineering**: Model-specific issues, drift, performance
- **Platform Engineering**: Kubernetes, infrastructure, scaling
- **Data Engineering**: Feature store, data pipelines

## Routing Matrix

| Alert Type | Severity | Primary Channel | Secondary Channel | Escalation |
|------------|----------|-----------------|-------------------|------------|
| SLO Burn Rate | Critical | PagerDuty | Slack #incidents | 10 min |
| Error Rate High | Critical | PagerDuty | Slack #incidents | 10 min |
| Latency Breach | High | Slack #ai-infra-urgent | Email | 30 min |
| Model Drift | High | Slack #ai-infra-urgent | Email | 1 hour |
| Feature Errors | Medium | Slack #ai-infra-alerts | - | - |
| Infrastructure | Medium | Slack #ai-infra-alerts | - | - |
| Deployment | Low | Slack #ai-infra-info | - | - |

## Maintenance Windows

### Scheduled Maintenance
- **Notification**: 48 hours advance notice in #ai-infra-info
- **Alert Silencing**: Auto-silence via Alertmanager silences API
- **Duration**: Typically 2-4 hours
- **Approval**: Engineering Manager + Product Owner

### Emergency Maintenance
- **Notification**: Immediate notification to #incidents
- **Alert Silencing**: Manual silence with incident ticket reference
- **Duration**: As needed
- **Approval**: On-call engineer authority

## Auto-Silence Rules

```yaml
# Silence alerts during known deployment windows
- matchers:
    - deployment_type = "scheduled"
  duration: 2h
  created_by: "ci/cd-pipeline"

# Silence test environment alerts overnight
- matchers:
    - environment = "test"
    - time_range = "22:00-06:00 UTC"
  duration: 8h
  created_by: "automation"
```

## On-Call Rotation

- **Rotation Length**: 1 week (Monday 9am - Monday 9am)
- **Primary/Secondary**: Always have both assigned
- **Handoff**: Monday morning sync (15 minutes)
- **PTO Coverage**: Swap assigned 1 week in advance
- **Compensation**: Additional PTO day per week on-call
```

### 1.3 Complete Alertmanager Configuration

Create `config/alertmanager/alertmanager.yml`:

```yaml
# Alertmanager Configuration for AI Infrastructure
# Version: 0.26.0
# Purpose: Multi-channel alert routing with escalation

global:
  # API endpoints for integrations
  slack_api_url: '${SLACK_WEBHOOK_URL}'
  pagerduty_url: 'https://events.pagerduty.com/v2/enqueue'

  # Global defaults
  resolve_timeout: 5m
  http_config:
    follow_redirects: true

  # SMTP for email notifications
  smtp_from: 'alerts@ai-infra.example.com'
  smtp_smarthost: 'smtp.example.com:587'
  smtp_auth_username: '${SMTP_USERNAME}'
  smtp_auth_password: '${SMTP_PASSWORD}'
  smtp_require_tls: true

# Templates for alert formatting
templates:
  - '/etc/alertmanager/templates/*.tmpl'

# Main routing tree
route:
  # Default receiver for unmatched alerts
  receiver: 'slack-default'

  # Group alerts by these labels
  group_by: ['alertname', 'service', 'severity']

  # Wait time before sending first notification
  group_wait: 10s

  # Wait time before sending notification about new alerts in group
  group_interval: 5m

  # Wait time before re-sending notification
  repeat_interval: 4h

  # Child routes (processed in order)
  routes:
    # Critical alerts - page immediately
    - matchers:
        - severity = "critical"
      receiver: 'pagerduty-critical'
      group_wait: 10s
      group_interval: 5m
      repeat_interval: 5m
      continue: true  # Also send to Slack

    - matchers:
        - severity = "critical"
      receiver: 'slack-incidents'
      group_wait: 10s

    # High priority - Slack + Email during business hours
    - matchers:
        - severity = "high"
      receiver: 'slack-urgent'
      group_wait: 30s
      group_interval: 10m
      repeat_interval: 1h
      # Time-based routing (business hours)
      active_time_intervals:
        - business_hours

    # Model drift alerts - ML team specific
    - matchers:
        - alertname =~ "ModelDrift.*|DataDrift.*"
      receiver: 'slack-ml-team'
      group_by: ['model_name', 'feature']
      repeat_interval: 6h

    # Infrastructure alerts
    - matchers:
        - alertname =~ "Node.*|Kube.*|Prometheus.*"
      receiver: 'slack-platform'
      group_by: ['cluster', 'node']
      repeat_interval: 2h

    # Warning level - Slack only
    - matchers:
        - severity = "warning"
      receiver: 'slack-alerts'
      repeat_interval: 12h

    # Info level - low-noise channel
    - matchers:
        - severity = "info"
      receiver: 'slack-info'
      repeat_interval: 24h

# Time interval definitions
time_intervals:
  - name: business_hours
    time_intervals:
      - times:
          - start_time: '09:00'
            end_time: '17:00'
        weekdays: ['monday:friday']
        location: 'America/New_York'

# Inhibition rules - suppress alerts based on other alerts
inhibit_rules:
  # Inhibit warning if critical is firing
  - source_matchers:
      - severity = "critical"
    target_matchers:
      - severity = "warning"
    equal: ['service', 'alertname']

  # Inhibit node alerts if entire cluster is down
  - source_matchers:
      - alertname = "KubernetesClusterDown"
    target_matchers:
      - alertname =~ "Node.*"
    equal: ['cluster']

  # Inhibit downstream service alerts if upstream dependency is down
  - source_matchers:
      - alertname = "FeatureStoreDown"
    target_matchers:
      - alertname = "InferenceFeatureErrors"
    equal: ['environment']

# Receiver definitions
receivers:
  # PagerDuty for critical alerts
  - name: 'pagerduty-critical'
    pagerduty_configs:
      - routing_key: '${PAGERDUTY_INTEGRATION_KEY}'
        severity: 'critical'
        description: '{{ .CommonAnnotations.summary }}'
        details:
          firing: '{{ .Alerts.Firing | len }}'
          resolved: '{{ .Alerts.Resolved | len }}'
          service: '{{ .CommonLabels.service }}'
          dashboard: '{{ .CommonAnnotations.dashboard }}'
          runbook: '{{ .CommonAnnotations.runbook }}'
        links:
          - href: '{{ .CommonAnnotations.dashboard }}'
            text: 'View Dashboard'
          - href: '{{ .CommonAnnotations.runbook }}'
            text: 'View Runbook'

  # Slack - Incidents channel (critical)
  - name: 'slack-incidents'
    slack_configs:
      - channel: '#ai-infra-incidents'
        username: 'AlertManager'
        icon_emoji: ':rotating_light:'
        title: ':fire: CRITICAL: {{ .CommonLabels.alertname }}'
        text: |
          *Summary:* {{ .CommonAnnotations.summary }}
          *Service:* {{ .CommonLabels.service }}
          *Severity:* {{ .CommonLabels.severity }}
          *Firing Alerts:* {{ .Alerts.Firing | len }}

          *Dashboard:* {{ .CommonAnnotations.dashboard }}
          *Runbook:* {{ .CommonAnnotations.runbook }}
        actions:
          - type: button
            text: 'View Dashboard :chart_with_upwards_trend:'
            url: '{{ .CommonAnnotations.dashboard }}'
          - type: button
            text: 'View Runbook :book:'
            url: '{{ .CommonAnnotations.runbook }}'
        color: 'danger'
        send_resolved: true

  # Slack - Urgent channel (high priority)
  - name: 'slack-urgent'
    slack_configs:
      - channel: '#ai-infra-urgent'
        username: 'AlertManager'
        icon_emoji: ':warning:'
        title: 'HIGH: {{ .CommonLabels.alertname }}'
        text: |
          *Summary:* {{ .CommonAnnotations.summary }}
          *Service:* {{ .CommonLabels.service }}
          *Firing:* {{ .Alerts.Firing | len }}

          {{ .CommonAnnotations.description }}
        color: 'warning'
        send_resolved: true

  # Slack - ML Team
  - name: 'slack-ml-team'
    slack_configs:
      - channel: '#ml-platform-alerts'
        username: 'ML Monitor'
        icon_emoji: ':robot_face:'
        title: 'ML Alert: {{ .CommonLabels.alertname }}'
        text: |
          *Model:* {{ .CommonLabels.model_name }}
          *Issue:* {{ .CommonAnnotations.summary }}

          {{ .CommonAnnotations.description }}
        color: '#FFA500'
        send_resolved: true

  # Slack - Platform team
  - name: 'slack-platform'
    slack_configs:
      - channel: '#platform-alerts'
        username: 'Platform Monitor'
        icon_emoji: ':kubernetes:'
        title: 'Infrastructure: {{ .CommonLabels.alertname }}'
        text: '{{ .CommonAnnotations.summary }}'
        color: '#0000FF'
        send_resolved: true

  # Slack - General alerts
  - name: 'slack-alerts'
    slack_configs:
      - channel: '#ai-infra-alerts'
        username: 'AlertManager'
        title: 'Warning: {{ .CommonLabels.alertname }}'
        text: '{{ .CommonAnnotations.summary }}'
        send_resolved: true

  # Slack - Info channel
  - name: 'slack-info'
    slack_configs:
      - channel: '#ai-infra-info'
        username: 'InfoBot'
        title: 'Info: {{ .CommonLabels.alertname }}'
        text: '{{ .CommonAnnotations.summary }}'
        color: 'good'

  # Default catch-all
  - name: 'slack-default'
    slack_configs:
      - channel: '#ai-infra-alerts'
        title: 'Uncategorized Alert: {{ .CommonLabels.alertname }}'
        text: '{{ .CommonAnnotations.summary }}'
```

### 1.4 Secrets Management

Create `config/alertmanager/secrets.yaml` (for Kubernetes):

```yaml
# Kubernetes Secret for Alertmanager credentials
# Apply with: kubectl apply -f secrets.yaml -n monitoring
apiVersion: v1
kind: Secret
metadata:
  name: alertmanager-secrets
  namespace: monitoring
type: Opaque
stringData:
  # PagerDuty integration key
  PAGERDUTY_INTEGRATION_KEY: "your-pagerduty-key-here"

  # Slack webhook URL
  SLACK_WEBHOOK_URL: "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"

  # SMTP credentials
  SMTP_USERNAME: "alerts@ai-infra.example.com"
  SMTP_PASSWORD: "your-smtp-password"
```

Create `.env.alertmanager` for Docker Compose:

```bash
# Alertmanager Environment Variables
# DO NOT commit this file to version control!

# PagerDuty Integration
PAGERDUTY_INTEGRATION_KEY=your_pagerduty_integration_key_here

# Slack Webhooks
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL

# SMTP Configuration
SMTP_USERNAME=alerts@ai-infra.example.com
SMTP_PASSWORD=your_smtp_password_here

# Email Recipients
ONCALL_EMAIL=oncall@ai-infra.example.com
ML_TEAM_EMAIL=ml-team@ai-infra.example.com
```

### 1.5 Alertmanager Deployment

Update `docker-compose.yml` from Exercise 02 to include Alertmanager:

```yaml
services:
  alertmanager:
    image: prom/alertmanager:v0.26.0
    container_name: alertmanager
    ports:
      - "9093:9093"
    volumes:
      - ./config/alertmanager:/etc/alertmanager
      - alertmanager-data:/alertmanager
    command:
      - '--config.file=/etc/alertmanager/alertmanager.yml'
      - '--storage.path=/alertmanager'
      - '--web.external-url=http://localhost:9093'
      - '--cluster.advertise-address=0.0.0.0:9093'
    env_file:
      - .env.alertmanager
    networks:
      - monitoring
    restart: unless-stopped

  prometheus:
    # ... existing configuration ...
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--alertmanager.url=http://alertmanager:9093'  # Add this line
    depends_on:
      - alertmanager

volumes:
  alertmanager-data:
    driver: local

networks:
  monitoring:
    driver: bridge
```

**Verification:**

```bash
# Start Alertmanager
docker-compose up -d alertmanager

# Check Alertmanager UI
open http://localhost:9093

# Check configuration is valid
docker exec alertmanager amtool check-config /etc/alertmanager/alertmanager.yml

# View current alerts
docker exec alertmanager amtool alert query

# Test silence creation
docker exec alertmanager amtool silence add alertname=Test --duration=1h --comment="Testing silence"
```

## Part 2: Alert Implementations

### 2.1 Metrics Alerts (Prometheus)

Create `rules/prometheus/inference-alerts.yml`:

```yaml
# Prometheus Alert Rules for AI Inference Service
# Purpose: SLO-based alerting following Google SRE multi-window burn rate methodology

groups:
  - name: inference_slo_alerts
    interval: 30s
    rules:
      # Critical: Fast burn rate (5m/1h windows)
      # Detects rapid SLO violations consuming error budget quickly
      - alert: InferenceLatencyBurnRateCritical
        expr: |
          (
            slo:inference_latency_p95:burn_rate{window="5m"} > 14.4
            and on(service, environment)
            slo:inference_latency_p95:burn_rate{window="1h"} > 14.4
          )
        for: 2m
        labels:
          severity: critical
          service: inference-gateway
          slo: latency
          team: ml-platform
        annotations:
          summary: "CRITICAL: Inference latency burn rate extremely high"
          description: |
            The inference service is consuming error budget at {{ $value | humanize }}x the acceptable rate.
            At this rate, the monthly error budget will be exhausted in < 6 hours.

            Current burn rates:
            - 5m window: {{ $value | humanize }}x (threshold: 14.4x)
            - 1h window: {{ with query "slo:inference_latency_p95:burn_rate{window=\"1h\"}" }}{{ . | first | value | humanize }}{{ end }}x

            This indicates a severe latency issue affecting users NOW.
          runbook: https://runbooks.example.com/inference-latency
          dashboard: http://grafana:3000/d/inference-slo/inference-service-slo
          playbook: |
            1. Check Grafana dashboard for latency spike timing
            2. Review recent deployments (rollback if needed)
            3. Check resource utilization (CPU, GPU, memory)
            4. Review inference request patterns for traffic spike
            5. Escalate to ML Platform team if issue persists > 15 minutes

      # High: Moderate burn rate (1h/6h windows)
      - alert: InferenceLatencyBurnRateHigh
        expr: |
          (
            slo:inference_latency_p95:burn_rate{window="1h"} > 6
            and on(service, environment)
            slo:inference_latency_p95:burn_rate{window="6h"} > 6
          )
          and
          (
            slo:inference_latency_p95:burn_rate{window="5m"} <= 14.4
            or
            slo:inference_latency_p95:burn_rate{window="1h"} <= 14.4
          )
        for: 15m
        labels:
          severity: high
          service: inference-gateway
          slo: latency
          team: ml-platform
        annotations:
          summary: "HIGH: Inference latency burn rate elevated"
          description: |
            The inference service is consuming error budget at {{ $value | humanize }}x the acceptable rate.
            At this rate, the monthly error budget will be exhausted in < 5 days.

            Current burn rates:
            - 1h window: {{ $value | humanize }}x (threshold: 6x)
            - 6h window: {{ with query "slo:inference_latency_p95:burn_rate{window=\"6h\"}" }}{{ . | first | value | humanize }}{{ end }}x
          runbook: https://runbooks.example.com/inference-latency
          dashboard: http://grafana:3000/d/inference-slo/inference-service-slo

      # Availability SLO - Critical error rate
      - alert: InferenceErrorRateCritical
        expr: |
          (
            slo:inference_availability:burn_rate{window="5m"} > 14.4
            and on(service, environment)
            slo:inference_availability:burn_rate{window="1h"} > 14.4
          )
        for: 2m
        labels:
          severity: critical
          service: inference-gateway
          slo: availability
          team: ml-platform
        annotations:
          summary: "CRITICAL: Inference error rate extremely high"
          description: |
            The inference service error rate is {{ $value | humanize }}% (SLO: 99.9% = 0.1% errors).
            Error budget consumption rate: {{ with query "slo:inference_availability:burn_rate{window=\"5m\"}" }}{{ . | first | value | humanize }}{{ end }}x

            This indicates a critical availability issue affecting users NOW.
          runbook: https://runbooks.example.com/inference-errors
          dashboard: http://grafana:3000/d/inference-slo/inference-service-slo
          playbook: |
            1. Check error logs: kubectl logs -l app=inference-gateway --tail=100 | grep ERROR
            2. Identify error patterns (feature store, model loading, OOM)
            3. Check downstream dependencies (feature store, model registry)
            4. Rollback recent deployment if errors started after deploy
            5. Page ML Platform on-call if cannot resolve in 10 minutes

      # Error rate warning
      - alert: InferenceErrorRateHigh
        expr: |
          (
            sum(rate(inference_requests_total{status=~"5.."}[5m])) by (service, environment)
            /
            sum(rate(inference_requests_total[5m])) by (service, environment)
          ) > 0.05
        for: 10m
        labels:
          severity: warning
          service: inference-gateway
          team: ml-platform
        annotations:
          summary: "Inference error rate elevated: {{ $value | humanizePercentage }}"
          description: |
            The inference service error rate is {{ $value | humanizePercentage }} (threshold: 5%).

            This is below SLO breach levels but warrants investigation.
          runbook: https://runbooks.example.com/inference-errors
          dashboard: http://grafana:3000/d/inference-slo/inference-service-slo

  - name: inference_operational_alerts
    interval: 1m
    rules:
      # Model loading failures
      - alert: ModelLoadFailure
        expr: |
          increase(model_load_errors_total[10m]) > 0
        for: 5m
        labels:
          severity: high
          service: inference-gateway
          component: model-loader
          team: ml-platform
        annotations:
          summary: "Model loading failures detected"
          description: |
            The inference service has failed to load models {{ $value }} times in the past 10 minutes.

            Model: {{ $labels.model_name }}
            Version: {{ $labels.model_version }}

            This may indicate:
            - Model registry connectivity issues
            - Corrupted model artifacts
            - Insufficient memory/disk space
            - Model format incompatibility
          runbook: https://runbooks.example.com/model-loading

      # Feature store errors
      - alert: FeatureStoreErrorsHigh
        expr: |
          (
            sum(rate(feature_fetch_errors_total[5m])) by (service, environment)
            /
            sum(rate(feature_fetch_total[5m])) by (service, environment)
          ) > 0.10
        for: 10m
        labels:
          severity: high
          service: inference-gateway
          component: feature-store
          team: ml-platform
        annotations:
          summary: "Feature store error rate high: {{ $value | humanizePercentage }}"
          description: |
            The feature store error rate is {{ $value | humanizePercentage }} (threshold: 10%).

            Feature: {{ $labels.feature_name }}

            Common causes:
            - Feature store service degradation
            - Missing features for new users
            - Cache expiration issues
            - Network connectivity problems
          runbook: https://runbooks.example.com/feature-store-errors

      # GPU utilization
      - alert: GPUUtilizationLow
        expr: |
          avg(inference_gpu_utilization_percent) by (instance, gpu_id) < 20
        for: 30m
        labels:
          severity: warning
          service: inference-gateway
          component: gpu
          team: ml-platform
        annotations:
          summary: "GPU underutilized on {{ $labels.instance }}"
          description: |
            GPU {{ $labels.gpu_id }} utilization is {{ $value | humanize }}% (expected: > 20%).

            This may indicate:
            - Inefficient batching configuration
            - CPU bottleneck
            - Model not using GPU
            - Insufficient traffic

            Consider:
            - Reviewing batch size configuration
            - Profiling inference pipeline
            - Cost optimization (downsize GPU)
          runbook: https://runbooks.example.com/gpu-optimization

      - alert: GPUMemoryHigh
        expr: |
          (inference_gpu_memory_used_bytes / inference_gpu_memory_total_bytes) > 0.90
        for: 10m
        labels:
          severity: high
          service: inference-gateway
          component: gpu
          team: ml-platform
        annotations:
          summary: "GPU memory usage critical on {{ $labels.instance }}"
          description: |
            GPU {{ $labels.gpu_id }} memory usage is {{ $value | humanizePercentage }} (threshold: 90%).

            Risk of OOM errors and inference failures.

            Immediate actions:
            - Check for memory leaks
            - Review batch size configuration
            - Consider model quantization
            - Add GPU nodes if sustained high traffic
          runbook: https://runbooks.example.com/gpu-memory

  - name: infrastructure_alerts
    interval: 1m
    rules:
      # Prometheus scrape failures
      - alert: PrometheusScrapeFailure
        expr: |
          up{job="inference-gateway"} == 0
        for: 5m
        labels:
          severity: warning
          component: prometheus
          team: platform
        annotations:
          summary: "Prometheus cannot scrape {{ $labels.instance }}"
          description: |
            Prometheus has been unable to scrape metrics from {{ $labels.instance }} for 5 minutes.

            Possible causes:
            - Service is down
            - Network connectivity issue
            - Metrics endpoint not responding
            - Authentication/authorization issue
          runbook: https://runbooks.example.com/prometheus-scrape-failure

      # High API latency (not SLO breach yet)
      - alert: InferenceLatencyElevated
        expr: |
          histogram_quantile(0.95,
            rate(inference_request_duration_seconds_bucket[5m])
          ) > 0.2
        for: 15m
        labels:
          severity: warning
          service: inference-gateway
          team: ml-platform
        annotations:
          summary: "Inference P95 latency elevated: {{ $value | humanizeDuration }}"
          description: |
            The inference service P95 latency is {{ $value | humanizeDuration }} (warning threshold: 200ms, SLO: 300ms).

            This is an early warning before SLO breach.
          runbook: https://runbooks.example.com/inference-latency
          dashboard: http://grafana:3000/d/inference-slo/inference-service-slo

      # Request rate anomaly
      - alert: InferenceRequestRateAnomalous
        expr: |
          abs(
            rate(inference_requests_total[5m])
            - avg_over_time(rate(inference_requests_total[5m])[1h:5m])
          ) >
          3 * stddev_over_time(rate(inference_requests_total[5m])[1h:5m])
        for: 10m
        labels:
          severity: warning
          service: inference-gateway
          team: ml-platform
        annotations:
          summary: "Inference request rate anomalous"
          description: |
            The inference request rate is {{ $value | humanize }} req/s, which is > 3 standard deviations from the 1-hour average.

            This could indicate:
            - Traffic spike (legitimate or attack)
            - Client retry storm
            - Scheduled batch job
            - Marketing campaign
          runbook: https://runbooks.example.com/traffic-anomaly
```

### 2.2 Log-Based Alerts (Grafana Alerting)

Create `rules/grafana/log-alerts.json`:

```json
{
  "uid": "log-alerts-001",
  "title": "Log-Based Alerts for Inference Service",
  "folder": "AI Infrastructure",
  "interval": 60,
  "rules": [
    {
      "uid": "feature-not-found-alert",
      "title": "Feature Not Found Errors High",
      "condition": "B",
      "data": [
        {
          "refId": "A",
          "queryType": "range",
          "datasourceUid": "loki-uid",
          "expr": "sum(count_over_time({service=\"inference-gateway\", level=\"error\"} |= \"FeatureNotFound\" [5m]))",
          "legendFormat": "",
          "instant": false
        },
        {
          "refId": "B",
          "queryType": "",
          "datasourceUid": "-100",
          "conditions": [
            {
              "evaluator": {
                "params": [20],
                "type": "gt"
              },
              "query": {
                "params": ["A"]
              },
              "type": "query"
            }
          ]
        }
      ],
      "noDataState": "NoData",
      "execErrState": "Error",
      "for": "10m",
      "annotations": {
        "summary": "High rate of FeatureNotFound errors",
        "description": "The inference service has logged {{ $values.A.Value }} FeatureNotFound errors in the past 5 minutes. This suggests feature store issues or missing feature definitions.",
        "runbook": "https://runbooks.example.com/feature-not-found"
      },
      "labels": {
        "severity": "warning",
        "team": "ml-platform",
        "component": "feature-store"
      },
      "isPaused": false
    },
    {
      "uid": "log-ingestion-outage",
      "title": "Log Ingestion Outage Detected",
      "condition": "B",
      "data": [
        {
          "refId": "A",
          "queryType": "instant",
          "datasourceUid": "loki-uid",
          "expr": "absent_over_time({job=\"docker-logs\"}[10m])",
          "legendFormat": "",
          "instant": true
        },
        {
          "refId": "B",
          "queryType": "",
          "datasourceUid": "-100",
          "conditions": [
            {
              "evaluator": {
                "params": [0],
                "type": "gt"
              },
              "query": {
                "params": ["A"]
              },
              "type": "query"
            }
          ]
        }
      ],
      "noDataState": "Alerting",
      "execErrState": "Error",
      "for": "5m",
      "annotations": {
        "summary": "No logs received from inference service",
        "description": "Loki has not received any logs from the inference service in the past 10 minutes. This could indicate: Promtail down, network issue, or service completely down.",
        "runbook": "https://runbooks.example.com/log-ingestion-outage"
      },
      "labels": {
        "severity": "high",
        "team": "platform",
        "component": "logging"
      },
      "isPaused": false
    },
    {
      "uid": "error-rate-spike-logs",
      "title": "Error Log Rate Spike",
      "condition": "B",
      "data": [
        {
          "refId": "A",
          "queryType": "range",
          "datasourceUid": "loki-uid",
          "expr": "sum(rate({service=\"inference-gateway\", level=\"error\"}[5m]))",
          "legendFormat": "",
          "instant": false
        },
        {
          "refId": "B",
          "queryType": "",
          "datasourceUid": "-100",
          "conditions": [
            {
              "evaluator": {
                "params": [10],
                "type": "gt"
              },
              "query": {
                "params": ["A"]
              },
              "type": "query"
            }
          ]
        }
      ],
      "noDataState": "NoData",
      "execErrState": "Error",
      "for": "10m",
      "annotations": {
        "summary": "Error log rate spike: {{ $values.A.Value | humanize }} errors/sec",
        "description": "The inference service is logging {{ $values.A.Value | humanize }} errors per second (threshold: 10/sec). Review logs for error patterns.",
        "runbook": "https://runbooks.example.com/error-log-spike",
        "dashboard": "http://grafana:3000/d/logs-dashboard"
      },
      "labels": {
        "severity": "warning",
        "team": "ml-platform",
        "component": "application"
      },
      "isPaused": false
    },
    {
      "uid": "pii-detected-logs",
      "title": "PII Detected in Logs (Security)",
      "condition": "B",
      "data": [
        {
          "refId": "A",
          "queryType": "range",
          "datasourceUid": "loki-uid",
          "expr": "sum(count_over_time({service=\"inference-gateway\"} |~ \"(SSN|social.*security|credit.*card|\\\\b\\\\d{3}-\\\\d{2}-\\\\d{4}\\\\b)\" [10m]))",
          "legendFormat": "",
          "instant": false
        },
        {
          "refId": "B",
          "queryType": "",
          "datasourceUid": "-100",
          "conditions": [
            {
              "evaluator": {
                "params": [0],
                "type": "gt"
              },
              "query": {
                "params": ["A"]
              },
              "type": "query"
            }
          ]
        }
      ],
      "noDataState": "NoData",
      "execErrState": "Error",
      "for": "5m",
      "annotations": {
        "summary": "SECURITY: Potential PII detected in logs",
        "description": "{{ $values.A.Value }} log entries potentially containing PII detected in the past 10 minutes. This is a compliance violation (GDPR, CCPA). Immediate action required.",
        "runbook": "https://runbooks.example.com/pii-in-logs-incident",
        "severity": "critical"
      },
      "labels": {
        "severity": "critical",
        "team": "security",
        "component": "compliance"
      },
      "isPaused": false
    }
  ]
}
```

### 2.3 Data/Model Drift Alerts

Create `rules/prometheus/ml-monitoring-alerts.yml`:

```yaml
# ML-Specific Monitoring Alerts
# Purpose: Model performance, drift detection, data quality

groups:
  - name: model_drift_alerts
    interval: 5m
    rules:
      # Population Stability Index (PSI) for feature drift
      - alert: FeatureDriftDetected
        expr: |
          model_drift_psi{metric_type="feature"} > 0.2
        for: 30m
        labels:
          severity: high
          team: ml-engineering
          component: drift-detection
        annotations:
          summary: "Feature drift detected: {{ $labels.feature_name }}"
          description: |
            Feature {{ $labels.feature_name }} has PSI of {{ $value | humanize }} (threshold: 0.2).

            PSI Severity:
            - 0.1-0.2: Minor shift (monitor)
            - 0.2-0.25: Medium shift (investigate)
            - >0.25: Major shift (retrain recommended)

            Current: {{ $value | humanize }}

            Actions:
            1. Review feature distribution changes in Grafana dashboard
            2. Check data pipeline for issues
            3. Evaluate model performance on recent data
            4. Consider retraining if PSI > 0.25 or performance degraded
          runbook: https://runbooks.example.com/feature-drift
          dashboard: http://grafana:3000/d/ml-monitoring/ml-monitoring

      # Target drift (prediction distribution shift)
      - alert: PredictionDriftDetected
        expr: |
          model_drift_psi{metric_type="prediction"} > 0.25
        for: 1h
        labels:
          severity: high
          team: ml-engineering
          component: drift-detection
        annotations:
          summary: "Prediction drift detected for model {{ $labels.model_name }}"
          description: |
            Model {{ $labels.model_name }} prediction distribution has shifted significantly (PSI: {{ $value | humanize }}).

            This could indicate:
            - Input data distribution change
            - Model degradation
            - Upstream feature engineering changes
            - Real-world distribution shift

            Recommended actions:
            - Compare recent predictions vs training distribution
            - Review model performance metrics
            - Check for upstream data changes
            - Consider model retraining
          runbook: https://runbooks.example.com/prediction-drift

      # Model performance degradation (if ground truth available)
      - alert: ModelPerformanceDegraded
        expr: |
          (
            model_performance_metric{metric="auc_roc"} < 0.75
            and
            model_performance_metric{metric="auc_roc"} offset 7d > 0.80
          )
        for: 24h
        labels:
          severity: critical
          team: ml-engineering
          component: model-performance
        annotations:
          summary: "Model {{ $labels.model_name }} performance degraded"
          description: |
            Model {{ $labels.model_name }} AUC-ROC has dropped from {{ with query "model_performance_metric{metric=\"auc_roc\"} offset 7d" }}{{ . | first | value | humanize }}{{ end }} (7 days ago) to {{ $value | humanize }} (current).

            This is a significant performance degradation requiring immediate attention.

            Actions:
            1. Investigate data drift
            2. Review recent training/deployment changes
            3. Analyze error cases
            4. Plan emergency model retrain
            5. Consider rollback to previous model version
          runbook: https://runbooks.example.com/model-performance-degradation
          playbook: emergency-retrain

      # Data quality issues
      - alert: MissingFeaturesHigh
        expr: |
          (
            sum(rate(feature_missing_total[10m])) by (feature_name)
            /
            sum(rate(inference_requests_total[10m]))
          ) > 0.10
        for: 15m
        labels:
          severity: warning
          team: data-engineering
          component: data-quality
        annotations:
          summary: "High missing feature rate: {{ $labels.feature_name }}"
          description: |
            Feature {{ $labels.feature_name }} is missing in {{ $value | humanizePercentage }} of requests (threshold: 10%).

            This degrades model performance and may indicate data pipeline issues.

            Actions:
            - Check feature store population job
            - Review feature engineering pipeline
            - Verify default value handling
          runbook: https://runbooks.example.com/missing-features

      # Fairness/Bias monitoring (example)
      - alert: ModelFairnessViolation
        expr: |
          abs(
            model_fairness_metric{metric="demographic_parity", group="A"}
            -
            model_fairness_metric{metric="demographic_parity", group="B"}
          ) > 0.1
        for: 1h
        labels:
          severity: high
          team: ml-engineering
          component: fairness
        annotations:
          summary: "Model fairness violation detected"
          description: |
            Model {{ $labels.model_name }} shows demographic parity difference of {{ $value | humanize }} between groups (threshold: 0.1).

            This may indicate model bias requiring investigation and potential mitigation.

            Actions:
            1. Review fairness metrics in detail
            2. Analyze error rates by demographic group
            3. Consult with ML ethics team
            4. Document findings for compliance
            5. Plan bias mitigation strategy
          runbook: https://runbooks.example.com/fairness-violation
          severity: high

  - name: data_quality_alerts
    interval: 5m
    rules:
      # Inference input validation failures
      - alert: InputValidationFailuresHigh
        expr: |
          (
            sum(rate(inference_input_validation_failures_total[10m]))
            /
            sum(rate(inference_requests_total[10m]))
          ) > 0.05
        for: 15m
        labels:
          severity: warning
          team: ml-platform
          component: data-validation
        annotations:
          summary: "Input validation failure rate: {{ $value | humanizePercentage }}"
          description: |
            {{ $value | humanizePercentage }} of inference requests are failing input validation (threshold: 5%).

            Common causes:
            - Client sending malformed requests
            - Schema changes not backward compatible
            - Data type mismatches
            - Out-of-range values

            Review validation error logs for patterns.
          runbook: https://runbooks.example.com/input-validation-failures
```

## Part 3: Runbook Development

### 3.1 Runbook Template

All runbooks should follow this standard structure for consistency:

Create `runbooks/templates/runbook-template.md`:

```markdown
# Runbook: [Alert Name]

**Alert Name**: `AlertNameFromPrometheus`
**Severity**: Critical / High / Warning
**Team**: ML Platform / Data Engineering / Platform
**Last Updated**: YYYY-MM-DD

## Overview
Brief description of what this alert indicates and why it matters.

## Impact
- **User Impact**: What users experience when this alert fires
- **Business Impact**: Revenue, SLA, reputation implications
- **Scope**: How many users/requests affected

## Symptoms
Observable signs that this issue is occurring:
- Specific metrics elevated/depressed
- Log patterns
- User-reported issues

## Triage Steps (5 minutes)

### 1. Verify the Alert
- [ ] Check Grafana dashboard: [link]
- [ ] Confirm metrics in Prometheus: [query]
- [ ] Review recent changes (deployments, config changes)

### 2. Assess Scope
- [ ] How many instances affected?
- [ ] What percentage of traffic impacted?
- [ ] Is issue isolated or widespread?

### 3. Quick Checks
- [ ] Check dependency health: [list dependencies]
- [ ] Review error logs: [log query]
- [ ] Check resource utilization

## Investigation

### Prometheus Queries
```promql
# List of relevant Prometheus queries
```

### Grafana Dashboards
- Primary: [dashboard link]
- Secondary: [related dashboards]

### Log Queries (LogQL)
```logql
# Loki queries to investigate
```

### Common Root Causes
1. **Cause 1**: Description and how to identify
2. **Cause 2**: Description and how to identify
3. **Cause 3**: Description and how to identify

## Mitigation

### Immediate Actions (< 15 minutes)
Step-by-step instructions to stop the bleeding:
1. Action 1
2. Action 2
3. Action 3

### Rollback Procedure (if deployment-related)
```bash
# Commands to rollback
```

### Scaling Response (if capacity-related)
```bash
# Commands to scale resources
```

## Escalation

### When to Escalate
- Issue not resolved within 30 minutes
- Impact increasing
- Root cause unclear

### Escalation Path
1. **Primary**: [Name/Role] - @slack-handle - [phone]
2. **Secondary**: [Name/Role] - @slack-handle - [phone]
3. **Manager**: [Name/Role] - @slack-handle - [phone]

### External Dependencies
- Vendor support: [contact info]
- Cloud provider support: [case escalation process]

## Post-Incident Tasks

### Immediate (within 24 hours)
- [ ] Document timeline in incident tracker
- [ ] Create postmortem draft
- [ ] Identify action items

### Follow-up
- [ ] Root cause analysis
- [ ] Implement preventive measures
- [ ] Update this runbook with learnings

## Related Runbooks
- [Related runbook 1]
- [Related runbook 2]

## References
- Documentation: [links]
- Architecture diagrams: [links]
- Previous incidents: [links]

---
**Runbook maintained by**: [Team]
**Review cadence**: Quarterly
**Next review**: YYYY-MM-DD
```

### 3.2 Inference Latency Runbook

Create `runbooks/inference/inference-latency.md`:

```markdown
# Runbook: Inference Latency SLO Breach

**Alert Name**: `InferenceLatencyBurnRateCritical` / `InferenceLatencyBurnRateHigh`
**Severity**: Critical (fast burn) / High (moderate burn)
**Team**: ML Platform
**Last Updated**: 2025-01-15

## Overview
The inference service P95 latency has exceeded the 300ms SLO threshold, consuming error budget faster than acceptable. At critical burn rates (14.4x), the monthly error budget will be exhausted in < 6 hours.

## Impact
- **User Impact**: Slow API responses, timeouts, degraded user experience
- **Business Impact**: SLA breach, potential customer churn, revenue loss
- **Scope**: Affects all inference API users

## Symptoms
- Grafana SLO dashboard shows red latency panels
- P95 latency > 300ms sustained
- User complaints about slow responses
- Increased client-side timeouts
- Error budget consumption chart trending toward zero

## Triage Steps (5 minutes)

### 1. Verify the Alert
- [ ] Check Grafana SLO dashboard: http://grafana:3000/d/inference-slo
- [ ] Confirm P95 latency in Prometheus:
  ```promql
  histogram_quantile(0.95, rate(inference_request_duration_seconds_bucket[5m]))
  ```
- [ ] Check recent deployments: `kubectl rollout history deployment/inference-gateway`

### 2. Assess Scope
- [ ] All instances affected or subset?
  ```promql
  histogram_quantile(0.95, rate(inference_request_duration_seconds_bucket[5m])) by (instance)
  ```
- [ ] Traffic volume normal or spiking?
  ```promql
  rate(inference_requests_total[5m])
  ```
- [ ] Error rate also elevated?
  ```promql
  rate(inference_requests_total{status=~"5.."}[5m])
  ```

### 3. Quick Checks
- [ ] **GPU utilization**: Are GPUs saturated?
  ```promql
  inference_gpu_utilization_percent
  ```
- [ ] **CPU/Memory**: Resource constraints?
  ```promql
  rate(container_cpu_usage_seconds_total{pod=~"inference-gateway.*"}[5m])
  ```
- [ ] **Feature store**: Is feature fetching slow?
  ```promql
  histogram_quantile(0.95, rate(feature_fetch_duration_seconds_bucket[5m]))
  ```
- [ ] **Model loading**: Recent model loading issues?
  ```promql
  model_load_errors_total
  ```

## Investigation

### Prometheus Queries

```promql
# Latency breakdown by endpoint
histogram_quantile(0.95,
  rate(inference_request_duration_seconds_bucket[5m])
) by (endpoint)

# Latency by model
histogram_quantile(0.95,
  rate(inference_request_duration_seconds_bucket[5m])
) by (model_name)

# Request rate
sum(rate(inference_requests_total[5m]))

# GPU queue depth (if instrumented)
inference_gpu_queue_depth

# Batch size
inference_batch_size

# Model inference time
histogram_quantile(0.95, rate(model_inference_duration_seconds_bucket[5m]))
```

### Grafana Dashboards
- **Primary**: SLO Dashboard - http://grafana:3000/d/inference-slo
- **Secondary**: Inference Service Dashboard - http://grafana:3000/d/inference-service
- **Infrastructure**: GPU Utilization - http://grafana:3000/d/gpu-metrics

### Log Queries (LogQL)

```logql
# Slow requests (> 1 second)
{service="inference-gateway", level="info"}
  | json
  | duration > 1s
  | line_format "{{.endpoint}} took {{.duration}}"

# Feature fetch errors
{service="inference-gateway", level="error"} |= "feature_fetch"

# GPU OOM errors
{service="inference-gateway", level="error"} |= "CUDA out of memory"

# Model loading slowness
{service="inference-gateway", level="warn"} |= "model_load_slow"
```

### Common Root Causes

#### 1. GPU Saturation
**Symptoms**: GPU utilization at 95-100%, queue depth growing
**Identification**:
```promql
inference_gpu_utilization_percent > 95
inference_gpu_queue_depth > 100
```
**Cause**: Traffic spike or inefficient batching

#### 2. Feature Store Latency
**Symptoms**: Feature fetch time elevated
**Identification**:
```promql
histogram_quantile(0.95, rate(feature_fetch_duration_seconds_bucket[5m])) > 0.1
```
**Cause**: Feature store degradation, cache misses, database slow

#### 3. Model Size / Complexity
**Symptoms**: Model inference time elevated after deployment
**Identification**:
```promql
histogram_quantile(0.95, rate(model_inference_duration_seconds_bucket[5m])) > 0.2
```
**Cause**: Recently deployed larger/complex model

#### 4. Resource Contention
**Symptoms**: CPU throttling, memory pressure
**Identification**:
```bash
kubectl top pods -l app=inference-gateway
kubectl describe pod <pod-name> | grep -A 5 "Conditions"
```
**Cause**: Under-provisioned resources

#### 5. Traffic Spike
**Symptoms**: Request rate 2-3x normal
**Identification**:
```promql
rate(inference_requests_total[5m]) >
  2 * avg_over_time(rate(inference_requests_total[5m])[1h:5m])
```
**Cause**: Marketing campaign, DDoS, client retry storm

## Mitigation

### Immediate Actions (< 15 minutes)

#### If Recent Deployment (within last 2 hours):
```bash
# 1. Check deployment time
kubectl rollout history deployment/inference-gateway

# 2. Rollback to previous version
kubectl rollout undo deployment/inference-gateway

# 3. Monitor latency recovery
watch 'kubectl get pods -l app=inference-gateway'

# 4. Verify rollback helped (check Grafana)
```

#### If GPU Saturation:
```bash
# 1. Scale up replicas immediately
kubectl scale deployment/inference-gateway --replicas=10

# 2. Verify new pods are running
kubectl get pods -l app=inference-gateway -w

# 3. Monitor latency improvement (should see relief in 2-3 minutes)
```

#### If Feature Store Issues:
```bash
# 1. Check feature store health
curl http://feature-store:8080/health

# 2. Increase feature cache TTL (temporary mitigation)
kubectl set env deployment/inference-gateway FEATURE_CACHE_TTL=600

# 3. Scale feature store if needed
kubectl scale deployment/feature-store --replicas=5

# 4. Consider serving with cached features only (degraded mode)
kubectl set env deployment/inference-gateway FEATURE_FETCH_TIMEOUT=100ms
```

#### If Traffic Spike:
```bash
# 1. Verify traffic source
# Check Grafana for client IPs / user agents

# 2. If legitimate traffic, scale aggressively
kubectl scale deployment/inference-gateway --replicas=20

# 3. If attack, implement rate limiting
kubectl apply -f rate-limit-policy.yaml

# 4. Alert security team if DDoS suspected
```

### Rollback Procedure

```bash
# Full rollback procedure
# 1. Identify current and previous versions
kubectl rollout history deployment/inference-gateway

# 2. Rollback
kubectl rollout undo deployment/inference-gateway

# 3. Wait for rollout
kubectl rollout status deployment/inference-gateway

# 4. Verify health
for pod in $(kubectl get pods -l app=inference-gateway -o name); do
  kubectl exec $pod -- curl -s http://localhost:8080/health
done

# 5. Check metrics (wait 5 minutes for data)
# Verify P95 latency returned to < 300ms in Grafana
```

### Scaling Response

```bash
# Horizontal scaling
kubectl scale deployment/inference-gateway --replicas=15

# If Horizontal Pod Autoscaler (HPA) exists, check current scaling
kubectl get hpa inference-gateway

# Temporarily increase HPA max replicas if needed
kubectl patch hpa inference-gateway -p '{"spec":{"maxReplicas":30}}'

# Vertical scaling (requires pod restart)
# Increase GPU resources if available
kubectl set resources deployment/inference-gateway \
  -c inference-container \
  --limits=nvidia.com/gpu=2
```

## Escalation

### When to Escalate
- Latency not improving after 20 minutes of mitigation
- Root cause unclear
- Requires infrastructure changes (GPU nodes, etc.)
- Feature store or dependencies need involvement

### Escalation Path
1. **Primary**: ML Platform On-Call - @ml-platform-oncall - [PagerDuty auto-escalates]
2. **Secondary**: ML Platform Team Lead - @sarah-ml-lead
3. **Manager**: Engineering Manager - @john-eng-manager

### External Dependencies
- **Feature Store Team**: @data-eng-oncall (if feature store issues)
- **Platform Team**: @platform-oncall (if Kubernetes/infrastructure issues)
- **Cloud Provider**: [AWS/GCP support case process for GPU node issues]

## Post-Incident Tasks

### Immediate (within 24 hours)
- [ ] Document incident timeline in Jira: [create incident ticket]
- [ ] Calculate actual SLO burn and remaining error budget
- [ ] Create postmortem draft (template in `incidents/templates/`)
- [ ] Identify immediate action items

### Follow-up (within 1 week)
- [ ] Complete root cause analysis
- [ ] Review alert thresholds (were they appropriate?)
- [ ] Implement monitoring improvements
- [ ] Capacity planning review if scaling was needed
- [ ] Update load testing scenarios
- [ ] Runbook improvements based on learnings

## Related Runbooks
- [Inference Error Rate](./inference-error-rate.md)
- [GPU Out of Memory](./gpu-oom.md)
- [Feature Store Outage](./feature-store-outage.md)

## References
- **SLO Definition**: docs/slos/inference-service-slo.md
- **Architecture**: docs/architecture/inference-service.md
- **Deployment Process**: docs/deployment/inference-deployment.md
- **Previous Incidents**:
  - INC-2024-087: Latency spike from model size increase
  - INC-2024-112: Traffic spike from retry storm

---
**Runbook maintained by**: ML Platform Team
**Review cadence**: Quarterly
**Next review**: 2025-04-15
```

### 3.3 Inference Error Rate Runbook

Create `runbooks/inference/inference-error-rate.md`:

```markdown
# Runbook: Inference Error Rate High

**Alert Name**: `InferenceErrorRateCritical` / `InferenceErrorRateHigh`
**Severity**: Critical (SLO burn rate > 14.4x) / High (> 5% errors)
**Team**: ML Platform
**Last Updated**: 2025-01-15

## Overview
The inference service is returning HTTP 5xx errors at an elevated rate, indicating service degradation or outage.

## Impact
- **User Impact**: Failed predictions, errors in client applications
- **Business Impact**: Loss of functionality, SLA breach, user trust degradation
- **Scope**: Percentage of users affected depends on error rate (5-100%)

## Symptoms
- Spike in HTTP 5xx responses
- Error budget consumption alert
- Client applications logging API failures
- User-reported "service unavailable" errors
- Increased retry traffic

## Triage Steps (5 minutes)

### 1. Verify the Alert
- [ ] Check error rate in Grafana: http://grafana:3000/d/inference-slo
- [ ] Confirm in Prometheus:
  ```promql
  rate(inference_requests_total{status=~"5.."}[5m]) /
  rate(inference_requests_total[5m])
  ```
- [ ] Check pod status: `kubectl get pods -l app=inference-gateway`

### 2. Identify Error Type
- [ ] What HTTP status codes? (500, 502, 503, 504)
  ```promql
  sum by (status) (rate(inference_requests_total{status=~"5.."}[5m]))
  ```
- [ ] Which endpoints failing?
  ```promql
  sum by (endpoint) (rate(inference_requests_total{status=~"5.."}[5m]))
  ```

### 3. Check Service Health
- [ ] Pods running? `kubectl get pods -l app=inference-gateway`
- [ ] Recent crashes? `kubectl get events --sort-by='.lastTimestamp' | head -20`
- [ ] Pod logs showing errors? `kubectl logs -l app=inference-gateway --tail=100 | grep ERROR`

## Investigation

### Prometheus Queries

```promql
# Error rate by status code
sum by (status) (rate(inference_requests_total{status=~"5.."}[5m]))

# Error rate by endpoint
sum by (endpoint) (rate(inference_requests_total{status=~"5.."}[5m]))

# Pod restart count
kube_pod_container_status_restarts_total{pod=~"inference-gateway.*"}

# Memory usage (OOM indicator)
container_memory_usage_bytes{pod=~"inference-gateway.*"} /
container_spec_memory_limit_bytes{pod=~"inference-gateway.*"}
```

### Log Queries

```logql
# All ERROR level logs
{service="inference-gateway", level="error"}
  | json
  | line_format "{{.timestamp}} {{.message}}"

# Specific error patterns
{service="inference-gateway"} |= "exception" or "error" or "failed"

# OOM errors
{service="inference-gateway"} |= "OutOfMemory" or "OOM"

# Model loading errors
{service="inference-gateway"} |= "model_load_error"

# Feature store errors
{service="inference-gateway"} |= "FeatureStoreException"
```

### Common Root Causes

#### 1. Service Pods Crash Looping
**Symptoms**: Pods constantly restarting
**Identification**:
```bash
kubectl get pods -l app=inference-gateway
# Look for RESTARTS > 5, STATUS = CrashLoopBackOff
```
**Cause**: OOM, initialization failure, bad configuration

#### 2. Out of Memory (OOM)
**Symptoms**: Pods killed by Kubernetes, 502/503 errors
**Identification**:
```bash
kubectl describe pod <pod-name> | grep -A 10 "Last State"
# Look for "OOMKilled"
```
**Cause**: Memory leak, large model, batch size too large

#### 3. Feature Store Down/Unreachable
**Symptoms**: Consistent errors, logs show feature fetch failures
**Identification**:
```logql
{service="inference-gateway", level="error"} |= "FeatureNotFound" or "FeatureStoreTimeout"
```
**Cause**: Feature store deployment, network issue, database problem

#### 4. Model Loading Failure
**Symptoms**: Errors on startup or after deployment
**Identification**:
```logql
{service="inference-gateway", level="error"} |= "model_load"
```
**Cause**: Corrupted model artifact, incompatible version, missing files

#### 5. GPU Out of Memory
**Symptoms**: CUDA errors in logs
**Identification**:
```logql
{service="inference-gateway", level="error"} |= "CUDA" or "out of memory"
```
**Cause**: Model too large, batch size too big

## Mitigation

### Immediate Actions

#### If Pods Crash Looping:
```bash
# 1. Check pod logs for crash reason
kubectl logs <failing-pod> --previous

# 2. If recent deployment, rollback
kubectl rollout undo deployment/inference-gateway

# 3. If configuration issue, revert config
kubectl rollout undo deployment/inference-gateway

# 4. Monitor recovery
kubectl get pods -l app=inference-gateway -w
```

#### If OOM Issues:
```bash
# 1. Increase memory limits (temporary)
kubectl set resources deployment/inference-gateway \
  --limits=memory=8Gi \
  --requests=memory=4Gi

# 2. Reduce batch size (if configurable)
kubectl set env deployment/inference-gateway MAX_BATCH_SIZE=16

# 3. Scale horizontally to reduce per-pod load
kubectl scale deployment/inference-gateway --replicas=20

# 4. Restart pods to clear memory
kubectl rollout restart deployment/inference-gateway
```

#### If Feature Store Issues:
```bash
# 1. Check feature store health
kubectl get pods -l app=feature-store
curl http://feature-store:8080/health

# 2. Enable degraded mode (use cached features only)
kubectl set env deployment/inference-gateway FEATURE_FALLBACK_MODE=cache_only

# 3. Alert feature store team
# @data-eng-oncall in #incidents channel

# 4. Monitor error rate improvement
```

#### If Model Loading Issues:
```bash
# 1. Check model registry connectivity
kubectl exec -it <pod> -- curl http://model-registry:8080/health

# 2. Verify model artifacts exist
kubectl exec -it <pod> -- ls -lh /models/

# 3. Rollback to previous known-good model version
kubectl set env deployment/inference-gateway MODEL_VERSION=v1.2.3

# 4. Restart pods
kubectl rollout restart deployment/inference-gateway
```

### Emergency Circuit Breaker

If errors > 50% and root cause unclear, enable circuit breaker to protect downstream:

```bash
# Enable circuit breaker to fail fast
kubectl set env deployment/inference-gateway CIRCUIT_BREAKER_ENABLED=true
kubectl set env deployment/inference-gateway CIRCUIT_BREAKER_THRESHOLD=0.5

# This will return 503 immediately instead of attempting requests
```

## Escalation

### When to Escalate
- Error rate > 25% for > 15 minutes
- Service completely down (100% errors)
- Root cause requires other team involvement
- Cannot resolve within 30 minutes

### Escalation Path
1. **Primary**: ML Platform On-Call - @ml-platform-oncall
2. **Feature Store Team**: @data-eng-oncall (if feature store issue)
3. **Platform Team**: @platform-oncall (if infrastructure issue)
4. **Incident Commander**: @eng-manager (if duration > 1 hour)

## Post-Incident Tasks

### Immediate
- [ ] Document timeline and actions taken
- [ ] Quantify error budget consumption
- [ ] Create postmortem ticket

### Follow-up
- [ ] Root cause analysis
- [ ] Implement preventive measures (health checks, retries, circuit breakers)
- [ ] Review resource limits and requests
- [ ] Update monitoring/alerting
- [ ] Chaos engineering tests to validate resilience

## Related Runbooks
- [Inference Latency](./inference-latency.md)
- [Feature Store Outage](./feature-store-outage.md)
- [Model Loading Failure](./model-loading-failure.md)

## References
- **Error Budget Policy**: docs/slos/error-budget-policy.md
- **Incident Response Process**: docs/on-call/incident-response.md

---
**Runbook maintained by**: ML Platform Team
**Review cadence**: Quarterly
**Next review**: 2025-04-15
```

### 3.4 Feature Drift Runbook

Create `runbooks/ml-operations/feature-drift.md`:

```markdown
# Runbook: Feature Drift Detected

**Alert Name**: `FeatureDriftDetected`
**Severity**: High (PSI > 0.2)
**Team**: ML Engineering + Data Engineering
**Last Updated**: 2025-01-15

## Overview
Population Stability Index (PSI) for a feature has exceeded 0.2, indicating the feature distribution in production has shifted significantly from the training distribution.

## Impact
- **Model Impact**: Prediction quality may degrade
- **Business Impact**: Potential revenue loss from poor predictions
- **Scope**: Depends on feature importance and drift severity

## Symptoms
- PSI metric > 0.2 for specific feature
- Model performance metrics declining (if ground truth available)
- Feature distribution charts in Grafana show clear shift
- Increased prediction uncertainty

## Triage Steps (15 minutes)

### 1. Verify Drift
- [ ] Check ML Monitoring dashboard: http://grafana:3000/d/ml-monitoring
- [ ] Confirm PSI value:
  ```promql
  model_drift_psi{metric_type="feature", feature_name="<feature>"}
  ```
- [ ] Review feature distribution histogram

### 2. Assess Impact
- [ ] What is feature importance? (Check model documentation)
- [ ] Has model performance degraded?
  ```promql
  model_performance_metric{metric="auc_roc"}
  ```
- [ ] How severe is drift?
  - PSI 0.1-0.2: Minor (monitor)
  - PSI 0.2-0.25: Medium (investigate)
  - PSI > 0.25: Major (action required)

### 3. Identify Cause
- [ ] Recent data pipeline changes?
- [ ] Upstream data source changes?
- [ ] Real-world distribution shift (legitimate)?

## Investigation

### Prometheus Queries

```promql
# PSI over time
model_drift_psi{feature_name="<feature>"}

# Feature statistics
feature_statistics{feature_name="<feature>", statistic="mean"}
feature_statistics{feature_name="<feature>", statistic="std"}

# Prediction performance trend
model_performance_metric{metric="auc_roc"}
```

### Data Analysis

```python
# Connect to feature store and analyze distribution
import pandas as pd
from feature_store import FeatureStore

fs = FeatureStore()

# Get current production distribution
prod_dist = fs.get_feature_distribution(
    feature_name="<feature>",
    start_date="2025-01-01",
    end_date="2025-01-15"
)

# Compare to training distribution
train_dist = fs.get_training_distribution(
    feature_name="<feature>",
    model_version="v1.5.0"
)

# Calculate detailed PSI
from scipy.stats import chisquare
psi = calculate_psi(train_dist, prod_dist)

# Visualize
import matplotlib.pyplot as plt
plt.hist([train_dist, prod_dist], label=['Training', 'Production'])
plt.legend()
plt.savefig('drift_analysis.png')
```

### Common Root Causes

#### 1. Data Pipeline Bug
**Symptoms**: Sudden drift, feature values illogical
**Identification**: Check feature engineering pipeline logs
**Action**: Fix pipeline, backfill data if possible

#### 2. Upstream Data Source Change
**Symptoms**: Drift coincides with vendor/partner integration change
**Identification**: Review data source changelog
**Action**: Adapt feature engineering or switch source

#### 3. Real-World Distribution Shift
**Symptoms**: Gradual drift, feature values reasonable
**Identification**: Correlate with business metrics (new markets, seasonality)
**Action**: Model retraining required

#### 4. Feature Engineering Code Change
**Symptoms**: Drift after deployment
**Identification**: Review recent feature engineering commits
**Action**: Rollback or retrain with new definition

## Mitigation

### Immediate Actions (< 1 hour)

#### Investigate Data Pipeline:
```bash
# Check recent feature engineering job runs
kubectl logs -l app=feature-engineering --since=24h | grep ERROR

# Verify data sources
python scripts/validate_data_sources.py

# Check for data quality issues
python scripts/feature_quality_check.py --feature=<feature_name>
```

#### Assess Model Performance:
```python
# Run ad-hoc model evaluation on recent data
python scripts/model_eval.py \
  --model-version=v1.5.0 \
  --date-range=last-7-days \
  --output=drift_impact_report.json
```

#### Decision Tree:
- **If PSI < 0.25 AND performance not degraded**: Monitor for 24 hours
- **If PSI > 0.25 OR performance degraded > 5%**: Escalate to ML Engineering for retraining
- **If data quality issue identified**: Fix pipeline urgently

### Medium-Term Actions (< 1 week)

#### Plan Model Retraining:
```bash
# Create retraining task
python scripts/create_training_job.py \
  --model=fraud_detection \
  --reason="feature_drift_user_age" \
  --priority=high

# Estimated timeline: 3-5 days
# 1. Data collection: 1 day
# 2. Training: 1-2 days
# 3. Validation: 1 day
# 4. Deployment: 1 day
```

#### Implement Drift Mitigation:
- **Option 1**: Retrain with recent data
- **Option 2**: Apply distribution correction (if appropriate)
- **Option 3**: Remove/replace drifted feature
- **Option 4**: Ensemble with new model trained on recent data

## Escalation

### When to Escalate
- PSI > 0.25 sustained for > 24 hours
- Model performance degraded > 10%
- Feature critical to model (high importance)
- Data pipeline issue requires Data Engineering

### Escalation Path
1. **ML Engineering Team Lead**: @sarah-ml-lead
2. **Data Engineering** (if pipeline issue): @data-eng-team
3. **Product Owner** (if retraining required): @product-ml

## Post-Incident Tasks

### Immediate
- [ ] Document drift episode and investigation
- [ ] Update model monitoring dashboard
- [ ] Create retraining ticket if needed

### Follow-up
- [ ] Implement automated drift response
- [ ] Improve data quality monitoring upstream
- [ ] Add distribution checks to feature engineering pipeline
- [ ] Update model retraining schedule if patterns emerging
- [ ] Consider online learning if appropriate

## Related Runbooks
- [Prediction Drift](./prediction-drift.md)
- [Model Performance Degradation](./model-performance-degradation.md)
- [Data Quality Issues](./data-quality-issues.md)

## References
- **Drift Monitoring Setup**: docs/ml-monitoring/drift-detection.md
- **PSI Calculation**: docs/ml-monitoring/psi-methodology.md
- **Retraining Process**: docs/ml-ops/model-retraining.md

---
**Runbook maintained by**: ML Engineering Team
**Review cadence**: Quarterly
**Next review**: 2025-04-15
```

### 3.5 Linking Runbooks in Alerts

Update Prometheus alert rules to include runbook links:

```yaml
# Example alert with runbook link
- alert: InferenceLatencyBurnRateCritical
  # ... alert configuration ...
  annotations:
    summary: "CRITICAL: Inference latency burn rate extremely high"
    description: "..."
    runbook_url: "https://runbooks.example.com/inference-latency"  # HTTP link
    runbook_file: "file:///runbooks/inference/inference-latency.md"  # Local file
    dashboard_url: "http://grafana:3000/d/inference-slo"
```

**Best Practice**: Store runbooks in Git repository and deploy alongside monitoring stack:

```bash
# Deploy runbooks as ConfigMap for easy access
kubectl create configmap runbooks \
  --from-file=runbooks/ \
  --namespace=monitoring

# Mount in Grafana pod for inline viewing
# Add to Grafana deployment:
volumes:
  - name: runbooks
    configMap:
      name: runbooks
volumeMounts:
  - name: runbooks
    mountPath: /etc/grafana/runbooks
```

## Part 4: Incident Simulation

### 4.1 Simulation Framework Setup

Create `scripts/incident-simulation.sh`:

```bash
#!/bin/bash
# Incident Simulation Framework
# Purpose: Trigger realistic production incidents for runbook practice

set -e

NAMESPACE="monitoring"
DEPLOYMENT="inference-gateway"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to wait for alert to fire
wait_for_alert() {
    local alert_name=$1
    local timeout=${2:-300}  # 5 minutes default

    log_info "Waiting for alert '$alert_name' to fire (timeout: ${timeout}s)..."

    local elapsed=0
    while [ $elapsed -lt $timeout ]; do
        # Check Alertmanager API for firing alert
        if curl -s http://localhost:9093/api/v2/alerts | grep -q "$alert_name"; then
            log_info "✓ Alert '$alert_name' is FIRING!"
            return 0
        fi
        sleep 10
        elapsed=$((elapsed + 10))
        echo -n "."
    done

    log_error "✗ Alert did not fire within ${timeout}s"
    return 1
}

# Function to check Slack notification (mock)
check_slack_notification() {
    log_info "Check Slack #ai-infra-incidents channel for alert notification"
    log_warn "Manual verification required: Did you receive Slack notification?"
    read -p "Press Enter when confirmed..."
}

# Cleanup function
cleanup() {
    log_info "Cleaning up simulation artifacts..."
    kubectl rollout undo deployment/$DEPLOYMENT -n $NAMESPACE 2>/dev/null || true
    kubectl delete configmap incident-simulation -n $NAMESPACE 2>/dev/null || true
}

trap cleanup EXIT

echo "======================================"
echo "   Incident Simulation Framework"
echo "======================================"
echo ""
echo "Available Scenarios:"
echo "  1. Latency Spike (Scenario A)"
echo "  2. Feature Store Outage (Scenario B)"
echo "  3. Error Rate Spike (Scenario C)"
echo "  4. Data Drift (Scenario D)"
echo "  5. GPU OOM (Scenario E)"
echo ""
read -p "Select scenario (1-5): " scenario

case $scenario in
    1) source ./scenarios/latency-spike.sh ;;
    2) source ./scenarios/feature-store-outage.sh ;;
    3) source ./scenarios/error-rate-spike.sh ;;
    4) source ./scenarios/data-drift.sh ;;
    5) source ./scenarios/gpu-oom.sh ;;
    *) log_error "Invalid scenario"; exit 1 ;;
esac
```

### 4.2 Scenario A: Latency Spike Simulation

Create `scripts/scenarios/latency-spike.sh`:

```bash
#!/bin/bash
# Scenario A: Inference Latency Spike
# Simulates sudden latency degradation requiring immediate response

echo "========================================"
echo "  Scenario A: Latency Spike"
echo "========================================"
echo ""
echo "This scenario will:"
echo "  1. Inject artificial latency into inference service"
echo "  2. Generate load to trigger SLO burn rate alert"
echo "  3. Require you to follow the latency runbook"
echo "  4. Document timeline and mitigation steps"
echo ""
read -p "Press Enter to start simulation..."

# Create incident directory
INCIDENT_ID="INC-$(date +%Y%m%d-%H%M%S)-latency"
INCIDENT_DIR="incidents/${INCIDENT_ID}"
mkdir -p "$INCIDENT_DIR"

log_info "Incident ID: $INCIDENT_ID"
log_info "Incident directory: $INCIDENT_DIR"

# Record start time
START_TIME=$(date -Iseconds)
echo "# Incident Timeline: Latency Spike" > "$INCIDENT_DIR/timeline.md"
echo "" >> "$INCIDENT_DIR/timeline.md"
echo "**Incident ID**: $INCIDENT_ID" >> "$INCIDENT_DIR/timeline.md"
echo "**Start Time**: $START_TIME" >> "$INCIDENT_DIR/timeline.md"
echo "" >> "$INCIDENT_DIR/timeline.md"
echo "## Timeline" >> "$INCIDENT_DIR/timeline.md"
echo "" >> "$INCIDENT_DIR/timeline.md"
echo "| Time | Event | Action Taken | Notes |" >> "$INCIDENT_DIR/timeline.md"
echo "|------|-------|--------------|-------|" >> "$INCIDENT_DIR/timeline.md"
echo "| $START_TIME | Simulation started | Injected 500ms latency | - |" >> "$INCIDENT_DIR/timeline.md"

# Step 1: Inject latency
log_info "Step 1: Injecting artificial latency (500ms) into inference service..."

kubectl set env deployment/$DEPLOYMENT \
    ARTIFICIAL_LATENCY_MS=500 \
    -n $NAMESPACE

log_info "Waiting for deployment rollout..."
kubectl rollout status deployment/$DEPLOYMENT -n $NAMESPACE

# Step 2: Generate load
log_info "Step 2: Generating load to trigger alerts..."

# Install hey if not available
if ! command -v hey &> /dev/null; then
    log_warn "'hey' not found, installing..."
    go install github.com/rakyll/hey@latest
fi

# Start load generation in background
SERVICE_URL="http://localhost:8000/predict"
log_info "Sending 100 req/s for 10 minutes to $SERVICE_URL"

hey -z 10m -q 100 -c 10 \
    -m POST \
    -H "Content-Type: application/json" \
    -d '{"features": {"user_age": 25, "account_balance": 1000}}' \
    $SERVICE_URL > "$INCIDENT_DIR/load-test-results.txt" 2>&1 &

LOAD_PID=$!
log_info "Load generation started (PID: $LOAD_PID)"

# Step 3: Wait for alert
log_info "Step 3: Monitoring for latency alert to fire..."
log_warn "Expected: InferenceLatencyBurnRateCritical or InferenceLatencyBurnRateHigh"

if wait_for_alert "InferenceLatency" 300; then
    ALERT_TIME=$(date -Iseconds)
    echo "| $ALERT_TIME | Alert FIRED | InferenceLatencyBurnRate alert triggered | Check Grafana dashboard |" >> "$INCIDENT_DIR/timeline.md"

    log_info "✓ Alert successfully triggered!"
    log_info ""
    log_info "==================== YOUR TURN ===================="
    log_info "ALERT FIRED: Inference Latency SLO Burn Rate High"
    log_info ""
    log_info "Follow the runbook: runbooks/inference/inference-latency.md"
    log_info ""
    log_info "Tasks:"
    log_info "  1. Check Grafana SLO dashboard: http://localhost:3000/d/inference-slo"
    log_info "  2. Verify P95 latency > 300ms"
    log_info "  3. Check deployment history: kubectl rollout history deployment/$DEPLOYMENT"
    log_info "  4. DECISION: Rollback or scale?"
    log_info "  5. Execute mitigation from runbook"
    log_info "  6. Document your actions in $INCIDENT_DIR/timeline.md"
    log_info ""
    log_info "==================================================="

    # Provide helper commands
    echo ""
    echo "Useful commands:"
    echo "  # Check current P95 latency"
    echo "  curl -s 'http://localhost:9090/api/v1/query?query=histogram_quantile(0.95,rate(inference_request_duration_seconds_bucket[5m]))' | jq '.data.result[0].value[1]'"
    echo ""
    echo "  # View deployment history"
    echo "  kubectl rollout history deployment/$DEPLOYMENT -n $NAMESPACE"
    echo ""
    echo "  # Rollback deployment"
    echo "  kubectl rollout undo deployment/$DEPLOYMENT -n $NAMESPACE"
    echo ""
    echo "  # Check alert status"
    echo "  curl -s http://localhost:9093/api/v2/alerts | jq '.[] | select(.labels.alertname | contains(\"Latency\"))'"
    echo ""

    # Wait for user to resolve
    read -p "Press Enter when you have resolved the incident..."

    RESOLVE_TIME=$(date -Iseconds)
    echo "| $RESOLVE_TIME | Incident RESOLVED | User completed mitigation | Document root cause |" >> "$INCIDENT_DIR/timeline.md"

    # Verify resolution
    log_info "Verifying incident resolution..."

    # Check if latency returned to normal
    CURRENT_P95=$(curl -s 'http://localhost:9090/api/v1/query?query=histogram_quantile(0.95,rate(inference_request_duration_seconds_bucket[5m]))' | jq -r '.data.result[0].value[1]')

    if (( $(echo "$CURRENT_P95 < 0.3" | bc -l) )); then
        log_info "✓ Latency recovered: P95 = ${CURRENT_P95}s (target: < 0.3s)"
        echo "| $RESOLVE_TIME | Verification | P95 latency: ${CURRENT_P95}s | Within SLO |" >> "$INCIDENT_DIR/timeline.md"
    else
        log_warn "✗ Latency still elevated: P95 = ${CURRENT_P95}s"
        echo "| $RESOLVE_TIME | Verification | P95 latency: ${CURRENT_P95}s | ABOVE SLO |" >> "$INCIDENT_DIR/timeline.md"
    fi

else
    log_error "Alert did not fire. Check Prometheus alert rules and Alertmanager configuration."
    exit 1
fi

# Stop load generation
kill $LOAD_PID 2>/dev/null || true
wait $LOAD_PID 2>/dev/null || true

# Step 4: Post-incident tasks
echo ""
log_info "Step 4: Post-Incident Tasks"
log_info ""
log_info "Complete the following:"
log_info "  1. Fill out post-incident review: $INCIDENT_DIR/post-incident-review.md"
log_info "  2. Calculate MTTD (Mean Time To Detect): Alert time - Start time"
log_info "  3. Calculate MTTR (Mean Time To Resolve): Resolve time - Alert time"
log_info "  4. Document root cause analysis"
log_info "  5. Create action items for prevention"
log_info ""

# Generate post-incident review template
cat > "$INCIDENT_DIR/post-incident-review.md" <<EOF
# Post-Incident Review: Latency Spike

**Incident ID**: $INCIDENT_ID
**Date**: $(date +%Y-%m-%d)
**Severity**: [Critical/High/Medium/Low]
**Duration**: [Calculate: Resolve time - Start time]
**Incident Commander**: [Your name]

## Summary
[Brief 2-3 sentence summary of what happened]

## Impact
- **Users Affected**: [percentage or number]
- **Revenue Impact**: [if applicable]
- **SLO Impact**: [error budget consumed]

## Timeline
[See timeline.md for detailed timeline]

**Key Milestones**:
- **$START_TIME**: Incident began (latency injection)
- **[FILL IN]**: Alert fired
- **[FILL IN]**: Mitigation started
- **[FILL IN]**: Incident resolved

## Detection
- **MTTD (Mean Time To Detect)**: [Calculate: Alert time - Incident start]
- **Detection Method**: Prometheus multi-window burn rate alert
- **Alert Effectiveness**: [Did alert fire appropriately? Too early/late?]

## Response & Mitigation
- **MTTR (Mean Time To Resolve)**: [Calculate: Resolve time - Alert time]
- **Actions Taken**:
  1. [List actions from timeline]
  2. [...]
- **Runbook Used**: runbooks/inference/inference-latency.md
- **Runbook Effectiveness**: [Was runbook helpful? Any gaps?]

## Root Cause Analysis

### What Happened
[Detailed explanation of the root cause]

In this simulation: Artificial 500ms latency was injected via environment variable.

### Why It Happened
[Why did the root cause occur?]

In a real scenario, this could be due to:
- Recently deployed larger ML model
- Feature store database slowdown
- GPU saturation from traffic spike
- Upstream dependency latency

### Contributing Factors
- [Factor 1]
- [Factor 2]

## What Went Well
1. Alert fired within expected time
2. Runbook provided clear guidance
3. [Add more based on your experience]

## What Could Be Improved
1. [Improvement 1]
2. [Improvement 2]
3. [Add based on your experience]

## Action Items

| Action | Owner | Priority | Due Date | Status |
|--------|-------|----------|----------|--------|
| [Example: Add pre-deployment latency testing] | [Team] | High | [Date] | Open |
| [Example: Improve alert notification clarity] | [Team] | Medium | [Date] | Open |
| [Add more action items] | | | | |

## Lessons Learned
1. [Lesson 1]
2. [Lesson 2]
3. [Lesson 3]

## Related Incidents
- [Link to similar past incidents if any]

---
**Review Date**: [Schedule review meeting date]
**Attendees**: [List attendees for postmortem meeting]
**Follow-up**: [Schedule follow-up for action items]
EOF

log_info "✓ Post-incident review template created: $INCIDENT_DIR/post-incident-review.md"
log_info ""
log_info "Simulation complete! Review your incident artifacts in $INCIDENT_DIR/"
```

### 4.3 Scenario B: Feature Store Outage Simulation

Create `scripts/scenarios/feature-store-outage.sh`:

```bash
#!/bin/bash
# Scenario B: Feature Store Outage
# Simulates feature store failure causing inference errors

echo "========================================"
echo "  Scenario B: Feature Store Outage"
echo "========================================"
echo ""
echo "This scenario will:"
echo "  1. Simulate feature store unavailability"
echo "  2. Trigger FeatureNotFound errors"
echo "  3. Fire log-based alerts"
echo "  4. Require degraded mode activation"
echo ""
read -p "Press Enter to start simulation..."

# Create incident directory
INCIDENT_ID="INC-$(date +%Y%m%d-%H%M%S)-feature-store"
INCIDENT_DIR="incidents/${INCIDENT_ID}"
mkdir -p "$INCIDENT_DIR"

log_info "Incident ID: $INCIDENT_ID"

# Record start time
START_TIME=$(date -Iseconds)
echo "# Incident Timeline: Feature Store Outage" > "$INCIDENT_DIR/timeline.md"
echo "" >> "$INCIDENT_DIR/timeline.md"
echo "| Time | Event | Action Taken | Notes |" >> "$INCIDENT_DIR/timeline.md"
echo "|------|-------|--------------|-------|" >> "$INCIDENT_DIR/timeline.md"
echo "| $START_TIME | Simulation started | Disabled feature store | - |" >> "$INCIDENT_DIR/timeline.md"

# Step 1: Simulate feature store failure
log_info "Step 1: Simulating feature store outage..."

# Scale feature store to 0 replicas
kubectl scale deployment/feature-store --replicas=0 -n $NAMESPACE

log_info "Feature store scaled to 0 replicas"

# Step 2: Generate inference traffic
log_info "Step 2: Generating inference requests (will fail to fetch features)..."

hey -z 5m -q 50 -c 5 \
    -m POST \
    -H "Content-Type: application/json" \
    -d '{"features": {"user_age": 25}}' \
    http://localhost:8000/predict > "$INCIDENT_DIR/load-test-results.txt" 2>&1 &

LOAD_PID=$!

# Step 3: Wait for log-based alert
log_info "Step 3: Monitoring for FeatureNotFound alert..."

if wait_for_alert "FeatureNotFound" 300; then
    ALERT_TIME=$(date -Iseconds)
    echo "| $ALERT_TIME | Alert FIRED | FeatureNotFound errors high | Check logs |" >> "$INCIDENT_DIR/timeline.md"

    log_info "✓ Alert successfully triggered!"
    log_info ""
    log_info "==================== YOUR TURN ===================="
    log_info "ALERT FIRED: Feature Store Errors High"
    log_info ""
    log_info "Follow the runbook: runbooks/inference/feature-store-errors.md"
    log_info ""
    log_info "Tasks:"
    log_info "  1. Check error logs:"
    log_info "     kubectl logs -l app=inference-gateway --tail=50 | grep FeatureNotFound"
    log_info ""
    log_info "  2. Verify feature store status:"
    log_info "     kubectl get pods -l app=feature-store"
    log_info ""
    log_info "  3. DECISION: Enable degraded mode (cached features) or restore feature store?"
    log_info ""
    log_info "  4. Execute mitigation:"
    log_info "     Option A - Restore feature store:"
    log_info "       kubectl scale deployment/feature-store --replicas=3"
    log_info ""
    log_info "     Option B - Enable degraded mode:"
    log_info "       kubectl set env deployment/inference-gateway FEATURE_FALLBACK_MODE=cache_only"
    log_info ""
    log_info "  5. Document your actions in $INCIDENT_DIR/timeline.md"
    log_info ""
    log_info "==================================================="

    read -p "Press Enter when you have resolved the incident..."

    RESOLVE_TIME=$(date -Iseconds)
    echo "| $RESOLVE_TIME | Incident RESOLVED | User completed mitigation | - |" >> "$INCIDENT_DIR/timeline.md"

else
    log_error "Alert did not fire. Check Grafana log-based alert configuration."
    exit 1
fi

# Cleanup
kill $LOAD_PID 2>/dev/null || true
kubectl scale deployment/feature-store --replicas=3 -n $NAMESPACE

log_info "✓ Simulation complete!"
log_info "Review artifacts in $INCIDENT_DIR/"
```

### 4.4 Scenario C: Error Rate Spike

Create `scripts/scenarios/error-rate-spike.sh`:

```bash
#!/bin/bash
# Scenario C: Error Rate Spike
# Simulates sudden increase in 500 errors

echo "========================================"
echo "  Scenario C: Error Rate Spike"
echo "========================================"

INCIDENT_ID="INC-$(date +%Y%m%d-%H%M%S)-error-rate"
INCIDENT_DIR="incidents/${INCIDENT_ID}"
mkdir -p "$INCIDENT_DIR"

log_info "Incident ID: $INCIDENT_ID"

# Inject error rate
log_info "Injecting 30% error rate into inference service..."

kubectl set env deployment/$DEPLOYMENT \
    INJECT_ERROR_RATE=0.30 \
    -n $NAMESPACE

kubectl rollout status deployment/$DEPLOYMENT -n $NAMESPACE

# Generate load
log_info "Generating load..."

hey -z 10m -q 100 -c 10 \
    -m POST \
    -H "Content-Type: application/json" \
    -d '{"features": {"user_age": 25}}' \
    http://localhost:8000/predict > "$INCIDENT_DIR/load-test-results.txt" 2>&1 &

LOAD_PID=$!

# Monitor for alert
if wait_for_alert "InferenceErrorRate" 300; then
    log_info "✓ Alert fired: InferenceErrorRateHigh"
    log_info ""
    log_info "==================== YOUR TURN ===================="
    log_info "Follow runbook: runbooks/inference/inference-error-rate.md"
    log_info ""
    log_info "Check error logs:"
    log_info "  kubectl logs -l app=inference-gateway | grep ERROR"
    log_info ""
    log_info "Identify error cause, then:"
    log_info "  kubectl rollout undo deployment/$DEPLOYMENT"
    log_info "==================================================="

    read -p "Press Enter when resolved..."
fi

kill $LOAD_PID 2>/dev/null || true
kubectl set env deployment/$DEPLOYMENT INJECT_ERROR_RATE- -n $NAMESPACE

log_info "✓ Simulation complete!"
```

### 4.5 Scenario D: Data Drift Detection

Create `scripts/scenarios/data-drift.sh`:

```bash
#!/bin/bash
# Scenario D: Data Drift
# Simulates gradual feature distribution shift

echo "========================================"
echo "  Scenario D: Data Drift Detection"
echo "========================================"

INCIDENT_ID="INC-$(date +%Y%m%d-%H%M%S)-drift"
INCIDENT_DIR="incidents/${INCIDENT_ID}"
mkdir -p "$INCIDENT_DIR"

log_info "Incident ID: $INCIDENT_ID"

# Inject drift via altered feature distribution
log_info "Simulating feature drift by altering input distribution..."

# Create Python script to send drifted requests
cat > /tmp/drift_simulation.py <<'EOF'
import requests
import numpy as np
import time
import sys

# Original distribution: Normal(mean=35, std=10)
# Drifted distribution: Normal(mean=50, std=15)  <- Significant shift

url = "http://localhost:8000/predict"
duration = 600  # 10 minutes

start_time = time.time()
while time.time() - start_time < duration:
    # Generate drifted user_age feature
    age = int(np.random.normal(50, 15))  # Drifted from mean=35
    age = max(18, min(100, age))  # Clamp to reasonable range

    payload = {"features": {"user_age": age, "account_balance": 1000}}

    try:
        resp = requests.post(url, json=payload, timeout=5)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)

    time.sleep(0.1)  # 10 req/s

print("Drift simulation complete")
EOF

python3 /tmp/drift_simulation.py &
DRIFT_PID=$!

log_info "Sending drifted requests for 10 minutes..."
log_info "Original user_age distribution: N(35, 10)"
log_info "Drifted user_age distribution: N(50, 15)"

# Wait for drift alert (PSI calculation happens periodically)
log_info "Waiting for drift alert (may take 30-60 minutes for PSI calculation)..."

if wait_for_alert "FeatureDrift" 3600; then
    log_info "✓ Alert fired: FeatureDriftDetected"
    log_info ""
    log_info "==================== YOUR TURN ===================="
    log_info "Follow runbook: runbooks/ml-operations/feature-drift.md"
    log_info ""
    log_info "Check ML monitoring dashboard:"
    log_info "  http://localhost:3000/d/ml-monitoring"
    log_info ""
    log_info "Analyze drift:"
    log_info "  1. Review PSI value and feature distribution"
    log_info "  2. Assess model performance impact"
    log_info "  3. Determine if retraining needed"
    log_info "  4. Document decision in $INCIDENT_DIR/"
    log_info "==================================================="

    read -p "Press Enter when analysis complete..."
fi

kill $DRIFT_PID 2>/dev/null || true

log_info "✓ Simulation complete!"
```

### 4.6 Incident Documentation Template

Create `incidents/templates/incident-template.md`:

```markdown
# Incident Report: [Title]

**Incident ID**: INC-YYYYMMDD-HHMM-category
**Date**: YYYY-MM-DD
**Severity**: [Critical/High/Medium/Low]
**Status**: [Investigating/Mitigating/Resolved/Closed]
**Incident Commander**: [Name]

## Quick Summary
[1-2 sentence summary of what happened]

## Impact
- **Start Time**: YYYY-MM-DD HH:MM:SS UTC
- **End Time**: YYYY-MM-DD HH:MM:SS UTC (or "Ongoing")
- **Duration**: X hours Y minutes
- **Users Affected**: [number or percentage]
- **Services Affected**: [list services]
- **SLO Impact**: [error budget consumed]

## Timeline

| Time (UTC) | Event | Action Taken | Taken By |
|------------|-------|--------------|----------|
| HH:MM:SS | Incident began | [Description] | System |
| HH:MM:SS | Alert fired | InferenceLatencyHigh | Alertmanager |
| HH:MM:SS | Acknowledged | Opened incident channel | On-call Engineer |
| HH:MM:SS | Investigation started | Checked Grafana dashboard | On-call Engineer |
| HH:MM:SS | Root cause identified | [Description] | On-call Engineer |
| HH:MM:SS | Mitigation started | [Action] | On-call Engineer |
| HH:MM:SS | Incident resolved | [Resolution] | On-call Engineer |
| HH:MM:SS | Post-mortem scheduled | - | Incident Commander |

## Detection
- **Detection Method**: [Prometheus alert / User report / Monitoring dashboard]
- **Alert Name**: [AlertName]
- **MTTD (Mean Time To Detect)**: [time from incident start to detection]
- **Detection Effectiveness**: [Was detection timely? Appropriate?]

## Root Cause
[Detailed explanation of what caused the incident]

## Resolution
[Describe how the incident was resolved]

**Mitigation Steps**:
1. [Step 1]
2. [Step 2]
3. [Step 3]

**MTTR (Mean Time To Resolve)**: [time from detection to resolution]

## Follow-up Actions

| Action Item | Owner | Priority | Due Date | Status |
|-------------|-------|----------|----------|--------|
| [Action 1] | [Name] | [P0/P1/P2] | YYYY-MM-DD | [Open/In Progress/Done] |
| [Action 2] | [Name] | [P0/P1/P2] | YYYY-MM-DD | [Open/In Progress/Done] |

## Lessons Learned

### What Went Well
1. [Item 1]
2. [Item 2]

### What Could Be Improved
1. [Item 1]
2. [Item 2]

### Action Items for Improvement
- [Action 1]
- [Action 2]

## Supporting Data
- **Grafana Dashboard**: [link]
- **Prometheus Queries**: [link or queries]
- **Logs**: [link to relevant logs]
- **Related Incidents**: [links to similar past incidents]

---
**Post-Incident Review Meeting**: [Date/Time]
**Attendees**: [List]
```

## Part 5: Post-Incident Review Template

The post-incident review (also called "postmortem") is a blameless analysis to learn from incidents and prevent recurrence.

### 5.1 Blameless Postmortem Culture

**Key Principles**:
- **Blameless**: Focus on systems and processes, not individuals
- **Learning-focused**: Document what happened, why, and how to prevent it
- **Action-oriented**: Concrete action items with owners and deadlines
- **Transparent**: Share learnings across organization

### 5.2 Post-Incident Review Sections

The template should cover:
- **Summary**: What happened in 2-3 sentences
- **Impact**: Users affected, duration, SLO consumption
- **Timeline**: Detailed timeline of events and actions
- **Detection**: MTTD, detection method effectiveness
- **Response**: MTTR, mitigation actions, runbook effectiveness
- **Root Cause Analysis**: What, why, contributing factors (5 Whys method)
- **What Went Well**: Positive aspects of response
- **What Could Be Improved**: Gaps and improvements
- **Action Items**: Concrete tasks with owners, priorities, due dates
- **Lessons Learned**: Key takeaways for the team

### 5.3 Completing Post-Incident Reviews

**Process**:
1. Schedule postmortem meeting within 48 hours of resolution
2. Invite all participants (on-call, escalations, stakeholders)
3. Use timeline to walk through incident chronologically
4. Apply 5 Whys to identify root cause (not surface symptoms)
5. Document action items with SMART goals (Specific, Measurable, Achievable, Relevant, Time-bound)
6. Publish postmortem to team wiki/documentation
7. Track action items in project management system
8. Review action item completion in weekly team meetings

**Example 5 Whys**:
- **Why did latency spike?** → GPU queue depth grew to 500
- **Why did GPU queue grow?** → Traffic increased 3x from normal
- **Why did traffic increase?** → Marketing campaign launched
- **Why didn't we scale proactively?** → No notification of campaign
- **Why no notification?** → No process for eng/marketing coordination
- **Root cause**: Lack of cross-team communication process for traffic-impacting events
- **Action item**: Create Slack channel + process for launch coordination

## Part 6: Continuous Improvement Backlog

### 6.1 Observability Backlog Creation

Create `docs/observability-backlog.md`:

```markdown
# Observability & Reliability Backlog

**Last Updated**: 2025-01-15
**Owner**: ML Platform Team

## Priority Levels
- **P0 (Critical)**: Blocking production, must fix ASAP
- **P1 (High)**: Important for reliability, complete within 1 sprint
- **P2 (Medium)**: Valuable improvements, complete within 1 month
- **P3 (Low)**: Nice to have, backlog grooming

## Alerting Improvements

| Task | Priority | Effort | Owner | Due Date | Status |
|------|----------|--------|-------|----------|--------|
| Add multi-window burn rate alerts for availability SLO | P1 | 2 days | @ml-platform | 2025-01-30 | Open |
| Implement alert fatigue tracking (alerts per week per person) | P2 | 3 days | @platform | 2025-02-15 | Open |
| Add PagerDuty escalation policy testing | P2 | 1 day | @ml-platform | 2025-02-15 | Open |
| Create synthetic monitoring / canary checks | P1 | 5 days | @ml-platform | 2025-01-30 | Open |

## Runbook Improvements

| Task | Priority | Effort | Owner | Due Date | Status |
|------|----------|--------|-------|----------|--------|
| Add runbook for GPU OOM incidents | P1 | 2 days | @ml-platform | 2025-01-30 | Open |
| Create runbook for model registry outage | P2 | 2 days | @ml-ops | 2025-02-15 | Open |
| Add automated runbook testing (validate commands work) | P2 | 5 days | @platform | 2025-02-28 | Open |
| Runbook versioning and changelog | P3 | 1 day | @ml-platform | TBD | Open |

## Monitoring Improvements

| Task | Priority | Effort | Owner | Due Date | Status |
|------|----------|--------|-------|----------|--------|
| Automate drift detection pipeline (daily PSI calculation) | P1 | 5 days | @ml-ops | 2025-01-31 | Open |
| Add GPU memory leak detection | P1 | 3 days | @ml-platform | 2025-01-30 | Open |
| Implement canary deployment guardrails with automatic rollback | P1 | 8 days | @ml-ops | 2025-02-15 | Open |
| Expand log redaction coverage (credit cards, phone numbers) | P1 | 2 days | @security | 2025-01-25 | Open |
| Add model performance tracking (when ground truth available) | P2 | 5 days | @ml-eng | 2025-02-28 | Open |
| Implement distributed tracing span analysis | P2 | 5 days | @ml-platform | 2025-03-15 | Open |

## Dashboard Improvements

| Task | Priority | Effort | Owner | Due Date | Status |
|------|----------|--------|-------|----------|--------|
| Create on-call dashboard (active incidents, alert summary) | P1 | 3 days | @platform | 2025-01-30 | Open |
| Add SLO error budget burn-down chart | P1 | 2 days | @ml-platform | 2025-01-30 | Open |
| Create model comparison dashboard (A/B test results) | P2 | 5 days | @ml-ops | 2025-02-15 | Open |
| Add cost monitoring dashboard (GPU hours, inference costs) | P2 | 3 days | @finops | 2025-02-28 | Open |

## Process Improvements

| Task | Priority | Effort | Owner | Due Date | Status |
|------|----------|--------|-------|----------|--------|
| Implement on-call handoff checklist | P1 | 1 day | @ml-platform | 2025-01-20 | Open |
| Create incident severity classification guide | P1 | 2 days | @eng-manager | 2025-01-25 | Open |
| Add postmortem action item tracking to weekly team meeting | P1 | 1 day | @eng-manager | 2025-01-18 | Open |
| Quarterly on-call retrospective process | P2 | 2 days | @eng-manager | 2025-03-31 | Open |

## Infrastructure Improvements

| Task | Priority | Effort | Owner | Due Date | Status |
|------|----------|--------|-------|----------|--------|
| Implement Grafana OnCall for rotation management | P1 | 3 days | @platform | 2025-02-15 | Open |
| Add automated silencing during maintenance windows | P2 | 3 days | @platform | 2025-02-28 | Open |
| Anomaly detection with Prometheus `predict_linear` | P2 | 5 days | @ml-platform | 2025-03-15 | Open |
| Integrate with ServiceNow for incident tracking | P3 | 10 days | @platform | TBD | Open |
```

### 6.2 Prioritization Framework

Use this framework to prioritize backlog items:

**Impact vs Effort Matrix**:
```
High Impact, Low Effort → P0/P1 (Quick wins)
High Impact, High Effort → P1 (Strategic initiatives)
Low Impact, Low Effort → P2 (Fill capacity)
Low Impact, High Effort → P3 (Deprioritize)
```

**Reliability Impact Scoring**:
- **MTTD Reduction**: Does this help detect issues faster?
- **MTTR Reduction**: Does this help resolve issues faster?
- **Incident Prevention**: Does this prevent incidents entirely?
- **On-Call Quality of Life**: Does this reduce toil or alert fatigue?
- **Customer Impact**: Does this improve user experience?

Score each dimension 1-5, sum for priority.

## Part 7: Validation Checklist

### 7.1 Alert Infrastructure Validation

- [ ] **Alertmanager Deployed**: Alertmanager running and accessible (http://localhost:9093)
- [ ] **Alert Routes Configured**: Alerting policy implemented with proper routing
- [ ] **Contact Points Tested**:
  - [ ] Slack webhook configured and tested (send test notification)
  - [ ] PagerDuty integration key configured
  - [ ] Email SMTP settings configured
- [ ] **Secrets Management**: Credentials stored securely (Kubernetes secrets / .env file not in Git)
- [ ] **Inhibition Rules Working**: Verify critical alerts suppress warning alerts

### 7.2 Alert Rules Validation

- [ ] **SLO Burn Rate Alerts**:
  - [ ] Multi-window (5m/1h) burn rate alert configured
  - [ ] Recording rules for burn rate windows exist
  - [ ] Alert fires when latency exceeds SLO threshold
- [ ] **Error Rate Alerts**:
  - [ ] Critical error rate alert configured (>14.4x burn)
  - [ ] Warning error rate alert configured (>5%)
  - [ ] Alert includes runbook and dashboard links
- [ ] **Log-Based Alerts**:
  - [ ] FeatureNotFound log alert configured in Grafana
  - [ ] Log ingestion outage alert configured
  - [ ] Alerts fire when log patterns detected
- [ ] **ML Monitoring Alerts**:
  - [ ] Feature drift PSI alert configured
  - [ ] Prediction drift alert configured
  - [ ] Missing features alert configured

### 7.3 Runbook Validation

- [ ] **Runbooks Created**: Minimum 3 runbooks documented (latency, errors, drift)
- [ ] **Runbook Completeness**: Each runbook includes:
  - [ ] Impact and symptoms
  - [ ] Triage steps (< 5 minutes)
  - [ ] Investigation queries (Prometheus, Loki)
  - [ ] Mitigation procedures (step-by-step)
  - [ ] Escalation contacts
  - [ ] Post-incident tasks
- [ ] **Runbook Links**: Alert annotations include runbook URLs
- [ ] **Runbook Testing**: Execute at least 1 runbook during simulation (verify commands work)

### 7.4 Incident Simulation Validation

- [ ] **Simulation Scripts**: Incident simulation framework created
- [ ] **Scenario A (Latency)**:
  - [ ] Latency injection successful
  - [ ] Alert fired within 5 minutes
  - [ ] Runbook followed successfully
  - [ ] Timeline documented
  - [ ] Incident resolved
- [ ] **Scenario B (Feature Store)**:
  - [ ] Feature store outage simulated
  - [ ] Log-based alert fired
  - [ ] Degraded mode activated or store restored
  - [ ] Documented
- [ ] **Scenario C (Errors)**:
  - [ ] Error rate increased
  - [ ] Alert fired
  - [ ] Rollback executed
  - [ ] Errors resolved

### 7.5 Post-Incident Review Validation

- [ ] **Template Created**: Post-incident review template exists
- [ ] **Completed Reviews**: At least 2 simulations have completed postmortems
- [ ] **Action Items Identified**: Each postmortem has 2+ concrete action items
- [ ] **MTTD/MTTR Calculated**: Metrics calculated for each incident
- [ ] **Blameless Culture**: Review focuses on systems, not individuals

### 7.6 Continuous Improvement Validation

- [ ] **Backlog Created**: Observability backlog documented
- [ ] **Prioritization**: Tasks prioritized by P0/P1/P2/P3
- [ ] **Effort Estimates**: Each task has effort estimate
- [ ] **Owners Assigned**: Tasks have clear owners
- [ ] **Backlog Integration**: Linked to project management tool (Jira/GitHub Issues/Linear)

### 7.7 End-to-End Validation

- [ ] **Full Flow Test**: Trigger alert → receive notification → follow runbook → resolve → document
- [ ] **Alert Fatigue Check**: No more than 5 alerts/week per person for non-critical severity
- [ ] **Runbook Accessibility**: Runbooks accessible from alert notification (link works)
- [ ] **Documentation Published**: All artifacts committed to Git and shared with team

## Part 8: Stretch Goals

### 8.1 Advanced Alerting

- **Grafana OnCall Integration**:
  ```bash
  # Install Grafana OnCall
  helm repo add grafana https://grafana.github.io/helm-charts
  helm install oncall grafana/oncall

  # Configure on-call schedules
  # - Weekly rotation (Monday-Monday)
  # - Primary + secondary on-call
  # - Escalation after 10 minutes
  # - PTO/swap management
  ```

- **Automated Maintenance Silences**:
  ```yaml
  # Add to CI/CD pipeline
  - name: Create Alertmanager silence
    run: |
      amtool silence add \
        --alertmanager.url=http://alertmanager:9093 \
        --author="CI/CD Pipeline" \
        --comment="Deployment: ${{ github.sha }}" \
        --duration=30m \
        service="inference-gateway"
  ```

- **Anomaly Detection**:
  ```promql
  # Predict future latency based on trend
  predict_linear(
    inference_request_duration_seconds_p95[1h],
    3600  # 1 hour into future
  ) > 0.5  # Alert if predicted to exceed 500ms

  # Z-score anomaly detection
  abs(
    rate(inference_requests_total[5m])
    - avg_over_time(rate(inference_requests_total[5m])[1h])
  ) >
  3 * stddev_over_time(rate(inference_requests_total[5m])[1h])
  ```

### 8.2 Incident Management Platform Integration

- **ServiceNow Integration**:
  ```yaml
  # Alertmanager receiver
  - name: 'servicenow-incidents'
    webhook_configs:
      - url: 'https://your-instance.service-now.com/api/now/table/incident'
        http_config:
          basic_auth:
            username: '$SERVICENOW_USER'
            password: '$SERVICENOW_PASS'
        send_resolved: true
  ```

- **Opsgenie Integration**:
  ```yaml
  - name: 'opsgenie'
    opsgenie_configs:
      - api_key: '$OPSGENIE_API_KEY'
        priority: '{{ if eq .CommonLabels.severity "critical" }}P1{{ else }}P3{{ end }}'
        tags: '{{ .CommonLabels.service }},{{ .CommonLabels.team }}'
        responders:
          - type: team
            name: ML Platform
  ```

### 8.3 Chaos Engineering

- **Chaos Mesh for Kubernetes**:
  ```yaml
  # Inject latency chaos
  apiVersion: chaos-mesh.org/v1alpha1
  kind: NetworkChaos
  metadata:
    name: latency-injection
  spec:
    action: delay
    mode: one
    selector:
      labelSelectors:
        app: inference-gateway
    delay:
      latency: "500ms"
      correlation: "100"
    duration: "10m"
    scheduler:
      cron: "@weekly"  # Run chaos test weekly
  ```

- **Automated Runbook Validation**:
  ```bash
  # Weekly cron job to validate runbooks
  #!/bin/bash
  # Test each runbook command still works

  for runbook in runbooks/*/*.md; do
    echo "Testing $runbook..."
    # Extract bash commands from runbook
    # Execute in dry-run mode
    # Report failures to team
  done
  ```

### 8.4 Advanced Metrics

- **SLO Error Budget Dashboard**:
  - Current error budget remaining (percentage)
  - Error budget burn-down rate
  - Projected exhaustion date
  - Historical error budget usage
  - Alert budget (max allowed alerts per week)

- **On-Call Health Metrics**:
  - Alerts per week per person
  - Incident frequency and duration
  - MTTD/MTTR trends
  - On-call satisfaction scores
  - Burnout risk indicators

## Reflection Questions

### Question 1: Alert Sensitivity vs. Detection Speed

**How do you balance alert sensitivity (avoiding noise) with the need for rapid detection?**

**Discussion Points**:
- **SLO-based alerting**: Alerts tied to user impact, not arbitrary thresholds
- **Multi-window burn rates**: Fast burn (catch critical issues quickly) + slow burn (catch gradual degradation)
- **Alert fatigue metrics**: Track alerts/week/person; if >20/week, tune thresholds
- **Alert reviews**: Quarterly review of all alerts; disable/tune ones with low signal
- **Severity tiering**: Page only for critical (user-impacting); Slack for warnings
- **Testing**: Chaos engineering to validate alerts fire appropriately

**Your Answer**: [Reflect on your experience in this exercise]

### Question 2: On-Call Sustainability

**What indicators suggest the on-call workload is unsustainable?**

**Warning Signs**:
- Alerts > 20/week per person
- Incidents lasting > 2 hours frequently
- Same alerts firing repeatedly (not addressed)
- On-call engineers reporting burnout
- High turnover in on-call rotation
- Incidents during business hours only (insufficient monitoring)
- Team avoiding on-call duty

**Remediation Strategies**:
- Increase team size or rotation size
- Automate common mitigation tasks
- Improve prevention (fix recurring issues)
- Add secondary on-call for backup
- Reduce non-critical alerts
- Build runbooks to speed MTTR
- Follow-through on postmortem action items

**Your Answer**: [Reflect on sustainability considerations]

### Question 3: Multi-Region Runbooks

**How would you adapt runbooks for a multi-region deployment?**

**Considerations**:
- **Regional failover procedures**: Steps to failover traffic to healthy region
- **Region-specific contact points**: Different on-call teams per region/timezone
- **Cross-region dependencies**: Document how regions depend on each other
- **Regional alert routing**: Route alerts to appropriate regional team
- **Degraded mode**: Define regional degradation vs full outage
- **Data locality**: Account for data residency requirements
- **Time zones**: Runbooks should note UTC times and local time conversions

**Example Additions to Runbook**:
```markdown
## Regional Deployment Notes

### Regions
- us-east-1 (Primary)
- eu-west-1 (Secondary)
- ap-southeast-1 (Secondary)

### Regional Failover
If us-east-1 degraded:
1. Check region health dashboard
2. Verify eu-west-1 and ap-southeast-1 healthy
3. Update Route53 weights: us-east-1=0, eu-west-1=50, ap-southeast-1=50
4. Monitor traffic shift in Grafana
5. Create incident for us-east-1 recovery

### Regional Contacts
- us-east-1: @us-oncall
- eu-west-1: @eu-oncall
- ap-southeast-1: @apac-oncall
```

**Your Answer**: [Reflect on multi-region considerations]

### Question 4: Backlog Prioritization

**Which actions from the backlog provide the highest impact for future reliability?**

**Evaluation Framework**:
- **Impact on MTTD**: How much does this reduce detection time?
- **Impact on MTTR**: How much does this reduce resolution time?
- **Prevention**: Can this prevent entire classes of incidents?
- **Effort vs Impact**: Is this a quick win or strategic investment?
- **Frequency**: Does this address common incidents or rare edge cases?

**High-Impact Items** (from typical backlog):
1. **Automated Drift Detection**: Prevents model degradation (high frequency, high user impact)
2. **Canary Deployment Guardrails**: Prevents bad deploys reaching production (incident prevention)
3. **On-Call Dashboard**: Reduces MTTR by providing quick overview (low effort, immediate value)
4. **Runbook Automation**: Reduces MTTR for common incidents (scales with team)
5. **SLO Error Budget Tracking**: Provides visibility into reliability trends (strategic)

**Your Answer**: [Reflect on prioritization from your backlog]

---

## Exercise Complete!

Congratulations! You've built a production-ready alerting and incident response system for ML infrastructure, including:

✅ **Complete Alerting Stack**:
- Alertmanager with multi-channel routing
- SLO-based burn rate alerts
- Log-based alerts for application errors
- ML-specific drift and performance alerts

✅ **Professional Runbooks**:
- Latency, error rate, and drift runbooks following Google SRE best practices
- Step-by-step mitigation procedures
- Investigation queries and commands
- Escalation paths

✅ **Incident Simulation Framework**:
- Automated incident injection
- Timeline and documentation generation
- Hands-on runbook practice

✅ **Post-Incident Review Process**:
- Blameless postmortem template
- MTTD/MTTR tracking
- Action item management

✅ **Continuous Improvement**:
- Prioritized observability backlog
- Effort estimates and ownership

**Next Steps**:
1. Complete Module 009 quiz to test your knowledge
2. Review Module 009 to reinforce concepts
3. Continue to Module 010: Cloud Platforms

---

**Module 009: Monitoring & Logging Basics** - Exercise 05 Complete
