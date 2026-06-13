---
title: Fractal Decision Ecosystem
type: index
status: active
created: 2026-05-13
owner: codex
scope: fde
tags: [fde, index, brain]
---

# Fractal Decision Ecosystem（FDE）

Fractal Decision Ecosystem（FDE）は、判断・通信・実装・検索・検証・改善を迷子にしないための routing OS です。

どの入口から始まっても、FDE は作業を次の型へ戻します。

```text
entry -> packet -> evidence -> decision -> closure
```

FDE が扱うのは、個別の作業内容そのものではなく、作業をどこへ置き、何を根拠にし、どう閉じるかです。長い議論、raw log、private draft、外部AIの出力本文はここへ厚く入れず、必要な file や registry へ逃がします。

## まず読むもの

初見、または新しい session では、次の順に読んでください。

| 順 | file | 役割 |
|---:|---|---|
| 1 | [operating-card.md](operating-card.md) | 毎 turn の最小起動。本線、gate、mode、closure を決める |
| 2 | [dialogue-protocol.md](dialogue-protocol.md) | AI と人間の対話ルール。1問圧縮、fact tag、Type1 境界を見る |
| 3 | [axis-registry.md](axis-registry.md) | 8-axis、work mode、closure rule、置き場の判断を見る |
| 4 | [core.md](core.md) | packet / move / orchestration_required の薄い定義を見る |
| 5 | [root-router.md](root-router.md) | FDE root router の詳細を見る |

迷ったら、まず [operating-card.md](operating-card.md) に戻します。

## FDE が決めること

FDE は、次の問いを短く閉じるための仕組みです。

- 今の問いは何か。
- どの mode で進めるか。
- owner / lane / layer はどこか。
- 何を evidence として採用するか。
- どこへ保存、委譲、保留、退避するか。
- どの closure_rule で完了とみなすか。

FDE が直接持つのは判断の型と入口です。個別手順、lane 固有ルール、実装詳細、外部正本は registry / playbook / report / source pointer へ分けます。

## 最小 packet

FDE で作業を始める時は、最低限この形に落とします。

```text
packet_id:
intent:
mode:
who:
what:
why:
when:
where:
how:
howmuch:
withwhat:
closure_rule:
```

短い作業では `who / what / why / when / where` だけで足ります。実装、調査、公開判断、外部AI連携など、リスクや迷子化の可能性がある時だけ `how / howmuch / withwhat` を足します。

## 主要 file

| file | 役割 |
|---|---|
| [operating-card.md](operating-card.md) | 毎 turn の起動カード。main thread、gate、return_to、closure を決める |
| [dialogue-protocol.md](dialogue-protocol.md) | AI と人間の対話ルール。問いの圧縮、fact tag、Type1 境界 |
| [axis-registry.md](axis-registry.md) | 8-axis、work mode、closure rule、配置判断 |
| [core.md](core.md) | FDE の最小 core。packet / move / orchestration_required |
| [root-router.md](root-router.md) | 詳細な root routing と scoring |
| [data-index.md](data-index.md) | type / catalog / source pointer の入口 |
| [dependency-registry.md](dependency-registry.md) | FDE 外部依存、外部正本、playbook、report の registry |
| [source-pointers.md](source-pointers.md) | 元議論や source cluster への pointer |
| [search-orchestration.md](search-orchestration.md) | 検索、外部AI、browser route を薄く扱う規則 |
| [lifecycle-operating-pattern.md](lifecycle-operating-pattern.md) | capture / close / archive / reflect の共通 slot |

## 配置ルール

新しい rule、prompt、workflow、script、file を作る前に、既存の置き場を探します。

| 種別 | 置き場 |
|---|---|
| 判断の動作 | `core.md` / `operating-card.md` |
| 軸、mode、closure | `axis-registry.md` |
| 対話作法 | `dialogue-protocol.md` |
| data / catalog / pointer | `data-index.md` / `source-pointers.md` |
| 外部正本、手順、playbook 参照 | `dependency-registry.md` |
| FDE 外の詳細手順 | `dependency-registry:playbooks` または対象 repo/tool の runbook |
| 調査、監査、実測 | `dependency-registry:reports` |
| 作業中 draft | 公開境界の外にある private draft workspace |

新しい file は、「何を軽くするか」が 1 行で言える時だけ追加します。

## 公開境界

この repository は、Fractal Decision Ecosystem（FDE）の standalone public candidate として整理されています。ただし、公開や repository visibility 変更はこの README では承認されません。

公開前には、必ず人間 review と明示承認が必要です。公開判断では、少なくとも次を確認します。

- README / LICENSE / SECURITY.md / PUBLIC_READY.md
- secret scan
- personal path scan
- draft workspace の除外
- patent / public kernel gate
- GitHub repository visibility の明示承認

現在の公開準備状態は [PUBLIC_READY.md](PUBLIC_READY.md) を見てください。

## 補助 file

| file | 役割 |
|---|---|
| [pattern-vocabulary.md](pattern-vocabulary.md) | 語彙や alias を axis へ吸わせる表 |
| [external-references.md](external-references.md) | 外部 review や raw output への参照入口 |
| [brain-concept-rollup.md](brain-concept-rollup.md) | Brain 内の概念を FDE へ吸収、参照、保留に分ける入口 |
| [external-ai-route-registry.md](external-ai-route-registry.md) | browser AI / API route の用途別 registry snapshot |
| [external-ai-file-loop.md](external-ai-file-loop.md) | 外部AI file-backed loop の FDE snapshot |
| [external-ai-file-review-packet.md](external-ai-file-review-packet.md) | 外部AI review packet template の snapshot |
| [user-judgment-confidence-layer.md](user-judgment-confidence-layer.md) | ユーザー判断の信頼度層 |
| [ops-best-practice-inventory.md](ops-best-practice-inventory.md) | ops / hooks / dependency-registry best practice の FDE filter |
| [visual.html](visual.html) | FDE の視覚ビュー |

## 言語方針

- 初出は `Fractal Decision Ecosystem（FDE）` と書き、以後は `FDE` を使います。
- 人間が読む本文、見出し、説明文は日本語で書きます。
- code identifier、schema field、file name、GitHub Actions keyword、frontmatter key は英語のまま維持します。
- 日付は provenance / lifecycle / evidence / report / audit trail のために使います。core concept、heading、route name、gate name、closure rule には日付を混ぜません。

## この repository に置かないもの

FDE は全情報を吸い込む巨大 hub ではありません。次のものは、必要に応じて pointer 化し、本文へ厚く戻しません。

- raw 議論
- 検討中メモ
- 外部AIの長文出力
- private draft workspace
- machine-local runtime state
- 秘密情報
- 外部送信ログ

closure_rule: active
