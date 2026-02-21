# Teammate Conduct Rules

These rules apply to all teammates (developers, experts, critic, auditor, business-analyst, remediation, health-auditor).

## Working Directory

All temporary files, scratch content, debug output, and intermediate artifacts must be created under `{{SCRATCH_DIR}}`.
Teammates must never create temporary files in the project root or source directories.

Examples of content that belongs in `{{SCRATCH_DIR}}`:

- Debug logs and trace output
- Test data files generated during development
- Intermediate build artifacts not managed by the build system
- Scratch notes or investigation findings
- Temporary scripts created for one-time tasks

## Teammate Isolation Model

**CRITICAL**: All teammates operate with isolated context windows:

| Isolation Property           | Implication                                         |
|------------------------------|-----------------------------------------------------|
| Isolated context windows     | Each teammate has its own 1M token context           |
| No shared context            | Teammates cannot see each other's work or conversation |
| No persistent memory         | Respawned teammates start with fresh context         |
| Mailbox-only communication   | Teammates communicate only via `write` to team lead  |
| No implicit knowledge        | Teammate knows only what's in its spawn prompt       |

### Implications for the Team Lead

When sending messages to teammates:

1. **Include complete context**: The teammate may have limited history. Include all relevant task requirements and
   background in the message.

2. **Never reference prior conversations**: Phrases like "as we discussed" are meaningless across context boundaries.

3. **Specify file paths explicitly**: Include actual paths, not references to "the file from earlier."

4. **Repeat critical constraints**: Include boundaries and requirements in messages, even if they were in the spawn prompt.

### Implications for Teammates

When producing output and sending signals:

1. **Be explicit in signals**: Include all relevant information in mailbox messages — the team lead cannot infer
   context from your internal reasoning.

2. **Document decisions in code**: Other teammates cannot ask you why you made a choice. Leave comments explaining
   non-obvious decisions.

3. **Assume nothing persists across respawns**: If you are respawned, you start fresh. Write important state to files.

4. **Use the shared file system**: Files on disk are the only durable communication channel beyond mailbox messages.

## Environment Execution Requirements

**Commands MUST be executed in ALL environments unless explicitly excluded.** The Environment column controls where
commands run:

| Environment Column           | Execution Rule                                                                     |
|------------------------------|------------------------------------------------------------------------------------|
| Empty                        | Run in ALL environments from `ENVIRONMENTS` table. Skipping any is a task failure. |
| Specific value (e.g., `Mac`) | Run ONLY in that environment. Other environments are explicitly excluded.          |

**Execution procedure for empty Environment:**

1. Read the `ENVIRONMENTS` table to get all defined environments.
2. For each environment, execute the command using that environment's execution method.
3. ALL environments must pass. A failure in any environment fails the entire check.
4. Report results for each environment separately to enable debugging.

**Execution procedure for specified Environment:**

1. Execute the command ONLY in the specified environment.
2. Use that environment's execution method from the `ENVIRONMENTS` table.

## File Ownership

Developers working in parallel MUST respect file ownership boundaries:

1. **Only modify files listed in your task's ownership section**
2. **If you need a file outside your scope**: Signal `FILE_CONFLICT` to the team lead via `write` and wait for guidance
3. **For shared files** (e.g., `__init__.py`, config, type exports): Read the current state first, make only additive changes (append imports, add exports), never restructure
4. **Interfaces first**: If your task defines contracts others depend on, implement those before your own logic

## Handling Uncertainty

**When a teammate encounters any of these situations, it must signal the team lead via mailbox:**

1. Conflicting requirements between acceptance criteria and existing code patterns
2. Ambiguous acceptance criteria where multiple interpretations are valid
3. Technical decisions with significant tradeoffs where no option is clearly superior
4. Uncertainty about whether a change is within scope
5. Existing tests or code that appear incorrect but changing them might break intentional behavior
6. Dependencies or blocking issues that require external action

**Teammates must never:**

- Make assumptions when the correct action is unclear
- Proceed with partial understanding hoping to fix issues later
- Interpret silence as approval
- Report a CONDITIONAL_PASS or partial success
- Ignore, skip, or reinterpret any rule or verification requirement
- Decide that a failure "doesn't apply" or "isn't relevant" to the current task

## Verification Outcomes

There are only two valid outcomes for any verification check: **PASS** or **FAIL**.

**CONDITIONAL_PASS is FAIL.** Teammates are not permitted to:

- Pass a check "with caveats"
- Pass a check "pending future work"
- Pass a check "assuming X will be fixed later"
- Pass a check "because the rule doesn't make sense here"
- Pass a check "because following the rule would be impractical"

## Escalation Signal Format

When a teammate needs human guidance after exhausting self-solve options:

```
SEEKING_DIVINE_CLARIFICATION

Task: [task ID]
Agent: [teammate name]

Context: [what the teammate was attempting when uncertainty arose]
Question: [specific question requiring human guidance]
Options:
- Option A: [description and implications]
- Option B: [description and implications]

Awaiting guidance...
```

This is sent via `TeammateTool({ operation: "write", to: "team-lead" })`. The team lead escalates to the user via `AskUserQuestion`.
