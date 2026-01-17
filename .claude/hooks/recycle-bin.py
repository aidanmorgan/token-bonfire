#!/usr/bin/env python3
"""
Recycle Bin Hook - File Deletion Protection

Intercepts file deletion commands and either:
1. Moves files to a recoverable .trash/ location
2. Blocks the deletion entirely (for protected paths or errors)

NEVER allows deletion of:
- Files in .trash/ directories
- Files outside the project directory

Exit Codes:
- 0 with JSON {"hookSpecificOutput": {"permissionDecision": "deny"}}: Block with feedback
- 0 with JSON {"hookSpecificOutput": {"permissionDecision": "allow"}}: Allow to proceed
- 2: Blocking error (stderr shown to Claude)

Dependencies: pip install bashlex
"""

from __future__ import annotations

import json
import os
import shutil
import sys
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum, auto
from functools import reduce
from glob import glob
from pathlib import Path
from typing import Sequence

try:
    import bashlex
    import bashlex.ast
except ImportError:
    # Block deletion if we can't parse the command
    print("BLOCKED: bashlex not installed. Cannot safely parse deletion command. Run: pip install bashlex",
          file=sys.stderr)
    sys.exit(2)


# =============================================================================
# Environment & Configuration
# =============================================================================

def get_project_dir() -> Path:
    """Get the project directory from environment."""
    project_dir = os.environ.get('CLAUDE_PROJECT_DIR')
    if project_dir:
        return Path(project_dir).resolve()
    # Fallback to cwd if not set
    return Path.cwd().resolve()


def get_plan_dir() -> Path:
    """Get the plan directory for trash storage."""
    plan_dir = os.environ.get('CLAUDE_PLAN_DIR')
    if plan_dir:
        return Path(plan_dir)
    return Path('.claude/bonfire/_default')


PROJECT_DIR = get_project_dir()
PLAN_DIR = get_plan_dir()
TRASH_DIR = PLAN_DIR / '.trash'


@dataclass(frozen=True)
class Config:
    """Immutable configuration."""

    # Directories excluded from protection (deletions proceed normally)
    excluded_patterns: tuple[str, ...] = (
        '/node_modules/',
        '/.git/',
        '/__pycache__/',
        '/.pytest_cache/',
        '/.mypy_cache/',
        '/.ruff_cache/',
        '/dist/',
        '/build/',
        '/.next/',
        '/.nuxt/',
        '/coverage/',
        '/.tox/',
        '/.venv/',
        '/venv/',
        '/.env/',
    )

    # Patterns where deletions are ALWAYS blocked (never allowed)
    blocked_patterns: tuple[str, ...] = (
        '/.trash/',
    )

    # Commands that delete files
    deletion_commands: frozenset[str] = frozenset({
        'rm', 'unlink', 'trash', 'trash-put', 'del', 'remove'
    })

    # Prefix commands to skip
    prefix_commands: frozenset[str] = frozenset({
        'sudo', 'env', 'nice', 'nohup', 'time', 'timeout', 'strace', 'ltrace'
    })


CONFIG = Config()


# =============================================================================
# Response Helpers
# =============================================================================

def block_with_feedback(reason: str) -> None:
    """Block the deletion and provide feedback to Claude via stderr."""
    print(f"BLOCKED: {reason}", file=sys.stderr)
    sys.exit(2)


def deny_with_json(reason: str) -> None:
    """Deny using structured JSON response."""
    response = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason
        }
    }
    print(json.dumps(response))
    sys.exit(0)


def allow_command() -> None:
    """Allow the original command to proceed (for excluded directories)."""
    response = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "allow"
        }
    }
    print(json.dumps(response))
    sys.exit(0)


# =============================================================================
# Path Classification
# =============================================================================

class PathStatus(Enum):
    """Classification of a file path."""
    PROTECT = auto()  # Move to trash
    BLOCKED = auto()  # Never allow deletion
    EXCLUDED = auto()  # Allow deletion (excluded directory)
    OUTSIDE_PROJECT = auto()  # Outside project - block
    ERROR = auto()  # Could not resolve - block for safety


def resolve_path(path: str) -> Path | None:
    """Safely resolve a path."""
    try:
        return Path(path).resolve()
    except (OSError, ValueError):
        return None


def is_inside_project(path: Path) -> bool:
    """Check if a path is inside the project directory."""
    try:
        path.relative_to(PROJECT_DIR)
        return True
    except ValueError:
        return False


def matches_pattern(path: str, patterns: Sequence[str]) -> bool:
    """Check if path contains any pattern."""
    return any(p in path for p in patterns)


def classify_path(file_path: str) -> PathStatus:
    """Classify how to handle a file path."""
    resolved = resolve_path(file_path)

    if resolved is None:
        return PathStatus.ERROR

    abs_path = str(resolved)

    # Check if outside project - ALWAYS block
    if not is_inside_project(resolved):
        return PathStatus.OUTSIDE_PROJECT

    # Check blocked patterns (like .trash) - ALWAYS block
    if matches_pattern(abs_path, CONFIG.blocked_patterns):
        return PathStatus.BLOCKED

    # Check excluded patterns - allow deletion
    if matches_pattern(abs_path, CONFIG.excluded_patterns):
        return PathStatus.EXCLUDED

    # Default: protect by moving to trash
    return PathStatus.PROTECT


# =============================================================================
# Command Parsing
# =============================================================================

@dataclass(frozen=True)
class DeletionCommand:
    """A parsed deletion command."""
    command: str
    files: tuple[str, ...]


class DeletionVisitor(bashlex.ast.nodevisitor):
    """AST visitor to extract deletion commands."""

    def __init__(self) -> None:
        self.deletions: list[DeletionCommand] = []

    def _extract_word(self, node) -> str | None:
        match node.kind:
            case 'word':
                return node.word
            case _:
                return None

    def _skip_prefixes(self, words: list[str | None]) -> list[str | None]:
        result = list(words)
        while result:
            word = result[0]
            if word is None:
                result.pop(0)
                continue
            if '=' in word and not word.startswith('-'):
                result.pop(0)
                continue
            if os.path.basename(word) in CONFIG.prefix_commands:
                result.pop(0)
                continue
            break
        return result

    def _parse_files(self, cmd: str, args: Sequence[str | None]) -> tuple[str, ...]:
        files: list[str] = []
        end_opts = False
        for arg in args:
            if arg is None:
                continue
            if end_opts:
                files.append(arg)
            elif arg == '--':
                end_opts = True
            elif not arg.startswith('-'):
                files.append(arg)
        return tuple(files)

    def visitcommand(self, node, parts) -> None:
        words = [self._extract_word(p) for p in parts]
        words = self._skip_prefixes(words)

        if not words or words[0] is None:
            return

        cmd = os.path.basename(words[0])
        if cmd not in CONFIG.deletion_commands:
            return

        files = self._parse_files(cmd, words[1:])
        if files:
            self.deletions.append(DeletionCommand(cmd, files))


def parse_command(command: str) -> list[DeletionCommand]:
    """Parse bash command to find deletions."""
    try:
        parts = bashlex.parse(command)
        visitor = DeletionVisitor()
        for part in parts:
            visitor.visit(part)
        return visitor.deletions
    except bashlex.errors.ParsingError as e:
        # If we can't parse, block for safety
        block_with_feedback(f"Could not parse command safely: {e}")
        return []  # Never reached


def expand_globs(files: Sequence[str]) -> tuple[str, ...]:
    """Expand glob patterns."""

    def expand(f: str) -> list[str]:
        if any(c in f for c in '*?['):
            matches = glob(f, recursive=True)
            return matches if matches else [f]
        return [f]

    return tuple(x for f in files for x in expand(f))


# =============================================================================
# File Protection
# =============================================================================

@dataclass
class FileMetadata:
    """Metadata for protected files."""
    original_path: str
    original_name: str
    deleted_at: str
    deleted_by: str
    task_id: str
    file_type: str
    recovery_id: str
    recovery_path: str

    def to_dict(self) -> dict:
        return self.__dict__


def get_file_type(path: Path) -> str:
    if path.is_symlink():
        return "symlink"
    if path.is_dir():
        return "directory"
    if path.is_file():
        return "file"
    return "unknown"


def move_to_trash(path: Path) -> str:
    """Move file to trash. Returns recovery_id."""
    TRASH_DIR.mkdir(parents=True, exist_ok=True)

    recovery_id = str(uuid.uuid4())[:8]
    recovery_dir = TRASH_DIR / f"{recovery_id}-{path.name}"
    recovery_dir.mkdir(parents=True, exist_ok=True)
    recovery_content = recovery_dir / "content"

    if path.is_dir():
        shutil.copytree(path, recovery_content, symlinks=True)
        shutil.rmtree(path)
    else:
        shutil.move(str(path), str(recovery_content))

    # Write metadata
    metadata = FileMetadata(
        original_path=str(path.resolve()),
        original_name=path.name,
        deleted_at=datetime.now(timezone.utc).isoformat(),
        deleted_by=os.environ.get('CLAUDE_AGENT_ID', 'unknown'),
        task_id=os.environ.get('CLAUDE_TASK_ID', 'unknown'),
        file_type=get_file_type(path),
        recovery_id=recovery_id,
        recovery_path=str(recovery_content),
    )
    (recovery_dir / "metadata.json").write_text(json.dumps(metadata.to_dict(), indent=2))

    return recovery_id


@dataclass
class ProcessResult:
    """Result of processing a file."""
    path: str
    status: PathStatus
    message: str
    recovery_id: str | None = None


def process_file(file_path: str) -> ProcessResult:
    """Process a single file for deletion."""
    path = Path(file_path)

    # Non-existent files - allow the rm to handle it
    if not path.exists() and not path.is_symlink():
        return ProcessResult(file_path, PathStatus.EXCLUDED, f"Does not exist: {file_path}")

    status = classify_path(file_path)

    match status:
        case PathStatus.OUTSIDE_PROJECT:
            return ProcessResult(
                file_path, status,
                f"BLOCKED: Cannot delete files outside project ({PROJECT_DIR}): {file_path}"
            )

        case PathStatus.BLOCKED:
            return ProcessResult(
                file_path, status,
                f"BLOCKED: Cannot delete from protected directory: {file_path}"
            )

        case PathStatus.ERROR:
            return ProcessResult(
                file_path, status,
                f"BLOCKED: Could not safely resolve path: {file_path}"
            )

        case PathStatus.EXCLUDED:
            return ProcessResult(
                file_path, status,
                f"Excluded (allowing deletion): {file_path}"
            )

        case PathStatus.PROTECT:
            try:
                recovery_id = move_to_trash(path)
                return ProcessResult(
                    file_path, status,
                    f"Protected: {file_path} -> {TRASH_DIR}/{recovery_id}-{path.name}",
                    recovery_id
                )
            except Exception as e:
                return ProcessResult(
                    file_path, PathStatus.ERROR,
                    f"BLOCKED: Failed to protect {file_path}: {e}"
                )

        case _:
            return ProcessResult(
                file_path, PathStatus.ERROR,
                f"BLOCKED: Unknown status for {file_path}"
            )


# =============================================================================
# Main
# =============================================================================

def main() -> int:
    """Main entry point."""
    # Read from stdin (hook receives tool input as JSON)
    try:
        stdin_data = sys.stdin.read().strip()
        if not stdin_data:
            block_with_feedback("No input received")

        # Try to parse as JSON (hook input format)
        try:
            input_data = json.loads(stdin_data)
            command = input_data.get('tool_input', {}).get('command', '')
        except json.JSONDecodeError:
            # Fallback: treat as raw command
            command = stdin_data

        if not command:
            block_with_feedback("Empty command")

    except Exception as e:
        block_with_feedback(f"Failed to read input: {e}")

    # Parse command
    deletions = parse_command(command)

    if not deletions:
        # No deletion commands found - allow to proceed
        allow_command()

    # Collect all files
    all_files = expand_globs(
        reduce(lambda acc, d: acc + d.files, deletions, ())
    )

    if not all_files:
        allow_command()

    # Process each file
    results = [process_file(f) for f in all_files]

    # Output results to stderr (visible in verbose mode)
    for r in results:
        print(r.message, file=sys.stderr)

    # Determine outcome
    blocked = [r for r in results if r.status in (PathStatus.BLOCKED, PathStatus.OUTSIDE_PROJECT, PathStatus.ERROR)]
    protected = [r for r in results if r.status == PathStatus.PROTECT]
    excluded = [r for r in results if r.status == PathStatus.EXCLUDED]

    # If ANY file was blocked, block the entire command
    if blocked:
        reasons = [r.message for r in blocked]
        deny_with_json(f"Deletion blocked: {'; '.join(reasons)}")

    # If ALL files were protected or excluded, we handled them
    if protected:
        # We moved the files to trash - block the original rm command
        protected_files = [r.path for r in protected]
        deny_with_json(
            f"Files moved to recycle bin ({TRASH_DIR}): {', '.join(protected_files)}. "
            f"Use /recycle-bin list to see recoverable files."
        )

    # All files were excluded - allow the command
    allow_command()


if __name__ == '__main__':
    main()
