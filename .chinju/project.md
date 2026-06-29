# Project Context

Project ID: `fde`

## Purpose

Fractal Decision Ecosystem（FDE）は、AI支援の判断・実装・公開境界を fact gate、scope route、publication containment、done verification closeout で扱う private-first operating package。

この repository は、private運用の正本、sanitized public-kernel candidate、rights / patent / publication gate、local MVP gate を同じ package 内で保証する。

## Users

- Owner / operator: FDEを運用し、公開・特許・権利判断を承認する人間。
- Codex / AI agents: local-firstで実装・検証・handoffを行うが、外部writeや公開判断は別承認まで止める。
- Future reviewer: `public-kernel/`、rights notice、MVP gate の evidence を読む。

## Important Constraints

- Repository visibility is private by default.
- Public release / external send / GitHub visibility change / patent filing / connector submit requires explicit current-conversation approval.
- `Patent Pending` / `特許出願中` wording is allowed only after an application is actually filed.
- External issue trackers are not required for local FDE operation.
- `python scripts\mvp_gate_check.py` is the top-level private MVP gate.
- `python scripts\public_ready_check.py` and `python scripts\pre_publication_gate_check.py --json` must remain green before publication discussion resumes.
