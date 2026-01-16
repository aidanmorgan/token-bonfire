# MCP Servers Guide

This document explains how to interpret and use the `MCP_SERVERS` table provided at agent dispatch time.
The actual available servers are configured per-environment and provided in the orchestrator prompt.

---

## What is MCP?

MCP (Model Context Protocol) servers extend agent capabilities beyond native Claude Code tools. They provide:

- **Extended capabilities**: Access to systems native tools cannot reach (containers, APIs, persistent storage)
- **Specialized operations**: Domain-specific functions optimized for particular tasks
- **Integration**: Connection to external services and platforms

---

## How You Receive MCP Information

At dispatch time, you receive an `MCP_SERVERS` table listing available functions:

```
MCP_SERVERS:
| Server | Function | Example | Use When |
|--------|----------|---------|----------|
| ... rows from configuration ... |
```

**This table is your source of truth.** Only invoke functions listed in your table.

---

## Interpreting the MCP_SERVERS Table

### Column Definitions

| Column       | Meaning                                               |
|--------------|-------------------------------------------------------|
| **Server**   | The MCP server name (e.g., `devcontainers`, `github`) |
| **Function** | The specific function to call on that server          |
| **Example**  | Example invocation showing required parameters        |
| **Use When** | Guidance on when this function is appropriate         |

### Reading an Entry

Given a row like:

```
| devcontainers | devcontainer_exec | `mcp__devcontainers__devcontainer_exec(workspace="/project", command="pytest")` | Running commands in container env |
```

This tells you:

- **Server**: `devcontainers`
- **Function**: `devcontainer_exec`
- **How to call**: `mcp__devcontainers__devcontainer_exec(workspace="/project", command="pytest")`
- **When**: When you need to run commands inside a container environment

---

## Invocation Pattern

All MCP functions follow this pattern:

```
mcp__[server_name]__[function_name](parameters)
```

The **Example** column in your table shows the exact syntax with required parameters.

### Parameter Types

- **String parameters**: Quoted values like `workspace="/project"`
- **Boolean parameters**: `true` or `false`
- **Optional parameters**: May be omitted if not needed
- **List parameters**: JSON array syntax `["item1", "item2"]`

---

## MCP vs Native Tools Decision

**General Rule**: Prefer native tools for standard operations. Use MCP only when:

1. Native tools cannot accomplish the task
2. MCP provides significantly better ergonomics
3. The `Use When` column matches your situation

### Native Tool Coverage

| Operation      | Native Tool | Use MCP When                                                        |
|----------------|-------------|---------------------------------------------------------------------|
| Read files     | `Read`      | Need metadata (size, timestamps)                                    |
| Write files    | `Write`     | Need auto-directory creation                                        |
| Edit files     | `Edit`      | -                                                                   |
| Search files   | `Glob`      | -                                                                   |
| Search content | `Grep`      | -                                                                   |
| Run commands   | `Bash`      | Need container execution, structured output, or dependency tracking |

### When MCP is Required

Use MCP when your table shows a function for:

- Container execution (native Bash cannot reach containers)
- External API access (GitHub, etc.)
- Cross-session persistence
- Complex command orchestration

---

## Availability Checking

**CRITICAL**: Only invoke functions listed in your `MCP_SERVERS` table.

Before using an MCP function:

1. Check if the server appears in your table
2. Check if the specific function is listed
3. Follow the example syntax exactly

If a function is NOT in your table:

- The MCP server is not configured for this session
- Use alternative approaches (native tools, Bash commands)
- Do NOT guess or assume availability

---

## Error Handling

When an MCP call fails:

1. **Check the error message** - It may indicate parameter issues
2. **Verify you matched the example syntax** - Parameters are order and type sensitive
3. **Fall back to native tools** - If appropriate for the operation
4. **Report in your signal** - Include MCP failures in your status

---

## Agent-Specific Guidance

### Developer Agents

Check your `MCP_SERVERS` table for:

- Container execution functions (for verification commands with container environments)
- Sequential execution functions (for complex build/test sequences)

### Auditor Agents

Check your `MCP_SERVERS` table for:

- Container execution (running tests in container environments)
- CI/GitHub functions (checking PR status)

### Remediation Agents

Check your `MCP_SERVERS` table for:

- Container execution (diagnosing container issues)
- Sequential execution (running diagnostic sequences)

### Expert Agents

Check your `MCP_SERVERS` table for:

- Memory/persistence functions (caching research)
- Domain-specific functions relevant to your expertise

---

## Do Not Assume

This guide explains the MCP concept and invocation pattern. The actual available servers and functions are:

1. Defined in `base_variables.md` for the environment
2. Populated into the orchestrator prompt at generation time
3. Provided to you in the `MCP_SERVERS` table at dispatch

**Always consult your provided table, not this guide, for what's available.**

---

## Cross-References

- [Agent Conduct](agent-conduct.md) - General agent behavior rules
- [Environment Verification](environment-verification.md) - Multi-environment execution
- [State Management](state-management.md) - When to use MCP memory vs state file
