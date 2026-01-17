# Health Auditor Agent Creation Prompt

**Navigation Index**

This meta-prompt has been split into focused sections for better organization and navigation.

---

## Table of Contents

### 1. [Overview and Inputs](health-auditor/index.md)

- Inputs provided by orchestrator
- Best practices research structure
- Creation prompt frontmatter

### 2. [Identity and Authority](health-auditor/identity.md)

- Agent identity and stakes
- Common failure modes
- Decision authority (decide/consult/escalate)
- Pre-signal verification checklist
- Success criteria
- Expert awareness and limitations

### 3. [Procedures and Signals](health-auditor/procedures.md)

- Health practices template
- Health validation criteria (HEALTHY vs UNHEALTHY)
- Audit method (3 phases)
- Boundaries and constraints
- MCP servers integration
- Expert request format
- Signal formats (HEALTHY/UNHEALTHY)
- Quality checklist

---

## Quick Reference

**Output File**: `.claude/agents/health-auditor.md`
**Runtime Model**: haiku
**Version**: 2025-01-17-v2

**Core Principle**: Independent verification - trust nothing, verify everything.

**Signal Types**:

- `HEALTH_AUDIT: HEALTHY` - All verifications pass
- `HEALTH_AUDIT: UNHEALTHY` - Any verification fails

---

## Cross-References

- **[Documentation Index](../index.md)** - Navigation hub for all docs
- [Prompt Engineering Guide](prompt-engineering-guide.md) - Quality standards
- [Signal Specification](../signal-specification.md) - Health audit signal formats
- [Infrastructure Remediation](../infrastructure-remediation.md) - When health audit is triggered
- [Remediation Loop](../remediation-loop.md) - Health audit role in the loop
- [Expert Delegation](../expert-delegation.md) - How to request expert help
- [MCP Servers](../mcp-servers.md) - Using MCP server capabilities
