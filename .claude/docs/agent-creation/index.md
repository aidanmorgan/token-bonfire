# Agent Creation Meta-Prompts

**Navigation index for agent creation documentation.** These meta-prompts instruct the team lead how to generate
agent prompt files.

---

## Quick Reference

Baseline teammate definitions live in `.claude/agents/*.md` (source of truth). Expert advisor creation uses meta-prompts:

| Agent Type       | Definition / Meta-Prompt                                   | Purpose                       |
|------------------|------------------------------------------------------------|-------------------------------|
| Developer        | `.claude/agents/developer.md`                              | Implementation and coding     |
| Critic           | `.claude/agents/critic.md`                                 | Code quality review           |
| Ripple           | `.claude/agents/ripple.md`                                 | Second-order effects analysis |
| Auditor          | `.claude/agents/auditor.md`                                | Acceptance verification       |
| Business Analyst | `.claude/agents/business-analyst.md`                       | Requirements expansion        |
| Remediation      | `.claude/agents/remediation.md`                            | Infrastructure repair         |
| Health Auditor   | `.claude/agents/health-auditor.md`                         | Health verification           |
| Expert Advisors  | [expert-creation/index.md](expert-creation/index.md)       | Domain-specific advisory      |

---

## Expert Creation Subdirectory

Expert advisor prompts are generated per-plan via meta-prompts:

| Subdirectory                                         | Contents                                      |
|------------------------------------------------------|-----------------------------------------------|
| [expert-creation/](expert-creation/)                 | types, gap-analysis, inputs, prompt-structure |

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
- [Communication Protocol](../communication-protocol.md) - SendMessage API and signal reference
