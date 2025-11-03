# Exercise 08: SLO and Error Budget Management for ML Services

## Overview
Implement Service Level Objectives (SLOs) and error budget tracking for ML services. Learn to define meaningful SLIs, set realistic SLOs, calculate error budgets, and use them for informed decision-making about reliability versus feature velocity.

**Duration:** 3-4 hours
**Difficulty:** Advanced

## Learning Objectives
By completing this exercise, you will:
- Define Service Level Indicators (SLIs) for ML services
- Set achievable Service Level Objectives (SLOs)
- Calculate and track error budgets
- Implement multi-window multi-burn-rate alerting (Google SRE approach)
- Create SLO dashboards for stakeholder communication
- Make data-driven decisions using error budgets
- Balance reliability work vs feature development

## Prerequisites
- Completed PromQL and Recording Rules exercise
- Prometheus and Grafana installed
- Understanding of percentiles and availability calculations
- Basic knowledge of SRE principles

## Scenario
Your **ML Platform** team needs to formalize reliability targets. Currently:
- No clear reliability targets
- Unclear when to prioritize bug fixes vs new features
- Disagreement between team on "good enough" performance
- Users complaining inconsistently about reliability

You'll define SLOs for 3 services:
1. **Model Serving API** - Real-time inference
2. **Batch Inference** - Nightly processing jobs
3. **Feature Store** - Real-time feature serving

Each needs different SLOs based on user expectations and business requirements.

## Tasks

### Task 1: Understanding SLI, SLO, SLA

**TODO 1.1:** Document the hierarchy

```markdown
# SLI vs SLO vs SLA

## SLI (Service Level Indicator)
**Definition**: Quantitative measure of service level
**Examples**:
- Request success rate
- Request latency (p50, p95, p99)
- Data freshness
- Model prediction accuracy

## SLO (Service Level Objective)
**Definition**: Target value or range for an SLI
**Examples**:
- 99.9% of requests succeed (availability SLO)
- 95% of requests complete in <200ms (latency SLO)
- Model accuracy stays >92% (quality SLO)

## SLA (Service Level Agreement)
**Definition**: Business contract with consequences for missing SLO
**Examples**:
- "We guarantee 99.5% uptime or you get 10% credit"
- Less strict than internal SLO (buffer for safety)

## Key Principle
SLI < SLO < SLA
(actual < internal target < contractual obligation)
```

**TODO 1.2:** Calculate error budget

```python
# calculate_error_budget.py
def calculate_error_budget(slo_target: float, time_period_days: int = 30):
    """
    Calculate error budget given an SLO target.

    Args:
        slo_target: Target availability (e.g., 0.999 for 99.9%)
        time_period_days: Time period for budget (default 30 days)

    Returns:
        dict: Error budget details
    """
    total_minutes = time_period_days * 24 * 60
    allowed_error_rate = 1 - slo_target
    error_budget_minutes = total_minutes * allowed_error_rate

    return {
        "slo_target": f"{slo_target * 100}%",
        "allowed_error_rate": f"{allowed_error_rate * 100}%",
        "total_minutes": total_minutes,
        "error_budget_minutes": error_budget_minutes,
        "error_budget_hours": error_budget_minutes / 60,
        "error_budget_days": error_budget_minutes / 60 / 24
    }

# TODO: Calculate error budgets for different SLO targets
print("=== Error Budget Comparison ===\n")

targets = [0.99, 0.995, 0.999, 0.9999]
for target in targets:
    budget = calculate_error_budget(target)
    print(f"SLO: {budget['slo_target']}")
    print(f"  Allowed downtime: {budget['error_budget_minutes']:.2f} min/month")
    print(f"  ({budget['error_budget_hours']:.2f} hours)")
    print()

# Example output:
# SLO: 99.0%
#   Allowed downtime: 432.00 min/month (7.20 hours)
#
# SLO: 99.9%
#   Allowed downtime: 43.20 min/month (0.72 hours)
#
# SLO: 99.99%
#   Allowed downtime: 4.32 min/month (0.07 hours)
```

### Task 2: Define SLIs for ML Services

**TODO 2.1:** Model Serving API SLIs

```yaml
# slis_model_serving.yaml
slis:
  availability:
    description: "Proportion of successful requests"
    measurement: |
      (total_requests - failed_requests) / total_requests
    promql: |
      (
        sum(rate(http_requests_total{job="model-api",code=~"2.."}[5m]))
      ) / (
        sum(rate(http_requests_total{job="model-api"}[5m]))
      )
    good_event: "HTTP 2xx response"
    valid_event: "All HTTP requests"

  latency:
    description: "Proportion of requests completing fast enough"
    measurement: |
      requests_under_threshold / total_requests
    promql: |
      histogram_quantile(0.95,
        sum(rate(http_request_duration_seconds_bucket{job="model-api"}[5m])) by (le)
      )
    threshold: "200ms for 95th percentile"
    good_event: "Request completes in <200ms"
    valid_event: "All HTTP requests"

  quality:
    description: "Model prediction quality over time"
    measurement: |
      Accuracy drift from baseline
    promql: |
      model_prediction_accuracy
    threshold: ">92% accuracy"
    good_event: "Prediction with >92% accuracy"
    valid_event: "All predictions with ground truth"
```

**TODO 2.2:** Implement SLI recording rules

```yaml
# sli-recording-rules.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: sli-recording-rules
  namespace: monitoring
data:
  sli_rules.yml: |
    groups:
    - name: sli_availability
      interval: 30s
      rules:
      # Availability SLI: ratio of successful requests
      - record: sli:availability:ratio
        labels:
          service: model-api
        expr: |
          (
            sum(rate(http_requests_total{job="model-api",code=~"2.."}[5m]))
          ) / (
            sum(rate(http_requests_total{job="model-api"}[5m]))
          )

      # Latency SLI: ratio of fast requests (<200ms)
      - record: sli:latency:good_ratio
        labels:
          service: model-api
        expr: |
          (
            sum(rate(http_request_duration_seconds_bucket{job="model-api",le="0.2"}[5m]))
          ) / (
            sum(rate(http_request_duration_seconds_count{job="model-api"}[5m]))
          )

    - name: sli_quality
      interval: 300s  # Every 5 minutes
      rules:
      # Model quality SLI
      - record: sli:quality:accuracy_ratio
        labels:
          service: model-api
        expr: |
          (
            sum(model_correct_predictions_total)
          ) / (
            sum(model_total_predictions_with_ground_truth_total)
          )

    - name: sli_error_budget
      interval: 60s
      rules:
      # Error budget remaining (30-day window)
      - record: slo:error_budget:remaining_ratio
        labels:
          service: model-api
          slo: "99.9"
        expr: |
          1 - (
            (1 - sli:availability:ratio{service="model-api"})
            / (1 - 0.999)
          )

      # Error budget burn rate (how fast we're consuming budget)
      - record: slo:error_budget:burn_rate_1h
        labels:
          service: model-api
        expr: |
          (1 - sli:availability:ratio{service="model-api"}[1h])
          / (1 - 0.999)
```

```bash
# TODO: Apply SLI recording rules
kubectl apply -f sli-recording-rules.yaml
kubectl rollout restart deployment prometheus-server -n monitoring
```

### Task 3: Set SLO Targets

**TODO 3.1:** SLO selection matrix

```python
# slo_selection.py
"""
SLO Selection Guide for ML Services
"""

slo_targets = {
    "model_serving_api": {
        "availability": {
            "target": 0.999,  # 99.9%
            "rationale": "User-facing, real-time inference. High expectations.",
            "error_budget_30d": "43.2 minutes/month",
            "measurement_window": "30 days"
        },
        "latency_p95": {
            "target": 0.200,  # 200ms
            "rationale": "User experience degrades if slower. Based on user testing.",
            "measurement_window": "5 minutes"
        },
        "quality": {
            "target": 0.92,  # 92% accuracy
            "rationale": "Model retraining triggered if below this threshold.",
            "measurement_window": "24 hours"
        }
    },
    "batch_inference": {
        "success_rate": {
            "target": 0.95,  # 95%
            "rationale": "Batch jobs less critical, retries acceptable.",
            "error_budget_30d": "36 hours/month",
            "measurement_window": "30 days"
        },
        "completion_time": {
            "target": 4 * 3600,  # 4 hours
            "rationale": "Must complete before morning business hours.",
            "measurement_window": "per job"
        }
    },
    "feature_store": {
        "availability": {
            "target": 0.9999,  # 99.99%
            "rationale": "Critical dependency for all models. Very high availability.",
            "error_budget_30d": "4.32 minutes/month",
            "measurement_window": "30 days"
        },
        "latency_p99": {
            "target": 0.010,  # 10ms
            "rationale": "Must be fast to not impact model latency SLO.",
            "measurement_window": "5 minutes"
        }
    }
}

# TODO: Document SLO targets
for service, slos in slo_targets.items():
    print(f"\n=== {service.upper().replace('_', ' ')} ===")
    for slo_name, slo_config in slos.items():
        print(f"\n{slo_name}:")
        for key, value in slo_config.items():
            print(f"  {key}: {value}")
```

**TODO 3.2:** Create SLO configuration

```yaml
# slo-config.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: slo-config
  namespace: monitoring
data:
  slos.yaml: |
    slos:
    - name: model-api-availability
      service: model-api
      type: availability
      target: 0.999  # 99.9%
      window: 30d
      sli_query: sli:availability:ratio{service="model-api"}
      alert_thresholds:
        - window: 1h
          burn_rate: 14.4
          severity: critical
        - window: 6h
          burn_rate: 6
          severity: critical
        - window: 3d
          burn_rate: 1
          severity: warning

    - name: model-api-latency
      service: model-api
      type: latency
      target: 0.95  # 95% of requests under 200ms
      threshold: 200ms
      window: 7d
      sli_query: sli:latency:good_ratio{service="model-api"}
      alert_thresholds:
        - window: 1h
          burn_rate: 14.4
          severity: critical
        - window: 6h
          burn_rate: 6
          severity: warning

    - name: feature-store-availability
      service: feature-store
      type: availability
      target: 0.9999  # 99.99%
      window: 30d
      sli_query: sli:availability:ratio{service="feature-store"}
      alert_thresholds:
        - window: 5m
          burn_rate: 14.4
          severity: page
        - window: 1h
          burn_rate: 6
          severity: critical
```

### Task 4: Multi-Window Multi-Burn-Rate Alerting

**TODO 4.1:** Implement Google SRE alerting approach

```yaml
# slo-alerts.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: slo-alerts
  namespace: monitoring
data:
  slo_alerts.yml: |
    groups:
    - name: slo_fast_burn
      interval: 30s
      rules:
      # Fast burn: 14.4x burn rate over 1 hour
      # Consumes 2% of 30-day error budget in 1 hour
      - alert: ModelAPIErrorBudgetFastBurn
        expr: |
          (
            (1 - sli:availability:ratio{service="model-api"})
            / (1 - 0.999)
          ) > 14.4
          and
          (
            (1 - avg_over_time(sli:availability:ratio{service="model-api"}[1h]))
            / (1 - 0.999)
          ) > 14.4
        for: 2m
        labels:
          severity: critical
          service: model-api
          slo: availability
          page: "true"
        annotations:
          summary: "Fast error budget burn for Model API"
          description: |
            Model API is burning error budget at 14.4x rate.
            At this rate, entire monthly budget exhausted in 2 days.
            Current availability: {{ $value | humanizePercentage }}
          runbook: "https://wiki/runbooks/slo-fast-burn"

    - name: slo_moderate_burn
      interval: 60s
      rules:
      # Moderate burn: 6x burn rate over 6 hours
      # Consumes 5% of 30-day error budget in 6 hours
      - alert: ModelAPIErrorBudgetModerateBurn
        expr: |
          (
            (1 - avg_over_time(sli:availability:ratio{service="model-api"}[6h]))
            / (1 - 0.999)
          ) > 6
          and
          (
            (1 - avg_over_time(sli:availability:ratio{service="model-api"}[30m]))
            / (1 - 0.999)
          ) > 6
        for: 15m
        labels:
          severity: warning
          service: model-api
          slo: availability
        annotations:
          summary: "Moderate error budget burn for Model API"
          description: |
            Model API burning error budget at 6x rate over 6 hours.
            Monthly budget exhausted in 5 days at this rate.

    - name: slo_slow_burn
      interval: 300s
      rules:
      # Slow burn: 1x burn rate over 3 days
      # Steady consumption of error budget
      - alert: ModelAPIErrorBudgetSlowBurn
        expr: |
          (
            (1 - avg_over_time(sli:availability:ratio{service="model-api"}[3d]))
            / (1 - 0.999)
          ) > 1
        for: 1h
        labels:
          severity: info
          service: model-api
          slo: availability
        annotations:
          summary: "Sustained error budget burn for Model API"
          description: |
            Model API consuming error budget at steady rate.
            Budget will exhaust in ~30 days if trend continues.

    - name: slo_budget_exhausted
      interval: 300s
      rules:
      # Error budget completely exhausted
      - alert: ModelAPIErrorBudgetExhausted
        expr: slo:error_budget:remaining_ratio{service="model-api"} < 0
        for: 5m
        labels:
          severity: critical
          service: model-api
          freeze: "true"  # Trigger feature freeze
        annotations:
          summary: "Error budget EXHAUSTED for Model API"
          description: |
            30-day error budget completely exhausted.
            FEATURE FREEZE in effect - focus on reliability.
            Remaining budget: {{ $value | humanizePercentage }}
```

```bash
# TODO: Apply SLO alerts
kubectl apply -f slo-alerts.yaml
kubectl rollout restart deployment prometheus-server -n monitoring
```

**TODO 4.2:** Create alert decision matrix

```python
# alert_decision_matrix.py
"""
Multi-window multi-burn-rate alert thresholds.
Based on Google SRE Workbook Chapter 5.
"""

def generate_alert_windows(slo_target: float, window_days: int = 30):
    """
    Generate alert thresholds for different burn rates.

    Args:
        slo_target: SLO target (e.g., 0.999)
        window_days: SLO window in days
    """
    error_budget = 1 - slo_target

    alerts = [
        {
            "name": "Fast Burn - Page",
            "short_window": "1h",
            "long_window": "5m",
            "burn_rate": 14.4,
            "budget_consumed_1h": "2%",
            "time_to_exhaustion": f"{window_days / 14.4:.1f} days",
            "severity": "page",
            "response_time": "Immediate"
        },
        {
            "name": "Moderate Burn - Ticket",
            "short_window": "6h",
            "long_window": "30m",
            "burn_rate": 6,
            "budget_consumed_6h": "5%",
            "time_to_exhaustion": f"{window_days / 6:.1f} days",
            "severity": "ticket",
            "response_time": "Next business day"
        },
        {
            "name": "Slow Burn - Info",
            "short_window": "3d",
            "long_window": "6h",
            "burn_rate": 1,
            "budget_consumed_3d": "10%",
            "time_to_exhaustion": f"{window_days} days",
            "severity": "info",
            "response_time": "Weekly review"
        }
    ]

    print(f"=== Alert Windows for {slo_target*100}% SLO ({window_days}d) ===\n")
    for alert in alerts:
        print(f"{alert['name']}:")
        for key, value in alert.items():
            if key != "name":
                print(f"  {key}: {value}")
        print()

# TODO: Generate alert windows
generate_alert_windows(0.999, 30)
generate_alert_windows(0.9999, 30)
```

### Task 5: SLO Dashboard and Reporting

**TODO 5.1:** Create Grafana SLO dashboard

```json
{
  "dashboard": {
    "title": "ML Platform SLO Dashboard",
    "panels": [
      {
        "title": "Model API Availability SLO",
        "type": "gauge",
        "targets": [
          {
            "expr": "sli:availability:ratio{service='model-api'} * 100",
            "legendFormat": "Current Availability"
          }
        ],
        "thresholds": [
          {"value": 99.9, "color": "green"},
          {"value": 99.5, "color": "yellow"},
          {"value": 0, "color": "red"}
        ]
      },
      {
        "title": "Error Budget Remaining (30d)",
        "type": "graph",
        "targets": [
          {
            "expr": "slo:error_budget:remaining_ratio{service='model-api'} * 100",
            "legendFormat": "Budget Remaining %"
          }
        ]
      },
      {
        "title": "Error Budget Burn Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "slo:error_budget:burn_rate_1h{service='model-api'}",
            "legendFormat": "1h burn rate"
          }
        ]
      },
      {
        "title": "SLI Status Summary",
        "type": "stat",
        "targets": [
          {
            "expr": "sli:availability:ratio{service='model-api'}",
            "legendFormat": "Availability"
          },
          {
            "expr": "sli:latency:good_ratio{service='model-api'}",
            "legendFormat": "Latency"
          },
          {
            "expr": "sli:quality:accuracy_ratio{service='model-api'}",
            "legendFormat": "Quality"
          }
        ]
      }
    ]
  }
}
```

**TODO 5.2:** Generate SLO reports

```python
# generate_slo_report.py
import requests
from datetime import datetime, timedelta

PROM_URL = "http://localhost:9090"

def query_prometheus(query):
    """Query Prometheus and return result."""
    response = requests.get(
        f"{PROM_URL}/api/v1/query",
        params={"query": query}
    )
    result = response.json()["data"]["result"]
    return float(result[0]["value"][1]) if result else None

def generate_monthly_slo_report(service: str, slo_target: float):
    """Generate monthly SLO compliance report."""

    print(f"=== Monthly SLO Report: {service} ===")
    print(f"Report Date: {datetime.now().strftime('%Y-%m-%d')}")
    print(f"SLO Target: {slo_target * 100}%\n")

    # Current availability
    availability = query_prometheus(
        f'sli:availability:ratio{{service="{service}"}}'
    )
    print(f"Current Availability: {availability * 100:.3f}%")

    # Error budget remaining
    error_budget = query_prometheus(
        f'slo:error_budget:remaining_ratio{{service="{service}"}}'
    )
    print(f"Error Budget Remaining: {error_budget * 100:.2f}%")

    # SLO compliance
    compliance = "✓ MEETING SLO" if availability >= slo_target else "✗ VIOLATING SLO"
    print(f"Status: {compliance}\n")

    # Calculate downtime
    total_minutes_30d = 30 * 24 * 60
    actual_downtime = (1 - availability) * total_minutes_30d
    allowed_downtime = (1 - slo_target) * total_minutes_30d

    print(f"Downtime Analysis:")
    print(f"  Actual downtime: {actual_downtime:.2f} minutes")
    print(f"  Allowed downtime: {allowed_downtime:.2f} minutes")
    print(f"  Difference: {allowed_downtime - actual_downtime:.2f} minutes\n")

    # Recommendations
    print("Recommendations:")
    if error_budget < 0:
        print("  ⚠️  FEATURE FREEZE - Focus on reliability")
        print("  ⚠️  Root cause analysis required")
        print("  ⚠️  Incident review meeting")
    elif error_budget < 0.25:
        print("  ⚠️  Low error budget - Prioritize stability")
        print("  ⚠️  Defer risky changes")
    elif error_budget > 0.75:
        print("  ✓ Healthy error budget - Can take risks")
        print("  ✓ Good time for experiments")
    else:
        print("  ✓ Normal operations")

# TODO: Generate report
generate_monthly_slo_report("model-api", 0.999)
```

### Task 6: Error Budget Policy

**TODO 6.1:** Create error budget policy document

```markdown
# ML Platform Error Budget Policy

## Purpose
Define how we use error budgets to balance feature velocity and reliability.

## Error Budget Definition
- **30-day rolling window** for all services
- Budget = (1 - SLO) × time period
- Example: 99.9% SLO = 43.2 minutes downtime/month allowed

## Decision Framework

### 100% - 75% Budget Remaining: GREEN
**Actions**:
- Normal feature development pace
- Can take calculated risks
- Good time for experiments and refactoring
- Deploy during business hours acceptable

**Restrictions**: None

### 75% - 25% Budget Remaining: YELLOW
**Actions**:
- Elevated caution
- Prioritize stability over new features
- Increased testing requirements
- Deploy outside business hours preferred

**Restrictions**:
- No risky architectural changes
- Require senior engineer approval for deploys

### 25% - 0% Budget Remaining: ORANGE
**Actions**:
- Focus on reliability
- Bug fixes only
- Comprehensive testing mandatory
- Deploy only during low-traffic windows

**Restrictions**:
- No new features
- Emergency changes require VP approval

### <0% Budget Exhausted: RED (FEATURE FREEZE)
**Actions**:
- COMPLETE FEATURE FREEZE
- All hands on reliability
- Incident post-mortem required
- Root cause analysis

**Restrictions**:
- No deploys except critical fixes
- CEO approval required for any changes

## Exemptions
- Security patches (always allowed)
- Data loss prevention (always allowed)
- Legal/compliance requirements (case-by-case)

## Escalation
- YELLOW: Engineering Manager notified
- ORANGE: VP Engineering notified
- RED: Executive team notified

## Review Cadence
- Weekly: Review error budget status
- Monthly: Review SLO targets
- Quarterly: Review policy effectiveness
```

**TODO 6.2:** Implement automated policy enforcement

```python
# error_budget_policy.py
from enum import Enum
from dataclasses import dataclass

class BudgetZone(Enum):
    GREEN = "green"
    YELLOW = "yellow"
    ORANGE = "orange"
    RED = "red"

@dataclass
class PolicyAction:
    zone: BudgetZone
    can_deploy: bool
    can_new_features: bool
    approval_required: str
    notification_required: list

def get_policy_for_budget(budget_remaining: float) -> PolicyAction:
    """
    Determine policy actions based on remaining error budget.

    Args:
        budget_remaining: Remaining error budget (0.0 to 1.0)

    Returns:
        PolicyAction with restrictions and requirements
    """
    if budget_remaining >= 0.75:
        return PolicyAction(
            zone=BudgetZone.GREEN,
            can_deploy=True,
            can_new_features=True,
            approval_required="standard",
            notification_required=[]
        )
    elif budget_remaining >= 0.25:
        return PolicyAction(
            zone=BudgetZone.YELLOW,
            can_deploy=True,
            can_new_features=True,
            approval_required="senior_engineer",
            notification_required=["engineering_manager"]
        )
    elif budget_remaining >= 0:
        return PolicyAction(
            zone=BudgetZone.ORANGE,
            can_deploy=True,
            can_new_features=False,
            approval_required="engineering_manager",
            notification_required=["engineering_manager", "vp_engineering"]
        )
    else:  # < 0
        return PolicyAction(
            zone=BudgetZone.RED,
            can_deploy=False,
            can_new_features=False,
            approval_required="vp_engineering",
            notification_required=["engineering_manager", "vp_engineering", "ceo"]
        )

# TODO: Check policy before deployment
def check_deployment_allowed(service: str, budget_remaining: float, change_type: str) -> bool:
    """
    Check if deployment is allowed based on error budget policy.

    Args:
        service: Service name
        budget_remaining: Current error budget remaining (0-1)
        change_type: "feature", "bugfix", "security", "refactor"

    Returns:
        bool: True if deployment allowed
    """
    policy = get_policy_for_budget(budget_remaining)

    print(f"=== Deployment Policy Check ===")
    print(f"Service: {service}")
    print(f"Error Budget Remaining: {budget_remaining * 100:.1f}%")
    print(f"Zone: {policy.zone.value.upper()}")
    print(f"Change Type: {change_type}")
    print()

    # Security patches always allowed
    if change_type == "security":
        print("✓ ALLOWED: Security patches exempt from policy")
        return True

    # Check zone restrictions
    if policy.zone == BudgetZone.RED:
        print("✗ BLOCKED: Feature freeze in effect")
        print(f"Approval required: {policy.approval_required}")
        return False

    if policy.zone == BudgetZone.ORANGE and change_type == "feature":
        print("✗ BLOCKED: No new features in ORANGE zone")
        print("Only bug fixes allowed")
        return False

    print(f"✓ ALLOWED (Approval: {policy.approval_required})")
    if policy.notification_required:
        print(f"Notifications: {', '.join(policy.notification_required)}")

    return True

# TODO: Run policy checks
check_deployment_allowed("model-api", 0.85, "feature")
check_deployment_allowed("model-api", 0.15, "feature")
check_deployment_allowed("model-api", -0.05, "bugfix")
check_deployment_allowed("model-api", -0.05, "security")
```

## Deliverables

Submit a repository with:

1. **SLO Documentation** (`SLO_SPEC.md`)
   - Defined SLIs for each service
   - SLO targets with rationale
   - Error budget calculations
   - Measurement methodology

2. **Prometheus Configuration**
   - SLI recording rules
   - Multi-window multi-burn-rate alerts
   - Error budget tracking queries

3. **Error Budget Policy** (`ERROR_BUDGET_POLICY.md`)
   - Decision framework
   - Deployment restrictions by zone
   - Escalation procedures

4. **Dashboards**
   - Grafana SLO dashboard JSON
   - Error budget visualization
   - Burn rate charts

5. **Scripts**
   - `generate_slo_report.py` - Monthly reports
   - `check_deployment_allowed.py` - Policy enforcement
   - `calculate_error_budget.py` - Budget calculator

## Success Criteria

- [ ] SLIs defined for 3+ services with clear measurement methodology
- [ ] SLO targets set with business justification
- [ ] Error budgets calculated and tracked in Prometheus
- [ ] Multi-window multi-burn-rate alerts implemented
- [ ] Alert thresholds validated (not too noisy, catch real issues)
- [ ] SLO dashboard created and accessible to stakeholders
- [ ] Error budget policy documented and communicated
- [ ] Automated policy checks prevent violations
- [ ] Monthly SLO reports generated
- [ ] Team understands how to use error budgets for decision-making

## Bonus Challenges

1. **Composite SLOs**: Create SLO that depends on multiple services
2. **User Journey SLO**: Track end-to-end user experience across services
3. **SLO Simulator**: Build tool to simulate impact of incidents on error budget
4. **Automated Postmortems**: Generate incident reports from SLO violations
5. **SLO-based Alerting Only**: Remove all symptom-based alerts, use only SLO alerts
6. **Cost Attribution**: Link error budget consumption to infrastructure costs

## Resources

- [Google SRE Book - Service Level Objectives](https://sre.google/sre-book/service-level-objectives/)
- [Google SRE Workbook - Implementing SLOs](https://sre.google/workbook/implementing-slos/)
- [Sloth - SLO Generator](https://sloth.dev/)
- [SLO Workshop by Google](https://github.com/google/slo-generator)
- [The Art of SLOs by Alex Hidalgo](https://www.alexhidalgo.com)

## Evaluation Rubric

| Criteria | Points |
|----------|--------|
| SLI definition and measurement | 15 |
| SLO target selection with rationale | 15 |
| Error budget calculation and tracking | 15 |
| Multi-window multi-burn-rate alerting | 20 |
| SLO dashboard and visualization | 15 |
| Error budget policy and enforcement | 15 |
| Documentation quality | 5 |

**Total: 100 points**
