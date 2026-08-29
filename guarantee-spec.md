---
title: FDE 保証仕様
type: brain
status: active
created: 2026-05-22
updated: 2026-08-29
owner: development
scope: fde-guarantee-spec
tags: [fde, guarantee, startup, output-mode, notification, state-ssot]
related:
  - operating-card.md
  - dialogue-protocol.md
  - axis-registry.md
  - dependency-registry.md
note: >
  各 hook / script が参照する SSOT。各章は機械参照される正本である。
  lane-communication は dependency-registry:lane-communication（operator-local-adapter）。
  変更時は single_writer が行い、変更後に dependency-registry を確認する。
---

# FDE 保証仕様

各 hook と script がここを正本として参照する「保証仕様」。宣言だけで終わる状態から、機械が強制し・届けられ・閉じたか確認する状態へ移行するための定義集。

---

## 1. 起動保証

### 1.1 目的

業務に入る前にリスク tier を選び、通常作業へ Full 起動コストを漏らさず、
高リスク作業だけを確実に Full boot へ上げる。SessionStart hook はこの章を
`additionalContext` として注入し、保証 script が正本・runtime copy・出力契約の
drift を検査する。

### 1.2 満たすべき前提条件（起動ゲート）

起動ゲートは tier ごとに分ける。Lite を Full の不足状態として扱わない。

| 条件番号 | tier | 条件名 | 満たす判定 | ユーザー向け出力 |
|---|---|---|---|---|
| C-1 | 共通 | tier 選択 | Full trigger の有無を先に判定した | 通常は非表示 |
| C-2L | Lite | operating card | `operating-card.md` を読み、4点 check と `mode` / `closure_rule` を内部保持した | YAML を出さず直接回答 |
| C-2F | Full | FDE 3 file 読了 | operating-card / dialogue-protocol / axis-registry をすべて読んだ | boot check を表示 |
| C-3F | Full | mode / closure 宣言 | `mode` と `owner / next_state / target_file` が空でない | 業務前に表示 |

Full trigger は Type1 / 外部送信 / 公開 / 削除 / 課金 / auth / production / hook /
settings / secrets / SSOT変更 / 複数lane・agent / 再発 / owner・source・closure・risk
不明。該当しない日常会話・軽い調査・短い判断・単発小修正は Lite とする。

Lite の内部判定をユーザーへ毎回表示することは `over_triage_visible` として検知対象にする。
ただしユーザーが監査表示を求めた場合、route が曖昧な場合、または route failure 報告は例外。

### 1.3 機械チェック可能な述語

SessionStart hook は会話 transcript や tool-use log を読まない warn-only injector である。
したがって「実際に読んだ」「実際に宣言した」の判定を hook 単体の能力として記述しない。
機械保証は静的契約・runtime drift・hook smoke を対象にし、turn 内遵守は runtime prompt
とレビューで扱う。

> 棄却済み設計の記録: 旧 §1.3 の `C1_fde_files_read`（SessionStart hook が tool-use
> ログを走査し Read 呼び出しと照合する）は、SessionStart 時点で当該セッションの
> tool-use ログが存在しないため機械述語として成立しない。棄却済みであり再実装しない。
> 本節を参照してこの再提案を却下する。

```text
startup_gate:
  static_contract:
    lite_default_present: 日常作業を Lite とする文言がある
    lite_hidden_present: Lite は可視 YAML を出さず直接回答する文言がある
    full_triggers_present: Full trigger 群が明記されている
    full_boot_present: Full の 3 file と可視宣言が明記されている
  runtime_drift:
    canonical: fde-boot-gate.sh（dependency-registry:startup-boot-gate）
    copies: 各 runtime（Claude / Codex）の hooks 配下へ配布した runtime copy
    satisfied: すべての runtime copy が存在し、canonical と SHA-256 が一致
  hook_smoke:
    satisfied: exit 0 かつ valid JSON、additionalContext が static_contract を満たす
    skip_satisfied: FDE_BOOT_GATE_SKIP=1 で exit 0 かつ stdout が空
  aggregate:
    command: fde_boot_gate_guarantee --json（operator-local。物理 path は registry 経由で解決）
    all_satisfied: static_contract AND runtime_drift AND hook_smoke
```

### 1.4 現状と移行方針

起動 hook は warn-only とし、hard block へ昇格しない。理由は、Lite の通常応答を
誤停止させず、Full trigger を prompt route で上げるため。runtime copy の更新は
Type1 として明示承認下でのみ行い、settings の登録変更は別承認境界に保つ。

保証範囲は「正本とruntime hookが同じtier契約を注入する」まで。モデルが各turnで
正しく分類したことの絶対保証ではない。誤分類は `over_triage_visible` または
`full_trigger_missed` として記録し、再発時に trigger / detector を修復する。

### 1.5 毎turn事実来歴保証

実装 (hook / schema / sync script) は operator-local
（`dependency-registry:fact-provenance`）。本節は契約の要点のみ公開する。

repositoryの事実来歴SessionStart hookは非表示segment markerとenvelope契約をinjectし、
Stop hookは全表示byteのcoverage、分類排他、metadata一致、本文全体hash binding、
recorded metadata、session lifecycleを検証する。

- envelope schema: `fact-provenance-envelope/v2`（v1 fallbackなし）
- 保存schema: `fact-provenance/v2`
- binding schema: `assistant-output-binding/v1`
- 表示本文: fact labelを人間可読のまま保持する
- 監査記録: `recorded_by` / `recorded_at`、segment hash・byte数、分類、`actor_kind` /
  `event_time` / `scope_id`を0600のlocal JSONLへ保存し、raw本文やraw sourceは保存しない
- stop条件: envelope欠落・複数・末尾以外・不正、marker外byte、segment metadata不一致、分類混在、
  binding欠落、validator不在、startup marker不整合
- live境界: `fact_provenance_install_sync.py --check --json`（operator-local。物理 path は
  registry 経由で解決）のruntime driftが残る間はlive保証済みとしない
- 非保証: 外部世界での真実性、意味分類の正しさ、source kindの真正性、Windows runtime互換、
  host runtime再起動後の発火は個別証拠なしに昇格しない

---

## 2. 出力モード

### 2.1 目的

人間向け出力と機械間 packet の書き方と切替条件を定義する。Phase 2 の detector がこの章を正本として禁止記号範囲を実装する。誤検知を避けるため、Phase 2 では最初に警告粒度（ブロックではなく warn）から始める。

### 2.2 モード定義

#### モード A: 人間向け出力

CEO など人間が直接読む出力。

**許可する要素:**

- 見出し: `#` / `##` / `###` によるマークダウン見出し
- 番号付きリスト: `1.` `2.` 形式の数字+ピリオド
- 箇条書き: `-` または `*` の1文字記号（リスト先頭のみ）
- テーブル: `|` によるマークダウンテーブル
- コードブロック: 三連バッククォート（内部は技術的内容のため例外）
- 太字・斜体: `**text**` / `*text*`（強調の最小単位）
- 改行・空行

**禁止する要素（禁止記号の正確な範囲）:**

以下を「禁止記号」として定義する。Phase 2 detector はこのリストを正本として検知する。

| 禁止カテゴリ | 具体例 | 禁止理由 |
|---|---|---|
| ギリシャ文字 | α β γ δ ε ζ η θ ι κ λ μ ν ξ ο π ρ σ τ υ φ χ ψ ω（大文字含む） | 人間には読みにくく、コード/数式文脈以外では装飾に過ぎない |
| 数学記号 | ∑ ∏ ∫ ∂ ∇ ∞ ≈ ≠ ≤ ≥ ± × ÷ √ | 同上 |
| 特殊矢印の連続装飾 | → ← ↑ ↓ ↔ ⇒ ⇔ を3個以上連続で並べる | 人間向け文書に不要な装飾（単発の矢印は可） |
| コミット hash / ID 裸出し | `a3180fd7` のような16進数8〜40文字の連続（文脈なしに裸で書く） | 人間には意味がなく、読み飛ばされる情報 |
| 内部コード裸出し | `task_id=xxx` `workstream_id=yyy` `message_id=zzz` など内部識別子をそのまま列挙 | 人間向け文書に不要な内部詳細 |
| 長 path 裸出し | machine-local 絶対 path をテキスト中に裸で埋め込む（50文字超の path） | 読みにくく、repo-local 相対 path や capability key で足りる |
| agent / session ID | `agent_id: abc123def456` などの内部 ID 裸出し | 人間向け文書に不要 |

**例外:**

- 絵文字・チェックマーク系の記号（✅ ❌ ⚠️ ★ ☆ ✓ ✗ 🔑 などの絵文字全般）は許可する。[事実: CEO 直接 2026-05-23「絵文字はOK」] により従来の絵文字禁止を撤回。Phase 2 detector の emoji_symbols 検知（旧カテゴリ4）も無効化済で hook と整合。
- コードブロック（` ``` ` 内）は技術的内容のため禁止記号の適用外。
- 「場所: path:line」形式の申し送りなど、明示的に path 記述が必要な場面は短縮表記を優先する。
- ユーザーが明示的に「hash を出してほしい」と指示した場合はその turn のみ例外。

#### モード B: 機械間 packet

lane / agent / hook 間で受け渡す構造化データ。

**必須要素:**

- envelope フィールド: `schema_version` / `message_id` / `from` / `to` / `return_to` / `correlation_id`
- fact tag: 各主張に `[事実: source]` / `[推測]` / `[不明]` を付ける
- `obsidian_check` と `scope_route` フィールド
- `waiting_contract` の9フィールド（wait_reason / wake_trigger / check_owner / check_method / check_cadence / expiry_or_retake / fallback_on_expiry / expected_output_path を含む）

**モード B での禁止:**

人間向けの見出しや番号リストを主要構造として使わない。構造は YAML / frontmatter フィールドで表現する。

### 2.3 モード切替条件

| 状況 | 使うモード | 判断根拠 |
|---|---|---|
| CEO / 人間への直接返答 | モード A | 受信者が人間 |
| lane / agent への dispatch file | モード B | 受信者が machine / agent |
| SessionStart hook の inject メッセージ | モード A | 人間が読む警告 |
| terminal_update_emit.sh への引数 | モード A（1行サマリ） | 人間が読む通知 |
| handoff frontmatter | モード B | machine 参照 |

### 2.4 検知粒度の方針（Phase 2 実装指針）

Phase 2 detector は最初は警告粒度（warn）で実装し、誤検知率を測定してからブロック粒度（block）へ昇格する。理由: 既存の file / script / agent 出力には技術的に必要な記号が含まれる場合があり、初期ブロックは業務を止めるリスクがある。

```
output_mode_detector:
  mode: warn  # 初期値。block へは CEO GO で昇格
  scan_target: assistant 出力テキスト（コードブロック内を除く）
  warn_pattern:
    - category: greek_letters
      pattern: /[α-ωΑ-Ω]/
    - category: math_symbols
      pattern: /[∑∏∫∂∇∞≈≠≤≥±×÷√]/
    - category: decorative_symbols
      pattern: /[→←↑↓↔⇒⇔★☆✓✗✅❌⚠️]/
    - category: bare_commit_hash
      pattern: /\b[0-9a-f]{8,40}\b/  # 文脈なし連続16進数
    - category: long_absolute_path
      pattern: /\/[A-Za-z0-9_\-\/\.]{50,}/  # 50文字超の絶対 path
  false_positive_exception:
    - code_blocks: 三連バッククォート内は除外
    - user_explicit_request: ユーザー明示指示の turn は skip
  action_on_warn: 出力末尾に警告行を追記（本文はブロックしない）
  action_on_block: 出力を保留し警告とともに rewrite 要求（Phase 2 昇格後）
```

---

## 3. 通知保証

### 3.1 目的

重要イベントを必ず届け、届いたかを確認する閉ループを定義する。Phase 3 がこの章を正本として実装する。

### 3.2 必ず届ける重要イベント（4種）

| イベント番号 | イベント名 | 定義 | 発火タイミング |
|---|---|---|---|
| E-1 | 着手 | dispatch を受領し、作業を開始したこと | dispatch file を Read した直後、最初の tool 実行前 |
| E-2 | 完了 | 依頼された全 Receiver Action を実施し、diff / test / smoke / blocker の4点セットが揃ったこと | DONE reply file を書いた直後 |
| E-3 | 詰まり | 自己解決できないブロッカーが発生し、作業が止まっていること | blocker を検知した turn 内、3手以内 |
| E-4 | 承認待ち | Type1 / CEO GO が必要な操作に到達し、手動承認を待っていること | Type1 操作が必要と判断した turn 内、1手以内 |

### 3.3 通知の配達方法

標準配達経路: `bash <local-project-root>/shared/scripts/terminal_update_emit.sh INFO <lane> "<1行サマリ>" <関連ファイルパス>`

1行サマリの形式: `[E-1/E-2/E-3/E-4] <イベント内容> / <関連ファイル短縮名>`

例:
- `[E-1] guarantee-spec.md 起草着手 / fde/guarantee-spec.md`
- `[E-2] guarantee-spec.md 作成・commit 完了 / fde/guarantee-spec.md`
- `[E-3] TYPE1 blocker: settings.json 変更待ち`
- `[E-4] CEO GO 待ち: Phase1 SessionStart hook 有効化`

### 3.4 配達確認（消費確認）の定義

「届いた通知が消費されたか」を確認するための定義。

**配達確認とは:** 送信した通知が受信者（人間 / lane / pipeline）によって読まれ、何らかのアクションまたは ACK が発生したこと。

**確認方法の優先順位:**

1. ファイルベース ACK: 受信者が reply file を書き、そのファイルが `consumed_events:` に E番号を列挙した
2. terminal-updates.jsonl の消費者確認: pipelines.toml に登録された consumer が当該エントリを処理済みにした
3. event_ledger の done event: `shared/lib/event_ledger.py` が当該 dispatch に対する done event を記録した
4. CEO の明示応答: CEO が次のターンで関連話題に言及した

**未確認イベントのロールアップ:** terminal-updates.jsonl の未処理エントリ（consumer 未登録 or 処理待ち）は、定期的にロールアップして CEO / orchestrator に報告する。ロールアップ周期はパイプライン登録で定義する（pipeline-dispatcher のカウントベース）。

### 3.5 closed-loop 検知の定義

以下を「閉ループ破綻」として検知する。Phase 3 の script 化対象。

| 破綻パターン | 検知条件 | 修復アクション |
|---|---|---|
| 読んだが返していない | dispatch file の mtime から N turn 以上経過しているのに reply file が存在しない | orchestrator へ未返答 dispatch の一覧を通知 |
| waiting 無限増殖 | `waiting_contract` を持つ file の件数が閾値（例: 10件）を超えた | waiting 一覧をロールアップして CEO に提示 |
| E-1 なしの E-2 | 着手通知なしに完了通知が来た | 着手通知の遡及記録と警告 |
| E-3/E-4 後の沈黙 | E-3/E-4 通知から N turn 以上 CEO / orchestrator の応答がない | エスカレーション再送 |

### 3.6 送信経路の運用保証

#### 目的

lane dispatch や lane 起こしに使う送信経路を 1 本化し、submit 漏れを機械的に防ぐ。  
根拠: 正しい送信経路 `cmux_file_signal.py --verify-submit` が memory (feedback) に書いてあるだけで機械強制されておらず、raw `cmux send "...\n"` を使った submit 漏れ事故が実地で発生した [事実: absorbed session note 2026-05-22夜 / send-path guarantee summary]。

#### 既定経路

lane dispatch および lane 起こし (他 surface への処理依頼・通知・ACK) は、以下を既定経路とする。

```
python3 shared/scripts/cmux_file_signal.py \
  --message-file <packet_path> \
  --workspace <ws> \
  --surface <surface> \
  --path-only \
  --verify-submit
```

`--path-only` はパケット本文を流さずパス 1 行のみ送信する [事実: `feedback_cmux_path_only_no_helper`]。  
`--verify-submit` は送信後に `verify_submit state=done status=OK` が返るまでリトライする [事実: `feedback_cmux_wrapper_verify_submit_standard`]。

#### raw `cmux send` の許容範囲

raw `cmux send` (cmux CLI 直叩き) は以下の場合にのみ使用を許容する。それ以外は既定経路を使う。

| 許容ケース | 判定軸 | 例 |
|---|---|---|
| 同一 pane の短い状態確認 | 改行なし / submit 意図なし | `cmux send "status?"` (改行なし / Enter を意図しない) |
| emergency | surface が応答せず既定経路が実行できない緊急状態 | cmux_file_signal 自体が失敗している場合 |
| ユーザー明示 | CEO が明示的に raw send を指示した turn | CEO「直接 send して」 |

**重要:** 改行付き (`\n` / `$'\n'` / Enter キー相当) の raw `cmux send` は submit 意図の操作と見なす。上記許容ケースを満たさない限り route_failure 扱いとする。

#### 送信後確認の必須化

submit 意図の送信を行った場合、以下のいずれかを必ず実行する。

1. **verify-submit 確認**: `--verify-submit` オプション経由であれば、stdout に `verify_submit state=done status=OK retries_used=N` が出力されることを確認する。
2. **read-screen 確認**: raw send を使用した場合は、直後に `cmux read-screen` を実行し、相手 surface が送信内容を受け取り処理を開始したことを目視確認する。

**確認なき submit 意図送信 = route_failure 扱い**

`route_failure` の定義: 保証仕様が要求する手順を省略して送信した操作。route_failure が発生した場合は次の対応を行う。
- 当該 turn 内に `route_failure: send_path_unconfirmed` として記録する。
- 可能であれば再送を試みる (既定経路を使い、同一 packet を再送)。
- 再送不可の場合は E-3 (詰まり) イベントとして通知する。

#### 改行付き送信と改行なし送信の区別

運用上の判定軸として以下を定義する。

| 送信種別 | 定義 | 扱い |
|---|---|---|
| **submit 意図の送信** | 改行 (`\n` / `$'\n'` / Enter) を末尾に含む送信。相手 surface での即時処理開始を意図する | 既定経路 (cmux_file_signal --verify-submit) 必須 |
| **状態確認の送信** | 改行を含まない送信。相手 surface の応答待ちや短い ping を意図する | raw `cmux send` 許容 / ただし用途を明示する |

Phase 3 の PreToolUse hook draft はこの区別を検知ロジックの主軸とする (draft: `phase3-send-path-guard.draft.sh`)。

#### Phase5 pointer

cmux 0.64.7 のネイティブ `workspace.prompt_submit` method を取り込めば、submit を socket レベルで保証できる。Phase 5 (shared 最適化) での検討対象として予約する [事実: absorbed send-path guarantee note / operator-local shared 未取込]。

---

## 4. 状態 SSOT

### 4.1 原則

**pane / workspace / surface の「生きた状態」の正本は cmux 自身である。**

ローカルファイル（lane-registry.yaml 等）は「名前解決ヒント」と「学習データ」の役割のみ持つ。live state を持たない。

### 4.2 役割の分離

| データ種別 | 正本 | ローカルファイルの役割 |
|---|---|---|
| pane が存在するか / 生きているか | cmux read-screen / cmux tree の実測結果 | キャッシュ不可。毎回実測 |
| workspace に surface が attach されているか | cmux surface.list 等の実測 | キャッシュ不可。毎回実測 |
| surface の role（development / lab 等） | cmux の surface メタデータ | lane-registry.yaml は「過去のマッピング履歴」として補助参照可 |
| lane の名前と function の定義 | lane-registry.yaml | これは静的定義であり、ここは正本 |
| 過去の名前解決パターン / 解決履歴 | ローカルの学習データ（cache ファイル等） | 正本ではなく参考。実測と矛盾したら実測優先 |

### 4.3 操作上のルール

1. **live state は実測で取る:** cmux surface / pane の状態を判断する際、ローカルファイルの記述だけで判断しない。必ず cmux の実測を先に行う。
2. **ローカルは名前解決のヒントにとどめる:** lane-registry.yaml が surface ID と lane 名の対応を持っていても、その surface が今も生きているかは cmux で確認する。
3. **乖離を検知する:** ローカルの静的 registry と cmux の live tree が乖離した場合、ローカルを更新するのではなく、乖離を lint として報告する。乖離の修復はオペレーターが判断する。
4. **学習データは蓄積してよいが、正本扱いしない:** 過去の名前解決履歴（「development surface は ws:A の surface:3 だった」等）はキャッシュとして蓄積できる。ただし、次回の実測と矛盾したら実測を優先し、学習データを更新する。

### 4.4 実装上の制約

現状 [事実: 元 packet §Phase 4 / lane-registry.yaml]: lane-registry.yaml と cmux live tree の二重管理が存在し、自動同期がない。本章はその解消に向けた原則定義であり、Phase 4 ADR の参照正本とする。Phase 4 では以下を実施する（ADR 起票後に有効化）:

- 原則を ADR として正式化する
- registry と live tree の乖離を検知する軽量 lint を追加する
- lane-registry.yaml の role を「静的な意味マッピング」に限定し、live state フィールドを持たせない

---

## 5. 検索・再利用保証（設計原則確定 / MVP 実装フェーズ）

### 5.1 中核原則

> **蒸留可能性は「強制点の実在」で決まる。tool 境界 or 観測可能 artifact が無いルールは doc に留め、"untrust だから hard 化" を全ルールに一律適用しない。**

この原則は、「全ルールを hook で強制すべき」という再提案ループを恒久的に閉じるための上位定義である。強制の有無は優先度ではなく「強制できる物理的な境界が実在するか」で決まる。

### 5.2 ルールの class 分類

FDE の検索・再利用に関わる 11 メソッドを、強制点の種類によって以下 4 class に分類する。

| class | 定義 | 蒸留先 | 該当メソッド |
|---|---|---|---|
| **A: tool 境界あり / 不可逆** | PreToolUse で物理 block 可 | hook（block 可） | #4 外部送信（send-path-guard 実装済） |
| **B: 事後 artifact あり** | 違反が観測可能な成果物を残す | detector / lint（warn + ledger） | #5 prior-art（新規 shared/lib × registry 未登録）、#9 packet 必須 field |
| **C: 局所 soft 助言が ROI 高** | reasoning 内部だが nudge 価値あり | advisory（条件付き / programmatic 経路のみ wrapper） | #1 decompose、#2 grep/RAG、#3 thin-source |
| **D: doc 据え置き（蒸留しない）** | 強制点なし + ROI 低。意図的に固定形にしない | doc のみ（決定を記録し再提案を止める） | #6 web technique、#7 main-thread-check、#10 delegation、#11 layer 分離 |

**補足:**

- **Class C は対話 Claude に対して hard 化できない**。検索ルーティングの判断は reasoning 内部で完結し、tool 呼び出し前に決まるため chokepoint を作れない。価値が出るのは agent / script が検索を programmatic に発行する時のみ（その時 import すれば on-path）。対話用途では advisory 止まりと明記する。
- **Class D は「やらない」ことが設計判断**。理由（強制点なし + ROI 低）を本章に記録し、将来 session での蒸留再提案を閉じる。D 群（#6 / #7 / #10 / #11）を hook 化することは意図的に保留した決定であり、再提案は本章を参照して却下する。

### 5.3 Class A: #4 外部送信の block 昇格条件

`send-path-guard.sh` は既に warn + `SEND_PATH_GUARD_MODE=block` 切替を実装済みである [事実: `~/.claude/hooks/scripts/send-path-guard.sh`]。block 昇格は以下の手順に従う。

**昇格条件（axis-registry の Shadow ルール準拠）:**

1. Shadow フェーズで 10 件以上の「検知したが block しなかった（Shadow OK）」イベントを記録する。
2. 記録期間中に false-positive（正当な送信を誤検知）が 0 件であることを確認する。
3. CEO GO を取得する（Type1 相当: hook / settings / auth 変更のため）。
4. `SEND_PATH_GUARD_MODE=block` を `~/.claude/settings.json` の env に設定し有効化する。

**昇格前の確認コマンド（dry-run）:**

```bash
SEND_PATH_GUARD_MODE=block bash ~/.claude/hooks/scripts/send-path-guard.sh
```

改行付き raw send が `exit 2` になることを確認してから昇格する。

### 5.4 Class B: prior-art 事後 detector

`shared/lib/` 配下の新規 `.py` が `ssot-registry.yaml` に `owner_file` 登録されていない場合、`fde_lint.py` が lint issue として報告する（warn 相当）。

- 検出関数: `fde_lint.lint_shared_lib_registry()`
- 対象: `shared/lib/*.py`（`__init__.py` / `test_*.py` 除く）
- 登録先: `ssot-registry.yaml` の `topics.<id>.owner_file`

新規 `shared/lib` スクリプトを追加した際は、同 PR / 同 commit で registry entry を追加することを義務とする。`fde_lint.py` が自動検出するため、GREEN 維持が登録完了の証跡となる。

---

## 付録: 各 Phase と本章の対応

| Phase | 参照する章 | Type1 要否 | 現在の状態 |
|---|---|---|---|
| Phase 1: 起動保証機械化 | §1 起動保証 | enforce 昇格は要 (CEO GO 待ち) | 検知レイヤー稼働中（`fde-boot-gate.sh` を SessionStart に登録済 / 宣言ベース・block しない）。enforce(block) 昇格のみ未 [事実: operator-local settings 2026-05-27] |
| Phase 2: 出力モード定義・detector | §2 出力モード | enforce 昇格は要 (CEO GO 待ち) | 検知レイヤー稼働中（`cloud-code-output-gate.sh` 登録済 / `symbol-detector` は DRY_RUN=1）。enforce 昇格のみ未 [事実: operator-local settings 2026-05-27] |
| Phase 3: 通知信頼性実装 | §3 通知保証 | 不要 | 実装可 |
| Phase 4: cmux 状態 SSOT 原則確定 | §4 状態 SSOT | 要 (Codex-main review) | 設計確定 |
| Phase 5: shared cmux 最適化 | §4 状態 SSOT（参考） | 不要（設計判断除く） | 未着手 |
| Phase 6: 検索・再利用保証（MVP） | §5 検索・再利用保証 | 一部要（Class A 昇格） | Class B detector 実装済。Class A (#4 送信) は `send-path-guard.sh` warn 稼働中だが block 昇格は未達（Shadow 7/10件 + false-positive 1件 [git commit メッセージ文字列の誤検知] → grep 改善が昇格前提）[事実: operator-local ledger 2026-05-27] |


