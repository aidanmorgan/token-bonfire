# FIWB - Parallel Implementation Coordinator

Launch the parallel implementation coordinator to execute a plan file.

## Usage

```
/fiwb <plan_file>
```

## Arguments

- `$ARGUMENTS`: Path to the implementation plan file (e.g., `COMPREHENSIVE_IMPLEMENTATION_PLAN.md`)

## Instructions

Display "FUCK IT, WE BALL!" to the user.

Invoke the fiwb skill to:

1. Generate an orchestrator prompt from the specified plan file
2. Create the plan directory with state and event log files
3. Assume the coordinator role and begin parallel execution

**Execute this skill:**

Use the Skill tool with:

- skill: "fiwb"
- args: "$ARGUMENTS"

The coordinator will:

- Parse the plan file to identify all tasks
- Create required agent files in `.claude/agents/`
- Initialize state tracking in `.claude/surrogate_activities/[plan]/`
- Begin dispatching parallel agents
- Manage the audit loop until all tasks complete

## Documentation

All documentation is accessible from the index:

- **[Documentation Index](.claude/docs/index.md)** - Navigation hub for all docs

Key references for the orchestrator:

| Document                                                        | Purpose                              |
|-----------------------------------------------------------------|--------------------------------------|
| [task-delivery-loop.md](.claude/docs/task-delivery-loop.md)     | Core dispatch → review → audit cycle |
| [signal-specification.md](.claude/docs/signal-specification.md) | All signal formats                   |
| [state-management.md](.claude/docs/state-management.md)         | Coordinator state tracking           |
| [agent-definitions.md](.claude/docs/agent-definitions.md)       | Agent types and creation             |

## Example

```
/fiwb COMPREHENSIVE_IMPLEMENTATION_PLAN.md
```

This launches the coordinator to execute all tasks in the plan using parallel agents.
