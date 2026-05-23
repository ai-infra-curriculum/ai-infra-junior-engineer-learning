# Runbook: LogIngestionLag

**Alert:** `LogIngestionLag`
**Severity:** warning
**Pages:** no

## What it means

Logstash's input-to-Elasticsearch lag has exceeded 5 minutes. New logs are still arriving in the cluster but not yet searchable in Kibana.

## How bad is it?

Operators investigating an active incident may see stale logs and make wrong decisions. If lag exceeds the retention window of source pods, logs can be lost outright.

## First checks

1. **Is the Logstash pipeline backed up?**
   ```promql
   logstash_pipeline_events_in_total - logstash_pipeline_events_out_total
   ```
2. **Is Elasticsearch slow on indexing?**
   ```promql
   elasticsearch_indices_indexing_index_time_seconds_total
   ```
3. **Is the input rate spiking?** A burst of logs from a misbehaving app can overrun the pipeline.
4. **Disk pressure on Elasticsearch data nodes?**

## Likely causes

1. **Index settings out of date.** New large index without rollover policy.
2. **Slow query backlog on Elasticsearch.** Heavy Kibana queries blocking indexing threads.
3. **A noisy producer.** Single pod emitting MB/s of logs.
4. **Cluster red/yellow status** from a node restart or shard reallocation.

## Mitigation

- Identify the noisy producer by index size and rate:
  ```
  GET _cat/indices?v&s=store.size:desc
  ```
- Add a Logstash filter or container-level log-level change to cut volume.
- For Elasticsearch pressure: scale out data nodes or close low-priority indices.
- If indexing is permanently slow, increase Logstash workers or batch size.

## When this requires a postmortem

- Logs were lost (not just delayed).
- Caused an incident's MTTR to grow by > 30 minutes.
