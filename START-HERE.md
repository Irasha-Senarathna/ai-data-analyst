# Start Here — AI Data Analyst starter kit

This kit sets up Claude Code so it builds your project the right way.
Read this page once, then follow `PROMPTS.md`.

---

## What is in this kit (in simple words)

| File | What it is | Why you need it |
|---|---|---|
| `CLAUDE.md` | Project memory | Claude reads it at the start of every session: what the project is, the stack, the rules. You never have to repeat yourself. |
| `PROMPTS.md` | Your step-by-step prompts | One prompt per milestone. Copy, paste, run, commit. |
| `.claude/settings.json` | Hooks config | Turns on the two automatic hooks below. |
| `.claude/hooks/protect_files.py` | Hook: protect files | Blocks Claude from editing `.env`, the database file, or lock files. |
| `.claude/hooks/format_file.py` | Hook: auto-format | Formats every file right after Claude edits it (ruff / prettier). |
| `.claude/agents/sql-reviewer.md` | Subagent | A second "expert" that reviews your SQL and dbt models for mistakes. |
| `.claude/agents/security-reviewer.md` | Subagent | Reviews code for security problems. Read-only, cannot change code. |
| `.claude/agents/test-writer.md` | Subagent | Writes and runs tests. Only allowed to edit test files. |
| `.claude/skills/milestone/` | Skill → `/milestone` | Runs one milestone the right way: plan → tests → code → verify → review → summary. |
| `.claude/skills/new-dbt-model/` | Skill → `/new-dbt-model` | Creates a dbt model with docs and tests. |
| `.claude/skills/add-eval-question/` | Skill → `/add-eval-question` | Adds benchmark questions with correct answers. |
| `.claude/skills/add-agent-tool/` | Skill → `/add-agent-tool` | Adds a new tool to the AI agent with safety checks and tests. |

**Hook** = something that runs automatically every time (like a rule Claude can't forget).
**Subagent** = a helper with its own job and its own limited permissions.
**Skill** = a saved recipe you start with a slash command, e.g. `/milestone 3`.

---

## One-time setup (about 30 minutes)

1. **Install the tools**
   - Git, Docker Desktop, Python 3.12, Node.js 20+
   - `pip install ruff` (used by the format hook)
   - Ollama → then run `ollama pull qwen2.5-coder:7b` (the free local AI model, ~5 GB)
   - Claude Code

2. **Create your project folder and copy this kit into it**
   ```bash
   mkdir ai-data-analyst && cd ai-data-analyst
   git init
   # copy everything from this kit here, including the hidden .claude folder
   ```
   On Mac/Linux, hidden folders start with a dot. Use `ls -a` to check `.claude/` is there.

3. **Start Claude Code**
   ```bash
   claude
   ```
   - Type `/hooks` → you should see the two hooks.
   - Type `/agents` → you should see the three subagents.
   - Type `/` → you should see `/milestone`, `/new-dbt-model`, etc.

4. **First commit**
   ```bash
   git add -A && git commit -m "chore: add Claude Code starter kit"
   ```

---

## How to work, every day

1. Open `PROMPTS.md` and copy the **next** prompt.
2. Paste it into Claude Code. Answer any questions it asks.
3. When it finishes, **check it yourself**: run the commands it gives you, open the app.
4. `git commit` with the message it suggests.
5. Type `/clear` and go to the next prompt.

**Golden rules**
- One milestone at a time. Never paste all prompts at once.
- If Claude goes the wrong way, press **Esc** to stop it, or use `/rewind` to undo.
- Read what Claude writes. You must be able to explain every part in an interview.
- Prompt 0 is the most important. Spend time answering its questions well.

---

## Timeline (rough)

| Week | Milestones |
|---|---|
| 1 | 0–2: plan, scaffold, data pipeline |
| 2 | 3–4: marts, data quality, semantic layer |
| 3–4 | 5–6: the AI agent, self-correction, "why" questions |
| 5 | 7: evals + improving accuracy |
| 6 | 8: web app |
| 7 | 9: security + observability |
| 8 | 10: CI/CD, deploy, README, demo video |

---

## Cost

- Claude Code: needs a paid Claude plan.
- Everything inside the project: **$0** (open-source tools, public data, local AI model via Ollama).
- Hardware: 16 GB RAM is comfortable. With 8 GB, use a smaller model such as `qwen2.5-coder:3b`.
