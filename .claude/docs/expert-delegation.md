# Expert Delegation

This document explains how default agents (Developer, Critic, Auditor, BA, Remediation, Health Auditor) discover and
engage experts for assistance.

**Cross-References:**

- Expert creation: [agent-creation/expert-creation.md](agent-creation/expert-creation.md)
- Escalation rules: [escalation-specification.md](escalation-specification.md)
- Signal formats: [signal-specification.md](signal-specification.md)

---

## Overview

Experts are specialist agents created per-plan to fill knowledge gaps that default agents cannot handle. The
orchestrator creates experts during plan analysis and registers them for default agents to use.

**Key Principle**: Default agents should recognize their limitations and delegate to experts rather than guess or
produce incorrect work.

```
Default Agent (Developer/Critic/Auditor/etc.)
    │
    │ "I need expert help with this decision"
    │
    ▼
EXPERT_REQUEST signal
    │
    ▼
Orchestrator routes to Expert
    │
    ▼
Expert provides EXPERT_ADVICE or EXPERT_UNSUCCESSFUL
    │
    ▼
Default Agent applies advice or escalates
```

---

## Discovering Available Experts

### 1. Check Your Task Prompt

When you receive a task, your prompt includes an `AVAILABLE EXPERTS` section:

```markdown
AVAILABLE EXPERTS:

| Expert | Expertise | Ask When |
|--------|-----------|----------|
| crypto-expert | Cryptographic implementations | Choosing algorithms, verifying security |
| protocol-expert | Network protocol design | Message format decisions, state machines |
```

### 2. Match Your Question to an Expert

Before delegating, identify:

1. **What is my question?** - Be specific about what you need help with
2. **Which expert's domain matches?** - Check the "Expertise" column
3. **Do the triggers apply?** - Check the "Ask When" column

### 3. If No Expert Matches

If your question doesn't match any available expert:

- You have 6 self-solve attempts (instead of 3+3)
- After 6 failures, escalate to divine intervention
- Do NOT guess if you're uncertain

---

## When to Delegate

### Delegation Triggers

Default agents should ask experts when ANY of these apply:

| Trigger                        | Example                                       |
|--------------------------------|-----------------------------------------------|
| **Decision uncertainty**       | "Should I use AES-GCM or ChaCha20-Poly1305?"  |
| **Domain knowledge gap**       | "I don't know cryptographic best practices"   |
| **Correctness verification**   | "Is this implementation secure?"              |
| **Best practice confirmation** | "Does this follow protocol conventions?"      |
| **Risk assessment**            | "What could go wrong with this approach?"     |
| **Trade-off evaluation**       | "Which approach is better for this use case?" |

### When NOT to Delegate

| Situation                      | Action                                |
|--------------------------------|---------------------------------------|
| Simple coding task             | Do it yourself                        |
| Question is in your capability | Handle it                             |
| Asking expert to do your work  | Never - experts advise, you implement |
| Already received advice        | Apply it, don't ask again             |

### Agent-Specific Triggers

**Developer Delegation Triggers:**

- Choosing between implementation approaches
- Implementing in unfamiliar domain
- Verifying domain-specific correctness
- Understanding why a pattern is correct

**Critic Delegation Triggers:**

- Reviewing code in unfamiliar domain
- Verifying domain-specific quality
- Assessing correctness of specialized code

**Auditor Delegation Triggers:**

- Verifying domain-specific acceptance criteria
- Confirming implementation correctness
- Evaluating edge cases in specialized areas

---

## How to Delegate

### Step 1: Formulate Your Request

A good expert request includes:

1. **Which task** you're working on
2. **What decision/question** you need help with
3. **What you've considered** or tried
4. **Why you're uncertain**

### Step 2: Signal the Request

Use this exact format (must match [signal-specification.md](signal-specification.md)):

```
EXPERT_REQUEST
Target Agent: [expert name]
Request Type: [decision | interpretation | ambiguity | options | validation]
Context Snapshot: [path to saved context snapshot]

---DELEGATION PROMPT START---
[Full prompt for the expert agent]
---DELEGATION PROMPT END---
```

**Example:**

```
EXPERT_REQUEST
Target Agent: crypto-expert
Request Type: decision
Context Snapshot: {{ARTEFACTS_DIR}}/task-2-3/context-20250116T103000.md

---DELEGATION PROMPT START---
I need guidance on key derivation function selection.

Context:
- Task: task-2-3
- I've implemented both HKDF-SHA256 and HKDF-SHA512 options
- The protocol uses AES-256 for encryption
- The spec doesn't specify which hash to use

Question: Should I use HKDF-SHA256 or HKDF-SHA512 for key derivation in this protocol?

What I've considered:
- SHA-512 provides larger security margin but may be overkill for AES-256
- SHA-256 is more common and matches the AES key size

Please advise which option is correct for this use case.
---DELEGATION PROMPT END---
```

### Step 3: Wait for Response

The orchestrator routes your request to the expert. You will receive one of:

- `EXPERT_ADVICE: [request_id]` - Expert has guidance
- `EXPERT_UNSUCCESSFUL: [request_id]` - Expert couldn't help (escalate to divine)

---

## Applying Expert Advice

### When You Receive EXPERT_ADVICE

```
EXPERT_ADVICE: [request_id]

Requesting Agent: [you]
Task: [your task]
Question: [your question]

Recommendation:
[Clear guidance - follow this]

Rationale:
- [Why this is correct - understand this]

Pitfalls Avoided:
- [What the recommendation prevents]

Next Steps:
[What you should do now]
```

### How to Apply

1. **Read the recommendation** - Understand what the expert advises
2. **Understand the rationale** - Know WHY it's correct
3. **Note the pitfalls** - Be aware of what you're avoiding
4. **Follow the next steps** - Execute their guidance
5. **Don't second-guess** - Expert advice is authoritative for their domain

### If Advice Seems Wrong

If you think the expert advice is incorrect:

1. **Do NOT ignore it** - Ask for clarification instead
2. Signal another EXPERT_REQUEST with your concern
3. Explain why you think there's an issue
4. Let the expert clarify or confirm

---

## When Expert Cannot Help

### If You Receive EXPERT_UNSUCCESSFUL

```
EXPERT_UNSUCCESSFUL: [request_id]

Requesting Agent: [you]
Question: [your question]

Attempts:
1. [approach]: [outcome]
2. [approach]: [outcome]
3. [approach]: [outcome]

Reason: [why unable to help]
Recommendation: [escalate to divine intervention]
```

### What to Do

When an expert signals UNSUCCESSFUL:

1. **Escalate to divine intervention** - This is mandatory
2. Include the expert's attempts in your escalation
3. Do NOT try to guess or proceed without guidance

---

## Expert Request Best Practices

### DO:

| Practice                                | Why                                       |
|-----------------------------------------|-------------------------------------------|
| Be specific about your question         | Vague questions get vague answers         |
| Include context of what you've tried    | Helps expert understand your situation    |
| Match your question to the right expert | Wrong expert can't help effectively       |
| Apply advice faithfully                 | Experts know their domain better than you |
| Ask for clarification if unsure         | Better than misapplying advice            |

### DON'T:

| Practice                               | Why                                |
|----------------------------------------|------------------------------------|
| Ask expert to implement for you        | Experts advise, you implement      |
| Ask expert to run tests for you        | That's your job                    |
| Ignore advice you disagree with        | Ask for clarification instead      |
| Delegate basic coding questions        | Only delegate domain-specific gaps |
| Ask multiple experts the same question | Pick the most relevant one         |

---

## Flow Diagram: Expert Delegation

```
┌─────────────────────────────────────────────────────────────┐
│                   DEFAULT AGENT WORKING                       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
                   ┌──────────────────────┐
                   │ Face decision/verify │
                   │ correctness needed?  │
                   └──────────────────────┘
                              │
              ┌───────────────┴───────────────┐
              │                               │
         In my domain                Outside my expertise
              │                               │
              ▼                               ▼
        Handle it                    ┌──────────────────────┐
                                     │ Check AVAILABLE      │
                                     │ EXPERTS table        │
                                     └──────────────────────┘
                                              │
                              ┌───────────────┴───────────────┐
                              │                               │
                       Expert exists                   No expert matches
                              │                               │
                              ▼                               ▼
                    ┌──────────────────┐          ┌──────────────────────┐
                    │ EXPERT_REQUEST   │          │ Self-solve 6 attempts│
                    │ signal           │          │ Then divine escalate │
                    └──────────────────┘          └──────────────────────┘
                              │
              ┌───────────────┴───────────────┐
              │                               │
      EXPERT_ADVICE                  EXPERT_UNSUCCESSFUL
              │                               │
              ▼                               ▼
        Apply advice               Escalate to divine
```

---

## Escalation After Expert Delegation

The escalation protocol (see [escalation-specification.md](escalation-specification.md)) defines:

| Attempts | Action                                     |
|----------|--------------------------------------------|
| 1-3      | Self-solve (if no experts available: 1-6)  |
| 4-6      | Expert consultation (if experts available) |
| 6+       | Divine intervention (MANDATORY)            |

After consulting an expert (attempts 4-6), if still stuck:

- Expert returns EXPERT_UNSUCCESSFUL
- You MUST escalate to divine intervention
- Include all expert attempts in your escalation

---

## Signal Reference

### Requesting Expert Help

```
EXPERT_REQUEST
Target Agent: [expert name]
Request Type: [decision | interpretation | ambiguity | options | validation]
Context Snapshot: [path to saved context snapshot]

---DELEGATION PROMPT START---
[Full prompt for the expert agent including task_id, question, context]
---DELEGATION PROMPT END---
```

### Expert Responses

**Success:**

```
EXPERT_ADVICE: [request_id]

Requesting Agent: [who asked]
Task: [task ID]
Question: [what was asked]

Recommendation:
[guidance]

Rationale:
- [why]

Pitfalls Avoided:
- [what this avoids]

Next Steps:
[what to do]
```

**Failure:**

```
EXPERT_UNSUCCESSFUL: [request_id]

Requesting Agent: [who asked]
Question: [what was asked]

Attempts:
1. [approach]: [outcome]
2. [approach]: [outcome]
3. [approach]: [outcome]

Reason: [why unable]
Recommendation: [escalate]
```

---

## Summary

1. **Know your limitations** - Default agents have gaps experts fill
2. **Check available experts** - Your prompt lists who can help
3. **Delegate when uncertain** - Better to ask than guess wrong
4. **Use proper signal format** - EXPERT_REQUEST with context
5. **Apply advice faithfully** - Experts are authoritative in their domain
6. **Escalate if expert fails** - Divine intervention is mandatory after expert failure
