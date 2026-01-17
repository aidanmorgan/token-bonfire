# Concurrent File Modification

With `{{ACTIVE_DEVELOPERS}}` parallel developers, file conflicts are possible. This documentation has been split into
focused sections for easier navigation.

## Documentation Structure

The concurrency documentation is organized into the following sections:

- **[Overview](concurrency/index.md)** - Quick reference and navigation hub
- **[File Locks](concurrency/file-locks.md)** - File lock protocol and lifecycle
- **[Queue Management](concurrency/queue-management.md)** - Queue timeout handling
- **[Conflict Handling](concurrency/conflict-handling.md)** - Runtime conflict handling
- **[Race Safety](concurrency/race-safety.md)** - Race condition prevention and best practices

## Quick Start

For a comprehensive overview of the concurrency system, start with the [concurrency index](concurrency/index.md).

If you need specific information:

- Understanding how files are locked and released → [File Locks](concurrency/file-locks.md)
- Managing tasks waiting for file availability → [Queue Management](concurrency/queue-management.md)
- Handling runtime file conflicts → [Conflict Handling](concurrency/conflict-handling.md)
- Preventing race conditions in parallel operations → [Race Safety](concurrency/race-safety.md)
