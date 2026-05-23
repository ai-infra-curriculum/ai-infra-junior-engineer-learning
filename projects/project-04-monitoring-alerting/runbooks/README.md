# Runbooks

A runbook is the playbook an on-call engineer follows when an alert fires. The goal is to make an incident at 3am no harder than the same incident at 3pm. Each runbook covers one alert (or one tightly related family) and answers:

1. **What does this alert mean?** Plain-English description of what's wrong.
2. **How bad is it?** Who's affected, what's degraded.
3. **What to check first.** Specific dashboards and queries that confirm the diagnosis.
4. **Likely causes.** Ranked by probability.
5. **Mitigation steps.** Concrete commands and links.
6. **Rollback.** If mitigation makes it worse.
7. **Postmortem trigger.** When this incident requires a written postmortem.

## Conventions

- Each runbook is named after the alertname in `prometheus/alerts.yml`.
- The alert's `runbook_url` annotation should point to the rendered runbook URL.
- Mitigation commands assume kubectl context is already set; show the full command including namespace.
- "Likely causes" should reflect what has actually broken in production history, not theoretical possibilities.

## Index

| Alert | Severity | Runbook |
|---|---|---|
| `HighErrorRate` | critical | [high-error-rate.md](high-error-rate.md) |
| `SlowResponse` | warning | [slow-response.md](slow-response.md) |
| `TargetDown` | critical | [target-down.md](target-down.md) |
| `ModelDriftDetected` | warning | [model-drift.md](model-drift.md) |
| `LogIngestionLag` | warning | [log-ingestion-lag.md](log-ingestion-lag.md) |
