#!/usr/bin/env python3
"""
File Recovery Utility

Recovers files that were protected by the deletion hook.

Usage:
    python recover-file.py list                    # List all recoverable files
    python recover-file.py recover <recovery_id>  # Recover a specific file
    python recover-file.py recover <recovery_id> --to <path>  # Recover to specific path
    python recover-file.py purge <recovery_id>    # Permanently delete
    python recover-file.py purge-all --older-than 7d  # Purge files older than 7 days
"""

import argparse
import json
import os
import shutil
import sys
from datetime import datetime, timedelta
from pathlib import Path


def get_plan_dir() -> Path:
    """Get the current plan directory."""
    plan_dir = os.environ.get("CLAUDE_PLAN_DIR")
    if plan_dir:
        return Path(plan_dir)

    # Try to find surrogate_activities directories
    surrogate_base = Path(".claude/surrogate_activities")
    if surrogate_base.exists():
        # Return the first one found, or _default
        dirs = [d for d in surrogate_base.iterdir() if d.is_dir()]
        if dirs:
            return dirs[0]

    return surrogate_base / "_default"


def get_tmp_dir() -> Path:
    """Get the .trash directory for recoverable files."""
    return get_plan_dir() / ".trash"


def list_recoverable_files() -> list[dict]:
    """List all recoverable files with their metadata."""
    tmp_dir = get_tmp_dir()
    if not tmp_dir.exists():
        return []

    files = []
    for recovery_dir in tmp_dir.iterdir():
        if not recovery_dir.is_dir():
            continue

        metadata_file = recovery_dir / "metadata.json"
        if not metadata_file.exists():
            continue

        with open(metadata_file) as f:
            metadata = json.load(f)
            metadata["recovery_dir"] = str(recovery_dir)
            files.append(metadata)

    # Sort by deletion time, newest first
    files.sort(key=lambda x: x.get("deleted_at", ""), reverse=True)
    return files


def recover_file(recovery_id: str, destination: str | None = None) -> bool:
    """Recover a file by its recovery ID."""
    tmp_dir = get_tmp_dir()

    # Find the recovery directory
    recovery_dir = None
    for d in tmp_dir.iterdir():
        if d.is_dir() and d.name.startswith(recovery_id):
            recovery_dir = d
            break

    if not recovery_dir:
        print(f"Error: Recovery ID not found: {recovery_id}", file=sys.stderr)
        return False

    metadata_file = recovery_dir / "metadata.json"
    content_path = recovery_dir / "content"

    if not metadata_file.exists() or not content_path.exists():
        print(f"Error: Recovery data incomplete for: {recovery_id}", file=sys.stderr)
        return False

    with open(metadata_file) as f:
        metadata = json.load(f)

    # Determine destination
    if destination:
        dest_path = Path(destination)
    else:
        dest_path = Path(metadata["original_path"])

    # Check if destination already exists
    if dest_path.exists():
        print(f"Warning: Destination already exists: {dest_path}", file=sys.stderr)
        response = input("Overwrite? [y/N]: ").strip().lower()
        if response != "y":
            print("Recovery cancelled.")
            return False

        if dest_path.is_dir():
            shutil.rmtree(dest_path)
        else:
            dest_path.unlink()

    # Ensure parent directory exists
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    # Recover the file
    if content_path.is_dir():
        shutil.copytree(content_path, dest_path)
    else:
        shutil.copy2(content_path, dest_path)

    print(f"Recovered: {metadata['original_path']}")
    print(f"       To: {dest_path}")

    # Optionally clean up recovery directory
    response = input("Delete recovery data? [Y/n]: ").strip().lower()
    if response != "n":
        shutil.rmtree(recovery_dir)
        print("Recovery data deleted.")

    return True


def purge_file(recovery_id: str) -> bool:
    """Permanently delete a recoverable file."""
    tmp_dir = get_tmp_dir()

    # Find the recovery directory
    for d in tmp_dir.iterdir():
        if d.is_dir() and d.name.startswith(recovery_id):
            shutil.rmtree(d)
            print(f"Purged: {recovery_id}")
            return True

    print(f"Error: Recovery ID not found: {recovery_id}", file=sys.stderr)
    return False


def purge_old_files(older_than: str) -> int:
    """Purge files older than specified duration."""
    # Parse duration (e.g., "7d", "24h", "30m")
    unit = older_than[-1]
    value = int(older_than[:-1])

    if unit == "d":
        delta = timedelta(days=value)
    elif unit == "h":
        delta = timedelta(hours=value)
    elif unit == "m":
        delta = timedelta(minutes=value)
    else:
        print(f"Error: Unknown duration unit: {unit}", file=sys.stderr)
        return 0

    cutoff = datetime.utcnow() - delta
    purged = 0

    for file_info in list_recoverable_files():
        deleted_at = datetime.fromisoformat(file_info["deleted_at"].replace("Z", "+00:00"))
        if deleted_at.replace(tzinfo=None) < cutoff:
            recovery_dir = Path(file_info["recovery_dir"])
            shutil.rmtree(recovery_dir)
            print(f"Purged: {file_info['original_name']} (deleted {file_info['deleted_at']})")
            purged += 1

    return purged


def main():
    parser = argparse.ArgumentParser(description="File Recovery Utility")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # List command
    list_parser = subparsers.add_parser("list", help="List recoverable files")
    list_parser.add_argument("--json", action="store_true", help="Output as JSON")

    # Recover command
    recover_parser = subparsers.add_parser("recover", help="Recover a file")
    recover_parser.add_argument("recovery_id", help="Recovery ID (or prefix)")
    recover_parser.add_argument("--to", dest="destination", help="Recovery destination path")

    # Purge command
    purge_parser = subparsers.add_parser("purge", help="Permanently delete recoverable file")
    purge_parser.add_argument("recovery_id", help="Recovery ID (or prefix)")

    # Purge-all command
    purge_all_parser = subparsers.add_parser("purge-all", help="Purge old recoverable files")
    purge_all_parser.add_argument("--older-than", required=True, help="Duration (e.g., 7d, 24h, 30m)")

    args = parser.parse_args()

    if args.command == "list":
        files = list_recoverable_files()
        if args.json:
            print(json.dumps(files, indent=2))
        else:
            if not files:
                print("No recoverable files found.")
            else:
                print(f"{'Recovery ID':<40} {'Original Name':<30} {'Deleted At':<25} {'Type'}")
                print("-" * 110)
                for f in files:
                    rid = f.get("recovery_id", "unknown")[:36]
                    name = f.get("original_name", "unknown")[:28]
                    deleted = f.get("deleted_at", "unknown")[:23]
                    ftype = f.get("file_type", "unknown")
                    print(f"{rid:<40} {name:<30} {deleted:<25} {ftype}")

    elif args.command == "recover":
        recover_file(args.recovery_id, args.destination)

    elif args.command == "purge":
        purge_file(args.recovery_id)

    elif args.command == "purge-all":
        count = purge_old_files(args.older_than)
        print(f"Purged {count} files.")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
