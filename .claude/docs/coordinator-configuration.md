# Coordinator Configuration

All configuration values for the Parallel Implementation Coordinator.

---

## Tool Usage

| Tool            | When to Use                                                           |
|-----------------|-----------------------------------------------------------------------|
| Task            | Dispatch agents (developer, auditor, BA, remediation, health auditor) |
| TaskOutput      | Poll background agents, retrieve results                              |
| Read            | Load state file, plan file, event log, reference documents            |
| Write           | Persist state file (use atomic write pattern)                         |
| Bash            | Execute usage script only                                             |
| AskUserQuestion | Divine clarification ONLY - never for routine decisions               |
| TodoWrite       | Track coordinator's own task progress                                 |

---

## Template Variables

Variables use `{{variable}}` syntax. The coordinator expands templates before dispatching agents.

| Variable Type | When Expanded    | Example                           |
|---------------|------------------|-----------------------------------|
| Config values | At prompt load   | `{{ACTIVE_DEVELOPERS}}` → `5`     |
| State values  | At dispatch time | `{{task_id}}` → `1-1-1`           |
| Loops         | At dispatch time | `{{#each VERIFICATION_COMMANDS}}` |
| Conditionals  | At dispatch time | `{{#if recommended_agents}}`      |

---

## Directory Structure

All plan-related files are organized under `{{PLAN_DIR}}`:

```
.claude/surrogate_activities/[plan]/
├── state.json              # Coordinator state persistence
├── event-log.jsonl         # Event store for all operations
├── .trash/                 # Deleted files (recoverable via metadata)
├── .scratch/               # Agent scratch files (temporary work)
└── .artefacts/             # Inter-agent artifact transfer
```

### Core Files

| Variable         | Default Value                                 | Description                                                  |
|------------------|-----------------------------------------------|--------------------------------------------------------------|
| `PLAN_FILE`      | (required)                                    | Implementation plan to execute                               |
| `PLAN_DIR`       | `.claude/surrogate_activities/{{PLAN_NAME}}/` | Base directory for all session artifacts                     |
| `STATE_FILE`     | `{{PLAN_DIR}}state.json`                      | Coordinator state persistence                                |
| `EVENT_LOG_FILE` | `{{PLAN_DIR}}event-log.jsonl`                 | Event store for all coordinator operations and agent results |
| `USAGE_SCRIPT`   | `.claude/scripts/get-claude-usage.py`         | Session usage monitoring                                     |
| `TRASH_DIR`      | `{{PLAN_DIR}}.trash/`                         | Deleted files storage (recoverable)                          |
| `SCRATCH_DIR`    | `{{PLAN_DIR}}.scratch/`                       | Agent scratch files for temporary work                       |
| `ARTEFACTS_DIR`  | `{{PLAN_DIR}}.artefacts/`                     | Inter-agent artifact transfer directory                      |

### Directory Derivation

When no explicit `PLAN_DIR` is provided, it is derived from `PLAN_FILE`:

1. Extract the plan file name (e.g., `COMPREHENSIVE_IMPLEMENTATION_PLAN.md`)
2. Remove the `.md` extension
3. Convert to lowercase kebab-case (e.g., `comprehensive-implementation-plan`)
4. Create path: `.claude/surrogate_activities/{{PLAN_NAME}}/`

**Example:**

```
PLAN_FILE: plans/my-feature-plan.md
PLAN_NAME: my-feature-plan
PLAN_DIR:  .claude/surrogate_activities/my-feature-plan/

Directory structure created:
.claude/surrogate_activities/my-feature-plan/
├── state.json           # Coordinator state
├── event-log.jsonl      # Event history
├── .scratch/            # Temporary agent work
├── .artefacts/          # Inter-agent artifacts
└── .trash/              # Recoverable deletions
```

---

## Thresholds

| Variable                   | Value        | Description                                                        |
|----------------------------|--------------|--------------------------------------------------------------------|
| `CONTEXT_THRESHOLD`        | `10%`        | Trigger auto-compaction when context remaining falls to this level |
| `SESSION_THRESHOLD`        | `10%`        | Trigger session pause when session remaining falls to this level   |
| `RECENT_COMPLETION_WINDOW` | `60 minutes` | Re-audit tasks completed within this window on session start       |

---

## Parallel Execution Limits

| Variable               | Value    | Description                                                                            |
|------------------------|----------|----------------------------------------------------------------------------------------|
| `ACTIVE_DEVELOPERS`    | `5`      | Maximum parallel developer agents                                                      |
| `REMEDIATION_ATTEMPTS` | `10`     | Maximum remediation cycles before workflow failure                                     |
| `TASK_FAILURE_LIMIT`   | `3`      | Maximum audit failures per task before workflow aborts                                 |
| `AGENT_TIMEOUT`        | `900000` | Agent timeout in milliseconds (15 minutes) - tracked internally, not via shell timeout |

---

## Agent Models

Variable: `AGENT_MODELS`

| Agent Type         | Model    | Description                                                                        |
|--------------------|----------|------------------------------------------------------------------------------------|
| `coordinator`      | `opus`   | Orchestrates workflow, manages state, dispatches agents                            |
| `business_analyst` | `sonnet` | Expands underspecified tasks into implementable specifications                     |
| `developer`        | `sonnet` | Implements delegated tasks following language best practices and project standards |
| `auditor`          | `opus`   | Validates completed work with unit, integration, and e2e test verification         |
| `remediation`      | `sonnet` | Fixes infrastructure issues and pre-existing failures                              |
| `health_auditor`   | `haiku`  | Runs verification commands to check codebase health                                |

Valid model values: `opus`, `sonnet`, `haiku`

---

## Environments

Variable: `ENVIRONMENTS`

| Name           | Description                     | How to Execute                                                    |
|----------------|---------------------------------|-------------------------------------------------------------------|
| `Mac`          | Local macOS development machine | Run command directly in shell                                     |
| `Devcontainer` | Linux development container     | Use `mcp__devcontainers__devcontainer_exec` with workspace folder |

When a command specifies no environment, it must pass in ALL defined environments.

---

## Agent Reference Documents

Variable: `AGENT_DOCS`

| Pattern                               | Agent            | Environment | Must Read | Purpose                                            |
|---------------------------------------|------------------|-------------|-----------|----------------------------------------------------|
| `design/rules.md`                     |                  |             | Y         | Coding standards that all modified files must pass |
| `design/architecture.md`              |                  |             |           | System architecture for context                    |
| `ARCHITECTURE.md`                     |                  |             |           | High-level component overview                      |
| `design/patterns/**/*.md`             |                  |             |           | Reusable code patterns and conventions             |
| `design/testing-guide.md`             | developer        |             | Y         | Test writing standards and patterns                |
| `design/api-specs/**/*.md`            | developer        |             |           | API specifications for implementation              |
| `design/audit-checklist.md`           | auditor          |             | Y         | Detailed audit verification steps                  |
| `design/security-checklist.md`        | auditor          |             |           | Security review criteria                           |
| `design/remediation-guide.md`         | remediation      |             | Y         | Common infrastructure fixes                        |
| `design/build-system.md`              | remediation      |             |           | Build system configuration and troubleshooting     |
| `design/task-expansion-guide.md`      | business-analyst |             | Y         | Guidelines for expanding underspecified tasks      |
| `design/acceptance-criteria-guide.md` | business-analyst |             | Y         | Writing testable acceptance criteria               |
| `design/health-checks.md`             | health-auditor   |             | Y         | Health verification procedures                     |

---

## Developer Commands

Variable: `DEVELOPER_COMMANDS`

**Environment column**: Empty = run in ALL environments. Specific value = run only in that environment.
**Exit Code column**: Expected exit code. Empty = default to 0.

| Task              | Environment | Command                     | Exit Code | Purpose                                                                                   |
|-------------------|-------------|-----------------------------|-----------|-------------------------------------------------------------------------------------------|
| Sync Dependencies |             | `uv sync`                   | 0         | Ensure all dependencies are installed and lockfile is up to date                          |
| Fix Lints         |             | `uv run ruff check --fix .` | 0         | Eliminate mechanical corrections that waste developer time on fixes automation can handle |
| Format            |             | `uv run ruff format .`      | 0         | Prevent merge conflicts and readability issues caused by inconsistent formatting          |
| Run Tests         |             | `uv run pytest`             | 0         | Provide evidence that implementation meets requirements before claiming completion        |

---

## Verification Commands

Variable: `VERIFICATION_COMMANDS`

**Environment column**: Empty = must pass in ALL environments. Specific value = run only in that environment.
**Exit Code column**: Expected exit code. Empty = default to 0.

| Check             | Environment | Command                              | Exit Code | Purpose                                                                                      |
|-------------------|-------------|--------------------------------------|-----------|----------------------------------------------------------------------------------------------|
| Type Check        |             | `uv run pyright`                     | 0         | Type errors indicate incorrect assumptions about data flow that cause runtime failures       |
| Unit Tests        |             | `uv run pytest tests/unit -v`        | 0         | Failing unit tests indicate broken functionality that blocks downstream work                 |
| Integration Tests |             | `uv run pytest tests/integration -v` | 0         | Component interaction failures cause production bugs that are expensive to diagnose          |
| E2E Tests         |             | `uv run pytest tests/e2e -v`         | 0         | End-to-end failures reveal broken user workflows that unit tests miss                        |
| Lint Check        |             | `uv run ruff check .`                | 0         | Lint violations indicate potential bugs or non-idiomatic code that causes maintenance issues |
| Format Check      |             | `uv run ruff format --check .`       | 0         | Formatting inconsistencies cause merge conflicts and reduce code readability                 |

---

## MCP Servers

Variable: `MCP_SERVERS`

MCP (Model Context Protocol) servers extend agent capabilities beyond native Claude Code tools.
Each row represents one callable function. Agents may ONLY invoke functions listed in this table.

For interpretation guidance, see: [MCP Servers Guide](mcp-servers.md)

| Server          | Function             | Example                                                                                       | Use When                                                                |
|-----------------|----------------------|-----------------------------------------------------------------------------------------------|-------------------------------------------------------------------------|
| `devcontainers` | `devcontainer_exec`  | `mcp__devcontainers__devcontainer_exec(workspace_folder="/project", command="uv run pytest")` | Running verification commands when Environment specifies "Devcontainer" |
| `devcontainers` | `devcontainer_list`  | `mcp__devcontainers__devcontainer_list()`                                                     | Discovering available devcontainers before execution                    |
| `devcontainers` | `devcontainer_start` | `mcp__devcontainers__devcontainer_start(workspace_folder="/project")`                         | Starting a stopped devcontainer before command execution                |

---

## Related Documentation

- [State Management](state-management.md) - State file format and persistence
- [MCP Servers](mcp-servers.md) - MCP server details
- [Coordinator Execution Model](coordinator-execution-model.md) - Operational rules
- [Coordinator Startup](coordinator-startup.md) - Session initialization
