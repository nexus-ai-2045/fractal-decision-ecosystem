# FDE impact-ordered TODO execution log

Date: 2026-07-01
Scope: private repository operation only

This file records the TODO inventory requested for FDE and the execution status for the current local cycle. It does not approve public release, external sending, repository visibility changes, patent filing, or announcement.

## Priority Rule

Higher impact means a task protects more of the operating surface, has higher blast radius if wrong, or gates later work.

Order:

1. Private MVP / safety gates
2. Roadmap and operating contract
3. Publication and rights boundary
4. Test plan and regression coverage
5. Operational closeout evidence
6. Optional external approval work

## Executed TODOs

| impact | todo | design / plan | test plan | implementation | test result | operation guarantee |
|---:|---|---|---|---|---|---|
| P0 | Verify private MVP gate still runs from the supported Windows entrypoint | Use `scripts/run_mvp_gate.ps1` as the top-level wrapper so Python launcher differences are absorbed | Run wrapper and require the real MVP gate marker/output, not only exit 0 | No code change needed | `FDE MVP GATE CHECK OK`; `external_actions_performed: false` | Private local MVP remains complete; public release is still approval-gated |
| P0 | Verify roadmap contract remains connected to the MVP gate | Keep `ROADMAP.md` as goal/evidence/gate/owner/done_when contract, not a feature wishlist | Run `scripts/roadmap_gate_check.py` | No code change needed | `FDE ROADMAP GATE CHECK OK`; `first_iteration_status: ready` | Roadmap gate remains operationally connected |
| P1 | Verify pre-publication packet and public-kernel boundary | Treat public kernel as a candidate only; keep private operating package and rights/patent boundaries separate | Run `scripts/pre_publication_gate_check.py --json` and inspect blockers | No code change needed | `overall: ok`; remaining blocker is exact GitHub visibility approval before public release | Pre-publication packet is locally consistent, but publication remains unapproved |
| P1 | Verify public readiness check | Confirm required files, links, handle/path patterns, workflow contract, and guarantee wording | Run `scripts/public_ready_check.py` | No code change needed | `PUBLIC READY CHECK PASSED` | Public-readiness checks pass locally without performing publication |
| P1 | Verify test suite | Keep focused regression tests around gates, ADR numbering, local AI workspace boundary, and wrapper behavior | Run `python -m pytest -q` | No code change needed | `13 passed` | Regression coverage is green for the current gate surface |
| P2 | Verify syntax/import surface | Compile scripts and tests | Run `python -m compileall -q scripts tests` | No code change needed | Passed with no output | Python files compile cleanly |
| P2 | Verify whitespace/diff hygiene | Keep changes reviewable before handoff | Run `git diff --check` | This TODO log added after the initial clean diff check | Initial check passed; rerun after this file if committing | No whitespace issue observed before adding this log |

## Active External / Human-Gated TODOs

These remain intentionally incomplete because executing them would cross a human-review or external-action boundary.

| impact | todo | why not executed now | trigger to resume | required gate |
|---:|---|---|---|---|
| P0 | Change GitHub repository visibility | Visibility change is a public/destructive action | User explicitly approves the exact `owner/name` repository in the current conversation | Publication containment gate plus README, license, SECURITY.md, secret scan, personal path scan, and `PUBLIC_READY.md` review |
| P0 | Public release / external send / announcement | External/public action is not authorized by local gate success | User asks for a specific public action and gives explicit approval after review | Human review and publication containment gate |
| P1 | Patent filing submission | Filing is optional external work, not local implementation residue | User chooses a filing path and explicitly approves submission | Filing packet review, receipt capture, application number/hash storage |
| P1 | Use `Patent Pending` / `特許出願中` wording | Current docs forbid it until an application is actually filed | Filing has actually occurred and evidence is stored | Rights/patent wording review |
| P2 | Calendar 12-month nonprovisional / PCT follow-up | Only meaningful if a filing exists | Filing receipt exists | Calendar/reminder creation with explicit approval if it writes outside the repo |

## Current Local Evidence

- `pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_mvp_gate.ps1`: OK
- `python scripts\roadmap_gate_check.py`: OK
- `python scripts\pre_publication_gate_check.py --json`: OK
- `python scripts\public_ready_check.py`: OK
- `python -m pytest -q`: 13 passed
- `python -m compileall -q scripts tests`: OK
- `git diff --check`: OK before this log was added

## Next Closeout Rule

Before saying "residue zero" again, rerun the supported closeout bundle:

1. `pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_mvp_gate.ps1`
2. `python scripts\roadmap_gate_check.py`
3. `python -m compileall -q scripts tests`
4. `python -m pytest -q`
5. `git diff --check`
6. Confirm no public/external/visibility action was performed unless explicitly approved.
