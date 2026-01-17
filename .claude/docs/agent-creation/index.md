# Agent Creation Meta-Prompts

**Navigation index for agent creation documentation.** These meta-prompts instruct the orchestrator how to generate
agent prompt files.

---

## Quick Reference

| Agent Type       | Meta-Prompt                                | Purpose                     |
|------------------|--------------------------------------------|-----------------------------|
| Developer        | [developer.md](developer.md)               | Implementation and coding   |
| Critic           | [critic.md](critic.md)                     | Code review and quality     |
| Auditor          | [auditor.md](auditor.md)                   | Verification and acceptance |
| Business Analyst | [business-analyst.md](business-analyst.md) | Requirements expansion      |
| Remediation      | [remediation.md](remediation.md)           | Infrastructure repair       |
| Health Auditor   | [health-auditor.md](health-auditor.md)     | Health verification         |
| Experts          | [expert-creation.md](expert-creation.md)   | Domain-specific experts     |

---

## Agent Subdirectories

Each baseline agent has a subdirectory with detailed sections:

| Agent            | Subdirectory                           | Contents                                      |
|------------------|----------------------------------------|-----------------------------------------------|
| Developer        | [developer/](developer/)               | identity, practices, workflow, signals        |
| Critic           | [critic/](critic/)                     | identity, review-criteria, signals            |
| Auditor          | [auditor/](auditor/)                   | identity, verification, signals               |
| Business Analyst | [business-analyst/](business-analyst/) | identity, expansion                           |
| Remediation      | [remediation/](remediation/)           | identity, practices, signals                  |
| Health Auditor   | [health-auditor/](health-auditor/)     | identity, procedures                          |
| Expert Creation  | [expert-creation/](expert-creation/)   | types, gap-analysis, inputs, prompt-structure |

---

## Supporting Documentation

| Document                                                   | Purpose                           |
|------------------------------------------------------------|-----------------------------------|
| [prompt-engineering-guide.md](prompt-engineering-guide.md) | Quality standards for all prompts |

---

## How Meta-Prompts Work

Meta-prompts are **instructions TO the orchestrator** about how to create agent files. They define:

1. **Inputs** - What research and context the orchestrator provides
2. **Structure** - Required sections for the generated agent file
3. **Transformation** - How to convert research into actionable guidance
4. **Quality checks** - Verification before writing the file

See [meta-prompting.md](../meta-prompting.md) for the full architecture explanation.

---

## Cross-References

- **[Documentation Index](../index.md)** - Navigation hub for all docs
- [Meta-Prompting](../meta-prompting.md) - Two-tier prompt generation system
- [Agent Definitions](../agent-definitions.md) - Agent roles and capabilities
- [Agent Conduct](../agent-conduct.md) - Rules all agents must follow
