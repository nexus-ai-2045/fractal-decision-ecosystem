---
title: Fractal Decision Ecosystem core
type: brain
status: active
created: 2026-05-13
owner: codex
scope: fde-core
tags: [fde, core, routing, lightweight]
related:
  - operating-card.md
  - root-router.md
  - data-index.md
  - lifecycle-operating-pattern.md
---

# Fractal Decision Ecosystem 中核

FDE は **Fractal Decision Ecosystem** の略。人間向け本文では初出を `Fractal Decision Ecosystem（FDE）` と展開する。

FDE core は **判断の動作だけ**を持つ。type catalog、lane別事情、例、過去知見、詳細 policy はここへ入れない。

毎 turn の起動は `operating-card.md` を先に見る。core は packet 詳細が必要な時だけ読む。

## 0. 4ポイント復帰

| ポイント | 内容 |
|---|---|
| 今わかったこと | FDE が太る主因は、動作・データ・policy・state が同じ本文に混ざること。 |
| まだ不明なこと | 既存の太い FDE 本文から、どこまで安全に分離できるかは段階的に確認する。 |
| 次にやる1手 | 新規 dispatch / operating-card はこの core を入口にし、詳細が必要な時だけ data index から辿る。 |
| Done when | FDE を読む時に、まずこの file だけで判断 loop を開始できる。 |

## 1. Core Loop

```text
1. 問いを1行にする
2. first_requested_mvp を固定し、追加依頼 / 横道 / 発生問題を横置きできる形にする
3. risk / exception を先に見る
4. namespace / scope / abstraction_layer / lane / done_when を置く
5. 最大3回だけ source pointer / path / tool を変えて確認する
6. status を切る: 確認済み / 未確認 / 不明 / 次に確認
7. 4ポイント復帰で戻る
```

## 2. Minimal Packet

```text
question:
mode: search | implement | review | operate | ideate | decide
execution_mode: summarize | delegate | execute | review | decide | park
orchestration_required: yes | no
orchestration_reason:
delegate_plan:
codex_main_role:
route_mode: fast_reply | balanced | parallel_deep | background_watch
budget:
force_level: WHEN_FREE | QUEUE_NEXT | FORCE_NOW
namespace:
scope:
out_of_scope:
abstraction_layer:
lane:
owner:
risk:
evidence:
done_when:
exit_condition:
merge_with:
return_to:
precheck:
route_authority:
payload_fingerprint:
first_requested_mvp:
side_requests:
problem_scope:
fact_label:
delivery_receipt:
external_review_state: not_sent | sent | received | failed | held | invalid_surface | timeout | not_applicable
send_status: ok | failed | held | unknown | not_applicable
failure_kind: none | attachment_failed | wrong_surface | timeout | payload_too_large | secret_risk | selector_drift | unknown
postmortem_action: none | retry_with_new_route | reroute | human_gate | add_check | archive_with_reason
main_line_age:
next_move: stay | up | down | reroute | park | exception
mode_result:
closure_rule:
```

人間向け凡例:

| field | 意味 |
|---|---|
| mode | 作業種別。search / implement / review / operate / ideate / decide。何を閉じるかの契約 |
| execution_mode | この turn の動き。要約して戻す / 委譲する / 自分で実行する / 評価する / 判断する / 保留する |
| orchestration_required | 分業が必要か。広い読み取り / 複数対象 / 外部AI / 送信 / 回収 / 比較レビューでは既定 yes |
| orchestration_reason | yes/no の理由。no で空なら packet-invalid |
| delegate_plan | 読み取り / 変換 / 送信 / 回収 / review などの分担 |
| codex_main_role | Codex 本体に残す役割。採否 / 最小編集 / 統合 / ユーザー説明だけを基本にする |
| route_mode | 速度・確度・コストの routing。即答 / 通常 / 並列深掘り / 待ち監視のどれか |
| budget | token / time / cost / risk の上限。例: `token: low`, `time: 10m`, `cost: no paid API`, `risk: no external write` |
| force_level | lane / AI / worker へ渡す時の緊急度。`WHEN_FREE` は空いたら、`QUEUE_NEXT` は次キュー、`FORCE_NOW` は現タスク中断レベル。未指定時は `WHEN_FREE` とみなすが、dispatch では明示する |
| namespace | 名前空間。例: fde, cmux, playbook, main-top, sales, research, security |
| scope | 今回扱う範囲 |
| out_of_scope | 今回あえて扱わない範囲 |
| abstraction_layer | 抽象度 / 高さ。principle, strategy, design, operation, implementation, evidence |
| layer | `abstraction_layer` の人間向け別名 |
| lane | 担当領域 / owner |
| axis | 分類タグ。レイヤー / レーン / 状態の総称にしない |
| done_when | 人間が見て閉じたと判断できる条件 |
| exit_condition | 次に何が起きたらこの loop を終了できるか |
| merge_with | 既存 thread / issue に合流できる時の戻り先 |
| return_to | 委譲 / 検索 / 横置き論点の後に戻る本線 |
| precheck | 開始前の短い現実確認。例: live todo と主線が一致 / return_to あり / orchestration_required 解決済み |
| route_authority | 実行経路の正本。外部AI / browser / cmux / API / lane dispatch では、実行前に読む registry / playbook / wrapper を列挙する |
| payload_fingerprint | 外部送信する本文 / file の同一性確認。最低形は path / byte_size / checksum_or_first_last_line / prompt_language |
| first_requested_mvp | ユーザーが最初に閉じてほしい成果。追加依頼や途中で出た問題より優先する |
| side_requests | MVPを止めずに横置きする追加依頼。owner / return_to / 再浮上条件だけ残す |
| problem_scope | 実行中に出た問題の扱い。MVP完了に必要なものだけ解決し、不要なら hold / reroute にする |
| fact_label | ユーザーに見える claim の事実ラベル。`[事実: source] / [推測] / [不明]` のどれか。確認済みと未確認を混ぜない |
| user_signal | ユーザーの指摘・補正・目的判断。`[ユーザー指摘]` として fact_label とは分ける |
| delivery_receipt | 外部 surface / lane / worker へ送った時の到達確認。最低形は `surface_confirmed / payload_confirmed / response_or_null` |
| external_review_state | 外部レビューの状態。未送信 / 送信済み / 受信済み / 失敗 / 保留 / surface誤り / timeout。`received` だけがレビュー入力になる |
| send_status | 外部送信・回収の状態。`ok` 以外を review 済みや採用済みにしない |
| failure_kind | 失敗の種類。`send_status: ok` 以外、または `external_review_state: received` 以外で成果物に進める前に必ず置く |
| postmortem_action | 再発防止または次ルート。失敗を close する前に retry / reroute / human gate / check 追加 / archive 理由のどれかへ接続する |
| main_line_age | 主線を最後に live todo / lane status と照合してからの経過。古い場合は採用前に再確認する |
| confirmation_budget | 確認数の上限。`confidence / impact / reversible / route_delta` から `0 / 1 / packet` を選ぶ |
| mode_result | mode 別の成果。search は result / blocker / unknown / candidate list、review は adopt / revise / reject / unknown |
| closure_rule | done / self_resolve / escalate / reroute / continue の受領条件 |

必須:
- `question` は 1 行。
- `mode` と `execution_mode` を先に置く。`mode` は作業種別、`execution_mode` はこの turn の動き。曖昧な時は実行せず、owner / closure を決める packet に戻す。
- `mode_result` と `closure_rule` を混ぜない。`mode_result` は成果、`closure_rule` は route の閉じ方。
- `orchestration_required` を空にしない。広い読み取り / 複数対象 / 外部AI / 送信 / 回収 / 比較レビューは `yes` を既定にする。
- `orchestration_required: no` は `orchestration_reason` が必須。理由がない no は `packet-invalid`。
- `orchestration_required: yes` は `delegate_plan` / `codex_main_role` / `return_to` が必須。
- `orchestration_required: yes` で `precheck` / `delegate_plan` / `codex_main_role` / `return_to` / `route_mode` / `budget` が `missing | unknown` の時は adoption block とし、先に route repair / delegate_plan 生成へ戻す。
- `route_mode` を空にしない。即答は `fast_reply`、通常は `balanced`、時間をかける並列探索は `parallel_deep`、待ち / 監視は `background_watch`。
- `budget` を空にしない。少なくとも token / time / cost / risk のどれか 1 つを書く。
- `first_requested_mvp` を空にしない。追加依頼や途中で見つかった問題は、MVP完了に必要なら `problem_scope: must_fix_for_mvp`、不要なら `side_requests` へ横置きする。
- `side_requests` は作業中の本線を奪わない。横置きしたものは `return_to` / owner / 再浮上条件を持つ時だけ残し、持てないものは今は捨てる。
- 実行中の問題は全部解こうとしない。MVPの `done_when` に直結する blocker だけを解決し、改善案・周辺最適化・別route修理は hold / reroute にする。
- `risk` / `exception` は `scope` より先に見る。`out_of_scope` で Type1 / secret / prod / destructive / external send を隠さない。
- `namespace` は正本群・概念空間。`lane` は owner / 担当領域。混ぜない。
- `namespace` / `scope` / `out_of_scope` / `abstraction_layer` を空で進めない。
- `owner` / `risk` / `evidence` / `done_when` / `exit_condition` / `closure_rule` を空で進めない。
- 新規 thread を増やす前に `merge_with` を確認する。合流先がなければ `none` と明記する。
- `execution_mode: delegate | review | park` の時は `return_to` を置く。戻り先がない委譲は作らない。
- `execution_mode: delegate | review | decide` の時は `precheck` を置き、`return_to` が live todo / lane status と矛盾していないか見る。
- 外部AI / browser / cmux / API / lane dispatch に送る前に `pre_send_decision` を置く。ユーザー指示をそのまま送信理由にせず、FDEで `send_now | capture_first | ask_missing_context | hold | reroute` を選ぶ。`pre_send_decision` が `missing | unknown` の時は送らない。
- 外部AI / browser / cmux / API / lane dispatch に入る時は `route_authority` を置く。最低限 `dependency-registry:external-ai-route` / `dependency-registry:external-ai-file-loop` / `dependency-registry:browser-ai-review-playbook` / `dependency-registry:cmux-browser-review-send` の該当分を確認する。欠ける場合は `packet-invalid`。
- ユーザーに見える説明・状況報告・判断・完了報告では `fact_label` を置く。`[事実: source]` は source / file / line / command / screenshot などの観測根拠を添える。ユーザーの指摘・補正・目的判断は `[ユーザー指摘]` として別 layer に置く。未確認の補完は `[推測]`、閉じないものは `[不明]` として返す。
- `fact_label` なしで返した場合は運用ミスだけで閉じず、`route_failure: fact_output_gate_missed` として `operating-card.md` の Fact Output Gate に戻す。
- 外部AI / browser / cmux / API / lane dispatch に送る payload は `payload_fingerprint` を置く。本文のサイズ・言語・同一性が確認できない場合は `send_status: held`。
- 外部AI / browser / lane / worker へ送る時は `delivery_receipt` / `external_review_state` / `send_status` を置く。`send_status: ok` は `surface_confirmed / payload_confirmed / response_or_null` が揃った時だけ。
- 外部レビューの状態は `not_sent -> sent -> received` または `failed | held | invalid_surface | timeout` へ明示遷移させる。`received` 以外を review evidence に入れない。
- `send_status: failed | held | unknown` または `external_review_state != received` の成果物は、採用判断の input ではなく blocker / held evidence として扱う。`mode_result: adopt | revise | reject` へ直接進めない。
- `send_status: failed | held | unknown` または `external_review_state: failed | held | invalid_surface | timeout` の時は `failure_kind` と `postmortem_action` を置く。種類と次アクションのない失敗は close しない。
- `failure_kind: unknown` は暫定だけに使う。次に調べる観測点を `postmortem_action` で `add_check` または `human_gate` へ接続する。
- `main_line_age` が古い、または `[不明]` の場合は、作業前または採用前に active todo / lane status（operator-local adapter または本 repo の active docs）と再照合する。
- `return_to` は自由記述だけで閉じない。採用前に active todo / lane status と一致することを `precheck` または `delivery_receipt` に残す。archive 済み case を本線にしない。
- 不明は推測で埋めず `[不明]` として戻す。

## 3. Move

| move | 使う時 |
|---|---|
| stay | 同じ層で閉じられる |
| up | 意味・優先順位・Type1・人間判断が必要 |
| down | 実装・検証・保存へ落とせる |
| reroute | owner / lane / abstraction_layer / namespace / scope が違う |
| park | 今やらないが再浮上条件を残す |
| exception | 外部送信 / secret / prod / destructive / collision |

## 4. Return Format

```text
今わかったこと:
まだ不明なこと:
次にやる1手:
Done when:
```

## 5. ここに置かないもの

| 混ざりやすいもの | 置き場 |
|---|---|
| type catalog / route catalog | `data-index.md` |
| lifecycle の汎用 slot | `lifecycle-operating-pattern.md` |
| lane別の入口 | `operating-card.md` / operator-local lane cards |
| Type1 / security / write boundary | `public-kernel/GATES.md` / `SECURITY.md` / `ai-contact-safety-contract.md` |
| 現在状態 / queue | operator-local adapter、または本 repo の active docs |
| 過去知見 / report | `ops-best-practice-inventory.md` / operator-local reports |

closure_rule: active
