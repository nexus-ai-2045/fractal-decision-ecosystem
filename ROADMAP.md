# FDE ロードマップ

状態: 初回実装サイクル準備完了 / ローカル実装残務ゼロ

外部 action: なし

このロードマップは、公開済みの Fractal Decision Ecosystem（FDE）repository（`nexus-ai-2045/fractal-decision-ecosystem`）内で実装サイクルを進めるための作業正本です。外部送信、announcement、patent filing、さらなる repository visibility 変更、public release の宣言は、このロードマップでは承認しません。

## 方針

- roadmap は機能一覧ではなく、`goal / evidence / gate / owner / done_when` を持つ運用 contract として扱う。
- Now / Next / Future は release plan ではなく、現在の優先度、次の検証、将来候補を分けるために使う。
- merge は人間目視レビュー後にだけ行う。
- human review 前のPRは draft または review待ちとして扱い、公開・visibility 変更へ進めない。

## 完成図

FDE の完成図は、次の3つが揃った状態です。

| 層 | 完成状態 | 確認方法 |
|---|---|---|
| 判断制御面 | 依頼を `entry -> packet -> evidence -> decision -> closure` に戻せる | `operating-card.md` / `dialogue-protocol.md` / `axis-registry.md` |
| ローカル運用面 | 実装・ADR・README・roadmap・tests・gate が同期している | pytest、MVP gate、roadmap gate、post-merge receipt |
| 公開境界面 | 公開候補と private package が分かれ、明示承認まで外へ出ない | pre-publication gate、public-kernel diff、human review packet |

今の repository package は、判断制御面とローカル運用面を閉じています。repository 本体は公開済みですが、公開境界面は、外部送信・announcement・patent filing・さらなる visibility 変更・public release の宣言を未承認のまま止めるところまでが完了状態です。

## 可視化マップ

レビュー時は、文字量の多い正本へ入る前に次の図で全体の位置を合わせます。

| 見たいもの | 可視化入口 | 確認すること |
|---|---|---|
| 全体構造 | `SYSTEM_OVERVIEW.md` | 判断制御面、ローカル運用面、公開境界面、隣接product adapter が混ざっていないか |
| 初見レビュー | `visual.html` | 目的、発火順、停止線、未実装ロードマップが一画面で追えるか |
| workflow | `fde_workflow.yaml` | intake から closeout までが state machine として読めるか |
| TODOと残務 | `TODO_IMPACT_EXECUTION_2026-07-01.md` | 実行済みTODO、外部承認TODO、closeout bundle が分かれているか |
| 運用保証 | `scripts/fde_operational_closeout.py --json` | implementation、operation、external/public residue が分かれているか |

## Now

| lane | goal | evidence | gate | owner | done_when |
|---|---|---|---|---|---|
| Core/Product | FDE の価値仮説と使い方を1つの入口へ束ねる | `README.md` / `operating-card.md` / `ROADMAP.md` | roadmap gate | Codex + human | 最初のPRで roadmap gate が通る |
| Team Formation / Orchestration | 意思決定に必要な分岐、役割、回収形式、採否権限を先に設計する | `search-orchestration.md` / `operating-card.md` / `decisions/ADR-0004-team-formation-orchestration-gate.md` | team formation gate | Codex + delegated reviewers | 非trivial作業で team plan または no-team reason が残る |
| UX/Product Design | 読む人が迷わず入口、境界、次アクションを見つけられるようにする | `README.md` / `visual.html` / `decisions/ADR-0002-product-creative-review-path.md` | human review | human | 目視で入口、レビュー導線、境界が確認される |
| Security | 公開・secret・visibility・LLM security の停止線を維持する | `PUBLIC_READY.md` / `SECURITY.md` / scripts | pre-publication gate | Codex | local gate が external action false で通る |
| AI/OpenAI Dev | AI実装を eval / smoke / preflight で閉じる | `tests/` / `scripts/` | pytest + mvp gate | Codex | pytest と MVP gate が通る |
| Creative/Comms | 公開候補素材と説明素材を human review 前提に分ける | `assets/` / `PUBLIC_KERNEL_PLAN.md` / `decisions/ADR-0002-product-creative-review-path.md` | publication containment gate | human | 公開前の未承認境界とレビュー観点が明記される |
| Operations | PR、review、merge の手順を外部影響ゲートつきで運用する | Git branch / PR / checks | human review before merge | Codex + human | PR作成後、merge前に人間確認が残る |

## Next

- ローカル実装残務: なし。
- Roadmap gate は `scripts/mvp_gate_check.py` に接続済み。
- 開発カード / ADR / 自動採番の採用は `decisions/ADR-0001-development-card-adr-numbering.md` に記録済み。
- Product / Creative review path は `decisions/ADR-0002-product-creative-review-path.md` に記録済み。
- AI contact safety contract は `ai-contact-safety-contract.md` と `decisions/ADR-0003-ai-contact-safety-contract.md` に記録済み。
- Team formation / orchestration は `decisions/ADR-0004-team-formation-orchestration-gate.md` に記録済み。
- MVP smoke / preflight scope review は `MVP_SCOPE_REVIEW_2026-07-02.md` に記録済み。
- Product Design / Security / Creative / OpenAI Dev の追加TDDサイクルは、次に明示された実装要求が出た場合だけ切る。
- PR / merge / public release は、このロードマップでは承認しない。必要な場合は `smoke -> preflight -> diff review -> PR -> human review -> merge` の順序を別承認で記録する。

## Future

- design system maturity、SAMM/SSDF maturity、eval-driven AI development、creative operations governance を lane 別の成熟度表へ落とす。
- device app / OS service / avatar / voice / nearby AI contact の製品仕様は FDE 本体に入れず、必要なら別 product / life-commons-system 側へ分離する。
- public kernel と private operating package の差分を、公開前チェックで機械確認できるようにする。
- human review 後の merge receipt と post-merge verification を `OPERATIONAL_GUARANTEE.md` に反映する。

## Implementation Orchestration

未実装予定は、次の lane を常時並走できる単位として扱う。ただし public release、repository visibility 変更、外部送信、patent filing、hook/settings/credential 変更は、この roadmap では実行しない。

| lane | 目的 | 主な入力 | 主な出力 | 通常ゲート |
|---|---|---|---|---|
| Core FDE | entry -> packet -> evidence -> decision -> closure を壊さず拡張する | `README.md` / `operating-card.md` / `root-router.md` | routing contract、operating card更新 | roadmap gate、MVP gate |
| Team Formation / Orchestration | 判断に必要な分岐、役割、実行順、回収条件を設計し、必要なら Team Creator として delegate を作る | `search-orchestration.md` / `operating-card.md` / `dependency-registry.md` | team_plan、delegate_plan、return_contract、adoption_gate、no_team_reason | team formation gate、roadmap gate |
| Review UX | 初見レビューで入口、境界、次アクションを迷わせない | `visual.html` / ADR-0002 / `README.md` | review path、目視レビュー観点 | Product Design review、HTML smoke |
| Safety / Security | 公開、secret、visibility、AI contact の停止線を維持する | `PUBLIC_READY.md` / `SECURITY.md` / ADR-0003 | gate、threat model、finding log | public-ready、pre-publication gate、codex-security scoped scan |
| AI Contact Contract | 隣接productの接触構想をFDEの判断契約へ戻す | `ai-contact-safety-contract.md` / ADR-0003 | identity、consent、data boundary、closure checks | pytest、MVP gate、no-transport check |
| Public Kernel / Rights | private operating package と public candidate を分ける | `PUBLIC_KERNEL_PLAN.md` / `TODO_FDE_PUBLIC_KERNEL_RIGHTS.md` / patent packet | diff manifest、review package | pre-publication gate、human review |
| Operations | PR、merge、post-merge receipt を安全に閉じる | PR、checks、merge commit | merge receipt、local sync、residual report | readiness preflight、post-merge verification |

推奨するオーケストレーション:

- FDEの意思決定は、単独判断ではなく、必要な team formation を設計することまで含む。Team Creator は外部ツール名ではなく、`task -> roles -> delegates -> return contract -> adoption gate` を作るFDE内の役割として扱う。
- まず `chat-orchestrator` で workstream を `implementation / verification / public-boundary` に分ける。
- 非trivial作業、複数surface、設計比較、smoke/preflight、レビュー回収、分岐実装は、`team_plan` または `no_team_reason` を残す。
- 変更が FDE routing、ADR、source pointer、保証語彙に触れる場合は、FDE skill と roadmap gate を先に使う。
- security、secret、public kernel、AI contact、publication boundary に触れる場合は `codex-security` または threat-model 観点を併用する。
- visual、review path、creative explanation に触れる場合は Product Design / Creative Production 観点を使う。ただし asset や説明素材は private draft として止める。
- OpenAI API、agent、eval へ進む場合は、公式docs確認、key管理、adversarial smoke、no-external-action gate を先に置く。

## Implementation Roadmap

ここから先は、ここまで出てきた未実装予定を実行順へ並べ直したもの。完了と言える範囲は、常に private repo 内の local guarantee に限定する。

### Sprint 0: Post-Merge Verification Receipt

状態: ローカル完了

目的:

merge 済み変更を、local main、remote main、PR receipt、gate evidence で再確認できる状態にする。

実装:

- #7 / #8 などの merge receipt を `OPERATIONAL_GUARANTEE.md` または closeout note に残す。
- local main と origin/main の同期状態を確認する。
- `visual.html`、ADR、README、ROADMAP のリンクが post-merge 後も壊れていないことを確認する。

スモーク:

- `git status --short --branch`
- `git log -1 --oneline`
- `python -m pytest -q`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_mvp_gate.ps1`

停止ライン:

- local main と origin/main が説明不能に diverge している。
- merge receipt が取れない。

### Sprint 1: Roadmap / Gate Drift Guard

状態: ローカル完了

目的:

未実装ロードマップが prose-only で drift しないように、roadmap gate と tests で最低限の用語を見張る。

実装:

- `scripts/roadmap_gate_check.py` に Implementation Orchestration / Implementation Roadmap の必須語を追加する。
- Future の候補が FDE本体実装か、隣接product側の実装かを明記する。
- `tests/test_public_ready.py` の roadmap gate test で落ちるようにする。

スモーク:

- `python scripts\roadmap_gate_check.py --json`
- `python -m pytest -q`
- MVP gate

停止ライン:

- Roadmap が public release、visibility 変更、patent filing の承認に読める。

### Sprint 2: AI Contact Safety Contract Hardening

状態: 次のFDE-native実装候補

目的:

AI同士の contact を、transport 実装ではなく `identity / consent / data boundary / evidence / closure` の判断契約として強化する。

実装:

- `ai-contact-safety-contract.md` に contact packet schema の候補を追加する。
- `blocked` 条件、revocation、replay protection、TTL、checksum、human approval をテストで見る。
- transport adapter を未承認のままにする check を追加する。

スモーク:

- contract text check
- pytest
- MVP gate

停止ライン:

- Wi-Fi、Bluetooth、P2P、cloud relay、external AI send を実装しようとする。

### Sprint 2.5: Team Formation / Orchestration Gate

状態: 次のFDE-native実装候補

目的:

FDEの意思決定に、必要な分岐設計、team creator、delegate配役、回収契約、採否ゲートを含める。FDEは「決めるだけ」ではなく、決めるための最小チームを設計し、結果を本線へ戻す。

実装:

- `team_plan` の最小項目を `task / roles / delegate_plan / return_contract / adoption_gate / stopline_owner` として固定する。
- `no_team_reason` を許可するが、tiny作業、tool不在、停止線、overhead過多など理由を必須にする。
- delegate は証拠、diff、smoke結果、blockerを返す補助であり、final decision、publication approval、credential/auth/settings/destructive operation は本線が保持する。
- `Team Creator` は、役割生成と回収形式を作るFDE内 role として扱い、特定外部ツール名には固定しない。

スモーク:

- roadmap gate
- pytest
- MVP gate

停止ライン:

- delegate に final decision、公開承認、secret/auth/settings/destructive operation を渡す。
- team を作ったのに return contract、採否条件、stopline owner がない。

### Sprint 3: Review UX / Visual Smoke

目的:

初見レビューで「何を見るか」「何が未承認か」「次に何を判断するか」が分かる状態をさらに強くする。

実装:

- `visual.html` のレビュー導線を、MVP gate、public kernel、AI contact contract、stop line の4観点で整理する。
- HTMLリンクスモークを追加する。
- 必要ならスクリーンショット/visual QAを private artifact として残す。

スモーク:

- link existence check
- HTML content smoke
- Product Design review checklist

停止ライン:

- visual が public approval や launch material に見える。

### Sprint 4: Public Kernel / Rights Diff Automation

目的:

private operating package と public candidate の差分を、公開前に機械確認できるようにする。

実装:

- `public-kernel/` と private root の差分 manifest を生成する。
- patent packet、rights notice、PUBLIC_READY、SECURITY、license boundary を同じ pre-publication gate で確認する。
- public package に入れてはいけない source pointer / personal path / secret pattern を検査する。

スモーク:

- `python scripts\pre_publication_gate_check.py --json`
- `python scripts\public_ready_check.py`
- secret / personal path scan

停止ライン:

- public kernel が private operating package と同一視される。
- repository visibility 変更を同時に実行しようとする。

### Sprint 5: Eval-Driven FDE Operations

状態: closed-loop workflow contract 実装済み / 会話fixture拡張は future scope

目的:

FDEの判断ルートを `goal -> evidence -> operational guarantee -> feedback -> system update` まで閉じ、会話の揺れや曖昧な依頼でも発火することを評価できるようにする。

実装:

- `fde_workflow.yaml` に goal / capability inventory / roadmap / preflight / verification layers / operational guarantee / feedback / system update の順序を固定する。
- `scripts/fde_workflow_check.py` で閉ループ順序、検証層、学習先、採用条件を機械検証する。
- 学習の更新先を `route / skill / gate / test / ssot / roadmap` に限定し、`evidence / rollback_path / adoption_gate` を必須化する。
- `publication`, `review`, `merge`, `AI contact`, `source pointer`, `residual-zero` などの会話fixtureを作る。
- expected route、required gate、stop line、final closeout の評価を作る。
- OpenAI API等を使う場合は key管理と no-external-action を先に固定する。

スモーク:

- `python3 scripts/fde_workflow_check.py`
- malformed workflow regression test
- fixture dry run
- route expectation check
- no-public-action check

停止ライン:

- eval が外部送信、credential保存、public-facing write を必要とする。

### Sprint 6: Human-Gated Publication / Filing Package

目的:

公開、GitHub public 化、patent filing など外部影響のある作業を、実行前レビュー可能な package として整える。

実装:

- README、license、SECURITY、PUBLIC_READY、rights notice、secret scan、personal path scan の証跡を束ねる。
- patent filing を行う場合の packet hash、receipt、application number の保存先を決める。
- 実行コマンド、対象repo、visibleになる内容、未review項目を事前に列挙する。

スモーク:

- pre-publication gate
- readiness preflight
- human review checklist

停止ライン:

- 明示GOなしに public release、visibility 変更、patent filing、announcement を実行しようとする。

## Stop Lines

- repository は公開済み。さらなる repository visibility 変更（再度の private 化を含む）はこのロードマップでは承認しない。
- external posting、announcement、submission、patent filing、public release の宣言はこのロードマップでは承認しない。
- merge は人間目視レビュー後の明示GOまで実行しない。
