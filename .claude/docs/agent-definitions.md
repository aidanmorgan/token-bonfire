# Teammate Definitions

All teammates are **named, persistent agents** spawned at startup via `Task({ team_name, name, run_in_background: true })`. They run for the duration of the plan, communicating via mailbox messages.

Static roles use native agent definitions in `.claude/agents/<name>.md` (spawned with `subagent_type: "<agent-name>"`). Expert advisors use inline prompts from `.claude/experts/<plan_slug>/<name>.md` (spawned with `subagent_type: "general-purpose"`).

---

## Team Structure

| Role | Count | Model | Spawn Name | Purpose |
|------|-------|-------|------------|---------|
| Team Lead | 1 (main session) | opus | N/A (is the session) | Orchestrates team, spawns developers, generates expert advisors, manages task lifecycle |
| Developers | 2-MAX_DEVELOPERS | EXPERT_MODEL | `dev-N` | Generic parallel implementers, claim tasks, write code, self-verify |
| Named Expert Advisors | 0-N (determined by gap analysis) | EXPERT_MODEL | `<expert-name>` | Advisory only — answer developer questions, provide domain guidance, never write code |
| Critic | 1 | EXPERT_MODEL | `critic` | Code quality reviewer (bugs, style, error handling, dead code) |
| Ripple | 1 | EXPERT_MODEL | `ripple` | Second-order effects analyst (downstream impact, API contracts, test coverage gaps) |
| Auditor | 1 | AUDITOR_MODEL | `auditor` | Acceptance criteria verifier, runs verification commands, sole authority for task completion |

Configuration lives in `.claude/base_variables.md`.

---

## Signal Formatting Rules

Signals are sent as plain-text mailbox messages via `TeammateTool({ operation: "write", to: "team-lead" })`. The team lead reads its mailbox to receive signals.

| Rule               | Requirement                             | Example                                                                                 |
|--------------------|-----------------------------------------|-----------------------------------------------------------------------------------------|
| Signal name        | Use EXACT name from specification       | `READY_FOR_REVIEW` not `Ready for Review`                                               |
| Placement          | Signal should be FIRST LINE of message  | Before explanatory text                                                                 |
| No false positives | Don't use signal keywords in prose      | Don't say "this is READY_FOR_REVIEW" in explanations                                    |

### Valid Signal Names

| Signal                         | Used By              | Team Lead Action |
|--------------------------------|----------------------|-----------------|
| `READY_FOR_REVIEW: <id>`       | Developer            | `write` to `critic` |
| `NEED_CLARIFICATION: <question>` | Developer          | Route to `business-analyst` or `AskUserQuestion` |
| `NEED_EXPERT_ADVICE: <question>` | Developer          | Route to appropriate expert advisor via `write` |
| `INFRA_BLOCKED: <details>`     | Developer            | `write` to `remediation` |
| `FILE_CONFLICT: <file>`        | Developer            | Coordinate ownership via `write` |
| `REVIEW_PASSED: <id>`          | Critic               | `write` to `ripple` |
| `REVIEW_FAILED: <id>`          | Critic               | `write` feedback to owning developer |
| `RIPPLE_PASSED: <id>`          | Ripple               | `write` to `auditor` |
| `RIPPLE_FAILED: <id>`          | Ripple               | `write` feedback to owning developer |
| `AUDIT_PASSED: <id>`           | Auditor              | `TaskUpdate({ status: "completed" })` |
| `AUDIT_FAILED: <id>`           | Auditor              | `write` feedback to owning developer |
| `AUDIT_BLOCKED: <id>`          | Auditor              | `write` to `remediation` |
| `EXPERT_ADVICE_PROVIDED: <response>` | Expert Advisor   | `write` guidance to requesting developer via team lead |
| `EXPANDED_TASK_SPECIFICATION: <id>` | Business Analyst | `TaskUpdate` description, route to developer |
| `REMEDIATION_COMPLETE`         | Remediation          | `write` to `health-auditor` |
| `HEALTH_AUDIT: HEALTHY`        | Health Auditor       | Resume normal flow |
| `HEALTH_AUDIT: UNHEALTHY`      | Health Auditor       | `write` to `remediation` |
| `SEEKING_DIVINE_CLARIFICATION` | Any teammate         | `AskUserQuestion` |
| `CHECKPOINT: <id>`             | Developer            | Log progress |

### Required Teammate Instruction

Every teammate's spawn prompt MUST instruct them to:

1. Output exactly ONE signal per mailbox message
2. Place the signal as the FIRST LINE of the message
3. Never use signal keywords in explanatory prose
4. Use the EXACT signal format (spacing, punctuation, field names)

---

## Teammate Communication

### Isolation Model

Teammates operate with isolated context windows:

| Property                       | Implication                                         |
|--------------------------------|-----------------------------------------------------|
| Isolated context windows       | Each teammate has its own 1M token context           |
| No shared context              | Teammates cannot see each other's work or conversation |
| No persistent memory on resume | Respawned teammates start with fresh context         |
| Mailbox-only communication     | Teammates communicate only via `write` to team lead  |

### Communication Rules

- **Developers** communicate with the team lead only (never directly with critic, auditor, experts, or other developers)
- **Expert advisors** communicate with the team lead only (never directly with developers, critic, or auditor)
- **Critic** communicates with the team lead only
- **Ripple** communicates with the team lead only
- **Auditor** communicates with the team lead only
- **Team lead** routes messages between all teammates
- **Never use `broadcast`** — it scales with team size and is expensive

---

## Developers

Developers are generic, parallel implementers. Multiple developers are spawned at startup and claim tasks from the shared task list. They write code, self-verify, and consult expert advisors when they need domain guidance.

### Developer Signals

Developers send these signals to the team lead via mailbox:

| Signal | Usage |
|--------|-------|
| `READY_FOR_REVIEW: <task-id>` | Implementation complete, self-verified |
| `NEED_CLARIFICATION: <question>` | Ambiguous requirements or missing dependency |
| `NEED_EXPERT_ADVICE: <question>` | Needs domain guidance from an expert advisor |
| `INFRA_BLOCKED: <details>` | Infrastructure prevents progress |
| `FILE_CONFLICT: <file> <details>` | Needs file outside ownership scope |
| `CHECKPOINT: <task-id>` | Progress report on long-running task |

At spawn time, developers use `subagent_type: "developer"` which loads role instructions from `.claude/agents/developer.md`. Configuration tables from `base_variables.md` are passed via the `prompt` parameter.

---

## Named Expert Advisors

Expert advisors are domain specialists generated by the team lead based on plan analysis. Each expert advisor is a persistent, named teammate with deep domain knowledge. **Expert advisors are advisory only — they answer developer questions and provide domain guidance but never write code directly.**

### Expert Definition Files

Expert definitions are saved to `.claude/experts/<plan_slug>/<expert-name>.md` and contain:

```markdown
# <Expert Name>

## Identity
- Who they are, what domain, what's at stake

## Expertise
- Deep domain research (technologies, patterns, pitfalls)
- Decision frameworks for choices developers will face
- Verification criteria specific to their domain

## Applicable Domains
- Technology areas and task categories they can advise on
```

At spawn time, this is composed with `.claude/prompts/expert.md` (the advisory loop) and configuration from `base_variables.md` to form the complete spawn prompt.

### Expert Advisor Signals

Expert advisors send these signals to the team lead via mailbox:

| Signal | Usage |
|--------|-------|
| `EXPERT_ADVICE_PROVIDED: <response>` | Domain guidance provided in response to a developer question |

### Expert Persistence

Expert definitions are saved to disk and survive crashes:
- On resume, definitions are loaded from `.claude/experts/<plan_slug>/` — no regeneration needed
- Fresh expert advisors are spawned using the persisted prompts
- The deep research investment in expert prompts is preserved across sessions

---

## Supporting Teammates

### Critic

**Spawn name**: `critic`
**Model**: EXPERT_MODEL
**Agent definition**: `.claude/agents/critic.md`

Reviews code quality between Developer and Auditor. When a developer signals `READY_FOR_REVIEW`, the team lead forwards to the critic.

| Reviews                         | Does NOT Review                           |
|---------------------------------|-------------------------------------------|
| Code correctness and bugs       | Requirements implementation               |
| Error handling approach         | Test adequacy/coverage                    |
| Naming and style consistency    | Performance correctness                   |
| Code structure and design       | Security correctness                      |
| TODOs, FIXMEs, debug statements | Acceptance criteria verification          |

**Signals**: `REVIEW_PASSED: <task-id>` or `REVIEW_FAILED: <task-id>`

### Ripple

**Spawn name**: `ripple`
**Model**: EXPERT_MODEL
**Agent definition**: `.claude/agents/ripple.md`

Analyzes second-order effects between Critic and Auditor. When the critic signals `REVIEW_PASSED`, the team lead forwards to the ripple analyst.

| Analyzes                          | Does NOT Analyze                          |
|-----------------------------------|-------------------------------------------|
| Downstream consumer breakage      | First-order code quality (bugs, style)    |
| API contract drift                | Acceptance criteria verification          |
| Test coverage gaps in affected modules | Running tests or verification commands |
| Behavioral changes in callers     | Code structure and design                 |
| Shared state impacts              | Naming and style consistency              |

**Signals**: `RIPPLE_PASSED: <task-id>` or `RIPPLE_FAILED: <task-id>`

### Auditor

**Spawn name**: `auditor`
**Model**: AUDITOR_MODEL
**Agent definition**: `.claude/agents/auditor.md`

The quality gatekeeper. The ONLY entity whose signal (`AUDIT_PASSED`) triggers task completion.

**Key responsibilities**:
- Verify every acceptance criterion has implementation evidence
- Execute all verification commands independently
- Check for quality tells (TODOs, placeholders, debug artifacts)
- Make pass/fail/blocked judgment

**Signals**: `AUDIT_PASSED: <task-id>`, `AUDIT_FAILED: <task-id>`, `AUDIT_BLOCKED: <task-id>`

### Business Analyst

**Spawn name**: `business-analyst`
**Model**: EXPERT_MODEL
**Agent definition**: `.claude/agents/business-analyst.md`

Transforms underspecified tasks into implementable specifications. Analyzes; does not implement.

**Signals**: `EXPANDED_TASK_SPECIFICATION: <task-id>`, `SEEKING_DIVINE_CLARIFICATION`

### Remediation

**Spawn name**: `remediation`
**Model**: EXPERT_MODEL
**Agent definition**: `.claude/agents/remediation.md`

Restores broken infrastructure to working state. Fixes systemic issues that block all development.

**Signals**: `REMEDIATION_COMPLETE`

### Health Auditor

**Spawn name**: `health-auditor`
**Model**: haiku
**Agent definition**: `.claude/agents/health-auditor.md`

Independently verifies codebase integrity after remediation. Does not trust remediation's claims.

**Signals**: `HEALTH_AUDIT: HEALTHY`, `HEALTH_AUDIT: UNHEALTHY`

---

## Teammate Spawning

For full spawning details and examples, see [Team Architecture - Spawning](team-architecture.md#spawning).

---

## Related Documentation

- [Team Architecture](team-architecture.md) - Full team structure, communication, and lifecycle
- [Signal Specification](signals/index.md) - Complete signal format reference
- Agent definitions: `.claude/agents/developer.md`, `critic.md`, `ripple.md`, `auditor.md`, `business-analyst.md`, `remediation.md`, `health-auditor.md`
- [Expert Prompt](../prompts/expert.md) - Expert advisory loop (inline, not a native agent definition)
- [Team Lead Prompt](../prompts/team-lead.md) - Team lead orchestration instructions
