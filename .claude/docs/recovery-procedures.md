# Recovery Procedures

**This documentation lives in the `recovery/` subdirectory.**

See **[Recovery System Overview](recovery/index.md)** for the complete documentation:

- [Event Log Recovery](recovery/event-log-recovery.md) - Corruption detection, state reconstruction
- [State Recovery](recovery/state-recovery.md) - State file recovery
- [Agent Recovery](recovery/agent-recovery.md) - Missing agent files
- [Baseline Failures](recovery/baseline-failures.md) - Pre-existing failure handling
- [Session Recovery](recovery/session-recovery.md) - Complete session recovery orchestration

---

## Recovery Philosophy

1. **Event Log as Source of Truth**: When conflicts occur, the event log is authoritative
2. **Fail Safe, Not Silent**: Recovery operations log their actions and outcomes
3. **Automatic Where Possible**: Recover without human intervention when safe

---

## Related Documentation

- [Event Logging](event-logging.md) - Event structure and logging procedures
- [State Management](state-management.md) - State schema and persistence
- [Session Management](session-management.md) - Session lifecycle management
