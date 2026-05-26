---
title: User Judgment Confidence Layer
type: brain
status: active
created: 2026-05-13
owner: codex-top
scope: fde-user-judgment-confidence
tags: [fde, judgment, confidence, user-signal, adoption-gate]
---

# User Judgment Confidence Layer

obsidian_check: not_checked
scope_route: top / fde-user-judgment-confidence
closure_rule: active

## Premise

- [ユーザー指摘] ユーザーが判断軸について「これはおかしい」「これはこうして」と明示した内容は、判断軸として採用度・信用度を高く扱ってよい。
- [判断] 外部AIレビュー / 一般論 / runtime推測より、ユーザー明示判断は高優先の `human_judgment_signal` として採否gateに入れる。

## Proposed Field

```yaml
human_judgment_signal:
  label: "[ユーザー指摘]"
  source: user / top-dialogue / lane-reply
  confidence: high / medium / low
  statement:
  applies_to:
  conflict_policy: user_signal_over_external_review_unless_local_fact_contradicts
  verification_needed: yes / no
```

## Rule

- [判断] `confidence: high` は、ユーザーが「おかしい」「こうして」「前に言った」「それは違う」など、運用判断や目的に関する明示補正をした時に付ける。
- [判断] local fact と矛盾しない限り、外部AIレビューの `optional` や `推測` より優先する。
- [判断] ただしファイル内容・実行結果・外部サービス状態など、観測で真偽が決まるものは local fact check を優先する。
- [判断] FDE採否時は `human_judgment_signal` / `[ユーザー指摘]` を `fact_check` / `[事実: source]` と分けて表示し、混ぜない。

