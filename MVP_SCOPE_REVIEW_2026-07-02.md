# FDE MVP Scope Review - 2026-07-02

Status: local smoke / preflight review complete

External actions: none

## Purpose

This review captures the current FDE MVP scope before continuing the remaining implementation roadmap.

It does not approve public release, repository visibility change, external sending, patent filing, or announcement.

## Smoke And Preflight Evidence

| check | result |
|---|---|
| `git status --short --branch` | `## codex/unimplemented-roadmap-20260702` |
| `python scripts\roadmap_gate_check.py --json` | `overall: ok`, `external_actions_performed: false` |
| `python scripts\pre_publication_gate_check.py --json` | `overall: ok`, blocker remains exact GitHub visibility approval before public release |
| `python scripts\public_ready_check.py` | `PUBLIC READY CHECK PASSED` |
| `python -m pytest -q` | `18 passed` |
| `pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_mvp_gate.ps1` | `FDE MVP GATE CHECK OK` |
| `python -m compileall -q scripts tests` | ok |

## MVP Content Summary

FDE is a local decision and routing OS. Its core shape is:

```text
entry -> packet -> evidence -> decision -> closure
```

The current private MVP contains:

- Root routing and operating rules for decision work.
- A roadmap gate that keeps `goal / evidence / gate / owner / done_when` visible.
- Public-readiness and pre-publication gates that do not perform external actions.
- ADR numbering and local decision records.
- Product / Creative review path through `visual.html`, `README.md`, `ROADMAP.md`, `OPERATIONAL_GUARANTEE.md`, and public-kernel materials.
- AI contact safety contract that keeps product transport out of FDE and returns contact ideas to identity, consent, data boundary, evidence, decision, and closure.
- Post-merge receipts for FDE PR #7 and #8.

## Scope Boundary

In scope for FDE:

- Routing, decision contracts, operating cards, source pointers, fact gates, review path, completion semantics.
- AI contact safety contract as an abstract decision contract.
- Public-kernel / private-package boundary checks.
- Eval-style checks for whether FDE routes the right gate.

Out of scope for FDE:

- Device app, OS service, avatar, voice UI, Bluetooth, Wi-Fi, P2P, cloud relay.
- Actual external AI contact or external sending.
- LCS product UX, onboarding, data download, contact card implementation.
- GitHub public visibility change, public release, patent filing, announcement.

## Review Findings

1. Sprint 0 is locally complete.
   Post-merge receipts for PR #7 and #8 are recorded in `OPERATIONAL_GUARANTEE.md`.

2. Sprint 1 is locally complete.
   Roadmap drift is guarded by `scripts/roadmap_gate_check.py` and `tests/test_public_ready.py`.

3. Sprint 2 is the next FDE-native work.
   The next implementation should harden `ai-contact-safety-contract.md` with contact packet schema candidates and tests for blocked, revocation, replay protection, TTL, checksum, and human approval.

4. Publication remains approval-gated.
   Local pre-publication checks pass, but exact repository visibility approval is still a human/external blocker.

## Next Gate

Before starting Sprint 2, run:

```powershell
python -m pytest -q
pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_mvp_gate.ps1
```

If Sprint 2 adds schema-like examples or fixtures, connect them to `tests/test_public_ready.py` and keep transport implementation explicitly out of scope.
