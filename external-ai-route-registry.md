---
title: External AI Route Registry
type: reference
status: active
created: 2026-05-08
updated: 2026-05-21
owner: codex-main
tags: [external-ai, browser-ai, routing, registry, smoke]
related:
  - external-ai-file-loop.md
  - external-ai-file-review-packet.md
  - Documents/reports/2026-05-21-provider-facts-table-official-url.md
---

# 外部AI route registry

外部 AI / browser AI / API route の用途別 registry。料金・無料枠・提供 model は変動するため、実行直前に確認する。

- [事実: `Documents/reports/2026-05-21-provider-facts-table-official-url.md`] Provider facts table は 2026-05-21 に公式 URL のみで取得済み。`free_or_included_candidate` / `paid_explicit_required` の分類は同 report を参照する。FDE 本文採用、account / key / billing / smoke / 外部送信は未実施。

## route

| route | 種別 | 得意 | file upload | file download | 既定用途 | 状態 |
|---|---|---|---|---|---|---|
| ChatGPT browser | browser AI | 長文構成 / HTML / 実装レビュー / 要約 / Library管理 | 512MB / 2M tokens / ZIP(コード解析) | PDF, Excel, 画像 / Google Sheets統合 | 統合案レビュー / 文書管理 | adopted (May 2026) |
| Claude.ai browser | browser AI | 長文読解 / 戦略レビュー / 反証 / Artifacts | 500MB (20files) / Project(30MB) | Word, Excel, PPT (Artifacts) | 深い critique / ビジネス文書作成 | adopted (May 2026) |
| Gemini browser | browser AI | 長文処理 / Google系調査 / 比較 / 動画・音声 | 1.65GB (Video/Audio) / Drive同期 | Google系, PDF, Office / Drive保存 | 比較レビュー / 動画・音声解析 | adopted (May 2026) |
| Grok browser | browser AI | 高速な壁打ち / X 文脈 / 反応案 / coding critique | 50MB / ZIP(ソースコード) | PDF, 画像 (Grok Studio) | 短時間 critique / リアルタイムX調査 | adopted (May 2026) |
| Perplexity / search AI | search AI | 出典付き web 調査 / ローカルPC操作 | 1GB (Ent) / 50MB (Pro) / ローカル直接 | 生成レポート / 編集済みローカルファイル | 最新情報確認 / ローカルデータ統合 | adopted (May 2026) |
| GitHub repo / Copilot / GitHub Models | repo + IDE AI + model bench | repo 正本保管 / VS Code 補助 / prompt-model 比較 | Codespaces連携 / Playground | 生成コード / WASMビルド成果物 | 無料 repo + Copilot + モデル比較 | adopted (May 2026) |
| Groq API | API | 高速 batch / classifier / short summary | n/a | n/a | 大量定型処理 | candidate |
| Google AI Platform | API | 大量処理 / Google 文脈 | n/a | n/a | batch / evaluator | candidate |
| Hugging Face / GitHub Models / OpenRouter / Cerebras | API/router | 無料枠 / model 比較 / fallback / 高速推論 | n/a | n/a | smoke bench | candidate |

## 既存 local asset

新規実装前に以下を確認する。

| path | 役割 |
|---|---|
| `dependency-registry:shared-scripts` | browser AI / multi AI review の既存実行系 |
| `dependency-registry:shared-scripts` | browser chat route の既存設定候補 |
| `dependency-registry:shared-scripts` | provider 実装群 |
| `dependency-registry:shared-scripts` | OpenRouterProvider / CerebrasProvider の OpenAI-compatible no-call provider 定義 |
| `dependency-registry:shared-lib` | Groq / Hugging Face / OpenRouter など API route の既存 router |
| `dependency-registry:shared-lib` | Groq client helper |
| `dependency-registry:shared-lib` | Gemini CLI client helper |
| `dependency-registry:shared-lib` | LLM client 抽象 |
| `dependency-registry:grok-tools` | Grok browser / http / scraper / task DB 既存実験 |
| `dependency-registry:multi-ai-unified-design` | multi AI 統合設計の既存候補 |
| `dependency-registry:multi-ai-review-gate` | review gate 既存設計 |
| `dependency-registry:multi-ai-methodology` | multi AI review 方法論 |
| `dependency-registry:groq-grok-distinction` | Groq / Grok 混同防止 |
| `dependency-registry:research-multi-ai-prompt` | multi AI consultation prompt |

## smoke record schema

```markdown
| date | route | input_packet | output_path | elapsed | cost_or_quota | token_eff | time_eff | impl_eff | parallel_eff | freshness | quality | next_use |
|---|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---|
```

## route score 軸

5 点満点。実測がないものは `unknown` と書き、推測で固定しない。

| 軸 | 意味 | 高得点の条件 |
|---|---|---|
| token_eff | Codex-main の context を節約できるか | file upload / output path / path-only return ができる |
| time_eff | 壁時計時間が短いか | 投入から回収までが速い / 待機を main が抱えない |
| impl_eff | 実装成果物に直結するか | HTML / code / diff / JSON をそのまま worker が保存できる |
| parallel_eff | 並列しやすいか | 同じ packet を複数 route に投げても衝突しない |
| freshness | リアルタイム性 / 現在情報に強いか | web search / X search / citations / current source が使える |
| quality | 回答品質 | 抜け漏れ、反証、構成、実装可能性が高い |

## ecosystem leverage map

単体 AI ではなく、各 provider が背負う ecosystem まで含めて ROI を見る。採用判断は ecosystem 側に置かず、FDE / Codex / CEO に戻す。

| ecosystem | 接続しているもの | 使い方 | guardrail |
|---|---|---|---|
| Google / Gemini | Google Search / YouTube / Docs / Drive / Gemini Notebook / NotebookLM | 調査、source-backed 要約、長文咀嚼、RAG 的な遅延レビュー | source 追加 / upload は実操作。Notebook は正本ではなく digestion layer |
| GitHub | repository / Issues / PR / Actions / VS Code / Copilot / GitHub Models | repo は無料正本置き場、Copilot は IDE 補助、GitHub Models は prompt/model smoke | 有料枠追加や billing opt-in は Type1。repo の source of truth は local git と同期して確認 |
| OpenAI / ChatGPT | ChatGPT Projects / Search / browser AI / Codex | 構成、実装レビュー、読者視点、統合案 | browser project を workspace と対応させる。home URL reuse を入口にしない |
| xAI / Grok | X / realtime web / Grok browser | X 文脈、速報、短時間 critique、SNS反応仮説 | 厳密な事実確定や repo 正本判断に使わない |
| DeepSeek | browser / API / hosted models | 低コスト反証、コード案、比較ベンチ | sandbox 限定。secret / private repo / 顧客情報 / 未公開戦略を入れない。採用前に Codex local fact check |

## routing heuristic

| 優先したい効率 | 使う route |
|---|---|
| token_eff | browser AI file upload / Spark file-backed / Cloud Code result_path |
| time_eff | Grok / Groq API / Spark |
| impl_eff | ChatGPT browser / Grok browser / Cloud Code worker |
| parallel_eff | browser AI 4 route 横投げ / API batch |
| freshness | Grok browser / Perplexity / ChatGPT search / Gemini search |
| quality | Claude.ai / ChatGPT / Gemini の比較回収 |

## browser AI surface routing

browser AI に聞く時は、目的別に既存 surface を使い分ける。番号は drift するため固定せず、送信直前に `cmux tree --all` と `dependency-registry:cmux-browser-review-send` の resolver で取り直す。

| 用途 | 既定の聞き先 | 使う時 | fallback |
|---|---|---|---|
| 設計レビュー / 技術調査 / 外部 critique | `リサーチ` workspace の browser AI project 面 | FDE / Cloud ops / 実装方針 / ベスプラ比較 | provider home/new chat |
| Main / Top との壁打ち / 意味づけ / idea fan-out | `Main / Top` workspace の browser AI 面 (旧: `Kusanagi / 草薙`) | CEO 対話の隣で即時比較し、lane へ流す前の発散・分類をしたい時 | Research project 面 |
| コンテンツ / 営業 / ラボ 固有の素材 | 各 lane workspace の browser 面 | lane 固有 context を保ったまま聞く時 | リサーチ project 面 |
| 汚したくない単発 smoke | provider home/new chat | prompt や selector の動作確認 | Research project 面 |

運用:

- 正式レビューは `リサーチ` の project 面を優先する。広い検索 / 外部ベスプラ / OSS・公式比較は、必要に応じてリサーチ側の Gemini / search surface に軽い下調べを先行させる。
- Main / Top の browser AI は恒久作業場ではなく、idea intake と即時壁打ち用。結果は lane pointer / report / todo に吸収し、surface は残骸化する前に閉じる。
- 新規 home は「きれいな単発」または project 面が壊れている時だけ使う。
- 同じ packet を複数 provider に投げる時は file-backed prompt にし、回収結果を local report に残す。
- `multi-AI` は実装上の総称として残っていても、運用名は `browser AI review` / `browser AI debut` に寄せる。

## 3者役割分担 (Codex 5.5 x Grok x TOP) 2026-05-15

CEO Type1 GO 済みの 3者分担。外部AI route を決める時は、情報軸と構造軸を混ぜない。

| role | primary axis | responsibilities | route / guardrail |
|---|---|---|---|
| Codex 5.5 | 構造 / 自動化 | dispatch chain 健康度、SSOT drift 検知、設計 review、Type1 境界 sub-judge | local source / FDE / socket dogfood を照合し、採用判断を戻す |
| Grok | 外部情報 / 即興 | X/Web fact check、業界・競合・マクロ動向、brainstorming、文面質感、軽量外部情報窓口 | `dependency-registry:grok-cmux-pane-route` を primary。厳密事実・repo 正本判断は Codex が再確認 |
| TOP | lane routing / CEO 窓口 | lane 振り分け、横断 packet 起票、ACK 回収、socket / file-backed 運用ルール | CEO 判断と broadcast の収束役 |
| Sales CC | 営業 outcome | 案件発掘、CASE、draft、CEO GO、送信、polling、返信 draft | sales lane 内の outcome 実行。TOP #3 とは直交して並走 |

Grok primary route:

| priority | route | use | status |
|---|---|---|---|
| primary | cmux pane terminal + file-backed packet (`workspace:1 surface:79` は 2026-05-15 採用時点の live 候補) | TOP 隣接の即時壁打ち / X-Web 文脈 / short critique | adopted 2026-05-15 / surface 番号は送信直前に再確認 |
| secondary | Research workspace browser AI | 即時性より調査深度 / provider 比較 / Research 協調が必要な時 | candidate |
| avoid-default | API client | secret / quota / billing / key 管理が必要な時 | 現時点非推奨。Type1 + smoke まで hold |

## Gemini web search routing

### Gemini route taxonomy

`Gemini` とだけ言って route を確定しない。実行前に接続面 / profile / workspace / cost class を分ける。

| route | 使う時 | 注意 |
|---|---|---|
| Chrome Gemini | human が Chrome / primary browser profile で直接見る時 | Codex は通常触らない。human 作業面を汚さない |
| CMUX Top Gemini | Main / Top の右側など、CEO 対話の隣で FDE / 運用判断を即レビューする時 | 既存文脈を使う。汚したくない時だけ同 workspace に新規 Gemini を開く |
| CMUX Research Gemini | Research workspace で調査 / fan-out / 反証を回す時 | 採用判断は FDE / Codex / CEO へ戻す |
| Gemini Notebook / NotebookLM | 長文 source / notebook 文脈を使う時 | source 追加 / upload は実操作なので smoke / Type1-adjacent として扱う |
| Gemini CLI / headless | browser / pane 経路が使えない時の例外 | 既定では使わない。token / context 効率が悪い場合は `avoid` とする |

file-attached review は `cmux_ops.py review-attach` の dry-run -> 実機添付 -> `review-send` -> collect receipt で閉じる。添付 chip / file list が見えない場合は `attachment_unverified` として採用判断に使わない。この rule は route / completion 条件であり、`review-attach` wrapper 実装品質の採用根拠にはしない。wrapper 実装の採否は別の test / smoke / implementation review で扱う。

- [事実: `dependency-registry:ideas-inbox` 2026-05-04] Gemini は「外向け窓」用途、つまりトレンド観測 / 競合・OSS 探索 / web 検索 fan-out に限定する方針メモがある。
- [事実: `dependency-registry:gemini-lightweight-research`] Gemini headless query は `dependency-registry:shared-lib` の scratch cwd 隔離を使う。対話 `gemini-boot.sh` と headless query は別レーンとして扱う。
- [推測] WebSearch の費用効率は Gemini が有利な可能性があるが、現時点では route smoke の `cost_or_quota` 実測がないため固定しない。
- [不明] Gemini search の file upload / download / quota / speed は未確認。実行直前に smoke で測る。

運用:

- web / trend / OSS / competitor fan-out は Gemini search を候補に入れる。
- 長文比較、Google 文脈、外部定義の複数候補整理、Claude / Codex への反証役にも Gemini を使う。
- Gemini を Research に閉じ込めない。Research は収集・比較の入口で、採用判断は FDE / Codex / CEO へ戻す。
- 内部判断、正本化、採用判定、Obsidian / repo の最終 source of truth 判定には Gemini を使わない。
- Gemini 結果は `[事実: source] / [推測] / [不明]` に再分類し、source 付きの local result file として戻す。

## Research lane shelf operation

Research lane では、5.5 が問いの切り方・採否を担当し、Gemini CLI / browser AI は小スコープの補佐に限定する。

```text
5.5 judge -> Gemini small scoped recommendation/research -> 5-line return -> 5.5 adoption
```

| shelf | role | rule |
|---|---|---|
| Research controller | 問いの分割 / 採否 / FDE packet化 | `done_when` に直結する 1 問だけ切る |
| Gemini CLI support | 小さい候補出し / 反証 / 低コスト要約 | tool 実行禁止 or read-only。広域探索を渡さない |
| browser AI shelf | provider 別の外部観点 / source-backed review | public-safe packet、surface 明示、Type1 境界確認後のみ |

運用:

- Gemini へは `1 job = 1 question`。返却は `route / recommendation / reason / blocker / next_check` か `route / diff_or_status / test_or_smoke / blocker / next_check` に圧縮する。
- Gemini / browser AI の返答は採用判断ではない。Research 5.5 / Codex が local source と照合して `adopt / partial / hold / reject` を決める。
- secret / billing / external submit / auth / upload / source 追加 / FDE正本更新は human gate。
- surface 番号は drift するため正本化しない。送信直前に cmux tree / resolver / receipt で確認する。

## Grok coding loop

Grok は未開拓枠として、Research lane で coding / design review の smoke を回す。ただし Grok は正本 writer ではない。

```text
Research prompt -> Grok coding/design reply -> Codex classify -> small patch or hold -> evidence back to FDE
```

| phase | owner | rule |
|---|---|---|
| prompt | Research / Codex | file-backed prompt。対象 path / 制約 / 出力形式を固定する |
| reply | Grok browser | code / diff idea / risk / unknown を短く返す |
| classify | Codex | `adopt / hold / reject / unknown` に分ける。現物確認なしに採用しない |
| implement | Codex / Cloud Code / worker | 採用分だけ小さく実装。Type1 / secret / production は止める |
| return | Codex | result path / diff / test / reason を FDE / report へ戻す |

最初の smoke は「小さい既存 script / doc tool / browser helper」に限定する。Grok に repository 全体の write 権限や secret を渡さない。

## cost policy

| class | rule |
|---|---|
| `free_only_default` | 既定。無料枠・無料 credit・free model variant は積極的に登録候補へ入れる |
| `existing_subscription_use` | すでに継続課金している browser AI / IDE AI 枠。追加課金なしで使える範囲は積極活用する |
| `free_needs_registration` | CEO が隣で account / key を作る。AI は手順・保存先・smoke だけ出す |
| `paid_explicit_required` | 有料・prepaid・最低購入・クレカ必須。明示許可まで作らない |
| `cloud_ai_high_cost` | Cloud AI / 従量課金 / agent 実行など、壁時計では速くても費用が伸びやすい枠。小さな packet と budget 付きで使う |
| `unknown_cost` | 公式 source で無料/有料が確定するまで Research に戻す |

運用:

- 新規課金 / billing opt-in / plan upgrade / API key 作成は Type1。CEO GO まで止める。
- 既存サブスク枠は sunk cost として ROI 高めに扱う。ただし quota / message limit / premium request は smoke record に残す。
- Cloud AI は「高価だが強い実行枠」。browser AI / free API / 既存サブスクで足りる棚卸しや critique には使いすぎない。
- 無料 repo / free tier / 既存サブスク / 新規有料を混ぜて語らない。`cost_class` を先に付ける。

## Browser AI capability inventory

Research tab / Research lane に任せる非同期棚卸し。目的は「どの browser AI を、何に、どの cost class で使うと Codex-main の token / 時間を最も節約できるか」を実測すること。

scope_route:
- selected_scope: lane-dispatch / research capability inventory
- owner: Research lane
- parallelizable: yes
- write_scope: report / smoke record only
- collision_risk: low if each provider surface is separated
- type1_risk: external send / upload / new billing はあり。public-safe packet のみで開始
- evidence_required: provider, surface, cost_class, input_packet, output_path, elapsed, attachment_verified, quota note

対象:

| provider | 最初に測る能力 | 最小 smoke |
|---|---|---|
| Gemini browser / Notebook | Google search 連携、YouTube / web / docs source 咀嚼、NotebookLM 同期 | public URL 1 件 + 20 行要約 + citation / source retention 確認 |
| ChatGPT browser / Projects | 実装レビュー、構成、読者視点、project memory / file 添付 | 小さい file-backed packet + critique / patch idea |
| Claude.ai browser | 長文読解、反証、設計レビュー | 同一 packet で risk / missing test / alternative |
| Grok browser | X / realtime / coding critique | 短い repo snippet or URL + 速度 / freshness / critique |
| GitHub Copilot / Models | VS Code 補助、repo 文脈、prompt-model 比較 | selection review / prompt eval / rate-limit note |
| DeepSeek sandbox | 低コスト coding反証 / model比較 | public-safe toy prompt + no-secret output review |

完了条件:

- provider ごとに `best_use / avoid / cost_class / surface_route / attachment_or_source_handling / result_format / failure_mode` を 1 表で残す。
- 推測だけで「使える」と言わない。最低 1 smoke または `not_tested` を明記する。
- Research の結果は raw / report まで。FDE 反映と運用採用は Codex / CEO が local で行う。

## Main / Top AI bench

Top の目的は、CEO のアイディアを発散し、適切な lane に落として、吸収結果を即運用に戻すこと。AI を増やす時も、作業面を増殖させるのではなく、短い bench として使う。

| slot | 既定候補 | 役割 | guardrail |
|---|---|---|---|
| primary judge | Codex | local SSOT / fact check / 採否 / patch | 正本 writer。外部AI回答をそのまま採用しない |
| code executor / heavy worker | Cloud Code / Claude Code | 実装案、diff、長めの技術検討 | secret / Type1 / destructive は停止。結果は file-backed |
| broad ideation / Google context | Gemini Top / Notebook | 発散、要約、Google文脈、外部観点 | 正本採否はしない。Notebook/source追加は実操作として扱う |
| fast critique | Grok | 高速反応、X / realtime、短いcoding critique | 入力可能・cost確認できる時だけ。厳密事実は採用根拠にしない |
| sandbox-only | DeepSeek | public-safe 反証、低コスト比較 | Top常駐なし。secret/private/customer data 禁止 |

Top bench の完了条件:

- 発散結果を `Research / Lab / Content / Sales / Development / Operations` のどこへ落とすか決める。
- lane owner / next_action / evidence path だけ Top に残す。
- browser surface は結果を report 化してから閉じる。
- DeepSeek / unknown provider は `sandbox_only` とし、公開可能 toy input 以外を送らない。


## Free API inventory dispatch

Research に投げる棚卸し packet。目的は、無料で使える API / trial / free tier / free model variant を広く集め、Codex-main / Cloud Code の token 消費を避ける実用 route を見つけること。有料 route は混ぜず、`paid_explicit_required` として別棚にする。

必須出力:

```text
provider:
official_url:
free_tier_or_trial:
cost_class:
rate_limit:
best_use:
file_upload:
structured_output:
secret_risk:
setup_steps:
key_lifecycle_skill:
unknown:
```

優先候補:

- Groq free plan
- Google AI / Gemini API free tier
- GitHub Models included free usage
- OpenRouter `:free` model variants
- Hugging Face monthly free credits / Inference Providers
- Cloudflare Workers AI free allocation
- Cerebras free/trial status
- Grok browser / cmux pane route status check。
- Perplexity API free status check。なければ paid 棚
- Together AI free status check。なければ paid 棚
- Cloudflare Workers AI / AI Gateway free or trial route

Research は料金・無料枠が変動するものを固定せず、公式 source と取得日を残す。

## freshness note

- [事実: xAI Grok page 2026-05-08 browse] Grok は realtime search / X trends / document understanding を product capability として掲げている。
- [事実: X Help Grok 2026-05-08 browse] Grok on X は、回答時に X public posts search と real-time web search を使うか判断できる。
- [事実: OpenAI Help ChatGPT Search 2026-05-08 browse] ChatGPT Search は timely answers with web sources を提供する。
- [推測] X の反応・トレンド・世論系は Grok route の freshness が高い可能性がある。実運用では smoke で測る。

## ルール

- browser AI は「外部作業面」。Codex-main の context 節約を目的に使う。
- route 評価は推測で固定しない。file upload / download / quota / speed は smoke で測る。
- Cloud Code Sonnet / Spark / API route も同じ。安い・速い・得意は実測があるまで `unknown`。
- secret / private credential / production data は投げない。
- 外部送信に Type1 リスクがある材料は CEO GO を取る。

## 初回 smoke set

| smoke | route | input | expected output | owner | status |
|---|---|---|---|---|---|
| master-map-html-grok | Grok browser | `imported-source` | HTML draft + 10 line note | cc-coordinator | ready |
| master-map-critique-chatgpt | ChatGPT browser | `imported-source` | 20 line critique | cc-coordinator | ready |
| master-map-critique-claude | Claude.ai browser | same packet | 20 line critique | cc-coordinator | ready |
| master-map-critique-gemini | Gemini browser | same packet | 20 line critique | cc-coordinator | ready |
| realtime-source-grok | Grok browser | 1 URL + 1 行の確認観点 + `done_when` | freshness score | research lane | ready |

