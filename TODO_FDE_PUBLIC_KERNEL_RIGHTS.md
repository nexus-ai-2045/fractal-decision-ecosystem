# TODO: FDE Public Kernel / Rights / Defensive Patent Gate

Status: human / external blockers 解消まで active。Linear は optional local tracking。

Purpose: FDE を private に維持したまま、rights posture・defensive provisional patent timing・sanitized public-kernel release boundary を一つの work item として追跡する。

## Local MVP Gate

- [x] `MVP_STATUS.md` に private local MVP state を記録する
- [x] `python scripts\mvp_gate_check.py` で public-ready / pre-publication / pytest checks を集約する
- [x] `LINEAR_EXPORT.md` に final copy-paste Linear packet を用意する
- [x] Next milestone を閉じる: inventor / owner / filing decision
- [x] Patent filing は local implementation residue ではなく optional external action として扱う
- [ ] Next milestone: publication approval only if public release is requested

## Optional Linear Tracking

- [x] `LINEAR_EXPORT.md` を single issue packet として finalize する
- [x] `LINEAR_CREATE_MANUAL.md` を manual creation fallback として維持する
- [x] `LINEAR_ISSUE_RECORD.md` placeholder を追加する
- [x] Linear issue creation is optional, not required for local FDE operation
- [ ] If used, Linear issue を手動作成する
- [ ] If used, Linear issue identifier / URL を `LINEAR_ISSUE_RECORD.md` に記録する
- [ ] If used, Linear project / labels / priority を確認する
- [ ] If used, repo evidence 更新後、この section の完了項目を check する

## Primary Human Blockers

- [x] Patent / filing 方針は broad に保ち、local operation blocker にしない
- [x] Inventor decision を記録する: user-confirmed sole inventor
- [x] Owner / assignee decision を記録する: user owner, no assignee

## Patent / Filing

- [x] `PROVISIONAL_PATENT_DISCLOSURE_DRAFT.md` を用意する
- [x] Diagrams / processing flow / generator pseudocode が含まれることを確認する
- [x] Filing packet を PDF 化する
- [ ] If later chosen, 別途承認後に chosen filing path で submit する
- [ ] If filed, filing receipt / application number / submitted PDF / file hash を private に保存する
- [ ] If filed, 12-month nonprovisional / PCT follow-up deadline を calendar 化する
- [ ] `Patent Pending` は application が実際に filed された後だけ使う

## Rights / License

- [x] `LICENSE` が owner freedom を保ち、third party license を default で付与しないことを確認する
- [x] `RIGHTS_NOTICE.md` が no patent license / no trademark license / no derivative works / no model training を明記していることを確認する
- [x] Public kernel が private FDE operating system を license しないことを確認する

## Public Kernel

- [x] Public candidate scope を `public-kernel/` に限定する
- [x] Full 50-skill recursive implementation を private に保つ
- [x] Private structure を reveal する generator internals を private に保つ
- [x] `Documents/brain` pointers を private に保つ
- [x] Local filesystem paths を private に保つ
- [x] External AI route registry を private に保つ
- [x] Absorbed dialogues を private に保つ
- [x] Machine-specific runtime procedures を private に保つ
- [x] Private guarantee scripts を private に保つ
- [x] Filing decision 完了まで patent-candidate implementation details を private に保つ

## Verification

- [x] `python scripts\public_ready_check.py`
- [x] `python -m pytest -q`
- [x] `python scripts\pre_publication_gate_check.py --json`
- [x] `public-kernel/` に local paths / private source pointers / secrets / absorbed dialogues / private workflow details がないことを確認する
- [x] `PUBLIC_READY.md` が current rights posture / patent gate / public-kernel gate に合っている
- [x] Linear issue creation is not required before `python scripts\mvp_gate_check.py`

## Publication Gate

- [ ] Exact repository への explicit current-conversation approval なしに GitHub repository visibility を変更しない
- [ ] Public release / external send / Slack / Gmail / Drive / browser send は別承認の action として扱う
- [ ] Public release が後で要求された場合、action 前に target repository を `owner/name` form で明示する
- [ ] Public release が後で要求された場合、commit history と files が web 上で visible になることを再確認する
- [ ] Public release が後で要求された場合、README / license / SECURITY.md / secret scan / personal path scan / `PUBLIC_READY.md` を確認する

## Current Local Evidence

- `LINEAR_EXPORT.md`: optional Linear issue packet
- `LINEAR_CREATE_MANUAL.md`: manual issue creation fallback
- `LINEAR_ISSUE_RECORD.md`: post-creation placeholder
- `PUBLIC_KERNEL_PLAN.md`: public-kernel boundary
- `DEFENSIVE_PATENT_REVIEW.md`: defensive patent context
- `PROVISIONAL_PATENT_DISCLOSURE_DRAFT.md`: provisional patent disclosure draft
- `INVENTION_RECORD.md`: private invention record
- `public-kernel/`: sanitized public-kernel candidate
- `patent-packet/`: PDF patent packet and SHA256 manifest
- `scripts/pre_publication_gate_check.py`: pre-publication gate
- `scripts/mvp_gate_check.py`: private local MVP gate
- `MVP_STATUS.md`: MVP status and next milestone
