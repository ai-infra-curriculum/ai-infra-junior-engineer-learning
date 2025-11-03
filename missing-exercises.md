# Missing Exercises Review (Updated)

Re-evaluated each junior module after the README refresh to determine whether ~8 hands-on exercises exist and whether they cover the lecture topics now advertised.

## mod-001-python-fundamentals
- **Lectures advertised:** 7 focused deep-dives, including "Decorators and Packaging" (`lessons/mod-001-python-fundamentals/README.md:90-98`).
- **Exercises present:** 7 (`lessons/mod-001-python-fundamentals/exercises/`).
- **Gap:** No lab addresses decorators, packaging, or publishing flows even though Lecture 05 now highlights packaging best practices; existing work stops at async and testing.
- **Suggested addition:** Packaging/release lab (wheel build, internal index publish, dependency management) to close the Lecture 05 gap.

## mod-002-linux-essentials
- **Lectures advertised:** Week 4 now emphasizes networking and advanced tooling (`lessons/mod-002-linux-essentials/README.md:52-70`).
- **Exercises present:** 8 practical labs (`lessons/mod-002-linux-essentials/exercises/`).
- **Gap:** None of the eight exercises target networking diagnostics (ip/ss), SSH security, or firewall tooling despite the new focus; coverage remains filesystem/process/scripting-heavy.
- **Suggested addition:** Dedicated Linux networking and troubleshooting exercise (interface config, firewall rules, latency triage).

## mod-003-git-version-control
- **Lectures advertised:** Fundamentals through advanced infrastructure workflows (`lessons/mod-003-git-version-control/README.md:63-174`).
- **Exercises present:** 8 covering repo setup, branching, collaboration, advanced history, ML/DVC, and Git LFS.
- **Gap:** Exercises map cleanly to the refreshed syllabus—no missing content identified.

## mod-004-ml-basics
- **Lectures advertised:** Five lectures, starting with "Machine Learning Overview for Infrastructure" (`lessons/mod-004-ml-basics/README.md:81-132`).
- **Exercises present:** 5 framework-specific inference labs.
- **Gap:** Nothing reinforces the introductory ML workflow/system design material; learners jump straight into PyTorch/TensorFlow/ONNX tasks.
- **Suggested addition:** Scenario-based exercise covering dataset prep, training vs inference trade-offs, and deployment planning to reflect Lecture 01.

## mod-005-docker-containers
- **Lectures advertised:** Extensive coverage from fundamentals to best practices (`lessons/mod-005-docker-containers/README.md`).
- **Exercises present:** 8 labs touching operations, image builds, Compose, networking, volumes, and production deployment.
- **Gap:** Coverage aligns with the updated module; no additional exercises required.

## mod-006-kubernetes-intro
- **Lectures advertised:** Architecture through ML workloads (`lessons/mod-006-kubernetes-intro/README.md:58-118`).
- **Exercises present:** 7 labs (deployments, Helm, debugging, storage, config, ingress, ML workloads).
- **Gap:** Still one short of the "~8" target; no hands-on material for topics like autoscaling or RBAC that often appear in introductory tracks.
- **Suggested addition:** Autoscaling or security/RBAC lab to round out the module.

## mod-007-apis-web-services
- **Lectures advertised:** HTTP fundamentals, FastAPI, auth/testing, deployment (`lessons/mod-007-apis-web-services/README.md:58-160`).
- **Exercises present:** 6 FastAPI-focused projects (`lessons/mod-007-apis-web-services/exercises/`).
- **Gap:** No exercises cover Flask fundamentals (`lessons/mod-007-apis-web-services/README.md:121-146`) or comprehensive API testing despite the expanded lecture content.
- **Suggested additions:**
  1. Flask vs FastAPI migration lab.
  2. Automated API testing/contract testing workshop.

## mod-008-databases-sql
- **Lectures advertised:** SQL fundamentals, advanced analytics, transactions, and a new NoSQL section (`lessons/mod-008-databases-sql/README.md:377-436`).
- **Exercises present:** 5 (CRUD, schema design, joins, ORM, indexing).
- **Gap:** No exercises on transactions/concurrency (`lessons/mod-008-databases-sql/README.md:377-386`) or NoSQL comparisons despite detailed lecture coverage.
- **Suggested additions:**
  1. Transaction isolation/concurrency scenario lab.
  2. NoSQL evaluation comparing document/key-value stores for ML.

## mod-009-monitoring-basics
- **Lectures advertised:** Expanded sections on distributed tracing, ML monitoring, and SLIs/SLOs (`lessons/mod-009-monitoring-basics/README.md:109-518`).
- **Exercises present:** 6 (observability stack, Prometheus install, dashboards, logging pipeline, alert runbook, Airflow monitoring).
- **Gap:** No dedicated practice for PromQL recording rules, tracing instrumentation, or SLO/error-budget design even though they now appear prominently.
- **Suggested additions:**
  1. PromQL and recording-rule lab with alert tuning.
  2. SLO/error-budget workshop covering incident triggers for ML services.

## mod-010-cloud-platforms
- **Lectures advertised:** Large AWS core plus new multi-cloud/FinOps sections (`lessons/mod-010-cloud-platforms/README.md:535-622`).
- **Exercises present:** 7 AWS-only labs (`lessons/mod-010-cloud-platforms/exercises/`).
- **Gap:** No exercises on GCP/Azure basics or multi-cloud strategy (Lecture 11) and no focused cloud cost optimization practice despite the expanded cost management section (`lessons/mod-010-cloud-platforms/README.md:535-543`).
- **Suggested additions:**
  1. Multi-cloud architecture comparison/decision exercise.
  2. FinOps lab (Cost Explorer, budgets, savings plan analysis).

## Summary
- Modules 003 and 005 already meet the 8-exercise alignment target.
- Modules 001, 006, 007, 008, 009, and 010 still need at least one additional exercise to hit "~8" and to cover new lecture scope.
- Modules 004, 007, 008, 009, and 010 show the largest gaps between the richer lecture outlines and currently available exercises.
