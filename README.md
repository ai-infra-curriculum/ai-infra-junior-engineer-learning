# Junior AI Infrastructure Engineer - Learning Repository

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub Issues](https://img.shields.io/github/issues/ai-infra-curriculum/ai-infra-junior-engineer-learning)](https://github.com/ai-infra-curriculum/ai-infra-junior-engineer-learning/issues)
[![Contributions Welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg)](CONTRIBUTING.md)

Welcome to the **Junior AI Infrastructure Engineer Learning Repository**! This comprehensive curriculum is designed to take you from beginner to job-ready in AI/ML infrastructure, with hands-on projects and industry-relevant skills.

## 🎯 Learning Objectives

By completing this curriculum, you will be able to:

- **Deploy ML models** via REST APIs with Flask/FastAPI
- **Containerize applications** using Docker
- **Orchestrate deployments** on Kubernetes
- **Build ML pipelines** with experiment tracking (MLflow)
- **Implement monitoring** with Prometheus and Grafana
- **Version datasets** with DVC
- **Automate workflows** using Airflow/Prefect
- **Deploy to cloud platforms** (AWS/GCP/Azure)
- **Implement CI/CD** for ML applications
- **Apply security best practices** for production systems

## 📚 Curriculum Overview

**Total Duration:** 440 hours (11 weeks full-time, 22 weeks part-time)
**Difficulty:** Beginner to Intermediate
**Prerequisites:** Basic Python programming, command-line familiarity

### Learning Modules (10 modules, ~150 hours)

| Module | Topic | Duration | Difficulty |
|--------|-------|----------|------------|
| **001** | Python Fundamentals for Infrastructure | 15 hours | Beginner |
| **002** | Linux Essentials | 15 hours | Beginner |
| **003** | Git & Version Control | 10 hours | Beginner |
| **004** | ML Basics (PyTorch/TensorFlow) | 20 hours | Beginner |
| **005** | Docker & Containerization | 15 hours | Beginner |
| **006** | Kubernetes Introduction | 20 hours | Beginner+ |
| **007** | APIs & Web Services | 15 hours | Beginner |
| **008** | Databases & SQL | 15 hours | Beginner |
| **009** | Monitoring & Logging Basics | 15 hours | Beginner+ |
| **010** | Cloud Platforms (AWS/GCP/Azure) | 20 hours | Beginner+ |

### Hands-On Projects (5 projects, ~290 hours)

| Project | Description | Duration | Technologies |
|---------|-------------|----------|--------------|
| **01** | [Simple Model API Deployment](projects/project-01-simple-model-api/) | 60 hours | Flask/FastAPI, Docker, AWS/GCP |
| **02** | [Kubernetes Model Serving](projects/project-02-kubernetes-serving/) | 80 hours | Kubernetes, Helm, Prometheus |
| **03** | [ML Pipeline with Experiment Tracking](projects/project-03-ml-pipeline-tracking/) | 100 hours | MLflow, Airflow, DVC |
| **04** | [Monitoring & Alerting System](projects/project-04-monitoring-alerting/) | 80 hours | Prometheus, Grafana, ELK Stack |
| **05** | [Production-Ready ML System (Capstone)](projects/project-05-production-ml-capstone/) | 120 hours | All above + CI/CD |

## 🚀 Getting Started

### Prerequisites

Before starting, ensure you have:

- **Python 3.11+** installed
- **Docker Desktop** or Docker Engine
- **Git** for version control
- **Code editor** (VS Code, PyCharm, etc.)
- **Cloud account** (free tier): AWS, GCP, or Azure
- **Basic command-line skills**

### Setup Instructions

1. **Clone this repository:**
   ```bash
   git clone https://github.com/ai-infra-curriculum/ai-infra-junior-engineer-learning.git
   cd ai-infra-junior-engineer-learning
   ```

2. **Set up Python environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Install Docker:**
   - Follow instructions at [docs.docker.com](https://docs.docker.com/get-docker/)
   - Verify: `docker --version`

4. **Choose your learning path:**
   - **Beginner:** Start with Module 001
   - **Some experience:** Review modules 001-003, start Module 004
   - **Ready for projects:** Jump to Project 01

### Recommended Learning Path

```
Week 1-2:  Modules 001-003 (Python, Linux, Git)
Week 3-4:  Modules 004-005 (ML Basics, Docker)
Week 5:    Module 006 (Kubernetes) + Project 01
Week 6-7:  Project 01 (Simple Model API)
Week 8:    Module 007-008 (APIs, Databases) + Project 02
Week 9-10: Project 02 (Kubernetes Serving)
Week 11:   Module 009-010 (Monitoring, Cloud)
Week 12-14: Project 03 (ML Pipeline)
Week 15-16: Project 04 (Monitoring)
Week 17-20: Project 05 (Capstone)
Week 21-22: Portfolio polish, job applications
```

## 📖 Repository Structure

```
ai-infra-junior-engineer-learning/
├── README.md                    # This file
├── CURRICULUM.md                # Detailed curriculum guide
├── CODE_OF_CONDUCT.md          # Community guidelines
├── CONTRIBUTING.md             # How to contribute
├── LICENSE                     # MIT License
├── requirements.txt            # Python dependencies
├── .github/                    # GitHub templates & workflows
│   ├── workflows/              # CI/CD automation
│   └── ISSUE_TEMPLATE/         # Issue templates
├── lessons/                    # Learning modules
│   ├── mod-001-python-fundamentals/
│   │   ├── README.md           # Module overview
│   │   ├── lecture-notes/      # Lecture content
│   │   ├── exercises/          # Hands-on practice
│   │   ├── quizzes/            # Knowledge checks
│   │   └── resources/          # Additional materials
│   ├── mod-002-linux-essentials/
│   └── ...                     # More modules
├── projects/                   # Hands-on projects
│   ├── project-01-simple-model-api/
│   │   ├── README.md           # Project guide
│   │   ├── requirements.md     # Requirements spec
│   │   ├── src/                # Code stubs
│   │   ├── tests/              # Test stubs
│   │   ├── docs/               # Documentation templates
│   │   └── docker/             # Docker configs
│   └── ...                     # More projects
├── assessments/                # Quizzes & exams
│   ├── quizzes/                # Module quizzes
│   ├── practical-exams/        # Hands-on assessments
│   └── rubrics/                # Grading criteria
├── resources/                  # Additional resources
│   ├── cheat-sheets/           # Quick references
│   ├── reading-lists/          # Recommended reading
│   └── tools.md                # Tool recommendations
├── progress/                   # Track your learning
│   ├── overall-progress.md     # Overall tracker
│   ├── module-progress.md      # Module checklist
│   └── project-progress.md     # Project tracker
└── community/                  # Community resources
    ├── FAQ.md                  # Frequently asked questions
    └── study-groups.md         # Study group info
```

## 🎓 Assessment & Certification

### Assessment Structure

Each project includes:
- **100-point rubric** with clear criteria
- **Passing score:** 70 points
- **Excellence:** 90+ points
- **Self-assessment checklists**
- **Peer review guidelines**

### Grading Breakdown

- **Code Quality** (25%): Clean, maintainable, well-documented code
- **Functionality** (30%): Meets all requirements, works as expected
- **Infrastructure** (20%): Proper deployment, scalability, reliability
- **Documentation** (15%): Clear README, API docs, deployment guides
- **Performance** (10%): Meets performance benchmarks

### Portfolio Building

Each project is designed to be **portfolio-worthy**:
- Professional README files
- Live demos (where possible)
- Architecture diagrams
- Performance metrics
- GitHub Actions CI/CD

**Showcase your capstone project** (Project 05) to potential employers!

## 🛠️ Technology Stack

### Core Technologies

- **Languages:** Python 3.11+, Bash, YAML
- **ML Frameworks:** PyTorch 2.0+, TensorFlow 2.13+, Scikit-learn 1.3+
- **Container & Orchestration:** Docker 24.0+, Kubernetes 1.28+, Helm 3.12+
- **MLOps:** MLflow 2.8+, DVC 3.30+, Airflow 2.7+ / Prefect 2.13+
- **Monitoring:** Prometheus 2.47+, Grafana 10.2+, ELK Stack 8.11+
- **Cloud:** AWS / GCP / Azure (choose one)
- **Databases:** PostgreSQL 15+, Redis 7+
- **CI/CD:** GitHub Actions, GitLab CI

### Development Tools

- **IDE:** VS Code, PyCharm, or similar
- **Version Control:** Git, GitHub
- **API Testing:** Postman, cURL, httpie
- **Container Management:** Docker Desktop, Minikube, Kind
- **Cloud CLI:** aws-cli, gcloud, az

## 💼 Career Outcomes

### What You'll Be Able to Do

After completing this curriculum, you'll be qualified for:

- **Junior ML Infrastructure Engineer**
- **Junior MLOps Engineer**
- **DevOps Engineer (ML focus)**
- **Cloud Infrastructure Engineer (entry-level)**
- **ML Platform Engineer (junior)**

### Expected Salary Range (US, 2025)

- **Entry-level:** $67,000 - $95,000
- **With 1-2 years exp:** $80,000 - $110,000
- **Geographic variation:** Higher in tech hubs (SF, NYC, Seattle)

### Skills You'll Master

**Technical:**
- ML model deployment and serving
- Container orchestration (Docker, Kubernetes)
- Infrastructure as Code (Terraform basics)
- CI/CD pipeline development
- Monitoring and observability
- Cloud platform management
- Data pipeline development

**Professional:**
- Problem-solving
- Technical documentation
- Code review
- Agile methodologies
- Collaboration and communication

## 📝 How to Use This Repository

### For Self-Learners

1. **Start with Module 001** and progress sequentially
2. **Complete all exercises** in each module
3. **Build each project** following the requirements
4. **Self-assess** using the provided rubrics
5. **Share your work** on GitHub for portfolio building
6. **Join the community** for support and networking

### For Instructors

This repository provides:
- **Ready-to-use curriculum** for a semester-long course
- **Comprehensive lecture materials** with exercises
- **Hands-on projects** with detailed specifications
- **Assessment rubrics** for grading
- **Scaffolded learning** from beginner to intermediate

**Suggested course structure:** 16-week semester, 10 hours/week

### For Study Groups

- Use the **discussion forums** for collaboration
- Schedule **weekly meetups** to review modules
- **Pair program** on projects
- **Peer review** each other's code
- Share resources and tips

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

**Ways to contribute:**
- Report bugs or issues
- Suggest improvements
- Add exercises or resources
- Share your project solutions (in discussions)
- Improve documentation
- Create tutorial videos

## 📞 Support & Community

### Getting Help

- **GitHub Discussions:** Ask questions, share insights
- **GitHub Issues:** Report bugs or content issues
- **FAQ:** See [community/FAQ.md](community/FAQ.md)
- **Email:** ai-infra-curriculum@joshua-ferguson.com

### Community Resources

- **Study Groups:** Join or create study groups
- **Office Hours:** Weekly virtual office hours (TBD)
- **Discord Server:** Join our Discord for real-time chat (link TBD)
- **LinkedIn Group:** Network with fellow learners (link TBD)

## 📜 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Contributors:** Thank you to all contributors!
- **Reviewers:** Industry experts who validated this curriculum
- **Open Source Community:** For the amazing tools we build upon
- **Students:** Your feedback makes this curriculum better

## 🔗 Related Resources

### Other Curriculum Levels

- **Next Level:** [AI Infrastructure Engineer](https://github.com/ai-infra-curriculum/ai-infra-engineer-learning)
- **Specialized Tracks:**
  - [ML Platform Engineer](https://github.com/ai-infra-curriculum/ai-infra-ml-platform-learning)
  - [MLOps Engineer](https://github.com/ai-infra-curriculum/ai-infra-mlops-learning)
  - [Security Engineer](https://github.com/ai-infra-curriculum/ai-infra-security-learning)
  - [Performance Engineer](https://github.com/ai-infra-curriculum/ai-infra-performance-learning)
- **Architecture Track:** [AI Infrastructure Architect](https://github.com/ai-infra-curriculum/ai-infra-architect-learning)
- **Leadership Track:** [Team Lead / Manager](https://github.com/ai-infra-curriculum/ai-infra-team-lead-learning)

### Solutions Repository

Looking for complete solutions and step-by-step guides?
👉 **[Junior AI Infrastructure Engineer - Solutions](https://github.com/ai-infra-curriculum/ai-infra-junior-engineer-solutions)**

**Note:** We recommend attempting projects on your own before reviewing solutions!

---

**Ready to start your AI Infrastructure career?** 🚀
Begin with [Module 001: Python Fundamentals](lessons/mod-001-python-fundamentals/)

**Questions?** Open an issue or join our community discussions!

**Last Updated:** October 2025
**Version:** 1.0.0
**Maintained by:** AI Infrastructure Curriculum Team
