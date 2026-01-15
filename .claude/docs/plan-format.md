# Plan File Format Specification

The `{{PLAN_FILE}}` must follow this format for the coordinator to parse and execute it.

## Required Structure

```markdown
# [Plan Title]

## Overview
[Brief description of what this plan accomplishes]

## Phases

### Phase 1: [Phase Name]

#### Task [ID]: [Title]

**Work**:
[Detailed description of what needs to be implemented]

**Acceptance Criteria**:
- [ ] [Testable criterion 1]
- [ ] [Testable criterion 2]

**Blocked By**: [task-id-1, task-id-2] OR none

**Required Reading**:
- [file path or glob pattern]

**Environment**: [Mac | Devcontainer | (blank for all)]

---

#### Task [ID]: [Title]
...

### Phase 2: [Phase Name]
...
```

## Task ID Format

Task IDs must be unique and follow the pattern: `[phase]-[section]-[number]`

Examples:
- `1-1-1` (Phase 1, Section 1, Task 1)
- `2-3-4` (Phase 2, Section 3, Task 4)
- `1-auth-1` (Phase 1, Auth Section, Task 1)

## Field Specifications

### Work Field

The work description must include:
- What to create, modify, or delete
- Expected behavior
- Integration points with existing code
- Any constraints or requirements

**Good Example**:
```markdown
**Work**:
Create a new `UserAuthenticator` class in `src/auth/authenticator.py` that:
1. Accepts username and password
2. Validates against the database using `UserRepository`
3. Returns a JWT token on success
4. Raises `AuthenticationError` on failure
5. Logs all authentication attempts

Follow the existing pattern in `src/auth/token_validator.py` for error handling.
```

**Bad Example**:
```markdown
**Work**:
Implement user authentication.
```

### Acceptance Criteria Field

Each criterion must be:

| Requirement | Why |
|-------------|-----|
| Testable | Can run a command or check to verify |
| Specific | No ambiguity about what "done" means |
| Observable | Result can be seen or measured |
| Independent | Can be verified in isolation |

**Valid Criteria Patterns**:

```markdown
**Acceptance Criteria**:
- [ ] `uv run pytest tests/unit/test_authenticator.py` exits 0
- [ ] Class `UserAuthenticator` exists in `src/auth/authenticator.py`
- [ ] Method `authenticate(username, password)` returns `str` (JWT token)
- [ ] Invalid credentials raise `AuthenticationError` with message
- [ ] All authentication attempts logged to `auth.log`
- [ ] `uv run pyright src/auth/authenticator.py` reports 0 errors
```

**Invalid Criteria**:

| Criterion | Problem |
|-----------|---------|
| "Code should be clean" | Subjective, not testable |
| "Implement the feature" | Not specific |
| "Handle errors appropriately" | Ambiguous |
| "Should be fast" | Not measurable without numbers |
| "Follow best practices" | Vague |

### Blocked By Field

Specify task IDs that must complete before this task can start.

```markdown
**Blocked By**: 1-1-1, 1-1-2
```

Or if no dependencies:
```markdown
**Blocked By**: none
```

### Required Reading Field

Files the developer must read before starting work.

```markdown
**Required Reading**:
- src/auth/token_validator.py (existing pattern)
- design/auth-flow.md (specification)
- tests/unit/test_token_validator.py (test pattern)
```

Supports glob patterns:
```markdown
**Required Reading**:
- src/auth/**/*.py
- design/auth-*.md
```

### Environment Field

Restrict task to specific environment. Omit for all environments.

```markdown
**Environment**: Devcontainer
```

Valid values:
- `Mac` - macOS only
- `Devcontainer` - Linux container only
- (blank) - Must pass in ALL environments

## Coordinator Parsing Procedure

### Step 1: Extract Phases

```python
phases = []
current_phase = None

for line in plan_content.split('\n'):
    if line.startswith('### Phase'):
        phase_match = re.match(r'### Phase (\d+): (.+)', line)
        current_phase = {
            'number': phase_match.group(1),
            'name': phase_match.group(2),
            'tasks': []
        }
        phases.append(current_phase)
```

### Step 2: Extract Tasks

```python
for each phase:
    tasks = re.findall(r'#### Task (.+?): (.+?)\n\n\*\*Work\*\*:(.*?)\*\*Acceptance Criteria\*\*:(.*?)\*\*Blocked By\*\*:(.*?)\*\*Required Reading\*\*:(.*?)(?=####|\Z)',
                       phase_content, re.DOTALL)
```

### Step 3: Build Dependency Graph

```python
dependency_graph = {}
for task in all_tasks:
    task_id = task['id']
    blocked_by = parse_blocked_by(task['blocked_by'])
    dependency_graph[task_id] = blocked_by
```

### Step 3a: Mandatory Cycle Detection (BLOCKING)

**CRITICAL**: Cycle detection MUST run before any task dispatch. Plans with cycles cannot be executed.

```python
def detect_and_report_cycles(graph):
    """Detect circular dependencies and report full cycle path."""

    visited = set()
    path = []
    path_set = set()
    cycles_found = []

    def dfs(node):
        visited.add(node)
        path.append(node)
        path_set.add(node)

        for neighbor in graph.get(node, []):
            if neighbor in path_set:
                # Found cycle - extract the cycle path
                cycle_start = path.index(neighbor)
                cycle = path[cycle_start:] + [neighbor]
                cycles_found.append(cycle)
            elif neighbor not in visited:
                dfs(neighbor)

        path.pop()
        path_set.remove(node)

    for node in graph:
        if node not in visited:
            dfs(node)

    return cycles_found


def enforce_no_cycles(dependency_graph):
    """MANDATORY: Reject plan if cycles exist."""

    cycles = detect_and_report_cycles(dependency_graph)

    if cycles:
        output("PLAN REJECTED: CIRCULAR DEPENDENCIES DETECTED")
        output("")
        for i, cycle in enumerate(cycles, 1):
            output(f"Cycle {i}: {' -> '.join(cycle)}")
        output("")
        output("Fix the blocked_by fields to remove circular dependencies.")
        output("Each task's dependencies must form a directed acyclic graph (DAG).")

        log_event("plan_rejected",
                  reason="circular_dependencies",
                  cycles=cycles)

        raise PlanValidationError(f"Plan contains {len(cycles)} circular dependencies")

    log_event("cycle_detection_passed", task_count=len(dependency_graph))
    return True
```

**Enforcement Point**:

```python
def load_plan(plan_file):
    """Load and validate plan before execution."""

    # Parse phases and tasks
    phases = extract_phases(plan_file)
    tasks = extract_all_tasks(phases)

    # Build dependency graph
    dependency_graph = build_dependency_graph(tasks)

    # MANDATORY: Reject if cycles exist
    enforce_no_cycles(dependency_graph)  # Raises if cycles found

    # Continue with remaining validation...
    validate_task_ids_unique(tasks)
    validate_blocked_by_references(tasks, dependency_graph)
    validate_acceptance_criteria(tasks)

    return tasks, dependency_graph
```

### Cycle Detection on Dynamic Changes

If tasks are added dynamically (e.g., remediation tasks), re-validate:

```python
def add_task_dynamically(new_task, dependency_graph):
    """Add task and re-validate for cycles."""

    # Add to graph temporarily
    temp_graph = dependency_graph.copy()
    temp_graph[new_task['id']] = parse_blocked_by(new_task['blocked_by'])

    # Check for cycles
    cycles = detect_and_report_cycles(temp_graph)

    if cycles:
        log_event("dynamic_task_rejected",
                  task_id=new_task['id'],
                  reason="would_create_cycle",
                  cycle=cycles[0])
        return False, f"Adding task would create cycle: {' -> '.join(cycles[0])}"

    # Safe to add
    dependency_graph[new_task['id']] = temp_graph[new_task['id']]
    return True, None
```

### Step 4: Initialize State

```python
state = {
    'total_tasks': len(all_tasks),
    'completed_tasks': [],
    'in_progress_tasks': [],
    'pending_audit': [],
    'blocked_tasks': {
        task_id: deps
        for task_id, deps in dependency_graph.items()
        if deps
    },
    'available_tasks': [
        task_id
        for task_id, deps in dependency_graph.items()
        if not deps
    ]
}
```

## Validation Rules

The coordinator must validate the plan before execution:

| Check | Action on Failure |
|-------|-------------------|
| All task IDs unique | Reject plan |
| All blocked_by references exist | Reject plan |
| No circular dependencies | Reject plan |
| All acceptance criteria testable | Warn, ask for clarification |
| At least one task with no blockers | Reject plan (can't start) |
| Required reading files exist | Warn (may be created during execution) |

### Acceptance Criteria Quality Validation

Before dispatching any task, validate that acceptance criteria are testable:

```python
def validate_acceptance_criteria(criteria_list):
    """Validate that all acceptance criteria are testable and specific."""

    issues = []
    INVALID_PATTERNS = [
        (r'should be clean', 'Vague: what makes code "clean"?'),
        (r'appropriate', 'Vague: what is "appropriate"?'),
        (r'properly', 'Vague: what does "properly" mean?'),
        (r'handle.*appropriately', 'Vague: specify exact handling behavior'),
        (r'follow best practices', 'Vague: which practices specifically?'),
        (r'implement.*feature', 'Too general: specify observable behavior'),
        (r'should be fast', 'Not measurable: specify time threshold'),
        (r'should be secure', 'Vague: specify security requirements'),
        (r'good.*error.*handling', 'Vague: specify error responses'),
    ]

    VALID_PATTERNS = [
        r'`[^`]+`\s+exits?\s+\d+',           # Command exits with code
        r'`[^`]+`\s+exists?',                 # File/class/function exists
        r'raises?\s+`[^`]+`',                 # Raises specific exception
        r'returns?\s+`[^`]+`',                # Returns specific type
        r'contains?\s+',                      # Contains specific content
        r'\d+\s+(seconds?|ms|milliseconds?)', # Measurable time
        r'HTTP\s+\d{3}',                      # Specific HTTP status
    ]

    for criterion in criteria_list:
        # Check for invalid patterns
        for pattern, reason in INVALID_PATTERNS:
            if re.search(pattern, criterion, re.IGNORECASE):
                issues.append({
                    'criterion': criterion,
                    'issue': 'Not testable',
                    'reason': reason
                })
                break
        else:
            # Check if any valid pattern matches
            is_valid = any(
                re.search(p, criterion, re.IGNORECASE)
                for p in VALID_PATTERNS
            )
            if not is_valid:
                issues.append({
                    'criterion': criterion,
                    'issue': 'Unclear verification method',
                    'reason': 'Could not identify testable assertion'
                })

    return issues
```

**On validation failure:**
```python
if issues:
    output("ACCEPTANCE CRITERIA VALIDATION ISSUES")
    for issue in issues:
        output(f"  - {issue['criterion'][:50]}...")
        output(f"    Issue: {issue['issue']}")
        output(f"    Reason: {issue['reason']}")

    # Seek divine clarification
    output("SEEKING DIVINE CLARIFICATION")
    output("The following acceptance criteria need clarification:")
    for issue in issues:
        output(f"  - {issue['criterion']}")
    output("Please provide testable versions of these criteria.")
```

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

Use existing pattern from `src/models/product.py`.

**Acceptance Criteria**:
- [ ] `src/models/user.py` exists
- [ ] `User` dataclass has all required fields
- [ ] `uv run pytest tests/unit/test_user_model.py` exits 0
- [ ] `uv run pyright src/models/user.py` exits 0

**Blocked By**: none

**Required Reading**:
- src/models/product.py

---

#### Task 1-1-2: Create UserRepository

**Work**:
Create `UserRepository` class in `src/repositories/user_repository.py` with methods:
- `get_by_username(username: str) -> User | None`
- `create(user: User) -> User`

Follow repository pattern from `src/repositories/product_repository.py`.

**Acceptance Criteria**:
- [ ] `UserRepository` class exists
- [ ] Both methods implemented with type hints
- [ ] `uv run pytest tests/unit/test_user_repository.py` exits 0
- [ ] Integration test with database passes

**Blocked By**: 1-1-1

**Required Reading**:
- src/repositories/product_repository.py
- src/models/user.py

---

### Phase 2: Authentication

#### Task 2-1-1: Create Authenticator

**Work**:
Create `Authenticator` class in `src/auth/authenticator.py` that:
1. Takes `UserRepository` as dependency
2. Implements `authenticate(username, password) -> str` returning JWT
3. Raises `AuthenticationError` on invalid credentials

**Acceptance Criteria**:
- [ ] `Authenticator` class exists with constructor accepting `UserRepository`
- [ ] `authenticate` method returns JWT string on success
- [ ] `authenticate` raises `AuthenticationError` on invalid credentials
- [ ] JWT contains user_id and expiration
- [ ] `uv run pytest tests/unit/test_authenticator.py` exits 0

**Blocked By**: 1-1-2

**Required Reading**:
- src/repositories/user_repository.py
- design/auth-spec.md
```
