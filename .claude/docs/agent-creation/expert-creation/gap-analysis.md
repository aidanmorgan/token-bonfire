# Gap Analysis Process

**Navigation**: [Expert Creation Index](index.md) | Previous: [Expert Types](types.md) | Next: [Inputs](inputs.md)

---

## Overview

Before creating an expert, the orchestrator runs gap analysis to identify where default agents will need expert support.

---

## Gap Analysis Prompt

Use this prompt to analyze the implementation plan:

```
Analyze this implementation plan to identify where default agents will need expert support.

PLAN: {{PLAN_FILE}}

DEFAULT AGENT LIMITATIONS:

Developer:
- May not know domain-specific best practices
- May not recognize subtle pitfalls in specialized areas
- Cannot make expert judgment calls on trade-offs

Critic:
- May not recognize domain-specific quality issues
- Cannot judge domain-specific correctness

Auditor:
- May not recognize domain-specific correctness
- Cannot verify specialized implementations

IDENTIFY:

1. **Expertise Gaps**
   - What specialized knowledge do tasks require?
   - What domains have best practices default agents won't know?
   - What areas have pitfalls requiring expert awareness?

2. **Decision Points**
   - Where will default agents face choices they can't make alone?
   - What trade-offs require domain expertise?

3. **Verification Gaps**
   - What aspects can't default agents verify correctly?
   - Where does "correct" require domain knowledge?

OUTPUT:

GAP ANALYSIS: [Plan Name]

Gap 1: [Name]
- Affected Tasks: [task IDs]
- Default Agent Limitation: [which agent, what they can't do]
- Expertise Required: [specific knowledge needed]

RECOMMENDED EXPERTS:

1. [Expert Name]
   - Fills Gap: [which gap]
   - Supports: [which default agents]
   - Expertise Focus: [specific to plan]
   - Delegation Triggers: [when to ask]
```

---

## Gap Analysis Components

### 1. Expertise Gaps

Identify specialized knowledge that tasks require:

- **What specialized knowledge do tasks require?**
    - Technical domains (crypto, auth, databases)
    - Project-specific conventions
    - Methodological knowledge (testing, quality)

- **What domains have best practices default agents won't know?**
    - Domain-specific patterns
    - Industry standards
    - Framework-specific approaches

- **What areas have pitfalls requiring expert awareness?**
    - Subtle security issues
    - Performance traps
    - Correctness edge cases

### 2. Decision Points

Identify where default agents will face choices they can't make alone:

- **Where will default agents face choices they can't make alone?**
    - Architecture decisions
    - Technology selection
    - Trade-off evaluation

- **What trade-offs require domain expertise?**
    - Security vs. usability
    - Performance vs. maintainability
    - Completeness vs. simplicity

### 3. Verification Gaps

Identify what aspects default agents can't verify correctly:

- **What aspects can't default agents verify correctly?**
    - Domain-specific correctness
    - Best practice compliance
    - Edge case handling

- **Where does "correct" require domain knowledge?**
    - Cryptographic implementation
    - Concurrency patterns
    - Data integrity

---

## Gap Analysis Output Format

```
GAP ANALYSIS: [Plan Name]

Gap 1: [Gap Name]
- Affected Tasks: [task-001, task-002]
- Default Agent Limitation: Developer may not know secure key derivation practices
- Expertise Required: Cryptographic best practices, key management

Gap 2: [Gap Name]
- Affected Tasks: [task-003]
- Default Agent Limitation: Critic cannot judge protocol correctness
- Expertise Required: Protocol design, state machine verification

RECOMMENDED EXPERTS:

1. crypto-expert
   - Fills Gap: Gap 1
   - Supports: Developer (implementation), Critic (review), Auditor (verification)
   - Expertise Focus: Cryptographic primitives, key management for THIS plan
   - Delegation Triggers:
     - Developer: When implementing encryption/hashing
     - Critic: When reviewing security-sensitive code
     - Auditor: When verifying cryptographic correctness

2. protocol-expert
   - Fills Gap: Gap 2
   - Supports: Developer (design), Critic (correctness)
   - Expertise Focus: Protocol state machines, message formats for THIS plan
   - Delegation Triggers:
     - Developer: When designing protocol flows
     - Critic: When reviewing protocol implementation
```

---

## Using Gap Analysis Results

The gap analysis output provides inputs for expert creation:

| Gap Analysis Component   | Used In Expert Creation          |
|--------------------------|----------------------------------|
| Gap name                 | Expert identity, expertise focus |
| Affected tasks           | `AFFECTED_TASKS` input           |
| Default agent limitation | Expert identity rationale        |
| Expertise required       | Guides domain research           |
| Recommended experts      | Expert names and types           |
| Supports                 | `SUPPORTING_AGENTS` input        |
| Delegation triggers      | Expert's `<who_asks_me>` section |

---

## Next Steps

- **Next**: [Inputs](inputs.md) - Gather research and context for expert creation
- **See also**: [Expert Types](types.md) - Understand which expert type addresses each gap
