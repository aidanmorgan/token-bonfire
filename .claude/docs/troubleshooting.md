# Troubleshooting

Common issues and recovery procedures for the Bonfire team system.

## Developer Issues

### Developer stuck on a task
**Symptoms**: Developer not signaling ready-for-review, no mailbox messages.
**Resolution**: Team lead uses `TeammateTool({ operation: "write", to: "<developer-name>" })` to check status. If no response after ~5 minutes, the heartbeat timeout will release the task. Respawn the developer.

### Developer fails self-verification repeatedly
**Symptoms**: Developer signals INFRA_BLOCKED or repeatedly fails verification commands.
**Resolution**:
1. Check if dependencies are installed (`uv sync` or equivalent)
2. Check if test fixtures or test databases are available
3. Check if required files from other tasks exist yet (dependency issue)
4. If infrastructure is broken, team lead fixes or escalates to user

### Developer edits conflict with another developer
**Symptoms**: Two developers modify the same file, causing merge issues.
**Resolution**: Task descriptions should specify file ownership boundaries. If conflict occurs, team lead uses `write` to message both developers to coordinate. One developer yields and waits.

### Developer crashes
**Symptoms**: Developer stops responding, heartbeat timeout fires (~5 min).
**Resolution**: Task auto-releases and becomes claimable again. Team lead respawns the developer via `Task({ team_name, name: "<developer-name>", subagent_type: "developer", prompt: "<config tables>", run_in_background: true })`. No prompt recomposition needed — role instructions come from `.claude/agents/developer.md`.

### Developer needs domain expertise
**Symptoms**: Developer is uncertain about domain-specific decisions or implementation approaches.
**Resolution**: Developer sends `NEED_EXPERT_ADVICE` to the team lead, who routes the question to the appropriate expert advisor. The expert advisor provides guidance via `EXPERT_ADVICE_PROVIDED`, which the team lead relays back to the developer.

## Critic Issues

### Critic rejects same task 3+ times
**Symptoms**: REVIEW_FAILED cycles without progress.
**Resolution**:
1. Team lead reads both the critic's feedback and developer's changes
2. Identifies if the issue is with the implementation, the code quality criteria, or the review
3. Uses `write` to provide specific guidance to the developer
4. If criteria are unclear, escalates to user via `AskUserQuestion`

### Critic becomes a bottleneck
**Symptoms**: Multiple tasks waiting in pending-review state.
**Resolution**: Critic processes FIFO. If backlog grows, team lead can prioritize critical-path tasks by ordering review requests.

## Ripple Issues

### Ripple keeps failing the same task
**Symptoms**: RIPPLE_FAILED cycles without progress on the same task.
**Resolution**:
1. Check if the changes have broader scope than expected — the developer may be modifying shared APIs or contracts that affect many consumers
2. Team lead reads ripple feedback and determines whether the downstream impacts are real or speculative
3. If real: the task may need to be split into a broader refactoring effort. Escalate to user via `AskUserQuestion`
4. If speculative: team lead uses `write` to guide ripple to focus on concrete, evidenced impacts only

### Ripple flags too many latent issues
**Symptoms**: Ripple reports a long list of "latent" downstream issues alongside concrete impacts.
**Resolution**: Latent issues are informational only and do NOT block task progression. Ripple should only flag concrete impacts (broken consumers, altered API contracts, test coverage gaps, behavioral drift in callers). If ripple is treating latent issues as blockers, team lead uses `write` to remind ripple that only concrete downstream impacts warrant `RIPPLE_FAILED`.

## Auditor Issues

### Auditor rejects same task 3+ times
**Symptoms**: AUDIT_FAILED cycles without progress.
**Resolution**:
1. Team lead reads both the auditor's feedback and developer's changes
2. Identifies if the issue is with the implementation, the acceptance criteria, or the audit
3. Uses `write` to provide specific guidance to the developer
4. If criteria are unclear, escalates to user via `AskUserQuestion`

### Auditor becomes a bottleneck
**Symptoms**: Multiple tasks waiting in pending-audit state.
**Resolution**: Auditor processes FIFO. If backlog grows, team lead can prioritize critical-path tasks by ordering audit requests.

### Verification command fails for infrastructure reasons
**Symptoms**: Commands fail with environment errors, not code errors.
**Resolution**: Team lead investigates and fixes (e.g., missing dependencies, broken test fixtures). If unfixable, escalates to user.

## Plan Issues

### Circular dependencies detected
**Symptoms**: Bootstrap script exits with cycle detection error on stderr.
**Resolution**: Fix the `Blocked By` fields in the plan file to remove circular references. Each task's dependencies must form a DAG.

### No tasks without blockers
**Symptoms**: Bootstrap script reports no root tasks.
**Resolution**: At least one task must have `Blocked By: none`. Review the plan's dependency chain and identify the true starting points.

### All tasks blocked but plan not complete
**Symptoms**: No pending unblocked tasks, but completed count < total.
**Resolution**: Team lead reports the blocking chain to the user. Usually means a dependency was not properly marked as completed, or a missing task creates a gap. Dependencies auto-unblock when the blocking task is `completed`.

## Expert Advisor Generation Issues

### Too few expert advisors generated
**Symptoms**: Developers frequently lack domain guidance, sending many `NEED_EXPERT_ADVICE` requests with no matching expert advisor.
**Resolution**: The team lead should split the expert advisor's domain into sub-domains during gap analysis. Regenerate expert advisors by deleting `.claude/experts/<plan_slug>/` and re-running `/bonfire`.

### Expert advisor domain mismatch
**Symptoms**: Expert advisor unable to answer questions in their supposed domain.
**Resolution**: Regenerate the expert advisor roster with more targeted research.

### Expert advisor definitions corrupted or outdated
**Symptoms**: Expert advisor prompts reference wrong technologies or stale patterns.
**Resolution**: Delete `.claude/experts/<plan_slug>/` and re-run `/bonfire` to trigger fresh expert advisor generation with new research.

## Infrastructure Issues

### Dependencies won't install
**Resolution**: Check `pyproject.toml` or equivalent for version conflicts. Run the sync command with verbose output. If a package is unavailable, escalate to user.

### Tests fail on infrastructure, not code
**Symptoms**: Tests pass locally but fail in CI, or tests fail with connection/timeout errors.
**Resolution**: Check for network-dependent tests, missing environment variables, or test database setup. These are infrastructure issues, not code issues.

### MCP server unavailable
**Symptoms**: Devcontainer commands fail.
**Resolution**: Check if the devcontainer is running (`devcontainer_list`). Start it if needed (`devcontainer_start`). If the MCP server itself is down, fall back to local execution or escalate.

## Recovery After Crash

The shared task list is keyed by `plan_slug` and persists on disk. Expert advisor definitions are persisted to `.claude/experts/<plan_slug>/`. Static role instructions live in `.claude/agents/*.md`. This means recovery is automatic:

1. Run `/bonfire $PLAN_FILE` again — the bootstrapper produces the same `plan_slug`
2. Team lead finds expert advisor files at `.claude/experts/<plan_slug>/` → loads them (no regeneration)
3. Team lead calls `TaskList` and finds existing tasks → enters **resume mode**
4. Spawns static roles by agent name (`subagent_type: "<agent-name>"`) — no prompt recomposition needed
5. Spawns expert advisors from disk prompts (`subagent_type: "general-purpose"`) with persisted domain knowledge
6. Developers claim pending/unblocked tasks from the shared task list
7. Completed tasks stay completed — no work is lost
8. In-progress tasks from crashed developers auto-release after heartbeat timeout (~5 min)

**No manual intervention needed.** The slug-based naming ensures the same plan always maps to the same shared task list and expert advisor definitions. Native agent definitions in `.claude/agents/` simplify respawning — the team lead only needs to pass config tables, not recompose full prompts.

## Agent Teams Limitations

- **Teammate context not preserved on resume** — `/resume` does not restore teammate context windows, but static roles respawn from `.claude/agents/*.md` definitions and expert advisor prompts (with all domain research) are persisted to disk and reloaded on respawn
- **One team per session** — `cleanup` current team before starting a new one
- **No nested teams** — teammates cannot spawn their own sub-teams
- **Fixed lead** — cannot transfer leadership to a teammate
- **Permissions set at spawn** — teammates start with lead's permission mode

## Escalation Path

See [escalation-specification.md](escalation-specification.md) for the complete escalation procedure.

**Quick reference**: Self-solve (1-3 attempts) → Expert advisor consultation (4-6 attempts) → User clarification (mandatory after 6 total attempts or when mandatory triggers apply).
