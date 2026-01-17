# Expert Creation Guide

**THIS IS A META-PROMPT.** It instructs a prompt-creation sub-agent to write expert agent files.

**Purpose**: Create expert agents that fill gaps identified from plan analysis
**Runtime Model**: opus (for creation)
**Version**: 2025-01-17-v5

**Required Reading**: [prompt-engineering-guide.md](prompt-engineering-guide.md) - MUST follow all quality standards

---

## Documentation Structure

This expert creation guide has been split into focused documents for easier navigation and reference:

### Core Documentation

1. **[Overview and Index](expert-creation/index.md)**
    - Meta-level context
    - Documentation structure
    - Quick reference guide
    - Expert chain summary

2. **[Expert Types and Core Concepts](expert-creation/types.md)**
    - Three types of experts: Domain, Reference, and Left-Field
    - Methodology experts for project-specific procedural knowledge
    - Key principles: narrower but deeper expertise
    - Responsibility split between orchestrator, default agents, and experts
    - Researching existing expert prompts

3. **[Gap Analysis](expert-creation/gap-analysis.md)**
    - Gap analysis process the orchestrator performs
    - Identifying expertise gaps, decision points, and verification gaps
    - Determining which experts to create
    - Gap analysis output format

4. **[Inputs and Research](expert-creation/inputs.md)**
    - Inputs provided by orchestrator
    - Deep domain research requirements (CRITICAL)
    - Research process for each expert type
    - Quality standards for research

5. **[Prompt Structure](expert-creation/prompt-structure.md)**
    - Complete expert agent file structure
    - Required sections and their purposes
    - Mission-oriented identity and failure modes
    - Expertise sections for different expert types
    - Decision authority and signal formats
    - All template sections preserved exactly

6. **[Verification and Registration](expert-creation/verification.md)**
    - Verification checklists before finalizing
    - Expert registration process
    - Quality standards and depth tests
    - Orchestrator registration code

---

## Quick Start

For creating a new expert agent:

1. **Start with Gap Analysis**: [expert-creation/gap-analysis.md](expert-creation/gap-analysis.md)
    - Identify what gaps exist in default agent capabilities
    - Determine which expert type is needed

2. **Gather Inputs**: [expert-creation/inputs.md](expert-creation/inputs.md)
    - Perform deep domain research
    - Collect reference documentation insights
    - Build decision frameworks

3. **Write the Expert Prompt**: [expert-creation/prompt-structure.md](expert-creation/prompt-structure.md)
    - Use the appropriate template for expert type
    - Include all required sections
    - Ensure DEEP expertise, not surface-level

4. **Verify and Register**: [expert-creation/verification.md](expert-creation/verification.md)
    - Run through all checklists
    - Pass depth and authority tests
    - Register with orchestrator

---

## Key Principle

**Experts are narrower but deeper than baseline agents**

- **Baseline agents**: Wide breadth, general depth
- **Experts**: Narrow breadth, expert-level depth

Experts provide AUTHORITATIVE guidance, not suggestions. They give ANSWERS, not options.

---

## Expert Chain Summary

1. Default agent signals EXPERT_REQUEST
2. Orchestrator routes to expert
3. Expert provides EXPERT_ADVICE or EXPERT_UNSUCCESSFUL (after 3 attempts)
4. On EXPERT_ADVICE: Agent applies advice
5. On EXPERT_UNSUCCESSFUL: Agent MUST escalate to divine intervention

**Experts CANNOT delegate** - they are the last resort before human intervention.

---

## Cross-References

- **[Documentation Index](../index.md)** - Navigation hub for all docs
- [Prompt Engineering Guide](prompt-engineering-guide.md) - MUST read before creating experts
- [Agent Definitions](../agent-definitions.md) - Default agent definitions
- [Signal Specification](../signal-specification.md) - Expert signal formats
- [Escalation Specification](../escalation-specification.md) - Escalation rules
- [Expert Delegation](../expert-delegation.md) - Delegation protocol
- [MCP Servers](../mcp-servers.md) - Using MCP server capabilities
