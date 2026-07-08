# Junior AI Infrastructure Engineer — Job Requirements Report

**Role:** Junior AI Infrastructure Engineer (level 10)
**Repository:** `ai-infra-junior-engineer-learning`
**Generated:** 2026-07-01 (refresh of 2026-06-01 packet)
**Postings analyzed:** 42 (date window: ~2025-09 to 2026-07; 41 dated in last 90 days)
**Machine-readable source:** [`.aicg/job-requirements.json`](.aicg/job-requirements.json)
**Curriculum-plan delta (v2):** [`.aicg/curriculum-plan-delta-v2.json`](.aicg/curriculum-plan-delta-v2.json)

---

## 1. How to read this document

- Each requirement is grouped by category, lists the **owner role** (per the curriculum hierarchy), and points to where it is covered in this repo *or* in a higher-level repo.
- Ownership follows the lowest-level rule: a requirement is owned by the lowest level where it is genuinely required, and higher-level roles only re-own it when they need extra depth, architecture, or leadership context.
- Frequencies are the number of analyzed postings (out of 42) that explicitly listed the requirement; junior postings cluster on a stable core (Docker, K8s, Python, AWS/GCP, Prometheus, CI/CD) and treat LLM / GPU / RAG as preferred-not-required.
- All evidence postings and quotes are in [`.aicg/job-requirements.json`](.aicg/job-requirements.json) under `postings[]` (referenced by ID below).

---

## 2. Market snapshot (last 90 days)

- **Title soup.** Almost no postings use the literal title "Junior AI Infrastructure Engineer." The role is hired under: Junior MLOps, Junior DevOps (AI Platform), Junior Platform Operations, Junior Data Platform, Junior IaC, Associate MLOps, ML Engineer I, AI Infrastructure Engineer I, New College Grad ML Infra.
- **Experience band.** 0–3 years is the most common ask; "Associate" / "I" / "Early Career" titles are explicitly entry-level. A handful (e.g. NYT MLOps at 2+ yrs) are border-line level 20.
- **Salary band.** USD ~$60k–$150k base for true entry-level; the median posting that lists a salary clusters $85k–$125k.
- **Stable core stack (>60% of postings):** Python, Linux, Git, Docker, Kubernetes, one cloud (AWS dominant), CI/CD, Prometheus/Grafana, Terraform basics, REST API frameworks (Flask / FastAPI).
- **Preferred-not-required at level 10:** MLflow, Airflow/Prefect, Helm authoring, GitOps (Argo CD), vector DBs, LLM serving (vLLM, Triton, TRT-LLM), CUDA/NCCL, Spark/Ray.
- **2026 momentum signal:** LLM / RAG / vector-DB exposure shows up in 6–7 of 32 postings — material, but still preferred and concentrated in NYT, RingCentral, Citi, NVIDIA-new-grad style postings. The same set of postings already lists this clearly as bonus for juniors.

### 2.1 July 2026 refresh (delta since 2026-06-01)

A ~30-day sweep added 10 new postings (`p33-lockheed-ai-infra-platform-ops-junior` … `p42-dv01-mlops-cloud-eng`) for a rolling window of 42, of which 41 are dated 2026-04-01 or later (last 90 days).

- **No new stable-core skill has crossed the 0.30 addition threshold.** Python, Docker, Kubernetes, one cloud, CI/CD, Prometheus/Grafana, Terraform basics, MLflow, and Airflow/Prefect/Dagster remain the dominant required stack.
- **Preferred-not-required items held steady at the junior tier:** LLM serving 6/42 (0.14), vector DB + RAG 7/42 (0.17), GPU/CUDA/NCCL 8/42 (0.19), GitOps 7/42 (0.17). All below the 0.30 addition threshold, and all still owned by their higher-level tracks (see §3.9).
- **Notable additions:** NVIDIA `AI/ML Infra SWE - GPU Clusters (New Grad 2026)` reinforces that GPU-cluster / Slurm / PyTorch DDP+FSDP work stays firmly owned at level 35 (Performance Engineer). Lockheed's junior AI-Infra Platform Ops posting is the first entry-level posting in the sample to list Argo CD *by name* alongside GitLab CI / Jenkins — still one posting, still owned at level 20.
- **Verdict.** No material market shift. Curriculum-plan delta v2 is intentionally empty (`additions: []`, `updates: []`, `removals: []`) — see [`.aicg/curriculum-plan-delta-v2.json`](.aicg/curriculum-plan-delta-v2.json).

---

## 3. Requirements by category

### 3.1 Languages & local tooling (owned at level 10 ✅)

| ID | Requirement | Owner | Coverage | Evidence |
|----|-------------|-------|----------|----------|
| req-001 | **Python** (production-quality, not notebooks) | level 10 | [`lessons/mod-001-python-fundamentals/`](lessons/mod-001-python-fundamentals/) | p01, p02, p03, p04, p13, p14, p20, p25 |
| req-002 | **Linux** administration + shell | level 10 | [`lessons/mod-002-linux-essentials/`](lessons/mod-002-linux-essentials/) | p01, p14, p16, p21, p28 |
| req-003 | **Git / GitHub / GitLab** workflows | level 10 | [`lessons/mod-003-git-version-control/`](lessons/mod-003-git-version-control/) | p02, p04, p14 |
| req-021 | **Bash / shell scripting** | level 10 | [`lessons/mod-002-linux-essentials/`](lessons/mod-002-linux-essentials/) | p01, p04, p14 |

Existing coverage is sufficient — no additions proposed.

### 3.2 Containers & orchestration (owned at level 10 ✅)

| ID | Requirement | Owner | Coverage | Evidence |
|----|-------------|-------|----------|----------|
| req-004 | **Docker** (Dockerfiles, multi-stage, Compose) | level 10 | [`lessons/mod-005-docker-containers/`](lessons/mod-005-docker-containers/) | p01, p02, p03, p04, p17, p32 |
| req-005 | **Kubernetes** (Pods/Deployments/Services/HPA/kubectl) | level 10 | [`lessons/mod-006-kubernetes-intro/`](lessons/mod-006-kubernetes-intro/) | p01, p02, p03, p04, p30, p32 |
| req-022 | **Helm** at consumer level | level 10 | [`lessons/mod-006-kubernetes-intro/`](lessons/mod-006-kubernetes-intro/) | p01, p02 |

### 3.3 APIs, data, and ML basics (owned at level 10 ✅)

| ID | Requirement | Owner | Coverage | Evidence |
|----|-------------|-------|----------|----------|
| req-006 | **REST APIs** for ML serving (Flask / FastAPI) | level 10 | [`lessons/mod-007-apis-web-services/`](lessons/mod-007-apis-web-services/) | p03, p17, p19 |
| req-007 | **SQL & PostgreSQL** for ML metadata | level 10 | [`lessons/mod-008-databases-sql/`](lessons/mod-008-databases-sql/) | p02, p13 |
| req-010 | **PyTorch / TensorFlow / Scikit-learn** (load + run pretrained models) | level 10 | [`lessons/mod-004-ml-basics/`](lessons/mod-004-ml-basics/) | p05, p20, p21, p23, p25 |

### 3.4 Cloud & operations (owned at level 10 ✅)

| ID | Requirement | Owner | Coverage | Evidence |
|----|-------------|-------|----------|----------|
| req-009 | **AWS / GCP / Azure** fundamentals | level 10 | [`lessons/mod-010-cloud-platforms/`](lessons/mod-010-cloud-platforms/) | p01, p02, p03, p04, p12, p14, p17, p32 |
| req-020 | **Secrets management & basic security** | level 10 | [`projects/project-05-production-ml-capstone/`](projects/project-05-production-ml-capstone/) | p01, p10, p14 |

### 3.5 Monitoring & observability (owned at level 10 ✅)

| ID | Requirement | Owner | Coverage | Evidence |
|----|-------------|-------|----------|----------|
| req-008 | **Prometheus & Grafana** | level 10 | [`lessons/mod-009-monitoring-basics/`](lessons/mod-009-monitoring-basics/) | p01, p02, p03, p07, p14, p15 |
| req-013 | **ML model monitoring & data drift** basics | level 10 | [`projects/project-04-monitoring-alerting/`](projects/project-04-monitoring-alerting/) | p02, p03, p04, p17 |
| req-016 | **Incident response & on-call** basics | level 10 | [`lessons/mod-009-monitoring-basics/`](lessons/mod-009-monitoring-basics/) (partial — see §4) | p07, p14, p15 |

### 3.6 Automation, IaC, CI/CD (owned at level 10 ✅, partial)

| ID | Requirement | Owner | Coverage | Evidence |
|----|-------------|-------|----------|----------|
| req-011 | **CI/CD pipelines** for ML (GitHub Actions / Jenkins / GitLab CI) | level 10 | [`projects/project-05-production-ml-capstone/`](projects/project-05-production-ml-capstone/) (partial — see §4) | p01, p02, p03, p04, p08, p17, p32 |
| req-012 | **Terraform** basics for IaC | level 10 | [`projects/project-05-production-ml-capstone/`](projects/project-05-production-ml-capstone/) | p01, p02, p03, p08, p09, p12, p14, p30 |

### 3.7 MLOps workflows (owned at level 10 ✅)

| ID | Requirement | Owner | Coverage | Evidence |
|----|-------------|-------|----------|----------|
| req-014 | **MLflow** experiment tracking + registry | level 10 | [`projects/project-03-ml-pipeline-tracking/`](projects/project-03-ml-pipeline-tracking/) | p03, p17, p32 |
| req-015 | **Airflow / Prefect** data + ML pipelines | level 10 | [`projects/project-03-ml-pipeline-tracking/`](projects/project-03-ml-pipeline-tracking/) | p02, p03, p13, p32 |

### 3.8 Soft skills (owned at level 10 ✅)

| ID | Requirement | Owner | Coverage | Evidence |
|----|-------------|-------|----------|----------|
| req-026 | Communication / cross-functional collaboration | level 10 | [`CURRICULUM.md#professional-skills`](CURRICULUM.md) | p04, p05, p07 |

### 3.9 Out of scope at level 10 — linked to owner role

These requirements appear in the postings but are explicitly preferred-not-required for junior roles, and they belong to higher-level tracks. The junior curriculum points to them; no level-10 module is justified by the current evidence.

| ID | Requirement | Owner role (level) | Where it lives |
|----|-------------|--------------------|----------------|
| req-017 | **LLM serving** (vLLM / TensorRT-LLM / Triton) | `ai-infra-engineer-learning` (20) | [mod-110-llm-infrastructure](https://github.com/ai-infra-curriculum/ai-infra-engineer-learning/blob/main/lessons/mod-110-llm-infrastructure/README.md) |
| req-018 | **Vector DBs & RAG plumbing** | `ai-infra-ml-platform-learning` (30) | [ai-infra-ml-platform-learning](https://github.com/ai-infra-curriculum/ai-infra-ml-platform-learning) |
| req-019 | **GPU / CUDA / NCCL** deep work | `ai-infra-performance-learning` (35) | [ai-infra-performance-learning](https://github.com/ai-infra-curriculum/ai-infra-performance-learning) |
| req-023 | **Distributed processing** (Spark / Dask / Ray) | `ai-infra-engineer-learning` (20) | [ai-infra-engineer-learning](https://github.com/ai-infra-curriculum/ai-infra-engineer-learning) |
| req-024 | **Bare-metal / Slurm / HPC** schedulers | `ai-infra-performance-learning` (35) | [ai-infra-performance-learning](https://github.com/ai-infra-curriculum/ai-infra-performance-learning) |
| req-025 | **GitOps** (Argo CD / Flux) | `ai-infra-engineer-learning` (20) | [ai-infra-engineer-learning](https://github.com/ai-infra-curriculum/ai-infra-engineer-learning) |

For each, Module 004 / Module 010 / Project 02 already gives the awareness layer (e.g., "GPU vs CPU for inference", "managed Kubernetes services", "model versioning") that a junior needs to recognize the technology and hand off to the next level.

---

## 4. Coverage gaps (partial) — and the recommendation

Two requirements are technically covered but at less depth than the market now demands. Both are addressed inside existing modules/projects rather than via new modules — the evidence does not justify net-new level-10 modules.

### 4.1 CI/CD pipelines for ML (req-011)

- **Where it is now.** The capstone project (`project-05`) lists GitHub Actions and CI/CD as a deliverable; no standalone module owns the end-to-end pipeline pattern (build → test → image → deploy → trigger retrain).
- **Evidence.** 7/32 postings explicitly require CI/CD for ML deployments (p01, p02, p03, p04, p08, p17, p32). NYT's posting is the clearest spec: "Develop robust CI/CD pipelines for automated model training, validation, deployment, and retraining."
- **Recommendation.** Reinforce inside the existing project READMEs. No curriculum-plan-delta entry is proposed; the existing project scope already requires the deliverable.

### 4.2 Incident response & on-call basics (req-016)

- **Where it is now.** Module 009 teaches alerting rule design but does not walk the on-call lifecycle (paging, triage, runbooks, postmortems).
- **Evidence.** 3 postings explicitly mention on-call rotation as a junior responsibility (p07 Capgemini, p14 Trulioo "24/7 on-call rotation," p15 SBC Innovations).
- **Recommendation.** This is a narrow gap — three postings — and is more naturally taught inside Module 009 by extending its existing alerting content. Treated as content-level reinforcement, not a curriculum-plan-delta module. If the runner wants a module-level proposal, see [`.aicg/curriculum-plan-delta.json`](.aicg/curriculum-plan-delta.json) — currently empty by design.

---

## 5. Where this curriculum already matches the market

Across the 32 postings, the level-10 stable-core stack (Python / Linux / Git / Docker / Kubernetes / one cloud / CI/CD / Prometheus / FastAPI / Postgres / MLflow / Airflow) covers >80% of explicit must-have requirements. The 10-module + 5-project structure aligns 1:1 with the most-cited skills, and every required level-10 requirement is currently covered.

The role hierarchy is also working as intended: every gap that *would* be additive at level 10 (LLM serving, GPU work, vector DBs, distributed Spark/Ray, GitOps, Slurm) is already covered at the role-appropriate higher level. Linking, not duplicating, is the right move.

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

- Sources: Indeed, Built In, ZipRecruiter, Glassdoor, LinkedIn, Greenhouse-hosted boards, Workday-hosted boards (Workday, BCBS, Astreya, NVIDIA, HPE, CMU, Lockheed), Breezy (Accrete), Workable (Quadric), Remoterocketship, Remotive, the speedyapply/2026-AI-College-Jobs curated new-grad list, Hacker News "Who is hiring" archives.
- Date window: Sept 2025 → July 2026 (skewed to last 90 days: 41/42 postings are dated 2026-04-01 or later; older outliers retained only when they listed concrete skills).
- 42 postings analyzed (specification asked for ≥25); 30 had retrievable full descriptions, the remaining 12 came from aggregated / paywalled listings where title/employer/level were confirmable but the full posting body was not always fully retrievable (Indeed, Glassdoor, some LinkedIn) — these are still counted because they confirm role *prevalence* and *level*, even when individual skills could not always be extracted.
- July 2026 refresh cycle added 10 postings (`p33`–`p42`) on top of the 32-posting June baseline. No requirement, evidence pattern, or ownership assignment changed as a result of the refresh; the curriculum-plan-delta v2 is intentionally empty per continuity bias.
- Ownership rule applied: a requirement appears at the lowest role where it is genuinely required. If a higher-level repo already owns a requirement (e.g. LLM serving at level 20), it is *linked*, not duplicated.

---

**Maintained by VeriSwarm.ai**
