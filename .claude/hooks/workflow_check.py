"""Claude Code PreToolUse hook: enforce plan file existence before code changes.

Reads stdin JSON from Claude Code hook system.
Exit 0 = allow, Exit 2 = block (only code that matters for PreToolUse).
"""

import sys
import json
import os
import subprocess
from datetime import date
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
PLANS_DIR = PROJECT_ROOT / "docs" / "plans"

# Directories always allowed (writing plans/docs/config itself must not be blocked)
ALWAYS_ALLOWED_DIRS = {"docs", ".claude"}

# Root-level files always allowed
ALWAYS_ALLOWED_FILES = {
    "Version.md", "CLAUDE.md", "requirements.txt", ".gitignore",
    "run_app.bat", "note_pad_run.bat", "run.bat",
}


def has_plan_for_today() -> bool:
    if not PLANS_DIR.exists():
        return False
    today = date.today().isoformat()
    for f in PLANS_DIR.iterdir():
        if f.is_file() and f.name.startswith(today):
            return True
    return False


def classify_path(filepath: str) -> str:
    """Return 'trivial', 'source', or 'unknown' for a given file path."""
    try:
        rel = Path(filepath).resolve().relative_to(PROJECT_ROOT.resolve())
    except ValueError:
        return "unknown"

    parts = rel.parts

    if len(parts) == 0:
        return "unknown"

    # Always allow: docs/** and .claude/**
    if parts[0] in ALWAYS_ALLOWED_DIRS:
        return "trivial"

    # Always allow root-level known-safe files
    if len(parts) == 1 and parts[0] in ALWAYS_ALLOWED_FILES:
        return "trivial"

    # Allow root-level .bat files and .md files
    if len(parts) == 1:
        name = parts[0]
        if name.endswith(".bat") or name == "CLAUDE.md" or name.startswith("README"):
            return "trivial"

    # Source code under notepad/
    if parts[0] == "notepad":
        subdir = parts[1] if len(parts) > 1 else ""
        if subdir in ("src", "tests") or parts[-1].endswith(".py"):
            return "source"
        # main.py at notepad/ level
        if len(parts) == 2 and parts[1] == "main.py":
            return "source"

    return "unknown"


def get_affected_paths(hook_input: dict) -> list:
    tool_name = hook_input.get("tool_name", "")
    tool_input = hook_input.get("tool_input", {})

    paths = []

    if tool_name in ("Write", "Edit"):
        fp = tool_input.get("file_path", "")
        if fp:
            paths.append(fp)

    elif tool_name == "Bash":
        cmd = tool_input.get("command", "")
        if "git commit" in cmd:
            try:
                result = subprocess.run(
                    ["git", "-C", str(PROJECT_ROOT), "diff", "--cached", "--name-only"],
                    capture_output=True, text=True, timeout=5,
                )
                output = (result.stdout or "").strip()
                if output:
                    paths.extend(output.split("\n"))
                else:
                    result = subprocess.run(
                        ["git", "-C", str(PROJECT_ROOT), "diff", "--name-only"],
                        capture_output=True, text=True, timeout=5,
                    )
                    output = (result.stdout or "").strip()
                    if output:
                        paths.extend(output.split("\n"))
            except Exception:
                pass

    return [str(PROJECT_ROOT / p) if not os.path.isabs(p) else p for p in paths if p]


def main():
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            sys.exit(0)
        hook_input = json.loads(raw)
    except (json.JSONDecodeError, Exception):
        sys.exit(0)

    paths = get_affected_paths(hook_input)

    if not paths:
        sys.exit(0)

    source_paths = [p for p in paths if classify_path(p) == "source"]

    if not source_paths:
        sys.exit(0)

    if has_plan_for_today():
        sys.exit(0)

    today = date.today().isoformat()
    msg = f"""
============================================================
 WORKFLOW CHECK: Action BLOCKED
============================================================
 Source files affected: {', '.join(source_paths[:5])}
 No plan file found in: {PLANS_DIR}
 Today's date: {today}

 Required workflow steps before code changes:
   Step 1: Brainstorming -> Skill("superpowers-skills-brainstorming")
   Step 2: Proposal        -> Skill("openspec-propose")
   Step 3: Human review    -> ask user to confirm
   Step 4: Write plan      -> Skill("superpowers-skills-writing-plans")
            -> saves to docs/plans/{today}-<feature>.md

 Create a plan file first, then retry.
 See CLAUDE.md "MANDATORY WORKFLOW" section for details.
============================================================
"""
    print(msg, file=sys.stderr)
    sys.exit(2)


if __name__ == "__main__":
    main()
