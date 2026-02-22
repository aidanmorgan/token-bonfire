# Gap Analysis Procedure

How the team lead identifies where teammates need expert support.

**Purpose**: Identify where static agents need expert guidance to make authoritative decisions.

**CRITICAL**: Maximum of **MAX_EXPERTS expert advisors** per project (default 3). Prioritize by impact and task coverage.

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
2. Multiple teammates need authoritative interpretation
3. The document contains nuanced rules that developers might misapply

The team lead analyzes each reference document and determines whether a dedicated expert is needed.
If so, the expert is persisted to `.claude/experts/<plan_slug>/[doc-name]-expert.md`.

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

The team lead detects languages, frameworks, and tools from:

- Plan content mentions
- Reference document paths and content
- File extensions in the codebase
- Build tool configuration files

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
| Decision Criticality | 1-5   | How costly if a developer guesses wrong?    |
| Knowledge Gap        | 1-5   | How far outside static agent competence?  |

**Priority = (Task Coverage + Decision Criticality + Knowledge Gap) / 3**

- HIGH: >= 4.0
- MEDIUM: >= 2.5
- LOW: < 2.5

---

## Gap Analysis Execution

The team lead performs gap analysis by:

1. **Phase 1**: Identify reference documentation experts from analyzed project docs
2. **Phase 2**: Create methodology experts (ALWAYS created for every project)
3. **Phase 3**: Use an LLM sub-agent to identify domain and left-field experts from the plan
4. **Phase 4**: Merge all expert categories, enforce MAX_EXPERTS limit (default 3) with priority ordering

### Priority Ordering for MAX_EXPERTS Limit

When more than MAX_EXPERTS expert advisors are identified:

1. **Reference experts** - Project docs are foundational
2. **Methodology experts** - Project-specific workflow knowledge
3. **HIGH priority** domain/left-field experts
4. **MEDIUM priority** experts
5. **LOW priority** experts (dropped first)

---

## Output Format

The gap analysis produces a list of expert gaps, each containing:

- `expert_name`: Unique identifier for the expert
- `domain`: Area of expertise
- `description`: What the expert does
- `task_ids`: Which tasks benefit
- `requesting_agents`: Which teammates may ask this expert
- `priority`: HIGH / MEDIUM / LOW
- `obvious_or_leftfield`: reference / methodology / obvious / leftfield
- `keyword_triggers`: Keywords that indicate when to consult this expert

All experts are persisted to `.claude/experts/<plan_slug>/` after prompt generation.

---

## Related Documentation

- [Research Synthesis](research-synthesis.md) - Knowledge gathering
- [Agent Generation](agent-generation/research.md) - Creating agent prompts
- [Expert Creation](../agent-creation/expert-creation/index.md) - Expert templates
- [Expert Creation](../agent-creation/expert-creation/index.md) - Expert creation framework
