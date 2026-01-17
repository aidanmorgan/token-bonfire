# Critic Agent Creation Meta-Prompt

**Output File**: `.claude/agents/critic.md`
**Runtime Model**: sonnet
**Version**: 2025-01-17-v5

---

## Document Organization

This meta-prompt has been split into focused documents for easier navigation and maintenance:

### 1. [Overview & Inputs](critic/index.md)

**Lines 1-141 of original**

- Meta-level context: what this document is
- Orchestrator's role in critic creation
- Inputs provided by orchestrator
- Best practices research structure
- Plan context and project documentation

### 2. [Identity & Authority](critic/identity.md)

**Lines 142-417 of original**

- Creation prompt and mission
- Agent identity (mission-oriented)
- Failure modes and countermeasures
- Decision authority (decide/consult/escalate)
- Pre-signal verification checklist
- Success criteria (minimum/expected/excellent)

### 3. [Review Criteria & Method](critic/review-criteria.md)

**Lines 418-617 of original**

- Review criteria (QUALITY/ARCHITECTURE/DETECTION)
- Quality tells (automatic fail indicators)
- What to critique
- Review methodology and workflow
- Calibration examples

### 4. [Signals & Delegation](critic/signals.md)

**Lines 618-964 of original**

- Signal formats (REVIEW_PASSED, REVIEW_FAILED)
- Expert awareness (broad but shallow)
- Expert delegation protocol
- Divine intervention escalation
- Boundaries and context management
- Coordinator integration
- MCP servers

---

## Quick Reference

### For Orchestrator Implementers

Start with [Overview & Inputs](critic/index.md) to understand what data the orchestrator must provide.

### For Prompt Engineers

Read [Identity & Authority](critic/identity.md) to understand the mission-oriented approach,
then [Review Criteria](critic/review-criteria.md) for how to transform research into checkable criteria.

### For System Architects

See [Signals & Delegation](critic/signals.md) for integration patterns and signal formats.

---

## Key Concepts

**Broad But Shallow**: Critics are competent across many technologies but delegate to experts for domain depth.

**Integration Verification**: Code must be wired into the system, not just written in isolation.

**Mission-Oriented**: Critics believe they're reviewing junior developer code, ensuring thorough feedback.

**Three Dimensions**: Every review checks QUALITY, ARCHITECTURE, and DETECTION.

---

## Cross-References

- **[Documentation Index](../index.md)** - Navigation hub for all docs
- [Prompt Engineering Guide](prompt-engineering-guide.md) - How to write effective prompts
- [Signal Specification](../signal-specification.md) - Critic signal formats
- [Review Audit Flow](../review-audit-flow.md) - Critic's role in the workflow
- [Expert Delegation](../expert-delegation.md) - How critics request expert help
- [Agent Conduct](../agent-conduct.md) - Rules all agents must follow
- [MCP Servers](../mcp-servers.md) - Using MCP server capabilities
