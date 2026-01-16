# Orchestrator Gap Analysis

Critical gaps that would prevent autonomous high-quality code generation.

## Priority 1: BLOCKING - System Won't Function

### GAP-001: Plan Format Not Defined

**Problem**: The orchestrator references `{{PLAN_FILE}}` but doesn't specify the expected format. The coordinator can't
parse tasks without knowing the structure.

**Impact**: Fatal - coordinator can't extract tasks, dependencies, or acceptance criteria.

**Required**:

```markdown
## Task Format Specification

Each task in PLAN_FILE must have:
- Task ID: Unique identifier (e.g., `task-1.2.3`)
- Title: Short description
- Work: Detailed implementation specification
- Acceptance Criteria: List of verifiable requirements
- Blocked By: List of task IDs that must complete first
- Required Reading: Task-specific files to read
- Environment: (optional) Specific environment if not all
```

**Action**: Create `plan-format.md` with task schema, examples, and parsing rules.

---

### GAP-002: Agent Output Retrieval Not Specified

**Problem**: Documents say "await agent" and "parse output" but don't specify HOW the coordinator gets agent results.
The Task tool returns output, but the procedure isn't documented.

**Impact**: Fatal - coordinator can't receive signals from agents.

**Required**:

- Document that Task tool returns agent output when complete
- Specify timeout handling
- Specify what happens if agent crashes mid-work

**Action**: Add to task-delivery-loop.md how to retrieve and process Task tool results.

---

### GAP-003: Developer Codebase Access Not Documented

**Problem**: Developer agents need to read/write files, but there's no documentation about what tools they have access
to or how to use them.

**Impact**: Fatal - developers can't actually modify code.

**Required**:

```markdown
## Developer Tool Access

Developers have access to:
- Read: Read file contents
- Write: Create new files
- Edit: Modify existing files
- Glob: Find files by pattern
- Grep: Search file contents
- Bash: Run shell commands (for verification)

Before editing any file, developers MUST:
1. Read the file first
2. Understand existing patterns
3. Make minimal changes
```

**Action**: Add tool access documentation to developer-spec.md.

---

## Priority 2: HIGH - Will Cause Failures

### GAP-004: Context Delivery to Agents Undefined

**Problem**: Agents are stateless. When auditor needs task spec, or expert results need to reach developer,
HOW does that information transfer happen?

**Impact**: Agents work without proper context → wrong output.

**Current Gap**:

- Developer completes → Auditor dispatched, but auditor doesn't receive the task spec in prompt
- Expert completes → Results need to reach developer, but developer is a separate agent invocation

**Required**:

- Auditor prompt must include full task specification, not just "acceptance criteria"
- Expert results must be included in developer's NEXT prompt (rework or continuation)
- State file should track context that needs to flow between agents

**Action**: Update auditor-spec.md and developer-spec.md with explicit context inclusion.

---

### GAP-005: Concurrent File Modification Not Handled

**Problem**: With 5 parallel developers, what if two tasks modify the same file?

**Impact**: Merge conflicts, lost work, inconsistent state.

**Required**:

```markdown
## File Lock Protocol

Before dispatching a developer:
1. Identify files the task will modify (from task spec or analysis)
2. Check if any in-progress task is modifying those files
3. If conflict: either queue the task or dispatch with explicit coordination instructions

After developer completes:
1. Release file locks
2. Verify no conflicts with concurrent work
```

**Action**: Add file coordination to task-delivery-loop.md or create new `concurrency.md`.

---

### GAP-006: Acceptance Criteria Quality Not Verified

**Problem**: If plan has vague acceptance criteria ("implement feature X"), auditor can't properly verify. No validation
that acceptance criteria are testable.

**Impact**: Auditor can't do their job → bad code passes.

**Required**:

```markdown
## Acceptance Criteria Requirements

Valid acceptance criteria must be:
- Testable: Can be verified by running a command or checking code
- Specific: No ambiguity about what "done" means
- Complete: Cover all aspects of the work

Invalid examples:
- "Implement the feature" (not testable)
- "Code should be clean" (subjective)
- "Handle errors appropriately" (ambiguous)

Valid examples:
- "`uv run pytest tests/unit/test_feature.py` exits 0"
- "Function `process_data()` exists in `src/module.py`"
- "Error case returns 400 status code with message"
```

**Action**: Create acceptance criteria validation as part of plan parsing.

---

### GAP-007: Developer Context About Existing Code

**Problem**: Developer is told to "follow existing patterns" but has no efficient way to discover what patterns exist
beyond reading CLAUDE.md.

**Impact**: Inconsistent code, reinvented wheels, wrong patterns.

**Required**:

```markdown
## Pattern Discovery Protocol

Before implementing, developer should:
1. Search for similar functionality: `Grep` for related function names
2. Identify existing utilities: Read common utility files
3. Find test patterns: Look at existing tests for similar features
4. Note architectural patterns: How does data flow? What's the error handling pattern?

Include in developer prompt:
- List of "similar features" from plan analysis
- Paths to relevant utility modules
- Links to existing tests as examples
```

**Action**: Enhance developer prompt template with pattern discovery guidance.

---

## Priority 3: MEDIUM - Will Cause Quality Issues

### GAP-008: Test Quality Not Verified

**Problem**: Auditor checks tests exist but not whether tests are meaningful. Developer could write tests that always
pass.

**Impact**: Low-quality tests → bugs escape.

**Required**:

```markdown
## Test Quality Checks

Auditor must verify:
1. Tests exercise the actual functionality (not no-ops)
2. Tests have meaningful assertions (not just `assert True`)
3. Tests cover failure cases, not just success
4. Tests are independent (don't depend on order)
5. Test names describe what they test
```

**Action**: Add test quality section to auditor-spec.md audit checklist.

---

### GAP-009: No Architectural Consistency Check

**Problem**: Multiple developers working in parallel may make architecturally inconsistent decisions (different error
handling patterns, different naming conventions, different data structures for similar problems).

**Impact**: Inconsistent codebase, maintenance burden.

**Required**:

- Periodic architectural review by coordinator or quality reviewer
- Pattern enforcement across tasks
- Cross-task consistency check before marking phase complete

**Action**: Add architectural consistency to quality reviewer template or create dedicated agent.

---

### GAP-010: No Progress Visibility During Long Tasks

**Problem**: Checkpoint reporting is defined but not enforced. Long-running developers may work in silence.

**Impact**: No visibility into progress, can't detect stuck agents early.

**Required**:

```markdown
## Checkpoint Enforcement

Coordinator should request checkpoint from active developers:
- Every N minutes (configurable)
- After significant context compaction
- When load is low and coordinator is idle

Developer MUST respond to checkpoint requests within 30 seconds with:
- Current status
- What's been done
- What's remaining
- Any blockers
```

**Action**: Add checkpoint timing to continuous operation loop.

---

### GAP-011: Partial Environment Failures

**Problem**: What if tests pass in Mac but fail in Devcontainer? Current docs say "FAIL" but don't specify recovery.

**Impact**: Unclear how to proceed when environments disagree.

**Required**:

```markdown
## Environment Disagreement Protocol

If command passes in some environments but fails in others:
1. Log all results per environment
2. Treat as FAIL (most conservative)
3. Developer rework prompt includes per-environment details
4. Investigate if failure is environment-specific bug or real issue
```

**Action**: Add environment disagreement handling to task-delivery-loop.md.

---

### GAP-012: Expert Result Integration

**Problem**: When expert returns results, how does delegating developer use them? Developer is a fresh agent
invocation.

**Impact**: Expert work is wasted if not properly integrated.

**Required**:

```markdown
## Result Integration Protocol

When expert completes:
1. Store results in state under task context
2. If delegating developer is still active: inject results into conversation
3. If delegating developer finished: include results in rework prompt
4. Track which results were integrated vs pending
```

**Action**: Add result integration to agent-coordination.md.

---

## Priority 4: LOW - Nice to Have

### GAP-013: No Rollback Capability

**Problem**: If developer makes bad changes that pass audit but break something later, no rollback mechanism.

**Mitigation**: Git provides rollback, but orchestrator doesn't track which commits belong to which task.

**Action**: Consider tracking commit SHAs per task in state.

---

### GAP-014: No Learning From Failures

**Problem**: If same type of failure happens repeatedly, no mechanism to learn and prevent.

**Impact**: Same mistakes repeated.

**Action**: Consider failure pattern analysis as enhancement.

---

### GAP-015: No Dependency Cycle Detection

**Problem**: If plan has circular dependencies, coordinator may deadlock.

**Impact**: Workflow stuck with no progress.

**Action**: Add cycle detection during plan parsing.

---

## Summary: Actions Completed

All gaps have been addressed. The orchestrator is now ready for autonomous high-quality code generation.

| Priority | Gap                         | Action                                                         | Status |
|----------|-----------------------------|----------------------------------------------------------------|--------|
| P1       | GAP-001 Plan Format         | Create plan-format.md                                          | FIXED  |
| P1       | GAP-002 Agent Output        | Add to task-delivery-loop.md                                   | FIXED  |
| P1       | GAP-003 Tool Access         | Add to developer-spec.md                                       | FIXED  |
| P2       | GAP-004 Context Delivery    | Update auditor-spec.md, developer-spec.md                      | FIXED  |
| P2       | GAP-005 Concurrent Files    | Create concurrency.md                                          | FIXED  |
| P2       | GAP-006 AC Quality          | Add validation to plan parsing                                 | FIXED  |
| P2       | GAP-007 Pattern Discovery   | Enhance developer prompt                                       | FIXED  |
| P3       | GAP-008 Test Quality        | Add to auditor checklist                                       | FIXED  |
| P3       | GAP-009 Arch Consistency    | Add phase completion review to task-delivery-loop.md           | FIXED  |
| P3       | GAP-010 Progress Visibility | Add checkpoint enforcement to task-delivery-loop.md            | FIXED  |
| P3       | GAP-011 Env Disagreement    | Add environment disagreement protocol to task-delivery-loop.md | FIXED  |
| P3       | GAP-012 Result Integration  | Add result integration to agent-coordination.md                | FIXED  |
| P4       | GAP-013 Rollback            | Add rollback capability to state-management.md                 | FIXED  |
| P4       | GAP-014 Learning            | Add failure pattern learning to state-management.md            | FIXED  |
| P4       | GAP-015 Cycle Detection     | Add mandatory cycle detection to plan-format.md                | FIXED  |

### Documentation Updates Summary

| Document                   | Additions                                                                                                                            |
|----------------------------|--------------------------------------------------------------------------------------------------------------------------------------|
| task-delivery-loop.md      | Agent output retrieval, timeout tracking, architectural consistency check, checkpoint enforcement, environment disagreement protocol |
| plan-format.md             | Acceptance criteria validation, mandatory cycle detection                                                                            |
| developer-spec.md          | Tool access, pattern discovery (already present from earlier)                                                                        |
| auditor-spec.md            | Full task specification in prompt, test quality verification (already present)                                                       |
| state-management.md        | Rollback capability, failure pattern learning                                                                                        |
| agent-coordination.md      | Expert result integration                                                                                                            |
| concurrency.md             | NEW - File lock protocol, conflict detection/resolution                                                                              |
| base_variables.md          | Python tooling (pyright, pytest, ruff), AGENT_TIMEOUT                                                                                |
| main orchestrator template | AGENT_TIMEOUT variable, updated Reference Documents table                                                                            |
