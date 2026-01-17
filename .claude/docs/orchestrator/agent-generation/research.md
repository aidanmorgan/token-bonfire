# Research Infrastructure and Essay Generation

[← Back to Agent Generation](./index.md)

How research is gathered, persisted, and synthesized for agent creation.

---

## Research Persistence

**CRITICAL**: All research performed during agent creation MUST be persisted as long-form essays.

| Agent Type          | Research Output Location                             |
|---------------------|------------------------------------------------------|
| **Baseline Agents** | `{{ARTEFACTS_DIR}}/agent-research/[agent-name].md`   |
| **Experts**         | `{{ARTEFACTS_DIR}}/expert-research/[expert-name].md` |

These research essays serve as:

1. **Transparency** - Document what knowledge was gathered and synthesized
2. **Debugging** - Understand why an agent behaves a certain way
3. **Iteration** - Improve research process based on outcomes
4. **Auditability** - Verify research quality and completeness

---

## Research Essay Format

Each agent/expert receives a dedicated long-form research essay documenting ALL knowledge gathered during creation.

### Research Essay Structure

```markdown
# Research Essay: [Agent/Expert Name]

**Generated**: [ISO-8601 timestamp]
**Agent Type**: [baseline|expert]
**Expert Category**: [domain|reference|methodology|leftfield] (experts only)

---

## Executive Summary

[2-3 paragraph summary of what this agent/expert does and what knowledge was gathered]

---

## Research Sources

### Project Documentation Analyzed
| Document | Type | Key Insights |
|----------|------|--------------|
| CLAUDE.md | coding-standard | [summary] |
| ... | ... | ... |

### Web Searches Performed
| Query | Top Results | Key Findings |
|-------|-------------|--------------|
| "{query}" | [URLs] | [summary] |
| ... | ... | ... |

### Codebase Patterns Discovered
| Pattern | Location | Relevance |
|---------|----------|-----------|
| [pattern name] | [file paths] | [why important] |
| ... | ... | ... |

---

## Knowledge Synthesis

### Primary Domain: [domain name]

[Detailed writeup of the domain knowledge, organized by sub-topic]

#### [Sub-topic 1]

[Comprehensive coverage of this aspect, including:
- Core principles and why they matter
- Best practices discovered from web research
- How this project specifically implements/expects this
- Edge cases and exceptions to standard advice
- Common misconceptions that could cause issues]

#### [Sub-topic 2]

[Same structure as above]

...

### Technology-Specific Knowledge: [language/framework]

[Detailed writeup specific to the project's technology stack]

#### Language Idioms and Patterns

[What idiomatic code looks like in this language for this agent's responsibilities]

#### Framework Conventions

[Framework-specific patterns and conventions relevant to this agent]

#### Testing Patterns (if applicable)

[How tests should be structured for this technology stack]

---

## Project-Specific Adaptations

### How This Project Differs from Standard Practices

[Document any ways the project's conventions differ from industry standards,
and how this agent should adapt]

### Priority Order for Conflicting Guidance

1. Project documentation requirements (highest priority)
2. Existing codebase patterns
3. Industry best practices (lowest priority)

### Project Constraints and Implications

[Any constraints from project docs that affect how this agent should operate]

---

## Delegation Guidance (Baseline Agents Only)

### Experts Available for Consultation

| Expert | Domain | When to Delegate |
|--------|--------|------------------|
| [name] | [domain] | [specific triggers] |
| ... | ... | ... |

### Delegation Decision Framework

[Detailed guidance on when to delegate vs handle independently]

---

## Quality Criteria

### What "Good" Looks Like for This Agent

[Specific quality criteria derived from research]

### Red Flags This Agent Should Catch

[Problems this agent is specifically equipped to identify]

### Common Mistakes to Avoid

[Based on research, what are common pitfalls]

---

## Research Gaps and Limitations

### Areas Where Research Was Limited

[Document any areas where web search returned insufficient results]

### Assumptions Made

[Any assumptions made where definitive guidance wasn't found]

### Recommended Follow-up Research

[Suggestions for improving this agent's knowledge in future iterations]

---

## Raw Research Data

<details>
<summary>Expand for full research transcripts</summary>

### Web Search Results

[Full transcripts of web search results]

### Document Analysis Notes

[Detailed notes from analyzing project documentation]

</details>
```

---

## Research Essay Generation Function

```python
def generate_research_essay(
    agent_name: str,
    agent_type: str,  # 'baseline' or 'expert'
    research_data: dict,
    plan_context: dict,
    artefacts_dir: str
) -> str:
    """Generate and persist a long-form research essay for an agent.

    CRITICAL: This function MUST be called for EVERY agent/expert created.
    The essay documents ALL research performed and knowledge synthesized.

    Args:
        agent_name: Name of the agent (e.g., 'developer', 'crypto-expert')
        agent_type: 'baseline' for core agents, 'expert' for specialists
        research_data: All research data gathered (web searches, doc analysis, etc.)
        plan_context: Context from the plan being executed
        artefacts_dir: Path to artefacts directory

    Returns:
        Path to the generated research essay file
    """

    # Determine output directory
    if agent_type == 'baseline':
        research_dir = f"{artefacts_dir}/{AGENT_RESEARCH_DIR}"
    else:
        research_dir = f"{artefacts_dir}/{EXPERT_RESEARCH_DIR}"

    os.makedirs(research_dir, exist_ok=True)
    essay_path = f"{research_dir}/{agent_name}.md"

    # Generate the essay using an LLM to synthesize all research into prose
    essay_content = Task(
        subagent_type="general-purpose",
        model="opus",
        prompt=f'''
Generate a comprehensive research essay documenting all knowledge gathered for this agent.

AGENT NAME: {agent_name}
AGENT TYPE: {agent_type}

RESEARCH DATA:
{json.dumps(research_data, indent=2)}

PLAN CONTEXT:
{json.dumps(plan_context, indent=2)}

CRITICAL REQUIREMENTS:
1. Write in LONG-FORM PROSE - this is an essay, not bullet points
2. Include ALL research sources with specific citations
3. Synthesize web research with project-specific findings
4. Document any conflicts between sources and how they were resolved
5. Be comprehensive - err on the side of including too much detail
6. Include the raw research data in a collapsible section at the end

Use the research essay structure defined in the agent-generation documentation.
The essay should be 2000-5000 words depending on the complexity of the domain.

OUTPUT: Return ONLY the markdown content of the essay, starting with the # heading.
'''
    )

    Write(essay_path, essay_content)

    log_event("research_essay_generated",
              agent_name=agent_name,
              agent_type=agent_type,
              essay_path=essay_path,
              word_count=len(essay_content.split()))

    return essay_path
```

---

## Quality Verification Requirement

**CRITICAL**: Every generated agent/expert prompt MUST be verified before being written.

**Prompt Generation Flow (Per Agent):**

1. Load template + injection context
2. Generate initial prompt
3. Invoke `/verify-prompt` skill
4. Apply CRITICAL + HIGH recommendations
5. Write revised prompt to file
6. Log: `prompt_quality_verified=True`

See [prompt-engineering-guide.md](../../agent-creation/prompt-engineering-guide.md) for quality standards.

---

## Related Documentation

- [Expert Generation](./expert-generation.md) - How experts receive deep research
- [Baseline Generation](./baseline-generation.md) - How baseline agents receive broad research
- [Prompt Engineering Guide](../../agent-creation/prompt-engineering-guide.md) - Quality standards
