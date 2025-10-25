# Project 03: ML Pipeline with Experiment Tracking

**Role:** Junior AI Infrastructure Engineer (Level 0)
**Duration:** 100 hours (2-3 weeks full-time, 4-5 weeks part-time)
**Complexity:** Intermediate
**Prerequisites:** Projects 1-2 (API Deployment, Kubernetes Serving)

---

## Project Overview

Build an end-to-end machine learning pipeline with automated experiment tracking, data versioning, model registry, and workflow orchestration. This project introduces MLOps fundamentals: managing the complete ML lifecycle from data ingestion to model deployment.

### What You'll Build

In this project, you will construct a production-grade ML pipeline that:

- **Automates the entire ML workflow** from raw data to deployed models
- **Tracks every experiment** with complete reproducibility using MLflow
- **Versions all data and models** with DVC (Data Version Control)
- **Orchestrates complex workflows** using Apache Airflow
- **Validates data quality** with Great Expectations
- **Manages model lifecycle** through MLflow Model Registry
- **Provides experiment analysis** through interactive dashboards

### Real-World Context

After successfully deploying models (Projects 1-2), data science teams face a new challenge: managing dozens of experiments, tracking which dataset versions produce the best models, and automating retraining workflows. Without proper MLOps infrastructure, teams struggle with:

- **Lost experiments** - "Which hyperparameters produced that 92% accuracy model?"
- **Data inconsistency** - "Did we train on version 1.2 or 1.3 of the dataset?"
- **Manual processes** - "Someone needs to retrain the model weekly"
- **No reproducibility** - "I can't recreate last month's results"

This project simulates building internal ML platform capabilities that solve these problems at scale.

### Learning Objectives

By completing this project, you will:

1. **Design and implement ML pipelines** using workflow orchestration tools (Airflow)
2. **Track experiments systematically** with MLflow (metrics, parameters, artifacts)
3. **Version datasets and models** using DVC (Data Version Control)
4. **Build a model registry** for model lifecycle management
5. **Automate model retraining** with scheduled pipelines
6. **Create comparison dashboards** for experiment analysis
7. **Implement data validation** and pipeline monitoring
8. **Apply MLOps best practices** for reproducibility and governance

---

## Technology Stack

### Core Technologies

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Orchestration** | Apache Airflow 2.7+ | Workflow management and scheduling |
| **Experiment Tracking** | MLflow 2.8+ | Tracking runs, models, artifacts |
| **Data Versioning** | DVC 3.30+ | Dataset version control |
| **Data Validation** | Great Expectations 0.18+ | Data quality checks |
| **ML Framework** | PyTorch 2.0+ | Model training |
| **Database** | PostgreSQL 15+ | MLflow backend, feature store |
| **Object Storage** | MinIO (local) | Artifact storage |
| **Message Queue** | Redis 7+ | Airflow task queue |

### Why These Technologies?

- **Apache Airflow**: Industry standard for workflow orchestration (used by Airbnb, Netflix, Adobe)
- **MLflow**: Most popular open-source MLOps platform with 15K+ GitHub stars
- **DVC**: Git-like versioning for data and models, integrates seamlessly with existing workflows
- **Great Expectations**: Prevents bad data from entering pipelines with automated validation
- **PostgreSQL**: Reliable, scalable database for metadata and features
- **MinIO**: S3-compatible object storage for local development

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    ML Pipeline Architecture                 │
└─────────────────────────────────────────────────────────────┘

┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Data        │     │  PostgreSQL  │     │  MinIO/S3    │
│  Sources     │────▶│  Feature     │     │  Artifact    │
│  (CSV/API)   │     │  Store       │     │  Storage     │
└──────────────┘     └──────────────┘     └──────────────┘
       │                     │                     │
       │                     │                     │
       ▼                     ▼                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    Airflow/Prefect                          │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  DAG: ML Training Pipeline                           │   │
│  │                                                       │   │
│  │  [Data Ingestion] → [Data Validation] → [Preprocessing]│
│  │         │                                             │   │
│  │         ▼                                             │   │
│  │  [Feature Engineering] → [Train Model] → [Evaluate]  │   │
│  │         │                      │              │       │   │
│  │         ▼                      ▼              ▼       │   │
│  │  [DVC Commit]         [MLflow Track]  [Model Register]│  │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
                   ┌────────────────┐
                   │  MLflow        │
                   │  - Tracking    │
                   │  - Registry    │
                   │  - UI          │
                   └────────────────┘
```

### Data Flow

```
Raw Data (CSV/API)
       │
       ▼
Data Validation (Great Expectations)
       │
       ▼
Preprocessing (Clean, Transform)
       │
       ▼
Feature Store (PostgreSQL) ◄──── DVC (Versioning)
       │
       ▼
Model Training (PyTorch) ◄──── MLflow (Tracking)
       │
       ▼
Model Evaluation (Metrics)
       │
       ▼
Model Registry (Versioned) ◄──── MLflow Registry
```

---

## Project Structure

```
project-03-ml-pipeline-tracking/
├── README.md                           # This file
├── requirements.md                     # Detailed requirements
├── architecture.md                     # Architecture deep dive
├── docker-compose.yml                  # Multi-service orchestration
├── .env.example                        # Environment configuration
├── src/
│   ├── data_ingestion.py              # Data ingestion module (STUB)
│   ├── preprocessing.py               # Data preprocessing (STUB)
│   ├── training.py                    # Model training with MLflow (STUB)
│   └── evaluation.py                  # Model evaluation (STUB)
├── dags/
│   └── ml_pipeline_dag.py             # Airflow DAG (STUB)
├── mlflow/
│   └── MLproject                      # MLflow project configuration
├── dvc/
│   ├── data.dvc                       # DVC data versioning
│   └── .dvcignore                     # DVC ignore patterns
├── tests/
│   └── test_pipeline.py               # Pipeline tests (STUB)
└── docs/
    ├── SETUP.md                        # Setup instructions
    ├── MLFLOW_GUIDE.md                 # MLflow usage guide
    └── DVC_WORKFLOW.md                 # DVC workflow guide
```

---

## Getting Started

### Prerequisites

Before starting this project, ensure you have:

- Completed Projects 1 and 2 (API Deployment, Kubernetes basics)
- Docker and Docker Compose installed
- Python 3.11+ installed
- Git installed
- Basic understanding of:
  - Machine learning concepts (training, validation, testing)
  - SQL and databases
  - Workflow automation concepts

### Quick Start

1. **Navigate to project directory:**
   ```bash
   cd projects/project-03-ml-pipeline-tracking/
   ```

2. **Set up environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Start infrastructure with Docker Compose:**
   ```bash
   docker-compose up -d
   ```

5. **Verify services:**
   - MLflow UI: http://localhost:5000
   - Airflow UI: http://localhost:8080
   - MinIO Console: http://localhost:9001

6. **Read the detailed requirements:**
   ```bash
   cat requirements.md
   ```

7. **Follow the implementation guide in architecture.md**

---

## Learning Path

### Phase 1: Environment Setup (15 hours)
- Set up Docker Compose infrastructure
- Configure MLflow tracking server
- Initialize DVC for data versioning
- Install all dependencies

**Deliverable:** All services running and accessible

### Phase 2: Data Pipeline (25 hours)
- Implement data ingestion from multiple sources
- Add data validation with Great Expectations
- Build preprocessing pipeline
- Version data with DVC

**Deliverable:** Complete data pipeline with validation

### Phase 3: MLflow Integration (20 hours)
- Set up MLflow experiment tracking
- Implement model training with tracking
- Log parameters, metrics, and artifacts
- Build model registry

**Deliverable:** Multiple tracked experiments in MLflow

### Phase 4: Workflow Orchestration (30 hours)
- Design Airflow DAG structure
- Implement pipeline tasks
- Configure scheduling and error handling
- Test end-to-end pipeline

**Deliverable:** Automated pipeline running on schedule

### Phase 5: Analysis & Documentation (10 hours)
- Create experiment comparison notebooks
- Write comprehensive documentation
- Build experiment analysis dashboard
- Prepare demo materials

**Deliverable:** Complete documentation and analysis tools

---

## Key Concepts

### MLOps Fundamentals

**What is MLOps?**
MLOps (Machine Learning Operations) applies DevOps principles to ML workflows, ensuring models are:
- **Reproducible** - Same code and data produces same results
- **Automated** - Manual steps are eliminated
- **Monitored** - Performance is continuously tracked
- **Versioned** - All artifacts are version controlled

**Why MLOps Matters:**
- **Development speed**: Experiment 10x faster with automated tracking
- **Collaboration**: Teams can share experiments and reproduce results
- **Production readiness**: Models transition smoothly from research to production
- **Governance**: Complete audit trail of all experiments

### Experiment Tracking

**What to Track:**
- **Parameters**: Hyperparameters (learning rate, batch size, model architecture)
- **Metrics**: Performance metrics (accuracy, loss, F1 score)
- **Artifacts**: Model files, plots, datasets, logs
- **Code version**: Git commit hash for reproducibility
- **Environment**: Dependencies and hardware specs

**Benefits:**
- Never lose a good experiment
- Compare models systematically
- Share results with team members
- Reproduce results months later

### Data Versioning

**Why Version Data:**
- Data changes over time
- Need to recreate old experiments
- Track data lineage
- Collaborate on datasets

**DVC Workflow:**
```bash
# Track dataset
dvc add data/raw/dataset.csv

# Commit to Git
git add data/raw/dataset.csv.dvc
git commit -m "Add dataset version 1.0"

# Push to remote storage
dvc push

# Later: retrieve exact dataset
dvc pull
```

### Workflow Orchestration

**Why Use Airflow:**
- **Dependencies**: Tasks run in correct order
- **Scheduling**: Automatic execution (daily, weekly)
- **Monitoring**: Track task success/failure
- **Retries**: Automatic retry on failure
- **Scalability**: Distribute tasks across workers

**DAG (Directed Acyclic Graph):**
```python
# Define task dependencies
ingest_data >> validate_data >> preprocess_data
preprocess_data >> train_model >> evaluate_model
evaluate_model >> register_model
```

---

## Success Criteria

### Minimum Requirements

- [ ] All infrastructure services running (MLflow, Airflow, PostgreSQL, MinIO)
- [ ] Data pipeline ingests, validates, and preprocesses data
- [ ] At least 5 experiments tracked in MLflow
- [ ] Models logged with complete metadata (params, metrics, artifacts)
- [ ] Airflow DAG runs successfully end-to-end
- [ ] Data versioned with DVC
- [ ] Model registry contains multiple versions
- [ ] Pipeline scheduled and runs automatically
- [ ] Documentation complete and clear

### Excellence Criteria

- [ ] 10+ experiments with systematic hyperparameter search
- [ ] Comprehensive data validation with Great Expectations
- [ ] Advanced experiment analysis notebooks
- [ ] Custom MLflow visualizations
- [ ] Pipeline monitoring and alerting
- [ ] Production-ready error handling
- [ ] Complete test coverage
- [ ] Professional documentation with diagrams

---

## Common Challenges & Solutions

### Challenge 1: Service Dependencies
**Problem:** Airflow tries to connect before PostgreSQL is ready
**Solution:** Use Docker health checks and `depends_on` with conditions

### Challenge 2: Experiment Clutter
**Problem:** Too many experiments, hard to find relevant ones
**Solution:** Use meaningful tags and naming conventions

### Challenge 3: Data Too Large
**Problem:** Git can't handle large datasets
**Solution:** Always use DVC for data, never commit data to Git

### Challenge 4: MLflow Artifacts Not Saving
**Problem:** Artifacts disappear after runs
**Solution:** Verify artifact store configuration (S3/MinIO endpoint)

### Challenge 5: Airflow DAG Not Updating
**Problem:** Code changes don't appear in Airflow UI
**Solution:** Check DAG folder mount and Airflow refresh interval

---

## Resources

### Official Documentation
- [MLflow Documentation](https://mlflow.org/docs/latest/index.html)
- [Apache Airflow Documentation](https://airflow.apache.org/docs/)
- [DVC Documentation](https://dvc.org/doc)
- [Great Expectations Documentation](https://docs.greatexpectations.io/)

### Tutorials
- [MLflow Quickstart](https://mlflow.org/docs/latest/tutorials-and-examples/tutorial.html)
- [Airflow Tutorial](https://airflow.apache.org/docs/apache-airflow/stable/tutorial.html)
- [DVC Get Started](https://dvc.org/doc/start)

### Community
- [MLflow Discord](https://mlflow.org/community)
- [Airflow Slack](https://apache-airflow-slack.herokuapp.com/)
- [DVC Community](https://dvc.org/community)

---

## Next Steps

After completing this project:

1. **Move to Project 4**: Monitoring and Alerting System
2. **Extend this project** with:
   - Model drift detection
   - A/B testing framework
   - Feature store (Feast)
   - AutoML integration
3. **Portfolio**: Add this to your portfolio with demo video
4. **Blog**: Write about building production ML pipelines
5. **Interview prep**: Discuss MLOps architecture in interviews

---

## Assessment

Your work will be evaluated on:

- **Functionality (40%)**: Does the pipeline work end-to-end?
- **MLOps Practices (30%)**: Proper tracking, versioning, automation?
- **Code Quality (15%)**: Clean, well-organized, tested code?
- **Documentation (15%)**: Clear, comprehensive documentation?

**Passing Score:** 70/100
**Target for Excellence:** 85/100

---

## Support

### Getting Help

1. **Check documentation** in `docs/` folder
2. **Review code stubs** for TODO comments and guidance
3. **Search issues** in project repository
4. **Ask questions** in community forums
5. **Read error logs** carefully - they often point to the solution

### Common Error Messages

See `docs/TROUBLESHOOTING.md` for solutions to common issues.

---

**Project Version:** 1.0
**Last Updated:** October 18, 2025
**Maintained By:** AI Infrastructure Curriculum Team

**Ready to start?** Open `requirements.md` for detailed specifications!
