# Documentation Index

## Team Architecture

| Document | Purpose |
|----------|---------|
| [Team Architecture](team-architecture.md) | Team structure, expert generation, communication, task lifecycle |
| [Teammate Definitions](agent-definitions.md) | Overview of all named teammates and their responsibilities |
| [Teammate Coordination](agent-coordination.md) | How teammates communicate via mailbox and coordinate |
| [Teammate Conduct](agent-conduct.md) | Behavioral expectations for all teammates |
| [Teammate Context Management](agent-context-management.md) | How teammates manage their context windows, including progress monitoring |
| [Plan Format](plan-format.md) | Plan file format specification |
| [Troubleshooting](troubleshooting.md) | Common issues and recovery procedures |

## Named Teammate Creation

| Document | Purpose |
|----------|---------|
| [Creation Index](agent-creation/index.md) | Overview of teammate creation meta-prompts |
| [Developer (implementation loop)](agent-creation/developer/index.md) | Developer agent creation — domain-specialized implementer |
| [Critic](agent-creation/critic/index.md) | Critic creation — code quality review |
| [Auditor](agent-creation/auditor/index.md) | Auditor creation — acceptance verification |
| [Business Analyst](agent-creation/business-analyst/index.md) | Business analyst creation — requirement expansion |
| [Remediation](agent-creation/remediation/index.md) | Remediation creation — infrastructure repair |
| [Health Auditor](agent-creation/health-auditor/index.md) | Health auditor creation — health verification |
| [Expert Creation](agent-creation/expert-creation/index.md) | Domain expert generation from plan research |
| [Prompt Engineering Guide](agent-creation/prompt-engineering-guide.md) | How to write effective teammate prompts |

## Expert System

| Document | Purpose |
|----------|---------|
| [Experts Overview](experts/index.md) | Expert agent system overview |
| [Expert Delegation](expert-delegation.md) | How teammates delegate to domain experts |
| [Gap Analysis](orchestrator/gap-analysis-procedure.md) | Determining what experts are needed |
| [Meta-Prompting](meta-prompting.md) | Two-tier prompt generation architecture |

## Signal Specification

| Document | Purpose |
|----------|---------|
| [Signal Reference](signals/index.md) | Complete signal reference — all formats, routing table, delivery mechanism |

## Task & Review Flow

| Document | Purpose |
|----------|---------|
| [Task Dispatch](task-dispatch.md) | How the team lead routes tasks to expert agents |
| [Task Delivery Loop](task-delivery-loop.md) | The implementation → review → audit pipeline |
| [Review Audit Flow](review-audit-flow.md) | Staged review pipeline (Critic → Ripple → Auditor) |
| [Expert Rework](developer-rework.md) | How experts receive and handle rework requests |
| [Expert Specification](developer-spec.md) | Expert agent behavior specification |
| [Auditor Specification](auditor-spec.md) | Auditor teammate behavior specification |
| [Task Quality](task-quality.md) | Task quality standards and assessment |
| [Remediation Loop](remediation-loop.md) | Infrastructure failure handling and remediation procedure |

## Escalation & Error Handling

| Document | Purpose |
|----------|---------|
| [Escalation Specification](escalation-specification.md) | When and how teammates escalate to the user |
| [Error Classification](error-classification.md) | Error types and handling |
| [Environment Verification](environment-verification.md) | Environment health checks |

## Team Lead & Coordination

| Document | Purpose |
|----------|---------|
| [Team Lead Fresh Start](coordinator/fresh-start.md) | New session initialization — bootstrap flow |
| [Team Lead Resume](coordinator/resume.md) | Resuming interrupted sessions |
| [Team Lead Execution Model](coordinator-execution-model.md) | The lead's execution loop and mailbox monitoring |
| [Team Lead Configuration](coordinator-configuration.md) | Configuration reference (native tools) |
| [Team Lead Templates](coordinator-templates.md) | Prompt template reference |

## State & Recovery

| Document | Purpose |
|----------|---------|
| [Task State Tracking](state/index.md) | Task state via native `TaskList`/`TaskUpdate`/`TaskGet` |
| [Communication Protocol](communication-protocol.md) | Mailbox messaging via `TeammateTool write` |
| [Recovery Procedures](recovery/index.md) | Crash recovery via slug-based task list |
| [Session Management](session-management.md) | Native context management and resume |
| [Timeout Recovery](agent-timeout-recovery.md) | Native heartbeat timeout handling |
| [Timeout Specification](timeout-specification.md) | Timeout configuration |

## Concurrency

| Document | Purpose |
|----------|---------|
| [Concurrency Overview](concurrency/index.md) | Parallel execution coordination, file ownership, dependencies, race safety |

## Configuration

| File | Purpose |
|------|---------|
| `.claude/base_variables.md` | Project-specific commands, environments, team settings |
| `.claude/settings.json` | Agent teams feature flag |

## Native Agent Definitions

Static roles are defined in `.claude/agents/` with YAML frontmatter (model, tools, memory, permissions) and role instructions in the body. Spawned with `subagent_type: "<agent-name>"`.

| Agent | File |
|-------|------|
| Developer | `.claude/agents/developer.md` |
| Critic | `.claude/agents/critic.md` |
| Ripple | `.claude/agents/ripple.md` |
| Auditor | `.claude/agents/auditor.md` |
| Business Analyst | `.claude/agents/business-analyst.md` |
| Remediation | `.claude/agents/remediation.md` |
| Health Auditor | `.claude/agents/health-auditor.md` |

## Role Prompts (Active)

| Role | File |
|------|------|
| Team Lead | `.claude/prompts/team-lead.md` |
| Expert (advisory loop) | `.claude/prompts/expert.md` |

## Generated at Runtime

| Directory | Purpose |
|-----------|---------|
| `.claude/experts/<plan_slug>/` | Persisted expert agent definitions (one `.md` per expert) |
