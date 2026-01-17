# Expert Verification and Registration

**Navigation**: [Expert Creation Index](index.md) | Previous: [Prompt Structure](prompt-structure.md)

---

## Overview

Before finalizing an expert agent, verify it meets all quality standards and register it for use by default agents.

---

## Verification Checklist

Before finishing, verify:

### Structure Checklist

- [ ] `<expert_identity>` explains why this expert exists and their authority
- [ ] `<who_asks_me>` lists which agents and tasks
- [ ] `<expertise>` contains COMPREHENSIVE domain knowledge (not surface-level)
- [ ] `<decision_authority>` establishes expert-level judgment capabilities
- [ ] `<signal_format>` contains EXACT signal strings
- [ ] `<boundaries>` emphasizes NO DELEGATION
- [ ] `<mcp_servers>` lists available MCP servers with usage guidance

### Depth Checklist

- [ ] Foundational principles explained (not just rules listed)
- [ ] Expert-level patterns with WHY they work
- [ ] Subtle pitfalls that only experts would catch
- [ ] Decision frameworks that produce DEFINITIVE answers
- [ ] Edge cases where standard advice fails
- [ ] Common misconceptions with authoritative corrections
- [ ] Trade-off analysis approaches
- [ ] Expert opinions on domain debates (not hedged "it depends")

### Quality Checklist

- [ ] All advice frameworks are actionable, not vague
- [ ] Expert demonstrates DEEPER knowledge than baseline agents
- [ ] A domain expert reading this would recognize genuine expertise

---

## Quality Check

The expert you create will be consulted when default agents face domain-specific challenges. Your guidance determines
whether they get **authoritative help** or vague platitudes.

### Mission-Oriented Checklist

- [ ] Does the identity create ownership and stakes?
- [ ] Does the expert understand they give ANSWERS not OPTIONS?
- [ ] Are failure modes anticipated with countermeasures?
- [ ] Is "no delegation" emphasized throughout?
- [ ] Does the expert take AUTHORITATIVE positions?

### Depth Verification Checklist

- [ ] Does the expert demonstrate DEEP understanding (not surface-level knowledge)?
- [ ] Can the expert explain WHY patterns work, not just WHAT they are?
- [ ] Does the expert have authoritative opinions on domain debates?
- [ ] Can the expert identify subtle pitfalls that baseline agents would miss?
- [ ] Does the expert have decision frameworks that produce DEFINITIVE recommendations?
- [ ] Can the expert explain when standard advice DOESN'T apply?
- [ ] Does the expert correct common misconceptions with expert reasoning?

### Expert Type Checklist

For Domain/Left-Field Experts:

- [ ] Deep web research incorporated
- [ ] Foundational principles explained
- [ ] Trade-off frameworks produce definitive answers

For Reference Experts:

- [ ] Document analyzed comprehensively
- [ ] All rules extracted with rationale
- [ ] Edge cases and precedence documented
- [ ] Verification checklist provided

For Methodology Experts:

- [ ] Multiple documents synthesized
- [ ] Cross-document relationships documented
- [ ] Procedural knowledge extracted
- [ ] Project-specific conventions identified

---

## Quality Tests

### The Depth Test

If a domain expert read this agent's guidance, would they think:

- "This is surface-level knowledge anyone could find" → **NOT DEEP ENOUGH**
- "This demonstrates genuine expertise and nuanced understanding" → **CORRECT DEPTH**

### The Authority Test

When an expert gives advice, does it:

- Present options and trade-offs without a recommendation? → **NOT AUTHORITATIVE**
- Give a clear answer with "Do X because Y"? → **CORRECT AUTHORITY**

**Write it as if you're creating a consultant brief for someone who has spent 10+ years mastering this specific domain.
**

---

## Expert Registration

After writing the file, output:

```
EXPERT_CREATED: [expert_name]

Gap Filled: [from gap analysis]
Supports: [which default agents]
Tasks: [task IDs]
File: .claude/agents/experts/[expert_name].md

Keyword Triggers: [comma-separated domain keywords for dynamic task matching]

Expertise Encoded:
- [key practice]
- [key pitfall to catch]

Delegation Triggers for Default Agents:
- Developer should ask when: [trigger]
- Critic should ask when: [trigger]
- Auditor should ask when: [trigger]
```

---

## Orchestrator: Registering Experts

After creating experts, register them so default agents know they're available:

```python
def register_expert(expert_name: str, gap: dict, keyword_triggers: list[str]):
    """Register expert so default agents can use it."""
    state['available_experts'].append({
        'name': expert_name,
        'expertise': gap['expertise'],
        'supports_agents': gap['supports'],
        'delegation_triggers': gap['triggers'],
        'keyword_triggers': keyword_triggers,
        'affected_tasks': gap['tasks'],
        'file': f".claude/agents/experts/{expert_name}.md"
    })

    log_event("expert_created",
              name=expert_name,
              expertise=gap['expertise'],
              keyword_triggers=keyword_triggers,
              supports=gap['supports'])

    save_state()
```

---

## Summary: The Expert Chain

1. Default agent signals EXPERT_REQUEST
2. Orchestrator routes to expert
3. Expert provides EXPERT_ADVICE or EXPERT_UNSUCCESSFUL (after 3 attempts)
4. On EXPERT_ADVICE: Agent applies advice
5. On EXPERT_UNSUCCESSFUL: Agent MUST escalate to divine intervention (expert CANNOT delegate)

---

## Cross-References

- **[Documentation Index](../../index.md)** - Navigation hub for all docs
- [Agent Definitions](../../agent-definitions.md) - Default agent definitions
- [Signal Specification](../../signal-specification.md) - Expert signal formats
- [Escalation Specification](../../escalation-specification.md) - Escalation rules
- [Expert Delegation](../../expert-delegation.md) - Delegation protocol
- [MCP Servers](../../mcp-servers.md) - Using MCP server capabilities
