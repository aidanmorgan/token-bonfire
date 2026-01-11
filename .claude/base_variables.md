# Base Variables

Configuration variables for the whole project, consistent between creating teams to implement plans.

## Core Files

| Variable | Value | Description |
|----------|-------|-------------|
| `PLAN_FILE` | *(derived from skill parameter)* | Set by `/fuck-it-we-ball <plan_file>` |
| `STATE_FILE` | `.claude/surrogate_activities/[stub]/state.json` | Derived from plan file name (e.g., `comprehensive-implementation-plan-state.json`) |
| `EVENT_LOG_FILE` | `.claude/surrogate_activities/[stub]/event-log.jsonl` | Derived from plan file name (e.g., `comprehensive-implementation-plan-event-log.jsonl`) |
| `USAGE_SCRIPT` | `.claude/scripts/get-claude-usage.py` | Session usage monitoring |
| `WORKING_DIR` | `.tmp` | Directory for agent temporary files |

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
| `design/rules.md` |             | | Y | Rust development standards and compliance requirements that all code must follow |
| `design/architecture.md` | | | | System architecture showing component relationships and boundaries               |
| `design/ARCHITECTURE.md` | | | | High-level component overview and module structure                               |

### Developer Commands

| Task | Environment | Command | Purpose |
|------|-------------|---------|---------|
| Build Rust |  | `RUSTFLAGS="-D warnings" cargo build --all` | Catch compilation errors and warnings early before they compound into harder-to-debug problems |
| Fix Rust Lints |  | `cargo clippy --fix --all --all-targets --all-features` | Eliminate mechanical corrections that waste developer time on fixes automation can handle |
| Format Rust |  | `cargo fmt --all` | Prevent merge conflicts and readability issues caused by inconsistent formatting |
| Run Rust Tests |  | `cargo test --all --all-features` | Provide evidence that implementation meets requirements before claiming completion |
| Build C |  | `cmake -DCMAKE_C_FLAGS="-Wall -Wextra -Werror -pedantic" .. && make` | Catch C compilation errors and warnings before they propagate to dependent code |
| Format C |  | `clang-format -i src/**/*.c src/**/*.h` | Prevent merge conflicts and readability issues in C code |
| Fix Python Lints |  | `ruff check --fix scripts/ tests/` | Eliminate Python lint issues that waste reviewer time on mechanical corrections |
| Format Python |  | `ruff format scripts/ tests/` | Prevent merge conflicts in Python scripts and test files |

### Verification Commands

| Check | Environment | Command | Exit Code | Purpose |
|-------|-------------|---------|-----------|---------|
| Rust Build |  | `RUSTFLAGS="-D warnings" cargo build --all` | 0 | Compilation errors or warnings prevent deployment and indicate incomplete work |
| Rust Clippy |  | `cargo clippy --all --all-targets --all-features -- -D warnings -D clippy::all -D clippy::pedantic` | 0 | Clippy warnings indicate potential bugs or non-idiomatic code that causes maintenance issues |
| Rust Format |  | `cargo fmt --all -- --check` | 0 | Formatting inconsistencies cause merge conflicts and reduce code readability |
| Rust Tests |  | `cargo test --all --all-features` | 0 | Failing tests indicate broken functionality that blocks downstream work |
| C Build |  | `cmake -DCMAKE_C_FLAGS="-Wall -Wextra -Werror -pedantic" .. && make` | 0 | C compilation errors or warnings indicate incomplete or incorrect implementation |
| C Clang-Tidy |  | `clang-tidy -p build --warnings-as-errors=* src/**/*.c` | 0 | Static analysis catches bugs and security issues before they reach production |
| C Format |  | `clang-format --dry-run --Werror src/**/*.c src/**/*.h` | 0 | Formatting inconsistencies in C code cause merge conflicts and readability issues |
| Python Ruff |  | `ruff check scripts/ tests/` | 0 | Lint violations indicate potential bugs that cause test or script failures |
| Python Format |  | `ruff format --check scripts/ tests/` | 0 | Formatting inconsistencies in Python cause merge conflicts |
| Shell Check |  | `shellcheck -e SC1091 scripts/*.sh` | 0 | Shell script issues cause silent failures in CI/CD pipelines |
| TOML Check |  | `taplo check Cargo.toml */Cargo.toml` | 0 | Invalid TOML breaks cargo and prevents builds |
