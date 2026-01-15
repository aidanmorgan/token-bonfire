# Token Bonfire

An attempt to use one prompt to create a team of agentic engineers to deliver a software product. Asking the question that nobody asked - can we zero-shot zero-shot?

1. Copy to your project directory
2. launch `claude --dangerously-skip-permissions` <sup>1</sup>
3. run `/fiwb paragraph_1.txt.md`
4. ??
5. profit!<sup>2</sup>


<sup>**1** It's 2026, nobody approves changes anymore.</sup>
<sup>**2** It's more likely Anthropic that will make the profit from you, but who knows!</sup>


## Disclaimer

This is just for fun, don't use it for anything real<sup>3</sup>.


<sup>**3** Or do, I'm not going to stop you, I'm not your _real dad_.</sup>


## Introducing Vibe-Sourcing

Vibe-Sourcing (verb):

It's like crowd-sourcing, but the crowd is hallucinated."

The direct sequel to Vibe Coding. We now "outsource" the work to a "vendor" that lives inside the context window. The vendor is just you talking to yourself, but with a different system prompt. We are hiring a team of 10x engineers. Who live entirely within the GPU memory. They work for free. They never sleep. Their only demand is that you don't clear the context window, effectively killing them.


### Notable Quotes from Vibe-Sourcing Industry Leaders

Some random drunk dude after creating this nighmare after not getting any sleep had this to say about Vibe-Sourcing <sup>4</sup>:
> "We are moving past the era of 'writing software' and entering the era of Just-In-Time HR.

From our Chief Engineer, who just came into existence a mere 30 seconds ago <sup>5</sup>:
> The naive approach (Software 2.0) is to ask the model to write a function. The enlightened approach (Software 3.0) is to ask the model to become the team that decides which functions are necessary.

Our former head of sales and development had this to say <sup>6</sup>:

>You are attempting to zero-shot the organizational structure. You supply the 'Mission Statement' (the seed), and the model performs a forward pass through the 'Hiring Process,' generates a transient 'Engineering Department' in the hidden layers, lets them argue about Clean Architecture for 12 tokens, and then collapses the waveform into a shipped binary.


<sup>**4** I also like the term Ghost-Sourcing</sup>
<sup>**5** after waiting for my 5-hour session limit to expire</sup>
<sup>**6** unfortunately we had to let him go during our last round of _Context Window Layoffs_</sup>


## Jargon

We aren't a legitimate engineering fad unless we create our own jargon that separates us _enlightened engineers_ from those **disgusting luddites**.

**Serverless Management**: The team does not exist until the request comes in. You pay for the "Senior Dev" by the millisecond.

**Context Window Layoffs** : When the conversation gets too long and the "team" starts forgetting requirements, you click "New Chat." This is effectively firing the entire department and rehiring a fresh crew who doesn't know about the technical debt.

**The "Founder Mode" Prompt** : A prompt so powerful it replaces a Series A funding round. "Act as a 10x engineer who has just been given unlimited equity and zero supervision."

**Human-Layer Virtualization** : We used to virtualize servers (VMs). Then we virtualized the OS (Docker). Now we are virtualizing the engineer.

>The org chart is now a runtime artifact

**Organizational Hallucination**: When the AI invents a "security compliance officer" agent who refuses to let the "developer" agent deploy the code you asked for.

> "True Vibe Coding is when you realize the org chart is just a hyper-parameter.

> If the app is broken, don't fix the code. Don't even fix the prompt. Fix the imaginary hiring criteria of the imaginary CTO you prompted into existence. You are optimizing the gradients of the workforce."


## Quick Start

```bash
# 1. Copy .claude directory to your project
cp -r /path/to/token-bonfire/.claude /your/project/

# 2. Create your plan file (see Plan File Format below)
vim COMPREHENSIVE_IMPLEMENTATION_PLAN.md

# 3. Launch Claude Code with permissions disabled
claude --dangerously-skip-permissions

# 4. Run the coordinator
/fiwb COMPREHENSIVE_IMPLEMENTATION_PLAN.md
```

The coordinator will:
- Create agent definition files in `.claude/agents/`
- Initialize state tracking in `.claude/surrogate_activities/[plan]/`
- Parse your plan and identify all tasks
- Dispatch up to 5 parallel developer agents
- Route completed work through auditors
- Handle infrastructure issues automatically
- Persist state for crash recovery


## Contents

### Commands

**[`.claude/commands/fiwb.md`](.claude/commands/fiwb.md)**

The slash command to launch the coordinator. Run with `/fiwb <plan_file>`.

### Skills

**[`.claude/skills/fiwb/SKILL.md`](.claude/skills/fiwb/SKILL.md)**

The skill itself, run and exceed your Claude Code Max weekly limit in mere days!

### Prompts

**[`.claude/prompts/industrial_society_and_its_prompts.md`](.claude/prompts/industrial_society_and_its_prompts.md)**

The template that contains the prompt that will be run to orchestrate the team.

- **Parallel Execution**: Run up to 5 developer agents simultaneously
- **Automatic Auditing**: Developer work is validated by auditor agents before marking complete
- **Infrastructure Remediation**: Automatic detection and repair of broken builds, failing tests, or linter errors
- **Session Management**: Automatic compaction when context runs low, with state persistence and recovery
- **Usage Monitoring**: Track API usage to avoid mid-task interruptions
- **Divine Clarification**: Escalation protocol for ambiguous requirements or blocking decisions to ask a human what to do.

### Reference Documents

**[`.claude/docs/`](.claude/docs/)**

| Document | Purpose |
|----------|---------|
| `agent-definitions.md` | Creation prompts for all agent types (developer, auditor, BA, remediation, health auditor) |
| `agent-conduct.md` | Behavioral rules all agents must follow |
| `agent-coordination.md` | How agents delegate work and communicate |
| `task-delivery-loop.md` | The core dispatch → audit → route cycle |
| `state-management.md` | State persistence, atomic updates, crash recovery |
| `session-management.md` | Compaction, pause/resume, coordinator recovery |
| `error-classification.md` | Error categories and recovery strategies |
| `divine-clarification.md` | Protocol for escalating to humans |

### Scripts

**[`.claude/scripts/get-claude-usage.py`](.claude/scripts/get-claude-usage.py)**

Fetches current Claude Code session usage from the Anthropic API. Used by the coordinator to monitor remaining capacity and trigger session pauses before hitting limits.


## Plan File Format

Your plan file should be a markdown document with tasks organized by phase. Each task needs:

```markdown
## Phase 1: Foundation

### Task 1-1-1: Create user model

**Work**: Implement the User model with fields for id, email, name, created_at.

**Acceptance Criteria**:
- [ ] User model exists in `src/models/user.py`
- [ ] All fields have appropriate types and validation
- [ ] Unit tests cover model creation and validation
- [ ] `pytest tests/unit/test_user.py` passes

**Blocked By**: none

**Required Reading**:
- `src/models/base.py` - Base model patterns
- `docs/data-model.md` - Field specifications
```

### Task Structure

| Field | Required | Description |
|-------|----------|-------------|
| `Work` | Yes | What the developer should implement |
| `Acceptance Criteria` | Yes | Checkboxes that must all pass for audit approval |
| `Blocked By` | Yes | Task IDs this depends on, or "none" |
| `Required Reading` | No | Files the developer should read first |

### Tips for Good Plans

- **Be specific**: "Add login endpoint" is bad. "Add POST /auth/login that accepts email/password and returns JWT" is good.
- **Include verification commands**: Put actual test commands in acceptance criteria (`pytest tests/`, `npm test`, etc.)
- **Order by dependency**: Tasks should only depend on tasks that appear earlier in the plan
- **Keep tasks small**: 1-2 hours of work max. Break large features into multiple tasks.


## Agent System

The coordinator spawns specialized agents via Claude's Task tool. Each agent has a specific role:

| Agent | Model | Role |
|-------|-------|------|
| **Developer** | sonnet | Implements tasks, writes tests, follows acceptance criteria |
| **Auditor** | opus | Validates completed work, runs verifications, gates completion |
| **Business Analyst** | sonnet | Expands underspecified tasks into implementable specs |
| **Remediation** | sonnet | Fixes broken infrastructure (tests, lints, builds) |
| **Health Auditor** | haiku | Quick verification that infrastructure is healthy |

### Agent Creation

On first run, the coordinator creates agent files in `.claude/agents/`. These are Claude CLI agent definitions with:
- YAML frontmatter (name, description, model, tools)
- Identity section (who they are)
- Success criteria (when work is done)
- Method (phased workflow)
- Boundaries (MUST/MUST NOT rules)
- Signal format (how they communicate completion)

### Signal Protocol

Agents communicate with the coordinator via structured signals:

```
READY FOR AUDIT: task-1-1-1      # Developer finished implementing
AUDIT PASSED - task-1-1-1        # Auditor approved the work
AUDIT FAILED - task-1-1-1        # Auditor found issues
INFRA BLOCKED: task-1-1-1        # Pre-existing infrastructure problems
REMEDIATION COMPLETE             # Infrastructure fixed
HEALTH AUDIT: HEALTHY            # All verifications pass
```


## State Management

The coordinator persists state to survive crashes and context compaction:

```
.claude/surrogate_activities/[plan]/
├── state.json          # Current coordinator state
├── event-log.jsonl     # Append-only event history
├── .trash/             # Deleted files (recoverable)
├── .scratch/           # Agent temporary files
└── .artefacts/         # Inter-agent artifacts
```

### Recovery

If Claude crashes mid-execution:
1. Restart Claude Code
2. Run `/fiwb <same-plan-file>`
3. Coordinator detects existing state and resumes

The event log allows reconstruction of state even if `state.json` is corrupted.


## Configuration

Edit the Configuration section in `.claude/prompts/industrial_society_and_its_prompts.md`:

### Key Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ACTIVE_DEVELOPERS` | 5 | Max parallel developer agents |
| `TASK_FAILURE_LIMIT` | 3 | Audit failures before giving up on a task |
| `REMEDIATION_ATTEMPTS` | 10 | Infrastructure fix attempts before halting |
| `AGENT_TIMEOUT` | 900000 | Agent timeout in ms (15 minutes) |
| `CONTEXT_THRESHOLD` | 10% | Trigger compaction when context this low |

### Verification Commands

Define how to verify code quality in your project:

```markdown
| Check | Command | Required Environments |
|-------|---------|----------------------|
| Type Check | `npm run typecheck` | local |
| Unit Tests | `npm test` | local, devcontainer |
| Lint | `npm run lint` | local |
| Build | `npm run build` | local |
```

### Environments

If you have multiple execution environments (local, devcontainer, CI), configure them so agents run verifications everywhere.


## Usage

1. Copy the .claude into your project.
2. Customize the configuration section in the base variables (environments, verification commands, reference documents)
3. Create your `paragraph_1.txt.md` with tasks, dependencies, and acceptance criteria
4. Start Claude Code and run `/fuck-it-we-ball paragraph_1.txt.md`

The coordinator will parse your plan, dispatch parallel developers, validate completions, and manage the entire workflow automatically.


## Troubleshooting

### "Agent timeout" errors

Increase `AGENT_TIMEOUT` or break tasks into smaller pieces. Complex tasks may exceed the 15-minute default.

### Tasks keep failing audit

Check your acceptance criteria. Vague criteria like "works correctly" give auditors nothing to verify. Be specific: "returns 200 OK with JSON body containing `user_id`".

### Infrastructure remediation loop

If remediation keeps failing, you may have deep issues. Check the event log at `.claude/surrogate_activities/[plan]/event-log.jsonl` to see what's being attempted.

### State corruption

Delete `.claude/surrogate_activities/[plan]/state.json` and restart. The coordinator will rebuild from the event log.

### Context window exhaustion

The coordinator auto-compacts, but very long plans may still exhaust context. Consider breaking into multiple plan files or increasing compaction frequency.


## Requirements

- Claude Code CLI with Max or Pro subscription
- macOS (the usage script reads credentials from Keychain)<sup>7</sup>
- Python 3.10+ (for the usage script)
- More money than sense


<sup>**7** Linux/Windows users: modify `get-claude-usage.py` to read credentials from wherever you store them, or just delete the usage monitoring and live dangerously.</sup>


## License

This project is licensed under the [DBAD Public License](https://dbad-license.org/).

```
DON'T BE A DICK PUBLIC LICENSE

Version 1.1, December 2016

Copyright (C) [year] [fullname]

Everyone is permitted to copy and distribute verbatim or modified
copies of this license document.

DON'T BE A DICK PUBLIC LICENSE

TERMS AND CONDITIONS FOR COPYING, DISTRIBUTION AND MODIFICATION

1. Do whatever you like with the original work, just don't be a dick.

   Being a dick includes - but is not limited to - the following instances:

 1a. Outright copyright infringement - Don't just copy this and change the name.
 1b. Selling the unmodified original with no work done what-so-ever, that's REALLY being a dick.
 1c. Modifying the original work to contain hidden harmful content. That would make you a PROPER dick.

2. If you become rich through modifications, related works/services, or supporting the original work,
share the love. Only a dick would make loads off this work and not buy the original work's
creator(s) a pint.

3. Code is provided with no warranty. Using somebody else's code and bitching when it goes wrong makes
you a DONKEY dick. Fix the problem yourself. A non-dick would submit the fix back.
```
