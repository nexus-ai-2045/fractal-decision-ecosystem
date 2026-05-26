---
title: External AI File Loop
type: brain
status: active
created: 2026-05-08
updated: 2026-05-08
owner: codex-main
tags: [external-ai, browser-ai, file-backed, context-budget, routing]
related:
  - dependency-registry:current-orchestration-premise
  - dependency-registry:source-routing-budget
  - dependency-registry:lane-communication
  - external-ai-route-registry.md
  - external-ai-file-review-packet.md
  - dependency-registry:visual-status-map-playbook
---

# External AI File Loop

## 目的

Codex-main の context を汚さず、browser AI / external AI の長文読解・反証・比較・HTML 化能力を使う。

## invariant

外部 AI に深い読解や比較を投げる時は、chat 本文ではなく file を渡す。戻りも file として保存し、Codex-main は path と短い採否だけ読む。

```text
local packet file
  -> browser AI / external AI file upload
  -> external result file download or copy
  -> local result path
  -> Codex-main reads <= 40 lines
```

FDE folder のように複数 file が正本である対象は、ZIP を既定にしない。browser の attach / file chooser で folder 内 file を複数選択し、provider が file count / size で拒否したら、同じ `immutable_context_key` で続きの file を追加送信する。外部AIには、足りない file があれば path を返させる。

## routing rule

| task | 既定 route | 戻し方 |
|---|---|---|
| 長文読解 / 戦略レビュー / 反証 | browser AI (ChatGPT / Claude.ai / Gemini / Grok) | result file + 20 line summary |
| 最新情報 / 出典付き調査 | search AI / web AI | citations + result file |
| 大量分類 / batch 要約 / evaluator | API 系 AI | JSONL / CSV / Markdown result file |
| local grep / repo 棚卸し / diff 表 | Spark / Cloud Code | `dependency-registry:tmp-scratch` or `dependency-registry:inbox` result path |
| 最終採否 / Type1 境界 | Codex-main + CEO | short decision packet |

## contract

```text
external_ai_file_loop:
- input_packet_path:
- target_route:
- upload_method:
- payload_container_type:
- sent_files:
- remaining_files:
- needed_files:
- question:
- expected_artifact:
- output_save_path:
- main_read_limit: 40 lines
- type1_risk: none / yes
- integration_action:
```

## Codex-main wait budget

Codex-main は待機面ではない。外部 AI / Spark / Cloud Code に投げたら、その turn で長時間待たず、path と回収方法だけ残す。

| 処理 | Codex-main の上限 | 代替 |
|---|---:|---|
| route 判定 | 30 秒 | `dependency-registry:ai-case-route` |
| prompt / packet 作成 | 3 分 | Spark / Cloud Code へ file-backed |
| browser AI 待ち | 0 秒 | browser surface 側で継続、回収は result file |
| 長文結果読解 | 40 行 | worker が要約 file を作る |
| HTML 実装 | しない | browser AI 生成 + worker 保存 + smoke |

## browser implementation route

HTML / dashboard / visual map は、browser AI にコード生成まで投げてよい。

```text
Codex-main:
  design constraints + input packet path を作る

browser AI:
  HTML / CSS / Mermaid 構成案 or code を生成する

worker:
  生成 code を local file に保存
  link / render / smoke を確認
  Codex-main へ path + screenshot/smoke だけ返す
```

候補 route:

- Grok: 高速な HTML / UI 草案 / critique。
- ChatGPT: 構成整理 / HTML 実装 / polish。
- Claude.ai: 長文設計レビュー / 抜け漏れ検出。
- Gemini: 比較 / Google 系文脈 / 長文整理。

## output rule

- 外部 AI へ渡す packet は、背景・材料・問い・出力形式を 1 file にまとめる。
- pointer / registry / SSOT が外部AIから読めない時は、manifest または alias file に展開して添付する。元 pointer と展開 file は packet に両方書く。
- 生ログ全部を渡さず、話題ごとに取り合わせる。
- 外部 AI の返答は `dependency-registry:reports` または `dependency-registry:inbox` に保存する。
- Codex-main への報告は `path + 3 行要約` まで。
- HTML が返る場合、worker が保存し、Codex-main は必要なら screenshot / 見出しだけ確認する。

## smoke rule

新しい route は、最初に同じ小 packet を投げて測る。

```text
route_smoke:
- route:
- file_upload: yes/no
- file_download: yes/no
- elapsed:
- cost_or_quota:
- token_eff: 1-5
- time_eff: 1-5
- impl_eff: 1-5
- parallel_eff: 1-5
- freshness: 1-5
- output_quality: 1-5
- recovery_path:
- next_best_use:
```

## smoke-first operation

外部 AI / browser AI / API route は、設計議論を長く続けず smoke を先に切る。

原則:

- 新 route は本番投入前に 1 packet smoke。
- 新しい用途 (HTML / review / realtime / batch) も 1 packet smoke。
- smoke packet は小さく、同じ input を複数 route に投げる。
- 採点は `external-ai-route-registry.md` に残す。
- Codex-main は smoke 結果の path と採点だけ見る。

最小 smoke:

```text
input: 20-80 行の markdown packet
ask: 1 問だけ
expected: 20 行以内 or 1 artifact
return: local output path
main read: <= 20 lines
```

## optimization axes

外部 AI route は「賢そう」ではなく、4 つの効率で選ぶ。

| 軸 | 目的 |
|---|---|
| token_eff | Codex-main の context を消費しない |
| time_eff | 待ち時間を main が抱えず、壁時計時間を短くする |
| impl_eff | HTML / code / JSON / diff など実装可能な成果に直結する |
| parallel_eff | 同じ packet を複数 route に横投げして比較できる |
| freshness | web / X / 現在情報をどれだけ新しく取れるか |

Codex-main が直接実装するのは、4 軸のどれにも外部化メリットがない時だけ。

## current first use

5/8 の最初の適用対象は master map 統合。

- input packet: `dependency-registry:inbox`
- expected output: `dependency-registry:reports`

