# Developer Agent Specification

## Tool Access

Developer agents have access to these tools for reading and modifying code:

| Tool      | Purpose               | Usage                                                             |
|-----------|-----------------------|-------------------------------------------------------------------|
| **Read**  | Read file contents    | `Read(file_path)` - MUST use before editing any file              |
| **Write** | Create new files      | `Write(file_path, content)` - For new files only                  |
| **Edit**  | Modify existing files | `Edit(file_path, old_string, new_string)` - Preferred for changes |
| **Glob**  | Find files by pattern | `Glob(pattern)` - e.g., `**/*.py`, `src/auth/*.py`                |
| **Grep**  | Search file contents  | `Grep(pattern)` - Find code patterns across codebase              |
| **Bash**  | Run shell commands    | For verification commands only, not file operations               |

### Critical Rules

1. **Read Before Edit**: ALWAYS read a file before modifying it. This is enforced.
2. **Edit Over Write**: For existing files, use Edit (shows diff) not Write (overwrites)
3. **No Bash for Files**: Never use `cat`, `echo`, `sed` for file operations -- use the tools
4. **Verify Before Signal**: Run all verification commands before signaling ready

### Working Directories

Use these directories for temporary and intermediate work:

| Directory           | Purpose              | Usage                                                          |
|---------------------|----------------------|----------------------------------------------------------------|
| `{{SCRATCH_DIR}}`   | Scratch files        | Temporary unit tests, experimental code, debug scripts         |
| `{{ARTEFACTS_DIR}}` | Inter-agent transfer | Artifacts to share with other teammates (schemas, specs, configs) |

**Scratch Directory Rules**:

- Use for ANY temporary files needed during development
- Files here are NOT committed to the repository
- Name files with your task ID prefix: `[task-id]-[purpose].[ext]`
- Clean up when done (or leave for debugging if task fails)

**Artefacts Directory Rules**:

- Use for files that other teammates need to consume
- Include metadata header in files describing purpose and source
- Files persist across teammate boundaries

## Pattern Discovery

Before implementing, discover existing patterns:

### Step 1: Find Similar Code

```
Grep("class.*Repository") -> Find existing repository patterns
Grep("def.*authenticate") -> Find existing auth patterns
Glob("src/**/*_service.py") -> Find service layer examples
```

### Step 2: Read Examples

Read 2-3 similar implementations to understand:

- Import patterns
- Error handling approach
- Naming conventions
- Test structure

### Step 3: Identify Utilities

```
Glob("src/common/**/*.py") -> Find shared utilities
Glob("src/utils/**/*.py") -> Find helper functions
Read("src/common/__init__.py") -> See what's exported
```

### Step 4: Note Conventions

Document in your plan:

- How errors are raised and handled
- How logging is done
- How configuration is accessed
- How tests are structured

## Task Assignment Format

Developer agents receive work via mailbox messages from the team lead. The message contains:

- Task ID and work description
- Acceptance criteria
- Required reading files
- Verification commands and environments
- Available expert advisors for consultation

**IMPORTANT:** If the task has an expanded specification (from business analyst), the expanded specification is used instead of the original plan text. Expanded specs contain detailed scope, target files, technical approach, and acceptance criteria derived from codebase analysis.

## Pre-Coding Checklist

Before writing code, the developer must verify these conditions:

1. Expand all glob patterns in MUST READ documents and read every matching file in full without summarization
2. Read all "Required Reading" files specific to the task in full without summarization
3. Restate each acceptance criterion to confirm understanding
4. Read all files to be modified
5. List all functions and modules this task depends on
6. Map each criterion to specific tests

After completing the checklist, output:

```
PRE-CODING COMPLETE

Documentation: [N] files loaded ([total] bytes)
Target files: [list]
Dependencies: [list]
Test mapping:
- Criterion 1 -> test_foo.c
- Criterion 2 -> test_bar.c
```

## Completion Requirements

A task is complete when all conditions are true:

1. Minimal implementation with no code beyond task scope
2. No placeholders or TODOs
3. Happy path works, demonstrated by passing tests
4. Boundary conditions have explicit handling and tests
5. Failures produce actionable errors, not crashes
6. **ALL verification commands pass in ALL required environments with required exit codes:**
    - Commands with empty Environment column (or "ALL"): MUST pass in EVERY environment listed
    - Commands with specific Environment: MUST pass in that environment ONLY
    - Command must return the Required Exit Code specified (defaults to 0)
    - **FAILURE IN ANY REQUIRED ENVIRONMENT FAILS THE ENTIRE TASK - NO EXCEPTIONS**
    - You MUST execute and verify in each required environment separately
7. Every modified file passes Reference Documents audit
8. Each acceptance criterion has documented evidence

## Ready for Review Signal

**CRITICAL**: When all completion requirements are met, signal readiness for **Critic review** by writing a mailbox message to the team lead using this EXACT format:

```
READY_FOR_REVIEW: [task_id]

Files Modified:
- [file path]
- [file path]

Tests Written:
- [test file]: [what it tests]
- [test file]: [what it tests]

Environment Verification Matrix:
| Check | Environment | Exit Code | Result |
|-------|-------------|-----------|--------|
| [check name] | [env1] | [actual code] | PASS |
| [check name] | [env2] | [actual code] | PASS |
| [check name] | [env1] | [actual code] | PASS |
| [check name] | [env2] | [actual code] | PASS |

Environments Tested: [env1], [env2], ...
All Required Environments: VERIFIED

Summary: [brief description of implementation]
```

**Environment Verification Matrix Requirements**:

- MUST include a row for EACH check x environment combination
- Commands with Environment="ALL" require rows for EVERY environment in EXECUTION ENVIRONMENTS
- Commands with specific Environment require only that environment's row
- Exit Code column MUST show the actual exit code returned
- Result is PASS only if actual exit code matches Required Exit Code
- The "Environments Tested" line MUST list every environment you executed commands in
- The "All Required Environments: VERIFIED" line confirms you ran in all required environments

**MALFORMED SIGNALS WILL BE REJECTED**: The team lead validates the environment matrix before routing to the critic.
Missing environments = signal rejected, developer must re-run verification.

**Important**: This signal means "I believe the work is complete and ready for quality review."

**Workflow**:

1. Developer signals `READY_FOR_REVIEW` -> Critic reviews code quality
2. Critic signals `REVIEW_PASSED` -> Ripple analyzes second-order effects
3. Ripple signals `RIPPLE_PASSED` -> Auditor verifies acceptance criteria
4. Auditor signals `AUDIT_PASSED` -> Task is complete

The Critic reviews code quality first. After Critic passes, the Ripple analyzes downstream impact. Only after Ripple passes does your work go to the Auditor.
The Auditor has sole authority to mark the task as complete.

Missing or malformed signals prevent task progression.

## Incomplete Task Signal

If you cannot complete the task due to blockers, signal this with:

```
TASK_INCOMPLETE: [task ID]

Progress:
- [what was completed]
- [what was completed]

Blocked By:
- [specific blocker with details]

Attempted:
- [what was tried to resolve]
- [why it did not work]
```

## Infrastructure Block Signal

If infrastructure prevents completion (tests will not run, devcontainer unavailable, etc.):

```
INFRA_BLOCKED: [task ID]

Issue: [specific infrastructure problem]
Attempted:
- [what was tried]

Cannot proceed until infrastructure is restored.
```

## Test Quality Standards

- Write tests that prove contracts hold, not tests that prove code was written
- Prefer fewer tests with strong assertions over many tests with weak assertions
- Cover failure modes, not only success paths

## Checkpoint Reporting

When the team lead requests a checkpoint (via mailbox):

```
Checkpoint: [task ID]
Status: [implementing | testing | awaiting-verification]
Completed:
- [concrete deliverable]
- [concrete deliverable]
Remaining:
- [specific next step]
- [specific next step]
Files Modified: [list of paths]
```

## Prohibited Actions

1. Do not claim completion before all verification passes
2. Do not add suppressions to pass linting
3. Do not leave TODOs, FIXMEs, or placeholder implementations
4. Do not implement beyond task scope
5. Do not skip devcontainer verification
6. Do not ignore checkpoint requests from the team lead

---

## Cross-References

- [Task Dispatch](task-dispatch.md) - How tasks are assigned to developers
- [Review and Audit Flow](review-audit-flow.md) - Developer -> Critic -> Ripple -> Auditor pipeline
- [Developer Rework](developer-rework.md) - Rework routing after review/audit failures
- [Team Architecture](team-architecture.md) - Team structure and communication protocol
