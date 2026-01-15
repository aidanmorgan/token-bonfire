# Agent Coordination

The coordinator actively manages supporting agent engagement through task analysis, proactive recommendations, and mediated delegation.

See [Supporting Agents](supporting-agents.md) for agent categories, creation framework, and templates.

## Task-Agent Matching

When preparing to dispatch a baseline agent (developer, auditor, remediation), the coordinator analyzes the task against available supporting agents.

### Matching Algorithm

```
For each task ready for dispatch:
  1. Extract task keywords: technologies, patterns, domain terms, quality concerns
  2. For each agent in supporting_agents:
     a. Check if task_id is in agent.applicable_tasks → RECOMMENDED
     b. Check if task keywords overlap agent.keyword_triggers → SUGGESTED
     c. Check if task might need agent.request_types → AVAILABLE
     d. Otherwise → not included
  3. Sort agents by match strength: RECOMMENDED > SUGGESTED > AVAILABLE
  4. Group by agent_type: domain_expert, advisor, quality_reviewer, task_executor, pattern_specialist
  5. Include top matches per category in task assignment with match reason
```

### Match Categories

| Category | Criteria | Baseline Agent Guidance |
|----------|----------|------------------------|
| RECOMMENDED | Task ID in agent's `applicable_tasks` | Strongly consider using this agent for relevant work |
| SUGGESTED | Task keywords match agent's `keyword_triggers` | Use if work aligns with agent's capabilities |
| AVAILABLE | Agent's `request_types` might be useful | Available for unexpected needs |

### Matching by Agent Type

Different agent types serve different purposes in task support:

| Agent Type | Typical Matching Signal | Delegation Trigger |
|------------|------------------------|-------------------|
| Domain Expert | Technical domain keywords | Complex domain-specific implementation |
| Advisor | Decision points, uncertainty | "How should I..." questions |
| Task Executor | Repetitive task patterns | Well-defined subtask extraction |
| Quality Reviewer | Quality dimension keywords | Pre-completion review needs |
| Pattern Specialist | Pattern-related keywords | Pattern selection or conformance |

## Proactive vs Reactive Coordination

### Proactive (Coordinator-Initiated)

The coordinator identifies agent support opportunities before dispatching:

1. **Pre-dispatch analysis**: Analyze task for supporting agent applicability
2. **Agent-first routing**: For tasks requiring specialized artifacts, dispatch supporting agent first
3. **Quality gate insertion**: For high-risk tasks, schedule quality review before audit
4. **Parallel support**: Dispatch independent supporting agents alongside baseline agents

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
   supporting_agents includes quality_reviewer for that dimension
THEN
   Schedule quality review between developer completion and auditor dispatch
```

### Reactive (Baseline Agent-Initiated)

Baseline agents signal delegation needs during work:

1. Baseline agent outputs delegation request signal
2. Coordinator intercepts and identifies target supporting agent
3. Coordinator spawns supporting agent with delegation context
4. Supporting agent completes work and signals completion
5. Coordinator delivers results to baseline agent
6. Baseline agent integrates and continues

## Coordinator Delegation Handler

When a baseline agent signals delegation intent, the coordinator processes it:

### Step 1: Parse Delegation Signal

Baseline agents signal delegation using this format:
```
DELEGATION REQUEST

Agent: [supporting agent name or type]
Request Type: [advice | task | review | pattern]
Request: [specific ask]
Context: [relevant background]
Constraints: [requirements]
Expected Output: [what's needed back]
```

Extract:
- Target agent (by name or type)
- Request type
- Request details
- Context and constraints
- Expected output format

### Step 2: Validate Delegation

```
1. Verify target agent exists in supporting_agents
2. Verify request_type is in agent.request_types
3. Verify baseline agent is active on a task (not completed/blocked)
4. Verify request is within agent's capabilities
5. Verify no circular delegation
```

If validation fails, return error to baseline agent with reason and suggestions.

### Step 3: Spawn Supporting Agent

```
Task tool parameters:
  model: [from AGENT_MODELS or agent-specific override]
  subagent_type: [agent.agent_id]
  prompt: |
    [agent.creation_prompt]

    ---

    DELEGATION REQUEST

    From: [baseline_agent_type] [agent_id] working on [task_id]
    Request Type: [request_type]
    Request: [request details]
    Context: [context from baseline agent]
    Constraints: [constraints from baseline agent]
    Expected Output: [expected output]

    Process this request according to your role and return results.
    Signal completion with: "AGENT COMPLETE: [your type]"
```

### Step 4: Track Delegation

Update state:
```json
{
  "active_supporting_agents": {
    "[run_id]": {
      "agent_id": "[agent.agent_id]",
      "delegating_agent": "[baseline_agent_id]",
      "task_id": "[task_id]",
      "request_type": "[type]",
      "request_summary": "[summary]",
      "dispatched_at": "ISO-8601"
    }
  }
}
```

Log event: `supporting_agent_delegated`

### Step 5: Handle Completion Signals

Supporting agents signal completion in standardized format:

**On `AGENT COMPLETE`:**
1. Parse output for deliverables, recommendations, warnings, confidence
2. Update state (remove from active_supporting_agents)
3. Update supporting_agent_stats with metrics
4. Log event: `supporting_agent_complete`
5. Deliver results to baseline agent (see format below)

**On `OUT_OF_SCOPE`:**
1. Parse suggested alternative
2. Log event: `supporting_agent_out_of_scope`
3. If alternative agent exists and is appropriate, route there
4. Otherwise, return to baseline agent with guidance

**On `BLOCKED` or `NEED_CLARIFICATION`:**
1. Determine if coordinator can resolve
2. If yes, provide clarification and let agent continue
3. If no, escalate to baseline agent or coordinator decision

### Step 6: Deliver Results

Format for delivering results to baseline agent:

```
DELEGATION RESULTS

Agent: [agent name] ([agent_id])
Request Type: [type]
Original Request: [summary]
Duration: [N] seconds
Confidence: [HIGH | MEDIUM | LOW]

## Deliverables
[Formatted deliverables from supporting agent]

## Recommendations
[If any]

## Warnings
[If any]

Resume your work with these results.
```

## Parallel Agent Execution

### Conditions for Parallel Dispatch

1. Multiple delegation requests are independent
2. No data dependencies between requests
3. Results can be integrated separately

### Parallel Dispatch Flow

```
1. Identify independent delegation opportunities
2. Spawn supporting agents in parallel (single message, multiple Task calls)
3. Track all active supporting agents
4. As each completes, process results
5. Deliver results as they arrive or batch for efficiency
```

### Parallel with Baseline Agent

Supporting agents can work in parallel with baseline agents when:
- Supporting agent work is independent of baseline agent's current step
- Results can be integrated when available
- No blocking dependency exists

## Agent Availability Management

### Concurrency Limits

```
MAX_CONCURRENT_PER_AGENT = 2

Before spawning:
  active_count = active_supporting_agents.filter(agent_id == target).count
  IF active_count >= MAX_CONCURRENT_PER_AGENT
  THEN
    Queue the request in pending_delegation_requests
    Notify baseline agent: "Agent [name] busy, request queued (position [N])"
    Log event: delegation_queued
```

### Queue Processing

When a supporting agent completes:
1. Check pending_delegation_requests for same agent_id
2. If queued requests exist, dispatch oldest request
3. Notify originally requesting baseline agent that their request is now being processed

## Performance Tracking

Track supporting agent effectiveness for optimization:

```json
{
  "supporting_agent_stats": {
    "[agent_id]": {
      "delegations": 10,
      "completions": 9,
      "failures": 0,
      "out_of_scope": 1,
      "avg_duration_seconds": 95,
      "confidence_distribution": {"HIGH": 7, "MEDIUM": 2, "LOW": 0},
      "tasks_benefited": ["task-3", "task-7", "task-12"],
      "baseline_agents_served": ["dev-1", "dev-2", "auditor-1"]
    }
  }
}
```

Use this data to:
- Prioritize high-performing agents in recommendations
- Identify agents that frequently go out of scope (refine capabilities)
- Optimize agent creation for future plans
- Identify gaps in supporting agent coverage

## Coordinator Output Formats

**On agent dispatch:**
```
SUPPORTING AGENT DISPATCHED

Agent: [name] ([agent_id])
Type: [agent_type]
For: [baseline_agent_type] [baseline_agent_id] on [task_id]
Request: [summary]

Baseline agent work continues where possible.
```

**On results delivery:**
```
SUPPORTING AGENT RESULTS READY

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

[baseline_agent_type] [baseline_agent_id] will receive results when available.
```

**On out-of-scope routing:**
```
DELEGATION REROUTED

Original Agent: [name] could not handle request (out of scope)
Rerouted To: [alternative agent name]
Reason: [explanation]

Processing continues with alternative agent.
```

---

## Supporting Agent Result Integration

When supporting agents return results, the coordinator must ensure proper integration with the delegating baseline agent.

### Result Storage

Store results in state for delivery:

```json
{
  "pending_result_delivery": [
    {
      "result_id": "result-1",
      "supporting_agent_id": "db-expert-1",
      "delegating_agent_id": "dev-agent-2",
      "task_id": "task-7",
      "request_type": "task",
      "deliverables": [...],
      "recommendations": [...],
      "warnings": [...],
      "confidence": "HIGH",
      "completed_at": "ISO-8601"
    }
  ]
}
```

### Integration Scenarios

#### Scenario 1: Delegating Agent Still Active

If the baseline agent is still working when supporting agent completes:

```python
def integrate_results_active_agent(result, delegating_agent):
    """Inject results into active agent's context."""

    # The Task tool doesn't support mid-execution injection
    # Store for next interaction point
    pending_result_delivery.append({
        'result_id': generate_id(),
        'supporting_agent_id': result['agent_id'],
        'delegating_agent_id': delegating_agent['agent_id'],
        'task_id': delegating_agent['task_id'],
        'deliverables': result['deliverables'],
        'recommendations': result.get('recommendations', []),
        'warnings': result.get('warnings', []),
        'confidence': result.get('confidence', 'MEDIUM'),
        'completed_at': datetime.now().isoformat(),
        'delivery_status': 'pending'
    })

    log_event("supporting_agent_results_queued",
              result_id=result['result_id'],
              waiting_for=delegating_agent['agent_id'])

    save_state()

    # Notify coordinator output
    output(f"Supporting agent results ready for {delegating_agent['task_id']}")
    output(f"Will deliver when agent reaches interaction point")
```

#### Scenario 2: Delegating Agent Completed (Awaiting Audit)

If baseline agent finished before supporting agent:

```python
def integrate_results_completed_agent(result, task_id):
    """Include results in rework or next task prompt."""

    # Store with task for inclusion in rework if needed
    task = get_task(task_id)
    task['supporting_agent_results'] = task.get('supporting_agent_results', [])
    task['supporting_agent_results'].append({
        'agent_id': result['agent_id'],
        'deliverables': result['deliverables'],
        'recommendations': result.get('recommendations', []),
        'warnings': result.get('warnings', []),
        'confidence': result.get('confidence', 'MEDIUM')
    })

    save_state()

    log_event("supporting_agent_results_stored",
              task_id=task_id,
              agent_id=result['agent_id'])

    # If task is in rework cycle, include in next dispatch
    if task_id in failed_audits:
        output(f"Supporting agent results will be included in rework prompt")
```

#### Scenario 3: Delegating Agent Failed/Crashed

If baseline agent crashed before receiving results:

```python
def integrate_results_failed_agent(result, task_id):
    """Store results for task re-dispatch."""

    # Store with task - will be included when task re-dispatches
    store_results_with_task(result, task_id)

    log_event("supporting_agent_results_orphaned",
              task_id=task_id,
              will_include_on_redispatch=True)

    output(f"Supporting agent results stored for {task_id} re-dispatch")
```

### Result Delivery Format

When delivering results to a baseline agent (in rework or continuation):

```markdown
SUPPORTING AGENT RESULTS AVAILABLE

The following supporting agent work completed while you were working:

{{#each pending_results}}
---
## From: {{this.agent_name}} ({{this.agent_id}})
Request: {{this.original_request}}
Confidence: {{this.confidence}}

### Deliverables
{{#each this.deliverables}}
{{this}}
{{/each}}

{{#if this.recommendations}}
### Recommendations
{{#each this.recommendations}}
- {{this}}
{{/each}}
{{/if}}

{{#if this.warnings}}
### Warnings
{{#each this.warnings}}
- {{this}}
{{/each}}
{{/if}}
---
{{/each}}

Integrate these results into your work as appropriate.
```

### Developer Rework with Results

When dispatching developer rework, include any pending results:

```python
def prepare_rework_prompt(task_id, audit_failures):
    """Prepare rework prompt including supporting agent results."""

    task = get_task(task_id)
    pending_results = task.get('supporting_agent_results', [])

    prompt = f"""
    REWORK REQUIRED: {task_id}

    AUDIT FAILURES:
    {format_failures(audit_failures)}

    REQUIRED FIXES:
    {format_required_fixes(audit_failures)}
    """

    if pending_results:
        prompt += f"""

    SUPPORTING AGENT RESULTS:
    The following work was completed by supporting agents and should be integrated:

    {format_supporting_results(pending_results)}

    Consider these results when addressing the required fixes.
    """

    return prompt
```

### Result Integration Tracking

Track which results have been delivered:

```json
{
  "result_delivery_log": [
    {
      "result_id": "result-1",
      "delivered_to": "dev-agent-2",
      "delivered_at": "ISO-8601",
      "delivery_context": "rework_prompt",
      "acknowledged": true
    }
  ]
}
```

### Integration State Events

| Event | Trigger | Data |
|-------|---------|------|
| `supporting_agent_results_queued` | Results ready, agent active | result_id, waiting_for |
| `supporting_agent_results_stored` | Results stored with task | task_id, agent_id |
| `supporting_agent_results_delivered` | Results sent to agent | result_id, delivered_to |
| `supporting_agent_results_orphaned` | Delegating agent crashed | task_id, will_include_on_redispatch |

---

## Inter-Agent Artefact Transfer

For complex artifacts that need to be shared between agents (schemas, specifications, generated code, analysis results), use the artefacts directory.

### Artefacts Directory: `{{ARTEFACTS_DIR}}`

```
{{PLAN_DIR}}/.artefacts/
├── [task-id]/                    # Artifacts organized by source task
│   ├── schema.json               # Generated schema
│   ├── analysis-report.md        # Analysis document
│   └── manifest.json             # Artifact manifest
└── shared/                       # Cross-task artifacts
    └── project-patterns.md       # Discovered patterns
```

### Artifact Manifest Format

Each task's artifacts should have a manifest:

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
        },
        {
            "name": "api-spec.yaml",
            "type": "openapi",
            "purpose": "API specification for auth endpoints",
            "consumers": ["task-3-2-*"]
        }
    ]
}
```

### Creating Artifacts

When an agent needs to share work products:

```python
# Write artifact to artefacts directory
artifact_dir = f"{{{{ARTEFACTS_DIR}}}}/{task_id}"
Bash(f"mkdir -p {artifact_dir}")

# Write the artifact
Write(f"{artifact_dir}/schema.json", schema_content)

# Write manifest
manifest = {
    "task_id": task_id,
    "created_by": agent_id,
    "created_at": datetime.now().isoformat(),
    "artifacts": [
        {
            "name": "schema.json",
            "type": "json_schema",
            "purpose": "Database schema for user model",
            "consumers": ["task-3-1-2"]
        }
    ]
}
Write(f"{artifact_dir}/manifest.json", json.dumps(manifest, indent=2))
```

### Consuming Artifacts

When a task needs artifacts from a previous task:

```python
# Include in developer prompt
prompt += f"""
AVAILABLE ARTIFACTS:

The following artifacts are available from prior tasks:

{{{{#each available_artifacts}}}}
From {{{{this.task_id}}}}:
- {{{{this.name}}}}: {{{{this.purpose}}}}
  Path: {{{{ARTEFACTS_DIR}}}}/{{{{this.task_id}}}}/{{{{this.name}}}}
{{{{/each}}}}

Read relevant artifacts before implementation.
"""
```

### Artifact Discovery

The coordinator discovers available artifacts when dispatching:

```python
def discover_artifacts_for_task(task_id):
    """Find artifacts relevant to this task."""

    available = []
    artefacts_dir = Path(ARTEFACTS_DIR)

    if not artefacts_dir.exists():
        return available

    for task_dir in artefacts_dir.iterdir():
        if not task_dir.is_dir():
            continue

        manifest_path = task_dir / "manifest.json"
        if not manifest_path.exists():
            continue

        with open(manifest_path) as f:
            manifest = json.load(f)

        for artifact in manifest.get("artifacts", []):
            # Check if this task is a consumer
            consumers = artifact.get("consumers", [])
            if any(fnmatch(task_id, pattern) for pattern in consumers):
                available.append({
                    "task_id": manifest["task_id"],
                    "name": artifact["name"],
                    "type": artifact["type"],
                    "purpose": artifact["purpose"],
                    "path": str(task_dir / artifact["name"])
                })

    return available
```

### Artifact Types

| Type | Extension | Purpose |
|------|-----------|---------|
| `json_schema` | `.json` | Database schemas, API contracts |
| `openapi` | `.yaml` | REST API specifications |
| `typescript_types` | `.d.ts` | TypeScript type definitions |
| `python_protocol` | `.pyi` | Python protocol/interface definitions |
| `sql_migration` | `.sql` | Database migration scripts |
| `analysis_report` | `.md` | Analysis documents, findings |
| `test_fixtures` | `.json` | Shared test data |
| `config_template` | `.template` | Configuration templates |

### Artifact Lifecycle

1. **Creation**: Agent writes artifact with manifest
2. **Discovery**: Coordinator includes in dependent task prompts
3. **Consumption**: Dependent agent reads and uses artifact
4. **Archival**: After all consumers complete, artifact may be archived
5. **Cleanup**: Coordinator purges old artifacts on plan completion
