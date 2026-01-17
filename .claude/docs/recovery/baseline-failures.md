# Pre-Existing Failures Baseline

Procedures for establishing and using a baseline of pre-existing failures to distinguish between inherited problems and
newly introduced issues.

## Overview

Establish a baseline of what failures exist BEFORE any work begins. This allows distinguishing between:

- **Pre-existing failures**: Issues that existed before the session started
- **Task-introduced failures**: Issues caused by work done in this session

See also:

- [Session Recovery](session-recovery.md) - Complete recovery procedures including baseline
- [Event Log Recovery](event-log-recovery.md) - Event log as source of truth
- [Recovery Index](index.md) - Overview of all recovery procedures

---

## Baseline Capture at Session Start

```python
def capture_pre_existing_failures_baseline(config: dict) -> dict:
    """Run all verification commands and capture any failures as baseline."""

    baseline = {
        'captured_at': datetime.now().isoformat(),
        'environments': {},
        'summary': {
            'total_failures': 0,
            'by_environment': {},
            'by_check': {}
        }
    }

    for env in config['ENVIRONMENTS']:
        env_name = env['name']
        baseline['environments'][env_name] = {
            'checks': {},
            'failure_count': 0
        }

        for cmd in config['VERIFICATION_COMMANDS']:
            check_name = cmd['check']
            command = cmd['command']
            expected_exit = cmd.get('exit_code', 0)

            # Execute check in environment with timeout to prevent hang
            BASELINE_CHECK_TIMEOUT_SECONDS = 60  # Max time per check
            try:
                result = execute_in_environment(command, env_name,
                                                timeout=BASELINE_CHECK_TIMEOUT_SECONDS)
            except TimeoutError:
                # Treat timeout as failure with special marker
                result = ExecutionResult(
                    exit_code=-1,
                    output=f"TIMEOUT after {BASELINE_CHECK_TIMEOUT_SECONDS}s"
                )
                log_event("baseline_check_timeout",
                          check=check_name,
                          environment=env_name,
                          command=command)

            check_result = {
                'command': command,
                'exit_code': result.exit_code,
                'expected_exit_code': expected_exit,
                'passed': result.exit_code == expected_exit,
                'timed_out': result.exit_code == -1,
                'output_summary': result.output[:500] if not result.exit_code == expected_exit else None
            }

            baseline['environments'][env_name]['checks'][check_name] = check_result

            if not check_result['passed']:
                baseline['environments'][env_name]['failure_count'] += 1
                baseline['summary']['total_failures'] += 1
                baseline['summary']['by_environment'][env_name] =
                    baseline['summary']['by_environment'].get(env_name, 0) + 1
                baseline['summary']['by_check'][check_name] =
                    baseline['summary']['by_check'].get(check_name, 0) + 1

    return baseline
```

## Baseline Storage

Store the baseline in state and in a dedicated file for reference:

```python
def store_pre_existing_baseline(baseline: dict, plan_dir: str):
    """Store baseline for later reference."""

    # Store in state
    state['pre_existing_failures_baseline'] = baseline

    # Also write to file for debugging
    baseline_path = f"{plan_dir}/.pre-existing-baseline.json"
    Write(baseline_path, json.dumps(baseline, indent=2))

    log_event("pre_existing_baseline_captured",
              total_failures=baseline['summary']['total_failures'],
              by_environment=baseline['summary']['by_environment'],
              by_check=baseline['summary']['by_check'])

    save_state()
```

## Pre-Existing Failure Classification

When an auditor reports failures, classify them:

```python
def classify_audit_failures(current_failures: list, baseline: dict, task_id: str) -> dict:
    """Classify failures as pre-existing or task-introduced."""

    classification = {
        'pre_existing': [],
        'task_introduced': [],
        'uncertain': []
    }

    for failure in current_failures:
        check_name = failure['check']
        env_name = failure['environment']

        # Check if this failure existed in baseline
        baseline_check = baseline['environments'].get(env_name, {}).get('checks', {}).get(check_name, {})

        if not baseline_check:
            # Check didn't exist in baseline - uncertain
            classification['uncertain'].append(failure)
        elif not baseline_check['passed']:
            # Failed in baseline too - pre-existing
            failure['baseline_exit_code'] = baseline_check['exit_code']
            classification['pre_existing'].append(failure)
        else:
            # Passed in baseline, fails now - task introduced
            failure['baseline_exit_code'] = baseline_check['exit_code']
            classification['task_introduced'].append(failure)

    log_event("failure_classification",
              task_id=task_id,
              pre_existing=len(classification['pre_existing']),
              task_introduced=len(classification['task_introduced']),
              uncertain=len(classification['uncertain']))

    return classification
```

## Handling Based on Classification

```python
def handle_classified_failures(task_id: str, classification: dict):
    """Route failures based on classification."""

    # Task-introduced failures: Developer must fix
    if classification['task_introduced']:
        return {
            'action': 'REWORK',
            'failures': classification['task_introduced'],
            'message': f"Task introduced {len(classification['task_introduced'])} new failures"
        }

    # Pre-existing failures only: Trigger remediation
    if classification['pre_existing'] and not classification['task_introduced']:
        return {
            'action': 'REMEDIATE_PRE_EXISTING',
            'failures': classification['pre_existing'],
            'message': f"{len(classification['pre_existing'])} pre-existing failures detected - triggering remediation"
        }

    # Mixed: Developer fixes task-introduced, then remediation for pre-existing
    if classification['pre_existing'] and classification['task_introduced']:
        return {
            'action': 'REWORK_THEN_REMEDIATE',
            'task_failures': classification['task_introduced'],
            'pre_existing_failures': classification['pre_existing'],
            'message': f"Fix {len(classification['task_introduced'])} task-introduced failures first, then remediate {len(classification['pre_existing'])} pre-existing"
        }

    return {'action': 'PASS', 'message': 'No failures detected'}
```

## Session Start with Baseline Check

```python
def session_start_with_baseline():
    """Full session start including baseline capture."""

    # 1. Run standard recovery checks
    recovery_issues = session_recovery_check()

    # 2. Check if baseline already exists (session resume)
    if 'pre_existing_failures_baseline' in state:
        baseline = state['pre_existing_failures_baseline']
        log_event("using_existing_baseline",
                  captured_at=baseline['captured_at'],
                  total_failures=baseline['summary']['total_failures'])
    else:
        # 3. Capture fresh baseline
        output("Capturing pre-existing failures baseline...")
        baseline = capture_pre_existing_failures_baseline(CONFIG)
        store_pre_existing_baseline(baseline, PLAN_DIR)

        if baseline['summary']['total_failures'] > 0:
            output(f"WARNING: {baseline['summary']['total_failures']} pre-existing failures detected")
            output(f"  By environment: {baseline['summary']['by_environment']}")
            output(f"  By check: {baseline['summary']['by_check']}")

            # Ask whether to proceed or remediate first
            if baseline['summary']['total_failures'] > 10:
                output("RECOMMEND: Remediate pre-existing failures before starting work")

    return baseline
```

## State Format for Baseline

```json
{
  "pre_existing_failures_baseline": {
    "captured_at": "2025-01-16T10:00:00Z",
    "environments": {
      "native": {
        "checks": {
          "unit_tests": {
            "passed": true,
            "exit_code": 0
          },
          "lint": {
            "passed": false,
            "exit_code": 1,
            "output_summary": "..."
          }
        },
        "failure_count": 1
      },
      "devcontainer": {
        "checks": {
          "unit_tests": {
            "passed": true,
            "exit_code": 0
          },
          "lint": {
            "passed": false,
            "exit_code": 1,
            "output_summary": "..."
          }
        },
        "failure_count": 1
      }
    },
    "summary": {
      "total_failures": 2,
      "by_environment": {
        "native": 1,
        "devcontainer": 1
      },
      "by_check": {
        "lint": 2
      }
    }
  }
}
```

---

## Cross-References

- [Session Recovery](session-recovery.md) - Complete session recovery including baseline
- [Environment Verification](../environment-verification.md) - Verification commands and procedures
- [Remediation Loop](../remediation-loop.md) - Handling pre-existing failures
