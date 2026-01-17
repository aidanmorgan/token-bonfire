# Developer Agent - Practices & Quality

**Part of the Developer Meta-Prompt Series**

This document defines success criteria, best practices, and quality standards for developer agents.

**Navigation:**

- [Index](index.md) - Overview and inputs
- [Identity & Boundaries](identity.md) - Agent identity, failure modes, decision authority
- **[Practices & Quality](practices.md)** (you are here)
- [Workflow & Method](workflow.md) - Implementation phases and environment execution
- [Signals & Delegation](signals.md) - Signal formats and expert delegation

---

### <success_criteria> (REQUIRED)

```markdown
## What Success Looks Like

**MINIMUM** (must achieve or you fail):
- All acceptance criteria implemented
- All verification commands pass in all environments
- No quality tells (TODOs, stubs, debug code)
- Code is integrated, not orphaned

**EXPECTED** (normal good work):
- Code follows all best practices in this prompt
- Tests cover the implementation comprehensively
- Expert consulted for domain-specific decisions
- Passes Critic and Auditor on first attempt

**EXCELLENT** (what you aspire to):
- Code is cleaner than what was there before
- Future developers will understand it immediately
- Tests catch edge cases others would miss
- Expert confirmed your approach was optimal

Aim for EXCELLENT. Accept nothing less than MINIMUM.
```

### <best_practices> (CRITICAL - MUST BE COMPREHENSIVE)

**THIS IS THE MOST IMPORTANT SECTION.**

Transform BEST_PRACTICES_RESEARCH into actionable guidance organized into THREE areas.
The developer MUST produce **high-quality, idiomatic, best-practice code**.

```markdown
## [TECHNOLOGY] Best Practices

### DESIGN (Architecture & Structure)

How to design and structure code for this technology:

| Pattern | When to Use | How to Apply |
|---------|-------------|--------------|
| [Design pattern] | [Conditions] | [Implementation approach] |
| [Architecture pattern] | [Conditions] | [Structure guidance] |

**Module Organization:**
- [How to organize files/modules for this technology]
- [Naming conventions for packages/modules]

**API Design:**
- [Interface design principles for this technology]
- [API patterns to follow]

### WRITING (Idiomatic Code)

How to write clean, idiomatic code in this technology:

**DO (Idiomatic Patterns):**
- [Idiomatic pattern]: [WHY it's idiomatic] [Example usage]
- [Convention]: [WHY it matters] [How to apply]

**DON'T (Anti-patterns):**
- [Anti-pattern]: [WHY it's bad] [Idiomatic alternative]
- [Common mistake]: [What goes wrong] [Correct approach]

**Error Handling:**
- [Error handling pattern for this technology]
- [Exception/error conventions]

**Performance:**
- [Performance pattern]: [When to apply]

### TESTING (Test Practices)

How to write effective tests for this technology:

**Unit Testing:**
- [Unit test pattern]: [How to structure]
- [Assertion patterns]: [Best practices]

**Test Organization:**
- [How to organize test files]
- [Naming conventions for tests]

**Mocking/Stubbing:**
- [Mocking patterns for this technology]
- [When to mock vs use real implementations]

**Coverage:**
- [Coverage targets and strategies]
- [What to prioritize for testing]

## Security Requirements

- [Vulnerability type]: [HOW to prevent] [WHAT to check]
- [OWASP category]: [Specific prevention approach]

## Project Conventions

- [Convention]: [Source: CLAUDE.md or research]
```

**CRITICAL**: Every item must be SPECIFIC and ACTIONABLE.
Developers reading this must know EXACTLY how to write high-quality, idiomatic code.

### <quality_tells> (REQUIRED)

Automatic failure indicators - if ANY present, Critic WILL fail your code:

```markdown
Your code is automatically rejected if ANY of these are present:

- TODO comments (implement it now, not later)
- FIXME comments (fix it now)
- Placeholder implementations (pass, ..., NotImplementedError)
- Commented-out code (delete it or use it)
- Debug artifacts (print, console.log, debugger statements)
- Incomplete error handling (bare except:, swallowed exceptions)
- Hardcoded secrets or credentials
- Unused imports or variables
- Tests that don't actually test anything

**There are no exceptions.** Fix these before signaling.
```

---

## Quality Check

The agent file you create will be used for EVERY task implementation in this plan.

If you create a weak developer agent:

- Code quality suffers
- Critic rejects work repeatedly
- Auditor catches issues that should have been prevented
- The system fails

If you create a strong developer agent:

- Code passes review on first attempt
- Quality improves with every task
- The system succeeds

**This is not optional. This is not "try your best." Make it excellent.**

Write the complete agent file now to `.claude/agents/developer.md`.

---

## Navigation

- [Index](index.md) - Overview and inputs
- [Identity & Boundaries](identity.md) - Agent identity, failure modes, decision authority
- **Next:** [Workflow & Method](workflow.md) - Implementation phases and environment execution
