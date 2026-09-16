# 人間レビュー署名receipt

FDEの`verified`はGitHubのPR状態ではなく、Gitへ保存したhuman review receiptと署名で判定する。

## 正本

- 公開鍵: `keys/fde-human-review-nexus_ai.pub`
- 指紋: `SHA256:lnzqUQWKfJisG+fpkiwNj0Sx/oJnFDOYo27MPmnn/WU`
- 秘密鍵: リポジトリ・receipt・CIログへ保存しない

## receiptの最低項目

`schema_version`、`decision`、`reviewer`、`reviewed_at`、`reviewed_tree`、`reviewed_files`、`receipt_sha256`を持つ。署名対象は正規化したreceipt本文とし、対象treeとreceipt hashを同じ判断へ結び付ける。

## 検証結果

- 公開鍵または署名がない: `unknown`
- 署名が不正、対象tree不一致、receipt hash不一致: `unknown`
- 署名・公開鍵・対象tree・receipt hashが一致: `verified`

GitHubのPR、レビュー、CIは補助証拠として保存できるが、本人承認の正本ではない。訂正は既存receiptを上書きせず、新しいreceiptから`supersedes`でつなぐ。

## 鍵運用

鍵の所有者は`nexus_ai`運用主体とする。秘密鍵の紛失・漏洩を検知した場合は署名検証を停止し、公開鍵の差し替えを新しいADRと人間承認で行う。鍵の削除や履歴改変は行わない。

## 将来の拡張

独立した信頼ドメインが2つ以上になり、同一receiptを複数主体で検証する必要が生じた場合に限り、Merkle固定またはpermissioned blockchainを検討する。現在の運用はGitと署名receiptで閉じる。
