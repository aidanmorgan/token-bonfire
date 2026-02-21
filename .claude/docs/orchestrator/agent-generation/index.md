# Agent Generation Phase

How the team lead generates all agent prompts before task execution begins.

**CRITICAL**: The team lead MUST generate all agent prompts before task execution begins.

---

## Overview

| Agent Type           | When Generated            | Definition Location                          |
|----------------------|---------------------------|----------------------------------------------|
| **Experts**          | For each gap identified   | `.claude/experts/<plan_slug>/[name].md`      |
| **Developer**        | Always (core role)        | `.claude/agents/developer.md`                |
| **Critic**           | Always (core role)        | `.claude/agents/critic.md`                   |
| **Auditor**          | Always (core role)        | `.claude/agents/auditor.md`                  |
| **Remediation**      | When infra issues arise   | `.claude/agents/remediation.md`              |
| **Business Analyst** | When underspecified tasks | `.claude/agents/business-analyst.md`         |
| **Health Auditor**   | When remediation needed   | `.claude/agents/health-auditor.md`           |

---

## Documentation Structure

This documentation is split into focused sections:

1. **[Research Infrastructure](./research.md)** - How research is gathered, persisted as essays, and synthesized
2. **[Expert Generation](./expert-generation.md)** - Creating specialized domain experts with deep research
3. **[Baseline Generation](./baseline-generation.md)** - Creating static agents with broad research

---

## Quick Reference

### Module-Level Constants

```python
MAX_EXPERTS = 3             # Max parallel expert advisor teammates (from base_variables.md)
AGENTS_DIR = ".claude/agents"
EXPERTS_DIR = ".claude/experts"  # Experts stored per plan slug
AGENT_RESEARCH_DIR = "agent-research"   # Relative to ARTEFACTS_DIR
EXPERT_RESEARCH_DIR = "expert-research" # Relative to ARTEFACTS_DIR
AGENT_CREATION_TIMEOUT_SECONDS = 300  # 5 minutes per agent
POLL_INTERVAL_SECONDS = 2
```

---

## Related Documentation

- [Research Synthesis](../research-synthesis.md) - Knowledge gathering
- [Gap Analysis Procedure](../gap-analysis-procedure.md) - Identifying expert needs
- [Expert Creation](../../agent-creation/expert-creation/index.md) - Expert templates
- [Prompt Engineering Guide](../../agent-creation/prompt-engineering-guide.md) - Quality standards
- [Task Delivery Loop](../../task-delivery-loop.md) - Main execution loop
