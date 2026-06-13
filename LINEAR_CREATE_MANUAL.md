# Manual Linear Issue Creation

Status: ready for manual creation.

This file is the fallback path when no Linear create-issue tool is exposed in the current Codex session.

## Target Issue

- Title: `Prepare FDE public kernel with restrictive rights and defensive patent gate`
- Priority: High
- Status: Todo / Backlog
- Labels: `FDE`, `rights`, `patent`, `public-kernel`, `publication-gate`, `mvp-gate`
- Project: FDE / Fractal Decision Ecosystem, if available
- Assignee: owner

## Body

Paste the full contents of `LINEAR_EXPORT.md` into the issue description.

## Do Not Do In Linear

- Do not mark the work as public-release approved.
- Do not mark FDE as `Patent Pending`.
- Do not treat the issue as patent filing approval.
- Do not treat the issue as GitHub visibility approval.
- Do not attach private source pointers, local paths, absorbed dialogues, or secret material.

## Completion Evidence To Add After Creation

- Linear issue identifier.
- Linear issue URL.
- Date created.
- Whether the issue is in the FDE / Fractal Decision Ecosystem project.
- Whether labels were applied.

## Current Blocker

The Codex session is blocked from creating the Linear issue directly because no reliable Linear write surface is available from the current environment.

Confirmed blockers:

- No Linear create-issue tool is exposed in the current Codex tool surface.
- No local `linear` CLI is available.
- No `LINEAR_*` environment variable or API token is available.
- Chrome extension control is available, but there is no existing Linear tab to continue from.
- Creating the issue through Chrome would require a logged-in Linear browser session and explicit approval to press the final create / submit button because it is an external write action.

Local fallback state:

- `LINEAR_EXPORT.md` is ready to paste into Linear.
- The contents of `LINEAR_EXPORT.md` have been copied to the clipboard.
- After manual creation, record the Linear issue identifier and URL back in this repo.
