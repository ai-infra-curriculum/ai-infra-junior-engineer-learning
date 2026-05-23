# Velero — Cluster Backup & Restore

Velero backs up Kubernetes API objects and persistent volume snapshots to S3. It is the disaster-recovery counterpart to `docs/DISASTER_RECOVERY.md` and the runtime tool that makes that document executable rather than aspirational.

## What this protects against

- **Accidental namespace deletion.** Restore a namespace from yesterday's backup.
- **Cluster loss.** Restore an entire cluster's workloads into a fresh cluster (the prod-to-staging drill).
- **Data corruption.** Restore PVCs from snapshots taken before the corruption.
- **Region failure.** Replicate backups cross-region; spin up a new cluster in the secondary region.

It does **not** protect against:

- **Backups themselves being deleted.** S3 versioning + object lock are required for that.
- **Bugs in the data.** Velero captures whatever state existed; if the data was broken at backup time, it's broken in the restore too.

## Install

```bash
helm repo add vmware-tanzu https://vmware-tanzu.github.io/helm-charts
helm upgrade --install velero vmware-tanzu/velero \
  -n velero --create-namespace \
  -f velero/values.yaml
```

Prerequisites (provisioned by Terraform in `terraform/modules/iam` and an S3 bucket module not shown here):

- S3 bucket with versioning + KMS encryption.
- IRSA role with `s3:GetObject`, `s3:PutObject`, `s3:DeleteObject` on the bucket and `kms:Decrypt`/`Encrypt` on the KMS key.
- EBS CSI driver (snapshot support).

## Daily operations

```bash
# Trigger an ad-hoc backup of one namespace
velero backup create model-api-now --include-namespaces model-api

# List recent backups
velero backup get

# Inspect what's inside
velero backup describe model-api-now --details
```

## Restore

```bash
# Restore an entire namespace from the most recent matching backup
velero restore create model-api-restore \
  --from-backup cluster-daily-2026-05-22 \
  --include-namespaces model-api

# Watch progress
velero restore describe model-api-restore --details
```

## Validate quarterly

A backup you've never restored is a hope, not a recovery plan. Run a documented restore drill every quarter:

1. Take a backup of prod into staging-prefixed location.
2. Restore that backup into a clean staging cluster.
3. Run the smoke test from `loadtest/` against the restored stack.
4. Measure: time-to-restore, data freshness, anything that didn't come back automatically (DNS, external secrets, etc.).
5. Update `docs/DISASTER_RECOVERY.md` with what you learned.

## Schedules

The two default schedules in `values.yaml`:

| Name | Frequency | TTL | Scope |
|---|---|---|---|
| `cluster-daily` | 01:00 UTC daily | 30 days | All namespaces except kube-system/public/velero |
| `critical-hourly` | Hourly on the hour | 7 days | `model-api`, `mlflow`, `airflow` only |

Adjust frequency and TTL to your RPO. Hourly is overkill if you can rebuild from CI; daily is too coarse if you can't.
