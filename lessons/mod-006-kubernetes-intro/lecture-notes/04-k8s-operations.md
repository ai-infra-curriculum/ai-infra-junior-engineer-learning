# Lecture 04: Kubernetes Operations

## Table of Contents
1. [Introduction](#introduction)
2. [kubectl Essentials](#kubectl-essentials)
3. [Debugging Pods and Deployments](#debugging-pods-and-deployments)
4. [Logs and Events](#logs-and-events)
5. [Executing Commands in Containers](#executing-commands-in-containers)
6. [Resource Monitoring](#resource-monitoring)
7. [Troubleshooting Common Issues](#troubleshooting-common-issues)
8. [kubectl Productivity Tips](#kubectl-productivity-tips)
9. [Cluster Maintenance](#cluster-maintenance)
10. [Security Operations](#security-operations)
11. [Summary and Key Takeaways](#summary-and-key-takeaways)

## Introduction

Understanding Kubernetes architecture and how to deploy applications is essential, but day-to-day operations require a different set of skills. This lecture covers the practical operations tasks you'll perform regularly as an AI infrastructure engineer: debugging failing Pods, viewing logs, monitoring resources, and troubleshooting issues.

### Learning Objectives

By the end of this lecture, you will:
- Master essential kubectl commands for daily operations
- Debug failing Pods and Deployments effectively
- View and analyze logs and events
- Execute commands in running containers
- Monitor resource usage across the cluster
- Troubleshoot common Kubernetes issues
- Use kubectl efficiently with aliases and shortcuts
- Perform basic cluster maintenance tasks
- Apply security best practices in operations

### Prerequisites
- Lecture 01-03 (Architecture, Deployments, Helm)
- kubectl installed and configured
- Access to a Kubernetes cluster
- Basic Linux command-line skills

## kubectl Essentials

### kubectl Context and Configuration

kubectl uses kubeconfig files to connect to clusters.

```bash
# View current context
kubectl config current-context

# List all contexts
kubectl config get-contexts

# Switch context
kubectl config use-context production-cluster

# View kubeconfig
kubectl config view

# Set default namespace
kubectl config set-context --current --namespace=production
```

**Kubeconfig Structure**:
```yaml
# ~/.kube/config
apiVersion: v1
kind: Config
clusters:
- cluster:
    server: https://k8s.example.com:6443
    certificate-authority-data: <base64-cert>
  name: production-cluster
contexts:
- context:
    cluster: production-cluster
    namespace: default
    user: admin-user
  name: production
current-context: production
users:
- name: admin-user
  user:
    client-certificate-data: <base64-cert>
    client-key-data: <base64-key>
```

### Basic kubectl Commands

**Get Resources**:
```bash
# List resources
kubectl get pods
kubectl get deployments
kubectl get services
kubectl get nodes

# All resources
kubectl get all

# All resources in all namespaces
kubectl get all --all-namespaces
kubectl get all -A  # shorthand

# Wide output (more info)
kubectl get pods -o wide

# JSON output
kubectl get pod nginx -o json

# YAML output
kubectl get pod nginx -o yaml

# Custom columns
kubectl get pods -o custom-columns=NAME:.metadata.name,STATUS:.status.phase,NODE:.spec.nodeName

# JSONPath queries
kubectl get pods -o jsonpath='{.items[*].metadata.name}'

# Watch for changes
kubectl get pods -w
```

**Describe Resources**:
```bash
# Detailed information including events
kubectl describe pod nginx-pod
kubectl describe deployment nginx-deployment
kubectl describe node worker-1

# Multiple resources
kubectl describe pods
```

**Create/Apply Resources**:
```bash
# Create from file
kubectl create -f manifest.yaml

# Apply (create or update)
kubectl apply -f manifest.yaml

# Apply directory
kubectl apply -f ./manifests/

# Apply URL
kubectl apply -f https://example.com/manifest.yaml

# Create from command line
kubectl create deployment nginx --image=nginx
kubectl create service clusterip nginx --tcp=80:80
```

**Delete Resources**:
```bash
# Delete by name
kubectl delete pod nginx-pod

# Delete from file
kubectl delete -f manifest.yaml

# Delete all pods with label
kubectl delete pods -l app=nginx

# Delete all resources in namespace
kubectl delete all --all -n my-namespace

# Force delete (skip graceful termination)
kubectl delete pod nginx-pod --force --grace-period=0
```

**Edit Resources**:
```bash
# Edit in-place (opens editor)
kubectl edit deployment nginx-deployment

# Edit with specific editor
KUBE_EDITOR="nano" kubectl edit pod nginx-pod

# Patch resource
kubectl patch deployment nginx -p '{"spec":{"replicas":5}}'
```

### Resource Shortcuts

```bash
# Common shortcuts
po    # pods
deploy # deployments
svc   # services
ns    # namespaces
no    # nodes
pv    # persistentvolumes
pvc   # persistentvolumeclaims
cm    # configmaps
sa    # serviceaccounts

# Examples
kubectl get po
kubectl describe deploy nginx
kubectl delete svc nginx
```

### Namespace Operations

```bash
# Create namespace
kubectl create namespace development

# List namespaces
kubectl get namespaces
kubectl get ns

# Set default namespace
kubectl config set-context --current --namespace=development

# Get resources from specific namespace
kubectl get pods -n production

# Get resources from all namespaces
kubectl get pods --all-namespaces
kubectl get pods -A
```

## Debugging Pods and Deployments

### Pod Status and Phases

**Pod Phases**:
- **Pending**: Pod accepted but not yet scheduled or containers not created
- **Running**: Pod bound to node, containers created
- **Succeeded**: All containers terminated successfully
- **Failed**: All containers terminated, at least one failed
- **Unknown**: Pod state cannot be determined

**Container States**:
- **Waiting**: Container not yet running (pulling image, etc.)
- **Running**: Container is executing
- **Terminated**: Container finished execution

### Debugging Workflow

```
1. Check Pod status
   ↓
2. Describe Pod (view events)
   ↓
3. Check logs
   ↓
4. Check resource constraints
   ↓
5. Check node health
   ↓
6. Exec into container (if running)
```

### Step 1: Check Pod Status

```bash
# View Pod status
kubectl get pods

# Common statuses and meanings:
# Running: Pod is running normally
# Pending: Waiting to be scheduled
# ContainerCreating: Pulling images/creating containers
# CrashLoopBackOff: Container repeatedly crashing
# ImagePullBackOff: Cannot pull container image
# Error: Container exited with error
# Completed: Job/batch Pod finished successfully
# Terminating: Pod is being deleted
# Unknown: Node lost contact

# Check status with wide output
kubectl get pods -o wide

# Check specific Pod
kubectl get pod nginx-pod
```

### Step 2: Describe Pod

```bash
# Describe Pod to see events
kubectl describe pod nginx-pod

# Key sections to check:
# - Status: Current phase
# - Conditions: Ready, ContainersReady, PodScheduled
# - Containers: Container statuses
# - Events: What happened (crucial for debugging!)
```

**Example Events**:
```
Events:
  Type     Reason            Message
  ----     ------            -------
  Normal   Scheduled         Successfully assigned default/nginx-pod to worker-1
  Normal   Pulling           Pulling image "nginx:1.21"
  Normal   Pulled            Successfully pulled image
  Normal   Created           Created container nginx
  Normal   Started           Started container nginx

  # Or error events:
  Warning  Failed            Failed to pull image "nginx:invalid-tag"
  Warning  BackOff           Back-off restarting failed container
```

### Step 3: Common Pod Issues and Solutions

**Issue: ImagePullBackOff**

```bash
# Symptom
NAME        READY   STATUS             RESTARTS   AGE
my-pod      0/1     ImagePullBackOff   0          2m

# Check events
kubectl describe pod my-pod

# Common causes:
# 1. Image doesn't exist
# 2. Image tag is wrong
# 3. Private registry requires authentication
# 4. Image pull rate limit exceeded

# Solutions:
# 1. Fix image name/tag
# 2. Create imagePullSecret
kubectl create secret docker-registry regcred \
  --docker-server=https://index.docker.io/v1/ \
  --docker-username=myuser \
  --docker-password=mypass

# Add to Pod spec
imagePullSecrets:
- name: regcred
```

**Issue: CrashLoopBackOff**

```bash
# Symptom
NAME        READY   STATUS             RESTARTS   AGE
my-pod      0/1     CrashLoopBackOff   5          5m

# Container is starting then crashing repeatedly
# Check logs to see why
kubectl logs my-pod

# Check previous container logs (after crash)
kubectl logs my-pod --previous

# Common causes:
# 1. Application error on startup
# 2. Missing environment variables
# 3. Configuration error
# 4. Insufficient resources
# 5. Liveness probe failing too early

# Solutions depend on logs, but common fixes:
# - Fix application code
# - Add required env vars/config
# - Increase resources
# - Adjust liveness probe initialDelaySeconds
```

**Issue: Pending (Not Scheduled)**

```bash
# Symptom
NAME        READY   STATUS    RESTARTS   AGE
my-pod      0/1     Pending   0          5m

# Check why not scheduled
kubectl describe pod my-pod

# Common causes shown in events:
# 1. Insufficient CPU/memory on nodes
# 2. No nodes match nodeSelector/affinity
# 3. Taints preventing scheduling
# 4. PVC not available

# Example events:
Events:
  Warning  FailedScheduling  0/3 nodes are available: 3 Insufficient memory.

# Solutions:
# 1. Add more nodes or resize existing
# 2. Reduce resource requests
# 3. Fix nodeSelector/affinity
# 4. Remove taints or add tolerations
# 5. Create/fix PVC
```

**Issue: ContainerCreating (Stuck)**

```bash
# Symptom
NAME        READY   STATUS              RESTARTS   AGE
my-pod      0/1     ContainerCreating   0          5m

# Check events
kubectl describe pod my-pod

# Common causes:
# 1. Volume mount issues
# 2. Image pull is slow
# 3. CNI plugin issue

# Example:
Events:
  Warning  FailedMount  Unable to mount volumes: timeout expired waiting for volumes to attach

# Solutions:
# - Check PVC status
# - Verify StorageClass exists
# - Check node kubelet logs
```

**Issue: Pod Ready But Not Receiving Traffic**

```bash
# Symptom
# Pod is Running but Service not routing traffic

# Check Pod readiness
kubectl get pod my-pod -o json | jq '.status.conditions'

# Check if Pod has readiness probe
kubectl get pod my-pod -o yaml | grep -A5 readinessProbe

# Check if Pod matches Service selector
kubectl describe service my-service

# Check endpoints
kubectl get endpoints my-service

# If endpoints empty, labels don't match
# Fix: Update Pod labels or Service selector
```

### Debugging Deployments

```bash
# Check Deployment status
kubectl get deployment nginx-deployment

# Detailed status
kubectl describe deployment nginx-deployment

# Check rollout status
kubectl rollout status deployment/nginx-deployment

# Check rollout history
kubectl rollout history deployment/nginx-deployment

# Check ReplicaSet
kubectl get replicaset
kubectl describe replicaset <replicaset-name>

# Common Deployment issues:
# 1. Image pull errors
# 2. Resource constraints
# 3. Liveness probe failures
# 4. Config errors

# Debug by checking Pods created by Deployment
kubectl get pods -l app=nginx

# Then debug individual Pods as shown above
```

## Logs and Events

### Viewing Logs

**Basic Log Commands**:
```bash
# View Pod logs
kubectl logs nginx-pod

# Follow logs (stream)
kubectl logs -f nginx-pod

# Logs from specific container (multi-container Pod)
kubectl logs nginx-pod -c sidecar-container

# Previous container logs (after crash)
kubectl logs nginx-pod --previous

# Logs since timestamp
kubectl logs nginx-pod --since=1h
kubectl logs nginx-pod --since-time=2023-01-01T00:00:00Z

# Last N lines
kubectl logs nginx-pod --tail=100

# Logs with timestamps
kubectl logs nginx-pod --timestamps

# All logs from Pods matching label
kubectl logs -l app=nginx

# Logs from all containers in Pod
kubectl logs nginx-pod --all-containers=true
```

**ML Training Job Logs Example**:
```bash
# Stream training logs
kubectl logs -f training-job-xyz --tail=50

# Save logs to file
kubectl logs training-job-xyz > training-logs.txt

# Monitor multiple Pods
kubectl logs -l job-name=training-job -f --max-log-requests=10
```

### Viewing Events

```bash
# Cluster-wide events
kubectl get events

# Events in specific namespace
kubectl get events -n production

# Events sorted by timestamp
kubectl get events --sort-by='.lastTimestamp'

# Watch events
kubectl get events -w

# Events for specific resource
kubectl describe pod nginx-pod  # includes events

# Filter events
kubectl get events --field-selector involvedObject.kind=Pod
kubectl get events --field-selector type=Warning
kubectl get events --field-selector reason=Failed

# Human-readable timestamps
kubectl get events --sort-by='.lastTimestamp' -o custom-columns=LAST:.lastTimestamp,TYPE:.type,REASON:.reason,MESSAGE:.message
```

**Event Types**:
- **Normal**: Regular operations (Created, Started, Pulled, etc.)
- **Warning**: Issues that need attention (Failed, BackOff, Unhealthy, etc.)

### Log Aggregation

For production, use centralized logging:

**EFK Stack** (Elasticsearch, Fluentd, Kibana):
```bash
# Fluentd runs as DaemonSet
kubectl get daemonset fluentd -n kube-system

# Logs sent to Elasticsearch
# View in Kibana web UI
```

**PLG Stack** (Promtail, Loki, Grafana):
```bash
# Promtail collects logs
# Loki stores logs
# Grafana visualizes

# Query logs in Grafana with LogQL
{namespace="production", app="ml-model"} |= "error"
```

**ELK Stack** (Elasticsearch, Logstash, Kibana):
```bash
# Similar to EFK but uses Logstash
# Better for complex log processing
```

## Executing Commands in Containers

### kubectl exec

```bash
# Execute command in Pod
kubectl exec nginx-pod -- ls /usr/share/nginx/html

# Interactive shell
kubectl exec -it nginx-pod -- /bin/bash
kubectl exec -it nginx-pod -- /bin/sh  # if bash not available

# Specific container (multi-container Pod)
kubectl exec -it nginx-pod -c sidecar -- /bin/sh

# Execute as specific user
kubectl exec nginx-pod -- su - appuser -c "whoami"

# Set environment variables
kubectl exec nginx-pod -- env DEBUG=true /app/script.sh
```

### Common Debugging Commands Inside Containers

```bash
# Interactive shell
kubectl exec -it nginx-pod -- /bin/bash

# Inside container:

# Check processes
ps aux

# Check network
netstat -tlnp
ss -tlnp

# Check files
ls -la /app
cat /etc/config/app.properties

# Check environment
env | grep -i db

# Check disk space
df -h

# Check memory
free -h

# Test connectivity
curl localhost:8080/health
wget -qO- http://api-service:8080/

# DNS resolution
nslookup redis-service
dig redis-service.default.svc.cluster.local

# Check mounted volumes
mount | grep /data

# Check logs (if app writes to file)
tail -f /var/log/app.log

# Install debugging tools (if needed, temporary)
apt-get update && apt-get install -y curl
apk add curl  # for alpine-based images
```

### Debug Container (Ephemeral Containers)

For containers without shell or debugging tools:

```bash
# Add ephemeral debug container to running Pod
kubectl debug -it nginx-pod --image=busybox --target=nginx

# Debug with different image
kubectl debug nginx-pod --image=ubuntu --target=nginx

# Create copy of Pod with debugging tools
kubectl debug nginx-pod -it --copy-to=nginx-debug --container=debug --image=busybox
```

### kubectl run for Quick Tests

```bash
# Create temporary test Pod
kubectl run test-pod --rm -it --image=busybox -- /bin/sh

# Test network connectivity
kubectl run test-curl --rm -it --image=curlimages/curl -- curl http://nginx-service

# Test DNS
kubectl run test-dns --rm -it --image=busybox -- nslookup kubernetes.default

# Test PostgreSQL connection
kubectl run test-pg --rm -it --image=postgres:14 -- psql -h postgres-service -U admin
```

## Resource Monitoring

### kubectl top

Requires Metrics Server to be installed.

```bash
# Node resource usage
kubectl top nodes

# Output:
# NAME       CPU(cores)   CPU%   MEMORY(bytes)   MEMORY%
# master     250m         12%    1024Mi          51%
# worker-1   1200m        30%    4096Mi          68%
# worker-2   800m         20%    3072Mi          51%

# Pod resource usage
kubectl top pods

# All namespaces
kubectl top pods -A

# Specific namespace
kubectl top pods -n production

# Sort by memory
kubectl top pods --sort-by=memory

# Sort by CPU
kubectl top pods --sort-by=cpu

# Containers in Pod
kubectl top pod nginx-pod --containers
```

### Resource Quotas and Limits

```bash
# View resource quotas
kubectl get resourcequota

# Describe quota
kubectl describe resourcequota compute-quota

# View limit ranges
kubectl get limitrange

# Check actual vs requested resources
kubectl describe node worker-1

# Section "Allocated resources" shows:
# Resource           Requests      Limits
# --------           --------      ------
# cpu                2500m (62%)   5000m (125%)
# memory             8Gi (50%)     16Gi (100%)
# nvidia.com/gpu     2             2
```

### Monitoring ML Workloads

```bash
# Monitor GPU usage (requires nvidia-smi in container)
kubectl exec -it ml-training-pod -- nvidia-smi

# Monitor GPU Pods
kubectl top pods -l gpu=true --sort-by=memory

# Check GPU allocation
kubectl describe node gpu-node-1 | grep -A5 "Allocated resources"

# Output:
# nvidia.com/gpu: 2 (of 4 available)
```

### Monitoring Tools

**Prometheus + Grafana**:
```bash
# Deploy Prometheus Operator
helm install prometheus prometheus-community/kube-prometheus-stack

# Access Grafana
kubectl port-forward svc/prometheus-grafana 3000:80

# View pre-built dashboards:
# - Kubernetes cluster monitoring
# - Node exporter metrics
# - Pod resource usage
```

**Kubernetes Dashboard**:
```bash
# Deploy dashboard
kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.7.0/aio/deploy/recommended.yaml

# Create admin user and get token
kubectl -n kubernetes-dashboard create token admin-user

# Access dashboard
kubectl proxy
# Visit: http://localhost:8001/api/v1/namespaces/kubernetes-dashboard/services/https:kubernetes-dashboard:/proxy/
```

## Troubleshooting Common Issues

### Node Issues

**Node NotReady**:
```bash
# Check node status
kubectl get nodes

# NAME       STATUS     ROLES    AGE   VERSION
# worker-1   NotReady   <none>   5d    v1.25.0

# Describe node
kubectl describe node worker-1

# Check conditions
kubectl get node worker-1 -o json | jq '.status.conditions'

# Common causes:
# 1. kubelet not running
# 2. Network plugin issue
# 3. Disk pressure
# 4. Memory pressure

# SSH to node and check:
# kubelet status
systemctl status kubelet

# kubelet logs
journalctl -u kubelet -f

# Restart kubelet
systemctl restart kubelet
```

**Node Disk Pressure**:
```bash
# Symptom
kubectl describe node worker-1
# Conditions:
#   DiskPressure    True

# Solution: Clean up disk
# SSH to node
docker system prune -a
# Or
crictl rmi --prune

# Remove old container logs
find /var/log/pods -type f -mtime +7 -delete
```

### Network Issues

**Pod Cannot Reach Service**:
```bash
# Test from Pod
kubectl run test --rm -it --image=busybox -- wget -qO- http://nginx-service

# If fails, check:

# 1. Service exists
kubectl get service nginx-service

# 2. Endpoints populated
kubectl get endpoints nginx-service

# 3. Pod labels match service selector
kubectl get pods --show-labels
kubectl describe service nginx-service

# 4. Network policies blocking traffic
kubectl get networkpolicy

# 5. CoreDNS working
kubectl run test --rm -it --image=busybox -- nslookup nginx-service
```

**DNS Resolution Issues**:
```bash
# Check CoreDNS Pods
kubectl get pods -n kube-system -l k8s-app=kube-dns

# Check CoreDNS logs
kubectl logs -n kube-system -l k8s-app=kube-dns

# Test DNS from Pod
kubectl run test --rm -it --image=busybox -- nslookup kubernetes.default

# Check DNS configuration in Pod
kubectl exec test-pod -- cat /etc/resolv.conf

# Should show:
# nameserver 10.96.0.10
# search default.svc.cluster.local svc.cluster.local cluster.local
```

### Storage Issues

**PVC Stuck in Pending**:
```bash
# Check PVC status
kubectl get pvc

# Describe PVC
kubectl describe pvc my-pvc

# Common causes in events:
# 1. No PV available
# 2. StorageClass doesn't exist
# 3. Access mode mismatch
# 4. Insufficient storage

# Check PVs
kubectl get pv

# Check StorageClass
kubectl get storageclass

# Solution: Create PV or fix StorageClass
```

**Pod Cannot Mount Volume**:
```bash
# Symptom
kubectl describe pod my-pod
# Events:
#   Warning  FailedMount  MountVolume.SetUp failed

# Common causes:
# 1. PVC doesn't exist
# 2. PVC not bound
# 3. Volume already mounted on different node (RWO)
# 4. NFS server unreachable

# Check PVC status
kubectl get pvc

# Check if volume mounted elsewhere
kubectl get pods -o json | jq '.items[] | select(.spec.volumes[]?.persistentVolumeClaim.claimName=="my-pvc") | .metadata.name'

# Solution: Fix PVC or ensure RWX access mode for multi-pod access
```

### Configuration Issues

**ConfigMap/Secret Not Found**:
```bash
# Symptom
kubectl describe pod my-pod
# Events:
#   Warning  Failed  Error: configmap "app-config" not found

# Check if exists
kubectl get configmap app-config
kubectl get secret app-secret

# Check namespace
kubectl get configmap app-config -n correct-namespace

# Solution: Create ConfigMap/Secret or fix reference
```

**Wrong Environment Variables**:
```bash
# Check actual env vars in Pod
kubectl exec my-pod -- env

# Compare with expected
kubectl get pod my-pod -o yaml | grep -A10 env:

# Check ConfigMap/Secret contents
kubectl get configmap app-config -o yaml
kubectl get secret app-secret -o jsonpath='{.data.password}' | base64 -d
```

### Performance Issues

**High CPU Usage**:
```bash
# Identify high CPU Pods
kubectl top pods --sort-by=cpu

# Check for CPU throttling
kubectl describe pod high-cpu-pod

# Check container limits
kubectl get pod high-cpu-pod -o jsonpath='{.spec.containers[].resources}'

# Solutions:
# 1. Increase CPU limits
# 2. Optimize application code
# 3. Scale horizontally (more replicas)
```

**High Memory Usage / OOMKilled**:
```bash
# Check Pod status
kubectl get pods

# NAME      READY   STATUS      RESTARTS   AGE
# my-pod    0/1     OOMKilled   5          10m

# Check events
kubectl describe pod my-pod
# Events:
#   Warning  OOMKilling  Memory cgroup out of memory: Kill process

# Check memory limits
kubectl get pod my-pod -o jsonpath='{.spec.containers[].resources.limits.memory}'

# Solutions:
# 1. Increase memory limits
# 2. Fix memory leaks in application
# 3. Use more memory-efficient algorithms
```

## kubectl Productivity Tips

### Aliases and Shortcuts

```bash
# Add to ~/.bashrc or ~/.zshrc

# Basic aliases
alias k='kubectl'
alias kg='kubectl get'
alias kd='kubectl describe'
alias kdel='kubectl delete'
alias kl='kubectl logs'
alias kex='kubectl exec -it'
alias kap='kubectl apply -f'

# Namespace shortcuts
alias kgp='kubectl get pods'
alias kgd='kubectl get deployments'
alias kgs='kubectl get services'
alias kgn='kubectl get nodes'

# Advanced aliases
alias kgpa='kubectl get pods --all-namespaces'
alias kgpw='kubectl get pods -o wide'
alias kgpwa='kubectl get pods -o wide --all-namespaces'
alias kdp='kubectl describe pod'
alias kdd='kubectl describe deployment'
alias kds='kubectl describe service'

# Watch
alias kgpw='watch kubectl get pods'

# Logs
alias klf='kubectl logs -f'
alias klp='kubectl logs -f --previous'

# Shell into pod
alias ksh='kubectl exec -it $1 -- /bin/sh'
alias kbash='kubectl exec -it $1 -- /bin/bash'

# Usage:
# k get pods
# kg deploy
# kl my-pod
# kex my-pod -- /bin/bash
```

### kubectl Plugins

**krew** (kubectl plugin manager):
```bash
# Install krew
# https://krew.sigs.k8s.io/docs/user-guide/setup/install/

# Popular plugins
kubectl krew install ctx      # Switch contexts
kubectl krew install ns       # Switch namespaces
kubectl krew install tree     # Show resource hierarchy
kubectl krew install tail     # Tail logs from multiple pods
kubectl krew install neat     # Clean up kubectl output
kubectl krew install whoami   # Show current user info

# Usage
kubectl ctx                   # List contexts
kubectl ctx production        # Switch to production
kubectl ns production         # Switch namespace
kubectl tree deployment nginx # Show deployment hierarchy
kubectl tail -l app=nginx     # Tail logs from all nginx pods
```

**Useful Plugins**:
- **kubectl-tree**: Show resource hierarchy
- **kubectl-tail**: Multi-pod log tailing
- **kubectl-neat**: Remove clutter from kubectl output
- **kubectl-images**: Show images used in cluster
- **kubectl-resource-capacity**: Show resource capacity

### Shell Completion

```bash
# Bash
echo 'source <(kubectl completion bash)' >>~/.bashrc
echo 'alias k=kubectl' >>~/.bashrc
echo 'complete -F __start_kubectl k' >>~/.bashrc

# Zsh
echo 'source <(kubectl completion zsh)' >>~/.zshrc
echo 'alias k=kubectl' >>~/.zshrc
echo 'complete -F __start_kubectl k' >>~/.zshrc

# Test
k get po<TAB>  # Should autocomplete to 'pods'
```

### Advanced kubectl Techniques

**JSONPath Queries**:
```bash
# Get Pod IPs
kubectl get pods -o jsonpath='{.items[*].status.podIP}'

# Get container images
kubectl get pods -o jsonpath='{.items[*].spec.containers[*].image}' | tr -s ' ' '\n'

# Get Pod and Node
kubectl get pods -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.nodeName}{"\n"}{end}'

# Get failing Pods
kubectl get pods --field-selector=status.phase!=Running

# Get resource limits
kubectl get pods -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.containers[*].resources.limits}{"\n"}{end}'
```

**Field Selectors**:
```bash
# By status
kubectl get pods --field-selector status.phase=Running
kubectl get pods --field-selector status.phase!=Running

# By node
kubectl get pods --field-selector spec.nodeName=worker-1

# By namespace
kubectl get pods --all-namespaces --field-selector metadata.namespace!=kube-system

# Multiple conditions
kubectl get pods --field-selector status.phase=Running,spec.nodeName=worker-1
```

**Label Selectors**:
```bash
# Equality-based
kubectl get pods -l app=nginx
kubectl get pods -l app=nginx,tier=frontend

# Set-based
kubectl get pods -l 'environment in (production, staging)'
kubectl get pods -l 'tier notin (frontend)'
kubectl get pods -l 'app,environment'  # Has both labels
kubectl get pods -l '!app'  # Doesn't have app label
```

## Cluster Maintenance

### Draining Nodes

```bash
# Drain node (evict all pods for maintenance)
kubectl drain worker-1 --ignore-daemonsets --delete-emptydir-data

# Cordon node (prevent scheduling but don't evict)
kubectl cordon worker-1

# Uncordon node (allow scheduling again)
kubectl uncordon worker-1

# Workflow:
# 1. Drain node
# 2. Perform maintenance (upgrade, reboot, etc.)
# 3. Uncordon node
```

### Backing Up Resources

```bash
# Backup all resources
kubectl get all --all-namespaces -o yaml > cluster-backup.yaml

# Backup specific namespace
kubectl get all -n production -o yaml > production-backup.yaml

# Backup specific resource types
kubectl get configmap,secret,pvc --all-namespaces -o yaml > configs-backup.yaml

# Backup with velero (recommended)
velero backup create my-backup --include-namespaces production

# Restore
velero restore create --from-backup my-backup
```

### Resource Cleanup

```bash
# Delete completed Jobs
kubectl delete jobs --field-selector status.successful=1

# Delete evicted Pods
kubectl get pods --all-namespaces --field-selector status.phase=Failed -o json | kubectl delete -f -

# Delete old ReplicaSets
kubectl delete replicaset --all-namespaces --field-selector status.replicas=0

# Clean up unused PVs
kubectl get pv --field-selector status.phase=Released

# Find and delete unused ConfigMaps/Secrets (manual check)
# This requires analysis to ensure they're not referenced
```

## Security Operations

### RBAC Debugging

```bash
# Check current user permissions
kubectl auth can-i list pods
kubectl auth can-i delete deployments --namespace production

# Check permissions for service account
kubectl auth can-i list pods --as=system:serviceaccount:default:my-sa

# Check what resources user can access
kubectl auth can-i --list

# Describe role/rolebinding
kubectl describe role developer
kubectl describe rolebinding developer-binding

# Get all roles/rolebindings
kubectl get roles --all-namespaces
kubectl get rolebindings --all-namespaces
kubectl get clusterroles
kubectl get clusterrolebindings
```

### Security Scanning

```bash
# Scan images for vulnerabilities (trivy)
trivy image nginx:1.21

# Scan cluster configuration (kubesec)
kubectl get deploy nginx -o yaml | kubesec scan -

# Check Pod Security Standards
kubectl label namespace production pod-security.kubernetes.io/enforce=restricted
```

### Audit Logs

```bash
# View audit logs (on control plane node)
cat /var/log/kubernetes/audit.log | grep "user.username"

# Filter by user
cat /var/log/kubernetes/audit.log | jq 'select(.user.username=="admin")'

# Filter by namespace
cat /var/log/kubernetes/audit.log | jq 'select(.objectRef.namespace=="production")'

# Filter by verb
cat /var/log/kubernetes/audit.log | jq 'select(.verb=="delete")'
```

## Summary and Key Takeaways

### Essential kubectl Commands

```bash
# Get information
kubectl get pods/deployments/services
kubectl describe pod <name>
kubectl logs <pod>
kubectl top pods/nodes

# Debugging
kubectl exec -it <pod> -- /bin/bash
kubectl debug <pod>
kubectl get events

# Operations
kubectl apply -f manifest.yaml
kubectl delete pod <name>
kubectl scale deployment <name> --replicas=5
kubectl rollout status/history/undo

# Context management
kubectl config use-context <context>
kubectl config set-context --current --namespace=<ns>
```

### Debugging Checklist

1. **Check Pod status**: `kubectl get pods`
2. **Describe Pod**: `kubectl describe pod <name>`
3. **View events**: Check Events section in describe output
4. **Check logs**: `kubectl logs <pod>`
5. **Previous logs** (if crashed): `kubectl logs <pod> --previous`
6. **Exec into Pod**: `kubectl exec -it <pod> -- /bin/bash`
7. **Check Service/Endpoints**: `kubectl get endpoints <service>`
8. **Check resources**: `kubectl top pods`
9. **Check node**: `kubectl describe node <node>`

### Common Issues Quick Reference

| Issue | Check | Solution |
|-------|-------|----------|
| ImagePullBackOff | Image name, registry auth | Fix image, add imagePullSecret |
| CrashLoopBackOff | Logs, resource limits | Fix app, adjust resources |
| Pending | Node resources, PVC | Add nodes, fix PVC |
| Not receiving traffic | Service selector, readiness probe | Fix labels, adjust probe |
| OOMKilled | Memory limits | Increase limits |
| Node NotReady | kubelet, disk space | Restart kubelet, clean disk |

### Best Practices

1. **Use namespaces** to organize resources
2. **Label everything** for easy filtering
3. **Set resource requests/limits** always
4. **Use readiness probes** for traffic routing
5. **Use liveness probes** for auto-restart
6. **Centralize logs** (EFK, PLG, ELK)
7. **Monitor resources** (Prometheus, Grafana)
8. **Regular backups** (Velero)
9. **Practice RBAC** principle of least privilege
10. **Automate** with scripts and CI/CD

### Productivity Tips

- Use **aliases** for common commands
- Install **kubectl plugins** (krew)
- Enable **shell completion**
- Use **kubectl explain** for resource documentation
- Master **JSONPath** and **field/label selectors**
- Keep **kubeconfig organized**
- Use **contexts** for multiple clusters

### Next Steps

- Practice debugging scenarios in Exercise 03
- Set up monitoring with Prometheus
- Configure centralized logging
- Automate operations with scripts
- Learn about GitOps (ArgoCD, Flux)
- Study Kubernetes operators
- Explore service meshes (Istio, Linkerd)

### Further Reading

- kubectl Cheat Sheet: https://kubernetes.io/docs/reference/kubectl/cheatsheet/
- Debugging Guide: https://kubernetes.io/docs/tasks/debug/
- Best Practices: https://kubernetes.io/docs/concepts/configuration/overview/
- Monitoring: https://kubernetes.io/docs/tasks/debug/debug-cluster/resource-metrics-pipeline/

---

**Congratulations!** You now have the operational skills to manage Kubernetes clusters effectively. Practice these skills regularly to build muscle memory and troubleshooting intuition.
