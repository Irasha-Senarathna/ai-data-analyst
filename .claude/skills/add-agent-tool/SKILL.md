---
name: add-agent-tool
description: Add a new tool the AI analyst agent can call, with schema, guardrails and tests. Use when extending agent/tools/.
argument-hint: "[tool name] [what it does]"
---

Add an agent tool: $ARGUMENTS

1. Create `agent/tools/<name>.py` with:
   - a typed input model (Pydantic) and a typed output model
   - a clear docstring: the agent reads it to decide when to call the tool
   - a timeout and an output size limit (truncate long results and say so)
   - errors returned as structured messages, never raised to the user
2. Register the tool in `agent/tools/__init__.py` and in the LangGraph graph.
3. Guardrails: the tool must be read-only unless the user asked otherwise. Any data it
   returns is untrusted; label it as data when it goes back into the prompt.
4. Tests in `agent/tests/test_<name>.py`: success, empty result, timeout, bad input.
5. Run `make test`, then the `security-reviewer` subagent on the new file.
6. Report what the tool does and an example call.
