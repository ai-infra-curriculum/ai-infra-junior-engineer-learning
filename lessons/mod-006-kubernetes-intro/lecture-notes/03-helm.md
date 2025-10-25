# Lecture 03: Helm - Kubernetes Package Manager

## Table of Contents
1. [Introduction](#introduction)
2. [Why Helm?](#why-helm)
3. [Helm Architecture](#helm-architecture)
4. [Installing Helm](#installing-helm)
5. [Using Helm Charts](#using-helm-charts)
6. [Creating Helm Charts](#creating-helm-charts)
7. [Helm Templates](#helm-templates)
8. [Values and Customization](#values-and-customization)
9. [Chart Dependencies](#chart-dependencies)
10. [Helm Best Practices](#helm-best-practices)
11. [Helm for ML Applications](#helm-for-ml-applications)
12. [Summary and Key Takeaways](#summary-and-key-takeaways)

## Introduction

Managing Kubernetes manifests can become complex quickly. As applications grow, you'll find yourself managing dozens or hundreds of YAML files with repetitive configuration. **Helm** solves this problem by providing package management for Kubernetes.

Think of Helm as the "apt", "yum", or "npm" for Kubernetes - it lets you define, install, and upgrade even the most complex Kubernetes applications with a single command.

### Learning Objectives

By the end of this lecture, you will:
- Understand what Helm is and why it's essential
- Install and configure Helm
- Use public Helm charts from repositories
- Create custom Helm charts for your applications
- Use templates and values for configuration
- Manage chart dependencies
- Apply Helm best practices
- Deploy ML applications with Helm

### Prerequisites
- Lecture 02: Deploying Applications on Kubernetes
- kubectl configured and working
- Access to a Kubernetes cluster
- Basic understanding of Go templates (helpful but not required)

## Why Helm?

### The Problem Without Helm

Imagine deploying a web application with:
- Frontend Deployment
- Backend Deployment
- Database StatefulSet
- 3 Services
- 2 ConfigMaps
- 3 Secrets
- Ingress
- ServiceAccounts
- RBAC rules

**Without Helm**:
```bash
# Deploy to development
kubectl apply -f frontend-deployment-dev.yaml
kubectl apply -f backend-deployment-dev.yaml
kubectl apply -f database-statefulset-dev.yaml
kubectl apply -f frontend-service.yaml
kubectl apply -f backend-service.yaml
kubectl apply -f database-service.yaml
kubectl apply -f configmap-dev.yaml
kubectl apply -f secrets-dev.yaml
kubectl apply -f ingress-dev.yaml
# ... and so on

# Deploy to production (different files!)
kubectl apply -f frontend-deployment-prod.yaml
kubectl apply -f backend-deployment-prod.yaml
# ... repeat for all resources with production config
```

**Challenges**:
1. Duplicate YAML files for each environment
2. Manual management of configuration differences
3. No versioning of deployments
4. Difficult to rollback
5. No dependency management
6. Hard to share and reuse configurations

### The Solution With Helm

**With Helm**:
```bash
# Deploy to development
helm install myapp ./mychart -f values-dev.yaml

# Deploy to production
helm install myapp ./mychart -f values-prod.yaml

# Upgrade
helm upgrade myapp ./mychart

# Rollback
helm rollback myapp

# Uninstall
helm uninstall myapp
```

**Benefits**:
1. **Templating**: Single template, multiple environments
2. **Packaging**: Bundle related resources together
3. **Versioning**: Track deployment history
4. **Rollback**: Easy rollback to previous versions
5. **Dependencies**: Manage chart dependencies
6. **Sharing**: Public and private chart repositories
7. **Hooks**: Run jobs before/after install/upgrade

## Helm Architecture

### Helm Components

```
┌─────────────────────────────────────────┐
│          Helm Client (CLI)              │
│   Commands: install, upgrade, rollback  │
└────────────────┬────────────────────────┘
                 │
                 │ Uses kubectl config
                 │
                 ▼
┌─────────────────────────────────────────┐
│      Kubernetes API Server              │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│         Kubernetes Resources            │
│  (Deployments, Services, ConfigMaps)    │
└─────────────────────────────────────────┘
```

**Key Point**: Helm 3 is client-only (no Tiller server like Helm 2). It uses your kubectl configuration to connect directly to Kubernetes.

### Key Concepts

**1. Chart**: A Helm package containing all resource definitions
```
mychart/
├── Chart.yaml          # Chart metadata
├── values.yaml         # Default values
├── templates/          # Kubernetes manifests (templated)
│   ├── deployment.yaml
│   ├── service.yaml
│   └── ingress.yaml
└── charts/             # Dependent charts
```

**2. Release**: An instance of a chart deployed to Kubernetes
```bash
# Creates a release named "my-nginx"
helm install my-nginx bitnami/nginx
```

**3. Repository**: A collection of charts
```bash
# Add repository
helm repo add bitnami https://charts.bitnami.com/bitnami

# Search repository
helm search repo nginx
```

**4. Values**: Configuration parameters for a chart
```yaml
# values.yaml
replicaCount: 3
image:
  repository: nginx
  tag: "1.21"
```

## Installing Helm

### Installation Methods

**macOS**:
```bash
brew install helm
```

**Linux**:
```bash
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
```

**Windows (Chocolatey)**:
```bash
choco install kubernetes-helm
```

**From Binary**:
```bash
# Download from https://github.com/helm/helm/releases
wget https://get.helm.sh/helm-v3.12.0-linux-amd64.tar.gz
tar -zxvf helm-v3.12.0-linux-amd64.tar.gz
sudo mv linux-amd64/helm /usr/local/bin/helm
```

### Verify Installation

```bash
# Check version
helm version

# Should output:
# version.BuildInfo{Version:"v3.12.0", ...}

# Get help
helm help

# List available commands
helm --help
```

### Configure Helm

```bash
# Add stable repository
helm repo add stable https://charts.helm.sh/stable

# Add Bitnami repository (widely used)
helm repo add bitnami https://charts.bitnami.com/bitnami

# Update repositories
helm repo update

# List repositories
helm repo list

# Search for charts
helm search repo nginx
helm search repo postgres
```

## Using Helm Charts

### Finding Charts

**Search Hub** (https://artifacthub.io):
```bash
# Search in Artifact Hub
helm search hub prometheus

# Search in added repositories
helm search repo prometheus
```

**Popular Chart Repositories**:
- **Bitnami**: https://charts.bitnami.com/bitnami
- **Prometheus Community**: https://prometheus-community.github.io/helm-charts
- **Grafana**: https://grafana.github.io/helm-charts
- **Elastic**: https://helm.elastic.co
- **NGINX**: https://kubernetes.github.io/ingress-nginx

### Installing a Chart

```bash
# Install with default values
helm install my-nginx bitnami/nginx

# Install with custom name
helm install my-web-server bitnami/nginx

# Install in specific namespace
helm install my-nginx bitnami/nginx --namespace production --create-namespace

# Install with custom values
helm install my-nginx bitnami/nginx --set replicaCount=3

# Install with values file
helm install my-nginx bitnami/nginx -f my-values.yaml

# Dry run (see what would be installed)
helm install my-nginx bitnami/nginx --dry-run --debug

# Install specific version
helm install my-nginx bitnami/nginx --version 13.2.0
```

### Viewing Release Information

```bash
# List releases
helm list
helm list --all-namespaces

# Get release details
helm status my-nginx

# Get release values
helm get values my-nginx

# Get all values (including defaults)
helm get values my-nginx --all

# Get manifest
helm get manifest my-nginx

# Get release history
helm history my-nginx
```

### Upgrading Releases

```bash
# Upgrade with new values
helm upgrade my-nginx bitnami/nginx --set replicaCount=5

# Upgrade with values file
helm upgrade my-nginx bitnami/nginx -f new-values.yaml

# Upgrade to specific version
helm upgrade my-nginx bitnami/nginx --version 13.2.1

# Force recreation of resources
helm upgrade my-nginx bitnami/nginx --force

# Wait for upgrade to complete
helm upgrade my-nginx bitnami/nginx --wait --timeout 5m
```

### Rolling Back

```bash
# Rollback to previous version
helm rollback my-nginx

# Rollback to specific revision
helm rollback my-nginx 2

# List history to see revisions
helm history my-nginx
```

### Uninstalling Releases

```bash
# Uninstall release
helm uninstall my-nginx

# Uninstall but keep history
helm uninstall my-nginx --keep-history

# Can be rolled back if history kept
helm rollback my-nginx
```

### Example: Installing PostgreSQL

```bash
# Add Bitnami repo
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

# View chart values
helm show values bitnami/postgresql > postgres-values.yaml

# Create custom values
cat > my-postgres-values.yaml <<EOF
auth:
  postgresPassword: "supersecret"
  database: "myapp"
primary:
  persistence:
    size: 20Gi
  resources:
    requests:
      memory: "256Mi"
      cpu: "250m"
    limits:
      memory: "512Mi"
      cpu: "500m"
metrics:
  enabled: true
EOF

# Install PostgreSQL
helm install postgres bitnami/postgresql -f my-postgres-values.yaml

# Check status
helm status postgres
kubectl get pods

# Get connection info
export POSTGRES_PASSWORD=$(kubectl get secret postgres-postgresql -o jsonpath="{.data.postgres-password}" | base64 -d)
kubectl run postgres-client --rm -it --image=postgres:14 -- psql -h postgres-postgresql -U postgres
```

## Creating Helm Charts

### Chart Structure

```bash
# Create new chart
helm create mychart

# Directory structure
mychart/
├── .helmignore         # Files to ignore (like .gitignore)
├── Chart.yaml          # Chart metadata
├── values.yaml         # Default configuration values
├── charts/             # Chart dependencies
└── templates/          # Kubernetes manifests
    ├── NOTES.txt       # Help text displayed after install
    ├── _helpers.tpl    # Template helpers
    ├── deployment.yaml
    ├── service.yaml
    ├── ingress.yaml
    ├── serviceaccount.yaml
    ├── hpa.yaml
    └── tests/
        └── test-connection.yaml
```

### Chart.yaml

The Chart.yaml file defines chart metadata:

```yaml
apiVersion: v2
name: mychart
description: A Helm chart for my application
type: application
version: 0.1.0        # Chart version (SemVer)
appVersion: "1.0.0"   # Application version

# Optional fields
keywords:
  - web
  - api
  - python
home: https://example.com
sources:
  - https://github.com/example/mychart
maintainers:
  - name: John Doe
    email: john@example.com
    url: https://example.com
icon: https://example.com/icon.png
dependencies:
  - name: postgresql
    version: "11.x.x"
    repository: https://charts.bitnami.com/bitnami
    condition: postgresql.enabled
```

**Field Explanations**:
- **apiVersion**: Chart API version (v2 for Helm 3)
- **name**: Chart name
- **version**: Chart version (incremented on chart changes)
- **appVersion**: Version of the application being deployed
- **type**: `application` or `library`

### values.yaml

Default configuration values:

```yaml
# values.yaml
replicaCount: 2

image:
  repository: myapp
  pullPolicy: IfNotPresent
  tag: "1.0.0"

imagePullSecrets: []
nameOverride: ""
fullnameOverride: ""

serviceAccount:
  create: true
  annotations: {}
  name: ""

podAnnotations: {}

podSecurityContext:
  fsGroup: 2000

securityContext:
  capabilities:
    drop:
    - ALL
  readOnlyRootFilesystem: true
  runAsNonRoot: true
  runAsUser: 1000

service:
  type: ClusterIP
  port: 80

ingress:
  enabled: false
  className: ""
  annotations: {}
  hosts:
    - host: chart-example.local
      paths:
        - path: /
          pathType: ImplementationSpecific
  tls: []

resources:
  limits:
    cpu: 100m
    memory: 128Mi
  requests:
    cpu: 100m
    memory: 128Mi

autoscaling:
  enabled: false
  minReplicas: 1
  maxReplicas: 100
  targetCPUUtilizationPercentage: 80

nodeSelector: {}

tolerations: []

affinity: {}
```

## Helm Templates

Templates are Kubernetes manifests with Go template syntax.

### Basic Templating

**Template Syntax**:
```yaml
# templates/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ .Release.Name }}-deployment
  labels:
    app: {{ .Chart.Name }}
    version: {{ .Chart.AppVersion }}
spec:
  replicas: {{ .Values.replicaCount }}
  selector:
    matchLabels:
      app: {{ .Chart.Name }}
  template:
    metadata:
      labels:
        app: {{ .Chart.Name }}
    spec:
      containers:
      - name: {{ .Chart.Name }}
        image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
        ports:
        - containerPort: 8080
        resources:
          {{- toYaml .Values.resources | nindent 10 }}
```

**Built-in Objects**:
- **`.Release.Name`**: Release name
- **`.Release.Namespace`**: Namespace
- **`.Release.IsUpgrade`**: True if upgrade
- **`.Release.IsInstall`**: True if install
- **`.Chart.Name`**: Chart name from Chart.yaml
- **`.Chart.Version`**: Chart version
- **`.Chart.AppVersion`**: App version
- **`.Values`**: Values from values.yaml and overrides
- **`.Files`**: Access files in chart
- **`.Capabilities`**: Info about Kubernetes cluster

### Template Functions

**String Functions**:
```yaml
# Quote
value: {{ .Values.name | quote }}

# Upper/Lower case
name: {{ .Values.name | upper }}
name: {{ .Values.name | lower }}

# Default value
replicas: {{ .Values.replicaCount | default 3 }}

# Trim whitespace
name: {{ .Values.name | trim }}
```

**Logic Functions**:
```yaml
# If/else
{{- if .Values.ingress.enabled }}
apiVersion: networking.k8s.io/v1
kind: Ingress
# ...
{{- end }}

{{- if .Values.postgresql.enabled }}
# PostgreSQL configuration
{{- else }}
# External database configuration
{{- end }}

# With (set scope)
{{- with .Values.nodeSelector }}
nodeSelector:
  {{- toYaml . | nindent 2 }}
{{- end }}

# Range (loop)
{{- range .Values.environments }}
- name: {{ .name }}
  value: {{ .value }}
{{- end }}
```

**YAML Functions**:
```yaml
# toYaml: Convert to YAML
resources:
  {{- toYaml .Values.resources | nindent 2 }}

# toJson: Convert to JSON
config: {{ .Values.config | toJson }}

# indent/nindent: Indent lines
labels:
  {{- toYaml .Values.labels | nindent 4 }}
```

### Template Helpers (_helpers.tpl)

Reusable template snippets:

```yaml
# templates/_helpers.tpl

{{/*
Expand the name of the chart.
*/}}
{{- define "mychart.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "mychart.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "mychart.labels" -}}
helm.sh/chart: {{ .Chart.Name }}-{{ .Chart.Version }}
{{ include "mychart.selectorLabels" . }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "mychart.selectorLabels" -}}
app.kubernetes.io/name: {{ include "mychart.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}
```

**Using Helpers**:
```yaml
# templates/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "mychart.fullname" . }}
  labels:
    {{- include "mychart.labels" . | nindent 4 }}
spec:
  selector:
    matchLabels:
      {{- include "mychart.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      labels:
        {{- include "mychart.selectorLabels" . | nindent 8 }}
```

### Conditional Resources

Only create resources when enabled:

```yaml
# templates/ingress.yaml
{{- if .Values.ingress.enabled -}}
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: {{ include "mychart.fullname" . }}
  {{- with .Values.ingress.annotations }}
  annotations:
    {{- toYaml . | nindent 4 }}
  {{- end }}
spec:
  {{- if .Values.ingress.className }}
  ingressClassName: {{ .Values.ingress.className }}
  {{- end }}
  rules:
  {{- range .Values.ingress.hosts }}
    - host: {{ .host | quote }}
      http:
        paths:
        {{- range .paths }}
          - path: {{ .path }}
            pathType: {{ .pathType }}
            backend:
              service:
                name: {{ include "mychart.fullname" $ }}
                port:
                  number: {{ $.Values.service.port }}
        {{- end }}
  {{- end }}
{{- end }}
```

### NOTES.txt

Provide instructions after installation:

```
# templates/NOTES.txt
Thank you for installing {{ .Chart.Name }}.

Your release is named {{ .Release.Name }}.

To learn more about the release, try:

  $ helm status {{ .Release.Name }}
  $ helm get all {{ .Release.Name }}

{{- if .Values.ingress.enabled }}
Application is available at:
{{- range .Values.ingress.hosts }}
  http{{ if $.Values.ingress.tls }}s{{ end }}://{{ .host }}
{{- end }}
{{- else }}
Get the application URL by running:
  export POD_NAME=$(kubectl get pods --namespace {{ .Release.Namespace }} -l "app.kubernetes.io/name={{ include "mychart.name" . }}" -o jsonpath="{.items[0].metadata.name}")
  kubectl --namespace {{ .Release.Namespace }} port-forward $POD_NAME 8080:80
  echo "Visit http://127.0.0.1:8080"
{{- end }}
```

## Values and Customization

### Multiple Values Files

```bash
# Base values
# values.yaml
replicaCount: 2
image:
  tag: "1.0.0"

# Development overrides
# values-dev.yaml
replicaCount: 1
resources:
  limits:
    memory: "256Mi"

# Production overrides
# values-prod.yaml
replicaCount: 5
resources:
  limits:
    memory: "1Gi"
ingress:
  enabled: true

# Install
helm install myapp ./mychart -f values-dev.yaml
helm install myapp ./mychart -f values-prod.yaml
```

### Merging Values

Values are merged in this order (last wins):
1. Default values in values.yaml
2. Values from `-f file1.yaml`
3. Values from `-f file2.yaml` (if multiple -f)
4. Values from `--set key=value`

```bash
# All these values are merged
helm install myapp ./mychart \
  -f values.yaml \
  -f values-prod.yaml \
  --set replicaCount=10 \
  --set image.tag=1.2.3
```

### Setting Values

**Command Line**:
```bash
# Simple value
--set replicaCount=3

# Nested value
--set image.tag=1.2.0

# List
--set environments[0].name=DEV,environments[0].value=development

# Multiple values
--set key1=val1,key2=val2

# String values
--set name="My App"

# null value
--set serviceAccount.name=null
```

### Values Schema Validation

Define schema to validate values:

```yaml
# values.schema.json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["replicaCount", "image"],
  "properties": {
    "replicaCount": {
      "type": "integer",
      "minimum": 1,
      "maximum": 10
    },
    "image": {
      "type": "object",
      "required": ["repository", "tag"],
      "properties": {
        "repository": {
          "type": "string"
        },
        "tag": {
          "type": "string",
          "pattern": "^[0-9]+\\.[0-9]+\\.[0-9]+$"
        }
      }
    }
  }
}
```

Helm validates values against this schema during install/upgrade.

## Chart Dependencies

### Defining Dependencies

```yaml
# Chart.yaml
dependencies:
  - name: postgresql
    version: "11.x.x"
    repository: https://charts.bitnami.com/bitnami
    condition: postgresql.enabled
    tags:
      - database

  - name: redis
    version: "17.x.x"
    repository: https://charts.bitnami.com/bitnami
    condition: redis.enabled
    tags:
      - cache
```

### Managing Dependencies

```bash
# Download dependencies
helm dependency update ./mychart

# This creates:
# mychart/charts/postgresql-11.x.x.tgz
# mychart/charts/redis-17.x.x.tgz
# mychart/Chart.lock

# List dependencies
helm dependency list ./mychart

# Build dependencies (from charts/)
helm dependency build ./mychart
```

### Configuring Dependencies

Configure dependency values in parent chart's values.yaml:

```yaml
# values.yaml
postgresql:
  enabled: true
  auth:
    database: myapp
    username: myapp
    password: secret
  primary:
    persistence:
      size: 10Gi

redis:
  enabled: true
  auth:
    enabled: false
  master:
    persistence:
      size: 8Gi
```

### Conditional Dependencies

```yaml
# Chart.yaml
dependencies:
  - name: postgresql
    condition: postgresql.enabled    # Only install if true

  - name: redis
    tags:
      - cache
    condition: redis.enabled
```

```bash
# Disable dependency
helm install myapp ./mychart --set postgresql.enabled=false

# Enable/disable by tags
helm install myapp ./mychart --set tags.cache=false
```

## Helm Best Practices

### Chart Structure

1. **Keep templates simple**: Complex logic belongs in application code
2. **Use helpers**: Avoid repetition with _helpers.tpl
3. **Document values**: Comment all values in values.yaml
4. **Provide defaults**: Sensible defaults in values.yaml
5. **Support customization**: Allow overriding important settings

### Naming Conventions

```yaml
# Good naming
{{- define "mychart.fullname" -}}
{{- printf "%s-%s" .Release.Name .Chart.Name | trunc 63 | trimSuffix "-" }}
{{- end }}

# Use in resources
name: {{ include "mychart.fullname" . }}-deployment
name: {{ include "mychart.fullname" . }}-service
name: {{ include "mychart.fullname" . }}-configmap
```

### Labels

Use standard labels:

```yaml
{{- define "mychart.labels" -}}
app.kubernetes.io/name: {{ include "mychart.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
helm.sh/chart: {{ .Chart.Name }}-{{ .Chart.Version }}
{{- end }}
```

### Resource Management

Always allow resource customization:

```yaml
# values.yaml
resources:
  limits:
    cpu: 100m
    memory: 128Mi
  requests:
    cpu: 100m
    memory: 128Mi

# template
resources:
  {{- toYaml .Values.resources | nindent 10 }}
```

### Security

```yaml
# values.yaml
podSecurityContext:
  runAsNonRoot: true
  runAsUser: 1000
  fsGroup: 2000

securityContext:
  capabilities:
    drop:
    - ALL
  readOnlyRootFilesystem: true
  allowPrivilegeEscalation: false

# template
securityContext:
  {{- toYaml .Values.securityContext | nindent 10 }}
```

### Documentation

```yaml
# values.yaml with comments
# Number of replicas to deploy
# @default -- 2
replicaCount: 2

# Image configuration
image:
  # Image repository
  # @default -- myapp
  repository: myapp

  # Image pull policy
  # @default -- IfNotPresent
  pullPolicy: IfNotPresent

  # Image tag (defaults to Chart.AppVersion)
  # @default -- Chart.AppVersion
  tag: ""
```

### Testing Charts

```bash
# Lint chart
helm lint ./mychart

# Dry run install
helm install myapp ./mychart --dry-run --debug

# Template rendering (no API server needed)
helm template myapp ./mychart

# Template with values
helm template myapp ./mychart -f values-prod.yaml

# Test release
helm test myapp
```

### Chart Tests

```yaml
# templates/tests/test-connection.yaml
apiVersion: v1
kind: Pod
metadata:
  name: "{{ include "mychart.fullname" . }}-test-connection"
  annotations:
    "helm.sh/hook": test
spec:
  containers:
    - name: wget
      image: busybox
      command: ['wget']
      args: ['{{ include "mychart.fullname" . }}:{{ .Values.service.port }}']
  restartPolicy: Never
```

```bash
# Run tests
helm test myapp
```

## Helm for ML Applications

### ML Model Serving Chart

```yaml
# Chart.yaml
apiVersion: v2
name: ml-model-server
description: Helm chart for ML model serving
type: application
version: 0.1.0
appVersion: "1.0.0"

dependencies:
  - name: redis
    version: "17.x.x"
    repository: https://charts.bitnami.com/bitnami
    condition: redis.enabled
```

```yaml
# values.yaml
replicaCount: 3

image:
  repository: tensorflow/serving
  tag: "2.8.0-gpu"
  pullPolicy: IfNotPresent

model:
  name: "my_model"
  version: "1"
  basePath: "/models"
  configFile: ""

gpu:
  enabled: true
  count: 1

resources:
  requests:
    memory: "2Gi"
    cpu: "1"
  limits:
    memory: "4Gi"
    cpu: "2"

service:
  type: ClusterIP
  restPort: 8501
  grpcPort: 8500

autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70

monitoring:
  enabled: true
  serviceMonitor:
    enabled: true

redis:
  enabled: true
  auth:
    enabled: false

persistence:
  enabled: true
  size: 100Gi
  storageClass: ""
  accessMode: ReadOnlyMany

affinity:
  podAntiAffinity:
    preferredDuringSchedulingIgnoredDuringExecution:
    - weight: 100
      podAffinityTerm:
        labelSelector:
          matchExpressions:
          - key: app.kubernetes.io/name
            operator: In
            values:
            - ml-model-server
        topologyKey: kubernetes.io/hostname
```

```yaml
# templates/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "ml-model-server.fullname" . }}
  labels:
    {{- include "ml-model-server.labels" . | nindent 4 }}
spec:
  replicas: {{ .Values.replicaCount }}
  selector:
    matchLabels:
      {{- include "ml-model-server.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      labels:
        {{- include "ml-model-server.selectorLabels" . | nindent 8 }}
    spec:
      containers:
      - name: model-server
        image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
        ports:
        - name: rest
          containerPort: {{ .Values.service.restPort }}
        - name: grpc
          containerPort: {{ .Values.service.grpcPort }}
        env:
        - name: MODEL_NAME
          value: {{ .Values.model.name | quote }}
        - name: MODEL_BASE_PATH
          value: {{ .Values.model.basePath | quote }}
        {{- if .Values.redis.enabled }}
        - name: REDIS_HOST
          value: {{ .Release.Name }}-redis-master
        - name: REDIS_PORT
          value: "6379"
        {{- end }}
        resources:
          {{- toYaml .Values.resources | nindent 10 }}
        {{- if .Values.gpu.enabled }}
          limits:
            nvidia.com/gpu: {{ .Values.gpu.count }}
        {{- end }}
        volumeMounts:
        - name: model-storage
          mountPath: {{ .Values.model.basePath }}
          readOnly: true
        livenessProbe:
          httpGet:
            path: /v1/models/{{ .Values.model.name }}
            port: rest
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /v1/models/{{ .Values.model.name }}
            port: rest
          initialDelaySeconds: 10
          periodSeconds: 5
      volumes:
      - name: model-storage
        {{- if .Values.persistence.enabled }}
        persistentVolumeClaim:
          claimName: {{ include "ml-model-server.fullname" . }}-models
        {{- else }}
        emptyDir: {}
        {{- end }}
      {{- with .Values.affinity }}
      affinity:
        {{- toYaml . | nindent 8 }}
      {{- end }}
```

### Deploying ML Application

```bash
# Create values for production
cat > ml-prod-values.yaml <<EOF
replicaCount: 5

model:
  name: "resnet50"
  version: "1"

gpu:
  enabled: true
  count: 1

resources:
  requests:
    memory: "4Gi"
    cpu: "2"
  limits:
    memory: "8Gi"
    cpu: "4"

autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 20
  targetCPUUtilizationPercentage: 60

redis:
  enabled: true
  master:
    persistence:
      size: 10Gi

persistence:
  enabled: true
  size: 500Gi
  storageClass: "fast-ssd"

ingress:
  enabled: true
  hosts:
    - host: ml-api.example.com
      paths:
        - path: /
          pathType: Prefix
EOF

# Install
helm install ml-prod ./ml-model-server -f ml-prod-values.yaml

# Upgrade
helm upgrade ml-prod ./ml-model-server -f ml-prod-values.yaml

# Monitor rollout
kubectl rollout status deployment/ml-prod-ml-model-server
```

## Summary and Key Takeaways

### Key Concepts

- **Helm** is the package manager for Kubernetes
- **Charts** package Kubernetes applications
- **Releases** are chart instances deployed to clusters
- **Repositories** distribute charts
- **Values** customize chart behavior
- **Templates** use Go templates for dynamic manifests

### Helm Commands

```bash
# Repository management
helm repo add/update/list/remove

# Chart management
helm create/package/lint

# Release management
helm install/upgrade/rollback/uninstall

# Information
helm list/status/history/get

# Testing
helm test/lint/template
```

### Chart Structure

```
mychart/
├── Chart.yaml         # Metadata
├── values.yaml        # Default values
├── templates/         # Kubernetes manifests
│   ├── _helpers.tpl   # Helper templates
│   ├── NOTES.txt      # Usage instructions
│   └── *.yaml         # Resource templates
└── charts/            # Dependencies
```

### Best Practices

1. Use semantic versioning for charts
2. Document all values with comments
3. Provide sensible defaults
4. Use helpers for reusable templates
5. Apply standard labels
6. Allow resource customization
7. Test charts with `helm lint` and `helm test`
8. Use dependencies for complex applications
9. Secure secrets properly
10. Version control your charts

### Next Steps

- **Lecture 04**: Kubernetes Operations
- **Exercise 02**: Create a Helm chart for your application
- Practice with public charts from Artifact Hub
- Create charts for your ML models

### Further Reading

- Helm Documentation: https://helm.sh/docs/
- Artifact Hub: https://artifacthub.io/
- Chart Best Practices: https://helm.sh/docs/chart_best_practices/
- Helm GitHub: https://github.com/helm/helm

---

**Congratulations!** You now understand Helm and can package Kubernetes applications effectively. Practice creating charts to solidify your knowledge.
