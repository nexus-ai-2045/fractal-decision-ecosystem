# 公開準備

状態: private repository 候補。private 運用では準備完了。public 化は patent / public kernel gate で保留。

## 完了済み必須チェック

- [x] README が存在し、Fractal Decision Ecosystem を明記している
- [x] LICENSE が存在する
- [x] SECURITY.md が存在する
- [x] local Markdown link を確認済み
- [x] secret らしい token pattern を確認済み
- [x] 個人の absolute path を確認済み
- [x] draft workspace folder を除外済み
- [x] GitHub repository target を確認済み
- [x] private repository への push 完了
- [x] GitHub Actions の private MVP gate workflow 通過
- [x] 運用保証を文書化済み
- [x] 外部 review 失敗では `failure_kind` と `postmortem_action` が必須

## 公開境界

この package は Fractal Decision Ecosystem（FDE）の standalone public candidate として整備しています。
source workspace、draft 作業 folder、machine-local path、private operational state は公開境界の外です。

この file は GitHub publication や repository visibility 変更を承認しません。
それらの操作には、現在の会話で対象 repository を明示した承認が必要です。

## 公開リリースゲート

private repository の主検証は `python scripts\mvp_gate_check.py` です。
人間 review と repository visibility approval は実装残務ではなく、必須の publication gate です。
`nexus-ai-2045/fractal-decision-ecosystem` についてこの gate が明示完了するまで、repository は private のまま維持します。

## Patent / Publication Blockers

- patent / filing 方針は意図的に broad に保つ。local operation の必須残務にはしない。
- inventor / owner / assignee decision は記録済み。
- inventor は user-confirmed sole inventor として決定済み。
- owner は user、assignee は none / unassigned として決定済み。
- filing 実行は optional external action。実行する場合は現在の会話での明示承認が必要。
- filing した場合だけ receipt / application number / submitted PDF / file hash を保存する。
- public 化する場合は本体 repo ではなく `public-kernel/` 相当の sanitized kernel のみを対象にする。
- `Patent Pending` 表記は patent application filed 後だけ使う。
