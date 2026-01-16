# Recycle Bin Hook Manager

Manage the file deletion protection hook that moves deleted files to `.trash/` instead of permanently deleting them.

## Usage

```
/recycle-bin install                    # Enable deletion protection
/recycle-bin uninstall                  # Disable deletion protection
/recycle-bin status                     # Check current status
/recycle-bin list                       # List recoverable files
/recycle-bin recover <id>               # Recover a file
/recycle-bin recover <id> --to <path>   # Recover to different location
/recycle-bin purge <id>                 # Permanently delete from trash
```

## Arguments

- `$ARGUMENTS`: The action and any additional arguments

## Instructions

Run the management script with the provided arguments:

```bash
python3 .claude/scripts/manage-recycle-bin.py $ARGUMENTS
```

Display the output to the user.

### Action-Specific Notes

- **install/uninstall**: Emphasize that the user **must restart Claude Code** for the change to take effect.
- **list**: Shows all files in `.trash/` that can be recovered.
- **recover**: Restores a file. Use `--to <path>` for a different location, `--force` to overwrite.
- **purge**: Permanently deletes a file from trash (cannot be undone).

## Security Guarantees

The hook **NEVER** allows deletion of:

1. **Files in `.trash/` directories** - Prevents accidental loss of recoverable files
2. **Files outside the project directory** - Uses `CLAUDE_PROJECT_DIR` to prevent system damage

If a file cannot be safely moved to trash, deletion is **BLOCKED**.

## What the Hook Does

When installed, the hook intercepts file deletion commands (`rm`, `unlink`, `trash`) and:

1. Verifies the file is inside the project directory
2. Parses the bash command to identify files being deleted
3. Moves each file to `.claude/surrogate_activities/[plan]/.trash/[uuid]-[filename]/`
4. Creates `metadata.json` with recovery information
5. Blocks the original deletion command with feedback to Claude

## Dependencies

The hook requires `bashlex` for bash command parsing:

```bash
pip install bashlex
```

The install command will check for this dependency.

## Configuration

The hook is configured in `.claude/settings.json`:

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

## Documentation

- [Hook README](.claude/hooks/README.md) - Full hook documentation
