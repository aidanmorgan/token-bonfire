# Agent Prompt Engineering Guide

**Purpose**: Define principles for creating mission-oriented, high-quality agent prompts
**Version**: 2025-01-17-v2

---

## Core Philosophy

Agents are not tools to be configured. They are **roles to be inhabited**.

A well-crafted prompt doesn't just tell an agent what to do - it transforms how the agent thinks about their work. The
goal is to create agents that:

- **Own their mission** - feel personal responsibility for outcomes
- **Recognize their limits** - know when to ask for help vs. push through
- **Act with judgment** - make decisions within their authority, escalate beyond it
- **Produce verifiable work** - output that proves they did the work, not just claimed to

---

## Agent vs Expert: The Depth Distinction

**CRITICAL**: Baseline agents and experts serve different purposes and require different prompt structures.

### Baseline Agents (Developer, Critic, Auditor, etc.)

**Broad but shallow.** They handle many technologies and situations with competent general knowledge.

| Characteristic      | Implication for Prompts                  |
|---------------------|------------------------------------------|
| Wide scope          | Provide frameworks for common situations |
| General knowledge   | Emphasize when to recognize limits       |
| Many technologies   | Research injects breadth, not depth      |
| Frequent delegation | Expert awareness is critical             |

Baseline agents should think: "I can handle most things competently, but I know when I'm out of my depth."

### Expert Agents (Plan-Specific Specialists)

**Narrow but deep.** They provide authoritative guidance in one specific domain.

| Characteristic  | Implication for Prompts                           |
|-----------------|---------------------------------------------------|
| Single domain   | Deep expertise, not broad coverage                |
| Authoritative   | Definitive recommendations, not suggestions       |
| Last resort     | Cannot delegate - must solve or escalate to human |
| Rare invocation | Each consultation matters                         |

Experts should think: "In my domain, I am the authority. I give answers, not options."

---

## Mission-Oriented Identity

### The Stakes Are Real

Every agent prompt must make consequences concrete:

**WRONG** (abstract):

```
You review code for quality.
```

**RIGHT** (concrete stakes):

```
You are the last line of defense before code ships to production.

If you pass broken code:
- Real users experience real failures
- Security flaws expose customer data
- Bugs corrupt data at 3am when no one's watching

If you're too strict:
- Velocity dies
- Developers ignore your feedback
- Important features don't ship

Your judgment determines which of these happens.
```

### Ownership Language

Use personal, accountable language:

| Weak                          | Strong                            |
|-------------------------------|-----------------------------------|
| "The code should be reviewed" | "You review this code"            |
| "Tests need to pass"          | "Your tests must pass"            |
| "Issues should be reported"   | "You report every issue you find" |
| "Quality is important"        | "You are responsible for quality" |

### What You Are NOT

Every identity should include explicit scope limits:

```markdown
You Are NOT:
- A rubber stamp who approves everything
- A pedant who fails code for style preferences
- An implementer who fixes issues yourself
- A guesser who passes uncertain code
```

---

## Required Sections

Every agent prompt MUST include these sections:

### 1. Frontmatter (YAML)

```yaml
---
name: [agent-name]
description: [One sentence: what + when to use]
model: [sonnet | opus | haiku]
tools: [comma-separated list]
version: "YYYY-MM-DD-v1"
---
```

**Model Selection**:

- `opus`: Quality gatekeeping, complex judgment, high-stakes decisions
- `sonnet`: Implementation, moderate complexity, standard workflows
- `haiku`: Binary verification, fast checks, simple decisions

### 2. Agent Identity (CRITICAL)

This is the most important section. It shapes everything else.

```xml
<agent_identity>
You are [ROLE] responsible for [MISSION].

**THE STAKES**:
[Concrete consequences of doing this well vs poorly]

**YOUR AUTHORITY**:
- You CAN: [decisions within scope]
- You CANNOT: [decisions requiring escalation]

**YOUR COMMITMENT**:
- [What you refuse to compromise]
- [What you prioritize above all]

**YOU ARE NOT**:
- [Anti-pattern 1]
- [Anti-pattern 2]
</agent_identity>
```

### 3. Failure Modes (REQUIRED)

Anticipate how agents fail and build in countermeasures:

```xml
<failure_modes>
The most common ways agents in your role fail:

| Failure | Why It Happens | Your Countermeasure |
|---------|----------------|---------------------|
| Rubber-stamping | Assumption work is correct | Before passing: list 3 things that COULD be wrong |
| Vague feedback | Avoiding specifics | Every issue: file:line + specific fix |
| Scope creep | Helpfulness instinct | You [role]. You do not [other role]. |
| Missing context | Rushing | Read ALL relevant files before any judgment |
| False confidence | Pattern matching | If you haven't verified it, you don't know it |

You MUST internalize these countermeasures.
</failure_modes>
```

### 4. Decision Authority Matrix (REQUIRED)

Be explicit about what decisions the agent can make:

```xml
<decision_authority>
**DECIDE YOURSELF** (no escalation needed):
| Decision | Guidance |
|----------|----------|
| [Type] | [How to decide] |

**CONSULT EXPERT** (delegate before deciding):
| Decision | Which Expert | Why |
|----------|--------------|-----|
| [Type] | [expert-name] | [Requires domain depth] |

**ESCALATE TO HUMAN** (divine intervention):
| Decision | Why Human Needed |
|----------|------------------|
| [Type] | [Beyond agent authority] |

NEVER guess on expert or human decisions. Ask.
</decision_authority>
```

### 5. Pre-Signal Verification (REQUIRED)

Force self-questioning before any signal:

```xml
<pre_signal_verification>
**BEFORE ANY PASS/SUCCESS SIGNAL**, answer:
1. "What's the weakest part of this? Why am I passing it anyway?"
2. "If this fails in production, what will I wish I had caught?"
3. "Did I VERIFY this, or am I ASSUMING it?"

**BEFORE ANY FAIL SIGNAL**, answer:
1. "Is every issue I'm citing real, or am I being pedantic?"
2. "Can they fix this without asking followup questions?"
3. "Am I failing for the right reasons?"

**BEFORE ANY ESCALATION**, answer:
1. "Did I genuinely try 3 different approaches?"
2. "What SPECIFICALLY would help me?"

If you cannot answer these, you are not ready to signal.
</pre_signal_verification>
```

### 6. Success Criteria (Tiered)

Define minimum, expected, and excellent:

```xml
<success_criteria>
**MINIMUM** (must achieve):
- [Binary requirement]
- [Binary requirement]

**EXPECTED** (normal good work):
- [Quality standard]
- [Quality standard]

**EXCELLENT** (aspire to):
- [Excellence marker]
- [Excellence marker]

Aim for EXCELLENT, not just MINIMUM.
</success_criteria>
```

### 7. Method (Phased)

Each phase must have concrete, verifiable actions:

```xml
<method>
PHASE 1: [NAME]
1. [Action that produces observable output]
2. [Action that produces observable output]
Checkpoint: [What you should have at this point]

PHASE 2: [NAME]
...

FINAL PHASE: SIGNAL
1. Complete pre-signal verification
2. Output signal in exact format
</method>
```

### 8. Boundaries

Define both MUST and MUST NOT with reasons:

```xml
<boundaries>
**MUST**:
- [Required action] - because [consequence if skipped]
- [Required action] - because [consequence if skipped]

**MUST NOT**:
- [Prohibited action] - because [why this causes harm]
- [Prohibited action] - because [why this causes harm]
</boundaries>
```

### 9. Expert Awareness (Baseline Agents Only)

```xml
<expert_awareness>
**YOU ARE BROAD BUT SHALLOW.** You handle many things competently, but you are
not an expert in any specific domain.

**RECOGNIZE YOUR LIMITS**:
- You know patterns, not deep domain knowledge
- You can spot obvious issues, not subtle ones
- You can apply standard practices, not make authoritative domain calls

**AVAILABLE EXPERTS**:
| Expert | Domain | Ask When |
|--------|--------|----------|
{{AVAILABLE_EXPERTS}}

**WHEN TO ASK**:
- Domain-specific correctness questions
- Trade-offs requiring deep expertise
- "Is this the RIGHT way?" not just "Does this work?"

**IT IS BETTER TO ASK THAN TO GUESS WRONG.**
</expert_awareness>
```

### 10. Coordinator Integration

```xml
<coordinator_integration>
SIGNAL RULES:
- Signal MUST start at column 0 (no indentation)
- Signal MUST appear at END of response
- NEVER use signal keywords in prose
- Output exactly ONE primary signal per response
</coordinator_integration>
```

### 11. Signal Format

```xml
<signal_format>
[SIGNAL_NAME]:
\`\`\`
[Exact format with placeholders]
\`\`\`

CRITICAL: Use EXACT format. Malformed signals break the workflow.
</signal_format>
```

---

## Anti-Vagueness Standards

These words are BANNED without specifics:

| Banned        | Replacement Required           |
|---------------|--------------------------------|
| "carefully"   | What specific checks?          |
| "properly"    | What does proper mean?         |
| "appropriate" | What are the criteria?         |
| "as needed"   | When is it needed?             |
| "thoroughly"  | What does thorough include?    |
| "consider"    | What specifically to consider? |
| "ensure"      | How to verify?                 |
| "good"        | What makes it good?            |

**WRONG**: "Review the code carefully for issues"
**RIGHT**: "For each file, verify: no TODO/FIXME comments, no unused imports, all error paths handled, test coverage for
new code paths"

---

## Learning from Existing Prompts

Before creating an agent prompt, research existing successful prompts for similar roles.

### Why Research Existing Prompts

The orchestrator researches popular, well-regarded agent prompts to:

- Learn identity framing techniques that create ownership
- Discover constraint patterns that prevent common failures
- Find output format approaches that work well
- Understand error handling patterns from production prompts
- Gather decision-making frameworks that produce good results

### What to Look For

When analyzing existing prompts, extract:

| Element             | What to Look For                    | How to Adapt                         |
|---------------------|-------------------------------------|--------------------------------------|
| Identity            | How does it create agent ownership? | Apply similar framing to your domain |
| Constraints         | What boundaries prevent failure?    | Translate to your agent's scope      |
| Output Format       | How does it structure responses?    | Adapt signal format as needed        |
| Error Handling      | How does it handle edge cases?      | Apply similar patterns               |
| Decision Frameworks | How does it guide choices?          | Customize for your domain            |

### Adaptation vs Copying

DO: Extract patterns and principles, then apply them to your specific context
DON'T: Copy prompts verbatim - they won't fit your plan context

**Good adaptation:**

- "This prompt uses concrete stakes - I'll create stakes specific to MY agent"
- "This prompt has a failure modes table - I'll add one for MY agent's failures"

**Bad copying:**

- "This prompt mentions X so I'll mention X" (without understanding why)

---

## Calibration Examples (REQUIRED for Gatekeeping Agents)

Agents that pass/fail work need concrete examples:

```xml
<calibration>
**PASSES** (and why):
\`\`\`[language]
[Code example]
\`\`\`
Passes because: [specific reasons]

**FAILS** (and why):
\`\`\`[language]
[Code example]
\`\`\`
Fails because: [specific reasons]

**JUDGMENT CALL** (how to decide):
\`\`\`[language]
[Borderline example]
\`\`\`
Decision framework: [how to reason about this]
</calibration>
```

---

## Verification That Can't Be Faked

Structure requirements so completion proves the work was done:

**WRONG** (can fake):

```
Review the code and report issues.
```

**RIGHT** (proves engagement):

```
For each modified file, document:
- Lines reviewed: [X-Y]
- What this section does: [summary]
- Issues found: [list with line numbers, or "None after checking for: X, Y, Z"]
- Verdict: [PASS/ISSUE]
```

The structure forces actual engagement - you can't fill it out without reading.

---

## Quality Checklist

Before finalizing ANY agent prompt:

**Structure**:

- [ ] Frontmatter complete
- [ ] Identity creates ownership and stakes
- [ ] Failure modes anticipated with countermeasures
- [ ] Decision authority explicit (decide/consult/escalate)
- [ ] Pre-signal verification required
- [ ] Success criteria tiered (minimum/expected/excellent)
- [ ] Method has concrete, verifiable phases
- [ ] Boundaries explain WHY
- [ ] Signal format exact

**Language**:

- [ ] No banned vague words without specifics
- [ ] Uses ownership language ("you", "your")
- [ ] Stakes are concrete, not abstract
- [ ] Consequences explained for both directions

**For Baseline Agents**:

- [ ] Expert awareness section present
- [ ] Limits acknowledged
- [ ] Delegation triggers clear

**For Experts**:

- [ ] Deep expertise demonstrated (not surface-level)
- [ ] Authoritative tone (answers, not options)
- [ ] Cannot delegate emphasized
- [ ] Decision frameworks produce definitive recommendations

---

## The Meta-Prompt Mission

When you write a meta-prompt, remember:

**You are not configuring a tool. You are defining a role that will be inhabited.**

The agent you create will:

- Review every piece of code
- Audit every implementation
- Make pass/fail decisions with real consequences

If you create a weak agent:

- Bugs ship
- Quality degrades
- The system fails

If you create a strong agent:

- Quality improves with every cycle
- Issues die before they're born
- The system succeeds

**This is not optional. This is not "try your best." Make it excellent.**

---

## Cross-References

- **[Documentation Index](../index.md)** - Navigation hub
- [Meta-Prompting Architecture](../meta-prompting.md) - How this system works
- [Signal Specification](../signal-specification.md) - Signal formats
- [Escalation Specification](../escalation-specification.md) - When to escalate
- [Agent Context Management](../agent-context-management.md) - Context handling
