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

**無限に発散してしまいがちなAIの仕事を「根拠のある判断」と「閉じた改善ループ」に変える。**

FDEは、AI作業の目標、根拠、実装、検証、停止線、学習先をひとつの流れに戻す判断制御面です。個別のAIアプリではなく、完了・未保証・人間承認待ちを混ぜずに閉じるための運用パッケージです。

## 目的

AIができるはずの判断・検証・停止・学習が、実運用で毎回発火しない問題を解きます。

- 事実 / 推測 / 不明を分け、根拠のある判断に戻す
- 実装と検証の残務を、公開承認と混ぜずに閉じる
- 失敗を反省文で終わらせず、`route / skill / gate / test / ssot / roadmap` へ戻す

詳細な概念説明は [docs/fde-concept-guide.md](docs/fde-concept-guide.md)、層と図は [SYSTEM_OVERVIEW.md](SYSTEM_OVERVIEW.md) を見てください。

## できること

| できる | 自動では行わない |
|---|---|
| 問い・owner・mode・完了条件を packet 化する | 公開・外部送信・visibility変更を承認する |
| ローカル gate / pytest / closeout で検証する | CIやbot成功を人間レビュー済みとみなす |
| feedback packet で実装runtimeから学びを受ける | adopt を packet 内自己申告だけで許可する |
| 二本線（Decision Experience / Autonomous Execution）を契約する | runtime の無人 merge / release を保証する |

| 役割 | FDEがそろえるもの | 主な証拠 |
|---|---|---|
| 判断 | 問い、owner、mode、完了条件 | packet / evidence / decision |
| 開発 | 既存資産確認、実装、検証層 | diff / pytest / smoke / gate |
| 運用 | 残務、remote CI、closeout | receipt / operational guarantee |
| 改善 | 失敗を仕組みへ戻す | regression test / updated SSOT |

## クイックスタート

必要なものは Python 3、git、PowerShell（Windows）または同等の shell です。

```powershell
git clone https://github.com/nexus-ai-2045/fractal-decision-ecosystem.git
cd fractal-decision-ecosystem
pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_mvp_gate.ps1 --json
```

| 目的 | 入口 |
|---|---|
| 全体像 | [visual.html](visual.html) / [SYSTEM_OVERVIEW.md](SYSTEM_OVERVIEW.md) |
| レビュー順 | [ROADMAP.md](ROADMAP.md) → [OPERATIONAL_GUARANTEE.md](OPERATIONAL_GUARANTEE.md) |
| 公開境界 | [PUBLIC_READY.md](PUBLIC_READY.md) / [PREFLIGHT.md](PREFLIGHT.md) |
| 概念の詳細 | [docs/fde-concept-guide.md](docs/fde-concept-guide.md) |
| feedback 契約 | [docs/feedback-loop-packet.md](docs/feedback-loop-packet.md) |

## 中核ループ

```text
Goal -> Evidence -> Decision -> Verify -> Closure
  ^                                          |
  +-- route / skill / gate / test / SSOT / roadmap
```

外側の workflow は machine-readable な [fde_workflow.yaml](fde_workflow.yaml) が正本です。

```text
goal_and_boundary -> capability_inventory -> roadmap -> preflight
-> implement -> verify -> operational_guarantee -> feedback
-> system_update -> goal_and_boundary
```

実装runtimeから学びを戻す時は [`fde.feedback.v1`](docs/feedback-loop-packet.md) を使います。Autonomous Execution の intake は `return_path.schema=fde.feedback.v1` を必須とし、`autonomy_enforcement` は `schema_bound` です（feedback の自動生成や auto-adopt は含みません）。

## 安全境界

FDEは公開、外部送信、GitHub visibility変更、release、mergeを自動承認しません。公開面に出る操作は、何が外から見えるかを明示し、人間レビューと現在会話での明示承認があるまで停止します。

- CIやbot checkの成功は、人間レビュー済みではありません
- `scripts/pr_review_signal_check.py` は check成功 / bot review / 人間レビュー待ちを分けます
- Autonomous Execution は `review_packet` で止まります
- secret / personal path / credential / settings / destructive は Type1 相当で停止します

公開前確認: [PUBLIC_READY.md](PUBLIC_READY.md) / [PREFLIGHT.md](PREFLIGHT.md) / [SECURITY.md](SECURITY.md)

## まず読むもの

| 順 | file | 役割 |
|---:|---|---|
| 1 | [operating-card.md](operating-card.md) | 毎 turn の最小起動 |
| 2 | [dialogue-protocol.md](dialogue-protocol.md) | 対話ルールと fact tag |
| 3 | [axis-registry.md](axis-registry.md) | 8-axis と closure rule |
| 4 | [core.md](core.md) | packet / move の薄い定義 |
| 5 | [docs/fde-concept-guide.md](docs/fde-concept-guide.md) | 概念と配置の詳細 |

## 主要 file

| file | 役割 |
|---|---|
| [fde_workflow.yaml](fde_workflow.yaml) | 閉ループの machine contract |
| [SYSTEM_OVERVIEW.md](SYSTEM_OVERVIEW.md) | 層・workflow・図の入口 |
| [ROADMAP.md](ROADMAP.md) | Now / Next / Future |
| [OPERATIONAL_GUARANTEE.md](OPERATIONAL_GUARANTEE.md) | 運用保証の現在地 |
| [docs/feedback-loop-packet.md](docs/feedback-loop-packet.md) | 実装runtimeとの feedback 契約 |
| [docs/fde-concept-guide.md](docs/fde-concept-guide.md) | 発火条件・配置・語彙の詳細 |
| [visual.html](visual.html) | 視覚ビュー |

## 言語方針

- 初出は `Fractal Decision Ecosystem（FDE）` と書き、以後は `FDE` を使います。
- 人間が読む本文、見出し、説明文は日本語で書きます。
- code identifier、schema field、file name、GitHub Actions keyword、frontmatter key は英語のまま維持します。
- 日付は provenance / lifecycle / evidence のために使い、core concept や gate 名には混ぜません。

## 貢献と検査

- 開発の入り方: [CONTRIBUTING.md](CONTRIBUTING.md)
- 見せる相手を広げる前の記録: [PREFLIGHT.md](PREFLIGHT.md)
- セキュリティ方針: [SECURITY.md](SECURITY.md)

```powershell
python -m pytest -q
python scripts/public_ready_check.py
python scripts/fde_workflow_check.py --json
```

release 前に README 設計を機械検査する場合の例（[repo-preflight](https://github.com/nexus-ai-2045/repo-preflight)）:

```powershell
python path\to\repo-preflight\scripts\readiness_scan.py --repo . --release
```
