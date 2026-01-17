# Agent Generation Phase

How the orchestrator generates all agent prompts before task execution begins.

**CRITICAL**: The orchestrator MUST generate all agent prompts before task execution begins.

---

## Overview

| Agent Type           | When Generated            | Output Location                      |
|----------------------|---------------------------|--------------------------------------|
| **Experts**          | For each gap identified   | `.claude/agents/experts/[name].md`   |
| **Developer**        | Always (core agent)       | `.claude/agents/developer.md`        |
| **Critic**           | Always (core agent)       | `.claude/agents/critic.md`           |
| **Auditor**          | Always (core agent)       | `.claude/agents/auditor.md`          |
| **Remediation**      | Always (core agent)       | `.claude/agents/remediation.md`      |
| **Business Analyst** | When underspecified tasks | `.claude/agents/business-analyst.md` |
| **Health Auditor**   | When remediation needed   | `.claude/agents/health-auditor.md`   |

---

## Documentation Structure

This documentation is split into focused sections:

1. **[Research Infrastructure](./research.md)** - How research is gathered, persisted as essays, and synthesized
2. **[Expert Generation](./expert-generation.md)** - Creating specialized domain experts with deep research
3. **[Baseline Generation](./baseline-generation.md)** - Creating core agents with broad research

---

## Quick Reference

### Module-Level Constants

```python
ACTIVE_DEVELOPERS = 3       # Max parallel agent creation sub-agents
AGENTS_DIR = ".claude/agents"
EXPERTS_DIR = ".claude/agents/experts"
AGENT_RESEARCH_DIR = "agent-research"   # Relative to ARTEFACTS_DIR
EXPERT_RESEARCH_DIR = "expert-research" # Relative to ARTEFACTS_DIR
AGENT_CREATION_TIMEOUT_SECONDS = 300  # 5 minutes per agent
POLL_INTERVAL_SECONDS = 2
```

---

## Related Documentation

- [Research Synthesis](../research-synthesis.md) - Knowledge gathering
- [Gap Analysis Procedure](../gap-analysis-procedure.md) - Identifying expert needs
- [Expert Creation](../../agent-creation/expert-creation.md) - Expert templates
- [Prompt Engineering Guide](../../agent-creation/prompt-engineering-guide.md) - Quality standards
- [Task Delivery Loop](../../task-delivery-loop.md) - Main execution loop
