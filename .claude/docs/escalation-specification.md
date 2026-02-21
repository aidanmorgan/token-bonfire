# Escalation Specification

Clear rules for when and how teammates escalate issues, including user clarification procedures.

**Related Documents:**

- [expert-delegation.md](expert-delegation.md) - Developer-to-expert advisor consultation

---

## Escalation Hierarchy

**Escalation Ladder**:

1. Self-Solve (1-3 attempts)
2. If unsuccessful: Expert Advisor Consultation (4-6 attempts) [if expert advisors available]
3. If unsuccessful: User Clarification (MANDATORY after 6 total attempts)

---

## Attempt Counting Rules

| Rule                      | Definition                                                |
|---------------------------|-----------------------------------------------------------|
| What counts as an attempt | A DISTINCT approach (different tool, method, or strategy) |
| What doesn't count        | Retrying the same approach, fixing typos                  |
| Maximum self-solve        | 3 attempts (or 6 if no expert advisors available)         |
| Maximum consultation      | 3 attempts (try different expert advisors)                |
| Maximum total             | 6 attempts before user clarification                      |

---

## Escalation by Teammate Type

### Developers/Critic/Ripple/Auditor (WITH Expert Advisors Available)

| Phase                    | Attempts  | Action                                  |
|--------------------------|-----------|------------------------------------------|
| Self-Solve               | 1-3       | Try different approaches yourself       |
| Expert Advisor Consult   | 4-6       | Send NEED_EXPERT_ADVICE to team lead    |
| User Clarification       | After 6   | MANDATORY escalation to team lead       |

**Note**: "After 6" means if all 6 attempts fail, escalation to the team lead is MANDATORY.

**After 3 consultation attempts all unsuccessful:**

```
MANDATORY: Message team lead with SEEKING_DIVINE_CLARIFICATION
DO NOT: Continue trying different approaches
DO NOT: Retry the same expert advisors
```

### Developers/Critic/Ripple/Auditor (WITHOUT Expert Advisors)

| Phase      | Attempts | Action                             |
|------------|----------|-------------------------------------|
| Self-Solve | 1-6      | Try different approaches yourself  |
| User       | After 6  | MANDATORY escalation to team lead  |

### Expert Advisor Agents

| Phase      | Attempts | Action                     |
|------------|----------|----------------------------|
| Self-Solve | 1-3      | Try different approaches   |
| Fail       | 4+       | Reply unable to help       |

**Expert advisor agents CANNOT:**

- Delegate to other agents
- Escalate to the user
- Request additional resources
- Write or modify code (advisory only)

---

## Mandatory Escalation Triggers

These situations REQUIRE immediate escalation (no more attempts):

| Trigger                       | Action                               | Reason                  |
|-------------------------------|--------------------------------------|-------------------------|
| 6 total failed attempts       | Message team lead for clarification  | Exhausted all options   |
| 3 expert advisor consults fail| Message team lead for clarification  | All expert advisors failed |
| Ripple rejects same task 3+   | Message team lead for clarification  | Investigate if changes need broader scope |
| Circular dependency detected  | Message team lead for clarification  | Cannot resolve          |
| Security concern              | Message team lead for clarification  | Requires human judgment |
| Ambiguous acceptance criteria | Message team lead for clarification  | Cannot verify           |

---

## Attempt Documentation Format

Each attempt must be documented:

```markdown
ATTEMPT [N]: [Self-Solve | Expert Advisor Consultation]
Approach: [what was tried]
Outcome: [result]
Why Different: [how this differs from previous attempts]
```

---

## Escalation Message Format

When escalating to the team lead:

```
SEEKING_DIVINE_CLARIFICATION

Task: [task_id]
Teammate: [name]

Question: [specific question for user]

Context:
[relevant background]

Options Considered:
1. [option]: [why insufficient]
2. [option]: [why insufficient]

Attempts Made:
- Self-solve: [N] attempts
- Expert advisor consultation: [N] attempts (if applicable)

What Would Help:
[specific guidance needed]
```

---

## User Clarification Procedure

When a teammate messages the team lead seeking clarification, the team lead acts as intermediary.

### Team Lead Procedure

1. **Detect Message**: Read mailbox for "SEEKING_DIVINE_CLARIFICATION" from teammate
2. **Track Question**: Add to pending questions in team lead context
3. **Request User Input**: Ask the user directly

4. **Receive Response**: Get user answer
5. **Deliver Response**: Message teammate via `TeammateTool write` with guidance

```
TeammateTool({
  operation: "write",
  to: "<teammate-name>",
  content: "USER GUIDANCE\n\nTask: [task ID]\n\nQuestion: [original question]\nGuidance: [user response]\n\nResume work incorporating this guidance."
})
```

6. **Clean Up**: Remove from pending questions
7. **Resume Operations**: Continue monitoring the task loop

**CRITICAL**: After delivering guidance, the team lead must resume normal operations and continue monitoring
the task loop. Without this, the team lead remains paused.

### Output Formats

**On clarification request:**

```
CLARIFICATION REQUESTED

Teammate: [name]
Task: [task ID]
Question: [summary]

Asking user for guidance...
```

**On guidance delivery:**

```
GUIDANCE DELIVERED

Teammate: [name]
Task: [task ID]
Guidance: [response summary]

Teammate resuming work with guidance.
```

---

## Handling Pending Questions

Questions awaiting user response are tracked by the team lead. On resume:

1. Check pending questions for unanswered items
2. For each pending question, ask the user again
3. Deliver responses before resuming associated teammates

### Multiple Pending Questions

When multiple teammates have pending questions, process in order received. Each question is independent.

---

## Escalation Tracking

The team lead tracks escalation state in its context:

- Per-task self-solve attempt count
- Per-task expert advisor consultation attempt count
- Total attempts per task
- Which expert advisors have been tried
- Pending questions awaiting user response

---

## Post-Clarification Flow

After user clarification is received:

1. Deliver guidance to the teammate via mailbox message
2. **Reset attempt counters** for that specific issue
3. Update task status - the developer can resume work
4. Do NOT reset counters for unrelated issues

**IMPORTANT**: Without resetting counters, the teammate will immediately re-escalate on any subsequent failure since
counters are still at threshold.

---

## Task Status During Clarification

When a teammate escalates, the task should not be available for other developers to claim. The team lead ensures
the task remains in a blocked state until guidance is delivered.

---

## Cross-References

- [expert-delegation.md](expert-delegation.md) - Developer-to-expert advisor consultation process
- [team-architecture.md](team-architecture.md) - Team structure
