# Expert Verification and Registration

**Navigation**: [Expert Creation Index](index.md) | Previous: [Prompt Structure](prompt-structure.md)

---

## Overview

Before finalizing an expert agent, verify it meets all quality standards and register it for use by baseline teammates.

---

## Verification Checklist

Before finishing, verify:

### Structure Checklist

- [ ] `<expert_identity>` explains why this expert exists and their authority
- [ ] `<who_asks_me>` lists which teammates and tasks
- [ ] `<expertise>` contains COMPREHENSIVE domain knowledge (not surface-level)
- [ ] `<decision_authority>` establishes expert-level judgment capabilities
- [ ] `<message_format>` contains SendMessage templates for EXPERT RESULT
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
- [ ] Expert demonstrates DEEPER knowledge than baseline teammates
- [ ] A domain expert reading this would recognize genuine expertise

---

## Quality Check

The expert you create will be consulted when baseline teammates face domain-specific challenges. Your guidance determines
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
- [ ] Can the expert identify subtle pitfalls that baseline teammates would miss?
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

- "This is surface-level knowledge anyone could find" -> **NOT DEEP ENOUGH**
- "This demonstrates genuine expertise and nuanced understanding" -> **CORRECT DEPTH**

### The Authority Test

When an expert gives advice, does it:

- Present options and trade-offs without a recommendation? -> **NOT AUTHORITATIVE**
- Give a clear answer with "Do X because Y"? -> **CORRECT AUTHORITY**

**Write it as if you're creating a consultant brief for someone who has spent 10+ years mastering this specific domain.**

---

## Expert Registration

After writing the file, the team lead registers the expert so teammates know it's available.

The registration information includes:

```
EXPERT_CREATED: [expert_name]

Gap Filled: [from gap analysis]
Supports: [which baseline teammates]
Tasks: [task IDs]
File: .claude/experts/<plan_slug>/[expert_name].md

Keyword Triggers: [comma-separated domain keywords for dynamic task matching]

Expertise Encoded:
- [key practice]
- [key pitfall to catch]

Delegation Triggers for Teammates:
- Developer should ask when: [trigger]
- Critic should ask when: [trigger]
- Ripple should ask when: [trigger]
- Auditor should ask when: [trigger]
```

The team lead tracks available experts in its context and includes the expert table when spawning
developers, the critic, and the auditor, so they know which expert advisors are available and when to consult them.

Expert agents are spawned as named teammates via:

```
Task({
  team_name: "<team>",
  name: "<expert-name>",
  prompt: "You are [expert-name]... [contents of expert file]",
  run_in_background: true
})
```

They communicate via `SendMessage`, just like all other teammates.

---

## Summary: The Expert Chain

1. Developer sends `NEED_EXPERT_ADVICE` to team lead, specifying the expert name
2. Team lead routes the request to the expert
3. Expert reads mailbox, applies expertise
4. Expert responds with EXPERT RESULT or indicates failure (after 3 attempts)
5. Team lead forwards expert advice to developer as `EXPERT_ADVICE_PROVIDED`
6. Developer implements the code based on expert guidance
7. On failure: Developer MUST escalate to team lead for user clarification (expert CANNOT delegate)

---

## Cross-References

- **[Documentation Index](../../index.md)** - Navigation hub for all docs
- [Escalation Specification](../../escalation-specification.md) - Escalation rules
- [Communication Protocol](../../communication-protocol.md) - SendMessage API and signal reference
