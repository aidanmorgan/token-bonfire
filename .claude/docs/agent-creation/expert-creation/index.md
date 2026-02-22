# Expert Creation - Overview

**THIS IS A META-PROMPT.** It instructs a prompt-creation sub-agent to write expert agent files.

**Purpose**: Create expert agents that fill gaps identified from plan analysis
**Runtime Model**: opus (for creation)
**Version**: 2025-01-17-v5

**Required Reading**: [prompt-engineering-guide.md](../prompt-engineering-guide.md) - MUST follow all quality standards

---

## What This Documentation Is

The team lead analyzes the plan for gaps, researches the domain, substitutes variables, and spawns a prompt-creation
sub-agent. The sub-agent (you) receives gap analysis and research, then writes the expert agent file to
`.claude/experts/<plan_slug>/[expert-name].md`. Expert agents provide specialist advisory guidance via mailbox messages
and CANNOT delegate further. Experts are advisory only -- they never write code directly.

**YOUR RESPONSIBILITY**: The file you write MUST be complete and self-contained. An expert spawned with that file must
know EXACTLY:

- What expertise they provide and for which tasks
- How to give **AUTHORITATIVE, ACTIONABLE** advisory guidance (not suggestions or options)
- That they are **advisory only** -- they never write code, only provide guidance
- What messages to send and in what format
- That they CANNOT delegate (they are the last resort before user clarification)
- How developers will request their advice via `NEED_EXPERT_ADVICE` / `EXPERT_ADVICE_PROVIDED` signals

---

## Documentation Structure

This expert creation guide is organized into focused documents:

### 1. [Types](types.md) - Expert Types and Core Concepts

- Three types of experts: Domain, Reference, and Left-Field
- Methodology experts for project-specific procedural knowledge
- Key principles: narrower but deeper expertise
- Responsibility split between team lead, baseline teammates, and experts

### 2. [Gap Analysis](gap-analysis.md) - Identifying Where Experts Are Needed

- Gap analysis process the team lead performs
- Identifying expertise gaps, decision points, and verification gaps
- Determining which experts to create

### 3. [Inputs](inputs.md) - Research and Inputs for Expert Creation

- Inputs provided by team lead
- Deep domain research requirements
- Research process and existing expert prompt analysis

### 4. [Prompt Structure](prompt-structure.md) - Writing the Expert Prompt

- Complete expert agent file structure
- Required sections and their purposes
- Mission-oriented identity and failure modes
- Expertise sections for different expert types
- Decision authority and message formats

### 5. [Verification](verification.md) - Quality Assurance

- Verification checklists before finalizing
- Expert registration process
- Quality standards and depth tests

---

## Quick Reference

**Key Principle**: Experts are **narrower but deeper** than baseline teammates

- **Baseline teammates**: Wide breadth, general depth
- **Experts**: Narrow breadth, expert-level depth

**Expert Chain**:

1. Developer sends `NEED_EXPERT_ADVICE` to team lead, specifying the expert name
2. Team lead routes the request to the expert
3. Expert reads mailbox, provides advisory `EXPERT RESULT` or indicates failure (after 3 attempts)
4. Team lead forwards expert advice to developer as `EXPERT_ADVICE_PROVIDED`
5. Developer implements the code based on expert guidance
6. On failure: Developer MUST escalate to team lead for user clarification

---

## Cross-References

- **[Documentation Index](../../index.md)** - Navigation hub for all docs
- [Escalation Specification](../../escalation-specification.md) - Escalation rules
- [Communication Protocol](../../communication-protocol.md) - SendMessage API and signal reference
