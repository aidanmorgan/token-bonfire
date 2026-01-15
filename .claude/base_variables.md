# Base Variables

Configuration variables for the whole project, consistent between creating teams to implement plans.

## Directory Structure

All plan-related files are organized under `.claude/surrogate_activities/[plan]/`:

```
.claude/surrogate_activities/[plan]/
├── state.json              # Coordinator state persistence
├── event-log.jsonl         # Event store for all operations
├── .trash/                 # Deleted files (recoverable)
│   └── [uuid]-[original-name]
│       ├── content         # Original file content
│       └── metadata.json   # Recovery metadata
├── .scratch/               # Agent scratch files (temporary work)
└── .artefacts/             # Inter-agent artifact transfer
```

## Core Files

| Variable | Value | Description                                                             |
|----------|-------|-------------------------------------------------------------------------|
| `PLAN_FILE` | *(derived from skill parameter)* | Set by `/fiwb <plan_file>`                                              |
| `PLAN_DIR` | `.claude/surrogate_activities/[plan]/` | Base directory for all plan-related files (derived from plan file name) |
| `STATE_FILE` | `{{PLAN_DIR}}/state.json` | Coordinator state persistence                                           |
| `EVENT_LOG_FILE` | `{{PLAN_DIR}}/event-log.jsonl` | Event store for all coordinator operations and agent results            |
| `USAGE_SCRIPT` | `.claude/scripts/get-claude-usage.py` | Session usage monitoring                                                |
| `TRASH_DIR` | `{{PLAN_DIR}}/.trash/` | Deleted files storage (recoverable via metadata)                        |
| `SCRATCH_DIR` | `{{PLAN_DIR}}/.scratch/` | Agent scratch files for temporary work                                  |
| `ARTEFACTS_DIR` | `{{PLAN_DIR}}/.artefacts/` | Inter-agent artifact transfer directory                                 |

## Directory Derivation

The `[plan]` component is derived from the plan file name:

```python
def derive_plan_directory(plan_file):
    """Derive plan directory from plan file path."""
    # Example: COMPREHENSIVE_IMPLEMENTATION_PLAN.md -> comprehensive-implementation-plan
    basename = os.path.basename(plan_file)
    name_without_ext = os.path.splitext(basename)[0]
    slug = name_without_ext.lower().replace('_', '-')
    return f".claude/surrogate_activities/{slug}/"
```

## Thresholds

| Variable | Value | Description |
|----------|-------|-------------|
| `CONTEXT_THRESHOLD` | `10%` | Trigger auto-compaction at this context level |
| `SESSION_THRESHOLD` | `10%` | Trigger session pause at this session level |
| `RECENT_COMPLETION_WINDOW` | `60 minutes` | Re-audit tasks completed within this window |

## Parallel Execution Limits

| Variable | Value | Description |
|----------|-------|-------------|
| `ACTIVE_DEVELOPERS` | `5` | Maximum parallel developer agents |
| `REMEDIATION_ATTEMPTS` | `10` | Maximum remediation cycles before failure |
| `TASK_FAILURE_LIMIT` | `3` | Maximum audit failures per task before abort |
| `AGENT_TIMEOUT` | `900000` | Agent timeout in milliseconds (15 minutes) - tracked internally |

## Agent Models

| Agent Type | Model    | Description |
|------------|----------|-------------|
| `coordinator` | `opus`   | Orchestrates workflow, manages state |
| `developer` | `sonnet` | Implements tasks, writes code |
| `auditor` | `opus`   | Validates completed work |
| `remediation` | `sonnet` | Fixes infrastructure issues |
| `health_auditor` | `haiku`  | Runs verification commands |

## Environments

| Name | Description | How to Execute |
|------|-------------|----------------|
| `Mac` | Local macOS development machine | Run command directly via Bash tool |

## Agent Reference Documents

| Column | Description |
|--------|-------------|
| Pattern | Glob pattern matching files to provide |
| Agent | Target agent type. Empty means all agents. Valid: `developer`, `auditor`, `remediation` |
| Environment | Target environment from `ENVIRONMENTS`. Empty means all environments. |
| Must Read | If `Y`, agent must read file fully without summarization before starting work. If empty, file path is added to context as reference only. |
| Purpose | Why this document is provided |

| Pattern | Agent       | Environment | Must Read | Purpose                                                                          |
|---------|-------------|-------------|------|----------------------------------------------------------------------------------|
| `design/rules.md` |             | | Y | Python development standards and compliance requirements that all code must follow |
| `design/architecture.md` | | | | System architecture showing component relationships and boundaries               |
| `ARCHITECTURE.md` | | | | High-level component overview and module structure                               |
| `design/testing-guide.md` | developer | | Y | Test writing standards and patterns |

### Developer Commands

| Task | Environment | Command | Purpose |
|------|-------------|---------|---------|
| Sync Dependencies |  | `uv sync` | Ensure all dependencies are installed and lockfile is up to date |
| Fix Lints |  | `uv run ruff check --fix .` | Eliminate mechanical corrections that waste developer time on fixes automation can handle |
| Format |  | `uv run ruff format .` | Prevent merge conflicts and readability issues caused by inconsistent formatting |
| Run Tests |  | `uv run pytest` | Provide evidence that implementation meets requirements before claiming completion |

### Verification Commands

| Check | Environment | Command | Exit Code | Purpose |
|-------|-------------|---------|-----------|---------|
| Type Check |  | `uv run pyright` | 0 | Type errors indicate incorrect assumptions about data flow that cause runtime failures |
| Unit Tests |  | `uv run pytest tests/unit -v` | 0 | Failing unit tests indicate broken functionality that blocks downstream work |
| Integration Tests |  | `uv run pytest tests/integration -v` | 0 | Component interaction failures cause production bugs that are expensive to diagnose |
| E2E Tests |  | `uv run pytest tests/e2e -v` | 0 | End-to-end failures reveal broken user workflows that unit tests miss |
| Lint Check |  | `uv run ruff check .` | 0 | Lint violations indicate potential bugs or non-idiomatic code that causes maintenance issues |
| Format Check |  | `uv run ruff format --check .` | 0 | Formatting inconsistencies cause merge conflicts and reduce code readability |
