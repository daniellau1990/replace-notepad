"""Claude Code PreToolUse hook: enforce Version.md consistency on git commit.

Reads stdin JSON from Claude Code hook system.
Exit 0 = allow, Exit 2 = block.

Only checks git commit — Write/Edit always allowed.
"""

import sys
import json
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def get_app_version() -> str:
    """Extract APP_VERSION from notepad/src/app.py."""
    app_py = PROJECT_ROOT / "notepad" / "src" / "app.py"
    if not app_py.exists():
        return ""
    try:
        content = app_py.read_text(encoding="utf-8")
        m = re.search(r'APP_VERSION\s*=\s*"([^"]+)"', content)
        return m.group(1) if m else ""
    except Exception:
        return ""


def check_version_md() -> bool:
    """Return True if notepad/Version.md contains current APP_VERSION."""
    current = get_app_version()
    if not current:
        return True  # can't check, allow
    version_md = PROJECT_ROOT / "notepad" / "Version.md"
    if not version_md.exists():
        return False
    try:
        content = version_md.read_text(encoding="utf-8")
        return current in content
    except Exception:
        return True


def main():
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            sys.exit(0)
        hook_input = json.loads(raw)
    except (json.JSONDecodeError, Exception):
        sys.exit(0)

    tool_name = hook_input.get("tool_name", "")
    tool_input = hook_input.get("tool_input", {})
    cmd = tool_input.get("command", "")

    # Only check git commit — Write/Edit always pass
    if tool_name != "Bash" or "git commit" not in cmd:
        sys.exit(0)

    if not check_version_md():
        current = get_app_version()
        msg = f"""
============================================================
 WORKFLOW CHECK: Action BLOCKED (Version.md out of sync)
============================================================
 Current APP_VERSION: {current}
 Version.md does NOT contain this version.

 Before committing, update notepad/Version.md:
   - Add a new ## {current} section with change summary
   - Keep the format consistent with existing entries
   - The version string "{current}" must appear in the file

 See CLAUDE.md "HOOK 保护" section.
============================================================
"""
        print(msg, file=sys.stderr)
        sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    main()
