# Claude Code Hooks

This directory contains hooks that modify Claude Code behavior.

## recycle-bin.py

**Purpose**: Intercepts file deletion commands and either moves files to a recoverable location or blocks the deletion
entirely.

**Triggered by**: Commands containing `rm`, `unlink`, or `trash`

**Dependencies**:

```bash
pip install bashlex
```

## Security Guarantees

The hook **NEVER** allows deletion of:

1. **Files in `.trash/` directories** - Protected to prevent accidental loss of recoverable files
2. **Files outside the project directory** - Uses `CLAUDE_PROJECT_DIR` environment variable

If a file cannot be safely moved to trash, the deletion is **BLOCKED** (not allowed to proceed).

## Behavior

| Path Type                    | Action                        | Exit Code      |
|------------------------------|-------------------------------|----------------|
| Inside project, normal file  | Move to `.trash/`, block `rm` | 0 + deny JSON  |
| Inside project, excluded dir | Allow `rm` to proceed         | 0 + allow JSON |
| Inside `.trash/`             | **BLOCK**                     | 0 + deny JSON  |
| Outside project              | **BLOCK**                     | 0 + deny JSON  |
| Cannot resolve path          | **BLOCK**                     | 0 + deny JSON  |
| Cannot parse command         | **BLOCK**                     | Exit 2         |

## Hook Communication

The hook uses Claude Code's structured JSON response format:

```python
# Block with feedback to Claude
{
    "hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": "Explanation shown to Claude"
    }
}

# Allow command to proceed
{
    "hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "allow"
    }
}
```

Exit code 2 blocks the command and sends `stderr` directly to Claude.

## Environment Variables

| Variable             | Description                              |
|----------------------|------------------------------------------|
| `CLAUDE_PROJECT_DIR` | Project root - files outside are blocked |
| `CLAUDE_PLAN_DIR`    | Base for `.trash/` directory             |
| `CLAUDE_AGENT_ID`    | Recorded in deletion metadata            |
| `CLAUDE_TASK_ID`     | Recorded in deletion metadata            |

## Excluded Directories

Deletions in these directories proceed normally (no protection):

- `node_modules/`, `.git/`, `__pycache__/`
- `.pytest_cache/`, `.mypy_cache/`, `.ruff_cache/`
- `dist/`, `build/`, `.next/`, `.nuxt/`
- `coverage/`, `.tox/`, `.venv/`, `venv/`, `.env/`

## Recovery

Use the `/recycle-bin` command to manage protected files:

```bash
/recycle-bin list                 # List recoverable files
/recycle-bin recover <id>         # Recover to original location
/recycle-bin recover <id> --to <path>  # Recover elsewhere
/recycle-bin purge <id>           # Permanently delete
```

## Metadata Format

Each protected file has a `metadata.json`:

```json
{
  "original_path": "/absolute/path/to/file.py",
  "original_name": "file.py",
  "deleted_at": "2026-01-16T12:00:00+00:00",
  "deleted_by": "dev-agent-1",
  "task_id": "task-3-1-1",
  "file_type": "file",
  "recovery_id": "abc123de",
  "recovery_path": ".claude/surrogate_activities/[plan]/.trash/abc123de-file.py/content"
}
```

## Configuration

Add to `.claude/settings.json`:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": {
          "tool_name": "Bash",
          "command_patterns": [
            "rm ",
            "rm$",
            "unlink ",
            "trash "
          ]
        },
        "hooks": [
          {
            "type": "command",
            "command": ".claude/hooks/recycle-bin.py"
          }
        ]
      }
    ]
  }
}
```

## Testing

Dry run (analyze without protecting):

```bash
echo '{"tool_input": {"command": "rm -rf src/old"}}' | .claude/hooks/recycle-bin.py
```
