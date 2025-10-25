# Kubernetes Cheat Sheet

Quick reference guide for essential kubectl commands and Kubernetes concepts.

---

## Table of Contents

- [kubectl Basics](#kubectl-basics)
- [Resource Management](#resource-management)
- [Pods](#pods)
- [Deployments](#deployments)
- [Services](#services)
- [ConfigMaps and Secrets](#configmaps-and-secrets)
- [Namespaces](#namespaces)
- [Troubleshooting](#troubleshooting)
- [YAML Templates](#yaml-templates)

---

## kubectl Basics

### Configuration
```bash
# View current context
kubectl config current-context

# List all contexts
kubectl config get-contexts

# Switch context
kubectl config use-context <context-name>

# View cluster info
kubectl cluster-info

# View kubectl configuration
kubectl config view

# Set default namespace
kubectl config set-context --current --namespace=<namespace>
```

### Getting Help
```bash
# General help
kubectl --help

# Help for specific command
kubectl get --help

# Explain resource
kubectl explain pod
kubectl explain pod.spec
kubectl explain pod.spec.containers
```

### Basic Commands
```bash
# Get resources
kubectl get <resource>
kubectl get pods
kubectl get deployments
kubectl get services
kubectl get all

# Describe resource (detailed info)
kubectl describe <resource> <name>
kubectl describe pod my-pod

# Create resource from file
kubectl apply -f <file.yaml>
kubectl create -f <file.yaml>

# Delete resource
kubectl delete <resource> <name>
kubectl delete -f <file.yaml>

# Edit resource
kubectl edit <resource> <name>
```

---

## Resource Management

### Viewing Resources

#### Get Resources
```bash
# List all pods
kubectl get pods
kubectl get po  # shorthand

# List with more details
kubectl get pods -o wide

# List in all namespaces
kubectl get pods --all-namespaces
kubectl get pods -A  # shorthand

# List specific namespace
kubectl get pods -n <namespace>

# Output formats
kubectl get pods -o yaml
kubectl get pods -o json
kubectl get pods -o name
kubectl get pods -o custom-columns=NAME:.metadata.name,STATUS:.status.phase
```

#### Watch Resources
```bash
# Watch for changes
kubectl get pods --watch
kubectl get pods -w  # shorthand

# Watch all resources
kubectl get all -w
```

#### Filtering
```bash
# Filter by label
kubectl get pods -l app=myapp
kubectl get pods --selector app=myapp

# Filter by field
kubectl get pods --field-selector status.phase=Running

# Multiple filters
kubectl get pods -l app=myapp,env=prod
```

### Creating Resources

#### Imperative Commands
```bash
# Create pod
kubectl run nginx --image=nginx

# Create deployment
kubectl create deployment nginx --image=nginx

# Create service
kubectl expose deployment nginx --port=80 --type=NodePort

# Create from file
kubectl create -f deployment.yaml
```

#### Declarative Commands
```bash
# Apply configuration (create or update)
kubectl apply -f deployment.yaml
kubectl apply -f ./configs/

# Apply with recursion
kubectl apply -f ./configs/ -R
```

### Updating Resources
```bash
# Set image
kubectl set image deployment/nginx nginx=nginx:1.19

# Scale deployment
kubectl scale deployment nginx --replicas=3

# Autoscale
kubectl autoscale deployment nginx --min=2 --max=10 --cpu-percent=80

# Edit resource
kubectl edit deployment nginx

# Patch resource
kubectl patch deployment nginx -p '{"spec":{"replicas":5}}'
```

### Deleting Resources
```bash
# Delete pod
kubectl delete pod nginx

# Delete deployment
kubectl delete deployment nginx

# Delete from file
kubectl delete -f deployment.yaml

# Delete by label
kubectl delete pods -l app=myapp

# Force delete
kubectl delete pod nginx --force --grace-period=0

# Delete all pods in namespace
kubectl delete pods --all -n <namespace>
```

---

## Pods

### Pod Operations
```bash
# List pods
kubectl get pods

# Describe pod
kubectl describe pod <pod-name>

# Get pod logs
kubectl logs <pod-name>
kubectl logs <pod-name> -f  # follow
kubectl logs <pod-name> --tail=100  # last 100 lines
kubectl logs <pod-name> -c <container-name>  # specific container
kubectl logs <pod-name> --previous  # previous instance

# Execute command in pod
kubectl exec <pod-name> -- <command>
kubectl exec -it <pod-name> -- bash  # interactive bash
kubectl exec -it <pod-name> -c <container> -- bash  # specific container

# Port forwarding
kubectl port-forward <pod-name> 8080:80

# Copy files
kubectl cp <pod-name>:/path/in/pod /local/path
kubectl cp /local/path <pod-name>:/path/in/pod

# Top (resource usage)
kubectl top pod <pod-name>
kubectl top pods --all-namespaces
```

### Pod Debugging
```bash
# Get pod YAML
kubectl get pod <pod-name> -o yaml

# Get events
kubectl get events --sort-by=.metadata.creationTimestamp

# Describe for troubleshooting
kubectl describe pod <pod-name>

# Check pod status
kubectl get pod <pod-name> -o jsonpath='{.status.phase}'

# Check container statuses
kubectl get pod <pod-name> -o jsonpath='{.status.containerStatuses[*].state}'
```

### Pod YAML Example
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx-pod
  labels:
    app: nginx
spec:
  containers:
  - name: nginx
    image: nginx:1.19
    ports:
    - containerPort: 80
    env:
    - name: ENV
      value: "production"
    resources:
      requests:
        memory: "64Mi"
        cpu: "250m"
      limits:
        memory: "128Mi"
        cpu: "500m"
```

---

## Deployments

### Deployment Operations
```bash
# Create deployment
kubectl create deployment nginx --image=nginx:1.19

# List deployments
kubectl get deployments
kubectl get deploy  # shorthand

# Describe deployment
kubectl describe deployment nginx

# Scale deployment
kubectl scale deployment nginx --replicas=5

# Autoscale
kubectl autoscale deployment nginx --min=2 --max=10 --cpu-percent=80

# Update image
kubectl set image deployment/nginx nginx=nginx:1.20

# Check rollout status
kubectl rollout status deployment/nginx

# View rollout history
kubectl rollout history deployment/nginx

# Rollback to previous version
kubectl rollout undo deployment/nginx

# Rollback to specific revision
kubectl rollout undo deployment/nginx --to-revision=2

# Pause rollout
kubectl rollout pause deployment/nginx

# Resume rollout
kubectl rollout resume deployment/nginx

# Restart deployment (recreate pods)
kubectl rollout restart deployment/nginx
```

### Deployment YAML Example
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
  labels:
    app: nginx
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 1
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
        image: nginx:1.19
        ports:
        - containerPort: 80
        livenessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 5
          periodSeconds: 5
        resources:
          requests:
            memory: "64Mi"
            cpu: "250m"
          limits:
            memory: "128Mi"
            cpu: "500m"
```

---

## Services

### Service Operations
```bash
# List services
kubectl get services
kubectl get svc  # shorthand

# Describe service
kubectl describe service nginx

# Create service from deployment
kubectl expose deployment nginx --port=80 --type=NodePort

# Get service endpoint
kubectl get endpoints nginx

# Delete service
kubectl delete service nginx
```

### Service Types

#### ClusterIP (default)
```yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx-clusterip
spec:
  type: ClusterIP
  selector:
    app: nginx
  ports:
  - port: 80
    targetPort: 80
```

#### NodePort
```yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx-nodeport
spec:
  type: NodePort
  selector:
    app: nginx
  ports:
  - port: 80
    targetPort: 80
    nodePort: 30080  # optional, will auto-assign if omitted
```

#### LoadBalancer
```yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx-loadbalancer
spec:
  type: LoadBalancer
  selector:
    app: nginx
  ports:
  - port: 80
    targetPort: 80
```

---

## ConfigMaps and Secrets

### ConfigMaps

#### Create ConfigMap
```bash
# From literal values
kubectl create configmap app-config \
  --from-literal=ENV=production \
  --from-literal=DEBUG=false

# From file
kubectl create configmap app-config --from-file=config.properties

# From directory
kubectl create configmap app-config --from-file=./configs/

# From YAML
kubectl apply -f configmap.yaml
```

#### ConfigMap YAML
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  ENV: "production"
  DEBUG: "false"
  config.properties: |
    property1=value1
    property2=value2
```

#### Use ConfigMap in Pod
```yaml
spec:
  containers:
  - name: app
    image: myapp
    # Environment variables from ConfigMap
    env:
    - name: ENV
      valueFrom:
        configMapKeyRef:
          name: app-config
          key: ENV
    # All keys as env vars
    envFrom:
    - configMapRef:
        name: app-config
    # Mount as volume
    volumeMounts:
    - name: config-volume
      mountPath: /etc/config
  volumes:
  - name: config-volume
    configMap:
      name: app-config
```

### Secrets

#### Create Secret
```bash
# From literal values
kubectl create secret generic db-secret \
  --from-literal=username=admin \
  --from-literal=password=secret123

# From file
kubectl create secret generic db-secret --from-file=./secret.txt

# TLS secret
kubectl create secret tls tls-secret \
  --cert=path/to/cert.crt \
  --key=path/to/key.key

# Docker registry secret
kubectl create secret docker-registry regcred \
  --docker-server=<registry> \
  --docker-username=<username> \
  --docker-password=<password>
```

#### Secret YAML
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: db-secret
type: Opaque
data:
  # Values must be base64 encoded
  username: YWRtaW4=  # admin
  password: c2VjcmV0MTIz  # secret123
```

#### Encode/Decode Base64
```bash
# Encode
echo -n "secret123" | base64

# Decode
echo "c2VjcmV0MTIz" | base64 --decode
```

#### Use Secret in Pod
```yaml
spec:
  containers:
  - name: app
    image: myapp
    env:
    - name: DB_PASSWORD
      valueFrom:
        secretKeyRef:
          name: db-secret
          key: password
    envFrom:
    - secretRef:
        name: db-secret
    volumeMounts:
    - name: secret-volume
      mountPath: /etc/secrets
      readOnly: true
  volumes:
  - name: secret-volume
    secret:
      secretName: db-secret
```

---

## Namespaces

### Namespace Operations
```bash
# List namespaces
kubectl get namespaces
kubectl get ns  # shorthand

# Create namespace
kubectl create namespace dev

# Delete namespace
kubectl delete namespace dev

# Get resources in namespace
kubectl get pods -n dev

# Set default namespace
kubectl config set-context --current --namespace=dev
```

### Namespace YAML
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: dev
  labels:
    environment: development
```

### Resource Quotas
```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: dev-quota
  namespace: dev
spec:
  hard:
    requests.cpu: "10"
    requests.memory: 20Gi
    limits.cpu: "20"
    limits.memory: 40Gi
    pods: "10"
```

---

## Troubleshooting

### Debugging Commands

#### Pod Issues
```bash
# Check pod status
kubectl get pods
kubectl describe pod <pod-name>

# View logs
kubectl logs <pod-name>
kubectl logs <pod-name> --previous  # previous container

# Events
kubectl get events --sort-by=.metadata.creationTimestamp
kubectl get events -n <namespace>

# Pod shell access
kubectl exec -it <pod-name> -- sh
kubectl exec -it <pod-name> -- bash

# Check resource usage
kubectl top pod <pod-name>
kubectl top node
```

#### Network Issues
```bash
# Check service endpoints
kubectl get endpoints <service-name>

# Describe service
kubectl describe service <service-name>

# Port forward for testing
kubectl port-forward <pod-name> 8080:80

# Test connectivity from pod
kubectl exec -it <pod-name> -- wget -qO- http://service-name
kubectl exec -it <pod-name> -- curl service-name
```

#### Resource Issues
```bash
# Check node resources
kubectl describe node <node-name>
kubectl top nodes

# Check pod resource usage
kubectl top pods

# Check resource quotas
kubectl describe resourcequota -n <namespace>
```

### Common Pod States

**Pending**: Waiting to be scheduled
```bash
# Check node resources
kubectl describe node
# Check events
kubectl describe pod <pod-name>
```

**ImagePullBackOff**: Can't pull container image
```bash
# Check image name and credentials
kubectl describe pod <pod-name>
```

**CrashLoopBackOff**: Container keeps crashing
```bash
# Check logs
kubectl logs <pod-name>
kubectl logs <pod-name> --previous
```

**Error**: Container exited with error
```bash
# Check logs and describe
kubectl logs <pod-name>
kubectl describe pod <pod-name>
```

---

## YAML Templates

### Complete Deployment Example
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
  namespace: production
  labels:
    app: myapp
    environment: production
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
        version: "1.0"
    spec:
      containers:
      - name: myapp
        image: myapp:1.0
        imagePullPolicy: IfNotPresent
        ports:
        - containerPort: 8000
          name: http
        env:
        - name: ENV
          valueFrom:
            configMapKeyRef:
              name: app-config
              key: ENV
        - name: DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: password
        resources:
          requests:
            memory: "128Mi"
            cpu: "250m"
          limits:
            memory: "256Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 3
        volumeMounts:
        - name: config-volume
          mountPath: /etc/config
        - name: data-volume
          mountPath: /data
      volumes:
      - name: config-volume
        configMap:
          name: app-config
      - name: data-volume
        persistentVolumeClaim:
          claimName: data-pvc
      imagePullSecrets:
      - name: regcred
---
apiVersion: v1
kind: Service
metadata:
  name: myapp-service
  namespace: production
spec:
  type: LoadBalancer
  selector:
    app: myapp
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: myapp-hpa
  namespace: production
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: myapp
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

---

## Quick Reference

### Most Common Commands
```bash
# View resources
kubectl get pods
kubectl get deployments
kubectl get services
kubectl get all

# Describe (detailed info)
kubectl describe pod <name>

# Logs
kubectl logs -f <pod-name>

# Execute command
kubectl exec -it <pod-name> -- bash

# Apply configuration
kubectl apply -f <file.yaml>

# Scale
kubectl scale deployment <name> --replicas=3

# Port forward
kubectl port-forward <pod-name> 8080:80
```

### Resource Shortnames
```bash
po = pods
deploy = deployments
svc = services
ns = namespaces
no = nodes
cm = configmaps
pv = persistentvolumes
pvc = persistentvolumeclaims
sa = serviceaccounts
```

---

## Useful Aliases

Add these to your `~/.bashrc` or `~/.zshrc`:

```bash
alias k='kubectl'
alias kg='kubectl get'
alias kd='kubectl describe'
alias kdel='kubectl delete'
alias kl='kubectl logs'
alias kex='kubectl exec -it'
alias kaf='kubectl apply -f'
alias kdf='kubectl delete -f'

# With watch
alias kgpw='kubectl get pods -w'
alias kgdw='kubectl get deployments -w'

# All namespaces
alias kgpa='kubectl get pods --all-namespaces'
alias kgda='kubectl get deployments --all-namespaces'
```

---

## Additional Resources

- [Official Kubernetes Documentation](https://kubernetes.io/docs/)
- [kubectl Cheat Sheet](https://kubernetes.io/docs/reference/kubectl/cheatsheet/)
- [Play with Kubernetes](https://labs.play-with-k8s.com/)
- [Kubernetes the Hard Way](https://github.com/kelseyhightower/kubernetes-the-hard-way)

---

**Keep this cheat sheet handy for daily Kubernetes operations!**
