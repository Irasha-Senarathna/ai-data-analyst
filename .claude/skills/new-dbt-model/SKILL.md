---
name: new-dbt-model
description: Create a new dbt model with documentation and tests in this project's style. Use when adding a staging, intermediate or mart model.
argument-hint: "[model name] [short purpose]"
---

Create a dbt model: $ARGUMENTS

1. Pick the layer by name prefix: `stg_` (clean one source), `int_` (join/reshape),
   `fct_` / `dim_` (marts the agent queries).
2. Write the SQL in `dbt/models/<layer>/<name>.sql` using CTEs:
   `source` → `renamed` → `final`. Explicit column lists, no `SELECT *` in marts.
3. Add the model to the layer's `schema.yml` with:
   - a one-line description of the model and its grain ("one row per order")
   - a description for every column (the agent reads these to write SQL)
   - tests: `unique` + `not_null` on the primary key, `relationships` on foreign keys,
     `accepted_values` on status-like columns
4. If it is a mart, add or update matching metrics in `semantic/metrics.yml`.
5. Run `dbt build --select <name>` and fix any failures.
6. Report the grain, row count, and tests added.
