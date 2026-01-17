# Baseline Agent Generation

[← Back to Agent Generation](./index.md)

How the orchestrator generates core agent prompts with broad research.

**CRITICAL**: Each baseline agent receives TAILORED research for their specific role.

---

## Baseline Agents

```python
BASELINE_AGENTS = ['developer', 'critic', 'auditor', 'remediation', 'health-auditor']
```

---

## Generation Loop

```python
def generate_baseline_agent_prompts(experts: list[dict], plan_file: str, config: dict, research: dict, artefacts_dir: str):
    """Generate baseline agent prompts using parallel sub-agents.

    CRITICAL: For each baseline agent, this function:
    1. Performs BROAD research tailored to the agent's role
    2. Generates and persists a research essay documenting all findings
    3. Creates the agent prompt using the research
    4. Verifies the prompt meets quality standards
    """

    os.makedirs(f"{artefacts_dir}/{AGENT_RESEARCH_DIR}", exist_ok=True)

    pending_agents = list(BASELINE_AGENTS)
    active_creators = {}
    created_agents = []
    plan_context = research.get('plan_context', {})

    while pending_agents or active_creators:
        # Fill slots up to ACTIVE_DEVELOPERS
        while len(active_creators) < ACTIVE_DEVELOPERS and pending_agents:
            agent_name = pending_agents.pop(0)

            # Get AGENT-SPECIFIC research
            agent_specific_research = get_research_for_agent(research, agent_name)

            # ═══════════════════════════════════════════════════════════════════
            # CRITICAL: Generate and persist research essay BEFORE creating prompt
            # ═══════════════════════════════════════════════════════════════════
            essay_path = generate_research_essay(
                agent_name=agent_name,
                agent_type='baseline',
                research_data={
                    'agent_role': agent_name,
                    'broad_research': agent_specific_research,
                    'web_searches': research.get('by_agent', {}).get(agent_name, {}).get('web_searches', []),
                    'relevant_docs': research.get('by_agent', {}).get(agent_name, {}).get('relevant_docs', []),
                    'technologies': research.get('technologies', {}),
                    'shared_research': research.get('shared', {}),
                    'available_experts': experts
                },
                plan_context=plan_context,
                artefacts_dir=artefacts_dir
            )

            agent_id = Task(
                subagent_type="developer",
                model="opus",
                run_in_background=True,
                prompt=f"""
Create a baseline agent file.

AGENT TYPE: {agent_name}
OUTPUT FILE: {AGENTS_DIR}/{agent_name}.md

TEMPLATE: {Read(f".claude/docs/agent-creation/{agent_name}.md")}

AVAILABLE EXPERTS: {format_experts_table(experts)}

BEST PRACTICES RESEARCH (TAILORED FOR {agent_name.upper()}):
{agent_specific_research}

RESEARCH ESSAY: {essay_path}
(The full research essay has been persisted - reference it for comprehensive context)
"""
            )
            active_creators[agent_id] = {
                'agent_name': agent_name,
                'essay_path': essay_path,
                'research': agent_specific_research
            }

        # Wait for completions and verify
        if active_creators:
            completed_id, result = await_any_agent(list(active_creators.keys()))
            creator_info = active_creators.pop(completed_id)

            # Verify file exists and is valid
            agent_file = f"{AGENTS_DIR}/{creator_info['agent_name']}.md"
            if os.path.exists(agent_file):
                created_agents.append({
                    'name': creator_info['agent_name'],
                    'file': agent_file,
                    'research_essay': creator_info['essay_path']
                })
                log_event("baseline_agent_created",
                          name=creator_info['agent_name'],
                          file=agent_file,
                          research_essay=creator_info['essay_path'])
            else:
                # Re-queue if file not created
                pending_agents.append(creator_info['agent_name'])

    return created_agents
```

---

## Final Verification Gate

**CRITICAL**: The task delivery loop MUST NOT start until all agents exist.

```python
def verify_agents_created(experts: list[dict]) -> None:
    """Verify all agent files exist on disk and are valid."""

    # Check experts
    for expert in experts:
        if not os.path.exists(expert['file']):
            raise AgentCreationError(f"Expert not created: {expert['name']}")
        content = Read(expert['file'])
        if 'EXPERT_ADVICE' not in content:
            raise AgentCreationError(f"Expert invalid: {expert['name']}")

    # Check baseline agents
    for agent_name in BASELINE_AGENTS:
        if not os.path.exists(f"{AGENTS_DIR}/{agent_name}.md"):
            raise AgentCreationError(f"Baseline agent not created: {agent_name}")
```

---

## Synchronization Gate

```python
def execute_agent_generation_phase(gaps, plan_file, best_practices, artefacts_dir):
    """Generate ALL agent prompts with BLOCKING synchronization."""

    # Write config file
    config = {
        'environments': CONFIG['ENVIRONMENTS'],
        'verification_commands': CONFIG['VERIFICATION_COMMANDS'],
        'best_practices': best_practices,
        'available_experts': [],
    }
    Write(f"{artefacts_dir}/agent-generation-config.json", json.dumps(config))

    # PHASE 5a: GENERATE EXPERTS (BLOCKING)
    experts = generate_expert_prompts(gaps, plan_file, best_practices)

    # Update config with experts
    config['available_experts'] = experts
    Write(f"{artefacts_dir}/agent-generation-config.json", json.dumps(config))

    # PHASE 5b: GENERATE BASELINE AGENTS (BLOCKING)
    generate_baseline_agent_prompts(experts, plan_file, config, best_practices)

    # PHASE 5c: FINAL VERIFICATION
    verify_all_agents_exist()

    return experts
```

---

## Thread Safety

```python
import threading
state_lock = threading.Lock()

# When modifying shared state:
with state_lock:
    active_creators[agent_id] = {...}

with state_lock:
    agent_info = active_creators.pop(completed_id)
```

---

## Polling for Completion

```python
def await_any_agent(agent_ids: list[str]) -> tuple[str, str]:
    """Wait for any one of the given agents to complete."""

    while True:
        for agent_id in agent_ids:
            result = TaskOutput(task_id=agent_id, block=False, timeout=1000)
            if result.status == 'completed':
                return agent_id, result.output
        time.sleep(POLL_INTERVAL_SECONDS)
```

---

## Expert Table Format

```python
def format_experts_table(experts: list[dict]) -> str:
    """Format experts for injection into baseline agent prompts."""

    table = "| Expert | Domain | Tasks | Delegation Triggers |\n"
    table += "|--------|--------|-------|--------------------|\n"

    for expert in experts:
        table += f"| {expert['name']} | {expert['domain']} | {expert['tasks']} | {expert.get('delegation_triggers', [])} |\n"

    return table
```

---

## Related Documentation

- [Research Infrastructure](./research.md) - How research essays are generated
- [Expert Generation](./expert-generation.md) - Creating specialized experts
- [Developer Template](../../agent-creation/developer.md) - Developer agent template
- [Critic Template](../../agent-creation/critic.md) - Critic agent template
- [Auditor Template](../../agent-creation/auditor.md) - Auditor agent template
- [Remediation Template](../../agent-creation/remediation.md) - Remediation agent template
