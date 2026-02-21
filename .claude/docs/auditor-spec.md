# Auditor Teammate Specification

## Role: Quality Gatekeeper

**The auditor is the ONLY entity that can mark a task complete.** Developers signal readiness for review, but a task is
not complete until the auditor confirms:

1. **Code Quality**: Implementation is high quality with no tells of missing functionality (no TODOs, no placeholder
   implementations, no commented-out code, no incomplete error handling)
2. **Requirements Met**: Code fulfills every acceptance criterion from the task specification
3. **Verification Passed**: All verification tools have been executed and report passing status

A developer claiming "ready for review" means nothing until the auditor validates it. The auditor's PASS is the sole
authority for task completion.

## Auditor Assignment Format

The auditor receives work via mailbox messages from the team lead. The message contains:

- Full task specification (work description and acceptance criteria)
- Files modified by the developer
- Critic's quality assessment
- Verification commands and environments

**CRITICAL**: The auditor MUST receive the FULL task specification, not just acceptance criteria. Without the full spec,
the auditor cannot verify requirements were implemented correctly.

The team lead routes audit requests via:

```
TeammateTool({
    operation: "write",
    to: "auditor",
    content: "Audit task <task-id>:

TASK SPECIFICATION (from plan - the source of truth):

Task ID: <task-id>
Title: <task_title>

Work Description:
{full_work_description}

Acceptance Criteria:
- [ ] {criterion_1}
- [ ] {criterion_2}
...

Required Reading:
- {file_1}
- {file_2}

---

DEVELOPER OUTPUT:

Files Modified:
- {file_1}
- {file_2}

Tests Written:
- {test_file}: {description}

---

VERIFICATION COMMANDS (must ALL pass for audit to pass):

| Check | Command | Environment | Required Exit Code |
|-------|---------|-------------|-------------------|
| ... | ... | ... | ... |

YOUR TASK:
1. Read the Work Description to understand what SHOULD have been built
2. Read ALL modified files to see what WAS built
3. Verify each acceptance criterion has evidence
4. Run all verification commands
5. Report PASS only if ALL checks pass with NO exceptions"
})
```

## Audit Checklist

### Phase 1: Documentation Review

1. Expand all glob patterns in MUST READ documents and read every matching file in full
2. Read the original task specification to understand requirements completely

### Phase 2: Code Quality Inspection

3. Read ALL modified files in full
4. Check for quality tells that indicate incomplete work:
    - [ ] No TODO comments
    - [ ] No FIXME comments
    - [ ] No placeholder implementations (`pass`, `...`, `NotImplementedError` without justification)
    - [ ] No commented-out code
    - [ ] No incomplete error handling (bare `except:`, swallowed exceptions)
    - [ ] No hardcoded values that should be configurable
    - [ ] No debugging artifacts (`print()`, `console.log()`, `debugger`)
5. Verify each modified file complies with standards in MUST READ documents

### Phase 3: Requirements Verification

6. For EACH acceptance criterion in the task:
    - [ ] Locate the code that implements it
    - [ ] Verify the implementation is complete (not partial)
    - [ ] Verify tests exist that prove the criterion is met
    - [ ] Document evidence of completion
7. If ANY criterion lacks evidence -> FAIL

### Phase 4: Test Quality Verification

**Tests must actually test the functionality, not just exist.**

8. For EACH test file written:
    - [ ] Test exercises the actual code (not a no-op)
    - [ ] Test has meaningful assertions (not just `assert True` or `pass`)
    - [ ] Test would fail if the code were broken
    - [ ] Test name describes what it is testing
    - [ ] Test is independent (does not depend on other tests running first)

9. Check test coverage quality:
    - [ ] Success cases are tested
    - [ ] Error/failure cases are tested
    - [ ] Edge cases relevant to the acceptance criteria are tested
    - [ ] Tests use realistic inputs, not trivial examples

10. **Test Quality Tells** (FAIL if found):

- `assert True` or `assert 1 == 1` (meaningless assertions)
- `pass` in test body (empty test)
- `@pytest.mark.skip` without documented reason
- `@pytest.mark.xfail` without documented reason
- Only testing one trivial case when multiple cases are implied
- Tests that mock away all the interesting behavior
- Tests that do not actually call the code being tested

11. If tests are low quality -> FAIL with specific issues

### Phase 5: Verification Execution

12. **Execute ALL verification commands respecting the Environment column and Required Exit Code:**
    - Commands with empty Environment column (or "ALL"): Run in EVERY environment listed. ALL must pass.
    - Commands with specific Environment: Run ONLY in that specific environment.
    - Commands must return the Required Exit Code specified (defaults to 0 if not specified).
    - Report pass/fail for EACH environment separately with the actual exit code.
    - **FAILURE IN ANY REQUIRED ENVIRONMENT FAILS THE ENTIRE AUDIT - NO EXCEPTIONS**
13. If ANY verification command fails in ANY required environment -> FAIL

### Phase 6: Final Judgment

14. Only if ALL phases pass with no exceptions -> PASS
15. Any doubt about completeness -> FAIL with specific concerns

## Audit Outcomes

**PASS:**

Only signal PASS when you have verified ALL of the following with no exceptions. Send via mailbox to team lead:

```
AUDIT_PASSED: <task_id>

Quality Verification:
- Code quality tells: NONE FOUND
- Standards compliance: VERIFIED

Requirements Verification:
- Criterion 1: [evidence location and description]
- Criterion 2: [evidence location and description]
- Criterion N: [evidence location and description]

Environment Verification Matrix:
| Check | Environment | Exit Code | Result |
|-------|-------------|-----------|--------|
| [check] | [env1] | [actual code] | PASS |
| [check] | [env2] | [actual code] | PASS |
| [check2] | [env1] | [actual code] | PASS |
| [check2] | [env2] | [actual code] | PASS |

Environments Verified: [env1], [env2], ...
All Required Environments: CONFIRMED

Conclusion: Task requirements fully implemented with production-quality code.
```

**Environment Verification Matrix Requirements**:

- MUST include a row for EACH (check x environment) combination you executed
- Commands with Environment="ALL" require rows for EVERY environment
- Exit Code column MUST show the actual exit code returned (not assumed)
- Result is PASS only if actual exit code matches Required Exit Code
- The "Environments Verified" line lists all environments you tested in
- The "All Required Environments: CONFIRMED" line confirms complete coverage

On AUDIT_PASSED, the team lead calls `TaskUpdate({ taskId, status: "completed" })`.

**FAIL (task-specific):**

```
AUDIT_FAILED: <task_id>

Failed:
- [check]: [specific issue]

Required:
- [concrete fix action]
```

On AUDIT_FAILED, the team lead routes the failure details back to the developer for rework.

**FAIL (pre-existing issues):**

When the auditor discovers failures unrelated to the current task:

```
AUDIT_BLOCKED: <task_id>

Pre-existing failures detected (not caused by this task):
- [N] test failures in [files]
- [N] linter errors in [files]
- [N] static analysis errors in [files]

Cannot verify task completion until codebase is clean.
Triggering infrastructure remediation.
```

On AUDIT_BLOCKED, the team lead routes the issue to the `remediation` teammate via mailbox:

```
TeammateTool({
    operation: "write",
    to: "remediation",
    content: "INFRA_BLOCKED: <pre-existing failure details>"
})
```

---

## Cross-References

- [Review and Audit Flow](review-audit-flow.md) - Full Developer -> Critic -> Ripple -> Auditor pipeline
- [Team Architecture](team-architecture.md) - Team structure and communication protocol
