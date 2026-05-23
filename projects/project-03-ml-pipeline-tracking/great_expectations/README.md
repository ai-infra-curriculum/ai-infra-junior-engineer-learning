# Great Expectations Configuration — Project 03

Great Expectations validates the training dataset *before* model training runs. A failed checkpoint causes the DVC `validate` stage to exit non-zero, which blocks `train` from running on bad data.

## What's here

- `great_expectations.yml` — project-level config (data sources, stores, sites)
- `expectations/training_data_suite.json` — the expectation suite for training data
- `checkpoints/training_data_checkpoint.yml` — the runnable checkpoint that pairs the suite with a dataset

## Running

From the project root:

```bash
# Run validation
great_expectations checkpoint run training_data_checkpoint

# View results in the Data Docs
great_expectations docs build
open great_expectations/uncommitted/data_docs/local_site/index.html
```

The Airflow DAG `dags/ml_pipeline_dag.py` invokes the same checkpoint between the `preprocessing` and `training` tasks, so production runs and local runs use identical validation logic.

## When to update the suite

- **Schema changes**: when a feature is added, removed, or renamed.
- **Range changes**: when expected min/max/mean change due to genuine business shifts (not data quality bugs).
- **Drift baselines**: refresh the KL-divergence partition_object monthly from the latest known-good production training set.

Every change to the suite requires a PR; mismatched expectations are a common cause of misleading "data is fine" results.

## Failure modes the suite catches

| Expectation | Catches |
|---|---|
| `expect_table_row_count_to_be_between` | Empty extract; runaway join |
| `expect_table_columns_to_match_set` | Schema drift, accidental column add/remove |
| `expect_column_values_to_be_unique` (transaction_id) | Duplicate rows from broken upstream |
| `expect_column_values_to_be_in_set` (label ∈ {0,1}) | Mis-mapped labels |
| `expect_column_mean_to_be_between` (label) | Class-balance collapse (all 0 or all 1) |
| `expect_column_kl_divergence_to_be_less_than` (amount) | Distribution drift indicating upstream pipeline change |
