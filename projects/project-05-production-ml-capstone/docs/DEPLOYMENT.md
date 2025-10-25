# Deployment Guide: Production ML System

**Last Updated:** October 18, 2025
**Version:** 1.0

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development Setup](#local-development-setup)
3. [Staging Deployment](#staging-deployment)
4. [Production Deployment](#production-deployment)
5. [Rollback Procedures](#rollback-procedures)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Tools

Install the following tools before deploying:

```bash
# kubectl (Kubernetes CLI)
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x kubectl
sudo mv kubectl /usr/local/bin/

# Helm (Kubernetes package manager)
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# kustomize (optional, built into kubectl)
kubectl version --client

# Docker
# Follow instructions at: https://docs.docker.com/get-docker/
```

### Required Access

Ensure you have:

- [ ] Kubernetes cluster access (kubeconfig file)
- [ ] Container registry credentials (ghcr.io, ECR, GCR)
- [ ] Domain name configured (for production)
- [ ] DNS access (to create A records)
- [ ] GitHub repository access
- [ ] Secrets (API keys, credentials)

### Infrastructure Requirements

**Development:**
- Minikube or kind
- 8GB RAM minimum
- 20GB disk space

**Staging:**
- Kubernetes cluster (3 nodes)
- Node size: 8GB RAM, 4 CPU
- LoadBalancer support
- Persistent storage (50GB)

**Production:**
- Kubernetes cluster (5+ nodes)
- Node size: 16GB RAM, 8 CPU
- Multi-zone deployment
- LoadBalancer with DDoS protection
- Persistent storage (200GB)

---

## Local Development Setup

### Step 1: Start Local Kubernetes

```bash
# Using Minikube
minikube start --memory=8192 --cpus=4

# Using kind
kind create cluster --config kind-config.yaml
```

### Step 2: Build Docker Image

```bash
# Build image
docker build -t ml-api:dev .

# Load image into Minikube (if using Minikube)
minikube image load ml-api:dev

# Or push to registry
docker tag ml-api:dev ghcr.io/your-org/ml-api:dev
docker push ghcr.io/your-org/ml-api:dev
```

### Step 3: Deploy to Local Kubernetes

```bash
# Deploy using kustomize
kubectl apply -k kubernetes/overlays/dev/

# Verify deployment
kubectl get pods -n ml-system-dev
kubectl get svc -n ml-system-dev

# Wait for pods to be ready
kubectl wait --for=condition=Ready pods -l app=ml-api -n ml-system-dev --timeout=5m
```

### Step 4: Access Local Application

```bash
# Port forward to access locally
kubectl port-forward -n ml-system-dev svc/ml-api 5000:80

# Test in another terminal
curl http://localhost:5000/health
```

### Step 5: View Logs

```bash
# View pod logs
kubectl logs -n ml-system-dev -l app=ml-api --tail=100 -f

# Describe pod for troubleshooting
kubectl describe pod -n ml-system-dev -l app=ml-api
```

---

## Staging Deployment

Staging deployment is **automatic** via CI/CD when code is merged to the `develop` branch.

### Manual Staging Deployment

If you need to deploy manually:

#### Step 1: Configure Access

```bash
# Set kubeconfig for staging cluster
export KUBECONFIG=/path/to/staging-kubeconfig.yaml

# Verify cluster access
kubectl cluster-info
kubectl get nodes
```

#### Step 2: Create Namespace

```bash
# Create namespace (if not exists)
kubectl create namespace ml-system-staging

# Verify
kubectl get namespace ml-system-staging
```

#### Step 3: Create Secrets

```bash
# Create secrets (DO NOT commit to Git!)
kubectl create secret generic api-keys \
  --from-literal=API_KEY=staging-api-key-here \
  -n ml-system-staging

kubectl create secret generic mlflow-credentials \
  --from-literal=password=mlflow-password-here \
  -n ml-system-staging
```

**Better approach: Use SealedSecrets**

```bash
# Install SealedSecrets controller
kubectl apply -f https://github.com/bitnami-labs/sealed-secrets/releases/download/v0.24.0/controller.yaml

# Create sealed secret
kubectl create secret generic api-keys \
  --from-literal=API_KEY=staging-api-key-here \
  --dry-run=client -o yaml | \
  kubeseal -o yaml > sealed-secret.yaml

# Commit sealed-secret.yaml to Git (it's encrypted)
kubectl apply -f sealed-secret.yaml
```

#### Step 4: Install Dependencies

```bash
# Install NGINX Ingress Controller
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update
helm upgrade --install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace \
  --set controller.service.type=LoadBalancer

# Install cert-manager
helm repo add jetstack https://charts.jetstack.io
helm repo update
helm upgrade --install cert-manager jetstack/cert-manager \
  --namespace cert-manager \
  --create-namespace \
  --set installCRDs=true

# Verify installations
kubectl get pods -n ingress-nginx
kubectl get pods -n cert-manager
```

#### Step 5: Configure DNS

```bash
# Get LoadBalancer IP
kubectl get svc ingress-nginx-controller -n ingress-nginx

# Create DNS A record pointing staging.example.com to LoadBalancer IP
# (Do this in your DNS provider: GoDaddy, Cloudflare, Route53, etc.)
```

#### Step 6: Deploy Application

```bash
# Deploy using kustomize
kubectl apply -k kubernetes/overlays/staging/

# Watch rollout
kubectl rollout status deployment/ml-api -n ml-system-staging

# Verify pods
kubectl get pods -n ml-system-staging
```

#### Step 7: Verify Certificate

```bash
# Wait for certificate to be ready
kubectl wait --for=condition=Ready certificate/staging-tls \
  -n ml-system-staging --timeout=5m

# Check certificate status
kubectl get certificate -n ml-system-staging
kubectl describe certificate staging-tls -n ml-system-staging

# Check ingress
kubectl get ingress -n ml-system-staging
```

#### Step 8: Test Deployment

```bash
# Test health endpoint
curl https://staging.example.com/health

# Test with API key
curl -H "X-API-Key: staging-api-key-here" \
  https://staging.example.com/info

# Run integration tests
export API_URL=https://staging.example.com
export API_KEY=staging-api-key-here
pytest tests/integration/test_e2e.py -v
```

---

## Production Deployment

Production deployment requires **manual approval** and uses a **canary deployment** strategy.

### Pre-Deployment Checklist

Before deploying to production:

- [ ] All tests passing in staging
- [ ] Security scan completed (no critical/high vulnerabilities)
- [ ] Load testing completed successfully
- [ ] Rollback procedure tested
- [ ] Disaster recovery plan reviewed
- [ ] Monitoring and alerts configured
- [ ] On-call team notified
- [ ] Change request approved (if required)
- [ ] Backup of current production verified
- [ ] Team ready for deployment window

### Production Deployment Steps

#### Step 1: Trigger CD Pipeline

Production deployment is triggered via GitHub Actions workflow:

```bash
# Navigate to GitHub Actions in your repository
# Select "CD Pipeline" workflow
# Click "Run workflow"
# Choose:
#   - environment: production
#   - image_tag: v1.2.3 (specific version, never 'latest')
# Click "Run workflow"
```

**Manual Approval Required:**
- GitHub will pause and request approval
- Team lead/manager must approve
- Approval gates ensure production safety

#### Step 2: Monitor Canary Deployment

Once approved, the pipeline:

1. Deploys canary pods (10% of traffic)
2. Monitors for 10 minutes:
   - Error rate < 0.1%
   - Latency P95 < 500ms
   - No crashes

#### Step 3: Promote or Rollback

If canary is healthy:
- Traffic gradually shifts: 10% → 25% → 50% → 100%
- Full rollout completes

If canary is unhealthy:
- Automatic rollback
- Alert sent to team
- Incident created

### Manual Production Deployment

If you need to deploy manually (emergency):

#### Step 1: Configure Access

```bash
# Set kubeconfig for production cluster
export KUBECONFIG=/path/to/production-kubeconfig.yaml

# Verify cluster access
kubectl cluster-info
kubectl get nodes
```

#### Step 2: Backup Current State

**CRITICAL: Always backup before production changes!**

```bash
# Backup current deployment
kubectl get all -n ml-system-production -o yaml > \
  backup-production-$(date +%Y%m%d-%H%M%S).yaml

# Backup ConfigMaps and Secrets
kubectl get configmap -n ml-system-production -o yaml >> \
  backup-production-$(date +%Y%m%d-%H%M%S).yaml
kubectl get secret -n ml-system-production -o yaml >> \
  backup-production-$(date +%Y%m%d-%H%M%S).yaml

# Store backup in safe location
aws s3 cp backup-production-*.yaml s3://your-backup-bucket/
```

#### Step 3: Deploy Canary

```bash
# Deploy canary (10% traffic)
helm upgrade ml-system ./helm/ml-system \
  --namespace ml-system-production \
  --values ./helm/ml-system/values-production.yaml \
  --set api.image.tag=v1.2.3 \
  --set api.canary.enabled=true \
  --set api.canary.weight=10 \
  --wait \
  --timeout 10m
```

#### Step 4: Monitor Canary

```bash
# Watch canary pod logs
kubectl logs -n ml-system-production -l version=canary -f

# Monitor Grafana dashboards
# Check error rate, latency, throughput

# Query Prometheus for error rate
# Error rate should be < 0.1%
```

**Monitor for 10-15 minutes**

If error rate increases or latency spikes, **ROLLBACK IMMEDIATELY**.

#### Step 5: Promote Canary

If metrics are healthy:

```bash
# Full rollout
helm upgrade ml-system ./helm/ml-system \
  --namespace ml-system-production \
  --values ./helm/ml-system/values-production.yaml \
  --set api.image.tag=v1.2.3 \
  --set api.canary.enabled=false \
  --wait \
  --timeout 15m

# Verify rollout
kubectl rollout status deployment/ml-api -n ml-system-production
```

#### Step 6: Verify Production

```bash
# Run smoke tests
curl https://api.example.com/health

export API_URL=https://api.example.com
export API_KEY=$PRODUCTION_API_KEY
pytest tests/integration/test_e2e.py -v --skip-slow

# Monitor for 1 hour minimum
# Watch Grafana, check logs, verify metrics
```

#### Step 7: Tag Deployment

```bash
# Tag Git commit
git tag -a "prod-v1.2.3" -m "Production deployment v1.2.3"
git push origin "prod-v1.2.3"

# Update MLflow (tag model as Production)
# (Run your model tagging script)
```

---

## Rollback Procedures

### When to Rollback

Rollback immediately if:
- Error rate > 1%
- P95 latency > 1 second
- Pod crashes
- Critical functionality broken
- Security issue discovered

### Automatic Rollback

The CD pipeline automatically rolls back if canary deployment fails.

### Manual Rollback (Helm)

```bash
# List releases
helm list -n ml-system-production

# Rollback to previous release
helm rollback ml-system -n ml-system-production

# Rollback to specific revision
helm rollback ml-system 5 -n ml-system-production

# Verify rollback
kubectl rollout status deployment/ml-api -n ml-system-production
```

### Manual Rollback (kubectl)

```bash
# Rollback deployment
kubectl rollout undo deployment/ml-api -n ml-system-production

# Rollback to specific revision
kubectl rollout undo deployment/ml-api --to-revision=3 -n ml-system-production

# Check rollout history
kubectl rollout history deployment/ml-api -n ml-system-production
```

### Rollback from Backup

If Helm/kubectl rollback fails:

```bash
# Restore from backup
kubectl apply -f backup-production-YYYYMMDD-HHMMSS.yaml

# Verify restoration
kubectl get pods -n ml-system-production
```

### Post-Rollback

After rollback:

1. **Notify team** - Alert via Slack/PagerDuty
2. **Create incident** - Document the issue
3. **Check logs** - Identify root cause
4. **Fix issue** - Address the problem
5. **Test in staging** - Verify fix
6. **Plan re-deployment** - Schedule next attempt

---

## Troubleshooting

### Pods Not Starting

```bash
# Check pod status
kubectl get pods -n ml-system-production

# Describe pod
kubectl describe pod <pod-name> -n ml-system-production

# Check events
kubectl get events -n ml-system-production --sort-by='.lastTimestamp'
```

**Common causes:**
- Image pull errors (wrong tag, registry auth)
- Resource limits (not enough CPU/memory)
- Configuration errors (wrong environment variables)
- Secrets missing

### Certificate Not Issuing

```bash
# Check certificate status
kubectl describe certificate <cert-name> -n ml-system-production

# Check cert-manager logs
kubectl logs -n cert-manager deploy/cert-manager -f

# Check challenges
kubectl get challenges -n ml-system-production
```

**Common causes:**
- DNS not pointing to LoadBalancer
- Firewall blocking port 80 (HTTP-01 challenge)
- Rate limits (use staging first!)

### High Error Rate

```bash
# Check application logs
kubectl logs -n ml-system-production -l app=ml-api --tail=200

# Check Grafana dashboards
# Open browser to Grafana URL

# Query Prometheus
kubectl port-forward -n monitoring svc/prometheus 9090:9090
# Open http://localhost:9090
```

**Common causes:**
- Model loading failure
- Database connection issues
- Resource exhaustion
- Dependency unavailable

### Deployment Stuck

```bash
# Check rollout status
kubectl rollout status deployment/ml-api -n ml-system-production

# Force rollback if stuck
kubectl rollout undo deployment/ml-api -n ml-system-production

# Delete stuck pods
kubectl delete pod <pod-name> -n ml-system-production --force --grace-period=0
```

---

## Best Practices

1. **Never deploy on Friday** (or before long weekend)
2. **Always backup** before production changes
3. **Test in staging** before production
4. **Monitor continuously** during and after deployment
5. **Have rollback plan ready** before deploying
6. **Use canary or blue/green** for production
7. **Tag deployments** in Git
8. **Document changes** in release notes
9. **Notify team** before deployment
10. **Review metrics** for 24 hours post-deployment

---

## Support

**For issues during deployment:**
- Check #ml-infrastructure Slack channel
- Page on-call engineer (PagerDuty)
- Review runbooks in `/docs/runbooks/`

**For urgent production issues:**
- Follow incident response procedure
- Contact: incidents@example.com

---

**Document Version:** 1.0
**Last Reviewed:** October 18, 2025
**Next Review:** January 18, 2026
