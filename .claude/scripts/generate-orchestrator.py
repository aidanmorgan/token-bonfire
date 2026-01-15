#!/usr/bin/env python3
"""Generate orchestrator prompt from template and base variables.

Usage:
    python generate-orchestrator.py <plan_file>

Example:
    python generate-orchestrator.py COMPREHENSIVE_IMPLEMENTATION_PLAN.md

Creates:
    .claude/plans/<slug>.md - The processed orchestrator prompt
    .claude/plans/<slug>/ - Directory for state and event log
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import NamedTuple, TypeAlias, TypeGuard

# =============================================================================
# Type Aliases
# =============================================================================

TableRow: TypeAlias = dict[str, str]
TableData: TypeAlias = list[TableRow]


# =============================================================================
# Enums
# =============================================================================


class FilePath(str, Enum):
    """Standard file paths relative to repository root."""

    BASE_VARIABLES = ".claude/base_variables.md"
    TEMPLATE = ".claude/prompts/industrial_society_and_its_prompts.md"
    PLANS_DIR = ".claude/plans"


class FilePathTemplate(str, Enum):
    """File path templates with placeholders."""

    STATE_FILE = ".claude/plans/{slug}/coordination-state.json"
    EVENT_LOG = ".claude/plans/{slug}/event-log.jsonl"
    OUTPUT_FILE = ".claude/plans/{slug}.md"


class SectionHeader(str, Enum):
    """Markdown section headers in base_variables.md."""

    CORE_FILES = "## Core Files"
    THRESHOLDS = "## Thresholds"
    PARALLEL_LIMITS = "## Parallel Execution Limits"
    AGENT_MODELS = "## Agent Models"
    ENVIRONMENTS = "## Environments"
    AGENT_DOCS = "## Agent Reference Documents"
    DEVELOPER_COMMANDS = "### Developer Commands"
    VERIFICATION_COMMANDS = "### Verification Commands"


class VariableKey(str, Enum):
    """Known variable keys used in templates."""

    PLAN_FILE = "PLAN_FILE"
    STATE_FILE = "STATE_FILE"
    EVENT_LOG_FILE = "EVENT_LOG_FILE"
    USAGE_SCRIPT = "USAGE_SCRIPT"
    WORKING_DIR = "WORKING_DIR"
    AGENT_MODELS = "AGENT_MODELS"
    ENVIRONMENTS = "ENVIRONMENTS"
    AGENT_DOCS = "AGENT_DOCS"
    DEVELOPER_COMMANDS = "DEVELOPER_COMMANDS"
    VERIFICATION_COMMANDS = "VERIFICATION_COMMANDS"


class ColumnName(str, Enum):
    """Standard column names in markdown tables."""

    VARIABLE = "Variable"
    VALUE = "Value"
    DESCRIPTION = "Description"
    PATTERN = "Pattern"
    AGENT = "Agent"
    ENVIRONMENT = "Environment"
    MUST_READ = "Must Read"
    PURPOSE = "Purpose"
    NAME = "Name"
    HOW_TO_EXECUTE = "How to Execute"
    AGENT_TYPE = "Agent Type"
    MODEL = "Model"
    TASK = "Task"
    COMMAND = "Command"
    CHECK = "Check"
    EXIT_CODE = "Exit Code"


class RowKey(str, Enum):
    """Normalized row keys (lowercase, underscored)."""

    VARIABLE = "variable"
    VALUE = "value"
    PATTERN = "pattern"


class ParseState(Enum):
    """State machine states for table parsing."""

    SEARCHING = auto()
    IN_TABLE = auto()
    HEADERS_FOUND = auto()


# =============================================================================
# Named Tuples (Immutable Configuration)
# =============================================================================


class CoreFileDefinition(NamedTuple):
    """Definition of a core file variable."""

    variable: VariableKey
    default_value: str
    description: str


class ColumnSet(NamedTuple):
    """A set of columns for a table."""

    columns: tuple[ColumnName, ...]

    def to_strings(self) -> tuple[str, ...]:
        """Convert to string tuple for table generation."""
        return tuple(col.value for col in self.columns)


class TableParseConfig(NamedTuple):
    """Configuration for parsing a markdown table."""

    section: SectionHeader
    columns: ColumnSet
    variable_key: VariableKey | None = None
    filter_row_key: RowKey | None = None


class TableReplaceConfig(NamedTuple):
    """Configuration for replacing a table in the template."""

    variable_key: VariableKey
    columns: ColumnSet
    pattern: str
    skip_header_lines: int = 0


class ParsedTableResult(NamedTuple):
    """Result of parsing a table section."""

    rows: TableData
    simple_variables: dict[str, str]


class ResolvedPaths(NamedTuple):
    """Resolved file paths for generation."""

    base_variables: Path
    template: Path
    plans_dir: Path


class SlugPaths(NamedTuple):
    """Paths derived from a slug."""

    state_file: str
    event_log: str
    output_dir: Path
    output_file: Path


# =============================================================================
# Configuration Constants
# =============================================================================

CORE_FILE_DEFINITIONS: tuple[CoreFileDefinition, ...] = (
    CoreFileDefinition(
        VariableKey.PLAN_FILE,
        "",
        "Implementation plan to execute",
    ),
    CoreFileDefinition(
        VariableKey.STATE_FILE,
        "",
        "Coordinator state persistence",
    ),
    CoreFileDefinition(
        VariableKey.EVENT_LOG_FILE,
        "",
        "Event store for all coordinator operations and agent results",
    ),
    CoreFileDefinition(
        VariableKey.USAGE_SCRIPT,
        ".claude/scripts/get-claude-usage.py",
        "Session usage monitoring",
    ),
    CoreFileDefinition(
        VariableKey.WORKING_DIR,
        ".tmp",
        "Directory for agent temporary files and scratch content",
    ),
)

CORE_FILES_COLUMNS = ColumnSet((ColumnName.VARIABLE, ColumnName.VALUE, ColumnName.DESCRIPTION))
ENVIRONMENTS_COLUMNS = ColumnSet((ColumnName.NAME, ColumnName.DESCRIPTION, ColumnName.HOW_TO_EXECUTE))
AGENT_MODELS_COLUMNS = ColumnSet((ColumnName.AGENT_TYPE, ColumnName.MODEL, ColumnName.DESCRIPTION))
AGENT_DOCS_COLUMNS = ColumnSet(
    (ColumnName.PATTERN, ColumnName.AGENT, ColumnName.ENVIRONMENT, ColumnName.MUST_READ, ColumnName.PURPOSE)
)
DEVELOPER_COMMANDS_COLUMNS = ColumnSet((ColumnName.TASK, ColumnName.ENVIRONMENT, ColumnName.COMMAND, ColumnName.PURPOSE))
VERIFICATION_COMMANDS_COLUMNS = ColumnSet(
    (ColumnName.CHECK, ColumnName.ENVIRONMENT, ColumnName.COMMAND, ColumnName.EXIT_CODE, ColumnName.PURPOSE)
)

TABLE_PARSE_CONFIGS: tuple[TableParseConfig, ...] = (
    TableParseConfig(
        section=SectionHeader.CORE_FILES,
        columns=CORE_FILES_COLUMNS,
    ),
    TableParseConfig(
        section=SectionHeader.THRESHOLDS,
        columns=CORE_FILES_COLUMNS,
    ),
    TableParseConfig(
        section=SectionHeader.PARALLEL_LIMITS,
        columns=CORE_FILES_COLUMNS,
    ),
    TableParseConfig(
        section=SectionHeader.AGENT_MODELS,
        columns=AGENT_MODELS_COLUMNS,
        variable_key=VariableKey.AGENT_MODELS,
    ),
    TableParseConfig(
        section=SectionHeader.ENVIRONMENTS,
        columns=ENVIRONMENTS_COLUMNS,
        variable_key=VariableKey.ENVIRONMENTS,
    ),
    TableParseConfig(
        section=SectionHeader.AGENT_DOCS,
        columns=AGENT_DOCS_COLUMNS,
        variable_key=VariableKey.AGENT_DOCS,
        filter_row_key=RowKey.PATTERN,
    ),
    TableParseConfig(
        section=SectionHeader.DEVELOPER_COMMANDS,
        columns=DEVELOPER_COMMANDS_COLUMNS,
        variable_key=VariableKey.DEVELOPER_COMMANDS,
    ),
    TableParseConfig(
        section=SectionHeader.VERIFICATION_COMMANDS,
        columns=VERIFICATION_COMMANDS_COLUMNS,
        variable_key=VariableKey.VERIFICATION_COMMANDS,
    ),
)

TABLE_REPLACE_CONFIGS: tuple[TableReplaceConfig, ...] = (
    TableReplaceConfig(
        variable_key=VariableKey.ENVIRONMENTS,
        columns=ENVIRONMENTS_COLUMNS,
        pattern=r"(Variable: `ENVIRONMENTS`\s*\n\n[^\n]*\n\n)(\|[^\n]+\|(?:\n\|[^\n]+\|)*)",
    ),
    TableReplaceConfig(
        variable_key=VariableKey.AGENT_MODELS,
        columns=AGENT_MODELS_COLUMNS,
        pattern=r"(Variable: `AGENT_MODELS`\s*\n\n[^\n]*\n\n)(\|[^\n]+\|(?:\n\|[^\n]+\|)*)",
    ),
    TableReplaceConfig(
        variable_key=VariableKey.AGENT_DOCS,
        columns=AGENT_DOCS_COLUMNS,
        pattern=r"(\| Pattern \| Agent \| Environment \| Must Read \| Purpose \|\n\|[^\n]+\|\n)(\|[^\n]+\|(?:\n\|[^\n]+\|)*)",
        skip_header_lines=2,
    ),
    TableReplaceConfig(
        variable_key=VariableKey.DEVELOPER_COMMANDS,
        columns=DEVELOPER_COMMANDS_COLUMNS,
        pattern=r"(Variable: `DEVELOPER_COMMANDS`\s*\n\n[^\n]*\n[^\n]*\n[^\n]*\n\n)(\|[^\n]+\|(?:\n\|[^\n]+\|)*)",
    ),
    TableReplaceConfig(
        variable_key=VariableKey.VERIFICATION_COMMANDS,
        columns=VERIFICATION_COMMANDS_COLUMNS,
        pattern=r"(Variable: `VERIFICATION_COMMANDS`\s*\n\n[^\n]*\n[^\n]*\n[^\n]*\n\n)(\|[^\n]+\|(?:\n\|[^\n]+\|)*)",
    ),
)

CORE_FILES_PATTERN = r"(### Core Files\s*\n\n)(\|[^\n]+\|(?:\n\|[^\n]+\|)*)"


# =============================================================================
# Type Guards
# =============================================================================


def is_valid_table_row(value: object) -> TypeGuard[TableRow]:
    """Check if a value is a valid table row (dict[str, str])."""
    if not isinstance(value, dict):
        return False
    return all(isinstance(k, str) and isinstance(v, str) for k, v in value.items())


def is_valid_table_data(value: object) -> TypeGuard[TableData]:
    """Check if a value is valid table data (list[dict[str, str]])."""
    if not isinstance(value, list):
        return False
    return all(is_valid_table_row(row) for row in value)


def is_table_line(line: str) -> TypeGuard[str]:
    """Check if a line is a markdown table row."""
    stripped = line.strip()
    return stripped.startswith("|") and stripped.endswith("|")


def has_required_key(row: TableRow, key: RowKey) -> TypeGuard[TableRow]:
    """Check if a row has a required key with a non-empty value."""
    return key.value in row and bool(row[key.value].strip())


def is_separator_row(cells: list[str]) -> bool:
    """Check if cells represent a markdown table separator row."""
    if not cells:
        return False
    return all(cell.replace("-", "").replace(":", "").strip() == "" for cell in cells)


def is_variable_row(row: TableRow) -> TypeGuard[TableRow]:
    """Check if a row contains variable definitions."""
    return has_required_key(row, RowKey.VARIABLE)


# =============================================================================
# Dataclasses (Mutable/Complex State)
# =============================================================================


@dataclass
class Variables:
    """Container for all parsed and derived variables."""

    simple: dict[str, str] = field(default_factory=dict)
    tables: dict[str, TableData] = field(default_factory=dict)

    def get(self, key: str | VariableKey, default: str = "") -> str:
        """Get a simple variable value."""
        key_str = key.value if isinstance(key, VariableKey) else key
        return self.simple.get(key_str, default)

    def set(self, key: str | VariableKey, value: str) -> None:
        """Set a simple variable value."""
        key_str = key.value if isinstance(key, VariableKey) else key
        self.simple[key_str] = value

    def get_table(self, key: str | VariableKey) -> TableData:
        """Get a table variable value."""
        key_str = key.value if isinstance(key, VariableKey) else key
        return self.tables.get(key_str, [])

    def set_table(self, key: str | VariableKey, data: TableData) -> None:
        """Set a table variable value."""
        key_str = key.value if isinstance(key, VariableKey) else key
        if is_valid_table_data(data):
            self.tables[key_str] = data

    def update_simple(self, updates: dict[str, str]) -> None:
        """Update multiple simple variables."""
        self.simple.update(updates)


@dataclass(frozen=True)
class GenerationResult:
    """Immutable result of orchestrator generation."""

    plan_file: str
    slug: str
    state_file: str
    event_log: str
    output_file: Path

    def print_summary(self) -> None:
        """Print a formatted summary of the generation."""
        separator = "=" * 60
        lines = [
            "",
            separator,
            "ORCHESTRATOR GENERATED",
            separator,
            f"Plan: {self.plan_file}",
            f"State: {self.state_file}",
            f"Events: {self.event_log}",
            f"Output: {self.output_file}",
            separator,
        ]
        print("\n".join(lines))


# =============================================================================
# Pure Functions - String Processing
# =============================================================================


def slugify(name: str) -> str:
    """Convert a filename to a URL-friendly slug.

    Examples:
        >>> slugify("COMPREHENSIVE_IMPLEMENTATION_PLAN")
        'comprehensive-implementation-plan'
        >>> slugify("my-feature-plan")
        'my-feature-plan'
        >>> slugify("AuthFeaturePlan")
        'auth-feature-plan'
    """
    slug = name.lower()
    slug = slug.replace("_", "-")
    slug = re.sub(r"([a-z])([A-Z])", r"\1-\2", slug)
    slug = re.sub(r"-+", "-", slug)
    return slug.strip("-")


def derive_slug_from_path(plan_file: str) -> str:
    """Derive a slug from a plan file path."""
    stem = Path(plan_file).stem
    return slugify(stem)


def normalize_header(header: str) -> str:
    """Normalize a table header to a dict key."""
    return header.lower().replace(" ", "_")


def strip_backticks(value: str) -> str:
    """Remove surrounding backticks from a value."""
    return value.strip("`").strip()


def wrap_backticks(value: str) -> str:
    """Wrap a value in backticks."""
    return f"`{value}`"


# =============================================================================
# Pure Functions - Table Parsing
# =============================================================================


def parse_table_cells(line: str) -> list[str]:
    """Parse a markdown table row into cells."""
    if not is_table_line(line):
        return []
    return [cell.strip() for cell in line.split("|")[1:-1]]


def cells_to_row(cells: list[str], headers: list[str]) -> TableRow:
    """Convert cells and headers to a table row dict."""
    return {
        headers[i]: strip_backticks(cell)
        for i, cell in enumerate(cells)
        if i < len(headers)
    }


def extract_simple_variables(rows: TableData) -> dict[str, str]:
    """Extract simple variable definitions from table rows."""
    variables: dict[str, str] = {}
    for row in rows:
        if is_variable_row(row):
            var_name = strip_backticks(row[RowKey.VARIABLE.value])
            if var_name:
                variables[var_name] = row.get(RowKey.VALUE.value, "")
    return variables


def filter_rows_by_key(rows: TableData, key: RowKey) -> TableData:
    """Filter rows that have a specific key."""
    return [row for row in rows if has_required_key(row, key)]


def parse_markdown_table(text: str, header_pattern: str) -> TableData:
    """Parse a markdown table following a header pattern.

    Uses a state machine for clear parsing logic.

    Args:
        text: The full document text
        header_pattern: String to identify the table section

    Returns:
        List of dicts, one per data row, with normalized header keys
    """
    lines = text.split("\n")
    rows: TableData = []
    headers: list[str] = []
    state = ParseState.SEARCHING

    for line in lines:
        if state == ParseState.SEARCHING:
            if header_pattern in line:
                state = ParseState.IN_TABLE
            continue

        if state == ParseState.IN_TABLE:
            if not line.strip():
                continue

            cells = parse_table_cells(line)
            if not cells:
                continue

            headers = [normalize_header(h) for h in cells]
            state = ParseState.HEADERS_FOUND
            continue

        if state == ParseState.HEADERS_FOUND:
            if not line.strip():
                break

            cells = parse_table_cells(line)
            if not cells:
                break

            if is_separator_row(cells):
                continue

            row = cells_to_row(cells, headers)
            if is_valid_table_row(row):
                rows.append(row)

    return rows


def parse_table_with_config(content: str, config: TableParseConfig) -> ParsedTableResult:
    """Parse a table using configuration and extract variables."""
    rows = parse_markdown_table(content, config.section.value)

    if config.filter_row_key is not None:
        rows = filter_rows_by_key(rows, config.filter_row_key)

    simple_vars: dict[str, str] = {}
    if config.variable_key is None:
        simple_vars = extract_simple_variables(rows)

    return ParsedTableResult(rows=rows, simple_variables=simple_vars)


# =============================================================================
# Pure Functions - Table Generation
# =============================================================================


def generate_table_header(columns: tuple[str, ...]) -> str:
    """Generate markdown table header row."""
    return "| " + " | ".join(columns) + " |"


def generate_table_separator(column_count: int) -> str:
    """Generate markdown table separator row."""
    return "|" + "|".join(["---"] * column_count) + "|"


def generate_table_row(row: TableRow, columns: tuple[str, ...]) -> str:
    """Generate a single markdown table data row."""
    cells = [row.get(normalize_header(col), "") for col in columns]
    return "| " + " | ".join(cells) + " |"


def generate_markdown_table(rows: TableData, columns: ColumnSet) -> str:
    """Generate a markdown table from row data."""
    if not rows:
        return ""

    col_strings = columns.to_strings()
    header = generate_table_header(col_strings)
    separator = generate_table_separator(len(col_strings))
    data_rows = [generate_table_row(row, col_strings) for row in rows]

    return "\n".join([header, separator, *data_rows])


def build_core_file_row(definition: CoreFileDefinition, variables: Variables) -> TableRow:
    """Build a table row for a core file definition."""
    value = variables.get(definition.variable, definition.default_value)
    return {
        RowKey.VARIABLE.value: wrap_backticks(definition.variable.value),
        RowKey.VALUE.value: wrap_backticks(value),
        "description": definition.description,
    }


def build_core_files_table(variables: Variables) -> str:
    """Build the Core Files table with current variable values."""
    rows = [build_core_file_row(defn, variables) for defn in CORE_FILE_DEFINITIONS]
    return generate_markdown_table(rows, CORE_FILES_COLUMNS)


# =============================================================================
# Pure Functions - Template Processing
# =============================================================================


def substitute_variables(text: str, variables: Variables) -> str:
    """Replace {{VARIABLE}} patterns with values."""

    def replacer(match: re.Match[str]) -> str:
        var_name = match.group(1)
        value = variables.get(var_name)
        return value if value else match.group(0)

    return re.sub(r"\{\{(\w+)\}\}", replacer, text)


def replace_table_section(
    content: str,
    pattern: str,
    new_table: str,
    skip_header_lines: int = 0,
) -> str:
    """Replace a table section in the content."""
    if skip_header_lines > 0:
        table_lines = new_table.split("\n")
        new_table = "\n".join(table_lines[skip_header_lines:])

    if re.search(pattern, content):
        return re.sub(pattern, rf"\g<1>{new_table}", content)
    return content


def apply_table_replacement(content: str, config: TableReplaceConfig, variables: Variables) -> str:
    """Apply a single table replacement."""
    table_data = variables.get_table(config.variable_key)
    if not table_data:
        return content

    new_table = generate_markdown_table(table_data, config.columns)
    return replace_table_section(content, config.pattern, new_table, config.skip_header_lines)


def process_template(template_content: str, variables: Variables) -> str:
    """Process the template with variables."""
    content = substitute_variables(template_content, variables)

    core_files_table = build_core_files_table(variables)
    content = replace_table_section(content, CORE_FILES_PATTERN, core_files_table)

    for config in TABLE_REPLACE_CONFIGS:
        content = apply_table_replacement(content, config, variables)

    return content


# =============================================================================
# I/O Functions
# =============================================================================


def resolve_paths(repo_root: Path) -> ResolvedPaths:
    """Resolve standard paths relative to repository root."""
    return ResolvedPaths(
        base_variables=repo_root / FilePath.BASE_VARIABLES.value,
        template=repo_root / FilePath.TEMPLATE.value,
        plans_dir=repo_root / FilePath.PLANS_DIR.value,
    )


def resolve_slug_paths(plans_dir: Path, slug: str) -> SlugPaths:
    """Resolve paths derived from a slug."""
    return SlugPaths(
        state_file=FilePathTemplate.STATE_FILE.value.format(slug=slug),
        event_log=FilePathTemplate.EVENT_LOG.value.format(slug=slug),
        output_dir=plans_dir / slug,
        output_file=plans_dir / f"{slug}.md",
    )


def validate_path_exists(path: Path, description: str) -> None:
    """Validate that a path exists, exit with error if not."""
    if not path.exists():
        print(f"Error: {description} not found at {path}")
        sys.exit(1)


def validate_inputs(paths: ResolvedPaths) -> None:
    """Validate that required input files exist."""
    validate_path_exists(paths.base_variables, "base_variables.md")
    validate_path_exists(paths.template, "Template")


def parse_base_variables(base_vars_path: Path) -> Variables:
    """Parse base_variables.md into structured variables."""
    content = base_vars_path.read_text()
    variables = Variables()

    for config in TABLE_PARSE_CONFIGS:
        result = parse_table_with_config(content, config)
        variables.update_simple(result.simple_variables)

        if config.variable_key is not None:
            variables.set_table(config.variable_key, result.rows)

    return variables


def write_output(output_file: Path, content: str) -> None:
    """Write content to output file."""
    output_file.write_text(content)


def ensure_directory(directory: Path) -> None:
    """Ensure a directory exists."""
    directory.mkdir(parents=True, exist_ok=True)


# =============================================================================
# Main Entry Points
# =============================================================================


def generate_orchestrator(plan_file: str, repo_root: Path | None = None) -> GenerationResult:
    """Generate an orchestrator prompt from a plan file.

    Args:
        plan_file: Path to the implementation plan
        repo_root: Repository root path (defaults to cwd)

    Returns:
        GenerationResult with paths and metadata
    """
    if repo_root is None:
        repo_root = Path.cwd()

    paths = resolve_paths(repo_root)
    validate_inputs(paths)

    slug = derive_slug_from_path(plan_file)
    slug_paths = resolve_slug_paths(paths.plans_dir, slug)

    print(f"Plan file: {plan_file}")
    print(f"Derived slug: {slug}")

    print(f"Reading base variables from {paths.base_variables}")
    variables = parse_base_variables(paths.base_variables)

    variables.set(VariableKey.PLAN_FILE, plan_file)
    variables.set(VariableKey.STATE_FILE, slug_paths.state_file)
    variables.set(VariableKey.EVENT_LOG_FILE, slug_paths.event_log)

    ensure_directory(slug_paths.output_dir)
    print(f"Created directory: {slug_paths.output_dir}")

    print(f"Processing template from {paths.template}")
    template_content = paths.template.read_text()
    content = process_template(template_content, variables)

    write_output(slug_paths.output_file, content)
    print(f"Written orchestrator prompt to: {slug_paths.output_file}")

    return GenerationResult(
        plan_file=plan_file,
        slug=slug,
        state_file=slug_paths.state_file,
        event_log=slug_paths.event_log,
        output_file=slug_paths.output_file,
    )


def main() -> None:
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python generate-orchestrator.py <plan_file>")
        print("Example: python generate-orchestrator.py COMPREHENSIVE_IMPLEMENTATION_PLAN.md")
        sys.exit(1)

    plan_file = sys.argv[1]
    result = generate_orchestrator(plan_file)
    result.print_summary()


if __name__ == "__main__":
    main()
