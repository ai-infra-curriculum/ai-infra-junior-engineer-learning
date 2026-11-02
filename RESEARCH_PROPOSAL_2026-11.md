# Research Proposal — Junior AI Infrastructure Engineer — 2026-11

Format: **curriculum-plan v2** (per-role manifest at `manifest/curriculum_plan.junior-engineer.manifest.json` in the content-generator repo).

## Summary

- Baseline requirement count: **15 owned at level 10 (26 tracked total)**
- Additions: **0**
- Updates: **1** (req-018-vector-db-rag — promoted from level-30 linked to level-10 covered via one new mod-004 exercise)
- Removals: **0**

## Continuity check

Validator did not flag this delta for explicit approval. 1 update is well under both the 20% addition cap and the 10% removal cap, and the single update extends existing content (adds one exercise to the existing mod-004-ml-basics module) rather than creating a new module.

Validator notes:

_(none)_

## Rationale

**First promotion in the junior-engineer manifest since tracking began.** A ~30-day refresh sweep (2026-08-01 → 2026-11-01) added 10 fresh postings (p59 Crowe, p60 Klaviyo, p61 iManage, p62 AppZen, p63 ServiceTitan, p64 SambaNova, p65 Visa, p66 NRG Energy, p67 Indium, p68 FNZ) for a rolling cumulative sample of 68. The vector-DB + RAG signal — flagged by the October packet as the primary promotion candidate for this cycle — **crossed the 0.30 addition threshold on the cumulative tally**: 22/68 = 0.324, up from 14/58 = 0.241 in October (+0.083, the second consecutive single-cycle acceleration).

In the fresh November sample (n=10), vector/RAG is required in **6 postings** (Klaviyo AI Engineer I, AppZen AI/ML Engineer, ServiceTitan AI Engineer, Visa SW Engineer LangChain/RAG, Indium Fresher, FNZ Azure+AI Platform Engineer) and preferred in **2** (iManage Applied AI Engineer, NRG Agentic AI Developer) — total 8/10 fresh postings (0.80) mention it, closely reproducing the October fresh-sample tilt of 4/6 (0.67). The signal has clearly spread beyond the AI-native / inference-first cluster: tier-1 financial infrastructure (Visa in Austin), B2B SaaS and legal tech (Klaviyo in Boston, iManage in Chicago, ServiceTitan US-remote), US energy utilities (NRG at only $65-75K), Indian services firms (AppZen in Pune, Indium at fresher 0-YoE), and Indian captive AI platform (FNZ in Gurugram).

Per the ownership rule (lowest-level role where genuinely required), req-018-vector-db-rag is promoted from level-30 'linked' (ai-infra-ml-platform-learning) to level-10 'covered' via **one new exercise under the existing mod-004-ml-basics module**: `exercise-06-embeddings-and-vector-search`. This extends existing content (preferred per the continuity bias) rather than creating a new module. Scope is deliberately minimal — the awareness layer only: embeddings concepts (dense vs sparse), similarity metrics (cosine / dot / euclidean), a minimal pgvector hands-on reusing mod-008 PostgreSQL coverage, and a toy end-to-end retrieval pattern (query embedding → top-k docs → prompt stuffing). Deeper vector-DB internals (ANN index tuning, sharding, replication, hybrid search, re-ranking strategies) remain owned at level 30 ai-infra-ml-platform-learning.

The other three watched signals stayed flat or regressed with denominator growth: LLM serving 12/68 (0.176, down from 0.190 — only SambaNova new this cycle), GPU/CUDA 13/68 (0.191, down from 0.207 — only SambaNova new this cycle), GitOps 9/68 (0.132, down from 0.155 — zero new hits this cycle). All three remain well below threshold and continue to be owned at their higher-level repos per the ownership rule.

**Methodology sanity check.** Frequency counts required + preferred mentions together, unchanged vs prior cycles. The strict required-only count for vector/RAG is 20/68 = 0.294 — fractionally below 0.30 on strict interpretation. This is why the delta is a conservative single-exercise extension of an existing module rather than a new standalone module or project. If the December cycle reproduces this cycle's required-only share, strict-required will also cross threshold and the current light-touch promotion will have been correctly scoped.

**Honest sample caveat.** The research agent dropped 7 candidates for cause this cycle (too senior, staffing agency, expired, excluded employer, missing verbatim skill list, clearance-gated). The 10 postings kept are the clean set; padding to 15 would have introduced staffing-agency reposts and senior roles mislabeled as junior.

## How to apply (after approval)

```sh
aicg org plan-delta-apply \
  --role junior-engineer \
  --delta .aicg/curriculum-plan-delta-v2.json
```

The CLI re-validates the delta against the current baseline. If the validator's flags or rejects have changed since this proposal was written (e.g., new postings landed in another role), the apply will surface them before writing.

After apply:

1. The content-generator will scaffold `lessons/mod-004-ml-basics/exercise-06-embeddings-and-vector-search/` (exercise README + starter code + solution + test harness).
2. `CURRICULUM.md`, `CURRICULUM_INDEX.md`, and `VERSIONS.md` will regenerate from the merged manifest (do NOT hand-edit them).
3. `req-018-vector-db-rag` in `.aicg/job-requirements.json` already reflects the promoted owner_role (ai-infra-junior-engineer-learning) and coverage_path (lessons/mod-004-ml-basics/exercise-06-embeddings-and-vector-search) — this change was written as part of this packet.

## Next-cycle watch items

- **Vector/RAG required-only vs required+preferred.** This cycle crossed on the cumulative lenient count (0.324) but sat fractionally below on strict required-only (0.294). If December reproduces, strict count will cross too — at which point the awareness-layer exercise should be re-scoped to a slightly larger exercise or an addition to project-05-production-ml-capstone (end-to-end RAG serving + eval).
- **LLM-serving stack bifurcation.** Mainstream junior AI postings (Klaviyo, iManage, ServiceTitan, Visa, NRG, Indium, FNZ) treat RAG / retrieval as the required LLM-application primitive but do NOT list serving-stack internals (vLLM / Triton / TRT-LLM). Only hardware/GPU-cloud specialists (SambaNova this cycle, NVIDIA last cycle) list serving-stack depth as required. Expect this bifurcation to continue; the owner-at-level-20 assignment remains correct.
- **Agentic AI / MCP / tool-calling.** 5 of 10 fresh postings (Klaviyo, ServiceTitan, Visa, NRG, Indium, FNZ) explicitly list "agentic AI", "agent orchestration", "tool calling", or "MCP" at the required or strong-preferred level. This is a new sub-signal to begin tracking separately from vanilla RAG — RAG + agents + tools are being bundled together but they are distinct skills. Not yet a threshold candidate.
- **OpenTelemetry displacing Prometheus/Grafana.** FNZ's AI Platform Engineer posting lists OpenTelemetry + distributed tracing in place of Prom/Grafana. Still one posting; worth tracking across future cycles since the junior-tier observability signal has been locked on Prom/Grafana for 2+ years and a shift to OTel would warrant a lesson update in mod-009.
