# Inputs and Research for Expert Creation

**Navigation**: [Expert Creation Index](index.md) | Previous: [Gap Analysis](gap-analysis.md) |
Next: [Prompt Structure](prompt-structure.md)

---

## Overview

After gap analysis, the orchestrator gathers comprehensive inputs and performs deep research to create the expert agent.

---

## Inputs Provided by Orchestrator

| Input                    | Description                                             | Use In                         |
|--------------------------|---------------------------------------------------------|--------------------------------|
| `GAP_ANALYSIS`           | What gap this expert fills                              | `<expert_identity>` section    |
| `AFFECTED_TASKS`         | Task IDs that need this expertise                       | `<plan_context>` section       |
| `SUPPORTING_AGENTS`      | Which default agents delegate to this expert            | `<who_asks_me>` section        |
| `DEEP_DOMAIN_RESEARCH`   | **Comprehensive** domain-specific knowledge (see below) | `<expertise>` section          |
| `REFERENCE_DOC_INSIGHTS` | Insights from plan's reference documentation            | `<plan_context>` section       |
| `DECISION_FRAMEWORKS`    | Expert-level decision patterns for the domain           | `<decision_authority>` section |
| `SIGNAL_SPECIFICATION`   | Exact signal formats                                    | `<signal_format>` section      |
| `PLAN_FILE`              | The implementation plan                                 | Context for advice             |
| `MCP_SERVERS`            | Available MCP servers for extended capabilities         | `<mcp_servers>` section        |

---

## Deep Domain Research (CRITICAL)

Unlike baseline agents who receive general best practices, **experts receive deep, comprehensive research**:

```
BASELINE AGENT RESEARCH:
- "Use type hints in Python"
- "Avoid mutable default arguments"
- "Follow PEP8"

EXPERT RESEARCH (much deeper):
- Complete understanding of domain theory and principles
- Historical context of why patterns evolved
- Edge cases and when standard advice doesn't apply
- Trade-off analysis frameworks with concrete decision criteria
- Common misconceptions and why they're wrong
- Expert-level opinions with authoritative justification
- Integration patterns with this specific plan's architecture
- Verification criteria that only domain experts would know
```

The orchestrator performs **additional specialized research** for each expert beyond what baseline agents receive.

---

## Research Requirements by Expert Type

### Domain Expert Research

For Domain Experts, research must include:

1. **Foundational Principles**
    - Core theory and concepts
    - Why patterns evolved historically
    - Fundamental trade-offs

2. **Expert-Level Patterns**
    - When to use each pattern
    - Why each pattern works
    - How to apply to this plan

3. **Pitfalls and Anti-Patterns**
    - Subtle issues non-experts miss
    - Why they're problematic
    - How to detect and correct

4. **Decision Frameworks**
    - Concrete criteria for choices
    - Trade-off evaluation methods
    - Authoritative recommendations

5. **Edge Cases**
    - When standard advice fails
    - What to do instead
    - Expert reasoning

6. **Common Misconceptions**
    - What seems right but isn't
    - Why it's wrong
    - Correct understanding

### Reference Expert Research

For Reference Experts, research must include:

1. **Document Intent**
    - Why it was created
    - What problems it solves
    - Consequences if ignored

2. **Comprehensive Rules**
    - All rules with rationale
    - Strictness levels
    - Correct application
    - Common misapplication

3. **Edge Cases & Precedence**
    - Conflicting rules
    - Resolution approaches
    - Expert reasoning

4. **Verification Checklist**
    - Specific checks
    - Violation patterns
    - How to fix

### Methodology Expert Research

For Methodology Experts, research must include:

1. **Document Analysis**
    - All relevant documents read
    - Explicit rules extracted
    - Examples and anti-examples
    - Document intent

2. **Cross-Document Synthesis**
    - Relationships between documents
    - Implicit conventions
    - Conflict resolution
    - Gaps requiring judgment

3. **Procedural Knowledge**
    - Step-by-step processes
    - Decision trees
    - Common mistakes
    - Gotchas

4. **Project-Specific Context**
    - How this project does things
    - What makes it unique
    - Integration with existing code

---

## Research Process

### For Domain/Left-Field Experts

```
1. WEB RESEARCH
   - Search for authoritative sources
   - Find expert-level content (not beginner tutorials)
   - Identify competing approaches and their trade-offs
   - Extract decision criteria

2. DEEP ANALYSIS
   - Understand foundational principles
   - Identify patterns and anti-patterns
   - Extract verification criteria
   - Document edge cases

3. PLAN INTEGRATION
   - Apply domain knowledge to this plan
   - Identify plan-specific considerations
   - Map domain patterns to plan requirements
   - Create plan-specific decision frameworks

4. SYNTHESIZE
   - Combine research into authoritative knowledge
   - Create decision frameworks with concrete criteria
   - Document expert opinions with justification
   - Prepare verification methods
```

### For Reference Experts

```
1. DOCUMENT READING
   - Read document completely multiple times
   - Extract all explicit rules
   - Note examples and anti-examples
   - Identify document purpose

2. DEEP INTERPRETATION
   - Understand WHY each rule exists
   - Identify strictness levels
   - Find edge cases and conflicts
   - Note common misapplications

3. VERIFICATION DESIGN
   - Create checklist for compliance
   - Document violation patterns
   - Design correction approaches
   - Map rules to this plan

4. SYNTHESIZE
   - Become authoritative interpreter
   - Create guidance for different agents
   - Document when to be strict vs. flexible
   - Prepare expert opinions on edge cases
```

### For Methodology Experts

```
1. IDENTIFY DOCUMENTS
   - Scan plan reference documentation
   - Check CLAUDE.md relevant sections
   - Find implicit documentation (configs, examples)

2. ANALYZE DOCUMENTS
   - Read each completely
   - Extract explicit rules
   - Note implicit patterns
   - Understand intent

3. SYNTHESIZE ACROSS DOCUMENTS
   - Find relationships
   - Identify conventions not explicitly stated
   - Resolve conflicts
   - Note judgment areas

4. CREATE PROCEDURAL KNOWLEDGE
   - Convert rules to step-by-step guidance
   - Build decision trees
   - Document common mistakes
   - Prepare project-specific advice
```

---

## Input Template for Expert Creation

After research, the orchestrator provides these inputs to the expert creation sub-agent:

```markdown
## INPUTS (provided by orchestrator)

### Gap Being Filled

This expert exists because default agents have this limitation:

GAP_ANALYSIS:
{{GAP_ANALYSIS}}

### Affected Tasks

Tasks that need this expertise:

AFFECTED_TASKS:
{{AFFECTED_TASKS}}

### Default Agents Who Will Delegate

These default agents will ask for help:

SUPPORTING_AGENTS:
{{SUPPORTING_AGENTS}}

### Deep Domain Research (COMPREHENSIVE)

This is your PRIMARY INPUT. This research is DEEPER than what baseline agents receive.
Use this to build AUTHORITATIVE expertise into the expert agent.

DEEP_DOMAIN_RESEARCH:
{{DEEP_DOMAIN_RESEARCH}}

This research includes:
- Foundational principles and theory
- Expert-level patterns and when to apply them
- Anti-patterns with nuanced explanations of WHY they're problematic
- Decision frameworks with concrete criteria
- Edge cases where standard advice doesn't apply
- Common misconceptions and corrections
- Trade-off analysis approaches

### Reference Documentation Insights

Insights extracted from the plan's reference documentation (CLAUDE.md, specs, etc.):

REFERENCE_DOC_INSIGHTS:
{{REFERENCE_DOC_INSIGHTS}}

Use these to ground your advice in THIS project's specific context.

### Expert Decision Frameworks

Pre-researched decision patterns for this domain:

DECISION_FRAMEWORKS:
{{DECISION_FRAMEWORKS}}

These frameworks enable the expert to make AUTHORITATIVE decisions, not guesses.

### Signal Specification

Experts MUST use these EXACT formats:

SIGNAL_SPECIFICATION:
{{SIGNAL_SPECIFICATION}}

### MCP Servers

Available MCP servers that extend expert capabilities beyond native tools.

MCP_SERVERS:
{{MCP_SERVERS}}

See: `.claude/docs/mcp-servers.md` for detailed usage guidance.
```

---

## Quality Standards for Research

### Depth Test

If a domain expert read the research, would they think:

- "This is surface-level knowledge anyone could find" → **NOT DEEP ENOUGH**
- "This demonstrates genuine expertise and nuanced understanding" → **CORRECT DEPTH**

### Completeness Test

Does the research enable the expert to:

- Make definitive recommendations (not "it depends")?
- Explain WHY, not just WHAT?
- Catch subtle pitfalls?
- Handle edge cases authoritatively?

If NO to any of these, research is **INCOMPLETE**.

### Plan-Specificity Test

Can the expert use this research to:

- Give advice specific to THIS plan?
- Apply domain knowledge to plan requirements?
- Make decisions considering plan constraints?

If NO to any of these, research needs **MORE PLAN INTEGRATION**.

---

## Next Steps

- **Next**: [Prompt Structure](prompt-structure.md) - Write the expert prompt with all required sections
- **See also**: [Expert Types](types.md) - Different types require different research approaches
