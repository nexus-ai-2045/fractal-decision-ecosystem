---
title: FDE filtered Claude ops best-practice inventory
type: report
status: active
created: 2026-05-12
owner: foundation
tags: [fde, claude-ops, best-practice]
---

# FDE filter 済み Claude ops best-practice inventory（運用ベストプラクティス）

作成日: 2026-05-12
目的: 外部ベスプラ / GitHub 実例 / ローカル調査 / 既存 `.claude` ルールを、FDE で採用判定する。

## FDE filter

[事実: `root-router.md`] FDE は root router / King of SSOT。単なる tree ではなく、判断・経路・状態・保存先を決める ecosystem。

[事実: `dependency-registry:multi-ai-design`] 現行の上位 6 概念は、直列化 / 構造的不可能 / ライフサイクル / ビュー分離 / 出自追跡 / 人間最終判断。

この inventory では、各 best practice を次の 6 軸で判定する。

| FDE 軸 | 採用判断 |
|---|---|
| 直列化 | 状態更新・正本更新・commit が単一経路に寄るか |
| 構造的不可能 | ルール文ではなく hook / harness / permission で防げるか |
| ライフサイクル | proposed → testing → adopted / rejected / archive があるか |
| ビュー分離 | 人間用 report と machine source を分けるか |
| 出自追跡 | source / diff / log / generated_by / timestamp が残るか |
| 人間最終判断 | AI が案を出し、人間が意味変更を承認する形か |

## 採用必須

| practice | source | FDE 理由 | 採用先 |
|---|---|---|---|
| dependency-registry:project-claude は短く具体的に、重い手順は rules / skills へ逃がす | Claude Code Docs memory / best practices | ビュー分離 + context 節約 | dependency-registry:project-claude / `dependency-registry:project-docs` |
| 検証可能な success criteria を先に置く | Claude Code Docs best practices | Verification / 出自追跡 | dependency-registry:project-claude / implementation layer |
| Explore → Plan → Implement → Commit | Claude Code Docs best practices | ライフサイクル + 直列化 | Cloud ops plan |
| hooks は zero-exception enforcement に使う | Claude Code Docs hooks | 構造的不可能 | hooks plan |
| hook enforcement は `exit 2` / JSON decision を正しく使う | Claude Code Docs hooks | 構造的不可能 | hook harness |
| hook は safe env で十分 test してから production | Claude Code Docs hooks | Verification + ライフサイクル | hook stage gate |
| `settings.json` precedence / managed / project / local を区別 | Claude Code Docs settings | SSOT drift 防止 | settings inventory |
| TDD skill を実装時 default にする | local `skills/test-driven-development` + Fowler/Beck | Verification + Incremental | implementation layer |
| bug fix は failing regression test から | local TDD skill | Detect + Verification | implementation layer |
| dependency-registry:project-claude / rules / docs / hooks の自己編集は Type1相当 | local blind-spots / invariants | 人間最終判断 + 出自追跡 | safety |
| `CONTROL-PLANE.md` と `settings.json` の hook graph を harness で確認 | local hooks | 直列化 + 構造的不可能 | hook inventory |
| config / hook / skill 変更は diff / staged path / rollback path を残す | 今回の事故 + Codex/CLOUD logs | 出自追跡 | commit gate |
| browser-to-api: 認証なし read-only site の API を CDP capture (`browse network on` 併用) → OpenAPI 3.1 + client.mjs 自動生成。受託の API 連携 / スクレイピング案件の初動調査を時短 | Lab PoC #1 (jsonplaceholder) + PoC #3 (PokeAPI 2026-05-22) / operator-local playbook | 出自追跡 (RESULT に command / event count / 生成物) + ライフサイクル (Lab PoC → playbook → adopted) + 人間最終判断 (CEO 2026-05-22 GO) | `dependency-registry:playbooks`（operator-local-adapter） |

> [採用境界 / browser-to-api] 認証なし・読み取り専用・利用規約クリアの site 限定。authenticated / production / 外部書込 = Type1 (案件ごと個別 gate)。single-sample は confidence low のため、実運用は複数 sample で精度を上げる。response body schema は `browse network on` 併用時のみ取得可 (PoC #3 で実証 / 未使用時は本文なし)。

## 採用候補

| practice | source | FDE 判定 | 次アクション |
|---|---|---|---|
| dependency-registry:project-claude 500-1500 tokens / 200 lines 未満 | Claude Docs / local optimization guide | 採用。ただし 6大原則は削らない | draft に line budget を入れる |
| global hooks は少数に抑える | local `claude-code-optimization-guide.md` | 採用候補。現行 hooks が多いので inventory 必須 | live / auxiliary / archive 分類 |
| HTML comment は人間向け note に使う | Claude Docs / local guide | 採用候補。人間用 meta を token から外す | dependency-registry:project-claude draft で検討 |
| skills は on-demand workflow | Claude Docs / writing-skills docs | 採用 | skills inventory |
| subagents は heavy read / isolated review に使う | Claude Docs / local agent-selection | 採用。ただし通常 CC と EA/COS を混ぜない | `agent-selection` drift check |
| GitHub 実例の `Commands / Testing / Architecture / Harness` 前方配置 | GitHub examples | project dependency-registry:project-claude には採用。global には薄く | Projects 側へ反映 |
| harness-first / agent harness 比較 | local research digest 2026-05-07/10 | 採用候補。ベンチ数値は park | cmux / Cloud ops comparison |

## 保留または注意

| practice | 理由 |
|---|---|
| GitHub trending repo の丸ごと採用 | FDE の SSOT / 出自追跡を通さないと drift する |
| 「Hooks で全部強制」 | hook 過多は context / latency / false positive / bypass の原因 |
| dependency-registry:project-claude 10-section template の丸写し | global には重い。project には一部有効 |
| benchmark / harness 優勝 claims | local digest で cheating / harness bias 留保あり。open harness / reproduction を確認するまで採用しない |
| 自動 memory に判断を任せる | dependency-registry:project-claude / auto memory は context であり enforcement ではない |

## ローカルで抜かしてはいけない既存ロジック

[事実: `root-router.md`] 判断の入口は FDE。迷ったら新規入口を増やさずここへ戻す。

[事実: `dependency-registry:multi-ai-design`] Codex は補助 AI ではなく、実装 dispatch と軽い drift 修復を担う orchestrator。

[事実: `dependency-registry:source-routing-budget`] ベスプラ / 実装方針は existing code / shared wrapper / tests → local GitHub checkout → SSOT → 公式の順で確認する。

[事実: `dependency-registry:claude-meta-rules`] 原則を追加・変更する時は `Principle / Invariant / Detector / Repair Path / Evidence` に落とす。

[事実: `dependency-registry:claude-invariants`] dependency-registry:project-claude は人間承認なしに変更されない、という invariant がある。

[事実: `dependency-registry:claude-control-plane`] hooks の実体 SSOT は `settings.json`、設計・I/O・archive 状態は CONTROL-PLANE にまとまる。

[事実: `dependency-registry:claude-testing-rule`] TDD / デグレ防止 / 完了前検証 / 非コード成果物検証は既存 live rule。

[事実: `dependency-registry:claude-tdd-skill`] TDD は skill として存在し、実装時に使うべき callable workflow。

## Cloud ops refactor への追加要件

1. best practice を見つけたら、採用前に FDE 6軸へ通す。
2. FDE で `採用必須 / 採用候補 / 保留 / 捨てる` を分ける。
3. 採用必須だけ dependency-registry:project-claude / rules / hooks / skills に反映する。
4. 採用候補は `ops-best-practice-inventory.md` / operator-local reports に留め、Cloud live へ直接入れない。
5. hook / harness 系は、local invariant test が先。外部 trend は後。

## 参照

- `root-router.md`
- `dependency-registry:multi-ai-design`
- `dependency-registry:source-routing-budget`
- `dependency-registry:claude-optimization-guide`
- `dependency-registry:claude-meta-rules`
- `dependency-registry:claude-invariants`
- `dependency-registry:claude-control-plane`
- `dependency-registry:claude-testing-rule`
- `dependency-registry:claude-tdd-skill`
- Claude Code Docs: official Claude Code docs imported source
- Claude Code memory docs: official Claude Code docs imported source
- Claude Code hooks docs: official Claude Code docs imported source
- Claude Code settings docs: official Claude Code docs imported source

