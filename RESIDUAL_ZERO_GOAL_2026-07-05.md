# FDE Residual Zero Goal

Status: active goal design / private repository scope
Date: 2026-07-05

この file は、FDE repository 全体を「残務ゼロ」と呼ぶための再設計 goal です。
public release、repository visibility 変更、external sending、patent filing、
credential / auth / settings / destructive operation は承認しません。

## Goal

FDE repository の残務ゼロは、次の3層を混ぜずに達成します。

| layer | residual zero の意味 | gate |
|---|---|---|
| implementation | FDE private package の必須実装、ADR、roadmap、tests が同期し、未実装は explicit future scope または human/external blocker に分離されている | pytest、MVP gate、roadmap gate |
| operation | local smoke / preflight / CI / PR receipt / post-merge receipt / operational guarantee が確認できる | MVP gate、GitHub PR checks、post-merge verification |
| external/public | public release、repo visibility、external send、patent filing は未承認なら残務ではなく approval-gated blocker として扱う | publication containment gate、pre-publication gate |

## Current Measurement

2026-07-05 時点の実測:

- `python -m pytest -q` -> 19 passed
- `pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_mvp_gate.ps1` -> `FDE MVP GATE CHECK OK`
- `python scripts\pre_publication_gate_check.py --json` -> `overall: ok`
- `python scripts\public_ready_check.py` -> `PUBLIC READY CHECK PASSED`
- PR #10 `FDEにTeam Formation Orchestration Gateを追加` -> open、CI `public-ready` pass

## Blocker Ledger

| blocker | kind | owner | unblock condition |
|---|---|---|---|
| PR #10 is not merged | repo integration | human + Codex | human review、merge approval、post-merge verification |
| AI contact schema hardening is not implemented | FDE implementation | Codex | no-transport contact check、schema examples、tests、MVP gate |
| residual-zero / visual smoke is not implemented | FDE operation | Codex | `verify_residual_zero_contract.py`、`visual_html_smoke.py`、tests、MVP gate |
| public kernel diff / human publication packet is not implemented | FDE public-boundary package | Codex | `public_kernel_diff_manifest.py`、`human_review_packet_check.py`、pre-publication gate |
| public release / repository visibility / patent filing | external approval | human | exact current-conversation approval for the exact target and operation |
| ignored `.chinju/sessions/` can be included by manual zip/upload | package hygiene | Codex + human | keep ignored path outside repo package、document manual-package warning、public-ready check remains green |

## Three-PR Plan

### PR 1: Team Formation + Residual Zero Goal

Status: in progress as PR #10.

Scope:

- Team Formation / Orchestration Gate を FDE 中核に入れる。
- Team Creator を FDE 内 role として定義する。
- この residual zero goal を正本化し、goal check を MVP gate に接続する。

Pre-review:

- Team Formation が常時delegate必須に読めないこと。
- delegate に final decision、publication approval、credential / auth / settings / destructive operation を渡していないこと。
- 残務ゼロが public release approval と混ざっていないこと。

Done when:

- PR #10 の CI が pass する。
- local MVP gate が pass する。
- human review 後に merge され、post-merge receipt が残る。

### PR 2: Contact Safety + Residual Operation Smoke

Scope:

- `ai-contact-safety-contract.md` に contact packet schema candidates を追加する。
- `no_transport_contact_check.py` で Wi-Fi / Bluetooth / P2P / cloud relay / external AI send 実装混入を止める。
- `verify_residual_zero_contract.py` で implementation / operation / external-public の残務語彙が混ざらないことを見る。
- `visual_html_smoke.py` で review UX、MVP gate、public/private stop line の導線を見る。

Pre-review:

- contact schema が transport adapter 実装に見えないこと。
- residual-zero check が過保証になっていないこと。
- visual smoke が launch material / public approval に読めないこと。

Done when:

- pytest、new smoke checks、MVP gate が pass する。
- external actions remain false。

### PR 3: Public Boundary Package + Operational Closeout

Scope:

- `public_kernel_diff_manifest.py --check` で private root と `public-kernel/` の差分を確認する。
- `human_review_packet_check.py` で public release / repo visibility / patent filing の review packet 必須項目を確認する。
- `OPERATIONAL_GUARANTEE.md` を過保証しない形に更新し、PR #10 以降の post-merge receipt を追加する。
- `TODO_FDE_PUBLIC_KERNEL_RIGHTS.md` を local package residual と external approval blocker に分ける。

Pre-review:

- public kernel が private operating package と同一視されていないこと。
- repository visibility 変更、public release、patent filing の承認に読めないこと。
- branch protection / GitHub native secret scanning など未使用の外部保証を、local guarantee と混ぜていないこと。

Done when:

- pre-publication gate、public-ready check、pytest、MVP gate が pass する。
- post-merge verification receipt が残る。
- local implementation residue and local operation residue are zero。
- external/public actions remain approval-gated and unperformed。

## Close Condition

この goal は、次をすべて満たした時だけ complete とします。

- PR 1-3 の required local gates が pass している。
- merged PR の post-merge receipt が `OPERATIONAL_GUARANTEE.md` に残っている。
- `MVP_STATUS.md` と `OPERATIONAL_GUARANTEE.md` が implementation / operation / external-public を分けている。
- `pre_publication_gate_check.py --json` が remaining human/external blockers を出し、external actions performed が false である。
- repository visibility remains private unless exact repo-specific approval is given。
