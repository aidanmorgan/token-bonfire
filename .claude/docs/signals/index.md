# Signal Specification - Overview

All agent-to-coordinator signals are defined in this directory. **This is the single source of truth.**

## Workflow Overview

```
Developer → READY_FOR_REVIEW → Critic → REVIEW_PASSED → Auditor → AUDIT_PASSED → Complete
                                    ↓                        ↓
                              REVIEW_FAILED             AUDIT_FAILED
                                    ↓                        ↓
                              (back to Developer)    (back to Developer)
```

## Signal Detection Rules

| Rule               | Requirement                        | Example                                |
|--------------------|------------------------------------|----------------------------------------|
| Line position      | Signal MUST start at column 0      | `READY_FOR_REVIEW: task-1` (correct)   |
| Signal name        | Use EXACT name from this spec      | `AUDIT_PASSED` not `Audit Passed`      |
| Separator          | Use colon and space after signal   | `READY_FOR_REVIEW: task-1`             |
| Placement          | Signal at END of response          | After all explanatory text             |
| No false positives | Don't use signal keywords in prose | Don't write "this is READY_FOR_REVIEW" |

## Signal Categories

### Why Three Categories?

Signals are grouped by their role in the system:

| Category         | Purpose                                               | When Used                                                           |
|------------------|-------------------------------------------------------|---------------------------------------------------------------------|
| **Workflow**     | Move tasks through Developer → Critic → Auditor chain | Main development flow                                               |
| **Supporting**   | Auxiliary processes that feed into workflow           | Task expansion, infrastructure repair, health checks                |
| **Coordination** | Meta-concerns about the system itself                 | Expert delegation, human escalation, concurrency, progress tracking |

**The distinction**: Workflow signals advance tasks toward completion. Supporting signals prepare or repair the
environment. Coordination signals manage how agents work together.

### Workflow Signals

Primary signals for the main development workflow.

- [Developer Signals](workflow-signals.md#developer-signals) - READY_FOR_REVIEW, TASK_INCOMPLETE, INFRA_BLOCKED
- [Critic Signals](workflow-signals.md#critic-signals) - REVIEW_PASSED, REVIEW_FAILED
- [Auditor Signals](workflow-signals.md#auditor-signals) - AUDIT_PASSED, AUDIT_FAILED, AUDIT_BLOCKED

### Supporting Signals

Signals for supporting agents and processes.

- [Business Analyst Signals](supporting-signals.md#business-analyst-signals) - EXPANDED_TASK_SPECIFICATION
- [Remediation Signals](supporting-signals.md#remediation-signals) - REMEDIATION_COMPLETE
- [Health Auditor Signals](supporting-signals.md#health-auditor-signals) - HEALTH_AUDIT

### Coordination Signals

Signals for system coordination and expert delegation.

- [Escalation Signals](coordination-signals.md#escalation-signals) - SEEKING_DIVINE_CLARIFICATION, EXPERT_REQUEST
- [Expert Signals](coordination-signals.md#expert-signals) - EXPERT_ADVICE, EXPERT_UNSUCCESSFUL, EXPERT_CREATED
- [Concurrency Signals](coordination-signals.md#concurrency-signals) - FILE CONFLICT
- [Checkpoint Signals](coordination-signals.md#checkpoint-signals) - CHECKPOINT

### Signal Parsing

Implementation details for signal detection and handling.

- [Signal Parsing Reference](parsing.md) - Regex patterns, handlers, and unknown signal handling

## Signal Priority

When multiple signals could apply, use this priority:

1. `INFRA_BLOCKED` / `AUDIT_BLOCKED` - Infrastructure issues take precedence
2. `SEEKING_DIVINE_CLARIFICATION` - Human escalation
3. `EXPERT_REQUEST` - Expert consultation
4. `FILE CONFLICT` - Concurrency management
5. Primary workflow signals (`READY_FOR_REVIEW`, `REVIEW_PASSED`, `AUDIT_PASSED`, etc.)

## Related Documentation

- Signal handling procedures: [task-delivery-loop.md](../task-delivery-loop.md)
- Expert delegation: [expert-delegation.md](../expert-delegation.md)
- State management: [state-management.md](../state-management.md)
