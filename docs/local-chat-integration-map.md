# Local chat integration map

Status: portable composition contract (no new product runtime)

This document integrates **local chat / dialogue / session state** into FDE **without inventing a second orchestrator or copying private chat bodies** into the public package.

## Principle

Local chat is not an FDE product surface. FDE stays a control plane:

| Concern | Reuse (do not reinvent) | Destination |
|---|---|---|
| Session state / resume | `scripts/fde_operational_closeout.py --write-context-receipt` + dated closeout notes | machine receipt / historical note |
| Workstream split (`implementation` / `verification` / `public-boundary`) | roadmap term `chat-orchestrator` as **composition**, not a new binary | plan text + team formation fields |
| Task ranking | `scripts/fde_task_manager.py` + `fde.manager_task.v1` | plan-only JSON |
| Local verification run | `scripts/fde_target_workflow.py` (stop at `review_packet`) | metadata-only receipt |
| Learning return | `scripts/fde_feedback_packet.py --from-receipt` → `fde.feedback.v1` draft | hold/revise only |
| Durable human lesson | operator-local world absorption (outside public package) | abstract lesson + pointer |
| Discord raw thread | operator-local Discord bridge (outside public package) | abstract `learning_handoff` only |

## Curse-of-dimensionality control (FDE)

Do **not** expand chat into N×M dimensions (every tool × every surface × every memory store).

Use three fixed axes only:

1. **Decision Experience** — compress the ask into a packet (`question / owner / mode / evidence / stop`).
2. **Autonomous Execution** — bounded local checks with an explicit external boundary and return path.
3. **Public / external boundary** — approval-gated; never implied by green local gates.

Everything else is an **operator-local adapter** or a typed receipt. Raw chat, raw tool dumps, and personal paths stay out of packets.

## Composition called `chat-orchestrator`

`chat-orchestrator` in `ROADMAP.md` / roadmap gate vocabulary means this sequence, not a new executable:

```text
local chat / handoff ask
  -> Decision Experience packet (operating-card / dialogue-protocol)
  -> fde.manager_task.v1 plan (optional ranking)
  -> fde.target_workflow.v1 run until review_packet
  -> fde.feedback.v1 draft from receipt (hold/revise)
  -> fde_operational_closeout receipt / human review packet
  -> external_approval_required for push/PR/merge/public actions
```

Forbidden expansions:

- auto `act.decision=adopt`
- auto push / PR / merge / visibility change
- absorbing Discord or chat transcripts into the public package
- a second closeout generator (`fde_context_closeout.py` is **not** required; use `fde_operational_closeout.py --write-context-receipt`)

## Operator-local adapters (public package stays path-free)

| capability key | resolution | public package behavior if missing |
|---|---|---|
| `local-chat-closeout` | operator-local-adapter | use repo closeout scripts + dated notes only |
| `world-absorption` | operator-local-adapter | skip; do not invent private world paths |
| `discord-context-bridge` | operator-local-adapter | skip; no raw Discord ingress in public core |
| `handoff-index` | operator-local-adapter | use repo historical closeout docs only |

Physical paths are never published. See `dependency-registry.md` and ADR-0005.

## MPC-style preflight (one horizon)

Before implementing from a chat thread, predict one step ahead:

1. **Goal / boundary** — what must stay local vs approval-gated.
2. **Prior art** — existing schema / script / test that already covers it.
3. **Stop state** — `review_packet` or `external_approval_required`.
4. **Return path** — `fde.feedback.v1` draft or closeout receipt only.
5. **Non-goals** — public release, patent filing, credential / settings change.

If more than three concurrent workstreams appear, re-split with team formation (`team_plan` or `no_team_reason`) instead of growing one chat into a mega-thread.

## Smoke (repo-local)

```powershell
python scripts/fde_feedback_packet.py --from-receipt <receipt.json> --manifest <manifest.json> --json
python scripts/fde_operational_closeout.py --json --skip-pytest
python -m pytest -q tests/test_feedback_packet.py tests/test_target_workflow_runner.py
```

`external_actions_performed` for these checks remains false unless a separate approved action is taken outside this package.
