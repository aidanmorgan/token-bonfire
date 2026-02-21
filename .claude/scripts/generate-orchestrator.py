#!/usr/bin/env python3
"""Extract plan metadata (title and slug) from a plan file.

Usage:
    python generate-orchestrator.py <plan_file>

Extracts the plan title from the first H1 heading and computes a
deterministic slug. Task parsing is delegated to a Claude sub-agent
that can understand any plan format.

Outputs JSON to stdout:
    { "plan_title": "...", "plan_slug": "..." }
"""

from __future__ import annotations

import json
import re
import sys
import unicodedata
from pathlib import Path


def slugify(text: str) -> str:
    """Convert text to a URL-safe slug suitable for use as a task list name.

    Examples:
        "User Authentication Implementation Plan" -> "user-authentication-implementation-plan"
        "API v2.0 Migration" -> "api-v2-0-migration"
    """
    # Normalize unicode characters
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    # Lowercase
    text = text.lower()
    # Replace non-alphanumeric with hyphens
    text = re.sub(r"[^a-z0-9]+", "-", text)
    # Strip leading/trailing hyphens and collapse multiples
    text = re.sub(r"-+", "-", text).strip("-")
    return text or "untitled-plan"


def extract_plan_title(content: str) -> str:
    """Extract the plan title from the first H1 heading."""
    match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    return match.group(1).strip() if match else "Untitled Plan"


def main() -> None:
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python generate-orchestrator.py <plan_file>", file=sys.stderr)
        print(
            "Extracts plan title and slug. Task parsing is handled by a Claude sub-agent.",
            file=sys.stderr,
        )
        sys.exit(1)

    plan_file = sys.argv[1]
    plan_path = Path(plan_file)

    if not plan_path.exists():
        print(f"ERROR: Plan file not found: {plan_file}", file=sys.stderr)
        sys.exit(1)

    content = plan_path.read_text()
    title = extract_plan_title(content)
    slug = slugify(title)

    print(json.dumps({"plan_title": title, "plan_slug": slug}, indent=2))


if __name__ == "__main__":
    main()
