# Runbook: ModelDriftDetected

**Alert:** `ModelDriftDetected`
**Severity:** warning
**Pages:** no (Slack `#alerts-warnings`, also notifies the model owner)

## What it means

Feature distribution drift (PSI > 0.2) or output prediction drift has exceeded the configured threshold over a 24-hour window. The model's input or output no longer matches what it was trained on.

## How bad is it?

Drift is not an outage but it predicts degradation. Left unchecked, model accuracy will decline and downstream metrics (conversion, fraud rate, etc.) will follow.

## First checks

1. **Which features are drifting?** The alert label `feature` identifies the worst offender. Look at the drift dashboard for the full ranking.
2. **Is the drift abrupt or gradual?**
   - **Abrupt** → likely upstream data pipeline change (new schema, new vendor).
   - **Gradual** → likely real-world distribution shift (seasonality, market trend).
3. **Is prediction distribution also drifting?** Input drift without output drift is sometimes a false alarm for tree models. Output drift is more actionable.
4. **What's the latest model evaluation?** If we have ground-truth labels arriving, has measured accuracy / AUC moved?

## Likely causes

1. **Upstream schema change.** A producer changed how a field is computed.
2. **New segment / cohort.** Onboarded users / markets / merchants the model didn't see at training time.
3. **Seasonality.** Holidays, end of quarter, marketing campaigns.
4. **Bug in feature pipeline.** A null-handling change makes a column always zero.

## Mitigation

This is **not** an action-now alert. The workflow is:

1. File a ticket assigning the model owner.
2. Confirm whether the drift correlates with a known event (campaign, schema change).
3. If accuracy is measurably degrading, trigger retraining via the `model_retraining` DAG in Project 03.
4. If the feature change is bug-shaped, fix the upstream pipeline rather than retrain over bad data.

## When this requires a postmortem

- Accuracy degradation noticed by an external party before us.
- Drift was caused by a release we shipped (process gap).
