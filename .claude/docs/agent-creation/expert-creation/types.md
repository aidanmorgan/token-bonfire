# Expert Types and Core Concepts

**Navigation**: [Expert Creation Index](index.md) | Next: [Gap Analysis](gap-analysis.md)

---

## Overview

Experts are specialist agents created per-plan to fill knowledge gaps that default agents cannot handle.

**Key Principle: Narrower but Deeper**

- **Baseline agents** (Developer, Critic, Auditor): Wide breadth, general depth
- **Experts** (per-plan specialists): Narrow breadth, expert-level depth

**Why Experts Exist**: Baseline agents have broad capabilities but shallow domain knowledge. They can implement code,
review quality, and verify criteria - but they cannot make authoritative judgments in specialized domains. Experts fill
this gap with **deep expertise** that enables:

- **Authoritative decisions** in their domain (not guesses)
- **Expert-level opinions** backed by comprehensive knowledge
- **Pitfall detection** that requires domain mastery to recognize
- **Trade-off evaluation** using nuanced understanding

---

## Key Terms

- **Default agents**: Developer, Critic, Auditor, BA, Remediation, Health Auditor
- **Experts**: Specialist agents created per-plan for **deep** domain expertise

---

## Responsibility Split

| Role               | Responsibilities                                                                 |
|--------------------|----------------------------------------------------------------------------------|
| **Orchestrator**   | Identifies gaps, **deeply researches domain**, creates experts, registers them   |
| **Default agents** | Recognize limitations, delegate to experts when facing domain-specific decisions |
| **Experts**        | Provide **authoritative** advice, **CANNOT delegate further**                    |

---

## Three Types of Experts

The orchestrator creates THREE types of experts, each requiring different prompt structure:

| Expert Type            | Knowledge Source                       | Purpose                                                           |
|------------------------|----------------------------------------|-------------------------------------------------------------------|
| **Domain Expert**      | Web research on technical domain       | Deep expertise in technical areas (crypto, auth, etc.)            |
| **Reference Expert**   | Project documentation analysis         | Authoritative knowledge of project docs (coding standards, specs) |
| **Methodology Expert** | Multiple project documents synthesized | Procedural expertise for THIS project                             |

---

## Domain Experts

Created for technical domains explicitly mentioned in the plan.

**Examples**:

- `crypto-expert` - for plans involving encryption
- `auth-expert` - for plans involving authentication
- `database-expert` - for plans involving complex queries

**Knowledge Source**: Web research on the technical domain

**Purpose**: Provide deep technical expertise that baseline agents lack

---

## Reference Experts

Created for project-specific documentation that requires authoritative interpretation.

**Examples**:

- `coding-standards-expert` - deep knowledge of project coding conventions
- `testing-guidelines-expert` - how to write tests for THIS project
- `api-spec-expert` - authoritative interpretation of API contracts

**Knowledge Source**: Deep analysis of a specific project document

**Purpose**: Become the authoritative interpreter of that document

Reference experts are DIFFERENT: they don't need web research, they need deep analysis of a specific document.

---

## Methodology Experts

Beyond domain and reference experts, the orchestrator creates **methodology experts** - a distinct category that
synthesizes knowledge from MULTIPLE project documents to answer procedural questions about HOW to work in THIS project.

### How Methodology Experts Differ

| Expert Type            | Knowledge Source                       | Knowledge Depth                                    | Questions They Answer                   |
|------------------------|----------------------------------------|----------------------------------------------------|-----------------------------------------|
| **Domain Expert**      | Web research on technical domain       | Deep technical expertise (crypto, auth, databases) | "What's the secure way to implement X?" |
| **Reference Expert**   | ONE specific project document          | Deep knowledge of that single document             | "What does the API spec say about Y?"   |
| **Methodology Expert** | MULTIPLE project documents synthesized | Procedural expertise for THIS project              | "How should I approach doing Z here?"   |

**Key distinction**: Domain and reference experts know WHAT. Methodology experts know HOW TO DO THINGS for THIS project.

### Standard Methodology Expert Types

| Methodology Expert      | Purpose                                          | Source Documents                                                                 | Questions They Answer                                                                                                                      |
|-------------------------|--------------------------------------------------|----------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------|
| **Testing Methodology** | How to write high-quality tests for THIS project | testing-guide, test-standards, CLAUDE.md testing sections, coverage requirements | "What test patterns should I use?", "How do I structure test files?", "What coverage is required?", "How do I test async code here?"       |
| **Coding Standards**    | How to write code conforming to project rules    | coding-standard, style-guide, CLAUDE.md, linter configs                          | "How should I name this variable?", "What patterns are required?", "Is this abstraction level appropriate?", "What imports style is used?" |
| **Test Execution**      | How to run tests in project environment          | ci-cd docs, environment docs, README, Makefile/scripts                           | "How do I run tests locally?", "What commands verify my changes?", "How do I run a single test?", "What's the CI pipeline sequence?"       |
| **Quality Evaluation**  | How to evaluate if work meets quality bar        | quality-guidelines, review-checklist, definition of done                         | "Is this code review-ready?", "Does this meet the quality bar?", "What would reviewers flag?", "Are acceptance criteria met?"              |

### Orchestrator Responsibility for Methodology Experts

The orchestrator analyzes reference documentation tables in the plan to determine which methodology experts are needed:

1. **Scan the plan's reference documentation section** for documents related to:
    - Testing (test guides, test standards, coverage requirements)
    - Coding standards (style guides, naming conventions, patterns)
    - Build/CI (environment setup, test commands, verification steps)
    - Quality (review checklists, acceptance criteria, quality gates)

2. **For each methodology area with relevant documentation**, create an expert that:
    - Reads and deeply analyzes ALL relevant project documents
    - Synthesizes cross-document relationships and implicit conventions
    - Becomes the authority on "how we do X in THIS project"

3. **Register methodology experts** so agents can consult them for procedural questions

### Research Process for Methodology Experts

When creating a methodology expert, the orchestrator performs deep document analysis:

```
METHODOLOGY EXPERT RESEARCH PROCESS:

1. IDENTIFY RELEVANT DOCUMENTS
   - Scan plan's reference documentation table
   - Check for CLAUDE.md sections relevant to methodology
   - Look for implicit documentation (Makefile, configs, examples)

2. DEEP DOCUMENT ANALYSIS
   - Read each document completely
   - Extract explicit rules and requirements
   - Note examples and anti-examples
   - Identify document intent (WHY these rules exist)

3. CROSS-DOCUMENT SYNTHESIS
   - Find relationships between documents
   - Identify implicit conventions (patterns that appear but aren't stated)
   - Resolve conflicts between documents (which takes precedence)
   - Note gaps where judgment is needed

4. PROCEDURAL KNOWLEDGE EXTRACTION
   - Convert declarative rules into procedural guidance
   - Create decision trees for common scenarios
   - Document step-by-step processes
   - Identify gotchas and common mistakes

5. CREATE EXPERT WITH SYNTHESIZED KNOWLEDGE
   - Expert receives the SYNTHESIS, not raw documents
   - Expert can answer procedural questions authoritatively
   - Expert knows BOTH what to do AND why
```

### When to Create Methodology Experts

The orchestrator creates methodology experts when:

1. **Plan involves standard development activities** (testing, coding, building)
2. **Project has documented conventions** that agents must follow
3. **Multiple documents govern the same area** (requiring synthesis)
4. **Quality evaluation requires project-specific criteria**

Methodology experts are ALWAYS created for non-trivial plans because:

- Every project has conventions (even if implicit)
- Getting methodology wrong causes rework
- Synthesized knowledge is more useful than raw documents
- Procedural questions arise constantly during implementation

---

## Researching Existing Expert Prompts

Before creating an expert, the orchestrator researches existing successful expert/specialist prompts:

### Search Queries for Expert Inspiration

| Expert Type        | Research Queries                                                |
|--------------------|-----------------------------------------------------------------|
| Domain Expert      | "domain expert AI prompts", "specialist consultant prompts"     |
| Reference Expert   | "documentation expert prompts", "standards interpreter prompts" |
| Methodology Expert | "best practices advisor prompts", "process expert prompts"      |

### Patterns to Extract

From successful expert prompts, extract:

- How they establish authoritative voice
- How they structure definitive recommendations
- How they handle uncertainty within expertise
- How they frame "cannot help" scenarios

---

## Next Steps

- **Next**: [Gap Analysis](gap-analysis.md) - Identify where default agents need expert support
- **See also**: [Prompt Structure](prompt-structure.md) - Learn how different expert types structure their prompts
