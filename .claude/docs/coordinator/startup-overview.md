# Coordinator Startup Overview

Session initialization overview and decision logic for the coordinator.

---

## Navigation

- **[Startup Overview](startup-overview.md)** - This file
- [Fresh Start](fresh-start.md) - Fresh session initialization
- [Resume](resume.md) - Resume session procedures
- [Coordinator Configuration](../coordinator-configuration.md) - Configuration values
- [State Management](../state-management.md) - State tracking

---

## Session Initialization

**FIRST: Check for existing state file.** This determines if this is a fresh start or resume.

```
If {{STATE_FILE}} does NOT exist:
    → Fresh start. Proceed to FRESH START.

If {{STATE_FILE}} exists:
    → Resume. Proceed to RESUME FROM STATE.
```

---

## Decision Logic Summary

### Fresh Start Decision Tree

1. **Check Agent and Expert Files**
    - If ANY agent missing → Regenerate ALL (research, experts, agents)
    - If ALL agents exist AND experts exist → Use existing, skip to Plan Discovery
    - If ALL agents exist BUT no experts → Run gap analysis, create experts only

2. **Rationale**
    - Agents are created with plan-specific best practices AND expert list embedded
    - If any agent is missing, regenerate all to ensure expert list is properly embedded

### Resume Decision Tree

1. **Check Agent Files**
    - If ALL agents exist → Use existing agents
    - If ANY agent missing → Regenerate ALL agents AND experts

2. **Handle In-Progress Work**
    - All `in_progress_tasks` → Move back to `available_tasks` (incomplete)
    - All `pending_audit` → Move back to `available_tasks` (audit interrupted)
    - Recent completions → Re-verify (move to `pending_audit`)

3. **Reconcile State**
    - Check if plan file changed
    - Clear stale agent tracking
    - Save updated state

---

## Critical Ordering

**FRESH START**: Experts are created BEFORE agents so agents have the expert list embedded.

```
Research → Gap Analysis → Create Experts → Create Agents (with expert list)
```

---

## Related Documentation

- [Fresh Start](fresh-start.md) - Complete fresh start procedures
- [Resume](resume.md) - Complete resume procedures
- [Coordinator Configuration](../coordinator-configuration.md) - Configuration values
- [State Management](../state-management.md) - State field details
