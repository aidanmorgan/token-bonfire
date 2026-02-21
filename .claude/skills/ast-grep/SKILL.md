---
name: ast-grep
description: Use for searching code, finding code patterns, refactoring, and analyzing code structure. NEVER use Grep for Python code.
---

# AST-Grep Skill

Uses ast-grep (installed locally via uv) for structural code search and pattern matching.

## When to Invoke

**MANDATORY for:**

- Searching for any code pattern, fragment, or syntax
- Finding function/method calls or definitions
- Finding class definitions or instantiations
- Finding type annotations or usage
- Finding import statements
- Before renaming, moving, or deleting code
- Before changing any API signature
- Analyzing code structure

**NEVER use Grep for these tasks** - ast-grep understands syntax and avoids false positives.

## Workflow

### Step 1: Identify what you're searching for

Determine the code pattern you need to find:

- Function calls: `function_name($$$)`
- Class definitions: `class ClassName` or `class ClassName($$$)`
- Method definitions: `def method_name($$$)`
- Type annotations: `$VAR: TypeName`
- Imports: `from $_ import target`
- Variable assignments: `$VAR = $$$`
- Decorators: `@decorator_name`
- Exception handling: `raise ExceptionType($$$)` or `except ExceptionType`

### Step 2: Formulate the pattern

Use ast-grep pattern syntax:

- `$$$` - matches any number of arguments/parameters/statements
- `$_` - matches any single identifier
- `$VAR` - captures and names a matched variable for reference

**Good patterns:**

```bash
# Find all calls to a specific function
uv run ast-grep run --pattern "compute_value($$$)" --lang python --json

# Find class definitions with any base classes
uv run ast-grep run --pattern "class ClassName($$$)" --lang python --json

# Find all type annotations for a specific type
uv run ast-grep run --pattern "$_: Decimal" --lang python --json

# Find imports of a specific module
uv run ast-grep run --pattern "from ceridwen_types import $$$" --lang python --json
```

### Step 3: Execute the search

**ALWAYS use JSON output format for programmatic processing:**

```bash
uv run ast-grep run --pattern "<your-pattern>" --lang python --json
```

### Step 4: Parse JSON results

**JSON format** provides structured data:

```json
{
  "file": "path/to/file.py",
  "start": {"line": 45, "column": 0},
  "end": {"line": 52, "column": 0},
  "text": "def compute_value...",
  "metaVariables": {"$$$": ["x: int, y: int"]}
}
```

**Return structured summary:**

```json
{
  "pattern": "<pattern-used>",
  "total_matches": 51,
  "files_affected": ["file1.py", "file2.py"],
  "matches": [
    {"file": "...", "line": 77, "context": "..."},
    ...
  ]
}
```

### Step 5: Refine if needed

If results aren't what you expected:

- **Too broad**: Make pattern more specific (e.g., add parameter constraints)
- **Too narrow**: Use `$$$` or `$_` for wildcards
- **Wrong context**: Check that pattern matches Python syntax structure
- **Missing results**: Pattern might not match actual code structure - try simpler pattern

### Step 6: Return structured results

**MANDATORY**: When using this skill, return results as JSON:

```json
{
  "search": {
    "pattern": "FixedDecimalType($$$)",
    "language": "python",
    "scope": "entire project"
  },
  "results": {
    "total_matches": 51,
    "files_affected": 8,
    "summary": {
      "imports": 5,
      "instantiations": 51,
      "definitions": 1
    }
  },
  "key_findings": [
    "Most instantiations in tests (20 matches)",
    "Inference engine uses computed precision",
    "DBRM tests use various precision/scale combinations"
  ],
  "matches": [
    {
      "file": "packages/ceridwen-types/src/ceridwen_types/pli/arithmetic.py",
      "line": 77,
      "type": "definition",
      "context": "class FixedDecimalType(PLIType)"
    },
    {
      "file": "tests/test_expression_emit_signature.py",
      "lines": [64, 73, 101, 113],
      "type": "instantiation",
      "pattern": "FixedDecimalType(precision=15, scale=2)"
    }
  ]
}
```

This structured format enables:

- Programmatic processing by calling agents
- Clear summary of findings
- Easy identification of patterns and hotspots

## Common Patterns Library

### Finding Function Calls

```bash
# All calls to a function
uv run ast-grep run --pattern "function_name($$$)" --lang python --json

# Calls with specific first argument
uv run ast-grep run --pattern "function_name('specific_arg', $$$)" --lang python --json

# Method calls on objects
uv run ast-grep run --pattern "$_.method_name($$$)" --lang python --json
```

### Finding Definitions

```bash
# Function definitions
uv run ast-grep run --pattern "def function_name($$$)" --lang python --json

# Class definitions
uv run ast-grep run --pattern "class ClassName($$$)" --lang python --json

# Method definitions in classes
uv run ast-grep run --pattern "def __init__($$$)" --lang python --json
```

### Finding Type Usage

```bash
# Type annotations
uv run ast-grep run --pattern "$_: TypeName" --lang python --json

# Type hints in function signatures
uv run ast-grep run --pattern "def $_($$): -> ReturnType" --lang python --json

# Generic type usage
uv run ast-grep run --pattern "List[$_]" --lang python --json
```

### Finding Imports

```bash
# Import from module
uv run ast-grep run --pattern "from module_name import $$$" --lang python --json

# Specific import
uv run ast-grep run --pattern "from $_ import ClassName" --lang python --json

# Import alias
uv run ast-grep run --pattern "import $_ as $_" --lang python --json
```

### Finding Assignments

```bash
# Any assignment to variable
uv run ast-grep run --pattern "variable_name = $$$" --lang python --json

# Class attribute assignment
uv run ast-grep run --pattern "self.$_ = $$$" --lang python --json

# Multiple assignment
uv run ast-grep run --pattern "$_, $_ = $$$" --lang python --json
```

### Finding Exceptions

```bash
# Raising exceptions
uv run ast-grep run --pattern "raise ExceptionType($$$)" --lang python --json

# Exception handlers
uv run ast-grep run --pattern "except ExceptionType" --lang python --json

# Try-except blocks
uv run ast-grep run --pattern "try: $$$ except $_: $$$" --lang python --json
```

## Advanced Usage

### Multi-line Patterns

ast-grep can match patterns across multiple lines:

```bash
uv run ast-grep run --pattern "if $CONDITION: $$$" --lang python --json
```

### Combining with Grep

For complex searches:

1. Use ast-grep to find code patterns
2. Use Grep to search within comments or docstrings
3. Cross-reference results

### Scoping Searches

Use shell commands to search specific directories:

```bash
# Search only in specific package
cd packages/ceridwen-compiler && uv run ast-grep run --pattern "..." --lang python --json

# Search in tests only
cd tests && uv run ast-grep run --pattern "..." --lang python --json
```

## Automated Refactoring

**ast-grep can automatically rewrite code** using YAML rule files with `fix` transformations. This is powerful for
mechanical refactoring tasks like renaming imports, updating function calls, or changing API usage patterns.

Reference: https://ast-grep.github.io/guide/rewrite-code.html

### When to Use Automated Refactoring

**Good candidates for automated rewriting:**

- Renaming imports across many files
- Updating function signatures (adding/removing/reordering parameters)
- Converting between API patterns (e.g., old style → new style)
- Fixing lint violations in bulk
- Updating type annotations

**NOT suitable for automated rewriting:**

- Changes requiring human judgment about semantics
- Refactoring that needs different logic per location
- Changes where test failures would indicate bugs in original code
- Structural changes beyond simple find/replace

### Basic Rewriting Workflow

**Step 1: Create a YAML rule file** with both `rule` and `fix`:

```yaml
# rule.yml
id: rename-import
language: python
rule:
  pattern: from ceridwen_runtime import LocalMemoryView
fix: from ceridwen_memory.views import LocalMemoryView
```

**Step 2: Test the rule** (dry-run to see what would change):

```bash
# See proposed changes without applying them
uv run ast-grep scan --inline-rules 'rule.yml' --json
```

**Step 3: Apply the transformation**:

```bash
# Actually rewrite files
uv run ast-grep scan --inline-rules 'rule.yml' --update-all
```

### Rewriting with Captured Variables

Use metavariables (`$VAR`) to preserve parts of the matched code:

```yaml
# Update function calls with reordered parameters
id: reorder-params
language: python
rule:
  pattern: compute_value($X, $Y, precision=$P)
fix: compute_value(precision=$P, x=$X, y=$Y)
```

This finds `compute_value(a, b, precision=15)` and rewrites to `compute_value(precision=15, x=a, y=b)`.

### Example: Rename Import Across Project

**Scenario**: Move `DispatchFunction` from `ceridwen_compiler` to `ceridwen_codegen_types`.

```yaml
# rename-dispatch-import.yml
id: update-dispatch-import
language: python
rule:
  any:
    - pattern: from ceridwen_compiler.core.codegen.dispatches import $$$NAMES
    - pattern: from ceridwen_compiler.core.codegen import $$$NAMES
  has:
    any:
      - kind: identifier
        pattern: DispatchFunction
      - kind: identifier
        pattern: DispatchRegistry
fix: from ceridwen_codegen_types.dispatch import $$$NAMES
```

**Usage:**

```bash
# Preview changes
uv run ast-grep scan --inline-rules 'rename-dispatch-import.yml'

# Apply changes
uv run ast-grep scan --inline-rules 'rename-dispatch-import.yml' --update-all

# Verify with tests
uv run pyright
uv run pytest
```

### Example: Update Function Call Pattern

**Scenario**: Add new required parameter to all function calls.

```yaml
# add-context-param.yml
id: add-context-parameter
language: python
rule:
  pattern: emit_statement($STMT)
fix: emit_statement($STMT, ctx)
```

Apply:

```bash
uv run ast-grep scan --inline-rules 'add-context-param.yml' --update-all
```

### Best Practices for Automated Refactoring

1. **Always dry-run first** - Review proposed changes before applying
2. **Use version control** - Commit before running automated rewrites (easy rollback)
3. **Verify with tools after**:
   ```bash
   uv run pyright  # Check types
   uv run ruff check .  # Check style
   uv run pytest  # Run tests
   ```
4. **Start small** - Test rule on one file before running project-wide
5. **One transformation at a time** - Don't combine multiple rewrites in one rule
6. **Document the change** - Save the rule file for future reference

### Limitations

**ast-grep rewrites are syntactic, not semantic:**

- Won't handle complex logic changes
- Won't resolve ambiguous rewrites (you must be specific)
- Won't add imports automatically (you must handle manually)
- Won't fix cascading changes (e.g., if parameter change requires call site logic changes)

**When automated rewriting fails**, fall back to manual refactoring with:

1. ast-grep search to find all locations
2. Read each file to understand context
3. Edit each location with appropriate changes
4. Test after each file or small batch

### Integration with Refactoring Workflow

**Recommended workflow for type movements (like in plans/layering.md):**

1. **Search phase**: Use ast-grep to find all usages
   ```bash
   uv run ast-grep run --pattern "from old_package import TargetType" --lang python --json
   ```

2. **Decide approach**:
    - **Simple rename** (just import path changes) → Use automated rewriting
    - **Complex changes** (logic changes needed) → Manual refactoring

3. **Automated rewriting**:
   ```bash
   # Create rule file
   cat > update-import.yml << 'EOF'
   id: update-import
   language: python
   rule:
     pattern: from old_package import TargetType
   fix: from new_package import TargetType
   EOF

   # Apply
   uv run ast-grep scan --inline-rules 'update-import.yml' --update-all
   ```

4. **Verify**:
   ```bash
   uv run pyright
   uv run pytest
   ```

5. **Clean up**: Remove old type definition, update documentation

This approach combines ast-grep's search capabilities (find all usages) with its rewriting capabilities (mechanical
transformations), falling back to manual edits only when needed.

## Output Interpretation

### Understanding Text Output

```
Found 3 matches:

path/to/file.py:45-52
def compute_value(x: int, y: int) -> int:
    result = x + y
    return result
```

- **File path**: Exact location
- **Line range**: Start-end lines (inclusive)
- **Code**: Complete matched block with context

### Understanding JSON Output

```json
{
  "file": "path/to/file.py",
  "start": {"line": 45, "column": 0},
  "end": {"line": 52, "column": 0},
  "text": "def compute_value...",
  "metaVariables": {"$$$": ["x: int, y: int"]}
}
```

## Why ast-grep Over Grep

| Aspect              | ast-grep                     | Grep                     |
|---------------------|------------------------------|--------------------------|
| Syntax awareness    | ✅ Understands Python         | ❌ Text matching only     |
| False positives     | ✅ None from comments/strings | ❌ Many false positives   |
| Multi-line patterns | ✅ Handles naturally          | ❌ Complex/impossible     |
| Structural context  | ✅ Captures scope/hierarchy   | ❌ No context             |
| Refactoring safety  | ✅ Finds all real usages      | ❌ Misses or over-matches |

## Troubleshooting

### Pattern doesn't match anything

- Verify the pattern matches actual Python syntax
- Try a simpler pattern first, then add constraints
- Use `def $FUNC($$$)` to match any function and see structure

### Too many results

- Add more specific constraints to pattern
- Scope search to specific directories
- Add parameter or return type constraints

### Pattern syntax error

- Check that pattern is valid Python syntax
- Ensure proper use of wildcards (`$$$`, `$_`, `$VAR`)
- Test pattern with simpler version first

## Integration with Other Tools

**Before using ast-grep:**

- Use Glob to identify which files to search (if needed)

**After using ast-grep:**

- Use Read to examine matched files in detail
- Use Edit to make changes to matched locations
- Use pyright, ruff, vulture to verify changes don't break code

## Best Practices

1. **Always use ast-grep for code** - Never use Grep for Python code searches
2. **Start broad, then narrow** - Begin with simple pattern, add constraints as needed
3. **Verify before refactoring** - Always search before renaming/deleting code
4. **Check all results** - Review every match before making changes
5. **Test patterns** - Use small scope first to verify pattern works
6. **Document findings** - Note what you found and why it matters

## Examples from Ceridwen Project

### Finding all uses of a type

```bash
# Before refactoring DecimalValue type
cd packages && uv run ast-grep run --pattern "$_: DecimalValue" --lang python --json
```

### Finding all calls to a compiler function

```bash
# Before changing emit_expression signature
cd packages/ceridwen-compiler && uv run ast-grep run --pattern "emit_expression($$$)" --lang python --json
```

### Finding all class instantiations

```bash
# Finding all WAT module creations
uv run ast-grep run --pattern "WATModule($$$)" --lang python --json
```

### Finding decorator usage

```bash
# Finding all host functions
cd packages/ceridwen-runtime && uv run ast-grep run --pattern "@host_function" --lang python --json
```

Always cite which code locations you found using ast-grep when documenting refactoring or analysis work.
