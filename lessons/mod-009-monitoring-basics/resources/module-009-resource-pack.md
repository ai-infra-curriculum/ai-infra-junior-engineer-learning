# Module 009 Resource Pack (Monitoring & Logging)

This checklist captures the supplementary assets that accompany Module 009. Attach the referenced files to this directory (or link to their locations) as they are produced during implementation. Use the status column to track completion and highlight open TODOs.

| Asset | Description | Suggested Location | Status / Notes |
|-------|-------------|--------------------|----------------|
| `dashboards/inference-gateway.json` | Grafana service-level dashboard for the inference gateway (Exercise 03) | `/home/claude/ai-infrastructure-project/repositories/learning/ai-infra-junior-engineer-learning/assets/dashboards/` | TODO – export when dashboard is implemented during repo build phase |
| `dashboards/platform-health.json` | Grafana platform health dashboard (Exercise 03) | same as above | TODO – pending dashboard implementation |
| `dashboards/executive-overview.json` | Executive KPI dashboard | same as above | TODO – to be created alongside stakeholder dashboards |
| `alerting/inference-rules.json` | Grafana alert definitions or Prometheus alert rules bundle | `assets/alerting/` | TODO – generate from Grafana/Prometheus configs |
| `prometheus/docker-compose.monitoring.yml` | Reference stack configuration from Exercise 02 | `assets/prometheus/` | TODO – capture canonical compose file after testing |
| `prometheus/rules/*.yml` | Recording + alerting rules used in exercises | `assets/prometheus/rules/` | TODO – copy from lab outputs once authored |
| `promtail/promtail-config.yaml` | Log shipping configuration (Exercise 04) | `assets/logging/` | TODO – add after log pipeline is validated |
| `loki/local-config.yaml` | Loki deployment config | `assets/logging/` | TODO – add after log pipeline is validated |
| `docs/prometheus-architecture.png` | Architecture diagram (Exercise 02) | `docs/diagrams/` | TODO – diagram to be produced (use draw.io template) |
| `docs/logging-architecture.png` | Logging pipeline diagram (Exercise 04) | `docs/diagrams/` | TODO – diagram to be produced |
| `docs/alerting-policy.md` | Alert routing matrix (Exercise 05) | `docs/` | TODO – author during alert configuration |
| `runbooks/inference-latency.md` | Incident runbook (Exercise 05) | `runbooks/` | TODO – populate per runbook template |
| `incidents/INC-001-latency.md` | Sample incident timeline | `incidents/` | TODO – create during incident simulation |
| `validations/module-009-checklist.md` | QA checklist once content is validated | `validations/` | TODO – to be produced by QA/content-validation agent |

## Usage Notes
- Treat this file as the authoritative index when populating assets. Update the status column (`TODO`, `IN PROGRESS`, `COMPLETE`) so QA can quickly audit progress.
- When assets live outside this repository, add hyperlinks or relative paths so future contributors can locate them.
- Before concluding Phase 8 for Module 009, ensure all TODOs above are either satisfied or annotated with rationale/deferment notes for the content-validation agent.
