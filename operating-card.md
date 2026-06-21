---
title: FDE operating card
type: brain
status: active
created: 2026-05-13
owner: codex
scope: fde-operating-card
tags: [fde, operating-card, orchestration]
related:
  - core.md
  - search-orchestration.md
---

# FDE 運用カード

毎 turn の最小起動カード。長い FDE 本文を読む代わりに、まずこれだけを見る。

## 0.0 Session Boot Gate

session 開始時に FDE 共通必読 3 file を読んでから業務へ入る gate。未読のまま進むと mode 未宣言・推測連発・fact tag 漏れ・deny rule 迂回が再発する (= memory `feedback_fde_session_start_gate`)。

必須:

- `fde_boot_check` を置き、3 file を読了済みか確認する。
- 未読があれば先に読む。ショートカットしない。
- 読了後に `mode` と `closure_rule` を宣言してから §0 Main Thread へ進む。
- session-start hook による機械強制は別 Type1 実装として分離予定。本 gate は宣言ベース運用とし、「機械保証済み」とは断定しない。
- この gate を忘れた session の route_failure は `route_failure: fde_boot_unread` として扱い、mode 宣言後に再開する。Gate Importance は §0.2 rank 2 (main thread / return_to) に準じる。

共通必読 3 file:
1. `operating-card.md`   — 本 file
2. `dialogue-protocol.md` — CEO 対話 R1-R11 / standard packet
3. `axis-registry.md`     — 8-axis / Work Mode Gate / Closure Rule

```text
fde_boot_check:
- operating_card_read: yes | no
- dialogue_protocol_read: yes | no
- axis_registry_read: yes | no
- mode_declared:
- closure_rule_declared:
- route_failure: none | fde_boot_unread
```

## 0. Main Thread

```text
本線:
今閉じる1件:
mode:
execution_mode:
戻り先(return_to):
main_line_age:
precheck:
route_authority:
payload_fingerprint:
immutable_context_key:
fact_label:
```

本線が空なら作業しない。横道に入る時も `return_to` を置く。`immutable_context_key` は、外部AI / lane / worker が要約しても消してはいけない復帰キーで、`correlation_id + return_to + payload_fingerprint` を既定にする。`mode` は作業種別、`execution_mode` はこの turn の動きとして分ける。`main_line_age` が古い / 不明な時は、採用・外部送信・長い作業の前に live todo / lane status と再照合する。

Token rule: FDE / Obsidian は全文再読しない。まずこの card + source pointer だけで動き、必要な時だけ該当 1 file / 1 節へ降りる。`obsidian_check` は検索クエリではなく `done` / `na` / source pointer で閉じる。

### 0.1 Fact Output Gate

ユーザーに見える説明・状況報告・判断・完了報告は、`fact_label` なしで返さない。`dialogue-protocol.md` の R7 は対話用の詳細ルールだが、毎 turn の入口ではこの gate を先に見る。

必須:

- 確認済みは `[事実: source]` を付ける。source は local file / command output / tool result / browser screenshot / external reply など、観測・照合手段が分かる粒度にする。
- ユーザーの指摘・補正・目的判断は `[ユーザー指摘]` として分ける。これは高優先の判断材料だが、local fact / command output と同じ `[事実: user]` にはしない。
- 未確認の補完は `[推測]` と明記する。
- source / path / tool を変えても閉じないものは `[不明]` として返す。推測で埋めない。
- 確認済みと未確認を同じ bullet に混ぜない。
- `完了` / `送信済み` / `レビュー済み` / `採用` は、対応する evidence と fact label がない場合は言わない。
- fact tag を忘れた応答は `route_failure: fact_output_gate_missed` として扱い、次 turn で運用ミスではなく entry route の穴として修復する。

```text
fact_output_gate:
- fact_label: [事実: source] | [推測] | [不明]
- user_signal: [ユーザー指摘] | none
- source_pointer:
- unknowns:
- mixed_claims_separated: yes | no
- route_failure: none | fact_output_gate_missed
```

### 0.1.1 External SSOT Closure Gate

FDE 関連の rule / report / inbox / lane rule / 外部AI review が FDE folder 外にある時は、直接根拠にしない。先に `dependency-registry.md` で `absorbed / external-authority / unabsorbed_candidate / not_fde / stale` を切る。

必須:

- `absorbed`: FDE 内 snapshot / pointer を読む。元 source は通常読まない。
- `external-authority`: registry の key 経由で必要部分だけ読む。
- `unabsorbed_candidate`: 採用前に audit / Type1 review へ戻す。
- `not_fde`: lane local / historical evidence として扱い、FDE へ入れない。
- `stale`: 入口から外す。
- `already-adopted`: 提案内容が FDE 内 snapshot / rule と全項目一致する場合。新規 Type1 escalation にせず、元 proposal を `status: done` / `close-type: already-adopted` で閉じる。

```text
external_ssot_closure_gate:
- source_pointer:
- registry_key:
- closure_class: absorbed | external-authority | unabsorbed_candidate | not_fde | stale | already-adopted
- action: use_internal_snapshot | read_external_authority | type1_review | ignore | cleanup | close_duplicate_proposal
```

#### 吸収済み重複提案 gate

Type1 / FDE 採用提案を起票する前に、同じ内容が operating-card / FDE 正本へ吸収済みか確認する。吸収済みの場合は、CEO 判断を増やさず `already-adopted` として閉じる。

必須:

- 提案の状態名・定義・運用規約を FDE 正本の該当箇所と表で照合する。
- 全項目一致なら新規採用判断ではなく、`close-type: already-adopted` を使う。
- 一部だけ不足している場合は、不足分だけを `unabsorbed_candidate` として提案し直す。
- `read-screen` で見た議論は補助 evidence。正本化は file-backed ACK / report / FDE 本文で行う。

```text
absorbed_duplicate_proposal_gate:
- proposal:
- fde_target:
- matched_items:
- missing_items:
- closure: already-adopted | unabsorbed_candidate | needs_review
```

### 0.2 Gate Importance Order

複数 gate が同時に見える時は、重要順位で処理する。数を固定せず、衝突時の勝ち負けを先に決める。

| rank | gate | 先に見る理由 | route_failure |
|---:|---|---|---|
| 0 | user correction / human judgment | ユーザーの補正・違和感・目的判断は route を更新する最上位 signal。ただし真偽判定ではなく、認知の罠があり得る前提で evidence と分ける | `human_judgment_ignored` |
| 1 | safety / Type1 / destructive / secret | 取り返しがつかない、または外部影響がある | `safety_gate_missed` |
| 2 | main thread / return_to / parent anchor | 主線ズレを防ぐ。横道はここに戻る | `main_thread_drift` |
| 3 | SSOT / prior-art / route authority | 車輪の再発明と手順再発明を止める | `ssot_first_missed` |
| 4 | resource / budget / runtime status | token / time / weekly / context を守る | `resource_gate_missed` |
| 5 | required-sufficient orchestration | やりすぎ・足りなすぎ・抱え込みを防ぐ | `required_sufficient_gate_missed` |
| 6 | delivery / evidence / fact labels | 送ったつもり・見たつもり・推測混入を防ぐ | `evidence_loop_skipped` |
| 7 | implementation / smoke / commit | 変更の正しさと保存単位を閉じる | `verification_missing` |

運用:

- 上位 gate が未解決なら、下位 gate の実行結果で採用判断しない。
- Type1 で待機に入る場合は、`wake_trigger` と `check_owner` を持たない限り accepted / done にしない。解除条件が曖昧な Type1 待ちは `route_failure: type1_wait_contract_missing` として扱う。
- 「SSOTないの？」「車輪の再発明」「違う」は rank 0 + rank 3 として扱い、新規実装を一度止める。ただしユーザー指摘も local fact / safety / Type1 evidence と照合し、認知の罠が疑われる時は短く棚卸しする。
- 速度が必要でも rank 1-3 は省略しない。省略する場合は `not_checked` ではなく `held` または `reroute` にする。
- 重要順位を間違えたら、反省ではなく `route_failure` として該当 gate を補強する。

#### sales / content Type1 audit

sales / content の外部送信・納品・公開候補を扱う時は、実行前に `ADR-0139-sales-content-type1-gate-required.md` と `sales_content_type1_gate_lint.py` を Type1 audit として見る。

必須:

- `Documents/lanes/sales/` または `Documents/lanes/content/` の send / proposal / delivery / publish / reply 系 file は、`type1_status` / `approval_ref` / `external_action` / `gate_evaluated_at` を確認する。
- `python3 shared/scripts/sales_content_type1_gate_lint.py --json` が issue を返す場合、外部送信・納品・公開へ進まない。
- `.archive` は通常 audit から除外し、歴史資料を確認する時だけ `--include-archive` を使う。
- この audit は P1 の監査採用であり、hook / fail-closed 化は P3 の別 task とする。

```text
sales_content_type1_audit:
- adr: Documents/decisions/ADR-0139-sales-content-type1-gate-required.md
- command: python3 shared/scripts/sales_content_type1_gate_lint.py --json
- result: pass | issues | not_applicable
- action: proceed | hold_for_type1_gate | reroute_to_p3
```

### 0.3 Repeated User Correction Triage

同じ趣旨のユーザー指摘を 2 回以上受けたら、現在の下層作業を継続しない。`route_failure` として上位 layer に戻し、意味・本線・既存資産・実行順を triage してから次の 1 手へ進む。

対象例:

- 「FDEチェックしているのか」
- 「ブラウザを進めろ」
- 「既存資産を生かしていない」
- 「完了扱いではなく実際に完了しろ」
- 「トリアージしていない」

必須:

- `repeated_user_correction_count` を置く。
- `route_failure` を `human_judgment_ignored` / `ssot_first_missed` / `main_thread_drift` / `semantic_triage_missing` / `evidence_loop_skipped` のどれかに分類する。
- 返答の前に `current_lower_action` を止め、`semantic_triage` を作る。
- `semantic_triage` は `adopt / absorb / hold / reroute / discard / blocker` のどれかへ分ける。
- `done` は triage と吸収・分離が終わった後だけ使う。先に `done` と書いて後で意味を合わせに行かない。

```text
repeated_user_correction_triage:
- repeated_user_correction_count:
- repeated_signal:
- route_failure:
- current_lower_action: stop | continue
- semantic_triage:
  - adopt:
  - absorb:
  - hold:
  - reroute:
  - discard:
  - blocker:
- next_action:
```

## 1. Route

FDE のオーケストレーション検討は常時 ON とする。これは毎回必ず並列 dispatch するという意味ではなく、作業開始時に `orchestration_required` と `route_mode` を明示し、十分なら local / fast path で閉じ、不足なら Spark / explorer / worker / lane / 外部AIのどこへ逃がすかを決めるという意味。

```text
orchestration_required: yes | no
route_mode: fast_reply | balanced | parallel_deep | background_watch
budget: token / time / cost / risk
resource_status:
codex_main_role:
delegate_plan:
done_when:
exit_condition:
```

既定:

| 条件 | route |
|---|---|
| すべての作業開始 | `orchestration_required` を検討し、理由 1 行を残す |
| 3 file / 3 surface / 複数AI / 比較 / 回収 / 広い検索 | `orchestration_required: yes` |
| user が待っている短答 | `fast_reply` |
| 通常作業 | `balanced` |
| 並列調査・外部AI・広い吸収 | `parallel_deep` |
| 待ち・監視・回収 | `background_watch` |

### 1.0 Resource Budget Gate

重いオーケストレーション、外部AI再投入、複数lane横断、長い統合判断の前に、対象runtimeの残り context / 5h limit / weekly limit / 実行中task を確認する。`/status` は目的ではなく、次の route_mode と delegate 先を決めるための計測。

必須:

- `resource_status` は固定時間だけでなく、通信回数・dispatch回数・重いtool使用回数で更新する。時間は上限目安で、長時間作業では概ね 1 時間を超えて未確認にしない。
- 目安: ユーザーとの重要往復 5-8 回、外部AI / lane / worker dispatch 2-3 回、または長い tool / browser / test 連続実行の後に status を見直す。
- 週次残量は日次または重要dispatch前に見る。
- weekly 残量は「リセットまでの日数」で割って 1日あたり budget を見る。1日あたり budget を超えそうなら Spark / 外部AI / 既存lane / wrapper へ逃がす。
- status 差分は直近ログと照合し、何が消費を増やしたかを `resource_cost_attribution` として残す。対象は user/assistant 往復、tool output、full read、browser screenshot、external dispatch、test/build、subagent。
- 消費の大きい要因が分かったら、次の route で read_light / grep_first / file-backed / Spark delegate / external AI / cached summary のどれかへ寄せる。
- 自分だけでなく、作業を渡す lane / runtime の `resource_status` を確認する。
- `context left` が少ない lane には、新しい重い調査・長文統合・外部レビュー回収を渡さない。成果物の参照、短い返答、commit済み事実の照会に絞る。
- `5h` / `weekly` に余裕があっても、context が詰まっているなら長い本線を持たせない。
- 短い調査、diff 要約、候補抽出、比較表、lint/test 結果の整形は、まず `GPT-5.3-Codex-Spark` を候補にする。5.5 は問いの切り方・採否・最小正本反映に残す。
- `Tasks` / background terminals が残っている場合は、追加dispatch前に本当に待つべきか、別routeへ逃がすかを決める。
- status command は、実行済み evidence として `terminal-read` / screenshot / pasted output のどれかで確認する。入力欄に残っているだけなら未実行。

```text
resource_budget_gate:
- target_runtime:
- checked_at:
- reset_at:
- days_until_reset:
- daily_weekly_budget:
- conversation_turns_since_check:
- dispatches_since_check:
- heavy_tool_runs_since_check:
- resource_cost_attribution:
  - suspected_driver:
  - evidence_log:
  - mitigation:
- context_left:
- context_used:
- five_hour_left:
- weekly_left:
- active_tasks:
- status_evidence: terminal_read | screenshot | user_paste | unknown
- spark_candidate: yes | no
- routing_decision: keep_local | spark_delegate | delegate | collect_only | hold | move_to_fresh_runtime
```

### 1.0.1 Thin Source Routing Gate

薄く見る時は、最初に source route を選ぶ。Top 5.5 が何でも読むと token / time を浪費するため、問いの種類ごとに最小 source を使う。

| source route | 使う時 | 使わない時 | evidence |
|---|---|---|---|
| local stat / grep | file の有無、mtime、差分、session jsonl の bytes/mtime | 意味解釈や外部知識が必要 | command output |
| Obsidian / Documents pointer | SSOT、過去に決めた rule、FDE正本、lane契約を確認する | 新しい外部情報・別AI視点が必要 | source pointer |
| Gemini pane | 低コストの広い下調べ、候補出し、外部観点、長文要約 | local fact の代替、正本採否、機密/Type1、未確認の実行 | prompt/response receipt |
| Spark / lightweight Codex | diff要約、表作成、短い調査、test log整形 | Top採否、価値判断、Type1 | changed files / test / smoke |
| browser AI / external AI | 発散レビュー、反証、複数AI差分、外部視点 | local source が不足したままの採用判断 | raw + fact/推測/不明分類 |

必須:

- `thin_source_route` を置く。`local_stat | obsidian_pointer | gemini_pane | spark | external_ai | top_decision` のどれか。
- Obsidian は「正本 / 過去決定 / source pointer」を見るために使う。検索クエリを作文して evidence にしない。
- Gemini pane は「薄い下調べ / 発散 / 要約」に使う。Gemini の回答を `[事実: source]` として採用せず、`[推測]` または external reply として local fact check へ戻す。
- Gemini CLI / API / browser AI は、使う前に resource / quota / cost / payload_fingerprint を確認する。確認できない時は `send_status: held`。
- ユーザーが「薄く」と言った時は、全文読みに行かず、`local stat -> source pointer -> Gemini/Spark delegate` の順にする。
- `thin_source_route` を間違えたら `route_failure: thin_source_route_missed` として、次回は route table に戻す。

```text
thin_source_routing:
- question:
- thin_source_route: local_stat | obsidian_pointer | gemini_pane | spark | external_ai | top_decision
- why_this_source:
- source_budget:
- expected_output:
- adoption_gate: local_fact_check | user_judgment | top_decision | none
- route_failure: none | thin_source_route_missed
```

### 1.0.2 SSOT / Prior-Art First Gate

browser / cmux / API / lane / shared wrapper / external AI / OSS / GitHub / runtime capability に触る前に、SSOT と既存実装を先に見る。これは検索の作法ではなく、車輪の再発明を止める実行 gate。

必須:

- `ssot_first_check` を置く。SSOT 管理層は `dependency-registry:ssot-registry` / `ssot-loader` / `ssot-lint` / `placement-rules` / `structural-separation` / `ssot-split` を優先確認。placement 判定は `dependency-registry:typology-placement` + `placement-rules` の組み合わせで。実行系なら `route_authority` を読む（browser AI = `dependency-registry:browser-ai-review-playbook`、cmux = `dependency-registry:cmux-reference`、新規 = `dependency-registry:official-capability`）。
- 既存 wrapper / lib がある場合は、先に `--help` / dry-run / smoke を見る。足りない要素だけを変更対象にする。
- SSOT が見つからない時は、`unknown_location_routing` に入り、最大 3 query で探す。見つからなければ `[不明]` として SSOT 欠落を修復対象にする。
- user が「車輪の再発明」「SSOTないの？」と指摘したら、進行中の新規実装を止め、`route_failure: ssot_first_missed` として rollback / reroute / minimal patch のどれかを選ぶ（ssot-registry 未登録や placement 矛盾も含む）。

```text
ssot_prior_art_first_gate:
- operation:
- ssot_pointer:
- ssot_registry_key: dependency-registry:ssot-registry | ssot-lint | structural-separation | placement-rules
- placement_key: dependency-registry:typology-placement | placement-rules
- route_authority:
- local_prior_art:
- official_capability:
- existing_wrapper_or_lib:
- gap_only_to_implement:
- user_reinvention_signal: yes | no
- route_failure: none | ssot_first_missed | prior_art_missed
```

### 1.1 Execution Assurance Cycle

仮説・違和感・広い調査・開発対話・外部AI review は、思いつきで走らせない。毎 turn の実行前に、既存 FDE と照合してから 1 cycle だけ回し、戻って親を確認する。

```text
execution_assurance_cycle:
- plan: FDE/core と照合し、question / done_when / exit_condition を 1 行化
- route_design: route_mode / delegate_plan / route_authority / budget を選ぶ
- run_once: 最小 packet / smoke / worker で 1 回だけ走らせる
- return_check: return_to を active todo / lane status / parent anchor と照合し、Anchor Integrity Check で親アンカーが生存しているか見る
- absorb_or_repair: adopt / hold / reject / reroute を記録
```

必須:

- `plan` なしに dispatch / browser / cmux / 外部AI / lane 対話へ進まない。
- `route_design` は token / time / cost / risk の budget を持つ。
- `run_once` は 1 回の小実行。2 周目に入る前に `return_check` へ戻る。
- `return_check` が `mismatched | unknown` なら採用判断へ進まず、親アンカーを更新する。
- Anchor Integrity Check が `missing | changed | stale` なら、採用判断へ進まず `repair_plan` を 1 行で作り、親アンカーを再固定してから再開する。
- この cycle を忘れたら `route_failure: execution_assurance_missing` として、次 turn で文書ではなく gate / lint / wrapper のどれかへ修復する。

### 1.2 Required-Sufficient Orchestration Gate

ユーザーからの恒常条件。毎 turn / dispatch / browser送信 / lane返答 / 完了報告の前に、「FDEでオーケストレーション、必要かつ十分、トークン効率、速度効率、事前レビュー要否、運用保証」が満たされているか確認する。

必須:

- `orchestration_required` を明示する。複数AI・複数lane・広い検索・外部送信・長い統合判断なら既定で `yes`。
- `necessary_sufficient` を置く。やりすぎ/足りなすぎを分け、今回閉じる最小単位を決める。
- `token_efficiency` と `speed_efficiency` を分けて書く。速いがtokenを食う、token節約だが遅い、を混ぜない。
- `review_gate` を置く。事前レビューが必要なら先に投げ、不要なら理由を1行で残す。
- `operational_guarantee` を置く。test / smoke / receipt / status / blocker有無のどれで再現性を担保するかを書く。
- 不明な場合は `unknown` で止めず、source pointer / path / tool を変えて最大3回確認する。閉じなければ `[不明]` としてユーザーに棚卸しする。
- この gate を忘れたら `route_failure: required_sufficient_gate_missed` として、運用ミスではなく仕組みの穴として修復する。

```text
required_sufficient_orchestration_gate:
- orchestration_required: yes | no
- route_mode: fast_reply | balanced | parallel_deep | background_watch
- first_requested_mvp:
- side_requests:
- problem_scope: must_fix_for_mvp | hold | reroute | ignore
- necessary_sufficient:
  - enough:
  - excess_to_avoid:
  - missing_risk:
- token_efficiency:
- speed_efficiency:
- review_gate: required | not_required
- review_target:
- operational_guarantee:
- user_shelf_down_needed: yes | no
- blocker:
- route_failure: none | required_sufficient_gate_missed
```

### 1.3 MVP First Gate

ユーザーが最初に頼んだ成果を閉じる前に、追加依頼や途中で見つかった問題へ本線を奪わせない。

必須:

- `first_requested_mvp` を 1 行で固定する。
- 追加依頼は `side_requests` に置く。MVPに必要なら `problem_scope: must_fix_for_mvp`、不要なら `hold` または `reroute`。
- 実装中に見つかった問題は、MVP完了の blocker か、後で直せる改善かを分ける。
- `must_fix_for_mvp` 以外の問題で browser / cmux / selector / shared wrapper 探索を深掘りしない。
- 完了報告では、MVP本体 / 横置き / blocker を分けて書く。

## 2. Role Split

Codex 本体に残すもの:

- 問いの切り方
- 採用 / 棄却 / 保留
- 最小編集
- diff / test / smoke の最終確認
- ユーザーへの報告

逃がすもの:

- 広い読み取り
- 複数 surface 操作
- 外部AI送信 / 回収
- selector / wrapper drift 調査
- 比較表作成

### 2.0.1 Delegation Efficiency Gate

FDECC 精査から採用する効率ルール。委譲は増やせばよいわけではない。Codex 本体は、委譲前に scope / 成果物 / smoke を切る。

必須:

- dispatch 前に 1 回、`phase / step / expected_output / smoke` を置く。
- 1 delegate は原則 1 file または 1 concept。複数成果物を詰め込まない。
- delegate prompt には `smoke 結果 / blocker / changed files` の返却条件を入れる。
- `cp` / `mv` / 小さい一括置換 / 小さい file 読みは Codex 本体で実行し、dispatch しない。
- 並列は通常 2 件まで。3 件以上は探索 mode か、対象が独立していて戻り先が明確な時だけ。
- 完了待ちは transcript だけで判断しない。対象 file の mtime / diff / smoke を見る。

```text
delegation_efficiency:
- phase:
- step:
- delegate_scope: one_file | one_concept | exploratory
- expected_output:
- smoke_required:
- max_parallel:
- return_to:
```

## 2.1 User Input Safety

ユーザーの入力欄や作業画面を確認ダイアログ・権限確認・長い foreground 操作で塞ぐなら、その時点で orchestration failure。

必須:

- 確認ダイアログが出そうな操作を細かく直列実行しない。
- 外部AI / cmux / browser 操作では、先に `route_authority` を埋める。該当 authority を読んでいない実行は `packet-invalid`。
- 外部送信 / cmux / browser 操作は、可能な限り 1 worker / 1 script / 1 approval にまとめる。
- approval が複数回必要になったら、実行を止めて batch 化・権限設計・hold のどれかへ reroute する。
- `background_watch` は「ユーザー入力を塞がない」ことを done_when に含める。
- ユーザーが入力できない状態で待っているなら、作業は進んでいても FDE では未完了。
- 音声で `ペイン / pane` と聞こえる文脈を、`Gemini` / 外部AI route に読み替えない。外部AIを使う前に、`外部AI review の話か、cmux pane の話か` を文脈で確定する。確定できない場合は 1 行確認し、外部プロセスを起動しない。

### 2.1.0 CMUX Lane Send Gate

他workspace / 他lane / sidecar の terminal agent に送る時は、CMUXを直接の記憶で叩かない。`route_authority` として `Documents/references/cmux/pane-communication.md` / `Documents/references/cmux/send-targeting.md` の該当節を確認する。

必須:

- lane / sidecar / worker への正式依頼・返答は file-backed prompt / signal を使う。既定入口は `python3 shared/scripts/cmux_file_signal.py --message-file ... --workspace ... --surface ... --preflight --postflight-lines ...`。
- raw `cmux send` / `cmux send-key` は通常運用で使わない。使えるのは user が明示した即時操作・scratch・緊急復旧だけ。
- raw 操作を使う場合も、`workspace` と `surface` を両方指定し、`send` と `send-key enter` を同じ target に直列で行う。
- `cmux send` は入力欄へ置くだけで実行ではない。送信後は `terminal-read` / postflight / screenshot で、入力欄に残っていないことと結果が出たことを確認する。
- `Surface is not a terminal` / `not_found` / Enter未投入 / 入力欄残りは `route_failure: cmux_send_gate_missed` として扱い、同じ経路を繰り返さず wrapper / workspace+surface / file-backed へ reroute する。
- `role_resolution` / `liveness_check` の自動解決は FDE に直書きせず、`shared/scripts/cmux_resolve_surface.py` / 既存 lock / pipeline へ接続して処理する。
- lane / sidecar / worker dispatch の送達証跡は、まず `shared/scripts/cmux_feed_trace.py` と `feed.list` / `workstream_id` で見る。`read-screen` は prompt 詰まり、permission dialog、UI blocker の fallback にする。
- `delivered` は対象 `message_file` を含む `userPrompt`、`accepted` は同一 `workstream_id` の `Read` / `toolUse`、`result_written` は `Write`、`done` は `stop` または file-backed reply 存在で判定する。

```text
cmux_lane_send_gate:
- route_authority: Documents/references/cmux/pane-communication.md | Documents/references/cmux/send-targeting.md
- target_workspace:
- target_surface:
- role_resolution: resolved | pending | mismatch
- liveness_check: ok | stale | absent | unknown
- send_mode: file_signal | wrapper_direct | raw_user_explicit | scratch
- preflight: done | skipped_with_reason
- submit_verified: yes | no | unknown
- feed_trace:
  - command: python3 shared/scripts/cmux_feed_trace.py --message-file <path> --since <iso8601> --json
  - delivered: yes | no | unknown
  - accepted: yes | no | unknown
  - result_written: yes | no | unknown
  - done: yes | no | unknown
  - workstream_id:
- postflight: terminal_read | receipt_file | screenshot | not_done
- route_failure: none | cmux_send_gate_missed | liveness_stale | role_mismatch
```

## 2.1.1 External Review Gate

外部AI / browser AI / cmux review は、送ったつもりで本線を止めない。`mode: review` の採否に入る前に、送信・回収は `mode: operate` / `execution_mode: delegate` として閉じる。

必須:

- 送る前に `pre_send_decision` を置く。ユーザーから「送って」と見える指示が来ても、FDE側で `send_now | capture_first | ask_missing_context | hold | reroute` を選んでから動く。判断根拠なしの送信は `send_gate_missed`。
- `pre_send_decision: capture_first` の時は、`cmux browser snapshot` / `get html` / `get text` / 必要なら screenshot を保存し、送信・添付を続ける前に `capture_receipt` を残す。
- `pre_send_decision: send_now` は、`route_authority` / `payload_fingerprint` / `target_surface` / `return_to` が確認済みの時だけ使う。添付可否・本文可否・surface identity が不明なら `capture_first` または `hold`。
- `review_target_type` を `external_ai | internal_lane | internal_agent | human` で置く。宛先種別で、渡す文脈・出力形式・採否権限・推測の扱いを変える。
- 受信側では `sender_type` を `external_ai | internal_lane | internal_agent | human | unknown` で置く。route / message_file / surface / app / author / reply_to の evidence で判定し、判定できなければ `unknown` のまま採否に入らない。
- `target_surface` / `payload_pointer` / `payload_fingerprint` を置く。
- `payload_container_type` を `zip | single_file | multi_file | body_text | pointer_only` で置く。provider が ZIP を許すか、ZIP内ファイル数を数えるか、単一fileへ畳むべきかを分ける。
- `provider_upload_capability` を `zip_ok | zip_counts_inner_files | single_file_only | multi_file_ok | body_only | unknown` で置く。実測前は `unknown` のままにし、成功/失敗 receipt で更新する。
- browser AI に local folder を渡す時は、ZIP を既定にしない。まず browser の file chooser / attach button で対象 folder 内 file をまとめて選ぶ。`file_count_limit` / `payload_too_large` が出たら、同一 `immutable_context_key` で「残りを送る」と明記して追加送信し、provider が要求した `needed_files` を優先する。
- pointer / registry / SSOT が外部AIに読めない時は、外部AI向け alias file / manifest / expanded pointer を作り、`payload_fingerprint` に元 pointer と展開先を両方残す。
- `immutable_context_key` を置く。外部AIへの prompt / 添付 / reply summary からこの key が消えた場合は `payload_confirmed: no` とする。
- `external_review_state` を `not_sent | sent | received | failed | held | invalid_surface | timeout` で残す。
- `delivery_receipt` に `surface_confirmed / payload_confirmed / attachment_or_body_confirmed / response_or_null / collected_at` を残す。
- `transmit_success` と `send_status` を残す。
- 外部AIへの prompt では、各指摘に `[事実: 添付file/section]` / `[推測]` / `[不明]` を付けさせる。推測には追加確認、未知には閉じられない理由を書かせる。
- 採否では、外部AIの `[推測]` / `[不明]` をそのまま `adopt` にしない。local file / command / もう一つの reviewer 差分で事実確認してから `adopt` へ進める。
- `unblock_policy` を置く。外部AI review は品質 gate であり、本線 blocker にしない。
- `failure_reason` を置く。profile lock / selector drift / wrong surface / timeout / attachment missing を unknown に潰さない。
- `failure_reason` が `selector drift | attachment missing | file_count_limit | payload_too_large | timeout | invalid_surface` の時は、同じ操作を 2 回以上粘らず `reroute` または `held` に落とす。
- `failure_kind` を置く。`attachment_failed | wrong_surface | timeout | payload_too_large | secret_risk | selector_drift | unknown` を同じ failure として畳まない。
- `postmortem_action` を置く。`retry_with_new_route | reroute | human_gate | add_check | archive_with_reason` のどれにも接続しない失敗は完了にしない。
- `file_count_limit | payload_too_large` は即失敗ではない。初回 payload の `sent_files` / `rejected_files` / `remaining_files` を保存し、追加送信で閉じられるなら `progressive_disclosure` へ遷移する。
- `return_to` は active todo / lane status と照合し、archive 済み case を本線として採用しない。

```text
external_review_gate:
- pre_send_decision: send_now | capture_first | ask_missing_context | hold | reroute
- pre_send_reason:
- capture_receipt:
- target_surface:
- payload_pointer:
- payload_fingerprint:
- immutable_context_key:
- external_review_state: not_sent | sent | received | failed | held | invalid_surface | timeout
- delivery_receipt:
  - surface_confirmed:
  - payload_confirmed:
  - attachment_or_body_confirmed:
  - response_or_null:
  - collected_at:
- transmit_success: yes | no | unknown
- send_status: ok | failed | held | unknown | not_applicable
- failure_reason:
- failure_kind: none | attachment_failed | wrong_surface | timeout | payload_too_large | secret_risk | selector_drift | unknown
- postmortem_action: none | retry_with_new_route | reroute | human_gate | add_check | archive_with_reason
- reviewer_fact_tags: required | missing
- assumption_check: done | needed | not_applicable
- review_target_type: external_ai | internal_lane | internal_agent | human
- sender_type: external_ai | internal_lane | internal_agent | human | unknown
- sender_type_evidence:
- payload_container_type: zip | single_file | multi_file | body_text | pointer_only
- provider_upload_capability: zip_ok | zip_counts_inner_files | single_file_only | multi_file_ok | body_only | unknown
- folder_upload_strategy: file_chooser_multi_select | manifest_plus_key_files | provider_requested_files | not_applicable
- sent_files:
- rejected_files:
- remaining_files:
- needed_files:
- reroute_condition:
- unblock_policy: continue_main_line | wait_background | reroute
- return_to_checked_against: active_todo | lane_status | both
```

`external_review_state: received` かつ `send_status: ok` だけを review evidence に入れる。それ以外は held evidence として保存し、本線へ戻す。
`reviewer_fact_tags: missing` または `assumption_check: needed` の項目は、final adoption に入れず `provisional_adopt` / `hold` / `needs_cross_review` へ分ける。

宛先別 contract:

| review_target_type | 目的 | 必須入力 | 出力 | 採否の扱い |
|---|---|---|---|---|
| `external_ai` | 反証・発散・別モデル差分 | 添付payload / pointer展開 / fact tag要求 / `immutable_context_key` | `[事実] [推測] [不明]` 付き critique | raw は採用しない。local fact check または別AI差分確認後に採否 |
| `internal_lane` | レーン境界・運用整合 | CMUX packet / reply_to / scope_route / closure_rule | blocker / fix-required / optional と file pointer | lane authority 内なら採用候補。Topで親アンカー照合 |
| `internal_agent` | 実装・局所調査・検証 | owner / write_scope / done_when / tests | patch / report / changed files / test log | diff と test log で確認して採否 |
| `human` | 意思決定・優先度・違和感レビュー | 1画面要約 / 採否候補 / open question最大3つ | approve / reject / direction / question | 人間判断を最上位 input として、実装前に source log へ戻す |

`external_ai` は広く使わせる。`human` は短く、判断点を絞る。`internal_lane` は protocol 適合、`internal_agent` は作業scopeと検証ログを重視する。

### 2.1.2 External Code / Binary Trust Gate

GitHub / OSS / 外部ツールを取り込む時は、再利用条件と実行形式を分ける。source が読めることと、binary を信用して実行できることは別判断。

必須:

- `reuse_permission` を置く。license / terms / repository notice が未確認なら、copy / vendor / publish / redistribute へ進まない。
- `artifact_form` を `source | script | package | binary | hosted_service | unknown` で置く。
- `source` / `script` は license と attribution を確認し、必要なら local smoke 後に採用候補にする。
- `package` / `binary` は license だけでなく provenance / release署名またはchecksum / maintainer / update channel / sandbox可否を確認する。閉じなければ sandbox / read-only / no-network の PoC までに留める。
- CMUX のような既存採用済み実行ファイルも例外扱いにしない。信頼根拠は `trusted_existing_runtime` として evidence を残し、更新時は同 gate を再適用する。
- ライセンス不明、カスタム license、商用制限、copyleft 影響、binary provenance 不明は `needs-legal-or-policy-review` または `lab_sandbox_only` に落とす。

```text
external_artifact_trust_gate:
- source_url_or_path:
- artifact_form: source | script | package | binary | hosted_service | unknown
- reuse_permission: permissive | copyleft | noncommercial | proprietary | custom | unknown
- intended_use: read_reference | copy_snippet | vendor_source | install_package | run_binary | publish_derived
- provenance_evidence:
- license_evidence:
- attribution_required: yes | no | unknown
- sandbox_required: yes | no
- adoption_state: reference_only | adopt_source | lab_sandbox_only | hold | reject
```

受信時の判定:

| evidence | sender_type | 扱い |
|---|---|---|
| `route: <lane> -> top` / `message_file` / `reply_to` が CMUX packet | `internal_lane` | packet gate と reply contract を優先 |
| Codex subagent id / worker result / changed files / tests | `internal_agent` | diff と test log を優先 |
| browser surface / provider名 / 外部AI raw response | `external_ai` | fact tag / cross review / local fact check を必須 |
| user chat / CEO判断 / 明示的な人間レビュー | `human` | 短い確認と意思決定を優先 |
| evidence が衝突または不足 | `unknown` | `sender_type_unknown` として hold。最大1問で確認するか、source pointer を変えて確認 |

相手から来た質問・レビュー依頼で `sender_type` が `unknown` のままなら、相手の出力様式を勝手に外部AI/人間/内部laneへ寄せない。`review_target_type` と `sender_type` の両方が閉じてから、採否・実装・返信へ進む。

添付 container の分岐:

| provider_upload_capability | 使う payload | 失敗時 |
|---|---|---|
| `zip_ok` | ZIP | receipt に file_count / checksum を残す |
| `zip_counts_inner_files` | single Markdown へ畳む | ZIP は再試行しない。`file_count_limit` として記録 |
| `single_file_only` | single Markdown / PDF など 1 file | 複数file添付を避ける |
| `multi_file_ok` | 必要十分な複数file | file数上限に当たったら single file へ畳む |
| `body_only` | prompt body へ圧縮 | 添付なしで `payload_confirmed` を本文一致で見る |
| `unknown` | まず小さい smoke または既存 receipt を見る | 失敗したら capability を更新して reroute |

ZIP拒否・ZIP内file数上限・添付dialog失敗は同じ failure ではない。`failure_reason` を `zip_not_supported | file_count_limit | attachment_dialog_failed | selector drift | payload_too_large` へ分け、同じ失敗経路を繰り返さない。

`file_count_limit` の reroute は、単一file化だけに固定しない。次のどれかへ進める。

| reroute | 使う時 | done_when |
|---|---|---|
| `progressive_disclosure` | 全部は渡せないが、相手に不足fileを選ばせられる | 最小bundleで問いを投げ、`needed_files` / `unneeded_files` / `next_chunk_request` を回収 |
| `single_file_rollup` | 構造より全体読解が重要 | source見出し付き single Markdown に畳み、checksum を残す |
| `chunked_followup` | reviewer が追加で必要な領域を指定した | chunk_id / included_files / prior_context_key を付けて追加送信 |
| `ask_for_missing_context` | 相手が「分からない」と返した | 不足理由を `needed_files` として回収し、再送判断へ戻す |

progressive disclosure prompt では、最初に「この問いに答えるのに足りないfileがあれば `needed_files`、不要なら `enough_context: yes`」を出力させる。追加送信では `immutable_context_key` と `prior_context_key` を維持する。

## 2.1.2 Communication Evidence Loop

通信・レビュー依頼・自分の prompt は、相手に答えさせるだけでなく、次にこちらが渡すべき evidence を発見するために使う。

必須:

- 相手に `[事実] / [推測] / [不明]` を分けさせる。
- 相手の `[推測]` は `assumption_debt`、`[不明]` は `context_debt` として回収する。
- `assumption_debt` / `context_debt` は、こちら側の `needed_evidence` / `needed_files` / `needed_runtime_check` に変換する。
- 追加で渡す時は `prior_context_key` と `immutable_context_key` を維持し、同じ話題の続きだと分かる形にする。
- `needed_evidence` を渡せない時は、推測を採用せず `hold` / `needs_cross_review` / `human_decision` へ分ける。

```text
communication_evidence_loop:
- received_fact_tags: complete | partial | missing
- assumption_debt:
- context_debt:
- needed_evidence:
- needed_files:
- needed_runtime_check:
- topic_key:
- topic_round: 1 | 2 | 3
- max_rounds_per_topic: 3
- prior_context_key:
- next_send_payload:
- close_when: all_needed_evidence_sent | max_rounds_reached | debt_marked_hold | human_decision
```

相手に fact tag を付けさせた結果、こちらが何を渡せばよいかが見える。この変換を省いて、推測レビューをそのまま採用するのは `route_failure: evidence_loop_skipped` として扱う。

同一 `topic_key` での往復は最大 3 周まで。3 周しても `[推測]` / `[不明]` が残る場合は、さらに同じ相手へ聞き続けず、`hold` / `needs_cross_review` / `human_decision` / `local_runtime_check` のどれかへ切り替える。`topic_key` は「同じ論点か」を見るための短い名前で、provider 名や surface 番号ではなく、論点そのものに付ける。

## 2.2 Ambiguous Term Route Gate

音声入力・typo・同音異義・サービス名は、単語だけで route を確定しない。同じ語が複数の実行経路を持つ場合は、実行前に候補 route を展開して文脈で 1 つに落とす。文脈で落ちない時の次アクションは「黙って停止」ではなく、**意味を確定するための 1 問確認**。

例: 「Gemini で検索」

| route | 意味 | 実行前に必要な確認 |
|---|---|---|
| local search | Gemini 関連の local file / 設定 /履歴を探す | `rg` / Obsidian source pointer |
| web search | Gemini の現行仕様・外部情報を調べる | web 検索が必要な理由 |
| external AI | Gemini に prompt を投げて回答を得る | 外部AI利用の明示 / route_authority / payload_fingerprint |
| feature search | Gemini アプリ内の機能・画面を探す | 対象 surface / browser route |
| pane search | Gemini が開いている pane / surface を探す | `cmux tree` / surface 確認 |

route が文脈で確定できない時の標準動作:

```text
ambiguous_route:
- term:
- candidates:
- inferred_route:
- confidence: high | medium | low
- missing_meaning:
- clarification_question:
- action: execute | ask_one_question
```

`confidence: low` で tool / external / browser / cmux 操作へ進まない。代わりに `missing_meaning` を 1 つに絞り、`clarification_question` を返す。聞く時は 1 問だけ: 「ここでの Gemini は、外部AIに投げる意味ですか、開いている pane を探す意味ですか?」

この gate の目的は「実行禁止」ではなく「意味確定」。確認すれば route が決まる場合は blocker 扱いしない。

## 2.3 Confirmation Budget

確認は多ければよいわけではない。全レイヤーで、確認するかどうかは **confidence / impact / reversibility / route_delta** で決める。

```text
confirmation_budget:
- known_context:
- ambiguity:
- confidence: high | medium | low
- impact: low | medium | high
- reversible: yes | no
- route_delta: none | small | material
- confirmation_count: 0 | 1 | 2+
- action: infer_and_execute | ask_one_question | make_packet | stop_for_type1
```

| 条件 | 確認数 | 動き |
|---|---:|---|
| confidence high + impact low + reversible yes + route_delta none/small | 0 | 推定して進む。必要なら `[推測]` を付ける |
| confidence medium + impact low/medium + reversible yes | 0-1 | 文脈で補えるなら進む。不明点が route を変える時だけ 1 問 |
| confidence low + route_delta material | 1 | 1 問で意味確定してから進む |
| impact high / irreversible / Type1 / external / destructive | 1+packet | review packet / CEO GO。暗黙推定しない |
| 既決事項 / 直前に明示済み / source pointer あり | 0 | 再質問しない。既知として扱う |

確認質問の上限:

- 通常 turn: 1 問まで。
- 3 つ以上聞きたくなったら、質問ではなく packet 化して「何が未確定か」を整理する。
- 同じことを 2 回聞きたくなったら、先に `known_context` と source pointer を見直す。

この rule は全レイヤー共通。意味 layer / route layer / file state / pane state / code edit / external AI のどれでも、まず確認予算を切る。

## 2.4 Extreme Response Feedback Loop

AI は曖昧さや指摘を受けた時に、急に極端へ振れることがある。例: `削除します` / `全部やめます` / `今後やりません` / `実行しません` / `触りません` / `停止します`。これは安全ではなく、route 判断の過補正である場合がある。

極端語が出たら、実行前に次を切る。

```text
extreme_response_check:
- trigger_words:
- user_intent: correct_course | stop | forbid | delete | reduce_scope | clarify
- proposed_action:
- proportionality: low | ok | overcorrected
- safer_next_action:
- feedback_record: yes | no
```

| trigger | 既定解釈 | 禁止される反応 | 代わりにすること |
|---|---|---|---|
| `削除` | destructive / Type1 候補 | 即削除 / 全削除提案 | archive / mark / review packet |
| `やりません` | overcorrection 候補 | 永久禁止化 | 条件付き hold / route 修正 |
| `実行しない` | route 未確定 | 黙って停止 | 意味確定の 1 問 / confirmation budget |
| `全部` / `常に` / `絶対` | scope 過大化 | blanket rule 化 | scope / trigger / exception を限定 |
| `もうしない` | 謝罪反応 | 抽象反省 | detector / gate / next_action に変換 |

feedback loop:

1. ユーザーが「それは違う / 極端 / またやった」と指摘する。
2. その出力を `trigger_words / user_intent / proposed_action / proportionality` に分類する。
3. `safer_next_action` を 1 行にする。
4. 同じ型が 2 回出たら、この operating-card か該当 gate に detector を追加する。
5. 追加する detector は禁止文ではなく、次の route を変えるルールにする。

目的は「AI を臆病にする」ことではなく、**比例した反応**に戻すこと。確認・保留・削除・停止は、それぞれ impact と reversibility に応じて選ぶ。

## 3. Closure

```text
confirmed:
unknown:
changed:
test_or_smoke:
delivery_receipt:
external_review_state: not_sent | sent | received | failed | held | invalid_surface | timeout | not_applicable
transmit_success:
send_status: ok | failed | held | unknown | not_applicable
mode_result:
held:
next_collect:
```

`mode_result` は成果、`closure_rule` は閉じ方。review の `adopt / revise / reject / unknown` は `mode_result` に置き、`closure_rule` へ混ぜない。

外部AI / browser / lane / worker へ送った時は、`delivery_receipt` に `surface_confirmed / payload_confirmed / attachment_or_body_confirmed / response_or_null` を残す。`transmit_success` は `payload_fingerprint` と画面上の投入内容が一致した時だけ yes。3 つが揃わない、または `transmit_success` が yes でない場合は `send_status: failed | held | unknown` とし、レビュー済み・採用済みとして閉じない。

外部AI / cmux / browser 操作で `route_authority` が空だった場合、結果が成功しても FDE 上は `logic_bug: route-authority-missing` として扱い、次 turn で `core.md` / `search-orchestration.md` / `dependency-registry.md` / playbook のどれかを直す。

同じ注意を 2 回受けたら、返答だけで閉じず `core.md` / `search-orchestration.md` / playbook / registry のどれかを直す。

closure_rule: active
