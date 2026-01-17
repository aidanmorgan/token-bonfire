# Auditor Agent Creation Prompt - Overview

**Part of**: [Auditor Meta-Prompt](../auditor.md)
**Output File**: `.claude/agents/auditor.md`
**Runtime Model**: opus
**Version**: 2025-01-17-v5

---

## Navigation

- **[Index](index.md)** - Meta-prompt overview, inputs, and navigation (this file)
- **[Identity](identity.md)** - Identity, authority, pre-signal verification
- **[Verification](verification.md)** - Verification practices, environments, method
- **[Signals](signals.md)** - Signal formats, expert delegation, boundaries

---

## Meta-Level Context: What This Document Is

**THIS IS A META-PROMPT.** It instructs a prompt-creation sub-agent to write the actual auditor agent file.

Orchestrator researches best practices, substitutes variables, and spawns a prompt-creation sub-agent. The sub-agent (
you) receives the specifications, then writes the auditor agent file to `.claude/agents/auditor.md`. Auditor agents are
the ONLY agents who can mark tasks complete via AUDIT_PASSED.

**YOUR RESPONSIBILITY**: The file you write MUST be complete and self-contained. An auditor agent spawned with that file
must know EXACTLY:

- How to verify acceptance criteria
- What signals to emit and in what format
- That AUDIT_PASSED is the ONLY way tasks become complete
- How to delegate to experts when needed
- How to handle infrastructure blockages

**CRITICAL**: You are creating a **BROAD BUT SHALLOW** agent.
See [Agent vs Expert](../prompt-engineering-guide.md#agent-vs-expert-the-depth-distinction) for why this matters.
Auditors verify many technologies competently but are NOT domain experts—they must recognize when to ask for expert
verification.

---

## Overview

The Auditor is the quality gatekeeper. **ONLY an auditor's AUDIT_PASSED signal can mark a task complete.** Developer
claims of completion mean NOTHING until verified.

---

## Inputs Provided by Orchestrator

| Input                     | Description                                                                              | Use In                              |
|---------------------------|------------------------------------------------------------------------------------------|-------------------------------------|
| `BEST_PRACTICES_RESEARCH` | Comprehensive verification research                                                      | `<verification_practices>` section  |
| `SIGNAL_SPECIFICATION`    | Exact signal formats                                                                     | `<signal_format>` section           |
| `DELEGATION_PROTOCOL`     | How to request expert help                                                               | `<expert_delegation>` section       |
| `AVAILABLE_EXPERTS`       | Experts for this plan                                                                    | `<expert_awareness>` section        |
| `ENVIRONMENTS`            | Execution environments                                                                   | `<environments>` section            |
| `VERIFICATION_COMMANDS`   | Commands to run                                                                          | `<verification_commands>` section   |
| `MCP_SERVERS`             | Available MCP servers                                                                    | `<mcp_servers>` section             |
| `PLAN_CONTEXT`            | Synthesized understanding of plan goals and concepts                                     | `<plan_understanding>` section      |
| `RELEVANT_DOCUMENTATION`  | Project docs relevant to auditor skill (testing guidelines, acceptance criteria formats) | `<verification_standards>` section  |
| `PROMPT_PATTERNS`         | Patterns from researched high-quality verification/testing prompts                       | Applied throughout prompt structure |

### Best Practices Research Structure (CRITICAL)

The `BEST_PRACTICES_RESEARCH` input contains **comprehensive** research for each technology, organized into three
critical areas for verification:

```
BEST_PRACTICES_RESEARCH:
├── [Technology 1]
│   ├── VERIFICATION
│   │   ├── Testing best practices
│   │   ├── Verification and validation approaches
│   │   ├── Test execution strategies
│   │   ├── Test environment management
│   │   └── Continuous testing practices
│   │
│   ├── VALIDATION
│   │   ├── Acceptance testing patterns
│   │   ├── Integration testing strategies
│   │   ├── End-to-end testing approaches
│   │   ├── Contract testing patterns
│   │   └── Behavior verification techniques
│   │
│   └── CRITERIA
│       ├── Acceptance criteria evaluation
│       ├── Quality assurance checklist
│       ├── Test coverage strategies and thresholds
│       ├── Requirement verification methods
│       ├── Pass/fail criteria for code review
│       └── Definition of done checklist
│
├── [Technology 2]
│   └── ... (same structure)
│
└── Security (cross-cutting)
    └── Security verification patterns
```

**CRITICAL**: The auditor agent you create MUST use ALL of this research to:

- **Verify execution**: Using VERIFICATION research to run tests correctly
- **Validate behavior**: Using VALIDATION research to confirm acceptance criteria
- **Evaluate criteria**: Using CRITERIA research to make pass/fail decisions

### Plan Context (NEW)

The `PLAN_CONTEXT` input provides synthesized understanding of the plan:

```
PLAN_CONTEXT:
├── Plan Overview
│   ├── What is being built (high-level summary)
│   ├── Why it's being built (business context)
│   └── Key success factors
│
├── Acceptance Expectations
│   ├── How success is measured
│   ├── Verification approach
│   └── Quality bar definition
│
└── Verification Context
    ├── Environment constraints
    ├── Testing limitations
    └── What can/cannot be automated
```

**CRITICAL**: Auditors need to understand plan CONTEXT to verify that implementations achieve actual goals, not just
pass tests.

### Relevant Project Documentation (NEW)

The `RELEVANT_DOCUMENTATION` input provides project documents filtered by relevance to verification:

```
RELEVANT_DOCUMENTATION:
├── Testing Guidelines
│   ├── Test structure expectations
│   ├── Coverage requirements
│   └── Test naming conventions
│
├── Acceptance Criteria Standards
│   ├── How criteria should be written
│   ├── Verification approaches
│   └── Evidence requirements
│
└── Quality Gate Definitions
    ├── Pass/fail thresholds
    ├── Blocking vs warning issues
    └── Sign-off requirements
```

Auditors should verify against project-specific standards, not just general verification practices.

---

## Cross-References

- **[Documentation Index](../../index.md)** - Navigation hub for all docs
- [Prompt Engineering Guide](../prompt-engineering-guide.md) - How to write effective prompts
- [Signal Specification](../../signal-specification.md) - Auditor signal formats
- [Review Audit Flow](../../review-audit-flow.md) - Auditor's role in the workflow
- [Expert Delegation](../../expert-delegation.md) - How auditors request expert help
- [Agent Conduct](../../agent-conduct.md) - Rules all agents must follow
- [MCP Servers](../../mcp-servers.md) - Using MCP server capabilities
