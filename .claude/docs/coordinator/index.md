# Coordinator Startup Procedures

**Navigation index for coordinator startup documentation.**

---

## Startup Documents

| Document                                   | Purpose                       |
|--------------------------------------------|-------------------------------|
| [startup-overview.md](startup-overview.md) | High-level startup flow       |
| [fresh-start.md](fresh-start.md)           | New session initialization    |
| [resume.md](resume.md)                     | Resuming interrupted sessions |

---

## Startup Flow Summary

```
Session Start
    │
    ├── Fresh Start (no existing state)
    │   └── See: fresh-start.md
    │
    └── Resume (state file exists)
        └── See: resume.md
```

---

## Related Documentation

| Document                                                            | Purpose                  |
|---------------------------------------------------------------------|--------------------------|
| [coordinator-startup.md](../coordinator-startup.md)                 | Main startup reference   |
| [coordinator-configuration.md](../coordinator-configuration.md)     | Configuration thresholds |
| [coordinator-execution-model.md](../coordinator-execution-model.md) | Execution loop           |
| [coordinator-templates.md](../coordinator-templates.md)             | Reusable templates       |

---

## Cross-References

- **[Documentation Index](../index.md)** - Navigation hub for all docs
- [State Management](../state-management.md) - State file handling
- [Recovery Procedures](../recovery-procedures.md) - Error recovery
