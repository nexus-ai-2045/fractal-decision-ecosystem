# ADR-0006: Orchestration / Spark operational gate

Status: accepted
Date: 2026-07-19

## Context

FDE は `operating-card.md` / `core.md` / `search-orchestration.md` / ADR-0004 で、
`orchestration_required`、Team Formation、`GPT-5.3-Codex-Spark` / `spark_candidate` /
`spark_delegate` を運用契約として定義しています。

しかし public package では、これらの語彙が docs に存在するだけで、
MVP gate / workflow / operational guarantee から機械検証されていませんでした。
結果として「オーケストレーション検討は常時 ON」「短い調査は Spark 候補」が
運用保証の強制チェックに入らず、再発防止が弱い状態でした。

## Decision

repo-local の `scripts/orchestration_gate_check.py` を一級 gate とする。

この gate は次を read-only で検証する。

1. docs contract  
   `core.md` / `operating-card.md` / `search-orchestration.md` / ADR-0004 / 本 ADR /
   `OPERATIONAL_GUARANTEE.md` / `ROADMAP.md` に orchestration / Spark 必須語彙があること。
2. optional packet validation (`--packet-file`)  
   - `orchestration_required` 必須  
   - `no` なら `orchestration_reason` 必須  
   - `yes` なら `delegate_plan` / `codex_main_role` / `return_to` / `precheck` /
     `route_mode` / `budget` と `team_plan` または `no_team_reason` 必須  
   - `team_plan` がある場合は ADR-0004 最小項目必須  
   - Spark 向き作業は `spark_candidate` 必須  
   - `routing_decision: spark_delegate` は Type1 / final decision / publication を持てない

`fde_workflow.yaml` の `orchestrate` state と `required_local_gates`、
`scripts/mvp_gate_check.py`、`OPERATIONAL_GUARANTEE.md` からこの gate を参照する。

## Consequences

- orchestration / Spark は「推奨」ではなく、docs + optional packet の機械 gate になる。
- Spark は軽量 delegate であり、採否・Type1・publication の権限を持たないことがテストで守られる。
- 新しい外部 Spark runtime や wrapper は追加しない。既存 docs と既存 gate パターンを再利用する。

## Alternatives Considered

| alternative | 判断 |
|---|---|
| docs 文言追加だけ | 再発防止にならないため不採用 |
| 外部 Spark API wrapper を新設 | 車輪の再発明 / 公開 package 境界超過のため不採用 |
| shared/scripts/fde_lint.py を期待する | public package に無いため不採用。repo-local gate に蒸留 |
| ADR-0004 を拡張するだけ | Team Formation と Spark ops gate の責務が混ざるため分離 |

## Non-Goals

- Spark / Codex の実ランタイム呼び出しを実装しない。
- 外部AI送信、public release、visibility 変更、credential 変更を承認しない。
- 毎回並列 dispatch を義務化しない。

## Verification

- `python3 scripts/orchestration_gate_check.py --json`
- `python3 -m pytest -q tests/test_orchestration_gate.py`
- `python3 scripts/mvp_gate_check.py`
- `python3 scripts/fde_workflow_check.py`
