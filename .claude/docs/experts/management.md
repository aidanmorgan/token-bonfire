# Expert Management

[← Back to Expert Framework](./index.md)

---

## Recording Experts

Record each created agent in `experts` state:

```json
{
  "agent_id": "unique-id",
  "agent_type": "domain_expert | advisor | task_executor | quality_reviewer | pattern_specialist",
  "name": "Human-readable name",
  "domain": "Area of expertise",
  "capabilities": [
    "capability 1",
    "capability 2"
  ],
  "applicable_tasks": [
    "task-1",
    "task-5"
  ],
  "keyword_triggers": [
    "keyword1",
    "keyword2"
  ],
  "request_types": [
    "advice",
    "task",
    "review"
  ],
  "creation_prompt": "Full prompt used to create the agent",
  "created_at": "ISO-8601",
  "usage_count": 0
}
```

Log event: `expert_created` with full agent details.

---

## Agent Spawning

Experts are NOT pre-spawned. The coordinator spawns them on-demand when:

1. **Proactive routing**: Coordinator determines a task benefits from agent support
2. **Reactive delegation**: Baseline agent signals delegation during work
3. **Quality gate**: Coordinator inserts quality review before audit

See [Agent Coordination](../agent-coordination.md) for coordination mechanics.

---

## Example Experts

Based on common plan patterns, these agents are frequently useful:

| Agent                  | Category           | When Useful                                         |
|------------------------|--------------------|-----------------------------------------------------|
| Security Reviewer      | Quality Reviewer   | Plans with auth, user input, or sensitive data      |
| API Designer           | Advisor            | Plans with multiple API endpoints                   |
| Database Expert        | Domain Expert      | Plans with schema changes or complex queries        |
| Test Strategy Advisor  | Advisor            | Plans with complex testing requirements             |
| Error Handling Pattern | Pattern Specialist | Plans across many modules needing consistent errors |
| Performance Reviewer   | Quality Reviewer   | Plans with latency or throughput requirements       |
| Configuration Executor | Task Executor      | Plans with repetitive config file generation        |

---

[← Back to Expert Framework](./index.md)
