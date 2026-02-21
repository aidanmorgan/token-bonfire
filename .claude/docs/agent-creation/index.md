# Agent Creation Meta-Prompts

**Navigation index for agent creation documentation.** These meta-prompts instruct the team lead how to generate
agent prompt files.

---

## Quick Reference

| Agent Type       | Meta-Prompt                                        | Purpose                     |
|------------------|----------------------------------------------------|-----------------------------|
| Developer        | [developer/index.md](developer/index.md)           | Implementation and coding   |
| Critic           | [critic/index.md](critic/index.md)                 | Code quality review         |
| Ripple           | *(no meta-prompt — static definition at `.claude/agents/ripple.md`)* | Second-order effects analysis |
| Auditor          | [auditor/index.md](auditor/index.md)               | Acceptance verification     |
| Business Analyst | [business-analyst/index.md](business-analyst/index.md) | Requirements expansion  |
| Remediation      | [remediation/index.md](remediation/index.md)       | Infrastructure repair       |
| Health Auditor   | [health-auditor/index.md](health-auditor/index.md) | Health verification         |
| Expert Advisors  | [expert-creation/index.md](expert-creation/index.md) | Domain-specific advisory  |

---

## Agent Subdirectories

Each agent type has a subdirectory with detailed sections:

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

Meta-prompts are **instructions TO the team lead** about how to create agent prompt files. They define:

1. **Inputs** - What research and context the team lead provides
2. **Structure** - Required sections for the generated agent file
3. **Transformation** - How to convert research into actionable guidance
4. **Quality checks** - Verification before writing the file

See [meta-prompting.md](../meta-prompting.md) for the full architecture explanation.

---

## Cross-References

- **[Documentation Index](../index.md)** - Navigation hub for all docs
- [Meta-Prompting](../meta-prompting.md) - Two-tier prompt generation system
- [Team Architecture](../team-architecture.md) - Team structure and communication
