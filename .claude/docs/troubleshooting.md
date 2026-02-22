# Troubleshooting

Common issues and recovery procedures for the Bonfire team system.

## Developer Issues

### Developer stuck on a task
**Symptoms**: Developer not signaling ready-for-review, no messages received.
**Resolution**: Team lead sends a status check via `SendMessage({ type: "message", recipient: "<dev-name>", ... })`. If no response after ~5 minutes, the heartbeat timeout will release the task. Respawn the developer with `Task({ team_name: "<plan_slug>", name: "<dev-name>", subagent_type: "developer", ... })`.

### Developer fails self-verification repeatedly
**Symptoms**: Developer signals INFRA_BLOCKED or repeatedly fails verification commands.
**Resolution**:
1. Check if dependencies are installed (`uv sync` or equivalent)
2. Check if test fixtures or test databases are available
3. Check if required files from other tasks exist yet (dependency issue)
4. If infrastructure is broken, route to `remediation` via `SendMessage`

### Developer edits conflict with another developer
**Symptoms**: Two developers modify the same file, causing merge issues.
**Resolution**: Task descriptions should specify file ownership boundaries. If conflict occurs, team lead sends messages to both developers via `SendMessage` to coordinate. One developer yields and waits.

### Developer crashes
**Symptoms**: Developer stops responding, heartbeat timeout fires (~5 min).
**Resolution**: Task auto-releases and becomes available for reassignment. Team lead respawns the developer via `Task({ team_name: "<plan_slug>", name: "<dev-name>", subagent_type: "developer", prompt: "<config tables>", run_in_background: true })`. Role instructions come from `.claude/agents/developer.md` automatically.

### Developer needs domain expertise
**Symptoms**: Developer sends `NEED_EXPERT_ADVICE` to the team lead.
**Resolution**: Team lead forwards the question to the appropriate expert advisor via `SendMessage`. The expert provides guidance via `EXPERT_ADVICE_PROVIDED`, which the team lead relays back to the developer via `SendMessage`.

## Critic Issues

### Critic rejects same task 3+ times
**Symptoms**: REVIEW_FAILED cycles without progress.
**Resolution**:
1. Team lead reads both the critic's feedback and developer's changes
2. Identifies if the issue is with the implementation, the code quality criteria, or the review
3. Sends specific guidance to the developer via `SendMessage`
4. If criteria are unclear, escalates to user via `AskUserQuestion`

### Critic becomes a bottleneck
**Symptoms**: Multiple tasks waiting in pending-review state.
**Resolution**: Critic processes FIFO. If backlog grows, team lead can prioritize critical-path tasks by ordering review requests.

## Ripple Issues

### Ripple keeps failing the same task
**Symptoms**: RIPPLE_FAILED cycles without progress.
**Resolution**:
1. Check if the changes have broader scope than expected
2. Team lead reads ripple feedback and determines whether impacts are real or speculative
3. If real: the task may need to be split. Escalate to user via `AskUserQuestion`
4. If speculative: send guidance to ripple via `SendMessage` to focus on concrete impacts only

### Ripple flags too many latent issues
**Symptoms**: Ripple reports many "latent" issues alongside concrete impacts.
**Resolution**: Latent issues are informational only and do NOT block progression. If ripple is treating them as blockers, team lead sends guidance via `SendMessage` to remind ripple that only concrete impacts warrant `RIPPLE_FAILED`.

## Auditor Issues

### Auditor rejects same task 3+ times
**Symptoms**: AUDIT_FAILED cycles without progress.
**Resolution**:
1. Team lead reads both the auditor's feedback and developer's changes
2. Identifies the root cause
3. Sends specific guidance to the developer via `SendMessage`
4. If criteria are unclear, escalates to user via `AskUserQuestion`

### Verification command fails for infrastructure reasons
**Symptoms**: Commands fail with environment errors, not code errors.
**Resolution**: Auditor signals `AUDIT_BLOCKED`. Team lead routes to `remediation` via `SendMessage`.

## Plan Issues

### Circular dependencies detected
**Resolution**: Fix the `Blocked By` fields in the plan file to remove circular references. Each task's dependencies must form a DAG.

### All tasks blocked but plan not complete
**Resolution**: Team lead reports the blocking chain to the user. Usually means a dependency was not properly marked as completed, or a missing task creates a gap.

## Expert Advisor Issues

### Expert advisor domain mismatch
**Resolution**: Regenerate the expert advisor roster by deleting `.claude/experts/<plan_slug>/` and re-running `/bonfire`.

### Expert advisor crashes
**Resolution**: Respawn from disk prompt with `Task({ team_name: "<plan_slug>", name: "<expert-name>", subagent_type: "general-purpose", model: "<EXPERT_MODEL>", prompt: "<expert definition from disk>", run_in_background: true })`.

## Infrastructure Issues

### Dependencies won't install
**Resolution**: Check `pyproject.toml` for version conflicts. Run sync with verbose output. Escalate to user if unresolvable.

### MCP server unavailable
**Resolution**: Check if devcontainer is running (`devcontainer_list`). Start if needed (`devcontainer_start`). Fall back to local execution or escalate.

## Recovery After Crash

The shared task list is keyed by `plan_slug` and persists on disk. Expert advisor definitions persist at `.claude/experts/<plan_slug>/`. Recovery is automatic:

1. Run `/bonfire $PLAN_FILE` again — same `plan_slug` produced
2. Team lead finds expert files → loads them (no regeneration)
3. Team lead calls `TaskList` → finds existing tasks → enters **resume mode**
4. Respawns static roles with `team_name: "<plan_slug>"` and `subagent_type: "<agent-name>"`
5. Respawns expert advisors from disk prompts with `team_name: "<plan_slug>"`
6. Team lead assigns pending tasks to developers as they send `REQUESTING_WORK`
7. Completed tasks stay completed — no work is lost
8. In-progress tasks from crashed developers auto-release after heartbeat timeout (~5 min)

## Agent Teams Limitations

- **Teammate context not preserved on resume** — but static roles respawn from `.claude/agents/*.md` and expert prompts are persisted to disk
- **One team per session** — `TeamDelete` current team before starting a new one
- **No nested teams** — teammates cannot spawn sub-teams
- **Fixed lead** — cannot transfer leadership
- **Permissions set at spawn** — teammates inherit lead's permission mode
