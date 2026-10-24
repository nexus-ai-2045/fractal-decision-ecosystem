# TODO: FDE Public Kernel / Rights / Defensive Patent Gate

Status: human / external blockers 解消まで active。External issue tracker は local gate の前提にしない。

Purpose: FDE を private に維持したまま、rights posture・defensive provisional patent timing・sanitized public-kernel release boundary を一つの work item として追跡する。

## Local MVP Gate

- [x] `MVP_STATUS.md` に private local MVP state を記録する
- [x] `pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_mvp_gate.ps1` で public-ready / pre-publication / pytest checks を集約する
- [x] Next milestone を閉じる: inventor / owner / filing decision
- [x] Patent filing は local implementation residue ではなく optional external action として扱う
- [ ] Next milestone: publication approval only if public release is requested

## Primary Human Blockers

- [x] Patent / filing 方針は broad に保ち、local operation blocker にしない
- [x] Inventor decision を記録する: user-confirmed sole inventor
- [x] Owner / assignee decision を記録する: user owner, no assignee

## Patent / Filing

- [x] `PROVISIONAL_PATENT_DISCLOSURE_DRAFT.md` を local-only draft として用意する (git 追跡対象外)
- [x] Diagrams / processing flow / generator pseudocode が含まれることを確認する
- [x] Filing packet を `patent-packet/FDE_PROVISIONAL_PATENT_DISCLOSURE_DRAFT.pdf` として local-only で PDF 化できるようにする (`scripts/build_patent_packet.py`)
- [x] `patent-packet/MANIFEST.sha256` に PDF packet の integrity hash を記録できるようにする (local-only 生成)
- [x] 2026-07 の repository public 化で `PROVISIONAL_PATENT_DISCLOSURE_DRAFT.md` と `patent-packet/` が誤って世界公開されたため、両方を git 追跡から除去し `.gitignore` に追加する
- [x] 除去の事実と公開自体は取り消せないことの証跡を `PATENT_DISCLOSURE_RECORD.md` に記録する
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
- [x] `python scripts\public_kernel_diff_manifest.py --check`
- [x] `python scripts\human_review_packet_check.py --json`
- [x] `public-kernel/` に local paths / private source pointers / secrets / absorbed dialogues / private workflow details がないことを確認する
- [x] `PUBLIC_READY.md` が current rights posture / patent gate / public-kernel gate に合っている
- [x] External issue tracker is not required before `pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_mvp_gate.ps1`

## Publication Gate

- [ ] Exact repository への explicit current-conversation approval なしに GitHub repository visibility を変更しない
- [ ] Public release / external send / Slack / Gmail / Drive / browser send は別承認の action として扱う
- [ ] Public release が後で要求された場合、action 前に target repository を `owner/name` form で明示する
- [ ] Public release が後で要求された場合、commit history と files が web 上で visible になることを再確認する
- [ ] Public release が後で要求された場合、README / license / SECURITY.md / secret scan / personal path scan / `PUBLIC_READY.md` を確認する

## Current Local Evidence

- `PUBLICATION_REVIEW_PACKET.md`: human review packet; public action approval ではない
- `PUBLIC_KERNEL_PLAN.md`: public-kernel boundary
- `DEFENSIVE_PATENT_REVIEW.md`: defensive patent context
- `PROVISIONAL_PATENT_DISCLOSURE_DRAFT.md`: provisional patent disclosure draft (local-only, git 追跡対象外、`.gitignore` 済み)
- `INVENTION_RECORD.md`: private invention record
- `PATENT_DISCLOSURE_RECORD.md`: 特許素材の公開・除去に関する事実記録 (法的助言ではない)
- `public-kernel/`: sanitized public-kernel candidate
- `patent-packet/`: local-only 生成物 (`scripts/build_patent_packet.py` で再生成可能)。git 追跡対象外、`.gitignore` 済み
- `scripts/pre_publication_gate_check.py`: pre-publication gate
- `scripts/public_kernel_diff_manifest.py`: public-kernel diff manifest check
- `scripts/human_review_packet_check.py`: publication review packet check
- `scripts/run_mvp_gate.ps1`: Windows local supported MVP gate entrypoint
- `scripts/mvp_gate_check.py`: private local MVP gate implementation
- `MVP_STATUS.md`: MVP status and next milestone
