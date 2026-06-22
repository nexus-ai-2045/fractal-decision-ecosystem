# chinju Agent Guidance

Project: `fde`

Read these files before making changes:

1. `.chinju/README.md`
2. `.chinju/project.md`
3. `.chinju/workflow.md`
4. `.chinju/quality-gates.md`
5. `.chinju/knowledge/invariants.md`
6. `.chinju/knowledge/incidents.md`
7. `.chinju/knowledge/edge-cases.md`

Default loop:

```text
/spec -> implementation -> /regression -> /fix if needed -> /regression -> review
```

Use local checks by default. Ask before sending repository code to an external provider or sub-agent.
Do not overwrite user changes or run destructive git commands without explicit approval.
