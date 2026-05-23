# model-api Helm Chart

Helm chart for the ML model serving API in Project 02.

This chart packages the deployment manifests from `../kubernetes/` into a reusable, parameterized chart suitable for promoting the same artifact across dev, staging, and production environments.

## Quick start

```bash
# Install into the current namespace
helm install model-api ./helm/model-api

# Override values per environment
helm upgrade --install model-api ./helm/model-api -f values-prod.yaml

# Inspect rendered manifests before applying
helm template model-api ./helm/model-api
```

## Values

See `values.yaml` for the full set of configurable options. The most commonly overridden ones:

| Key | Default | Purpose |
|---|---|---|
| `image.repository` | `model-api` | Container image repository |
| `image.tag` | `1.0.0` | Image tag (set per deploy) |
| `replicaCount` | `2` | Static replica count when autoscaling disabled |
| `autoscaling.enabled` | `true` | Toggle HPA |
| `autoscaling.minReplicas` / `maxReplicas` | `2` / `10` | HPA bounds |
| `ingress.hosts[0].host` | `model-api.example.com` | Hostname for ingress |
| `resources` | 200m/512Mi req | Container resources |
| `modelStorage.type` | `pvc` | `pvc`, `s3`, `gcs`, or `initContainer` |
| `env` | `LOG_LEVEL`, `MODEL_PATH`, `WORKERS` | Container env vars |
| `serviceMonitor.enabled` | `true` | Create Prometheus ServiceMonitor |

## Promotion across environments

Maintain per-environment values files:

```
helm/
  model-api/
    values.yaml           # defaults
    values-dev.yaml
    values-staging.yaml
    values-prod.yaml
```

```bash
helm upgrade --install model-api ./helm/model-api \
  -n model-api-prod --create-namespace \
  -f ./helm/model-api/values-prod.yaml \
  --set image.tag=$GIT_SHA \
  --atomic --timeout 5m
```

`--atomic` rolls back on failure; `--timeout` bounds rollout waits.

## Migration from the raw manifests

The raw manifests in `../kubernetes/` and this chart produce equivalent resources for the default values. Once the chart is in use, the raw manifests serve as a reference/teaching aid only — operations go through Helm.

## Troubleshooting

```bash
# What will be applied?
helm template model-api ./helm/model-api -f values-prod.yaml

# Diff against the live release
helm diff upgrade model-api ./helm/model-api -f values-prod.yaml

# Rollback
helm rollback model-api
```
