# Orchestrator Generation

How to bootstrap the Token Bonfire orchestrator with a plan file.

---

## What is the Orchestrator?

The **orchestrator** is the brain of Token Bonfire—a coordinator that transforms a plan file into a running multi-agent
system.

### The Problem It Solves

A single LLM agent can implement code, but struggles with:

- **Consistency**: Following best practices across an entire project
- **Quality gates**: Self-reviewing work objectively
- **Specialization**: Deep expertise in every domain the plan touches
- **Persistence**: Remembering state across long-running sessions

### The Solution: Specialized, Researched Agents

The orchestrator solves this by creating **specialized agents at runtime**:

1. **Researches** the technologies in your plan to gather best practices
2. **Generates** agent prompts tailored to your specific project
3. **Creates experts** for domains where baseline agents lack depth
4. **Coordinates** the workflow: Developer → Critic → Auditor → Complete

Each agent has a focused role with clear boundaries. Developers don't review their own code—Critics do. Critics don't
verify acceptance criteria—Auditors do. This separation creates genuine quality gates.

### Why Research-Driven?

Agents are only as good as their instructions. Instead of static prompts, the orchestrator:

- Researches current best practices for each technology
- Synthesizes this research into agent-specific guidance
- Creates experts for specialized domains

This means a Python project gets Python-specific best practices, not generic advice.

---

## Overview

The orchestrator is the central coordinator that:

1. Analyzes a plan to understand requirements
2. **Generates ALL agent prompts** - both baseline agents and plan-specific experts
3. Manages the task delivery loop
4. Handles state persistence and recovery

**CRITICAL**: The orchestrator GENERATES agent prompts during bootstrap. It does not rely on pre-existing agent
definitions. Each session creates tailored agent definitions based on the specific plan being executed.

---

## Quick Reference

| Need                           | Document                                               |
|--------------------------------|--------------------------------------------------------|
| Research & knowledge synthesis | [research-synthesis.md](research-synthesis.md)         |
| Gap analysis for experts       | [gap-analysis-procedure.md](gap-analysis-procedure.md) |
| Agent prompt generation        | [agent-generation.md](agent-generation.md)             |
| Task quality assessment        | [task-quality.md](task-quality.md)                     |
| State management               | [state-schema.md](state-schema.md)                     |
| Event logging                  | [event-schema.md](event-schema.md)                     |

---

## Core Agents

| Agent           | Role                 | Why Core                         |
|-----------------|----------------------|----------------------------------|
| **Developer**   | Implements tasks     | Primary executor                 |
| **Critic**      | Reviews code quality | Quality gate before audit        |
| **Auditor**     | Formal verification  | Acceptance criteria verification |
| **Remediation** | Fixes infrastructure | Build/test failures              |

These agents are created automatically in both NEW and RESUME flows.

### Non-Core Default Agents

| Agent            | Role               | When Needed          |
|------------------|--------------------|----------------------|
| Business Analyst | Task expansion     | Underspecified tasks |
| Health Auditor   | State verification | Recovery scenarios   |

### Experts

Experts are specialist agents created per-plan to fill gaps.
See [expert-creation.md](../agent-creation/expert-creation.md).

---

## Startup Protocol Summary

| Scenario     | Detection                         | Action                                                                      |
|--------------|-----------------------------------|-----------------------------------------------------------------------------|
| **NEW**      | No state file exists              | Full bootstrap: parse plan, research, generate all agents, capture baseline |
| **RESUME**   | State file exists, clean pause    | Load state, verify agents, continue from last position                      |
| **RECOVERY** | State file exists, no clean pause | Recover state from event log, reconcile orphans, then resume                |

### Decision Tree

1. State file exists?
    - NO → NEW
    - YES → Valid JSON?
        - NO → RECOVERY → then RESUME
        - YES → Clean pause recorded?
            - YES → RESUME
            - NO → RECOVERY → then RESUME
2. Pre-flight validation
    - FAIL → Halt with error
    - PASS → Continue to session-specific flow

### Critical Steps by Session Type

| Step                          | NEW | RESUME             | RECOVERY            |
|-------------------------------|-----|--------------------|---------------------|
| Pre-flight validation         | Yes | Yes                | Yes                 |
| Load state                    | -   | Yes                | Reconstruct         |
| Parse plan                    | Yes | Yes                | Yes                 |
| Research best practices       | Yes | Yes                | Skip (use existing) |
| Gap analysis                  | Yes | Yes (for new gaps) | Skip                |
| Generate ALL agents           | Yes | Missing only       | Missing only        |
| Capture pre-existing baseline | Yes | - (use existing)   | -                   |
| Task quality assessment       | Yes | - (already done)   | -                   |
| Recover orphaned agents       | -   | -                  | Yes                 |
| Begin task loop               | Yes | Yes                | Yes                 |

---

## New Session Flow

**NEW SESSION BOOTSTRAP**:

1. **INITIALIZE STATE** - Create session ID, state file, event log
2. **PARSE PLAN** - Extract tasks, dependencies, technologies, domains
3. **RESEARCH BEST PRACTICES** - WebSearch for technologies in plan
   → See [research-synthesis.md](research-synthesis.md)
4. **GAP ANALYSIS** - Identify where baseline agents need expert support
   → See [gap-analysis-procedure.md](gap-analysis-procedure.md)
5. **AGENT GENERATION PHASE (CRITICAL)** - Generate expert prompts, baseline agent prompts, verify all created
   → See [agent-generation.md](agent-generation.md)
6. **ASSESS TASK QUALITY** - Classify tasks, spawn BA for underspecified ones
   → See [task-quality.md](task-quality.md)
7. **CAPTURE PRE-EXISTING BASELINE** - Run all verification commands before work begins
8. **BEGIN TASK DELIVERY LOOP**
   → See [Task Delivery Loop](../task-delivery-loop.md)

---

## Resume Session Flow

**RESUME SESSION FLOW**:

1. **LOAD STATE** - Load existing state, update session ID
2. **PRE-FLIGHT VALIDATION** - Verify environment is ready
3. **RECOVERY CHECKS** - Validate state consistency
4. **RE-PARSE PLAN** - Plan may have changed since last session
5. **RESEARCH BEST PRACTICES** - Needed for any agent creation/updates
6. **AGENT VERIFICATION & GENERATION** - Verify core agents exist, generate missing, re-run gap analysis
7. **BEGIN TASK DELIVERY LOOP** - Continue from where we left off

---

## Pre-Flight Validation

**CRITICAL**: Before ANY work begins, validate the environment is ready.

| Check                | What                                    | Blocking |
|----------------------|-----------------------------------------|----------|
| Plan file            | Exists and contains required sections   | Yes      |
| Required directories | `.claude/agents`, `.claude/state`, etc. | Yes      |
| Agent templates      | All creation templates exist            | Yes      |
| Verification tools   | Basic tool availability                 | Warning  |
| Environments         | Listed environments accessible          | Warning  |

See [environment-verification.md](../environment-verification.md) for details.

---

## Pre-Existing Failures Baseline

**NEW sessions only**: Capture baseline before any work begins.

This distinguishes:

- Pre-existing failures (existed before we started)
- Task-introduced failures (caused by our work)

See [recovery-procedures.md](../recovery-procedures.md) for baseline handling.

---

## Session Type Detection

```python
def detect_session_type(plan_file: str) -> str:
    """Determine session type: 'NEW' | 'RESUME' | 'RECOVERY'"""

    state_file = get_state_file_path(plan_file)

    if not os.path.exists(state_file):
        return 'NEW'

    try:
        state = json.loads(Read(state_file))

        if state.get('paused_at'):
            return 'RESUME'

        last_event = get_last_event(event_log_file)
        if last_event and last_event.get('event_type') == 'session_pause':
            return 'RESUME'

        return 'RECOVERY'

    except (json.JSONDecodeError, IOError):
        return 'RECOVERY'
```

---

## Main Entry Point

```python
def start_orchestrator(plan_file: str) -> None:
    """Start or resume orchestrator."""

    session_type = detect_session_type(plan_file)

    if session_type == 'RECOVERY':
        state = coordinator_recovery()
        session_type = 'RESUME'

    # Pre-flight validation (both flows)
    pre_flight_results = pre_flight_validation(plan_file, CONFIG)
    if not pre_flight_results['passed']:
        raise PreFlightValidationError(pre_flight_results['blocking_issues'])

    artefacts_dir = get_artefacts_dir(plan_file)

    if session_type == 'RESUME':
        state = load_state(f"{artefacts_dir}/state.json")
        best_practices = get_or_refresh_research(plan_file, artefacts_dir, force_refresh=False)
        ensure_core_agents_exist(best_practices, state.get('experts', []))
    else:
        # NEW: Full bootstrap
        state = initialize_orchestrator(plan_file, artefacts_dir)

        # Research phase
        best_practices = get_or_refresh_research(plan_file, artefacts_dir, force_refresh=True)
        reference_docs = best_practices.get('reference_documentation', {})

        # Gap analysis
        gaps = analyze_gaps(plan_file, reference_docs=reference_docs)

        # Generate all agents
        experts = execute_agent_generation_phase(gaps, plan_file, best_practices, artefacts_dir)
        capture_and_store_baseline(plan_file, CONFIG, state)

    begin_task_loop(state)
```

---

## Directory Structure After Bootstrap

```
.claude/agents/
├── developer.md
├── critic.md
├── auditor.md
├── business-analyst.md
├── remediation.md
├── health-auditor.md
└── experts/
    └── [plan-specific experts].md

.claude/bonfire/[plan-name]/
├── state.json
├── events.jsonl
├── best-practices-research.json
├── agent-research/
│   ├── developer.md          # Long-form research essay for Developer agent
│   ├── critic.md             # Long-form research essay for Critic agent
│   ├── auditor.md            # Long-form research essay for Auditor agent
│   ├── remediation.md        # Long-form research essay for Remediation agent
│   └── health-auditor.md     # Long-form research essay for Health Auditor agent
└── expert-research/
    ├── [expert-name].md      # Long-form research essay for each expert
    ├── crypto-expert.md      # Example: Cryptography expert research
    ├── api-versioning-expert.md  # Example: API versioning expert research
    └── ...
```

### Research Essay Contents

Each research essay in `agent-research/` and `expert-research/` contains:

| Section                          | Purpose                                                                  |
|----------------------------------|--------------------------------------------------------------------------|
| **Executive Summary**            | 2-3 paragraph overview of the agent and its knowledge                    |
| **Research Sources**             | Tables of all project docs, web searches, and codebase patterns analyzed |
| **Knowledge Synthesis**          | Long-form prose synthesizing all sources into coherent guidance          |
| **Project-Specific Adaptations** | How this project differs from standard practices                         |
| **Delegation Guidance**          | (Baseline agents) Which experts to consult and when                      |
| **Quality Criteria**             | What "good" looks like for this agent's outputs                          |
| **Research Gaps**                | Areas where research was limited or assumptions were made                |
| **Raw Research Data**            | Collapsible section with full research transcripts                       |

These essays serve as:

- **Transparency**: Document exactly what knowledge was gathered
- **Debugging**: Understand why an agent behaves a certain way
- **Iteration**: Improve research process based on outcomes
- **Auditability**: Verify research quality and completeness

---

## Related Documentation

### Orchestrator Sub-Documents

- [research-synthesis.md](research-synthesis.md) - Knowledge gathering and synthesis
- [gap-analysis-procedure.md](gap-analysis-procedure.md) - Expert identification
- [agent-generation.md](agent-generation.md) - Agent prompt creation
- [task-quality.md](task-quality.md) - Task assessment
- [state-schema.md](state-schema.md) - State file format
- [event-schema.md](event-schema.md) - Event log format

### External References

- [Task Delivery Loop](../task-delivery-loop.md) - Main execution loop
- [Expert Creation](../agent-creation/expert-creation.md) - Creating expert agents
- [State Management](../state-management.md) - State persistence
- [Recovery Procedures](../recovery-procedures.md) - Error recovery
- [Session Management](../session-management.md) - Pause/resume protocols
- [Environment Verification](../environment-verification.md) - Environment checks
