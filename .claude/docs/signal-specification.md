# Signal Specification

**This document has been reorganized for better navigation.**

The signal specification has been split into focused documents in the `signals/` subdirectory:

## Quick Links

- **[Signal Overview & Index](signals/index.md)** - Start here for an overview of all signals and detection rules

### Signal Categories

- **[Workflow Signals](signals/workflow-signals.md)** - Developer, Critic, and Auditor signals for the main workflow
    - READY_FOR_REVIEW, TASK_INCOMPLETE, INFRA_BLOCKED
    - REVIEW_PASSED, REVIEW_FAILED
    - AUDIT_PASSED, AUDIT_FAILED, AUDIT_BLOCKED

- **[Supporting Signals](signals/supporting-signals.md)** - Business Analyst, Remediation, and Health Auditor signals
    - EXPANDED_TASK_SPECIFICATION
    - REMEDIATION_COMPLETE
    - HEALTH_AUDIT: HEALTHY, HEALTH_AUDIT: UNHEALTHY

- **[Coordination Signals](signals/coordination-signals.md)** - Escalation, Expert, Concurrency, and Checkpoint signals
    - SEEKING_DIVINE_CLARIFICATION, EXPERT_REQUEST
    - EXPERT_ADVICE, EXPERT_UNSUCCESSFUL, EXPERT_CREATED
    - FILE CONFLICT
    - CHECKPOINT

- **[Signal Parsing Reference](signals/parsing.md)** - Implementation details, regex patterns, handlers, and unknown
  signal handling

## Workflow Overview

```
Developer → READY_FOR_REVIEW → Critic → REVIEW_PASSED → Auditor → AUDIT_PASSED → Complete
                                    ↓                        ↓
                              REVIEW_FAILED             AUDIT_FAILED
                                    ↓                        ↓
                              (back to Developer)    (back to Developer)
```

## Related Documentation

- [Task Delivery Loop](task-delivery-loop.md) - Signal handling procedures
- [Expert Delegation](expert-delegation.md) - Expert system details
- [State Management](state-management.md) - State tracking integration
