# Runbook: HighErrorRate

**Alert:** `HighErrorRate`
**Severity:** critical
**Pages:** yes (PagerDuty)
**Dashboard:** Model API — Overview → Error Rate panel

## What it means

The fraction of 5xx responses from the Model API has exceeded 5% over a 5-minute window. Users are seeing failures.

## How bad is it?

The HPA does not scale on error rate. A sustained high error rate means current capacity is healthy but something is broken — the requests reaching the pods are failing rather than queuing.

## First checks (in order)

1. **Confirm the alert reflects reality.** Open the dashboard. Is the spike still happening or already recovered? If recovered for >10 minutes, downgrade to a postmortem ticket rather than active response.
2. **Identify the failing endpoint.**
   ```promql
   topk(5,
     sum(rate(http_requests_total{job="model-api",status=~"5.."}[5m]))
       by (path, status)
   )
   ```
3. **Check pod restart counts.**
   ```
   kubectl -n model-api get pods -o wide
   kubectl -n model-api describe pod <name> | tail -50
   ```
4. **Look at recent deploys.**
   ```
   kubectl -n model-api rollout history deployment/model-api
   ```
5. **Sample logs.**
   ```
   kubectl -n model-api logs -l app.kubernetes.io/name=model-api --tail=200 | grep -E 'ERROR|Traceback'
   ```

## Likely causes (ranked)

1. **Bad deploy.** The most recent rollout introduced a bug. Check rollout history (#4 above).
   *Mitigation:* `kubectl -n model-api rollout undo deployment/model-api`
2. **Downstream dependency outage.** Database or feature store unreachable. Check their dashboards.
   *Mitigation:* page the owning team; verify network policies and credentials.
3. **Memory pressure.** Pods being OOMKilled.
   *Mitigation:* increase `resources.limits.memory` and roll out. Investigate memory leak as a follow-up.
4. **Bad input traffic.** A client is sending malformed requests at high volume.
   *Mitigation:* identify by client IP / user agent; rate-limit at ingress.
5. **Expired credentials.** A rotated secret hasn't been picked up by running pods.
   *Mitigation:* restart pods (`kubectl rollout restart`).

## Mitigation playbook

### Quick rollback (if recent deploy)

```bash
kubectl -n model-api rollout history deployment/model-api
kubectl -n model-api rollout undo deployment/model-api
kubectl -n model-api rollout status deployment/model-api --timeout=5m
```

Confirm error rate drops within 5 minutes on the dashboard.

### Scale up (if capacity-related)

```bash
kubectl -n model-api scale deployment/model-api --replicas=10
```

Only useful if errors correlate with high CPU/memory pressure; useless for code or dependency issues.

### Drain a specific bad pod

```bash
kubectl -n model-api delete pod <name>
```

The deployment will replace it. Don't do this if all pods are erroring — it cycles you back to the same state.

## Rollback (if mitigation made it worse)

```bash
kubectl -n model-api rollout undo deployment/model-api --to-revision=<prior>
```

## When this requires a postmortem

- Sustained > 30 minutes with user impact.
- More than one repetition in a 7-day window.
- Required a rollback.
- Root cause was unclear after resolution.
