# Escalation Specification

Clear rules for when and how agents escalate issues, including divine clarification procedures.

**Related Documents:**

- [signal-specification.md](signal-specification.md) - Signal formats
- [expert-delegation.md](expert-delegation.md) - Expert consultation
- [agent-definitions.md](agent-definitions.md) - Agent types and capabilities

---

## Escalation Hierarchy

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        ESCALATION LADDER                                 │
├─────────────────────────────────────────────────────────────────────────┤
│  Self-Solve (1-3 attempts)                                               │
│        ↓ If unsuccessful                                                │
│  Expert Delegation (4-6 attempts) [if experts available]                │
│        ↓ If unsuccessful                                                │
│  Divine Intervention (MANDATORY after 6 total attempts)                 │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Attempt Counting Rules

| Rule                      | Definition                                                |
|---------------------------|-----------------------------------------------------------|
| What counts as an attempt | A DISTINCT approach (different tool, method, or strategy) |
| What doesn't count        | Retrying the same approach, fixing typos                  |
| Maximum self-solve        | 3 attempts (or 6 if no experts available)                 |
| Maximum delegation        | 3 attempts (try different experts)                        |
| Maximum total             | 6 attempts before divine intervention                     |

---

## Escalation by Agent Type

### Baseline Agents (WITH Experts Available)

| Phase             | Attempts | Action                            |
|-------------------|----------|-----------------------------------|
| Self-Solve        | 1-3      | Try different approaches yourself |
| Expert Delegation | 4-6      | Request help from experts         |
| Divine            | 7+       | MANDATORY escalation to human     |

**After 3 delegation attempts all return EXPERT_UNSUCCESSFUL:**

```
MANDATORY: Signal SEEKING_DIVINE_CLARIFICATION
DO NOT: Continue trying different approaches
DO NOT: Retry the same experts
```

### Baseline Agents (WITHOUT Experts)

| Phase      | Attempts | Action                            |
|------------|----------|-----------------------------------|
| Self-Solve | 1-6      | Try different approaches yourself |
| Divine     | 7+       | MANDATORY escalation to human     |

### Expert Agents

| Phase      | Attempts | Action                     |
|------------|----------|----------------------------|
| Self-Solve | 1-3      | Try different approaches   |
| Fail       | 4+       | Signal EXPERT_UNSUCCESSFUL |

**Expert agents CANNOT:**

- Delegate to other agents
- Escalate to divine intervention
- Request additional resources

---

## Mandatory Escalation Triggers

These situations REQUIRE immediate escalation (no more attempts):

| Trigger                       | Signal                       | Reason                  |
|-------------------------------|------------------------------|-------------------------|
| 6 total failed attempts       | SEEKING_DIVINE_CLARIFICATION | Exhausted all options   |
| 3 EXPERT_UNSUCCESSFUL         | SEEKING_DIVINE_CLARIFICATION | All experts failed      |
| Circular dependency detected  | SEEKING_DIVINE_CLARIFICATION | Cannot resolve          |
| Security concern              | SEEKING_DIVINE_CLARIFICATION | Requires human judgment |
| Ambiguous acceptance criteria | SEEKING_DIVINE_CLARIFICATION | Cannot verify           |

---

## Attempt Documentation Format

Each attempt must be documented:

```markdown
ATTEMPT [N]: [Self-Solve | Expert Delegation]
Approach: [what was tried]
Outcome: [result]
Why Different: [how this differs from previous attempts]
```

---

## Escalation Signal Format

When escalating to divine intervention:

```
SEEKING_DIVINE_CLARIFICATION

Task: [task_id]
Agent: [agent_type]

Question: [specific question for human]

Context:
[relevant background]

Options Considered:
1. [option]: [why insufficient]
2. [option]: [why insufficient]

Attempts Made:
- Self-solve: [N] attempts
- Expert delegation: [N] attempts (if applicable)

What Would Help:
[specific guidance needed]
```

---

## Divine Clarification Procedure

When an agent signals for divine clarification, the coordinator acts as intermediary between the agent and the human.

### Coordinator Procedure

1. **Detect Signal**: Parse "SEEKING_DIVINE_CLARIFICATION" from agent output
2. **Log Event**: `agent_seeks_guidance` with agent_id, task_id, question
3. **Update State**: Add to `pending_divine_questions`
4. **Request Human Input**: Use AskUserQuestion tool

```
AskUserQuestion:
Context: Agent [agent_id] working on [task_id] requires guidance
Question: [agent's question]
Options: [agent's options]
```

5. **Receive Response**: Get human answer
6. **Log Event**: `divine_response_received`
7. **Deliver Response**: Resume agent with guidance

```
DIVINE RESPONSE

Task: [task ID]
Agent: [agent ID]

Question: [original question]
Guidance: [human response]

Resume work incorporating this guidance.
```

8. **Clean Up**: Remove from `pending_divine_questions`
9. **Log Event**: `agent_resumes_with_guidance`
10. **Resume Operations**: Call `fill_actor_slots()` to resume normal task dispatch

**CRITICAL**: Step 10 is essential. Without it, the coordinator remains paused after divine response, only processing
the single resumed task. New available work will not be dispatched.

```python
# After delivering divine response:
pending_divine_questions.remove(question_for_task)
log_event("agent_resumes_with_guidance", ...)

# MUST resume normal operations
if not pending_divine_questions:  # No more pending questions
    fill_actor_slots()  # Resume dispatching available tasks
```

### Output Formats

**On divine clarification request:**

```
DIVINE CLARIFICATION REQUESTED

Agent: [agent ID]
Task: [task ID]
Question: [summary]

Awaiting human guidance...
```

**On divine response delivery:**

```
DIVINE GUIDANCE DELIVERED

Agent: [agent ID]
Task: [task ID]
Guidance: [response summary]

Agent resuming work with guidance.
```

---

## Handling Pending Questions

Questions awaiting divine response persist in `pending_divine_questions`. On coordinator resume:

1. Check `pending_divine_questions` for unanswered questions
2. For each pending question, request human input again
3. Deliver responses before resuming associated agents

### Multiple Pending Questions

When multiple agents have pending questions, process in order received. Each question is independent.

---

## Escalation Tracking in State

```json
{
  "escalation_tracking": {
    "[task_id]": {
      "self_solve_attempts": 2,
      "expert_attempts": 1,
      "total_attempts": 3,
      "experts_tried": ["crypto-expert", "protocol-expert"],
      "last_attempt_type": "expert_delegation",
      "last_attempt_outcome": "EXPERT_UNSUCCESSFUL"
    }
  },
  "pending_divine_questions": [
    {
      "task_id": "task-1-1",
      "agent_id": "dev-123",
      "question": "...",
      "options": ["..."],
      "requested_at": "2025-01-16T10:30:00Z"
    }
  ]
}
```

---

## Post-Divine Clarification Flow

After divine clarification is received:

1. Log event: `divine_clarification_received`
2. Resume agent with clarification in prompt
3. **Reset attempt counters** for that specific issue (see below)
4. Update task status from `awaiting-divine-guidance` to `implementing`
5. Do NOT reset counters for unrelated issues

### Reset Escalation Counters

```python
def reset_escalation_counters(task_id):
    """Reset attempt counters after divine clarification is received."""

    if task_id in escalation_tracking:
        # Reset all counters for fresh start with divine guidance
        escalation_tracking[task_id] = {
            'self_solve_attempts': 0,
            'delegation_attempts': 0,
            'total_attempts': 0,
            'experts_tried': [],  # Keep expert history for reference
            'last_attempt_type': None,
            'last_attempt_outcome': 'divine_guidance_received',
            'divine_clarifications_received': escalation_tracking[task_id].get('divine_clarifications_received', 0) + 1
        }

        log_event("escalation_counters_reset",
                  task_id=task_id,
                  reason="divine_clarification_received")

    # Also reset incomplete count if this was a TASK_INCOMPLETE escalation
    if task_id in task_attempts:
        task_attempts[task_id]['incomplete_count'] = 0

    save_state()
```

**IMPORTANT**: Without this reset, the agent will immediately re-escalate on any subsequent failure since counters are
still at threshold.

---

## Task Status During Divine Intervention

When an agent escalates to divine intervention, the task status must be updated to prevent re-dispatch:

```python
def escalate_to_divine(task_id, question, options, context=None):
    """Escalate to human with proper state tracking."""

    # Update task status to prevent re-dispatch
    update_task_status(task_id, "awaiting-divine-guidance")

    # Add to pending questions
    pending_divine_questions.append({
        'task_id': task_id,
        'question': question,
        'options': options,
        'context': context,
        'escalated_at': datetime.now().isoformat()
    })

    log_event("agent_seeks_guidance",
              task_id=task_id,
              question=question)

    save_state()

    # Invoke human question
    AskUserQuestion(question=question, options=options)
```

---

## Cross-References

- [signal-specification.md](signal-specification.md) - Signal formats
- [expert-delegation.md](expert-delegation.md) - Expert consultation process
- [agent-definitions.md](agent-definitions.md) - Agent types
- [state-management.md](state-management.md) - State tracking
