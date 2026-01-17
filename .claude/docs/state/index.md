# Coordinator State Tracking

Track these fields to coordinate parallel work and resume after interruption.

See [State Schema](../orchestrator/state-schema.md) for complete state file format.
See [Event Schema](../orchestrator/event-schema.md) for event log format.

---

## Navigation

This documentation is split into focused sections:

### Core State Management

- **[State Fields](fields.md)** - All state field definitions organized by category
    - Session tracking
    - Task tracking
    - Infrastructure tracking
    - Expert tracking
    - File conflict tracking
    - Divine intervention

- **[Attempt Tracking](attempt-tracking.md)** - Attempt tracking and escalation thresholds
    - Attempt tracking structure
    - Escalation thresholds
    - Persistence across crashes and sessions

### State Operations

- **[Update Triggers](update-triggers.md)** - When and how state updates occur
    - Developer dispatch and completion
    - Critic review complete
    - Critic timeout handling
    - Auditor pass/fail/blocked
    - Remediation and health audit
    - Divine intervention
    - Expert delegation

- **[Persistence](persistence.md)** - Atomic updates and recovery
    - Atomic write procedures
    - Recovery on resume
    - State file guarantees

### Task Management

- **[Task Tracking](task-tracking.md)** - Task selection, rollback, and agent tracking
    - Task selection priority
    - Rollback capability
    - Learning from failures
    - Parallel agent tracking
    - Slot management

---

## Related Documentation

- [State Schema](../orchestrator/state-schema.md) - Complete state file format
- [Event Schema](../orchestrator/event-schema.md) - Event log format
- [Recovery Procedures](../recovery-procedures.md) - Error recovery
- [Task Delivery Loop](../task-delivery-loop.md) - Main execution loop
