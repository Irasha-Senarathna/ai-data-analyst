---
name: add-eval-question
description: Add benchmark questions with verified correct answers to the eval set. Use when growing or fixing evals/questions.yaml.
argument-hint: "[question in plain English, or a topic to generate several]"
---

Add eval question(s): $ARGUMENTS

1. Write the question the way a business user would ask it.
2. Write the correct SQL yourself against the marts in `dbt/models/marts/`.
   Use metric definitions from `semantic/metrics.yml`.
3. Run the SQL on DuckDB and save the exact result (rounded to 2 decimals).
4. Append to `evals/questions.yaml`:
   ```yaml
   - id: q###            # next free number
     question: "..."
     difficulty: easy | medium | hard   # hard = multi-step or "why" questions
     tags: [revenue, time-filter, join]
     gold_sql: |
       SELECT ...
     expected_result: [...]
   ```
5. Check the question is not a duplicate and the difficulty mix stays roughly
   40% easy, 40% medium, 20% hard.
6. Run `make eval -- --ids <new ids>` and report how the agent did on them.
