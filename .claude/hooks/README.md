# Claude Code Hooks

This directory contains hooks that modify Claude Code behavior.

## protect-deletions.sh

**Purpose**: Intercepts file deletion commands and moves files to a recoverable location instead of permanently deleting them.

**Triggered by**: Commands containing `rm`, `unlink`, or `trash`

**Behavior**:
1. Intercepts the deletion command
2. Moves the file to `{{PLAN_DIR}}/.trash/[uuid]-[original-name]/`
3. Creates metadata.json with recovery information
4. Returns success to prevent actual deletion

**Excluded directories** (files ARE deleted):
- `node_modules/`
- `.git/`
- `__pycache__/`
- `.pytest_cache/`
- `.mypy_cache/`
- `.ruff_cache/`

**Recovery**: Use `.claude/scripts/recover-file.py` to list and recover files.

## Configuration

Add to your `.claude/settings.json`:

```json
{
  "hooks": {
    "PreToolExecution": [
      {
        "matcher": {
          "tool_name": "Bash",
          "command_patterns": ["rm ", "rm$", "unlink ", "trash "]
        },
        "hooks": [
          {
            "type": "command",
            "command": ".claude/hooks/protect-deletions.sh"
          }
        ]
      }
    ]
  }
}
```

## Environment Variables

The hooks use these environment variables when available:

| Variable | Description |
|----------|-------------|
| `CLAUDE_PLAN_DIR` | Base directory for the current plan |
| `CLAUDE_AGENT_ID` | ID of the agent performing the deletion |
| `CLAUDE_TASK_ID` | ID of the current task |

## Metadata Format

Each protected file has a `metadata.json`:

```json
{
    "original_path": "/absolute/path/to/file.py",
    "original_name": "file.py",
    "deleted_at": "2025-01-16T12:00:00Z",
    "deleted_by": "dev-agent-1",
    "task_id": "task-3-1-1",
    "file_type": "file",
    "recovery_id": "abc123-def456",
    "recovery_path": ".claude/surrogate_activities/[plan]/.trash/abc123-file.py/content"
}
```
