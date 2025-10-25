# Module 009 Quiz: Monitoring & Observability

## Quiz Information

- **Module:** Monitoring & Observability Basics
- **Total Questions:** 50
- **Time Limit:** 90 minutes
- **Passing Score:** 80% (40/50 correct)
- **Topics Covered:**
  - Observability foundations, SLOs/SLA/error budgets
  - Prometheus architecture, exporters, PromQL, alerting
  - Grafana dashboards, templating, provisioning, alerting
  - Logging pipelines (Loki/Elasticsearch), structured logging, correlation
  - Incident response, ML-specific monitoring (drift, fairness, GPU usage)

## Instructions

1. Answer all questions; only one answer is correct unless explicitly stated.
2. Some scenario questions require selecting the best operational choice.
3. Explanations follow each answer to reinforce core concepts.
4. The answer key for instructors resides in the solutions repository (`ai-infra-junior-engineer-solutions`).

---

### 1. Which statement best differentiates monitoring from observability?
A) Monitoring focuses on logs; observability focuses on metrics.  
B) Monitoring answers whether the system is healthy; observability helps explain *why* it behaves a certain way.  
C) Monitoring is reactive; observability is proactive; both use the same data.  
D) Monitoring is only for infrastructure; observability is only for applications.

**Correct Answer:** B  
**Explanation:** Monitoring checks predefined indicators, whereas observability enables understanding of internal state through signals like metrics, logs, and traces.

---

### 2. What is an error budget if the SLO is 99.5% availability over 30 days?
A) 0.5% downtime allowed (~3.6 hours)  
B) 0.5% uptime allowed (~3.6 hours)  
C) 99.5% uptime allowed (~28.5 days)  
D) 0.05% downtime allowed (~22 minutes)

**Correct Answer:** A  
**Explanation:** Error budget is the complement of the SLO. For 99.5%, 0.5% downtime ≈ 3.6 hours per 30-day window.

---

### 3. Which Prometheus component is responsible for storing metrics and evaluating rules?
A) Alertmanager  
B) Pushgateway  
C) Prometheus server  
D) Exporter

**Correct Answer:** C  
**Explanation:** Prometheus server scrapes targets, stores time series, and evaluates recording/alerting rules before forwarding alerts to Alertmanager.

---

### 4. When should the Prometheus Pushgateway be used?
A) For long-running services behind firewalls  
B) For short-lived batch jobs that cannot be scraped directly  
C) For exporting traces to Jaeger  
D) For scaling Prometheus horizontally

**Correct Answer:** B  
**Explanation:** Pushgateway buffers metrics from ephemeral jobs; it is not intended for long-running services or scaling.

---

### 5. Which PromQL function returns the per-second rate of a monotonically increasing counter over a range?
A) `increase()`  
B) `rate()`  
C) `avg_over_time()`  
D) `histogram_quantile()`

**Correct Answer:** B  
**Explanation:** `rate()` computes the per-second average rate for counters over the specified range vector; `increase()` returns the total increase, not per-second rate.

---

### 6. What is the primary risk of high-cardinality metrics in Prometheus?
A) Alerts become too sensitive  
B) Dashboards cannot display them  
C) TSDB memory usage and query performance degrade sharply  
D) Counter resets become impossible to detect

**Correct Answer:** C  
**Explanation:** Each unique label set increases series count; high cardinality inflates memory, storage, and query costs.

---

### 7. In Grafana, which feature allows the same dashboard to filter by environment, cluster, or team without duplicating panels?
A) Transformations  
B) Canvas panels  
C) Templating variables  
D) Dashboard permissions

**Correct Answer:** C  
**Explanation:** Variables (templating) enable parameterized queries so dashboards adapt to different contexts.

---

### 8. What is the benefit of provisioning Grafana dashboards as code?
A) It allows real-time editing without restart  
B) It enables Git-based version control and consistent deployment across environments  
C) It automatically generates alert rules  
D) It converts PromQL to SQL

**Correct Answer:** B  
**Explanation:** Provisioning ensures dashboards are reproducible, reviewed via Git, and deployed via CI/CD or GitOps workflows.

---

### 9. In a Loki pipeline, which stage parses JSON fields so they can be used as labels or filters?
A) `docker {}`  
B) `json {}`  
C) `match {}`  
D) `drop {}`  

**Correct Answer:** B  
**Explanation:** The `json` stage extracts fields from structured logs, enabling filtering by keys like `level` or `trace_id`.

---

### 10. Which metric best captures SLO compliance for inference latency?
A) `avg_over_time(inference_latency_seconds[5m])`  
B) `histogram_quantile(0.99, sum(rate(inference_latency_seconds_bucket[5m])) by (le))`  
C) `max(inference_latency_seconds)`  
D) `sum(inference_latency_seconds_count)`

**Correct Answer:** B  
**Explanation:** Using histogram buckets with `histogram_quantile` computes latency percentiles (e.g., P99) that directly map to latency SLOs.

---

### 11. What is the purpose of multi-window, multi-burn-rate alerting?
A) To verify Kubernetes autoscaling before generating an alert  
B) To combine fast and slow detection windows so alerts trigger only when sustained SLO violations occur  
C) To alert simultaneously on latency and error rate  
D) To reduce the number of Alertmanager receivers

**Correct Answer:** B  
**Explanation:** Using different windows balances responsiveness with noise reduction—fast window catches severe spikes, long window confirms persistence.

---

### 12. Which Grafana panel type is best for visualizing latency distribution across GPU IDs?
A) Stat panel  
B) Gauge panel  
C) Heatmap  
D) Bar gauge

**Correct Answer:** C  
**Explanation:** Heatmaps effectively show changes across two dimensions (e.g., GPU ID vs time) with intensity representing utilization or latency.

---

### 13. What should you do before deleting a column via database migration that dashboards rely on?
A) Drop the column immediately and fix dashboards later  
B) Scale Prometheus to avoid downtime  
C) Audit dashboard queries, update or provide fallback views, and notify stakeholders  
D) Convert the column to JSONB

**Correct Answer:** C  
**Explanation:** Observability artifacts often depend on schema; audit and stage changes to prevent broken dashboards/alerts.

---

### 14. Which tool enriches FastAPI logs with trace IDs when using OpenTelemetry?
A) `structlog` with manual span context extraction  
B) Promtail pipeline stages  
C) Grafana Tempo  
D) Prometheus relabeling

**Correct Answer:** A  
**Explanation:** Trace context must be captured in the service; e.g., `structlog` can pull IDs via `get_current_span()` and add them to log records.

---

### 15. What is a key advantage of structured JSON logging over plain text?
A) It reduces disk usage  
B) It increases log verbosity  
C) It enables reliable parsing, filtering, and correlation in log analysis tools  
D) It eliminates the need for log aggregation

**Correct Answer:** C  
**Explanation:** Structured logs allow downstream systems to parse fields consistently, enabling filtering and correlation across logs, metrics, and traces.

---

### 16. Which Prometheus query detects when a target stops exposing metrics entirely?
A) `up == 1`  
B) `increase(up[5m])`  
C) `absent(up{job="inference-gateway"})`  
D) `rate(up[5m]) > 0`

**Correct Answer:** C  
**Explanation:** `absent()` returns a vector when no series match; useful for alerting on missing scrapes.

---

### 17. What is the primary role of Alertmanager in the Prometheus ecosystem?
A) Running PromQL queries  
B) Storing time-series data  
C) Deduplicating, silencing, and routing alerts to notifications  
D) Rendering Grafana dashboards

**Correct Answer:** C  
**Explanation:** Alertmanager manages alert delivery (Slack, PagerDuty, email) and handles grouping/silencing.

---

### 18. During an incident, which dashboard panels should appear at the top of an on-call dashboard?
A) Experiment results and feature flags  
B) SLO compliance, error rate, request volume, and high-level resource saturation  
C) Cost analytics and marketing KPIs  
D) Historical release notes

**Correct Answer:** B  
**Explanation:** On-call dashboards must surface actionable SLI/SLO metrics and resource health immediately for rapid triage.

---

### 19. Which description best matches a burn-rate alert?
A) Alerts when CPU usage >90% for 5 minutes  
B) Alerts when the ratio of errors to budgeted errors exceeds a threshold over a window  
C) Alerts when Prometheus cannot reach Alertmanager  
D) Alerts when Grafana dashboards are edited

**Correct Answer:** B  
**Explanation:** Burn rate compares actual error budget consumption versus allowable rate, enabling SLO enforcement.

---

### 20. Why should logs avoid high-cardinality labels like `user_id`?
A) They cause dashboards to be unreadable  
B) They make alerting impossible  
C) They introduce privacy/compliance risks and create storage/query explosions  
D) They prevent tracing integration

**Correct Answer:** C  
**Explanation:** High-cardinality fields in logs balloon storage and can expose sensitive data; prefer hashed or aggregated identifiers.

---

### 21. Which metric indicates GPU overheating risk for inference workloads?
A) `ai_infra_inference_requests_total`  
B) `node_disk_io_time_seconds_total`  
C) `DCGM_FI_DEV_GPU_TEMP`  
D) `container_memory_rss`

**Correct Answer:** C  
**Explanation:** DCGM exporter exposes GPU metrics; temperature enables proactive throttling or scaling decisions.

---

### 22. What is the best practice for storing Grafana alert rule definitions?
A) Manual entry only  
B) Embedded in Prometheus configuration  
C) Managed via code or API exports stored in Git, aligned with dashboards  
D) Stored in Excel spreadsheets

**Correct Answer:** C  
**Explanation:** Treat alert rules as code—versioned, reviewed, and deployed alongside dashboards ensures consistency and auditability.

---

### 23. Which LogQL query counts error-level logs for the inference service in the past 10 minutes?
A) `{service="inference-gateway"} |= "error"`  
B) `count_over_time({service="inference-gateway", level="error"}[10m])`  
C) `sum(rate({service="inference-gateway"}[10m]))`  
D) `increase({level="error"}[10m])`

**Correct Answer:** B  
**Explanation:** `count_over_time` returns occurrences within the range; combine with `sum` if grouping is needed.

---

### 24. Which step best prepares an on-call engineer before a major release?
A) Disable all alerts to reduce noise  
B) Review runbooks, confirm dashboards/alerts reference the upcoming release, and schedule maintenance windows  
C) Scale down Prometheus to reduce costs  
D) Only monitor models, ignore infrastructure

**Correct Answer:** B  
**Explanation:** Pre-release readiness includes aligning runbooks, verifying observability assets, and planning silences if necessary.

---

### 25. In ML observability, what metric detects covariate drift?
A) Error budget burn rate  
B) Population Stability Index (PSI) comparing feature distributions  
C) Request latency  
D) CPU saturation

**Correct Answer:** B  
**Explanation:** PSI and similar measures track distribution shifts in input features, signaling covariate drift.

---

### 26. Which approach ensures log data remains compliant with privacy regulations?
A) Keep all raw logs forever  
B) Delete logs daily regardless of policy  
C) Apply redaction/masking at ingestion, define retention per log class, enforce access controls and deletion workflows  
D) Store logs in public object storage for transparency

**Correct Answer:** C  
**Explanation:** Compliance demands intentional retention, redaction, and access management; policies must be enforced programmatically.

---

### 27. Why is it important to pair alert annotations with runbook links?
A) They automatically resolve the alert  
B) They provide immediate context and next steps, reducing Mean Time to Mitigate  
C) They change alert severity automatically  
D) They disable duplicate alerts

**Correct Answer:** B  
**Explanation:** Annotations with runbook links enable responders to act quickly with relevant instructions.

---

### 28. What is the most effective way to validate observability changes in CI/CD?
A) Deploy directly to production; roll back if issues arise  
B) Run promtool/linting checks, deploy to staging, execute smoke tests, and monitor for regressions before production rollout  
C) Manually check dashboards weekly  
D) Disable CI checks for speed

**Correct Answer:** B  
**Explanation:** Treat observability assets like code—lint/test, stage, and observe before production to prevent incidents.

---

### 29. Which KPI best reflects the health of an on-call rotation?
A) Number of dashboards created  
B) Mean Time To Acknowledge (MTTA) and alert volume per shift  
C) Amount of log storage used  
D) Number of Prometheus rules

**Correct Answer:** B  
**Explanation:** MTTA and alert load indicate responder fatigue and effectiveness, guiding adjustments to alerting and staffing.

---

### 30. During a post-incident review, what should be the focus?
A) Assigning blame to individuals  
B) Confirming that downtime penalties are charged  
C) Identifying systemic improvements, documenting timeline, root causes, and action items with owners  
D) Reducing logging to prevent future incidents

**Correct Answer:** C  
**Explanation:** Blameless postmortems emphasize learning and systemic fixes, producing actionable tasks to prevent recurrence.

---

### 31. What is the purpose of multi-window burn rate alerts in SLO monitoring?
A) To reduce alert noise by requiring multiple consecutive breaches
B) To detect both fast (short window) and slow (long window) error budget consumption
C) To send alerts to multiple on-call engineers
D) To automatically scale infrastructure based on SLO violations

**Correct Answer:** B
**Explanation:** Multi-window alerts (e.g., 5m/1h windows) catch rapid SLO violations (short window) and gradual degradation (long window), providing comprehensive coverage.

---

### 32. Given a 99.9% availability SLO, what burn rate multiplier indicates critical error budget exhaustion in <6 hours?
A) 1x
B) 6x
C) 14.4x
D) 100x

**Correct Answer:** C
**Explanation:** A burn rate of 14.4x means you're consuming error budget 14.4 times faster than acceptable, exhausting a 30-day budget in ~50 hours (< 6 hours at sustained rate).

---

### 33. Which Alertmanager feature prevents duplicate notifications when multiple related alerts fire?
A) Grouping
B) Inhibition rules
C) Silences
D) Time intervals

**Correct Answer:** B
**Explanation:** Inhibition rules suppress alerts based on other active alerts (e.g., suppress node alerts if cluster is down).

---

### 34. What is the recommended structure for a production runbook?
A) Just list the alert name and contact
B) Impact, symptoms, triage steps (<5 min), investigation queries, mitigation procedures, escalation path, post-incident tasks
C) Only include Prometheus queries
D) Defer all details to verbal communication

**Correct Answer:** B
**Explanation:** Comprehensive runbooks enable rapid response by providing complete troubleshooting workflows and escalation procedures.

---

### 35. During an incident, what metric measures time from issue occurrence to detection?
A) MTTR (Mean Time To Repair)
B) MTTD (Mean Time To Detect)
C) MTTA (Mean Time To Acknowledge)
D) MTBF (Mean Time Between Failures)

**Correct Answer:** B
**Explanation:** MTTD is the time between when an issue starts and when monitoring/alerting detects it.

---

### 36. Which PromQL query calculates the P95 latency from histogram buckets?
A) `rate(http_request_duration_seconds_sum[5m])`
B) `histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))`
C) `avg(http_request_duration_seconds)`
D) `max(http_request_duration_seconds)`

**Correct Answer:** B
**Explanation:** `histogram_quantile()` computes quantiles from histogram buckets; 0.95 = P95, rate() provides per-second rates.

---

### 37. What is a Population Stability Index (PSI) threshold indicating significant feature drift?
A) PSI < 0.1
B) PSI 0.1-0.2
C) PSI > 0.2
D) PSI = 1.0

**Correct Answer:** C
**Explanation:** PSI > 0.2 indicates significant distribution shift; PSI > 0.25 typically triggers model retraining.

---

### 38. In a blameless postmortem, what should be the primary focus?
A) Identifying the engineer who caused the issue
B) Documenting timeline, root cause analysis (systemic), and preventive action items
C) Calculating financial penalties
D) Reducing monitoring to prevent future alerts

**Correct Answer:** B
**Explanation:** Blameless postmortems focus on systemic improvements, not individual blame, to foster learning and prevent recurrence.

---

### 39. Which log redaction technique is most effective for PII compliance?
A) Delete all logs
B) Apply regex patterns at ingestion to mask/redact sensitive data (SSN, credit cards, emails)
C) Store logs in plain text for transparency
D) Only log errors, not info-level logs

**Correct Answer:** B
**Explanation:** Automated redaction at ingestion (using Promtail pipeline stages or similar) prevents PII from ever reaching storage.

---

### 40. What is the recommended approach for incident simulation and runbook practice?
A) Wait for real incidents to practice
B) Create automated simulation scripts that inject faults, trigger alerts, and generate incident timelines
C) Only test in production during business hours
D) Avoid testing to prevent false alarms

**Correct Answer:** B
**Explanation:** Regular incident simulations (chaos engineering, game days) validate runbooks and build muscle memory without impacting users.

---

### 41. When should you escalate an incident to the next level?
A) Immediately for all incidents
B) After 30 minutes if unresolved, impact is increasing, or root cause unclear
C) Never escalate to avoid looking incompetent
D) Only during business hours

**Correct Answer:** B
**Explanation:** Escalation criteria should be time-based, impact-based, or complexity-based to ensure appropriate expertise is engaged.

---

### 42. Which Grafana feature allows dashboard variables to be populated from Prometheus label values?
A) Static variables
B) Query variables with label_values()
C) Constant variables
D) Text box variables

**Correct Answer:** B
**Explanation:** Query variables using `label_values(metric, label)` dynamically populate dropdown filters based on Prometheus data.

---

### 43. What is the benefit of correlation IDs in distributed tracing?
A) They reduce log storage costs
B) They enable end-to-end request tracking across multiple services and link traces to logs
C) They automatically fix performance issues
D) They disable unnecessary metrics

**Correct Answer:** B
**Explanation:** Correlation IDs (trace IDs) link logs and traces for a single request across microservices, enabling comprehensive debugging.

---

### 44. Which metric best indicates GPU saturation in an inference service?
A) CPU usage
B) GPU utilization at 95-100% with increasing queue depth
C) Network bandwidth
D) Disk I/O

**Correct Answer:** B
**Explanation:** High GPU utilization combined with growing queue depth indicates saturation; additional GPU capacity needed.

---

### 45. What is the correct order of actions when responding to a critical SLO burn rate alert?
A) Rollback → Investigate → Notify stakeholders → Document
B) Verify alert → Assess scope → Investigate root cause → Mitigate → Document → Post-incident review
C) Disable alerts → Fix issue later → Re-enable alerts
D) Wait to see if it resolves itself

**Correct Answer:** B
**Explanation:** Structured incident response follows: verify (avoid false positives), assess (scope/impact), investigate, mitigate, document, and learn.

---

### 46. Which Log QL query detects log ingestion outages?
A) `{job="logs"} |= "error"`
B) `absent_over_time({job="docker-logs"}[10m])`
C) `rate({job="logs"}[5m])`
D) `count({job="logs"})`

**Correct Answer:** B
**Explanation:** `absent_over_time()` returns 1 when no logs exist in the time range, indicating ingestion failure.

---

### 47. What is the purpose of Alertmanager's `group_wait` parameter?
A) How long to wait before sending the first notification for a group of alerts
B) How long to wait between re-sending notifications
C) How long to keep alerts in memory
D) How long to wait for user acknowledgment

**Correct Answer:** A
**Explanation:** `group_wait` buffers alerts briefly to group related alerts together in a single notification, reducing noise.

---

### 48. When monitoring model fairness, what metric detects demographic parity violations?
A) Latency P95
B) Absolute difference in prediction rates between demographic groups exceeding threshold (e.g., > 0.1)
C) Error budget consumption
D) GPU temperature

**Correct Answer:** B
**Explanation:** Demographic parity compares positive prediction rates across groups; significant differences (> 10%) indicate potential bias.

---

### 49. Which practice reduces alert fatigue in on-call rotations?
A) Send all alerts to pagers for maximum awareness
B) Implement SLO-based alerting, tune thresholds quarterly, automate common mitigations, and track alerts/week/person
C) Disable all non-critical alerts permanently
D) Only alert during business hours

**Correct Answer:** B
**Explanation:** Alert fatigue is reduced by focusing on user impact (SLOs), regularly tuning thresholds, automation, and monitoring workload metrics.

---

### 50. What is the recommended retention period for incident timelines and postmortems?
A) Delete after resolution
B) Keep for 30 days
C) Archive indefinitely for organizational learning and compliance
D) Only keep if incident was critical

**Correct Answer:** C
**Explanation:** Incident documentation provides historical context for future issues, supports compliance, and enables long-term reliability improvements.

---

## Quiz Complete!

**Reminder for Instructors:** The detailed answer key and solution walkthroughs reside in the corresponding solutions repository (`ai-infra-junior-engineer-solutions/quizzes/module-009/quiz-01-monitoring-observability-answer-key.md`). Update both learning and solutions repos in lockstep when modifying quiz content.
