# Technology Versions - Junior Engineer Track

**Last Updated**: January 2025

This document specifies the recommended and tested versions for all technologies used in the AI Infrastructure Junior Engineer curriculum.

## Core Languages

| Technology | Version | Notes |
|------------|---------|-------|
| **Python** | 3.11+ | Recommended: 3.11 or 3.12. Minimum: 3.11 |
| **Bash** | 5.0+ | Standard on modern Linux/macOS |
| **SQL** | PostgreSQL 15+ | For database modules |

## Python Package Ecosystem

### Core ML Frameworks
| Package | Version | Purpose |
|---------|---------|---------|
| **PyTorch** | 2.1.0+ | Deep learning framework |
| **TensorFlow** | 2.15.0+ | Alternative ML framework |
| **scikit-learn** | 1.3.0+ | Traditional ML algorithms |
| **numpy** | 1.24.0+ | Numerical computing |
| **pandas** | 2.1.0+ | Data manipulation |

### ML Infrastructure
| Package | Version | Purpose |
|---------|---------|---------|
| **transformers** | 4.35.0+ | Hugging Face transformers (LLMs) |
| **onnx** | 1.15.0+ | Model format conversion |
| **onnxruntime** | 1.16.0+ | ONNX inference |

### Web & APIs
| Package | Version | Purpose |
|---------|---------|---------|
| **Flask** | 3.0.0+ | Web framework |
| **FastAPI** | 0.104.0+ | Modern async API framework |
| **requests** | 2.31.0+ | HTTP client |
| **uvicorn** | 0.24.0+ | ASGI server |

### Testing & Quality
| Package | Version | Purpose |
|---------|---------|---------|
| **pytest** | 7.4.0+ | Testing framework |
| **black** | 23.11.0+ | Code formatter |
| **ruff** | 0.1.6+ | Fast linter |
| **mypy** | 1.7.0+ | Type checker |

### Monitoring & Logging
| Package | Version | Purpose |
|---------|---------|---------|
| **prometheus-client** | 0.19.0+ | Prometheus metrics |
| **psutil** | 5.9.0+ | System monitoring |
| **structlog** | 23.2.0+ | Structured logging |

## Container Technologies

| Technology | Version | Notes |
|------------|---------|-------|
| **Docker** | 24.0+ | Container runtime |
| **Docker Compose** | 2.23+ | Multi-container orchestration |
| **containerd** | 1.7+ | Container runtime (alternative) |

### Base Images
| Image | Tag | Use Case |
|-------|-----|----------|
| `python` | 3.11-slim | Lightweight Python apps |
| `python` | 3.11 | Full Python environment |
| `nvidia/cuda` | 12.2.0-runtime-ubuntu22.04 | GPU-enabled containers |
| `pytorch/pytorch` | 2.1.0-cuda12.1-cudnn8-runtime | PyTorch with GPU |

## Kubernetes

| Technology | Version | Notes |
|------------|---------|-------|
| **Kubernetes** | 1.28+ | Orchestration platform |
| **kubectl** | 1.28+ | CLI tool (match cluster version) |
| **Minikube** | 1.32+ | Local development cluster |
| **Kind** | 0.20+ | Kubernetes in Docker |
| **Helm** | 3.13+ | Package manager |

### Kubernetes Add-ons
| Tool | Version | Purpose |
|------|---------|---------|
| **metrics-server** | 0.6+ | Resource metrics |
| **NVIDIA device plugin** | 0.14+ | GPU support |

## Cloud Platforms

### AWS
| Service/Tool | Version | Notes |
|--------------|---------|-------|
| **AWS CLI** | 2.15+ | Command-line interface |
| **boto3** | 1.34+ | Python SDK |
| **Amazon Linux 2023** | Latest | Recommended AMI |

### Popular AMIs
| AMI Type | ID Pattern | Use Case |
|----------|-----------|----------|
| Amazon Linux 2023 | `al2023-ami-*` | General compute |
| Ubuntu 22.04 LTS | `ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-*` | ML workloads |
| Deep Learning AMI | `Deep Learning AMI GPU PyTorch 2.*` | GPU training |

## Databases

| Technology | Version | Notes |
|------------|---------|-------|
| **PostgreSQL** | 15+ | Relational database |
| **Redis** | 7.2+ | Cache/in-memory store |
| **MongoDB** | 7.0+ | NoSQL document database |
| **SQLite** | 3.40+ | Embedded database |

## Monitoring Stack

| Technology | Version | Notes |
|------------|---------|-------|
| **Prometheus** | 2.48+ | Metrics collection |
| **Grafana** | 10.2+ | Visualization |
| **Alertmanager** | 0.26+ | Alert routing |
| **Node Exporter** | 1.7+ | System metrics |
| **cAdvisor** | 0.47+ | Container metrics |

### Logging
| Technology | Version | Notes |
|------------|---------|-------|
| **Elasticsearch** | 8.11+ | Log storage |
| **Logstash** | 8.11+ | Log processing |
| **Kibana** | 8.11+ | Log visualization |
| **Fluentd** | 1.16+ | Log collector |

## Infrastructure as Code

| Technology | Version | Notes |
|------------|---------|-------|
| **Terraform** | 1.6+ | IaC tool |
| **Ansible** | 2.16+ | Configuration management |

### Terraform Providers
| Provider | Version | Notes |
|----------|---------|-------|
| `hashicorp/aws` | ~> 5.0 | AWS provider |
| `hashicorp/random` | ~> 3.6 | Random resources |

## Version Control

| Technology | Version | Notes |
|------------|---------|-------|
| **Git** | 2.40+ | Version control |
| **GitHub CLI** | 2.40+ | GitHub operations |

## Workflow Orchestration

| Technology | Version | Notes |
|------------|---------|-------|
| **Apache Airflow** | 2.7+ | Workflow orchestration |

## Operating Systems

| OS | Version | Notes |
|-----|---------|-------|
| **Ubuntu** | 22.04 LTS | Recommended for production |
| **Amazon Linux** | 2023 | AWS-optimized |
| **macOS** | 13+ (Ventura) | Development |
| **Windows** | 11 + WSL2 | Windows development |

## CUDA & GPU

| Technology | Version | Notes |
|------------|---------|-------|
| **CUDA Toolkit** | 12.2+ | NVIDIA GPU programming |
| **cuDNN** | 8.9+ | Deep learning primitives |
| **NVIDIA Driver** | 535+ | GPU driver |
| **nvidia-docker** | 2.14+ | Docker GPU support |

## Development Tools

| Tool | Version | Notes |
|------|---------|-------|
| **VS Code** | 1.85+ | Recommended IDE |
| **JupyterLab** | 4.0+ | Interactive notebooks |
| **tmux** | 3.3+ | Terminal multiplexer |
| **vim/neovim** | 9.0+ / 0.9+ | Text editors |

## Version Policy

### Compatibility Promise

- **Backward Compatibility**: Exercises work with specified versions and newer
- **Testing**: All content tested with recommended versions
- **Updates**: Document updated quarterly (Jan, Apr, Jul, Oct)

### Version Selection Criteria

1. **Stability**: Prefer LTS or stable releases
2. **Security**: Use versions with active security support
3. **Community**: Choose widely-adopted versions
4. **Cloud Compatibility**: Match major cloud provider defaults

### Upgrade Strategy

- **Minor versions**: Upgrade when available (e.g., 3.11.1 → 3.11.2)
- **Major versions**: Test thoroughly before upgrading
- **Dependencies**: Pin in production, flexible in development

## Installation Quick Reference

### Python Environment Setup
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip

# macOS
brew install python@3.11

# Verify
python3 --version  # Should show 3.11.x or 3.12.x
```

### Docker Installation
```bash
# Ubuntu
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Verify
docker --version  # Should show 24.0+
docker compose version  # Should show 2.23+
```

### AWS CLI Installation
```bash
# Linux/macOS
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Verify
aws --version  # Should show 2.15+
```

### Kubernetes Tools
```bash
# kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install kubectl /usr/local/bin/

# Minikube
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# Verify
kubectl version --client
minikube version
```

### Terraform
```bash
# Using package manager
brew install terraform  # macOS
# OR
wget https://releases.hashicorp.com/terraform/1.6.0/terraform_1.6.0_linux_amd64.zip
unzip terraform_1.6.0_linux_amd64.zip
sudo mv terraform /usr/local/bin/

# Verify
terraform version
```

## Deprecated Versions

These versions are no longer supported in the curriculum:

| Technology | Deprecated Version | Reason | Migration Path |
|------------|-------------------|---------|----------------|
| Python | < 3.11 | EOL approaching | Upgrade to 3.11+ |
| TensorFlow | 1.x | Deprecated by Google | Upgrade to 2.15+ |
| Kubernetes | < 1.26 | Out of support | Upgrade to 1.28+ |
| Docker | < 20.10 | Security vulnerabilities | Upgrade to 24.0+ |

## Cloud Provider Managed Services

### AWS Managed Services (Alternative Versions)
| Service | Managed Version | Self-Managed Version |
|---------|----------------|----------------------|
| RDS PostgreSQL | 15.x | PostgreSQL 15+ |
| ElastiCache Redis | 7.x | Redis 7.2+ |
| EKS | 1.28 | Kubernetes 1.28+ |
| SageMaker | Managed | PyTorch 2.1.0+ |

## Breaking Changes & Migration Guides

### Python 3.11 → 3.12
- **Impact**: Minor
- **Changes**: Performance improvements, new syntax features
- **Action**: Test thoroughly, update type hints if needed

### TensorFlow 2.14 → 2.15
- **Impact**: Low
- **Changes**: Keras 3.0 integration
- **Action**: Review Keras code for compatibility

### Kubernetes 1.27 → 1.28
- **Impact**: Medium
- **Changes**: API deprecations
- **Action**: Update manifests, check for deprecated APIs

## Support Policy

| Version Type | Support Duration | Update Frequency |
|--------------|------------------|------------------|
| Major (e.g., Python 3.11 → 3.12) | 12 months notice | Annually |
| Minor (e.g., 3.11.1 → 3.11.2) | Immediate | As released |
| Security patches | Immediate | As released |

## Getting Help

- **Version Issues**: Check GitHub Issues for known problems
- **Compatibility**: Refer to official documentation
- **Updates**: Watch repository for VERSIONS.md updates

---

**Note**: This document is maintained by the curriculum team. For questions or version-specific issues, please open a GitHub issue.
