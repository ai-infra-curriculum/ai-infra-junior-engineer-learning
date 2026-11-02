# Junior AI Infrastructure Engineer — Job Requirements Report

**Role:** Junior AI Infrastructure Engineer (level 10)
**Repository:** `ai-infra-junior-engineer-learning`
**Generated:** 2026-11-01 (refresh of 2026-10-01 packet)
**Postings analyzed:** 68 (date window: ~2025-09 to 2026-11; 25 dated in last 90 days 2026-08-01 → 2026-11-01)
**Machine-readable source:** [`.aicg/job-requirements.json`](.aicg/job-requirements.json)
**Curriculum-plan delta (v2):** [`.aicg/curriculum-plan-delta-v2.json`](.aicg/curriculum-plan-delta-v2.json)

---

## 1. How to read this document

- Each requirement is grouped by category, lists the **owner role** (per the curriculum hierarchy), and points to where it is covered in this repo *or* in a higher-level repo.
- Ownership follows the lowest-level rule: a requirement is owned by the lowest level where it is genuinely required, and higher-level roles only re-own it when they need extra depth, architecture, or leadership context.
- Frequencies are the number of analyzed postings (out of 68) that explicitly listed the requirement; junior postings cluster on a stable core (Docker, K8s, Python, AWS/GCP, Prometheus, CI/CD). As of the November 2026 refresh, vector DBs + RAG at the awareness layer has crossed the 0.30 addition threshold and is promoted to level-10 owned coverage (see §2.4 and §3.3).
- All evidence postings and quotes are in [`.aicg/job-requirements.json`](.aicg/job-requirements.json) under `postings[]` (referenced by ID below).

---

## 2. Market snapshot (last 90 days)

- **Title soup.** Almost no postings use the literal title "Junior AI Infrastructure Engineer." The role is hired under: Junior MLOps, Junior DevOps (AI Platform), Junior Platform Operations, Junior Data Platform, Junior IaC, Associate MLOps, ML Engineer I, AI Infrastructure Engineer I, New College Grad ML Infra.
- **Experience band.** 0–3 years is the most common ask; "Associate" / "I" / "Early Career" titles are explicitly entry-level. A handful (e.g. NYT MLOps at 2+ yrs) are border-line level 20.
- **Salary band.** USD ~$60k–$150k base for true entry-level; the median posting that lists a salary clusters $85k–$125k.
- **Stable core stack (>60% of postings):** Python, Linux, Git, Docker, Kubernetes, one cloud (AWS dominant), CI/CD, Prometheus/Grafana, Terraform basics, REST API frameworks (Flask / FastAPI).
- **Preferred-not-required at level 10:** MLflow, Airflow/Prefect, Helm authoring, GitOps (Argo CD), LLM serving (vLLM, Triton, TRT-LLM), CUDA/NCCL, Spark/Ray. (Vector DBs + RAG are no longer "preferred-not-required" — as of the November 2026 refresh they are required at the junior tier in a plurality of fresh postings and the awareness layer is owned at level 10; see §2.4 and §3.3.)
- **2026 momentum signal — threshold crossed.** Vector-DB + RAG now **22/68 (0.324)**, up from 14/58 (0.241) in October — +0.083, the second consecutive single-cycle acceleration and the first time any watched signal has cleared the 0.30 addition threshold since tracking began. In the fresh November sample (n=10), 6 of 10 postings require RAG at the junior tier (Klaviyo, AppZen, ServiceTitan, Visa, Indium, FNZ) and 2 of 10 list it preferred (iManage, NRG) — total 8/10 fresh (0.80). Signal has spread into tier-1 financial infrastructure (Visa Austin), B2B SaaS and legal tech (Klaviyo, iManage, ServiceTitan), US energy utilities (NRG at $65-75K), Indian services firms (AppZen, Indium at 0-YoE fresher tier), and Indian captive AI platform (FNZ). LLM serving (12/68 = 0.176) and GPU/CUDA (13/68 = 0.191) stayed flat with denominator growth; GitOps (9/68 = 0.132) regressed. The three remain owned at their higher-level repos.

### 2.1 July 2026 refresh (delta since 2026-06-01)

A ~30-day sweep added 10 new postings (`p33-lockheed-ai-infra-platform-ops-junior` … `p42-dv01-mlops-cloud-eng`) for a rolling window of 42, of which 41 are dated 2026-04-01 or later (last 90 days).

- **No new stable-core skill has crossed the 0.30 addition threshold.** Python, Docker, Kubernetes, one cloud, CI/CD, Prometheus/Grafana, Terraform basics, MLflow, and Airflow/Prefect/Dagster remain the dominant required stack.
- **Preferred-not-required items held steady at the junior tier:** LLM serving 6/42 (0.14), vector DB + RAG 7/42 (0.17), GPU/CUDA/NCCL 8/42 (0.19), GitOps 7/42 (0.17). All below the 0.30 addition threshold, and all still owned by their higher-level tracks (see §3.9).
- **Notable additions:** NVIDIA `AI/ML Infra SWE - GPU Clusters (New Grad 2026)` reinforces that GPU-cluster / Slurm / PyTorch DDP+FSDP work stays firmly owned at level 35 (Performance Engineer). Lockheed's junior AI-Infra Platform Ops posting is the first entry-level posting in the sample to list Argo CD *by name* alongside GitLab CI / Jenkins — still one posting, still owned at level 20.
- **Verdict.** No material market shift. Curriculum-plan delta v2 is intentionally empty (`additions: []`, `updates: []`, `removals: []`) — see [`.aicg/curriculum-plan-delta-v2.json`](.aicg/curriculum-plan-delta-v2.json).

### 2.2 August 2026 refresh (delta since 2026-07-01)

A ~30-day sweep added 10 new postings (`p43-newsbreak-swe-ml-infra-newgrad` … `p52-jobgether-mlops-early-band`) for a rolling window of 52, of which 51 are dated 2026-05-01 or later (last 90 days). Sources include NewsBreak, NVIDIA, Loop, Together AI, Gore Mutual, TensorOps, CyferSoft, AI Singapore (NUS), and a Lever-hosted Jobgether listing.

- **Watched-signal update.** All four preferred-not-required signals ticked up modestly in the last 30 days but remain below the 0.30 addition threshold in the rolling 90-day window:

  | Signal | July baseline | August rolling | Δ | Verdict |
  |---|---|---|---|---|
  | LLM serving (vLLM / TRT-LLM / Triton) | 6/42 = 0.14 | 10/52 = 0.19 | +0.05 | Below threshold — watch |
  | Vector DBs + RAG | 7/42 = 0.17 | 10/52 = 0.19 | +0.02 | Below threshold — watch |
  | GPU / CUDA / NCCL | 8/42 = 0.19 | 11/52 = 0.21 | +0.02 | Below threshold — watch |
  | GitOps (Argo CD / Flux) | 7/42 = 0.17 | 9/52 = 0.17 | 0 | Flat — still preferred, never required |

- **Sample bias caveat.** Growth on LLM/RAG/GPU is concentrated at AI-native, inference-first, or GPU-cloud employers (NVIDIA new-grad postings p44/p45, Together AI, TensorOps, Loop, NewsBreak). Traditional-enterprise and Associate-band listings in the sample (Gore Mutual, CyferSoft, AI Singapore, Jobgether-hosted MLOps) do NOT list these as required at the junior tier — the stable Docker/K8s/Python/cloud/CI-CD/MLflow/Airflow core still dominates their required-skills lists.
- **Notable observations at the junior tier.**
  - **TensorOps** and **Loop 2026 new grad** are the first entry-level postings in the rolling window to list *RAG* as a required skill (not preferred). Two postings out of 52 — not yet threshold-crossing, but the first crack.
  - **AI Singapore (NUS) Platforms Engineer, MLOps** is the second junior-tier posting in the sample to name **Argo CD** explicitly (the first was Lockheed `p33` in July). Still a preferred listing.
  - **NVIDIA** new-grad postings (p44 GPU Clusters, p45 AI Inference Perf) continue to dominate the GPU/CUDA signal but remain best owned by the level-35 Performance Engineer track — they hire for a specialist role, not a general junior AI-infra engineer.
- **Verdict.** No material market shift. Curriculum-plan delta v2 remains intentionally empty (`additions: []`, `updates: []`, `removals: []`) — see [`.aicg/curriculum-plan-delta-v2.json`](.aicg/curriculum-plan-delta-v2.json). Flagged for close watch next cycle: if LLM serving or RAG grows by another ~0.05 the next refresh, the addition threshold will be reached and a promotion of those items from level 20/30 "linked" coverage to level-10 owned modules should be revisited.

### 2.3 October 2026 refresh (delta since 2026-08-01)

A ~60-day sweep added 6 new postings (`p53-torc-robotics-ml-engineer-i-mlops-framework` … `p58-scale-ai-swe-new-grad`) for a rolling cumulative sample of 58. The research window is 2026-07-01 → 2026-10-01; 22 postings have `date_observed` within that strict 90-day window. Sources include Greenhouse (Torc, Scale AI), AshbyHQ (Quora), BlackRock Careers, Vector Institute (via freehire), and AvePoint Careers.

- **Watched-signal update.** Only one of the four signals moved materially; two slightly dropped, one was flat:

  | Signal | August rolling | October rolling | Δ | Verdict |
  |---|---|---|---|---|
  | LLM serving (vLLM / TRT-LLM / Triton) | 10/52 = 0.192 | 11/58 = 0.190 | ≈0 | Flat — the August concern that LLM serving was accelerating did NOT reproduce this cycle |
  | Vector DBs + RAG | 10/52 = 0.192 | 14/58 = 0.241 | +0.049 | **Accelerating** — largest single-cycle move since tracking began; still below threshold |
  | GPU / CUDA / NCCL | 11/52 = 0.212 | 12/58 = 0.207 | −0.005 | Flat/slight drop — pattern holds: GPU-depth concentrates above the 2-3 YoE line |
  | GitOps (Argo CD / Flux) | 9/52 = 0.173 | 9/58 = 0.155 | −0.018 | Flat/slight drop — still preferred, never required |

- **Fresh-sample tilt.** In the n=6 fresh sample alone, vector/RAG hit 4/6 (0.67) — a dramatic single-cycle tilt. BlackRock lists LangChain + LlamaIndex + RAG + Faiss/Chroma as *required* at the Associate (1-3 YoE) band — the first tier-1 finance employer in the entire sample to do so. Scale AI's new-grad SWE posting literally uses "build a customer service RAG application that handles thousands of questions a day" as the day-one project description. Vector Institute lists LangChain in preferred for a Canadian Associate role priced at the sub-US$75k-equivalent band. AvePoint lists vector-DB in preferred for an entry-level Junior AI Engineer role in Vietnam. The signal is spreading beyond the AI-native / inference-first cluster into finance, non-profit research, and non-US entry-level roles.
- **Sample caveats.** 6 fresh postings is lower cadence than the 10/cycle August and July achieved; the agent dropped ~6 candidates for cause (too senior, staffing agency, expired, excluded employer, missing verbatim skill list). Reducto's LLM/ML Engineer posting required 3+ YoE and ~$200K-$300K comp (effectively mid-level), suggesting the LLM-serving signal is concentrating at the 2-3 YoE boundary rather than at 0-2 YoE. Honest "only 6 clean postings" is kept over padded output per the research-packet discipline.
- **Promotion contingency for 2026-11.** If next cycle reproduces anywhere near this cycle's 4/6 (0.67) in-sample rate for vector/RAG, cumulative will cross 0.30 and req-018-vector-db-rag should be promoted from level-30 "linked" coverage to a level-10 owned requirement. Suggested smallest usable slice: extend `project-05-production-ml-capstone` with embeddings → pgvector → retrieval, re-using the existing PostgreSQL coverage in module 008 (keeps the delta well under the 20% addition cap). Alternative: a single new exercise under `mod-004-ml-basics` covering "embeddings + similarity search" as the awareness layer.
- **Verdict.** No material market shift *yet*. Curriculum-plan delta v2 remains intentionally empty (`additions: []`, `updates: []`, `removals: []`) — see [`.aicg/curriculum-plan-delta-v2.json`](.aicg/curriculum-plan-delta-v2.json). The vector/RAG signal is the primary promotion candidate for the November cycle; the LLM-serving and GPU watch items set in August can be downgraded in urgency.

### 2.4 November 2026 refresh (delta since 2026-10-01) — **first threshold crossing since tracking began**

A ~30-day sweep added 10 new postings (`p59-crowe-ml-software-engineer-1` … `p68-fnz-ai-platform-engineer-azure-ai`) for a rolling cumulative sample of 68. The research window is 2026-08-01 → 2026-11-01; 25 postings have `date_observed` within that strict 90-day window. Nine of the ten fresh postings were posted in October 2026; p59 Crowe was posted 2026-08-14 (within window). Sources include Greenhouse (Klaviyo campus), Lever (AppZen), Workday (ServiceTitan, Visa), AshbyHQ (via mirrors), ApplyToJob (iManage), direct employer boards (NRG Energy, SambaNova via Zapply mirror), jobfound.org (Indium, FNZ), freehire.me (Crowe, NRG mirror), and the dozman99/new-grad-radar curated AI-focused new-grad digest.

- **Watched-signal update — the threshold crossed.** Vector/RAG cleared the 0.30 addition threshold for the first time since tracking began:

  | Signal | October rolling | November rolling | Δ | Verdict |
  |---|---|---|---|---|
  | **Vector DBs + RAG** | **14/58 = 0.241** | **22/68 = 0.324** | **+0.083** | **Threshold crossed — promoted** |
  | LLM serving (vLLM / TRT-LLM / Triton / SGLang) | 11/58 = 0.190 | 12/68 = 0.176 | −0.014 | Below threshold — stays level 20 |
  | GPU / CUDA / NCCL | 12/58 = 0.207 | 13/68 = 0.191 | −0.016 | Below threshold — stays level 35 |
  | GitOps (Argo CD / Flux) | 9/58 = 0.155 | 9/68 = 0.132 | −0.023 | Flat/regressed — stays level 20 |

- **Fresh-sample tilt.** In the n=10 fresh sample, vector/RAG hit 6 required + 2 preferred = 8/10 (0.80), closely reproducing October's 4/6 (0.67). Required-at-junior-tier postings this cycle: Klaviyo AI Engineer I (Boston, $104-156K), AppZen AI/ML Engineer (Pune), ServiceTitan AI Engineer (US-remote, $138-221K zone-based), Visa SW Engineer LangChain/RAG track (Austin, $86.5-134.4K), Indium Fresher (Chennai/Bangalore, 0 YoE), FNZ AI Platform Engineer (Gurugram, Azure+AI). Preferred-at-junior-tier: iManage Applied AI Engineer (Chicago, $100-130K), NRG Energy Agentic AI Developer (Houston/Princeton, $65-75K). The signal has clearly spread beyond the AI-native / inference-first cluster: tier-1 financial infrastructure (Visa), B2B SaaS and legal tech (Klaviyo, iManage, ServiceTitan), US energy utilities (NRG at low $65-75K band), Indian services firms (AppZen, Indium at fresher 0-YoE), and Indian captive AI platform (FNZ).
- **Promotion of req-018-vector-db-rag.** Per the Oct packet's explicit promotion contingency and the ownership rule (lowest-level role where genuinely required), req-018 is promoted from level-30 "linked" (ai-infra-ml-platform-learning) to level-10 "covered" via one new exercise under the existing `mod-004-ml-basics` module: `exercise-06-embeddings-and-vector-search`. Scope is deliberately minimal — the awareness layer only: embeddings concepts (dense vs sparse), similarity metrics (cosine / dot / euclidean), a minimal pgvector hands-on reusing mod-008 PostgreSQL coverage, and a toy end-to-end retrieval pattern (query embedding → top-k docs → prompt stuffing). Deeper vector-DB internals (ANN index tuning, sharding, replication, hybrid search, re-ranking) remain owned at level 30. This extends existing content (preferred per continuity bias) rather than creating a new module.
- **Methodology sanity check.** Frequency counts required + preferred mentions together, unchanged vs prior cycles. The strict required-only count for vector/RAG is 20/68 = 0.294 — fractionally below 0.30 on strict interpretation. This is why the delta is a conservative single-exercise extension of an existing module rather than a new standalone module or project. If December reproduces this cycle's required-only share, strict-required will also cross threshold and the current light-touch promotion will have been correctly scoped.
- **Honest sample caveat.** The research agent dropped 7 candidates for cause (too senior, staffing agency, expired, excluded employer, missing verbatim skill list, clearance-gated — e.g., JHU APL AI/ML Platform Engineer requires US citizenship + Interim Secret clearance, Teradata AI Infra Engineer requires 3+ YoE and Go/Rust/CUDA depth, Hop requires 3-5 YoE). The 10 postings kept are the clean set; padding to 15 would have introduced staffing-agency reposts and senior roles mislabeled as junior.
- **Verdict.** First material market shift since tracking began. Curriculum-plan delta v2 contains **1 update** (req-018-vector-db-rag) and **0 additions / 0 removals** — well under the 20% addition cap and 10% removal cap. See [`.aicg/curriculum-plan-delta-v2.json`](.aicg/curriculum-plan-delta-v2.json) and [`RESEARCH_PROPOSAL_2026-11.md`](RESEARCH_PROPOSAL_2026-11.md). Next-cycle watch items: strict-required-only crossing for vector/RAG (currently 0.294), agentic AI / MCP / tool-calling as a distinct sub-signal (5-of-10 fresh postings list it alongside RAG), and OpenTelemetry displacing Prometheus/Grafana at the junior tier (first appearance this cycle via FNZ).

---

## 3. Requirements by category

### 3.1 Languages & local tooling (owned at level 10 ✅)

| ID | Requirement | Owner | Coverage | Evidence |
|----|-------------|-------|----------|----------|
| req-001 | **Python** (production-quality, not notebooks) | level 10 | [`lessons/mod-001-python-fundamentals/`](lessons/mod-001-python-fundamentals/) | p01, p02, p03, p04, p13, p14, p20, p25, p43, p44, p46, p47, p48, p49, p50, p51, p52, p53, p54, p55, p56, p57, p58, p59, p60, p61, p62, p63, p64, p65, p66, p67, p68 |
| req-002 | **Linux** administration + shell | level 10 | [`lessons/mod-002-linux-essentials/`](lessons/mod-002-linux-essentials/) | p01, p14, p16, p21, p28, p51, p59 |
| req-003 | **Git / GitHub / GitLab** workflows | level 10 | [`lessons/mod-003-git-version-control/`](lessons/mod-003-git-version-control/) | p02, p04, p14, p43, p48, p50, p56, p61, p62, p63, p67 |
| req-021 | **Bash / shell scripting** | level 10 | [`lessons/mod-002-linux-essentials/`](lessons/mod-002-linux-essentials/) | p01, p04, p14 |

Existing coverage is sufficient — no additions proposed.

### 3.2 Containers & orchestration (owned at level 10 ✅)

| ID | Requirement | Owner | Coverage | Evidence |
|----|-------------|-------|----------|----------|
| req-004 | **Docker** (Dockerfiles, multi-stage, Compose) | level 10 | [`lessons/mod-005-docker-containers/`](lessons/mod-005-docker-containers/) | p01, p02, p03, p04, p17, p32, p44, p48, p49, p51, p52, p54, p55, p56, p59, p61, p62, p65, p66, p67 |
| req-005 | **Kubernetes** (Pods/Deployments/Services/HPA/kubectl) | level 10 | [`lessons/mod-006-kubernetes-intro/`](lessons/mod-006-kubernetes-intro/) | p01, p02, p03, p04, p30, p32, p44, p47, p49, p51, p52, p54, p55, p56, p61, p66, p67, p68 |
| req-022 | **Helm** at consumer level | level 10 | [`lessons/mod-006-kubernetes-intro/`](lessons/mod-006-kubernetes-intro/) | p01, p02 |

### 3.3 APIs, data, and ML basics (owned at level 10 ✅)

| ID | Requirement | Owner | Coverage | Evidence |
|----|-------------|-------|----------|----------|
| req-006 | **REST APIs** for ML serving (Flask / FastAPI) | level 10 | [`lessons/mod-007-apis-web-services/`](lessons/mod-007-apis-web-services/) | p03, p17, p19, p59, p60, p62, p63, p65, p67 |
| req-007 | **SQL & PostgreSQL** for ML metadata | level 10 | [`lessons/mod-008-databases-sql/`](lessons/mod-008-databases-sql/) | p02, p13, p63, p66, p67 |
| req-010 | **PyTorch / TensorFlow / Scikit-learn** (load + run pretrained models) | level 10 | [`lessons/mod-004-ml-basics/`](lessons/mod-004-ml-basics/) | p05, p20, p21, p23, p25, p53, p54, p56, p57, p61, p62, p64, p66 |
| req-018 | **Embeddings & vector search** (awareness-layer RAG) — *new in Nov 2026, see §2.4* | level 10 | [`lessons/mod-004-ml-basics/exercise-06-embeddings-and-vector-search`](lessons/mod-004-ml-basics/exercise-06-embeddings-and-vector-search) *(scaffolded on delta apply)* | p06, p13, p19, p46, p49, p55, p56, p57, p58, p60, p61, p62, p63, p65, p66, p67, p68 |

### 3.4 Cloud & operations (owned at level 10 ✅)

| ID | Requirement | Owner | Coverage | Evidence |
|----|-------------|-------|----------|----------|
| req-009 | **AWS / GCP / Azure** fundamentals | level 10 | [`lessons/mod-010-cloud-platforms/`](lessons/mod-010-cloud-platforms/) | p01, p02, p03, p04, p12, p14, p17, p32, p43, p44, p48, p49, p50, p52, p54, p55, p56, p61, p63, p66, p67, p68 |
| req-020 | **Secrets management & basic security** | level 10 | [`projects/project-05-production-ml-capstone/`](projects/project-05-production-ml-capstone/) | p01, p10, p14 |

### 3.5 Monitoring & observability (owned at level 10 ✅)

| ID | Requirement | Owner | Coverage | Evidence |
|----|-------------|-------|----------|----------|
| req-008 | **Prometheus & Grafana** (and OpenTelemetry at junior tier) | level 10 | [`lessons/mod-009-monitoring-basics/`](lessons/mod-009-monitoring-basics/) | p01, p02, p03, p07, p14, p15, p48, p51, p52, p68 |
| req-013 | **ML model monitoring & data drift** basics | level 10 | [`projects/project-04-monitoring-alerting/`](projects/project-04-monitoring-alerting/) | p02, p03, p04, p17, p53 |
| req-016 | **Incident response & on-call** basics | level 10 | [`lessons/mod-009-monitoring-basics/`](lessons/mod-009-monitoring-basics/) (partial — see §4) | p07, p14, p15 |

### 3.6 Automation, IaC, CI/CD (owned at level 10 ✅, partial)

| ID | Requirement | Owner | Coverage | Evidence |
|----|-------------|-------|----------|----------|
| req-011 | **CI/CD pipelines** for ML (GitHub Actions / Jenkins / GitLab CI) | level 10 | [`projects/project-05-production-ml-capstone/`](projects/project-05-production-ml-capstone/) (partial — see §4) | p01, p02, p03, p04, p08, p17, p32, p48, p50, p51, p52, p53, p59, p62, p67, p68 |
| req-012 | **Terraform** basics for IaC | level 10 | [`projects/project-05-production-ml-capstone/`](projects/project-05-production-ml-capstone/) | p01, p02, p03, p08, p09, p12, p14, p30, p53, p67, p68 |

### 3.7 MLOps workflows (owned at level 10 ✅)

| ID | Requirement | Owner | Coverage | Evidence |
|----|-------------|-------|----------|----------|
| req-014 | **MLflow** experiment tracking + registry | level 10 | [`projects/project-03-ml-pipeline-tracking/`](projects/project-03-ml-pipeline-tracking/) | p03, p17, p32, p48, p51, p52, p66 |
| req-015 | **Airflow / Prefect** data + ML pipelines | level 10 | [`projects/project-03-ml-pipeline-tracking/`](projects/project-03-ml-pipeline-tracking/) | p02, p03, p13, p32, p53 |

### 3.8 Soft skills (owned at level 10 ✅)

| ID | Requirement | Owner | Coverage | Evidence |
|----|-------------|-------|----------|----------|
| req-026 | Communication / cross-functional collaboration | level 10 | [`CURRICULUM.md#professional-skills`](CURRICULUM.md) | p04, p05, p07, p43, p48, p55, p58, p59, p63, p66 |

### 3.9 Out of scope at level 10 — linked to owner role

These requirements appear in the postings but are explicitly preferred-not-required for junior roles, and they belong to higher-level tracks. The junior curriculum points to them; no level-10 module is justified by the current evidence.

| ID | Requirement | Owner role (level) | Where it lives |
|----|-------------|--------------------|----------------|
| req-017 | **LLM serving** (vLLM / TensorRT-LLM / Triton / SGLang) | `ai-infra-engineer-learning` (20) | [mod-110-llm-infrastructure](https://github.com/ai-infra-curriculum/ai-infra-engineer-learning/blob/main/lessons/mod-110-llm-infrastructure/README.md) |
| req-019 | **GPU / CUDA / NCCL** deep work | `ai-infra-performance-learning` (35) | [ai-infra-performance-learning](https://github.com/ai-infra-curriculum/ai-infra-performance-learning) |
| req-023 | **Distributed processing** (Spark / Dask / Ray) | `ai-infra-engineer-learning` (20) | [ai-infra-engineer-learning](https://github.com/ai-infra-curriculum/ai-infra-engineer-learning) |
| req-024 | **Bare-metal / Slurm / HPC** schedulers | `ai-infra-performance-learning` (35) | [ai-infra-performance-learning](https://github.com/ai-infra-curriculum/ai-infra-performance-learning) |
| req-025 | **GitOps** (Argo CD / Flux) | `ai-infra-engineer-learning` (20) | [ai-infra-engineer-learning](https://github.com/ai-infra-curriculum/ai-infra-engineer-learning) |

For each, Module 004 / Module 010 / Project 02 already gives the awareness layer (e.g., "GPU vs CPU for inference", "managed Kubernetes services", "model versioning") that a junior needs to recognize the technology and hand off to the next level.

**Note on req-018 (vector DBs & RAG plumbing).** Previously listed here as linked to ai-infra-ml-platform-learning. Promoted to level-10 owned coverage in the November 2026 refresh (see §2.4 and §3.3); the awareness-layer slice (embeddings + similarity search + minimal retrieval) is now owned at level 10 via `mod-004-ml-basics/exercise-06-embeddings-and-vector-search`. Deeper vector-DB internals (ANN index tuning, sharding, replication, hybrid search, re-ranking) still live at `ai-infra-ml-platform-learning` (30).

---

## 4. Coverage gaps (partial) — and the recommendation

Two requirements are technically covered but at less depth than the market now demands. Both are addressed inside existing modules/projects rather than via new modules — the evidence does not justify net-new level-10 modules.

### 4.1 CI/CD pipelines for ML (req-011)

- **Where it is now.** The capstone project (`project-05`) lists GitHub Actions and CI/CD as a deliverable; no standalone module owns the end-to-end pipeline pattern (build → test → image → deploy → trigger retrain).
- **Evidence.** 16/68 postings explicitly require CI/CD for ML deployments (p01, p02, p03, p04, p08, p17, p32, p48, p50, p51, p52, p53, p59, p62, p67, p68). NYT's posting is the clearest spec: "Develop robust CI/CD pipelines for automated model training, validation, deployment, and retraining." FNZ's Oct 2026 AI Platform Engineer posting is the most recent reinforcement (GitHub Actions + Terraform + K8s production ops bundled at fresher tier).
- **Recommendation.** Reinforce inside the existing project READMEs. No curriculum-plan-delta entry is proposed; the existing project scope already requires the deliverable.

### 4.2 Incident response & on-call basics (req-016)

- **Where it is now.** Module 009 teaches alerting rule design but does not walk the on-call lifecycle (paging, triage, runbooks, postmortems).
- **Evidence.** 3 postings explicitly mention on-call rotation as a junior responsibility (p07 Capgemini, p14 Trulioo "24/7 on-call rotation," p15 SBC Innovations).
- **Recommendation.** This is a narrow gap — three postings — and is more naturally taught inside Module 009 by extending its existing alerting content. Treated as content-level reinforcement, not a curriculum-plan-delta module. If the runner wants a module-level proposal, see [`.aicg/curriculum-plan-delta.json`](.aicg/curriculum-plan-delta.json) — currently empty by design.

---

## 5. Where this curriculum already matches the market

Across the 68 postings, the level-10 stable-core stack (Python / Linux / Git / Docker / Kubernetes / one cloud / CI/CD / Prometheus / FastAPI / Postgres / MLflow / Airflow) still covers >80% of explicit must-have requirements. The 10-module + 5-project structure aligns 1:1 with the most-cited skills, and every required level-10 requirement is currently covered.

The role hierarchy is working as intended: gaps that *would* be additive at level 10 for LLM serving, GPU work, distributed Spark/Ray, GitOps, and Slurm are already covered at the role-appropriate higher level, and linking (not duplicating) remains the right move for those. **The exception this cycle is vector DBs + RAG**, which crossed the 0.30 addition threshold in the November 2026 refresh (22/68 = 0.324) with the signal spreading from the AI-native cluster into tier-1 finance (BlackRock, Visa), mainstream B2B SaaS (Klaviyo, iManage, ServiceTitan), US utilities (NRG), and Indian services + captive AI platforms (AppZen, Indium, FNZ). Per the ownership rule, the awareness-layer slice of req-018 is now owned at level 10 via `mod-004-ml-basics/exercise-06-embeddings-and-vector-search` — the first promotion since tracking began. Deeper vector-DB internals remain at level 30.

---

## 6. External resources for out-of-scope items

For learners who want to extend beyond the level-10 scope before promoting to a higher role track:

- **LLM serving** — vLLM docs (`https://docs.vllm.ai/`), NVIDIA Triton docs (`https://docs.nvidia.com/deeplearning/triton-inference-server/`), TensorRT-LLM repo.
- **Vector DBs & RAG** — pgvector docs, Weaviate / Qdrant / Milvus quickstarts, LangChain "RAG from scratch" guides.
- **GPU/CUDA** — NVIDIA "Accelerated Computing" learning paths; NCP-AII certification track.
- **Distributed processing** — Ray, Dask, and Spark official quickstarts.
- **GitOps** — Argo CD getting started, Flux v2 docs.
- **Slurm / HPC** — SchedMD "Slurm in 10 minutes," NVIDIA DGX SuperPOD reference architectures.

These are reference-only and intentionally not pulled into the level-10 curriculum.

---

## 7. Methodology

- Sources: Indeed, Built In, ZipRecruiter, Glassdoor, LinkedIn, Greenhouse-hosted boards (incl. Klaviyo campus), Lever-hosted boards (AppZen), AshbyHQ, Workday-hosted boards (Workday, BCBS, Astreya, NVIDIA, HPE, CMU, Lockheed, ServiceTitan, Visa), Breezy (Accrete), Workable (Quadric), the NUS careers portal, Remoterocketship, Remotive, ApplyToJob (iManage), direct employer boards (BlackRock Careers, Vector Institute via freehire, NRG Energy, SambaNova via Zapply), jobfound.org (Indium, FNZ), dreamworkhq / zapply (Visa / SambaNova mirrors), freehire.me (Crowe), the speedyapply/2026-AI-College-Jobs curated new-grad list, dozman99/new-grad-radar curated AI-focused new-grad digest, Hacker News "Who is hiring" archives.
- Date window: Sept 2025 → Nov 2026. Strict last-90-days window (2026-08-01 → 2026-11-01) contains 25 postings; the remaining 43 are retained from prior cycles because they confirm the stable-core baseline and most ownership assignments haven't changed.
- 68 postings analyzed (specification asked for ≥25); ~50 had retrievable full descriptions, the remaining ~18 came from aggregated / paywalled listings where title/employer/level were confirmable but the full posting body was not always fully retrievable — these are still counted because they confirm role *prevalence* and *level*, even when individual skills could not always be extracted.
- July 2026 refresh added 10 postings (`p33`–`p42`); August 2026 added 10 more (`p43`–`p52`); October 2026 added 6 (`p53`–`p58`); November 2026 added 10 (`p59`–`p68`). The November refresh is the first cycle since tracking began where any watched signal crossed the 0.30 addition threshold: vector/RAG moved from 14/58 (0.241) to 22/68 (0.324). Curriculum-plan-delta v2 contains 1 update (req-018 promoted from level-30 linked to level-10 covered via one new exercise under mod-004-ml-basics) and 0 additions / 0 removals — well under the 20% / 10% caps. The agent dropped 7 candidates for cause this cycle (too senior, staffing agency, expired, excluded employer, missing verbatim skill list, clearance-gated) rather than pad the sample.
- Ownership rule applied: a requirement appears at the lowest role where it is genuinely required. If a higher-level repo already owns a requirement (e.g. LLM serving at level 20), it is *linked*, not duplicated. The November cycle's one ownership change (req-018 vector/RAG, level 30 → level 10 awareness-layer only; deeper internals stay at level 30) is a direct application of this rule to the newly-threshold-crossing signal.

---

**Maintained by VeriSwarm.ai**
