# FDE Decisions

FDE の repo-local ADR 置き場。

## ルール

- ADR は `decisions/ADR-NNNN-short-title.md` 形式で保存する。
- 次番号は `python scripts\adr_next.py` で確認する。
- 採用判断、採番ルール、公開境界、長期運用に残す決定をここへ置く。
- ADR は local evidence であり、public release、GitHub visibility 変更、外部送信、特許出願の承認ではない。

## 採用済みADR

| ADR | 決定 | レビュー観点 |
|---|---|---|
| [ADR-0001-development-card-adr-numbering.md](ADR-0001-development-card-adr-numbering.md) | 開発カード、ADR採番、local evidence の扱い | 実装判断と運用カード |
| [ADR-0002-product-creative-review-path.md](ADR-0002-product-creative-review-path.md) | Product / Creative review path | 全体デザイン、視覚入口、公開境界 |
| [ADR-0003-ai-contact-safety-contract.md](ADR-0003-ai-contact-safety-contract.md) | AI contact safety contract | AI同士のcontactをFDE packet / consent / evidence / closureへ戻す抽象契約 |
| [ADR-0004-team-formation-orchestration-gate.md](ADR-0004-team-formation-orchestration-gate.md) | Team Formation / Orchestration Gate | 意思決定に必要なteam creator、delegate配役、return contract、adoption gate |
| [ADR-0005-public-env-independent-pointers.md](ADR-0005-public-env-independent-pointers.md) | Public package の pointer 環境非依存化 | capability key / absorbed / operator-local-adapter。物理 path 非掲載 |
