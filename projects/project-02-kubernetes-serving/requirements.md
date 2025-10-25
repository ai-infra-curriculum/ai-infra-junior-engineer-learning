# Project 02: Detailed Requirements

## Table of Contents
1. [Functional Requirements](#functional-requirements)
2. [Non-Functional Requirements](#non-functional-requirements)
3. [Kubernetes-Specific Requirements](#kubernetes-specific-requirements)
4. [Acceptance Criteria](#acceptance-criteria)

---

## Functional Requirements

### FR-1: Kubernetes Deployment Configuration

#### FR-1.1: Multi-Replica Deployment
**Requirement:** Deploy model API as Kubernetes Deployment with 3 replicas for high availability.

**Details:**
- Use `apps/v1` Deployment API
- Set `spec.replicas: 3` for baseline availability
- Configure appropriate pod labels for service discovery
- Implement proper selector matching

**Acceptance Criteria:**
- All 3 pods running and in Ready state
- Pods distributed across available nodes (if multi-node cluster)
- Deployment shows 3/3 available replicas
- Pods automatically recreated on failure

**Test:**
```bash
kubectl get deployment model-api -n ml-serving
# Should show: READY 3/3, UP-TO-DATE 3, AVAILABLE 3

kubectl get pods -n ml-serving
# Should show 3 pods with STATUS Running
```

---

#### FR-1.2: Resource Management
**Requirement:** Configure CPU and memory resource requests and limits for predictable performance.

**Details:**
- **CPU Requests:** 500m (0.5 cores) - guaranteed CPU allocation
- **CPU Limits:** 1000m (1 core) - maximum CPU usage
- **Memory Requests:** 1Gi - guaranteed memory allocation
- **Memory Limits:** 2Gi - maximum memory usage (prevents OOM kills)

**Rationale:**
- Requests ensure scheduling on nodes with sufficient resources
- Limits prevent resource starvation of other pods
- Memory limits should be 2x requests to handle traffic spikes
- CPU limits allow bursting during high load

**Acceptance Criteria:**
- Pods scheduled successfully with resource guarantees
- No OOMKilled events under normal load
- CPU throttling only occurs above 70% sustained usage
- Memory usage stays within limits during load tests

**Test:**
```bash
kubectl describe pod <pod-name> -n ml-serving | grep -A 8 Limits
# Should show configured requests and limits

kubectl top pod -n ml-serving
# Monitor actual resource usage
```

---

#### FR-1.3: Liveness Probe
**Requirement:** Implement liveness probe to detect and recover from application deadlocks.

**Details:**
- **Endpoint:** `GET /health`
- **Initial Delay:** 30 seconds (allow model loading time)
- **Period:** 10 seconds (check frequency)
- **Timeout:** 5 seconds (request timeout)
- **Failure Threshold:** 3 (consecutive failures before restart)

**Health Endpoint Behavior:**
- Returns 200 OK if application is responsive
- Returns 500 if application is in error state
- Checks internal application state (not just HTTP server)

**Acceptance Criteria:**
- Pod restarts automatically if unresponsive for 30 seconds (3 failures × 10s)
- No false positives during normal operation
- Liveness failures visible in pod events
- Application recovers successfully after restart

**Test:**
```bash
# Simulate application hang
kubectl exec <pod-name> -n ml-serving -- kill -STOP 1

# Wait 30-40 seconds, pod should restart
kubectl get events --field-selector involvedObject.name=<pod-name> -n ml-serving
# Should show liveness probe failure
```

---

#### FR-1.4: Readiness Probe
**Requirement:** Implement readiness probe to prevent traffic to pods not ready to serve requests.

**Details:**
- **Endpoint:** `GET /health`
- **Initial Delay:** 10 seconds (faster than liveness for quick startup)
- **Period:** 5 seconds (more frequent checks)
- **Timeout:** 3 seconds
- **Failure Threshold:** 3

**Health Endpoint Requirements:**
- Verify model is loaded in memory
- Check database connectivity (if applicable)
- Validate required configuration loaded
- Return 200 only when fully ready

**Acceptance Criteria:**
- New pods don't receive traffic until model is loaded
- Pods removed from service endpoints when not ready
- Rolling updates wait for new pods to be ready
- No 500 errors during pod startup

**Test:**
```bash
# Deploy new version
kubectl set image deployment/model-api model-api=model-api:v1.1 -n ml-serving

# Watch endpoints
kubectl get endpoints model-api-service -n ml-serving --watch
# Should only show ready pods
```

---

#### FR-1.5: Configuration Management
**Requirement:** Use ConfigMap for application configuration to separate config from code.

**Details:**
- **ConfigMap Name:** `model-config`
- **Configuration Keys:**
  - `model_name`: Model to load (e.g., "resnet50")
  - `log_level`: Logging verbosity (DEBUG, INFO, WARNING, ERROR)
  - `max_batch_size`: Maximum inference batch size
  - `timeout`: Request timeout in seconds

**Environment Variable Injection:**
```yaml
env:
  - name: MODEL_NAME
    valueFrom:
      configMapKeyRef:
        name: model-config
        key: model_name
```

**Acceptance Criteria:**
- Configuration changes don't require image rebuilds
- Pods automatically restart when ConfigMap updated (with proper annotations)
- Configuration validated on pod startup
- Invalid configuration prevents pod from becoming ready

**Test:**
```bash
# Update ConfigMap
kubectl edit configmap model-config -n ml-serving

# Verify pods reload (if using ConfigMap volume or reloader)
kubectl rollout status deployment/model-api -n ml-serving
```

---

### FR-2: Service & Load Balancing

#### FR-2.1: ClusterIP Service
**Requirement:** Create internal ClusterIP Service for pod-to-pod communication.

**Details:**
- **Service Type:** ClusterIP (default, internal only)
- **Port:** 80 (standard HTTP)
- **Target Port:** 5000 (application port)
- **Selector:** `app: model-api`
- **Session Affinity:** None (distribute evenly)

**Acceptance Criteria:**
- Service accessible from within cluster
- DNS name resolves: `model-api-service.ml-serving.svc.cluster.local`
- Traffic distributed round-robin across pods
- Service updates automatically when pods change

**Test:**
```bash
# From within cluster
kubectl run test-pod --image=curlimages/curl -it --rm -n ml-serving -- \
  curl http://model-api-service/health

# Check endpoints
kubectl get endpoints model-api-service -n ml-serving
```

---

#### FR-2.2: LoadBalancer Service
**Requirement:** Create external-facing LoadBalancer Service for internet access.

**Details:**
- **Service Type:** LoadBalancer (cloud provider integration)
- **External Port:** 80 (HTTP)
- **Target Port:** 5000
- **Load Balancer Source Ranges:** (Optional) Restrict by IP

**Cloud Provider Behavior:**
- **AWS EKS:** Creates Classic ELB or NLB
- **GCP GKE:** Creates TCP/UDP Load Balancer
- **Azure AKS:** Creates Azure Load Balancer
- **Minikube:** Use `minikube tunnel` for local testing

**Acceptance Criteria:**
- External IP assigned within 2 minutes
- Service accessible from internet
- Health checks configured at load balancer level
- SSL/TLS termination (if configured)

**Test:**
```bash
# Get external IP
kubectl get svc model-api-lb -n ml-serving
EXTERNAL_IP=$(kubectl get svc model-api-lb -n ml-serving -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

# Test from outside cluster
curl http://$EXTERNAL_IP/health
```

---

#### FR-2.3: Session Affinity (Optional)
**Requirement:** Configure session affinity if stateful sessions needed.

**Details:**
- **Type:** ClientIP
- **Timeout:** 3600 seconds (1 hour)
- **Use Case:** When client needs consistent pod routing

**Note:** For stateless ML inference, session affinity is typically NOT needed.

---

#### FR-2.4: Ingress Configuration
**Requirement:** Implement NGINX Ingress for HTTP routing with path-based rules.

**Details:**
- **Ingress Class:** nginx
- **Host:** `model-api.example.com`
- **Paths:**
  - `/predict` → model-api-service:80
  - `/health` → model-api-service:80
  - `/metrics` → model-api-service:80
- **TLS:** Optional (use cert-manager for automatic certificates)

**Annotations:**
- `nginx.ingress.kubernetes.io/rewrite-target: /`
- `nginx.ingress.kubernetes.io/ssl-redirect: "true"`
- `nginx.ingress.kubernetes.io/rate-limit: "100"` (requests per second)

**Acceptance Criteria:**
- Ingress controller provisions successfully
- Host-based routing works correctly
- Path-based routing directs to correct endpoints
- TLS certificates valid (if enabled)

**Test:**
```bash
# Get Ingress IP
kubectl get ingress -n ml-serving

# Test with host header
curl -H "Host: model-api.example.com" http://<ingress-ip>/health
```

---

### FR-3: Auto-Scaling

#### FR-3.1: Horizontal Pod Autoscaler (HPA)
**Requirement:** Configure HPA to automatically scale pods based on resource utilization.

**Details:**
- **Minimum Replicas:** 3 (baseline for availability)
- **Maximum Replicas:** 10 (cost control and cluster capacity)
- **Target CPU Utilization:** 70%
- **Target Memory Utilization:** 80%

**Scaling Behavior:**
- **Scale Up:** Aggressive (respond quickly to load)
  - Up to 100% increase per 30 seconds
  - Or max 2 pods per 30 seconds
  - No stabilization window (immediate scaling)

- **Scale Down:** Conservative (avoid flapping)
  - Max 50% decrease per 60 seconds
  - 5-minute stabilization window
  - Prevents rapid scale-down after brief traffic spikes

**Acceptance Criteria:**
- HPA monitors pod metrics every 15 seconds
- Scales up within 1 minute of reaching 70% CPU
- Scales down after 5 minutes of low utilization
- No rapid flapping between replica counts
- Scaling events visible in HPA status

**Test:**
```bash
# Generate load
kubectl run load-generator --image=busybox -n ml-serving -- /bin/sh -c \
  "while true; do wget -q -O- http://model-api-service/predict; done"

# Watch HPA
kubectl get hpa model-api-hpa -n ml-serving --watch

# Check scaling events
kubectl describe hpa model-api-hpa -n ml-serving
```

---

#### FR-3.2: Metrics Server
**Requirement:** Deploy and configure Kubernetes Metrics Server for HPA data.

**Details:**
- Metrics Server collects resource metrics from kubelets
- Provides CPU and memory data to HPA controller
- Updates every 15 seconds

**Installation:**
```bash
# For Minikube
minikube addons enable metrics-server

# For cloud clusters
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
```

**Acceptance Criteria:**
- `kubectl top nodes` returns data
- `kubectl top pods` returns data
- HPA shows current CPU/memory utilization
- Metrics updated within 30 seconds

---

### FR-4: Rolling Updates & Rollbacks

#### FR-4.1: RollingUpdate Strategy
**Requirement:** Implement zero-downtime deployment updates using RollingUpdate strategy.

**Details:**
- **Strategy Type:** RollingUpdate
- **Max Surge:** 1 (can create 1 extra pod during update)
- **Max Unavailable:** 0 (always maintain minimum replicas)
- **Min Ready Seconds:** 10 (wait before considering pod ready)

**Update Process:**
1. Create 1 new pod with new version
2. Wait for new pod to be ready
3. Terminate 1 old pod
4. Repeat until all pods updated

**Acceptance Criteria:**
- Zero request failures during update
- Always maintain minimum 3 pods available
- Update completes within 5 minutes for 3→3 pods
- Failed updates rollback automatically

**Test:**
```bash
# Update image version
kubectl set image deployment/model-api model-api=model-api:v1.1 -n ml-serving

# Watch rollout in real-time
kubectl rollout status deployment/model-api -n ml-serving

# Monitor requests during update (should have no errors)
while true; do curl http://<service-ip>/health; sleep 1; done
```

---

#### FR-4.2: Rollback Capability
**Requirement:** Support quick rollback to previous deployment version.

**Details:**
- Kubernetes maintains rollout history (default: 10 revisions)
- One-command rollback to previous version
- Rollback uses same RollingUpdate strategy

**Commands:**
```bash
# View rollout history
kubectl rollout history deployment/model-api -n ml-serving

# Rollback to previous version
kubectl rollout undo deployment/model-api -n ml-serving

# Rollback to specific revision
kubectl rollout undo deployment/model-api --to-revision=2 -n ml-serving
```

**Acceptance Criteria:**
- Rollback completes within 2 minutes
- Zero downtime during rollback
- Rollout history shows all revisions
- Can rollback to any previous revision

---

### FR-5: Monitoring & Observability

#### FR-5.1: Prometheus Deployment
**Requirement:** Deploy Prometheus for metrics collection and storage.

**Details:**
- **Deployment Method:** Helm chart (prometheus-community/prometheus)
- **Retention:** 7 days
- **Scrape Interval:** 30 seconds
- **Scrape Targets:**
  - Kubernetes API server metrics
  - Node metrics (via node-exporter)
  - Pod metrics (via cAdvisor)
  - Application metrics (via /metrics endpoint)

**ServiceMonitor Configuration:**
```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: model-api-metrics
spec:
  selector:
    matchLabels:
      app: model-api
  endpoints:
  - port: http
    path: /metrics
    interval: 30s
```

**Acceptance Criteria:**
- Prometheus scrapes all targets successfully
- No more than 1% scrape failures
- Metrics visible in Prometheus UI
- Data retained for 7 days

---

#### FR-5.2: Grafana Dashboards
**Requirement:** Deploy Grafana and create comprehensive dashboards.

**Details:**
- **Deployment Method:** Helm chart (grafana/grafana)
- **Data Source:** Prometheus
- **Required Dashboards:**
  1. **Cluster Overview:** Node count, total CPU/memory
  2. **Application Metrics:** Request rate, latency, errors
  3. **Pod Metrics:** Pod count, restarts, resource usage
  4. **HPA Metrics:** Current/desired replicas, scaling events

**Key Panels:**
- **Pod Count Over Time:** `count(kube_pod_info{namespace="ml-serving"})`
- **CPU Usage:** `rate(container_cpu_usage_seconds_total{pod=~"model-api.*"}[5m])`
- **Memory Usage:** `container_memory_usage_bytes{pod=~"model-api.*"}`
- **Request Rate:** `rate(model_api_requests_total[5m])`
- **Error Rate:** `rate(model_api_requests_total{status=~"5.."}[5m])`
- **P95 Latency:** `histogram_quantile(0.95, rate(model_api_request_duration_seconds_bucket[5m]))`

**Acceptance Criteria:**
- All panels show live data
- Dashboards refresh every 30 seconds
- Time range selectable (1h, 6h, 24h, 7d)
- Export to JSON for version control

---

#### FR-5.3: Application Metrics
**Requirement:** Expose Prometheus metrics from application at `/metrics` endpoint.

**Details:**
Required metrics using `prometheus_client` library:

1. **Counter Metrics:**
   - `model_api_requests_total{method, endpoint, status}` - Total requests
   - `model_api_predictions_total{model_name, status}` - Total predictions

2. **Histogram Metrics:**
   - `model_api_request_duration_seconds{method, endpoint}` - Request latency
   - `model_api_inference_duration_seconds{model_name}` - Model inference time

3. **Gauge Metrics:**
   - `model_api_model_loaded{model_name, version}` - Model load status
   - `model_api_active_connections` - Current connections

**Acceptance Criteria:**
- `/metrics` endpoint returns Prometheus format
- Metrics increment correctly on requests
- Labels properly populated
- Histogram buckets cover expected latency range (0.01s to 10s)

---

#### FR-5.4: Alerting
**Requirement:** Configure alerts for critical conditions.

**Details:**
**Required Alerts:**

1. **High Error Rate:**
   ```yaml
   - alert: HighErrorRate
     expr: rate(model_api_requests_total{status=~"5.."}[5m]) > 0.05
     for: 2m
     annotations:
       summary: "High error rate detected"
   ```

2. **Pod Crash Loop:**
   ```yaml
   - alert: PodCrashLooping
     expr: rate(kube_pod_container_status_restarts_total{pod=~"model-api.*"}[15m]) > 0
     for: 5m
   ```

3. **High Memory Usage:**
   ```yaml
   - alert: HighMemoryUsage
     expr: container_memory_usage_bytes{pod=~"model-api.*"} / container_spec_memory_limit_bytes > 0.9
     for: 5m
   ```

**Acceptance Criteria:**
- Alerts trigger correctly when conditions met
- Alert notifications sent (email, Slack, PagerDuty)
- Alerts resolve automatically when condition clears
- Alert history visible in Prometheus UI

---

## Non-Functional Requirements

### NFR-1: Performance

#### NFR-1.1: Throughput
**Requirement:** Support minimum 1000 requests per second cluster-wide.

**Measurement:**
```bash
# Using k6 load testing
k6 run --vus 100 --duration 5m load-test.js
```

**Acceptance Criteria:**
- Sustain 1000 RPS for 5 minutes
- P95 latency < 500ms
- Error rate < 1%
- No pod restarts during test

---

#### NFR-1.2: Latency
**Requirement:** Maintain low latency under load.

**Targets:**
- **P50 (Median):** < 100ms
- **P95:** < 300ms
- **P99:** < 500ms
- **P99.9:** < 1000ms

**Measurement:** Use Grafana histogram queries on `model_api_request_duration_seconds`

---

#### NFR-1.3: Auto-Scaling Responsiveness
**Requirement:** Auto-scaling responds quickly to load changes.

**Targets:**
- **Scale-up:** New pods ready within 2 minutes of crossing threshold
- **Scale-down:** Pods removed after 5-minute stabilization window
- **HPA Decision:** Metrics evaluated every 15 seconds

---

### NFR-2: Reliability

#### NFR-2.1: Availability
**Requirement:** 99.9% uptime (43 minutes downtime per month allowed).

**Calculation:**
```
Uptime % = (Total Time - Downtime) / Total Time × 100
```

**Requirements:**
- Redundant replicas prevent single pod failure
- Health checks detect and recover failures
- Rolling updates maintain availability

---

#### NFR-2.2: Zero-Downtime Deployments
**Requirement:** All deployments must complete without service interruption.

**Verification:**
- Continuous request monitoring during deployment
- Zero 503 Service Unavailable errors
- P99 latency < 500ms maintained

---

#### NFR-2.3: Fault Recovery
**Requirement:** Automatic recovery from pod failures.

**Targets:**
- **Detection Time:** < 30 seconds (via liveness probe)
- **Recovery Time:** < 60 seconds (pod restart + readiness)
- **Total Downtime:** < 90 seconds per pod failure

---

### NFR-3: Scalability

#### NFR-3.1: Horizontal Scaling
**Requirement:** Support scaling from 3 to 10 replicas seamlessly.

**Verification:**
- Test manual scaling: `kubectl scale deployment model-api --replicas=10`
- Test auto-scaling under load
- Verify no performance degradation at max scale

---

#### NFR-3.2: Traffic Spike Handling
**Requirement:** Handle 10x traffic spikes gracefully.

**Scenario:** Sudden increase from 100 RPS to 1000 RPS

**Expected Behavior:**
- HPA scales up within 2 minutes
- Error rate stays < 5% during scale-up
- Latency increases temporarily but recovers
- No pod crashes

---

### NFR-4: Security

#### NFR-4.1: Secrets Management
**Requirement:** All sensitive data stored in Kubernetes Secrets, not ConfigMaps.

**Examples:**
- API keys
- Database passwords
- TLS certificates

**Usage:**
```yaml
env:
  - name: API_KEY
    valueFrom:
      secretKeyRef:
        name: api-secrets
        key: api-key
```

---

#### NFR-4.2: Pod Security Standards
**Requirement:** Apply Pod Security Standards (restricted profile).

**Details:**
- Run as non-root user
- Drop all capabilities
- Read-only root filesystem (where possible)
- No privilege escalation

---

#### NFR-4.3: Network Policies
**Requirement:** Restrict pod-to-pod communication using Network Policies.

**Rules:**
- Only allow ingress from Ingress controller
- Only allow egress to required services
- Deny all other traffic by default

---

## Kubernetes-Specific Requirements

### KR-1: Namespace Isolation
**Requirement:** Deploy all resources in dedicated namespace `ml-serving`.

**Benefits:**
- Resource isolation
- RBAC scoping
- Resource quota enforcement
- Easier cleanup

---

### KR-2: Labels and Annotations
**Requirement:** Use consistent labels for resource organization.

**Standard Labels:**
```yaml
labels:
  app: model-api
  version: v1.0
  component: inference
  managed-by: helm
  part-of: ml-platform
```

**Standard Annotations:**
```yaml
annotations:
  prometheus.io/scrape: "true"
  prometheus.io/port: "5000"
  prometheus.io/path: "/metrics"
```

---

### KR-3: ConfigMap Versioning
**Requirement:** Version ConfigMaps to trigger rolling updates.

**Strategy:** Add hash to ConfigMap name and reference in Deployment
```yaml
configMapRef:
  name: model-config-v2-abc123
```

**Alternative:** Use ConfigMap volume and pod annotations

---

## Acceptance Criteria Summary

### Deployment Criteria
- ✅ 3 pods running and ready
- ✅ Health checks passing
- ✅ Resources properly configured
- ✅ ConfigMap loaded correctly

### Networking Criteria
- ✅ Service accessible internally and externally
- ✅ Ingress routing correctly
- ✅ Load balancing across all pods
- ✅ DNS resolution working

### Scaling Criteria
- ✅ HPA monitoring metrics
- ✅ Scales up under load (tested)
- ✅ Scales down when idle (tested)
- ✅ Maintains availability during scaling

### Updates Criteria
- ✅ Rolling update completes successfully
- ✅ Zero downtime verified
- ✅ Rollback works correctly
- ✅ Update history maintained

### Monitoring Criteria
- ✅ Prometheus scraping metrics
- ✅ Grafana dashboards showing data
- ✅ Alerts configured and tested
- ✅ Application metrics exposed

### Performance Criteria
- ✅ 1000+ RPS sustained
- ✅ P99 latency < 500ms
- ✅ Error rate < 1%
- ✅ Auto-scaling responds < 2 minutes

---

**Document Version:** 1.0
**Last Updated:** October 2025
**Status:** Final
