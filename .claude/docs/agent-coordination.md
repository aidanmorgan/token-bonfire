# Agent Coordination

The coordinator actively manages expert engagement through task analysis, proactive recommendations, and mediated
delegation.

**Related Documentation:**

- [Experts](experts.md) - Expert categories, creation framework, and templates
- [Expert Delegation](expert-delegation.md) - How default agents engage experts
- [Agent Context Management](agent-context-management.md) - Context monitoring and checkpointing

---

## Task-Agent Matching

When preparing to dispatch a baseline agent (developer, auditor, remediation), the coordinator analyzes the task against
available experts.

### Matching Algorithm

```
For each task ready for dispatch:
  1. Extract task keywords: technologies, patterns, domain terms, quality concerns
  2. For each agent in experts:
     a. Check if task_id is in agent.applicable_tasks → RECOMMENDED
     b. Check if task keywords overlap agent.keyword_triggers → SUGGESTED
     c. Check if task might need agent.request_types → AVAILABLE
     d. Otherwise → not included
  3. Sort agents by match strength: RECOMMENDED > SUGGESTED > AVAILABLE
  4. Group by agent_type: domain_expert, advisor, quality_reviewer, task_executor, pattern_specialist
  5. Include top matches per category in task assignment with match reason
```

### Match Categories

| Category    | Criteria                                       | Baseline Agent Guidance                              |
|-------------|------------------------------------------------|------------------------------------------------------|
| RECOMMENDED | Task ID in agent's `applicable_tasks`          | Strongly consider using this agent for relevant work |
| SUGGESTED   | Task keywords match agent's `keyword_triggers` | Use if work aligns with agent's capabilities         |
| AVAILABLE   | Agent's `request_types` might be useful        | Available for unexpected needs                       |

### Matching by Agent Type

| Agent Type         | Typical Matching Signal      | Delegation Trigger                     |
|--------------------|------------------------------|----------------------------------------|
| Domain Expert      | Technical domain keywords    | Complex domain-specific implementation |
| Advisor            | Decision points, uncertainty | "How should I..." questions            |
| Task Executor      | Repetitive task patterns     | Well-defined subtask extraction        |
| Quality Reviewer   | Quality dimension keywords   | Pre-completion review needs            |
| Pattern Specialist | Pattern-related keywords     | Pattern selection or conformance       |

---

## Proactive vs Reactive Coordination

### Proactive (Coordinator-Initiated)

The coordinator identifies agent support opportunities before dispatching:

1. **Pre-dispatch analysis**: Analyze task for expert applicability
2. **Agent-first routing**: For tasks requiring specialized artifacts, dispatch expert first
3. **Quality gate insertion**: For high-risk tasks, schedule quality review before audit
4. **Parallel support**: Dispatch independent experts alongside baseline agents

**Decision criteria for agent-first routing:**

```
IF task has RECOMMENDED agents of type domain_expert AND
   agent.capabilities cover 50%+ of task requirements
THEN
   Route to domain expert first for artifact generation
   Baseline agent receives artifacts as input
```

**Decision criteria for quality gate insertion:**

```
IF task involves any of: security, auth, payments, data integrity AND
   experts includes quality_reviewer for that dimension
THEN
   Schedule quality review between developer completion and auditor dispatch
```

### Reactive (Baseline Agent-Initiated) - Pause/Resume Model

When a baseline agent needs delegation, the **requesting agent** is responsible for:

1. Generating the prompt for the delegated agent
2. Saving a context snapshot before requesting delegation
3. Specifying what kind of support is needed

See [Expert Delegation](expert-delegation.md) for the full delegation flow and signal formats.

**Appropriate Delegation Requests**:

| Request Type     | Use When                                         | Example                                        |
|------------------|--------------------------------------------------|------------------------------------------------|
| `decision`       | Multiple valid approaches, need expert to choose | "Should I use Strategy A or Strategy B?"       |
| `interpretation` | Requirement is unclear, need expert analysis     | "What does 'scalable' mean in this context?"   |
| `ambiguity`      | Conflicting signals in codebase or requirements  | "The existing code does X but the spec says Y" |
| `options`        | Need expert to enumerate and evaluate choices    | "What are the patterns for handling this?"     |
| `validation`     | Want expert confirmation before proceeding       | "Is this approach correct?"                    |

**NOT appropriate for delegation** (do it yourself):

- Implementation work
- Running commands
- Reading files
- Simple lookups

---

## Delegation Flow Summary

```
1. Agent encounters decision point requiring expert guidance
2. Agent SAVES context snapshot to {{ARTEFACTS_DIR}}/[task_id]/context-[timestamp].md
3. Agent GENERATES the prompt for the delegated agent
4. Agent outputs EXPERT_REQUEST signal (includes prompt + snapshot path)
5. Coordinator DETECTS signal and PAUSES agent (stores agent_id for resume)
6. Coordinator SPAWNS delegated agent with the agent-provided prompt
7. Delegated agent completes and signals response
8. Coordinator RESUMES requesting agent with:
   - Delegation results
   - Path to their context snapshot
9. Requesting agent reads snapshot, integrates results, continues
```

See [Agent Context Management](agent-context-management.md) for context snapshot requirements.

---

## Delegation Signal Format

Baseline agents signal delegation using this format:

```
EXPERT_REQUEST

Target Agent: [expert name or type]
Request Type: [decision | interpretation | ambiguity | options | validation]
Context Snapshot: [path to saved context snapshot]

---DELEGATION PROMPT START---
[The full prompt for the delegated agent, generated by the requesting agent]
---DELEGATION PROMPT END---
```

See [Signal Specification](signal-specification.md) for complete signal formats.

---

## Context Snapshot Validation

**CRITICAL**: The coordinator validates context snapshots before processing delegation.

**Required Sections**:

| Section                      | Required    | Purpose                             |
|------------------------------|-------------|-------------------------------------|
| `# Context Snapshot:`        | Yes         | Header with task ID and timestamp   |
| `## Current Task`            | Yes         | Task ID and work description        |
| `## Progress So Far`         | Yes         | What has been completed (non-empty) |
| `## Current State`           | Yes         | Current work item and blocker       |
| `## Relevant Context`        | Recommended | Decisions, constraints, patterns    |
| `## Question for Delegation` | Yes         | Specific question (non-empty)       |
| `## Options Considered`      | Recommended | Options with pros/cons              |

On validation failure, the delegation is rejected and the agent must resubmit with a valid snapshot.

---

## Parallel Agent Execution

### Conditions for Parallel Dispatch

1. Multiple delegation requests are independent
2. No data dependencies between requests
3. Results can be integrated separately

### Parallel Dispatch Flow

```
1. Identify independent delegation opportunities
2. Spawn experts in parallel (single message, multiple Task calls)
3. Track all active experts
4. As each completes, process results
5. Deliver results as they arrive or batch for efficiency
```

---

## Agent Availability Management

### Concurrency Limits

```
MAX_CONCURRENT_PER_AGENT = 2

Before spawning:
  active_count = active_experts.filter(agent_id == target).count
  IF active_count >= MAX_CONCURRENT_PER_AGENT
  THEN
    Queue the request in pending_delegation_requests
    Notify baseline agent: "Agent [name] busy, request queued (position [N])"
    Log event: delegation_queued
```

When an expert completes:

1. Check pending_delegation_requests for same agent_id
2. If queued requests exist, dispatch oldest request
3. Notify originally requesting baseline agent

---

## Performance Tracking

Track expert effectiveness for optimization:

```json
{
  "expert_stats": {
    "[agent_id]": {
      "delegations": 10,
      "completions": 9,
      "failures": 0,
      "out_of_scope": 1,
      "avg_duration_seconds": 95,
      "confidence_distribution": {"HIGH": 7, "MEDIUM": 2, "LOW": 0},
      "tasks_benefited": ["task-3", "task-7", "task-12"]
    }
  }
}
```

Use this data to:

- Prioritize high-performing agents in recommendations
- Identify agents that frequently go out of scope (refine capabilities)
- Optimize agent creation for future plans
- Identify gaps in expert coverage

---

## Expert Result Integration

When experts return results, the coordinator ensures proper integration with the delegating baseline agent.

### Integration Scenarios

| Scenario                | Action                                            |
|-------------------------|---------------------------------------------------|
| Delegating agent active | Queue results for next interaction point          |
| Agent awaiting audit    | Store with task for inclusion in rework if needed |
| Agent crashed/failed    | Store results for task re-dispatch                |

### Result Delivery Format

```markdown
DELEGATION RESULTS

Agent: [agent name] ([agent_id])
Request Type: [type]
Original Request: [summary]
Confidence: [HIGH | MEDIUM | LOW]

## Deliverables
[Formatted deliverables from expert]

## Recommendations
[If any]

## Warnings
[If any]

Resume your work with these results.
```

---

## Inter-Agent Artefact Transfer

For complex artifacts that need to be shared between agents, use the artefacts directory.

### Artefacts Directory Structure

- `{{PLAN_DIR}}/.artefacts/[task-id]/` - Artifacts per task (schema.json, analysis-report.md, manifest.json)
- `{{PLAN_DIR}}/.artefacts/shared/` - Cross-task artifacts (project-patterns.md)

### Artifact Manifest Format

```json
{
    "task_id": "task-3-1-1",
    "created_by": "dev-agent-2",
    "created_at": "ISO-8601",
    "artifacts": [
        {
            "name": "schema.json",
            "type": "json_schema",
            "purpose": "Database schema for user authentication",
            "consumers": ["task-3-1-2", "task-3-2-1"]
        }
    ]
}
```

### Artifact Types

| Type               | Extension | Purpose                               |
|--------------------|-----------|---------------------------------------|
| `json_schema`      | `.json`   | Database schemas, API contracts       |
| `openapi`          | `.yaml`   | REST API specifications               |
| `typescript_types` | `.d.ts`   | TypeScript type definitions           |
| `python_protocol`  | `.pyi`    | Python protocol/interface definitions |
| `sql_migration`    | `.sql`    | Database migration scripts            |
| `analysis_report`  | `.md`     | Analysis documents, findings          |
| `test_fixtures`    | `.json`   | Shared test data                      |

### Artifact Lifecycle

1. **Creation**: Agent writes artifact with manifest
2. **Discovery**: Coordinator includes in dependent task prompts
3. **Consumption**: Dependent agent reads and uses artifact
4. **Archival**: After all consumers complete, artifact may be archived
5. **Cleanup**: Coordinator purges old artifacts on plan completion

---

## Coordinator Output Formats

**On expert dispatch:**

```
EXPERT DISPATCHED

Agent: [name] ([agent_id])
Type: [agent_type]
For: [baseline_agent_type] [baseline_agent_id] on [task_id]
Request: [summary]
```

**On results delivery:**

```
EXPERT RESULTS READY

Agent: [name] ([agent_id])
Duration: [N] seconds
Confidence: [level]
Deliverables: [count] items

Results delivered to [baseline_agent_type] [baseline_agent_id].
```

**On queue notification:**

```
DELEGATION QUEUED

Agent: [name] ([agent_id])
Position: [N] in queue
Reason: Agent at capacity ([current]/[max])
```

---

## Related Documentation

- [experts.md](experts.md) - Expert categories and creation framework
- [expert-delegation.md](expert-delegation.md) - Detailed delegation flow
- [agent-context-management.md](agent-context-management.md) - Context and checkpointing
- [signal-specification.md](signal-specification.md) - Signal format reference
- [state-management.md](state-management.md) - State tracking
- [event-logging.md](event-logging.md) - Event logging
