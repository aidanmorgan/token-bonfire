# Agent Context Management

All agents run as Task calls with their own context window. Long-running tasks can exhaust context before completion.
This document defines how agents should manage their context to ensure reliable operation.

## Context Monitoring

Agents should be aware of context usage throughout their work. While exact context metrics may not be available, agents
should:

1. **Track complexity**: Large codebases, many files, complex tasks consume more context
2. **Monitor response length**: Very long outputs indicate high context usage
3. **Be aware of repetition**: Repeated explanations or re-reading files suggests context pressure

## Proactive Checkpointing

When working on complex tasks, agents should output progress checkpoints proactively:

### Checkpoint Triggers

| Trigger                            | Action                                 |
|------------------------------------|----------------------------------------|
| Completed a major subtask          | Output checkpoint with progress        |
| About to read multiple large files | Checkpoint first, then proceed         |
| Implementation exceeds 3 files     | Checkpoint after each file             |
| Verification phase begins          | Checkpoint implementation status       |
| Stuck on an issue                  | Checkpoint before trying next approach |

### Checkpoint Format

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

## Context Exhaustion Signal

If an agent detects it is running low on context (very long conversation, many iterations, large file operations), it
should:

1. **Immediately output a checkpoint** with current progress
2. **Save work-in-progress to files** (use scratch directory if needed)
3. **Signal for continuation**

### Context Pause Signal

```
CONTEXT PAUSE: [task ID]

Status: [current status]
Progress: [N]%

Work Saved:
- [file path]: [description]
- {{SCRATCH_DIR}}/[task_id]/work-in-progress.md: [summary of remaining work]

Completed:
- [list of completed items]

Remaining:
- [list of remaining items]

Resume Instructions:
[specific instructions for resuming this work]
```

## Scratch Directory Usage

When context is limited or work is complex, agents should use the scratch directory:

- **Location**: `{{SCRATCH_DIR}}/[task_id]/`
- **Purpose**: Store intermediate work, analysis results, notes
- **Files to create**:
    - `analysis.md`: Understanding of the task and codebase
    - `plan.md`: Implementation plan with checklist
    - `progress.md`: Running log of completed items
    - `blockers.md`: Issues encountered and attempted solutions

### Example Usage

```python
# Save analysis to scratch
write_file(f"{SCRATCH_DIR}/{task_id}/analysis.md", """
# Task Analysis: {task_id}

## Understanding
- [what the task requires]

## Codebase Context
- [relevant patterns found]

## Dependencies
- [files that need modification]
""")
```

## Recovery from Context Exhaustion

When a task is resumed after context pause:

1. **Read previous checkpoint**: Look for most recent checkpoint output
2. **Read scratch files**: Restore context from saved analysis and progress
3. **Verify current state**: Check if partial work was saved correctly
4. **Continue from resume point**: Don't restart from beginning

### Resume Context Format (provided by coordinator)

```
Resume Context: [last checkpoint summary]
Previous Progress: Review existing work before continuing.
Scratch Directory: {{SCRATCH_DIR}}/[task_id]/
```

## Best Practices

### Do

- Checkpoint after each significant milestone
- Save analysis to scratch files for complex tasks
- Be concise in explanations (save context for work)
- Use references instead of repeating content
- Signal early if context is becoming constrained

### Don't

- Wait until context is exhausted to checkpoint
- Repeat large code blocks in explanations
- Re-read files unnecessarily (cache key information)
- Provide lengthy explanations when short ones suffice
- Ignore signs of context pressure

## Agent-Specific Guidance

### Developer

- Checkpoint after each file implementation
- Save implementation plan to scratch before coding
- Use incremental verification (test after each file)

### Auditor

- Checkpoint after reviewing each criterion
- Save verification results to scratch as you go
- Don't re-run tests unnecessarily

### Business Analyst

- Save domain research to scratch immediately
- Checkpoint after analyzing each ambiguity
- Preserve research even if specification not complete

### Remediation

- Checkpoint after each fix attempt
- Document what was tried in scratch
- Save diagnostic output for debugging

### Health Auditor

- This agent is fast (haiku model) - context exhaustion rare
- Still checkpoint if running many verification commands

## Cross-References

- Checkpoint format: [checkpoint-enforcement.md](checkpoint-enforcement.md)
- Signal formats: [signal-specification.md](signal-specification.md)
- State management: [state-management.md](state-management.md)
