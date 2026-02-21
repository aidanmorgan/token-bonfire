# Task State Tracking

Track task state using native Agent Teams primitives to coordinate parallel work and resume after interruption.

State is managed via `TaskCreate`/`TaskUpdate`/`TaskList`/`TaskGet` — no custom state files needed.
Communication uses `TeammateTool({ operation: "write", to: "<name>" })` — no custom event logs needed.

See [State Fields](fields.md) for the task list field reference.
See [Signal Specification](../signals/index.md) for the communication message reference.

---

## Navigation

This documentation is split into focused sections:

### Core State Management

- **[State Fields](fields.md)** - All state field definitions organized by category
    - Task tracking (via shared task list)
    - Infrastructure tracking (via team lead context)
    - Expert tracking (via persisted prompt files on disk)
    - File conflict tracking (via mailbox messages)
    - User escalation

- **[Attempt Tracking](attempt-tracking.md)** - Attempt tracking and escalation thresholds
    - Attempt tracking structure
    - Escalation thresholds
    - Persistence across crashes and sessions

### State Operations

- **[Update Triggers](update-triggers.md)** - When and how state updates occur
    - Developer dispatch and completion
    - Critic review complete
    - Ripple review complete
    - Critic timeout handling
    - Auditor pass/fail/blocked
    - Remediation and health audit
    - User escalation
    - Business analyst delegation

- **[Persistence](persistence.md)** - Native tool state persistence
    - Shared task list persistence
    - Expert prompt files on disk
    - Resume via plan slug

### Task Management

- **[Task Tracking](task-tracking.md)** - Task selection, rollback, and developer tracking
    - Task selection priority
    - Rollback capability
    - Learning from failures
    - Parallel developer tracking

---

## Related Documentation

- [State Fields](fields.md) - Task list field reference
- [Signal Specification](../signals/index.md) - Communication message reference
- [Recovery Procedures](../recovery/index.md) - Error recovery
- [Team Architecture](../team-architecture.md) - Team structure and lifecycle
