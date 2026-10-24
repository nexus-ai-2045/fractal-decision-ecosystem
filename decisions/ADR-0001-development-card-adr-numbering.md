# ADR-0001: 開発カード、ADR、自動採番の採用

Status: accepted

Date: 2026-06-22

## Context / 背景

FDE では、繰り返し使う開発判断を local evidence として残す必要がある。ただし、外部 issue tracking、公開、repository visibility 変更を必須条件にしてはいけない。

既存の `ai-development-living-harness.md` は開発カードの運用テンプレートとして使える。足りなかったのは、repo-local ADR の置き場と、次の ADR 番号を一貫して割り当てる軽量な方法だった。

## Decision / 決定

FDE の local operation として次を採用する。

- `ai-development-living-harness.md` の AI開発標準カードを、実装単位の標準カードとして使う。
- repo-local ADR は `decisions/` に保存する。
- ADR filename は `ADR-NNNN-short-title.md` 形式にする。
- 次の ADR 番号は `python scripts\adr_next.py` で確認する。
- 外部 issue / card system は optional かつ approval-gated のままにする。local ADR の採用は、外部 tracker、PR、public release、visibility 変更、patent filing の承認を意味しない。

## Consequences / 影響

- 小さい判断は development card または commit message に残してよい。
- repo の durable behavior を定義する判断は ADR にする。
- MVP gate が ADR lane と auto-numbering helper を確認するため、将来の regression を検出できる。

## Verification / 検証

- `python scripts\adr_next.py` が次の ADR filename を返す。
- `python scripts\mvp_gate_check.py` が ADR と auto-numbering file を tracked-file gate に含める。
