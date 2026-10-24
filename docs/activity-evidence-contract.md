# FDE Activity Evidence 受領契約

`fde.activity-evidence.v1` は、Activity Log が保持する原証拠をFDEの判断へ参照させるための、本文を含まない受領契約です。

## 責務境界

- Activity Log / LCS: 人間・AI・tool・systemの原イベント、本文、identity来歴を保持する。
- FDE: `event_id`、`content_hash`、actor分類、時刻、来歴ポインタだけを検証して判断根拠に使う。
- このvalidator: packetをread-onlyで検証する。取得、送信、DB書込み、自動採用は行わない。

schema適合は、原証拠の真実性、本人性、同意、公開可否、FDEでの採用を保証しません。`identity_status=verified` もproducerから届いた分類であり、検証方式やattestationが別途確認されるまで、FDEの事実確度・認可・自動採用を上げてはいけません。`content_hash`はproducerの正規化済み重複判定hashであり、原文完全性hashや匿名化保証ではありません。

本文、prompt、response、URL、個人パス、secretは契約外です。必要な調査は`event_id`と`content_hash`から原証拠側の承認済み経路へ戻します。

現行v1はvisibilityを運びません。受領側はprivateとして扱い、公開面へ投影しません。visibility伝播と原証拠の再検証はproducer/consumer協調変更を伴う後続契約です。

## 検証

```powershell
python scripts/fde_activity_evidence.py --input evidence.json --json
```

成功時も`external_actions_performed`は常に`false`です。受領後の採否はFDEの人間レビュー境界で別に判断します。
