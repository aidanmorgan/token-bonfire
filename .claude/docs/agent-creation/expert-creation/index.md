# Expert Creation - Overview

**THIS IS A META-PROMPT.** It instructs a prompt-creation sub-agent to write expert agent files.

**Purpose**: Create expert agents that fill gaps identified from plan analysis
**Runtime Model**: opus (for creation)
**Version**: 2025-01-17-v5

**Required Reading**: [prompt-engineering-guide.md](../prompt-engineering-guide.md) - MUST follow all quality standards

---

## What This Documentation Is

Orchestrator analyzes the plan for gaps, researches the domain, substitutes variables, and spawns a prompt-creation
sub-agent. The sub-agent (you) receives gap analysis and research, then writes the expert agent file to
`.claude/agents/experts/[expert-name].md`. Expert agents provide specialist advice, signal EXPERT_ADVICE or
EXPERT_UNSUCCESSFUL, and CANNOT delegate further.

**YOUR RESPONSIBILITY**: The file you write MUST be complete and self-contained. An expert spawned with that file must
know EXACTLY:

- What expertise they provide and for which tasks
- How to give **AUTHORITATIVE, ACTIONABLE** advice (not suggestions or options)
- What signals to emit and in what format
- That they CANNOT delegate (they are the last resort before divine intervention)
- How default agents will request their help

---

## Documentation Structure

This expert creation guide is organized into focused documents:

### 1. [Types](types.md) - Expert Types and Core Concepts

- Three types of experts: Domain, Reference, and Left-Field
- Methodology experts for project-specific procedural knowledge
- Key principles: narrower but deeper expertise
- Responsibility split between orchestrator, default agents, and experts

### 2. [Gap Analysis](gap-analysis.md) - Identifying Where Experts Are Needed

- Gap analysis process the orchestrator performs
- Identifying expertise gaps, decision points, and verification gaps
- Determining which experts to create

### 3. [Inputs](inputs.md) - Research and Inputs for Expert Creation

- Inputs provided by orchestrator
- Deep domain research requirements
- Research process and existing expert prompt analysis

### 4. [Prompt Structure](prompt-structure.md) - Writing the Expert Prompt

- Complete expert agent file structure
- Required sections and their purposes
- Mission-oriented identity and failure modes
- Expertise sections for different expert types
- Decision authority and signal formats

### 5. [Verification](verification.md) - Quality Assurance

- Verification checklists before finalizing
- Expert registration process
- Quality standards and depth tests

---

## Quick Reference

**Key Principle**: Experts are **narrower but deeper** than baseline agents

- **Baseline agents**: Wide breadth, general depth
- **Experts**: Narrow breadth, expert-level depth

**Expert Chain**:

1. Default agent signals EXPERT_REQUEST
2. Orchestrator routes to expert
3. Expert provides EXPERT_ADVICE or EXPERT_UNSUCCESSFUL (after 3 attempts)
4. On EXPERT_ADVICE: Agent applies advice
5. On EXPERT_UNSUCCESSFUL: Agent MUST escalate to divine intervention

---

## Cross-References

- **[Documentation Index](../../index.md)** - Navigation hub for all docs
- [Agent Definitions](../../agent-definitions.md) - Default agent definitions
- [Signal Specification](../../signal-specification.md) - Expert signal formats
- [Escalation Specification](../../escalation-specification.md) - Escalation rules
- [Expert Delegation](../../expert-delegation.md) - Delegation protocol
- [MCP Servers](../../mcp-servers.md) - Using MCP server capabilities
