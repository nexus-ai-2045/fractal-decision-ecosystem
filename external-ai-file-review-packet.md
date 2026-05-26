---
title: External AI File Review Packet Template
type: reference
status: active
created: 2026-05-08
updated: 2026-05-08
owner: codex-main
tags: [external-ai, prompt-template, file-backed, review]
related:
  - external-ai-file-loop.md
  - external-ai-route-registry.md
---

# External AI File Review Packet Template

```markdown
---
title: <topic> external AI review packet
type: inbox
status: ready-for-external
created: YYYY-MM-DD
from: codex-main
to: external-ai
tags: [external-ai, review, file-loop]
---

# <topic>

## 背景

<なぜ外部AIに読ませるか。3-5行。>

## 材料

| path | 役割 |
|---|---|
| <path> | <why> |

## レビュー先 contract

- review_target_type: external_ai
- 外部AI / 別AIは反証・発散・別モデル差分・候補抽出のために使う。
- raw answer は採用決定ではない。Codex 側で local fact check / 他AI差分確認をしてから採否する。
- provider 名に固定しない。基本 contract は `researcher_or_reviewer_ai -> technical_judge_or_integrator`。
- Grok -> Codex は一例。Gemini / ChatGPT / Claude / Cloud Code / Grok などにも同じ contract を使える。
- handoff は PDCA で改善する。Plan で採否基準を決め、Do で調査/反証し、Check で technical judge が評価し、Act で正本へ反映し、Improve で次回の依頼テンプレと採否基準を更新する。
- 人間レビュー用の要約ではないため、推測・不明・追加確認を省略しない。

## 問い

1. <最重要の問い>
2. <必要なら追加>

## 出力形式

- 20 行以内
- 採用 / 修正採用 / 保留 / 棄却の判定
- 抜け・重複・構造ミスを優先
- 追加で読むべき file があれば path だけ
- 各指摘に `[事実: 添付file/section]` / `[推測]` / `[不明]` のどれかを付ける
- `[推測]` は、事実に近づけるための追加確認を 1 行で添える
- `[不明]` は、添付不足・runtime未確認・外部状態など、閉じられない理由を書く
- `[推測]` / `[不明]` を `採用` 根拠にしない
- pdca_record を返す: `plan_assumption / do_output / check_result / act_recommendation / improve_next_prompt`
- 添付 file が多すぎる / 足りない / ZIP が読めない場合は、推測で回答せず `needed_files:` に path だけ列挙する
- 外部 OSS / GitHub 実装を勧める場合は、license / reuse permission / source or binary の別を分け、未確認なら `[不明]` と書く

## 禁止

- secret / credential を推測しない
- 未確認を断定しない
- 長文を書き戻さない
- 他AIとの比較が必要な論点を単独レビューで確定しない
```

