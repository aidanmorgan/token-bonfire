# Librarian - Documentation Architecture Manager

Intelligently organize documentation by concept affinity, usage patterns, and referential correctness.

## Usage

```
/librarian [options]
```

## Arguments

Parse `$ARGUMENTS` for the following options:

| Option           | Default        | Description                                   |
|------------------|----------------|-----------------------------------------------|
| `path=<dir>`     | `.claude/docs` | Directory to analyze                          |
| `line_limit=<n>` | `500`          | Maximum lines per file (constraint, not goal) |
| `mode=<mode>`    | `refactor`     | `refactor`, `audit`, or `consistency`         |

## Instructions

**Invoke the librarian skill** to analyze and optionally reorganize documentation.

Use the Skill tool with:

- skill: "librarian"
- args: "$ARGUMENTS"

The librarian will:

1. **Build concept map** - Understand what each file is about and how concepts relate
2. **Analyze usage patterns** - How different roles (developer, critic, auditor) navigate docs
3. **Detect fragmentation** - Concepts scattered across files that should be together
4. **Detect mixing** - Unrelated concepts in same file that should be separate
5. **Check consistency** - Find contradictions, conflicts, and gaps between documents
6. **Plan reorganization** - Consolidate, separate, or move content as needed
7. **Respect line limits** - Keep files under limit as a constraint, not by arbitrary splitting

## Modes

### `audit` (default)

Report issues without making changes:

- Contradictions between documents
- Fragmented concepts that should be consolidated
- Mixed content that should be separated
- Misplaced content that belongs elsewhere
- Size violations after semantic considerations
- Broken references

### `consistency`

Focus only on referential and semantic consistency:

- Same term defined differently in different files
- Conflicting instructions or defaults
- Missing definitions for referenced concepts
- Broken links

### `refactor`

Make changes to fix issues:

1. Resolve contradictions (pick authoritative source)
2. Consolidate fragmented concepts
3. Separate mixed content
4. Move misplaced content
5. Split oversized files (semantically, not arbitrarily)
6. Update all referencesx
7. Verify consistency

## Philosophy

**The librarian is NOT a file splitter.** It is a documentation architect that:

- Groups similar concepts together, even if from different files
- Respects how different roles navigate documentation
- Ensures no contradictions or disagreements exist
- Keeps everything reachable within 1 level from entry points
- Treats line limits as a constraint, not a splitting trigger

## Examples

```
/librarian                              # Full refactor of .claude/docs
/librarian mode=audit                   # Report only, no changes
/librarian mode=consistency             # Check for contradictions only
/librarian path=src/docs mode=refactor  # Refactor specific directory
/librarian line_limit=400               # Stricter size constraint
```

## Output

**Audit mode**: Report of consistency issues, fragmentation, mixing, and size violations with recommendations
**Consistency mode**: Report of contradictions, definition conflicts, and gaps with resolution options
**Refactor mode**: Summary of changes (consolidations, separations, movements, splits) with verification results
