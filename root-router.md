---
title: Fractal Decision Ecosystem
type: brain
status: active
created: 2026-05-09
updated_at: 2026-05-12T15:10:00+0900
updated_by: codex-main
mode: Root Router
topic: Fractal Decision Ecosystem / root routing / self-growing protocol
active_scope: 判断・通信・実装・検索・検証・改善の root routing
next_action: 迷ったら packet 化して stay/up/down/reroute/park/exception に落とす
tags: [fde, ssot, root-router, decision, routing]
source:
  - Documents/reports/fde/2026-05-13-fde-v1-draft.md
  - browser-ai-review-synthesis.md
  - ops-best-practice-inventory.md
  - external-ai-route-registry.md
related:
  - core.md
  - data-index.md
  - lifecycle-operating-pattern.md
  - axis-registry.md
  - pattern-vocabulary.md
  - dialogue-protocol.md
  - source-pointers.md
  - visual.html
---

# Fractal Decision Ecosystem

FDE は **Fractal Decision Ecosystem** の略で、判断・通信・実装・検索・検証・改善の **root router / King of SSOT**。
全文保管庫ではない。どの入口から来ても、次の一手・保存先・owner・閉じ方を決めるために使う。

人間向け本文では初出を `Fractal Decision Ecosystem（FDE）` と展開し、略称だけで閉じない。

軽量入口:
- まず `core.md` で判断 loop を始める。
- type / catalog / pointer は `data-index.md` から辿る。
- lifecycle mini は `lifecycle-operating-pattern.md` を使う。

この file は展開版 root router / 詳細参照として維持する。毎回の起動や短い判断で全文を読む入口にはしない。

## Definition

| 語 | 意味 | 維持する性質 |
|---|---|---|
| Fractal | 会話、検索、実装、hook、起動、lane、外部AI、経営判断のどの粒度でも同じ型で使える | 入口の設計も FDE 内に含め、入口が変わっても packet / evidence / owner / closure に落ちる |
| Decision | 意思決定を、できるだけ正確かつコンパクトにする | 何を決めたか、何を決めていないか、次の一手は何かが短く残る |
| Ecosystem | 個別 rule の寄せ集めではなく、矛盾なく閉じる判断環境 | 例外、保留、更新、破棄、外部入力まで同じ世界観で扱える |

FDE に入れたものは、どこから始まっても `entry -> packet -> evidence -> decision -> closure` に戻れること。入口は外部の前処理ではなく FDE の構成要素。戻れないものは、FDE 本文に入れず pointer / report / idea に逃がす。

## 0. 原則

| 原則 | 意味 | 壊れる時 |
|---|---|---|
| 直列化 | 状態更新・正本更新・commit は単一経路に寄せる | 複数主体が同じ file / queue / 判断を書き換える |
| 構造的不可能 | 重要違反は注意喚起ではなく hook / harness / permission で防ぐ | 「気をつける」だけで再発する |
| ライフサイクル | proposed → testing → adopted / rejected / archived を持つ | todo / idea / rule が腐る |
| ビュー分離 | 人間が読む report と machine source を分ける | report が正本になり、手編集で drift する |
| 出自追跡 | source / diff / log / timestamp / generated_by を残す | 後で何が起きたか分からない |
| 人間最終判断 | AI は案と検証を出す。不可逆・外部・意味変更は人間が決める | AI が静かに世界線を書き換える |

この 6 原則は、CC運用6原則 (SSOT / CE / Detect / Type 1-2 / Verification Loop / Incremental Change) の運用展開として扱う。

運用時は、6 原則の前提として **最初に頼まれた MVP を先に閉じる**。追加依頼、途中で見つかった問題、改善案は、MVP の `done_when` に直結しない限り `side_requests` へ横置きする。横置きは放置ではなく、owner / return_to / 再浮上条件を持つ park / reroute として扱う。

commit / state-write / lifecycle-transition は FDE 単一 writer 経由だけに寄せる。それ以外の経路からの正本更新は hook / permission / review gate で止める。

## 1. 最小 packet

packet schema / field definition / required validator の正本は `core.md` §2 Minimal Packet。

root-router は routing interpretation だけを持つ。

- 必須 field 欠如は `packet-invalid` として `unknown-or-conflict` に落とす。
- `execution_mode` / `orchestration_required` / `delegate_plan` / `codex_main_role` / `return_to` は `core.md` 側の定義に従う。
- `closure_rule` は「誰が / 何を見て / どこへ記録したら閉じるか」を 1 行で書く。
- validation 失敗を `user-stop` とは呼ばない。`user-stop` は CEO の明示停止だけに使う。

## 2. Current operating goal

今のゴールは、FDE を完璧な百科事典にすることではない。上位レイヤーへ戻りながら、走らせて直せる最小の意思決定 OS にすること。

完了条件:

- 入口、責任分離、戻り道、例外、成長ループが 1 packet で説明できる。
- Cloud Code / Codex / Gemini / 外部AIの役割が FDE に戻せる。
- 実装や修正は下位 layer に降ろし、証拠付きで戻せる。
- 出戻りが起きたら、同じ議論を続けず `entry / owner / evidence / closure` のどれが欠けたかで修正する。

## 3. Layer responsibility loop

FDE は、考える場所・動かす場所・戻す場所を分ける。上位で決め、下位で試し、証拠付きで戻す。

```text
start -> decide -> dispatch/down -> run -> verify -> return/up -> absorb_or_repair
```

| layer | 責任 | やってよいこと | 戻り先 |
|---|---|---|---|
| meaning / CEO | 価値判断、Type1、採用定義、優先順位 | 決める / 止める / 問いを立て直す | FDE packet |
| FDE / router | 入口、軸、owner、closure、例外 priority | 分ける / 圧縮する / dispatch する | meaning または lane |
| lane / worker | 実装、検索、検証、調査、比較 | 小さく動かす / 証拠を残す | FDE / report |
| source / evidence | file、log、test、diff、external review | 事実を支える | packet の evidence |
| archive / quarantine | 使わないもの、危ないもの、未判定 | 退避 / 隔離 / 再浮上条件付け | lifecycle |

責任を混ぜない。worker は採用判断をしない。router は長い実装を抱えない。CEO は細部実装を抱えない。source は判断の代わりにならない。

実行中に上位の問いが変わったら `up`。実装へ落とせるなら `down`。同じ層で閉じるなら `stay`。責任者が違うなら `reroute`。

## 4. Any-start routing

入口固定ではない。CEO 発話、bug、rule、idea、検索結果、外部AIレビュー、hook failure、handoff のどこから始まってもよい。
ただし「入口が何でもよい」は「入口設計が不要」という意味ではない。入口は、対象をどの粒度・軸・責任者・閉じ方へ落とすかを決める最初の decision として扱う。

入口設計:

| entry design | 問い |
|---|---|
| detect | これは何の入口か。会話 / 検索 / 実装 / hook / 起動 / 外部AI / 経営判断のどれか |
| grain | 粒度は session / lane / file / claim / command / rule のどれか |
| axis | 最初に見る軸は owner / evidence / risk / lifecycle / placement / cost のどれか |
| contract | 何が出れば閉じるか。何が出たら上位へ戻すか |
| return_path | 迷った時にどこへ戻るか。FDE / CEO / lane / report / archive のどれか |
| pivot | 自走中の新 entry / 軌道修正か。前 entry を staged 保護し、新 entry に routing 再実行するか |

入口は増える。新しい入口を見つけた時は、本文を増やす前に `detect / grain / axis / contract / return_path` で packet 化し、既存入口で吸収できるかを見る。吸収できず、複数領域で繰り返し効く時だけ entry として昇格する。

### runtime 起動時の必読リストへの追加 (= startup entry promotion)

runtime 起動時に毎回読む必読リスト (= dependency-registry:project-claude §起動時の必読 / `dependency-registry:runtime-boot` §共通入口) への新規 entry 追加は、以下の手続きを通す。

1. **事故実証**: 該当 file を読まずに事故った実例を 1 件以上残す (= session log / decisions.md / report のいずれか)。実証なしの追加は禁止。
2. **5 条件チェック**: `axis-registry.md` §No New Surface Before Mapping の 5 条件 (= 既存 WHERE / HOW / WITHWHAT / 損失明確 / owner+target+closure) を確認し、既存 map で吸収できないことを示す。
3. **正本選択**: 入口正本は `runtime-boot-branching.md` §共通入口 とし、dependency-registry:project-claude §起動時の必読 / `dependency-registry:memory-md` §起動入口 / `dependency-registry:memory-cache` は pointer に寄せる (= drift 防止)。
4. **昇格条件**: pilot 後 10 Shadow OK で本番標準 (= 鉄板) 昇格。例外 1 件で reset (= axis-registry §Shadow OK Reset Rule)。
5. **decisions 記録**: 該当 lane の `decisions.md` に D-N として起票し、Decision / Source / Rationale / Impact を残す。

詳細 axis: `axis-registry.md` §No New Surface Before Mapping / §Shadow OK Reset Rule。

move 定義の正本は `core.md` §3 Move。

root-router では、move を「現層で閉じる / 上へ戻す / 下へ降ろす / 別軸へ送る / 保留する / 例外化する」の routing decision として解釈する。

`park` / `exception` も closure_rule を持つ。期限・再浮上条件・owner がない park は腐るので禁止。
どの move にも落ちない時は `unknown-or-conflict` に凍結し、owner / scope / evidence の不足だけを 1 問にして人間へ戻す。

## 5. First-match routing tree

迷ったら上から判定する。最初に当たった枝へ落とす。例外語彙は §6 の名前へ寄せ、tree の 1 番は §6 に渡す入口として扱う。

1. §6 exception priority に当たるか。
2. 説明だけで閉じるか → `answer-only`
3. 意味・違和感・方向が未確定か → `strategy-meaning`
4. 情報が多すぎるか → `judgment-box`
5. owner / route / stale が未確定か → `coord-router`
6. 実装・検証で閉じるか → `implementation`
7. lane 成果物か → `lane`
8. 今閉じる価値があるか → `score`
9. ないなら `park`

## 6. Exception priority

例外は tree の外に逃がさない。`user-stop` は最上位で、他の例外や routing tree で上書きしない。

```text
user-stop
> type1-or-external
> unknown-or-conflict
> emergency-repair
> collision-risk
> 3x3-exhausted
> freeze-or-budget
> normal tree
```

| exception | 条件 | 動作 |
|---|---|---|
| `user-stop` | CEO が stop / 保留 / 今やらないと言った | 自走停止 |
| `type1-or-external` | 外部送信 / 公開 / 削除 / 課金 / auth / prod / main push / global principle 変更 | CEO GO まで止める |
| `unknown-or-conflict` | source / scope / owner / safety / SSOT が不明 | fact-check / scope-routing gate |
| `emergency-repair` | 主 Outcome / 安全 / データを守れない | 最小修復だけ |
| `collision-risk` | 同じ file / DB / queue / lane を複数主体が触る | owner を 1 つに絞る |
| `3x3-exhausted` | 3 視点 x 3 レイヤーで解けない | scope / layer / owner / workspace のどれを切り直すか 1 問に圧縮し、人間判断へ上げる |
| `freeze-or-budget` | token / weekly / 維持モード / deadline が危険 | pointer 1 行で park |

## 7. 3x3 rule

通常の深掘りは最大で **3 視点 x 3 レイヤー**。

```text
3x3で収束 -> normal tree
3x3で未収束 -> exception: 3x3-exhausted
```

3x3 は「必ず 9 回やる」ではない。低コストで角度を変え、十分な確度に達したら止める。
3x3 で閉じない時は、同じ問いを続けない。`scope | layer | owner | workspace` のどれを変えるかだけを決める。

## 8. Entry / evidence / label routing

検索・Obsidian・SSOT drift・hook・起動復旧は、同じ型で閉じる。

```text
entry detect -> 3 probe -> claim split -> evidence check -> label update -> close/escalate
```

| item | ルール |
|---|---|
| entry | SSOT drift / Obsidian search / file placement / hook / boot-recovery / external wall-bounce から選ぶ |
| 3 probe | entry ごとに最大 3 本。4 本目が必要なら `3x3-exhausted` へ戻す |
| label | `事実` / `採用定義` / `事実寄り` / `推測` / `不明` / `判断` |
| search target | `不明`、`推測`、弱い `事実寄り`、source が claim を直接支えないもの |
| close | source が claim を直接支える、または採用定義として現行 rule にある |
| escalate | 判断 / Type1 / 外部 / 3 probe で閉じない不明 |

SSOT round 1 は `dependency-registry:entry-guided-fact-label` に証跡を残し、この節へ吸収済み。

## 9. Scoring

| score | bucket | 動作 |
|---:|---|---|
| 8-10 | `adopt-now` | 今採用。ただし最小 diff / pointer まで |
| 5-7 | `park-retake` | 期限付きで park |
| 3-4 | `decision-needed` | CEO / Strategy へ 1 問に圧縮 |
| 0-2 | `discard` | 棄却または archive |

score は目的で使い分ける。

| scoring | 対象 |
|---|---|
| RICE | idea / backlog |
| voice ambiguity risk | 音声誤変換・曖昧語 |
| convergence score | 今閉じるか |
| type1 risk | 影響範囲・可逆性・外部性 |

## 10. FDE filter

外部ベスプラ、GitHub trend、ローカル GitHub、公式 docs、外部AIレビューは、直接採用しない。

```text
input -> FDE 6原則 -> adopt-required / candidate / hold / reject
```

採用前に必ず見る。

| 問い | 対応原則 |
|---|---|
| 正本更新が単一経路か | 直列化 |
| hook / harness で防げるか | 構造的不可能 |
| proposed / testing / adopted があるか | ライフサイクル |
| report と source が混ざっていないか | ビュー分離 |
| diff / log / source が残るか | 出自追跡 |
| 人間判断が必要な意味変更か | 人間最終判断 |

## 11. Self-growing loop

FDE は完成後も育てる。ただし本文を膨らませない。

```text
observe -> packetize -> score -> pilot -> verify -> human_gate_if_needed -> absorb_or_quarantine_or_discard
```

| phase | ルール |
|---|---|
| observe | drift / blocker / repeated correction を拾う |
| packetize | 最小 packet にする |
| score | adopt-now / park-retake / decision-needed / discard |
| pilot | shadow / 1 lane / 1 command / 1 rule で試す |
| verify | diff / log / test / review で確認。失敗時は 1 回だけ repair、再失敗なら quarantine / discard |
| human_gate_if_needed | Type1 / 外部 / root routing / 意味変更は CEO GO まで止める |
| absorb | 本文は短く、詳細は pointer / registry へ |
| quarantine | adopted 後に害が出た rule を一時隔離し、rejected / archived / repair へ分ける |

同じ packet は `pilot -> verify -> repair` を 2 周以上回さない。2 周目で閉じないものは `3x3-exhausted` か `decision-needed` に戻す。

成長ループは全レイヤーで回す。会話、検索、実装、hook、起動、lane、外部AI、経営判断のどこでも、内部 feedback と外部監査を受け、採用 / 保留 / 棄却 / 隔離へ戻す。

```text
inside feedback -> outside audit -> localize -> pilot -> verify -> absorb_or_quarantine_or_discard
```

FDE は閉じた経営として自分の判断系を持つ。ただし外部AI、Web、OSS、実運用 log、ユーザー違和感を入力として受け続ける。外に開き、採用判断は内側で閉じる。

吸収条件:

- 同型の問題が 2 回以上起きた。
- source / detector / repair path がある。
- 本文に入れると毎回の判断が明らかに良くなる。
- verify / smoke / browser AI review のうち、目的に合う根拠が 1 つ以上ある。
- 1 行で書けない場合は pointer に逃がす。

## 12. Update rule

FDE 本文を更新してよい時。ただしすべて source / detector / repair path / rollback を持つこと。

- root routing の意味が変わった。
- 例外 priority が変わった。
- 新しい軸が複数領域に効くと実証された。
- browser AI review / local smoke / 実運用 log のいずれかで採用妥当と確認された。

更新してはいけない時:

- 単発の思いつき。
- 特定 lane だけの手順。
- 長い説明や議論ログ。
- source / detector / repair path がない。

更新時は次を残す。

```text
changed:
why:
source:
diff:
verification:
rollback:
```

browser AI review は `external-ai-route-registry.md` に従う。設計レビューは `リサーチ` の project 面を既定にし、新規 home は fallback とする。

## 13. Pointers

| 用途 | file |
|---|---|
| packet / move core | `core.md` |
| type / catalog / pointer index | `data-index.md` |
| dependency registry | `dependency-registry.md` |
| 詳細軸 | `axis-registry.md` |
| pattern vocabulary | `pattern-vocabulary.md` |
| dialogue protocol | `dialogue-protocol.md` |
| source pointers | `source-pointers.md` |
| external references | `external-references.md` |
| lifecycle mini | `lifecycle-operating-pattern.md` |
| search orchestration | `search-orchestration.md` |
| visual | `visual.html` |
| browser AI route | `external-ai-route-registry.md` |
| lane communication | `dependency-registry:lane-communication` |
| fact / scope / voice gate | `dependency-registry:fact-gate` / `dependency-registry:scope-gate` / `dependency-registry:voice-guard` |

本文は root router だけを持つ。詳細は pointer へ逃がす。

