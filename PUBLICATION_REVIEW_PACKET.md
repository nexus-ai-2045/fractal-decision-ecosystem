# FDE 公開レビューpacket

状態: review packet のみ / public action 承認なし
日付: 2026-07-05（visibility 変更 実施: 2026-07）

この packet は、public release、さらなる repository visibility 変更、external send、
patent filing を検討する時の人間レビュー用 checklist です。
この file 自体は、それらの action を新たに承認しません。

## 対象

- Repository: `nexus-ai-2045/fractal-decision-ecosystem`
- 現在の visibility: public
- visibility 変更は実施済み（2026-07）。以後の変更は再承認制。
- 現時点で承認された操作: なし
- この packet による external action 実行: false

## Repository Visibility をさらに変更する場合

GitHub repository の visibility を変更すると、少なくとも次が web 上で visible になります（public 化時点で既に反映済み）。

- commit history
- tracked files
- pull request metadata
- issue / discussion / release surfaces if enabled later
- license and rights posture
- public-kernel candidate

repository は次の exact operation により 2026-07 に public 化されました。さらなる visibility change は、現在の会話で対象 repository を明示した承認が改めて必要です。

```text
gh repo edit nexus-ai-2045/fractal-decision-ecosystem --visibility public
```

## Public Action 前に必須の人間レビュー

- target repository を `owner/name` form で確認する
- exact operation / command を確認する
- web上で visible になる内容を要約する
- README をレビューする
- LICENSE をレビューする
- SECURITY.md をレビューする
- PUBLIC_READY.md をレビューする
- personal path scan を確認する
- secret scan を確認する
- public-kernel diff manifest を確認する
- patent / rights wording をレビューする
- `Patent Pending` が実際の filing 前に使われていないことを確認する
- private source pointers と machine-local procedures が public candidate に含まれないことを確認する

## ローカル証跡bundle

- `PUBLIC_READY.md`
- `SECURITY.md`
- `LICENSE`
- `RIGHTS_NOTICE.md`
- `PUBLIC_KERNEL_PLAN.md`
- `TODO_FDE_PUBLIC_KERNEL_RIGHTS.md`
- `public-kernel/`
- `scripts/public_ready_check.py`
- `scripts/pre_publication_gate_check.py`
- `scripts/public_kernel_diff_manifest.py`
- `scripts/human_review_packet_check.py`

## 停止線

- この packet から repository public 化を実行しない。
- この packet から patent filing を submit しない。
- この packet から external message を送信しない。
- local gate success を publication approval として扱わない。
- public-kernel candidate を full private operating package として扱わない。
