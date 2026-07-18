---
title: Fractal Decision Ecosystem Axis Registry
type: brain
status: active
created: 2026-05-10
updated_at: 2026-05-13T00:00:00+0900
owner: codex
promote_at: 2026-05-13
promote_source: kusanagi D-10 / CEO GO 2026-05-10
promote_evidence: this repositoryCC/_workspace/wave1-C-related-discussion-absorb.md §axis 9 expansion 件の確定状態
related:
  - root-router.md
  - pattern-vocabulary.md
tags: [layer-context, axis, registry, routing]
shadow:
  active: false
  topic: 8-axis MECE refactor (6W2H base)
  start_at: 2026-05-10T07:05:00+0900
  promoted_at: 2026-05-13
  promoted_by: codex
---

# Fractal Decision Ecosystem 軸レジストリ

`root-router.md` の詳細軸レジストリ。root router は軽く保ち、軸の定義はここで見る。

会話・検索・playbook / lesson / idea に出る語をどの軸へ吸わせるかは `fde/pattern-vocabulary.md` を見る。

## 8-axis MECE

Provenance: shadow から本体へ昇格済み。日時と source は frontmatter の `promote_at` / `promote_source` / `promote_evidence` に残す。

旧 15 軸の重複を 8 primary axis に統合。FDECC 精査で、正本側に未反映だった promote 状態だけを薄く戻した。

### 8 primary axis (6W2H base)

| # | axis | 何を見るか | 旧 15 軸の吸収先 |
|---|---|---|---|
| 1 | `WHO`      | 役割・責務・owner | role |
| 2 | `WHAT`     | 出力・artifact・lane Outcome | content (subset) |
| 3 | `WHY`      | 意味・動機・収束判断 | decision |
| 4 | `WHEN`     | 状態・lifecycle・triage・拡散段階 | lifecycle / best-practice diffusion |
| 5 | `WHERE`    | 物理 (workspace) + 論理 (storage) | storage + **workspace (新規)** |
| 6 | `HOW`      | 手段（実装深度・構造・pattern・契約・通信）| programming / architecture / design-pattern / protocol / communication |
| 7 | `HOWMUCH`  | 安全度・検証深度・risk・cost・score | risk / testing |
| 8 | `WITHWHAT` | 根拠・veracity・source・research intake | research / search-practice + **fact (新規)** |

### packet 標準

```
packet_id:
intent:
mode:           # search | implement | review | operate | ideate | decide  (= Work Mode Gate)
who:
what:
why:
when:
where:          # workspace + storage 併記可
how:
howmuch:
withwhat:       # evidence / fact tag [事実|推測|不明] / search_depth: L1|L2|L3
closure_rule:   # mode 別の完了条件 (= Closure Rule 表参照)
```

最小 5 行 packet は `who / what / why / when / where` で足る。`how / howmuch / withwhat` は深掘り時のみ。
`mode` と `closure_rule` は **作業開始時に必須**。`mode_unknown` の場合は作業を進めず返す。

### MECE 性チェック

| ペア | 重複なし |
|---|---|
| WHO vs WHERE | ✓ 主体 vs 場所 |
| WHAT vs HOW | ✓ 成果 vs 手段 |
| WHY vs WHEN | ✓ 動機 vs 状態 |
| WITHWHAT vs HOWMUCH | ✓ 根拠 vs 安全度 |
| WHERE physical vs WHERE logical | ⚠ 同軸内 sub 分割（workspace vs storage）|

### 作業モードゲート

Provenance: GPT-5.5 P0 review 由来。採用履歴は source history に残す。

AI は作業開始時に、まず現在の mode を 1 つ選ぶ。

```
- search    : 調べる / 探す / 既存確認
- implement : 作る / 直す / 実装する
- review    : 評価する / 反証する / 判断する
- operate   : 状態を流す / lane に戻す / handoff する
- ideate    : 壁打ち / アイデア出し / 抽象化する
- decide    : 採用 / 保留 / 棄却 / Type1 判断
```

mode が決まってから 8-axis map に落とす。mode が不明な場合は、作業を進めず `mode_unknown` として返す。

### 閉じ方ルール

Provenance: GPT-5.5 P0 review 由来。採用履歴は source history に残す。

AI は作業開始時に、完了条件を 1 つ持つ。closure がない作業は開始しない。

| mode | closure |
|---|---|
| search    | 検索結果 / blocker / unknown / candidate list のどれかを返す |
| implement | diff / file path / test result / unresolved issue を返す |
| review    | adopt / revise / reject / unknown を返す |
| operate   | owner / next_state / target_file / return_path を返す |
| ideate    | idea / task / decision / lab-trial / park のどれかに落とす |
| decide    | adopt / park / discard / lab-trial / decision-needed を返す |

### 対応づけ前に新規面を作らない

Provenance: GPT-5.5 P0 review 由来。採用履歴は source history に残す。

AI は、新しい file / rule / SSOT / workflow / axis / layer を作る前に、必ず既存 map 上の置き場所を探す。

新規作成できるのは以下の場合のみ。

1. 既存の WHERE に置けない
2. 既存の HOW で扱えない
3. 既存の WITHWHAT で再利用元が見つからない
4. 作らない場合の損失が明確
5. owner / target_file / closure_rule がある

上記を満たさない新規作成は、`new_surface_blocked` とする。

### Shadow OK リセットルール

Provenance: Grok review 由来。採用履歴は source history に残す。

例外発生時は **Shadow OK カウンタを 0 に reset** し、例外 packet を本 file の §不整合・気づき log に追記する。
（10 Shadow OK で鉄板化したルールも、例外 1 件で再カウントから始める）

### 不整合・気づき log

- 8-axis MECE shadow promote 実施済み。日時と source は frontmatter の provenance fields に残す。

---

## 役割 / 別名

| alias | general role | 使い方 |
|---|---|---|
| Main / Top (旧: 草薙) | Strategy / Meaning / HITL direction | 意味・違和感・方向・問いづくり |
| Coord / 運営 | Coordinator / Dispatcher / Process Manager | owner / route / stale / return_path |
| Codex 5.5 | Technical Judge / Architect Review | 技術判断・SSOT・test・scope review |
| Foundation | Harness / Platform / Reliability | shared wrapper / gate / trace / DB / capability port |
| Sales | Revenue / Deal Pipeline | 案件・提案・受注・売上 |
| Content | Publishing / Trust Asset | 発信・信用・公開資産 |
| Research | Frontier Intake | 外部情報・best practice・一次情報 |
| Lab | Experiment / PoC | 小さく試す・壊して判断 |

呼称ルール:
- 現行の上位判断レイヤーは `Main / Top` と呼ぶ。
- `草薙` は既存 lane 名・過去 decision・互換 alias として残す。
- 新規 packet / role 表では、意味判断の戻り先を `Main / Top` と書き、必要な時だけ `dependency-registry:kusanagi-role` を参照する。

## アーカイブ: 旧15軸

> **archived 2026-05-13**: 8-axis MECE shadow を本採用。履歴保全のため残置するが、新規分類は §8-axis MECE と §Programming Axis 以降の詳細テーブルを使う。

| axis | 何を見るか | 主な問い | 収束先 |
|---|---|---|---|
| `role axis` | 誰の責務か | Strategy / Judgment Box / Coordinator / Technical Judge / lane のどれか | owner / next_action |
| `programming axis` | 技術深度 | 技術判断 / 実装設計 / コード変更 / 検証 / 運用反映のどれか | P0-P4 |
| `architecture axis` | 構造設計 | component / boundary / dependency / state / failure mode は何か | architecture note / Technical Judge |
| `design-pattern axis` | 既存 pattern への対応 | orchestrator / dispatcher / harness / guardrail / tracing / eval / HITL のどれか | pattern mapping |
| `protocol axis` | 手順・契約 | 入出力 schema / ACK / DONE / retry / timeout / freeze / stop 条件は何か | protocol / playbook |
| `communication axis` | 通信・手紙 | sender / receiver / intent / force_level / reply_mode / return_path は何か | message packet |
| `storage axis` | 保存・SSOT | brain / decision / report / handoff / task / lane status / idea のどこか | target_file |
| `lifecycle axis` | 状態遷移 | input / triage / ready / active / blocked / done / archived のどこか | lifecycle state |
| `testing axis` | 検証深度 | lint / unit / property-based / integration / contract / snapshot / smoke / e2e / acceptance / exploratory / user-layer / regression のどれか | test evidence |
| `operations health axis` | 運用劣化 | monitoring / alerting / health check / drift / stale / broken link / missing registry key / role drift のどれか | page / ticket / log / repair / archive / registry update |
| `route-mode axis` | 速度・確度・コスト | fast_reply / balanced / parallel_deep / background_watch のどれか | route_mode / budget |
| `research axis` | 外部情報 | library search / official docs / trend / OSS / web / YouTube のどれか | research intake |
| `search-practice axis` | 探し方 | local first / official first / primary source / trend watch / cross-check のどれか | search plan |
| `best-practice diffusion axis` | 広げ方 | discover / compare / localize / pilot / adopt / broadcast のどこか | adoption path |
| `decision axis` | 収束判断 | adopt-now / park-retake / decision-needed / discard のどれか | convergence bucket |
| `risk axis` | 例外・安全 | Type1 / unknown / collision / budget / emergency / user-stop はあるか | exception branch |
| `content axis` | 発信素材 | 本人の一言 / 事実補足 / AI整形の順か | Content rule |

通常は primary axis 1 つで足りる。3 視点 x 3 レイヤーまで見ても閉じない時だけ `3x3-exhausted` にする。

## プログラミング軸

| depth | name | 条件 | owner |
|---|---|---|---|
| P0 | 技術判断 | 実装方針 / architecture / SSOT / scope / risk を決める | Technical Judge / Codex 5.5 |
| P1 | 実装設計 | どの file / module / test を触るか決める | Foundation / lane owner |
| P2 | コード変更 | patch / refactor / script / wrapper を書く | implementation lane / worker |
| P3 | 検証 | test / build / smoke / diff / log で確認する | implementer + reviewer |
| P4 | 運用反映 | current-status / decisions / queue / release note に吸収する | Coord / lane owner |

P0 と P4 は同じ人が抱えすぎない。P0 は技術判断、P4 は運用吸収として分ける。

## 通信 packet 軸

通信・手紙は、本文の良し悪しより封筒を先に見る。

```text
from:
to:
intent:
force_level:
reply_mode:
return_path:
evidence:
closure_rule:
```

## 構造 / pattern 軸

| pattern | local meaning |
|---|---|
| `orchestrator` | 全体を分解し、他 agent / lane を動かす。ただし全権にしない |
| `dispatcher` | intent を owner へ配る |
| `process manager` | stale / retry / return_path / completion を管理する |
| `harness` | session / context / gate / wrapper / trace の受け皿 |
| `guardrail` | 入出力前後の禁止線 / validation |
| `tracing` | 何が起きたかを追える evidence |
| `eval` | 出力品質 / 判断材料の評価 |
| `HITL` | 人間承認 / Type1 / 不可逆判断 |
| `swarm worker` | specialist lane が成果物を返す |

pattern に寄せても owner が決まらない場合は `role axis` に戻す。

## 保存 / SSOT 軸

| 性質 | 保存先 |
|---|---|
| 判断ルール / durable invariant | `core.md` / `operating-card.md` / `dependency-registry:brain-general`（withheld） |
| 個別 lane の決定 | `decisions/` / `dependency-registry:lane-decisions`（operator-local-adapter） |
| 現在地 / 次 action | operator-local adapter (`lane-status` / `todo`)、または本 repo の active docs |
| 調査・監査・実測 | `ops-best-practice-inventory.md` / operator-local reports |
| 引き継ぎ契約 | `dependency-registry:handoff-index`（operator-local-adapter） |
| 判断待ち / 通信 packet | `external-ai-file-review-packet.md` / operator-local inbox |
| idea / 改善案 | `dependency-registry:ideas`（operator-local-adapter） / `ROADMAP.md` |
| 手順 | `operating-card.md` / operator-local playbooks |
| SSOT 管理層 (registry / loader / lint) | `dependency-registry.md` + operator-local SSOT adapter |
| placement / 種別判断 / 構造分離 | `dependency-registry.md` capability keys（operator-local-adapter） |

## lifecycle / triage 軸

| state | 意味 | 次 |
|---|---|---|
| `input` | 入ってきたばかり / 未分類 | triage |
| `triage` | 分類中 / owner・価値・保存先を判定中 | ready / park / discard / decision-needed |
| `ready` | 着手条件が揃った | active |
| `active` | いま動かす | done / blocked / park |
| `blocked` | owner / Type1 / external / missing evidence で止まった | escalate / self_resolve |
| `done` | evidence つきで閉じた | absorbed / archived |
| `absorbed` | current-status / decision / task に反映済み | archived |
| `park` | 今はやらないが再開条件あり | retake |
| `discard` | 棄却 | archive / delete only if safe |
| `archived` | 履歴保存 | 通常読まない |

## test / 検証軸

| test layer | 何を見るか | evidence |
|---|---|---|
| `unit` | 関数 / 小部品が正しいか | test name / pass log |
| `property-based` | 想定外入力 / 組合せで invariant が崩れないか (Hypothesis 等) | property 定義 / 反例最小化 log |
| `integration` | module / wrapper / DB / queue が繋がるか | integration test / dry-run |
| `contract` | provider-consumer の packet / schema 約束が両側で一致するか | JSON Schema / Pact / 両側 validate 結果 |
| `snapshot` | template / 出力 / packet が暗黙に変質していないか (golden master 含む) | baseline diff / 承認済 snapshot ID |
| `smoke` | 主要動線が壊れていないか | shortest real-ish run |
| `e2e` | user 視点の端から端まで動くか | browser / CLI / workflow evidence |
| `user-layer` | CEO / 実ユーザーが迷わず使えるか | screenshot / output / 操作時間 |
| `regression` | 既知バグが戻っていないか | fixture / specific test |
| `blocker` | これが落ちると先に進めないか | BLOCKED reason / owner |

`property-based` / `contract` / `snapshot` は ADR-0140 proposed 中の pilot 語彙。運用標準へ昇格するまでは high-value script に限定して使う。

即採用した運用はその時点から使い始める。開始後に **10 回の `Shadow OK`** が出たら、安心運用を越えて本番標準 / 鉄板扱いへ上げる。例外が出た場合は回数を稼いで隠さず、例外 packet として `Exception Priority` に戻す。

## 調査 / 検索軸

| source type | 例 | 主用途 |
|---|---|---|
| `library-search` | local notes / local docs / repo grep | 既存知識の確認 |
| `official-docs` | OpenAI / Anthropic / Google / GitHub docs | 仕様・公式機能の確認 |
| `trend` | GitHub trending / X / news / community | 旬・市場変化の検知 |
| `OSS` | repo / issue / PR / release | 実装例・採用候補 |
| `web` | 一般 web / blog / article | 補助情報 |
| `YouTube-video` | YouTube / NotebookLM / transcript | 暗黙知・教育・発信素材 |
| `internal-log` | dev-log / inbox / reports | 自分たちの事実履歴 |

検索順:

1. `local first`: repo / local notes / lane status / decisions を先に見る。
2. `official first`: 技術・API・仕様は公式 docs / primary source を優先する。
3. `existing implementation`: 既存 script / shared lib / package / OSS 実装を探す。
4. `external comparison`: 足りない時だけ web / trend / community を見る。
5. `cross-check`: 重要判断は 2-3 source で照合する。

## best practice 拡散軸

| state | 意味 | 次 |
|---|---|---|
| `discover` | 見つけた | compare |
| `compare` | local 既存と比較 | localize / discard |
| `localize` | Projects の文脈に翻訳 | pilot |
| `pilot` | 小さく試す | adopt / park / discard |
| `adopt` | rule / playbook / script / test に吸収 | broadcast / status update |
| `broadcast` | 関係 lane に pointer で周知 | absorbed |
| `watch` | 今は採用せず観測 | retake |
| `discard` | 不採用 | reason 1 line |

広げ方の原則: 全 lane broadcast から始めない。1 lane / 1 script / 1 playbook で pilot し、adopt 後も pointer で広げる。

