# Prepare FDE public kernel with restrictive rights and defensive patent gate

Status: ready to convert into Linear issue.
Priority: High
Labels: FDE, rights, patent, public-kernel, publication-gate, mvp-gate

## Summary

FDE should remain private while rights posture, defensive patent timing, and a minimal sanitized public kernel are tracked as one work item.

The local private MVP gate is implemented. The current blocker is no longer code readiness; it is the human / external decision set around inventor, owner / assignee, and whether to file a defensive provisional patent application before any public disclosure.

## Primary Blocker

Decide whether to self-file a defensive provisional patent application before any public disclosure.

Public release before filing can weaken patent options. Do not mark FDE as `Patent Pending` unless an application has actually been filed.

## Current State

- Repository is private.
- No GitHub visibility change has been performed.
- No external publication action has been performed.
- No patent filing action has been performed.
- No Linear connector write has been performed from this session because a Linear create-issue tool is not currently exposed.
- `LICENSE` has been changed from MIT to a restrictive source-available / all-rights-reserved license.
- Rights and publication planning docs have been drafted:
  - `RIGHTS_NOTICE.md`
  - `PUBLIC_KERNEL_PLAN.md`
  - `DEFENSIVE_PATENT_REVIEW.md`
  - `PROVISIONAL_PATENT_DISCLOSURE_DRAFT.md`
- `public-kernel/` has been created as the sanitized public kernel candidate.
- `patent-packet/` has been created with a printable PDF draft and SHA256 manifest.
- `scripts/pre_publication_gate_check.py` verifies the local pre-publication gate.
- `scripts/mvp_gate_check.py` verifies the local private MVP gate.
- `MVP_STATUS.md` records the private MVP gate state and next milestone.
- Full private FDE / Brain / recursive skill layer should remain private.
- Public release should be a reduced public kernel only.

## Local MVP Gate

Command:

```text
python scripts\mvp_gate_check.py
```

Expected result:

- MVP status is complete for the private local gate.
- Public-readiness check passes.
- Pre-publication gate check passes.
- Pytest passes.
- External actions performed remains false.
- Repository visibility expectation remains private.

## Blockers

1. Confirm inventor name(s).
2. Confirm owner / assignee.
3. Complete provisional patent disclosure packet. Done locally; final human review still required.
4. Add diagrams or flow descriptions before any filing. Done.
5. Decide whether to include generator excerpt or pseudocode. Pseudocode included.
6. Export filing packet to PDF. Done locally.
7. File provisional application or explicitly decide not to file.
8. Save filing receipt, application number, submitted PDF, and file hash.
9. Calendar 12-month nonprovisional / PCT follow-up deadline if filed.
10. Create sanitized public kernel separate from the private repo. Done as `public-kernel/`.
11. Run secret scan and personal-path scan on the sanitized kernel. Done via pre-publication gate.
12. Re-run public-readiness checks after the license and rights changes. Done locally.
13. Get explicit repo-specific human approval before any GitHub visibility change.
14. Keep this Linear issue open until inventor / owner / filing decision is recorded.

## Public Kernel Scope

Publish only:

- Fractal Decision Ecosystem concept overview.
- Abstract recursive map: core / router / leaf.
- Four public gates:
  - pre-execution fact check
  - scope routing
  - publication containment
  - done verification closeout
- Restrictive license and rights notice.

Keep private:

- Full 50-skill recursive implementation.
- Generator internals if they reveal private structure.
- `Documents/brain` pointers.
- Local filesystem paths.
- External AI route registry.
- Absorbed dialogues.
- Machine-specific runtime procedures.
- Private guarantee scripts.
- Patent-candidate implementation details until filing decision is complete.

## Acceptance Criteria

- Patent filing decision is recorded.
- If filed, filing receipt and application number are stored privately.
- `Patent Pending` language is used only after filing.
- Public kernel exists as a separate sanitized artifact.
- Public kernel contains no local paths, private source pointers, secrets, private workflow details, or absorbed dialogue content.
- License posture remains source-available / all rights reserved / no patent license / no trademark license / no derivative works / no model training.
- `PUBLIC_READY.md` is updated after current rights posture and checks.
- `MVP_STATUS.md` records the private local MVP gate state.
- `scripts/mvp_gate_check.py` passes locally.
- No repository is made public without explicit current-conversation approval.

## Suggested Linear Fields

- Title: Prepare FDE public kernel with restrictive rights and defensive patent gate
- Priority: High
- Status: Todo / Backlog
- Project: FDE / Fractal Decision Ecosystem, if available
- Assignee: owner
