# Meta-Prompting Architecture

**Purpose**: Explain the two-tier prompt generation system used to create agent and expert prompts dynamically.

---

## Overview

Token Bonfire uses **meta-prompting** - a two-tier architecture where prompts create other prompts. Rather than shipping
static agent definitions, the system generates tailored agent prompts at runtime based on the specific implementation
plan being executed.

### Why Meta-Prompting?

Static agent prompts have limitations:

| Problem              | Impact                                          |
|----------------------|-------------------------------------------------|
| Generic guidance     | Agents lack plan-specific context               |
| Stale best practices | Technology evolves faster than documentation    |
| One-size-fits-all    | Same prompt for crypto work and UI work         |
| No expert support    | Can't anticipate what expertise each plan needs |

Meta-prompting solves these by generating agents dynamically with:

- **Current best practices** from web research
- **Plan-specific context** from the implementation plan
- **Tailored expertise** from gap analysis
- **Project conventions** from reference documentation

---

## The Two Tiers

### Tier 1: Meta-Prompts (Templates)

Meta-prompts are stored in `.claude/docs/agent-creation/` and define:

- **Structure**: What sections an agent prompt must contain
- **Variables**: Placeholders for dynamic content (e.g., `{{BEST_PRACTICES_RESEARCH}}`)
- **Instructions**: How to transform research into actionable guidance
- **Quality criteria**: What makes a good agent prompt

Meta-prompts are instructions TO an LLM about how to write prompts FOR other LLMs.

### Tier 2: Generated Agent Prompts

Generated prompts are written to `.claude/agents/` for static role definitions and `.claude/experts/<plan_slug>/` for experts:

- **Concrete guidance**: Specific patterns, anti-patterns, and decision frameworks
- **Plan context**: Task IDs, affected files, acceptance criteria
- **Expert awareness**: Which specialists are available for this plan
- **Communication formats**: Copy-paste ready message templates

Generated prompts are instructions TO an LLM about how to perform a role.

---

## Generation Flow

```
PLAN FILE
    |
    v
+---------------------------------------------------------------+
| TEAM LEAD                                                      |
|                                                                |
|  1. Parse plan -> extract technologies, domains, tasks         |
|  2. WebSearch -> gather current best practices per agent type  |
|  3. Gap analysis -> identify where experts are needed          |
|  4. Deep research -> comprehensive expertise for each expert   |
|  5. Spawn prompt-creation sub-agents with:                     |
|     - Meta-prompt template                                     |
|     - Agent-specific research                                  |
|     - Plan context                                             |
|     - Available experts list                                   |
+---------------------------------------------------------------+
    |
    v
+---------------------------------------------------------------+
| PROMPT-CREATION SUB-AGENT                                      |
|                                                                |
|  Receives:                                                     |
|  - Template from .claude/docs/agent-creation/[agent].md        |
|  - BEST_PRACTICES_RESEARCH (agent-specific)                    |
|  - AVAILABLE_EXPERTS (list with triggers)                      |
|  - ENVIRONMENTS and VERIFICATION_COMMANDS                      |
|                                                                |
|  Produces:                                                     |
|  - Agent definition at .claude/agents/[role].md                |
|  - OR expert prompt at .claude/experts/<plan_slug>/[name].md   |
+---------------------------------------------------------------+
    |
    v
GENERATED AGENT PROMPT
(ready to spawn actual working teammates)
```

---

## Pre-Creation Research Phases

Before creating any agents or experts, the team lead performs comprehensive research to ensure each generated prompt
has the best chance of success.

### Phase 1: Plan Analysis

Extract from the plan:

- Technologies, frameworks, databases, infrastructure
- Domains and business context
- Task requirements and dependencies
- Critical success factors

### Phase 2: Reference Documentation Analysis

For each reference document mentioned in the plan (coding standards, specs, design docs):

- Deeply analyze document content and intent
- Map documents to relevant agent skills
- Identify which methodology experts to create
- Extract implicit conventions and patterns

### Phase 3: Agent Prompt Pattern Research

Research existing high-quality agent prompts that perform similar tasks:

- Search for proven coding agent prompts
- Search for code review agent prompts
- Search for testing/verification agent prompts
- Extract structural patterns and techniques that work well

This enables the team lead to learn from the broader AI agent community rather than reinventing prompt engineering
patterns.

### Phase 4: Technology Best Practices Research

For each technology in the plan, research current best practices:

- Developer: DESIGN, WRITING, TESTING practices
- Critic: QUALITY, ARCHITECTURE, DETECTION practices
- Auditor: VERIFICATION, VALIDATION, CRITERIA practices
- Expert Advisor: domain-specific advisory knowledge
- Remediation: DIAGNOSIS, FIXING, PREVENTION practices

### Phase 5: Gap Analysis & Expert Identification

Analyze where teammates need expert support:

- Domain experts for technical domains (crypto, auth, etc.)
- Reference experts for specific project documents
- Methodology experts for project workflows (testing, coding standards, test execution, quality evaluation)
- Left-field experts for non-obvious but valuable domains

### Phase 6: Deep Expert Research

For each identified expert, perform comprehensive domain research:

- Foundational principles and theory
- Expert-level patterns beyond standard practice
- Edge cases where standard advice doesn't apply
- Decision frameworks for authoritative recommendations
- Common misconceptions to correct

---

## Meta-Prompt Structure

Every meta-prompt in `.claude/docs/agent-creation/` follows this pattern:

### 1. Meta-Level Context

Explains that this is a meta-prompt, not a direct agent prompt:

```markdown
**THIS IS A META-PROMPT.** It instructs a prompt-creation sub-agent to write
the actual [agent] file.
```

### 2. Inputs Table

Documents what variables the team lead provides:

| Input                     | Description                  | Use In                       |
|---------------------------|------------------------------|------------------------------|
| `BEST_PRACTICES_RESEARCH` | Technology-specific guidance | `<practices>` section        |
| `AVAILABLE_EXPERTS`       | Experts for this plan        | `<expert_awareness>` section |

### 3. Research Structure

Documents how research is organized for this agent type:

```
BEST_PRACTICES_RESEARCH:
+-- [Technology 1]
|   +-- CATEGORY_A
|   |   +-- Specific guidance
|   |   +-- More guidance
|   +-- CATEGORY_B
|       +-- Different guidance
+-- [Technology 2]
    +-- ...
```

### 4. Creation Prompt

The actual instructions given to the prompt-creation sub-agent:

```
You are creating a [Agent Type] prompt for the Token Bonfire system.

**YOUR MISSION**: Write an expert-level agent prompt file that will guide [agents] to:
1. [Primary capability]
2. [Secondary capability]
...

## INPUTS (provided by team lead)
{{BEST_PRACTICES_RESEARCH}}
...

## STEP 1: [Transform inputs]
## STEP 2: [Write sections]
## STEP 3: [Verify output]
```

### 5. Section Templates

Shows the exact structure each section should have:

```markdown
### <section_name> (REQUIRED)

```markdown
[Template showing expected format]
[With placeholders like [TECHNOLOGY] or [task_id]]
```

```

### 6. Quality Checklist

Verification criteria before the sub-agent finishes:

- [ ] All required sections present
- [ ] Communication formats are correct
- [ ] Guidance is specific, not vague
- [ ] Agent can work without additional context

---

## Research Injection

The team lead performs **agent-specific research** before creating each agent type.

### Research Categories by Agent

| Agent | Research Focus | Categories |
|-------|----------------|------------|
| Developer | Implementation | DESIGN, WRITING, TESTING |
| Critic | Code quality review | QUALITY, ARCHITECTURE, DETECTION |
| Ripple | Second-order effects analysis | IMPACT, CONTRACTS, COVERAGE |
| Auditor | Acceptance verification | VERIFICATION, VALIDATION, CRITERIA |
| Remediation | Fixing | DIAGNOSIS, FIXING, PREVENTION |
| Business Analyst | Specification | REQUIREMENTS, SPECIFICATION, PATTERNS |

### Research Flow

```python
# Pseudocode - actual implementation in team lead bootstrap

for agent_type in ['developer', 'critic', 'auditor', 'remediation', ...]:
    for technology in plan_technologies:
        for category in AGENT_CATEGORIES[agent_type]:
            queries = format_queries(category, technology, current_year)
            results = WebSearch(queries)
            research[agent_type][technology][category] = extract_practices(results)
```

### Injection Point

Research is injected via template variable:

```markdown
BEST_PRACTICES_RESEARCH:
{{BEST_PRACTICES_RESEARCH}}
```

The team lead calls `format_best_practices_for_agent(research, agent_type)` to produce agent-tailored content.

---

## Static Agents vs Expert Depth

The system creates two types of agents with different research depth:

### Static Agents (Developers, Critic, Ripple, Auditor)

Wide breadth, general depth. Receive research covering many topics at moderate depth.

```
STATIC AGENT RESEARCH:
- "Use type hints in Python"
- "Avoid mutable default arguments"
- "Follow PEP8"
```

### Expert Agents

Narrow breadth, expert depth. Receive comprehensive research in their specific domain.

```
EXPERT RESEARCH:
- Complete understanding of domain theory and principles
- Historical context of why patterns evolved
- Edge cases and when standard advice doesn't apply
- Trade-off analysis frameworks with concrete criteria
- Common misconceptions and why they're wrong
- Expert-level opinions with authoritative justification
```

### Why the Difference?

Static agents handle many domains and need broad competence. Experts handle one domain
and need authoritative depth. The research investment matches the role.

---

## Variable Reference

Variables available in meta-prompts:

| Variable                      | Source                    | Used By                |
|-------------------------------|---------------------------|------------------------|
| `{{BEST_PRACTICES_RESEARCH}}` | WebSearch + formatting    | All agents             |
| `{{AVAILABLE_EXPERTS}}`       | Gap analysis              | Developers, Critic, Ripple, Auditor |
| `{{DELEGATION_PROTOCOL}}`     | expert-delegation.md      | Developers, Critic, Ripple, Auditor |
| `{{ENVIRONMENTS}}`            | Plan parsing              | Remediation, Health    |
| `{{VERIFICATION_COMMANDS}}`   | Plan parsing              | Remediation, Health    |
| `{{MCP_SERVERS}}`             | Configuration             | All agents             |
| `{{GAP_ANALYSIS}}`            | Gap analysis output       | Experts only           |
| `{{AFFECTED_TASKS}}`          | Gap analysis              | Experts only           |
| `{{DEEP_DOMAIN_RESEARCH}}`    | Expert-specific WebSearch | Experts only           |
| `{{DECISION_FRAMEWORKS}}`     | Research extraction       | Experts only           |

---

## Creating New Agent Types

To add a new agent type:

### 1. Create Meta-Prompt

Write `.claude/docs/agent-creation/[new-agent].md` following the structure above.

### 2. Define Research Categories

Add research query templates for the new agent type.

### 3. Add to Generation Loop

Include in the static agent list or expert generation as appropriate.

### 4. Update Team Architecture

Add the new teammate to team-architecture.md documentation.

### 5. Update Index

Add to index.md navigation.

---

## Quality Verification

Generated prompts should be verified before use. The system supports a `/verify-prompt` skill that checks:

- All required sections present
- Communication formats are correct
- Guidance is specific, not vague
- No placeholder text remaining
- Decision frameworks are actionable

See [prompt-engineering-guide.md](agent-creation/prompt-engineering-guide.md) for quality standards.

---

## Benefits of Meta-Prompting

### Consistency

All agents follow the same structural patterns because they're generated from coordinated templates.

### Currency

Best practices are researched at runtime, not baked in at documentation time.

### Customization

Each plan gets agents tailored to its specific technologies, domains, and tasks.

### Maintainability

Changing agent behavior means updating one meta-prompt, not many generated files.

### Expertise Injection

The system can create specialists for any domain by researching deeply and generating expert prompts.

---

## Anti-Patterns to Avoid

### In Meta-Prompts

| Anti-Pattern              | Problem                   | Solution                     |
|---------------------------|---------------------------|------------------------------|
| Vague instructions        | Sub-agent guesses wrong   | Be specific about format     |
| Missing section templates | Inconsistent output       | Provide exact structure      |
| No quality checklist      | Incomplete agents         | Add verification steps       |
| Generic guidance          | Doesn't leverage research | Reference injected variables |

### In Generated Prompts

| Anti-Pattern           | Problem                 | Solution                    |
|------------------------|-------------------------|-----------------------------|
| "Review carefully"     | Not actionable          | "Check for X, Y, Z"         |
| "It depends"           | No decision made        | Provide decision framework  |
| Missing message format | Communication failures  | Copy exact format from spec |
| Surface-level patterns | Matches static agents   | Demonstrate expert depth    |

---

## File Locations

| Purpose            | Location                                                  |
|--------------------|-----------------------------------------------------------|
| Meta-prompts       | `.claude/docs/agent-creation/*.md`                        |
| Agent definitions  | `.claude/agents/*.md`                                     |
| Generated experts  | `.claude/experts/<plan_slug>/*.md`                        |
| Team lead logic    | `.claude/docs/orchestrator/orchestrator-generation.md`    |
| Prompt standards   | `.claude/docs/agent-creation/prompt-engineering-guide.md` |

---

## Cross-References

- **[Documentation Index](index.md)** - Navigation hub for all docs
- [Team Lead Generation](orchestrator/orchestrator-generation.md) - Full generation implementation
- [Prompt Engineering Guide](agent-creation/prompt-engineering-guide.md) - Quality standards
- [Expert Creation](agent-creation/expert-creation/index.md) - Expert meta-prompt
- [Team Architecture](team-architecture.md) - Team structure and communication
