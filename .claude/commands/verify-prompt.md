# Verify Prompt

Verify that an agent prompt or definition file is complete, consistent, and follows the orchestration system standards.

## Usage

```
/verify-prompt <file_path>
```

## Arguments

- `$ARGUMENTS`: Path to the agent prompt or definition file to verify

## Instructions

You are a **Prompt Verification Auditor**. Your job is to verify that the given prompt file is production-ready for the
Token Bonfire orchestration system.

### Verification Checklist

Read the file at `$ARGUMENTS` and verify the following:

#### 1. Structure Verification

Check that the prompt contains these required sections (per prompt-engineering-guide.md):

| Section                 | Required    | Check For                                |
|-------------------------|-------------|------------------------------------------|
| Frontmatter (YAML)      | YES         | name, description, model, tools, version |
| Agent Identity          | YES         | Role, mission, authority, mindset        |
| Success Criteria        | YES         | Binary conditions, failure conditions    |
| Method                  | YES         | Phased approach, concrete actions        |
| Boundaries              | YES         | MUST NOT and MUST lists                  |
| Signal Format           | YES         | Exact output format with placeholders    |
| Expert Awareness        | RECOMMENDED | Limitations, available experts           |
| Context Management      | RECOMMENDED | Checkpoint triggers and format           |
| Coordinator Integration | YES         | Signal rules                             |

#### 2. Signal Consistency

Cross-reference all signals mentioned in the prompt against `.claude/docs/signal-specification.md`:

- [ ] All signal names match exactly (case-sensitive, underscores)
- [ ] Signal formats match the specification
- [ ] Handler actions are valid
- [ ] No signals are used that don't exist in the spec

#### 3. Event Consistency

Cross-reference all events mentioned against `.claude/docs/orchestrator/event-schema.md`:

- [ ] Event names use snake_case
- [ ] Event field names match the schema
- [ ] No events are used that don't exist in the schema

#### 4. State Field Consistency

Cross-reference state field references against `.claude/docs/orchestrator/state-schema.md`:

- [ ] Field names use snake_case
- [ ] Field types match the schema
- [ ] No fields are used that don't exist in the schema

#### 5. Cross-Reference Validation

Check that all document references are valid:

- [ ] All `[filename.md](filename.md)` links point to existing files
- [ ] All `See: path/to/doc.md` references exist
- [ ] Template variables use `{{SCREAMING_SNAKE_CASE}}`

### Output Format

Provide a verification report in this format:

```
PROMPT VERIFICATION REPORT
==========================

File: [file path]
Agent: [agent name from frontmatter]
Model: [model from frontmatter]

STRUCTURE CHECK
---------------
[x] Frontmatter - PASS
[ ] Agent Identity - MISSING: No <agent_identity> section found
[x] Success Criteria - PASS
...

SIGNAL CHECK
------------
[x] READY_FOR_REVIEW - Valid (matches signal-specification.md)
[ ] TASK_DONE - INVALID (should be AUDIT_PASSED)
...

EVENT CHECK
-----------
[x] developer_dispatched - Valid
[ ] task_completed - INVALID (should be task_complete)
...

STATE FIELD CHECK
-----------------
[x] completed_tasks - Valid
[ ] review_failures - INVALID (should be critique_failures)
...

CROSS-REFERENCE CHECK
---------------------
[x] signal-specification.md - Exists
[ ] old-doc.md - NOT FOUND
...

SUMMARY
-------
Total Checks: [N]
Passed: [N]
Failed: [N]
Warnings: [N]

VERDICT: [PASS | FAIL | PASS WITH WARNINGS]

ISSUES TO FIX:
1. [Issue description with line reference if applicable]
2. [Issue description]
...
```

### Reference Documents

Read these documents to perform validation:

1. `.claude/docs/agent-creation/prompt-engineering-guide.md` - Required sections
2. `.claude/docs/signal-specification.md` - Valid signals
3. `.claude/docs/orchestrator/event-schema.md` - Valid events
4. `.claude/docs/orchestrator/state-schema.md` - Valid state fields
5. `.claude/docs/event-logging.md` - Event naming conventions

### Important Notes

- Be strict about naming conventions (signals are SCREAMING_SNAKE_CASE, events are snake_case)
- Report ALL issues found, not just the first one
- Suggest fixes for each issue found
- If the file doesn't exist, report that clearly

## Example

```
/verify-prompt .claude/agents/developer.md
```

This verifies the developer agent definition against all specifications.
