# Team Lead Fresh Start

Fresh session initialization procedures when no tasks exist in `TaskList`.

---

## Navigation

- **[Fresh Start](fresh-start.md)** - This file
- [Resume](resume.md) - Resume session procedures
- [Team Lead Configuration](../coordinator-configuration.md) - Configuration values
- [Team Architecture](../team-architecture.md) - Team structure and communication

---

## FRESH START (No Existing Tasks)

**CRITICAL ORDERING**: Expert prompts are created BEFORE teammates are spawned so teammates have the expert list available.

```
Research -> Gap Analysis -> Create Expert Prompts -> Create Tasks -> Spawn Team
```

### Step 1: Derive Plan Directory and Create Structure

Derive `PLAN_NAME` from `PLAN_FILE`:

1. Extract the plan file name (e.g., `COMPREHENSIVE_IMPLEMENTATION_PLAN.md`)
2. Remove the `.md` extension
3. Convert to lowercase kebab-case (e.g., `comprehensive-implementation-plan`)
4. Set `PLAN_DIR` to `.claude/bonfire/{plan_name}/`

Create the directory structure:

```
.claude/bonfire/{{PLAN_NAME}}/
+-- .scratch/
+-- .artefacts/
```

Also ensure the expert prompts directory exists:

```
.claude/experts/{{PLAN_NAME}}/
```

### Step 2: Check Prompt AND Expert Files Existence

Before doing any research or creation, check which files exist.

**Required agent definitions:**

| Teammate         | File Path                          |
|------------------|------------------------------------|
| Developer        | `.claude/agents/developer.md`      |
| Critic           | `.claude/agents/critic.md`         |
| Auditor          | `.claude/agents/auditor.md`        |

**Expert prompts directory:**

```
.claude/experts/{{PLAN_NAME}}/
```

**Decision Logic:**

- If ANY agent definition is missing -> Cannot proceed, create definitions
- If ALL definitions exist AND experts exist -> Use existing, skip to step 8
- If ALL definitions exist BUT no experts -> Run gap analysis, create experts only

### Step 3: Research Best Practices for Technologies

Only if prompts need creation:

Use a `Task` call with `model: opus` and `subagent_type: "general-purpose"` to research best practices for the technologies used in the plan.

The research agent should:

1. Read the plan file to identify technologies
2. Search codebase for existing patterns via `Glob` and `Grep`
3. Read `CLAUDE.md` for project conventions
4. Research each technology via `WebSearch` for best practices, anti-patterns, and security considerations

Store the research output for use in expert creation.

### Step 4: Gap Analysis - Identify Expert Needs

Analyze the plan to identify where default teammates will need expert support.

**When this step runs:**

- Prompts need creation -> Always run
- All prompts exist but no experts -> Run to determine if experts needed

Use a `Task` call with `model: opus` and `subagent_type: "general-purpose"` to analyze the plan for:

1. **Expertise Gaps**: What specialized knowledge do tasks require?
2. **Decision Points**: Where will teammates face choices needing expertise?
3. **Verification Gaps**: What cannot be verified correctly without domain knowledge?
4. **Risk Areas**: Where could mistakes have serious consequences?

If no gaps are identified, output "NO EXPERTS REQUIRED" and skip to step 6.

### Step 5: Create Expert Prompts to Fill Gaps

Only if gap analysis recommends experts.

For each recommended expert, create a prompt file at `.claude/experts/{{PLAN_NAME}}/[expert-name].md`.

Each expert prompt should include:
- Identity: Who they are, why they exist
- Plan context: This specific plan's challenges
- Expertise: Best practices, pitfalls, decision guidance
- Boundaries: What they cannot do
- Signal format: How they communicate results via mailbox

### Step 6: Plan Discovery and Task Creation

**CRITICAL**: Tasks MUST be created BEFORE spawning the team so teammates have work available immediately.

Read `{{PLAN_FILE}}`, parse tasks, and create them via `TaskCreate`:

For each task in the plan:

```
TaskCreate({
    title: "Task <task-id>: <title>",
    description: "<work description>",
    status: "pending",
    blockedBy: [dependency task IDs]
})
```

### Step 7: Spawn the Team

Spawn all named teammates at startup using `Task` with `run_in_background: true`:

```
# Developers (NUM_DEVELOPERS implementers)
for i in range(1, NUM_DEVELOPERS + 1):
    Task({ team_name: "bonfire", name: f"dev-{i}", subagent_type: "developer",
           prompt: "<config tables>", run_in_background: true })

# Static roles use native agent definitions (subagent_type = agent name)
Task({ team_name: "bonfire", name: "critic", subagent_type: "critic",
       prompt: "<config tables>", run_in_background: true })

Task({ team_name: "bonfire", name: "auditor", subagent_type: "auditor",
       prompt: "<config tables>", run_in_background: true })

Task({ team_name: "bonfire", name: "business-analyst", subagent_type: "business-analyst",
       prompt: "<config tables>", run_in_background: true })

Task({ team_name: "bonfire", name: "remediation", subagent_type: "remediation",
       prompt: "<config tables>", run_in_background: true })

Task({ team_name: "bonfire", name: "health-auditor", subagent_type: "health-auditor",
       prompt: "<config tables>", run_in_background: true })

# Expert advisors use inline prompts (dynamically generated per plan)
for each expert in gap_analysis.recommended_experts:
    Task({ team_name: "bonfire", name: expert.name, subagent_type: "general-purpose",
           prompt: Read(f".claude/experts/{{PLAN_NAME}}/{expert.name}.md") })
```

All teammates are now persistent and running. They self-organize by reading their mailbox.

### Step 8: Task Quality Assessment

Assess each task for implementability per [Task Quality](../task-quality.md).

Route `NEEDS_EXPANSION` tasks to the `business-analyst` teammate via mailbox:

```
TeammateTool({ operation: "write", to: "business-analyst",
               content: "Expand task <task-id>: <task description>" })
```

Use `AskUserQuestion` for `NEEDS_CLARIFICATION` tasks.

Only `IMPLEMENTABLE` tasks are ready for developer assignment. Wait for all business analyst expansions to complete before routing to developers.

### Step 9: Proceed to Execution Loop

Begin the main loop: developers claim tasks, monitor mailbox for results, route through Developer -> Critic -> Ripple -> Auditor pipeline.

---

## Related Documentation

- [Resume](resume.md) - Resume session procedures
- [Team Lead Configuration](../coordinator-configuration.md) - Configuration values
- [Task Quality](../task-quality.md) - Task assessment
- [Team Architecture](../team-architecture.md) - Team structure and communication
