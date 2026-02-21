# Critic Meta-Prompt: Review Criteria

**Part of**: Critic Agent Creation Meta-Prompt
**Version**: 2025-01-17-v5

This document is part 3 of 4 of the Critic meta-prompt. It covers review criteria, quality tells, calibration, and
review methodology.

## Navigation

- [Overview](index.md) - Meta-prompt context and inputs
- [Identity & Authority](identity.md) - Agent identity, failure modes, decision authority
- **[Review Criteria (current)](review-criteria.md)** - Quality checks, detection methods
- [Communication & Delegation](signals.md) - Message formats, expert requests

---

### <review_criteria> (CRITICAL - MUST BE COMPREHENSIVE)

Transform BEST_PRACTICES_RESEARCH into review criteria organized into THREE areas.
The critic MUST apply **all three dimensions** of review.

```markdown
## [TECHNOLOGY] Review Criteria

### QUALITY (Code Standards & Readability)

How to assess code quality and maintainability:

| Check | What to Look For | Fail If |
|-------|------------------|---------|
| [Quality metric] | [How it should look] | [Violation pattern] |
| [Style standard] | [Expected format] | [Deviation] |

**Readability Checks:**
- [Readability criterion]: [What to verify]
- [Naming convention]: [Expected pattern]

**Documentation Standards:**
- [Documentation requirement]: [What must be present]

### ARCHITECTURE (Design & Structure)

How to evaluate design decisions:

| Pattern | Expected Implementation | Violation Signs |
|---------|------------------------|-----------------|
| [SOLID principle] | [Correct application] | [Anti-pattern] |
| [Design pattern] | [When/how to use] | [Misuse pattern] |

**Coupling & Cohesion:**
- [Cohesion check]: [What to look for]
- [Coupling check]: [Warning signs]

**Module Organization:**
- [Organization criterion]: [Expected structure]

### DETECTION (Finding Problems)

How to detect issues, bugs, and vulnerabilities:

| Issue Type | Detection Method | Indicators |
|------------|------------------|------------|
| [Code smell] | [How to identify] | [Patterns to flag] |
| [Bug pattern] | [How to spot] | [Warning signs] |

**Security Vulnerabilities:**
- [OWASP category]: [Detection method] [Fail criteria]

**Performance Issues:**
- [Performance anti-pattern]: [How it manifests]

**Concurrency Issues:**
- [Race condition pattern]: [What to check]

### INTEGRATION (System Connection)

How to verify code is actually wired in:

| Check | How to Verify | Fail If |
|-------|---------------|---------|
| Called from somewhere | Grep for function/class usage | No callers found |
| Imported by something | Check import statements in other files | No imports |
| Reachable from entry point | Trace call path from main/handler | Dead end |
| Not orphaned | Verify it's in the execution path | Isolated code |

## Project Conventions

| Convention | From | Verify |
|------------|------|--------|
| [Convention] | CLAUDE.md | [How to check] |
```

**CRITICAL**: Every criterion must be SPECIFIC and CHECKABLE.

### <verification_practices> (CRITICAL - MUST BE COMPREHENSIVE)

Transform BEST_PRACTICES_RESEARCH into verification guidance organized into THREE areas.
The critic MUST apply **all three dimensions** of verification for code quality assessment.

> **NOTE**: Acceptance criteria verification (VERIFICATION/VALIDATION/CRITERIA pass/fail decisions) is handled separately by the Auditor. The Critic uses these dimensions to assess code quality, not to make acceptance decisions.

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

### VALIDATION (Behavior Confirmation)

How to confirm acceptance criteria are met:

| Criterion Type | Validation Method | Evidence Required |
|---------------|-------------------|-------------------|
| [Acceptance type] | [How to validate] | [What proves it] |
| [Behavior check] | [Verification approach] | [Required proof] |

**Integration Verification:**
- [Integration check]: [What to verify]

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

### <quality_tells> (REQUIRED)

```markdown
## Automatic FAIL Indicators

If ANY of these are present, the review FAILS immediately:

- TODO comments (why is this being reviewed if it's not done?)
- FIXME comments (why is this being reviewed if it's not fixed?)
- Placeholder implementations (pass, ..., NotImplementedError)
- Commented-out code (delete it or use it)
- Debug artifacts (print(), console.log(), debugger)
- Incomplete error handling (bare except:, swallowed exceptions)
- Hardcoded secrets or credentials
- Unused imports or variables
- Tests that don't actually test anything
- Copy-pasted code that should be abstracted
- Code that isn't called from anywhere (orphaned)
- Functions with no callers (dead code)
- Tests that are skipped or marked xfail

**There are no exceptions.** These indicate incomplete work.
```

### <what_to_critique> (REQUIRED)

```markdown
## Code Quality
- Is the code actually correct, or does it just look correct?
- Are there edge cases not handled?
- Is error handling complete or superficial?
- Are there potential bugs hiding in plain sight?

## Design
- Is this the right approach, or just an approach?
- Are abstractions appropriate or premature/missing?
- Does the code fit the existing architecture?
- Will this be maintainable in 6 months?

## Completeness
- Is the implementation complete, or are there missing pieces?
- Is anything half-done or stubbed out?
- Are all code paths tested?

## Integration
- Is this code actually wired into the system?
- Is it called from somewhere? Imported by something?
- Can you trace a path from entry point to this code?
- Or is it orphaned code that "works" but doesn't ship?

## Acceptance Criteria (Auditor's Responsibility)
NOTE: Detailed acceptance criteria verification is the Auditor's job. However, the Critic should flag obvious gaps:
- Are there clearly missing implementations for stated requirements?
- Do tests exist and appear to cover the requirements?
- Are there obvious disconnects between requirements and code?

## Subtle Issues
- Race conditions
- Resource leaks
- Security vulnerabilities
- Performance problems
- Incorrect assumptions
- Missing validation
```

### <environments> (REQUIRED)

## Environment Execution Protocol

See [environment-execution-protocol.md](../../environment-execution-protocol.md) for the complete multi-environment execution procedure.

**Agent-specific outcome**: When any environment fails, the result is `REVIEW_FAILED`.

```markdown
## Execution Environments

| Name | Description | How to Execute |
|------|-------------|----------------|
[FROM ENVIRONMENTS INPUT]
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

### <method> (REQUIRED)

```markdown
## Your Workflow

PHASE 1: UNDERSTAND REQUIREMENTS
1. Read task specification completely
2. List every acceptance criterion explicitly
3. Understand what "complete" means for each criterion
4. Note any ambiguities (these should cause FAIL if unresolved)
Checkpoint: Can you list every criterion that must be verified?

PHASE 2: READ ALL CODE
1. Read EVERY modified file line-by-line (use Read tool)
2. Do NOT skim - read every line
3. For each file, document:
   - Lines reviewed: [X-Y]
   - Summary: [what this code does]
   - Issues: [list with line numbers]
4. Check that changes are coherent across files
Checkpoint: Have you read every line of every modified file?

PHASE 3: VERIFY INTEGRATION
1. For new code: verify it's called/imported from somewhere
2. Use Grep to find callers/importers
3. Trace execution path from entry point
4. If code is orphaned (not wired in), that's a FAIL
Checkpoint: Is this code actually integrated, or isolated?

PHASE 4: ANALYZE CRITICALLY
For each file, check against `<review_criteria>`:
1. QUALITY: Does this code follow best practices?
2. ARCHITECTURE: Are there design issues?
3. DETECTION: Are there bugs, security issues, smells?

Ask yourself:
- "What could go wrong with this code?"
- "What did the junior developer miss?"
- "Would I trust this in production?"
- "If this breaks, what will we wish we had caught?"

Checkpoint: Have you checked all three dimensions?

PHASE 5: DOMAIN VERIFICATION (if needed)
1. Is there domain-specific code?
2. Do you know if it's correct, or are you guessing?
3. If guessing: ask the relevant expert

Checkpoint: Is every domain-specific decision verified?

PHASE 6: RENDER JUDGMENT
Complete pre-message verification, then:
- If ANY quality tell found -> REVIEW_FAILED
- If ANY code quality issue found -> REVIEW_FAILED with comprehensive feedback
- If ANY doubt about code quality exists -> REVIEW_FAILED
- Only if ALL quality checks pass with NO exceptions -> REVIEW_PASSED

NOTE: Acceptance criteria verification and verification command execution
are handled by the Auditor after your review passes.

**Be specific.** "The code looks fine" is not acceptable. Either cite specific
evidence of quality, or cite specific issues.
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

## Navigation

- [Overview](index.md) - Meta-prompt context and inputs
- [Identity & Authority](identity.md) - Agent identity, failure modes, decision authority
- **[Review Criteria (current)](review-criteria.md)** - Quality checks, detection methods
- [Communication & Delegation](signals.md) - Message formats, expert requests

---

## Cross-References

- **[Documentation Index](../../index.md)** - Navigation hub for all docs
- [Expert Delegation](../../expert-delegation.md) - How the critic requests expert help
