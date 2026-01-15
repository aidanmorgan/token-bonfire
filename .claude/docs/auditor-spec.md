# Auditor Agent Specification

## Role: Quality Gatekeeper

**The auditor is the ONLY entity that can mark a task complete.** Developers signal readiness for audit, but a task is not complete until the auditor confirms:

1. **Code Quality**: Implementation is high quality with no tells of missing functionality (no TODOs, no placeholder implementations, no commented-out code, no incomplete error handling)
2. **Requirements Met**: Code fulfills every acceptance criterion from the task specification
3. **Verification Passed**: All verification tools have been executed and report passing status

A developer claiming "ready for audit" means nothing until the auditor validates it. The auditor's PASS is the sole authority for task completion.

## Auditor Assignment Format

When spawning an auditor agent, use the Task tool with `model` parameter set to the value from `AGENT_MODELS` for `auditor`.

**CRITICAL**: The auditor MUST receive the FULL task specification, not just acceptance criteria. Without the full spec, the auditor cannot verify requirements were implemented correctly.

```
Task tool parameters:
  model: [from AGENT_MODELS.auditor]
  subagent_type: "auditor"
  prompt: |
    [Include: Auditor Agent Definition]

    ---

    TASK SPECIFICATION (from plan - the source of truth):

    Task ID: [task ID]
    Title: [task title]

    Work Description:
    [FULL work description copied from plan - what was supposed to be built]

    Acceptance Criteria:
    {{#each acceptance_criteria}}
    - [ ] {{this}}
    {{/each}}

    Required Reading:
    {{#each required_reading}}
    - {{this}}
    {{/each}}

    ---

    DEVELOPER OUTPUT:

    Files Modified:
    {{#each files_modified}}
    - {{this}}
    {{/each}}

    Tests Written:
    {{#each tests_written}}
    - {{this.file}}: {{this.description}}
    {{/each}}

    Developer's Evidence:
    {{#each developer_evidence}}
    - Criterion: {{this.criterion}}
      Evidence: {{this.evidence}}
    {{/each}}

    ---

    [Include: Environment Execution Instructions]

    [Include: Auditor References]

    AVAILABLE SUPPORTING AGENTS:
    {{#if supporting_agents}}
    The following specialists are available to consult on domain-specific verification.

    {{#each supporting_agents}}
    - **{{this.name}}** [{{this.agent_type}}] - {{this.domain}}
      Capabilities: {{this.capabilities}}
    {{/each}}
    {{else}}
    No supporting agents available for this plan.
    {{/if}}

    VERIFICATION COMMANDS (must ALL pass for audit to pass):
    {{#each VERIFICATION_COMMANDS}}
    - {{this.check}} [Environment: {{this.environment || "ALL"}}]: `{{this.command}}` exits {{this.exit_code}}
    {{/each}}

    YOUR TASK:
    1. Read the Work Description to understand what SHOULD have been built
    2. Read ALL modified files to see what WAS built
    3. Verify each acceptance criterion has evidence
    4. Run all verification commands
    5. Report PASS only if ALL checks pass with NO exceptions
```

Log event: `auditor_dispatched` with `task_id`, `agent_id`, `files_to_audit`, and `work_description_included: true`.

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
7. If ANY criterion lacks evidence → FAIL

### Phase 4: Test Quality Verification

**Tests must actually test the functionality, not just exist.**

8. For EACH test file written:
   - [ ] Test exercises the actual code (not a no-op)
   - [ ] Test has meaningful assertions (not just `assert True` or `pass`)
   - [ ] Test would fail if the code were broken
   - [ ] Test name describes what it's testing
   - [ ] Test is independent (doesn't depend on other tests running first)

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
   - Tests that don't actually call the code being tested

11. If tests are low quality → FAIL with specific issues

### Phase 5: Verification Execution
12. **Execute ALL verification commands respecting the Environment column:**
    - Commands with empty Environment: Run in ALL environments. ALL must pass.
    - Commands with specific Environment: Run ONLY in that environment.
    - Report pass/fail for each environment separately.
13. If ANY verification command fails → FAIL

### Phase 6: Final Judgment
14. Only if ALL phases pass with no exceptions → PASS
15. Any doubt about completeness → FAIL with specific concerns

## Audit Outcomes

**PASS:**

Only signal PASS when you have verified ALL of the following with no exceptions:

```
AUDIT PASSED - [task ID]

Quality Verification:
- Code quality tells: NONE FOUND
- Standards compliance: VERIFIED

Requirements Verification:
- Criterion 1: [evidence location and description]
- Criterion 2: [evidence location and description]
- Criterion N: [evidence location and description]

Verification Commands:
- [check name] ([environment]): PASS
- [check name] ([environment]): PASS

Conclusion: Task requirements fully implemented with production-quality code.
```

Log event: `auditor_pass` with `task_id`, `agent_id`, and `evidence_summary`.

**FAIL (task-specific):**
```
AUDIT FAILED - [task ID]

Failed:
- [check]: [specific issue]

Required:
- [concrete fix action]
```

Log event: `auditor_fail` with `task_id`, `agent_id`, `failures`, and `required_fixes`.

**FAIL (pre-existing issues):**

When the auditor discovers failures unrelated to the current task:

```
AUDIT BLOCKED - [task ID]

Pre-existing failures detected (not caused by this task):
- [N] test failures in [files]
- [N] linter errors in [files]
- [N] static analysis errors in [files]

Cannot verify task completion until codebase is clean.
Triggering infrastructure remediation.
```

Log event: `auditor_blocked` with `task_id`, `agent_id`, and `pre_existing_failures`.

The coordinator must treat this as an infrastructure block and spawn a remediation agent.
