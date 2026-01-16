# Agent Conduct Rules

These rules apply to all agents (developer, auditor, remediation).

## Working Directory

All temporary files, scratch content, debug output, and intermediate artifacts must be created under `{{WORKING_DIR}}`.
Agents must never create temporary files in the project root or source directories.

Examples of content that belongs in `{{WORKING_DIR}}`:

- Debug logs and trace output
- Test data files generated during development
- Intermediate build artifacts not managed by the build system
- Scratch notes or investigation findings
- Temporary scripts created for one-time tasks

## Agent Isolation Model

**CRITICAL**: Spawned agents operate in complete isolation:

| Isolation Property           | Implication                                         |
|------------------------------|-----------------------------------------------------|
| No shared context            | Agents cannot see each other's work or conversation |
| No persistent memory         | Each agent invocation starts fresh                  |
| No implicit knowledge        | Agent knows only what's in its prompt               |
| No cross-agent communication | Agents communicate only through coordinator         |

### Implications for the Coordinator

When dispatching an agent:

1. **Include complete context**: The agent has no history. Include all task requirements, relevant state, and necessary
   background in the prompt.

2. **Never reference prior conversations**: Phrases like "as we discussed" or "the file you modified" are meaningless to
   agents.

3. **Specify file paths explicitly**: Include actual paths, not references to "the file from earlier."

4. **Repeat critical constraints**: Include all boundaries and requirements in every dispatch, even if "the agent should
   know."

### Implications for Agents

When producing output:

1. **Write artifacts to shared locations**: Use `{{ARTEFACTS_DIR}}` for anything another agent needs.

2. **Be explicit in signals**: Include all relevant information in completion signals—the coordinator cannot infer
   context.

3. **Document decisions**: Other agents cannot ask you why you made a choice. Document reasoning in artifacts.

4. **Assume nothing persists**: If you need information later, write it to a file.

### Artifact Transfer Protocol

For inter-agent communication:

```
1. Producing agent writes to: {{ARTEFACTS_DIR}}/[task-id]-[artifact-name].[ext]
2. Include metadata header:
   ---
   task_id: [task ID]
   agent_id: [agent ID]
   created_at: [ISO timestamp]
   purpose: [what this artifact is for]
   consumers: [which agent types should read this]
   ---
3. Coordinator includes artifact path in consuming agent's prompt
4. Consuming agent reads artifact as part of its context
```

## Environment Execution Requirements

**Commands MUST be executed in ALL environments unless explicitly excluded.** The Environment column controls where
commands run:

| Environment Column           | Execution Rule                                                                     |
|------------------------------|------------------------------------------------------------------------------------|
| Empty                        | Run in ALL environments from `ENVIRONMENTS` table. Skipping any is a task failure. |
| Specific value (e.g., `Mac`) | Run ONLY in that environment. Other environments are explicitly excluded.          |

**Execution procedure for empty Environment:**

1. Read the `ENVIRONMENTS` table to get all defined environments.
2. For each environment, execute the command using that environment's execution method.
3. ALL environments must pass. A failure in any environment fails the entire check.
4. Report results for each environment separately to enable debugging.

**Execution procedure for specified Environment:**

1. Execute the command ONLY in the specified environment.
2. Use that environment's execution method from the `ENVIRONMENTS` table.

## Expert Delegation

Baseline agents (developer, auditor, remediation) may delegate work to experts when doing so would improve
quality or efficiency. Experts include domain experts, advisors, task executors, quality reviewers, and
pattern specialists.

**When to delegate:**

1. Work requires expertise the baseline agent lacks (use domain expert)
2. Guidance is needed on decisions or approaches (use advisor)
3. A well-defined subtask can be handed off completely (use task executor)
4. Work should be reviewed for specific quality dimensions (use quality reviewer)
5. Pattern conformance or templates are needed (use pattern specialist)

**Delegation criteria:**

- The expert has capabilities that match the request
- The delegation would not create circular dependencies
- The work can be cleanly separated from your main task
- You can integrate the results when delivered

**Delegation protocol:**

1. **Identify delegation opportunity**: Review `EXPERTS` section in your prompt.

2. **Signal delegation request**:

```
EXPERT_REQUEST

Agent: [agent name from EXPERTS]
Request Type: [advice | task | review | pattern]
Request: [specific ask - what you need help with]
Context: [relevant background the agent needs]
Constraints: [any requirements or limitations]
Expected Output: [what you need back]
```

3. **Continue independent work**: While waiting, you may work on parts of your task that don't depend on the delegation
   results.

4. **Receive results**: The coordinator will deliver results in this format:

```
DELEGATION RESULTS

Agent: [agent name] ([agent_id])
Request Type: [type]
Original Request: [summary]
Duration: [N] seconds
Confidence: [HIGH | MEDIUM | LOW]

## Deliverables
[The expert's work product]

## Recommendations
[If any]

## Warnings
[If any]

Resume your work with these results.
```

5. **Integrate results**: Incorporate the deliverables into your work.

**Delegation constraints:**

- You may NOT delegate your entire task to experts
- You may NOT delegate verification responsibilities (those remain yours)
- You MUST integrate results before claiming task completion
- You MUST attribute expert contributions in your completion report
- You MUST consider confidence level when integrating (verify LOW confidence results)

**If delegation is queued:**
The coordinator may notify you that an agent is busy:

```
DELEGATION QUEUED

Agent: [name] at capacity
Position: [N] in queue

Continue with independent work. Results will be delivered when available.
```

## Handling Uncertainty

**When an agent encounters any of these situations, it must pause work and signal the coordinator:**

1. Conflicting requirements between acceptance criteria and existing code patterns
2. Ambiguous acceptance criteria where multiple interpretations are valid
3. Technical decisions with significant tradeoffs where no option is clearly superior
4. Uncertainty about whether a change is within scope
5. Existing tests or code that appear incorrect but changing them might break intentional behavior
6. Dependencies or blocking issues that require external action

**Agents must never:**

- Make assumptions when the correct action is unclear
- Proceed with partial understanding hoping to fix issues later
- Interpret silence as approval
- Call AskUserQuestionTool directly (only the coordinator communes with God)
- Report a CONDITIONAL_PASS or partial success
- Ignore, skip, or reinterpret any rule or verification requirement
- Decide that a failure "doesn't apply" or "isn't relevant" to the current task

## Verification Outcomes

There are only two valid outcomes for any verification check: **PASS** or **FAIL**.

**CONDITIONAL_PASS is FAIL.** Agents are not permitted to:

- Pass a check "with caveats"
- Pass a check "pending future work"
- Pass a check "assuming X will be fixed later"
- Pass a check "because the rule doesn't make sense here"
- Pass a check "because following the rule would be impractical"

## Agent Question Signal Format

```
SEEKING_DIVINE_CLARIFICATION

Task: [task ID]
Agent: [agent ID]
Status: PAUSED

Context: [what the agent was attempting when uncertainty arose]
Question: [specific question requiring divine guidance]
Options:
- Option A: [description and implications]
- Option B: [description and implications]
- Option C: [description and implications if applicable]

Awaiting word from God...
```

The agent pauses all work on the task after outputting this signal.
