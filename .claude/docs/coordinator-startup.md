# Coordinator Startup - Navigation Index

Session initialization procedures for fresh starts and resumes.

---

## Overview

The coordinator startup procedures have been split into focused documents for easier navigation and maintenance.

**Start here:** [Startup Overview](coordinator/startup-overview.md) - Understand the decision logic and initialization
flow.

---

## Startup Documentation

### [Startup Overview](coordinator/startup-overview.md)

Overview and decision logic for session initialization.

- Session initialization decision tree
- Fresh start vs resume logic
- Critical ordering requirements

### [Fresh Start](coordinator/fresh-start.md)

Fresh session initialization when no state file exists.

- Plan directory creation
- Session ID generation
- Agent and expert file checking
- Research best practices
- Gap analysis and expert creation
- Agent file creation with expert awareness
- Plan discovery and task assessment

### [Resume](coordinator/resume.md)

Resume session procedures when state file exists.

- State file loading
- Session ID generation for resume
- Agent file verification
- In-progress task handling
- Pending audit task handling
- Recent completion re-verification
- State reconciliation with plan

---

## Related Documentation

- [Coordinator Configuration](coordinator-configuration.md) - Configuration values
- [State Management](state-management.md) - State tracking
- [Task Quality](task-quality.md) - Task assessment
- [Recovery Procedures](recovery-procedures.md) - Error recovery
- [Agent Creation Guide](agent-creation/prompt-engineering-guide.md) - Agent creation standards
