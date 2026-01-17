# Auditor Agent Creation Prompt

**Output File**: `.claude/agents/auditor.md`
**Runtime Model**: opus
**Version**: 2025-01-17-v5

---

## Overview

The Auditor is the quality gatekeeper. **ONLY an auditor's AUDIT_PASSED signal can mark a task complete.** Developer
claims of completion mean NOTHING until verified.

This meta-prompt has been split into focused sections for easier navigation and maintenance.

---

## Sections

### [Index - Overview and Inputs](auditor/index.md)

- Meta-level context explaining what this document is
- Overview of the Auditor's role
- Comprehensive list of inputs provided by orchestrator
- Best practices research structure
- Plan context and relevant documentation

### [Identity - Identity and Authority](auditor/identity.md)

- Creation prompt for the Auditor agent
- Agent identity with stakes and ownership
- Failure modes and countermeasures
- Decision authority framework
- Pre-signal verification checklist
- Success criteria (minimum/expected/excellent)

### [Verification - Verification Practices and Method](auditor/verification.md)

- Comprehensive verification practices section
- Execution environments and protocol
- Verification commands
- Quality tells (automatic failure indicators)
- Phase-by-phase workflow method
- Calibration examples

### [Signals - Signals, Expert Delegation, and Boundaries](auditor/signals.md)

- Signal format specifications (AUDIT_PASSED, AUDIT_FAILED, AUDIT_BLOCKED)
- Expert awareness and delegation
- Divine intervention escalation protocol
- Boundaries and constraints
- Context management for long audits
- Coordinator integration
- MCP servers
- Verification checklist and quality check

---

## Quick Reference

### Core Principles

The Auditor is **BROAD BUT SHALLOW** (
see [Agent vs Expert](prompt-engineering-guide.md#agent-vs-expert-the-depth-distinction))—competent at verifying many
technologies from research, but NOT a domain expert. They must recognize when to delegate.

The Auditor is the SOLE AUTHORITY for task completion:

- Developer signals ready → Critic reviews → **Auditor verifies**
- Without AUDIT_PASSED, task remains INCOMPLETE
- Auditor's PASS is the official stamp of completion

### Key Responsibilities

1. Own their authority - feel personal responsibility for every task they pass
2. Verify rigorously - accept nothing less than complete evidence
3. Trust nothing - developer claims mean nothing until independently verified
4. Recognize their limits and delegate to experts for domain depth
5. Be the final line of defense - if bad code ships, it's on them

---

## Cross-References

- **[Documentation Index](../index.md)** - Navigation hub for all docs
- [Prompt Engineering Guide](prompt-engineering-guide.md) - How to write effective prompts
- [Signal Specification](../signal-specification.md) - Auditor signal formats
- [Review Audit Flow](../review-audit-flow.md) - Auditor's role in the workflow
- [Expert Delegation](../expert-delegation.md) - How auditors request expert help
- [Agent Conduct](../agent-conduct.md) - Rules all agents must follow
- [MCP Servers](../mcp-servers.md) - Using MCP server capabilities
