# Lecture 04: Logging, Alerting, and ML-Focused Monitoring Workflows

## Lecture Overview
Logs complete the observability triad by recording contextual events, error details, and audit trails. Combined with alerting pipelines and ML-specific monitoring practices, they enable rapid incident response and continuous assurance of model performance. This lecture covers end-to-end logging architecture (collection, aggregation, storage, query), alerting strategy, incident management, and advanced ML observability patterns, closing the loop for Module 009.

**Estimated Reading Time:** 80–95 minutes
**Hands-on Companion Lab:** Exercise 04 – Logging Pipeline, Exercise 05 – Alerting & Incident Response
**Prerequisite Knowledge:** Lectures 01–03, familiarity with Prometheus/Grafana, basic knowledge of Kubernetes or containerized deployments.

### Learning Objectives

By the end of this lecture, you will:
- Design end-to-end logging pipelines for distributed ML systems
- Implement structured logging with proper context propagation
- Deploy and configure Loki or ELK stack for log aggregation
- Write effective alerting rules based on SLO error budgets
- Integrate log correlation with metrics and distributed traces
- Apply ML-specific monitoring patterns for model performance
- Establish incident management workflows for production ML systems

---

## 1. Logging Fundamentals for AI Infrastructure

### 1.1 Role of Logs
- Capture discrete events (errors, warnings, state changes).
- Provide audit trail for compliance (GDPR, HIPAA).
- Supply context missing from aggregated metrics (stack traces, payload identifiers).
- Drive post-incident analysis (timeline reconstruction, impact assessment).

### 1.2 Structured vs Unstructured Logs
- **Structured Logs:** JSON or key/value format. Easier parsing, filterable by fields, machine-readable.
- **Unstructured Logs:** Free-form text. Harder to query, prone to parsing issues.
- Standardize on structured logs with schema versioning to minimize downstream friction.

### 1.3 Logging Levels & Guidance
| Level | Purpose | AI/ML Examples |
|-------|---------|----------------|
| DEBUG | Detailed diagnosis | Feature values for a development run (not prod) |
| INFO | Normal operation | “Training job started”, “Model version deployed” |
| WARN | Unexpected event, self-recoverable | Retry due to network timeout |
| ERROR | User-visible or unrecoverable | Inference request failed, data validation error |
| FATAL | System cannot continue | Database connectivity loss, corrupted model artifact |

**Guideline:** Avoid logging sensitive data (PII, secret keys); apply masking or hashing. Adopt retention policies fitting compliance (e.g., 30 days for INFO, 180 days for audit logs).

---

## 2. Logging Architecture Patterns

### 2.1 Log Shipping Pipeline
1. **Collection:** Agents (Fluent Bit, Vector, Filebeat) or sidecars read from stdout/files.
2. **Transport:** Ship logs via gRPC/HTTP to aggregation system.
3. **Aggregation/Indexing:** Loki, Elasticsearch/OpenSearch, Splunk.
4. **Storage:** On-premise, object storage, managed services.
5. **Query & Visualization:** Grafana Loki panels, Kibana dashboards, SQL engines.

### 2.2 Kubernetes Logging
- Containers output logs to stdout/stderr.
- Fluent Bit/Fluentd DaemonSet tails logs from `/var/log/containers`.
- Apply filters to enrich logs with metadata (namespace, pod, labels).
- Support multi-tenancy via labels (team, environment).

### 2.3 Loki Stack (PLG: Prometheus + Loki + Grafana)
- Lightweight, cost-efficient for high-volume logs.
- Log streams indexed by labels (limit label cardinality).
- Query language LogQL similar to PromQL.
  - Example: `{app="inference-gateway"} |= "timeout" | json | latency > 300`
- Store compressed chunks in object storage (S3, GCS).
- Central Grafana for visualization, alerting.

### 2.4 Elastic Stack (ELK / OpenSearch)
- Beats/Logstash ingest logs, transform, send to Elasticsearch.
- Kibana for dashboards; integrate with Grafana via Elasticsearch data source.
- Powerful search, but resource intensive (plan capacity carefully).

---

## 3. Log Enrichment & Context Propagation

### 3.1 Common Fields
- `timestamp`, `level`, `message`, `service`, `environment`, `region`.
- Correlation IDs: `trace_id`, `span_id`, `request_id`.
- Model metadata: `model_name`, `model_version`, `experiment_id`.
- User metadata (if required): ensure privacy (hash user IDs).
- Resource info: `pod_name`, `node`, `gpu_id`.

### 3.2 Correlation with Metrics & Traces
- Propagate trace IDs using OpenTelemetry instrumentation; include in logs and metrics labels.
- Example Python snippet:
```python
from opentelemetry.trace import get_current_span

span = get_current_span()
trace_id = span.get_span_context().trace_id
log.info("prediction_failed",
         extra={"trace_id": format(trace_id, '032x'),
                "model_version": model_version,
                "latency_ms": latency})
```
- Grafana exemplars link metrics to traces; logs provide step-by-step context.

### 3.3 Redaction & Compliance
- Mask or remove sensitive fields (PII, secrets) at ingestion time.
- Define data retention per log type (audit logs longer retention).
- Apply access controls to restrict query capabilities for sensitive logs.
- Provide compliance exports (search/erase requests) when required.

---

## 4. Log Querying & Analysis

### 4.1 LogQL Basics (for Loki)
- Exact match: `{app="inference-gateway", level="error"}`
- Filter contains: `|= "timeout"`
- Negation: `!= "healthcheck"`
- Parse JSON: `| json | latency_ms > 200`
- Aggregate: 
  ```logql
  sum(count_over_time({app="inference-gateway", level="error"}[5m]))
  ```
  for error rate trends.

### 4.2 Elasticsearch Query Examples
- Kibana DSL or SQL-like queries:
```json
GET /inference-logs/_search
{
  "query": {
    "bool": {
      "must": [
        { "match": { "service": "feature-store" }},
        { "range": { "@timestamp": { "gte": "now-15m" }}}
      ],
      "filter": [
        { "term": { "level": "ERROR" }}
      ]
    }
  }
}
```
- Aggregations: group by model version, count errors.

### 4.3 Command-Line Tools
- `kubectl logs`, `stern`, `kail` for quick investigations.
- `rg`, `awk`, `jq` for local log parsing.
- Use CLI for triage, pivot to centralized system for long-term analysis.

---

## 5. Alerting Pipeline Design

### 5.1 Alert Lifecycle
1. **Detection:** Metrics or log thresholds trigger alert.
2. **Notification:** Alert routed to on-call (PagerDuty, Slack, email).
3. **Acknowledgement:** On-call acknowledges, triages.
4. **Resolution:** Mitigation applied, service restored.
5. **Analysis:** Post-incident review, root cause documentation.

### 5.2 Alert Quality Criteria
- **SLO-aligned:** Derived from user-impacting SLIs.
- **No duplication:** Single alert per issue; use alert correlation.
- **Actionable:** Clear instructions; no ambiguous alerts.
- **Adaptive:** Support different severity levels (page vs ticket).
- **Tested:** Validate in staging, run synthetic tests.

### 5.3 Alert Types
- **Symptom-based:** Error rate, latency, SLO burn rate (preferred).
- **Resource-based:** CPU/memory/gpu saturation (backup).
- **Event-based:** Deploy failures, cron jobs missed.
- **Log-based:** Detect patterns (e.g., repeated authentication failure).

### 5.4 Alert Routes & Escalation
- Primary on-call rotation → secondary engineering lead → incident commander.
- Use schedules for follow-the-sun coverage.
- Escalation policies ensure unacknowledged alerts escalate after defined interval.

### 5.5 Burn Rate Alerting Recap
- Multi-window, multi-burn approach reduces noise.
- Example: Burn rate >14 for 5m AND >4 for 1h triggers page; ensures persistent issue before alert.

---

## 6. Incident Response for AI Services

### 6.1 Severity Levels
- **SEV0:** Complete outage, major business impact (e.g., inference down globally).
- **SEV1:** Degraded performance (latency >SLO, partial outage).
- **SEV2:** Minor impact, no customer-visible effect yet (forecasted breach).
- **SEV3:** Non-urgent issues, track via ticket.

### 6.2 Incident Roles
- **Incident Commander (IC):** Coordinates response, communication.
- **Communications Lead:** Keeps stakeholders updated.
- **Subject Matter Experts:** Model owners, infra engineers.
- **Scribe:** Records timeline, key decisions (for postmortem).

### 6.3 ML-Specific Incident Considerations
- Validate data pipelines (schema drift causing bad predictions).
- Check model versions; rollback to previous model if needed.
- Examine feature store health; fallback to cached features or default values.
- Evaluate cost overruns due to runaway training jobs.

### 6.4 Post-Incident Review
- Identify contributing factors, detection gaps, process issues.
- Highlight ML-specific lessons (e.g., need for automated data validation).
- Update runbooks, dashboards, alerts accordingly.

---

## 7. ML Observability Deep Dive

### 7.1 Model Performance Monitoring
- Track live metrics: accuracy, precision, recall when labels available quickly.
- For delayed labels, use proxy metrics (click-through, conversion).
- Slice metrics by geography, user cohort, device type.
- Visualize via Grafana or specialized ML observability tools.

### 7.2 Data Quality Monitoring
- Metrics: missing values, distribution shifts, correlation changes.
- Tools: Evidently AI, Great Expectations, TFDV.
- Integrate with Prometheus via custom exporters or push metrics to monitoring stack.
- Alert on persistent deviations beyond thresholds.

### 7.3 Drift Detection
- **Covariate drift:** Feature distribution changes (monitor PSI, JS divergence).
- **Concept drift:** Relationship between features and labels changes (monitor accuracy drop, residuals, fairness).
- **Label drift:** Output distribution changes.
- For real-time detection, run mini-batch statistical tests.
- Provide dashboards comparing training vs serving distributions.

### 7.4 ML-specific Alerts
- Loss of fresh labels (no ground truth for >24 hours).
- Drift metrics exceeding threshold.
- Model fairness metrics below target (e.g., recall for cohort <90% of overall).
- Feature pipeline backlog impacting training schedule.

### 7.5 Champion-Challenger Monitoring
- Compare baseline vs canary model metrics.
- Use dashboards to show splits: request routing, latency differences, accuracy.
- Implement automatic rollback when canary violates thresholds.

---

## 8. Logging & Monitoring in Hybrid/Edge Deployments

### 8.1 Edge Considerations
- Limited connectivity: buffer logs locally, forward when connected.
- Prioritize critical metrics and logs (model health, hardware status).
- Use lightweight agents (e.g., Fluent Bit, Vector).

### 8.2 Hybrid Cloud
- Ensure consistent schema and labeling across environments.
- Use VPN/TLS tunneling for secure log transfer.
- Centralize retention policies to satisfy regulatory requirements.

### 8.3 Data Residency & Privacy
- Store logs in region to comply with local regulations.
- Mask PII at source; consider differential privacy for user data.

---

## 9. Automation & Tooling

### 9.1 Infrastructure-as-Code
- Manage logging and alerting resources via Terraform/Helm.
- Example: `helm install loki grafana/loki-stack`.
- Use GitOps (Argo CD, Flux) for declarative deployments.

### 9.2 Continuous Integration Checks
- Lint alert rules with `promtool check rules`.
- Validate Loki pipeline configuration via unit tests (Vector/Fluent Bit test harness).
- Run staging environment smoke tests to verify instrumentation after each deploy.

### 9.3 Observability CI/CD Pipeline
1. Developer updates instrumentation or dashboards.
2. CI runs tests (promtool, linting, unit tests).
3. Observability changes reviewed, merged to main branch.
4. CD deploys to staging; smoke tests; manual QA.
5. Promote to production, monitor for regressions.

---

## 10. Governance, Security, and Compliance

### 10.1 Role-Based Access Control
- Limit who can query sensitive logs, manage alerts, modify dashboards.
- Use SSO/identity providers with group mappings.
- Implement least privilege (view-only vs edit).

### 10.2 Audit Logging
- Track changes to alert rules, dashboards, retention policies.
- Maintain tamper-proof logs stored separately (write-once storage).
- Ensure incident notes are recorded for compliance.

### 10.3 Retention & Deletion Policies
- Align with legal requirements; define retention for each log class.
- Automate deletion using lifecycle rules (S3 lifecycle policies, Loki retention).
- Document processes for “right to be forgotten” requests.

### 10.4 Secure Transport & Storage
- Encrypt logs in transit (TLS) and at rest (KMS, key management).
- Segment networks; restrict egress from log aggregation clusters.
- Harden access with firewall rules, security groups.

---

## 11. Practical Checklists

### 11.1 Logging Readiness
- [ ] Standardized structured logging libraries across services.
- [ ] Log ingestion pipeline deployed (agents, aggregator, storage).
- [ ] Correlation IDs included in logs and traces.
- [ ] Log retention policies documented and enforced.
- [ ] Redaction/masking of sensitive fields implemented.
- [ ] Query dashboards built for common scenarios (error logs, audit trail).

### 11.2 Alerting Readiness
- [ ] SLO-based alerts defined and tested in staging.
- [ ] Alert routes and escalation policies configured.
- [ ] On-call schedule documented and accessible.
- [ ] Runbooks linked in alert annotations.
- [ ] Alert noise reviewed monthly (post-incident retro).
- [ ] Synthetic monitoring (blackbox) alerts in place for critical endpoints.

### 11.3 ML Monitoring Readiness
- [ ] Model performance metrics tracked and visualized.
- [ ] Data drift detection integrated with monitoring stack.
- [ ] Fairness and ethics metrics defined for critical models.
- [ ] Champion-challenger dashboards available.
- [ ] Incident process includes ML-specific checklists.

---

## 12. Knowledge Check
1. Compare Loki and Elasticsearch for log aggregation in terms of cost, scalability, and feature set.
2. Outline steps to implement end-to-end tracing and ensure logs carry trace IDs.
3. Design an alert for model accuracy dropping below threshold due to delayed labels—what signals and thresholds would you use?
4. Explain how you would detect and mitigate concept drift in production.
5. Describe the governance measures required to keep logs compliant with data privacy regulations.

---

## 13. Additional Resources
- CNCF Observability Landscape (https://landscape.cncf.io/)
- Grafana Loki documentation & best practices.
- OpenTelemetry Collector configuration guides.
- “Machine Learning Observability: Best Practices” (Fiddler, Arize, WhyLabs whitepapers).
- Google SRE Workbook – Incident Response chapters.
- MITRE ATLAS for adversarial ML threats (relevant for security logging).

---

## 14. Summary
- Logs provide granular context that complements metrics and traces, essential for diagnosing AI infrastructure issues.
- Structured logging, correlation IDs, and centralized aggregation enable efficient querying.
- Alerting must align with SLOs and incorporate ML-specific considerations (drift, fairness).
- Incident response for AI systems includes additional checks for data pipelines and model performance.
- Governance, security, and compliance are integral to sustainable monitoring and logging practices.

With all four lectures complete, Module 009 now provides a comprehensive foundation for monitoring and observability in AI infrastructure. Proceed to the exercises to cement these concepts hands-on, and finalize the module by assembling the knowledge check quiz.
