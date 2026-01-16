# Documentation Index

**Navigation hub for all orchestration documentation.** Find what you need in one click.

---

## Quick Reference by Role

### For Developers

| Need                | Document                                                             |
|---------------------|----------------------------------------------------------------------|
| Signal formats      | [signal-specification.md](signal-specification.md#developer-signals) |
| Ask an expert       | [expert-delegation.md](expert-delegation.md)                         |
| Context running low | [agent-context-management.md](agent-context-management.md)           |
| Escalate to human   | [escalation-specification.md](escalation-specification.md)           |
| MCP servers         | [mcp-servers.md](mcp-servers.md)                                     |

### For Critics

| Need                | Document                                                          |
|---------------------|-------------------------------------------------------------------|
| Signal formats      | [signal-specification.md](signal-specification.md#critic-signals) |
| Review criteria     | [review-audit-flow.md](review-audit-flow.md#critic-review)        |
| Ask an expert       | [expert-delegation.md](expert-delegation.md)                      |
| Context running low | [agent-context-management.md](agent-context-management.md)        |

### For Auditors

| Need                | Document                                                           |
|---------------------|--------------------------------------------------------------------|
| Signal formats      | [signal-specification.md](signal-specification.md#auditor-signals) |
| Audit procedure     | [review-audit-flow.md](review-audit-flow.md#auditor-verification)  |
| Ask an expert       | [expert-delegation.md](expert-delegation.md)                       |
| Context running low | [agent-context-management.md](agent-context-management.md)         |

### For Remediation Agents

| Need             | Document                                                               |
|------------------|------------------------------------------------------------------------|
| Signal formats   | [signal-specification.md](signal-specification.md#remediation-signals) |
| Remediation loop | [remediation-loop.md](remediation-loop.md)                             |
| Health audit     | [infrastructure-remediation.md](infrastructure-remediation.md)         |

### For Experts

| Need                | Document                                                          |
|---------------------|-------------------------------------------------------------------|
| Signal formats      | [signal-specification.md](signal-specification.md#expert-signals) |
| Expert protocol     | [expert-delegation.md](expert-delegation.md#expert-response)      |
| Context running low | [agent-context-management.md](agent-context-management.md)        |

### For Orchestrator

| Need              | Document                                         |
|-------------------|--------------------------------------------------|
| Task dispatch     | [task-dispatch.md](task-dispatch.md)             |
| Review/audit flow | [review-audit-flow.md](review-audit-flow.md)     |
| State management  | [state-management.md](state-management.md)       |
| Concurrency       | [concurrency.md](concurrency.md)                 |
| Recovery          | [recovery-procedures.md](recovery-procedures.md) |

---

## All Documents by Category

### Signals (Single Source of Truth)

- [signal-specification.md](signal-specification.md) - **All signal formats defined here**

### Workflow

| Document                                       | Purpose                                         |
|------------------------------------------------|-------------------------------------------------|
| [task-delivery-loop.md](task-delivery-loop.md) | Overview of the dispatch → review → audit cycle |
| [task-dispatch.md](task-dispatch.md)           | Task selection and developer dispatch           |
| [review-audit-flow.md](review-audit-flow.md)   | Critic review and auditor verification          |
| [developer-rework.md](developer-rework.md)     | Handling failed reviews/audits                  |

### Agent Behavior

| Document                                                   | Purpose                      |
|------------------------------------------------------------|------------------------------|
| [agent-conduct.md](agent-conduct.md)                       | Rules all agents must follow |
| [agent-definitions.md](agent-definitions.md)               | Agent types and roles        |
| [agent-context-management.md](agent-context-management.md) | Handling context limits      |
| [agent-coordination.md](agent-coordination.md)             | Task-agent matching          |

### Escalation & Experts

| Document                                                   | Purpose                    |
|------------------------------------------------------------|----------------------------|
| [escalation-specification.md](escalation-specification.md) | When and how to escalate   |
| [expert-delegation.md](expert-delegation.md)               | Requesting expert help     |
| [divine-clarification.md](divine-clarification.md)         | Escalating to human        |
| [gap-analysis.md](gap-analysis.md)                         | Identifying expertise gaps |

### Infrastructure

| Document                                                       | Purpose                     |
|----------------------------------------------------------------|-----------------------------|
| [remediation-loop.md](remediation-loop.md)                     | Infrastructure repair cycle |
| [infrastructure-remediation.md](infrastructure-remediation.md) | Remediation procedures      |
| [environment-verification.md](environment-verification.md)     | Multi-environment execution |
| [mcp-servers.md](mcp-servers.md)                               | MCP server capabilities     |

### State & Recovery

| Document                                         | Purpose                    |
|--------------------------------------------------|----------------------------|
| [state-management.md](state-management.md)       | Coordinator state tracking |
| [event-logging.md](event-logging.md)             | Event log specification    |
| [recovery-procedures.md](recovery-procedures.md) | Failure recovery           |
| [session-management.md](session-management.md)   | Session lifecycle          |

### Quality & Errors

| Document                                               | Purpose                  |
|--------------------------------------------------------|--------------------------|
| [task-quality.md](task-quality.md)                     | Task quality assessment  |
| [error-classification.md](error-classification.md)     | Error types and handling |
| [timeout-specification.md](timeout-specification.md)   | Timeout configuration    |
| [checkpoint-enforcement.md](checkpoint-enforcement.md) | Progress checkpoints     |

### Planning

| Document                         | Purpose                    |
|----------------------------------|----------------------------|
| [plan-format.md](plan-format.md) | Implementation plan format |
| [experts.md](experts.md)         | Expert creation framework  |

### Schemas

| Document                                                                           | Purpose                        |
|------------------------------------------------------------------------------------|--------------------------------|
| [orchestrator/state-schema.md](orchestrator/state-schema.md)                       | State file JSON schema         |
| [orchestrator/event-schema.md](orchestrator/event-schema.md)                       | Event log JSON schema          |
| [orchestrator/orchestrator-generation.md](orchestrator/orchestrator-generation.md) | Orchestrator prompt generation |

---

## Agent Creation (Meta-Prompts)

These instruct the orchestrator how to create agent files:

| Document                                                                                 | Creates                    |
|------------------------------------------------------------------------------------------|----------------------------|
| [agent-creation/developer.md](agent-creation/developer.md)                               | Developer agents           |
| [agent-creation/critic.md](agent-creation/critic.md)                                     | Critic agents              |
| [agent-creation/auditor.md](agent-creation/auditor.md)                                   | Auditor agents             |
| [agent-creation/business-analyst.md](agent-creation/business-analyst.md)                 | Business analyst agents    |
| [agent-creation/remediation.md](agent-creation/remediation.md)                           | Remediation agents         |
| [agent-creation/health-auditor.md](agent-creation/health-auditor.md)                     | Health auditor agents      |
| [agent-creation/expert-creation.md](agent-creation/expert-creation.md)                   | Plan-specific experts      |
| [agent-creation/prompt-engineering-guide.md](agent-creation/prompt-engineering-guide.md) | Guidelines for all prompts |

---

## Mandatory vs On-Demand Reading

### Mandatory (Read Before Starting)

Agents MUST read these before beginning work:

| Agent      | Mandatory Documents                                                 |
|------------|---------------------------------------------------------------------|
| All agents | `agent-conduct.md`                                                  |
| Developer  | `signal-specification.md` (developer section)                       |
| Critic     | `signal-specification.md` (critic section), `review-audit-flow.md`  |
| Auditor    | `signal-specification.md` (auditor section), `review-audit-flow.md` |

### On-Demand (Read When Needed)

| Situation             | Read                          |
|-----------------------|-------------------------------|
| Need expert help      | `expert-delegation.md`        |
| Context running low   | `agent-context-management.md` |
| Need to escalate      | `escalation-specification.md` |
| Infrastructure broken | `remediation-loop.md`         |
| Using MCP             | `mcp-servers.md`              |

---

## Directory Structure

```
.claude/
├── agents/                    # Generated agent files
│   ├── developer.md
│   ├── critic.md
│   ├── auditor.md
│   └── experts/               # Plan-specific experts
├── docs/                      # This documentation
│   ├── index.md               # YOU ARE HERE
│   ├── agent-creation/        # Meta-prompts for creating agents
│   └── orchestrator/          # Orchestrator-specific schemas
├── prompts/                   # Main orchestrator template
├── commands/                  # Slash commands
└── scripts/                   # Helper scripts
```

---

## Navigation Guarantee

Every document is reachable in **one click** from this index.
Every agent template links to this index for navigation.
