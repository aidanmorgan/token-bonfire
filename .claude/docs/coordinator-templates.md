# Coordinator Templates

Reusable template definitions for agent references and environment execution instructions.
These are expanded by the coordinator when dispatching agents.

---

## Developer References {#developer-references}

```
MUST READ (expand globs, read fully without summarization before starting):
{{#each AGENT_DOCS where (agent == "" or agent == "developer") and must_read == "Y"}}
- {{this.pattern}}: {{this.purpose}}
{{/each}}

REFERENCE (available for lookup during implementation):
{{#each AGENT_DOCS where (agent == "" or agent == "developer") and must_read != "Y"}}
- {{this.pattern}}: {{this.purpose}}
{{/each}}
```

---

## Auditor References {#auditor-references}

```
MUST READ (expand globs, read fully without summarization before auditing):
{{#each AGENT_DOCS where (agent == "" or agent == "auditor") and must_read == "Y"}}
- {{this.pattern}}: {{this.purpose}}
{{/each}}

REFERENCE (available for lookup during audit):
{{#each AGENT_DOCS where (agent == "" or agent == "auditor") and must_read != "Y"}}
- {{this.pattern}}: {{this.purpose}}
{{/each}}
```

---

## Business Analyst References {#ba-references}

```
MUST READ (expand globs, read fully without summarization before expanding):
{{#each AGENT_DOCS where (agent == "" or agent == "business-analyst") and must_read == "Y"}}
- {{this.pattern}}: {{this.purpose}}
{{/each}}

REFERENCE (available for lookup during expansion):
{{#each AGENT_DOCS where (agent == "" or agent == "business-analyst") and must_read != "Y"}}
- {{this.pattern}}: {{this.purpose}}
{{/each}}
```

---

## Remediation References {#remediation-references}

```
MUST READ (expand globs, read fully without summarization before fixing):
{{#each AGENT_DOCS where (agent == "" or agent == "remediation") and must_read == "Y"}}
- {{this.pattern}}: {{this.purpose}}
{{/each}}

REFERENCE (available for lookup during remediation):
{{#each AGENT_DOCS where (agent == "" or agent == "remediation") and must_read != "Y"}}
- {{this.pattern}}: {{this.purpose}}
{{/each}}
```

---

## Health Auditor References {#health-auditor-references}

```
MUST READ (expand globs, read fully before health check):
{{#each AGENT_DOCS where (agent == "" or agent == "health-auditor") and must_read == "Y"}}
- {{this.pattern}}: {{this.purpose}}
{{/each}}

REFERENCE (available for lookup during health check):
{{#each AGENT_DOCS where (agent == "" or agent == "health-auditor") and must_read != "Y"}}
- {{this.pattern}}: {{this.purpose}}
{{/each}}
```

---

## Environment Execution Instructions {#environment-execution-instructions}

```
## EXECUTION ENVIRONMENTS

| Name | Description | How to Execute |
|------|-------------|----------------|
{{#each ENVIRONMENTS}}
| {{this.name}} | {{this.description}} | {{this.how_to_execute}} |
{{/each}}

## CRITICAL - ENVIRONMENT EXECUTION PROTOCOL

### Step 1: Check the Environment Column

For EACH verification command, check its Environment column:
- **EMPTY or "ALL"** → You MUST run in EVERY environment listed above
- **SPECIFIC value** (e.g., "Mac") → Run ONLY in that environment

### Step 2: Execute in Each Required Environment

For commands with EMPTY Environment column:

1. **Execute in Mac environment:**
   - Run: `[command]`
   - Record the ACTUAL exit code returned

2. **Execute in Devcontainer environment:**
   - Run: `mcp__devcontainers__devcontainer_exec(workspace_folder="/project", command="[command]")`
   - Record the ACTUAL exit code returned

3. **Compare exit codes:**
   - Each must match the Required Exit Code (default: 0)
   - FAILURE IN EITHER ENVIRONMENT = TASK FAILURE

### Step 3: Build the Environment Verification Matrix

As you execute, build this table:

| Check | Environment | Exit Code | Result |
|-------|-------------|-----------|--------|
| [check1] | Mac | [actual] | PASS/FAIL |
| [check1] | Devcontainer | [actual] | PASS/FAIL |
| [check2] | Mac | [actual] | PASS/FAIL |
| [check2] | Devcontainer | [actual] | PASS/FAIL |

### Step 4: Include Matrix in Signal

Your signal MUST include:
- The complete Environment Verification Matrix
- "Environments Tested: Mac, Devcontainer" line
- "All Required Environments: VERIFIED" confirmation

## FAILURE MODES

| Situation | Result |
|-----------|--------|
| Command fails in Mac but passes in Devcontainer | TASK FAILURE |
| Command fails in Devcontainer but passes in Mac | TASK FAILURE |
| Missing environment in matrix | SIGNAL REJECTED |
| Skipped an environment | SIGNAL REJECTED |

**THERE ARE NO EXCEPTIONS. BOTH ENVIRONMENTS MUST PASS.**
```

---

## Template Variable Expansion

The coordinator expands these templates when building agent prompts.

### Expansion Rules

| Syntax                 | Meaning                     | Example                               |
|------------------------|-----------------------------|---------------------------------------|
| `{{variable}}`         | Simple substitution         | `{{PLAN_FILE}}` → `plans/my-plan.md`  |
| `{{#each collection}}` | Iterate over array          | Loop over VERIFICATION_COMMANDS       |
| `{{#if condition}}`    | Conditional inclusion       | Include section only if experts exist |
| `{{this.field}}`       | Access current item in loop | `{{this.pattern}}` in AGENT_DOCS loop |

### Common Variables

| Variable                | Source        | Description                     |
|-------------------------|---------------|---------------------------------|
| `AGENT_DOCS`            | Configuration | Agent reference documents table |
| `ENVIRONMENTS`          | Configuration | Execution environments          |
| `VERIFICATION_COMMANDS` | Configuration | Commands for validation         |
| `DEVELOPER_COMMANDS`    | Configuration | Commands developers run         |
| `available_experts`     | State         | Experts created for this plan   |

---

## Related Documentation

- [Coordinator Configuration](coordinator-configuration.md) - Variable definitions
- [Task Dispatch](task-dispatch.md) - How prompts are constructed
- [Agent Coordination](agent-coordination.md) - Expert matching
