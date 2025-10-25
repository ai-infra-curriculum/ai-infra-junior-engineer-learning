# Lecture 01: Kubernetes Architecture

## Table of Contents
1. [Introduction](#introduction)
2. [What is Kubernetes?](#what-is-kubernetes)
3. [Kubernetes Architecture Overview](#kubernetes-architecture-overview)
4. [Control Plane Components](#control-plane-components)
5. [Worker Node Components](#worker-node-components)
6. [Kubernetes Objects and API](#kubernetes-objects-and-api)
7. [Cluster Networking](#cluster-networking)
8. [How Kubernetes Schedules Workloads](#how-kubernetes-schedules-workloads)
9. [High Availability and Fault Tolerance](#high-availability-and-fault-tolerance)
10. [Kubernetes in AI/ML Infrastructure](#kubernetes-in-aiml-infrastructure)
11. [Summary and Key Takeaways](#summary-and-key-takeaways)

## Introduction

Kubernetes (often abbreviated as K8s, where "8" represents the eight letters between "K" and "s") is the most widely adopted container orchestration platform in the world. Originally developed by Google and based on their internal Borg system, Kubernetes was open-sourced in 2014 and donated to the Cloud Native Computing Foundation (CNCF) in 2015.

Understanding Kubernetes architecture is fundamental to working with modern cloud-native applications and AI/ML infrastructure. This lecture provides a deep dive into how Kubernetes works under the hood, preparing you to deploy, manage, and troubleshoot containerized applications effectively.

### Learning Objectives

By the end of this lecture, you will:
- Understand the overall Kubernetes architecture and design philosophy
- Identify and explain the purpose of each control plane component
- Understand worker node components and their roles
- Comprehend the Kubernetes API and object model
- Explain how Kubernetes networking works
- Understand the scheduling and lifecycle management process
- Apply this knowledge to AI/ML infrastructure scenarios

### Prerequisites
- Module 003: Docker Fundamentals
- Basic understanding of distributed systems
- Familiarity with YAML syntax
- Linux command-line proficiency

## What is Kubernetes?

### Core Purpose

Kubernetes is a **container orchestration platform** that automates the deployment, scaling, and management of containerized applications. It solves the challenge of running containers at scale across multiple machines while providing:

- **Automated deployment** and rollback
- **Service discovery** and load balancing
- **Self-healing** capabilities
- **Horizontal scaling** based on demand
- **Secret and configuration** management
- **Storage orchestration**
- **Batch execution** and job management

### The Problem Kubernetes Solves

Before Kubernetes, deploying containerized applications at scale required:
- Manual container placement across servers
- Custom scripts for health monitoring and restart
- Complex load balancing configuration
- Manual scaling based on demand
- Difficult rollouts and rollbacks
- No standard way to manage configuration

Kubernetes provides a **declarative** approach: you tell Kubernetes the desired state of your application, and it continuously works to maintain that state.

### Declarative vs Imperative

**Imperative approach** (traditional):
```bash
# Manual steps to deploy an application
ssh server1
docker run -d --name app1 myapp:v1
ssh server2
docker run -d --name app2 myapp:v1
# Configure load balancer...
# Set up health checks...
```

**Declarative approach** (Kubernetes):
```yaml
# Describe desired state in YAML
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: app
        image: myapp:v1
```

Kubernetes reads this manifest and makes it happen, continuously ensuring your desired state matches reality.

### Key Benefits for AI/ML Workloads

1. **Resource Management**: Efficiently allocate GPU/CPU resources for training and inference
2. **Scalability**: Automatically scale model serving based on request load
3. **Portability**: Run the same ML workloads on any cloud or on-premises
4. **Experimentation**: Quickly spin up/down environments for ML experiments
5. **Job Scheduling**: Run batch training jobs, hyperparameter tuning, etc.
6. **Storage**: Manage data and model storage with persistent volumes

## Kubernetes Architecture Overview

Kubernetes follows a **master-worker** (also called control plane and worker nodes) architecture. A Kubernetes cluster consists of:

1. **Control Plane** (master): Makes global decisions about the cluster
2. **Worker Nodes**: Run the actual application workloads
3. **Add-ons**: Optional components for DNS, monitoring, etc.

### High-Level Architecture Diagram

```
                    Kubernetes Cluster
    ┌──────────────────────────────────────────────┐
    │                                              │
    │  ┌────────────────────────────────────┐     │
    │  │        Control Plane               │     │
    │  │  ┌──────────────────────────────┐  │     │
    │  │  │   API Server (kube-apiserver)│  │     │
    │  │  └────────────┬─────────────────┘  │     │
    │  │               │                     │     │
    │  │  ┌────────────┴─────────────┐      │     │
    │  │  │                          │      │     │
    │  │  ▼                          ▼      │     │
    │  │ ┌──────────┐          ┌─────────┐ │     │
    │  │ │Scheduler │          │  etcd   │ │     │
    │  │ │(kube-    │          │ (key-   │ │     │
    │  │ │scheduler)│          │  value  │ │     │
    │  │ └──────────┘          │  store) │ │     │
    │  │                       └─────────┘ │     │
    │  │ ┌──────────────────────────────┐  │     │
    │  │ │ Controller Manager           │  │     │
    │  │ │ (kube-controller-manager)    │  │     │
    │  │ └──────────────────────────────┘  │     │
    │  │                                    │     │
    │  │ ┌──────────────────────────────┐  │     │
    │  │ │ Cloud Controller Manager     │  │     │
    │  │ │ (cloud-specific logic)       │  │     │
    │  │ └──────────────────────────────┘  │     │
    │  └────────────────────────────────────┘     │
    │                                              │
    │  ┌────────────────────────────────────┐     │
    │  │         Worker Nodes               │     │
    │  │                                    │     │
    │  │  Node 1      Node 2      Node 3   │     │
    │  │ ┌──────┐    ┌──────┐    ┌──────┐  │     │
    │  │ │kubelet│    │kubelet│    │kubelet│  │     │
    │  │ └───┬──┘    └───┬──┘    └───┬──┘  │     │
    │  │     │           │           │      │     │
    │  │ ┌───▼───┐   ┌──▼────┐   ┌──▼───┐  │     │
    │  │ │kube-  │   │kube-  │   │kube- │  │     │
    │  │ │proxy  │   │proxy  │   │proxy │  │     │
    │  │ └───────┘   └───────┘   └──────┘  │     │
    │  │     │           │           │      │     │
    │  │ ┌───▼───────────▼───────────▼───┐  │     │
    │  │ │  Container Runtime (Docker,  │  │     │
    │  │ │  containerd, CRI-O)          │  │     │
    │  │ └──────────────────────────────┘  │     │
    │  │     │           │           │      │     │
    │  │ ┌───▼───┐   ┌──▼────┐   ┌──▼───┐  │     │
    │  │ │ Pods  │   │ Pods  │   │ Pods │  │     │
    │  │ │░░░░░░░│   │░░░░░░░│   │░░░░░░│  │     │
    │  │ └───────┘   └───────┘   └──────┘  │     │
    │  └────────────────────────────────────┘     │
    │                                              │
    └──────────────────────────────────────────────┘
```

### Component Communication

All components communicate through the **API Server**. This is a crucial architectural principle:

- Worker nodes don't talk to each other directly
- The Scheduler doesn't directly tell nodes what to run
- Controllers watch the API Server for changes
- Everything goes through the API Server's RESTful API

This centralized communication model provides:
- **Consistency**: Single source of truth (etcd via API Server)
- **Security**: Authentication and authorization in one place
- **Auditability**: All actions can be logged
- **Extensibility**: Easy to add new components that watch the API

## Control Plane Components

The control plane is the "brain" of the Kubernetes cluster. It makes global decisions about the cluster (like scheduling) and detects and responds to cluster events (like starting a new pod when a deployment's replicas field is unsatisfied).

### 1. API Server (kube-apiserver)

**Purpose**: The frontend for the Kubernetes control plane. All communication goes through the API Server.

**Key Responsibilities**:
- Exposes the Kubernetes API (RESTful HTTP API)
- Authenticates and authorizes requests
- Validates and processes API requests
- Updates etcd with the cluster state
- Serves as the communication hub for all components

**How it Works**:
```
User/kubectl → API Server → Validate → Authenticate → Authorize →
               Admission Controllers → Write to etcd → Return response
```

**Example Interaction**:
```bash
# When you run this command:
kubectl create deployment nginx --image=nginx

# The API Server:
# 1. Authenticates you (are you who you say you are?)
# 2. Authorizes you (are you allowed to create deployments?)
# 3. Validates the request (is the deployment spec valid?)
# 4. Runs admission controllers (mutate/validate the object)
# 5. Stores the deployment in etcd
# 6. Returns success to kubectl
```

**Key Characteristics**:
- **Stateless**: Doesn't store any data itself (uses etcd)
- **Horizontally scalable**: Can run multiple replicas for high availability
- **RESTful**: Uses standard HTTP methods (GET, POST, PUT, DELETE, PATCH)
- **Versioned API**: Supports multiple API versions (v1, v1beta1, etc.)

**API Groups and Versions**:
```yaml
# Core API group (legacy, no group name)
apiVersion: v1
kind: Pod

# Apps API group
apiVersion: apps/v1
kind: Deployment

# Batch API group
apiVersion: batch/v1
kind: Job
```

### 2. etcd

**Purpose**: Consistent and highly-available key-value store used as Kubernetes' backing store for all cluster data.

**Key Responsibilities**:
- Store the entire cluster state
- Provide consistency using the Raft consensus algorithm
- Support watch operations for real-time updates
- Enable cluster configuration storage

**What's Stored in etcd**:
- All Kubernetes objects (Pods, Deployments, Services, etc.)
- Cluster configuration
- Secrets and ConfigMaps
- Resource quotas and limits
- Network policies
- Service account tokens

**Example etcd Structure**:
```
/registry/
  /pods/
    /default/
      /nginx-pod
  /deployments/
    /default/
      /nginx-deployment
  /services/
    /default/
      /nginx-service
  /secrets/
    /default/
      /my-secret
```

**Key Characteristics**:
- **Strongly consistent**: Uses Raft consensus (requires quorum)
- **Highly available**: Typically run 3 or 5 instances
- **Watch capability**: Components can watch for changes
- **Fast**: Optimized for frequent small reads/writes

**Why Raft Consensus?**:
Raft ensures that all etcd instances agree on the cluster state, even in the face of network partitions or node failures. It requires a majority (quorum) to make decisions:
- 3 nodes: Can tolerate 1 failure
- 5 nodes: Can tolerate 2 failures
- 7 nodes: Can tolerate 3 failures (rarely needed)

**Security Note**:
etcd contains all cluster secrets (even encrypted ones). Securing etcd is critical:
- Use TLS for client-server communication
- Use TLS for peer-to-peer communication
- Enable encryption at rest
- Restrict network access
- Regular backups

### 3. Scheduler (kube-scheduler)

**Purpose**: Watches for newly created Pods and assigns them to worker nodes based on resource requirements, constraints, and policies.

**Key Responsibilities**:
- Select the best node for each Pod
- Consider resource requirements (CPU, memory, GPU)
- Respect constraints (node selectors, affinity, taints/tolerations)
- Balance workloads across nodes
- Handle priorities and preemption

**Scheduling Process**:
```
1. Watch API Server for unscheduled Pods (spec.nodeName == "")
2. Filtering Phase: Eliminate unsuitable nodes
   - Insufficient resources?
   - Node selector mismatch?
   - Taints/tolerations violations?
   - Pod affinity/anti-affinity rules?
3. Scoring Phase: Rank remaining nodes
   - Resource balance (spread workloads)
   - Node affinity preferences
   - Inter-pod affinity
   - Image locality
4. Bind Pod to highest-scoring node
5. Update API Server (set spec.nodeName)
```

**Example Scheduling Decision**:
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: ml-training
spec:
  containers:
  - name: trainer
    image: pytorch:latest
    resources:
      requests:
        memory: "16Gi"
        cpu: "4"
        nvidia.com/gpu: "1"  # Requires GPU
  nodeSelector:
    gpu-type: "nvidia-v100"  # Must match node label
```

**Scheduler Decision Process**:
1. **Filter**: Nodes without V100 GPUs → eliminated
2. **Filter**: Nodes without 16Gi memory → eliminated
3. **Filter**: Nodes without available GPU → eliminated
4. **Score**: Remaining nodes ranked by:
   - Available resources
   - Workload distribution
   - Image already present?
5. **Bind**: Pod assigned to highest-scoring node

**Advanced Scheduling**:
- **Affinity/Anti-affinity**: Co-locate or separate Pods
- **Taints and Tolerations**: Dedicate nodes to specific workloads
- **Priority Classes**: Preempt lower-priority Pods if needed
- **Custom Schedulers**: Write your own scheduler for special needs

**AI/ML Example - GPU Node Selection**:
```yaml
# Taint GPU nodes so only GPU workloads run there
kubectl taint nodes gpu-node-1 nvidia.com/gpu=true:NoSchedule

# ML Pod tolerates the taint
apiVersion: v1
kind: Pod
metadata:
  name: ml-inference
spec:
  tolerations:
  - key: nvidia.com/gpu
    operator: Equal
    value: "true"
    effect: NoSchedule
  containers:
  - name: model-server
    image: tensorflow/serving:latest-gpu
    resources:
      limits:
        nvidia.com/gpu: 1
```

### 4. Controller Manager (kube-controller-manager)

**Purpose**: Runs controller processes that regulate the state of the cluster, continuously working to move the current state toward the desired state.

**Key Responsibilities**:
- Run multiple controllers in a single process
- Watch for changes via the API Server
- Make changes to bring actual state to desired state
- Handle node failures, replication, endpoints, service accounts

**Core Controllers**:

**a) Node Controller**:
- Monitors node health
- Marks nodes as unhealthy if they stop heartbeating
- Evicts Pods from failed nodes

```
Every 10s: Check node heartbeat
If missed 40s: Mark node as Unknown
If Unknown for 5m: Evict Pods from node
```

**b) Replication Controller / ReplicaSet Controller**:
- Ensures the correct number of Pod replicas are running
- Creates/deletes Pods to match desired replicas

```yaml
# Desired state: 3 replicas
spec:
  replicas: 3

# Controller continuously ensures:
# - If 2 replicas exist → create 1 more
# - If 4 replicas exist → delete 1
# - If 3 replicas exist → do nothing
```

**c) Endpoints Controller**:
- Populates Endpoints objects (links Services to Pods)
- Watches Services and Pods
- Updates endpoints when Pods are added/removed

```
Service "web" with selector "app=nginx"
  → Controller finds all Pods with label "app=nginx"
  → Creates Endpoints object with Pod IPs
  → kube-proxy uses Endpoints for load balancing
```

**d) Service Account & Token Controllers**:
- Creates default service accounts for new namespaces
- Generates API access tokens for service accounts

**e) Deployment Controller**:
- Manages Deployment objects
- Creates/updates ReplicaSets
- Handles rolling updates and rollbacks

```yaml
# User updates deployment image
kubectl set image deployment/nginx nginx=nginx:1.20

# Deployment controller:
# 1. Creates new ReplicaSet with nginx:1.20
# 2. Scales new ReplicaSet up gradually
# 3. Scales old ReplicaSet down gradually
# 4. Monitors rollout health
# 5. Rollback if update fails
```

**f) Job Controller**:
- Manages Job objects
- Creates Pods to run jobs to completion
- Tracks successful/failed completions

**g) CronJob Controller**:
- Creates Jobs on a schedule
- Manages Job history and cleanup

**Controller Pattern** (Reconciliation Loop):
```go
// Pseudocode for how controllers work
for {
  desiredState = getFromAPIServer()
  currentState = getFromCluster()

  if currentState != desiredState {
    makeChangesToReachDesiredState()
  }

  sleep(reconciliationPeriod)
}
```

This **level-triggered** (not edge-triggered) approach means:
- Controllers periodically check state (resilient to missed events)
- If manual changes are made, controllers fix them
- Self-healing behavior

### 5. Cloud Controller Manager (cloud-controller-manager)

**Purpose**: Embeds cloud-specific control logic, allowing Kubernetes to interact with the underlying cloud provider's API.

**Key Responsibilities**:
- Manage cloud-specific resources (load balancers, volumes, routes)
- Remove cloud provider code from core Kubernetes
- Enable cloud provider plugins

**Cloud-Specific Controllers**:

**a) Node Controller**:
- Check if a node has been deleted in the cloud after it stops responding
- Update node with cloud provider-specific information (zone, instance type)

**b) Route Controller**:
- Set up routes in the cloud so containers on different nodes can communicate

**c) Service Controller**:
- Create/delete cloud load balancers for LoadBalancer-type Services

```yaml
apiVersion: v1
kind: Service
metadata:
  name: ml-api
spec:
  type: LoadBalancer  # Cloud controller creates cloud LB
  selector:
    app: ml-api
  ports:
  - port: 80
    targetPort: 8080
```

**d) Volume Controller**:
- Create/attach/mount cloud volumes (EBS, Persistent Disk, etc.)

**Example Cloud Providers**:
- AWS: ELB/ALB/NLB for services, EBS for volumes
- GCP: Cloud Load Balancer, Persistent Disk
- Azure: Azure Load Balancer, Azure Disk
- OpenStack: Neutron LBaaS, Cinder

## Worker Node Components

Worker nodes are the machines (physical or virtual) that run your containerized applications. Each worker node runs the components necessary to maintain running Pods and provide the Kubernetes runtime environment.

### Node Anatomy

```
Worker Node
┌─────────────────────────────────────────────┐
│                                             │
│  ┌────────────────────────────────────┐    │
│  │         kubelet                    │    │
│  │  (Node agent, Pod lifecycle)       │    │
│  └────────┬───────────────────────────┘    │
│           │                                 │
│           ▼                                 │
│  ┌────────────────────────────────────┐    │
│  │    Container Runtime               │    │
│  │  (Docker, containerd, CRI-O)       │    │
│  └────────┬───────────────────────────┘    │
│           │                                 │
│           ▼                                 │
│  ┌────────────────────────────────────┐    │
│  │         Pods                       │    │
│  │  ┌──────────┐  ┌──────────┐       │    │
│  │  │Container │  │Container │       │    │
│  │  │    1     │  │    2     │       │    │
│  │  └──────────┘  └──────────┘       │    │
│  └────────────────────────────────────┘    │
│                                             │
│  ┌────────────────────────────────────┐    │
│  │       kube-proxy                   │    │
│  │  (Network proxy, load balancing)   │    │
│  └────────────────────────────────────┘    │
│                                             │
│  ┌────────────────────────────────────┐    │
│  │    Optional: Device Plugins        │    │
│  │  (GPU, FPGA, InfiniBand, etc.)     │    │
│  └────────────────────────────────────┘    │
│                                             │
└─────────────────────────────────────────────┘
```

### 1. kubelet

**Purpose**: The primary node agent that runs on each worker node. It's responsible for ensuring containers are running in Pods as specified.

**Key Responsibilities**:
- Register node with API Server
- Watch API Server for Pods assigned to its node
- Start/stop containers via container runtime
- Monitor Pod and container health
- Report node and Pod status to API Server
- Execute liveness and readiness probes
- Mount volumes

**kubelet Workflow**:
```
1. Register with API Server (send node info)
2. Watch for Pods with spec.nodeName == <this-node>
3. For each Pod:
   a. Pull container images
   b. Create containers via CRI (Container Runtime Interface)
   c. Mount volumes
   d. Set up network
   e. Start containers
   f. Monitor health probes
   g. Report status to API Server
4. If Pod should be deleted:
   a. Stop containers
   b. Clean up volumes
   c. Remove Pod from node
```

**Health Probes**:

kubelet performs three types of probes:

**Liveness Probe**: Is the container still alive?
```yaml
livenessProbe:
  httpGet:
    path: /healthz
    port: 8080
  initialDelaySeconds: 3
  periodSeconds: 10
# If fails, kubelet restarts container
```

**Readiness Probe**: Is the container ready to receive traffic?
```yaml
readinessProbe:
  tcpSocket:
    port: 8080
  initialDelaySeconds: 5
  periodSeconds: 5
# If fails, Pod removed from Service endpoints
```

**Startup Probe**: Has the container successfully started?
```yaml
startupProbe:
  exec:
    command: ["/bin/sh", "-c", "cat /app/initialized"]
  failureThreshold: 30
  periodSeconds: 10
# Protects slow-starting containers from liveness probe
```

**Pod Lifecycle Managed by kubelet**:
```
Pending → Running → Succeeded/Failed
           ↓
         CrashLoopBackOff (if repeatedly failing)
```

**Resource Monitoring**:
kubelet monitors:
- CPU usage per container
- Memory usage per container
- Filesystem usage
- Network I/O

This data is exposed via the Metrics API and used by horizontal pod autoscaler (HPA).

### 2. Container Runtime

**Purpose**: The software responsible for running containers. Kubernetes supports any CRI-compliant runtime.

**Supported Runtimes**:
- **containerd**: Lightweight, industry-standard runtime (CNCF graduated project)
- **CRI-O**: Lightweight runtime specifically for Kubernetes
- **Docker Engine**: Via cri-dockerd shim (deprecated in K8s 1.24+)

**Container Runtime Interface (CRI)**:
Kubernetes uses CRI to communicate with container runtimes, providing a plugin interface:

```
kubelet → CRI API → Container Runtime → Containers
```

**CRI Operations**:
- `RunPodSandbox`: Create Pod sandbox (network namespace)
- `CreateContainer`: Create container
- `StartContainer`: Start container
- `StopContainer`: Stop container
- `RemoveContainer`: Remove container
- `ListContainers`: List containers
- `PullImage`: Pull container image

**Why Multiple Runtimes?**:
Different use cases benefit from different runtimes:
- **containerd**: General purpose, lightweight
- **CRI-O**: Minimal, designed for Kubernetes only
- **gVisor**: Enhanced security (sandboxed containers)
- **Kata Containers**: VM-like isolation with container UX

**Image Management**:
Container runtime handles:
- Pulling images from registries
- Image caching
- Image layers and storage
- Image garbage collection

### 3. kube-proxy

**Purpose**: Network proxy that runs on each node, implementing Kubernetes Service networking.

**Key Responsibilities**:
- Maintain network rules on nodes
- Enable Service abstraction (ClusterIP)
- Implement load balancing to Pod backends
- Support different Service types (ClusterIP, NodePort, LoadBalancer)

**How Services Work** (with kube-proxy):

```
Client → Service IP:Port (virtual, not real)
            ↓
         kube-proxy (intercepts traffic)
            ↓
         Load balances to Pod IPs
            ↓
         Pod 1, Pod 2, or Pod 3 (backends)
```

**Proxy Modes**:

**a) iptables mode** (default):
- Uses Linux iptables rules for routing
- Randomly selects backend Pod
- Lower overhead than userspace mode
- No retry if selected Pod doesn't respond

```bash
# Example iptables rules created by kube-proxy
iptables -t nat -A KUBE-SERVICES \
  -d 10.96.0.1/32 -p tcp --dport 80 \
  -j KUBE-SVC-XYZABC

iptables -t nat -A KUBE-SVC-XYZABC \
  -m statistic --mode random --probability 0.33 \
  -j KUBE-SEP-POD1

iptables -t nat -A KUBE-SVC-XYZABC \
  -m statistic --mode random --probability 0.50 \
  -j KUBE-SEP-POD2

iptables -t nat -A KUBE-SVC-XYZABC \
  -j KUBE-SEP-POD3
```

**b) ipvs mode** (IP Virtual Server):
- Uses Linux IPVS (in-kernel load balancer)
- More efficient for large numbers of Services
- Better load balancing algorithms (round-robin, least connection, etc.)
- Better performance

**c) userspace mode** (legacy):
- kube-proxy acts as an actual proxy
- Higher overhead
- Can retry failed backends

**Service Types Implemented by kube-proxy**:

1. **ClusterIP**: Internal cluster IP (default)
2. **NodePort**: Exposes service on each node's IP at a static port
3. **LoadBalancer**: Uses cloud provider's load balancer
4. **ExternalName**: Maps to DNS name

**Example NodePort Flow**:
```
External Client → Node IP:30001 (NodePort)
                      ↓
                  kube-proxy rule
                      ↓
                  Service ClusterIP:80
                      ↓
                  Load balance to Pods
                      ↓
                  Pod:8080
```

### 4. Device Plugins (Optional)

**Purpose**: Enable Kubernetes to manage specialized hardware resources like GPUs, FPGAs, high-performance NICs, etc.

**How Device Plugins Work**:
```
Hardware → Device Plugin → kubelet → Scheduler
                                        ↓
                                   Pod with resource request
```

**GPU Example** (NVIDIA Device Plugin):
```yaml
# Node advertises GPU resources
kubectl describe node gpu-node-1

Capacity:
  nvidia.com/gpu: 4

# Pod requests GPU
apiVersion: v1
kind: Pod
metadata:
  name: gpu-job
spec:
  containers:
  - name: cuda-container
    image: nvidia/cuda:11.0-base
    resources:
      limits:
        nvidia.com/gpu: 1
```

**Common Device Plugins**:
- **NVIDIA GPU Plugin**: For NVIDIA GPUs
- **AMD GPU Plugin**: For AMD GPUs
- **Intel QAT Plugin**: For Intel QuickAssist
- **RDMA Plugin**: For high-performance networking
- **FPGA Plugin**: For FPGAs

**Critical for AI/ML**:
Device plugins are essential for AI infrastructure, enabling:
- GPU allocation for training and inference
- Multi-GPU workloads
- GPU sharing (with tools like NVIDIA MPS)
- Resource tracking and accounting

## Kubernetes Objects and API

### Understanding Kubernetes Objects

Kubernetes objects are persistent entities in the Kubernetes system that represent the state of your cluster:
- **What** containerized applications are running
- **Where** they're running (which nodes)
- **How many** replicas exist
- **Policies** around restart, updates, and scaling

### Object Specification

Every Kubernetes object has two important fields:

**spec**: Desired state (what you want)
**status**: Current state (what actually exists)

Kubernetes continuously works to make **status** match **spec**.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx
spec:                    # DESIRED STATE
  replicas: 3           # Want 3 Pods
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:1.20
status:                  # CURRENT STATE (read-only, set by system)
  replicas: 3           # Currently 3 Pods
  readyReplicas: 3      # 3 are ready
  conditions:
  - type: Available
    status: "True"
```

### Required Fields

Every Kubernetes object manifest requires:

1. **apiVersion**: Which API version to use
2. **kind**: Type of object to create
3. **metadata**: Data to uniquely identify the object
4. **spec**: Desired state for the object

```yaml
apiVersion: v1           # API version
kind: Pod                # Object type
metadata:                # Identifying information
  name: my-pod
  namespace: default
  labels:
    app: myapp
spec:                    # Desired state
  containers:
  - name: nginx
    image: nginx:1.20
```

### Namespaces

Namespaces provide a mechanism for isolating groups of resources within a single cluster.

**Default Namespaces**:
- **default**: Default namespace for objects with no namespace
- **kube-system**: For Kubernetes system components
- **kube-public**: Publicly readable by all users
- **kube-node-lease**: For node heartbeat/lease objects

**Creating Namespaces**:
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: ml-training

# OR via kubectl
kubectl create namespace ml-training
```

**Using Namespaces**:
```bash
# Create resources in namespace
kubectl create deployment nginx --image=nginx -n ml-training

# View resources in namespace
kubectl get pods -n ml-training

# View all namespaces
kubectl get namespaces
```

**Resource Quotas** (per namespace):
```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: ml-quota
  namespace: ml-training
spec:
  hard:
    requests.cpu: "100"
    requests.memory: 200Gi
    requests.nvidia.com/gpu: "4"
    persistentvolumeclaims: "10"
```

### Labels and Selectors

**Labels**: Key-value pairs attached to objects for identification and organization.

```yaml
metadata:
  labels:
    environment: production
    app: ml-api
    version: v1.2.3
    tier: backend
    owner: ml-team
```

**Selectors**: Query objects by labels.

**Equality-based**:
```bash
kubectl get pods -l environment=production
kubectl get pods -l environment!=staging
kubectl get pods -l 'environment in (production, qa)'
```

**Set-based**:
```yaml
selector:
  matchLabels:
    app: ml-api
  matchExpressions:
  - key: tier
    operator: In
    values:
    - backend
    - api
  - key: environment
    operator: NotIn
    values:
    - development
```

**Why Labels Matter**:
- Services use selectors to find Pods
- Deployments use selectors to manage ReplicaSets
- Network Policies use selectors for access control
- Operators and controllers query by labels

### Annotations

Annotations attach non-identifying metadata to objects. Unlike labels, annotations are not used for selection.

```yaml
metadata:
  annotations:
    description: "ML model serving API v1.2.3"
    prometheus.io/scrape: "true"
    prometheus.io/port: "9090"
    kubectl.kubernetes.io/last-applied-configuration: |
      {...}
    deployed-by: "jenkins-pipeline"
    git-commit: "a3b5f9c"
```

**Common Uses**:
- Build/release information
- Client libraries configuration
- Tool-specific configuration
- Documentation/description

## Cluster Networking

Kubernetes networking model has four key requirements:

1. **All Pods can communicate with all other Pods** without NAT
2. **All Nodes can communicate with all Pods** without NAT
3. **The IP a Pod sees itself as** is the same IP others see it as
4. **Containers in the same Pod** share network namespace

### Pod Networking

Each Pod gets its own IP address. Containers within a Pod:
- Share the same IP address
- Share the same network namespace
- Communicate via localhost
- Share the same port space (no port conflicts!)

```
Pod (IP: 10.244.1.5)
┌─────────────────────────────┐
│  Container 1                │
│  listening on :8080         │
│           ↕                 │
│       localhost             │
│           ↕                 │
│  Container 2                │
│  listening on :9090         │
└─────────────────────────────┘
```

### Container Network Interface (CNI)

Kubernetes uses CNI plugins to set up networking. Popular CNI plugins:

**Calico**:
- Layer 3 networking using BGP
- Network policy enforcement
- Good for large-scale deployments

**Flannel**:
- Simple overlay network
- Easy to set up
- Uses VXLAN or host-gw backend

**Weave Net**:
- Mesh network
- Automatic discovery
- Encryption support

**Cilium**:
- eBPF-based
- Advanced network policies
- Service mesh capabilities

### Service Networking

Services provide stable IP addresses and DNS names for dynamic sets of Pods.

**ClusterIP** (default):
```yaml
apiVersion: v1
kind: Service
metadata:
  name: ml-api
spec:
  type: ClusterIP         # Cluster-internal IP
  selector:
    app: ml-api
  ports:
  - port: 80              # Service port
    targetPort: 8080      # Container port
```

**DNS Names**:
Services automatically get DNS names:
```
<service-name>.<namespace>.svc.cluster.local

# Examples:
ml-api.default.svc.cluster.local
redis.cache.svc.cluster.local
```

### Network Policies

Network Policies control traffic flow between Pods (firewall rules).

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: ml-api-policy
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: ml-api
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          role: frontend
    ports:
    - protocol: TCP
      port: 8080
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: database
    ports:
    - protocol: TCP
      port: 5432
```

This policy:
- Applies to Pods with label `app=ml-api`
- Allows ingress from Pods with `role=frontend` on port 8080
- Allows egress to Pods with `app=database` on port 5432
- Denies all other traffic (default deny)

## How Kubernetes Schedules Workloads

### End-to-End Deployment Flow

Let's trace what happens when you create a Deployment:

```bash
kubectl create deployment nginx --image=nginx --replicas=3
```

**Step-by-Step Process**:

**1. kubectl → API Server**:
```
kubectl constructs API request:
POST /apis/apps/v1/namespaces/default/deployments
{
  "metadata": {"name": "nginx"},
  "spec": {
    "replicas": 3,
    "selector": {"matchLabels": {"app": "nginx"}},
    "template": {...}
  }
}
```

**2. API Server**:
- Authenticates request
- Authorizes request (RBAC)
- Validates Deployment spec
- Runs admission controllers
- Stores Deployment in etcd
- Returns success to kubectl

**3. Deployment Controller** (watches API Server):
```
Deployment controller notices new Deployment
  → Creates ReplicaSet with desired replica count: 3
  → Stores ReplicaSet in etcd (via API Server)
```

**4. ReplicaSet Controller** (watches API Server):
```
ReplicaSet controller notices new ReplicaSet
  → Current replicas: 0
  → Desired replicas: 3
  → Creates 3 Pod objects (spec.nodeName empty)
  → Stores Pods in etcd (via API Server)
```

**5. Scheduler** (watches API Server for Pods with no nodeName):
```
Scheduler notices 3 unscheduled Pods
For each Pod:
  → Filters suitable nodes (resources, affinity, taints)
  → Scores nodes
  → Selects best node
  → Updates Pod with spec.nodeName = "node-2"
  → Stores in etcd (via API Server)
```

**6. kubelet on node-2** (watches API Server for Pods on its node):
```
kubelet notices Pod scheduled to its node
  → Pulls nginx image (if not cached)
  → Creates Pod sandbox (network namespace)
  → Starts nginx container
  → Monitors container health
  → Reports status to API Server
```

**7. Endpoints Controller** (if Service exists):
```
Endpoints controller notices new Pod with matching labels
  → Updates Service Endpoints with Pod IP
  → Stores in etcd (via API Server)
```

**8. kube-proxy** (watches API Server for Services/Endpoints):
```
kube-proxy notices updated Endpoints
  → Updates iptables/ipvs rules
  → Traffic to Service now load-balanced to new Pod
```

### Visual Timeline

```
Time  Component             Action
─────────────────────────────────────────────────────────
  0s  kubectl               Creates Deployment
  0s  API Server            Stores Deployment in etcd
  1s  Deployment Controller Creates ReplicaSet
  1s  API Server            Stores ReplicaSet in etcd
  2s  ReplicaSet Controller Creates 3 Pod objects
  2s  API Server            Stores Pods in etcd
  3s  Scheduler             Assigns Pods to nodes
  3s  API Server            Updates Pods with nodeName
  4s  kubelet (node-1)      Pulls image, starts container
  4s  kubelet (node-2)      Pulls image, starts container
  4s  kubelet (node-3)      Pulls image, starts container
 10s  kubelet (nodes)       Containers running
 10s  API Server            Pod status: Running
 10s  Endpoints Controller  Updates Service endpoints
 11s  kube-proxy (all)      Updates network rules
 11s  DONE                  Pods serving traffic
```

## High Availability and Fault Tolerance

### Control Plane HA

Production clusters run multiple control plane nodes:

```
       Load Balancer (API Server endpoint)
                 │
        ┌────────┼────────┐
        ▼        ▼        ▼
    API Srv  API Srv  API Srv
        │        │        │
        └────────┼────────┘
                 │
           ┌─────┴─────┐
           ▼           ▼           ▼
        etcd-1      etcd-2      etcd-3
      (Raft leader) (follower) (follower)
```

**Key Points**:
- **Multiple API Servers**: Load-balanced, stateless
- **etcd Cluster**: 3 or 5 nodes with Raft consensus
- **Single Controller Manager**: Leader election (only one active)
- **Single Scheduler**: Leader election (only one active)

**Leader Election**:
Controller Manager and Scheduler use leader election to ensure only one is active:
```
3 Controller Managers running
  → One holds the leader lease
  → Others are standby
  → If leader fails, standby takes over within seconds
```

### Worker Node Fault Tolerance

**Node Failure Detection**:
```
kubelet stops sending heartbeats
  → Node controller marks node Unknown (after 40s)
  → Pods marked as Unknown (after 5 minutes)
  → Scheduler doesn't place new Pods on node
  → Pods evicted (after 5 minutes)
  → ReplicaSets recreate Pods on healthy nodes
```

**Pod Eviction Grace Period**:
```yaml
# In Pod spec
terminationGracePeriodSeconds: 30

# On eviction:
1. Send SIGTERM to containers
2. Wait up to 30 seconds
3. Send SIGKILL if still running
4. Remove Pod
```

### Self-Healing

Kubernetes automatically recovers from failures:

**Container Crashes**:
```
Container exits with error
  → kubelet restarts container
  → Exponential backoff if repeated failures
  → CrashLoopBackOff state (10s, 20s, 40s, 80s, 160s, 5m max)
```

**Node Failures**:
```
Node becomes unreachable
  → Pods rescheduled to healthy nodes
  → StatefulSet Pods require manual intervention (by default)
```

**Application Failures**:
```
Liveness probe fails
  → Container restarted
Readiness probe fails
  → Pod removed from Service endpoints (no traffic)
  → Container keeps running
```

## Kubernetes in AI/ML Infrastructure

### Why Kubernetes for ML?

1. **Resource Management**: Efficiently use expensive GPU resources
2. **Scalability**: Scale model serving from 1 to 1000s of replicas
3. **Portability**: Run anywhere (cloud, on-prem, hybrid)
4. **Isolation**: Separate dev, staging, production environments
5. **Automation**: Automated deployment, scaling, recovery

### ML Workload Patterns on K8s

**1. Model Training** (Batch Jobs):
```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: model-training
spec:
  template:
    spec:
      restartPolicy: OnFailure
      containers:
      - name: trainer
        image: pytorch/pytorch:latest
        command: ["python", "train.py"]
        resources:
          limits:
            nvidia.com/gpu: 4  # 4 GPUs
            memory: "64Gi"
        volumeMounts:
        - name: training-data
          mountPath: /data
        - name: model-output
          mountPath: /models
      volumes:
      - name: training-data
        persistentVolumeClaim:
          claimName: training-data-pvc
      - name: model-output
        persistentVolumeClaim:
          claimName: model-storage-pvc
```

**2. Model Serving** (Deployments):
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: model-server
spec:
  replicas: 3
  selector:
    matchLabels:
      app: model-server
  template:
    metadata:
      labels:
        app: model-server
    spec:
      containers:
      - name: tensorflow-serving
        image: tensorflow/serving:latest-gpu
        ports:
        - containerPort: 8501
        resources:
          limits:
            nvidia.com/gpu: 1
        env:
        - name: MODEL_NAME
          value: "my_model"
        volumeMounts:
        - name: model-volume
          mountPath: /models
      volumes:
      - name: model-volume
        persistentVolumeClaim:
          claimName: model-pvc
```

**3. Jupyter Notebooks** (StatefulSets):
```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: jupyter
spec:
  serviceName: jupyter
  replicas: 1
  selector:
    matchLabels:
      app: jupyter
  template:
    metadata:
      labels:
        app: jupyter
    spec:
      containers:
      - name: jupyter
        image: jupyter/tensorflow-notebook:latest
        ports:
        - containerPort: 8888
        resources:
          limits:
            nvidia.com/gpu: 1
        volumeMounts:
        - name: notebook-storage
          mountPath: /home/jovyan
  volumeClaimTemplates:
  - metadata:
      name: notebook-storage
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 100Gi
```

**4. Distributed Training** (Kubeflow, PyTorch Operator):
```yaml
apiVersion: kubeflow.org/v1
kind: PyTorchJob
metadata:
  name: distributed-training
spec:
  pytorchReplicaSpecs:
    Master:
      replicas: 1
      template:
        spec:
          containers:
          - name: pytorch
            image: pytorch/pytorch:latest
            resources:
              limits:
                nvidia.com/gpu: 1
    Worker:
      replicas: 3
      template:
        spec:
          containers:
          - name: pytorch
            image: pytorch/pytorch:latest
            resources:
              limits:
                nvidia.com/gpu: 1
```

### ML-Specific Kubernetes Tools

- **Kubeflow**: End-to-end ML platform on Kubernetes
- **KServe**: Model serving framework
- **Argo Workflows**: ML pipeline orchestration
- **MLflow**: Experiment tracking, model registry
- **Seldon Core**: Advanced model serving
- **NVIDIA GPU Operator**: Automated GPU management

## Summary and Key Takeaways

### Core Concepts

1. **Kubernetes Architecture** is master-worker with control plane managing worker nodes
2. **API Server** is the central communication hub - everything goes through it
3. **etcd** stores all cluster state using Raft consensus
4. **Scheduler** assigns Pods to nodes based on resources and constraints
5. **Controllers** continuously reconcile desired state with actual state
6. **kubelet** is the node agent managing Pod lifecycle
7. **kube-proxy** implements Service networking and load balancing

### Key Principles

- **Declarative**: Describe desired state, Kubernetes makes it happen
- **Self-Healing**: Automatically recovers from failures
- **Level-Triggered**: Controllers periodically check state
- **API-Centric**: All components interact via API Server
- **Extensible**: Add custom resources, controllers, schedulers

### Mental Model

Think of Kubernetes as a **distributed operating system** for containers:
- **API Server** = Kernel (all calls go through it)
- **etcd** = Filesystem (stores all state)
- **Scheduler** = Process scheduler (assigns work to CPUs/nodes)
- **Controllers** = System daemons (keep things running)
- **kubelet** = Init system (manages processes/containers on each machine)

### For AI/ML Engineers

- Kubernetes provides **standardized infrastructure** for ML workloads
- **GPU management** via device plugins is critical for training/inference
- **Jobs** for training, **Deployments** for serving, **StatefulSets** for notebooks
- **Namespaces** isolate teams and environments
- **Resource quotas** prevent resource contention
- **Horizontal scaling** makes model serving elastic

### Next Steps

Now that you understand Kubernetes architecture, you're ready to:
1. Deploy applications (Lecture 02)
2. Use Helm for package management (Lecture 03)
3. Operate and debug clusters (Lecture 04)
4. Build real ML infrastructure on Kubernetes

### Further Reading

- Official Kubernetes Documentation: https://kubernetes.io/docs/
- Kubernetes API Reference: https://kubernetes.io/docs/reference/
- CNCF Landscape: https://landscape.cncf.io/
- Kubernetes Enhancement Proposals (KEPs): https://github.com/kubernetes/enhancements

---

**Congratulations!** You now understand how Kubernetes works under the hood. This foundational knowledge will serve you throughout your career in AI infrastructure. In the next lecture, we'll put this knowledge into practice by deploying applications to Kubernetes.
