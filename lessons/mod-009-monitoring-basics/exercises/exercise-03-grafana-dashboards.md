# Exercise 03: Grafana Dashboards & Visualization

## Overview

Transform Prometheus metrics into actionable insights by building a comprehensive Grafana dashboard suite for the ML Platform. You'll create production-ready dashboards for on-call engineers, platform operators, and executives, implement dashboard-as-code workflows, configure unified alerting, and establish governance processes. This exercise converts the observability data from Exercises 01-02 into visual narratives that drive operational excellence.

**Difficulty:** Intermediate → Advanced
**Estimated Time:** 4–5 hours
**Prerequisites:**
- Exercises 01-02 completed (instrumented inference gateway + Prometheus stack)
- Lecture 03 (Grafana Dashboards & Visualization)
- Understanding of PromQL from Exercise 02
- Basic knowledge of JSON

## Learning Objectives

By finishing this lab you will be able to:

1. Deploy and configure Grafana with multiple data sources (Prometheus, Loki, Jaeger)
2. Design effective dashboards using panel best practices and visualization theory
3. Build service dashboards with SLO tracking, latency heatmaps, and error analysis
4. Create platform health dashboards for infrastructure monitoring
5. Develop executive overview dashboards with business-relevant KPIs
6. Implement dashboard templating for multi-environment support
7. Configure Grafana unified alerting with contact points and notification policies
8. Provision dashboards as code using JSON and Grafana provisioning
9. Establish dashboard governance and ownership models
10. Create drill-down navigation and dashboard linking strategies
11. Implement annotation streams for deployment tracking
12. Apply accessibility and color-blind friendly design patterns

## Scenario

The ML Platform team has metrics flowing into Prometheus from Exercise 02, but engineers are overwhelmed by raw metric data. Leadership wants real-time visibility into SLO compliance, and the on-call team needs actionable dashboards during incidents.

Your task is to build a comprehensive dashboard suite that:
- Enables on-call engineers to diagnose incidents in < 5 minutes
- Provides platform operators with infrastructure health visibility
- Gives executives weekly SLO compliance and error budget status
- Supports multi-environment deployments (lab, staging, production)
- Follows dashboard-as-code best practices for versioning and reproducibility

---

## Part 1: Grafana Deployment and Configuration

### Step 1.1: Extend Docker Compose with Grafana

Update `docker-compose.yml` from Exercise 02 to include Grafana:

```yaml
# Add to docker-compose.yml from Exercise 02

services:
  # ... (existing services from Exercise 02)

  # ==============================================
  # Grafana
  # ==============================================
  grafana:
    image: grafana/grafana:10.2.3
    container_name: grafana
    ports:
      - "3000:3000"
    environment:
      # Admin credentials
      - GF_SECURITY_ADMIN_USER=admin
      - GF_SECURITY_ADMIN_PASSWORD=admin
      - GF_SECURITY_ALLOW_EMBEDDING=true

      # Server settings
      - GF_SERVER_ROOT_URL=http://localhost:3000
      - GF_SERVER_SERVE_FROM_SUB_PATH=false

      # Auth settings (disable for lab, enable for production)
      - GF_AUTH_ANONYMOUS_ENABLED=false
      - GF_AUTH_BASIC_ENABLED=true
      - GF_AUTH_DISABLE_LOGIN_FORM=false

      # Database (SQLite for lab, PostgreSQL for production)
      - GF_DATABASE_TYPE=sqlite3

      # Provisioning
      - GF_PATHS_PROVISIONING=/etc/grafana/provisioning

      # Unified alerting (enabled by default in v9+)
      - GF_UNIFIED_ALERTING_ENABLED=true
      - GF_ALERTING_ENABLED=false  # Disable legacy alerting

      # Feature toggles
      - GF_FEATURE_TOGGLES_ENABLE=publicDashboards,tempoSearch,tempoBackendSearch

      # Logging
      - GF_LOG_LEVEL=info
      - GF_LOG_MODE=console

    volumes:
      # Grafana data
      - grafana-data:/var/lib/grafana

      # Provisioning configuration
      - ./grafana/provisioning/datasources:/etc/grafana/provisioning/datasources:ro
      - ./grafana/provisioning/dashboards:/etc/grafana/provisioning/dashboards:ro

      # Dashboard JSON files
      - ./grafana/dashboards:/var/lib/grafana/dashboards:ro

      # Alert provisioning (optional)
      - ./grafana/provisioning/alerting:/etc/grafana/provisioning/alerting:ro

    networks:
      - monitoring
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "wget", "--spider", "-q", "http://localhost:3000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    depends_on:
      - prometheus

volumes:
  # ... (existing volumes)
  grafana-data:
```

### Step 1.2: Create Project Structure for Grafana

```bash
mkdir -p grafana/{provisioning,dashboards,screenshots}
mkdir -p grafana/provisioning/{datasources,dashboards,alerting,notifiers}
mkdir -p grafana/dashboards/{service,platform,executive}
mkdir -p docs/dashboard-guides
```

**Expected Structure:**
```
grafana/
├── provisioning/
│   ├── datasources/
│   │   └── prometheus.yml
│   ├── dashboards/
│   │   └── dashboards.yml
│   └── alerting/
│       └── rules.yml
├── dashboards/
│   ├── service/
│   │   ├── inference-gateway.json
│   │   └── model-registry.json
│   ├── platform/
│   │   ├── prometheus-health.json
│   │   ├── node-exporter.json
│   │   └── alertmanager.json
│   └── executive/
│       └── slo-overview.json
└── screenshots/
    └── (dashboard screenshots for documentation)
```

### Step 1.3: Configure Data Sources via Provisioning

Create `grafana/provisioning/datasources/prometheus.yml`:

```yaml
# grafana/provisioning/datasources/prometheus.yml
apiVersion: 1

datasources:
  # ==============================================
  # Prometheus
  # ==============================================
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: false
    jsonData:
      httpMethod: POST
      timeInterval: 15s
      queryTimeout: 60s
      # Custom query params (optional)
      customQueryParameters: ""
      # Exemplars configuration (for trace linking)
      exemplarTraceIdDestinations:
        - name: trace_id
          datasourceUid: tempo
      # Prometheus type (default is Prometheus)
      prometheusType: Prometheus
      prometheusVersion: 2.48.0
      # Incremental querying
      incrementalQuerying: true
      incrementalQueryOverlapWindow: 10m
    version: 1

  # ==============================================
  # Loki (Logs)
  # ==============================================
  - name: Loki
    type: loki
    access: proxy
    url: http://loki:3100
    isDefault: false
    editable: false
    jsonData:
      maxLines: 1000
      # Derived fields for trace linking
      derivedFields:
        - datasourceUid: tempo
          matcherRegex: "trace_id=(\\w+)"
          name: trace_id
          url: "$${__value.raw}"
    version: 1

  # ==============================================
  # Tempo/Jaeger (Traces)
  # ==============================================
  - name: Tempo
    type: tempo
    access: proxy
    url: http://jaeger:16686  # Jaeger query endpoint
    isDefault: false
    editable: false
    jsonData:
      httpMethod: GET
      tracesToLogs:
        datasourceUid: loki
        tags: ['service', 'span_id']
        mappedTags: [{key: 'service.name', value: 'service'}]
        mapTagNamesEnabled: true
        filterByTraceID: true
        filterBySpanID: true
      serviceMap:
        datasourceUid: prometheus
      nodeGraph:
        enabled: true
    version: 1

  # ==============================================
  # Alertmanager
  # ==============================================
  - name: Alertmanager
    type: alertmanager
    access: proxy
    url: http://alertmanager:9093
    isDefault: false
    editable: false
    jsonData:
      implementation: prometheus
    version: 1
```

**Key Features**:
- Prometheus as default data source
- Trace linking from Prometheus exemplars to Tempo
- Log linking from Tempo to Loki
- Alertmanager integration for alert status panels

### Step 1.4: Start Grafana and Verify Data Sources

```bash
# Start the updated stack
docker-compose up -d grafana

# Check Grafana logs
docker-compose logs -f grafana

# Wait for Grafana to be healthy
docker-compose ps grafana
```

Access Grafana:
- URL: http://localhost:3000
- Username: `admin`
- Password: `admin` (change on first login)

**Verify data sources:**
1. Navigate to **Configuration → Data Sources**
2. Verify all data sources show green "Data source is working" status
3. Test Prometheus query: `up` (should return metrics)

**✅ Checkpoint:** Grafana is running and all data sources are connected.

---

## Part 2: Dashboard Design Principles

### Step 2.1: Define Dashboard Requirements

Create `docs/dashboard-requirements.md`:

```markdown
# Dashboard Requirements

## Service Dashboard: Inference Gateway

**Audience**: On-call engineers, service owners
**Purpose**: Real-time operational visibility and incident triage
**Update Frequency**: Every 15 seconds

### Required Panels:
1. **SLO Summary Row**
   - Current P99 latency vs 300ms target
   - Availability % (30-day rolling)
   - Error rate vs 0.5% target
   - Error budget remaining

2. **Golden Signals Row**
   - Latency: P50/P95/P99 time series
   - Traffic: Requests per second by status code
   - Errors: Error rate by endpoint
   - Saturation: Queue depth, CPU, memory

3. **ML Metrics Row**
   - Inference latency breakdown (preprocessing, model, postprocessing)
   - Model confidence distribution
   - Predictions by class (top 10)
   - Batch size distribution

4. **Resources Row**
   - CPU usage per container
   - Memory usage per container
   - GPU utilization (if available)
   - Network I/O

5. **Logs & Traces Row**
   - Recent errors from Loki
   - Trace ID search
   - Link to Jaeger for distributed tracing

### Variables:
- `environment`: lab, staging, production
- `cluster`: cluster name
- `instance`: service instance ID

### Thresholds:
- Latency: Warn at 250ms, Critical at 300ms
- Error rate: Warn at 0.4%, Critical at 0.5%
- CPU: Warn at 70%, Critical at 85%
- Memory: Warn at 80%, Critical at 90%

---

## Platform Dashboard: Prometheus & Infrastructure

**Audience**: Platform engineers, SREs
**Purpose**: Monitor the monitoring stack health

### Required Panels:
1. **Prometheus Health**
   - Up targets count
   - Scrape duration P99
   - TSDB head series count
   - Ingestion rate (samples/sec)

2. **Node Exporter Stats**
   - CPU usage by mode (user, system, idle)
   - Memory usage (used, cached, available)
   - Disk I/O (read, write IOPS)
   - Network traffic (rx, tx bytes/sec)

3. **Alert Activity**
   - Active alerts by severity
   - Alert firing timeline
   - Alert acknowledgment status

---

## Executive Dashboard: SLO Overview

**Audience**: Engineering managers, executives
**Purpose**: Weekly review, OKR tracking, budget planning

### Required Panels:
1. **SLO Compliance**
   - 30-day availability trend
   - Error budget burn down
   - SLO violations count
   - Mean time to recovery (MTTR)

2. **Business Metrics**
   - Total inference requests (30-day)
   - Unique models served
   - Peak throughput achieved
   - Cost per 1M requests (if available)

3. **Operational Metrics**
   - Incident count by severity
   - Average incident duration
   - Deployment frequency
   - Change failure rate

### Update Frequency: Daily (snapshot at midnight UTC)
```

**✅ Checkpoint:** Dashboard requirements documented.

### Step 2.2: Panel Design Best Practices

Create `docs/dashboard-design-guide.md`:

```markdown
# Dashboard Design Best Practices

## Visual Hierarchy

1. **Top Row**: Most critical metrics (SLOs, error budget)
2. **Middle Rows**: Golden Signals and service-specific metrics
3. **Bottom Rows**: Supporting details (logs, traces, resources)

## Color Palette

### Status Colors (Accessible)
- **Green**: #73BF69 (success, healthy, within SLO)
- **Yellow**: #FFA500 (warning, approaching threshold)
- **Red**: #E02F44 (critical, SLO violation)
- **Blue**: #5794F2 (informational, neutral)

### Gradient Colors
- Use gradient scales for heatmaps: Green → Yellow → Red
- Avoid pure red/green combinations (color-blind friendly)

## Panel Types

### Use Stat Panels for:
- Single value metrics (current error rate, latency)
- SLO compliance percentages
- Counters (total requests, errors)

### Use Time Series for:
- Trends over time (latency, throughput)
- Comparisons (P50 vs P95 vs P99)
- Multiple metrics on same axis

### Use Heatmaps for:
- Latency distribution over time
- Request volume by hour and day
- Resource utilization patterns

### Use Tables for:
- Top N lists (highest latency endpoints, most errors)
- Log aggregations
- Alert status summaries

### Use Bar Gauge for:
- Current vs target comparisons
- Multi-series comparisons
- Threshold visualization

## Threshold Configuration

**Latency Example:**
```json
{
  "thresholds": {
    "mode": "absolute",
    "steps": [
      { "color": "green", "value": null },
      { "color": "yellow", "value": 0.25 },  // 250ms
      { "color": "red", "value": 0.3 }       // 300ms
    ]
  }
}
```

## Panel Descriptions

Always include panel descriptions with:
- What the metric measures
- Why it matters
- What action to take if threshold exceeded
- Link to runbook

**Example:**
```
This panel shows P99 request latency for the inference gateway.

SLO: 99% of requests < 300ms

If latency exceeds 300ms:
1. Check for recent deployments
2. Review trace samples for slow spans
3. Check resource utilization (CPU/GPU)
4. Follow runbook: go/runbook-high-latency
```
```

**✅ Checkpoint:** Design guide established.

---

## Part 3: Build Service Dashboard (Inference Gateway)

### Step 3.1: Create Dashboard Configuration File

Create `grafana/provisioning/dashboards/dashboards.yml`:

```yaml
# grafana/provisioning/dashboards/dashboards.yml
apiVersion: 1

providers:
  - name: 'AI Infrastructure'
    orgId: 1
    folder: 'AI Infrastructure'
    type: file
    disableDeletion: false
    allowUiUpdates: true  # Allow edits in UI (set to false in production)
    updateIntervalSeconds: 30
    options:
      path: /var/lib/grafana/dashboards
      foldersFromFilesStructure: true
```

### Step 3.2: Create Inference Gateway Dashboard JSON

Create `grafana/dashboards/service/inference-gateway.json`:

**Note:** Due to length, I'll provide a comprehensive but abbreviated version. Full dashboard would be 2,000+ lines of JSON.

```json
{
  "dashboard": {
    "title": "Inference Gateway - Service Dashboard",
    "uid": "inference-gateway-service",
    "tags": ["inference", "ml-platform", "service"],
    "timezone": "UTC",
    "schemaVersion": 38,
    "version": 1,
    "refresh": "30s",

    "templating": {
      "list": [
        {
          "name": "datasource",
          "type": "datasource",
          "query": "prometheus",
          "current": {
            "text": "Prometheus",
            "value": "Prometheus"
          }
        },
        {
          "name": "environment",
          "type": "custom",
          "query": "lab,staging,production",
          "current": {
            "text": "lab",
            "value": "lab"
          },
          "multi": false,
          "includeAll": false
        },
        {
          "name": "cluster",
          "type": "query",
          "datasource": "$datasource",
          "query": "label_values(http_requests_total{environment=\"$environment\"}, cluster)",
          "refresh": 2,
          "multi": false,
          "includeAll": false
        },
        {
          "name": "instance",
          "type": "query",
          "datasource": "$datasource",
          "query": "label_values(http_requests_total{environment=\"$environment\",cluster=\"$cluster\"}, instance)",
          "refresh": 2,
          "multi": true,
          "includeAll": true
        }
      ]
    },

    "annotations": {
      "list": [
        {
          "name": "Deployments",
          "datasource": "Prometheus",
          "enable": true,
          "iconColor": "blue",
          "expr": "changes(process_start_time_seconds{service=\"inference-gateway\"}[5m]) > 0",
          "tagKeys": "version",
          "titleFormat": "Deployment",
          "textFormat": "Service restarted (version: {{version}})"
        },
        {
          "name": "Alerts",
          "datasource": "Prometheus",
          "enable": true,
          "iconColor": "red",
          "expr": "ALERTS{service=\"inference-gateway\",alertstate=\"firing\"}",
          "tagKeys": "alertname,severity",
          "titleFormat": "{{ alertname }}",
          "textFormat": "Severity: {{ severity }}"
        }
      ]
    },

    "panels": [
      {
        "id": 1,
        "type": "row",
        "title": "SLO Summary",
        "collapsed": false,
        "gridPos": {"h": 1, "w": 24, "x": 0, "y": 0}
      },
      {
        "id": 2,
        "type": "stat",
        "title": "P99 Latency (SLO: <300ms)",
        "gridPos": {"h": 4, "w": 6, "x": 0, "y": 1},
        "targets": [
          {
            "expr": "slo:service_latency:p99_rate5m{service=\"inference-gateway\",environment=\"$environment\",cluster=\"$cluster\"}",
            "refId": "A",
            "legendFormat": "P99 Latency"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "s",
            "thresholds": {
              "mode": "absolute",
              "steps": [
                {"color": "green", "value": null},
                {"color": "yellow", "value": 0.25},
                {"color": "red", "value": 0.3}
              ]
            }
          }
        },
        "options": {
          "graphMode": "area",
          "colorMode": "background",
          "orientation": "auto",
          "textMode": "value_and_name",
          "reduceOptions": {
            "calcs": ["lastNotNull"]
          }
        },
        "description": "99th percentile request latency over 5-minute window.\n\nSLO: 99% of requests < 300ms\n\nIf exceeds threshold:\n1. Check recent deployments\n2. Review trace samples for slow spans  \n3. Check resource utilization\n4. Runbook: go/runbook-high-latency"
      },
      {
        "id": 3,
        "type": "stat",
        "title": "Availability (SLO: 99.5%)",
        "gridPos": {"h": 4, "w": 6, "x": 6, "y": 1},
        "targets": [
          {
            "expr": "slo:service_availability:ratio_rate30m{service=\"inference-gateway\",environment=\"$environment\",cluster=\"$cluster\"} * 100",
            "refId": "A",
            "legendFormat": "Availability"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "percent",
            "decimals": 2,
            "thresholds": {
              "mode": "absolute",
              "steps": [
                {"color": "red", "value": null},
                {"color": "yellow", "value": 99.0},
                {"color": "green", "value": 99.5}
              ]
            }
          }
        },
        "options": {
          "graphMode": "area",
          "colorMode": "background",
          "orientation": "auto",
          "textMode": "value",
          "reduceOptions": {
            "calcs": ["lastNotNull"]
          }
        },
        "description": "Percentage of successful requests (non-5xx) over 30-minute window.\n\nSLO: 99.5% availability\n\nIf below threshold:\n1. Check active alerts\n2. Review error logs\n3. Investigate recent changes\n4. Runbook: go/runbook-availability"
      },
      {
        "id": 4,
        "type": "stat",
        "title": "Error Rate (SLO: <0.5%)",
        "gridPos": {"h": 4, "w": 6, "x": 12, "y": 1},
        "targets": [
          {
            "expr": "slo:service_error_rate:ratio_rate30m{service=\"inference-gateway\",environment=\"$environment\",cluster=\"$cluster\"} * 100",
            "refId": "A",
            "legendFormat": "Error Rate"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "percent",
            "decimals": 2,
            "thresholds": {
              "mode": "absolute",
              "steps": [
                {"color": "green", "value": null},
                {"color": "yellow", "value": 0.4},
                {"color": "red", "value": 0.5}
              ]
            }
          }
        },
        "options": {
          "graphMode": "area",
          "colorMode": "background",
          "orientation": "auto",
          "textMode": "value",
          "reduceOptions": {
            "calcs": ["lastNotNull"]
          }
        },
        "description": "Percentage of requests resulting in 5xx errors over 30-minute window.\n\nSLO: Error rate < 0.5%\n\nIf exceeds threshold:\n1. Check error logs for patterns\n2. Review recent deployments\n3. Check downstream dependencies\n4. Runbook: go/runbook-high-errors"
      },
      {
        "id": 5,
        "type": "stat",
        "title": "Error Budget Remaining",
        "gridPos": {"h": 4, "w": 6, "x": 18, "y": 1},
        "targets": [
          {
            "expr": "slo:service_availability:error_budget_remaining{service=\"inference-gateway\",environment=\"$environment\",cluster=\"$cluster\"} * 100",
            "refId": "A",
            "legendFormat": "Budget Remaining"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "percent",
            "decimals": 1,
            "thresholds": {
              "mode": "absolute",
              "steps": [
                {"color": "red", "value": null},
                {"color": "yellow", "value": 25},
                {"color": "green", "value": 50}
              ]
            }
          }
        },
        "options": {
          "graphMode": "none",
          "colorMode": "background",
          "orientation": "auto",
          "textMode": "value_and_name",
          "reduceOptions": {
            "calcs": ["lastNotNull"]
          }
        },
        "description": "Percentage of error budget remaining for the month.\n\nTarget: > 50% remaining at mid-month\n\nIf < 25%:\n1. Freeze non-critical deployments\n2. Focus on reliability improvements\n3. Review error budget policy\n4. Escalate to engineering manager"
      },

      {
        "id": 10,
        "type": "row",
        "title": "Golden Signals - Latency",
        "collapsed": false,
        "gridPos": {"h": 1, "w": 24, "x": 0, "y": 5}
      },
      {
        "id": 11,
        "type": "timeseries",
        "title": "Request Latency Percentiles",
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 6},
        "targets": [
          {
            "expr": "histogram_quantile(0.50, sum(rate(http_request_duration_seconds_bucket{service=\"inference-gateway\",environment=\"$environment\",cluster=\"$cluster\",instance=~\"$instance\"}[5m])) by (le))",
            "refId": "P50",
            "legendFormat": "P50"
          },
          {
            "expr": "histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket{service=\"inference-gateway\",environment=\"$environment\",cluster=\"$cluster\",instance=~\"$instance\"}[5m])) by (le))",
            "refId": "P95",
            "legendFormat": "P95"
          },
          {
            "expr": "histogram_quantile(0.99, sum(rate(http_request_duration_seconds_bucket{service=\"inference-gateway\",environment=\"$environment\",cluster=\"$cluster\",instance=~\"$instance\"}[5m])) by (le))",
            "refId": "P99",
            "legendFormat": "P99"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "s",
            "custom": {
              "lineWidth": 2,
              "fillOpacity": 10,
              "showPoints": "never",
              "axisPlacement": "auto"
            },
            "thresholds": {
              "mode": "absolute",
              "steps": [
                {"color": "green", "value": null},
                {"color": "yellow", "value": 0.25},
                {"color": "red", "value": 0.3}
              ]
            }
          },
          "overrides": [
            {
              "matcher": {"id": "byName", "options": "P99"},
              "properties": [
                {"id": "custom.lineWidth", "value": 3}
              ]
            }
          ]
        },
        "options": {
          "legend": {
            "displayMode": "table",
            "placement": "bottom",
            "calcs": ["mean", "lastNotNull", "max"]
          },
          "tooltip": {
            "mode": "multi",
            "sort": "desc"
          }
        },
        "description": "Request latency at P50, P95, and P99 percentiles.\n\nThe P99 line shows the 99th percentile latency - 99% of requests are faster than this value.\n\nWatch for:\n- Sudden spikes (potential incidents)\n- Gradual increases (performance degradation)\n- Gap between P50 and P99 (outliers)"
      },
      {
        "id": 12,
        "type": "heatmap",
        "title": "Latency Heatmap",
        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 6},
        "targets": [
          {
            "expr": "sum(increase(http_request_duration_seconds_bucket{service=\"inference-gateway\",environment=\"$environment\",cluster=\"$cluster\",instance=~\"$instance\"}[$__interval])) by (le)",
            "refId": "A",
            "format": "heatmap",
            "legendFormat": "{{le}}"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "custom": {
              "hideFrom": {
                "tooltip": false,
                "viz": false,
                "legend": false
              }
            }
          }
        },
        "options": {
          "calculate": false,
          "calculation": {},
          "cellGap": 2,
          "cellValues": {},
          "color": {
            "exponent": 0.5,
            "fill": "dark-orange",
            "mode": "scheme",
            "reverse": false,
            "scale": "exponential",
            "scheme": "Turbo",
            "steps": 128
          },
          "exemplars": {
            "color": "rgba(255,0,255,0.7)"
          },
          "filterValues": {
            "le": 1e-9
          },
          "legend": {
            "show": true
          },
          "rowsFrame": {
            "layout": "auto"
          },
          "tooltip": {
            "show": true,
            "yHistogram": false
          },
          "yAxis": {
            "axisPlacement": "left",
            "reverse": false,
            "unit": "s"
          }
        },
        "description": "Heatmap visualization of request latency distribution over time.\n\nDarker colors = more requests at that latency.\n\nUse this to identify:\n- Latency patterns (bimodal distributions)\n- Sudden shifts in performance\n- Outliers and long-tail behavior"
      },

      {
        "id": 20,
        "type": "row",
        "title": "Golden Signals - Traffic & Errors",
        "collapsed": false,
        "gridPos": {"h": 1, "w": 24, "x": 0, "y": 14}
      },
      {
        "id": 21,
        "type": "timeseries",
        "title": "Requests per Second",
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 15},
        "targets": [
          {
            "expr": "sum(rate(http_requests_total{service=\"inference-gateway\",environment=\"$environment\",cluster=\"$cluster\",instance=~\"$instance\",status_code=~\"2..\"}[5m]))",
            "refId": "2xx",
            "legendFormat": "2xx Success"
          },
          {
            "expr": "sum(rate(http_requests_total{service=\"inference-gateway\",environment=\"$environment\",cluster=\"$cluster\",instance=~\"$instance\",status_code=~\"4..\"}[5m]))",
            "refId": "4xx",
            "legendFormat": "4xx Client Error"
          },
          {
            "expr": "sum(rate(http_requests_total{service=\"inference-gateway\",environment=\"$environment\",cluster=\"$cluster\",instance=~\"$instance\",status_code=~\"5..\"}[5m]))",
            "refId": "5xx",
            "legendFormat": "5xx Server Error"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "reqps",
            "custom": {
              "drawStyle": "line",
              "lineInterpolation": "smooth",
              "barAlignment": 0,
              "lineWidth": 2,
              "fillOpacity": 15,
              "gradientMode": "opacity",
              "spanNulls": false,
              "showPoints": "never",
              "stacking": {
                "mode": "normal",
                "group": "A"
              }
            }
          },
          "overrides": [
            {
              "matcher": {"id": "byName", "options": "5xx Server Error"},
              "properties": [
                {"id": "color", "value": {"mode": "fixed", "fixedColor": "red"}}
              ]
            },
            {
              "matcher": {"id": "byName", "options": "4xx Client Error"},
              "properties": [
                {"id": "color", "value": {"mode": "fixed", "fixedColor": "orange"}}
              ]
            },
            {
              "matcher": {"id": "byName", "options": "2xx Success"},
              "properties": [
                {"id": "color", "value": {"mode": "fixed", "fixedColor": "green"}}
              ]
            }
          ]
        },
        "options": {
          "legend": {
            "displayMode": "table",
            "placement": "bottom",
            "calcs": ["mean", "lastNotNull", "max"]
          },
          "tooltip": {
            "mode": "multi",
            "sort": "desc"
          }
        },
        "description": "Request rate per second, broken down by HTTP status code.\n\nStacked area chart shows total traffic volume.\n\nWatch for:\n- Traffic spikes (legitimate or attack?)\n- Drop in traffic (upstream issues?)\n- Increase in 5xx errors (service degradation)"
      },
      {
        "id": 22,
        "type": "table",
        "title": "Error Summary by Endpoint",
        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 15},
        "targets": [
          {
            "expr": "topk(10, sum(increase(http_requests_total{service=\"inference-gateway\",environment=\"$environment\",cluster=\"$cluster\",status_code=~\"5..\"}[1h])) by (endpoint, status_code))",
            "refId": "A",
            "format": "table",
            "instant": true
          }
        ],
        "transformations": [
          {
            "id": "organize",
            "options": {
              "excludeByName": {"Time": true},
              "indexByName": {
                "endpoint": 0,
                "status_code": 1,
                "Value": 2
              },
              "renameByName": {
                "endpoint": "Endpoint",
                "status_code": "Status Code",
                "Value": "Error Count (1h)"
              }
            }
          }
        ],
        "fieldConfig": {
          "defaults": {
            "custom": {
              "align": "auto",
              "displayMode": "auto"
            },
            "thresholds": {
              "mode": "absolute",
              "steps": [
                {"color": "green", "value": null},
                {"color": "yellow", "value": 10},
                {"color": "red", "value": 100}
              ]
            }
          },
          "overrides": [
            {
              "matcher": {"id": "byName", "options": "Error Count (1h)"},
              "properties": [
                {"id": "custom.displayMode", "value": "color-background"},
                {"id": "custom.width", "value": 150}
              ]
            }
          ]
        },
        "options": {
          "showHeader": true,
          "sortBy": [
            {"displayName": "Error Count (1h)", "desc": true}
          ]
        },
        "description": "Top 10 endpoints by error count in the last hour.\n\nUse this to identify:\n- Which endpoints are failing most\n- Specific status codes (500, 503, etc.)\n- Patterns in error distribution\n\nClick endpoint name to filter to that endpoint."
      }

      // Additional panels would continue for:
      // - ML Metrics (inference latency breakdown, confidence, predictions)
      // - Resources (CPU, memory, GPU)
      // - Logs & Traces (Loki logs, Jaeger links)
    ]
  }
}
```

**Note:** The full dashboard JSON would include 20-30 panels covering:
- SLO summary
- Latency metrics
- Traffic and errors
- ML-specific metrics
- Resource utilization
- Logs and traces
- Deployment annotations

For brevity, I've shown the structure and key panels. The complete version would be 1,500-2,000 lines of JSON.

**✅ Checkpoint:** Service dashboard JSON created.

### Step 3.3: Import and Test Dashboard

```bash
# Restart Grafana to load provisioned dashboards
docker-compose restart grafana

# Or reload provisioning without restart
curl -X POST http://admin:admin@localhost:3000/api/admin/provisioning/dashboards/reload
```

**Access dashboard:**
1. Navigate to http://localhost:3000
2. Go to **Dashboards → Browse**
3. Open folder "AI Infrastructure"
4. Select "Inference Gateway - Service Dashboard"

**Verify**:
- All panels load data
- Variables work (select different environment/cluster)
- Thresholds display correctly
- Annotations show deployment markers

**✅ Checkpoint:** Service dashboard is functional.

---

## Part 4: Platform Health Dashboard

Create `grafana/dashboards/platform/prometheus-health.json`:

```json
{
  "dashboard": {
    "title": "Prometheus - Platform Health",
    "uid": "prometheus-health",
    "tags": ["platform", "prometheus", "monitoring"],
    "timezone": "UTC",
    "refresh": "1m",

    "panels": [
      {
        "id": 1,
        "type": "stat",
        "title": "Targets Up",
        "gridPos": {"h": 4, "w": 6, "x": 0, "y": 0},
        "targets": [
          {
            "expr": "count(up == 1)",
            "refId": "A"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "none",
            "thresholds": {
              "mode": "absolute",
              "steps": [
                {"color": "red", "value": null},
                {"color": "yellow", "value": 5},
                {"color": "green", "value": 8}
              ]
            }
          }
        },
        "options": {
          "graphMode": "area",
          "colorMode": "background"
        },
        "description": "Number of scrape targets currently up.\n\nExpected: 8-10 targets\n\nIf < 8: Investigate which targets are down using Status -> Targets page."
      },
      {
        "id": 2,
        "type": "stat",
        "title": "TSDB Head Series",
        "gridPos": {"h": 4, "w": 6, "x": 6, "y": 0},
        "targets": [
          {
            "expr": "prometheus_tsdb_head_series",
            "refId": "A"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "short",
            "decimals": 0,
            "thresholds": {
              "mode": "absolute",
              "steps": [
                {"color": "green", "value": null},
                {"color": "yellow", "value": 50000},
                {"color": "red", "value": 100000}
              ]
            }
          }
        },
        "options": {
          "graphMode": "area",
          "colorMode": "background"
        },
        "description": "Number of active time series in TSDB head (in-memory).\n\nTarget: < 100,000 series\n\nIf > 100,000:\n1. Check for cardinality explosion\n2. Review metric relabeling rules\n3. Consider horizontal scaling"
      },
      {
        "id": 3,
        "type": "timeseries",
        "title": "Scrape Duration P99",
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 4},
        "targets": [
          {
            "expr": "histogram_quantile(0.99, sum(rate(prometheus_target_interval_length_seconds_bucket[5m])) by (job, le))",
            "refId": "A",
            "legendFormat": "{{job}}"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "s",
            "thresholds": {
              "mode": "absolute",
              "steps": [
                {"color": "green", "value": null},
                {"color": "yellow", "value": 5},
                {"color": "red", "value": 10}
              ]
            }
          }
        },
        "options": {
          "legend": {
            "displayMode": "table",
            "placement": "right"
          }
        },
        "description": "P99 scrape duration by job.\n\nIf > 10s:\n1. Target may be slow or overloaded\n2. Check target resource usage\n3. Consider increasing scrape timeout"
      },
      {
        "id": 4,
        "type": "table",
        "title": "Top Metrics by Cardinality",
        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 4},
        "targets": [
          {
            "expr": "topk(10, count by (__name__)({__name__!=\"\"}))",
            "refId": "A",
            "format": "table",
            "instant": true
          }
        ],
        "fieldConfig": {
          "defaults": {
            "custom": {
              "displayMode": "color-background"
            }
          }
        },
        "description": "Top 10 metrics by series count.\n\nHigh cardinality metrics can cause performance issues.\n\nReview metrics with > 10,000 series for optimization opportunities."
      }
    ]
  }
}
```

**✅ Checkpoint:** Platform health dashboard created.

---

## Part 5: Executive SLO Overview Dashboard

Create `grafana/dashboards/executive/slo-overview.json`:

```json
{
  "dashboard": {
    "title": "SLO Overview - Executive Dashboard",
    "uid": "slo-overview",
    "tags": ["slo", "executive", "business"],
    "timezone": "UTC",
    "refresh": "5m",

    "panels": [
      {
        "id": 1,
        "type": "stat",
        "title": "30-Day Availability",
        "gridPos": {"h": 6, "w": 8, "x": 0, "y": 0},
        "targets": [
          {
            "expr": "avg_over_time(slo:service_availability:ratio_rate30m{service=\"inference-gateway\"}[30d]) * 100",
            "refId": "A"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "percent",
            "decimals": 3,
            "thresholds": {
              "mode": "absolute",
              "steps": [
                {"color": "red", "value": null},
                {"color": "yellow", "value": 99.0},
                {"color": "green", "value": 99.5}
              ]
            }
          }
        },
        "options": {
          "graphMode": "area",
          "colorMode": "background",
          "textMode": "value_and_name",
          "orientation": "horizontal",
          "reduceOptions": {
            "calcs": ["mean"]
          }
        },
        "description": "30-day rolling average availability.\n\nSLO Target: 99.5%\nError Budget: 0.5% (216 minutes/month)"
      },
      {
        "id": 2,
        "type": "bargauge",
        "title": "Error Budget Consumption",
        "gridPos": {"h": 6, "w": 8, "x": 8, "y": 0},
        "targets": [
          {
            "expr": "(1 - slo:service_availability:error_budget_remaining{service=\"inference-gateway\"}) * 100",
            "refId": "A",
            "legendFormat": "Budget Used"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "percent",
            "min": 0,
            "max": 100,
            "thresholds": {
              "mode": "absolute",
              "steps": [
                {"color": "green", "value": null},
                {"color": "yellow", "value": 50},
                {"color": "orange", "value": 75},
                {"color": "red", "value": 90}
              ]
            }
          }
        },
        "options": {
          "orientation": "horizontal",
          "displayMode": "gradient",
          "showUnfilled": true
        },
        "description": "Percentage of monthly error budget consumed.\n\n<50% = On track\n50-75% = Monitor closely\n75-90% = Freeze non-critical changes\n>90% = Critical - all hands on reliability"
      },
      {
        "id": 3,
        "type": "table",
        "title": "SLO Compliance Summary (30d)",
        "gridPos": {"h": 6, "w": 8, "x": 16, "y": 0},
        "targets": [
          {
            "expr": "avg_over_time(slo:service_availability:ratio_rate30m[30d]) * 100",
            "refId": "availability",
            "format": "table",
            "instant": true
          },
          {
            "expr": "avg_over_time(slo:service_latency:success_ratio_rate30m[30d]) * 100",
            "refId": "latency",
            "format": "table",
            "instant": true
          },
          {
            "expr": "(1 - avg_over_time(slo:service_error_rate:ratio_rate30m[30d])) * 100",
            "refId": "errors",
            "format": "table",
            "instant": true
          }
        ],
        "transformations": [
          {
            "id": "merge"
          },
          {
            "id": "organize",
            "options": {
              "renameByName": {
                "Value #availability": "Availability %",
                "Value #latency": "Latency SLO %",
                "Value #errors": "Error SLO %"
              }
            }
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "percent",
            "decimals": 2,
            "custom": {
              "displayMode": "color-background"
            },
            "thresholds": {
              "mode": "absolute",
              "steps": [
                {"color": "red", "value": null},
                {"color": "yellow", "value": 99.0},
                {"color": "green", "value": 99.5}
              ]
            }
          }
        },
        "description": "30-day SLO compliance across all SLIs.\n\nAll metrics should be green (> 99.5%)."
      },
      {
        "id": 4,
        "type": "timeseries",
        "title": "Total Inference Requests (30d)",
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 6},
        "targets": [
          {
            "expr": "sum(increase(inference_requests_total{service=\"inference-gateway\"}[1d]))",
            "refId": "A",
            "legendFormat": "Daily Requests"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "short",
            "custom": {
              "drawStyle": "bars",
              "barAlignment": 0,
              "lineWidth": 1,
              "fillOpacity": 80
            }
          }
        },
        "options": {
          "legend": {
            "displayMode": "list",
            "placement": "bottom"
          }
        },
        "description": "Daily inference request volume over 30 days.\n\nBusiness metric: Total predictions served."
      },
      {
        "id": 5,
        "type": "stat",
        "title": "Mean Time to Recovery (MTTR)",
        "gridPos": {"h": 4, "w": 6, "x": 12, "y": 6},
        "targets": [
          {
            "expr": "avg(ALERTS_FOR_STATE{alertstate=\"firing\"})",
            "refId": "A"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "s",
            "decimals": 0,
            "thresholds": {
              "mode": "absolute",
              "steps": [
                {"color": "green", "value": null},
                {"color": "yellow", "value": 1800},  // 30 min
                {"color": "red", "value": 3600}      // 1 hour
              ]
            }
          }
        },
        "options": {
          "graphMode": "none",
          "colorMode": "background"
        },
        "description": "Average time to resolve incidents (time from alert firing to resolved).\n\nTarget: < 30 minutes\n\nNote: Calculated from Prometheus alert duration."
      },
      {
        "id": 6,
        "type": "stat",
        "title": "Deployment Frequency (30d)",
        "gridPos": {"h": 4, "w": 6, "x": 18, "y": 6},
        "targets": [
          {
            "expr": "count(changes(process_start_time_seconds{service=\"inference-gateway\"}[30d]) > 0)",
            "refId": "A"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "short",
            "decimals": 0
          }
        },
        "options": {
          "graphMode": "area",
          "colorMode": "value",
          "textMode": "value_and_name"
        },
        "description": "Number of deployments in the last 30 days.\n\nHigher deployment frequency (with maintained stability) indicates healthy DevOps practices."
      }
    ]
  }
}
```

**✅ Checkpoint:** Executive dashboard created.

---

## Part 6: Grafana Unified Alerting

### Step 6.1: Create Alert Rules via Provisioning

Create `grafana/provisioning/alerting/rules.yml`:

```yaml
# grafana/provisioning/alerting/rules.yml
apiVersion: 1

groups:
  - orgId: 1
    name: inference-gateway-alerts
    folder: AI Infrastructure
    interval: 1m
    rules:
      - uid: latency-high
        title: Inference Latency High
        condition: C
        data:
          - refId: A
            relativeTimeRange:
              from: 600
              to: 0
            datasourceUid: prometheus
            model:
              expr: slo:service_latency:p99_rate5m{service="inference-gateway"}
              refId: A
          - refId: B
            relativeTimeRange:
              from: 0
              to: 0
            datasourceUid: __expr__
            model:
              type: reduce
              expression: A
              reducer: last
              refId: B
          - refId: C
            relativeTimeRange:
              from: 0
              to: 0
            datasourceUid: __expr__
            model:
              type: threshold
              expression: B
              conditions:
                - evaluator:
                    params: [0.3]
                    type: gt
                  operator:
                    type: and
                  query:
                    params: [C]
                  type: query
              refId: C
        noDataState: OK
        execErrState: Alerting
        for: 10m
        annotations:
          summary: "P99 latency exceeds 300ms SLO"
          description: "Inference gateway P99 latency is {{ $values.B }} seconds, exceeding the 300ms SLO target."
          runbook_url: "https://runbooks.example.com/high-latency"
        labels:
          severity: warning
          service: inference-gateway
          team: ml-platform
```

### Step 6.2: Create Notification Contact Points

Create `grafana/provisioning/alerting/contact-points.yml`:

```yaml
# grafana/provisioning/alerting/contact-points.yml
apiVersion: 1

contactPoints:
  - orgId: 1
    name: slack-critical
    receivers:
      - uid: slack-critical
        type: slack
        settings:
          url: https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK
          recipient: "#ml-platform-alerts-critical"
          username: Grafana Alert
          icon_emoji: ":rotating_light:"
          title: "{{ .GroupLabels.alertname }}"
          text: |
            {{ range .Alerts }}
            *Summary:* {{ .Annotations.summary }}
            *Description:* {{ .Annotations.description }}
            *Severity:* {{ .Labels.severity }}
            *Service:* {{ .Labels.service }}
            *Runbook:* {{ .Annotations.runbook_url }}
            {{ end }}

  - orgId: 1
    name: slack-warnings
    receivers:
      - uid: slack-warnings
        type: slack
        settings:
          url: https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK
          recipient: "#ml-platform-alerts-warnings"
          username: Grafana Alert
          icon_emoji: ":warning:"

  - orgId: 1
    name: pagerduty
    receivers:
      - uid: pagerduty
        type: pagerduty
        settings:
          integrationKey: YOUR_PAGERDUTY_KEY
          severity: critical
```

### Step 6.3: Create Notification Policies

Create `grafana/provisioning/alerting/policies.yml`:

```yaml
# grafana/provisioning/alerting/policies.yml
apiVersion: 1

policies:
  - orgId: 1
    receiver: slack-warnings  # Default receiver
    group_by: ['alertname', 'service']
    group_wait: 30s
    group_interval: 5m
    repeat_interval: 12h
    routes:
      # Critical alerts -> PagerDuty + Slack
      - receiver: pagerduty
        matchers:
          - severity = critical
        group_wait: 10s
        group_interval: 2m
        repeat_interval: 4h
        continue: true  # Also route to Slack

      - receiver: slack-critical
        matchers:
          - severity = critical

      # Warning alerts -> Slack only
      - receiver: slack-warnings
        matchers:
          - severity = warning
```

**✅ Checkpoint:** Grafana alerting is configured.

---

## Part 7: Dashboard as Code and GitOps

### Step 7.1: Export Dashboards to Version Control

```bash
# Create dashboards directory in Git
mkdir -p git-repo/grafana/dashboards

# Export all dashboards via Grafana API
for uid in inference-gateway-service prometheus-health slo-overview; do
  curl -s -H "Authorization: Bearer YOUR_API_KEY" \
    http://localhost:3000/api/dashboards/uid/$uid \
    | jq '.dashboard' \
    > git-repo/grafana/dashboards/${uid}.json
done

# Commit to version control
cd git-repo
git add grafana/
git commit -m "Add Grafana dashboards for inference gateway"
git push
```

### Step 7.2: Create Dashboard Update Process

Create `docs/dashboard-update-process.md`:

```markdown
# Dashboard Update Process

## Making Changes to Dashboards

1. **Development**:
   - Make changes in Grafana UI (lab environment)
   - Test thoroughly with real data
   - Screenshot before/after for review

2. **Export**:
   ```bash
   scripts/export-dashboard.sh <dashboard-uid>
   ```

3. **Review**:
   - Open pull request with exported JSON
   - Include screenshots in PR description
   - Request review from dashboard owner

4. **Deploy**:
   - Merge PR to main branch
   - CI/CD pipeline updates provisioned dashboards
   - Verify in staging, then production

## Dashboard Ownership

| Dashboard | Owner | Slack Channel | Review Cadence |
|-----------|-------|---------------|----------------|
| Inference Gateway Service | @ml-platform-oncall | #ml-platform | Weekly |
| Prometheus Health | @platform-sre | #platform | Monthly |
| SLO Overview | @engineering-manager | #leadership | Monthly |

## Quality Standards

- **Performance**: All panels must load in < 5 seconds
- **Clarity**: Panel titles and descriptions must be clear
- **Thresholds**: All stat panels must have appropriate thresholds
- **Documentation**: Link to runbooks in panel descriptions
- **Variables**: Use templating for multi-environment support
```

**✅ Checkpoint:** Dashboard-as-code workflow established.

---

## Part 8: Validation and Documentation

### Step 8.1: Create Dashboard Test Plan

Create `docs/dashboard-test-plan.md`:

```markdown
# Dashboard Test Plan

## Pre-Deployment Checklist

- [ ] All data sources connected and healthy
- [ ] All panels load data within 5 seconds
- [ ] Variables work correctly (change values, verify panels update)
- [ ] Thresholds display correct colors
- [ ] Panel descriptions are clear and actionable
- [ ] Links to runbooks work
- [ ] Annotations appear for deployments
- [ ] Dashboard exports to JSON without errors
- [ ] Provisioning file syntax is valid

## Load Testing

1. Generate traffic with load test:
   ```bash
   scripts/load-test-metrics.sh --duration=10m --rate=100
   ```

2. Verify dashboards update in real-time
3. Check for query performance issues
4. Validate alert thresholds trigger correctly

## User Acceptance Testing

1. Share dashboard with on-call engineer
2. Ask them to complete incident simulation
3. Collect feedback on panel usefulness
4. Iterate based on feedback
```

### Step 8.2: Create README

Update `README.md`:

```markdown
# Grafana Dashboards

## Quick Start

```bash
# Start Grafana
docker-compose up -d grafana

# Access Grafana
open http://localhost:3000

# Login: admin / admin
```

## Dashboards

### Service Dashboards

**Inference Gateway** (`inference-gateway-service`)
- URL: http://localhost:3000/d/inference-gateway-service
- Purpose: Real-time operational visibility for on-call engineers
- Owner: ML Platform Team (#ml-platform)
- Key Metrics: SLO compliance, latency, errors, resources

### Platform Dashboards

**Prometheus Health** (`prometheus-health`)
- URL: http://localhost:3000/d/prometheus-health
- Purpose: Monitor the monitoring stack
- Owner: Platform SRE (#platform-sre)
- Key Metrics: Scrape health, TSDB metrics, cardinality

### Executive Dashboards

**SLO Overview** (`slo-overview`)
- URL: http://localhost:3000/d/slo-overview
- Purpose: Weekly SLO review and OKR tracking
- Owner: Engineering Manager (#leadership)
- Key Metrics: 30-day availability, error budget, MTTR

## Updating Dashboards

See [docs/dashboard-update-process.md](docs/dashboard-update-process.md)

## Alerting

Grafana unified alerting is enabled. Alerts route to:
- Critical → PagerDuty + Slack (#ml-platform-alerts-critical)
- Warning → Slack (#ml-platform-alerts-warnings)

## Troubleshooting

**Dashboard not loading data:**
1. Check data source connection (Configuration → Data Sources)
2. Verify Prometheus is scraping targets (Status → Targets in Prometheus)
3. Check query syntax in panel edit mode

**Variables not working:**
1. Verify query returns data (test in Explore)
2. Check variable regex syntax
3. Ensure labels exist in metrics

**Provisioned dashboards not appearing:**
1. Check provisioning logs: `docker-compose logs grafana | grep provisioning`
2. Verify JSON syntax: `jsonlint dashboards/service/inference-gateway.json`
3. Restart Grafana: `docker-compose restart grafana`
```

**✅ Checkpoint:** Documentation is complete.

---

## Part 9: Stretch Goals and Advanced Topics

### Optional Enhancement 1: Dynamic Drill-Down Links

Add panel links for drill-down navigation:

```json
{
  "links": [
    {
      "title": "View in Jaeger",
      "url": "http://localhost:16686/search?service=inference-gateway&start=${__from:date:seconds}000&end=${__to:date:seconds}000",
      "targetBlank": true
    },
    {
      "title": "View Logs in Loki",
      "url": "http://localhost:3000/explore?left=%5B%22now-1h%22,%22now%22,%22Loki%22,%7B%22expr%22:%22%7Bservice%3D%5C%22inference-gateway%5C%22%7D%22%7D%5D",
      "targetBlank": true
    }
  ]
}
```

### Optional Enhancement 2: Cost Dashboards

If cloud billing data is available (BigQuery, Athena):

```json
{
  "id": 100,
  "type": "stat",
  "title": "Cost per 1M Requests",
  "targets": [
    {
      "expr": "(sum(gcp_billing_total_cost{project=\"ml-platform\"}[30d]) / sum(increase(http_requests_total[30d]))) * 1000000",
      "refId": "A"
    }
  ],
  "fieldConfig": {
    "defaults": {
      "unit": "currencyUSD",
      "decimals": 2
    }
  }
}
```

### Optional Enhancement 3: Grafana Reporting

Set up scheduled PDF reports:

```yaml
# In Grafana UI: Share → Export → Create Report

# Or via API:
POST /api/reports
{
  "name": "Weekly SLO Report",
  "dashboards": [
    {"uid": "slo-overview"}
  ],
  "recipients": "engineering-manager@example.com",
  "replyTo": "noreply@example.com",
  "message": "Weekly SLO compliance report",
  "schedule": {
    "frequency": "weekly",
    "dayOfMonth": "1",
    "timeZone": "America/New_York"
  }
}
```

---

## Summary and Reflection

Congratulations! You've built a comprehensive Grafana dashboard suite that transforms Prometheus metrics into actionable operational insights.

**What You Built**:
1. ✅ Complete Grafana deployment with Docker Compose
2. ✅ Multiple data sources (Prometheus, Loki, Tempo, Alertmanager)
3. ✅ Service dashboard with 20+ panels covering SLOs, latency, traffic, errors, ML metrics
4. ✅ Platform health dashboard for monitoring infrastructure
5. ✅ Executive SLO overview for business visibility
6. ✅ Grafana unified alerting with contact points and policies
7. ✅ Dashboard provisioning as code for version control
8. ✅ Dashboard governance and update processes

**Skills Gained**:
- Designing effective dashboards for different audiences
- Building complex PromQL queries for visualizations
- Implementing dashboard templating and variables
- Configuring Grafana alerting with notification routing
- Establishing dashboard-as-code workflows
- Applying visualization best practices
- Creating dashboard ownership models

### Deliverables Checklist

- ✅ Grafana deployed and configured
- ✅ Service dashboard for inference gateway
- ✅ Platform health dashboard
- ✅ Executive SLO overview dashboard
- ✅ Grafana alerting rules and contact points
- ✅ Dashboard provisioning configuration
- ✅ Dashboard update process documentation
- ✅ README with dashboard catalog

### Reflection Questions

1. **How does templating improve dashboard reuse across environments?**
   - Consider: Variable substitution, multi-tenancy, environment isolation
   - Think about: Maintenance burden, consistency, scalability

2. **Which panels would you prioritize during an incident vs a postmortem review?**
   - Incident: Real-time latency, error rates, recent deployments
   - Postmortem: Historical trends, SLO compliance, timeline reconstruction

3. **How would you validate that dashboards remain accurate as services evolve?**
   - Automated testing of PromQL queries
   - Regular review with dashboard owners
   - Alerts for missing metrics
   - Dashboard versioning in Git

4. **What processes ensure stakeholders trust the visualizations?**
   - Document data sources and calculation methods
   - Regular review and validation
   - Clear ownership and accountability
   - Version control and change management

---

## Next Steps

**In Exercise 04** (Logging Pipeline), you will:
- Deploy Loki for centralized log aggregation
- Configure Promtail for log shipping
- Build log parsing and filtering pipelines
- Create log-based metrics
- Integrate logs with traces for unified debugging

**Continue to:** [Exercise 04: Logging Pipeline](exercise-04-logging-pipeline.md)

---

**Exercise 03 Complete!** 🎉

You've transformed raw metrics into visual narratives that drive operational excellence and business decisions.
