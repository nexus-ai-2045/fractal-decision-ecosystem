---
title: FDE v1 Browser AI Review Synthesis
type: report
status: reflected
created: 2026-05-12
owner: codex-main
tags: [fde, browser-ai-review, synthesis, ssot]
source:
  - external-ai-route-registry.md
  - root-router.md
  - core.md
note: private report / inbox path は公開しない。要点は本 file に absorb 済み。
---

# FDE v1 browser AI review 統合

## route

正式レビュー名は `browser AI review` / `browser AI debut` とする。`multi-AI` は実装名として残っていても、運用語としては使わない。

| provider | workspace / surface | 状態 | 採用に使ったか |
|---|---|---|---|
| Claude | Research / surface:34 | 回答あり | yes |
| Grok | Research / surface:33 | 回答あり | yes |
| ChatGPT | Research / surface:32 | 未回答 / thinking (2026-05-12 再回収でも新規回答なし) | no |
| Gemini | Research / surface:30 | 未回答 / UI 上は分析中 (2026-05-12 再回収でも新規回答なし) | no |
| ChatGPT | Content / surface:24 | 先行回答あり | yes, fallback evidence |
| Grok | Main / Top / surface:110 | 添付あり回答あり (2026-05-13) | yes, final external evidence |

## 採用済み修正

| 指摘 | source | 反映先 |
|---|---|---|
| packet validation が必要 | ChatGPT fallback | `dependency-registry:fde-v1-draft-report` §1 |
| `user-stop` と validation failure を分ける | ChatGPT fallback / Codex correction | §1 / §4 |
| routing tree と exception priority の二重語彙を統一する | Claude / ChatGPT fallback | §3 / §4 |
| single writer を明記する | Claude | §0 |
| closure_rule の閉じ方を明記する | Claude | §1 / §2 |
| 3x3-exhausted は人間判断へ 1 問に圧縮する | Claude / Grok | §4 / §5 |
| self-growing loop に human gate を入れる | ChatGPT fallback / Claude | §8 |
| verify 失敗時と無限ループ防止を入れる | Grok | §8 |
| adopted 後の quarantine / rollback を入れる | Claude | §8 / §9 |
| browser AI の聞き先は Research project 面を既定にする | CEO correction / cmux tree 実測 | `external-ai-route-registry.md` |
| `orchestration_required: yes` の runtime enforcement を物理 block にする | Grok attached review / local smoke | `shared/scripts/fde_lint.py --packet-file` |
| `codex_main_role` 欠落も adoption block に含める | Grok attached review / local diff | `core.md` §2 |
| `fde_lint.py` を CI に常駐させる | Gemini post-Grok review | `.github/workflows/fde-lint.yml` |
| CMUX browser 添付で Desktop staging だけに依存せず、file dialog から対象 folder を開いて全 file 選択する | Grok attached review follow-up / user correction | `shared/scripts/cmux_browser_attach_file.py --folder` / `cmux_ops.py review-attach --folder` |

## 保留

| 指摘 | 理由 |
|---|---|
| validation failure を `user-stop` にする | `user-stop` は CEO 明示停止だけに限定するため、`unknown-or-conflict` に落とした |
| 全 routing failure を `human-stop` と呼ぶ | 用語増加で drift するため、既存 `unknown-or-conflict` に寄せた |
| ChatGPT / Gemini Research 面の回答待ち | 再回収しても新規回答なし。待ちで本体修正を止めない |

## 2026-05-13 Attached Grok Verdict

- [事実: absorbed Grok attached review / 2026-05-13] Grok は添付ファイル群を読んだ後、`verdict: ready` / `adopt_now: yes` / `still_open_unknowns: なし` / `needed_files: なし` と回答。
- [事実: absorbed lint contract] `orchestration_required: yes` の runtime packet は `precheck` / `delegate_plan` / `codex_main_role` / `return_to` / `route_mode` / `budget` 欠落時に lint error になる。
- [事実: absorbed attach follow-up] Grok follow-up の「添付失敗そのものを実装レベルで閉じる」指摘を受け、folder 選択 / select-all 経路を追加した。
- [事実: absorbed local smoke] operator-local wrapper tests は当時 pass。公開 package はその wrapper 実体を同梱しない。
- [事実: absorbed Gemini follow-up text] Gemini follow-up は `verdict: ready` と回答。これは wrapper 実装差分に対する本文レビューとして扱い、file-attached review 完了証跡にはしない。
- [ユーザー指摘: 2026-05-13] Gemini file-attached review は未完了。wrapper出力や本文回答だけを file-attached completion として扱わない。

## 2026-05-13 Gemini Post-Grok Verdict

- [事実: `cmux browser --surface surface:111 get text --selector body`] Gemini は post-Grok 実装差分に `verdict: ready` と回答。
- [事実: `cmux browser --surface surface:111 get text --selector body`] `absorbed_diff` は `codex_main_role` 必須化 / lint 組み込み / Grok review reflected 更新。
- [事実: `cmux browser --surface surface:111 get text --selector body`] `missing_diff: なし` / `must_patch_before_adopt: なし` / `needed_files: なし` / `enough_context: yes`。
- [事実: `cmux browser --surface surface:111 get text --selector body`] `operational_guarantee` は CI への `fde_lint.py` 常駐。これは `.github/workflows/fde-lint.yml` へ反映。
- [推測] `route_authority` 無効時の CEO 承認フォールバック自動化は Type1 提案候補。既存 `root-router.md` の `type1-or-external` / `decision-needed` と重なるため、今は proposal-only とし追加実装しない。

## 2026-05-13 Gemini Attachment Correction

- [ユーザー指摘: 2026-05-13] Gemini の file-attached review は未完了。
- [事実: local note] Gemini から取得済みの `ready` は、本文/evidence digest route または実装差分レビューとして扱う。FDE folder 添付が成功し、添付内容を Gemini が読んだことの証跡とは分ける。
- [判断] Gemini file-attached review は `external_review_state: held`。次に進める時は、添付chip / attached file list / Gemini回答内の attachment_read 相当を delivery evidence に含める。

## 現在の判定

判定: `ready -> reflected`

FDE v1 draft は、browser AI review で出た重大穴を反映済み。2026-05-13 の Grok 添付レビューでは runtime enforcement まで含めて `ready` 判定。現行正本 `root-router.md` は v1 に置換済み。


