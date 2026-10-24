---
title: FDE search orchestration
type: brain
status: active
created: 2026-05-13
owner: codex
scope: fde-search-orchestration
tags: [fde, search, orchestration, codex, claude-code]
related:
  - core.md
  - pattern-vocabulary.md
  - dependency-registry.md
  - dependency-registry:claude-code-reference
  - dependency-registry:source-routing-budget
---

# FDE 検索 orchestration

検索は Codex 本体が全部読む作業ではない。広い探索は sidecar / subagent / 外部AI に逃がし、Codex 本体は問いの切り方、採否、diff、検証、正本反映に集中する。

## 1. Official layer と local layer を混ぜない

| layer | 使う名前 | 役割 |
|---|---|---|
| official layer | Subagent / Explore / Plan / Hook / Status line / Permission / Worktree isolation | Claude Code 公式機能として存在する部品 |
| local role layer | researcher / planner / implementer / reviewer / router / log_keeper / diff_taker | Projects 内での運用役割 |
| FDE layer | namespace / scope / abstraction_layer / evidence / closure_rule | 問いを閉じるための判断 packet |

公式概念を踏襲するが、Codex の強みを消さない。Codex は単なる Claude Code subagent controller ではなく、実装判断・差分統合・検証・正本反映の final integrator として残す。

## 2. Search packet

```text
question:
mode: search | review | operate
execution_mode: summarize | delegate | execute | review | decide | park
orchestration_required: yes
route_mode: fast_reply | balanced | parallel_deep | background_watch
budget:
why_search:
namespace:
scope:
out_of_scope:
source_order:
route_authority:
payload_fingerprint:
delegate_to:
evidence_needed:
stop_after:
done_when:
exit_condition:
return_to:
delivery_receipt:
external_review_state: not_sent | sent | received | failed | held | invalid_surface | timeout | not_applicable
send_status: ok | failed | held | unknown | not_applicable
failure_kind: none | attachment_failed | wrong_surface | timeout | payload_too_large | secret_risk | selector_drift | unknown
postmortem_action: none | retry_with_new_route | reroute | human_gate | add_check | archive_with_reason
mode_result:
return_format:
closure_rule:
```

必須:
- `question` は 1 行。
- この packet は `core.md` の下位 schema。`mode` / `execution_mode` / `orchestration_required` / `route_mode` / `budget` / `done_when` / `exit_condition` / `return_to` を省略しない。
- `mode_result` と `closure_rule` を混ぜない。search の result / blocker / unknown / candidate list は `mode_result`、route の閉じ方は `closure_rule` に置く。
- 外部AI / browser / cmux / API route では `route_authority` を省略しない。実行前に `dependency-registry:external-ai-route` / `dependency-registry:external-ai-file-loop` / `dependency-registry:browser-ai-review-playbook` / `dependency-registry:cmux-browser-review-send` の該当分を読む。
- 外部AI / browser / cmux / API route に渡す payload は `payload_fingerprint` を省略しない。path / byte_size / checksum_or_first_last_line / prompt_language を最低限残す。
- 外部AI / browser / lane / worker へ送る時は `delivery_receipt` / `external_review_state` / `send_status` を省略しない。未送信・添付失敗・profile lock・selector drift・timeout は `held` または `failed` で記録し、review 済みにしない。
- 外部レビューは `external_review_state: received` かつ `send_status: ok` の時だけ review evidence に入れる。その他は held evidence として保存し、本線へ戻す。
- 外部レビュー失敗は `failure_kind` と `postmortem_action` を必ず残す。失敗の種類が不明なまま同じ route を再実行しない。
- `why_search` が「なんとなく不安」だけなら検索しない。FDE core に戻す。
- `source_order` は最大 3 本。例: local file -> official docs -> web / external AI。
- `delegate_to` は `Codex本体` / `Explore` / `Plan` / `researcher` / `external AI` など、official layer と local role layer を混ぜずに書く。
- `stop_after` を置く。検索は完璧化でなく、採否に足りる証拠を集める作業。

## 3. Delegation rule

| 検索の型 | 逃がす先 | Codex 本体がやること |
|---|---|---|
| 広い file / log / grep | Explore / researcher | 問いを切る、採否、反映 |
| 実装前の文脈収集 | Plan / planner | write scope と検証順を決める |
| 公式機能の確認 | official docs / reference | 公式概念と local role を分離する |
| 外部AI比較 | external AI / browser AI | raw を採用せず、FDE filter で反映 |
| 実装差分確認 | reviewer / Technical Judge | blocker と最小修正を選ぶ |
| 単純な機械 op | Codex 本体 | `cp` / `mv` / 小さい sed 的変更は dispatch せず、差分と smoke だけ戻す |

## 3.1 Query decomposition

複合質問（「〜かつ〜」「〜 and 〜」「疑問符が2つ以上」など）は、単一クエリとして投げると recall が下がる。並列サブクエリに分解してそれぞれ実行し、結果を統合する。

| 状況 | 対処 |
|---|---|
| 疑問符（？ / ?）が2つ以上 | サブクエリに分割して並列実行 |
| "and" / "かつ" / 読点2か所以上の列挙 | 各節をサブクエリに分割 |
| 単一疑問・単純質問 | 分解不要 |

制約: 既存の `source_order` 最大3本ルール（§2）と矛盾しない。分解後の各サブクエリも source_order ≤ 3 を守る。

**Detector**: `route_search(query)["decompose"] is True` のとき `sub_queries` が2件未満ならルーティング失敗。
**Repair Path**: `shared/scripts/search_route.py` の `_is_composite` / `_split_query` を修正し、`test_search_route.py` を全 pass させてから再実行する。

## 3.2 grep vs semantic-RAG routing

検索対象の性質によって最適なツールが異なる。「何でもベクター化（semantic RAG）」は anti-pattern。コードベースや構造化設定はインデックス密度が低く、意味検索が誤 chunk を引いて silent failure になる。

| 対象の性質 | 推奨ツール | 理由 |
|---|---|---|
| コードベース / 構造化設定ファイル | grep / Glob | 依存関係・定義箇所・正確なパターンを拾える。ベクター RAG は誤 chunk で silent failure |
| 大量非構造テキスト（ドキュメント / 議事録 / ナレッジベース） | 意味検索 / RAG | 全文 grep は再現率が低く、意味的に近いチャンクを拾う方が適切 |
| 外部情報 / Web / 最新動向 | web 検索 | ローカルに存在しない情報は外部経路を使う |
| 対象が不明 | grep 先行（local-first 原則） | まずローカルで grep → 見つからなければ意味検索 → 外部の順で昇格 |

**anti-pattern**: 対象がコードや設定でも semantic RAG を第一選択にすること。依存関係の見落とし・誤 chunk の採用に直結する。

**Detector**: `route_search(query, target_hint)["tool"]` が `"grep"` のはずの対象で `"semantic_rag"` を返したら設定ミス。
**Repair Path**: `target_hint` の値が `_CODE_HINTS` / `_SEMANTIC_HINTS` / `_WEB_HINTS` のいずれにも属さない場合は `"unknown"` が返る。`shared/scripts/search_route.py` のヒントセットに追加して再テストする。

## 3.3 Web search technique (= web step に出る時の打ち方)

web は検索順（`axis-registry.md §Research/Search Axis` / 本 file §4.2）の最終段。local / official / 既存実装で足りない時だけ出る。出る時は次の打ち方で精度とコストを両立する。

| # | technique | 中身 |
|---|---|---|
| 1 | 知りたい事実で打つ | クエリは「文書タイトル」ではなく「知りたい事実の言い方」で書く。例: ✕ `Python ssotloader` → ◯ `Python で設定を1か所にまとめる方法` |
| 2 | 演算子で絞る | `site:` / `filetype:` / `intitle:` をスタック（演算子と語の間にスペースを入れない）。`OR` 結合は括弧でくくる。例: `site:github.com filetype:py "ssot_loader"` |
| 4 | 一次ソース優先 + 横読み検証 | 一次ソース（公式 docs / 論文 / 著名 engineering blog）を優先。記事を読み込む前に別タブで発信元・引用元を確認する（lateral reading）。作成時点と事象発生時点が近いほど信頼度が高い |

既存ルールに委ねる（重複させない）:
- 3 クエリで閉じなければ打ち切り → `[不明]`: 本 file §4.2 Unknown Location Routing / §6 Return format
- 重要判断は 2-3 source で cross-check: `axis-registry.md §Research/Search Axis` 検索順 5

**Detector**: web 検索結果を `[事実: source]` として採用する前に、source が一次か二次か / 発信元確認済みかが return format に無い場合は、二次情報未検証として扱う。
**Repair Path**: source pointer に発信元（URL / 著者 / 日付）を付け、二次情報は一次で裏取りしてから採用する。

## 4. Orchestration gate

作業開始前に、次の trigger を見る。1 つでも当たれば `orchestration_required: yes` が既定。

| trigger | 例 | 既定の分担 |
|---|---|---|
| 広い読み取り | 複数 file / log / grep / registry 全体 | reader / Explore に逃がす |
| 複数対象 | 3 file 以上 / 3 surface 以上 / 複数 lane | 対象ごとに担当を分ける |
| 外部AI | browser AI / API / Gemini / Grok / Claude / ChatGPT | sender / collector を分ける |
| 送信 | browser へ prompt 投入 / file-backed packet 投入 | sender が実行し、Codex は採否へ戻る |
| 回収 | 待ち / transcript / result file / collect-body | collector が回収し、Codex は比較する |
| 比較レビュー | 2 provider 以上 / 複数案評価 | reviewer が表にし、Codex は採用判断だけ持つ |

`orchestration_required: no` にできるのは、単純機械 op、1 file の小修正、即答できる説明、または安全な smoke だけ。no の理由が書けない場合は作業を開始しない。

### 4.0.0 Route authority gate

外部AI / browser AI / cmux / API route は、記憶や直近の drift だけで実行しない。route authority を読んでから実行する。

```text
route_authority:
- route_registry: dependency-registry:external-ai-route
- file_loop: dependency-registry:external-ai-file-loop
- execution_wrapper: dependency-registry:cmux-browser-review-send
- playbook: dependency-registry:browser-ai-review-playbook
- live_surface_check: cmux tree --all / resolver
```

この gate が欠けた外部AI送信・回収・hold 判定は `logic_bug: route-authority-missing`。成功/失敗に関係なく、その結果を正本採用せず、まず route を修復する。

### 4.0.1 Delivery receipt gate

送信 / 回収 / 比較レビューは、送ったつもりで閉じない。

```text
delivery_receipt:
- surface_confirmed:
- payload_confirmed:
- attachment_or_body_confirmed:
- response_or_null:
- collected_at:
external_review_state: not_sent | sent | received | failed | held | invalid_surface | timeout
transmit_success:
send_status: ok | failed | held | unknown
failure_kind: none | attachment_failed | wrong_surface | timeout | payload_too_large | secret_risk | selector_drift | unknown
postmortem_action: none | retry_with_new_route | reroute | human_gate | add_check | archive_with_reason
```

`send_status: ok` は、対象 surface が正しいこと、payload が本文または添付として届いたこと、payload_fingerprint と画面上の投入内容が一致したこと、回答または明示 null が回収されたことが揃った時だけ使う。1 つでも欠ける場合は `failed` または `held` とし、Codex 本体は採用判断ではなく route 修復 / hold / return_to へ戻す。

`send_status: failed | held | unknown` または `external_review_state: failed | held | invalid_surface | timeout` の時は、`failure_kind` で出来事を分け、`postmortem_action` で次の処置を決める。`attachment_failed` と `wrong_surface` と `timeout` を同じ失敗として扱わない。

`external_review_state: held` や `waiting` 相当の状態に入る時は、待ちの正体を消さない。最低限、次の `waiting_contract` を同じ packet / TODO / lane status のどれかに残す。

```text
waiting_contract:
- waiting_for:
- expected_reply:
- check_owner:
- next_check_at:
- wake_trigger:
- timeout_or_cooldown:
- fallback_action:
- return_to:
```

`waiting_contract` が無い待機は `route_failure: waiting_contract_missing` として扱い、完了・採用・close 判定に使わない。

### 4.0.1.1 External AI handoff + PDCA loop

外部AI / 別AIは、採用判断者ではなく researcher / reviewer / challenger として使う。Codex 5.5 またはその時の technical judge / integrator が、採否・統合・正本反映を持つ。

Grok -> Codex は一例であり、Gemini / ChatGPT / Claude / Cloud Code / Grok などの provider 名に固定しない。contract は `researcher_or_reviewer_ai -> technical_judge_or_integrator` として書く。

```text
ai_handoff_contract:
- researcher_or_reviewer_ai:
- technical_judge_or_integrator:
- purpose:
- expected_output:
- evidence_format:
- adoption_criteria:
- return_to:
- pdca_record:
```

PDCA:
- Plan: 依頼前に目的、期待出力、採否基準、証跡形式を決める。
- Do: AI が調査、反証、候補出し、比較表化を行う。
- Check: technical judge / integrator が事実性、有用性、採用可否、漏れを評価する。
- Act: 採用した知見を FDE / brain / TODO / lane status へ反映し、不採用理由を残す。
- Improve: 次回の AI 依頼テンプレ、採否基準、役割分担を更新する。

AI に投げっぱなしにしない。`pdca_record` が無い外部AI handoff は、採用済みではなく `received_not_integrated` として扱う。

### 4.0.2 Main thread check

`return_to` は文字列一致だけで閉じない。外部AI / browser / cmux / lane dispatch の採用前に、active todo / lane status と照合する。

```text
main_thread_check:
- return_to:
- active_todo_pointer:
- lane_status_pointer:
- archive_conflict_checked: yes | no
- result: matched | mismatched | unknown
```

`result: mismatched | unknown` の場合は、採用判断へ進まず `held` として本線確認へ戻す。

検索・広域読み取り・外部AI比較を始める時は、`source_order` / `delegate_to` / `stop_after` / `return_format` が必須。欠ける場合は `packet-invalid` とする。

Codex 本体に残すもの:
- 問いの切り方
- 採用 / 棄却 / 保留
- 最小編集
- diff / test / smoke の最終確認
- ユーザーへの報告

## 4.1 Route Mode

`orchestration_required` は分業の有無、`route_mode` は速度・確度・コストの選択。混ぜない。

| route_mode | 使う時 | 既定の動き | done_when / exit_condition |
|---|---|---|---|
| `fast_reply` | すぐ答える / user が待っている / 低リスク | 既知事実 + 最大 1 source。長い探索をしない | 1 画面で次行動が決まる |
| `balanced` | 通常作業 | local first + 必要なら 1 delegate | source と採否が残る |
| `parallel_deep` | 広い読み取り / 比較 / FDE吸収 / 外部AI review | reader / reviewer / collector を分ける | 本体が採用判断へ戻れる |
| `background_watch` | 待ち / 回収 / 重い検証 / 外部pane応答 | watcher / collector へ逃がす | 期限・再確認方法・戻り先がある |

`route_mode` を選ばず「適切にやる」と書いた packet は受領しない。`budget` に token / time / cost / risk の上限を書く。

## 4.2 Unknown Location Routing

「どこにあるか分からない」は実装問題ではなく routing 問題として扱う。

| step | action | stop_after |
|---|---|---|
| local pointer | README / dependency-registry / data-index / playbook を見る | 既知 pointer が見つかるまで |
| local search | `rg` で最大 3 query | path 候補が出るまで |
| delegate search | Gemini CLI / explorer / browser AI / web を route に応じて使う | source / confidence / next_action が返るまで |
| absorb | 見つけた場所を registry / pointer / playbook に戻す | 次回同じ検索が不要になるまで |

同じ「探せ」が 2 回出たら、検索結果だけで閉じず registry / pointer / playbook の修復を done_when に入れる。

## 5. Prior-art gate

新規機構を作る前に、公式機能・既存 OSS・ローカル既存実装を最大 3 本で見る。足りない要素だけを実装対象にし、既存で足りるものは `dependency-registry` 参照へ落とす。

## 6. Return format

検索担当は長文を返さない。Codex 本体へ戻す形はこれだけ。

```text
confirmed:
contradicted:
unknown:
recommended_action:
sources:
```

`unknown` は推測で埋めない。source / query / path / tool を変えた確認を最大 3 回まで行い、閉じなければ `[不明]` として FDE core に戻す。

## 7. Guard

- 公式概念を local role 名で上書きしない。
- local role を公式機能のように断定しない。
- 検索担当に採用判断まで渡さない。
- Codex 本体が検索ログを抱え込まない。
- 検索結果は raw / report / digest に逃がし、FDE core へ長文を戻さない。
- 担当の返答は `confirmed / contradicted / unknown / recommended_action / sources` に圧縮する。raw長文返却は受領しない。
- trigger に当たったのに `orchestration_required` が無い作業は受領しない。
- 送信 / 回収 / 比較レビューを Codex 本体だけで抱えた場合は、次 turn で修復 packet を切る。

## 8. Lint / Smoke / E2E check

FDE 自体を変えた時は、まず `lint` で形式・参照・registry key を見る。その後、必要に応じて smoke / E2E に進む。

| level | check | 何を見るか | 使う時 | done_when / exit_condition |
|---|---|---|---|---|
| L0 | lint | 形式、参照、未定義 key、draft 混入 | doc / registry / SSOT の変更 | 機械 check が pass |
| L1 | unit | 小さい単位の関数・規則 | 実装 / script の局所変更 | 期待入出力が pass |
| L2 | integration / contract | module 接続 / 入出力 schema / provider-consumer 約束 | file-backed packet / wrapper / API | 境界 contract が pass |
| L3 | smoke | 小さい実行で入口が動くか | wrapper / route / FDE rule の変更 | 代表 happy path が pass |
| L4 | E2E | 入口から回収・比較・採用まで通るか | browser AI / multi-surface / pipeline | 入口から closure まで通る |
| L5 | regression | 以前の failure が戻っていないか | bug fix / drift repair | 既知 failure が再発しない |
| L6 | acceptance / user-layer | 期待する業務/ユーザー結果を満たすか | 完成判定 / CEO確認 | CEO / owner が採用判断できる |
| side | exploratory | まだ仮説が粗い時の手動探索 | 新route / 新UI / ラボ | 次の check level が決まる |

各検証 step は `done_when` または `exit_condition` を持つ。持たない検証は evidence ではなく作業ログとして扱う。

FDE package lint:

```bash
python3 shared/scripts/fde_lint.py
```

Orchestration smoke:

```bash
rg -n "orchestration_required|delegate_plan|codex_main_role|広い読み取り|複数対象|外部AI|送信|回収|比較レビュー|packet-invalid" core.md search-orchestration.md
```

E2E 例: `FDE bundle review -> pointer meaning transform -> 4 browser send -> collect -> compare -> Codex adopt` は、bundle / transform / send / collect / compare を分ける。Codex 本体が全部抱えたら E2E 失敗。

失敗として検出するもの:
- 広域検索なのに `delegate_to` がない。
- `stop_after` がない。
- raw長文を Codex 本体へ返している。
- 比較レビューを Codex 本体だけで実施している。
- `return_to` がない。

closure_rule: active
