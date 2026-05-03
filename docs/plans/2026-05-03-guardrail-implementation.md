# Guardrail Implementation Plan

> 2026-05-03 | Enforce CLAUDE.md workflow with PreToolUse hooks

## Goal

Block writes to `notepad/src/**/*.py` and `git commit` commands when no plan file exists for today at `docs/plans/YYYY-MM-DD-<feature>.md`.

## Implementation

1. `.claude/hooks/workflow_check.py` — Python script: stdin JSON → classify paths → check plan → exit 0/2
2. `CLAUDE.md` — restructured: workflow moved to top with MANDATORY box + GATE markers + Quick Compliance Check
3. `.claude/settings.local.json` — added 2 PreToolUse hooks (Write|Edit guard + git commit guard)

## Test Results

| Test | Result |
|------|--------|
| No plan + source write | BLOCK (exit 2) |
| No plan + docs write | ALLOW (exit 0) |
| No plan + Version.md write | ALLOW (exit 0) |
| No plan + .claude write | ALLOW (exit 0) |
| Plan exists + source write | ALLOW (exit 0) |
