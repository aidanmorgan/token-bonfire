# Base Variables

Configuration variables for the whole project, consistent between creating teams to implement plans.

## Team Configuration

| Variable              | Value    | Description                                                                 |
|-----------------------|----------|-----------------------------------------------------------------------------|
| `NUM_DEVELOPERS`      | `5`      | Number of parallel developer agents that write code                        |
| `DEVELOPER_MODEL`     | `sonnet` | Model for developer agents                                                 |
| `MAX_EXPERTS`         | `3`      | Maximum number of advisory expert agents (actual count determined by plan)  |
| `EXPERT_MODEL`        | `sonnet` | Model for expert advisor and review pipeline agents                        |
| `AUDITOR_MODEL`       | `opus`   | Model for auditor teammate                                                 |
| `TASK_FAILURE_LIMIT`  | `3`      | Maximum review/audit failures per task before escalating to user            |
| `REMEDIATION_ATTEMPTS`| `3`      | Maximum remediation cycles before escalating infrastructure issues to user  |

## Environments

| Name  | Description                     | How to Execute                     |
|-------|---------------------------------|------------------------------------|
| `Mac` | Local macOS development machine | Run command directly via Bash tool |

## Agent Reference Documents

| Column      | Description                                                                                                                               |
|-------------|-------------------------------------------------------------------------------------------------------------------------------------------|
| Pattern     | Glob pattern matching files to provide                                                                                                    |
| Agent       | Target agent type. Empty means all agents. Valid: `developer`, `expert`, `critic`, `auditor`                                              |
| Environment | Target environment from Environments table. Empty means all environments.                                                                 |
| Must Read   | If `Y`, agent must read file fully without summarization before starting work. If empty, file path is added to context as reference only. |
| Purpose     | Why this document is provided                                                                                                             |

| Pattern                   | Agent      | Environment | Must Read | Purpose                                                                            |
|---------------------------|------------|-------------|-----------|------------------------------------------------------------------------------------|
| `design/rules.md`         |            |             | Y         | Python development standards and compliance requirements that all code must follow |
| `design/architecture.md`  |            |             |           | System architecture showing component relationships and boundaries                 |
| `ARCHITECTURE.md`         |            |             |           | High-level component overview and module structure                                 |
| `design/testing-guide.md` | developer  |             | Y         | Test writing standards and patterns                                                |

### Developer Commands

Commands developer agents run after implementing a task (self-verification before signaling ready-for-review).

| Task              | Environment | Command                     | Purpose                                                                                   |
|-------------------|-------------|-----------------------------|-------------------------------------------------------------------------------------------|
| Sync Dependencies |             | `uv sync`                   | Ensure all dependencies are installed and lockfile is up to date                          |
| Fix Lints         |             | `uv run ruff check --fix .` | Eliminate mechanical corrections that waste developer time on fixes automation can handle |
| Format            |             | `uv run ruff format .`      | Prevent merge conflicts and readability issues caused by inconsistent formatting          |
| Run Tests         |             | `uv run pytest`             | Provide evidence that implementation meets requirements before claiming completion        |

### Verification Commands

Commands the auditor runs to independently verify task completion.

| Check             | Environment | Command                              | Exit Code | Purpose                                                                                      |
|-------------------|-------------|--------------------------------------|-----------|----------------------------------------------------------------------------------------------|
| Type Check        |             | `uv run pyright`                     | 0         | Type errors indicate incorrect assumptions about data flow that cause runtime failures       |
| Unit Tests        |             | `uv run pytest tests/unit -v`        | 0         | Failing unit tests indicate broken functionality that blocks downstream work                 |
| Integration Tests |             | `uv run pytest tests/integration -v` | 0         | Component interaction failures cause production bugs that are expensive to diagnose          |
| E2E Tests         |             | `uv run pytest tests/e2e -v`        | 0         | End-to-end failures reveal broken user workflows that unit tests miss                        |
| Lint Check        |             | `uv run ruff check .`                | 0         | Lint violations indicate potential bugs or non-idiomatic code that causes maintenance issues |
| Format Check      |             | `uv run ruff format --check .`       | 0         | Formatting inconsistencies cause merge conflicts and reduce code readability                 |

## MCP Servers

Variable: `MCP_SERVERS`

MCP (Model Context Protocol) servers extend agent capabilities with specialized tools.
Each row represents one callable function. Agents receive this table and may ONLY invoke functions listed here.

| Server          | Function             | Example                                                                                       | Use When                                                                |
|-----------------|----------------------|-----------------------------------------------------------------------------------------------|-------------------------------------------------------------------------|
| `devcontainers` | `devcontainer_exec`  | `mcp__devcontainers__devcontainer_exec(workspace_folder="/project", command="uv run pytest")` | Running verification commands when Environment specifies "Devcontainer" |
| `devcontainers` | `devcontainer_list`  | `mcp__devcontainers__devcontainer_list()`                                                     | Discovering available devcontainers before execution                    |
| `devcontainers` | `devcontainer_start` | `mcp__devcontainers__devcontainer_start(workspace_folder="/project")`                         | Starting a stopped devcontainer before command execution                |
