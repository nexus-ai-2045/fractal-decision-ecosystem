---
title: Fractal Decision Ecosystem Source Pointers
type: brain
status: active
created: 2026-05-10
updated_at: 2026-07-18T00:00:00+0900
owner: codex
related:
  - root-router.md
  - dependency-registry.md
tags: [layer-context, source, pointer, ssot, public]
---

# Fractal Decision Ecosystem 出典ポインタ

`root-router.md` の元議論ポインタ集。root router 本文には要約だけ置き、詳細はここから辿る。

この file は **公開 package で解決できる** source cluster の入口。browser AI / 外部AI / raw review は `external-references.md` へ寄せる。元の private workspace path や `imported-source` だけの行は置かない。吸収済みの概念は repo-local file を指す。

| cluster | 何を見るか | 公開解決先 | source class |
|---|---|---|---|
| 三層運用 / TOP・秘書・Coord | 基本ロール / escalation / inbox lifecycle / 詰まりゼロ | `operating-card.md` / `dialogue-protocol.md` | absorbed |
| fact / scope gate | source 確認、scope route、3x3 reroute の既存 gate | `core.md` / `public-kernel/GATES.md` | absorbed |
| layer / port 整理 | 7 layer + capability port / surface vs lane | `axis-registry.md` / `pattern-vocabulary.md` | absorbed |
| orchestrator / harness 対応 | Coord=dispatcher、Foundation=harness、秘書=eval+rollup | `ai-development-living-harness.md` / `search-orchestration.md` | absorbed |
| role drift / TOP化 | Coord / 秘書の役割ズレ、self-loop 破棄、protocol freeze | `operating-card.md` / `dialogue-protocol.md` | absorbed |
| 5/10 議論まとめ | 7 layer、voice ambiguity、維持モード、retake list | `brain-concept-rollup.md` / `pattern-vocabulary.md` | absorbed |
| TOP評価 / Outcome 定義 | 「動く」= Outcome micro-step、coord 縮退、retake 優先順 | `OPERATIONAL_GUARANTEE.md` / `MVP_STATUS.md` | absorbed |
| 秘書 freeze | 秘書の TOP 化停止、pointer 1 行 only | `operating-card.md` | absorbed |
| content 原則 | AI は発信者ではなく整形者、本人の一言が先 | `dialogue-protocol.md` | absorbed |
| Output 圧迫 / Outcome 優先 | 公開停止真因、仕組み整備が Outcome を圧迫する問題 | `PUBLIC_KERNEL_PLAN.md` / `ROADMAP.md` | absorbed |
| voice ambiguity risk | ambiguity × impact × irreversibility × downstream_branching | `dialogue-protocol.md` / `search-orchestration.md` | absorbed |
| daily improvement | 各 cycle 末尾の 1 改善 / 大 sweep 禁止 | `lifecycle-operating-pattern.md` / `ROADMAP.md` | absorbed |
| RICE / idea ledger | idea を RICE と state に閉じる運用 | `dependency-registry:rice-rescoring` / `dependency-registry:ideas-ledger` | operator-local-adapter |
| procedure / common sense | 運用標準、CEO-facing decision UI、protocol common sense | `operating-card.md` / `dialogue-protocol.md` | absorbed |
| FDECC review / refactor workspace | 外部構造提案を採否して FDE へ戻す | `external-references.md` / `dependency-registry:fdecc-review-workspace` | withheld |
| visual | この SSOT の視覚ビュー | `visual.html` / `SYSTEM_OVERVIEW.md` | repo-local |

未掲載の新規議論が出たら、まずこの表に cluster と **公開解決先** を 1 行足す。解決できない private path は書かず、`operator-local-adapter` または `withheld` にする。本文展開は原則しない。
