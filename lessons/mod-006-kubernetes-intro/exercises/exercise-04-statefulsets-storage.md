# Exercise 04: StatefulSets and Persistent Storage in Kubernetes

## Exercise Overview

**Objective**: Master StatefulSets for running stateful applications like databases, understand persistent storage in Kubernetes, and implement data persistence patterns for ML workloads.

**Difficulty**: Intermediate
**Estimated Time**: 3-4 hours
**Prerequisites**:
- Exercise 01-03 (Kubernetes basics)
- Module 005 (Docker volumes)
- Lecture 02 (Deploying Apps)

## Learning Objectives

By completing this exercise, you will:
- Compare StatefulSets and Deployments for stateful application management
- Configure PersistentVolumes (PV) and PersistentVolumeClaims (PVC)
- Implement Storage Classes for dynamic volume provisioning
- Set up Headless Services for stable network identities
- Deploy stateful applications like databases on Kubernetes
- Execute volume snapshots and backup procedures
- Design ML model storage patterns with persistent volumes
- Apply data persistence best practices for production workloads
- Manage pod ordering and scaling guarantees with StatefulSets
- Troubleshoot common persistent storage issues

---

## Part 1: Understanding StatefulSets

### Step 1.1: StatefulSet Basics

```yaml
# Create a simple StatefulSet
cat > statefulset-basic.yaml << 'EOF'
apiVersion: v1
kind: Service
metadata:
  name: nginx-headless
spec:
  clusterIP: None  # Headless service
  selector:
    app: nginx-stateful
  ports:
  - port: 80
    name: web
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: web
spec:
  serviceName: "nginx-headless"
  replicas: 3
  selector:
    matchLabels:
      app: nginx-stateful
  template:
    metadata:
      labels:
        app: nginx-stateful
    spec:
      containers:
      - name: nginx
        image: nginx:alpine
        ports:
        - containerPort: 80
          name: web
        volumeMounts:
        - name: www
          mountPath: /usr/share/nginx/html
  volumeClaimTemplates:
  - metadata:
      name: www
    spec:
      accessModes: [ "ReadWriteOnce" ]
      resources:
        requests:
          storage: 1Gi
EOF

# Apply StatefulSet
kubectl apply -f statefulset-basic.yaml

# Watch pods being created
kubectl get pods -l app=nginx-stateful -w

# Notice:
# - Pods created in order: web-0, web-1, web-2
# - Each has stable identity
# - Each has own persistent volume
```

### Step 1.2: StatefulSet vs Deployment

```bash
# Create comparison table
cat > comparison.md << 'EOF'
| Feature | Deployment | StatefulSet |
|---------|------------|-------------|
| Pod names | Random (web-abc123) | Ordered (web-0, web-1) |
| Network identity | Random | Stable (web-0.service) |
| Storage | Shared or ephemeral | Dedicated per pod |
| Startup order | Parallel | Sequential |
| Update strategy | Rolling (random) | Ordered |
| Use case | Stateless apps | Databases, ML training |
EOF

# Test stable network identity
kubectl run -it --rm debug --image=alpine --restart=Never -- sh

# Inside debug pod:
# ping web-0.nginx-headless
# ping web-1.nginx-headless
# ping web-2.nginx-headless
# Each pod has stable DNS name!
```

### Step 1.3: Scaling StatefulSets

```bash
# Scale up
kubectl scale statefulset web --replicas=5

# Watch ordered creation
kubectl get pods -l app=nginx-stateful -w
# web-3 created after web-2 is ready
# web-4 created after web-3 is ready

# Scale down
kubectl scale statefulset web --replicas=2

# Watch ordered deletion
kubectl get pods -l app=nginx-stateful -w
# web-4 deleted first
# web-3 deleted second
# web-2 deleted third

# Verify PVCs remain
kubectl get pvc
# All 5 PVCs still exist!
```

✅ **Checkpoint**: You understand StatefulSet behavior and ordering.

---

## Part 2: Persistent Volumes

### Step 2.1: Manual PV and PVC Creation

```yaml
# Create PersistentVolume
cat > pv.yaml << 'EOF'
apiVersion: v1
kind: PersistentVolume
metadata:
  name: manual-pv
spec:
  capacity:
    storage: 5Gi
  accessModes:
    - ReadWriteOnce
  persistentVolumeReclaimPolicy: Retain
  hostPath:
    path: /mnt/data  # Local path (for minikube/kind)
EOF

kubectl apply -f pv.yaml

# Create PersistentVolumeClaim
cat > pvc.yaml << 'EOF'
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: manual-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 2Gi
EOF

kubectl apply -f pvc.yaml

# Check binding
kubectl get pv,pvc
# PVC should be Bound to PV
```

### Step 2.2: Using PVC in Pod

```yaml
cat > pod-with-pvc.yaml << 'EOF'
apiVersion: v1
kind: Pod
metadata:
  name: pod-with-storage
spec:
  containers:
  - name: app
    image: busybox
    command: ['sh', '-c', 'echo "Data persists!" > /data/test.txt && sleep 3600']
    volumeMounts:
    - mountPath: /data
      name: storage
  volumes:
  - name: storage
    persistentVolumeClaim:
      claimName: manual-pvc
EOF

kubectl apply -f pod-with-storage.yaml

# Verify data
kubectl exec pod-with-storage -- cat /data/test.txt

# Delete and recreate pod
kubectl delete pod pod-with-storage
kubectl apply -f pod-with-storage.yaml

# Data still exists!
kubectl exec pod-with-storage -- cat /data/test.txt
```

### Step 2.3: Access Modes

```yaml
cat > access-modes-demo.yaml << 'EOF'
# ReadWriteOnce (RWO) - Single node read-write
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: rwo-claim
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
---
# ReadOnlyMany (ROX) - Multi-node read-only
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: rox-claim
spec:
  accessModes:
    - ReadOnlyMany
  resources:
    requests:
      storage: 1Gi
---
# ReadWriteMany (RWX) - Multi-node read-write
# (Requires network storage like NFS)
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: rwx-claim
spec:
  accessModes:
    - ReadWriteMany
  resources:
    requests:
      storage: 1Gi
EOF
```

✅ **Checkpoint**: You can create and use PersistentVolumes.

---

## Part 3: Storage Classes

### Step 3.1: Dynamic Provisioning

```yaml
# View available storage classes
kubectl get storageclass

# Create custom StorageClass
cat > storageclass.yaml << 'EOF'
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast-ssd
provisioner: kubernetes.io/no-provisioner  # Use appropriate provisioner
parameters:
  type: pd-ssd  # Cloud provider specific
volumeBindingMode: WaitForFirstConsumer
reclaimPolicy: Delete
EOF

kubectl apply -f storageclass.yaml
```

### Step 3.2: Using StorageClass

```yaml
cat > pvc-with-storageclass.yaml << 'EOF'
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: dynamic-pvc
spec:
  storageClassName: fast-ssd
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
EOF

kubectl apply -f pvc-with-storageclass.yaml

# PV automatically created!
kubectl get pv,pvc
```

### Step 3.3: Default StorageClass

```bash
# View default storage class
kubectl get storageclass
# Look for (default) annotation

# Set default storage class
kubectl patch storageclass fast-ssd \
  -p '{"metadata": {"annotations":{"storageclass.kubernetes.io/is-default-class":"true"}}}'

# PVCs without storageClassName use default
cat > pvc-default.yaml << 'EOF'
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: uses-default
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 5Gi
  # No storageClassName - uses default!
EOF
```

✅ **Checkpoint**: You understand dynamic provisioning with StorageClasses.

---

## Part 4: Running PostgreSQL StatefulSet

### Step 4.1: PostgreSQL with Persistent Storage

```yaml
cat > postgres-statefulset.yaml << 'EOF'
apiVersion: v1
kind: ConfigMap
metadata:
  name: postgres-config
data:
  POSTGRES_DB: mydb
  POSTGRES_USER: myuser
---
apiVersion: v1
kind: Secret
metadata:
  name: postgres-secret
type: Opaque
stringData:
  POSTGRES_PASSWORD: secretpassword
---
apiVersion: v1
kind: Service
metadata:
  name: postgres-headless
spec:
  clusterIP: None
  selector:
    app: postgres
  ports:
  - port: 5432
    name: postgres
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
spec:
  serviceName: postgres-headless
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
        image: postgres:15
        ports:
        - containerPort: 5432
          name: postgres
        envFrom:
        - configMapRef:
            name: postgres-config
        - secretRef:
            name: postgres-secret
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/postgresql/data
          subPath: postgres  # Important for PostgreSQL
  volumeClaimTemplates:
  - metadata:
      name: postgres-storage
    spec:
      accessModes: [ "ReadWriteOnce" ]
      resources:
        requests:
          storage: 5Gi
EOF

kubectl apply -f postgres-statefulset.yaml
```

### Step 4.2: Testing Database Persistence

```bash
# Wait for PostgreSQL to be ready
kubectl wait --for=condition=ready pod/postgres-0 --timeout=120s

# Create test data
kubectl exec -it postgres-0 -- psql -U myuser -d mydb << 'EOSQL'
CREATE TABLE test_data (
    id SERIAL PRIMARY KEY,
    value TEXT
);

INSERT INTO test_data (value) VALUES
    ('Kubernetes'),
    ('Persistent'),
    ('Storage');

SELECT * FROM test_data;
EOSQL

# Delete the pod
kubectl delete pod postgres-0

# Wait for recreation
kubectl wait --for=condition=ready pod/postgres-0 --timeout=120s

# Verify data persists
kubectl exec -it postgres-0 -- psql -U myuser -d mydb -c "SELECT * FROM test_data;"
# Data still there!
```

### Step 4.3: Accessing PostgreSQL from Another Pod

```yaml
cat > postgres-client.yaml << 'EOF'
apiVersion: v1
kind: Pod
metadata:
  name: postgres-client
spec:
  containers:
  - name: client
    image: postgres:15
    command: ['sleep', '3600']
    env:
    - name: PGHOST
      value: postgres-0.postgres-headless
    - name: PGUSER
      value: myuser
    - name: PGPASSWORD
      valueFrom:
        secretKeyRef:
          name: postgres-secret
          key: POSTGRES_PASSWORD
    - name: PGDATABASE
      value: mydb
EOF

kubectl apply -f postgres-client.yaml

# Connect to database
kubectl exec -it postgres-client -- psql -c "SELECT * FROM test_data;"
```

✅ **Checkpoint**: You can run stateful databases on Kubernetes.

---

## Part 5: ML Model Storage Patterns

### Step 5.1: Shared Model Storage

```yaml
cat > ml-model-storage.yaml << 'EOF'
# Shared PVC for models (requires RWX storage)
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: ml-models
spec:
  accessModes:
    - ReadWriteMany  # Multiple pods can access
  resources:
    requests:
      storage: 50Gi
  storageClassName: nfs-storage  # Network storage
---
# Model training job
apiVersion: batch/v1
kind: Job
metadata:
  name: train-model
spec:
  template:
    spec:
      containers:
      - name: trainer
        image: pytorch/pytorch:2.0.1-cuda11.7-cudnn8-runtime
        command: ['python', 'train.py']
        volumeMounts:
        - name: models
          mountPath: /models
        - name: training-code
          mountPath: /workspace
      volumes:
      - name: models
        persistentVolumeClaim:
          claimName: ml-models
      - name: training-code
        configMap:
          name: training-scripts
      restartPolicy: Never
---
# Model serving deployment
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
      - name: server
        image: pytorch/pytorch:2.0.1-cuda11.7-cudnn8-runtime
        command: ['python', 'serve.py']
        volumeMounts:
        - name: models
          mountPath: /models
          readOnly: true  # Read-only for serving
      volumes:
      - name: models
        persistentVolumeClaim:
          claimName: ml-models
EOF
```

### Step 5.2: Per-Experiment Storage (StatefulSet)

```yaml
cat > ml-experiment-storage.yaml << 'EOF'
apiVersion: v1
kind: Service
metadata:
  name: ml-experiment
spec:
  clusterIP: None
  selector:
    app: ml-training
  ports:
  - port: 6006
    name: tensorboard
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: ml-training
spec:
  serviceName: ml-experiment
  replicas: 3  # 3 parallel experiments
  selector:
    matchLabels:
      app: ml-training
  template:
    metadata:
      labels:
        app: ml-training
    spec:
      containers:
      - name: trainer
        image: pytorch/pytorch:2.0.1-cuda11.7-cudnn8-runtime
        command:
        - python
        - train.py
        - --experiment-id=$(POD_NAME)
        env:
        - name: POD_NAME
          valueFrom:
            fieldRef:
              fieldPath: metadata.name
        volumeMounts:
        - name: experiment-data
          mountPath: /experiments
      - name: tensorboard
        image: tensorflow/tensorflow:latest
        command: ['tensorboard', '--logdir=/experiments', '--host=0.0.0.0']
        ports:
        - containerPort: 6006
          name: tensorboard
        volumeMounts:
        - name: experiment-data
          mountPath: /experiments
  volumeClaimTemplates:
  - metadata:
      name: experiment-data
    spec:
      accessModes: [ "ReadWriteOnce" ]
      resources:
        requests:
          storage: 20Gi
EOF
```

### Step 5.3: Model Registry Storage

```yaml
cat > model-registry.yaml << 'EOF'
# MinIO for S3-compatible object storage
apiVersion: v1
kind: Service
metadata:
  name: minio
spec:
  clusterIP: None
  selector:
    app: minio
  ports:
  - port: 9000
    name: api
  - port: 9001
    name: console
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: minio
spec:
  serviceName: minio
  replicas: 1
  selector:
    matchLabels:
      app: minio
  template:
    metadata:
      labels:
        app: minio
    spec:
      containers:
      - name: minio
        image: minio/minio
        args:
        - server
        - /data
        - --console-address
        - ":9001"
        env:
        - name: MINIO_ROOT_USER
          value: minioadmin
        - name: MINIO_ROOT_PASSWORD
          value: minioadmin
        ports:
        - containerPort: 9000
          name: api
        - containerPort: 9001
          name: console
        volumeMounts:
        - name: minio-storage
          mountPath: /data
  volumeClaimTemplates:
  - metadata:
      name: minio-storage
    spec:
      accessModes: [ "ReadWriteOnce" ]
      resources:
        requests:
          storage: 100Gi
EOF

kubectl apply -f model-registry.yaml

# Access MinIO console
kubectl port-forward svc/minio 9001:9001
# Open http://localhost:9001
```

✅ **Checkpoint**: You can implement ML storage patterns.

---

## Part 6: Volume Snapshots and Backups

### Step 6.1: VolumeSnapshot

```yaml
# Create VolumeSnapshotClass
cat > volumesnapshotclass.yaml << 'EOF'
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshotClass
metadata:
  name: csi-hostpath-snapclass
driver: hostpath.csi.k8s.io
deletionPolicy: Delete
EOF

kubectl apply -f volumesnapshotclass.yaml

# Create snapshot of PostgreSQL data
cat > postgres-snapshot.yaml << 'EOF'
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshot
metadata:
  name: postgres-snapshot-1
spec:
  volumeSnapshotClassName: csi-hostpath-snapclass
  source:
    persistentVolumeClaimName: postgres-storage-postgres-0
EOF

kubectl apply -f postgres-snapshot.yaml

# Check snapshot status
kubectl get volumesnapshot
```

### Step 6.2: Restore from Snapshot

```yaml
cat > restore-from-snapshot.yaml << 'EOF'
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgres-restored
spec:
  dataSource:
    name: postgres-snapshot-1
    kind: VolumeSnapshot
    apiGroup: snapshot.storage.k8s.io
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 5Gi
EOF

kubectl apply -f restore-from-snapshot.yaml

# Use restored PVC in a pod
cat > postgres-restored-pod.yaml << 'EOF'
apiVersion: v1
kind: Pod
metadata:
  name: postgres-restored
spec:
  containers:
  - name: postgres
    image: postgres:15
    env:
    - name: POSTGRES_PASSWORD
      value: secretpassword
    volumeMounts:
    - name: data
      mountPath: /var/lib/postgresql/data
      subPath: postgres
  volumes:
  - name: data
    persistentVolumeClaim:
      claimName: postgres-restored
EOF

kubectl apply -f postgres-restored-pod.yaml

# Verify data was restored
kubectl exec postgres-restored -- psql -U postgres -c "\l"
```

### Step 6.3: Backup Strategy Script

```bash
cat > backup-volumes.sh << 'EOF'
#!/bin/bash

NAMESPACE=${1:-default}
SNAPSHOT_CLASS="csi-hostpath-snapclass"

# Get all PVCs in namespace
pvcs=$(kubectl get pvc -n $NAMESPACE -o jsonpath='{.items[*].metadata.name}')

for pvc in $pvcs; do
    timestamp=$(date +%Y%m%d-%H%M%S)
    snapshot_name="${pvc}-snapshot-${timestamp}"

    echo "Creating snapshot: $snapshot_name"

    cat <<YAML | kubectl apply -f -
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshot
metadata:
  name: $snapshot_name
  namespace: $NAMESPACE
spec:
  volumeSnapshotClassName: $SNAPSHOT_CLASS
  source:
    persistentVolumeClaimName: $pvc
YAML

done

echo "Backup complete!"
EOF

chmod +x backup-volumes.sh

# Run backup
./backup-volumes.sh default
```

✅ **Checkpoint**: You can backup and restore volumes.

---

## Part 7: Best Practices

### Step 7.1: Resource Management

```yaml
cat > statefulset-with-resources.yaml << 'EOF'
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: database
spec:
  serviceName: database
  replicas: 3
  selector:
    matchLabels:
      app: database
  template:
    metadata:
      labels:
        app: database
    spec:
      containers:
      - name: db
        image: postgres:15
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
            storage: "10Gi"  # For volumeClaimTemplates
          limits:
            memory: "2Gi"
            cpu: "1000m"
        volumeMounts:
        - name: data
          mountPath: /var/lib/postgresql/data
  volumeClaimTemplates:
  - metadata:
      name: data
    spec:
      accessModes: [ "ReadWriteOnce" ]
      resources:
        requests:
          storage: 10Gi
      storageClassName: fast-ssd
EOF
```

### Step 7.2: Init Containers for Setup

```yaml
cat > statefulset-with-init.yaml << 'EOF'
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: app-with-init
spec:
  serviceName: app
  replicas: 2
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
    spec:
      initContainers:
      - name: init-permissions
        image: busybox
        command: ['sh', '-c', 'chown -R 1000:1000 /data']
        volumeMounts:
        - name: data
          mountPath: /data
      - name: init-data
        image: busybox
        command: ['sh', '-c', 'echo "Initialized" > /data/init.txt']
        volumeMounts:
        - name: data
          mountPath: /data
      containers:
      - name: app
        image: myapp:latest
        volumeMounts:
        - name: data
          mountPath: /data
  volumeClaimTemplates:
  - metadata:
      name: data
    spec:
      accessModes: [ "ReadWriteOnce" ]
      resources:
        requests:
          storage: 5Gi
EOF
```

### Step 7.3: Pod Disruption Budgets

```yaml
cat > pdb.yaml << 'EOF'
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: postgres-pdb
spec:
  minAvailable: 2  # At least 2 pods must be available
  selector:
    matchLabels:
      app: postgres
---
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: ml-training-pdb
spec:
  maxUnavailable: 1  # Max 1 pod can be down
  selector:
    matchLabels:
      app: ml-training
EOF

kubectl apply -f pdb.yaml

# Test disruption protection
# kubectl drain <node-name>
# Will respect PDB limits
```

✅ **Checkpoint**: You understand StatefulSet best practices.

---

## Summary

**What You Accomplished**:
✅ Understood StatefulSets vs Deployments
✅ Created and managed PersistentVolumes
✅ Used StorageClasses for dynamic provisioning
✅ Deployed stateful PostgreSQL database
✅ Implemented ML storage patterns
✅ Created volume snapshots and backups
✅ Applied best practices for stateful apps

**Key Concepts**:
- StatefulSets provide stable identity
- PVs and PVCs manage persistent storage
- StorageClasses enable dynamic provisioning
- Headless services for StatefulSet networking
- Volume snapshots for backups
- Different access modes for different use cases

**Production Patterns**:
- Database persistence
- Shared model storage (RWX)
- Per-experiment storage (StatefulSet)
- Model registry (MinIO)
- Automated backups
- Resource limits and PDBs

---

**Exercise Version**: 1.0
**Last Updated**: October 2025
**Estimated Time**: 3-4 hours
**Difficulty**: Intermediate
