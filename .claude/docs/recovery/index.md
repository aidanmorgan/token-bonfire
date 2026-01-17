# Recovery System Overview

This directory contains comprehensive recovery procedures for handling various failure scenarios in the Token Bonfire
coordination system.

## Purpose

The recovery system ensures the coordinator can gracefully handle and recover from:

- File corruption (event logs, state files, plan files)
- Missing files (agent definitions, configuration)
- Session interruptions and restarts
- Pre-existing infrastructure failures
- Inconsistent state across multiple data sources

## Recovery Documents

### Core Recovery Procedures

1. **[Event Log Recovery](event-log-recovery.md)**
    - Corruption detection and validation
    - Recovery from truncation
    - Reconstruction when missing
    - State reconstruction from events

2. **[State Recovery](state-recovery.md)**
    - State file corruption detection
    - Recovery from corrupted state files
    - State reconstruction from event log

3. **[Agent Recovery](agent-file-recovery.md)**
    - Missing agent definition files
    - Agent file recreation from templates
    - Critic-specific recovery procedures

### Failure Management

4. **[Baseline Failures](baseline-failures.md)**
    - Pre-existing failure baseline capture
    - Classification of failures (pre-existing vs task-introduced)
    - Handling strategies based on failure type
    - Session start procedures with baseline

5. **[Session Recovery](session-recovery.md)**
    - Pending queue reconstruction (critique/audit)
    - Complete session recovery orchestration
    - Recovery summary and reporting

## Recovery Philosophy

The recovery system follows these principles:

1. **Event Log as Source of Truth**: When conflicts occur, the event log is the authoritative record
2. **Fail Safe, Not Silent**: Recovery operations log their actions and outcomes
3. **Backward Compatible**: Unknown event types are logged but don't fail recovery
4. **Baseline Awareness**: Distinguish between inherited problems and newly introduced issues
5. **Automatic Where Possible**: Recover without human intervention when safe to do so

## Recovery Flow

```
Session Start
    ↓
Validate Event Log ────→ Corrupted? ──→ Recover from truncation
    ↓                                          ↓
Validate State File ───→ Corrupted? ──→ Reconstruct from events
    ↓                                          ↓
Validate Plan File ────→ Missing? ────→ HALT (not recoverable)
    ↓                                          ↓
Validate Agent Files ──→ Missing? ────→ Recreate from templates
    ↓                                          ↓
Reconstruct Queues ────→ Restore pending critique/audit tasks
    ↓                                          ↓
Capture/Load Baseline ─→ Track pre-existing failures
    ↓
Continue Session
```

## Cross-References

- [Event Logging](../event-logging.md) - Event structure and logging procedures
- [State Management](../state-management.md) - State schema and persistence
- [Session Management](../session-management.md) - Session lifecycle management
- [Agent Definitions](../agent-definitions.md) - Agent file structure
