#!/usr/bin/env python3
"""Get Claude Code session/subscription usage."""

import json
import subprocess
import sys
import urllib.request


def get_claude_version() -> str:
    """Get the installed Claude Code version."""
    try:
        result = subprocess.run(["claude", "--version"], capture_output=True, text=True, check=True)
        # Output is like "2.1.3 (Claude Code)"
        return result.stdout.strip().split()[0]
    except (subprocess.CalledProcessError, IndexError):
        return "2.1.3"


def get_access_token() -> str | None:
    """Get the Claude Code access token from macOS Keychain."""
    try:
        user_result = subprocess.run(["whoami"], capture_output=True, text=True, check=True)
        username = user_result.stdout.strip()

        result = subprocess.run(
            ["security", "find-generic-password", "-s", "Claude Code-credentials", "-a", username, "-w"],
            capture_output=True,
            text=True,
            check=True,
        )
        creds = json.loads(result.stdout.strip())
        return creds.get("claudeAiOauth", {}).get("accessToken")
    except (subprocess.CalledProcessError, json.JSONDecodeError, KeyError):
        return None


def get_usage() -> dict:
    """Fetch usage from the Anthropic API."""
    token = get_access_token()
    if not token:
        return {"error": "Could not retrieve access token from Keychain"}

    version = get_claude_version()
    req = urllib.request.Request(
        "https://api.anthropic.com/api/oauth/usage",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "anthropic-beta": "oauth-2025-04-20",
            "User-Agent": f"claude-code/{version}",
        },
    )

    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        return {"error": f"HTTP {e.code}: {e.reason}"}
    except urllib.error.URLError as e:
        return {"error": f"URL error: {e.reason}"}


def main() -> int:
    """Main entry point."""
    usage = get_usage()

    if "error" in usage:
        print(f"Error: {usage['error']}")
        return 1

    five_hour = usage.get("five_hour", {})
    utilization = five_hour.get("utilization", 0)
    resets_at = five_hour.get("resets_at", "unknown")

    print(f"utilisation: {utilization}%")
    print(f"remaining: {100 - utilization}%")
    print(f"resets_at: {resets_at}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
