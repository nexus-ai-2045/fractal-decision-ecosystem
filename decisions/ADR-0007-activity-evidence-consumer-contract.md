# ADR-0007: Activity Evidence consumer契約

- Status: accepted
- Date: 2026-08-10

## Context

Activity Log / LCSは原イベントとactor来歴を保持し、FDEは判断と承認境界を担う。producerには本文を除いた`fde.activity-evidence.v1`出力があるが、FDE側には受領契約がなく、形式driftや機微情報混入をfail-closedにできなかった。

## Decision

FDEにproducerの現行8フィールドと互換なversioned consumer schemaとread-only validatorを置く。全objectをclosedにし、本文・routing情報・個人path・secret・不正JSONを拒否する。

validator成功はcontract適合だけを示す。真実性、本人性、同意、認可、公開、FDE採用を示さない。visibility欠落時はprivateとして扱う。

## Consequences

- FDEは原文DBを複製せず、Activity Log / LCSへのpointer境界を維持できる。
- producerとのschema driftはversion更新とcross-repo確認が必要になる。
- `content_hash`は正規化済み重複判定hashであり、完全性保証には使わない。
- 実データ取込、自動採用、producer変更、外部送信はこの決定に含めない。

## Human review gate

人間承認はGitHubのレビュー状態を正本にせず、対象treeに結び付いた署名receiptで検証する。FDEが採用する公開鍵は `keys/fde-human-review-nexus_ai.pub`（指紋 `SHA256:lnzqUQWKfJisG+fpkiwNj0Sx/oJnFDOYo27MPmnn/WU`）である。秘密鍵はリポジトリへ保存しない。署名、対象tree、receipt hashのいずれかが検証できない場合は `unknown` とし、自動採用しない。

このADRの採用は、外部送信、公開、release、mergeの追加承認を意味しない。
