# TODO: FDE Public Kernel / Rights / Defensive Patent Gate

Status: active

目的: FDE private repo を維持したまま、権利条件・defensive provisional patent・最小 public kernel 公開判断を一つの作業単位に閉じる。

## MVP Gate

- [x] `MVP_STATUS.md` に private local MVP 判定を記録する
- [x] `python scripts\mvp_gate_check.py` で public-ready / pre-publication / pytest を集約する
- [ ] 次: inventor / owner / filing decision を閉じる

## Linear Tracking

- [x] `LINEAR_EXPORT.md` を latest MVP gate 状態へ更新する
- [x] `LINEAR_CREATE_MANUAL.md` に manual issue creation fallback を固定する
- [ ] Linear issue identifier / URL を記録する
- [ ] Linear project / labels / priority を確認する

## 最重要ブロッカー

- [ ] Defensive provisional patent application を出すか決める
- [ ] Inventor name(s) を確定する
- [ ] Owner / assignee を確定する

## Patent / Filing

- [x] `PROVISIONAL_PATENT_DISCLOSURE_DRAFT.md` を最終確認する
- [x] 図・処理フロー・generator 擬似コードが十分か確認する
- [x] Filing packet を PDF 化する
- [ ] Filing する場合は USPTO Patent Center 等で提出する
- [ ] Filing receipt / application number / submitted PDF / file hash を private に保存する
- [ ] Filing した場合、12か月後の nonprovisional / PCT follow-up 期限をカレンダー化する
- [ ] Filing しない場合、その判断理由を `INVENTION_RECORD.md` に記録する
- [ ] `Patent Pending` 表記は application filed 後だけ使う

## Rights / License

- [x] `LICENSE` が private owner は完全自由、第三者は無許諾になっていることを確認する
- [x] `RIGHTS_NOTICE.md` が no patent license / no trademark license / no derivative works / no model training を明記していることを確認する
- [x] Public kernel を出しても private FDE operating system がライセンスされないことを確認する

## Public Kernel

- [x] 公開対象を `public-kernel/` のみに限定する
- [x] Full 50-skill recursive implementation を公開しない
- [x] Generator internals を公開しない
- [x] `Documents/brain` pointers を公開しない
- [x] Local filesystem paths を公開しない
- [x] External AI route registry を公開しない
- [x] Absorbed dialogues を公開しない
- [x] Machine-specific runtime procedures を公開しない
- [x] Private guarantee scripts を公開しない
- [x] Patent-candidate implementation details を filing decision 完了まで公開しない

## Verification

- [x] `python scripts\public_ready_check.py` を通す
- [x] `python -m pytest -q` を通す
- [x] `python scripts\pre_publication_gate_check.py --json` を通す
- [x] `public-kernel/` に local paths / private source pointers / secrets / absorbed dialogues / private workflow details がないことを確認する
- [x] `PUBLIC_READY.md` を現行の rights posture / patent gate / public-kernel gate に合わせて更新する

## Publication Gate

- [ ] GitHub repository visibility は明示承認なしに変更しない
- [ ] Public release / external send / Slack / Gmail / Drive / browser send は別承認にする
- [ ] 公開する場合は対象 repository を owner/name 形式で明示する
- [ ] 公開する場合は commit history と files が web 上で visible になることを再確認する

## Current Local Evidence

- `LINEAR_EXPORT.md`: Linear issue 用の元メモ
- `PUBLIC_KERNEL_PLAN.md`: public kernel 方針
- `DEFENSIVE_PATENT_REVIEW.md`: defensive patent 方針
- `PROVISIONAL_PATENT_DISCLOSURE_DRAFT.md`: provisional patent disclosure draft
- `INVENTION_RECORD.md`: private invention record
- `public-kernel/`: sanitized public kernel candidate
- `patent-packet/`: PDF patent packet と SHA256 manifest
- `scripts/pre_publication_gate_check.py`: pre-publication gate 機械検証
- `scripts/mvp_gate_check.py`: private local MVP gate 機械検証
- `MVP_STATUS.md`: MVP 判定と次 milestone
- `LINEAR_CREATE_MANUAL.md`: Linear issue 手動作成 fallback
