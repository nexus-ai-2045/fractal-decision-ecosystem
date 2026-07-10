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

## 2026-07-07 Visualization / Systematization Cycle

| impact | todo | design / plan | test plan | implementation | test result | operation guarantee |
|---:|---|---|---|---|---|---|
| P0 | Merge FDE systematization PR | Use guarded merge with current-turn human merge approval, CI success, account match, and clean merge state | `github_pr_readiness_preflight.py`, `pr_merge_guarded.py` dry-run, GitHub Actions check | PR #13 was marked ready and squash-merged into `main` | `public-ready` passed; guarded merge returned `decision: merged` | main contains workflow manifest, drift check, closeout runner, and `.chinju` package separation |
| P0 | Save machine-readable workflow | Treat FDE as control plane, not product runtime | `scripts/fde_workflow_check.py --json` | `fde_workflow.yaml` records intake -> closeout plus external approval stop state | `overall: ok`; `external_actions_performed: false` | Local workflow can be verified without public action |
| P1 | Add system visualization | Add a single map for README / ROADMAP / TODO / feature / gate review | `test_system_overview_visualizes_fde_control_plane` | `SYSTEM_OVERVIEW.md` adds Mermaid diagrams and feature map | Test guards required terms and file pointers | Reviewers can start from one visual overview before reading long docs |
| P1 | Keep visual HTML as first-screen review entry | Mirror system overview and feature map into `visual.html` without implying publication approval | `scripts/visual_html_smoke.py` and pytest | `visual.html` links to system overview, roadmap, TODO, and closeout evidence | HTML smoke checks required text and href targets | Visual review remains local-only and approval-gated |
| P1 | Refresh README / ROADMAP / TODO routing | Make the docs agree on where to read whole-system state | pytest, roadmap gate, MVP gate | README review path and ROADMAP visualization map point to `SYSTEM_OVERVIEW.md`; review-fix cycle added the adapter plane, feature map, and roadmap funnel to `SYSTEM_OVERVIEW.md` | `python -m pytest -q`: 27 passed; `python scripts\fde_architecture_drift_check.py --json`: ok; `python scripts\roadmap_gate_check.py --json`: ok; `run_mvp_gate.ps1`: `FDE MVP GATE CHECK OK`; `git diff --check`: OK | Docs close through pytest, the architecture drift check, the roadmap gate, and the MVP gate rerun after the review-fix cycle |
| P1 | Make subprocess output decoding shell-agnostic | `subprocess.run(..., text=True)` decoded child output with the locale-dependent encoding, so the two Windows shim tests crashed with `UnicodeDecodeError` (byte `0x81`) when pytest ran under a UTF-8 shell (e.g. Git Bash) while `pwsh` emitted CP932 bytes | Reproduce the 2 failures under Git Bash (RED), then rerun the full suite under both Git Bash and native PowerShell (GREEN) | Pinned all decoded subprocess output to `encoding="utf-8", errors="replace"`: 2 sites in `tests/test_public_ready.py`, `_git` / `_run_pytest` in `scripts/fde_operational_closeout.py`, `_run_pytest` in `scripts/mvp_gate_check.py`, `check_git_history` in `scripts/public_ready_check.py` (asserted markers and JSON output are ASCII, so lossy replacement cannot affect any check) | Git Bash: 27 passed; PowerShell: 27 passed; `run_mvp_gate.ps1`: `FDE MVP GATE CHECK OK`; `fde_operational_closeout.py --json --skip-pytest`: ok | Gate and test results no longer depend on the invoking shell's console code page |

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
- `python -m pytest -q`: 26 passed after PR #13 merge
- `python -m compileall -q scripts tests`: OK
- `git diff --check`: OK before this log was added
- `python scripts\fde_operational_closeout.py --json --skip-pytest`: OK after PR #13 merge
- `python -m pytest -q`: 27 passed after PR #14 review-fix cycle (adapter plane, feature map, roadmap funnel added to `SYSTEM_OVERVIEW.md`)
- `python -m pytest -q`: 27 passed under both native PowerShell and Git Bash after pinning subprocess output decoding to `encoding="utf-8", errors="replace"`; the previous Git Bash-only `UnicodeDecodeError` in the two Windows shim tests was a locale-dependent decoding bug in the repo, now fixed

## Next Closeout Rule

Before saying "residue zero" again, rerun the supported closeout bundle:

1. `pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_mvp_gate.ps1`
2. `python scripts\fde_workflow_check.py --json`
3. `python scripts\fde_architecture_drift_check.py --json`
4. `python scripts\fde_operational_closeout.py --json`
5. `python scripts\roadmap_gate_check.py --json`
6. `python -m compileall -q scripts tests`
7. `python -m pytest -q`
8. `git diff --check`
9. Confirm no public/external/visibility action was performed unless explicitly approved.
