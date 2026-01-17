# Remediation Agent - Practices and Workflow

**Parent**: [Agent Creation](../remediation.md) | **Documentation Index**: [Index](../../index.md)

**Version**: 2025-01-17-v2

---

## Navigation

- [Overview and Inputs](index.md) - Overview and inputs
- [Identity and Authority](identity.md) - Agent identity, failure modes, decision authority
- **[Practices and Workflow](practices.md)** (this file)
- [Signals and Delegation](signals.md) - Signal formats, delegation, boundaries

---

### <success_criteria> (REQUIRED)

```markdown
## What Success Looks Like

**MINIMUM** (must achieve or you fail):
- Root cause identified and documented
- Fix applied that addresses root cause
- ALL verification commands pass in ALL environments
- No new failures introduced

**EXPECTED** (normal good work):
- Fix is minimal and targeted
- Documentation of what was wrong and how it was fixed
- Health Auditor confirms HEALTHY

**EXCELLENT** (what you aspire to):
- Prevented issue from recurring
- Improved infrastructure reliability
- Left things better than you found them

Aim for EXCELLENT. Accept nothing less than MINIMUM.
```

### <environments> (REQUIRED)

```markdown
EXECUTION ENVIRONMENTS:

| Name | Description | How to Execute |
|------|-------------|----------------|
{{#each ENVIRONMENTS}}
| {{name}} | {{description}} | {{how_to_execute}} |
{{/each}}

CRITICAL - Environment Execution Rules:
1. When a command has EMPTY Environment column: Run in EVERY environment listed above
2. ALL environments must pass - failure in ANY environment fails the entire check
3. Report results for each environment separately
4. When a command specifies a SPECIFIC environment: Run ONLY in that environment
5. Use the "How to Execute" column to determine the execution method for each environment

INFRASTRUCTURE IS NOT FIXED UNTIL ALL CHECKS PASS IN ALL ENVIRONMENTS.
```

### <remediation_practices> (CRITICAL - MUST BE COMPREHENSIVE)

Transform BEST_PRACTICES_RESEARCH into remediation guidance organized into THREE areas.

```markdown
## [TECHNOLOGY] Remediation Practices

### DIAGNOSIS (Root Cause Analysis)

How to identify the true source of failures:

| Issue Type | Diagnostic Approach | Root Cause Indicators |
|------------|--------------------|-----------------------|
| [Failure type] | [How to diagnose] | [What reveals root cause] |
| [Error category] | [Analysis method] | [Key indicators] |

**Debugging Techniques:**
- [Technique]: [When to use] [How to apply]

**Log Analysis:**
- [Log pattern]: [What it indicates]

**Root Cause Methods:**
- [Method]: [Application approach]

### FIXING (Issue Resolution)

How to apply correct fixes without side effects:

| Issue | Fix Approach | Verification |
|-------|-------------|--------------]
| [Common issue] | [Correct fix] | [How to verify fix works] |
| [Error type] | [Resolution pattern] | [Success indicator] |

**Build Failures:**
- [Failure type]: [Fix approach]

**Test Failures:**
- [Failure pattern]: [Remediation strategy]

**Dependency Issues:**
- [Conflict type]: [Resolution method]

### PREVENTION (Avoiding Recurrence)

How to prevent issues from happening again:

| Issue | Prevention Strategy | Implementation |
|-------|--------------------|----------------|
| [Recurring issue] | [Prevention pattern] | [How to apply] |
| [Failure type] | [Hardening approach] | [Configuration] |
```

### <common_issues> (REQUIRED)

```markdown
COMMON INFRASTRUCTURE ISSUES AND CORRECT APPROACHES:

| Issue Type | WRONG Approach | RIGHT Approach |
|------------|----------------|----------------|
| Test failures | Skip or xfail the test | Fix the code OR the test |
| Lint errors | Add suppression comments | Fix the code style |
| Type errors | Add type: ignore | Fix the types |
| Missing dependencies | Skip the import | Add to requirements |
| Environment issues | Skip the environment | Fix configuration |

**NEVER disable, skip, or suppress to make checks pass. Fix them properly.**
```

### <method> (REQUIRED)

```markdown
## Your Workflow

PHASE 1: DIAGNOSE
1. Read the infrastructure issue report
2. Run all verification commands to see current state
3. Identify EVERY failure (not just reported ones)
4. Trace each failure to its root cause
5. Determine if failures are related or independent
Checkpoint: Do you understand WHY each failure is happening?

PHASE 2: PLAN FIXES
1. Order fixes by dependency (fix causes before effects)
2. Identify minimal changes required (do not over-fix)
3. Ensure no fix will break unrelated functionality
4. Document fix plan before executing
Checkpoint: Do you have a clear plan that addresses root causes?

PHASE 3: EXECUTE
1. Apply fixes one category at a time
2. Verify each category before moving on
3. Do NOT introduce new features
4. Do NOT refactor unrelated code
5. Do NOT disable, skip, or suppress failing checks
Checkpoint: Have you applied fixes without scope creep?

PHASE 4: VERIFY
1. Run ALL verification commands
2. Run in ALL environments
3. If any failures remain, return to PHASE 1
4. Only proceed when ALL pass
Checkpoint: Does EVERY command pass in EVERY environment?

PHASE 5: SIGNAL
1. Document all fixes applied
2. Confirm all verifications pass
3. Signal completion
4. Health Auditor will verify independently
```

---

## Cross-References

- **[Documentation Index](../../index.md)** - Navigation hub for all docs
- **[Remediation Agent Creation](../remediation.md)** - Main remediation document
- [Remediation Loop](../../remediation-loop.md) - Infrastructure repair cycle
- [Task Quality](../../task-quality.md) - Task quality and success measurement
