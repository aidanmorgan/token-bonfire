# Plan File Format Specification

Plans can use **any markdown format**. Task parsing is handled by a Claude sub-agent that understands natural language structure, not rigid regex patterns.

## Plan Title & Slug

The `# [Plan Title]` heading is used to generate a deterministic **plan slug** (e.g., "User Authentication Implementation Plan" → `user-authentication-implementation-plan`). This slug identifies the shared task list — re-running the same plan reuses the same task list and preserves progress.

## What the Sub-Agent Extracts

The plan parser sub-agent reads the plan file and identifies:

| Field | Required | Description |
|-------|----------|-------------|
| Task ID | Yes | Unique identifier from the plan (e.g., `C-1`, `H-3`, `1-1-1`, `T-5`) |
| Title | Yes | Short descriptive title |
| Description | Yes | Problem statement, work to be done, implementation details |
| Acceptance Criteria | Recommended | Testable criteria for completion |
| Unit Test Plan | Optional | Specific test cases to write |
| Affected Files/Crates | Optional | Where changes should be made |
| Design References | Optional | Related design documents |
| Dependencies | Optional | Explicit or inferred execution ordering |

## Supported Plan Formats

The sub-agent can parse any of these structures:

### Priority-grouped (like gap analyses)
```markdown
## Critical Priority
### C-1: Task Title
**Problem:** ...
**Acceptance Criteria:** ...

## High Priority
### H-1: Task Title
...
```

### Phase-based (traditional)
```markdown
### Phase 1: Foundation
#### Task 1-1-1: Task Title
**Work**: ...
**Blocked By**: none
```

### Wave-based (parallel execution)
```markdown
## Execution Strategy
- **Wave 1** (C-1, C-2, H-1): Foundation tasks
- **Wave 2** (H-5, H-6): Depends on Wave 1
```

### Flat task lists
```markdown
## Tasks
- [ ] T-1: Do something
- [ ] T-2: Do something else (depends on T-1)
```

## Dependency Inference

The sub-agent determines task dependencies from:

1. **Explicit `Blocked By` fields** — direct dependency declarations
2. **Execution Strategy / Wave sections** — tasks in later waves depend on earlier waves
3. **Phase ordering** — later phases depend on earlier phases
4. **Crate/file overlap** — tasks modifying the same files may need ordering
5. **No dependencies** — if the plan has no ordering information, all tasks are created with no blockers

## Quality Guidelines for Acceptance Criteria

Good acceptance criteria are:

| Requirement | Why |
|-------------|------|
| Testable | Can run a command or check to verify |
| Specific | No ambiguity about what "done" means |
| Observable | Result can be seen or measured |

**Good**: `cargo clippy -p proscenium-query -- -D warnings` passes clean
**Bad**: "Code should be clean"

## Validation

The sub-agent validates after creating all tasks:
- All task IDs are unique
- No circular dependencies exist
- At least one task has no blockers (plan can start)
- Tasks marked as "COMPLETE" are skipped

## Example Plan

```markdown
# User Authentication Implementation Plan

## Overview
Implement user authentication with JWT tokens.

## Phases

### Phase 1: Foundation

#### Task 1-1-1: Create User Model

**Work**:
Create `User` dataclass in `src/models/user.py` with fields:
- id: int
- username: str
- password_hash: str
- created_at: datetime

**Acceptance Criteria**:
- [ ] `src/models/user.py` exists
- [ ] `User` dataclass has all required fields
- [ ] `uv run pytest tests/unit/test_user_model.py` exits 0

**Blocked By**: none

---

#### Task 1-1-2: Create UserRepository

**Work**:
Create `UserRepository` class with CRUD methods.

**Acceptance Criteria**:
- [ ] `UserRepository` class exists
- [ ] `uv run pytest tests/unit/test_user_repository.py` exits 0

**Blocked By**: 1-1-1
```
