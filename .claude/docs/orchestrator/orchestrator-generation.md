# Orchestrator Generation

This document describes how to bootstrap the Token Bonfire orchestrator with a plan file.

## Overview

The orchestrator is the central coordinator that:

1. Analyzes a plan to understand requirements
2. **Generates ALL agent prompts** - both baseline agents and plan-specific experts
3. Manages the task delivery loop
4. Handles state persistence and recovery

**CRITICAL**: The orchestrator GENERATES agent prompts during bootstrap. It does not rely on pre-existing agent
definitions. Each session creates tailored agent definitions based on the specific plan being executed.

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

```
start_orchestrator(plan_file)
    │
    ├─ State file exists?
    │   │
    │   ├─ YES → Valid JSON?
    │   │         │
    │   │         ├─ YES → Clean pause recorded?
    │   │         │         │
    │   │         │         ├─ YES → RESUME
    │   │         │         │
    │   │         │         └─ NO → RECOVERY → then RESUME
    │   │         │
    │   │         └─ NO → RECOVERY → then RESUME
    │   │
    │   └─ NO → NEW
    │
    ▼
    Pre-flight validation
    │
    ├─ FAIL → Halt with error
    │
    └─ PASS → Continue to session-specific flow
```

### Critical Steps by Session Type

| Step                          | NEW | RESUME           | RECOVERY            |
|-------------------------------|-----|------------------|---------------------|
| Pre-flight validation         | ✓   | ✓                | ✓                   |
| Load state                    | -   | ✓                | Reconstruct         |
| Parse plan                    | ✓   | ✓                | ✓                   |
| Research best practices       | ✓   | ✓                | Skip (use existing) |
| Gap analysis                  | ✓   | ✓ (for new gaps) | Skip                |
| Generate ALL agents           | ✓   | Missing only     | Missing only        |
| Capture pre-existing baseline | ✓   | - (use existing) | - (use existing)    |
| Task quality assessment       | ✓   | - (already done) | -                   |
| Recover orphaned agents       | -   | -                | ✓                   |
| Begin task loop               | ✓   | ✓                | ✓                   |

---

## New Session Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    NEW SESSION BOOTSTRAP                         │
├─────────────────────────────────────────────────────────────────┤
│  1. INITIALIZE STATE                                             │
│     - Create session ID, state file, event log                   │
│     ↓                                                            │
│  2. PARSE PLAN                                                   │
│     - Extract tasks, dependencies, technologies, domains         │
│     ↓                                                            │
│  3. RESEARCH BEST PRACTICES                                      │
│     - WebSearch for technologies in plan                         │
│     ↓                                                            │
│  4. GAP ANALYSIS                                                 │
│     - Identify where baseline agents need expert support         │
│     ↓                                                            │
│  ╔═════════════════════════════════════════════════════════════╗ │
│  ║  5. AGENT GENERATION PHASE ★★★ (CRITICAL)                   ║ │
│  ║     - Generate expert prompts for identified gaps            ║ │
│  ║     - Generate baseline agent prompts with injected context  ║ │
│  ║     - Verify all agents created                              ║ │
│  ╚═════════════════════════════════════════════════════════════╝ │
│     ↓                                                            │
│  6. ASSESS TASK QUALITY                                          │
│     - Classify tasks, spawn BA for underspecified ones           │
│     ↓                                                            │
│  7. CAPTURE PRE-EXISTING BASELINE                                │
│     - Run all verification commands before work begins           │
│     ↓                                                            │
│  8. BEGIN TASK DELIVERY LOOP                                     │
└─────────────────────────────────────────────────────────────────┘
```

---

## Best Practices Research (Step 3)

**CRITICAL**: This step MUST use actual WebSearch to find current best practices. Do NOT rely on static knowledge.

### Purpose

Agents perform better when given current, technology-specific guidance. This step:

1. Extracts technologies mentioned in the plan
2. Performs web searches for current best practices
3. Structures findings for injection into agent prompts

### Technology Extraction

```python
def extract_technologies_from_plan(plan_content: str) -> dict:
    """Extract technologies, frameworks, and domains from plan."""

    technologies = {
        'languages': [],      # Python, TypeScript, Rust, etc.
        'frameworks': [],     # React, FastAPI, Django, etc.
        'databases': [],      # PostgreSQL, MongoDB, Redis, etc.
        'infrastructure': [], # Docker, Kubernetes, AWS, etc.
        'domains': [],        # Cryptography, Authentication, etc.
        'tools': []           # pytest, eslint, webpack, etc.
    }

    # Extract from:
    # - Tech stack section
    # - Task descriptions mentioning specific technologies
    # - Acceptance criteria with tool names
    # - File paths implying technology (.py, .ts, .rs, etc.)

    return technologies
```

### Web Search Execution

**MUST use WebSearch tool** for each technology category:

```python
# WebSearch retry and fallback constants
WEBSEARCH_RETRY_LIMIT = 3
WEBSEARCH_RETRY_DELAY_SECONDS = 2

def research_best_practices(technologies: dict) -> dict:
    """Perform web searches for current best practices.

    CRITICAL: Includes error handling for WebSearch failures.
    Falls back to cached/static knowledge if all searches fail.
    """

    research_results = {
        'searched_at': datetime.now().isoformat(),
        'technologies': {},
        'general_patterns': {},
        'search_failures': []  # Track any failed searches
    }

    current_year = datetime.now().year

    for category, tech_list in technologies.items():
        for tech in tech_list:
            # Perform actual web search
            search_queries = [
                f"{tech} best practices {current_year}",
                f"{tech} common mistakes to avoid",
                f"{tech} production patterns"
            ]

            tech_research = {
                'best_practices': [],
                'anti_patterns': [],
                'security_considerations': [],
                'sources': [],
                'search_succeeded': True
            }

            for query in search_queries:
                # ═══════════════════════════════════════════════════════════
                # WebSearch with retry and error handling
                # ═══════════════════════════════════════════════════════════
                results = None
                last_error = None

                for attempt in range(WEBSEARCH_RETRY_LIMIT):
                    try:
                        results = WebSearch(query=query)
                        break  # Success - exit retry loop
                    except Exception as e:
                        last_error = str(e)
                        log_event("websearch_retry",
                                  query=query,
                                  attempt=attempt + 1,
                                  error=last_error)
                        if attempt < WEBSEARCH_RETRY_LIMIT - 1:
                            time.sleep(WEBSEARCH_RETRY_DELAY_SECONDS)

                if results is None:
                    # All retries failed - log and continue
                    research_results['search_failures'].append({
                        'query': query,
                        'tech': tech,
                        'error': last_error or 'Unknown error'
                    })
                    tech_research['search_succeeded'] = False
                    log_event("websearch_failed",
                              query=query,
                              tech=tech,
                              error=last_error)
                    continue  # Skip to next query

                # Extract actionable guidance from results
                try:
                    tech_research['sources'].append({
                        'query': query,
                        'results_summary': summarize_search_results(results)
                    })

                    # Parse best practices from search results
                    practices = extract_practices_from_results(results)
                    tech_research['best_practices'].extend(practices['do'])
                    tech_research['anti_patterns'].extend(practices['dont'])
                except Exception as e:
                    log_event("websearch_parse_error",
                              query=query,
                              error=str(e))

            research_results['technologies'][tech] = tech_research

    # ═══════════════════════════════════════════════════════════════════════
    # Fallback: If ALL searches failed, use static fallback
    # ═══════════════════════════════════════════════════════════════════════
    if all(not t.get('search_succeeded', False)
           for t in research_results['technologies'].values()):
        log_event("websearch_total_failure",
                  tech_count=len(research_results['technologies']),
                  fallback="static_knowledge")

        # Add warning to results
        research_results['WARNING'] = (
            "All web searches failed. Using static knowledge only. "
            "Agents may have outdated best practices information."
        )

    return research_results
```

### Search Query Templates

| Technology Type | Search Queries                                                                                        |
|-----------------|-------------------------------------------------------------------------------------------------------|
| Language        | `"[lang] best practices [year]"`, `"[lang] idiomatic code patterns"`, `"[lang] common pitfalls"`      |
| Framework       | `"[framework] best practices [year]"`, `"[framework] production tips"`, `"[framework] anti-patterns"` |
| Database        | `"[db] query optimization"`, `"[db] schema design best practices"`, `"[db] connection pooling"`       |
| Security        | `"[domain] security best practices OWASP"`, `"[domain] common vulnerabilities"`                       |
| Testing         | `"[tool] testing best practices"`, `"[tool] test organization patterns"`                              |

### Research Output Format

Store research in `{{ARTEFACTS_DIR}}/best-practices-research.json`:

```json
{
  "searched_at": "2025-01-16T10:30:00Z",
  "plan_file": "IMPLEMENTATION_PLAN.md",
  "technologies": {
    "Python": {
      "best_practices": [
        "Use type hints for all function signatures",
        "Prefer pathlib over os.path for file operations",
        "Use dataclasses or Pydantic for data structures"
      ],
      "anti_patterns": [
        "Mutable default arguments",
        "Bare except clauses",
        "Global state mutation"
      ],
      "security_considerations": [
        "Never use eval() or exec() with user input",
        "Use secrets module for cryptographic randomness",
        "Validate and sanitize all external input"
      ],
      "sources": [
        {"query": "Python best practices 2025", "url": "..."}
      ]
    },
    "FastAPI": {
      "best_practices": [
        "Use dependency injection for shared resources",
        "Define Pydantic models for request/response validation",
        "Use async endpoints for I/O-bound operations"
      ],
      "anti_patterns": [
        "Blocking calls in async endpoints",
        "Circular imports between routers"
      ],
      "security_considerations": [
        "Always validate path parameters",
        "Use OAuth2 with JWT for authentication"
      ],
      "sources": [...]
    }
  },
  "cross_cutting": {
    "error_handling": ["Use structured logging", "Include correlation IDs"],
    "testing": ["Aim for 80%+ coverage on critical paths"],
    "documentation": ["Document public APIs with examples"]
  }
}
```

### Injection into Agent Prompts

The orchestrator injects research into agent prompts via the `{{BEST_PRACTICES_FROM_RESEARCH}}` template variable:

```python
def format_best_practices_for_agent(research: dict, agent_type: str) -> str:
    """Format research results for injection into agent prompt."""

    sections = []

    for tech, data in research['technologies'].items():
        section = f"## {tech}\n\n"

        if data['best_practices']:
            section += "**DO:**\n"
            for practice in data['best_practices']:
                section += f"- {practice}\n"

        if data['anti_patterns']:
            section += "\n**DON'T:**\n"
            for anti in data['anti_patterns']:
                section += f"- {anti}\n"

        if agent_type in ('developer', 'critic') and data['security_considerations']:
            section += "\n**SECURITY:**\n"
            for sec in data['security_considerations']:
                section += f"- {sec}\n"

        sections.append(section)

    return "\n\n".join(sections)
```

### Caching and Reuse

Research is cached in the **plan artefact directory**: `{{ARTEFACTS_DIR}}/best-practices-research.json`

This keeps research co-located with plan-specific state and artefacts.

- **NEW sessions**: Always perform fresh research
- **RESUME sessions**: Reuse existing research if < 24 hours old
- **RECOVERY sessions**: Reuse existing research (no network dependency)

```python
def get_or_refresh_research(plan_file: str, artefacts_dir: str, force_refresh: bool = False) -> dict:
    """Get cached research or perform fresh search."""

    cache_file = f"{artefacts_dir}/best-practices-research.json"

    if not force_refresh and os.path.exists(cache_file):
        cached = json.loads(Read(cache_file))
        cached_at = datetime.fromisoformat(cached['searched_at'])

        if datetime.now() - cached_at < timedelta(hours=24):
            log_event("best_practices_cache_hit",
                      cached_at=cached['searched_at'],
                      technologies=list(cached['technologies'].keys()))
            return cached

    # Perform fresh research using WebSearch
    technologies = extract_technologies_from_plan(Read(plan_file))
    research = research_best_practices(technologies)

    # Cache in plan artefact directory
    Write(cache_file, json.dumps(research, indent=2))
    log_event("best_practices_researched",
              technologies=list(research['technologies'].keys()),
              cached_to=cache_file)

    return research
```

### Artefact Directory Structure

```
{{ARTEFACTS_DIR}}/
├── best-practices-research.json    # Cached web search results
├── state.json                      # Coordinator state
├── events.jsonl                    # Event log
├── task-1-1/                       # Per-task artefacts
│   └── context-snapshot.md
└── ...
```

---

## Resume Session Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    RESUME SESSION FLOW                           │
├─────────────────────────────────────────────────────────────────┤
│  1. LOAD STATE                                                   │
│     - Load existing state, update session ID                     │
│     ↓                                                            │
│  2. PRE-FLIGHT VALIDATION                                        │
│     - Verify environment is ready                                │
│     ↓                                                            │
│  3. RECOVERY CHECKS                                              │
│     - Validate state consistency                                 │
│     ↓                                                            │
│  4. RE-PARSE PLAN                                                │
│     - Plan may have changed since last session                   │
│     ↓                                                            │
│  5. RESEARCH BEST PRACTICES                                      │
│     - Needed for any agent creation/updates                      │
│     ↓                                                            │
│  ╔═════════════════════════════════════════════════════════════╗ │
│  ║  6. AGENT VERIFICATION & GENERATION ★★★                     ║ │
│  ║     - Verify core agents exist, generate any missing         ║ │
│  ║     - Re-run gap analysis for new gaps                       ║ │
│  ║     - Generate new expert prompts                            ║ │
│  ║     - Update baseline agents with new expert awareness       ║ │
│  ╚═════════════════════════════════════════════════════════════╝ │
│     ↓                                                            │
│  7. BEGIN TASK DELIVERY LOOP                                     │
│     - Continue from where we left off                            │
└─────────────────────────────────────────────────────────────────┘
```

---

## Agent Generation Phase

**The orchestrator MUST generate all agent prompts before task execution begins.**

### Module-Level Constants

```python
# ═══════════════════════════════════════════════════════════════════════════════
# CONSTANTS - Define these at module level before any functions
# ═══════════════════════════════════════════════════════════════════════════════

import os
import json
import time
import threading
from datetime import datetime, timedelta

# Concurrency control
ACTIVE_DEVELOPERS = 3  # Max parallel agent creation sub-agents (matches task delivery)

# Directory paths
AGENTS_DIR = ".claude/agents"
EXPERTS_DIR = ".claude/agents/experts"

# Timeouts
AGENT_CREATION_TIMEOUT_SECONDS = 300  # 5 minutes per agent
POLL_INTERVAL_SECONDS = 2

# Thread safety for parallel operations
state_lock = threading.Lock()

# Configuration object - loaded from plan or defaults
CONFIG = {
    'ENVIRONMENTS': [],           # Populated from plan analysis
    'VERIFICATION_COMMANDS': [],  # Populated from plan analysis
    'MAX_RETRIES': 3,
    'TIMEOUT_MINUTES': 30
}

def initialize_config_from_plan(plan_file: str, artefacts_dir: str) -> dict:
    """Initialize CONFIG from plan analysis. Call at startup."""
    global CONFIG

    plan_content = Read(plan_file)

    CONFIG['ENVIRONMENTS'] = extract_environments_from_plan(plan_content)
    CONFIG['VERIFICATION_COMMANDS'] = extract_verification_commands(plan_content)
    CONFIG['ARTEFACTS_DIR'] = artefacts_dir

    return CONFIG
```

### What Gets Generated

| Agent Type           | When Generated                      | Output Location                      |
|----------------------|-------------------------------------|--------------------------------------|
| **Experts**          | For each gap identified in analysis | `.claude/agents/experts/[name].md`   |
| **Developer**        | Always (core agent)                 | `.claude/agents/developer.md`        |
| **Critic**           | Always (core agent)                 | `.claude/agents/critic.md`           |
| **Auditor**          | Always (core agent)                 | `.claude/agents/auditor.md`          |
| **Remediation**      | Always (core agent)                 | `.claude/agents/remediation.md`      |
| **Business Analyst** | When underspecified tasks exist     | `.claude/agents/business-analyst.md` |
| **Health Auditor**   | When remediation is needed          | `.claude/agents/health-auditor.md`   |

### Quality Verification Requirement

**CRITICAL**: Every generated agent/expert prompt MUST be verified before being written.

```
┌─────────────────────────────────────────────────────────────┐
│           PROMPT GENERATION FLOW (Per Agent)                │
├─────────────────────────────────────────────────────────────┤
│  1. Load template + injection context                       │
│     ↓                                                       │
│  2. Generate initial prompt                                 │
│     ↓                                                       │
│  3. Invoke /verify-prompt skill ★                           │
│     ↓                                                       │
│  4. Apply CRITICAL + HIGH recommendations ★                 │
│     ↓                                                       │
│  5. Write revised prompt to file                            │
│     ↓                                                       │
│  6. Log: prompt_quality_verified=True                       │
└─────────────────────────────────────────────────────────────┘
```

See [prompt-engineering-guide.md](../agent-creation/prompt-engineering-guide.md) for quality standards.

### Generation Process Overview

```python
def execute_agent_generation_phase(gaps, plan_file, best_practices, artefacts_dir):
    """Generate ALL agent prompts."""

    # ═══════════════════════════════════════════════════════════════════════
    # CRITICAL: Create ALL required directories BEFORE any file writes
    # ═══════════════════════════════════════════════════════════════════════
    os.makedirs(AGENTS_DIR, exist_ok=True)
    os.makedirs(EXPERTS_DIR, exist_ok=True)
    os.makedirs(artefacts_dir, exist_ok=True)

    log_event("directories_created",
              agents_dir=AGENTS_DIR,
              experts_dir=EXPERTS_DIR,
              artefacts_dir=artefacts_dir)

    # Write config file for sub-agents to read (in artefacts dir)
    config = {
        'environments': CONFIG['ENVIRONMENTS'],
        'verification_commands': CONFIG['VERIFICATION_COMMANDS'],
        'best_practices': best_practices,
        'available_experts': [],
    }
    Write(f"{artefacts_dir}/agent-generation-config.json", json.dumps(config))

    # Phase 5a: Generate expert prompts
    experts = generate_expert_prompts(gaps, plan_file)

    # Update config with created experts
    config['available_experts'] = experts
    Write(f"{artefacts_dir}/agent-generation-config.json", json.dumps(config))

    # Phase 5b: Generate baseline agent prompts
    generate_baseline_agent_prompts(experts, plan_file, config_file)

    # Phase 5c: Verify all agents created
    verify_agents_created(experts)

    return experts
```

Sub-agents read templates and config files directly—no string concatenation needed.

### Expert Prompt Generation (Phase 5a)

**CRITICAL**: Expert prompts MUST be written to `.claude/agents/experts/` directory.

**CRITICAL**: Orchestrator maintains up to `{{ACTIVE_DEVELOPERS}}` parallel sub-agents creating experts.

```python
EXPERTS_DIR = ".claude/agents/experts"

def generate_expert_prompts(gaps: list[dict], plan_file: str, best_practices: dict) -> list[dict]:
    """Generate expert agent prompts using parallel sub-agents.

    Maintains {{ACTIVE_DEVELOPERS}} concurrent creation sub-agents.
    Waits for ALL experts to be created before returning.
    """

    os.makedirs(EXPERTS_DIR, exist_ok=True)

    output(f"CREATING {len(gaps)} EXPERT AGENTS (max {ACTIVE_DEVELOPERS} parallel)...")
    output("=" * 60)

    # Work queues
    pending_gaps = list(gaps)          # Gaps not yet dispatched
    active_creators = {}               # agent_id -> expert_info
    created_experts = []               # Successfully created experts

    # ═══════════════════════════════════════════════════════════════════════
    # PARALLEL CREATION LOOP - Maintain {{ACTIVE_DEVELOPERS}} active creators
    # ═══════════════════════════════════════════════════════════════════════

    while pending_gaps or active_creators:

        # Fill slots up to ACTIVE_DEVELOPERS
        while len(active_creators) < ACTIVE_DEVELOPERS and pending_gaps:
            gap = pending_gaps.pop(0)
            expert_name = gap['expert_name']
            expert_file = f"{EXPERTS_DIR}/{expert_name}.md"

            output(f"  [{len(active_creators)+1}/{ACTIVE_DEVELOPERS}] Dispatching: {expert_name}")

            # Prepare context
            template = Read(".claude/docs/agent-creation/expert-creation.md")
            domain_research = research_domain_best_practices(gap['domain'])

            # ═══════════════════════════════════════════════════════════════
            # THREAD-SAFE: Update active_creators under lock before dispatch
            # ═══════════════════════════════════════════════════════════════

            # Dispatch sub-agent in background
            agent_id = Task(
                subagent_type="developer",
                model="opus",
                run_in_background=True,  # Non-blocking dispatch
                prompt=f"""
You are creating an expert agent file. Write it directly to disk.

EXPERT NAME: {expert_name}
OUTPUT FILE: {expert_file}

TEMPLATE:
{template}

GAP BEING FILLED: {gap['description']}
TASKS NEEDING THIS EXPERT: {gap['task_ids']}
AGENTS WHO WILL ASK: {gap['requesting_agents']}

BEST PRACTICES FOR THIS DOMAIN:
{format_research(domain_research)}

SIGNAL SPECIFICATION:
{Read(".claude/docs/signal-specification.md")}

INSTRUCTIONS:
1. Create a complete expert agent markdown file following the template
2. Use the Write tool to save it to: {expert_file}
3. The file must be self-contained and production-ready

When done, output: EXPERT_CREATED: {expert_name}
"""
            )

            with state_lock:
                active_creators[agent_id] = {
                    'name': expert_name,
                    'file': expert_file,
                    'domain': gap['domain'],
                    'tasks': gap['task_ids'],
                    'requesting_agents': gap['requesting_agents'],
                    'capabilities': gap.get('capabilities', []),  # REQUIRED: What this expert can do
                    'delegation_triggers': gap.get('delegation_triggers', {}),  # When to delegate
                    'dispatched_at': datetime.now().isoformat()
                }

            log_event("expert_creation_dispatched",
                      expert_name=expert_name,
                      active_creators=len(active_creators),
                      pending=len(pending_gaps))

        # Wait for at least one creator to complete
        if active_creators:
            completed_id, result = await_any_agent(list(active_creators.keys()))

            # ═══════════════════════════════════════════════════════════════
            # THREAD-SAFE: Use state_lock when modifying shared state
            # ═══════════════════════════════════════════════════════════════
            with state_lock:
                expert_info = active_creators.pop(completed_id)

            # Verify file was written
            if os.path.exists(expert_info['file']):
                content = Read(expert_info['file'])
                if len(content) >= 100 and 'EXPERT_ADVICE' in content:
                    output(f"  ✓ {expert_info['name']} created ({len(pending_gaps)} pending, {len(active_creators)} active)")
                    created_experts.append(expert_info)

                    log_event("expert_created",
                              expert_name=expert_info['name'],
                              file_path=expert_info['file'])
                else:
                    output(f"  ✗ {expert_info['name']} INVALID - re-queuing")
                    pending_gaps.append({
                        'expert_name': expert_info['name'],
                        'domain': expert_info['domain'],
                        'task_ids': expert_info['tasks'],
                        'requesting_agents': expert_info['requesting_agents'],
                        'capabilities': expert_info.get('capabilities', []),
                        'delegation_triggers': expert_info.get('delegation_triggers', {}),
                        'description': expert_info['domain']
                    })
            else:
                output(f"  ✗ {expert_info['name']} NOT WRITTEN - re-queuing")
                pending_gaps.append({
                    'expert_name': expert_info['name'],
                    'domain': expert_info['domain'],
                    'task_ids': expert_info['tasks'],
                    'requesting_agents': expert_info['requesting_agents'],
                    'capabilities': expert_info.get('capabilities', []),
                    'delegation_triggers': expert_info.get('delegation_triggers', {}),
                    'description': expert_info['domain']
                })

    # ═══════════════════════════════════════════════════════════════════════
    # VERIFY ALL EXPERTS
    # ═══════════════════════════════════════════════════════════════════════

    output("")
    output("VERIFYING ALL EXPERT FILES...")
    verify_experts_created(created_experts)

    output(f"✓ ALL {len(created_experts)} EXPERTS CREATED SUCCESSFULLY")
    output("=" * 60)

    return created_experts


def await_any_agent(agent_ids: list[str]) -> tuple[str, str]:
    """Wait for any one of the given agents to complete. Return (agent_id, result)."""

    while True:
        for agent_id in agent_ids:
            result = TaskOutput(task_id=agent_id, block=False, timeout=1000)
            if result.status == 'completed':
                return agent_id, result.output
        time.sleep(2)  # Poll interval


def verify_experts_created(experts: list[dict]) -> None:
    """Verify all expert files exist on disk and are valid."""

    missing = []
    invalid = []

    for expert in experts:
        if not os.path.exists(expert['file']):
            missing.append(expert['name'])
        else:
            content = Read(expert['file'])
            if 'EXPERT_ADVICE' not in content or 'EXPERT_UNSUCCESSFUL' not in content:
                invalid.append(f"{expert['name']} (missing signal formats)")

    if missing:
        raise AgentCreationError(f"Expert files not created: {missing}")

    if invalid:
        raise AgentCreationError(f"Expert files invalid: {invalid}")

    log_event("experts_verified",
              expert_count=len(experts),
              expert_files=[e['file'] for e in experts])
```

### Baseline Agent Generation (Phase 5b)

**CRITICAL**: Orchestrator maintains up to `{{ACTIVE_DEVELOPERS}}` parallel sub-agents creating baseline agents.

```python
AGENTS_DIR = ".claude/agents"
BASELINE_AGENTS = ['developer', 'critic', 'auditor', 'remediation', 'health-auditor']

def generate_baseline_agent_prompts(experts: list[dict], plan_file: str, config: dict) -> None:
    """Generate baseline agent prompts using parallel sub-agents.

    Maintains {{ACTIVE_DEVELOPERS}} concurrent creation sub-agents.
    Waits for ALL baseline agents to be created before returning.
    """

    output("")
    output(f"CREATING {len(BASELINE_AGENTS)} BASELINE AGENTS (max {ACTIVE_DEVELOPERS} parallel)...")
    output("=" * 60)

    # Work queues
    pending_agents = list(BASELINE_AGENTS)  # Agent names not yet dispatched
    active_creators = {}                     # agent_id -> agent_info
    created_agents = []                      # Successfully created agents

    # ═══════════════════════════════════════════════════════════════════════
    # PARALLEL CREATION LOOP - Maintain {{ACTIVE_DEVELOPERS}} active creators
    # ═══════════════════════════════════════════════════════════════════════

    while pending_agents or active_creators:

        # Fill slots up to ACTIVE_DEVELOPERS
        while len(active_creators) < ACTIVE_DEVELOPERS and pending_agents:
            agent_name = pending_agents.pop(0)
            agent_file = f"{AGENTS_DIR}/{agent_name}.md"

            output(f"  [{len(active_creators)+1}/{ACTIVE_DEVELOPERS}] Dispatching: {agent_name}")

            template = Read(f".claude/docs/agent-creation/{agent_name}.md")

            # Dispatch sub-agent in background
            agent_id = Task(
                subagent_type="developer",
                model="opus",
                run_in_background=True,  # Non-blocking dispatch
                prompt=f"""
You are creating a baseline agent file. Write it directly to disk.

AGENT TYPE: {agent_name}
OUTPUT FILE: {agent_file}

TEMPLATE:
{template}

AVAILABLE EXPERTS (include in agent's expert awareness section):
{format_experts_table(experts)}

BEST PRACTICES:
{config['best_practices']}

VERIFICATION COMMANDS:
{config['verification_commands']}

ENVIRONMENTS:
{config['environments']}

PLAN:
{Read(plan_file)}

INSTRUCTIONS:
1. Create a complete {agent_name} agent markdown file following the template
2. Include the available experts table so the agent knows who to delegate to
3. Use the Write tool to save it to: {agent_file}
4. The file must be self-contained and production-ready

When done, output: AGENT_CREATED: {agent_name}
"""
            )

            with state_lock:
                active_creators[agent_id] = {
                    'name': agent_name,
                    'file': agent_file,
                    'dispatched_at': datetime.now().isoformat()
                }

            log_event("baseline_agent_creation_dispatched",
                      agent_name=agent_name,
                      active_creators=len(active_creators),
                      pending=len(pending_agents))

        # Wait for at least one creator to complete
        if active_creators:
            completed_id, result = await_any_agent(list(active_creators.keys()))

            # THREAD-SAFE: Use state_lock when modifying shared state
            with state_lock:
                agent_info = active_creators.pop(completed_id)

            # Verify file was written
            if os.path.exists(agent_info['file']):
                content = Read(agent_info['file'])
                if len(content) >= 100:
                    output(f"  ✓ {agent_info['name']} created ({len(pending_agents)} pending, {len(active_creators)} active)")
                    created_agents.append(agent_info)

                    log_event("baseline_agent_created",
                              agent_name=agent_info['name'],
                              file_path=agent_info['file'])
                else:
                    output(f"  ✗ {agent_info['name']} INVALID - re-queuing")
                    pending_agents.append(agent_info['name'])
            else:
                output(f"  ✗ {agent_info['name']} NOT WRITTEN - re-queuing")
                pending_agents.append(agent_info['name'])

    # ═══════════════════════════════════════════════════════════════════════
    # VERIFY ALL BASELINE AGENTS
    # ═══════════════════════════════════════════════════════════════════════

    output("")
    output("VERIFYING ALL BASELINE AGENT FILES...")

    missing = []
    for agent_name in BASELINE_AGENTS:
        if not os.path.exists(f"{AGENTS_DIR}/{agent_name}.md"):
            missing.append(agent_name)

    if missing:
        raise AgentCreationError(f"Baseline agent files not created: {missing}")

    output(f"✓ ALL {len(BASELINE_AGENTS)} BASELINE AGENTS CREATED SUCCESSFULLY")
    output("=" * 60)
```

### Synchronization Gate Before Task Loop

**CRITICAL**: The task delivery loop MUST NOT start until all agents exist.

```python
def execute_agent_generation_phase(gaps, plan_file, best_practices, artefacts_dir):
    """Generate ALL agent prompts with BLOCKING synchronization."""

    output("")
    output("╔══════════════════════════════════════════════════════════════╗")
    output("║           AGENT GENERATION PHASE (BLOCKING)                   ║")
    output("╚══════════════════════════════════════════════════════════════╝")

    # Write config file for sub-agents to read
    config = {
        'environments': CONFIG['ENVIRONMENTS'],
        'verification_commands': CONFIG['VERIFICATION_COMMANDS'],
        'best_practices': best_practices,
        'available_experts': [],
    }
    Write(f"{artefacts_dir}/agent-generation-config.json", json.dumps(config))

    # ═══════════════════════════════════════════════════════════════════════
    # PHASE 5a: GENERATE EXPERTS (BLOCKING - WAIT FOR ALL)
    # ═══════════════════════════════════════════════════════════════════════
    experts = generate_expert_prompts(gaps, plan_file, best_practices)

    # Update config with created experts AFTER they all exist
    config['available_experts'] = experts
    Write(f"{artefacts_dir}/agent-generation-config.json", json.dumps(config))

    # ═══════════════════════════════════════════════════════════════════════
    # PHASE 5b: GENERATE BASELINE AGENTS (BLOCKING - WAIT FOR ALL)
    # ═══════════════════════════════════════════════════════════════════════
    generate_baseline_agent_prompts(experts, plan_file, config)

    # ═══════════════════════════════════════════════════════════════════════
    # PHASE 5c: FINAL VERIFICATION GATE
    # ═══════════════════════════════════════════════════════════════════════
    output("")
    output("FINAL VERIFICATION: Ensuring all agent files exist before task loop...")

    verify_all_agents_ready(experts)

    output("")
    output("╔══════════════════════════════════════════════════════════════╗")
    output("║     ✓ ALL AGENTS CREATED - READY TO BEGIN TASK LOOP          ║")
    output("╚══════════════════════════════════════════════════════════════╝")
    output("")

    return experts


def verify_all_agents_ready(experts: list[dict]) -> None:
    """Final gate: verify ALL agents exist before task loop starts."""

    all_required = []

    # Baseline agents
    for agent_name in BASELINE_AGENTS:
        all_required.append({
            'name': agent_name,
            'file': f"{AGENTS_DIR}/{agent_name}.md",
            'type': 'baseline'
        })

    # Experts
    for expert in experts:
        all_required.append({
            'name': expert['name'],
            'file': expert['file'],
            'type': 'expert'
        })

    missing = []
    for agent in all_required:
        if not os.path.exists(agent['file']):
            missing.append(f"{agent['type']}:{agent['name']}")

    if missing:
        raise AgentCreationError(
            f"FATAL: Cannot start task loop. Missing agents: {missing}"
        )

    log_event("all_agents_verified",
              baseline_count=len(BASELINE_AGENTS),
              expert_count=len(experts),
              total=len(all_required))
```

### Directory Structure After Generation

```
.claude/
├── agents/
│   ├── developer.md           # Baseline agent
│   ├── critic.md              # Baseline agent
│   ├── auditor.md             # Baseline agent
│   ├── remediation.md         # Baseline agent
│   ├── health-auditor.md      # Baseline agent
│   └── experts/               # Expert agents subdirectory
│       ├── crypto-expert.md   # Plan-specific expert
│       ├── protocol-expert.md # Plan-specific expert
│       └── ...
└── surrogate_activities/
    └── [plan-name]/
        ├── state.json
        ├── events.jsonl
        └── best-practices-research.json
```

---

## Pre-Flight Validation

**CRITICAL**: Before ANY work begins, validate the environment is ready.

See [environment-verification.md](../environment-verification.md) for environment details.

### Validation Checks

| Check                | What                                    | Blocking |
|----------------------|-----------------------------------------|----------|
| Plan file            | Exists and contains required sections   | Yes      |
| Required directories | `.claude/agents`, `.claude/state`, etc. | Yes      |
| Agent templates      | All creation templates exist            | Yes      |
| Verification tools   | Basic tool availability                 | Warning  |
| Environments         | Listed environments accessible          | Warning  |

```python
def pre_flight_validation(plan_file: str, config: dict) -> dict:
    """Validate environment before starting work."""

    results = {'passed': True, 'blocking_issues': [], 'warnings': []}

    # 1. Plan file exists and is valid
    # 2. Required directories can be created
    # 3. Agent creation templates exist
    # 4. Verification commands can execute
    # 5. Environments accessible

    return results
```

---

## Pre-Existing Failures Baseline

**NEW sessions only**: Capture baseline before any work begins.

This distinguishes:

- Pre-existing failures (existed before we started)
- Task-introduced failures (caused by our work)

```python
def capture_and_store_baseline(plan_file, config, state):
    """Capture pre-existing failures baseline for new sessions."""

    baseline = capture_pre_existing_failures_baseline(config)
    state['pre_existing_failures_baseline'] = baseline

    # Also write to file for debugging
    Write(f"{plan_dir}/.pre-existing-baseline.json", json.dumps(baseline))

    return baseline
```

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
        if last_event and last_event.get('event') == 'session_pause':
            return 'RESUME'

        return 'RECOVERY'

    except (json.JSONDecodeError, IOError):
        return 'RECOVERY'
```

---

## Main Entry Point Summary

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

    # Determine artefacts directory from plan file
    artefacts_dir = get_artefacts_dir(plan_file)  # e.g., .claude/surrogate_activities/[plan-name]/

    if session_type == 'RESUME':
        # Load state, verify agents, continue
        state = load_state(f"{artefacts_dir}/state.json")
        best_practices = get_or_refresh_research(plan_file, artefacts_dir, force_refresh=False)
        ensure_core_agents_exist(best_practices, state.get('experts', []))
        # ... resume flow
    else:
        # NEW: Full bootstrap
        state = initialize_orchestrator(plan_file, artefacts_dir)
        best_practices = get_or_refresh_research(plan_file, artefacts_dir, force_refresh=True)
        gaps = analyze_gaps(plan_file)
        experts = execute_agent_generation_phase(gaps, plan_file, best_practices, artefacts_dir)
        capture_and_store_baseline(plan_file, CONFIG, state)
        # ... new session flow

    begin_task_loop(state)
```

---

## Directory Structure After Bootstrap

```
.claude/
├── agents/
│   ├── developer.md
│   ├── critic.md
│   ├── auditor.md
│   ├── business-analyst.md
│   ├── remediation.md
│   ├── health-auditor.md
│   └── experts/
│       ├── [expert-1].md
│       └── [expert-2].md
├── state/
│   ├── coordinator-state.json
│   ├── event-log.jsonl
│   └── agent-generation-config.json
└── scratch/
    └── [task-id]/
        └── [working files]
```

---

## Related Documentation

- [Task Delivery Loop](../task-delivery-loop.md) - Main execution loop
- [Expert Creation](../agent-creation/expert-creation.md) - Creating expert agents
- [State Management](../state-management.md) - State persistence
- [Task Quality](task-quality.md) - Task assessment
- [Recovery Procedures](../recovery-procedures.md) - Error recovery
- [Session Management](../session-management.md) - Pause/resume protocols
- [Environment Verification](../environment-verification.md) - Environment checks
- [State Schema](state-schema.md) - State file format
- [Event Schema](event-schema.md) - Event log format
