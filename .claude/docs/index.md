# Documentation Index

**Navigation hub for all orchestration documentation.** Find what you need in one click.

---

## Quick Reference by Role

### For Developers

| Need                | Document                                                   |
|---------------------|------------------------------------------------------------|
| Signal formats      | [signals/workflow-signals.md](signals/workflow-signals.md) |
| Ask an expert       | [expert-delegation.md](expert-delegation.md)               |
| Context running low | [agent-context-management.md](agent-context-management.md) |
| Escalate to human   | [escalation-specification.md](escalation-specification.md) |
| MCP servers         | [mcp-servers.md](mcp-servers.md)                           |

### For Critics

| Need                | Document                                                   |
|---------------------|------------------------------------------------------------|
| Signal formats      | [signals/workflow-signals.md](signals/workflow-signals.md) |
| Review criteria     | [review-audit-flow.md](review-audit-flow.md#critic-review) |
| Ask an expert       | [expert-delegation.md](expert-delegation.md)               |
| Context running low | [agent-context-management.md](agent-context-management.md) |

### For Auditors

| Need                | Document                                                          |
|---------------------|-------------------------------------------------------------------|
| Signal formats      | [signals/workflow-signals.md](signals/workflow-signals.md)        |
| Audit procedure     | [review-audit-flow.md](review-audit-flow.md#auditor-verification) |
| Ask an expert       | [expert-delegation.md](expert-delegation.md)                      |
| Context running low | [agent-context-management.md](agent-context-management.md)        |

### For Remediation Agents

| Need             | Document                                                       |
|------------------|----------------------------------------------------------------|
| Signal formats   | [signals/supporting-signals.md](signals/supporting-signals.md) |
| Remediation loop | [remediation-loop.md](remediation-loop.md)                     |
| Health audit     | [infrastructure-remediation.md](infrastructure-remediation.md) |

### For Experts

| Need                | Document                                                           |
|---------------------|--------------------------------------------------------------------|
| Signal formats      | [signals/coordination-signals.md](signals/coordination-signals.md) |
| Expert protocol     | [expert-delegation.md](expert-delegation.md#expert-response)       |
| Context running low | [agent-context-management.md](agent-context-management.md)         |

### For Orchestrator

| Need              | Document                                                         |
|-------------------|------------------------------------------------------------------|
| Configuration     | [coordinator-configuration.md](coordinator-configuration.md)     |
| Execution model   | [coordinator-execution-model.md](coordinator-execution-model.md) |
| Session startup   | [coordinator-startup.md](coordinator-startup.md)                 |
| Templates         | [coordinator-templates.md](coordinator-templates.md)             |
| Task dispatch     | [task-dispatch.md](task-dispatch.md)                             |
| Review/audit flow | [review-audit-flow.md](review-audit-flow.md)                     |
| State management  | [state-management.md](state-management.md)                       |
| Concurrency       | [concurrency.md](concurrency.md)                                 |
| Recovery          | [recovery-procedures.md](recovery-procedures.md)                 |

---

## All Documents by Category

### Coordinator

| Document                                                         | Purpose                                    |
|------------------------------------------------------------------|--------------------------------------------|
| [coordinator-configuration.md](coordinator-configuration.md)     | Configuration tables, thresholds           |
| [coordinator-execution-model.md](coordinator-execution-model.md) | Identity, 5-agent rules, execution loop    |
| [coordinator-startup.md](coordinator-startup.md)                 | Fresh start and resume procedures          |
| [coordinator-templates.md](coordinator-templates.md)             | Reusable agent reference templates         |
| [coordinator/index.md](coordinator/index.md)                     | Detailed startup procedures (subdirectory) |

### Signals

All signal formats are defined in the `signals/` subdirectory:

| Document                                                           | Purpose                             |
|--------------------------------------------------------------------|-------------------------------------|
| [signals/index.md](signals/index.md)                               | Signal overview and detection rules |
| [signals/workflow-signals.md](signals/workflow-signals.md)         | Developer, Critic, Auditor signals  |
| [signals/supporting-signals.md](signals/supporting-signals.md)     | BA, Remediation, Health signals     |
| [signals/coordination-signals.md](signals/coordination-signals.md) | Expert, Escalation, Concurrency     |
| [signals/parsing.md](signals/parsing.md)                           | Signal parsing implementation       |

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

| Document                                                   | Purpose                         |
|------------------------------------------------------------|---------------------------------|
| [escalation-specification.md](escalation-specification.md) | When and how to escalate        |
| [expert-delegation.md](expert-delegation.md)               | Requesting expert help          |
| [divine-clarification.md](divine-clarification.md)         | Escalating to human             |
| [gap-analysis.md](gap-analysis.md)                         | Identifying expertise gaps      |
| [experts/](experts/index.md)                               | Expert framework (subdirectory) |

### Infrastructure

| Document                                                       | Purpose                     |
|----------------------------------------------------------------|-----------------------------|
| [remediation-loop.md](remediation-loop.md)                     | Infrastructure repair cycle |
| [infrastructure-remediation.md](infrastructure-remediation.md) | Remediation procedures      |
| [environment-verification.md](environment-verification.md)     | Multi-environment execution |
| [mcp-servers.md](mcp-servers.md)                               | MCP server capabilities     |

### State & Recovery

State management is organized in the `state/` subdirectory:

| Document                                             | Purpose                     |
|------------------------------------------------------|-----------------------------|
| [state-management.md](state-management.md)           | State overview (index)      |
| [state/fields.md](state/fields.md)                   | State field definitions     |
| [state/update-triggers.md](state/update-triggers.md) | When state updates          |
| [state/persistence.md](state/persistence.md)         | Atomic updates and recovery |
| [state/task-tracking.md](state/task-tracking.md)     | Task selection and tracking |

Recovery is organized in the `recovery/` subdirectory:

| Document                                                         | Purpose                   |
|------------------------------------------------------------------|---------------------------|
| [recovery-procedures.md](recovery-procedures.md)                 | Recovery overview (index) |
| [recovery/event-log-recovery.md](recovery/event-log-recovery.md) | Event log recovery        |
| [recovery/state-recovery.md](recovery/state-recovery.md)         | State file recovery       |
| [recovery/session-recovery.md](recovery/session-recovery.md)     | Session orchestration     |

| Document                                       | Purpose                 |
|------------------------------------------------|-------------------------|
| [event-logging.md](event-logging.md)           | Event log specification |
| [session-management.md](session-management.md) | Session lifecycle       |

### Concurrency

Concurrency handling is organized in the `concurrency/` subdirectory:

| Document                                                             | Purpose                      |
|----------------------------------------------------------------------|------------------------------|
| [concurrency.md](concurrency.md)                                     | Concurrency overview (index) |
| [concurrency/file-locks.md](concurrency/file-locks.md)               | File locking protocol        |
| [concurrency/queue-management.md](concurrency/queue-management.md)   | Queue timeout handling       |
| [concurrency/conflict-handling.md](concurrency/conflict-handling.md) | Runtime conflicts            |
| [concurrency/race-safety.md](concurrency/race-safety.md)             | Race condition prevention    |

### Quality & Errors

| Document                                               | Purpose                  |
|--------------------------------------------------------|--------------------------|
| [task-quality.md](task-quality.md)                     | Task quality assessment  |
| [error-classification.md](error-classification.md)     | Error types and handling |
| [timeout-specification.md](timeout-specification.md)   | Timeout configuration    |
| [checkpoint-enforcement.md](checkpoint-enforcement.md) | Progress checkpoints     |

### Planning

| Document                               | Purpose                           |
|----------------------------------------|-----------------------------------|
| [plan-format.md](plan-format.md)       | Implementation plan format        |
| [experts/](experts/index.md)           | Expert creation framework         |
| [meta-prompting.md](meta-prompting.md) | Two-tier prompt generation system |

### Orchestrator Generation

| Document                                                                           | Purpose                           |
|------------------------------------------------------------------------------------|-----------------------------------|
| [orchestrator/orchestrator-generation.md](orchestrator/orchestrator-generation.md) | Main orchestrator bootstrap       |
| [orchestrator/research-synthesis.md](orchestrator/research-synthesis.md)           | Knowledge gathering and synthesis |
| [orchestrator/gap-analysis-procedure.md](orchestrator/gap-analysis-procedure.md)   | Expert identification procedure   |
| [orchestrator/agent-generation.md](orchestrator/agent-generation.md)               | Agent prompt creation (index)     |
| [orchestrator/agent-generation/](orchestrator/agent-generation/)                   | Agent generation details          |
| [orchestrator/task-quality.md](orchestrator/task-quality.md)                       | Task quality assessment           |

### Schemas

| Document                                                     | Purpose                |
|--------------------------------------------------------------|------------------------|
| [orchestrator/state-schema.md](orchestrator/state-schema.md) | State file JSON schema |
| [orchestrator/event-schema.md](orchestrator/event-schema.md) | Event log JSON schema  |

---

## Agent Creation (Meta-Prompts)

**[meta-prompting.md](meta-prompting.md)** - Start here to understand the two-tier prompt generation architecture.

These instruct the orchestrator how to create agent files. Each is now organized as a subdirectory:

| Document                                                                                 | Creates                    |
|------------------------------------------------------------------------------------------|----------------------------|
| [agent-creation/developer.md](agent-creation/developer.md)                               | Developer agents           |
| [agent-creation/developer/](agent-creation/developer/)                                   | Developer details          |
| [agent-creation/critic.md](agent-creation/critic.md)                                     | Critic agents              |
| [agent-creation/critic/](agent-creation/critic/)                                         | Critic details             |
| [agent-creation/auditor.md](agent-creation/auditor.md)                                   | Auditor agents             |
| [agent-creation/auditor/](agent-creation/auditor/)                                       | Auditor details            |
| [agent-creation/business-analyst.md](agent-creation/business-analyst.md)                 | Business analyst agents    |
| [agent-creation/business-analyst/](agent-creation/business-analyst/)                     | BA details                 |
| [agent-creation/remediation.md](agent-creation/remediation.md)                           | Remediation agents         |
| [agent-creation/remediation/](agent-creation/remediation/)                               | Remediation details        |
| [agent-creation/health-auditor.md](agent-creation/health-auditor.md)                     | Health auditor agents      |
| [agent-creation/health-auditor/](agent-creation/health-auditor/)                         | Health auditor details     |
| [agent-creation/expert-creation.md](agent-creation/expert-creation.md)                   | Plan-specific experts      |
| [agent-creation/expert-creation/](agent-creation/expert-creation/)                       | Expert creation details    |
| [agent-creation/prompt-engineering-guide.md](agent-creation/prompt-engineering-guide.md) | Guidelines for all prompts |

---

## Mandatory vs On-Demand Reading

### Mandatory (Read Before Starting)

Agents MUST read these before beginning work:

| Agent      | Mandatory Documents                                                     |
|------------|-------------------------------------------------------------------------|
| All agents | `agent-conduct.md`                                                      |
| Developer  | `signals/workflow-signals.md` (developer section)                       |
| Critic     | `signals/workflow-signals.md` (critic section), `review-audit-flow.md`  |
| Auditor    | `signals/workflow-signals.md` (auditor section), `review-audit-flow.md` |

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
│   └── experts/
│
├── docs/                      # This documentation
│   ├── index.md               # This file
│   ├── signals/               # Signal specifications
│   ├── recovery/              # Recovery procedures
│   ├── state/                 # State management
│   ├── concurrency/           # Concurrency handling
│   ├── experts/               # Expert framework
│   ├── coordinator/           # Coordinator procedures
│   ├── orchestrator/          # Orchestrator generation
│   └── agent-creation/        # Agent meta-prompts
│       ├── developer/
│       ├── critic/
│       ├── auditor/
│       ├── business-analyst/
│       ├── remediation/
│       ├── health-auditor/
│       └── expert-creation/
│
├── prompts/                   # Main orchestrator template
├── commands/                  # Slash commands
├── skills/                    # Bonfire and other skills
└── scripts/                   # Helper scripts
```

---

## Navigation Guarantee

Every document is reachable in **one click** from this index.
Every agent template links to this index for navigation.
All subdirectories have their own index files for detailed navigation.
