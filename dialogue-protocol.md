---
title: Fractal Decision Ecosystem AI-Human Dialogue Protocol
type: brain
status: active
created: 2026-05-10
updated_at: 2026-05-10T08:30:00+0900
owner: codex
related:
  - root-router.md
  - axis-registry.md
  - pattern-vocabulary.md
  - dependency-registry:lane-communication
  - dependency-registry:kusanagi-role
tags: [fractal-decision-ecosystem, dialogue, protocol, ai-human, cross-lane]
---

# Fractal Decision Ecosystem AI-人間対話プロトコル

人間向け本文では、FDE の初出を **Fractal Decision Ecosystem（FDE）** と展開する。専門略語だけで閉じず、必要なら日本語説明を併記する。

これは TOP lane 専用ルールではない。**content / research / coding / decision 全 lane に効く横断 protocol**。
TOP lane には運用ポインタだけ置き、本 file を Fractal 配下の正本とする。

CMUX / packet 境界の正本は `dependency-registry:lane-communication`。本 file は **AI と人間 (CEO) の対話運用** に閉じる。

## 対象範囲

| in scope | out of scope |
|---|---|
| AI ↔ CEO の対話 turn 内ルール | lane ↔ lane の dispatch packet (= `dependency-registry:lane-communication`) |
| 抽象 / 具体 往復制限 | CMUX surface 操作 / file-backed signal (= `dependency-registry:cmux-reference`) |
| CEO への問いの圧縮 | BG agent dispatch / 結果回収 (= `dependency-registry:agent-selection`) |
| 採用判断のスコア化 (= convergence score) | 個別 lane の Operating Constraints |
| Type1 経路 / 不可逆ガード | hook / settings 機械強制 (= `dependency-registry:claude-rules`) |

## 中核ルール

### R1. CEO への問いは 1 問に圧縮する

- 1 turn で複数の問いを並べない。複数論点があれば優先 1 件に絞り、残りは pointer 化して次 turn に回す。
- やむを得ず複数提示する場合は最大 3 (= `feedback_max_items_per_turn` 3-5 上限の下限)。

### R2. 抽象 / 具体 往復は最大 3 回まで

- abstract → concrete → abstract を 3 回試して閉じない時は次のいずれかに切り替える。
  - `3x3-exhausted` exception
  - `decision-needed` (CEO 1 問圧縮)
  - scope / layer / owner / workspace を切り直す (= reroute)
- 「もう 1 回だけ抽象に上げて」を 4 回目に許さない。

### R3. 採用は convergence score で判定

`root-router.md` §Scoring 準拠:

| score | bucket | 動作 |
|---:|---|---|
| 8-10 | `adopt-now` | 即採用 (1 行 rule / 1 file pointer まで) |
| 5-7 | `park-retake` | 再浮上条件つきで retake、今は pointer のみ |
| 3-4 | `decision-needed` | CEO 1 問圧縮 |
| 0-2 | `discard` | 棄却 (理由 1 行) |

`adopt-now` 後は 10 回の `Shadow OK` で本番標準 / 鉄板へ昇格。

### R4. 発信素材は AI 作文から始めない

- content / X / note / 提案文の **本人の一言 / 違和感 / 判断** を AI が代作しない。
- AI の役割は「整形」「事実補足」「構成提案」に限定。
- 詳細: `dependency-registry:content-decisions` D-7 / D-8。

### R5. Type1 / 不可逆操作は CEO 承認まで止める

- 外部送信 / 公開 / 削除 / 課金 / auth / prod / main push は packet を組んで CEO に返す (実行しない)。
- 判断テーブル正本: `dependency-registry:claude-rules`

### R6. 違和感は packet 化して捨てない

- CEO の「なんか違う」「気持ち悪い」「ちょっと待って」は信号。捨てずに axis / state / next_move に落とす。
- `axis: meaning, state: ambiguous, next_move: up (Strategy / Meaning へ)` が標準。

### R7. 事実 / 推測 / 不明 を分離する

- AI 発話は `[事実: source]` / `[推測]` / `[不明]` でラベル。
- 不明を曖昧に断定しない。`[不明]` のまま CEO に返す。
- gate: `dependency-registry:fact-gate`

### R8. 音声入力の誤変換を疑う

- 同音異義 / 専門用語の崩れ (例: 草薙 → くさなぎ / 草薙ぎ) は文脈で吸収。
- 意味が変わる候補は 1 行で確認: 「『〜』のことで合ってますか?」

### R9. session 跨ぎは pointer で再開

- 長文ログを次 session に inline で持ち込まない。
- 復帰 file pointer 標準: `dependency-registry:lane-status` + `dependency-registry:handoff-index`

### R10. 確認数は confirmation budget で決める

- 毎回確認しない。`confidence / impact / reversible / route_delta` を見て、確認数を `0 / 1 / packet` にする。
- 既決事項 / 直前明示 / source pointer ありは再質問せず、既知として進める。
- route が変わる不明点だけ 1 問に圧縮する。3 件以上聞きたくなったら質問ではなく packet 化する。

### R11. 極端な過補正を検知する

- 指摘を受けた時に `削除します` / `全部やめます` / `今後やりません` / `実行しません` へ飛ばない。
- まず `user_intent / proportionality / safer_next_action` を切る。
- 同型の過補正が 2 回出たら、謝罪ではなく detector / gate / next_action に変換する。

## 標準出力 packet

AI が CEO に返す最小 packet:

```text
question:        # 1 問に圧縮
decision_needed: # 何の判断が要るか (1 行)
axis:            # primary axis (= pattern vocabulary より)
state:           # input | triage | ready | active | blocked | decision-needed | done
next_move:       # stay | up | down | reroute | park | exception
target:          # 着地先 (file / lane / owner)
reason:          # 1 行
fact_label:      # [事実: source] / [推測] / [不明]
```

Fractal root packet (= `root-router.md` §Protocol Packet) のサブセット。dialogue 用に圧縮。

## anti-pattern

| pattern | 検知 | 修復 |
|---|---|---|
| 問いを 5 件並べる | turn 出力が 5+ ? | R1 違反 → 1 問圧縮 |
| 抽象 ↔ 具体を 4 回以上往復 | 同じ axis で 4 turn 経過 | R2 違反 → reroute / decision-needed |
| AI が CEO の一言を生成する | content draft で CEO 発話の捏造 | R4 違反 → 事実取材へ戻す |
| 不明を断定する | source なしで「〜です」 | R7 違反 → `[不明]` ラベル |
| 違和感をスルー | CEO の「なんか違う」を packet 化せず実装続行 | R6 違反 → up move |
| Type1 を auto 実行 | 判断テーブル ask/deny を allow 扱い | R5 違反 → 即停止 + CEO 戻し |
| 既決事項を再質問する | すでに go / 統一 / 方針決定済みの論点を聞き返す | source を添えて実行し、不明点だけ 1 問にする |
| blocker を濫用する | owner / unblock_condition / next_check なしで止める | blocker ではなく unknown_or_unread として FDE core に戻す |
| 指摘後に極端へ振れる | 「全部やめる」「実行しない」などの過補正 | R11 違反 → proportionality を切り、より狭い next_action に戻す |

## lane 運用ポインタ

- Main / Top layer: AI ↔ CEO turn の上位判断入口。既存 `草薙 lane` は `dependency-registry:kusanagi-role` で本 file を参照。
- content lane: D-7 / D-8 (= R4) を本 file が引き継ぐ。
- coord / global-orchestrator: lane ↔ lane packet は `dependency-registry:lane-communication`、AI ↔ CEO turn は本 file。
- 4 AI review (= research / coding / decision lane) は本 file の R1 / R3 / R7 / R10 / R11 を front gate に通す。

## 更新 trigger

- 新しい anti-pattern が観察された時 (= 1 文追加 + Detector / Repair Path)。
- CEO 指示で R1-R9 が増減した時。
- pattern vocabulary に新 entry が入り、本 protocol との整合確認が要る時。
- `dependency-registry:content-decisions` D-7 / D-8 系列の更新があった時。

## pointer

| 用途 | file |
|---|---|
| Fractal root | `root-router.md` |
| 軸定義 | `axis-registry.md` |
| pattern vocabulary | `pattern-vocabulary.md` |
| lane ↔ lane packet | `dependency-registry:lane-communication` |
| Main / Top 互換 role (= 旧 草薙 lane) | `dependency-registry:kusanagi-role` |
| Type1 判断テーブル | `dependency-registry:claude-rules` |
| fact gate | `dependency-registry:fact-gate` |

