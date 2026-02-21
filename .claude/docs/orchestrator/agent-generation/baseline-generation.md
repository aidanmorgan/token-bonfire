# Static Agent Generation

[<- Back to Agent Generation](./index.md)

How the team lead composes agent-specific research for static agents.

**CRITICAL**: Static role definitions (`.claude/agents/*.md`) are pre-existing files with YAML frontmatter and are NOT regenerated at runtime. Static agent generation is about composing agent-specific research that supplements these static definitions, NOT about creating the definition files themselves.

---

## Static Agents

```python
BASELINE_AGENTS = ['developer', 'critic', 'ripple', 'auditor', 'remediation', 'health-auditor']
```

---

## Research Composition Loop

For NEW sessions where `.claude/agents/*.md` files already exist, static agent generation composes agent-specific research. The meta-prompt templates in `.claude/docs/agent-creation/` guide research composition, and the static agent definitions are pre-existing.

For each static agent:

1. **Get agent-specific research** - Filter the broad research for this agent's role
2. **Generate research essay** - Persist findings to `{ARTEFACTS_DIR}/agent-research/{agent-name}.md`
3. **Spawn research-composition sub-agent** - Use `Task()` with:
   - The meta-prompt template from `.claude/docs/agent-creation/{agent-name}.md`
   - The agent-specific research
   - The available experts table
   - Research output path: `{ARTEFACTS_DIR}/agent-research/{agent-name}.md`
4. **Verify research essay** - Check the file exists and contains required sections

The team lead can compose multiple research essays in parallel using background `Task()` calls, up to `MAX_EXPERTS`
concurrent sub-agents.

---

## Final Verification Gate

**CRITICAL**: The task delivery loop MUST NOT start until all agent definitions and research exist.

Verify:

- All expert advisor prompts exist at `.claude/experts/<plan_slug>/[name].md`
- All static agent definitions exist at `.claude/agents/[name].md` (pre-existing, checked into repo)
- Research essays exist at `{ARTEFACTS_DIR}/agent-research/[name].md`

---

## Synchronization Gate

The team lead performs agent generation in a blocking sequence:

1. **PHASE A: GENERATE EXPERTS** - Create all expert prompts first (experts inform static agents)
2. **PHASE B: GENERATE STATIC AGENTS** - Create developer, critic, ripple, auditor, remediation, health-auditor prompts
3. **PHASE C: FINAL VERIFICATION** - Verify all prompts exist and are valid

Only after all three phases complete does the team lead spawn teammates and begin the task loop.

---

## Expert Table Format

The team lead formats the available experts into a table for injection into static agent prompts:

```
| Expert | Domain | Tasks | Delegation Triggers |
|--------|--------|-------|---------------------|
| crypto-expert | Cryptographic protocols | task-2-1, task-2-3 | encryption, key derivation |
| observability-expert | Monitoring and tracing | task-5-1 | logging, metrics |
```

This table is included in each developer, critic, and auditor prompt so they know which expert advisors are available to consult.

---

## Related Documentation

- [Research Infrastructure](./research.md) - How research essays are generated
- [Expert Generation](./expert-generation.md) - Creating specialized experts
- [Developer Template](../../agent-creation/developer/index.md) - Developer agent template
- [Critic Template](../../agent-creation/critic/index.md) - Critic agent template
- [Auditor Template](../../agent-creation/auditor/index.md) - Auditor agent template
- [Remediation Template](../../agent-creation/remediation/index.md) - Remediation agent template
