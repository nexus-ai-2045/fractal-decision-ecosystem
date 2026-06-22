# chinju Project Settings

This directory contains the project-local guidance that chinju and AI agents read.

Common edits:

- Project purpose and users: `.chinju/project.md`
- Development loop: `.chinju/workflow.md`
- Test, lint, build, and smoke commands: `.chinju/quality-gates.md`
- Behavior that must not break: `.chinju/knowledge/invariants.md`
- Past bugs and exception handling: `.chinju/knowledge/incidents.md`
- Unusual states, users, inputs, and integrations: `.chinju/knowledge/edge-cases.md`
- Local-first and provider-send policy: `.chinju/policy.json`

Generated artifacts usually live under `.chinju/jobs/`, `.chinju/specs/`,
`.chinju/tui/`, `.chinju/reports/`, `.chinju/usage/`, `.chinju/triage/`,
`.chinju/memory/`, `.chinju/tmp/`, and `.chinju/layout-audit/`. Those paths are
local run output, not the canonical project guidance.

When asking another LLM to update this setup, say something like:

```text
Read .chinju/README.md and update the chinju project guidance so regression
always runs npm test before PR.
```
