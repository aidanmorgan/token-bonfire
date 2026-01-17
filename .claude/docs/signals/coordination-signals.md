# Coordination Signals

Signals for system coordination, expert delegation, concurrency management, and checkpoints.

---

## Escalation Signals

### SEEKING_DIVINE_CLARIFICATION

```
^SEEKING_DIVINE_CLARIFICATION$
```

**Usage**: Agent needs human guidance after exhausting self-solve and delegation.

**Allowed By**: Baseline agents only (developer, auditor, BA, remediation, health auditor)

**Format**:

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
- Delegation: [N] attempts (if applicable)

What Would Help:
[specific guidance needed]
```

### EXPERT_REQUEST

```
^EXPERT_REQUEST$
```

**Usage**: Baseline agent requests expert assistance.

**Allowed By**: Baseline agents only

**Format**:

```
EXPERT_REQUEST
Target Agent: [agent name]
Request Type: [decision | interpretation | ambiguity | options | validation]
Context Snapshot: [path to snapshot file]

---DELEGATION PROMPT START---
[Agent-generated prompt for expert]
---DELEGATION PROMPT END---
```

---

## Expert Signals

Experts are specialist agents created per-plan to support default agents.

### EXPERT_ADVICE

```
^EXPERT_ADVICE: (.+)$
```

**Usage**: Expert has provided advice in response to a default agent's request.

**Format**:

```
EXPERT_ADVICE: [request_id]

Requesting Agent: [who asked]
Task: [which task]
Question: [what was asked]

Recommendation:
[Clear guidance]

Rationale:
- [Why this is correct for this plan]

Pitfalls Avoided:
- [What this recommendation avoids]

Next Steps:
[What the default agent should do]
```

### EXPERT_UNSUCCESSFUL

```
^EXPERT_UNSUCCESSFUL: (.+)$
```

**Usage**: Expert cannot provide advice after 3 attempts. Default agent should escalate to divine intervention.

**Format**:

```
EXPERT_UNSUCCESSFUL: [request_id]

Requesting Agent: [who asked]
Question: [what was asked]

Attempts:
1. [approach]: [outcome]
2. [approach]: [outcome]
3. [approach]: [outcome]

Reason: [why unable to help]
Recommendation: [escalate to divine intervention]
```

### EXPERT_CREATED

```
^EXPERT_CREATED: (.+)$
```

**Usage**: Orchestrator has created a new expert during plan analysis.

**Format**:

```
EXPERT_CREATED: [expert_name]

Gap Filled: [description]
Supports: [which default agents]
Tasks: [task IDs]
File: .claude/agents/experts/[expert_name].md

Keyword Triggers: [comma-separated domain keywords for dynamic task matching]

Expertise Encoded:
- [specific to this plan]

Delegation Triggers:
- Developer should ask when: [trigger]
- Auditor should ask when: [trigger]
```

`Keyword Triggers` enables dynamic expert matching at dispatch time.

---

## Concurrency Signals

### FILE CONFLICT

```
^FILE CONFLICT: (.+)$
```

**Usage**: Agent needs to modify a file assigned to another agent.

**Format**:

```
FILE CONFLICT: [file_path]

Assigned To: [other_agent_id or UNKNOWN]
I Need To: [description of needed change]
Reason: [why this file must be modified]
Can Wait: [YES | NO]
```

**Coordinator Response**:

- If can wait: Queue request, notify when available
- If cannot wait: Coordinate merge or reassign

---

## Checkpoint Signals

### CHECKPOINT RESPONSE

```
^CHECKPOINT: (.+)$
```

**Usage**: Developer responds to coordinator checkpoint request.

**Format**:

```
CHECKPOINT: [task_id]

Progress: [percentage or phase]
Current Activity: [what agent is doing]
Files Modified: [count]
Blockers: [NONE | description]
Estimated Remaining: [description, not time]
```

---

## Related Documentation

- [Signal Index](index.md) - Overview and detection rules
- [Workflow Signals](workflow-signals.md) - Developer, Critic, Auditor signals
- [Supporting Signals](supporting-signals.md) - BA, Remediation, Health Auditor signals
- [Signal Parsing](parsing.md) - Implementation details
- [Expert Delegation](../expert-delegation.md) - Expert system details
