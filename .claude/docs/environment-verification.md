# Environment Verification Specification

This document specifies how teammates must execute and report verification commands across multiple environments, and how
the team lead enforces complete coverage.

## Execution Environments

The team lead provides a list of execution environments in `EXECUTION ENVIRONMENTS`. Each environment represents a
distinct runtime context where verification commands must pass.

Example environments:

- `native` - Host machine without containerization
- `devcontainer` - Development container
- `docker-compose` - Full service stack
- `ci` - CI/CD pipeline simulation

## Verification Command Interpretation

### Environment Column Values

| Environment Value | Interpretation        | Action Required                 |
|-------------------|-----------------------|---------------------------------|
| Empty or "ALL"    | Universal requirement | Run in EVERY listed environment |
| Specific name     | Targeted requirement  | Run ONLY in that environment    |

### Required Exit Code

Each verification command specifies a required exit code (defaults to 0). The command PASSES only if the actual
exit code exactly matches the required exit code.

## Execution Protocol

### Step 1: Enumerate Required Executions

Before running any verification, build the execution matrix: for each command, determine which environments it must
run in (ALL environments for universal commands, specific environment for targeted commands).

### Step 2: Execute Each Matrix Entry

For each entry in the execution matrix:

1. Switch to the target environment (if different from current)
2. Execute the command
3. Capture the actual exit code
4. Record pass/fail based on exit code match

### Step 3: Validate Complete Coverage

Before reporting completion, verify every required (check, environment) pair was executed.

## Message Format Requirements

### Developer READY_FOR_REVIEW

The environment verification matrix MUST be included in the message to the team lead:

```
READY_FOR_REVIEW: [task_id]

Files Modified:
- [file path]

Tests Written:
- [test file]: [what it tests]

Environment Verification Matrix:
| Check | Environment | Exit Code | Result |
|-------|-------------|-----------|--------|
| unit_tests | native | 0 | PASS |
| unit_tests | devcontainer | 0 | PASS |
| lint | native | 0 | PASS |
| lint | devcontainer | 0 | PASS |
| type_check | native | 0 | PASS |
| type_check | devcontainer | 0 | PASS |

Environments Tested: native, devcontainer
All Required Environments: VERIFIED

Summary: [description]
```

**Matrix Requirements**:

- MUST include a row for EACH check x environment combination required
- Commands with Environment="ALL" require rows for EVERY environment in EXECUTION ENVIRONMENTS
- Commands with specific Environment require only that environment's row
- Exit Code column MUST show the actual exit code returned
- Result is PASS only if actual exit code matches Required Exit Code
- "Environments Tested" line MUST list every environment you executed commands in
- "All Required Environments: VERIFIED" line confirms complete coverage

### Auditor AUDIT_PASSED

The auditor must independently verify and report:

```
AUDIT_PASSED: [task_id]

Quality Verification:
- Code quality tells: NONE FOUND
- Standards compliance: VERIFIED

Requirements Verification:
- Criterion 1: [evidence]
- Criterion 2: [evidence]

Environment Verification Matrix:
| Check | Environment | Exit Code | Result |
|-------|-------------|-----------|--------|
| unit_tests | native | 0 | PASS |
| unit_tests | devcontainer | 0 | PASS |
| lint | native | 0 | PASS |
| lint | devcontainer | 0 | PASS |

Environments Verified: native, devcontainer
All Required Environments: CONFIRMED

Conclusion: Task requirements fully implemented with production-quality code.
```

## Team Lead Validation

### On READY_FOR_REVIEW Message

The team lead validates the message BEFORE routing to the critic:

1. Check for matrix header
2. Extract all matrix rows
3. Build expected matrix from verification commands and environments
4. Check each expected entry exists and passed
5. Check "Environments Tested" line
6. Check "All Required Environments: VERIFIED" confirmation

### On Message Rejection

If validation fails, the team lead does NOT route to the critic:

1. Return the task to in-progress status via `TaskUpdate`
2. Message the developer with the rejection reason:

```
TeammateTool({
  operation: "write",
  to: "<developer-name>",
  content: "SIGNAL REJECTED: [task_id]\n\nReason: [validation error]\n\nRequired Action:\n1. Re-run the missing/failed verification in the required environment(s)\n2. Ensure ALL (check, environment) pairs are executed\n3. Re-submit READY_FOR_REVIEW with complete Environment Verification Matrix\n\nThe message will be rejected until the matrix shows PASS for all required combinations."
})
```

## Environment Disagreement Handling

When environments disagree (some pass, some fail), treat as FAIL:

- The entire check is considered FAILED
- The developer must fix the issue
- The developer must re-run in ALL required environments
- A new complete matrix must be reported

## Common Environment Disagreement Causes

| Cause              | Symptom                                 | Typical Fix                     |
|--------------------|-----------------------------------------|---------------------------------|
| Path separators    | Works on Mac, fails on Linux            | Use `pathlib` or `os.path.join` |
| Line endings       | Git diff fails                          | Configure `.gitattributes`      |
| Case sensitivity   | Import works on Mac, fails on Linux     | Match exact case                |
| Shell differences  | `[[` works on Mac bash, fails elsewhere | Use POSIX `[`                   |
| Missing dependency | Works locally, fails in container       | Update container setup          |
| Timezone           | Time tests fail in different TZ         | Use UTC in tests                |

## Anti-Patterns

### DO NOT:

1. **Skip environments**: "It passed in native, devcontainer is probably fine" - NO
2. **Assume exit codes**: Report actual exit codes, not assumed values
3. **Batch results**: Each (check, environment) pair needs its own row
4. **Omit the matrix**: The matrix is REQUIRED, not optional
5. **Report partial results**: All required combinations must be present

### DO:

1. Execute every required (check, environment) combination
2. Record actual exit codes from each execution
3. Include complete matrix in message
4. Confirm environment list matches requirements
5. Re-run everything if any single execution fails

## Ripple Exemption

The `ripple` teammate is **read-only** and does not run verification commands or execute code. Ripple uses native tools (`Grep`, `Glob`, `Read`) to trace downstream impact of changes. It does not participate in the environment verification matrix and is exempt from all execution environment requirements. Ripple never edits files and never runs commands — its analysis is purely static.

## Cross-References

- Task delivery loop: [task-delivery-loop.md](task-delivery-loop.md)
- Team architecture: [team-architecture.md](team-architecture.md)
