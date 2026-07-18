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

| PR | scope | state | merge commit | merged at |
|---|---|---|---|---|
| [#7](https://github.com/nexus-ai-2045/fractal-decision-ecosystem/pull/7) | ADR採番ワークフロー | MERGED | `af1af13e444c2dad0f9878e77d243ae98c469fb9` | 2026-06-22T20:18:37+09:00 |
| [#8](https://github.com/nexus-ai-2045/fractal-decision-ecosystem/pull/8) | AI contact安全契約とレビュー導線 | MERGED | `a627c1683a2cd7b08cc29a31bacd4bae73d2e034` | 2026-07-02T06:07:22+09:00 |
| [#10](https://github.com/nexus-ai-2045/fractal-decision-ecosystem/pull/10) | Team Formation と残務ゼロゴール | MERGED | `57b0146c46d47be6eb6c8793df3f825fad875a11` | 2026-07-06T00:12:21+09:00 |
| [#11](https://github.com/nexus-ai-2045/fractal-decision-ecosystem/pull/11) | AI contact安全契約と残務ゼロsmoke | MERGED | `075939b32de6ab5de6086adf810c919f57c2120b` | 2026-07-06T00:14:15+09:00 |
| [#12](https://github.com/nexus-ai-2045/fractal-decision-ecosystem/pull/12) | 公開境界レビューpacketと差分check | MERGED | `c8404c9c0a44bbac8047ce676f260970e15dbdc2` | 2026-07-06T00:15:47+09:00 |

Post-merge local sync evidence:

- `main...origin/main` に同期済み。
- #8 の squash merge 後、local duplicate commit は rebase skip で remote main に合わせた。
- #10 / #11 / #12 は stacked PR として review 後に squash merge し、#11 / #12 は `main` へ retarget して GitHub Actions `public-ready` pass 後に merge した。
- #10 / #11 / #12 の merge は当時privateだったrepository mainへの反映であり、追加のpublic action approvalではない。

## 必須検証

この package は、以下の check がすべて通った時だけ運用可能とみなします。

- `pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_mvp_gate.ps1`
- `python3 scripts/roadmap_gate_check.py`
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
post-merge の branch / remote-tracking / worktree 掃除の実行正本は `scripts/post_merge_cleanup.py` です。skill や記憶だけでは発火保証しません。merge 後は `python3 scripts/post_merge_cleanup.py --apply --json`、または closeout の `--run-post-merge-cleanup` / `--require-post-merge-cleanup` を使います。remote head の自動削除は GitHub の `delete_branch_on_merge`（Automatically delete head branches）を正とします。
macOS / Linuxのsupported entrypointは`python3`、Windowsのtop-level supported entrypointは`scripts/run_mvp_gate.ps1`です。存在しない`python`commandを前提にしません。
`scripts/roadmap_gate_check.py` は、`ROADMAP.md` の Now / Next / Future、
lane、goal、evidence、gate、owner、done_when、人間目視レビュー後 merge 境界を検証します。
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
