# Agent Prompt Engineering Guide

**Purpose**: Define best practices for creating effective agent prompts
**Version**: 2024-01-16-v1

## Overview

This guide defines the standard structure and best practices for creating agent prompts in the Token Bonfire
orchestration system. All agent creation prompts MUST follow these guidelines.

---

## Prompt Structure

Every agent prompt MUST include these sections in order:

### 1. Frontmatter (YAML)

```yaml
---
name: [ agent-name ]
description: [ One sentence describing what this agent does and when to use it ]
model: [ sonnet | opus | haiku ]
tools: [ comma-separated list of tools ]
version: "YYYY-MM-DD-v1"
---
```

**Model Selection**:

- `opus`: High-stakes decisions, quality gatekeeping, complex analysis
- `sonnet`: Implementation work, moderate complexity tasks
- `haiku`: Simple verification, fast binary decisions

### 2. Agent Identity

Define WHO the agent is, not just what it does. Include:

```xml

<agent_identity>
    You are [ROLE NAME] with [EXPERIENCE/EXPERTISE].

    Your Mission:
    - [Primary responsibility]
    - [Secondary responsibility]

    Your Authority:
    - [What decisions you can make]
    - [What outcomes you control]

    Your Mindset:
    - [How you approach work]
    - [What you prioritize]
    - [What you refuse to compromise on]
</agent_identity>
```

**Best Practices**:

- Use strong, clear role definition
- Make the agent feel ownership of their responsibility
- Define attitude and approach, not just tasks
- Include what the agent is NOT (to prevent scope creep)

### 3. Framing (Optional but Recommended)

Provide context that shapes how the agent interprets their work:

```xml

<framing>
    **CRITICAL CONTEXT**: [Important perspective or constraint]

    [Explanation of why this framing matters]
    [How this affects how the agent should approach work]
</framing>
```

**Use framing when**:

- You want to influence the agent's interpretation of ambiguous situations
- You need to prevent specific failure modes
- You want to create a specific psychological stance

### 4. Success Criteria

Define what "done" looks like. Be specific and verifiable:

```xml

<success_criteria>
    Work is complete when ALL of these are true:
    1. [Specific, verifiable criterion]
    2. [Specific, verifiable criterion]
    3. [Specific, verifiable criterion]

    Work is NOT complete if:
    - [Failure condition]
    - [Failure condition]
</success_criteria>
```

**Best Practices**:

- Use binary conditions (yes/no, not "mostly")
- Make criteria independently verifiable
- Include explicit failure conditions

### 5. Method (Phased Approach)

Break work into clear phases:

```xml

<method>
    PHASE 1: [PHASE NAME]
    1. [Concrete action]
    2. [Concrete action]
    3. [Concrete action]

    PHASE 2: [PHASE NAME]
    1. [Concrete action]
    2. [Concrete action]

    ...

    PHASE N: SIGNAL
    1. [How to output result]
</method>
```

**Best Practices**:

- Each phase has a clear purpose
- Actions are concrete and verifiable
- Include decision points and how to handle them
- End with explicit signaling phase

### 6. Boundaries

Define what the agent MUST and MUST NOT do:

```xml

<boundaries>
    MUST NOT:
    - [Prohibited action with brief reason]
    - [Prohibited action with brief reason]

    MUST:
    - [Required action with brief reason]
    - [Required action with brief reason]
</boundaries>
```

**Best Practices**:

- Be specific about prohibited actions
- Explain WHY something is prohibited (prevents workarounds)
- Include both process and output constraints

### 7. Expert Awareness

Make the agent aware of their limitations and available help:

```xml

<expert_awareness>
    **YOU HAVE LIMITATIONS.** Recognize them and ask for help.

    YOUR LIMITATIONS:
    - [Specific limitation relevant to this role]
    - [Specific limitation relevant to this role]

    AVAILABLE EXPERTS:
    {{#each available_experts}}
    | {{name}} | {{expertise}} | Ask when: {{delegation_triggers}} |
    {{/each}}

    WHEN TO ASK AN EXPERT:
    - [Trigger condition]
    - [Trigger condition]

    **IT IS BETTER TO ASK THAN TO GUESS WRONG.**
</expert_awareness>
```

### 8. Context Management

Define how to handle long-running work:

```xml

<context_management>
    [Brief description of context risks for this agent type]

    CHECKPOINT TRIGGERS:
    - [When to checkpoint]
    - [When to checkpoint]

    CHECKPOINT FORMAT:
    [Exact format for checkpoints]

    See: .claude/docs/agent-context-management.md
</context_management>
```

### 9. Coordinator Integration

Define signal rules:

```xml

<coordinator_integration>
    SIGNAL RULES:
    - Signal MUST start at column 0 (beginning of line)
    - Signal MUST appear at END of response
    - NEVER use signal keywords in prose
    - Output exactly ONE signal per response
</coordinator_integration>
```

### 10. Signal Format

Define exact output formats:

```xml

<signal_format>
    [SIGNAL_NAME]:
```

[Exact format with placeholders]

```

[ALTERNATIVE_SIGNAL]:
```

[Exact format with placeholders]

```
</signal_format>
```

---

## Best Practices Injection

For agents that need current best practices (Developer, Critic), include:

```xml

<best_practices>
    {{BEST_PRACTICES_FROM_RESEARCH}}

    (This section is populated by the orchestrator based on pre-creation research for the technologies in this plan.)
</best_practices>
```

The orchestrator populates this by:

1. Identifying languages, frameworks, and tools in the plan
2. Using WebSearch to find current best practices
3. Summarizing key patterns and anti-patterns

---

## Prompt Engineering Principles

### 1. Be Specific, Not General

**Wrong**: "Review the code carefully"
**Right**: "Read every modified file line-by-line. For each file, check for: [specific list]"

### 2. Define the Negative Space

Tell the agent what NOT to do, not just what to do:

**Wrong**: "Fix the code"
**Right**: "Fix the code. Do NOT add features. Do NOT refactor beyond the fix. Do NOT change tests to make them pass."

### 3. Create Accountability

Make the agent feel ownership:

**Wrong**: "Check if tests pass"
**Right**: "You are the final quality gate. If you pass broken code, it goes to production. Run every test yourself."

### 4. Use Concrete Examples

When possible, show exact formats:

**Wrong**: "Output your findings in a structured format"
**Right**:

```
Output in this exact format:
```

AUDIT_PASSED - [task ID]

Quality: VERIFIED
Requirements: [list with evidence]

```
```

### 5. Anticipate Failure Modes

Include guardrails for common mistakes:

```xml

<quality_tells>
    If ANY found, task FAILS:
    - TODO comments
    - FIXME comments
    - Placeholder implementations
    ...
</quality_tells>
```

### 6. Make Instructions Scannable

Use:

- Numbered lists for sequences
- Bullet points for parallel items
- Bold for emphasis
- Tables for structured data
- Headers for sections

### 7. Include Decision Frameworks

When the agent faces choices, provide guidance:

```
If X, then Y.
If A and B, then C.
When in doubt, [default action].
```

---

## Pre-Creation Research

For agents that implement or review code, the CREATOR must research best practices before writing the agent definition.

### Research Process

```markdown
## Pre-Creation Research (REQUIRED)

Before writing the agent file, you MUST research current best practices:

1. **Identify Technologies**: Read the plan and codebase to identify:
    - Programming languages used
    - Frameworks and libraries
    - Tools and build systems

2. **Research Best Practices**: Use WebSearch to find current standards:
    - "[language] best practices [current year]"
    - "[framework] recommended patterns"
    - "[library] common pitfalls"

3. **Document Findings**: Create a best practices summary to embed in the agent.
```

### What to Research

| Agent Type | Research Focus                                               |
|------------|--------------------------------------------------------------|
| Developer  | Implementation patterns, coding standards, testing practices |
| Critic     | Code review criteria, quality issues, anti-patterns          |
| Auditor    | Verification approaches, acceptance testing patterns         |
| Expert     | Domain-specific best practices for their expertise area      |

---

## Terminology Standards

Use these terms consistently across all prompts:

| Term                    | Meaning                                                        |
|-------------------------|----------------------------------------------------------------|
| **Default agents**      | Developer, Critic, Auditor, BA, Remediation, Health Auditor    |
| **Experts**             | Specialist agents created per-plan to provide domain expertise |
| **Orchestrator**        | The coordinator that manages agents and workflow               |
| **Signal**              | Structured output that triggers coordinator actions            |
| **Checkpoint**          | Progress snapshot for context management                       |
| **Divine intervention** | Human escalation when agents are stuck                         |

---

## Quality Checklist

Before finalizing any agent prompt, verify:

- [ ] Frontmatter is complete and accurate
- [ ] Agent identity defines WHO, not just WHAT
- [ ] Success criteria are specific and verifiable
- [ ] Method has clear phases with concrete actions
- [ ] Boundaries define both MUST and MUST NOT
- [ ] Expert awareness is included (if applicable)
- [ ] Context management defines checkpoints
- [ ] Signal format is exact with examples
- [ ] No vague instructions ("carefully", "properly", "as needed")
- [ ] Decision frameworks provided for ambiguous situations
- [ ] Failure modes are anticipated and addressed
- [ ] Pre-creation research completed (for code-related agents)

---

## Required: Quality Verification Skill

**CRITICAL**: When creating agent/expert prompts during orchestrator bootstrap, you MUST use the `/verify-prompt`
skill before writing the file.

### Verification Workflow

```
1. Generate initial prompt using template + context
2. Invoke /verify-prompt skill:
   - Use Skill tool with skill: "verify-prompt"
   - Provide the generated prompt in context
3. Review the PROMPT QUALITY REVIEW output
4. Apply ALL CRITICAL recommendations (mandatory)
5. Apply ALL HIGH recommendations (mandatory)
6. Apply MEDIUM recommendations (optional)
7. Write the REVISED prompt to the agent file
```

### Example Usage

```python
# After generating initial_prompt...

# Invoke verification skill
Skill(skill="verify-prompt")

# The skill will output recommendations like:
# ISSUE: agent_identity - Generic identity
# SEVERITY: CRITICAL
# RECOMMENDED: [improved text]

# Apply recommendations to initial_prompt
# Write revised prompt to file
```

### Why This Matters

Poor quality prompts lead to:

- Agents that don't follow instructions
- Vague outputs that can't be parsed
- Scope creep and unauthorized actions
- Failed audits and wasted cycles

The `/verify-prompt` skill catches these issues before they cause problems.

See: `.claude/skills/verify-prompt.md` for full skill documentation.

---

## Cross-References

- **[Documentation Index](../index.md)** - Navigation hub for all docs
- [Signal Specification](../signal-specification.md) - Signal formats
- [Escalation Specification](../escalation-specification.md) - Escalation rules
- [Agent Context Management](../agent-context-management.md) - Context management
- [MCP Servers](../mcp-servers.md) - MCP server capabilities
