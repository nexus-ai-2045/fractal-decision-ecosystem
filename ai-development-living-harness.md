---
title: AI開発標準カードとLiving Harness
type: brain
status: active
created: 2026-06-21
owner: codex
scope: ai-development-living-harness
tags: [ai-development, living-harness, fde, pdca, ssot]
related:
  - operating-card.md
  - dialogue-protocol.md
  - axis-registry.md
  - brain-concept-rollup.md
---

# AI開発標準カードとLiving Harness

obsidian_check: checked
scope_route: fde-ssot / ai-development-process / no-external-action

この file は、AI と人間が共同で開発する時の標準カードを、Fractal Decision Ecosystem（FDE）側の SSOT として置く。

目的は、原則を固定しつつ、実装ハーネスや検査コマンドは環境に合わせて更新できる状態を保つこと。

## 1. 正本版カード

新しい開発単位を始める前に、次を 1 枚で切る。

| 項目 | 書くこと |
|---|---|
| 目的 | 何のためにやるか。ユーザー価値を 1 行で書く |
| 主ユーザー行動 | ユーザーが実際に行う中心行動 |
| 主経路 | 最初に通す通常経路。迷ったらここへ戻る |
| 保存単位 | 何をどこへ保存し、何を保存しないか |
| 最小E2E | 最初に通す end-to-end の 1 本 |
| やらないこと | 今回の scope から外すもの |
| fallback | 主経路が失敗した時の代替経路 |
| 公開/個人情報境界 | public に出せる情報と出せない情報 |
| 完了条件 | 何をもって done と言えるか |
| ズレ検知条件 | route drift を検知する条件 |
| owner | 判断、実装、検証、公開の責任者 |
| 検証証跡 | test、smoke、log、PR、スクリーンショットなど |
| ADR化する判断 | 長期ルールに昇格する判断 |
| 未確認 | まだ断定できないこと |
| 人間ゲート | 人間の明示判断が必要な操作 |
| 次の一手 | この turn で進める 1 件 |

## 2. 軽量版カード

小さい変更や壁打ちは、次だけでよい。

| 項目 | 書くこと |
|---|---|
| 目的 | 何を閉じるか |
| 主経路 | まず通す道 |
| 保存単位 | どこへ残すか |
| 最小E2E | 最小確認 |
| やらないこと | 今回は触らないもの |
| fallback | 失敗時の戻り先 |
| 公開/個人情報境界 | public/private の線 |
| 完了条件 | done の条件 |
| ズレ検知条件 | 遠回りを検知する条件 |
| owner | 責任者 |
| 検証証跡 | 証跡 |
| ADR化する判断 | 残す判断 |
| 次の一手 | すぐやる 1 件 |

## 3. 開発プロセス

既定の流れは次にする。

```text
Design
-> smoke & preflight
-> blocker 前提の research & design completion
-> TDD
-> human gate
-> implementation & orchestration
-> verification & tests
-> PR & human gate
-> PR push
-> merge
-> post-merge verification
```

省略できるのは、低リスクで reversible な範囲だけ。Type1、公開、外部送信、auth、secret、production、settings、hook、SSOT 変更は省略しない。

## 4. Living Harness

Living Harness は「原則を固定し、満たし方を更新する」ための運用名。

| 層 | 固定するもの | 更新してよいもの |
|---|---|---|
| 原則 | SSOT、PDCA、検証、Type1、人間ゲート、Incremental Change | 表現、例、手順名 |
| ハーネス | drift 検知、preflight、smoke、gate、trace | 実装言語、コマンド、timeout、CI |
| テンプレ | 開発カード、PR本文、handoff、ADR | 項目順、詳細度、repo別の型 |
| 運用 | route failure を学習し、次回の検知へ戻すこと | どの repo / tool へ吸収するか |

Living Harness は、毎回同じ手順を手で守るためではない。再発したズレを検知条件、テンプレ、テスト、hook、smoke のどこかへ吸収して、次回の遠回りを減らすために使う。

## 5. Brain / FDE / world / harness の役割

| 置き場 | 役割 |
|---|---|
| inbox / report | 素材、観測、棚卸し、未整理ログ |
| brain | 概念、定義、比喩、原則候補を一度こねる場所 |
| pattern / playbook | 2 回以上使えそうな型 |
| decisions / ADR | 採用判断 |
| FDE pointer | 複数入口から使う routing / packet / closure 抽象 |
| world | 過去対話、決定、経験の長期吸収 |
| harness | 3 回以上再発するズレの自動検知、停止、誘導 |

Brain でこねるが、Brain に溜め込まない。採用、保留、破棄、FDE昇格、harness化の出口を必ず持つ。

## 6. route drift stop 条件

次の条件が出たら、実装を続けずに route を切り直す。

- 主目的より取得経路や adapter 比較が中心になっている。
- public / private / personal の境界が曖昧なまま PR に進みそう。
- repo が違う、branch が違う、PR base が違う可能性がある。
- 最小E2Eがまだないのに周辺機能が増えている。
- SSOT がない、または同じ判断が複数 file に分散している。
- user が「ズレている」「遠回り」「ごっちゃ」と指摘した。
- route failure を反省だけで閉じ、検知条件へ戻していない。

## 7. 完了条件

このカードを使った作業は、次を満たした時に done と言える。

- 目的、主経路、保存単位、やらないことが 1 枚で読める。
- 最小E2Eまたは smoke が通っている。
- public/private 境界が明示されている。
- PR / commit / report が 1 意味単位に分かれている。
- 未確認と人間ゲートが残っていれば、done ではなく hold として返している。
