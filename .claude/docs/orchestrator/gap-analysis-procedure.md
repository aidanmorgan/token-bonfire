# Gap Analysis Procedure

How the orchestrator identifies where baseline agents need expert support.

**Purpose**: Identify where baseline agents (Developer, Critic, Auditor) need expert guidance to make authoritative
decisions.

**CRITICAL**: Maximum of **25 experts** per project. Prioritize by impact and task coverage.

---

## Expert Categories

The gap analysis identifies FOUR types of experts:

| Expert Category         | Purpose                                 | Knowledge Shape                                         |
|-------------------------|-----------------------------------------|---------------------------------------------------------|
| **Reference Experts**   | Authoritative knowledge of project docs | Deep understanding of specific documentation            |
| **Methodology Experts** | Project-specific workflow expertise     | Synthesized from multiple docs for procedural knowledge |
| **Domain Experts**      | Deep expertise in technical domains     | Narrow but deep domain knowledge                        |
| **Left-Field Experts**  | Non-obvious but valuable expertise      | Deep knowledge of adjacent/implicit domains             |

---

## Phase 1: Reference Documentation Experts

**Created first** as they inform the domain analysis.

Reference experts are created when:

1. A document is complex enough to warrant deep expertise
2. Multiple agents need authoritative interpretation
3. The document contains nuanced rules that baseline agents might misapply

```python
def identify_reference_documentation_experts(reference_docs: dict) -> list[dict]:
    """Identify which reference documents need dedicated experts."""

    reference_experts = []

    for doc_path, analysis in reference_docs.items():
        expert_rec = analysis.get('expert_recommendation', {})

        if expert_rec.get('should_create_expert'):
            reference_experts.append({
                'expert_name': expert_rec.get('expert_name'),
                'domain': f"Project documentation: {doc_path}",
                'description': f"Authoritative expert on {analysis.get('summary', doc_path)}",
                'task_ids': ['*'],  # Applies to all tasks
                'requesting_agents': ['developer', 'critic', 'auditor'],
                'priority': 'HIGH',
                'obvious_or_leftfield': 'reference',
                'source_document': doc_path,
                'document_type': analysis.get('document_type')
            })

    return reference_experts
```

---

## Phase 2: Methodology Experts

**ALWAYS created for every project.** They provide essential guidance on project-specific workflows.

Methodology experts combine:

1. Project reference documentation (if available)
2. Web research for industry best practices
3. Codebase analysis to infer existing conventions
4. Synthesis of all sources into coherent guidance

### Methodology Expert Types

| Type                  | Triggers                          | Description                                        |
|-----------------------|-----------------------------------|----------------------------------------------------|
| `testing-methodology` | testing, test, spec, coverage     | How to write high-quality tests for this project   |
| `coding-standards`    | code, style, convention, lint     | How to write code that follows project conventions |
| `test-execution`      | run, execute, ci, pipeline, build | How to execute tests in project environment        |
| `quality-evaluation`  | quality, review, evaluate, assess | How to evaluate quality for this project           |

### Technology Detection

```python
def detect_project_technologies(plan_content: str, reference_docs: dict = None) -> dict:
    """Detect languages, frameworks, and tools used in the project."""

    technologies = {
        'languages': [],      # Python, TypeScript, etc.
        'frameworks': [],     # React, FastAPI, etc.
        'test_frameworks': [], # Pytest, Jest, etc.
        'build_tools': [],
        'databases': [],
        'infrastructure': []
    }

    # Detect from plan content and reference doc paths
    # ...

    return technologies
```

### Methodology Expert Structure

```python
{
    'expert_name': '{project}-testing-expert',
    'domain': 'Project methodology: testing-methodology',
    'description': 'How to write high-quality tests for this specific project',
    'task_ids': ['*'],
    'requesting_agents': ['developer', 'critic', 'auditor'],
    'priority': 'HIGH',
    'obvious_or_leftfield': 'methodology',
    'methodology_type': 'testing-methodology',
    'source_documents': ['TESTING.md'],
    'keyword_triggers': ['testing', 'test', 'spec'],
    'has_explicit_docs': True,
    'detected_technologies': {...},
    'research_sources': {
        'project_docs': [...],
        'web_search_required': True,
        'codebase_analysis_required': True,
        'synthesis_required': True
    },
    'web_search_queries': [
        'Python unit testing best practices 2024',
        'pytest best practices advanced'
    ]
}
```

---

## Phase 3: Domain and Left-Field Experts

### Obvious Experts (Direct Domain Matches)

Identify experts for domains explicitly mentioned in the plan:

- Specific technologies requiring deep expertise
- Regulatory/compliance domains
- Industry-specific knowledge
- Complex integrations with external systems

### Left-Field Experts (Non-Obvious but Valuable)

**MANDATORY: At least 2-3 left-field experts must be identified.**

Left-field experts address risks and quality concerns the plan author didn't think to mention.

**Questions to ask:**

- What could go wrong that a specialist would catch?
- What implicit requirements matter for production quality?
- What expertise would prevent future technical debt?
- What domains intersect with this plan in non-obvious ways?
- What would a senior architect insist on having input from?

**Common left-field categories:**

| Category                 | Focus                                               |
|--------------------------|-----------------------------------------------------|
| Observability/Monitoring | Logging, metrics, tracing, alerting                 |
| Security                 | Auth flows, data protection, vulnerability patterns |
| Performance              | Caching, optimization, load handling                |
| Resilience               | Error handling, retry logic, graceful degradation   |
| Maintainability          | Documentation, code organization, extensibility     |
| Operations               | Deployment, configuration, environment management   |
| Data Integrity           | Validation, consistency, migration safety           |
| User Experience          | Accessibility, error messages, edge cases           |

### Expert Prioritization

Score each potential expert:

| Factor               | Scale | Description                                 |
|----------------------|-------|---------------------------------------------|
| Task Coverage        | 1-5   | How many tasks benefit?                     |
| Decision Criticality | 1-5   | How costly if baseline agent guesses wrong? |
| Knowledge Gap        | 1-5   | How far outside baseline agent competence?  |

**Priority = (Task Coverage + Decision Criticality + Knowledge Gap) / 3**

- HIGH: >= 4.0
- MEDIUM: >= 2.5
- LOW: < 2.5

---

## Gap Analysis Prompt

```python
def analyze_gaps(plan_file: str, reference_docs: dict = None) -> list[dict]:
    """Analyze plan to identify ALL expertise gaps requiring expert agents."""

    plan_content = Read(plan_file)

    # Phase 1: Reference Documentation Experts
    reference_experts = identify_reference_documentation_experts(reference_docs or {})

    # Phase 2: Methodology Experts (ALWAYS created)
    methodology_experts = identify_project_methodology_experts(
        reference_docs or {},
        plan_content
    )

    # Phase 3: Domain and Left-Field Experts (via LLM analysis)
    domain_experts = Task(
        subagent_type="general-purpose",
        model="opus",
        prompt=f'''
Analyze this implementation plan to identify where baseline agents
will need expert guidance to make authoritative decisions.

PLAN:
{plan_content}

Identify:
1. OBVIOUS EXPERTS - domains explicitly mentioned
2. LEFT-FIELD EXPERTS (MANDATORY 2-3) - non-obvious but valuable

Return JSON array of expert gaps...
'''
    )

    # Phase 4: Merge all expert categories
    all_experts = reference_experts + methodology_experts + domain_experts

    # Enforce 25 expert limit with priority ordering
    if len(all_experts) > 25:
        all_experts.sort(key=lambda x: (
            0 if x.get('obvious_or_leftfield') == 'reference' else
            1 if x.get('obvious_or_leftfield') == 'methodology' else 2,
            {'HIGH': 0, 'MEDIUM': 1, 'LOW': 2}.get(x.get('priority', 'LOW'), 2),
            -len(x.get('task_ids', []))
        ))
        all_experts = all_experts[:25]

    return all_experts
```

---

## Output Format

```json
{
  "expert_gaps": [
    {
      "expert_name": "claude-md-expert",
      "domain": "Project documentation: CLAUDE.md",
      "description": "Authoritative expert on project coding standards",
      "task_ids": ["*"],
      "requesting_agents": ["developer", "critic", "auditor"],
      "priority": "HIGH",
      "obvious_or_leftfield": "reference",
      "source_document": "CLAUDE.md"
    },
    {
      "expert_name": "myproject-testing-expert",
      "domain": "Project methodology: testing-methodology",
      "description": "How to write high-quality tests for this project",
      "task_ids": ["*"],
      "requesting_agents": ["developer", "critic", "auditor"],
      "priority": "HIGH",
      "obvious_or_leftfield": "methodology",
      "methodology_type": "testing-methodology",
      "keyword_triggers": ["testing", "test", "spec"]
    },
    {
      "expert_name": "crypto-expert",
      "domain": "cryptographic protocols",
      "description": "Authoritative guidance on encryption and key management",
      "task_ids": ["task-2-1", "task-2-3"],
      "requesting_agents": ["developer", "critic", "auditor"],
      "priority": "HIGH",
      "obvious_or_leftfield": "obvious",
      "rationale": "Multiple tasks involve encryption"
    },
    {
      "expert_name": "observability-expert",
      "domain": "monitoring and tracing",
      "description": "Guidance on logging, metrics, and tracing",
      "task_ids": ["task-5-1"],
      "requesting_agents": ["developer", "auditor"],
      "priority": "MEDIUM",
      "obvious_or_leftfield": "leftfield",
      "rationale": "Plan doesn't mention observability but production needs it"
    }
  ],
  "analysis_metadata": {
    "total_identified": 22,
    "reference_experts": 2,
    "methodology_experts": 4,
    "domain_experts": 9,
    "leftfield_experts": 7,
    "limit_applied": false
  }
}
```

---

## Priority Ordering for 25-Expert Limit

When more than 25 experts are identified:

1. **Reference experts** - Project docs are foundational
2. **Methodology experts** - Project-specific workflow knowledge
3. **HIGH priority** domain/left-field experts
4. **MEDIUM priority** experts
5. **LOW priority** experts (dropped first)

---

## Related Documentation

- [Research Synthesis](research-synthesis.md) - Knowledge gathering
- [Agent Generation](agent-generation.md) - Creating agent prompts
- [Expert Creation](../agent-creation/expert-creation.md) - Expert templates
- [Experts](../experts.md) - Expert framework
