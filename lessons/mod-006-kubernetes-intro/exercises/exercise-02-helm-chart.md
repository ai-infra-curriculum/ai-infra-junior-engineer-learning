# Exercise 02: Create a Helm Chart

## Overview

In this exercise, you'll create a Helm chart from scratch for a Python Flask application, customize it for different environments, and learn best practices for Helm chart development. This builds on your Kubernetes knowledge by adding the power of templating and package management.

## Learning Objectives

By completing this exercise, you will:
- Create a Helm chart from scratch
- Understand Helm chart structure and conventions
- Write Go templates for Kubernetes manifests
- Create reusable helper functions in _helpers.tpl
- Customize deployments with values files
- Manage chart dependencies
- Test and validate Helm charts
- Package and distribute charts

## Prerequisites

- Completed Exercise 01 (First Deployment)
- Completed Lecture 03 (Helm)
- Helm 3.x installed
- kubectl configured
- Access to a Kubernetes cluster
- Basic understanding of Go templates (helpful but not required)

## Setup

```bash
# Verify Helm installation
helm version

# Create working directory
mkdir -p ~/helm-exercises/exercise-02
cd ~/helm-exercises/exercise-02

# Create namespace
kubectl create namespace helm-demo
kubectl config set-context --current --namespace=helm-demo
```

## Part 1: Create Basic Helm Chart

### Step 1: Generate Chart Scaffold

```bash
# Create new chart
helm create flask-app

# Explore the generated structure
tree flask-app

# Output:
# flask-app/
# ├── .helmignore
# ├── Chart.yaml
# ├── values.yaml
# ├── charts/
# └── templates/
#     ├── NOTES.txt
#     ├── _helpers.tpl
#     ├── deployment.yaml
#     ├── hpa.yaml
#     ├── ingress.yaml
#     ├── service.yaml
#     ├── serviceaccount.yaml
#     └── tests/
#         └── test-connection.yaml

# Enter chart directory
cd flask-app
```

### Step 2: Understand Chart.yaml

View and modify `Chart.yaml`:

```yaml
apiVersion: v2
name: flask-app
description: A Helm chart for Flask application
type: application
version: 0.1.0
appVersion: "1.0.0"

keywords:
  - flask
  - python
  - api
  - web

maintainers:
  - name: Your Name
    email: your.email@example.com

home: https://github.com/yourusername/flask-app
sources:
  - https://github.com/yourusername/flask-app

# Optional: icon URL
# icon: https://example.com/icon.png
```

**Questions**:
1. What's the difference between `version` and `appVersion`?
2. When should you increment each version?

### Step 3: Customize values.yaml

Edit `values.yaml` with Flask-specific defaults:

```yaml
# Default values for flask-app

replicaCount: 2

image:
  repository: tiangolo/uwsgi-nginx-flask
  pullPolicy: IfNotPresent
  tag: "python3.9"

imagePullSecrets: []
nameOverride: ""
fullnameOverride: ""

serviceAccount:
  create: true
  annotations: {}
  name: ""

podAnnotations:
  prometheus.io/scrape: "true"
  prometheus.io/port: "9090"

podSecurityContext:
  runAsNonRoot: true
  runAsUser: 1000
  fsGroup: 2000

securityContext:
  capabilities:
    drop:
    - ALL
  readOnlyRootFilesystem: false  # Flask needs write for temp files
  allowPrivilegeEscalation: false

service:
  type: ClusterIP
  port: 80
  targetPort: 80

ingress:
  enabled: false
  className: "nginx"
  annotations: {}
    # kubernetes.io/ingress.class: nginx
    # cert-manager.io/cluster-issuer: letsencrypt-prod
  hosts:
    - host: flask-app.local
      paths:
        - path: /
          pathType: Prefix
  tls: []
  #  - secretName: flask-app-tls
  #    hosts:
  #      - flask-app.local

resources:
  limits:
    cpu: 200m
    memory: 256Mi
  requests:
    cpu: 100m
    memory: 128Mi

autoscaling:
  enabled: false
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70
  targetMemoryUtilizationPercentage: 80

# Flask-specific configuration
flask:
  env: production
  debug: false
  secretKey: "change-me-in-production"

# Database configuration (optional)
database:
  enabled: false
  host: postgresql
  port: 5432
  name: flaskdb
  username: flaskuser

# Redis configuration (optional)
redis:
  enabled: false
  host: redis-master
  port: 6379

nodeSelector: {}

tolerations: []

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
            - flask-app
        topologyKey: kubernetes.io/hostname
```

## Part 2: Create Templates

### Step 4: Update Deployment Template

Edit `templates/deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "flask-app.fullname" . }}
  labels:
    {{- include "flask-app.labels" . | nindent 4 }}
spec:
  {{- if not .Values.autoscaling.enabled }}
  replicas: {{ .Values.replicaCount }}
  {{- end }}
  selector:
    matchLabels:
      {{- include "flask-app.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      annotations:
        checksum/config: {{ include (print $.Template.BasePath "/configmap.yaml") . | sha256sum }}
      {{- with .Values.podAnnotations }}
        {{- toYaml . | nindent 8 }}
      {{- end }}
      labels:
        {{- include "flask-app.selectorLabels" . | nindent 8 }}
    spec:
      {{- with .Values.imagePullSecrets }}
      imagePullSecrets:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      serviceAccountName: {{ include "flask-app.serviceAccountName" . }}
      securityContext:
        {{- toYaml .Values.podSecurityContext | nindent 8 }}
      containers:
      - name: {{ .Chart.Name }}
        securityContext:
          {{- toYaml .Values.securityContext | nindent 12 }}
        image: "{{ .Values.image.repository }}:{{ .Values.image.tag | default .Chart.AppVersion }}"
        imagePullPolicy: {{ .Values.image.pullPolicy }}
        ports:
        - name: http
          containerPort: {{ .Values.service.targetPort }}
          protocol: TCP
        env:
        - name: FLASK_ENV
          value: {{ .Values.flask.env | quote }}
        - name: FLASK_DEBUG
          value: {{ .Values.flask.debug | quote }}
        {{- if .Values.database.enabled }}
        - name: DATABASE_HOST
          value: {{ .Values.database.host | quote }}
        - name: DATABASE_PORT
          value: {{ .Values.database.port | quote }}
        - name: DATABASE_NAME
          value: {{ .Values.database.name | quote }}
        - name: DATABASE_USERNAME
          valueFrom:
            secretKeyRef:
              name: {{ include "flask-app.fullname" . }}-db
              key: username
        - name: DATABASE_PASSWORD
          valueFrom:
            secretKeyRef:
              name: {{ include "flask-app.fullname" . }}-db
              key: password
        {{- end }}
        {{- if .Values.redis.enabled }}
        - name: REDIS_HOST
          value: {{ .Values.redis.host | quote }}
        - name: REDIS_PORT
          value: {{ .Values.redis.port | quote }}
        {{- end }}
        envFrom:
        - configMapRef:
            name: {{ include "flask-app.fullname" . }}
        livenessProbe:
          httpGet:
            path: /health
            port: http
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /ready
            port: http
          initialDelaySeconds: 10
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 3
        resources:
          {{- toYaml .Values.resources | nindent 12 }}
      {{- with .Values.nodeSelector }}
      nodeSelector:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      {{- with .Values.affinity }}
      affinity:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      {{- with .Values.tolerations }}
      tolerations:
        {{- toYaml . | nindent 8 }}
      {{- end }}
```

### Step 5: Create ConfigMap Template

Create `templates/configmap.yaml`:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: {{ include "flask-app.fullname" . }}
  labels:
    {{- include "flask-app.labels" . | nindent 4 }}
data:
  FLASK_APP: "app.py"
  LOG_LEVEL: "INFO"
  {{- range $key, $value := .Values.flask }}
  {{- if ne $key "secretKey" }}
  {{ $key | upper }}: {{ $value | quote }}
  {{- end }}
  {{- end }}
```

### Step 6: Create Secret Template

Create `templates/secret.yaml`:

```yaml
{{- if .Values.database.enabled }}
apiVersion: v1
kind: Secret
metadata:
  name: {{ include "flask-app.fullname" . }}-db
  labels:
    {{- include "flask-app.labels" . | nindent 4 }}
type: Opaque
data:
  username: {{ .Values.database.username | b64enc }}
  password: {{ .Values.database.password | default (randAlphaNum 16) | b64enc }}
{{- end }}
---
apiVersion: v1
kind: Secret
metadata:
  name: {{ include "flask-app.fullname" . }}-flask
  labels:
    {{- include "flask-app.labels" . | nindent 4 }}
type: Opaque
data:
  secret-key: {{ .Values.flask.secretKey | b64enc }}
```

### Step 7: Update Service Template

The generated `templates/service.yaml` should work, but verify it looks like:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: {{ include "flask-app.fullname" . }}
  labels:
    {{- include "flask-app.labels" . | nindent 4 }}
spec:
  type: {{ .Values.service.type }}
  ports:
    - port: {{ .Values.service.port }}
      targetPort: http
      protocol: TCP
      name: http
  selector:
    {{- include "flask-app.selectorLabels" . | nindent 4 }}
```

## Part 3: Helpers and Functions

### Step 8: Update _helpers.tpl

Edit `templates/_helpers.tpl`:

```yaml
{{/*
Expand the name of the chart.
*/}}
{{- define "flask-app.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "flask-app.fullname" -}}
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
Create chart name and version as used by the chart label.
*/}}
{{- define "flask-app.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "flask-app.labels" -}}
helm.sh/chart: {{ include "flask-app.chart" . }}
{{ include "flask-app.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "flask-app.selectorLabels" -}}
app.kubernetes.io/name: {{ include "flask-app.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "flask-app.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "flask-app.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Generate database URL
*/}}
{{- define "flask-app.databaseURL" -}}
{{- if .Values.database.enabled }}
{{- printf "postgresql://%s@%s:%s/%s" .Values.database.username .Values.database.host (.Values.database.port | toString) .Values.database.name }}
{{- end }}
{{- end }}
```

### Step 9: Update NOTES.txt

Edit `templates/NOTES.txt`:

```
Thank you for installing {{ .Chart.Name }}.

Your release is named {{ .Release.Name }}.
Release version: {{ .Chart.AppVersion }}

To learn more about the release, try:

  $ helm status {{ .Release.Name }}
  $ helm get all {{ .Release.Name }}

{{- if .Values.ingress.enabled }}

Application is available at:
{{- range $host := .Values.ingress.hosts }}
  {{- range .paths }}
  http{{ if $.Values.ingress.tls }}s{{ end }}://{{ $host.host }}{{ .path }}
  {{- end }}
{{- end }}

{{- else if contains "NodePort" .Values.service.type }}

Get the application URL by running these commands:
  export NODE_PORT=$(kubectl get --namespace {{ .Release.Namespace }} -o jsonpath="{.spec.ports[0].nodePort}" services {{ include "flask-app.fullname" . }})
  export NODE_IP=$(kubectl get nodes --namespace {{ .Release.Namespace }} -o jsonpath="{.items[0].status.addresses[0].address}")
  echo http://$NODE_IP:$NODE_PORT

{{- else if contains "LoadBalancer" .Values.service.type }}

Get the application URL by running these commands:
  NOTE: It may take a few minutes for the LoadBalancer IP to be available.
  export SERVICE_IP=$(kubectl get svc --namespace {{ .Release.Namespace }} {{ include "flask-app.fullname" . }} --template "{{"{{ range (index .status.loadBalancer.ingress 0) }}{{.}}{{ end }}"}}")
  echo http://$SERVICE_IP:{{ .Values.service.port }}

{{- else if contains "ClusterIP" .Values.service.type }}

Get the application URL by running these commands:
  export POD_NAME=$(kubectl get pods --namespace {{ .Release.Namespace }} -l "app.kubernetes.io/name={{ include "flask-app.name" . }},app.kubernetes.io/instance={{ .Release.Name }}" -o jsonpath="{.items[0].metadata.name}")
  kubectl --namespace {{ .Release.Namespace }} port-forward $POD_NAME 8080:{{ .Values.service.targetPort }}
  echo "Visit http://127.0.0.1:8080 to use your application"
{{- end }}

{{- if .Values.database.enabled }}

Database configuration:
  Host: {{ .Values.database.host }}
  Port: {{ .Values.database.port }}
  Database: {{ .Values.database.name }}
  Username: {{ .Values.database.username }}
{{- end }}

{{- if .Values.redis.enabled }}

Redis configuration:
  Host: {{ .Values.redis.host }}
  Port: {{ .Values.redis.port }}
{{- end }}
```

## Part 4: Environment-Specific Values

### Step 10: Create Development Values

Create `values-dev.yaml`:

```yaml
replicaCount: 1

image:
  tag: "python3.9"

flask:
  env: development
  debug: true

resources:
  limits:
    cpu: 100m
    memory: 128Mi
  requests:
    cpu: 50m
    memory: 64Mi

service:
  type: NodePort

autoscaling:
  enabled: false
```

### Step 11: Create Production Values

Create `values-prod.yaml`:

```yaml
replicaCount: 5

image:
  tag: "python3.9"
  pullPolicy: Always

flask:
  env: production
  debug: false
  secretKey: "prod-secret-from-vault-12345"

resources:
  limits:
    cpu: 500m
    memory: 512Mi
  requests:
    cpu: 250m
    memory: 256Mi

service:
  type: ClusterIP

ingress:
  enabled: true
  className: "nginx"
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/rate-limit: "100"
  hosts:
    - host: flask-app.production.example.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: flask-app-tls
      hosts:
        - flask-app.production.example.com

autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 20
  targetCPUUtilizationPercentage: 60

database:
  enabled: true
  host: postgresql.production.svc.cluster.local
  port: 5432
  name: flaskdb_prod
  username: flaskuser
  password: "prod-password-from-vault"

redis:
  enabled: true
  host: redis-master.production.svc.cluster.local
  port: 6379

affinity:
  podAntiAffinity:
    requiredDuringSchedulingIgnoredDuringExecution:
    - labelSelector:
        matchExpressions:
        - key: app.kubernetes.io/name
          operator: In
          values:
          - flask-app
      topologyKey: kubernetes.io/hostname
```

## Part 5: Testing and Validation

### Step 12: Lint the Chart

```bash
# Go back to parent directory
cd ~/helm-exercises/exercise-02

# Lint chart
helm lint flask-app

# Should output: "1 chart(s) linted, 0 chart(s) failed"

# Lint with values
helm lint flask-app -f flask-app/values-dev.yaml
helm lint flask-app -f flask-app/values-prod.yaml
```

### Step 13: Dry Run

```bash
# Dry run with default values
helm install flask-dev ./flask-app --dry-run --debug

# Dry run with dev values
helm install flask-dev ./flask-app -f flask-app/values-dev.yaml --dry-run --debug

# Dry run with prod values
helm install flask-prod ./flask-app -f flask-app/values-prod.yaml --dry-run --debug

# Template rendering only (no API server)
helm template flask-dev ./flask-app -f flask-app/values-dev.yaml
```

### Step 14: Install Development Release

```bash
# Install with dev values
helm install flask-dev ./flask-app -f flask-app/values-dev.yaml

# Check release
helm list

# Check status
helm status flask-dev

# Check resources
kubectl get all
kubectl get configmap
kubectl get secret
```

### Step 15: Test the Application

```bash
# Get the NodePort
kubectl get service flask-dev-flask-app

# Test (adjust port as needed)
curl http://localhost:30XXX

# Port-forward if needed
kubectl port-forward svc/flask-dev-flask-app 8080:80
curl http://localhost:8080
```

## Part 6: Upgrades and Rollbacks

### Step 16: Upgrade the Release

```bash
# Modify values-dev.yaml
# Change replicaCount: 2

# Upgrade
helm upgrade flask-dev ./flask-app -f flask-app/values-dev.yaml

# Watch rollout
kubectl get pods -w

# Check history
helm history flask-dev
```

### Step 17: Rollback

```bash
# Rollback to previous revision
helm rollback flask-dev

# Or rollback to specific revision
helm rollback flask-dev 1

# Check history
helm history flask-dev
```

## Part 7: Chart Dependencies (Advanced)

### Step 18: Add PostgreSQL Dependency

Edit `Chart.yaml` and add dependency:

```yaml
dependencies:
  - name: postgresql
    version: "12.x.x"
    repository: https://charts.bitnami.com/bitnami
    condition: postgresql.enabled
```

### Step 19: Configure PostgreSQL

Update `values.yaml`:

```yaml
# Add at the end
postgresql:
  enabled: false
  auth:
    postgresPassword: "postgres"
    username: "flaskuser"
    password: "flaskpass"
    database: "flaskdb"
  primary:
    persistence:
      size: 1Gi
```

### Step 20: Install with Dependency

```bash
# Update dependencies
cd flask-app
helm dependency update

# This downloads postgresql chart to charts/ directory
ls charts/

# Install with PostgreSQL enabled
cd ..
cat > values-with-db.yaml <<EOF
replicaCount: 1

database:
  enabled: true
  host: flask-dev-postgresql
  port: 5432
  name: flaskdb
  username: flaskuser
  password: flaskpass

postgresql:
  enabled: true
EOF

helm install flask-with-db ./flask-app -f values-with-db.yaml

# Check resources (PostgreSQL pods created)
kubectl get pods
kubectl get pvc
```

## Part 8: Package and Share

### Step 21: Package the Chart

```bash
# Package chart
helm package flask-app

# Creates: flask-app-0.1.0.tgz

# Install from package
helm install flask-packaged flask-app-0.1.0.tgz
```

### Step 22: Create Chart Repository (Optional)

```bash
# Create index
helm repo index .

# Generated: index.yaml

# Can host on GitHub Pages, S3, etc.
# Users can add: helm repo add myrepo https://example.com/charts
```

## Cleanup

```bash
# List all releases
helm list

# Uninstall releases
helm uninstall flask-dev
helm uninstall flask-with-db
helm uninstall flask-packaged

# Delete namespace
kubectl delete namespace helm-demo

# Switch back to default namespace
kubectl config set-context --current --namespace=default
```

## Verification Checklist

- [ ] Created Helm chart from scratch
- [ ] Customized Chart.yaml with metadata
- [ ] Created comprehensive values.yaml
- [ ] Built templates for Deployment, Service, ConfigMap, Secret
- [ ] Wrote helper functions in _helpers.tpl
- [ ] Created environment-specific values files
- [ ] Linted chart successfully
- [ ] Performed dry-run installs
- [ ] Installed and tested releases
- [ ] Upgraded and rolled back releases
- [ ] Added chart dependencies
- [ ] Packaged chart for distribution

## Reflection Questions

1. **Templating**: How do Go templates make Kubernetes manifests reusable?

2. **Values**: What's the benefit of having separate values files for different environments?

3. **Helpers**: Why use helper functions in _helpers.tpl instead of repeating code?

4. **Dependencies**: When should you use chart dependencies vs separate installations?

5. **Versioning**: How do Chart version and appVersion differ? When do you increment each?

## Challenges

### Challenge 1: Add More Resources

Add these resources to your chart:
- HorizontalPodAutoscaler (conditionally based on values)
- NetworkPolicy
- PodDisruptionBudget
- ServiceMonitor (for Prometheus)

### Challenge 2: Advanced Templating

Implement:
- Multiple container support
- Init containers
- Sidecar containers
- Volume mounts from values

### Challenge 3: Testing

Write tests in `templates/tests/`:
- Test database connectivity
- Test API health endpoint
- Test Redis connectivity

### Challenge 4: CI/CD Integration

Create GitHub Actions workflow that:
- Lints chart on PR
- Runs `helm test` on merge
- Publishes chart to repository

## Common Issues and Solutions

### Issue: "Error: YAML parse error"

**Solution**: Check YAML indentation. Use `helm lint` to find issues.

### Issue: "Error: template: ... function \"include\" not defined"

**Solution**: Ensure _helpers.tpl exists and functions are properly defined.

### Issue: "Error: dependencies are not up to date"

**Solution**: Run `helm dependency update`.

### Issue: Values not applying

**Solution**: Check you're using `-f values-file.yaml` or values file is named correctly.

## Next Steps

- Complete Exercise 03: Debugging Kubernetes Issues
- Create Helm charts for your actual applications
- Publish charts to Artifact Hub
- Learn about Helm hooks for advanced workflows
- Explore Helmfile for managing multiple releases

## Additional Resources

- Helm Documentation: https://helm.sh/docs/
- Chart Best Practices: https://helm.sh/docs/chart_best_practices/
- Artifact Hub: https://artifacthub.io/
- Helm Template Functions: https://helm.sh/docs/chart_template_guide/function_list/

---

**Congratulations!** You've created a production-ready Helm chart. You can now package, version, and deploy complex Kubernetes applications with ease.

Save your chart as a template for future projects!
