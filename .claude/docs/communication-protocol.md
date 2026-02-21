# Communication Protocol

In the native Agent Teams system, there is no custom event log file. All inter-agent communication uses targeted mailbox messages via `TeammateTool({ operation: "write", to: "<name>" })`.

## Message Flow

All messages flow through the team lead. No direct developer-to-developer, developer-to-expert, developer-to-critic, or developer-to-auditor communication.

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

## Message Types

### Developer to Team Lead

| Message | When | Content |
|---|---|---|
| `READY_FOR_REVIEW: <task-id>` | Task implemented and self-verified | Summary, files modified, files read-only |
| `NEED_CLARIFICATION: <question>` | Ambiguous requirements or missing dependency | Question details, context, options |
| `NEED_EXPERT_ADVICE: <question>` | Needs domain guidance from an expert advisor | Question details, domain, context |
| `INFRA_BLOCKED: <details>` | Infrastructure prevents progress | Issue type, error details, commands tried |
| `FILE_CONFLICT: <file> <details>` | Needs to modify file outside ownership scope | File path, reason, proposed change |

### Expert Advisor to Team Lead

| Message | When | Content |
|---|---|---|
| `EXPERT_ADVICE_PROVIDED: <response>` | Domain guidance provided in response to developer question | Advice, recommendations, patterns to follow |

### Critic to Team Lead

| Message | When | Content |
|---|---|---|
| `REVIEW_PASSED: <task-id>` | Code quality checks passed | Quality review summary |
| `REVIEW_FAILED: <task-id> [feedback]` | Code quality issues found | Specific issues with file paths and line numbers |

### Ripple to Team Lead

| Message | When | Content |
|---|---|---|
| `RIPPLE_PASSED: <task-id>` | No breaking downstream impacts | Impact summary, files analyzed |
| `RIPPLE_FAILED: <task-id> [feedback]` | Second-order issues found | Issues with source, affected, remediation |

### Auditor to Team Lead

| Message | When | Content |
|---|---|---|
| `AUDIT_PASSED: <task-id>` | All acceptance criteria verified, verification commands pass | Verification summary, evidence |
| `AUDIT_FAILED: <task-id> [feedback]` | Acceptance criteria not met | Failed criteria, required fixes with file paths and line numbers |
| `AUDIT_BLOCKED: <task-id> [details]` | Pre-existing infrastructure failures prevent verification | Infrastructure issue details |

### Team Lead to Developer

| Message | When | Content |
|---|---|---|
| Review feedback | Critic, ripple, or auditor rejected task | Specific issues and required fixes |
| Clarification response | User or business-analyst provided answer | Answer to the developer's question |
| Expert advice | Expert advisor provided domain guidance | Forwarded advice from expert advisor |
| Infrastructure fix confirmation | Remediation completed | What was fixed, resume instructions |
| File ownership resolution | File conflict resolved | Who owns the file, what to do |

### Team Lead to Expert Advisor

| Message | When | Content |
|---|---|---|
| Developer question | Developer needs domain guidance | Question details, task context |

### Team Lead to Critic

| Message | When | Content |
|---|---|---|
| Review request | Developer signaled ready for review | Task ID, modified files, code context |

### Team Lead to Ripple

| Message | When | Content |
|---|---|---|
| Ripple request | Critic passed review | Task ID, modified files, summary, critic assessment |

### Team Lead to Auditor

| Message | When | Content |
|---|---|---|
| Audit request | Ripple passed impact analysis | Task ID, acceptance criteria, modified files, environment |

### Team Lead to Remediation

| Message | When | Content |
|---|---|---|
| Infrastructure issue | Developer or auditor reported infra problem | Issue type, error details, affected tasks |

### Team Lead to Health Auditor

| Message | When | Content |
|---|---|---|
| Verification request | Remediation completed | What was fixed, commands to verify |

### Team Lead to Business Analyst

| Message | When | Content |
|---|---|---|
| Expansion request | Task needs clarification | Task ID, missing criteria, context |

## Audit Trail

The team lead maintains visibility into the workflow by tracking:
- Which tasks are at which stage in the critic -> ripple -> auditor pipeline
- Failure counts per task (critic failures, auditor failures, timeouts)
- Infrastructure status

This information is maintained in the team lead's context. It does not need to be persisted to a separate file because:
- Task state persists in the shared task list (via plan slug)
- Expert advisor definitions persist on disk (at `.claude/experts/<plan_slug>/`)
- On resume, the team lead reconstructs state from `TaskList` and expert advisor files
