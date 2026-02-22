# Team Lead Generation

How to bootstrap the Token Bonfire team lead with a plan file.

---

## What is the Team Lead?

The **team lead** is the brain of Token Bonfire — it transforms a plan file into a running multi-agent
team using Claude Code's native Agent Teams primitives.

### The Problem It Solves

A single LLM agent can implement code, but struggles with:

- **Consistency**: Following best practices across an entire project
- **Quality gates**: Self-reviewing work objectively
- **Specialization**: Deep expertise in every domain the plan touches
- **Persistence**: Remembering state across long-running sessions

### The Solution: Specialized, Researched Agents

The team lead solves this by creating **specialized agents at runtime**:

1. **Researches** the technologies in your plan to gather best practices
2. **Generates** agent prompts tailored to your specific project
3. **Creates expert advisors** for domains where developers lack depth
4. **Coordinates** the workflow: Developer -> Critic -> Ripple -> Auditor -> Complete

Each teammate has a focused role with clear boundaries. Developers don't review their own code -- the Critic does.
Developers don't verify acceptance criteria -- the Auditor does independently. This separation creates genuine quality
gates.

### Why Research-Driven?

Agents are only as good as their instructions. Instead of static prompts, the team lead:

- Researches current best practices for each technology
- Synthesizes this research into agent-specific guidance
- Creates experts for specialized domains

This means a Python project gets Python-specific best practices, not generic advice.

---

## Overview

The team lead is the central orchestrator that:

1. Analyzes a plan to understand requirements
2. **Generates ALL agent prompts** - both role prompts and plan-specific experts
3. Creates tasks via `TaskCreate` and manages the shared task list
4. Spawns teammates via `Task()` with background execution
5. Monitors progress via mailbox messages

**CRITICAL**: Static roles (developer, critic, auditor, etc.) use pre-existing `.claude/agents/*.md` definition files with YAML frontmatter. Only expert advisors are generated at runtime based on the specific plan being executed. The team lead composes agent-specific research but does NOT regenerate the static definition files.

---

## Quick Reference

| Need                           | Document                                               |
|--------------------------------|--------------------------------------------------------|
| Research & knowledge synthesis | [research-synthesis.md](research-synthesis.md)         |
| Gap analysis for experts       | [gap-analysis-procedure.md](gap-analysis-procedure.md) |
| Agent prompt generation        | [agent-generation/research.md](agent-generation/research.md) |
| Task quality assessment        | [../task-quality.md](../task-quality.md)               |
| Task list schema               | [../state/task-tracking.md](../state/task-tracking.md) |
| Communication messages         | [../communication-protocol.md](../communication-protocol.md) |

---

## Static Agents (Always Present)

| Teammate        | Role                 | Why Always Needed                |
|-----------------|----------------------|----------------------------------|
| **Developers**  | Implement tasks      | Primary executors (5 sonnet)     |
| **Critic**      | Code quality review  | Quality gate (sonnet)            |
| **Ripple**      | Second-order effects | Downstream impact analysis (sonnet) |
| **Auditor**     | Verify acceptance    | AC verification (opus)           |

These teammates are spawned automatically in both NEW and RESUME flows.

### On-Demand Static Agents

| Teammate         | Role               | When Needed          |
|------------------|---------------------|----------------------|
| Business Analyst | Task expansion      | Underspecified tasks |
| Health Auditor   | State verification  | Recovery scenarios   |
| Remediation      | Fix infrastructure  | Build/test failures  |

### Experts

Experts are specialist agents created per-plan to fill gaps.
See [Expert Creation Guide](../agent-creation/expert-creation/index.md).
Experts are persisted to `.claude/experts/<plan_slug>/`.

---

## Startup Protocol Summary

| Scenario     | Detection                         | Action                                                                      |
|--------------|-----------------------------------|-----------------------------------------------------------------------------|
| **NEW**      | No tasks in shared task list      | Full bootstrap: parse plan, research, generate all agents, create tasks     |
| **RESUME**   | Tasks exist in shared task list   | Load existing tasks, verify prompts, spawn fresh teammates, continue        |

### Decision Tree

1. Check shared task list via `TaskList`
    - Empty -> NEW
    - Has tasks -> RESUME
2. Pre-flight validation
    - FAIL -> Halt with error
    - PASS -> Continue to session-specific flow

### Critical Steps by Session Type

| Step                          | NEW | RESUME             |
|-------------------------------|-----|--------------------|
| Pre-flight validation         | Yes | Yes                |
| Parse plan                    | Yes | Yes                |
| Research best practices       | Yes | Skip (prompts are pre-existing) |
| Gap analysis                  | Yes | Yes (for new gaps)              |
| Generate expert advisors      | Yes | Missing only                    |
| Create tasks via TaskCreate   | Yes | - (already exist)  |
| Spawn teammates               | Yes | Yes (fresh)        |
| Begin task loop               | Yes | Yes                |

---

## New Session Flow

**NEW SESSION BOOTSTRAP**:

1. **PARSE PLAN** - Extract tasks, dependencies, technologies, domains
2. **RESEARCH BEST PRACTICES** - WebSearch for technologies in plan
   -> See [research-synthesis.md](research-synthesis.md)
3. **GAP ANALYSIS** - Identify where developers need expert advisory support
   -> See [gap-analysis-procedure.md](gap-analysis-procedure.md)
4. **AGENT GENERATION PHASE (CRITICAL)** - Generate expert advisor prompts, compose agent-specific research, verify all created
   -> See [agent-generation/research.md](agent-generation/research.md)
5. **ASSESS TASK QUALITY** - Classify tasks, spawn BA for underspecified ones
   -> See [../task-quality.md](../task-quality.md)
6. **CREATE TASKS** - Use `TaskCreate` for each task from the plan, set dependencies via `TaskUpdate({ addBlockedBy })`
7. **SPAWN TEAMMATES** - Spawn developers, critic, auditor, and expert advisors as named teammates via `Task({ team_name, name, run_in_background: true })`
8. **BEGIN TASK DELIVERY LOOP**
   -> See [Task Delivery Loop](../task-delivery-loop.md)

---

## Resume Session Flow

**RESUME SESSION FLOW**:

1. **CHECK TASK LIST** - `TaskList` returns task summaries (`id`, `subject`, `status`, `owner`, `blockedBy`) — use `TaskGet` for full detail
2. **PRE-FLIGHT VALIDATION** - Verify environment is ready
3. **RE-PARSE PLAN** - Plan may have changed since last session
4. **SKIP RESEARCH** - Do NOT re-run research synthesis (per team-lead.md: prompts are pre-existing)
5. **AGENT VERIFICATION** - Verify static agent definitions and expert prompts exist; generate missing experts only
6. **SPAWN FRESH TEAMMATES** - Spawn developers, critic, auditor, and expert advisors using persisted prompts
7. **BEGIN TASK DELIVERY LOOP** - Continue from where we left off

---

## Pre-Flight Validation

**CRITICAL**: Before ANY work begins, validate the environment is ready.

| Check                | What                                    | Blocking |
|----------------------|-----------------------------------------|----------|
| Plan file            | Exists and contains required sections   | Yes      |
| Required directories | `.claude/agents`, `.claude/experts`     | Yes      |
| Agent templates      | All creation templates exist            | Yes      |
| Verification tools   | Basic tool availability                 | Warning  |
| Environments         | Listed environments accessible          | Warning  |

See [environment-verification.md](../environment-verification.md) for details.

---

## Directory Structure After Bootstrap

```
.claude/agents/
+-- developer.md
+-- critic.md
+-- ripple.md
+-- auditor.md
+-- remediation.md
+-- health-auditor.md
+-- business-analyst.md

.claude/experts/<plan_slug>/
+-- [plan-specific experts].md

.claude/bonfire/<plan-slug>/
+-- best-practices-research.json
+-- agent-research/
|   +-- developer.md           # Long-form research essay for Developer
|   +-- critic.md              # Long-form research essay for Critic
|   +-- auditor.md             # Long-form research essay for Auditor
|   +-- remediation.md         # Long-form research essay for Remediation
|   +-- health-auditor.md      # Long-form research essay for Health Auditor
+-- expert-research/
    +-- [expert-name].md       # Long-form research essay for each expert
    +-- crypto-expert.md       # Example: Cryptography expert research
    +-- api-versioning-expert.md  # Example: API versioning expert research
```

### Research Essay Contents

Each research essay in `agent-research/` and `expert-research/` contains:

| Section                          | Purpose                                                                  |
|----------------------------------|--------------------------------------------------------------------------|
| **Executive Summary**            | 2-3 paragraph overview of the agent and its knowledge                    |
| **Research Sources**             | Tables of all project docs, web searches, and codebase patterns analyzed |
| **Knowledge Synthesis**          | Long-form prose synthesizing all sources into coherent guidance          |
| **Project-Specific Adaptations** | How this project differs from standard practices                         |
| **Delegation Guidance**          | (Static agents) Which experts to consult and when                        |
| **Quality Criteria**             | What "good" looks like for this agent's outputs                          |
| **Research Gaps**                | Areas where research was limited or assumptions were made                |
| **Raw Research Data**            | Collapsible section with full research transcripts                       |

These essays serve as:

- **Transparency**: Document exactly what knowledge was gathered
- **Debugging**: Understand why an agent behaves a certain way
- **Iteration**: Improve research process based on outcomes
- **Auditability**: Verify research quality and completeness

---

## Related Documentation

### Sub-Documents

- [research-synthesis.md](research-synthesis.md) - Knowledge gathering and synthesis
- [gap-analysis-procedure.md](gap-analysis-procedure.md) - Expert identification
- [agent-generation/research.md](agent-generation/research.md) - Agent prompt creation
- [../task-quality.md](../task-quality.md) - Task assessment
- [../state/task-tracking.md](../state/task-tracking.md) - Task list schema
- [../communication-protocol.md](../communication-protocol.md) - Communication message reference

### External References

- [Task Delivery Loop](../task-delivery-loop.md) - Main execution loop
- [Expert Creation](../agent-creation/expert-creation/index.md) - Creating expert agents
- [Communication Protocol](../communication-protocol.md) - Team structure and communication
- [Environment Verification](../environment-verification.md) - Environment checks
