# Coordinator Fresh Start

Fresh session initialization procedures when no state file exists.

---

## Navigation

- [Startup Overview](startup-overview.md) - Overview and decision logic
- **[Fresh Start](fresh-start.md)** - This file
- [Resume](resume.md) - Resume session procedures
- [Coordinator Configuration](../coordinator-configuration.md) - Configuration values
- [State Management](../state-management.md) - State tracking

---

## FRESH START (No State File)

**CRITICAL ORDERING**: Experts are created BEFORE agents so agents have the expert list embedded.

```
Research → Gap Analysis → Create Experts → Create Agents (with expert list)
```

### Step 1: Derive Plan Directory and Create Structure

```python
# Derive PLAN_NAME from PLAN_FILE
plan_file = "{{PLAN_FILE}}"
plan_name = os.path.splitext(os.path.basename(plan_file))[0].lower().replace("_", "-")

# Set PLAN_DIR
PLAN_DIR = f".claude/bonfire/{plan_name}/"

# Create directory structure
os.makedirs(f"{PLAN_DIR}.scratch", exist_ok=True)
os.makedirs(f"{PLAN_DIR}.artefacts", exist_ok=True)
os.makedirs(f"{PLAN_DIR}.trash", exist_ok=True)
os.makedirs(".claude/agents/experts", exist_ok=True)
```

This creates:

```
.claude/bonfire/{{PLAN_NAME}}/
├── .scratch/
├── .artefacts/
└── .trash/
```

### Step 2: Generate Session ID

Create a new UUID to identify this session. All events logged during this session will include this ID.

```json
{
  "session_id": "<new UUID>",
  "session_started_at": "<current ISO-8601 timestamp>",
  "previous_session_id": null,
  "session_resume_count": 0
}
```

### Step 3: Check Agent AND Expert Files Existence

Before doing any research or creation, check which files exist.

**Required agents:**

| Agent            | File Path                            |
|------------------|--------------------------------------|
| Developer        | `.claude/agents/developer.md`        |
| Auditor          | `.claude/agents/auditor.md`          |
| Business Analyst | `.claude/agents/business-analyst.md` |
| Remediation      | `.claude/agents/remediation.md`      |
| Health Auditor   | `.claude/agents/health-auditor.md`   |
| Critic           | `.claude/agents/critic.md`           |

```python
REQUIRED_AGENTS = [
    ("developer", ".claude/agents/developer.md"),
    ("auditor", ".claude/agents/auditor.md"),
    ("business-analyst", ".claude/agents/business-analyst.md"),
    ("remediation", ".claude/agents/remediation.md"),
    ("health-auditor", ".claude/agents/health-auditor.md"),
    ("critic", ".claude/agents/critic.md"),
]

missing_agents = []
existing_agents = []

for name, path in REQUIRED_AGENTS:
    if os.path.exists(path):
        existing_agents.append(name)
    else:
        missing_agents.append(name)

# Check experts
experts_dir = ".claude/agents/experts/"
existing_experts = []
if os.path.exists(experts_dir):
    existing_experts = [f[:-3] for f in os.listdir(experts_dir) if f.endswith('.md')]

# Decision logic
needs_full_creation = len(missing_agents) > 0  # Any agent missing = regenerate ALL
```

**Decision Logic:**

- If ANY agent is missing → Regenerate ALL (research, experts, agents)
- If ALL agents exist AND experts exist → Use existing, skip to step 9
- If ALL agents exist BUT no experts → Run gap analysis, create experts only

**Rationale:** Agents are created with plan-specific best practices AND expert list embedded. If any agent is
missing, we need to regenerate all to ensure the expert list is properly embedded.

Log the check result:

```json
{
  "event": "existence_check",
  "existing_agents": ["developer", "auditor", ...],
  "missing_agents": ["critic"],
  "existing_experts": ["crypto-expert"],
  "decision": "regenerate_all" | "create_experts_only" | "use_existing"
}
```

**IF all agents AND experts exist:** Skip to step 9 (Plan Discovery).
**IF all agents exist but no experts:** Skip to step 5 (Gap Analysis).
**IF any agent missing:** Continue to step 4 (Research).

### Step 4: Research Best Practices for Technologies

Only if `needs_full_creation`:

```
Task tool parameters:
  model: opus
  subagent_type: "general-purpose"
  prompt: |
    Research best practices for the technologies used in this implementation plan.

    PLAN: {{PLAN_FILE}}

    STEP 1: Identify Technologies
    - Read the plan file
    - Glob("**/*.{py,rs,ts,js,go,c,cpp}") to find source files
    - Read("CLAUDE.md") for project conventions
    - Document: languages, frameworks, libraries, build tools

    STEP 2: Research Each Technology (use WebSearch)
    - "[language] best practices 2026" (use current year)
    - "[language] code review checklist"
    - "[framework] anti-patterns"
    - "[language] common mistakes and pitfalls"
    - "[language] security vulnerabilities OWASP"

    STEP 3: Output Summary
    BEST PRACTICES RESEARCH

    Languages: [list]
    Frameworks: [list]

    [LANGUAGE 1] Best Practices:
    - [Practice]: [Why it matters]
    - [Anti-pattern]: [Why to avoid]

    [FRAMEWORK 1] Patterns:
    - [Pattern]: [When to use]
    - [Anti-pattern]: [Why to avoid]

    Project-Specific Conventions:
    - [From CLAUDE.md]

    Security Considerations:
    - [Vulnerability type]: [What to check]
    - [OWASP category]: [Prevention approach]
```

Store the research output in state as `best_practices_research`.

### Step 5: Gap Analysis - Identify Expert Needs

Analyze the plan to identify where default agents will need expert support.

**When this step runs:**

- needs_full_creation = true → Always run
- All agents exist but no experts → Run to determine if experts needed

**Delete existing experts if regenerating:**

```python
if needs_full_creation:
    experts_dir = ".claude/agents/experts/"
    if os.path.exists(experts_dir):
        for expert_file in os.listdir(experts_dir):
            if expert_file.endswith('.md'):
                os.remove(os.path.join(experts_dir, expert_file))
                log_event("expert_deleted", file=expert_file, reason="full_regeneration")
```

**Run gap analysis:**

```
Task tool parameters:
  model: opus
  subagent_type: "general-purpose"
  prompt: |
    Analyze this implementation plan to identify where default agents will need expert support.

    PLAN: {{PLAN_FILE}}
    BEST PRACTICES RESEARCH: {{best_practices_research}}

    DEFAULT AGENT LIMITATIONS:

    Developer: General implementation, follows patterns, writes tests
      - May not know domain-specific best practices
      - Cannot make expert judgment calls on trade-offs

    Critic: Code quality review, identifies issues, provides feedback
      - May not recognize domain-specific quality issues
      - Cannot judge domain-specific correctness

    Auditor: Verifies acceptance criteria, runs tests
      - May not recognize domain-specific quality issues
      - Cannot judge correctness in specialized areas

    ANALYZE THE PLAN FOR:

    1. **Expertise Gaps**: What specialized knowledge do tasks require?
    2. **Decision Points**: Where will agents face choices needing expertise?
    3. **Verification Gaps**: What can't agents verify correctly alone?
    4. **Risk Areas**: Where could mistakes have serious consequences?

    OUTPUT FORMAT:
    GAP ANALYSIS: [Plan Name]

    IDENTIFIED GAPS:

    Gap 1: [Name]
    - Affected Tasks: [task IDs]
    - Default Agent Limitation: [which agent, what they can't do]
    - Expertise Required: [specific knowledge needed]
    - Risk if Unsupported: [consequences]

    RECOMMENDED EXPERTS:

    1. [Expert Name]
       - Fills Gap: [which gap]
       - Supports: [Developer, Auditor, etc.]
       - Expertise Focus: [specific to plan]
       - Delegation Triggers: [when to ask]

    If NO gaps are identified that require experts, output:
    GAP ANALYSIS: [Plan Name]
    NO EXPERTS REQUIRED - Default agents can handle all tasks in this plan.
```

Store the gap analysis in state as `gap_analysis`.

### Step 6: Create Experts to Fill Gaps

Only if gap analysis recommends experts:

**Skip if:**

- Gap analysis returned "NO EXPERTS REQUIRED"
- All recommended experts already exist

For each expert recommended in gap analysis, create the expert agent.

See: `.claude/docs/agent-creation/expert-creation.md` for complete expert creation prompts.

```
For EACH expert in gap_analysis.recommended_experts:

Task tool parameters:
  model: opus
  subagent_type: "developer"
  prompt: |
    Create an expert agent for the Token Bonfire orchestration system.

    **REQUIRED**: Follow guidelines in .claude/docs/agent-creation/prompt-engineering-guide.md

    CONTEXT:
    Plan: {{PLAN_FILE}}
    Gap Being Filled: [from gap analysis]
    Default Agents This Expert Supports: [from gap analysis]
    Affected Tasks: [from gap analysis]

    RESEARCH (MANDATORY):
    1. Read affected tasks from plan
    2. Search codebase for existing patterns: Glob, Grep
    3. Research best practices: WebSearch("[expertise] best practices 2025")

    Write expert to: .claude/agents/experts/[expert-name].md

    Include:
    - <expert_identity>: Who they are, why they exist
    - <plan_context>: This specific plan's challenges
    - <expertise>: Best practices, pitfalls, decision guidance
    - <boundaries>: CANNOT delegate
    - <signal_format>: EXPERT_ADVICE or EXPERT_UNSUCCESSFUL
```

Verify each expert file exists at `.claude/agents/experts/[name].md`. Log event: `expert_created`

### Step 7: Create Agent Files

Only if `needs_full_creation`:

Now create the default agent files WITH the expert list embedded.

**CRITICAL**: Agents are created AFTER experts so the expert list can be embedded.

For each agent type, use the corresponding creation prompt:

| Agent            | Creation Prompt                                   |
|------------------|---------------------------------------------------|
| Developer        | `.claude/docs/agent-creation/developer.md`        |
| Critic           | `.claude/docs/agent-creation/critic.md`           |
| Auditor          | `.claude/docs/agent-creation/auditor.md`          |
| Business Analyst | `.claude/docs/agent-creation/business-analyst.md` |
| Remediation      | `.claude/docs/agent-creation/remediation.md`      |
| Health Auditor   | `.claude/docs/agent-creation/health-auditor.md`   |

```
For EACH agent in [developer, critic, auditor, business-analyst, remediation, health-auditor]:

Task tool parameters:
  model: opus
  subagent_type: "developer"
  prompt: |
    Create an agent definition for the Token Bonfire orchestration system.

    **REQUIRED**: Read and follow .claude/docs/agent-creation/{{agent-type}}.md

    INPUTS TO PROVIDE TO THE CREATION PROMPT:

    BEST_PRACTICES_RESEARCH:
    {{best_practices_research}}

    SIGNAL_SPECIFICATION:
    [Read from .claude/docs/signal-specification.md]

    DELEGATION_PROTOCOL:
    [Read from .claude/docs/expert-delegation.md]

    AVAILABLE_EXPERTS:
    {{#each available_experts}}
    | {{name}} | {{expertise}} | {{delegation_triggers}} |
    {{/each}}

    ENVIRONMENTS:
    {{ENVIRONMENTS}}

    VERIFICATION_COMMANDS:
    {{VERIFICATION_COMMANDS}}

    The creation prompt is a META-PROMPT that instructs you to write the actual
    agent file. Follow its instructions completely.

    Output file: .claude/agents/{{agent-type}}.md
```

Verify each agent file exists. Log event: `agent_definition_created` for each.

### Step 8: Register Experts with Default Agents

Update state so default agents know available experts.

```json
{
  "available_experts": [
    {
      "name": "crypto-expert",
      "expertise": "Cryptographic implementation for this plan",
      "supports_agents": ["developer", "auditor", "critic"],
      "delegation_triggers": ["crypto", "encryption", "hashing", "signing"],
      "affected_tasks": ["1-2-1", "2-1-3"]
    }
  ]
}
```

**Expert Awareness Injection**: When dispatching default agents, inject expert awareness into their prompts:

```
<expert_awareness>
YOU HAVE LIMITATIONS. Recognize them and ask for help.

YOUR LIMITATIONS AS A [AGENT_TYPE]:
- [From gap analysis - specific to this agent]

AVAILABLE EXPERTS:
| Expert | Expertise | Ask When |
|--------|-----------|----------|
{{#each available_experts}}
| {{name}} | {{expertise}} | {{delegation_triggers}} |
{{/each}}

IT IS BETTER TO ASK THAN TO GUESS WRONG.
</expert_awareness>
```

### Step 9: Plan Discovery

Read `{{PLAN_FILE}}`, parse tasks, build dependency graph, initialize state file.

### Step 10: Task Quality Assessment

Assess each task for implementability per [Task Quality](../task-quality.md).
Spawn business analyst agents for `NEEDS_EXPANSION` tasks. Use divine intervention for `NEEDS_CLARIFICATION` tasks.
Only `IMPLEMENTABLE` tasks enter `available_tasks`. Wait for all BA expansions to complete before dispatching
developers.

### Step 11: Save Initial State

Persist state to `{{STATE_FILE}}` before dispatching any agents.

### Step 12: Proceed to Execution Loop

---

## Related Documentation

- [Startup Overview](startup-overview.md) - Overview and decision logic
- [Resume](resume.md) - Resume session procedures
- [Coordinator Configuration](../coordinator-configuration.md) - Configuration values
- [State Management](../state-management.md) - State tracking
- [Task Quality](../task-quality.md) - Task assessment
