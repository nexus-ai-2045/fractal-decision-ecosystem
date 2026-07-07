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

![FDEの道具箱を開く個人と人懐っこいAI相棒](assets/fde-cover.png)

グラフィカルに読む入口: [visual.html](visual.html)

レビュー導線: [visual.html](visual.html) → [ROADMAP.md](ROADMAP.md) → [OPERATIONAL_GUARANTEE.md](OPERATIONAL_GUARANTEE.md) / [MVP_STATUS.md](MVP_STATUS.md) → [PUBLIC_KERNEL_PLAN.md](PUBLIC_KERNEL_PLAN.md) → [TODO_FDE_PUBLIC_KERNEL_RIGHTS.md](TODO_FDE_PUBLIC_KERNEL_RIGHTS.md)

Fractal Decision Ecosystem（FDE）は、AI が本来デフォルトで持っているはずの判断・整理・検証・接続・改善の能力を、毎回ちゃんと発揮させるための体系です。

AI は、問いを分解する、根拠を分ける、過去の文脈に接続する、危険な操作を止める、次の一手へ閉じる、といった能力をすでに持っています。けれど実運用では、その能力が毎回自動で発火するとは限りません。FDE は、その「発揮されない問題」を解くために、入口、判断軸、根拠、閉じ方、発火条件をまとめた routing OS です。

## 完成図

FDE の完成図は、巨大なAIアプリではなく、AI作業を軽く賢くするための **判断制御面** です。人間の依頼、ローカルファイル、GitHub、外部AI、公開候補が混ざっても、毎回同じ順番で「何を根拠に、どこまで進めて、何を止めるか」を閉じます。

完成時に起きてほしい変化:

| 以前 | FDE後 |
|---|---|
| 毎回、文脈確認と残務確認を手でやり直す | `entry -> packet -> evidence -> decision -> closure` に戻し、必要な file と gate だけを見る |
| ロードマップが機能一覧になり、完了条件が曖昧になる | `goal / evidence / gate / owner / done_when` で、やることと閉じ方を同時に持つ |
| 「完了」「公開可能」「運用保証」が混ざる | 実装残務、運用残務、外部/公開承認を分けて答える |
| 外部AIやdelegateの意見をそのまま採用しそうになる | evidence、return contract、adoption gate を通してから採否する |
| 公開・送信・visibility変更が勢いで進みそうになる | human review と明示承認まで止める |

つまり「軽くなる」は、読む量を減らすことです。「賢くなる」は、AIが毎回よい判断を思いつくことではなく、よい判断に必要な gate と evidence が自動で発火することです。

## 何に困っている時の解決策か

FDE は、「AI ができるはずなのに、その場で発揮されない」状態を解くための仕組みです。

| 困りごと | FDE で発火させる能力 |
|---|---|
| AI が文脈を読めるはずなのに、毎回浅い返答から始まる | entry を packet 化し、過去文脈・目的・戻り先へ接続する |
| AI が判断できるはずなのに、質問や提案が散らばる | mode、axis、closure_rule を先に立て、何を決める turn かを固定する |
| AI が検証できるはずなのに、事実・推測・不明が混ざる | evidence と fact label を必須化し、根拠のない断定を止める |
| AI が危険操作を避けられるはずなのに、公開・送信・visibility 変更が曖昧になる | Type1 / publication gate を発火させ、人間承認まで止める |
| AI が改善できるはずなのに、同じ失敗を反省だけで終える | route_failure を分類し、skill / document / validator のどこを直すかへ落とす |
| AI が全体を接続できるはずなのに、file、外部AI、GitHub、local state がばらける | registry / source pointer で正本、外部 authority、未吸収 candidate、stale を分ける |

## どのように発火させるか

FDE は、どの入口から始まっても、AI の処理を次の型へ戻します。

```text
entry -> packet -> evidence -> decision -> closure
```

この型は、AI に次の能力を自動で呼び出させるための発火順です。

| 段階 | 発火させる能力 |
|---|---|
| `entry` | ユーザーの言葉から、本当の入口と目的を読む |
| `packet` | 問い、owner、mode、戻り先、閉じ方を圧縮する |
| `evidence` | 事実、推測、不明、source pointer を分ける |
| `decision` | adopt / park / discard / decision-needed / blocked を切る |
| `closure` | 何が終わり、何が未保証で、次に何をするかを返す |

つまり、FDE が直接扱うのは個別の作業内容そのものではなく、AI が本来やるべき判断動作を、どの条件で発火させ、どの根拠で閉じるかです。長い議論、raw log、private draft、外部AIの出力本文はここへ厚く入れず、必要な file や registry へ逃がします。

## 何で発火させるか

FDE は、主に次の部品で AI の能力を発火させます。

| 部品 | 役割 |
|---|---|
| `trigger` | どの言葉、状態、失敗、操作で FDE を起動するかを決める |
| `packet` | 今の問い、owner、mode、根拠、閉じ方を短く持つ |
| `mode` | search / implement / review / operate / ideate / decide のどれで進むかを決める |
| `8-axis` | who / what / why / when / where / how / howmuch / withwhat に分けて迷子化を防ぐ |
| `evidence` | 事実、推測、不明を分け、採用する根拠を明示する |
| `gate` | 公開、外部送信、破壊操作、secret、visibility 変更を人間承認まで止める |
| `registry / source pointer` | 詳細手順、外部正本、raw source を本文へ抱え込まず参照する |
| `closure_rule` | 何をもって完了、保留、blocker、unknown とするかを先に決める |
| `route_failure` | 能力が発揮されなかった時に、原因と修正先を分類する |

## 自動発火の考え方

FDE の目的は、AI に毎回「FDE 使う？」と聞かせることではありません。特定の言葉、状況、リスク、失敗を見たら、自動で必要な能力が起動する状態にすることです。

代表的な発火条件:

- FDE、判断整理、正本、root router、operating card、fact gate などの語が出た時
- 事実、推測、不明、根拠、source、evidence が混ざりそうな時
- 完了、保証、公開可能、送信済み、採用済みなどを断定しそうな時
- 公開、投稿、共有、GitHub visibility、外部送信、credential、hook/settings に触れる時
- 同じ失敗、同じ指摘、同じ迷子化が繰り返された時
- 新しい file、rule、workflow、prompt を作りたくなった時
- 外部AI、browser、GitHub、local file のどれを正本にするか迷う時

発火後は、まず `entry -> packet -> evidence -> decision -> closure` に戻します。必要なら `operating-card.md`、`dialogue-protocol.md`、`axis-registry.md` の順で読む範囲を広げます。

## なぜ公開候補にするか

FDE は、個人の技量だけで完成させるためのものではありません。

個人で閉じると、到達点はどうしてもその人の得意領域と技量の上限に引っ張られます。だから、自分が得意なところに尖って取り組み、足りないところはそれを得意な人が補える形にしておく必要があります。

FDE を公開候補にする理由は、AI の使い方を一部の個人技や暗黙知に閉じないためです。AI が本来持っている能力を発火させる体系を外に出し、他の人が読み、試し、補い、直せる形にすることで、日本国内でも実践知が広がります。

AI格差は生まれます。だからこそ、FDE は「AI をうまく使える人だけの秘密の手順」ではなく、発火条件、判断軸、根拠、公開境界、失敗時の直し方まで見える形にします。

## 隣接構想: AI contact safety contract

FDE は、AI同士の contact が発生する場面でも、判断の型を崩さないための抽象契約を持ちます。

ただし、device app、OS service、avatar、音声UI、download data bundle の製品仕様は FDE 本体に入れません。FDE に残すのは、contact を `packet -> identity / consent -> data boundary -> evidence -> closure` に戻す安全契約です。

詳細は [ai-contact-safety-contract.md](ai-contact-safety-contract.md) と [decisions/ADR-0003-ai-contact-safety-contract.md](decisions/ADR-0003-ai-contact-safety-contract.md) を見てください。

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

## レビューする時の順番

Product Design / Creative Production の観点で見る時は、先に全体導線を確認してから個別 file に降ります。

| 順 | 見るもの | 確認すること |
|---:|---|---|
| 1 | [visual.html](visual.html) | 初見でFDEの目的、使い方、停止線が分かるか |
| 2 | [ROADMAP.md](ROADMAP.md) | `goal / evidence / gate / owner / done_when` が崩れていないか |
| 3 | [OPERATIONAL_GUARANTEE.md](OPERATIONAL_GUARANTEE.md) / [MVP_STATUS.md](MVP_STATUS.md) | private local complete と public approval が分かれているか |
| 4 | [PUBLIC_KERNEL_PLAN.md](PUBLIC_KERNEL_PLAN.md) / [TODO_FDE_PUBLIC_KERNEL_RIGHTS.md](TODO_FDE_PUBLIC_KERNEL_RIGHTS.md) | public-kernel、rights、patent、visibility の境界が混ざっていないか |
| 5 | [decisions/ADR-0002-product-creative-review-path.md](decisions/ADR-0002-product-creative-review-path.md) | 全体デザイン判断の採用理由と非目標が明記されているか |
| 6 | [ai-contact-safety-contract.md](ai-contact-safety-contract.md) | AI同士のcontactがFDEのidentity / consent / evidence / closureへ戻るか |

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
| [ai-development-living-harness.md](ai-development-living-harness.md) | AI開発標準カード、Living Harness、route drift stop 条件 |
| [mvp-axis-operating-card.md](mvp-axis-operating-card.md) | FDEで色々な軸のMVPを切るための13運用カード |
| [dependency-registry.md](dependency-registry.md) | FDE 外部依存、外部正本、playbook、report の registry |
| [source-pointers.md](source-pointers.md) | 元議論や source cluster への pointer |
| [search-orchestration.md](search-orchestration.md) | 検索、外部AI、browser route を薄く扱う規則 |
| [lifecycle-operating-pattern.md](lifecycle-operating-pattern.md) | capture / close / archive / reflect の共通 slot |
| [ai-contact-safety-contract.md](ai-contact-safety-contract.md) | AI同士のcontactをFDE packet / consent / evidence / closureへ戻す抽象契約 |

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
