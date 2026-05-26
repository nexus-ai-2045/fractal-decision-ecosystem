---
title: FDE brain concept rollup
type: brain
status: active
created: 2026-05-13
owner: codex
scope: fde-brain-concept-rollup
tags: [fde, brain, concept-rollup, orchestration]
related:
  - core.md
  - dependency-registry.md
  - search-orchestration.md
  - dependency-registry:brain-concept-first-pass
  - dependency-registry:fdecc-review-workspace
  - dependency-registry:official-capability
  - dependency-registry:cross-runtime-primitives
---

# FDE brain concept rollup

Brain 内の概念は、FDE 本文へ全部入れない。FDE に入れるのは、どの lane / runtime / tool から来ても `entry -> packet -> evidence -> decision -> closure` に戻れる抽象だけ。

`FD` と発話された場合も `FDE` として扱う。

## 1. 吸収ルール

| 判定 | 入れるもの | 置き場 |
|---|---|---|
| absorb | 判断 OS として再利用できる抽象 | FDE core / axis / dialogue / search / lifecycle mini |
| reference | 外部正本・公式仕様・lane 固有運用 | `dependency-registry:<key>` |
| review-input | Cloud Code / 外部AI / FDECC の提案 | 採否してから FDE に戻す |
| hold | live state / log / surface id / hook 実体 / current-status 本文 | FDE には入れない |

## 1.1 元ファイルの扱い

元ファイルは原則 **残す**。FDE へ吸収した直後に物理削除しない。

| 元ファイル状態 | 扱い |
|---|---|
| `active` | まだ外部正本 / live authority として読む |
| `absorbed` | 概念は FDE へ吸収済み。元 file は証跡 / 詳細として残す |
| `superseded` | 新しい正本に置換済み。通常入口から外す |
| `archived` | 履歴として保存。通常起動・FDE判断では読まない |

吸収済みにする時は、元 file の先頭に可能なら次を置く。

```yaml
status: absorbed
absorbed_by: <target>.md
absorbed_at: YYYY-MM-DD
remaining_role: evidence | historical-source | external-authority
```

削除・物理移動は別 gate。`typology-lifecycle` と `typology-placement` を通し、link audit / review をしてから行う。

## 2. FDE に吸収する概念

| concept | 取り込み先 | source |
|---|---|---|
| packet / evidence / owner / closure | `core.md` / `root-router.md` | `dependency-registry:fde-root` |
| exception priority / 3x3 / entry routing | `root-router.md` | `dependency-registry:fde-root` |
| namespace / scope / abstraction_layer / merge_with / exit_condition | `core.md` / `pattern-vocabulary.md` | `dependency-registry:layer-vocabulary-synthesis` |
| capture / clarify / promote / close / archive / reflect | `lifecycle-operating-pattern.md` | `dependency-registry:typology-lifecycle` |
| official capability check | FDE filter / search orchestration | `dependency-registry:official-capability` |
| scope_route / fact_check / task_create / handoff / checkpoint | FDE packet の必須 guard 候補 | `dependency-registry:cross-runtime-primitives` |
| Codex final integrator | `search-orchestration.md` | `dependency-registry:claude-code-reference` + Codex運用 |

## 3. 参照に留める概念

| concept | registry key | 理由 |
|---|---|---|
| runtime 起動入口 | `dependency-registry:runtime-boot` | 起動正本であり、FDE本文へ重複させない |
| Codex restart | `dependency-registry:codex-restart` | runtime 固有 protocol |
| lane communication | `dependency-registry:lane-communication` | lane 間 packet 正本 |
| lane status | `dependency-registry:lane-status` / `dependency-registry:lane-status-protocol` | live cache / 履歴化しやすい |
| typology / placement | `dependency-registry:typology-placement` | 保存先の全体正本 |
| security | `dependency-registry:security-baseline` | policy authority |
| CEO response gate | `dependency-registry:ceo-response-gate` | Cloud Code 応答 gate。dialogue protocol へ概念だけ吸収 |
| cmux 操作 | `dependency-registry:cmux-reference` | surface id / workspace id は live 実体 |
| shared scripts / lib | `dependency-registry:shared-scripts` / `dependency-registry:shared-lib` | 実装実体 |

## 4. FDECC の扱い

`dependency-registry:fdecc-review-workspace` は、基盤側で Cloud Code に FDE をレビュー・改善させている作業枝として扱う。

- FDECC をそのまま正本にしない。
- FDECC の提案は `review-input` として Codex 側で採否する。
- 良い案は FDE の薄い部品へ戻す。
- 未採用案、draft、workspace 下の調査ログは FDE 本文へ入れない。

## 5. Hold するもの

- live state / current-status 本文
- cmux surface 番号、workspace 番号、pane 番号
- hook / settings / `~/.claude` 実体
- raw external AI output
- FDECC `_workspace` draft
- historical visual map / snapshot

## 6. 次の吸収候補

| candidate | action |
|---|---|
| `cc-ceo-response-behavior-gate.md` | dialogue-protocol の anti-pattern / response packet へ概念だけ吸収 |
| `official-capability-inventory-first.md` | FDE filter に prior-art gate として短く吸収 |
| `cross-runtime-operational-primitives.md` | FDE packet guard の source として registry 化 |
| `orchestrator-routing-rule.md` §distillation / delegation / execution_mode | search-orchestration / root-router に短く反映 |
| FDECC registry方式 | dependency-registry の改善案として採否 |

## 7. Thin pass report

Brain root の薄い一巡分類は `dependency-registry:brain-concept-first-pass` に置く。

この file に長表を持ち込まない。FDE 本体は吸収ルールと次の候補だけを持つ。

## 8. Thin absorb pass 1

| source | absorbed_into | absorbed_concept |
|---|---|---|
| `orchestrator-routing-rule.md` | `core.md` | `execution_mode`: summarize / delegate / execute / review / decide / park |
| `official-capability-inventory-first.md` | `search-orchestration.md` | prior-art gate: official / OSS / local existing before new mechanism |
| `cc-ceo-response-behavior-gate.md` | `dialogue-protocol.md` | existing-decision re-ask and blocker abuse anti-patterns |

## 9. Thin absorb pass 2

| source | absorbed_into | absorbed_concept |
|---|---|---|
| `FDECC/registry/dependency-registry.md` | `dependency-registry.md` | Data / Policy / State / Procedure / Knowledge role split |
| `FDECC/spec/orchestration-efficiency-lessons.md` | `search-orchestration.md` | simple mechanical ops stay in Codex body; exploration / judgement is delegated |
| `FDECC/spec/orchestration-efficiency-lessons.md` | `dependency-registry:fde-orchestration-return-stack-report` | plan-before-dispatch and 1 agent = 1 file or 1 concept |

## 10. Thin absorb pass 3

| source | absorbed_into | absorbed_concept |
|---|---|---|
| CEO correction 2026-05-13 | `core.md` | `orchestration_required` / `delegate_plan` / `codex_main_role` as pre-execution gate |
| CEO correction 2026-05-13 | `search-orchestration.md` | trigger table: wide read / multi-target / external AI / send / collect / comparative review |
| CEO correction 2026-05-13 | `search-orchestration.md` | smoke / E2E check for orchestration gate |

## 11. Thin absorb pass 4

| source | absorbed_into | absorbed_concept |
|---|---|---|
| `FDECC/router/root-router.md` | `root-router.md` | packet / move の重複定義を `core.md` 正本へ寄せる |
| `FDECC/README.md` / `MIGRATION-MAP.md` | `README.md` / `external-references.md` | FDECC は正本ではなく review / refactor workspace |
| `FDECC/pointer` / `registry` | `source-pointers.md` / `external-references.md` / `dependency-registry.md` | internal source と external review の分離を明示 |

## 12. FDECC 精査 pass 5

| source | decision | target | reason |
|---|---|---|---|
| `FDECC/registry/axis-registry.md` | adopt | `axis-registry.md` | CEO GO / kusanagi D-10 済みなのに正本が shadow のままだったため、8-axis promote 状態だけ反映 |
| `FDECC/spec/dialogue-protocol.md` | adopt | `dialogue-protocol.md` | 横断 protocol の owner が `kusanagi` のままだったため `codex` へ補正 |
| `FDECC/spec/orchestration-efficiency-lessons.md` | partial-adopt | `operating-card.md` | plan-first / 1 delegate = 1 file or concept / smoke return / 機械 op 直実行だけ採用 |
| `FDECC/registry/dependency-registry.md` | already-covered | `dependency-registry.md` | `content-decisions` key は正本側に登録済み。FDECC path 化は不採用 |
| `FDECC/registry/pattern-vocabulary.md` | hold | `pattern-vocabulary.md` | 圧縮案はあるが正本側の table が実用中。CEO 判断待ちの `深度` / `スレッド` は保持 |
| `FDECC/router/root-router.md` | reject-as-copy | `root-router.md` | FDECC path へ向ける差分は作業枝用。現行正本 `` には戻さない |

## 13. Naming pass 6

| source | decision | target | reason |
|---|---|---|---|
| CEO correction 2026-05-13 | adopt | `axis-registry.md` / `core.md` / `dialogue-protocol.md` / `external-ai-route-registry.md` | 上位判断レイヤーの主呼称を `Main / Top` に寄せ、`草薙` は既存 lane 名・互換 alias として扱う |

closure_rule: active

