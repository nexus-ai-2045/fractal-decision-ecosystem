# ADR-0002: Product / Creative review path

Status: accepted
Date: 2026-07-01

## Context

FDE には、すでに private local MVP gate、roadmap contract、publication stop line があります。次の設計リスクは実装不足ではなく、レビューする人が「最初にどの面を見るのか」「どんなフィードバックが有効なのか」「どこから public release 承認なのか」を迷うことです。

Product Design review では、repository の中をたどる明確なユーザー導線が必要です。Creative Production review では、private implementation、rights、publication boundary を混ぜずに、public-candidate story のメッセージ階層を確認できる必要があります。

## Decision

現在の FDE package では、次の単一レビュー導線を採用します。

1. `visual.html` で product story と first-screen comprehension を見る。
2. `README.md` で source-backed explanation と file routing を見る。
3. `ROADMAP.md` で `goal / evidence / gate / owner / done_when` を見る。
4. `OPERATIONAL_GUARANTEE.md` と `MVP_STATUS.md` で private local completion を見る。
5. `PUBLIC_KERNEL_PLAN.md` と `TODO_FDE_PUBLIC_KERNEL_RIGHTS.md` で public-kernel と rights boundary を見る。

`visual.html` は concept story だけでなく、review path と stop line を直接見せます。Product / creative の変更は、レビューする人が次を答えられる状態で reviewable とみなします。

- FDE は何のためのものか。
- 最初に何を inspect すればよいか。
- 何が locally complete なのか。
- 何が public release として未承認なのか。
- どの gate がその主張を証明するのか。

## Consequences

- visual entry は読み物だけでなく review surface になります。
- Product Design feedback は、local visual entry の comprehension、hierarchy、interaction、accessibility を対象にできます。
- Creative Production feedback は、asset を launch approval と扱わずに、positioning、message clarity、public-candidate framing、asset fit を対象にできます。
- 新しい durable design decision は repo-local ADR を使い、package の一部になったら local gate に含めます。

## Alternatives Considered

| alternative | 判断 |
|---|---|
| READMEだけでレビュー導線を説明する | 視覚入口から直接レビューに入れないため不採用 |
| visual.htmlだけを更新してADRを残さない | 後続レビューで意図が消えるため不採用 |
| Product / Creative review path をADR化する | 採用 |

## Review Acceptance Criteria

レビューする人が、次を確認できる状態を合格とします。

- 初見読者がFDEの目的と最初に読む場所を説明できる。
- Product reviewer が入口、階層、次アクション、アクセシビリティリスクを指摘できる。
- Creative reviewer が公開候補の見せ方と launch approval の違いを分けられる。
- Security / publication reviewer が public release 未承認境界を確認できる。

## Non-Goals

- この ADR は publication、external sending、repository visibility changes、patent filing、announcement を承認しません。
- この ADR は新しい brand system を作りません。
- この ADR は human review を置き換えません。

## Verification

- `python scripts\adr_next.py` が次の ADR number を返します。
- `python scripts\public_ready_check.py` がこの ADR を required local documentation として確認します。
- `pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_mvp_gate.ps1` が supported local closeout gate のままです。
