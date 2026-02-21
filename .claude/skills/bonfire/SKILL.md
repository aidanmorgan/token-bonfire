---
name: bonfire
description: Bootstrap an implementation plan and coordinate a parallel team of named agents using native Agent Teams.
---

# Bonfire — Parallel Implementation Team Lead

Parse an implementation plan into tasks, generate domain expert knowledge bases, and coordinate parallel execution through developer agents with a staged review pipeline and independent verification.

## Parameters

| Parameter   | Required | Description                          |
|-------------|----------|--------------------------------------|
| `plan_file` | Yes      | Path to the implementation plan file |

## Invocation

```
/bonfire COMPREHENSIVE_IMPLEMENTATION_PLAN.md
```

## Named Teammates

Every bonfire team consists of these named teammates. **ALL must be spawned for the plan to proceed.**

### Core Pipeline Agents (always spawned, always active)

| Name | Role | Model | Count | Agent Definition | Spawned When |
|------|------|-------|-------|------------------|-------------|
| `dev-1` through `dev-N` | **Developer Agent** — general-purpose implementer. Claims tasks, writes code, runs tests. Consults experts when domain knowledge is needed. | `DEVELOPER_MODEL` | `NUM_DEVELOPERS` (default 5) | `.claude/agents/developer.md` | Always |
| `critic` | **Critic** — code quality gatekeeper. Reviews developer code for bugs, style, error handling, dead code. Does NOT verify acceptance criteria. Signals `REVIEW_PASSED` or `REVIEW_FAILED`. | `EXPERT_MODEL` | 1 | `.claude/agents/critic.md` | Always |
| `ripple` | **Ripple** — second-order effects analyst. Analyzes downstream impact of changes: broken consumers, altered API contracts, test coverage gaps, behavioral drift. Does NOT review first-order quality or acceptance criteria. Signals `RIPPLE_PASSED` or `RIPPLE_FAILED`. | `EXPERT_MODEL` | 1 | `.claude/agents/ripple.md` | Always |
| `auditor` | **Auditor** — acceptance criteria verifier. SOLE AUTHORITY for task completion. Independently runs all verification commands, verifies every acceptance criterion with evidence. Signals `AUDIT_PASSED`, `AUDIT_FAILED`, or `AUDIT_BLOCKED`. | `AUDITOR_MODEL` | 1 | `.claude/agents/auditor.md` | Always |

### Reactive Agents (always spawned, activate on demand)

| Name | Role | Model | Count | Agent Definition | Activates When |
|------|------|-------|-------|------------------|----------------|
| `<expert-name>` (e.g., `auth-expert`, `database-expert`) | **Expert Advisor** — domain-specialized knowledge source. Provides advice, patterns, pitfalls, and design guidance to developers. Does NOT write code directly. | `EXPERT_MODEL` | 2–`MAX_EXPERTS` | `.claude/experts/<plan_slug>/<expert-name>.md` (inline prompt) | Developer signals `NEED_EXPERT_ADVICE` for a task in this expert's domain |
| `business-analyst` | **Business Analyst** — requirement expansion specialist. Expands underspecified tasks into implementable specifications with verifiable acceptance criteria. Searches codebase for patterns to ground decisions. Signals `EXPANDED_TASK_SPECIFICATION` or `SEEKING_DIVINE_CLARIFICATION`. | `EXPERT_MODEL` | 1 | `.claude/agents/business-analyst.md` | Task is underspecified or acceptance criteria are untestable |
| `remediation` | **Remediation** — infrastructure repair specialist. Diagnoses and fixes verification failures that block development. Applies minimal targeted fixes. Never disables checks. Signals `REMEDIATION_COMPLETE`. | `EXPERT_MODEL` | 1 | `.claude/agents/remediation.md` | Infrastructure verification fails and blocks development |
| `health-auditor` | **Health Auditor** — codebase health verifier. Independently runs all verification commands after remediation to confirm fixes worked. Binary judgment only. Signals `HEALTH_AUDIT: HEALTHY` or `HEALTH_AUDIT: UNHEALTHY`. | `haiku` | 1 | `.claude/agents/health-auditor.md` | After remediation completes, to verify fixes |

### Task Flow Through Named Agents

```
Task (underspecified?) ──→ business-analyst ──→ Expanded Specification
                                                       │
Task (clear) ─────────────────────────────────────────→ │
                                                       ▼
                                                  developer agent
                                                  (implements code)
                                                  │              │
                                     NEED_EXPERT_ADVICE    READY_FOR_REVIEW
                                                  │              │
                                                  ▼              ▼
                                             expert advisor   critic
                                          (provides guidance)  (code quality review)
                                                  │           │        │
                                          advice returned  REVIEW_PASSED  REVIEW_FAILED
                                          developer continues  │        └──→ developer reworks
                                                              ▼
                                                             ripple
                                                    (second-order effects analysis)
                                                          │        │
                                                  RIPPLE_PASSED  RIPPLE_FAILED
                                                          │        └──→ developer reworks
                                                          ▼
                                                        auditor
                                                (acceptance verification)
                                                    │     │       │
                                            AUDIT_PASSED  │  AUDIT_BLOCKED
                                                    │     │       └──→ remediation
                                                    │  AUDIT_FAILED          │
                                                    │     └──→ developer REMEDIATION_COMPLETE
                                                    │          reworks         │
                                                    ▼                    health-auditor
                                              Task Complete                   │
                                                                    HEALTHY / UNHEALTHY
                                                                      │          │
                                                                 resume      retry
                                                                development  remediation
```

## Workflow

### Step 1: Bootstrap the Plan

#### Step 1a: Extract plan metadata

Run the plan bootstrapper to get plan identity:

```bash
python .claude/scripts/generate-orchestrator.py "$plan_file"
```

This outputs JSON to stdout containing:
- `plan_title` — human-readable plan name
- `plan_slug` — deterministic slug derived from the title (shared task list name and team name)

The `plan_slug` ensures re-running the same plan reuses the same shared task list and expert definitions.

#### Step 1b: Parse tasks via sub-agent

Spawn a sub-agent to read the plan file, identify all tasks and their dependencies, and create them in the shared task list. This replaces rigid regex parsing with Claude's ability to understand any plan format.

```
Task({
  description: "Parse plan into tasks",
  subagent_type: "general-purpose",
  prompt: "<see below>"
})
```

The sub-agent prompt MUST include:

1. The full plan file path to read
2. The `plan_slug` (for context, not for task list naming — the sub-agent uses TaskCreate/TaskUpdate directly)
3. These explicit instructions:

```
You are a plan parser. Read the plan file at "<plan_file>" and extract every task into the shared task list.

For EACH task you find in the plan:

1. Call TaskCreate with:
   - subject: "<task-id>: <task-title>" (e.g., "C-1: Implement PushdownEntityScope DataFusion Optimizer Rule")
   - description: Include ALL of the following from the plan:
     - The problem description / work to be done
     - Unit test plan (if present)
     - Acceptance criteria (as a checklist)
     - Crate(s) and file(s) affected
     - Design reference documents
   - activeForm: A present-continuous summary (e.g., "Implementing PushdownEntityScope optimizer rule")

2. Track the mapping of plan task IDs (e.g., "C-1", "H-3") to TaskCreate-assigned numeric IDs.

3. After ALL tasks are created, set up dependencies using TaskUpdate:
   - Tasks within the same execution wave/phase can run in parallel (no dependencies between them)
   - Tasks in later waves depend on tasks from earlier waves that touch the same crate or subsystem
   - Use the plan's "Execution Strategy" or "Phases" section to determine wave groupings
   - Call TaskUpdate({ taskId: "<numeric-id>", addBlockedBy: ["<numeric-id>", ...] }) for each dependency

4. Skip any tasks marked as "COMPLETE" or already done.

5. After creating all tasks, respond with a summary:
   - Total tasks created
   - Number of execution waves/phases identified
   - The ID mapping (plan-ID -> numeric-ID) so the team lead can reference tasks
   - Any tasks that were skipped and why

IMPORTANT:
- Do NOT invent dependencies that aren't implied by the plan structure
- Do NOT skip tasks just because they lack explicit "Blocked By" fields — infer wave membership from the plan's execution strategy section
- Tasks within the same wave should NOT block each other
- If the plan has no explicit execution order, create all tasks with no dependencies (flat list)
```

**Wait for the sub-agent to complete** before proceeding. The sub-agent's response provides the task ID mapping needed for expert assignment.

### Step 2: Read Team Configuration

Read these files:
- `.claude/prompts/team-lead.md` — Team lead instructions
- `.claude/prompts/expert.md` — Expert advisory loop (embedded in every expert advisor's spawn prompt)
- `.claude/base_variables.md` — Project configuration

**Note:** Static role instructions for developer, critic, ripple, auditor, business-analyst, remediation, and health-auditor are defined in `.claude/agents/*.md` and loaded automatically when spawning with `subagent_type: "<agent-name>"`. You do NOT need to read these files.

Extract from `base_variables.md`:
- `NUM_DEVELOPERS` (default 5)
- `DEVELOPER_MODEL` (default sonnet)
- `MAX_EXPERTS` (default 3)
- `EXPERT_MODEL` (default sonnet)
- `AUDITOR_MODEL` (default opus)
- Developer Commands table
- Verification Commands table
- Agent Reference Documents table
- Environments table
- MCP Servers table

### Step 3: Detect Resume vs Fresh Start

Check two things:
1. **Expert definitions on disk**: Do `.md` files exist at `.claude/experts/<plan_slug>/`?
2. **Shared task list**: Call `TaskList` — are there existing tasks?

| Experts on disk? | Tasks exist? | Mode |
|-----------------|-------------|------|
| No | No | **FRESH START** |
| Yes | Yes | **RESUME** |
| Yes | No | **EXPERT REUSE** |
| No | Yes | **ORPHANED TASKS** |

### Step 4: Assume Team Lead Role

Follow the team lead instructions from `.claude/prompts/team-lead.md`. Use **Delegate Mode** (Shift+Tab) so you don't grab implementation work.

#### Fresh Start (no experts, no tasks):

1. **Gap analysis** — analyze the plan to determine what domain expert knowledge bases are needed. Cluster tasks by domain affinity. Each cluster becomes a named expert advisor.

2. **Deep domain research** — for each expert, WebSearch their technologies for best practices, pitfalls, and patterns. Synthesize into expert-level knowledge (not surface-level tips).

3. **Generate expert prompt files** — write each expert's definition to `.claude/experts/<plan_slug>/<expert-name>.md` with identity, domain expertise, and applicable tasks.

4. **Create tasks** in the shared task list:
   - `TaskCreate` for each task with subject, description, activeForm
   - `TaskUpdate({ addBlockedBy })` for dependencies

5. **Spawn the team** (see Spawn Procedure below)

#### Resume (experts on disk, tasks exist):

1. **Load expert definitions** from `.claude/experts/<plan_slug>/` — do NOT regenerate
2. **Skip research** — expert definitions already contain domain knowledge
3. **Audit task state** — report completed/pending/blocked/orphaned
4. **Spawn the team** (see Spawn Procedure below)

#### Expert Reuse (experts on disk, no tasks):

1. **Load expert definitions** from disk
2. **Skip research**
3. **Create tasks** in the shared task list
4. **Spawn the team**

#### Orphaned Tasks (no experts, tasks exist):

1. **Gap analysis + research + generate experts** (full expert generation)
2. **Audit task state** (don't recreate tasks)
3. **Spawn the team**

### Step 5: Spawn Team

**ALL named teammates listed below MUST be spawned. The plan CANNOT proceed with any missing.**

#### Spawn Procedure

**Step 5.1: Create the team** using the `plan_slug`:

```
TeamCreate({ team_name: "<plan_slug>" })
```

**Step 5.2: Spawn ALL developer agents** — one `Task` call per developer, all in parallel in a single message:

```
Task({
  team_name: "<plan_slug>",
  name: "dev-<N>",
  subagent_type: "developer",
  prompt: "<config tables + dynamic content>",
  run_in_background: true
})
```

The agent definition (`.claude/agents/developer.md`) provides the role instructions, model, and permissions automatically. The `prompt` parameter carries only dynamic content:

1. Developer identity: "You are `dev-<N>`, a developer agent on a parallel implementation team."
2. Fresh start vs resume flag
3. Developer commands table (from `base_variables.md`)
4. Agent reference documents table (from `base_variables.md`)
5. Environments table (from `base_variables.md`)
6. MCP servers table (from `base_variables.md`)
7. **Expert roster** — list of available expert advisors and their domains, so the developer knows who to ask for help:
   ```
   Available Expert Advisors:
   - <expert-name-1>: <domain description> (tasks: <task-ids>)
   - <expert-name-2>: <domain description> (tasks: <task-ids>)
   ...
   When you need domain-specific guidance, signal NEED_EXPERT_ADVICE to the team lead
   specifying which expert and your question.
   ```

**Developers are generalists.** They can claim ANY task from the task list. They do not have task affinity — any developer can work on any task. When a task requires deep domain knowledge, the developer signals `NEED_EXPERT_ADVICE` and the team lead routes the question to the appropriate expert advisor.

**Step 5.3: Spawn ALL named expert advisors** — one `Task` call per expert, all in parallel:

Expert advisors use `subagent_type: "general-purpose"` with full inline prompts (they are dynamically generated per plan, not static agent definitions).

```
Task({
  team_name: "<plan_slug>",
  name: "<expert-name>",
  subagent_type: "general-purpose",
  model: "<EXPERT_MODEL>",
  prompt: "<FULL self-contained expert advisor prompt>",
  run_in_background: true
})
```

Each expert advisor's spawn prompt MUST include (in this order):
1. Expert definition file (from `.claude/experts/<plan_slug>/<expert-name>.md`)
2. **Advisor role instructions** (NOT developer.md — experts do NOT implement):
   ```
   You are an expert advisor on a parallel implementation team. You do NOT write code or claim tasks.
   Your role is to provide domain-specific guidance when developer agents ask for help.

   When you receive a question from the team lead (routed from a developer):
   1. Read the relevant code/files to understand the current state
   2. Provide specific, actionable advice grounded in your domain expertise
   3. Include code examples, patterns, or references from your knowledge base
   4. Signal EXPERT_ADVICE_PROVIDED with your response

   When not answering questions, you are idle. Do not claim tasks or write code.
   Wait for the team lead to route questions to you.
   ```
3. Agent reference documents table (from `base_variables.md`)
4. Environments table (from `base_variables.md`)

**Step 5.4: Spawn the `critic`:**

```
Task({
  team_name: "<plan_slug>",
  name: "critic",
  subagent_type: "critic",
  prompt: "<config tables>",
  run_in_background: true
})
```

The agent definition (`.claude/agents/critic.md`) provides role instructions, model, memory, and tool restrictions automatically. The `prompt` parameter carries only:
1. Agent reference documents table (from `base_variables.md`)
2. Environments table (from `base_variables.md`)
3. MCP servers table (from `base_variables.md`)

**Step 5.5: Spawn the `ripple`:**

```
Task({
  team_name: "<plan_slug>",
  name: "ripple",
  subagent_type: "ripple",
  prompt: "<config tables>",
  run_in_background: true
})
```

The agent definition (`.claude/agents/ripple.md`) provides role instructions, model, memory, and tool restrictions automatically. The `prompt` parameter carries only:
1. Agent reference documents table (from `base_variables.md`)
2. Environments table (from `base_variables.md`)
3. MCP servers table (from `base_variables.md`)

**Step 5.6: Spawn the `auditor`:**

```
Task({
  team_name: "<plan_slug>",
  name: "auditor",
  subagent_type: "auditor",
  prompt: "<config tables>",
  run_in_background: true
})
```

The agent definition (`.claude/agents/auditor.md`) provides role instructions, model, memory, and tool restrictions automatically. The `prompt` parameter carries only:
1. Verification commands table (from `base_variables.md`)
2. Agent reference documents table (from `base_variables.md`)
3. Environments table (from `base_variables.md`)
4. MCP servers table (from `base_variables.md`)

**Step 5.7: Spawn the `business-analyst`:**

```
Task({
  team_name: "<plan_slug>",
  name: "business-analyst",
  subagent_type: "business-analyst",
  prompt: "<config tables>",
  run_in_background: true
})
```

The agent definition (`.claude/agents/business-analyst.md`) provides role instructions, model, and tool restrictions automatically. The `prompt` parameter carries only:
1. Agent reference documents table (from `base_variables.md`)
2. MCP servers table (from `base_variables.md`)

**Step 5.8: Spawn the `remediation` agent:**

```
Task({
  team_name: "<plan_slug>",
  name: "remediation",
  subagent_type: "remediation",
  prompt: "<config tables>",
  run_in_background: true
})
```

The agent definition (`.claude/agents/remediation.md`) provides role instructions, model, and permissions automatically. The `prompt` parameter carries only:
1. Developer commands table (from `base_variables.md`)
2. Verification commands table (from `base_variables.md`)
3. Environments table (from `base_variables.md`)
4. MCP servers table (from `base_variables.md`)

**Step 5.9: Spawn the `health-auditor`:**

```
Task({
  team_name: "<plan_slug>",
  name: "health-auditor",
  subagent_type: "health-auditor",
  prompt: "<config tables>",
  run_in_background: true
})
```

The agent definition (`.claude/agents/health-auditor.md`) provides role instructions, model, and tool restrictions automatically. The `prompt` parameter carries only:
1. Verification commands table (from `base_variables.md`)
2. Environments table (from `base_variables.md`)
3. MCP servers table (from `base_variables.md`)

**Step 5.10: Verify all teammates spawned.** Confirm every named teammate is running before entering the execution phase. Log the full roster:

```
TEAM SPAWNED for <plan_slug>:
  Developers:       dev-1, dev-2, dev-3, dev-4, dev-5
  Expert Advisors:  <expert-1>, <expert-2>, ..., <expert-N>
  Critic:           critic
  Ripple:           ripple
  Auditor:          auditor
  Business Analyst: business-analyst
  Remediation:      remediation
  Health Auditor:   health-auditor
  Total teammates:  <5+N+6>
```

### Step 6: Execution Phase

Monitor mailbox continuously. Route messages through the staged pipeline:

**From developer agents:**
- `READY_FOR_REVIEW: <task-id>` → `write` review request to `critic`
- `NEED_EXPERT_ADVICE: <expert-name> <question>` → `write` question to the named expert advisor
- `NEED_CLARIFICATION: <question>` → route to `business-analyst` or escalate via `AskUserQuestion`
- `INFRA_BLOCKED: <details>` → `write` to `remediation`
- `FILE_CONFLICT: <details>` → coordinate ownership between developers

**From expert advisors:**
- `EXPERT_ADVICE_PROVIDED: <task-id> [advice]` → `write` advice back to the requesting developer

**From `critic`:**
- `REVIEW_PASSED: <task-id>` → `write` ripple request to `ripple`
- `REVIEW_FAILED: <task-id> [feedback]` → `write` feedback to owning developer for rework

**From `ripple`:**
- `RIPPLE_PASSED: <task-id>` → `write` audit request to `auditor`
- `RIPPLE_FAILED: <task-id> [feedback]` → `write` feedback to owning developer for rework

**From `auditor`:**
- `AUDIT_PASSED: <task-id>` → `TaskUpdate({ status: "completed" })` — **ONLY the auditor's pass triggers completion**
- `AUDIT_FAILED: <task-id> [feedback]` → `write` feedback to owning developer for rework
- `AUDIT_BLOCKED: <task-id> [details]` → `write` to `remediation`

**From `business-analyst`:**
- `EXPANDED_TASK_SPECIFICATION: <task-id>` → update task description, route to developer
- `SEEKING_DIVINE_CLARIFICATION: <question>` → escalate to user via `AskUserQuestion`

**From `remediation`:**
- `REMEDIATION_COMPLETE` → `write` to `health-auditor` to verify fixes

**From `health-auditor`:**
- `HEALTH_AUDIT: HEALTHY` → resume normal development flow
- `HEALTH_AUDIT: UNHEALTHY [details]` → `write` details back to `remediation` for retry

### Step 7: Completion

When ALL tasks are `completed` (via `AUDIT_PASSED`):
- Send `shutdown_request` to EACH teammate
- Wait for shutdown responses from each
- `TeamDelete` to remove team resources
- Report final status to user

## Error Handling

| Error                      | Action                                                            |
|----------------------------|-------------------------------------------------------------------|
| Script execution fails     | Output error message and stop                                     |
| base_variables.md missing  | Output: "Create .claude/base_variables.md first"                  |
| Plan file missing          | Output: "Plan file not found: $plan_file"                        |
| Task parser sub-agent fails | Review error, retry once, then escalate to user                  |
| Cycle detected in tasks    | Sub-agent reports cycle details; stop and escalate                |
| Developer crash            | Heartbeat timeout releases task; respawn with `subagent_type: "developer"` |
| Expert advisor crash       | Respawn from disk prompt with `subagent_type: "general-purpose"`; queued advice requests resume |
| Critic/Ripple/Auditor crash | Respawn by name (`subagent_type: "<agent-name>"`); queued reviews resume |
| Business-analyst crash     | Respawn with `subagent_type: "business-analyst"`; queued requests resume |
| Remediation crash          | Respawn with `subagent_type: "remediation"`; queued requests resume |
| Health-auditor crash       | Respawn with `subagent_type: "health-auditor"`; queued requests resume |
| Remediation stuck          | Escalate to user via `AskUserQuestion`                           |
| Auditor rejects 3+ times   | Investigate root cause, escalate if needed                       |
| Any teammate fails to spawn | HALT — do not proceed without the full team                      |

## Prerequisites

| Requirement            | Location                                   |
|------------------------|--------------------------------------------|
| Agent definitions      | `.claude/agents/` (developer, critic, ripple, auditor, business-analyst, remediation, health-auditor) |
| Base variables         | `.claude/base_variables.md`                |
| Team lead prompt       | `.claude/prompts/team-lead.md`             |
| Expert advisory loop   | `.claude/prompts/expert.md`                |
| Bootstrap script       | `.claude/scripts/generate-orchestrator.py` |
| Plan file              | `$plan_file`                               |

## Key Directories

| Directory | Purpose |
|-----------|---------|
| `.claude/agents/` | Native agent definitions (YAML frontmatter + role instructions) |
| `.claude/experts/<plan_slug>/` | Persisted expert knowledge bases (survive resume) |
| `.claude/prompts/` | Team lead prompt and expert advisory loop (static roles deprecated — see `.claude/agents/`) |
