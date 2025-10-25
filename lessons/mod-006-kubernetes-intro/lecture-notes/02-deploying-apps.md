# Lecture 02: Deploying Applications on Kubernetes

## Table of Contents
1. [Introduction](#introduction)
2. [Pods: The Atomic Unit](#pods-the-atomic-unit)
3. [ReplicaSets: Maintaining Desired State](#replicasets-maintaining-desired-state)
4. [Deployments: Declarative Updates](#deployments-declarative-updates)
5. [Services: Stable Network Endpoints](#services-stable-network-endpoints)
6. [ConfigMaps: Configuration Management](#configmaps-configuration-management)
7. [Secrets: Sensitive Data Management](#secrets-sensitive-data-management)
8. [Persistent Storage](#persistent-storage)
9. [Complete Application Example](#complete-application-example)
10. [Best Practices](#best-practices)
11. [Summary and Key Takeaways](#summary-and-key-takeaways)

## Introduction

In the previous lecture, you learned how Kubernetes works architecturally. Now it's time to put that knowledge into practice by deploying actual applications to Kubernetes. This lecture covers the core workload resources you'll use daily as an AI infrastructure engineer.

### Learning Objectives

By the end of this lecture, you will:
- Create and manage Pods effectively
- Use ReplicaSets to maintain desired replica counts
- Deploy applications with Deployments and perform rolling updates
- Expose applications using different Service types
- Manage application configuration with ConfigMaps and Secrets
- Understand persistent storage with Volumes and PersistentVolumeClaims
- Deploy a complete multi-tier application
- Apply best practices for production deployments

### Prerequisites
- Lecture 01: Kubernetes Architecture
- kubectl installed and configured
- Access to a Kubernetes cluster (Docker Desktop, Minikube, or cloud)
- Basic understanding of YAML syntax

### Verify Your Environment

```bash
# Check cluster access
kubectl cluster-info

# Verify nodes are ready
kubectl get nodes

# Check current context
kubectl config current-context

# Create a test namespace for this lecture
kubectl create namespace lecture-02-demo
kubectl config set-context --current --namespace=lecture-02-demo
```

## Pods: The Atomic Unit

A **Pod** is the smallest deployable unit in Kubernetes. It represents a single instance of a running process in your cluster.

### Pod Fundamentals

**Key Characteristics**:
- Pods contain one or more containers (usually one)
- Containers in a Pod share the same network namespace (same IP, same ports)
- Containers in a Pod share the same storage volumes
- Pods are ephemeral - they can be created and destroyed at any time
- Each Pod gets a unique IP address (within the cluster)

### Single-Container Pod

The most common pattern: one container per Pod.

```yaml
# simple-pod.yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx-pod
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
```

**Create the Pod**:
```bash
kubectl apply -f simple-pod.yaml

# Watch it start
kubectl get pods -w

# View details
kubectl describe pod nginx-pod

# View logs
kubectl logs nginx-pod

# Access the Pod (port-forward)
kubectl port-forward nginx-pod 8080:80
# Visit http://localhost:8080
```

### Multi-Container Pod

Sometimes you need multiple containers in a Pod (sidecar pattern).

```yaml
# multi-container-pod.yaml
apiVersion: v1
kind: Pod
metadata:
  name: app-with-logging
spec:
  containers:
  # Main application container
  - name: app
    image: busybox
    command: ['sh', '-c', 'while true; do echo "$(date) - Application log" >> /var/log/app.log; sleep 5; done']
    volumeMounts:
    - name: shared-logs
      mountPath: /var/log

  # Sidecar container for log processing
  - name: log-shipper
    image: busybox
    command: ['sh', '-c', 'tail -f /var/log/app.log']
    volumeMounts:
    - name: shared-logs
      mountPath: /var/log

  volumes:
  - name: shared-logs
    emptyDir: {}
```

**Key Points**:
- Both containers share the same network (can communicate via localhost)
- Both containers share the same volume (shared-logs)
- If either container fails, the whole Pod fails

```bash
kubectl apply -f multi-container-pod.yaml

# View logs from specific container
kubectl logs app-with-logging -c app
kubectl logs app-with-logging -c log-shipper
```

### Common Multi-Container Patterns

**1. Sidecar Pattern**: Helper container enhances main container
```
Main Container → App
Sidecar Container → Log shipping, metrics collection, proxying
```

**2. Ambassador Pattern**: Proxy container for external services
```
Main Container → Connects to localhost:6379
Ambassador Container → Proxies to external Redis cluster
```

**3. Adapter Pattern**: Standardizes output/interface
```
Main Container → Custom metrics format
Adapter Container → Converts to Prometheus format
```

### Pod Lifecycle

```
Pending → ContainerCreating → Running → Succeeded/Failed
                                  ↓
                          CrashLoopBackOff (if failing)
```

**Pod Phases**:
- **Pending**: Pod accepted, but containers not yet created
- **Running**: Pod bound to node, at least one container running
- **Succeeded**: All containers terminated successfully
- **Failed**: All containers terminated, at least one failed
- **Unknown**: Pod state cannot be determined

### Resource Requests and Limits

Always specify resource requirements for production workloads.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: resource-pod
spec:
  containers:
  - name: app
    image: nginx
    resources:
      requests:       # Minimum guaranteed resources
        memory: "128Mi"
        cpu: "250m"   # 250 millicores = 0.25 CPU
      limits:         # Maximum allowed resources
        memory: "256Mi"
        cpu: "500m"   # 500 millicores = 0.5 CPU
```

**Resource Units**:
- **CPU**: `1` = 1 CPU core, `1000m` = 1 core, `100m` = 0.1 core
- **Memory**: `128Mi` = 128 mebibytes, `1Gi` = 1 gibibyte, `1000M` = 1000 megabytes

**Behavior**:
- **Requests**: Used by scheduler to find suitable node
- **Limits**: Enforced by kubelet; container killed if exceeded (memory), throttled (CPU)

### Health Probes

Kubernetes can monitor container health and take action.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: healthy-pod
spec:
  containers:
  - name: web
    image: nginx:1.21
    ports:
    - containerPort: 80

    # Liveness probe - is container alive?
    livenessProbe:
      httpGet:
        path: /
        port: 80
      initialDelaySeconds: 10
      periodSeconds: 10
      timeoutSeconds: 2
      failureThreshold: 3

    # Readiness probe - is container ready for traffic?
    readinessProbe:
      httpGet:
        path: /
        port: 80
      initialDelaySeconds: 5
      periodSeconds: 5
      timeoutSeconds: 2
      failureThreshold: 3

    # Startup probe - has slow-starting container started?
    startupProbe:
      httpGet:
        path: /
        port: 80
      initialDelaySeconds: 0
      periodSeconds: 10
      failureThreshold: 30  # 30 * 10 = 5 minutes to start
```

**Probe Types**:
1. **exec**: Execute command in container (exit code 0 = success)
2. **httpGet**: HTTP GET request (status code 200-399 = success)
3. **tcpSocket**: TCP connection (successful connection = success)
4. **grpc**: gRPC health check (requires gRPC health checking protocol)

**When to Use Each Probe**:
- **Liveness**: Detect deadlocked/hung containers → restart
- **Readiness**: Control when Pod receives traffic → remove from Service
- **Startup**: Protect slow-starting containers from liveness probe

### Init Containers

Init containers run before application containers and must complete successfully.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: init-pod
spec:
  # Init containers run sequentially before main containers
  initContainers:
  - name: download-data
    image: busybox
    command: ['sh', '-c', 'wget -O /data/model.pkl https://example.com/model.pkl']
    volumeMounts:
    - name: data
      mountPath: /data

  - name: check-dependencies
    image: busybox
    command: ['sh', '-c', 'until nslookup redis-service; do echo waiting for redis; sleep 2; done']

  # Main application container starts after init containers succeed
  containers:
  - name: app
    image: ml-inference:latest
    volumeMounts:
    - name: data
      mountPath: /data

  volumes:
  - name: data
    emptyDir: {}
```

**Common Use Cases**:
- Download dependencies or configuration
- Wait for external services to be ready
- Set up permissions or data
- Populate shared volumes

### Pod Best Practices

1. **Use labels**: Organize and select Pods effectively
2. **Set resource requests/limits**: Enable proper scheduling and avoid resource contention
3. **Use health probes**: Enable self-healing and proper traffic routing
4. **Don't run as root**: Use securityContext to drop privileges
5. **Single concern per container**: Keep containers focused
6. **Use specific image tags**: Avoid `latest` in production

## ReplicaSets: Maintaining Desired State

A **ReplicaSet** ensures that a specified number of Pod replicas are running at any given time.

### ReplicaSet Basics

```yaml
# replicaset.yaml
apiVersion: apps/v1
kind: ReplicaSet
metadata:
  name: nginx-replicaset
  labels:
    app: nginx
spec:
  replicas: 3           # Desired number of Pods
  selector:             # Which Pods to manage
    matchLabels:
      app: nginx
      tier: frontend
  template:             # Pod template
    metadata:
      labels:           # Must match selector
        app: nginx
        tier: frontend
    spec:
      containers:
      - name: nginx
        image: nginx:1.21
        ports:
        - containerPort: 80
```

```bash
kubectl apply -f replicaset.yaml

# View ReplicaSet
kubectl get replicasets
kubectl get rs  # shorthand

# View Pods created by ReplicaSet
kubectl get pods -l app=nginx

# Scale ReplicaSet
kubectl scale replicaset nginx-replicaset --replicas=5

# Delete a Pod - watch it be recreated!
kubectl delete pod <pod-name>
kubectl get pods -w
```

### How ReplicaSets Work

```
ReplicaSet Controller watches for:
- ReplicaSet objects
- Pod objects with matching labels

Reconciliation loop:
1. Count current Pods with matching labels
2. Compare to desired replicas
3. Create new Pods if count < desired
4. Delete excess Pods if count > desired
```

### Label Selectors

ReplicaSets use labels to identify which Pods they manage.

```yaml
# Equality-based selector
selector:
  matchLabels:
    app: nginx
    environment: production

# Set-based selector
selector:
  matchExpressions:
  - key: tier
    operator: In
    values: [frontend, backend]
  - key: environment
    operator: NotIn
    values: [development]
```

**Important**: ReplicaSet selector is **immutable** after creation!

### When NOT to Use ReplicaSets Directly

ReplicaSets are rarely created directly. Instead, use **Deployments**, which manage ReplicaSets for you and provide additional features:
- Rolling updates
- Rollback capability
- Update strategies
- Revision history

## Deployments: Declarative Updates

A **Deployment** provides declarative updates for Pods and ReplicaSets. It's the recommended way to deploy stateless applications.

### Basic Deployment

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
  labels:
    app: nginx
spec:
  replicas: 3
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
        image: nginx:1.21
        ports:
        - containerPort: 80
        resources:
          requests:
            memory: "64Mi"
            cpu: "100m"
          limits:
            memory: "128Mi"
            cpu: "200m"
```

```bash
kubectl apply -f deployment.yaml

# View Deployment
kubectl get deployments
kubectl get deploy  # shorthand

# View ReplicaSets created by Deployment
kubectl get replicasets

# View Pods
kubectl get pods

# View deployment details
kubectl describe deployment nginx-deployment

# View rollout status
kubectl rollout status deployment/nginx-deployment
```

### Deployment Hierarchy

```
Deployment
    ↓ (creates and manages)
ReplicaSet
    ↓ (creates and manages)
Pods
```

### Scaling Deployments

```bash
# Imperative scaling
kubectl scale deployment nginx-deployment --replicas=5

# Declarative scaling (preferred)
# Edit deployment.yaml: replicas: 5
kubectl apply -f deployment.yaml

# Autoscaling (HPA)
kubectl autoscale deployment nginx-deployment --min=2 --max=10 --cpu-percent=80
```

### Rolling Updates

Deployments enable zero-downtime updates through rolling updates.

```yaml
# Update strategy configuration
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1        # Max Pods above desired during update
      maxUnavailable: 1  # Max Pods below desired during update
```

**Update Deployment**:
```bash
# Method 1: Update image
kubectl set image deployment/nginx-deployment nginx=nginx:1.22

# Method 2: Edit in-place
kubectl edit deployment nginx-deployment

# Method 3: Update manifest and apply (preferred)
# Edit deployment.yaml: image: nginx:1.22
kubectl apply -f deployment.yaml

# Watch rollout
kubectl rollout status deployment/nginx-deployment

# View rollout history
kubectl rollout history deployment/nginx-deployment
```

**Rolling Update Process**:
```
Initial state: 3 replicas of nginx:1.21

1. Create new ReplicaSet for nginx:1.22
2. Scale new ReplicaSet to 1 (surge)
   Old: 3, New: 1  (total: 4, maxSurge: 1)
3. Wait for new Pod to be ready
4. Scale old ReplicaSet to 2
   Old: 2, New: 1  (total: 3)
5. Scale new ReplicaSet to 2
   Old: 2, New: 2  (total: 4)
6. Scale old ReplicaSet to 1
   Old: 1, New: 2  (total: 3)
7. Scale new ReplicaSet to 3
   Old: 1, New: 3  (total: 4)
8. Scale old ReplicaSet to 0
   Old: 0, New: 3  (total: 3)
9. Done!
```

### Rollbacks

If an update goes wrong, roll back to a previous version.

```bash
# View rollout history
kubectl rollout history deployment/nginx-deployment

# View specific revision
kubectl rollout history deployment/nginx-deployment --revision=2

# Rollback to previous version
kubectl rollout undo deployment/nginx-deployment

# Rollback to specific revision
kubectl rollout undo deployment/nginx-deployment --to-revision=2

# Pause rollout (for troubleshooting)
kubectl rollout pause deployment/nginx-deployment

# Resume rollout
kubectl rollout resume deployment/nginx-deployment
```

### Update Strategies

**1. RollingUpdate** (default):
```yaml
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxSurge: 25%        # Can be number or percentage
    maxUnavailable: 25%
```
- Gradual replacement of old Pods with new Pods
- Zero downtime
- Both versions running temporarily

**2. Recreate**:
```yaml
strategy:
  type: Recreate
```
- All old Pods terminated before new Pods created
- Downtime occurs
- Only one version running at a time
- Useful when simultaneous versions cause issues

### Deployment for ML Model Serving

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ml-model-server
  labels:
    app: ml-model
    version: v1
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ml-model
  template:
    metadata:
      labels:
        app: ml-model
        version: v1
    spec:
      containers:
      - name: model-server
        image: tensorflow/serving:2.8.0
        ports:
        - name: http
          containerPort: 8501
        - name: grpc
          containerPort: 8500
        env:
        - name: MODEL_NAME
          value: "my_model"
        - name: MODEL_BASE_PATH
          value: "/models"
        resources:
          requests:
            memory: "2Gi"
            cpu: "1"
          limits:
            memory: "4Gi"
            cpu: "2"
            nvidia.com/gpu: "1"
        livenessProbe:
          httpGet:
            path: /v1/models/my_model
            port: 8501
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /v1/models/my_model
            port: 8501
          initialDelaySeconds: 10
          periodSeconds: 5
        volumeMounts:
        - name: model-storage
          mountPath: /models
      volumes:
      - name: model-storage
        persistentVolumeClaim:
          claimName: model-pvc
```

## Services: Stable Network Endpoints

Pods are ephemeral and have dynamic IP addresses. **Services** provide stable network endpoints and load balancing.

### Why Services?

**Problem**: Pod IPs change when:
- Pods are rescheduled
- Deployments are updated
- Pods crash and are recreated

**Solution**: Services provide:
- Stable IP address (ClusterIP)
- Stable DNS name
- Load balancing across Pod backends
- Service discovery

### Service Types

1. **ClusterIP** (default): Internal cluster IP only
2. **NodePort**: Exposes service on each node's IP at a static port
3. **LoadBalancer**: Provisions cloud load balancer
4. **ExternalName**: Maps to external DNS name

### ClusterIP Service

Most common type for internal services.

```yaml
# service-clusterip.yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx-service
spec:
  type: ClusterIP           # Default, can be omitted
  selector:                 # Pods with these labels are backends
    app: nginx
  ports:
  - name: http
    protocol: TCP
    port: 80                # Service port
    targetPort: 80          # Container port
```

```bash
kubectl apply -f service-clusterip.yaml

# View service
kubectl get services
kubectl get svc  # shorthand

# Describe service (shows endpoints)
kubectl describe service nginx-service

# Service is accessible within cluster
kubectl run test-pod --rm -it --image=busybox -- sh
# Inside pod:
wget -qO- nginx-service
wget -qO- nginx-service.default.svc.cluster.local
```

**DNS Names**:
```
<service-name>.<namespace>.svc.cluster.local

# Examples:
nginx-service.default.svc.cluster.local
redis-cache.production.svc.cluster.local

# Short forms (from same namespace):
nginx-service
```

### How Services Work

```
1. Service created with selector: app=nginx
2. Endpoints controller watches Service and Pods
3. Finds all Pods with label app=nginx
4. Creates Endpoints object with Pod IPs:
   - 10.244.1.5:80
   - 10.244.2.3:80
   - 10.244.3.7:80
5. kube-proxy watches Service and Endpoints
6. Updates iptables/ipvs rules:
   - Traffic to Service ClusterIP → Load balanced to Pod IPs
```

**View Endpoints**:
```bash
kubectl get endpoints nginx-service
kubectl get ep nginx-service  # shorthand
```

### NodePort Service

Exposes service on each node's IP at a static port (30000-32767).

```yaml
# service-nodeport.yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx-nodeport
spec:
  type: NodePort
  selector:
    app: nginx
  ports:
  - name: http
    protocol: TCP
    port: 80              # Service port (cluster-internal)
    targetPort: 80        # Container port
    nodePort: 30080       # Node port (optional, auto-assigned if omitted)
```

```bash
kubectl apply -f service-nodeport.yaml
kubectl get service nginx-nodeport

# Access from outside cluster
# Get node IP
kubectl get nodes -o wide

# Access service
curl http://<NODE-IP>:30080
```

**Traffic Flow**:
```
External Client
    ↓
<any-node-ip>:30080 (NodePort)
    ↓
Service ClusterIP:80
    ↓
Load balanced to Pod:80
```

### LoadBalancer Service

Provisions a cloud load balancer (works on cloud platforms).

```yaml
# service-loadbalancer.yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx-loadbalancer
spec:
  type: LoadBalancer
  selector:
    app: nginx
  ports:
  - name: http
    protocol: TCP
    port: 80
    targetPort: 80
```

```bash
kubectl apply -f service-loadbalancer.yaml

# Get external IP (takes ~1 minute on cloud)
kubectl get service nginx-loadbalancer -w

# Access via external IP
curl http://<EXTERNAL-IP>
```

**Cloud Provisioning**:
- AWS: Creates ELB/ALB/NLB
- GCP: Creates Google Cloud Load Balancer
- Azure: Creates Azure Load Balancer

**Traffic Flow**:
```
External Client
    ↓
Cloud Load Balancer (external IP)
    ↓
NodePort on nodes
    ↓
Service ClusterIP
    ↓
Pod backends
```

### ExternalName Service

Maps service to external DNS name (no selectors or endpoints).

```yaml
# service-externalname.yaml
apiVersion: v1
kind: Service
metadata:
  name: external-database
spec:
  type: ExternalName
  externalName: database.example.com
```

```bash
# Pods can access external service via internal name
mysql -h external-database -u user -p
# Actually connects to database.example.com
```

### Headless Services

Service without ClusterIP for direct Pod access.

```yaml
# service-headless.yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx-headless
spec:
  clusterIP: None       # Headless service
  selector:
    app: nginx
  ports:
  - port: 80
    targetPort: 80
```

```bash
# DNS returns Pod IPs directly, not Service IP
nslookup nginx-headless.default.svc.cluster.local

# Returns:
# nginx-headless.default.svc.cluster.local has address 10.244.1.5
# nginx-headless.default.svc.cluster.local has address 10.244.2.3
# nginx-headless.default.svc.cluster.local has address 10.244.3.7
```

**Use Cases**:
- StatefulSets (need to address specific Pods)
- Client-side load balancing
- Service discovery without load balancing

### Service Best Practices

1. **Use ClusterIP by default**: Only expose externally when needed
2. **Name ports**: Use named ports for clarity and flexibility
3. **Session affinity**: Use `sessionAffinity: ClientIP` if needed
4. **Health checks**: Ensure Pods have readiness probes
5. **Namespace services**: Use namespaces to organize services

## ConfigMaps: Configuration Management

**ConfigMaps** store non-confidential configuration data as key-value pairs.

### Creating ConfigMaps

**Method 1: From literal values**:
```bash
kubectl create configmap app-config \
  --from-literal=database_host=postgres.default \
  --from-literal=database_port=5432 \
  --from-literal=log_level=info
```

**Method 2: From file**:
```bash
# Create config file
cat > app.properties <<EOF
database.host=postgres.default
database.port=5432
log.level=info
EOF

kubectl create configmap app-config --from-file=app.properties
```

**Method 3: From YAML**:
```yaml
# configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  database_host: "postgres.default"
  database_port: "5432"
  log_level: "info"
  # Multi-line configuration
  app.properties: |
    database.host=postgres.default
    database.port=5432
    log.level=info
    feature.experimental=true
```

```bash
kubectl apply -f configmap.yaml

# View ConfigMap
kubectl get configmaps
kubectl describe configmap app-config
kubectl get configmap app-config -o yaml
```

### Using ConfigMaps

**1. Environment Variables**:
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: app-pod
spec:
  containers:
  - name: app
    image: myapp:latest
    env:
    # Single key
    - name: DATABASE_HOST
      valueFrom:
        configMapKeyRef:
          name: app-config
          key: database_host

    # All keys as env vars
    envFrom:
    - configMapRef:
        name: app-config
```

**2. Volume Mount** (for config files):
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: app-pod
spec:
  containers:
  - name: app
    image: myapp:latest
    volumeMounts:
    - name: config-volume
      mountPath: /etc/config
  volumes:
  - name: config-volume
    configMap:
      name: app-config
```

Files created in container:
```
/etc/config/database_host
/etc/config/database_port
/etc/config/log_level
/etc/config/app.properties
```

**3. Specific Keys as Files**:
```yaml
volumes:
- name: config-volume
  configMap:
    name: app-config
    items:
    - key: app.properties
      path: application.properties
```

Creates: `/etc/config/application.properties`

### ML Configuration Example

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: ml-model-config
data:
  MODEL_NAME: "resnet50"
  MODEL_VERSION: "1.0.0"
  BATCH_SIZE: "32"
  MAX_BATCH_DELAY: "5000"
  NUM_THREADS: "4"
  model_config.json: |
    {
      "model_name": "resnet50",
      "model_platform": "tensorflow",
      "input_format": "NHWC",
      "output_nodes": ["predictions"],
      "optimization_level": "2"
    }
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ml-model-server
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ml-model
  template:
    metadata:
      labels:
        app: ml-model
    spec:
      containers:
      - name: model-server
        image: tensorflow/serving:latest
        envFrom:
        - configMapRef:
            name: ml-model-config
        volumeMounts:
        - name: config
          mountPath: /config
      volumes:
      - name: config
        configMap:
          name: ml-model-config
          items:
          - key: model_config.json
            path: model_config.json
```

### ConfigMap Updates

```bash
# Update ConfigMap
kubectl edit configmap app-config

# Or apply updated YAML
kubectl apply -f configmap.yaml
```

**Important**:
- Pods do **NOT** automatically restart on ConfigMap updates
- Environment variables are **NOT** updated (set at Pod creation)
- Mounted files **ARE** updated (eventually consistent, ~1 minute)

**Force Pod update**:
```bash
# Trigger rollout by updating deployment annotation
kubectl patch deployment myapp -p \
  '{"spec":{"template":{"metadata":{"annotations":{"configmap-version":"'$(date +%s)'"}}}}}'
```

## Secrets: Sensitive Data Management

**Secrets** store sensitive data like passwords, tokens, and keys.

### Creating Secrets

**Method 1: From literal values**:
```bash
kubectl create secret generic db-credentials \
  --from-literal=username=admin \
  --from-literal=password=super-secret-password
```

**Method 2: From files**:
```bash
echo -n 'admin' > username.txt
echo -n 'super-secret-password' > password.txt
kubectl create secret generic db-credentials \
  --from-file=username.txt \
  --from-file=password.txt
```

**Method 3: From YAML** (values must be base64 encoded):
```bash
# Encode values
echo -n 'admin' | base64  # YWRtaW4=
echo -n 'super-secret-password' | base64  # c3VwZXItc2VjcmV0LXBhc3N3b3Jk
```

```yaml
# secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: db-credentials
type: Opaque
data:
  username: YWRtaW4=
  password: c3VwZXItc2VjcmV0LXBhc3N3b3Jk
```

```bash
kubectl apply -f secret.yaml

# View secret (values hidden)
kubectl get secret db-credentials
kubectl describe secret db-credentials

# Decode secret
kubectl get secret db-credentials -o jsonpath='{.data.password}' | base64 -d
```

### Secret Types

- **Opaque** (default): Arbitrary user-defined data
- **kubernetes.io/service-account-token**: Service account token
- **kubernetes.io/dockerconfigjson**: Docker registry credentials
- **kubernetes.io/tls**: TLS certificate and key
- **kubernetes.io/ssh-auth**: SSH credentials
- **kubernetes.io/basic-auth**: Basic authentication

### Using Secrets

**1. Environment Variables**:
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: app-pod
spec:
  containers:
  - name: app
    image: myapp:latest
    env:
    - name: DB_USERNAME
      valueFrom:
        secretKeyRef:
          name: db-credentials
          key: username
    - name: DB_PASSWORD
      valueFrom:
        secretKeyRef:
          name: db-credentials
          key: password
```

**2. Volume Mount** (more secure):
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: app-pod
spec:
  containers:
  - name: app
    image: myapp:latest
    volumeMounts:
    - name: secret-volume
      mountPath: /etc/secrets
      readOnly: true
  volumes:
  - name: secret-volume
    secret:
      secretName: db-credentials
```

Files created in container:
```
/etc/secrets/username
/etc/secrets/password
```

**Read in application**:
```python
# Read from file (more secure than env vars)
with open('/etc/secrets/username') as f:
    username = f.read()
with open('/etc/secrets/password') as f:
    password = f.read()
```

### Docker Registry Secret

For pulling from private container registries:

```bash
kubectl create secret docker-registry regcred \
  --docker-server=https://index.docker.io/v1/ \
  --docker-username=myuser \
  --docker-password=mypassword \
  --docker-email=myemail@example.com
```

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: private-pod
spec:
  containers:
  - name: app
    image: myregistry/private-image:latest
  imagePullSecrets:
  - name: regcred
```

### TLS Secret

For HTTPS endpoints:

```bash
kubectl create secret tls tls-secret \
  --cert=path/to/cert.pem \
  --key=path/to/key.pem
```

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: tls-ingress
spec:
  tls:
  - hosts:
    - myapp.example.com
    secretName: tls-secret
  rules:
  - host: myapp.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: myapp
            port:
              number: 80
```

### Secret Best Practices

1. **Use volume mounts** instead of environment variables (more secure)
2. **Restrict RBAC access** to secrets
3. **Enable encryption at rest** in etcd
4. **Use external secret managers** (AWS Secrets Manager, HashiCorp Vault)
5. **Rotate secrets regularly**
6. **Don't commit secrets** to Git (use .gitignore)
7. **Use namespaces** to isolate secrets
8. **Limit secret size** (max 1MB per secret)

### External Secrets Operator

For production, consider using External Secrets Operator:

```yaml
apiVersion: external-secrets.io/v1beta1
kind: SecretStore
metadata:
  name: aws-secret-store
spec:
  provider:
    aws:
      service: SecretsManager
      region: us-west-2
---
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: db-credentials
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: aws-secret-store
  target:
    name: db-credentials
  data:
  - secretKey: username
    remoteRef:
      key: prod/db/credentials
      property: username
  - secretKey: password
    remoteRef:
      key: prod/db/credentials
      property: password
```

## Persistent Storage

Pods are ephemeral, but data often needs to persist. Kubernetes provides several storage abstractions.

### Storage Hierarchy

```
Storage Class
    ↓ (provisions)
Persistent Volume (PV)
    ↓ (bound to)
Persistent Volume Claim (PVC)
    ↓ (mounted in)
Pod
```

### Volume Types

**1. emptyDir**: Temporary storage (deleted when Pod deleted)
```yaml
volumes:
- name: temp-storage
  emptyDir: {}
```

**2. hostPath**: Node's filesystem (not recommended for production)
```yaml
volumes:
- name: host-storage
  hostPath:
    path: /data
    type: Directory
```

**3. PersistentVolumeClaim**: Durable storage
```yaml
volumes:
- name: data-storage
  persistentVolumeClaim:
    claimName: my-pvc
```

### PersistentVolume (PV)

Cluster storage resource provisioned by admin or dynamically.

```yaml
# pv.yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: my-pv
spec:
  capacity:
    storage: 100Gi
  accessModes:
  - ReadWriteOnce      # Single node read-write
  persistentVolumeReclaimPolicy: Retain
  storageClassName: fast
  hostPath:            # For demo only; use cloud volumes in production
    path: /mnt/data
```

**Access Modes**:
- **ReadWriteOnce** (RWO): Single node, read-write
- **ReadOnlyMany** (ROX): Multiple nodes, read-only
- **ReadWriteMany** (RWX): Multiple nodes, read-write (rare, usually NFS)

**Reclaim Policies**:
- **Retain**: Manual reclamation (default for manually created PVs)
- **Delete**: Delete volume when PVC deleted (default for dynamic provisioning)
- **Recycle**: Scrub volume and make available again (deprecated)

### PersistentVolumeClaim (PVC)

Request for storage by user.

```yaml
# pvc.yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: my-pvc
spec:
  accessModes:
  - ReadWriteOnce
  resources:
    requests:
      storage: 50Gi    # Request 50Gi (PV has 100Gi)
  storageClassName: fast
```

```bash
kubectl apply -f pvc.yaml

# View PVCs
kubectl get pvc

# View binding
kubectl describe pvc my-pvc
```

**Binding Process**:
```
1. User creates PVC requesting 50Gi with accessMode RWO
2. Kubernetes finds PV with:
   - At least 50Gi capacity
   - AccessMode RWO
   - Matching storageClassName
3. Binds PVC to PV
4. PVC status: Bound
```

### Using PVC in Pod

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: app-with-storage
spec:
  containers:
  - name: app
    image: myapp:latest
    volumeMounts:
    - name: data
      mountPath: /data
  volumes:
  - name: data
    persistentVolumeClaim:
      claimName: my-pvc
```

### Dynamic Provisioning

StorageClass enables dynamic PV provisioning.

```yaml
# storageclass.yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast-ssd
provisioner: kubernetes.io/aws-ebs  # Cloud provider provisioner
parameters:
  type: gp3
  iops: "3000"
  throughput: "125"
allowVolumeExpansion: true
volumeBindingMode: WaitForFirstConsumer
```

**PVC with StorageClass**:
```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: dynamic-pvc
spec:
  accessModes:
  - ReadWriteOnce
  resources:
    requests:
      storage: 100Gi
  storageClassName: fast-ssd  # Uses StorageClass
```

```bash
kubectl apply -f dynamic-pvc.yaml

# PV automatically created!
kubectl get pv
kubectl get pvc
```

### ML Storage Example

```yaml
# ML model storage
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: model-storage
spec:
  accessModes:
  - ReadWriteMany  # Multiple Pods need access
  resources:
    requests:
      storage: 1Ti
  storageClassName: nfs
---
# ML training data
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: training-data
spec:
  accessModes:
  - ReadWriteMany
  resources:
    requests:
      storage: 10Ti
  storageClassName: s3-csi  # S3-backed storage
---
# ML training job
apiVersion: batch/v1
kind: Job
metadata:
  name: training-job
spec:
  template:
    spec:
      restartPolicy: OnFailure
      containers:
      - name: trainer
        image: pytorch/pytorch:latest
        command: ["python", "train.py"]
        volumeMounts:
        - name: training-data
          mountPath: /data
          readOnly: true
        - name: model-output
          mountPath: /models
      volumes:
      - name: training-data
        persistentVolumeClaim:
          claimName: training-data
      - name: model-output
        persistentVolumeClaim:
          claimName: model-storage
```

### Volume Snapshots

Create backups of volumes:

```yaml
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshot
metadata:
  name: model-snapshot
spec:
  volumeSnapshotClassName: csi-snapclass
  source:
    persistentVolumeClaimName: model-storage
```

## Complete Application Example

Let's deploy a complete multi-tier application: a web frontend, API backend, and database.

### Application Architecture

```
Internet
    ↓
LoadBalancer Service (frontend)
    ↓
Frontend Deployment (3 replicas)
    ↓
ClusterIP Service (api)
    ↓
Backend Deployment (3 replicas)
    ↓
ClusterIP Service (database)
    ↓
Database StatefulSet (1 replica)
    ↓
PersistentVolumeClaim
```

### Database Layer

```yaml
# database.yaml
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: postgres-config
data:
  POSTGRES_DB: "myapp"
---
apiVersion: v1
kind: Secret
metadata:
  name: postgres-secret
type: Opaque
data:
  POSTGRES_USER: YWRtaW4=        # admin
  POSTGRES_PASSWORD: cGFzc3dvcmQ=  # password
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgres-pvc
spec:
  accessModes:
  - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
spec:
  serviceName: postgres
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:14
        ports:
        - containerPort: 5432
        envFrom:
        - configMapRef:
            name: postgres-config
        - secretRef:
            name: postgres-secret
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/postgresql/data
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
      volumes:
      - name: postgres-storage
        persistentVolumeClaim:
          claimName: postgres-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: postgres
spec:
  selector:
    app: postgres
  ports:
  - port: 5432
    targetPort: 5432
  clusterIP: None  # Headless service for StatefulSet
```

### Backend API Layer

```yaml
# backend.yaml
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: backend-config
data:
  DATABASE_HOST: "postgres"
  DATABASE_PORT: "5432"
  DATABASE_NAME: "myapp"
  LOG_LEVEL: "info"
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
        version: v1
    spec:
      containers:
      - name: api
        image: myapp/backend:v1
        ports:
        - containerPort: 8080
        envFrom:
        - configMapRef:
            name: backend-config
        env:
        - name: DATABASE_USER
          valueFrom:
            secretKeyRef:
              name: postgres-secret
              key: POSTGRES_USER
        - name: DATABASE_PASSWORD
          valueFrom:
            secretKeyRef:
              name: postgres-secret
              key: POSTGRES_PASSWORD
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 10
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: backend
spec:
  selector:
    app: backend
  ports:
  - port: 8080
    targetPort: 8080
```

### Frontend Layer

```yaml
# frontend.yaml
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: frontend-config
data:
  API_URL: "http://backend:8080"
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: frontend
  template:
    metadata:
      labels:
        app: frontend
        version: v1
    spec:
      containers:
      - name: web
        image: myapp/frontend:v1
        ports:
        - containerPort: 80
        envFrom:
        - configMapRef:
            name: frontend-config
        resources:
          requests:
            memory: "64Mi"
            cpu: "50m"
          limits:
            memory: "128Mi"
            cpu: "100m"
        livenessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 10
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: frontend
spec:
  type: LoadBalancer
  selector:
    app: frontend
  ports:
  - port: 80
    targetPort: 80
```

### Deploy the Application

```bash
# Deploy in order
kubectl apply -f database.yaml
kubectl wait --for=condition=ready pod -l app=postgres --timeout=60s

kubectl apply -f backend.yaml
kubectl wait --for=condition=ready pod -l app=backend --timeout=60s

kubectl apply -f frontend.yaml

# Check status
kubectl get all

# Get external IP
kubectl get service frontend

# Test application
curl http://<EXTERNAL-IP>
```

## Best Practices

### Resource Management

1. **Always set resource requests and limits**:
```yaml
resources:
  requests:     # For scheduling
    memory: "128Mi"
    cpu: "100m"
  limits:       # Prevent resource hogging
    memory: "256Mi"
    cpu: "200m"
```

2. **Use ResourceQuotas** per namespace:
```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: compute-quota
spec:
  hard:
    requests.cpu: "100"
    requests.memory: "200Gi"
    limits.cpu: "200"
    limits.memory: "400Gi"
    persistentvolumeclaims: "10"
```

3. **Use LimitRanges** for defaults:
```yaml
apiVersion: v1
kind: LimitRange
metadata:
  name: default-limits
spec:
  limits:
  - default:
      memory: "256Mi"
      cpu: "200m"
    defaultRequest:
      memory: "128Mi"
      cpu: "100m"
    type: Container
```

### Health Checks

Always implement health probes:

```yaml
livenessProbe:    # Restart if unhealthy
  httpGet:
    path: /health
    port: 8080
  initialDelaySeconds: 30
  periodSeconds: 10
  timeoutSeconds: 5
  failureThreshold: 3

readinessProbe:   # Remove from service if not ready
  httpGet:
    path: /ready
    port: 8080
  initialDelaySeconds: 10
  periodSeconds: 5
  timeoutSeconds: 2
  failureThreshold: 3
```

### Security

1. **Don't run as root**:
```yaml
securityContext:
  runAsNonRoot: true
  runAsUser: 1000
  fsGroup: 2000
  capabilities:
    drop:
    - ALL
```

2. **Use read-only root filesystem**:
```yaml
securityContext:
  readOnlyRootFilesystem: true
```

3. **Use Pod Security Standards**:
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: production
  labels:
    pod-security.kubernetes.io/enforce: restricted
```

### Labels and Annotations

Use consistent labeling:

```yaml
metadata:
  labels:
    app.kubernetes.io/name: myapp
    app.kubernetes.io/instance: myapp-prod
    app.kubernetes.io/version: "1.2.3"
    app.kubernetes.io/component: api
    app.kubernetes.io/part-of: myapp
    app.kubernetes.io/managed-by: helm
    environment: production
    team: ml-platform
```

### Rolling Updates

Configure for zero downtime:

```yaml
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0  # No downtime
  minReadySeconds: 10    # Wait before considering ready
```

### Affinity and Anti-Affinity

Spread Pods for high availability:

```yaml
spec:
  affinity:
    podAntiAffinity:
      preferredDuringSchedulingIgnoredDuringExecution:
      - weight: 100
        podAffinityTerm:
          labelSelector:
            matchLabels:
              app: myapp
          topologyKey: kubernetes.io/hostname
```

## Summary and Key Takeaways

### Core Resources

- **Pods**: Smallest deployable unit, usually one container
- **ReplicaSets**: Maintain desired number of Pod replicas
- **Deployments**: Declarative updates, rolling updates, rollbacks
- **Services**: Stable network endpoint, load balancing
- **ConfigMaps**: Configuration data
- **Secrets**: Sensitive data
- **PVCs**: Persistent storage

### Deployment Hierarchy

```
Deployment → ReplicaSet → Pods
Service → Endpoints → Pod IPs
```

### Service Types

- **ClusterIP**: Internal only (default)
- **NodePort**: Expose on node ports (30000-32767)
- **LoadBalancer**: Cloud load balancer
- **ExternalName**: DNS mapping

### Best Practices Checklist

- [ ] Set resource requests and limits
- [ ] Implement liveness and readiness probes
- [ ] Use specific image tags (not `latest`)
- [ ] Run as non-root user
- [ ] Use ConfigMaps for configuration
- [ ] Use Secrets for sensitive data (mounted as volumes)
- [ ] Label resources consistently
- [ ] Use namespaces for isolation
- [ ] Configure rolling update strategy
- [ ] Use Pod anti-affinity for HA
- [ ] Implement monitoring and logging
- [ ] Document your deployments

### Next Steps

Now that you can deploy applications, proceed to:
- **Lecture 03**: Helm for package management
- **Lecture 04**: Operations and debugging
- **Exercise 01**: Deploy your first application
- **Exercise 02**: Create a Helm chart

### Further Reading

- Kubernetes API Reference: https://kubernetes.io/docs/reference/
- Best Practices: https://kubernetes.io/docs/concepts/configuration/overview/
- Production Checklist: https://learnk8s.io/production-best-practices

---

**Congratulations!** You now know how to deploy applications to Kubernetes. Practice these concepts in the hands-on exercises to solidify your understanding.
