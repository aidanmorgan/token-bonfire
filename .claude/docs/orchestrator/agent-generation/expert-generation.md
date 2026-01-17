# Expert Prompt Generation

[← Back to Agent Generation](./index.md)

How the orchestrator generates specialized domain expert prompts with deep research.

**CRITICAL**: Experts receive DEEPER research than baseline agents - narrower domain but comprehensive expertise.

---

## Expert Research Routing

```python
def research_for_expert(gap: dict, plan_content: str, reference_docs: dict) -> dict:
    """Route to appropriate research function based on expert type."""

    expert_type = gap.get('obvious_or_leftfield', 'obvious')

    if expert_type == 'reference':
        return research_reference_documentation_expertise(gap, reference_docs)
    elif expert_type == 'methodology':
        return research_methodology_expertise(gap, reference_docs)
    else:
        return research_deep_domain_expertise(gap['domain'], gap, plan_content)
```

---

## Reference Expert Research

Reference experts need AUTHORITATIVE knowledge of project-specific documentation.

```python
def research_reference_documentation_expertise(gap: dict, reference_docs: dict) -> dict:
    """DEEP analysis of specific project document."""

    # Analyze:
    # 1. Document intent (why exists, problems solved)
    # 2. Comprehensive content extraction (every rule, rationale, strictness)
    # 3. Application guidance (how to apply, common misapplication)
    # 4. Edge cases (when rules conflict, precedence)
    # 5. Verification criteria (how to check compliance)
    # 6. Cross-document relationships
```

---

## Methodology Expert Research

Methodology experts SYNTHESIZE knowledge from MULTIPLE documents.

```python
def research_methodology_expertise(gap: dict, reference_docs: dict) -> dict:
    """Analysis across multiple project docs for procedural knowledge."""

    methodology_prompts = {
        'testing-methodology': [...],    # Test structure, patterns, coverage
        'coding-standards': [...],       # Code style, architecture, error handling
        'test-execution': [...],         # Running tests, environment, CI/CD
        'quality-evaluation': [...]      # Quality gates, review criteria, metrics
    }
```

---

## Domain Expert Research

Domain/left-field experts receive deep web research.

```python
EXPERT_SEARCH_TEMPLATES = {
    'queries': [
        "{domain} comprehensive best practices {year}",
        "{domain} expert-level patterns and techniques",
        "{domain} common pitfalls only experts catch",
        "{domain} decision frameworks and trade-offs",
        "{domain} edge cases and exceptions to standard advice",
        "{domain} misconceptions and corrections"
    ]
}
```

---

## Expert Creation Loop

```python
def generate_expert_prompts(gaps: list[dict], plan_file: str, best_practices: dict, artefacts_dir: str) -> list[dict]:
    """Generate expert agent prompts using parallel sub-agents.

    CRITICAL: For each expert, this function:
    1. Performs DEEP research specific to the expert's domain
    2. Generates and persists a research essay documenting all findings
    3. Creates the expert prompt using the research
    4. Verifies the prompt meets quality standards
    """

    os.makedirs(EXPERTS_DIR, exist_ok=True)
    os.makedirs(f"{artefacts_dir}/{EXPERT_RESEARCH_DIR}", exist_ok=True)

    pending_gaps = list(gaps)
    active_creators = {}
    created_experts = []
    plan_content = Read(plan_file)
    reference_docs = best_practices.get('reference_documentation', {})
    plan_context = best_practices.get('plan_context', {})

    while pending_gaps or active_creators:
        # Fill slots up to ACTIVE_DEVELOPERS
        while len(active_creators) < ACTIVE_DEVELOPERS and pending_gaps:
            gap = pending_gaps.pop(0)

            # Perform DEEP research for this expert
            deep_research = research_for_expert(gap, plan_content, reference_docs)

            # ═══════════════════════════════════════════════════════════════════
            # CRITICAL: Generate and persist research essay BEFORE creating prompt
            # ═══════════════════════════════════════════════════════════════════
            essay_path = generate_research_essay(
                agent_name=gap['expert_name'],
                agent_type='expert',
                research_data={
                    'gap_definition': gap,
                    'deep_research': deep_research,
                    'web_searches': deep_research.get('web_search_results', []),
                    'document_analysis': deep_research.get('document_analysis', {}),
                    'codebase_patterns': deep_research.get('codebase_patterns', []),
                    'synthesis_notes': deep_research.get('synthesis', {})
                },
                plan_context=plan_context,
                artefacts_dir=artefacts_dir
            )

            formatted_research = format_deep_research_for_expert(deep_research)

            # Dispatch sub-agent in background
            agent_id = Task(
                subagent_type="developer",
                model="opus",
                run_in_background=True,
                prompt=f"""
Create an EXPERT agent file.

EXPERT NAME: {gap['expert_name']}
OUTPUT FILE: {EXPERTS_DIR}/{gap['expert_name']}.md

DEEP DOMAIN RESEARCH:
{formatted_research}

RESEARCH ESSAY: {essay_path}
(The full research essay has been persisted - reference it for comprehensive context)

CRITICAL: Expert must have DEEP expertise - narrower but more comprehensive.
"""
            )
            active_creators[agent_id] = {
                'gap': gap,
                'essay_path': essay_path,
                'research': deep_research
            }

        # Wait for completions and verify
        if active_creators:
            completed_id, result = await_any_agent(list(active_creators.keys()))
            creator_info = active_creators.pop(completed_id)

            # Verify file exists and is valid
            expert_file = f"{EXPERTS_DIR}/{creator_info['gap']['expert_name']}.md"
            if os.path.exists(expert_file):
                content = Read(expert_file)
                if 'EXPERT_ADVICE' in content:
                    created_experts.append({
                        'name': creator_info['gap']['expert_name'],
                        'file': expert_file,
                        'research_essay': creator_info['essay_path'],
                        'domain': creator_info['gap']['domain'],
                        'category': creator_info['gap'].get('obvious_or_leftfield', 'domain')
                    })
                    log_event("expert_created",
                              name=creator_info['gap']['expert_name'],
                              file=expert_file,
                              research_essay=creator_info['essay_path'])
                else:
                    # Re-queue if invalid
                    pending_gaps.append(creator_info['gap'])
            else:
                pending_gaps.append(creator_info['gap'])

    return created_experts
```

---

## Related Documentation

- [Research Infrastructure](./research.md) - How research essays are generated
- [Baseline Generation](./baseline-generation.md) - Creating core agents
- [Expert Creation Template](../../agent-creation/expert-creation.md) - Expert prompt templates
- [Gap Analysis](../gap-analysis-procedure.md) - How expert needs are identified
