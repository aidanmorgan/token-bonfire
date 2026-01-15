---
name: fiwb
description: Generate an orchestrator prompt from a plan file and assume the coordinator role. Creates plan directory with state and event log files.
---

# FIWB (Fuck It We Ball)

Generate an orchestrator prompt from the template and base variables, then assume the coordinator role to execute the plan.

## Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `plan_file` | Yes | Path to the implementation plan file |

The plan slug is automatically derived from the plan file name:
- `COMPREHENSIVE_IMPLEMENTATION_PLAN.md` → `comprehensive-implementation-plan`
- `AuthFeaturePlan.md` → `auth-feature-plan`
- `my-feature-plan.md` → `my-feature-plan`

## Invocation

```
/fiwb COMPREHENSIVE_IMPLEMENTATION_PLAN.md
```

## Workflow

### Step 1: Generate Orchestrator Prompt

Run the generation script:

```bash
python .claude/scripts/generate-orchestrator.py "$plan_file"
```

This script:
1. Derives the plan slug from the plan file name
2. Reads `.claude/base_variables.md` for configuration
3. Reads `.claude/prompts/industrial_society_and_its_prompts.md` template
4. Replaces all variable tables with values from base_variables.md
5. Sets derived variables:
   - `PLAN_FILE` = `$plan_file`
   - `STATE_FILE` = `.claude/plans/<slug>/coordination-state.json`
   - `EVENT_LOG_FILE` = `.claude/plans/<slug>/event-log.jsonl`
6. Creates `.claude/plans/<slug>/` directory
7. Writes processed template to `.claude/plans/<slug>.md`

### Step 2: Read Generated Orchestrator

Read the generated file at `.claude/plans/<slug>.md`.

### Step 3: Assume Orchestrator Role

Output:
```
ORCHESTRATOR GENERATED

Plan: $plan_file
Slug: <derived-slug>
State: .claude/plans/<slug>/coordination-state.json
Events: .claude/plans/<slug>/event-log.jsonl
Prompt: .claude/plans/<slug>.md

ASSUMING ORCHESTRATOR ROLE...
```

The generated prompt becomes your operating instructions. Execute the "On Session Start" procedure from the orchestrator prompt:
1. Validate all agent definitions exist (create missing ones using Creation Prompts)
2. Load plan file and discover tasks
3. Build dependency graph
4. Initialize state file
5. Dispatch developers to fill all actor slots

Continue as orchestrator until:
- Plan completion (all tasks complete)
- Context exhaustion (trigger compaction)
- Session limit (trigger pause)

## Error Handling

| Error | Action |
|-------|--------|
| Script execution fails | Output error message and stop |
| base_variables.md missing | Output: "Create .claude/base_variables.md first" |
| Template missing | Output: "Template not found at .claude/prompts/industrial_society_and_its_prompts.md" |
| Plan file missing | Warn but continue. Orchestrator fails on start if file missing at runtime. |

## Files Created

| Path | Description |
|------|-------------|
| `.claude/plans/<slug>.md` | Processed orchestrator prompt |
| `.claude/plans/<slug>/` | Directory for state and event files |
| `.claude/plans/<slug>/coordination-state.json` | Created by orchestrator during execution |
| `.claude/plans/<slug>/event-log.jsonl` | Created by orchestrator during execution |

## Prerequisites

| Requirement | Location |
|-------------|----------|
| Base variables | `.claude/base_variables.md` |
| Prompt template | `.claude/prompts/industrial_society_and_its_prompts.md` |
| Generation script | `.claude/scripts/generate-orchestrator.py` |
| Plan file | `$plan_file` |
