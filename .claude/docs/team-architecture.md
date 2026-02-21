# Team Architecture

Bonfire uses Claude Code's native Agent Teams (experimental, v2.1.32+) to coordinate parallel implementation work. This document describes the team structure, developer spawning, expert advisor generation, communication protocol, task lifecycle, and decomposition strategy.

## Native Primitives Used

| Primitive | What It Does |
|-----------|-------------|
| `TeammateTool({ operation: "spawnTeam", team_name: "<plan_slug>" })` | Creates the team with a slug-based name, makes the caller the team lead |
| `Task({ team_name, name: "<name>", run_in_background: true })` | Spawns a named teammate (developer, expert advisor, etc.) with its own 1M token context window |
| `TaskCreate` / `TaskUpdate` / `TaskList` / `TaskGet` | Shared task list with native atomic operations for safe concurrent claims |
| `TeammateTool({ operation: "write", to })` | Targeted mailbox message to a specific teammate |
| `TeammateTool({ operation: "requestShutdown" })` | Graceful teammate shutdown |
| `TeammateTool({ operation: "cleanup" })` | Remove team resources after all teammates shut down |

## Shared Task List & Plan Slug

The shared task list is the central coordination mechanism. It is identified by the **plan slug** — a deterministic, URL-safe string derived from the plan title by the bootstrapper script (`generate-orchestrator.py`).

**Key properties:**
- Same plan title always produces the same slug (e.g., "User Auth Implementation" → `user-auth-implementation`)
- The slug is used as both the `team_name` for `spawnTeam` and the task list identifier
- Tasks persist on disk, so re-running the same plan loads the existing task list with all progress intact
- All teammates (developers, expert advisors, critic, and auditor) share the same task list via the native `TaskCreate`/`TaskUpdate`/`TaskList`/`TaskGet` tools

## Team Structure

| Role | Count | Model | Purpose |
|------|-------|-------|---------|
| Team Lead | 1 (the main session) | opus | Orchestrates the team, generates expert advisors, manages task lifecycle, dispatches reviews |
| Developers | 2–MAX_DEVELOPERS | EXPERT_MODEL | Generic parallel implementers, claim tasks, write code, self-verify, consult expert advisors |
| Named Expert Advisors | 0–N (determined by gap analysis) | EXPERT_MODEL | Advisory only — answer developer questions, provide domain guidance, never write code |
| Critic | 1 | EXPERT_MODEL | Code quality reviewer (bugs, style, error handling, dead code) |
| Ripple | 1 | EXPERT_MODEL | Second-order effects analyst (downstream impact, API contracts, test coverage gaps) |
| Auditor | 1 | AUDITOR_MODEL | Acceptance criteria verifier, runs verification commands, sole authority for task completion |
| Business Analyst | 1 | EXPERT_MODEL | Transforms underspecified tasks into implementable specifications |
| Remediation | 1 | EXPERT_MODEL | Restores broken infrastructure to working state |
| Health Auditor | 1 | haiku | Independently verifies codebase integrity after remediation |

Configuration lives in `.claude/base_variables.md` (source of truth for all project settings).

## Native Agent Definitions

Static roles (developer, critic, ripple, auditor, business-analyst, remediation, health-auditor) are defined as native `.claude/agents/*.md` files with YAML frontmatter:

```yaml
---
name: <agent-name>
description: <one-line role description>
model: <sonnet|opus|haiku>
background: true
memory: project          # optional — persistent project memory
permissionMode: acceptEdits  # optional — for agents that write code
disallowedTools: Write, Edit, NotebookEdit  # optional — for read-only agents
---

# Role instructions (body)
...
```

When spawned with `subagent_type: "<agent-name>"`, the agent definition provides:
- **Role instructions** (the markdown body) — loaded automatically
- **Model** — from YAML frontmatter
- **Tool restrictions** — `disallowedTools` from YAML frontmatter
- **Memory** — `memory: project` for persistent agent memory
- **Permissions** — `permissionMode` from YAML frontmatter
- **Background** — `background: true` from YAML frontmatter

The `prompt` parameter in `Task()` carries only configuration tables from `base_variables.md` and dynamic content (developer identity, expert roster, resume flag).

**Expert advisors** remain `subagent_type: "general-purpose"` with full inline prompts because they are dynamically generated per plan from research.

## Developer Spawning

Developers are generic, parallel implementers. They are NOT domain specialists — they claim any available task and write code. When they encounter domain-specific questions, they request advice from expert advisors via the team lead.

Developers are spawned at startup as `dev-1`, `dev-2`, etc. using `subagent_type: "developer"` which loads role instructions from `.claude/agents/developer.md`. Configuration tables from `base_variables.md` are passed via the `prompt` parameter.

## Expert Advisor Generation

Expert advisors are **advisory-only** agents with deep domain knowledge generated from plan analysis and research. They never write code directly — they answer developer questions and provide domain guidance.

### How Expert Advisors Are Determined

1. **Gap analysis**: Team lead analyzes the plan to extract technologies, domains, and patterns
2. **Clustering**: Domains are grouped by affinity — each cluster becomes one named expert advisor
3. **Deep research**: For each expert advisor, the team lead performs targeted WebSearch on their technologies and synthesizes expert-level knowledge
4. **Prompt generation**: Each expert advisor gets a persisted prompt file with identity and domain expertise

### Expert Advisor Prompt Structure

Each expert advisor's prompt file (saved to `.claude/experts/<plan_slug>/<expert-name>.md`) contains:

```
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

### Expert Advisor Persistence

Expert advisor definitions are saved to `.claude/experts/<plan_slug>/`:
```
.claude/experts/
  user-auth-implementation/
    auth-expert.md
    database-expert.md
    api-expert.md
```

On resume, these files are loaded from disk — no regeneration needed. This is what enables crash recovery without losing the deep research investment.

### Spawning

The team lead is the main Claude Code session. It:
1. Generates or loads expert advisor definitions
2. Calls `spawnTeam` with `team_name: "<plan_slug>"` to create or rejoin the team
3. Spawns developers via `Task({ subagent_type: "developer", name: "dev-N", prompt: "<config tables>", run_in_background: true })`
4. Spawns each named expert advisor via `Task({ subagent_type: "general-purpose", name: "<expert-name>", prompt: "<full inline prompt>", run_in_background: true })`
5. Spawns static roles (critic, ripple, auditor, business-analyst, remediation, health-auditor) via `Task({ subagent_type: "<agent-name>", prompt: "<config tables>", run_in_background: true })`

**Context windows are isolated.** Each teammate gets its own 1M token context. Teammates do NOT inherit the lead's conversation history and cannot see each other's context. They only see:
- Their agent definition body (from `.claude/agents/*.md`, loaded automatically for native agents)
- The `prompt` parameter (config tables and dynamic content)
- CLAUDE.md files in the working directory (auto-loaded)
- Mailbox messages received via `write`

### Display Modes

Configured via `teammateMode` in `.claude/settings.json`:
- `"in-process"` — teammates run hidden, fastest (default for bonfire)
- `"tmux"` — visible split panes in tmux
- `"auto"` — tmux if available, in-process otherwise

Navigate between teammates with Shift+Up/Down. View task list with Ctrl+T.

## Communication Protocol

All inter-agent communication uses `TeammateTool({ operation: "write", to: "<name>" })` for targeted messages. **Never use `broadcast`** — it scales with team size and is expensive.

### Message Flow

```
Developer ──READY_FOR_REVIEW──> Team Lead ──review request──> Critic
Developer <──review feedback─── Team Lead <──REVIEW_FAILED── Critic
                                Team Lead ──ripple request──> Ripple (after Critic passes)
Developer <──ripple feedback─── Team Lead <──RIPPLE_FAILED── Ripple
                                Team Lead ──audit request──> Auditor (after Ripple passes)
                                Team Lead <──AUDIT_PASS/FAIL── Auditor

Developer ──NEED_EXPERT_ADVICE──> Team Lead ──question──> Expert Advisor
Developer <──domain guidance───── Team Lead <──EXPERT_ADVICE_PROVIDED── Expert Advisor
```

Developers communicate with the team lead only. Expert advisors communicate with the team lead only. The critic, ripple, and auditor communicate with the team lead only. No direct developer-expert, developer-critic, developer-auditor, or developer-developer messaging.

### Message Types

**Developer → Team Lead:**
- `READY_FOR_REVIEW: <task-id>` — task implemented and self-verified
- `NEED_CLARIFICATION: <question>` — ambiguous requirements or missing dependency
- `NEED_EXPERT_ADVICE: <question>` — needs domain guidance from an expert advisor
- `INFRA_BLOCKED: <details>` — infrastructure prevents progress
- `FILE_CONFLICT: <file> <details>` — needs to modify file outside ownership scope

**Expert Advisor → Team Lead:**
- `EXPERT_ADVICE_PROVIDED: <response>` — domain guidance in response to a developer question

**Critic → Team Lead:**
- `REVIEW_PASSED: <task-id>` — code quality checks passed
- `REVIEW_FAILED: <task-id> [feedback]` — code quality issues found

**Ripple → Team Lead:**
- `RIPPLE_PASSED: <task-id>` — no breaking/degrading/gap impacts found
- `RIPPLE_FAILED: <task-id> [feedback]` — second-order issues found

**Auditor → Team Lead:**
- `AUDIT_PASSED: <task-id>` — acceptance criteria verified, all verification commands pass
- `AUDIT_FAILED: <task-id> [feedback]` — acceptance criteria not met
- `AUDIT_BLOCKED: <task-id> [details]` — pre-existing infrastructure failures prevent verification

**Team Lead → Developer:**
- Review feedback (forwarded from critic, ripple, or auditor)
- Clarification responses
- Expert advice (forwarded from expert advisor)
- File ownership resolution
- Infrastructure fix confirmations

**Team Lead → Expert Advisor:**
- Developer questions requiring domain guidance

**Team Lead → Critic:**
- Review requests with task ID, modified files, code context

**Team Lead → Ripple:**

| Message | When | Content |
|---|---|---|
| Ripple request | Critic passed review | Task ID, modified files, summary, critic assessment |

**Team Lead → Auditor:**
- Audit requests with task ID, acceptance criteria, modified files, environment

## Task Lifecycle

```
pending → in_progress → ready_for_review → in_critic_review → in_ripple_review → in_audit → completed
                                                                                              ↘ needs_rework → in_progress (loop)
```

1. **pending**: Task created, waiting for dependencies or a developer
2. **in_progress**: Developer claimed via `TaskUpdate({ status: "in_progress" })`
3. **ready_for_review**: Developer self-verified, sent `READY_FOR_REVIEW` to lead
4. **in_critic_review**: Team lead dispatched review request to critic
5. **in_ripple_review**: Critic passed, team lead dispatched ripple request
6. **in_audit**: Ripple passed, team lead dispatched audit request to auditor
7. **completed**: Auditor passed (`AUDIT_PASSED`), team lead called `TaskUpdate({ status: "completed" })`
8. **needs_rework**: Critic, ripple, or auditor failed, lead forwarded feedback to developer

Only the team lead marks tasks `completed`. Developers, the critic, and the auditor never do.

## Task Dependencies

Dependencies use the native `addBlockedBy` on `TaskUpdate`. The bootstrapper script parses `Blocked By` fields from the plan file.

**Dependencies auto-unblock.** When a blocking task is marked `completed`, all tasks that were `blockedBy` it automatically become available. No manual unblocking needed.

Task claiming uses native atomic operations to prevent race conditions when multiple developers try to claim the same task.

## Task Claiming by Developers

Developers are generic and claim any available unblocked task from the shared task list. There is no task affinity — any developer can work on any task.

- Developers check `TaskList` for pending, unblocked tasks
- They claim tasks via `TaskUpdate({ status: "in_progress" })` (native atomic to prevent races)
- When a developer encounters a domain-specific challenge, they signal `NEED_EXPERT_ADVICE` to the team lead, who routes the question to the appropriate expert advisor
- The team lead can also assign tasks to specific developers via mailbox messages

## Task Decomposition Strategy

Good decomposition is critical for parallel teams. The lead performs this analysis during gap analysis before creating tasks.

### Principles

1. **Non-overlapping file sets** — each task owns specific files. No two concurrent tasks modify the same file.
2. **Clear interface boundaries** — tasks interact through defined contracts (types, APIs), not shared mutable state.
3. **Minimal cross-task dependencies** — maximize parallelizable work.
4. **Testable in isolation** — each task can be verified independently.
5. **Domain clustering** — group related tasks so developers can consult the same expert advisor.

### Single-Writer Pattern

When a file must be touched by multiple tasks:
- Assign **one task** as the owner of that file
- Other tasks depend on it via `blockedBy`
- The owning task creates the foundation; dependent tasks extend it after it completes

### Interface-First Pattern

When multiple tasks share types or API contracts:
1. Create a **contract task** that defines types, interfaces, and schemas
2. All implementation tasks `blockedBy` the contract task
3. Developers implement against the defined contracts without modifying them
4. Prevents parallel developers from creating conflicting type definitions

## Developer Self-Organization

Developers are self-organizing. They:
1. Check `TaskList` for pending, unblocked tasks
2. Claim the task via `TaskUpdate({ status: "in_progress" })` (native atomic)
3. Read required files, implement, consult expert advisors if needed, self-verify
4. Signal `READY_FOR_REVIEW` to lead via `write`
5. Immediately claim next task or process review feedback — never idle

The `TeammateIdle` hook (configured in `.claude/settings.json`) prompts developers to check for available work or mailbox messages when they stop.

## File Ownership

To prevent conflicts when multiple developers edit concurrently:
- Task descriptions specify which files the developer owns
- Developers ONLY modify files within their task's scope
- Shared files (config, `__init__.py`, type exports) use additive-only changes (append, never restructure)
- Developers signal `FILE_CONFLICT` to the lead if they discover they need files outside their scope
- The lead identifies potential conflicts during gap analysis before task creation

## Verification Protocol

Two levels of verification ensure quality:

### Developer Commands (self-verification by developers)
Run before signaling ready-for-review. Defined in `base_variables.md` under "Developer Commands". Typically: sync deps, fix lints, format, run tests.

### Verification Commands (independent verification by auditor)
Run by the auditor after receiving an audit request. Defined in `base_variables.md` under "Verification Commands". Typically: type check, unit/integration/e2e tests, lint check, format check.

Both sets of commands are project-specific and read from configuration, not hardcoded.

## Resume & Crash Recovery

Because expert advisor definitions are persisted to `.claude/experts/<plan_slug>/` and the shared task list is keyed by `plan_slug`, Bonfire supports seamless resume:

1. Re-run `/bonfire $PLAN_FILE` — the bootstrapper produces the same `plan_slug`
2. Team lead finds expert advisor files on disk → loads them (no regeneration)
3. Team lead calls `TaskList` and finds existing tasks → audits state
4. Spawns fresh developers and expert advisors using the persisted prompts — developers claim pending tasks
5. Completed tasks stay completed; orphaned in-progress tasks auto-release

This means a crashed session, interrupted plan, or new Claude Code session can pick up exactly where it left off — including the deep research investment in expert advisor prompts.

## Failure Handling

For detailed failure handling, timeout recovery, and respawn procedures, see [agent-timeout-recovery.md](agent-timeout-recovery.md).

## Shutdown Sequence

1. Lead calls `requestShutdown` for each teammate
2. Each teammate finishes current work, sends `shutdown_approved`
3. Lead calls `cleanup` to remove team resources
4. Lead reports final status to user

## Quality Assurance Checklist (Completion)

Before the lead reports success:
- [ ] All tasks marked `completed` (none stuck)
- [ ] All tasks passed critic review (`REVIEW_PASSED`), ripple analysis (`RIPPLE_PASSED`), and auditor verification (`AUDIT_PASSED`)
- [ ] No hanging developers or expert advisors
- [ ] Final verification commands pass
- [ ] No inconsistent code style across developers
- [ ] Clean working tree (no uncommitted debris)

## Known Limitations

For known limitations and common issues, see [troubleshooting.md](troubleshooting.md).

## Key Files

For the complete key files reference, see the Key Files table in [CLAUDE.md](../../CLAUDE.md).
