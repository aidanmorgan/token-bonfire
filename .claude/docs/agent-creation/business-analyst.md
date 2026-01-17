# Business Analyst Agent - Navigation

This document has been split into focused sections for better organization and readability.

---

## Sections

### [1. Overview and Inputs](business-analyst/index.md)

**Lines 1-150 of original document**

Key topics:

- Meta-prompt overview
- Orchestrator inputs (BEST_PRACTICES_RESEARCH, SIGNAL_SPECIFICATION, etc.)
- Best practices research structure
- Agent frontmatter and identity
- The stakes of specification quality
- Authority boundaries

Start here to understand:

- What inputs the Business Analyst receives
- How the agent is created
- The agent's core identity and mission

---

### [2. Identity and Authority](business-analyst/identity.md)

**Lines 151-300 of original document**

Key topics:

- Common failure modes and countermeasures
- Decision authority matrix (decide/consult/escalate)
- Pre-signal verification checklists
- Success criteria (minimum/expected/excellent)
- Analysis practices template structure

Start here to understand:

- How the Business Analyst should make decisions
- What mistakes to avoid
- How to verify work quality before signaling

---

### [3. Task Expansion Process and Signals](business-analyst/expansion.md)

**Lines 301-555 of original document**

Key topics:

- 5-phase expansion method
- Boundaries (MUST and MUST NOT)
- Context management and checkpointing
- MCP server integration
- Expert awareness and delegation
- Escalation protocol
- Signal formats (EXPANDED_TASK_SPECIFICATION, SEEKING_DIVINE_CLARIFICATION)
- Expert request format
- Quality checklist

Start here to understand:

- How the Business Analyst performs task expansion
- When and how to ask experts
- How to signal completion or request help
- Complete signal format specifications

---

## Quick Reference

### Common Tasks

| I need to...                           | Go to...                                                                       |
|----------------------------------------|--------------------------------------------------------------------------------|
| Understand what inputs the BA receives | [Overview and Inputs](business-analyst/index.md)                               |
| Know when to escalate vs. decide       | [Identity and Authority](business-analyst/identity.md#decision-authority)      |
| See the expansion method phases        | [Task Expansion Process](business-analyst/expansion.md#method)                 |
| Find signal formats                    | [Task Expansion Process](business-analyst/expansion.md#signal-format)          |
| Learn about expert delegation          | [Task Expansion Process](business-analyst/expansion.md#expert-awareness)       |
| Check quality before signaling         | [Identity and Authority](business-analyst/identity.md#pre-signal-verification) |

---

## Document Organization

This split follows the natural flow of the Business Analyst creation process:

1. **Index** - What the agent receives and its core identity
2. **Identity** - How the agent should think and decide
3. **Expansion** - What the agent does and how it signals

Each file:

- Includes navigation links to other sections
- Preserves all templates and signal formats exactly
- Contains headers for easy scanning
- Cross-references related documentation

---

## Related Documentation

- **[Documentation Index](../index.md)** - Navigation hub for all docs
- [Prompt Engineering Guide](prompt-engineering-guide.md) - Quality standards for all agents
- [Signal Specification](../signal-specification.md) - Complete signal format reference
- [Escalation Specification](../escalation-specification.md) - When and how to escalate
- [Expert Delegation](../expert-delegation.md) - How to request expert help

---

**Version**: 2025-01-17-v2
**Last Updated**: Split from monolithic file for better organization
