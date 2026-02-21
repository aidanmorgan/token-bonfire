# Recovery System Overview

This directory contains recovery procedures for handling various failure scenarios in the Token Bonfire coordination system.

## Purpose

Recovery in the native Agent Teams system is largely automatic because:
- The **shared task list** persists on disk, keyed by plan slug
- **Expert prompt files** persist at `.claude/experts/<plan_slug>/`
- **Dependencies auto-unblock** when blocking tasks complete
- **Orphaned in-progress tasks** auto-release after heartbeat timeout (~5 min)

The recovery system ensures the team lead can gracefully handle:
- Session interruptions and restarts
- Missing expert prompt files
- Pre-existing infrastructure failures
- Crashed teammates

## Recovery Documents

### Core Recovery Procedures

1. **[Task List Recovery](state-recovery.md)**
    - Auditing task state on resume
    - Handling orphaned in-progress tasks
    - Verifying completed tasks

2. **[Agent Recovery](agent-file-recovery.md)**
    - Missing expert prompt files
    - Plan file validation
    - Expert regeneration when needed

### Failure Management

3. **[Baseline Failures](baseline-failures.md)**
    - Pre-existing failure baseline capture
    - Classification of failures (pre-existing vs task-introduced)
    - Handling strategies based on failure type

4. **[Session Recovery](session-recovery.md)**
    - Complete session recovery orchestration
    - Resume detection and mode selection
    - Recovery summary and reporting

## Recovery Philosophy

The recovery system follows these principles:

1. **Task List as Source of Truth**: The native shared task list (keyed by plan slug) is the authoritative record
2. **Expert Files as Knowledge Store**: Persisted expert prompts at `.claude/experts/<plan_slug>/` preserve domain research
3. **Automatic Resume**: Re-running `/bonfire $PLAN_FILE` produces the same slug, loads existing state
4. **Fail Safe, Not Silent**: Recovery operations report their findings to the user
5. **Baseline Awareness**: Distinguish between inherited problems and newly introduced issues

## Recovery Flow

```
Resume (re-run /bonfire $PLAN_FILE)
    |
    v
Parse plan -> same plan_slug
    |
    v
Check expert files on disk -> Missing? -> Regenerate from plan
    |                                          |
    v                                          v
Call TaskList -> Audit task state         Generate expert prompts
    |                                          |
    v                                          v
Spawn fresh teammates from prompts       Create tasks if needed
    |
    v
Experts claim pending tasks
    |
    v
Orphaned in-progress tasks auto-release (~5 min)
    |
    v
Continue execution
```

## Cross-References

- [Communication Protocol](../communication-protocol.md) - Inter-agent messaging
- [State Management](../state/index.md) - Task state tracking
- [Session Management](../session-management.md) - Session lifecycle
- [Team Architecture](../team-architecture.md) - Resume and crash recovery details
