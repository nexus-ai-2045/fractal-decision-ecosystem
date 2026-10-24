<!-- repo-preflight:review-record -->

# 公開範囲とレビュー条件

このリポジトリは、Fractal Decision Ecosystem（FDE）の standalone 運用パッケージとして、判断制御の契約・文書・ローカル gate・テストを公開対象とします。特定の個人端末、非公開 workspace、顧客データ、実行時レポートは含めません。

## 公開対象

- FDE の判断ループ、gate、workflow 契約（`fde_workflow.yaml` など）
- feedback packet など machine-readable schema と検証 CLI
- 運用文書（README、SYSTEM_OVERVIEW、ROADMAP、OPERATIONAL_GUARANTEE など）
- ローカル public-ready / MVP gate と回帰テスト
- MIT License とセキュリティ報告方針

## 公開対象外

- ローカル絶対 path、個人アカウント、通知先
- 秘密情報、顧客データ、private draft workspace
- 個別案件の secret 検査結果や人間レビュー記録そのもの
- 公開・push・merge・visibility 変更を自動実行する機能
- patent 出願の実行そのもの（判断資料は別ゲート）

## 判定上の停止線

ローカル gate の `pass` は、担当する自動検査に合格したことだけを示します。secret が存在しないこと、依存関係が安全であること、実際の CI が成功したこと、公開してよいことは保証しません。

公開・release・visibility 変更には、対象リポジトリ固有の追加検査、専門 scanner、実 CI 結果、ライセンス確認、人間による目視レビュー、現在会話での明示承認が必要です。

補足の公開準備メモ: [PUBLIC_READY.md](PUBLIC_READY.md)
