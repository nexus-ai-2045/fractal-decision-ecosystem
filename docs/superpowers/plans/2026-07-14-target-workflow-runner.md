# FDE Target Workflow Runner Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** FDEの既存state/gateを再利用し、対象repo固有の検証コマンドを再開可能・metadata-onlyに実行してPR承認点まで導く薄いrunnerを追加する。
**Architecture:** FDEは制御面だけを持ち、対象repoのmanifestがコマンドとtimeoutを宣言する。runnerはallowlisted argv、状態receipt、lock、resume/run-until-gateを提供し、PR作成・merge・公開・外部送信は実行能力に含めない。
**Tech Stack:** Python stdlib、JSON、pytest、既存FDE gate。

---

### Task 1: target workflow contract

**Files:**
- Create: `schemas/fde_target_workflow.v1.schema.json`
- Create: `examples/dcb_target_workflow.json`
- Create: `tests/test_target_workflow_runner.py`

- [ ] RED: schema/version、repo root、argv-only checks、timeout、approval gate、禁止actionをtestする。
- [ ] DCB既存のpytest/ops/repo-goal/PR readinessを参照するexample manifestを追加する。
- [ ] PR create、merge、visibility、release、sendがmanifest commandに入る場合は拒否する契約を固定する。

### Task 2: resumable runner

**Files:**
- Create: `scripts/fde_target_workflow.py`
- Modify: `fde_workflow.yaml`
- Modify: `scripts/fde_workflow_check.py`
- Modify: `tests/test_target_workflow_runner.py`

- [ ] RED: `status`、`run --until review_packet`、成功receipt、失敗停止、timeout、lock、resume、本文/secret/path非露出をtestする。
- [ ] subprocessをshellなし・UTF-8・bounded timeoutで実行し、receiptはcheck名、exit、duration、digestだけ保存する。
- [ ] local verification後は`human_review_required`で必ず停止する。
- [ ] focused testと全pytestをGREENにする。

### Task 3: closeout統合とPR readiness

- [ ] runner receiptを`fde_operational_closeout.py`が読める形で集約し、implementation/operation/external residueを分離する。
- [ ] `run_mvp_gate.ps1`、全pytest、workflow/drift/publication gatesをfresh実行する。
- [ ] spec、品質、security diff reviewを通す。
- [ ] 1目的のcommitとdraft PRを作成し、人間目視レビュー待ちで停止する。mergeは行わない。
