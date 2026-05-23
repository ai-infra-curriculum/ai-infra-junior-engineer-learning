# Reading List — Advanced Path

This is the senior / staff-track reading list. Most of it is research papers and source code, not books. The expectation is that you read with a notebook and write a synthesis after each item: what's the idea, what does it replace, what does it break.

You should reach this path after 2–3 years of production ML infrastructure work, or after completing the [Intermediate Path](intermediate-path.md) with build projects on at least four tracks.

## Track 1 — ML Systems at Scale

You understand single-service production ML. The advanced path is multi-tenant, multi-model platforms.

### Papers

- *TFX: A TensorFlow-Based Production-Scale Machine Learning Platform* — Baylor et al., KDD 2017. Google's view of an end-to-end platform.
- *Michelangelo* (Uber, 2017) and follow-up post-mortems — particularly the multi-tenant feature store work.
- *KubeFlow Pipelines* — read the source for the compiler and execution layer.
- *Triton Inference Server* design docs.
- *vLLM: Easy, Fast, and Cheap LLM Serving with PagedAttention* — Kwon et al.

### Build

- Design and implement a multi-tenant model serving layer that hosts 50+ models with shared CPU/GPU pools. Account for: model loading/eviction, fair scheduling, per-tenant rate limiting, isolation, blast-radius limits.

---

## Track 2 — Distributed Systems Deep Dive

### Books and Long Reads

- *Distributed Systems* — van Steen & Tanenbaum (free online).
- *Principles of Distributed Computing* — Lynch.
- "The Limits of CAP" — Brewer's revisited essay.

### Papers (canonical)

- "Paxos Made Simple" — Lamport.
- "In Search of an Understandable Consensus Algorithm (Raft)" — Ongaro & Ousterhout.
- "Chain Replication for Supporting High Throughput and Availability" — van Renesse & Schneider.
- "Calvin: Fast Distributed Transactions for Partitioned Database Systems" — Thomson et al.
- "Spanner: Becoming a SQL System" — follow-up after the original Spanner paper.

### Source code reading

Pick one and read deeply for two weeks:
- etcd's Raft implementation
- CockroachDB's distributed SQL layer
- TiKV / TiDB
- Cassandra's gossip and hinted handoff

---

## Track 3 — High-Performance ML Infrastructure

### Topics

- GPU memory hierarchy and how it shapes batching strategies.
- KV-cache management for transformer inference (PagedAttention, vLLM, TensorRT-LLM).
- Tensor and pipeline parallelism for training.
- Quantization: int8, int4, FP8, what each costs and what each gives back.
- Distillation, pruning, structured sparsity.
- Compilers: TVM, XLA, MLIR, ONNX runtime.
- Schedulers: Slurm, Volcano, Kueue.

### Build

- Take a production-relevant LLM (7B or 13B parameters), serve it three ways: HuggingFace + transformers, vLLM, TensorRT-LLM. Measure latency, throughput, and dollar-cost per million tokens. Identify the cliffs.

---

## Track 4 — Data Infrastructure

### Books

- *Streaming Systems* — Akidau, Chernyak, Lax (O'Reilly). Pairs with Flink/Spark Streaming docs.
- *The Enterprise Big Data Lake* — Alex Gorelik.

### Papers

- "MillWheel: Fault-Tolerant Stream Processing at Internet Scale" — Akidau et al.
- "The Dataflow Model" — Akidau et al.
- "Apache Iceberg: An Architectural Look Under the Covers" — Netflix tech blog series.
- "Delta Lake: High-Performance ACID Table Storage over Cloud Object Stores" — Armbrust et al.

### Build

- A real streaming feature pipeline: Kafka → Flink/Beam → online feature store. Backfill from a batch source. Measure end-to-end latency and exactly-once semantics.

---

## Track 5 — Reliability and Resilience

### Books and Papers

- *Site Reliability Engineering* — Google SRE book, full read this time.
- *Seeking SRE* — David Blank-Edelman (ed.).
- *The Site Reliability Workbook* — Google.
- "Failure Sketching: A Technique for Automated Root Cause Diagnosis of In-Production Failures" — Kasikci et al.

### Topics

- Chaos engineering: Netflix's Principles of Chaos, Chaos Mesh, Litmus.
- Capacity planning under uncertainty.
- Cost-aware autoscaling.
- Graceful degradation strategies for ML services (cached predictions, simpler model fallbacks).

### Build

- Run a Game Day on a production-like environment. Document the failure modes you didn't predict. Then add the missing observability for each.

---

## Track 6 — Security Architecture

### Books

- *Building Secure and Reliable Systems* — Google SRE/Security.
- *Threat Modeling: A Practical Guide for Development Teams* — Tarandach & Coles.

### Topics

- mTLS everywhere — service mesh integration deep dive.
- SBOM, supply-chain integrity, SLSA framework.
- Confidential computing for sensitive inference (TEEs, Intel SGX, AWS Nitro).
- ML-specific threats: model inversion, membership inference, adversarial examples, prompt injection in LLM serving.

### Build

- Threat-model an LLM-backed customer-facing application end-to-end. Implement at least three mitigations (input validation, output filtering, rate-limit budgets) and write the threat model up.

---

## Track 7 — Leadership and Cross-Functional Skills

The senior track requires more than depth.

### Books

- *Staff Engineer* — Will Larson.
- *The Manager's Path* — Camille Fournier (even if you're not managing).
- *An Elegant Puzzle* — Will Larson.
- *Engineering Management for the Rest of Us* — Sarah Drasner.
- *Accelerate* — Forsgren, Humble, Kim. The empirical case for high-performance engineering practices.

### Practice

- Write design documents that other senior engineers want to read. Read [Google's design doc anatomy](https://www.industrialempathy.com/posts/design-docs-at-google/).
- Run a multi-team postmortem. Sit through someone else's.
- Mentor someone earlier in their career. Teaching is how you find out what you don't actually know.

---

## Track 8 — Research Engineering

Optional but increasingly valuable. ML infrastructure work is converging with applied ML research.

### Reading habits

- Subscribe to **Papers With Code**, **NeurIPS / ICML / ICLR proceedings**, **arXiv-sanity-lite**.
- Pick one paper per week. Implement the core idea in a notebook. Write a one-page summary.

### Topics to track

- LLM serving optimizations (PagedAttention, speculative decoding, batched inference)
- Fine-tuning approaches (LoRA, QLoRA, DPO, ORPO)
- Retrieval (RAG, hybrid search, re-ranking)
- Evaluation (LMSys leaderboards, Eleuther's lm-evaluation-harness)
- Agent systems (ReAct, Toolformer, voyager-like architectures)

---

## How to Use This List

- This is a 2–5 year list. Pacing is the whole point.
- Maintain a research notebook. Quarterly: re-read it and ask "what is now obvious that wasn't a quarter ago?"
- Write publicly when you can. Blog posts and conference talks expose holes in your understanding faster than anything else.
- Build with a colleague when possible — the second perspective catches blind spots.
- Don't optimize for completing the list. Optimize for what your day job needs next.

After this path, the next move is usually domain specialization (a specific ML modality, a specific industry) or leadership (staff engineer, eng manager, founder).
