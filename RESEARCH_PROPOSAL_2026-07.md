# Research Proposal — Junior AI Infrastructure Engineer — 2026-07

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

Market unchanged this cycle. A ~30-day refresh sweep (2026-06-01 → 2026-07-01) added 10 postings on top of the June baseline (32) for a rolling window of 42 postings observed in the last 90 days (2026-04-01 → 2026-07-01). The stable-core level-10 stack (Python, Linux, Git, Docker, Kubernetes, one cloud, CI/CD, Prometheus/Grafana, Flask/FastAPI, PostgreSQL, Terraform basics, MLflow, Airflow/Prefect) still dominates required-skills lists in >60% of postings. The four items the June packet flagged as accelerating-but-preferred at the junior tier (LLM serving via vLLM/Triton/TRT-LLM, vector DBs + RAG, GPU/CUDA/NCCL deep work, GitOps via Argo CD/Flux) remain preferred-not-required at the junior tier in the July sample: LLM serving 6/42 (0.14), vector DB + RAG 7/42 (0.17), GPU/CUDA 8/42 (0.19), GitOps 7/42 (0.17) — all well below the 0.30 addition threshold. No requirement has become obsolete. Per continuity bias and the ownership rule, the correct output is empty additions/updates/removals — every higher-level item is already linked to its owner role (level 20 / 30 / 35) and every level-10 requirement is already covered by an existing module or project.

## How to apply (after approval)

```sh
aicg org plan-delta-apply \
  --role junior-engineer \
  --delta .aicg/curriculum-plan-delta-v2.json
```

The CLI re-validates the delta against the current baseline. If the validator's flags or rejects have changed since this proposal was written (e.g., new postings landed in another role), the apply will surface them before writing.
