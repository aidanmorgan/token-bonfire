# Attempt Tracking

[← Back to State Management](index.md)

Track attempts across agent crashes and session restarts to enforce escalation paths.

---

## Attempt Tracking Structure

```json
{
  "task_attempts": {
    "task-3-1-1": {
      "self_solve_attempts": 2,
      "delegation_attempts": 1,
      "audit_failures": 1,
      "critic_failures": 0,
      "critic_timeouts": 0,
      "incomplete_count": 0,
      "signal_rejections": 1,
      "last_attempt_at": "2025-01-16T10:30:00Z",
      "escalation_level": "delegation",
      "last_blocker": null,
      "history": [...]
    }
  }
}
```

## Escalation Thresholds

| Attempt Type          | Threshold | Escalation Action                      |
|-----------------------|-----------|----------------------------------------|
| `self_solve_attempts` | 3         | Escalate to delegation                 |
| `delegation_attempts` | 3         | Escalate to divine intervention        |
| `audit_failures`      | 3         | Halt task, require human review        |
| `critic_failures`     | 3         | Halt task, require human review        |
| `critic_timeouts`     | 3         | Re-dispatch critic with same task      |
| `incomplete_count`    | 3         | Escalate to divine intervention        |
| `signal_rejections`   | 5         | Notify coordinator of persistent issue |

---

## Related Documentation

- [State Fields](fields.md) - All state field definitions
- [Update Triggers](update-triggers.md) - When attempt counts are incremented
- [Escalation Specification](../escalation-specification.md) - Detailed escalation rules
