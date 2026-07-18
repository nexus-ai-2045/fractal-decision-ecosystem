# ADR-0005: Public package の pointer を環境非依存にする

Status: accepted  
Date: 2026-07-18

## Context

この repository は public である。一方で本文・registry に `Documents/...`、`imported-source`、machine-local path、Obsidian / cmux 専用 path など、clone した第三者が解決できない pointer が多く残っていた。

## Decision

1. `dependency-registry.md` は物理 path 列を持たない。key は capability 名として公開し、`repo-local` / `absorbed` / `operator-local-adapter` / `withheld` / `planned` で解決クラスを示す。
2. `source-pointers.md` と入口文書は、opaque label だけで閉じず、公開解決先（repo-local file）を書く。
3. operator-local adapter が無い環境では skip / hold し、推測 path を作らない。
4. architecture drift check は private path の存在確認ではなく、capability key の掲載と path 非埋込を検証する。

## Consequences

- public clone だけで概念・gate・workflow を読める。
- 個人 workspace の便利さは失わないが、その接続情報は public registry に書き戻さない。
- historical report は absorb 済み要約として残し、元 private path は掲載しない。
