# Linear issue packet: FDE public kernel / rights / defensive patent gate

Status: optional local handoff packet。Linear を使う場合だけ手動作成に使う。
Priority: High
Labels: FDE, rights, patent, public-kernel, publication-gate, mvp-gate

## Title

Prepare FDE public kernel with restrictive rights and defensive patent gate

## Summary

FDE は、rights posture と sanitized public kernel の公開境界が明示的に閉じるまで private のまま維持する。

private local MVP gate は実装済みで、通常の code readiness は主 blocker ではない。inventor / owner / rights strategy の判断も記録済み。残っている blocker は公開する場合の外部手続き。

- GitHub repository visibility を変更する場合の repo-specific な明示承認

この issue は、公開・patent filing・外部 submit・GitHub visibility 変更の承認として扱わない。

## Current State

- Repository visibility は private のまま。
- GitHub visibility change は未実行。
- External publication / release / announcement は未実行。
- Patent filing は未実行。Filing は optional external action として扱う。
- Inventor decision: user-confirmed sole inventor。
- Owner / assignee decision: user owner, no assignee。
- Rights strategy: patent / filing details は意図的に broad に保つ。
- Codex から Linear connector write は未実行。Linear は必須ではなく、使う場合だけ手動作成する。
- `Patent Pending` 表記は、application が実際に filed されるまで使わない。
- Full private FDE / Brain / recursive skill layer は private のまま維持する。
- 公開する場合も full private repo ではなく、sanitized public kernel のみに限定する。

## Local Evidence

- `MVP_STATUS.md`: private local MVP gate state と next milestone。
- `PUBLIC_READY.md`: publication gate と残 human / patent blockers。
- `RIGHTS_NOTICE.md`: restrictive rights posture。
- `LICENSE`: restrictive source-available / all-rights-reserved license posture。
- `PUBLIC_KERNEL_PLAN.md`: public-kernel boundary。
- `DEFENSIVE_PATENT_REVIEW.md`: defensive patent decision context。
- `PROVISIONAL_PATENT_DISCLOSURE_DRAFT.md`: local private draft。filing が後で選ばれた場合だけ human review が必要。
- `INVENTION_RECORD.md`: private invention record。
- `public-kernel/`: sanitized public-kernel candidate。
- `patent-packet/`: printable PDF draft と SHA256 manifest。
- `scripts/pre_publication_gate_check.py`: local pre-publication gate。
- `scripts/mvp_gate_check.py`: top-level private MVP gate。

## Local Gate Command

```text
python scripts\mvp_gate_check.py
```

Expected result:

- public-readiness check passes
- pre-publication gate check passes
- pytest passes
- external actions performed remains false
- repository visibility expectation remains private
- next milestone remains publication approval only if public release is requested

## Primary External Blocker

Public release する場合は、exact repository と visible になる内容を明示して、human approval を取る。

Patent / filing details は broad に保つ。`Patent Pending` / `特許出願中` は application が実際に filed されるまで使わない。

## Remaining Tasks

1. `Patent Pending` wording は application が実際に filed されるまで使わない。
2. Exact repo-specific public-visibility approval が現在の会話で出るまで repository は private に維持する。
3. Linear を使う場合だけ、手動作成後に issue ID / URL / project / labels を `LINEAR_ISSUE_RECORD.md` に記録する。

## Public Kernel Scope

公開対象:

- Fractal Decision Ecosystem concept overview。
- Abstract recursive map: core / router / leaf。
- Four public gates:
  - pre-execution fact check
  - scope routing
  - publication containment
  - done verification closeout
- Restrictive license and rights notice。

private に残すもの:

- Full 50-skill recursive implementation。
- Private structure を reveal する generator internals。
- `Documents/brain` pointers。
- Local filesystem paths。
- External AI route registry。
- Absorbed dialogues。
- Machine-specific runtime procedures。
- Private guarantee scripts。
- Filing decision が完了するまで patent-candidate implementation details。

## Acceptance Criteria

- Patent / filing details を broad に保つ方針が記録されている。
- Inventor decision が記録されている。
- Owner / assignee decision が記録されている。
- Filing は optional external action として扱われている。
- `Patent Pending` language は filing 後だけ使われている。
- Public kernel は separate sanitized artifact のまま。
- Public kernel に local paths / private source pointers / secrets / private workflow details / absorbed dialogue content が含まれていない。
- License posture は source-available / all rights reserved / no patent license / no trademark license / no derivative works / no model training のまま。
- `PUBLIC_READY.md` が current rights posture と checks に合っている。
- `MVP_STATUS.md` が private local MVP gate state を記録している。
- `python scripts\mvp_gate_check.py` が local で pass する。
- Exact repository への explicit current-conversation approval なしに repository を public にしない。
- Linear を使う場合だけ、manual issue 作成後に `LINEAR_ISSUE_RECORD.md` が更新されている。

## Suggested Linear Fields

- Title: `Prepare FDE public kernel with restrictive rights and defensive patent gate`
- Priority: High
- Status: Todo / Backlog
- Labels: `FDE`, `rights`, `patent`, `public-kernel`, `publication-gate`, `mvp-gate`
- Project: FDE / Fractal Decision Ecosystem, if available
- Assignee: owner
