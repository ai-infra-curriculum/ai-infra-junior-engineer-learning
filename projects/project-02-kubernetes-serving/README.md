# Project 02: Kubernetes Model Serving

**Duration:** 80 hours (2 weeks full-time, 3-4 weeks part-time)
**Complexity:** Beginner+
**Prerequisites:** Project 01 (Simple Model API Deployment)

---

## Overview

Transform your basic Flask/FastAPI model serving application from Project 01 into a production-grade, scalable Kubernetes deployment. This project teaches container orchestration fundamentals, auto-scaling, load balancing, rolling updates, and comprehensive monitoring using industry-standard tools.

### Real-World Scenario

Your simple model API from Project 01 was a success! The business now requires:
- **High availability**: 99.9% uptime guarantee
- **Scalability**: Handle 1000+ requests per second during peak hours
- **Zero-downtime deployments**: Updates without service interruption
- **Observability**: Real-time metrics and alerting

Enter Kubernetes - the de facto standard for container orchestration that solves all these challenges.

---

## Learning Objectives

By completing this project, you will be able to:

1. **Deploy containerized applications to Kubernetes** using Deployments, Services, and ConfigMaps
2. **Implement auto-scaling** with Horizontal Pod Autoscaler (HPA) based on CPU and memory metrics
3. **Configure load balancing** using Kubernetes Services and Ingress controllers
4. **Perform rolling updates** with zero downtime and automatic rollback capabilities
5. **Set up monitoring infrastructure** with Prometheus and Grafana
6. **Package applications with Helm** for repeatable, configurable deployments
7. **Implement health checks** using liveness and readiness probes
8. **Manage application configuration** with ConfigMaps and Secrets
9. **Debug Kubernetes deployments** using kubectl, logs, and monitoring tools
10. **Optimize resource allocation** with requests and limits

---

## Architecture Overview

### High-Level Architecture

```
                    Internet
                       │
                       ▼
              ┌─────────────────┐
              │  LoadBalancer   │ ← External IP
              │    Service      │
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │     Ingress     │ ← NGINX Controller
              │  /predict       │
              │  /health        │
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │  ClusterIP      │ ← Internal Load Balancer
              │   Service       │
              └─────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
   ┌────────┐     ┌────────┐     ┌────────┐
   │ Pod 1  │     │ Pod 2  │     │ Pod 3  │
   │ API v1 │     │ API v1 │     │ API v1 │
   └────────┘     └────────┘     └────────┘
        │              │              │
        └──────────────┴──────────────┘
                       │
                       ▼
              ┌─────────────────┐
              │      HPA        │ ← Auto-scaler
              │  Min: 3         │
              │  Max: 10        │
              │  Target: 70% CPU│
              └─────────────────┘
```

### Monitoring Architecture

```
┌─────────────────────────────────────┐
│           Prometheus                │
│  ┌─────────────────────────────┐   │
│  │ Scrapes metrics from:       │   │
│  │ • Pods (via /metrics)       │   │
│  │ • Kubernetes API            │   │
│  │ • Node exporter             │   │
│  └─────────────────────────────┘   │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│            Grafana                  │
│  ┌─────────────────────────────┐   │
│  │ Dashboards:                 │   │
│  │ • Pod count & health        │   │
│  │ • CPU/Memory usage          │   │
│  │ • Request rate & latency    │   │
│  │ • Error rates               │   │
│  └─────────────────────────────┘   │
└─────────────────────────────────────┘
```

---

## Technology Stack

### Core Technologies

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Orchestration** | Kubernetes 1.28+ | Container orchestration and scheduling |
| **Local Cluster** | Minikube / Kind | Local development and testing |
| **Cloud Platform** | EKS / GKE / AKS | Production Kubernetes cluster |
| **Package Manager** | Helm 3.12+ | Application templating and deployment |
| **Monitoring** | Prometheus + Grafana | Metrics collection and visualization |
| **Ingress** | NGINX Ingress Controller | HTTP routing and load balancing |
| **CLI Tools** | kubectl, helm | Cluster management |

### Recommended Tools

- **K9s** - Terminal UI for Kubernetes cluster management
- **Lens** - Kubernetes IDE with visual cluster exploration
- **kubectx/kubens** - Quick context and namespace switching
- **stern** - Multi-pod log tailing
- **k6** - Load testing tool

---

## Project Structure

```
project-02-kubernetes-serving/
├── README.md                          # This file
├── requirements.md                    # Detailed requirements
├── architecture.md                    # Architecture documentation
├── .env.example                       # Environment configuration template
│
├── src/
│   ├── app.py                        # Enhanced API from Project 01 (STUB)
│   ├── model.py                      # Model loading logic (STUB)
│   ├── metrics.py                    # Prometheus metrics (STUB)
│   └── requirements.txt              # Python dependencies
│
├── kubernetes/
│   ├── deployment.yaml               # K8s Deployment manifest (STUB)
│   ├── service.yaml                  # K8s Service manifest (STUB)
│   ├── ingress.yaml                  # Ingress configuration (STUB)
│   ├── hpa.yaml                      # Horizontal Pod Autoscaler (STUB)
│   ├── configmap.yaml                # Application configuration (STUB)
│   └── secrets.yaml.example          # Secrets template
│
├── monitoring/
│   ├── servicemonitor.yaml           # Prometheus ServiceMonitor (STUB)
│   └── grafana-dashboard.json        # Grafana dashboard template
│
├── tests/
│   ├── test_k8s.py                   # Kubernetes deployment tests (STUB)
│   ├── test_api.py                   # API integration tests (STUB)
│   └── load-test.js                  # K6 load test script (STUB)
│
└── docs/
    ├── SETUP.md                      # Setup instructions
    ├── OPERATIONS.md                 # Operational runbook
    └── TROUBLESHOOTING.md            # Common issues and solutions
```

---

## Requirements

### Functional Requirements

#### FR-1: Kubernetes Deployment
- Deploy model API as Kubernetes Deployment with 3 replicas
- Configure resource requests (CPU: 500m, Memory: 1Gi) and limits (CPU: 1000m, Memory: 2Gi)
- Implement liveness probe checking `/health` endpoint
- Implement readiness probe ensuring model is loaded before traffic
- Use ConfigMap for application configuration (model name, log level)

#### FR-2: Service & Load Balancing
- Create ClusterIP Service for internal access
- Create LoadBalancer Service for external access
- Implement Ingress for HTTP routing with path-based routing
- Verify load distribution across all pods

#### FR-3: Auto-Scaling
- Configure HPA to scale from 3 to 10 pods
- Set target CPU utilization at 70%
- Define scale-up and scale-down policies
- Test auto-scaling under load

#### FR-4: Rolling Updates
- Implement RollingUpdate strategy
- Configure maxSurge=1 and maxUnavailable=0 for zero-downtime
- Test update from v1.0 to v1.1
- Implement rollback capability

#### FR-5: Monitoring & Observability
- Deploy Prometheus for metrics collection
- Deploy Grafana for visualization
- Create dashboard showing pod count, CPU, memory, request rate
- Configure alerts for high error rates or pod failures

### Non-Functional Requirements

#### NFR-1: Performance
- Support 1000+ requests/second across cluster
- P99 latency < 500ms under load
- Auto-scaling responds within 2 minutes

#### NFR-2: Reliability
- 99.9% uptime (< 43 minutes downtime/month)
- Zero downtime during deployments
- Automatic pod recovery within 30 seconds

#### NFR-3: Scalability
- Support 3-10 pod replicas
- Handle 10x traffic spikes gracefully
- Resource-efficient scaling

#### NFR-4: Security
- Secrets stored in Kubernetes Secrets (not ConfigMaps)
- Pod Security Standards applied
- Network policies restricting pod communication
- RBAC configured for least-privilege access

---

## Getting Started

### Prerequisites

Before starting this project, ensure you have:

1. **Completed Project 01**: Understanding of Flask/FastAPI model serving
2. **Docker installed**: For building container images
3. **Basic Linux/Unix knowledge**: Command line proficiency
4. **Git**: Version control basics
5. **Cloud account** (optional): AWS, GCP, or Azure for production deployment

### Setup Steps

1. **Install Kubernetes Tools**
   ```bash
   # Install kubectl
   curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
   sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

   # Install Minikube
   curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
   sudo install minikube-linux-amd64 /usr/local/bin/minikube

   # Install Helm
   curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
   ```

2. **Start Local Kubernetes Cluster**
   ```bash
   # Start Minikube with sufficient resources
   minikube start --cpus=4 --memory=8192 --driver=docker

   # Verify installation
   kubectl version
   kubectl get nodes
   ```

3. **Enable Required Addons**
   ```bash
   # Enable metrics server for HPA
   minikube addons enable metrics-server

   # Enable ingress controller
   minikube addons enable ingress
   ```

4. **Clone Project and Install Dependencies**
   ```bash
   cd project-02-kubernetes-serving

   # Install Python dependencies
   pip install -r src/requirements.txt

   # Copy environment template
   cp .env.example .env
   ```

5. **Build Docker Image**
   ```bash
   # Build image
   docker build -t model-api:v1.0 .

   # For Minikube, use its Docker daemon
   eval $(minikube docker-env)
   docker build -t model-api:v1.0 .
   ```

---

## Implementation Phases

### Phase 1: Local Kubernetes Setup (20 hours)
- Set up Minikube cluster
- Create Kubernetes manifests (Deployment, Service, ConfigMap, HPA)
- Deploy application locally
- Test health checks and load balancing

### Phase 2: Monitoring Setup (15 hours)
- Install Prometheus and Grafana using Helm
- Configure application metrics endpoint
- Create Grafana dashboards
- Set up basic alerts

### Phase 3: Helm Chart Creation (20 hours)
- Initialize Helm chart structure
- Create templated manifests
- Define values.yaml with configuration options
- Test chart installation and upgrades

### Phase 4: Cloud Deployment (15 hours)
- Create cloud Kubernetes cluster (EKS/GKE/AKS)
- Deploy application to cloud
- Configure DNS and SSL/TLS
- Perform load testing

### Phase 5: Testing & Documentation (10 hours)
- Write automated deployment tests
- Create operational runbook
- Document troubleshooting procedures
- Prepare demo

---

## Deliverables

### Required Deliverables

1. **Kubernetes Manifests**
   - Working Deployment, Service, ConfigMap, HPA, Ingress
   - Properly configured health checks
   - Resource requests and limits

2. **Helm Chart**
   - Complete chart with templates
   - Comprehensive values.yaml
   - README with installation instructions

3. **Monitoring Setup**
   - Prometheus deployment
   - Grafana dashboards (exported JSON)
   - Alert rules configuration

4. **Documentation**
   - Architecture diagram
   - Deployment guide
   - Operations runbook
   - Troubleshooting guide

5. **Test Suite**
   - Kubernetes deployment tests
   - API integration tests
   - Load test scripts and results

6. **Demo**
   - 10-minute video or live demo showing:
     - Deployment process
     - Auto-scaling in action
     - Rolling update with zero downtime
     - Monitoring dashboards

---

## Assessment Criteria

Your project will be evaluated on:

### Kubernetes Configuration (30%)
- Properly configured Deployment with health checks
- Correct Service and Ingress setup
- Working auto-scaling with appropriate thresholds
- Proper resource management

### Monitoring & Observability (20%)
- Prometheus metrics collection
- Informative Grafana dashboards
- Meaningful alerts
- Application-level metrics

### Helm Chart (20%)
- Well-structured chart with reusable templates
- Comprehensive and documented values.yaml
- Flexibility for different environments
- Clear documentation

### Operations (15%)
- Smooth rolling updates
- Quick rollback capability
- Responsive auto-scaling
- Clear operational procedures

### Performance (15%)
- Meets latency requirements under load
- Efficient resource utilization
- Proper scaling behavior
- Handles traffic spikes

**Passing Score:** 70/100

---

## Resources

### Official Documentation
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Helm Documentation](https://helm.sh/docs/)
- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)

### Recommended Tutorials
- [Kubernetes Basics Tutorial](https://kubernetes.io/docs/tutorials/kubernetes-basics/)
- [HPA Walkthrough](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale-walkthrough/)
- [Helm Quickstart](https://helm.sh/docs/intro/quickstart/)

### Books
- "Kubernetes Up & Running" by Kelsey Hightower
- "The Kubernetes Book" by Nigel Poulton

### Tools
- [K9s](https://k9scli.io/) - Terminal UI for Kubernetes
- [Lens](https://k8slens.dev/) - Kubernetes IDE
- [k6](https://k6.io/) - Load testing tool

---

## Common Pitfalls

1. **No resource limits**: Pods can consume all node resources causing crashes
2. **Poor health checks**: Readiness probes too aggressive or missing entirely
3. **Wrong HPA metrics**: Scaling on inappropriate metrics or thresholds
4. **No rolling update strategy**: Updates cause downtime
5. **Hardcoded values**: Not using ConfigMaps makes updates difficult
6. **Missing monitoring**: Can't debug issues without metrics
7. **No namespace isolation**: Mixing resources complicates management

## Pro Tips

1. **Use namespaces**: Separate dev/staging/prod environments
2. **Label everything**: Makes resource selection and debugging easier
3. **Test locally first**: Use Minikube before expensive cloud deployments
4. **Use Helm early**: Avoid managing raw YAML for complex applications
5. **Monitor from day 1**: Set up Prometheus + Grafana before issues arise
6. **Document as you go**: Future you will be grateful
7. **Load test thoroughly**: Find your limits before production traffic

---

## Support

If you encounter issues:

1. **Check TROUBLESHOOTING.md** for common problems
2. **Review Kubernetes logs**: `kubectl logs <pod-name>`
3. **Describe resources**: `kubectl describe pod <pod-name>`
4. **Check events**: `kubectl get events --sort-by='.lastTimestamp'`
5. **Use monitoring dashboards**: Check Grafana for anomalies

---

## Next Steps

After completing this project, you'll be ready for:

- **Project 03**: Advanced monitoring and observability
- **Project 04**: CI/CD pipeline for model deployments
- **Project 05**: Multi-model serving with traffic routing

---

**Project Version:** 1.0
**Last Updated:** October 2025
**Maintained By:** AI Infrastructure Curriculum Team
