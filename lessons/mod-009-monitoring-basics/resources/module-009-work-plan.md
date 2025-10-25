# Module 009 Work Plan – Monitoring & Observability Basics

## Session Objectives
- Produce four comprehensive lecture notes (~3,000-4,000 words each) covering observability fundamentals, Prometheus metrics, Grafana visualization, and logging/alerting workflows.
- Design 4-5 progressive hands-on exercises that culminate in a functioning monitoring stack for the junior AI infrastructure environment.
- Author a 30-question knowledge check quiz aligned to lecture learning outcomes.
- Prepare supporting docs (dashboards, sample configs, troubleshooting guides) for reuse in future modules and cross-role curricula.

## Deliverable Breakdown

| Deliverable | Description | Notes |
|-------------|-------------|-------|
| `lecture-notes/lecture-01-observability-fundamentals.md` | Conceptual overview, SLO/SLI basics, monitoring maturity, ML-specific concerns | Include case study + checklist |
| `lecture-notes/lecture-02-prometheus-metrics-pipeline.md` | Prometheus architecture, exporters, PromQL deep dive, instrumentation patterns | Provide YAML snippets, query examples |
| `lecture-notes/lecture-03-grafana-dashboards.md` | Dashboard design, panel recipes, alert rules, best practices | Add dashboard JSON references and review workflow |
| `lecture-notes/lecture-04-logging-alerting-ml-monitoring.md` | Logging stack, structured logging, Alertmanager, ML observability (drift, performance) | Cover playbooks + on-call runbook basics |
| Exercises (5) | Labs progressing from metrics ingestion to full-stack observability | Mirror Module 008 structure; 1,500-3,000 words each |
| Quiz | 30 questions, mix of MCQ and scenario-based | Provide answer key in solutions repo |

## Exercise Roadmap
1. **Exercise 01 – Observability Foundations Lab:** Instrument a sample Python API with basic metrics/logs; analyze baseline dashboards.
2. **Exercise 02 – Prometheus Setup & Exporters:** Deploy Prometheus + node_exporter + custom exporter via Docker Compose; craft PromQL queries.
3. **Exercise 03 – Grafana Dashboards:** Build service-level dashboards, apply templating, set SLO panels, and share dashboards.
4. **Exercise 04 – Logging Pipeline:** Configure Loki or ELK stack, implement structured logs, write logQL/Elasticsearch queries.
5. **Exercise 05 – Alerting & Incident Response:** Configure Alertmanager, PagerDuty/slack webhook stubs, write runbook, simulate incident review.

## Dependencies & Reuse
- Reference Module 005 Docker compose templates for rapid stack deployment.
- Reuse Module 007 API service for instrumentation examples.
- Align terminology with QA and validation templates (Phase 6-7 requirements).
- Ensure lab scripts integrate with repo-level Makefile if present.

## Timeline & Estimation
- **Lectures:** 4 sessions (~12-14 hours total).
- **Exercises:** 5 sessions (~15 hours total).
- **Quiz + polish:** 1 session (~3 hours).
- **Buffer:** 2 hours for peer review and documentation cleanup.

## Quality Checks
- Include diagrams or ASCII architecture overviews in each lecture.
- Provide copy-paste friendly code blocks, validated configs, and troubleshooting tips.
- Cross-reference learning objectives from README to guarantee coverage.
- Update `memory/project-state.json` after completing lectures and exercises to keep orchestrator aligned.
