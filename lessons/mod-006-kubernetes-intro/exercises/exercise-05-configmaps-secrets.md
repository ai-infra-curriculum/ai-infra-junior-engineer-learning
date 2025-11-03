# Exercise 05: ConfigMaps, Secrets, and Configuration Management

## Exercise Overview

**Objective**: Master configuration management in Kubernetes using ConfigMaps and Secrets, implement environment-specific configurations, and apply best practices for ML application configuration.

**Difficulty**: Intermediate
**Estimated Time**: 3-4 hours
**Prerequisites**:
- Exercise 01-04 (Kubernetes basics, StatefulSets)
- Module 005 (Docker environment variables)

## Learning Objectives

By completing this exercise, you will:
- Create and manage ConfigMaps from literals, files, and YAML manifests
- Implement Secrets for secure credential management
- Inject environment variables into pods using ConfigMaps and Secrets
- Apply configuration injection patterns (volumes vs environment variables)
- Integrate external configuration systems (etcd, HashiCorp Vault)
- Configure ML model parameters and hyperparameters
- Design multi-environment configuration strategies (dev, staging, prod)
- Follow configuration security best practices
- Update running applications with configuration changes
- Debug configuration-related pod failures

---

## Part 1: ConfigMaps Basics

### Step 1.1: Creating ConfigMaps

```bash
# Method 1: From literal values
kubectl create configmap app-config \
  --from-literal=database.host=postgres \
  --from-literal=database.port=5432 \
  --from-literal=log.level=info

# View ConfigMap
kubectl get configmap app-config -o yaml

# Method 2: From file
cat > app.properties << 'EOF'
database.host=postgres
database.port=5432
database.name=myapp
cache.enabled=true
cache.ttl=3600
log.level=info
log.format=json
EOF

kubectl create configmap app-config-file --from-file=app.properties

# Method 3: From YAML
cat > configmap.yaml << 'EOF'
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config-yaml
data:
  database.host: postgres
  database.port: "5432"
  app.json: |
    {
      "name": "MyApp",
      "version": "1.0.0",
      "features": {
        "auth": true,
        "caching": true
      }
    }
EOF

kubectl apply -f configmap.yaml
```

### Step 1.2: Using ConfigMaps as Environment Variables

```yaml
cat > pod-with-configmap.yaml << 'EOF'
apiVersion: v1
kind: Pod
metadata:
  name: app-with-config
spec:
  containers:
  - name: app
    image: busybox
    command: ['sh', '-c', 'env | grep DB_ && sleep 3600']
    env:
    # Single value from ConfigMap
    - name: DB_HOST
      valueFrom:
        configMapKeyRef:
          name: app-config
          key: database.host
    - name: DB_PORT
      valueFrom:
        configMapKeyRef:
          name: app-config
          key: database.port
    # All keys as environment variables
    envFrom:
    - configMapRef:
        name: app-config
        prefix: APP_
EOF

kubectl apply -f pod-with-configmap.yaml

# Check environment variables
kubectl logs app-with-config
```

### Step 1.3: Mounting ConfigMaps as Volumes

```yaml
cat > pod-with-config-volume.yaml << 'EOF'
apiVersion: v1
kind: Pod
metadata:
  name: app-with-config-volume
spec:
  containers:
  - name: app
    image: nginx:alpine
    volumeMounts:
    - name: config
      mountPath: /etc/config
      readOnly: true
  volumes:
  - name: config
    configMap:
      name: app-config-file
      items:
      - key: app.properties
        path: application.properties
EOF

kubectl apply -f pod-with-config-volume.yaml

# Verify mounted config
kubectl exec app-with-config-volume -- cat /etc/config/application.properties
```

✅ **Checkpoint**: You can create and use ConfigMaps.

---

## Part 2: Secrets Management

### Step 2.1: Creating Secrets

```bash
# Method 1: From literal values
kubectl create secret generic db-credentials \
  --from-literal=username=admin \
  --from-literal=password=secretpass123

# View Secret (values are base64 encoded)
kubectl get secret db-credentials -o yaml

# Decode secret value
kubectl get secret db-credentials -o jsonpath='{.data.password}' | base64 -d

# Method 2: From file
echo -n 'admin' > username.txt
echo -n 'secretpass123' > password.txt

kubectl create secret generic db-credentials-file \
  --from-file=username=username.txt \
  --from-file=password=password.txt

# Clean up files
rm username.txt password.txt

# Method 3: From YAML (NOT RECOMMENDED - secrets in plain text)
cat > secret.yaml << 'EOF'
apiVersion: v1
kind: Secret
metadata:
  name: db-credentials-yaml
type: Opaque
stringData:  # Use stringData for plain text (auto base64 encoded)
  username: admin
  password: secretpass123
EOF

kubectl apply -f secret.yaml
```

### Step 2.2: Using Secrets as Environment Variables

```yaml
cat > pod-with-secret.yaml << 'EOF'
apiVersion: v1
kind: Pod
metadata:
  name: app-with-secret
spec:
  containers:
  - name: app
    image: postgres:15
    env:
    - name: POSTGRES_USER
      valueFrom:
        secretKeyRef:
          name: db-credentials
          key: username
    - name: POSTGRES_PASSWORD
      valueFrom:
        secretKeyRef:
          name: db-credentials
          key: password
    # All secret keys as env vars
    envFrom:
    - secretRef:
        name: db-credentials
        prefix: DB_
EOF

kubectl apply -f pod-with-secret.yaml

# Verify (don't print passwords in production!)
kubectl exec app-with-secret -- env | grep DB_
```

### Step 2.3: Mounting Secrets as Volumes

```yaml
cat > pod-with-secret-volume.yaml << 'EOF'
apiVersion: v1
kind: Pod
metadata:
  name: app-with-secret-volume
spec:
  containers:
  - name: app
    image: busybox
    command: ['sh', '-c', 'cat /etc/secrets/username && sleep 3600']
    volumeMounts:
    - name: secrets
      mountPath: /etc/secrets
      readOnly: true
  volumes:
  - name: secrets
    secret:
      secretName: db-credentials
      defaultMode: 0400  # Read-only for owner
EOF

kubectl apply -f pod-with-secret-volume.yaml

# Each key becomes a file
kubectl exec app-with-secret-volume -- ls -la /etc/secrets
kubectl exec app-with-secret-volume -- cat /etc/secrets/username
```

### Step 2.4: TLS Secrets

```bash
# Generate TLS certificate (self-signed for testing)
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout tls.key -out tls.crt \
  -subj "/CN=myapp.example.com"

# Create TLS secret
kubectl create secret tls tls-secret \
  --cert=tls.crt \
  --key=tls.key

# View TLS secret
kubectl get secret tls-secret -o yaml

# Cleanup
rm tls.key tls.crt
```

✅ **Checkpoint**: You can create and use Secrets securely.

---

## Part 3: Configuration Patterns

### Step 3.1: Multi-Environment Configuration

```yaml
# Development ConfigMap
cat > config-dev.yaml << 'EOF'
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
  namespace: development
data:
  APP_ENV: development
  DB_HOST: postgres-dev
  LOG_LEVEL: debug
  CACHE_ENABLED: "false"
  FEATURE_FLAG_NEW_UI: "true"
---
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
  namespace: development
type: Opaque
stringData:
  DB_PASSWORD: dev_password
  API_KEY: dev_api_key_12345
EOF

# Production ConfigMap
cat > config-prod.yaml << 'EOF'
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
  namespace: production
data:
  APP_ENV: production
  DB_HOST: postgres-prod.default.svc.cluster.local
  LOG_LEVEL: info
  CACHE_ENABLED: "true"
  FEATURE_FLAG_NEW_UI: "false"
---
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
  namespace: production
type: Opaque
stringData:
  DB_PASSWORD: "CHANGE_ME_IN_PRODUCTION"
  API_KEY: "prod_api_key_should_be_rotated"
EOF

# Create namespaces
kubectl create namespace development
kubectl create namespace production

# Apply configs
kubectl apply -f config-dev.yaml
kubectl apply -f config-prod.yaml
```

### Step 3.2: Deployment with Environment-Specific Config

```yaml
cat > deployment-multi-env.yaml << 'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
  namespace: development  # Change to 'production' for prod
spec:
  replicas: 2
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
    spec:
      containers:
      - name: app
        image: myapp:latest
        envFrom:
        - configMapRef:
            name: app-config
        - secretRef:
            name: app-secrets
        env:
        - name: POD_NAME
          valueFrom:
            fieldRef:
              fieldPath: metadata.name
        - name: POD_NAMESPACE
          valueFrom:
            fieldRef:
              fieldPath: metadata.namespace
EOF
```

### Step 3.3: Configuration Versioning

```yaml
cat > config-versioned.yaml << 'EOF'
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config-v1
  labels:
    version: v1
data:
  config.json: |
    {
      "version": "1.0.0",
      "settings": {
        "timeout": 30
      }
    }
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config-v2
  labels:
    version: v2
data:
  config.json: |
    {
      "version": "2.0.0",
      "settings": {
        "timeout": 60,
        "retries": 3
      }
    }
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
    spec:
      containers:
      - name: app
        image: myapp:latest
        volumeMounts:
        - name: config
          mountPath: /etc/config
      volumes:
      - name: config
        configMap:
          name: app-config-v2  # Easy to switch versions
EOF
```

✅ **Checkpoint**: You can manage multi-environment configurations.

---

## Part 4: ML Configuration Patterns

### Step 4.1: Model Configuration

```yaml
cat > ml-model-config.yaml << 'EOF'
apiVersion: v1
kind: ConfigMap
metadata:
  name: model-config
data:
  model_config.yaml: |
    model:
      name: resnet50
      version: "1.0.0"
      framework: pytorch
      input_shape: [3, 224, 224]
      batch_size: 32

    inference:
      device: cuda
      precision: fp16
      max_batch_delay_ms: 100

    preprocessing:
      normalize: true
      mean: [0.485, 0.456, 0.406]
      std: [0.229, 0.224, 0.225]

    postprocessing:
      top_k: 5
      threshold: 0.5
---
apiVersion: v1
kind: Secret
metadata:
  name: model-credentials
type: Opaque
stringData:
  s3_access_key: AKIAIOSFODNN7EXAMPLE
  s3_secret_key: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
  model_encryption_key: base64_encoded_encryption_key
EOF

kubectl apply -f ml-model-config.yaml
```

### Step 4.2: ML Training Job with Configuration

```yaml
cat > ml-training-job.yaml << 'EOF'
apiVersion: batch/v1
kind: Job
metadata:
  name: model-training
spec:
  template:
    spec:
      containers:
      - name: trainer
        image: pytorch/pytorch:2.0.1-cuda11.7-cudnn8-runtime
        command:
        - python
        - train.py
        - --config=/config/training_config.yaml
        env:
        # Training hyperparameters from ConfigMap
        - name: LEARNING_RATE
          valueFrom:
            configMapKeyRef:
              name: training-config
              key: learning_rate
        - name: BATCH_SIZE
          valueFrom:
            configMapKeyRef:
              name: training-config
              key: batch_size
        - name: EPOCHS
          valueFrom:
            configMapKeyRef:
              name: training-config
              key: epochs
        # Credentials from Secret
        - name: WANDB_API_KEY
          valueFrom:
            secretKeyRef:
              name: ml-secrets
              key: wandb_api_key
        volumeMounts:
        - name: config
          mountPath: /config
        - name: data
          mountPath: /data
        resources:
          limits:
            nvidia.com/gpu: 1
      volumes:
      - name: config
        configMap:
          name: training-config
      - name: data
        persistentVolumeClaim:
          claimName: training-data
      restartPolicy: Never
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: training-config
data:
  learning_rate: "0.001"
  batch_size: "64"
  epochs: "100"
  training_config.yaml: |
    model:
      architecture: resnet50
      pretrained: true

    optimizer:
      type: adam
      learning_rate: 0.001
      weight_decay: 0.0001

    scheduler:
      type: cosine
      warmup_epochs: 5

    augmentation:
      random_crop: true
      random_flip: true
      color_jitter: 0.2
---
apiVersion: v1
kind: Secret
metadata:
  name: ml-secrets
type: Opaque
stringData:
  wandb_api_key: "your_wandb_api_key"
  mlflow_tracking_uri: "http://mlflow:5000"
EOF
```

### Step 4.3: Feature Store Configuration

```yaml
cat > feature-store-config.yaml << 'EOF'
apiVersion: v1
kind: ConfigMap
metadata:
  name: feast-config
data:
  feature_store.yaml: |
    project: ml_project
    registry: s3://feast-registry/registry.db
    provider: aws
    online_store:
      type: redis
      connection_string: redis:6379
    offline_store:
      type: bigquery
      dataset: feast_offline_store
    entity_key_serialization_version: 2
---
apiVersion: v1
kind: Secret
metadata:
  name: feast-credentials
type: Opaque
stringData:
  aws_access_key_id: AKIAIOSFODNN7EXAMPLE
  aws_secret_access_key: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
  gcp_service_account: |
    {
      "type": "service_account",
      "project_id": "my-project"
    }
EOF
```

✅ **Checkpoint**: You can configure ML workloads properly.

---

## Part 5: Advanced Configuration Techniques

### Step 5.1: Configuration Hot Reload

```yaml
cat > deployment-with-reload.yaml << 'EOF'
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config-reload
data:
  config.json: |
    {
      "refresh_interval": 60,
      "log_level": "info"
    }
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app-with-reload
spec:
  replicas: 2
  selector:
    matchLabels:
      app: reload-demo
  template:
    metadata:
      labels:
        app: reload-demo
      annotations:
        # Force pod restart on ConfigMap change
        checksum/config: "{{ include (print $.Template.BasePath \"/configmap.yaml\") . | sha256sum }}"
    spec:
      containers:
      - name: app
        image: myapp:latest
        volumeMounts:
        - name: config
          mountPath: /etc/config
        # Sidecar for watching config changes
      - name: config-reloader
        image: jimmidyson/configmap-reload:v0.5.0
        args:
        - --volume-dir=/etc/config
        - --webhook-url=http://localhost:8080/reload
        volumeMounts:
        - name: config
          mountPath: /etc/config
      volumes:
      - name: config
        configMap:
          name: app-config-reload
EOF
```

### Step 5.2: Immutable ConfigMaps and Secrets

```yaml
cat > immutable-config.yaml << 'EOF'
apiVersion: v1
kind: ConfigMap
metadata:
  name: immutable-config-v1
immutable: true  # Cannot be modified!
data:
  setting: value1
---
apiVersion: v1
kind: Secret
metadata:
  name: immutable-secret-v1
immutable: true  # Cannot be modified!
type: Opaque
stringData:
  password: secret123
EOF

kubectl apply -f immutable-config.yaml

# Try to modify (will fail)
# kubectl patch configmap immutable-config-v1 -p '{"data":{"setting":"value2"}}'
# Error: field is immutable

# Instead, create new version
cat > immutable-config-v2.yaml << 'EOF'
apiVersion: v1
kind: ConfigMap
metadata:
  name: immutable-config-v2
immutable: true
data:
  setting: value2
EOF
```

### Step 5.3: SubPath Mounting

```yaml
cat > subpath-mount.yaml << 'EOF'
apiVersion: v1
kind: ConfigMap
metadata:
  name: multi-file-config
data:
  nginx.conf: |
    server {
      listen 80;
      location / {
        root /usr/share/nginx/html;
      }
    }
  app.conf: |
    key=value
    log_level=info
---
apiVersion: v1
kind: Pod
metadata:
  name: subpath-demo
spec:
  containers:
  - name: nginx
    image: nginx:alpine
    volumeMounts:
    # Mount single file from ConfigMap
    - name: config
      mountPath: /etc/nginx/conf.d/default.conf
      subPath: nginx.conf  # Only mount this key
    # Mount another file to different location
    - name: config
      mountPath: /etc/app/app.conf
      subPath: app.conf
  volumes:
  - name: config
    configMap:
      name: multi-file-config
EOF

kubectl apply -f subpath-mount.yaml

# Verify individual files are mounted
kubectl exec subpath-demo -- ls -la /etc/nginx/conf.d/
kubectl exec subpath-demo -- ls -la /etc/app/
```

✅ **Checkpoint**: You understand advanced configuration patterns.

---

## Part 6: External Configuration Systems

### Step 6.1: Using External Secrets Operator

```yaml
# Install External Secrets Operator (conceptual)
# kubectl apply -f https://raw.githubusercontent.com/external-secrets/external-secrets/main/deploy/crds/bundle.yaml

# SecretStore pointing to external system
cat > secret-store.yaml << 'EOF'
apiVersion: external-secrets.io/v1beta1
kind: SecretStore
metadata:
  name: vault-backend
spec:
  provider:
    vault:
      server: "http://vault:8200"
      path: "secret"
      version: "v2"
      auth:
        kubernetes:
          mountPath: "kubernetes"
          role: "myapp"
---
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: vault-secret
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: vault-backend
    kind: SecretStore
  target:
    name: vault-generated-secret
    creationPolicy: Owner
  data:
  - secretKey: password
    remoteRef:
      key: secret/data/database
      property: password
EOF
```

### Step 6.2: ConfigMap from Git Repository

```yaml
cat > git-sync-config.yaml << 'EOF'
apiVersion: v1
kind: Pod
metadata:
  name: git-sync-demo
spec:
  containers:
  - name: app
    image: myapp:latest
    volumeMounts:
    - name: config
      mountPath: /etc/config
  - name: git-sync
    image: k8s.gcr.io/git-sync:v3.1.6
    env:
    - name: GIT_SYNC_REPO
      value: https://github.com/myorg/config-repo
    - name: GIT_SYNC_BRANCH
      value: main
    - name: GIT_SYNC_ROOT
      value: /git
    - name: GIT_SYNC_DEST
      value: config
    - name: GIT_SYNC_PERIOD
      value: "60s"
    volumeMounts:
    - name: config
      mountPath: /git
  volumes:
  - name: config
    emptyDir: {}
EOF
```

✅ **Checkpoint**: You can integrate external configuration systems.

---

## Part 7: Best Practices

### Step 7.1: Separation of Concerns

```yaml
cat > best-practice-separation.yaml << 'EOF'
# Application config - can be public
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  log_level: info
  cache_ttl: "3600"
  max_connections: "100"
---
# Infrastructure config - environment-specific
apiVersion: v1
kind: ConfigMap
metadata:
  name: infrastructure-config
data:
  db_host: postgres.default.svc.cluster.local
  redis_host: redis.default.svc.cluster.local
---
# Secrets - always sensitive
apiVersion: v1
kind: Secret
metadata:
  name: credentials
type: Opaque
stringData:
  db_password: secret
  api_key: key123
EOF
```

### Step 7.2: Configuration Validation

```yaml
cat > validated-config.yaml << 'EOF'
apiVersion: v1
kind: ConfigMap
metadata:
  name: validated-config
data:
  validate.sh: |
    #!/bin/bash
    # Validate configuration before starting app

    # Check required vars
    required_vars=("DB_HOST" "DB_PORT" "API_KEY")
    for var in "${required_vars[@]}"; do
      if [ -z "${!var}" ]; then
        echo "ERROR: $var is not set"
        exit 1
      fi
    done

    # Validate format
    if ! [[ "$DB_PORT" =~ ^[0-9]+$ ]]; then
      echo "ERROR: DB_PORT must be numeric"
      exit 1
    fi

    echo "Configuration validated successfully"
---
apiVersion: v1
kind: Pod
metadata:
  name: validated-app
spec:
  initContainers:
  - name: validate-config
    image: busybox
    command: ['sh', '/scripts/validate.sh']
    envFrom:
    - configMapRef:
        name: app-config
    - secretRef:
        name: app-secrets
    volumeMounts:
    - name: scripts
      mountPath: /scripts
  containers:
  - name: app
    image: myapp:latest
    envFrom:
    - configMapRef:
        name: app-config
    - secretRef:
        name: app-secrets
  volumes:
  - name: scripts
    configMap:
      name: validated-config
      defaultMode: 0755
EOF
```

### Step 7.3: Documentation and Labeling

```yaml
cat > documented-config.yaml << 'EOF'
apiVersion: v1
kind: ConfigMap
metadata:
  name: documented-config
  labels:
    app: myapp
    environment: production
    version: "1.0"
    team: platform
  annotations:
    description: "Production configuration for MyApp"
    owner: "platform-team@example.com"
    last-updated: "2025-10-18"
    change-policy: "requires-approval"
data:
  # Database configuration
  db.host: postgres.prod.svc.cluster.local
  db.port: "5432"

  # Caching configuration
  cache.enabled: "true"
  cache.ttl: "3600"

  # Feature flags
  feature.new_ui: "false"
  feature.beta_api: "false"
EOF
```

✅ **Checkpoint**: You follow configuration best practices.

---

## Part 8: Troubleshooting

### Step 8.1: Debugging Configuration Issues

```bash
# List all ConfigMaps
kubectl get configmaps

# Describe ConfigMap
kubectl describe configmap app-config

# Get ConfigMap as YAML
kubectl get configmap app-config -o yaml

# Check which pods use a ConfigMap
kubectl get pods -o json | \
  jq '.items[] | select(.spec.volumes[]?.configMap.name=="app-config") | .metadata.name'

# View environment variables in a pod
kubectl exec <pod-name> -- env

# Check mounted config files
kubectl exec <pod-name> -- ls -la /etc/config
kubectl exec <pod-name> -- cat /etc/config/app.properties

# Watch for ConfigMap changes
kubectl get configmap app-config -w
```

### Step 8.2: Common Issues and Solutions

```yaml
# Issue 1: ConfigMap not found
# Solution: Ensure ConfigMap exists in same namespace
kubectl get configmap -n <namespace>

# Issue 2: Permission denied reading mounted file
# Solution: Check defaultMode
cat > fix-permissions.yaml << 'EOF'
volumes:
- name: config
  configMap:
    name: app-config
    defaultMode: 0644  # Readable by all
EOF

# Issue 3: Environment variables not updated
# Solution: Restart pods (ConfigMap changes don't auto-reload env vars)
kubectl rollout restart deployment myapp

# Issue 4: Secret values not decoded
# Solution: Use stringData instead of data in Secret YAML
cat > secret-fix.yaml << 'EOF'
apiVersion: v1
kind: Secret
metadata:
  name: my-secret
stringData:  # Use this for plain text
  password: mypassword
# Not:
# data:
#   password: bXlwYXNzd29yZA==  # base64 encoded
EOF
```

✅ **Checkpoint**: You can troubleshoot configuration issues.

---

## Summary

**What You Accomplished**:
✅ Created and used ConfigMaps
✅ Managed Secrets securely
✅ Implemented multi-environment configurations
✅ Configured ML training and inference
✅ Applied advanced configuration patterns
✅ Integrated external config systems
✅ Followed best practices
✅ Debugged configuration issues

**Key Concepts**:
- ConfigMaps for non-sensitive configuration
- Secrets for sensitive data
- Multiple ways to inject config (env vars, volumes)
- Environment-specific configurations
- Configuration versioning
- Hot reload patterns
- External secret management

**Best Practices**:
- Never commit secrets to Git
- Use immutable ConfigMaps for stability
- Separate app config from infrastructure config
- Validate configuration before use
- Document and label configurations
- Use external secret stores in production
- Version your configurations

---

**Exercise Version**: 1.0
**Last Updated**: October 2025
**Estimated Time**: 3-4 hours
**Difficulty**: Intermediate
