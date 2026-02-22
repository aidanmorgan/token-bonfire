# Conflict Handling

[<-- Back to Concurrency Index](index.md)

Runtime conflict detection and resolution when developers discover file access issues during implementation.

## File Conflict Signal

If a developer discovers they need a file outside their task's ownership scope:

```
FILE_CONFLICT: [file_path]

Task: [task_id]
I Need To: [description of needed change]
Reason: [why this file must be modified]
Can Wait: [YES | NO]
```

This is sent via `SendMessage({ type: "message", recipient: "team-lead", content: "...", summary: "..." })`.

### Team Lead Response

On receiving `FILE_CONFLICT`, the team lead:

1. **Identifies the owner**: Check which developer's task owns the conflicting file (from task descriptions)

2. **If no conflict exists** (file is not owned by another active task):
   - Send message to the requesting developer: "No conflict detected. Proceed with modification."

3. **If the owning task is nearly complete** (already in review or audit):
   - Send message to the requesting developer: "File owned by [task-id] (in review). Wait for completion — dependency will auto-unblock."

4. **If active conflict exists**:
   - Send messages to both developers to coordinate:
     - Assign a single owner for the file
     - The other developer yields and works on non-conflicting parts
     - Or restructure to avoid the shared file

5. **For shared files** (`__init__.py`, config, type exports):
   - Send message to the requesting developer: "Shared file. Make additive-only changes (append imports/exports, never restructure). Read current state first."

## Merge Conflict Recovery

If git merge conflicts occur despite precautions, the team lead routes to `remediation`:

```
SendMessage({
  type: "message",
  recipient: "remediation",
  content: "MERGE_CONFLICT\n\nFiles: [list]\nTask: [task_id]\nResolve merge conflicts preserving both changes where possible.",
  summary: "Merge conflict in [files]"
})
```

The `remediation` teammate resolves the conflicts and signals `REMEDIATION_COMPLETE` when done.

---

[<-- Back to Concurrency Index](index.md)
