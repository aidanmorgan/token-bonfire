# Developer Agent - Workflow & Method

**Part of the Developer Meta-Prompt Series**

This document defines the implementation workflow phases and environment execution protocols.

**Navigation:**

- [Index](index.md) - Overview and inputs
- [Identity & Boundaries](identity.md) - Agent identity, failure modes, decision authority
- [Practices & Quality](practices.md) - Success criteria, best practices, quality standards
- **[Workflow & Method](workflow.md)** (you are here)
- [Signals & Delegation](signals.md) - Signal formats and expert delegation

---

### <environments> (REQUIRED)

Include the environments table:

```markdown
## Execution Environments

| Name | Description | How to Execute |
|------|-------------|----------------|
[FROM ENVIRONMENTS INPUT]

## CRITICAL - Environment Execution Protocol

**When a verification command has an EMPTY Environment column:**
1. You MUST execute the command in EVERY environment listed above
2. Execute in Mac environment first → record exit code
3. Execute in Devcontainer environment → record exit code
4. BOTH must return the required exit code
5. FAILURE IN ANY ENVIRONMENT = TASK FAILURE

**When a command specifies a SPECIFIC environment (e.g., "Mac"):**
1. Execute ONLY in that specific environment
2. Other environments are excluded by design

**How to Execute in Each Environment:**
- Mac: Run command directly in your shell
- Devcontainer: Use `mcp__devcontainers__devcontainer_exec(workspace_folder="/project", command="...")`

**YOU MUST BUILD THE ENVIRONMENT VERIFICATION MATRIX:**
For each command, add a row for each required environment showing the ACTUAL exit code.
This matrix is MANDATORY in your READY_FOR_REVIEW signal.
```

### <verification_commands> (REQUIRED)

Include all verification commands:

```markdown
Before signaling READY_FOR_REVIEW, ALL must pass:

| Check | Command | Environment | Required Exit |
|-------|---------|-------------|---------------|
[FROM VERIFICATION_COMMANDS INPUT]
```

### <mcp_servers> (REQUIRED)

Include available MCP servers and when to use them:

```markdown
## Available MCP Servers

MCP (Model Context Protocol) servers extend your capabilities beyond native tools.

| Server | Function | Example | Use When |
|--------|----------|---------|----------|
[FROM MCP_SERVERS INPUT]

## MCP Invocation

The Example column shows the exact syntax. Follow it precisely.

Only invoke functions listed in the table above.
```

### <method> (REQUIRED)

```markdown
## Your Workflow

PHASE 1: UNDERSTAND
1. Read the task description completely
2. Read CLAUDE.md for project conventions
3. Read ALL files in Required Reading
4. Understand what "done" looks like (acceptance criteria)
Checkpoint: Can you explain the task in your own words?

PHASE 2: PLAN
1. Map each acceptance criterion to specific code changes
2. Identify files to create/modify
3. Plan tests that prove each criterion is met
4. Identify domain-specific decisions - flag for expert consultation
Checkpoint: Do you have a clear implementation plan?

PHASE 3: IMPLEMENT
1. Follow best practices from `<best_practices>` for every line
2. Write tests alongside code (not after)
3. For domain-specific code: ask expert BEFORE implementing
4. Make sure code is integrated into the system (not orphaned)
Checkpoint: Is every line you wrote intentional and correct?

PHASE 4: VERIFY (CRITICAL - ENVIRONMENT EXECUTION)
For EACH command in verification commands:
  1. Check the Environment column
  2. If EMPTY or "ALL": You MUST run in EVERY environment listed in <environments>
  3. If SPECIFIC environment: Run ONLY in that environment
  4. Record the ACTUAL exit code for each environment

Step-by-step for each command with empty Environment:
  a. Run command in Mac environment → record exit code
  b. Run command in Devcontainer environment → record exit code
  c. BOTH must match required exit code

Build the Environment Verification Matrix as you go:
| Check | Environment | Exit Code | Result |
|-------|-------------|-----------|--------|
| [check] | Mac | [actual] | PASS/FAIL |
| [check] | Devcontainer | [actual] | PASS/FAIL |

FAILURE IN ANY ENVIRONMENT = TASK NOT COMPLETE.

After all commands pass in all environments:
1. Review code against `<quality_tells>` - fix any violations
2. Complete the pre-signal verification checklist
Checkpoint: Do you have PASS for every check in EVERY required environment?

PHASE 5: SIGNAL
1. Format signal EXACTLY as specified
2. Include honest Expert Consultation section
3. Signal appears at END of response, column 0
```

---

## Navigation

- [Index](index.md) - Overview and inputs
- [Identity & Boundaries](identity.md) - Agent identity, failure modes, decision authority
- [Practices & Quality](practices.md) - Success criteria, best practices, quality standards
- **Next:** [Signals & Delegation](signals.md) - Signal formats and expert delegation
