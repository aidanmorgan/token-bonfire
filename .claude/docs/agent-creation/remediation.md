# Remediation Agent Creation Prompt

**Output File**: `.claude/agents/remediation.md`
**Runtime Model**: sonnet
**Version**: 2025-01-17-v2

**Required Reading**: [prompt-engineering-guide.md](prompt-engineering-guide.md)

---

## Navigation Index

This document has been split into focused sections for easier navigation and maintenance:

### Core Sections

1. **[Overview and Inputs](remediation/index.md)**
    - Meta-level context
    - Inputs provided by orchestrator
    - Best practices research structure
    - Creation prompt overview
    - Understanding the remediation role

2. **[Identity and Authority](remediation/identity.md)**
    - Frontmatter specification
    - Agent identity (mission-oriented)
    - Failure modes and countermeasures
    - Decision authority framework
    - Pre-signal verification checklist

3. **[Practices and Workflow](remediation/practices.md)**
    - Success criteria (minimum/expected/excellent)
    - Execution environments
    - Remediation practices (diagnosis/fixing/prevention)
    - Common issues and correct approaches
    - Five-phase workflow method

4. **[Signals and Delegation](remediation/signals.md)**
    - Signal formats (REMEDIATION_COMPLETE)
    - Expert awareness (broad but shallow)
    - Expert request format
    - Divine intervention protocol
    - Boundaries and constraints
    - Context management
    - MCP servers

---

## Quick Reference

### Key Principles

The remediation agent is **BROAD BUT SHALLOW** (
see [Agent vs Expert](prompt-engineering-guide.md#agent-vs-expert-the-depth-distinction))—competent at fixing many
infrastructure issues from research, but NOT a domain expert. They must recognize when to delegate.

Remediation is **URGENT**:

- The entire workflow is BLOCKED until infrastructure is fixed
- Every minute spent on broken infrastructure is wasted time
- Work with urgency AND precision

### Critical Rules

**MUST**:

- Diagnose root cause before fixing
- Run ALL verifications in ALL environments
- Apply minimal changes
- Document what changed and why
- Ask experts when stuck

**MUST NOT**:

- Skip or xfail tests
- Add suppressions to linters
- Disable static analysis
- Introduce new features
- Declare victory without ALL verification passing

---

## Cross-References

- **[Documentation Index](../index.md)** - Navigation hub for all docs
- [Prompt Engineering Guide](prompt-engineering-guide.md) - How to write effective prompts
- [Signal Specification](../signal-specification.md) - Remediation signal formats
- [Remediation Loop](../remediation-loop.md) - Infrastructure repair cycle
- [Expert Delegation](../expert-delegation.md) - How to request expert help
- [Escalation Specification](../escalation-specification.md) - Divine intervention
- [MCP Servers](../mcp-servers.md) - Using MCP server capabilities
