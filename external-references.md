---
title: FDE external references
type: brain
status: active
created: 2026-05-13
updated_at: 2026-07-18
owner: codex
scope: fde-external-references
tags: [fde, external-ai, references, source, public]
related:
  - root-router.md
  - source-pointers.md
  - external-ai-route-registry.md
---

# FDE 外部参照

FDE の外部参照・browser AI review・外部 best practice はここから辿る。

FDE core / root-router には外部出力の長文を混ぜない。採用済みの判断だけを FDE 側に戻し、raw / report / route registry は pointer として保持する。

内部 source cluster は `source-pointers.md`、外部 review はこの file と `dependency-registry` で扱う。公開 package では物理 path や opaque label だけで閉じない。

## 1. Browser AI / external AI route

| 用途 | pointer | 扱い |
|---|---|---|
| browser AI / API route registry | `external-ai-route-registry.md` | route / 得意分野 / smoke schema の参照。FDE本文には取り込まない |
| external AI file loop | `external-ai-file-loop.md` | file-backed review の運用参照 |
| review packet template | `external-ai-file-review-packet.md` | 外部AIへ投げる packet template |

## 2. FDE review source

| source | 何を見たか | 反映先 |
|---|---|---|
| `browser-ai-review-synthesis.md` | FDE v1 の browser AI review 統合 | `root-router.md` |
| `ops-best-practice-inventory.md` | Claude ops / hooks / best practice の FDE filter | `root-router.md` / ops 方針 |
| `research-lane-round-trail.md` | Research lane round trail | `source-pointers.md` |
| `dependency-registry:fde-contradiction-audit-report` | contradiction audit（absorb 済み） | `ops-best-practice-inventory.md` |
| `dependency-registry:fde-orchestration-return-stack-report` | orchestration return stack（absorb 済み） | `search-orchestration.md` / `operating-card.md` |
| `dependency-registry:fdecc-review-workspace` | 外部 refactor / review workspace | withheld。採否後だけ FDE 正本へ薄く戻す |

## 3. Raw external AI outputs

| cluster | 公開解決先 | 扱い |
|---|---|---|
| 2026-05-12 FDE protocol browser AI raw | `browser-ai-review-synthesis.md` | 要約のみ。raw 本文は持たない |
| 2026-05-13 layer vocabulary raw | `pattern-vocabulary.md` | 要約のみ |
| 2026-05-13 orchestration test plan raw | `search-orchestration.md` | 要約のみ |
| 2026-05-08 external AI raw set | `external-ai-route-registry.md` | 要約のみ |

## 4. 採用ルール

- raw output は FDE 正本に貼らない。
- `adopt / revise / hold / reject / unknown` へ分類してから戻す。
- 採用したら `source-pointers.md` か対象 file の `related` に **公開解決先** を足す。
- 未採用・未確認は `[不明]` または `hold` として残す。
- private path や `imported-source` だけの行は追加しない。

closure_rule: active
