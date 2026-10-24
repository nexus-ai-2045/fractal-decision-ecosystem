# FDE Invention Record

Status: private working record. Do not publish.

## Current Recorded Decisions

- Inventor(s): user-confirmed sole inventor. Legal filing name to be entered at filing time.
- Owner: user.
- Assignee: none / unassigned.
- Patent / filing details: intentionally broad unless a separate filing action is approved.
- Guard wording: use `Patent Pending` / `特許出願中` only after an application is actually filed.
- Public release: hold until explicit repository visibility approval is recorded.

## Protectable Surfaces To Preserve

- Recursive core / router / leaf skill-routing architecture.
- Source-pointer-only runtime shim pattern.
- Trigger-gap and runtime-coverage validation.
- Human approval boundary coupled to publication, external send, hooks, settings, auth, credentials, and repository visibility.
- Done-verification closeout before completion claims.
- Public/private split that exposes only an abstract kernel.

## Evidence To Preserve

- Git commit history.
- Draft timestamps.
- Prompt and design notes.
- Generated 50-skill layer.
- Validation outputs.
- Rights and license changes.
- Provisional patent disclosure draft (local-only; removed from public git tracking
  2026-07 after an unintended public exposure, see `PATENT_DISCLOSURE_RECORD.md`).
- Patent packet PDF and SHA256 manifest (local-only generation via
  `scripts/build_patent_packet.py`; not tracked in the public repository).
- Pre-publication gate output from `python scripts\pre_publication_gate_check.py --json`.
- Private MVP gate output from `pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_mvp_gate.ps1`.
- Test output from `python -m pytest -q`.

## Do Not Publish Without Explicit Release Approval

- Full recursive skill list.
- Generator source.
- Internal source pointers.
- Local file paths.
- Absorbed dialogues.
- External AI route registry.
- Private guarantee scripts.
- This invention record.
