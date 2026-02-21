# Conflict Handling

[<-- Back to Concurrency Index](index.md)

Runtime conflict detection and resolution when experts discover file access issues during implementation.

## File Conflict Signal

If an expert discovers they need a file outside their task's ownership scope:

```
FILE_CONFLICT: [file_path]

Task: [task_id]
I Need To: [description of needed change]
Reason: [why this file must be modified]
Can Wait: [YES | NO]
```

This is sent as a mailbox message via `TeammateTool({ operation: "write", to: "team-lead" })`.

### Team Lead Response

On receiving `FILE_CONFLICT`, the team lead:

1. **Identifies the owner**: Check which expert's task owns the conflicting file (from task descriptions)

2. **If no conflict exists** (file is not owned by another active task):
   - `write` to the requesting expert: "No conflict detected. Proceed with modification."

3. **If the owning task is nearly complete** (already in review or audit):
   - `write` to the requesting expert: "File owned by [task-id] (in review). Wait for completion — dependency will auto-unblock."

4. **If active conflict exists**:
   - `write` to both experts to coordinate:
     - Assign a single owner for the file
     - The other expert yields and works on non-conflicting parts
     - Or restructure to avoid the shared file

5. **For shared files** (`__init__.py`, config, type exports):
   - `write` to the requesting expert: "Shared file. Make additive-only changes (append imports/exports, never restructure). Read current state first."

## Merge Conflict Recovery

If git merge conflicts occur despite precautions, the team lead routes to `remediation`:

```
TeammateTool({ operation: "write", to: "remediation", message: "MERGE_CONFLICT\n\nFiles: [list]\nTask: [task_id]\nResolve merge conflicts preserving both changes where possible." })
```

The `remediation` teammate resolves the conflicts and signals `REMEDIATION_COMPLETE` when done.

---

[<-- Back to Concurrency Index](index.md)
