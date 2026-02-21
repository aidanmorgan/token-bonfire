# Research & Knowledge Synthesis

How the team lead gathers and synthesizes knowledge for agent generation.

**CRITICAL**: This step MUST use actual WebSearch to find current best practices. Do NOT rely on static knowledge.

---

## Overview

Before creating agents, the team lead performs comprehensive research to understand:

1. **Plan Context** - What the plan is trying to accomplish
2. **Reference Documentation** - Project-specific docs and standards
3. **Technology Best Practices** - Current practices for technologies in the plan
4. **Existing Prompt Patterns** - Learn from successful agent prompts

---

## Pre-Research Information Synthesis

### Phase 1: Plan Analysis

Analyze the plan to understand scope, domain, and technical requirements:

```
PLAN ANALYSIS:
+-- PROJECT UNDERSTANDING
|   +-- What is being built (product/system/feature)
|   +-- Key domain concepts and terminology
|   +-- Success criteria and quality expectations
|   +-- Implicit requirements and constraints
|
+-- TECHNICAL EXTRACTION
|   +-- Languages and frameworks mentioned
|   +-- Databases and infrastructure
|   +-- External services and integrations
|   +-- Build and deployment tools
|
+-- TASK DECOMPOSITION
    +-- Task dependencies and sequencing
    +-- Complexity assessment per task
    +-- Domain expertise required per task
```

### Phase 2: Reference Documentation Inventory

Identify ALL project reference documentation:

```
REFERENCE DOCUMENTATION:
+-- CODING & DEVELOPMENT (standards, ADRs, API specs, schemas)
+-- QUALITY & TESTING (guidelines, quality gates, checklists)
+-- PROCESS & METHODOLOGY (CI/CD, deployment, troubleshooting)
+-- DOMAIN-SPECIFIC (business rules, security, integrations)
```

### Phase 3: Methodology Expert Determination

| Methodology Expert Type | When to Create                     | Source Documentation              |
|-------------------------|------------------------------------|-----------------------------------|
| Testing Methodology     | Project has specific test patterns | Testing guidelines, test strategy |
| Coding Standards        | Project has detailed style guides  | Style guides, linting rules       |
| Test Execution          | Complex test infrastructure        | CI/CD docs, test runner configs   |
| Quality Evaluation      | Formal quality gates exist         | Quality gate definitions          |

### Phase 4: Existing Prompt Discovery

Search for existing high-quality agent prompts:

```
PROMPT DISCOVERY:
+-- SEARCH LOCATIONS
|   +-- .claude/agents/ directory
|   +-- .claude/docs/agent-creation/ templates
|   +-- WebSearch for published best practices
|
+-- SYNTHESIS APPROACH
    +-- Extract successful patterns
    +-- Identify gaps for current plan
    +-- Adapt and extend for specific needs
```

### Phase 5: Plan Context Synthesis

Create synthesized context for ALL agent prompts:

```
PLAN CONTEXT SYNTHESIS:
+-- PROJECT SUMMARY (one-paragraph, goals, stakeholders)
+-- DOMAIN GLOSSARY (technical terms, business terminology)
+-- CRITICAL CONSTRAINTS (non-negotiable, limitations, timeline)
+-- QUALITY EXPECTATIONS (code quality, testing, documentation)
```

---

## Knowledge Model Philosophy

The system creates fundamentally different types of agents with distinct knowledge requirements.

| Agent Type              | Knowledge Shape          | Research Approach                |
|-------------------------|--------------------------|----------------------------------|
| **Static Agents**       | BROAD general knowledge  | Wide coverage at competent level |
| **Domain Experts**      | DEEP technical expertise | Comprehensive in one area        |
| **Reference Experts**   | DEEP document knowledge  | Authoritative on specific docs   |
| **Methodology Experts** | DEEP process knowledge   | Project-specific workflows       |

---

## Agent Knowledge Model (BROAD)

Static agents need **BROAD general knowledge** enabling them to work across many situations.

**Three Pillars of Agent Knowledge:**

1. **Skill-Specific Knowledge** - Best practices for their primary responsibility
2. **Plan Concept Understanding** - Project goals and domain concepts
3. **Relevant Documentation Awareness** - Project docs filtered by skill relevance

**Distribution by Agent:**

| Agent            | Skill Focus                              | Key Documentation                    |
|------------------|------------------------------------------|--------------------------------------|
| Developer        | Implementation patterns, language idioms | Coding standards, API specs          |
| Critic           | Code quality, review patterns            | Review guidelines, quality gates     |
| Ripple           | Downstream impact, API contracts         | Consumer mappings, dependency graphs |
| Auditor          | Verification, acceptance criteria        | Verification commands, quality gates |
| Remediation      | Debugging, infrastructure fixes          | CI/CD docs, environment configs      |
| Health Auditor   | Health checks, output interpretation     | Verification commands                |
| Business Analyst | Requirements, specification              | Requirements templates               |

---

## Expert Knowledge Model (DEEP)

Experts need **DEEP domain knowledge** making them the authoritative voice.

### Domain Experts

```
DOMAIN EXPERT KNOWLEDGE:
+-- FOUNDATIONAL PRINCIPLES (why this domain works the way it does)
+-- EXPERT-LEVEL PATTERNS (advanced techniques, when to break rules)
+-- EDGE CASES & EXCEPTIONS (when standard advice fails)
+-- DECISION FRAMEWORKS (trade-off analysis, definitive recommendations)
+-- COMMON MISCONCEPTIONS (what generalists get wrong)
```

### Reference Experts

```
REFERENCE EXPERT KNOWLEDGE:
+-- DOCUMENT CONTENT (every section, rationale, implicit conventions)
+-- CROSS-DOCUMENT RELATIONSHIPS (how docs relate, precedence)
+-- APPLICATION GUIDANCE (how to apply in practice, examples)
+-- ENFORCEMENT CRITERIA (violations, strictness, exceptions)
```

### Methodology Experts

```
METHODOLOGY EXPERT KNOWLEDGE:
+-- TESTING METHODOLOGY (project patterns, coverage, CI/CD integration)
+-- CODING STANDARDS (style, linting, naming conventions)
+-- TEST EXECUTION (how to run tests, environment setup)
+-- QUALITY EVALUATION (quality gates, review criteria, definition of done)
```

---

## Technology Extraction

The team lead extracts technologies from the plan content:

- **Languages**: Python, TypeScript, Rust, etc.
- **Frameworks**: React, FastAPI, Django, etc.
- **Databases**: PostgreSQL, MongoDB, Redis, etc.
- **Infrastructure**: Docker, Kubernetes, AWS, etc.
- **Domains**: Cryptography, Authentication, etc.
- **Tools**: pytest, eslint, webpack, etc.

Sources include the tech stack section, task descriptions, acceptance criteria with tool names, and file paths
implying technology.

---

## Web Search Execution

### Agent-Specific Search Templates

**Developer:**

- Design: `{tech} software design patterns {year}`, `{tech} architecture patterns`
- Writing: `{tech} idiomatic code patterns`, `{tech} coding style guide`, `{tech} error handling`
- Testing: `{tech} unit testing best practices`, `{tech} test organization`

**Critic:**

- Quality: `{tech} code review checklist`, `{tech} code quality metrics`
- Architecture: `{tech} design smells`, `{tech} SOLID principles`
- Detection: `{tech} code smells identification`, `{tech} security vulnerability detection`

**Auditor:**

- Verification: `{tech} acceptance testing best practices`, `{tech} verification patterns`
- Criteria: `{tech} acceptance criteria validation`, `{tech} integration testing`

**Remediation:**

- Diagnosis: `{tech} debugging techniques`, `{tech} root cause analysis`
- Fixing: `{tech} common error fixes`, `{tech} build failure resolution`
- Prevention: `{tech} preventing common errors`, `{tech} CI/CD best practices`

**Shared (All Agents):**

- `{tech} security best practices OWASP`, `{tech} common vulnerabilities`

### Retry Logic

WebSearch calls should be retried up to 3 times with a 2-second delay between attempts.

---

## Research Output Format

### Structured Data (JSON)

Store aggregated research in `{{ARTEFACTS_DIR}}/best-practices-research.json`:

```json
{
  "searched_at": "ISO-8601",
  "research_type": "baseline_agent_broad",
  "plan_context": {
    "high_level_goal": "...",
    "problem_being_solved": "...",
    "key_concepts": [{"term": "...", "meaning": "...", "importance": "..."}],
    "critical_success_factors": [{"factor": "...", "why_critical": "..."}],
    "implicit_requirements": [{"requirement": "...", "implication_for_agents": "..."}]
  },
  "by_agent": {
    "developer": {
      "technologies": {
        "Python": {
          "by_category": {
            "design": ["..."],
            "writing": ["..."],
            "testing": ["..."]
          },
          "anti_patterns": ["..."]
        }
      },
      "relevant_docs": [...]
    }
  },
  "shared": {
    "technologies": {
      "Python": {
        "security_considerations": ["..."]
      }
    }
  },
  "reference_documentation": {
    "CLAUDE.md": {
      "document_type": "coding-standard",
      "agent_relevance": {...},
      "expert_recommendation": {...}
    }
  }
}
```

### Long-Form Research Essays (Markdown)

**CRITICAL**: In addition to structured JSON, research MUST be persisted as long-form essays.

| Essay Location                                  | Content                                              |
|-------------------------------------------------|------------------------------------------------------|
| `{{ARTEFACTS_DIR}}/agent-research/[agent].md`   | Comprehensive research essay for each static agent |
| `{{ARTEFACTS_DIR}}/expert-research/[expert].md` | Comprehensive research essay for each expert         |

See [agent-generation/index.md](agent-generation/index.md) for the essay format and generation process.

---

## Injection into Agent Prompts

The team lead injects agent-specific research via `{{BEST_PRACTICES_RESEARCH}}`:

The formatting function produces agent-tailored content from three sources:

1. Plan context (every agent needs to understand the plan)
2. Agent-specific category research (design/writing/testing for developer)
3. Shared security (for developer, critic, and auditor)
4. Agent-relevant documentation

---

## Caching and Reuse

Research is cached in `{{ARTEFACTS_DIR}}/best-practices-research.json`:

| Session Type | Research Behavior                                              |
|--------------|----------------------------------------------------------------|
| NEW          | Always perform fresh research                                  |
| RESUME       | Skip research — static agent definitions are pre-existing      |

---

## Related Documentation

- [Gap Analysis Procedure](gap-analysis-procedure.md) - Identifying expert needs
- [Agent Generation](agent-generation.md) - Creating agent prompts
- [Team Lead Generation](orchestrator-generation.md) - Main bootstrap doc
- [Expert Creation](../agent-creation/expert-creation/index.md) - Expert templates
