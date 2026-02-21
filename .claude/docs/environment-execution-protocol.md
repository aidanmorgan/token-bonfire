# Environment Execution Protocol

Shared protocol for executing verification commands across multiple environments. Used by developer, critic, and auditor agents.

---

## Execution Environments

| Name | Description | How to Execute |
|------|-------------|----------------|
[FROM ENVIRONMENTS INPUT]

## CRITICAL - Environment Execution Protocol

**When a verification command has an EMPTY Environment column:**
1. You MUST execute the command in EVERY environment listed above
2. Execute in Mac environment first -> record ACTUAL exit code
3. Execute in Devcontainer environment -> record ACTUAL exit code
4. BOTH must return the required exit code
5. FAILURE IN ANY ENVIRONMENT = `<OUTCOME>`

**When a command specifies a SPECIFIC environment (e.g., "Mac"):**
1. Execute ONLY in that specific environment
2. Other environments are excluded by design

**How to Execute in Each Environment:**
- Mac: Run command directly in your shell
- Devcontainer: Use `mcp__devcontainers__devcontainer_exec(workspace_folder="/project", command="...")`

**YOU MUST BUILD THE ENVIRONMENT VERIFICATION MATRIX:**
For each command, add a row for each required environment showing the ACTUAL exit code.
This matrix is MANDATORY in your completion message.

**FAILURE TO RUN IN ALL REQUIRED ENVIRONMENTS IS A `<OUTCOME>`.**

---

## Environment Verification Matrix

Build this matrix as you execute each command:

| Check | Environment | Exit Code | Result |
|-------|-------------|-----------|--------|
| [check] | Mac | [actual] | PASS/FAIL |
| [check] | Devcontainer | [actual] | PASS/FAIL |

---

## Agent-Specific Outcomes

Each agent type uses this protocol with a different failure signal:

| Agent | Outcome Signal |
|-------|---------------|
| Developer | `TASK_FAILURE` |
| Critic | `REVIEW_FAILED` |
| Auditor | `AUDIT_FAILED` |

---

## Cross-References

- [Developer Workflow](agent-creation/developer/workflow.md) - Developer-specific workflow phases
- [Critic Review Criteria](agent-creation/critic/review-criteria.md) - Critic review method
- [Auditor Verification](agent-creation/auditor/verification.md) - Auditor verification method
