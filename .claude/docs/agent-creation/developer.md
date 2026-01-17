# Developer Agent Creation Prompt

**This document has been split into multiple files for better organization.**

## Navigation

The Developer meta-prompt is now organized into the following sections:

1. **[Index & Overview](developer/index.md)**
    - Meta-level context and purpose
    - Inputs provided by orchestrator
    - Best practices research structure
    - Plan context and documentation
    - Creation prompt overview

2. **[Identity & Boundaries](developer/identity.md)**
    - Frontmatter and agent metadata
    - Plan understanding requirements
    - Project conventions
    - Agent identity (mission-oriented)
    - Failure modes and countermeasures
    - Decision authority matrix
    - Pre-signal verification checklist
    - Operational boundaries
    - Context management
    - Coordinator integration

3. **[Practices & Quality](developer/practices.md)**
    - Success criteria (minimum/expected/excellent)
    - Best practices (design, writing, testing)
    - Quality tells (automatic failures)
    - Quality check

4. **[Workflow & Method](developer/workflow.md)**
    - Execution environments
    - Environment execution protocol
    - Verification commands
    - MCP servers
    - Implementation workflow (5 phases)

5. **[Signals & Delegation](developer/signals.md)**
    - Signal formats (READY_FOR_REVIEW, TASK_INCOMPLETE, INFRA_BLOCKED)
    - Expert awareness
    - Expert delegation protocol
    - Divine intervention escalation
    - Cross-references

## Quick Reference

**Output File**: `.claude/agents/developer.md`
**Runtime Model**: sonnet
**Version**: 2025-01-17-v5

## Purpose

This is a META-PROMPT that instructs a prompt-creation sub-agent to write the actual developer agent file. The developer
agent is **BROAD BUT SHALLOW** (
see [Agent vs Expert](prompt-engineering-guide.md#agent-vs-expert-the-depth-distinction))—competent across many
technologies through researched best practices, but not a domain expert.

## Key Sections Required in Generated Agent

The generated developer agent file must include all of these sections:

- `<plan_understanding>` - Context and goals
- `<project_conventions>` - Project-specific standards
- `<agent_identity>` - Mission-oriented identity with stakes
- `<failure_modes>` - How developers fail and countermeasures
- `<decision_authority>` - What to decide vs delegate vs escalate
- `<pre_signal_verification>` - Honest self-check before signaling
- `<success_criteria>` - Three-tier success definition
- `<best_practices>` - Technology-specific guidance (DESIGN/WRITING/TESTING)
- `<quality_tells>` - Automatic failure indicators
- `<environments>` - Execution environment protocols
- `<verification_commands>` - Pre-signal verification requirements
- `<mcp_servers>` - Available MCP capabilities
- `<method>` - Five-phase workflow
- `<signal_format>` - Exact signal formats
- `<expert_awareness>` - Broad-but-shallow nature
- `<expert_delegation>` - How to request expert help
- `<divine_intervention>` - Escalation protocol
- `<boundaries>` - Must/must not rules

## Related Documentation

- [Prompt Engineering Guide](prompt-engineering-guide.md) - Required reading before creating agents
- [Signal Specification](../signal-specification.md) - Developer signal formats
- [Expert Delegation](../expert-delegation.md) - How developers request expert help
- [Agent Conduct](../agent-conduct.md) - Rules all agents must follow
- [Escalation Specification](../escalation-specification.md) - When to escalate
- [MCP Servers](../mcp-servers.md) - Using MCP server capabilities

---

**Start Reading**: [Index & Overview](developer/index.md)
