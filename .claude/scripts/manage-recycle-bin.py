#!/usr/bin/env python3
"""
Manage the recycle-bin hook installation and file recovery.

Usage:
    python manage-recycle-bin.py install
    python manage-recycle-bin.py uninstall
    python manage-recycle-bin.py status
    python manage-recycle-bin.py list [--json]
    python manage-recycle-bin.py recover <recovery_id> [--to <path>] [--force]
    python manage-recycle-bin.py purge <recovery_id>
"""

from __future__ import annotations

import json
import os
import shutil
import sys
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from typing import Iterator, Mapping, NamedTuple, Sequence, TypeGuard


# =============================================================================
# Types & Protocols
# =============================================================================

class Action(Enum):
    """CLI actions."""
    INSTALL = auto()
    UNINSTALL = auto()
    STATUS = auto()
    LIST = auto()
    RECOVER = auto()
    PURGE = auto()
    HELP = auto()


class ExitCode(Enum):
    """Exit codes with semantic meaning."""
    SUCCESS = 0
    ERROR = 1
    MISSING_ARG = 2


@dataclass(frozen=True)
class RecoverableFile:
    """A file that can be recovered from trash."""
    recovery_id: str
    original_path: str
    original_name: str
    deleted_at: str
    deleted_by: str
    task_id: str
    file_type: str
    recovery_dir: Path

    @property
    def content_path(self) -> Path:
        return self.recovery_dir / "content"

    @property
    def metadata_path(self) -> Path:
        return self.recovery_dir / "metadata.json"

    def to_dict(self) -> dict:
        return {
            "recovery_id": self.recovery_id,
            "original_path": self.original_path,
            "original_name": self.original_name,
            "deleted_at": self.deleted_at,
            "deleted_by": self.deleted_by,
            "task_id": self.task_id,
            "file_type": self.file_type,
            "recovery_dir": str(self.recovery_dir),
        }


class RecoverOptions(NamedTuple):
    """Options for file recovery."""
    recovery_id: str
    destination: Path | None
    force: bool


class HookStatus(NamedTuple):
    """Status of the recycle-bin hook."""
    installed: bool
    settings_exists: bool
    hook_script_exists: bool
    bashlex_installed: bool
    config: dict | None


# Result type for operations that can fail
class Ok[T](NamedTuple):
    value: T


class Err(NamedTuple):
    message: str


type Result[T] = Ok[T] | Err


def is_ok[T](result: Result[T]) -> TypeGuard[Ok[T]]:
    """TypeGuard for Ok results."""
    return isinstance(result, Ok)


def is_err[T](result: Result[T]) -> TypeGuard[Err]:
    """TypeGuard for Err results."""
    return isinstance(result, Err)


# =============================================================================
# Configuration
# =============================================================================

@dataclass(frozen=True)
class Config:
    """Immutable configuration."""
    settings_file: Path = Path(".claude/settings.json")
    hook_script: Path = Path(".claude/hooks/recycle-bin.py")
    surrogate_base: Path = Path(".claude/surrogate_activities")

    @property
    def hook_config(self) -> dict:
        return {
            "matcher": {
                "tool_name": "Bash",
                "command_patterns": ["rm ", "rm$", "unlink ", "trash "]
            },
            "hooks": [{
                "type": "command",
                "command": str(self.hook_script)
            }]
        }


CONFIG = Config()


# =============================================================================
# Settings Management
# =============================================================================

def load_settings() -> dict:
    """Load settings.json or return empty dict."""
    if not CONFIG.settings_file.exists():
        return {}
    try:
        return json.loads(CONFIG.settings_file.read_text())
    except json.JSONDecodeError:
        print(f"Warning: {CONFIG.settings_file} is invalid JSON", file=sys.stderr)
        return {}


def save_settings(settings: dict) -> None:
    """Save settings atomically."""
    CONFIG.settings_file.parent.mkdir(parents=True, exist_ok=True)
    CONFIG.settings_file.write_text(json.dumps(settings, indent=2) + "\n")


def is_our_hook(hook: dict) -> bool:
    """Check if a hook config is the recycle-bin hook."""
    return any(
        h.get("type") == "command" and "recycle-bin.py" in h.get("command", "")
        for h in hook.get("hooks", [])
    )


def get_pre_tool_hooks(settings: dict) -> list[dict]:
    """Extract PreToolUse hooks from settings."""
    return settings.get("hooks", {}).get("PreToolUse", [])


def is_installed(settings: dict) -> bool:
    """Check if hook is installed."""
    return any(is_our_hook(h) for h in get_pre_tool_hooks(settings))


def add_hook(settings: dict) -> dict:
    """Return new settings with hook added."""
    new_settings = dict(settings)
    new_settings.setdefault("hooks", {}).setdefault("PreToolUse", [])
    new_settings["hooks"]["PreToolUse"].append(CONFIG.hook_config)
    return new_settings


def remove_hook(settings: dict) -> dict:
    """Return new settings with hook removed."""
    new_settings = dict(settings)
    hooks = new_settings.get("hooks", {})
    pre_tool = [h for h in hooks.get("PreToolUse", []) if not is_our_hook(h)]

    if pre_tool:
        hooks["PreToolUse"] = pre_tool
    elif "PreToolUse" in hooks:
        del hooks["PreToolUse"]

    if hooks:
        new_settings["hooks"] = hooks
    elif "hooks" in new_settings:
        del new_settings["hooks"]

    return new_settings


# =============================================================================
# Trash Directory
# =============================================================================

def get_trash_dir() -> Path:
    """Get the trash directory."""
    if plan_dir := os.environ.get("CLAUDE_PLAN_DIR"):
        return Path(plan_dir) / ".trash"

    if CONFIG.surrogate_base.exists():
        dirs = [
            d for d in CONFIG.surrogate_base.iterdir()
            if d.is_dir() and not d.name.startswith(".")
        ]
        if dirs:
            return dirs[0] / ".trash"

    return CONFIG.surrogate_base / "_default" / ".trash"


def parse_metadata(recovery_dir: Path) -> Result[RecoverableFile]:
    """Parse metadata from a recovery directory."""
    metadata_file = recovery_dir / "metadata.json"

    if not metadata_file.exists():
        return Err(f"No metadata in {recovery_dir}")

    try:
        data = json.loads(metadata_file.read_text())
        return Ok(RecoverableFile(
            recovery_id=data.get("recovery_id", "unknown"),
            original_path=data.get("original_path", "unknown"),
            original_name=data.get("original_name", "unknown"),
            deleted_at=data.get("deleted_at", "unknown"),
            deleted_by=data.get("deleted_by", "unknown"),
            task_id=data.get("task_id", "unknown"),
            file_type=data.get("file_type", "unknown"),
            recovery_dir=recovery_dir,
        ))
    except (json.JSONDecodeError, KeyError) as e:
        return Err(f"Invalid metadata in {recovery_dir}: {e}")


def list_recoverable() -> Iterator[RecoverableFile]:
    """Yield all recoverable files, sorted by deletion time."""
    trash_dir = get_trash_dir()
    if not trash_dir.exists():
        return

    files = []
    for recovery_dir in trash_dir.iterdir():
        if not recovery_dir.is_dir():
            continue
        result = parse_metadata(recovery_dir)
        if is_ok(result):
            files.append(result.value)

    # Sort by deletion time, newest first
    yield from sorted(files, key=lambda f: f.deleted_at, reverse=True)


def find_by_id(recovery_id: str) -> Result[RecoverableFile]:
    """Find a recoverable file by ID prefix."""
    for file in list_recoverable():
        if file.recovery_id.startswith(recovery_id):
            return Ok(file)
    return Err(f"Recovery ID not found: {recovery_id}")


# =============================================================================
# Actions
# =============================================================================

def check_dependencies() -> Result[None]:
    """Check if required dependencies are available."""
    try:
        import bashlex  # noqa: F401
        return Ok(None)
    except ImportError:
        return Err("bashlex is not installed. Run: pip install bashlex")


def action_install() -> ExitCode:
    """Install the recycle-bin hook."""
    # Check dependencies
    if is_err(dep_result := check_dependencies()):
        print(f"ERROR: {dep_result.message}")
        return ExitCode.ERROR

    # Check hook script exists
    if not CONFIG.hook_script.exists():
        print(f"ERROR: Hook script not found at {CONFIG.hook_script}")
        return ExitCode.ERROR

    settings = load_settings()

    if is_installed(settings):
        print("Recycle bin hook is already installed.")
        return ExitCode.SUCCESS

    save_settings(add_hook(settings))

    print("=" * 60)
    print("RECYCLE BIN HOOK INSTALLED")
    print("=" * 60)
    print()
    print("Files deleted via rm/unlink/trash will now be moved to:")
    print(f"  {get_trash_dir()}")
    print()
    print("To recover files:")
    print("  /recycle-bin list")
    print("  /recycle-bin recover <id>")
    print()
    print("-" * 60)
    print("IMPORTANT: You must RESTART Claude Code for this to take effect.")
    print("-" * 60)

    return ExitCode.SUCCESS


def action_uninstall() -> ExitCode:
    """Remove the recycle-bin hook."""
    settings = load_settings()

    if not is_installed(settings):
        print("Recycle bin hook is not installed.")
        return ExitCode.SUCCESS

    save_settings(remove_hook(settings))

    print("=" * 60)
    print("RECYCLE BIN HOOK REMOVED")
    print("=" * 60)
    print()
    print("File deletions will now be permanent.")
    print()
    print("-" * 60)
    print("IMPORTANT: You must RESTART Claude Code for this to take effect.")
    print("-" * 60)

    return ExitCode.SUCCESS


def action_status() -> ExitCode:
    """Show current hook status."""
    settings = load_settings()

    status = HookStatus(
        installed=is_installed(settings),
        settings_exists=CONFIG.settings_file.exists(),
        hook_script_exists=CONFIG.hook_script.exists(),
        bashlex_installed=is_ok(check_dependencies()),
        config=next((h for h in get_pre_tool_hooks(settings) if is_our_hook(h)), None),
    )

    print("Recycle Bin Hook Status")
    print("-" * 40)
    print(f"Installed: {'Yes' if status.installed else 'No'}")
    print(f"Settings file: {CONFIG.settings_file} ({'exists' if status.settings_exists else 'missing'})")
    print(f"Hook script: {CONFIG.hook_script} ({'exists' if status.hook_script_exists else 'missing'})")
    print(f"bashlex: {'installed' if status.bashlex_installed else 'NOT installed (required)'}")

    if status.config:
        print()
        print("Hook configuration:")
        print(json.dumps(status.config, indent=2))

    return ExitCode.SUCCESS


def action_list(as_json: bool) -> ExitCode:
    """List all recoverable files."""
    files = list(list_recoverable())

    if as_json:
        print(json.dumps([f.to_dict() for f in files], indent=2))
        return ExitCode.SUCCESS

    if not files:
        print("No recoverable files found.")
        print(f"\nTrash directory: {get_trash_dir()}")
        return ExitCode.SUCCESS

    # Table formatting
    def truncate(s: str, n: int) -> str:
        return s[:n - 3] + "..." if len(s) > n else s

    def truncate_left(s: str, n: int) -> str:
        return "..." + s[-(n - 3):] if len(s) > n else s

    print("Recoverable Files")
    print("=" * 100)
    print(f"{'ID':<10} {'Name':<32} {'Deleted At':<20} {'Type':<8} {'Path'}")
    print("-" * 100)

    for f in files:
        print(
            f"{f.recovery_id[:8]:<10} "
            f"{truncate(f.original_name, 30):<32} "
            f"{f.deleted_at[:19]:<20} "
            f"{f.file_type[:6]:<8} "
            f"{truncate_left(f.original_path, 40)}"
        )

    print("-" * 100)
    print(f"Total: {len(files)} file(s)")
    print()
    print("To recover: /recycle-bin recover <id>")

    return ExitCode.SUCCESS


def action_recover(opts: RecoverOptions) -> ExitCode:
    """Recover a file."""
    result = find_by_id(opts.recovery_id)

    if is_err(result):
        print(f"Error: {result.message}")
        print("\nUse '/recycle-bin list' to see available files.")
        return ExitCode.ERROR

    file = result.value

    if not file.content_path.exists():
        print(f"Error: Recovery data incomplete for: {opts.recovery_id}")
        return ExitCode.ERROR

    dest = opts.destination or Path(file.original_path)

    if dest.exists() and not opts.force:
        print(f"Error: Destination already exists: {dest}")
        print("\nUse --force to overwrite, or --to <path> for different location.")
        return ExitCode.ERROR

    # Remove existing if force
    if dest.exists():
        shutil.rmtree(dest) if dest.is_dir() else dest.unlink()

    # Ensure parent exists
    dest.parent.mkdir(parents=True, exist_ok=True)

    # Copy content
    if file.content_path.is_dir():
        shutil.copytree(file.content_path, dest)
    else:
        shutil.copy2(file.content_path, dest)

    # Clean up recovery directory
    shutil.rmtree(file.recovery_dir)

    print("=" * 60)
    print("FILE RECOVERED")
    print("=" * 60)
    print()
    print(f"Original: {file.original_path}")
    print(f"Restored: {dest}")
    print(f"Deleted:  {file.deleted_at}")
    if file.deleted_by != "unknown":
        print(f"By:       {file.deleted_by}")
    print()
    print("Recovery data cleaned up.")

    return ExitCode.SUCCESS


def action_purge(recovery_id: str) -> ExitCode:
    """Permanently delete a recoverable file."""
    result = find_by_id(recovery_id)

    if is_err(result):
        print(f"Error: {result.message}")
        return ExitCode.ERROR

    file = result.value
    shutil.rmtree(file.recovery_dir)

    print(f"Purged: {file.original_path}")
    print(f"Recovery ID: {file.recovery_id}")

    return ExitCode.SUCCESS


def action_help() -> ExitCode:
    """Show usage information."""
    print("Usage: /recycle-bin <action> [options]")
    print()
    print("Hook Management:")
    print("  install              Enable recycle bin hook")
    print("  uninstall            Remove recycle bin hook")
    print("  status               Show current hook status")
    print()
    print("File Recovery:")
    print("  list [--json]        List recoverable files")
    print("  recover <id>         Recover to original location")
    print("  recover <id> --to <path>   Recover to different location")
    print("  recover <id> --force       Overwrite if exists")
    print("  purge <id>           Permanently delete from trash")
    print()
    print("The hook intercepts rm/unlink/trash commands and moves files to")
    print(f"{get_trash_dir()} instead of deleting them.")

    return ExitCode.SUCCESS


# =============================================================================
# CLI Parsing
# =============================================================================

def parse_action(arg: str) -> Action:
    """Parse action from command line argument."""
    mapping: Mapping[str, Action] = {
        "install": Action.INSTALL,
        "uninstall": Action.UNINSTALL,
        "status": Action.STATUS,
        "list": Action.LIST,
        "recover": Action.RECOVER,
        "purge": Action.PURGE,
        "help": Action.HELP,
        "--help": Action.HELP,
        "-h": Action.HELP,
    }
    return mapping.get(arg.lower().strip(), Action.HELP)


def parse_recover_options(args: Sequence[str]) -> Result[RecoverOptions]:
    """Parse recover command options."""
    if len(args) < 1:
        return Err("Missing recovery ID")

    recovery_id = args[0]
    destination: Path | None = None
    force = "--force" in args

    if "--to" in args:
        try:
            idx = args.index("--to")
            destination = Path(args[idx + 1])
        except (IndexError, ValueError):
            return Err("--to requires a path argument")

    return Ok(RecoverOptions(recovery_id, destination, force))


def dispatch(action: Action, args: Sequence[str]) -> ExitCode:
    """Dispatch to the appropriate action handler."""
    match action:
        case Action.INSTALL:
            return action_install()
        case Action.UNINSTALL:
            return action_uninstall()
        case Action.STATUS:
            return action_status()
        case Action.LIST:
            return action_list(as_json="--json" in args)
        case Action.RECOVER:
            result = parse_recover_options(args)
            if is_err(result):
                print(f"Error: {result.message}")
                print("Usage: /recycle-bin recover <id> [--to <path>] [--force]")
                return ExitCode.MISSING_ARG
            return action_recover(result.value)
        case Action.PURGE:
            if not args:
                print("Error: Missing recovery ID")
                print("Usage: /recycle-bin purge <id>")
                return ExitCode.MISSING_ARG
            return action_purge(args[0])
        case Action.HELP:
            return action_help()


def main() -> int:
    """Entry point."""
    if len(sys.argv) < 2:
        return action_help().value

    action = parse_action(sys.argv[1])
    remaining_args = sys.argv[2:]

    return dispatch(action, remaining_args).value


if __name__ == "__main__":
    sys.exit(main())
