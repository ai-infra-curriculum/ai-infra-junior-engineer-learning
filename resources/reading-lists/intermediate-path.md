# Reading List — Intermediate Path

You finished the Junior Engineer curriculum. You can deploy a model behind an API, run it in Kubernetes, monitor it, and pipeline it with MLflow + Airflow + DVC. The next 6–12 months build deeper expertise and prepare you for an AI Infrastructure Engineer (Level 1) role.

This list is curated, not exhaustive. Read fewer things deeply rather than skimming everything. Build one substantial project per topic where indicated.

## Track 1 — Production ML Systems

You can build a pipeline. Now learn to operate one at scale.

### Books

- *Designing Machine Learning Systems* — Chip Huyen. The reference text for thinking about end-to-end ML in production. Read cover to cover.
- *Building Machine Learning Powered Applications* — Emmanuel Ameisen. Pairs well with the Huyen book; more product-oriented.
- *Reliable Machine Learning* — Pineau et al. (O'Reilly, 2022). Emphasis on operations: monitoring, reproducibility, incident response.

### Papers and Long-form

- "Hidden Technical Debt in Machine Learning Systems" — Sculley et al., NeurIPS 2015. Required reading.
- "The ML Test Score" — Breck et al., Google. A checklist that maps directly to operational maturity.
- "Continuous Delivery for Machine Learning" — Sato, Wider, Windheuser (martinfowler.com).

### Build

- Take one of your curriculum projects and add: shadow-model deployment, online A/B testing, canary releases, automated rollback on metric regression. Write up what broke.

---

## Track 2 — Distributed Systems

ML infrastructure is distributed systems with ML on top.

### Books

- *Designing Data-Intensive Applications* — Martin Kleppmann. Single most useful systems book on the market. Read the chapters on replication, partitioning, consistency, and stream processing first.
- *Database Internals* — Alex Petrov. Pairs with DDIA for storage-engine depth.

### Papers

- "MapReduce" (Dean & Ghemawat, 2004) — foundational; understand why it shaped everything after.
- "Bigtable" (Chang et al., 2006), "Dynamo" (DeCandia et al., 2007), "Spanner" (Corbett et al., 2012) — the canonical NoSQL papers.
- "Kafka: a Distributed Messaging System for Log Processing" (Kreps et al., 2011).

### Build

- Implement Raft or Paxos in a language you know. Toy version is fine. Then read someone else's implementation.

---

## Track 3 — Observability Beyond Dashboards

Module 009 introduced metrics, logs, and traces. Go deeper.

### Books

- *Observability Engineering* — Majors, Fong-Jones, Miranda (Honeycomb). Modern, opinionated.
- *Site Reliability Engineering* (Google SRE book). Read chapters on SLOs, error budgets, and toil.
- *The Site Reliability Workbook* — practical exercises.

### Practice

- Take a working service and instrument it end-to-end with **OpenTelemetry** — metrics, logs, and traces. Visualize the same request across all three.
- Define real SLOs for a real service. Compute error budget. Build a burn-rate alert.

---

## Track 4 — Kubernetes Internals

You can deploy to Kubernetes. Now learn how it actually works.

### Books

- *Kubernetes in Action* — Marko Lukša (2nd ed.). The right level of "under the hood."
- *Programming Kubernetes* — Hausenblas & Schimanski. For building operators and controllers.

### Practice

- Build a small **operator** with kubebuilder or Operator SDK. A "ModelDeployment" CRD that reconciles to a Deployment + Service + HPA + ServiceMonitor is a great starter.
- Read the etcd, kube-apiserver, and kubelet source for one specific subsystem (e.g., how scheduling picks a node). Don't read all of it.

---

## Track 5 — Cloud Architecture

Module 010 introduced one cloud. Pick a deeper specialization.

- **AWS** — *AWS Certified Solutions Architect Professional* exam guide. Even if you don't take the cert, the breadth helps.
- **GCP** — *Google Cloud Platform in Action* (Manning) + the Professional Cloud Architect cert path.
- **Azure** — *Azure for Architects* (Packt).

### Practice

- Build the **same** ML serving stack in two clouds. Document the trade-offs honestly.
- Read your team's IaC. If you can't get to that, read [AWS's open-source EKS Blueprints repo](https://github.com/aws-ia/terraform-aws-eks-blueprints).

---

## Track 6 — Performance Engineering

Latency and cost will define your seniority.

### Books

- *Systems Performance* — Brendan Gregg (2nd ed.). Required reading. Skim end-to-end, deep-dive on the chapters relevant to your stack.
- *BPF Performance Tools* — Brendan Gregg. For the day you need eBPF.

### Practice

- Profile a real model serving endpoint. Find the bottleneck (CPU? memory bandwidth? GC? deserialization?). Eliminate it. Document.
- Run a model on CPU, GPU, and a quantized version. Measure latency, throughput, cost-per-1000-predictions. Write up which deployment surface should host which model.

---

## Track 7 — Security for ML Infrastructure

Underrated. Hiring teams ask about it more every year.

### Books

- *Web Application Hacker's Handbook* — Stuttard & Pinto. Old, still relevant.
- *Threat Modeling: Designing for Security* — Adam Shostack.

### Topics

- Threat modeling an ML serving stack (data exfiltration, model theft, adversarial inputs).
- Secrets management at scale (Vault, AWS Secrets Manager, External Secrets Operator).
- Supply-chain attacks on ML pipelines (poisoned datasets, compromised model artifacts).
- Service-mesh authentication (mTLS via Istio or Linkerd).

### Practice

- Add Trivy and Grype scans to your CI. Sign images with cosign. Set up Kyverno or OPA to enforce signed-image-only policies.

---

## Track 8 — One ML Specialization

You're a generalist. Get strong in one ML area so you can speak the language with the ML team.

Pick one, not all:

### Recommendation Systems
- *Practical Recommender Systems* — Kim Falk.
- Build a two-tower retrieval + re-ranker on a public dataset (MovieLens, Goodbooks-10k).

### NLP / LLMs
- HuggingFace course (free, online).
- Build a RAG application end-to-end: ingest → embed → store → retrieve → re-rank → generate.

### Computer Vision
- *Deep Learning for Computer Vision* — Adrian Rosebrock; or PyImageSearch tutorials.
- Build a real-time detection service end-to-end: dataset → training → ONNX export → TensorRT optimization → gRPC service.

### Time Series / Forecasting
- *Forecasting: Principles and Practice* — Hyndman & Athanasopoulos (free online).
- Deploy a Prophet/NeuralProphet/Darts model with rolling re-training.

---

## How to Use This List

- **Three tracks max** for the next 6 months. Avoid skimming everything.
- **One build project per track.** Real systems break differently than tutorials.
- **Pair every book with code.** Solo reading without practice fades fast.
- **Find a study partner.** Explaining DDIA's chapter on consistency to someone else is how you learn it.
- **Track time honestly.** Two hours per weekday, three per weekend day → about 90 hours over 6 weeks for a single track.

Next stop: [Advanced Path](advanced-path.md) once you've completed at least three of these tracks with build projects.
