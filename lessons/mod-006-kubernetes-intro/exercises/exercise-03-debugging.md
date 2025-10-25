# Exercise 03: Debugging Kubernetes Issues

## Overview

In this hands-on exercise, you'll troubleshoot various Kubernetes issues using real-world scenarios. You'll learn systematic debugging approaches, use kubectl effectively for investigation, and develop troubleshooting intuition essential for production environments.

## Learning Objectives

By completing this exercise, you will:
- Apply systematic debugging methodology
- Diagnose common Pod failures
- Troubleshoot networking issues
- Resolve storage problems
- Debug configuration errors
- Use kubectl commands effectively for investigation
- Read and interpret logs and events
- Fix performance issues

## Prerequisites

- Completed Exercises 01-02
- Completed Lecture 04 (Kubernetes Operations)
- kubectl configured
- Access to a Kubernetes cluster
- Patience and determination!

## Setup

```bash
# Create namespace for debugging exercises
kubectl create namespace debug-lab
kubectl config set-context --current --namespace=debug-lab

# Verify setup
kubectl get namespace debug-lab
```

## Debugging Methodology

Before starting, remember the systematic approach:

```
1. Identify the symptom
2. Check Pod status
3. Describe resources (read events!)
4. Check logs
5. Verify configuration
6. Test connectivity
7. Check resources (CPU/memory/disk)
8. Form hypothesis
9. Test and verify fix
```

## Scenario 1: Image Pull Failure

### Problem Description

A new application deployment fails to start. Pods are stuck in `ImagePullBackOff`.

### Deploy the Broken Application

```bash
cat <<EOF | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: broken-image-app
spec:
  replicas: 2
  selector:
    matchLabels:
      app: broken-image
  template:
    metadata:
      labels:
        app: broken-image
    spec:
      containers:
      - name: app
        image: nginx:nonexistent-tag-12345
        ports:
        - containerPort: 80
EOF
```

### Your Task

1. **Identify the issue**:
```bash
# Check Pod status
kubectl get pods

# What status do you see?
```

2. **Investigate**:
```bash
# Describe a Pod
POD_NAME=$(kubectl get pods -l app=broken-image -o jsonpath='{.items[0].metadata.name}')
kubectl describe pod $POD_NAME

# What error message is in the Events section?
```

3. **Fix the issue**:
```bash
# Update the deployment with correct image
kubectl set image deployment/broken-image-app app=nginx:1.21

# Verify fix
kubectl rollout status deployment/broken-image-app
kubectl get pods
```

### Questions

1. What specific error message indicated the problem?
2. How can you prevent this in production?
3. What would you do if the image requires private registry authentication?

## Scenario 2: Application Crash Loop

### Problem Description

An application keeps crashing and restarting (CrashLoopBackOff).

### Deploy the Crashing Application

```bash
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: crashing-app
spec:
  containers:
  - name: app
    image: busybox
    command: ["/bin/sh"]
    args: ["-c", "echo Starting app; sleep 5; exit 1"]
  restartPolicy: Always
EOF
```

### Your Task

1. **Observe the crash loop**:
```bash
# Watch the Pod restart
kubectl get pod crashing-app -w

# After seeing a few restarts, press Ctrl+C
```

2. **Check logs**:
```bash
# View current logs
kubectl logs crashing-app

# View previous container logs (after crash)
kubectl logs crashing-app --previous

# What do the logs show?
```

3. **Describe the Pod**:
```bash
kubectl describe pod crashing-app

# Check:
# - Restart count
# - Last State (why it terminated)
# - Exit code
```

4. **Fix the issue**:
```bash
# Delete the broken Pod
kubectl delete pod crashing-app

# Create working version
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: working-app
spec:
  containers:
  - name: app
    image: busybox
    command: ["/bin/sh"]
    args: ["-c", "echo Starting app; while true; do echo Running; sleep 10; done"]
  restartPolicy: Always
EOF

# Verify it's working
kubectl get pod working-app
kubectl logs working-app
```

### Questions

1. What exit code did the container return?
2. How does Kubernetes handle container crashes?
3. What's the backoff timing for restarts?

## Scenario 3: Pending Pod (Resource Constraints)

### Problem Description

A Pod is stuck in `Pending` state and never starts.

### Deploy Resource-Heavy Pod

```bash
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: resource-heavy
spec:
  containers:
  - name: app
    image: nginx
    resources:
      requests:
        memory: "100Gi"  # Unrealistic requirement
        cpu: "50"
EOF
```

### Your Task

1. **Check status**:
```bash
kubectl get pod resource-heavy

# Status should be: Pending
```

2. **Investigate**:
```bash
kubectl describe pod resource-heavy

# Look for scheduling events
# What's the error message?
```

3. **Check node resources**:
```bash
kubectl top nodes

# Compare available resources to Pod requests
```

4. **Fix the issue**:
```bash
# Delete the Pod
kubectl delete pod resource-heavy

# Create with realistic resources
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: resource-realistic
spec:
  containers:
  - name: app
    image: nginx
    resources:
      requests:
        memory: "128Mi"
        cpu: "100m"
      limits:
        memory: "256Mi"
        cpu: "200m"
EOF

kubectl get pod resource-realistic
```

### Questions

1. Why couldn't the Pod be scheduled?
2. How do you find available cluster resources?
3. What's the difference between requests and limits?

## Scenario 4: Service Not Routing Traffic

### Problem Description

A Service exists, but traffic isn't reaching the Pods.

### Deploy Application and Service

```bash
# Deploy Pods with WRONG labels
cat <<EOF | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: webapp
  template:
    metadata:
      labels:
        app: webapp  # Note the label
    spec:
      containers:
      - name: nginx
        image: nginx
        ports:
        - containerPort: 80
---
apiVersion: v1
kind: Service
metadata:
  name: web-service
spec:
  selector:
    app: web-app  # Different label!
  ports:
  - port: 80
    targetPort: 80
EOF
```

### Your Task

1. **Test connectivity**:
```bash
# Try to access the service
kubectl run test-pod --rm -it --image=busybox -- wget -qO- http://web-service

# It should timeout or fail
```

2. **Investigate**:
```bash
# Check Service
kubectl get service web-service

# Check Endpoints
kubectl get endpoints web-service

# Are there any endpoints listed?
```

3. **Compare labels**:
```bash
# Service selector
kubectl get service web-service -o jsonpath='{.spec.selector}'

# Pod labels
kubectl get pods -l app=webapp --show-labels

# Do they match?
```

4. **Fix the mismatch**:
```bash
# Option 1: Fix the Service selector
kubectl patch service web-service -p '{"spec":{"selector":{"app":"webapp"}}}'

# Verify endpoints are now populated
kubectl get endpoints web-service

# Test again
kubectl run test-pod --rm -it --image=busybox -- wget -qO- http://web-service

# Should work now!
```

### Questions

1. Why were no endpoints created initially?
2. How does Kubernetes populate Service endpoints?
3. What's the relationship between Service selectors and Pod labels?

## Scenario 5: DNS Resolution Failure

### Problem Description

Pods cannot resolve service names via DNS.

### Setup

```bash
# Create a service
kubectl create deployment dns-test --image=nginx
kubectl expose deployment dns-test --port=80
```

### Your Task

1. **Test DNS resolution**:
```bash
# Create test Pod
kubectl run dns-client --rm -it --image=busybox -- sh

# Inside the Pod, test DNS:
nslookup dns-test

# If it fails, you have a DNS problem!
# Exit the Pod
exit
```

2. **Check CoreDNS**:
```bash
# Check CoreDNS Pods
kubectl get pods -n kube-system -l k8s-app=kube-dns

# Check CoreDNS logs
kubectl logs -n kube-system -l k8s-app=kube-dns --tail=50

# Any errors?
```

3. **Test DNS manually**:
```bash
# Get CoreDNS service IP
kubectl get service -n kube-system kube-dns

# Create test Pod with correct DNS config
kubectl run dns-debug --rm -it --image=busybox -- sh

# Inside Pod:
cat /etc/resolv.conf
# Should show:
# nameserver 10.96.0.10 (or similar)
# search default.svc.cluster.local svc.cluster.local cluster.local

nslookup kubernetes.default
nslookup dns-test.debug-lab.svc.cluster.local

exit
```

### Questions

1. What nameserver IP is configured in /etc/resolv.conf?
2. What search domains are configured?
3. How would you troubleshoot a CoreDNS issue?

## Scenario 6: Liveness Probe Killing Container

### Problem Description

Container keeps restarting due to failing liveness probe.

### Deploy Application with Aggressive Probe

```bash
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: probe-issue
spec:
  containers:
  - name: slow-starter
    image: nginx
    livenessProbe:
      httpGet:
        path: /
        port: 80
      initialDelaySeconds: 1  # Too short!
      periodSeconds: 2
      failureThreshold: 2
    readinessProbe:
      httpGet:
        path: /
        port: 80
      initialDelaySeconds: 1
      periodSeconds: 2
EOF
```

### Your Task

1. **Monitor the Pod**:
```bash
# Watch Pod status
kubectl get pod probe-issue -w

# May see restarts
```

2. **Check events**:
```bash
kubectl describe pod probe-issue

# Look for "Liveness probe failed" or "Unhealthy"
```

3. **Fix the probe**:
```bash
# Delete Pod
kubectl delete pod probe-issue

# Recreate with better probe config
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: probe-fixed
spec:
  containers:
  - name: slow-starter
    image: nginx
    livenessProbe:
      httpGet:
        path: /
        port: 80
      initialDelaySeconds: 15  # Give it time to start
      periodSeconds: 10
      failureThreshold: 3
    readinessProbe:
      httpGet:
        path: /
        port: 80
      initialDelaySeconds: 5
      periodSeconds: 5
EOF

kubectl get pod probe-fixed
```

### Questions

1. Why did the liveness probe fail initially?
2. What's the purpose of `initialDelaySeconds`?
3. When should you use liveness vs readiness probes?

## Scenario 7: ConfigMap Not Found

### Problem Description

Pod fails to start due to missing ConfigMap.

### Deploy Pod Referencing Missing ConfigMap

```bash
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: config-missing
spec:
  containers:
  - name: app
    image: nginx
    envFrom:
    - configMapRef:
        name: app-config  # Doesn't exist!
EOF
```

### Your Task

1. **Check Pod status**:
```bash
kubectl get pod config-missing

# May be in CreateContainerConfigError
```

2. **Investigate**:
```bash
kubectl describe pod config-missing

# Look for: "configmap \"app-config\" not found"
```

3. **Fix by creating ConfigMap**:
```bash
# Create the missing ConfigMap
kubectl create configmap app-config \
  --from-literal=APP_NAME=myapp \
  --from-literal=LOG_LEVEL=info

# Delete and recreate Pod (or just wait for kubelet to retry)
kubectl delete pod config-missing
kubectl apply -f - <<EOF
apiVersion: v1
kind: Pod
metadata:
  name: config-fixed
spec:
  containers:
  - name: app
    image: nginx
    envFrom:
    - configMapRef:
        name: app-config
EOF

# Verify
kubectl get pod config-fixed
kubectl exec config-fixed -- env | grep APP_
```

### Questions

1. What error indicated the missing ConfigMap?
2. Can a Pod start if optional ConfigMap is missing?
3. How do you make ConfigMap reference optional?

## Scenario 8: Persistent Volume Issue

### Problem Description

Pod stuck in `ContainerCreating` due to volume mount issue.

### Create PVC Without Available PV

```bash
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: missing-pvc
spec:
  accessModes:
  - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
  storageClassName: nonexistent-storage-class
---
apiVersion: v1
kind: Pod
metadata:
  name: storage-issue
spec:
  containers:
  - name: app
    image: nginx
    volumeMounts:
    - name: data
      mountPath: /data
  volumes:
  - name: data
    persistentVolumeClaim:
      claimName: missing-pvc
EOF
```

### Your Task

1. **Check PVC status**:
```bash
kubectl get pvc missing-pvc

# Status: Pending
```

2. **Check Pod status**:
```bash
kubectl get pod storage-issue

# Status: ContainerCreating
```

3. **Investigate**:
```bash
# Describe PVC
kubectl describe pvc missing-pvc

# Note: no matching StorageClass

# Describe Pod
kubectl describe pod storage-issue

# Look for volume mount errors
```

4. **Fix by using existing StorageClass**:
```bash
# List available StorageClasses
kubectl get storageclass

# Delete and recreate with correct StorageClass
kubectl delete pod storage-issue
kubectl delete pvc missing-pvc

cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: working-pvc
spec:
  accessModes:
  - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
  # Remove storageClassName or use existing one
---
apiVersion: v1
kind: Pod
metadata:
  name: storage-working
spec:
  containers:
  - name: app
    image: nginx
    volumeMounts:
    - name: data
      mountPath: /data
  volumes:
  - name: data
    persistentVolumeClaim:
      claimName: working-pvc
EOF

# Wait for PVC to bind
kubectl get pvc -w

# Check Pod
kubectl get pod storage-working
```

### Questions

1. Why was the PVC stuck in Pending?
2. How do you check available StorageClasses?
3. What's dynamic provisioning?

## Scenario 9: Resource Limit OOMKilled

### Problem Description

Container keeps getting killed due to out of memory.

### Deploy Memory-Hungry App

```bash
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: memory-hog
spec:
  containers:
  - name: app
    image: polinux/stress
    command: ["stress"]
    args: ["--vm", "1", "--vm-bytes", "300M"]  # Try to allocate 300MB
    resources:
      requests:
        memory: "128Mi"
      limits:
        memory: "256Mi"  # Will be killed at 256MB
EOF
```

### Your Task

1. **Watch the Pod**:
```bash
kubectl get pod memory-hog -w

# May see OOMKilled status
```

2. **Check events**:
```bash
kubectl describe pod memory-hog

# Look for: "OOMKilled" or "Memory cgroup out of memory"
```

3. **Check logs** (if available):
```bash
kubectl logs memory-hog
```

4. **Fix by increasing limits**:
```bash
kubectl delete pod memory-hog

cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: memory-adequate
spec:
  containers:
  - name: app
    image: polinux/stress
    command: ["stress"]
    args: ["--vm", "1", "--vm-bytes", "300M", "--vm-hang", "60"]
    resources:
      requests:
        memory: "256Mi"
      limits:
        memory: "512Mi"  # Enough headroom
EOF

kubectl get pod memory-adequate
```

### Questions

1. What happens when a container exceeds memory limits?
2. What happens when it exceeds CPU limits?
3. How do you prevent OOMKilled?

## Scenario 10: Network Policy Blocking Traffic

### Problem Description

Pods cannot communicate due to Network Policy.

### Deploy Restrictive Network Policy

```bash
# Deploy two apps
kubectl create deployment frontend --image=nginx
kubectl create deployment backend --image=nginx
kubectl expose deployment backend --port=80

# Apply restrictive policy
cat <<EOF | kubectl apply -f -
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-all
spec:
  podSelector: {}  # Applies to all Pods
  policyTypes:
  - Ingress
  - Egress
EOF
```

### Your Task

1. **Test connectivity** (should fail):
```bash
kubectl run test --rm -it --image=busybox -- wget -qO- --timeout=2 http://backend

# Should timeout
```

2. **Check Network Policies**:
```bash
kubectl get networkpolicy

kubectl describe networkpolicy deny-all
```

3. **Fix by allowing necessary traffic**:
```bash
# Delete restrictive policy
kubectl delete networkpolicy deny-all

# Create specific policy
cat <<EOF | kubectl apply -f -
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-backend
spec:
  podSelector:
    matchLabels:
      app: backend
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: frontend
    ports:
    - protocol: TCP
      port: 80
EOF

# Label frontend Pod
kubectl label pod -l app=frontend app=frontend

# Test again
kubectl run test --rm -it --image=busybox -l app=frontend -- wget -qO- http://backend

# Should work now
```

### Questions

1. How do Network Policies work?
2. What's the default behavior without policies?
3. How do you debug network policy issues?

## Comprehensive Debugging Challenge

### Multi-Problem Scenario

Deploy this broken multi-tier application and fix ALL issues:

```bash
cat <<EOF | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: challenge-frontend
spec:
  replicas: 2
  selector:
    matchLabels:
      tier: frontend
  template:
    metadata:
      labels:
        app: webapp
        tier: frontend
    spec:
      containers:
      - name: web
        image: nginx:invalid
        ports:
        - containerPort: 80
        resources:
          requests:
            memory: "50Mi"
            cpu: "50m"
          limits:
            memory: "100Mi"
            cpu: "100m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 2
          periodSeconds: 3
        env:
        - name: BACKEND_URL
          valueFrom:
            configMapKeyRef:
              name: app-settings
              key: backend_url
---
apiVersion: v1
kind: Service
metadata:
  name: frontend-service
spec:
  selector:
    app: frontend-app
  ports:
  - port: 80
    targetPort: 80
EOF
```

### Your Tasks

1. Find and fix the image issue
2. Create the missing ConfigMap
3. Fix the liveness probe
4. Fix the Service selector
5. Verify everything works

### Solution Verification

When fixed, this should work:
```bash
kubectl run test --rm -it --image=busybox -- wget -qO- http://frontend-service
```

## Cleanup

```bash
# Delete all resources
kubectl delete all --all -n debug-lab
kubectl delete pvc --all -n debug-lab
kubectl delete configmap --all -n debug-lab
kubectl delete networkpolicy --all -n debug-lab

# Delete namespace
kubectl delete namespace debug-lab

# Switch to default namespace
kubectl config set-context --current --namespace=default
```

## Key Takeaways

### Debugging Checklist

For any issue, always:
1. **Check status**: `kubectl get pods`
2. **Read events**: `kubectl describe pod <name>`
3. **View logs**: `kubectl logs <pod> [--previous]`
4. **Check config**: Verify manifests, ConfigMaps, Secrets
5. **Test connectivity**: Use test Pods
6. **Check resources**: `kubectl top pods/nodes`
7. **Verify labels/selectors**: Match Service to Pods

### Common Issue Patterns

| Symptom | Likely Cause | First Check |
|---------|--------------|-------------|
| ImagePullBackOff | Wrong image/tag | `describe pod` events |
| CrashLoopBackOff | App crashing | `logs --previous` |
| Pending | No resources/PVC | `describe pod` |
| Not routing traffic | Label mismatch | `get endpoints` |
| ContainerCreating | Volume/config issue | `describe pod` events |
| OOMKilled | Memory exceeded | `describe pod` last state |
| DNS fails | CoreDNS issue | Check CoreDNS Pods |

### Pro Tips

1. **Events are gold**: Always read the Events section
2. **Labels matter**: Double-check label selectors
3. **Logs before crashes**: Use `--previous` flag
4. **Test in isolation**: Use temporary test Pods
5. **Watch resources**: Use `-w` to see changes
6. **Use describe liberally**: It shows most issues
7. **Check the obvious**: Image names, typos, indentation

## Additional Resources

- Kubernetes Debugging Guide: https://kubernetes.io/docs/tasks/debug/
- Application Introspection and Debugging: https://kubernetes.io/docs/tasks/debug-application-cluster/
- Debug Running Pods: https://kubernetes.io/docs/tasks/debug-application-cluster/debug-running-pod/

---

**Congratulations!** You've completed the debugging exercise. You now have hands-on experience troubleshooting real Kubernetes issues. These skills are essential for maintaining production clusters.

Remember: Systematic debugging beats random guessing every time!
