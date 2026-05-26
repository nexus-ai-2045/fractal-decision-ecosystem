# 公開準備

状態: private repository 候補。private 運用では準備完了。

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
- [x] GitHub Actions の public-readiness workflow 通過
- [x] 運用保証を文書化済み
- [x] 外部 review 失敗では `failure_kind` と `postmortem_action` が必須

## 公開境界

この package は Fractal Decision Ecosystem（FDE）の standalone public candidate として整備しています。
source workspace、draft 作業 folder、machine-local path、private operational state は公開境界の外です。

この file は GitHub publication や repository visibility 変更を承認しません。
それらの操作には、現在の会話で対象 repository を明示した承認が必要です。

## 公開リリースゲート

人間 review と repository visibility approval は実装残務ではなく、必須の publication gate です。
`nexus-ai-2045/fractal-decision-ecosystem` についてこの gate が明示完了するまで、repository は private のまま維持します。
