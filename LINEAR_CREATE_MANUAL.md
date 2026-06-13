# Manual Linear Issue Creation

Status: optional。Linear を使う場合だけ手動作成 ready。

これは connector を使わない fallback 手順。Linear は FDE 運用保証の必須条件ではない。Codex は、外部 write action への別途明示承認なしに、この repo から Linear issue を作成・submit しない。

## Copy-Paste Source

`LINEAR_EXPORT.md` を issue packet として使う。

Linear を使う場合の手順:

1. Linear で新規 issue を手動作成する。
2. `LINEAR_EXPORT.md` の title を使う。
3. `LINEAR_EXPORT.md` の全文を issue description に貼る。
4. 可能なら suggested priority / project / assignee / labels を設定する。
5. 作成後、Linear issue ID と URL を `LINEAR_ISSUE_RECORD.md` に戻す。

## Suggested Fields

- Title: `Prepare FDE public kernel with restrictive rights and defensive patent gate`
- Priority: High
- Status: Todo / Backlog
- Labels: `FDE`, `rights`, `patent`, `public-kernel`, `publication-gate`, `mvp-gate`
- Project: FDE / Fractal Decision Ecosystem, if available
- Assignee: owner

## This Is Not Approval For

- public release
- GitHub repository visibility change
- patent filing
- `Patent Pending` wording
- private source pointers / local paths / absorbed dialogues / secret material の添付
- Codex による connector / browser / API submit

## Optional Repo Follow-Up After Manual Creation

Linear issue を作った場合だけ、`LINEAR_ISSUE_RECORD.md` に次を記録する。

- Linear issue identifier
- Linear issue URL
- created date
- project used
- labels applied
- priority used
- current status

その後、実際に完了した項目だけ `TODO_FDE_PUBLIC_KERNEL_RIGHTS.md` の optional Linear tracking section で check する。
