---
title: Fractal Decision Ecosystem index
type: index
status: active
created: 2026-05-13
owner: codex
scope: fde
tags: [fde, index, brain]
---

# Fractal Decision Ecosystem（FDE）

Fractal Decision Ecosystem（FDE）は、判断・通信・実装・検索・検証・改善を
迷子にしないための **North Star / root routing layer**。

FDE は、会話・調査・実装・レビュー・公開判断のどの粒度から始まっても、
`entry -> packet -> evidence -> decision -> closure` に戻すための routing OS。

- Fractal: 会話、検索、実装、lane、外部AI、経営判断のどの粒度でも同じ型で使える。
- Decision: 何を決めたか、何を決めていないか、次の一手は何かを短く残す。
- Ecosystem: 個別 rule の寄せ集めではなく、例外・保留・更新・破棄まで矛盾なく閉じる判断環境。

## Stable Name / Alias

- 正式名: **Fractal Decision Ecosystem**
- 略称: `FDE`
- 日本語説明: 判断・通信・実装・検索・検証・改善のルーティング OS
- 表記ルール: 人間向け本文では初出を `Fractal Decision Ecosystem（FDE）` と書き、以後だけ `FDE` を使う。
- `FD` と言われた場合も、文脈上は `FDE` として扱う。

FDE は全情報を吸い込む巨大 hub ではない。どの入口から始まっても、
`entry -> packet -> evidence -> decision -> closure` に戻すための方位基準である。

ここに置くのは、複数領域で繰り返し効く軽量部品だけ。太い本文に戻さず、
動作・データ・policy・state・procedure・knowledge を分けて保つ。

この公開パッケージは、完成済みの軽量部品だけを含む。draft workspace、個人環境の
runtime state、秘密情報、外部送信ログは公開境界の外に置く。

## What FDE Is

FDE は以下を決めるための routing OS。

- 今の問いは何か。
- どの mode で閉じるか。
- owner / lane / layer はどこか。
- 何を evidence として採用するか。
- どこへ保存・委譲・保留・退避するか。
- どの closure_rule で閉じるか。

FDE が直接持つのは判断の型と入口。個別手順、lane 固有ルール、実装詳細、
外部正本は registry / playbook / report / source pointer へ逃がす。

## Time / Provenance Rule

FDE の原則は日付に依存しない。日付は provenance / lifecycle / evidence / report / audit trail のために使う。

- `created` / `updated` / `source` / `promote_at` / dated report path は traceability として残す。
- core concept / heading / route name / gate name / closure rule に日付を混ぜない。
- 日付が必要な説明は source / evidence / reflected / archive へ置き、本文の意味は timeless に保つ。
- FDE は「いつ作ったか」ではなく「どの問いを、どの根拠で、どこへ閉じるか」を決める。

## 初見 runtime の読む順

FDE を使う runtime は、外部 report / inbox / lane rule を先に読まない。
まずこの repository 内で routing を閉じる。

1. `operating-card.md`: 毎 turn の最小起動。本線、gate、budget、closure を決める。
2. `dialogue-protocol.md`: CEO / 人間との対話、1問圧縮、fact tag、Type1 の作法を見る。
3. `axis-registry.md`: mode、8-axis、closure、No New Surface Before Mapping を見る。
4. `core.md`: packet / move / orchestration_required の最小定義を確認する。
5. `data-index.md`: type / catalog / source pointer の入口を確認する。
6. `dependency-registry.md`: FDE 外の SSOT / report / lane rule を読む必要があるかを判定する。
7. `source-pointers.md` / `external-references.md`: 元議論、外部AI review、raw cluster は pointer 経由でだけ辿る。

registry にない外部 source は、FDE の根拠として採用しない。必要なら `unabsorbed_candidate` として audit / Type1 review に戻す。

## 通常入口（毎セッション読む）

session 開始時に必ず読む 3 file + 詳細参照の主要 file。

| file | 役割 |
|---|---|
| [operating-card.md](operating-card.md) | **共通必読1**: 毎 turn 最初に読む最小カード。本線 / route / 役割分担 / closure / §0.0 Session Boot Gate |
| [dialogue-protocol.md](dialogue-protocol.md) | **共通必読2**: AI ↔ CEO 対話の 1問圧縮 / 抽象具体往復 / Type1 / fact tag |
| [axis-registry.md](axis-registry.md) | **共通必読3**: 8-axis / Work Mode Gate / Closure Rule / surface 拡張抑制 |
| [core.md](core.md) | 3回確認 / 4ポイント復帰 / route move だけを持つ薄い入口 |
| [root-router.md](root-router.md) | 展開版 FDE root router / 詳細参照 |
| [data-index.md](data-index.md) | type / catalog / source pointer の入口 |
| [dependency-registry.md](dependency-registry.md) | FDE 外部依存の唯一の registry |
| [search-orchestration.md](search-orchestration.md) | 検索を sidecar / subagent / 外部AIへ逃がし、Codex 本体へ採否だけ戻す薄い規則 |
| [lifecycle-operating-pattern.md](lifecycle-operating-pattern.md) | operating-card 用の capture / close / archive / reflect 共通 slot |

## Placement Rule

新しい rule / prompt / graph / script / workflow を作る前に、まず既存 map 上の置き場を探す。

| 種別 | 置き場 |
|---|---|
| 判断の動作 | `core.md` / `operating-card.md` |
| 軸・mode・closure | `axis-registry.md` |
| 対話作法 | `dialogue-protocol.md` |
| data / catalog / pointer | `data-index.md` / `source-pointers.md` |
| 外部正本・手順・playbook 参照 | `dependency-registry.md` |
| FDE 外の詳細手順 | `dependency-registry:playbooks` または対象 repo/tool の runbook |
| 調査・監査・実測 | `dependency-registry:reports` |
| 作業中 draft | 公開境界の外にある private draft workspace |

新しい file は「何を軽くするか」が 1 行で言える時だけ追加する。
既存の WHERE / HOW / WITHWHAT で扱えるなら、新規面を作らない。

## Graph / Visuals

FDE の graph 表現は FDE 本体ではなく視覚入口である。

- Fractal Decision Ecosystem（FDE）は North Star layer。
- 周辺 brain / operating notes は foundation layer。
- `_graph-network` や coverage shard は迷子防止の補助航路であり、FDE そのものではない。
- graph / color / shard の具体手順は FDE 本文へ厚く入れず、registry / runbook / procedure へ逃がす。
- FDE anchor は、全ノートを吸い込む巨大 hub ではなく、迷った時に戻る方位基準として扱う。

## 補助（必要な時だけ読む）

特定用途・詳細参照・外部AI連携・証跡 file。通常の session 起動では読まない。

| file | 役割 |
|---|---|
| [pattern-vocabulary.md](pattern-vocabulary.md) | 語彙・alias・pattern chain を axis へ吸わせる表 |
| [source-pointers.md](source-pointers.md) | 元議論・source cluster の pointer 集 |
| [external-references.md](external-references.md) | browser AI review / 外部 best practice / raw output の参照入口 |
| [brain-concept-rollup.md](brain-concept-rollup.md) | Brain 内の概念を FDE 吸収 / registry 参照 / hold に分ける入口 |
| [external-ai-route-registry.md](external-ai-route-registry.md) | browser AI / API route の用途別 registry の FDE snapshot |
| [external-ai-file-loop.md](external-ai-file-loop.md) | 外部AI file-backed loop の FDE snapshot |
| [external-ai-file-review-packet.md](external-ai-file-review-packet.md) | 外部AI review packet template の FDE snapshot |
| [user-judgment-confidence-layer.md](user-judgment-confidence-layer.md) | ユーザー判断の信頼度層 |
| [ops-best-practice-inventory.md](ops-best-practice-inventory.md) | Claude ops / hooks / dependency-registry best practice の FDE filter |
| [visual.html](visual.html) | FDE の視覚ビュー |

## 証跡 / reflected

| file | 役割 |
|---|---|
| [browser-ai-review-synthesis.md](browser-ai-review-synthesis.md) | FDE v1 browser AI review の反映済み証跡 |
| [ops-best-practice-inventory.md](ops-best-practice-inventory.md) | Claude ops / hooks / dependency-registry:project-claude best practice の FDE filter |
| [research-lane-round-trail.md](research-lane-round-trail.md) | Research lane の FDE round trail 取り込み証跡 |

## External Evidence / Outside This Package

| file | 役割 |
|---|---|
| historical v1 draft report | FDE v1 draft の履歴参照。通常入口では読まない |
| contradiction audit report | FDE / Cloud Code contradiction audit の作業証跡 |
| orchestration return stack report | orchestration / layer 論点 return stack |

## 追加ルール

- ここには完成した軽量部品だけを置く。
- raw議論、検討中メモ、外部AIの長文出力は置かない。
- draft / continue / 作業中 report は公開境界の外に置く。
- 新しい file は「何を軽くするか」が 1 行で言える時だけ追加する。
- FDE 本体を読まずに済ませるための入口を増やし、FDE 本体の説明を増やさない。
- 毎 turn の起動は [operating-card.md](operating-card.md) から始める。詳細が必要な時だけ `core.md` / `search-orchestration.md` へ降りる。
- FDE 外の path を本文へ直書きしない。必要な外部依存は [dependency-registry.md](dependency-registry.md) に集約する。
- FDE 関連の外部 rule / prompt / runbook は、採用前に `absorbed / external-authority / unabsorbed_candidate / not_fde / stale` へ分類する。

closure_rule: active

