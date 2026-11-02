# Research Proposal — Junior AI Infrastructure Engineer — 2026-08

Format: **curriculum-plan v2** (per-role manifest at `manifest/curriculum_plan.junior-engineer.manifest.json` in the content-generator repo).

## Summary

- Baseline requirement count: **15**
- Additions: **0**
- Updates: **0**
- Removals: **0**

## Continuity check

Validator did not flag this delta for explicit approval.

Validator notes:

_(none)_

## Rationale

Market unchanged this cycle. A ~30-day refresh sweep (2026-07-01 → 2026-08-01) added 10 postings on top of the July baseline (42) for a rolling window of 52 postings observed in the last 90 days (2026-05-01 → 2026-08-01). The stable-core level-10 stack (Python, Linux, Git, Docker, Kubernetes, one cloud, CI/CD, Prometheus/Grafana, Flask/FastAPI, PostgreSQL, Terraform basics, MLflow, Airflow/Prefect) still dominates required-skills lists in >60% of postings. The four items the July packet flagged as accelerating-but-preferred at the junior tier all ticked up modestly but remain below the 0.30 addition threshold in the rolling window: LLM serving 10/52 (0.19, +0.05), vector DB + RAG 10/52 (0.19, +0.02), GPU/CUDA/NCCL 11/52 (0.21, +0.02), GitOps 9/52 (0.17, flat). Growth is concentrated at AI-native, inference-first, and GPU-cloud employers (NVIDIA new-grad, Together AI, TensorOps, Loop, NewsBreak); traditional-enterprise and Associate-band listings (Gore Mutual, CyferSoft, AI Singapore, Jobgether-hosted MLOps) still list the same items as preferred-not-required. First entry-level postings to require RAG (TensorOps, Loop) surfaced this cycle — a signal to watch, not a threshold crossing. Per continuity bias and the ownership rule, the correct output is empty additions/updates/removals — every higher-level item is already linked to its owner role (level 20 / 30 / 35) and every level-10 requirement is already covered by an existing module or project. Next cycle (2026-09) should re-verify LLM serving and RAG specifically; another +0.05 on either would cross threshold and warrant promotion to level-10 owned modules.

## How to apply (after approval)

```sh
aicg org plan-delta-apply \
  --role junior-engineer \
  --delta .aicg/curriculum-plan-delta-v2.json
```

The CLI re-validates the delta against the current baseline. If the validator's flags or rejects have changed since this proposal was written (e.g., new postings landed in another role), the apply will surface them before writing.
