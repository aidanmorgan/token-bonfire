# Documentation Index

## Core Reference

| Document | Purpose |
|----------|---------|
| [Communication Protocol](communication-protocol.md) | `SendMessage` API, signal reference, message routing |
| [Task Dispatch](task-dispatch.md) | Push-based task assignment from team lead to developers |
| [Task Delivery Loop](task-delivery-loop.md) | Full task routing procedure and priority ordering |
| [Review Audit Flow](review-audit-flow.md) | Staged review pipeline (Critic → Ripple → Auditor) |
| [Expert Delegation](expert-delegation.md) | Expert consultation triggers, request protocol, escalation |
| [Plan Format](plan-format.md) | Plan file format specification |
| [Troubleshooting](troubleshooting.md) | Common issues, recovery procedures, limitations |

## Team & Agent Conduct

| Document | Purpose |
|----------|---------|
| [Autonomy Boundaries](autonomy.md) | **Hard invariants on team lead and teammate behavior — read first** |
| [Agent Conduct](agent-conduct.md) | Teammate isolation model, file ownership, verification rules |
| [Agent Context Management](agent-context-management.md) | Context window strategies for teammates |
| [Escalation Specification](escalation-specification.md) | Escalation ladder, attempt counting, user clarification |
| [Error Classification](error-classification.md) | Error categories, recovery strategies, classification logic |
| [Task Quality](task-quality.md) | Task quality assessment criteria and expansion workflow |
| [Environment Verification](environment-verification.md) | Multi-environment execution, signal validation, disagreement handling |

## State & Tracking

| Document | Purpose |
|----------|---------|
| [Task Tracking](state/task-tracking.md) | Task selection priority, rollback, failure pattern learning |
| [Attempt Tracking](state/attempt-tracking.md) | Per-task attempt counters and escalation thresholds |
| [Update Triggers](state/update-triggers.md) | Signal-to-state-change mapping, blocker routing |

## Recovery & Resilience

| Document | Purpose |
|----------|---------|
| [Resume Procedure](team-lead/resume.md) | Session resume: re-spawn, re-verify, reconcile |
| [Baseline Failures](recovery/baseline-failures.md) | Pre-session failure baseline capture |
| [Timeout Recovery](agent-timeout-recovery.md) | Per-teammate timeout handling, disagreement detection |
| [Remediation Loop](remediation-loop.md) | Infrastructure repair loop, user-response handler |
| [Developer Rework](developer-rework.md) | Rework routing after review/audit failures |

## Specifications

| Document | Purpose |
|----------|---------|
| [Auditor Spec](auditor-spec.md) | 6-phase audit checklist, test quality tells |

## Concurrency

| Document | Purpose |
|----------|---------|
| [Concurrency Index](concurrency/index.md) | Overview of concurrent file modification handling |
| [File Ownership](concurrency/file-ownership.md) | File ownership protocol and single-writer pattern |
| [Task Dependencies](concurrency/queue-management.md) | Native dependency management with `addBlockedBy` |
| [Conflict Handling](concurrency/conflict-handling.md) | Runtime conflict detection and resolution |
| [Race Safety](concurrency/race-safety.md) | Race condition prevention with named teammates |

## Agent Creation (Meta-Prompting)

| Document | Purpose |
|----------|---------|
| [Meta-Prompting](meta-prompting.md) | Two-tier prompt generation architecture |
| [Agent Creation Index](agent-creation/index.md) | Navigation index for agent creation docs |
| [Prompt Engineering Guide](agent-creation/prompt-engineering-guide.md) | Quality standards for all teammate prompts |

### Baseline Agent Meta-Prompts

| Document | Purpose |
|----------|---------|
| [Developer Meta-Prompt](agent-creation/developer.md) | Developer agent generation with research injection |
| [Critic Meta-Prompt](agent-creation/critic.md) | Critic agent generation with review criteria |
| [Auditor Meta-Prompt](agent-creation/auditor.md) | Auditor agent generation with verification practices |
| [Business Analyst Meta-Prompt](agent-creation/business-analyst.md) | BA agent generation with expansion protocol |
| [Remediation Meta-Prompt](agent-creation/remediation.md) | Remediation agent generation with diagnosis practices |
| [Health Auditor Meta-Prompt](agent-creation/health-auditor.md) | Health auditor generation with baseline comparison |

### Expert Creation

| Document | Purpose |
|----------|---------|
| [Expert Creation Index](agent-creation/expert-creation/index.md) | Expert agent creation overview |
| [Expert Types](agent-creation/expert-creation/types.md) | Domain, Reference, and Methodology expert types |
| [Gap Analysis](agent-creation/expert-creation/gap-analysis.md) | Identifying where experts are needed |
| [Expert Inputs](agent-creation/expert-creation/inputs.md) | Research inputs for expert creation |
| [Expert Prompt Structure](agent-creation/expert-creation/prompt-structure.md) | Complete expert prompt file structure |
| [Expert Verification](agent-creation/expert-creation/verification.md) | Quality assurance and registration |

### Orchestrator

| Document | Purpose |
|----------|---------|
| [Orchestrator Generation](orchestrator/orchestrator-generation.md) | Bootstrap protocol, research essay format |
| [Gap Analysis Procedure](orchestrator/gap-analysis-procedure.md) | Left-field experts, prioritization scoring |
| [Research Synthesis](orchestrator/research-synthesis.md) | Per-agent search queries, research output schema |
| [Research Format](orchestrator/agent-generation/research.md) | Research essay template and quality gate |

## Source of Truth Files

These are the authoritative definitions — docs above are supplementary reference only.

| File | What It Defines |
|------|----------------|
| `.claude/agents/developer.md` | Developer agent behavior, work loop, signals |
| `.claude/agents/critic.md` | Critic review procedure and signals |
| `.claude/agents/ripple.md` | Ripple analysis procedure and signals |
| `.claude/agents/auditor.md` | Auditor verification procedure and signals |
| `.claude/agents/business-analyst.md` | Business analyst expansion procedure |
| `.claude/agents/remediation.md` | Remediation repair procedure |
| `.claude/agents/health-auditor.md` | Health auditor verification procedure |
| `.claude/docs/autonomy.md` | Hard invariants on team lead behavior — pipeline enforcement, expert boundaries |
| `.claude/prompts/team-lead.md` | Team lead orchestration: bootstrap, assignment, routing, completion |
| `.claude/prompts/expert.md` | Expert advisory loop |
| `.claude/skills/bonfire/SKILL.md` | `/bonfire` skill: full workflow from plan to completion |
| `.claude/base_variables.md` | Project configuration: team size, commands, environments |

## Generated at Runtime

| Directory | Purpose |
|-----------|---------|
| `.claude/experts/<plan_slug>/` | Persisted expert agent definitions (one `.md` per expert) |
