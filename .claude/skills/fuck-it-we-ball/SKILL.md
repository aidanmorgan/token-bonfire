---
name: fuck-it-we-ball
description: Generate a parallel implementation coordinator prompt from base variables and a plan file. Use when starting a new parallel implementation workflow.
---

# Fuck It We Ball

Generates a coordinator prompt from base variables and a plan file, then assumes the orchestrator role.

## Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `plan_file` | Yes | Plan file path (e.g., `COMPREHENSIVE_IMPLEMENTATION_PLAN.md`) |

## Invocation

```
/fuck-it-we-ball COMPREHENSIVE_IMPLEMENTATION_PLAN.md
```

## Workflow

### Step 1: Read Inputs

Read `.claude/base_variables.md` and `.claude/prompts/industrial_society_and_its_prompts.md`.

### Step 2: Derive Plan-Specific Variables

From the `plan_file` parameter:

| Variable | Derivation | Example |
|----------|------------|---------|
| `PLAN_FILE` | *(derived from skill parameter)* | Set by `/fuck-it-we-ball <plan_file>` |
| `STATE_FILE` | `.claude/surrogate_activities/[stub]/state.json` | Derived from plan file name (e.g., `comprehensive-implementation-plan-state.json`) |
| `EVENT_LOG_FILE` | `.claude/surrogate_activities/[stub]/event-log.jsonl` | Derived from plan file name (e.g., `comprehensive-implementation-plan-event-log.jsonl`) |

These override base_variables.md values for PLAN_FILE, STATE_FILE, and EVENT_LOG_FILE.

### Step 3: Generate Orchestrator Prompt

Substitute variables into the template:

| Pattern | Replacement |
|---------|-------------|
| `{{PLAN_FILE}}` | Derived plan file path |
| `{{STATE_FILE}}` | Derived state file path |
| `{{EVENT_LOG_FILE}}` | Derived event log path |
| `{{VARIABLE_NAME}}` | Value from base_variables.md |
| `{{#each TABLE}}...{{/each}}` | Expand for each table row |
| `{{this.column}}` | Column value in current row |
| `[Include: Name]` | Inline the referenced definition |

### Step 4: Write Orchestrator File

```
mkdir -p .claude/surrogate_activities/[stub]
```

Write to `.claude/surrogate_activities/[stub]/orchestrator.md`.

### Step 5: Assume Orchestrator Role

Output:
```
ORCHESTRATOR GENERATED

Plan: [plan_file]
State: .claude/surrogate_activities/[stub]/state.json
Events: .claude/surrogate_activities/[stub]/event-log.jsonl
Output: .claude/surrogate_activities/[stub]/orchestrator.md

ASSUMING ORCHESTRATOR ROLE...
```

Read the generated orchestrator file. The generated prompt becomes your operating instructions. Execute the "On Session Start" procedure: load plan, discover tasks and dependencies, initialize state, dispatch developers.

Continue as orchestrator until plan completion, context exhaustion, or session limit.

## Error Handling

| Error | Action |
|-------|--------|
| base_variables.md missing | Stop. Output: "Create .claude/base_variables.md first." |
| Template missing | Stop. Output: "Template not found at .claude/prompts/industrial_society_and_its_prompts.md" |
| Plan file missing | Warn and continue. Orchestrator fails on start if file missing at runtime. |
| Undefined variable | Stop. List undefined variables. |

## Prerequisites

| Requirement | Location |
|-------------|----------|
| Base variables | `.claude/base_variables.md` |
| Prompt template | `.claude/prompts/industrial_society_and_its_prompts.md` |
| Plan file | Parameter value |
