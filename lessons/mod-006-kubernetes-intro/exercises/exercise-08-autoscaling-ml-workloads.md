# Exercise 08: Autoscaling ML Workloads in Kubernetes

## Overview
Master Kubernetes autoscaling mechanisms to automatically scale ML workloads based on demand. Learn to configure Horizontal Pod Autoscaler (HPA), Vertical Pod Autoscaler (VPA), and custom metrics-based scaling for model serving APIs, batch inference jobs, and training pipelines.

**Duration:** 3-4 hours
**Difficulty:** Intermediate to Advanced

## Learning Objectives
By completing this exercise, you will:
- Configure Horizontal Pod Autoscaler based on CPU, memory, and custom metrics
- Implement Vertical Pod Autoscaler to optimize resource requests
- Use metrics-server and Prometheus Adapter for autoscaling decisions
- Scale ML model serving APIs based on request rates and latency
- Implement event-driven autoscaling with KEDA
- Design autoscaling policies for cost-effective ML infrastructure
- Handle GPU-based workload scaling considerations

## Prerequisites
- Kubernetes cluster (minikube, kind, or cloud cluster)
- kubectl configured
- Helm 3 installed
- Basic understanding of Kubernetes Deployments and Services
- Completed previous Kubernetes exercises

## Scenario
You're managing an **ML Platform** with variable workload patterns:
- **Model Serving API**: Traffic spikes during business hours (9am-5pm)
- **Batch Inference**: Nightly jobs processing large datasets
- **Training Jobs**: Submitted ad-hoc by data scientists
- **Feature Store**: Caching layer with fluctuating memory needs

Manual scaling is inefficient and costly. You'll implement autoscaling to:
- Automatically scale model servers during traffic spikes
- Right-size pod resources based on actual usage
- Scale down during low-demand periods to save costs
- Handle bursty workloads without manual intervention

## Tasks

### Task 1: Environment Setup and Metrics Server

**TODO 1.1:** Install metrics-server (required for HPA)

```bash
# TODO: Check if metrics-server is installed
kubectl get deployment metrics-server -n kube-system

# If not installed, deploy it
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml

# For local clusters (minikube/kind), may need to disable TLS
kubectl patch deployment metrics-server -n kube-system --type='json' \
  -p='[{"op": "add", "path": "/spec/template/spec/containers/0/args/-", "value": "--kubelet-insecure-tls"}]'

# Wait for metrics-server to be ready
kubectl wait --for=condition=ready pod -l k8s-app=metrics-server -n kube-system --timeout=120s

# TODO: Verify metrics are available
kubectl top nodes
kubectl top pods -A
```

**TODO 1.2:** Create namespace for ML workloads

```yaml
# ml-platform-namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: ml-platform
  labels:
    name: ml-platform
---
apiVersion: v1
kind: ResourceQuota
metadata:
  name: ml-platform-quota
  namespace: ml-platform
spec:
  hard:
    requests.cpu: "20"
    requests.memory: "40Gi"
    limits.cpu: "40"
    limits.memory: "80Gi"
    pods: "50"
---
apiVersion: v1
kind: LimitRange
metadata:
  name: ml-platform-limits
  namespace: ml-platform
spec:
  limits:
  - max:
      cpu: "4"
      memory: "8Gi"
    min:
      cpu: "100m"
      memory: "128Mi"
    default:
      cpu: "500m"
      memory: "512Mi"
    defaultRequest:
      cpu: "200m"
      memory: "256Mi"
    type: Container
```

```bash
# TODO: Apply namespace configuration
kubectl apply -f ml-platform-namespace.yaml

# Verify
kubectl describe namespace ml-platform
kubectl get resourcequota -n ml-platform
kubectl get limitrange -n ml-platform
```

### Task 2: Horizontal Pod Autoscaler (HPA) - CPU-based

**TODO 2.1:** Deploy a sample ML model serving API

```yaml
# model-api-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fraud-detector-api
  namespace: ml-platform
  labels:
    app: fraud-detector
    tier: serving
spec:
  replicas: 2
  selector:
    matchLabels:
      app: fraud-detector
  template:
    metadata:
      labels:
        app: fraud-detector
    spec:
      containers:
      - name: api
        image: hashicorp/http-echo:latest
        args:
        - "-text=Fraud Detection API v1.0"
        ports:
        - containerPort: 5678
          name: http
        resources:
          requests:
            cpu: 200m
            memory: 256Mi
          limits:
            cpu: 500m
            memory: 512Mi
        # Simulate CPU-intensive inference
        lifecycle:
          postStart:
            exec:
              command:
              - /bin/sh
              - -c
              - |
                (while true; do
                  # Simulate periodic CPU load (10% baseline)
                  dd if=/dev/zero of=/dev/null bs=1M count=100 2>/dev/null
                  sleep 5
                done) &
---
apiVersion: v1
kind: Service
metadata:
  name: fraud-detector-api
  namespace: ml-platform
spec:
  selector:
    app: fraud-detector
  ports:
  - port: 80
    targetPort: 5678
  type: ClusterIP
```

```bash
# TODO: Deploy the application
kubectl apply -f model-api-deployment.yaml

# Verify deployment
kubectl get deployment fraud-detector-api -n ml-platform
kubectl get pods -n ml-platform -l app=fraud-detector

# Check current CPU usage
kubectl top pods -n ml-platform -l app=fraud-detector
```

**TODO 2.2:** Configure HPA based on CPU utilization

```yaml
# hpa-cpu.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: fraud-detector-hpa
  namespace: ml-platform
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: fraud-detector-api
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 50  # Scale when average CPU > 50%
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300  # Wait 5 min before scaling down
      policies:
      - type: Percent
        value: 50  # Remove max 50% of pods at once
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 0  # Scale up immediately
      policies:
      - type: Percent
        value: 100  # Double pods at once if needed
        periodSeconds: 60
      - type: Pods
        value: 4  # Or add max 4 pods at once
        periodSeconds: 60
      selectPolicy: Max  # Use the more aggressive policy
```

```bash
# TODO: Create HPA
kubectl apply -f hpa-cpu.yaml

# Check HPA status
kubectl get hpa fraud-detector-hpa -n ml-platform
kubectl describe hpa fraud-detector-hpa -n ml-platform

# Monitor in real-time
watch -n 2 'kubectl get hpa fraud-detector-hpa -n ml-platform'
```

**TODO 2.3:** Generate load and observe scaling

```bash
# TODO: Deploy load generator
kubectl run load-generator \
  --image=busybox:latest \
  --restart=Never \
  -n ml-platform \
  -- /bin/sh -c "while true; do wget -q -O- http://fraud-detector-api.ml-platform.svc.cluster.local; done"

# Monitor HPA scaling
kubectl get hpa fraud-detector-hpa -n ml-platform --watch

# Check pod count
kubectl get pods -n ml-platform -l app=fraud-detector

# View HPA events
kubectl describe hpa fraud-detector-hpa -n ml-platform | tail -n 20

# TODO: Stop load and observe scale-down
kubectl delete pod load-generator -n ml-platform

# Wait ~5 minutes and observe scale down
kubectl get hpa fraud-detector-hpa -n ml-platform --watch
```

### Task 3: HPA with Custom Metrics (Prometheus)

**TODO 3.1:** Install Prometheus and Prometheus Adapter

```bash
# TODO: Add Helm repos
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Install Prometheus
helm install prometheus prometheus-community/prometheus \
  --namespace monitoring \
  --create-namespace \
  --set server.persistentVolume.enabled=false \
  --set alertmanager.enabled=false

# Wait for Prometheus
kubectl wait --for=condition=ready pod -l app=prometheus -n monitoring --timeout=180s

# TODO: Install Prometheus Adapter
helm install prometheus-adapter prometheus-community/prometheus-adapter \
  --namespace monitoring \
  --set prometheus.url=http://prometheus-server.monitoring.svc.cluster.local \
  --set prometheus.port=80

# Verify adapter is serving custom metrics
kubectl get apiservices | grep custom.metrics
```

**TODO 3.2:** Deploy model API with Prometheus metrics

```yaml
# model-api-with-metrics.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: recommendation-api
  namespace: ml-platform
spec:
  replicas: 2
  selector:
    matchLabels:
      app: recommendation-api
  template:
    metadata:
      labels:
        app: recommendation-api
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "8080"
        prometheus.io/path: "/metrics"
    spec:
      containers:
      - name: api
        image: nginx:alpine
        ports:
        - containerPort: 8080
          name: metrics
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 300m
            memory: 256Mi
---
apiVersion: v1
kind: Service
metadata:
  name: recommendation-api
  namespace: ml-platform
  labels:
    app: recommendation-api
spec:
  selector:
    app: recommendation-api
  ports:
  - port: 80
    targetPort: 8080
    name: http
---
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: recommendation-api
  namespace: ml-platform
spec:
  selector:
    matchLabels:
      app: recommendation-api
  endpoints:
  - port: http
    interval: 30s
```

**TODO 3.3:** Configure HPA with custom metrics

```yaml
# hpa-custom-metrics.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: recommendation-hpa
  namespace: ml-platform
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: recommendation-api
  minReplicas: 2
  maxReplicas: 20
  metrics:
  # CPU metric
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70

  # Memory metric
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80

  # Custom metric: HTTP requests per second
  - type: Pods
    pods:
      metric:
        name: http_requests_per_second
      target:
        type: AverageValue
        averageValue: "100"  # Scale when > 100 req/s per pod

  # Custom metric: Inference latency (p95)
  - type: Pods
    pods:
      metric:
        name: inference_latency_p95
      target:
        type: AverageValue
        averageValue: "200m"  # Scale when p95 latency > 200ms

  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 25  # Remove 25% of pods at once
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 30
      policies:
      - type: Pods
        value: 5
        periodSeconds: 30
```

```bash
# TODO: Apply custom metrics HPA
kubectl apply -f hpa-custom-metrics.yaml

# Check available custom metrics
kubectl get --raw "/apis/custom.metrics.k8s.io/v1beta1" | jq .

# Describe HPA
kubectl describe hpa recommendation-hpa -n ml-platform
```

### Task 4: Vertical Pod Autoscaler (VPA)

**TODO 4.1:** Install VPA

```bash
# TODO: Clone VPA repository
git clone https://github.com/kubernetes/autoscaler.git
cd autoscaler/vertical-pod-autoscaler

# Install VPA
./hack/vpa-up.sh

# Verify VPA components
kubectl get pods -n kube-system | grep vpa

# VPA has 3 components:
# - recommender: Monitors resource usage and provides recommendations
# - updater: Evicts pods that need resource updates
# - admission-controller: Sets resource requests on new pods
```

**TODO 4.2:** Deploy workload with VPA

```yaml
# training-job-with-vpa.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: model-training-job
  namespace: ml-platform
spec:
  replicas: 1
  selector:
    matchLabels:
      app: model-training
  template:
    metadata:
      labels:
        app: model-training
    spec:
      containers:
      - name: trainer
        image: python:3.9-slim
        command:
        - /bin/bash
        - -c
        - |
          echo "Starting model training..."
          # Simulate varying resource usage
          while true; do
            python3 -c "
            import time
            import random
            # Simulate training epoch with varying memory
            data = [random.random() for _ in range(random.randint(1000000, 5000000))]
            print(f'Training epoch with {len(data)} samples')
            time.sleep(30)
            "
          done
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 1000m
            memory: 2Gi
---
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: model-training-vpa
  namespace: ml-platform
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: model-training-job
  updatePolicy:
    updateMode: "Auto"  # Can be: Off, Initial, Recreate, Auto
  resourcePolicy:
    containerPolicies:
    - containerName: trainer
      minAllowed:
        cpu: 100m
        memory: 128Mi
      maxAllowed:
        cpu: 2000m
        memory: 4Gi
      controlledResources:
      - cpu
      - memory
```

```bash
# TODO: Deploy with VPA
kubectl apply -f training-job-with-vpa.yaml

# Wait for VPA to gather data (5-10 minutes)
echo "Waiting for VPA recommendations..."
sleep 300

# TODO: Check VPA recommendations
kubectl describe vpa model-training-vpa -n ml-platform

# Look for:
# - Lower Bound: Minimum recommended resources
# - Target: Recommended resource requests
# - Upper Bound: Maximum recommended resources
# - Uncapped Target: Recommendation without policy limits

# View VPA status
kubectl get vpa model-training-vpa -n ml-platform -o yaml
```

**TODO 4.3:** Compare VPA update modes

```yaml
# vpa-modes-comparison.yaml
---
# Mode 1: "Off" - Only provide recommendations, don't apply
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: vpa-mode-off
  namespace: ml-platform
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: fraud-detector-api
  updatePolicy:
    updateMode: "Off"  # Just recommend, don't change anything
---
# Mode 2: "Initial" - Set resources on pod creation only
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: vpa-mode-initial
  namespace: ml-platform
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: recommendation-api
  updatePolicy:
    updateMode: "Initial"  # Apply only when pod is created
---
# Mode 3: "Recreate" - Evict and recreate pods with new resources
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: vpa-mode-recreate
  namespace: ml-platform
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: model-training-job
  updatePolicy:
    updateMode: "Recreate"  # Will restart pods to apply changes
---
# Mode 4: "Auto" - Automatic (currently same as Recreate)
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: vpa-mode-auto
  namespace: ml-platform
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: model-training-job
  updatePolicy:
    updateMode: "Auto"
```

```bash
# TODO: Apply different VPA modes
kubectl apply -f vpa-modes-comparison.yaml

# Compare recommendations
kubectl get vpa -n ml-platform
kubectl describe vpa vpa-mode-off -n ml-platform
```

### Task 5: Event-Driven Autoscaling with KEDA

**TODO 5.1:** Install KEDA

```bash
# TODO: Install KEDA with Helm
helm repo add kedacore https://kedacore.github.io/charts
helm repo update

helm install keda kedacore/keda \
  --namespace keda \
  --create-namespace

# Verify KEDA installation
kubectl get pods -n keda
```

**TODO 5.2:** Scale based on message queue length (simulate inference queue)

```yaml
# inference-queue-processor.yaml
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: batch-inference-processor
  namespace: ml-platform
spec:
  replicas: 1
  selector:
    matchLabels:
      app: batch-inference
  template:
    metadata:
      labels:
        app: batch-inference
    spec:
      containers:
      - name: processor
        image: busybox:latest
        command:
        - /bin/sh
        - -c
        - |
          while true; do
            echo "Processing inference batch..."
            sleep 10
          done
        resources:
          requests:
            cpu: 200m
            memory: 256Mi
---
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: batch-inference-scaler
  namespace: ml-platform
spec:
  scaleTargetRef:
    name: batch-inference-processor
  minReplicaCount: 0  # Scale to zero when no messages
  maxReplicaCount: 20
  pollingInterval: 30
  cooldownPeriod: 300
  triggers:
  # Example: Scale based on Prometheus metric
  - type: prometheus
    metadata:
      serverAddress: http://prometheus-server.monitoring.svc.cluster.local
      metricName: queue_depth
      query: sum(inference_queue_length)
      threshold: "10"  # Scale up if queue > 10 items per pod
  # Example: Scale based on CPU (same as HPA)
  - type: cpu
    metricType: Utilization
    metadata:
      value: "60"
```

**TODO 5.3:** Scale based on cron schedule

```yaml
# scheduled-training-scaler.yaml
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: scheduled-training-scaler
  namespace: ml-platform
spec:
  scaleTargetRef:
    name: model-training-job
  minReplicaCount: 0
  maxReplicaCount: 5
  triggers:
  # Scale up during business hours (more training demand)
  - type: cron
    metadata:
      timezone: America/New_York
      start: 0 9 * * 1-5  # 9 AM Mon-Fri
      end: 0 18 * * 1-5   # 6 PM Mon-Fri
      desiredReplicas: "3"
  # Scale down at night
  - type: cron
    metadata:
      timezone: America/New_York
      start: 0 22 * * *   # 10 PM every day
      end: 0 6 * * *      # 6 AM every day
      desiredReplicas: "0"
```

```bash
# TODO: Apply KEDA scalers
kubectl apply -f inference-queue-processor.yaml
kubectl apply -f scheduled-training-scaler.yaml

# Check KEDA scalers
kubectl get scaledobject -n ml-platform
kubectl describe scaledobject batch-inference-scaler -n ml-platform
```

### Task 6: Cluster Autoscaler Simulation

**TODO 6.1:** Understanding Cluster Autoscaler (CA)

```yaml
# large-workload-trigger-ca.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: large-training-job
  namespace: ml-platform
spec:
  replicas: 5
  selector:
    matchLabels:
      app: large-training
  template:
    metadata:
      labels:
        app: large-training
    spec:
      containers:
      - name: trainer
        image: busybox:latest
        command: ["sleep", "3600"]
        resources:
          requests:
            cpu: 4000m  # Request large resources to trigger CA
            memory: 8Gi
          limits:
            cpu: 4000m
            memory: 8Gi
```

```bash
# TODO: Describe how Cluster Autoscaler works
cat << 'EOF' > cluster-autoscaler-guide.md
# Cluster Autoscaler for ML Workloads

## How it Works
1. **Scale Up**: When pods are pending due to insufficient cluster resources
2. **Scale Down**: When nodes are underutilized for extended period (10+ min)

## Configuration Considerations for ML

### Node Pools
- **CPU-only pool**: For serving, feature stores, general workloads
  - Min: 2 nodes, Max: 20 nodes
  - Instance: 4 vCPU, 16GB RAM

- **GPU pool**: For training and GPU inference
  - Min: 0 nodes, Max: 10 nodes (expensive!)
  - Instance: 8 vCPU, 30GB RAM, 1x NVIDIA T4

### Important Annotations

Prevent node scale-down:
```yaml
annotations:
  cluster-autoscaler.kubernetes.io/safe-to-evict: "false"
```

Priority classes for training jobs:
```yaml
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata:
  name: high-priority-training
value: 1000
globalDefault: false
description: "High priority for urgent training jobs"
```

### Cost Optimization
- Use **spot/preemptible instances** for fault-tolerant training
- Set **aggressive scale-down delays** for CPU pools (5 min)
- Set **conservative scale-down** for GPU pools (30 min) to avoid churn
- Use **node affinity** to prefer cheaper instance types

EOF

cat cluster-autoscaler-guide.md
```

**TODO 6.2:** Configure Pod Disruption Budgets for safe scaling

```yaml
# pod-disruption-budgets.yaml
---
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: fraud-detector-pdb
  namespace: ml-platform
spec:
  minAvailable: 1  # At least 1 pod must be available
  selector:
    matchLabels:
      app: fraud-detector
---
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: recommendation-pdb
  namespace: ml-platform
spec:
  maxUnavailable: 30%  # Max 30% of pods can be unavailable
  selector:
    matchLabels:
      app: recommendation-api
```

```bash
# TODO: Apply PDBs
kubectl apply -f pod-disruption-budgets.yaml

# Verify
kubectl get pdb -n ml-platform
```

### Task 7: Autoscaling Best Practices and Monitoring

**TODO 7.1:** Create comprehensive monitoring dashboard

```yaml
# autoscaling-servicemonitor.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: autoscaling-dashboard
  namespace: monitoring
data:
  dashboard.json: |
    {
      "title": "ML Platform Autoscaling",
      "panels": [
        {
          "title": "HPA Current Replicas",
          "targets": [
            {
              "expr": "kube_horizontalpodautoscaler_status_current_replicas"
            }
          ]
        },
        {
          "title": "HPA Desired Replicas",
          "targets": [
            {
              "expr": "kube_horizontalpodautoscaler_status_desired_replicas"
            }
          ]
        },
        {
          "title": "HPA CPU Utilization",
          "targets": [
            {
              "expr": "kube_horizontalpodautoscaler_status_current_metrics_value{metric_name='cpu'}"
            }
          ]
        },
        {
          "title": "VPA Recommendations vs Current",
          "targets": [
            {
              "expr": "kube_verticalpodautoscaler_status_recommendation_containerrecommendations_target"
            }
          ]
        }
      ]
    }
```

**TODO 7.2:** Create autoscaling test suite

```bash
# TODO: Create load testing script
cat > test_autoscaling.sh << 'EOF'
#!/bin/bash
# Autoscaling Test Suite for ML Platform

NAMESPACE="ml-platform"

echo "=== ML Platform Autoscaling Test Suite ==="

# Test 1: HPA CPU-based scaling
echo -e "\n[Test 1] HPA CPU-based Scaling"
echo "Current state:"
kubectl get hpa fraud-detector-hpa -n $NAMESPACE

echo "Generating load..."
kubectl run load-test-1 --image=busybox:latest --restart=Never -n $NAMESPACE -- \
  /bin/sh -c "while true; do wget -q -O- http://fraud-detector-api; done" &

LOAD_PID=$!
sleep 120  # Wait 2 minutes

echo "After load:"
kubectl get hpa fraud-detector-hpa -n $NAMESPACE
kubectl get pods -n $NAMESPACE -l app=fraud-detector

# Cleanup
kill $LOAD_PID 2>/dev/null
kubectl delete pod load-test-1 -n $NAMESPACE --ignore-not-found

# Test 2: VPA recommendations
echo -e "\n[Test 2] VPA Recommendations"
kubectl describe vpa -n $NAMESPACE | grep -A 10 "Recommendation:"

# Test 3: KEDA scaling
echo -e "\n[Test 3] KEDA ScaledObjects"
kubectl get scaledobject -n $NAMESPACE

# Test 4: Resource utilization
echo -e "\n[Test 4] Current Resource Utilization"
kubectl top pods -n $NAMESPACE --sort-by=cpu
kubectl top pods -n $NAMESPACE --sort-by=memory

echo -e "\n=== Test Complete ==="
EOF

chmod +x test_autoscaling.sh

# TODO: Run tests
# ./test_autoscaling.sh
```

**TODO 7.3:** Document autoscaling decision matrix

```bash
# TODO: Create decision guide
cat > autoscaling_decision_matrix.md << 'EOF'
# Autoscaling Decision Matrix for ML Workloads

## When to Use Each Autoscaler

| Workload Type | HPA | VPA | KEDA | Cluster Autoscaler |
|---------------|-----|-----|------|-------------------|
| **Model Serving API** | ✅ Primary | ⚠️ Monitor only | ✅ For queue-based | ✅ If on cloud |
| **Batch Inference** | ❌ Not suitable | ✅ Yes | ✅ Primary | ✅ Yes |
| **Training Jobs** | ❌ Not suitable | ✅ Yes | ✅ For scheduling | ✅ For GPU nodes |
| **Feature Store** | ✅ Based on hits | ✅ Memory usage | ❌ Not needed | ✅ Yes |
| **Notebooks/Dev** | ❌ Not suitable | ⚠️ Risky | ❌ Not needed | ✅ For spot nodes |

## Scaling Recommendations by Use Case

### Real-Time Model Serving
```yaml
Strategy: HPA with custom metrics + VPA in "Off" mode + PDB
Metrics:
  - HTTP requests per second (target: 100 req/s/pod)
  - Inference latency p95 (target: <200ms)
  - CPU utilization (target: 70%)
Scale: 2-20 replicas
Scale-down delay: 5 minutes
```

### Batch Inference Processing
```yaml
Strategy: KEDA with message queue + VPA in "Auto" mode
Metrics:
  - Queue depth (target: 10 messages/pod)
  - Or schedule-based (run nightly 2-6 AM)
Scale: 0-50 replicas (scale to zero when idle)
```

### Training Workloads
```yaml
Strategy: VPA + KEDA cron + Cluster Autoscaler
Metrics:
  - Schedule-based scaling (business hours)
  - Resource recommendations from VPA
Scale: 0-10 GPU nodes (expensive!)
Node pool: Spot/preemptible instances
```

### Feature Store (Redis)
```yaml
Strategy: HPA on memory + VPA
Metrics:
  - Memory utilization (target: 80%)
  - Cache hit rate (target: >90%)
Scale: 3-15 replicas
Stateful: Use StatefulSet, careful with scale-down
```

## Anti-Patterns to Avoid

❌ **Don't**: Use HPA and VPA together on same deployment (conflicts)
✅ **Do**: Use VPA in "Off" mode for recommendations, manually tune HPA

❌ **Don't**: Set minReplicas=0 for critical services
✅ **Do**: Keep at least 2 replicas for high-availability

❌ **Don't**: Use aggressive scale-down (< 2 min) for ML workloads
✅ **Do**: Use 5-10 min stabilization to avoid thrashing

❌ **Don't**: Ignore PodDisruptionBudgets
✅ **Do**: Set PDBs to ensure minimum availability during scale-down

❌ **Don't**: Forget resource requests (HPA won't work)
✅ **Do**: Always set CPU/memory requests based on profiling
EOF

cat autoscaling_decision_matrix.md
```

## Deliverables

Submit a repository with:

1. **Kubernetes Manifests**
   - HPA configurations (CPU-based and custom metrics)
   - VPA configurations with different update modes
   - KEDA ScaledObjects for event-driven scaling
   - PodDisruptionBudgets for safe scaling
   - Resource quotas and limit ranges

2. **Testing Scripts**
   - `test_autoscaling.sh` - Automated test suite
   - Load generation scripts
   - Results showing scaling behavior

3. **Documentation**
   - `AUTOSCALING_GUIDE.md` - Comprehensive guide with decision matrix
   - Diagrams showing scaling architecture
   - Performance benchmarks (scaling latency, cost savings)
   - Troubleshooting guide for common issues

4. **Monitoring Configuration**
   - Prometheus rules for autoscaling alerts
   - Grafana dashboard JSON for visualization

## Success Criteria

- [ ] Metrics-server installed and providing pod metrics
- [ ] HPA successfully scales deployment based on CPU load
- [ ] HPA configured with custom Prometheus metrics
- [ ] VPA provides resource recommendations
- [ ] KEDA installed and scaling based on events/schedule
- [ ] PodDisruptionBudgets prevent unsafe evictions
- [ ] Load testing demonstrates automatic scale-up and scale-down
- [ ] Documentation clearly explains when to use each autoscaler
- [ ] Monitoring dashboard shows autoscaling metrics
- [ ] Scale-down behavior is stable (no thrashing)

## Bonus Challenges

1. **Multi-Metric HPA**: Configure HPA with 3+ different metrics and observe which triggers first
2. **Custom Metrics Adapter**: Implement custom metrics from application (e.g., queue depth from app logs)
3. **GPU Autoscaling**: Simulate GPU node autoscaling with node affinity and taints
4. **Cost Analysis**: Calculate cost savings from autoscaling vs fixed capacity
5. **Predictive Scaling**: Use historical metrics to predict load and pre-scale
6. **Cross-Region Scaling**: Design multi-cluster autoscaling strategy

## Resources

- [Kubernetes HPA Documentation](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/)
- [Vertical Pod Autoscaler](https://github.com/kubernetes/autoscaler/tree/master/vertical-pod-autoscaler)
- [KEDA Documentation](https://keda.sh/docs/)
- [Prometheus Adapter](https://github.com/kubernetes-sigs/prometheus-adapter)
- [GKE Cluster Autoscaler](https://cloud.google.com/kubernetes-engine/docs/concepts/cluster-autoscaler)

## Evaluation Rubric

| Criteria | Points |
|----------|--------|
| Metrics-server setup and verification | 10 |
| HPA configuration (CPU-based) | 15 |
| HPA with custom metrics (Prometheus) | 20 |
| VPA implementation and recommendations | 15 |
| KEDA event-driven scaling | 15 |
| Testing and load generation | 10 |
| Documentation and decision matrix | 10 |
| Monitoring and observability | 5 |

**Total: 100 points**
