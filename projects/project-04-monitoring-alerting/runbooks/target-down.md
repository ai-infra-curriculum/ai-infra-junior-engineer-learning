# Runbook: TargetDown

**Alert:** `TargetDown`
**Severity:** critical
**Pages:** yes

## What it means

Prometheus has been unable to scrape a configured target for 5 minutes. We have no metrics from that target — alerts that depend on metrics from this target are silenced.

## How bad is it?

**Severity depends on the target.** A down API pod is user-impacting. A down Prometheus exporter is monitoring-impacting only.

## First checks

1. **Identify the missing target.** The alert label `instance` and `job` tell you what's missing.
2. **Is the pod actually running?**
   ```
   kubectl get pods -A -o wide | grep <instance>
   ```
3. **Is the network path working?**
   ```
   kubectl run -it --rm debug --image=curlimages/curl -- \
     curl -sf http://<instance>/metrics
   ```
4. **Is Prometheus healthy?** If multiple `TargetDown` alerts fire at once, Prometheus itself or its network may be the problem.

## Likely causes

1. **Pod restart loop.** Crashing before exporter responds.
2. **Network policy blocking scrape.** Recent NetworkPolicy change.
3. **Service mesh / sidecar issue.** mTLS configuration mismatch.
4. **Prometheus scrape config dropped the target.** Recent ConfigMap edit.
5. **DNS resolution failure** in the Prometheus pod.

## Mitigation

- Restart the affected pod: `kubectl rollout restart deployment/<name> -n <ns>`.
- Verify Prometheus targets page: `kubectl port-forward -n monitoring svc/prometheus 9090:9090` → http://localhost:9090/targets.
- If a NetworkPolicy is the cause, temporarily add the Prometheus namespace to its `from` selector while the owning team investigates.

## When this requires a postmortem

- Caused a missed page on a real incident.
- Required > 1 hour to diagnose.
