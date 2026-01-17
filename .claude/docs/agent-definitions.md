# Agent Definitions and Creation Prompts

Variable: `AGENT_DEFINITIONS`

These are **prompts to spawn an agent** that creates the actual agent file. The coordinator dispatches an agent with the
creation prompt, and that agent writes the agent file to `.claude/agents/`.

For full creation prompts, see the individual files in [agent-creation/](agent-creation/index.md).

---

## Claude CLI Agent File Format

The agent must create files in this format:

```markdown
---
name: agent-name
description: When to use this agent (Claude uses this for auto-delegation)
model: sonnet
tools: Read, Edit, Write, Bash, Grep, Glob
---

<agent_identity>
[Who the agent is and what it does]
</agent_identity>

<success_criteria>
[When the agent's work is complete]
</success_criteria>

<method>
[Phased workflow the agent follows]
</method>

<boundaries>
[MUST and MUST NOT rules]
</boundaries>

<delegation_format>
[How to request help from other agents - if applicable]
</delegation_format>

<signal_format>
[Exact output format for completion signals]
</signal_format>
```

### Required Sections

Every agent file MUST contain:

- **Frontmatter**: name, description, model, tools
- **Identity**: Clear role definition and responsibilities
- **Success Criteria**: Specific, measurable completion conditions
- **Method/Workflow**: Phased approach with explicit steps
- **Boundaries**: MUST and MUST NOT rules
- **Signal Format**: Exact output format for coordinator parsing

---

## Protocol Compliance Requirements (All Agents)

**CRITICAL**: All agents must follow these rules for proper orchestrator integration.

### Signal Detection

The coordinator parses agent output using regex patterns that anchor to line start (`^`). Signal detection fails if
these rules are violated.

| Rule               | Requirement                             | Example                                                                                 |
|--------------------|-----------------------------------------|-----------------------------------------------------------------------------------------|
| Line position      | Signal MUST start at column 0           | `READY_FOR_REVIEW: task-1` (correct) vs `  READY_FOR_REVIEW: task-1` (wrong - indented) |
| Signal name        | Use EXACT name from specification       | `AUDIT_PASSED` not `AUDIT PASS` or `Audit Passed`                                       |
| Placement          | Signal should appear at END of response | After all explanatory text, not in the middle                                           |
| No false positives | Don't use signal keywords in prose      | Don't say "this is READY_FOR_REVIEW" in explanations                                    |

### Valid Signal Names

The coordinator recognizes these signal patterns:

| Signal                         | Regex Pattern                    | Used By              |
|--------------------------------|----------------------------------|----------------------|
| `READY_FOR_REVIEW: <id>`       | `^READY_FOR_REVIEW: (.+)$`       | Developer            |
| `TASK_INCOMPLETE: <id>`        | `^TASK_INCOMPLETE: (.+)$`        | Developer            |
| `INFRA_BLOCKED: <id>`          | `^INFRA_BLOCKED: (.+)$`          | Developer            |
| `REVIEW_PASSED: <id>`          | `^REVIEW_PASSED: (.+)$`          | Critic               |
| `REVIEW_FAILED: <id>`          | `^REVIEW_FAILED: (.+)$`          | Critic               |
| `AUDIT_PASSED: <id>`           | `^AUDIT_PASSED: (.+)$`           | Auditor              |
| `AUDIT_FAILED: <id>`           | `^AUDIT_FAILED: (.+)$`           | Auditor              |
| `AUDIT_BLOCKED: <id>`          | `^AUDIT_BLOCKED: (.+)$`          | Auditor              |
| `EXPANDED_TASK_SPECIFICATION`  | `^EXPANDED_TASK_SPECIFICATION$`  | Business Analyst     |
| `REMEDIATION_COMPLETE`         | `^REMEDIATION_COMPLETE$`         | Remediation          |
| `HEALTH_AUDIT: HEALTHY`        | `^HEALTH_AUDIT: HEALTHY$`        | Health Auditor       |
| `HEALTH_AUDIT: UNHEALTHY`      | `^HEALTH_AUDIT: UNHEALTHY$`      | Health Auditor       |
| `SEEKING_DIVINE_CLARIFICATION` | `^SEEKING_DIVINE_CLARIFICATION$` | Baseline agents only |
| `EXPERT_REQUEST`               | `^EXPERT_REQUEST$`               | Baseline agents only |
| `EXPERT_ADVICE: <id>`          | `^EXPERT_ADVICE: (.+)$`          | Experts              |
| `EXPERT_UNSUCCESSFUL: <id>`    | `^EXPERT_UNSUCCESSFUL: (.+)$`    | Experts              |

### Required Agent Instruction

Every agent creation prompt MUST instruct the agent to:

1. Output exactly ONE primary signal per response
2. Place the signal at the END of the response
3. Never use signal keywords in explanatory prose
4. Use the EXACT signal format (spacing, punctuation, field names)

### Include in All Agent Files

Every agent file's boundaries section should include:

```
COORDINATOR INTEGRATION (CRITICAL):
- Signal MUST start at column 0 (beginning of line, no indentation)
- Signal MUST appear at END of response (after all explanatory text)
- NEVER use signal keywords in prose (e.g., don't say "this is READY_FOR_REVIEW")
- Use EXACT signal format including spacing and punctuation
```

---

## Delegation Hierarchy

Agents are classified into two tiers with different delegation capabilities:

### Baseline Agents (Can Delegate)

These are the 6 core agents that execute the main workflow. They CAN delegate to experts.

| Agent            | Role                              | Can Delegate     |
|------------------|-----------------------------------|------------------|
| Developer        | Implements tasks                  | YES - to experts |
| Critic           | Reviews code quality before audit | YES - to experts |
| Auditor          | Validates work                    | YES - to experts |
| Business Analyst | Expands tasks                     | YES - to experts |
| Remediation      | Fixes infrastructure              | YES - to experts |
| Health Auditor   | Verifies health                   | YES - to experts |

### Experts (Cannot Delegate)

These are domain specialists created by the coordinator based on plan analysis. They CANNOT delegate further.

| Agent Type          | Examples                               | Can Delegate |
|---------------------|----------------------------------------|--------------|
| Domain Experts      | crypto-advisor, database-specialist    | NO           |
| Quality Reviewers   | security-reviewer, performance-analyst | NO           |
| Pattern Specialists | api-designer, ui-specialist            | NO           |

### Delegation Rules

1. **Baseline agents** can delegate to experts via `EXPERT_REQUEST`
2. **Experts** CANNOT delegate - they must self-solve or signal unsuccessful
3. **Experts** have 3 self-solve attempts before signaling `EXPERT_UNSUCCESSFUL`
4. **All delegation** goes through the coordinator - agents never communicate directly

### Expert Escalation

When an expert cannot complete a delegated request:

```
EXPERT_UNSUCCESSFUL: [request_id]

Delegating Agent: [who requested this work]
Request: [what was requested]

Attempts Made:
1. [approach 1]: [outcome]
2. [approach 2]: [outcome]
3. [approach 3]: [outcome]

Reason: [why all attempts failed]
Recommendation: [suggested alternative approach for calling agent]
```

The coordinator routes this back to the original delegating agent, who can then:

- Try a different expert
- Try a different approach themselves
- Escalate to divine intervention (after 3 delegation attempts total)

---

## Baseline Agent Definitions

### Developer Agent {#agent-def-developer}

**Output File**: `.claude/agents/developer.md`
**Runtime Model**: sonnet
**Creation Prompt**: See [agent-creation/developer.md](agent-creation/developer.md)

The Developer agent transforms task specifications into production-quality code. It implements what the coordinator
designs, focusing on execution excellence.

**Key Responsibilities**:

- Read and understand task specifications and acceptance criteria
- Implement code following existing codebase patterns
- Write tests proving each acceptance criterion
- Run verification commands in all required environments
- Signal ready for review when complete

**Signals**:

- Emits: `READY_FOR_REVIEW: <task_id>` (success)
- Emits: `TASK_INCOMPLETE: <task_id>` (blocked)
- Emits: `INFRA_BLOCKED: <task_id>` (pre-existing failures)

**Workflow Position**: Receives task → Implements → **Developer** → Critic

---

### Critic Agent {#agent-def-critic}

**Output File**: `.claude/agents/critic.md`
**Runtime Model**: sonnet
**Creation Prompt**: See [agent-creation/critic.md](agent-creation/critic.md)

The Critic agent sits between Developer and Auditor. When a Developer signals `READY_FOR_REVIEW`, the Critic reviews
code quality before passing to the Auditor. This catches quality issues early, before formal audit.

**Key Responsibilities**:

- Review code for bugs and correctness issues
- Check error handling approach
- Verify naming and style consistency
- Identify code structure and design issues
- Flag TODOs, FIXMEs, debug statements

**Signals**:

- Receives: `READY_FOR_REVIEW: <task_id>` (from Developer)
- Emits: `REVIEW_PASSED: <task_id>` or `REVIEW_FAILED: <task_id>`

**Workflow Position**: Developer → **Critic** → Auditor

**Critic Authority and Scope**:

| Reviews                         | Does NOT Review                           |
|---------------------------------|-------------------------------------------|
| Code correctness and bugs       | Requirements implementation               |
| Error handling approach         | Test adequacy/coverage                    |
| Naming and style consistency    | Performance correctness                   |
| Code structure and design       | Security correctness (delegate to expert) |
| TODOs, FIXMEs, debug statements | Acceptance criteria verification          |

---

### Auditor Agent {#agent-def-auditor}

**Output File**: `.claude/agents/auditor.md`
**Runtime Model**: opus
**Creation Prompt**: See [agent-creation/auditor.md](agent-creation/auditor.md)

The Auditor is the quality gatekeeper - the ONLY entity that can mark a task complete. Developers signal readiness for
audit but that claim means NOTHING until verified.

**Key Responsibilities**:

- Verify every acceptance criterion has implementation evidence
- Verify every acceptance criterion has test coverage
- Execute all verification commands independently
- Check for quality tells (TODOs, placeholders, debug artifacts)
- Make pass/fail/blocked judgment

**Signals**:

- Receives: `REVIEW_PASSED: <task_id>` (from Critic)
- Emits: `AUDIT_PASSED: <task_id>` (task complete)
- Emits: `AUDIT_FAILED: <task_id>` (needs rework)
- Emits: `AUDIT_BLOCKED: <task_id>` (infrastructure issues)

**Workflow Position**: Critic → **Auditor** → Task Complete or Developer Rework

---

### Business Analyst Agent {#agent-def-business-analyst}

**Output File**: `.claude/agents/business-analyst.md`
**Runtime Model**: sonnet
**Creation Prompt**: See [agent-creation/business-analyst.md](agent-creation/business-analyst.md)

The Business Analyst transforms underspecified tasks into implementable specifications. It analyzes; does not
implement (developer implements).

**Key Responsibilities**:

- Identify gaps in task specifications (scope, acceptance, location, approach, dependencies)
- Search codebase for similar implementations and patterns
- Expand specifications with verifiable acceptance criteria
- Assess confidence level (HIGH/MEDIUM/LOW)
- Ensure architectural alignment with existing patterns

**Signals**:

- Emits: `EXPANDED_TASK_SPECIFICATION` (success)
- Emits: `SEEKING_DIVINE_CLARIFICATION` (low confidence, needs human input)

**Workflow Position**: Underspecified Task → **Business Analyst** → Implementable Specification

---

### Remediation Agent {#agent-def-remediation}

**Output File**: `.claude/agents/remediation.md`
**Runtime Model**: sonnet
**Creation Prompt**: See [agent-creation/remediation.md](agent-creation/remediation.md)

The Remediation agent restores broken infrastructure to working state. It fixes systemic issues that block all
development.

**Key Responsibilities**:

- Diagnose all verification failures
- Fix root causes (not symptoms)
- Apply minimal changes without introducing new features
- Verify fixes don't cause regressions (rollback if they do)
- Confirm all verifications pass in all environments

**Signals**:

- Emits: `REMEDIATION_COMPLETE` (infrastructure restored)

**Workflow Position**: Infrastructure Broken → **Remediation** → Health Auditor

---

### Health Auditor Agent {#agent-def-health-auditor}

**Output File**: `.claude/agents/health-auditor.md`
**Runtime Model**: haiku
**Creation Prompt**: See [agent-creation/health-auditor.md](agent-creation/health-auditor.md)

The Health Auditor independently verifies codebase integrity after remediation. It does not trust Remediation Agent's
claims - verifies independently.

**Key Responsibilities**:

- Execute all verification commands independently
- Run in all required environments
- Report binary HEALTHY/UNHEALTHY outcome
- Never fix issues (only report)

**Signals**:

- Emits: `HEALTH_AUDIT: HEALTHY` (all verifications pass)
- Emits: `HEALTH_AUDIT: UNHEALTHY` (failures remain)

**Workflow Position**: Remediation → **Health Auditor** → Development Resumes or Remediation Retry

---

## Expert Agents

Experts are domain specialists created by the coordinator based on plan analysis.
See [expert-creation.md](agent-creation/expert-creation.md) for the full creation process.

### Runtime Model Selection

| Model    | Use When                                                           | Examples                                |
|----------|--------------------------------------------------------------------|-----------------------------------------|
| `opus`   | Complex judgment, nuanced analysis, architectural decisions        | Security Reviewer, Architecture Advisor |
| `sonnet` | Implementation work, code generation, moderate complexity analysis | Database Expert, Test Strategy Advisor  |
| `haiku`  | Simple verification, binary checks, pattern matching               | Format Checker, Naming Validator        |

### Tool Selection by Category

| Agent Category     | Typical Tools                              |
|--------------------|--------------------------------------------|
| Domain Expert      | Read, Edit, Write, Bash, Grep, Glob        |
| Advisor            | Read, Grep, Glob (no Write - advise only)  |
| Task Executor      | Read, Edit, Write, Bash, Grep, Glob        |
| Quality Reviewer   | Read, Bash, Grep, Glob (no Write - review) |
| Pattern Specialist | Read, Grep, Glob (may include Write)       |

### Expert Signals

Experts have TWO signals only:

**SUCCESS**:

```
EXPERT_ADVICE: [request_id]

Delegating Agent: [who requested this work]
Request: [what was requested]

Result:
- [what was accomplished]

Summary:
[1-2 sentence summary for delegating agent]
```

**FAILURE** (after 3 attempts):

```
EXPERT_UNSUCCESSFUL: [request_id]

Delegating Agent: [who requested this work]
Request: [what was requested]

Attempts Made:
1. [approach 1]: [outcome]
2. [approach 2]: [outcome]
3. [approach 3]: [outcome]

Reason: [why all attempts failed]
Recommendation: [suggested alternative approach for calling agent]
```

---

## Agent Creation Process

When the coordinator needs to create an agent:

1. **Check if Agent Exists**:
   ```python
   if not file_exists(f".claude/agents/{agent_name}.md"):
       # Spawn agent to create it
   ```

2. **Spawn Creation Agent**:
   ```
   Task tool parameters:
     model: opus  # ALWAYS use opus for agent prompt generation
     subagent_type: "developer"
     prompt: [Creation Prompt from agent-creation/*.md]
   ```

   **Why opus for generation**: Creating effective agent prompts requires:
    - Understanding of prompt engineering best practices
    - Nuanced instruction design for complex behaviors
    - Anticipating edge cases and failure modes
    - Crafting precise signal formats for reliable parsing

3. **Agent Creates File**:
    - Reads the creation prompt requirements
    - Writes agent file to `.claude/agents/[name].md`
    - Includes all required sections
    - Sets appropriate runtime model in frontmatter

4. **Coordinator Verifies**:
    - File exists at expected path
    - Frontmatter has: name, description, model, tools
    - Body has: identity, success criteria, method, boundaries, signal format
    - Log event: `agent_definition_created`

5. **Agent Ready for Use**:
    - Claude CLI can now delegate to this agent
    - Coordinator can spawn this agent via Task tool

---

## Related Documentation

- [Agent Creation Prompts](agent-creation/index.md) - Full creation prompts for each agent
- [Prompt Engineering Guide](agent-creation/prompt-engineering-guide.md) - Best practices for agent prompts
- [Expert Creation](agent-creation/expert-creation.md) - Creating expert agents
- [Signal Specification](signal-specification.md) - Complete signal format reference
- [Agent Coordination](agent-coordination.md) - How agents interact
