# Expert Advisor Consultation

This document explains how developers (and other teammates: critic, ripple, auditor) discover and
consult expert advisors for domain guidance.

**Cross-References:**

- Expert advisor creation: [agent-creation/expert-creation/index.md](agent-creation/expert-creation/index.md)
- Escalation rules: [escalation-specification.md](escalation-specification.md)

---

## Overview

Expert advisors are specialist advisory agents created per-plan to fill knowledge gaps that developers cannot handle. The
team lead creates expert advisors during plan analysis, persists them to `.claude/experts/<plan_slug>/`, and spawns them as
named teammates for the team to consult.

**Key Principle**: Expert advisors are advisory only — they provide domain guidance but never write or modify code. Developers implement; expert advisors advise.

**Key Principle**: Developers should recognize their limitations and consult expert advisors rather than guess or
produce incorrect work.

**Flow**: Developer sends `NEED_EXPERT_ADVICE` to team lead -> Team lead routes to expert advisor -> Expert advisor replies with `EXPERT_ADVICE_PROVIDED` -> Team lead relays advice to developer -> Developer applies guidance

---

## Discovering Available Expert Advisors

### 1. Check Your Task Context

When you receive a task, the task description or team lead instructions include an `AVAILABLE EXPERTS` section:

```markdown
AVAILABLE EXPERTS:

| Expert | Expertise | Keyword Triggers | Ask When |
|--------|-----------|------------------|----------|
| crypto-expert | Cryptographic implementations | encryption, AES, RSA, hashing, SHA, key derivation | Choosing algorithms, verifying security |
| protocol-expert | Network protocol design | protocol, handshake, message format, state machine | Message format decisions, state machines |
```

### 2. Match Your Question to an Expert Advisor

Before consulting an expert advisor, identify:

1. **What is my question?** - Be specific about what you need help with
2. **Which expert advisor's domain matches?** - Check the "Expertise" column
3. **Do the keyword triggers apply?** - Check the "Keyword Triggers" column for domain keywords in your task
4. **Do the triggers apply?** - Check the "Ask When" column

### 3. If No Expert Advisor Matches

If your question doesn't match any available expert advisor:

- You have 6 self-solve attempts total (since no expert advisor can help)
- After 6 self-solve failures, escalate to the team lead
- Do NOT guess if you're uncertain

---

## When to Consult Expert Advisors

### Consultation Triggers

Developers should consult expert advisors when ANY of these apply:

| Trigger                        | Example                                       |
|--------------------------------|-----------------------------------------------|
| **Decision uncertainty**       | "Should I use AES-GCM or ChaCha20-Poly1305?"  |
| **Domain knowledge gap**       | "I don't know cryptographic best practices"   |
| **Correctness verification**   | "Is this implementation secure?"              |
| **Best practice confirmation** | "Does this follow protocol conventions?"      |
| **Risk assessment**            | "What could go wrong with this approach?"     |
| **Trade-off evaluation**       | "Which approach is better for this use case?" |

### When NOT to Consult

| Situation                              | Action                                          |
|----------------------------------------|-------------------------------------------------|
| Simple coding task                     | Do it yourself                                  |
| Question is in your capability         | Handle it                                       |
| Asking expert advisor to write code    | Never - expert advisors advise, developers implement |
| Already received advice                | Apply it, don't ask again                       |

### Pre-Implementation Review (Optional)

For complex tasks where you want to validate your approach before coding:

1. **Before implementing**, send `NEED_EXPERT_ADVICE` to the team lead about your planned approach
2. **Describe your approach**, not the implementation details
3. **Ask for confirmation** or alternative recommendations
4. **Document as**: `Pre-implementation review: [expert-name] confirmed approach`

**When to use pre-implementation review:**

| Situation                 | Consider Pre-Implementation Review |
|---------------------------|------------------------------------|
| Multiple valid approaches | YES - expert advisor can guide best choice |
| High-risk implementation  | YES - catch issues early           |
| Unfamiliar domain         | YES - validate understanding       |
| Simple, clear task        | NO - proceed with implementation   |
| Time-sensitive task       | OPTIONAL - use judgment            |

Pre-implementation review is a judgment call by the developer, critic, ripple, or auditor based on task complexity and their confidence
level.

### Teammate-Specific Triggers

**Developer Consultation Triggers:**

- Choosing between implementation approaches
- Implementing in unfamiliar domain
- Verifying domain-specific correctness
- Understanding why a pattern is correct

**Critic Consultation Triggers:**

- Reviewing code quality in unfamiliar domain
- Verifying domain-specific style and patterns
- Assessing correctness of specialized code
- Evaluating edge cases in specialized areas

**Ripple Consultation Triggers:**

- Tracing downstream impact through unfamiliar module boundaries
- Determining whether an API contract change affects external consumers
- Assessing test coverage gaps in domains outside ripple's expertise
- Evaluating behavioral drift in callers that use specialized patterns

**Auditor Consultation Triggers:**

- Verifying acceptance criteria in unfamiliar domain
- Assessing domain-specific verification results
- Evaluating whether domain-specific requirements are met

---

## How to Consult Expert Advisors

### Step 1: Formulate Your Request

A good consultation request includes:

1. **Which task** you're working on
2. **What decision/question** you need help with
3. **What you've considered** or tried
4. **Why you're uncertain**

### Step 2: Send NEED_EXPERT_ADVICE to Team Lead

Developers send consultation requests to the team lead, who routes them to the appropriate expert advisor:

```
SendMessage({
  type: "message",
  recipient: "team-lead",
  content: "NEED_EXPERT_ADVICE: [task_id]\nExpert: [expert-name]\nRequest Type: [decision | interpretation | ambiguity | options | validation]\n\n[Full description of what you need help with, including context, what you've considered, and why you're uncertain]",
  summary: "Need expert advice on [topic] for task [task_id]"
})
```

**Example:**

```
SendMessage({
  type: "message",
  recipient: "team-lead",
  content: "NEED_EXPERT_ADVICE: task-2-3\nExpert: crypto-expert\nRequest Type: decision\n\nI need guidance on key derivation function selection.\n\nContext:\n- I've implemented both HKDF-SHA256 and HKDF-SHA512 options\n- The protocol uses AES-256 for encryption\n- The spec doesn't specify which hash to use\n\nQuestion: Should I use HKDF-SHA256 or HKDF-SHA512 for key derivation in this protocol?\n\nWhat I've considered:\n- SHA-512 provides larger security margin but may be overkill for AES-256\n- SHA-256 is more common and matches the AES key size\n\nPlease advise which option is correct for this use case.",
  summary: "Need crypto-expert advice on key derivation function selection"
})
```

### Step 3: Check for Response

Check your mailbox for the team lead's relay of the expert advisor's reply. The team lead will deliver the response via a message to your mailbox.

You will receive one of:

- `EXPERT_ADVICE_PROVIDED` with guidance from the expert advisor
- Expert advisor unable to help (escalate to team lead for user clarification)

---

## Applying Expert Advisor Advice

### When You Receive EXPERT_ADVICE_PROVIDED

The expert advisor replies (via team lead relay) with structured guidance including:

- **Recommendation**: Clear guidance to follow
- **Rationale**: Why this is correct
- **Pitfalls Avoided**: What the recommendation prevents
- **Next Steps**: What you should do now

### How to Apply

1. **Read the recommendation** - Understand what the expert advisor advises
2. **Understand the rationale** - Know WHY it's correct
3. **Note the pitfalls** - Be aware of what you're avoiding
4. **Follow the next steps** - Execute their guidance
5. **Don't second-guess** - Expert advisor advice is authoritative for their domain

### If Advice Seems Wrong

If you think the expert advisor's advice is incorrect:

1. **Do NOT ignore it** - Ask for clarification instead
2. Send another `NEED_EXPERT_ADVICE` to the team lead with your concern
3. Explain why you think there's an issue
4. Let the expert advisor clarify or confirm

---

## When Expert Advisor Cannot Help

If the expert advisor indicates they are unable to help:

1. **Escalate to the team lead** - This is mandatory
2. Include the expert advisor's attempts in your escalation
3. Do NOT try to guess or proceed without guidance

---

## Consultation Best Practices

### DO:

| Practice                                        | Why                                              |
|-------------------------------------------------|--------------------------------------------------|
| Be specific about your question                 | Vague questions get vague answers                |
| Include context of what you've tried            | Helps expert advisor understand your situation   |
| Match your question to the right expert advisor | Wrong expert advisor can't help effectively      |
| Apply advice faithfully                         | Expert advisors know their domain better than you|
| Ask for clarification if unsure                 | Better than misapplying advice                   |

### DON'T:

| Practice                                        | Why                                              |
|-------------------------------------------------|--------------------------------------------------|
| Ask expert advisor to write code for you        | Expert advisors advise, developers implement     |
| Ask expert advisor to run tests for you         | That's the developer's job                       |
| Ignore advice you disagree with                 | Ask for clarification instead                    |
| Consult for basic coding questions              | Only consult for domain-specific gaps            |
| Ask multiple expert advisors the same question  | Pick the most relevant one                       |

---

## Flow Diagram: Expert Advisor Consultation

1. Developer faces decision requiring domain expertise
2. In my domain -> Handle it
3. Outside expertise -> Check AVAILABLE EXPERTS table
4. Expert advisor exists -> Send NEED_EXPERT_ADVICE to team lead -> Team lead routes to expert advisor -> EXPERT_ADVICE_PROVIDED (apply) or expert advisor unable (escalate to team lead)
5. No expert advisor -> Self-solve 6 attempts then escalate to team lead

---

## Escalation After Expert Advisor Consultation

The escalation protocol (see [escalation-specification.md](escalation-specification.md)) defines:

| Attempts | Action                                              |
|----------|------------------------------------------------------|
| 1-3      | Self-solve (if no expert advisors available: 1-6)   |
| 4-6      | Expert advisor consultation (if advisors available) |
| After 6  | Escalate to team lead (MANDATORY)                   |

After consulting an expert advisor (attempts 4-6), if still stuck:

- Expert advisor indicates unable to help
- You MUST escalate to the team lead
- Include all expert advisor attempts in your escalation

---

## Summary

1. **Know your limitations** - Developers have gaps that expert advisors fill
2. **Check available expert advisors** - Your task context lists who can help
3. **Consult when uncertain** - Better to ask than guess wrong
4. **Use NEED_EXPERT_ADVICE signal** - Send to team lead, who routes to the expert advisor
5. **Apply advice faithfully** - Expert advisors are authoritative in their domain
6. **Escalate if expert advisor fails** - Escalation to team lead is mandatory after expert advisor failure
