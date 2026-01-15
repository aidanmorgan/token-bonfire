#!/bin/bash
# File Deletion Protection Hook
#
# This hook intercepts file deletion commands and moves files to a recoverable
# location instead of permanently deleting them.
#
# Usage: This script is invoked by Claude Code hooks system before commands like:
#   rm, rm -f, rm -rf, unlink, trash
#
# Files are moved to: {{PLAN_DIR}}/.trash/[uuid]-[original-name]/
# With metadata stored in: metadata.json

set -euo pipefail

# Configuration
SURROGATE_BASE=".claude/surrogate_activities"

# Get the current plan directory from environment or default
get_plan_dir() {
    if [[ -n "${CLAUDE_PLAN_DIR:-}" ]]; then
        echo "$CLAUDE_PLAN_DIR"
    else
        # Default to a generic location if plan not set
        echo "$SURROGATE_BASE/_default"
    fi
}

# Generate a unique ID for the deleted file
generate_uuid() {
    if command -v uuidgen &> /dev/null; then
        uuidgen | tr '[:upper:]' '[:lower:]'
    else
        # Fallback: use timestamp + random
        echo "$(date +%s)-$$-$RANDOM"
    fi
}

# Get the original filename without path
get_basename() {
    basename "$1"
}

# Create the tmp directory structure
ensure_tmp_dir() {
    local plan_dir="$1"
    local tmp_dir="$plan_dir/.trash"
    mkdir -p "$tmp_dir"
    echo "$tmp_dir"
}

# Move file to recoverable location with metadata
protect_file() {
    local file_path="$1"
    local plan_dir
    local tmp_dir
    local uuid
    local original_name
    local recovery_dir
    local metadata_file
    local abs_path
    local file_type

    # Skip if file doesn't exist
    if [[ ! -e "$file_path" ]]; then
        echo "SKIP: File does not exist: $file_path" >&2
        return 0
    fi

    # Get absolute path
    abs_path="$(cd "$(dirname "$file_path")" && pwd)/$(basename "$file_path")"

    # Skip files in .trash directories (already protected)
    if [[ "$abs_path" == *"/.trash/"* ]]; then
        echo "SKIP: File already in .trash: $file_path" >&2
        return 0
    fi

    # Skip files in node_modules, .git, etc.
    if [[ "$abs_path" == *"/node_modules/"* ]] || \
       [[ "$abs_path" == *"/.git/"* ]] || \
       [[ "$abs_path" == *"/__pycache__/"* ]] || \
       [[ "$abs_path" == *"/.pytest_cache/"* ]] || \
       [[ "$abs_path" == *"/.mypy_cache/"* ]] || \
       [[ "$abs_path" == *"/.ruff_cache/"* ]]; then
        echo "SKIP: File in excluded directory: $file_path" >&2
        # Allow actual deletion for these
        return 1
    fi

    plan_dir="$(get_plan_dir)"
    tmp_dir="$(ensure_tmp_dir "$plan_dir")"
    uuid="$(generate_uuid)"
    original_name="$(get_basename "$file_path")"
    recovery_dir="$tmp_dir/${uuid}-${original_name}"

    # Create recovery directory
    mkdir -p "$recovery_dir"

    # Determine file type
    if [[ -d "$file_path" ]]; then
        file_type="directory"
    elif [[ -f "$file_path" ]]; then
        file_type="file"
    elif [[ -L "$file_path" ]]; then
        file_type="symlink"
    else
        file_type="unknown"
    fi

    # Move the file/directory to recovery location
    if [[ -d "$file_path" ]]; then
        # For directories, copy then remove
        cp -R "$file_path" "$recovery_dir/content"
    else
        mv "$file_path" "$recovery_dir/content"
    fi

    # Create metadata file
    metadata_file="$recovery_dir/metadata.json"
    cat > "$metadata_file" << EOF
{
    "original_path": "$abs_path",
    "original_name": "$original_name",
    "deleted_at": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
    "deleted_by": "${CLAUDE_AGENT_ID:-unknown}",
    "task_id": "${CLAUDE_TASK_ID:-unknown}",
    "file_type": "$file_type",
    "recovery_id": "$uuid",
    "recovery_path": "$recovery_dir/content"
}
EOF

    echo "PROTECTED: $file_path -> $recovery_dir" >&2
    echo "Recovery ID: $uuid" >&2

    # If it was a directory that we copied, now remove the original
    if [[ -d "$file_path" ]]; then
        rm -rf "$file_path"
    fi

    return 0
}

# Main hook logic
main() {
    local cmd="$1"
    shift

    case "$cmd" in
        rm|unlink|trash)
            # Process each file argument
            local skip_next=false
            for arg in "$@"; do
                if $skip_next; then
                    skip_next=false
                    continue
                fi

                # Skip flags
                case "$arg" in
                    -*)
                        # Check for flags that take arguments
                        if [[ "$arg" == "-I" ]] || [[ "$arg" == "--interactive" ]]; then
                            skip_next=true
                        fi
                        continue
                        ;;
                esac

                # Protect this file
                if ! protect_file "$arg"; then
                    # Protection was skipped, allow deletion
                    return 1
                fi
            done

            # Return success to prevent actual deletion
            return 0
            ;;
        *)
            # Unknown command, allow to proceed
            return 1
            ;;
    esac
}

# Run main if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
