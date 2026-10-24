# 公開準備

状態: repository は公開済み（public）。外部送信・announcement・patent filing・さらなる visibility 変更・public release の宣言は、引き続き現在ターンの人間承認制で止める。

## 完了済み必須チェック

- [x] README が存在し、Fractal Decision Ecosystem を明記している
- [x] LICENSE が存在する
- [x] SECURITY.md が存在する
- [x] local Markdown link を確認済み
- [x] secret らしい token pattern を確認済み
- [x] 個人の absolute path を確認済み
- [x] draft workspace folder を除外済み
- [x] GitHub repository target を確認済み
- [x] repository への push と public 化承認の反映が完了
- [x] GitHub Actions の MVP gate workflow 通過
- [x] 運用保証を文書化済み
- [x] 外部 review 失敗では `failure_kind` と `postmortem_action` が必須

## 公開境界

この package は Fractal Decision Ecosystem（FDE）の standalone public candidate として、`nexus-ai-2045/fractal-decision-ecosystem` に公開済みです。
source workspace、draft 作業 folder、machine-local path、private operational state は公開境界の外です。

この file は、行われた repository public 化の事実を記録するものであり、追加の action を新たに承認するものではありません。
外部送信、announcement、patent filing、さらなる repository visibility 変更、public release の宣言には、現在の会話で対象 repository を明示した承認が必要です。

## 公開リリースゲート

repository の主検証は `pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_mvp_gate.ps1` です。
`nexus-ai-2045/fractal-decision-ecosystem` は、人間 review と repository visibility approval を経て public 化されています。
この gate は public 化後も維持すべき最低ラインとして機能し続けます。外部送信、announcement、patent filing、さらなる visibility 変更、public release の宣言は、この gate 通過だけでは承認されず、現在の会話での明示 GO が必要です。

## 特許 / 公開ブロッカー

- patent / filing 方針は意図的に broad に保つ。local operation の必須残務にはしない。
- inventor / owner / assignee decision は記録済み。
- inventor は user-confirmed sole inventor として決定済み。
- owner は user、assignee は none / unassigned として決定済み。
- filing 実行は optional external action。実行する場合は現在の会話での明示承認が必要。
- filing した場合だけ receipt / application number / submitted PDF / file hash を保存する。
- repository 本体は既に公開済みだが、patent packet や rights 関連の sanitized 差分確認には引き続き `public-kernel/` を参照する。
- patent filing は patent / public kernel gate で保留のまま。
- `Patent Pending` 表記は patent application filed 後だけ使う。
