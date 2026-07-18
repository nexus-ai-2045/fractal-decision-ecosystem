---
title: Fractal Decision Ecosystem Pattern Vocabulary
type: brain
status: active
created: 2026-05-10
updated_at: 2026-05-10T07:35:00+0900
owner: codex
related:
  - root-router.md
  - axis-registry.md
tags: [fractal-decision-ecosystem, pattern, vocabulary, alias, search]
---

# Fractal Decision Ecosystem パターン語彙

会話・local notes 検索・playbook / lesson / idea から出てくる語を、Fractal Decision Ecosystem の判断軸へ吸わせるための語彙表。

これは用語辞典ではない。**ある語が出た時に、次に見る軸・方法・検証・保存先を連鎖させるための pattern chain**。

## 使い方

```text
語が出る
-> pattern family を見る
-> primary axis に吸わせる
-> method / linked concepts / out-of-scope-but-useful を確認する
-> packet に落とす
```

最小出力:

```text
term:
pattern_family:
namespace:
scope:
out_of_scope:
abstraction_layer:
primary_axis:
method:
next_link:
target_file:
```

## pattern 語彙

## layer 語彙 guard

source: `dependency-registry:layer-vocabulary-synthesis`

FDE 内で「軸」が増えすぎる時は、次の語彙へ分解してから packet に落とす。

| 語 | FDE 内の意味 | 使ってよい場所 | 禁止する混同 |
|---|---|---|---|
| namespace | 名前空間 | FDE / CMUX / playbook / lane など、同じ語の意味が変わる境界 | 担当者、抽象度、状態 |
| scope | 今回扱う範囲 | 読む file、直す file、検証する機能、議論する範囲 | 網羅性そのもの |
| out_of_scope | 今回あえて扱わない範囲 | FDE が全部見に行くのを止める時 | 放置、忘却 |
| abstraction_layer | 抽象度 / 高さ | principle, strategy, design, operation, implementation, evidence の上下移動 | 担当領域、状態、検証量 |
| レイヤー | `abstraction_layer` の人間向け別名 | 会話上の抽象 / 具体の上下移動 | 担当領域、状態、検証量 |
| レーン | 担当領域 / owner | Main / Top、運営、開発、営業、コンテンツ、リサーチ、ラボなどの責任分界 | 抽象度、進捗状態 |
| 軸 | 分類タグ | WHO / WHAT / WHY / WHEN / WHERE / HOW / HOWMUCH / WITHWHAT への吸収 | レイヤー、レーン、深度、状態の総称 |
| スレッド | 閉じる対象の話題単位 | owner / next_move / done_when / exit_condition を持つ単位 | 無限に分裂する話題束 |
| フェーズ | 状態 / 時間帯 | input, triage, active, blocked, done, archived | レイヤー、レーン |
| 深度 | 許容された具体化レベルの候補語 | CEO 判断までは補助語としてだけ使う | レイヤーの同義語として乱用 |
| merge_with | 既存 thread / issue への合流先 | 新規話題を立てる前の重複確認 | 新規 thread を増やす免罪符 |
| exit_condition | loop を終了してよい外形条件 | Done when を実行可能な観測条件に落とす時 | 気分としての完了 |

必須 guard:

```text
thread:
namespace:
scope:
out_of_scope:
abstraction_layer:
lane:
owner:
next_move:
done_when:
exit_condition:
merge_with:
closure_rule:
```

`merge_with` は合流先がない時も `none` と書く。空欄にしない。

未決:

- `深度` を独立語として残すかは CEO 判断待ち。
- `スレッド` を `issue = 閉じる単位 / thread = issue の束` に分けるかは CEO 判断待ち。

| pattern family | 入口語 / alias | primary axis | 方法論 / 切り口 | まとまる概念 | 含まれないが応用可能な概念 | 具体例 / 次リンク |
|---|---|---|---|---|---|---|
| routing / tree | MECE, TREE, branch, first-match, reroute, park | WHY / WHEN | 条件分岐で必ずどこかへ落とす | exception priority, convergence score, stay/up/down/reroute/park | value chain, double diamond, 3x3 | `MECE -> first-match -> exception -> target` |
| protocol / packet | protocol, HTTP, packet, header, body, status, cache, trace id | HOW | 通信を封筒と中身に分ける | intent, route, owner, evidence, return_path, closure_rule | API design, event sourcing, workflow engine | `HTTP -> packet -> route/status/cache -> trace` |
| testing / verification | test, pytest, lint, smoke, unit, integration, contract, E2E, acceptance, exploratory, regression, user-layer | HOWMUCH | 検証深度を選ぶ | lint, unit, integration, contract, smoke, e2e, acceptance, exploratory, regression, evidence | QA, acceptance criteria, observability | `lint -> smoke -> evidence -> E2E or regression` |
| operational health / drift | monitoring, alerting, health check, drift, stale, broken link, SSOT drift, role drift, index drift | WHEN / WITHWHAT | 運用中に正本・参照・役割がズレていないかを見る | stale pointer, missing link, unexpected state, repeated correction, page/ticket/log | monitoring, health check, audit | `drift -> lint/status -> repair or archive` |
| shadow adoption | shadow test, Shadow OK, pilot, ironclad, 鉄板 | HOWMUCH / WHEN | 即採用後の安定確認 | 10 Shadow OK, exception packet,本番標準 | beta, canary, feature flag | `adopt-now -> use -> 10 Shadow OK -> 鉄板` |
| blocker / risk | blocker, block, Type1, emergency, collision, budget | HOWMUCH | 例外を通常処理に混ぜない | user-stop, type1-or-external, unknown, collision, freeze | incident response, risk register | `blocker -> Exception Priority -> owner` |
| lifecycle / state | state, lifecycle, input, triage, ready, active, done, archived | WHEN | 状態遷移で迷子を防ぐ | absorbed, park, discard, retake | Kanban, stage gate, release train | `input -> triage -> ready -> active -> done -> absorbed` |
| role / owner | role, owner, dispatcher, coordinator, lane, surface, port | WHO | 誰が閉じるかを見る | Strategy, Judgment Box, Technical Judge, lane owner | RACI, org design, incident commander | `role -> owner -> return_path` |
| scope / boundary | scope, boundary, range, 範囲, force_level, contract | WHERE / HOWMUCH | 触ってよい範囲を決める | file scope, lane scope, workspace, Type1, external | access control, blast radius | `scope -> safe/unsafe -> gate` |
| architecture / design | architecture, architect, design pattern, harness, layer, SSOT | HOW | 構造・境界・依存を見分ける | component, dependency, state, failure mode, source of truth | DDD, system design, platform engineering | `architecture -> boundary -> SSOT -> test` |
| best practice diffusion | best practice, discover, compare, localize, pilot, adopt | WHEN / WITHWHAT | 外部事例をローカル運用へ翻訳する | source, comparison, localization, adoption path | benchmark, case study, maturity model | `discover -> compare -> localize -> pilot -> adopt` |
| research / library search | library search, local-notes search, local first, official first | WITHWHAT | 探す順序を固定する | repo, local notes, official docs, OSS, web | semantic search, graph search, RAG | `local first -> official first -> cross-check` |
| route mode / budget | route_mode, fast_reply, balanced, parallel_deep, background_watch, quick answer, token, cost, time budget | HOWMUCH / WHEN | 速度・確度・コストで route を選ぶ | fast_reply, balanced, parallel_deep, background_watch, budget | service level, QoS, triage class | `route_mode -> budget -> delegate or answer` |
| unknown location / source routing | where is it, どこにある, missing source, pointer missing, SSOT missing | WHERE / WITHWHAT | 探索先と戻し先を決める | local index, registry, pointer, Gemini, explorer, web, absorb | information retrieval, routing table | `unknown_location -> local index -> Gemini/explorer -> registry update` |
| trend / frontier intake | trend, GitHub trending, X, news, YouTube, OSS | WITHWHAT | 旬を取り込むが即事実化しない | watch, digest, candidate, smoke | market sensing, weak signal, horizon scanning | `trend -> candidate -> local smoke` |
| playbook | playbook, runbook, SOP, 手順 | HOW / WHEN | 再利用可能な手順にする | trigger, steps, evidence, failure mode | skill, checklist, template | `playbook -> trigger -> steps -> evidence` |
| lesson | lesson, 学び, failure, guard, recurrence | WHEN / HOWMUCH | 失敗・成功を次回の発動条件へ圧縮する | cause, trigger, guard, regression | postmortem, retrospective | `lesson -> trigger -> guard -> playbook/rule` |
| idea / backlog | idea, improvement, RICE, queue, park | WHY / WHEN | 候補を収束スコアへ落とす | reach, impact, confidence, effort, adopt-now | opportunity scoring, roadmap | `idea -> RICE -> adopt/park/decision/discard` |
| abstraction / concrete | abstract, concrete, 中小, 具体, example, case | WHY / HOW | 抽象と具体を往復する | 3 examples, 3 layers, 3 views, grounding | ladder of abstraction, case method | `abstract -> 具体例3つ -> axis` |
| content / communication | 本人の一言, 違和感, 判断, 事実補足, AI整形 | WHAT / WHY | 発信者と整形者を分ける | original voice, fact, edit, publish-readiness | editorial process, narrative design | `本人の一言 -> 事実 -> AI整形` |
| storage / SSOT | SSOT, pointer, target_file, cache, decision, report | WHERE | 保存先で意味を固定する | brain, decisions, reports, handoffs, inbox, ideas | knowledge graph, archive policy | `term -> target_file -> pointer` |
| trace / evidence | evidence, source, log, line, trace, fact, unknown | WITHWHAT | 事実性を支える | source path, log, test result, screenshot, [事実] | audit trail, provenance | `claim -> evidence -> confidence` |

## method chain

### 検証系

```text
test -> L0 lint / L1 unit / L2 integration-contract / L3 smoke / L4 e2e / L5 regression / L6 acceptance -> evidence
shadow test -> Shadow OK x10 -> 本番標準 / 鉄板
blocker -> Exception Priority -> owner / gate / reroute
drift -> lint/status/health-check -> repair / archive
route_mode -> budget -> fast_reply / balanced / parallel_deep / background_watch -> return_to
unknown_location -> registry/data-index/playbook -> local rg max3 -> Gemini/explorer/search -> source path -> registry/pointer update
```

### 検索系

```text
library search -> local first -> official first -> OSS / web -> cross-check
trend -> candidate -> localize -> smoke -> adopt / park
local-notes search -> related note -> alias term -> axis -> packet
```

### 設計系

```text
architecture -> boundary -> state -> failure mode -> SSOT -> test
design pattern -> local meaning -> owner -> playbook
scope -> blast radius -> Type1 / normal -> gate
```

### 判断系

```text
idea -> RICE -> convergence score -> adopt-now / park-retake / decision-needed / discard
MECE -> first-match -> exception priority -> target
3 views x 3 layers -> solved or 3x3-exhausted
```

### コンテンツ系

```text
本人の一言 -> その時の事実 -> AI整形 -> publish / park
AI作文っぽい -> original voice missing -> content lane rule
```

## search seed

local notes / vault 検索で関連語を広げる時の seed。

```text
protocol HTTP packet route status cache trace id
lint smoke unit integration contract acceptance exploratory shadow Shadow OK E2E pytest blocker evidence drift monitoring health-check
MECE TREE RICE first-match exception branch
playbook lesson idea trigger guard skill
state lifecycle input triage active blocked done archived
role owner dispatcher coordinator lane surface port
architecture design pattern harness layer SSOT
library search local first official first OSS trend cross-check best practice route_mode fast_reply balanced parallel_deep background_watch budget unknown_location
scope boundary force_level contract Type1
abstract concrete 中小 具体 3x3 3視点 3レイヤー
```

## entry protocol

Provenance: Claude proposal 由来。採用履歴は source history に残し、入口別固定 chain の意味だけをここで扱う。

入口語が出た瞬間に固定の chain へ落とす。chain が 5 本超えたら `dependency-registry:brain-chains` に分離。

| 入口 | 入口語 | chain | 主軸 | 空振り時 | version |
|---|---|---|---|---|---|
| 新アイディア発見 | idea, 思いついた, 提案 | 再帰検索 v1 (= local-notes search → 関連 → axis → packet) | WITHWHAT | decision-needed | v1 stable |
| AI 回答前の事実確認 | 事実?, source?, 不明 | 検索 chain 流用 | WITHWHAT | 不明として明示 | v1 stable |
| 実装 | 作って, 実装, 直して | core packet -> scope/risk -> TDD or smoke -> diff/test -> FDE absorb | HOW | reroute / escalate | v1 stable |
| review | レビュー, 評価, 反論 | 4 AI review packet | WITHWHAT / WHY | unknown | v1 stable |
| 詰まり | blocked, stale, 詰まった | Exception Priority | HOWMUCH | escalate | v1 stable |
| session 跨ぎ復帰 | session-snapshot, 再開 | restart-protocol | WHEN / WHO | last-status read | v1 stable |
| 公開判断 | 公開していい?, GO? | content lane rule | WHAT / WHY | Type1 / CEO | v1 stable |

入口競合: 文中で先に出現した入口を採用 (first-match)。

## 配置ルール

- 語彙・alias・連想 chain はこの file に足す。
- 軸の定義そのものは `axis-registry.md` に置く。
- root router の判断規則は `root-router.md` に置く。
- 元議論の証跡は `source-pointers.md` に置く。
- 外部AI / browser AI review の raw / report / route は `external-references.md` から辿る。

