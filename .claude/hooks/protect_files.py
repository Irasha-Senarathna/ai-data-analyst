"""Hook: stop Claude from editing secret or generated files.

Claude Code sends the tool call as JSON on stdin.
Exit code 2 = block the edit and tell Claude why (message on stderr).
Exit code 0 = allow.
"""

import json
import os
import sys

# Exact file names that must never be edited by Claude.
PROTECTED_NAMES = {
    ".env",              # real secrets (editing .env.example is fine)
    "warehouse.duckdb",  # the database file itself
    "package-lock.json",
    "uv.lock",
    "poetry.lock",
}
# Folders Claude must never write into.
PROTECTED_DIRS = ("/.git/",)

data = json.load(sys.stdin)
path = data.get("tool_input", {}).get("file_path", "")
name = os.path.basename(path)

if name in PROTECTED_NAMES or any(d in path for d in PROTECTED_DIRS):
    print(
        f"Blocked: '{path}' is a protected file. "
        "Edit .env.example instead, or ask the user to change it.",
        file=sys.stderr,
    )
    sys.exit(2)

sys.exit(0)
