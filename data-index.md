---
title: Fractal Decision Ecosystem data index
type: brain
status: active
created: 2026-05-13
owner: codex
scope: fde-data-index
tags: [fde, data, index, routing]
related:
  - core.md
  - root-router.md
  - axis-registry.md
  - pattern-vocabulary.md
  - source-pointers.md
  - external-references.md
---

# Fractal Decision Ecosystem データ索引

FDE data index は、FDE core が参照する **データ / catalog / pointer** の入口。FDE の動作規則はここに置かない。

## 1. Catalog

| 欲しいもの | 見る file |
|---|---|
| package entry / FDECC との関係 | `README.md` |
| packet / move / orchestration gate | `core.md` |
| axis / route の詳細 | `axis-registry.md` |
| 語彙・入口語・pattern chain | `pattern-vocabulary.md` |
| 元議論・source cluster | `source-pointers.md` |
| Brain 内概念の吸収/参照/保留 | `brain-concept-rollup.md` |
| 外部AI・browser AI review・best practice | `external-references.md` |
| dialogue / CEO 問いの作法 | `dialogue-protocol.md` |
| AI開発標準カード / Living Harness | `ai-development-living-harness.md` |
| MVP軸別13運用カード | `mvp-axis-operating-card.md` |
| 検索の分担 / Codex 本体への戻し方 | `search-orchestration.md` |
| 外部依存 key / FDECC review workspace | `dependency-registry.md` |
| SSOT 管理 (registry / loader / lint / placement / 構造分離) | `dependency-registry.md`（operator-local adapter。無い場合は本 repo の README / decisions / public-kernel で閉じる） |
| lifecycle mini / operating-card slot | `lifecycle-operating-pattern.md` / `operating-card.md` |
| 既存の太い root router | `root-router.md` |

## 2. FDE type の扱い

type は FDE core に増やさない。必要な時だけ選ぶ lens として扱う。

```text
search / matrix / development / test / cmux-operation
communication / protocol / security / typology / naming
idea / reflection / orchestration
```

type が増えそうな時:
1. 既存 type の組み合わせで吸収する。
2. lane local playbook へ逃がす。
3. 2 回以上、複数 lane で再発したら catalog 追加を検討する。

## 3. Data / Policy / State の分離

| 種別 | 意味 | 置き場 |
|---|---|---|
| core | 判断の動作 | `core.md` |
| data | type / catalog / source pointer | 本 file |
| policy | してよい/ダメ | `public-kernel/GATES.md` / `SECURITY.md` / `dependency-registry:fact-gate` |
| state | 現在地 / queue / blocker | operator-local adapter、または本 repo の active docs |
| procedure | 手順 | `operating-card.md` / operator-local playbooks |
| knowledge | 知見 | `ops-best-practice-inventory.md` / operator-local reports |

closure_rule: active
