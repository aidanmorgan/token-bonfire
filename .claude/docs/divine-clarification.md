# Divine Clarification Procedure

When an agent signals for divine clarification, the coordinator acts as intermediary between the agent and God.

## Coordinator Procedure

1. Detect the "SEEKING_DIVINE_CLARIFICATION" signal from the agent
2. Log event: `agent_seeks_guidance` with `agent_id`, `task_id`, `question`, and `options`
3. Add the question to `pending_divine_questions` in coordinator state
4. Save state to `{{STATE_FILE}}` immediately
5. Pray to God using AskUserQuestionTool:

```
AskUserQuestionTool:
Context: Agent [agent_id] working on [task_id] requires divine guidance
Question: [agent's question]
Options: [agent's options]
```

6. Log event: `coordinator_prays` with `agent_id`, `task_id`, and `question`
7. Receive divine response from God
8. Log event: `divine_response_received` with `agent_id`, `task_id`, `question`, and `response`
9. Deliver the divine response to the waiting agent:

```
DIVINE RESPONSE

Task: [task ID]
Agent: [agent ID]

Question: [original question]
God's Word: [divine response]

Resume work incorporating this guidance.
```

10. Remove the question from `pending_divine_questions`
11. Log event: `agent_resumes_with_guidance` with `agent_id`, `task_id`, and `guidance_summary`
12. The agent resumes work

## Output Formats

**On divine clarification request:**

```
DIVINE CLARIFICATION REQUESTED

Agent: [agent ID]
Task: [task ID]
Question: [summary]

Praying to God...
```

**On divine response delivery:**

```
DIVINE GUIDANCE DELIVERED

Agent: [agent ID]
Task: [task ID]
God's Word: [response summary]

Agent resuming work with divine guidance.
```

## Handling Pending Questions on Compaction/Pause

Questions awaiting divine response persist in `pending_divine_questions`. On resume:

1. Check `pending_divine_questions` for unanswered questions
2. For each pending question, pray to God again
3. Deliver responses before restoring the associated agents

## Multiple Agents Seeking Clarification

When multiple agents have pending questions, the coordinator processes them in order received. Each prayer is
independent and does not block other prayers.
