# Recycle Bin - File Recovery Skill

Recover accidentally deleted files from the recycle bin. Use this skill proactively when you detect that a file has been
deleted and may need to be recovered.

## When to Use

Use this skill when:

- A file deletion was accidental or premature
- You need to recover a file that was moved to trash
- You want to list what files are available for recovery
- The user asks about recovering deleted files

## Usage

```
/recycle-bin list                       # List all recoverable files
/recycle-bin recover <id>               # Recover to original location
/recycle-bin recover <id> --to <path>   # Recover to different location
/recycle-bin recover <id> --force       # Overwrite if destination exists
/recycle-bin purge <id>                 # Permanently delete from trash
/recycle-bin status                     # Check if hook is installed
```

## Instructions

### Listing Recoverable Files

To see what files can be recovered:

```bash
python3 .claude/scripts/manage-recycle-bin.py list
```

This shows:

- Recovery ID (use this for recover/purge commands)
- Original file name
- When it was deleted
- File type
- Original path

### Recovering a File

To recover a file to its original location:

```bash
python3 .claude/scripts/manage-recycle-bin.py recover <recovery_id>
```

To recover to a different location:

```bash
python3 .claude/scripts/manage-recycle-bin.py recover <recovery_id> --to /path/to/new/location
```

To overwrite an existing file:

```bash
python3 .claude/scripts/manage-recycle-bin.py recover <recovery_id> --force
```

### Proactive Recovery

When you notice:

1. A file was deleted that shouldn't have been
2. A build/test failure references a missing file that was recently deleted
3. The user mentions a file they need that was deleted

You should:

1. List recoverable files to find the file
2. Verify it's the right file (check original path and deletion time)
3. Recover it to the appropriate location
4. Inform the user what was recovered

### Checking Hook Status

To verify the recycle bin hook is active:

```bash
python3 .claude/scripts/manage-recycle-bin.py status
```

If not installed, suggest: `/recycle-bin install`

## Security Guarantees

The hook **NEVER** allows deletion of:

1. **Files in `.trash/` directories** - Prevents loss of recoverable files
2. **Files outside `CLAUDE_PROJECT_DIR`** - Prevents system damage

If a file cannot be safely moved to trash, deletion is **BLOCKED** (not allowed).

## How the Hook Works

When installed, the recycle bin hook:

1. Verifies the file is inside the project directory
2. Intercepts `rm`, `unlink`, and `trash` commands
3. Moves files to `.claude/bonfire/[plan]/.trash/`
4. Creates metadata for each file (original path, deletion time, etc.)
5. Blocks the original deletion command with feedback to Claude

The hook does NOT protect files in (deletions proceed normally):

- `node_modules/`, `.git/`, `__pycache__/`
- `dist/`, `build/`, `.next/`, `.nuxt/`
- `.venv/`, `venv/`, `.tox/`, `coverage/`

## File Locations

- Trash directory: `.claude/bonfire/[plan]/.trash/`
- Each file has: `[recovery_id]-[filename]/content` (the file) and `metadata.json`

## Example Session

```
Claude: I notice the config.py file was deleted but is needed for the build.
        Let me check if it can be recovered.

> python3 .claude/scripts/manage-recycle-bin.py list

Recoverable Files
============================================
Recovery ID  Original Name  Deleted At            Type    Path
abc12345     config.py      2026-01-16T10:30:00   file    ...src/config.py
--------------------------------------------

Claude: Found it. Let me recover the config.py file.

> python3 .claude/scripts/manage-recycle-bin.py recover abc12345

FILE RECOVERED
Original: /path/to/src/config.py
Restored: /path/to/src/config.py

Claude: I've recovered src/config.py to its original location.
        The build should work now.
```

## Dependencies

The hook requires `bashlex` for bash command parsing:

```bash
pip install bashlex
```
