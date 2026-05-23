# Load Testing — Project 02

This directory contains the load-test plan for the Model API. The goal of each test is to surface a specific characteristic of the deployment, not just to "send lots of requests."

## Test plans

| Plan | Users | Duration | Goal |
|---|---|---|---|
| **Smoke** | 5 | 1 min | Confirm the deployment responds and basic endpoints work |
| **Ramp** | 0 → 200 over 3 min, hold 5 min | 8 min | Find the comfortable steady-state RPS and identify when latency degrades |
| **Soak** | 100 | 60 min | Catch memory leaks, GC pauses, slow log accumulation |
| **Spike** | 50 → 500 in 30s, hold 2 min | 3 min | Validate HPA reacts and there's no cascading failure |

## Running

### Smoke

```bash
locust -f loadtest/locustfile.py \
  --host https://model-api.example.com \
  --headless --users 5 --spawn-rate 5 --run-time 1m \
  --csv loadtest/results/smoke
```

### Ramp

```bash
locust -f loadtest/locustfile.py \
  --host https://model-api.example.com \
  --headless --users 200 --spawn-rate 1 --run-time 8m \
  --csv loadtest/results/ramp
```

### Soak

```bash
locust -f loadtest/locustfile.py \
  --host https://model-api.example.com \
  --headless --users 100 --spawn-rate 10 --run-time 60m \
  --csv loadtest/results/soak
```

### Spike

```bash
locust -f loadtest/locustfile.py \
  --host https://model-api.example.com \
  --headless --users 500 --spawn-rate 15 --run-time 3m \
  --csv loadtest/results/spike
```

## Acceptance criteria

A passing load test for this project should show:

- **Smoke:** 100% success, p95 < 500ms.
- **Ramp:** sustained 100 RPS with p95 < 800ms, no 5xx errors.
- **Soak:** memory growth < 10% over 60 min, no error rate drift.
- **Spike:** HPA scales replicas up within 60s, no requests dropped after the first 30s, p99 < 2s during the spike.

## Recording results

Each run writes CSV summaries under `loadtest/results/<run-name>_*.csv`:

- `*_stats.csv` — per-endpoint request count, failure count, latency percentiles
- `*_failures.csv` — error breakdown
- `*_stats_history.csv` — time-series for plotting

Plot the time series with the included notebook (`loadtest/analyze.ipynb`, optional) or with any plotting tool. Attach the screenshots to your project submission.

## Tunable env vars

| Variable | Default | Description |
|---|---|---|
| `FEATURE_COUNT` | `10` | Number of features per `/predict` request |
| `MODEL_VERSIONS` | `latest` | Comma-separated model versions to round-robin |

## Note on test environment

Always run load tests against a dedicated test environment with the same shape as production (same instance types, same HPA limits, same model). Tests against shared environments are misleading and risk impacting other teams.
