# 運用保証

状態: public repository 運用として保証済み

## 対象範囲

この保証は、Fractal Decision Ecosystem（FDE）の現在の public repository package を対象にします。

- repository content
- local MVP gate script
- local test
- GitHub Actions validation
- repository metadata と operating setting
- private handle と personal path の確認
- roadmap first iteration gate の local readiness

この保証は repository の public 化の事実を記録するものであり、追加の public action を新たに承認するものではありません。

## 残務

実装残務: なし

運用残務: なし

未実装ロードマップ: あり。ただし future scope として `ROADMAP.md` に分離済みであり、現在の repository package の実装残務ではない。

public release 残務: 人間承認が必要

patent decision 残務: なし

patent filing 実行残務: なし（optional / approval-gated）

現在の visibility: public

## Post-Merge Receipts

この節は、merge 後の local/remote 同期と運用証跡を残すための receipt です。これは public release、repository visibility 変更、external sending、patent filing の承認ではありません。

Current public GitHub PR receipts（この repository の現行 PR 番号）:

| PR | scope | state | merge commit | merged at |
|---|---|---|---|---|
| [#1](https://github.com/nexus-ai-2045/fractal-decision-ecosystem/pull/1) | PR本文のPII/ローカルパス検査 | MERGED | `81804ccf7e493f64d9d383012604db0c115fbe00` | 2026-07-13T13:00:49+09:00 |
| [#2](https://github.com/nexus-ai-2045/fractal-decision-ecosystem/pull/2) | 信頼済み対象の検証runner | MERGED | `9cc7064ca14ea28a1cbbaf4962021214188db1c3` | 2026-07-16T06:35:54+09:00 |
| [#3](https://github.com/nexus-ai-2045/fractal-decision-ecosystem/pull/3) | FDE運用学習ループと自動バージョニング | MERGED | `60d108fc5e74f275cbefdfd29e344ff117338739` | 2026-07-16T09:10:49+09:00 |
| [#6](https://github.com/nexus-ai-2045/fractal-decision-ecosystem/pull/6) | 公開packageのpointer環境非依存化 | MERGED | `e75a9398583d381db3dc990eaa81d0333ddc9bb0` | 2026-07-18T17:55:32+00:00 |

Historical in-repo squash commits（commit message の `(#N)` は当時の採番。現行 GitHub の同番号 PR とは別物）:

| historical label | scope | state | commit | committed at |
|---|---|---|---|---|
| historical (#7) | ADR採番ワークフロー | IN_HISTORY | `94affdd3a02a38053d67a3f469a9244d401fa448` | 2026-06-22T20:18:37+09:00 |
| historical (#8) | AI contact安全契約とレビュー導線 | IN_HISTORY | `151d88cff34e2703d220aabb9d489ef0e04fa7a6` | 2026-07-02T06:07:22+09:00 |
| historical (#10) | Team Formation と残務ゼロゴール | IN_HISTORY | `3be1e4fffa9545756cdaa85c815d73f6cb380b2f` | 2026-07-06T00:12:21+09:00 |
| historical (#11) | AI contact安全契約と残務ゼロsmoke | IN_HISTORY | `c132183250b50eafa3c2d81ca7ba20e3f8acac7b` | 2026-07-06T00:14:15+09:00 |
| historical (#12) | 公開境界レビューpacketと差分check | IN_HISTORY | `ad643d1de0693924a64abf8e314a000420ce9961` | 2026-07-06T00:15:46+09:00 |

注意: 現行 GitHub の [#7](https://github.com/nexus-ai-2045/fractal-decision-ecosystem/pull/7) は open の post-merge cleanup PR であり、historical (#7) ADR採番 commit とは別である。receipt では GitHub PR URL と historical label を混同しない。

Post-merge local sync evidence:

- `main...origin/main` に同期済み。
- historical (#8) の squash 後、local duplicate commit は rebase skip で remote main に合わせた。
- historical (#10) / (#11) / (#12) は stacked PR として review 後に squash merge し、GitHub Actions `public-ready` pass 後に main へ反映した。
- これらの historical merge は当時privateだったrepository mainへの反映であり、追加のpublic action approvalではない。

## 必須検証

この package は、以下の check がすべて通った時だけ運用可能とみなします。

- `pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_mvp_gate.ps1`
- `python3 scripts/roadmap_gate_check.py`
- `python3 scripts/orchestration_gate_check.py`
- `python3 scripts/residual_zero_goal_check.py`
- `python3 scripts/no_transport_contact_check.py`
- `python3 scripts/verify_residual_zero_contract.py`
- `python3 scripts/visual_html_smoke.py`
- `python3 scripts/public_kernel_diff_manifest.py --check`
- `python3 scripts/human_review_packet_check.py --json`
- `python3 scripts/fde_workflow_check.py`
- `python3 -m compileall -q scripts tests`
- GitHub Actions workflow `Public Ready`
- Git history の author / committer が `Nexus AI <noreply@nexus-ai.local>` である
- repository visibility は既に public 化の明示承認を経て変更済みであり、それ以上の visibility 変更には改めて明示承認が必要である
- `Patent Pending` / `特許出願中` は application filed 後だけ使う
- 外部 review 失敗には `failure_kind` と `postmortem_action` がある

## 強制チェック

`scripts/run_mvp_gate.ps1` は、Windows local の supported entrypoint として Python launcher の差を吸収します。
`py -3` / `python` の probe が Python 3.11+ として確認できない場合、または Windows pyenv shim failure が検出された場合は、MVP gate 本体を通過扱いにせず非ゼロ終了します。
MVP gate 本体の出力 marker が確認できない場合も、wrapper 成功ではなく gate 未実行として失敗扱いにします。
`scripts/mvp_gate_check.py` は、public readiness check、pre-publication gate、
`MVP_STATUS.md`、pytest を集約する private MVP gate です。
`scripts/fde_workflow_check.py` は、goal / capability inventory / roadmap / preflight / implementation / verification / operational guarantee / feedback / system update の順序、`lint / unit / integration / smoke / e2e / regression` の検証層、学習の更新先と adoption 条件を read-only で検証します。
`scripts/fde_operational_closeout.py --json --require-delivery-ready` は、gate healthに加えてworktree、upstream、ahead/behind、delivery residue、保存すべきcontextを検査し、未commit・未pushの状態を残務ゼロと誤判定しません。
`--require-remote-ci`はcurrent HEADのGitHub Actions `Public Ready`成功とHEAD一致を必須化します。`--record-human-review <reviewer>`はstaged treeへの明示レビューをreceipt化し、commit treeとの一致を検証します。`--write-context-receipt`はrunごとのgoal、boundary、planned transitionとcompleted/blocked実績、検証layerの適用/waiver、feedback、full HEAD、gate digestをignored `.fde-runtime/closeout-receipts/`へatomicかつ追記型で保存します。
macOS / Linuxのsupported entrypointは`python3`、Windowsのtop-level supported entrypointは`scripts/run_mvp_gate.ps1`です。存在しない`python`commandを前提にしません。
`scripts/roadmap_gate_check.py` は、`ROADMAP.md` の Now / Next / Future、
lane、goal、evidence、gate、owner、done_when、人間目視レビュー後 merge 境界を検証します。
`scripts/orchestration_gate_check.py` は、`orchestration_required` / Team Formation /
`spark_candidate` / `GPT-5.3-Codex-Spark` の docs contract を検証し、
任意の `--packet-file` で Spark 権限境界まで fail-closed します。
通常の `--json` closeout は residual-zero 保証ではなく、delivery / human review / remote CI を
別 flag（`--require-delivery-ready` / `--require-remote-ci`）で要求します。
`scripts/residual_zero_goal_check.py` は、implementation / operation / external-public を分けた
残務ゼロ goal と 3PR close condition を検証します。
`scripts/no_transport_contact_check.py` は、AI contact schema が transport 実装承認へ漏れていないことを検証します。
`scripts/verify_residual_zero_contract.py` は、残務ゼロの local operation claim と external approval blocker が混ざっていないことを検証します。
`scripts/visual_html_smoke.py` は、review UX の local link と public/private stop line を検証します。
`scripts/public_kernel_diff_manifest.py` と `scripts/human_review_packet_check.py` は、公開前review packageを検証しますが、public release や visibility 変更を承認しません。
内側の `scripts/public_ready_check.py` は、必須 file、local link、private handle pattern、
personal absolute path、draft status、Git history author metadata、この保証 file、
外部 review 失敗 field、GitHub Actions workflow contract を検証します。

現在の plan では、この repository に GitHub branch protection と GitHub native secret scanning はありません。
その代わりに、local readiness check と CI workflow で補完します。
