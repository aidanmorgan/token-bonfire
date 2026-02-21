# Teammate Context Management

All teammates run as background `Task` calls with their own 1M token context window. Long-running tasks can exhaust context before completion. This document defines how teammates should manage their context to ensure reliable operation.

## Context Monitoring

Teammates should be aware of context usage throughout their work. While exact context metrics may not be available, teammates should:

1. **Track complexity**: Large codebases, many files, complex tasks consume more context
2. **Monitor response length**: Very long outputs indicate high context usage
3. **Be aware of repetition**: Repeated explanations or re-reading files suggests context pressure

## Optional Progress Checkpointing

Teammates MAY send CHECKPOINT signals to the team lead for progress visibility on complex tasks. Checkpoints are **optional** — the native Agent Teams heartbeat (~5 min) handles unresponsive detection automatically. CHECKPOINT signals are purely informational; no routing action is required from the team lead.

### Situations Where Checkpoints Are Useful

| Situation                          | Why a Checkpoint Helps                   |
|------------------------------------|------------------------------------------|
| Completed a major subtask          | Gives team lead visibility into progress |
| About to read multiple large files | Signals active work before a quiet period |
| Implementation exceeds 3 files     | Progress transparency on large tasks     |
| Verification phase begins          | Confirms implementation is done          |
| Stuck on an issue                  | Keeps team lead informed before trying next approach |

### Checkpoint Format

Sent via `TeammateTool({ operation: "write", to: "team-lead" })`:

```
CHECKPOINT: [task ID]
Status: [implementing | testing | awaiting-verification]
Completed:
- [concrete deliverable]
- [concrete deliverable]
Remaining:
- [specific next step]
- [specific next step]
Files Modified: [list of paths]
Estimated Progress: [N]%
```

## Context Exhaustion Handling

If a teammate detects it is running low on context (very long conversation, many iterations, large file operations), it should:

1. **Immediately send a checkpoint** to the team lead with current progress
2. **Save work-in-progress to files** (use scratch directory if needed)
3. **Signal the team lead** so the task can be reassigned or the teammate respawned

### Context Pause Signal

Sent via `TeammateTool({ operation: "write", to: "team-lead" })`:

```
CONTEXT PAUSE: [task ID]

Status: [current status]
Progress: [N]%

Work Saved:
- [file path]: [description]

Completed:
- [list of completed items]

Remaining:
- [list of remaining items]

Resume Instructions:
[specific instructions for resuming this work]
```

On receiving this signal, the team lead can:
- Respawn the teammate from its persisted prompt file (for experts, from `.claude/experts/<plan_slug>/<name>.md`)
- Include the resume instructions in the respawn prompt
- The teammate starts with a fresh context but can pick up where the previous instance left off

## Scratch Directory Usage

When context is limited or work is complex, teammates should use the scratch directory:

- **Location**: `{{SCRATCH_DIR}}/[task_id]/`
- **Purpose**: Store intermediate work, analysis results, notes
- **Files to create**:
    - `analysis.md`: Understanding of the task and codebase
    - `plan.md`: Implementation plan with checklist
    - `progress.md`: Running log of completed items
    - `blockers.md`: Issues encountered and attempted solutions

## Recovery from Context Exhaustion

When a teammate is respawned after context pause:

1. **Read scratch files**: Restore context from saved analysis and progress
2. **Check the task state**: Call `TaskGet` to see current task status
3. **Verify current state**: Check if partial work was saved correctly
4. **Continue from resume point**: Don't restart from beginning

The team lead includes resume context in the respawn prompt:

```
Resume Context: [last checkpoint summary]
Previous Progress: Review existing work before continuing.
Scratch Directory: {{SCRATCH_DIR}}/[task_id]/
```

## Best Practices

### Do

- Optionally send CHECKPOINT signals after significant milestones for team lead visibility
- Save analysis to scratch files for complex tasks
- Be concise in explanations (save context for work)
- Use references instead of repeating content
- Signal early if context is becoming constrained

### Don't

- Send checkpoints so frequently they clutter the mailbox (they are optional, not required)
- Repeat large code blocks in explanations
- Re-read files unnecessarily (cache key information)
- Provide lengthy explanations when short ones suffice
- Ignore signs of context pressure

## Role-Specific Guidance

### Developers

- Optionally checkpoint after each file implementation for team lead visibility
- Save implementation plan to scratch before coding
- Use incremental verification (test after each file)

### Auditor

- Optionally checkpoint after reviewing each criterion
- Save verification results to scratch as you go
- Don't re-run tests unnecessarily

### Business Analyst

- Save domain research to scratch immediately
- Optionally checkpoint after analyzing each ambiguity
- Preserve research even if specification not complete

### Remediation

- Optionally checkpoint after each fix attempt
- Document what was tried in scratch
- Save diagnostic output for debugging

### Health Auditor

- This teammate uses haiku model — context exhaustion is rare
- CHECKPOINT signals are rarely needed

## Progress Monitoring (Team Lead)

The team lead monitors developer progress through the shared task list and mailbox messages. In the native Agent Teams system, there is no custom checkpoint collection mechanism — teammates maintain their own context and signal progress through the standard communication protocol.

### Via Shared Task List

The team lead calls `TaskList` periodically to see:
- Which tasks are `pending`, `in_progress`, `completed`, etc.
- Which tasks have been claimed by developers
- Which tasks are blocked on dependencies

### Via Mailbox Messages

Developers communicate progress through standard signals:
- `READY_FOR_REVIEW: <task-id>` — implementation complete, self-verified
- `NEED_CLARIFICATION: <question>` — blocked, needs guidance
- `INFRA_BLOCKED: <details>` — infrastructure issue
- `FILE_CONFLICT: <file> <details>` — ownership conflict

### Heartbeat Timeout

Each teammate has a native heartbeat. If a teammate stops responding:
- Heartbeat timeout (~5 min) detects the issue
- Orphaned tasks auto-release and become available for other developers
- Team lead can respawn the teammate from its agent definition

### Stalled Developer Detection

If a developer has claimed a task (`in_progress`) but has not signaled `READY_FOR_REVIEW` or any other message for an extended period:

1. Team lead can send a message via `write` asking for a status update
2. If the developer responds: continue monitoring
3. If the developer does not respond (heartbeat timeout): the native system releases the task
4. Team lead respawns the developer using `subagent_type: "developer"` which loads `.claude/agents/developer.md`

### Progress Dashboard

The team lead periodically reports status:

```
FLOW STATUS: [N] developers active | [N] tasks pending | [N] in critic | [N] in audit | [N]/[total] complete
```

For detailed status:

```
PROGRESS DASHBOARD
==================
Active developers: [N]
Overall: [N]/[total] tasks complete ([percentage]%)

Task Status:
- [task-id]: in_progress (claimed by <dev-N>)
- [task-id]: ready_for_review (waiting for critic)
- [task-id]: in_review (with auditor)

Pending: [N] tasks ready
Blocked: [N] tasks waiting on dependencies
```

The native Agent Teams system eliminates the need for custom checkpoint protocols because:
- Teammates are self-organizing (claim tasks, implement, signal when done)
- The shared task list provides real-time visibility into task state
- Heartbeat timeouts handle unresponsive teammates automatically
- The `TeammateIdle` hook prevents developers from going idle unnecessarily

---

## Cross-References

- Signal formats: [signals/index.md](signals/index.md)
- Timeout values: [timeout-specification.md](timeout-specification.md)
- Task state tracking: [state/index.md](state/index.md)
- Team architecture: [team-architecture.md](team-architecture.md)
- Troubleshooting: [troubleshooting.md](troubleshooting.md)
