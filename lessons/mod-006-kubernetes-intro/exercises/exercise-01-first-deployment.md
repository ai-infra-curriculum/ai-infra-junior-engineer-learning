# Exercise 01: First Kubernetes Deployment

## Overview

In this hands-on exercise, you'll deploy your first application to Kubernetes, expose it with a Service, and practice scaling. This exercise reinforces the core concepts of Pods, Deployments, Services, and kubectl operations.

## Learning Objectives

By completing this exercise, you will:
- Create and manage Kubernetes Deployments
- Expose applications using Services
- Scale applications up and down
- Update application images (rolling updates)
- Troubleshoot basic issues
- Use kubectl effectively

## Prerequisites

- Completed Lectures 01-02 (Architecture, Deploying Apps)
- kubectl installed and configured
- Access to a Kubernetes cluster (Docker Desktop, Minikube, or cloud)
- Basic understanding of YAML and Docker

## Setup

### Verify Your Environment

```bash
# Check kubectl is working
kubectl version --short

# Check cluster access
kubectl cluster-info

# Verify nodes are ready
kubectl get nodes

# Create namespace for this exercise
kubectl create namespace exercise-01
kubectl config set-context --current --namespace=exercise-01

# Verify namespace
kubectl config view --minify | grep namespace
```

## Part 1: Deploy a Simple Web Application

### Step 1: Create a Deployment

Create a file called `nginx-deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-web
  labels:
    app: nginx
    tier: frontend
spec:
  replicas: 2
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
        tier: frontend
    spec:
      containers:
      - name: nginx
        image: nginx:1.21
        ports:
        - containerPort: 80
          name: http
        resources:
          requests:
            memory: "64Mi"
            cpu: "100m"
          limits:
            memory: "128Mi"
            cpu: "200m"
        livenessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 10
          periodSeconds: 5
        readinessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 5
          periodSeconds: 3
```

**Deploy the application**:
```bash
kubectl apply -f nginx-deployment.yaml

# Watch the deployment
kubectl get deployments -w
# Press Ctrl+C to stop watching

# Check the Pods
kubectl get pods

# Check the ReplicaSet
kubectl get replicasets
```

**Questions to answer**:
1. How many Pods were created?
2. What is the naming pattern for the Pods?
3. What is the relationship between Deployment, ReplicaSet, and Pods?

### Step 2: Inspect the Deployment

```bash
# View detailed deployment information
kubectl describe deployment nginx-web

# View deployment YAML
kubectl get deployment nginx-web -o yaml

# View Pod details
POD_NAME=$(kubectl get pods -l app=nginx -o jsonpath='{.items[0].metadata.name}')
kubectl describe pod $POD_NAME

# View Pod logs
kubectl logs $POD_NAME
```

**Questions to answer**:
1. What image is the container using?
2. What are the resource requests and limits?
3. What health probes are configured?
4. What events occurred during deployment?

### Step 3: Test the Application

```bash
# Get Pod IP
kubectl get pods -o wide

# Port-forward to access the application
kubectl port-forward deployment/nginx-web 8080:80

# Open another terminal and test
curl http://localhost:8080

# Or open in browser: http://localhost:8080
# You should see the nginx welcome page

# Stop port-forward (Ctrl+C in first terminal)
```

**Challenge**: Can you explain why we need to use port-forward to access the Pod?

## Part 2: Expose with a Service

### Step 4: Create a ClusterIP Service

Create a file called `nginx-service.yaml`:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx-service
  labels:
    app: nginx
spec:
  type: ClusterIP
  selector:
    app: nginx
  ports:
  - name: http
    port: 80
    targetPort: 80
    protocol: TCP
```

**Deploy the Service**:
```bash
kubectl apply -f nginx-service.yaml

# View the Service
kubectl get services

# Describe the Service
kubectl describe service nginx-service

# View the Endpoints
kubectl get endpoints nginx-service
```

**Questions to answer**:
1. What is the ClusterIP assigned to the service?
2. How many endpoints are listed?
3. Do the endpoint IPs match the Pod IPs?

### Step 5: Test the Service

```bash
# Create a test Pod to access the service
kubectl run test-pod --rm -it --image=busybox -- sh

# Inside the test Pod:
wget -qO- http://nginx-service
# You should see the nginx HTML

# Test DNS resolution
nslookup nginx-service
# Should resolve to the ClusterIP

# Exit the test Pod
exit
```

**Challenge**: Try accessing the service using the full DNS name: `nginx-service.exercise-01.svc.cluster.local`

### Step 6: Create a NodePort Service

Modify `nginx-service.yaml` to use NodePort:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx-service
spec:
  type: NodePort  # Changed from ClusterIP
  selector:
    app: nginx
  ports:
  - name: http
    port: 80
    targetPort: 80
    nodePort: 30080  # Specify port (optional)
    protocol: TCP
```

**Update the Service**:
```bash
kubectl apply -f nginx-service.yaml

# View the updated Service
kubectl get service nginx-service

# Note the NodePort (30080)

# Get Node IP (for local cluster, use localhost)
# For Docker Desktop/Minikube:
curl http://localhost:30080

# For cloud cluster:
NODE_IP=$(kubectl get nodes -o jsonpath='{.items[0].status.addresses[?(@.type=="ExternalIP")].address}')
curl http://$NODE_IP:30080
```

**Questions to answer**:
1. What is the difference between ClusterIP and NodePort?
2. When would you use NodePort vs ClusterIP?
3. What port range is allowed for NodePort? (Hint: 30000-32767)

## Part 3: Scaling the Application

### Step 7: Scale Up

```bash
# Scale to 5 replicas
kubectl scale deployment nginx-web --replicas=5

# Watch the Pods being created
kubectl get pods -w

# Check deployment status
kubectl get deployment nginx-web

# Check the endpoints (should have 5 now)
kubectl get endpoints nginx-service
```

**Questions to answer**:
1. How long did it take to create new Pods?
2. Are all Pods running on the same node or different nodes?
3. Did the Service automatically discover the new Pods?

### Step 8: Scale Down

```bash
# Scale down to 1 replica
kubectl scale deployment nginx-web --replicas=1

# Watch the Pods being terminated
kubectl get pods -w

# Check endpoints again
kubectl get endpoints nginx-service
```

**Challenge**: What happens to the endpoints as Pods are terminated?

### Step 9: Update replicas in YAML

Edit `nginx-deployment.yaml` and change `replicas: 2` to `replicas: 3`:

```yaml
spec:
  replicas: 3  # Changed from 2
```

```bash
# Apply the changes
kubectl apply -f nginx-deployment.yaml

# Verify the change
kubectl get deployment nginx-web
```

**Question**: What's the difference between `kubectl scale` and updating the YAML?

## Part 4: Rolling Updates

### Step 10: Update the Application Image

```bash
# Update the image to nginx:1.22
kubectl set image deployment/nginx-web nginx=nginx:1.22

# Watch the rollout
kubectl rollout status deployment/nginx-web

# Check the rollout history
kubectl rollout history deployment/nginx-web

# View the Pods (you'll see both old and new during rollout)
kubectl get pods -w
```

**Questions to answer**:
1. Were all Pods replaced at once, or gradually?
2. Was there any downtime?
3. How does Kubernetes ensure zero-downtime updates?

### Step 11: Verify the Update

```bash
# Check which image is running
kubectl get deployment nginx-web -o jsonpath='{.spec.template.spec.containers[0].image}'

# Check a Pod's image
POD_NAME=$(kubectl get pods -l app=nginx -o jsonpath='{.items[0].metadata.name}')
kubectl get pod $POD_NAME -o jsonpath='{.spec.containers[0].image}'

# Describe the Pod to see image pull events
kubectl describe pod $POD_NAME | grep -A5 Events
```

### Step 12: Rollback the Update

```bash
# View rollout history
kubectl rollout history deployment/nginx-web

# Rollback to previous version
kubectl rollout undo deployment/nginx-web

# Watch the rollout
kubectl rollout status deployment/nginx-web

# Verify the image is back to nginx:1.21
kubectl get deployment nginx-web -o jsonpath='{.spec.template.spec.containers[0].image}'
```

**Challenge**: Can you rollback to a specific revision? (Hint: `--to-revision=<number>`)

## Part 5: Troubleshooting

### Step 13: Simulate a Failed Deployment

Create a file called `broken-deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: broken-app
spec:
  replicas: 2
  selector:
    matchLabels:
      app: broken
  template:
    metadata:
      labels:
        app: broken
    spec:
      containers:
      - name: app
        image: nginx:invalid-tag  # This image doesn't exist
        ports:
        - containerPort: 80
```

**Deploy the broken application**:
```bash
kubectl apply -f broken-deployment.yaml

# Watch the Pods (they will fail)
kubectl get pods -w

# After a minute, press Ctrl+C
```

### Step 14: Debug the Issue

```bash
# Check Pod status
kubectl get pods -l app=broken

# You should see: ImagePullBackOff or ErrImagePull

# Describe a Pod to see the error
POD_NAME=$(kubectl get pods -l app=broken -o jsonpath='{.items[0].metadata.name}')
kubectl describe pod $POD_NAME

# Look for error messages in Events section
kubectl describe pod $POD_NAME | grep -A10 Events
```

**Questions to answer**:
1. What error message do you see?
2. Why is the Pod failing?
3. How would you fix this issue?

### Step 15: Fix the Deployment

Edit `broken-deployment.yaml` to use a valid image:

```yaml
image: nginx:1.21  # Fixed!
```

```bash
# Apply the fix
kubectl apply -f broken-deployment.yaml

# Watch the Pods recover
kubectl get pods -l app=broken -w

# Verify they're running
kubectl get pods -l app=broken
```

### Step 16: Cleanup Broken Deployment

```bash
kubectl delete deployment broken-app
```

## Part 6: ConfigMaps and Customization

### Step 17: Create a ConfigMap

Create a custom nginx configuration:

```bash
# Create a ConfigMap with custom HTML
kubectl create configmap nginx-html --from-literal=index.html='
<html>
<head><title>My First K8s App</title></head>
<body>
  <h1>Hello from Kubernetes!</h1>
  <p>This is my first deployment on Kubernetes.</p>
  <p>Hostname: ${HOSTNAME}</p>
</body>
</html>
'

# View the ConfigMap
kubectl get configmap nginx-html -o yaml
```

### Step 18: Use ConfigMap in Deployment

Create `nginx-with-config.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-custom
spec:
  replicas: 2
  selector:
    matchLabels:
      app: nginx-custom
  template:
    metadata:
      labels:
        app: nginx-custom
    spec:
      containers:
      - name: nginx
        image: nginx:1.21
        ports:
        - containerPort: 80
        volumeMounts:
        - name: html
          mountPath: /usr/share/nginx/html
      volumes:
      - name: html
        configMap:
          name: nginx-html
---
apiVersion: v1
kind: Service
metadata:
  name: nginx-custom-service
spec:
  type: NodePort
  selector:
    app: nginx-custom
  ports:
  - port: 80
    targetPort: 80
    nodePort: 30081
```

```bash
# Deploy
kubectl apply -f nginx-with-config.yaml

# Test
curl http://localhost:30081
# Should see your custom HTML
```

## Part 7: Resource Management

### Step 19: Test Resource Limits

Create `resource-test.yaml`:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: resource-test
spec:
  containers:
  - name: stress
    image: polinux/stress
    command: ["stress"]
    args: ["--vm", "1", "--vm-bytes", "250M", "--vm-hang", "1"]
    resources:
      requests:
        memory: "128Mi"
        cpu: "100m"
      limits:
        memory: "256Mi"  # Will be killed if exceeds
        cpu: "200m"
```

```bash
# Deploy
kubectl apply -f resource-test.yaml

# Watch the Pod (may get OOMKilled)
kubectl get pod resource-test -w

# Check events
kubectl describe pod resource-test

# If OOMKilled, you'll see: "Memory cgroup out of memory"
```

### Step 20: Monitor Resources

```bash
# Check resource usage
kubectl top pods

# Check node resources
kubectl top nodes

# Clean up
kubectl delete pod resource-test
```

## Cleanup

```bash
# Delete all resources in the namespace
kubectl delete all --all -n exercise-01

# Or delete the namespace entirely
kubectl delete namespace exercise-01

# Switch back to default namespace
kubectl config set-context --current --namespace=default
```

## Verification Checklist

Ensure you completed all tasks:

- [ ] Created a Deployment with multiple replicas
- [ ] Exposed the Deployment with a ClusterIP Service
- [ ] Changed Service type to NodePort
- [ ] Scaled the Deployment up and down
- [ ] Performed a rolling update
- [ ] Rolled back an update
- [ ] Debugged a failed deployment
- [ ] Used a ConfigMap for configuration
- [ ] Tested resource limits
- [ ] Cleaned up all resources

## Reflection Questions

1. **Architecture**: How do Deployments, ReplicaSets, and Pods relate to each other?

2. **Services**: What are the differences between ClusterIP and NodePort services? When would you use each?

3. **Scaling**: How does Kubernetes handle scaling? What happens to traffic during scale-up/scale-down?

4. **Updates**: How does Kubernetes achieve zero-downtime updates? What happens if an update fails?

5. **Debugging**: What steps would you take to debug a Pod that's stuck in `CrashLoopBackOff`?

6. **Resource Management**: Why are resource requests and limits important? What happens when a container exceeds its limits?

## Challenges

### Challenge 1: Multi-Tier Application

Deploy a complete multi-tier application:
- Frontend (nginx)
- Backend API (any simple API image)
- Database (Redis or PostgreSQL)

Connect them using Services and verify they can communicate.

### Challenge 2: Custom Health Checks

Modify the nginx deployment to include:
- Liveness probe that checks `/health` endpoint
- Readiness probe with different threshold
- Startup probe for slow-starting container simulation

### Challenge 3: Autoscaling

Configure Horizontal Pod Autoscaler (HPA) for the nginx deployment:
```bash
kubectl autoscale deployment nginx-web --cpu-percent=50 --min=2 --max=10
```

Generate load and watch it scale up.

### Challenge 4: Deployment Strategies

Experiment with different deployment strategies:
- RollingUpdate with maxSurge=1, maxUnavailable=0
- RollingUpdate with maxSurge=2, maxUnavailable=1
- Recreate strategy

Observe the differences during updates.

## Common Issues and Solutions

### Issue: "error: error validating: error validating data..."

**Solution**: Check your YAML syntax, especially indentation.

### Issue: "The connection to the server localhost:8080 was refused"

**Solution**: kubectl is not configured. Check your kubeconfig:
```bash
kubectl cluster-info
```

### Issue: Pods stuck in "Pending"

**Solution**: Check if cluster has enough resources:
```bash
kubectl describe pod <pod-name>
kubectl top nodes
```

### Issue: "ImagePullBackOff"

**Solution**: Check image name and tag:
```bash
kubectl describe pod <pod-name>
# Look for image pull errors in Events
```

## Next Steps

- Complete Exercise 02: Create a Helm Chart
- Complete Exercise 03: Debugging Kubernetes Issues
- Experiment with StatefulSets for stateful applications
- Learn about DaemonSets and Jobs
- Explore Ingress for HTTP routing

## Additional Resources

- Kubernetes Documentation: https://kubernetes.io/docs/
- kubectl Cheat Sheet: https://kubernetes.io/docs/reference/kubectl/cheatsheet/
- Play with Kubernetes: https://labs.play-with-k8s.com/
- Katacoda Interactive Tutorials: https://www.katacoda.com/courses/kubernetes

---

**Congratulations!** You've completed your first Kubernetes deployment exercise. You've learned the core workflows for deploying, scaling, updating, and troubleshooting applications on Kubernetes.

Save your YAML files for reference and practice these commands regularly to build muscle memory.
