---
name: milestone
description: Build one project milestone end to end (plan, tests first, implement, verify, review, summarize). Use when the user says "start milestone N".
disable-model-invocation: true
argument-hint: "[milestone number or name]"
---

Build milestone: $ARGUMENTS

Follow these steps in order. Do not skip any.

1. **Understand.** Read `CLAUDE.md` and `docs/plan.md`. Find this milestone's goal and
   acceptance criteria. If anything is unclear, ask the user before writing code.
2. **Plan.** Write a short checklist of the files you will create or change. Show it.
3. **Tests first.** Write tests that describe the acceptance criteria. Run them; they should fail.
4. **Implement.** Write the smallest code that makes the tests pass.
5. **Verify.** Run `make lint` and `make test`. Fix every failure. If the milestone
   touches the agent, also run `make eval` and report the score.
6. **Review.** Use the `sql-reviewer` subagent if SQL or dbt changed, and the
   `security-reviewer` subagent if agent/, api/ or auth changed. Fix Critical/High findings.
7. **Docs.** Update `docs/` and the milestone status in `docs/plan.md`.
8. **Summary.** Tell the user: what was built, how to try it (exact commands),
   test and eval results, and a suggested git commit message.
