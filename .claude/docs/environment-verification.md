# Environment Verification Specification

This document specifies how agents must execute and report verification commands across multiple environments, and how
the coordinator enforces complete coverage.

## Execution Environments

The coordinator provides a list of execution environments in `EXECUTION ENVIRONMENTS`. Each environment represents a
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

Before running any verification, build the execution matrix:

```python
def build_execution_matrix(verification_commands, execution_environments):
    """Build complete matrix of (check, environment) pairs."""

    matrix = []

    for cmd in verification_commands:
        env_value = cmd.get('environment', 'ALL')
        required_exit = cmd.get('exit_code', 0)

        if env_value in ('', 'ALL'):
            # Universal: run in ALL environments
            for env in execution_environments:
                matrix.append({
                    'check': cmd['check'],
                    'command': cmd['command'],
                    'environment': env,
                    'required_exit_code': required_exit
                })
        else:
            # Specific: run only in named environment
            matrix.append({
                'check': cmd['check'],
                'command': cmd['command'],
                'environment': env_value,
                'required_exit_code': required_exit
            })

    return matrix
```

### Step 2: Execute Each Matrix Entry

For each entry in the execution matrix:

1. Switch to the target environment (if different from current)
2. Execute the command
3. Capture the actual exit code
4. Record pass/fail based on exit code match

```python
def execute_verification_matrix(matrix):
    """Execute all verification commands and record results."""

    results = []

    for entry in matrix:
        # Switch environment if needed
        activate_environment(entry['environment'])

        # Execute command
        actual_exit_code = run_command(entry['command'])

        # Determine result
        passed = (actual_exit_code == entry['required_exit_code'])

        results.append({
            'check': entry['check'],
            'environment': entry['environment'],
            'required_exit_code': entry['required_exit_code'],
            'actual_exit_code': actual_exit_code,
            'result': 'PASS' if passed else 'FAIL'
        })

    return results
```

### Step 3: Validate Complete Coverage

Before signaling completion, verify the matrix is complete:

```python
def validate_environment_coverage(results, verification_commands, execution_environments):
    """Ensure all required (check, environment) pairs were executed."""

    expected = build_execution_matrix(verification_commands, execution_environments)
    executed = {(r['check'], r['environment']) for r in results}

    missing = []
    for entry in expected:
        key = (entry['check'], entry['environment'])
        if key not in executed:
            missing.append(key)

    if missing:
        raise VerificationIncompleteError(
            f"Missing environment verification: {missing}"
        )

    return True
```

## Signal Format Requirements

### Developer READY_FOR_REVIEW

The environment verification matrix MUST be included in the signal:

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

- MUST include a row for EACH check × environment combination required
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

## Coordinator Validation

### Signal Validation Regex

The coordinator validates signals using these regex patterns:

```python
MATRIX_HEADER_PATTERN = r'\| Check \| Environment \| Exit Code \| Result \|'
MATRIX_ROW_PATTERN = r'\| (\S+) \| (\S+) \| (\d+) \| (PASS|FAIL) \|'
ENVIRONMENTS_TESTED_PATTERN = r'Environments Tested: (.+)'
VERIFIED_PATTERN = r'All Required Environments: VERIFIED'
```

### On READY_FOR_REVIEW Signal

The coordinator validates the signal BEFORE routing to Critic:

```python
def validate_ready_for_review_signal(signal_text, task_id, config):
    """Validate environment matrix in developer signal."""

    # 1. Check for matrix header
    if not re.search(MATRIX_HEADER_PATTERN, signal_text):
        return {
            'valid': False,
            'error': 'Missing Environment Verification Matrix header',
            'action': 'REJECT_SIGNAL'
        }

    # 2. Extract all matrix rows
    rows = re.findall(MATRIX_ROW_PATTERN, signal_text)
    if not rows:
        return {
            'valid': False,
            'error': 'No verification results found in matrix',
            'action': 'REJECT_SIGNAL'
        }

    # 3. Build expected matrix
    expected = build_execution_matrix(
        config['VERIFICATION_COMMANDS'],
        config['ENVIRONMENTS']
    )

    # 4. Check each expected entry exists and passed
    parsed_results = {(r[0], r[1]): {'exit_code': int(r[2]), 'result': r[3]}
                      for r in rows}

    for entry in expected:
        key = (entry['check'], entry['environment'])
        if key not in parsed_results:
            return {
                'valid': False,
                'error': f"Missing: {entry['check']} in {entry['environment']}",
                'action': 'REJECT_SIGNAL'
            }
        result = parsed_results[key]
        if result['result'] != 'PASS':
            return {
                'valid': False,
                'error': f"Failed: {entry['check']} in {entry['environment']} (exit {result['exit_code']})",
                'action': 'REJECT_SIGNAL'
            }

    # 5. Check "Environments Tested" line
    env_match = re.search(ENVIRONMENTS_TESTED_PATTERN, signal_text)
    if not env_match:
        return {
            'valid': False,
            'error': 'Missing "Environments Tested:" line',
            'action': 'REJECT_SIGNAL'
        }

    # 6. Check "All Required Environments: VERIFIED" confirmation
    if not re.search(VERIFIED_PATTERN, signal_text):
        return {
            'valid': False,
            'error': 'Missing "All Required Environments: VERIFIED" confirmation',
            'action': 'REJECT_SIGNAL'
        }

    return {'valid': True, 'parsed_matrix': parsed_results}
```

### On Signal Rejection

If validation fails, the coordinator does NOT route to Critic:

```python
def handle_signal_rejection(task_id, developer_id, validation_result):
    """Handle rejected READY_FOR_REVIEW signal."""

    log_event("signal_rejected",
              task_id=task_id,
              developer_id=developer_id,
              reason=validation_result['error'])

    # Return developer to implementing status (DO NOT route to Critic)
    update_task_status(task_id, "implementing")

    # Notify developer of required action
    send_to_developer(developer_id, f"""
SIGNAL REJECTED: {task_id}

Reason: {validation_result['error']}

Required Action:
1. Re-run the missing/failed verification in the required environment(s)
2. Ensure ALL (check, environment) pairs are executed
3. Re-submit READY_FOR_REVIEW with complete Environment Verification Matrix

The signal will be rejected until the matrix shows PASS for all required combinations.
""")

    save_state()
```

## State Tracking

Track per-environment results in state:

```json
{
  "in_progress_tasks": [
    {
      "task_id": "task-3",
      "developer_id": "dev-agent-1",
      "status": "implementing",
      "environment_verification": {
        "required_environments": ["native", "devcontainer"],
        "verification_commands": [
          {"check": "unit_tests", "environment": "ALL", "exit_code": 0},
          {"check": "lint", "environment": "ALL", "exit_code": 0}
        ],
        "developer_results": null,
        "signal_attempts": 0
      }
    }
  ],
  "pending_audit": [
    {
      "task_id": "task-4",
      "environment_verification": {
        "required_environments": ["native", "devcontainer"],
        "developer_results": [
          {"check": "unit_tests", "environment": "native", "exit_code": 0, "result": "PASS"},
          {"check": "unit_tests", "environment": "devcontainer", "exit_code": 0, "result": "PASS"},
          {"check": "lint", "environment": "native", "exit_code": 0, "result": "PASS"},
          {"check": "lint", "environment": "devcontainer", "exit_code": 0, "result": "PASS"}
        ],
        "signal_attempts": 1,
        "auditor_results": null
      }
    }
  ]
}
```

## Environment Disagreement Handling

When environments disagree (some pass, some fail), treat as FAIL:

```python
def handle_environment_disagreement(task_id, check_name, disagreement):
    """Handle case where environments disagree on verification result."""

    log_event("environment_disagreement",
              task_id=task_id,
              check=check_name,
              passed_in=disagreement['passed'],
              failed_in=disagreement['failed'])

    # Treat as failure - developer must fix
    return {
        'result': 'FAIL',
        'reason': 'environment_disagreement',
        'details': {
            'check': check_name,
            'passed_environments': disagreement['passed'],
            'failed_environments': disagreement['failed'],
            'investigation_needed': True
        }
    }
```

## Common Environment Disagreement Causes

| Cause              | Symptom                                 | Typical Fix                     |
|--------------------|-----------------------------------------|---------------------------------|
| Path separators    | Works on Mac, fails on Linux            | Use `pathlib` or `os.path.join` |
| Line endings       | Git diff fails                          | Configure `.gitattributes`      |
| Case sensitivity   | Import works on Mac, fails on Linux     | Match exact case                |
| Shell differences  | `[[` works on Mac bash, fails elsewhere | Use POSIX `[`                   |
| Missing dependency | Works locally, fails in container       | Update container setup          |
| Timezone           | Time tests fail in different TZ         | Use UTC in tests                |

## Failure Handling

### Single Environment Failure

If a check fails in one environment but passes in another:

1. The entire check is considered FAILED
2. Developer must fix the issue
3. Developer must re-run in ALL required environments
4. A new complete matrix must be reported

### Environment Unavailable

If an environment is unavailable:

```
INFRA_BLOCKED: [task ID]

Issue: Environment '[env_name]' unavailable
Attempted:
- [what was tried to access the environment]

Cannot complete verification - environment required for:
- [check 1]
- [check 2]

Cannot proceed until environment is restored.
```

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
3. Include complete matrix in signal
4. Confirm environment list matches requirements
5. Re-run everything if any single execution fails

## Cross-References

- Task delivery loop: [task-delivery-loop.md](task-delivery-loop.md)
- Signal formats: [signal-specification.md](signal-specification.md)
- Developer specification: [developer-spec.md](developer-spec.md)
- Auditor specification: [auditor-spec.md](auditor-spec.md)
