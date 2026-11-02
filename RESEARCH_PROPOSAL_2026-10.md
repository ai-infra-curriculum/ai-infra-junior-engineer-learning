# Research Proposal — Junior AI Infrastructure Engineer — 2026-10

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

Market unchanged this cycle — continuity preserved. A ~60-day refresh sweep (2026-07-01 → 2026-10-01) added 6 fresh postings (p53-p58: Torc Robotics ML Eng I MLOps Framework, Quora New Grad ML Platform SWE, BlackRock AI/ML Engineer Associate, Vector Institute Associate SW Dev ML, AvePoint Junior AI Engineer, Scale AI New Grad SWE) for a rolling cumulative sample of 58. The stable-core level-10 stack (Python, Linux, Git, Docker, Kubernetes, one cloud, CI/CD, Prometheus/Grafana, Flask/FastAPI, PostgreSQL, Terraform basics, MLflow, Airflow/Prefect) still dominates required-skills lists in >60% of postings. Watched-signal update: LLM serving 11/58 (0.190, essentially flat vs August's 0.192), vector DB + RAG 14/58 (0.241, +0.049 — the largest single-cycle move since tracking began), GPU/CUDA 12/58 (0.207, slight drop vs 0.212), GitOps 9/58 (0.155, slight drop vs 0.173). All four signals remain below the 0.30 addition threshold on cumulative tally. Vector/RAG is the only signal with meaningful upward acceleration this cycle: BlackRock is the first tier-1 finance employer in the sample to treat LangChain+LlamaIndex+RAG as *required* (not preferred) at the 1-3 YoE Associate band; Scale AI's new-grad SWE posting uses 'build a customer service RAG application' as the day-one project description; Vector Institute and AvePoint add LangChain/vector-DB signal in preferred. In the fresh-only sample (n=6) vector/RAG is 4/6 (0.67). If the November cycle reproduces anywhere near that in-sample rate, cumulative will cross 0.30 and req-018-vector-db-rag should be promoted from level-30 'linked' coverage to a level-10 owned exercise (likely extending project-05-production-ml-capstone with the smallest usable RAG slice: embeddings → pgvector → retrieval). Per continuity bias and the ownership rule, the correct output this cycle is empty additions/updates/removals — no signal has crossed threshold, and both the LLM-serving and GPU signals (which the August packet flagged as watch items) failed to accelerate this cycle, invalidating the earlier concern that they were on track to cross. The one promotion candidate is already fully covered at level 30 (ai-infra-ml-platform-learning).

## How to apply (after approval)

```sh
aicg org plan-delta-apply \
  --role junior-engineer \
  --delta .aicg/curriculum-plan-delta-v2.json
```

The CLI re-validates the delta against the current baseline. If the validator's flags or rejects have changed since this proposal was written (e.g., new postings landed in another role), the apply will surface them before writing.
