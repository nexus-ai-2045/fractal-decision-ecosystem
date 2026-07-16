# FDE Residual Zero Goal

> Historical goal record: visibility、branch、test件数は記録日時点の証跡です。現在の残務ゼロ判定は `scripts/fde_operational_closeout.py --json --require-delivery-ready` を正本とし、clean worktreeとupstream同期まで確認します。

Status: historical goal completed / current public repository residual semantics retained
Date: 2026-07-05

この file は、FDE repository 全体を「残務ゼロ」と呼ぶための再設計 goal です。
public release、repository visibility 変更、external sending、patent filing、
credential / auth / settings / destructive operation は承認しません。

## Goal

FDE repository の残務ゼロは、次の3層を混ぜずに達成します。

| layer | residual zero の意味 | gate |
|---|---|---|
| implementation | FDE repository package の必須実装、ADR、roadmap、tests が同期し、未実装は explicit future scope または human/external blocker に分離されている | pytest、MVP gate、roadmap gate |
| operation | local smoke / preflight / CI / PR receipt / post-merge receipt / operational guarantee が確認できる | MVP gate、GitHub PR checks、post-merge verification |
| external/public | public release、repo visibility、external send、patent filing は未承認なら残務ではなく approval-gated blocker として扱う | publication containment gate、pre-publication gate |

## Current Measurement

2026-07-05 時点のhistorical実測:

- `python -m pytest -q` -> 19 passed
- `pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_mvp_gate.ps1` -> `FDE MVP GATE CHECK OK`
- `python scripts\pre_publication_gate_check.py --json` -> `overall: ok`
- `python scripts\public_ready_check.py` -> `PUBLIC READY CHECK PASSED`
- PR #10 `FDEにTeam Formationと残務ゼロゴールを追加` -> merged、CI `public-ready` pass
- PR #11 `AI contact安全契約と残務ゼロsmokeを強化` -> merged、CI `public-ready` pass
- PR #12 `公開境界レビューpacketと差分checkを追加` -> merged、CI `public-ready` pass

2026-07-06 historical post-merge 実測:

- local `main` and `origin/main` point to `0658300873d83bc8b7e11f588ed65d6224a1b69d`
- `python -m pytest -q` -> 27 passed
- `pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_mvp_gate.ps1` -> `FDE MVP GATE CHECK OK`
- GitHub Actions `Public Ready` for `0658300873d83bc8b7e11f588ed65d6224a1b69d` -> success
- open PR count -> 0
- repository visibility -> PRIVATE（当時。現在はpublic）

## Blocker Ledger

| blocker | kind | owner | unblock condition |
|---|---|---|---|
| local implementation blockers | FDE implementation | Codex | resolved by PR #10 / #11 / #12 and post-merge gates |
| local operation blockers | FDE operation | Codex | resolved by post-merge receipt、pytest、MVP gate、GitHub Actions |
| public release / repository visibility / patent filing | external approval | human | exact current-conversation approval for the exact target and operation |

## Three-PR Plan

### PR 1: Team Formation + Residual Zero Goal

Status: merged as PR #10.

Scope:

- Team Formation / Orchestration Gate を FDE 中核に入れる。
- Team Creator を FDE 内 role として定義する。
- この residual zero goal を正本化し、goal check を MVP gate に接続する。

Pre-review:

- Team Formation が常時delegate必須に読めないこと。
- delegate に final decision、publication approval、credential / auth / settings / destructive operation を渡していないこと。
- 残務ゼロが public release approval と混ざっていないこと。

Done when:

- PR #10 の CI が pass する。Done.
- local MVP gate が pass する。Done.
- human review 後に merge され、post-merge receipt が残る。Done.

### PR 2: Contact Safety + Residual Operation Smoke

Status: merged as PR #11.

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

- pytest、new smoke checks、MVP gate が pass する。Done.
- external actions remain false。Done.

### PR 3: Public Boundary Package + Operational Closeout

Status: merged as PR #12 plus post-merge receipt commit.

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

- pre-publication gate、public-ready check、pytest、MVP gate が pass する。Done.
- post-merge verification receipt が残る。Done.
- local implementation residue and local operation residue are zero。Done.
- external/public actions remain approval-gated and unperformed。Done.

## Close Condition

この goal は、次をすべて満たした時だけ complete とします。

- PR 1-3 の required local gates が pass している。
- merged PR の post-merge receipt が `OPERATIONAL_GUARANTEE.md` に残っている。
- `MVP_STATUS.md` と `OPERATIONAL_GUARANTEE.md` が implementation / operation / external-public を分けている。
- `pre_publication_gate_check.py --json` が remaining human/external blockers を出し、external actions performed が false である。
- repository visibility is public; any further visibility change remains approval-gated and requires exact repo-specific approval。
