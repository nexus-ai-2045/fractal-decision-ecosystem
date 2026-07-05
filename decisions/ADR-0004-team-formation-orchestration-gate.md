# ADR-0004: Team formation orchestration gate

Status: accepted
Date: 2026-07-05

## Context

FDE の意思決定は、単に gate を通すだけでは足りません。実際の作業では、複数surfaceの調査、設計比較、smoke / preflight、実装、レビュー回収、public boundary 確認が分岐します。

ユーザーから、FDE に orchestration や team creator が入っていないように見えるのはおかしい、意思決定に必要な分岐実行と配役設計も FDE に含まれるはずだ、という指摘がありました。

既存の `operating-card.md` と `search-orchestration.md` には orchestration の断片があります。しかし roadmap と reviewable design では、team formation が一級の gate として見えにくい状態でした。

## Decision

FDE は、意思決定の前段として Team Formation / Orchestration Gate を持ちます。

非trivialな作業では、次のどちらかを残します。

```text
team_plan
```

または

```text
no_team_reason
```

`team_plan` の最小項目は次です。

```text
task
roles
delegate_plan
return_contract
adoption_gate
stopline_owner
```

`Team Creator` は、特定の外部ツール名ではなく、FDE 内の role として扱います。この role は、必要な役割、分岐単位、delegate の返却形式、採否条件、停止線の owner を作ります。

## Consequences

- FDE は「判断するだけ」ではなく、判断に必要な最小チームを設計します。
- delegate は evidence、diff、smoke result、blocker、candidate option を返す補助です。
- final decision、publication approval、credential / auth / settings / destructive operation は main runtime が保持します。
- 小さい作業は team を作らず fast path で閉じてよいですが、`no_team_reason` を残します。
- team formation が欠けたまま複数surface、比較レビュー、広い調査、外部AI review、分岐実装へ進む場合は route failure として扱います。

## Alternatives Considered

| alternative | 判断 |
|---|---|
| orchestration を `search-orchestration.md` だけに置く | reviewable design で見えにくいため不採用 |
| 毎回必ず複数delegateを作る | overhead が大きく、tiny task に不向きなため不採用 |
| Team Creator を特定ツール名として固定する | runtime差分に弱いため不採用 |
| Team Creator を FDE role として定義する | 採用 |

## Non-Goals

- この ADR は外部AI送信、public release、repository visibility 変更、credential / auth / settings 変更、destructive operation を承認しません。
- この ADR は常に並列実行することを義務化しません。
- この ADR は delegate に final decision や publication approval を渡す決定ではありません。

## Verification

- `ROADMAP.md` が Team Formation / Orchestration を lane と sprint として持つ。
- `scripts/roadmap_gate_check.py` が Team Formation / Orchestration と ADR-0004 を required term として確認する。
- `tests/test_public_ready.py` が team formation gate の required terms を確認する。
- MVP gate が external actions false のまま通る。
