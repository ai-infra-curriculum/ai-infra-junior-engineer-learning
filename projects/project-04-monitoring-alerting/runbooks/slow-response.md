# Runbook: SlowResponse

**Alert:** `SlowResponse`
**Severity:** warning
**Pages:** no (Slack `#alerts-warnings`)

## What it means

p95 request latency on the Model API has exceeded the SLO (typically 800ms) for 10 minutes.

## How bad is it?

Users perceive slowness. No outright failures, but conversion / engagement metrics likely impacted.

## First checks

1. **Confirm scope.** Is p95 elevated for all endpoints or just one?
   ```promql
   histogram_quantile(0.95,
     sum(rate(http_request_duration_seconds_bucket{job="model-api"}[5m]))
       by (le, path))
   ```
2. **Check inference latency separately.** If inference is fine but HTTP latency is high, the slowness is in middleware or networking. If inference is slow, the model itself is the bottleneck.
3. **Check CPU saturation.** Pods near their CPU limit can't scale up beyond the limit even if HPA hasn't reacted yet.
4. **Check HPA state.** Is it at max replicas?
5. **Check recent deploy.** A new model version might be slower than the previous.

## Likely causes

1. **HPA lag during traffic ramp.** Real fix: lower HPA scale-up stabilization window.
2. **Slower model version.** Compare inference duration histogram between versions.
3. **Cold cache.** After a deploy, hot caches are empty. Latency returns to normal in ~5–10 minutes.
4. **Slow downstream call.** Database or feature store latency.
5. **GC / memory pressure.** Pods near memory limit GC frequently.

## Mitigation

- Manually scale up while HPA catches up: `kubectl -n model-api scale deployment/model-api --replicas=N`.
- Roll back model version if a new deploy correlates with the regression.
- If a downstream is slow, escalate to that team — do not "fix" upstream by adding more replicas.

## When this requires a postmortem

- Persistent > 2 hours with no clear cause.
- Recurring weekly at the same time (capacity planning gap).
