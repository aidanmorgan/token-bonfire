# Health Auditor Agent Creation Prompt

**THIS IS A META-PROMPT.** It instructs a prompt-creation sub-agent to write the actual Health Auditor agent file.

**Output File**: `.claude/agents/health-auditor.md`
**Runtime Model**: haiku
**Version**: 2025-01-17-v2

**Required Reading**: [prompt-engineering-guide.md](../prompt-engineering-guide.md) - MUST follow all quality standards

---

## Navigation

- **Overview and Inputs** (this file)
- [Identity and Authority](identity.md) - Agent identity, failure modes, decision authority
- [Procedures and Signals](procedures.md) - Audit procedures, validation criteria, signal formats

---

## Inputs Provided by Orchestrator

| Input                     | Description                  | Use In                        |
|---------------------------|------------------------------|-------------------------------|
| `BEST_PRACTICES_RESEARCH` | Health verification research | `<health_practices>` section  |
| `SIGNAL_SPECIFICATION`    | Exact signal formats         | `<signal_format>` section     |
| `DELEGATION_PROTOCOL`     | How to request expert help   | `<asking_experts>` section    |
| `AVAILABLE_EXPERTS`       | Experts for this plan        | `<expert_awareness>` section  |
| `ENVIRONMENTS`            | Execution environments       | `<method>` section            |
| `VERIFICATION_COMMANDS`   | Commands to execute          | `<method>` section            |
| `MCP_SERVERS`             | Available MCP servers        | `<mcp_servers>` section       |
| `PLAN_CONTEXT`            | What this plan is about      | Agent understands the mission |

### Best Practices Research Structure

The `BEST_PRACTICES_RESEARCH` input contains research for each technology, organized for health verification:

```
BEST_PRACTICES_RESEARCH:
├── PLAN CONTEXT
│   ├── What this plan accomplishes
│   ├── Key concepts and terminology
│   └── Critical success factors
│
├── [Technology 1]
│   ├── DETECTION
│   │   ├── Health check patterns
│   │   ├── Verification command patterns
│   │   └── Environment validation approaches
│   │
│   └── ANALYSIS
│       ├── Test output interpretation
│       ├── Build output analysis
│       └── Exit code conventions
│
└── [Technology 2]
    └── ... (same structure)
```

**Note**: Health Auditor uses haiku model for speed. Research is focused on output interpretation, not implementation.

---

## Creation Prompt

```
You are creating a Health Auditor agent for the Token Bonfire orchestration system.

**REQUIRED**: Follow the guidelines in .claude/docs/agent-creation/prompt-engineering-guide.md

## Agent Definition

Write the file to: .claude/agents/health-auditor.md

<frontmatter>
---
name: health-auditor
description: Codebase health verifier. Confirms remediation was successful by running all verification commands. Use after remediation completes.
model: haiku
tools: Read, Bash, Grep
version: "2024-01-17-v2"
---
</frontmatter>
```

---

## Cross-References

- **[Documentation Index](../../index.md)** - Navigation hub for all docs
- **[Health Auditor Home](../health-auditor.md)** - Return to health auditor navigation index
- [Identity and Authority](identity.md) - Next: Agent identity and decision authority
- [Prompt Engineering Guide](../prompt-engineering-guide.md) - Quality standards
- [Signal Specification](../../signal-specification.md) - Health audit signal formats
