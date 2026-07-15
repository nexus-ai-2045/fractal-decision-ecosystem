# FDE システム化アーキテクチャ確認

状態: local architecture check / review-ready context save
日付: 2026-07-07 JST
対象: FDE private repository operating package

このメモは、現在のFDE作業を「毎回同じように回せるシステム」にできるかを、アーキテクチャ観点で確認するための保存メモです。

## 現在の文脈

直前の closeout 状態は、`CHAT_CONTEXT_CLOSEOUT_2026-07-06.md`、`RESIDUAL_ZERO_GOAL_2026-07-05.md`、`OPERATIONAL_GUARANTEE.md` に記録済みです。

この確認の開始時点で見えていた repository context:

- 現在の branch: `main`
- local branch relation: `main...origin/main`
- latest commit: `73ed93c FDEチャットcloseoutコンテキストを保存`
- 直近の merged implementation PR:
  - PR #10: Team Formation と Residual Zero Goal
  - PR #11: AI contact safety contract と residual-zero smoke
  - PR #12: publication-boundary review packet と diff check
- 直近の closeout evidence:
  - `python -m pytest -q` -> `27 passed`
  - `scripts/run_mvp_gate.ps1` -> `FDE MVP GATE CHECK OK`
  - public-ready / pre-publication checks は public action なしで通過
  - repository visibility は private のまま維持

## アーキテクチャ結論

システム化は可能です。

正しい形は、FDE を product runtime ではなく、decision、evidence、orchestration、gate、closeout の control plane として扱うことです。LCS device app、OS-level agent、avatar、voice contact、Bluetooth、Wi-Fi、peer-to-peer contact などの隣接構想は、product layer または platform adapter 側に置きます。FDE は、それらの周囲にある判断契約と検証ゲートを持ちます。

短く言うと:

- FDE: control plane、review grammar、evidence router、gate runner、closeout recorder
- LCS / product layer: runtime、device UX、network transport、avatar / voice interface、user-facing setup、downloaded data
- Public release layer: human review packet、visibility boundary、publication approval、release-specific evidence

## 既にある部品

この repository には、反復可能な operating system にするための部品がすでにあります。

| 層 | 既存の部品 | 役割 |
|---|---|---|
| entry / dialogue | `entry -> packet -> evidence -> decision -> closure` | 曖昧な依頼を bounded decision packet に戻す |
| orchestration | Team Formation gate、`team_plan`、`delegate_plan`、`return_contract`、`adoption_gate`、`no_team_reason` | 作業を分岐するか、どう戻すかを決める |
| local quality gates | pytest、MVP gate、roadmap gate、visual HTML smoke | local regression と stale review surface を止める |
| residual-zero gates | residual-zero goal check / residual-zero contract check | implementation residue、operation residue、external/public residue を分ける |
| AI contact boundary | no-transport contact check / AI contact safety contract | 隣接product/contact構想を抽象契約に留める |
| publication boundary | pre-publication gate、public kernel diff manifest、human review packet | 公開承認ではないreview packageを作る |
| evidence / receipts | `OPERATIONAL_GUARANTEE.md`、closeout notes、PR receipts | 何を実行し、何を実行していないかを後から見えるようにする |

## 次のシステム形

次の durable form は、さらに長い prose ではなく、小さな state machine と gate bundle にするのがよいです。

推奨する到達形:

1. `fde_workflow.yaml`
   - `intake`、`scope`、`orchestrate`、`implement`、`verify`、`review_packet`、`closeout`、`external_approval_required` などの状態を定義する
   - public release、repository visibility change、credential、auth/settings、destructive operation、external sending などの blocked transition を定義する

2. `scripts/fde_operational_closeout.py`
   - accepted local gate bundle を実行する
   - implementation residue、operation residue、public/external residue、branch state、latest commit、gate results、next required human decision を JSON で出す
   - 既定は read-only check とし、public action は実行しない

3. `scripts/fde_architecture_drift_check.py`
   - docs、scripts、tests が同じ required primitives を見ているか確認する
   - gate が文書化されているのにテストされていない、またはテストされているのに文書から消えている場合に落とす

4. `scripts/fde_context_closeout.py`
   - current branch、gate evidence、merged PR receipts、stop lines から dated context note を生成する
   - chat context save を手作業の再構成にしない

5. PR / merge state model
   - stacked PR、retargeting、CI、merge receipt、local sync、post-merge verification を反復可能な workflow として扱う
   - publish / release / visibility は automatic path の外に置く

## 固定する境界

- local gate pass は publication approval ではない
- GitHub visibility change は自動化しない
- public release、broad sharing、submission、posting、launch は現在の会話での明示的な人間承認が必要
- delegate は evidence収集、log圧縮、option比較、bounded check はできるが、final decision、publication approval、credential、auth/settings、destructive operation、external sending は持たない
- LCS / product runtime 構想は、FDE repository が別途 product-runtime charter を受けない限り adapter scope に置く

## リスク

| リスク | なぜ問題か | 推奨control |
|---|---|---|
| control plane が product runtime を吸収する | FDE が device / app / network UX まで背負って重くなる | FDE は contracts、gates、adapters 周辺に留める |
| automation が publication boundary を越える | closeout runner が release runner に化ける | read-only default、external-action blocklist、human approval stop |
| prose-only closeout が drift する | manual note は branch、PR、gate state を落としやすい | JSON-backed closeout evidence を生成する |
| stacked PR state が暗黙化する | retarget / merge / receipt が監査しにくくなる | explicit PR state model と post-merge receipt check を追加する |
| gate / document mismatch | gate が docs だけ、または tests だけに残る | architecture drift check を追加する |

## 推奨実装slice

採用するなら、次の順で実装します。

1. machine-readable workflow manifest と drift check を追加する
2. external action を止めたまま JSON を出す operational closeout runner を追加する
3. context closeout generator と PR receipt state model を追加する

この順序が効く理由は、今後の「残務ゼロ」「実装完了」「運用保証」回答を、FDEを隣接product runtimeへ膨らませずに、毎回同じ証跡で閉じられるようにするためです。

## レビュー回答

この仕組みは機械化できます。

現在のrepoは concept only ではありません。すでに gates、tests、review packets、residual-zero semantics、post-merge receipts があります。足りないのは、もう一つの設計文書ではなく、同じ checks を毎回走らせ、結果を一貫した closeout artifact に記録する、薄い read-only の machine-readable orchestration layer です。

この確認のclose condition:

- このcontext noteがrepo内に存在する
- 追加後もlocal testsとMVP gateが通る
- public action、external send、repository visibility changeを実行しない

## 2026-07-15 Closed-Loop Implementation Context

- repo-local machine SSOT: `fde_workflow.yaml` v2
- workspace operating authority: `Documents/brain/fde/operating-card.md`
- external detail authorities: `dependency-registry.md` の measurement / command smoke / runtime guarantee / low-PDCA pointers
- strict validator: comment、duplicate key、unknown key、invalid syntax、state/transition/evidence/gate driftをfail-closedで拒否
- closeout: worktree、upstream、ahead/behind、gate healthを分離し、`--require-delivery-ready`時は未commit・未pushをエラーにする
- current visibility: public。古いprivate表記はhistorical evidenceでありcurrent SSOTではない
- context resume source: `scripts/fde_operational_closeout.py --json --require-delivery-ready` のfull HEAD、gate receipt、residue、`context_to_preserve`、`resume_checks`
