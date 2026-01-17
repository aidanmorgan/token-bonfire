# Agent Generation Phase

**Navigation Index**: This document has been split into focused sections for better organization.

---

## Documentation Structure

The agent generation documentation is organized into the following sections:

### 1. [Overview and Index](./agent-generation/index.md)

- Quick reference to agent types and output locations
- Module-level constants
- Links to all subsections

### 2. [Research Infrastructure](./agent-generation/research.md)

- Research persistence requirements
- Research essay format and structure
- Research essay generation function
- Quality verification requirements

### 3. [Expert Generation](./agent-generation/expert-generation.md)

- Expert research routing (reference, methodology, domain)
- Deep domain research process
- Expert creation loop with parallel sub-agents
- Expert verification and validation

### 4. [Baseline Agent Generation](./agent-generation/baseline-generation.md)

- Baseline agent list (developer, critic, auditor, etc.)
- Agent-specific research gathering
- Baseline agent creation loop
- Final verification gate and synchronization

---

## Quick Start

**For orchestrator implementation**: Start with the [Overview](./agent-generation/index.md) to understand the complete
flow.

**For research details**: See [Research Infrastructure](./agent-generation/research.md) for essay generation
requirements.

**For expert creation**: See [Expert Generation](./agent-generation/expert-generation.md) for deep research process.

**For baseline agents**: See [Baseline Generation](./agent-generation/baseline-generation.md) for core agent creation.

---

## Critical Requirements

**CRITICAL**: The orchestrator MUST generate all agent prompts before task execution begins.

**CRITICAL**: All research performed during agent creation MUST be persisted as long-form essays.

**CRITICAL**: Every generated agent/expert prompt MUST be verified before being written.

---

## Related Documentation

- [Research Synthesis](./research-synthesis.md) - Knowledge gathering
- [Gap Analysis Procedure](./gap-analysis-procedure.md) - Identifying expert needs
- [Expert Creation](../agent-creation/expert-creation.md) - Expert templates
- [Prompt Engineering Guide](../agent-creation/prompt-engineering-guide.md) - Quality standards
- [Task Delivery Loop](../task-delivery-loop.md) - Main execution loop
