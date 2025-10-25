# Disaster Recovery Plan: Production ML System

**Last Updated:** October 18, 2025
**Version:** 1.0
**Classification:** CONFIDENTIAL

---

## Table of Contents

1. [Overview](#overview)
2. [Recovery Objectives](#recovery-objectives)
3. [Backup Strategy](#backup-strategy)
4. [Recovery Procedures](#recovery-procedures)
5. [Testing Schedule](#testing-schedule)
6. [Roles and Responsibilities](#roles-and-responsibilities)

---

## Overview

This Disaster Recovery (DR) plan outlines procedures to recover the Production ML System in case of catastrophic failures including:

- Complete cluster failure
- Data center outage
- Ransomware attack
- Accidental data deletion
- Regional cloud provider outage
- Cascading system failures

### Scope

**In Scope:**
- Kubernetes cluster and workloads
- PostgreSQL database (MLflow metadata)
- Object storage (S3/MinIO) - models and artifacts
- Configuration (Git repositories)
- Secrets and credentials

**Out of Scope:**
- Cloud provider infrastructure (assumed recoverable via IaC)
- Network infrastructure
- Third-party SaaS services

---

## Recovery Objectives

### RTO (Recovery Time Objective)

Maximum acceptable downtime before system must be restored:

| Component | RTO | Priority |
|-----------|-----|----------|
| **ML API (Production)** | 1 hour | Critical |
| **MLflow** | 4 hours | High |
| **Monitoring** | 8 hours | Medium |
| **ML Pipeline** | 24 hours | Low |

### RPO (Recovery Point Objective)

Maximum acceptable data loss:

| Component | RPO | Backup Frequency |
|-----------|-----|------------------|
| **PostgreSQL** | 24 hours | Daily |
| **Model Artifacts** | 24 hours | Daily |
| **Configuration** | 0 (Git history) | Continuous |
| **Logs** | 1 week | Weekly archive |

### Service Level Agreement (SLA)

- **Production API Availability:** 99.9% uptime
- **Data Durability:** 99.999% (no data loss)
- **Mean Time to Recovery:** < 2 hours

---

## Backup Strategy

### What to Backup

1. **Kubernetes Resources**
   - Deployments, Services, ConfigMaps
   - Ingress, Secrets (encrypted)
   - Persistent Volume Claims

2. **Databases**
   - PostgreSQL (MLflow metadata)
   - Full database dump
   - Transaction logs

3. **Object Storage**
   - Model artifacts (S3/MinIO)
   - Training datasets
   - Experiment logs

4. **Configuration**
   - Git repositories (GitHub)
   - Infrastructure as Code (Terraform/Pulumi)
   - Helm charts and values

5. **Secrets** (Encrypted)
   - API keys
   - Database credentials
   - TLS certificates

### Backup Schedule

| Backup Type | Frequency | Retention | Storage Location |
|-------------|-----------|-----------|------------------|
| **Kubernetes Manifests** | Daily | 30 days | S3 (us-west-2) |
| **PostgreSQL Full** | Daily 2 AM UTC | 30 days | S3 (us-west-2 + us-east-1) |
| **PostgreSQL Incremental** | Hourly | 7 days | S3 (us-west-2) |
| **Model Artifacts** | Daily | 90 days | S3 (us-west-2 + us-east-1) |
| **Git Repositories** | Continuous | Unlimited | GitHub + Mirror |
| **Secrets (Encrypted)** | Weekly | 30 days | S3 (encrypted) + Vault |

### Backup Automation

#### Daily Kubernetes Backup Script

```bash
#!/bin/bash
# /scripts/backup-kubernetes.sh

BACKUP_DATE=$(date +%Y%m%d-%H%M%S)
BACKUP_DIR="/backups/${BACKUP_DATE}"
S3_BUCKET="s3://ml-system-backups"

# Create backup directory
mkdir -p ${BACKUP_DIR}

# Backup all resources in production namespace
kubectl get all -n ml-system-production -o yaml > ${BACKUP_DIR}/all-resources.yaml
kubectl get configmap -n ml-system-production -o yaml > ${BACKUP_DIR}/configmaps.yaml
kubectl get secret -n ml-system-production -o yaml > ${BACKUP_DIR}/secrets.yaml
kubectl get pvc -n ml-system-production -o yaml > ${BACKUP_DIR}/pvcs.yaml
kubectl get ingress -n ml-system-production -o yaml > ${BACKUP_DIR}/ingress.yaml

# Backup PostgreSQL
kubectl exec -n ml-system-production postgresql-0 -- \
  pg_dump -U mlflow mlflow > ${BACKUP_DIR}/mlflow-db.sql

# Compress backup
tar -czf ${BACKUP_DIR}.tar.gz ${BACKUP_DIR}

# Upload to S3 (primary region)
aws s3 cp ${BACKUP_DIR}.tar.gz ${S3_BUCKET}/${BACKUP_DATE}.tar.gz

# Replicate to secondary region
aws s3 cp ${S3_BUCKET}/${BACKUP_DATE}.tar.gz \
  s3://ml-system-backups-dr/$(basename ${BACKUP_DIR}).tar.gz \
  --source-region us-west-2 \
  --region us-east-1

# Cleanup local backup (keep only last 7 days)
find /backups -type d -mtime +7 -exec rm -rf {} \;

echo "Backup completed: ${BACKUP_DATE}"
```

#### Automated Backup Cron Job

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: backup-cronjob
  namespace: ml-system-production
spec:
  schedule: "0 2 * * *"  # Daily at 2 AM UTC
  jobTemplate:
    spec:
      template:
        spec:
          serviceAccountName: backup-sa
          containers:
          - name: backup
            image: backup-tools:latest
            command: ["/scripts/backup-kubernetes.sh"]
            volumeMounts:
            - name: backups
              mountPath: /backups
          volumes:
          - name: backups
            persistentVolumeClaim:
              claimName: backup-pvc
          restartPolicy: OnFailure
```

### Backup Verification

**Weekly verification:**
- Restore backup to test environment
- Verify data integrity
- Test application functionality
- Document any issues

```bash
# Verification script
#!/bin/bash
# /scripts/verify-backup.sh

LATEST_BACKUP=$(aws s3 ls s3://ml-system-backups/ | sort | tail -n 1 | awk '{print $4}')

# Download backup
aws s3 cp s3://ml-system-backups/${LATEST_BACKUP} /tmp/

# Extract
tar -xzf /tmp/${LATEST_BACKUP} -C /tmp/

# Restore to test namespace
kubectl apply -f /tmp/backups/*/all-resources.yaml --namespace=ml-system-test

# Run smoke tests
pytest tests/integration/test_e2e.py --api-url=https://test.example.com

echo "Backup verification completed"
```

---

## Recovery Procedures

### Scenario 1: Single Pod Failure

**Symptoms:** One or more pods crash or become unresponsive

**RTO:** < 2 minutes (automatic)

**Recovery:**
1. Kubernetes automatically restarts failed pods
2. Health checks remove unhealthy pods from service
3. No manual intervention required

**Verification:**
```bash
kubectl get pods -n ml-system-production
kubectl logs -n ml-system-production <pod-name>
```

---

### Scenario 2: Node Failure

**Symptoms:** Entire node becomes unavailable

**RTO:** < 5 minutes (automatic)

**Recovery:**
1. Kubernetes detects node failure
2. Reschedules pods to healthy nodes
3. Services continue with reduced capacity
4. Auto-scaling may trigger to add capacity

**Manual intervention (if needed):**
```bash
# Drain failing node
kubectl drain <node-name> --ignore-daemonsets --delete-emptydir-data

# Delete node
kubectl delete node <node-name>

# Add new node (via cloud provider)
# Node auto-joins cluster via autoscaling group
```

**Verification:**
```bash
kubectl get nodes
kubectl get pods -n ml-system-production -o wide
```

---

### Scenario 3: Database Failure

**Symptoms:** PostgreSQL pod crashes or data corruption

**RTO:** < 30 minutes

**Recovery:**

#### Step 1: Identify Failure
```bash
# Check database pod
kubectl get pods -n ml-system-production | grep postgres

# Check logs
kubectl logs -n ml-system-production postgresql-0
```

#### Step 2: Attempt Automatic Recovery
If using replicated PostgreSQL:
```bash
# Promote replica to primary
# (This depends on your PostgreSQL setup: Patroni, Stolon, etc.)
```

#### Step 3: Restore from Backup
```bash
# Get latest backup
LATEST_BACKUP=$(aws s3 ls s3://ml-system-backups/ | grep mlflow-db | sort | tail -n 1 | awk '{print $4}')

# Download backup
aws s3 cp s3://ml-system-backups/${LATEST_BACKUP} /tmp/mlflow-db.sql.gz

# Extract
gunzip /tmp/mlflow-db.sql.gz

# Delete existing database (if corrupted)
kubectl exec -n ml-system-production postgresql-0 -- dropdb -U mlflow mlflow

# Create new database
kubectl exec -n ml-system-production postgresql-0 -- createdb -U mlflow mlflow

# Restore from backup
kubectl exec -i -n ml-system-production postgresql-0 -- \
  psql -U mlflow mlflow < /tmp/mlflow-db.sql
```

#### Step 4: Verify Recovery
```bash
# Check database connectivity
kubectl exec -n ml-system-production postgresql-0 -- psql -U mlflow -c "SELECT COUNT(*) FROM experiments;"

# Restart ML API pods to reconnect
kubectl rollout restart deployment/ml-api -n ml-system-production
```

**Data Loss:** Up to 24 hours (last backup)

---

### Scenario 4: Complete Cluster Failure

**Symptoms:** Entire Kubernetes cluster unavailable

**RTO:** < 1 hour

**Recovery:**

#### Step 1: Provision New Cluster

```bash
# If using managed Kubernetes (GKE/EKS/AKS):
# Create new cluster via cloud provider console or CLI

# Example for GKE:
gcloud container clusters create ml-cluster-dr \
  --zone us-east1-a \
  --num-nodes 5 \
  --machine-type n1-standard-8 \
  --enable-autoscaling --min-nodes 3 --max-nodes 20

# Get credentials
gcloud container clusters get-credentials ml-cluster-dr --zone us-east1-a
```

#### Step 2: Install Core Infrastructure

```bash
# Install NGINX Ingress
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace

# Install cert-manager
helm repo add jetstack https://charts.jetstack.io
helm install cert-manager jetstack/cert-manager \
  --namespace cert-manager \
  --create-namespace \
  --set installCRDs=true

# Install Prometheus/Grafana
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace
```

#### Step 3: Restore Application

```bash
# Download latest backup
LATEST_BACKUP=$(aws s3 ls s3://ml-system-backups/ | sort | tail -n 1 | awk '{print $4}')
aws s3 cp s3://ml-system-backups/${LATEST_BACKUP} /tmp/
tar -xzf /tmp/${LATEST_BACKUP} -C /tmp/

# Create namespace
kubectl create namespace ml-system-production

# Restore secrets (decrypt first if encrypted)
kubectl apply -f /tmp/backups/*/secrets.yaml

# Restore ConfigMaps
kubectl apply -f /tmp/backups/*/configmaps.yaml

# Restore PVCs
kubectl apply -f /tmp/backups/*/pvcs.yaml

# Restore application
kubectl apply -f /tmp/backups/*/all-resources.yaml

# Wait for pods to be ready
kubectl wait --for=condition=Ready pods -l app=ml-api \
  -n ml-system-production --timeout=10m
```

#### Step 4: Restore Database

```bash
# Restore PostgreSQL (same as Scenario 3, Step 3)
```

#### Step 5: Update DNS

```bash
# Get new LoadBalancer IP
NEW_IP=$(kubectl get svc ingress-nginx-controller -n ingress-nginx \
  -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

# Update DNS A record to point to NEW_IP
# (Do this in your DNS provider)

echo "Update DNS: api.example.com → ${NEW_IP}"
```

#### Step 6: Verify Recovery

```bash
# Wait for DNS propagation
# dig api.example.com

# Test endpoint
curl https://api.example.com/health

# Run integration tests
export API_URL=https://api.example.com
export API_KEY=$PRODUCTION_API_KEY
pytest tests/integration/test_e2e.py -v
```

#### Step 7: Monitor

- Watch Grafana dashboards
- Check error rates and latency
- Review logs for issues
- Monitor for 24 hours

---

### Scenario 5: Ransomware Attack / Data Deletion

**Symptoms:** Unexpected data deletion, encryption, or corruption

**RTO:** < 4 hours

**Recovery:**

#### Step 1: Isolate and Assess

```bash
# Immediately isolate affected systems
# Disconnect from network if needed

# Assess damage
# Identify what data/systems are affected
```

#### Step 2: Restore from Immutable Backup

```bash
# Use backup from BEFORE the attack
# Backups should be in immutable storage (S3 Object Lock)

# List available backups
aws s3 ls s3://ml-system-backups/ | grep $(date -d '7 days ago' +%Y%m%d)

# Restore from pre-attack backup
# Follow steps from Scenario 4
```

#### Step 3: Security Review

- Change all credentials and API keys
- Rotate TLS certificates
- Review audit logs
- Identify attack vector
- Patch vulnerabilities

#### Step 4: Verify Data Integrity

```bash
# Check restored data integrity
# Compare checksums with known good backups
# Run data validation tests
```

---

## Testing Schedule

### Backup Testing

| Test Type | Frequency | Responsible | Duration |
|-----------|-----------|-------------|----------|
| **Backup verification** | Weekly | DevOps | 30 min |
| **Single pod recovery** | Monthly | DevOps | 15 min |
| **Database restore** | Quarterly | DevOps + DBA | 2 hours |
| **Full DR exercise** | Annually | All teams | 8 hours |

### Annual DR Exercise

**Date:** First Saturday of Q1 (January)
**Duration:** 8 hours
**Participants:** DevOps, SRE, Engineering, Management

**Procedure:**
1. **Simulate failure** - Take down production cluster (during maintenance window)
2. **Execute recovery** - Follow DR procedures
3. **Verify functionality** - Run full test suite
4. **Document issues** - Record any problems encountered
5. **Update plan** - Revise DR plan based on learnings
6. **Report results** - Present to leadership

---

## Roles and Responsibilities

### Incident Commander
- **Primary:** Engineering Manager
- **Backup:** Senior DevOps Engineer
- **Responsibilities:**
  - Declare disaster
  - Coordinate recovery efforts
  - Communicate with stakeholders
  - Make decisions on recovery strategy

### Recovery Team

**DevOps Engineers:**
- Execute recovery procedures
- Restore infrastructure
- Verify system health

**Database Administrators:**
- Restore databases
- Verify data integrity
- Optimize queries post-recovery

**Software Engineers:**
- Verify application functionality
- Fix any issues discovered
- Support testing

**SRE/On-Call:**
- Monitor recovery progress
- Escalate issues
- Provide 24/7 coverage

### Communication

**Internal:**
- Status updates every 30 minutes
- Slack #incident-response channel
- Email updates to leadership

**External:**
- Status page updates (status.example.com)
- Customer notifications (if SLA impacted)
- Post-mortem report (public if appropriate)

---

## Emergency Contacts

| Role | Name | Phone | Email |
|------|------|-------|-------|
| **Incident Commander** | TBD | TBD | TBD |
| **DevOps Lead** | TBD | TBD | TBD |
| **Engineering Manager** | TBD | TBD | TBD |
| **CTO** | TBD | TBD | TBD |
| **Cloud Provider Support** | - | - | support@cloudprovider.com |
| **Security Team** | - | - | security@example.com |

**Emergency Escalation:**
1. On-call engineer (PagerDuty)
2. DevOps lead
3. Engineering manager
4. CTO

---

## Post-Recovery

### Immediate Actions (0-4 hours)

1. **Verify system health**
   - All services operational
   - No data loss or corruption
   - Performance metrics normal

2. **Monitor continuously**
   - Watch for anomalies
   - Check error rates
   - Review logs

3. **Communicate status**
   - Update status page
   - Notify stakeholders
   - Send all-clear message

### Short-term Actions (4-24 hours)

1. **Root cause analysis**
   - Identify what caused the failure
   - Document timeline
   - Collect evidence

2. **Assess impact**
   - Calculate downtime
   - Measure data loss
   - Estimate business impact

3. **Create action items**
   - Preventive measures
   - Process improvements
   - Infrastructure changes

### Long-term Actions (1-4 weeks)

1. **Post-mortem**
   - Write detailed report
   - Share with team
   - Present to leadership

2. **Implement improvements**
   - Fix root causes
   - Update runbooks
   - Enhance monitoring

3. **Update DR plan**
   - Incorporate lessons learned
   - Revise procedures
   - Update documentation

4. **Training**
   - Train team on new procedures
   - Conduct tabletop exercises
   - Update knowledge base

---

## Continuous Improvement

This DR plan should be reviewed and updated:

- **Quarterly:** After each DR test
- **After incidents:** Following any actual disaster recovery
- **With changes:** When system architecture changes
- **Annually:** Comprehensive review

**Document Version:** 1.0
**Last Tested:** [To be filled after first test]
**Next Review:** January 18, 2026
**Owner:** DevOps Team

---

**Remember:** Practice makes perfect. The more you test your DR procedures, the smoother actual recovery will be!
