# Module 006: Kubernetes Introduction

## Module Overview

Welcome to Module 006, where you'll learn the fundamentals of Kubernetes (K8s), the industry-standard container orchestration platform. This module provides a comprehensive introduction to Kubernetes architecture, core concepts, and practical operations essential for AI infrastructure work.

Kubernetes has become the de facto standard for deploying, scaling, and managing containerized applications, including ML models and AI workloads. Understanding Kubernetes is critical for any AI infrastructure engineer, as it provides the foundation for building scalable, resilient ML systems.

## What You'll Learn

By the end of this module, you will be able to:

- **Understand Kubernetes Architecture**: Master the core components of Kubernetes including the control plane, worker nodes, and how they interact
- **Deploy Applications**: Create and manage Pods, Deployments, Services, and other Kubernetes resources
- **Use Helm**: Package and deploy applications using Helm charts
- **Operate Kubernetes Clusters**: Use kubectl effectively, debug issues, and monitor cluster health
- **Apply K8s to ML Workloads**: Understand how Kubernetes supports AI/ML infrastructure needs

## Prerequisites

Before starting this module, you should have:

### Required Knowledge
- **Module 003**: Docker Fundamentals (containerization concepts)
- **Module 004**: Container Orchestration Basics
- **Linux CLI**: Basic command-line proficiency
- **YAML**: Understanding of YAML syntax and structure
- **Networking**: Basic networking concepts (ports, DNS, load balancing)

### Required Tools
- Docker Desktop with Kubernetes enabled **OR** Minikube installed
- kubectl CLI tool (version 1.25+)
- Helm CLI (version 3.10+)
- A code editor (VS Code recommended with Kubernetes extension)
- At least 8GB RAM available for local cluster

### Recommended Setup
```bash
# Verify Docker
docker --version

# Verify Kubernetes cluster
kubectl cluster-info

# Verify Helm
helm version

# Check cluster nodes
kubectl get nodes
```

If you don't have a local Kubernetes cluster yet, see `resources/cluster-setup-guide.md` for detailed setup instructions.

## Module Structure

> **Status Update (2025-10-29):** All 5 comprehensive lectures are now complete and available! This module includes practical examples for ML workload deployment on Kubernetes.

This module includes **5 lectures** and **8 exercises** organized into key sections:

### 1. Kubernetes Architecture (Lecture 01)
**Duration**: 3-4 hours
**File**: `lecture-notes/01-k8s-architecture.md`

- Control plane components (API Server, Scheduler, Controller Manager, etcd)
- Worker node components (kubelet, kube-proxy, container runtime)
- Kubernetes objects and API resources
- Cluster networking model
- How Kubernetes schedules and manages containers

### 2. Deploying Applications (Lecture 02)
**Duration**: 4-5 hours
**File**: `lecture-notes/02-deploying-apps.md`

- Pods: The smallest deployable unit
- Deployments: Managing application lifecycle
- Services: Exposing applications
- ConfigMaps and Secrets: Managing configuration
- Persistent storage with Volumes and PersistentVolumeClaims

### 3. Helm Package Management (Lecture 03)
**Duration**: 3-4 hours
**File**: `lecture-notes/03-helm.md`

- Introduction to Helm and package management
- Helm charts structure and templating
- Installing and managing releases
- Creating custom Helm charts
- Helm repositories and chart distribution

### 4. Kubernetes Operations (Lecture 04)
**Duration**: 3-4 hours
**File**: `lecture-notes/04-k8s-operations.md`

- kubectl command reference and shortcuts
- Debugging Pods and Deployments
- Viewing logs and executing commands in containers
- Resource monitoring and metrics
- Troubleshooting common issues

### 5. ML Workloads and Kubeflow (Lecture 05)
**Duration**: 4-5 hours
**File**: `lecture-notes/05-ml-workloads-kubeflow.md`

- Running ML workloads on Kubernetes
- GPU resource management
- Kubeflow introduction and components
- ML pipelines on Kubernetes
- Model serving with KServe/KFServing
- Distributed training patterns
- ML infrastructure best practices

## Learning Path

### Week 1: Foundation
**Days 1-2**: Kubernetes Architecture
- Read lecture-notes/01-k8s-architecture.md
- Watch recommended videos on K8s architecture
- Set up local Kubernetes cluster
- Explore cluster components with kubectl

**Days 3-4**: Deploying Applications
- Read lecture-notes/02-deploying-apps.md
- Complete exercise-01-first-deployment.md
- Practice creating Pods, Deployments, Services
- Experiment with different service types

### Week 2: Advanced Topics
**Days 5-6**: Helm Package Management
- Read lecture-notes/03-helm.md
- Complete exercise-02-helm-chart.md
- Install applications from Helm Hub
- Create your first Helm chart

**Days 7**: Operations and Debugging
- Read lecture-notes/04-k8s-operations.md
- Complete exercise-03-debugging.md
- Practice troubleshooting scenarios
- Review kubectl command shortcuts

### Week 3: Practice and Assessment
**Days 8-9**: Hands-on Practice
- Build a complete ML model serving application on K8s
- Deploy with Helm
- Implement monitoring and logging
- Document your deployment

**Day 10**: Assessment
- Complete module-006-quiz.md
- Self-assessment of learning objectives
- Identify areas for further study

## Hands-on Exercises

> **Status Update (2025-10-29):** All 8 comprehensive exercises are now complete! Each exercise builds practical Kubernetes skills with ML infrastructure examples.

This module includes **8 exercises** that progress from basics to advanced Kubernetes operations:

### Exercise 01: First Deployment
Deploy a simple web application to Kubernetes, expose it with a Service, and scale it up and down. This exercise reinforces core concepts of Pods, Deployments, and Services.

**Skills practiced**:
- Writing Kubernetes manifests
- Using kubectl to manage resources
- Exposing applications
- Scaling applications

### Exercise 02: Helm Chart
Create a Helm chart for a Python Flask application, parameterize the deployment, and install it with different configurations.

**Skills practiced**:
- Helm chart structure
- Templating with Go templates
- Values customization
- Release management

### Exercise 03: Debugging
**File**: `exercises/exercise-03-debugging.md`

Troubleshoot a broken Kubernetes deployment, identify issues using kubectl, fix configuration problems, and verify the application works.

**Skills practiced**:
- Debugging with kubectl
- Reading logs and events
- Identifying common issues
- Fixing misconfigurations

### Exercise 04: ConfigMaps and Secrets
**File**: `exercises/exercise-04-configmaps-secrets.md`

Manage application configuration using ConfigMaps and Secrets.

**Skills practiced**:
- Creating ConfigMaps
- Managing Secrets
- Injecting configuration into Pods
- Environment variables and volume mounts

### Exercise 05: Persistent Storage
**File**: `exercises/exercise-05-persistent-storage.md`

Work with persistent storage for stateful applications.

**Skills practiced**:
- PersistentVolumeClaims
- Storage classes
- StatefulSets basics
- Data persistence patterns

### Exercise 06: Networking and Ingress
**File**: `exercises/exercise-06-networking-ingress.md`

Configure networking and expose applications externally.

**Skills practiced**:
- Service types (ClusterIP, NodePort, LoadBalancer)
- Ingress resources
- DNS and service discovery
- Network policies basics

### Exercise 07: ML Workload Deployment
**File**: `exercises/exercise-07-ml-workload.md`

Deploy a complete ML model serving application on Kubernetes.

**Skills practiced**:
- GPU resource requests
- Model serving deployment
- Horizontal Pod Autoscaling
- ML-specific configurations
- End-to-end ML infrastructure

### Exercise 08: Autoscaling ML Workloads in Kubernetes
**Difficulty**: Intermediate to Advanced
**Duration**: 3-4 hours
**File**: `exercises/exercise-08-autoscaling-ml-workloads.md`

Master Kubernetes autoscaling for ML workloads.

**Skills practiced**:
- Configure Horizontal Pod Autoscaler (HPA) with CPU and custom metrics
- Implement Vertical Pod Autoscaler (VPA) for resource optimization
- Use Prometheus Adapter for custom metrics
- Implement event-driven autoscaling with KEDA
- Design autoscaling policies for cost-effective ML infrastructure
- Handle GPU-based workload scaling considerations

## Assessment Criteria

You should be able to demonstrate:

1. **Conceptual Understanding** (25%)
   - Explain Kubernetes architecture components
   - Describe how Kubernetes schedules workloads
   - Understand Kubernetes networking model
   - Explain the relationship between Pods, Deployments, and Services

2. **Practical Skills** (50%)
   - Deploy applications using kubectl
   - Write Kubernetes manifest files
   - Create and customize Helm charts
   - Use kubectl to inspect and debug resources
   - Troubleshoot common Kubernetes issues

3. **Best Practices** (25%)
   - Apply resource limits and requests
   - Use labels and selectors effectively
   - Implement health checks (liveness/readiness probes)
   - Manage configuration with ConfigMaps and Secrets
   - Follow security best practices

## Key Kubernetes Resources You'll Master

```yaml
# Core workload resources
- Pod                    # Single instance of running process
- Deployment            # Declarative updates for Pods
- ReplicaSet            # Maintains desired number of Pod replicas
- StatefulSet           # For stateful applications
- DaemonSet             # Runs on all/selected nodes
- Job                   # Run-to-completion tasks
- CronJob               # Scheduled jobs

# Service and networking
- Service               # Expose applications
- Ingress               # HTTP/HTTPS routing
- NetworkPolicy         # Network access control

# Configuration and storage
- ConfigMap             # Configuration data
- Secret                # Sensitive data
- PersistentVolume      # Cluster storage
- PersistentVolumeClaim # Storage request

# Cluster resources
- Namespace             # Virtual clusters
- Node                  # Worker machine
- ServiceAccount        # Identity for processes
```

## Real-World AI/ML Use Cases

Throughout this module, we'll connect Kubernetes concepts to AI infrastructure scenarios:

- **Model Serving**: Deploy ML models as microservices with auto-scaling
- **Training Jobs**: Run distributed training workloads with Jobs and GPU resources
- **Data Processing**: Schedule ETL pipelines with CronJobs
- **Feature Stores**: Deploy stateful feature storage with StatefulSets
- **Experiment Tracking**: Run MLflow or similar tools on Kubernetes
- **Jupyter Notebooks**: Provide on-demand notebook environments

## Time Commitment

- **Lecture Reading**: 10-12 hours
- **Hands-on Exercises**: 8-10 hours
- **Practice and Exploration**: 6-8 hours
- **Assessment**: 2 hours

**Total**: Approximately 26-32 hours over 2-3 weeks

This is intensive material, so pace yourself and ensure you understand each concept before moving forward.

## Success Indicators

You've successfully completed this module when you can:

- [ ] Explain the role of each Kubernetes control plane component
- [ ] Create and manage Pods using kubectl
- [ ] Write Deployment manifests with proper resource limits
- [ ] Expose applications using different Service types
- [ ] Create and install Helm charts
- [ ] Debug failing Pods and Deployments
- [ ] Monitor cluster resources
- [ ] Apply best practices for production deployments
- [ ] Deploy a complete ML application to Kubernetes

## Common Challenges and Tips

### Challenge 1: YAML Syntax Errors
**Solution**: Use a YAML validator, enable editor syntax checking, and start with working examples.

### Challenge 2: Resource Not Starting
**Solution**: Always check `kubectl describe pod <name>` for events and `kubectl logs <pod>` for application logs.

### Challenge 3: Networking Issues
**Solution**: Understand Service types, verify selectors match Pod labels, check cluster networking is working.

### Challenge 4: Helm Template Errors
**Solution**: Use `helm template` to render charts locally, validate YAML output, and test incrementally.

### Challenge 5: Cluster Resource Exhaustion
**Solution**: Set resource requests/limits, monitor cluster capacity, clean up unused resources regularly.

## Getting Help

If you get stuck:

1. **Check the lecture notes**: Most common issues are addressed
2. **Review the exercises**: Step-by-step guidance is provided
3. **Consult official docs**: https://kubernetes.io/docs/
4. **Use kubectl explain**: `kubectl explain deployment.spec` shows resource documentation
5. **Debug systematically**: Follow the troubleshooting guide in lecture 04
6. **Community resources**: Kubernetes Slack, Stack Overflow, Reddit r/kubernetes

## Next Steps

After completing this module:

- **Module 007**: Advanced Kubernetes - StatefulSets, custom resources, operators
- **Module 008**: Kubernetes Monitoring - Prometheus, Grafana, logging
- **Module 009**: CI/CD with Kubernetes - GitOps, ArgoCD, automated deployments
- **Project 03**: Deploy a complete ML model serving system on Kubernetes

## Additional Resources

See `resources/recommended-reading.md` for:
- Official Kubernetes documentation links
- Tutorial videos and courses
- Books and blog posts
- Practice environments (Katacoda, Play with Kubernetes)
- Community resources

## Module Files

```
mod-006-kubernetes-intro/
├── README.md (this file)
├── lecture-notes/
│   ├── 01-k8s-architecture.md
│   ├── 02-deploying-apps.md
│   ├── 03-helm.md
│   └── 04-k8s-operations.md
├── exercises/
│   ├── exercise-01-first-deployment.md
│   ├── exercise-02-helm-chart.md
│   └── exercise-03-debugging.md
├── quizzes/
│   └── module-006-quiz.md
└── resources/
    ├── recommended-reading.md
    └── cluster-setup-guide.md
```

## Changelog

- **2025-10-18**: Initial module creation
- Content aligned with Junior AI Infrastructure Engineer role requirements
- Exercises designed for hands-on skill development
- Assessment quiz covers all learning objectives

---

**Ready to begin?** Start with `lecture-notes/01-k8s-architecture.md` to understand how Kubernetes works under the hood.

**Questions or feedback?** Contact ai-infra-curriculum@joshua-ferguson.com
