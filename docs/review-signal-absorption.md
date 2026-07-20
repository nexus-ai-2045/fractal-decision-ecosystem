# PRレビューシグナル吸収ルール

## 目的

CI成功、bot check成功、bot review comment、人間レビューを混ぜない。自動レビューが未実行だった場合は、PRがgreenでも「レビュー済み」と扱わず、FDEの `review_packet -> human_review_required` に戻す。

## 契約

`scripts/pr_review_signal_check.py` は、GitHub PRの `reviews`、`comments`、`statusCheckRollup` を読み、次を分離して返す。

| field | 意味 |
|---|---|
| `checks_success` | CI/check runが成功しているか |
| `cursor_bugbot` | Cursor Bugbotが実行されたか、disabled/未実行か |
| `codex_review_signal` | Codex review commentが見えるか |
| `automated_review_coverage` | 自動レビューを採用可能なシグナルとして扱えるか |
| `human_review_required` | 人間レビュー待ちへ戻す必要があるか |
| `do_not_treat_check_success_as_review_approval` | check成功をレビュー承認に読み替えてはいけないか |

## 運用

PR作成後のcloseoutでは、`gh pr view <PR> --json reviews,comments,statusCheckRollup` を保存し、次を実行する。

```powershell
python -m scripts.pr_review_signal_check --pr-json pr-review.json --json
```

mergeまたはrelease前に「人間レビュー済み」と言う場合だけ、次を使う。

```powershell
python -m scripts.pr_review_signal_check --pr-json pr-review.json --require-human-review --json
```

このcheckが `human_review_required: true` を返す時、PRはCI greenでもレビュー済みではない。Cursor Bugbotがdisabled、review commentが説明だけ、または自動reviewが未実行の場合は、運用上の結論を `human_review_required` とする。

## PR #9 からの吸収

PR #9では、Cursorのcheck run自体は成功したが、レビュー本文は「Bugbot未実行」「人間レビューが必要」だった。この差を見落とすと、check成功をレビュー成功として扱う誤報になる。

再発防止として、レビュー状態を次の3層に分ける。

1. CI/check run: 実行環境とgateが通った証拠。
2. automated review signal: botが実際にレビューしたか、未実行/disabledだったか。
3. human review: merge/release前の人間判断。

CI成功だけで2または3を満たしたとは扱わない。
