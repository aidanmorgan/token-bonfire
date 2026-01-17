# Signal Parsing Reference

Implementation details for signal detection, parsing, and handling.

---

## Signal Parsing Reference

```python
SIGNAL_PATTERNS = {
    # Developer signals
    'ready_for_review': re.compile(r'^READY_FOR_REVIEW:\s*(\S+)', re.MULTILINE),
    'task_incomplete': re.compile(r'^TASK_INCOMPLETE:\s*(\S+)', re.MULTILINE),
    'infra_blocked': re.compile(r'^INFRA_BLOCKED:\s*(\S+)', re.MULTILINE),

    # Critic signals
    'review_passed': re.compile(r'^REVIEW_PASSED:\s*(\S+)', re.MULTILINE),
    'review_failed': re.compile(r'^REVIEW_FAILED:\s*(\S+)', re.MULTILINE),

    # Auditor signals
    'audit_passed': re.compile(r'^AUDIT_PASSED:\s*(\S+)', re.MULTILINE),
    'audit_failed': re.compile(r'^AUDIT_FAILED:\s*(\S+)', re.MULTILINE),
    'audit_blocked': re.compile(r'^AUDIT_BLOCKED:\s*(\S+)', re.MULTILINE),

    # BA signals
    'expanded_spec': re.compile(r'^EXPANDED_TASK_SPECIFICATION:\s*(\S+)', re.MULTILINE),

    # Remediation signals
    'remediation_complete': re.compile(r'^REMEDIATION_COMPLETE$', re.MULTILINE),

    # Health auditor signals
    'health_healthy': re.compile(r'^HEALTH_AUDIT: HEALTHY$', re.MULTILINE),
    'health_unhealthy': re.compile(r'^HEALTH_AUDIT: UNHEALTHY$', re.MULTILINE),

    # Escalation signals
    'divine_clarification': re.compile(r'^SEEKING_DIVINE_CLARIFICATION$', re.MULTILINE),

    # Expert signals
    'expert_request': re.compile(r'^EXPERT_REQUEST$', re.MULTILINE),
    'expert_advice': re.compile(r'^EXPERT_ADVICE:\s*(\S+)', re.MULTILINE),
    'expert_unsuccessful': re.compile(r'^EXPERT_UNSUCCESSFUL:\s*(\S+)', re.MULTILINE),
    'expert_created': re.compile(r'^EXPERT_CREATED:\s*(\S+)', re.MULTILINE),

    # Concurrency signals
    'file_conflict': re.compile(r'^FILE CONFLICT:\s*(\S+)', re.MULTILINE),

    # Checkpoint signals
    'checkpoint': re.compile(r'^CHECKPOINT:\s*(\S+)', re.MULTILINE),
}


# Signal to handler action mapping
SIGNAL_HANDLERS = {
    # Developer signals
    'ready_for_review': 'DISPATCH_CRITIC',
    'task_incomplete': 'LOG_AND_FILL_SLOTS',
    'infra_blocked': 'ENTER_REMEDIATION',

    # Critic signals
    'review_passed': 'DISPATCH_AUDITOR',
    'review_failed': 'DISPATCH_DEVELOPER_REWORK',

    # Auditor signals
    'audit_passed': 'MARK_COMPLETE',
    'audit_failed': 'DISPATCH_DEVELOPER_REWORK',
    'audit_blocked': 'ENTER_REMEDIATION',

    # BA signals
    'expanded_spec': 'PROCESS_EXPANSION',

    # Remediation signals
    'remediation_complete': 'DISPATCH_HEALTH_AUDITOR',
    'health_healthy': 'EXIT_REMEDIATION',
    'health_unhealthy': 'RETRY_REMEDIATION',

    # Escalation signals
    'divine_clarification': 'AWAIT_DIVINE_RESPONSE',

    # Expert signals
    'expert_request': 'DISPATCH_EXPERT',
    'expert_advice': 'DELIVER_TO_REQUESTING_AGENT',
    'expert_unsuccessful': 'ESCALATE_TO_DIVINE',
    'expert_created': 'REGISTER_EXPERT',

    # Concurrency signals
    'file_conflict': 'QUEUE_OR_COORDINATE',

    # Checkpoint signals
    'checkpoint': 'PROCESS_CHECKPOINT',

    # Unknown/malformed signal recovery
    'unknown': 'REQUEST_CLARIFICATION',
}


def parse_signal(agent_output: str) -> dict:
    """Parse agent output for signals. Returns signal info with handler action."""
    for signal_type, pattern in SIGNAL_PATTERNS.items():
        match = pattern.search(agent_output)
        if match:
            return {
                'signal': signal_type,
                'task_id': match.group(1) if match.lastindex else None,
                'handler': SIGNAL_HANDLERS.get(signal_type, 'UNKNOWN'),
                'raw_output': agent_output
            }
    return {'signal': 'unknown', 'handler': 'REQUEST_CLARIFICATION', 'raw_output': agent_output}
```

---

## Unknown Signal Handling

When `parse_signal()` returns `'unknown'`, the coordinator MUST NOT ignore it. Unknown signals indicate either:

- Agent produced malformed output
- Agent is confused about expected signal format
- New signal type not yet in patterns

**Handler: REQUEST_CLARIFICATION**

```python
def handle_unknown_signal(task_id, agent_id, raw_output):
    """Handle unrecognized agent output to prevent system halt."""

    unknown_signal_count[task_id] = unknown_signal_count.get(task_id, 0) + 1

    if unknown_signal_count[task_id] >= 3:
        # Agent consistently produces invalid signals - escalate
        log_event("agent_signal_failure", task_id=task_id, agent_id=agent_id,
                  reason="3_consecutive_unknown_signals")

        # Treat as agent timeout - re-dispatch with explicit signal instructions
        handle_agent_timeout(task_id, agent_id,
                             context="Agent produced 3 unrecognized signals. "
                                     "Re-dispatching with explicit format requirements.")
        unknown_signal_count[task_id] = 0
        return

    # Request checkpoint to verify agent is responsive
    request_checkpoint(task_id)

    # If checkpoint received within timeout: request signal re-send
    # If no checkpoint: treat as agent timeout
    log_event("unknown_signal_recovery", task_id=task_id,
              attempt=unknown_signal_count[task_id],
              output_preview=raw_output[:200])
```

**Recovery Path**:

1. First unknown signal → request checkpoint, log warning
2. Second unknown signal → request checkpoint, log error
3. Third unknown signal → treat as agent failure, re-dispatch task

---

## Related Documentation

- [Signal Index](index.md) - Overview and detection rules
- [Workflow Signals](workflow-signals.md) - Developer, Critic, Auditor signals
- [Supporting Signals](supporting-signals.md) - BA, Remediation, Health Auditor signals
- [Coordination Signals](coordination-signals.md) - Escalation, Expert, Concurrency, Checkpoint signals
- [Task Delivery Loop](../task-delivery-loop.md) - Signal handling procedures
- [State Management](../state-management.md) - State tracking integration
