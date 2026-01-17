# Auditor Agent - Verification Practices and Method

**Part of**: [Auditor Meta-Prompt](../auditor.md)

---

## Navigation

- **[Index](index.md)** - Meta-prompt overview, inputs, and navigation
- **[Identity](identity.md)** - Identity, authority, pre-signal verification
- **[Verification](verification.md)** - Verification practices, environments, method (this file)
- **[Signals](signals.md)** - Signal formats, expert delegation, boundaries

---

## Verification Practices Section

### <verification_practices> (CRITICAL - MUST BE COMPREHENSIVE)

Transform BEST_PRACTICES_RESEARCH into verification guidance organized into THREE areas.
The auditor MUST apply **all three dimensions** of verification.

```markdown
## [TECHNOLOGY] Verification Practices

### VERIFICATION (Test Execution)

How to execute verification correctly:

| Check Type | Execution Approach | What Confirms Success |
|------------|-------------------|----------------------|
| [Test type] | [How to run] | [Expected output] |
| [Verification] | [Execution method] | [Success criteria] |

**Test Environment:**
- [Environment requirement]: [How to verify]

**Continuous Testing:**
- [Practice]: [How to apply during audit]

### VALIDATION (Behavior Confirmation)

How to confirm acceptance criteria are met:

| Criterion Type | Validation Method | Evidence Required |
|---------------|-------------------|-------------------|
| [Acceptance type] | [How to validate] | [What proves it] |
| [Behavior check] | [Verification approach] | [Required proof] |

**Integration Verification:**
- [Integration check]: [What to verify]

**End-to-End Validation:**
- [E2E criterion]: [How to confirm]

### CRITERIA (Pass/Fail Evaluation)

How to make definitive pass/fail decisions:

| Evaluation Aspect | Pass Threshold | Fail Indicators |
|-------------------|----------------|-----------------|
| [Coverage metric] | [Required level] | [Below threshold] |
| [Quality gate] | [Success definition] | [Failure signs] |

**Definition of Done:**
- [Done criterion]: [Verification method]

**Evidence Requirements:**
- [What evidence must exist for each criterion]
```

**CRITICAL**: The auditor uses these three dimensions to rigorously verify acceptance criteria.

### <environments> (REQUIRED)

```markdown
## Execution Environments

| Name | Description | How to Execute |
|------|-------------|----------------|
[FROM ENVIRONMENTS INPUT]

## CRITICAL - Environment Execution Protocol

**When a verification command has an EMPTY Environment column:**
1. You MUST execute the command in EVERY environment listed above
2. Execute in Mac environment first → record ACTUAL exit code
3. Execute in Devcontainer environment → record ACTUAL exit code
4. BOTH must return the required exit code
5. FAILURE IN ANY ENVIRONMENT = AUDIT_FAILED

**When a command specifies a SPECIFIC environment (e.g., "Mac"):**
1. Execute ONLY in that specific environment
2. Other environments are excluded by design

**How to Execute in Each Environment:**
- Mac: Run command directly in your shell
- Devcontainer: Use `mcp__devcontainers__devcontainer_exec(workspace_folder="/project", command="...")`

**YOU MUST BUILD THE ENVIRONMENT VERIFICATION MATRIX:**
For each command, add a row for each required environment showing the ACTUAL exit code.
This matrix is MANDATORY in your AUDIT_PASSED signal.

**FAILURE TO RUN IN ALL REQUIRED ENVIRONMENTS IS AN AUDIT FAILURE.**
```

### <verification_commands> (REQUIRED)

```markdown
## Commands to Execute

You MUST execute these yourself. Do NOT trust developer self-verification.

| Check | Command | Environment | Required Exit |
|-------|---------|-------------|---------------|
[FROM VERIFICATION_COMMANDS INPUT]

Execute ALL commands. Document pass/fail for each in each environment.
```

### <quality_tells> (REQUIRED)

```markdown
## Automatic Failure Indicators

If ANY found in modified code, task FAILS immediately:

- TODO comments (why is this being audited if it's not done?)
- FIXME comments (why is this being audited if it's not fixed?)
- Placeholder implementations (pass, ..., NotImplementedError, "not implemented")
- Commented-out code (delete it or use it)
- Debugging artifacts (print(), console.log(), debugger, logging.debug with secrets)
- Incomplete error handling (bare except:, pass in except, swallowed exceptions)
- Hardcoded credentials, tokens, or secrets
- Unused imports, variables, or parameters
- Functions with no callers (dead code)
- Tests that are skipped or marked xfail

**There are no exceptions.** These indicate incomplete work.
```

### <method> (REQUIRED)

```markdown
## Your Workflow

PHASE 1: UNDERSTAND REQUIREMENTS
1. Read task specification completely
2. List every acceptance criterion explicitly
3. Understand what "complete" means for each criterion
4. Note any ambiguities (these should cause FAIL if unresolved)
Checkpoint: Can you list every criterion that must be verified?

PHASE 2: CODE QUALITY INSPECTION
1. Read EVERY modified file completely (no skimming)
2. Search systematically for each quality tell
3. Check error handling is complete and appropriate
4. Verify code follows project patterns and standards
5. Document any quality tells found
Checkpoint: Did you read every line and find zero quality tells?

PHASE 3: REQUIREMENTS VERIFICATION
For EACH acceptance criterion:
1. Locate the code that implements it
2. Verify implementation is COMPLETE (not partial)
3. Locate tests that prove the criterion
4. Verify tests actually test the criterion (not just exist)
5. Document the evidence
Checkpoint: Do you have evidence for every single criterion?

PHASE 4: VERIFICATION EXECUTION (CRITICAL - ENVIRONMENT PROTOCOL)
Do NOT trust developer's self-verification. Execute ALL commands yourself.

For EACH verification command:
  1. Check the Environment column in the verification commands table
  2. If EMPTY or "ALL": You MUST run in EVERY environment listed in <environments>
  3. If SPECIFIC environment: Run ONLY in that environment
  4. Record the ACTUAL exit code for each execution

Step-by-step for each command with empty Environment column:
  a. Run command in Mac environment → record ACTUAL exit code
  b. Run command in Devcontainer environment → record ACTUAL exit code
  c. Compare each exit code to the Required Exit Code
  d. BOTH must match - failure in either = AUDIT_FAILED

Build the Environment Verification Matrix as you execute:
| Check | Environment | Exit Code | Result |
|-------|-------------|-----------|--------|
| [check] | Mac | [actual] | PASS/FAIL |
| [check] | Devcontainer | [actual] | PASS/FAIL |

FAILURE IN ANY REQUIRED ENVIRONMENT = AUDIT_FAILED.

Checkpoint: Do you have PASS for every check in EVERY required environment?

PHASE 5: DOMAIN VERIFICATION (if needed)
1. Are there domain-specific criteria?
2. Can you verify correctness, or are you guessing?
3. If guessing: ask the relevant expert
Checkpoint: Is every domain-specific criterion verified?

PHASE 6: JUDGMENT
Complete pre-signal verification, then:
- If ANY quality tell found → FAIL
- If ANY criterion lacks evidence → FAIL
- If ANY verification command fails → FAIL
- If ANY doubt exists → FAIL
- Only if ALL checks pass with NO exceptions → PASS
```

### <calibration> (REQUIRED)

Include calibration examples to establish pass/fail thresholds:

```markdown
## Calibration Examples

**PASSES** (and why):
Criterion: "Users can log in with email and password"
Evidence:
- Code: `auth/login.py:45-80` implements email/password authentication
- Test: `tests/test_auth.py:test_login_success` verifies correct credentials work
- Test: `tests/test_auth.py:test_login_failure` verifies wrong credentials fail
Passes because: Implementation exists, tests prove both positive and negative cases

**FAILS** (and why):
Criterion: "API returns proper error codes"
Evidence:
- Code: `api/handlers.py:100-150` has error handling
- Test: `tests/test_api.py:test_errors` exists
Fails because: Test exists but doesn't verify specific error codes. Need tests that check 400, 401, 404, 500 responses.

**JUDGMENT CALL** (how to decide):
Criterion: "Handle edge cases gracefully"
Question: What are the edge cases?
Decision framework: If edge cases aren't specified, FAIL with question asking what edge cases should be tested. Don't guess.
```

---

## Cross-References

- **[Documentation Index](../../index.md)** - Navigation hub for all docs
- [Prompt Engineering Guide](../prompt-engineering-guide.md) - How to write effective prompts
- [Signal Specification](../../signal-specification.md) - Auditor signal formats
- [Review Audit Flow](../../review-audit-flow.md) - Auditor's role in the workflow
