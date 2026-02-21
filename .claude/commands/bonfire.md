# Bonfire - Parallel Implementation Team Lead

Launch the parallel implementation team lead to execute a plan file.

## Usage

```
/bonfire <plan_file>
```

## Arguments

- `$ARGUMENTS`: Path to the implementation plan file (e.g., `COMPREHENSIVE_IMPLEMENTATION_PLAN.md`)

## Instructions

Invoke the bonfire skill to:

1. Bootstrap the plan (parse tasks, generate plan slug)
2. Research technologies and generate named expert agents
3. Spawn all named teammates and begin parallel execution

**Execute this skill:**

Use the Skill tool with:

- skill: "bonfire"
- args: "$ARGUMENTS"

The team lead will:

- Parse the plan file to identify all tasks via `generate-orchestrator.py`
- Generate expert agents and persist to `.claude/experts/<plan_slug>/`
- Create tasks via `TaskCreate` in the shared task list
- Spawn all named teammates (experts, critic, auditor, business-analyst, remediation, health-auditor)
- Monitor mailbox and route work through the staged pipeline until all tasks complete

## Documentation

All documentation is accessible from the index:

- **[Documentation Index](.claude/docs/index.md)** - Navigation hub for all docs

Key references for the team lead:

| Document                                                        | Purpose                                   |
|-----------------------------------------------------------------|-------------------------------------------|
| [task-delivery-loop.md](.claude/docs/task-delivery-loop.md)     | Core dispatch -> review -> audit cycle    |
| [signals/index.md](.claude/docs/signals/index.md)               | All signal formats (mailbox messages)     |
| [state/index.md](.claude/docs/state/index.md)                   | Task state via native TaskList/TaskUpdate |
| [agent-definitions.md](.claude/docs/agent-definitions.md)       | Teammate types and responsibilities       |

## Example

```
/bonfire COMPREHENSIVE_IMPLEMENTATION_PLAN.md
```

This launches the team lead to execute all tasks in the plan using named teammates.
