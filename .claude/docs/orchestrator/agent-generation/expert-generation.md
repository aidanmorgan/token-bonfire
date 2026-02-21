# Expert Prompt Generation

[<- Back to Agent Generation](./index.md)

How the team lead generates specialized domain expert prompts with deep research.

**CRITICAL**: Experts receive DEEPER research than static agents - narrower domain but comprehensive expertise.

---

## Expert Research Routing

The team lead routes research based on expert type:

| Expert Type | Research Approach |
|-------------|-------------------|
| **Reference** | Deep analysis of specific project documentation |
| **Methodology** | Analysis across multiple project docs for procedural knowledge |
| **Domain/Left-field** | Deep web research on the specific domain |

---

## Reference Expert Research

Reference experts need AUTHORITATIVE knowledge of project-specific documentation.

Analysis includes:
1. Document intent (why exists, problems solved)
2. Comprehensive content extraction (every rule, rationale, strictness)
3. Application guidance (how to apply, common misapplication)
4. Edge cases (when rules conflict, precedence)
5. Verification criteria (how to check compliance)
6. Cross-document relationships

---

## Methodology Expert Research

Methodology experts SYNTHESIZE knowledge from MULTIPLE documents.

| Methodology Type | Focus Areas |
|------------------|-------------|
| `testing-methodology` | Test structure, patterns, coverage |
| `coding-standards` | Code style, architecture, error handling |
| `test-execution` | Running tests, environment, CI/CD |
| `quality-evaluation` | Quality gates, review criteria, metrics |

---

## Domain Expert Research

Domain and left-field experts receive deep web research:

- `{domain} comprehensive best practices {year}`
- `{domain} expert-level patterns and techniques`
- `{domain} common pitfalls only experts catch`
- `{domain} decision frameworks and trade-offs`
- `{domain} edge cases and exceptions to standard advice`
- `{domain} misconceptions and corrections`

---

## Expert Creation Loop

For each expert identified by gap analysis, the team lead:

1. **Performs DEEP research** specific to the expert's domain
2. **Generates and persists a research essay** to `{ARTEFACTS_DIR}/expert-research/{expert-name}.md`
3. **Spawns a prompt-creation sub-agent** via `Task()` with:
   - Deep domain research
   - Research essay path for reference
   - Output file path: `.claude/experts/<plan_slug>/{expert-name}.md`
4. **Verifies the created prompt** - Checks the file exists and contains expert-level content

The team lead can create multiple expert prompts in parallel using background `Task()` calls.

After creation, each expert prompt is persisted to `.claude/experts/<plan_slug>/` so it survives session
restarts and can be reused on resume.

---

## Related Documentation

- [Research Infrastructure](./research.md) - How research essays are generated
- [Baseline Generation](./baseline-generation.md) - Creating static agents
- [Expert Creation Template](../../agent-creation/expert-creation/index.md) - Expert prompt templates
- [Gap Analysis](../gap-analysis-procedure.md) - How expert needs are identified
